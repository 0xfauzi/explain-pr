"""The key store and the one output rule.

A key holds what a check found. `KeyStore.reveal` is the only way to read one, and
it refuses until the person has answered, skipped or the question has closed.
`agent_output` is the only function whose return values go to an agent channel.
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass
from pathlib import Path

from firsthand import paths
from firsthand.model import REVEALED, Key, KeyItem, KeyLocked, Moment, StepRun, Want

KEY_FORMAT = 1


def _key_to_json(k: Key) -> dict:
    data = asdict(k)
    data["tests"] = [
        {
            "id": t.id,
            "result": t.result,
            "assert_line": t.assert_line,
            "assert_text": t.assert_text,
            "fail_line": t.fail_line,
        }
        for t in k.tests
    ]
    data["steps"] = [{**asdict(s), "failing": list(s.failing)} for s in k.steps]
    data["undone_paths"] = list(k.undone_paths)
    return {"v": KEY_FORMAT, **data}


def _key_from_json(data: dict) -> Key:
    return Key(
        moment=data["moment"],
        kind=data["kind"],
        how=data["how"],
        base_tree=data["base_tree"],
        head_tree=data["head_tree"],
        made_at=data["made_at"],
        tests=tuple(
            KeyItem(
                id=t["id"],
                result=t["result"],
                assert_line=t.get("assert_line"),
                assert_text=t.get("assert_text"),
                fail_line=t.get("fail_line"),
            )
            for t in data["tests"]
        ),
        steps=tuple(
            StepRun(
                step=s["step"],
                command=s["command"],
                exit=s.get("exit"),
                failing=tuple(s.get("failing", ())),
                output_sha256=s.get("output_sha256", ""),
            )
            for s in data.get("steps", ())
        ),
        undone_paths=tuple(data.get("undone_paths", ())),
        duration_s=float(data.get("duration_s", 0.0)),
        extra=data.get("extra"),
    )


class KeyStore:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = Path(directory) if directory is not None else paths.keys_dir()
        self._lock = threading.Lock()
        self._keys: dict[str, Key] = {}
        if self.directory.is_dir():
            for path in sorted(self.directory.glob("*.json")):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    k = _key_from_json(data)
                except (OSError, ValueError, KeyError, TypeError):
                    continue  # a broken key file is ignored: its check simply has no key
                self._keys[k.moment] = k

    def _file(self, check_id: str) -> Path:
        if self.directory == paths.keys_dir():
            return paths.key_file(check_id)
        paths.key_file(check_id)  # the same id check as the default folder
        return self.directory / f"{check_id}.json"

    def put(self, k: Key) -> None:
        """Keep the key in memory and in a 0600 file. Replaces an older key of the same id."""
        target = self._file(k.moment)
        with self._lock:
            self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            data = json.dumps(_key_to_json(k), indent=2, sort_keys=True) + "\n"
            paths.write_private(target, data.encode())
            self._keys[k.moment] = k

    def has(self, check_id: str) -> bool:
        with self._lock:
            return check_id in self._keys

    def reveal(
        self, check_id: str, moment: Moment | None, *, silent: bool = False
    ) -> Key:
        """The gate. KeyLocked unless the moment is revealed, or there is none and silent."""
        allowed = (moment is not None and moment.state in REVEALED) or (
            moment is None and silent
        )
        if not allowed:
            raise KeyLocked(
                "This result cannot be shown before the question is answered."
            )
        with self._lock:
            if check_id not in self._keys:
                raise KeyError(check_id)
            return self._keys[check_id]

    def discard(self, check_id: str) -> None:
        with self._lock:
            self._keys.pop(check_id, None)
            try:
                self._file(check_id).unlink(missing_ok=True)
            except ValueError:
                pass

    def pending(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._keys))


@dataclass(frozen=True)
class OutputContext:
    room_url: str | None
    work_computer: bool
    work_notice: bool
    task_name: str
    high_stakes: str | None = None
    ack: str | None = None


def _no_key_line(want: Want, moment: Moment | None, ctx: OutputContext) -> str | None:
    """The lines that carry no result: the question, an ack, the pending line."""
    from firsthand import words  # imported here: words imports this module's types

    if want == "question":
        ok = moment is not None and moment.state == "open"
        return words.question_line(moment, ctx) if ok else None  # type: ignore[arg-type]
    if want == "ack":
        return words.ack_line(ctx.ack, ctx.task_name)
    if want in ("work", "confirm"):
        return _brief_line(want, moment, ctx)
    ok = moment is not None and moment.state == "sealed"
    return words.pending_line(moment, ctx) if ok else None  # type: ignore[arg-type]


def _brief_line(want: Want, moment: Moment | None, ctx: OutputContext) -> str | None:
    """The Brief's two lines with no result: the person's own line passed to the
    agent ("work"), and "Is this your check?" ("confirm"), which names a test only."""
    from firsthand import words_brief

    if moment is None or moment.kind != "brief" or moment.state != "sealed":
        return None
    phase = words_brief.phase(moment)
    if want == "work":
        return words_brief.work_line(moment) if words_brief.line_of(moment) else None
    if phase == "confirm" and not (moment.extra or {}).get("confirm"):
        return words_brief.confirm_line(moment, ctx)
    return None


def _key_line(
    want: Want, moment: Moment | None, key: Key, ctx: OutputContext
) -> str | None:
    """The lines that carry a result, made from a key the store has revealed."""
    from firsthand import words

    if want == "result":
        return "\n".join(words.result_lines(moment, key, ctx)) if moment else None
    if want == "finding":
        return words.finding_line(key)
    if want == "fact":
        return words.fact_line(key, ctx.high_stakes or "")
    return None


def agent_output(
    want: Want,
    *,
    moment: Moment | None,
    store: KeyStore,
    check_id: str | None = None,
    silent: bool = False,
    ctx: OutputContext,
) -> str | None:
    """The one output rule: everything for an agent channel comes from here."""
    if want in ("question", "ack", "pending", "work", "confirm"):
        return _no_key_line(want, moment, ctx)
    ref = check_id or (moment.id if moment is not None else None)
    if ref is None:
        return None
    try:
        key = store.reveal(ref, moment, silent=silent)
    except (KeyLocked, KeyError):
        return None  # too early, or nothing to say
    return _key_line(want, moment, key, ctx)
