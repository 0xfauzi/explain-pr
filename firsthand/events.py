"""The spool line codec and the secret scan.

A spool line is one JSON object per line in run/spool.jsonl. The dispatcher
appends, the daemon reads. `scan_secrets` is used on every free-text field before
it enters the spool or the record.
"""

from __future__ import annotations

import json
import re
import secrets
from collections.abc import Mapping
from datetime import UTC, datetime

from firsthand.model import SpoolEvent

SPOOL_VERSION = 1
MAX_PROMPT_CHARS = 20_000
MAX_LINE_BYTES = 65_536
MAX_FAILING = 50
MAX_FAILING_CHARS = 300
MAX_QUESTION_CHARS = 2_000

EVENT_KINDS = frozenset(
    {
        "session_start",
        "prompt_submit",
        "before_tool",
        "after_tool",
        "tool_failed",
        "turn_end",
    }
)
TOOL_KINDS = frozenset({"edit", "shell", "ask", "plan", "other"})

_BASE_KEYS = ("v", "id", "at", "agent", "session", "cwd", "event")
_TOOL_KEYS = ("tool", "tool_use", "command", "exit", "failing", "paths")
_KEYS_BY_EVENT: dict[str, tuple[str, ...]] = {
    "session_start": ("source", "venv"),
    "prompt_submit": ("prompt", "prompt_cut", "venv"),
    "before_tool": (*_TOOL_KEYS, "question"),
    "after_tool": _TOOL_KEYS,
    "tool_failed": (*_TOOL_KEYS, "interrupted"),
    "turn_end": (),
}
_TRUE_ONLY = ("prompt_cut", "interrupted", "sub")

# Order matters: a private key block and a bearer token are replaced before the
# generic assignment rule could take part of them.
_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private-key",
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?(?:-----END [A-Z0-9 ]*PRIVATE KEY-----|\Z)",
            re.DOTALL,
        ),
    ),
    ("aws-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "github-token",
        re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}"),
    ),
    ("slack-token", re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("api-key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
)
# A name holding secret, token, password or credential anywhere (AWS_SECRET_ACCESS_KEY,
# GH_TOKEN, db_password), or an api, access, private, auth or signing key.
_ASSIGNMENT = re.compile(
    r"(?P<name>(?:[A-Za-z0-9_.-]*(?:secret|token|passw(?:or)?d|credentials?)"
    r"|[A-Za-z0-9_.-]*(?:api|access|private|auth|signing)[_-]?key)"
    r"[A-Za-z0-9_.-]*\s*[:=](?!:)\s*)(?P<value>\S{8,})",  # not a pytest id's "::"
    re.IGNORECASE,
)
# The password in scheme://user:password@host, and in mysql -p<password>.
_VALUE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "url-password",
        re.compile(
            r"(?P<keep>\b[a-z][a-z0-9+.-]*://[^\s:/@]+:)(?P<value>[^\s@/]+)(?=@)",
            re.IGNORECASE,
        ),
    ),
    (
        "mysql-password",
        re.compile(r"(?P<keep>\bmysql\w*\b[^\n|;&]*?\s-p)(?P<value>[^\s\[]\S*)"),
    ),
)


def now_stamp(now: datetime | None = None) -> str:
    """UTC to the second, as "2026-11-14T09:12:03Z"."""
    moment = now or datetime.now(UTC)
    if moment.tzinfo is not None:
        moment = moment.astimezone(UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def new_event_id() -> str:
    return secrets.token_hex(6)


def scan_secrets(text: str) -> tuple[str, list[str]]:
    """Return the text with each secret replaced by [redacted: <kind>], and the kinds found."""
    found: list[str] = []
    for kind, pattern in _SECRET_PATTERNS:
        text, count = pattern.subn(f"[redacted: {kind}]", text)
        if count:
            found.append(kind)

    def _assign(match: re.Match[str]) -> str:
        if match.group("value").startswith("[redacted:"):
            return match.group(0)
        found.append("assignment")
        return match.group("name") + "[redacted: assignment]"

    text = _ASSIGNMENT.sub(_assign, text)
    for kind, pattern in _VALUE_PATTERNS:
        text, count = pattern.subn(
            lambda m, kind=kind: m.group("keep") + f"[redacted: {kind}]", text
        )
        if count:
            found.append(kind)
    return text, list(dict.fromkeys(found))


def _clean_failing(value: object) -> list[str]:
    if not isinstance(value, list | tuple):
        return []
    return [str(item)[:MAX_FAILING_CHARS] for item in value[:MAX_FAILING]]


def _shape(line: Mapping[str, object]) -> dict[str, object]:
    """Keep only the keys this event may carry, in a fixed order."""
    event = line.get("event")
    allowed = _KEYS_BY_EVENT.get(str(event), ())
    out: dict[str, object] = {"v": SPOOL_VERSION}
    for name in (*_BASE_KEYS[1:], *allowed):
        if name in _TRUE_ONLY:
            if line.get(name):
                out[name] = True
            continue
        if name in line:
            out[name] = line[name]
        elif name in allowed:
            out[name] = [] if name in ("failing", "paths") else None
    if line.get("sub"):
        out["sub"] = True
    if "failing" in out:
        out["failing"] = _clean_failing(out["failing"])
    return out


def encode(line: Mapping[str, object]) -> bytes:
    """One JSON line ending in a newline. Unknown keys are dropped.

    A prompt is cut to MAX_PROMPT_CHARS. Raises ValueError when the line is still
    over MAX_LINE_BYTES after that.
    """
    out = _shape(line)
    prompt = out.get("prompt")
    if isinstance(prompt, str) and len(prompt) > MAX_PROMPT_CHARS:
        out["prompt"] = prompt[:MAX_PROMPT_CHARS]
        out["prompt_cut"] = True
    data = (json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    if len(data) > MAX_LINE_BYTES:
        raise ValueError(f"spool line is {len(data)} bytes, over {MAX_LINE_BYTES}")
    return data


def _opt_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _opt_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _str_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def _required(obj: Mapping[str, object]) -> dict[str, str] | None:
    out: dict[str, str] = {}
    for name in _BASE_KEYS[1:]:
        value = obj.get(name)
        if not isinstance(value, str):
            return None
        out[name] = value
    return out


def decode(raw: bytes | str) -> SpoolEvent | None:
    """A SpoolEvent, or None for a blank, malformed or unknown-version line."""
    try:
        text = raw.decode() if isinstance(raw, bytes) else raw
        if not text.strip():
            return None
        obj = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(obj, dict) or obj.get("v") != SPOOL_VERSION:
        return None
    base = _required(obj)
    if base is None or base["event"] not in EVENT_KINDS:
        return None
    tool = obj.get("tool")
    return SpoolEvent(
        **base,  # type: ignore[arg-type]
        tool=tool if tool in TOOL_KINDS else None,  # type: ignore[arg-type]
        tool_use=_opt_str(obj.get("tool_use")),
        command=_opt_str(obj.get("command")),
        exit=_opt_int(obj.get("exit")),
        failing=_str_tuple(obj.get("failing")),
        paths=_str_tuple(obj.get("paths")),
        prompt=_opt_str(obj.get("prompt")),
        prompt_cut=obj.get("prompt_cut") is True,
        source=_opt_str(obj.get("source")),
        venv=_opt_str(obj.get("venv")),
        sub=obj.get("sub") is True,
        interrupted=obj.get("interrupted") is True,
        question=_opt_str(obj.get("question")),
    )
