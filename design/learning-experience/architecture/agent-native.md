# Agent-native architecture: learning lives inside the harness

Status: design proposal, 2026-11-07. Stance: maximise what each harness renders
natively (skills, hooks, status line, MCP elicitation, MCP Apps where they
render, mods and artifacts in Claude), fall back to plain text gracefully, and
run no extra service. Everything below either runs inside a process the harness
already starts (a stdio MCP server, a hook, a mod, a monitor) or on a surface the
platform already hosts (claude.ai artifacts, Codex Sites, cloud scheduled tasks).

Status keys used throughout: **[T]** verified by test in this project,
**[D]** documented by the vendor, **[R]** reported by third parties,
**[S]** speculative. Every dependency is listed with its cheapest experiment in
section 11.

---

## 1. The idea in five lines

1. There is **one question unit** (the card) and **one store** (`.learning/` in
   the repo). Every surface is a door onto the same card and writes the same
   attempt file.
2. A small **learning MCP server (`lwb`)**, launched over stdio by the harness,
   owns the card lifecycle: open, seal rubric, deliver, lock, reveal, grade. It
   reads the client's declared capabilities and picks the richest door that
   harness can draw.
3. **Hooks are the transition engine.** They notice the four research-backed
   moments (before a build, during the wait, when it works, when it fails) and
   hand the agent one line of context. The learner never types a command to
   move between building and learning.
4. **Answers come back as events, not as copied text.** Every door appends to
   `.learning/events.jsonl`; a monitor, an asyncRewake hook, the session inbox
   socket or an artifact `sendToClaudeSession` turns that into a turn in the
   running session.
5. **Calm by default.** The learning layer is a count in the periphery until the
   learner reaches for it, or until one of the two moments where the research
   says it should take the centre (prediction before, explain-back after).

---

## 2. Principles that decide hard cases

| Principle | Consequence in this design | Source |
|---|---|---|
| Ask during the wait, not instead of the build | Prediction is posted when the agent starts a long step and is answered while it works. It only blocks at the instant the outcome would be revealed. | Cai et al. 2015 wait-learning; Iqbal and Bailey breakpoints [S for agents] |
| Prediction targets the one observable | Each prediction card names the observable (`observable: "exit code and the first failing assertion of test_retry"`). The gate hook keys on it. | St. Hilaire 2024 |
| Productive failure needs consolidation | After the outcome, the card flips to a two-column "You said / It did" view before any explanation. | Sinha and Kapur 2021 |
| The agent never debugs first for a learner | PostToolUseFailure offers "Call the cause first?" once per failing test. "Not now" is honoured exactly. | Shen and Tamkin 2026; Bastani 2025 |
| Rubric fixed before the question, unseen before lock | Rubric sealed by hash at `ask`, revealed only by `lock_answer`. | skill ground rules; section 8 |
| No praise, task-only feedback, a where-next line | "Correct." / "Not quite." / "No." then the gap, then "Back on 14 Nov." | Kluger and DeNisi 1996; skill Voice |
| Every detour ends with a resume cue | Last line of every learning exchange: "Back to: wiring the retry budget into `client.py`." | Altmann and Trafton; Parnin |
| No streaks, no XP, no loss copy | Faint weekly cells with no counter; the due count is the only number. | Silverman and Barasch 2023 |
| Never push while the learner is at the machine | Presence check before any phone push. | Claude Code push rule, CLAUDE_CLIENT_PRESENCE_FILE [D] |
| One nudge a day at most, three ignored means stop | Encoded in the scheduler prompt and the server's nudge ledger. | Duolingo KDD 2020 |

---

## 3. The core objects

### 3.1 The card (one schema, every door)

```json
{
  "id": "att_20261107_7f3a",            // attempt id, also the idempotency key
  "kind": "prediction",                  // prediction | explain-back | retrieval | transfer | diagnosis | repair | field
  "topic": "retry-budget", "dimension": "distributed-systems",
  "level_before": "with help",           // drives support (expertise reversal)
  "prompt": "When test_retry runs, what is the first assertion that fails, and why?",
  "excerpt": {"path": "src/client.py", "lines": [41, 58], "code": "..."},
  "observable": {"tool": "Bash", "match": "pytest .*test_retry"},
  "answer": {"type": "text", "max": 400},  // text | choice | line-pick
  "confidence": ["guess", "fairly sure", "sure"],
  "actions": ["answer", "dont_know", "not_now"],
  "rubric_seal": "sha256:9c1e...",       // hash of rubric + salt; rubric itself never on the card
  "resume_cue": "Back to: retry budget in client.py",
  "doors": []                            // filled with each door that showed it
}
```

