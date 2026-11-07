# Protocol bridge architecture: one learning daemon that every harness talks to

Status: design proposal, 2026-11-07. Stance: a small local process, `lwbd`, owns
the learner's record, knows which surface the learner is on, delivers each
question to that surface, and pushes each answer back into the running build
session. Harnesses reach it through the protocols they already speak: MCP
(stdio shim), hooks (a one-shot client), ACP (a proxy agent), the Codex
app-server (a companion), and plain HTTP for pages. The sibling proposal
`agent-native.md` runs no service; this one accepts one service in exchange for
cross-session memory, real timers, presence, and a single place where rubrics
stay sealed.

Status keys: **[T]** verified by test in this project, **[D]** documented by the
vendor or spec, **[R]** reported by third parties, **[S]** speculative. Every
dependency is listed with its cheapest experiment in section 14.

Hard rule kept from the brief: the files in `.learning/` are the truth. The
daemon is an accelerator and a router. If it is not running, every harness falls
back to the current direct-file behaviour (`learning.py`, `room.py`) with no loss
of data.

---

## 1. The idea in six lines

1. **One card, many doors.** A question is one object (the card) with one id,
   one sealed rubric and one lock. Every surface (mod pane, elicitation form,
   terminal, local page, hosted artifact, phone app, push) is a door onto it.
2. **One owner.** `lwbd` is the only writer of `.learning/` on a machine. It
   holds the card state machine, the schedule, presence, and the session
   registry.
3. **Thin adapters, not integrations.** Each harness gets a 30 to 200 line
   adapter in the protocol it already speaks. The adapters carry no logic.
4. **Answers are events, and events go home.** When a card locks, the daemon
   picks the best return path into the session that asked (MCP task
   completion, tool result, inbox socket, monitor line, asyncRewake, Codex
   `turn/steer`, artifact `sendToClaudeSession`) and uses exactly one.
5. **Presence decides the door.** At the keyboard: a band in the harness. Idle
   at the machine: a count in the periphery. Away: one push, at most one a day.
6. **The model grades; the daemon never does.** The daemon has no model. It
   reveals the rubric to the grader (the build agent, or the hosted page's
   `sample` capability) only after the lock.

---

## 2. Shape of the system

```
                         +------------------------------------------------+
                         |                   lwbd (local)                  |
  Claude Code  --stdio-->|  MCP shim  ->  RPC  ->  Card engine  -> Store   |--> .learning/ (git)
  (CLI, desktop          |                         |   Sealer      (flock)  |
   Code tab, VS Code)    |  hook client  ------->  |   Scheduler            |
  Codex CLI / app --stdio|                         |   Presence             |
                    ---->|  ACP proxy (Zed) ---->  |   Router  ---------+   |
  Cursor / VS Code ----->|  app-server companion   |   Session registry |   |
                         |                         |   Return paths <---+   |
                         |  HTTP 127.0.0.1:8765  (local page, Browser pane) |
                         |  Mailbox client (E2E sealed, via relay)          |
                         +------------------------------------------------+
                                  |                         |
                    local doors   |                         |  away doors
            mod band and pane     |                         |  PWA on github.io + Web Push
            elicitation form      |                         |  ntfy (generic text only)
            terminal (lwb answer) |                         |  claude.ai artifact (db, sample)
            local page            |                         |  Remote Control / cloud session
                                                            |  Codex request_user_input on iOS
```

Processes:

| Process | Lifetime | Started by | Speaks |
|---|---|---|---|
| `lwbd` | long-lived, lazy | first adapter that cannot reach the socket (socket activation by fork), or launchd/systemd user unit if the learner opts in | JSON-RPC 2.0 over `~/.lwb/lwbd.sock` (0600); HTTP on 127.0.0.1 |
| `lwb mcp` (shim) | one per harness session | the harness, from `.mcp.json` / `config.toml` | MCP stdio upward, RPC to `lwbd` downward |
| `lwb hook <event>` | one per hook event | the harness hook runner | stdin JSON in, stdout JSON out |
| `lwb acp-proxy` | one per editor session | Zed (ACP agent config) | ACP both ways |
| `lwb codex-attach` | optional, per Codex thread | `lwb mcp` on first card in Codex, or the learner | Codex app-server JSON-RPC |
| `lwb answer` | one-shot | the learner in any terminal | RPC |

The daemon is Python 3.11 standard library only, like the current scripts. It
imports `record.py` for all file reads and writes, so the file format does not
fork. It exits after 30 minutes with no registered sessions, no open HTTP
clients and nothing scheduled within the hour. It restarts in about 100 ms on
the next adapter call.

Why MCP over the socket: the daemon speaks MCP itself (the 2025-11-25 handshake,
with the 2026-07-28 `server/discover` path added once Claude Code stops falling
back [T: it falls back today]). The shim is then a byte pipe plus one
`_meta.lwb/session` block, so any harness that can reach a Streamable HTTP MCP
server on localhost can skip the shim entirely.

