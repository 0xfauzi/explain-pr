"""Call it: before any fix, where is the cause of a failing test?

The pick form only (build-2.md section 11, 2b). The engine reaches this moment
through the names below and through `call_it_run` for the two runs: the red run,
which confirms the failure in a scratch copy and reads the trace, and the fix run,
which undoes the fix and runs the test again. The line form and the Which change
form are not built: the first needs a reader, the second a bisect.
"""

from __future__ import annotations

import difflib
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath

from firsthand import gitwatch
from firsthand.model import Answer, FileChange, Key, Reply, Score
from firsthand.runner import pytest_adapter
from firsthand.runner.snapshot import SnapshotStore

KIND = "call_it"
SKILL = 3
HEADLINE = "CALL IT"
BREAKS = ("failure_prompt", "failure_turn_end")
MAX_PICKS = 3
NOTE_TRACE = "named in the trace"
NOTE_CHANGED = "changed in this task"
FIXED_ANSWER = "the file changed in this task"

_TRACEBACK = re.compile(r"Traceback \(most recent call last\)")
_FAILED = re.compile(r"^FAILED (\S+)", re.MULTILINE)
_PY_FRAME = re.compile(r'File "([^"]+?\.py)", line (\d+)(?:, in (\S+))?')
_PYTEST_FRAME = re.compile(r"^(\S+?\.py):(\d+):(?: in (\S+))?", re.MULTILINE)
_PARAM = re.compile(r"\[.*\]$")

_SLEEP = re.compile(r"\bsleep\s*\(")
_BROAD = re.compile(r"^\s*except\s*(:|\(?\s*(Exception|BaseException)\b)")
_SKIP = re.compile(
    r"pytest\.mark\.(skip|skipif|xfail)\b|pytest\.(skip|xfail)\s*\(|unittest\.skip|@skip\b"
)
_ASSERT = re.compile(r"^\s*(assert\b|self\.assert\w*\s*\()")
PATTERN_ORDER = ("sleep", "except", "assert", "skip")


@dataclass(frozen=True)
class Frame:
    path: str  # relative to the project root
    line: int
    where: str | None = None  # the function name, when the trace gives it


@dataclass(frozen=True)
class Case:
    """One Call it check: the failure, its red and green trees, the card's picks."""

    check_id: str  # the moment id when a question is asked
    project_id: str
    project_root: str
    task_id: str
    change_id: str
    test: str  # a pytest node id with no parameter suffix
    red_tree: str
    green_tree: str | None = None
    picks: tuple[Mapping[str, object], ...] = ()
    frames: tuple[Frame, ...] = ()
    fix_changes: tuple[FileChange, ...] = ()  # non-test files changed from red to green
    changed: tuple[str, ...] = ()  # every path changed from red to green
    patterns: tuple[Mapping[str, object], ...] = ()


# ------------------------------------------------------------------ triggers


def is_failure_prompt(text: str | None) -> bool:
    """A pasted traceback or a pytest FAILED line."""
    text = text or ""
    return bool(_TRACEBACK.search(text) or _FAILED.search(text))


def strip_param(test_id: str) -> str:
    return _PARAM.sub("", test_id)


def failed_ids(text: str | None) -> list[str]:
    """Test ids from FAILED lines, parameter suffix removed, in order, once each."""
    found: list[str] = []
    for match in _FAILED.finditer(text or ""):
        tid = strip_param(match.group(1))
        if "::" in tid and tid not in found:
            found.append(tid)
    return found


def _relative(path: str, root: str) -> str | None:
    p = path.replace("\\", "/")
    if p.startswith("/"):
        prefix = root.rstrip("/") + "/"
        if not p.startswith(prefix):
            return None
        p = p[len(prefix) :]
    p = p.removeprefix("./")
    if not p or p.startswith("../") or "site-packages/" in p:
        return None
    return p


def frames_from_text(text: str | None, root: str) -> tuple[Frame, ...]:
    """Frames named in a pasted trace or a junit failure, outermost first."""
    out: list[Frame] = []
    for pattern in (_PY_FRAME, _PYTEST_FRAME):
        for match in pattern.finditer(text or ""):
            rel = _relative(match.group(1), root)
            if rel is None:
                continue
            frame = Frame(rel, int(match.group(2)), match.group(3))
            if frame not in out:
                out.append(frame)
    return tuple(out)


