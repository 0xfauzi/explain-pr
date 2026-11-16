"""Read models for Call it: its card, its result and its Waiting row.

The shapes are those of build-2a-contract.md section 7.2, plus `trace` on the
card and `path` on each file pick. Why a file is listed is shown only in the
result's More, after the answer is sealed. As in `views`, a result comes only from a
`check.ran` event in the record, never from the key store.
"""

from __future__ import annotations

from firsthand import views, views_path, views_room, words, words_callit
from firsthand.model import REVEALED, Moment

KIND = "call_it"
LABEL = "Call it"
SIZE = "One tap"


def _status_line(v: views.ViewInput, m: Moment, has_result: bool) -> str | None:
    if has_result:
        return None
    if m.state == "sealed":
        return words_callit.waiting_line(m)
    scored = v.last(m.id, "call.scored")
    reason = scored["body"].get("unscored_reason") if scored else None
    if reason in ("never-green",):
        return words_callit.NEVER_GREEN
    if v.last(m.id, "check.unavailable") is not None or reason == "check-unavailable":
        return words.CHECK_DROPPED
    if m.state == "closed":
        return {
            "fix-started": words_callit.FIX_STARTED,
            "moved-on": words.MOVED_ON,
        }.get(m.close_how or "")
    return None


def _can(v: views.ViewInput, m: Moment) -> dict:
    held_pick = m.state == "held" and (m.pending or {}).get("kind") == "pick"
    return {
        "lock": m.state == "open",
        "undo": m.state == "held",
        "confidence": held_pick,
        "show": held_pick,
        "skip": m.state == "open",
        "wrong_start": False,
        "dispute": False,
    }


def question_view(v: views.ViewInput, m: Moment, say=None) -> dict:
    result = result_view(v, m)
    return {
        "id": m.id,
        "ref": views.short_ref(m.id),
        "kind": m.kind,
        "state": m.state,
        "reason": words_callit.REASON,
        "skip_ok": True,
        "context": words_callit.context_line(m, views.project_name(v, m.project_id)),
        "lead": None,
        "evidence": [],
        "trace": words_callit.trace(m),
        "path": views_path.picture(m),
        "prompt": words_callit.PROMPT,
        "picks": words_callit.pick_rows(m),
        "multi": False,
        "footer": words_callit.FOOTER,
        "line": v.lines.get(m.id),
        "can": _can(v, m),
        "held": views.held(m),
        "call": views.call(v, m),
        "status_line": _status_line(v, m, result is not None),
        "say": list(say) if say is not None else None,
        "result": result,
    }


def _chip(v: views.ViewInput, m: Moment) -> tuple[str, str]:
    return views.chip(v, m)


def _reason(v: views.ViewInput, m: Moment, k) -> str | None:
    if m.answer == "dont_know":
        return words.DONT_KNOW_REASON
    if m.state == "skipped":
        return words.SKIPPED_REASON
    if m.state == "closed":
        return (
            words_callit.FIX_STARTED if m.close_how == "fix-started" else words.MOVED_ON
        )
    scored = v.last(m.id, "call.scored")
    reason = scored["body"].get("unscored_reason") if scored else None
    return words_callit.unscored_text(reason, k)


def _cue(v: views.ViewInput, m: Moment, k) -> dict | None:
    scored = v.last(m.id, "call.scored")
    if not scored or scored["body"]["result"] != "miss":
        return None
    text = words_callit.cue_text(k)
    if text is None:
        return None
    from firsthand.moments import call_it

    path = call_it.cue_path(k)
    line = words_callit.cue_line(k)
    evidence = []
    if path is not None and line is not None:
        source = v.read_source(m.project_id, m.base_tree, path)
        evidence.append(
            {"path": path, "line": line, "text": views.line_of(source, line)}
        )
    return {"text": text, "evidence": evidence}


def _more(v: views.ViewInput, m: Moment, k) -> dict:
    matched, scored, fixed = views.counts(v, KIND)
    test = words_callit.failing_id(m)
    return {
        "rows": [
            {"id": test, "name": words_callit.name(m), "text": words_callit.more_row(k)}
        ]
        + words_callit.pick_more_rows(m),
        "checked": words.checked_line("pytest"),
        "commands": [s.command for s in k.steps],
        "counts": words_callit.counts_line(matched, scored, fixed) if scored else None,
        "sure": views.sure(v, KIND),
        "sent": None,
        "dispute": None,
    }


def _result_path(m: Moment, k) -> dict | None:
    from firsthand.moments import call_it

    return views_path.result_picture(m, m.answer, call_it.fix_paths(k))


def result_view(v: views.ViewInput, m: Moment) -> dict | None:
    if m.state not in REVEALED:
        return None
    ran = v.last(m.id, "check.ran")
    if ran is None:
        return None
    k = views.key_from_ran(ran["body"], m)
    chip, label = _chip(v, m)
    result = {
        "headline": words_callit.HEADLINE,
        "chip": chip,
        "chip_label": label,
        "reason": _reason(v, m, k) if chip == "not_scored" else None,
        "you_said": words.you_said(m),
        "what_happened": words_callit.what_happened(k),
        "cue": _cue(v, m, k),
        "back": words.back_line(m.task_name),
        "more": _more(v, m, k),
        "path": _result_path(m, k),
    }
    return views_room.result_fields(v, m, result, ran, k)


def happened(v: views.ViewInput, m: Moment) -> str:
    """The journal's What happened row."""
    result = result_view(v, m)
    if result is not None:
        return " ".join(result["what_happened"]) + " Checked by a run."
    return _status_line(v, m, False) or words.MOVED_ON


def waiting(v: views.ViewInput, project_id: str) -> list[dict]:
    rows = [
        m
        for m in sorted(v.moments.values(), key=lambda x: x.id, reverse=True)
        if m.project_id == project_id
        and m.kind == KIND
        and m.state == "sealed"
        and v.last(m.id, "check.ran") is None
    ]
    return [
        {
            "id": m.id,
            "ref": views.short_ref(m.id),
            "kind": LABEL,
            "text": words_callit.waiting_row(m),
            "href": f"/q/{views.short_ref(m.id)}",
        }
        for m in rows
    ]
