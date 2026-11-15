"""The record: a local git repo of plain JSON events, outside any project.

Layout: FORMAT, then events/<yyyy>/<mm>/<ulid>.json, one file per event. Only the
daemon process constructs a Record once init has finished, so there is one writer.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import threading
import time
from collections.abc import Collection, Mapping
from datetime import UTC, datetime
from pathlib import Path

from firsthand import ENGINE, paths
from firsthand.events import now_stamp
from firsthand.model import FirsthandError

FORMAT_LINE = "firsthand-record 1"

# Carried from the skill's record for step 5. Unused in 2a.
INTERVALS_AFTER_SUCCESS = [3, 7, 21, 60, 180]
DURABLE_AFTER_DAYS = 7
DEFAULT_DUE_LIMIT = 3

CONFLICT_MARKER = re.compile(r"^(<{7}|={7}|>{7})( |$)", re.MULTILINE)

EVENT_TYPES = frozenset(
    {
        "task.started",
        "task.event",
        "moment.offered",
        "call.sealed",
        "call.confirmed",
        "call.confidence",
        "check.ran",
        "check.unavailable",
        "call.scored",
        "moment.skipped",
        "moment.closed",
        "note.posted",
        "episode.red",
        "episode.green",
    }
)

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_AUTHOR = ("firsthand", "firsthand@localhost")
_ulid_lock = threading.Lock()
_ulid_last: list[int] = [0, 0]  # last millisecond, last random part


class RecordError(FirsthandError):
    code = "record"


def git(*args: str, cwd: Path | None = None) -> str | None:
    """Output of a git command, or None if git is missing or the command fails."""
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": _AUTHOR[0],
        "GIT_AUTHOR_EMAIL": _AUTHOR[1],
        "GIT_COMMITTER_NAME": _AUTHOR[0],
        "GIT_COMMITTER_EMAIL": _AUTHOR[1],
    }
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    try:
        done = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except OSError:
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def _encode32(value: int, length: int) -> str:
    chars = []
    for _ in range(length):
        chars.append(_CROCKFORD[value & 31])
        value >>= 5
    return "".join(reversed(chars))


def new_ulid(at: datetime | None = None) -> str:
    """26 characters, Crockford base 32, sortable by time.

    Within one millisecond in this process the random part is incremented, so ids
    made in a row still sort in the order they were made.
    """
    ms = int(at.timestamp() * 1000) if at is not None else time.time_ns() // 1_000_000
    with _ulid_lock:
        if at is None and ms <= _ulid_last[0]:
            ms = _ulid_last[0]
            rand = (_ulid_last[1] + 1) & ((1 << 80) - 1)
        else:
            rand = secrets.randbits(80)
        if at is None:
            _ulid_last[0], _ulid_last[1] = ms, rand
    return _encode32(ms, 10) + _encode32(rand, 16)


def read_json(path: Path) -> dict:
    """Raises RecordError on conflict markers or bad JSON."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RecordError(f"{path} cannot be read ({exc}).") from exc
    if CONFLICT_MARKER.search(text):
        raise RecordError(
            f"{path} has unresolved git merge conflict markers. Remove them and save valid JSON."
        )
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RecordError(
            f"{path} is not valid JSON ({exc}). Restore it from git."
        ) from exc
    if not isinstance(data, dict):
        raise RecordError(f"{path} does not hold a JSON object. Restore it from git.")
    return data


def write_json(path: Path, data: Mapping) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(data), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def ensure_record(root: Path | None = None) -> Path:
    """Create the record (mode 0700, git repo, FORMAT, first commit "init"). Idempotent."""
    root = root or paths.record_dir()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    if not (root / ".git").exists() and git("init", "-q", cwd=root) is None:
        raise RecordError(f"git init failed in {root}. Check that git is installed.")
    fmt = root / "FORMAT"
    if not fmt.exists():
        fmt.write_text(FORMAT_LINE + "\n", encoding="utf-8")
    if git("rev-parse", "--verify", "-q", "HEAD", cwd=root) is None:
        _commit(root, "init")
    return root


def _commit(root: Path, subject: str) -> bool:
    if git("add", "-A", cwd=root) is None:
        raise RecordError(f"git add failed in {root}.")
    status = git("status", "--porcelain", cwd=root)
    if status is None:
        raise RecordError(f"git status failed in {root}.")
    if not status:
        return False
    done = git(
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "--no-verify",
        "-m",
        subject,
        cwd=root,
    )
    if done is None:
        raise RecordError(f"git commit failed in {root}.")
    return True


class Record:
    def __init__(self, root: Path | None = None, engine: str = ENGINE) -> None:
        self.root = root or paths.record_dir()
        self.engine = engine
        fmt = self.root / "FORMAT"
        try:
            line = fmt.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RecordError(f"No record at {self.root}. Run: firsthand init") from exc
        if line != FORMAT_LINE:
            raise RecordError(f"{fmt} says {line!r}, expected {FORMAT_LINE!r}.")
        self._lock = threading.RLock()
        self._events: list[dict] = []
        self._by_id: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        events_dir = self.root / "events"
        if not events_dir.is_dir():
            return
        for path in events_dir.glob("*/*/*.json"):
            event = read_json(path)
            self._index(event)
        self._events.sort(key=lambda e: e["id"])

    def _index(self, event: dict) -> None:
        self._events.append(event)
        self._by_id[event["id"]] = event

    def append(
        self,
        type: str,
        body: Mapping[str, object],
        *,
        project: str | None = None,
        change: str | None = None,
        moment: str | None = None,
        surface: str | None = None,
        at: str | None = None,
    ) -> dict:
        """Write one event file and return the event."""
        if type not in EVENT_TYPES:
            raise RecordError(f"unknown event type {type!r}")
        stamp = at or now_stamp()
        try:
            when = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        except ValueError as exc:
            raise RecordError(f"bad time {stamp!r}") from exc
        with self._lock:
            event_id = new_ulid()
            event = {
                "format": 1,
                "id": event_id,
                "type": type,
                "project": project,
                "change": change,
                "moment": moment,
                "surface": surface,
                "engine": self.engine,
                "at": stamp,
                "body": dict(body),
                "x": {},
            }
            path = (
                self.root / "events" / f"{when:%Y}" / f"{when:%m}" / f"{event_id}.json"
            )
            write_json(path, event)
            self._index(event)
            return event

    def events(
        self,
        *,
        types: Collection[str] | None = None,
        project: str | None = None,
        moment: str | None = None,
        since: str | None = None,
    ) -> list[dict]:
        """Matching events, oldest first by id. `since` compares with `at`."""
        with self._lock:
            return [
                e
                for e in self._events
                if (types is None or e["type"] in types)
                and (project is None or e.get("project") == project)
                and (moment is None or e.get("moment") == moment)
                and (since is None or e.get("at", "") >= since)
            ]

    def get(self, event_id: str) -> dict | None:
        with self._lock:
            return self._by_id.get(event_id)

    def commit(self, subject: str) -> bool:
        """git add -A and commit as firsthand. False when there was nothing to commit."""
        with self._lock:
            return _commit(self.root, subject)

    def dirty(self) -> bool:
        with self._lock:
            status = git("status", "--porcelain", cwd=self.root)
            if status is None:
                raise RecordError(f"git status failed in {self.root}.")
            return bool(status)
