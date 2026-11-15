"""firsthand.words: the lines of experience.md and contract section 9, character for character."""

from __future__ import annotations

import unittest
from datetime import UTC
from pathlib import Path

import support

from firsthand import words
from firsthand.keys import OutputContext
from firsthand.model import PRINT_PREFIX, Key, KeyItem, Moment, TestItem

ROOM = "http://127.0.0.1:4127"
MOMENT_ID = "01JC8Y2F7H3QZ5W8N1P4R6T9KD"


def item(n: int, name: str, line: int, status: str = "new") -> TestItem:
    return TestItem(
        n=n,
        id=f"tests/test_refunds.py::{name}",
        name=name,
        path="tests/test_refunds.py",
        line=line - 2,
        status=status,  # type: ignore[arg-type]
        assert_lines=(line,),
        assert_line=line,
        assert_text="assert x",
    )


THREE = (
    item(1, "test_same_key_refunds_once", 23),
    item(2, "test_refund_response_is_stable", 41),
    item(3, "test_refund_amount_validated", 55),
)


def moment(tests=THREE, **changes: object) -> Moment:
    m = Moment(
        id=MOMENT_ID,
        kind="revert_test",
        state="open",
        project_id="prj_3b9f52c1a7e0",
        change_id="C",
        task_id="T",
        session="s",
        task_name="idempotent refunds",
        base_at="2026-11-14T09:12:03Z",
        base_tree="b",
        head_tree="h",
        tests=tests,
        how="pytest",
        high_stakes=None,
        offered_at="2026-11-14T09:40:00Z",
    )
    for k, v in changes.items():
        setattr(m, k, v)
    return m


def key(*results: str, tests=THREE) -> Key:
    return Key(
        moment=MOMENT_ID,
        kind="revert_test",
        how="pytest",
        base_tree="b",
        head_tree="h",
        made_at="",
        tests=tuple(
            KeyItem(t.id, r, t.assert_line, t.assert_text, None)  # type: ignore[arg-type]
            for t, r in zip(tests, results, strict=True)
        ),
        steps=(),
        undone_paths=(),
        duration_s=1.0,
    )


def ctx(
    work: bool = False, notice: bool = False, room: str | None = ROOM
) -> OutputContext:
    return OutputContext(
        room_url=room, work_computer=work, work_notice=notice, task_name="x"
    )


class QuestionTest(support.TempHome):
    def test_several_tests(self) -> None:
        self.assertEqual(
            words.question_line(moment(), ctx()),
            "Firsthand (skip ok): your agent finished and added 3 tests. Which of them "
            "would still pass with the change undone? 1 test_same_key_refunds_once, "
            "2 test_refund_response_is_stable, 3 test_refund_amount_validated. "
            "Reply the numbers, or none. With the tests shown: "
            "http://127.0.0.1:4127/q/r6t9kd",
        )

    def test_one_test(self) -> None:
        one = (item(1, "test_refund_response_is_stable", 41),)
        self.assertEqual(
            words.question_line(moment(one), ctx()),
            "Firsthand (skip ok): your agent finished and added 1 test, "
            "test_refund_response_is_stable. Would it still pass with the change undone? "
            "Reply fails or passes. With the test shown: http://127.0.0.1:4127/q/r6t9kd",
        )

    def test_work_computer_link_first_with_notice(self) -> None:
        line = words.question_line(moment(), ctx(work=True, notice=True))
        self.assertTrue(
            line.startswith(
                "Firsthand (skip ok): http://127.0.0.1:4127/q/r6t9kd Your agent finished"
            )
        )
        self.assertTrue(
            line.endswith(
                " A reply here is part of your agent's chat. The Room is not."
            )
        )

    def test_no_room(self) -> None:
        line = words.question_line(moment(), ctx(room=None))
        self.assertTrue(line.endswith("With the tests shown: run firsthand room"))

    def test_edited(self) -> None:
        mixed = (THREE[0], item(2, "test_b", 41, "edited"))
        self.assertIn(
            "added or edited 2 tests", words.question_line(moment(mixed), ctx())
        )
        self.assertEqual(
            words.lead(moment(mixed)), "It added or edited 2 tests. Read them first."
        )
        self.assertEqual(
            words.lead(moment(THREE[:1])), "It added 1 test. Read it first."
        )

    def test_context_line(self) -> None:
        self.assertEqual(
            words.context_line(moment(), "orbit-pay", UTC),
            "Verification | orbit-pay | idempotent refunds | change since 09:12",
        )


