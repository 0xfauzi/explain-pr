"""End to end with real processes in a temporary home (build-2a-contract.md 10.5, 5 to 9).

Each test runs `python -m firsthand hook claude-code <Event>` with Claude Code's
hook JSON on stdin, which appends to the spool and starts a real daemon. The
daemon runs real checks with pytest from the shared test virtualenv. Nothing
reads or writes the real home: support.TempHome sets HOME and FIRSTHAND_HOME.
"""

from __future__ import annotations

import contextlib
import http.client
import json
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path

import fixtures
import support

from firsthand import client, paths
from firsthand.model import PRINT_PREFIX, FirsthandError

REPO = Path(__file__).resolve().parents[2]
HOOK_TIMEOUT_S = 20


def setUpModule() -> None:
    if support.pytest_python() is None:
        raise unittest.SkipTest(support.pytest_python_reason())


def wait_for(cond, timeout: float = 30.0, step: float = 0.05):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        got = cond()
        if got:
            return got
        time.sleep(step)
    raise AssertionError(f"timed out waiting for {getattr(cond, '__name__', cond)}")


class Process(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        python = support.pytest_python()
        assert python is not None
        self.venv = str(python.parent.parent)
        os.environ.pop("FIRSTHAND_NO_DAEMON", None)
        os.environ["VIRTUAL_ENV"] = self.venv
        os.environ["PYTHONPATH"] = str(REPO)
        os.environ.pop("CLAUDECODE", None)
        paths.ensure_private_dirs()
        paths.write_private(paths.port_file(), b"0\n")  # any free port, for tests
        self.addCleanup(self.stop_daemon)
        self.outputs: list[tuple[str, str]] = []

    # -------------------------------------------------------------- helpers

    def daemon_pid(self) -> int | None:
        try:
            return json.loads(paths.daemon_info_file().read_text())["pid"]
        except (OSError, ValueError, KeyError):
            return None

    def stop_daemon(self) -> None:
        pid = self.daemon_pid()
        with contextlib.suppress(FirsthandError, OSError):
            client.call("stop", start=False, timeout_s=2.0)
        if pid is not None:
            try:
                wait_for(lambda: not _alive(pid), timeout=5)
            except AssertionError:
                os.kill(pid, signal.SIGKILL)

    def hook(self, event: str, payload: dict) -> str:
        proc = subprocess.run(
            [sys.executable, "-m", "firsthand", "hook", "claude-code", event],
            input=json.dumps(payload).encode(),
            capture_output=True,
            env=dict(os.environ),
            cwd=str(REPO),
            timeout=HOOK_TIMEOUT_S,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stderr, b"", "a hook never writes to stderr")
        out = proc.stdout.decode()
        self.outputs.append((event, out))
        return out

    def base(self, root: Path, session: str, event: str) -> dict:
        return {
            "session_id": session,
            "transcript_path": "/nowhere/transcript.jsonl",
            "cwd": str(root),
            "hook_event_name": event,
        }

    def prompt(self, root: Path, text: str, session: str = "s1") -> str:
        return self.hook(
            "UserPromptSubmit",
            {**self.base(root, session, "UserPromptSubmit"), "prompt": text},
        )

    def stop(self, root: Path, session: str = "s1") -> str:
        payload = {
            **self.base(root, session, "Stop"),
            "stop_hook_active": False,
            "last_assistant_message": "Done. I fixed the refund bug and added a test.",
        }
        return self.hook("Stop", payload)

    def edit(self, root: Path, path: str, n: int, session: str = "s1") -> None:
        tool = {
            "tool_name": "Write",
            "tool_use_id": f"toolu_e{n}",
            "tool_input": {"file_path": str(root / path), "content": "..."},
        }
        self.hook("PreToolUse", {**self.base(root, session, "PreToolUse"), **tool})
        self.hook(
            "PostToolUse",
            {
                **self.base(root, session, "PostToolUse"),
                **tool,
                "tool_response": {"filePath": str(root / path), "success": True},
            },
        )

    def ran_tests(self, root: Path, session: str = "s1") -> None:
        tool = {
            "tool_name": "Bash",
            "tool_use_id": "toolu_run",
            "tool_input": {"command": "python -m pytest -q"},
        }
        self.hook("PreToolUse", {**self.base(root, session, "PreToolUse"), **tool})
        self.hook(
            "PostToolUse",
            {
                **self.base(root, session, "PostToolUse"),
                **tool,
                "tool_response": {
                    "stdout": "1 passed in 0.01s\n",
                    "stderr": "",
                    "interrupted": False,
                    "isImage": False,
                },
            },
        )

    def events(self, kind: str | None = None) -> list[dict]:
        found = []
        for path in sorted((paths.record_dir() / "events").glob("*/*/*.json")):
            try:
                event = json.loads(path.read_text())
            except ValueError:
                continue  # being written
            if kind is None or event["type"] == kind:
                found.append(event)
        return sorted(found, key=lambda e: e["id"])

    def fixture(self, name: str = "passes_anyway") -> Path:
        fx = fixtures.FIXTURES[name]
        return fixtures.build(self.tmp / name, fx)

    def warm(self, root: Path) -> None:
        """The day's first prompt, in another session: it is never asked about."""
        self.prompt(root, "good morning", session="s0")
        wait_for(lambda: self.events("task.started"))
        wait_for(self.idle_spool)
        self.stop(root, session="s0")

    def idle_spool(self) -> bool:
        try:
            return paths.spool_file().stat().st_size == 0
        except FileNotFoundError:
            return True

    def finished_change(self, root: Path, name: str = "passes_anyway") -> None:
        """A task with a change and a passing test run, the check left to finish."""
        self.prompt(root, "fix the refund bug")
        wait_for(lambda: len(self.events("task.started")) >= 2)
        fixtures.write_change(root, fixtures.FIXTURES[name])
        for n, path in enumerate(sorted(fixtures.FIXTURES[name].change)):
            self.edit(root, path, n)
        self.ran_tests(root)
        # The agent writes its summary while the check runs.
        wait_for(lambda: list(paths.keys_dir().glob("*.json")), timeout=60)


class ProcessTest(Process):
    def test_first_prompt_starts_the_daemon_and_sets_the_base(self) -> None:
        root = self.fixture()
        self.assertIsNone(self.daemon_pid())
        out = self.prompt(root, "fix the refund bug", session="s9")
        self.assertEqual(out, "", "no reply while the daemon starts")
        started = wait_for(lambda: self.events("task.started"))
        body = started[0]["body"]
        self.assertEqual(body["prompt"], "fix the refund bug")
        self.assertRegex(body["spool_id"], r"^[0-9a-f]{12}$")
        self.assertRegex(body["base_tree"], r"^[0-9a-f]{40}$")
        self.assertIsNotNone(wait_for(self.daemon_pid))

    def test_killed_daemon_restarts_and_loses_nothing(self) -> None:
        root = self.fixture()
        self.prompt(root, "fix the refund bug")
        wait_for(lambda: self.events("task.started"))
        pid = wait_for(self.daemon_pid)
        wait_for(self.idle_spool)
        os.kill(pid, signal.SIGKILL)
        wait_for(lambda: not _alive(pid))
        fixtures.write_change(root, fixtures.FIXTURES["passes_anyway"])
        self.edit(root, "refunds.py", 1)
        self.ran_tests(root)
        new_pid = wait_for(self.daemon_pid)
        wait_for(lambda: self.daemon_pid() != pid)
        self.stop(root)
        wait_for(
            lambda: any(e["body"]["kind"] == "done" for e in self.events("task.event"))
        )
        self.assertNotEqual(new_pid, pid)
        spool_ids = [
            e["body"]["spool_id"]
            for e in self.events()
            if e["type"].startswith("task.")
            and e["body"].get("kind") != "line_delivered"
        ]
        self.assertEqual(len(spool_ids), len(set(spool_ids)), "each line applied once")
        kinds = [e["body"]["kind"] for e in self.events("task.event")]
        self.assertEqual(kinds.count("test_run"), 1)
        self.assertEqual(kinds.count("done"), 1)

    def test_stop_prints_one_system_message_and_nothing_else(self) -> None:
        root = self.fixture()
        self.warm(root)
        self.finished_change(root)
        out = self.stop(root)
        data = json.loads(out)
        self.assertEqual(list(data), ["systemMessage"])
        line = data["systemMessage"]
        self.assertTrue(line.startswith("Firsthand (skip ok): "), line)
        self.assertNotIn("\n", line)
        for event, printed in self.outputs[:-1]:
            self.assertEqual(printed, "", f"{event} printed {printed!r}")
        reply = self.prompt(root, "passes")
        self.assertFalse(reply.startswith("{"))
        self.assertIn(PRINT_PREFIX, reply)
        self.assertIn("Firsthand, revert test. Matched. You said passes.", reply)
        for _, printed in self.outputs:
            for word in (
                "decision",
                "permissionDecision",
                "hookSpecificOutput",
                '"continue"',
            ):
                self.assertNotIn(word, printed)
        commits = support.git(paths.record_dir(), "log", "--format=%s").splitlines()
        wait_for(
            lambda: any(
                s.startswith("question ")
                for s in support.git(
                    paths.record_dir(), "log", "--format=%s"
                ).splitlines()
            )
        )
        self.assertTrue(commits)

    def test_room_ticket_inbox_lock_show(self) -> None:
        root = self.fixture()
        self.warm(root)
        self.finished_change(root)
        self.stop(root)
        url = client.call("room_ticket", {"next": "/"}, agent=False)["url"]
        port = int(url.split(":")[2].split("/")[0])
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
        conn.request(
            "GET", url.split(str(port), 1)[1], headers={"Host": f"127.0.0.1:{port}"}
        )
        res = conn.getresponse()
        res.read()
        self.assertEqual(res.status, 303)
        cookie = res.getheader("Set-Cookie").split(";")[0]
        headers = {"Host": f"127.0.0.1:{port}", "Cookie": cookie}
        session = _get(conn, "/api/session", headers)
        inbox = _get(conn, "/api/inbox", headers)
        self.assertEqual(len(inbox["now"]), 1)
        ref = inbox["now"][0]["ref"]
        post = {
            **headers,
            "Origin": f"http://127.0.0.1:{port}",
            "X-Firsthand-Token": session["token"],
            "Content-Type": "application/json",
        }
        held = _post(conn, f"/api/q/{ref}/lock", post, {"answer": "passes"})
        self.assertEqual(held["state"], "held")
        self.assertIsNone(held["result"])
        shown = _post(conn, f"/api/q/{ref}/show", post, {})
        self.assertEqual(shown["result"]["chip"], "matched")
        self.assertEqual(shown["call"]["channel"], "room")
        conn.close()


class InstallTest(Process):
    def test_init_then_uninstall_restores_settings_byte_for_byte(self) -> None:
        root = self.fixture()
        settings = paths.claude_settings()
        settings.parent.mkdir(parents=True)
        original = (
            b'{\n  "permissions": {"allow": ["Bash(ls:*)"]},\n'
            b'  "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo done"}]}]}\n}\n'
        )
        settings.write_bytes(original)
        cmd = [sys.executable, "-m", "firsthand"]
        init = subprocess.run(
            [
                *cmd,
                "init",
                "--yes",
                "--work-computer",
                "no",
                "--test-command",
                "pytest -q",
            ],
            capture_output=True,
            env=dict(os.environ),
            cwd=str(root),
            timeout=60,
            check=False,
        )
        self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
        merged = json.loads(settings.read_text())
        self.assertEqual(len(merged["hooks"]["Stop"]), 2)
        self.assertEqual(merged["permissions"], {"allow": ["Bash(ls:*)"]})
        self.assertTrue(paths.claude_skill_file().is_file())
        out = subprocess.run(
            [*cmd, "uninstall"],
            capture_output=True,
            env=dict(os.environ),
            cwd=str(root),
            timeout=60,
            check=False,
        )
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual(settings.read_bytes(), original)
        self.assertFalse(paths.claude_skill_file().exists())
        self.assertTrue((paths.record_dir() / "FORMAT").is_file(), "the record is kept")


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().split()[2] != "Z"
    except OSError:
        return True


def _get(conn: http.client.HTTPConnection, path: str, headers: dict) -> dict:
    conn.request("GET", path, headers=headers)
    res = conn.getresponse()
    body = res.read()
    assert res.status == 200, (res.status, body)
    return json.loads(body)


def _post(
    conn: http.client.HTTPConnection, path: str, headers: dict, data: dict
) -> dict:
    conn.request("POST", path, body=json.dumps(data).encode(), headers=headers)
    res = conn.getresponse()
    body = res.read()
    assert res.status == 200, (res.status, body)
    return json.loads(body)


if __name__ == "__main__":
    unittest.main()
