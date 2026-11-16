"""Read models for the Room and the CLI (build-2a-contract.md section 7.2).

Pure functions over the record's events, the engine's moments and a source
reader. Results come only from `check.ran` events in the record, never from the
key store: a `Key` is rebuilt from the event body and source lines are read from
the snapshot store by tree, path and line.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, tzinfo
from pathlib import Path

from firsthand import words
from firsthand.model import (
    REVEALED,
    Key,
    KeyItem,
    Moment,
    ProjectSettings,
    Settings,
    StepRun,
)

MAX_SOURCE_LINES = 200
NOTES_SHOWN = 5
FIXED_ANSWER = "none"
SURE_BAND_MIN = 5
REVERT = "revert_test"
CALL = "call_it"
BRIEF = "brief"
KIND_LABELS = {REVERT: "Revert test", CALL: "Call it", BRIEF: "Brief"}
# The first word of each kind's context line: the skill it exercises.
SKILL_WORDS = {REVERT: "Verification", CALL: "Debugging", BRIEF: "Framing"}

# read_source(project_id, tree, path) -> text or None
SourceReader = Callable[[str, str, str], str | None]


def short_ref(moment_id: str) -> str:
    return words.short_ref(moment_id)


@dataclass
class ViewInput:
    """What every view reads. The engine builds one per call."""

    events: Sequence[dict]
    moments: Mapping[str, Moment]
    settings: Settings
    projects: Mapping[str, ProjectSettings]
    tz: tzinfo
    today: date
    room_url: str | None
    read_source: SourceReader
    record_path: str = "~/.firsthand/record"
    quiet: Mapping[str, str | None] = field(default_factory=dict)  # project -> scope
    quiet_all: Mapping[str, tuple[str, ...]] = field(
        default_factory=dict
    )  # every scope
    lines: Mapping[str, str | None] = field(default_factory=dict)  # moment -> line

    def __post_init__(self) -> None:
        self.by_moment: dict[str, list[dict]] = {}
        # Entry numbers: a moment's 1-based place among offered moments, in record order.
        self.numbers: dict[str, int] = {}
        for e in self.events:
            if e.get("moment"):
                self.by_moment.setdefault(e["moment"], []).append(e)
            if e["type"] == "moment.offered" and e.get("moment"):
                self.numbers.setdefault(e["moment"], len(self.numbers) + 1)

    def of(self, moment_id: str, kind: str) -> list[dict]:
        return [e for e in self.by_moment.get(moment_id, ()) if e["type"] == kind]

    def last(self, moment_id: str, kind: str) -> dict | None:
        found = self.of(moment_id, kind)
        return found[-1] if found else None


# ------------------------------------------------------------- small parts


def local_date(at: str, tz: tzinfo) -> date:
    when = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    return when.astimezone(tz).date()


def key_from_ran(body: Mapping[str, object], m: Moment | None) -> Key:
    """Rebuild a Key from a check.ran body. assert_text is not in the record."""
    texts = {t.id: t.assert_text for t in m.tests} if m is not None else {}
    items = tuple(
        KeyItem(
            id=r["id"],
            result=r["result"],
            assert_line=r.get("assert_line"),
            assert_text=texts.get(r["id"]),
            fail_line=r.get("fail_line"),
        )
        for r in body.get("results", ())  # type: ignore[union-attr]
    )
    steps = tuple(
        StepRun(
            step=s["step"],
            command=s["command"],
            exit=s.get("exit"),
            failing=tuple(s.get("failing", ())),
            output_sha256=s.get("output_sha256", ""),
        )
        for s in body.get("steps", ())  # type: ignore[union-attr]
    )
    return Key(
        moment=str(body.get("check")),
        kind=str(body.get("check_kind", "revert_test")),
        how=body.get("how", "pytest"),  # type: ignore[arg-type]
        base_tree=str(body.get("base_tree", "")),
        head_tree=str(body.get("head_tree", "")),
        made_at="",
        tests=items,
        steps=steps,
        undone_paths=tuple(body.get("undone_paths", ())),  # type: ignore[arg-type]
        duration_s=float(body.get("duration_s", 0.0)),  # type: ignore[arg-type]
        extra=body.get("extra"),  # type: ignore[arg-type]
    )


def _line_of(text: str | None, line: int | None) -> str | None:
    if text is None or line is None:
        return None
    lines = text.splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()[:200]
    return None


def _function_source(text: str, start: int) -> str:
    lines = text.splitlines()[start - 1 :]
    if not lines:
        return ""
    indent = len(lines[0]) - len(lines[0].lstrip())
    body = [lines[0]]
    for line in lines[1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        body.append(line)
    while body and not body[-1].strip():
        body.pop()
    return "\n".join(body[:MAX_SOURCE_LINES])


def _project_name(v: ViewInput, project_id: str | None) -> str:
    p = v.projects.get(project_id or "")
    return p.name if p is not None else (project_id or "")


def asked_today(v: ViewInput) -> int:
    """moment.offered today, local date, not closed as unseen or wrong-start, nor
    closed as fix-started before anyone saw it."""
    not_counted = {
        e["moment"]
        for e in v.events
        if e["type"] == "moment.closed"
        and (
            e["body"].get("how") in ("unseen", "wrong-start")
            or (
                e["body"].get("how") == "fix-started" and e["body"].get("seen") is False
            )
        )
    }
    return sum(
        1
        for e in v.events
        if e["type"] == "moment.offered"
        and local_date(e["at"], v.tz) == v.today
        and e["moment"] not in not_counted
    )


def kind_of(v: ViewInput, moment_id: str) -> str:
    """The moment kind, from the live moment or its moment.offered event."""
    m = v.moments.get(moment_id)
    if m is not None:
        return m.kind
    offered = v.last(moment_id, "moment.offered")
    return str(offered["body"].get("moment_kind", REVERT)) if offered else REVERT


def _scores(v: ViewInput, kind: str = REVERT) -> list[tuple[dict, Moment | None]]:
    """The last call.scored of each moment of this kind, with the moment."""
    last: dict[str, dict] = {}
    for e in v.events:
        if e["type"] == "call.scored" and e.get("moment"):
            last[e["moment"]] = e
    return [
        (e, v.moments.get(mid)) for mid, e in last.items() if kind_of(v, mid) == kind
    ]


def counts(v: ViewInput, kind: str = REVERT) -> tuple[int, int, int]:
    return _counts(v, kind)


def _counts(v: ViewInput, kind: str = REVERT) -> tuple[int, int, int]:
    scored = [e for e, _ in _scores(v, kind) if e["body"]["result"] != "unscored"]
    matched = sum(1 for e in scored if e["body"]["result"] == "match")
    fixed = sum(1 for e in scored if e["body"]["outcome_kind"] == "common")
    return matched, len(scored), fixed


def sure(v: ViewInput, kind: str = REVERT) -> str | None:
    return _sure(v, kind)


def _sure(v: ViewInput, kind: str = REVERT) -> str | None:
    bands = {"high": [0, 0], "low": [0, 0]}
    for e, m in _scores(v, kind):
        if e["body"]["result"] == "unscored" or m is None or m.confidence is None:
            continue
        band = bands[m.confidence]
        band[1] += 1
        band[0] += e["body"]["result"] == "match"
    if max(bands["high"][1], bands["low"][1]) < SURE_BAND_MIN:
        return None
    return words.sure_line(*bands["high"], *bands["low"])


# ----------------------------------------------------------------- results


def _chip(v: ViewInput, m: Moment) -> tuple[str, str]:
    if m.state == "sealed":
        return "pending", "Locked"
    scored = v.last(m.id, "call.scored")
    result = scored["body"]["result"] if scored else None
    if result == "match":
        return "matched", "Matched"
    if result == "miss":
        return "did_not_match", "Did not match"
    return "not_scored", "Not scored"


def _not_scored_reason(v: ViewInput, m: Moment) -> str | None:
    scored = v.last(m.id, "call.scored")
    if scored and scored["body"].get("supersedes"):
        return words.dispute_line(False)
    if m.answer == "dont_know":
        return words.DONT_KNOW_REASON
    if m.state == "skipped":
        return words.SKIPPED_REASON
    if m.close_how == "shown-first":
        return words.SHOWN_FIRST
    if m.state == "closed":
        return words.MOVED_ON
    return None


def _cue(v: ViewInput, m: Moment, k: Key) -> dict | None:
    scored = v.last(m.id, "call.scored")
    if not scored or scored["body"]["result"] != "miss":
        return None
    text = words.cue_text(m, k)
    if text is None:
        return None
    target = words.cue_target(m, k)
    path = target.id.split("::", 1)[0]
    source = v.read_source(m.project_id, m.head_tree, path)
    test = next((t for t in m.tests if t.id == target.id), None)
    # The quoted line is the one the cue names: the assertion of a test that still
    # passes, else the line where the run stopped.
    if target.result == "still_passes":
        line = target.assert_line or (test.line if test else None)
    else:
        line = target.fail_line or target.assert_line or (test.line if test else None)
    evidence = []
    if line is not None and k.how == "pytest":
        evidence.append({"path": path, "line": line, "text": _line_of(source, line)})
    return {"text": text, "evidence": evidence}


def _sent(v: ViewInput, m: Moment, k: Key) -> str | None:
    for e in v.events:
        body = e["body"]
        if (
            e["type"] == "task.event"
            and body.get("kind") == "line_delivered"
            and body.get("line") in ("finding", "result")
            and body.get("check") == m.id
        ):
            fact = words.note_fact(k)
            if not fact:
                return None
            return f'Sent to your agent: "{fact}"'
    return None


def _dispute(v: ViewInput, m: Moment) -> str | None:
    reruns = [e for e in v.of(m.id, "check.ran") if e["body"].get("rerun_of")]
    if not reruns:
        return None
    scored = v.last(m.id, "call.scored")
    stands = not (scored and scored["body"].get("supersedes"))
    return words.dispute_line(stands)


def _more(v: ViewInput, m: Moment, k: Key) -> dict:
    matched, scored, fixed = _counts(v)
    return {
        "rows": [
            {
                "id": t.id,
                "name": t.id.rsplit("::", 1)[-1],
                "text": words.more_row(t),
            }
            for t in k.tests
        ],
        "checked": words.checked_line(k.how),
        "commands": [s.command for s in k.steps],
        "counts": words.counts_line(matched, scored, fixed) if scored else None,
        "sure": _sure(v),
        "sent": _sent(v, m, k),
        "dispute": _dispute(v, m),
    }


def result_view(v: ViewInput, m: Moment) -> dict | None:
    """Null unless the moment is revealed and a check.ran event exists for it."""
    if m.kind == CALL:
        return _callit().result_view(v, m)
    if m.kind == BRIEF:
        return _brief().result_view(v, m)
    if m.state not in REVEALED or m.close_how == "wrong-start":
        return None  # a check from the wrong base is never shown
    ran = v.last(m.id, "check.ran")
    if ran is None:
        return None
    k = key_from_ran(ran["body"], m)
    chip, label = _chip(v, m)
    result = {
        "headline": "REVERT TEST",
        "chip": chip,
        "chip_label": label,
        "reason": _not_scored_reason(v, m) if chip == "not_scored" else None,
        "you_said": words.you_said(m),
        "what_happened": words.what_happened(m, k),
        "cue": _cue(v, m, k),
        "back": words.back_line(m.task_name),
        "more": _more(v, m, k),
    }
    return _room().result_fields(v, m, result, ran, k)


# ---------------------------------------------------------------- question


def _evidence(v: ViewInput, m: Moment) -> list[dict]:
    rows = []
    sources: dict[str, str | None] = {}
    for t in m.tests:
        if t.path not in sources:
            sources[t.path] = v.read_source(m.project_id, m.head_tree, t.path)
        text = sources[t.path]
        row: dict[str, object] = {
            "n": t.n,
            "id": t.id,
            "name": t.name,
            "path": t.path,
            "line": t.line,
            "status": t.status,
        }
        if text is not None:
            row["asserts"] = (
                [{"line": n, "text": _line_of(text, n)} for n in t.assert_lines]
                if m.how == "pytest"
                else []
            )
            row["source"] = _function_source(text, t.line) if m.how == "pytest" else ""
        rows.append(row)
    return rows


def _picks(m: Moment) -> list[dict]:
    if len(m.tests) == 1:
        values = [("fails", "Fails"), ("passes", "Still passes")]
    else:
        values = [(str(t.n), str(t.n)) for t in m.tests] + [("none", "None")]
    return [{"value": a, "label": b} for a, b in values] + [
        {"value": "dont_know", "label": "Don't know"}
    ]


def _held(m: Moment) -> dict | None:
    if m.state != "held" or not m.pending:
        return None
    if m.pending.get("kind") == "skip":
        return {"kind": "skip"}
    return {
        "kind": "pick",
        "answer": m.pending.get("answer"),
        "confidence": m.pending.get("confidence"),
    }


def _call(v: ViewInput, m: Moment) -> dict | None:
    if m.state not in ("sealed", "settled") or m.answer is None:
        return None
    sealed = v.last(m.id, "call.sealed")
    label = words.answer_text(m).rstrip(".")
    conf = {"high": "Sure", "low": "Not sure"}.get(m.confidence or "")
    return {
        "answer": m.answer,
        "label": label,
        "confidence": m.confidence,
        "confidence_label": conf,
        "channel": m.channel,
        "at": sealed["at"] if sealed else None,
    }


def _status_line(v: ViewInput, m: Moment, has_result: bool) -> str | None:
    if m.state == "sealed" and not has_result:
        return words.STILL_RUNNING
    unavailable = v.last(m.id, "check.unavailable")
    if unavailable and not has_result:
        if unavailable["body"].get("reason") == "time limit":
            return words.TIME_DROPPED
        return words.CHECK_DROPPED
    if m.state == "closed":
        return {
            "moved-on": words.MOVED_ON,
            "shown-first": words.SHOWN_FIRST,
            "check-dropped": words.CHECK_DROPPED,
            "wrong-start": words.WRONG_START,
        }.get(m.close_how or "")
    return None


def _can(v: ViewInput, m: Moment) -> dict:
    held_pick = m.state == "held" and (m.pending or {}).get("kind") == "pick"
    scored = v.last(m.id, "call.scored")
    disputed = any(e["body"].get("rerun_of") for e in v.of(m.id, "check.ran"))
    return {
        "lock": m.state == "open",
        "undo": m.state == "held",
        "confidence": held_pick,
        "show": held_pick,
        "skip": m.state == "open",
        "wrong_start": m.state == "open",
        "dispute": m.state == "settled"
        and scored is not None
        and scored["body"]["result"] != "unscored"
        and not disputed,
    }


def _callit():
    from firsthand import views_callit  # imported here: it imports this module

    return views_callit


def _brief():
    from firsthand import views_brief  # imported here: it imports this module

    return views_brief


def _room():
    from firsthand import views_room  # imported here: it imports this module

    return views_room


def question_view(v: ViewInput, m: Moment, say: Sequence[str] | None = None) -> dict:
    if m.kind == CALL:
        view = _callit().question_view(v, m, say)
    elif m.kind == BRIEF:
        view = _brief().question_view(v, m, say)
    else:
        view = _revert_view(v, m, say)
    return _room().question_fields(v, m, view)


def _revert_view(v: ViewInput, m: Moment, say: Sequence[str] | None) -> dict:
    result = result_view(v, m)
    return {
        "id": m.id,
        "ref": short_ref(m.id),
        "kind": m.kind,
        "state": m.state,
        "reason": "Your agent finished",
        "skip_ok": True,
        "context": words.context_line(m, _project_name(v, m.project_id), v.tz),
        "lead": words.lead(m),
        "evidence": _evidence(v, m),
        "trace": None,
        "prompt": words.prompt(m),
        "picks": _picks(m),
        "multi": len(m.tests) >= 2,  # the picks are toggles, sent with Lock
        "footer": words.FOOTER,
        "line": v.lines.get(m.id),
        "can": _can(v, m),
        "held": _held(m),
        "call": _call(v, m),
        "status_line": _status_line(v, m, result is not None),
        "say": list(say) if say is not None else None,
        "result": result,
    }


# ------------------------------------------------------------------- inbox


def _notice(v: ViewInput, project_id: str | None) -> str | None:
    if v.settings.dial == "off":
        return "Firsthand is off. It keeps your record. Open Settings"
    scope = v.quiet.get(project_id or "")
    return {
        "session": "Quiet for this session. Runs still post notes. Undo",
        "today": "Quiet for today. Runs still post notes. Undo",
        "here": "Quiet for this project. Runs still post notes. Undo",
    }.get(scope or "")


def _notes(v: ViewInput, project_id: str) -> list[dict]:
    return [
        e
        for e in reversed(v.events)
        if e["type"] == "note.posted" and e.get("project") == project_id
    ]


def _printed(v: ViewInput, note: dict) -> bool:
    ran = next((e for e in v.events if e["id"] == note["body"].get("check")), None)
    check = ran["body"].get("check") if ran else None
    return any(
        e["type"] == "task.event"
        and e["body"].get("kind") == "line_delivered"
        and e["body"].get("line") == "fact"
        and e["body"].get("check") == check
        for e in v.events
    )


def _task_of(v: ViewInput, note: dict) -> str:
    name = ""
    for e in v.events:
        if e["id"] == note["id"]:
            break
        if e["type"] == "task.started" and e.get("change") == note.get("change"):
            name = e["body"].get("name", "")
    return name


def note_title(body: dict) -> str:
    """A note's fact as a title: no full stop, each test by its short name."""
    title = body.get("fact", "").rstrip(".")
    for ev in body.get("evidence", ()):
        title = title.replace(ev["test"], ev["test"].rsplit("::", 1)[-1])
    return title


