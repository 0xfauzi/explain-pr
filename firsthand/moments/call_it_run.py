"""The two runs of Call it, each in a scratch copy. Neither raises.

- The red run, at the failure: the failing test is run on the red snapshot. It must
  fail there too (the control), or nothing is asked. Its junit failure text gives
  the trace frames and the message the card shows.
- The fix run, at the first green run: the test is run on the green snapshot (the
  control, it must pass), then every non-test file changed between red and green is
  put back as it was at red and the test is run again.
"""

from __future__ import annotations

import shlex
import subprocess
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from firsthand import events
from firsthand.model import (
    CheckOutcome,
    FirsthandError,
    Key,
    KeyItem,
    StepRun,
)
from firsthand.moments.call_it import KIND, Case, Frame, frames_from_text, strip_param
from firsthand.moments.revert_test import RunContext
from firsthand.runner import pytest_adapter
from firsthand.runner.scratch import Scratch, find_python, scrubbed_env, source_wins

MAX_MESSAGE = 200
_UNEXPECTED = (
    OSError,
    ValueError,
    LookupError,
    TypeError,
    AttributeError,
    RuntimeError,
    subprocess.SubprocessError,
)


@dataclass(frozen=True)
class RedOutcome:
    ok: bool  # the test fails on the red snapshot as it did in the agent's run
    unavailable: str | None
    frames: tuple[Frame, ...] = ()
    message: str | None = None
    cancelled: bool = False


class _Stop(Exception):
    def __init__(self, reason: str | None, step: str) -> None:
        super().__init__(reason or "cancelled")
        self.reason = reason
        self.step = step


def _failure(junit: Path, test_id: str) -> tuple[str | None, str]:
    """(message, text) of the test's failure or error element, or (None, "")."""
    try:
        root = ET.parse(junit).getroot()
    except (OSError, ET.ParseError):
        return None, ""
    func = test_id.rsplit("::", 1)[-1]
    for case in root.iter("testcase"):
        name = strip_param(case.get("name", ""))
        element = case.find("failure")
        if element is None:
            element = case.find("error")
        if element is not None and (name == func or not name):
            return element.get("message"), element.text or ""
    return None, ""


def _first_line(text: str | None) -> str | None:
    for line in (text or "").splitlines():
        if line.strip():
            return " ".join(line.split())[:MAX_MESSAGE]
    return None


class _Run:
    """Shared setup and one pytest run of the case's test."""

    def __init__(self, case: Case, ctx: RunContext, tree: str) -> None:
        self.case = case
        self.ctx = ctx
        self.tree = tree
        self.start = time.monotonic()
        self.deadline = self.start + ctx.time_limit_s
        self.scratch: Scratch | None = None
        self.python: Path | None = None
        self.env: dict[str, str] = {}
        self.steps: list[StepRun] = []

    def setup(self) -> None:
        try:
            self.scratch = Scratch(self.ctx.store, self.tree, self.case.check_id)
        except (FirsthandError, OSError):
            raise _Stop("snapshot failed", "setup") from None
        root = Path(self.case.project_root)
        self.python = find_python(root, self.ctx.venv_hint)
        if self.python is None:
            raise _Stop("no interpreter", "setup")
        self.env = scrubbed_env(
            self.scratch, python=self.python, extra=self.ctx.project.env
        )
        if not pytest_adapter.has_pytest(self.python, self.env, self.scratch.tree):
            raise _Stop("pytest not found", "setup")
        if not source_wins(
            self.python, self.scratch, self.env, self.case.fix_changes, root
        ):
            raise _Stop("editable install", "setup")

    def run(self, step: str) -> tuple[str, int | None, Path]:
        """Run the test once. Returns its outcome, the junit line and the junit path."""
        assert self.scratch is not None and self.python is not None
        if self.ctx.cancel.is_set():
            raise _Stop(None, step)
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise _Stop("time limit", step)
        junit = self.scratch.out / f"{step}.xml"
        argv = pytest_adapter.argv(self.python, [self.case.test], junit)
        res = self.scratch.run(
            argv, env=self.env, timeout_s=remaining, cancel=self.ctx.cancel
        )
        if self.ctx.cancel.is_set():
            raise _Stop(None, step)
        outcome, line = pytest_adapter.read_junit(junit, [self.case.test])[
            self.case.test
        ]
        failing = () if outcome == "passed" else (self.case.test,)
        command, _ = events.scan_secrets(shlex.join(argv))
        self.steps.append(StepRun(step, command, res.exit, failing, res.output_sha256))  # type: ignore[arg-type]
        if res.timed_out:
            raise _Stop("time limit", step)
        return outcome, line, junit

    def close(self) -> None:
        if self.scratch is not None:
            self.scratch.close()