Confidence uses certainty-based-marking meanings shown on every door:
**guess** ("I would not bet on it"), **fairly sure** ("more likely right than
wrong"), **sure** ("I would be surprised to be wrong"). One tap, before reveal.

Level-adaptive support (Kalyuga) is chosen when the card is made:
`not yet` gets a labelled worked example then a completion question;
`with help` gets completion; `recalls` gets predict and explain;
`transfers` gets design-first, a planted bug or a new context, with no
explainer offered.

### 3.2 The store

`.learning/` stays plain files, one file per topic and per attempt (record.py).
Additions:

- `events.jsonl`: append-only, one line per state change
  (`opened`, `shown{door}`, `answered`, `locked`, `graded`, `snoozed`,
  `not_now`). This is the one bell every listener watches.
- `inbox/<attempt-id>.json`: answers that arrived from a door that cannot run
  `learning.py` (artifact db, Codex Site, phone). `learning.py import` folds them
  in; the attempt id makes a repeat import a no-op.
- `seals/<attempt-id>.rubric`: the rubric, written once at `ask`, outside the
  card. See section 8 for who can read it and when.
- `reviews.jsonl`: one line per graded review in an FSRS-compatible shape
  (`topic, ts, rating 1..4, confidence, door`) so the 3/7/21/60/180 ladder can be
  replayed through FSRS-6 offline later without changing the live schedule.
- `.gitattributes`: `*.jsonl merge=union` [T].
- `config.json`: `mode: quiet | normal | deep`, nudge ledger, paused flag.

### 3.3 The learning MCP server (`lwb`)

A stdlib Python stdio server that imports `record.py` and shares its write path
with `learning.py`, so the CLI and the server can never disagree.

| Tool | Who calls it | What it does |
|---|---|---|
| `lwb_ask(topic, kind, prompt, rubric, observable?, mode)` | agent | Seals the rubric, writes the attempt, appends `opened`, then delivers on the best door. `mode=wait` returns at once (non-blocking); `mode=block` elicits now. |
| `lwb_post(...)` | agent | Same, but only queues for the inbox (away, review). |
| `lwb_status()` | agent, hooks, status line | `{open, due, waiting_grade, mode}` in one line. |
| `lwb_lock_answer(id, answer, confidence)` | the card (app-only in MCP Apps), elicitation path internally | Locks the answer, then returns the rubric. Refuses a second lock. |
| `lwb_grade(id, outcome, hint, gap, feedback)` | agent | Closes the attempt via record.py; returns the next review date and the resume cue. |
| `lwb_due(limit)`, `lwb_map()`, `lwb_record_read(topic?)` | agent, pages via `mcp` capability | Read side. |

Door negotiation happens inside the server at delivery time, from what the
client declared in `initialize` plus presence files:

```
1. Mod present (.learning/.presence/mod-*) .......... draw in the mod pane      (Claude Code CLI, desktop Code tab, VS Code)
2. Client declares io.modelcontextprotocol/ui ....... MCP App card              (Claude chat, ChatGPT, VS Code, Cursor, Codex desktop if fixed)
3. Client declares elicitation.form ................. form elicitation          (Claude Code CLI and cloud cards, Codex CLI and desktop, ACP)
4. Learner away (no presence, mobile flag) .......... hosted page + one push    (artifact room or Codex Site)
5. Nothing ......................................... return the card as text  (chat; the agent shows it verbatim)
```

When tier 2 and 3 both exist, the server prefers SEP-3118 app-rendered
elicitation once merged; until then it sends the MCP App result for the
designed card and keeps the elicitation as the blocking fallback.

For `mode=wait`, the server uses the **MCP tasks extension** where the client
supports it (Claude Code CLI shows a footer task [D]): the tool returns a task
handle immediately and the task completes when `answered` lands in
`events.jsonl`. Elsewhere it returns at once and relies on the bell (3.4).

### 3.4 The bell: how an answer reaches the running session

Ranked by preference; the plugin installs the first that the harness supports.

| Bell | Harness | Wakes idle session | Status |
|---|---|---|---|
| Plugin monitor `tail -F .learning/events.jsonl` (filtered to `answered`) | Claude Code CLI, desktop | yes, as a notification | [D] |
| SessionStart hook with `asyncRewake: true` waiting on `inbox/` and `events.jsonl` | Claude Code (no plugin needed) | yes, exit 2 | [D] |
| Session inbox socket `CLAUDE_CODE_MESSAGING_SOCKET` written by `learning.py answer` or `serve` started from the session | Claude Code local | yes | [D], socket exists here [T], wire format untested |
| Artifact `room.sendToClaudeSession` / `comments.sendToClaude` on the Submit gesture | hosted page to Claude Code session | yes | [D] |
| MCP elicitation response | any client with form mode | n/a, turn was blocked waiting | [T] Claude Code 2.1.319, [T] Codex 0.167 |
| MCP task completion | Claude Code CLI | reported at next pause | [D] |
| Codex `turn/steer` from a companion | Codex app-server | yes | [D], out of stance (needs a companion process); kept as option |
| Codex Stop hook `decision: block` with "1 answer waiting" | Codex | at turn end | [D] |
| Cursor `stop` `followup_message` | Cursor | at turn end, auto-submitted | [D] |
| SessionStart context injection "2 answers waiting" | all | next session | [D] |

Whatever rings, the agent's reaction is the same: call `lwb_status`, grade the
waiting answer with the revealed rubric, give the three-line feedback, end with
the resume cue, continue building.

---

## 4. The learner's moments

Each moment has a trigger (what notices it), a door (where it is drawn), a
blocking rule and an exit (how the build resumes).

### 4.1 Before a build: the prediction

- **Trigger.** `UserPromptSubmit` hook classifies the prompt with a cheap rule
  (touches a tracked topic's anchors, or names a new dimension). It injects one
  line: `lwb: prediction due for topic retry-budget (level: with help).` The
  skill tells the agent to make one prediction card about the observable the
  build will show, then start work in the same turn. In Quiet mode only one
  prediction per session; in Deep mode one per build step.
- **Door.** Delivered with `mode=wait`. Desktop Code tab and CLI: the mod band
  turns from `learning · 3 due` to `1 question · press 1`, and the agent keeps
  editing files. Phone (Remote Control): the agent asks with AskUserQuestion,
  which is forwarded and stays open [D]; or the elicitation card if it is
  forwarded (experiment E-RC). Codex: `request_user_input_async` (renders in
  TUI, desktop and ChatGPT iOS [D]); falls back to elicitation at the gate.
- **The gate.** A `PreToolUse` hook matches the card's `observable` (for
  example the pytest command). If the prediction is still open, it denies once
  with reason `lwb: prediction for att_7f3a is open; call lwb_ask mode=block for
  it or mark it not_now, then rerun.` The agent then elicits (blocking) or
  records Not now. Codex has an equivalent pre-tool hook [D]; Cursor has
  `beforeShellExecution` [D]. This is the one point where the build waits, and
  it waits only if the learner chose not to answer during the dead time.
- **Exit.** Outcome runs, card flips to "You said / It did", resume cue.

### 4.2 During the build

- Periphery only. Status line (Claude Code `statusLine` command calling
  `learning.py status --line`): `learn 1 open · 3 due · normal`. Mod band in the
  same words. Codex TUI status line if configurable [S], otherwise nothing.
- `/btw` and the desktop side chat are the place to ask "how does this work?"
  without polluting history [D]. The skill tells the agent: an answer given in
  `/btw` to a question about a tracked topic gets one note in the
  event log (`asked_how`) so the record can show "asked how" as a good habit,
  never as a score.
- MessageDisplay hook strips praise phrases from learning feedback [D,
  behaviour untested].

### 4.3 When it fails: the debugging drill

- **Trigger.** `PostToolUseFailure` (Claude Code) or the Codex post-tool hook
  sees a failing test on a tracked topic. It injects:
  `lwb: offer diagnosis drill once for test_retry; do not diagnose first.`
- **Door.** A `diagnosis` card: "The test failed. Name the cause before I look.
  Pick the line." Answer type `line-pick` in the mod pane and MCP App card
  (click a line in the excerpt), `text` with `path:line` in elicitation and
  terminal. Hint ladder H0 to H3 is server-held; each hint is a
  `lwb_hint(id)` call so the hint level is recorded, not trusted.
- **Exit.** "Not now" means the agent debugs normally and says nothing more. A
  miss at `sure` confidence is marked as a hypercorrection event: plainest
  correction, review tomorrow, a mark on the record cell.

### 4.4 After it works: the explain-back

- **Trigger.** `Stop` (Claude Code), Codex `Stop` with `decision: block` once
  per passing build, Cursor `stop` with `followup_message`, Gemini `AfterAgent`.
  The hook checks the event log: tests passed in this turn, topic touched, no
  explain-back yet for this change. It injects or continues with:
  `lwb: explain-back due for retry-budget; ask once, then stop.`
- **Door.** Same tiering. This one may block (the work is done), so
  elicitation is acceptable. On desktop the mod pane opens itself only if the
  learner was idle for 20 s; otherwise the band says `1 question · press 1`.
- **Exit.** Graded feedback, record cell lights, resume cue to the next task.

### 4.5 Away

- **Trigger.** Notification `idle_prompt` hook plus presence. If no presence
  file and no terminal focus for 10 min and a card is open, send one
  `PushNotification` with the card's first line [D]. Never while present.
- **Door.** Phone: tapping opens the Claude app on the session (Remote Control),
  where the AskUserQuestion or the card text waits. If the session is not
  reachable, the card is copied to the hosted room artifact's db with
  `lwb_post`, and the push links there.
- **Exit.** Answer from the page goes back by `sendToClaudeSession` (Submit is
  the gesture) or sits in the db inbox until the next SessionStart pull.

### 4.6 Review (spaced retrieval)

- **Clock.** The platform's own: a **cloud scheduled task** (daily, minimum
  1 h interval, laptop closed, push [D]) with `create_new_session_on_fire` runs
  `learning.py due` on the repo, writes at most five due cards (three-group
  inbox: Now 1, Due up to 5, Later) to the room artifact db, and lets the task's
  push notification carry "3 reviews due". Desktop scheduled tasks for local-only
  repos [D]. Codex: no verified scheduler in this stance, so due cards surface
  at SessionStart and through a Codex Site page if the learner set one up.
