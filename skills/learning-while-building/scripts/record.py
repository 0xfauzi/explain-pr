"""The learner's record as data: constants, storage, attempts and the schedule.

learning.py is the command line over this module. Kept separate so the
schedule rules can be read in one place, and imported by a test or a script
without running the CLI.

Storage is one file per thing, so that separate sessions on separate branches
add separate files and git merges them without conflict:

  .learning/dimensions.json        the dimensions the learner cares about
  .learning/topics/<id>.json       one per topic
  .learning/attempts/<id>.json     one per attempt; the grade is added to it

Attempt ids are a timestamp plus random hex, never "highest number plus one",
which two sessions starting from the same commit would both compute. The only
conflicts left are real ones (the same topic or attempt changed on two
branches); git reports those, and load_record names the file and how to resolve.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import secrets
from pathlib import Path

SCHEMA_VERSION = 2

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
# "unknown" when the learner gave no confidence. Recorded as missing, never guessed.
CONFIDENCES = ["low", "medium", "high", "unknown"]
HINT_LEVELS = [0, 1, 2, 3]

# Who graded an attempt. Only "claude" grades count toward levels and the review
# schedule: the learner produced an answer and it was judged against a rubric
# fixed beforehand, or Claude inspected an artifact of real work. "page" results
# are recognition (multiple choice, ordering); "self" is self-assessment or a
# self-report with nothing to inspect. Both are kept, and inform misconceptions
# and gaps, but do not move a topic up.
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

TOPIC_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
CONFLICT_MARKER = re.compile(r"^(<{7}|={7}|>{7})( |$)", re.MULTILINE)


class RecordError(Exception):
    """A problem the caller can fix. The message says how."""


# ---------------------------------------------------------------- time


def today(arg: str | None) -> dt.date:
    if not arg:
        return dt.datetime.now().astimezone().date()
    try:
        return dt.date.fromisoformat(arg)
    except ValueError as exc:
        raise RecordError(f"--today must be YYYY-MM-DD, got {arg!r}") from exc


def now_stamp(today_arg: str | None) -> str:
    """Local time with microseconds, so two writes in one second still order.

    With --today (testing and back-dating), the date is replaced and the real
    time of day is kept for the same reason.
    """
    now = dt.datetime.now().astimezone().replace(tzinfo=None)
    if today_arg:
        now = dt.datetime.combine(today(today_arg), now.time())
    return now.isoformat()


def new_attempt_id(stamp: str) -> str:
    # 24 random bits on top of a microsecond timestamp. Two sessions would have
    # to start an attempt in the same microsecond and draw the same 6 hex digits.
    compact = re.sub(r"[^0-9]", "", stamp)[:14]
    return f"{compact[:8]}T{compact[8:]}-{secrets.token_hex(3)}"


# ---------------------------------------------------------------- storage


def data_dir(arg: str | None) -> Path:
    return Path(arg or os.environ.get("LEARNING_DIR") or ".learning")


def read_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if CONFLICT_MARKER.search(text):
        raise RecordError(conflict_help(path))
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RecordError(
            f"{path} is not valid JSON ({exc}). Restore it from git."
        ) from exc


def conflict_help(path: Path) -> str:
    kind = path.parent.name
    if kind == "attempts":
        how = (
            "The same attempt was graded on two branches. Keep the side with the "
            "EARLIER grade timestamp: the learner's first answer is the attempt."
        )
    elif kind == "topics":
        how = (
            "The same topic was added or changed on two branches. If both sides "
            "describe the same concept, keep one (prefer the retired side if one "
            "retired it). If they are different concepts, keep one here and add the "
            "other under a new id with `topic add`."
        )
    else:
        how = "Both branches changed the dimensions. Keep the union of both lists."
    return (
        f"{path} has unresolved git merge conflict markers. {how} "
        "Remove the markers, save valid JSON, then run `learning.py check`."
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_v2(root: Path) -> None:
    if (root / "dimensions.json").exists():
        return
    if (root / "topics.json").exists():
        raise RecordError(
            f"{root}/ uses the old single-file format. Run `learning.py migrate` once "
            "to convert it, then commit the result."
        )
    raise RecordError(
        f"No record at {root}/. Run `learning.py init` from the repository root first, "
        "or pass --dir to point at an existing record."
    )


def load_record(root: Path) -> dict:
    """Dimensions and topics: {"dimensions": [...], "topics": {id: topic}}."""
    require_v2(root)
    head = read_json(root / "dimensions.json")
    if head.get("schema_version") != SCHEMA_VERSION:
        raise RecordError(
            f"{root}/dimensions.json has schema_version {head.get('schema_version')!r}; "
            f"this script reads {SCHEMA_VERSION}."
        )
    topics = {p.stem: read_json(p) for p in sorted((root / "topics").glob("*.json"))}
    return {"dimensions": head["dimensions"], "topics": topics}


def save_dimensions(root: Path, dimensions: list[str]) -> None:
    write_json(
        root / "dimensions.json",
        {"schema_version": SCHEMA_VERSION, "dimensions": dimensions},
    )


def save_topic(root: Path, topic_id: str, topic: dict) -> None:
    write_json(root / "topics" / f"{topic_id}.json", topic)


def load_attempts(root: Path) -> dict[str, dict]:
    """Every attempt, keyed by id. `graded` is None until graded."""
    attempts = {}
    for path in sorted((root / "attempts").glob("*.json")):
        attempt = read_json(path)
        attempt.setdefault("graded", None)
        attempts[path.stem] = attempt
    return attempts


def save_attempt(root: Path, attempt: dict) -> None:
    write_json(root / "attempts" / f"{attempt['id']}.json", attempt)


def find_attempt(attempts: dict[str, dict], ref: str) -> dict:
    """Exact id, or a unique prefix or suffix of one."""
    if ref in attempts:
        return attempts[ref]
    hits = [a for k, a in attempts.items() if k.startswith(ref) or k.endswith(ref)]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise RecordError(f"No attempt {ref!r}. Run `ask` first; it prints the id.")
    raise RecordError(f"{ref!r} matches {len(hits)} attempts; give more of the id.")


# ---------------------------------------------------------------- attempts


def graded_for_topic(attempts: dict[str, dict], topic_id: str) -> list[dict]:
    rows = [a for a in attempts.values() if a["topic"] == topic_id and a["graded"]]
    return sorted(rows, key=lambda a: (a["graded"]["at"], a["id"]))


def is_clean_success(attempt: dict) -> bool:
    grade = attempt["graded"]
    return grade["outcome"] == "correct" and grade["hint"] == 0


def scheduled_history(attempts: dict[str, dict], topic_id: str) -> list[dict]:
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


def answered_on(attempt: dict) -> dt.date:
    return dt.date.fromisoformat(attempt["graded"]["at"][:10])


def next_due(topic: dict, history: list[dict]) -> dt.date:
    if not history:
        return dt.date.fromisoformat(topic["created"]) + dt.timedelta(
            days=INTERVAL_AFTER_MISS
        )
    last = answered_on(history[-1])
    streak = success_streak(history)
    if streak == 0:
        return last + dt.timedelta(days=INTERVAL_AFTER_MISS)
    step = min(streak, len(INTERVALS_AFTER_SUCCESS)) - 1
    return last + dt.timedelta(days=INTERVALS_AFTER_SUCCESS[step])


def attempt_level(attempt: dict) -> int:
    if is_clean_success(attempt):
        return 3 if attempt["kind"] in NOVEL_KINDS else 2
    if attempt["graded"]["outcome"] in ("correct", "partial"):
        return 1
    return 0


def level(history: list[dict]) -> int:
    """Highest level ever demonstrated. A historical fact, not current ability."""
    return max((attempt_level(a) for a in history), default=0)


def highest_reached(history: list[dict]) -> tuple[int, dt.date | None]:
    """The highest level and the date it was first reached."""
    best, when = 0, None
    for attempt in history:
        reached = attempt_level(attempt)
        if reached > best:
            best, when = reached, answered_on(attempt)
    return best, when


def describe_miss(grade: dict) -> str:
    if grade["outcome"] == "correct":
        return f"correct only with hint H{grade['hint']}"
    if grade["hint"]:
        return f"{grade['outcome']} even with hint H{grade['hint']}"
    return f"{grade['outcome']}, unaided"


def current_evidence(topic: dict, history: list[dict], now: dt.date) -> str:
    """A plain reading of the latest evidence, separate from the historical best.

    The rule, in order: no graded reviews means no evidence; a latest answer that
    was not an unaided correct one makes the topic uncertain, whatever came
    before; a review that is overdue means the last success is unverified; else
    the topic is holding.
    """
    if not history:
        return "no reviewed answers yet"
    last = history[-1]
    when = answered_on(last).isoformat()
    if not is_clean_success(last):
        return f"uncertain: latest review was {describe_miss(last['graded'])} ({when})"
    if next_due(topic, history) < now:
        return f"unverified: last unaided correct {when}, review overdue"
    return f"holding: unaided correct {when}"


def durable_since(topic: dict, history: list[dict]) -> dt.date | None:
    created = dt.date.fromisoformat(topic["created"])
    for attempt in history:
        answered = answered_on(attempt)
        if (
            is_clean_success(attempt)
            and (answered - created).days >= DURABLE_AFTER_DAYS
        ):
            return answered
    return None


def is_durable(topic: dict, history: list[dict]) -> bool:
    return durable_since(topic, history) is not None


def require_topic(data: dict, topic_id: str) -> dict:
    topic = data["topics"].get(topic_id)
    if topic is None:
        known = ", ".join(sorted(data["topics"])) or "(none yet)"
        raise RecordError(f"No topic {topic_id!r}. Known topics: {known}")
    return topic
