"""The fixture tests of build-2.md section 9, replayed against a real Engine.

Each test builds a fixture repo, replays recorded spool lines through a real
Engine with a real Record and ConfigStore, the inline executor and a fixed clock,
and runs pytest for real in the shared test virtualenv. It asserts on the record
events, the Stop line, the score for a reply, and that the fixture repo is
byte-identical before and after (support.repo_fingerprint).
"""

from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime
from pathlib import Path

import fixtures
import support

from firsthand import paths
from firsthand.config import ConfigStore
from firsthand.daemon import Daemon
from firsthand.engine import Engine
from firsthand.model import EngineError, HookReply
from firsthand.record import Record, ensure_record

ROOM = "http://127.0.0.1:4127"
NOW = datetime(2026, 11, 14, 9, 30, tzinfo=UTC)
RESULT_WORDS = (
    "passes with the change undone",
    "still passes",
    "fails on its assertion",
    "cannot run",
    "fails_on_assertion",
    "still_passes",
    "cannot_run",
)


def setUpModule() -> None:
    if support.pytest_python() is None:
        raise unittest.SkipTest(support.pytest_python_reason())


class Replay(support.TempHome):
    """A real Engine over a temporary home, fed spool lines one by one."""

    def setUp(self) -> None:
        super().setUp()
        python = support.pytest_python()
        assert python is not None
        self.venv = str(python.parent.parent)
        paths.ensure_private_dirs()
        self.record = Record(ensure_record())
        self.config = ConfigStore(paths.record_dir(), commit=self.record.commit)
        self.replies: list[HookReply] = []
        self.engine = self.new_engine()
        self.clock = fixtures.Clock()
        self.fingerprints: dict[str, list[str]] = {}

    def new_engine(self) -> Engine:
        return Engine(
            record=self.record,
            settings=self.config,
            room_url=ROOM,
            clock=lambda: NOW,
            tz=UTC,
            executor=lambda fn: fn(),
        )

    def feed(self, evs, *, deliver: bool = True) -> list[HookReply]:
        out = []
        for ev in evs:
            got: list[HookReply] = []
            self.engine.handle(ev, got.append)
            if ev.event in ("prompt_submit", "turn_end"):
                self.assertEqual(len(got), 1, f"one reply for {ev.event}")
            else:
                self.assertEqual(got, [], f"no reply for {ev.event}")
            for r in got:
                if deliver and (r.visible or r.context):
                    self.engine.delivered(r.event_id, True)
            out += got
        self.replies += out
        return out

    def project(self, name: str, folder: str | None = None) -> Path:
        fx = fixtures.FIXTURES[name]
        root = fixtures.build(self.tmp / (folder or name), fx)
        self.fingerprints[str(root)] = [support.repo_fingerprint(root)]
        return root

    def run_fixture(self, name: str, folder: str | None = None, warm: bool = True):
        """Replay a session up to the done-signal stop. Returns (root, stop reply)."""
        fx = fixtures.FIXTURES[name]
        root = self.project(name, folder)
        if warm:
            self.feed(fixtures.warmup(self.clock, root, self.venv))
        self.feed(fixtures.task_start(self.clock, root, self.venv))
        self.assertEqual(
            support.repo_fingerprint(root), self.fingerprints[str(root)][0]
        )
        fixtures.write_change(root, fx)
        self.fingerprints[str(root)].append(support.repo_fingerprint(root))
        replies = self.feed(fixtures.edits_and_stop(self.clock, root, fx))
        return root, replies[-1]

    def say(self, root: Path, text: str) -> HookReply:
        return self.feed([fixtures.prompt(self.clock, root, text)])[0]

    def stop(self, root: Path) -> HookReply:
        return self.feed([fixtures.stop(self.clock, root)])[0]

    def types(self, *, skip_task: bool = True) -> list[str]:
        return [
            e["type"]
            for e in self.record.events()
            if not (skip_task and e["type"].startswith("task."))
        ]

    def of(self, kind: str) -> list[dict]:
        return self.record.events(types=(kind,))

    def key_results(self) -> list[str]:
        ran = self.of("check.ran")
        self.assertTrue(ran, "a check ran")
        return [r["result"] for r in ran[-1]["body"]["results"]]

    def assert_untouched(self, root: Path) -> None:
        self.assertEqual(
            support.repo_fingerprint(root),
            self.fingerprints[str(root)][-1],
            "the fixture repo changed",
        )

    def question_commits(self) -> list[str]:
        log = support.git(paths.record_dir(), "log", "--format=%s")
        return [s for s in log.splitlines() if s.startswith("question ")]


