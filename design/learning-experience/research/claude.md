# Research track: Claude surfaces

What Claude Code (CLI, desktop app Code tab, web, mobile, IDE extensions) and the Claude app offer, as of 2026-11-07, that can carry a learning moment into a build and carry the learner's answer back out, without the learner leaving the flow.

Researcher: Claude surfaces track, one of five. Session: Claude Code 2.1.319, cloud container, artifact runtime contract 0.2.96.

## How to read the evidence marks

Every claim carries one mark.

| Mark | Meaning |
| :- | :- |
| **[T]** | Verified by a test I ran in this session (command and result are given). |
| **[T-prior]** | Verified by a test this project ran earlier (stated in the brief or in `experiments/`). |
| **[D]** | Documented officially: code.claude.com docs, or the platform's own type definitions served to this session (`/tmp/claude-0/bundled-skills/2.1.319/.../artifact-capabilities/0.2.96/*.d.ts`). |
| **[R]** | Reported by a third party (issue tracker, blog). |
| **[S]** | Speculative: my inference from the documented parts; needs a test. |

## The ten findings that matter most

1. **Mods are the native in-session learning surface we were missing.** A mod is a plugin with JavaScript hooks that runs inside Claude Code and can draw a band above the prompt, a pane beside the transcript, buttons, text inputs and selects, restyle the spinner and re-draw the `AskUserQuestion` dialog. It renders in the CLI, the desktop app's Code tab, and the VS Code extension. It can start a turn with `$.prompt.submit`, run timers, call a model, read files and keep a shared store. [D] [mods overview](https://code.claude.com/docs/en/plugins/mods/overview.md), [interface](https://code.claude.com/docs/en/plugins/mods/interface.md). I built a probe mod that reads `.learning/inbox.json`, draws "N question waiting" above the prompt with an Answer button, and adds an `/learn` command; `claude plugin validate` passed and a `claude plugin test` unit test passed on 2.1.319. [T]
2. **A running session can be pushed into, four documented ways.** (a) The per-session inbox socket `CLAUDE_CODE_MESSAGING_SOCKET`, which "a script or hook" can post to; messages from the session's own child processes are delivered by default. (b) Plugin **monitors**: a background command whose every stdout line reaches Claude as a notification. (c) Hooks with `asyncRewake`, which wake Claude "immediately even when the session is idle" on exit code 2. (d) **Channels** (`claude/channel` MCP capability), research preview, CLI only. [D] for all four; the socket and its token are present in this session's environment [T].
3. **A hosted page can talk to the learner's running Claude.** Artifact `comments.sendToClaude` posts a comment and notifies the Claude sessions watching the artifact; the publishing session watches its artifacts and receives a sent comment "right away" (Claude Code 2.1.228+). `room.sendToClaudeSession` hands page data to the conversation beside the page, or with `deliver: "send"` to a session of the viewer's that has the artifact. Live docs go further: "the moment the edit lands, Claude is told what changed" and answers in place. [D] ([artifacts](https://code.claude.com/docs/en/artifacts.md), `comments.d.ts`, `room.d.ts`, `artifact.d.ts`).
4. **The phone is reachable today without a tunnel**, through Remote Control (drive a local session from the Claude app; `AskUserQuestion` questions are forwarded and stay open; push notifications to the phone via the `PushNotification` tool and two `/config` toggles), through cloud sessions, and through hosted artifacts that open on the phone. [D] [remote control](https://code.claude.com/docs/en/remote-control.md), [mobile](https://code.claude.com/docs/en/mobile.md); artifacts open on the phone [T-prior].
5. **MCP elicitation gives a native, structured answer form inside the build**, in the CLI terminal and, for cloud sessions, as a card on claude.ai/code and in the desktop Code tab. Form mode can carry an answer field plus a confidence enum; the `Elicitation` hook can observe or answer it. [D] [mcp](https://code.claude.com/docs/en/mcp.md#respond-to-mcp-elicitation-requests). This is the replacement for MCP Apps in Claude Code, which do not render there [T-prior].
6. **Spaced retrieval can run on the platform's clock, not the learner's memory.** Cloud scheduled tasks (formerly routines) run with the laptop closed, can fire into an existing session (`persistent_session_id`) or a fresh one, can push to the phone or email, and have an API trigger (`POST .../fire` with a `text` payload). Desktop scheduled tasks run locally; `/loop` and `CronCreate` are session-only and expire after 7 days. [D] [routines](https://code.claude.com/docs/en/routines.md), [scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks.md); the create/send_later tools are present in this session [T].
7. **A page opened in the Claude app can call a local MCP server on the viewer's device** (`mcp` capability, `server: "host:<name>"`), and any page can call the `Claude Code Remote` connector's tools as the viewer. That is a route for a hosted learning page to read and write the repo's plain-file record through a local `learning` MCP server, and possibly to message a session. [D] (live capability roster served by the artifact-capabilities skill this session). Viewer tool sets may be smaller; untested. [S] for the session-messaging use.
8. **Deep links exist for every local surface**: `claude-cli://open?repo=owner/name&q=...` (terminal), `claude://code/new?q=...` (desktop app new session), `vscode://anthropic.claude-code/open?prompt=...&session=<id>` (resume a VS Code session), `https://claude.ai/code/session_<id>` (web and phone), and artifact links with `#anchor` per view. None of them sends the prompt by itself. GitHub strips custom schemes, so they cannot live on the GitHub Pages site as links, only on artifacts or local pages. [D] [deep links](https://code.claude.com/docs/en/deep-links.md), [desktop](https://code.claude.com/docs/en/desktop.md), [VS Code](https://code.claude.com/docs/en/vs-code.md).
9. **There are built-in learning precedents to build on, not compete with**: the `Learning` output style (leaves `TODO(human)` for real design decisions), `/btw` side questions that run while Claude is working and add nothing to history, the desktop side chat (Cmd+;), "You should know" notes above the prompt, and prompt suggestions. [D] [output styles](https://code.claude.com/docs/en/output-styles.md), [interactive mode](https://code.claude.com/docs/en/interactive-mode.md).
10. **Every hook event is available to time a learning moment**, including `Stop` (with `last_assistant_message`, `background_tasks`, `session_crons`), `PostToolBatch`, `TaskCompleted`, `SubagentStop`, `PostToolUseFailure` (debugging drills), `Notification` with `idle_prompt` (a natural "you are away, here is a question" moment), `FileChanged` (fires for any process that changes a watched file), `PreCompact` and `MessageDisplay`. [D] [hooks](https://code.claude.com/docs/en/hooks.md).

The rest of this report gives the detail, a per-surface matrix, what each mechanism enables for this skill, and the cheapest experiments.

## 1. The surfaces and what each one is

| Surface | Where code runs | What the learner sees | Notes |
| :- | :- | :- | :- |
| Claude Code CLI | Learner's machine | Terminal UI | Everything below works here first. [D] |
| Desktop app, Code tab | Learner's machine (local, SSH, WSL) or cloud | Panes: chat, diff, browser, terminal, file, plan, tasks, subagent; session details rail | Hosts Claude Code through the Agent SDK `canUseTool` path. Browser pane opens local HTML files clicked in chat. Side chats with Cmd+;. OS notification when a session finishes and you are not viewing it. [D] [desktop](https://code.claude.com/docs/en/desktop.md) |
| VS Code extension, JetBrains | Learner's machine | Chat panel (VS Code), integrated terminal (JetBrains) | Mods render in the VS Code panel from extension 2.1.299. [D] |
| claude.ai/code (web) and Claude app Code tab (phone) | Cloud sessions, or the learner's machine via Remote Control | Transcript, diff pane, questions, elicitation cards | Remote Control forwards `AskUserQuestion` and permission prompts and keeps them open. Local-only commands (`/plugin`, `/resume`) do not work from the phone. [D] |
| Claude app chat (web, desktop, phone) | Anthropic | Chat with MCP Apps, artifacts | MCP Apps render here, not in Claude Code. [T-prior] [D] |
| Hosted artifact page | Anthropic, claude.ai viewer | A private page on claude.ai, desktop and phone browsers | Capabilities live roster this session: `artifact`, `assets`, `comments`, `db`, `downloads`, `files`, `mcp`, `room`, `sample`, `self`, `user`, plus built-in `permissions`. [T] (roster served to this session) |
| Dispatch | Desktop app, launched from the phone | A Code session in the sidebar; push when it finishes or needs approval | Pro, Max, Ultra only. [D] |

## 2. Moving from building to learning: how the build raises a learning moment

These are the mechanisms that let the agent (or the harness itself) put a question, a drill or an explanation in front of the learner at the right moment.

### 2.1 Skills and plugins

| Item | What it is | What it enables for this skill | Mark |
| :- | :- | :- | :- |
| Skill (`SKILL.md`) | Instructions Claude loads when the task matches or on `/name` | The current product. Agent Skills standard, so it also runs in other harnesses. | [D] [skills](https://code.claude.com/docs/en/skills.md) |
| `` !`command` `` dynamic context | Shell output inlined into the skill before Claude reads it | Inline `learning.py inbox --brief` and due reviews at invocation, so the skill always starts from the record. Not run for skills synced from claude.ai into other sessions. | [D] |
| Skill frontmatter `hooks` | Hooks registered when the skill is invoked, kept for the session | The skill can install its own Stop or PostToolUse checkpoint hooks the first time it runs, with no settings edit. | [D] |
| `context: fork`, `background` | Run the skill in a forked subagent, optionally in the background | A grader or question-writer that does not consume the build's context and does not block it. | [D] |
| `disallowed-tools` | Tools removed while the skill is active | Keep `AskUserQuestion` out of a background grading loop so it never blocks. | [D] |
| Plugin | Package of skills, commands, agents, hooks, MCP servers, LSP, monitors, output styles, themes, channels, mods, `bin/` executables, default `agent` setting | The distribution unit: one `/plugin install learning-while-building@...` gives skill + hooks + monitor + mod + MCP server + output style. Works in CLI, desktop, VS Code; cloud sessions load plugins that reach them. | [D] [plugin components](https://code.claude.com/docs/en/plugins/components.md) |
| Plugin `bin/` executables | Commands put on the PATH while the plugin is enabled | `learning` as a real command instead of `python3 skills/.../learning.py`. | [D] |
| Plugin `userConfig` | Install-time options | Learner preferences (quiet hours, max questions per session, phone pushes on/off). | [D] |
| Plugin evals (`claude plugin eval`) | Eval cases with a no-plugin baseline | Measure that the skill asks one prediction before a build and never praises. | [D] [plugin evals](https://code.claude.com/docs/en/plugin-evals.md) |

### 2.2 Hooks (settings hooks), every event

Handler types: `command`, `http`, `mcp_tool`, `prompt` (single-turn model judgment), `agent` (experimental, tool-using). Options include `async` (background, result delivered on the next turn) and `asyncRewake` (background, exit code 2 wakes Claude at once even when idle). [D] [hooks](https://code.claude.com/docs/en/hooks.md)

| Event | When | Learning use | Mark |
| :- | :- | :- | :- |
| `SessionStart` | Session begins or resumes | Inject "2 reviews due, 1 answer waiting to grade" as context; return `watchPaths` for `FileChanged`. | [D] |
| `Setup` | `--init-only`, or `--init`/`--maintenance` with `-p` | Create `.learning/` once. | [D] |
| `InstructionsLoaded` | CLAUDE.md or rules load | Detect which dimensions the project touches. | [D] |
| `UserPromptSubmit` | Prompt submitted (also on self-started turns) | Detect "build X" requests and add a reminder: ask one prediction first. Detect an answer typed in chat and route it to the record. | [D] |
| `UserPromptExpansion` | A typed command expands | Gate `/learn` variants. | [D] |
| `PreToolUse` | Before a tool runs; can block or `defer` | Hold the first `Write` of a planned build until the prediction is answered, only in "strict" mode. In the Agent SDK, `defer` pauses for a long user wait. | [D] |
| `PermissionRequest` | A permission decision is needed | Not a learning moment; leave alone. | [D] |
| `PermissionDenied` | Auto mode denied a call | None. | [D] |
| `PostToolUse` | After a tool succeeds | Count edits per dimension; after tests go green, mark "explain-back due". | [D] |
| `PostToolUseFailure` | After a tool fails | A failing test or crash is the cue for a debugging drill: "Before I look, what do you think broke?" This targets the largest gap in Shen and Tamkin. | [D] |
| `PostToolBatch` | After a batch of parallel calls | Cheaper single checkpoint per batch. | [D] |
| `Notification` | Claude Code notifies; matchers `permission_prompt`, `idle_prompt`, `elicitation_dialog`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`, `auth_*`, `quota_auto_resume_*`, `plugin_notification` | `idle_prompt` (about 60 s after Claude finishes and you have not typed) is the natural moment to post a retrieval question to the phone. | [D] |
| `MessageDisplay` | While assistant text streams | Display-only rewrite: strip praise words, or format "Correct." / "Not quite." lines. Claude never sees the change. | [D] |
| `SubagentStart`, `SubagentStop` | Subagent lifecycle | A grader subagent finishing is a cue to show feedback. | [D] |
| `TaskCreated`, `TaskCompleted` | Task list changes | A completed task is a natural explain-back checkpoint. | [D] |
| `Stop` | Main agent finished responding; input has `last_assistant_message`, `background_tasks`, `session_crons`; can block to continue (8-continuation cap) | The main checkpoint hook: if a build just went green and no explain-back is posted, continue the turn with "post the explain-back now". A `prompt` hook can judge this. `/goal` is a built-in prompt-based Stop hook. | [D] |
| `StopFailure` | Turn ended on API error | None. | [D] |
| `TeammateIdle` | Agent team teammate goes idle | None for now. | [D] |
| `ConfigChange`, `CwdChanged`, `DirectoryAdded` | Config or directory changes | Re-resolve the record location. | [D] |
| `FileChanged` | A watched file changes on disk, whoever changed it | When the local page or terminal saves an answer to `.learning/answers/...`, the hook fires; its `systemMessage` shows a brief terminal notice. No decision control; for waking Claude use `asyncRewake` or a monitor. | [D] |
| `WorktreeCreate`, `WorktreeRemove` | Worktrees | Share one record across worktrees. | [D] |
| `PreCompact`, `PostCompact` | Context compaction | Save "questions in flight" before compaction loses them. | [D] |
| `PreModelSwitch`, `PostModelSwitch` | Model changes | None. | [D] |
| `SessionEnd` | Session ends (1.5 s budget) | Write a session summary to the record. | [D] |
| `Elicitation`, `ElicitationResult` | MCP server asks for input; user responds | Log the answer and confidence to the record even if the server is elsewhere. | [D] |

Environment hints for hooks: `$CLAUDE_CODE_REMOTE` is `"true"` in cloud sessions; `$CLAUDE_CODE_BRIDGE_SESSION_ID` is set while a local session has Remote Control, which tells a hook the learner may be on the phone. [D]

### 2.3 Mods (the in-process interface layer)

Mods are plugins whose hooks module exports `register(on)`. Requires CLI 2.1.287+ or desktop's bundled 2.1.286+. Not sandboxed; runs with the user's permissions; `claude plugin validate` lists every event and call a mod makes. [D] [mods reference](https://code.claude.com/docs/en/plugins/mods/reference.md)

Where drawing appears: terminal (yes), desktop Code tab (yes, except terminal-only elements; not in WSL sessions), VS Code panel (yes, 2.1.299+), `claude -p` and Agent SDK (hooks run, nothing draws), Remote Control (hooks run on the machine; drawing only in the machine's terminal, not on the phone), cloud sessions (hooks run if the plugin reaches the session; nothing draws). [D]

| Capability | API | Learning use | Mark |
| :- | :- | :- | :- |
| Band above the prompt | `ui.render` on `AbovePrompt` (terminal, desktop) | A one-line, always-present "learning strip": "1 question waiting · 2 reviews due · Answer [1]". Digit hotkeys fire when typed alone into an empty prompt. This is the seamless switch between building and learning: no context switch, no new window. | [D] [T] (probe mod) |
| Pane | `$.ui.open({id})`, `ui.render` on `Pane` (terminal, desktop, VS Code) | The full question card: prompt, code excerpt (`Code` element with `path` and `startLine`), answer `Input` with `rows`, confidence `Select`, "I don't know", "Not now". A pane opened by the mod itself only appears in terminals 144 columns wide (110 after the user opened it once), so open it from a command or button. | [D] |
| Record visualisation | `Svg` (desktop, VS Code), `Raster` (terminal) | Draw the per-dimension record ramp (#F6C9AF, #EE8B5B, #C2410C) as cells, the site's visual signature, inside the app. | [D] |
| Restyle Claude Code's own rows | `ui.render` on `Spinner`, `ToolUse`, `TurnDuration`, `AskUserQuestion`, `PromptHint` | Spinner suffix "· 1 question waiting"; a line under each turn via `turn.complete` returning `{text}`; add a confidence row above the `AskUserQuestion` dialog (the dialog must keep Claude Code's reference once). The permission prompt cannot be changed. | [D] |
| Commands that run without a turn | `$.command.register({name, immediate: true})` + `command.run` | `/learn`, `/record`, `/due` that open panes instantly even while Claude is working: the learner can answer mid-build without stopping it. | [D] [T] |
| Tools for Claude | `$.tool.register` (appears as `mcp__<plugin>__<name>`) | `learning_post`, `learning_grade` tools backed by the record, without an MCP server process. | [D] |
| Start a turn | `$.prompt.submit({text})` waits until idle, then starts a turn | When the learner submits an answer in the pane, queue "Grade attempt 42 against its rubric" for the next idle moment. Never interrupts a build. | [D] |
| Model calls | `$.model.complete`, `$.model.fork` (forks the conversation, prompt-cached) | Grade a short answer in the mod itself, on the session's plan, against the stored rubric, and show "Correct." at once. Or write the question with full build context via `fork`. | [D] |
| Background timers | `$.clock.every`, `$.ui.status`, `$.ui.toast`, `$.ui.log`, `$.ui.notify` | Poll the record for answers from the phone page; show a status line; raise an OS notification (`notify` returns `no-surface` in desktop and VS Code). | [D] |
| State | `$.store` (shared by every session on the machine, 4 MiB), `$.state` | Cross-session "questions in flight" without races on files. | [D] |
| Cross-session | `$.session.send`, `session.receive` (with `origin.kind` such as `peer`, `scheduled-trigger`) | Route a review question to whichever session the learner is in now. | [D] |
| Surfaces | `$.session.surfaces`, `session.attach`/`detach` events | Know when a Remote Control device attaches (learner on phone) and switch to push-style delivery. | [D] |
| Audio | `$.audio.speak` | Read a review question aloud. Accessibility option, off by default. | [D] |
| Tests | `claude plugin test` with stubs | The learning UI is unit-testable in CI with no session. | [D] [T] |

Test I ran [T]: a mod at `/tmp/claude-0/-home-user-explain-pr/074e39f7-08cf-5ec8-b66b-62906beb6d01/scratchpad/lwb-mod/` with `session.start`, `command.run{command=learn}`, `ui.render{component=AbovePrompt}`, `turn.complete`. `claude plugin validate ./lwb-mod` printed the hooks and calls and "Validation passed with warnings" (README, LICENSE, icon). `claude plugin test` ran one test that fires `session.start` with a stubbed `fs.read` returning two questions, then runs `/learn`, and checks the pane `learn` opened: "1 pass". I could not see a live render: this cloud container has no desktop app or interactive TTY to show.

### 2.4 Output styles, status line, prompt suggestions, built-in learning features

| Item | What it enables | Mark |
| :- | :- | :- |
| Output style (custom, shippable in a plugin) | A session-wide voice: plain feedback, no praise, "one question at a time". Note: a custom style drops Claude Code's built-in coding instructions unless `keep-coding-instructions: true`. The repo already has `output-styles/`. | [D] [output styles](https://code.claude.com/docs/en/output-styles.md) |
| Built-in `Learning` style | Leaves `TODO(human)` at real design decisions and waits; adds `Insight` blocks. This is generation practice, close to Kapur's productive failure. The skill should coexist: if Learning style is on, do not also ask a prediction for the same decision. | [D] |
| Status line | A shell command's output in its own row, refreshed on events or every N seconds (`refreshInterval`), with OSC 8 clickable links in terminals that support them. "Record: 3 recalls, 1 transfers · 1 due" and a link to the hosted page. CLI only; desktop shows its own UI. | [D] [status line](https://code.claude.com/docs/en/statusline.md) |
| Prompt suggestions, `prompt.suggest`/`prompt.fill` in mods | A dim suggested next prompt; a mod can suggest "/learn answer" when a question is waiting. Desktop has its own "suggested prompt". | [D] |
| "You should know" | Built-in side agent that shows one note above the prompt. A precedent for the band. | [D] |
| `/btw` and desktop side chat | Ask about the build while Claude keeps working, nothing added to history. The right place for "how does this work?" questions, which the research says protect understanding. It has no tools, so any answer meant for the record must be restated in the main session or the pane. | [D] [interactive mode](https://code.claude.com/docs/en/interactive-mode.md) |

### 2.5 Questions inside the session

| Item | What it enables | Limits | Mark |
| :- | :- | :- | :- |
| `AskUserQuestion` tool | Multiple choice with an `Other` free-text row and a notes field. Forwarded to the phone under Remote Control and kept open. Good for predictions with plausible distractors and for confidence as a second question. | Blocks the turn until answered (optional `askUserQuestionTimeout` 60 s, 5 m, 10 m, not under Remote Control). Use only for the pre-build prediction when the learner is present. | [D] [tools reference](https://code.claude.com/docs/en/tools-reference.md) |
| MCP elicitation, form mode | A server-defined form during a tool call: `answer` (string), `confidence` (enum: guessing, unsure, fairly sure, certain), `dont_know` (boolean). Rubric stays on the server, so it is fixed before the question and invisible. | Blocks the tool call while the dialog is open (Claude Code does not background a call that waits on a dialog). In `-p` and SDK sessions without a handler, the request is cancelled. Answerable as a card in cloud sessions on claude.ai/code and desktop. Phone under Remote Control: not documented. | [D] [mcp](https://code.claude.com/docs/en/mcp.md#respond-to-mcp-elicitation-requests) |
| MCP elicitation, URL mode | Ask the learner to open a URL (the hosted page or the local page), then "I'm done, continue". | Opens a browser; a context switch. | [D] |
| MCP tasks with input requests | A long-running server task that can ask a question later. | `elicitation/create` only served in interactive terminal sessions. | [D] |
| Plan mode / `ExitPlanMode` | The plan approval moment is a prediction moment: "Before you approve, which file will change most?" | Do not block approval on it. | [S] |

### 2.6 Notifications and the phone

| Item | What it enables | Mark |
| :- | :- | :- |
| `PushNotification` tool | Desktop notification locally; phone push with Remote Control or in a cloud session. The tool skips when the learner is at the terminal. Under 200 characters: "1 question waiting: why does the retry use jitter?" | [D] [T] (tool present in this session) |
| `/config` toggles "Push when Claude decides", "Push when actions required" | The learner opts in; `CLAUDE_CLIENT_PRESENCE_FILE` suppresses pushes while they are at the machine. | [D] |
| Desktop OS notification on session finish | Free: the end of a build is announced; the skill should make the first line of the final message the learning ask. | [D] |
| Cloud scheduled task notifications (`push`, `email`) | A daily review run notifies only "when a run finishes with something noteworthy". | [D] (tool schema in this session) |
| Dispatch push | When a Dispatch-spawned Code session finishes or needs approval. | [D] |

### 2.7 Pages the agent can open for the learner

| Item | What it enables | Mark |
| :- | :- | :- |
| Artifact (Claude Code `Artifact` tool) | A private hosted page on claude.ai; opens in the browser on publish; `Ctrl+]` reopens the latest; a `⧉` pill below the prompt lists the session's artifacts; anchors link to one view (`#review`). Under Remote Control, no tab opens on the machine. | [D] [artifacts](https://code.claude.com/docs/en/artifacts.md) |
| Desktop Browser pane | Clicking an HTML path in chat opens it in a pane beside the chat. The local page (`learning.py serve`) can be a configured preview server in `.claude/launch.json`, so it lives in the same window as the build. | [D] [desktop preview](https://code.claude.com/docs/en/desktop.md#preview-your-app) |
| `SendUserFile` | Sends a file (an explainer HTML, a record PNG) to the learner's device with `display: render`. | [D] [T] (tool present) |
| Mods `Link` element | Opens an https URL from a pane (desktop and VS Code require https or http://localhost). | [D] |

## 3. Moving from learning back to building: how an answer reaches the running session

This is the part that looked impossible ("a page cannot talk to a running session"). It is not. There are at least nine documented paths. The table is ordered from most native to most indirect.

| # | Path | Learner is | Reaches | Latency and wake | Mark |
| :- | :- | :- | :- | :- | :- |
| 1 | Answer in the mod pane; mod writes the record and `$.prompt.submit`s "grade attempt N" | At the machine (CLI, desktop, VS Code) | Same session, next idle moment | Immediate, never interrupts | [D] |
| 2 | Answer in chat (local or from the phone via Remote Control) | Anywhere | Same session | Immediate | [D] |
| 3 | Elicitation form or `AskUserQuestion` | Present | Same session, inside the turn | Immediate, blocks | [D] |
| 4 | Local page (`learning.py serve`) saves the answer, then posts a line to `$CLAUDE_CODE_MESSAGING_SOCKET` | At the machine, or in the desktop Browser pane | Same session; own-child messages delivered by default when no `crossSessionInbound` applies | Delivered when Claude is free; arrives as a message | [D]; socket and token present here [T]; wire format not documented [S] |
| 5 | Plugin monitor running `tail -F .learning/events.jsonl` | Any route that writes the record (terminal `learning.py answer`, local page, `room-pull`) | Same session as a notification | Each line is an event; interactive sessions only | [D] [plugin monitors](https://code.claude.com/docs/en/plugins/components.md#monitors) |
| 6 | `asyncRewake` hook started at `SessionStart` that waits for a new answer file and exits 2 | Same as 5 | Same session, wakes even when idle | Immediate | [D] |
| 7 | Hosted page: `comments.sendToClaude` (owner or editor) | Phone or desktop browser | The publishing session, which watches its artifacts; replies arrive in the thread | "Right away"; permission mode decides whether Claude replies alone; 60 sends per hour cap per artifact | [D] [artifacts](https://code.claude.com/docs/en/artifacts.md#let-claude-reply-to-comments-on-its-own), `comments.d.ts` |
| 8 | Hosted page: `room.sendToClaudeSession(data, {deliver})` | Page open beside a conversation, or alone | `pane`: the conversation beside the page; `session`: a session of the viewer's that has the artifact; `new`: a new conversation; staged by default, `send` asks the viewer once | From the viewer's click only; `canSendToClaudeSession()` says which | [D] `room.d.ts` |
| 9 | Hosted page writes `db`; session reads it with `ArtifactData` at the next checkpoint (current `room-pull`) | Anywhere | Any session, on demand | Polling | [D] [T-prior] |
| 10 | Live doc edit (`artifact.edit` or a gesture on synced markup) | Anywhere | "a watching Claude session", which "typically answers with an edit of its own a second or two later" | Real time | [D] `artifact.d.ts` (live docs are created by the platform, for example Claude Docs) |
| 11 | Room agent peer: the publishing Claude Code session joins the room as `kind: "agent"` and reads a digest | Anywhere | Publishing session | Flag-gated, off by default | [D] `room.d.ts` |
| 12 | Channel server (`claude/channel` capability) with a webhook or a chat bridge (Telegram, Discord, iMessage, fakechat) | Phone chat app | Session started with `--channels` | Immediate; research preview; allowlisted plugins only, `--dangerously-load-development-channels` for our own; CLI only; not on the v2 MCP revision 2026-07-28 | [D] [channels](https://code.claude.com/docs/en/channels.md), [reference](https://code.claude.com/docs/en/channels-reference.md) |
| 13 | Cross-session `SendMessage` / `mcp__claude-code-remote__send_message` | Another session (for example a review session on the phone) | Another local, Remote Control or cloud session | Immediate; cloud sessions cannot reply across machines | [D] [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging.md) |
| 14 | Page `mcp` capability calling `host:learning` (a local MCP server) | Page opened in the Claude desktop app | The local record directly, no session needed | Immediate | [D] (live roster text this session) |
| 15 | Page `mcp` capability calling the `Claude Code Remote` connector's `send_message` | Any Claude app | A cloud or Remote Control session | Unknown | [S]: "a viewer may have fewer of the connector's tools", untested |
| 16 | Cloud scheduled task API trigger `POST /fire` with `text` | Any process with the token | A fresh cloud session (or the task's bound session) | Seconds | [D] [routines](https://code.claude.com/docs/en/routines.md#add-an-api-trigger) |
| 17 | `watch_url` inbound webhook (cloud sessions) | Artifact service only (signed) | This cloud session as `<webhook-payload>` | Immediate | [D] (tool schema in this session; signing secret only usable by the artifact service) |

What this means: the learner can answer on whichever surface is in front of them, and the running build session hears about it within seconds on every Claude surface. The record (plain files in the repo) stays the source of truth; each path only says "something changed, go grade it".

## 4. Links into sessions and pages

| Link | Opens | Carries | Mark |
| :- | :- | :- | :- |
| `claude-cli://open?repo=owner/name&q=...` or `&cwd=/abs/path` | A new terminal with Claude Code in that repo, prompt filled, not sent; warning line "Prompt from an external link" | Prompt up to 5,000 chars | [D] [deep links](https://code.claude.com/docs/en/deep-links.md) |
| `claude://code/new?q=...` (plus `ssh_host`, `ssh_port`, `ssh_folder`) | Desktop app new-session page, prompt filled | Prompt | [D] [desktop](https://code.claude.com/docs/en/desktop.md#open-an-ssh-session-from-a-link) |
| `vscode://anthropic.claude-code/open?prompt=...&session=<id>` | A VS Code Claude tab, optionally resuming a session | Prompt, session id | [D] [VS Code](https://code.claude.com/docs/en/vs-code.md) |
| `https://claude.ai/code/session_<id>` | The session on web and phone | Nothing else | [D] |
| `https://claude.ai/code/artifact/<uuid>#anchor` | The hosted page at one view | Anchor | [D] |
| Custom schemes on GitHub | Stripped from READMEs, issues, wikis and GitHub-rendered Markdown | Put them in code blocks or on the hosted page instead. GitHub Pages HTML is a static site, not rendered Markdown, so a plain `<a href="claude-cli://...">` there should work in browsers that allow the scheme. | [D] for GitHub Markdown; [S] for Pages HTML |

A link that resumes a specific local CLI session from the phone does not exist; Remote Control is the route for that. [D by absence in the deep links page]

## 5. Scheduling spaced retrieval (gaps 3, 7, 21, 60, 180 days)

| Option | Runs on | Survives | Fits | Mark |
| :- | :- | :- | :- | :- |
| `CronCreate` / `/loop` | The open session | Session only; recurring jobs expire after 7 days; restored on `--resume` if unexpired | In-session reminders ("in 20 minutes, ask the explain-back"). Not for 21-day gaps. | [D] [T] (tool present; schema states 7-day expiry) |
| Desktop scheduled tasks | Learner's machine, no open session needed | Restarts; missed runs handled | A morning "reviews due" run against local files. Machine must be on. | [D] [desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks.md) |
| Cloud scheduled tasks (`/schedule`, `create_trigger`) | Anthropic cloud, fresh clone of the repo | Yes, minimum 1 hour interval | A daily run that reads `.learning/` from the repo, publishes or updates the hosted review page, writes due questions to its `db`, and pushes to the phone. Can bind to a persistent session or spawn fresh. API trigger for external events. | [D] [routines](https://code.claude.com/docs/en/routines.md) |
| `send_later` | This cloud session | Container restarts | A one-shot "come back to this question tomorrow" (a miss returns next day). | [D] [T] (tool present) |

The record files are the scheduler's state; any of these only needs to run `learning.py due`.

## 6. MCP in Claude Code, item by item

| Feature | Status in Claude Code | Learning use | Mark |
| :- | :- | :- | :- |
| Tools | Yes; deferred behind tool search unless marked to load upfront | `learning_post`, `learning_answer`, `learning_grade`, `learning_due`. Mark core tools `isDeferred: false` so Claude sees them every turn. | [D] |
| Resources and `@` mentions | Yes, `@server:proto://path` | `@learning:record://dimension/concurrency` attaches the learner's record for a dimension. | [D] |
| Resource subscriptions | Not documented for Claude Code | Do not rely on it. | [D by absence] |
| `list_changed` | Yes; v2 runtime holds a stream open | A server can add a `learning_answer_waiting` prompt or tool when an answer arrives. | [D] |
| Prompts as slash commands | Yes, `/server:prompt (MCP)` | `/learning:practice`, `/learning:review`. | [D] |
| Elicitation | Form and URL modes on user-configured servers (2.1.287+) and on revision 2026-07-28 | See 2.5. | [D] |
| Sampling | Not documented for Claude Code | Grade with `sample` on the page or `$.model.complete` in a mod instead. | [D by absence] |
| Notifications into the session | Only through the channel capability | See path 12. | [D] |
| MCP tasks | Yes, long calls become tasks with status messages | A grading task that runs in the background and reports. | [D] |
| MCP Apps (`ui://`) | Not rendered; `ui://` resources are hidden from `@` and resource listing, still readable by URI | None in Claude Code. Keep the experiment server for Claude chat. | [T-prior] [D] [R] [community request](https://claudeissues.com/issue/88881-feature-render-mcp-apps-for-locally-configured-mcp-servers-config-file-localhost) |
| Claude Code as an MCP server (`claude mcp serve`) | Yes | Another harness could drive Claude Code's tools; not needed here. | [D] |

## 7. Agent SDK

The SDK runs the same Claude Code loop from Python or TypeScript. `AskUserQuestion` and permission requests both reach the host's `canUseTool` callback, which can stay pending indefinitely; a `PreToolUse` hook can `defer` for long waits. Hooks, skills, plugins, subagents and `MessageDisplay` work; mods run but draw nothing; channels' development flag is ignored; artifacts are off by default. [D] [Agent SDK user input](https://code.claude.com/docs/en/agent-sdk/user-input.md), [overview](https://code.claude.com/docs/en/agent-sdk/overview.md)

What it enables: our own small host (for example a "learning companion" desktop or web app) that runs builds through the SDK and renders the learning UI natively, for learners who are not in the Claude app. This is a later option, not the first move: the owner works in the Claude app, where mods, artifacts and Remote Control already reach.

## 8. Per-surface matrix

Rows are mechanisms; columns are where the learner is. Y = works, N = does not, P = partly, ? = untested or undocumented.

| Mechanism | CLI | Desktop Code tab (local) | VS Code | Phone via Remote Control | Cloud session (web, phone) | Claude chat |
| :- | :-: | :-: | :-: | :-: | :-: | :-: |
| Skill + `learning.py` | Y | Y | Y | Y (runs on the machine) | Y | P (no shell) |
| Settings hooks | Y | Y | Y | Y (on machine) | Y | N |
| Mod band and pane | Y | Y | Y (pane, not band) | N (draws on machine only) | N | N |
| Mod commands, tools, timers, `$.prompt.submit` | Y | Y | Y | Y (on machine) | Y if plugin reaches it | N |
| Plugin monitor | Y | ? (interactive; desktop hosts via SDK) | ? | Y (on machine) | ? | N |
| Inbox socket post | Y | Y | Y | Y (on machine) | Y (same container) | N |
| Channels | Y (`--channels`) | N | N | N | N | N |
| `AskUserQuestion` | Y | Y | Y | Y (forwarded, stays open) | Y | N |
| MCP elicitation form | Y | ? local; Y cloud card | ? | ? | Y (card) | N |
| `PushNotification` | desktop notice | desktop notice | ? | Y phone | Y phone | N |
| Status line | Y | N | N | N | N | N |
| Output style | Y | Y | Y | Y | Y | N |
| `/btw` side question | Y | Y (side chat) | Y (panel) | ? | ? | N |
| Artifact publish | Y | Y | ? | Y (published from the machine; no tab opens) | Y | Y (chat artifacts are a different runtime) |
| Hosted page grading (`db` + `sample`) | Y | Y | Y | Y | Y | Y |
| Page to session (`comments.sendToClaude`, `room.sendToClaudeSession`) | Y (publishing session watches) | Y | ? | Y | Y | Y (pane) |
| Deep link into a new session | `claude-cli://` | `claude://code/new` | `vscode://...` | N | `claude.ai/code/session_` | N |
| Local page (`learning.py serve`) | Y | Y (Browser pane) | Y | N without tunnel | N | N |

## 9. Things that looked impossible, and the mechanism that makes them possible

| Looked impossible | Mechanism | Mark |
| :- | :- | :- |
| A card UI inside Claude Code (MCP Apps do not render) | Mods: band, pane, `Input`, `Select`, `Button`, `Svg`, `Code`, in CLI, desktop and VS Code | [D] [T] |
| A structured answer form without leaving the session | MCP elicitation form mode; mods `Input` + `Select` | [D] |
| A page waking a running session | Comments `sendToClaude`; `room.sendToClaudeSession`; live docs; socket post from the local page's process; monitor; `asyncRewake` | [D] |
| Phone answers without a tunnel | Hosted artifact (grades on the page), Remote Control chat, cloud session; mod hooks still run on the machine and can see the record change | [D] [T-prior] |
| Reviews 21 or 180 days later when no session is open | Cloud scheduled tasks reading the record from the repo, pushing to the phone | [D] |
| A hosted page reading the repo's plain-file record | `files` capability (`project: "chan_..."`, a Claude Code project's files), or `mcp` with `host:<server>` in the Claude app | [D] |
| Knowing whether the learner is on the phone | `$CLAUDE_CODE_BRIDGE_SESSION_ID`, mods `session.attach`, `$.session.surfaces`, `CLAUDE_CLIENT_PRESENCE_FILE` | [D] |
| Removing praise even when the model slips | `MessageDisplay` hook (display only) or a mod `ui.render` on `AssistantMessage` | [D] |

Still not possible, as far as the documentation shows: drawing a mod on the phone (Remote Control draws only in the machine's terminal); rendering MCP Apps in any Claude Code surface; a page starting Claude's turn without a viewer gesture ("There is no way for a page to start Claude's turn by itself"); MCP sampling and resource subscriptions in Claude Code; channels outside the CLI. [D]

## 10. What this suggests for the product (for the architecture track)

This section is my synthesis, marked [S] as a whole.

**One record, many doors, one bell.** The repo's `.learning/` files stay the single source of truth. Each surface is a door (chat, mod pane, terminal `learning answer`, local page, hosted page, phone). Every door writes the same event line to `.learning/events.jsonl` (or the hosted `db`, pulled into it). One bell tells the build session: a plugin monitor tailing that file, with the inbox socket and comments `sendToClaude` as bells for the doors that cannot write the file directly.

**The seam lives above the prompt.** In the Claude app's Code tab and the CLI, the learning strip is a mod band: one quiet line in the site's ink and accent, "1 question waiting", a digit hotkey, nothing else. Pressing it opens a pane that looks like a site card (white, 1.5px #DAD8D0 border feel within what the element set allows), with the answer field, confidence and "I don't know". Submitting locks the answer, writes the record, and queues grading for the next idle moment with `$.prompt.submit`. The build never stops. This is what Linear and Raycast do: the command is always one key away and never a modal you did not ask for.

**Timing follows the learning science.** Prediction before a build (generation and pretesting effects, Kapur's productive failure): asked in chat or with `AskUserQuestion` only when the learner is present, triggered by `UserPromptSubmit` recognising a build request. Explain-back after green tests (self-explanation): raised by a `Stop` prompt hook or `TaskCompleted`, posted, not blocking. Debugging drill (Shen and Tamkin's largest gap): raised by `PostToolUseFailure` on a failing test, "what do you think broke?" before Claude looks. Spaced retrieval (Roediger and Karpicke, Bjork's desirable difficulties): cloud scheduled task plus phone push, answered on the hosted page, graded there with `sample` against the rubric fixed in advance. Confidence on every answer (Metcalfe's hypercorrection: confident errors corrected stick best): a `Select` in the pane, an enum in elicitation, a control on the page.

**Away from the desk.** When `idle_prompt` fires or a Remote Control device attaches, the skill posts instead of asks, sends one `PushNotification` with the question's first line, and the hosted page is the door. Its answer comes back through comments `sendToClaude` or the `db` pull at the next checkpoint.

**Accessibility.** Mods draw native controls that follow the app's focus and keyboard rules; the band's digit hotkeys work without a mouse; `Svg` needs `alt`; screen reader mode disables `AskUserQuestion` timeouts; reduced motion should keep the record cells static. The hosted page must keep its own WCAG work since mods do not reach it.

**Other harnesses.** Mods, monitors, channels, artifacts and Remote Control are Claude-only. The cross-harness floor stays: the skill, `learning.py` in a terminal, the local page, chat questions. Everything in this report is an enhancement detected at run time, never a requirement.

## 11. Cheapest experiments, in order

1. **Mod band live render** (10 minutes): `claude --plugin-dir ./lwb-mod` in the CLI, then in the desktop Code tab, with a fake `.learning/inbox.json`. Confirm the band shows, hotkey 1 opens the pane, `/learn` works mid-turn with `immediate: true`. Then add `Input`, `Select` and `$.prompt.submit` and confirm grading is queued until idle.
2. **Inbox socket post from a child process** (15 minutes): in an interactive local session, run a background Bash child that sleeps 30 s then writes one JSON line to `$CLAUDE_CODE_MESSAGING_SOCKET` with the auth line; observe whether a message arrives and its exact framing. The wire format is not documented, so try `{"type":"auth","token":...}` then a text line, and read `--debug` output.
3. **Plugin monitor on `.learning/events.jsonl`** (10 minutes): add `monitors/monitors.json` with `tail -F`, append a line from another terminal, confirm Claude gets a notification while idle, in CLI and in the desktop Code tab.
4. **Comments `sendToClaude` from the phone** (15 minutes): publish `room.html` with `comments: {}`; on the phone, press a "Send my answer to Claude" control; confirm the publishing session (left running with Remote Control) receives it and grades without a typed prompt.
5. **`room.sendToClaudeSession` with `deliver: "send"`** (10 minutes): log `canSendToClaudeSession()` on desktop and on the phone, with and without a conversation open beside the page.
6. **Elicitation form in desktop local and over Remote Control** (20 minutes): extend `experiments/mcp-app/server.py` with a tool that elicits `{answer, confidence, dont_know}`; record where the form appears.
7. **`mcp` capability `host:learning` from a page in the desktop app** (20 minutes): a tiny local MCP server exposing `record_read`; publish a page declaring `{mcp:{servers:[{server:"host:learning",tools:["record_read"]}]}}`; open it in the Claude desktop app.
8. **`Claude Code Remote` connector from a page** (15 minutes): publish a page that calls `listTools()` on that connector and shows whether `send_message` is in the viewer's set.
9. **Cloud scheduled task for reviews** (20 minutes): `create_trigger` daily with `create_new_session_on_fire`, prompt "run learning.py due; if any, write them to the room page db and push", notifications `{push: true}`.
10. **`asyncRewake` SessionStart hook** (15 minutes): a script that waits for a new file in `.learning/answers/` and exits 2 with its path on stderr; confirm Claude wakes while idle.

## Sources

Official Claude Code documentation (fetched 2026-11-07 from the index at https://code.claude.com/docs/llms.txt):
[mods overview](https://code.claude.com/docs/en/plugins/mods/overview.md),
[mods interface](https://code.claude.com/docs/en/plugins/mods/interface.md),
[mods API](https://code.claude.com/docs/en/plugins/mods/api.md),
[mods reference](https://code.claude.com/docs/en/plugins/mods/reference.md),
[mods events](https://code.claude.com/docs/en/plugins/mods/events.md),
[mods gallery](https://code.claude.com/docs/en/plugins/mods/gallery.md),
[mods test](https://code.claude.com/docs/en/plugins/mods/test.md),
[plugin components](https://code.claude.com/docs/en/plugins/components.md),
[plugin manifest](https://code.claude.com/docs/en/plugins/manifest-reference.md),
[hooks](https://code.claude.com/docs/en/hooks.md),
[channels](https://code.claude.com/docs/en/channels.md),
[channels reference](https://code.claude.com/docs/en/channels-reference.md),
[cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging.md),
[env vars](https://code.claude.com/docs/en/env-vars.md),
[artifacts](https://code.claude.com/docs/en/artifacts.md),
[remote control](https://code.claude.com/docs/en/remote-control.md),
[mobile](https://code.claude.com/docs/en/mobile.md),
[desktop](https://code.claude.com/docs/en/desktop.md),
[desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks.md),
[scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks.md),
[routines / cloud scheduled tasks](https://code.claude.com/docs/en/routines.md),
[deep links](https://code.claude.com/docs/en/deep-links.md),
[VS Code](https://code.claude.com/docs/en/vs-code.md),
[MCP](https://code.claude.com/docs/en/mcp.md),
[tools reference](https://code.claude.com/docs/en/tools-reference.md),
[status line](https://code.claude.com/docs/en/statusline.md),
[output styles](https://code.claude.com/docs/en/output-styles.md),
[interactive mode](https://code.claude.com/docs/en/interactive-mode.md),
[skills](https://code.claude.com/docs/en/skills.md),
[Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview.md),
[Agent SDK user input](https://code.claude.com/docs/en/agent-sdk/user-input.md).

Platform type definitions served to this session: `/tmp/claude-0/bundled-skills/2.1.319/efe741960848ef81d2b0e6539b3f3e0b/artifact-capabilities/0.2.96/` (`room.d.ts`, `comments.d.ts`, `artifact.d.ts`, `db.d.ts`, `sample.d.ts`, `mcp.d.ts`, `files.d.ts`, `user.d.ts`, `claude.d.ts`), and the live capability roster from the `artifact-capabilities` skill.

Third party: [MCP Apps rendering request for locally configured servers](https://claudeissues.com/issue/88881-feature-render-mcp-apps-for-locally-configured-mcp-servers-config-file-localhost), [ext-apps issue 671](https://github.com/modelcontextprotocol/ext-apps/issues/671), [MCP Apps guide](https://mcp.so/blog/mcp-apps-guide).

Tests run in this session: probe mod at `/tmp/claude-0/-home-user-explain-pr/074e39f7-08cf-5ec8-b66b-62906beb6d01/scratchpad/lwb-mod/` (`claude plugin validate`, `claude plugin test`, Claude Code 2.1.319); environment check for `CLAUDE_CODE_MESSAGING_SOCKET` and `CLAUDE_CODE_MESSAGING_TOKEN` (both set, socket present with mode `srw-------`). Project test: `experiments/mcp-app/README.md` (Claude Code in the Claude app shows text only).
