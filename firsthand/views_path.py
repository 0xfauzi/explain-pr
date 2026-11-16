"""The picture of a Call it failure: the route the failing test took, drawn.

The question and its result draw the same structure. The test starts the path;
each file the trace names follows, outermost first, once each; the picks that
are not on the path sit below it. On the question a stop names only a file and
a line: nothing says why a file was listed or where the fix landed. The result
adds the person's answer and the fix files.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from firsthand import words_callit
from firsthand.model import Moment

LEAD = "The picture shows the path of the failure."
NOTE = "The failure shows here:"
OFF = "Not on the path of the failure."
SAID = "your answer"
FIX = "the fix landed here"
FLOW_STOPS = 2  # the test and two files fit across the page


def _split(path: str) -> tuple[str | None, str]:
    head, _, tail = path.rpartition("/")
    return (head + "/" if head else None), tail


def _frames(m: Moment) -> list[Mapping[str, object]]:
    return list((m.extra or {}).get("frames", ()))  # type: ignore[arg-type]


def trace_files(m: Moment) -> list[tuple[str, int]]:
    """Each file the trace names, outermost first, with the line of its last frame.

    The test's own file is left out when its only frame is the test itself."""
    frames = _frames(m)
    test_file = words_callit.failing_id(m).split("::", 1)[0]
    paths = [str(f["path"]) for f in frames]
    order: list[str] = []
    lines: dict[str, int] = {}
    for f in frames:
        path = str(f["path"])
        if path == test_file and paths.count(path) == 1:
            continue
        if path not in order:
            order.append(path)
        lines[path] = int(str(f["line"]))
    return [(p, lines[p]) for p in order]


def _stop(path: str, line: int | None, value: str | None, on_path: bool) -> dict:
    folder, file = _split(path)
    return {
        "path": path,
        "dir": folder,
        "file": file,
        "line": line,
        "value": value,
        "on_path": on_path,
        "end": False,
        "said": False,
        "fix": False,
    }


def _said_path(m: Moment, answer: str | None) -> str | None:
    listed = words_callit.picks(m)
    if answer and answer.isdigit() and 1 <= int(answer) <= len(listed):
        return str(listed[int(answer) - 1]["path"])
    return None


def picture(
    m: Moment, answer: str | None = None, fix: Sequence[str] = ()
) -> dict | None:
    """The stops in order. `answer` and `fix` are given only by `result_picture`."""
    if not _frames(m):
        return None
    value = {str(p["path"]): str(p["n"]) for p in words_callit.picks(m)}
    traced = trace_files(m)
    stops = [_stop(p, line, value.get(p), True) for p, line in traced]
    if stops:
        stops[-1]["end"] = True
    on_path = {p for p, _ in traced}
    off = [p for p in value if p not in on_path]
    off += [p for p in fix if p not in on_path and p not in off]
    stops += [_stop(p, None, value.get(p), False) for p in off]
    said = _said_path(m, answer)
    for s in stops:
        s["said"] = s["path"] == said
        s["fix"] = s["path"] in fix
    message = (m.extra or {}).get("message")
    return {
        "lead": LEAD,
        "test": words_callit.name(m),
        "flow": len(traced) == FLOW_STOPS,
        "message": str(message) if message else None,
        "stops": stops,
        "words": {"note": NOTE, "off": OFF},
    }


def result_picture(m: Moment, answer: str | None, fix: Sequence[str]) -> dict | None:
    """The picture on a result: the answer and the fix are marked on it."""
    drawn = picture(m, answer, fix)
    if drawn is not None:
        drawn["words"].update({"said": SAID, "fix": FIX})
    return drawn
