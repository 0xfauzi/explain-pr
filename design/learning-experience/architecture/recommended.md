# Recommended architecture: Room first, agent native

Status: recommendation, 2026-11-07. Written by a review panel (a staff platform
engineer, a learning scientist and a product designer) after scoring the three
proposals in this folder: `agent-native.md`, `companion.md` and
`protocol-bridge.md`. Nothing in this document is built yet. Each claim has a tag.

Tags: **[T]** verified by a test in this project, **[D]** documented by the
vendor or the spec, **[R]** reported by third parties, **[S]** our inference,
not tested. Section 12 lists every dependency with its status and its cheapest
experiment.

---

## 0. Panel scores

Scale 1 to 10, higher is better. For "effort and risk", higher means less effort
and less risk.

| Architecture | Seamless build, learn, build | Works on the owner's surfaces today | Cross-harness reach | Learning quality | Privacy | Effort and risk | Total |
|---|---|---|---|---|---|---|---|
| agent-native | 8 | 5 | 8 | 9 | 6 | 7 | 43 |
| companion | 7 | 7 | 7 | 8 | 8 | 4 | 41 |
| protocol-bridge | 8 | 3 | 9 | 7 | 8 | 3 | 38 |
| **recommended** (projected) | 8 (phase 1: 6, end state: 9) | 9 | 8 | 9 | 9 | 8 | 51 |

Why the scores are what they are:

- **agent-native** has the best learning design (the prediction targets one
  observable, the gate blocks only when the outcome would show, wait-time
  prediction, "You said / It did", a diagnosis drill that is offered once) and
  it runs no extra service. But its flagship is the mod band and pane, and mods
  draw nothing in cloud sessions or on the phone [D]. This session, which is
  the owner's real surface, is a cloud session. It also stores `seals/` inside
  `.learning/`. That folder is committed, so a rubric shows in the editor and,
  in a public repo, on GitHub before the answer locks.
- **companion** found the two facts that matter most for the owner: the
  claude.ai artifact is the one designed surface that is verified on desktop
  and phone today [T], and explain-pr is a public repo, so a committed record
  is public. Its definition of "seamless" (four testable properties and one
  acceptance test) is the best of the three. But it costs about 33 days, it
  puts a GitHub token on the phone, and its Grader Action sends rubrics to
  CI. Also, sending the learner to a separate app is one more context switch
  than they need when they are at the machine.
