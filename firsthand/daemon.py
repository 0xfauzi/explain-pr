"""The process around the engine: spool tail, control socket, reply files, lifecycle.

One daemon per user. It holds run/daemon.lock for its whole life. The engine and
the Room are built by factories, so a test can run the loop with fakes. Heavy
imports stay inside functions: `hooks.py` imports this module for `spawn`.
"""

from __future__ import annotations

import contextlib
import errno
import fcntl
import json
import logging
import os
import select
import signal
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from firsthand import __version__, events, paths

if TYPE_CHECKING:
    from firsthand.model import EngineAPI, HookReply

ENGINE_NAME = f"firsthand/{__version__}"
MAX_REQUEST_BYTES = 65_536
CONFIRM_AFTER_S = 1.0
CONNECTION_TIMEOUT_S = 2.0

# Ops that hold the person's calls or a session credential.
REFUSED_UNDER_AGENT = {
    "journal": "firsthand journal",
    "skills": "firsthand skills",
    "answer_room": "firsthand room --tty",
    "room_ticket": "firsthand room",
}


@dataclass(frozen=True)
class DaemonContext:
    record_dir: Path
    room_url: str | None


class _ProtocolError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class _EngineSlot:
    """Passed to the Room factory before the engine exists, so the engine can be
    built with the Room's real URL. Every attribute is the engine's once it is set."""

    def __init__(self) -> None:
        self.target: object | None = None

    def __getattr__(self, name: str) -> object:
        target = self.__dict__.get("target")
        if target is None:
            raise AttributeError(name)
        return getattr(target, name)


_LOGGER = logging.getLogger("firsthand.daemon")
# The handler sits on the package logger, so the engine's and the Room's lines
# ("firsthand.engine", "firsthand.room") reach daemon.log too.
_PACKAGE_LOGGER = logging.getLogger("firsthand")


def _open_log() -> logging.Handler | None:
    """Send the daemon's log lines to run/daemon.log (mode 0600) while it runs."""
    path = paths.daemon_log_file()
    try:
        os.close(os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600))
        handler = logging.FileHandler(path, encoding="utf-8")
    except OSError:
        return None
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(message)s"))
    _PACKAGE_LOGGER.addHandler(handler)
    _PACKAGE_LOGGER.setLevel(logging.INFO)
    _PACKAGE_LOGGER.propagate = False
    return handler


def _close_log(handler: logging.Handler | None) -> None:
    if handler is not None:
        _PACKAGE_LOGGER.removeHandler(handler)
        handler.close()


def _log(message: str) -> None:
    if _PACKAGE_LOGGER.handlers:
        _LOGGER.info(message)


def _default_engine(ctx: DaemonContext) -> EngineAPI:
    from firsthand.config import ConfigStore
    from firsthand.engine import Engine
    from firsthand.record import Record, ensure_record

    ensure_record(ctx.record_dir)
    rec = Record(ctx.record_dir)
    store = ConfigStore(ctx.record_dir, commit=rec.commit)
    return Engine(record=rec, settings=store, room_url=ctx.room_url, log=_log)


def _default_room(engine: EngineAPI, port: int) -> object:
    from firsthand.room.server import RoomServer

    return RoomServer(engine, port=port, sessions_file=paths.room_sessions_file())


def _sweep() -> None:
    try:
        from firsthand.runner import scratch

        scratch.sweep()
    except Exception:  # a failed sweep must not stop the daemon
        _LOGGER.exception("scratch sweep failed")


def _error_body(exc: BaseException) -> dict:
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", None)
    if isinstance(code, str) and isinstance(message, str):
        return {"code": code, "message": message}
    return {
        "code": "internal",
        "message": "Firsthand hit an internal error. See ~/.firsthand/run/daemon.log.",
    }


