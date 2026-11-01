#!/usr/bin/env python3
"""Keep the learner's record: topics, attempts, the review schedule, and the map.

Every write goes through this script so the record stays valid and the schedule
is computed the same way every time. Claude never edits the data files by hand.

Data lives in one directory (default `.learning/` under the current directory,
override with --dir or the LEARNING_DIR environment variable):

  topics.json     the dimensions the learner cares about, and one entry per topic
  attempts.jsonl  append-only: an `ask` line when a question is posed (with the
                  rubric fixed in advance), and a `grade` line when it is graded

Commands:
  init      [--dimensions a,b,c]
  topic     add --id ID --dimension D --concept TEXT [--anchor PATH ...]
  topic     retire --id ID --reason TEXT
  ask       --topic ID --kind KIND --question TEXT --rubric TEXT
  grade     --attempt N --outcome O --hint H --confidence C --answer TEXT [--gap TEXT]
  due       [--limit N]
  map
  check

Only the standard library is used. Python 3.9 or later.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
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
        if a["kind"] in SCHEDULED_KINDS and a["graded"]["outcome"] != "skipped"
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


# ---------------------------------------------------------------- commands


def cmd_init(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    if (root / "topics.json").exists():
        raise RecordError(f"{root}/topics.json already exists. Nothing was changed.")
    dims = (
        [d.strip() for d in args.dimensions.split(",")]
        if args.dimensions
        else DEFAULT_DIMENSIONS
    )
    dims = [d for d in dims if d]
    if not dims:
        raise RecordError(
            "--dimensions was empty. Pass a comma-separated list, or omit it."
        )
    root.mkdir(parents=True, exist_ok=True)
    save_topics(
        root, {"schema_version": SCHEMA_VERSION, "dimensions": dims, "topics": {}}
    )
    (root / "attempts.jsonl").touch()
    print(f"Created {root}/ with dimensions: {', '.join(dims)}")
    print(
        "Commit this directory, or it is lost when the session's container is reclaimed."
    )


def require_topic(data: dict, topic_id: str) -> dict:
    topic = data["topics"].get(topic_id)
    if topic is None:
        known = ", ".join(sorted(data["topics"])) or "(none yet)"
        raise RecordError(f"No topic {topic_id!r}. Known topics: {known}")
    return topic


def cmd_topic_add(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    if args.id in data["topics"]:
        raise RecordError(
            f"Topic {args.id!r} already exists. Pick another id or reuse it."
        )
    if args.dimension not in data["dimensions"]:
        raise RecordError(
            f"Dimension {args.dimension!r} is not in this record. "
            f"Available: {', '.join(data['dimensions'])}. "
            "If the learner agrees a new one is needed, run `topic add-dimension --name NAME`."
        )
    missing = [a for a in args.anchor or [] if not Path(a).exists()]
    if missing:
        raise RecordError(f"Anchor paths do not exist: {', '.join(missing)}")
    data["topics"][args.id] = {
        "dimension": args.dimension,
        "concept": args.concept,
        "anchors": args.anchor or [],
        "created": today(args.today).isoformat(),
        "status": "active",
    }
    save_topics(root, data)
    print(
        f"Added topic {args.id} ({args.dimension}). First review due in {INTERVAL_AFTER_MISS} day."
    )


def cmd_topic_dimension(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    if args.name in data["dimensions"]:
        raise RecordError(f"Dimension {args.name!r} already exists.")
    data["dimensions"].append(args.name)
    save_topics(root, data)
    print(f"Added dimension {args.name}.")


def cmd_topic_retire(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    topic = require_topic(data, args.id)
    topic["status"] = "retired"
    topic["retired_reason"] = args.reason
    save_topics(root, data)
    print(f"Retired topic {args.id}: {args.reason}")


def cmd_ask(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    topic = require_topic(data, args.topic)
    if topic["status"] != "active":
        raise RecordError(f"Topic {args.topic!r} is retired. Add a new topic instead.")
    if not args.rubric.strip():
        raise RecordError(
            "--rubric is empty. Write the expected answer points before asking."
        )
    attempts = build_attempts(load_events(root))
    open_ones = [str(n) for n, a in attempts.items() if not a["graded"]]
    if open_ones:
        raise RecordError(
            f"Attempt(s) {', '.join(open_ones)} are still ungraded. Grade each one first; "
            "use --outcome skipped if the learner never answered."
        )
    number = max(attempts, default=0) + 1
    append_event(
        root,
        {
            "event": "ask",
            "attempt": number,
            "topic": args.topic,
            "kind": args.kind,
            "question": args.question,
            "rubric": args.rubric,
            "at": now_stamp(args.today),
        },
    )
    print(f"Attempt {number} recorded. Ask the question now; do not show the rubric.")


def cmd_grade(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    attempts = build_attempts(load_events(root))
    attempt = attempts.get(args.attempt)
    if attempt is None:
        raise RecordError(
            f"No attempt {args.attempt}. Run `ask` first; it prints the number."
        )
    if attempt["graded"]:
        raise RecordError(
            f"Attempt {args.attempt} is already graded. Ask a new question instead."
        )
    if args.outcome == "correct" and args.hint == 3:
        raise RecordError(
            "Hint level 3 means the answer was given. Grade it partial or wrong, not correct."
        )
    append_event(
        root,
        {
            "event": "grade",
            "attempt": args.attempt,
            "outcome": args.outcome,
            "hint": args.hint,
            "confidence": args.confidence,
            "answer": args.answer,
            "gap": args.gap or "",
            "at": now_stamp(args.today),
        },
    )
    data = load_topics(root)
    topic = data["topics"][attempt["topic"]]
    history = scheduled_history(build_attempts(load_events(root)), attempt["topic"])
    print(f"Graded attempt {args.attempt}: {args.outcome}, hint H{args.hint}.")
    print(f"Next review of {attempt['topic']}: {next_due(topic, history).isoformat()}")


def interleave(rows: list[tuple]) -> list[tuple]:
    """Round-robin across dimensions so one session mixes kinds of problem."""
    by_dim: dict[str, list[tuple]] = {}
    for row in rows:
        by_dim.setdefault(row[2], []).append(row)
    ordered = []
    while any(by_dim.values()):
        for dim in list(by_dim):
            if by_dim[dim]:
                ordered.append(by_dim[dim].pop(0))
    return ordered


def due_rows(data: dict, attempts: dict[int, dict], now: dt.date) -> list[tuple]:
    rows = []
    for topic_id, topic in data["topics"].items():
        if topic["status"] != "active":
            continue
        history = scheduled_history(attempts, topic_id)
        due = next_due(topic, history)
        if due <= now:
            rows.append(
                ((now - due).days, topic_id, topic["dimension"], topic, history)
            )
    rows.sort(key=lambda r: -r[0])
    return rows


def print_due(row: tuple) -> None:
    overdue, topic_id, dim, topic, history = row
    suggestion = "retrieval" if success_streak(history) == 0 else "transfer"
    print(
        f"- {topic_id} [{dim}] overdue {overdue}d, {len(history)} prior review(s), "
        f"level: {LEVEL_NAMES[level(history)]}, suggested kind: {suggestion}"
    )
    print(f"    concept: {topic['concept']}")
    for anchor in topic["anchors"]:
        missing = not Path(anchor).exists()
        flag = "  (MISSING: re-locate or retire the topic)" if missing else ""
        print(f"    anchor: {anchor}{flag}")


def cmd_due(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    attempts = build_attempts(load_events(root))
    for attempt in attempts.values():
        if not attempt["graded"]:
            print(
                f"UNGRADED attempt {attempt['attempt']} on {attempt['topic']}: grade it "
                "(--outcome skipped if never answered) before asking anything new."
            )
    rows = due_rows(data, attempts, today(args.today))
    chosen = interleave(rows)[: args.limit]
    if not chosen:
        print("Nothing due.")
        return
    print(f"{len(rows)} topic(s) due; showing {len(chosen)}.")
    for row in chosen:
        print_due(row)


def is_confident_miss(attempt: dict) -> bool:
    grade = attempt["graded"]
    return grade["confidence"] == "high" and grade["outcome"] == "wrong"


def summarize_dimension(
    dim: str, topics: list[tuple], attempts: dict[int, dict]
) -> str:
    counts = {name: 0 for name in LEVEL_NAMES.values()}
    durable = 0
    overconfident = 0
    for tid, topic in topics:
        history = scheduled_history(attempts, tid)
        counts[LEVEL_NAMES[level(history)]] += 1
        durable += is_durable(topic, history)
        overconfident += sum(1 for a in history if is_confident_miss(a))
    spread = ", ".join(f"{n} {name}" for name, n in counts.items() if n)
    return (
        f"{dim}: {len(topics)} topic(s): {spread}; durable {durable}; "
        f"confident-and-wrong {overconfident}"
    )


def dimension_rows(data: dict, attempts: dict[int, dict]) -> list[str]:
    lines = []
    for dim in data["dimensions"]:
        topics = [
            (tid, t)
            for tid, t in data["topics"].items()
            if t["dimension"] == dim and t["status"] == "active"
        ]
        if topics:
            lines.append(summarize_dimension(dim, topics, attempts))
        else:
            lines.append(f"{dim}: no evidence yet")
    return lines


def interval_rows(attempts: dict[int, dict], data: dict) -> list[str]:
    """Success rate by how many clean successes preceded the review."""
    tallies: dict[int, list[int]] = {}
    for tid in data["topics"]:
        history = scheduled_history(attempts, tid)
        streak = 0
        for attempt in history:
            hit = is_clean_success(attempt)
            bucket = tallies.setdefault(streak, [0, 0])
            bucket[0] += hit
            bucket[1] += 1
            streak = streak + 1 if hit else 0
    lines = []
    for streak in sorted(tallies):
        hits, total = tallies[streak]
        gap = (
            "first review or after a miss"
            if streak == 0
            else f"after {INTERVALS_AFTER_SUCCESS[min(streak, len(INTERVALS_AFTER_SUCCESS)) - 1]}d gap"
        )
        lines.append(f"  {gap}: {hits}/{total} unassisted correct")
    return lines


def cmd_map(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    attempts = build_attempts(load_events(root))
    print(
        "Levels: not yet < with help < recalls (known case, no hints) < transfers (novel case, no hints)"
    )
    print(
        "Durable: an unassisted correct answer at least a week after the topic was recorded."
    )
    print()
    for line in dimension_rows(data, attempts):
        print(line)
    rates = interval_rows(attempts, data)
    if rates:
        print()
        print(
            "Schedule check (if late steps fail often, the gaps are too long for this learner):"
        )
        for line in rates:
            print(line)
    gaps = [
        (a["topic"], a["graded"]["gap"])
        for a in attempts.values()
        if a["graded"] and a["graded"]["gap"]
    ]
    if gaps:
        print()
        print("Most recent recorded gaps:")
        for topic_id, gap in gaps[-5:]:
            print(f"  {topic_id}: {gap}")


def check_ask(event: dict, data: dict, asked: set[int]) -> list[str]:
    number = event.get("attempt")
    problems = []
    if number in asked:
        problems.append(f"attempt {number} asked twice")
    if event.get("topic") not in data["topics"]:
        problems.append(f"attempt {number} names unknown topic {event.get('topic')!r}")
    if event.get("kind") not in KINDS:
        problems.append(f"attempt {number} has unknown kind {event.get('kind')!r}")
    asked.add(number)
    return problems


def check_grade(event: dict, asked: set[int], graded: set[int]) -> list[str]:
    number = event.get("attempt")
    problems = []
    if number not in asked:
        problems.append(f"grade for attempt {number} has no ask before it")
    if number in graded:
        problems.append(f"attempt {number} graded twice")
    graded.add(number)
    return problems


def check_attempts(data: dict, events: list[dict]) -> list[str]:
    problems = []
    asked: set[int] = set()
    graded: set[int] = set()
    for event in events:
        kind = event.get("event")
        if kind == "ask":
            problems += check_ask(event, data, asked)
        elif kind == "grade":
            problems += check_grade(event, asked, graded)
        else:
            problems.append(f"unknown event {kind!r}")
    return problems


def cmd_check(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    problems = check_attempts(data, load_events(root))
    for tid, topic in data["topics"].items():
        if topic["dimension"] not in data["dimensions"]:
            problems.append(
                f"topic {tid} names unknown dimension {topic['dimension']!r}"
            )
    if problems:
        for problem in problems:
            print(f"PROBLEM: {problem}")
        raise SystemExit(1)
    print(f"OK: {len(data['topics'])} topic(s), {len(load_events(root))} event(s).")


# ---------------------------------------------------------------- cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dir", help="record directory (default .learning or $LEARNING_DIR)"
    )
    parser.add_argument("--today", help="override today's date, YYYY-MM-DD")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument(
        "--dimensions",
        help=f"comma-separated; default: {','.join(DEFAULT_DIMENSIONS)}",
    )
    p.set_defaults(func=cmd_init)

    topic = sub.add_parser("topic").add_subparsers(dest="topic_command", required=True)
    p = topic.add_parser("add")
    p.add_argument("--id", required=True)
    p.add_argument("--dimension", required=True)
    p.add_argument("--concept", required=True)
    p.add_argument("--anchor", action="append", help="repository path; repeatable")
    p.set_defaults(func=cmd_topic_add)
    p = topic.add_parser("add-dimension")
    p.add_argument("--name", required=True)
    p.set_defaults(func=cmd_topic_dimension)
    p = topic.add_parser("retire")
    p.add_argument("--id", required=True)
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_topic_retire)

    p = sub.add_parser("ask")
    p.add_argument("--topic", required=True)
    p.add_argument("--kind", required=True, choices=KINDS)
    p.add_argument("--question", required=True)
    p.add_argument("--rubric", required=True)
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("grade")
    p.add_argument("--attempt", required=True, type=int)
    p.add_argument("--outcome", required=True, choices=OUTCOMES)
    p.add_argument("--hint", required=True, type=int, choices=HINT_LEVELS)
    p.add_argument("--confidence", required=True, choices=CONFIDENCES)
    p.add_argument("--answer", required=True, help="the learner's answer, paraphrased")
    p.add_argument("--gap", help="what was missing or wrong, in one line")
    p.set_defaults(func=cmd_grade)

    p = sub.add_parser("due")
    p.add_argument("--limit", type=int, default=DEFAULT_DUE_LIMIT)
    p.set_defaults(func=cmd_due)

    sub.add_parser("map").set_defaults(func=cmd_map)
    sub.add_parser("check").set_defaults(func=cmd_check)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except RecordError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