def _existing(frames: tuple[Frame, ...], tree: Path) -> tuple[Frame, ...]:
    return tuple(f for f in frames if (tree / f.path).is_file())


def run_red(case: Case, ctx: RunContext) -> RedOutcome:
    """The control at the failure: the test must fail on the red snapshot."""
    r = _Run(case, ctx, case.red_tree)
    try:
        r.setup()
        outcome, _, junit = r.run("red")
        if outcome in ("passed", "skipped", "missing"):
            ctx.on_control(False)
            return RedOutcome(False, "does not match here")
        message, text = _failure(junit, case.test)
        assert r.scratch is not None
        frames = _existing(frames_from_text(text, str(r.scratch.tree)), r.scratch.tree)
        ctx.on_control(True)
        return RedOutcome(True, None, frames, _first_line(message))
    except _Stop as stop:
        if stop.reason is None:
            return RedOutcome(False, None, cancelled=True)
        ctx.on_control(False)
        return RedOutcome(False, stop.reason)
    except _UNEXPECTED:
        if ctx.cancel.is_set():
            return RedOutcome(False, None, cancelled=True)
        ctx.on_control(False)
        return RedOutcome(False, "snapshot failed")
    finally:
        r.close()


def _key(case: Case, r: _Run, outcome: str, line: int | None, undone: tuple) -> Key:
    result = pytest_adapter.classify(outcome)
    item = KeyItem(
        id=case.test,
        result=result,
        assert_line=None,
        assert_text=None,
        fail_line=line if result != "still_passes" else None,
    )
    extra = {
        "test": case.test,
        "picks": [dict(p) for p in case.picks],
        "frames": [{"path": f.path, "line": f.line} for f in case.frames],
        "fix_paths": [c.path for c in case.fix_changes],
        "changed": list(case.changed),
        "patterns": [dict(p) for p in case.patterns],
    }
    return Key(
        moment=case.check_id,
        kind=KIND,
        how="pytest",
        base_tree=case.red_tree,
        head_tree=case.green_tree or "",
        made_at=events.now_stamp(),
        tests=(item,),
        steps=tuple(r.steps),
        undone_paths=undone,
        duration_s=round(time.monotonic() - r.start, 3),
        extra=extra,
    )


def run(case: Case, ctx: RunContext) -> CheckOutcome:
    """The fix run: control on green, the fix undone, the test run again."""
    assert case.green_tree is not None
    r = _Run(case, ctx, case.green_tree)
    try:
        r.setup()
        outcome, _, _ = r.run("control")
        if outcome != "passed":
            ctx.on_control(False)
            return CheckOutcome(None, "does not match here", "control", tuple(r.steps))
        ctx.on_control(True)
        assert r.scratch is not None
        try:
            undone = r.scratch.undo(case.red_tree, case.fix_changes)
        except (FirsthandError, OSError):
            return CheckOutcome(None, "snapshot failed", "undone", tuple(r.steps))
        outcome, line, _ = r.run("undone")
        k = _key(case, r, outcome, line, undone)
        return CheckOutcome(k, None, None, tuple(r.steps))
    except _Stop as stop:
        if stop.reason is None:
            return CheckOutcome(None, None)
        return CheckOutcome(None, stop.reason, stop.step, tuple(r.steps))  # type: ignore[arg-type]
    except _UNEXPECTED:
        if ctx.cancel.is_set():
            return CheckOutcome(None, None)
        return CheckOutcome(None, "snapshot failed", "setup", tuple(r.steps))
    finally:
        r.close()
