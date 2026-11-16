"""Fields the Room's pages read on top of the read models (build-room.md section 3).

Each one is derived from recorded events or from state the views already read.
Nothing here changes an event, the record format or scoring. Split from `views`
to keep each file under the size limit.
"""

from __future__ import annotations

from collections.abc import Mapping

from firsthand import views, words, words_brief, words_callit
from firsthand.model import Key, Moment
from firsthand.moments import revert_test

CONFIRM_TEXT = "Is this your check?"
_RUN_LABELS = {views.CALL: "fix undone"}
_CONFIDENCE = {"high": "Sure", "low": "Not sure"}


# ------------------------------------------------------------- the answer


def _revert_said(m: Moment, answer: str) -> tuple[str, list[str]]:
    if answer == "dont_know":
        return "Don't know", []
    if len(m.tests) == 1:
        said = {"fails": "Fails", "passes": "Still passes"}.get(answer, answer)
        return said, [m.tests[0].name]
    if answer == "none":
        return "None", []
    numbers = revert_test.picked_numbers(answer, len(m.tests)) or ()
    if not numbers:
        return answer, []
    return words._and([str(x) for x in numbers]), [m.tests[x - 1].name for x in numbers]


def _callit_said(m: Moment, answer: str) -> tuple[str, list[str]]:
    if answer == "dont_know":
        return "Don't know", []
    listed = words_callit.picks(m)
    if answer.isdigit() and 1 <= int(answer) <= len(listed):
        return answer, [str(listed[int(answer) - 1]["path"])]
    if answer.isdigit():
        return f"{answer}, somewhere else", []
    return answer, []


def _brief_said(m: Moment) -> tuple[str, list[str]]:
    said = words_brief.answer_text(m).rstrip(".")
    names = [words_brief.test_name(m)] if (m.extra or {}).get("test") else []
    return said, names


def said(m: Moment, answer: str | None) -> tuple[str, list[str]]:
    """The answer in words with no test name, path or confidence, and the machine
    names it refers to."""
    if m.kind == views.BRIEF:
        return _brief_said(m)
    if answer is None:
        return words.answer_text(m).rstrip("."), []
    if m.kind == views.CALL:
        return _callit_said(m, answer)
    return _revert_said(m, answer)


def answer_line(m: Moment) -> str:
    """said, a full stop, then the confidence: "1 and 3. Sure." A quoted line keeps
    its closing quote as its end."""
    if m.answer is None:
        return words.answer_text(m)
    text, _ = said(m, m.answer)
    if not text.endswith('"'):
        text += "."
    conf = _CONFIDENCE.get(m.confidence or "")
    return f"{text} {conf}." if conf else text


def locked_at(v: views.ViewInput, m: Moment) -> str | None:
    sealed = v.last(m.id, "call.sealed")
    if sealed is None:
        return None
    return sealed["body"].get("picked_at") or sealed["at"]


def _confirm(v: views.ViewInput, m: Moment) -> dict | None:
    if m.kind != views.BRIEF:
        return None
    e = v.last(m.id, "call.confirmed")
    return {"value": e["body"].get("value"), "at": e["at"]} if e else None


# ------------------------------------------------------------- the question


def question_fields(v: views.ViewInput, m: Moment, view: dict) -> dict:
    """Adds the Room's fields to a question view, in place, and returns it."""
    confirm = m.kind == views.BRIEF and view.get("form") == "pick"
    view.update(
        {
            "no": v.numbers.get(m.id),
            "kind_label": views.KIND_LABELS[m.kind],
            "skill": views.SKILL_WORDS[m.kind],
            "where": {
                "project": views.project_name(v, m.project_id),
                "task": m.task_name,
                "since": words.clock_time(m.base_at, v.tz)
                if m.kind == views.REVERT
                else None,
            },
            "prompt_text": CONFIRM_TEXT if confirm else view["prompt"],
            "prompt_name": words_brief.test_name(m) if confirm else None,
        }
    )
    held = view.get("held")
    if held and held.get("kind") == "pick":
        text, names = said(m, held.get("answer"))
        held.update({"at": (m.pending or {}).get("at"), "said": text, "names": names})
    call = view.get("call")
    if call:
        text, names = said(m, m.answer)
        call.update(
            {
                "locked_at": locked_at(v, m),
                "said": text,
                "names": names,
                "confirm": _confirm(v, m),
            }
        )
    return view


# ---------------------------------------------------------------- the result


def _revert_facts(k: Key) -> list[dict]:
    return [
        {
            "k": t.id.rsplit("::", 1)[-1],
            "v": words.more_row(t),
            "key": t.result == "still_passes",
        }
        for t in k.tests
    ]