def _note_item(v: ViewInput, note: dict) -> dict:
    body = note["body"]
    fact = body.get("fact", "")
    title = note_title(body)
    return {
        "id": note["id"],
        "at": note["at"],
        "time": words.clock_time(note["at"], v.tz),
        "title": title,
        "text": fact,
        "evidence": list(body.get("evidence", ())),
        "printed": _printed(v, note),
        "checked": "Checked by a run, no model.",
        "task": _task_of(v, note),
    }


def _results(v: ViewInput, project_id: str) -> list[dict]:
    items = []
    for m in sorted(v.moments.values(), key=lambda x: x.id, reverse=True):
        if m.project_id != project_id or m.opened or m.state not in REVEALED:
            continue
        if m.close_how == "wrong-start":
            continue
        if m.kind in (CALL, BRIEF) and m.state == "sealed":
            continue  # under Waiting, or Now for the Brief's confirm
        chip, label = _chip(v, m)
        items.append(
            {
                "id": m.id,
                "ref": short_ref(m.id),
                "kind": KIND_LABELS.get(m.kind, "Revert test"),
                "task": m.task_name,
                "chip": chip,
                "chip_label": label,
                "href": f"/r/{short_ref(m.id)}",
            }
        )
    return items


def _now(v: ViewInput, project_id: str) -> list[dict]:
    live = [
        m
        for m in v.moments.values()
        if m.project_id == project_id
        and (m.state in ("open", "held") or (m.kind == BRIEF and _brief().asking(m)))
    ]
    if live and live[0].kind == BRIEF:
        return [_brief().now_row(live[0])]
    return [_now_item(m) for m in live[:1]]


