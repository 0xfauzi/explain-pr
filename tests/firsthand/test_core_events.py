"""firsthand.events: the spool line codec and the secret scan."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import support

from firsthand import events
from firsthand.model import SpoolEvent

BASE = {
    "id": "3fa94c0b71de",
    "at": "2026-11-14T09:12:03Z",
    "agent": "claude-code",
    "session": "abc123",
    "cwd": "/home/sam/orbit-pay",
}

LINES = {
    "session_start": {"source": "startup", "venv": "/v"},
    "prompt_submit": {"prompt": "fix refunds", "venv": None},
    "before_tool": {
        "tool": "shell",
        "tool_use": "toolu_01",
        "command": "pytest -q",
        "exit": None,
        "failing": [],
        "paths": [],
    },
    "after_tool": {
        "tool": "edit",
        "tool_use": "toolu_02",
        "command": None,
        "exit": None,
        "failing": [],
        "paths": ["/home/sam/orbit-pay/a.py"],
    },
    "tool_failed": {
        "tool": "shell",
        "tool_use": "toolu_03",
        "command": "pytest -q",
        "exit": 1,
        "failing": ["tests/test_a.py::test_x"],
        "paths": [],
        "interrupted": True,
    },
    "turn_end": {},
}


# Built in pieces so that the repo's private-key hook does not read this fixture as a key.
_PEM_KIND = "RSA " + "PRIVATE KEY"
PEM = f"-----BEGIN {_PEM_KIND}-----\nMIIabc\n-----END {_PEM_KIND}-----"


class EventsTest(support.TempHome):
    def test_round_trip_each_kind(self) -> None:
        for kind, extra in LINES.items():
            line = {**BASE, "event": kind, **extra}
            raw = events.encode(line)
            self.assertTrue(raw.endswith(b"\n"))
            self.assertEqual(raw.count(b"\n"), 1)
            ev = events.decode(raw)
            self.assertIsInstance(ev, SpoolEvent, kind)
            self.assertEqual(ev.event, kind)
            self.assertEqual(ev.session, "abc123")
            for name, value in extra.items():
                got = getattr(ev, name)
                want = tuple(value) if isinstance(value, list) else value
                self.assertEqual(got, want, f"{kind}.{name}")

    def test_unknown_keys_dropped_and_keys_by_event(self) -> None:
        raw = events.encode(
            {
                **BASE,
                "event": "turn_end",
                "transcript_path": "/x",
                "prompt": "leak",
                "sub": True,
            }
        )
        obj = json.loads(raw)
        self.assertEqual(
            set(obj), {"v", "id", "at", "agent", "session", "cwd", "event", "sub"}
        )
        self.assertEqual(obj["v"], 1)
        raw = events.encode({**BASE, "event": "after_tool", "tool": "shell"})
        obj = json.loads(raw)
        self.assertEqual(obj["failing"], [])
        self.assertIsNone(obj["exit"])
        self.assertNotIn("interrupted", obj)

    def test_malformed_lines(self) -> None:
        for raw in (
            b"",
            b"   \n",
            b"{not json",
            b"[1,2]",
            b'{"v": 2, "event": "turn_end"}',
            json.dumps({**BASE, "v": 1, "event": "nonsense"}).encode(),
            json.dumps({"v": 1, "event": "turn_end"}).encode(),
            b"\xff\xfe",
        ):
            self.assertIsNone(events.decode(raw), raw)

    def test_prompt_cut(self) -> None:
        raw = events.encode({**BASE, "event": "prompt_submit", "prompt": "a" * 25_000})
        ev = events.decode(raw)
        self.assertEqual(len(ev.prompt), events.MAX_PROMPT_CHARS)
        self.assertTrue(ev.prompt_cut)
        short = events.decode(
            events.encode({**BASE, "event": "prompt_submit", "prompt": "a"})
        )
        self.assertFalse(short.prompt_cut)
        self.assertNotIn(
            b"prompt_cut",
            events.encode({**BASE, "event": "prompt_submit", "prompt": "a"}),
        )

    def test_line_too_long(self) -> None:
        with self.assertRaises(ValueError):
            events.encode({**BASE, "event": "after_tool", "command": "x" * 70_000})

    def test_failing_limits(self) -> None:
        raw = events.encode(
            {**BASE, "event": "tool_failed", "failing": ["y" * 400] * 80}
        )
        ev = events.decode(raw)
        self.assertEqual(len(ev.failing), 50)
        self.assertEqual(len(ev.failing[0]), 300)

    def test_stamp_and_id(self) -> None:
        self.assertEqual(
            events.now_stamp(datetime(2026, 11, 14, 9, 12, 3, 999, tzinfo=UTC)),
            "2026-11-14T09:12:03Z",
        )
        self.assertRegex(events.now_stamp(), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertRegex(events.new_event_id(), r"^[0-9a-f]{12}$")

    def test_scan_each_kind(self) -> None:
        cases = {
            "aws-key": "key AKIA" + "ABCDEFGHIJKLMNOP here",
            "github-token": "ghp_" + "a" * 36,
            "slack-token": "xoxb-" + "1234567890-abc",
            "api-key": "sk-" + "b" * 24,
            "private-key": PEM,
            "bearer": "Authorization: Bearer " + "c" * 30,
            "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.abcdefghij",
            "assignment": "PASSWORD=hunter2hunter2",
        }
        for kind, text in cases.items():
            out, found = events.scan_secrets(text)
            self.assertIn(kind, found, text)
            self.assertIn(f"[redacted: {kind}]", out)
        out, found = events.scan_secrets("github_pat_" + "d" * 45)
        self.assertEqual(found, ["github-token"])
        out, found = events.scan_secrets("api_key: " + "abcdefgh12345")
        self.assertEqual(out, "api_key: [redacted: assignment]")

    def test_scan_names_urls_and_mysql(self) -> None:
        cases = {
            "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY pytest": (
                "AWS_SECRET_ACCESS_KEY=[redacted: assignment] pytest"
            ),
            "psql postgres://admin:hunter2pass@db.prod.example.com:5432/app": (
                "psql postgres://admin:[redacted: url-password]@db.prod.example.com:5432/app"
            ),
            "mysql -u root -pS3cretPassw0rd! app": (
                "mysql -u root -p[redacted: mysql-password] app"
            ),
        }
        for text, expected in cases.items():
            self.assertEqual(events.scan_secrets(text)[0], expected)

    def test_clean_text_unchanged(self) -> None:
        for text in (
            "fix the refund bug in api/charges.py",
            "token = short",
            "",
            "pytest -q",
            "pytest -q -p no:cacheprovider tests/test_token.py::test_refresh_works",
            "primary_key=True",
        ):
            self.assertEqual(events.scan_secrets(text), (text, []))
