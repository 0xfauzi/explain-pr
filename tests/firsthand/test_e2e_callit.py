"""Call it (build-2.md section 11, 2b), replayed against a real Engine.

The four fixtures of 2b, each a real git repo with pytest really run in scratch
copies: a causal fix, a fix in a file the trace never names, a sleep patch and a
test that never goes green. Each test asserts the record events, the Stop line,
the score, and that the fixture repo is byte-identical before and after
(support.repo_fingerprint) whenever only the agent's own writes happened.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import fixtures
import support
from test_e2e_replay import ROOM, Replay

from firsthand.model import HookReply

TEST = fixtures.TOTAL_ID


def setUpModule() -> None:
    if support.pytest_python() is None:
        raise unittest.SkipTest(support.pytest_python_reason())


class CallReplay(Replay):
    """Replay helpers for one Call it fixture."""

    def setUp(self) -> None:
        super().setUp()
        self.config.set("work_computer", False)  # the one-line form of experience 6.2

    def call_project(self, name: str, folder: str | None = None) -> Path:
        fx = fixtures.CALL_FIXTURES[name]
        root = self.tmp / (folder or name)
        root.mkdir(parents=True, exist_ok=True)
        support.make_repo(root, fx.base)
        self.fingerprints[str(root)] = [support.repo_fingerprint(root)]
        return root

    def agent_writes(self, root: Path, files) -> None:
        """The agent edits the project: a new fingerprint is expected."""
        support.write_files(root, files)
        self.fingerprints[str(root)].append(support.repo_fingerprint(root))

    def red_turn(self, name: str, folder: str | None = None) -> tuple[Path, HookReply]:
        """Warm-up, the task prompt, the agent's breaking edit, a red run, the stop."""
        fx = fixtures.CALL_FIXTURES[name]
        root = self.call_project(name, folder)
        self.feed(fixtures.warmup(self.clock, root, self.venv))
        self.feed(
            fixtures.task_start(self.clock, root, self.venv, prompt="tidy the pricing")
        )
        if fx.broken:
            self.agent_writes(root, fx.broken)
            self.feed(fixtures.edit_events(self.clock, root, fx.broken, "break"))
        self.feed([fixtures.pytest_run(self.clock, root, failing=(TEST,))])
        stop = self.stop(root)
        return root, stop

    def green_turn(
        self, name: str, root: Path, prompt: str = "please fix it"
    ) -> HookReply:
        fx = fixtures.CALL_FIXTURES[name]
        assert fx.fixed is not None
        self.say(root, prompt)
        self.agent_writes(root, fx.fixed)
        self.feed(fixtures.edit_events(self.clock, root, fx.fixed, "fix"))
        self.feed([fixtures.pytest_run(self.clock, root)])
        return self.stop(root)

    def moment(self):
        offered = self.of("moment.offered")
        self.assertTrue(offered, "a question was offered")
        return self.engine.moments[offered[-1]["moment"]]

    def scored(self) -> dict:
        return self.of("call.scored")[-1]["body"]