---

## 3. Core model

### 3.1 The card

```json
{
  "id": "c_2026-11-07T14-03-11_7f3a",
  "repo": "/home/user/explain-pr",
  "topic": "http-server-threading",
  "dimension": "concurrency",
  "kind": "predict | explain | debug | review | transfer | drill | explainer",
  "moment": "before | during | after | failed | away | review",
  "level_at_ask": "with help",
  "support": "completion | predict-explain | design-first | worked-example",
  "prompt": "When two requests arrive at once, which thread writes the attempt file?",
  "excerpt": {"path": "scripts/room.py", "line": 212, "text": "..."},
  "observable": "the order of the two lines in events.jsonl",
  "rubric_commit": "sha256:4b1e...",
  "state": "sealed",
  "origin": {"harness": "claude-code", "surface": "desktop-code-tab",
             "session": "074e39f7-...", "return": ["mcp-task", "inbox-socket"]},
  "deliveries": [{"door": "mod-pane", "at": "...", "seen": true}],
  "answer": null,
  "confidence": null,
  "dont_know": false,
  "locked_at": null,
  "outcome": null
}
```

States, in order, each written as an event:

```
drafted -> sealed -> delivered(door...) -> locked -> revealed -> graded -> fed_back -> scheduled
              \-> not_now (Later; honoured exactly, no re-ask this session)
              \-> skipped (session ended, learner never saw it)
```

- `sealed`: rubric stored outside the repo, only `rubric_commit` in the card
  (section 8).
- `locked`: answer and confidence are final. No door accepts an edit after
  this. The first lock wins; a second lock from another door is kept as a note.
- `revealed`: for a prediction, only after the observable has happened (the
  test ran, the server responded). For a review, right after lock.
- `graded`: outcome (correct, partial, wrong, skipped), hint level H0 to H3,
  grader. This becomes the existing attempt file with the existing fields, so
  `learning.py map`, `due` and `check` keep working unchanged.

### 3.2 Files

```
.learning/                         in the repo, committed, plain files (unchanged layout)
  dimensions.json
  topics/<id>.json
  attempts/<id>.json               one per graded card (written at graded)
  events.jsonl                     NEW: append-only card events, merge=union
  reviews.jsonl                    NEW: FSRS-compatible log (card, topic, ts, rating 1-4, elapsed)
  config.json                      NEW: mode (quiet | normal | deep), nudge caps, doors allowed
~/.lwb/                            per machine, never committed
  lwbd.sock, lwbd.pid, token
  sealed/<card>.json               rubric + salt until lock
  presence.json                    last signal per surface
  sessions.json                    registered sessions and their return paths
  mailbox/keys.json                X25519 or P-256 keys for paired phones
  outbox/, inbox/                  queued mailbox messages
```

`.gitattributes` gains `.learning/*.jsonl merge=union` [T: union merge of two
branches that both appended worked with no conflict].

### 3.3 Sessions and presence

A session registers on its first shim or hook call with: harness, surface,
session id, repo, and the return paths it supports, probed rather than assumed:

| Probe | How the adapter learns it |
|---|---|
| MCP tasks | client capabilities in `initialize` |
| elicitation form / url | client capabilities in `initialize` [T for Claude Code 2.1.319 and Codex 0.167.0] |
| MCP Apps (`io.modelcontextprotocol/ui`) | client capabilities / extensions [T: forwarded by Codex app-server] |
| Claude inbox socket | `CLAUDE_CODE_MESSAGING_SOCKET` in the shim's or hook's environment [T: exists in this session; S: inherited by MCP children] |
| Claude mod present | the mod calls `lwb.hello` on load |
| Codex app-server | `CODEX_*` env or a successful `lwb codex-attach` |
| Remote Control active | hook input or `/remote-control` status [S] |

Presence signals feed one number per surface, `last_seen`, and a derived state:

- **at keys**: a hook fired in the last 2 min, or the mod heartbeat, or the
  local page is visible (`visibilitychange`), or the terminal is focused
  (`CLAUDE_CLIENT_PRESENCE_FILE` exists [D]).
- **idle at machine**: none of those for 2 to 15 min, machine awake.
- **away**: more than 15 min, or the machine is asleep (the daemon notices on
  wake by the clock jump), or the learner opened a phone door.

---

## 4. The learner's moments, and where each happens

Rows are moments. Columns are harness surfaces. Each cell names the door, and
the fallback after the slash. "Ret" is the return path for the answer.

