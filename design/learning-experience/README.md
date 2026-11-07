# Learning while building: the plan

Status: plan, revised 7 Nov 2026 for a product anyone can install. Nothing here
is built yet. Open `index.html` for the visual summary. Serve this folder with
`python3 -m http.server` (or open it from the repo root or GitHub Pages) to step
through the prototypes.

## 1. What the experience is

You build with the agent in chat. At two moments in a task you choose to learn
from, the agent asks one question and keeps working: a prediction before it
builds, and "explain why it works" after it works. When you are new to an idea,
it can leave one marked line of the real build for you to write, and the tests
grade it. You answer in chat with one line, or in the Room: a local page beside the
session, and on the phone if you turn on sync. The same card is in every place,
in the same state. You say how sure you
are with every answer, and the agent grades against an answer key it fixed
before it asked. A prediction is compared ("You said / It did / The gap"), never
graded. Every exchange ends with one "Back to the build" and the line
`Back to: <task>. Next: <step>.` Days later the idea comes back in new words,
then in a new case. The Map shows what you can do without the agent, and it goes
down when you forget. A level goes up only at a spaced review, never in the
session where the agent wrote the code.

## 2. The product architecture

This is a product that anyone installs into the coding agent they already use.
It is not built for one person or one harness. Section 5 lists the decisions
behind it. The claude.ai artifact design in `architecture/recommended.md` is now
one optional adapter, not the default.

**Install.** One command installs the engine and the `lwb` command:
`uvx lwb` or `pipx install lwb` (Python, because the engine already exists in
Python). Then `lwb install` finds the coding agents on the machine and writes
the config each one reads: its MCP server entry, and the skill or rules file.

**Parts, in order of how much they are shared:**

| Part | What it is | Where it runs |
|---|---|---|
| Engine | Record, levels, review schedule, sealed answer keys, grading rules. From `record.py` and `learning.py`. | Every surface |
| `lwb` MCP server | stdio server with `lwb_post`, `lwb_lock`, `lwb_reveal`, `lwb_grade`, `lwb_hint`, `lwb_due`, `lwb_map`, `lwb_sync`. | Every agent that loads stdio MCP servers |
| Instructions | `SKILL.md` for agents that read Agent Skills. A generated rules file (`AGENTS.md` section, Cursor rule, and so on) for agents that do not. One source, several outputs. | Every agent |
| Chat text | The question as plain text in chat; the answer as one line. | Every surface. This is the floor. |
| Local Room | A web page that `lwb room` serves on 127.0.0.1 with a one-time token: Inbox, Card, Compare, Map, Drill, Settings. | Where the agent runs on the user's machine |
| Record | `~/.lwb/`, a local git repo. One commit per grade. No remote. | The user's machine |

**Opt-in, off by default:**

| Option | What it adds | Cost |
|---|---|---|
| Own git remote | The user adds a remote. The record syncs between machines and into cloud sessions. | None to us |
| lwb Sync | End-to-end encrypted sync. The service stores data it cannot read. Unlocks the phone app, the phone tap and one daily reminder. | A hosted service to build, run and secure |
| claude.ai Room | The artifact Room from the earlier design, for Claude app users. Its data is stored on claude.ai. | Already designed |

**Cloud sessions.** Claude Code on the web, Codex cloud and similar delete
their disk. `lwb init` detects this and says it before the first question:
"This session's disk is deleted later. Your record will be lost unless you
connect a remote." It then offers the user's own remote, lwb Sync, or a
download at the end. It never connects one without the user's answer.

**Feature parity.** Every learning event (prediction, explain-back, your line,
review, drill, explainer) works in chat text on every surface. The Room, the
phone and reminders are faster ways to do the same events, not extra events.
So parity means: the same events, the same record and the same levels
everywhere. It does not mean the same screens everywhere.

**One level rule everywhere:** "Levels change only at reviews: right without
help at a review a week or more after you first met the idea gives Without
help, and right on a case unlike any you have seen gives New situation."

## 3. What is tested, and what needs a test first

**Tested in this project, Claude Code only:** chat text cards in the Claude app
on desktop and phone; a project stdio MCP server from `.mcp.json`; the skill
deciding when to ask; union-merged JSONL with one file per attempt; the
claude.ai artifact Room with `db` and `sample`. Nothing is tested on any other
agent yet.

**Day-0 tests:**