class ResultTest(support.TempHome):
    def test_matched_chat_form(self) -> None:
        m = moment(state="settled", answer="2", channel="chat")
        lines = words.result_lines(
            m, key("fails_on_assertion", "still_passes", "cannot_run"), ctx()
        )
        self.assertEqual(
            lines,
            [
                "Firsthand, revert test. Matched. You said 2.",
                (
                    "test_refund_response_is_stable still passes with the change undone. "
                    "It would pass whether or not the change exists."
                ),
                "More: http://127.0.0.1:4127/r/r6t9kd",
                "Back to: idempotent refunds. Next: read the summary.",
            ],
        )

    def test_miss_has_the_cue(self) -> None:
        m = moment(state="settled", answer="none", confidence="low")
        k = key("fails_on_assertion", "still_passes", "cannot_run")
        lines = words.result_lines(m, k, ctx())
        self.assertEqual(
            lines[0], "Firsthand, revert test. Did not match. You said none. Not sure."
        )
        self.assertEqual(
            lines[1],
            "test_refund_response_is_stable still passes with the change undone.",
        )
        self.assertEqual(
            lines[2],
            "What would have shown it: Its only assertion is at tests/test_refunds.py:41.",
        )
        self.assertEqual(words.you_said(m), "None. Not sure.")

    def test_what_happened_rows(self) -> None:
        k = key("fails_on_assertion", "fails_on_assertion", "cannot_run")
        self.assertEqual(
            words.what_happened(moment(answer="none"), k),
            ["None of them passes with the change undone."],
        )
        self.assertEqual(
            words.what_happened(moment(answer="3"), k),
            [
                (
                    "test_refund_amount_validated does not pass with the change undone: "
                    "it cannot run without the new code."
                )
            ],
        )

    def test_a_set_answer(self) -> None:
        two = key("still_passes", "fails_on_assertion", "still_passes")
        m = moment(state="settled", answer="1,3", confidence="high")
        self.assertEqual(
            words.you_said(m),
            "1 and 3, test_same_key_refunds_once and test_refund_amount_validated. Sure.",
        )
        self.assertEqual(
            words.what_happened(m, two),
            [
                (
                    "test_same_key_refunds_once and test_refund_amount_validated still "
                    "pass with the change undone."
                )
            ],
        )
        lines = words.result_lines(m, two, ctx())
        self.assertEqual(
            lines[0], "Firsthand, revert test. Matched. You said 1 and 3. Sure."
        )
        self.assertNotIn("What would have shown it", " ".join(lines))
        # One of two is a miss, and the cue is about the one left out.
        one = moment(state="settled", answer="1")
        lines = words.result_lines(one, two, ctx())
        self.assertEqual(lines[0], "Firsthand, revert test. Did not match. You said 1.")
        self.assertEqual(
            lines[2],
            "What would have shown it: Its only assertion is at tests/test_refunds.py:55.",
        )
        # A picked test that does not still pass gets the fail cue.
        extra = moment(state="settled", answer="1,2,3")
        self.assertEqual(
            words.cue_text(extra, two), "It fails at tests/test_refunds.py:41."
        )
        none = key("fails_on_assertion", "fails_on_assertion", "cannot_run")
        both = moment(answer="1,3")
        self.assertEqual(
            words.what_happened(both, none),
            [
                (
                    "test_same_key_refunds_once does not pass with the change undone: "
                    "it fails on its assertion. test_refund_amount_validated does not "
                    "pass with the change undone: it cannot run without the new code."
                )
            ],
        )
        self.assertEqual(words.answer_text(moment(answer="none")), "None.")

    def test_more_rows_and_counts(self) -> None:
        self.assertEqual(
            words.counts_line(5, 7, 4),
            'Your calls of this kind: 5 of 7 matched. Always answering "none" would have scored 4 of 7.',
        )
        self.assertEqual(
            words.sure_line(6, 8, 3, 6), "Sure: 6 of 8 matched. Not sure: 3 of 6."
        )
        self.assertEqual(
            words.checked_line("exit_code"), "Checked by a run, by exit code, no model."
        )

    def test_pending_and_dispute(self) -> None:
        self.assertEqual(
            words.pending_line(moment(), ctx()),
            "Firsthand: locked. The check is still running. The result will be at "
            "http://127.0.0.1:4127/r/r6t9kd",
        )
        self.assertEqual(
            words.dispute_line(False),
            "Rechecked. The check was wrong. This call is removed from your record.",
        )


