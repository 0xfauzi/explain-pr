"""The generic adapter: one run of the test command per changed test file, by exit code."""

from __future__ import annotations

import shlex
from collections.abc import Sequence
from pathlib import PurePosixPath

from firsthand import gitwatch
from firsthand.model import FileChange, TestItem, TestResult

MAX_FILES = 4


def test_files(changes: Sequence[FileChange]) -> tuple[TestItem, ...]:
    """One item per added or modified test file, at most four."""
    items = []
    for change in changes:
        if change.status not in ("A", "M") or not gitwatch.is_test_path(change.path):
            continue
        items.append(
            TestItem(
                n=len(items) + 1,
                id=change.path,
                name=PurePosixPath(change.path).name,
                path=change.path,
                line=1,
                status="new" if change.status == "A" else "edited",
                assert_lines=(),
                assert_line=None,
                assert_text=None,
            )
        )
        if len(items) == MAX_FILES:
            break
    return tuple(items)


def argv(test_command: str, test_file: str) -> list[str]:
    return [*shlex.split(test_command), test_file]


def classify(exit_code: int | None) -> TestResult:
    return "still_passes" if exit_code == 0 else "does_not_pass"
