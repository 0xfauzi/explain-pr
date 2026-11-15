"""The engine checkpoint, run/state.json: private to the engine.

Plain conversions between the engine's live objects and JSON. It never holds a
key result: moments carry only what the card shows, and checks are rerun after a
restart unless their key file is still in the key store.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path

from firsthand import paths
from firsthand.model import (
    Candidate,
    HeadState,
    HookReply,
    Moment,
    SpoolEvent,
    TestItem,
)
from firsthand.timeline import SessionState, Task

STATE_FORMAT = 1
MAX_MOMENTS = 400
MAX_SEEN = 512


# ----------------------------------------------------- the engine's live objects


@dataclass(eq=False)
class Check:
    cand: Candidate
    skey: str
    # control, undoing, failed, finished, unavailable or cancelled
    status: str = "control"
    decided: bool = False
    silent: bool = False
    cancel: threading.Event = field(default_factory=threading.Event)
    rerun_of: str | None = None  # a dispute: the check.ran event it reruns
    reason: str | None = None  # the person's dispute text, scanned

    @property
    def id(self) -> str:
        return self.cand.check_id


@dataclass
class Project:
    id: str
    root: str
    live: str | None = None  # the moment in open, held or sealed
    check: str | None = None  # the current check of this project
    queued: tuple[str, Candidate] | None = None
    replaces: str | None = None


@dataclass
class Session:
    key: str
    st: SessionState
    done_tree: str | None = None
    queue: list[dict] = field(default_factory=list)  # {"text", "check"}
    fact_due: str | None = None
    fact_check: str | None = None
    last_at: str = ""
    episode: dict | None = (
        None  # Call it: the failure being followed (engine_callit.py)
    )
    brief: dict | None = None  # Brief: the task start being watched (engine_brief.py)


@dataclass
class PendingReply:
    ev: SpoolEvent
    fn: Callable[[HookReply], None]
    done: bool = False
    deadline: float = 0.0


def skey(agent: str, session: str, project: str) -> str:
    return f"{agent}/{session}/{project}"


def _task_to(t: Task | None) -> dict | None:
    if t is None:
        return None
    data = asdict(t)
    data["pending_ask"] = sorted(t.pending_ask)
    return data


def _task_from(data: Mapping | None) -> Task | None:
    if not data:
        return None
    return Task(**{**data, "pending_ask": set(data.get("pending_ask", ()))})


def session_to(s: SessionState) -> dict:
    data = asdict(s)
    data["task"] = _task_to(s.task)
    data["head"] = asdict(s.head) if s.head is not None else None
    return data


def session_from(data: Mapping) -> SessionState:
    head = data.get("head")
    return SessionState(
        **{
            **data,
            "task": _task_from(data.get("task")),
            "head": HeadState(**head) if head else None,
        }
    )


def moment_to(m: Moment) -> dict:
    data = asdict(m)
    data["tests"] = [asdict(t) for t in m.tests]
    return data


def moment_from(data: Mapping) -> Moment:
    tests = tuple(
        TestItem(**{**t, "assert_lines": tuple(t.get("assert_lines", ()))})
        for t in data.get("tests", ())
    )
    return Moment(**{**data, "tests": tests})


def load(path: Path | None = None) -> dict:
    """The checkpoint, or an empty one when the file is missing or unreadable."""
    target = path or paths.state_file()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("v") != STATE_FORMAT:
        return {}
    return data


def save(data: Mapping[str, object], path: Path | None = None) -> None:
    target = path or paths.state_file()
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    body = json.dumps({"v": STATE_FORMAT, **data}, sort_keys=True) + "\n"
    paths.write_private(target, body.encode())
