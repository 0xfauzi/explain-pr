"""Settings files: one file per setting and one file per project, inside the record.

`ConfigStore` satisfies `model.SettingsStore`. It validates every value against
build-2a-contract.md section 4.5 and raises `EngineError("invalid")` with a
message that names the allowed values.
"""

from __future__ import annotations

import dataclasses
import json
import re
import socket
import threading
import tomllib
from collections.abc import Callable, Mapping
from datetime import date
from pathlib import Path

from firsthand import events, paths
from firsthand.model import DEFAULT_HIGH_STAKES, EngineError, ProjectSettings, Settings

DIALS = ("off", "notes", "standard", "deep")
PROJECT_FORMAT = 1
DEFAULT_PORT = 4127
PYTEST_COMMAND = "pytest -q"

_SAFE_ID = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_PROJECT_KEYS = (
    "test_command",
    "quiet",
    "name",
    "high_stakes_add",
    "high_stakes_remove",
)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _check_dial(key: str, value: object) -> object:
    if value not in DIALS:
        raise EngineError(
            f"{key} must be one of: off, notes, standard, deep.", "invalid"
        )
    return value


def _check_limit(key: str, value: object) -> object:
    if not _is_int(value) or not 1 <= value <= 3:
        raise EngineError(f"{key} must be 1, 2 or 3.", "invalid")
    return value


def _check_bool(key: str, value: object) -> object:
    if not isinstance(value, bool):
        raise EngineError(f"{key} must be true or false.", "invalid")
    return value


def _check_date(key: str, value: object) -> object:
    if value is None:
        return None
    try:
        if not isinstance(value, str) or not _DATE.match(value):
            raise ValueError(value)
        date.fromisoformat(value)
    except ValueError:
        raise EngineError(
            f"{key} must be a date such as 2026-11-14, or null.", "invalid"
        ) from None
    return value


def _check_time_limit(key: str, value: object) -> object:
    if not _is_int(value) or not 30 <= value <= 600:
        raise EngineError(
            f"{key} must be a whole number of seconds from 30 to 600.", "invalid"
        )
    return value


_CHECKS: dict[str, Callable[[str, object], object]] = {
    "dial": _check_dial,
    "dial_before_off": _check_dial,
    "daily_limit": _check_limit,
    "findings_to_agent": _check_bool,
    "work_computer": _check_bool,
    "quiet_today": _check_date,
    "check_time_limit_s": _check_time_limit,
}


def _valid(key: str, value: object) -> object:
    check = _CHECKS.get(key)
    if check is None:
        names = ", ".join(_CHECKS)
        raise EngineError(f"Unknown setting: {key}. Settings are: {names}.", "invalid")
    return check(key, value)