def _now_item(m: Moment) -> dict:
    held = (m.pending or {}).get("kind") if m.state == "held" else None
    one = m.kind == CALL or len(m.tests) == 1
    return {
        "id": m.id,
        "ref": short_ref(m.id),
        "reason": "A test is failing" if m.kind == CALL else "Your agent finished",
        "task": m.task_name,
        "size": None if held else ("One tap" if one else f"{len(m.tests)} tests"),
        "held": held,
        "href": f"/q/{short_ref(m.id)}",
    }


def inbox_view(v: ViewInput, project_id: str | None) -> dict:
    projects = [{"id": p.id, "name": p.name} for p in v.projects.values()]
    closing = f"Asked today: {asked_today(v)} of {v.settings.daily_limit}."
    state = {
        "dial": v.settings.dial,
        "quiet": v.quiet.get(project_id or ""),
        "notice": _notice(v, project_id),
    }
    if project_id is None:
        return _room().inbox_fields(
            v,
            {
                "project": None,
                "projects": projects,
                "state": state,
                "now": [],
                "waiting": [],
                "notes": [],
                "older_notes": 0,
                "results": [],
                "closing": closing,
                "empty": words.FIRST_VISIT,
            },
        )
    notes = _notes(v, project_id)
    view = {
        "project": {"id": project_id, "name": _project_name(v, project_id)},
        "projects": projects,
        "state": state,
        "now": _now(v, project_id),
        "waiting": _callit().waiting(v, project_id) + _brief().waiting(v, project_id),
        "notes": [_note_item(v, n) for n in notes[:NOTES_SHOWN]],
        "older_notes": max(0, len(notes) - NOTES_SHOWN),
        "results": _results(v, project_id),
        "closing": closing,
        "empty": None,
    }
    return _room().inbox_fields(v, view)