- **Door.** Room artifact on the phone: the card, one-tap confidence, Submit.
  Grading on the page with the `sample` capability against the rubric fetched
  after lock (as today). In-session alternative: `/learn review` opens the mod
  pane queue on desktop; elicitation sequence in CLI and Codex.
- **Exit.** Page results are inbox entries; `learning.py import` at the next
  SessionStart folds them in. Page-graded results count as reviews; level
  changes still need an in-session or evidence-backed result where record.py
  already demands it.

### 4.7 Map

- `/learn map` (Claude plugin command and Codex skill command): text grid in
  chat (monospace, glyph per level: `·` not yet, `▁` with help, `▃` recalls,
  `▇` transfers). In the mod pane and the room artifact: the record grid in the
  site's visual language, best level as a 1.5px ink outline, latest as the fill,
  so decay shows. Calibration: three bars (guess / fairly sure / sure) with
  the share correct in each.

### 4.8 Drill and explainer

- Drills (`references/repair-drills.md`) are cards of kind `repair` with a
  planted bug; delivered through the same tiers.
- Explainers are built as artifacts in Claude (or as MCP App resources where
  those render, or as a static file opened by the local `serve` otherwise) using
  the card module for embedded predict-before-reveal prompts (Orbit pattern).
  Each embedded prompt is a real attempt with an id; answering it calls
  `sendToClaudeSession` or writes the db inbox, and it enters the review
  schedule like any other card. Page results stay weaker evidence.

