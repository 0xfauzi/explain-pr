"""Unit tests for moments/brief.py, words_brief.py and the Brief's output rule.

No git and no pytest run, except `new_tests`, which reads two snapshots.
"""

from __future__ import annotations

import unittest

import support

from firsthand import events, gitwatch, keys, timeline, words
from firsthand.adapters import claude_code
from firsthand.model import HeadState, Key, KeyItem, Moment, Reply, TestItem
from firsthand.moments import brief
from firsthand.runner.snapshot import SnapshotStore

LINE = "a retried POST /charges with the same key returns the first charge id."
TEST_ID = "tests/test_charges.py::test_retry_returns_first_charge"


def item(test_id: str = TEST_ID, line: int = 4) -> TestItem:
    return TestItem(
        n=1,
        id=test_id,
        name=test_id.rsplit("::", 1)[-1],
        path=test_id.split("::", 1)[0],
        line=line,
        status="new",
        assert_lines=(line + 2,),
        assert_line=line + 2,
        assert_text="assert x",
    )


def moment(phase: str = "line", state: str = "open", **extra: object) -> Moment:
    return Moment(
        id="01JC8Y2F7H3QZ5W8N1P4R6T9KD",
        kind="brief",
        state=state,  # type: ignore[arg-type]
        project_id="prj_1",
        change_id="c",
        task_id="t",
        session="s1",
        task_name="idempotency for POST /charges",
        base_at="2026-11-14T09:12:00Z",
        base_tree="B",
        head_tree="B",
        tests=(item(),) if phase in ("checking", "confirm", "done") else (),
        how="pytest",
        high_stakes=None,
        offered_at="2026-11-14T09:12:30Z",
        answer="line" if state != "open" else None,  # type: ignore[arg-type]
        extra={
            "phase": phase,
            "line": LINE if state != "open" else None,
            "test": TEST_ID,
            **extra,
        },
    )


def key(result: str = "fails_on_assertion") -> Key:
    return Key(
        moment="01JC8Y2F7H3QZ5W8N1P4R6T9KD",
        kind="brief",
        how="pytest",
        base_tree="B",
        head_tree="H",
        made_at="",
        tests=(
            KeyItem(
                TEST_ID, result, 6, "assert x", 6 if result != "still_passes" else None
            ),
        ),  # type: ignore[arg-type]
        steps=(),
        undone_paths=("api/charges.py",),
        duration_s=1.0,
    )


CTX = keys.OutputContext(
    room_url="http://127.0.0.1:4127",
    work_computer=False,
    work_notice=False,
    task_name="idempotency for POST /charges",
)


class TriggerTest(unittest.TestCase):
    def test_names_check(self) -> None:
        cases = {
            "add idempotency to POST /charges": False,
            "make test_retry_returns_first_charge pass": True,
            "fix tests/test_charges.py::test_retry": True,
            "update tests/test_charges.py": True,
            "add it, then run pytest -q": True,
            "add some tests for it": False,
        }
        for prompt, named in cases.items():
            with self.subTest(prompt=prompt):
                self.assertEqual(brief.names_check(prompt, "pytest -q"), named)
        self.assertFalse(brief.names_check("then run pytest", None))

    def test_question_and_categories(self) -> None:
        self.assertTrue(brief.is_question("could this be idempotent?  "))
        self.assertFalse(brief.is_question("make this idempotent."))
        self.assertEqual(
            brief.categories(
                ["api/charges.py", "tests/test_x.py", "db/models.py", "api/other.py"]
            ),
            ["input", "schema"],
        )
        self.assertFalse(brief.qualifies(["other"], plan=False))
        self.assertTrue(brief.qualifies(["other"], plan=True))
        self.assertTrue(brief.qualifies(["input", "schema"], plan=False))

    def test_gitwatch_category(self) -> None:
        cases = {
            "tests/test_a.py": "tests",
            "app/migrations/0003_add.py": "schema",
            "payments/refund.py": "money",
            "auth/tokens.py": "auth",
            "api/routes.py": "input",
            "users/profile.py": "personal",
            "pkg/__init__.py": "public",
            "pyproject.toml": "config",
            "pricing.py": "other",
        }
        for path, cat in cases.items():
            with self.subTest(path=path):
                self.assertEqual(gitwatch.category(path), cat)

    def test_first_test_prefers_the_one_that_failed_first(self) -> None:
        a = item("tests/test_a.py::test_alpha")
        b = item(TEST_ID)
        self.assertEqual(brief.first_test([a, b], ()).id, a.id)
        self.assertEqual(brief.first_test([a, b], (TEST_ID + "[1]",)).id, b.id)
        self.assertIsNone(brief.first_test([], (TEST_ID,)))


