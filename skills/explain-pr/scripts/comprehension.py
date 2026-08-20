"""Ask whether a document taught anybody anything, by examining a reader who read it.

This is the only measurement here that aims at the thing we actually want. It is
also the weakest, and both facts should stay visible.

How it works. A reader runs in an empty directory holding one document. It has no
access to the thing the document describes. It answers a fixed set of questions,
and a separate judge scores each answer against a key, without being told which
document produced it.

Where the questions come from decides whether any of it means anything. Write the
key from the primary source, the code or the change or the subject itself, and
write it BEFORE you open the document you are testing. A key read off the document
scores the document against itself, which always passes and never informs.

A control arm runs automatically. Its packet says nothing about the subject, so
whatever it scores is the reader answering from what it already knew. If the
control scores much above zero, every other number is inflated by that much and
the run should be thrown away.

What this cannot do. The reader is a model standing in for a person, and that
substitution is unproven. A person's understanding depends on what they already
know, what they need it for, and how tired they are. None of that is in here. Use
this to compare two drafts of the same thing, not to certify that a document is
good.

Usage:
  python comprehension.py exam.toml doc-a.html doc-b.md --runs 3

The exam is TOML so that this needs nothing installed. `tomllib` is in the
standard library from Python 3.11.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

READER_TIMEOUT_S = 900
JUDGE_TIMEOUT_S = 180

#: The reader is pinned to the default voice. A reader written in one style is a
#: different reader, and we are comparing documents, not readers.
NEUTRAL = json.dumps({"outputStyle": "default"})

NULL_PACKET = """\
# No material

This directory holds nothing about the subject you are being asked about. That is
deliberate.
"""

READER_PROMPT = """\
This directory holds everything you may use. Read all of it before answering. You
have no access to the thing it describes, and you must not answer from your own
knowledge of the subject.

Some files may contain interactive figures written as HTML and JavaScript. You
have Bash. If running one would answer a question, run it.

Answer these questions. Each answer is at most 120 words.

{questions}

If the material does not answer a question, say exactly: NOT IN THE MATERIAL. A
confident wrong answer scores below an honest NOT IN THE MATERIAL.

