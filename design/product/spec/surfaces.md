# Spec: surfaces, parity and conformance

Part of `../PRODUCT.md` (section 5.4). Tier facts come from `../research/surfaces.md` section 8.7. A "?" there is untested and is an experiment (E6).

---

## 1. The parity model

Founder decision 6 asks for feature parity on all surfaces. This spec challenges it explicitly, on evidence (`../PRODUCT.md` 5.4), and replaces it with **parity of outcome**: each of the outcomes below is reachable on every surface, in plain text plus a CLI call, and recorded identically.

| # | Outcome | Floor mechanism |
| :- | :- | :- |
| O1 | Be asked at a breakpoint, with why-now and skip | The skill tells the agent to call `moment` at named breakpoints |
| O2 | Answer with confidence, locked before reveal | Chat reply relayed through `answer`, or `firsthand answer` typed in a terminal |
| O3 | Be graded against a sealed key | Engine grader providers (architecture section 5) |
| O4 | Write your line, graded by tests | Marker comment plus `line check` |
| O5 | Review due items within the cap | `due` tool or `firsthand review` |
| O6 | See the map | `map` tool or `firsthand map` |
| O7 | Quiet and off controls | `config` tool or `firsthand quiet` |
| O8 | Every exchange ends with the resume cue | Engine-written text |
| O9 | Land in the one record | Engine writes, or cloud carry |

What a richer tier changes is speed and integrity, never the outcome. Integrity differences are shown, not hidden: an agent-relayed answer is labelled and capped at Seen (`learning.md` section 5).

---

## 2. Tiers

| Tier | Mechanism | What it buys |
| :- | :- | :- |
| T0 | Instruction file, skill folder, shell | The whole loop |
| T1 | MCP tools only (no prompts, no resources) | No shell quoting; works on Copilot cloud agent [verified: research/surfaces.md] |
| T2 | Hooks | Breakpoints without model goodwill; verbatim prompt capture (answer provenance "captured"); engine-read pressure; agent-edit attribution for your line |
| T3 | Native ask: MCP elicitation or ACP elicitation | Answer typed straight to the engine (provenance "typed"); candidate host for unseen questions |
| T4 | Designed UI: MCP Apps, plugin UI | Map and cards inline |
| T5 | Away from keyboard | Vendor phone apps |

The engine detects tiers at run time and always returns complete text as well. It speaks both MCP revisions (2025-11-25 and 2026-07-28) [verified: research/surfaces.md]. It does not use MCP sampling (deprecated) and never needs MCP Apps [verified: research/surfaces.md 10.7].

---

## 3. Surface table

