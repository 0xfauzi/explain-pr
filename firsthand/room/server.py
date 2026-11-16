"""The Room server: one page, a JSON API over the engine, and an event stream.

It starts from the standard-library server of the learning-while-building skill
(`skills/learning-while-building/scripts/room.py`): a ThreadingHTTPServer, a quiet
request log, the same size limits, `Cache-Control: no-store`, and one write lock
around every POST.

The whole request path is `handle()`, a function of the request and the server's
state, so tests need no socket. The HTTP handler class only moves bytes in and out
of it and runs the event stream.

The Room imports nothing from the rest of Firsthand. It receives an object with
the engine's methods (`EngineAPI` in the build contract) and calls it by name. An
engine error is any exception with string attributes `code` and `message`.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import queue
import re
import secrets
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import BinaryIO
from urllib.parse import parse_qs, quote, urlsplit

# A pick or a short sentence. The cap stops a runaway client from filling the record.
MAX_ANSWER_CHARS = 4000
# The server reads at most this much from one request body.
MAX_BODY_BYTES = 20_000
TICKET_TTL_S = 60
SESSION_TTL_S = 30 * 24 * 3600
# A comment line on every open event stream this often, so a dead one is found.
KEEPALIVE_S = 15.0

HERE = Path(__file__).resolve().parent
_LOGGER = logging.getLogger("firsthand.room")
_LOGGER.addHandler(logging.NullHandler())
COOKIE = "fh_session"

SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": (
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; "
        "frame-ancestors 'none'"
    ),
}

STATUS = {
    "bad_request": 400,
    "invalid": 400,
    "no_session": 401,
    "forbidden": 403,
    "refused": 403,
    "not_found": 404,
    "no_question": 404,
    "state": 409,
    "confirm": 409,
    "too_large": 413,
}


def no_session_text() -> str:
    from firsthand import install

    return f"This page needs a session. Run in a terminal: {install.command()} room"


def ticket_used_text() -> str:
    from firsthand import install

    return (
        "This link has been used or has expired. Run in a terminal: "
        f"{install.command()} room"
    )


INTERNAL = "Something went wrong inside Firsthand. Nothing was changed."

FONTS = (
    "newsreader-latin-opsz-normal",
    "newsreader-latin-opsz-italic",
    "ibm-plex-mono-latin-300-normal",
    "ibm-plex-mono-latin-400-normal",
    "ibm-plex-mono-latin-400-italic",
    "ibm-plex-mono-latin-500-normal",
    "ibm-plex-sans-latin-400-normal",
    "ibm-plex-sans-latin-500-normal",
    "ibm-plex-sans-latin-600-normal",
)
LICENCES = ("OFL-Newsreader", "OFL-IBM-Plex-Mono", "OFL-IBM-Plex-Sans")

# An exact table: a request path is looked up, never joined onto a folder.
STATIC = {
    "room.css": "text/css; charset=utf-8",
    "room.js": "text/javascript; charset=utf-8",
    "room-views.js": "text/javascript; charset=utf-8",
    "icon.svg": "image/svg+xml",
    "icon-open.svg": "image/svg+xml",
    **{f"fonts/{name}.woff2": "font/woff2" for name in FONTS},
    **{f"fonts/{name}.txt": "text/plain; charset=utf-8" for name in LICENCES},
}

REF = r"[A-Za-z0-9_-]{1,64}"
PAGE_RE = re.compile(rf"^/(?:journal|skills|settings|[qr]/{REF})?$")
Q_GET_RE = re.compile(rf"^/api/q/({REF})$")
Q_POST_RE = re.compile(
    rf"^/api/q/({REF})/(lock|undo|confidence|show|skip|wrong-start|dispute)$"
)

SETTINGS_KEYS = frozenset({"dial", "daily_limit", "findings_to_agent", "quiet_today"})
PROJECT_KEYS = frozenset(
    {"test_command", "quiet", "high_stakes_add", "high_stakes_remove"}
)


@dataclass
class Response:
    status: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    stream: bool = False


@dataclass(frozen=True)
class Session:
    token: str
    expires: float


class Refusal(Exception):
    """A request the Room itself refuses, before the engine is called."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def _digest(session_id: str) -> str:
    return hashlib.sha256(session_id.encode()).hexdigest()


