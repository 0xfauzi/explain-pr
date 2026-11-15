"""The hook dispatcher: one spool line per hook call, then at most a short wait.

It always returns 0, never writes to stderr, and prints only what the adapter's
`render` returns for a reply the daemon left ready. Any error is one line in
run/hook.log. Imports are kept small: a hook runs before every tool call.
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import logging
import os
import time
from collections.abc import Mapping
from typing import BinaryIO, TextIO

from firsthand import daemon, events, paths
from firsthand.adapters import claude_code

MAX_STDIN_BYTES = 5 * 1024 * 1024
WAIT_S = 0.3
POLL_S = 0.01
LOCK_WAIT_S = 0.2
ADAPTERS = {claude_code.NAME: claude_code}
_WAITS_FOR_REPLY = ("prompt_submit", "turn_end")


def _lock(fd: int, wait_s: float) -> bool:
    """Take the spool lock, waiting at most wait_s. False if it stayed held."""
    deadline = time.monotonic() + wait_s
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            if time.monotonic() >= deadline:
                return False
            time.sleep(POLL_S)


def append_line(data: bytes) -> None:
    """Append one encoded spool line under an exclusive lock, in one write.

    A hook never waits long: if the lock stays held past LOCK_WAIT_S (a stalled
    daemon), the line is written without it. One O_APPEND write of a short line
    is atomic, so it is not interleaved with another hook's line.
    """
    fd = os.open(paths.spool_file(), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        locked = _lock(fd, LOCK_WAIT_S)
        try:
            os.write(fd, data)
        finally:
            if locked:
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _claim(event_id: str, session: str, deadline: float) -> dict | None:
    """Wait for this event's reply file and take it by rename. None when none came."""
    ready = paths.reply_file(event_id)
    claimed = ready.with_suffix(".claimed")
    while True:
        try:
            os.rename(ready, claimed)
        except FileNotFoundError:
            if time.monotonic() >= deadline:
                return None
            time.sleep(POLL_S)
            continue
        try:
            reply = json.loads(claimed.read_text(encoding="utf-8"))
        finally:
            with contextlib.suppress(OSError):
                claimed.unlink()
        if not isinstance(reply, dict) or reply.get("id") != event_id:
            return None
        if reply.get("session") != session:
            return None
        return reply


_LOGGER = logging.getLogger("firsthand.hooks")
_LOGGER.propagate = False


class _OneLine(logging.Formatter):
    """One line per failure: the exception's name and message, no traceback."""

    def formatException(self, ei) -> str:
        return f"{ei[0].__name__}: {ei[1]}" if ei and ei[0] else ""

    def format(self, record: logging.LogRecord) -> str:
        return super().format(record).replace("\n", " ")[:2000]


def _open_log() -> logging.Handler | None:
    try:
        paths.ensure_private_dirs()
        path = paths.hook_log_file()
        os.close(os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600))
        handler = logging.FileHandler(path, encoding="utf-8")
    except OSError:  # nowhere to report it: a hook prints nothing
        return None
    handler.setFormatter(_OneLine("%(asctime)s %(message)s"))
    _LOGGER.addHandler(handler)
    return handler


def _dispatch(
    agent: str,
    event_name: str,
    stdin: BinaryIO,
    stdout: TextIO,
    environ: Mapping[str, str],
) -> None:
    adapter = ADAPTERS.get(agent)
    if adapter is None:
        return
    raw = stdin.read(MAX_STDIN_BYTES + 1)
    if len(raw) > MAX_STDIN_BYTES:
        raise ValueError("hook input is over 5 MB")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise TypeError("hook input is not a JSON object")
    event_id = events.new_event_id()
    line = adapter.to_spool(
        event_name, payload, at=events.now_stamp(), event_id=event_id, environ=environ
    )
    if line is None:
        return
    data = events.encode(line)
    paths.ensure_private_dirs()
    append_line(data)
    started_at = time.monotonic()
    running = daemon.is_running()
    if not running and not environ.get("FIRSTHAND_NO_DAEMON"):
        daemon.spawn()
    if not running or line["event"] not in _WAITS_FOR_REPLY:
        return
    reply = _claim(event_id, str(line["session"]), started_at + WAIT_S)
    if reply is None:
        return
    out = adapter.render(str(line["event"]), reply)
    if out:
        stdout.write(out)
        stdout.flush()


def main(
    agent: str,
    event_name: str,
    stdin: BinaryIO,
    stdout: TextIO,
    environ: Mapping[str, str] | None = None,
) -> int:
    """Run one hook call. Always returns 0."""
    try:
        _dispatch(
            agent, event_name, stdin, stdout, os.environ if environ is None else environ
        )
    except BaseException:  # a hook must never fail the agent's turn
        handler = _open_log()
        if handler is not None:
            _LOGGER.exception("%s", event_name)
            _LOGGER.removeHandler(handler)
            handler.close()
    return 0