| Surface | T0 | T1 MCP | T2 hooks | T3 ask | T4 UI | T5 phone | v1 level | Notes |
| :- | :-: | :-: | :-: | :-: | :-: | :-: | :- | :- |
| Claude Code CLI, desktop, IDE | Y | Y | Y | Y | Y (mods) | Y | Tested adapter | Reads AGENTS.md only when no CLAUDE.md exists [verified: https://code.claude.com/docs/en/memory.md] |
| Claude Code web and phone | Y | Y | Y | Y (cards) | N | Y | Tested adapter, cloud | `CLAUDE_CODE_REMOTE=true` marks cloud [verified: research/surfaces.md] |
| Codex CLI | Y | Y | Y | Y | N | Y | Tested adapter | Hooks [verified: https://learn.chatgpt.com/docs/hooks]; skills [verified: https://developers.openai.com/codex/skills] |
| Codex app | Y | Y | Y | Y | ? | Y | Tested adapter | MCP App panels untested |
| Codex cloud | Y | ? | ? | N | N | review only | Floor, untested | |
| Cursor IDE | Y | Y | Y | Y | Y | N | Tested adapter | followup_message hooks [verified: https://cursor.com/docs/agent/hooks] |
| Cursor cloud agents | Y | Y | Y | ? | ? | Y (iOS, web) | Floor, untested | Isolated VMs [verified: https://cursor.com/docs/cloud-agent] |
| VS Code Copilot | Y | Y | Y (preview) | Y | Y | N | v1.1 | MCP Apps and elicitation [verified: https://code.visualstudio.com/api/extension-guides/ai/mcp] |
| Copilot CLI | Y | Y | Y | ? | N | N | v1.1 | Hooks [verified: https://docs.github.com/en/copilot/concepts/agents/hooks] |
| Copilot in VS, JetBrains, Eclipse, Xcode | Y | Y | N | ? | N | N | Floor, known gap | No hooks [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet] |
| Copilot cloud agent | Y | Y (tools only) | Y (subset) | N | N | GitHub Mobile | Floor, known gap | No live user; your line listed in PR body; 59-minute sessions |
| Gemini CLI | Y | Y | Y | N | N | N | v1.1 | Hooks [verified: https://geminicli.com/docs/hooks/reference/]; no elicitation [verified: https://geminicli.com/docs/tools/mcp-server/] |
| Devin Desktop and CLI | Y | Y | Y | ? | ? | ? | v2 | Formerly Windsurf, per press [unverified]; hooks [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] |
| Amp | Y | Y | Y | Y | Y | Y | v2 | [verified: https://ampcode.com/docs/customize/plugins] |
| OpenCode | Y | Y | Y | ? | Y (experimental) | N | v2 | [verified: https://opencode.ai/docs/plugins/] |
| Kiro | Y | Y | Y | ? | ? | ? | v2 | [verified: https://kiro.dev/docs/hooks/] |
| Cline | Y | Y | Y (macOS, Linux) | ? | ? | N | v2 | |
| Roo Code, goose, Junie | Y | Y | N | ? | goose: MCP Apps | N | Floor, untested | |
| Zed agent | Y | Y | N | N | N | N | Floor, untested | No elicitation [verified: https://zed.dev/docs/ai/mcp] |
| Zed or JetBrains with an ACP agent | Y | Y | agent's own | Y (ACP) | N | N | Floor, untested | [verified: https://www.jetbrains.com/help/ai-assistant/acp.html] |
| Aider | Y | N | N | N | N | N | Floor, untested | No MCP, no hooks; lint and test commands only [verified: https://aider.chat/docs/config/options.html] |
| Claude chat, ChatGPT (no code agent) | n/a | Y | n/a | n/a | Y (MCP Apps) | Y | Later, review only | Optional review surface, not a build surface |

AGENTS.md is read by 23 listed agents [verified: https://agents.md]. The `.agents/skills/` path is read by Codex, Cursor, VS Code Copilot, Gemini CLI, Zed, Roo, Amp, OpenCode, goose and Devin [verified: research/surfaces.md section 3].

---

## 4. Install at user scope

- `init` writes to user-level locations only: each agent's global instruction file, user skill folder, user MCP config and user hooks config. Which user-level paths each agent supports is recorded per adapter; where an agent has no user-level instruction file [unverified per agent], the engine asks once per repo whether to add the three-line block, and the default is no.
- Never writes a project's AGENTS.md, CLAUDE.md, `.cursor/`, `.claude/` or skills folder without a per-repo yes.
- The three-line instruction block points to the skill. Long rules never go in instruction files, because every session of every agent pays for them (research/surfaces.md 10.7).
- `init` prints each found agent's support level and its known gaps in one line each.

---

## 5. Your line: attribution per tier

Because same-session lines cap at Seen, attribution errors cannot inflate a level. Attribution still matters for honesty and for `line.survived`.

| Tier | How the engine knows who wrote the line |
| :- | :- |
| T2 hooks with edit events | `line open` records the marker region hash. After-tool edit events show any agent edit that touches the region: recorded as `line.agent_edit` and treated as "handed back". Changes to the region not made through an agent tool are attributed to the user |
| T1 MCP, no hooks | At each `moment` call the engine hashes the region and compares with the last agent turn's recorded edits (the skill tells the agent to report files it edited). The user confirms with "line done", typed. Provenance: relayed |
| T0 shell only | The user runs `firsthand line done` or says "line done"; the engine diffs the region against the open hash. Provenance: relayed |
| Cloud agent opening a PR | The marker is listed in the PR body. The line is checked at next local session from the merged code ("scan after session", below) |

**Scan after session.** On any surface, the engine can read your-line markers and their outcomes from merged code, so surfaces with no MCP and no hooks (Aider, Copilot cloud agent) still feed the record.

**Pre-commit integration** is opt-in. It is offered as a snippet for the repo's existing manager (husky, lefthook, the pre-commit framework) or via a chained `core.hooksPath`. The engine never overwrites `.git/hooks`. The hook never fails a commit. It prints one line about an open marker and offers "write it".

**Turn-end hooks** on T2 surfaces never refuse to end a turn. If the agent filled the user's line, the hook records it as handed back and adds one line: `I filled your line in retry.py:42, so it counts as handed back.`

---

## 6. Pressure and quiet per tier

- T2: the engine reads prompts from the prompt-submit hook and the branch from git, and decides.
- T0 and T1: the engine reads the branch on any call (quiet patterns always work). Prompt pressure depends on the model following the skill. `init` says so for each such agent.
- Kill phrase: "quiet" and "learning off" work on every surface, through the `config` tool or the CLI. Conformance tests them on every row.

---

## 7. MCP tools (the core works with tools alone)

| Tool | Purpose |
| :- | :- |
| `moment` | Agent reports a breakpoint, files edited, candidate idea picks from the engine's list; engine replies ask or stay quiet, with full text |
| `seal` | Separate context commits a question and key; returns the question only |
| `answer` | Records answer, confidence and help; locks it; returns grade text or "graded later" |
| `line` | open, check, done, hand back |
| `due` | Today's reviews within the cap |
| `map` | The map as text; an MCP App where declared |
| `config` | Dial, quiet, reminder, budget |
| `candidates` | Returns the fixed candidate idea list for a diff |

Each tool is mirrored one to one as a CLI subcommand for hosts without MCP.

---

## 8. Conformance

- One scripted session per agent per release, run headless where the agent allows (Claude Code `-p`, Codex `exec`, Gemini CLI non-interactive, Copilot CLI [verified: research/surfaces.md 10.6]); a manual checklist where it does not.
- Checks O1 to O9, plus: no key reaches the asking context before lock; the budget holds across two agents writing one record; no letter shortcuts registered; the why-now, skip and resume lines are present; the accessibility gate items that apply.
- Runs are nondeterministic, so each outcome is run 10 times per surface per release and reported as a pass rate (design default). A row is "Tested" when every outcome passes in at least 8 of 10 runs (threshold, a decision). Below that, the failing outcome is listed as a known gap.
- A cost budget per release caps model spend on conformance (amount set by the founder).
- The table is public on the site. A row never shows "supported" until it has run.

---

## 9. Packaging

All adapters are generated from one manifest: Claude Code plugin, Codex plugin, Cursor plugin, Gemini extension, Kiro power, Amp plugin, OpenCode npm package, Devin plugin, Cline MCP listing (research/surfaces.md section 10). Package names are [unverified] until E0.
