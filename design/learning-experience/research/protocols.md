# Research track: protocols and technologies for cross-surface continuity

What open protocols and platform technologies can carry a learning moment (a prediction question, an explain-back, a debugging drill, a spaced review) from the place where the learner is building to the place where they are, and carry the answer back into the record, across Claude Code, the Claude app, Codex and other harnesses. As of 2026-11-07.

Researcher: protocols track, one of five. Session: Claude Code 2.1.319, cloud container. A sibling report covers Claude-specific surfaces in depth (`design/learning-experience/research/claude.md`); this one covers the protocol layer underneath and the harness-neutral pieces.

## Evidence marks

| Mark | Meaning |
| :- | :- |
| **[T]** | Verified by a test I ran in this session. The command and result are in the appendix. |
| **[T-prior]** | Verified earlier by this project (stated in the brief or in `experiments/`). |
| **[D]** | Documented officially (spec, vendor docs, source repository). |
| **[R]** | Reported by third parties (issue threads, blogs). |
| **[S]** | Speculative: my inference; needs a test. |

## The ten findings that matter most

1. **MCP elicitation is the one in-flow answer surface that every serious harness now shares.** Claude Code declares `elicitation: {form: {}, url: {}}` to a local stdio server, and the `Elicitation` hook receives the full request and can answer it [T]. Cloud sessions show elicitation as a card on claude.ai/code and in the desktop Code tab [D]. Codex exposes it to its rich clients as the server request `mcpServer/elicitation/request` (form or URL) [D], and ACP stabilized `elicitation/create` with form and URL modes on 2026-07-24 [D]. One learning MCP server can therefore ask a question with an answer field and a confidence enum inside the build, in all of them, without any custom UI.
2. **URL mode elicitation is the mechanism for a rich answer page that the agent cannot see.** The spec requires the client to open the URL "in a secure manner that does not enable the client or LLM to inspect the content or user inputs" and to show the full URL before consent [D]. That is exactly the shape for a polished answer page (diagram, code, sketch input) hosted on a page we design, with the answer returned to the server only, and `notifications/elicitation/complete` resuming the turn. Claude Code supports it in the terminal and on cloud cards ("Open link", then "I'm done, continue") [D].
3. **MCP Apps are a progressive enhancement, not the spine.** They render in Claude chat, ChatGPT (which recommends the standard `ui/*` bridge over `window.openai`), VS Code Copilot, Goose and others [D][R], but not in Claude Code [T-prior]. The Codex desktop issue (openai/codex#21019) was closed as completed on 2026-08-05, with a user reporting a fix in build 26.616.51431 [R]; OpenAI's own guide still says to keep tools useful "without a component so ChatGPT and Codex can complete the workflow" [D]. Design: every learning tool returns complete text plus an elicitation path, and links a `ui://` view for hosts that render it.
4. **MCP itself changed shape in 2026-07-28, and it matters for us.** The core became stateless: no `initialize`, no `Mcp-Session-Id`; server-to-client requests such as elicitation now travel as Multi Round-Trip Requests (`resultType: "input_required"`, answered via `inputResponses`) [D]. Tasks and MCP Apps became official extensions (`io.modelcontextprotocol/tasks`, `io.modelcontextprotocol/ui`). Sampling, Roots and Logging are deprecated. Notifications moved to one `subscriptions/listen` stream [D]. Claude Code 2.1.319 tries `server/discover` first and falls back to the 2025-11-25 handshake [T]. Our server should speak both.
5. **A learning question can be a long-running MCP task.** With the tasks extension a tool call returns a task handle; the client polls `tasks/get`; the task can open an elicitation while running [D]. In Claude Code the footer shows "1 MCP task" and the transcript announces completion (CLI, Agent SDK and GitHub Actions only, public beta) [D]. This models "question asked now, answered later on the phone, result folded back into this session" natively.
6. **Push to the phone without an app store is real on both platforms.** iOS 16.4+ allows Web Push for Home Screen web apps (manifest `display: standalone`, permission on a user tap) [D]; iOS 18.4 added Declarative Web Push, which shows a notification from a JSON payload with no service worker and can set the app badge [D]. Web Push payloads are encrypted end to end (RFC 8291), so the push service cannot read the question. The GitHub Pages origin (`0xfauzi.github.io/explain-pr/`) can host the installable app, and a GitHub Actions cron or a Claude cloud scheduled task can send the pushes with a VAPID key held as a secret [S for the full chain].
7. **ntfy is the zero-setup push fallback, and it works from this cloud container.** One `curl` to `ntfy.sh/<topic>` with `Title` and `Click` headers was accepted [T]. It has actions (`view`, `http`), scheduled delivery up to 3 days, and iOS and Android apps [D]. But the topic name is the only secret on the public server [D] and payloads are not end-to-end encrypted, so it may carry only "1 review due" plus a link, never question text or rubric.
8. **Git is already a correct sync layer for the record, with one tweak.** The record is one file per attempt (`record.py`), which merges without conflicts. For any append-only log, `.gitattributes` `*.jsonl merge=union` merged a laptop branch and a phone branch cleanly [T]. A CRDT (Automerge, Yjs) adds nothing for a single learner whose writes are per-attempt; it becomes worth it only for live co-editing of an explainer page.
9. **The rubric leaks through the transcript today, and protocols can fix it.** `learning.py ask --rubric "..."` runs as a visible Bash command in Claude Code and Codex, so the learner sees the rubric before answering [S, from how both harnesses display commands]. Fixes, in order of strength: the rubric is written by a learning MCP server tool or a forked subagent whose arguments are collapsed; the attempt file stores only `sha256(rubric + salt)` until the answer locks (commit-reveal gives tamper evidence that the rubric was fixed first); the rubric never ships to a browser before lock (grading runs where the rubric is). Anything sent to a page before lock is readable in devtools.
10. **GitHub is a strong asynchronous surface but a weak in-flow one.** Check runs carry up to three buttons (`requested_action`, label 20 chars) and 65,535 chars of Markdown, but only a GitHub App can create them [D]. PR and issue comments reach GitHub Mobile push with no setup, and an Actions workflow can turn a reply into a graded attempt. Good for "explain this PR back" on merge and for reviews, poor for a prediction before a build.

## 1. What "seamless" requires at the protocol level

A learning moment crosses three boundaries. The protocols must handle each.

| Boundary | What must move | Hard constraint |
| :- | :- | :- |
| Build to question | The agent pauses at a chosen point and puts one question in front of the learner, in the surface they are already looking at | No context switch for the learner in the common case; the build resumes by itself once answered |
| Here to elsewhere | A question waits; the learner answers later on another device | Laptop may be closed; the phone has no tunnel to localhost |
| Answer to record | The answer, confidence and lock time reach `.learning/` and are graded against a rubric fixed earlier | Rubric not visible before lock; record stays plain files in the repo; works in every harness |

The recommended architecture, argued below: **a learning MCP server is the spine** (one server, stdio locally and Streamable HTTP when hosted), **elicitation is the default in-flow surface**, **MCP Apps and Claude artifacts are rich enhancements**, **Web Push to an installable page on the GitHub Pages origin carries reviews to the phone**, and **git carries the record**.

## 2. MCP in depth

### 2.1 Versions in play

| Revision | Status | What matters for this product | Mark |
| :- | :- | :- | :- |
| 2025-11-25 | Previous stable | URL mode elicitation (SEP-1036), titled and multi-select enums (SEP-1330), defaults in elicitation schemas (SEP-1034), sampling with tools (SEP-1577), experimental tasks (SEP-1686), icons, Client ID Metadata Documents, OIDC discovery, SSE polling. [changelog](https://modelcontextprotocol.io/specification/2025-11-25/changelog) | [D] |
| 2026-07-28 | Current, released | Stateless core; `initialize` and `Mcp-Session-Id` retired; optional `server/discover`; MRTR for elicitation; Tasks and MCP Apps as extensions; `subscriptions/listen`; Sampling, Roots, Logging deprecated (12-month support); `iss` validation (RFC 9207); DCR deprecated in favor of CIMD. [release post](https://blog.modelcontextprotocol.io/posts/2026-07-28/) | [D] |

Claude Code 2.1.319 sent `server/discover` first, then `initialize` with protocol `2025-11-25` when our probe did not answer the new call [T]. On its v2 runtime it holds a stream open for `list_changed` from 2026-07-28 servers [D] ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp.md)).

### 2.2 Elicitation (form and URL)

Form mode: flat object of primitives only (string with `email|uri|date|date-time` formats, number, integer, boolean, single and multi-select enums with titles, defaults). The client must let the user review and modify before sending, and must show which server is asking. Three outcomes: `accept`, `decline`, `cancel` [D] ([spec](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)).

This fits the skill's question shape exactly: `answer` (string, or enum for a prediction with options), `confidence` (titled enum: "Guess", "Unsure", "Fairly sure", "Certain"), and optionally `hint_requested` (boolean). `decline` maps to "skip"; `cancel` to "ask later". A prediction question's options can be an enum with titles; an explain-back is a long string.

URL mode: `mode: "url"`, `url`, `elicitationId`. The client must not prefetch, must show the full URL and highlight the domain, must get consent, and must open it so the client and model cannot inspect the inputs (on iOS, `SFSafariViewController`, not `WKWebView`). The server may send `notifications/elicitation/complete`; the client should still offer manual continue. The server must bind the elicitation to the user and must verify that whoever opens the URL is that user (anti-phishing). The URL must not carry personal data or be pre-authenticated [D].

What URL mode enables here:

- A designed answer page in the approved visual language (paper, grain, record segments), richer than a form: a diagram to annotate, a code excerpt with a line to click, a "predict the output" box, a sketch canvas. The page posts the answer to the learning server; the server records it; the build resumes.
- The answer page is the same one the phone opens later from a push, so "answer now" and "answer later" share one UI.
- Constraint: the URL must be reachable by the browser that opens it. For a local stdio server that is `http://127.0.0.1:port` on the same machine (fine on desktop, not on the phone); for cloud sessions or the phone it must be a hosted origin (claude.ai artifact, a tunnel, or a small hosted service). Claude Code caps the URL at roughly 8,000 characters [D], so pass an id, never the question.
- Identity: for a local server, a one-time token in the URL is acceptable only because the URL never leaves the machine; for a hosted one the spec's rule applies (session cookie or equivalent tied to the same subject) [D].

Claude Code specifics: dialogs in the interactive terminal; cards on claude.ai/code and the desktop Code tab for cloud sessions; an `Elicitation` hook can observe or auto-answer; in `-p` mode a task that asks for input is cancelled [D]. I confirmed the hook receives `mcp_server_name`, `message`, `mode` and `requested_schema`, and that its `accept` content reaches the server [T]. Codex: `mcpServer/elicitation/request` in the app-server protocol [D] ([app-server](https://learn.chatgpt.com/docs/app-server)); third-party posts say Codex CLI handles form mode since about v0.129 and opens a browser for URL mode, but they conflict [R].

Security note: the elicitation `message` and form content pass through the client and are visible to the model when the tool result returns [T: the accept content appeared verbatim in the tool result]. That is fine for the learner's answer, which the agent must grade. It is not fine for the rubric, which must never be in the `message`.

### 2.3 Tasks (long-running)

A tool call can return a task (`resultType: "task"`, `taskId`, `status`, `pollIntervalMs`, `ttlMs`); the client polls `tasks/get`; 2026-07-28 adds `tasks/update` and removes `tasks/list` [D]. A running task can raise an elicitation. Claude Code shows tasks in the footer and `/tasks`, announces completion in the transcript, and is CLI, Agent SDK and GitHub Actions only (not the VS Code extension or desktop app yet) [D].

What it enables: a `learning.review` tool that returns a task immediately, so the build is never blocked; the task stays `working` until the learner answers (in the terminal, on a URL page, or on the phone through the same server), then completes with the graded result. The agent sees "MCP task completed" and can give the feedback at the next natural pause. This is the cleanest protocol-native form of "question now, answer whenever".

Constraint: tasks are tied to the client that started them. A task cannot outlive the session's process for a local stdio server [S]; the durable state must live in `.learning/` so a new session can pick it up.

### 2.4 Notifications, subscriptions, list changes

- `notifications/tools/list_changed` and resource list changes are honored by Claude Code in interactive sessions (refetch without reconnect) [D]. Use: when a review becomes due, the server can expose a `review_due` prompt or resource and signal the change, so `@` mentions and prompt menus show "Review due: idempotency".
- Resource subscriptions (`resources/subscribe`, now `subscriptions/listen` in 2026-07-28) [D]. Claude Code did not subscribe to our probe's resources in a `-p` run [T: only `resources/list` was called]. Treat as not available for push into the agent.
- To actually wake a Claude Code session, the documented paths are Claude-specific: `claude/channel` channels (research preview, and not for servers that negotiate 2026-07-28), plugin monitors, `asyncRewake` hooks, the messaging socket [D] (see the sibling report). Protocol-level push into an idle agent does not exist in MCP.

### 2.5 Sampling

Sampling (server asks the client's model to generate) gained tool calling in 2025-11-25 and was deprecated in 2026-07-28 [D]. Claude Code did not declare a `sampling` capability to our probe [T]. Do not build on it. Grading stays with the agent (or a forked grader subagent) reading the rubric from the record.

### 2.6 Authorization

For a hosted learning server: OAuth 2.1 with Protected Resource Metadata (RFC 9728), Client ID Metadata Documents preferred over DCR, `iss` validation, incremental scopes via `WWW-Authenticate` [D]. Practical reading: a hosted server that holds a personal record must authenticate the learner, and the simplest identity provider for this audience is GitHub. Local stdio servers need no auth. Origin header checks (HTTP 403 on bad Origin) matter if the local server also listens on HTTP for the answer page [D].

## 3. MCP Apps

Extension `io.modelcontextprotocol/ui`, spec 2026-01-26 (SEP-1865) [D] ([spec](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx)).

| Piece | Detail | Use for this product |
| :- | :- | :- |
| `ui://` resource, `text/html;profile=mcp-app` | Linked from a tool via `_meta.ui.resourceUri` | The question card, the explain-back card, the record view |
| Sandbox and CSP | Sandboxed iframe (double iframe on web); `_meta.ui.csp` lists allowed origins; default blocks network; host may only tighten | Ship fonts and grain inline; no network needed |
| `ui/message` | View adds a message to the conversation (host may ask consent) | Lock an answer, post "My answer: B, fairly sure" into chat |
| `ui/update-model-context` | Stores context for future turns, overwritten each call, may be deferred | Tell the model the answer is locked without a visible message |
| `tools/call` from the view, `_meta.ui.visibility: ["app"]` | App-only tools are hidden from the model | `lock_answer` callable only by the card, so the model cannot answer for the learner |
| Display modes | `inline`, `fullscreen`, `pip`; host returns the applied mode | Inline question; fullscreen explainer; pip for a review timer while building in chat |
| Host context | Theme, styles, locale, time zone, platform, dimensions | Match light/dark; phone layout |

Where it renders: Claude chat web and desktop [T-prior], ChatGPT [D], VS Code Copilot, Goose, others [R]; not Claude Code including inside the Claude app [T-prior]; Codex desktop disputed (fixed per one user report, issue closed 2026-08-05) [R]. ChatGPT's guide recommends the standard bridge and keeps `window.openai` for extras such as widget state [D] ([ChatGPT UI](https://developers.openai.com/plugins/build/chatgpt-ui)).

Rubric safety: the card must not receive the rubric before lock. App-only tools help: `lock_answer` (app-only) returns the rubric and grade only after the server stores the locked answer.

## 4. Agent Client Protocol (ACP)

JSON-RPC 2.0 between an editor (client) and an agent running as a subprocess: `session/new`, `session/prompt`, `session/update` notifications, `session/request_permission`, `fs/*`, `terminal/*`; extensibility via `_meta` and underscore methods [D] ([overview](https://agentclientprotocol.com/protocol/overview)). Elicitation (`elicitation/create`, `elicitation/complete`, form and URL, session/tool-call/request scopes) was stabilized on 2026-07-24 [D] ([announcement](https://agentclientprotocol.com/announcements/elicitation-stabilized)).

What it enables: if the learner builds in an ACP editor (Zed, JetBrains and others, with Claude Code or Codex via adapters [R]), the agent's own elicitations reach the editor's native UI. More ambitiously, a **learning proxy agent**: an ACP agent that wraps the real agent, passes everything through, and inserts learning moments (prediction before the first write, explain-back on turn end) at protocol level, harness-independent [S]. Constraint: it only helps where an ACP client is in use; neither the Claude app nor the Codex app is an ACP client.

## 5. Codex app-server

Codex's own rich-client protocol: JSON-RPC over stdio (default), experimental WebSocket (`--listen ws://...` with `--ws-auth capability-token`), or Unix socket; Thread, Turn, Item; `turn/start`, `turn/steer`, `turn/interrupt`; server requests `tool/requestUserInput` (1 to 3 short questions, experimental) and `mcpServer/elicitation/request`; notifications such as `turn/completed`, `item/completed`, `fs/changed` [D] ([app-server](https://learn.chatgpt.com/docs/app-server)).

What it enables: a learning companion client (a small local web app or a mod-like pane) can attach to a running Codex thread, watch `turn/completed` to time an explain-back, and use `turn/steer` to inject "the learner answered: ..." into the in-flight turn [S]. `codex --remote` with TLS and token auth lets a remote TUI drive it [D]. Notifications: `notify` in `config.toml` runs a program on `agent-turn-complete`; `[tui] notifications` covers `approval-requested` [R].

Codex reads MCP server `instructions` from initialization (first 512 characters should stand alone) [D], so the learning server can carry the skill's ground rules to Codex even without the skill installed. Agent Skills (SKILL.md) are read by Codex from `~/.codex/skills` or `.agents/skills` per third-party guides [R].

## 6. A2A and AG-UI

| Protocol | What it is | Relevance | Mark |
| :- | :- | :- | :- |
| A2A 1.0 ([spec](https://a2a-protocol.org/latest/specification/)) | Agent to agent: Agent Card, tasks with `TASK_STATE_INPUT_REQUIRED`, webhooks push, streaming; JSON-RPC, gRPC, REST | A hosted "tutor agent" that any build agent delegates to ("make a debugging drill from this diff"); its `INPUT_REQUIRED` state and webhooks model asynchronous answers well. No consumer harness exposes A2A to the learner, so this is backend plumbing only. | [D] |
| AG-UI ([docs](https://docs.ag-ui.com/introduction)) | Agent to user-facing app: event stream over HTTP/WebSocket, interrupts for human in the loop, generative UI | Right protocol if we build our own learning app that talks to an agent directly (for example a phone app streaming a grader). Claude Agent SDK integration is community-made. Not reachable from Claude Code or Codex sessions. | [D] |

Both are worth knowing and not worth building on first. MCP plus elicitation already reaches the harnesses the owner uses.

## 7. The phone: PWAs and Web Push

| Fact | Mark |
| :- | :- |
| iOS/iPadOS 16.4+: Home Screen web apps can request push permission, from a user gesture; manifest `display` must be `standalone` or `fullscreen` ([WebKit](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/)) | [D] |
| iOS/iPadOS 18.4, macOS 15.5: Declarative Web Push: payload with `"web_push": 8030`, `notification.title`, `navigate`, optional `body`, `app_badge`; no service worker needed; a service worker can still modify it ([WebKit](https://webkit.org/blog/16535/meet-declarative-web-push/)) | [D] |
| Android Chrome: Web Push from a normal tab or installed PWA, no install requirement | [D] (long-standing platform behavior) |
| Web Push payloads are encrypted to the subscription keys (RFC 8291) and authenticated with VAPID (RFC 8292); the push service sees only metadata | [D] |

What it enables: the GitHub Pages site becomes the installable "Learning" app (one origin, the approved design), with a "Turn on reminders" pill button that subscribes. A review due on day 7 arrives as "1 review due. About 2 minutes." The tap opens the answer page. The app badge shows the count of due reviews.

The full chain, and where each piece runs:

1. Subscribe on `0xfauzi.github.io/explain-pr/app/` (service worker scope must sit under the Pages path). The subscription (endpoint plus keys) must reach the sender: copy-paste, a QR scanned by the laptop, or a write through a claude.ai artifact's `db` [S].
2. Schedule: the due list is computed from `.learning/` (`learning.py due`). A GitHub Actions `schedule:` workflow reads the committed record daily, or a Claude cloud scheduled task does [S].
3. Send: `pywebpush` or `web-push` with the VAPID private key in a repository secret [D for the libraries; S for the chain].
4. Answer: the page must post the answer somewhere durable. Options: a claude.ai artifact page (db capability) that the next session imports; a hosted learning MCP server; or GitHub (issue comment through the API with the learner's token) [S].

Constraints: the per-repo Pages origin is shared by all of `0xfauzi.github.io`; storage and push permission are per origin, not per path [D]. A static site cannot keep a secret, so it can never grade. Lock-screen text must be generic (no question text; it is visible to anyone holding the phone). iOS requires the Home Screen install, which is a visible onboarding step to design.

## 8. Push relays and OS notifications

| Tool | What it does | Privacy | Mark |
| :- | :- | :- | :- |
| ntfy ([publish docs](https://docs.ntfy.sh/publish/)) | HTTP PUT/POST to a topic; `Title`, `Priority`, `Tags`, `Click`, `Actions` (view, http, broadcast, copy), `Delay` up to 3 days; iOS and Android apps; self-hostable | Topic name is the password on ntfy.sh; no end-to-end encryption; self-hosting plus access tokens recommended | [D]; publish from this container accepted [T] |
| Claude Code `PushNotification` and Remote Control push | Phone push from a session | Anthropic-hosted | [D] (sibling report) |
| Codex `notify` | Runs a program on `agent-turn-complete` | Local | [R] |
| OSC 9 / OSC 777 terminal escapes | Terminal shows an OS notification (iTerm2, Ghostty, WezTerm, kitty, Windows Terminal) | Local | [R] |
| `osascript`, `notify-send`, `terminal-notifier` | OS notification from any CLI | Local | [D] |

Use: `learning.py` gets one `notify` function that tries, in order, the harness's own channel, Web Push, ntfy (only with a generic message), then a local OS notification.

## 9. Reaching a local page from the phone: tunnels

| Option | Reach | Identity | Constraints | Mark |
| :- | :- | :- | :- | :- |
| Tailscale Serve ([kb](https://tailscale.com/kb/1312/serve)) | Devices in the learner's tailnet; HTTPS on `*.ts.net` with valid certs | Adds `Tailscale-User-Login` and `Tailscale-User-Name` headers | Phone needs the Tailscale app; HTTPS certs must be enabled | [D] |
| Tailscale Funnel ([kb](https://tailscale.com/kb/1223/funnel)) | Public internet | None | Ports 443, 8443, 10000 only; beta; all plans | [D] |
| Cloudflare quick tunnel ([docs](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/)) | Public, random hostname per run | None | 200 in-flight requests; no SSE; testing only | [D] |
| Cloudflare Tunnel with Access | Public hostname gated by Access login | Access JWT | Needs account and domain | [D] |
| Codespaces port forwarding | `*.app.github.dev`, private by default | GitHub login | Only when building in a Codespace | [D] |

Tailscale Serve is the best of these for a local-first learner: private, real HTTPS (so service workers and push work), and identity headers that let `learning.py serve` know the viewer without its own login [D]. Funnel and quick tunnels expose a personal record publicly and need their own auth; do not use them for the record. Hosted claude.ai artifacts avoid tunnels entirely for Claude users [T-prior].

## 10. Sync: git, CRDTs, hosted stores

| Option | Fit | Mark |
| :- | :- | :- |
| Git with one file per attempt (current `record.py` layout) | Conflict-free for independent attempts; plain files; travels with the repo to every harness | [D] (record.py docstring) |
| Git union merge for append-only JSONL (`*.jsonl merge=union`) | Merged a laptop and a phone branch without conflict, both lines kept | [T] |
| Automerge 3 / automerge-repo, Yjs with y-indexeddb and y-websocket | Real-time multi-device co-editing with offline support; needs a sync server for cross-device; binary docs are not plain files | [D] (project docs); fit [S] |
| Claude artifact `db` | Hosted, per-artifact store readable by the page and by Claude via `ArtifactData`; the bridge from phone to next session | [T-prior] |

Recommendation: keep git as the source of truth; treat every other store (artifact db, a hosted server, the PWA's IndexedDB) as an inbox that the next session imports through `learning.py import`, with attempt ids as idempotency keys. CRDTs only if live shared explainers become a feature.

Privacy: the record is personal. If the repo is public, `.learning/` must be in a separate private repo, a private branch, or encrypted (for example `age` with a key on the learner's devices, or `git-crypt`) [S]. This is a first-run decision the product must ask once.

## 11. GitHub as a surface

| Mechanism | What it enables | Constraint | Mark |
| :- | :- | :- | :- |
| PR and issue comments | "Explain this PR back" posted on merge; the learner replies from GitHub Mobile; an Actions workflow (or `claude-code-action`) grades the reply into the record | Public repos make answers public | [D] |
| Check runs ([REST](https://docs.github.com/en/rest/checks/runs)) | A "Learning" check with up to 3 buttons (`requested_action`), Markdown summary up to 65,535 chars, annotations on lines ("Predict what this line does") | GitHub App only; buttons send a webhook to the app | [D] |
| GitHub Mobile notifications | Push for mentions, reviews, assigned issues, no setup | Notification text shows the issue title | [D] |
| Actions `schedule:` | Daily due-review job independent of any laptop or harness | Scheduled runs pause after 60 days without repo activity on public repos | [D] |
| Codespaces | Build plus private forwarded learning page reachable on the phone | Paid compute | [D] |

## 12. Security and privacy summary

| Risk | Where it arises | Mitigation |
| :- | :- | :- |
| Rubric visible before the answer locks | Bash command line in the transcript; attempt file committed and pushed; rubric shipped to a page; rubric in an elicitation `message` | Write rubrics through an MCP tool or forked subagent; store `sha256(rubric+salt)` until lock and reveal after; grade only where the rubric lives; app-only `lock_answer` tool returns the rubric after lock |
| Rubric changed after the answer | Agent grading leniently | Commit-reveal hash in the attempt file, checked by `learning.py check` |
| Question text on a lock screen or relay | ntfy, Web Push previews, GitHub notification titles | Generic notification text; encrypted Web Push payloads; self-hosted ntfy with tokens |
| Record exposed publicly | Public repo, Funnel, quick tunnels | Private record repo or encryption; Tailscale Serve, not Funnel |
| Phishing via URL elicitation | Hosted answer page | Bind elicitation to the learner identity; check the same subject opens it [D] |
| Model answers for the learner | MCP App or form tool callable by the model | App-only visibility for lock tools; elicitation requires the human client UI; record `answered_via` |
| Learner's answers used as model context | Elicitation results enter the transcript | Expected; say so in onboarding |

## 13. Options matrix (by surface)

| Surface | In-flow question | Rich answer page | Async review | Answer back to record |
| :- | :- | :- | :- | :- |
| Claude Code CLI | Elicitation form [T] | URL elicitation to local page [D] | MCP task, hooks, cloud scheduled task [D] | Server writes `.learning/` directly |
| Claude Code cloud / Claude app Code tab / phone | Elicitation card [D] | URL elicitation to hosted page (artifact) [D] | Push via Remote Control or Web Push [D/S] | Artifact db, then import |
| Claude chat (web, desktop, phone) | MCP App card [T-prior] | Fullscreen MCP App, artifact [D] | Artifact, push | `ui/message`, artifact db |
| Codex CLI | Elicitation (third-party reports) [R] | URL elicitation [R] | `notify`, Actions cron [R/D] | Server writes `.learning/` |
| Codex app | Elicitation via app-server [D] | MCP App possibly [R] | OS notification | Same server |
| ACP editors (Zed, JetBrains) | `elicitation/create` [D] | URL mode [D] | Editor-dependent | Same server |
| Phone without any harness | none | Installable page on Pages origin [S] | Web Push, ntfy, GitHub Mobile [D] | Artifact db, GitHub comment, hosted server |

## Appendix: tests run in this session

**A1. Claude Code elicitation capability and hook** [T]. A 60-line stdio probe server (scratchpad `probe/probe.py`) logged every message and answered `tools/call` with an `elicitation/create` (form: `answer` string, `confidence` enum). Run: `claude -p "Call the mcp__probe__ask tool once..." --mcp-config mcp.json --strict-mcp-config --settings settings.json --allowedTools mcp__probe__ask --model haiku`, with an `Elicitation` command hook that returned `{"hookSpecificOutput":{"hookEventName":"Elicitation","action":"accept","content":{...}}}`. Results: messages received in order `server/discover`, `initialize`, `notifications/initialized`, `tools/list`, `resources/list`, `tools/call`, then our elicitation response. `initialize` declared `capabilities: {roots: {listChanged: true}, elicitation: {form: {}, url: {}}}`, protocol `2025-11-25`, client `claude-code 2.1.319`. No `sampling`, no `resources/subscribe`. The hook input carried `hook_event_name: "Elicitation"`, `mcp_server_name`, `message`, `mode`, `requested_schema`. The server received `{"action":"accept","content":{"answer":"order saved, no email","confidence":"fairly sure"}}` and the model saw it in the tool result.

**A2. ntfy from the cloud container** [T]. `curl -H "Title: Review due" -H "Click: https://0xfauzi.github.io/explain-pr/" -d "probe from research agent" https://ntfy.sh/lwb-probe-<random>` returned an `event: message` JSON with an id and a 12-hour expiry. Delivery to a phone was not tested.

**A3. Git union merge on JSONL** [T]. With `.gitattributes` `*.jsonl merge=union`, a `main` branch appending `a2 asked` and a `phone` branch appending `a1 answered` merged with "Auto-merging events.jsonl" and no conflict; both lines kept.

## Cheapest next experiments

1. Interactive elicitation in the Claude app Code tab on the phone (cloud session): does the card appear, and does a titled enum render as buttons? One tool call with the probe server committed to `.mcp.json`.
2. URL elicitation in a cloud session to a claude.ai artifact answer page: does "Open link" open the artifact in the app, and does the artifact's db write reach the session?
3. Codex CLI and Codex app with the same probe server: record declared elicitation modes and whether MCP App cards render on the current build.
4. Installable page on the Pages origin with Declarative Web Push sent from a GitHub Actions job: does it arrive on an iPhone with the app closed?
5. Rubric visibility: run `learning.py ask` in Claude Code and Codex and screenshot what the learner sees; then the same through an MCP tool and a forked subagent.
