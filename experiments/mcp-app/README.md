# MCP App test

A test of one question: which apps show an MCP App inside the conversation?

The server has one tool, `learning_question`. It returns a practice question as
text. Apps that support MCP Apps also show the question as a card. On the card
you select an answer and how sure you are, then lock it. The card then sends your
answer into the chat. The last line of the card shows the name of the app that
rendered it.

The server uses only the Python standard library.

## Run the test

Do the same steps in each app:

1. Connect the server (see below).
2. In a new conversation, type: `Call the learning_question tool.`
3. Write down what you see:
   - a card, or only text;
   - if there is a card, the "Rendered by" line;
   - after you lock an answer, whether your answer appears in the chat.

### Claude Code (the Claude app, the web, or the CLI)

Add a file named `.mcp.json` at the repository root with this content. Then
start a new session and approve the `learning-question` server when you are
asked. For a cloud session, commit the file to the branch that the session
uses.

```json
{
  "mcpServers": {
    "learning-question": {
      "command": "python3",
      "args": ["experiments/mcp-app/server.py"]
    }
  }
}
```

On your own computer, you can also run this from the repository root:
`claude mcp add learning-question -- python3 experiments/mcp-app/server.py`.

### Claude desktop app (chat)

Open Settings, then Developer, then Edit Config. Add this to
`claude_desktop_config.json`, with the full path to your copy of this
repository. Then restart the app.

```json
{
  "mcpServers": {
    "learning-question": {
      "command": "python3",
      "args": ["/full/path/to/explain-pr/experiments/mcp-app/server.py"]
    }
  }
}
```

### Codex (the app or the CLI)

Add this to `~/.codex/config.toml`, with the full path. Then start a new session.

```toml
[mcp_servers.learning-question]
command = "python3"
args = ["/full/path/to/explain-pr/experiments/mcp-app/server.py"]
```

## Results

| App | Card shown | Answer sent to the chat |
|---|---|---|
| Claude Code in the Claude app | No, text only (2026-11-07). The agent received the tool's structuredContent as JSON. | Not applicable |
| Claude desktop app, chat | | |
| Codex app | | |
| Codex CLI | | |
