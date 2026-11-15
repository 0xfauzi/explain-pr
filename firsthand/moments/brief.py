"""Brief: one check that fails now and will pass when the task is done.

The person names a check in one line at the start of a multi-part task. The line
goes to the agent as work product. At the done signal the first test added in the
task is shown back ("Is this your check?") and, on yes, the Revert test's check is
the key: that one test with the change, and with the non-test changes undone.

Pure functions. The engine side is `engine_brief.py`; the run is `revert_test.run`
on a Candidate that holds the one test.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import replace

from firsthand import gitwatch
from firsthand.model import Answer, FileChange, Key, Reply, Score, TestItem
from firsthand.runner import pytest_adapter
from firsthand.runner.snapshot import SnapshotStore

KIND = "brief"
SKILL = 5
HEADLINE = "DONE CHECK"
BREAKS = ("task_start",)
MIN_CATEGORIES = 2
MAX_LINE_CHARS = 500

_TEST_ID = re.compile(r"::|\btest_\w+")
_WORD = re.compile(r"[^\s`'\"(),;]+")
_DONT_KNOW = ("don't know", "dont know", "i don't know")
_CONFIRM = {"yes": "yes", "y": "yes", "no": "no", "n": "no"}
_MARKER = re.compile(r"^check\s*:\s*(.*)$", re.IGNORECASE)


# ---------------------------------------------------------------- trigger


def names_check(prompt: str | None, test_command: str | None) -> bool:
    """The prompt names a test id, a test file or a command run by the test runner."""
    text = prompt or ""
    if _TEST_ID.search(text):
        return True
    words = _WORD.findall(text)
    if any(gitwatch.is_test_path(w) for w in words):
        return True
    token = gitwatch.runner_token(test_command or "")
    return bool(token) and any(w == token for w in words)


def is_question(prompt: str | None) -> bool:
    """A prompt that ends with a question mark asks, it does not start a build."""
    return (prompt or "").rstrip().endswith("?")


def categories(paths: Iterable[str]) -> list[str]:
    """The distinct path categories of non-test paths, in first-seen order."""
    seen: list[str] = []
    for path in paths:
        cat = gitwatch.category(path)
        if cat != "tests" and cat not in seen:
            seen.append(cat)
    return seen


def qualifies(cats: Sequence[str], plan: bool) -> bool:
    return plan or len(cats) >= MIN_CATEGORIES


# --------------------------------------------------------- the done check


def strip_param(test_id: str) -> str:
    return re.sub(r"\[.*\]$", "", test_id)


def new_tests(
    store: SnapshotStore, base_tree: str, head_tree: str, changes: Sequence[FileChange]
) -> list[TestItem]:
    """Tests that exist at head and not at base, by file path then line."""
    found: list[TestItem] = []
    for c in sorted(changes, key=lambda x: x.path):
        if c.status not in ("A", "M") or not c.path.endswith(".py"):
            continue
        if not gitwatch.is_test_path(c.path):
            continue
        head_src = store.read_file(head_tree, c.path)
        if head_src is None:
            continue
        base_src = store.read_file(base_tree, c.path) if c.status == "M" else None
        found += [
            t
            for t in pytest_adapter.changed_tests(base_src, head_src, c.path)
            if t.status == "new"
        ]
    return found


def first_test(found: Sequence[TestItem], red_ids: Sequence[str]) -> TestItem | None:
    """The test written for the line: the first new one that failed first, else the first."""
    if not found:
        return None
    red = [strip_param(i) for i in red_ids]
    by_id = {t.id: t for t in found}
    chosen = next((by_id[i] for i in red if i in by_id), found[0])
    return replace(chosen, n=1)


# ---------------------------------------------------------------- scoring


def score(answer: Answer | str | None, k: Key) -> Score | None:
    """A match when the check fails on its assertion with the change undone.

    `answer` is the confirm: only "yes" is scored. A check that still passes cannot
    tell done from not done; one that cannot run needs the new code to run at all.
    Both are misses.
    """
    if answer != "yes" or len(k.tests) != 1:
        return None
    result = k.tests[0].result
    matched = result == "fails_on_assertion"
    return Score(
        result="match" if matched else "miss",
        outcome_kind="common" if matched else "uncommon",
        catch=False,
        unscored_reason=None,
    )


def finding(k: Key) -> tuple:
    return tuple(t for t in k.tests if t.result in ("still_passes", "cannot_run"))


# ---------------------------------------------------------------- replies


def clean_line(text: str) -> str:
    """One line, inner whitespace collapsed, a leading "check:" dropped, cut."""
    words = " ".join((text or "").split())
    match = _MARKER.match(words)
    return (match.group(1) if match else words)[:MAX_LINE_CHARS]


def line_of_reply(text: str) -> str | None:
    """The line in a chat reply, or None when the reply is not one.

    A chat reply to the Brief must start with "check:". The question is printed at
    a turn end, which is also where the agent asks its own questions, so a plain
    reply is the person talking to the agent, not their check.
    """
    words = " ".join((text or "").split())
    match = _MARKER.match(words)
    return (clean_line(match.group(1)) or None) if match else None


def is_dont_know(text: str) -> bool:
    words = " ".join((text or "").replace("’", "'").strip().lower().split())
    return words.rstrip(".") in _DONT_KNOW


def reply_words(n: int = 0) -> tuple[str, ...]:
    """The confirm's words. The line itself is free text."""
    del n
    return ("yes", "no")


def parse_reply(text: str, n: int = 0) -> Reply | None:
    """The confirm reply: yes or no. Anything else is not a reply."""
    del n
    words = " ".join((text or "").strip().lower().split()).rstrip(".!")
    value = _CONFIRM.get(words)
    return Reply(value, None) if value else None  # type: ignore[arg-type]


def name_of(test_id: str) -> str:
    return test_id.rsplit("::", 1)[-1]
