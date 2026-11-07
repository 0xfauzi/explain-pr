# Other harnesses: what a learning skill can show, and where the learner can answer

Track: OpenAI Codex (ChatGPT desktop app, CLI, IDE extension, cloud, mobile), Cursor, Zed and the Agent Client Protocol, VS Code Copilot agent mode, Gemini CLI, Goose, and ChatGPT (Apps SDK and MCP Apps).

Research date: 2026-11-07. Author: research agent 5 of 5.

## How to read the evidence labels

Every claim carries one label.

| Label | Meaning |
|---|---|
| **TEST** | Verified by a test I ran in this session (commands and output summarized below). |
| **DOC** | Stated in official documentation, an official changelog, or the vendor's source repository. |
| **3P** | Reported by a third party: a GitHub issue from a user, a forum post, or a blog. |
| **SPEC** | My inference. Not verified. |

## The short answer

1. **Codex is much closer to rich UI than we thought.** The Codex engine already carries MCP Apps (`io.modelcontextprotocol/ui`) end to end. It records the `ui://` resource on every tool call and forwards the extension to MCP servers whenever the host app declares it. The CLI terminal UI does not declare it, so the CLI stays text only. The ChatGPT desktop app (which now contains Codex) has "embedded MCP app panels" in its changelog since April 2026, and the GitHub issue saying Desktop did not render MCP Apps (openai/codex#21019) was closed as completed on 2026-08-05. Status for third-party, locally configured servers on the current desktop build is still unconfirmed. (TEST for the engine plumbing; DOC for the panels; 3P for the fix.)
2. **MCP elicitation is the portable way to ask a question inside a Codex session, and it works now.** I ran Codex CLI 0.167.0 as an app server with a stub MCP server. The server sent `elicitation/create` with a schema for prediction plus confidence, and Codex relayed it to the client as `mcpServer/elicitation/request`. The answer came back to the server. Codex advertises both `form` and `url` elicitation modes to every MCP server, including in the plain CLI. (TEST)
3. **Codex has a native "ask the user" primitive that reaches the phone.** `request_user_input` (blocking, 1 to 3 short questions with options and an "Other" free text) and `request_user_input_async` (non-blocking, structured, "when enabled by the model catalog") render in the TUI, the desktop app, and ChatGPT for iOS ("Unanswered questions remain available after a turn finishes and when reopening a chat", iOS 1.2026.286). A skill cannot call these directly, but its instructions can ask the model to use them. (DOC)
4. **Codex Sites is the Codex-side equivalent of a hosted Claude artifact.** Sites are built from a prompt in ChatGPT or Codex, can be private to a workspace or public with optional "Sign in with ChatGPT", and can keep durable records in D1 (10 GB per Site). Hosting is free through 2026-12-31. This is the most direct path to a phone-reachable learning page for Codex users. (DOC)
5. **Agent Skills are now a common format.** Codex (`.agents/skills`), Cursor (`.agents/skills`, `.cursor/skills`, and it also reads `.claude/skills` and `.codex/skills`), VS Code Copilot (`.github/skills`, `.claude/skills`, `.agents/skills`), and Gemini CLI (`.gemini/skills`, `.agents/skills`) all load `SKILL.md` folders. The single best portability move is to ship the skill at `.agents/skills/learning-while-building/` (or symlink it there). (DOC)
6. **MCP Apps render in VS Code, Cursor, Goose Desktop, and ChatGPT.** VS Code: inline only, and `ui/message` "fills chat input box; does not auto-send". Cursor 2.6: inline in agent chat. Goose Desktop: experimental, apps "cannot communicate with goose (e.g. via chat)". ChatGPT: full support including fullscreen and picture in picture. Not rendered: Claude Code, Codex CLI TUI, Zed, Gemini CLI (not documented). (DOC, plus TEST for Codex CLI)
7. **A blocking UI question is being standardized.** SEP-3118 "App-Rendered Elicitations for MCP Apps" (ext-apps PR #733, from issue #511) lets a server attach `_meta.ui.resourceUri` to `elicitation/create` so the host renders a rich form and falls back to a plain form otherwise. This is exactly the learning question pattern: the agent pauses, the learner answers in a designed card, the build continues. Not yet merged. (DOC for the proposal)
8. **Hooks exist everywhere and are the seam for "seamless".** Codex, Cursor, VS Code Copilot, and Gemini CLI all have SessionStart, prompt-submit, tool, and stop hooks that can inject context. Codex's `Stop` hook with `decision: "block"` makes Codex continue with a new prompt, and Cursor's `stop` hook has `followup_message` that is auto-submitted. That is how a build can flow into an explain-back without the learner typing a command. (DOC)

## Part 1. OpenAI Codex

### 1.1 Surfaces in late 2026

| Surface | What it is | Evidence |
|---|---|---|
| ChatGPT desktop app (macOS, Windows) | "Codex is now part of the ChatGPT desktop app on macOS and Windows" (2026-07-09, release 26.707). Has an in-app browser, side panels, file viewer, PR chat. | DOC, [changelog](https://learn.chatgpt.com/docs/changelog) |
| Codex CLI (TUI) | Open source Rust TUI. Current release 0.167.0 (2026-11-06). | DOC, TEST (`codex --version` printed `codex-cli 0.167.0`) |
| IDE extension | VS Code family extension that talks to the same app server. | DOC, [InfoQ on the app server](https://www.infoq.com/news/2026/02/opanai-codex-app-server) (3P) |
| Codex cloud | Remote tasks in configured environments, results as diffs and PRs, "Review and continue from the web, mobile, or desktop app". | DOC, [cloud docs](https://learn.chatgpt.com/docs/cloud) |
| ChatGPT mobile (iOS, Android) | Remote control for Codex running on a trusted host: start tasks, approve commands, answer questions, review. Preview launched 2026-05-14. | DOC (changelog iOS entries), 3P ([9to5Mac](https://9to5mac.com/2026/05/14/openai-brings-codex-control-to-chatgpt-for-iphone-and-android/), [MacRumors](https://www.macrumors.com/2026/05/15/openai-brings-codex-chatgpt-mobile-app)) |

All surfaces sit on the **app server**, a JSON-RPC protocol: "the App Server now powers every Codex experience" (3P, InfoQ; consistent with DOC [app-server docs](https://learn.chatgpt.com/docs/app-server)).

### 1.2 AGENTS.md and skills

* **AGENTS.md** is Codex's project instruction file (DOC, [agents.md](https://agents.md)). The learning skill's always-on rules (the prediction question before a build, the explain-back after it works) can be stated there in two or three lines that point to the skill. (SPEC as a design choice)
* **Skills**: Codex reads `SKILL.md` folders from `.agents/skills` in every directory from the working directory up to the repo root, from `$HOME/.agents/skills`, from `/etc/codex/skills`, and from bundled system skills. Optional `scripts/`, `references/`, `assets/`. Progressive disclosure: only name, description, and path are loaded first, capped at about 2% of context or 8,000 characters. Explicit invocation with `$` or `/skills` in CLI and IDE, `@` in ChatGPT. (DOC, [build skills](https://learn.chatgpt.com/docs/build-skills))
* **`agents/openai.yaml`** inside the skill folder adds `interface` (display name, icon, brand color, `default_prompt` for the desktop app), `policy.allow_implicit_invocation`, and `dependencies` such as an MCP server. (DOC, same page)
* Skills inside **plugins** also work in ChatGPT Chat and Work on web, desktop, and mobile. (DOC, same page)
* `codex app-server` exposes `skills/list`. (DOC)

Implication: our skill folder works in Codex unchanged if it lives at `.agents/skills/learning-while-building/`. Adding `agents/openai.yaml` gives it an icon in the desktop app and lets us declare the learning MCP server as a dependency. (SPEC, low risk)

### 1.3 Hooks and notifications

Codex hooks (DOC, [hooks](https://learn.chatgpt.com/docs/hooks)):

* Events: `SessionStart`, `SessionEnd`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreModelRequest`, `PostModelRequest`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, `Interrupt`.
* Config in `~/.codex/hooks.json`, `<repo>/.codex/hooks.json`, or `[hooks]` in `config.toml`; plugins can bundle hooks. Project hooks need a trusted project, and non-managed hooks must be reviewed with `/hooks` before they run.
* Plain stdout from `SessionStart` and `UserPromptSubmit` becomes developer context. `additionalContext` works for SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, SubagentStart (about 2,500 tokens default).
* `Stop` with `decision: "block"` "make[s] Codex continue with a new prompt". This is the hook that can turn "the build passed" into "now the explain-back question" with no command from the learner.
* Feature `hooks` is stable and on by default (TEST: `codex features list` shows `hooks stable true`).

Notifications (DOC, [notifications](https://learn.chatgpt.com/docs/notifications)): desktop app alerts for turn completion, permission requests, and questions, with a sound setting (Codex app 26.917). An Activity view lists chats that are "running or waiting". The `notify` config runs an external program when a turn completes. The TUI emits terminal notifications; I also observed the TUI writing an OSC 7501 sequence `state=idle:app=codex` to the terminal (TEST, seen in the captured TUI output), which a terminal or wrapper could use to detect "Codex is idle, ask a question now". (OSC 7501 meaning is SPEC.)

### 1.4 The app-server protocol (the most important Codex surface for us)

Documented in [app-server docs](https://learn.chatgpt.com/docs/app-server) and the [README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md). (DOC)

* Transport: newline-delimited JSON-RPC over stdio by default; experimental WebSocket (`--listen ws://...`) and Unix socket.
* Threads and turns: `thread/start`, `thread/resume`, `thread/fork`, `turn/start`, `turn/steer`, `turn/interrupt`, `review/start`.
* Server-to-client requests that need a person: `item/commandExecution/requestApproval`, `item/fileChange/requestApproval`, `item/permissions/requestApproval`, `item/tool/requestUserInput`, `mcpServer/elicitation/request`. Also `item/tool/call` for client-side dynamic tools.
* `item/tool/requestUserInput` (experimental) carries 1 to 3 questions, each with options and an `isOther` free-text choice, and an `isBlocking` flag (TEST: generated TypeScript bindings show `ToolRequestUserInputParams = { threadId, turnId, itemId, questions, isBlocking, autoResolutionMs }`).
* `dynamicTools` on `thread/start` lets the client register its own tools; Codex calls them with `item/tool/call`.
* `mcpServer/tool/call` lets the client call an MCP tool directly, outside a model turn.
* MCP Apps fields: `mcpToolCall.mcpAppUi` has `resourceUri` and `preferredModelDisplayMode` (`inline` or `fullscreen`); `mcpAppResourceUri` is kept even without a display preference; "The UI information is preserved in tool-call events and saved history so clients can render without waiting for the full MCP catalog."
* `initialize` capabilities include `extensions`, "MCP extension settings declared by the app-server client". Codex keeps only `openai/form`, `openai/elicitation`, `openai/standard-form-input`, and `io.modelcontextprotocol/ui`, and projects them down to MCP servers ([client_capabilities.rs](https://github.com/openai/codex/blob/main/codex-rs/codex-mcp/src/client_capabilities.rs)).

#### Test I ran (TEST)

Setup: `npm i @openai/codex@latest` (0.167.0) in the scratchpad. A 60-line Python stub MCP server that logs every message, exposes one tool `learning_question` with `_meta.ui.resourceUri = "ui://learn/question.html"`, and on `tools/call` sends `elicitation/create` asking "Before the build: what will happen when the cache is cold?" with schema `{answer: string, confidence: low|medium|high}`. A driver started `codex app-server` with the stub configured via `-c mcp_servers.learn.*`, sent `initialize`, `thread/start`, and then `mcpServer/tool/call`. No model call was needed.

Results:

| Run | What the MCP server received in `initialize.capabilities` | Result |
|---|---|---|
| Client declares `extensions: {"io.modelcontextprotocol/ui": {"mimeTypes": ["text/html;profile=mcp-app"]}}` | `extensions: {"io.modelcontextprotocol/ui": {...}}`, `elicitation: {form: {}, url: {}}` | The UI extension is forwarded to the server. |
| Client declares nothing | `elicitation: {form: {}, url: {}}` only | No UI extension. |
| Client declares nothing, `--enable enable_mcp_apps` | same as above | The flag does not add the extension by itself; the host must declare it. |
| Codex CLI TUI (`codex` in a pty, dummy API key) | `elicitation: {form: {}, url: {}}` only | **The CLI TUI does not declare MCP Apps.** Text only. |

The elicitation round trip worked: the client got `mcpServer/elicitation/request` with `mode: "form"`, the message, and the schema; thread status changed to `waitingOnApproval`; the client answered `{action: "accept", content: {answer, confidence}}`; the server received it and returned the tool result, which kept its `_meta.ui.resourceUri`.

What this means:

* Any Codex host that wants to render MCP Apps has the data it needs. The TUI does not. The desktop app's behavior depends on what it declares, and its code is closed. (TEST plus SPEC)
* **A learning question as an MCP elicitation works in every Codex surface that renders elicitation forms.** The TUI has an elicitation prompt (changelog: "Make URLs clickable in MCP elicitation prompts"; DOC). The desktop app has "custom MCP approval panels" with "Don't ask again" (DOC, changelog). Whether ChatGPT for iOS renders MCP elicitation forms is not documented (SPEC: likely, since it relays approvals and questions).
* Elicitation `url` mode is also advertised. A server can send the learner to an HTTPS page (for example a hosted learning page) and wait for completion. That is a way to open the full designed learning page from inside a Codex turn and resume when the learner finishes. (TEST for the capability; the end-to-end flow is SPEC.)

#### Feature flags in 0.167.0 (TEST, `codex features list`)

`apps stable true`, `enable_mcp_apps under development false`, `hooks stable true`, `default_mode_request_user_input under development false`, `send_message_to_user_async under development false`, `apps_early_resource_discovery under development false`. Source of truth: [features/src/lib.rs](https://github.com/openai/codex/blob/main/codex-rs/features/src/lib.rs) (DOC).

### 1.5 MCP Apps in the Codex desktop app

* Changelog, Codex app 26.423 (2026-04-24): "Kept embedded MCP app panels from restarting or losing state during fullscreen changes and thread reloads." (DOC) So the desktop app has rendered MCP Apps in panels, at least for some servers.
* [openai/codex#21019](https://github.com/openai/codex/issues/21019): "Codex Desktop does not render MCP Apps inline UI resources even when tool result includes mcp_app_resource_uri". A user reports build 26.519.81530 rendered correctly, later builds broke, and 26.616.51431 (June 21) fixed it. `enable_mcp_apps` did not help some users. Closed as completed by an OpenAI maintainer on 2026-08-05 without comment. (3P for the reports, DOC for the closure)
* [openai/codex#28900](https://github.com/openai/codex/issues/28900): draw.io MCP App regression on build 26.611.61753, closed as a duplicate. (3P)
* The source shows a trust split: `connectorId`, `appName`, and `linkId` are only filled for the host-owned "Codex Apps" server, but `mcpAppResourceUri` and `mcpAppUi` are filled for every server ([mcp_tool_call.rs](https://github.com/openai/codex/blob/main/codex-rs/core/src/mcp_tool_call.rs)). (DOC) So third-party servers are not excluded at the engine level. (SPEC beyond that)
* A vendor reports its MCP App shows "a live session view" in "ChatGPT and Codex" ([Everruns changelog, 2026-09-29](https://everruns.com/docs/changelog/2026-09-29-mcp-app-chatgpt-codex/)). (3P)
* The project's own note in the brief says "Codex desktop reportedly does not render MCP Apps". That was true for some builds in May to June 2026. The later evidence suggests it may render now. **This must be re-tested on a current desktop build** with our server before we design around it. (SPEC)
* Codex also ships a "Plugin UI reference" ([developers.openai.com/plugins/reference](https://developers.openai.com/plugins/reference)) that says "Start with the open standard" (MCP Apps) and then `window.openai` "only for ChatGPT-specific capabilities". It names Codex as a host for tool annotations. A changelog entry adds "a bounded V8 runtime for UI plugin processes" (0.166 era). (DOC; the meaning of the V8 runtime for us is SPEC)

### 1.6 Codex Sites (hosted pages)

* "Build and share a website by describing it in ChatGPT or Codex." Sites can use D1 ("a relational database for durable structured data", 10 GB per Site) and R2 for files. Public sites can offer "optional Sign in with ChatGPT for identity-aware features"; signed-in visitors' email reaches the server in request headers. Sites can be "private to that workspace". Hosting free through 2026-12-31, then metered. (DOC, [Sites](https://learn.chatgpt.com/codex/sites), [data and connections](https://learn.chatgpt.com/codex/sites/data-and-connections))
* For us this is the Codex equivalent of the hosted claude.ai learning page: a phone-reachable page with identity and a database. Not documented: whether the agent can read the D1 rows back during a session. The agent can probably query its own Site's API over HTTPS (SPEC). Workspace-private sites may need a Business or Enterprise workspace (SPEC; "ChatGPT Business workspaces include Sites by default", DOC).

### 1.7 Mobile

* ChatGPT for iOS and Android acts as a remote for Codex on a trusted host (Mac first; Windows host support later, 3P). It can start tasks, approve commands, switch models, review, and **answer questions**: "Unanswered questions remain available after a turn finishes and when reopening a chat. More reliable replies to questions while another prompt is starting or finishing." (DOC, iOS 1.2026.286, 2026-10-22). Also Home Screen and Lock Screen widgets for recent tasks (DOC).
* Not documented: MCP Apps rendering inside a Codex thread on the phone, and MCP elicitation forms on the phone. (SPEC)

### 1.8 What a learner can do in Codex, per surface

| Surface | Show text | Rich UI | Native question UI | Notifications | Answer inside session | Answer outside session |
|---|---|---|---|---|---|---|
| CLI TUI | Yes | No (TEST: no UI extension declared) | `request_user_input` choices; MCP elicitation form prompt (DOC) | Terminal notification, `notify` program (DOC) | Yes: elicitation or request_user_input | `learning.py answer` in another terminal; hosted page |
| Desktop app | Yes | MCP app panels (DOC, April 2026); third-party status needs re-test | Question cards, approval panels, elicitation (DOC) | OS notifications for questions (DOC) | Yes | In-app browser can open a local or hosted page (DOC: in-app browser opens "local or public pages that don't require sign-in") |
| IDE extension | Yes | Unknown (SPEC: the extension is a webview client of the app server and could render) | Approvals and questions (SPEC) | Editor notifications (SPEC) | Yes (SPEC) | Hosted page |
| Cloud | Yes, in the task log | No (SPEC) | No live questions (SPEC) | Task done notifications on web and mobile (DOC) | No | Hosted page; files in the PR |
| ChatGPT mobile | Yes | Unknown (SPEC) | Questions and approvals (DOC) | Push (3P) | Yes, for questions (DOC) | Codex Site or hosted page in the browser |

## Part 2. Cursor

* **Skills**: Cursor loads `SKILL.md` from `.agents/skills/`, `.cursor/skills/`, `~/.agents/skills/`, `~/.cursor/skills/`, and "for compatibility" `.claude/skills/`, `.codex/skills/`, and the home equivalents. Automatic or `/` manual invocation; `disable-model-invocation: true` limits to manual. (DOC, [Cursor skills](https://cursor.com/docs/context/skills)) Our skill would load unchanged from `.claude/skills`.
* **MCP Apps**: Cursor 2.6 "MCP Apps support interactive user interfaces like charts", shown in agent chat, sandboxed iframe, can call tools. (DOC, [changelog 2.6](https://cursor.com/changelog/2-6), [forum](https://forum.cursor.com/t/cursor-2-6-mcp-apps/153482)) Whether Cursor supports `ui/message` (send a message into chat) is not stated. (SPEC)
* **Hooks** (DOC, [Cursor hooks](https://cursor.com/docs/agent/hooks)): `sessionStart` (inject `additional_context`), `postToolUse`, `beforeSubmitPrompt`, `stop` and `subagentStop` (`followup_message` "is auto-submitted as the next user message"), `afterAgentResponse`, and more. `preToolUse`, `beforeShellExecution`, `beforeMCPExecution` can show a `user_message`. Config in `.cursor/hooks.json` or `~/.cursor/hooks.json`.
* **Learner answers**: inside the session through an MCP App card (rich) or MCP elicitation (support not checked; SPEC), or plain chat. The `stop` hook's `followup_message` is the clean "after the build, ask the explain-back" seam.

## Part 3. Zed and the Agent Client Protocol (ACP)

* **Zed MCP**: "Zed currently supports MCP's Tools and Prompts features." Sampling and elicitation are listed as future work. No resources, no MCP Apps. Zed handles `notifications/tools/list_changed`. MCP servers configured in Zed "are forwarded to External Agents via the Agent Client Protocol". (DOC, [Zed MCP docs](https://zed.dev/docs/ai/mcp))
* **ACP** (DOC, [protocol overview](https://agentclientprotocol.com/protocol/overview)): JSON-RPC between editor (client) and agent. Client methods include `session/request_permission`, `fs/*`, `terminal/*`, and optional `elicitation/create` with `elicitation/complete` for URL flows. `session/update` streams message chunks, tool calls, plans, available commands, mode changes, user-facing notices. Extension through `_meta` and underscore-prefixed methods. The Rust schema crate tags elicitation types UNSTABLE ([docs.rs](https://docs.rs/agent-client-protocol-schema/)). No MCP Apps or HTML UI in ACP. (DOC)
* Claude Code, Codex, and Gemini CLI run inside Zed as ACP agents (DOC for the concept; the exact adapters were not checked in this session).
* **Learner answers**: text in the agent panel. ACP elicitation, once stable and supported by Zed, would give a native form. The ACP "available commands" update can expose a `/learn` command. A tool call can return a link; Zed renders markdown links (SPEC). Rich UI is out of reach in Zed today; the honest design is a link to the hosted or local page.

## Part 4. VS Code Copilot agent mode

* **MCP features** (DOC, [VS Code MCP guide](https://code.visualstudio.com/api/extension-guides/mcp)): elicitation, sampling, resources, prompts (as slash commands), and **MCP Apps**. MCP Apps table: display modes "`inline` only (not `fullscreen` or `pip`)"; send message "Fills chat input box; does not auto-send"; context updates "Appear as attachments"; clipboard write supported; camera, microphone, geolocation not supported.
* **Skills**: `.github/skills/`, `~/.copilot/skills/`, and in local sessions `.claude/skills/` and `.agents/skills/`. `/` invocation or automatic; `user-invocable` and `disable-model-invocation` frontmatter. (DOC, [agent skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills))
* **Hooks** (Preview): `sessionStart`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `preCompact`, `subagentStart`, `subagentStop`, `agentStop`, `sessionEnd`. Reads `.github/hooks/*.json` and also the repo's `.claude/settings.json`. (DOC, [hooks](https://code.visualstudio.com/docs/copilot/customization/hooks))
* **Webviews**: a VS Code extension can open a full webview panel (DOC, standard VS Code API). A small companion extension could host the learning page inside the editor and talk to the record files directly. (SPEC as a plan)
* **Known gap**: the rich-UI elicitation work is driven partly by VS Code's Connor Peet: the current workaround "doesn't let hosts recognize that input is needed, so VS Code doesn't show its input prompt, and app UI lingers after use" ([ext-apps#511](https://github.com/modelcontextprotocol/ext-apps/issues/511)). (DOC)
* **Learner answers**: an inline MCP App card is the best in-session experience. Because `ui/message` only fills the input box, the card should submit the answer by calling a server tool (`tools/call`), not by sending a chat message. Elicitation forms are a good fallback.

## Part 5. Gemini CLI

* **Skills**: `~/.gemini/skills/`, `~/.agents/skills/`, `.gemini/skills/`, `.agents/skills/`. Activation through an `activate_skill` tool with a consent prompt showing "the skill's name, purpose, and the directory path". (DOC, [Gemini CLI skills](https://geminicli.com/docs/cli/skills/))
* **Hooks**: `BeforeTool`, `AfterTool`, `BeforeAgent`, `AfterAgent`, `BeforeModel`, `BeforeToolSelection`, `AfterModel`, `SessionStart`, `SessionEnd`, `Notification`, `PreCompress` in `settings.json`. `additionalContext` injects context; `systemMessage` "appears in the terminal"; `AfterAgent` with `decision: "deny"` "rejects the response and triggers a retry". (DOC, [hooks reference](https://geminicli.com/docs/hooks/reference/))
* **MCP**: tools, resources, prompts (as slash commands), and rich content in tool results. Elicitation, sampling, and MCP Apps are not mentioned. (DOC, [MCP server docs](https://geminicli.com/docs/tools/mcp-server/))
* **Learner answers**: plain chat, or out of session. `systemMessage` from a hook is a quiet way to show "1 question due" at session start without spending model context.

## Part 6. Goose

* **MCP Apps**: supported in goose Desktop, experimental. Apps render inline when a tool returns UI, or in standalone sandboxed windows from an Apps page. "Apps can call tools and read resources through MCP (if enabled through CORS)." Apps "cannot communicate with goose (e.g. via chat)". Desktop 1.19.1+ for the tutorial. A WIP PR would advertise `io.modelcontextprotocol/ui` in capability negotiation ([goose#6927](https://github.com/block/goose/pull/6927)). (DOC, [goose MCP Apps guide](https://goose-docs.ai/docs/guides/interactive-chat/mcp-ui/), [building MCP Apps](https://goose-docs.ai/docs/tutorials/building-mcp-apps))
* The **standalone app window** is interesting for us: a learning page that lives next to the chat, not inside one message. (DOC for the feature, SPEC for fit)
* **Learner answers**: in the app card through a server tool call. The answer does not reach the model through chat, so the server must store it and the agent reads it on the next turn.

## Part 7. ChatGPT (Apps SDK and MCP Apps)

* ChatGPT "implements the open MCP Apps standard". Tools link to `_meta.ui.resourceUri` (alias `openai/outputTemplate`). UI can call `tools/call` and send `ui/message` follow-ups. Display modes: inline card, inline carousel, fullscreen, picture in picture ("On mobile, picture-in-picture may be presented as fullscreen"). Extras: `widgetState`/`setWidgetState`, file upload and download, `requestModal`, checkout. (DOC, [MCP Apps in ChatGPT](https://developers.openai.com/apps-sdk/mcp-apps-in-chatgpt), [Plugin UI reference](https://developers.openai.com/plugins/reference))
* Connecting a custom server: Plugins, "Add custom MCP server", public HTTPS endpoint or "Secure MCP Tunnel"; a dev tunnel works for testing. (DOC, [connect to ChatGPT](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt))
* Skills inside plugins work in ChatGPT on web, desktop, and mobile. (DOC, Codex skills page)
* **Learner answers**: ChatGPT is the strongest rich-UI host outside Claude. A "learning plugin" (skill plus MCP server with a UI) would give review sessions on the phone with a designed card. The record must live on the server, since ChatGPT has no access to the repo. (SPEC as design)

## Part 8. The cross-harness picture

### 8.1 Capability matrix

| Harness | Skills | MCP Apps (rich UI) | MCP elicitation (form) | Native ask-user | Hooks that can continue the turn | Phone |
|---|---|---|---|---|---|---|
| Claude Code (reference, from brief) | Yes | No | (not in this track) | AskUserQuestion (not in this track) | Stop hook (not in this track) | Claude app |
| Codex CLI | Yes (DOC) | No (TEST) | Yes, advertised and relayed (TEST) | `request_user_input` (DOC) | `Stop` block continues (DOC) | Via ChatGPT mobile remote (DOC) |
| Codex in ChatGPT desktop | Yes (DOC) | Panels exist (DOC); third-party needs re-test | Yes (DOC panels; SPEC for forms) | Question cards (DOC) | Same engine (DOC) | Same |
| Codex cloud | Configured per env (DOC) | No (SPEC) | No live user (SPEC) | No (SPEC) | Hooks run (SPEC) | Review only (DOC) |
| Cursor | Yes, reads `.claude/skills` (DOC) | Yes, 2.6 (DOC) | Not checked | Not checked | `stop` `followup_message` (DOC) | No (SPEC) |
| VS Code Copilot | Yes, reads `.claude/skills` (DOC) | Yes, inline only (DOC) | Yes (DOC) | Not checked | `agentStop` (DOC) | No |
| Zed | Through ACP agents (SPEC) | No (DOC) | No (DOC) | Permission prompts only (DOC) | Depends on agent | No |
| Gemini CLI | Yes (DOC) | Not documented | Not documented | Not checked | `AfterAgent` deny retries (DOC) | No |
| Goose Desktop | Not checked | Yes, experimental (DOC) | Not checked | Not checked | Not checked | No |
| ChatGPT | In plugins (DOC) | Yes, full (DOC) | Yes (SPEC) | n/a | n/a | Yes (DOC) |

### 8.2 Mechanisms that make "seamless" possible across harnesses

1. **One MCP server, four rendering tiers.** Ship a small `learning` MCP server whose `ask` tool:
   * declares `_meta.ui.resourceUri` so MCP Apps hosts (ChatGPT, VS Code, Cursor, Goose, Claude chat, maybe Codex desktop) render the designed card;
   * uses `elicitation/create` with a schema (answer, confidence 1 to 5, rubric hidden) so form hosts (Codex CLI and desktop, VS Code) show a native form and the turn pauses until the learner answers;
   * offers elicitation `url` mode to open the full hosted page when a form is too small (explainers, debugging drills);
   * returns plain text in `content` so text-only hosts (Zed, Gemini CLI) still work.
   The tool result's `structuredContent` gives the model the answer and the grade; `_meta` carries page-only data. (Mechanisms DOC and TEST; the design is SPEC)
2. **App-rendered elicitations (SEP-3118)** collapse tiers 1 and 2: one request that renders as the designed card where possible and as a form elsewhere, and that blocks the agent until the learner answers. Worth building against the draft now and watching the PRs ([ext-apps#733](https://github.com/modelcontextprotocol/ext-apps/pull/733), [SEP-3118](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/3118)). (DOC for the proposal)
3. **Hooks as the transition engine.** SessionStart: inject "2 reviews due; ask one before starting" (Codex, Cursor, VS Code, Gemini all support context injection). Stop: when the build turn ends with passing tests, block once and continue with the explain-back prompt (Codex `Stop` block, Cursor `followup_message`, Gemini `AfterAgent`). The learner never types a command to switch modes. (DOC)
4. **The Codex app server as a host we control.** For a fully designed Codex experience we could write our own thin client (desktop window, web page, or VS Code panel) that drives `codex app-server`, declares `io.modelcontextprotocol/ui`, and renders our cards and the learning record next to the thread. I verified that the server forwards the extension and relays elicitation to such a client. This is ambitious but entirely documented and open source. (TEST for the protocol; the client is SPEC)
5. **Hosted page per ecosystem for the phone.** Claude: the artifact with `db` (from the brief). Codex: a Codex Site with D1 and Sign in with ChatGPT. ChatGPT: the MCP App itself in a plugin. Everywhere else: the repo's plain record files plus `learning.py serve` behind a tunnel. The source of truth stays the repo files; the hosted stores are caches that sync. (SPEC as design)
6. **One skill folder.** Put the skill at `.agents/skills/learning-while-building/` and keep `.claude/skills/` as a symlink (or the reverse). Codex, Cursor, VS Code, and Gemini read `.agents/skills`; Cursor and VS Code also read `.claude/skills`. Add `agents/openai.yaml` for Codex UI metadata. (DOC)

## Part 9. Open questions and the cheapest experiment for each

| Question | Cheapest experiment |
|---|---|
| Does current Codex in ChatGPT desktop render a third-party local MCP App? | Add the existing learning-question MCP server to `~/.codex/config.toml`, ask Codex to call the tool in the desktop app, look for a panel. Five minutes on a Mac. |
| Does ChatGPT for iOS render MCP elicitation forms in a Codex thread? | Same server; trigger the elicitation from the desktop; open the thread on the phone. |
| Does `request_user_input` appear for a skill-driven question on the phone? | In Plan mode (where it is enabled), ask Codex to ask a prediction question with three options; answer it on iOS. |
| Can an agent read Codex Site D1 data back? | Create a tiny Site with a `/api/answers` route; ask Codex to fetch it during a session. |
| Does Cursor relay MCP elicitation? | Point Cursor at the stub server from this report; call the tool. |
| Will SEP-3118 land and which hosts adopt it? | Watch the PRs; test the reference inspector branch with our card. |

## Appendix: test details

* Codex package: `@openai/codex@0.167.0` from npm, installed in the session scratchpad.
* Feature list command: `codex features list`.
* App-server run: `codex app-server -c mcp_servers.learn.command="python3" -c 'mcp_servers.learn.args=["-I","stub.py","stub.log"]'` with `CODEX_HOME` set to an empty folder; JSON-RPC driver sent `initialize` (with and without `capabilities.extensions`), `initialized`, `thread/start {ephemeral: true}`, `mcpServer/tool/call`.
* Captured MCP `initialize` from Codex (with host extension): `{"protocolVersion": "2025-06-18", "capabilities": {"experimental": {"codex/auth-change": {}}, "extensions": {"io.modelcontextprotocol/ui": {"mimeTypes": ["text/html;profile=mcp-app"]}}, "elicitation": {"form": {}, "url": {}}}, "clientInfo": {"name": "codex-mcp-client", "title": "Codex", "version": "0.167.0"}}`.
* TUI run: `codex` in a pseudo-terminal (`script -qc`) after `codex login --with-api-key` with a dummy key; the MCP server received the same `initialize` without `extensions`.
* Scripts are in the session scratchpad (stub.py, drive.py); they are not part of the repo.