class Sessions:
    """Tickets (one-time links) and browser sessions. Only a session id's SHA-256
    is kept, in memory and in the sessions file."""

    def __init__(self, path: Path | None, clock: Callable[[], float]) -> None:
        self._path = path
        self._clock = clock
        self._lock = threading.Lock()
        self._tickets: dict[str, float] = {}
        self._sessions: dict[str, Session] = self._load()

    def _load(self) -> dict[str, Session]:
        if self._path is None:
            return {}
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            rows = data["sessions"]
            now = self._clock()
            return {
                str(r["id_sha256"]): Session(str(r["token"]), float(r["expires"]))
                for r in rows
                if float(r["expires"]) > now
            }
        except (OSError, ValueError, KeyError, TypeError):
            return {}

    def _save(self) -> None:
        if self._path is None:
            return
        rows = [
            {"id_sha256": k, "token": s.token, "expires": s.expires}
            for k, s in self._sessions.items()
        ]
        data = (json.dumps({"v": 1, "sessions": rows}, indent=2) + "\n").encode()
        self._path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        tmp = self._path.with_name(self._path.name + ".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
        os.replace(tmp, self._path)

    def new_ticket(self) -> str:
        ticket = secrets.token_urlsafe(24)
        with self._lock:
            now = self._clock()
            self._tickets = {t: e for t, e in self._tickets.items() if e > now}
            self._tickets[ticket] = now + TICKET_TTL_S
        return ticket

    def redeem(self, ticket: str) -> str | None:
        """Spend a ticket. Returns a new session id, or None when it is not valid."""
        with self._lock:
            expires = self._tickets.pop(ticket, None)
            now = self._clock()
            if expires is None or expires <= now:
                return None
            session_id = secrets.token_urlsafe(32)
            self._sessions = {
                k: s for k, s in self._sessions.items() if s.expires > now
            }
            self._sessions[_digest(session_id)] = Session(
                secrets.token_urlsafe(32), now + SESSION_TTL_S
            )
            self._save()
        return session_id

    def find(self, cookie_header: str | None) -> Session | None:
        if not cookie_header:
            return None
        try:
            jar = SimpleCookie()
            jar.load(cookie_header)
        except CookieError:
            return None
        morsel = jar.get(COOKIE)
        if morsel is None or not morsel.value:
            return None
        with self._lock:
            session = self._sessions.get(_digest(morsel.value))
        if session is None or session.expires <= self._clock():
            return None
        return session


class RoomServer:
    """The Room, bound to 127.0.0.1 at construction. `start()` serves it."""

    def __init__(
        self,
        engine: object,
        *,
        port: int,
        host: str = "127.0.0.1",
        sessions_file: Path | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if host != "127.0.0.1":
            raise ValueError("The Room binds to 127.0.0.1 only.")
        self.engine = engine
        self.sessions = Sessions(sessions_file, clock)
        self.write_lock = threading.Lock()
        self.keepalive_s = KEEPALIVE_S
        self._streams: list[queue.Queue[bytes | None]] = []
        self._streams_lock = threading.Lock()
        self._stopped = threading.Event()
        self._unsubscribe: Callable[[], None] | None = None
        self._thread: threading.Thread | None = None
        self._httpd = _HTTPServer((host, port), _Handler)
        self._httpd.room = self
        self.port: int = int(self._httpd.server_address[1])
        self.url = f"http://127.0.0.1:{self.port}"
        self.hosts = frozenset({f"127.0.0.1:{self.port}", f"localhost:{self.port}"})
        self.origins = frozenset({f"http://{h}" for h in self.hosts})

    def new_ticket(self, next_path: str = "/") -> str:
        ticket = self.sessions.new_ticket()
        return (
            f"{self.url}/enter?t={ticket}&next={quote(_safe_next(next_path), safe='/')}"
        )

    def start(self) -> threading.Thread:
        # Subscribing here, not in the constructor: the daemon builds the Room before
        # the engine exists and hands it a placeholder that is filled in later.
        self._unsubscribe = self.engine.subscribe(self.notice)
        thread = threading.Thread(
            target=self._httpd.serve_forever,
            kwargs={"poll_interval": 0.2},
            name="firsthand-room",
            daemon=True,
        )
        thread.start()
        self._thread = thread
        return thread

    def shutdown(self) -> None:
        self._stopped.set()
        with self._streams_lock:
            for q in self._streams:
                _put(q, None)
        if self._unsubscribe is not None:
            try:
                self._unsubscribe()
            finally:
                self._unsubscribe = None
        if self._thread is not None:
            self._httpd.shutdown()
            self._thread.join(timeout=5)
            self._thread = None
        self._httpd.server_close()

    def clients(self) -> int:
        with self._streams_lock:
            return len(self._streams)

    def notice(self, item: Mapping[str, object]) -> None:
        """Called by the engine on its own thread. Never blocks."""
        data = {
            "seq": item.get("seq"),
            "topic": item.get("topic"),
            "id": item.get("id"),
        }
        line = b"data: " + json.dumps(data).encode() + b"\n\n"
        with self._streams_lock:
            for q in self._streams:
                _put(q, line)

    def stream(self, out: BinaryIO) -> None:
        """Write engine notices to one open event stream until it closes."""
        q: queue.Queue[bytes | None] = queue.Queue(maxsize=256)
        with self._streams_lock:
            self._streams.append(q)
        try:
            out.write(b": open\n\n")
            out.flush()
            while not self._stopped.is_set():
                try:
                    item = q.get(timeout=self.keepalive_s)
                except queue.Empty:
                    item = b": keep\n\n"
                if item is None:
                    break
                out.write(item)
                out.flush()
        except OSError:
            pass
        finally:
            with self._streams_lock:
                if q in self._streams:
                    self._streams.remove(q)


def _put(q: queue.Queue[bytes | None], item: bytes | None) -> None:
    try:
        q.put_nowait(item)
    except queue.Full:
        pass


class _HTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    room: RoomServer


class _Handler(BaseHTTPRequestHandler):
    server: _HTTPServer

    def log_message(self, *args: object) -> None:  # keep the terminal and the log quiet
        return

    def version_string(self) -> str:
        return "Firsthand"

    def do_GET(self) -> None:
        self._serve("GET", b"")

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        # Read at most one byte past the limit: enough for handle() to refuse it.
        body = self.rfile.read(max(0, min(length, MAX_BODY_BYTES + 1)))
        if length > MAX_BODY_BYTES:
            self.close_connection = True
        self._serve("POST", body)

    def _serve(self, method: str, body: bytes) -> None:
        room = self.server.room
        resp = handle(room, method, self.path, dict(self.headers.items()), body)
        self.send_response(resp.status)
        for name, value in resp.headers.items():
            self.send_header(name, value)
        if not resp.stream:
            self.send_header("Content-Length", str(len(resp.body)))
        self.end_headers()
        if resp.stream:
            self.close_connection = True
            room.stream(self.wfile)
        else:
            self.wfile.write(resp.body)


# ---------------------------------------------------------------- responses


def _respond(status: int, body: bytes, content_type: str, **extra: str) -> Response:
    headers = {"Content-Type": content_type, **SECURITY_HEADERS}
    headers.update(extra)
    return Response(status, headers, body)


def _json(status: int, value: object) -> Response:
    return _respond(status, json.dumps(value).encode(), "application/json")


def _error(status: int, code: str, message: str) -> Response:
    return _json(status, {"error": {"code": code, "message": message}})


def _engine_error(exc: BaseException) -> Response:
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", None)
    if isinstance(code, str) and isinstance(message, str) and code in STATUS:
        return _error(STATUS[code], code, message)
    return _error(500, "internal", INTERNAL)


def _not_found() -> Refusal:
    return Refusal(404, "not_found", "There is nothing at this address.")


# ---------------------------------------------------------------- the request path


def handle(
    server: RoomServer, method: str, path: str, headers: Mapping[str, str], body: bytes
) -> Response:
    """The whole request path: checks, then the route. Never raises."""
    try:
        return _route(
            server,
            method.upper(),
            path,
            {k.lower(): v for k, v in headers.items()},
            body,
        )
    except Refusal as r:
        return _error(r.status, r.code, r.message)
    except Exception as exc:  # an engine error, or a fault: never a traceback
        resp = _engine_error(exc)
        if resp.status == 500:
            _LOGGER.exception("Room request failed: %s %s", method, urlsplit(path).path)
        return resp


def _route(
    server: RoomServer, method: str, path: str, headers: Mapping[str, str], body: bytes
) -> Response:
    if headers.get("host", "").lower() not in server.hosts:
        raise Refusal(403, "forbidden", "This address is not served here.")
    url = urlsplit(path)
    query = {k: v[0] for k, v in parse_qs(url.query).items()}
    if not url.path.startswith("/api/"):
        if method != "GET":
            raise _not_found()
        return _public(server, url.path, query)
    session = server.sessions.find(headers.get("cookie"))
    if session is None:
        raise Refusal(401, "no_session", no_session_text())
    if method == "GET":
        return _api_get(server, session, url.path, query)
    if method == "POST":
        data = _post_body(server, session, headers, body)
        with server.write_lock:
            return _json(200, _api_post(server.engine, url.path, data))
    raise _not_found()


def _public(server: RoomServer, path: str, query: Mapping[str, str]) -> Response:
    if PAGE_RE.match(path):
        return _respond(200, _asset("page.html"), "text/html; charset=utf-8")
    if path.startswith("/static/") and path[len("/static/") :] in STATIC:
        name = path[len("/static/") :]
        return _respond(200, _asset(f"static/{name}"), STATIC[name])
    if path == "/enter":
        return _enter(server, query)
    if path == "/favicon.ico":
        # Browsers ask for it on their own. No content, so no error in the console.
        return _respond(204, b"", "image/x-icon")
    raise _not_found()


def _asset(name: str) -> bytes:
    return (HERE / name).read_bytes()


def _safe_next(target: str) -> str:
    """A path on this site, or "/": one leading slash, no backslash, no control character."""
    ok = (
        target.startswith("/")
        and not target.startswith("//")
        and "\\" not in target
        and all(ch.isprintable() and not ch.isspace() for ch in target)
    )
    return target if ok else "/"


def _enter(server: RoomServer, query: Mapping[str, str]) -> Response:
    session_id = server.sessions.redeem(query.get("t", ""))
    if session_id is None:
        return _respond(
            403, (ticket_used_text() + "\n").encode(), "text/plain; charset=utf-8"
        )
    return _respond(
        303,
        b"",
        "text/plain; charset=utf-8",
        Location=_safe_next(query.get("next", "/")),
        **{"Set-Cookie": f"{COOKIE}={session_id}; HttpOnly; SameSite=Strict; Path=/"},
    )


def _project(query: Mapping[str, str]) -> str | None:
    return query.get("project") or None


def _limit(query: Mapping[str, str]) -> int:
    raw = query.get("limit")
    if raw is None:
        return 200
    if not raw.isdigit() or not 1 <= int(raw) <= 1000:
        raise Refusal(
            400, "bad_request", "limit must be a whole number from 1 to 1000."
        )
    return int(raw)


def _api_get(
    server: RoomServer, session: Session, path: str, query: Mapping[str, str]
) -> Response:
    engine = server.engine
    reads: dict[str, Callable[[], object]] = {
        "/api/session": lambda: {"token": session.token, "room": server.url},
        "/api/inbox": lambda: engine.inbox(project=_project(query)),
        "/api/journal": lambda: engine.journal(
            project=_project(query), limit=_limit(query)
        ),
        "/api/skills": lambda: engine.skills(project=_project(query)),
        "/api/settings": lambda: engine.settings(project=_project(query)),
    }
    if path == "/api/events":
        headers = {"Content-Type": "text/event-stream", **SECURITY_HEADERS}
        return Response(200, headers, b"", stream=True)
    if path in reads:
        return _json(200, reads[path]())
    m = Q_GET_RE.match(path)
    if m:
        return _json(200, engine.question(m.group(1)))
    raise _not_found()


def _post_body(
    server: RoomServer, session: Session, headers: Mapping[str, str], body: bytes
) -> dict:
    if headers.get("origin") not in server.origins:
        raise Refusal(403, "forbidden", "This request did not come from the Room page.")
    if not hmac.compare_digest(
        headers.get("x-firsthand-token", "").encode(), session.token.encode()
    ):
        raise Refusal(403, "forbidden", "This request did not come from the Room page.")
    if (
        headers.get("content-type", "").split(";")[0].strip().lower()
        != "application/json"
    ):
        raise Refusal(400, "bad_request", "The body must be JSON.")
    if len(body) > MAX_BODY_BYTES:
        raise Refusal(413, "too_large", "The request is too large.")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise Refusal(400, "bad_request", "The body must be JSON.") from None
    if not isinstance(data, dict):
        raise Refusal(400, "bad_request", "The body must be a JSON object.")
    return data


# ---------------------------------------------------------------- writes


def _text(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise Refusal(400, "bad_request", f"{key} must be text.")
    if len(value) > MAX_ANSWER_CHARS:
        raise Refusal(
            400, "bad_request", f"{key} is longer than {MAX_ANSWER_CHARS} characters."
        )
    return value


def _confidence(data: Mapping[str, object]) -> str | None:
    value = data.get("value")
    if value is not None and not isinstance(value, str):
        raise Refusal(400, "bad_request", "value must be high, low or null.")
    return value


Q_ACTIONS: dict[str, Callable[[object, str, Mapping[str, object]], object]] = {
    "lock": lambda e, ref, d: e.lock(
        ref, _text(d, "answer"), channel="room", final=False
    ),
    "undo": lambda e, ref, d: e.undo(ref),
    "confidence": lambda e, ref, d: e.confidence(ref, _confidence(d)),
    "show": lambda e, ref, d: e.show(ref),
    "skip": lambda e, ref, d: e.skip(ref, channel="room", final=False),
    "wrong-start": lambda e, ref, d: e.wrong_start(ref),
    "dispute": lambda e, ref, d: e.dispute(ref, _text(d, "reason")),
}


def _api_post(engine: object, path: str, data: Mapping[str, object]) -> object:
    m = Q_POST_RE.match(path)
    if m:
        return Q_ACTIONS[m.group(2)](engine, m.group(1), data)
    if path == "/api/settings":
        changes, project, confirm = _settings_body(data)
        return engine.set_settings(
            changes, project=project, source="room", confirm=confirm
        )
    raise _not_found()


def _settings_body(data: Mapping[str, object]) -> tuple[dict, str | None, bool]:
    changes = data.get("changes")
    project = data.get("project")
    confirm = data.get("confirm", False)
    if not isinstance(changes, dict) or not changes:
        raise Refusal(
            400, "bad_request", "changes must be an object with at least one key."
        )
    if project is not None and not isinstance(project, str):
        raise Refusal(400, "bad_request", "project must be a project id.")
    if not isinstance(confirm, bool):
        raise Refusal(400, "bad_request", "confirm must be true or false.")
    allowed = SETTINGS_KEYS | (PROJECT_KEYS if project else frozenset())
    unknown = sorted(set(changes) - allowed)
    if unknown:
        names = ", ".join(sorted(allowed))
        raise Refusal(
            400,
            "bad_request",
            f"Not a setting here: {', '.join(unknown)}. Use: {names}.",
        )
    for key, value in changes.items():
        if isinstance(value, str) and len(value) > MAX_ANSWER_CHARS:
            raise Refusal(400, "bad_request", f"{key} is too long.")
    return changes, project, confirm