class Daemon:
    def __init__(
        self,
        *,
        engine_factory: Callable[[DaemonContext], EngineAPI] | None = None,
        room_factory: Callable[[EngineAPI, int], object] | None = None,
        idle_exit_s: float = 1800.0,
        poll_s: float = 0.05,
    ) -> None:
        self._engine_factory = engine_factory or _default_engine
        self._room_factory = room_factory or _default_room
        self._idle_exit_s = idle_exit_s
        self._poll_s = poll_s
        self._stop = threading.Event()
        self._waiting: dict[str, tuple[float, bool]] = {}
        self._waiting_lock = threading.Lock()
        self._engine: EngineAPI | None = None
        self._room: object | None = None
        self._last_activity = time.monotonic()

    # ------------------------------------------------------------ lifecycle

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> int:
        paths.ensure_private_dirs()
        lock_fd = _take_lock()
        if lock_fd is None:
            return 0
        restore = _install_signals(self.stop)
        handler = _open_log()
        sock: socket.socket | None = None
        try:
            _log(f"started, pid {os.getpid()}")
            _sweep()
            self._start_parts()
            sock = _listen(paths.control_socket())
            self._write_info()
            self._loop(sock)
        finally:
            self._shutdown(sock)
            _log("stopped")
            _close_log(handler)
            restore()
            os.close(lock_fd)
        return 0

    def _start_parts(self) -> None:
        from firsthand import config

        port = config.read_port()
        if port is None:
            port = config.choose_port()
        slot = _EngineSlot()
        try:
            self._room = self._room_factory(slot, port)  # type: ignore[arg-type]
        except Exception:
            _LOGGER.exception("the Room did not start")
            self._room = None
        room_url = getattr(self._room, "url", None) if self._room is not None else None
        self._engine = self._engine_factory(DaemonContext(paths.record_dir(), room_url))
        slot.target = self._engine
        if self._room is not None:
            self._room.start()  # type: ignore[attr-defined]

    def _write_info(self) -> None:
        room_url = getattr(self._room, "url", None)
        info = {
            "v": 1,
            "pid": os.getpid(),
            "started": events.now_stamp(),
            "engine": ENGINE_NAME,
            "socket": str(paths.control_socket()),
            "port": getattr(self._room, "port", None),
            "room": room_url,
        }
        paths.write_private(
            paths.daemon_info_file(), (json.dumps(info) + "\n").encode()
        )

    def _shutdown(self, sock: socket.socket | None) -> None:
        if self._engine is not None:
            with contextlib.suppress(Exception):
                self._engine.close()
        if self._room is not None:
            with contextlib.suppress(Exception):
                self._room.shutdown()  # type: ignore[attr-defined]
        if sock is not None:
            sock.close()
            with contextlib.suppress(OSError):
                paths.control_socket().unlink()
        with contextlib.suppress(OSError):
            paths.daemon_info_file().unlink()

    # ------------------------------------------------------------- the loop

    def _loop(self, sock: socket.socket) -> None:
        offset = _read_offset()
        while not self._stop.is_set():
            readable, _, _ = select.select([sock], [], [], self._poll_s)
            if readable:
                self._serve_pending(sock)
            offset = self._read_spool(offset)
            self._safe(self._engine.tick)
            self._confirm_replies()
            if self._idle_too_long():
                _log("idle, exiting")
                break

    def _safe(self, fn: Callable[[], object]) -> None:
        try:
            fn()
        except Exception:
            _LOGGER.exception("engine error")

    def _idle_too_long(self) -> bool:
        now = time.monotonic()
        busy = not self._engine_idle() or self._room_clients() > 0
        if busy:
            self._last_activity = now
        return now - self._last_activity >= self._idle_exit_s

    def _engine_idle(self) -> bool:
        try:
            return bool(self._engine.idle())
        except Exception:
            _LOGGER.exception("engine.idle failed")
            return False

    def _room_clients(self) -> int:
        if self._room is None:
            return 0
        try:
            return int(self._room.clients())  # type: ignore[attr-defined]
        except Exception:
            _LOGGER.exception("room.clients failed")
            return 0

    # ---------------------------------------------------------------- spool

    def _read_spool(self, offset: int) -> int:
        path = paths.spool_file()
        lines, base = _read_lines(path, offset)
        for raw, end in lines:
            self._last_activity = time.monotonic()
            ev = events.decode(raw)
            if ev is not None:
                self._handle(ev)
            offset = base + end
            _save_offset(offset)
        return _truncate_if_read(path, offset)

    def _handle(self, ev: object) -> None:
        try:
            self._engine.handle(ev, self.write_reply)  # type: ignore[arg-type]
        except Exception:
            _LOGGER.exception("engine error on event %s", getattr(ev, "id", "?"))

    # -------------------------------------------------------------- replies

    def write_reply(self, r: HookReply) -> None:
        """Called by the engine, from any thread, once per prompt and stop."""
        body = {
            "v": 1,
            "id": r.event_id,
            "session": r.session,
            "event": r.event,
            "visible": r.visible,
            "context": r.context,
        }
        paths.ensure_private_dirs()
        paths.write_private(
            paths.reply_file(r.event_id), (json.dumps(body) + "\n").encode()
        )
        with self._waiting_lock:
            self._waiting[r.event_id] = (time.monotonic(), bool(r.visible or r.context))

    def _confirm_replies(self) -> None:
        now = time.monotonic()
        with self._waiting_lock:
            # A reply with text is confirmed as soon as the dispatcher has taken
            # it (the file is gone), so the next prompt sees it as delivered.
            due = [
                (i, text)
                for i, (at, text) in self._waiting.items()
                if now - at >= CONFIRM_AFTER_S
                or (text and not paths.reply_file(i).exists())
            ]
            for event_id, _ in due:
                del self._waiting[event_id]
        for event_id, holds_text in due:
            path = paths.reply_file(event_id)
            if not holds_text:
                with contextlib.suppress(OSError):
                    path.unlink()
                continue
            self._safe(
                lambda e=event_id, p=path: self._engine.delivered(e, _was_claimed(p))
            )

    # ------------------------------------------------------- control socket

    def _serve_pending(self, sock: socket.socket) -> None:
        while True:
            try:
                conn, _ = sock.accept()
            except (BlockingIOError, InterruptedError):
                return
            self._last_activity = time.monotonic()
            with conn:
                self._serve(conn)

    def _serve(self, conn: socket.socket) -> None:
        conn.settimeout(CONNECTION_TIMEOUT_S)
        try:
            raw = _read_line(conn)
        except (OSError, _ProtocolError) as exc:
            _send(conn, {"ok": False, "error": _error_body(exc)})
            return
        response, stop_after = self._respond(raw)
        _send(conn, response)
        if stop_after:
            self.stop()

    def _respond(self, raw: bytes) -> tuple[dict, bool]:
        try:
            request = _parse_request(raw)
            op = request["op"]
            result = self.dispatch(
                op, request["args"], cwd=request["cwd"], agent=request["agent"]
            )
        except Exception as exc:
            if not hasattr(exc, "code"):
                _LOGGER.exception("control error")
            return {"ok": False, "error": _error_body(exc)}, False
        return {"ok": True, "result": result}, op == "stop"

    def dispatch(self, op: str, args: dict, *, cwd: str | None, agent: bool) -> dict:
        """One control op, as build-2a-contract.md section 4.4."""
        if agent and op in REFUSED_UNDER_AGENT:
            from firsthand import install

            typed = REFUSED_UNDER_AGENT[op].replace("firsthand", install.command(), 1)
            raise _ProtocolError(
                "refused",
                "An agent cannot open this page. It holds your answers. "
                f"Run it in a terminal you opened: {typed}",
            )
        handler = _OPS.get(op)
        if handler is None:
            raise _ProtocolError("invalid", f"Unknown op: {op}.")
        return handler(self, args, cwd, agent)

    # ops, each (self, args, cwd, agent) -> dict

    def _op_ping(self, args: dict, cwd: str | None, agent: bool) -> dict:
        return {
            "pid": os.getpid(),
            "engine": ENGINE_NAME,
            "room": getattr(self._room, "url", None),
        }

    def _op_status(self, args: dict, cwd: str | None, agent: bool) -> dict:
        return self._engine.status(cwd)

    def _op_inbox(self, args: dict, cwd: str | None, agent: bool) -> dict:
        return self._engine.inbox(args.get("project"))

    def _op_question(self, args: dict, cwd: str | None, agent: bool) -> dict:
        return self._engine.question(args.get("ref"), cwd=cwd)

    def _op_answer(self, args: dict, cwd: str | None, agent: bool) -> dict:
        text = _required_str(args, "text")
        view = self._engine.lock(None, text, channel="chat", final=True, cwd=cwd)
        return {"lines": list(view.get("say") or [])}

    def _op_answer_room(self, args: dict, cwd: str | None, agent: bool) -> dict:
        ref = _required_str(args, "ref")
        text = _required_str(args, "text")
        return self._engine.lock(ref, text, channel="room", final=True)

    def _op_skip(self, args: dict, cwd: str | None, agent: bool) -> dict:
        view = self._engine.skip(None, channel="chat", final=True, cwd=cwd)
        return {"lines": list(view.get("say") or [])}

    def _op_quiet(self, args: dict, cwd: str | None, agent: bool) -> dict:
        scope = args.get("scope", "session")
        on = args.get("on", True)
        if not isinstance(on, bool):
            raise _ProtocolError("invalid", "on must be true or false.")
        return self._engine.quiet(scope, on, cwd=cwd)

    def _op_journal(self, args: dict, cwd: str | None, agent: bool) -> dict:
        limit = args.get("limit", 200)
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise _ProtocolError("invalid", "limit must be a positive whole number.")
        return self._engine.journal(args.get("project"), limit)

    def _op_skills(self, args: dict, cwd: str | None, agent: bool) -> dict:
        return self._engine.skills(args.get("project"))

    def _op_settings_get(self, args: dict, cwd: str | None, agent: bool) -> dict:
        return self._engine.settings(args.get("project"))

    def _op_settings_set(self, args: dict, cwd: str | None, agent: bool) -> dict:
        changes = args.get("changes")
        if not isinstance(changes, dict) or not changes:
            raise _ProtocolError(
                "invalid", "changes must be an object with at least one setting."
            )
        source = "agent" if agent else "cli"
        return self._engine.set_settings(
            changes, project=args.get("project"), source=source
        )

    def _op_room_ticket(self, args: dict, cwd: str | None, agent: bool) -> dict:
        if self._room is None:
            raise _ProtocolError(
                "unavailable",
                "The Room could not start on this computer. See ~/.firsthand/run/daemon.log, "
                "then run: firsthand status",
            )
        next_path = args.get("next") or "/"
        if not isinstance(next_path, str):
            raise _ProtocolError("invalid", "next must be a path.")
        return {"url": self._room.new_ticket(next_path)}  # type: ignore[attr-defined]

    def _op_stop(self, args: dict, cwd: str | None, agent: bool) -> dict:
        return {}


