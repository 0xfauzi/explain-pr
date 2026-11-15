"""Every path Firsthand uses. No other module builds a path under a home folder.

The environment is read on every call and never cached, so a test can change it.
Only `ensure_private_dirs` and `write_private` create anything.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path

_SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
_SOCKET_MAX = 96


def _checked(value: str) -> str:
    """Guard against a path built from an id that came from outside."""
    if not isinstance(value, str) or not _SAFE_ID.match(value) or value.startswith("."):
        raise ValueError(f"not a safe id for a file name: {value!r}")
    return value


def user_home() -> Path:
    env = os.environ.get("HOME")
    return Path(env) if env else Path.home()


def home() -> Path:
    env = os.environ.get("FIRSTHAND_HOME")
    return Path(env) if env else user_home() / ".firsthand"


def config_home() -> Path:
    env = os.environ.get("FIRSTHAND_CONFIG_HOME")
    if env:
        return Path(env)
    if os.environ.get("FIRSTHAND_HOME"):
        return home() / "dotconfig"
    return user_home() / ".config" / "firsthand"


def claude_dir() -> Path:
    env = os.environ.get("FIRSTHAND_CLAUDE_DIR")
    return Path(env) if env else user_home() / ".claude"


def record_dir() -> Path:
    return home() / "record"


def run_dir() -> Path:
    return home() / "run"


def cache_dir() -> Path:
    return home() / "cache"


def engine_dir(version: str) -> Path:
    return home() / "engine" / _checked(version)


def spool_file() -> Path:
    return run_dir() / "spool.jsonl"


def spool_offset_file() -> Path:
    return run_dir() / "spool.offset"


def daemon_lock_file() -> Path:
    return run_dir() / "daemon.lock"


def daemon_info_file() -> Path:
    return run_dir() / "daemon.json"


def daemon_log_file() -> Path:
    return run_dir() / "daemon.log"


def hook_log_file() -> Path:
    return run_dir() / "hook.log"


def control_socket() -> Path:
    """run/daemon.sock, or a short path under the temp folder when that is too long.

    A Unix socket path is limited to about 100 bytes. Both the daemon and its
    clients compute the same fallback from the run folder. The fallback folder is
    /tmp when it exists, not TMPDIR: a daemon started by an agent's hook and a CLI
    in the person's own terminal can have different TMPDIR values, and a long
    TMPDIR would make the fallback too long as well.
    """
    primary = run_dir() / "daemon.sock"
    if len(os.fsencode(str(primary))) <= _SOCKET_MAX:
        return primary
    digest = hashlib.sha256(str(run_dir()).encode()).hexdigest()[:8]
    folder = Path("/tmp") if Path("/tmp").is_dir() else Path(tempfile.gettempdir())
    return folder / f"fh-{os.getuid()}-{digest}" / "d.sock"


def state_file() -> Path:
    return run_dir() / "state.json"


def out_dir() -> Path:
    return run_dir() / "out"


def reply_file(event_id: str) -> Path:
    return out_dir() / f"{_checked(event_id)}.json"


def keys_dir() -> Path:
    return run_dir() / "keys"


def key_file(moment_id: str) -> Path:
    return keys_dir() / f"{_checked(moment_id)}.json"


def scratch_root() -> Path:
    return run_dir() / "scratch"


def scratch_dir(check_id: str) -> Path:
    return scratch_root() / _checked(check_id)


def index_dir() -> Path:
    return run_dir() / "index"


def snapshot_store(project_id: str) -> Path:
    return cache_dir() / "snapshots" / f"{_checked(project_id)}.git"


def port_file() -> Path:
    return config_home() / "port"


def backups_dir() -> Path:
    return config_home() / "backups"


def install_manifest() -> Path:
    return config_home() / "install.json"


def room_sessions_file() -> Path:
    return config_home() / "room-sessions.json"


def claude_settings() -> Path:
    return claude_dir() / "settings.json"


def claude_skill_file() -> Path:
    return claude_dir() / "skills" / "firsthand" / "SKILL.md"


def _private_dir(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path, 0o700)


def ensure_private_dirs() -> None:
    """Create home, run, out, keys, scratch, index, cache and config_home, mode 0700."""
    for path in (
        home(),
        run_dir(),
        out_dir(),
        keys_dir(),
        scratch_root(),
        index_dir(),
        cache_dir(),
        config_home(),
    ):
        _private_dir(path)


def write_private(path: Path, data: bytes) -> None:
    """Write to <path>.tmp with mode 0600, then replace <path> in one step."""
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)