class FixtureTest(Replay):
    """build-2.md section 9: one test per fixture."""

    def test_proves(self) -> None:
        root, stop = self.run_fixture("proves")
        self.assertIn("added 1 test, test_same_key_refunds_once", stop.visible or "")
        self.assertIn("Reply fails or passes.", stop.visible or "")
        r = self.say(root, "passes")
        self.assertEqual(self.key_results(), ["fails_on_assertion"])
        scored = self.of("call.scored")[-1]["body"]
        self.assertEqual(scored["result"], "miss")
        self.assertEqual(scored["outcome_kind"], "common")
        self.assertIn(
            "What would have shown it: It fails at tests/test_refunds.py:5.", r.context
        )
        self.assert_untouched(root)

    def test_passes_anyway(self) -> None:
        root, stop = self.run_fixture("passes_anyway")
        self.assertIsNotNone(stop.visible)
        r = self.say(root, "passes")
        self.assertEqual(self.key_results(), ["still_passes"])
        body = self.of("call.scored")[-1]["body"]
        self.assertEqual(
            (body["result"], body["outcome_kind"], body["catch"]),
            ("match", "uncommon", True),
        )
        self.assertIn("Firsthand, Revert test. Matched. You said passes.", r.context)
        self.assert_untouched(root)

    def test_needs_new_code(self) -> None:
        root, _ = self.run_fixture("needs_new_code")
        self.say(root, "fails")
        self.assertEqual(self.key_results(), ["cannot_run"])
        self.assertEqual(self.of("call.scored")[-1]["body"]["result"], "match")
        self.assert_untouched(root)

    def test_mixed3(self) -> None:
        root, stop = self.run_fixture("mixed3")
        self.assertIn(
            "1 test_same_key_refunds_once, 2 test_refund_response_is_stable, "
            "3 test_refund_total_adds_up. Reply the numbers, or none.",
            stop.visible,
        )
        r = self.say(root, "2 sure")
        self.assertEqual(
            self.key_results(), ["fails_on_assertion", "still_passes", "cannot_run"]
        )
        self.assertEqual(
            self.types(),
            [
                "moment.offered",
                "call.sealed",
                "call.confidence",
                "check.ran",
                "call.scored",
            ],
        )
        self.assertEqual(self.of("call.scored")[-1]["body"]["result"], "match")
        self.assertTrue(r.context.startswith("Firsthand result for the reply above."))
        self.assertEqual(len(self.question_commits()), 1)
        self.assertTrue(self.question_commits()[0].endswith(" match"))
        self.assert_untouched(root)

    def test_edited_test(self) -> None:
        root, stop = self.run_fixture("edited_test")
        self.assertIn("edited 1 test, test_duplicate_keys", stop.visible)
        offered = self.of("moment.offered")[-1]["body"]
        self.assertEqual(
            [(t["id"], t["status"]) for t in offered["tests"]],
            [("tests/test_refunds.py::test_duplicate_keys", "edited")],
        )
        self.say(root, "fails")
        self.assertEqual(self.key_results(), ["fails_on_assertion"])
        self.assert_untouched(root)

    def test_control_fails(self) -> None:
        root, stop = self.run_fixture("control_fails")
        self.assertIsNone(stop.visible)
        unavailable = self.of("check.unavailable")
        self.assertEqual(len(unavailable), 1)
        self.assertEqual(unavailable[0]["body"]["reason"], "does not match here")
        self.assertEqual(unavailable[0]["body"]["step"], "control")
        self.assertEqual(self.of("moment.offered"), [])
        self.assertEqual(self.of("check.ran"), [])
        self.assert_untouched(root)

    def test_no_tests(self) -> None:
        root, stop = self.run_fixture("no_tests")
        self.assertIsNone(stop.visible)
        self.assertEqual(self.of("task.event")[-1]["body"]["kind"], "done")
        for kind in ("moment.offered", "check.ran", "check.unavailable", "note.posted"):
            self.assertEqual(self.of(kind), [], kind)
        self.assert_untouched(root)

    def test_high_stakes_with_the_day_used(self) -> None:
        first, _ = self.run_fixture("passes_anyway", "first")
        self.say(first, "passes")
        root, stop = self.run_fixture("high_stakes", warm=False)
        self.assertEqual(
            stop.visible,
            "Firsthand: test_refund_response_is_stable passes with the change undone. "
            "payments/ is marked high stakes.",
        )
        offered = [
            e for e in self.of("moment.offered") if e["project"] != self.pid(first)
        ]
        self.assertEqual(offered, [])
        note = self.of("note.posted")[-1]["body"]
        self.assertEqual(note["printed"], "fact")
        self.assertEqual(note["high_stakes"], "**/payments/**")
        self.assertIsNone(self.stop(root).visible, "a fact line prints once")
        self.assert_untouched(first)
        self.assert_untouched(root)

    def test_high_stakes_offered_then_moved_on(self) -> None:
        root, stop = self.run_fixture("high_stakes")
        self.assertIn("Would it still pass with the change undone?", stop.visible)
        r = self.say(root, "thanks, now update the docs")
        self.assertNotIn("Firsthand: ", r.context or "")
        closed = self.of("moment.closed")[-1]["body"]
        self.assertEqual(closed["how"], "moved-on")
        nxt = self.stop(root)
        self.assertEqual(
            nxt.visible,
            "Firsthand: test_refund_response_is_stable passes with the change undone. "
            "payments/ is marked high stakes.",
        )
        self.assertEqual(self.of("note.posted")[-1]["body"]["printed"], "fact")
        self.assert_untouched(root)

    def pid(self, root: Path) -> str:
        from firsthand import gitwatch

        found = gitwatch.project_id(root)
        assert found is not None
        return found


