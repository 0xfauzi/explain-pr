# Companion architecture: one learning app, many doors

Status: design proposal, 2026-11-07. Stance: **Companion surface**. One excellent
learning app, the Room, that every agent hands off to and gets answers back from.
It ships as an installable web app (PWA) on the GitHub Pages origin and as a
private hosted page on claude.ai, from one codebase. Push notifications, deep
links and a sync layer (git plus small private inboxes) make it reachable from
the phone and from every harness.

Verification tags used below: **[T]** verified by test in this project,
**[D]** documented by the vendor, **[R]** reported by third parties,
**[S]** speculative (our inference, not yet tested). Each dependency has a
cheapest experiment in section 11.

---

## 1. What "seamless" means here

Seamless does not mean "the learning layer is everywhere all the time". The
research (calm tech, interruption science, Shen and Tamkin) says the opposite:
the learning layer stays in the periphery and moves to the centre only at the
two research-backed moments (before a build, after it works) or on the
learner's gesture. Seamless means four testable properties:

1. **No copying.** The learner never copies a question, an id, a URL or an
   answer between surfaces. Every handoff is a tap, a key or nothing.
2. **No re-explaining.** The card the learner sees on any door is the same
   object, with the same id, prompt, excerpt and state. Opening it anywhere
   shows where it stands (waiting, locked, graded).
3. **No stall.** The build never waits on the learner except for the one
   prediction before a build, which the learner chose to answer (and can skip
   with "Not now").