def _callit_facts(m: Moment, k: Key) -> list[dict]:
    from firsthand.moments import call_it

    facts = [{"k": "the fix", "v": p, "key": True} for p in call_it.fix_paths(k)]
    facts.append(
        {"k": words_callit.name(m), "v": words_callit.more_row(k), "key": False}
    )
    return facts


def _brief_facts(k: Key) -> list[dict]:
    if len(k.tests) != 1:
        return []
    t = k.tests[0]
    return [
        {
            "k": t.id.rsplit("::", 1)[-1],
            "v": words_brief.more_row(k),
            "key": t.result == "still_passes",
        }
    ]


def _facts(m: Moment, k: Key | None) -> list[dict]:
    if k is None:
        return []
    if m.kind == views.CALL:
        return _callit_facts(m, k)
    if m.kind == views.BRIEF:
        return _brief_facts(k)
    return _revert_facts(k)


def _names(m: Moment, facts: list[dict], result: Mapping) -> list[str]:
    names = [f["v"] if f["k"] == "the fix" else f["k"] for f in facts]
    if m.kind == views.CALL:
        names += [str(p["path"]) for p in words_callit.picks(m)]
    cue = result.get("cue") or {}
    names += [str(e["path"]) for e in cue.get("evidence", ())]
    out: list[str] = []
    for n in names:
        if n and n not in out:
            out.append(n)
    return out


def result_fields(
    v: views.ViewInput, m: Moment, result: dict, ran: Mapping | None, k: Key | None
) -> dict:
    """Adds the Room's fields to a result view, in place, and returns it."""
    facts = _facts(m, k)
    more = result.get("more") or {}
    result.update(
        {
            "ran_at": ran["at"] if ran is not None else None,
            "run_label": _RUN_LABELS.get(m.kind, "change undone"),
            "facts": facts,
            "names": _names(m, facts, result),
            "counts": more.get("counts"),
            "fresh": not m.opened,
        }
    )
    if m.kind == views.CALL:
        more["why"] = words_callit.pick_more_rows(m)
    return result


# ------------------------------------------------------------ inbox, journal


def happened(v: views.ViewInput, m: Moment) -> tuple[str, bool]:
    """The journal's What happened text, and whether it came from a run."""
    result = views.result_view(v, m)
    ran = bool(result and result.get("ran_at"))
    if m.kind == views.CALL:
        return views._callit().happened(v, m), ran
    if m.kind == views.BRIEF:
        return views._brief().happened(v, m), ran
    if result:
        return " ".join(result["what_happened"][:1]) + " Checked by a run.", ran
    return views.status_line(v, m, False) or words.MOVED_ON, False


def offered_at(v: views.ViewInput, m: Moment) -> str:
    offered = v.last(m.id, "moment.offered")
    return offered["at"] if offered else m.offered_at


def inbox_fields(v: views.ViewInput, view: dict) -> dict:
    """Adds the Room's fields to the inbox view, in place, and returns it."""
    for item in view["now"]:
        m = v.moments[item["id"]]
        item["no"] = v.numbers.get(m.id)
        item["kind_label"] = views.KIND_LABELS[m.kind]
        item["since"] = (
            words.clock_time(m.base_at, v.tz) if m.kind == views.REVERT else None
        )
    for item in view["waiting"]:
        m = v.moments[item["id"]]
        item.update(
            {
                "no": v.numbers.get(m.id),
                "task": m.task_name,
                "said": answer_line(m),
                "locked_at": locked_at(v, m),
            }
        )
    for item in view["results"]:
        m = v.moments[item["id"]]
        text, ran = happened(v, m)
        item.update(
            {
                "no": v.numbers.get(m.id),
                "at": offered_at(v, m),
                "said": answer_line(m),
                "happened": text,
                "ran": ran,
            }
        )
    view["next_no"] = len(v.numbers) + 1
    view["asked"] = {"today": views.asked_today(v), "limit": v.settings.daily_limit}
    return view


def journal_moment_fields(v: views.ViewInput, m: Moment, entry: dict) -> dict:
    text, ran = happened(v, m)
    at = entry["at"]
    entry.update(
        {
            "no": v.numbers.get(m.id),
            "time": f"{words.short_date(at, v.tz)} {words.clock_time(at, v.tz)}",
            "said": answer_line(m),
            "happened": text,
            "ran": ran,
        }
    )
    return entry


def journal_note_fields(v: views.ViewInput, note: dict, entry: dict) -> dict:
    at = note["at"]
    entry.update(
        {
            "no": None,
            "time": f"{words.short_date(at, v.tz)} {words.clock_time(at, v.tz)}",
            "evidence": list(note["body"].get("evidence", ())),
        }
    )
    return entry
