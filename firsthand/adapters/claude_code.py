"""The Claude Code adapter: hook payloads to spool lines, and replies to hook output.

`render` is the only place that shapes what a hook prints. It never returns a
permission decision, a `continue` flag or `hookSpecificOutput`.
"""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Mapping
from pathlib import Path

from firsthand import events

NAME = "claude-code"
EVENTS = {
    "SessionStart": "session_start",
    "UserPromptSubmit": "prompt_submit",
    "PreToolUse": "before_tool",
    "PostToolUse": "after_tool",
    "PostToolUseFailure": "tool_failed",
    "Stop": "turn_end",
}
MATCHER_EVENTS = ("PreToolUse", "PostToolUse", "PostToolUseFailure")
TOOL_KINDS = {
    "Edit": "edit",
    "Write": "edit",
    "MultiEdit": "edit",
    "Bash": "shell",
    "AskUserQuestion": "ask",
    "ExitPlanMode": "plan",
    "EnterPlanMode": "plan",
}
HOOK_TIMEOUT_S = 5
PROCESS_NAMES = ("claude",)
ENV_MARKERS = ("CLAUDECODE",)

MAX_OUTPUT_CHARS = 10_000
MAX_FAILING = 50
MAX_FAILING_CHARS = 300
SKILL_FILE = "claude_code_skill.md"

_EXIT_LINE = re.compile(r"^Exit code (-?\d+)\s*$")
_FAILED_LINE = re.compile(r"^FAILED (\S+)")
_TOOL_EVENTS = ("before_tool", "after_tool", "tool_failed")