---

## 5. Moment by harness

Doors in priority order; the first one that works is used.

| Moment | Claude Code, Claude app desktop (Code tab, local) | Claude Code via Claude app on phone | Claude Code CLI | Codex app (desktop) and CLI | Cursor (one more) |
|---|---|---|---|---|---|
| Before (predict) | Mod band and pane, wait mode; gate elicits | AskUserQuestion via Remote Control; cloud session: elicitation card | Mod pane; task in footer; elicitation at gate | `request_user_input_async`; elicitation at gate (blocks thread [T]) | MCP App card inline (2.6 [D]); text fallback |
| During | Status line + band | nothing (calm) | Status line + band | nothing, or status line [S] | nothing |
| Fails (drill) | Mod pane line-pick | AskUserQuestion with options | Mod pane or elicitation | elicitation form; `request_user_input` with three cause options | MCP App card line-pick |
| Works (explain-back) | Stop hook, pane or elicitation | AskUserQuestion; push if away | Stop hook, elicitation | Stop hook `decision: block`, elicitation | `stop` followup, MCP App card |
| Away | push via PushNotification, room artifact | push opens session or artifact | same as desktop | ChatGPT iOS keeps async questions [D]; Codex Site page [D] | text at next session |
| Review | cloud scheduled task + room artifact; `/learn review` pane | room artifact | `/learn review` elicitation sequence | SessionStart due list; Codex Site | SessionStart due list; card |
| Map | mod pane grid; artifact | artifact | text grid | text grid; MCP App if desktop renders | MCP App grid |
| Explainer | artifact with embedded prompts | artifact | artifact link; local file | MCP App panel if fixed; local file | MCP App |

MCP Apps in Claude Code: not rendered on any surface [T]. They are therefore
never a Claude Code door, only Claude chat and other hosts.

