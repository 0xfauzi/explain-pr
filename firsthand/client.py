"""The control socket client shared by the CLI and the tests."""

from __future__ import annotations

import json
import os
import socket
import time
from collections.abc import Mapping

from firsthand import daemon, paths
from firsthand.model import FirsthandError

MAX_RESPONSE_BYTES = 65_536
START_WAIT_S = 3.0
RETRY_S = 0.05


class DaemonUnavailable(FirsthandError):
    code = "unavailable"


class RemoteError(FirsthandError):
    """Carries the daemon's error code and message."""


def _connect(timeout_s: float) -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout_s)
    try:
        sock.connect(str(paths.control_socket()))
    except OSError:
        sock.close()
        raise
    return sock


def _connect_or_start(start: bool, timeout_s: float) -> socket.socket:
    try:
        return _connect(timeout_s)
    except OSError:
        if not start or os.environ.get("FIRSTHAND_NO_DAEMON"):
            raise DaemonUnavailable(
                "Firsthand is not running. It starts at the next prompt in your agent, "
                "or run: firsthand status"
            ) from None
    daemon.spawn()
    deadline = time.monotonic() + START_WAIT_S
    while True:
        try:
            return _connect(timeout_s)
        except OSError:
            if time.monotonic() >= deadline:
                raise DaemonUnavailable(
                    "Firsthand could not start. Its log is ~/.firsthand/run/daemon.log. "
                    "Then run: firsthand status"
                ) from None
            time.sleep(RETRY_S)


def _read_response(sock: socket.socket) -> dict:
    data = b""
    while b"\n" not in data:
        chunk = sock.recv(65_536)
        if not chunk:
            break
        data += chunk
        if len(data) > MAX_RESPONSE_BYTES + 1:
            break
    try:
        response = json.loads(data.split(b"\n", 1)[0].decode())
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise DaemonUnavailable(
            "Firsthand sent a reply that could not be read. Run: firsthand status"
        ) from None
    if not isinstance(response, dict):
        raise DaemonUnavailable(
            "Firsthand sent a reply that could not be read. Run: firsthand status"
        )
    return response


def call(
    op: str,
    args: Mapping[str, object] | None = None,
    *,
    cwd: str | None = None,
    agent: bool = False,
    start: bool = True,
    timeout_s: float = 5.0,
) -> dict:
    """Send one request to the daemon and return its result.

    Raises DaemonUnavailable when no daemon answers, RemoteError for an error reply.
    """
    request = {
        "v": 1,
        "op": op,
        "args": dict(args or {}),
        "cwd": cwd if cwd is not None else os.getcwd(),
        "agent": agent,
    }
    sock = _connect_or_start(start, timeout_s)
    try:
        sock.sendall((json.dumps(request) + "\n").encode())
        response = _read_response(sock)
    except OSError:
        raise DaemonUnavailable(
            "Firsthand stopped answering. Run: firsthand status"
        ) from None
    finally:
        sock.close()
    if response.get("ok") is True:
        result = response.get("result")
        return result if isinstance(result, dict) else {}
    error = response.get("error")
    error = error if isinstance(error, dict) else {}
    message = error.get("message")
    code = error.get("code")
    raise RemoteError(
        message if isinstance(message, str) else "Firsthand refused the request.",
        code if isinstance(code, str) else "internal",
    )
