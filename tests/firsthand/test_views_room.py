"""The fields the Room's pages read (build-room.md section 3): derived from recorded
events, added to the views, and changing nothing that was already there."""

from __future__ import annotations

import unittest
from datetime import UTC, date

import fixtures
import fixtures_brief as fb
import support
from test_core_engine import FakeLoop
from test_e2e_brief import BriefReplay
from test_e2e_callit import CallReplay

from firsthand import views
from firsthand.model import Settings

TESTS = (
    "test_same_key_refunds_once",
    "test_refund_response_is_stable",
    "test_refund_total_adds_up",
)


def view_input(events: list[dict]) -> views.ViewInput:
    return views.ViewInput(
        events=events,
        moments={},
        settings=Settings(),
        projects={},
        tz=UTC,
        today=date(2026, 11, 16),
        room_url=None,
        read_source=lambda *_: None,
    )


class EntryNumbers(unittest.TestCase):
    def test_numbers_follow_the_first_offer_in_record_order(self) -> None:
        offered = [
            {"type": "moment.offered", "moment": "A"},
            {"type": "call.sealed", "moment": "A"},
            {"type": "task.started", "moment": None},
            {"type": "moment.offered", "moment": "B"},
        ]
        self.assertEqual(view_input(offered).numbers, {"A": 1, "B": 2})
        later = [*offered, {"type": "moment.offered", "moment": "C"}]
        later.append({"type": "moment.offered", "moment": "A"})
        self.assertEqual(view_input(later).numbers, {"A": 1, "B": 2, "C": 3})


class NoteTitle(unittest.TestCase):
    def test_a_note_title_names_each_test_by_its_short_name(self) -> None:
        body = {
            "fact": "tests/test_a.py::test_again passes with the change undone.",
            "evidence": [
                {"test": "tests/test_a.py::test_again", "path": "tests/test_a.py"}
            ],
        }
        self.assertEqual(
            views.note_title(body), "test_again passes with the change undone"
        )


class RevertFields(FakeLoop):
    def test_question_fields_while_open(self) -> None:
        _, moment = self.ask()
        ref = moment[-6:].lower()
        q = self.engine.question(ref)
        self.assertEqual(q["no"], 1)
        self.assertEqual((q["kind_label"], q["skill"]), ("Revert test", "Verification"))
        self.assertEqual(q["where"]["task"], "fix the refund bug")
        self.assertEqual(q["where"]["project"], "p")
        # The folio names the question's own project, by id, not the inbox default.
        self.assertEqual(q["where"]["project_id"], self.engine.inbox()["project"]["id"])
        self.assertRegex(q["where"]["since"], r"^\d\d:\d\d$")
        self.assertEqual((q["prompt_text"], q["prompt_name"]), (q["prompt"], None))
        inbox = self.engine.inbox()
        now = inbox["now"][0]
        self.assertEqual((now["no"], now["kind_label"]), (1, "Revert test"))
        self.assertEqual(now["since"], q["where"]["since"])
        self.assertEqual(inbox["next_no"], 2)
        self.assertEqual(inbox["asked"], {"today": 1, "limit": 1})

    def test_held_then_shown(self) -> None:
        _, moment = self.ask()
        ref = moment[-6:].lower()
        held = self.engine.lock(ref, "1,2", channel="room", final=False)["held"]
        self.assertEqual(held["said"], "1 and 2")
        self.assertEqual(held["names"], list(TESTS[:2]))
        self.assertEqual(held["at"], "2026-11-14T09:30:00Z")
        self.engine.confidence(ref, "low")
        view = self.engine.show(ref)
        call, result = view["call"], view["result"]
        self.assertEqual((call["said"], call["names"]), ("1 and 2", list(TESTS[:2])))
        self.assertEqual(call["locked_at"], held["at"])
        self.assertIsNone(call["confirm"])
        ran = self.record.events(types=("check.ran",))[-1]
        self.assertEqual(result["ran_at"], ran["at"])
        self.assertEqual(result["run_label"], "change undone")
        self.assertEqual([f["k"] for f in result["facts"]], list(TESTS))
        self.assertEqual([f["key"] for f in result["facts"]], [False, True, False])
        self.assertEqual(result["facts"][1]["v"], "still passes")
        self.assertTrue(set(TESTS) <= set(result["names"]))
        self.assertEqual(result["counts"], result["more"]["counts"])
        self.assertTrue(result["fresh"], "first time on a screen")
        again = self.engine.question(ref)["result"]
        self.assertFalse(again["fresh"])
        self.assertEqual({**again, "fresh": True}, result)

    def test_locked_at_is_the_pick_not_the_seal(self) -> None:
        _, moment = self.ask()
        ref = moment[-6:].lower()
        self.engine.lock(ref, "2", channel="room", final=False)
        sealed = self.record.events(types=("call.sealed",))
        self.assertEqual(sealed, [], "nothing recorded while held")
        self.engine.show(ref)
        body = self.record.events(types=("call.sealed",))[-1]["body"]
        view = self.engine.question(ref)
        self.assertEqual(view["call"]["locked_at"], body.get("picked_at") or "")
        self.assertEqual(view["call"]["said"], "2")

    def test_journal_inbox_and_skills(self) -> None:
        self.ask()
        self.feed([fixtures.prompt(self.clock, self.root, "2 sure")])
        entry = self.engine.journal()["entries"][0]
        self.assertEqual(entry["no"], 1)
        self.assertEqual(entry["said"], "2. Sure.")
        self.assertTrue(entry["ran"])
        self.assertEqual(entry["happened"], entry["rows"][1]["text"])
        self.assertRegex(entry["time"], r"^\d{1,2} [A-Z][a-z]{2} \d\d:\d\d$")
        row = self.engine.skills()["rows"][0]
        self.assertEqual((row["matched"], row["total"]), (1, 1))
        self.assertEqual(len(row["calls"]), row["total"])
        self.assertEqual(row["calls"][0]["you"], "match")
        self.assertEqual(row["since"], row["calls"][0]["day"])
        self.assertEqual(row["fixed_answer"], "none")
        self.assertIsInstance(row["fixed_count"], int)
        self.assertTrue(row["fixed"].startswith('Always answering "none"'))
        brief = self.engine.skills()["rows"][-1]
        self.assertEqual((brief["calls"], brief["since"]), ([], None))
        self.assertIsNone(brief["fixed_answer"])


