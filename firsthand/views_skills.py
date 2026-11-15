"""The Skills read model: one row per skill with a scored moment.

Split from `views` to keep each file under the size limit.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date

from firsthand import words
from firsthand.model import Moment
from firsthand.views import (
    BRIEF,
    CALL,
    FIXED_ANSWER,
    REVERT,
    ViewInput,
    _counts,
    _scores,
    kind_of,
    local_date,
)


def _level(v: ViewInput, scored: Iterable[tuple[dict, Moment | None]]) -> dict:
    matched = [e for e, _ in scored if e["body"]["result"] == "match"]
    days = sorted({local_date(e["at"], v.tz) for e in matched})
    catches = [e for e in matched if e["body"].get("catch")]
    if len(days) >= 2 and catches:
        since = _shown_since(v, matched)
        return {"level": "shown", "level_line": f"Shown since {since}."}
    have = min(len(days), 1)
    return {"level": "too_few", "level_line": f"Too few calls. {have} of 2."}


def _shown_since(v: ViewInput, matched: Sequence[dict]) -> str:
    seen_days: set[date] = set()
    caught = False
    for e in matched:
        seen_days.add(local_date(e["at"], v.tz))
        caught = caught or bool(e["body"].get("catch"))
        if len(seen_days) >= 2 and caught:
            return words.short_date(e["at"], v.tz)
    return words.short_date(matched[-1]["at"], v.tz)


def _newest(v: ViewInput, scored: Sequence[tuple[dict, Moment | None]]) -> str | None:
    if not scored:
        return None
    newest = max(local_date(e["at"], v.tz) for e, _ in scored)
    days = (v.today - newest).days
    if days <= 0:
        return "newest call today"
    return "newest call 1 day ago" if days == 1 else f"newest call {days} days ago"


_SKILL_ROWS = (
    (REVERT, 1, "Verification", FIXED_ANSWER, words.COVERS, words.NO_EVIDENCE),
    (
        CALL,
        3,
        "Debugging and diagnosis",
        "the file changed in this task",
        "Naming where the cause is before the fix exists.",
        "Bugs with no failing test.",
    ),
    (
        BRIEF,
        5,
        "Framing the problem and the brief",
        None,  # a made thing, not a pick: no fixed answer (learning.md section 7.1)
        "Writing a done check that fails without the change.",
        "Whether the goal was the right goal.",
    ),
)


def _skill_row(v: ViewInput, spec: tuple) -> dict:
    kind, n, name, fixed_answer, covers, no_evidence = spec
    scored = [(e, m) for e, m in _scores(v, kind) if e["body"]["result"] != "unscored"]
    matched, total, fixed = _counts(v, kind)
    mine = {
        e["moment"]
        for e in v.events
        if e["type"] == "moment.offered" and kind_of(v, e["moment"]) == kind
    }
    answered = [
        e for e in v.events if e["type"] == "call.sealed" and e.get("moment") in mine
    ]
    dont_know = sum(1 for e in answered if e["body"].get("answer") == "dont_know")
    skipped = sum(
        1 for e in v.events if e["type"] == "moment.skipped" and e.get("moment") in mine
    )
    # A made thing (the Brief) has no fixed answer, so no call of it can be a catch
    # and "Shown" could never be reached: say so instead of a count that cannot move.
    level = (
        _level(v, scored) if fixed_answer else {"level": "none", "level_line": NO_LEVEL}
    )
    return {
        "n": n,
        "name": name,
        **level,
        "counts": f"Your calls of this kind: {matched} of {total} matched.",
        "fixed": (
            f'Always answering "{fixed_answer}" would have scored {fixed} of {total}.'
            if fixed_answer
            else None
        ),
        "asked": (
            f"Asked {len(mine)}. Answered {len(answered) - dont_know}. "
            f"Don't know {dont_know}. Skipped {skipped}."
        ),
        "newest": _newest(v, scored),
        "covers": covers,
        "no_evidence": no_evidence,
        "checked": "Checked by a run.",
    }


LEGEND = (
    (
        "Shown: you made this call correctly when it was not the easy answer, with "
        "matched calls on two different days."
    ),
    '"Too few calls. n of 2." counts the days with a matched call. Shown needs 2.',
)
NO_LEVEL = (
    "No level yet. A done check has no easy answer to beat, and what counts as "
    "a catch for one is not decided."
)


def skills_view(v: ViewInput, project_id: str | None) -> dict:
    del project_id  # counted across projects
    return {
        "legend": list(LEGEND),
        "rows": [_skill_row(v, spec) for spec in _SKILL_ROWS],
    }