class NewTestsTest(support.TempHome):
    def test_new_tests_only(self) -> None:
        root = self.tmp / "p"
        old = "def test_old():\n    assert 1\n"
        support.make_repo(root, {"a.py": "X = 1\n", "tests/test_a.py": old})
        store = SnapshotStore(root, "prj_t")
        base = store.take()
        support.write_files(
            root,
            {
                "tests/test_a.py": old.replace("1", "2")
                + "\n\ndef test_new():\n    assert 3\n",
                "tests/test_b.py": "def test_b():\n    assert 4\n",
                "a.py": "X = 2\n",
            },
        )
        head = store.take()
        found = brief.new_tests(store, base, head, store.diff(base, head))
        self.assertEqual(
            [t.id for t in found],
            ["tests/test_a.py::test_new", "tests/test_b.py::test_b"],
        )


class ScoreAndReplyTest(unittest.TestCase):
    def test_score(self) -> None:
        sc = brief.score("yes", key("fails_on_assertion"))
        assert sc is not None
        self.assertEqual((sc.result, sc.outcome_kind), ("match", "common"))
        for result in ("still_passes", "cannot_run"):
            sc = brief.score("yes", key(result))
            assert sc is not None
            self.assertEqual((sc.result, sc.outcome_kind), ("miss", "uncommon"))
        self.assertIsNone(brief.score("no", key()))
        self.assertIsNone(brief.score(None, key()))

    def test_cannot_run_is_not_called_unable_to_tell(self) -> None:
        # It fails without the change, only not on its assertion.
        from firsthand import words_brief

        lines = words_brief.what_happened(key("cannot_run"))
        self.assertNotIn(words_brief.CANNOT_TELL, lines)
        self.assertEqual(
            lines,
            ["Passes now. It cannot run with the change undone. That is weak proof."],
        )

    def test_outside_line(self) -> None:
        from firsthand import words_brief

        self.assertIsNone(words_brief.outside_line(["input"], []))
        self.assertEqual(
            words_brief.outside_line(["input", "schema"], ["payments/refunds.py"]),
            "Also changed, outside the kinds of file of the first edits "
            "(input, schema): payments/refunds.py.",
        )

    def test_reply_needs_the_check_marker(self) -> None:
        self.assertEqual(brief.line_of_reply("Check: a b  c"), "a b c")
        self.assertIsNone(brief.line_of_reply("YYYY-MM text is fine"))
        self.assertIsNone(brief.line_of_reply("check:"))
        self.assertEqual(brief.clean_line("check: x"), "x")

    def test_replies(self) -> None:
        self.assertEqual(brief.parse_reply("Yes."), Reply("yes", None))
        self.assertEqual(brief.parse_reply(" n "), Reply("no", None))
        self.assertIsNone(brief.parse_reply("yes please"))
        self.assertEqual(brief.reply_words(), ("yes", "no"))
        self.assertTrue(brief.is_dont_know("Don’t know."))
        self.assertFalse(brief.is_dont_know("I know"))
        self.assertEqual(brief.clean_line("  a\n  b  "), "a b")
        self.assertEqual(len(brief.clean_line("x" * 900)), brief.MAX_LINE_CHARS)


