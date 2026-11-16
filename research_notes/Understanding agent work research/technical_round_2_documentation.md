# Technical round 2: answers from official documentation (read 16 November 2026)

Reading notes for the report writer:

- Every finding below comes from a page downloaded with curl in this session on 16 Nov 2026 and read from the downloaded file. Nothing here comes from a summarising fetch tool or from memory unless it is under "Gaps".
- Each finding says how the page was read: **full** (every line read), **part** (searched for the relevant passages and read those), or **not opened**.
- Quoted strings are copied from the downloaded pages.
- Most vendor pages carry no date. Where a page has no date I give the highest product version it mentions, or say "undated".
- This round corrects four points in the first pass (`technical_feasibility.md`). They are collected at the end of Part 1 under "Corrections to the first pass".

## Part 1a. Claude Code: lifecycle events, the plan at the end of plan mode, timeouts, context injection, headless runs

### Takeaway
When Claude finishes planning it calls the `ExitPlanMode` tool, and a `PreToolUse` hook on that tool receives the whole plan as Markdown (`tool_input.plan`) plus the plan file path (`tool_input.planFilePath`). The hook runs before the approval prompt is shown, has 600 seconds by default, and fails open on timeout unless `onFailure: "block"` is set. A hook at prompt submission can add context, but there the default timeout is 30 seconds, not 600.

### Cited Findings

