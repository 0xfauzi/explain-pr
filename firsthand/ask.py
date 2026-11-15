"""Gates, the moment state table and the chat control words.

Pure functions. The engine asks `gates` whether a question may be offered, and
moves every moment through `step` so that no state change happens outside the
table of build-2a-contract.md section 8.2.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from firsthand.model import Dial, EngineError, MomentState

PRESSURE_WORDS = ("urgent", "prod is down")
CONTROL_WORDS = ("skip", "quiet", "quiet today", "quiet here")

# (from, action) -> to. Actions: pick and skip_room (the Room), undo, seal (a chat
# reply, firsthand answer, Show the result, or the next prompt on a held pick),
# skip_final, close, settle.
TABLE: dict[tuple[str, str], MomentState] = {
    ("open", "pick"): "held",
    ("open", "skip_room"): "held",
    ("held", "undo"): "open",
    ("held", "seal"): "sealed",
    ("held", "skip_final"): "skipped",
    ("open", "seal"): "sealed",
    ("open", "skip_final"): "skipped",
    ("open", "close"): "closed",
    ("sealed", "settle"): "settled",
}

_STATE_MESSAGES = {
    "held": "This call is locked. Undo it first, or show the result.",
    "sealed": "This question is already locked.",
    "settled": "This question is already answered.",
    "skipped": "This question was skipped.",
    "closed": "This question is closed.",
    "open": "This question is still open.",
}


@dataclass(frozen=True)
class GateInput:
    dial: Dial
    quiet: bool
    pressure: bool
    asked_today: int
    daily_limit: int
    change_asked: bool
    first_prompt_turn: bool
    session_stopped: bool


def gates(g: GateInput) -> str | None:
    """None means ask. Otherwise the name of the first gate that fails."""
    checks = (
        ("dial", g.dial not in ("standard", "deep")),
        ("quiet", g.quiet),
        ("pressure", g.pressure),
        ("limit", g.asked_today >= g.daily_limit),
        ("change", g.change_asked),
        ("first-prompt", g.first_prompt_turn),
        ("session-skips", g.session_stopped),
    )
    for name, failed in checks:
        if failed:
            return name
    return None


def fact_allowed(g: GateInput) -> bool:
    """A fact line may print: the dial is not off, no quiet, no pressure, not the first turn."""
    return (
        g.dial != "off" and not g.quiet and not g.pressure and not g.first_prompt_turn
    )


def is_pressure(branch: str | None, prompts: Iterable[str]) -> bool:
    if branch and branch.lower().startswith("hotfix"):
        return True
    return any(word in (p or "").lower() for p in prompts for word in PRESSURE_WORDS)


def normalise(text: str) -> str:
    """Strip, lower case, collapse inner whitespace, curly apostrophe, one full stop."""
    words = " ".join((text or "").replace("’", "'").strip().lower().split())
    return words[:-1].rstrip() if words.endswith(".") else words


def control_word(text: str) -> str | None:
    words = normalise(text)
    return words if words in CONTROL_WORDS else None


def step(state: MomentState, action: str) -> MomentState:
    """The next state, or EngineError("state") for a pair the table does not hold."""
    nxt = TABLE.get((state, action))
    if nxt is None:
        message = _STATE_MESSAGES.get(state, "This question cannot do that now.")
        raise EngineError(message, "state")
    return nxt