def _dumps(data: Mapping[str, object]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()


def _read(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _str_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _from_file(data: Mapping[str, object], project_id: str) -> ProjectSettings:
    runner = data.get("runner")
    runner = runner if isinstance(runner, Mapping) else {}
    env = runner.get("env")
    env = env if isinstance(env, Mapping) else {}
    command = data.get("test_command")
    name = data.get("name")
    return ProjectSettings(
        id=project_id,
        name=name if isinstance(name, str) and name else project_id,
        roots=_str_tuple(data.get("roots")),
        test_command=command if isinstance(command, str) and command.strip() else None,
        high_stakes=_str_tuple(data.get("high_stakes")),
        quiet=data.get("quiet") is True,
        env=tuple(sorted((str(k), str(v)) for k, v in env.items())),
        carry=_str_tuple(runner.get("carry")),
    )


def _to_file(p: ProjectSettings) -> dict[str, object]:
    return {
        "format": PROJECT_FORMAT,
        "id": p.id,
        "name": p.name,
        "roots": list(p.roots),
        "test_command": p.test_command,
        "high_stakes": list(p.high_stakes),
        "quiet": p.quiet,
        "runner": {"env": dict(p.env), "carry": list(p.carry)},
    }


def _text_value(key: str, value: object, *, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not value.strip():
        raise EngineError(f"{key} must be a non-empty string.", "invalid")
    return value.strip()


class ConfigStore:
    """Reads and writes record/config/<key>.json and record/projects/<id>.json."""

    def __init__(
        self,
        record_dir: Path | None = None,
        commit: Callable[[str], object] | None = None,
    ) -> None:
        self._root = Path(record_dir) if record_dir is not None else paths.record_dir()
        self._commit = commit
        self._lock = threading.RLock()

    def _config_file(self, key: str) -> Path:
        return self._root / "config" / f"{key}.json"

    def _project_file(self, project_id: str) -> Path:
        if not isinstance(project_id, str) or not _SAFE_ID.match(project_id):
            raise EngineError(f"Not a project id: {project_id!r}.", "invalid")
        return self._root / "projects" / f"{project_id}.json"

    def _write(self, path: Path, data: Mapping[str, object], subject: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        paths.write_private(path, _dumps(data))
        if self._commit is not None:
            self._commit(subject)

    def load(self) -> Settings:
        with self._lock:
            values: dict[str, object] = {}
            for key in _CHECKS:
                data = _read(self._config_file(key))
                if data is None or "value" not in data:
                    continue
                try:
                    values[key] = _valid(key, data["value"])
                except EngineError:
                    continue
            return Settings(**values)  # type: ignore[arg-type]

    def set(self, key: str, value: object) -> Settings:
        with self._lock:
            checked = _valid(key, value)
            body = {"key": key, "value": checked, "at": events.now_stamp()}
            self._write(self._config_file(key), body, f"config: {key}")
            return self.load()

    def project(self, project_id: str) -> ProjectSettings | None:
        with self._lock:
            try:
                path = self._project_file(project_id)
            except EngineError:
                return None
            data = _read(path)
            return _from_file(data, project_id) if data is not None else None

    def _save_project(self, p: ProjectSettings) -> ProjectSettings:
        self._write(self._project_file(p.id), _to_file(p), f"project: {p.id}")
        return p

    def ensure_project(self, project_id: str, root: str) -> ProjectSettings:
        with self._lock:
            current = self.project(project_id)
            if current is None:
                fresh = ProjectSettings(
                    id=project_id,
                    name=Path(root).name or project_id,
                    roots=(root,),
                    test_command=detect_test_command(Path(root)),
                    high_stakes=DEFAULT_HIGH_STAKES,
                )
                return self._save_project(fresh)
            if root in current.roots:
                return current
            return self._save_project(_replace(current, roots=(*current.roots, root)))

    def set_project(self, project_id: str, key: str, value: object) -> ProjectSettings:
        with self._lock:
            self._project_file(project_id)
            current = self.project(project_id)
            if current is None:
                raise EngineError(
                    f"No settings for project {project_id}. Run Firsthand in that project first.",
                    "not_found",
                )
            return self._save_project(_changed(current, key, value))


def _replace(p: ProjectSettings, **changes: object) -> ProjectSettings:
    return dataclasses.replace(p, **changes)  # type: ignore[arg-type]


def _changed(p: ProjectSettings, key: str, value: object) -> ProjectSettings:
    if key == "test_command":
        return _replace(p, test_command=_text_value(key, value, allow_none=True))
    if key == "name":
        return _replace(p, name=_text_value(key, value))
    if key == "quiet":
        return _replace(p, quiet=_check_bool(key, value))
    if key == "high_stakes_add":
        glob = _text_value(key, value)
        if glob in p.high_stakes:
            return p
        return _replace(p, high_stakes=(*p.high_stakes, glob))
    if key == "high_stakes_remove":
        glob = _text_value(key, value)
        if glob not in p.high_stakes:
            listed = ", ".join(p.high_stakes) or "none"
            raise EngineError(
                f"{glob} is not marked high stakes. Marked: {listed}.", "invalid"
            )
        return _replace(p, high_stakes=tuple(g for g in p.high_stakes if g != glob))
    names = ", ".join(_PROJECT_KEYS)
    raise EngineError(
        f"Unknown project setting: {key}. Project settings are: {names}.", "invalid"
    )


def _has_pytest_table(pyproject: Path) -> bool:
    try:
        text = pyproject.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return "[tool.pytest.ini_options]" in text
    tool = data.get("tool")
    pytest_table = tool.get("pytest") if isinstance(tool, dict) else None
    return isinstance(pytest_table, dict) and "ini_options" in pytest_table


def detect_test_command(root: Path) -> str | None:
    """ "pytest -q" when the project shows a pytest configuration, else None."""
    root = Path(root)
    if _has_pytest_table(root / "pyproject.toml"):
        return PYTEST_COMMAND
    for name in ("pytest.ini", "tox.ini", "conftest.py"):
        if (root / name).is_file():
            return PYTEST_COMMAND
    return None


def read_port() -> int | None:
    """The Room port from config_home()/port, or None when it is missing or not a port."""
    try:
        text = paths.port_file().read_text(encoding="ascii").strip()
    except (OSError, UnicodeDecodeError):
        return None
    if not text.isdigit():
        return None
    port = int(text)
    return port if 0 <= port <= 65535 else None


def _free(port: int) -> int | None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            return None
        return probe.getsockname()[1]


def choose_port() -> int:
    """A free loopback port, 4127 when it is free, written to paths.port_file()."""
    port = _free(DEFAULT_PORT) or _free(0)
    if port is None:
        raise OSError("no free loopback port")
    paths.ensure_private_dirs()
    paths.write_private(paths.port_file(), f"{port}\n".encode("ascii"))
    return port
