# Spec: surfaces, parity and conformance

Part of `../PRODUCT.md` (section 5.4). Tier facts come from `../research/surfaces.md` section 8.7. A "?" there is untested and is an experiment (E6). Red-team items are cited as "RT efficacy n" and so on.

---

## 1. The parity model

Founder decision 6 asks for feature parity on all surfaces. This spec challenges it explicitly, on evidence (`../PRODUCT.md` 5.4), and replaces it with **parity of outcome**: each outcome below is reachable on every surface, in plain text plus a CLI call, and recorded identically.

| # | Outcome | Floor mechanism |
| :- | :- | :- |
| O1 | Be asked at a breakpoint, with why-now and skip | The skill tells the agent to call `moment` at named breakpoints |
| O2 | Answer with confidence, locked before reveal | The pad, or a chat reply relayed through `answer` |
| O3 | Be graded against a sealed key | Engine grader providers |
| O4 | Write your line, graded by tests, with a delayed hidden-test review | Marker comment plus `line check` |
| O5 | Review due items within the cap | `due` tool or `firsthand review` |
| O6 | See the map | `map` tool or `firsthand map` |
| O7 | Quiet and off controls | `config` tool or `firsthand quiet` |
| O8 | Every exchange ends with the resume cue | Engine-written text |
| O9 | Land in the one record | Engine writes, or the import line |
| O10 | **Answers that can count toward a level** | The pad, on any surface with a local terminal (RT efficacy 15) |
| O11 | Review an agent's PR before its summary | `moment pr_review`, or `firsthand pr` |

What a richer tier changes is speed and integrity, never the outcome. Integrity is shown, not hidden: a relayed answer is labelled and counts as Met (`learning.md` section 5.4). On surfaces with no local terminal (Copilot cloud agent, cloud-only web sessions, vendor phone apps), O10 is reached at the user's next local session, through the pad, on the items queued there.

The product says what each surface can count, in one line, at install, at the session-start offer and on `map all`.

---

## 2. Tiers

| Tier | Mechanism | What it buys |
| :- | :- | :- |
| T0 | Instruction file, skill folder, shell | The whole loop; answers relayed unless the pad is open |
| T1 | MCP tools only | No shell quoting; works on Copilot cloud agent [verified: research/surfaces.md] |
| T2 | Hooks | Breakpoints without model goodwill; verbatim prompt capture ("captured"); engine-read pressure; agent-edit attribution; visibility of agent tool events during Call it |
| T3 | Native ask: MCP or ACP elicitation | Answer straight to the engine. Counts as typed only where verified that the content does not reach the model [unverified per host] |
| T4 | Designed UI: MCP Apps, plugin UI | Map and cards inline |
| T5 | Away from keyboard | Vendor phone apps (relayed) |
| Pad | Engine-owned terminal prompt | Typed provenance on any surface with a local terminal |

The engine detects tiers at run time and always returns complete text. It speaks both MCP revisions (2025-11-25 and 2026-07-28) [verified: research/surfaces.md]. It does not use MCP sampling and never needs MCP Apps [verified: research/surfaces.md 10.7].

---

## 3. Surface table

"Counts" says which channels can move a level on that surface, in v1.

| Surface | T0 | T1 | T2 | T3 | T4 | T5 | Counts | v1 level |
| :- | :-: | :-: | :-: | :-: | :-: | :-: | :- | :- |
| Claude Code CLI, desktop, IDE | Y | Y | Y | Y | Y (mods) | Y | Pad, captured | Tested adapter |
| Claude Code web and phone | Y | Y | Y | Y (cards) | N | Y | Next local pad | Floor, untested (cloud) |
| Codex CLI | Y | Y | Y | Y | N | Y | Pad, captured | Tested adapter |
| Codex app | Y | Y | Y | Y | ? | Y | Pad, captured | Tested adapter |
| Codex cloud | Y | ? | ? | N | N | review only | Next local pad | Floor, untested |
| Cursor IDE | Y | Y | Y | Y | Y | N | Pad (terminal panel), captured | Tested adapter |
| Cursor cloud agents | Y | Y | Y | ? | ? | Y (iOS, web) | Next local pad | Floor, untested |
| VS Code Copilot | Y | Y | Y (preview) | Y | Y | N | Pad, captured | v1.1 |
| Copilot CLI | Y | Y | Y | ? | N | N | Pad, captured | v1.1 |
| Copilot in VS, JetBrains, Eclipse, Xcode | Y | Y | N | ? | N | N | Pad | Floor, known gap: no hooks |
| Copilot cloud agent | Y | Y (tools) | Y (subset) | N | N | GitHub Mobile | Review first at PR time, local pad | Floor, known gap: no live user |
| Gemini CLI | Y | Y | Y | N | N | N | Pad, captured | v1.1 |
| Devin Desktop and CLI | Y | Y | Y | ? | ? | ? | Pad, captured | v2 |
| Amp | Y | Y | Y | Y | Y | Y | Pad, captured | v2 |
| OpenCode | Y | Y | Y | ? | Y (exp.) | N | Pad, captured | v2 |
| Kiro | Y | Y | Y | ? | ? | ? | Pad, captured | v2 |
| Cline | Y | Y | Y (macOS, Linux) | ? | ? | N | Pad, captured | v2 |
| Roo Code, goose, Junie | Y | Y | N | ? | goose: MCP Apps | N | Pad | Floor, untested |
| Zed agent | Y | Y | N | N | N | N | Pad | Floor, untested |
| Zed or JetBrains with an ACP agent | Y | Y | agent's own | Y (ACP) | N | N | Pad | Floor, untested |
| Aider | Y | N | N | N | N | N | Pad | Floor, untested |
| Vendor learning modes (`TODO(human)`) | n/a | n/a | n/a | n/a | n/a | n/a | Met only | Floor, untested (RT market 13) |