def qualifying_test(
    failing: Iterable[str], store: SnapshotStore, base_tree: str, red_tree: str
) -> str | None:
    """The first failing test that exists at the base and is not edited at red."""
    for raw in failing:
        tid = strip_param(raw)
        path = tid.split("::", 1)[0]
        if "::" not in tid or not path.endswith(".py"):
            continue
        base_src = store.read_file(base_tree, path)
        red_src = store.read_file(red_tree, path)
        if base_src is None or red_src is None:
            continue
        if tid not in {t.id for t in pytest_adapter.list_tests(base_src, path)}:
            continue
        edited = {t.id for t in pytest_adapter.changed_tests(base_src, red_src, path)}
        if tid not in edited:
            return tid
    return None


def covers(command: str | None, test_id: str) -> bool:
    """Whether a passing run of `command` ran `test_id`: a whole-suite run, or one naming it."""
    words = (command or "").split()
    named = [
        w
        for w in words
        if not w.startswith("-")
        and "=" not in w
        and ("/" in w or ".py" in w or "::" in w)
    ]
    if not named:
        return True
    path = test_id.split("::", 1)[0]
    for word in named:
        target = word.rstrip("/")
        if "::" in target:
            if test_id == target or test_id.startswith(target + "::"):
                return True
        elif path == target or path.startswith(target + "/"):
            return True
    return False


# --------------------------------------------------------------------- picks


def _traced(frames: Sequence[Frame]) -> list[str]:
    """Non-test files named in the trace, innermost first, once each."""
    out: list[str] = []
    for f in reversed(frames):
        if not gitwatch.is_test_path(f.path) and f.path not in out:
            out.append(f.path)
    return out


def _interleave(a: Sequence[str], b: Sequence[str], limit: int) -> list[str]:
    chosen: list[str] = []
    for i in range(max(len(a), len(b))):
        for source in (a, b):
            if i < len(source) and source[i] not in chosen:
                chosen.append(source[i])
    return chosen[:limit]


def build_picks(
    frames: Sequence[Frame], changed: Sequence[str]
) -> tuple[dict[str, object], ...]:
    """Up to three files: named in the trace (innermost first) and changed in the task.

    The list is sorted by path, so a position on the card says nothing.
    """
    traced = _traced(frames)
    touched = [p for p in sorted(changed) if not gitwatch.is_test_path(p)]
    picks = []
    for n, path in enumerate(sorted(_interleave(traced, touched, MAX_PICKS)), start=1):
        notes = [NOTE_TRACE] if path in traced else []
        notes += [NOTE_CHANGED] if path in touched else []
        picks.append({"n": n, "path": path, "note": ", ".join(notes)})
    return tuple(picks)


# ----------------------------------------------------------------- symptoms


def _added_and_removed(
    red: str | None, green: str | None
) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    a = (red or "").splitlines()
    b = (green or "").splitlines()
    added: list[tuple[int, str]] = []
    removed: list[tuple[int, str]] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if op in ("replace", "delete"):
            removed += [(i + 1, a[i]) for i in range(i1, i2)]
        if op in ("replace", "insert"):
            added += [(j + 1, b[j]) for j in range(j1, j2)]
    return added, removed


def _code(line: str) -> str:
    return line.split("#", 1)[0]


def _patterns_in(path: str, red: str | None, green: str | None) -> list[dict]:
    added, removed = _added_and_removed(red, green)
    found: list[dict] = []
    for line_no, text in added:
        code = _code(text)
        for kind, rx in (("sleep", _SLEEP), ("except", _BROAD), ("skip", _SKIP)):
            if rx.search(code):
                found.append({"kind": kind, "path": path, "line": line_no})
    if gitwatch.is_test_path(path):
        for line_no, text in removed:
            if _ASSERT.search(_code(text)):
                found.append({"kind": "assert", "path": path, "line": line_no})
    return found


