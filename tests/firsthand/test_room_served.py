"""One real RoomServer on port 0, driven through urllib as a browser would."""

from __future__ import annotations

import json
import unittest
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

import support

from firsthand.room.server import RoomServer


class EngineError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class FakeEngine:
    """A tiny engine with one question: open, held, then shown."""

    def __init__(self) -> None:
        self.state = "open"
        self.held: dict | None = None
        self.calls: list[str] = []

    def subscribe(self, fn):
        return lambda: None

    def inbox(self, project=None):
        self.calls.append("inbox")
        now = (
            [{"ref": "r6t9kd", "href": "/q/r6t9kd"}]
            if self.state in ("open", "held")
            else []
        )
        return {
            "project": {"id": "prj_1", "name": "orbit-pay"},
            "now": now,
            "closing": "Asked today: 1 of 1.",
        }

    def question(self, ref, *, cwd=None, seen=True):
        if ref != "r6t9kd":
            raise EngineError("not_found", "No question has that id.")
        result = (
            {"chip": "matched", "chip_label": "Matched"}
            if self.state == "settled"
            else None
        )
        return {"ref": ref, "state": self.state, "held": self.held, "result": result}

    def lock(self, ref, answer, *, channel, final, cwd=None):
        self.calls.append(f"lock {answer} {channel} {final}")
        if self.state != "open":
            raise EngineError("state", "This question is already locked.")
        self.state = "held"
        self.held = {"kind": "pick", "answer": answer, "confidence": None}
        return self.question(ref)

    def undo(self, ref):
        self.calls.append("undo")
        self.state, self.held = "open", None
        return self.question(ref)

    def show(self, ref):
        self.calls.append("show")
        if self.state == "open":
            raise EngineError("state", "Pick an answer first.")
        self.state, self.held = "settled", None
        return self.question(ref)


class RoomServedTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.engine = FakeEngine()
        self.room = RoomServer(
            self.engine, port=0, sessions_file=self.tmp / "cfg" / "room-sessions.json"
        )
        self.room.start()
        self.addCleanup(self.room.shutdown)
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )
        self.token: str | None = None

    def get(self, path: str):
        with self.opener.open(self.room.url + path, timeout=5) as resp:
            return resp.status, resp.headers, resp.read()

    def post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(
            self.room.url + path,
            data=json.dumps(body).encode(),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": self.room.url,
                "X-Firsthand-Token": self.token or "",
            },
        )
        with self.opener.open(req, timeout=5) as resp:
            return json.loads(resp.read())

    def enter(self, next_path: str = "/") -> None:
        status, _, body = self.get(
            self.room.new_ticket(next_path).removeprefix(self.room.url)
        )
        self.assertEqual(status, 200)  # urllib followed the 303 to the page
        self.assertIn(b"/static/room.js", body)
        _, _, raw = self.get("/api/session")
        self.token = json.loads(raw)["token"]

    def test_ticket_inbox_lock_undo_show(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/api/inbox")
        self.assertEqual(caught.exception.code, 401)

        self.enter("/q/r6t9kd")
        self.assertEqual(len(self.jar), 1)

        _, _, raw = self.get("/api/inbox")
        inbox = json.loads(raw)
        self.assertEqual(inbox["now"][0]["href"], "/q/r6t9kd")

        view = self.post("/api/q/r6t9kd/lock", {"answer": "2"})
        self.assertEqual(view["state"], "held")
        self.assertIsNone(view["result"])

        view = self.post("/api/q/r6t9kd/undo", {})
        self.assertEqual(view["state"], "open")

        self.post("/api/q/r6t9kd/lock", {"answer": "none"})
        view = self.post("/api/q/r6t9kd/show", {})
        self.assertEqual(view["result"]["chip"], "matched")
        self.assertEqual(
            self.engine.calls,
            ["inbox", "lock 2 room False", "undo", "lock none room False", "show"],
        )

        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.post("/api/q/r6t9kd/lock", {"answer": "1"})
        self.assertEqual(caught.exception.code, 409)
        self.assertEqual(
            json.loads(caught.exception.read()),
            {"error": {"code": "state", "message": "This question is already locked."}},
        )

        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.get("/api/q/zzzzzz")
        self.assertEqual(caught.exception.code, 404)

    def test_post_with_a_foreign_origin_is_refused_over_http(self) -> None:
        self.enter()
        req = urllib.request.Request(
            self.room.url + "/api/q/r6t9kd/lock",
            data=b'{"answer": "2"}',
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": "http://evil.example",
                "X-Firsthand-Token": self.token,
            },
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.opener.open(req, timeout=5)
        self.assertEqual(caught.exception.code, 403)
        self.assertEqual(self.engine.state, "open")

    def test_oversized_body_over_http_is_413(self) -> None:
        self.enter()
        req = urllib.request.Request(
            self.room.url + "/api/q/r6t9kd/lock",
            data=b'{"answer": "' + b"x" * 30_000 + b'"}',
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Origin": self.room.url,
                "X-Firsthand-Token": self.token,
            },
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.opener.open(req, timeout=5)
        self.assertEqual(caught.exception.code, 413)


if __name__ == "__main__":
    unittest.main()