# ----------------------------------------------------------------- journal


def _moment_entry(v: ViewInput, m: Moment) -> dict:
    chip, label = _chip(v, m)
    happened, _ = _room().happened(v, m)
    at = _room().offered_at(v, m)
    entry = {
        "id": m.id,
        "at": at,
        "date": words.short_date(at, v.tz),
        "task": m.task_name,
        "kind": KIND_LABELS.get(m.kind, "Revert test"),
        "chip": chip,
        "chip_label": label,
        "href": f"/r/{short_ref(m.id)}",
        "rows": [
            {"label": "You said", "text": words.you_said(m)},
            {"label": "What happened", "text": happened},
        ],
    }
    return _room().journal_moment_fields(v, m, entry)


def _note_entry(v: ViewInput, note: dict) -> dict:
    entry = {
        "id": note["id"],
        "at": note["at"],
        "date": words.short_date(note["at"], v.tz),
        "task": _task_of(v, note),
        "kind": "Note",
        "chip": None,
        "chip_label": None,
        "href": None,
        "rows": [{"label": "Fact", "text": note["body"].get("fact", "")}],
    }
    return _room().journal_note_fields(v, note, entry)


def journal_view(v: ViewInput, project_id: str | None, limit: int) -> dict:
    entries = [
        _moment_entry(v, m)
        for m in v.moments.values()
        if (project_id is None or m.project_id == project_id)
        and m.state in ("settled", "skipped", "closed")
        and m.close_how != "wrong-start"
    ]
    entries += [
        _note_entry(v, n)
        for n in v.events
        if n["type"] == "note.posted"
        and (project_id is None or n.get("project") == project_id)
    ]
    entries.sort(key=lambda e: (e["at"], e["id"]), reverse=True)
    scope = _project_name(v, project_id) if project_id else "All projects"
    return {"scope": scope, "entries": entries[:limit]}


