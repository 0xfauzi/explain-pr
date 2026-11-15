"""Shared dataclasses, type aliases and Protocols used across Firsthand.

Every group imports its vocabulary from here so that the names agree. Nothing in
this module does any I/O.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal, Protocol

# --------------------------------------------------------------- vocabulary

EventKind = Literal[
    "session_start",
    "prompt_submit",
    "before_tool",
    "after_tool",
    "tool_failed",
    "turn_end",
]
ToolKind = Literal["edit", "shell", "ask", "plan", "other"]
Dial = Literal["off", "notes", "standard", "deep"]
TestResult = Literal[
    "fails_on_assertion", "still_passes", "cannot_run", "does_not_pass"
]
How = Literal["pytest", "exit_code"]
# An answer as stored: "fails", "passes" or "dont_know" for one test; for several
# tests "none", one number ("2") or several ascending, joined by commas ("1,3");
# Call it a pick number; the Brief "line". Each moment validates its own.
Answer = str
Confidence = Literal["high", "low"]
Channel = Literal["room", "chat"]
MomentState = Literal["open", "held", "sealed", "settled", "skipped", "closed"]
CloseHow = Literal[
    "moved-on",
    "shown-first",
    "check-dropped",
    "wrong-start",
    "quiet",
    "off",
    "unseen",
    "fix-started",
]
Want = Literal[
    "question", "pending", "result", "finding", "fact", "ack", "work", "confirm"
]

REVEALED: frozenset[str] = frozenset({"sealed", "settled", "skipped", "closed"})
PRINT_PREFIX = "Firsthand result for the reply above. The firsthand skill prints these lines unchanged:"

# ------------------------------------------------------------------ errors


class FirsthandError(Exception):
    """Base. Carries a code for the Room and the control socket."""

    code: str = "internal"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self._message = message
        if code is not None:
            self.code = code

    @property
    def message(self) -> str:
        return self._message


class EngineError(FirsthandError):
    """Codes: not_found, state, invalid, confirm, refused, no_question."""


class KeyLocked(FirsthandError):
    """A result was asked for before it may be shown."""

    code = "locked"


# ------------------------------------------------------------- spool event


@dataclass(frozen=True)
class SpoolEvent:
    id: str
    at: str
    agent: str
    session: str
    cwd: str
    event: EventKind
    tool: ToolKind | None = None
    tool_use: str | None = None
    command: str | None = None
    exit: int | None = None
    failing: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()
    prompt: str | None = None
    prompt_cut: bool = False
    source: str | None = None
    venv: str | None = None
    sub: bool = False
    interrupted: bool = False
    question: str | None = None  # the ask tool's question text, on before_tool


# --------------------------------------------------------- git and checks


@dataclass(frozen=True)
class FileChange:
    path: str
    status: Literal["A", "M", "D"]


@dataclass(frozen=True)
class HeadState:
    commit: str | None
    branch: str | None


@dataclass(frozen=True)
class TestItem:
    n: int
    id: str
    name: str
    path: str
    line: int
    status: Literal["new", "edited"]
    assert_lines: tuple[int, ...]
    assert_line: int | None
    assert_text: str | None

    __test__ = False  # not a unittest or pytest test class


@dataclass(frozen=True)
class Candidate:
    kind: str
    check_id: str
    project_id: str
    project_root: str
    task_id: str
    change_id: str
    base_tree: str
    head_tree: str
    source_changes: tuple[FileChange, ...]
    tests: tuple[TestItem, ...]
    how: How
    high_stakes: str | None


@dataclass(frozen=True)
class StepRun:
    step: Literal["control", "undone"]
    command: str
    exit: int | None
    failing: tuple[str, ...]
    output_sha256: str


@dataclass(frozen=True)
class KeyItem:
    id: str
    result: TestResult
    assert_line: int | None
    assert_text: str | None
    fail_line: int | None


@dataclass(frozen=True)
class Key:
    moment: str
    kind: str
    how: How
    base_tree: str
    head_tree: str
    made_at: str
    tests: tuple[KeyItem, ...]
    steps: tuple[StepRun, ...]
    undone_paths: tuple[str, ...]
    duration_s: float
    extra: Mapping[str, object] | None = None  # moment-specific facts (Call it)


@dataclass(frozen=True)
class CheckOutcome:
    key: Key | None
    unavailable: str | None
    step: Literal["setup", "control", "undone"] | None = None
    steps: tuple[StepRun, ...] = ()


@dataclass(frozen=True)
class Reply:
    answer: Answer
    confidence: Confidence | None


@dataclass(frozen=True)
class Score:
    result: Literal["match", "miss", "unscored"]
    outcome_kind: Literal["common", "uncommon"]
    catch: bool
    unscored_reason: str | None


# ------------------------------------------------ moment, settings, reply


@dataclass
class Moment:
    id: str
    kind: str
    state: MomentState
    project_id: str
    change_id: str
    task_id: str
    session: str
    task_name: str
    base_at: str
    base_tree: str
    head_tree: str
    tests: tuple[TestItem, ...]
    how: How
    high_stakes: str | None
    offered_at: str
    seen: bool = False
    pending: dict | None = None
    answer: Answer | None = None
    confidence: Confidence | None = None
    channel: Channel | None = None
    close_how: CloseHow | None = None
    opened: bool = False
    extra: dict | None = None  # moment-specific card data (Call it: test, picks, trace)


@dataclass(frozen=True)
class Settings:
    dial: Dial = "standard"
    dial_before_off: Dial = "standard"
    daily_limit: int = 1
    findings_to_agent: bool = True
    work_computer: bool = True
    quiet_today: str | None = None
    check_time_limit_s: int = 120


@dataclass(frozen=True)
class ProjectSettings:
    id: str
    name: str
    roots: tuple[str, ...]
    test_command: str | None
    high_stakes: tuple[str, ...]
    quiet: bool = False
    env: tuple[tuple[str, str], ...] = ()
    carry: tuple[str, ...] = ()


DEFAULT_HIGH_STAKES = (
    "**/migrations/**",
    "**/auth/**",
    "**/payments/**",
    "**/billing/**",
)


class SettingsStore(Protocol):
    def load(self) -> Settings: ...
    def set(self, key: str, value: object) -> Settings: ...
    def project(self, project_id: str) -> ProjectSettings | None: ...
    def ensure_project(self, project_id: str, root: str) -> ProjectSettings: ...
    def set_project(
        self, project_id: str, key: str, value: object
    ) -> ProjectSettings: ...


@dataclass(frozen=True)
class HookReply:
    event_id: str
    session: str
    event: Literal["turn_end", "prompt_submit"]
    visible: str | None = None
    context: str | None = None


# ---------------------------------------------------------------- EngineAPI


class EngineAPI(Protocol):
    # events
    def handle(self, ev: SpoolEvent, reply: Callable[[HookReply], None]) -> None: ...
    def delivered(self, event_id: str, ok: bool) -> None: ...
    def tick(self) -> None: ...
    def idle(self) -> bool: ...
    def close(self) -> None: ...
    def subscribe(self, fn: Callable[[dict], None]) -> Callable[[], None]: ...

    # views
    def inbox(self, project: str | None = None) -> dict: ...
    def question(
        self, ref: str | None = None, *, cwd: str | None = None, seen: bool = True
    ) -> dict: ...
    def journal(self, project: str | None = None, limit: int = 200) -> dict: ...
    def skills(self, project: str | None = None) -> dict: ...
    def settings(self, project: str | None = None) -> dict: ...
    def status(self, cwd: str | None = None) -> dict: ...

    # actions
    def lock(
        self,
        ref: str | None,
        answer: str,
        *,
        channel: Channel,
        final: bool,
        cwd: str | None = None,
    ) -> dict:
        # A Protocol body never runs. The del marks these names as part of the
        # interface for vulture until an implementation in the tree reads them.
        del channel, final
        ...

    def undo(self, ref: str) -> dict: ...
    def show(self, ref: str) -> dict: ...
    def confidence(self, ref: str, value: str | None) -> dict: ...
    def skip(
        self, ref: str | None, *, channel: Channel, final: bool, cwd: str | None = None
    ) -> dict:
        del channel, final
        ...

    def wrong_start(self, ref: str) -> dict: ...
    def dispute(self, ref: str, reason: str) -> dict: ...
    def quiet(
        self,
        scope: Literal["session", "today", "here"],
        on: bool = True,
        *,
        cwd: str | None = None,
        session: str | None = None,
    ) -> dict: ...
    def set_settings(
        self,
        changes: Mapping[str, object],
        *,
        project: str | None = None,
        source: Literal["room", "cli", "agent"],
        confirm: bool = False,
    ) -> dict:
        del confirm
        ...
