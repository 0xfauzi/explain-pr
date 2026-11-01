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
  import    --file RESULTS.jsonl   (results pasted from an explainer page)
  due       [--limit N]
  map
  check

Only the standard library is used. Python 3.9 or later.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from record import (
    CONFIDENCES,
    DEFAULT_DIMENSIONS,
    DEFAULT_DUE_LIMIT,
    HINT_LEVELS,
    INTERVAL_AFTER_MISS,
    INTERVALS_AFTER_SUCCESS,
    KINDS,
    LEVEL_NAMES,
    OUTCOMES,
    SCHEMA_VERSION,
    RecordError,
    append_event,
    build_attempts,
    data_dir,
    graded_for_topic,
    is_clean_success,
    is_durable,
    level,
    load_events,
    load_topics,
    next_due,
    now_stamp,
    require_topic,
    save_topics,
    scheduled_history,
    success_streak,
    today,
)

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


IMPORT_FIELDS = [
    "topic",
    "id",
    "kind",
    "grader",
    "question",
    "rubric",
    "answer",
    "outcome",
    "confidence",
]


def parse_import_line(number: int, line: str, data: dict) -> dict:
    try:
        row = json.loads(line)
    except json.JSONDecodeError as exc:
        raise RecordError(
            f"line {number} is not JSON ({exc}). Ask the learner to copy the box again."
        ) from exc
    missing = [f for f in IMPORT_FIELDS if f not in row]
    if missing:
        raise RecordError(f"line {number} lacks {', '.join(missing)}")
    require_topic(data, row["topic"])
    checks = [
        ("kind", KINDS),
        ("grader", ["page", "self"]),
        ("outcome", OUTCOMES),
        ("confidence", CONFIDENCES),
    ]
    for field, allowed in checks:
        if row[field] not in allowed:
            raise RecordError(
                f"line {number}: {field} {row[field]!r} is not one of {allowed}"
            )
    return row


def cmd_import(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_topics(root)
    source = (
        sys.stdin.read()
        if args.file == "-"
        else Path(args.file).read_text(encoding="utf-8")
    )
    rows = [
        parse_import_line(n, line, data)
        for n, line in enumerate(source.splitlines(), 1)
        if line.strip()
    ]
    attempts = build_attempts(load_events(root))
    already = {(a["topic"], a.get("page_id"), a["question"]) for a in attempts.values()}
    number = max(attempts, default=0)
    added: list[dict] = []
    for row in rows:
        if (row["topic"], row["id"], row["question"]) in already:
            continue
        number += 1
        stamp = now_stamp(args.today)
        append_event(
            root,
            {
                "event": "ask",
                "attempt": number,
                "topic": row["topic"],
                "kind": row["kind"],
                "question": row["question"],
                "rubric": row["rubric"],
                "page_id": row["id"],
                "at": stamp,
            },
        )
        append_event(
            root,
            {
                "event": "grade",
                "attempt": number,
                "outcome": row["outcome"],
                "hint": 0,
                "confidence": row["confidence"],
                "answer": row["answer"][:400],
                "gap": ""
                if row["outcome"] == "correct"
                else f"page: {row['question'][:120]}",
                "grader": row["grader"],
                "at": stamp,
            },
        )
        added.append(row)
    print(
        f"Imported {len(added)} result(s); skipped {len(rows) - len(added)} already recorded."
    )
    confident_misses = [
        r for r in added if r["confidence"] == "high" and r["outcome"] == "wrong"
    ]
    for row in confident_misses:
        print(
            f"MISCONCEPTION to discuss: {row['question'][:100]} (answered: {row['answer'][:80]})"
        )


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
        overconfident += sum(
            1 for a in graded_for_topic(attempts, tid) if is_confident_miss(a)
        )
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

    p = sub.add_parser("import")
    p.add_argument(
        "--file",
        required=True,
        help="JSON lines from an explainer page, or - for stdin",
    )
    p.set_defaults(func=cmd_import)

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