- **protocol-bridge** has the widest reach (ACP proxy for Zed, Codex
  app-server companion), the best rules for returning answers ("exactly one
  path per event, at most one unprompted turn per 10 minutes"), and the
  strongest phone privacy (an end-to-end sealed mailbox). But a local daemon
  does not exist in a cloud session, so the owner's main surface gets the
  fallback path. It also needs crypto that the Python standard library does
  not have, and most of its chain is [S].

Decision: start from **agent-native** (harness-native, no service, best
learning flow). Make the **Room artifact** from companion the designed surface
for phase 1, because it is the only rich UI verified on the owner's devices.
Take sealing outside the working tree, reveal on the observable, the rate rule
and the read-only snapshot from **protocol-bridge**. Keep the daemon and the
sealed phone mailbox for the end state, behind experiments.

---

## 1. The decision in nine lines

1. **One card, one store, many doors.** Every question is one card with one id,
   one sealed rubric and one lock. Every surface shows the same card and writes
   the same attempt file through `record.py`.
2. **Chat is the build surface. The Room is the learning surface.** At the
   machine, the card appears in the conversation. Rich work (review queue,
   compare, map, drills, explainers) happens in the Room, a private claude.ai
   artifact that opens beside the session on desktop and in the Claude app on
   the phone [T].
3. **A small stdio MCP server, `lwb`, owns the card lifecycle.** A project
   stdio server from `.mcp.json` already loads in the owner's Claude Code
   sessions in the Claude app [T] (the `learning-question` test server). Phase
   1 uses only its tool calls. Later phases add elicitation, tasks and door
   negotiation to the same server.
4. **The skill drives transitions in phase 1. Hooks drive them in phase 2.**
   The skill already tells the agent when to ask [T]. Hooks make it automatic
   once one test in a cloud session passes.
5. **Answers come home with nothing copied.** In chat, the reply is the answer.
   In the Room, the answer is locked in the artifact db, graded on the page with
   `sample` [T], and pulled into the record by the session at its next turn. In
   phase 2, the Submit tap also rings the session (`room.sendToClaudeSession`).
6. **The rubric is sealed before the question and never seen before the lock.**
   It goes through an MCP tool input, not a Bash command. Only a sha256 commit
   goes into the record. `learning.py check` verifies it afterwards.
7. **The record is private.** If the project remote is public, the record lives
   in a private `learning-record` repo, not in the project.
8. **Calm by default.** One question at a time, a count in the periphery, the
   centre only at the two research moments (before a build, after it works) or
   on the learner's gesture. Every detour ends with a one-line resume cue.
9. **Every upgrade is behind a named experiment with a fallback that already
   works.** Phase 1 depends on nothing that is untested.

---

## 2. What "seamless" means, and how we test it

Seamless is not "learning everywhere all the time". Interruption research and
calm technology say the opposite. Seamless means four properties (from
companion), each with a test:

| Property | Meaning | Test |
|---|---|---|
| No copying | The learner never copies a question, id, URL or answer between surfaces. | Count copy and paste actions in a recorded session: must be 0. |
| No re-explaining | Every door shows the same card in the same state (waiting, locked, graded). | Open one card in chat, Room desktop and Room phone: same prompt, same state. |
| No stall | The build waits on the learner only for a prediction they chose to answer, and "Not now" is one tap or two words. | Time from "Not now" to the next tool call: under 5 s. |
| Resume in one line | Every learning exchange ends with "Back to: <task>. Next: <step>." | Every graded feedback in the transcript ends with that line. |

Acceptance tests, one per phase:

- **Phase 1:** the owner starts a build in Claude Code in the Claude app on the
  laptop, answers the prediction in chat, answers the explain-back on the phone
  in the Room, reads the page's feedback on the phone, and on the next message
  on the laptop the session has the grade in the record. Zero typed commands,
  zero copied strings. One extra turn is allowed.
- **Phase 2:** the same, but the Submit tap on the phone rings the session, and
  the session posts the grade and the resume cue with no extra turn.
- **End state:** the same in the Codex app with the answer given on the phone,
  and in the local desktop Code tab with the answer given in the mod pane while
  the agent keeps building.

---

## 3. What each surface can draw today

This table is why the phase 1 design looks as it does.

| Surface the owner uses | Chat text | AskUserQuestion | MCP elicitation | Mod band and pane | MCP App card | claude.ai artifact (Room) | Hooks run |
|---|---|---|---|---|---|---|---|
| Claude Code, Claude app desktop, cloud session (this session) | yes [T] | [D] | card [D] | no [D] | no [T] | yes [T] | yes, if committed in the repo [D] |
| Claude Code, Claude app desktop, local session | yes [T] | [D] | [S] | yes [D], validated and unit tested [T] | no [T] | yes [T] | yes [D] |
| Claude Code, Claude app phone (cloud or Remote Control) | yes [T] | forwarded and kept open under Remote Control [D] | card in cloud [D]; Remote Control [S] | no [D] | no [T] | yes [T] | on the machine [D] |
| Claude Code CLI | yes | yes [D] | form [T] | yes [D] | no [T] | link opens in browser [D] | yes [D] |
| Codex CLI and app | yes | `request_user_input(_async)` [D] | form, thread waits [T] | no | desktop [R], brief says no | link only | Codex hooks [D] |
| Cursor | yes | no | [D] | no | inline [D] | link only | Cursor hooks [D] |

Two facts decide the design. First, MCP Apps do not render anywhere in Claude
Code [T], so they are never the Claude Code door. Second, the artifact is the
only designed UI verified on both of the owner's devices [T]. So the Room is
the flagship designed surface, and the mod is the flagship for local desktop
sessions once it is tested live.

---

## 4. Core objects

### 4.1 The card

One schema for every door. It merges the three proposals: the `observable`
from agent-native, the `return` block from companion, and `moment` and
`support` from protocol-bridge.

```json
{
  "id": "c_20261107T141502_3f9c",
  "v": 1,
  "kind": "predict",
  "moment": "before",
  "topic": "retry-budget",
  "dimension": "distributed-systems",
  "level_at_ask": "with help",
  "support": "completion",
  "prompt": "When test_retry runs, which assertion fails first, and why?",
  "excerpt": {"path": "src/client.py", "lines": [41, 58], "text": "..."},
  "observable": {"tool": "Bash", "match": "pytest .*test_retry"},
  "answer_shape": "text",
  "confidence": ["guess", "fairly sure", "sure"],
  "actions": ["answer", "dont_know", "not_now"],
  "rubric_commit": "sha256:9c1e...",
  "return": {"claude_session": "session_013c...", "room": "https://claude.ai/code/artifact/..."},
  "resume_cue": "Back to: the retry budget in client.py. Next: the backoff cap.",
  "state": "sealed"
}
```

Kinds: `predict`, `explain`, `diagnose`, `review`, `transfer`, `repair`,
`explainer-prompt`. Answer shapes: `text`, `choice`, `line-pick`, `order`.

Confidence uses certainty-based marking, and every door shows the meaning:
**guess** ("I would not bet on it"), **fairly sure** ("more likely right than
wrong"), **sure** ("I would be surprised to be wrong"). It is one tap, given
before the reveal.

### 4.2 Lifecycle

```
drafted -> sealed -> delivered(door) -> locked -> revealed -> graded -> consolidated -> scheduled
              \-> not_now  (moves to Later; not offered again this session)
              \-> dont_know (locks as a real answer at "guess")
              \-> skipped  (session ended unseen; no penalty; expires after 7 days)
```

- Nothing is delivered before it is sealed. This turns the ground rule "fix the
  rubric first" into code.
- `locked` is final. If two doors lock the same card, the earliest `locked_at`
  wins and the later one is kept as `also_answered` ("You also answered on your
  phone: ..."). This is the rule `record.py` already uses.
- `revealed` happens after the observable shows for a prediction (the test ran),
  and right after the lock for everything else (from protocol-bridge).
- `consolidated` means the learner saw "You said / It did" side by side. For a
  `predict` card this step is not optional (Kapur: failure without
  consolidation is just failure).
- `scheduled` uses the existing ladder: 3, 7, 21, 60, 180 days, a miss returns
  next day, a miss at "sure" returns next day and gets a mark on the map.

### 4.3 Store

```
<record root>/                    the project's .learning/, or a private learning-record repo
  dimensions.json, topics/, attempts/     unchanged layout and record.py
  events.jsonl                    NEW: one line per state change (merge=union)
  reviews.jsonl                   NEW: FSRS-compatible log (topic, ts, rating 1-4, confidence, door)
  config.json                     NEW: mode quiet | normal | deep | paused, nudge ledger
  open.json                       NEW: open card ids and their doors (the "something is waiting" flag)
  map.json                        NEW: read-only snapshot for the Room (no answers, no rubrics)
<sealed root>/sealed/<card>.json  rubric + salt until lock; never in the project working tree
.gitattributes                    *.jsonl merge=union  [T]
```

Where the sealed root is: in a local session, `~/.lwb/sealed/` (from
protocol-bridge). In a cloud session, the home folder does not survive, so the
sealed root is a `sealed/` folder in the private record repo, outside the
project checkout. After the lock, `lwb` copies the rubric and salt into the
attempt file.

### 4.4 Privacy of the record

explain-pr is public, so a record committed to it is public, and so is every
branch (found by companion). Rule:

- `learning.py init` checks the remote with `gh repo view --json visibility`.
- Private project: the record stays in `.learning/` as today.
- Public project: the record lives in `<owner>/learning-record` (private),
  checked out next to the project or as `.learning/` with an ignore rule. Cloud
  sessions attach it as a second repository.
- The Room artifact is private by default [D]. It holds open cards, the
  `map.json` snapshot and inbox rows, never the full record history.

---

## 5. The learner's moments

Each moment has a job, a trigger, a door, a blocking rule and an exit. The
learning rule behind it is in the last column.

| Moment | Job | Trigger (phase 1, then phase 2) | Door at the machine | Door away | Blocks the build? | Basis |
|---|---|---|---|---|---|---|
| Before a build | One prediction about the one observable the build will show. | Skill rule, then `UserPromptSubmit` hook. | Chat card; later AskUserQuestion, elicitation or mod pane. | Not asked away. | Only at the gate, and only if the learner has not answered or said "Not now". | Prequestions help only what they ask about (St. Hilaire 2024); productive failure (Kapur). |
| During | Answer the prediction or one due review while the agent works. | The card is posted with `mode=wait`. | Chat card stays answerable; Room "Now"; later mod band count. | Room. | No. | Wait-learning (Cai 2015) [S for agents, E1]. |
| It fails | The learner names the cause before the agent debugs. Offered once per failing test. | Skill rule, then `PostToolUseFailure` hook. | "Call the cause first? Pick the line, or say not now." | Not offered. | No. "Not now" means the agent debugs and says nothing more. | Shen and Tamkin 2026: delegated debugging lost the most. |
| It works | Explain-back, then "You said / It did". | Skill rule, then `Stop` hook. | Chat card, Room Compare. | One push, then the Room. | The turn ends with the question. The work is done, so it does not hold anything up. | Generation, then consolidation. |
| Away | Questions wait. At most one push a day. | Presence (phase 2). | None. | Push opens the Room on the card. | No. | Calm technology; Duolingo notification back-off. |
| Review | Spaced retrieval and transfer. | Session start (`learning.py due`), then a daily cloud scheduled task. | "2 due" line once; `/learn review` or Room Due. | Room Due (max 5). | No. | Cepeda 2008; successive relearning; Bastani 2025 (answers stay hidden). |
| Map | What the learner can do without the agent, with decay visible. | On request. | Chat text grid; Room Map. | Room Map. | No. | Calibration (Metcalfe); illusion of competence. |
| Drill | Repair drill on a planted bug in a scratch branch or worktree. | On request, or offered in Deep mode. | Chat and Room Drill. | Not offered (needs the code). | No. | Debugging gap. |
| Explainer | A page with predict-before-reveal prompts that enter the schedule. | On request. | Artifact with embedded cards. | Same artifact. | No. | Mnemonic medium (Orbit, Quantum Country). |

Support follows the level (Kalyuga, expertise reversal):

| Level | Question type | Support |
|---|---|---|
| not yet | worked example, then a completion question | labelled steps |
| with help | completion problem | one hint offered |
| recalls | predict and explain | no hint unless asked |
| transfers | design first, new context, planted bug | no explainer offered |

Hints are a ladder H0 to H3. Each hint is a `lwb_hint(card)` call, so the hint
level is recorded, not trusted.

Feedback is the skill's Voice: "Correct." / "Not quite." / "No.", then the gap
with `path:line`, then "Back on 14 Nov.", then the resume cue. No praise, no
streaks, no XP, no loss copy.

---

## 6. The Room: product spec

One private claude.ai artifact per learner, pinned on request, rebuilt from
`assets/room.html`. The same HTML also runs under `learning.py serve` for local
use. It follows the approved site exactly (`docs/index.html`, `site.css`).

### 6.1 Visual language

- Paper `#F5F4F0` with `docs/assets/grain.png`, ink `#16161A`, accent
  `#E8541E`, text-safe accent `#C2410C`. Dark mode follows the token rules of
  the artifact contract, with paper and ink swapped and the ramp kept.
- Instrument Sans for headings (wdth 88, weight 650). JetBrains Mono for code,
  ids, paths and key caps.
- Cards: white, 1.5px `#DAD8D0` border, 16px radius (14px on the phone), max
  width 640px, 24px padding, 16px side gutter at 375px. Pill buttons. Primary
  buttons are ink filled. Accent is kept for the one live element: the edge of
  the Now card and a record cell that just lit.
- Record cells: ramp `#F6C9AF` (with help), `#EE8B5B` (recalls), `#C2410C`
  (transfers). Only the last one passes 3:1 [T], so every filled cell also has
  a 1.5px ink outline and a level glyph (one, two or three bars), the level in
  words as its accessible name, and a table view under every grid. Best level
  is the outline, latest is the fill, so decay is visible.
- Motion: a record cell fades in over 400 ms when a grade lands; the card moves
  8px on lock. Nothing else moves. `prefers-reduced-motion` removes both.

### 6.2 Screens

| Screen | Contents |
|---|---|
| Inbox | Three groups: Now (max 1), Due (max 5, then "3 more move to tomorrow"), Later. The only number on the page is the due count. |
| Card | Kind and topic line, prompt, excerpt with `path:line` header, answer field (or choices or line picker), confidence as a radio group with meanings, "I don't know", "Not now", Submit. After Submit: "Locked." |
| Compare | Two columns, "You said" and "It did", then the verdict word, the gap, the next date and "Back to the build". Stacks on the phone. |
| Map | Dimensions by topics grid, glyphs and outlines, a table toggle, calibration as three bars (share correct at guess, fairly sure, sure). Faint weekly cells with no counter. |
| Drill | Symptom, hypothesis field, line picker, then the reveal. |
| Settings | Mode (Quiet, Normal, Deep), Pause, pushes on or off. |

### 6.3 Keys

Shown in an action bar on every card, in key caps, Linear and Raycast style:
J and K move, Enter opens, 1 2 3 set confidence, D "I don't know", H "Not now",
Esc back, Cmd or Ctrl plus Enter submits, G then M opens the map. Every action
is also a button at least 44px tall.

### 6.4 Accessibility

The card is a `form`. Confidence is a labelled `fieldset` of radios, never
colour only. The verdict is in a `role="status"` region, and focus moves to
the verdict heading after Submit. Every control is reachable by keyboard.
Colour is never the only cue.

### 6.5 Copy samples

"1 question about retries." / "Answer before you look at the change." /
"Locked. Shown after the test runs." / "Saved. Claude adds it to your record
on your next message." / "No. A timeout means the reply did not arrive. It
does not tell us whether the charge ran. billing/charge.py:47. Back tomorrow."
/ "Back to the build: Claude is running the billing tests."

### 6.6 The same card as text

Chat, terminal and push bodies use one text layout with the same parts:

```
Question · retry-budget · predict
When test_retry runs, which assertion fails first, and why?
src/client.py:41-58
Reply with your answer and how sure you are: guess, fairly sure or sure.
Or reply "don't know" or "not now". Or answer in the Room: <link>#c=c_3f9c
```

---

## 7. The transition engine

**Phase 1 (skill rules, verified behaviour today [T]).** SKILL.md gains a short
"Moments" section: when to post a prediction, when to offer the diagnosis,
when to ask the explain-back, and the rate rule. The agent calls `lwb` tools.
The skill's existing Voice and ground rules apply.

**Phase 2 (hooks, after E-HOOKS).** Hooks committed in the repo's
`.claude/settings.json` (so cloud sessions get them) or shipped in the plugin:

| Hook | Does |
|---|---|
| `SessionStart` | Runs `learning.py due --count` and `lwb status`; injects one line: "2 due. 1 answer from the Room to add." |
| `UserPromptSubmit` | Cheap rule: does the prompt touch a tracked topic's anchors or name a new dimension? If yes and no card is open, injects "prediction due for retry-budget (with help)". |
| `PreToolUse` gate | If a `predict` card is open on this tool's observable, deny once with "Prediction c_3f9c is open. Ask it now or mark it not now, then rerun." |
| `PostToolUse` | When the observable ran, inject "Reveal c_3f9c now." (from protocol-bridge). |
| `PostToolUseFailure` | Once per failing test on a tracked topic: "Offer the diagnosis once. Do not diagnose first." |
| `Stop` | Tests passed this turn, topic touched, no explain-back yet: "Ask the explain-back once, then stop." |
| `PreCompact` | Writes the open card and resume cue to `open.json` so compaction cannot lose it. |
| `PreToolUse` on Read and Bash | Denies reads of the sealed root. `lwb_reveal` is the only way in, and it refuses before the lock. |

**Rate rule (from protocol-bridge).** One open card at a time. At most one
unprompted learning turn per 10 minutes per session. Quiet mode: one
prediction per session. Deep mode: one per build step. "Not now" is honoured
exactly for the rest of the session.

---

## 8. How the answer gets home

Data and bells are separate (from companion). Data goes into the record or an
inbox, keyed by card id. A bell only says "card X changed", so a lost bell
delays feedback but never loses an answer. Exactly one bell per event, the
first one the session supports (from protocol-bridge).

| Rank | Where the answer was given | Data path | Bell | Status | Phase |
|---|---|---|---|---|---|
| 1 | Chat reply | the agent calls `lwb_lock` with the text | none needed | [T] | 1 |
| 2 | Room, session at the machine | artifact db row (locked) | the agent pulls `open.json` cards with ArtifactData at the start of its next turn | [T] db read and write; the pull rule is a skill rule | 1 |
| 3 | Room, any device | artifact db row | Submit calls `room.sendToClaudeSession` (the tap is the required gesture) | [D] | 2 |
| 4 | AskUserQuestion | tool result | none needed | [D] | 2 |
| 5 | Elicitation form | tool result | none needed | [T] CLI and Codex; app [D] | 2 |
| 6 | Mod pane (local desktop) | `.learning/inbox/` or `/learn answer` | `$.prompt.submit` at idle | [D], mod validated [T] | 3 |
| 7 | Local page (`serve`) | `.learning/inbox/` | plugin monitor, `asyncRewake` hook or inbox socket | [D] | 3 |
| 8 | Wait-mode card | MCP task | task completion | [D] CLI | 3 |
| 9 | Codex | tool result, `request_user_input_async` reply, `turn/steer` from a companion | as listed | [T] form, [D] the rest | 3 |
| 10 | Any harness, phone PWA | sealed mailbox | drained at session start or by the cloud task | [S] | 3 |
| 11 | Anything else | inbox | `SessionStart` line "1 answer waiting" | [D] | 1 (as a skill rule), 2 (as a hook) |

On any bell the agent does the same five steps: import, reveal, grade, write
feedback (to chat if the learner is there, to the Room db as well), end with
the resume cue. Grades on the page by `sample` show immediately on the phone
and count as reviews. Level changes still follow `record.py`'s evidence rules.

---

## 9. Rubric privacy

Threat model (shared by all three proposals): not a cheating learner, but an
accidental glance. Seeing the rubric before answering destroys the retrieval.
The rubric must also be provably fixed before the question.

1. **No rubric in Bash.** Today `learning.py ask --rubric "..."` shows the
   rubric in a visible command [S, likely]. Phase 1: the agent passes the
   rubric as input to `lwb_seal`, an MCP tool. Where E-SEAL shows the app
   expands tool inputs, a subagent calls `lwb_seal`, so the main transcript
   shows only "Card sealed (sha256 9c1e...)".
2. **Commit and reveal.** The card holds `sha256(salt + rubric)`. The rubric
   lives in the sealed root, outside the project tree. After the lock it is
   copied into the attempt file, and `learning.py check` verifies the hash.
   The map can show "Rubric fixed 14:15. Answer locked 14:22."
3. **Pages get the rubric only after the lock.** In the Room db, the rubric is
   a separate doc that `room-push` writes only after the page reports a lock
   for on-page grading. The page states the residual risk in Settings: the
   owner can read their own db.
4. **The agent cannot peek.** A `PreToolUse` hook (phase 2) denies reads of the
   sealed root. Before that, the skill rule says the same.
5. **Push bodies** never hold code, answers or rubric text.

---

## 10. State and sync

- The record is plain files in git, written only through `record.py` (by
  `learning.py` or `lwb`). Agents never hand-edit it.
- Inboxes, not replicas: the Room db, the mod inbox folder, the phone mailbox.
  `learning.py import` is idempotent on card id and keeps the earliest lock.
  Answers whose seal does not match are rejected and logged.
- One file per attempt plus union-merged JSONL lets laptop sessions, cloud
  sessions and scheduled-task branches merge with no conflicts [T].
- `map.json` is rewritten on every grade, so the Room can show the record
  without the history.
- No network: every local door still works. The Room and scheduled tasks pause.
  Answers on the phone wait in the db.

---

## 11. Phases

### Phase 1: ships first, verified technology only (about 8 days)

Everything here is [T], or is a skill rule that only uses [T] parts.

| # | Build | Uses | Days |
|---|---|---|---|
| P1.1 | `record.py` and `learning.py`: `events.jsonl`, `open.json`, `map.json`, `reviews.jsonl`, `config.json` modes and pause, `rubric_commit` and the check, `.gitattributes`, `import --from-room` idempotent on card id, `status --line`. | Python stdlib [T] | 2 |
| P1.2 | `lwb` stdio MCP server, tools only: `lwb_seal`, `lwb_post`, `lwb_lock`, `lwb_reveal` (refuses before lock), `lwb_grade`, `lwb_hint`, `lwb_status`, `lwb_due`, `lwb_map`. Shares `record.py`. Registered in `.mcp.json` and in the plugin. | project stdio server in a Claude app session [T] | 2 |
| P1.3 | Room v2 artifact: Inbox, Card, Compare, Map, Drill, Settings; the db as inbox; on-page grading with `sample` after lock; keys and accessibility in section 6. One HTML for the artifact and for `serve`. | artifact with `db` and `sample` [T] | 3 |
| P1.4 | Skill: a "Moments" section, the text card layout, the level to support table, the rate rule, the pull rule ("if `open.json` lists Room cards, read them with ArtifactData before you reply"), the resume cue. | the skill [T] | 0.5 |
| P1.5 | Privacy: `init` checks the remote. A public project gets a private record repo. Until E-REPO passes, a public project keeps the record in a Room db mirror and in local files only, and nothing is committed to the public repo. | `gh` [T], artifact db [T] | 0.5 |

Phase 1 acceptance test: section 2. What the learner feels: questions in the
conversation at the two moments, one link to the Room for everything else, the
phone works through the same Room, and the session catches up on the next
message.

What phase 1 does not have: automatic triggers (the skill decides), instant
ringing from the phone, pushes, a daily review clock with the laptop closed.

### Phase 2: after named experiments (about 6 days of build, 1 day of tests)

Run the experiments in this order. Each is under an hour except E-SCHED (one
day of waiting). Each row says what passing unlocks and what happens if it
fails.

| Experiment | Unlocks if it passes | If it fails |
|---|---|---|
| E-SEND: Room Submit calls `room.sendToClaudeSession` on desktop and phone; log `canSendToClaudeSession()`. | Instant bell from the Room. Phase 2 acceptance test. | Keep the pull rule. Try `comments.sendToClaude`. |
| E-HOOKS: commit a hooks file in a cloud session branch that logs every event and adds one context line. | Section 7 hook engine on the owner's real surface. | Keep the skill rules. Try the plugin's hooks instead of the repo file. |
| E-SEAL: screenshot what the Claude app shows for a `lwb_seal` input, for a subagent call, and for `learning.py ask`. | Pick the sealing path for each surface. | Rubric written only at grading time by a subagent, with commit and reveal kept for audit. |
| E-AUQ: AskUserQuestion in a cloud session on desktop and phone, prediction choices plus confidence as a second question. | Native in-chat card for `predict` and `diagnose`. | Chat text card. |
| E-ELICIT: `lwb_ask mode=block` sends an elicitation form (answer, confidence enum, dont_know) in a cloud session on desktop and phone. | Structured answers with the rubric kept on the server. | AskUserQuestion or chat text. |
| E-REPO: attach `learning-record` to a cloud session, clone, commit, push. | Private record in git for public projects. | Keep the db mirror and add an export command. |
| E-PUSH: `PushNotification` from a cloud session reaches the phone; check that it is skipped while the learner is at the terminal. | The away moment. | No pushes. The Room badge or the due line at session start. |
| E-SCHED: daily cloud scheduled task with `create_new_session_on_fire` and push: `learning.py due`, write at most 5 cards to the Room db, one push, three ignored pushes stop it. | Review on the platform clock with the laptop closed. | Due list at session start only. |
| E1 (learning): alternate wait-time and before-build prediction for two weeks; log skips, answer time, 7-day recall. | Keep wait mode as the default. | Default to the gate blocking in Normal mode; wait mode only in Deep. |
| E2 (learning): Compare screen on half of the predictions. | Keep Compare for all predictions. | Keep it anyway for misses (strong prior), drop it for hits. |

Phase 2 build: hooks (2 days), Submit bell and feedback write back (1 day),
AskUserQuestion and elicitation doors in `lwb` with door choice from client
capabilities (2 days), push and scheduled review prompt with the nudge ledger
(1 day).

### Phase 3: the ambitious end state

Each item is behind its own experiment (section 12). Ordered by value to the
owner.

1. **Local desktop flagship: the mod.** For sessions on the owner's laptop
   (desktop Code tab, CLI, VS Code): a band above the prompt
   ("1 question · press 1", "2 due"), a pane with the same Card, Compare and Map
   components, instant `/learn` commands that work mid-turn, `$.prompt.submit`
   as the bell. The learner answers while the agent keeps editing. (E-MOD,
   E-MOD2.)
2. **Wait-time predictions everywhere.** `lwb_ask mode=wait` returns an MCP task
   handle; the gate hook blocks only if the card is still open when the
   observable runs. (E-TASK, E-GATE, E1.)
3. **One server, every harness.** `lwb` chooses the door from what the client
   declares: mod present, then MCP App card, then elicitation form, then the
   Room plus one push, then text. Codex gets `request_user_input_async`, the
   Stop block for the explain-back and, if E-CDX-APP passes, the card as an
   MCP App panel. Cursor and VS Code get the MCP App card (Submit calls
   `tools/call lwb_lock`, never `ui/message`). Zed gets ACP elicitation. When
   SEP-3118 merges, the card is the elicitation UI itself.
4. **A phone door for any harness.** An installable page at
   `0xfauzi.github.io/explain-pr/app/` in the site language, with Web Push and
   an app badge. It pairs by QR code and talks through an end-to-end sealed
   mailbox (from protocol-bridge), so the relay sees only ciphertext and no
   token sits on the phone. It cannot grade; Claude users grade in the Room.
   This is the answer for Codex and Cursor learners, who have no artifact.
5. **Optional `lwbd`.** Only if logs show over-asking across parallel sessions:
   a lazy local daemon that holds presence and caps for all sessions. Same
   files, same fallback to direct writes.
6. **Learning quality on real data.** FSRS-6 replay of `reviews.jsonl` against
   the ladder; hypercorrection analysis of misses at "sure"; calibration over
   time on the map; explainers with embedded cards that enter the schedule.

---

## 12. Dependency register

| # | Dependency | Status | Cheapest experiment | Phase | Fallback |
|---|---|---|---|---|---|
| 1 | Project stdio MCP server from `.mcp.json` loads in Claude Code sessions in the Claude app | [T] `learning-question` server present in this session | done | 1 | `learning.py` in Bash |
| 2 | MCP tool results show as text in Claude Code | [T] | done | 1 | none needed |
| 3 | MCP Apps render in Claude Code | [T] no, text only | re-test when release notes mention it | never for Claude Code | Room |
| 4 | Artifact with `db`, `sample`, `room`, `user`, `mcp` capabilities publishes from a Claude Code session and opens on the phone | [T] | done | 1 | `learning.py serve` locally |
| 5 | Session reads and writes the artifact db with ArtifactData | [T] (existing room-push path) | done | 1 | none |
| 6 | Union merge for `*.jsonl` | [T] | add to CI as a regression test | 1 | one file per event |
| 7 | WCAG contrast of the record ramp | [T] two of three fail 3:1 | done | 1 | outline, glyph and table |
| 8 | `room.sendToClaudeSession` / `comments.sendToClaude` from the Room | [D] | E-SEND | 2 | pull rule |
| 9 | Repo-committed hooks run in cloud sessions | [D] | E-HOOKS | 2 | skill rules |
| 10 | Tool inputs and subagent calls hidden or collapsed in the Claude app | [S] | E-SEAL | 1 (choice), 2 | rubric written at grading time |
| 11 | AskUserQuestion renders in the Claude app on desktop and phone; kept open under Remote Control | [D] | E-AUQ | 2 | chat text |
| 12 | Elicitation form as a card in cloud sessions, desktop and phone | [D] | E-ELICIT | 2 | AskUserQuestion |
| 13 | Elicitation forwarded through Remote Control | [S] | E-RC: trigger a form, open on the phone | 3 | AskUserQuestion |
| 14 | Elicitation form in Claude Code CLI; hook receives it | [T] 2.1.319 | done | 2 | text |
| 15 | Second private repo attached to a cloud session | [D] | E-REPO | 2 | db mirror |
| 16 | `PushNotification` reaches the phone; skipped while present | [D], tool present [T] | E-PUSH | 2 | due line at session start |
| 17 | Cloud scheduled task with fresh session, repo access and push | [D], tool present [T] | E-SCHED | 2 | due line at session start |
| 18 | Mods draw band and pane in local desktop Code tab, CLI, VS Code | [D], validated and unit tested [T] | E-MOD: `claude --plugin-dir ./lwb-mod` on the laptop with a fake `open.json` | 3 | chat and Room |
| 19 | Mod can write a file or submit `/learn answer` | [S] | E-MOD2 | 3 | pane is view only; answers in chat |
| 20 | `$.prompt.submit` queues at idle without stopping the build | [D] | part of E-MOD | 3 | the agent pulls at turn start |
| 21 | Plugin monitor and `asyncRewake` hook wake an idle local session | [D] | E-MON, E-WAKE | 3 | next turn |
| 22 | Inbox socket `CLAUDE_CODE_MESSAGING_SOCKET` wire format | [D] exists [T], format undocumented | E-SOCK with `--debug` | 3 | monitor |
| 23 | MCP tasks in Claude Code (CLI footer; desktop) | [D] CLI, [S] desktop | E-TASK | 3 | post and return at once |
| 24 | `PreToolUse` deny with reason as the prediction gate | [D] | E-GATE | 3 | ask before the build |
| 25 | `MessageDisplay` can strip praise | [D], effect untested | E-MSG | 3 | Voice rules in the skill |
| 26 | Codex elicitation form, thread waits | [T] 0.167 | done | 3 | text |
| 27 | Codex `request_user_input_async` on TUI, desktop, ChatGPT iOS | [D] | E-CDX-ASYNC | 3 | form at the gate |
| 28 | Codex Stop hook `decision: block` and pre-tool hook | [D] | E-CDX-STOP | 3 | skill rule |
| 29 | Codex desktop renders MCP Apps | [R] issue 21019 closed; brief says no | E-CDX-APP with `experiments/mcp-app/server.py` | 3 | form |
| 30 | Codex `turn/steer` from a companion attached to a live thread | [D] steer, [S] attach | E-CDX-STEER | 3 | Stop hook at turn end |
| 31 | `.agents/skills` read by Codex, Cursor, Gemini | [D] | symlink and run `/skills` | 3 | copy the skill |
| 32 | Cursor MCP App card inline; `stop` followup auto-submits | [D] | E-CUR | 3 | text |
| 33 | ACP elicitation in Zed through a proxy agent | [D] spec, [S] proxy | E-ACP | 3 | text |
| 34 | SEP-3118 app-rendered elicitation | [S] not merged | track ext-apps PR 733; run the inspector branch | 3 | form plus card |
| 35 | Web Push and badge on an installed page on iOS 16.4+ (Declarative on 18.4+) | [D] | E-PWA: one push from a `workflow_dispatch` Action | 3 | Room on Claude, no push elsewhere |
| 36 | WebCrypto P-256 and AES-GCM interop with Python without extra packages | [S] | E-CRYPTO: seal in Safari, open in Python | 3 | one vetted dependency |
| 37 | ntfy relay: publish [T], retention and CORS [S] | [T] / [S] | E-RELAY: poll after 1 h and 13 h | 3 | GitHub Actions relay |
| 38 | Artifact `mcp` capability reaching a local server | [S] | E-HOSTMCP | 3 | db inbox |
| 39 | `navigator.setAppBadge` on an installed artifact or page | [S] | feature-detect on iOS and Android | 3 | due count on the page |
| 40 | Wait-time prediction is not worse than before-build | [S] | E1 | 2 | gate blocks in Normal mode |
| 41 | Compare view improves 7-day recall | [D] literature | E2 | 2 | keep for misses |

---

## 13. Re-plan triggers

- **E-SEND fails:** the phone stays one turn behind. Make the pull rule
  stronger: a `SessionStart` and `UserPromptSubmit` hook line says "1 answer
  in the Room", and the Room says "Saved. Claude adds it on your next message."
- **E-HOOKS fails in cloud sessions:** keep the skill rules for cloud, and use
  hooks only in local sessions through the plugin.
- **E-SEAL shows tool inputs everywhere:** move rubric writing to grading time
  in a subagent that returns only the verdict. Keep the commit for audit.
- **E-MOD passes on the owner's laptop:** the local desktop Code tab gets the
  mod as its first door, ahead of chat cards. Cloud sessions keep the Room.
- **Claude Code ships MCP App rendering:** the card becomes an MCP App in
  Claude Code, and the Room keeps review, map and the phone.
- **E1 shows wait-time cards are skipped:** the gate blocks in Normal mode.
- **The owner moves most work to Codex:** move phase 3 item 4 (the phone page
  with the sealed mailbox) ahead of item 1.

---

## 14. What we left out, and why

- **The Grader Action and the GitHub inbox repo** (companion): they put a
  token on the phone and rubrics in CI, for a delay that the Room's on-page
  grading already removes for Claude users.
- **A daemon from day one** (protocol-bridge): it does not exist in cloud
  sessions, which are the owner's main surface. It stays an optional
  accelerator.
- **Seals inside the committed record** (agent-native): they leak in the
  editor and in public repos. Sealed files live outside the project tree.
- **Streaks, XP, percent bars, loss copy:** no learning basis for this
  learner, and the research on streaks shows they distort behaviour.
- **CRDT sync:** one learner, one file per attempt and union merge are enough.
