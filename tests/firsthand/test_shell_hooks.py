"""SHELL: the hook dispatcher."""

from __future__ import annotations

import contextlib
import fcntl
import io
import json
import os
import threading
import time
import unittest
from pathlib import Path
from typing import Self

import support

from firsthand import daemon, hooks, paths

FORBIDDEN = ("decision", "permissionDecision", "continue", "hookSpecificOutput")


def payload(event: str, **extra: object) -> bytes:
    body = {
        "session_id": "abc123",
        "cwd": "/home/sam/orbit-pay",
        "hook_event_name": event,
    }
    body.update(extra)
    return json.dumps(body).encode()


class FakeDaemonLock:
    """Holds run/daemon.lock the way a running daemon does."""

    def __enter__(self) -> Self:
        paths.ensure_private_dirs()
        self.fd = os.open(paths.daemon_lock_file(), os.O_RDWR | os.O_CREAT, 0o600)
        fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return self

    def __exit__(self, *exc: object) -> None:
        os.close(self.fd)


class Replier(threading.Thread):
    """Answers the first spool line with a reply file, as the daemon would."""

    def __init__(
        self, visible: str | None, context: str | None, session: str = "abc123"
    ) -> None:
        super().__init__(daemon=True)
        self.visible, self.context, self.session = visible, context, session
        self.event_id: str | None = None

    def run(self) -> None:
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            with contextlib.suppress(FileNotFoundError):
                text = paths.spool_file().read_text()
                if text.strip():
                    line = json.loads(text.splitlines()[0])
                    self.event_id = line["id"]
                    body = {
                        "v": 1,
                        "id": line["id"],
                        "session": self.session,
                        "event": line["event"],
                        "visible": self.visible,
                        "context": self.context,
                    }
                    paths.write_private(
                        paths.reply_file(line["id"]), json.dumps(body).encode()
                    )
                    return
            time.sleep(0.005)


class HooksTest(support.TempHome):
    def run_hook(self, event: str, data: bytes) -> tuple[int, str]:
        out = io.StringIO()
        code = hooks.main("claude-code", event, io.BytesIO(data), out)
        return code, out.getvalue()

    def spool_lines(self) -> list[dict]:
        if not paths.spool_file().exists():
            return []
        return [json.loads(x) for x in paths.spool_file().read_text().splitlines()]

    def test_one_line_per_call_mode_0600(self) -> None:
        for event in ("SessionStart", "PreToolUse", "Stop"):
            self.assertEqual(
                self.run_hook(event, payload(event, tool_name="Bash")), (0, "")
            )
        lines = self.spool_lines()
        self.assertEqual(
            [x["event"] for x in lines], ["session_start", "before_tool", "turn_end"]
        )
        self.assertEqual(len({x["id"] for x in lines}), 3)
        self.assertEqual(paths.spool_file().stat().st_mode & 0o777, 0o600)

    def test_garbage_and_unknown_input(self) -> None:
        cases = [
            ("Stop", b"not json"),
            ("Stop", b"[1, 2]"),
            ("Stop", b""),
            ("Notification", payload("Notification")),
            ("Stop", json.dumps({"cwd": "/x"}).encode()),
        ]
        for event, data in cases:
            self.assertEqual(self.run_hook(event, data), (0, ""))
        self.assertEqual(self.spool_lines(), [])
        log = paths.hook_log_file().read_text().splitlines()
        self.assertEqual(len(log), 3)  # the three that could not be parsed
        self.assertTrue(all("Error" in line for line in log))

    def test_unknown_agent(self) -> None:
        out = io.StringIO()
        self.assertEqual(
            hooks.main("nope", "Stop", io.BytesIO(payload("Stop")), out), 0
        )
        self.assertEqual(out.getvalue(), "")

    def test_missing_home(self) -> None:
        os.environ["FIRSTHAND_HOME"] = str(self.tmp / "plain-file" / "fh")
        (self.tmp / "plain-file").write_text("a file, not a folder")
        self.assertEqual(self.run_hook("Stop", payload("Stop")), (0, ""))

    def test_nothing_on_stderr(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.run_hook("Stop", b"{broken")
            self.run_hook("Stop", payload("Stop"))
        self.assertEqual(err.getvalue(), "")

    def test_reply_file_is_claimed_and_rendered(self) -> None:
        with FakeDaemonLock():
            replier = Replier("Firsthand (skip ok): a question line", None)
            replier.start()
            code, out = self.run_hook("Stop", payload("Stop"))
            replier.join()
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(out), {"systemMessage": "Firsthand (skip ok): a question line"}
        )
        self.assertFalse(paths.reply_file(replier.event_id).exists())
        self.assertFalse(
            paths.reply_file(replier.event_id).with_suffix(".claimed").exists()
        )
        for word in FORBIDDEN:
            self.assertNotIn(word, out)

    def test_prompt_context_is_plain_text(self) -> None:
        with FakeDaemonLock():
            replier = Replier(
                None, "Firsthand finding: t passes with the change undone."
            )
            replier.start()
            _, out = self.run_hook(
                "UserPromptSubmit", payload("UserPromptSubmit", prompt="go")
            )
            replier.join()
        self.assertEqual(out, "Firsthand finding: t passes with the change undone.")

    def test_reply_for_another_session_is_not_printed(self) -> None:
        with FakeDaemonLock():
            replier = Replier("a line", None, session="someone-else")
            replier.start()
            _, out = self.run_hook("Stop", payload("Stop"))
            replier.join()
        self.assertEqual(out, "")

    def test_no_reply_returns_within_the_budget(self) -> None:
        with FakeDaemonLock():
            started = time.monotonic()
            code, out = self.run_hook("Stop", payload("Stop"))
            took = time.monotonic() - started
        self.assertEqual((code, out), (0, ""))
        self.assertLess(took, 1.0)
        self.assertGreaterEqual(took, hooks.WAIT_S * 0.9)

    def test_held_spool_lock_does_not_stall_a_hook(self) -> None:
        paths.ensure_private_dirs()
        fd = os.open(paths.spool_file(), os.O_WRONLY | os.O_CREAT, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            with FakeDaemonLock():
                started = time.monotonic()
                code, out = self.run_hook(
                    "PreToolUse", payload("PreToolUse", tool_name="Bash")
                )
                took = time.monotonic() - started
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        self.assertEqual((code, out), (0, ""))
        self.assertLess(took, hooks.LOCK_WAIT_S + 0.5)
        self.assertEqual([x["event"] for x in self.spool_lines()], ["before_tool"])

    def test_no_wait_without_a_daemon_or_on_tool_events(self) -> None:
        started = time.monotonic()
        self.run_hook("Stop", payload("Stop"))
        with FakeDaemonLock():
            self.run_hook("PreToolUse", payload("PreToolUse", tool_name="Bash"))
        self.assertLess(time.monotonic() - started, hooks.WAIT_S)

    def test_no_daemon_flag_stops_the_spawn(self) -> None:
        self.run_hook("Stop", payload("Stop"))
        self.assertFalse(daemon.is_running())
        self.assertFalse(Path(paths.daemon_log_file()).exists())


if __name__ == "__main__":
    unittest.main()
