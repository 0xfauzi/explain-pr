"""Read models for the Brief: its card, its confirm, its result and its Waiting row.

The shapes are those of build-2a-contract.md section 7.2, plus `form` ("line" for
the free line, "pick" for the confirm), `said_label` and `more.notes`. As in
`views`, a result comes only from the record, never from the key store.
"""

from __future__ import annotations

from firsthand import gitwatch, views, words, words_brief
from firsthand.model import REVEALED, Moment

KIND = "brief"
LABEL = "Brief"
CONFIRM_PICKS = [{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]


def _extra(m: Moment) -> dict:
    return m.extra or {}


def asking(m: Moment) -> bool:
    """The card wants something from the person now: the line or the confirm."""
    return m.state == "open" or (
        m.state == "sealed"
        and words_brief.phase(m) == "confirm"
        and not _extra(m).get("confirm")
    )


def _reason_of(v: views.ViewInput, m: Moment) -> str | None:
    scored = v.last(m.id, "call.scored")
    return scored["body"].get("unscored_reason") if scored else None


def _status_line(v: views.ViewInput, m: Moment, has_result: bool) -> str | None:
    if has_result:
        return None
    phase = words_brief.phase(m)
    if m.state == "sealed" and phase == "building":
        return words_brief.WAITING_LINE
    if m.state == "sealed" and _extra(m).get("confirm"):
        return words_brief.CONFIRM_RUNNING
    if m.state == "settled":
        return words_brief.unscored_text(_reason_of(v, m))
    if m.state == "closed":
        return words.MOVED_ON
    return None


def _can(m: Moment) -> dict:
    confirm = m.state == "sealed" and words_brief.phase(m) == "confirm"
    open_confirm = confirm and not _extra(m).get("confirm")
    return {
        "lock": m.state == "open" or open_confirm,
        "undo": False,
        "confidence": False,
        "show": False,
        "skip": m.state == "open" or open_confirm,
        "wrong_start": False,
        "dispute": False,
    }


def question_view(v: views.ViewInput, m: Moment, say=None) -> dict:
    result = result_view(v, m)
    confirm = m.state == "sealed" and words_brief.phase(m) in ("checking", "confirm")
    project = views.project_name(v, m.project_id)
    return {
        "id": m.id,
        "ref": views.short_ref(m.id),
        "kind": m.kind,
        "state": m.state,
        "reason": words_brief.CONFIRM_REASON if confirm else words_brief.REASON,
        "skip_ok": True,
        "context": words_brief.context_line(m, project),
        "lead": None,
        "evidence": views.evidence(v, m) if confirm else [],
        "trace": None,
        "form": "pick" if confirm else "line",
        "prompt": words_brief.confirm_prompt(m) if confirm else words_brief.PROMPT,
        "picks": CONFIRM_PICKS if confirm else [],
        "multi": False,
        "footer": words_brief.CONFIRM_FOOTER if confirm else words_brief.FOOTER,
        "line": v.lines.get(m.id),
        "can": _can(m),
        "held": None,
        "call": views.call(v, m),
        "said_label": "Your check",
        "status_line": _status_line(v, m, result is not None),
        "say": list(say) if say is not None else None,
        "result": result,
    }


def _corrections(v: views.ViewInput, m: Moment) -> list[str]:
    """Prompts in this change after the done signal the check ran at, verbatim."""
    done = _extra(m).get("done_event")
    if not done:
        return []
    after = False
    found: list[str] = []
    for e in v.events:
        body = e["body"]
        if not after:
            after = (
                e["type"] == "task.event"
                and body.get("kind") == "done"
                and body.get("spool_id") == done
            )
            continue
        if e.get("change") != m.change_id:
            continue
        prompt = (
            body.get("prompt") if e["type"] in ("task.started", "task.event") else None
        )
        if prompt and (e["type"] == "task.started" or body.get("kind") == "prompt"):
            found.append(str(prompt))
    return found


def _questions(v: views.ViewInput, m: Moment) -> list[str]:
    """Questions the agent asked through its ask tool in this change, after the offer."""
    after = False
    found: list[str] = []
    for e in v.events:
        if not after:
            after = e["type"] == "moment.offered" and e.get("moment") == m.id
            continue
        body = e["body"]
        if (
            e["type"] == "task.event"
            and body.get("kind") == "ask"
            and body.get("question")
            and e.get("change") == m.change_id
        ):
            found.append(str(body["question"]))
    return found


def _outside(m: Moment, k) -> list[str]:
    """Changed non-test paths outside the categories of the first edits (learning.md
    4.3: shown, not scored)."""
    cats = [str(c) for c in (m.extra or {}).get("categories") or ()]
    if k is None or not cats:
        return []
    return [
        p
        for p in k.undone_paths
        if gitwatch.category(p) not in cats and not gitwatch.is_test_path(p)
    ]


def _notes(v: views.ViewInput, m: Moment, k=None) -> list[str]:
    notes = words_brief.corrections_lines(_corrections(v, m))
    asked = words_brief.questions_line(_questions(v, m))
    outside = words_brief.outside_line(
        [str(c) for c in (m.extra or {}).get("categories") or ()], _outside(m, k)
    )
    return notes + ([asked] if asked else []) + ([outside] if outside else [])


def _more(v: views.ViewInput, m: Moment, k) -> dict:
    matched, scored, _ = views.counts(v, KIND)
    rows = []
    if k is not None and k.tests:
        t = k.tests[0]
        rows.append(
            {
                "id": t.id,
                "name": t.id.rsplit("::", 1)[-1],
                "text": words_brief.more_row(k),
            }
        )
    return {
        "rows": rows,
        "checked": words_brief.CHECKED if k is not None else None,
        "commands": [s.command for s in k.steps] if k is not None else [],
        "counts": words_brief.counts_line(matched, scored) if scored else None,
        "sure": None,
        "sent": None,
        "dispute": None,
        "notes": _notes(v, m, k),
    }


def _you_said(m: Moment) -> str:
    said = words.answer_text(m)
    test = words_brief.test_name(m) if _extra(m).get("test") else None
    return f"{said} {test}" if test and said.startswith('"') else said


def result_view(v: views.ViewInput, m: Moment) -> dict | None:
    """The result once settled (or skipped, or closed). Null while the call is live."""
    if m.state not in REVEALED or m.state == "sealed":
        return None
    ran = v.last(m.id, "check.ran")
    k = views.key_from_ran(ran["body"], m) if ran is not None else None
    chip, label = views.chip(v, m)
    if k is None and m.state != "settled":
        return None
    reason = None
    if chip == "not_scored":
        reason = (
            words.DONT_KNOW_REASON
            if m.answer == "dont_know"
            else words_brief.unscored_text(_reason_of(v, m))
        )
    return {
        "headline": words_brief.HEADLINE,
        "chip": chip,
        "chip_label": label,
        "reason": reason,
        "said_label": "Your check",
        "you_said": _you_said(m),
        "what_happened": words_brief.what_happened(k) if k is not None else [],
        "cue": views.cue(v, m, k) if k is not None else None,
        "back": words.back_line(m.task_name),
        "more": _more(v, m, k),
    }


def happened(v: views.ViewInput, m: Moment) -> str:
    """The journal's What happened row."""
    result = result_view(v, m)
    if result is not None and result["what_happened"]:
        return " ".join(result["what_happened"]) + " Checked by a run."
    if result is not None and result["reason"]:
        return result["reason"]
    return _status_line(v, m, False) or words.MOVED_ON


def now_row(m: Moment) -> dict:
    confirm = m.state == "sealed"
    return {
        "id": m.id,
        "ref": views.short_ref(m.id),
        "reason": words_brief.CONFIRM_REASON if confirm else words_brief.REASON,
        "task": m.task_name,
        "size": "One tap" if confirm else words_brief.SIZE,
        "href": f"/q/{views.short_ref(m.id)}",
    }


def waiting(v: views.ViewInput, project_id: str) -> list[dict]:
    rows = [
        m
        for m in sorted(v.moments.values(), key=lambda x: x.id, reverse=True)
        if m.project_id == project_id
        and m.kind == KIND
        and m.state == "sealed"
        and not asking(m)
    ]
    return [
        {
            "id": m.id,
            "ref": views.short_ref(m.id),
            "kind": LABEL,
            "text": words_brief.WAITING_ROW
            if words_brief.phase(m) == "building"
            else words_brief.CHECK_ROW,
            "href": f"/q/{views.short_ref(m.id)}",
        }
        for m in rows
    ]
