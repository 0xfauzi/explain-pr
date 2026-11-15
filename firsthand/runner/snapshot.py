"""Snapshots of a project's tree, kept in a bare store outside the project.

A snapshot is a git tree written into ~/.firsthand/cache/snapshots/<id>.git, with
the project's own object folder as an alternate for reading. No method writes to
the project: not the working tree, the index, refs, .git/objects (not even an
mtime) or .git/worktrees. No project-configured command runs: content filters
(clean, smudge, process, as Git LFS sets up) and core.fsmonitor are turned off for
every git command here.
"""

from __future__ import annotations

import os
import secrets
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

from firsthand import gitwatch, paths
from firsthand.model import FileChange, FirsthandError

MAX_READ_BYTES = 1_000_000


class SnapshotError(FirsthandError):
    code = "snapshot"


def _base_env() -> dict[str, str]:
    env = dict(os.environ)
    for name in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    ):
        env.pop(name, None)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def _filter_drivers(project_root: Path) -> list[str]:
    """Names of the filter drivers configured for the project (local, global, system)."""
    try:
        done = subprocess.run(
            ["git", "config", "--null", "--name-only", "--get-regexp", r"^filter\."],
            cwd=project_root,
            env=_base_env(),
            capture_output=True,
            check=False,
        )
    except OSError:
        return []
    names: list[str] = []
    for key in done.stdout.decode("utf-8", errors="replace").split("\0"):
        driver = key[len("filter.") : key.rfind(".")] if key.count(".") >= 2 else ""
        if driver and driver not in names:
            names.append(driver)
    return names


def _no_commands(drivers: list[str]) -> dict[str, str]:
    """GIT_CONFIG_* variables that stop git running any project-configured command."""
    pairs = [("core.fsmonitor", "false")]
    for name in drivers:
        for part in ("clean", "smudge", "process"):
            pairs.append((f"filter.{name}.{part}", ""))
        pairs.append((f"filter.{name}.required", "false"))
    env = {"GIT_CONFIG_COUNT": str(len(pairs))}
    for i, (k, v) in enumerate(pairs):
        env[f"GIT_CONFIG_KEY_{i}"] = k
        env[f"GIT_CONFIG_VALUE_{i}"] = v
    return env


def _run(args: list[str], *, env: Mapping[str, str], cwd: Path | None = None) -> bytes:
    try:
        done = subprocess.run(
            ["git", *args], cwd=cwd, env=dict(env), capture_output=True, check=False
        )
    except OSError as exc:
        raise SnapshotError(f"git could not start: {exc}") from exc
    if done.returncode != 0:
        detail = done.stderr.decode(errors="replace").strip()
        raise SnapshotError(f"git {args[0]} failed: {detail}")
    return done.stdout


def _private_temp(directory: Path, suffix: str = "") -> Path:
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    return directory / f"{secrets.token_hex(8)}{suffix}"