class CueTest(support.TempHome):
    def test_cannot_run_cue_says_where_it_stopped(self) -> None:
        one = (item(1, "test_summary_rows", 18),)
        k = Key(
            moment=MOMENT_ID,
            kind="revert_test",
            how="pytest",
            base_tree="b",
            head_tree="h",
            made_at="",
            tests=(KeyItem(one[0].id, "cannot_run", 18, "assert x", 16),),
            steps=(),
            undone_paths=(),
            duration_s=1.0,
        )
        self.assertEqual(
            words.cue_text(moment(tests=one, answer="passes"), k),
            "With the change undone it stops at tests/test_refunds.py:16 with an "
            "error, not on an assertion.",
        )


class NoQuestionTest(support.TempHome):
    def test_finding_and_fact(self) -> None:
        k = key("fails_on_assertion", "still_passes", "cannot_run")
        self.assertEqual(
            words.finding_line(k),
            "Firsthand finding: tests/test_refunds.py::test_refund_response_is_stable passes "
            "with the change undone. tests/test_refunds.py::test_refund_amount_validated cannot "
            "run with the change undone.",
        )
        self.assertEqual(
            words.fact_line(k, "refunds/**"),
            "Firsthand: test_refund_response_is_stable passes without the change. "
            "refunds/ is marked high stakes.",
        )
        self.assertEqual(words.glob_label("**/migrations/**"), "migrations/")

    def test_acks(self) -> None:
        self.assertEqual(
            words.ack_line("skip", "idempotent refunds"),
            "Skipped. Back to: idempotent refunds. Next: read the summary.",
        )
        self.assertEqual(
            words.ack_line("quiet", "x"),
            'Quiet for this session. Checks still run and post notes. "quiet today" and '
            '"quiet here" also work.',
        )
        self.assertEqual(
            words.ack_line("off", "x"),
            "Firsthand is off. Nothing is asked, run or recorded. Your record is kept. "
            '"firsthand on" to return.',
        )

    def test_context_text(self) -> None:
        self.assertIsNone(words.context_text([], []))
        self.assertEqual(words.context_text([], ["a"]), "a")
        self.assertEqual(words.context_text(["p"], ["a"]), f"a\n{PRINT_PREFIX}\np")

    def test_task_name(self) -> None:
        self.assertEqual(
            words.task_name("Make refunds idempotent, then tidy up"),
            "Make refunds idempotent",
        )
        self.assertEqual(words.task_name(""), "this task")
        self.assertEqual(
            words.task_name("one two three four five six seven"),
            "one two three four five six",
        )

    def test_no_em_dash_anywhere(self) -> None:
        source = Path(words.__file__).read_text(encoding="utf-8")
        self.assertNotIn(chr(0x2014), source)


if __name__ == "__main__":
    unittest.main()
