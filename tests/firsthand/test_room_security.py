"""The Room's request checks: host, session, origin, token, body, tickets, headers."""

from __future__ import annotations

import json
import unittest
from urllib.parse import parse_qs, urlsplit

import support

from firsthand.room import server as room
from firsthand.room.server import RoomServer, handle


class FakeEngine:
    """Records every call and returns a small canned view."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def subscribe(self, fn):
        return lambda: None

    def __getattr__(self, name):
        def method(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return {"from": name}

        return method


class Clock:
    def __init__(self) -> None:
        self.now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


class RoomSecurityTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.engine = FakeEngine()
        self.clock = Clock()
        self.room = RoomServer(self.engine, port=0, clock=self.clock)
        self.addCleanup(self.room.shutdown)
        self.host = f"127.0.0.1:{self.room.port}"
        self.origin = f"http://{self.host}"

    # helpers

    def get(self, path: str, **headers: str) -> room.Response:
        return handle(self.room, "GET", path, {"Host": self.host, **headers}, b"")

    def enter(self, next_path: str = "/") -> room.Response:
        url = urlsplit(self.room.new_ticket(next_path))
        return self.get(f"{url.path}?{url.query}")

    def session(self) -> tuple[str, str]:
        cookie = self.enter().headers["Set-Cookie"].split(";")[0]
        token = json.loads(self.get("/api/session", Cookie=cookie).body)["token"]
        return cookie, token

    def post(self, path: str, body: bytes = b"{}", **overrides: str) -> room.Response:
        cookie, token = self.session()
        headers = {
            "Host": self.host,
            "Cookie": cookie,
            "Origin": self.origin,
            "X-Firsthand-Token": token,
            "Content-Type": "application/json",
        }
        headers.update(overrides)
        headers = {k: v for k, v in headers.items() if v != "-"}
        return handle(self.room, "POST", path, headers, body)

    def code(self, resp: room.Response) -> str:
        return json.loads(resp.body)["error"]["code"]

    # host

    def test_wrong_host_is_403_on_every_route(self) -> None:
        cookie, _ = self.session()
        paths = [
            "/",
            "/q/abc123",
            "/static/room.css",
            "/enter?t=x",
            "/api/inbox",
            "/api/session",
        ]
        for host in (
            "evil.example:80",
            "127.0.0.1",
            f"127.0.0.1:{self.room.port + 1}",
            "",
        ):
            for path in paths:
                resp = handle(
                    self.room, "GET", path, {"Host": host, "Cookie": cookie}, b""
                )
                self.assertEqual(resp.status, 403, (host, path))
                self.assertEqual(self.code(resp), "forbidden")
            resp = handle(
                self.room, "POST", "/api/q/abc123/lock", {"Host": host}, b"{}"
            )
            self.assertEqual(resp.status, 403)

    def test_localhost_host_is_accepted(self) -> None:
        resp = handle(
            self.room, "GET", "/", {"Host": f"localhost:{self.room.port}"}, b""
        )
        self.assertEqual(resp.status, 200)

    # session

    def test_api_without_session_is_401(self) -> None:
        for path in (
            "/api/inbox",
            "/api/q/abc123",
            "/api/journal",
            "/api/session",
            "/api/events",
        ):
            resp = self.get(path)
            self.assertEqual(resp.status, 401, path)
            self.assertEqual(self.code(resp), "no_session")
            self.assertEqual(
                json.loads(resp.body)["error"]["message"],
                room.no_session_text(),
            )
        resp = self.get("/api/inbox", Cookie="fh_session=made-up")
        self.assertEqual(resp.status, 401)
        self.assertEqual(self.engine.calls, [])

    def test_pages_need_no_session(self) -> None:
        for path in ("/", "/q/r6t9kd", "/r/r6t9kd", "/journal", "/skills", "/settings"):
            resp = self.get(path)
            self.assertEqual(resp.status, 200, path)
            self.assertTrue(resp.headers["Content-Type"].startswith("text/html"))

    def test_session_expires(self) -> None:
        cookie, _ = self.session()
        self.assertEqual(self.get("/api/inbox", Cookie=cookie).status, 200)
        self.clock.now += room.SESSION_TTL_S + 1
        self.assertEqual(self.get("/api/inbox", Cookie=cookie).status, 401)

    # POST checks

    def test_post_needs_origin(self) -> None:
        resp = self.post("/api/q/abc123/undo", Origin="-")
        self.assertEqual(resp.status, 403)
        resp = self.post("/api/q/abc123/undo", Origin="http://evil.example")
        self.assertEqual(resp.status, 403)
        resp = self.post(
            "/api/q/abc123/undo", Origin=f"http://127.0.0.1:{self.room.port + 1}"
        )
        self.assertEqual(resp.status, 403)
        self.assertEqual(self.engine.calls, [])

    def test_post_needs_the_session_token(self) -> None:
        self.assertEqual(
            self.post("/api/q/abc123/undo", **{"X-Firsthand-Token": "-"}).status, 403
        )
        self.assertEqual(
            self.post("/api/q/abc123/undo", **{"X-Firsthand-Token": "wrong"}).status,
            403,
        )
        self.assertEqual(self.engine.calls, [])

    def test_post_needs_a_json_object(self) -> None:
        self.assertEqual(
            self.post("/api/q/abc123/undo", **{"Content-Type": "text/plain"}).status,
            400,
        )
        self.assertEqual(self.post("/api/q/abc123/undo", b"answer=2").status, 400)
        self.assertEqual(self.post("/api/q/abc123/undo", b"[1, 2]").status, 400)
        self.assertEqual(self.post("/api/q/abc123/undo", b"\xff\xfe").status, 400)
        self.assertEqual(self.engine.calls, [])
        ok = self.post(
            "/api/q/abc123/undo", **{"Content-Type": "application/json; charset=utf-8"}
        )
        self.assertEqual(ok.status, 200)

    def test_body_over_the_limit_is_413(self) -> None:
        big = json.dumps({"answer": "x" * room.MAX_BODY_BYTES}).encode()
        resp = self.post("/api/q/abc123/lock", big)
        self.assertEqual(resp.status, 413)
        self.assertEqual(self.code(resp), "too_large")
        self.assertEqual(self.engine.calls, [])

    def test_answer_over_the_limit_is_refused(self) -> None:
        body = json.dumps({"answer": "x" * (room.MAX_ANSWER_CHARS + 1)}).encode()
        self.assertEqual(self.post("/api/q/abc123/lock", body).status, 400)
        self.assertEqual(self.engine.calls, [])

    def test_a_session_token_does_not_work_for_another_session(self) -> None:
        _, token_a = self.session()
        cookie_b, _ = self.session()
        headers = {
            "Host": self.host,
            "Cookie": cookie_b,
            "Origin": self.origin,
            "X-Firsthand-Token": token_a,
            "Content-Type": "application/json",
        }
        self.assertEqual(
            handle(self.room, "POST", "/api/q/abc123/undo", headers, b"{}").status, 403
        )

    # tickets

    def test_ticket_works_once(self) -> None:
        url = urlsplit(self.room.new_ticket("/q/r6t9kd"))
        first = self.get(f"{url.path}?{url.query}")
        self.assertEqual(first.status, 303)
        self.assertEqual(first.headers["Location"], "/q/r6t9kd")
        second = self.get(f"{url.path}?{url.query}")
        self.assertEqual(second.status, 403)
        self.assertIn(room.ticket_used_text().encode(), second.body)
        self.assertNotIn("Set-Cookie", second.headers)

    def test_ticket_expires(self) -> None:
        url = urlsplit(self.room.new_ticket())
        self.clock.now += room.TICKET_TTL_S + 1
        self.assertEqual(self.get(f"{url.path}?{url.query}").status, 403)

    def test_unknown_ticket_is_refused(self) -> None:
        self.assertEqual(self.get("/enter?t=nope").status, 403)
        self.assertEqual(self.get("/enter").status, 403)

    def test_next_cannot_leave_the_site(self) -> None:
        for bad in (
            "//evil.example/",
            "http://evil.example/",
            "evil",
            "/\\evil.example",
            "/a b",
            "",
        ):
            ticket = parse_qs(urlsplit(self.room.new_ticket()).query)["t"][0]
            resp = self.get(f"/enter?t={ticket}&next={bad}")
            self.assertEqual(resp.status, 303, bad)
            self.assertEqual(resp.headers["Location"], "/", bad)
        self.assertIn("next=/&", self.room.new_ticket("//evil.example") + "&")

    def test_cookie_is_httponly_and_strict(self) -> None:
        cookie = self.enter().headers["Set-Cookie"]
        parts = [p.strip() for p in cookie.split(";")]
        self.assertTrue(parts[0].startswith("fh_session="))
        self.assertIn("HttpOnly", parts)
        self.assertIn("SameSite=Strict", parts)
        self.assertIn("Path=/", parts)

    def test_sessions_file_keeps_only_a_digest(self) -> None:
        path = self.tmp / "config" / "room-sessions.json"
        server = RoomServer(self.engine, port=0, sessions_file=path, clock=self.clock)
        self.addCleanup(server.shutdown)
        url = urlsplit(server.new_ticket())
        host = f"127.0.0.1:{server.port}"
        resp = handle(server, "GET", f"{url.path}?{url.query}", {"Host": host}, b"")
        session_id = resp.headers["Set-Cookie"].split(";")[0].split("=", 1)[1]
        text = path.read_text()
        self.assertNotIn(session_id, text)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        # A restarted server keeps the session.
        again = RoomServer(self.engine, port=0, sessions_file=path, clock=self.clock)
        self.addCleanup(again.shutdown)
        host2 = f"127.0.0.1:{again.port}"
        cookie = f"fh_session={session_id}"
        self.assertEqual(
            handle(
                again, "GET", "/api/inbox", {"Host": host2, "Cookie": cookie}, b""
            ).status,
            200,
        )

    # headers

    def test_every_response_has_the_csp_and_no_cors(self) -> None:
        cookie, _ = self.session()
        responses = [
            self.get("/"),
            self.get("/static/room.js"),
            self.get("/static/nope.js"),
            self.get("/enter?t=nope"),
            self.enter(),
            self.get("/api/inbox"),
            self.get("/api/inbox", Cookie=cookie),
            self.get("/api/events", Cookie=cookie),
            self.get("/nowhere"),
            handle(self.room, "GET", "/", {"Host": "evil.example"}, b""),
            self.post("/api/q/abc123/undo"),
            self.post("/api/q/abc123/undo", Origin="-"),
        ]
        for resp in responses:
            self.assertEqual(
                resp.headers["Content-Security-Policy"],
                room.SECURITY_HEADERS["Content-Security-Policy"],
            )
            self.assertEqual(resp.headers["Cache-Control"], "no-store")
            self.assertEqual(resp.headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(resp.headers["Referrer-Policy"], "no-referrer")
            self.assertFalse(
                [h for h in resp.headers if h.lower().startswith("access-control-")]
            )
        self.assertIn(
            "script-src 'self'", room.SECURITY_HEADERS["Content-Security-Policy"]
        )
        self.assertIn(
            "frame-ancestors 'none'", room.SECURITY_HEADERS["Content-Security-Policy"]
        )

    def test_non_loopback_host_raises(self) -> None:
        for host in ("0.0.0.0", "localhost", "::1", "192.168.1.2"):
            with self.assertRaises(ValueError):
                RoomServer(self.engine, port=0, host=host)

    def test_taken_port_raises(self) -> None:
        with self.assertRaises(OSError):
            RoomServer(self.engine, port=self.room.port)


if __name__ == "__main__":
    unittest.main()
