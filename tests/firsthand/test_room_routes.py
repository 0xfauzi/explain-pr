"""Each Room route calls the engine method of the contract and returns its view unchanged."""

from __future__ import annotations

import json
import unittest
from urllib.parse import urlsplit

import support

from firsthand import install
from firsthand.room import server as room
from firsthand.room.server import RoomServer, handle


class EngineFailure(Exception):
    """An engine error: string attributes code and message, as the contract gives."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class FakeEngine:
    """Records calls. Returns a view naming the call, or raises what it is told to."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.raise_next: BaseException | None = None

    def subscribe(self, fn):
        return lambda: None

    def __getattr__(self, name):
        def method(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            if self.raise_next is not None:
                exc, self.raise_next = self.raise_next, None
                raise exc
            return {
                "view": name,
                "args": list(args),
                "nested": {"held": None, "result": None},
            }

        return method


class RoomRoutesTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.engine = FakeEngine()
        self.room = RoomServer(self.engine, port=0)
        self.addCleanup(self.room.shutdown)
        self.host = f"127.0.0.1:{self.room.port}"
        url = urlsplit(self.room.new_ticket())
        enter = handle(
            self.room, "GET", f"{url.path}?{url.query}", {"Host": self.host}, b""
        )
        self.cookie = enter.headers["Set-Cookie"].split(";")[0]
        session = self.get("/api/session")
        self.token = json.loads(session.body)["token"]
        self.engine.calls.clear()

    def get(self, path: str):
        return handle(
            self.room, "GET", path, {"Host": self.host, "Cookie": self.cookie}, b""
        )

    def post(self, path: str, body: object):
        headers = {
            "Host": self.host,
            "Cookie": self.cookie,
            "Origin": f"http://{self.host}",
            "X-Firsthand-Token": self.token,
            "Content-Type": "application/json",
        }
        return handle(self.room, "POST", path, headers, json.dumps(body).encode())

    def assert_call(self, resp, name: str, args: tuple, kwargs: dict) -> None:
        self.assertEqual(resp.status, 200, resp.body)
        self.assertEqual(self.engine.calls, [(name, args, kwargs)])
        self.assertEqual(
            json.loads(resp.body),
            {
                "view": name,
                "args": list(args),
                "nested": {"held": None, "result": None},
            },
        )
        self.assertEqual(resp.headers["Content-Type"], "application/json")
        self.engine.calls.clear()

    def test_session_route(self) -> None:
        data = json.loads(self.get("/api/session").body)
        self.assertEqual(
            data,
            {
                "token": self.token,
                "room": self.room.url,
                "command": f"{install.command()} room",
            },
        )
        self.assertEqual(self.engine.calls, [])

    def test_reads(self) -> None:
        self.assert_call(self.get("/api/inbox"), "inbox", (), {"project": None})
        self.assert_call(
            self.get("/api/inbox?project=prj_1"), "inbox", (), {"project": "prj_1"}
        )
        self.assert_call(self.get("/api/q/r6t9kd"), "question", ("r6t9kd",), {})
        self.assert_call(
            self.get("/api/journal"), "journal", (), {"project": None, "limit": 200}
        )
        self.assert_call(
            self.get("/api/journal?project=prj_1&limit=5"),
            "journal",
            (),
            {"project": "prj_1", "limit": 5},
        )
        self.assert_call(
            self.get("/api/skills?project=prj_1"), "skills", (), {"project": "prj_1"}
        )
        self.assert_call(self.get("/api/settings"), "settings", (), {"project": None})

    def test_bad_limit_is_400(self) -> None:
        for bad in ("0", "-1", "abc", "1001"):
            resp = self.get(f"/api/journal?limit={bad}")
            self.assertEqual(resp.status, 400, bad)
        self.assertEqual(self.engine.calls, [])

    def test_question_writes(self) -> None:
        ref = "r6t9kd"
        room = {"channel": "room", "final": False}
        self.assert_call(
            self.post(f"/api/q/{ref}/lock", {"answer": "2"}), "lock", (ref, "2"), room
        )
        self.assert_call(
            self.post(f"/api/q/{ref}/lock", {"answer": "dont_know"}),
            "lock",
            (ref, "dont_know"),
            room,
        )
        self.assert_call(self.post(f"/api/q/{ref}/undo", {}), "undo", (ref,), {})
        self.assert_call(
            self.post(f"/api/q/{ref}/confidence", {"value": "high"}),
            "confidence",
            (ref, "high"),
            {},
        )
        self.assert_call(
            self.post(f"/api/q/{ref}/confidence", {"value": None}),
            "confidence",
            (ref, None),
            {},
        )
        self.assert_call(self.post(f"/api/q/{ref}/show", {}), "show", (ref,), {})
        self.assert_call(self.post(f"/api/q/{ref}/skip", {}), "skip", (ref,), room)
        self.assert_call(
            self.post(f"/api/q/{ref}/wrong-start", {}), "wrong_start", (ref,), {}
        )
        self.assert_call(
            self.post(f"/api/q/{ref}/dispute", {"reason": "the test is flaky"}),
            "dispute",
            (ref, "the test is flaky"),
            {},
        )

    def test_write_bodies_are_checked(self) -> None:
        ref = "r6t9kd"
        self.assertEqual(self.post(f"/api/q/{ref}/lock", {}).status, 400)
        self.assertEqual(self.post(f"/api/q/{ref}/lock", {"answer": 2}).status, 400)
        self.assertEqual(
            self.post(f"/api/q/{ref}/confidence", {"value": 1}).status, 400
        )
        self.assertEqual(
            self.post(f"/api/q/{ref}/dispute", {"reason": None}).status, 400
        )
        self.assertEqual(self.engine.calls, [])

    def test_settings_write(self) -> None:
        self.assert_call(
            self.post("/api/settings", {"changes": {"dial": "notes"}}),
            "set_settings",
            ({"dial": "notes"},),
            {"project": None, "source": "room", "confirm": False},
        )
        self.assert_call(
            self.post(
                "/api/settings",
                {
                    "changes": {"test_command": "pytest -q", "daily_limit": 2},
                    "project": "prj_1",
                    "confirm": True,
                },
            ),
            "set_settings",
            ({"test_command": "pytest -q", "daily_limit": 2},),
            {"project": "prj_1", "source": "room", "confirm": True},
        )

    def test_settings_body_is_checked(self) -> None:
        bad = [
            {},
            {"changes": {}},
            {"changes": "dial"},
            {"changes": {"colour": "red"}},
            {"changes": {"test_command": "pytest"}},
            {"changes": {"dial": "off"}, "confirm": "yes"},
            {"changes": {"dial": "off"}, "project": 7},
        ]
        for body in bad:
            self.assertEqual(self.post("/api/settings", body).status, 400, body)
        self.assertEqual(self.engine.calls, [])

    def test_error_codes_map_to_status(self) -> None:
        table = {
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
        for code, status in table.items():
            self.engine.raise_next = EngineFailure(code, f"message for {code}")
            resp = self.get("/api/q/r6t9kd")
            self.assertEqual(resp.status, status, code)
            self.assertEqual(
                json.loads(resp.body),
                {"error": {"code": code, "message": f"message for {code}"}},
            )

    def test_other_errors_are_500_internal_with_no_detail(self) -> None:
        for exc in (
            EngineFailure("locked", "secret detail"),
            RuntimeError("secret detail"),
            KeyError("x"),
        ):
            self.engine.raise_next = exc
            resp = self.post("/api/q/r6t9kd/show", {})
            self.assertEqual(resp.status, 500)
            error = json.loads(resp.body)["error"]
            self.assertEqual(error["code"], "internal")
            self.assertNotIn("secret", error["message"])

    def test_unknown_paths_are_404(self) -> None:
        for path in (
            "/nowhere",
            "/q/",
            "/q/a/b",
            "/static/page.html",
            "/static/../server.py",
            "/api/nowhere",
            "/api/q/r6t9kd/eat",
        ):
            self.assertEqual(self.get(path).status, 404, path)
        self.assertEqual(self.post("/api/q/r6t9kd/eat", {}).status, 404)
        self.assertEqual(self.post("/api/inbox", {}).status, 404)
        self.assertEqual(self.post("/journal", {}).status, 404)
        self.assertEqual(self.engine.calls, [])

    def test_static_files(self) -> None:
        css = self.get("/static/room.css")
        self.assertEqual(css.status, 200)
        self.assertEqual(css.headers["Content-Type"], "text/css; charset=utf-8")
        js = self.get("/static/room.js")
        self.assertEqual(js.headers["Content-Type"], "text/javascript; charset=utf-8")
        page = self.get("/q/r6t9kd")
        self.assertIn(b"/static/room.js", page.body)

    def test_fonts_and_licences_are_served_from_the_table(self) -> None:
        fonts = [k for k in room.STATIC if k.endswith(".woff2")]
        self.assertEqual(len(fonts), 9)
        for name in fonts:
            resp = self.get(f"/static/{name}")
            self.assertEqual(resp.status, 200, name)
            self.assertEqual(resp.headers["Content-Type"], "font/woff2")
            self.assertEqual(resp.body[:4], b"wOF2", name)
            for header, value in room.SECURITY_HEADERS.items():
                self.assertEqual(resp.headers[header], value, header)
        for name in ("OFL-Newsreader", "OFL-IBM-Plex-Mono", "OFL-IBM-Plex-Sans"):
            resp = self.get(f"/static/fonts/{name}.txt")
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers["Content-Type"], "text/plain; charset=utf-8")
            self.assertIn(b"SIL OPEN FONT LICENSE", resp.body.upper())
        for path in (
            "/static/fonts/nope.woff2",
            "/static/fonts/../room.js",
            "/static/fonts/",
            "/static/newsreader-latin-opsz-normal.woff2",
        ):
            self.assertEqual(self.get(path).status, 404, path)
        self.assertEqual(self.get("/static/room-views.js").status, 200)

    def test_tab_icons_are_svg_from_the_table(self) -> None:
        for name in ("icon.svg", "icon-open.svg"):
            resp = self.get(f"/static/{name}")
            self.assertEqual(resp.status, 200, name)
            self.assertEqual(resp.headers["Content-Type"], "image/svg+xml")
            self.assertTrue(resp.body.startswith(b"<svg "), name)
            self.assertNotIn(b"<script", resp.body)
            for header, value in room.SECURITY_HEADERS.items():
                self.assertEqual(resp.headers[header], value, header)
        self.assertIn(
            "img-src 'self';", room.SECURITY_HEADERS["Content-Security-Policy"]
        )
        self.assertEqual(self.get("/static/icon.png").status, 404)

    def test_csp_allows_only_own_fonts(self) -> None:
        csp = room.SECURITY_HEADERS["Content-Security-Policy"]
        self.assertIn("font-src 'self'", csp)
        self.assertIn("style-src 'self';", csp)
        self.assertNotIn("unsafe", csp)

    def test_event_stream_route(self) -> None:
        resp = self.get("/api/events")
        self.assertEqual(resp.status, 200)
        self.assertTrue(resp.stream)
        self.assertEqual(resp.headers["Content-Type"], "text/event-stream")


if __name__ == "__main__":
    unittest.main()
