"""SHELL: the daemon process shell, with a fake engine and a fake Room."""

from __future__ import annotations

import json
import os
import threading
import time
import unittest

import support

from firsthand import client, daemon, events, hooks, paths
from firsthand.model import EngineError, HookReply


def line(event: str, n: int, session: str = "s1") -> bytes:
    return events.encode(
        {
            "v": 1,
            "id": f"{n:012x}",
            "at": "2026-11-14T09:12:03Z",
            "agent": "claude-code",
            "session": session,
            "cwd": "/home/sam/orbit-pay",
            "event": event,
        }
    )


class FakeEngine:
    def __init__(self) -> None:
        self.events: list[str] = []
        self.calls: list[tuple] = []
        self.delivered_calls: list[tuple[str, bool]] = []
        self.idle_value = True
        self.closed = False
        self.ticks = 0

    def handle(self, ev, reply) -> None:
        self.events.append(ev.id)
        if ev.event == "turn_end":
            reply(
                HookReply(
                    ev.id, ev.session, "turn_end", visible="Firsthand (skip ok): q"
                )
            )
        elif ev.event == "prompt_submit":
            reply(HookReply(ev.id, ev.session, "prompt_submit"))

    def delivered(self, event_id: str, ok: bool) -> None:
        self.delivered_calls.append((event_id, ok))

    def tick(self) -> None:
        self.ticks += 1

    def idle(self) -> bool:
        return self.idle_value

    def close(self) -> None:
        self.closed = True

    def _record(self, name: str, *args: object, **kw: object) -> dict:
        self.calls.append((name, args, kw))
        return {"view": name}

    def status(self, cwd=None):
        return self._record("status", cwd)

    def inbox(self, project=None):
        return self._record("inbox", project)

    def question(self, ref=None, *, cwd=None, seen=True):
        return self._record("question", ref, cwd=cwd)

    def lock(self, ref, answer, *, channel, final, cwd=None):
        if answer == "bad":
            raise EngineError("Reply 1, 2, 3 or none.", "invalid")
        self.calls.append(
            ("lock", (ref, answer), {"channel": channel, "final": final, "cwd": cwd})
        )
        return {"say": ["Firsthand, revert test. Matched. You said 2."], "result": None}

    def skip(self, ref, *, channel, final, cwd=None):
        self.calls.append(
            ("skip", (ref,), {"channel": channel, "final": final, "cwd": cwd})
        )
        return {"say": ["Skipped. Back to: refunds. Next: read the summary."]}

    def quiet(self, scope, on=True, *, cwd=None, session=None):
        self.calls.append(("quiet", (scope, on), {"cwd": cwd}))
        return {"lines": ["Quiet for today. Checks still run and post notes."]}

    def journal(self, project=None, limit=200):
        return self._record("journal", project, limit)

    def skills(self, project=None):
        return self._record("skills", project)

    def settings(self, project=None):
        return self._record("settings", project)

    def set_settings(self, changes, *, project=None, source, confirm=False):
        return self._record(
            "set_settings", dict(changes), project=project, source=source
        )


class FakeRoom:
    def __init__(self, engine, port: int) -> None:
        self.engine = engine
        self.port = port
        self.url = f"http://127.0.0.1:{port}"
        self.started = False
        self.stopped = False
        self.client_count = 0

    def start(self) -> None:
        self.started = True

    def shutdown(self) -> None:
        self.stopped = True

    def clients(self) -> int:
        return self.client_count

    def new_ticket(self, next_path: str = "/") -> str:
        return f"{self.url}/enter?t=tkt&next={next_path}"