class CallItFixtures(CallReplay):
    def test_causal_fix(self) -> None:
        root, stop = self.red_turn("causal_fix")
        self.assertEqual(
            stop.visible,
            "Firsthand (skip ok): test_total is failing. Before any fix, where is the "
            "cause? 1 pricing.py, 2 rates.py, 3 service.py, 4 somewhere else. "
            f"Reply 1 to 4, or: {ROOM}/q/{self.moment().id[-6:].lower()}",
        )
        offered = self.of("moment.offered")[-1]["body"]
        self.assertEqual(offered["moment_kind"], "call_it")
        self.assertEqual(offered["break"], "failure_turn_end")
        self.assertEqual(
            [(p["path"], p["traced"], p["changed"]) for p in offered["picks"]],
            [
                ("pricing.py", True, False),
                ("rates.py", False, True),
                ("service.py", True, False),
            ],
        )
        r = self.say(root, "2 sure")
        self.assertIn(
            "Firsthand: locked. Shown when test_total passes again.", r.context or ""
        )
        self.assertEqual(self.of("call.scored"), [])
        inbox = self.engine.inbox()
        self.assertEqual(
            [w["text"] for w in inbox["waiting"]],
            ["shown when test_total passes again"],
        )
        self.assertEqual(inbox["results"], [])
        stop = self.green_turn("causal_fix", root)
        self.assertIsNone(stop.visible, "a deferred result is never printed")
        body = self.scored()
        self.assertEqual(
            (body["result"], body["outcome_kind"], body["catch"]),
            ("match", "common", False),
        )
        ran = self.of("check.ran")[-1]["body"]
        self.assertEqual(ran["check_kind"], "call_it")
        self.assertEqual(ran["extra"]["fix_paths"], ["rates.py"])
        self.assertEqual(ran["results"][0]["result"], "cannot_run")
        self.assertEqual(ran["undone_paths"], ["rates.py"])
        result = self.engine.question(self.moment().id)["result"]
        self.assertEqual(result["headline"], "CALL IT")
        self.assertEqual(result["chip_label"], "Matched")
        self.assertEqual(result["you_said"], "2, rates.py. Sure.")
        self.assertEqual(
            result["what_happened"],
            [
                "The fix landed in rates.py.",
                "With the fix undone, the test fails again.",
            ],
        )
        # After the result, More says why each file was listed: evidence by now.
        self.assertEqual(
            [(row["name"], row["text"]) for row in result["more"]["rows"][1:]],
            [
                ("1  pricing.py", "named in the trace"),
                ("2  rates.py", "changed in this task"),
                ("3  service.py", "named in the trace"),
            ],
        )
        self.assertEqual(
            [
                e["type"]
                for e in self.record.events()
                if e["type"].startswith("episode")
            ],
            ["episode.red", "episode.green"],
        )
        self.assertEqual(len(self.question_commits()), 1)
        self.assertEqual(self.engine.inbox()["waiting"], [])
        self.assert_untouched(root)

    def test_work_computer_line(self) -> None:
        self.config.set("work_computer", True)
        _, stop = self.red_turn("causal_fix")
        ref = self.moment().id[-6:].lower()
        self.assertEqual(
            stop.visible,
            f"Firsthand (skip ok): {ROOM}/q/{ref} test_total is failing. Before any "
            "fix, where is the cause? 1 pricing.py, 2 rates.py, 3 service.py, 4 "
            "somewhere else. Reply 1 to 4. A reply here is part of your agent's chat. "
            "The Room is not.",
        )

    def test_fix_in_an_unnamed_file(self) -> None:
        root, stop = self.red_turn("unnamed_file")
        self.assertIn(
            "1 pricing.py, 2 service.py, 3 somewhere else. Reply 1 to 3", stop.visible
        )
        self.say(root, "1")
        self.green_turn("unnamed_file", root)
        body = self.scored()
        self.assertEqual((body["result"], body["outcome_kind"]), ("miss", "uncommon"))
        result = self.engine.question(self.moment().id)["result"]
        self.assertEqual(result["chip_label"], "Did not match")
        self.assertEqual(
            result["cue"]["text"],
            "The fix is in rates.py, a file the failing trace never names.",
        )
        self.assert_untouched(root)

    def test_somewhere_else_matches_an_unnamed_file(self) -> None:
        root, _ = self.red_turn("unnamed_file")
        self.say(root, "3")
        self.green_turn("unnamed_file", root)
        body = self.scored()
        self.assertEqual(
            (body["result"], body["outcome_kind"], body["catch"]),
            ("match", "uncommon", True),
        )
        self.assert_untouched(root)

    def test_sleep_patch(self) -> None:
        root, _ = self.red_turn("sleep_patch")
        self.say(root, "1")
        self.green_turn("sleep_patch", root)
        body = self.scored()
        self.assertEqual(
            (body["result"], body["unscored_reason"]), ("unscored", "symptom-patch")
        )
        ran = self.of("check.ran")[-1]["body"]
        self.assertEqual(
            ran["extra"]["patterns"],
            [{"kind": "sleep", "line": 7, "path": "pricing.py"}],
        )
        result = self.engine.question(self.moment().id)["result"]
        self.assertEqual(result["chip_label"], "Not scored")
        self.assertEqual(
            result["reason"],
            "Not scored. The fix adds a sleep at pricing.py:7. That can turn the test "
            "green without touching the cause, so where it landed proves nothing about "
            "your answer.",
        )
        self.assert_untouched(root)

    def test_never_green(self) -> None:
        root, stop = self.red_turn("never_green")
        self.assertIsNotNone(stop.visible)
        self.say(root, "2")
        # The change ends: the agent commits with the test still failing.
        support.git(root, "add", "-A")
        support.git(root, "commit", "-q", "-m", "wip")
        self.fingerprints[str(root)].append(support.repo_fingerprint(root))
        self.say(root, "next thing")
        body = self.scored()
        self.assertEqual(
            (body["result"], body["unscored_reason"]), ("unscored", "never-green")
        )
        self.assertEqual(self.of("check.ran"), [])
        view = self.engine.question(self.moment().id)
        self.assertEqual(
            view["status_line"], "Not scored. The change ended before the test passed."
        )
        self.assertEqual(len(self.question_commits()), 1)
        self.assert_untouched(root)