Source for everything in this section unless another link is given: [Claude Code hooks reference](https://code.claude.com/docs/en/hooks.md). Undated; the highest version it cites is v2.1.319. Read: **full** (293,498 bytes, 4,347 lines). Lines 1 to 1647 and 1778 to 2267 were read verbatim. For the rest, fenced code examples were skipped and very long table lines were cut at 330 to 900 characters.

**Lifecycle events (33) and what each carries**

- Every event receives the common fields `session_id`, `prompt_id`, `transcript_path`, `cwd`, `scratchpad_dir` (v2.1.257+), `permission_mode`, `effort`, `hook_event_name`, and `agent_id`/`agent_type` when inside a subagent. `permission_mode` is one of `"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"`, `"bypassPermissions"`; "Not all events receive this field." — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- Per-event data, from each event's "input" section — [hooks reference](https://code.claude.com/docs/en/hooks.md):

| Event | When | Event-specific data | Can block? |
|---|---|---|---|
| `SessionStart` | session begins or resumes | `source` (`startup`, `resume`, `clear`, `compact`, `fork`), optional `model`, `agent_type`, `session_title`; on resume also `seconds_since_last_response`, `context_tokens`, `prompt_cache_likely_expired`, `estimated_cache_write_usd` | No |
| `Setup` | `--init-only`, or `--init`/`--maintenance` with `-p` | `trigger` | No |
| `InstructionsLoaded` | a CLAUDE.md or rules file is loaded | `file_path`, `memory_type`, `load_reason`, `globs`, `trigger_file_path`, `parent_file_path` | No |
| `UserPromptSubmit` | prompt submitted, before Claude processes it | `prompt`, optional `session_title` | Yes |
| `UserPromptExpansion` | a typed command expands into a prompt | `expansion_type`, `command_name`, `command_args`, `command_source`, `prompt` | Yes |
| `MessageDisplay` | assistant text streams to screen | `turn_id`, `message_id`, `index`, `final`, `delta` | No (display only) |
| `PreToolUse` | "after Claude creates tool parameters and before processing the tool call" | `tool_name`, `tool_input`, `tool_use_id`; `mcp_server` for MCP tools | Yes |
| `PermissionRequest` | "when Claude Code is about to ask you for permission to use a tool" | `tool_name`, `tool_input`, optional `permission_suggestions` (no `tool_use_id`) | Via `decision.behavior` |
| `PermissionDenied` | auto mode denies a call | `tool_name`, `tool_input`, `tool_use_id`, `reason` | No |
| `PostToolUse` | tool succeeded | `tool_name`, `tool_input`, `tool_response`, optional `duration_ms` | No (tool already ran) |
| `PostToolUseFailure` | tool failed | `tool_name`, `tool_input`, `error`, `is_interrupt`, `duration_ms` | No |
| `PostToolBatch` | a batch of parallel tool calls resolved | `tool_calls` array (each with the serialised `tool_response`) | Yes (stops the loop) |
| `Notification` | Claude Code sends a notification | `message`, optional `title`, `notification_type` | No |
| `SubagentStart` / `SubagentStop` | subagent spawned / finished | `agent_id`, `agent_type`; on stop also `stop_hook_active`, `agent_transcript_path`, `last_assistant_message` | Stop only |
| `TaskCreated` / `TaskCompleted` | task created / marked complete | `task_id`, `task_subject`, optional `task_description`, `teammate_name` | Yes |
| `Stop` | main agent finished responding | `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons` | Yes (continues the turn; cap of 8 consecutive continuations) |
| `StopFailure` | turn ended on an API error | `error`, `error_details`, `last_assistant_message` | No |
| `TeammateIdle` | agent-team teammate about to idle | `teammate_name` | Yes |
| `ConfigChange` | a settings or skill file changed | `source`, optional `file_path` | Yes (not policy settings) |
| `CwdChanged` | working directory changed | `old_cwd`, `new_cwd` | No |
| `DirectoryAdded` | `/add-dir` or SDK request | `directory`, `source` | No |
| `FileChanged` | a watched file changed on disk, "no matter what changed the file" | `file_path`, `event` (`change`, `add`, `unlink`) | No |
| `WorktreeCreate` / `WorktreeRemove` | worktree created / removed | `name` / `worktree_path` | Non-zero exit fails it |
| `PreCompact` / `PostCompact` | before / after compaction | `trigger`, `custom_instructions` / `compact_summary` | Pre only |
| `PreModelSwitch` / `PostModelSwitch` | before / after a model change | `from_model`, `to_model`, `requested_model`, `source`, cost fields | Pre only |
| `Elicitation` / `ElicitationResult` | MCP server asks for user input / user answered | `mcp_server_name`, `message`, `mode`, `url`, `requested_schema` / `action`, `content` | Yes |
| `SessionEnd` | session terminates | `reason` | No |

- `PreToolUse` shows the exact edit before it is applied: for `Write`, `file_path` and `content`; for `Edit`, `file_path`, `old_string`, `new_string`, `replace_all`. "`tool_input.file_path` is always absolute". — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- Edits made through Bash are visible only after the fact and only approximately: `PostToolUse` can carry `tool_response.bashEditDiff` with `changedFiles` (at most 200). "The list is best effort and in public beta... Use the list to find what to review, not to enforce a policy." (v2.1.269+). — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- `Edit|Write` matchers miss Bash writes: "Claude Code doesn't run a `PostToolUse` hook matching `Edit|Write` when a `Bash` command or a process outside Claude Code rewrites the same file." The docs suggest a matcher-less `PostToolUse` hook that runs `git status --porcelain`. — [hooks reference](https://code.claude.com/docs/en/hooks.md)

**The moment a plan is presented**

- The event is `PreToolUse` with `tool_name` `ExitPlanMode`. The docs: "Presents a plan and asks the user to approve it before Claude leaves plan mode. Claude writes the plan to a file on disk before calling the tool, so the literal `tool_input` from the model is typically empty. Claude Code injects the plan content and file path before passing the input to hooks." — [hooks reference, ExitPlanMode](https://code.claude.com/docs/en/hooks.md)
- Data carried: `plan` (string, "Plan content in Markdown. Injected from the plan file on disk"), `planFilePath` (string, "Path to the plan file. Injected"), and `allowedPrompts` ("Deprecated. Claude Code accepts the field but ignores it"). — [same](https://code.claude.com/docs/en/hooks.md)
- After approval, `PostToolUse` carries the approved plan: "`tool_response` is an object with `plan` and `filePath` fields holding the approved plan, plus internal status flags. Read `tool_response.plan` for the plan content rather than re-reading the file from disk." — [same](https://code.claude.com/docs/en/hooks.md)
- The hook runs before the approval prompt. Three statements establish the order: `PreToolUse` "Runs after Claude creates tool parameters and before processing the tool call"; `PermissionRequest` "Runs when Claude Code is about to ask you for permission to use a tool"; and "PreToolUse hooks run before every tool call, whether or not it needs permission." — [same](https://code.claude.com/docs/en/hooks.md)
- A hook can answer the plan prompt itself, so the developer never sees the built-in dialog: "`AskUserQuestion` and `ExitPlanMode` require user interaction... A `PreToolUse` hook satisfies that requirement when it does the following: 1. Reads the tool's input from stdin 2. Collects the answer through your own UI 3. Returns `permissionDecision: "allow"` together with `updatedInput` that holds the answer, so the tool runs without prompting. Returning `"allow"` alone is not sufficient for these tools." — [same](https://code.claude.com/docs/en/hooks.md)
- Confirmed from the permissions page: "If the hook answers `ExitPlanMode` with `"allow"` and `updatedInput`, that tool still runs without a prompt." In plan mode a hook's `"allow"` has no effect on any other non-read-only call. — [Permissions, "Hook approvals in plan mode"](https://code.claude.com/docs/en/permissions.md) (undated; read: **part**)
- What the developer sees when no hook intervenes: "When the plan is ready, Claude presents it and asks how to proceed." Options are approve into auto mode, approve with manual edit approval, or "No, keep planning". "Press `Ctrl+G` to open the proposed plan in your default text editor and edit it directly before Claude proceeds." — [Permission modes](https://code.claude.com/docs/en/permission-modes.md) (undated; read: **part**)
- The signal that fires only after the prompt is on screen is different: a `Notification` hook with `permission_prompt` runs "only after the prompt has waited about six seconds". — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- Plan mode is not a hard block in one case: "In interactive terminal sessions with bypass permissions available, Claude Code also doesn't enforce plan mode's blocks. Claude is still instructed to plan without editing, but a file edit or shell command it attempts during planning runs without prompting." — [Permission modes](https://code.claude.com/docs/en/permission-modes.md)

**How long a hook may take**

- Defaults: "600 for `command`, `http`, and `mcp_tool`; 30 for `prompt`; 60 for `agent`. Claude Code lowers the `command`, `http`, and `mcp_tool` default to 30 on `UserPromptSubmit`, `PreModelSwitch`, and `PostModelSwitch`, and to 10 on `MessageDisplay`. `SessionEnd` hooks share a 1.5-second budget". The `timeout` field (seconds) overrides it per hook. — [hooks reference, common fields](https://code.claude.com/docs/en/hooks.md)
- A timeout does not block: "On `PreToolUse`, a timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call... The call continues through the normal permission flow, so don't count on a stalled hook to act as a gate. To block the call when a `command` or `http` hook times out, set `onFailure: "block"`" (v2.1.295+). — [same](https://code.claude.com/docs/en/hooks.md)
- `onFailure: "block"` has no effect on `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle`, or on background (`async`) hooks. — [same](https://code.claude.com/docs/en/hooks.md)
- Hooks cannot draw in the terminal: "command hooks run in their own session without a controlling terminal. The hook process and any child processes can't open `/dev/tty`". To show the user a message a hook returns `systemMessage`. — [same](https://code.claude.com/docs/en/hooks.md)

**Adding context at prompt submission**

- Yes. "There are two ways to add context to the conversation on exit code 0: Plain text stdout... JSON with `additionalContext`". "Neither channel produces a visible transcript entry." — [hooks reference, UserPromptSubmit](https://code.claude.com/docs/en/hooks.md)
- It cannot change the prompt: "`UserPromptSubmit`: can't replace the prompt; it only injects `additionalContext` alongside it". It can block it (`decision: "block"` or exit 2). — [same](https://code.claude.com/docs/en/hooks.md)
- Limits: "`UserPromptSubmit` hooks have a default timeout of 30 seconds... a `UserPromptSubmit` command, HTTP, or MCP tool hook that reaches its timeout is canceled and its output, including any `additionalContext`, is discarded. The prompt still reaches Claude without that context." Each `additionalContext` string is capped at 10,000 characters; longer text is saved to a file and Claude gets a 2,000-character preview. — [same](https://code.claude.com/docs/en/hooks.md)
- The event also fires on turns the user did not type: scheduled tasks and `/loop` iterations, a background subagent reporting back, and messages from another session. — [same](https://code.claude.com/docs/en/hooks.md)
- Wording advice: "Write the text as factual statements rather than imperative system instructions... Text framed as out-of-band system commands can trigger Claude's prompt-injection defenses". — [same](https://code.claude.com/docs/en/hooks.md)

**Headless runs (`claude -p`)**

- Hooks fire everywhere: "Claude Code fires the same hook events wherever it runs: sessions in the terminal, IDE extensions, the Desktop app, and cloud sessions." Cloud sessions "don't read your local `~/.claude/settings.json`". — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- No trust dialog: in a "`-p` or SDK session: Claude Code never shows the dialog and treats the folder as trusted, so hooks committed in a repository's `.claude/settings.json` run in a folder you've never trusted". — [hooks reference, Workspace trust](https://code.claude.com/docs/en/hooks.md)
- `--bare` removes hooks: it skips "auto-discovery of hooks, skills, custom commands, subagents, installed plugins, MCP servers, auto memory, and CLAUDE.md"; "Hooks still don't run in bare mode when you pass them with `--settings`"; "`--bare` is the recommended mode for scripted and SDK calls, and will become the default for `-p` in a future release." — [Run Claude Code programmatically](https://code.claude.com/docs/en/headless.md) (undated; cites v2.1.302; read: **part**)
- The plan step only exists in `-p` if something can answer it: "In non-interactive mode with the `-p` flag, Claude Code offers them [`AskUserQuestion` and `ExitPlanMode`] only when the run has a permission host to receive the prompt, such as an Agent SDK `canUseTool` callback." — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- A pause-and-resume mechanism exists only in `-p`: a `PreToolUse` hook may return `"defer"`; the turn ends with `stop_reason: "tool_deferred"` and a `deferred_tool_use` object (`id`, `name`, `input`); the caller later runs `claude -p --resume <session-id>` and the hook fires again. "There is no timeout or retry limit." It works "only when Claude makes a single tool call in the turn". — [same](https://code.claude.com/docs/en/hooks.md)
- Plan mode holds in headless: "Plan mode keeps its blocks wherever Claude Code runs without an interactive terminal, including non-interactive runs with `-p`, Agent SDK sessions, and conversations in the VS Code extension's chat panel." — [Permission modes](https://code.claude.com/docs/en/permission-modes.md)
- Other headless differences: async hooks still running at teardown are killed (outcome `cancelled`); `terminalSequence` is ignored; `MessageDisplay` runs once per message; in a Manual-mode `-p` run "a call that needs approval is denied unless something approves it, such as a `PermissionRequest` hook or a `--permission-prompt-tool`". — [hooks reference](https://code.claude.com/docs/en/hooks.md); [headless](https://code.claude.com/docs/en/headless.md)

### Inferences
- The plan hook is a real "before the first edit" point: the tool holds the complete intended change as text, the developer has not yet been asked to approve it, and the hook may hold the call for up to its timeout while it shows its own page. This is what Plannotator does (first pass).
- To ask for a prediction before the developer reads the agent's plan, the tool must intercept at `PreToolUse` on `ExitPlanMode` and present its own UI first. If it waits for the built-in dialog, the plan is already on screen.
- A prediction step at `UserPromptSubmit` must finish in 30 seconds or raise `timeout` explicitly, and it will also fire on scheduled and subagent-triggered turns, so the hook has to tell those apart.
- For "what actually changed", a matcher-less `PostToolUse` or `Stop` hook running git is more complete than watching `Edit|Write`, because Bash edits bypass those matchers.

### Gaps
- The documentation does not say whether Claude's plan text has already streamed into the conversation as ordinary assistant text before `ExitPlanMode` is called. It says only that the plan is written to a file first and that the tool "presents" it. Whether a developer could have read it early is not answered.
- The shape of `updatedInput` that a hook must return to approve or reject `ExitPlanMode` is not shown (the page gives the full example only for `AskUserQuestion`).
- No statement on the stability of hook payload schemas across versions was found.

## Part 1b. Other agents: is there a documented plan step, and can a third-party tool read the plan before the first edit?

### Takeaway
Every agent checked documents a plan step. Outside Claude Code, a documented way for a third party to read the plan before the first edit exists for Codex (as a stream item through the app-server protocol or `codex exec --json`, not through a hook) and, by naming only, for Devin CLI (an `exit_plan_mode` tool that hooks can match). For Cursor, Copilot, Antigravity and Cline the documentation describes the plan step but no interception point for it.

### Cited Findings

**OpenAI Codex CLI** (docs at learn.chatgpt.com; undated; no version on the pages)
- Plan step: "`/plan` — Switch to plan mode and optionally send a prompt. Ask Codex to propose an execution plan before implementation work starts." After planning the user can "Choose **Yes, clear context and implement** to start a fresh chat with the complete plan." — [Slash commands in Codex CLI](https://learn.chatgpt.com/docs/developer-commands.md?surface=cli) (read: **part**)
- The plan as data, through the app-server protocol: item type "`plan` - `{id, text}` containing proposed plan text in plan mode. Treat the final `plan` item from `item/completed` as authoritative."; "`item/plan/delta` - streams proposed plan text"; and "`turn/plan/updated` - `{ turnId, explanation?, plan }` whenever the agent shares or changes its plan; each `plan` entry is `{ step, status }`". — [Codex App Server](https://learn.chatgpt.com/docs/app-server.md) (read: **part**)
- The plan in headless output: with `codex exec --json`, "`stdout` becomes a JSON Lines (JSONL) stream... Event types include `thread.started`, `turn.started`, `turn.completed`, `turn.failed`, `item.*`, and `error`. Item types include agent messages, reasoning, command executions, file changes, MCP tool calls, web searches, and plan updates." — [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode.md) (read: **part**)
- Hooks see the mode and the checklist tool, not a "plan ready" event. Hook input "also include `permission_mode`, which describes the current permission mode as `default`, `acceptEdits`, `plan`, `dontAsk`, or `bypassPermissions`." Tool coverage lists "Other local function tools — Match the function tool name, such as `update_plan`." The 14 events contain no plan event. — [Codex hooks](https://learn.chatgpt.com/docs/hooks.md) (read: **part**: headings, common fields, tool coverage, PreToolUse, UserPromptSubmit)
- Prompt-time context: on `UserPromptSubmit`, "Plain text on `stdout` is added as extra developer context" and `additionalContext` likewise; the prompt can be blocked. Timeout: "If `timeout` is omitted, Codex uses `600` seconds for most hooks." Fail-open: "A `PreToolUse` error, timeout, or malformed response can let the tool run." — [Codex hooks](https://learn.chatgpt.com/docs/hooks.md)

**Cursor** (undated)
- Plan step: "Plan Mode creates detailed implementation plans before writing any code. Agent researches your codebase, asks clarifying questions, and generates a reviewable plan you can edit before building." Steps end with "You review and edit the plan through chat or markdown files" and "Click to build the plan when ready". "Plans are saved by default in your home directory. Click "Save to workspace" to move it to your workspace". — [Cursor Plan Mode](https://cursor.com/docs/agent/plan-mode.md) (read: **full**, 50 lines)
- CLI: Plan mode is reachable with "Shift+Tab, `/plan`, `--plan`, `--mode=plan`"; a "print mode" exists "for non-interactive scenarios like scripts, CI pipelines, or automation". — [Cursor CLI overview](https://cursor.com/docs/cli/overview.md) (read: **part**)
- Hooks: the word "plan" does not occur in the hooks page as a feature (the only match is "Enterprise plans"). The common hook input has no mode field (`conversation_id`, `generation_id`, `model`, `hook_event_name`, `cursor_version`, `workspace_roots`, `user_email`, `transcript_path`). `preToolUse` "fires for all tool types (Shell, Read, Write, MCP, Task, etc.)" with `tool_name`, `tool_input`; `"ask"` "is accepted by the schema but not enforced for `preToolUse` today". — [Cursor hooks](https://cursor.com/docs/hooks.md) (read: **part**: headings, common schema, preToolUse, beforeSubmitPrompt, cloud section, configuration options)
- `beforeSubmitPrompt` can stop a prompt (`continue: false`) but its documented output has no context field (only `continue` and `user_message`). Timeout default is "platform default" (no number given). Hooks fail open unless `failClosed: true`. — [Cursor hooks](https://cursor.com/docs/hooks.md)
- Cloud agents: "Cloud agents sometimes begin in a read-only environment for early exploratory turns. Hooks do not run during those turns." `sessionStart` and `sessionEnd` do not run in cloud agents. — [Cursor hooks](https://cursor.com/docs/hooks.md)

**GitHub Copilot CLI and Copilot in the cloud** (undated; the cloud page carries a note dated "October 28, 2026")
- CLI plan step: "there is also a **plan mode** in which Copilot will build a structured implementation plan for a task you want to complete... In plan mode, Copilot analyzes your request, asks clarifying questions to understand scope and requirements, and builds a plan before writing any code." — [About Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli) (read: **part**); "Press Shift+Tab to cycle in and out of plan mode." — [Using Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview) (read: **part**)
- Hooks reference: the word "plan" does not occur anywhere in the page. Default hook timeout is 30 seconds ("`timeoutSec` — Timeout in seconds. Default: `30`."). "Command hook **timeouts are always fail-open, even for `preToolUse` and admin-deployed policy hooks**". For `userPromptSubmitted`, "Command and HTTP config-file `userPromptSubmitted` hooks have their output dropped". `sessionStart` can add `additionalContext`. — [Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-configuration) (read: **part**; whole page searched)
- Cloud: "Copilot can research a repository, plan changes, and implement them in the background... You can review the proposed changes and ask for refinements before creating a pull request". No approval pause before coding is described. — [About Copilot in the cloud](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent) (read: **part**)
- Cloud execution: "Fully non-interactive. The agent runs with all tool permissions pre-granted, so no permission dialogs are shown and no notifications are surfaced to a user." Filesystem "Ephemeral. Files written by hooks... are discarded when the job ends." Network: "By default only GitHub and Copilot hostnames are reachable". "`COPILOT_AGENT_PROMPT` holds the prompt the job was invoked with." Only `.github/hooks/*.json` in the repository is read. — [Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-configuration)

**Google Antigravity CLI** (docs at antigravity.google; undated)
- Status of Gemini CLI, exact wording of the banner: "Unpaid tier and Google One users: Gemini CLI was replaced by Antigravity CLI on June 18th, 2026." The same page is marked "Last updated: Apr 10, 2026". — [Gemini CLI hooks reference](https://geminicli.com/docs/hooks/reference/) (read: **part**, banner only)
- Plan step: "The `/plan` command facilitates structured planning, codebase exploration, and requirements discovery before jumping directly into code execution." It "drafts a structured Implementation Plan artifact" and "You retain full control to leave inline comments, request adjustments, or click **Proceed** to begin implementation." Available on "Antigravity App, Antigravity CLI". — [Plan (/plan)](https://antigravity.google/docs/plan.md) (read: **part**, first 70 lines)
- "The agent requests your review on the implementation plan before making the changes needed to complete your task, whatever your artifact review policy is." (page marked "Available on: Antigravity App, Antigravity IDE"). — [Implementation plan](https://antigravity.google/docs/implementation-plan.md) (read: **full**)
- Hooks: six events, `SessionStart`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`. No plan event. Every hook receives `artifactDirectoryPath` ("The absolute path to the directory containing all conversation artifacts and screenshots"), `transcriptPath`, `conversationId`, `workspacePaths`, `modelName`, `lastUserInput`. `PreToolUse` receives `toolCall.name` and `toolCall.args` and returns a `decision` (`allow`, `auto_approve`, `deny`, `ask`, `force_ask`, `deny_unless_prior_grant`). The file-creation tool `write_to_file` has arguments `TargetFile`, `Overwrite`, `CodeContent`, `Description`, `IsArtifact` (optional), `ArtifactMetadata` (optional). Default timeout: "Timeout in seconds. Defaults to `30`." — [Antigravity hooks](https://antigravity.google/docs/hooks.md) (read: **part**, about the first 260 non-blank lines plus the PreInvocation section)
- Context before the model is called: `PreInvocation` "Fires before the model is called" and may return `injectSteps` (a `systemMessage`, `userMessage`, `ephemeralMessage` or `errorMessage`) and `terminationBehavior: "terminate"`. — [Antigravity hooks](https://antigravity.google/docs/hooks.md)
- Headless: `agy -p` with `--output-format json` or `stream-json` (NDJSON events); the `init` event lists tools and `permission_mode` ("`request-review` by default"). — [Headless mode](https://antigravity.google/docs/cli/headless.md) (read: **part**)

**Devin CLI / Devin Local (formerly Windsurf)** (docs.devin.ai; undated)
- Plan step: "`/plan` — Switch to Plan mode (read-only planning)". Plan mode: "Planning only — the agent proposes changes without making them. Read-only tool access ensures no code is modified." Its profile has "Read-only tools (grep, glob, read, todo, ask_user_question, exit_plan_mode)". — [Devin CLI commands and flags](https://docs.devin.ai/cli/reference/commands.md) (read: **part**)
- Hooks can match the plan-exit tool by name: the lifecycle hooks page lists tool names by category, including "Planning and tasks: `todo_write`, `exit_plan_mode`". `PreToolUse` receives `tool_input` ("Arguments passed to the tool"). `UserPromptSubmit` and `SessionStart` can return `additionalContext`. — [Devin CLI lifecycle hooks](https://docs.devin.ai/cli/extensibility/hooks/lifecycle-hooks.md) (read: **part**)
- Headless: "`--print [PROMPT]` / `-p` — Print response and exit (non-interactive mode)"; it "cannot show the workspace trust prompt, so it fails in an untrusted directory". — [Devin CLI commands and flags](https://docs.devin.ai/cli/reference/commands.md)

**Cline** (docs.cline.bot; undated)
- Plan step: "Plan & Act modes separate thinking from doing. Plan mode lets you explore and strategize without changing files." In Plan mode "Cline can read your codebase, run searches, and discuss strategy, but cannot modify any files or execute commands." The move to editing is a manual mode switch: "When confident in the plan, switch to Act mode". "The conversation history carries over when you switch modes." — [Plan & Act Mode](https://docs.cline.bot/core-workflows/plan-and-act.md) (read: **part**, first 60 lines)
- Headless: "Headless is triggered when using flags like `--json`, when stdin is piped, or when output is redirected"; "Mode selection also works in headless runs" (a "plan-first" example follows). — [Cline CLI overview](https://docs.cline.bot/usage/cli-overview.md) (read: **part**)
- Plugin hooks are `beforeRun`, `afterRun`, `beforeModel`, `afterModel`, `beforeTool`, `afterTool`, `onEvent`; the page has no plan or mode-switch hook. — [Cline SDK plugins](https://docs.cline.bot/sdk/plugins.md) (read: **part**)

**Summary table (documentation only)**

| Agent | Documented plan step | Documented way for a third party to read the plan before the first edit |
|---|---|---|
| Claude Code | Plan mode, `ExitPlanMode` | Yes: `PreToolUse` hook on `ExitPlanMode` gets `plan` and `planFilePath` |
| Codex CLI | `/plan` | Yes, but not by hook: `plan` item via app-server, "plan updates" via `codex exec --json`. Hooks see only `permission_mode: plan` and `update_plan` calls |
| Cursor | Plan Mode, plan saved as a Markdown file in the home directory | Not documented. No plan hook, no mode field in hook input |
| Copilot CLI | Plan mode (Shift+Tab) | Not documented. "plan" absent from hooks reference |
| Copilot in the cloud | "plan changes" described, no approval pause described | Not documented |
| Antigravity CLI | `/plan`, Implementation Plan artifact, Proceed | Not documented as such. Hooks get `artifactDirectoryPath` and can match `write_to_file` (which has `IsArtifact`) |
| Devin CLI | `/plan`, `exit_plan_mode` tool | Partly: `exit_plan_mode` is a matchable tool name; its arguments are not documented |
| Cline | Plan mode, manual switch to Act | Not documented |

### Inferences
- Only Claude Code documents both halves: a plan event and the plan text in its payload. Codex documents the plan text but on a different surface (a protocol the tool would have to host or a JSONL stream it would have to launch), which suits a wrapper, not a hook.
- For Antigravity and Cursor a workable but undocumented route is to watch the place plans are written (Antigravity's artifact directory, given to every hook; Cursor's plan files in the home directory or `.cursor/plans`). Both depend on file layouts the vendors do not promise.
- For Devin CLI, a `PreToolUse` hook on `exit_plan_mode` is the obvious analogue of the Claude Code route. Since Devin CLI reads Claude Code hook files (first pass), one hook definition might serve both, but the tool name and payload differ and Devin's payload for this tool is undocumented.
- For Cline and Copilot there is no plan object at all in the documentation; the fallback is to hold the first write tool call.

### Gaps
- Codex: the hooks page does not show the `tool_input` of `update_plan`, and does not say whether `PreToolUse` fires for anything when a plan-mode plan is finished. Whether `codex exec` can run in plan mode is not stated on the pages read.
- Cursor: where the plan file lives precisely, its filename, and whether writing it triggers `preToolUse` or `afterFileEdit` are not documented. The help page linked from Plan Mode (`cursor.com/help/ai-features/plan-mode.md`) was not opened.
- Copilot CLI: no page read describes a plan file, a plan tool name, or a plan approval event. A dedicated plan-mode page, if one exists, was not found.
- Antigravity: whether the Implementation Plan is written through `write_to_file` with `IsArtifact`, and the plan's filename inside `artifactDirectoryPath`, are not stated. The Implementation Plan page lists only App and IDE under "Available on", while the `/plan` page lists App and CLI; the CLI review flow for plans was read only in the general artifacts page.
- Devin: the arguments of `exit_plan_mode` are not documented. Devin Desktop ("Devin Local") plan behaviour was not read separately; the first pass found it shares the CLI harness.
- Cline: whether a plugin can observe the Plan-to-Act switch is not documented.

## Part 1c. MCP Apps: which hosts are documented as supporting it

### Takeaway
Cursor and VS Code (as an experimental feature) document MCP Apps support themselves. Claude Code's own documentation describes MCP Apps UI resources as something "for a host application to render" and hides them, with no statement that Claude Code renders them. Codex's MCP page does not mention MCP Apps.

### Cited Findings
- Official host list: "MCP Apps are currently supported by Claude, Claude Desktop, VS Code GitHub Copilot, Microsoft 365 Copilot, Goose, Postman, MCPJam, and Archestra.AI." Also: "Host support varies by client." — [MCP Apps overview](https://modelcontextprotocol.io/extensions/apps/overview.md) (undated; read: **part**, client-support section)
- The client matrix page lists 17 clients (including Claude Code, Cursor, ChatGPT, VS Code GitHub Copilot) but the MCP Apps column is empty in the page source for every client except MCP Inspector ("Partial"). The cells are blank in the source, so the first pass's "marks did not survive the fetch" was not a fetch problem. The page says: "This list is maintained by the community." — [Extension support matrix](https://modelcontextprotocol.io/extensions/client-matrix.md) (undated; read: **full**, 61 lines)
- **Cursor: supported.** Feature table row "**Apps (extension)** | Supported | Interactive UI views returned by MCP tools", and "Cursor supports the MCP Apps extension. MCP tools can return interactive UI along with standard tool output. MCP Apps follow progressive enhancement. If a host cannot render app UI, the same tool still works through normal MCP responses." Elicitation is also "Supported". — [Cursor MCP](https://cursor.com/docs/mcp.md) (undated; read: **part**)
- **VS Code Copilot: experimental.** "**Interactive results (Experimental):** MCP Apps display forms, visualizations, or other controls alongside a tool result." — [VS Code, MCP servers](https://github.com/microsoft/vscode-docs/blob/main/docs/agent-customization/mcp-servers.md) (source file of code.visualstudio.com/docs/agent-customization/mcp-servers; "DateApproved: 11/11/2026"; read: **part**)
- **Claude Code: not documented as rendering.** "MCP Apps UI resources are entries with a `ui://` URI or the `text/html;profile=mcp-app` media type: pages for a host application to render rather than content for Claude to read. They don't appear in the `@` suggestions or in the resource list tool's results, and a server that offers only UI resources shows an empty resource list. Reading a UI resource by its URI still works." — [Claude Code MCP](https://code.claude.com/docs/en/mcp.md) (undated; read: **part**; this is the only match for "MCP Apps", "ui://" in the 157 KB page)
- Claude Code does support MCP elicitation (form and URL modes), with `Elicitation` and `ElicitationResult` hooks. — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- **Codex: not mentioned.** The Codex MCP page contains no occurrence of "MCP App", "ui://", "elicit", "interactive" or "widget". — [Codex, Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp.md) (undated; read: **part**, keyword search of the whole page)
- Antigravity MCP page: no occurrence of "MCP App", "ui://" or "elicit". Cline MCP overview: none. Devin CLI MCP overview: none. — [Antigravity MCP](https://antigravity.google/docs/mcp.md); [Cline MCP](https://docs.cline.bot/mcp/mcp-overview.md); [Devin CLI MCP](https://docs.devin.ai/cli/extensibility/mcp/overview.md) (read: **part**, keyword search)
- A third-party server that already relies on this: LikeC4's `render-view` tool "Renders an existing saved view as an interactive diagram (pan/zoom/fit) inline in chat, for hosts that support MCP Apps". — [LikeC4 AI tools](https://likec4.dev/tooling/ai-tools/) (undated; read: **part**)

### Inferences
- An in-conversation diagram through MCP Apps would reach Cursor, VS Code Copilot (experimental) and the Claude chat apps, but not the terminal agents. In Claude Code and Codex the tool needs another surface (a local web page opened by a hook, as Plannotator does).
- Because MCP Apps "follow progressive enhancement", one MCP tool can return a text result everywhere and a diagram where the host renders it.

### Gaps
- No Claude Code page read states outright that Claude Code does not render MCP Apps; the conclusion rests on the wording above and on its absence from the official host list.
- ChatGPT desktop and the Codex IDE extension were not checked separately from the Codex MCP page.
- The MCP Apps specification version and date were not re-read in this round.

## Part 1d. Claude Agent SDK: receiving the plan or the list of files before edits begin

### Takeaway
There is no documented SDK call that returns the list of files the agent intends to change. The plan itself is reachable the same way as in Claude Code, through a `PreToolUse` hook callback on `ExitPlanMode`; the SDK's own typed input for that tool does not include the plan, while its typed output does.

### Cited Findings
- SDK hooks are the same events as callbacks: the SDK hooks page lists `PreToolUse` as "Tool call request (can block or modify)" and shows callbacks reading `input_data["tool_input"]`. — [Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks.md) (undated; read: **part**)
- SDK callback timeouts fail closed, unlike command hooks: "`PreToolUse`: Claude Code blocks the tool call" when a callback exceeds its timeout; on `UserPromptSubmit` "Claude Code blocks the prompt with a message naming the hook and the timeout". Defaults: "600 seconds for most events, 30 seconds for `UserPromptSubmit`". — [Agent SDK hooks, Hook timeout](https://code.claude.com/docs/en/agent-sdk/hooks.md)
- Typed tool shapes: `ExitPlanModeInput` contains only the deprecated `allowedPrompts` plus an open index signature; `ExitPlanModeOutput = { plan: string | null; isAgent: boolean; filePath?: string; hasTaskTool?: boolean; planWasEdited?: boolean; awaitingLeaderApproval?: boolean; requestId?: string; }`, "Returns the plan state after exiting plan mode." — [Agent SDK reference, TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript.md) (undated; read: **part**)
- The plan content is injected for hooks: "Claude Code injects the plan content and file path before passing the input to hooks." — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- A `canUseTool` callback counts as the permission host that makes `ExitPlanMode` available in non-interactive runs. — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- In SDK plan mode each attempted edit reaches the application one at a time: "During planning, edits made with Claude's file tools outside protected paths reach your `canUseTool` callback, even when an allow rule matches or a `PreToolUse` hook returns `allow`." — [Agent SDK permissions, Plan mode](https://code.claude.com/docs/en/agent-sdk/permissions.md) (undated; read: **part**)
- `planModeInstructions` option: "Custom workflow instructions for plan mode. When `permissionMode` is `'plan'`, this string replaces the default plan-mode workflow body. The CLI still wraps it with the read-only enforcement preamble and the ExitPlanMode protocol footer". — [Agent SDK reference, TypeScript](https://code.claude.com/docs/en/agent-sdk/typescript.md)
- File checkpointing is after the fact: it "tracks file modifications made through the Write, Edit, and NotebookEdit tools" and "creates backups of files before modifying them"; it does not undo Bash edits and "Subagent edits aren't tracked". — [File checkpointing](https://code.claude.com/docs/en/agent-sdk/file-checkpointing.md) (undated; read: **part**)

### Inferences
- An SDK-hosted version of the tool has a stronger gate than a command hook, because SDK callback timeouts block instead of passing.
- `planModeInstructions` is a documented way to ask the agent to put a machine-readable list of intended files into its plan. The list would be the model's statement, not a computed fact, and would need checking against the actual diff.

### Gaps
- The SDK user-input page (`agent-sdk/user-input.md`) contains no mention of `ExitPlanMode`; whether `canUseTool` receives the injected `plan` and `planFilePath` as hooks do is not stated.
- No documented structured "files to be changed" field exists anywhere in the pages read.

## Corrections to the first pass (from Parts 1a to 1d)
- `UserPromptSubmit` timeout in Claude Code is 30 seconds by default, not 600. — [hooks reference](https://code.claude.com/docs/en/hooks.md)
- The MCP client matrix cells are empty in the page itself. Cursor documents MCP Apps as "Supported"; VS Code documents it as "Experimental". — [client matrix](https://modelcontextprotocol.io/extensions/client-matrix.md); [Cursor MCP](https://cursor.com/docs/mcp.md)
- Codex plan mode and the `codex exec --json` event stream are confirmed in official documentation (the first pass had only secondary sources). The item type names `command_execution` and `agent_message` appear in the official sample; `file_change` and `todo_list` were not seen verbatim in the part read, which says "file changes" and "plan updates". — [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode.md)
- The Gemini CLI banner is narrower than "replaced": it addresses "Unpaid tier and Google One users". — [Gemini CLI hooks reference](https://geminicli.com/docs/hooks/reference/)

## Part 2a. Infrastructure tools: what they report before a change is applied

### Takeaway
Terraform gives exact, documented counts before apply, in two forms: a one-line `change_summary` message (`add`, `change`, `remove`) from `terraform plan -json`, and a per-resource `actions` list in `terraform show -json` from which create, update, replace and delete counts can be derived. `kubectl diff` and `cdk diff` document only text diffs and exit codes; the documented JSON shape of `pulumi preview --json` was not found.

### Cited Findings

**Terraform** (docs for v1.17.x, the version the website serves; source files read from the HashiCorp docs repository)
- `terraform plan -json` streams messages; at the end: "Terraform outputs a change summary when a plan or apply operation completes. Both message types include a `changes` object, which has the following keys: `add`: count of resources to be created (including as part of replacement); `change`: count of resources to be changed in-place; `remove`: count of resources to be destroyed (including as part of replacement); `operation`: one of `plan`, `apply`, or `destroy`". The message has `"type": "change_summary"`. — [Machine-readable UI](https://developer.hashicorp.com/terraform/internals/machine-readable-ui) ([source, v1.17.x](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/internals/machine-readable-ui.mdx); read: **part**)
- Per resource, the same stream emits a `planned_change` message whose `change.action` is one of "`noop`, `create`, `read`, `update`, `replace`, `delete`, `move`, `import`". — [same](https://developer.hashicorp.com/terraform/internals/machine-readable-ui)
- `terraform show -json <planfile>` gives `resource_changes`, each with a `change` object. "Valid actions values are: `["no-op"]`, `["create"]`, `["read"]`, `["update"]`, `["delete", "create"]`, `["create", "delete"]`, `["delete"]`. The two "replace" actions are represented in this way to allow callers to e.g. just scan the list for "delete" to recognize all three situations where the object will be deleted". Also `before`, `after`, `after_unknown`, `replace_paths`, and `action_reason` (for example `"replace_because_tainted"`). `format_version` is `"1.0"`. — [JSON output format](https://developer.hashicorp.com/terraform/internals/json-format) ([source, v1.17.x](https://github.com/hashicorp/web-unified-docs/blob/main/content/terraform/v1.17.x/docs/internals/json-format.mdx); read: **part**)
- Note on counting: in `change_summary` a replacement adds one to both `add` and `remove`; there is no separate replace count there. Replace is separate only in `planned_change.action` and in the `actions` pair. — both pages above

**Pulumi** (page shows CLI v3.276.0)
- Flags: "`-j, --json` Serialize the preview diffs, operations, and overall output as JSON. Set PULUMI_ENABLE_STREAMING_JSON_PREVIEW to stream JSON events instead."; "`--expect-no-changes` Return an error if any changes are proposed by this preview"; "`--diff` Display operation as a rich diff"; "`--show-replacement-steps` Show detailed resource replacement creates and deletes instead of a single step"; "`--save-plan string` [PREVIEW] Save the operations proposed by the preview to a plan file". — [pulumi preview](https://www.pulumi.com/docs/iac/cli/commands/pulumi_preview/) (read: **part**, options list)
- "The result of previews can be saved to an update plan, this can then be used during a later update to constrain the update only to the operations that were planned." — [Update plans](https://www.pulumi.com/docs/iac/operations/stack-management/update-plans/) (read: **part**)

**AWS CDK** (CDK v2 developer guide; undated)
- "`cdk diff` Perform a diff to see infrastructure changes between AWS CDK stacks." `--method`: "`auto` – Default. Creates an AWS CloudFormation change set to display accurate replacement information... `template` – Compares CloudFormation templates directly. Faster, but less accurate. Any change detected to properties that require resource replacement is displayed as a resource replacement, even if the change is purely cosmetic." `--fail`: "Fail and exit with a code of 1 if differences are detected." `--security-only`: "Only diff for broadened security changes." — [cdk diff](https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-diff.html) (read: **full** options section)
- The page documents no JSON or other machine-readable output option for `cdk diff`. — [same](https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-diff.html)

**kubectl** (Kubernetes reference, auto-generated page; version not captured)
- "Diff configurations specified by file name or stdin between the current online configuration, and the configuration as it would be if applied. The output is always YAML." "Exit status: 0 No differences were found. 1 Differences were found. >1 Kubectl or diff failed with an error." `KUBECTL_EXTERNAL_DIFF` selects another diff program. — [kubectl diff](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_diff/) (read: **part**, synopsis and options)

### Inferences
- Counts of create, update, replace and delete for a Terraform change are a pure function of documented JSON: count `resource_changes` by `actions`, treating a two-element list as replace.
- CDK and kubectl give a yes/no ("anything differs") by exit code and a text diff that must be parsed for anything finer. With `cdk diff --method=template`, replacement can be over-reported.
- All of these need credentials and live state (a Terraform backend, an AWS account, a cluster). A tool with only git cannot run them; it can only read a plan file or a CI log that someone else produced.

### Gaps
- Pulumi: no documentation page describing the JSON schema of `pulumi preview --json` (for example a change-summary field with counts per operation) was found; `https://www.pulumi.com/docs/iac/cli/json/` returned 404. The existence of per-operation counts in that JSON is unverified.
- CDK: whether a change set created by `cdk diff` can be read back as JSON through CloudFormation was not researched.
- kubectl: the page does not say whether deletions (resources removed from the manifests) appear in the diff; the `--prune` option text was not read.
- Terraform: `-detailed-exitcode` for `terraform plan` was not read in this round.

## Part 2b. Database migration tools: which report data loss or irreversibility

### Takeaway
Atlas and squawk flag dropped tables and columns as named, machine-readable rule violations; Atlas calls them destructive ("loss of data"), squawk frames them as breaking existing clients. Prisma warns about data loss when a migration is created, not in `migrate diff`. Django documents irreversibility per operation but `sqlmigrate` only prints SQL. Alembic and Flyway report neither: reversibility there is simply whether someone wrote a `downgrade()` or an undo script.

### Cited Findings

**Atlas** (atlasgo.io; undated)
- "Destructive changes are changes to a database schema that result in loss of data." "Running migration linting locally on in CI fails with exit code 1 in case destructive changes are detected." Checks: "DS101 Schema was dropped, DS102 Table was dropped, DS103 Non-virtual column was dropped". Data-dependent: "MF Data-dependent changes (changes that might fail)", including "MF102 Modifying non-unique index to unique, MF103 Adding a non-nullable column to an existing table, MF104 Modifying a nullable column to non-nullable". Backward-incompatible: "BC101 Renaming a table, BC102 Renaming a column, BC103 Dropping a table, BC104 Dropping a column". Some analyzer groups are marked "Atlas Pro" (seen on "CD Constraint deletion changes" and "TX Transaction Safety"). — [Atlas lint analyzers](https://atlasgo.io/lint/analyzers) (read: **part**, keyword extraction from a 372 KB page)
- Reversal is computed, not declared: for `atlas migrate down`, "Atlas computes a migration plan based on the current state of the database"; "If the down migration plan contains pre-migration checks, Atlas executes the checks on the database and reports the results"; "Manual down migration files override automatically generated plans"; `--skip-checks` "skips executing pre-migration checks". Approval can be required before a down plan is applied. — [Atlas down migrations](https://atlasgo.io/versioned/down) (read: **part**)

**squawk** (PostgreSQL only; "Copyright © 2026 Squawk Authors"; MIT licence file in the repository)
- "Linter for Postgres migrations & SQL". — [squawk README](https://github.com/sbdchd/squawk/blob/master/README.md) (read: **part**)
- Rule list includes `ban-drop-column`, `ban-drop-table`, `ban-drop-database`, `ban-drop-schema`, `ban-drop-not-null`, `ban-truncate-cascade`, `changing-column-type`, `renaming-column`, `renaming-table`, `adding-not-nullable-field`, `adding-required-field`, `constraint-missing-not-valid`, `require-concurrent-index-creation`, `require-timeout-settings`, and about 60 more. — [squawk rules](https://squawkhq.com/docs/rules) (read: **part**, rule names extracted)
- `ban-drop-column`: "Dropping a table or foreign table column or a composite type attribute may break existing clients." — [ban-drop-column](https://squawkhq.com/docs/ban-drop-column) (read: **part**)
- No rule about reversibility or missing down migrations appears in the rule names extracted. — [squawk rules](https://squawkhq.com/docs/rules)

**Prisma** (ORM v7 CLI reference; undated)
- `migrate diff`: "`--script` Outputs a SQL script instead of the default human-readable summary"; "`--exit-code` Change the exit code behavior to signal if the diff is empty or not (Empty: 0, Error: 1, Not empty: 2)". Limit: "The `migrate diff` command can only compare database features that are supported by Prisma. If two databases differ only in unsupported features, such as views or triggers, then `migrate diff` will not show any difference between them." — [Prisma CLI reference](https://www.prisma.io/docs/orm/reference/prisma-cli-reference) (read: **part**)
- Data-loss warnings come from `migrate dev` and `db push`: "In a non-interactive environment, such as a CI job, `migrate dev` cannot ask for confirmation. If the schema change raises a data loss warning, the command prints the warning, exits with an error and creates no migration." "Data loss warnings are evaluated against the database the command runs on". `db push --accept-data-loss`: "Ignore data loss warnings. This option is required if as a result of making the schema changes, data may be lost." — [same](https://www.prisma.io/docs/orm/reference/prisma-cli-reference)
- Agent-specific guard: "Prisma ORM includes built-in safety checks to prevent accidental destructive commands when run through AI coding assistants." — [same](https://www.prisma.io/docs/orm/reference/prisma-cli-reference)

**Django** (documentation for 5.2, the version requested; a newer release may exist)
- `sqlmigrate`: "Prints the SQL for the named migration. This requires an active database connection, which it will use to resolve constraint names". "`--backwards` Generates the SQL for unapplying the migration." The entry says nothing about data loss. — [django-admin, sqlmigrate](https://docs.djangoproject.com/en/5.2/ref/django-admin/#sqlmigrate) (read: **part**)
- Irreversibility is documented per operation. `RemoveField`: "The operation is reversible (apart from any data loss, which is irreversible) if the field is nullable or if it has a default value that can be used to populate the recreated column. If the field is not nullable and does not have a default value, the operation is irreversible." `RunSQL`: "If `reverse_sql` is `None` (the default), the `RunSQL` operation is irreversible." `RunPython`: "If `reverse_code` is `None` (the default), the `RunPython` operation is irreversible." Custom operations declare `reversible = True/False`. — [Migration operations](https://docs.djangoproject.com/en/5.2/ref/migration-operations/) (read: **part**)

**Alembic** (documentation for 1.20.1)
- Autogenerate "is not intended to be perfect. It is always necessary to manually review and correct the candidate migrations". It "will detect: Table additions, removals. Column additions, removals." It "can not detect: Changes of table name. These will come out as an add/drop of two different tables, and should be hand-edited into a name change instead. Changes of column name. Like table name changes, these are detected as a column add/drop pair". — [Alembic autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) (read: **part**)
- Down migrations are optional: "`upgrade()` is required while `downgrade()` is only needed if down-revision capability is desired, though it's probably a good idea." — [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) (read: **part**)
- `alembic check` "returns an error code plus a message if it is detected that new operations would be rendered into a new revision" (it tests whether models and migrations are in step, not whether a migration is destructive). — [Alembic autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- No passage read describes a data-loss warning or an irreversibility report.

**Flyway** (Redgate documentation; undated)
- Undo is a paid feature and is a hand-written script: "EDITION: TEAMS. Undo migrations are the opposite of regular versioned migrations." "An undo migration is responsible for undoing the effects of the versioned migration with the same version." Limits: "They work for undoing schema changes but not so well for undoing data changes - If your versioned migration script contains destructive changes (drop, delete, truncate, ...". "Undo migrations assume the whole migration succeeded and should now be undone." "Please note, you should take care if you have destructive changes (drop, delete, truncate etc) in your deployment." — [Flyway undo migrations](https://documentation.red-gate.com/fd/undo-migrations-273973334.html) (read: **part**)
- Dry runs (Teams edition): "The database is no longer modified and all SQL statements that would have been applied are sent to the dry run output instead." — [Flyway dry runs](https://documentation.red-gate.com/fd/migration-command-dry-runs-275218517.html) (read: **part**)

**Summary table (documentation only)**

| Tool | Reports that a migration drops data | Reports that it cannot be reversed |
|---|---|---|
| Atlas `migrate lint` | Yes: DS101 to DS103, exit code 1 | Not as a lint rule. `migrate down` computes a reverse plan with pre-migration checks |
| squawk | Flags drops by rule (`ban-drop-column`, `ban-drop-table`), worded as breaking clients | No rule found |
| Prisma | `migrate dev` and `db push` warn; `migrate diff` documents only diff and exit code | Not documented in the page read |
| Django `sqlmigrate` | No (prints SQL) | Not by `sqlmigrate` text; per-operation rules are documented and `--backwards` exists |
| Alembic | No | No; `downgrade()` is optional and hand-reviewed |
| Flyway | No (not in pages read) | No; an undo script exists or does not |

### Inferences
- "Does this migration drop a table or column" is a computed fact with Atlas or squawk on SQL migration files, without a database connection for squawk. With Alembic or Django the tool would have to inspect the migration file itself for `drop_table`, `drop_column`, `RemoveField`, `DeleteModel`.
- A rename shows up as a drop plus an add in Alembic autogenerate, so a naive "drops a column" check will fire on renames unless the migration was hand-edited.
- "Is it reversible" has three different meanings across tools: a down script exists (Alembic, Flyway), every operation declares a reverse (Django), or a reverse plan can be computed and passes checks (Atlas). None of them covers lost data, which Django states outright ("apart from any data loss, which is irreversible").

### Gaps
- Django: the pages read do not say what `sqlmigrate --backwards` does on an irreversible migration (whether it errors). Not verified.
- Flyway: the `check` command page (code analysis, `-changes`, `-drift`) could not be opened at the URL tried (it resolved to an unrelated page), so whether Flyway's code analysis flags drops is unanswered.
- Prisma: whether `migrate diff` prints data-loss warnings, and how down migrations are generated, were not found in the reference page.
- Atlas: which specific analyzers need the paid tier was read only in part; the DS analyzers' tier was not confirmed in this round. Atlas version not captured.
- squawk: version number not captured; the repository has a `LICENSE-MIT` file, and whether it is dual-licensed was not checked.

## Part 2c. Operational predictions that a computed fact could check

### Takeaway
A short list of closed operational questions can be scored from documented tool output with no model: resource counts by action from a Terraform plan, whether anything differs for CDK or Kubernetes, whether a migration drops a schema, table or column, and whether a down path exists. Each needs either a plan artefact produced with credentials or a migration file in the repository.

### Cited Findings
- Terraform counts: `changes.add`, `changes.change`, `changes.remove` in the `change_summary` message; per-resource `actions` in `resource_changes`. — [Machine-readable UI](https://developer.hashicorp.com/terraform/internals/machine-readable-ui); [JSON output format](https://developer.hashicorp.com/terraform/internals/json-format)
- Why a resource is replaced: `action_reason` and `replace_paths`. — [JSON output format](https://developer.hashicorp.com/terraform/internals/json-format)
- "Anything changes at all": `pulumi preview --expect-no-changes`, `cdk diff --fail` (exit 1), `kubectl diff` (exit 1), `prisma migrate diff --exit-code` (exit 2). — [pulumi preview](https://www.pulumi.com/docs/iac/cli/commands/pulumi_preview/); [cdk diff](https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-diff.html); [kubectl diff](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_diff/); [Prisma CLI reference](https://www.prisma.io/docs/orm/reference/prisma-cli-reference)
- Security widening: `cdk diff --security-only` ("Only diff for broadened security changes"). — [cdk diff](https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-diff.html)
- Destructive migration: Atlas DS101, DS102, DS103; squawk `ban-drop-*` rules. — [Atlas lint analyzers](https://atlasgo.io/lint/analyzers); [squawk rules](https://squawkhq.com/docs/rules)
- Migration that may fail on existing data: Atlas MF102 to MF104; squawk `adding-not-nullable-field`. — same pages
- Migration that breaks existing readers: Atlas BC101 to BC104; squawk `renaming-column`, `renaming-table`, `changing-column-type`. — same pages
- Reversibility declared: Django `reverse_sql`/`reverse_code` being `None` makes the operation irreversible; Alembic `downgrade()` is optional; Flyway undo scripts pair by version. — [Migration operations](https://docs.djangoproject.com/en/5.2/ref/migration-operations/); [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html); [Flyway undo migrations](https://documentation.red-gate.com/fd/undo-migrations-273973334.html)

### Inferences
Prediction questions and the fact that scores them (my synthesis; "needs" says what the tool must have):

| Prediction the developer makes | Computed fact | Needs |
|---|---|---|
| How many resources will this plan create, update, replace, delete | Count of `resource_changes` by `actions` in `terraform show -json` | A saved plan file (credentials and state) |
| Will anything be destroyed | `changes.remove > 0`, or any `actions` containing `"delete"` | Same |
| Will a named resource be replaced, and why | Its `actions` pair, `action_reason`, `replace_paths` | Same |
| Does this change touch live infrastructure at all | Exit code of `cdk diff --fail`, `kubectl diff`, `pulumi preview --expect-no-changes` | Cloud or cluster access |
| Does it widen permissions (CDK) | Non-empty `cdk diff --security-only` | AWS access |
| Does the migration drop a schema, table or column | Atlas DS101 to DS103 or squawk `ban-drop-*` on the migration file | Migration SQL; squawk needs no database |
| Could the migration fail on existing rows | Atlas MF codes, squawk `adding-not-nullable-field` | Migration SQL (the answer is "might", not "will") |
| Does it break code still reading the old shape | Atlas BC codes, squawk rename and type-change rules | Migration SQL |
| Does a down migration exist | Alembic: non-empty `downgrade()`; Flyway: matching undo script; Django: no operation with `reverse_sql=None` or `reverse_code=None` | Repository only |
| Was a new migration file added at all | `git diff --name-only` filtered to the migrations directory | Repository only |

- The repository-only rows (last two, and squawk on SQL files) fit a tool that has git and nothing else. The Terraform rows are exact but depend on a plan artefact the agent or CI must produce.
- "Does a down migration exist" is checkable; "is the change truly reversible" is not, because dropped data is not restored by any of these tools.

### Gaps
- No documentation read covers computing these facts for a change that an agent has only planned and not yet written; all of them need the files to exist.
- Pulumi per-operation counts from JSON remain unverified (see Part 2a gaps).
- Reading Alembic or Django migration files for drops is my proposal; neither project documents a command that does it.

## Part 3. Tools the first pass skipped

### Takeaway
Of the twelve, the ones that give a system-level graph from source without a build are ast-grep and Semgrep (pattern matches, not graphs), import-linter (Python import graph with rules), Joern's source frontends, and Nx (JavaScript-family workspaces it already manages). pydeps and ArchUnit work from bytecode, and Bazel query needs a Bazel workspace. D2 and ELK are free layout and rendering options; the LikeC4 and Structurizr MCP servers serve a hand-written architecture model, not one computed from code.

### Cited Findings

Licences below were read from the licence file in each project's repository on 16 Nov 2026.

- **Joern.** "Joern is a platform for analyzing source code, bytecode, and binary executables. It generates code property graphs (CPGs), a graph representation of code for cross-language code analysis. Code property graphs are stored in a custom graph database. This allows code to be mined using search queries formulated in a Scala-based domain-specific query language." Its stated goal is "vulnerability discovery and research in static program analysis". Frontends listed: C, C#, Ghidra (binaries), Go, Java source (`javasrc2cpg`), Java bytecode (`jimple2cpg`), JavaScript, Kotlin, PHP, Python, Ruby, Swift. Build needed: the docs describe source frontends that parse a directory directly (`joern-parse /some/input/path --language PYTHONSRC`); bytecode and binary frontends need compiled input. Licence: Apache 2.0. — [Joern README](https://github.com/joernio/joern/blob/master/README.md) (read: **part**); [Joern frontends](https://docs.joern.io/frontends/) (undated; read: **full**)
- **Semgrep.** "Semgrep is a fast, open-source, static analysis tool that searches code, finds bugs, and enforces secure guardrails and coding standards. Semgrep supports 30+ languages". "Semgrep rules look like the code you already write; no abstract syntax trees, regex wrestling, or painful DSLs." It computes pattern matches, not a dependency graph. Limit of the free edition, in the vendor's words: "Semgrep Community Edition will miss many true positives as it can only analyze code within the boundaries of a single function or file"; cross-file and cross-function analysis are in the paid platform. Languages named include C, C++, C#, Go, Java, JavaScript, Kotlin, PHP, Python, Ruby, Rust, Scala, Swift, Terraform, TypeScript, YAML. Licence of the repository: LGPL 2.1. — [Semgrep README](https://github.com/semgrep/semgrep/blob/develop/README.md) (read: **part**)
- **ast-grep.** "ast-grep(sg) is a CLI tool for code structural search, lint, and rewriting." "ast-grep's core is an algorithm to search and replace code based on abstract syntax tree produced by tree-sitter." It computes syntax-tree pattern matches per file; no name resolution is claimed. Built-in languages: Bash, C, C++, C#, CSS, Elixir, Go, Haskell, HCL, HTML, Java, JavaScript, JSON, Kotlin, Lua, Markdown, Nix, PHP, Python, Ruby, Rust, Scala, Solidity, Swift, TypeScript, TSX, YAML, Zig. No build needed (it parses source). Licence: MIT. — [ast-grep README](https://github.com/ast-grep/ast-grep/blob/main/README.md) (read: **part**); [ast-grep language list](https://ast-grep.github.io/reference/languages.html) (undated; read: **part**)
- **pydeps.** Draws a Python module dependency graph through Graphviz. How it finds edges: "pydeps finds imports by looking for import-opcodes in python bytecodes (think `.pyc` files). Therefore, only imported files will be found (ie. pydeps will not look at files in your directory that are not imported). Additionally, only files that can be found using the Python import machinery will be considered (ie. if a module is missing or not installed, it will not be included regardless if it is being imported)." Options include `--show-cycles` ("show only import cycles"), `--externals`, `--reverse`, `--cluster`. Python only. It needs the package and its dependencies importable, plus Graphviz installed. Licence: BSD-style (the licence file is the BSD "Redistribution and use in source and binary forms" text; the variant name is not stated in the lines read). — [pydeps README](https://github.com/thebjorn/pydeps/blob/master/README.rst) (read: **part**)
- **import-linter.** "**Import Linter** allows you to impose constraints on the imports between your Python modules. It also provides a browser-based user interface for exploring the architecture of any Python package." Tagline: "Lint your Python architecture." Python only. Licence: BSD 2-Clause. — [import-linter README](https://github.com/seddonym/import-linter/blob/main/README.md) (read: **full**, 1 KB)
- **ArchUnit.** "ArchUnit is a free, simple and extensible library for checking the architecture of your Java code. That is, ArchUnit can check dependencies between packages and classes, layers and slices, check for cyclic dependencies and more. It does so by analyzing given Java bytecode, importing all classes into a Java code structure." Rules run as ordinary unit tests. It works on bytecode, so the code must be compiled first. Licence: Apache 2.0. — [ArchUnit README](https://github.com/TNG/ArchUnit/blob/main/README.md) (read: **part**)
- **Bazel query.** Three query tools over a Bazel workspace: `query` "runs on the post-loading phase target graph"; `cquery` works on configured targets ("For cquery, this will include resolved toolchains"); `aquery` "operates on the post-analysis Configured Target Graph and exposes information about" actions and artifacts. `query` has "no concept of configurations" and resolves conditional dependencies "for all configurations, which means that it may be a conservative over-approximation, and not exactly precise." Graph output: `bazel query "allpaths(//foo, third_party/...)" --notool_deps --output graph | dot -Tsvg`. Functions include `deps`, `rdeps`, `somepath`, `allpaths`, `kind`. Language-agnostic, at the level of build targets, and only for repositories that already have Bazel BUILD files. `query` reads BUILD files without compiling. Licence: Apache 2.0. — [Bazel query guide](https://bazel.build/query/guide) and [Bazel query language](https://bazel.build/query/language) (undated; read: **part**)
- **Nx graph.** "The projects in the workspace have dependencies between them and form a graph known as the **Project Graph**. Nx uses this project graph in many ways to make informed decisions such as which tasks to run, when the results of a task can be restored from cache, and more." There is also a "**Task Graph**". "It caches the graph and reanalyzes only the files that changed." Launch with `npx nx graph`; the page has sections "Export project graph to JSON" and "Export the project graph as an image". Works on workspaces that use Nx. Licence: MIT. — [Nx, Explore your workspace](https://nx.dev/docs/features/explore-graph) (undated; read: **part**)
- **D2.** A text-to-diagram language with a CLI. "D2 bundles three layout engines. Select one with `--layout=dagre`, `--layout=elk`, or `--layout=tala`." "Dagro (default, bundled): A native Go port of the Dagre directed graph layout engine that produces layered/hierarchical layouts." "elk-go (bundled): A native Go port of the ELK directed graph layout engine, particularly suited for node-link diagrams with an inherent direction and ports." "TALA (bundled, opt-in): Native layout and edge-routing engine designed specifically for software architecture diagrams." Licence of the repository: Mozilla Public License 2.0. — [D2 README](https://github.com/terrastruct/d2/blob/master/README.md) (read: **part**)
- **ELK layout.** "The Eclipse Layout Kernel (or ELK) is two things: a collection of layout algorithms, and an infrastructure that bridges the gap between layout algorithms and diagram viewers and editors." Special features named: "ports (edges' attachment points on the corresponding nodes' borders) and hierarchical nodes (nodes that contain further nodes as children)". "ELK itself doesn't render the drawing but only computes positions (and possibly dimensions)". JavaScript version: "elkjs is not a diagramming framework itself - it computes positions for the elements of a diagram"; `elk-worker.js` "is generated from ELK's Java code base using GWT". Licence: Eclipse Public License 2.0 (both ELK and elkjs). — [ELK home](https://eclipse.dev/elk/) (undated; read: **part**); [elkjs README](https://github.com/kieler/elkjs/blob/master/README.md) (read: **part**)
- **LikeC4 MCP server.** "LikeC4 MCP Server provides knowledge of your LikeC4 model to LLMs." Tools include `list-projects`, `read-project-summary`, `search-element`, `read-element`, `read-view` ("Full view details (nodes/edges) and source location"), `find-relationships` ("Direct and indirect relationships between two elements"), `query-incomers-graph` ("Recursive BFS graph of all upstream dependencies/producers"), `query-outgoers-graph` ("all downstream consumers/dependents"), `render-view` (interactive diagram "for hosts that support MCP Apps") and `preview-view` ("Renders a preview of a LikeC4 view from DSL text without saving files"). Start with `likec4 mcp --http` or `npx -y @likec4/mcp` (stdio). It serves a model written by hand in the LikeC4 DSL; the page does not describe computing the model from code. Licence: MIT. — [LikeC4 AI tools](https://likec4.dev/tooling/ai-tools/) (undated; read: **part**)
- **Structurizr MCP server.** "A free and open source Structurizr MCP server is available on GitHub." Tools, enabled by flags: with `-dsl`, "Validate Structurizr DSL... Returns "OK" if the DSL is parseable, or an error message otherwise", "Parse Structurizr DSL... Returns a JSON workspace", "Inspect Structurizr DSL... Returns a list of inspection violations"; with `-mermaid` and `-plantuml`, export a view to Mermaid, PlantUML or C4-PlantUML; with `-server-create`, `-server-read`, `-server-update`, `-server-delete`, manage workspaces on a Structurizr server. A hosted instance runs "with the DSL, PlantUML, and Mermaid tools enabled." It works on a hand-written C4 model in the Structurizr DSL. Licence of the main Structurizr repository: Apache 2.0. — [Structurizr MCP server](https://docs.structurizr.com/ai/mcp) (undated; read: **part**)

### Inferences
- None of the twelve produces a before/after module-graph diff out of the box. import-linter (Python) and Nx (its workspaces) come closest to a ready graph; ast-grep can extract import statements in many languages without a build but leaves resolution to the caller.
- For drawing, ELK (through elkjs, or D2's bundled Go port) is the free engine that handles nested boxes and ports, which a module-inside-package diagram needs.
- LikeC4 and Structurizr are useful as output formats or as a place to keep a curated model, and LikeC4's `render-view` shows a working MCP Apps diagram. They do not remove the need to compute the graph.
- D2's README now lists TALA as "bundled, opt-in". The first pass recorded, as unverified background, that TALA is a paid engine. The README lines read here do not state TALA's licence terms, so the two are not reconciled.

### Gaps
- Joern: the docs read do not give maturity levels per frontend, indexing times, or how complete the call graph is for dynamic languages.
- Semgrep: the page read does not state whether a build is ever required; the supported-languages page was downloaded but the relevant sentence was not found. Which features fall under which licence beyond the repository's LGPL file was not read.
- import-linter: contract types and the statement of what the import graph misses were not re-read this round (the first pass listed the contract types). The current version number was not captured.
- pydeps: supported Python versions were not captured.
- ArchUnit: current version not confirmed (the user guide page contains the string "version 1.5.1", not verified as the latest).
- Nx: the JSON export command and its schema were not read in detail; language coverage beyond JavaScript and TypeScript (through plugins) was not checked.
- D2: TALA licence terms; whether elk-go matches Java ELK output.
- Structurizr MCP: the licence file of the MCP server's own repository was not opened (GitHub API calls were blocked in this session); the documentation calls it "free and open source".
- Licence names come from licence files, not from each project's documentation pages.
