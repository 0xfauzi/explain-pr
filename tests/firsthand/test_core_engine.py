"""firsthand.engine with a fake moment module: the loop without pytest.

The fake module has the moment surface of build-2a-contract.md section 5.1. Its
run() calls on_control and returns a key with results the test chooses, so these
tests need git (for the project and snapshots) but not pytest.
"""

from __future__ import annotations

import re
import types
import unittest
from datetime import UTC, datetime
from pathlib import Path

import fixtures
import support

from firsthand import paths
from firsthand.config import ConfigStore
from firsthand.engine import Engine
from firsthand.model import Candidate, CheckOutcome, EngineError, Key, KeyItem
from firsthand.moments import revert_test
from firsthand.record import Record, ensure_record

PACKAGE = Path(revert_test.__file__).resolve().parents[1]


def fake_module(results: tuple[str, ...]) -> types.SimpleNamespace:
    """A moment module whose check always finds `results`."""

    def match(m, store, new_id):
        real = revert_test.match(m, store, new_id)
        if real is None:
            return None
        return Candidate(**{**real.__dict__, "how": "pytest"})

    def run(c, ctx):
        ctx.on_control(True)
        tests = tuple(
            KeyItem(t.id, r, t.assert_line, t.assert_text, None)  # type: ignore[arg-type]
            for t, r in zip(c.tests, results, strict=False)
        )
        k = Key(
            c.check_id, c.kind, c.how, c.base_tree, c.head_tree, "", tests, (), (), 0.1
        )
        return CheckOutcome(k, None)

    return types.SimpleNamespace(
        KIND="revert_test",
        SKILL=1,
        HEADLINE="REVERT TEST",
        BREAKS=("test_run", "done"),
        match=match,
        run=run,
        score=revert_test.score,
        cue=revert_test.cue,
        finding=revert_test.finding,
        reply_words=revert_test.reply_words,
        parse_reply=revert_test.parse_reply,
    )


class FakeLoop(support.TempHome):
    results = ("fails_on_assertion", "still_passes", "cannot_run")

    def setUp(self) -> None:
        super().setUp()
        paths.ensure_private_dirs()
        self.record = Record(ensure_record())
        self.config = ConfigStore(paths.record_dir(), commit=self.record.commit)
        self.engine = Engine(
            record=self.record,
            settings=self.config,
            room_url="http://127.0.0.1:4127",
            clock=lambda: datetime(2026, 11, 14, 9, 30, tzinfo=UTC),
            tz=UTC,
            executor=lambda fn: fn(),
            moments=[fake_module(self.results)],  # type: ignore[list-item]
        )
        self.clock = fixtures.Clock()
        self.root = fixtures.build(self.tmp / "p", fixtures.FIXTURES["mixed3"])
        self.replies = []

    def feed(self, evs, deliver=True):
        out = []
        for ev in evs:
            got = []
            self.engine.handle(ev, got.append)
            for r in got:
                if deliver and (r.visible or r.context):
                    self.engine.delivered(r.event_id, True)
            out += got
        self.replies += out
        return out

    def ask(self):
        self.feed(fixtures.warmup(self.clock, self.root, None))
        self.feed(fixtures.task_start(self.clock, self.root, None))
        fixtures.write_change(self.root, fixtures.FIXTURES["mixed3"])
        stop = self.feed(
            fixtures.edits_and_stop(self.clock, self.root, fixtures.FIXTURES["mixed3"])
        )[-1]
        return stop, self.record.events(types=("moment.offered",))[-1]["moment"]

    def types_(self) -> list[str]:
        return [
            e["type"] for e in self.record.events() if not e["type"].startswith("task.")
        ]


