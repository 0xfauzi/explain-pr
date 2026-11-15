"""Engine notices reach open event streams, and the Room counts its streams."""

from __future__ import annotations

import http.client
import json
import threading
import time
import unittest
from urllib.parse import urlsplit

import support

from firsthand.room.server import RoomServer, handle


class FakeEngine:
    """Holds the Room's listener so a test can send notices as the engine would."""

    def __init__(self) -> None:
        self.listeners: list = []
        self.unsubscribed = 0

    def subscribe(self, fn):
        self.listeners.append(fn)

        def remove() -> None:
            self.unsubscribed += 1
            self.listeners.remove(fn)

        return remove

    def notify(self, notice: dict) -> None:
        for fn in list(self.listeners):
            fn(notice)


def wait_for(test: unittest.TestCase, check, what: str, timeout: float = 5.0) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if check():
            return
        time.sleep(0.01)
    test.fail(f"timed out waiting for {what}")


class RoomEventsTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.engine = FakeEngine()
        self.room = RoomServer(self.engine, port=0)
        self.room.keepalive_s = 0.05
        self.room.start()
        self.addCleanup(self.room.shutdown)
        self.host = f"127.0.0.1:{self.room.port}"
        url = urlsplit(self.room.new_ticket())
        enter = handle(
            self.room, "GET", f"{url.path}?{url.query}", {"Host": self.host}, b""
        )
        self.cookie = enter.headers["Set-Cookie"].split(";")[0]
        self.conns: dict[int, http.client.HTTPConnection] = {}

    def open_stream(self) -> http.client.HTTPResponse:
        conn = http.client.HTTPConnection("127.0.0.1", self.room.port, timeout=5)
        self.addCleanup(conn.close)
        conn.request(
            "GET", "/api/events", headers={"Host": self.host, "Cookie": self.cookie}
        )
        resp = conn.getresponse()
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.getheader("Content-Type"), "text/event-stream")
        self.assertEqual(resp.readline(), b": open\n")
        self.assertEqual(resp.readline(), b"\n")
        self.conns[id(resp)] = conn
        return resp

    def next_data(self, resp: http.client.HTTPResponse) -> dict:
        while True:
            line = resp.readline()
            if not line:
                self.fail("the stream closed")
            if line.startswith(b"data: "):
                self.assertEqual(resp.readline(), b"\n")
                return json.loads(line[len(b"data: ") :])

    def test_subscribes_on_start_only(self) -> None:
        engine = FakeEngine()
        room = RoomServer(engine, port=0)
        self.assertEqual(engine.listeners, [])
        room.start()
        self.assertEqual(len(engine.listeners), 1)
        room.shutdown()
        self.assertEqual(engine.listeners, [])
        self.assertEqual(engine.unsubscribed, 1)

    def test_a_notice_reaches_an_open_stream_as_one_data_line(self) -> None:
        resp = self.open_stream()
        wait_for(self, lambda: self.room.clients() == 1, "one client")
        self.engine.notify(
            {"seq": 12, "topic": "inbox", "id": None, "extra": "dropped"}
        )
        self.assertEqual(
            self.next_data(resp), {"seq": 12, "topic": "inbox", "id": None}
        )
        self.engine.notify(
            {"seq": 13, "topic": "question", "id": "01JC8Y2F7H3QZ5W8N1P4R6T9KD"}
        )
        self.assertEqual(
            self.next_data(resp),
            {"seq": 13, "topic": "question", "id": "01JC8Y2F7H3QZ5W8N1P4R6T9KD"},
        )

    def test_keep_comment_lines(self) -> None:
        resp = self.open_stream()
        self.assertEqual(resp.readline(), b": keep\n")

    def test_clients_counts_streams_and_a_closed_one_is_removed(self) -> None:
        self.assertEqual(self.room.clients(), 0)
        first = self.open_stream()
        second = self.open_stream()  # kept: a dropped response closes its socket
        wait_for(self, lambda: self.room.clients() == 2, "two clients")
        first.close()
        self.conns[id(first)].close()
        # The next keep line fails to write on the closed socket, which removes it.
        wait_for(self, lambda: self.room.clients() == 1, "the closed stream to go")
        self.engine.notify({"seq": 1, "topic": "settings", "id": None})
        self.assertEqual(self.next_data(second)["topic"], "settings")

    def test_notice_never_blocks(self) -> None:
        resp = self.open_stream()
        wait_for(self, lambda: self.room.clients() == 1, "one client")
        done = threading.Event()

        def flood() -> None:
            for n in range(2000):
                self.engine.notify({"seq": n, "topic": "inbox", "id": None})
            done.set()

        threading.Thread(target=flood, daemon=True).start()
        self.assertTrue(done.wait(5), "notices blocked the engine thread")
        self.assertEqual(self.next_data(resp)["topic"], "inbox")

    def test_shutdown_ends_streams(self) -> None:
        resp = self.open_stream()
        wait_for(self, lambda: self.room.clients() == 1, "one client")
        self.room.shutdown()
        wait_for(self, lambda: self.room.clients() == 0, "streams to close")
        resp.read()


if __name__ == "__main__":
    unittest.main()