class RuleTest(Replay):
    """The four extra assertions of build-2a-contract.md section 10.5."""

    def views_text(self, ref: str | None = None) -> str:
        parts = [self.engine.inbox(), self.engine.journal(), self.engine.skills()]
        if ref is not None:
            parts.append(self.engine.question(ref))
        return json.dumps(parts)

    def assert_no_result(self, text: str) -> None:
        self.assertNotIn('"decision"', text)
        for word in RESULT_WORDS:
            self.assertNotIn(word, text)

    def test_nothing_before_the_lock(self) -> None:
        root, _ = self.run_fixture("mixed3")
        ref = self.of("moment.offered")[-1]["moment"]
        self.assert_no_result(self.views_text(ref))
        status = self.engine.status(str(root))
        self.assert_no_result(json.dumps(status))
        self.engine.lock(ref, "2", channel="room", final=False)
        self.assertEqual(self.engine.question(ref)["state"], "held")
        self.assert_no_result(self.views_text(ref))
        self.assertEqual(self.of("check.ran"), [], "nothing revealed while held")
        for r in self.replies:
            self.assert_no_result(json.dumps([r.visible, r.context]))
        view = self.engine.show(ref)
        self.assertEqual(view["result"]["chip"], "matched")

    def test_second_change_asks_nothing_and_writes_a_note(self) -> None:
        root, _ = self.run_fixture("passes_anyway")
        self.say(root, "passes")
        self.stop(root)
        self.feed([fixtures.prompt(self.clock, root, "add a second check")])
        support.write_files(
            root,
            {
                "refunds.py": fixtures.FIXED_REFUNDS + "\n\nVERSION = 2\n",
                "tests/test_more.py": fixtures.TEST_PASSES_ANYWAY.replace(
                    "test_refund_response_is_stable", "test_refund_again"
                ),
            },
        )
        stop = self.stop(root)
        self.assertIsNone(stop.visible)
        self.assertEqual(len(self.of("moment.offered")), 1)
        notes = self.of("note.posted")
        self.assertEqual(len(notes), 1)
        self.assertIn(
            "test_refund_again passes with the change undone", notes[0]["body"]["fact"]
        )
        nxt = self.say(root, "ok")
        self.assertIn(
            "Firsthand finding: tests/test_more.py::test_refund_again", nxt.context
        )

    def ended(self, how: str) -> None:
        root, stop = self.run_fixture("passes_anyway")
        self.assertIsNotNone(stop.visible)
        if how == "skip":
            r = self.say(root, "skip")
            self.assertIn("Skipped. Back to: fix the refund bug.", r.context)
            self.assertEqual(len(self.of("moment.skipped")), 1)
        elif how == "quiet":
            r = self.say(root, "quiet")
            self.assertIn("Quiet for this session.", r.context)
            self.assertEqual(self.of("moment.closed")[-1]["body"]["how"], "quiet")
        elif how == "off":
            self.engine.set_settings({"dial": "off"}, source="cli")
            self.assertEqual(self.of("moment.closed")[-1]["body"]["how"], "off")
        else:
            self.say(root, "looks good, commit it later")
            self.assertEqual(self.of("moment.closed")[-1]["body"]["how"], "moved-on")
        self.assertIsNone(self.stop(root).visible)
        self.assertIsNone(self.stop(root).visible)
        self.assertEqual(self.of("call.scored"), [])

    def test_skip_ends_it(self) -> None:
        self.ended("skip")

    def test_quiet_ends_it(self) -> None:
        self.ended("quiet")

    def test_off_ends_it(self) -> None:
        self.ended("off")

    def test_next_prompt_ends_it(self) -> None:
        self.ended("prompt")

    def scored_by(self, how: str, warm: bool) -> dict:
        root, _ = self.run_fixture("mixed3", f"mixed3-{how}", warm=warm)
        ref = self.of("moment.offered")[-1]["moment"]
        if how == "chat":
            self.say(root, "2")
        elif how == "room":
            self.engine.lock(ref, "2", channel="room", final=False)
            self.engine.show(ref)
        else:
            daemon = Daemon()
            daemon._engine = self.engine  # the control op path, without a socket
            result = daemon.dispatch(
                "answer", {"text": "2"}, cwd=str(root), agent=False
            )
            self.assertTrue(
                result["lines"][0].startswith("Firsthand, Revert test. Matched.")
            )
        scored = self.of("call.scored")[-1]
        self.assertEqual(scored["moment"], ref)
        body = dict(scored["body"])
        body.pop("check")
        return body

    def test_three_ways_score_the_same(self) -> None:
        self.config.set("daily_limit", 3)
        chat = self.scored_by("chat", warm=True)
        self.assertEqual(chat["result"], "match")
        for how in ("room", "cli"):
            with self.subTest(how=how):
                self.assertEqual(self.scored_by(how, warm=False), chat)
        self.assertEqual(len(self.question_commits()), 3)


