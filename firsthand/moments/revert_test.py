"""The Revert test: which new test would still pass with the change undone?

The engine reaches this moment only through the public names below, so later
moments add modules with the same surface.
"""

from __future__ import annotations

import shlex
import subprocess
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from firsthand import events, gitwatch
from firsthand.model import (
    Answer,
    Candidate,
    CheckOutcome,
    FileChange,
    FirsthandError,
    Key,
    KeyItem,
    ProjectSettings,
    Reply,
    Score,
    StepRun,
    TestItem,
    TestResult,
)
from firsthand.runner import generic_adapter, pytest_adapter
from firsthand.runner.scratch import Scratch, find_python, scrubbed_env, source_wins
from firsthand.runner.snapshot import SnapshotStore

KIND = "revert_test"
SKILL = 1
HEADLINE = "REVERT TEST"
BREAKS = ("test_run", "done")
MAX_TESTS = 4

_STEPS = ("scratch", "control", "undo", "undone")
# Failures run() turns into "snapshot failed" instead of raising.
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
class MatchInput:
    project_id: str
    project_root: str
    task_id: str
    change_id: str
    base_tree: str
    head_tree: str
    changes: tuple[FileChange, ...]
    test_command: str | None
    high_stakes: tuple[str, ...]


@dataclass(frozen=True)
class RunContext:
    store: SnapshotStore
    project: ProjectSettings
    venv_hint: str | None
    time_limit_s: float
    on_control: Callable[[bool], None]
    cancel: threading.Event


# ------------------------------------------------------------------ match


def _moved_tests(
    m: MatchInput, store: SnapshotStore, tests: Sequence[FileChange]
) -> set[tuple[str, str]]:
    """Tests of a deleted test file: one that reappears unchanged in an added file
    was moved or renamed, not written (diff runs with no rename detection)."""
    moved: set[tuple[str, str]] = set()
    for change in tests:
        if change.status == "D" and change.path.endswith(".py"):
            moved |= pytest_adapter.test_dumps(
                store.read_file(m.base_tree, change.path), change.path
            )
    return moved


def _file_tests(
    m: MatchInput,
    store: SnapshotStore,
    change: FileChange,
    moved: set[tuple[str, str]],
) -> list[TestItem]:
    """The new and edited tests of one added or modified test file."""
    head_src = store.read_file(m.head_tree, change.path)
    if head_src is None:
        return []
    base_src = (
        store.read_file(m.base_tree, change.path) if change.status == "M" else None
    )
    kept = {sfx for sfx, _ in pytest_adapter.test_dumps(head_src, change.path) & moved}
    return [
        item
        for item in pytest_adapter.changed_tests(base_src, head_src, change.path)
        if not (item.status == "new" and item.id.split("::", 1)[1] in kept)
    ]


def _pytest_tests(
    m: MatchInput, store: SnapshotStore, tests: Sequence[FileChange]
) -> list[TestItem]:
    moved = _moved_tests(m, store, tests)
    items: list[TestItem] = []
    for change in tests:
        if change.status in ("A", "M") and change.path.endswith(".py"):
            items += _file_tests(m, store, change, moved)
    return [i for i in items if i.status == "new"] + [
        i for i in items if i.status != "new"
    ]


def match(
    m: MatchInput, store: SnapshotStore, new_id: Callable[[], str]
) -> Candidate | None:
    if not m.test_command:
        return None
    source, tests = gitwatch.split_changes(m.changes)
    if not source or not any(t.status in ("A", "M") for t in tests):
        return None
    how = "pytest" if gitwatch.runner_token(m.test_command) == "pytest" else "exit_code"
    if how == "pytest":
        found = _pytest_tests(m, store, tests)
    else:
        found = list(generic_adapter.test_files(m.changes))
    if not found:
        return None
    numbered = tuple(replace(item, n=i + 1) for i, item in enumerate(found[:MAX_TESTS]))
    return Candidate(
        kind=KIND,
        check_id=new_id(),
        project_id=m.project_id,
        project_root=m.project_root,
        task_id=m.task_id,
        change_id=m.change_id,
        base_tree=m.base_tree,
        head_tree=m.head_tree,
        source_changes=source,
        tests=numbered,
        how=how,
        high_stakes=gitwatch.first_match([c.path for c in m.changes], m.high_stakes),
    )


