"""SHELL: the firsthand command, with a fake control client."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest
import webbrowser

import support

from firsthand import cli, client, paths
from firsthand.model import FirsthandError

try:
    from firsthand import gitwatch, record  # noqa: F401 - CORE modules init needs

    HAVE_CORE = True
except ImportError:
    HAVE_CORE = False

STATUS = {
    "dial": "standard",
    "quiet": None,
    "asked_today": 0,
    "daily_limit": 1,
    "room": "http://127.0.0.1:4127",
    "project": {
        "id": "prj_3b9f52c1a7e0",
        "name": "orbit-pay",
        "test_command": "pytest -q",
        "watched": True,
        "why_not": None,
    },
    "question": {"ref": "r6t9kd", "line": "Firsthand (skip ok): which one?"},
}


class FakeClient:
    """Stands in for client.call: records each request and returns canned results."""

    def __init__(self) -> None:
        self.requests: list[tuple[str, dict, dict]] = []
        self.results: dict[str, object] = {}

    def __call__(self, op, args=None, **kw):
        self.requests.append((op, dict(args or {}), kw))
        result = self.results.get(op, {})
        if isinstance(result, Exception):
            raise result
        if callable(result):
            return result(args or {}, kw)
        return result


class CliCase(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.fake = FakeClient()
        self.swap(client, "call", self.fake)
        self.swap(sys, "stdin", io.StringIO(""))

    def swap(self, owner: object, name: str, value: object) -> None:
        old = getattr(owner, name)
        setattr(owner, name, value)
        self.addCleanup(setattr, owner, name, old)

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()


class CommandsTest(CliCase):
    def test_answer_and_skip(self) -> None:
        self.fake.results["answer"] = {
            "lines": ["Firsthand, Revert test. Matched. You said 2."]
        }
        code, out, _ = self.run_cli("answer", "2", "sure")
        self.assertEqual(code, 0)
        self.assertEqual(out, "Firsthand, Revert test. Matched. You said 2.\n")
        op, args, kw = self.fake.requests[-1]
        self.assertEqual((op, args), ("answer", {"text": "2 sure"}))
        self.assertEqual(kw["cwd"], os.getcwd())
        self.assertEqual(kw["agent"], cli.under_agent())
        self.fake.results["skip"] = {
            "lines": ["Skipped. Back to: x. Next: read the summary."]
        }
        self.assertEqual(
            self.run_cli("skip")[1], "Skipped. Back to: x. Next: read the summary.\n"
        )

    def test_error_ends_with_the_fix_and_exits_1(self) -> None:
        self.fake.results["answer"] = client.RemoteError(
            "No question is open. Nothing to answer.", "no_question"
        )
        code, out, err = self.run_cli("answer", "2")
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(err, "No question is open. Nothing to answer.\n")

    def test_quiet_off_on(self) -> None:
        self.fake.results["quiet"] = {
            "lines": ["Quiet for today. Runs still post notes."]
        }
        self.run_cli("quiet", "today")
        self.assertEqual(
            self.fake.requests[-1][:2], ("quiet", {"scope": "today", "on": True})
        )
        self.run_cli("quiet")
        self.assertEqual(self.fake.requests[-1][1]["scope"], "session")
        _, out, _ = self.run_cli("off")
        self.assertEqual(
            self.fake.requests[-1][:2], ("settings_set", {"changes": {"dial": "off"}})
        )
        self.assertEqual(out.strip(), cli.OFF_LINE)
        self.fake.results["settings_set"] = {"dial": "standard"}
        _, out, _ = self.run_cli("on")
        self.assertEqual(
            self.fake.requests[-1][:2],
            ("settings_set", {"changes": {"dial": "standard"}}),
        )
        self.assertEqual(out, "Firsthand is on: Standard.\n")

    def test_on_restores_the_dial_before_off(self) -> None:
        from firsthand.config import ConfigStore

        (paths.record_dir()).mkdir(parents=True)
        ConfigStore().set("dial_before_off", "deep")
        self.fake.results["settings_set"] = lambda args, kw: {
            "dial": args["changes"]["dial"]
        }
        self.assertEqual(self.run_cli("on")[1], "Firsthand is on: Deep.\n")

    def test_config_uses_the_project_here(self) -> None:
        self.fake.results["status"] = STATUS
        self.fake.results["settings_set"] = {
            "project": {
                "name": "orbit-pay",
                "test_command": "uv run pytest",
                "high_stakes": ["refunds/**"],
            }
        }
        code, out, _ = self.run_cli("config", "test-command", "uv run pytest")
        self.assertEqual(code, 0)
        self.assertEqual(
            self.fake.requests[-1][:2],
            (
                "settings_set",
                {
                    "changes": {"test_command": "uv run pytest"},
                    "project": "prj_3b9f52c1a7e0",
                },
            ),
        )
        self.assertEqual(out, "Test command for orbit-pay: uv run pytest\n")
        self.run_cli("config", "high-stakes", "refunds/**")
        self.assertEqual(
            self.fake.requests[-1][1]["changes"], {"high_stakes_add": "refunds/**"}
        )

    def test_config_outside_a_project(self) -> None:
        self.fake.results["status"] = {**STATUS, "project": None}
        code, _, err = self.run_cli("config", "test-command", "pytest")
        self.assertEqual(code, 1)
        self.assertIn("Run it from inside your project.", err)

    def test_status(self) -> None:
        self.fake.results["status"] = STATUS
        code, out, _ = self.run_cli("status")
        self.assertEqual(code, 0)
        self.assertIn("Open question: Firsthand (skip ok): which one?", out)
        self.assertIn("Asked today: 0 of 1.", out)
        self.assertIn("Dial: Standard.", out)
        self.assertIn("Test command: pytest -q", out)
        self.assertIn("Firsthand is running. Room: http://127.0.0.1:4127", out)
        self.assertFalse(self.fake.requests[-1][2]["start"])

    def test_status_lists_every_quiet_scope(self) -> None:
        self.fake.results["status"] = {
            **STATUS,
            "quiet": "session",
            "quiet_scopes": ["session", "today", "here"],
        }
        out = self.run_cli("status")[1]
        self.assertIn("Quiet: this session, today, this project.", out)

    def test_status_with_no_daemon(self) -> None:
        self.fake.results["status"] = client.DaemonUnavailable("not running")
        code, out, _ = self.run_cli("status")
        self.assertEqual(code, 0)
        self.assertIn("Firsthand is not running.", out)

    def test_journal_and_skills_text(self) -> None:
        self.fake.results["journal"] = {
            "scope": "orbit-pay",
            "entries": [
                {
                    "date": "14 Nov",
                    "task": "idempotent refunds",
                    "kind": "Revert test",
                    "chip_label": "Matched",
                    "rows": [{"label": "You said", "text": "2, test_x."}],
                }
            ],
        }
        self.swap(cli, "under_agent", lambda *a, **k: False)
        out = self.run_cli("journal")[1]
        self.assertIn("14 Nov  Revert test  idempotent refunds  Matched", out)
        self.assertIn("  You said: 2, test_x.", out)
        self.fake.results["skills"] = {
            "rows": [
                {
                    "n": 1,
                    "name": "Verification",
                    "level_line": "Too few answers. 1 of 2.",
                }
            ]
        }
        out = self.run_cli("skills")[1]
        self.assertIn("1. Verification\n  Too few answers. 1 of 2.", out)
        self.assertFalse(self.fake.requests[-1][2]["agent"])

    def test_journal_under_an_agent_is_refused(self) -> None:
        def refuse(args, kw):
            if kw["agent"]:
                raise client.RemoteError(
                    "Run it in a terminal you opened: firsthand journal", "refused"
                )
            return {"entries": []}

        os.environ["CLAUDECODE"] = "1"
        self.fake.results["journal"] = refuse
        code, out, err = self.run_cli("journal")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("firsthand journal", err)

    def test_room_opens_the_browser_without_printing_the_url(self) -> None:
        self.fake.results["room_ticket"] = {
            "url": "http://127.0.0.1:4127/enter?t=secret"
        }
        opened: list[str] = []
        self.swap(webbrowser, "open", lambda url: opened.append(url) or True)
        code, out, _ = self.run_cli("room")
        self.assertEqual(code, 0)
        self.assertEqual(opened, ["http://127.0.0.1:4127/enter?t=secret"])
        self.assertNotIn("secret", out)
        self.swap(webbrowser, "open", lambda url: False)
        self.swap(cli, "under_agent", lambda *a, **k: True)
        code, out, _ = self.run_cli("room")
        self.assertNotIn("secret", out)
        self.assertEqual(code, 1)
        self.swap(cli, "under_agent", lambda *a, **k: False)
        self.assertEqual(
            self.run_cli("room")[1], "http://127.0.0.1:4127/enter?t=secret\n"
        )

    def test_room_tty(self) -> None:
        self.swap(cli, "under_agent", lambda *a, **k: False)
        self.fake.results["question"] = {
            "ref": "r6t9kd",
            "context": "Verification | orbit-pay | refunds | change since 09:12",
            "lead": "It added 2 tests. Read them first.",
            "evidence": [
                {"n": 1, "name": "test_a", "path": "t.py", "line": 3, "asserts": []}
            ],
            "prompt": "Which of them would still pass with the change undone?",
            "picks": [
                {"value": "1"},
                {"value": "2"},
                {"value": "none"},
                {"value": "dont_know"},
            ],
            "multi": True,
            "result": None,
        }
        self.fake.results["answer_room"] = {
            "say": ["Firsthand: locked. The run has not finished."]
        }
        self.swap(sys, "stdin", io.StringIO("1 and 2\n"))
        code, out, _ = self.run_cli("room", "--tty")
        self.assertEqual(code, 0)
        self.assertIn("Reply the numbers, none or don't know. Or skip.", out)
        self.assertIn("Firsthand: locked.", out)
        self.assertEqual(
            self.fake.requests[-1][:2],
            ("answer_room", {"ref": "r6t9kd", "text": "1 and 2"}),
        )
        # A card of single picks (one test, Call it) still lists its words.
        self.fake.results["question"] = {
            **self.fake.results["question"],
            "multi": False,
            "picks": [{"value": "fails"}, {"value": "passes"}, {"value": "dont_know"}],
        }
        self.swap(sys, "stdin", io.StringIO("fails\n"))
        _, out, _ = self.run_cli("room", "--tty")
        self.assertIn("Reply with one of: fails, passes, don't know. Or skip.", out)
        self.swap(cli, "under_agent", lambda *a, **k: True)
        self.assertEqual(self.run_cli("room", "--tty")[0], 1)

    def test_hook_routes_without_parsing(self) -> None:
        self.swap(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"garbage")))
        self.assertEqual(self.run_cli("hook", "claude-code", "Stop"), (0, "", ""))
        self.assertEqual(self.run_cli("hook"), (0, "", ""))


class UnderAgentTest(support.TempHome):
    def test_environment_marker(self) -> None:
        self.assertTrue(cli.under_agent({"CLAUDECODE": "1"}, []))
        self.assertFalse(cli.under_agent({"CLAUDECODE": "0"}, []))
        self.assertFalse(cli.under_agent({"CLAUDECODE": ""}, []))
        self.assertFalse(cli.under_agent({}, []))

    def test_ancestor_name(self) -> None:
        self.assertTrue(cli.under_agent({}, ["bash", "claude", "login"]))
        self.assertTrue(cli.under_agent({}, ["/usr/local/bin/claude"]))
        self.assertFalse(cli.under_agent({}, ["bash", "zsh", "claude-helper"]))

    def test_real_ancestors_are_readable(self) -> None:
        self.assertIsInstance(cli._ancestor_names(), list)


@unittest.skipUnless(HAVE_CORE, "needs firsthand.record and firsthand.gitwatch (CORE)")
class InitTest(CliCase):
    def setUp(self) -> None:
        super().setUp()
        self.project = self.tmp / "orbit-pay"
        support.make_repo(self.project, {"app.py": "x = 1\n"})
        here = os.getcwd()
        os.chdir(self.project)
        self.addCleanup(os.chdir, here)
        self.claude = self.home / ".claude"
        self.claude.mkdir()
        self.original = b'{\n  "hooks": {\n    "Stop": [{"hooks": [{"type": "command", "command": "say done"}]}]\n  }\n}\n'
        paths.claude_settings().write_bytes(self.original)

    def test_without_a_terminal_and_yes_writes_nothing(self) -> None:
        code, out, _ = self.run_cli("init")
        self.assertEqual(code, 0)
        self.assertIn(
            "Firsthand will add itself to Claude Code. It will write these files:", out
        )
        self.assertIn("  ~/.claude/skills/firsthand/  new folder\n", out)
        launcher = paths.engine_dir("0.1.0") / "bin" / "firsthand"
        self.assertIn(
            f"  ~/.claude/settings.json      adds 6 hooks that call {launcher}\n", out
        )
        self.assertTrue(out.endswith("Run again with --yes to write these files.\n"))
        self.assertEqual(paths.claude_settings().read_bytes(), self.original)
        self.assertFalse(paths.claude_skill_file().exists())
        self.assertFalse(paths.home().exists())
        self.assertFalse(paths.config_home().exists())

    def test_yes_writes_everything_and_uninstall_keeps_the_record(self) -> None:
        code, out, err = self.run_cli(
            "init", "--yes", "--work-computer", "no", "--test-command", "pytest -q"
        )
        self.assertEqual(code, 0, err)
        settings = json.loads(paths.claude_settings().read_text())
        self.assertEqual(
            settings["hooks"]["Stop"][0]["hooks"][0]["command"], "say done"
        )
        launcher = paths.engine_dir("0.1.0") / "bin" / "firsthand"
        self.assertIn(f"{launcher} hook claude-code Stop", json.dumps(settings))
        self.assertTrue(paths.claude_skill_file().is_file())
        self.assertTrue(paths.install_manifest().is_file())
        self.assertTrue((paths.record_dir() / "FORMAT").is_file())
        self.assertIsNotNone(paths.port_file().read_text().strip())
        work = json.loads(
            (paths.record_dir() / "config" / "work_computer.json").read_text()
        )
        self.assertIs(work["value"], False)
        projects = list((paths.record_dir() / "projects").glob("*.json"))
        self.assertEqual(len(projects), 1)
        self.assertEqual(
            json.loads(projects[0].read_text())["test_command"], "pytest -q"
        )
        self.assertIn(
            "Firsthand is set up in Claude Code. It is on Standard: at most 1 question a day.",
            out,
        )
        self.assertIn("Your record: ~/.firsthand/record.", out)
        self.assertNotIn("This is a work computer.", out)
        self.assertNotIn("\u2014", out)

        code, out, _ = self.run_cli("uninstall")
        self.assertEqual(code, 0)
        self.assertEqual(paths.claude_settings().read_bytes(), self.original)
        self.assertFalse((self.claude / "skills").exists())
        self.assertTrue((paths.record_dir() / "FORMAT").is_file())
        self.assertIn("Restored ~/.claude/settings.json", out)
        self.assertIn("Your record is kept at ~/.firsthand/record.", out)

    def test_work_computer_notice(self) -> None:
        code, out, _ = self.run_cli("init", "--yes")
        self.assertEqual(code, 0)
        self.assertIn(
            "This is a work computer. Here is what your employer can and cannot see.",
            out,
        )
        work = json.loads(
            (paths.record_dir() / "config" / "work_computer.json").read_text()
        )
        self.assertIs(work["value"], True)

    def test_invalid_settings_stop_init(self) -> None:
        paths.claude_settings().write_text("{broken")
        code, _, err = self.run_cli("init", "--yes")
        self.assertEqual(code, 1)
        self.assertIn("run: firsthand init", err)
        self.assertEqual(paths.claude_settings().read_text(), "{broken")


class ErrorsTest(CliCase):
    def test_firsthand_error_is_caught(self) -> None:
        self.fake.results["skip"] = FirsthandError(
            "Nothing to skip. Run: firsthand status"
        )
        self.assertEqual(self.run_cli("skip")[0], 1)


if __name__ == "__main__":
    unittest.main()