class SnapshotStore:
    def __init__(self, project_root: Path, project_id: str) -> None:
        self.project_root = Path(project_root)
        self.project_id = project_id
        self.path = paths.snapshot_store(project_id)
        try:
            self._git_dir, self._objects = gitwatch.git_dirs(self.project_root)
        except FirsthandError as exc:
            raise SnapshotError(exc.message) from exc
        self._no_commands = _no_commands(_filter_drivers(self.project_root))
        if not (self.path / "objects").is_dir():
            self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            _run(["init", "-q", "--bare", str(self.path)], env=_base_env())

    def _store_env(self, **extra: str) -> dict[str, str]:
        env = _base_env()
        env.update(self._no_commands)
        env["GIT_DIR"] = str(self.path)
        env["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(self._objects)
        env.update(extra)
        return env

    def take(self) -> str:
        """The tree hash of the project as it stands, ignored files left out."""
        index = _private_temp(paths.index_dir(), ".index")
        source = self._git_dir / "index"
        try:
            if source.is_file():
                # copy2 keeps the index's mtime. git trusts an entry's stat data
                # only when the file is older than the index; a copy with a new
                # mtime would hide a same-size edit made in the second of the
                # last "git add" (git's racy-clean check).
                shutil.copy2(source, index)
            else:
                index.write_bytes(b"")
            if index.stat().st_size == 0:
                index.unlink()  # git treats a missing index as empty, not an empty file
            env = _base_env()
            env.update(self._no_commands)
            env["GIT_INDEX_FILE"] = str(index)
            env["GIT_OBJECT_DIRECTORY"] = str(self.path / "objects")
            # No alternate here: with the project's objects visible, git "freshens"
            # (touches) a blob it finds there. Blobs the copied index names stay in
            # the project's store, so the tree is written with --missing-ok and read
            # later with the alternate.
            _run(["add", "-A"], env=env, cwd=self.project_root)
            tree = (
                _run(["write-tree", "--missing-ok"], env=env, cwd=self.project_root)
                .decode()
                .strip()
            )
        finally:
            for leftover in (index, index.with_name(index.name + ".lock")):
                leftover.unlink(missing_ok=True)
        return tree

    def diff(self, base: str, head: str) -> tuple[FileChange, ...]:
        """Changes from base to head, sorted by path, with no rename detection."""
        out = _run(
            ["diff-tree", "-r", "-z", "--no-renames", "--name-status", base, head],
            env=self._store_env(),
        )
        parts = out.decode("utf-8", errors="surrogateescape").split("\0")
        changes = []
        for i in range(0, len(parts) - 1, 2):
            status, path = parts[i], parts[i + 1]
            letter = status[:1]
            if letter in ("A", "M", "D"):
                changes.append(FileChange(path=path, status=letter))  # type: ignore[arg-type]
            elif letter == "T":
                changes.append(FileChange(path=path, status="M"))
        return tuple(sorted(changes, key=lambda c: c.path))

    def read_bytes(
        self, tree: str, path: str, limit: int | None = None
    ) -> bytes | None:
        """The file's bytes, or None if absent or over `limit` bytes."""
        spec = f"{tree}:{path}"
        env = self._store_env()
        try:
            kind = _run(["cat-file", "-t", spec], env=env).decode().strip()
        except SnapshotError:
            return None
        if kind != "blob":
            return None
        if limit is not None:
            size = int(_run(["cat-file", "-s", spec], env=env).decode().strip())
            if size > limit:
                return None
        return _run(["cat-file", "blob", spec], env=env)

    def read_file(self, tree: str, path: str) -> str | None:
        """The file's text, or None if absent, binary or over 1 MB."""
        data = self.read_bytes(tree, path, MAX_READ_BYTES)
        if data is None or b"\0" in data:
            return None
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def checkout(self, tree: str, dest: Path) -> None:
        """Write the tree's files into dest, which must not exist or be empty."""
        dest = Path(dest)
        if dest.exists() and any(dest.iterdir()):
            raise SnapshotError(f"{dest} is not empty.")
        dest.mkdir(mode=0o700, parents=True, exist_ok=True)
        index = _private_temp(paths.index_dir(), ".index")
        env = self._store_env(GIT_INDEX_FILE=str(index))
        try:
            _run(["read-tree", tree], env=env)
            _run(
                ["--work-tree", str(dest), "checkout-index", "-a", "-f"],
                env=env,
                cwd=dest,
            )
        finally:
            for leftover in (index, index.with_name(index.name + ".lock")):
                leftover.unlink(missing_ok=True)

    def has(self, tree: str) -> bool:
        try:
            kind = (
                _run(["cat-file", "-t", tree], env=self._store_env()).decode().strip()
            )
        except SnapshotError:
            return False
        return kind == "tree"

    def head_tree(self) -> str | None:
        """The tree of the project's HEAD, None with no commit."""
        try:
            out = _run(
                ["rev-parse", "--verify", "-q", "HEAD^{tree}"],
                env={**_base_env(), **self._no_commands},
                cwd=self.project_root,
            )
        except SnapshotError:
            return None
        return out.decode().strip() or None