def plan(c: Candidate) -> tuple[str, ...]:
    return _STEPS


# -------------------------------------------------------------------- run


class _Stop(Exception):
    """Ends a run early with an outcome."""

    def __init__(self, outcome: CheckOutcome) -> None:
        super().__init__(outcome.unavailable or "cancelled")
        self.outcome = outcome


class _Runner:
    """One check from scratch copy to classified results. Used only by run()."""

    def __init__(self, c: Candidate, ctx: RunContext) -> None:
        self.c = c
        self.ctx = ctx
        self.start = time.monotonic()
        self.deadline = self.start + ctx.time_limit_s
        self.steps: list[StepRun] = []
        self.control_told = False
        self.scratch: Scratch | None = None
        self.python: Path | None = None
        self.env: dict[str, str] = {}

    # -- helpers

    def tell_control(self, ok: bool) -> None:
        if not self.control_told:
            self.control_told = True
            self.ctx.on_control(ok)

    def stop(self, reason: str | None, step: str) -> _Stop:
        if reason is None:
            return _Stop(CheckOutcome(None, None))
        self.tell_control(False)
        return _Stop(CheckOutcome(None, reason, step, tuple(self.steps)))  # type: ignore[arg-type]

    def groups(self) -> list[tuple[str, list[TestItem]]]:
        """Tests grouped by file, in card order: one run per file."""
        by_file: dict[str, list[TestItem]] = {}
        for item in self.c.tests:
            by_file.setdefault(item.path, []).append(item)
        return list(by_file.items())

    def _argv(self, path: str, items: list[TestItem], junit: Path) -> list[str]:
        if self.c.how == "pytest":
            assert self.python is not None
            return pytest_adapter.argv(self.python, [i.id for i in items], junit)
        return generic_adapter.argv(self.ctx.project.test_command or "", path)

    def run_step(self, step: str) -> dict[str, tuple[TestResult, int | None]]:
        assert self.scratch is not None
        results: dict[str, tuple[TestResult, int | None]] = {}
        for n, (path, items) in enumerate(self.groups(), start=1):
            if self.ctx.cancel.is_set():
                raise self.stop(None, step)
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise self.stop("time limit", step)
            junit = self.scratch.out / f"{step}-{n}.xml"
            argv = self._argv(path, items, junit)
            res = self.scratch.run(
                argv, env=self.env, timeout_s=remaining, cancel=self.ctx.cancel
            )
            if self.ctx.cancel.is_set():
                raise self.stop(None, step)
            if res.timed_out:
                self.steps.append(
                    self._step_run(step, argv, res.exit, (), res.output_sha256)
                )
                raise self.stop("time limit", step)
            got = self._classify(items, junit, res.exit)
            if step == "undone" and self._missing(items, junit):
                # A test with no result was never run (a stop-early option, a crash):
                # nothing can be said about it, so the check gives no key.
                self.steps.append(
                    self._step_run(step, argv, res.exit, (), res.output_sha256)
                )
                raise self.stop("does not match here", step)
            failing = tuple(i for i, (r, _) in got.items() if r != "still_passes")
            self.steps.append(
                self._step_run(step, argv, res.exit, failing, res.output_sha256)
            )
            results.update(got)
        return results

    def _classify(
        self, items: list[TestItem], junit: Path, exit_code: int | None
    ) -> dict[str, tuple[TestResult, int | None]]:
        if self.c.how == "pytest":
            read = pytest_adapter.read_junit(junit, [i.id for i in items])
            return {
                i: (pytest_adapter.classify(o), line) for i, (o, line) in read.items()
            }
        return {i.id: (generic_adapter.classify(exit_code), None) for i in items}

    def _missing(self, items: list[TestItem], junit: Path) -> bool:
        if self.c.how != "pytest" or not junit.is_file():
            return False  # no junit file: pytest stopped before any test, cannot run
        read = pytest_adapter.read_junit(junit, [i.id for i in items])
        return any(o == "missing" for o, _ in read.values())

    @staticmethod
    def _step_run(
        step: str,
        argv: Sequence[str],
        exit_code: int | None,
        failing: tuple[str, ...],
        sha: str,
    ) -> StepRun:
        command, _ = events.scan_secrets(shlex.join(argv))
        return StepRun(step, command, exit_code, failing, sha)  # type: ignore[arg-type]

    # -- the steps

    def setup(self) -> None:
        try:
            self.scratch = Scratch(self.ctx.store, self.c.head_tree, self.c.check_id)
        except (FirsthandError, OSError):
            raise self.stop("snapshot failed", "setup") from None
        project_root = Path(self.c.project_root)
        self.python = find_python(project_root, self.ctx.venv_hint)
        if self.python is None:
            raise self.stop("no interpreter", "setup")
        self.env = scrubbed_env(
            self.scratch, python=self.python, extra=self.ctx.project.env
        )
        if self.c.how != "pytest":
            return
        if not pytest_adapter.has_pytest(self.python, self.env, self.scratch.tree):
            raise self.stop("pytest not found", "setup")
        if not source_wins(
            self.python, self.scratch, self.env, self.c.source_changes, project_root
        ):
            raise self.stop("editable install", "setup")

    def control(self) -> None:
        results = self.run_step("control")
        if any(r != "still_passes" for r, _ in results.values()):
            raise self.stop("does not match here", "control")
        self.tell_control(True)

    def undone(self) -> CheckOutcome:
        assert self.scratch is not None
        try:
            undone_paths = self.scratch.undo(self.c.base_tree, self.c.source_changes)
        except (FirsthandError, OSError):
            raise self.stop("snapshot failed", "undone") from None
        results = self.run_step("undone")
        if self.ctx.cancel.is_set():
            raise self.stop(None, "undone")
        duration = round(time.monotonic() - self.start, 3)
        k = key(self.c, results, self.steps, undone_paths, duration, events.now_stamp())
        return CheckOutcome(k, None, None, tuple(self.steps))