class DaemonCase(support.TempHome):
    def start_daemon(
        self, **kw: object
    ) -> tuple[daemon.Daemon, FakeEngine, threading.Thread]:
        self.engine = FakeEngine()
        self.rooms: list[FakeRoom] = []
        self.contexts: list[daemon.DaemonContext] = []

        def engine_factory(ctx):
            self.contexts.append(ctx)
            return self.engine

        def room_factory(engine, port):
            room = FakeRoom(engine, port)
            self.rooms.append(room)
            return room

        d = daemon.Daemon(
            engine_factory=engine_factory, room_factory=room_factory, poll_s=0.01, **kw
        )
        self.result: list[int] = []
        thread = threading.Thread(
            target=lambda: self.result.append(d.run()), daemon=True
        )
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(d.stop)
        self.wait_for(paths.daemon_info_file().exists)
        return d, self.engine, thread

    def wait_for(self, check, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while not check():
            if time.monotonic() > deadline:
                self.fail("timed out waiting")
            time.sleep(0.01)


class SpoolAndRepliesTest(DaemonCase):
    def setUp(self) -> None:
        super().setUp()
        paths.ensure_private_dirs()
        self.engine = FakeEngine()
        self.d = daemon.Daemon()
        self.d._engine = self.engine

    def test_reads_in_order_saves_offset_waits_for_a_partial_line(self) -> None:
        first, second = line("session_start", 1), line("before_tool", 2)
        third = line("after_tool", 3)
        hooks.append_line(first + second + third[:10])
        offset = self.d._read_spool(0)
        self.assertEqual(self.engine.events, [f"{1:012x}", f"{2:012x}"])
        self.assertEqual(offset, len(first) + len(second))
        saved = json.loads(paths.spool_offset_file().read_text())
        self.assertEqual(saved, {"offset": offset})
        self.assertEqual(paths.spool_file().stat().st_size, offset + 10)

        with open(paths.spool_file(), "ab") as handle:
            handle.write(third[10:])
        offset = self.d._read_spool(offset)
        self.assertEqual(self.engine.events[-1], f"{3:012x}")
        self.assertEqual(offset, 0)
        self.assertEqual(paths.spool_file().stat().st_size, 0)
        self.assertEqual(
            json.loads(paths.spool_offset_file().read_text()), {"offset": 0}
        )

    def test_bad_lines_are_skipped(self) -> None:
        hooks.append_line(b"garbage\n" + line("turn_end", 7) + b'{"v": 9}\n')
        self.d._read_spool(0)
        self.assertEqual(self.engine.events, [f"{7:012x}"])

    def test_offset_past_the_end_restarts_at_zero(self) -> None:
        hooks.append_line(line("turn_end", 1))
        paths.write_private(paths.spool_offset_file(), b'{"offset": 99999}')
        self.assertEqual(daemon._read_offset(), 0)

    def _age(self) -> None:
        with self.d._waiting_lock:
            for key, (at, text) in list(self.d._waiting.items()):
                self.d._waiting[key] = (at - 2.0, text)

    def test_reply_file_and_delivery(self) -> None:
        self.d.write_reply(HookReply("aaaaaaaaaaaa", "s1", "turn_end", visible="line"))
        self.d.write_reply(HookReply("bbbbbbbbbbbb", "s1", "turn_end", visible="line"))
        self.d.write_reply(HookReply("cccccccccccc", "s1", "prompt_submit"))
        body = json.loads(paths.reply_file("aaaaaaaaaaaa").read_text())
        self.assertEqual(
            body,
            {
                "v": 1,
                "id": "aaaaaaaaaaaa",
                "session": "s1",
                "event": "turn_end",
                "visible": "line",
                "context": None,
            },
        )
        self.assertEqual(paths.reply_file("aaaaaaaaaaaa").stat().st_mode & 0o777, 0o600)
        os.rename(
            paths.reply_file("aaaaaaaaaaaa"), paths.out_dir() / "aaaaaaaaaaaa.claimed"
        )
        self.d._confirm_replies()
        # A claimed reply is confirmed at once; an unclaimed one waits a second.
        self.assertEqual(self.engine.delivered_calls, [("aaaaaaaaaaaa", True)])
        self._age()
        self.d._confirm_replies()
        self.assertEqual(
            sorted(self.engine.delivered_calls),
            [("aaaaaaaaaaaa", True), ("bbbbbbbbbbbb", False)],
        )
        self.assertFalse(paths.reply_file("bbbbbbbbbbbb").exists())
        self.assertFalse(paths.reply_file("cccccccccccc").exists())
        self.assertEqual(list(paths.out_dir().glob("*.expired")), [])


class ProcessTest(DaemonCase):
    def test_info_file_ops_and_clean_exit(self) -> None:
        _, engine, thread = self.start_daemon()
        info = json.loads(paths.daemon_info_file().read_text())
        room = self.rooms[0]
        self.assertEqual(info["pid"], os.getpid())
        self.assertEqual(info["engine"], "firsthand/0.1.0")
        self.assertEqual(info["port"], room.port)
        self.assertEqual(info["room"], room.url)
        self.assertEqual(info["socket"], str(paths.control_socket()))
        self.assertTrue(room.started)
        self.assertEqual(self.contexts[0].room_url, room.url)
        self.assertEqual(self.contexts[0].record_dir, paths.record_dir())
        self.assertIs(room.engine.target, engine)
        self.assertTrue(daemon.is_running())
        self.assertEqual(paths.control_socket().stat().st_mode & 0o777, 0o600)

        self.assertEqual(client.call("ping")["room"], room.url)
        self.assertEqual(
            client.call("answer", {"text": "2 sure"}, cwd="/p")["lines"][0][:9],
            "Firsthand",
        )
        self.assertEqual(
            engine.calls[-1],
            ("lock", (None, "2 sure"), {"channel": "chat", "final": True, "cwd": "/p"}),
        )
        client.call("answer_room", {"ref": "r6t9kd", "text": "2"})
        self.assertEqual(engine.calls[-1][1], ("r6t9kd", "2"))
        self.assertEqual(engine.calls[-1][2]["channel"], "room")
        self.assertEqual(client.call("skip", cwd="/p")["lines"][0][:7], "Skipped")
        self.assertEqual(
            engine.calls[-1][2], {"channel": "chat", "final": True, "cwd": "/p"}
        )
        client.call("quiet", {"scope": "today", "on": True}, cwd="/p")
        self.assertEqual(engine.calls[-1], ("quiet", ("today", True), {"cwd": "/p"}))
        self.assertEqual(client.call("status", cwd="/p"), {"view": "status"})
        self.assertEqual(engine.calls[-1][1], ("/p",))
        client.call("inbox", {"project": "prj_1"})
        client.call("question", {"ref": "r6t9kd"}, cwd="/p")
        self.assertEqual(engine.calls[-1], ("question", ("r6t9kd",), {"cwd": "/p"}))
        client.call("journal", {"limit": 5})
        self.assertEqual(engine.calls[-1], ("journal", (None, 5), {}))
        client.call("skills")
        client.call("settings_get")
        client.call("settings_set", {"changes": {"dial": "notes"}, "project": "prj_1"})
        self.assertEqual(
            engine.calls[-1],
            (
                "set_settings",
                ({"dial": "notes"},),
                {"project": "prj_1", "source": "cli"},
            ),
        )
        client.call("settings_set", {"changes": {"dial": "off"}}, agent=True)
        self.assertEqual(engine.calls[-1][2]["source"], "agent")
        url = client.call("room_ticket", {"next": "/q/r6t9kd"})["url"]
        self.assertEqual(url, f"{room.url}/enter?t=tkt&next=/q/r6t9kd")

        self.assertEqual(client.call("stop"), {})
        thread.join(5)
        self.assertEqual(self.result, [0])
        self.assertTrue(engine.closed)
        self.assertTrue(room.stopped)
        self.assertFalse(paths.daemon_info_file().exists())
        self.assertFalse(paths.control_socket().exists())
        self.assertFalse(daemon.is_running())

    def test_errors_and_refusals(self) -> None:
        self.start_daemon()
        with self.assertRaises(client.RemoteError) as caught:
            client.call("answer", {"text": "bad"})
        self.assertEqual(caught.exception.code, "invalid")
        self.assertEqual(caught.exception.message, "Reply 1, 2, 3 or none.")
        for op in ("journal", "skills", "answer_room", "room_ticket"):
            with self.assertRaises(client.RemoteError) as caught:
                client.call(op, {"ref": "x", "text": "1"}, agent=True)
            self.assertEqual(caught.exception.code, "refused", op)
            self.assertIn("firsthand", caught.exception.message)
        with self.assertRaises(client.RemoteError) as caught:
            client.call("nope")
        self.assertEqual(caught.exception.code, "invalid")
        with self.assertRaises(client.RemoteError) as caught:
            client.call("answer", {})
        self.assertEqual(caught.exception.code, "invalid")

    def test_spool_events_reach_the_engine_and_replies_are_written(self) -> None:
        _, engine, _ = self.start_daemon()
        hooks.append_line(line("prompt_submit", 1) + line("turn_end", 2))
        self.wait_for(lambda: len(engine.events) == 2)
        self.assertEqual(engine.events, [f"{1:012x}", f"{2:012x}"])
        self.wait_for(
            lambda: paths.reply_file(f"{2:012x}").exists() or engine.delivered_calls
        )
        self.wait_for(lambda: engine.delivered_calls == [(f"{2:012x}", False)])
        self.assertFalse(paths.reply_file(f"{1:012x}").exists())
        self.assertGreater(engine.ticks, 0)

    def test_second_daemon_exits_at_once(self) -> None:
        self.start_daemon()
        started = time.monotonic()
        self.assertEqual(
            daemon.Daemon(engine_factory=lambda ctx: FakeEngine()).run(), 0
        )
        self.assertLess(time.monotonic() - started, 1.0)
        self.assertEqual(len(self.contexts), 1)

    def test_idle_exit(self) -> None:
        _, engine, thread = self.start_daemon(idle_exit_s=0.3)
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(self.result, [0])
        self.assertTrue(engine.closed)

    def test_no_idle_exit_while_busy_or_watched(self) -> None:
        _, engine, thread = self.start_daemon(idle_exit_s=0.2)
        engine.idle_value = False
        self.rooms[0].client_count = 1
        time.sleep(0.5)
        self.assertTrue(thread.is_alive())
        engine.idle_value = True
        time.sleep(0.4)
        self.assertTrue(thread.is_alive())  # the Room still has a stream open
        self.rooms[0].client_count = 0
        thread.join(5)
        self.assertFalse(thread.is_alive())

    def test_runs_without_a_room(self) -> None:
        engine = FakeEngine()
        contexts = []

        def broken_room(engine, port):
            raise OSError("port taken")

        def factory(ctx):
            contexts.append(ctx)
            return engine

        d = daemon.Daemon(engine_factory=factory, room_factory=broken_room, poll_s=0.01)
        thread = threading.Thread(target=d.run, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(d.stop)
        self.wait_for(paths.daemon_info_file().exists)
        info = json.loads(paths.daemon_info_file().read_text())
        self.assertIsNone(info["room"])
        self.assertIsNone(info["port"])
        self.assertIsNone(contexts[0].room_url)
        with self.assertRaises(client.RemoteError) as caught:
            client.call("room_ticket")
        self.assertEqual(caught.exception.code, "unavailable")


class ClientTest(support.TempHome):
    def test_no_daemon_and_no_start(self) -> None:
        with self.assertRaises(client.DaemonUnavailable):
            client.call("ping", start=False)
        with self.assertRaises(client.DaemonUnavailable):
            client.call("ping")  # FIRSTHAND_NO_DAEMON is set, so nothing is started
        self.assertFalse(daemon.is_running())


if __name__ == "__main__":
    unittest.main()