_OPS: dict[str, Callable[[Daemon, dict, str | None, bool], dict]] = {
    "ping": Daemon._op_ping,
    "status": Daemon._op_status,
    "inbox": Daemon._op_inbox,
    "question": Daemon._op_question,
    "answer": Daemon._op_answer,
    "answer_room": Daemon._op_answer_room,
    "skip": Daemon._op_skip,
    "quiet": Daemon._op_quiet,
    "journal": Daemon._op_journal,
    "skills": Daemon._op_skills,
    "settings_get": Daemon._op_settings_get,
    "settings_set": Daemon._op_settings_set,
    "room_ticket": Daemon._op_room_ticket,
    "stop": Daemon._op_stop,
}


# ------------------------------------------------------------------ helpers


def _required_str(args: dict, name: str) -> str:
    value = args.get(name)
    if not isinstance(value, str) or not value.strip():
        raise _ProtocolError("invalid", f"{name} must be a non-empty string.")
    return value


def _parse_request(raw: bytes) -> dict:
    try:
        request = json.loads(raw.decode())
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise _ProtocolError(
            "bad_request", "The request is not one JSON object."
        ) from None
    if not isinstance(request, dict) or not isinstance(request.get("op"), str):
        raise _ProtocolError("bad_request", "The request has no op.")
    args = request.get("args") or {}
    if not isinstance(args, dict):
        raise _ProtocolError("bad_request", "args must be an object.")
    cwd = request.get("cwd")
    return {
        "op": request["op"],
        "args": args,
        "cwd": cwd if isinstance(cwd, str) else None,
        "agent": request.get("agent") is True,
    }


