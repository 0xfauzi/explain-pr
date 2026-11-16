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


def _match_days(v: ViewInput, scored: Iterable[tuple[dict, Moment | None]]) -> set:
    return {
        local_date(e["at"], v.tz) for e, _ in scored if e["body"]["result"] == "match"
    }


def _level(v: ViewInput, scored: Iterable[tuple[dict, Moment | None]]) -> dict:
    matched = [e for e, _ in scored if e["body"]["result"] == "match"]
    days = sorted({local_date(e["at"], v.tz) for e in matched})
    catches = [e for e in matched if e["body"].get("catch")]
    if len(days) >= 2 and catches:
        since = _shown_since(v, matched)
        return {
            "level": "shown",
            "level_line": f"Shown since {since}.",
            "days": 2,
            "shown_since": since,
        }
    have = min(len(days), 1)
    return {
        "level": "too_few",
        "level_line": f"Too few answers. {have} of 2.",
        "days": have,
        "shown_since": None,
    }


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
        return "newest answer today"
    if days == 1:
        return "newest answer 1 day ago"
    return f"newest answer {days} days ago"


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
        "Writing a check that fails with the change undone.",
        "Whether the goal was the right goal.",
    ),
)


def _no_level(v: ViewInput, scored: Sequence[tuple[dict, Moment | None]]) -> dict:
    return {
        "level": "none",
        "level_line": NO_LEVEL,
        "days": min(2, len(_match_days(v, scored))),
        "shown_since": None,
    }


def _calls(v: ViewInput, scored: Sequence[tuple[dict, Moment | None]], easy: bool):
    """One cell per scored call, oldest first: the set `_counts` counts."""
    events = sorted((e for e, _ in scored), key=lambda e: (e["at"], e["id"]))
    return [
        {
            "at": e["at"],
            "day": words.short_date(e["at"], v.tz),
            "you": e["body"]["result"],
            "easy": e["body"].get("outcome_kind") == "common" if easy else None,
            "catch": bool(e["body"].get("catch")),
        }
        for e in events
    ]


def _track(v: ViewInput, scored: Sequence[tuple[dict, Moment | None]], easy: bool):
    calls = _calls(v, scored, easy)
    return {"calls": calls, "since": calls[0]["day"] if calls else None}


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
    level = _level(v, scored) if fixed_answer else _no_level(v, scored)
    return {
        "n": n,
        "name": name,
        **level,
        "counts": f"Your answers of this kind: {matched} of {total} matched.",
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
        "matched": matched,
        "total": total,
        "fixed_count": fixed,
        "fixed_answer": fixed_answer,
        **_track(v, scored, bool(fixed_answer)),
    }


LEGEND = (
    (
        "Shown: your answers matched on 2 different days, and 1 or more was not the "
        "easy answer."
    ),
    (
        '"Too few answers. n of 2." counts the days with a matched answer. '
        "Shown needs 2 days and 1 catch."
    ),
)
NO_LEVEL = (
    "No level yet. A Brief has no easy answer. Firsthand has no rule for a catch "
    "on a Brief."
)


def skills_view(v: ViewInput, project_id: str | None) -> dict:
    del project_id  # counted across projects
    return {
        "legend": list(LEGEND),
        "rows": [_skill_row(v, spec) for spec in _SKILL_ROWS],
    }