4. **Resume in one line.** Every detour ends with a resume cue that names what
   the agent is doing now and what is next ("Back to the build: Claude is
   running the queue tests. Next: the retry backoff in queue.py:88.").

Acceptance test for the whole architecture: the owner starts a build in
Claude Code on the laptop, walks away, answers the explain-back on the phone
from a push, and when they sit back down the session already has the grade in
context and the Room on the laptop shows the feedback. Zero typed commands,
zero copied strings.

---

## 2. The shape in one picture

```
                         +-----------------------------------------+
                         |              THE ROOM (one app)         |
                         |  Now / Due / Later inbox, Card, Compare, |
                         |  Map, Drill, Explainer host, Modes       |
                         +--------+-------------+------------------+
                                  |             |
                 host A: PWA      |             |  host B: claude.ai artifact
   0xfauzi.github.io/explain-pr/app/            |  (db, sample, room, comments,
   (Web Push, badge, offline, installable)      |   user, mcp capabilities)
   also served locally by learning.py serve     |
                                  |             |
                   store adapter: |             | store adapter:
              GitHub inbox repo   |             | artifact db
              or local files      |             |
                                  v             v
   +------------------------------------------------------------------+
   |                    INBOXES (untrusted, append-only)               |
   |  .learning/inbox/ (local)   inbox repo   artifact db   MCP server |
   +------------------------------+-----------------------------------+
                                  |  learning.py import (idempotent by
                                  |  attempt id, earliest lock wins)
                                  v
   +------------------------------------------------------------------+
   |          CANONICAL RECORD: .learning/ plain files in git          |
   |   topics/, attempts/, sealed/, events.jsonl (union merge)         |
   +------------------------------------------------------------------+
                                  ^
        bells (answer arrived)    |   cards out (question posted)
   monitor, inbox socket, sendToClaude, MCP elicitation complete,
   Codex turn/steer, ntfy wake, Stop hooks
                                  |
   +------------------------------------------------------------------+
   |  HARNESSES: Claude Code (CLI, desktop Code tab, phone via Remote  |
   |  Control, cloud), Codex (CLI, app, iOS), Cursor                   |
   +------------------------------------------------------------------+
```

Three ideas carry the design:

- **The card is the unit.** A question is a Card object with an id, and every
  door renders the same Card (research: "one unit, many doors").
- **Inboxes are dumb; the record is git.** Every surface writes answers into
  an inbox it can reach. Only `learning.py import` writes the canonical
  record, with the attempt id as idempotency key. No CRDTs, no server of
  record.
- **Bells are separate from data.** Telling a running session "an answer
  arrived" is a different channel from carrying the answer. Bells carry no
  content, so they can use any transport, including insecure ones (ntfy).

---

## 3. The Card and its lifecycle

### 3.1 Card object

Stored at `.learning/cards/<attempt-id>.json` in the record (new, alongside
the existing `attempts/`). The PWA and artifact receive only the public view.

```json
{
  "id": "a_20261107T141502_3f9c2e",
  "v": 1,
  "kind": "explain-back",            // attempt | explain-back | review | transfer | drill | explainer-prompt
  "topic": "idempotent-retries",
  "dimension": "distributed-systems",
  "level_now": "with help",          // drives question type (expertise reversal)
  "prompt": "The retry now sends the same request key twice. What stops the charge running twice?",
  "excerpt": {"path": "billing/charge.py", "lines": [41, 58], "text": "..."},
  "answer_shape": "text",            // text | choice | line-pick | order
  "choices": null,
  "rubric_seal": "sha256:9a1f...",   // commit-reveal, see section 8
  "posted_at": "2026-11-07T14:15:02Z",
  "due_at": null,
  "return": {                        // where to ring the bell; any subset
    "claude_session": "session_013c...",
    "artifact": "https://claude.ai/code/artifact/...",
    "mcp": {"server": "learning", "elicitation_id": "el_77"},
    "codex_thread": "thr_..."
  },
  "resume_cue": "Claude is running the billing tests. Next: wire the key into the webhook path.",
  "state": "posted"
}
```

### 3.2 Lifecycle (one state machine for every door)

```
drafted -> sealed -> posted -> seen -> locked -> graded -> consolidated -> scheduled
                         \-> snoozed (Not now) -> posted
                         \-> dont_know (locks as a real low-confidence answer)
```

- **sealed**: rubric written, hash stored. Nothing can be posted unsealed. This
  is the existing ground rule "fix the rubric first", now enforced by code.
- **locked**: answer plus confidence saved. Irreversible. If two doors lock the
  same card (phone and laptop), the earliest `locked_at` wins, which matches
  `record.py`'s existing merge rule. The later lock is kept as `superseded`
  for audit.
- **graded**: outcome word, feedback (120 words max), gap, hint level.
- **consolidated**: for predictions, the learner has seen prediction and
  outcome side by side (productive failure needs this step). For misses, the
  one-line restatement was offered.
- **scheduled**: next review date from the 3/7/21/60/180 ladder, next day
  after a miss, earlier still after a high-confidence miss (hypercorrection).

Every transition appends one line to `.learning/events.jsonl`
(`*.jsonl merge=union` in `.gitattributes`, [T]). That file is the bell feed
for monitors and watchers.

---

## 4. The learner's moments

Each moment names its job, what the Room shows, and the research behind it.
Section 5 maps each to a door per harness.

| Moment | Job | Room screen | Basis |
|---|---|---|---|
| **Before a build** | One prediction about the one observable the build will show. Optional, skippable. | Card, short. Answer field, confidence (Guess / Fairly sure / Sure), I don't know, Not now. | Prequestions help only the content asked (St. Hilaire 2024); productive failure (Kapur). |
| **During** (agent working) | Use dead time: the prediction, or one due review, while the agent runs a long step. Never blocks. | Band count "1 question" in the build surface; Card opens on gesture. | Wait-learning (Cai 2015), breakpoints (Iqbal and Bailey). [S] for coding agents. |
| **Debugging** (test fails) | Offer once: "Call the cause first?" The learner states a hypothesis before the agent debugs. | Drill card with the failing output and a line picker. | Shen and Tamkin: delegating debugging lost the most. |
| **After it works** | Explain-back, then prediction vs outcome side by side. | Compare screen: "You said / It did / Why", with path:line. | Generation then comprehension cluster (86%); consolidation. |
| **Away** | The learner is not at the machine. Questions wait; one passive push at most. | Inbox with Now (max 1), Due (max 5), Later. | Calm tech; Duolingo recency penalty; presence rule. |
| **Review** | Spaced retrieval and transfer, 3/7/21/60/180, miss returns next day. | Due inbox, J/K, 1-3 confidence, Enter. | Cepeda 2008, successive relearning, Bastani 2025 (answers stay hidden). |
| **Map** | What the learner can do without the agent, per dimension, with decay visible. | Record grid: best level as outline, latest as fill; calibration three-bar chart; table view. | Hypercorrection, calibration (Metcalfe), AI illusion of competence. |
| **Drill** | Repair drill on an injected bug in a scratch branch. | Drill screen: symptom, hypothesis, line pick, then the agent reveals. | Repair drills reference; debugging gap. |
| **Explainer** | Interactive page with predict-before-reveal prompts that enter the review schedule. | Explainer host: page in the site language with embedded Cards (Orbit-style). | Quantum Country mnemonic medium. |

Copy rules for every screen: outcome word first ("Correct." / "Not quite." /
"No."), no praise, a "where next" line ("No. Back tomorrow."), the resume cue
on every return, no em dashes.

Support adapts to level (Kalyuga expertise reversal): `not yet` gets a
labelled worked example then a completion question, `with help` gets
completion problems, `recalls` gets predict and explain, `transfers` gets
design-first and new-context questions with no long explainers.

---

## 5. Where each moment happens, per harness

Doors are ranked. The first one that works on that surface is used; the rest
are fallbacks. "Room" means the companion app on whichever host fits.

### 5.1 Claude Code in the Claude desktop app (Code tab, local session)

| Moment | Door (ranked) | Answer returns by |
|---|---|---|
| Before | 1. Mod pane (band "1 question", key 1) [T: probe mod validated]. 2. AskUserQuestion. 3. Chat. | Mod: `$.prompt.submit` queues grading at next idle. Chat: direct. |
| During | Mod band count. Gesture opens the mod pane or the Room in the desktop Browser pane (`.claude/launch.json` points at `learning.py serve`) [D]. | Room local: writes `.learning/inbox/`, plugin monitor on `events.jsonl` notifies the session [D]. |
| Debugging | `PostToolUseFailure` hook adds "Call the cause first? (1)" to the band, once per failing test [D]. | Mod pane or Room drill. |
| After | `Stop`/`TaskCompleted` hook posts the explain-back card [D]; band lights; Compare screen in the Room. | As above. |
| Away | PushNotification to phone only if presence file is absent and Remote Control is attached [D]. | See 5.2. |
| Review, Map, Drill, Explainer | Room in the Browser pane, or `/learn review` (instant mod command). | Monitor bell. |

### 5.2 Claude Code in the Claude app on the phone (Remote Control to the laptop)

The session runs on the laptop against the real repo. The phone is a window.
Mods do not draw on the phone [D], so the Room carries the UI.

| Moment | Door | Answer returns by |
|---|---|---|
| Before / After | Forwarded AskUserQuestion stays open on the phone [D]. For richer cards, a push opens the **artifact Room** in the Claude app. | AskUserQuestion: native. Artifact: `room.sendToClaudeSession` or `comments.sendToClaude` on Submit (the tap is the required gesture) [D]. The session reads the db with ArtifactData, grades, writes feedback back to the db. |
| Away / Review | Push (one per day max). Tap opens the artifact Room on the Due inbox. | Same. Grading on the page with `sample` when no session is attached [T: existing hosted page grades]. |
| Map | Artifact Room, Map tab, from db mirror of the record (pushed by `room-push`). | None needed. |

### 5.3 Claude Code CLI (terminal, local)

| Moment | Door | Answer returns by |
|---|---|---|
| Before / After | Mod band and pane in the terminal [T]. Without the plugin: MCP elicitation form from the learning server (answer, confidence enum, dont_know) [T: CLI declares elicitation form and url]. | Elicitation: returns in the tool result. Mod: `$.prompt.submit`. |
| During | Band count. `learning.py answer` in a second terminal [T: exists]. | Monitor on `events.jsonl`; without plugins, `asyncRewake` SessionStart hook exits 2 on a new answer file [D]. |
| Handoff to Room | URL-mode elicitation opens `http://127.0.0.1:8765/#/c/<id>` (local serve). Client shows the URL and asks consent [D]. | Room posts to the same local server; server sends `notifications/elicitation/complete`; turn resumes [D, chain S]. |

### 5.4 Claude Code cloud session (web, phone app)

Elicitation forms render as cards [D]. The repo is a clone, so the record
syncs by commit and push on the session branch. The artifact Room is the
companion; `sendToClaude` reaches the publishing cloud session [D].
Cloud scheduled tasks run review days with the laptop closed (section 7.4).

### 5.5 Codex CLI and Codex app (desktop, inside ChatGPT desktop) and ChatGPT iOS

| Moment | Door | Answer returns by |
|---|---|---|
| Before | MCP elicitation form from the learning server; thread waits in `waitingOnApproval` [T]. | Tool result. |
| During | `request_user_input_async` (renders in TUI, desktop and ChatGPT iOS; stays after the turn) [D]. | Native reply into the thread. |
| After | Codex `Stop` hook with `decision: block` and an explain-back prompt, once per passing build [D]. Desktop: MCP App card if it renders (issue 21019 closed 2026-08-05) [R, re-test]. | Card submits with `tools/call` to the learning server. |
| Handoff to Room | URL-mode elicitation to local Room (desktop) or PWA (phone) [S for presentation]. | Local: same-process server. Phone PWA: inbox repo, then the **Codex bridge** (`learning.py bridge codex`, an app-server client) calls `turn/steer` with "Answer saved for card X" [D, chain S]. |
| Away / Review | PWA push; or Codex Sites as host C later [D]. | Inbox repo, imported at next session start (SessionStart hook injects "2 answers waiting"). |

### 5.6 One more: Cursor

Reads `.agents/skills` and `.claude/skills` [D]. MCP App cards render inline
(2.6) [D]: the Room's Card component is also built as a `ui://` resource
whose Submit calls `tools/call lock_answer` (not `ui/message`, which does not
auto-send in VS Code-family hosts [D]). The `stop` hook's `followup_message`
auto-submits the explain-back [D]. Away and review go through the PWA.

### 5.7 Fallback for any harness (Zed, Gemini CLI, plain shell)

Plain-text card in chat with a link to the Room, plus `learning.py answer`.
The SessionStart hook (where supported) injects "N answers waiting" so the
agent imports at the next session. Always works; never seamless. This is the
floor, and the design must never break it.

---

## 6. Moving a question out and the answer back, with no copying

### 6.1 Out: three delivery modes

The agent picks the mode from presence and moment, never the learner:

| Mode | When | Mechanism |
|---|---|---|
| **Inline** | Learner at the machine, moment is before or after a build. | Mod pane, elicitation form, AskUserQuestion, request_user_input. |
| **Handoff** | The card needs a rich surface (line picker, diagram, drill, explainer). | URL-mode elicitation or deep link to `/#/c/<id>` on the Room. Agent keeps working unless the card is a prediction. |
| **Deferred** | Learner away or busy. | `learning.py post` writes card to inboxes; push only if away and under the daily cap. |

Presence rule (copied from Claude Code): if the learner is at the machine
(typing, focused, or `CLAUDE_CLIENT_PRESENCE_FILE` present), never push to
the phone [D]. If Remote Control is attached and the terminal is idle, push
one line. If nothing is attached, the card waits; the scheduled task sends at
most one nudge a day, on a new topic each time, and stops after three ignored
nudges, leaving one inbox line.

### 6.2 Back: the bell table

Data travels through inboxes. The bell says only "card X changed". Ranked
per surface:

| Surface where the answer was given | Data path | Bell to the running session | Status |
|---|---|---|---|
| Mod pane | in-process | `$.prompt.submit` (queued at idle) | [T] mod validated; submit path [D] |
| Room on local serve | `.learning/inbox/<id>.json` | plugin monitor `tail -F events.jsonl`; or inbox socket post from `learning.py serve` when started from the session; or `asyncRewake` hook | [D] each, chain [S] |
| Elicitation form or URL | MCP server | tool result / `elicitation/complete` | [T] form; [D] url |
| Artifact Room | artifact db | `room.sendToClaudeSession` or `comments.sendToClaude` | [D] |
| PWA on phone | inbox repo commit | laptop `learning.py watch`: ntfy wake (SSE, content-free) plus GitHub ETag poll every 30 s; emits a line to `events.jsonl`; monitor notifies | [T] ntfy publish; rest [D/S] |
| PWA, no session anywhere | inbox repo commit | Grader Action (section 7.5) | [D] parts, chain [S] |
| Codex thread | MCP server or native | tool result / `turn/steer` via bridge | [T] elicitation; [D] steer |

What the session does on a bell: run `learning.py import`, grade against the
sealed rubric (rubric revealed only now), write feedback, then post the
resume cue. If the learner is in the conversation, two lines: what was graded
and where to read it. Otherwise nothing in chat; the feedback appears on the
Room that sent it (local serve via Server-Sent Events, artifact via db
subscription, PWA via the inbox repo plus a "Graded" push if away).

### 6.3 Deep links (both directions)

- **Into the Room**: `https://0xfauzi.github.io/explain-pr/app/#/c/<card-id>`
  (PWA), `<artifact-url>#c=<card-id>` (artifact), `http://127.0.0.1:8765/#/c/<id>`
  (local). The fragment never reaches a server, so card ids do not leak in logs.
  One resolver picks the right host: on a phone with the PWA installed, the
  PWA; inside the Claude app, the artifact.
- **Back to the build**: the Room's "Back to the build" button uses the
  card's `return` field: `claude.ai/code/session_<id>` (web and phone),
  `claude://code/new?q=`, `claude-cli://open?repo=&q=`,
  `vscode://anthropic.claude-code/open?session=` [D]. None of these sends a
  prompt [D], which is correct here: the bell already told the session. The
  link only brings the window forward, with the resume cue shown on the Room
  as the last thing the learner reads.

---

## 7. State and sync

### 7.1 Canonical record

`.learning/` plain files in git, as today, plus `cards/`, `sealed/` and
`events.jsonl`. One file per attempt makes git merges clean [T].

**Privacy problem found while designing:** explain-pr is a public repository,
so a record committed to it is public, and any branch of it is public too.
Rule: if the project repo is public, the record lives in a separate private
repo (`<owner>/learning-record`), checked out at `.learning/` as a nested
clone and ignored by the project repo. `learning.py init` detects a public
remote with `gh repo view --json visibility` and proposes this. Private
project repos keep the record in-tree.

### 7.2 Inboxes

| Inbox | Who writes | Who reads | Holds rubrics? |
|---|---|---|---|
| `.learning/inbox/` | local serve, `learning.py answer`, mod | `import` | No |
| **inbox repo** `<owner>/learning-inbox` (private) | PWA via GitHub REST with a fine-grained token scoped to this one repo (contents: read/write) | laptop watcher, Grader Action, cloud tasks | No, only `rubric_seal` |
| artifact db | artifact Room | session via ArtifactData; `room-pull` | Today yes (for on-page grading); see 8.3 |
| MCP server | elicitation, App card | server writes `.learning/inbox/` directly | Server-side only |

Card files flow out the same way: `learning.py post` writes the public card
view to every configured inbox (`room-push` already does this for the
artifact db).

Why a GitHub repo and not a new backend: it is private, has an API with CORS
from the browser, ETags for cheap polling, history for audit, and the owner
already trusts it. The token lives in the PWA's IndexedDB on the phone,
scoped to one repo that holds no rubrics. Version 2 replaces the pasted token
with a GitHub App and a 40-line Cloudflare Worker for the OAuth exchange
(GitHub's device-flow endpoints do not send CORS headers, so a pure-browser
login is not possible [R]).

### 7.3 Import rules

- Idempotent on attempt id. Re-importing the same inbox is a no-op.
- Earliest `locked_at` wins; later locks are stored as `superseded`.
- Answers on cards whose seal does not match the record are rejected and
  logged (catches stale or forged cards).
- Imported inbox files are deleted from the inbox repo in the same commit
  that writes them to the record, so the inbox stays small.

### 7.4 Platform clock for spaced review

- **Cloud scheduled task** (the default): daily, `create_new_session_on_fire`,
  `notifications {push: true}`. Prompt: run `learning.py due`, write due cards
  to the artifact db and inbox repo, send at most one Web Push, grade any
  waiting answers, commit and push the record [D]. Runs with the laptop
  closed. Minimum interval 1 h [D].
- **GitHub Actions cron** on the inbox repo: sends Web Push for Codex-only
  users (no Claude account needed) with `pywebpush` and a VAPID secret
  [D, chain S].
- Session-only timers (`/loop`, CronCreate) are not used for the schedule;
  they expire after 7 days [D].

### 7.5 Grading when no session is running

Feedback should arrive soon after a miss, so the system grades where it can:

1. A session is attached: the session grades within seconds of the bell.
2. Artifact Room: the page grades with `sample` against the rubric [T today].
3. PWA with nothing attached: the **Grader Action** on the inbox repo (on
   push) checks out the private record repo with a deploy key, runs
   `anthropics/claude-code-action` with the skill, grades against the sealed
   rubric, writes feedback to the inbox repo and the record [D parts, S
   chain]. Typical delay 1 to 3 minutes; the Room shows
   "Saved. Feedback in a few minutes." and a push "Graded" if away.
4. Nothing else works: graded at the next session start (SessionStart hook
   injects "2 answers waiting"). The Room says "Saved. Graded when Claude
   next runs."

Only grades by Claude count toward levels (existing rule in `record.py`).

### 7.6 FSRS-ready log

Every grade also writes `(topic, timestamp, rating 1-4, confidence)` to
`events.jsonl` so FSRS-6 can be replayed offline later, without changing the
ladder now.

---

## 8. Rubric privacy

### 8.1 Threat model

The learner owns everything and could read any rubric. The goal is not
secrecy against the owner; it is that **the rubric never reaches the
learner's eyes by accident before the answer locks**, and that it is
**provably fixed before the question**. Accidents today [S, untested]:
`learning.py ask --rubric "..."` is a visible Bash command in Claude Code and
Codex; the hosted page holds the rubric in its db.

### 8.2 Design

1. **Write rubrics out of sight.** In Claude Code, a forked subagent
   (`context: fork` skill or Task) writes the card and rubric; the main
   transcript shows only "Card sealed: a_...". In every harness, the learning
   MCP server's `seal_card` tool takes the rubric as input; harness UIs
   collapse tool inputs by default [S, check per harness]. Never through a
   visible Bash argument; `learning.py ask` gains `--rubric-file -` (stdin)
   for the fallback path.
2. **Commit-reveal.** The card carries `rubric_seal = sha256(rubric || salt)`.
   The rubric and salt sit in `.learning/sealed/<id>.json` in the record
   repo only. After grading, rubric and salt are copied into the attempt
   file, and `learning.py check` verifies every seal. The Map can show
   "rubric fixed 14:15, answer 14:22".
3. **Pages never hold a rubric before lock.** The PWA and inbox repo never
   do. The artifact page gets the rubric only through an app-only
   `lock_answer` path: the page locks the answer in the db first, then asks
   the session (sendToClaude) or the MCP server (page `mcp` capability, [S])
   for the verdict. Where on-page grading with `sample` is needed (no session
   at all), the rubric is written to the db in a field the page reads only
   after the lock is committed, and the page code enforces that order. This is
   honest about the residual risk: an owner opening the db can read it.
4. **MCP Apps and URL elicitation** keep the rubric on the server; the model
   in the build session never sees the learner's in-progress answer either
   (URL mode is outside the model's reach by spec [D]).

---

## 9. Offline and failure behaviour

| Failure | What the learner sees | What the system does |
|---|---|---|
| Phone offline | Room opens from the service worker cache with cached due cards (public view only). Submit says "Saved on this phone. Sends when online." | Outbox in IndexedDB; retry on open and on `online` event (no Background Sync on iOS). Lock time is the local time of the tap. |
| Laptop asleep, session gone | "Saved. Feedback in a few minutes." | Grader Action or next cloud task grades. |
| Bell lost (monitor not running, socket gone) | Nothing different. | SessionStart hook and every checkpoint run `learning.py inbox`; nothing depends on the bell arriving. Bells are an optimisation. |
| Two doors lock the same card | The later door shows "Already answered on phone at 14:22. Showing that answer." | Earliest lock wins (7.3). |
| Push not permitted or not installed | No push. Badge if installed. | Card waits in the inbox; the agent mentions "1 review due" once at the next session start. |
| Token expired (PWA) | One line: "Reconnect to save answers." with a button. | Answers stay in the outbox; nothing is lost. |
| Model unavailable for grading | "Saved. Graded later." | Answer stays locked and ungraded; never auto-graded by heuristics. |
| Harness without any rich surface | Plain-text card in chat and a Room link. | The floor in 5.7. |
| Learner says "Not now" | Card moves to Later. No follow-up in this session. | Honoured exactly (Linear agent guidelines). |
| Learner pauses learning | One tap in the Room or `/learn pause`. No pushes, no cards, no band. | Mode `paused` in `.learning/config.json`; the schedule shifts, misses are not counted. |

The rule underneath: **a lost message may delay feedback but never loses an
answer, never double-counts, and never blocks the build.**

---

## 10. What must be built

Sized in rough engineering days for one person, in build order.

### 10.1 Record and CLI (Python, stdlib only) - 4 days

- `cards/`, `sealed/`, `events.jsonl`, `config.json` (mode: quiet, normal,
  deep, paused; daily nudge cap; presence policy).
- `learning.py seal` (stdin rubric), `post` (writes to all inboxes), `import`
  (all inbox kinds, idempotent), `watch` (ntfy wake plus GitHub ETag poll,
  appends bells), `push` (Web Push via a tiny vendored VAPID signer, or
  `pywebpush` if present), `bridge codex` (app-server client, `turn/steer`).
- `.gitattributes` with `*.jsonl merge=union`.
- `init` detects a public remote and proposes the private record repo.

### 10.2 The Room (one codebase, three hosts) - 10 days

- Vanilla TypeScript plus a small reactive layer (no framework needed;
  under 60 KB), built by one script into `docs/app/` (PWA), an artifact
  bundle, and `assets/room.html` for `learning.py serve`.
- Store adapters: `local` (fetch to serve, SSE for feedback), `github`
  (inbox repo REST), `artifact` (db, room, comments, sample, user).
- Screens: Inbox (Now, Due capped at 5 with "3 more move to tomorrow",
  Later), Card, Compare (prediction vs outcome), Map (grid plus table plus
  calibration), Drill, Explainer host, Modes and Pause, Connect.
- Keys (Linear and Raycast style, shown in an action bar on every card):
  J/K move, Enter open, 1/2/3 confidence, D I don't know, H Not now, Esc
  back, Cmd+Enter submit, G then M map.
- PWA: manifest, service worker (cache app shell and cards), Web Push
  subscription, Declarative Web Push payloads where available (iOS 18.4+),
  `navigator.setAppBadge(dueCount)`.

### 10.3 Visual and interaction spec (follows docs/ exactly)

- Paper `#F5F4F0` with `grain.png`, ink `#16161A`, accent `#E8541E`,
  text-safe `#C2410C`. Instrument Sans headings (wdth 88, weight 650),
  JetBrains Mono for code, ids and keys.
- Card: white, 1.5px `#DAD8D0` border, 16px radius, max width 640px, 24px
  padding (16px at 375px). Excerpt in mono with `path:line` header. Pill
  buttons; primary is ink fill, accent reserved for the one live element
  (the "Now" card's edge, the lit record cell).
- Record cells: ramp `#F6C9AF` / `#EE8B5B` / `#C2410C`, each filled cell with
  a 1.5px ink outline and a level glyph (one to three bars), level name in
  the accessible name, and a table view toggle. This meets WCAG 1.4.11
  without changing the palette [T contrast measured].
- Motion: a cell fades in over 400 ms when a grade lands; the card slides
  8px on lock; nothing else moves. `prefers-reduced-motion` removes both.
- Live regions: verdicts announce through `role="status"`; focus moves to
  the verdict heading after submit; every control reachable by keyboard;
  touch targets at least 44px.
- Copy samples: "1 question about retries." / "Answer before you look at the
  change." / "Saved. Feedback in a few minutes." / "No. A timeout means the
  reply didn't arrive. It doesn't tell us whether the charge ran.
  billing/charge.py:47. Back tomorrow." / "Back to the build: Claude is
  running the billing tests."
- No streaks, XP, percent bars or loss copy. Consistency is faint weekly
  cells with no counter.

### 10.4 Learning MCP server - 5 days

- One server, stdio locally, Streamable HTTP when hosted; speaks 2025-11-25
  and falls back from 2026-07-28 `server/discover` [T observed].
- Tools: `seal_card`, `ask` (tiers: MCP App card where the host declares the
  UI extension, else form elicitation, else URL elicitation to the Room, else
  text), `post`, `lock_answer` (app-only visibility), `due`, `record`.
- Tasks extension for async questions in Claude Code CLI (footer shows the
  task, completion reported) [D].
- Writes `.learning/inbox/` directly and appends the bell.

### 10.5 Claude Code plugin - 4 days

- Mod: band above the prompt ("1 question", "2 due"), pane with Input,
  Select, Button, instant `/learn` commands [T probe].
- Monitor on `events.jsonl` [D]. Hooks: `UserPromptSubmit` (prediction
  offer on build-shaped prompts), `PostToolUseFailure` (drill offer, once),
  `Stop`/`TaskCompleted` (explain-back), `SessionStart` (import, due count),
  `PreCompact` (save in-flight card state), `Notification idle_prompt`
  (phone push when away).
- `.claude/launch.json` entry so the Browser pane opens the local Room.
- Output style for the plain voice, with a rule that a prediction and a
  `TODO(human)` from the Learning style never land on the same decision.

### 10.6 Codex and others pack - 3 days

- Skill at `.agents/skills/learning-while-building` with
  `.claude/skills` symlink and `agents/openai.yaml` [D].
- Codex `hooks.json` Stop hook (explain-back once per passing build),
  SessionStart (due count), `config.toml` MCP entry.
- Cursor stop hook `followup_message`; Card as `ui://` resource.

### 10.7 Sync and graders - 3 days

- Inbox repo template with the Grader Action and the Web Push cron.
- Cloud scheduled task prompt (daily review, nudge back-off rules).
- Optional ntfy wake topic (random 128-bit name, content-free messages).

Total: about 33 days for the full set. A first usable slice (section 12,
phase 1) is about 8 days.

---

## 11. Dependencies: status and cheapest experiment

| # | Dependency | Status | Cheapest experiment |
|---|---|---|---|
| 1 | Mods draw a band and pane in CLI, desktop Code tab, VS Code | [T] validated and unit-tested on 2.1.319 | `claude --plugin-dir ./lwb-mod` in the desktop Code tab with a fake `.learning/inbox.json`; check band, key 1, `/learn` mid-turn. |
| 2 | `$.prompt.submit` queues a turn at idle | [D] | In the probe mod, submit "grade card X" from the pane while a turn runs; confirm it waits and then runs. |
| 3 | Plugin monitor turns `events.jsonl` lines into notifications while idle | [D] | `monitors.json` with `tail -F`; append a line from another shell; check CLI and desktop. |
| 4 | `asyncRewake` SessionStart hook wakes an idle session | [D] | Hook that waits for `.learning/inbox/*.json` and exits 2; drop a file. |
| 5 | Inbox socket accepts posts from a child process | [D], socket present [T], wire format undocumented | Background Bash child writes auth plus one line; observe with `--debug`. |
| 6 | MCP form elicitation in Claude Code CLI | [T] declared and answered via hook | Commit the probe server to `.mcp.json`; call `ask` and answer in the terminal. |
| 7 | Elicitation cards in cloud sessions, and on the phone app | [D] | Same server from a cloud session opened in the Claude app on the phone; note enum rendering. |
| 8 | URL-mode elicitation opens the Room and resumes on `complete` | [D] spec; client behaviour [S] | Server sends `mode: url` to `127.0.0.1:8765/#/c/x`, page POSTs, server sends complete; run in Claude Code CLI and Codex TUI. |
| 9 | Codex form elicitation | [T] | Already passed with a stub; repeat with `ask`. |
| 10 | Codex desktop renders MCP App cards | [R] issue closed 2026-08-05; brief says no | Configure the existing `experiments/mcp-app` server in `~/.codex/config.toml`; call it in the current desktop build. |
| 11 | Codex `request_user_input_async` answered from ChatGPT iOS | [D] | Ask one prediction with three options in Plan mode; answer on iOS. |
| 12 | Codex app-server `turn/steer` from an outside process | [D] | 30-line script: start thread, subscribe `turn/completed`, send one steer. |
| 13 | Codex Stop hook `decision: block` continues with a new prompt | [D] | One build turn with the hook returning the explain-back prompt. |
| 14 | Artifact `room.sendToClaudeSession` / `comments.sendToClaude` reach the session, on phone and desktop | [D] | Publish Room with `room: {}`, `comments: {}`; log `canSendToClaudeSession()`; press Send on the phone. |
| 15 | Artifact `sample` grading on the page | [T] existing hosted page | None; already works. |
| 16 | Artifact `mcp` capability calls a local server (`host:learning`) | [S] | Page declares `host:learning`, calls `listTools()`; open in desktop app and on phone. |
| 17 | Remote Control forwards AskUserQuestion and pushes to the phone | [D] | `/remote-control`, enable push toggles, trigger an idle_prompt hook, answer on the phone. |
| 18 | Presence file suppresses pushes | [D] | Create `CLAUDE_CLIENT_PRESENCE_FILE`, fire a push, confirm none arrives; delete it and retry. |
| 19 | Web Push to an installed PWA on iOS 16.4+ (Declarative on 18.4+) | [D], chain [S] | `docs/app/` manifest plus subscribe page; install on iPhone; send one push from a `workflow_dispatch` Action with `pywebpush`. |
| 20 | App badge (`setAppBadge`) on iOS and Android | [D] | Feature-detect and set badge 2 from the installed PWA; check it clears. |
| 21 | Browser REST to a private repo with a fine-grained token (CORS) | [D] | From the PWA page, `PUT /repos/<owner>/learning-inbox/contents/x.json`; read back with `If-None-Match`. |
| 22 | GitHub device flow from the browser is blocked by CORS | [R] | Try `POST github.com/login/device/code` from the page; expect a CORS failure, which justifies the Worker in v2. |
| 23 | ntfy wake from phone to laptop | [T] publish from container | Laptop subscribes via SSE to a random topic; PWA publishes "x"; measure delay. |
| 24 | Union merge of `events.jsonl` across branches | [T] | Already passed; add to CI as a regression test. |
| 25 | Cloud scheduled task with push, laptop closed | [D] | `create_trigger` daily, `create_new_session_on_fire`, `notifications {push: true}`, prompt "run learning.py due"; close the laptop. |
| 26 | Grader Action with claude-code-action on inbox push | [D] parts, chain [S] | Inbox repo workflow on push: check out record repo with a deploy key, grade one canned answer, write feedback. |
| 27 | Desktop Browser pane hosts the local Room via `.claude/launch.json` | [D] | Add the entry, open the pane, load `127.0.0.1:8765`. |
| 28 | Deep links bring the right window forward | [D]; GitHub Markdown strips custom schemes [D] | Put `claude-cli://`, `claude://code/new` and `claude.ai/code/session_` links on the Room; click on macOS and the phone. |
| 29 | HTTPS PWA can fetch `http://127.0.0.1` (for one Room host on desktop) | [S] Chrome Private Network Access preflight; Safari unclear | Not needed if desktop uses the local-served Room; test only if we want one origin. |
| 30 | Rubric leaks through visible Bash | [S] | Run `learning.py ask --rubric` in Claude Code and Codex; screenshot; repeat via subagent and MCP tool. |
| 31 | MCP tasks extension visible in Claude Code footer | [D] (CLI, SDK, Actions only) | Tasks-capable tool that stays working until a file appears. |
| 32 | MCP Apps in Claude Code | [T] no: text only | Re-test only when release notes mention MCP Apps. |
| 33 | SEP-3118 app-rendered elicitations | [S] not merged | Run the reference inspector branch with the Card as elicitation UI; build `ask` so it can switch over with one flag. |
| 34 | Tailscale Serve for the local Room on the phone | [D] | `tailscale serve 8765`; open the ts.net URL on the phone; read `Tailscale-User-Login`. Optional door for owners who already use Tailscale. |

---

## 12. Plan

**Phase 1, one week: the acceptance test on Claude Code.** Record changes
(cards, seals, events), Room v1 on local serve and as the artifact,
monitor plus SessionStart hook, artifact `sendToClaude` path, presence-gated
PushNotification. Run experiments 1 to 4, 14, 17, 18, 30 first; each is under
an hour. Exit: the acceptance test in section 1 passes on the owner's laptop
and phone.

**Phase 2, one week: the PWA and the clock.** `docs/app/` with Web Push and
badge, inbox repo with token, `learning.py watch`, cloud scheduled task for
daily review, Grader Action. Experiments 19 to 23, 25, 26. Exit: a review
day runs with the laptop closed, from push to feedback.

**Phase 3, one week: Codex and Cursor.** MCP server tiers, URL elicitation
to the Room, Codex hooks and bridge, Cursor card. Experiments 8 to 13. Exit:
the acceptance test passes in the Codex app with the answer given on the
phone.

**Phase 4, ongoing: learning quality.** E1 (wait-time vs before-build
placement), E2 (Compare screen on half of predictions), E4 and E5
(hypercorrection and calibration chart), FSRS replay. The Room logs which
door and which delivery mode each answer used, so these run on real data.

---

## 13. How the experts would push on this

- **Bjork and Roediger**: retrieval must be effortful and answers hidden;
  hence sealed rubrics and no reveal before lock on any door, including the
  phone. The capped Due list keeps spacing intact after time away.
- **Kapur**: prediction without consolidation is just failure; hence the
  Compare screen is not optional for `attempt` cards.
- **Metcalfe**: the confident miss is the event to optimise for; it gets the
  plainest correction, the earliest return and a mark on the Map.
- **Linear and Raycast designers**: one object, one set of keys, an action
  bar that teaches shortcuts by use, and an agent that steps back on "Not
  now".
- **Duolingo learning team**: notification back-off and novelty matter more
  than copy; difficulty set by level is the engagement engine, not streaks.
- **Staff platform engineers**: inboxes plus an idempotent importer plus
  content-free bells is the design that survives every transport failing;
  no feature depends on a preview capability.
- **Accessibility experts**: outlines and glyphs on record cells, a table
  view, live regions for verdicts, and full keyboard paths on every door.
