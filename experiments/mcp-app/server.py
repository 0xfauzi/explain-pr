"""A minimal MCP server with one MCP App, to test which hosts render it.

Stdio transport, newline-delimited JSON-RPC, standard library only. The tool
`learning_question` returns a question as text, and links a small interface
(ui://learning-while-building/question) that hosts supporting MCP Apps
(extension io.modelcontextprotocol/ui, spec 2026-01-26) render as a card.
Locking an answer on the card sends it into the conversation with ui/message.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

UI_URI = "ui://learning-while-building/question"
UI_MIME = "text/html;profile=mcp-app"
PAGE = Path(__file__).with_name("question.html")

QUESTION = {
    "context": "Before you add confirmation emails to the checkout.",
    "question": (
        "The API saves the order. Then it puts a message on the queue. "
        "The API stops after the save and before the message. "
        "What does the customer see?"
    ),
    "options": [
        "No order and no email",
        "An order, but no confirmation email",
        "An order and two emails",
    ],
}

TOOL = {
    "name": "learning_question",
    "title": "Learning question",
    "description": (
        "Show the learner one practice question. Returns the question as text; "
        "hosts that support MCP Apps also show it as an interactive card."
    ),
    "inputSchema": {"type": "object", "properties": {}},
    "_meta": {"ui": {"resourceUri": UI_URI}},
}


def as_text(q: dict) -> str:
    letters = "ABC"
    lines = [q["context"], "", q["question"], ""]
    lines += [f"{letters[i]}. {opt}" for i, opt in enumerate(q["options"])]
    lines += ["", "Answer with a letter and how sure you are."]
    return "\n".join(lines)


def handle(method: str, params: dict) -> dict:
    if method == "initialize":
        return {
            "protocolVersion": params.get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": {"name": "learning-while-building-test", "version": "0.1.0"},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [TOOL]}
    if method == "tools/call":
        return {
            "content": [{"type": "text", "text": as_text(QUESTION)}],
            "structuredContent": QUESTION,
        }
    if method == "resources/list":
        return {"resources": [{"uri": UI_URI, "name": "question", "mimeType": UI_MIME}]}
    if method == "resources/read":
        return {
            "contents": [
                {
                    "uri": UI_URI,
                    "mimeType": UI_MIME,
                    "text": PAGE.read_text(encoding="utf-8"),
                    "_meta": {"ui": {"prefersBorder": True}},
                }
            ]
        }
    raise LookupError(method)


def respond(message: dict) -> dict | None:
    if "id" not in message:
        return None  # a notification, such as notifications/initialized
    try:
        result = handle(message.get("method", ""), message.get("params") or {})
    except LookupError:
        error = {
            "code": -32601,
            "message": f"Method not found: {message.get('method')}",
        }
        return {"jsonrpc": "2.0", "id": message["id"], "error": error}
    return {"jsonrpc": "2.0", "id": message["id"], "result": result}


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        reply = respond(json.loads(line))
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
