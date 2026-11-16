"""Every exact line of the Brief (experience.md section 5.3, prototypes/brief.html).

Pure functions, no I/O. `words` dispatches here for a moment or key whose kind is
`brief`, so `keys.agent_output` stays the only door to an agent channel. Lines
that experience.md does not give are listed in build-2a-contract.md section 15.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from firsthand.model import Key, KeyItem, Moment

if TYPE_CHECKING:
    from firsthand.keys import OutputContext

HEADLINE = "DONE CHECK"
REASON = "Starting a task"
CONFIRM_REASON = "Your agent finished"
PROMPT = "Name one check that fails now and will pass when this is done"
FOOTER = (
    "It goes to your agent as written. Checked by a run when your agent finishes: "
    "your test with the change, then with the change undone."
)
CONFIRM_FOOTER = "Checked by a run, no model: the change undone, your test kept."
CHECKED = "Checked by a run, no model: the change undone, your test kept."
SIZE = "One line"
CAN_TELL = "It can tell done from not done."
CANNOT_TELL = "It cannot tell done from not done."
WAITING_LINE = "Given to your agent. Shown when your agent finishes."
WAITING_ROW = "shown when your agent finishes"
CHECK_ROW = "the check is still running"
CONFIRM_RUNNING = "Locked. The check is still running."
_NO_ROOM = "run firsthand room"
_UNSCORED = {
    "no-test": "Not scored. No test was added in this task, so your check was not run.",
    "no-change": (
        "Not scored. Nothing outside the tests changed, so there was no change to undo."
    ),
    "not-your-check": "Not scored. I could not find your check among the new tests.",
    "never-done": "Not scored. The change ended before your agent finished.",
    "no-confirm": "Not scored. The change ended before you said whether this is your check.",
    "moved-on": "You moved on, so nothing was scored.",
    "skipped": "Skipped, so nothing was scored.",
    "check-unavailable": (
        "The check could not finish, so there is nothing to show. Nothing was scored."
    ),
}
_STOP = {
    "no-test": (
        "Firsthand: your agent finished, and no test was added for your check, so it "
        "was not run. Nothing was scored."
    ),
    "no-change": (
        "Firsthand: your agent finished, and nothing outside the tests changed, so "
        "your check was not run. Nothing was scored."
    ),
}


def _extra(m: Moment) -> Mapping[str, object]:
    return m.extra or {}


def phase(m: Moment) -> str:
    return str(_extra(m).get("phase") or "line")


def line_of(m: Moment) -> str:
    return str(_extra(m).get("line") or "")


def test_id(m: Moment) -> str:
    return str(_extra(m).get("test") or "")


def test_name(m: Moment) -> str:
    return test_id(m).rsplit("::", 1)[-1] or "the test"


def _url(ctx: OutputContext, kind: str, m: Moment) -> str | None:
    if ctx.room_url is None:
        return None
    return f"{ctx.room_url}/{kind}/{m.id[-6:].lower()}"


def _sentence(text: str) -> str:
    """The person's line as the middle of a sentence: no final full stop of its own."""
    return text.rstrip().rstrip(".!;:").rstrip()


def back_line(task: str, step: str = "read the summary") -> str:
    return f"Back to: {task}. Next: {step}."


def context_line(m: Moment, project_name: str) -> str:
    return f"Framing | {project_name} | {m.task_name}"


# ------------------------------------------------------------ the question


WORK_NOTICE = "A reply here is part of your agent's chat. The Room is not."
_ASK = "Name one check that fails now and will pass when this is done."
_REPLY = 'Reply here starting with "check:"'


def _work_notice(ctx: OutputContext) -> str:
    return " " + WORK_NOTICE if ctx.work_computer and ctx.work_notice else ""


def question_line(m: Moment, ctx: OutputContext) -> str:
    """The one line in the agent at the start of the task. Its reply is the line.

    On a work computer the Room link comes first (experience.md 6.2).
    """
    url = _url(ctx, "q", m)
    if ctx.work_computer and url is not None:
        line = f"Firsthand (skip ok): {url} Starting a task. {_ASK} {_REPLY}, or in the Room."
    else:
        line = f"Firsthand (skip ok): starting a task. {_ASK} {_REPLY}."
    return line + _work_notice(ctx)


def work_line(m: Moment) -> str:
    """What the agent receives: the person's own words and the fixed request."""
    return (
        f"Done when: {_sentence(line_of(m))}. Write this check as a failing test first."
    )


def sent_line(m: Moment) -> str:
    return (
        f'Given to your agent: "{work_line(m)}"\n'
        f"{back_line(m.task_name, 'your agent has started')}"
    )