# ------------------------------------------------------------------ skills


def skills_view(v: ViewInput, project_id: str | None) -> dict:
    from firsthand import views_skills  # imported here: it imports this module

    return views_skills.skills_view(v, project_id)


# ---------------------------------------------------------------- settings


def settings_view(v: ViewInput, project_id: str | None) -> dict:
    s = v.settings
    p = v.projects.get(project_id or "")
    project = None
    if p is not None:
        project = {
            "id": p.id,
            "name": p.name,
            "test_command": p.test_command,
            "high_stakes": list(p.high_stakes),
            "check_time_limit_s": s.check_time_limit_s,
        }
    return {
        "dial": s.dial,
        "daily_limit": s.daily_limit,
        "findings_to_agent": s.findings_to_agent,
        "work_computer": s.work_computer,
        "quiet": {
            "today": s.quiet_today == v.today.isoformat(),
            "here": bool(p and p.quiet),
        },
        "project": project,
        "record": v.record_path,
    }


def status_view(
    v: ViewInput,
    project: Mapping[str, object] | None,
    question: Mapping[str, object] | None,
) -> dict:
    project_id = project.get("id") if project else None
    return {
        "dial": v.settings.dial,
        "quiet": v.quiet.get(str(project_id or "")),
        "quiet_scopes": list(v.quiet_all.get(str(project_id or ""), ())),
        "asked_today": asked_today(v),
        "daily_limit": v.settings.daily_limit,
        "room": v.room_url,
        "project": dict(project) if project is not None else None,
        "question": dict(question) if question is not None else None,
    }


def record_label(record: Path, home: Path) -> str:
    try:
        return "~/" + str(record.relative_to(home))
    except ValueError:
        return str(record)


# Names views_callit shares with this module.
project_name = _project_name
held = _held
call = _call
chip = _chip
line_of = _line_of
evidence = _evidence
cue = _cue
status_line = _status_line
