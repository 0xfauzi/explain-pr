"""Every exact line of Call it (experience.md sections 5.2 and 6.2).

Pure functions, no I/O. `words` dispatches here for a moment or key whose kind is
`call_it`, so `keys.agent_output` stays the only door to an agent channel. Lines
that experience.md does not give are listed in build-2a-contract.md section 14.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from firsthand.model import Key, Moment

if TYPE_CHECKING:
    from firsthand.keys import OutputContext

HEADLINE = "CALL IT"
REASON = "A test is failing"
PROMPT = "Before any fix: where is the cause?"
FOOTER = (
    "Your agent keeps working. If it starts a fix before you answer, this closes "
    "and the failure is saved in your record. Its theory may already be on screen. "
    "Checked by a run, once the test passes again."
)
# The Replay drill is not in this preview, so the line does not name it.
FIX_STARTED = (
    "Your agent got there first. Nothing was scored. The failure is saved in your "
    "record."
)
NEVER_GREEN = "Not scored. The change ended before the test passed."
NO_FIX = (
    "Not scored. The test passed again with no change outside the tests, so there "
    "is no fix to undo."
)
NOT_CAUSAL = (
    "Not scored. With the fix undone, the test still passes, so where the fix "
    "landed proves nothing about your call."
)
SOMEWHERE_ELSE = "Somewhere else"
FIXED_SENTENCE = 'Always answering "the file changed in this task" would have scored'
_PATTERN_VERBS = {
    "sleep": "adds a sleep",
    "except": "adds a broad except",
    "assert": "removes or changes an assertion",
    "skip": "adds a skip",
}
_NO_ROOM = "run firsthand room"


def _extra(m: Moment) -> Mapping[str, object]:
    return m.extra or {}


def picks(m: Moment) -> list[Mapping[str, object]]:
    return list(_extra(m).get("picks", ()))  # type: ignore[arg-type]


def failing_id(m: Moment) -> str:
    return str(_extra(m).get("test") or "")


def name(m: Moment) -> str:
    return failing_id(m).rsplit("::", 1)[-1] or "the test"


def _url(ctx: OutputContext, kind: str, m: Moment) -> str | None:
    if ctx.room_url is None:
        return None
    return f"{ctx.room_url}/{kind}/{m.id[-6:].lower()}"


def _and(items: Sequence[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


# --------------------------------------------------------------- the question


def context_line(m: Moment, project_name: str) -> str:
    return f"Debugging | {project_name} | {m.task_name}"


def question_line(m: Moment, ctx: OutputContext) -> str:
    listed = [f"{p['n']} {p['path']}" for p in picks(m)]
    last = len(listed) + 1
    listed.append(f"{last} somewhere else")
    body = (
        f"{name(m)} is failing. Before any fix, where is the cause? "
        f"{', '.join(listed)}. Reply 1 to {last}"
    )
    url = _url(ctx, "q", m)
    if ctx.work_computer and url is not None:
        line = f"Firsthand (skip ok): {url} {body}."
    else:
        line = f"Firsthand (skip ok): {body}, or: {url or _NO_ROOM}"
    if ctx.work_computer and ctx.work_notice:
        line += " A reply here is part of your agent's chat. The Room is not."
    return line.replace("\n", " ")


def pick_rows(m: Moment) -> list[dict]:
    rows = [
        {"value": str(p["n"]), "label": f"{p['n']}  {p['path']}", "note": p["note"]}
        for p in picks(m)
    ]
    last = len(rows) + 1
    rows.append(
        {"value": str(last), "label": f"{last}  {SOMEWHERE_ELSE}", "note": None}
    )
    rows.append({"value": "dont_know", "label": "Don't know", "note": None})
    return rows


def trace(m: Moment) -> dict:
    message = _extra(m).get("message")
    title = f"{name(m)}: {message}" if message else f"{name(m)} is failing."
    frames = [
        {
            "path": f["path"],
            "line": f["line"],
            "where": f"in {f['where']}" if f.get("where") else None,
        }
        for f in _extra(m).get("frames", ())  # type: ignore[union-attr]
    ]
    return {"title": title, "frames": frames}


def waiting_line(m: Moment) -> str:
    return f"Locked. Shown when {name(m)} passes again."


def waiting_row(m: Moment) -> str:
    return f"shown when {name(m)} passes again"


def pending_line(m: Moment, ctx: OutputContext) -> str:
    url = _url(ctx, "r", m)
    where = f"at {url}" if url else f"in the Room: {_NO_ROOM}"
    return f"Firsthand: locked. Shown when {name(m)} passes again. The result will be {where}"


# ---------------------------------------------------------------- the result


def answer_text(m: Moment) -> str:
    answer = m.answer
    if answer is None:
        return "Skipped." if m.state == "skipped" else "No answer."
    if answer == "dont_know":
        return "Don't know."
    listed = picks(m)
    if answer.isdigit():
        n = int(answer)
        if 1 <= n <= len(listed):
            return f"{n}, {listed[n - 1]['path']}."
        return f"{n}, somewhere else."
    return f"{answer}."


def _key_extra(k: Key) -> Mapping[str, object]:
    return k.extra or {}


def _fix(k: Key) -> list[str]:
    return list(_key_extra(k).get("fix_paths", ()))  # type: ignore[arg-type]


def fails_again(k: Key) -> bool:
    return bool(k.tests) and k.tests[0].result != "still_passes"


def what_happened(k: Key) -> list[str]:
    fix = _fix(k)
    lines = [f"The fix landed in {_and(fix)}."] if fix else []
    if fix and fails_again(k):
        lines.append("With the fix undone, the test fails again.")
    elif fix:
        lines.append("With the fix undone, the test still passes.")
    return lines or ["The test passed again with no change outside the tests."]


def pattern_reason(pattern: Mapping[str, object]) -> str:
    verb = _PATTERN_VERBS.get(str(pattern.get("kind")), "adds a pattern")
    return (
        f"Not scored. The fix {verb} at {pattern['path']}:{pattern['line']}. That can "
        "turn the test green without touching the cause, so where it landed proves "
        "nothing about your call."
    )


def unscored_text(reason: str | None, k: Key | None) -> str | None:
    if reason == "symptom-patch" and k is not None:
        found = list(_key_extra(k).get("patterns", ()))  # type: ignore[arg-type]
        return pattern_reason(found[0]) if found else None
    return {
        "never-green": NEVER_GREEN,
        "no-fix": NO_FIX,
        "fix-not-causal": NOT_CAUSAL,
    }.get(reason or "")


def cue_text(k: Key) -> str | None:
    """What would have shown it: the fix file, and the trace line that names it."""
    from firsthand.moments import call_it

    path = call_it.cue_path(k)
    if path is None:
        return None
    lines = [
        int(f["line"])
        for f in _key_extra(k).get("frames", ())  # type: ignore[union-attr]
        if f["path"] == path
    ]
    if lines:
        return f"The fix is in {path}, which the trace names at line {lines[-1]}."
    return f"The fix is in {path}, a file the failing trace never names."


def cue_line(k: Key) -> int | None:
    from firsthand.moments import call_it

    path = call_it.cue_path(k)
    lines = [
        int(f["line"])
        for f in _key_extra(k).get("frames", ())  # type: ignore[union-attr]
        if f["path"] == path
    ]
    return lines[-1] if lines else None


def more_row(k: Key) -> str:
    return (
        "fails again with the fix undone"
        if fails_again(k)
        else "still passes with the fix undone"
    )


def counts_line(matched: int, scored: int, fixed: int) -> str:
    return (
        f"Your calls of this kind: {matched} of {scored} matched. "
        f"{FIXED_SENTENCE} {fixed} of {scored}."
    )


def result_lines(
    m: Moment, k: Key, ctx: OutputContext, result: str | None = None
) -> list[str]:
    """The chat form. Call it's result is never printed in the agent in 2b: it
    arrives after the fix, so it lives in the Room. Kept for `firsthand room --tty`."""
    from firsthand import words
    from firsthand.moments import call_it

    if result is None and m.answer not in (None, "dont_know"):
        sc = call_it.score(m.answer, k)  # type: ignore[arg-type]
        result = sc.result if sc is not None else None
    said = answer_text(m).rstrip(".")
    head = f"Firsthand, call it. {words.chip_label(result)}. You said {said}."
    lines = [head, " ".join(what_happened(k))]
    if result == "miss":
        cue = cue_text(k)
        if cue:
            lines.append(f"What would have shown it: {cue[0].lower()}{cue[1:]}")
    url = _url(ctx, "r", m)
    lines.append(f"More: {url}" if url else f"More: {_NO_ROOM}")
    lines.append(words.back_line(m.task_name))
    return lines
