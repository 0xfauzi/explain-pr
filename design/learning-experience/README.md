# Learning while building: the plan

Status: final plan, 7 Nov 2026, after the expert panel review. Nothing here is
built yet. Open `index.html` for the visual summary. Serve this folder with
`python3 -m http.server` (or open it from the repo root or GitHub Pages) to step
through the prototypes.

## 1. What the experience is

You build with the agent in chat. At two moments in a task you choose to learn
from, the agent asks one question and keeps working: a prediction before it
builds, and "explain why it works" after it works. When you are new to an idea,
it can leave one marked line of the real build for you to write, and the tests
grade it. You answer in chat with one line, or in the Room: a private claude.ai
page that opens beside the session on the laptop and in the Claude app on the
phone. The same card is in both places, in the same state. You say how sure you
are with every answer, and the agent grades against an answer key it fixed
before it asked. A prediction is compared ("You said / It did / The gap"), never
graded. Every exchange ends with one "Back to the build" and the line
`Back to: <task>. Next: <step>.` Days later the idea comes back in new words,
then in a new case. The Map shows what you can do without the agent, and it goes
down when you forget. A level goes up only at a spaced review, never in the
session where the agent wrote the code.

## 2. The recommended architecture, in short

- **One card, one store, many doors.** Each question is one card with one sealed
  answer key and one lock. Chat is the build surface. The Room (a claude.ai
  artifact with `db` and `sample`) is the learning surface on both devices.
- **A small stdio MCP server, `lwb`,** owns the card: `lwb_post` (seals and
  posts in one transcript row), `lwb_lock`, `lwb_reveal`, `lwb_grade`,
  `lwb_hint`, `lwb_sync` (reads the Room, checks hashes and the seal, imports,
  in one row), `lwb_due`, `lwb_map`.
- **The key is sealed by a subagent** that writes it from the code, so the main
  transcript and the main agent see only a hash.
- **The Room db has one writer per doc:** `cards/` (agent), `keys/` (agent,
  read once by the page after the answer exists), `answers/` (page, created once,
  with a sha256), `grades/` (page). The db is last-writer-wins, so this is what
  keeps answers from being lost.
- **The record is private and durable:** a private `learning-record` repo,
  committed and pushed after every grade. If that cannot work, the Room db is
  the system of record and `learning.py export` rebuilds the files.
- **Transitions:** skill rules in phase 1, hooks in phase 2. The bell from the
  phone is a ladder: Claude Code Remote `send_message`, then
  `sendToClaudeSession` with one confirmation tap, then the pull on the next
  message, which always works.
- **One level rule everywhere:** "Levels change only at reviews: right without
  help at a review a week or more after you first met the idea gives Without
  help, and right on a case unlike any you have seen gives New situation."

Full detail: `architecture/recommended.md`. Screens and copy: `experience.md`.
Tokens and components: `design-system.md`.

## 3. What can ship now, and what needs a test first

**Ships on tested parts** (verified in this project):

| Part | Evidence |
|---|---|
| Chat text cards in Claude Code in the Claude app, desktop and phone | [T] |
| A project stdio MCP server from `.mcp.json` loads in these sessions | [T] `learning-question` server |
| A private artifact with `db` and `sample` publishes from the session and opens on the phone | [T] |
| The session reads and writes the artifact db with ArtifactData | [T] existing room-push path |
| Grading on the page with `sample` | [T] |
| Union-merged JSONL and one file per attempt | [T] |
| The skill deciding when to ask | [T] |

**Needs a test first** (each about an hour, run on day 0 of phase 1 unless noted):

| Experiment | The test | If it fails |
|---|---|---|
| E-SEAL | Screenshot what the Claude app shows when a subagent writes the key and calls `lwb_post`. | Write the key at grading time; keep the hash for audit. |
| E-REPO | Attach `learning-record` to a cloud session, clone, commit, push after a grade. | Room db becomes the system of record, plus `export`. |
| E-OFFLINE | Phone in airplane mode, lock, close the Claude app, reopen, go online, read the db. | Keep the copy "Not sent yet. Keep this page open." |
| E-PERM | A fresh cloud session in default mode runs journey 2.a; count permission prompts. | Ship `.claude/settings.json` allow list; target 0 after the first. |
| E-CCR-SEND | The Room declares `mcp` with one tool, Claude Code Remote `send_message`, and sends `{card, event}` from the phone. Does the session wake? | Next rung: `sendToClaudeSession`, then the pull. |
| E-A11Y | Keyboard only from "Open card" to Lock to "Back to the build" on the desktop app; VoiceOver on an iPhone answering one card. | Chat becomes the accessible default; the Room drops letter keys. |
| E-SEND (phase 2) | Lock calls `sendToClaudeSession({deliver: "send"})` on desktop and phone; note if the phone leaves the page. | Keep the pull. |
| E-HOOKS (phase 2) | Commit a hooks file in a cloud session branch that logs every event. | Keep skill rules in cloud; hooks only locally. |
| E-AUQ, E-ELICIT (phase 2) | AskUserQuestion and an elicitation form in a cloud session, desktop and phone. | Chat text. |
| E-PUSH, E-SCHED (phase 2) | One push reaches the phone and is skipped while at the machine; a daily cloud task writes due cards. | Due line at session start. |
| E2, E7 (learning, from phase 1) | Compare shown on half the predictions; drills with hypothesis before code on half. Measure 7 and 21 day results. | Keep Compare for misses; keep line pick as step two. |
| Phase 3 | The local desktop mod, Codex `request_user_input_async`, MCP Apps in Cursor, a phone page with Web Push and a sealed mailbox for non-Claude harnesses. | Each has a fallback in the dependency register. |

**Learning gates.** Every phase is also judged on the record: unaided success
at the first spaced review with and without an explain-back, success at 21 days,
how often Sure is right, and drill success at 7 and 21 days. A phase that makes
the flow smoother and these numbers worse is rolled back.

## 4. Build order and rough size

| Step | What | Size |
|---|---|---|
| 0 | The six day-0 experiments above | 1 day |
| 1 | `record.py` and `learning.py`: events with uuids, reviews log, the level rule (same-session cap, hint and opened-code cap, drill credits its bug's topic), `completion` kind, daily cap 3, hash-checked `import`, `export`, I do not know out of calibration | 2.5 days |
| 2 | `lwb` server with one row per learning event, allow list, commit and push after each grade | 2 days |
| 3 | Room v2 from `assets/room.css`: Inbox, focused Card, Compare, Map, Drill, Settings; single-writer docs; one live region; shortcuts setting; short-viewport layout | 3 days |
| 4 | Skill: moments, the text card, your line, question quality rules, rate rule, pull rule | 1 day |
| 5 | Privacy: `init` checks the remote and sets up the record repo | 0.5 day |
| 6 | Phase 2: hooks, the bell ladder, AskUserQuestion and elicitation doors, push and the daily review | about 6 days plus 1 day of tests |
| 7 | Phase 3, item by item, behind its experiment | open |

Phase 1 is about 10 days. If E-CCR-SEND passes on day 0, the phone bell moves
into step 3.

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
