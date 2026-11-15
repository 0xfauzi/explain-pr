"""Tasks, bases and the done signal, as a pure state machine.

It runs no git command and writes nothing. The engine feeds it each spool event
with what it observed (a snapshot tree when `needs_snapshot` said so, and HEAD),
and records the effects it returns.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Literal

from firsthand import gitwatch
from firsthand.model import HeadState, SpoolEvent

_CLAUSE_END = re.compile(r"[.,;:?!\n]")
TASK_NAME_WORDS = 6
TASK_NAME_CHARS = 48


@dataclass
class Task:
    id: str
    change_id: str
    name: str
    started_at: str
    base_tree: str
    base_at: str
    first_prompt_id: str
    prompts: list[str]
    last_test_exit: int | None = None
    test_seen: bool = False
    pending_ask: set[str] = field(default_factory=set)
    done: bool = False
    first_of_day: bool = False
    turn_ended: bool = False


@dataclass
class SessionState:
    agent: str
    session: str
    project_id: str
    project_root: str
    task: Task | None = None
    previous_base: str | None = None
    change_id: str | None = None
    change_asked: bool = False
    fact_printed: bool = False
    last_turn_end_tree: str | None = None
    head: HeadState | None = None
    venv: str | None = None
    skips: int = 0
    quiet: bool = False
    turn_first_of_day: bool = False


@dataclass(frozen=True)
class Observed:
    tree: str | None
    head: HeadState


@dataclass(frozen=True)
class Effect:
    kind: Literal[
        "change_ended",
        "task_started",
        "task_event",
        "test_passed",
        "test_failed",
        "done",
    ]
    body: Mapping[str, object]


def task_name(prompt: str) -> str:
    """The first clause of the prompt, cut to 6 words and 48 characters. "this task" when empty."""
    clause = _CLAUSE_END.split(prompt or "", maxsplit=1)[0]
    words = clause.split()[:TASK_NAME_WORDS]
    name = " ".join(words)
    if len(name) > TASK_NAME_CHARS:
        name = name[:TASK_NAME_CHARS].rstrip()
    return name or "this task"


def _is_test_shell(ev: SpoolEvent, test_command: str | None) -> bool:
    return ev.tool == "shell" and gitwatch.is_test_run(ev.command or "", test_command)


def needs_snapshot(s: SessionState, ev: SpoolEvent, test_command: str | None) -> bool:
    if ev.event in ("prompt_submit", "turn_end"):
        return True
    # A passing test run (a green snapshot) and a failing one (a red snapshot).
    return ev.event in ("after_tool", "tool_failed") and _is_test_shell(
        ev, test_command
    )


def _head_changed(s: SessionState, head: HeadState) -> bool:
    if s.head is None:
        return False
    return s.head.commit != head.commit or s.head.branch != head.branch


def _end_change(s: SessionState, head: HeadState) -> Effect:
    old = s.head
    body = {
        "from_commit": old.commit if old else None,
        "from_branch": old.branch if old else None,
        "to_commit": head.commit,
        "to_branch": head.branch,
        "change": s.change_id,
        "task": s.task.id if s.task else None,
    }
    s.task = None
    s.change_id = None
    s.change_asked = False
    s.fact_printed = False
    s.previous_base = None
    s.last_turn_end_tree = None
    return Effect("change_ended", body)


def _nothing_built(task: Task, obs: Observed) -> bool:
    """A turn of this task has ended and the tree is still the task's base.

    A question asked before the work ("what does reports.py do?") is then not the
    task: the next prompt starts one, takes the base and names it.
    """
    return (
        task.turn_ended
        and not task.pending_ask
        and obs.tree is not None
        and obs.tree == task.base_tree
    )


def _on_prompt(
    s: SessionState,
    ev: SpoolEvent,
    obs: Observed,
    first_of_day: bool,
    new_id: Callable[[], str],
) -> list[Effect]:
    s.turn_first_of_day = first_of_day
    prompt = ev.prompt or ""
    task = s.task
    if task is not None and not task.done and not _nothing_built(task, obs):
        task.prompts.append(prompt)
        return [
            Effect(
                "task_event",
                {
                    "task": task.id,
                    "kind": "prompt",
                    "spool_id": ev.id,
                    "prompt": prompt,
                },
            )
        ]
    if task is not None and task.done:
        s.previous_base = task.base_tree  # nothing built: the earlier start stays
    if s.change_id is None:
        s.change_id = new_id()
    base = obs.tree or ""
    task = Task(
        id=new_id(),
        change_id=s.change_id,
        name=task_name(prompt),
        started_at=ev.at,
        base_tree=base,
        base_at=ev.at,
        first_prompt_id=ev.id,
        prompts=[prompt],
        first_of_day=first_of_day,
    )
    s.task = task
    body = {
        "task": task.id,
        "session": s.session,
        "name": task.name,
        "prompt": prompt,
        "base_tree": base,
        "base_at": ev.at,
        "head": obs.head.commit,
        "branch": obs.head.branch,
        "first_of_day": first_of_day,
        "spool_id": ev.id,
    }
    return [Effect("task_started", body)]


def _on_tool_result(
    s: SessionState, ev: SpoolEvent, obs: Observed, test_command: str | None
) -> list[Effect]:
    task = s.task
    assert task is not None
    if ev.tool == "ask" and ev.tool_use:
        task.pending_ask.discard(ev.tool_use)
    if not _is_test_shell(ev, test_command):
        return []
    # A null exit is stored as -1: it counts as failing and is not "no test was run".
    exit_code = ev.exit if ev.exit is not None else -1
    if exit_code == 0 and ev.failing:
        # Exit 0 with failing ids read from the output: the runner's exit was lost
        # in a pipe (pytest -q | tail). It is a failing run.
        exit_code = 1
    task.last_test_exit = exit_code
    task.test_seen = True
    effects = [
        Effect(
            "task_event",
            {
                "task": task.id,
                "kind": "test_run",
                "spool_id": ev.id,
                "command": ev.command,
                "exit": exit_code,
                "failing": list(ev.failing),
                "tree": obs.tree,
            },
        )
    ]
    if ev.event == "after_tool" and exit_code == 0:
        effects.append(Effect("test_passed", {"task": task.id, "tree": obs.tree}))
    elif exit_code != 0:
        body = {
            "task": task.id,
            "tree": obs.tree,
            "failing": list(ev.failing),
            "command": ev.command,
        }
        effects.append(Effect("test_failed", body))
    return effects


def _on_turn_end(s: SessionState, obs: Observed) -> list[Effect]:
    task = s.task
    previous = s.last_turn_end_tree
    s.last_turn_end_tree = obs.tree
    if task is not None:
        task.turn_ended = True
    if task is None or task.done or obs.tree is None:
        return []
    compare = previous if previous is not None else task.base_tree
    if obs.tree == compare:
        return []
    if task.last_test_exit not in (None, 0) or task.pending_ask:
        return []
    task.done = True
    return [Effect("done", {"task": task.id, "tree": obs.tree})]


def step(
    s: SessionState,
    ev: SpoolEvent,
    obs: Observed,
    *,
    test_command: str | None,
    first_of_day: bool,
    new_id: Callable[[], str],
) -> list[Effect]:
    """Apply one event to the session state. Returns the effects in order."""
    effects: list[Effect] = []
    if _head_changed(s, obs.head):
        effects.append(_end_change(s, obs.head))
    s.head = obs.head
    if ev.event in ("session_start", "prompt_submit") and ev.venv:
        s.venv = ev.venv
    if ev.event == "prompt_submit":
        effects += _on_prompt(s, ev, obs, first_of_day, new_id)
    elif ev.event == "turn_end":
        effects += _on_turn_end(s, obs)
    elif s.task is None:
        return effects
    elif ev.event == "before_tool":
        if ev.tool == "ask" and ev.tool_use:
            s.task.pending_ask.add(ev.tool_use)
            body = {"task": s.task.id, "kind": "ask", "spool_id": ev.id}
            if ev.question:
                body["question"] = ev.question
            effects.append(Effect("task_event", body))
    elif ev.event in ("after_tool", "tool_failed"):
        effects += _on_tool_result(s, ev, obs, test_command)
    return effects
