"""The learner's record as data: constants, storage, attempts and the schedule.

learning.py is the command line over this module. Kept separate so the
schedule rules can be read in one place, and imported by a test or a script
without running the CLI.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

SCHEMA_VERSION = 1

DEFAULT_DIMENSIONS = [
    "architecture-and-design",
    "domain-model",
    "correctness-and-testing",
    "debugging-and-diagnosis",
    "performance",
    "reliability-and-operations",
    "security",
    "data-and-storage",
    "concurrency",
    "code-reading",
]

# Kinds of attempt. "attempt" is a prediction made BEFORE any explanation, so a
# wrong answer there is expected and says nothing about retention: it is recorded
# but excluded from the schedule and from levels. The novel kinds put the learner
# in front of a case they have not seen explained, which is what transfer means.
KINDS = [
    "attempt",
    "explain-back",
    "retrieval",
    "transfer",
    "diagnosis",
    "repair",
    "field",
]
NOVEL_KINDS = {"transfer", "diagnosis", "repair", "field"}
SCHEDULED_KINDS = set(KINDS) - {"attempt"}

OUTCOMES = ["correct", "partial", "wrong", "skipped"]
CONFIDENCES = ["low", "medium", "high"]
HINT_LEVELS = [0, 1, 2, 3]

# Who graded an attempt. Only "claude" grades count toward levels and the review
# schedule: the learner produced an answer and it was judged against a rubric
# fixed beforehand. Page results are recognition (multiple choice, ordering) or
# self-assessment, which are weaker evidence, so they inform misconceptions and
# gaps but do not move a topic up.
GRADERS = ["claude", "page", "self"]

# Review intervals in days after each consecutive unassisted correct answer.
# Cepeda et al. (2008, Psychological Science) found the best gap between reviews
# grows with how long the knowledge must last; the learner wants it for the life
# of a project, months, so the gaps grow toward months. Karpicke and Roediger
# (2007) found expanding and equal schedules give similar long-term retention, so
# the exact values matter less than reviews happening at all. These are starting
# values. `map` prints the success rate at each step, so they can be tuned from
# the learner's own record rather than guessed.
INTERVALS_AFTER_SUCCESS = [3, 7, 21, 60, 180]
# After a wrong, partial or hinted answer, or for a topic never reviewed: tomorrow.
# Reviewing the same day mostly tests short-term memory.
INTERVAL_AFTER_MISS = 1

# A success counts as durable only if it came at least this long after the topic
# was first recorded. One week is the shortest gap in the schedule above that is
# clearly beyond the session in which the topic was learned.
DURABLE_AFTER_DAYS = 7

# Three reviews fit in a short break. More than that and practice becomes a chore
# the learner skips, which is worse than fewer reviews. A judgement, not a measure.
DEFAULT_DUE_LIMIT = 3

LEVEL_NAMES = {
    0: "not yet",
    1: "with help",
    2: "recalls",
    3: "transfers",
}


class RecordError(Exception):
    """A problem the caller can fix. The message says how."""


# ---------------------------------------------------------------- storage


def data_dir(arg: str | None) -> Path:
    return Path(arg or os.environ.get("LEARNING_DIR") or ".learning")


def today(arg: str | None) -> dt.date:
    if not arg:
        return dt.datetime.now().astimezone().date()
    try:
        return dt.date.fromisoformat(arg)
    except ValueError as exc:
        raise RecordError(f"--today must be YYYY-MM-DD, got {arg!r}") from exc


def load_topics(root: Path) -> dict:
    path = root / "topics.json"
    if not path.exists():
        raise RecordError(
            f"No record at {root}/. Run `learning.py init` from the repository root first, "
            "or pass --dir to point at an existing record."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecordError(
            f"{path} is not valid JSON ({exc}). Restore it from git."
        ) from exc
    if data.get("schema_version") != SCHEMA_VERSION:
        raise RecordError(
            f"{path} has schema_version {data.get('schema_version')!r}; "
            f"this script reads {SCHEMA_VERSION}."
        )
    return data


def save_topics(root: Path, data: dict) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    (root / "topics.json").write_text(text, encoding="utf-8")


def load_events(root: Path) -> list[dict]:
    path = root / "attempts.jsonl"
    if not path.exists():
        return []
    events = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RecordError(
                f"{path} line {number} is not valid JSON ({exc}). Restore it from git."
            ) from exc
    return events


def append_event(root: Path, event: dict) -> None:
    with (root / "attempts.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def now_stamp(today_arg: str | None) -> str:
    if today_arg:
        return f"{today(today_arg).isoformat()}T12:00:00"
    return (
        dt.datetime.now().astimezone().replace(microsecond=0, tzinfo=None).isoformat()
    )


# ---------------------------------------------------------------- attempts


def build_attempts(events: list[dict]) -> dict[int, dict]:
    """Join each `ask` with its `grade`, keyed by attempt number."""
    attempts: dict[int, dict] = {}
    for event in events:
        if event.get("event") == "ask":
            attempts[event["attempt"]] = dict(event, graded=None)
        elif event.get("event") == "grade" and event.get("attempt") in attempts:
            attempts[event["attempt"]]["graded"] = event
    return attempts


def graded_for_topic(attempts: dict[int, dict], topic_id: str) -> list[dict]:
    rows = [a for a in attempts.values() if a["topic"] == topic_id and a["graded"]]
    return sorted(rows, key=lambda a: a["graded"]["at"])


def is_clean_success(attempt: dict) -> bool:
    grade = attempt["graded"]
    return grade["outcome"] == "correct" and grade["hint"] == 0


def scheduled_history(attempts: dict[int, dict], topic_id: str) -> list[dict]:
    return [
        a
        for a in graded_for_topic(attempts, topic_id)
        if a["kind"] in SCHEDULED_KINDS
        and a["graded"]["outcome"] != "skipped"
        and a["graded"].get("grader", "claude") == "claude"
    ]


def success_streak(history: list[dict]) -> int:
    streak = 0
    for attempt in reversed(history):
        if not is_clean_success(attempt):
            break
        streak += 1
    return streak


def next_due(topic: dict, history: list[dict]) -> dt.date:
    if not history:
        return dt.date.fromisoformat(topic["created"]) + dt.timedelta(
            days=INTERVAL_AFTER_MISS
        )
    last = dt.date.fromisoformat(history[-1]["graded"]["at"][:10])
    streak = success_streak(history)
    if streak == 0:
        return last + dt.timedelta(days=INTERVAL_AFTER_MISS)
    step = min(streak, len(INTERVALS_AFTER_SUCCESS)) - 1
    return last + dt.timedelta(days=INTERVALS_AFTER_SUCCESS[step])


def level(history: list[dict]) -> int:
    best = 0
    for attempt in history:
        grade = attempt["graded"]
        if is_clean_success(attempt):
            best = max(best, 3 if attempt["kind"] in NOVEL_KINDS else 2)
        elif grade["outcome"] in ("correct", "partial"):
            best = max(best, 1)
    return best


def is_durable(topic: dict, history: list[dict]) -> bool:
    created = dt.date.fromisoformat(topic["created"])
    for attempt in history:
        answered = dt.date.fromisoformat(attempt["graded"]["at"][:10])
        if (
            is_clean_success(attempt)
            and (answered - created).days >= DURABLE_AFTER_DAYS
        ):
            return True
    return False


def require_topic(data: dict, topic_id: str) -> dict:
    topic = data["topics"].get(topic_id)
    if topic is None:
        known = ", ".join(sorted(data["topics"])) or "(none yet)"
        raise RecordError(f"No topic {topic_id!r}. Known topics: {known}")
    return topic
