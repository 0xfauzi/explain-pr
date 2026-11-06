"""Questions that do not block the build, answered wherever the learner is.

A build session posts a question (`post`) and carries on. The learner answers
later, in chat, from a terminal (`answer`), or on the learning room page. The
next session grades what is waiting (`inbox`, then `grade --feedback`), and the
learner reads the feedback with `questions` or on the page.

Every route reads and writes the same attempt files, so nothing depends on one
harness. Two optional page routes exist:

- `serve` runs the room page on this machine with only the standard library.
  It binds to 127.0.0.1 unless told otherwise.
- `room-push` and `room-pull` move questions and answers to and from a hosted
  page through plain JSON files, for harnesses that can publish such a page and
  write its data store. The page can then grade on the spot.

An attempt here moves through three states: open (posted, no answer), answered
(the learner's response is saved and locked), and graded.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from record import (
    CONFIDENCES,
    KINDS,
    OUTCOMES,
    RecordError,
    data_dir,
    find_attempt,
    load_attempts,
    load_record,
    new_attempt_id,
    now_stamp,
    require_topic,
    save_attempt,
)

ROOM_PAGE = Path(__file__).resolve().parent.parent / "assets" / "room.html"
# An answer is a few sentences. The cap stops a pasted file or a runaway client
# from filling the record; it is far above any real answer.
MAX_ANSWER_CHARS = 4000
# The server reads at most this much from one request body, for the same reason.
MAX_BODY_BYTES = 20_000
# Feedback the learner has not had a chance to read yet: the most recent few.
RECENT_FEEDBACK = 5
DONT_KNOW = "I don't know."


def state(attempt: dict) -> str:
    if attempt.get("graded"):
        return "graded"
    return "answered" if attempt.get("response") else "open"


def async_attempts(attempts: dict[str, dict]) -> list[dict]:
    rows = [a for a in attempts.values() if a.get("channel") == "async"]
    return sorted(rows, key=lambda a: (a["at"], a["id"]))


def save_response(
    root: Path, attempt: dict, answer: str, confidence: str, stamp: str
) -> None:
    """Record the learner's answer. It locks: a second answer is refused."""
    if state(attempt) != "open":
        raise RecordError(
            f"Question {attempt['id']} already has an answer; it is locked."
        )
    answer = answer.strip()
    if not answer:
        raise RecordError("The answer is empty. Write one, or answer 'I don't know.'")
    if confidence not in CONFIDENCES:
        raise RecordError(f"Confidence must be one of {CONFIDENCES}.")
    attempt["response"] = {
        "answer": answer[:MAX_ANSWER_CHARS],
        "confidence": confidence,
        "at": stamp,
    }
    save_attempt(root, attempt)


# ---------------------------------------------------------------- post, inbox