def symptoms(
    store: SnapshotStore, red_tree: str, green_tree: str, changes: Sequence[FileChange]
) -> tuple[dict, ...]:
    """Added sleep, bare or broad except or skip, and removed or changed asserts."""
    found: list[dict] = []
    for change in changes:
        if not change.path.endswith(".py"):
            continue
        red = store.read_file(red_tree, change.path) if change.status != "A" else None
        green = (
            store.read_file(green_tree, change.path) if change.status != "D" else None
        )
        found += _patterns_in(change.path, red, green)
    found.sort(key=lambda p: (PATTERN_ORDER.index(p["kind"]), p["path"], p["line"]))
    return tuple(found)


# ------------------------------------------------------------------- scoring


def _extra(k: Key) -> Mapping[str, object]:
    return k.extra or {}


def _picks(k: Key) -> list[Mapping[str, object]]:
    return list(_extra(k).get("picks", ()))  # type: ignore[arg-type]


def fix_paths(k: Key) -> list[str]:
    return list(_extra(k).get("fix_paths", ()))  # type: ignore[arg-type]


def patterns(k: Key) -> list[Mapping[str, object]]:
    return list(_extra(k).get("patterns", ()))  # type: ignore[arg-type]


def unscored_reason(k: Key) -> str | None:
    """Why no call on this key can be scored, or None."""
    if patterns(k):
        return "symptom-patch"
    if not fix_paths(k):
        return "no-fix"
    if not k.tests or k.tests[0].result == "still_passes":
        return "fix-not-causal"
    return None


def _matched(answer: str, k: Key) -> bool | None:
    picks = _picks(k)
    fix = set(fix_paths(k))
    if not answer.isdigit():
        return None
    n = int(answer)
    if 1 <= n <= len(picks):
        return str(picks[n - 1]["path"]) in fix
    if n == len(picks) + 1:
        return not any(str(p["path"]) in fix for p in picks)
    return None


def _fixed_answer_holds(k: Key) -> bool:
    fix = set(fix_paths(k))
    return any(
        NOTE_CHANGED in str(p.get("note", "")) and str(p["path"]) in fix
        for p in _picks(k)
    )


def score(answer: Answer, k: Key) -> Score | None:
    if answer == "dont_know":
        return None
    reason = unscored_reason(k)
    if reason is not None:
        return Score("unscored", "common", False, reason)
    matched = _matched(answer, k)
    if matched is None:
        return None
    uncommon = not _fixed_answer_holds(k)
    return Score(
        result="match" if matched else "miss",
        outcome_kind="uncommon" if uncommon else "common",
        catch=matched and uncommon,
        unscored_reason=None,
    )


def cue_path(k: Key) -> str | None:
    """The fix file the cue is about: one the trace names if there is one."""
    paths = fix_paths(k)
    frames = [f["path"] for f in _extra(k).get("frames", ())]  # type: ignore[union-attr]
    named = [p for p in paths if p in frames]
    return (named or paths or [None])[0]


def finding(k: Key) -> tuple:
    """Call it sends no finding to the agent: the agent made the fix itself."""
    return ()


# ------------------------------------------------------------------- replies


def reply_words(n_picks: int) -> tuple[str, ...]:
    return (*(str(i) for i in range(1, n_picks + 2)), "don't know")


def _normalise(text: str) -> str:
    text = " ".join(text.replace("’", "'").strip().lower().split())
    return text[:-1].rstrip() if text.endswith(".") else text


def parse_reply(text: str, n_picks: int) -> Reply | None:
    words = _normalise(text)
    confidence = None
    if words.endswith(" not sure"):
        words, confidence = words[: -len(" not sure")], "low"
    elif words.endswith(" sure"):
        words, confidence = words[: -len(" sure")], "high"
    if words not in reply_words(n_picks):
        return None
    if words == "don't know":
        return Reply("dont_know", None)
    return Reply(words, confidence)  # type: ignore[arg-type]


def name_of(test_id: str) -> str:
    return test_id.rsplit("::", 1)[-1]


def path_of(test_id: str) -> str:
    return str(PurePosixPath(test_id.split("::", 1)[0]))