class WordsTest(support.TempHome):
    def test_question_line_is_the_experience_copy(self) -> None:
        self.assertEqual(
            words.question_line(moment(), CTX),
            "Firsthand (skip ok): starting a task. Name one check that fails now and "
            'passes when this is done. Reply here starting with "check:".',
        )

    def test_work_and_sent_lines(self) -> None:
        m = moment("building", "sealed")
        work = keys.agent_output(
            "work", moment=m, store=keys.KeyStore(self._dir()), ctx=CTX
        )
        self.assertEqual(
            work,
            "Done when: a retried POST /charges with the same key returns the first "
            "charge id. Write this check as a failing test first.",
        )
        self.assertEqual(
            words.pending_line(m, CTX).split("\n"),
            [
                f'Given to your agent: "{work}"',
                "Back to: idempotency for POST /charges. Next: your agent has started.",
            ],
        )

    def test_confirm_line_only_while_confirming(self) -> None:
        store = keys.KeyStore(self._dir())
        m = moment("confirm", "sealed")
        self.assertEqual(
            keys.agent_output("confirm", moment=m, store=store, ctx=CTX),
            "Firsthand: is this your check? test_retry_returns_first_charge. Reply yes "
            "or no, or: http://127.0.0.1:4127/q/r6t9kd",
        )
        for later in (
            moment("confirm", "sealed", confirm="yes"),
            moment("building", "sealed"),
        ):
            self.assertIsNone(
                keys.agent_output("confirm", moment=later, store=store, ctx=CTX)
            )
        self.assertIsNone(
            keys.agent_output("work", moment=moment(), store=store, ctx=CTX)
        )

    def test_result_lines(self) -> None:
        m = moment("done", "settled", confirm="yes")
        self.assertEqual(
            words.result_lines(m, key(), CTX, "match"),
            [
                "Firsthand, Brief. Matched.",
                (
                    "test_retry_returns_first_charge passes now. It fails on its "
                    "assertion with the change undone. It can tell done from not done."
                ),
                "More: http://127.0.0.1:4127/r/r6t9kd",
                "Back to: idempotency for POST /charges. Next: read the summary.",
            ],
        )
        lines = words.result_lines(m, key("still_passes"), CTX)
        self.assertEqual(lines[0], "Firsthand, Brief. Did not match.")
        self.assertEqual(
            lines[1],
            "Your check passes with the change undone. It cannot tell done from not done.",
        )
        self.assertEqual(
            lines[2],
            "What would have shown it: Its only assertion is at tests/test_charges.py:6.",
        )
        no = moment("done", "settled", confirm="no")
        self.assertEqual(
            words.result_lines(no, key(), CTX)[:2],
            [
                "Firsthand, Brief. Not scored.",
                "Firsthand did not find your check in the new tests.",
            ],
        )

    def test_answer_text(self) -> None:
        self.assertEqual(
            words.answer_text(moment("building", "sealed")),
            '"a retried POST /charges with the same key returns the first charge id"',
        )

    def _dir(self):
        return self.tmp / "keys"


class AskTextTest(unittest.TestCase):
    def test_adapter_reads_the_question(self) -> None:
        payload = {
            "session_id": "s",
            "cwd": "/p",
            "tool_name": "AskUserQuestion",
            "tool_use_id": "t1",
            "tool_input": {
                "questions": [
                    {"question": "How long should a key stay valid?", "options": []},
                    {"question": "  Keep   old keys? "},
                ]
            },
        }
        line = claude_code.to_spool(
            "PreToolUse", payload, at="2026-11-14T09:00:00Z", event_id="e1", environ={}
        )
        assert line is not None
        self.assertEqual(
            line["question"], "How long should a key stay valid? / Keep old keys?"
        )
        ev = events.decode(events.encode(line))
        assert ev is not None
        self.assertEqual(ev.question, line["question"])
        after = claude_code.to_spool(
            "PostToolUse", payload, at="2026-11-14T09:00:01Z", event_id="e2", environ={}
        )
        assert after is not None
        self.assertNotIn("question", after)

    def test_timeline_keeps_the_question_on_the_ask_event(self) -> None:
        st = timeline.SessionState(
            agent="a", session="s", project_id="p", project_root="/p"
        )
        head = HeadState("c1", "main")
        prompt = events.decode(
            events.encode(
                {
                    "v": 1,
                    "id": "p1",
                    "at": "2026-11-14T09:00:00Z",
                    "agent": "a",
                    "session": "s",
                    "cwd": "/p",
                    "event": "prompt_submit",
                    "prompt": "go",
                }
            )
        )
        ask = events.decode(
            events.encode(
                {
                    "v": 1,
                    "id": "a1",
                    "at": "2026-11-14T09:00:01Z",
                    "agent": "a",
                    "session": "s",
                    "cwd": "/p",
                    "event": "before_tool",
                    "tool": "ask",
                    "tool_use": "t1",
                    "question": "Which one?",
                }
            )
        )
        assert prompt is not None and ask is not None
        ids = iter(f"id{i}" for i in range(10))
        timeline.step(
            st,
            prompt,
            timeline.Observed("T", head),
            test_command=None,
            first_of_day=False,
            new_id=lambda: next(ids),
        )
        fx = timeline.step(
            st,
            ask,
            timeline.Observed(None, head),
            test_command=None,
            first_of_day=False,
            new_id=lambda: next(ids),
        )
        self.assertEqual(fx[0].body["question"], "Which one?")


if __name__ == "__main__":
    unittest.main()
