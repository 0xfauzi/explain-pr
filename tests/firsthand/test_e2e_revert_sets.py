"""The Revert test with two tests that still pass, replayed against a real Engine.

With several tests the answer is the set of tests that would still pass with the
change undone. A match is that exact set: one of two is a miss.
"""

from __future__ import annotations

import unittest

import support
from test_e2e_replay import Replay

from firsthand.model import EngineError
from firsthand.moments import revert_test

BOTH = "test_refund_response_is_stable and test_no_keys_no_refunds"


def setUpModule() -> None:
    if support.pytest_python() is None:
        raise unittest.SkipTest(support.pytest_python_reason())


class TwoStillPass(Replay):
    def moment_id(self) -> str:
        return self.of("moment.offered")[-1]["moment"]

    def scored(self) -> dict:
        return self.of("call.scored")[-1]["body"]

    def test_one_of_two_is_a_miss(self) -> None:
        root, stop = self.run_fixture("two_pass")
        self.assertIn(
            "Which of them would still pass with the change undone? "
            "1 test_same_key_refunds_once, 2 test_refund_response_is_stable, "
            "3 test_no_keys_no_refunds. Reply the numbers, or none.",
            stop.visible or "",
        )
        r = self.say(root, "2")
        self.assertEqual(
            self.key_results(), ["fails_on_assertion", "still_passes", "still_passes"]
        )
        body = self.scored()
        self.assertEqual(
            (body["result"], body["outcome_kind"], body["catch"]),
            ("miss", "uncommon", False),
        )
        context = r.context or ""
        self.assertIn("Firsthand, Revert test. Did not match. You said 2.", context)
        self.assertIn(f"{BOTH} still pass with the change undone.", context)
        # The cue is about the test that still passes and was left out.
        self.assertIn(
            "What would have shown it: Its only assertion is at tests/test_c.py:5.",
            context,
        )
        result = self.engine.question(self.moment_id())["result"]
        self.assertEqual(result["you_said"], "2, test_refund_response_is_stable.")
        self.assertEqual(
            result["what_happened"], [f"{BOTH} still pass with the change undone."]
        )
        self.assertEqual(result["cue"]["evidence"][0]["path"], "tests/test_c.py")
        self.assert_untouched(root)

    def test_the_exact_set_matches(self) -> None:
        root, _ = self.run_fixture("two_pass")
        r = self.say(root, "2 and 3 sure")
        self.assertEqual(self.of("call.sealed")[-1]["body"]["answer"], "2,3")
        body = self.scored()
        self.assertEqual(
            (body["result"], body["outcome_kind"], body["catch"]),
            ("match", "uncommon", True),
        )
        self.assertIn(
            "Firsthand, Revert test. Matched. You said 2 and 3. Sure.", r.context or ""
        )
        result = self.engine.question(self.moment_id())["result"]
        self.assertEqual(result["you_said"], f"2 and 3, {BOTH}. Sure.")
        self.assertIsNone(result["cue"])
        self.assertTrue(self.question_commits()[0].endswith(" match"))
        self.assert_untouched(root)

    def test_room_lock_of_a_set_holds_then_shows(self) -> None:
        root, _ = self.run_fixture("two_pass")
        ref = self.moment_id()
        with self.assertRaises(EngineError) as caught:
            self.engine.lock(ref, "2,2", channel="room", final=False)
        self.assertEqual(caught.exception.message, revert_test.SET_HINT)
        with self.assertRaises(EngineError):
            self.engine.lock(ref, "2,4", channel="room", final=False)
        view = self.engine.question(ref)
        self.assertTrue(view["multi"])
        self.assertEqual(view["state"], "open")
        held = self.engine.lock(ref, "3,2", channel="room", final=False)
        self.assertEqual((held["state"], held["held"]["answer"]), ("held", "2,3"))
        self.assertIsNone(held["result"])
        shown = self.engine.show(ref)
        self.assertEqual(shown["result"]["chip_label"], "Matched")
        self.assertEqual(shown["call"]["label"], f"2 and 3, {BOTH}")
        self.assert_untouched(root)

    def test_none_from_the_command_line_is_a_miss(self) -> None:
        root, _ = self.run_fixture("two_pass")
        view = self.engine.lock(None, "none", channel="chat", final=True, cwd=str(root))
        self.assertEqual(self.scored()["result"], "miss")
        self.assertIn(f"{BOTH} still pass with the change undone.", view["say"][1])
        self.assert_untouched(root)


if __name__ == "__main__":
    unittest.main()
