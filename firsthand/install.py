"""Engine install, the settings merge, backups and uninstall.

Nothing here writes outside paths.claude_dir(), paths.config_home() and
paths.home(). Uninstall restores files byte for byte from their backups and
never touches the record.
"""

from __future__ import annotations

import contextlib
import copy
import difflib
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from firsthand import __version__, events, paths
from firsthand.adapters import claude_code
from firsthand.model import FirsthandError

OUR_MARK = " hook claude-code "
INSTALLED_DIR = "installed"


class InstallError(FirsthandError):
    code = "install"


@dataclass(frozen=True)
class PlannedWrite:
    path: Path
    existed: bool
    summary: str
    old: bytes | None
    new: bytes


@dataclass(frozen=True)
class UninstallReport:
    restored: tuple[Path, ...]
    removed: tuple[Path, ...]
    refused: tuple[tuple[Path, str], ...]


def _sha(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def _read_bytes(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _target(path: Path) -> Path:
    """The file a write lands in: a symlink's target, so the link itself stays.

    A dotfiles setup often links ~/.claude/settings.json elsewhere; replacing the
    link with a plain file would silently cut it off.
    """
    return Path(os.path.realpath(path)) if path.is_symlink() else path


def _atomic_write(path: Path, data: bytes, mode: int) -> None:
    path = _target(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def _mode_of(path: Path, default: int) -> int:
    try:
        return path.stat().st_mode & 0o777
    except FileNotFoundError:
        return default


# ---------------------------------------------------------------- engine


def _launcher_text(lib: Path) -> str:
    base = getattr(sys, "_base_executable", None) or sys.executable
    interpreter = os.path.realpath(base)
    return (
        f"#!{interpreter} -IS\n"
        '"""Firsthand launcher. Written by firsthand init."""\n'
        "import sys\n"
        f"sys.path.insert(0, {str(lib)!r})\n"
        "from firsthand.cli import main\n"
        "sys.exit(main())\n"
    )


def launcher_path(version: str = __version__) -> Path:
    return paths.engine_dir(version) / "bin" / "firsthand"


def command() -> str:
    """How to type the firsthand command on this computer.

    "firsthand" when that name is on PATH (a pip install), else the launcher's full
    path: init writes the launcher but puts nothing on PATH.
    """
    if shutil.which("firsthand"):
        return "firsthand"
    text, home = str(launcher_path()), str(paths.user_home()).rstrip("/")
    return "~" + text[len(home) :] if text.startswith(home + "/") else text


def install_engine(version: str) -> Path:
    """Copy the running package to engine/<version>/lib and write the launcher."""
    source = Path(__file__).resolve().parent
    lib = paths.engine_dir(version) / "lib"
    dest = lib / "firsthand"
    paths.ensure_private_dirs()
    if source != dest.resolve():
        staging = lib / ".firsthand.new"
        shutil.rmtree(staging, ignore_errors=True)
        lib.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source, staging, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
        )
        shutil.rmtree(dest, ignore_errors=True)
        os.replace(staging, dest)
    launcher = launcher_path(version)
    _atomic_write(launcher, _launcher_text(lib).encode(), 0o755)
    return launcher


# ---------------------------------------------------------- settings merge


def _parse_settings(settings_text: str | None) -> dict:
    if settings_text is None or not settings_text.strip():
        return {}
    try:
        data = json.loads(settings_text)
    except json.JSONDecodeError as exc:
        raise InstallError(
            f"~/.claude/settings.json is not valid JSON (line {exc.lineno}). "
            "Fix it, then run: firsthand init"
        ) from None
    if not isinstance(data, dict):
        raise InstallError(
            "~/.claude/settings.json is not a JSON object. Fix it, then run: firsthand init"
        )
    return data


def _is_ours(handler: object) -> bool:
    command = handler.get("command") if isinstance(handler, dict) else None
    return isinstance(command, str) and OUR_MARK in command


def _without_ours(groups: list) -> list:
    kept = []
    for group in groups:
        handlers = group.get("hooks") if isinstance(group, dict) else None
        if not isinstance(handlers, list) or not any(_is_ours(h) for h in handlers):
            kept.append(group)
            continue
        rest = [h for h in handlers if not _is_ours(h)]
        if rest:
            kept.append({**group, "hooks": rest})
    return kept


def merge_hooks(settings_text: str | None, fragment: Mapping[str, object]) -> str:
    """The settings text with every Firsthand hook replaced by the fragment's groups."""
    data = _parse_settings(settings_text)
    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError(
            '"hooks" in ~/.claude/settings.json is not an object. Fix it, then run: firsthand init'
        )
    merged: dict[str, object] = {}
    for event_name, groups in hooks.items():
        if not isinstance(groups, list):
            merged[event_name] = groups
            continue
        kept = _without_ours(groups)
        if kept or len(kept) == len(groups):
            merged[event_name] = kept
    new_hooks = fragment.get("hooks", fragment)
    for event_name, groups in dict(new_hooks).items():  # type: ignore[call-overload]
        current = merged.get(event_name)
        if not isinstance(current, list):
            current = []
        merged[event_name] = [*current, *copy.deepcopy(groups)]
    data["hooks"] = merged
    return json.dumps(data, indent=2) + "\n"


# ------------------------------------------------------------- plan, apply


def plan(launcher: Path) -> list[PlannedWrite]:
    """The writes init would make. Writes nothing."""
    skill = paths.claude_skill_file()
    skill_old = _read_bytes(skill)
    skill_summary = "new folder" if not skill.parent.exists() else "updates SKILL.md"
    settings = paths.claude_settings()
    settings_old = _read_bytes(settings)
    try:
        old_text = settings_old.decode("utf-8") if settings_old is not None else None
    except UnicodeDecodeError:
        raise InstallError(
            "~/.claude/settings.json is not UTF-8 text. Fix it, then run: firsthand init"
        ) from None
    settings_new = merge_hooks(
        old_text, claude_code.settings_fragment(launcher)
    ).encode()
    count = len(claude_code.EVENTS)
    return [
        PlannedWrite(
            skill,
            skill_old is not None,
            skill_summary,
            skill_old,
            claude_code.skill_text(launcher).encode(),
        ),
        PlannedWrite(
            settings,
            settings_old is not None,
            f"adds {count} hooks that call {launcher}",
            settings_old,
            settings_new,
        ),
    ]


def _lines(data: bytes | None) -> list[str]:
    if data is None:
        return []
    return data.decode("utf-8", errors="replace").splitlines(keepends=True)


def diff_text(w: PlannedWrite) -> str:
    before = str(w.path) if w.existed else "/dev/null"
    return "".join(
        difflib.unified_diff(_lines(w.old), _lines(w.new), before, str(w.path))
    )


def _read_manifest() -> dict | None:
    try:
        data = json.loads(paths.install_manifest().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _backup_name(path: Path, used: set[str]) -> str:
    name = path.name
    n = 2
    while name in used:
        name = f"{path.name}.{n}"
        n += 1
    used.add(name)
    return name


def _carry_backup(prior: dict, prior_dir: Path, backup: Path, used: set[str]) -> dict:
    """An entry from an earlier install whose file is still as that install left it."""
    name = prior.get("backup")
    if isinstance(name, str):
        used.add(name)
        source = prior_dir / name
        if source.is_file() and source != backup / name:
            paths.write_private(backup / name, source.read_bytes())
    return {
        "existed": prior.get("existed") is True,
        "backup": name if isinstance(name, str) else None,
        "sha256_before": prior.get("sha256_before"),
    }


def _fresh_backup(
    path: Path, current: bytes | None, backup: Path, used: set[str]
) -> dict:
    if current is None:
        return {"existed": False, "backup": None, "sha256_before": None}
    name = _backup_name(path, used)
    paths.write_private(backup / name, current)
    return {"existed": True, "backup": name, "sha256_before": _sha(current)}


def _prior_entries(manifest: dict | None) -> tuple[dict[str, dict], Path | None]:
    if not manifest:
        return {}, None
    entries = {
        f["path"]: f
        for f in manifest.get("files", [])
        if isinstance(f, dict) and isinstance(f.get("path"), str)
    }
    folder = manifest.get("backup")
    return entries, Path(folder) if isinstance(folder, str) else None


def apply(writes: Sequence[PlannedWrite], *, launcher: Path, stamp: str) -> Path:
    """Back up each file, write the new bytes and the manifest. Returns the backup folder."""
    paths.ensure_private_dirs()
    backup = paths.backups_dir() / stamp
    (backup / INSTALLED_DIR).mkdir(mode=0o700, parents=True, exist_ok=True)
    for folder in (paths.backups_dir(), backup, backup / INSTALLED_DIR):
        os.chmod(folder, 0o700)
    prior, prior_dir = _prior_entries(_read_manifest())
    used: set[str] = set()
    entries = []
    for w in writes:
        current = _read_bytes(w.path)
        old = prior.get(str(w.path))
        if (
            old is not None
            and prior_dir is not None
            and _sha(current) == old.get("sha256_after")
        ):
            kept = _carry_backup(old, prior_dir, backup, used)
            kept["created"] = old.get("created") or []
        else:
            kept = _fresh_backup(w.path, current, backup, used)
            kept["created"] = _missing_parents(w.path)
        entries.append({"path": str(w.path), **kept, "sha256_after": _sha(w.new)})
    for w, entry in zip(writes, entries, strict=True):
        written = (
            backup / INSTALLED_DIR / (entry["backup"] or _backup_name(w.path, used))
        )
        paths.write_private(written, w.new)
        entry["installed"] = str(written.relative_to(backup))
        _atomic_write(w.path, w.new, _mode_of(w.path, 0o644))
    manifest = {
        "v": 1,
        "agent": claude_code.NAME,
        "installed_at": events.now_stamp(),
        "engine": __version__,
        "launcher": str(launcher),
        "backup": str(backup),
        "files": entries,
    }
    paths.write_private(
        paths.install_manifest(), (json.dumps(manifest, indent=2) + "\n").encode()
    )
    return backup


# --------------------------------------------------------------- uninstall


def _missing_parents(path: Path) -> list[str]:
    """Folders above path, inside claude_dir(), that do not exist yet. Deepest first."""
    stop = paths.claude_dir()
    missing = []
    folder = path.parent
    while folder != stop and folder.is_relative_to(stop) and not folder.exists():
        missing.append(str(folder))
        folder = folder.parent
    return missing


def _remove_created(entry: dict) -> None:
    """Remove the folders init created for this file, while they are empty."""
    for folder in entry.get("created") or []:
        try:
            Path(folder).rmdir()
        except OSError:
            return


def _refusal_diff(entry: dict, backup: Path, path: Path, current: bytes | None) -> str:
    installed = entry.get("installed")
    expected = _read_bytes(backup / installed) if isinstance(installed, str) else None
    return "".join(
        difflib.unified_diff(
            _lines(expected), _lines(current), f"{path} as installed", f"{path} now"
        )
    )


def _check_one(entry: dict, backup: Path) -> tuple[str, str, bytes | None]:
    """("restore" | "remove" | "refused" | "unchanged", diff, original). Writes nothing."""
    path = Path(entry["path"])
    current = _read_bytes(path)
    digest = _sha(current)
    if digest != entry.get("sha256_after"):
        if digest == entry.get("sha256_before"):
            return "unchanged", "", None
        return "refused", _refusal_diff(entry, backup, path, current), None
    if entry.get("existed") is True:
        original = _read_bytes(backup / str(entry.get("backup")))
        if original is None or _sha(original) != entry.get("sha256_before"):
            return (
                "refused",
                f"The backup of {path} is missing or changed in {backup}.\n",
                None,
            )
        return "restore", "", original
    return "remove", "", None


def _undo_one(entry: dict, outcome: str, original: bytes | None) -> None:
    path = Path(entry["path"])
    if outcome == "restore":
        assert original is not None
        _atomic_write(path, original, _mode_of(path, 0o644))
    elif outcome == "remove":
        _target(path).unlink()
        _remove_created(entry)


def uninstall() -> UninstallReport:
    """Restore or remove every file init wrote, or none of them. Never touches the record.

    All or nothing: when any file is refused nothing is changed, so the hooks never
    keep running without the skill file they print through.
    """
    manifest = _read_manifest()
    if manifest is None:
        raise InstallError(
            "Firsthand is not installed here: there is no install record at "
            f"{paths.install_manifest()}. Nothing was changed."
        )
    backup = Path(str(manifest.get("backup", "")))
    restored: list[Path] = []
    removed: list[Path] = []
    refused: list[tuple[Path, str]] = []
    checked = [
        (entry, *_check_one(entry, backup))
        for entry in manifest.get("files", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    ]
    for entry, outcome, diff, _ in checked:
        if outcome == "refused":
            refused.append((Path(entry["path"]), diff))
    if refused:
        return UninstallReport((), (), tuple(refused))
    for entry, outcome, _, original in checked:
        _undo_one(entry, outcome, original)
        if outcome == "restore":
            restored.append(Path(entry["path"]))
        elif outcome == "remove":
            removed.append(Path(entry["path"]))
    paths.install_manifest().unlink()
    return UninstallReport(tuple(restored), tuple(removed), tuple(refused))
