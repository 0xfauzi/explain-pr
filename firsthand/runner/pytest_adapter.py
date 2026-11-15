"""The pytest adapter: list tests with ast, build argv, read junit XML.

pytest is never imported here. It runs inside the project's interpreter, in a
scratch copy.
"""

from __future__ import annotations

import ast
import re
import subprocess
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path, PurePosixPath

from firsthand.model import TestItem, TestResult

MAX_ASSERT_TEXT = 200
_PARAM_SUFFIX = re.compile(r"\[.*\]$")
_LINE_AT_END = re.compile(r"^(?P<path>.*?):(?P<line>\d+): (?P<kind>[^\s].*)$")
_ASSERT_KINDS = ("AssertionError", "Failed")
# The junit message attribute of an assertion failure: "assert x == y" for a bare
# assert, "AssertionError: ..." with a message, "Failed: ..." from pytest.raises.
_ASSERT_MESSAGE = re.compile(r"^(assert\b|AssertionError\b|Failed:)")

Outcome = tuple[str, int | None]


def _is_test_func(node: ast.AST) -> bool:
    return isinstance(
        node, ast.FunctionDef | ast.AsyncFunctionDef
    ) and node.name.startswith("test_")


def _base_name(base: ast.expr) -> str:
    if isinstance(base, ast.Attribute):
        return base.attr
    return base.id if isinstance(base, ast.Name) else ""


def _is_test_class(node: ast.AST) -> bool:
    """A Test* class, or a unittest.TestCase subclass, which pytest collects by any name."""
    if not isinstance(node, ast.ClassDef):
        return False
    if node.name.startswith("Test"):
        return True
    return any(_base_name(b).endswith("TestCase") for b in node.bases)


def _functions(tree: ast.Module) -> list[tuple[str, str, ast.AST]]:
    """(node id suffix, name, node) for every collectable test, in file order."""
    found = []
    for node in tree.body:
        if _is_test_func(node):
            found.append((node.name, node.name, node))  # type: ignore[attr-defined]
        elif _is_test_class(node):
            assert isinstance(node, ast.ClassDef)
            for child in node.body:
                if _is_test_func(child):
                    name = child.name  # type: ignore[attr-defined]
                    found.append((f"{node.name}::{name}", name, child))
    return found


def _asserts(node: ast.AST) -> list[ast.Assert]:
    return sorted(
        (n for n in ast.walk(node) if isinstance(n, ast.Assert)), key=lambda n: n.lineno
    )


def _one_line(source_lines: list[str], line: int) -> str | None:
    if not 1 <= line <= len(source_lines):
        return None
    text = " ".join(source_lines[line - 1].split())
    return text[:MAX_ASSERT_TEXT] or None


def _parse(source: str) -> ast.Module | None:
    try:
        return ast.parse(source)
    except (SyntaxError, ValueError):
        return None


def _items(tree: ast.Module, source: str, path: str) -> list[tuple[TestItem, ast.AST]]:
    lines = source.splitlines()
    out = []
    for suffix, name, node in _functions(tree):
        asserts = _asserts(node)
        assert_lines = tuple(a.lineno for a in asserts)
        last = assert_lines[-1] if assert_lines else None
        item = TestItem(
            n=0,
            id=f"{path}::{suffix}",
            name=name,
            path=path,
            line=node.lineno,  # type: ignore[attr-defined]
            status="new",
            assert_lines=assert_lines,
            assert_line=last,
            assert_text=_one_line(lines, last) if last is not None else None,
        )
        out.append((item, node))
    return out


def list_tests(source: str, path: str) -> tuple[TestItem, ...]:
    """Module-level test functions and test methods of module-level test classes."""
    tree = _parse(source)
    if tree is None:
        return ()
    return tuple(item for item, _ in _items(tree, source, path))


def changed_tests(
    base_source: str | None, head_source: str, path: str
) -> tuple[TestItem, ...]:
    """New tests first, then edited ones, each in file order. Unchanged tests are left out."""
    head_tree = _parse(head_source)
    if head_tree is None:
        return ()
    base_nodes: dict[str, str] = {}
    if base_source is not None:
        base_tree = _parse(base_source)
        if base_tree is not None:
            for item, node in _items(base_tree, base_source, path):
                base_nodes[item.id] = ast.dump(node)
    new, edited = [], []
    for item, node in _items(head_tree, head_source, path):
        if item.id not in base_nodes:
            new.append(item)
        elif base_nodes[item.id] != ast.dump(node):
            edited.append(_with_status(item, "edited"))
    return tuple(new + edited)