| Test | The test | If it fails |
|---|---|---|
| E-PARITY | In Claude Code (CLI, desktop, IDE), Codex (CLI, app, IDE), Cursor, Gemini CLI and GitHub Copilot in VS Code: does `lwb install` config load, do the tools run, does the agent follow the instructions at the two moments? | That agent gets chat text through instructions only, and a documented gap. |
| E-LOCALHOST | Can the user open the local Room from each surface, including the desktop apps and remote IDEs? | Chat text there, and a link that prints the Room address. |
| E-EPHEMERAL | Can `lwb init` tell a disk that is deleted from one that stays, on each cloud surface? | Always ask once at `init`. |
| E-SEAL | Does the main agent stay blind to the answer key on each agent? | Write the key at grading time and keep only the hash for audit. |
| E-PERM | How many permission prompts does a fresh install cause on each agent? | `lwb install` writes each agent's allow list. Target: 0 after the first. |
| E-A11Y | Keyboard only and a screen reader, Room and chat. | Chat becomes the accessible default. |

I can run the Claude Code tests in this session. The other agents need their own
accounts and keys, so each one needs a key from you, or a machine where they
are installed.

## 4. Build order

Sizes are rough estimates, not measured.

| Step | What | Size |
|---|---|---|
| 0 | Day-0 tests above | 1 to 2 days, depending on account access |
| 1 | Engine: events with ids, reviews log, the level rule, daily cap 3, `import`, `export`, local git record with a commit per grade | 2.5 days |
| 2 | `lwb` MCP server and `lwb install` for each agent that passed E-PARITY | 3 days |
| 3 | Instructions: one source, `SKILL.md` and rules outputs; the moments, your line, question quality rules, rate rule | 1.5 days |
| 4 | Local Room from `assets/room.css` | 3 days |
| 5 | `lwb init`: cloud detection, the remote question; packaging and the install page on the site | 1 day |
| 6 | Opt-in: own git remote | 0.5 day |
| 7 | Opt-in: lwb Sync, the phone app, the phone tap, one daily reminder | Not sized. Needs its own design: hosting, keys, account recovery, abuse. |
| 8 | Opt-in: the claude.ai Room adapter | 2 days, design exists |

Steps 0 to 6 make a product anyone can install that works on every agent that
passes E-PARITY, with no service to run.

## 5. Decisions (7 Nov 2026)

| # | Decision |
|---|---|
| 1 | The record lives in a local git repo. The tool commits to it. It has no remote unless the user asks for one. |
| 2 | "Your line" is on. |
| 3 | At most 3 due cards a day. |
| 4 | One confirmation tap on the phone is acceptable. |
| 5 | Letter-key shortcuts are off by default. |
| 6 | Feature parity on every coding surface (Claude Code, Codex, and other agents), for general users, not one person. |
| 7 | At most one reminder a day, at a time the user chooses. |

**What decisions 1 and 6 change.** Sections 2 to 4 assumed the Room is a
claude.ai artifact and the record is pushed to a private repo. Both are now
wrong as defaults:

- A claude.ai artifact works only for Claude users, and its db is a remote. So
  the default Room becomes a local page that the `lwb` server serves on
  localhost. Chat text stays the floor that works everywhere. The claude.ai
  artifact becomes an optional adapter.
- The parity layer is MCP plus the Agent Skills format. Which harnesses load
  both, and how, must be tested per harness (E-PARITY).
- A cloud session deletes its disk. A local-only record there is lost. In a
  session whose disk does not persist, `init` must say so and ask where to keep
  the record (E-EPHEMERAL).
- The phone needs a path to the record. A local-only record has none. Phone
  review, the phone tap (4) and reminders (7) work only after the user turns on
  a remote. Without one, due cards show at the start of the next session.

## 6. Questions only you can answer (first round, answered above)

1. **Where should your record live** when a project is public: a private
   `learning-record` repo (needs a second repo attached to cloud sessions), or
   the Room only?
2. **"Your line":** do you want the agent to stop at one marked line for you to
   write at Not yet and With help? It slows a build by about a minute and is the
   strongest learning event in the design.