---

## 6. Round trips, concretely

### 6.1 Desktop Code tab with the mod (the flagship)

```
learner: "add a retry budget to the client"
UserPromptSubmit hook ── injects "prediction due: retry-budget"
agent ── lwb_ask(kind=prediction, mode=wait, observable=pytest test_retry) ── returns task/at once
lwb ── seals rubric, writes attempt, appends opened, sees mod presence ── writes .learning/now.json
mod ── watches now.json ── band: "1 question · press 1"
agent ── keeps editing client.py (the wait)
learner ── presses 1, types, taps "fairly sure", Submit
mod ── learning.py answer --id att_7f3a (writes answer, appends answered)   [mods run commands? see E-MOD2]
        and $.prompt.submit("/learn graded-ready att_7f3a", at next idle) as backup bell
monitor ── sees answered ── notification to session
agent ── reaches pytest; PreToolUse gate passes (answered) ── runs tests
agent ── lwb_lock_answer already done; reads revealed rubric; lwb_grade
agent ── "You said: ... / It did: ... Not quite. Gap: ... Back on 10 Nov. Back to: ..."
```

No copying, no command, no context switch out of the Code tab.

### 6.2 Phone through Remote Control

The local session runs on the laptop against the real repo. The agent uses
AskUserQuestion for the card (options: the confidence levels attached to a free
answer via "Other", or a choice card for diagnosis). Remote Control forwards it
and keeps it open [D]. The answer is a normal tool result in the session, so
the bell is implicit. The rubric stays in `seals/`.

### 6.3 Cloud session (web or phone Code tab)

Elicitation renders as a card [D]. `lwb` runs as a project MCP server from
`.mcp.json`. The record is committed on the session branch; union merge joins it
with the laptop later [T]. Scheduled review tasks are cloud sessions of this kind.

### 6.4 Hosted room artifact

`lwb_post` writes the card (no rubric) to the artifact db through the agent's
`ArtifactData` call; rubric goes to a separate db doc read only by the page's
grade step after lock. Submit is the viewer gesture that calls
`room.sendToClaudeSession(...)`; if `canSendToClaudeSession()` is false, the
answer stays in db as an inbox row. The artifact may later call `host:learning`
through the `mcp` capability to write the repo record directly when opened in the
Claude desktop app [S].

### 6.5 Codex app and CLI

`lwb` configured in `~/.codex/config.toml` or the repo's `.codex/config.toml`.
Codex advertises elicitation form and url to every server [T]; the thread waits
in `waitingOnApproval` [T]. For non-blocking prediction the skill instructs Codex
to use `request_user_input_async` [D] and to pass the learner's answer to
`lwb_lock_answer`. Stop hook `decision: block` produces the explain-back [D].
If Codex desktop renders MCP Apps (issue 21019 closed 2026-08-05 [R]), the same
card resource appears as a panel.

### 6.6 Cursor

Reads `.claude/skills` and `.agents/skills` [D]. `lwb` in `.cursor/mcp.json`.
MCP App card renders inline (2.6 [D]); the card submits by calling
`lwb_lock_answer` with `tools/call` from the app, never by `ui/message`
(VS Code only fills the input box [D]). `stop` hook `followup_message` gives the
explain-back [D].

---

## 7. State and sync

- **Source of truth:** `.learning/` in the repo, written only through record.py
  (via `learning.py` or `lwb`). Agents never hand-edit.
- **Inboxes, not replicas:** artifact db, Codex Site D1, ChatGPT/Remote Control
  answers that land outside the repo. Each row carries the attempt id; `import`
  is idempotent. SessionStart runs `learning.py inbox --count` and injects
  "N answers waiting on the page" so the agent pulls them with `ArtifactData`.
- **Branches:** one file per attempt plus union-merged JSONL merges laptop,
  cloud-session and scheduled-task branches without conflict [T]. Scheduled
  review sessions push to a `learning/review` branch; SessionStart on the laptop
  offers to merge it (one line, no prompt if Quiet).
- **Presence:** mod writes `.learning/.presence/mod-<pid>` with a heartbeat;
  `CLAUDE_CLIENT_PRESENCE_FILE` [D] for terminal focus. Both are gitignored.
- **Compaction:** `PreCompact` hook writes the in-flight card id and the
  resume cue to `.learning/now.json`; SessionStart and post-compact context
  restores them so a half-answered card is not lost [D].

---

## 8. Rubric privacy