def cmd_post(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    data = load_record(root)
    topic = require_topic(data, args.topic)
    if topic["status"] != "active":
        raise RecordError(f"Topic {args.topic!r} is retired. Add a new topic instead.")
    if not args.rubric.strip():
        raise RecordError(
            "--rubric is empty. Write the expected answer points before posting."
        )
    stamp = now_stamp(args.today)
    attempt = {
        "id": new_attempt_id(stamp),
        "topic": args.topic,
        "kind": args.kind,
        "question": args.question,
        "rubric": args.rubric,
        "context": args.context or "",
        "channel": "async",
        "at": stamp,
        "graded": None,
    }
    save_attempt(root, attempt)
    print(
        f"Posted {attempt['id']}. Carry on with the build; grade it from `inbox` later."
    )
    print(
        "The learner can answer in chat, with `learning.py answer`, or on the room page."
    )


def cmd_inbox(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    rows = async_attempts(load_attempts(root))
    ready = [a for a in rows if state(a) == "answered"]
    waiting = sum(1 for a in rows if state(a) == "open")
    if not ready:
        print(f"Nothing to grade. {waiting} posted question(s) not answered yet.")
        return
    print(f"{len(ready)} answer(s) to grade; {waiting} question(s) still unanswered.")
    print(
        "Grade each with: grade --attempt ID --outcome O --hint 0 --feedback TEXT [--gap TEXT]"
    )
    for a in ready:
        r = a["response"]
        print()
        print(f"[{a['id']}] {a['topic']} ({a['kind']})")
        print(f"  question: {a['question']}")
        print(f"  rubric: {a['rubric']}")
        print(f"  answer ({r['confidence']} confidence): {r['answer']}")


# ---------------------------------------------------------------- learner CLI


def print_waiting(rows: list[dict]) -> None:
    open_rows = [a for a in rows if state(a) == "open"]
    if open_rows:
        print(
            f"{len(open_rows)} question(s) waiting. Answer the oldest with `learning.py answer`."
        )
        for n, a in enumerate(open_rows, 1):
            print(f"  {n}. [{a['kind']}] {a['question'][:100]}")
    else:
        print(
            "No questions waiting. Claude posts one when a build reaches a learning checkpoint."
        )
    waiting = sum(1 for a in rows if state(a) == "answered")
    if waiting:
        print(f"{waiting} answer(s) saved and waiting for grading at the next session.")


def print_feedback(rows: list[dict]) -> None:
    graded = sorted(
        (a for a in rows if state(a) == "graded"),
        key=lambda a: a["graded"]["at"],
        reverse=True,
    )
    if not graded:
        return
    print()
    print("Recent feedback:")
    for a in graded[:RECENT_FEEDBACK]:
        g = a["graded"]
        print(f"  {g['outcome'].upper()}  {a['question'][:90]}")
        if g.get("feedback"):
            print(f"    {g['feedback']}")


def cmd_questions(args: argparse.Namespace) -> None:
    rows = async_attempts(load_attempts(data_dir(args.dir)))
    print_waiting(rows)
    print_feedback(rows)


def read_answer_interactively(attempt: dict) -> tuple[str, str] | None:
    """Prompt in the terminal. None means the learner chose 'not now'."""
    print(f"[{attempt['kind']}] {attempt['topic']}")
    print()
    print(attempt["question"])
    if attempt.get("context"):
        print()
        print(attempt["context"])
    if attempt["kind"] == "retrieval":
        print()
        print("Answer from memory; opening the code first turns this into recognition.")
    print()
    print(
        "Type your answer; finish with an empty line. Type ? for 'I don't know', or press"
    )
    print("Enter on an empty first line for 'not now'.")
    lines = []
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if not text:
        return None
    if text == "?":
        return DONT_KNOW, "low"
    while True:
        print("How sure are you? [l]ow, [m]edium, [h]igh: ", end="", flush=True)
        line = sys.stdin.readline()
        if not line:  # end of input: keep the question open rather than guess
            return None
        level = {"l": "low", "m": "medium", "h": "high"}.get(line.strip().lower()[:1])
        if level:
            return text, level


def pick_open(rows: list[dict], ref: str | None) -> dict | None:
    open_rows = [a for a in rows if state(a) == "open"]
    if ref:
        attempt = find_attempt({a["id"]: a for a in rows}, ref)
        if state(attempt) != "open":
            raise RecordError(
                f"Question {attempt['id']} already has an answer; it is locked."
            )
        return attempt
    return open_rows[0] if open_rows else None


def cmd_answer(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    attempt = pick_open(async_attempts(load_attempts(root)), args.attempt)
    if attempt is None:
        print(
            "No questions waiting. Claude posts one when a build reaches a learning checkpoint."
        )
        return
    if args.dont_know:
        reply = (DONT_KNOW, "low")
    elif args.text is not None:
        if not args.confidence:
            raise RecordError("--text needs --confidence (low, medium or high).")
        reply = (args.text, args.confidence)
    else:
        reply = read_answer_interactively(attempt)
    if reply is None:
        print("Left open. It will be here next time.")
        return
    save_response(root, attempt, reply[0], reply[1], now_stamp(args.today))
    print(
        "Saved and locked. Your next session grades it; read the feedback with `learning.py questions`."
    )


# ---------------------------------------------------------------- page data


def page_view(attempt: dict, dimension: str, with_rubric: bool) -> dict:
    """One question as the room page sees it. The rubric goes only where the page grades."""
    view = {
        "topic": attempt["topic"],
        "dimension": dimension,
        "kind": attempt["kind"],
        "question": attempt["question"],
        "context": attempt.get("context", ""),
        "createdAt": attempt["at"],
        "status": state(attempt),
    }
    if with_rubric:
        view["rubric"] = attempt["rubric"]
    if attempt.get("response"):
        r = attempt["response"]
        view.update(answer=r["answer"], confidence=r["confidence"], answeredAt=r["at"])
    if attempt.get("graded"):
        g = attempt["graded"]
        view.update(
            outcome=g["outcome"],
            feedback=g.get("feedback", ""),
            gap=g.get("gap", ""),
            gradedAt=g["at"],
        )
    if attempt.get("restatement"):
        view["restatement"] = attempt["restatement"]
    return view


def room_rows(root: Path, with_rubric: bool) -> list[dict]:
    data = load_record(root)
    rows = []
    for a in async_attempts(load_attempts(root)):
        dim = data["topics"].get(a["topic"], {}).get("dimension", "")
        rows.append(dict(page_view(a, dim, with_rubric), id=a["id"]))
    return rows


def save_restatement(root: Path, attempt: dict, text: str) -> None:
    if state(attempt) != "graded":
        raise RecordError("Restate after the answer is graded.")
    attempt["restatement"] = text.strip()[:MAX_ANSWER_CHARS]
    save_attempt(root, attempt)


# ---------------------------------------------------------------- serve


def page_document() -> bytes:
    page = ROOM_PAGE.read_text(encoding="utf-8")
    head = '<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"></head><body>'
    return (head + page + "</body></html>").encode()


def route_get(root: Path, path: str) -> tuple[int, object]:
    if path in ("/", "/index.html"):
        return 200, page_document()
    if path == "/api/questions":
        return 200, room_rows(root, with_rubric=False)
    return 404, {"error": "not found"}


def route_post(root: Path, path: str, body: dict) -> tuple[int, object]:
    if path not in ("/api/answer", "/api/restate"):
        return 404, {"error": "not found"}
    try:
        attempt = find_attempt(load_attempts(root), str(body.get("id", "")))
        if attempt.get("channel") != "async":
            raise RecordError("That question was asked in chat; answer it there.")
        if path == "/api/answer":
            save_response(
                root,
                attempt,
                str(body.get("answer", "")),
                str(body.get("confidence", "")),
                now_stamp(None),
            )
        else:
            save_restatement(root, attempt, str(body.get("text", "")))
    except RecordError as exc:
        return 400, {"error": str(exc)}
    return 200, {"ok": True}


# The server answers requests on several threads. Saving an answer checks the
# question is open and then writes it; without this lock two simultaneous answers
# can both pass the check. Measured with the window widened to 50 ms: 15 of 20
# concurrent answers to one question were accepted without it, 1 of 20 with it.
WRITE_LOCK = threading.Lock()


def make_handler(root: Path) -> type:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args) -> None:  # keep the terminal quiet
            return

        def send(self, code: int, value: object) -> None:
            is_page = isinstance(value, bytes)
            body = value if is_page else json.dumps(value).encode()
            self.send_response(code)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8" if is_page else "application/json",
            )
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            self.send(*route_get(root, self.path))

        def do_POST(self) -> None:
            with WRITE_LOCK:
                self.handle_post()

        def handle_post(self) -> None:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                return self.send(413, {"error": "Request too large."})
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                return self.send(400, {"error": "Body must be JSON."})
            self.send(
                *route_post(root, self.path, body if isinstance(body, dict) else {})
            )

    return Handler


def cmd_serve(args: argparse.Namespace) -> None:
    root = data_dir(args.dir)
    load_record(root)
    if not ROOM_PAGE.exists():
        raise RecordError(
            f"Missing {ROOM_PAGE}; the skill's assets folder is incomplete."
        )
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print(
            f"Warning: listening on {args.host} lets anyone who can reach this machine read "
            "these questions and answer them. Prefer 127.0.0.1 with an SSH tunnel."
        )
    server = ThreadingHTTPServer((args.host, args.port), make_handler(root))
    print(
        f"Learning room at http://{args.host}:{server.server_address[1]}/  (Ctrl+C stops it)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")


# ---------------------------------------------------------------- hosted page sync


def cmd_room_push(args: argparse.Namespace) -> None:
    """Write one JSON file per ungraded posted question, for a hosted page's store."""
    root = data_dir(args.dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for row in room_rows(root, with_rubric=True):
        if row["status"] == "graded":
            continue
        doc_id = row.pop("id")
        (out / f"{doc_id}.json").write_text(
            json.dumps(row, indent=2) + "\n", encoding="utf-8"
        )
        count += 1
    print(
        f"Wrote {count} question file(s) to {out}/; write each to the page's 'questions' collection, id = file name."
    )


def pull_one(root: Path, attempt: dict, doc: dict) -> set[str]:
    """Apply one page document. Returns what changed: a set of 'answered' and 'graded'."""
    changed = set()
    if state(attempt) == "open" and doc.get("answer"):
        save_response(
            root,
            attempt,
            doc["answer"],
            doc.get("confidence", "unknown"),
            doc.get("answeredAt") or now_stamp(None),
        )
        changed.add("answered")
    graded_on_page = doc.get("status") == "graded" and doc.get("outcome") in OUTCOMES
    if state(attempt) == "answered" and graded_on_page:
        attempt["graded"] = {
            "outcome": doc["outcome"],
            "hint": 0,
            "confidence": attempt["response"]["confidence"],
            "answer": attempt["response"]["answer"],
            "feedback": doc.get("feedback", ""),
            "gap": doc.get("gap", ""),
            "evidence": "",
            # Claude graded it, on the page, against the rubric fixed before the question.
            "grader": "claude",
            "via": "page",
            "at": doc.get("gradedAt") or now_stamp(None),
        }
        changed.add("graded")
    if (
        doc.get("restatement")
        and not attempt.get("restatement")
        and attempt.get("graded")
    ):
        attempt["restatement"] = doc["restatement"][:MAX_ANSWER_CHARS]
    save_attempt(root, attempt)
    return changed


def cmd_room_pull(args: argparse.Namespace) -> None:
    """Read documents saved from a hosted page's store and apply answers and grades."""
    root = data_dir(args.dir)
    attempts = load_attempts(root)
    counts = {"answered": 0, "graded": 0}
    for path in sorted(Path(args.dir_in).glob("*.json")):
        attempt = attempts.get(path.stem)
        if attempt is None or attempt.get("channel") != "async":
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for change in pull_one(root, attempt, doc):
            counts[change] += 1
    print(
        f"From the page: {counts['answered']} new answer(s), {counts['graded']} graded there."
    )
    print("Grade anything still waiting with `inbox`.")


# ---------------------------------------------------------------- cli


def add_commands(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("post", help="leave a question for the learner without waiting")
    p.add_argument("--topic", required=True)
    p.add_argument("--kind", required=True, choices=KINDS)
    p.add_argument("--question", required=True)
    p.add_argument("--rubric", required=True)
    p.add_argument(
        "--context", help="a short code excerpt or situation shown with the question"
    )
    p.set_defaults(func=cmd_post)

    sub.add_parser("inbox", help="answers waiting to be graded").set_defaults(
        func=cmd_inbox
    )
    sub.add_parser(
        "questions", help="for the learner: what is waiting, and recent feedback"
    ).set_defaults(func=cmd_questions)

    p = sub.add_parser(
        "answer", help="for the learner: answer the oldest waiting question"
    )
    p.add_argument("--attempt", help="answer this question instead of the oldest")
    p.add_argument("--text", help="the answer, for use without a terminal prompt")
    p.add_argument("--confidence", choices=["low", "medium", "high"])
    p.add_argument(
        "--dont-know",
        action="store_true",
        help="record 'I don't know' with low confidence",
    )
    p.set_defaults(func=cmd_answer)

    p = sub.add_parser("serve", help="run the learning room page on this machine")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser(
        "room-push", help="write posted questions as JSON files for a hosted page"
    )
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_room_push)

    p = sub.add_parser(
        "room-pull", help="apply answers and grades saved from a hosted page"
    )
    p.add_argument(
        "--from", dest="dir_in", required=True, help="folder of <attempt-id>.json files"
    )
    p.set_defaults(func=cmd_room_pull)