def needs_pytest() -> None:
    if support.pytest_python() is None:
        raise unittest.SkipTest(support.pytest_python_reason())


class CallItFields(CallReplay):
    def setUp(self) -> None:
        needs_pytest()
        super().setUp()

    def test_result_facts_and_why(self) -> None:
        root, _ = self.red_turn("causal_fix")
        m = self.moment()
        ref = m.id[-6:].lower()
        self.say(root, "2 sure")
        waiting = self.engine.inbox()["waiting"][0]
        self.assertEqual((waiting["said"], waiting["task"]), ("2. Sure.", m.task_name))
        self.assertIsNotNone(waiting["locked_at"])
        self.green_turn("causal_fix", root)
        view = self.engine.question(ref)
        call, result = view["call"], view["result"]
        self.assertEqual((view["kind_label"], view["skill"]), ("Call it", "Debugging"))
        self.assertIsNone(view["where"]["since"])
        self.assertEqual(call["said"], "2")
        self.assertEqual(len(call["names"]), 1)
        self.assertEqual(result["run_label"], "fix undone")
        facts = result["facts"]
        self.assertEqual(facts[0]["k"], "the fix")
        self.assertTrue(facts[0]["key"])
        self.assertEqual(facts[-1]["k"], "test_total")
        self.assertFalse(facts[-1]["key"])
        self.assertIn(facts[0]["v"], result["names"])
        why = result["more"]["why"]
        self.assertTrue(why)
        self.assertEqual(result["more"]["rows"][1:], why)

    def test_somewhere_else_and_dont_know(self) -> None:
        self.red_turn("causal_fix")
        m = self.moment()
        listed = len(m.extra["picks"])  # type: ignore[index]
        from firsthand import views_room

        self.assertEqual(
            views_room.said(m, str(listed + 1)), (f"{listed + 1}, somewhere else", [])
        )
        self.assertEqual(views_room.said(m, "dont_know"), ("Don't know", []))


class BriefFields(BriefReplay):
    def setUp(self) -> None:
        needs_pytest()
        super().setUp()

    def test_confirm_sheet_and_result(self) -> None:
        root = self.brief_project()
        self.first_turn(root)
        ref = self.ref()
        self.say(root, f"check: {fb.LINE}")
        self.build_turn(root, fb.BRIEF_FIXTURES["tells"])
        q = self.engine.question(ref)
        self.assertEqual(q["prompt_text"], "Is this your check?")
        self.assertEqual(q["prompt_name"], "test_retry_returns_first_charge")
        self.assertEqual(q["call"]["said"], f'"{fb.LINE}"')
        self.say(root, "yes")
        view = self.engine.question(ref)
        call, result = view["call"], view["result"]
        self.assertEqual(call["confirm"]["value"], "yes")
        self.assertIsNotNone(call["confirm"]["at"])
        self.assertEqual(call["names"], ["test_retry_returns_first_charge"])
        self.assertEqual(result["run_label"], "change undone")
        self.assertEqual(
            [(f["k"], f["key"]) for f in result["facts"]],
            [("test_retry_returns_first_charge", False)],
        )
        self.assertIsNotNone(result["ran_at"])


if __name__ == "__main__":
    unittest.main()