def _read_line(conn: socket.socket) -> bytes:
    data = b""
    while b"\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk
        if len(data) > MAX_REQUEST_BYTES:
            raise _ProtocolError("too_large", "The request is over 65,536 bytes.")
    return data.split(b"\n", 1)[0]


def _send(conn: socket.socket, body: dict) -> None:
    data = (json.dumps(body) + "\n").encode()
    if len(data) > MAX_REQUEST_BYTES:
        data = (
            json.dumps(
                {
                    "ok": False,
                    "error": {
                        "code": "too_large",
                        "message": "The response is too large.",
                    },
                }
            )
            + "\n"
        ).encode()
    with contextlib.suppress(OSError):
        conn.sendall(data)


def _take_lock() -> int | None:
    fd = os.open(paths.daemon_lock_file(), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        os.close(fd)
        if exc.errno in (errno.EWOULDBLOCK, errno.EAGAIN, errno.EACCES):
            return None
        raise
    return fd


def _install_signals(stop: Callable[[], None]) -> Callable[[], None]:
    if threading.current_thread() is not threading.main_thread():
        return lambda: None
    saved = {
        s: signal.getsignal(s) for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    }
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, lambda *_: stop())
    signal.signal(signal.SIGINT, lambda *_: stop())

    def restore() -> None:
        for sig, handler in saved.items():
            signal.signal(sig, handler)

    return restore


