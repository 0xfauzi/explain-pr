"""SHELL: the Claude Code adapter."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import support

from firsthand import events
from firsthand.adapters import claude_code as cc
from firsthand.model import PRINT_PREFIX

AT = "2026-11-14T09:12:03Z"
ENV = {"VIRTUAL_ENV": "/home/sam/orbit-pay/.venv"}
TOKEN = "ghp_" + "a" * 36


def base(event: str, **extra: object) -> dict:
    payload = {
        "session_id": "abc123",
        "cwd": "/home/sam/orbit-pay",
        "hook_event_name": event,
        "transcript_path": "/home/sam/.claude/projects/x.jsonl",
    }
    payload.update(extra)
    return payload


def spool(event: str, payload: dict) -> dict | None:
    return cc.to_spool(event, payload, at=AT, event_id="3fa94c0b71de", environ=ENV)


class ToSpoolTest(support.TempHome):
    def assert_roundtrip(self, line: dict) -> None:
        decoded = events.decode(events.encode(line))
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.id, "3fa94c0b71de")

    def test_session_start(self) -> None:
        line = spool("SessionStart", base("SessionStart", source="startup"))
        self.assertEqual(line["event"], "session_start")
        self.assertEqual(line["source"], "startup")
        self.assertEqual(line["venv"], ENV["VIRTUAL_ENV"])
        self.assertEqual(line["agent"], "claude-code")
        self.assert_roundtrip(line)

    def test_prompt_with_token_is_redacted(self) -> None:
        line = spool(
            "UserPromptSubmit", base("UserPromptSubmit", prompt=f"use {TOKEN} now")
        )
        self.assertEqual(line["event"], "prompt_submit")
        self.assertNotIn(TOKEN, line["prompt"])
        self.assertIn("[redacted: github-token]", line["prompt"])
        self.assertNotIn("prompt_cut", line)
        self.assert_roundtrip(line)

    def test_long_prompt_is_cut(self) -> None:
        line = spool("UserPromptSubmit", base("UserPromptSubmit", prompt="x" * 25_000))
        self.assertEqual(len(line["prompt"]), events.MAX_PROMPT_CHARS)
        self.assertTrue(line["prompt_cut"])

    def test_bash_success(self) -> None:
        stdout = "..F\nFAILED tests/test_a.py::test_one - assert 1 == 2\n1 failed\n"
        payload = base(
            "PostToolUse",
            tool_name="Bash",
            tool_use_id="toolu_01",
            tool_input={"command": "pytest -q"},
            tool_response={
                "stdout": stdout,
                "stderr": "",
                "interrupted": False,
                "isImage": False,
            },
        )
        line = spool("PostToolUse", payload)
        self.assertEqual(line["event"], "after_tool")
        self.assertEqual(line["tool"], "shell")
        self.assertEqual(line["tool_use"], "toolu_01")
        self.assertEqual(line["command"], "pytest -q")
        self.assertEqual(line["exit"], 0)
        self.assertEqual(line["failing"], ["tests/test_a.py::test_one"])
        self.assertEqual(line["paths"], [])
        self.assert_roundtrip(line)

    def test_bash_failure(self) -> None:
        error = "Exit code 1\nFAILED tests/test_b.py::test_two - boom\n"
        payload = base(
            "PostToolUseFailure",
            tool_name="Bash",
            tool_use_id="toolu_02",
            tool_input={"command": f"API_TOKEN={TOKEN} pytest"},
            error=error,
            is_interrupt=True,
        )
        line = spool("PostToolUseFailure", payload)
        self.assertEqual(line["event"], "tool_failed")
        self.assertEqual(line["exit"], 1)
        self.assertEqual(line["failing"], ["tests/test_b.py::test_two"])
        self.assertTrue(line["interrupted"])
        self.assertNotIn(TOKEN, line["command"])
        self.assert_roundtrip(line)

    def test_bash_failure_without_exit_line(self) -> None:
        payload = base(
            "PostToolUseFailure",
            tool_name="Bash",
            tool_input={"command": "nosuch"},
            error="sh: nosuch: not found",
        )
        line = spool("PostToolUseFailure", payload)
        self.assertIsNone(line["exit"])
        self.assertNotIn("interrupted", line)

    def test_edit_and_write_paths(self) -> None:
        for tool in ("Edit", "Write", "MultiEdit"):
            payload = base(
                "PreToolUse",
                tool_name=tool,
                tool_use_id="t",
                tool_input={"file_path": "/home/sam/orbit-pay/refunds/service.py"},
            )
            line = spool("PreToolUse", payload)
            self.assertEqual(line["tool"], "edit", tool)
            self.assertEqual(line["paths"], ["/home/sam/orbit-pay/refunds/service.py"])
            self.assertIsNone(line["command"])
            self.assertIsNone(line["exit"])

    def test_ask_plan_and_other(self) -> None:
        kinds = {"AskUserQuestion": "ask", "ExitPlanMode": "plan", "Read": "other"}
        for tool, kind in kinds.items():
            line = spool(
                "PreToolUse", base("PreToolUse", tool_name=tool, tool_use_id="t9")
            )
            self.assertEqual(line["tool"], kind)
            self.assertEqual(line["tool_use"], "t9")

    def test_subagent_call(self) -> None:
        line = spool(
            "PreToolUse", base("PreToolUse", tool_name="Bash", agent_id="sub-1")
        )
        self.assertTrue(line["sub"])
        self.assertTrue(events.decode(events.encode(line)).sub)

    def test_stop(self) -> None:
        line = spool("Stop", base("Stop", last_assistant_message="secret plans"))
        self.assertEqual(line["event"], "turn_end")
        self.assertEqual(
            set(line), {"v", "id", "at", "agent", "session", "cwd", "event"}
        )

    def test_never_reads_transcript_or_last_message(self) -> None:
        for name in cc.EVENTS:
            payload = base(name, last_assistant_message="the last message", prompt="hi")
            text = json.dumps(spool(name, payload))
            self.assertNotIn("transcript", text)
            self.assertNotIn("projects/x.jsonl", text)
            self.assertNotIn("the last message", text)

    def test_unknown_event_or_no_session(self) -> None:
        self.assertIsNone(spool("Notification", base("Notification")))
        self.assertIsNone(spool("Stop", {"cwd": "/x"}))
        self.assertIsNone(spool("Stop", {"session_id": ""}))


class ParseTest(support.TempHome):
    def test_parse_exit(self) -> None:
        self.assertEqual(cc.parse_exit("Exit code 2\nmore"), 2)
        self.assertEqual(cc.parse_exit("Exit code 127"), 127)
        self.assertIsNone(cc.parse_exit("boom\nExit code 1"))
        self.assertIsNone(cc.parse_exit(""))

    def test_parse_failing_limits(self) -> None:
        text = "\n".join(f"FAILED t.py::test_{i} - x" for i in range(60))
        found = cc.parse_failing(text)
        self.assertEqual(len(found), 50)
        long_id = "t.py::" + "a" * 400
        self.assertEqual(len(cc.parse_failing(f"FAILED {long_id}")[0]), 300)
        self.assertEqual(cc.parse_failing("  FAILED indented\nPASSED x"), [])


class RenderTest(support.TempHome):
    FORBIDDEN = ("decision", "permissionDecision", "continue", "hookSpecificOutput")

    def test_turn_end_visible(self) -> None:
        out = cc.render(
            "turn_end", {"visible": "Firsthand (skip ok): a line", "context": None}
        )
        self.assertEqual(
            json.loads(out), {"systemMessage": "Firsthand (skip ok): a line"}
        )
        self.assertEqual(
            cc.render("Stop", {"visible": "x"}), json.dumps({"systemMessage": "x"})
        )

    def test_prompt_submit_context_is_plain_text(self) -> None:
        self.assertEqual(
            cc.render("prompt_submit", {"context": "Firsthand finding: a"}),
            "Firsthand finding: a",
        )
        self.assertEqual(
            cc.render("prompt_submit", {"context": '{"a": 1}'}), ' {"a": 1}'
        )

    def test_nothing_in_other_cases(self) -> None:
        self.assertEqual(cc.render("turn_end", {"visible": None, "context": "c"}), "")
        self.assertEqual(
            cc.render("prompt_submit", {"visible": "v", "context": None}), ""
        )
        self.assertEqual(cc.render("after_tool", {"visible": "v", "context": "c"}), "")

    def test_length_guard(self) -> None:
        self.assertEqual(cc.render("turn_end", {"visible": "x" * 10_001}), "")
        self.assertEqual(cc.render("prompt_submit", {"context": "x" * 10_001}), "")
        self.assertEqual(
            len(cc.render("prompt_submit", {"context": "x" * 10_000})), 10_000
        )

    def test_never_a_decision(self) -> None:
        for event in ("turn_end", "prompt_submit"):
            out = cc.render(event, {"visible": "v", "context": "c"})
            for word in self.FORBIDDEN:
                self.assertNotIn(word, out)


class SettingsFragmentTest(support.TempHome):
    def test_equals_build_2_section_3(self) -> None:
        def group(name: str, matcher: bool) -> list[dict]:
            handler = {
                "type": "command",
                "timeout": 5,
                "command": f"/abs/firsthand hook claude-code {name}",
            }
            return [
                {"matcher": "*", "hooks": [handler]}
                if matcher
                else {"hooks": [handler]}
            ]

        expected = {
            "hooks": {
                "SessionStart": group("SessionStart", False),
                "UserPromptSubmit": group("UserPromptSubmit", False),
                "PreToolUse": group("PreToolUse", True),
                "PostToolUse": group("PostToolUse", True),
                "PostToolUseFailure": group("PostToolUseFailure", True),
                "Stop": group("Stop", False),
            }
        }
        self.assertEqual(cc.settings_fragment(Path("/abs/firsthand")), expected)

    def test_launcher_path_is_quoted(self) -> None:
        command = cc.hook_command(Path("/home/sam smith/bin/firsthand"), "Stop")
        self.assertEqual(
            command, "'/home/sam smith/bin/firsthand' hook claude-code Stop"
        )


class SkillTextTest(support.TempHome):
    def test_frontmatter(self) -> None:
        text = cc.skill_text()
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        fields = dict(line.split(": ", 1) for line in match.group(1).splitlines())
        self.assertEqual(fields["name"], "firsthand")
        self.assertEqual(fields["user-invocable"], "false")
        self.assertLess(len(fields["description"]), 1536)
        self.assertIn('"Firsthand"', fields["description"])

    def test_holds_the_print_prefix_word_for_word(self) -> None:
        self.assertIn("\n" + PRINT_PREFIX + "\n", cc.skill_text())

    def test_body_rules(self) -> None:
        text = cc.skill_text()
        for phrase in (
            "Firsthand finding:",
            "firsthand answer",
            "~/.firsthand",
            '"skip" is final',
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("\u2014", text)


if __name__ == "__main__":
    unittest.main()