Threat model: not a cheating adversary (the learner is the only user), but
**accidental spoiling**. Seeing the rubric in a transcript before answering
destroys the retrieval. Today `learning.py ask --rubric "..."` prints in a
visible Bash call in Claude Code and Codex [S, likely].

Design:

1. The rubric never travels in a Bash command. The agent writes it through
   `lwb_ask` (an MCP tool call). Where the harness shows MCP tool inputs
   expanded, the skill instead has a forked subagent (`context: fork`) call
   `lwb_ask`, so the main transcript shows only "sealing rubric" (experiment
   E-SEAL compares what each harness shows).
2. `lwb` stores the rubric in `seals/<id>.rubric` and puts only
   `sha256(rubric + salt)` in the attempt file. On `lwb_lock_answer`, it reveals
   the rubric and the salt; `learning.py check` verifies the hash, so anyone can
   audit that the rubric was not changed after the answer.
3. Doors never receive the rubric before lock. The MCP App card calls an
   app-only `lwb_lock_answer` (hidden from the model's tool list per the Apps
   spec visibility field [D]) which returns the rubric for the reveal view.
   The room artifact stores the rubric in a separate db doc fetched only after
   lock; a curious viewer with devtools can read it, which is acceptable under
   this threat model and stated on the page.
4. URL-mode elicitation is the strongest form: the answer page is outside the
   model's reach and the model never sees the learner's raw input until lock
   [D]; used for rich answers (sketch, line pick) in text-only hosts.

---

## 9. Offline and failure behaviour

| Failure | Behaviour | Learner sees |
|---|---|---|
| No network | Everything local still works: mod, `lwb`, hooks, record. Artifact and scheduled tasks pause. Cards meant for the phone stay in `now.json`. | Nothing changes at the machine. |
| Mod not installed or surface cannot draw mods (phone, cloud) | Door 1 unavailable; server falls to elicitation or text. | Same card, plainer. |
| Client lacks elicitation | Text card in chat; learner replies in chat; the agent calls `lwb_lock_answer` with the reply. | Card as monospace block with key hints. |
| Elicitation declined or cancelled | Recorded as `not_now`; no retry this session. | Nothing more. |
| Gate hook misfires (observable never runs) | Open prediction expires at Stop; recorded `skipped`, no penalty. | One line: "Prediction closed unanswered." |
| Bell never rings (monitor dead) | SessionStart and Stop both run `lwb_status`; the answer is graded at the next turn end at worst. | Feedback a turn later. |
| Artifact cannot send to session | Answer stays in db inbox; pulled at next SessionStart. | "Saved. Your next session will grade it." |
| Two doors answer the same card | First `lock` wins (server-side atomic rename); the second gets "Already answered on the phone." | That line. |
| Record invalid | `learning.py check` exits 1; hooks go silent and say once "learning record needs a check". | Build continues. |
| Learner says stop | `/learn pause` sets `paused`; every hook exits 0 silently. | Nothing until `/learn resume`. |
| Three ignored nudges | Scheduler stops nudging; one inbox line remains. | "Reviews paused. /learn review when you want them." |

---

## 10. What must be built