def run(c: Candidate, ctx: RunContext) -> CheckOutcome:
    """Scratch copy, control run, undo, undone run. Never raises."""
    runner = _Runner(c, ctx)
    try:
        runner.setup()
        runner.control()
        return runner.undone()
    except _Stop as stop:
        return stop.outcome
    except _UNEXPECTED:  # the contract: run never raises
        if ctx.cancel.is_set():
            return CheckOutcome(None, None)
        return runner.stop(
            "snapshot failed", "setup" if runner.scratch is None else "undone"
        ).outcome
    finally:
        if runner.scratch is not None:
            runner.scratch.close()


# -------------------------------------------------------------------- key


def key(
    c: Candidate,
    results: Mapping[str, tuple[TestResult, int | None]],
    steps: Sequence[StepRun],
    undone_paths: Sequence[str],
    duration_s: float,
    made_at: str,
) -> Key:
    items = []
    for t in c.tests:
        result, line = results.get(t.id, ("cannot_run", None))
        items.append(
            KeyItem(
                id=t.id,
                result=result,
                assert_line=t.assert_line,
                assert_text=t.assert_text,
                fail_line=line if result != "still_passes" else None,
            )
        )
    return Key(
        moment=c.check_id,
        kind=c.kind,
        how=c.how,
        base_tree=c.base_tree,
        head_tree=c.head_tree,
        made_at=made_at,
        tests=tuple(items),
        steps=tuple(steps),
        undone_paths=tuple(undone_paths),
        duration_s=duration_s,
    )


# ------------------------------------------------------------ scoring


def _picked(answer: Answer, k: Key) -> KeyItem | None:
    if answer.isdigit() and 1 <= int(answer) <= len(k.tests):
        return k.tests[int(answer) - 1]
    return None