def confirm_line(m: Moment, ctx: OutputContext) -> str:
    url = _url(ctx, "q", m)
    if ctx.work_computer and url is not None:
        line = f"Firsthand: {url} Is this your check? {test_name(m)}. Reply yes or no."
    else:
        line = (
            f"Firsthand: is this your check? {test_name(m)}. Reply yes or no, "
            f"or: {url or _NO_ROOM}"
        )
    return line + _work_notice(ctx)


def confirm_prompt(m: Moment) -> str:
    return f"Is this your check? {test_name(m)}"


def stop_line(reason: str) -> str | None:
    return _STOP.get(reason)


def pending_line(m: Moment, ctx: OutputContext) -> str:
    if phase(m) in ("line", "building"):
        return sent_line(m)
    url = _url(ctx, "r", m)
    where = f"at {url}" if url else f"in the Room: {_NO_ROOM}"
    return f"Firsthand: locked. The check is still running. The result will be {where}"


# --------------------------------------------------------------- the result


def answer_text(m: Moment) -> str:
    if m.answer == "dont_know":
        return "Don't know."
    text = line_of(m)
    if text:
        return f'"{_sentence(text)}"'
    return "Skipped." if m.state == "skipped" else "No answer."


def _item(k: Key) -> KeyItem | None:
    return k.tests[0] if len(k.tests) == 1 else None


def what_happened(k: Key) -> list[str]:
    item = _item(k)
    result = item.result if item is not None else "does_not_pass"
    if result == "fails_on_assertion":
        return ["Passes now. Fails on its assertion with the change undone.", CAN_TELL]
    if result == "still_passes":
        return ["Your check passes with the change undone.", CANNOT_TELL]
    if result == "cannot_run":
        # Not CANNOT_TELL: it does fail without the change, only not on its
        # assertion (experience.md 5.3 gives that sentence to a passing check only).
        return [
            "Passes now. It cannot run with the change undone, which is weak proof."
        ]
    return ["Passes now. It does not pass with the change undone."]


def unscored_text(reason: str | None) -> str | None:
    return _UNSCORED.get(reason or "")


def more_row(k: Key) -> str:
    item = _item(k)
    return {
        "fails_on_assertion": "fails on its assertion with the change undone",
        "still_passes": "still passes with the change undone",
        "cannot_run": "cannot run without the new code, which is weak proof",
    }.get(item.result if item else "", "does not pass with the change undone")


def corrections_lines(prompts: Sequence[str]) -> list[str]:
    if not prompts:
        return []
    n = len(prompts)
    noun = "correction" if n == 1 else "corrections"
    return [f"After your agent finished, you sent {n} {noun}:"] + [
        f'"{p}"' for p in prompts
    ]


def questions_line(questions: Sequence[str]) -> str | None:
    if not questions:
        return None
    n = len(questions)
    noun = "question" if n == 1 else "questions"
    quoted = " ".join(f'"{q}"' for q in questions)
    return f"Your agent asked {n} {noun}: {quoted}"


MAX_OUTSIDE = 10


def outside_line(categories: Sequence[str], paths: Sequence[str]) -> str | None:
    """Paths changed outside the kinds of file of the first edits. Shown, not scored."""
    if not paths:
        return None
    shown = ", ".join(paths[:MAX_OUTSIDE])
    more = f", and {len(paths) - MAX_OUTSIDE} more" if len(paths) > MAX_OUTSIDE else ""
    return (
        f"Also changed, outside the kinds of file of the first edits "
        f"({', '.join(categories)}): {shown}{more}."
    )


def counts_line(matched: int, scored: int) -> str:
    return f"Your answers of this kind: {matched} of {scored} matched."


def _chat_fact(k: Key) -> str:
    """What happened, as one chat line that names the test (prototypes/brief.html)."""
    item = _item(k)
    if item is None or item.result == "still_passes":
        return " ".join(what_happened(k))
    name = item.id.rsplit("::", 1)[-1]
    rest = {
        "fails_on_assertion": f"It fails on its assertion with the change undone. {CAN_TELL}",
        "cannot_run": "It cannot run with the change undone, which is weak proof.",
    }.get(item.result, "It does not pass with the change undone.")
    return f"{name} passes now. {rest}"


def result_lines(
    m: Moment, k: Key, ctx: OutputContext, result: str | None, cue: str | None
) -> list[str]:
    """The chat form of the result, after "yes" (or "no") to "Is this your check?"."""
    chip = {"match": "Matched", "miss": "Did not match"}.get(result or "", "Not scored")
    lines = [f"Firsthand, done check. {chip}."]
    if _extra(m).get("confirm") == "no":
        lines.append(_UNSCORED["not-your-check"].removeprefix("Not scored. "))
    else:
        lines.append(_chat_fact(k))
        if result == "miss" and cue:
            lines.append(f"What would have shown it: {cue}")
    url = _url(ctx, "r", m)
    lines.append(f"More: {url}" if url else f"More: {_NO_ROOM}")
    lines.append(back_line(m.task_name))
    return lines