class EngineRulesTest(Replay):
    """Smaller engine rules the fixtures reach."""

    def test_repeated_spool_id_is_ignored(self) -> None:
        root = self.project("passes_anyway")
        evs = fixtures.warmup(self.clock, root, self.venv)
        self.feed(evs)
        got: list[HookReply] = []
        self.engine.handle(evs[1], got.append)
        self.assertEqual(got, [])
        self.assertEqual(len(self.of("task.started")), 1)

    def test_restart_resumes_an_open_question(self) -> None:
        root, _ = self.run_fixture("mixed3")
        ref = self.of("moment.offered")[-1]["moment"]
        self.engine.close()
        self.engine = self.new_engine()
        self.assertEqual(self.engine.question(ref)["state"], "open")
        r = self.say(root, "none")
        self.assertIn("Did not match", r.context)
        self.assertEqual(self.of("call.scored")[-1]["body"]["result"], "miss")

    def test_unseen_question_survives_a_prompt(self) -> None:
        root, stop = self.run_fixture("mixed3")
        # The dispatcher never claimed the line: deliver nothing.
        self.engine.delivered(stop.event_id, False)
        self.engine.moments[self.of("moment.offered")[-1]["moment"]].seen = False
        self.feed([fixtures.prompt(self.clock, root, "carry on")], deliver=False)
        self.assertEqual(self.of("moment.closed"), [])
        again = self.stop(root)
        self.assertIn("Which of them would still pass", again.visible)

    def test_two_skips_stop_the_session(self) -> None:
        root, _ = self.run_fixture("passes_anyway")
        self.say(root, "skip")
        self.engine.set_settings({"daily_limit": 3}, source="cli")
        self.commit(root)  # a new change: one question per change
        self.feed([fixtures.prompt(self.clock, root, "next task")])
        support.write_files(
            root,
            {
                "refunds.py": fixtures.FIXED_REFUNDS + "\nX = 1\n",
                "tests/test_x.py": fixtures.TEST_PROVES,
            },
        )
        stop = self.stop(root)
        self.assertIn("Firsthand (skip ok)", stop.visible)
        r = self.say(root, "skip")
        self.assertIn("No more questions this session.", r.context)
        self.commit(root)
        self.feed([fixtures.prompt(self.clock, root, "third task")])
        support.write_files(
            root,
            {
                "refunds.py": fixtures.FIXED_REFUNDS + "\nX = 2\n",
                "tests/test_y.py": fixtures.TEST_PROVES,
            },
        )
        self.assertIsNone(self.stop(root).visible)
        self.assertEqual(len(self.of("moment.offered")), 2)

    def commit(self, root: Path) -> None:
        """The person commits: HEAD moves, so the change ends."""
        support.git(root, "add", "-A")
        support.git(root, "commit", "-q", "-m", "work")

    def test_wrong_start_with_no_earlier_start_changes_nothing(self) -> None:
        root, _ = self.run_fixture("mixed3")
        ref = self.of("moment.offered")[-1]["moment"]
        with self.assertRaises(EngineError) as raised:
            self.engine.wrong_start(ref)
        self.assertEqual(raised.exception.code, "state")
        self.assertEqual(self.of("moment.closed"), [])
        self.assertEqual(len(self.of("moment.offered")), 1)
        view = self.engine.question(ref)
        self.assertIsNone(view["result"])
        self.assertTrue(view["can"]["lock"])
        self.assert_untouched(root)

    def _two_task_change(self) -> tuple[Path, str]:
        """The fix lands in one task, the tests in the next: the base is wrong."""
        root = self.tmp / "two"
        support.make_repo(
            root,
            {"pyproject.toml": fixtures.PYPROJECT, "refunds.py": fixtures.BASE_REFUNDS},
        )
        self.fingerprints[str(root)] = [support.repo_fingerprint(root)]
        self.feed(fixtures.warmup(self.clock, root, self.venv))
        self.feed(fixtures.task_start(self.clock, root, self.venv))
        first = {"refunds.py": fixtures.FIXED_REFUNDS}
        support.write_files(root, first)
        self.feed(fixtures.edit_events(self.clock, root, first, "fix"))
        self.assertIsNone(self.stop(root).visible)
        self.say(root, "now add tests for it")
        second = {
            "refunds.py": fixtures.FIXED_REFUNDS + "\nX = 1\n",
            "tests/test_a.py": fixtures.TEST_PROVES,
            "tests/test_b.py": fixtures.TEST_PASSES_ANYWAY,
        }
        support.write_files(root, second)
        self.fingerprints[str(root)].append(support.repo_fingerprint(root))
        self.feed(fixtures.edit_events(self.clock, root, second, "tests"))
        self.feed([fixtures.pytest_run(self.clock, root)])
        self.assertIn("added 2 tests", self.stop(root).visible or "")
        return root, self.of("moment.offered")[-1]["moment"]

    def test_wrong_start_and_dispute(self) -> None:
        root, ref = self._two_task_change()
        view = self.engine.wrong_start(ref)
        self.assertEqual(self.of("moment.closed")[-1]["body"]["how"], "wrong-start")
        moved = [e for e in self.of("task.event") if e["body"]["kind"] == "base_moved"]
        self.assertEqual(len(moved), 1)
        self.assertNotEqual(moved[0]["body"]["from"], moved[0]["body"]["to"])
        offered = self.of("moment.offered")
        self.assertEqual(len(offered), 2)
        self.assertEqual(offered[-1]["body"]["replaces"], ref)
        new_ref = offered[-1]["moment"]
        # The page moves to the replacement; the closed question shows no result.
        self.assertEqual(view["ref"], self.engine.question(new_ref)["ref"])
        self.assertIsNone(view["result"])
        self.assertIsNone(self.engine.question(ref)["result"])
        old_ran = [e for e in self.of("check.ran") if e.get("moment") == ref]
        self.assertEqual(old_ran, [])
        self.engine.lock(new_ref, "2", channel="chat", final=True)
        view = self.engine.dispute(new_ref, "the check looks off")
        self.assertIsNotNone(view)
        reruns = [e for e in self.of("check.ran") if e["body"]["rerun_of"]]
        self.assertEqual(len(reruns), 1)
        self.assertEqual(reruns[0]["body"]["reason"], "the check looks off")
        result = self.engine.question(new_ref)["result"]
        self.assertEqual(
            result["more"]["dispute"], "Rechecked. The result is the same."
        )
        self.assertEqual(self.engine.status(str(root))["asked_today"], 1)
        self.assert_untouched(root)


if __name__ == "__main__":
    unittest.main()
