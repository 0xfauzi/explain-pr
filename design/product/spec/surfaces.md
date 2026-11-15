# Spec: surfaces, parity and conformance

Part of `../PRODUCT.md`. Tier facts come from `../research/surfaces.md` section 8.7. The engine side of each mechanism is in `architecture.md`: trigger detection in section 5, the Room in section 8, install in section 9. On-screen wording and command names are in `experience.md`.

---

## 1. Parity of outcome

Founder decision: the same learning outcome on every coding agent surface. The mechanisms differ too much for the same features everywhere, so the product commits to **parity of outcome**: each outcome below is reachable on every surface with a local machine and recorded the same way.

This works because of how the model in `learning.md` is built. The check is an engine command that needs only a local shell and git. The answer is scored the same wherever it is typed, because the key is a fact the agent cannot change. The agent is needed only to say when a break happened, and git watch covers most of that.

| # | Outcome | Floor mechanism, present everywhere |
| :- | :- | :- |
| O1 | Be asked a question at a break, with why-now and "skip ok" | The skill tells the agent to call `moment` at five named breaks. Git watch catches the done family |
| O2 | Answer it, in the chat or out of it | A chat reply, or the Room on this computer |
| O3 | Have the call checked against what happened | The check runner, on the local machine |
| O4 | See the result: what you said, what happened, the cue, back to the build | The same lines in the chat and the Room |
| O5 | Get hazard lines, fact lines and notes with no question | The engine's line in the chat. The Room inbox |
| O6 | Have a finding reach the build | One line to the agent after the lock. A failing test as a patch on a tap |
| O7 | Do due reviews within the cap | The Room, or `firsthand review` |
| O8 | See the journal, the system view and the skills | The Room, or `firsthand journal` and `firsthand skills` as text |
| O9 | Quiet and off controls, and one-word skip | The words "skip", "quiet", "firsthand off" |
| O10 | Land in the one record | The daemon writes |
| O11 | Review a pull request or an imported branch before its description | `firsthand pr`, `firsthand import` |
| O12 | Drills | The Room. Old commits need a container runtime |
| O13 | Your line, at Deep | A text box in the Room, run in a scratch copy |

A richer tier changes timing and convenience, never the outcome. A cloud session has no local machine: it asks nothing, and its work is reviewed at the next local session through `firsthand import` (`architecture.md` section 10).

At install, and in the "What works here" note, the product says in one line what this agent gives: which breaks the engine sees itself and which depend on the agent reporting them.

---

## 2. Tiers

| Tier | Mechanism | What it adds |
| :- | :- | :- |
| T0 | Instruction file or skill, and a shell | The whole loop. The agent reports breaks with `firsthand moment` and passes replies with `firsthand answer` |
| T1 | MCP tools | No shell quoting. The question line comes back as a tool result |
| T2 | Hooks | Breaks seen when they happen, without relying on the model. The prompt captured verbatim, which gives the task's base. Hazard lines before a command runs. Replies read directly |
| T3 | Inline card: MCP Apps, or the agent's own plug-in UI | The question card drawn in the conversation |
| Room | The engine's local web app | Answers out of the chat, results, the journal, the system view, skills, drills |
| Phone | The Room, paired on the same network | Reviews and questions away from the keyboard |

Git watch is not a tier. It runs on every surface with a local repo.

The engine detects tiers at run time and always returns complete text. It speaks both MCP revisions (2025-11-25 and 2026-07-28) [verified: research/surfaces.md]. It does not use MCP sampling and never needs MCP Apps [verified: research/surfaces.md 10.7]. It does not use MCP or ACP elicitation: the chat reply, the Room and the inline card cover the need.

**At a turn end** a hook agent cannot relay a line without a new model turn. The question then reaches the person through the inline card, the hook's user-visible message, an OS notification or the Room (`architecture.md` section 5.5). Each adapter manifest records which of these the agent has.

---

## 3. Surface table

"Build step" is the order adapters are built in.

| Surface | T0 | T1 | T2 | T3 | Build step |
| :- | :-: | :-: | :-: | :-: | :- |
| Claude Code CLI, desktop, IDE | Y | Y | Y | Y (mods) | First (`build-2.md`) |
| Codex CLI and app | Y | Y | Y | ? | Second |
| Cursor IDE | Y | Y | Y | Y | Second |
| VS Code Copilot | Y | Y | Y (preview) | Y | Third |
| Copilot CLI | Y | Y | Y | N | Third |
| Gemini CLI | Y | Y | Y | N | Third |
| Devin Desktop and CLI, Amp, OpenCode, Kiro, Cline | Y | Y | Y | varies | Third |
| Copilot in VS, JetBrains, Eclipse, Xcode | Y | Y | N | N | Floor |
| Roo Code, goose, Junie, Zed agent | Y | Y | N | goose: MCP Apps | Floor |
| Aider | Y | N | N | N | Floor |
| Any cloud session (Claude Code web, Codex cloud, Cursor cloud agents, Copilot cloud agent) | | | | | No engine runs there. `firsthand import` at the next local session |

A "?" is not yet known. It is filled in when that adapter is built and recorded in the adapter manifest.