class CallItRules(CallReplay):
    def test_red_and_green_in_one_turn_asks_nothing(self) -> None:
        fx = fixtures.CALL_FIXTURES["causal_fix"]
        root = self.call_project("causal_fix")
        self.feed(fixtures.warmup(self.clock, root, self.venv))
        self.feed(fixtures.task_start(self.clock, root, self.venv))
        self.agent_writes(root, fx.broken)
        self.feed(fixtures.edit_events(self.clock, root, fx.broken, "break"))
        self.feed([fixtures.pytest_run(self.clock, root, failing=(TEST,))])
        self.agent_writes(root, fx.fixed)
        self.feed(fixtures.edit_events(self.clock, root, fx.fixed, "fix"))
        self.feed([fixtures.pytest_run(self.clock, root)])
        stop = self.stop(root)
        self.assertIsNone(stop.visible)
        self.assertEqual(self.of("moment.offered"), [])
        self.assertEqual(
            [
                e["type"]
                for e in self.record.events()
                if e["type"].startswith("episode")
            ],
            ["episode.red", "episode.green"],
        )
        self.assert_untouched(root)

    def test_pasted_failure_closes_at_the_first_edit(self) -> None:
        fx = fixtures.CALL_FIXTURES["unnamed_file"]
        root = self.call_project("unnamed_file")
        self.feed(fixtures.warmup(self.clock, root, self.venv))
        self.feed(
            fixtures.task_start(
                self.clock, root, self.venv, prompt=fixtures.PASTED_FAILURE
            )
        )
        offered = self.of("moment.offered")
        self.assertEqual(len(offered), 1)
        self.assertEqual(offered[0]["body"]["break"], "failure_prompt")
        self.assertEqual(self.engine.inbox()["now"][0]["reason"], "A test is failing")
        self.agent_writes(root, fx.fixed)
        self.feed(fixtures.edit_events(self.clock, root, fx.fixed, "fix"))
        closed = self.of("moment.closed")[-1]["body"]
        self.assertEqual(closed["how"], "fix-started")
        # Nobody saw the card: it uses neither the day's question nor the change's.
        self.assertIs(closed["seen"], False)
        m = self.moment()
        self.assertEqual(self.engine.asked_today(self.engine.day(m.offered_at)), 0)
        self.assertFalse(self.engine.session_of(m).st.change_asked)
        self.feed([fixtures.pytest_run(self.clock, root)])
        stop = self.stop(root)
        self.assertIsNone(stop.visible)
        self.assertEqual(self.of("call.scored"), [])
        self.assertEqual(self.of("check.ran"), [])
        view = self.engine.question(self.moment().id)
        self.assertEqual(
            view["status_line"],
            "Your agent got there first. Nothing was scored. The failure is saved in "
            "your record.",
        )
        self.assertEqual(
            [
                e["type"]
                for e in self.record.events()
                if e["type"].startswith("episode")
            ],
            ["episode.red", "episode.green"],
        )
        self.assert_untouched(root)

    def test_one_question_a_day(self) -> None:
        first, _ = self.red_turn("causal_fix", "first")
        self.say(first, "skip")
        self.assertEqual(len(self.of("moment.offered")), 1)
        second = self.call_project("causal_fix", "second")
        self.feed(
            fixtures.task_start(self.clock, second, self.venv, prompt="tidy pricing")
        )
        fx = fixtures.CALL_FIXTURES["causal_fix"]
        self.agent_writes(second, fx.broken)
        self.feed(fixtures.edit_events(self.clock, second, fx.broken, "break"))
        self.feed([fixtures.pytest_run(self.clock, second, failing=(TEST,))])
        stop = self.stop(second)
        self.assertIsNone(stop.visible)
        self.assertEqual(len(self.of("moment.offered")), 1)
        self.assertEqual(self.of("check.unavailable"), [])
        self.assert_untouched(first)
        self.assert_untouched(second)

    def test_room_lock_waits_then_shows(self) -> None:
        root, _ = self.red_turn("causal_fix")
        m = self.moment()
        view = self.engine.lock(m.id, "2", channel="room", final=False)
        self.assertEqual(view["state"], "held")
        self.assertIsNone(view["result"])
        view = self.engine.show(m.id)
        self.assertEqual(view["state"], "sealed")
        self.assertEqual(
            view["status_line"], "Locked. Shown when test_total passes again."
        )
        self.green_turn("causal_fix", root)
        view = self.engine.question(m.id)
        self.assertEqual(view["result"]["chip_label"], "Matched")
        self.assertEqual(self.scored()["result"], "match")
        self.assert_untouched(root)

    def test_no_note_before_the_seal(self) -> None:
        # "changed in this task" on the file the agent broke would mark the answer.
        root, stop = self.red_turn("causal_fix")
        m = self.moment()
        notes = ("named in the trace", "changed in this task", "traced")
        open_view = self.engine.question(m.id)
        self.assertEqual(
            [p["label"] for p in open_view["picks"]][:3],
            ["1  pricing.py", "2  rates.py", "3  service.py"],
        )
        held = self.engine.lock(m.id, "2", channel="room", final=False)
        self.assertEqual(held["state"], "held")
        sealed = self.engine.show(m.id)
        self.assertEqual(sealed["state"], "sealed")
        shown = [stop.visible or "", str(self.engine.inbox())]
        shown += [str(v) for v in (open_view, held, sealed)]
        for text in shown:
            for word in notes:
                self.assertNotIn(word, text)
        self.assert_untouched(root)

    def test_one_file_asks_nothing(self) -> None:
        root, stop = self.red_turn("one_file")
        self.assertIsNone(stop.visible)
        self.assertEqual(self.of("moment.offered"), [])
        red = self.of("episode.red")
        self.assertEqual([e["body"]["test"] for e in red], [TEST])
        self.green_turn("one_file", root)
        self.assertEqual(
            [
                e["type"]
                for e in self.record.events()
                if e["type"].startswith("episode")
            ],
            ["episode.red", "episode.green"],
        )
        self.assertEqual(self.of("call.scored"), [])
        self.assert_untouched(root)

    def test_no_result_before_the_lock(self) -> None:
        root, stop = self.red_turn("causal_fix")
        m = self.moment()
        view = self.engine.question(m.id)
        self.assertIsNone(view["result"])
        for text in [stop.visible or "", str(view), str(self.engine.inbox())]:
            for word in ("fix landed", "fails again", "still passes", "fix is in"):
                self.assertNotIn(word, text)
        self.assertEqual(self.of("check.ran"), [])
        for r in self.replies:
            for text in (r.visible or "", r.context or ""):
                self.assertNotIn("decision", text)
        self.assert_untouched(root)

    def test_restart_resumes_a_waiting_call(self) -> None:
        root, _ = self.red_turn("causal_fix")
        self.say(root, "2")
        self.engine.close()
        self.engine = self.new_engine()
        self.green_turn("causal_fix", root)
        self.assertEqual(self.scored()["result"], "match")
        self.assertEqual(len(self.question_commits()), 1)
        self.assert_untouched(root)

    def test_pasted_traceback_names_the_test_later(self) -> None:
        root = self.call_project("unnamed_file")
        self.feed(fixtures.warmup(self.clock, root, self.venv))
        pasted = (
            "this blows up:\nTraceback (most recent call last):\n"
            f'  File "{root}/service.py", line 4, in total\n'
            f'  File "{root}/pricing.py", line 7, in price\n'
            "ValueError: negative price\n"
        )
        self.feed(fixtures.task_start(self.clock, root, self.venv, prompt=pasted))
        self.assertEqual(self.of("moment.offered"), [])
        self.assertEqual(self.of("episode.red"), [])
        self.feed([fixtures.pytest_run(self.clock, root, failing=(TEST,))])
        red = self.of("episode.red")[-1]["body"]
        self.assertEqual((red["trigger"], red["test"]), ("prompt", TEST))
        offered = self.of("moment.offered")[-1]["body"]
        self.assertEqual(offered["break"], "failure_prompt")
        self.assertEqual(
            [p["path"] for p in offered["picks"]], ["pricing.py", "service.py"]
        )
        stop = self.stop(root)
        self.assertIn("test_total is failing.", stop.visible or "")
        self.assert_untouched(root)