class EngineTest(FakeLoop):
    def test_offer_line_at_the_done_stop(self) -> None:
        stop, _ = self.ask()
        self.assertIn(
            "Which one would still pass with the change undone?", stop.visible
        )
        self.assertEqual(self.types_(), ["moment.offered"])

    def test_room_pick_held_undone_repicked_shown(self) -> None:
        _, ref = self.ask()
        view = self.engine.lock(ref, "1", channel="room", final=False)
        self.assertEqual((view["state"], view["held"]["answer"]), ("held", "1"))
        self.assertTrue(view["can"]["show"])
        self.assertEqual(self.engine.undo(ref)["state"], "open")
        self.engine.lock(ref, "2", channel="room", final=False)
        self.engine.confidence(ref, "high")
        self.assertEqual(
            self.types_(), ["moment.offered"], "nothing recorded while held"
        )
        view = self.engine.show(ref)
        self.assertEqual(view["result"]["chip"], "matched")
        self.assertEqual(
            view["result"]["you_said"], "2, test_refund_response_is_stable. Sure."
        )
        self.assertEqual(
            self.types_(),
            [
                "moment.offered",
                "call.sealed",
                "call.confidence",
                "check.ran",
                "call.scored",
            ],
        )

    def test_dont_know_is_not_scored(self) -> None:
        _, ref = self.ask()
        view = self.engine.lock(ref, "dont_know", channel="room", final=False)
        self.assertEqual(view["state"], "settled")
        self.assertEqual(view["result"]["chip"], "not_scored")
        self.assertEqual(
            view["result"]["reason"], '"Don\'t know" is not counted as a miss.'
        )
        self.assertEqual(self.record.events(types=("call.scored",)), [])

    def test_invalid_reply(self) -> None:
        _, ref = self.ask()
        with self.assertRaises(EngineError) as caught:
            self.engine.lock(ref, "7", channel="room", final=False)
        self.assertEqual(caught.exception.code, "invalid")
        self.assertIn("1, 2, 3, none, don't know", caught.exception.message)

    def test_findings_wait_for_delivery(self) -> None:
        _, ref = self.ask()
        self.engine.skip(ref, channel="room", final=False)
        first = self.feed(
            [fixtures.prompt(self.clock, self.root, "go on")], deliver=False
        )[0]
        self.assertIn("Firsthand finding:", first.context)
        self.engine.delivered(first.event_id, False)
        again = self.feed(
            [fixtures.prompt(self.clock, self.root, "and then")], deliver=True
        )[0]
        self.assertIn("Firsthand finding:", again.context)
        last = self.feed([fixtures.prompt(self.clock, self.root, "done?")])[0]
        self.assertIsNone(last.context)
        delivered = [
            e
            for e in self.record.events(types=("task.event",))
            if e["body"]["kind"] == "line_delivered" and e["body"]["line"] == "finding"
        ]
        self.assertEqual(len(delivered), 1)

    def test_settings_widening(self) -> None:
        with self.assertRaises(EngineError) as caught:
            self.engine.set_settings({"daily_limit": 2}, source="agent")
        self.assertEqual(caught.exception.code, "refused")
        with self.assertRaises(EngineError) as caught:
            self.engine.set_settings({"daily_limit": 2}, source="room")
        self.assertEqual(caught.exception.code, "confirm")
        view = self.engine.set_settings({"daily_limit": 2}, source="room", confirm=True)
        self.assertEqual(view["daily_limit"], 2)
        view = self.engine.set_settings({"daily_limit": 1}, source="agent")
        self.assertEqual(view["daily_limit"], 1, "narrowing is allowed from the agent")
        self.engine.set_settings({"dial": "off"}, source="agent")
        self.assertEqual(self.config.load().dial_before_off, "standard")

    def test_quiet_today_closes_the_open_question(self) -> None:
        _, ref = self.ask()
        out = self.engine.quiet("today", True, cwd=str(self.root))
        self.assertEqual(
            out["lines"], ["Quiet for today. Checks still run and post notes."]
        )
        self.assertEqual(self.engine.question(ref)["state"], "closed")
        self.assertEqual(self.engine.inbox()["state"]["quiet"], "today")
        self.assertEqual(
            self.engine.quiet("today", False, cwd=str(self.root))["lines"],
            ["Quiet is off."],
        )


class ViewShapeTest(FakeLoop):
    """Each view has exactly the keys of build-2a-contract.md section 7.2."""

    def test_keys(self) -> None:
        _, ref = self.ask()
        self.engine.lock(ref, "2", channel="chat", final=True)
        inbox = self.engine.inbox()
        self.assertEqual(
            set(inbox),
            {
                "project",
                "projects",
                "state",
                "now",
                "waiting",
                "notes",
                "older_notes",
                "results",
                "closing",
                "empty",
            },
        )
        q = self.engine.question(ref)
        self.assertEqual(
            set(q),
            {
                "id",
                "ref",
                "kind",
                "state",
                "reason",
                "skip_ok",
                "context",
                "lead",
                "evidence",
                "trace",
                "prompt",
                "picks",
                "footer",
                "line",
                "can",
                "held",
                "call",
                "status_line",
                "say",
                "result",
            },
        )
        self.assertEqual(
            set(q["result"]),
            {
                "headline",
                "chip",
                "chip_label",
                "reason",
                "you_said",
                "what_happened",
                "cue",
                "back",
                "more",
            },
        )
        self.assertEqual(
            set(q["result"]["more"]),
            {"rows", "checked", "commands", "counts", "sure", "sent", "dispute"},
        )
        self.assertEqual(set(self.engine.journal()), {"scope", "entries"})
        self.assertEqual(
            set(self.engine.skills()["rows"][0]),
            {
                "n",
                "name",
                "level",
                "level_line",
                "counts",
                "fixed",
                "asked",
                "newest",
                "covers",
                "no_evidence",
                "checked",
            },
        )
        self.assertEqual(
            set(self.engine.settings()),
            {
                "dial",
                "daily_limit",
                "findings_to_agent",
                "work_computer",
                "quiet",
                "project",
                "record",
            },
        )
        self.assertEqual(
            set(self.engine.status(str(self.root))),
            {
                "dial",
                "quiet",
                "quiet_scopes",
                "asked_today",
                "daily_limit",
                "room",
                "project",
                "question",
            },
        )

    def test_empty_inbox_before_any_project(self) -> None:
        inbox = self.engine.inbox()
        self.assertIsNone(inbox["project"])
        self.assertTrue(inbox["empty"].startswith("Nothing here yet."))


class OutputRuleTest(unittest.TestCase):
    """Contract 8.3 rule 1: the engine never builds an agent line itself."""

    def test_engine_never_calls_the_line_builders(self) -> None:
        banned = re.compile(
            r"words\.(question_line|result_lines|finding_line|fact_line|pending_line|ack_line)\("
        )
        for name in ("engine.py", "engine_checks.py", "engine_actions.py", "views.py"):
            source = (PACKAGE / name).read_text(encoding="utf-8")
            self.assertIsNone(banned.search(source), name)

    def test_views_read_results_only_from_the_record(self) -> None:
        source = (PACKAGE / "views.py").read_text(encoding="utf-8")
        self.assertNotIn("KeyStore", source)
        self.assertNotIn("reveal(", source)
        self.assertNotIn(chr(0x2014), source)


if __name__ == "__main__":
    unittest.main()
