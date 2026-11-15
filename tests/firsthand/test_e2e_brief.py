"""The Brief (build-2.md section 11, 2c), replayed against a real Engine.

The three fixtures of 2c, each a real git repo with pytest really run in scratch
copies: a check that tells done from not done, one that passes anyway, and a task
where no test was written. Each test asserts the record events, the Stop line, the
lines added to the agent's context, the score, and that the fixture repo is
byte-identical before and after whenever only the agent's own writes happened.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import fixtures
import fixtures_brief as fb
import support
from test_e2e_replay import ROOM, Replay

from firsthand import cli
from firsthand.model import PRINT_PREFIX, HookReply

QUESTION = (
    "Firsthand (skip ok): starting a task. Name one check that fails now and will "
    'pass when this is done. Reply here starting with "check:".'
)
REPLY = f"check: {fb.LINE}"
WORK = f"Done when: {fb.LINE}. Write this check as a failing test first."
TASK = "add idempotency to charge creation"
RESULT_WORDS = ("Matched", "Did not match", "fails on its assertion", "passes with")


def setUpModule() -> None:
    if support.pytest_python() is None:
        raise unittest.SkipTest(support.pytest_python_reason())


class BriefReplay(Replay):
    def setUp(self) -> None:
        super().setUp()
        self.config.set("work_computer", False)

    def brief_project(self, folder: str = "charges") -> Path:
        root = self.tmp / folder
        support.make_repo(root, fb.BASE)
        self.fingerprints[str(root)] = [support.repo_fingerprint(root)]
        return root

    def agent_writes(self, root: Path, files) -> None:
        support.write_files(root, files)
        self.fingerprints[str(root)].append(support.repo_fingerprint(root))

    def first_turn(
        self,
        root: Path,
        prompt: str = fb.TASK_PROMPT,
        edits=fb.FIRST_EDITS,
        warm: bool = True,
    ) -> HookReply:
        """The task prompt, the agent's first edits, the turn end."""
        if warm:
            self.feed(fixtures.warmup(self.clock, root, self.venv))
        self.feed(fixtures.task_start(self.clock, root, self.venv, prompt=prompt))
        self.agent_writes(root, edits)
        self.feed(fixtures.edit_events(self.clock, root, edits, "first"))
        return self.stop(root)

    def ask_event(self, root: Path, text: str) -> None:
        use = "toolu_ask"
        self.feed(
            [
                fixtures.line(
                    self.clock,
                    root,
                    "s1",
                    "before_tool",
                    tool="ask",
                    tool_use=use,
                    question=text,
                ),
                fixtures.line(
                    self.clock, root, "s1", "after_tool", tool="ask", tool_use=use
                ),
            ]
        )

    def build_turn(self, root: Path, fx: fb.BriefFixture, ask: str | None = None):
        """After the line: the agent writes the test (or not), runs pytest, stops."""
        files = (
            {fx.test_file: fx.test_source}
            if fx.test_file
            else {"api/charges.py": fb.CHARGES_NEW + "# keys never expire\n"}
        )
        self.agent_writes(root, files)
        self.feed(fixtures.edit_events(self.clock, root, files, "build"))
        if ask:
            self.ask_event(root, ask)
        self.feed([fixtures.pytest_run(self.clock, root)])
        return self.stop(root)

    def moment(self):
        offered = [
            e for e in self.of("moment.offered") if e["body"]["moment_kind"] == "brief"
        ]
        self.assertTrue(offered, "a Brief was offered")
        return self.engine.moments[offered[-1]["moment"]]

    def ref(self) -> str:
        return self.moment().id[-6:].lower()

    def scored(self) -> dict:
        return self.of("call.scored")[-1]["body"]

    def no_result_yet(self) -> None:
        for r in self.replies:
            text = (r.visible or "") + (r.context or "")
            for word in RESULT_WORDS:
                self.assertNotIn(word, text)
        self.assertEqual(self.of("check.ran"), [])
        self.assertEqual(self.of("call.scored"), [])

    def answered_line(self, root: Path) -> HookReply:
        stop = self.first_turn(root)
        self.assertEqual(stop.visible, QUESTION)
        return self.say(root, REPLY)