| Moment | Claude Code, desktop Code tab | Claude Code on the phone | Claude Code CLI | Codex app (desktop) | Codex CLI | Cursor (the one more) |
|---|---|---|---|---|---|---|
| **Before a build** (one prediction on the observable) | `UserPromptSubmit` hook asks daemon if a prediction is due; agent opens a card; mod band "1 question" and pane / AskUserQuestion. Ret: tool result or MCP task | Remote Control forwards AskUserQuestion, stays open [D]; cloud session: elicitation card [D] | mod band and pane [T probe] / elicitation form [T] | elicitation form [T]; MCP App panel if it renders [R] | elicitation form [T] / `request_user_input` [D] | MCP App card inline [D Cursor 2.6] / text |
| **During** (wait time, answer while the agent works) | non-blocking card: MCP task handle, band shows count, learner answers in pane while tools run. Ret: task completion, then inbox socket | push only if away; else nothing | task in footer [D] / band | `request_user_input_async` [D] | async question [D] / plain text after the turn | card stays inline; answer sent by `tools/call` |
| **After it works** (explain-back + prediction vs outcome side by side) | `Stop` hook: daemon sees "tests passed, card locked", returns reveal context; agent grades; pane shows side-by-side and one-line resume cue | same card pushed if the learner left; answered in the Claude app | `Stop` hook / text | Codex `Stop` hook `decision: block` with the explain-back prompt [D] | same [D] | `stop` hook `followup_message` auto-submits [D] |
| **When it fails** (debug drill, hypothesis first) | `PostToolUseFailure` hook: daemon offers "Call the cause first?" once per failing test; pane takes the hypothesis | push only if away | same hook / text | Codex `PostToolUse` on non-zero exit [D] / text | same | hook / text |
| **Away** (laptop closed or learner elsewhere) | Remote Control push + forwarded question [D] | PWA push (any harness) or claude.ai artifact (Claude), at most one a day | same as desktop | ChatGPT for iOS keeps unanswered Codex questions [D] | PWA push | PWA push |
| **Review** (spaced, 3/7/21/60/180, miss returns next day) | `SessionStart` hook injects "2 due"; band; `/learn review` opens the inbox | cloud scheduled task fills the artifact db and pushes [D]; PWA inbox from the mailbox | `/learn review` in mod or terminal `lwb review` | `SessionStart` context [D]; elicitation per item | `lwb review` in a split terminal | `SessionStart` context; MCP App inbox card |
| **Map** (the record, best and latest per topic) | mod pane "Record"; local page in the desktop Browser pane via `.claude/launch.json` [D] | artifact page or PWA (rendered from the last synced snapshot) | `lwb map` (ANSI grid with glyphs) | MCP App card or local page link | `lwb map` | MCP App card |
| **Drill** (repair drills on the real code) | agent breaks a copy in a worktree; pane holds the hypothesis and the timer | not offered (needs the code) | same | same, in a Codex worktree | same | same |
| **Explainer** (a page built on request, with Orbit-style embedded prompts) | local page in the Browser pane; embedded prompts post to `lwbd` HTTP | hosted artifact; prompts write the artifact db, imported later | opens the local page in the browser | link out to local page / MCP App | link out | MCP App or link |

Zed and other ACP editors: `lwb acp-proxy` wraps the real agent, inserts
`elicitation/create` before the first `session/prompt` and after the last
`session/update` of a turn [D: ACP elicitation stable 2026-07-24; S: the proxy].

---

## 5. How a question reaches the learner and the answer gets home

Three end-to-end sequences. In none of them does the learner copy text.

### 5.1 Prediction during the wait, Claude Code desktop Code tab

1. Learner types "add a thread pool to room.py serve". `UserPromptSubmit`
   fires; `lwb hook user-prompt-submit` sends the prompt, session id and repo to
   the daemon. The daemon checks: mode is normal, no card open, the topic
   `http-server-threading` is at "with help", last prediction was more than
   20 min ago. It returns `additionalContext`: "Before running the first test,
   open one predict card on the observable that test shows. Support:
   completion." [D: hooks can add context]
2. The agent spawns a forked subagent (`context: fork`) that drafts the
   question and rubric and calls `lwb.open_card` with both. The main transcript
   shows only "Card sealed (sha256 4b1e...)". The daemon stores the rubric in
   `~/.lwb/sealed/`, writes `sealed` to `events.jsonl`. [S: what the desktop
   transcript shows for subagent tool calls; experiment X9]
3. The main agent calls `lwb.ask` with the card id and `mode: task`. Because
   the client declared tasks, the daemon returns a task handle at once and the
   agent keeps building [D: Claude Code shows MCP tasks in the footer for CLI
   and SDK; S: desktop Code tab].
4. Router: the learner is at keys and the mod said hello, so the door is the
   mod band: `1 question  ·  1 to open`. Hotkey `1` opens the pane: prompt,
   `room.py:212` excerpt, answer Input, confidence Select (Guess / Fairly sure /
   Sure), "I don't know", "Not now". [T: probe mod renders; S: mod to daemon
   transport, see X3]
