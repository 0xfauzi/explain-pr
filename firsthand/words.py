"""Every exact line the engine produces (build-2a-contract.md section 9).

Pure functions, no I/O. Only `keys.agent_output` may hand the question, result,
finding, fact, pending and ack lines to an agent channel.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, tzinfo
from typing import TYPE_CHECKING

from firsthand import timeline
from firsthand.model import PRINT_PREFIX, How, Key, KeyItem, Moment, TestItem

if TYPE_CHECKING:
    from firsthand.keys import OutputContext

FOOTER = "Checked by a run: the change undone, the tests kept."
NO_ROOM = "run firsthand room"
WORK_NOTICE = "A reply here is part of your agent's chat. The Room is not."
QUIET_OFF = "Quiet is off."
FIRST_VISIT = (
    "Nothing here yet. Notes about this project arrive in a few minutes. "
    "Your first question comes when your agent next finishes a change with tests."
)
COVERS = "Telling a test that proves a change from one that would pass anyway."
NO_EVIDENCE = "Checking work that has no tests."
DONT_KNOW_REASON = '"Don\'t know" is not counted as a miss.'
SKIPPED_REASON = "Skipped, so nothing was scored."
MOVED_ON = "You moved on, so nothing was scored."
WRONG_START = (
    "Closed. The start was moved back and the check runs again from there. "
    "Nothing was scored."
)
SHOWN_FIRST = "This was printed in your agent as a fact, so the question is closed."
STILL_RUNNING = "Locked. The check is still running."
CHECK_DROPPED = (
    "The check could not finish, so there is nothing to show. Nothing was scored."
)
TIME_DROPPED = (
    "The check took longer than 2 minutes, so I dropped it. Nothing was scored."
)
WOULD_PASS = "It would pass whether or not the change exists."

_MORE_ROWS = {
    "fails_on_assertion": "fails on its assertion",
    "still_passes": "still passes",
    "cannot_run": "cannot run without the new code, which is weak proof",
    "does_not_pass": "does not pass",
}
_ONE_TEST = {
    "still_passes": ["It still passes with the change undone.", WOULD_PASS],
    "fails_on_assertion": ["It fails on its assertion with the change undone."],
    "cannot_run": ["It cannot run with the change undone, which is weak proof."],
    "does_not_pass": ["It does not pass with the change undone."],
}
_MISS_REASON = {
    "fails_on_assertion": ": it fails on its assertion.",
    "cannot_run": ": it cannot run without the new code.",
    "does_not_pass": ".",
}
_ANSWER_LABELS = {
    "none": "None.",
    "fails": "Fails.",
    "passes": "Still passes.",
    "dont_know": "Don't know.",
}
_CHAT_ANSWER = {"dont_know": "don't know"}
_CHIPS = {"match": "Matched", "miss": "Did not match"}
_ACKS = {
    "skip": "Skipped. Back to: {task}. Next: read the summary.",
    "skip2": "Skipped. No more questions this session. Back to: {task}. Next: read the summary.",
    "quiet": (
        'Quiet for this session. Checks still run and post notes. "quiet today" and '
        '"quiet here" also work.'
    ),
    "quiet-today": "Quiet for today. Checks still run and post notes.",
    "quiet-here": "Quiet for this project. Checks still run and post notes.",
    "off": (
        "Firsthand is off. Nothing is asked, run or recorded. Your record is kept. "
        '"firsthand on" to return.'
    ),
}


# ---------------------------------------------------------------- helpers


def context_text(printable: Sequence[str], agent_only: Sequence[str]) -> str | None:
    """Agent-only lines first, then the print prefix and the lines to print."""
    lines = [line for line in agent_only if line]
    shown = [line for line in printable if line]
    if shown:
        lines += [PRINT_PREFIX, *shown]
    return "\n".join(lines) if lines else None


def task_name(prompt: str) -> str:
    return timeline.task_name(prompt)


def _local(at: str, tz: tzinfo) -> datetime:
    return (
        datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC).astimezone(tz)
    )


def clock_time(at: str, tz: tzinfo) -> str:
    return f"{_local(at, tz):%H:%M}"


def short_date(at: str, tz: tzinfo) -> str:
    when = _local(at, tz)
    return f"{when.day} {when:%b}"


def back_line(task: str) -> str:
    return f"Back to: {task}. Next: read the summary."


def glob_label(pattern: str) -> str:
    """ "refunds/**" -> "refunds/", "**/migrations/**" -> "migrations/"."""
    label = pattern
    while label.startswith("**/"):
        label = label[3:]
    for tail in ("/**", "/*"):
        if label.endswith(tail):
            return label[: -len(tail)] + "/"
    return label


def short_ref(moment_id: str) -> str:
    return moment_id[-6:].lower()


def _url(ctx: OutputContext, kind: str, m: Moment) -> str | None:
    if ctx.room_url is None:
        return None
    return f"{ctx.room_url}/{kind}/{short_ref(m.id)}"


def _and(items: Sequence[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _name(test_id: str) -> str:
    return test_id.rsplit("::", 1)[-1]


# ------------------------------------------------------------ the question


def _verb(tests: Sequence[TestItem]) -> str:
    edited = sum(1 for t in tests if t.status == "edited")
    if edited == 0:
        return "added"
    return "edited" if edited == len(tests) else "added or edited"


def lead(m: Moment) -> str:
    n = len(m.tests)
    verb = _verb(m.tests)
    if n == 1:
        return f"It {verb} 1 test. Read it first."
    return f"It {verb} {n} tests. Read them first."


def prompt(m: Moment) -> str:
    if len(m.tests) == 1:
        return "Would it still pass with the change undone?"
    return "Which one would still pass with the change undone?"


def context_line(m: Moment, project_name: str, tz: tzinfo) -> str:
    since = clock_time(m.base_at, tz)
    return f"Verification | {project_name} | {m.task_name} | change since {since}"


def _question_body(m: Moment) -> str:
    n = len(m.tests)
    verb = _verb(m.tests)
    if n == 1:
        name = m.tests[0].name
        return (
            f"your agent finished and {verb} 1 test, {name}. {prompt(m)} "
            "Reply fails or passes."
        )
    listed = ", ".join(f"{t.n} {t.name}" for t in m.tests)
    numbers = ", ".join(str(t.n) for t in m.tests)
    return (
        f"your agent finished and {verb} {n} tests. {prompt(m)} {listed}. "
        f"Reply {numbers} or none."
    )


def _callit():
    from firsthand import words_callit  # imported here: it imports this module

    return words_callit


def _brief():
    from firsthand import words_brief  # imported here: kept beside words_callit

    return words_brief


def question_line(m: Moment, ctx: OutputContext) -> str:
    if m.kind == "call_it":
        return _callit().question_line(m, ctx)
    if m.kind == "brief":
        return _brief().question_line(m, ctx)
    body = _question_body(m)
    url = _url(ctx, "q", m)
    shown = "With the test shown:" if len(m.tests) == 1 else "With the tests shown:"
    if ctx.work_computer and url is not None:
        line = f"Firsthand (skip ok): {url} {body[0].upper()}{body[1:]}"
    else:
        line = f"Firsthand (skip ok): {body} {shown} {url or NO_ROOM}"
    if ctx.work_computer and ctx.work_notice:
        line += " " + WORK_NOTICE
    return line.replace("\n", " ")


# -------------------------------------------------------------- the result


def _picked(m: Moment, k: Key) -> KeyItem | None:
    answer = m.answer or ""
    if answer.isdigit() and 1 <= int(answer) <= len(k.tests):
        return k.tests[int(answer) - 1]
    return None


def _passing(k: Key) -> list[KeyItem]:
    return [t for t in k.tests if t.result == "still_passes"]


def answer_text(m: Moment) -> str:
    """What the person said, without How sure: "2, test_x." or "None."."""
    if m.kind == "call_it":
        return _callit().answer_text(m)
    if m.kind == "brief":
        return _brief().answer_text(m)
    answer = m.answer
    if answer is None:
        return "Skipped." if m.state == "skipped" else "No answer."
    if answer.isdigit():
        index = int(answer) - 1
        name = m.tests[index].name if 0 <= index < len(m.tests) else answer
        return f"{answer}, {name}."
    return _ANSWER_LABELS.get(answer, f"{answer}.")


def you_said(m: Moment) -> str:
    text = answer_text(m)
    if m.answer is None:
        return text
    if m.confidence == "high":
        text += " Sure."
    elif m.confidence == "low":
        text += " Not sure."
    return text


def _still_pass(items: Sequence[KeyItem]) -> str:
    names = _and([_name(t.id) for t in items])
    verb = "still passes" if len(items) == 1 else "still pass"
    return f"{names} {verb} with the change undone."


def _several(m: Moment, k: Key) -> list[str]:
    passing = _passing(k)
    picked = _picked(m, k)
    if picked is not None and picked.result == "still_passes":
        return ["It still passes with the change undone.", WOULD_PASS]
    if passing:
        return [_still_pass(passing)]
    if picked is not None:
        tail = _MISS_REASON.get(picked.result, ".")
        return [f"{_name(picked.id)} does not pass with the change undone{tail}"]
    return ["None of them passes with the change undone."]


def what_happened(m: Moment, k: Key) -> list[str]:
    if len(k.tests) == 1:
        return list(_ONE_TEST.get(k.tests[0].result, _ONE_TEST["does_not_pass"]))
    return _several(m, k)


def _source_for(m: Moment, item: KeyItem) -> TestItem | None:
    return next((t for t in m.tests if t.id == item.id), None)


def _cue_target(m: Moment, k: Key) -> KeyItem:
    passing = _passing(k)
    if passing:
        return passing[0]
    return _picked(m, k) or k.tests[0]


def _assert_cue(path: str, item: KeyItem, source: TestItem | None) -> str:
    lines = source.assert_lines if source is not None else ()
    if not lines and item.assert_line is not None:
        lines = (item.assert_line,)
    if len(lines) == 1:
        return f"Its only assertion is at {path}:{lines[0]}."
    if lines:
        joined = _and([str(n) for n in lines])
        return f"Its assertions are at {path}:{joined}."
    line = source.line if source is not None else 1
    return f"It has no assert statement: {path}:{line}."


def cue_target(m: Moment, k: Key) -> KeyItem:
    """The test the cue is about: the one that still passes, else the picked one."""
    return _cue_target(m, k)


def cue_text(m: Moment, k: Key) -> str | None:
    """What would have shown it, from line numbers only. Only for a miss."""
    target = _cue_target(m, k)
    path = target.id.split("::", 1)[0]
    if k.how == "exit_code":
        return f"It was checked by exit code only: {path}."
    source = _source_for(m, target)
    if target.result == "still_passes":
        return _assert_cue(path, target, source)
    if target.result == "cannot_run" and target.fail_line is not None:
        return (
            f"With the change undone it stops at {path}:{target.fail_line} with an "
            "error, not on an assertion."
        )
    line = target.fail_line or target.assert_line
    if line is None and source is not None:
        line = source.line
    return f"It fails at {path}:{line}." if line is not None else f"It fails at {path}."


def more_row(item: KeyItem) -> str:
    return _MORE_ROWS.get(item.result, "does not pass")


def checked_line(how: How) -> str:
    if how == "exit_code":
        return "Checked by a run, by exit code, no model."
    return "Checked by a run, no model."


def counts_line(matched: int, scored: int, fixed: int) -> str:
    return (
        f"Your calls of this kind: {matched} of {scored} matched. "
        f'Always answering "none" would have scored {fixed} of {scored}.'
    )


def sure_line(
    sure_matched: int, sure_total: int, unsure_matched: int, unsure_total: int
) -> str:
    return (
        f"Sure: {sure_matched} of {sure_total} matched. "
        f"Not sure: {unsure_matched} of {unsure_total}."
    )


def pending_line(m: Moment, ctx: OutputContext) -> str:
    if m.kind == "call_it":
        return _callit().pending_line(m, ctx)
    if m.kind == "brief":
        return _brief().pending_line(m, ctx)
    url = _url(ctx, "r", m)
    where = f"at {url}" if url else "in the Room: run firsthand room"
    return f"Firsthand: locked. The check is still running. The result will be {where}"


def dispute_line(stands: bool) -> str:
    if stands:
        return "Rechecked. The result stands, and here is why."
    return "Rechecked. The check was wrong. This call is removed from your record."


def chip_label(result: str | None) -> str:
    return _CHIPS.get(result or "", "Not scored")


def _chat_answer(m: Moment) -> str:
    answer = m.answer or "none"
    return _CHAT_ANSWER.get(answer, answer)


def _chat_fact(m: Moment, k: Key) -> str:
    lines = what_happened(m, k)
    first = lines[0]
    subject = _picked(m, k) or (k.tests[0] if len(k.tests) == 1 else None)
    if subject is not None and first.startswith("It "):
        lines[0] = f"{_name(subject.id)} {first[3:]}"
    return " ".join(lines)


def result_lines(
    m: Moment, k: Key, ctx: OutputContext, result: str | None = None
) -> list[str]:
    """The chat form of the result. `result` is "match", "miss" or None (not scored)."""
    from firsthand.moments import revert_test  # the score rule lives with the moment

    if m.kind == "call_it":
        return _callit().result_lines(m, k, ctx, result)
    if m.kind == "brief":
        return _brief_result(m, k, ctx, result)
    if result is None and m.answer not in (None, "dont_know"):
        sc = revert_test.score(m.answer, k)  # type: ignore[arg-type]
        result = sc.result if sc is not None else None
    head = f"Firsthand, revert test. {chip_label(result)}. You said {_chat_answer(m)}."
    if m.confidence == "high":
        head += " Sure."
    elif m.confidence == "low":
        head += " Not sure."
    lines = [head]
    if m.answer == "dont_know":
        lines.append(DONT_KNOW_REASON)
    lines.append(_chat_fact(m, k))
    if result == "miss":
        cue = cue_text(m, k)
        if cue:
            lines.append(f"What would have shown it: {cue}")
    url = _url(ctx, "r", m)
    lines.append(f"More: {url}" if url else f"More: {NO_ROOM}")
    lines.append(back_line(m.task_name))
    return lines


def _brief_result(
    m: Moment, k: Key, ctx: OutputContext, result: str | None
) -> list[str]:
    from firsthand.moments import brief

    if result is None:
        sc = brief.score((m.extra or {}).get("confirm"), k)
        result = sc.result if sc is not None else None
    cue = cue_text(m, k) if result == "miss" and m.tests else None
    return _brief().result_lines(m, k, ctx, result, cue)


# ----------------------------------------------------- lines with no question


def _finding_parts(k: Key) -> tuple[list[str], list[str]]:
    passing = [t.id for t in k.tests if t.result == "still_passes"]
    broken = [t.id for t in k.tests if t.result == "cannot_run"]
    return passing, broken


def note_fact(k: Key) -> str:
    passing, broken = _finding_parts(k)
    parts = []
    if passing:
        verb = "passes" if len(passing) == 1 else "pass"
        parts.append(f"{', '.join(passing)} {verb} with the change undone.")
    if broken:
        parts.append(f"{', '.join(broken)} cannot run with the change undone.")
    return " ".join(parts)


def finding_line(k: Key) -> str:
    return f"Firsthand finding: {note_fact(k)}"


def fact_line(k: Key, pattern: str) -> str:
    passing = [t for t in k.tests if t.result == "still_passes"]
    name = _name(passing[0].id) if passing else _name(k.tests[0].id)
    return (
        f"Firsthand: {name} passes without the change. "
        f"{glob_label(pattern)} is marked high stakes."
    )


def note_title(k: Key) -> str:
    """The note's title in the Inbox: the fact with test names, no final full stop."""
    text = note_fact(k)
    for item in k.tests:
        text = text.replace(item.id, _name(item.id))
    return text.rstrip(".")


def ack_line(ack: str | None, task: str) -> str:
    template = _ACKS.get(ack or "skip", _ACKS["skip"])
    return template.format(task=task)