def _text(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _scanned(value: object) -> str | None:
    text = _text(value)
    if text is None:
        return None
    return events.scan_secrets(text)[0]


def parse_exit(error: str) -> int | None:
    """The exit code from a first line "Exit code N", or None when that line is missing."""
    first = error.split("\n", 1)[0].strip() if isinstance(error, str) else ""
    match = _EXIT_LINE.match(first)
    return int(match.group(1)) if match else None


def parse_failing(text: str) -> list[str]:
    """Test ids from lines that start "FAILED <id>", at most 50 of at most 300 characters."""
    if not isinstance(text, str):
        return []
    found: list[str] = []
    for line in text.splitlines():
        match = _FAILED_LINE.match(line)
        if match:
            found.append(match.group(1)[:MAX_FAILING_CHARS])
            if len(found) == MAX_FAILING:
                break
    return found


def _shell_result(kind: str, payload: Mapping[str, object]) -> dict[str, object]:
    """exit and failing for a shell call: 0 on success, parsed from `error` on failure."""
    if kind == "after_tool":
        response = payload.get("tool_response")
        stdout = response.get("stdout") if isinstance(response, Mapping) else None
        return {"exit": 0, "failing": parse_failing(_text(stdout) or "")}
    if kind == "tool_failed":
        error = _text(payload.get("error")) or ""
        return {"exit": parse_exit(error), "failing": parse_failing(error)}
    return {}


def ask_text(tool_input: Mapping[str, object]) -> str | None:
    """The ask tool's question texts, joined, scanned and cut. None when there are none."""
    questions = tool_input.get("questions")
    found: list[str] = []
    if isinstance(questions, list):
        for q in questions:
            text = _text(q.get("question")) if isinstance(q, Mapping) else None
            if text and text.strip():
                found.append(" ".join(text.split()))
    if not found:
        return None
    joined = _scanned(" / ".join(found)) or ""
    return joined[: events.MAX_QUESTION_CHARS] or None


def _tool_fields(kind: str, payload: Mapping[str, object]) -> dict[str, object]:
    tool = TOOL_KINDS.get(_text(payload.get("tool_name")) or "", "other")
    tool_input = payload.get("tool_input")
    tool_input = tool_input if isinstance(tool_input, Mapping) else {}
    file_path = _text(tool_input.get("file_path")) if tool == "edit" else None
    fields: dict[str, object] = {
        "tool": tool,
        "tool_use": _text(payload.get("tool_use_id")),
        "command": _scanned(tool_input.get("command")) if tool == "shell" else None,
        "exit": None,
        "failing": [],
        "paths": [file_path] if file_path else [],
    }
    if tool == "shell":
        fields.update(_shell_result(kind, payload))
    if tool == "ask" and kind == "before_tool":
        fields["question"] = ask_text(tool_input)
    if kind == "tool_failed" and payload.get("is_interrupt") is True:
        fields["interrupted"] = True
    return fields


def _prompt_fields(
    payload: Mapping[str, object], environ: Mapping[str, str]
) -> dict[str, object]:
    prompt = _scanned(payload.get("prompt")) or ""
    fields: dict[str, object] = {"prompt": prompt, "venv": environ.get("VIRTUAL_ENV")}
    if len(prompt) > events.MAX_PROMPT_CHARS:
        fields["prompt"] = prompt[: events.MAX_PROMPT_CHARS]
        fields["prompt_cut"] = True
    return fields


def to_spool(
    event_name: str,
    payload: Mapping[str, object],
    *,
    at: str,
    event_id: str,
    environ: Mapping[str, str],
) -> dict | None:
    """A spool line for one hook call, or None for an unknown event or no session id.

    Reads only the fields listed in build-2.md section 4. Never reads
    `transcript_path` or `last_assistant_message`.
    """
    kind = EVENTS.get(event_name)
    session = payload.get("session_id") if isinstance(payload, Mapping) else None
    if kind is None or not isinstance(session, str) or not session:
        return None
    line: dict[str, object] = {
        "v": events.SPOOL_VERSION,
        "id": event_id,
        "at": at,
        "agent": NAME,
        "session": session,
        "cwd": _text(payload.get("cwd")) or "",
        "event": kind,
    }
    if payload.get("agent_id"):
        line["sub"] = True
    if kind == "session_start":
        line["source"] = _text(payload.get("source"))
        line["venv"] = environ.get("VIRTUAL_ENV")
    elif kind == "prompt_submit":
        line.update(_prompt_fields(payload, environ))
    elif kind in _TOOL_EVENTS:
        line.update(_tool_fields(kind, payload))
    return line


def render(event: str, reply: Mapping[str, object]) -> str:
    """What the hook prints on stdout for a reply file. Usually the empty string.

    `event` is the spool kind (`turn_end`, `prompt_submit`) or the hook name.
    """
    kind = EVENTS.get(event, event)
    out = ""
    if kind == "turn_end":
        visible = reply.get("visible")
        if isinstance(visible, str) and visible:
            out = json.dumps({"systemMessage": visible})
    elif kind == "prompt_submit":
        context = reply.get("context")
        if isinstance(context, str) and context:
            # Plain text that starts with "{" would be read as JSON by Claude Code.
            out = " " + context if context.startswith("{") else context
    if len(out) > MAX_OUTPUT_CHARS:
        return ""
    return out


def hook_command(launcher: Path, event_name: str) -> str:
    """The shell command a hook runs. The launcher path is quoted for `sh -c`."""
    return shlex.quote(str(launcher)) + " hook claude-code " + event_name


def settings_fragment(launcher: Path) -> dict:
    """The "hooks" object that `init` merges into ~/.claude/settings.json."""
    hooks: dict[str, list[dict]] = {}
    for event_name in EVENTS:
        handler = {
            "type": "command",
            "timeout": HOOK_TIMEOUT_S,
            "command": hook_command(launcher, event_name),
        }
        group: dict[str, object] = {}
        if event_name in MATCHER_EVENTS:
            group["matcher"] = "*"
        group["hooks"] = [handler]
        hooks[event_name] = [group]
    return {"hooks": hooks}


def skill_text(launcher: Path | None = None) -> str:
    """The SKILL.md text installed for the agent, naming the launcher to run.

    init puts nothing on PATH, so the agent's shell runs the launcher by its path.
    """
    text = (Path(__file__).resolve().parent / SKILL_FILE).read_text(encoding="utf-8")
    command = shlex.quote(str(launcher)) if launcher is not None else "firsthand"
    return text.replace("FIRSTHAND_COMMAND", command)
