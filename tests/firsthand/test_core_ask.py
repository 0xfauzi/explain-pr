"""firsthand.ask: gates in order, fact_allowed, pressure, control words, the state table."""

from __future__ import annotations

import itertools
import unittest

import support

from firsthand import ask
from firsthand.model import EngineError

OPEN = ask.GateInput(
    dial="standard",
    quiet=False,
    pressure=False,
    asked_today=0,
    daily_limit=1,
    change_asked=False,
    first_prompt_turn=False,
    session_stopped=False,
)


def gate(**changes: object) -> ask.GateInput:
    return ask.GateInput(**{**OPEN.__dict__, **changes})  # type: ignore[arg-type]


class GateTest(support.TempHome):
    def test_open_gate_asks(self) -> None:
        self.assertIsNone(ask.gates(OPEN))
        self.assertIsNone(ask.gates(gate(dial="deep")))

    def test_each_reason(self) -> None:
        cases = [
            ("dial", {"dial": "notes"}),
            ("dial", {"dial": "off"}),
            ("quiet", {"quiet": True}),
            ("pressure", {"pressure": True}),
            ("limit", {"asked_today": 1}),
            ("change", {"change_asked": True}),
            ("first-prompt", {"first_prompt_turn": True}),
            ("session-skips", {"session_stopped": True}),
        ]
        for reason, changes in cases:
            with self.subTest(reason=reason):
                self.assertEqual(ask.gates(gate(**changes)), reason)

    def test_first_failing_gate_wins(self) -> None:
        g = gate(quiet=True, asked_today=5, session_stopped=True)
        self.assertEqual(ask.gates(g), "quiet")

    def test_fact_allowed(self) -> None:
        self.assertTrue(ask.fact_allowed(gate(asked_today=9, dial="notes")))
        for changes in (
            {"dial": "off"},
            {"quiet": True},
            {"pressure": True},
            {"first_prompt_turn": True},
        ):
            self.assertFalse(ask.fact_allowed(gate(**changes)), changes)

    def test_pressure(self) -> None:
        self.assertTrue(ask.is_pressure("hotfix/refunds", []))
        self.assertTrue(ask.is_pressure("main", ["This is URGENT"]))
        self.assertTrue(ask.is_pressure(None, ["prod is down again"]))
        self.assertFalse(ask.is_pressure("main", ["fix the refund bug"]))

    def test_control_words(self) -> None:
        self.assertEqual(ask.control_word(" Skip. "), "skip")
        self.assertEqual(ask.control_word("quiet   today"), "quiet today")
        self.assertEqual(ask.control_word("Quiet here"), "quiet here")
        self.assertIsNone(ask.control_word("skip the tests please"))


class TableTest(support.TempHome):
    def test_every_pair(self) -> None:
        states = ("open", "held", "sealed", "settled", "skipped", "closed")
        actions = ("pick", "skip_room", "undo", "seal", "skip_final", "close", "settle")
        for state, action in itertools.product(states, actions):
            with self.subTest(state=state, action=action):
                if (state, action) in ask.TABLE:
                    self.assertEqual(
                        ask.step(state, action), ask.TABLE[(state, action)]
                    )
                else:
                    with self.assertRaises(EngineError) as caught:
                        ask.step(state, action)
                    self.assertEqual(caught.exception.code, "state")

    def test_the_rows(self) -> None:
        self.assertEqual(ask.step("open", "pick"), "held")
        self.assertEqual(ask.step("held", "undo"), "open")
        self.assertEqual(ask.step("held", "seal"), "sealed")
        self.assertEqual(ask.step("held", "skip_final"), "skipped")
        self.assertEqual(ask.step("open", "close"), "closed")
        self.assertEqual(ask.step("sealed", "settle"), "settled")


if __name__ == "__main__":
    unittest.main()
