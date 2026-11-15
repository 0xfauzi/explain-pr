"""Test support for Firsthand: a temporary home for every test, and small git helpers.

Nothing under the real home folder is read or written by a test that extends
TempHome.
"""

from __future__ import annotations

import atexit
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Mapping
from pathlib import Path

from firsthand import paths

_REMOVED = (
    "FIRSTHAND_CONFIG_HOME",
    "FIRSTHAND_CLAUDE_DIR",
    "CLAUDE_CONFIG_DIR",
    "XDG_CONFIG_HOME",
    "VIRTUAL_ENV",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
)

_IDENTITY = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


class TempHome(unittest.TestCase):
    """Base class for every Firsthand test. Nothing under the real home is read or written."""

    tmp: Path
    home: Path
    fh: Path

    def setUp(self) -> None:
        super().setUp()
        saved = dict(os.environ)

        def restore() -> None:
            os.environ.clear()
            os.environ.update(saved)

        self.addCleanup(restore)
        self.tmp = Path(tempfile.mkdtemp(prefix="fh-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.home = self.tmp / "home"
        self.fh = self.home / ".firsthand"
        self.home.mkdir()
        os.environ["HOME"] = str(self.home)
        os.environ["FIRSTHAND_HOME"] = str(self.fh)
        os.environ["LEARNING_HOME"] = str(self.home / ".learning-while-building")
        for name in _REMOVED:
            os.environ.pop(name, None)
        os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
        os.environ["GIT_CONFIG_SYSTEM"] = os.devnull
        os.environ["FIRSTHAND_NO_DAEMON"] = "1"
        for where in (paths.home(), paths.config_home(), paths.claude_dir()):
            self.assertTrue(
                where.is_relative_to(self.tmp),
                f"{where} is outside the temporary folder",
            )


def child_env() -> dict[str, str]:
    """os.environ as TempHome set it, for subprocess calls."""
    return dict(os.environ)


def git(cwd: Path, *args: str) -> str:
    """Run git with a fixed identity. Returns stdout, raises on failure."""
    env = {**os.environ, **_IDENTITY}
    done = subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def write_files(root: Path, files: Mapping[str, str | None]) -> None:
    """Write each file under root. None deletes the file."""
    for rel, text in files.items():
        target = root / rel
        if text is None:
            if target.exists():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def make_repo(root: Path, files: Mapping[str, str]) -> None:
    """git init, write the files, and make one commit named "base"."""
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    write_files(root, files)
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", "base")


_VENV: dict[str, Path | str] = {}


def pytest_python() -> Path | None:
    """An interpreter with pytest, in a virtualenv built once per test process.

    The virtualenv lives in its own temporary folder, removed at exit. pip runs with
    HOME pointed inside that folder and no cache, so nothing reaches the real home.
    Returns None when it cannot be built (no network, no venv module); the reason is
    in pytest_python_reason().
    """
    if "python" in _VENV:
        return _VENV["python"]  # type: ignore[return-value]
    if "reason" in _VENV:
        return None
    where = Path(tempfile.mkdtemp(prefix="fh-venv-")).resolve()
    atexit.register(shutil.rmtree, where, True)
    venv = where / "venv"
    env = {
        **os.environ,
        "HOME": str(where),
        "XDG_CACHE_HOME": str(where / "cache"),
        "XDG_CONFIG_HOME": str(where / "config"),
        "PIP_NO_CACHE_DIR": "1",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
    }
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv)],
            env=env,
            check=True,
            capture_output=True,
            timeout=120,
        )
        subprocess.run(
            [str(venv / "bin" / "python"), "-m", "pip", "install", "-q", "pytest"],
            env=env,
            check=True,
            capture_output=True,
            timeout=300,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        _VENV["reason"] = f"could not build a virtualenv with pytest: {exc}"
        return None
    _VENV["python"] = venv / "bin" / "python"
    return _VENV["python"]  # type: ignore[return-value]


def pytest_python_reason() -> str:
    return str(_VENV.get("reason", "pytest virtualenv not built"))


def repo_fingerprint(root: Path) -> str:
    """sha256 over the working tree, every file under .git, the status and the object count."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    # --no-optional-locks: status must not refresh the index, or the fingerprint
    # itself would change the files it hashes.
    digest.update(git(root, "--no-optional-locks", "status", "--porcelain=v2").encode())
    digest.update(git(root, "count-objects", "-v").encode())
    return digest.hexdigest()