Sources per row are as in `../research/surfaces.md` section 8.7, including: Claude Code hooks [verified: https://code.claude.com/docs/en/hooks]; Codex hooks [verified: https://learn.chatgpt.com/docs/hooks]; Cursor hooks [verified: https://cursor.com/docs/agent/hooks]; Copilot customization [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet]; Gemini CLI hooks [verified: https://geminicli.com/docs/hooks/reference/]; Devin hooks [verified: https://docs.devin.ai/desktop/devin-local/customizations.md]; Aider options [verified: https://aider.chat/docs/config/options.html].

"Floor" means the instruction file, git watch and the Room, with a conformance run where the agent can be scripted.

Vendor learning modes (such as Claude Code's Learning output style) are not read. They work at the level of code lines, which this product does not train.

---

## 4. Install scope

The steps and the per-agent file table are in `architecture.md` section 9. The rules:

- `init` installs only into the agent it was launched from. Each further agent needs its own yes (`firsthand add <agent>`, or Settings in the Room).
- `init` writes user-level locations only. Where an agent has no user-level location for hooks or instructions, the engine asks once per repo whether to add it. Default no.
- It never writes a project's AGENTS.md, CLAUDE.md, `.cursor/`, `.claude/` or skills folder without a per-repo yes, and never asks the person to commit anything of Firsthand's.
- Before writing, it prints each path. Backups are byte-exact.
- Hook and MCP entries call an absolute pinned path (`security.md` section 3).

The instruction block is the same on every agent and is short. It says: call `moment` at task start, on a failure the person is present for, when asking the person to choose, before a risky step and when done. Print the engine's line unchanged. Pass a reply to `answer` unchanged. Treat "skip" as final. Never answer a question for the person. Never read `~/.firsthand`.

---

## 5. Your line: Deep only

Your line exists on Invariant, Missing case and the Replay drill, at the Deep setting. It is the same on every surface, because it does not happen in the agent.

- The Room shows a text box. The person writes a test, a constraint or a fix.
- The engine applies it in a scratch copy and reruns the check. The project is not touched.
- "Send to my agent" hands the line to the build as a patch, on a tap.
- No markers are placed in the project and no pre-commit hook is used.

---

## 6. Pressure and quiet per tier

- T2: the engine reads prompts from the prompt-submit hook and the branch from git.
- T0 and T1: the engine reads the branch on any call and at each git watch poll. Prompt pressure depends on the agent following the skill.
- "skip", "quiet" and "firsthand off" work on every surface. Conformance tests them on every row.
- No hook holds a tool call or refuses to end a turn.

---

## 7. MCP tools

| Tool | Purpose | Returns to the agent | May widen? |
| :- | :- | :- | :- |
| `moment` | The agent reports a break: `task_start`, `failure`, `options`, `risky_step`, `done` | "Nothing", or one line to print unchanged. For `risky_step`: the hazard line. Never a result before the lock | n/a |
| `answer` | Passes on a reply the person typed in chat, unchanged | The result lines to print unchanged, or "Locked. Shown when <event>." | n/a |
| `result` | Fetches what is waiting for the agent: a finding after a lock, a done-check line, or the path of a patch the person sent | One line or a path | n/a |
| `due` | Whether anything waits in the Room, with the link. Not its content | A count | n/a |
| `skills` | The skills as text | Text | n/a |
| `config` | Dial down, quiet, lower a limit | The new setting | Narrow only |

There is no tool that reads a key or changes a level. Widening is done in the Room on the person's computer. Each tool is mirrored as a CLI subcommand.

---

## 8. Conformance

Model behaviour varies between runs, so each adapter is tested by running it, many times, on every release.

- One scripted session per agent on a fixture project with known check results, run in CI through each agent's headless mode where it has one (Claude Code `-p`, Codex `exec`, Gemini CLI non-interactive, Copilot CLI [verified: research/surfaces.md 10.6]). A manual checklist where it does not.
- Checks O1 to O13, plus:
  - the done signal fires from hooks alone, from `moment done` alone, and from the commit backstop alone;
  - the first event of a session is in the spool and sets the base;
  - no result appears in the agent's context before the lock, skip or close;
  - the question line is printed unchanged, with why-now, "skip ok" and the link, and the link holds no credential;
  - a chat reply and a Room answer to the same fixture question produce the same score;
  - the daily limit holds across two agents writing one record, and a skip uses its slot;
  - nothing is printed on the first prompt of a day;
  - no hook holds a tool call, refuses to end a turn or returns a permission decision;
  - a hazard line is printed for a fixture command that points at a non-local database;
  - the project's working tree, index, refs and object store are byte-identical before and after every check;
  - the accessibility items in `experience.md` section 12;
  - the security checks in `security.md` section 8.
- Each outcome runs repeatedly per release and is reported as a pass rate. The table is public. A row never shows "supported" until it has run.
- Facts per agent that the research left open (whether a turn-end hook can show a line to the person, whether it carries the final message, hook latency) are recorded in the adapter manifest when the adapter is built.

---

## 9. Packaging and install channels

All adapters are generated from one manifest: Claude Code plugin, Codex plugin, Cursor plugin, Gemini extension, Kiro power, Amp plugin, OpenCode npm package, Devin plugin, Cline MCP listing (research/surfaces.md section 10). A directory-distributed plugin contains only the skill text and points to the pinned engine, so a directory auto-update cannot change hooks.

Install channels: PyPI first (`uvx firsthand init`), then each agent's plugin directory, the MCP registry and Homebrew [unverified: directory rules].