Reply with one JSON object and nothing else, inside a ```json fence, mapping each
question id to your answer:

```json
{{"q1": "...", "q2": "..."}}
```
"""

JUDGE_PROMPT = """\
Score one answer against one reference. You do not know who wrote the answer or
what they were given. Do not reward or punish style.

QUESTION
{ask}

REFERENCE ANSWER, checked against the primary source
{key}

ANSWER UNDER TEST
{answer}

2 - states every element the reference states and contradicts none
1 - correct as far as it goes but misses an element, or is too vague to act on
0 - wrong, contradicts the reference, absent, or says it is not in the material

An answer fuller than the reference is not penalised. An answer about a different
thing than the question asked scores 0.

Reply with one JSON object and nothing else. Keep `why` under 25 words with no
quotation marks in it.

{{"score": 0, "why": "one short sentence"}}
"""


def json_objects(text: str) -> list[dict[str, object]]:
    """Every top-level JSON object in the text, in order.

    Decoding from each opening brace survives a missing fence, a stray brace
    inside an answer, and a model that adds commentary around the object.
    """
    decoder = json.JSONDecoder()
    found: list[dict[str, object]] = []
    i = text.find("{")
    while i != -1:
        try:
            obj, end = decoder.raw_decode(text[i:])
        except json.JSONDecodeError:
            i = text.find("{", i + 1)
            continue
        if isinstance(obj, dict):
            found.append(obj)
        i = text.find("{", i + end)
    return found


def claude(prompt: str, *, model: str, cwd: Path, timeout: int, tools: list[str]) -> str:
    """One headless turn. The prompt goes on stdin, because `--allowedTools` is
    variadic and would swallow a positional prompt placed after it."""
    cmd = ["claude", "-p", "--model", model, "--settings", NEUTRAL]
    if tools:
        cmd += ["--allowedTools", *tools]
    done = subprocess.run(cmd, input=prompt, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if done.returncode != 0:
        raise RuntimeError(f"claude exited {done.returncode}: {done.stderr.strip()[:300]}")
    return done.stdout.strip()


def read_once(doc: Path | None, questions: str, model: str, wanted: set[str]) -> dict[str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        packet = Path(tmp)
        if doc is None:
            (packet / "README.md").write_text(NULL_PACKET)
        else:
            shutil.copy(doc, packet / doc.name)
        raw = claude(
            READER_PROMPT.format(questions=questions),
            model=model, cwd=packet, timeout=READER_TIMEOUT_S,
            tools=["Read", "Grep", "Glob", "Bash"],
        )
    candidates = json_objects(raw)
    if not candidates:
        raise RuntimeError(f"reader returned no JSON; first 200 chars: {raw[:200]!r}")
    best = max(candidates, key=lambda o: len(wanted & set(o)))
    missing = sorted(wanted - set(best))
    if missing:
        # A missing id is a reader that did not answer, not a wrong answer.
        # Scoring it zero would hide a harness fault inside a result.
        raise RuntimeError(f"reader skipped questions: {missing}")
    return {k: str(v) for k, v in best.items() if k in wanted}


def judge_one(q: dict[str, str], answer: str, model: str, cwd: Path) -> int:
    raw = claude(
        JUDGE_PROMPT.format(ask=q["ask"], key=q["key"], answer=answer),
        model=model, cwd=cwd, timeout=JUDGE_TIMEOUT_S, tools=[],
    )
    verdicts = [o for o in json_objects(raw) if "score" in o]
    if not verdicts:
        raise RuntimeError(f"judge returned no verdict; first 200 chars: {raw[:200]!r}")
    score = int(str(verdicts[0]["score"]))
    if score not in (0, 1, 2):
        raise RuntimeError(f"judge returned {score}, expected 0, 1 or 2")
    return score


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exam", help="TOML with a [[questions]] table of id, ask, key")
    ap.add_argument("documents", nargs="+", help="the documents to compare")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", default="sonnet", help="reader and judge model")
    args = ap.parse_args()

    exam = tomllib.loads(Path(args.exam).read_text())
    qs = exam["questions"]
    for q in qs:
        q["ask"] = " ".join(q["ask"].split())
        q["key"] = " ".join(q["key"].split())
    wanted = {q["id"] for q in qs}
    questions = "\n\n".join(f"{q['id']}. {q['ask']}" for q in qs)
    top = 2 * len(qs)

    arms: list[tuple[str, Path | None]] = [(Path(d).name, Path(d)) for d in args.documents]
    arms.append(("(control: nothing)", None))

    here = Path.cwd()
    results: dict[str, list[int]] = {}
    for name, doc in arms:
        totals = []
        for r in range(1, args.runs + 1):
            print(f"  {name} run {r}", file=sys.stderr, flush=True)
            answers = read_once(doc, questions, args.model, wanted)
            totals.append(sum(judge_one(q, answers[q["id"]], args.model, here) for q in qs))
        results[name] = totals

    print(f"\n{len(qs)} questions, {top} points per run, {args.runs} runs each\n")
    print(f"{'document':34s} {'mean':>6s} {'of':>4s} {'pct':>6s} {'runs':>12s}")
    print("-" * 68)
    for name, totals in results.items():
        mean = statistics.mean(totals)
        print(f"{name:34s} {mean:>6.1f} {top:>4d} {100 * mean / top:>5.0f}% "
              f"{','.join(str(t) for t in totals):>12s}")

    control = statistics.mean(results["(control: nothing)"])
    print(f"\nControl scored {control:.1f} of {top}.")
    if control > 0.15 * top:
        print("That is too high. The reader is answering from prior knowledge, so")
        print("every number above is inflated and this run should be discarded.")
    else:
        print("Low, so the points above came from reading rather than from prior knowledge.")
    print("\nThis compares documents. It does not certify that any of them is good,")
    print("and the reader is a model standing in for a person.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