def _matched(answer: Answer, k: Key) -> bool | None:
    """True or False for a scorable answer, None for one that cannot be scored."""
    any_passes = any(t.result == "still_passes" for t in k.tests)
    if len(k.tests) >= 2:
        if answer == "none":
            return not any_passes
        picked = _picked(answer, k)
        return None if picked is None else picked.result == "still_passes"
    if len(k.tests) == 1:
        result = k.tests[0].result
        if answer == "fails":
            return result in ("fails_on_assertion", "cannot_run", "does_not_pass")
        if answer == "passes":
            return result == "still_passes"
    return None


def score(answer: Answer, k: Key) -> Score | None:
    if answer == "dont_know":
        return None
    matched = _matched(answer, k)
    if matched is None:
        return None
    uncommon = any(t.result == "still_passes" for t in k.tests)
    return Score(
        result="match" if matched else "miss",
        outcome_kind="uncommon" if uncommon else "common",
        catch=matched and uncommon,
        unscored_reason=None,
    )


def _path(item: KeyItem) -> str:
    return item.id.split("::", 1)[0]


def _and_list(numbers: Sequence[int]) -> str:
    text = [str(n) for n in numbers]
    if len(text) == 1:
        return text[0]
    return ", ".join(text[:-1]) + " and " + text[-1]


def _assert_cue(item: KeyItem, source: TestItem | None) -> str:
    path = _path(item)
    if source is not None:
        lines: tuple[int, ...] = source.assert_lines
    else:
        lines = (item.assert_line,) if item.assert_line is not None else ()
    if len(lines) == 1:
        return f"Its only assertion is at {path}:{lines[0]}."
    if lines:
        return f"Its assertions are at {path}:{_and_list(lines)}."
    if source is not None:
        return f"It has no assert statement: {path}:{source.line}."
    return f"It has no assert statement: {path}."


def _fail_cue(item: KeyItem, source: TestItem | None) -> str:
    path = _path(item)
    line = (
        item.fail_line
        or item.assert_line
        or (source.line if source is not None else None)
    )
    return f"It fails at {path}:{line}." if line is not None else f"It fails at {path}."


def cue(
    answer: Answer, k: Key, tests: Sequence[TestItem] = ()
) -> tuple[str, tuple[KeyItem, ...]] | None:
    """What would have shown it, from line numbers only. None on a match.

    `tests` is optional: the card's TestItems give every assertion line and the def
    line, which a Key does not hold.
    """
    matched = _matched(answer, k) if answer != "dont_know" else None
    if matched is None or matched:
        return None
    sources = {t.id: t for t in tests}
    passing = [t for t in k.tests if t.result == "still_passes"]
    target = passing[0] if passing else (_picked(answer, k) or k.tests[0])
    if k.how == "exit_code":
        return f"It was checked by exit code only: {_path(target)}.", (target,)
    if passing:
        return _assert_cue(target, sources.get(target.id)), (target,)
    return _fail_cue(target, sources.get(target.id)), (target,)


def finding(k: Key) -> tuple[KeyItem, ...]:
    return tuple(t for t in k.tests if t.result in ("still_passes", "cannot_run"))


# ------------------------------------------------------------- replies


def reply_words(n_tests: int) -> tuple[str, ...]:
    if n_tests >= 2:
        return (*(str(i) for i in range(1, n_tests + 1)), "none", "don't know")
    return ("fails", "passes", "don't know")


def _normalise(text: str) -> str:
    text = " ".join(text.replace("’", "'").strip().lower().split())
    return text[:-1].rstrip() if text.endswith(".") else text


def parse_reply(text: str, n_tests: int) -> Reply | None:
    words = _normalise(text)
    confidence = None
    if words.endswith(" not sure"):
        words, confidence = words[: -len(" not sure")], "low"
    elif words.endswith(" sure"):
        words, confidence = words[: -len(" sure")], "high"
    if words not in reply_words(n_tests):
        return None
    if words == "don't know":
        return Reply("dont_know", None)
    return Reply(words, confidence)  # type: ignore[arg-type]
