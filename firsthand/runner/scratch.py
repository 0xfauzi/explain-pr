"""Scratch copies of a snapshot, a scrubbed environment, and timed runs.

A scratch copy lives under ~/.firsthand/run/scratch/<check-id>/ (mode 0700). The
project itself is never written. Runs get only the environment `scrubbed_env`
builds, so no token or credential from the daemon's environment reaches a test.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import threading
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from firsthand import paths
from firsthand.model import FileChange
from firsthand.runner.snapshot import SnapshotError, SnapshotStore

STRIPPED = (
    ".claude",
    ".mcp.json",
    ".cursor",
    ".codex",
    ".gemini",
    "AGENTS.md",
    "CLAUDE.md",
    ".vscode",
    ".idea",
    ".devcontainer",
)
ENV_ALLOW = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ")

_POLL_S = 0.02
_PROBE_TIMEOUT_S = 30.0
_MODULE_PART = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

_PROBE = r"""
import importlib.util, json, sys
out = {}
for name in json.loads(sys.argv[1]):
    try:
        spec = importlib.util.find_spec(name)
    except BaseException:
        spec = None
    out[name] = getattr(spec, "origin", None) if spec else None
print(json.dumps(out))
"""


@dataclass(frozen=True)
class RunResult:
    argv: tuple[str, ...]
    exit: int | None
    timed_out: bool
    duration_s: float
    output_sha256: str


def _make_writable(path: str) -> None:
    """chmod follows links, so a link is never touched: stay inside the folder."""
    if os.path.islink(path):
        return
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass


def remove_tree(root: Path) -> bool:
    """Delete a folder even when a test left read-only folders in it. True if gone."""
    if not os.path.lexists(root):
        return True
    if os.path.islink(root):
        os.unlink(root)
        return not os.path.lexists(root)
    _make_writable(str(root))
    for dirpath, dirnames, _ in os.walk(root):
        for name in dirnames:
            _make_writable(os.path.join(dirpath, name))
    shutil.rmtree(root, ignore_errors=True)
    return not os.path.lexists(root)


def _kill_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


class Scratch:
    root: Path
    tree: Path
    out: Path

    def __init__(self, store: SnapshotStore, tree: str, check_id: str) -> None:
        self.store = store
        self.root = paths.scratch_dir(check_id)
        self.tree = self.root / "tree"
        self.out = self.root / "out"
        self.home = self.root / "home"
        self.tmp = self.root / "tmp"
        try:
            if self.root.exists() and not remove_tree(self.root):
                raise OSError(f"{self.root} could not be removed")
            self.root.mkdir(mode=0o700, parents=True)
            os.chmod(self.root, 0o700)
            for folder in (self.home, self.tmp, self.out):
                folder.mkdir(mode=0o700)
            store.checkout(tree, self.tree)
            for name in STRIPPED:
                self._remove(self.tree / name)
        except OSError as exc:
            self.close()
            raise SnapshotError(f"scratch copy failed: {exc}") from exc
        except SnapshotError:
            self.close()
            raise

    @staticmethod
    def _remove(target: Path) -> None:
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)

    def undo(self, base_tree: str, changes: Sequence[FileChange]) -> tuple[str, ...]:
        """Put each changed file back as it was at the base. Returns the paths touched."""
        touched = []
        for change in changes:
            target = self.tree / change.path
            if not target.resolve().is_relative_to(self.tree.resolve()):
                continue
            if change.status == "A":
                if target.exists() or target.is_symlink():
                    self._remove(target)
                touched.append(change.path)
                continue
            data = self.store.read_bytes(base_tree, change.path)
            if data is None:
                raise SnapshotError(f"{change.path} is missing from the base snapshot.")
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            touched.append(change.path)
        return tuple(touched)

    def run(
        self,
        argv: Sequence[str],
        *,
        env: Mapping[str, str],
        timeout_s: float,
        cancel: threading.Event | None = None,
    ) -> RunResult:
        """Run in the scratch tree as a new process group. Never raises for a failing command."""
        start = time.monotonic()
        deadline = start + max(0.0, timeout_s)
        log = self.root / f"run-{os.getpid()}-{threading.get_ident()}.log"
        exit_code: int | None = None
        timed_out = False
        with open(log, "wb") as sink:
            try:
                proc = subprocess.Popen(
                    list(argv),
                    cwd=self.tree,
                    env=dict(env),
                    stdin=subprocess.DEVNULL,
                    stdout=sink,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            except OSError as exc:
                sink.write(str(exc).encode())
                proc = None
            if proc is not None:
                exit_code, timed_out = self._wait(proc, deadline, cancel)
        digest = hashlib.sha256(log.read_bytes()).hexdigest()
        log.unlink(missing_ok=True)
        return RunResult(
            argv=tuple(argv),
            exit=exit_code if proc is not None else 127,
            timed_out=timed_out,
            duration_s=round(time.monotonic() - start, 3),
            output_sha256=digest,
        )

    @staticmethod
    def _wait(
        proc: subprocess.Popen, deadline: float, cancel: threading.Event | None
    ) -> tuple[int | None, bool]:
        while True:
            try:
                code = proc.wait(timeout=_POLL_S)
            except subprocess.TimeoutExpired:
                code = None
            if code is not None:
                _kill_group(proc)  # a child left running in the group goes too
                return code, False
            stopped = cancel is not None and cancel.is_set()
            late = time.monotonic() >= deadline
            if stopped or late:
                _kill_group(proc)
                proc.wait()
                return None, late and not stopped

    def close(self) -> None:
        """Delete the scratch folder. Safe to call twice."""
        remove_tree(self.root)


def _venv_of(python: Path) -> Path | None:
    for candidate in (
        python.parent.parent,
        Path(os.path.abspath(python)).parent.parent,
    ):
        if (candidate / "pyvenv.cfg").is_file():
            return candidate
    return None


def scrubbed_env(
    scratch: Scratch, *, python: Path | None, extra: Iterable[tuple[str, str]] = ()
) -> dict[str, str]:
    """Only the allowed names, the scratch homes, PYTHONPATH and the declared extras."""
    env = {name: os.environ[name] for name in ENV_ALLOW if name in os.environ}
    env["HOME"] = str(scratch.home)
    env["TMPDIR"] = str(scratch.tmp)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    src = scratch.tree / "src"
    parts = [str(src)] if src.is_dir() else []
    parts.append(str(scratch.tree))
    env["PYTHONPATH"] = os.pathsep.join(parts)
    if python is not None:
        venv = _venv_of(python)
        if venv is not None:
            env["VIRTUAL_ENV"] = str(venv)
    for name, value in extra:
        env[name] = value
    return env


def find_python(project_root: Path, venv_hint: str | None) -> Path | None:
    candidates = []
    if venv_hint:
        candidates.append(Path(venv_hint) / "bin" / "python")
    candidates += [
        project_root / ".venv" / "bin" / "python",
        project_root / "venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    found = shutil.which("python3")
    return Path(found) if found else None


def _module_name(path: str) -> str | None:
    parts = list(Path(path).with_suffix("").parts)
    if parts and parts[0] == "src" and len(parts) > 1:
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts or not all(_MODULE_PART.match(p) for p in parts):
        return None
    return ".".join(parts)


def source_wins(
    python: Path,
    scratch: Scratch,
    env: Mapping[str, str],
    changes: Sequence[FileChange],
    project_root: Path,
) -> bool:
    """False when any changed module would load from the project instead of the scratch copy."""
    names = sorted(
        {
            name
            for change in changes
            if change.path.endswith(".py")
            for name in [_module_name(change.path)]
            if name is not None
        }
    )
    if not names:
        return True
    try:
        done = subprocess.run(
            [str(python), "-c", _PROBE, json.dumps(names)],
            cwd=scratch.tree,
            env=dict(env),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=_PROBE_TIMEOUT_S,
            start_new_session=True,
            check=False,
        )
        origins = json.loads(done.stdout.strip().splitlines()[-1])
    except (OSError, subprocess.TimeoutExpired, ValueError, IndexError):
        return True  # the probe could not tell; the control run still has to pass
    root = Path(project_root).resolve()
    for origin in origins.values():
        if (
            isinstance(origin, str)
            and os.path.isabs(origin)
            and Path(origin).resolve().is_relative_to(root)
        ):
            return False
    return True


def sweep() -> int:
    """Remove every folder under the scratch root. Returns how many were removed."""
    root = paths.scratch_root()
    if not root.is_dir():
        return 0
    count = 0
    for entry in root.iterdir():
        if entry.is_dir() and not entry.is_symlink():
            if remove_tree(entry):
                count += 1
        else:
            entry.unlink(missing_ok=True)
    return count
