# Coding agent surfaces and extension mechanisms

Track: coding agent surfaces and extension mechanisms. Written 7 Nov 2026.

This report asks one question: how does one learning product reach every
coding agent a general user might install, with the same learning outcomes on
each? It maps what every surface lets a third party add, finds the largest
common denominator, names the richer tiers above it, and proposes one
architecture that is written once and adapted per agent.

It starts from the earlier round (`design/learning-experience/research/claude.md`,
`codex-others.md`, `protocols.md`). Those reports were written for one person on
Claude Code. They are treated as evidence, not as the plan.

## How to read the tags

- **[verified: URL]** I read the claim on that page during this research.
- **[verified earlier: URL]** The earlier round read or tested it on that page
  (see the three files above). I did not re-read it today. Treat it as strong
  but one step older.
- **[unverified]** From a third-party page, a search snippet, or my inference.
  It may be true. It needs a check before we build on it.
- **needs to be measured** No number exists yet.

Where a cell says "not documented", I looked on the official page and the
feature was not there. That is weaker than "not supported".

---

## 1. Findings that matter most

1. **Three things now reach nearly every agent: an instruction file, an Agent
   Skill folder, and an MCP server's tools.** AGENTS.md lists 23 named agents
   that read it, including Codex, Cursor, Copilot coding agent, Gemini CLI,
   Zed, Junie, Amp, opencode, Aider, Windsurf, goose, Devin and Roo Code
   [verified: https://agents.md]. Claude Code reads AGENTS.md when no CLAUDE.md
   exists, from v2.1.277 [verified: https://code.claude.com/docs/en/memory.md].
   `.agents/skills/` is read by Codex, Cursor, VS Code Copilot, Gemini CLI, Zed,
   Roo, Amp, OpenCode, goose and Devin (sources in section 3). MCP tools work
   in every surface in this report except Aider, where MCP is not documented.
2. **Hooks exist on almost every agent, with the same five moments.** Session
   start, prompt submit, before tool, after tool, and turn end appear in Claude
   Code, Codex, Cursor, Copilot, Gemini CLI, Devin, Kiro, Amp and Cline (section
   5). The names and JSON shapes differ. One dispatcher with a thin per-agent
   mapping covers them all.
3. **Several agents already read Claude Code's files.** VS Code Copilot reads
   `.claude/settings.json` hooks [verified earlier:
   https://code.visualstudio.com/docs/copilot/customization/hooks]. Devin CLI
   reads hooks from `.claude/settings.json` and rules from `CLAUDE.md`
   [verified: https://docs.devin.ai/cli/extensibility/hooks/overview.md],
   [verified: https://docs.devin.ai/cli/extensibility/rules.md]. Cursor, Cline,
   OpenCode, Amp and goose read `.claude/skills/` [sources in section 3]. The
   Claude layout is a de facto second standard, but we should not rely on it.
4. **Interactive questions inside the build split into three groups.** MCP
   elicitation forms work in Claude Code, Codex, VS Code Copilot and Cursor
   [verified earlier: protocols.md test A1, codex-others.md test],
   [verified: https://code.visualstudio.com/api/extension-guides/ai/mcp],
   [verified: https://cursor.com/docs/context/mcp]. Zed and Gemini CLI do not
   document it [verified: https://zed.dev/docs/ai/mcp],
   [verified: https://geminicli.com/docs/tools/mcp-server/]. Cloud agents that
   run unattended (Copilot cloud agent, Codex cloud) have no live user to ask.
5. **Rich custom UI exists on a minority of surfaces, through four unrelated
   mechanisms.** MCP Apps render in Claude chat, Claude Desktop chat, VS Code
   Copilot, Goose, Cursor and ChatGPT, not in Claude Code [verified:
   https://modelcontextprotocol.io/extensions/apps/overview.md],
   [verified: https://cursor.com/docs/context/mcp], [verified earlier:
   protocols.md]. Claude Code has mods, Amp has plugin UI calls, OpenCode
   Desktop has an experimental GUI plugin export. None of these is portable.
6. **Every vendor now runs agents in the cloud, and their disks do not keep
   our files.** Claude Code cloud VMs are reclaimed after inactivity; the
   conversation is restored, background work is not [verified:
   https://code.claude.com/docs/en/claude-code-on-the-web.md]. Copilot cloud
   agent sessions on GitHub Actions stop at 59 minutes [verified:
   https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent].
   Cursor cloud agents run in "isolated VMs" [verified:
   https://cursor.com/docs/cloud-agent]. A record kept only in a local git repo
   with no remote cannot be written from these sessions. This collides with
   founder decision 1 (section 9).
7. **The phone is reached through each vendor's own app, never through a common
   path.** Claude app Code tab (cloud sessions and Remote Control) [verified:
   https://code.claude.com/docs/en/mobile.md], ChatGPT mobile for Codex
   [verified earlier: codex-others.md], Cursor iOS and web for cloud agents
   [verified: https://cursor.com/docs/cloud-agent], GitHub Mobile for Copilot
   cloud agent [verified: about-cloud-agent page above], Amp iOS and Android
   [verified: https://ampcode.com/manual]. Local-only agents (Aider, Gemini CLI,
   Zed, Cline, Roo, OpenCode, Kiro) have no documented phone path.
8. **The standards are consolidating under one roof.** The Agentic AI
   Foundation (AAIF) launched under the Linux Foundation on 9 Dec 2025 with MCP,
   goose and AGENTS.md as founding projects [unverified: press, e.g.
   https://sdtimes.com/ai/linux-foundation-forms-agentic-ai-foundation-to-be-new-home-for-mcp-goose-and-agents-md/].
   The AGENTS.md site itself says it is "stewarded by the Agentic AI Foundation
   under the Linux Foundation" [verified: https://agents.md]. MCP now has an
   official Skills extension (SEP-2640, Final) that serves SKILL.md folders over
   MCP [verified: https://modelcontextprotocol.io/extensions/skills/overview.md].
9. **Feature parity of mechanism is impossible. Feature parity of outcome is
   possible.** Aider has no hooks and no documented MCP. Copilot cloud agent
   supports MCP tools only, no prompts or resources [verified:
   https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp].
   We can still deliver every learning outcome on every surface (a prediction
   before a build, an explain-back after, a "your line", spaced review, a
   record) if the floor is plain text and each richer tier is an enhancement.
   This is a challenge to how decision 6 is worded (section 9).
10. **Windsurf is now Devin Desktop.** Cognition renamed it on 2 June 2026 and
   replaced the Cascade agent with Devin Local [unverified: press, e.g.
   https://dev.to/jovan_chan_9500711396d4e6/windsurf-is-now-devin-desktop-what-the-june-2-rebrand-agent-command-center-default-surface-and-5d0i].
   The Devin docs label releases "Devin Desktop (Windsurf)" and Devin Local
   reads AGENTS.md, `.agents/skills/`, MCP and hooks [verified:
   https://docs.devin.ai/desktop/devin-local/customizations.md]. Old
   `docs.windsurf.com` links now redirect to `docs.devin.ai`.

---

## 2. The surfaces in scope

| # | Surface | Vendor | Where the agent runs |
| :- | :- | :- | :- |
| 1 | Claude Code CLI | Anthropic | User's machine |
| 2 | Claude Code desktop app, Code tab | Anthropic | Machine, SSH, WSL, or cloud |
| 3 | Claude Code on the web (cloud sessions) | Anthropic | Anthropic VM |
| 4 | Claude Code in VS Code and JetBrains | Anthropic | User's machine |
| 5 | Claude app on the phone, Code tab | Anthropic | Cloud VM, or the machine via Remote Control |
| 6 | Codex CLI | OpenAI | User's machine |
| 7 | Codex in the ChatGPT desktop app | OpenAI | User's machine |
| 8 | Codex IDE extension | OpenAI | User's machine |
| 9 | Codex cloud | OpenAI | OpenAI container |
| 10 | ChatGPT mobile as Codex remote | OpenAI | A trusted host machine |
| 11 | Cursor IDE and Cursor CLI | Anysphere | User's machine |
| 12 | Cursor cloud agents (web, iOS, Slack) | Anysphere | Cursor VM |
| 13 | Devin Desktop (formerly Windsurf), Devin CLI | Cognition | Machine; cloud Devin by handoff |
| 14 | GitHub Copilot agent mode in VS Code | GitHub / Microsoft | User's machine |
| 15 | Copilot in Visual Studio, JetBrains, Eclipse, Xcode | GitHub | User's machine |
| 16 | Copilot CLI and the GitHub Copilot app | GitHub | User's machine |
| 17 | Copilot cloud agent (formerly coding agent) | GitHub | Cloud sandbox or GitHub Actions |
| 18 | Gemini CLI | Google | User's machine |
| 19 | Aider | Open source | User's machine |
| 20 | Cline | Cline | User's machine (VS Code, JetBrains, CLI) |
| 21 | Roo Code | Roo Code | User's machine (VS Code) |
| 22 | Zed agent, and external agents over ACP | Zed | User's machine |
| 23 | JetBrains AI Assistant and Junie | JetBrains | User's machine |
| 24 | Amp | Sourcegraph / Amp | Machine, web, phone apps |
| 25 | OpenCode | SST / Anomaly | User's machine (TUI, Desktop) |
| 26 | Kiro IDE, CLI, Web | AWS | Machine; web unverified |
| 27 | goose | Block (AAIF project) | User's machine |
| 28 | Factory Droid | Factory | User's machine |
| 29 | Claude chat and ChatGPT chat | Anthropic, OpenAI | Vendor cloud; not coding agents, but MCP Apps hosts |

Sources for "where it runs" are in the tables below. I did not research Warp,
Kilo Code, Augment, Jules or Continue in depth. AGENTS.md lists Warp, Kilo
Code, Augment and Jules as readers [verified: https://agents.md]; everything
else about them is [unverified].

---

## 3. Instructions files and Agent Skills

| Surface | Instruction files read | Agent Skills paths | Evidence |
| :- | :- | :- | :- |
| Claude Code (all surfaces) | `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`; `AGENTS.md` only when no CLAUDE.md is found, or by `@AGENTS.md` import | `.claude/skills/`, `~/.claude/skills/`, plugin skills | [verified: https://code.claude.com/docs/en/memory.md]; skills [verified earlier: https://code.claude.com/docs/en/skills.md] |
| Codex (CLI, app, IDE) | `AGENTS.md` | `.agents/skills/` up to repo root, `~/.agents/skills`, `/etc/codex/skills`; optional `agents/openai.yaml` | [verified earlier: https://learn.chatgpt.com/docs/build-skills] |
| Codex cloud | `AGENTS.md` [unverified] | Environment-level "Start skill" setting seen; in-task behaviour not documented | [verified: https://learn.chatgpt.com/docs/cloud] |
| Cursor IDE, CLI | `AGENTS.md` (root and nested), `.cursor/rules/*.mdc`; CLAUDE.md not mentioned | `.agents/skills/`, `.cursor/skills/`, `.claude/skills/`, `.codex/skills/` and home equivalents | [verified: https://cursor.com/docs/context/rules]; skills [verified earlier: https://cursor.com/docs/context/skills] |
| Cursor cloud agents | Rules not mentioned on the cloud page | Not mentioned | [verified: https://cursor.com/docs/cloud-agent] |
| Devin Desktop (Devin Local) | `AGENTS.md`, `AGENTS.local.md`, `AGENT.md`, `.devin/rules/`, legacy `.windsurf/rules/`, `.windsurfrules` | `.devin/skills/`, `.agents/skills/`, `.windsurf/skills/`, `~/.config/devin/skills/`, `~/.agents/skills/` | [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] |
| Devin CLI | Also `CLAUDE.md` and `~/.claude/CLAUDE.md` | Same as above | [verified: https://docs.devin.ai/cli/extensibility/rules.md], [verified: https://docs.devin.ai/cli/extensibility/skills/overview.md] |
| VS Code Copilot | `.github/copilot-instructions.md`, `AGENTS.md` | `.github/skills/`, `~/.copilot/skills/`, `.claude/skills/`, `.agents/skills/` | [verified earlier: https://code.visualstudio.com/docs/copilot/customization/agent-skills]; AGENTS.md [verified: https://agents.md] |
| Copilot in Visual Studio, JetBrains, Eclipse, Xcode | Custom instructions: yes in VS, preview elsewhere | Skills: VS yes, JetBrains preview, Eclipse and Xcode no | [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet] |
| Copilot CLI, GitHub.com, cloud agent | Custom instructions yes; AGENTS.md listed for "third-party agents" | Skills yes | [verified: cheat sheet above]; cloud agent [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent] |
| Gemini CLI | `GEMINI.md`; AGENTS.md listed as supported | `.gemini/skills/`, `.agents/skills/` and home equivalents; consent prompt on activation | [verified earlier: https://geminicli.com/docs/cli/skills/]; [verified: https://agents.md] |
| Aider | Any file loaded with `--read` or `read:` in `.aider.conf.yml`, conventionally `CONVENTIONS.md`; listed on agents.md | None documented | [verified: https://aider.chat/docs/usage/conventions.html], [verified: https://agents.md] |
| Cline | Rules ("always active"); `.clinerules/` | `.cline/skills/`, `.clinerules/skills/`, `.claude/skills/`, `~/.cline/skills/` | [verified: https://docs.cline.bot/customization/skills] |
| Roo Code | AGENTS.md listed on agents.md | `.roo/skills/`, `.agents/skills/`, home equivalents, `skills-{mode}/` | [verified: https://roocodeinc.github.io/Roo-Code/features/skills], [verified: https://agents.md] |
| Zed agent | AGENTS.md listed on agents.md; Zed's own rules page not read | `.agents/skills/`, `~/.agents/skills/`; trusted worktrees only | [verified: https://zed.dev/docs/ai/skills], [verified: https://agents.md] |
| Junie | `AGENTS.md` in project root (another page says `.junie/AGENTS.md` first) | Not documented on the Junie page | [verified: https://www.jetbrains.com/help/ai-assistant/junie-agent.html]; path order [unverified] |
| Amp | `AGENTS.md` | `.agents/skills/`, `.claude/skills/`, `~/.agents/skills/`, `~/.config/amp/skills/`, workspace and personal skill repositories; a skill can carry its own MCP servers | [verified: https://ampcode.com/docs/customize/skills], [verified: https://agents.md] |
| OpenCode | `AGENTS.md` | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`, home equivalents, HTTP catalogs | [verified: https://opencode.ai/docs/skills/], [verified: https://agents.md] |
| Kiro (IDE, CLI, Web) | Steering files; AGENTS.md picked up from workspace or `~/.kiro/steering/` | Skills supported; paths not read | [verified: https://kiro.dev/docs/ide/] for steering and skills; AGENTS.md [unverified] |
| goose | `.goosehints`, AGENTS.md (goose is on agents.md) | `.agents/skills/` (recommended), `.goose/skills/`, `.claude/skills/` | [verified: https://goose-docs.ai/docs/guides/context-engineering/using-skills], [verified: https://agents.md] |
| Factory Droid | `AGENTS.md`, `~/.factory/AGENTS.md` | `.factory/skills/` | [verified: https://agents.md] for AGENTS.md; rest [unverified] |
| ChatGPT chat | n/a | Skills inside plugins work on web, desktop and mobile | [verified earlier: https://learn.chatgpt.com/docs/build-skills] |

**What this means.** One skill folder at `.agents/skills/<name>/` (project) or
`~/.agents/skills/<name>/` (user) is read by at least 10 agents unchanged.
Claude Code and Cline need a copy or symlink under `.claude/skills/` or
`.cline/skills/`. Copilot reads `.github/skills/` and `.claude/skills/`. Aider
gets no skill; it gets the instruction file.

The instruction file is the true floor. A short block in AGENTS.md (and a
`@AGENTS.md` import line in CLAUDE.md when one exists) reaches every surface in
the table. It should say three things only: the learning tool is installed,
call it at the start of a session, and follow its instructions. Long rules in
AGENTS.md cost context in every session of every agent.

---

## 4. MCP support

| Surface | Transports | Tools | Prompts | Resources | Elicitation | Sampling | MCP Apps UI | Evidence |
| :- | :- | :- | :- | :- | :- | :- | :- | :- |
| Claude Code CLI, desktop, IDE | stdio, HTTP | Yes | Yes, as slash commands | Yes, `@` mentions; no subscriptions | Form and URL | Not declared | No | [verified earlier: https://code.claude.com/docs/en/mcp.md, protocols.md test A1] |
| Claude Code cloud sessions | Same; cards on web and desktop | Yes | Yes | Yes | Card on claude.ai/code | No | No | [verified earlier: same] |
| Claude chat, Claude Desktop chat | Remote connectors, local in Desktop | Yes | Yes | Yes | [unverified] | [unverified] | Yes | [verified: https://modelcontextprotocol.io/extensions/apps/overview.md] |
| Codex CLI | stdio, HTTP | Yes | [unverified] | [unverified] | Form and URL advertised | [unverified] | No (TUI does not declare it) | [verified earlier: codex-others.md test with 0.167.0] |
| Codex app (ChatGPT desktop) | Same engine | Yes | [unverified] | [unverified] | Approval and question panels | [unverified] | Panels exist; third-party servers need a re-test | [verified earlier: codex-others.md, https://learn.chatgpt.com/docs/changelog] |
| Codex cloud | [unverified] | [unverified] | [unverified] | [unverified] | No live user | [unverified] | [unverified] | [verified: https://learn.chatgpt.com/docs/cloud] says nothing on MCP |
| Cursor IDE | stdio, SSE, Streamable HTTP | Yes | Yes | Yes | Yes | Not mentioned | Yes (extension) | [verified: https://cursor.com/docs/context/mcp] |
| Cursor cloud agents | stdio, HTTP | Yes, team-configured | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [verified: https://cursor.com/docs/cloud-agent] |
| Devin Desktop / CLI | stdio, Streamable HTTP, SSE, with OAuth | Yes; approval before each call by default | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] |
| VS Code Copilot | stdio, HTTP, SSE (legacy) | Yes | Yes | Yes | Yes | Yes | Yes, inline only; `ui/message` fills the input box but does not send | [verified: https://code.visualstudio.com/api/extension-guides/ai/mcp]; inline detail [verified earlier: codex-others.md] |
| Copilot in VS, JetBrains, Eclipse, Xcode, CLI | MCP servers: yes on all | Yes | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet] |
| Copilot cloud agent | local, stdio, http, sse | Yes | No | No | [unverified]; no live user | [unverified] | No | [verified: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp]; OAuth remote servers not supported |
| Gemini CLI | stdio, SSE, Streamable HTTP | Yes | Yes, as slash commands | Yes | Not documented | Not documented | Not documented | [verified: https://geminicli.com/docs/tools/mcp-server/] |
| Aider | Not documented | Not documented | n/a | n/a | n/a | n/a | n/a | [verified: https://aider.chat/docs/config/options.html] (no MCP option) |
| Cline | stdio, remote [unverified] | Yes; MCP Marketplace with one-click install | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [verified: https://docs.cline.bot/mcp/mcp-marketplace.md] |
| Roo Code | [unverified] | Yes [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | Not read |
| Zed agent | Local command, remote URL | Yes | Yes | Not mentioned | No (listed as wanted) | No | No | [verified: https://zed.dev/docs/ai/mcp] |
| Zed external agents (ACP) | Zed forwards its MCP servers to the agent | Agent's own | Agent's own | Agent's own | ACP `elicitation/create` stabilized 24 Jul 2026 | n/a | No | [verified earlier: https://agentclientprotocol.com/announcements/elicitation-stabilized] |
| JetBrains AI Assistant, Junie | Custom MCP servers passed to agents; IntelliJ MCP server optional | Yes | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [verified: https://www.jetbrains.com/help/ai-assistant/acp.html], [verified: Junie page above] |
| Amp | [unverified]; servers can be bundled in a skill | Yes | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [verified: https://ampcode.com/docs/customize/skills] |
| OpenCode | Local command, remote URL in `opencode.json` | Yes | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [unverified: third-party summaries of https://opencode.ai/docs/mcp-servers] |
| Kiro | Local, Streamable HTTP | Yes; "powers" load MCP on keyword | [unverified] | [unverified] | [unverified] | [unverified] | [unverified] | [verified: https://kiro.dev/docs/ide/]; powers detail [unverified] |
| goose Desktop | stdio, HTTP | Yes | [unverified] | Yes | [unverified] | [unverified] | Yes, experimental; apps cannot talk to the chat | [verified earlier: https://goose-docs.ai/docs/guides/interactive-chat/mcp-ui/], [verified: MCP Apps page above] |
| ChatGPT chat | Remote HTTPS or Secure MCP Tunnel | Yes | n/a | Yes | [unverified] | n/a | Yes, full, with fullscreen and picture in picture | [verified earlier: https://developers.openai.com/apps-sdk/mcp-apps-in-chatgpt] |

**MCP protocol notes that change the design.**

- Revision 2026-07-28 made the core stateless, moved elicitation into Multi
  Round-Trip Requests, made Tasks and MCP Apps official extensions, and
  deprecated Sampling, Roots and Logging [verified earlier:
  https://blog.modelcontextprotocol.io/posts/2026-07-28/]. Claude Code 2.1.319
  tried `server/discover` first and fell back to 2025-11-25 [verified earlier:
  protocols.md test A1]. Our server must speak both revisions.
- Do not build on sampling. It is deprecated and Claude Code does not declare
  it. Grading runs in the agent itself, or in our engine with its own model
  call only if the user supplies a key.
- The MCP Skills extension lets a server serve a SKILL.md folder through
  `skills/list`, `skills/get` and `resources/read`, with digests and user
  approval on change [verified:
  https://modelcontextprotocol.io/extensions/skills/overview.md]. Host support
  "is still being implemented". The client matrix lists ChatGPT, fast-agent and
  MCP Inspector as partial [verified:
  https://modelcontextprotocol.io/extensions/client-matrix.md]. The other cells
  of that matrix did not survive my page fetch, so per-client MCP Apps and
  Tasks marks there are [unverified].
- Elicitation `message` text and the accepted answer pass through the client
  and reach the model [verified earlier: protocols.md test A1]. The rubric must
  never be in an elicitation. It stays inside our server until the answer locks.

---

## 5. Hooks and lifecycle events

Five canonical moments matter for learning. The table maps them per agent.

| Surface | Session start | Prompt submit | Before tool | After tool (and failure) | Turn end, can continue | Config location | Evidence |
| :- | :- | :- | :- | :- | :- | :- | :- |
| Claude Code | `SessionStart` | `UserPromptSubmit` | `PreToolUse` | `PostToolUse`, `PostToolUseFailure` | `Stop` (block to continue) | `.claude/settings.json`, plugin `hooks`, skill frontmatter | [verified earlier: https://code.claude.com/docs/en/hooks.md] |
| Codex | `SessionStart` | `UserPromptSubmit` | `PreToolUse` | `PostToolUse` | `Stop` with `decision: "block"` | `~/.codex/hooks.json`, `<repo>/.codex/hooks.json`, `config.toml`, plugin `hooks/hooks.json` | [verified: https://learn.chatgpt.com/docs/hooks] |
| Cursor IDE | `sessionStart` | `beforeSubmitPrompt` | `preToolUse`, `beforeShellExecution`, `beforeMCPExecution` | `postToolUse`, `postToolUseFailure`, `afterFileEdit` | `stop` with `followup_message` auto-submitted | `.cursor/hooks.json`, `~/.cursor/hooks.json` | [verified: https://cursor.com/docs/agent/hooks]; followup [verified earlier: codex-others.md] |
| Cursor cloud agents | Not run | `beforeSubmitPrompt` | `preToolUse` | `postToolUse`, `postToolUseFailure` | `stop` | Repo `.cursor/hooks.json` only | [verified: https://cursor.com/docs/agent/hooks], [verified: https://cursor.com/docs/cloud-agent] |
| Devin CLI and Devin Local | `SessionStart` | `UserPromptSubmit` | `PreToolUse` | `PostToolUse` | `Stop` | `.devin/hooks.v1.json`, also `.claude/settings.json` (CLI) | [verified: https://docs.devin.ai/cli/extensibility/hooks/overview.md]; Desktop reads `.devin/hooks.v1.json` [verified: customizations page] |
| Copilot CLI, Copilot app | `sessionStart` | `userPromptSubmitted` | `preToolUse` | `postToolUse`, `errorOccurred` | `agentStop` | `.github/hooks/*.json`, `~/.copilot/hooks/*.json`, plugins | [verified: https://docs.github.com/en/copilot/concepts/agents/hooks] |
| Copilot cloud agent | Subset of the above | Subset | Subset | Subset | Subset | `.github/hooks/*.json` | [verified: same page]; exact subset [unverified] |
| VS Code Copilot | `sessionStart` | `userPromptSubmitted` | `preToolUse` | `postToolUse` | `agentStop` | `.github/hooks/*.json` and `.claude/settings.json`; preview | [verified earlier: https://code.visualstudio.com/docs/copilot/customization/hooks] |
| Copilot in VS, JetBrains, Eclipse, Xcode | No hooks | | | | | | [verified: cheat sheet] |
| Gemini CLI | `SessionStart` | `BeforeAgent` | `BeforeTool` | `AfterTool` | `AfterAgent` (deny triggers a retry) | `settings.json`, extensions | [verified: https://geminicli.com/docs/hooks/reference/]; deny behaviour [verified earlier: codex-others.md] |
| Kiro | [unverified] | [unverified] | `PreToolUse` | `PostToolUse`, `PostFileSave` | `Stop` | Hook files; actions are shell command or agent prompt | [verified: https://kiro.dev/docs/hooks/] |
| Amp | `session.start` | `agent.start` | `tool.call` (allow, reject, modify) | `tool.result` | `agent.end` (return `continue`) | Plugins in `.amp/plugins/`, user and workspace repositories | [verified: https://ampcode.com/docs/customize/plugins] |
| OpenCode | Plugin events | Plugin events | Plugin events | Plugin events | Plugin events | JS or TS plugins, npm | [verified: https://opencode.ai/docs/plugins/] (event names not on that page) |
| Cline | `beforeRun` | [unverified] | `beforeTool` | `afterTool` | `afterRun` | SDK plugins; extension hooks since v3.36, macOS and Linux only | [verified: https://docs.cline.bot/sdk/plugins.md]; extension hooks [unverified] |
| Factory Droid | [unverified] | [unverified] | `pre_tool_use` [unverified] | `post_tool_use` [unverified] | [unverified] | `.factory/hooks.json` [unverified] | third-party only |
| Aider | None | None | None | `--auto-lint`, `--auto-test` after edits | None | `.aider.conf.yml` | [verified: https://aider.chat/docs/config/options.html] |
| Zed agent, Junie, Roo Code, goose | Not documented | | | | | | Zed and Junie pages read; Roo and goose skill pages do not mention hooks |

**What this means.** Every hook system that exists has a session start that can
inject context and a turn end that can either continue the turn or leave a
message. That is enough for the three timed learning moments: due reviews at
start, an explain-back or "your line" check at turn end, and a debugging drill
after a failing test.

A single program handles all of them: `learn hook <agent> <event>`. It reads the
agent's JSON on stdin, maps it to one internal event, decides, and writes the
agent's expected JSON or exit code. The per-agent part is a table of names and
output shapes, about the size of the table above.

---

## 6. Packaging, marketplaces and custom UI

| Surface | Package format | Marketplace or directory | Custom UI a third party can show | Evidence |
| :- | :- | :- | :- | :- |
| Claude Code CLI, desktop, VS Code | Plugin: skills, commands, agents, hooks, MCP, monitors, output styles, mods | Plugin marketplaces (`/plugin install`) | Mods: band above the prompt, pane, inputs, selects, SVG; CLI, desktop and VS Code only | [verified earlier: https://code.claude.com/docs/en/plugins/components.md, https://code.claude.com/docs/en/plugins/mods/overview.md] |
| Claude Code cloud and phone | Plugins that reach the session; `/plugin` not available from the app | Same | Elicitation cards; mods do not draw | [verified: https://code.claude.com/docs/en/mobile.md]; [verified earlier: claude.md] |
| Codex | Plugin: skills, apps, hooks; `agents/openai.yaml` for icon and MCP dependency | Plugins directory in ChatGPT, workspace directory | MCP App panels in the desktop app (third-party unconfirmed); question cards | [verified: https://learn.chatgpt.com/docs/build-plugins], [verified: https://learn.chatgpt.com/docs/hooks]; panels [verified earlier] |
| Cursor | Plugin: rules, skills, agents, commands, MCP, hooks | Cursor Marketplace, manually reviewed; team marketplaces; cursor.directory | MCP Apps inline in agent chat | [verified: https://cursor.com/docs/plugins], [verified: https://cursor.com/docs/context/mcp] |
| Devin Desktop, Devin CLI | Plugin: skills, rules, hooks, MCP, subagents; team marketplace | Team plugin marketplace | [unverified]; VS Code-family editor, so an editor extension may be possible [unverified] | [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] |
| VS Code Copilot | Copilot plugins; also any VS Code extension | VS Code Marketplace | MCP Apps inline; a VS Code extension webview panel | [verified: https://code.visualstudio.com/api/extension-guides/ai/mcp]; webview is the standard VS Code API [unverified for our use] |
| Copilot CLI, app, cloud agent | Plugins: agents, skills, hooks, integrations | [unverified] | None for cloud agent; text in PR | [verified: https://docs.github.com/en/copilot/concepts/customizations] (search summary) |
| Gemini CLI | Extension: prompts, MCP servers, commands, themes, hooks, sub-agents, skills | Extension gallery | Hook `systemMessage` text in the terminal | [verified: https://geminicli.com/docs/extensions/] |
| Kiro | Power: MCP servers, steering, optional hooks | Community powers | [unverified] | [verified: https://kiro.dev/docs/ide/]; contents [unverified] |
| Amp | Plugin, single-file or repository | Share URL; workspace repositories | `ctx.ui.notify`, `confirm`, `input`, `select`, command palette entries, buttons above the composer | [verified: https://ampcode.com/docs/customize/plugins] |
| OpenCode | npm plugin | npm | Desktop panels through an experimental `./gui-experimental` export | [verified: https://opencode.ai/docs/plugins/] |
| Cline | MCP servers; SDK plugins | MCP Marketplace | [unverified] | [verified: https://docs.cline.bot/mcp/mcp-marketplace.md] |
| JetBrains AI Assistant | ACP agents from the ACP registry; custom `~/.jetbrains/acp.json` | ACP registry | ACP permission and elicitation UI | [verified: https://www.jetbrains.com/help/ai-assistant/acp.html] |
| Zed | ACP agents; extensions | Zed extensions, ACP registry [unverified] | Text and markdown in the agent panel | [verified: https://zed.dev/docs/ai/mcp] |
| goose | Extensions (MCP), recipes, plugins with skills | [unverified] | MCP Apps, inline or standalone windows | [verified earlier: goose MCP Apps guide] |
| Aider | None | None | None | [verified: options page] |
| ChatGPT chat | Plugin: apps (MCP) and skills | Plugins directory | MCP Apps, full | [verified earlier: Apps SDK docs] |

---

## 7. Where it runs, disk lifetime, and mobile

| Surface | Runs | Disk between sessions | Phone access | Evidence |
| :- | :- | :- | :- | :- |
| Claude Code CLI, desktop local, IDE | User's machine | Persistent | Remote Control from the Claude app; push notifications while active | [verified: https://code.claude.com/docs/en/mobile.md] |
| Claude Code cloud | Anthropic VM; isolated | VM reclaimed after inactivity; conversation restored; shell work, subagents and session tasks not restored | Claude app Code tab | [verified: https://code.claude.com/docs/en/claude-code-on-the-web.md] |
| Codex CLI, app, IDE | Machine | Persistent | ChatGPT mobile as remote; answers questions, keeps unanswered ones | [verified earlier: codex-others.md, changelog iOS 1.2026.286] |
| Codex cloud | OpenAI workspace per task | Per-task workspace; setup cached; record persistence not documented | Review from web, mobile, desktop | [verified: https://learn.chatgpt.com/docs/cloud] |
| Cursor IDE, CLI | Machine | Persistent | None documented for local sessions | [unverified] |
| Cursor cloud agents | Isolated cloud VM | Not stated | Cursor iOS app, cursor.com/agents (PWA on Android), Slack | [verified: https://cursor.com/docs/cloud-agent] |
| Devin Desktop, CLI | Machine; `/handoff` sends to cloud Devin | Persistent locally | Cloud Devin web [unverified] | [verified: https://docs.devin.ai] |
| VS Code Copilot, other IDEs | Machine | Persistent | None | [unverified] |
| Copilot cloud agent | Cloud sandbox or GitHub Actions; 59-minute cap on Actions | Fresh per session; dotfiles bring skills only into cloud sandbox | GitHub Mobile can start tasks (paid plan from 28 Oct 2026) | [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent] |
| Gemini CLI, Aider, Cline, Roo, Zed, OpenCode, goose, Droid | Machine | Persistent | None documented | [unverified] |
| JetBrains AI, Junie | Machine (ACP agents not in WSL) | Persistent | None documented | [verified: acp page] |
| Amp | Machine, or ampcode.com in the browser | [unverified] | macOS, iOS and Android apps | [verified: https://ampcode.com/manual] |
| Kiro | IDE, CLI, Web share one engine | [unverified] | [unverified] | [verified: https://kiro.dev/docs/ide/] |

---

## 8. The largest common denominator, and the tiers above it

### 8.1 The floor (tier 0): text, a file, and a shell

Every surface in this report can do these three things:

1. Read an instruction file (AGENTS.md, or the agent's own file).
2. Run a shell command in the project, except unattended cloud agents with a
   locked network, which can still run a locally installed binary.
3. Show text and accept the user's next message.

That is enough for every learning outcome, done slowly: the agent asks a
prediction in chat, the user types the answer in chat, the agent runs
`learn answer` to record it. Aider sits here and only here.

### 8.2 Tier 1: Agent Skill plus MCP tools

Reaches every surface except Aider. The skill carries the teaching method with
progressive disclosure. The MCP server carries state and secrets: it holds the
rubric so the learner never sees it before answering, locks answers with a
timestamp, picks due reviews, and enforces "at most 3 due a day". Using MCP
tools instead of shell commands also stops the rubric showing in the
transcript, which the earlier round flagged [verified earlier: protocols.md
finding 9].

MCP tools are the only interactive primitive that Copilot cloud agent supports
[verified: Copilot cloud agent MCP page]. So the core tool set must work with
tools alone: no prompts, no resources, no elicitation required.

### 8.3 Tier 2: hooks

Reaches Claude Code, Codex, Cursor (local and cloud), Devin, Copilot CLI, app,
VS Code and cloud agent, Gemini CLI, Kiro, Amp, OpenCode and Cline. Missing in
Copilot for Visual Studio, JetBrains, Eclipse and Xcode, in Zed's own agent,
Junie, Roo, goose and Aider. Hooks make the learning moments arrive on time
without the model remembering to call the tool. Without hooks, the instruction
file and skill must carry the timing, which is less reliable and needs to be
measured.

### 8.4 Tier 3: a native question inside the turn

MCP elicitation form (Claude Code, Codex, Cursor, VS Code Copilot), ACP
elicitation (Zed external agents, JetBrains ACP agents), or the agent's own
ask-user tool, which the skill can tell the model to use: `AskUserQuestion` in
Claude Code [verified earlier: claude.md], `request_user_input` in Codex
[verified earlier: codex-others.md], `ctx.ui.input` and `select` in an Amp
plugin [verified: Amp plugins page]. Where none exists the question is plain
chat.

### 8.5 Tier 4: designed UI

MCP Apps (Claude chat and Desktop chat, VS Code Copilot, Cursor, goose,
ChatGPT, maybe Codex app), Claude Code mods (CLI, desktop, VS Code), Amp plugin
UI, OpenCode Desktop GUI plugins, and a VS Code extension webview. Each is
optional. The learning card is designed once as HTML and served as an MCP App
`ui://` resource; the native mechanisms (mods, Amp UI) draw a simpler version
of the same card.

### 8.6 Tier 5: away from the keyboard

Daily reminder and phone answers. No common mechanism exists. Section 9.3
lists what is possible under the founder decisions.

### 8.7 Tier map

| Surface | T0 | T1 skill | T1 MCP tools | T2 hooks | T3 native ask | T4 designed UI | T5 phone |
| :- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Claude Code CLI, desktop, IDE | Y | Y | Y | Y | Y | Y (mods) | Y (Remote Control) |
| Claude Code cloud, phone | Y | Y | Y | Y | Y (cards) | N | Y |
| Codex CLI | Y | Y | Y | Y | Y | N | Y (ChatGPT mobile) |
| Codex app | Y | Y | Y | Y | Y | ? (MCP App panels) | Y |
| Codex cloud | Y | ? | ? | ? | N | N | Review only |
| Cursor IDE | Y | Y | Y | Y | Y | Y (MCP Apps) | N |
| Cursor cloud agents | Y | ? | Y | Y | ? | ? | Y (iOS, web) |
| Devin Desktop, CLI | Y | Y | Y | Y | ? | ? | ? |
| VS Code Copilot | Y | Y | Y | Y (preview) | Y | Y (MCP Apps, webview) | N |
| Copilot in VS, JetBrains, Eclipse, Xcode | Y | partial | Y | N | ? | N | N |
| Copilot CLI, app | Y | Y | Y | Y | ? | N | N |
| Copilot cloud agent | Y | Y | Y (tools only) | Y (subset) | N | N | Start and review on GitHub Mobile |
| Gemini CLI | Y | Y | Y | Y | N | N | N |
| Aider | Y | N | N | N (lint and test only) | N | N | N |
| Cline | Y | Y | Y | Y (macOS, Linux) | ? | ? | N |
| Roo Code | Y | Y | Y | N | ? | ? | N |
| Zed agent | Y | Y | Y (tools, prompts) | N | N | N | N |
| Zed or JetBrains with an ACP agent | Y | agent's own | Y | agent's own | Y (ACP elicitation) | N | N |
| Junie | Y | ? | Y | N | ? | N | N |
| Amp | Y | Y | Y | Y | Y (plugin UI) | Y (plugin UI) | Y (apps) |
| OpenCode | Y | Y | Y | Y | ? | Y (Desktop, experimental) | N |
| Kiro | Y | Y | Y | Y | ? | ? | ? |
| goose | Y | Y | Y | N | ? | Y (MCP Apps) | N |

Y = documented or tested; N = documented absent or no mechanism; ? = not
documented or untested. Every "?" is an experiment in section 11.

---

## 9. Founder decisions against the evidence

### 9.1 Decision 1 (local git record, no remote) meets cloud agents

**Challenge, with evidence.** On cloud surfaces the agent's disk does not
survive and there is no local machine. Claude Code cloud VMs are reclaimed
[verified: claude-code-on-the-web page]; Copilot Actions sessions end at 59
minutes [verified: about-cloud-agent page]; Cursor cloud agents run in VMs
[verified: cloud-agent page]. A record that lives only in a local repo with no
remote cannot be read or written there. These surfaces are a growing share of
use: every vendor in this report except Aider, Zed and the small CLIs ships one.
How large a share for our users needs to be measured.

I do not propose dropping the decision. I propose a narrow, explicit exception
the user switches on per surface:

- **Default (local surfaces):** the record is a local git repo. The engine
  commits to it. No remote.
- **Cloud surfaces, default:** the engine detects a cloud session (for example
  `$CLAUDE_CODE_REMOTE="true"` [verified earlier: claude.md]) and runs in
  "visitor mode". It keeps today's attempts in memory and writes them as one
  small file in the project branch under `.learning-inbox/` only if the user
  says yes once. The local engine imports and deletes it next time it sees the
  branch. The full record never leaves the machine. The inbox carries only new
  attempts. Rubrics stay sealed with a hash, as the earlier round proposed
  [verified earlier: protocols.md section 12].
- **Cloud surfaces, opt-in:** the user can add a private remote for the record.
  That is exactly the "unless the user explicitly asks" path in decision 1.

Without one of these, decision 6 (parity) fails on every cloud surface.

### 9.2 Decision 6 (feature parity on all surfaces)

**Challenge, with evidence.** Literal parity of mechanism is not possible:
Aider has no hooks and no documented MCP; Copilot cloud agent has MCP tools
only and no live user; Zed's agent has no elicitation; most local CLIs have no
phone path (tables in sections 4, 5, 7). I propose defining parity as **parity
of outcome**: every surface delivers every learning outcome (prediction before
a build, your line, explain-back, debugging drill, spaced review, the record,
the daily reminder), through the best mechanism that surface has. The product
then has one testable promise per outcome per surface, with a stated
mechanism, and a conformance test (section 10.6) that checks it.

### 9.3 Decisions 4 and 7 (one phone tap; one reminder a day at a chosen time)

The reminder must come from something that runs whether or not an agent is
open. With no remote, the only always-on piece is the user's own machine.

| Route | Reaches the phone? | Needs a remote? | Evidence |
| :- | :- | :- | :- |
| OS scheduler (launchd, systemd timer, Task Scheduler) runs `learn remind` at the chosen time and shows an OS notification | Laptop only | No | Standard OS facilities [unverified for our install path] |
| Claude Code `PushNotification` while Remote Control is active | Yes, Claude app | No (Anthropic relay) | [verified: https://code.claude.com/docs/en/mobile.md] |
| Cloud scheduled task in Claude, or a Codex or Cursor equivalent | Yes | Needs the record or the due list in a repo the cloud can clone | [verified earlier: claude.md section 5] |
| Web Push to an installed page | Yes | Needs a sender with a VAPID key and the subscription; a remote of the due list, not of the record | [verified earlier: protocols.md section 7] |
| ntfy or similar relay | Yes | Third-party relay; send only "1 review due", never question text | [verified earlier: protocols.md section 8] |

Recommendation: the local OS scheduler is the default reminder, since it needs
nothing. A phone reminder is an opt-in per vendor, using that vendor's own app
where it exists, and it sends only a count, never question content. The one
confirmation tap (decision 4) is where the phone route needs it: iOS requires a
user gesture to allow Web Push [verified earlier: protocols.md section 7], and
Remote Control needs the user to open the session.

### 9.4 Decision 2 ("your line") is the most portable feature we have

It needs no protocol at all. The agent writes the build, leaves one marked line
for the learner (for example a comment `LEARN(you): ...` that the language's
linter tolerates), and records the attempt. Every surface can do it, including
Aider and Copilot cloud agent, where the line simply waits in the PR. A turn-end
hook (where hooks exist) checks that the agent did not fill the line itself, and
a pre-commit check run by `learn` catches it everywhere else. Cloud agents that
open a PR should list the line in the PR body, since the user meets it there.

### 9.5 Decisions 3 and 5

"At most 3 due reviews a day" is enforced in the engine, so it holds on every
surface by construction. "Letter shortcuts off by default" matters only on
surfaces where we draw UI: Claude Code mods support hotkeys typed into an empty
prompt [verified earlier: claude.md section 2.3]; MCP Apps and Amp plugin UI
follow the host's focus rules. Our UI must not register letter keys unless the
user turns them on.

---

## 10. Architecture: write once, run on every agent

### 10.1 Shape

```
            one source repo
                  |
        +---------+----------+
        |                    |
   learn engine         adapters (generated)
   (one program)        per agent: manifest, hook map,
        |               config snippet, skill copy
        |
  +-----+------+--------+---------+----------+
  |     |      |        |         |          |
 CLI   MCP    hook    local     scheduler   record
       server dispatch page               (local git repo)
```

The engine is one installable program, `learn`. Everything else is a thin
adapter generated from one description at build time. No adapter holds logic.

### 10.2 The engine's five faces

1. **CLI.** `learn status`, `learn ask`, `learn answer`, `learn due`,
   `learn mine` (your line), `learn remind`. The tier 0 floor, and what every
   other face calls.
2. **MCP server.** `learn mcp` over stdio, both protocol revisions. Core tools
   work with tools alone (Copilot cloud agent). It then upgrades by what the
   client declares: elicitation forms when `elicitation` is declared, an MCP
   App `ui://` card when the `io.modelcontextprotocol/ui` extension is declared
   [verified earlier: codex-others.md shows Codex forwards the extension only
   when the host declares it], prompts as `/learn` and `/review` where prompts
   work, and later the Skills extension to serve the skill itself.
3. **Hook dispatcher.** `learn hook <agent> <event>`. Canonical events:
   `session_start`, `prompt_submit`, `before_tool`, `after_tool`,
   `tool_failed`, `turn_end`, `session_end`. A per-agent table maps names and
   output shapes (section 5).
4. **Local page.** `learn page` on `127.0.0.1` for the richer review and
   record view on the laptop. Also the target of MCP URL-mode elicitation on
   local surfaces [verified earlier: protocols.md section 2.2].
5. **Scheduler.** `learn remind --install` writes one OS timer at the user's
   chosen time (decision 7).

### 10.3 Install

`learn setup` detects which agents are installed (by their config folders, such
as `~/.codex`, `~/.cursor`, `~/.gemini`, `~/.claude`) and, with one
confirmation per agent, writes:

- the skill to `~/.agents/skills/learning-while-building/`, plus copies where
  an agent does not read that path (`~/.claude/skills/`, `~/.cline/skills/`,
  `~/.copilot/skills/`);
- one MCP server entry in each agent's config;
- that agent's hook file, calling `learn hook <agent> <event>`;
- nothing in the project until the user starts learning in it. Then a
  three-line AGENTS.md block (and a CLAUDE.md import line if CLAUDE.md exists).

For marketplaces, the same build emits native packages: a Claude Code plugin,
a Codex plugin, a Cursor plugin, a Gemini CLI extension, a Kiro power, an Amp
plugin, an OpenCode npm plugin, a Devin plugin, and a Cline MCP Marketplace
listing. Each package installs or calls the same engine. Package count is not
the cost; drift is. One manifest description and a generator remove drift.

### 10.4 Runtime negotiation

At session start the engine learns where it is from three signals: the MCP
client's name and declared capabilities, the hook payload's shape, and known
environment variables (for example `$CLAUDE_CODE_REMOTE` and
`$CLAUDE_CODE_BRIDGE_SESSION_ID` [verified earlier: claude.md section 2.2]). It
picks the highest tier available and always returns complete text as well, so
a wrong guess degrades to tier 0, never to a broken screen.

### 10.5 Where the learning logic lives

In the engine and the skill, never in an adapter. The engine owns state,
rubrics, scheduling and limits. The skill owns how to teach. Adapters own only
"how does this agent spell session start". This is the property that makes
parity of outcome testable.

### 10.6 Conformance suite

One scripted session per agent per release: start a session, request a build,
check a prediction is asked before the first edit, check a your-line marker
appears and survives the agent's turn, answer it, check the record commit,
check a due review appears next session and that no more than 3 appear. Run
each agent headless where it allows (Claude Code `-p`, Codex `exec` or app
server, Gemini CLI non-interactive, Copilot CLI). Surfaces with no headless
mode get a manual checklist. Pass rates per surface need to be measured.

### 10.7 What I would not do

- Build on MCP sampling: deprecated [verified earlier: MCP 2026-07-28 post].
- Make MCP Apps the main UI: not rendered in Claude Code or Codex CLI
  [verified earlier: protocols.md finding 3].
- Rely on `.claude/` paths for other agents: helpful today, not a standard.
- Write a proxy agent that wraps other agents (the ACP idea in protocols.md):
  it reaches only ACP editors and adds a second place for logic.
- Put long rules in AGENTS.md: every session of every agent pays for them.

---

## 11. Cheapest experiments, in order

| # | Question | Experiment | Time |
| :- | :- | :- | :- |
| 1 | Does one `.agents/skills/` folder load unchanged in Codex, Cursor, VS Code Copilot, Gemini CLI, OpenCode, Amp, Zed, Roo, goose and Devin? | Install the current skill there; ask each "make this a learning task"; record whether it activates | Needs to be measured; under an hour per agent is a guess |
| 2 | Does a tools-only MCP server cover the core loop in Copilot cloud agent? | Repository MCP config with `learn mcp`; assign an issue; check the PR body lists the your-line marker | One task |
| 3 | Which hosts render the MCP App card today? | One tool with `_meta.ui.resourceUri` in Codex app, Cursor, VS Code, goose, Claude Desktop chat | One sitting |
| 4 | Do elicitation forms work in Cursor, Devin Desktop, Cline, Kiro, OpenCode, Copilot CLI? | Reuse the earlier probe server from protocols.md | One sitting |
| 5 | Can the hook dispatcher map turn end to "continue with the explain-back" in Codex, Cursor, Gemini CLI, Amp, Copilot CLI, Devin? | One hook per agent that continues once with a fixed prompt | One sitting |
| 6 | Does visitor mode survive a Claude Code cloud session that expires? | Answer one question, let the VM be reclaimed, reopen, check the inbox file in the branch | One day of waiting |
| 7 | What does the Cline extension hook system expose, and on which OS? | Read the official hooks page once it is reachable; test on macOS | Short |
| 8 | Which agents read Agent Skills served over the MCP Skills extension? | Serve the skill over MCP; check each host | After SEP-2640 host support ships |

---

## 12. Standards landscape

| Standard | What it covers | Steward | Status | Evidence |
| :- | :- | :- | :- | :- |
| MCP | Tools, prompts, resources, elicitation, tasks; 2026-07-28 revision current | AAIF (Linux Foundation) | Stable | [verified earlier: MCP release post]; stewardship [unverified: press] |
| MCP Apps (`io.modelcontextprotocol/ui`) | Interactive HTML in hosts | MCP extension | Official extension; host support varies | [verified: https://modelcontextprotocol.io/extensions/apps/overview.md] |
| MCP Skills extension | Serve SKILL.md over MCP | Skills Over MCP Working Group | SEP-2640 Final; hosts implementing | [verified: https://modelcontextprotocol.io/extensions/skills/overview.md] |
| AGENTS.md | Project instruction file | AAIF (Linux Foundation) | Widely read | [verified: https://agents.md] |
| Agent Skills | SKILL.md folder format | Open standard, originally Anthropic, at agentskills.io | Widely read | [verified: https://agentskills.io]; AAIF membership [unverified] |
| goose | Reference open agent | AAIF | Project | [unverified: press] |
| Agent Client Protocol | Editor to agent JSON-RPC; elicitation stable | Zed-led [unverified] | JetBrains ACP registry in use | [verified: https://www.jetbrains.com/help/ai-assistant/acp.html]; [verified earlier: ACP announcement] |
| A2A, AG-UI | Agent to agent; agent to UI | A2A under the Linux Foundation [unverified] | Not reachable from coding agents | [verified earlier: protocols.md section 6] |

AAIF platinum members reported at launch: Amazon Web Services, Anthropic,
Block, Bloomberg, Cloudflare, Google, Microsoft and OpenAI [unverified: press,
https://www.phoronix.com/news/Linux-Foundation-Agentic-AI]. I could not load a
member list from https://aaif.io. The practical reading: building on MCP,
AGENTS.md and Agent Skills puts us on the three formats every large vendor in
this report has committed to.

---

## 13. Sources read this session

- https://agents.md
- https://agentskills.io and https://agentskills.io/clients.md (client list did not render)
- https://modelcontextprotocol.io/extensions/apps/overview.md
- https://modelcontextprotocol.io/extensions/client-matrix.md
- https://modelcontextprotocol.io/extensions/skills/overview.md
- https://code.claude.com/docs/en/memory.md
- https://code.claude.com/docs/en/claude-code-on-the-web.md
- https://code.claude.com/docs/en/mobile.md
- https://learn.chatgpt.com/docs/hooks
- https://learn.chatgpt.com/docs/cloud
- https://learn.chatgpt.com/docs/build-plugins
- https://cursor.com/docs/context/mcp
- https://cursor.com/docs/context/rules
- https://cursor.com/docs/agent/hooks
- https://cursor.com/docs/cloud-agent
- https://cursor.com/docs/plugins
- https://docs.devin.ai, https://docs.devin.ai/llms.txt, https://docs.devin.ai/_llms/en/desktop.txt
- https://docs.devin.ai/desktop/cascade/hooks
- https://docs.devin.ai/desktop/devin-local/customizations.md
- https://docs.devin.ai/cli/extensibility/hooks/overview.md
- https://docs.devin.ai/cli/extensibility/skills/overview.md
- https://docs.devin.ai/cli/extensibility/rules.md
- https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- https://docs.github.com/en/copilot/concepts/agents/hooks
- https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent
- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp
- https://code.visualstudio.com/api/extension-guides/ai/mcp
- https://geminicli.com/docs/extensions/
- https://geminicli.com/docs/tools/mcp-server/
- https://geminicli.com/docs/hooks/reference/
- https://zed.dev/docs/ai/skills
- https://zed.dev/docs/ai/mcp
- https://www.jetbrains.com/help/ai-assistant/junie-agent.html
- https://www.jetbrains.com/help/ai-assistant/acp.html
- https://ampcode.com/manual
- https://ampcode.com/docs/customize/plugins
- https://ampcode.com/docs/customize/skills
- https://opencode.ai/docs/skills/
- https://opencode.ai/docs/plugins/
- https://kiro.dev/docs/ide/
- https://kiro.dev/docs/hooks/
- https://docs.cline.bot/customization/skills
- https://docs.cline.bot/sdk/plugins.md
- https://docs.cline.bot/mcp/mcp-marketplace.md (search snippet)
- https://roocodeinc.github.io/Roo-Code/features/skills
- https://goose-docs.ai/docs/guides/context-engineering/using-skills
- https://aider.chat/docs/config/options.html
- https://aider.chat/docs/usage/conventions.html
- Press on AAIF and the Windsurf rename, as cited inline (all [unverified])