def test_dumps(source: str | None, path: str) -> set[tuple[str, str]]:
    """(id suffix, ast dump) of each test: how a moved test is told from a new one."""
    tree = _parse(source) if source is not None else None
    if tree is None:
        return set()
    return {
        (item.id.split("::", 1)[1], ast.dump(node))
        for item, node in _items(tree, source or "", path)
    }


def _with_status(item: TestItem, status: str) -> TestItem:
    return replace(item, status=status)  # type: ignore[arg-type]


def argv(python: Path, ids: Sequence[str], junit: Path) -> list[str]:
    """One pytest run. All ids must be in one file.

    The options after the ids override the project's addopts, which pytest reads
    first: every listed test runs (no -x or --maxfail stop), and the failure text
    in the junit file has the long form the reader parses (no --tb=short).
    """
    return [
        str(python),
        "-m",
        "pytest",
        *ids,
        "-q",
        "-p",
        "no:cacheprovider",
        "--maxfail=0",
        "--tb=long",
        f"--junitxml={junit}",
    ]


def has_pytest(python: Path, env: Mapping[str, str], cwd: Path) -> bool:
    try:
        done = subprocess.run(
            [str(python), "-c", "import pytest"],
            cwd=cwd,
            env=dict(env),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=30,
            start_new_session=True,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return done.returncode == 0


# ------------------------------------------------------------------ junit


def _split_id(test_id: str) -> tuple[str, str | None, str]:
    """(file path, class name or None, function name)."""
    parts = test_id.split("::")
    path = parts[0]
    if len(parts) >= 3:
        return path, parts[-2], parts[-1]
    return path, None, parts[-1]


def _belongs(case: ET.Element, test_id: str) -> bool:
    path, cls, func = _split_id(test_id)
    name = _PARAM_SUFFIX.sub("", case.get("name", ""))
    if name != func:
        return False
    last = case.get("classname", "").split(".")[-1]
    expected = cls if cls is not None else PurePosixPath(path).stem
    return last == expected


def _message_is_assert(element: ET.Element) -> bool:
    return bool(_ASSERT_MESSAGE.match((element.get("message") or "").strip()))


def _failure_outcome(element: ET.Element, path: str) -> Outcome:
    text = element.text or ""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ("assert" if _message_is_assert(element) else "other", None)
    last = lines[-1].strip()
    kind = last.rsplit(": ", 1)[-1] if ": " in last else last
    if kind not in _ASSERT_KINDS and _message_is_assert(element):
        kind = "AssertionError"
    line_no: int | None = None
    match = _LINE_AT_END.match(last)
    if match and (
        match.group("path") == path
        or match.group("path").endswith("/" + path)
        or path.endswith(match.group("path"))
    ):
        line_no = int(match.group("line"))
    return ("assert" if kind in _ASSERT_KINDS else "other", line_no)


def _case_outcome(case: ET.Element, path: str) -> Outcome:
    error = case.find("error")
    if error is not None:
        return ("other", _failure_outcome(error, path)[1])
    failure = case.find("failure")
    if failure is not None:
        return _failure_outcome(failure, path)
    if case.find("skipped") is not None:
        return ("skipped", None)
    return ("passed", None)


def _combine(outcomes: list[Outcome]) -> Outcome:
    """A parametrized test: passed only if all passed, assert if every non-pass is assert."""
    if not outcomes:
        return ("missing", None)
    if len(outcomes) == 1:
        return outcomes[0]
    bad = [o for o in outcomes if o[0] != "passed"]
    if not bad:
        return ("passed", None)
    line = next((o[1] for o in bad if o[1] is not None), None)
    if all(o[0] == "assert" for o in bad):
        return ("assert", line)
    return ("other", line)


def _is_collection_failure(case: ET.Element) -> bool:
    error = case.find("error")
    return error is not None and "collection failure" in (error.get("message") or "")


def read_junit(junit: Path, ids: Sequence[str]) -> dict[str, tuple[str, int | None]]:
    """For each id: passed, assert, other, skipped or missing, with a line where one was read."""
    try:
        root = ET.parse(junit).getroot()
    except (OSError, ET.ParseError):
        return {i: ("missing", None) for i in ids}
    cases = list(root.iter("testcase"))
    if any(_is_collection_failure(c) for c in cases):
        return {i: ("other", None) for i in ids}
    out: dict[str, tuple[str, int | None]] = {}
    for test_id in ids:
        path = _split_id(test_id)[0]
        mine = [_case_outcome(c, path) for c in cases if _belongs(c, test_id)]
        out[test_id] = _combine(mine)
    return out


def classify(outcome: str) -> TestResult:
    if outcome == "passed":
        return "still_passes"
    if outcome == "assert":
        return "fails_on_assertion"
    return "cannot_run"