3. **Daily cap:** 3 due cards a day (the engine's current value) or more?
4. **Phone bell:** is one confirmation tap on the phone acceptable if the
   no-tap path (E-CCR-SEND) fails?
5. **Keys:** should letter-key shortcuts be on or off by default?
6. **Other harnesses:** how much of your work moves to Codex? If a lot, the phone
   page with a sealed mailbox (phase 3, item 4) moves ahead of the desktop mod.
7. **Pushes:** at most one a day, at a time you choose. Yes, or none?

## 7. Where the panel was not followed, and why

- **The bell as the hero of `index.html`** (product design). The hero shows
  phase 1, the pull on the next message, because that is what ships first. The
  bell is shown in `flow.html` with its experiment named.
- **The first prediction stays on retry timing** (learning science asked for a
  prediction on the timeout misconception). The rules the reviewer asked for are
  applied: the jitter is on the card, the test clock makes the result exact, and
  the gap names only what the card showed. `retry-budget` has no recorded
  misconception; the misconception topic, `timeouts-vs-failures`, is now the
  drill's planted bug and the next-day item after a sure miss.
- **One shared fixture file read by every prototype** (product design). The
  story is in `assets/orbit-pay.json` and every page now matches it, but each
  prototype still inlines its data so it opens on its own from any server.
  Tokens and grain are shared for real: every page links `assets/room.css` and
  `assets/grain.png`.
- **The Inbox has no "Back to the build" button.** The way back is drawn once,
  at the end of each learning exchange. The Inbox is not an exchange; it shows
  "Linked to orbit-pay · cloud session".
- **The explain-back keeps its verdict word** ("Correct.") while the level waits
  for the review. The word grades the answer; the level rule decides the record.
- **Grade appeal** is a quiet link on the verdict, not a full flow; the session
  looks again on the next message.

Everything else in the four reviews (all blockers and majors) is applied in
`experience.md`, `design-system.md`, `architecture/recommended.md`, `index.html`
and the eight prototypes. Each page was checked at 1440 and 390 wide: no
horizontal scroll at 390, no console errors, no em dashes.

## 8. Map of this folder

| Path | What it is |
|---|---|
| `README.md` | This plan. |
| `index.html` | The visual summary: hero, what seamless means, storyboard, the eight prototypes, how it ships. |
| `experience.md` | The product spec: decisions D1 to D18, principles, journeys a to j, every surface with exact copy, the prototype list. |
| `design-system.md` | Tokens, components, motion and accessibility rules (WCAG 2.2 AA). |
| `assets/room.css` | The shared tokens and base styles, light and dark. Inlined at build time into the Room and the explainer template. |
| `assets/grain.png` | Copy of the site's paper grain, so every page works from any server root. |
| `assets/orbit-pay.json` | The one story every page tells: dates, topics, cards, the level rule. |
| `architecture/recommended.md` | The chosen architecture: the card, the store, the moments, the Room, the transition engine, how answers get home, key privacy, phases, the dependency register, re-plan triggers. |
| `architecture/agent-native.md` | Proposal 1: harness-native, mod band and pane. Scored, partly adopted. |
| `architecture/companion.md` | Proposal 2: the Room and a companion app. Scored, partly adopted. |
| `architecture/protocol-bridge.md` | Proposal 3: protocol bridge and local daemon. Scored, partly adopted. |
| `research/learning-science.md` | The learning research, rules R1 to R38 and experiments E1 to E7. |
| `research/product-patterns.md` | Patterns from tools developers love: inbox, calm, notifications, onboarding. |
| `research/claude.md` | What Claude Code, the Claude app, artifacts and hooks can do, with evidence tags. |
| `research/codex-others.md` | The same for Codex, Cursor, Zed and others. |
| `research/protocols.md` | MCP, MCP Apps, elicitation, ACP and related protocols. |
| `critique/learning-scientist.md` | Panel review: learning science. |
| `critique/product-design.md` | Panel review: product design. |
| `critique/platform-engineering.md` | Panel review: platform engineering. |
| `critique/accessibility.md` | Panel review: accessibility. |
| `prototypes/flow.html` | Build and learn: chat at real harness fidelity (Claude Code, Codex, terminal) beside the Room on a phone. 14 states. |
| `prototypes/inbox.html` | The Room shell and Inbox. 16 states. |
| `prototypes/card.html` | The question card: every kind and shape, best guess, show the code as a hint, safe keys. 18 states. |
| `prototypes/verdict.html` | Compare with "The gap", verdicts under the level rule, decay, appeal. 11 states. |
| `prototypes/map.html` | The record, calibration with target bands, topic sheet, Growth. 16 states. |
| `prototypes/drill.html` | A debugging drill: hypothesis first, your check runs, then the reveal. 15 states. |
| `prototypes/explainer.html` | An explainer with neutral headings and questions before each section. 11 states. |
| `prototypes/onboarding.html` | First run in chat, the Room first open, Settings. 13 states. |