def _listen(path: Path) -> socket.socket:
    if path.parent != paths.run_dir():
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(path.parent, 0o700)
    with contextlib.suppress(FileNotFoundError):
        path.unlink()  # a stale socket: this process holds the lock
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    old_umask = os.umask(0o177)
    try:
        sock.bind(str(path))
    finally:
        os.umask(old_umask)
    os.chmod(path, 0o600)
    sock.listen(16)
    sock.setblocking(False)
    return sock


def _read_offset() -> int:
    try:
        offset = json.loads(paths.spool_offset_file().read_text()).get("offset", 0)
    except (OSError, ValueError, AttributeError):
        return 0
    try:
        size = paths.spool_file().stat().st_size
    except OSError:
        size = 0
    if not isinstance(offset, int) or offset < 0 or offset > size:
        return 0
    return offset


def _save_offset(offset: int) -> None:
    paths.write_private(
        paths.spool_offset_file(), json.dumps({"offset": offset}).encode()
    )


def _read_lines(path: Path, offset: int) -> tuple[list[tuple[bytes, int]], int]:
    """Complete lines from offset, each with its end relative to offset."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except FileNotFoundError:
        return [], offset
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            os.lseek(fd, offset, os.SEEK_SET)
            chunks = []
            while chunk := os.read(fd, 1 << 16):
                chunks.append(chunk)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)
    data = b"".join(chunks)
    cut = data.rfind(b"\n")
    lines: list[tuple[bytes, int]] = []
    start = 0
    while start <= cut:
        end = data.index(b"\n", start) + 1
        lines.append((data[start:end], end))
        start = end
    return lines, offset


def _truncate_if_read(path: Path, offset: int) -> int:
    try:
        fd = os.open(path, os.O_RDWR)
    except FileNotFoundError:
        return offset
    try:
        if offset == 0 or os.fstat(fd).st_size != offset:
            return offset
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            if os.fstat(fd).st_size != offset:
                return offset
            os.ftruncate(fd, 0)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)
    _save_offset(0)
    return 0


def _was_claimed(path: Path) -> bool:
    """True when the dispatcher took the reply file; an unclaimed one is removed."""
    expired = path.with_suffix(".expired")
    try:
        os.rename(path, expired)
    except FileNotFoundError:
        return True
    with contextlib.suppress(OSError):
        expired.unlink()
    return False


# ------------------------------------------------------ process functions


def is_running() -> bool:
    """True when some process holds the daemon lock."""
    try:
        fd = os.open(paths.daemon_lock_file(), os.O_RDWR)
    except OSError:
        return False
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return True
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    finally:
        os.close(fd)


def spawn() -> bool:
    """Start a detached daemon. False when one is already running. Does not wait."""
    if is_running():
        return False
    paths.ensure_private_dirs()
    package_parent = str(Path(__file__).resolve().parent.parent)
    code = (
        "import sys; sys.path.insert(0, " + repr(package_parent) + "); "
        "from firsthand.cli import main; sys.exit(main(['daemon']))"
    )
    flags = [
        f for f, on in (("-I", sys.flags.isolated), ("-S", sys.flags.no_site)) if on
    ]
    log_fd = os.open(
        paths.daemon_log_file(), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600
    )
    try:
        subprocess.Popen(
            [sys.executable, *flags, "-c", code],
            stdin=subprocess.DEVNULL,
            stdout=log_fd,
            stderr=log_fd,
            close_fds=True,
            start_new_session=True,
            env=dict(os.environ),
        )
    finally:
        os.close(log_fd)
    return True


def main() -> int:
    """The "firsthand daemon" command."""
    return Daemon().run()