class BriefFixtures(BriefReplay):
    def test_check_that_tells_done_from_not_done(self) -> None:
        fx = fb.BRIEF_FIXTURES["tells"]
        root = self.brief_project()
        stop = self.first_turn(root)
        self.assertEqual(stop.visible, QUESTION)
        offered = self.of("moment.offered")[-1]["body"]
        self.assertEqual(
            (
                offered["moment_kind"],
                offered["form"],
                offered["break"],
                offered["skill"],
            ),
            ("brief", "line", "task_start", 5),
        )
        self.assertEqual(offered["categories"], ["input", "schema"])
        r = self.say(root, REPLY)
        context = r.context or ""
        self.assertTrue(context.startswith(WORK), context)
        self.assertIn(PRINT_PREFIX, context)
        self.assertIn(f'Given to your agent: "{WORK}"', context)
        self.assertIn(f"Back to: {TASK}. Next: your agent has started.", context)
        sealed = self.of("call.sealed")[-1]["body"]
        self.assertEqual((sealed["answer"], sealed["line"]), ("line", fb.LINE))
        inbox = self.engine.inbox()
        self.assertEqual(
            [w["text"] for w in inbox["waiting"]], ["shown when your agent finishes"]
        )
        stop = self.build_turn(root, fx, ask="How long should a key stay valid?")
        self.assertEqual(
            stop.visible,
            "Firsthand: is this your check? test_retry_returns_first_charge. "
            f"Reply yes or no, or: {ROOM}/q/{self.ref()}",
        )
        self.no_result_yet()
        self.assertEqual(self.engine.inbox()["now"][0]["reason"], "Your agent finished")
        r = self.say(root, "yes")
        lines = (r.context or "").split("\n")
        self.assertIn(PRINT_PREFIX, lines)
        self.assertIn("Firsthand, done check. Matched.", lines)
        self.assertIn(
            "test_retry_returns_first_charge passes now. It fails on its assertion "
            "with the change undone. It can tell done from not done.",
            lines,
        )
        self.assertIn(f"More: {ROOM}/r/{self.ref()}", lines)
        self.assertIn(f"Back to: {TASK}. Next: read the summary.", lines)
        self.assertEqual(self.key_results(), [fx.expected])
        body = self.scored()
        self.assertEqual((body["result"], body["unscored_reason"]), ("match", None))
        self.assertEqual(self.of("call.confirmed")[-1]["body"]["value"], "yes")
        self.assertEqual(len(self.question_commits()), 1)
        self.say(root, "same key with a different amount must be refused")
        view = self.engine.question(self.ref())
        result = view["result"]
        self.assertEqual(
            (result["headline"], result["chip_label"]), ("DONE CHECK", "Matched")
        )
        self.assertEqual(
            result["you_said"], f'"{fb.LINE}" test_retry_returns_first_charge'
        )
        self.assertEqual(
            result["more"]["notes"],
            [
                "After your agent finished, you sent 1 correction:",
                '"same key with a different amount must be refused"',
                'Your agent asked 1 question: "How long should a key stay valid?"',
            ],
        )
        self.assert_untouched(root)

    def test_check_that_passes_anyway(self) -> None:
        fx = fb.BRIEF_FIXTURES["passes_anyway"]
        root = self.brief_project()
        self.answered_line(root)
        stop = self.build_turn(root, fx)
        self.assertIn(
            "is this your check? test_retry_returns_an_id.", stop.visible or ""
        )
        self.no_result_yet()
        lines = (self.say(root, "yes").context or "").split("\n")
        self.assertIn("Firsthand, done check. Did not match.", lines)
        self.assertIn(
            "Your check passes with the change undone. It cannot tell done from not done.",
            lines,
        )
        self.assertIn(
            "What would have shown it: Its only assertion is at tests/test_retry.py:5.",
            lines,
        )
        self.assertEqual(self.key_results(), [fx.expected])
        body = self.scored()
        self.assertEqual((body["result"], body["outcome_kind"]), ("miss", "uncommon"))
        result = self.engine.question(self.ref())["result"]
        self.assertEqual(result["cue"]["evidence"][0]["line"], 5)
        self.assert_untouched(root)

    def test_no_test_written(self) -> None:
        fx = fb.BRIEF_FIXTURES["no_test"]
        root = self.brief_project()
        self.answered_line(root)
        stop = self.build_turn(root, fx)
        self.assertEqual(
            stop.visible,
            "Firsthand: your agent finished, and no test was added for your check, so "
            "it was not run. Nothing was scored.",
        )
        body = self.scored()
        self.assertEqual(
            (body["result"], body["unscored_reason"]), ("unscored", "no-test")
        )
        self.assertEqual(self.of("check.ran"), [])
        result = self.engine.question(self.ref())["result"]
        self.assertEqual(result["chip_label"], "Not scored")
        self.assertEqual(
            result["reason"],
            "Not scored. No test was added in this task, so your check was not run.",
        )
        self.assertEqual(len(self.question_commits()), 1)
        self.assert_untouched(root)


