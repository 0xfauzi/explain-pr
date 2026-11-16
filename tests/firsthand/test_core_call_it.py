"""Unit tests for moments/call_it.py and words_callit.py: no git, no pytest run."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import support

from firsthand import keys, words
from firsthand.model import FileChange, Key, KeyItem, Moment, Reply
from firsthand.moments import call_it as ci

ROOT = "/home/sam/orbit-pay"
PICKS = (
    {"n": 1, "path": "api/charges.py", "traced": False, "changed": True},
    {"n": 2, "path": "ledger/postings.py", "traced": True, "changed": False},
    {"n": 3, "path": "webhooks/handler.py", "traced": True, "changed": False},
)
# The same picks as a record from before the notes left the card holds them.
OLD_PICKS = (
    {"n": 1, "path": "api/charges.py", "note": "changed in this task"},
    {"n": 2, "path": "ledger/postings.py", "note": "named in the trace"},
    {"n": 3, "path": "webhooks/handler.py", "note": "named in the trace"},
)
NOTE_WORDS = ("named in the trace", "changed in this task", "traced")
FRAMES = [
    {"path": "tests/test_hooks.py", "line": 12},
    {"path": "webhooks/handler.py", "line": 27},
    {"path": "ledger/postings.py", "line": 58},
]


def key(fix=("webhooks/handler.py",), result="fails_on_assertion", patterns=()) -> Key:
    return Key(
        moment="01M",
        kind="call_it",
        how="pytest",
        base_tree="R",
        head_tree="G",
        made_at="",
        tests=(KeyItem("tests/test_hooks.py::test_posts", result, None, None, 12),),
        steps=(),
        undone_paths=tuple(fix),
        duration_s=1.0,
        extra={
            "picks": [dict(p) for p in PICKS],
            "frames": FRAMES,
            "fix_paths": list(fix),
            "patterns": list(patterns),
        },
    )


def moment(answer=None, state="open") -> Moment:
    return Moment(
        id="01JC8Y2F7H3QZ5W8N1P4R6T9KD",
        kind="call_it",
        state=state,  # type: ignore[arg-type]
        project_id="prj_1",
        change_id="c",
        task_id="t",
        session="s1",
        task_name="webhook charge settled",
        base_at="2026-11-14T09:12:00Z",
        base_tree="R",
        head_tree="R",
        tests=(),
        how="pytest",
        high_stakes=None,
        offered_at="2026-11-14T09:12:00Z",
        answer=answer,
        extra={
            "test": "tests/test_hooks.py::test_settled_posts_to_ledger",
            "picks": [dict(p) for p in PICKS],
            "frames": FRAMES,
            "message": "assert 0 == 1",
        },
    )


def ctx(work: bool = False, room: str | None = "http://127.0.0.1:4127"):
    return keys.OutputContext(
        room_url=room, work_computer=work, work_notice=False, task_name="x"
    )


class TriggerTest(support.TempHome):
    def test_failure_prompts(self) -> None:
        self.assertTrue(ci.is_failure_prompt("Traceback (most recent call last):\n"))
        self.assertTrue(ci.is_failure_prompt("x\nFAILED tests/t.py::test_a - E\n"))
        self.assertFalse(ci.is_failure_prompt("make the test pass"))
        self.assertFalse(ci.is_failure_prompt("it FAILED tests/t.py::a"))
        self.assertFalse(ci.is_failure_prompt(None))

    def test_failed_ids(self) -> None:
        text = (
            "FAILED tests/t.py::test_a[1] - x\nFAILED tests/t.py::test_a[2]\n"
            "FAILED tests/t.py::TestK::test_b\nFAILED nothing\n"
        )
        self.assertEqual(
            ci.failed_ids(text), ["tests/t.py::test_a", "tests/t.py::TestK::test_b"]
        )

    def test_frames_from_a_pasted_traceback(self) -> None:
        text = (
            "Traceback (most recent call last):\n"
            f'  File "{ROOT}/webhooks/handler.py", line 27, in on_settled\n'
            '  File "/usr/lib/python3.13/site-packages/x/y.py", line 3, in z\n'
            '  File "/elsewhere/other.py", line 9, in w\n'
            '  File "ledger/postings.py", line 58, in post_for\n'
        )
        self.assertEqual(
            ci.frames_from_text(text, ROOT),
            (
                ci.Frame("webhooks/handler.py", 27, "on_settled"),
                ci.Frame("ledger/postings.py", 58, "post_for"),
            ),
        )

    def test_frames_from_pytest_text(self) -> None:
        text = "tests/test_total.py:5: \nservice.py:4: in total\npricing.py:6: ValueError\n"
        self.assertEqual(
            [(f.path, f.line, f.where) for f in ci.frames_from_text(text, ROOT)],
            [
                ("tests/test_total.py", 5, None),
                ("service.py", 4, "total"),
                ("pricing.py", 6, None),
            ],
        )

    def test_covers(self) -> None:
        tid = "tests/test_total.py::test_total"
        self.assertTrue(ci.covers("python -m pytest -q", tid))
        self.assertTrue(ci.covers("pytest tests/", tid))
        self.assertTrue(ci.covers("pytest tests/test_total.py -q", tid))
        self.assertTrue(ci.covers(f"pytest {tid}", tid))
        self.assertFalse(ci.covers("pytest tests/test_other.py", tid))
        self.assertFalse(ci.covers("pytest tests/test_total.py::test_else", tid))
        self.assertTrue(ci.covers(None, tid))


class PicksTest(support.TempHome):
    def test_trace_and_changed_files_sorted_and_capped(self) -> None:
        frames = ci.frames_from_text(
            "tests/test_h.py:1: \nwebhooks/handler.py:27: in on\nledger/postings.py:58: E\n",
            ROOT,
        )
        picks = ci.build_picks(frames, ["api/charges.py", "tests/test_h.py", "z.py"])
        self.assertEqual(
            [(p["n"], p["path"], p["traced"], p["changed"]) for p in picks],
            [
                (1, "api/charges.py", False, True),
                (2, "ledger/postings.py", True, False),
                (3, "webhooks/handler.py", True, False),
            ],
        )
        self.assertTrue(all("note" not in p for p in picks))
        self.assertTrue(ci.worth_asking(picks))

    def test_a_file_both_named_and_changed(self) -> None:
        picks = ci.build_picks((ci.Frame("a.py", 3),), ["a.py"])
        self.assertEqual([(p["traced"], p["changed"]) for p in picks], [(True, True)])
        self.assertEqual(
            ci.pick_facts(picks[0]), ["named in the trace", "changed in this task"]
        )
        self.assertFalse(ci.worth_asking(picks), "one file is not a choice")

    def test_old_records_with_a_note(self) -> None:
        both = {
            "n": 1,
            "path": "a.py",
            "note": "named in the trace, changed in this task",
        }
        self.assertEqual(
            ci.pick_facts(both), ["named in the trace", "changed in this task"]
        )
        self.assertEqual(ci.pick_facts(OLD_PICKS[1]), ["named in the trace"])
        old = key(fix=("api/charges.py",))
        old = Key(**{**old.__dict__, "extra": {**old.extra, "picks": list(OLD_PICKS)}})
        sc = ci.score("1", old)
        self.assertEqual((sc.result, sc.outcome_kind), ("match", "common"))
        self.assertEqual(ci.score("2", old).outcome_kind, "common")

    def test_no_files(self) -> None:
        picks = ci.build_picks((ci.Frame("tests/test_a.py", 3),), [])
        self.assertEqual(picks, ())
        self.assertFalse(ci.worth_asking(picks))


class _Store:
    """A snapshot store fake: trees are dicts of path to text."""

    def __init__(self, trees):
        self.trees = trees

    def read_file(self, tree, path):
        return self.trees[tree].get(path)


class SymptomTest(support.TempHome):
    def scan(self, red: dict, green: dict) -> list[tuple[str, str, int]]:
        changes = []
        for path in sorted(set(red) | set(green)):
            status = "A" if path not in red else "D" if path not in green else "M"
            changes.append(FileChange(path, status))  # type: ignore[arg-type]
        store = _Store({"R": red, "G": green})
        found = ci.symptoms(store, "R", "G", changes)  # type: ignore[arg-type]
        return [(p["kind"], p["path"], p["line"]) for p in found]

    def test_each_pattern(self) -> None:
        red = {
            "a.py": "def f():\n    return g()\n",
            "tests/test_a.py": "def test_f():\n    assert f() == 1\n",
        }
        green = {
            "a.py": (
                "import time\ndef f():\n    time.sleep(1)\n    try:\n        return g()\n"
                "    except Exception:\n        return 1\n"
            ),
            "tests/test_a.py": (
                "import pytest\n@pytest.mark.skip\ndef test_f():\n    f()\n"
            ),
        }
        self.assertEqual(
            self.scan(red, green),
            [
                ("sleep", "a.py", 3),
                ("except", "a.py", 6),
                ("assert", "tests/test_a.py", 2),
                ("skip", "tests/test_a.py", 2),
            ],
        )

    def test_bare_except_and_comments(self) -> None:
        red = {"a.py": "x = 1\n"}
        green = {"a.py": "x = 1\ntry:\n    y()\nexcept:\n    pass\n# time.sleep(1)\n"}
        self.assertEqual(self.scan(red, green), [("except", "a.py", 4)])

    def test_a_clean_fix(self) -> None:
        red = {"a.py": "RATE = -3\n", "tests/test_a.py": "def test():\n    assert 1\n"}
        green = {"a.py": "RATE = 3\n", "tests/test_a.py": red["tests/test_a.py"]}
        self.assertEqual(self.scan(red, green), [])

    def test_assert_removed_outside_tests_is_not_a_pattern(self) -> None:
        self.assertEqual(self.scan({"a.py": "assert x\n"}, {"a.py": "pass\n"}), [])

    def test_specific_except_is_not_broad(self) -> None:
        red = {"a.py": "x = 1\n"}
        green = {"a.py": "try:\n    x = 1\nexcept KeyError:\n    x = 2\n"}
        self.assertEqual(self.scan(red, green), [])


class ScoreTest(support.TempHome):
    def test_picks(self) -> None:
        k = key()
        self.assertEqual(ci.score("3", k).result, "match")
        self.assertEqual(ci.score("1", k).result, "miss")
        self.assertEqual(ci.score("4", k).result, "miss")
        self.assertIsNone(ci.score("dont_know", k))
        self.assertIsNone(ci.score("5", k))

    def test_somewhere_else(self) -> None:
        k = key(fix=("config/rates.py",))
        sc = ci.score("4", k)
        self.assertEqual(
            (sc.result, sc.outcome_kind, sc.catch), ("match", "uncommon", True)
        )
        self.assertEqual(ci.score("3", k).result, "miss")

    def test_fixed_answer_is_the_changed_file(self) -> None:
        sc = ci.score("1", key(fix=("api/charges.py",)))
        self.assertEqual(
            (sc.result, sc.outcome_kind, sc.catch), ("match", "common", False)
        )
        self.assertEqual(ci.score("2", key()).outcome_kind, "uncommon")

    def test_not_scored(self) -> None:
        cases = {
            "symptom-patch": key(
                patterns=({"kind": "sleep", "path": "a.py", "line": 3},)
            ),
            "no-fix": key(fix=()),
            "fix-not-causal": key(result="still_passes"),
        }
        for reason, k in cases.items():
            sc = ci.score("3", k)
            self.assertEqual((sc.result, sc.unscored_reason), ("unscored", reason))

    def test_cue(self) -> None:
        from firsthand import words_callit as wc

        self.assertEqual(
            wc.cue_text(key()),
            "The fix is in webhooks/handler.py, which the trace names at line 27.",
        )
        self.assertEqual(
            wc.cue_text(key(fix=("config/rates.py", "webhooks/handler.py"))),
            "The fix is in webhooks/handler.py, which the trace names at line 27.",
        )
        self.assertEqual(
            wc.cue_text(key(fix=("config/rates.py",))),
            "The fix is in config/rates.py, a file the failing trace never names.",
        )


class ReplyTest(support.TempHome):
    def test_words(self) -> None:
        self.assertEqual(ci.reply_words(3), ("1", "2", "3", "4", "don't know"))
        self.assertEqual(ci.reply_words(1), ("1", "2", "don't know"))

    def test_parse(self) -> None:
        self.assertEqual(ci.parse_reply(" 2 sure.", 3), Reply("2", "high"))
        self.assertEqual(ci.parse_reply("4 not sure", 3), Reply("4", "low"))
        self.assertEqual(ci.parse_reply("Don’t know", 3), Reply("dont_know", None))
        self.assertIsNone(ci.parse_reply("5", 3))
        self.assertIsNone(ci.parse_reply("none", 3))
        self.assertIsNone(ci.parse_reply("look at handler.py", 3))


class WordsTest(support.TempHome):
    def test_question_line_of_experience_6_2(self) -> None:
        m = moment()
        line = words.question_line(m, ctx())
        self.assertEqual(
            line,
            "Firsthand (skip ok): test_settled_posts_to_ledger is failing. Before any "
            "fix, where is the cause? 1 api/charges.py, 2 ledger/postings.py, 3 "
            "webhooks/handler.py, 4 somewhere else. Reply 1 to 4, or: "
            "http://127.0.0.1:4127/q/r6t9kd",
        )
        self.assertTrue(
            words.question_line(m, ctx(room=None)).endswith(", or: run firsthand room")
        )

    def test_no_pick_says_why_it_is_listed(self) -> None:
        from firsthand import words_callit as wc

        for picks in (PICKS, OLD_PICKS):
            m = moment()
            m.extra["picks"] = [dict(p) for p in picks]
            shown = str(wc.pick_rows(m)) + words.question_line(m, ctx(work=True))
            for word in NOTE_WORDS:
                self.assertNotIn(word, shown)
            self.assertEqual(
                [(r["name"], r["text"]) for r in wc.pick_more_rows(m)],
                [
                    ("1  api/charges.py", "changed in this task"),
                    ("2  ledger/postings.py", "named in the trace"),
                    ("3  webhooks/handler.py", "named in the trace"),
                ],
            )

    def test_agent_output_is_the_door(self) -> None:
        m = moment()
        store = keys.KeyStore(self.tmp / "keys")
        out = keys.agent_output("question", moment=m, store=store, ctx=ctx())
        self.assertEqual(out, words.question_line(m, ctx()))
        self.assertIsNone(keys.agent_output("result", moment=m, store=store, ctx=ctx()))
        m.state, m.answer = "sealed", "3"
        self.assertEqual(
            keys.agent_output("pending", moment=m, store=store, ctx=ctx()),
            "Firsthand: locked. Shown when test_settled_posts_to_ledger passes again. "
            "The result will be at http://127.0.0.1:4127/r/r6t9kd",
        )

    def test_you_said_and_result_lines(self) -> None:
        m = moment(answer="3", state="settled")
        m.confidence = "high"
        self.assertEqual(words.you_said(m), "3, webhooks/handler.py. Sure.")
        m.answer = "4"
        self.assertEqual(words.answer_text(m), "4, somewhere else.")
        m.answer = "1"
        lines = words.result_lines(m, key(), ctx())
        self.assertEqual(
            lines[0], "Firsthand, call it. Did not match. You said 1, api/charges.py."
        )
        self.assertEqual(
            lines[2],
            "What would have shown it: the fix is in webhooks/handler.py, which the "
            "trace names at line 27.",
        )

    def test_symptom_reason(self) -> None:
        from firsthand import words_callit as wc

        self.assertEqual(
            wc.pattern_reason(
                {"kind": "sleep", "path": "webhooks/handler.py", "line": 31}
            ),
            "Not scored. The fix adds a sleep at webhooks/handler.py:31. That can turn "
            "the test green without touching the cause, so where it landed proves "
            "nothing about your answer.",
        )

    def test_no_em_dash_in_call_it_copy(self) -> None:
        here = Path(__file__).resolve().parents[2] / "firsthand"
        for name in ("words_callit.py", "moments/call_it.py", "engine_callit.py"):
            self.assertNotIn(chr(0x2014), (here / name).read_text(encoding="utf-8"))

    def test_engine_callit_never_builds_an_agent_line(self) -> None:
        here = Path(__file__).resolve().parents[2] / "firsthand" / "engine_callit.py"
        source = here.read_text(encoding="utf-8")
        for name in (
            "question_line",
            "result_lines",
            "finding_line",
            "fact_line",
            "pending_line",
            "ack_line",
        ):
            self.assertIsNone(re.search(rf"words\w*\.{name}\(", source), name)


if __name__ == "__main__":
    unittest.main()