5. Learner answers while the agent writes code. The mod posts to the daemon
   (`fetch` to 127.0.0.1 with the per-boot token, or through the plugin's own
   MCP server if mods cannot fetch). The daemon locks the card and appends
   `locked`. The pane shows "Locked. Shown after the test runs."
6. Return path: the daemon completes the MCP task with
   `{card, confidence, locked: true}` and no answer text. The agent now knows
   it must not reveal anything that settles the prediction before the test.
   If the client had no tasks, the daemon would post one line to the inbox
   socket instead, and failing that, append to the monitor file.
7. The test runs. `PostToolUse` on the test command reports the exit code to
   the daemon; the daemon marks the observable seen and returns context:
   "Reveal card c_... now." The agent calls `lwb.reveal`, receives answer and
   rubric, grades with `lwb.grade` (outcome, hint level, feedback text).
8. The pane switches to the side-by-side: "You said: ... / It did: ..." then
   the feedback in the Voice ("Not quite. The second request waits on the GIL
   only while ..."), a "where next" line, and the resume cue: "Back to: wiring
   the pool into serve(). Next step: the shutdown path." The band goes quiet.

If no mod is installed (VS Code without mods, or an older CLI): step 4 becomes
an elicitation form at the moment of reveal, not before, so the build never
stops for it; the prediction is asked in chat text at step 3 and the form only
locks it.

### 5.2 Explain-back while away, any harness, answered on the phone

1. The build passes at 18:40. The `Stop` hook tells the daemon. Presence says
   the learner has been away 22 min (no hooks, terminal unfocused, no page
   visible). The daemon opens an explain card from a rubric the agent sealed
   when it planned the change (step 2 above, done at plan time).
2. Router picks the away door by what the learner has paired:
   - **Claude with Remote Control on**: the daemon posts to the inbox socket,
     the session calls `PushNotification` with the first line and asks with
     AskUserQuestion, which Remote Control forwards and keeps open [D].
     Answer returns as the tool result. Grading happens in that session.
   - **Any harness, PWA paired**: the daemon seals the card (prompt and
     excerpt, never the rubric) to the phone's public key and posts it to the
     relay; Web Push wakes the PWA with a generic body "1 question about
     room.py" [D: Declarative Web Push iOS 18.4; S: whole chain, X12]. The
     learner answers on the installed page; the PWA seals
     `{card, answer, confidence, locked_at}` to the daemon's key and posts it
     back. The daemon locks the card.
   - **Claude, no Remote Control**: the hosted artifact. The daemon cannot
     write the artifact db itself, so it asks the session (inbox socket) or
     the next cloud scheduled task to run `room-push` [D: ArtifactData]. The
     page can grade on the spot with `sample` because the rubric is released
     to the page db only on lock (section 8).
3. Home: when the laptop wakes, the daemon drains the relay, locks, and finds
   the origin session. If it is alive: inbox socket post "1 answer from your
   phone on c_..." so it grades at the next idle moment. If it is gone, the
   next `SessionStart` in that repo injects "1 answer waiting to grade", the
   agent grades in its first turn, and the feedback goes back to the phone by
   the same door (one sealed message, no push).

### 5.3 Codex CLI and Codex app

1. `~/.codex/config.toml` registers `lwb mcp`. Codex advertises elicitation
   form and url modes to every MCP server [T].
2. The skill (loaded from `.agents/skills/learning-while-building`, with
   `agents/openai.yaml` [D]) tells Codex to call `lwb.ask`. The daemon sends
   `elicitation/create` with `{answer: string, confidence: enum, dont_know:
   boolean}`; the thread waits in `waitingOnApproval` [T]. To keep the build
   moving, `lwb.ask` is called at the reveal point, and the prediction itself
   is asked as one line of text earlier (same as the no-mod Claude path).
3. For the wait-time version, `lwb codex-attach` connects to the thread through
   `codex app-server` [D], listens for `turn/completed`, and injects the locked
   answer with `turn/steer` when an answer arrives from another door [D; S:
   attaching to a thread the learner's own TUI owns, X14].
4. Explain-back: Codex `Stop` hook returns `decision: block` with "Ask the
   explain-back for card c_..." once per passing build [D].
5. Phone: Codex `request_user_input_async` questions remain answerable in
   ChatGPT for iOS after the turn ends [D]; the skill uses it for away cards
   when the PWA is not paired.

---

## 6. Return paths into a running session

The daemon uses exactly one path per event, the first that the session
supports, in this order. Each path carries the card id and lock state, never
the rubric.

| Rank | Path | Harness | Wakes an idle session? | Status |
|---|---|---|---|---|
| 1 | Tool result of the blocking `lwb.ask` (elicitation) | Claude Code, Codex, ACP | not needed (turn is waiting) | [T] |
| 2 | MCP task completion | Claude Code CLI and SDK | reported in footer; turn at next pause | [D] / desktop [S] |
| 3 | Mod `$.prompt.submit({immediate:false})` | Claude Code CLI, desktop, VS Code | queues a turn at the next idle moment | [D], probe [T] |
| 4 | Inbox socket `CLAUDE_CODE_MESSAGING_SOCKET` | Claude Code local | yes (delivered as a message) | [D]; wire format [S] |
| 5 | Plugin monitor on `~/.lwb/sessions/<id>.events` | Claude Code with plugins | notification each line | [D] |
| 6 | `asyncRewake` hook exits 2 | Claude Code without plugins | yes | [D] |
| 7 | Codex `turn/steer` via app-server | Codex | injects into the active turn | [D] |
| 8 | Codex / Cursor / Gemini stop hooks with follow-up | Codex, Cursor, Gemini | at turn end | [D] |
| 9 | Artifact `room.sendToClaudeSession` / `comments.sendToClaude` | Claude (page gesture) | yes, after a viewer tap | [D] |
| 10 | `SessionStart` context next time | all | next session | [D] |

Rate rule: at most one return per card, and at most one unprompted turn per
10 minutes per session. Extra events are batched into the next one.

---

## 7. State and sync

- **Single writer per machine.** All writes go through `lwbd`, which takes an
  `flock` on `.learning/.lock`. `learning.py` takes the same lock in fallback
  mode, so a terminal and a daemon cannot interleave a write.
- **Append-only events, one file per attempt.** Two machines (laptop and a
  cloud session branch) can both append; git union-merges `events.jsonl` and
  `reviews.jsonl`. Attempt files have unique ids, so they never collide.
- **Inboxes, not replicas.** Every store that is not the repo (artifact db,
  relay mailbox, Codex Site D1, GitHub PR comments) is an inbox. The daemon or
  `learning.py import` reads it with the card id plus a per-door `attempt_key`
  as the idempotency key. Importing twice changes nothing.
- **Lock conflicts.** If two doors locked the same card offline, the earliest
  `locked_at` wins; the other answer is stored as `also_answered` and shown in
  the feedback ("You also answered on your phone: ..."). Clocks are trusted to
  a minute; that is enough for a single learner.
- **Snapshot for read-only doors.** On every grade the daemon writes a
  compact `map.json` (topics, best, latest, due dates, no rubrics, no answers)
  that the PWA and artifact use for the record grid and the due count.
- **Schedule.** The due list is always recomputed from attempt files (the
  existing ladder). `reviews.jsonl` logs `(topic, ts, rating, elapsed_days)`
  so FSRS can be replayed offline later without changing the ladder now.
- **Cloud sessions** have no daemon. The shim detects that and runs the card
  engine in-process against the checkout, commits to the session branch, and
  the laptop merges on the next pull. Cloud scheduled tasks use the same path.

---

## 8. Rubric privacy

Threat model: the learner is the beneficiary, so the goal is to stop accidental
exposure (a glance at a transcript, a page's DOM, a Bash line, the model saying
too much) and to make the rubric provably fixed before the question. A
determined learner can always read their own disk; that is out of scope.

| Leak | Today | With the bridge |
|---|---|---|
| `learning.py ask --rubric` visible as a Bash command | likely [S, X9] | rubric goes through `lwb.open_card` called inside a forked subagent; main transcript shows the commit hash only |
| Rubric in `.learning/attempts/*.json` visible in the editor or diff before the answer | yes | stored in `~/.lwb/sealed/` outside the repo until lock; the repo only has `rubric_commit = sha256(salt + rubric)` |
| Agent reads the sealed file and leaks hints | possible | `PreToolUse` hook denies Read/Bash on `~/.lwb/sealed/` [D: hooks can deny]; `lwb.reveal` is the only way in, and it refuses before lock |
| Page receives the rubric before the answer | possible on the hosted page | pages get the rubric only in the response to the lock call; artifact db holds it in a field written by `room-push` after lock, or AES-GCM sealed with a key released after lock |
| Model gives away the answer while building (prediction) | possible | the task completion tells the agent a prediction is open on observable X; the skill forbids narrating X until reveal; `MessageDisplay` hook can redact [S] |

After lock, the rubric is written into the attempt file next to the answer, and
`learning.py check` verifies `sha256(salt + rubric) == rubric_commit`. The
record stays plain and auditable.

---

## 9. Phone without a tunnel: the sealed mailbox

The local page cannot be reached from the phone, and hosting the record is not
wanted. The bridge adds a small, end-to-end sealed mailbox so any harness gets a
phone door:

- **App**: a PWA at `https://0xfauzi.github.io/explain-pr/app/` in the site's
  visual language. Installable to the Home Screen; Web Push on iOS 16.4+ and
  Declarative Web Push on iOS 18.4+ (badge with the due count, no service
  worker needed for display) [D].
- **Pairing**: the local page shows a QR code with the daemon's public key, a
  relay topic and a one-time pairing secret. The PWA generates its own key pair
  in WebCrypto (P-256 ECDH, AES-GCM; X25519 when Safari support is confirmed)
  and returns its public key sealed to the daemon. No account.
- **Relay**: a dumb store-and-forward. First choice ntfy (publishing from this
  container worked [T]); the payload is ciphertext, so ntfy only ever sees a
  random topic and opaque bytes. The push body stays generic ("1 question
  about room.py") because the push text is not encrypted by ntfy. Second
  choice, for real Web Push: a GitHub Actions `workflow_dispatch` or a cloud
  scheduled task sends the VAPID push (payload encrypted per RFC 8291).
- **Limits handled**: ntfy.sh keeps messages for a limited time (about 12
  hours by default [D, check]); the PWA keeps its outbox in IndexedDB and
  re-posts until the daemon acks, and the daemon re-sends open cards each
  morning it is awake.
- **What the phone can do**: answer, set confidence, say "I don't know" or
  "Not now", read feedback, see the record grid from `map.json`. It cannot
  grade (no model). Grading happens in the next session, or on the claude.ai
  artifact for Claude users.

Alternatives kept: Tailscale Serve for learners who already run Tailscale
(private HTTPS on ts.net with identity headers [D]); the claude.ai artifact
(grades on page with `sample`, works today [T]); Remote Control (Claude, needs
the laptop awake [D]).

---

## 10. Presence ladder and nudges

| Rung | When | What the learner sees |
|---|---|---|
| 0 | learner busy typing or agent mid-turn and nothing due now | nothing; the band shows a count only if a card is open |
| 1 | idle at machine, something due | band: `2 due`; status line glyph |
| 2 | before a build or after it works (the two research moments) | the card in the centre (pane, form, or chat) |
| 3 | away more than 15 min and a card is open or a review is due | one push, then nothing |

Caps, enforced in the daemon so every harness obeys them: one push a day,
never while at keys, a different topic each day, stop after three ignored
pushes and leave one inbox line ("Reminders paused. /learn remind on to turn
them back on."). "Not now" moves the card to Later and the daemon will not
offer it again in that session. Modes: Quiet (reviews only, no predictions),
Normal, Deep (predictions on every build, drills offered).

---

## 11. Offline and failure behaviour

| Failure | Behaviour |
|---|---|
| `lwbd` not installed or will not start | shim and hooks run in direct-file mode (today's scripts); no presence, no push; nothing is lost |
| Stale socket after a crash | adapter checks `lwbd.pid`; if dead, removes the socket and forks a new daemon |
| Daemon restarts mid-card | card state is rebuilt from `events.jsonl` and `~/.lwb/sealed/`; open MCP tasks are re-attached by id on the shim's next call |
| Harness lacks elicitation | question in chat text; learner answers in chat; agent calls `lwb.lock` with the text |
| Mod cannot reach daemon | mod falls back to `$.prompt.submit("/learn answer c_... ...")`, which the agent forwards |
| Session ends before the answer | card stays open; next `SessionStart` in the repo injects it; after 7 days it becomes `skipped` |
| Context compaction | `PreCompact` hook asks the daemon for a one-line card summary and re-injects it after compaction |
| Laptop asleep | phone answers wait in the relay and IndexedDB; drained on wake |
| Relay down | PWA shows "Saved on this phone. It will send when it can."; local doors unaffected |
| No network at all | every local door works; the record commits locally |
| Git merge on `.learning/` | union merge for jsonl; attempt files never collide; `learning.py check` flags duplicates |
| Two doors answer the same card | earliest lock wins, the other kept as `also_answered` |
| Clock skew between phone and laptop | lock order uses the daemon's receive time when the skew exceeds 5 minutes |

---

## 12. Security

- Unix socket mode 0600 in `~/.lwb/`; the HTTP listener binds 127.0.0.1 only,
  requires the per-boot token from `~/.lwb/token`, and rejects requests whose
  `Host` is not `127.0.0.1:8765` or whose `Origin` is not the local page (DNS
  rebinding).
- No remote listener, ever, unless the learner runs Tailscale Serve
  themselves. No Funnel, no quick tunnels for the record.
- Mailbox payloads are sealed per message; keys never leave the device that
  made them; pairing secrets are single use.
- Push bodies never contain code, answers, or rubric text.
- Adapters treat text from pages and phones as data: the agent receives
  "answer for c_..." through `lwb.reveal`, inside a JSON field, never as an
  instruction.

---

## 13. What must be built

| # | Component | Size | Depends on |
|---|---|---|---|
| B1 | `lwbd` core: RPC server, card engine, events log, flock, sealer, scheduler (wraps `record.py`) | 600 lines | none |
| B2 | `lwb mcp` shim and MCP surface: `open_card`, `ask` (elicitation / task / text), `lock`, `reveal`, `grade`, `due`, `map`, `not_now` | 400 lines | B1 |
| B3 | `lwb hook` client plus hook configs for Claude Code, Codex, Cursor, Gemini | 250 lines + JSON | B1 |
| B4 | Router and presence (signals, rungs, caps, modes) | 300 lines | B1 |
| B5 | Return-path drivers: task completion, inbox socket, monitor file, asyncRewake script, Codex `turn/steer` | 300 lines | B2, experiments X1 to X5 |
| B6 | Claude Code mod: band, pane (question, inbox Now/Due/Later, record, side-by-side feedback), keys J/K/H/Enter/Esc/1-3 | 700 lines JS | B1, X3 |
| B7 | Local page v2 on `lwbd` HTTP (same card component, Browser pane via `.claude/launch.json`) | 500 lines HTML/JS | B1 |
| B8 | PWA on the Pages origin: install, pair, inbox, card, record grid, Web Push, IndexedDB outbox | 800 lines | B1, X11, X12 |
| B9 | Mailbox client in `lwbd` (sealing, relay poll, acks) | 250 lines | B8 |
| B10 | Card component shared by mod, local page, PWA, artifact: one HTML/CSS module in the site tokens, record cells with ink outline and glyph, table view | 400 lines | site.css |
| B11 | `lwb acp-proxy` for Zed | 300 lines | B2 |
| B12 | `lwb codex-attach` app-server companion | 200 lines | B2, X14 |
| B13 | Skill changes: call `lwb.*` instead of `learning.py ask` when the server is present; level-to-support table; resume cue; hypothesis-first offer | SKILL.md + references | B2 |
| B14 | `learning.py check` additions: rubric commit verification, union-merge duplicates, `reviews.jsonl` export | 120 lines | B1 |

Order: M0 experiments (section 15), M1 B1 B2 B3 B13 B14 (Claude Code CLI and
Codex CLI working with elicitation and hooks), M2 B4 B5 B6 B10 (seamless
in-session on desktop), M3 B7 B8 B9 (phone for every harness), M4 B11 B12
(Zed, Codex wait-time), M5 MCP Apps card where hosts render it.

---

## 14. Dependency register

| # | Dependency | Status | Cheapest experiment |
|---|---|---|---|
| D1 | Claude Code declares elicitation form and url | [T] 2.1.319 | done |
| D2 | Codex advertises elicitation form/url to all MCP servers; thread waits | [T] 0.167.0 | done |
| D3 | Elicitation renders as a card in cloud sessions on the phone | [D] | commit `.mcp.json` with the probe server, call it from a cloud session in the Claude app on the phone, screenshot |
| D4 | MCP tasks shown and completed in Claude Code CLI; desktop Code tab | [D] CLI / [S] desktop | probe tool that stays `working` until a file appears; run in CLI and desktop |
| D5 | Inbox socket accepts posts from MCP child processes; wire format | [D] / [S] format | from the shim, write auth line + one line to the socket; observe with `--debug` |
| D6 | `CLAUDE_CODE_MESSAGING_SOCKET` inherited by MCP stdio servers | [S] | shim logs its env on start |
| D7 | Plugin monitors notify an idle session | [D] | `monitors.json` with `tail -F`; append a line from another terminal |
| D8 | `asyncRewake` hook wakes an idle session | [D] | SessionStart hook that waits for a file and exits 2 |
| D9 | Mods render band and pane in CLI and desktop; `$.prompt.submit` queues | [T] validate+unit test / [S] desktop live | `claude --plugin-dir ./lwb-mod` in CLI and desktop with a fake inbox |
| D10 | Mods can reach 127.0.0.1 or the plugin MCP server | [S] | mod calls `fetch('http://127.0.0.1:8765/health')`; if blocked, call a plugin MCP tool |
| D11 | Hooks add context on UserPromptSubmit, Stop, PostToolUseFailure, SessionStart, PreCompact | [D] | one hook per event that echoes a marker; check it reaches the model |
| D12 | PreToolUse hook can deny reads of `~/.lwb/sealed` | [D] | deny rule test with Read and `cat` |
| D13 | Forked subagent tool calls are not shown in the main transcript | [S] | open a card from a `context: fork` subagent; screenshot CLI and desktop |
| D14 | Remote Control forwards AskUserQuestion and pushes | [D] | `/remote-control`, enable push, trigger an idle_prompt hook, answer from phone |
| D15 | Artifact `room.sendToClaudeSession` and `comments.sendToClaude` reach the session | [D] | publish room page with `room` and `comments`; press Send on phone; check arrival |
| D16 | Artifact `sample` grades on page | [T] | done |
| D17 | Cloud scheduled task with push runs `room-push` | [D] | daily task with `create_new_session_on_fire` and push on; watch one run |
| D18 | Codex `Stop` hook `decision: block` continues with a prompt | [D] | Stop hook that blocks once after tests passed |
| D19 | Codex app-server `turn/steer` into a thread | [D] | 30-line script: start thread, subscribe `turn/completed`, steer once |
| D20 | Attaching a companion to a thread the TUI or desktop app owns | [S] | run `codex app-server` beside a live TUI thread; try `thread/resume` by id |
| D21 | Codex `request_user_input_async` answerable in ChatGPT iOS | [D] | ask one async question; answer on the phone; check the thread |
| D22 | Codex desktop renders MCP App panels | [R] issue 21019 closed 2026-08-05 | run `experiments/mcp-app/server.py` in the current ChatGPT desktop Codex view |
| D23 | MCP Apps do not render in any Claude Code surface | [T] 2026-11-07 | re-test only when release notes mention it |
| D24 | Cursor `stop` hook `followup_message` auto-submits; MCP Apps inline | [D] | one stop hook; point Cursor at the probe server |
| D25 | ACP `elicitation/create` in Zed; a proxy agent can insert it | [D] spec / [S] Zed + proxy | pass-through proxy that sends one elicitation before the first prompt |
| D26 | Web Push to a Home Screen PWA on iOS; Declarative Web Push and badge | [D] | `docs/app/` manifest + subscribe page; one push from `workflow_dispatch` with pywebpush |
| D27 | ntfy publish works; retention window; CORS for PWA polling | [T] publish / [S] retention and CORS | publish a ciphertext, poll from the PWA after 1 h and 13 h |
| D28 | WebCrypto ECDH P-256 + AES-GCM interop with Python (`cryptography` or a stdlib-only path) | [S] | seal in Safari, open in Python; note that stdlib has no ECDH, so `lwbd` needs one dependency or a pure-Python X25519 (about 80 lines) |
| D29 | Union merge of `.learning/*.jsonl` | [T] | done |
| D30 | `CLAUDE_CLIENT_PRESENCE_FILE` reflects terminal focus | [D] | read it from a hook while switching windows |
| D31 | Desktop Browser pane hosts the local page via `.claude/launch.json` | [D] | add the launch entry, open the pane |
| D32 | MCP 2026-07-28 `server/discover`; Claude Code falls back to 2025-11-25 | [T] | done; re-test each release |
| D33 | Agent Skills shared at `.agents/skills` with `agents/openai.yaml` | [D] | symlink, run `/skills` in Codex and Gemini CLI |
| D34 | SEP-3118 app-rendered elicitations | [S] not merged | track ext-apps PR 733; run the reference inspector branch |

---

## 15. First week of experiments

Ordered by how much design each one unlocks per hour.

1. **X1 to X3 (half a day)**: D5, D6, D10. If the shim can post to the inbox
   socket and the mod can reach the daemon, sequence 5.1 is real on desktop.
   If not, the fallbacks are monitor lines and `$.prompt.submit`, which are
   already documented.
2. **X4 (1 hour)**: D4 in CLI and desktop. Decides whether "during" uses tasks
   or the band only.
3. **X5 (1 hour)**: D13 and D12 together. Decides how sealing looks.
4. **X6 (1 hour)**: D3 on the phone. Decides whether cloud sessions need any
   other door.
5. **X7 (2 hours)**: D18, D19, D20 in Codex. Decides whether Codex gets
   wait-time cards or only blocking forms.
6. **X8 (half a day)**: D26, D27, D28. The mailbox and PWA are the most
   ambitious piece; one push and one sealed round trip prove it.
7. **X9 (1 hour)**: D22. If the Codex desktop renders MCP Apps, the designed
   card ships there in M2 instead of M5.

Each experiment writes its result into `experiments/<name>/README.md` and
updates the status column above.

---

## 16. Risks and open questions

- **One more thing to install.** Mitigation: socket activation from the shim,
  idle exit, and full fallback to direct files. The learner never manages the
  daemon.
- **Return-path drift.** Hooks, mods and the inbox socket change between
  releases. The registry probes every session instead of trusting versions,
  and the order in section 6 is data in `config.json`, not code.
- **Over-asking.** The daemon is the one place that can see all sessions, so
  the caps live there. A learner with three sessions still gets one
  prediction at a time.
- **Grading needs a model.** Phone answers wait for the next session unless
  the learner uses the claude.ai artifact. A future option is a hosted grader
  (A2A tutor agent) if the learner wants grading with the laptop closed; that
  needs an API key and moves rubrics off the machine, so it stays opt-in.
- **Rubric sealing is a deterrent, not a vault.** The commit hash makes the
  "fixed before the question" rule checkable, which is the property the
  research needs.
- **Open**: can a mod draw on the Claude app's phone view of a desktop session
  (today: no)? Does Remote Control forward elicitation forms as well as
  AskUserQuestion? Does Codex expose a thread id to MCP servers so the daemon
  can target `turn/steer` without the learner attaching?