class BriefRules(BriefReplay):
    def assert_not_asked(self) -> None:
        self.assertEqual(
            [
                e
                for e in self.of("moment.offered")
                if e["body"]["moment_kind"] == "brief"
            ],
            [],
        )

    def test_prompt_that_names_a_test_asks_nothing(self) -> None:
        root = self.brief_project()
        stop = self.first_turn(
            root, prompt="add idempotency and make tests/test_retry.py pass"
        )
        self.assertIsNone(stop.visible)
        self.assert_not_asked()

    def test_prompt_that_names_the_test_command_asks_nothing(self) -> None:
        root = self.brief_project()
        self.first_turn(root, prompt="add idempotency, then run pytest")
        self.assert_not_asked()

    def test_one_category_asks_nothing(self) -> None:
        root = self.brief_project()
        self.first_turn(root, edits={"api/charges.py": fb.CHARGES_BASE + "# x\n"})
        self.assert_not_asked()

    def test_question_prompt_asks_nothing(self) -> None:
        root = self.brief_project()
        self.first_turn(root, prompt="could charge creation be idempotent?")
        self.assert_not_asked()

    def test_first_prompt_of_the_day_asks_nothing(self) -> None:
        root = self.brief_project()
        self.first_turn(root, warm=False)
        self.assert_not_asked()

    def test_task_after_a_question_only_turn_is_asked(self) -> None:
        # Asking about the code before giving the task is the usual way to work:
        # a turn that built nothing does not hold the task start.
        root = self.brief_project()
        self.feed(fixtures.warmup(self.clock, root, self.venv))
        self.feed(
            fixtures.task_start(
                self.clock, root, self.venv, prompt="explain how charges are created"
            )
        )
        self.assertIsNone(self.stop(root).visible)
        self.say(root, fb.TASK_PROMPT)
        self.agent_writes(root, fb.FIRST_EDITS)
        self.feed(fixtures.edit_events(self.clock, root, fb.FIRST_EDITS, "first"))
        self.assertEqual(self.stop(root).visible, QUESTION)
        started = [e["body"]["name"] for e in self.of("task.started")]
        self.assertEqual(started[-1], TASK)
        self.assertEqual(self.moment().task_name, TASK)

    def test_a_reply_to_the_agent_is_not_taken_as_the_check(self) -> None:
        # The line is printed at a turn end, where the agent asks its own questions.
        root = self.brief_project()
        self.assertEqual(self.first_turn(root).visible, QUESTION)
        r = self.say(root, "YYYY-MM text is fine")
        self.assertNotIn("Done when", r.context or "")
        self.assertEqual(self.of("call.sealed"), [])
        self.assertEqual(self.of("moment.closed")[-1]["body"]["how"], "moved-on")

    def test_work_computer_puts_the_link_first(self) -> None:
        self.config.set("work_computer", True)
        root = self.brief_project()
        stop = self.first_turn(root)
        url = f"{ROOM}/q/{self.ref()}"
        self.assertEqual(
            stop.visible,
            f"Firsthand (skip ok): {url} Starting a task. Name one check that fails "
            'now and will pass when this is done. Reply here starting with "check:", '
            "or in the Room. A reply here is part of your agent's chat. The Room is not.",
        )
        self.say(root, REPLY)
        stop = self.build_turn(root, fb.BRIEF_FIXTURES["tells"])
        self.assertEqual(
            stop.visible,
            f"Firsthand: {url} Is this your check? test_retry_returns_first_charge. "
            "Reply yes or no.",
        )

    def test_skip_is_final_and_sends_nothing(self) -> None:
        root = self.brief_project()
        self.first_turn(root)
        r = self.say(root, "skip")
        self.assertEqual(
            r.context,
            f"{PRINT_PREFIX}\nSkipped. Back to: {TASK}. Next: read the summary.",
        )
        self.assertEqual(len(self.of("moment.skipped")), 1)
        later = self.say(root, "carry on")
        self.assertNotIn("Done when", later.context or "")
        self.assertEqual(len(self.question_commits()), 1)

    def test_no_at_the_confirm_is_not_scored(self) -> None:
        root = self.brief_project()
        self.answered_line(root)
        self.build_turn(root, fb.BRIEF_FIXTURES["tells"])
        lines = (self.say(root, "no").context or "").split("\n")
        self.assertIn("Firsthand, done check. Not scored.", lines)
        self.assertIn("I could not find your check among the new tests.", lines)
        body = self.scored()
        self.assertEqual(
            (body["result"], body["unscored_reason"]), ("unscored", "not-your-check")
        )
        self.assertEqual(
            self.key_results(), ["fails_on_assertion"]
        )  # the facts are kept

    def test_moving_on_at_the_confirm_is_not_scored(self) -> None:
        root = self.brief_project()
        self.answered_line(root)
        self.build_turn(root, fb.BRIEF_FIXTURES["tells"])
        r = self.say(root, "now add a docstring")
        self.assertNotIn("Matched", r.context or "")
        body = self.scored()
        self.assertEqual(body["unscored_reason"], "moved-on")

    def test_high_stakes_fact_still_comes_while_a_brief_is_live(self) -> None:
        # The Brief owns the done signal, so the Revert test asks nothing, but its
        # check still runs silently on the other new tests (learning.md 6.4, 6.5).
        root = self.tmp / "charges"
        base = {**fb.BASE, "payments/refunds.py": fixtures.BASE_REFUNDS}
        support.make_repo(root, base)
        self.fingerprints[str(root)] = [support.repo_fingerprint(root)]
        first = {**fb.FIRST_EDITS, "payments/refunds.py": fixtures.FIXED_REFUNDS}
        stop = self.first_turn(root, edits=first)
        self.assertEqual(stop.visible, QUESTION)
        self.say(root, REPLY)
        anyway = fixtures.TEST_PASSES_ANYWAY.replace(
            "from refunds import", "from payments.refunds import"
        )
        files = {
            "tests/test_a_retry.py": fb.TEST_TELLS,
            "tests/test_refunds.py": anyway,
        }
        self.agent_writes(root, files)
        self.feed(fixtures.edit_events(self.clock, root, files, "build"))
        self.feed([fixtures.pytest_run(self.clock, root)])
        stop = self.stop(root)
        self.assertIn(
            "is this your check? test_retry_returns_first_charge", stop.visible
        )
        self.say(root, "yes")
        stop = self.stop(root)
        self.assertEqual(
            stop.visible,
            "Firsthand: test_refund_response_is_stable passes without the change. "
            "payments/ is marked high stakes.",
        )
        notes = self.of("note.posted")
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["body"]["note_kind"], "revert_test")
        offered = [e["body"]["moment_kind"] for e in self.of("moment.offered")]
        self.assertEqual(offered, ["brief"])
        self.assert_untouched(root)

    def test_line_answered_as_the_first_prompt_of_the_day_goes_out_at_once(
        self,
    ) -> None:
        from firsthand import events

        root = self.brief_project()
        stop = self.first_turn(root)
        self.assertEqual(stop.visible, QUESTION)
        raw = {
            "v": 1,
            "id": events.new_event_id(),
            "at": "2026-11-15T08:00:00Z",
            "agent": "claude-code",
            "session": "s1",
            "cwd": str(root),
            "event": "prompt_submit",
            "prompt": REPLY,
        }
        r = self.feed([events.decode(events.encode(raw))])[0]
        context = r.context or ""
        self.assertTrue(context.startswith(WORK), context)
        self.assertIn(f'Given to your agent: "{WORK}"', context)

    def test_line_typed_in_the_room_goes_out_with_the_next_prompt(self) -> None:
        root = self.brief_project()
        self.first_turn(root)
        view = self.engine.lock(self.ref(), fb.LINE, channel="room", final=False)
        self.assertEqual(view["call"]["label"], f'"{fb.LINE}"')
        self.assertEqual(
            view["status_line"], "Given to your agent. Shown when your agent finishes."
        )
        r = self.say(root, "go ahead")
        self.assertEqual((r.context or "").split("\n")[0], WORK)
        again = self.say(root, "and keep it small")
        self.assertNotIn("Done when", again.context or "")
        stop = self.build_turn(root, fb.BRIEF_FIXTURES["tells"])
        self.assertIn("is this your check?", stop.visible or "")
        view = self.engine.lock(self.ref(), "yes", channel="room", final=False)
        self.assertEqual(view["result"]["chip_label"], "Matched")

    def test_commit_before_done_is_not_scored_and_one_a_day_holds(self) -> None:
        root = self.brief_project()
        self.answered_line(root)
        support.git(root, "add", "-A")
        support.git(root, "commit", "-q", "-m", "wip")
        self.fingerprints[str(root)].append(support.repo_fingerprint(root))
        self.say(root, "now add refunds")  # a new change: HEAD moved
        self.assertEqual(self.scored()["unscored_reason"], "never-done")
        edits = {
            "api/refunds.py": "X = 1\n",
            "db/models.py": fb.MODELS_NEW + "R = []\n",
        }
        self.agent_writes(root, edits)
        self.feed(fixtures.edit_events(self.clock, root, edits, "second"))
        self.stop(root)
        self.assertEqual(len(self.of("moment.offered")), 1, "one question a day")

    def test_the_test_that_failed_first_is_the_check(self) -> None:
        """Written first as a failing test: it is the check, even if another sorts first."""
        root = self.brief_project()
        partial = {
            "api/charges.py": fb.CHARGES_BASE + "# idempotency next\n",
            "db/models.py": fb.MODELS_NEW,
        }
        stop = self.first_turn(root, edits=partial)
        self.assertEqual(stop.visible, QUESTION)
        self.say(root, REPLY)
        red = {"tests/test_retry.py": fb.TEST_TELLS}
        self.agent_writes(root, red)
        self.feed(fixtures.edit_events(self.clock, root, red, "red"))
        self.feed(
            [
                fixtures.pytest_run(
                    self.clock, root, failing=(fb.BRIEF_FIXTURES["tells"].test_id,)
                )
            ]
        )
        rest = {"tests/test_aaa.py": fb.TEST_ANYWAY, "api/charges.py": fb.CHARGES_NEW}
        self.agent_writes(root, rest)
        self.feed(fixtures.edit_events(self.clock, root, rest, "green"))
        self.feed([fixtures.pytest_run(self.clock, root)])
        stop = self.stop(root)
        self.assertIn(
            "is this your check? test_retry_returns_first_charge.", stop.visible or ""
        )
        lines = (self.say(root, "yes").context or "").split("\n")
        self.assertIn("Firsthand, done check. Matched.", lines)
        self.assert_untouched(root)

    def test_an_edit_after_the_test_run_checks_the_done_tree(self) -> None:
        root = self.brief_project()
        self.answered_line(root)
        files = {"tests/test_retry.py": fb.TEST_ANYWAY}
        self.agent_writes(root, files)
        self.feed(fixtures.edit_events(self.clock, root, files, "t1"))
        self.feed([fixtures.pytest_run(self.clock, root)])  # starts the check early
        late = {"tests/test_retry.py": fb.TEST_TELLS}
        self.agent_writes(root, late)
        self.feed(fixtures.edit_events(self.clock, root, late, "t2"))
        stop = self.stop(root)  # no new test run: the done tree is checked
        self.assertIn(
            "is this your check? test_retry_returns_first_charge.", stop.visible or ""
        )
        self.say(root, "yes")
        self.assertEqual(self.key_results(), ["fails_on_assertion"])
        self.assertEqual(
            self.of("check.ran")[-1]["body"]["head_tree"], self.moment().head_tree
        )

    def test_restart_keeps_the_confirm(self) -> None:
        root = self.brief_project()
        self.answered_line(root)
        self.build_turn(root, fb.BRIEF_FIXTURES["tells"])
        self.engine.close()
        self.engine = self.new_engine()
        lines = (self.say(root, "yes").context or "").split("\n")
        self.assertIn("Firsthand, done check. Matched.", lines)

    def test_text_views_show_all_three_moments(self) -> None:
        root = self.brief_project()
        self.answered_line(root)
        self.build_turn(root, fb.BRIEF_FIXTURES["tells"])
        status = cli._status_lines(self.engine.status(str(root)))
        self.assertIn(
            "Open question: Firsthand: is this your check? test_retry_returns_first_charge. "
            f"Reply yes or no, or: {ROOM}/q/{self.ref()}",
            status,
        )
        self.say(root, "yes")
        journal = cli._journal_lines(self.engine.journal())
        self.assertTrue(
            any("  Brief  " in x and "Matched" in x for x in journal), journal
        )
        skills = cli._skills_lines(self.engine.skills())
        for name in (
            "1. Verification",
            "3. Debugging and diagnosis",
            "5. Framing the problem and the brief",
        ):
            self.assertIn(name, skills)
        self.assertIn("  Your calls of this kind: 1 of 1 matched.", skills)
        # The legend explains the counts, and the Brief row says it has no level.
        self.assertTrue(skills[0].startswith("Shown: "), skills)
        framing = skills.index("5. Framing the problem and the brief")
        self.assertTrue(skills[framing + 1].startswith("  No level yet."), skills)


if __name__ == "__main__":
    unittest.main()
