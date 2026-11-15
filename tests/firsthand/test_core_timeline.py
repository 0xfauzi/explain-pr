"""firsthand.timeline: tasks, bases, the done signal and change ends."""

from __future__ import annotations

import itertools

import support

from firsthand import timeline as tl
from firsthand.model import HeadState, SpoolEvent

HEAD = HeadState("c0", "main")
_seq = itertools.count(1)


def ev(event: str, **kw) -> SpoolEvent:
    return SpoolEvent(
        id=f"e{next(_seq):04d}",
        at=kw.pop("at", "2026-11-14T09:12:03Z"),
        agent="claude-code",
        session="s1",
        cwd="/p",
        event=event,
        **kw,
    )


class TimelineTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.s = tl.SessionState(
            agent="claude-code", session="s1", project_id="prj", project_root="/p"
        )
        ids = itertools.count(1)
        self.new_id = lambda: f"ID{next(ids)}"

    def step(
        self,
        e: SpoolEvent,
        tree: str | None = None,
        head: HeadState = HEAD,
        first_of_day: bool = False,
    ) -> list[tl.Effect]:
        return tl.step(
            self.s,
            e,
            tl.Observed(tree=tree, head=head),
            test_command="pytest -q",
            first_of_day=first_of_day,
            new_id=self.new_id,
        )

    def kinds(self, effects: list[tl.Effect]) -> list[str]:
        return [f.kind for f in effects]

    def run_ev(self, exit_code: int | None, event: str = "after_tool") -> SpoolEvent:
        return ev(event, tool="shell", command="uv run pytest tests", exit=exit_code)

    def test_first_prompt_starts_a_task(self) -> None:
        fx = self.step(
            ev("prompt_submit", prompt="Make refunds idempotent, then test", venv="/v"),
            tree="T0",
            first_of_day=True,
        )
        self.assertEqual(self.kinds(fx), ["task_started"])
        body = fx[0].body
        self.assertEqual(body["base_tree"], "T0")
        self.assertEqual(body["name"], "Make refunds idempotent")
        self.assertEqual(body["head"], "c0")
        self.assertEqual(body["branch"], "main")
        self.assertTrue(body["first_of_day"])
        self.assertEqual(body["session"], "s1")
        task = self.s.task
        self.assertEqual(
            (task.id, task.change_id, task.base_tree), (body["task"], "ID1", "T0")
        )
        self.assertEqual(self.s.venv, "/v")
        self.assertTrue(self.s.turn_first_of_day)

    def test_second_prompt_is_a_prompt_event(self) -> None:
        self.step(ev("prompt_submit", prompt="one"), tree="T0")
        fx = self.step(ev("prompt_submit", prompt="two"), tree="T1")
        self.assertEqual(self.kinds(fx), ["task_event"])
        self.assertEqual(fx[0].body["kind"], "prompt")
        self.assertEqual(fx[0].body["prompt"], "two")
        self.assertEqual(self.s.task.prompts, ["one", "two"])
        self.assertEqual(self.s.task.base_tree, "T0")

    def test_needs_snapshot(self) -> None:
        self.assertTrue(tl.needs_snapshot(self.s, ev("prompt_submit"), "pytest -q"))
        self.assertTrue(tl.needs_snapshot(self.s, ev("turn_end"), None))
        self.assertTrue(tl.needs_snapshot(self.s, self.run_ev(0), "pytest -q"))
        self.assertTrue(
            tl.needs_snapshot(self.s, self.run_ev(1, "tool_failed"), "pytest -q")
        )
        self.assertFalse(
            tl.needs_snapshot(
                self.s, ev("after_tool", tool="shell", command="ls"), "pytest -q"
            )
        )
        self.assertFalse(
            tl.needs_snapshot(self.s, ev("before_tool", tool="edit"), "pytest -q")
        )

    def test_first_turn_end_compares_with_base(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        self.assertEqual(self.step(ev("turn_end"), tree="T0"), [])
        self.assertEqual(self.s.last_turn_end_tree, "T0")
        fx = self.step(ev("turn_end"), tree="T1")
        self.assertEqual(self.kinds(fx), ["done"])
        self.assertEqual(fx[0].body["tree"], "T1")
        self.assertTrue(self.s.task.done)

    def test_done_needs_a_changed_tree(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        self.step(ev("prompt_submit", prompt="y"), tree="T0")
        self.assertEqual(self.step(ev("turn_end"), tree="T0"), [])

    def test_done_needs_last_test_passing(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        fx = self.step(self.run_ev(1, "tool_failed"), tree="R1")
        self.assertEqual(self.kinds(fx), ["task_event", "test_failed"])
        self.assertEqual(fx[0].body["kind"], "test_run")
        self.assertEqual(fx[0].body["exit"], 1)
        self.assertEqual(fx[1].body["tree"], "R1")
        self.assertEqual(self.step(ev("turn_end"), tree="T1"), [])
        fx = self.step(self.run_ev(0), tree="T1")
        self.assertEqual(self.kinds(fx), ["task_event", "test_passed"])
        self.assertEqual(fx[1].body["tree"], "T1")
        self.assertEqual(self.kinds(self.step(ev("turn_end"), tree="T2")), ["done"])

    def test_null_exit_counts_as_failing(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        self.step(self.run_ev(None, "tool_failed"))
        self.assertEqual(self.s.task.last_test_exit, -1)
        self.assertEqual(self.step(ev("turn_end"), tree="T1"), [])

    def test_untested_turn_is_done(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        self.step(ev("after_tool", tool="shell", command="ls", exit=3))
        self.assertIsNone(self.s.task.last_test_exit)
        self.assertEqual(self.kinds(self.step(ev("turn_end"), tree="T1")), ["done"])

    def test_pending_ask_blocks_done_and_clears(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        fx = self.step(ev("before_tool", tool="ask", tool_use="tu1"))
        self.assertEqual(fx[0].body["kind"], "ask")
        self.assertEqual(self.step(ev("turn_end"), tree="T1"), [])
        self.step(ev("after_tool", tool="ask", tool_use="tu1"))
        self.assertEqual(self.s.task.pending_ask, set())
        self.assertEqual(self.kinds(self.step(ev("turn_end"), tree="T2")), ["done"])

    def test_changed_head_or_branch_ends_the_change(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        self.s.change_asked = True
        self.s.fact_printed = True
        self.step(ev("turn_end"), tree="T1")
        fx = self.step(
            ev("prompt_submit", prompt="next"), tree="T1", head=HeadState("c1", "main")
        )
        self.assertEqual(self.kinds(fx), ["change_ended", "task_started"])
        self.assertEqual(fx[0].body["to_commit"], "c1")
        self.assertFalse(self.s.change_asked)
        self.assertFalse(self.s.fact_printed)
        self.assertIsNone(self.s.previous_base)
        self.assertNotEqual(self.s.task.change_id, "ID1")
        fx = self.step(ev("turn_end"), tree="T2", head=HeadState("c1", "feature"))
        self.assertEqual(self.kinds(fx), ["change_ended"])
        self.assertIsNone(self.s.task)
        self.assertEqual(self.s.last_turn_end_tree, "T2")

    def test_next_task_after_done_keeps_change_and_previous_base(self) -> None:
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        self.step(ev("turn_end"), tree="T1")
        first = self.s.task
        fx = self.step(ev("prompt_submit", prompt="more"), tree="T1")
        self.assertEqual(self.kinds(fx), ["task_started"])
        self.assertEqual(self.s.previous_base, "T0")
        self.assertEqual(self.s.task.change_id, first.change_id)
        self.assertEqual(self.s.task.base_tree, "T1")
        self.assertEqual(self.step(ev("turn_end"), tree="T1"), [])

    def test_piped_run_with_failing_ids_is_a_failing_run(self) -> None:
        # pytest -q | tail exits 0 through the pipe; the failing ids say otherwise.
        self.step(ev("prompt_submit", prompt="x"), tree="T0")
        fx = self.step(
            ev(
                "after_tool",
                tool="shell",
                command="python -m pytest -q 2>&1 | tail -5",
                exit=0,
                failing=("tests/test_total.py::test_total",),
            ),
            tree="R1",
        )
        self.assertEqual(self.kinds(fx), ["task_event", "test_failed"])
        self.assertEqual(fx[1].body["failing"], ["tests/test_total.py::test_total"])
        self.assertNotEqual(self.s.task.last_test_exit, 0)
        self.assertEqual(self.step(ev("turn_end"), tree="T1"), [])

    def test_prompt_after_a_turn_that_built_nothing_starts_a_task(self) -> None:
        self.step(
            ev("prompt_submit", prompt="morning. what does reports.py do?"), tree="T0"
        )
        self.assertEqual(self.step(ev("turn_end"), tree="T0"), [])
        first = self.s.task
        fx = self.step(ev("prompt_submit", prompt="add a memo length limit"), tree="T0")
        self.assertEqual(self.kinds(fx), ["task_started"])
        self.assertEqual(fx[0].body["name"], "add a memo length limit")
        self.assertNotEqual(self.s.task.id, first.id)
        self.assertEqual(self.s.task.change_id, first.change_id)
        self.assertIsNone(self.s.previous_base)
        # Once something is built, a later prompt stays in the task.
        self.step(ev("after_tool", tool="edit", paths=("/p/a.py",)), tree=None)
        fx = self.step(ev("prompt_submit", prompt="also b"), tree="T1")
        self.assertEqual(self.kinds(fx), ["task_event"])

    def test_events_with_no_task_are_ignored(self) -> None:
        self.assertEqual(self.step(self.run_ev(0)), [])
        self.assertEqual(self.step(ev("before_tool", tool="ask", tool_use="x")), [])
        self.assertEqual(self.step(ev("turn_end"), tree="T9"), [])
        self.assertEqual(self.s.last_turn_end_tree, "T9")
        self.step(ev("session_start", source="startup", venv="/venv"))
        self.assertEqual(self.s.venv, "/venv")

    def test_task_name(self) -> None:
        table = {
            "Make refunds idempotent, and add tests": "Make refunds idempotent",
            "one two three four five six seven eight": "one two three four five six",
            "fix it?": "fix it",
            "": "this task",
            "   ": "this task",
            "\nsecond line": "this task",
            "a" * 60: "a" * 48,
        }
        for prompt, want in table.items():
            self.assertEqual(tl.task_name(prompt), want, prompt)
