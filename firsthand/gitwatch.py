"""Read-only facts about the project's git repo, and path and command tests.

No function here runs a git command that can write to the project.
"""

from __future__ import annotations

import hashlib
import os
import re
import shlex
import subprocess
from collections.abc import Iterable, Sequence
from functools import lru_cache
from pathlib import Path, PurePosixPath

from firsthand.model import FileChange, FirsthandError, HeadState

_WRAPPERS = (
    ("uv", "run"),
    ("poetry", "run"),
    ("pipenv", "run"),
    ("hatch", "run"),
    ("python", "-m"),
    ("python3", "-m"),
)
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_CD_PREFIX = re.compile(r"^\s*cd\s+(?:\"[^\"]*\"|'[^']*'|\S+)\s*&&\s*")


class GitError(FirsthandError):
    code = "git"


def _git(cwd: Path | str, *args: str) -> str | None:
    env = dict(os.environ)
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    # Reads must not refresh the project's index.
    env["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        done = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except (OSError, ValueError):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def project_root(cwd: str | Path) -> Path | None:
    """The main worktree's top level, so every worktree of a repo shares one root."""
    if not Path(cwd).is_dir():
        return None
    top = _git(cwd, "rev-parse", "--show-toplevel")
    if not top:
        return None
    common = _git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common:
        common_dir = Path(common).resolve()
        if common_dir.name == ".git":
            return common_dir.parent
    return Path(top).resolve()


def project_id(root: Path) -> str | None:
    """'prj_' and the first 12 hex of sha256 of the root commit hash. None with no commit."""
    roots = _git(root, "rev-list", "--max-parents=0", "HEAD")
    if not roots:
        return None
    first = min(roots.split())
    return "prj_" + hashlib.sha256(first.encode()).hexdigest()[:12]


def git_dirs(root: Path) -> tuple[Path, Path]:
    """(absolute git dir, absolute objects dir). Raises GitError."""
    git_dir = _git(root, "rev-parse", "--path-format=absolute", "--git-dir")
    objects = _git(root, "rev-parse", "--path-format=absolute", "--git-path", "objects")
    if not git_dir or not objects:
        raise GitError(f"{root} is not a git repo that can be read.")
    return Path(git_dir), Path(objects)


def head(root: Path) -> HeadState:
    commit = _git(root, "rev-parse", "--verify", "-q", "HEAD")
    branch = _git(root, "symbolic-ref", "-q", "--short", "HEAD")
    return HeadState(commit=commit or None, branch=branch or None)


def is_test_path(path: str) -> bool:
    """test_*.py, *_test.py, or any path part equal to "tests"."""
    parts = PurePosixPath(path.replace("\\", "/")).parts
    if not parts:
        return False
    name = parts[-1]
    if name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py")):
        return True
    return "tests" in parts[:-1]


# Path categories (learning.md section 3.5), in order: the first that matches wins.
# "tests" comes from is_test_path and "other" is everything left.
CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "schema",
        (
            "**/migrations/**",
            "**/alembic/**",
            "**/*.sql",
            "**/models.py",
            "**/models/**",
            "**/schema.py",
            "**/schema/**",
        ),
    ),
    (
        "money",
        (
            "**/payments/**",
            "**/billing/**",
            "**/ledger/**",
            "**/*payment*",
            "**/*invoice*",
            "**/*refund*",
        ),
    ),
    ("auth", ("**/auth/**", "**/auth.py", "**/*login*", "**/permissions*")),
    (
        "input",
        (
            "**/api/**",
            "**/routes/**",
            "**/views/**",
            "**/handlers/**",
            "**/endpoints/**",
            "**/forms.py",
            "**/serializers.py",
            "**/validators.py",
        ),
    ),
    ("personal", ("**/users/**", "**/*profile*", "**/*privacy*")),
    ("public", ("**/__init__.py", "**/*.pyi", "**/openapi.*", "**/*.proto")),
    (
        "config",
        (
            "**/*.toml",
            "**/*.ini",
            "**/*.cfg",
            "**/*.yaml",
            "**/*.yml",
            "**/Dockerfile",
            "**/Makefile",
            "**/.github/**",
            "**/infra/**",
            "**/settings.py",
            "**/config.py",
            "**/config/**",
        ),
    ),
)


def category(path: str) -> str:
    """The path category of learning.md section 3.5: tests, schema, money, ... or other."""
    if is_test_path(path):
        return "tests"
    for name, patterns in CATEGORIES:
        if any(glob_match(path, p) for p in patterns):
            return name
    return "other"


@lru_cache(maxsize=256)
def _glob_regex(pattern: str) -> re.Pattern[str]:
    if pattern.endswith("/"):
        pattern = pattern + "**"
    out = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def glob_match(path: str, pattern: str) -> bool:
    """'**' spans folders, '*' and '?' stay inside one part, a trailing '/' matches below."""
    return bool(_glob_regex(pattern).match(path.replace("\\", "/").lstrip("/")))


def first_match(paths: Iterable[str], patterns: Sequence[str]) -> str | None:
    """The first pattern, in the order given, that any path matches."""
    listed = list(paths)
    for pattern in patterns:
        if any(glob_match(p, pattern) for p in listed):
            return pattern
    return None


def split_changes(
    changes: Sequence[FileChange],
) -> tuple[tuple[FileChange, ...], tuple[FileChange, ...]]:
    """(source changes, test changes)."""
    source = tuple(c for c in changes if not is_test_path(c.path))
    tests = tuple(c for c in changes if is_test_path(c.path))
    return source, tests


def _strip_wrappers(words: list[str]) -> list[str]:
    changed = True
    while changed and words:
        changed = False
        while words and _ASSIGN.match(words[0]):
            words = words[1:]
            changed = True
        for first, second in _WRAPPERS:
            if (
                len(words) >= 2
                and os.path.basename(words[0]) == first
                and words[1] == second
            ):
                words = words[2:]
                changed = True
                break
    return words


def runner_token(command: str) -> str | None:
    """The runner's name: 'pytest' for 'cd api && uv run python -m pytest -q'."""
    text = command.strip()
    while True:
        cut = _CD_PREFIX.sub("", text, count=1)
        if cut == text:
            break
        text = cut
    try:
        words = shlex.split(text)
    except ValueError:
        return None
    words = _strip_wrappers(words)
    if not words:
        return None
    return os.path.basename(words[0]) or None


def is_test_run(command: str, test_command: str | None) -> bool:
    if not test_command or not command:
        return False
    token = runner_token(test_command)
    return token is not None and runner_token(command) == token