class CallItFrames(CallReplay):
    def test_card_shows_only_the_chosen_tests_frames(self) -> None:
        # A paste of several failures holds other tests' traces; the card and its
        # picks come from the red run of the one test it names.
        root = self.call_project("unnamed_file")
        other = {
            "audit.py": "def audit():\n    raise RuntimeError('x')\n",
            "tests/test_audit.py": (
                "from audit import audit\n\n\ndef test_audit():\n    audit()\n"
            ),
        }
        support.write_files(root, other)
        support.git(root, "add", "-A")
        support.git(root, "commit", "-q", "-m", "audit")
        self.fingerprints[str(root)].append(support.repo_fingerprint(root))
        self.feed(fixtures.warmup(self.clock, root, self.venv))
        pasted = (
            "two failures, please fix\n"
            "tests/test_audit.py:5: in test_audit\n"
            "audit.py:2: RuntimeError\n"
            "tests/test_total.py:5: in test_total\n"
            "FAILED tests/test_total.py::test_total - ValueError: negative price\n"
            "FAILED tests/test_audit.py::test_audit - RuntimeError: x\n"
        )
        self.feed(fixtures.task_start(self.clock, root, self.venv, prompt=pasted))
        offered = self.of("moment.offered")[-1]["body"]
        self.assertEqual(
            [p["path"] for p in offered["picks"]], ["pricing.py", "service.py"]
        )
        frames = [f["path"] for f in self.moment().extra["frames"]]
        self.assertNotIn("audit.py", frames)
        self.assertNotIn("tests/test_audit.py", frames)
        self.assert_untouched(root)


if __name__ == "__main__":
    unittest.main()