| # | Component | Contents | Size |
|---|---|---|---|
| B1 | `lwb` MCP server | stdio, stdlib Python, tools in 3.3, door negotiation, elicitation form and url, tasks extension (optional), MCP App resource `ui://lwb/card`, events.jsonl writer. Shares record.py. | ~600 lines |
| B2 | record.py / learning.py additions | `events.jsonl`, `status --line`, seals and hash check, `reviews.jsonl` FSRS log, inbox idempotency, confidence levels, `door` field, `.gitattributes`, `pause`, `mode`. | ~250 lines |
| B3 | Claude Code plugin | skill (moved under the plugin), `.mcp.json` for `lwb`, hooks (SessionStart with asyncRewake, UserPromptSubmit, PreToolUse gate, PostToolUseFailure, Stop, PreCompact, Notification), monitor on events.jsonl, statusLine script, `/learn` commands (review, map, drill, not-now, pause, mode), output style "Plain" coexisting with Learning style. | ~400 lines config + scripts |
| B4 | Claude Code mod | Band above prompt, pane (Input, Select, Button, Code excerpt, line pick), keys (1 open, J/K, H snooze, Enter, Esc, 1 to 3 confidence once open), `$.prompt.submit` at idle, presence heartbeat. | ~500 lines JS |
| B5 | Card module | One `card.css` + `card.js` from site tokens (paper, ink, accent, ramp, Instrument Sans wdth 88 / 650, JetBrains Mono, 1.5px #DAD8D0, 16px radius, pill buttons, reduced motion). Used by MCP App resource, room artifact, `serve` page, explainer embeds. A text renderer gives the same anatomy in monospace for chat, terminal and push bodies. | ~400 lines |
| B6 | Room artifact v2 | Inbox (Now 1 / Due 5 / Later), card, "You said / It did", record grid with outline + fill + glyph + table view, calibration bars, faint weekly cells, `sendToClaudeSession`, `setAppBadge` if available, db as inbox. | rework of assets/room.html |
| B7 | Codex pack | `.agents/skills/learning-while-building` (Claude path symlinked), `agents/openai.yaml`, `.codex/config.toml` snippet, `hooks.json` with Stop block-once and SessionStart, AGENTS.md lines. | ~100 lines |
| B8 | Cursor pack | `.cursor/mcp.json`, `hooks.json` with `stop` followup and `beforeShellExecution` gate. | ~60 lines |
| B9 | Scheduler prompt | Cloud scheduled task prompt (due, cap 5, novelty, nudge ledger, three-strike stop, presence-aware) and desktop scheduled task variant. | ~60 lines |
| B10 | Conformance test | One script that drives `lwb` with a fake client for each capability set (mod, ui, form, none) and checks the same card text, the same attempt file and the hash reveal. | ~200 lines |

**Milestones.**
M0 (1 day): B2 + B1 text and elicitation tiers + B10. Proves the round trip in
the CLI and Codex. M1: B3 hooks + monitor + status line; the flagship flow
without the mod. M2: B4 mod + B5 card; the desktop experience. M3: B6 + B9; the
phone and review loop. M4: B7 + B8; other harnesses and MCP App card.

**Accessibility, built into B4 to B6.** Record ramp fails 3:1 for two shades
[T], so filled cells get a 1.5px ink outline and a glyph; each cell's
accessible name says the level in words; a table view sits under every grid.
Cards are a `form` with a labelled `fieldset` for confidence (radio group, not
colour), `role=status` for feedback, focus returns to the prompt after Submit,
all actions have keys and visible key caps, reduced motion removes the cell
light-up. Phone targets at least 44px.

**Copy rules.** Learner-facing: "Correct." / "Not quite." / "No.", then the
gap, then "Back on <date>.", then "Back to: <task>." No praise, no streak words,
no em dashes. Not now is always one key and one tap.

---

## 11. Dependency register

| Dependency | Status | Cheapest experiment |
|---|---|---|
| MCP elicitation form in Claude Code CLI | [T] 2.1.319 declares form and url; hook answers it | Done. Re-run B10 against each release. |
| Elicitation as cards in Claude Code cloud sessions (web, phone) | [D] | E-CLOUD: commit `.mcp.json` with `lwb`, open a cloud session on the phone, call `lwb_ask mode=block`, note how a titled enum renders. |
| Elicitation in the desktop Code tab (local) | [S] | E-DESK: same call from the desktop Code tab; screenshot. |
| Elicitation forwarded through Remote Control to the phone | [S] | E-RC: `/remote-control`, trigger a block elicitation, open on the phone. If not forwarded, AskUserQuestion stays the phone door. |
| AskUserQuestion forwarded and kept open by Remote Control | [D] | E-RC2: ask one card with AskUserQuestion, answer on the phone after 10 min. |
| Mods draw band and pane in CLI, desktop Code tab, VS Code | [T] validate + unit test on 2.1.319; rendering [D] | E-MOD: `claude --plugin-dir ./lwb-mod` with a fake `now.json` in CLI and desktop; band renders, 1 opens pane, `/learn` works mid-turn. |
| Mod can run a local command or write a file on Submit | [S] | E-MOD2: from a pane Button handler, write `.learning/inbox/x.json` or call `$.prompt.submit`; check which works. If neither writes files, the mod submits `/learn answer <id> ...` as an immediate command. |
| `$.prompt.submit` queues at next idle without stopping the build | [D] | Part of E-MOD. |
| Plugin monitor wakes an idle session | [D] | E-MON: monitors.json with `tail -F events.jsonl`, append from another terminal, check notification in CLI and desktop. |
| asyncRewake SessionStart hook wakes idle session | [D] | E-WAKE: hook waits for `inbox/*.json` and exits 2; drop a file. |
| Session inbox socket framing | [D] exists [T], format undocumented | E-SOCK: background child writes auth + one line; observe with `--debug`. |
| PreToolUse deny-with-reason as the prediction gate | [D] | E-GATE: hook matches `pytest`, denies once while `now.json` is open; check the agent calls `lwb_ask mode=block` and reruns. |
| PostToolUseFailure, Stop, PreCompact, Notification idle_prompt, UserPromptSubmit context | [D] | E-HOOKS: one throwaway settings file logging each event with payload during a real build. |
| MessageDisplay can strip praise | [D], effect untested | E-MSG: hook replaces "Great job" with "" in a test turn. |
| statusLine command shows learning count | [D] | Point statusLine at `learning.py status --line`. |
| MCP tasks extension in Claude Code (CLI footer) | [D] | E-TASK: tool returns a task that completes when a file appears; watch footer. |
| MCP Apps in Claude Code | [T] not rendered | Re-test only when release notes mention MCP Apps. |
| MCP Apps in Claude chat, ChatGPT, VS Code, Cursor 2.6 | [D] | E-APPS: point VS Code and Cursor at `lwb`; card submits via `tools/call`. |
| MCP Apps in Codex desktop | [R] fixed per issue 21019 closure; brief says no | E-CDX-APP: `experiments/mcp-app/server.py` in the current ChatGPT desktop Codex view. |
| App-only tool visibility for `lwb_lock_answer` | [D] Apps spec | Included in E-APPS: confirm the model's tool list omits it. |
| SEP-3118 app-rendered elicitation | [S] not merged | Watch ext-apps PR 733; run the reference inspector branch with our card. |
| URL-mode elicitation and `elicitation/complete` resume | [D] Claude Code, [S] Codex presentation | E-URL: elicit url to a room artifact anchor from CLI and Codex; check consent UI and resume. |
| Codex elicitation form blocks thread | [T] 0.167 | Done. |
| Codex `request_user_input_async` on TUI, desktop, ChatGPT iOS | [D] | E-CDX-ASYNC: one prediction with three options, answer from iOS. |
| Codex Stop hook `decision: block` | [D] | E-CDX-STOP: block once after passing tests with explain-back prompt. |
| Codex pre-tool hook for the gate | [D] | Fold into E-CDX-STOP. |
| `.agents/skills` read by Codex, Cursor, VS Code, Gemini | [D] | Symlink, run `/skills` in Codex and Gemini. |
| Cursor `stop` followup_message auto-submit, `beforeShellExecution` | [D] | E-CUR: one build in Cursor with both hooks. |
| Room artifact `sendToClaudeSession` / `sendToClaude` on phone and desktop | [D] | E-ROOM: publish room v2 with `room: {}` and `comments: {}`, log `canSendToClaudeSession()` on both, press Submit. |
| Artifact `mcp` capability reaching `host:learning` | [S] | E-HOSTMCP: page declares `host:learning`, calls `listTools()` in desktop app and phone. |
| `navigator.setAppBadge` on an installed artifact | [S] | Feature-detect on iOS and Android home-screen install. |
| Cloud scheduled task with push, fresh session, repo access | [D] | E-SCHED: daily task running `learning.py due` and writing the room db; read the push. |
| PushNotification and presence suppression | [D] | E-PUSH: Notification hook fires while terminal focused (expect no push) and while away (expect one). |
| Union merge for JSONL | [T] | Done; add `.gitattributes` in B2. |
| Rubric not visible through MCP call or forked subagent | [S] | E-SEAL: screenshot `learning.py ask` vs `lwb_ask` vs forked subagent in Claude Code CLI, desktop and Codex. |
| Wait-time prediction is not worse than before-build | [S] | E1 from learning-science: alternate placement for two weeks; log answer time, skips, next-prompt delay. |
| Side-by-side consolidation helps 7-day recall | [D] lit | E2: half the predictions get "You said / It did"; compare. |

---

## 12. Re-plan triggers

- **E-MOD2 fails** (mods cannot write or submit answers): the pane becomes a
  view only, and Submit sends `/learn answer` through `$.prompt.submit`
  immediate commands; if that also fails, the band stays as a periphery signal
  and answers go through elicitation.
- **E-RC fails and AskUserQuestion is unreliable on the phone:** the phone door
  becomes the room artifact only, with a push deep link
  (`claude.ai/code/session_<id>` or the artifact anchor).
- **E-SEAL shows rubrics in every transcript:** move rubric authoring to the
  grading step only (rubric written by a forked subagent that never returns
  text), and keep commit-reveal for audit.
- **E1 shows wait-time prediction is skipped often:** default to blocking at
  the gate in Normal mode and keep wait mode for Deep.
- **Claude Code ships MCP App rendering:** door 2 moves above door 3 for Claude
  Code and the mod pane becomes optional on desktop.
- **Codex desktop renders MCP Apps (E-CDX-APP passes):** the card panel becomes
  Codex desktop's primary door, elicitation stays for the CLI.
