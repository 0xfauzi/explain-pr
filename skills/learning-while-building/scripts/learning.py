#!/usr/bin/env python3
"""Keep the learner's record: topics, attempts, the review schedule, and the map.

Every write goes through this script so the record stays valid and the schedule
is computed the same way every time. Claude never edits the data files by hand.

Data lives in one directory (default `.learning/` under the current directory,
override with --dir or the LEARNING_DIR environment variable), one file per
topic and per attempt; see record.py for the layout and why.

Commands:
  init      [--dimensions a,b,c]
  topic     add --id ID --dimension D --concept TEXT [--anchor PATH ...]
  topic     add-dimension --name D
  topic     retire --id ID --reason TEXT
  ask       --topic ID --kind KIND --question TEXT --rubric TEXT
  grade     --attempt ID --outcome O --hint H --confidence C --answer TEXT
            [--gap TEXT] [--evidence REF]
  import    --file RESULTS.jsonl   (results pasted from an explainer page)
  due       [--limit N]
  map
  check
  migrate   (convert a record from the old single-file format)

Only the standard library is used. Python 3.9 or later.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from record import (
    CONFIDENCES,
    DEFAULT_DIMENSIONS,
    DEFAULT_DUE_LIMIT,
    GRADERS,
    HINT_LEVELS,
    INTERVAL_AFTER_MISS,
    INTERVALS_AFTER_SUCCESS,
    KINDS,
    LEVEL_NAMES,
    OUTCOMES,
    TOPIC_ID,
    RecordError,
    current_evidence,
    data_dir,
    durable_since,
    find_attempt,
    graded_for_topic,
    highest_reached,
    is_clean_success,
    is_durable,
    level,
    load_attempts,
    load_record,
    new_attempt_id,
    next_due,
    now_stamp,
    read_json,
    require_topic,
    save_attempt,
    save_dimensions,
    save_topic,
    scheduled_history,
    success_streak,
    today,
)

# ---------------------------------------------------------------- git


def git(*args: str) -> str | None:
    try:
        done = subprocess.run(
            ["git", *args], capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def branch_note() -> None:
    """Say when a write lands on a branch other sessions cannot see yet."""
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    default = (
        git("symbolic-ref", "--short", "refs/remotes/origin/HEAD") or ""
    ).removeprefix("origin/")
    if branch and default and branch != default:
        print(
            f"Note: recorded on branch {branch}. Sessions on other branches see this only "
            f"after {branch} is pushed and merged into {default}."
        )


# ---------------------------------------------------------------- commands


def cmd_init(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    if (root / "dimensions.json").exists() or (root / "topics.json").exists():
        raise RecordError(f"{root}/ already holds a record. Nothing was changed.")
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
    save_dimensions(root, dims)
    for sub in ("topics", "attempts"):
        (root / sub).mkdir(parents=True, exist_ok=True)
        (root / sub / ".gitkeep").touch()
    print(f"Created {root}/ with dimensions: {', '.join(dims)}")
    print(
        "Commit and push this directory, or it is lost when the session's container is reclaimed."
    )


def cmd_topic_add(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    if not TOPIC_ID.match(args.id):
        raise RecordError(
            f"Topic id {args.id!r} must be lowercase letters, digits and hyphens."
        )
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
    topic = {
        "dimension": args.dimension,
        "concept": args.concept,
        "anchors": args.anchor or [],
        "created": today(args.today).isoformat(),
        "status": "active",
    }
    save_topic(root, args.id, topic)
    print(
        f"Added topic {args.id} ({args.dimension}). First review due in {INTERVAL_AFTER_MISS} day."
    )
    branch_note()


def cmd_topic_dimension(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    if args.name in data["dimensions"]:
        raise RecordError(f"Dimension {args.name!r} already exists.")
    save_dimensions(root, data["dimensions"] + [args.name])
    print(f"Added dimension {args.name}.")


def cmd_topic_retire(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    topic = require_topic(data, args.id)
    topic["status"] = "retired"
    topic["retired_reason"] = args.reason
    save_topic(root, args.id, topic)
    print(f"Retired topic {args.id}: {args.reason}")


def cmd_ask(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    topic = require_topic(data, args.topic)
    if topic["status"] != "active":
        raise RecordError(f"Topic {args.topic!r} is retired. Add a new topic instead.")
    if not args.rubric.strip():
        raise RecordError(
            "--rubric is empty. Write the expected answer points before asking."
        )
    open_ones = [
        f"{k} ({a['topic']})" for k, a in load_attempts(root).items() if not a["graded"]
    ]
    if open_ones:
        raise RecordError(
            f"Still ungraded: {', '.join(open_ones)}. Grade each one first; "
            "use --outcome skipped if the learner never answered."
        )
    stamp = now_stamp(args.today)
    attempt = {
        "id": new_attempt_id(stamp),
        "topic": args.topic,
        "kind": args.kind,
        "question": args.question,
        "rubric": args.rubric,
        "at": stamp,
        "graded": None,
    }
    save_attempt(root, attempt)
    print(
        f"Attempt {attempt['id']} recorded. Ask the question now; do not show the rubric."
    )


def grader_for(attempt: dict, evidence: str) -> str:
    """A field report counts only when Claude has something real to inspect."""
    if attempt["kind"] == "field" and not evidence:
        return "self"
    return "claude"


def cmd_grade(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    attempt = find_attempt(load_attempts(root), args.attempt)
    if attempt["graded"]:
        raise RecordError(
            f"Attempt {attempt['id']} is already graded. Ask a new question instead."
        )
    if args.outcome == "correct" and args.hint == 3:
        raise RecordError(
            "Hint level 3 means the answer was given. Grade it partial or wrong, not correct."
        )
    evidence = (args.evidence or "").strip()
    attempt["graded"] = {
        "outcome": args.outcome,
        "hint": args.hint,
        "confidence": args.confidence,
        "answer": args.answer,
        "gap": args.gap or "",
        "evidence": evidence,
        "grader": grader_for(attempt, evidence),
        "at": now_stamp(args.today),
    }
    save_attempt(root, attempt)
    data = load_record(root)
    topic = data["topics"][attempt["topic"]]
    history = scheduled_history(load_attempts(root), attempt["topic"])
    print(f"Graded {attempt['id']}: {args.outcome}, hint H{args.hint}.")
    if attempt["graded"]["grader"] == "self":
        print(
            "Self-report recorded; independent capability not verified, so levels are "
            "unchanged. One artifact (a commit, PR, test output or trace) that Claude has "
            "inspected would count: record a new field attempt with --evidence."
        )
    print(f"Next review of {attempt['topic']}: {next_due(topic, history).isoformat()}")
    branch_note()


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


def imported_attempt(row: dict, stamp: str) -> dict:
    return {
        "id": new_attempt_id(stamp),
        "topic": row["topic"],
        "kind": row["kind"],
        "question": row["question"],
        "rubric": row["rubric"],
        "page_id": row["id"],
        "at": stamp,
        "graded": {
            "outcome": row["outcome"],
            "hint": 0,
            "confidence": row["confidence"],
            "answer": row["answer"][:400],
            "gap": ""
            if row["outcome"] == "correct"
            else f"page: {row['question'][:120]}",
            "evidence": "",
            "grader": row["grader"],
            "at": stamp,
        },
    }


def cmd_import(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
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
    already = {
        (a["topic"], a.get("page_id"), a["question"])
        for a in load_attempts(root).values()
    }
    added: list[dict] = []
    for row in rows:
        if (row["topic"], row["id"], row["question"]) in already:
            continue
        save_attempt(root, imported_attempt(row, now_stamp(args.today)))
        added.append(row)
    print(
        f"Imported {len(added)} result(s); skipped {len(rows) - len(added)} already recorded."
    )
    for row in added:
        if row["confidence"] == "high" and row["outcome"] == "wrong":
            print(
                f"MISCONCEPTION to discuss: {row['question'][:100]} (answered: {row['answer'][:80]})"
            )
    if added:
        branch_note()


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


def due_rows(data: dict, attempts: dict[str, dict], now: dt.date) -> list[tuple]:
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


def print_due(row: tuple, now: dt.date) -> None:
    overdue, topic_id, dim, topic, history = row
    suggestion = "retrieval" if success_streak(history) == 0 else "transfer"
    print(
        f"- {topic_id} [{dim}] overdue {overdue}d, {len(history)} prior review(s), "
        f"highest: {LEVEL_NAMES[level(history)]}, suggested kind: {suggestion}"
    )
    print(f"    current: {current_evidence(topic, history, now)}")
    print(f"    concept: {topic['concept']}")
    for anchor in topic["anchors"]:
        missing = not Path(anchor).exists()
        flag = "  (MISSING: re-locate or retire the topic)" if missing else ""
        print(f"    anchor: {anchor}{flag}")


def cmd_due(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    attempts = load_attempts(root)
    for attempt in attempts.values():
        if not attempt["graded"]:
            print(
                f"UNGRADED attempt {attempt['id']} on {attempt['topic']}: grade it "
                "(--outcome skipped if never answered) before asking anything new."
            )
    now = today(args.today)
    rows = due_rows(data, attempts, now)
    chosen = interleave(rows)[: args.limit]
    if not chosen:
        print("Nothing due.")
        return
    print(f"{len(rows)} topic(s) due; showing {len(chosen)}.")
    for row in chosen:
        print_due(row, now)


def is_confident_miss(attempt: dict) -> bool:
    grade = attempt["graded"]
    return grade["confidence"] == "high" and grade["outcome"] == "wrong"


def topic_lines(
    topic_id: str, topic: dict, attempts: dict[str, dict], now: dt.date
) -> list[str]:
    history = scheduled_history(attempts, topic_id)
    best, reached = highest_reached(history)
    durable = durable_since(topic, history)
    everything = graded_for_topic(attempts, topic_id)
    confident_misses = sum(1 for a in everything if is_confident_miss(a))
    self_reports = sum(
        1
        for a in everything
        if a["kind"] == "field" and a["graded"]["grader"] == "self"
    )
    lines = [
        f"  {topic_id}: {topic['concept']}",
        f"    highest demonstrated: {LEVEL_NAMES[best]}"
        + (f" ({reached})" if reached else ""),
        f"    current evidence: {current_evidence(topic, history, now)}",
        f"    durable retention: {durable if durable else 'not yet demonstrated'}",
        f"    next review: {next_due(topic, history).isoformat()}",
    ]
    if confident_misses:
        lines.append(f"    confident-and-wrong answers: {confident_misses}")
    if self_reports:
        lines.append(f"    self-reported field work (not counted): {self_reports}")
    return lines


def dimension_lines(
    dim: str, data: dict, attempts: dict[str, dict], now: dt.date
) -> list[str]:
    topics = [
        (tid, t)
        for tid, t in data["topics"].items()
        if t["dimension"] == dim and t["status"] == "active"
    ]
    if not topics:
        return [f"{dim}: no evidence yet"]
    durable = sum(is_durable(t, scheduled_history(attempts, tid)) for tid, t in topics)
    lines = [f"{dim}: {len(topics)} topic(s), {durable} with durable retention"]
    for tid, topic in topics:
        lines += topic_lines(tid, topic, attempts, now)
    return lines


def interval_rows(attempts: dict[str, dict], data: dict) -> list[str]:
    """Success rate by how many clean successes preceded the review."""
    tallies: dict[int, list[int]] = {}
    for tid in data["topics"]:
        streak = 0
        for attempt in scheduled_history(attempts, tid):
            hit = is_clean_success(attempt)
            bucket = tallies.setdefault(streak, [0, 0])
            bucket[0] += hit
            bucket[1] += 1
            streak = streak + 1 if hit else 0
    lines = []
    for streak in sorted(tallies):
        hits, total = tallies[streak]
        step = INTERVALS_AFTER_SUCCESS[min(streak, len(INTERVALS_AFTER_SUCCESS)) - 1]
        gap = "first review or after a miss" if streak == 0 else f"after {step}d gap"
        lines.append(f"  {gap}: {hits}/{total} unassisted correct")
    return lines


def cmd_map(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    attempts = load_attempts(root)
    now = today(args.today)
    print("Highest demonstrated is the best answer ever given, a historical fact:")
    print(
        "  not yet < with help < recalls (known case, no hints) < transfers (new case, no hints)"
    )
    print("Current evidence reads only the latest review, so a later miss shows here.")
    print(
        "Durable retention: an unaided correct answer at least a week after the topic was added."
    )
    print()
    for dim in data["dimensions"]:
        for line in dimension_lines(dim, data, attempts, now):
            print(line)
    rates = interval_rows(attempts, data)
    if rates:
        print()
        print(
            "Schedule check (if late steps fail often, the gaps are too long for this learner):"
        )
        for line in rates:
            print(line)


def check_attempt(key: str, attempt: dict, data: dict) -> list[str]:
    problems = []
    if attempt.get("id") != key:
        problems.append(f"attempts/{key}.json holds id {attempt.get('id')!r}")
    if attempt.get("topic") not in data["topics"]:
        problems.append(f"attempt {key} names unknown topic {attempt.get('topic')!r}")
    if attempt.get("kind") not in KINDS:
        problems.append(f"attempt {key} has unknown kind {attempt.get('kind')!r}")
    grade = attempt.get("graded")
    if grade:
        for field, allowed in (
            ("outcome", OUTCOMES),
            ("confidence", CONFIDENCES),
            ("grader", GRADERS),
        ):
            if grade.get(field) not in allowed:
                problems.append(f"attempt {key} has {field} {grade.get(field)!r}")
        if grade.get("hint") not in HINT_LEVELS:
            problems.append(f"attempt {key} has hint {grade.get('hint')!r}")
    return problems


def cmd_check(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    attempts = load_attempts(root)
    problems = []
    for key, attempt in attempts.items():
        problems += check_attempt(key, attempt, data)
    for tid, topic in data["topics"].items():
        if topic.get("dimension") not in data["dimensions"]:
            problems.append(
                f"topic {tid} names unknown dimension {topic.get('dimension')!r}"
            )
    if problems:
        for problem in problems:
            print(f"PROBLEM: {problem}")
        raise SystemExit(1)
    print(f"OK: {len(data['topics'])} topic(s), {len(attempts)} attempt(s).")


def v1_attempts(lines: list[str]) -> dict[int, dict]:
    attempts: dict[int, dict] = {}
    for line in lines:
        if not line.strip():
            continue
        event = json.loads(line)
        number = event.pop("attempt")
        kind = event.pop("event")
        if kind == "ask":
            attempts[number] = dict(event, id=f"v1-{number:04d}", graded=None)
        elif kind == "grade" and number in attempts:
            # The old format had no evidence field, so an old field report is a
            # self-report by definition.
            is_field = attempts[number]["kind"] == "field"
            event.setdefault("grader", "self" if is_field else "claude")
            event.setdefault("evidence", "")
            attempts[number]["graded"] = event
    return attempts


def cmd_migrate(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    old_topics = root / "topics.json"
    if (root / "dimensions.json").exists():
        raise RecordError(
            f"{root}/ is already in the current format. Nothing was changed."
        )
    if not old_topics.exists():
        raise RecordError(f"No old-format record at {root}/topics.json.")
    old = read_json(old_topics)
    old_attempts = root / "attempts.jsonl"
    lines = (
        old_attempts.read_text(encoding="utf-8").splitlines()
        if old_attempts.exists()
        else []
    )
    attempts = v1_attempts(lines)
    save_dimensions(root, old["dimensions"])
    for tid, topic in old["topics"].items():
        save_topic(root, tid, topic)
    for attempt in attempts.values():
        save_attempt(root, attempt)
    (root / "topics").mkdir(exist_ok=True)
    (root / "attempts").mkdir(exist_ok=True)
    old_topics.unlink()
    if old_attempts.exists():
        old_attempts.unlink()
    print(
        f"Migrated {len(old['topics'])} topic(s) and {len(attempts)} attempt(s). Old files removed."
    )
    print("Commit the result. The old files remain in git history.")


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
        "--dimensions", help=f"comma-separated; default: {','.join(DEFAULT_DIMENSIONS)}"
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
    p.add_argument(
        "--attempt", required=True, help="the id `ask` printed, or a unique part of it"
    )
    p.add_argument("--outcome", required=True, choices=OUTCOMES)
    p.add_argument("--hint", required=True, type=int, choices=HINT_LEVELS)
    p.add_argument("--confidence", required=True, choices=CONFIDENCES)
    p.add_argument("--answer", required=True, help="the learner's answer, paraphrased")
    p.add_argument("--gap", help="what was missing or wrong, in one line")
    p.add_argument(
        "--evidence",
        help="an artifact Claude inspected: commit, PR, test output, trace",
    )
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
    sub.add_parser("migrate").set_defaults(func=cmd_migrate)
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