Sources per row are as in `../research/surfaces.md` section 8.7, including: Claude Code reads AGENTS.md only when no CLAUDE.md exists [verified: https://code.claude.com/docs/en/memory.md]; Codex hooks [verified: https://learn.chatgpt.com/docs/hooks]; Cursor hooks [verified: https://cursor.com/docs/agent/hooks]; Copilot customization [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet]; Gemini CLI hooks [verified: https://geminicli.com/docs/hooks/reference/]; Devin hooks [verified: https://docs.devin.ai/desktop/devin-local/customizations.md]; Aider options [verified: https://aider.chat/docs/config/options.html]. Devin Desktop being formerly Windsurf is per press [unverified].

Cloud rows are "Floor, untested" in v1 because the carry branch moves to v1.1 and the import line is the only cloud path in v1.

The vendor learning-mode row reads `TODO(human)` gaps left by Claude Code's Learning output style [verified that the feature exists: https://code.claude.com/docs/en/output-styles; marker stability unverified] as your-line events. It is best effort, with its own conformance check, and records Met.

---

## 4. Install scope

RT market 9 and RT privacy 3.

- `init` installs only into the agent it was launched from, detected from the parent process and environment markers. Run from a plain shell, it lists found agents and asks which, with none pre-selected.
- Each further agent needs its own yes, then or later (`firsthand add <agent>`).
- `init` writes user-level locations only: that agent's global instruction file, user skill folder, user MCP config and user hooks config. Where an agent has no user-level instruction file [unverified per agent], the engine asks once per repo whether to add the three-line block; default no.
- Never writes a project's AGENTS.md, CLAUDE.md, `.cursor/`, `.claude/` or skills folder without a per-repo yes.
- Before writing, it prints each path and the exact diff, with the instruction block's size and token estimate. Backups are byte-exact.
- Every adapter's file list is published in the repo and on the site.
- Hook and MCP entries call an absolute pinned path (`security.md` section 3).

---

## 5. Your line: attribution per tier

Same-session lines record Met, so attribution errors cannot inflate a level. The delayed hidden-test review is what counts, and it runs in the pad.

| Tier | How the engine knows who wrote the line |
| :- | :- |
| T2 hooks with edit events | `line open` records the region hash. Agent edits touching the region are `line.agent_edit` and treated as handed back |
| T1 MCP, no hooks | At each `moment` call the engine compares the region hash with the agent's reported edits. The user confirms with "line done". Provenance relayed |
| T0 shell only | `firsthand line done` or "line done"; the engine diffs the region |
| Cloud agent | Open lines stay in the session's import blob. Never listed in a PR body (RT privacy 7) |

**Scan after session.** At the next local session the engine reads its own recorded markers (by location and hash) and their outcomes from merged code, so Aider and cloud agents still feed the record.

**Pre-commit integration** is opt-in, as a snippet for husky, lefthook or the pre-commit framework, or a chained `core.hooksPath`. It never overwrites `.git/hooks` and never fails a commit. In shared repos it hands an open line back to the agent before the commit by default.

**Turn-end hooks** never refuse to end a turn.

---

## 6. Pressure and quiet per tier

- T2: the engine reads prompts from the prompt-submit hook and the branch from git.
- T0 and T1: the engine reads the branch on any call. Prompt pressure depends on the model following the skill. `init` says so.
- "quiet" and "learning off" work on every surface. Conformance tests them on every row.

---

## 7. MCP tools

| Tool | Purpose | May widen? |
| :- | :- | :- |
| `moment` | Agent reports a breakpoint (including `pr_review`), files edited, candidate picks; engine replies ask or stay quiet | n/a |
| `seal` | Separate context commits a question and key; returns the question only | n/a |
| `answer` | Records a relayed answer, confidence, help, format; locks it | n/a |
| `line` | open, check, done, hand back | n/a |
| `due` | Today's reviews within the cap | n/a |
| `map` | The map as text | n/a |
| `config` | Dial, quiet, reminder, budget, grader | Narrow only |
| `candidates` | The fixed candidate idea list for a diff | n/a |

Widening (raise the budget, add a grader provider, import, delete, consent, add a remote) is not offered as a tool. It is a CLI action that confirms in the pad (`security.md` section 7). Each tool is mirrored as a CLI subcommand.

---

## 8. Conformance

- One scripted session per agent per release, **run in CI** through each agent's headless mode where it has one (Claude Code `-p`, Codex `exec`, Gemini CLI non-interactive, Copilot CLI [verified: research/surfaces.md 10.6]); a manual checklist where it does not (RT market 6).
- Checks O1 to O11, plus: no key reaches the asking context before lock; the budget holds across two agents writing one record; no letter shortcuts; why-now, skip and resume lines present; accessibility items; the security checks in `security.md` section 14; the "what counts here" line is shown.
- Each outcome runs 10 times per surface per release and is reported as a pass rate (design default). A row is "Tested" when every outcome passes in at least 8 of 10 runs (threshold, a decision).
- A cost budget per release caps model spend on conformance (amount set by the founder).
- The table is public. A row never shows "supported" until it has run.

---

## 9. Packaging

All adapters are generated from one manifest: Claude Code plugin, Codex plugin, Cursor plugin, Gemini extension, Kiro power, Amp plugin, OpenCode npm package, Devin plugin, Cline MCP listing (research/surfaces.md section 10). A directory-distributed plugin contains only the T0 skill and points to the pinned engine, so a directory auto-update cannot change hooks (`security.md` section 3.4). Package names are reserved in v0 and confirmed by E0.
