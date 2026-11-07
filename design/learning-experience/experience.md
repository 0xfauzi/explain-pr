# Product experience specification: learning while building

Status: specification for prototypes, revised 2026-11-07 after the expert panel
review (`critique/`). Nothing here is built yet. Inputs:
`research/learning-science.md` (rules R1 to R38), `research/product-patterns.md`
(patterns H, I, C, N, P, E, O, A), `architecture/recommended.md` ("Room first,
agent native"), the approved site (`docs/index.html`, `docs/assets/site.css`,
`docs/assets/site.js`) and the skill's Voice section in
`skills/learning-while-building/SKILL.md`.

This document says what the learner sees, on which surface, at each moment, and
what the agent does. It gives the exact copy for every state. The design system
(tokens, components, motion, accessibility) is in `design-system.md`. Section 4
lists the prototype pages. Where a step depends on a phase 2 or phase 3
mechanism, it says so and gives the phase 1 behaviour next to it.

Tags used where a claim depends on a mechanism: **[T]** tested in this project,
**[D]** documented, **[S]** our inference, not tested. **P1**, **P2**, **P3** mark the
phase that makes a step possible.

---

## 0. The product in one paragraph

You build with the agent in chat. At two moments in a task you choose to learn
from, the agent asks you one question: before it builds (a prediction about
something the build will show) and after it works (explain why it works). At
"Not yet" and "With help" it may also leave one marked line for you to write.
You answer in chat with one line, or in the Room, a private page that opens
beside the session on the desktop and in the Claude app on the phone. The same
question is in both places, in the same state. When you answer, you say how sure
you are. The agent grades against an answer it fixed before it asked. Then you
see what you said next to what happened, and one button puts you back in the
build. Days later the same idea comes back as a new question. The Map shows what
you can do without the agent, and it goes down when you forget.

### 0.1 Decisions this document makes

Each one is applied everywhere below. D10 to D18 come from the panel review.

| # | Decision | Why |
|---|---|---|
| D1 | Level words shown to the learner follow the site: **Not yet**, **With help**, **Without help**, **New situation**. The data keeps the skill's names (`not yet`, `with help`, `recalls`, `transfers`). | The site is the approved language. |
| D2 | Confidence labels are **Guess**, **Fairly sure**, **Sure**, each with its meaning and a target: Guess "I would not bet on it" (right less than 1 in 2), Fairly sure "More likely right than wrong" (about 2 in 3), Sure "I would be surprised to be wrong" (4 in 5 or better). "I do not know" is a separate action. | Certainty-based marking needs defined levels (R21). |
| D3 | Interface labels use STE style with no contractions ("I do not know", "Not now", "Lock my answer"). Feedback prose follows the skill's Voice. | Two registers, each approved in its place. |
| D4 | The button that commits an answer is **Lock my answer** everywhere. After it: "Locked." | One verb across doors (C1). |
| D5 | The resume cue has one form: `Back to: <task>. Next: <step>.` | One shape is easy to scan and to test. |
| D6 | The Room tab bar has four items: **Inbox**, **Map**, **Drills**, **Explainers**. Settings is behind the learner's initial. Card, Compare, Verdict and Drill are focused views with no tab bar. | The answer is the only job on those screens. |
| D7 | The record ramp keeps its colours, and every filled cell gets a 1.5px ink outline and a bar glyph (1, 2 or 3 bars). Best level is an outline ring, latest is the fill. | Two of three ramp colours fail 3:1 [T]. Decay must be visible. |
| D8 | Control borders are `#7A7A83` (3.86:1), not `#8E8E96`. | Measured [T]. |
| D9 | Predictions are compared, never graded. Compare shows "You said / It did / The gap" and the chip **Compared**, with no verdict word. They never move a level. | R9: errors on predictions must be safe. |
| D10 | **The level rule**, one sentence used on every surface and in `record.py`: "Levels change only at reviews: right without help at a review a week or more after you first met the idea gives Without help, and right on a case unlike any you have seen gives New situation." An explain-back in the session where the agent wrote the code confirms With help at most. Its verdict says: "This counts when it holds at your review on <date>." | Same-session answers measure working memory, not recall (Rhodes and Tauber; `record.py` `DURABLE_AFTER_DAYS = 7`). |
| D11 | **Caps.** A hint, or opening the code on an explain, review or transfer card, makes the attempt count as With help. A drill credits the topic the planted bug exercises. The restatement after "Not quite" is not graded. | The record must say what the learner did alone. |
| D12 | **Question quality.** A prediction is answerable from what the card shows plus the concept, its observable is deterministic, and it targets the topic's known misconception when there is one. Reviews are free text or a number, never options. Options appear only on predictions at Not yet. Transfer, diagnosis, repair and interleaved cards show the area, not the topic, until the lock. A transfer item differs from every earlier item and feedback in surface (object, code shape, failure) and keeps the deep structure; its rubric holds a "distance" note, and the grader gives no New situation credit if the item restates earlier feedback. | Recall beats recognition (Roediger and Karpicke). Transfer fails when people do not notice which idea applies (Gick and Holyoak). |
| D13 | **No card ids in learner-facing strings.** In chat a card is named by topic and moment ("the retry-budget prediction"). | Ids feel like a debug view and invite copying. |
| D14 | **One learning event, one transcript row.** `lwb_post` seals and posts. `lwb_sync` reads the Room, imports and checks the seal. Its result line is the learner-facing copy. | Each tool call is its own row in Claude Code. |
| D15 | **One way back.** Every learning exchange in the Room ends with one primary **Back to the build** button, with the resume cue as its caption. No other "back" link on card, verdict or drill views. | It is the product's signature action. |
| D16 | **I do not know.** On predictions it first asks "Write your best guess in a few words. It costs nothing." with **Show the answer** behind it. On reviews it locks at once (an honest miss is valid evidence). It is never counted in calibration. | Errorful generation beats being shown the answer (Kornell, Hays and Bjork 2009). |
| D17 | **Keys are safe and optional.** Settings has "Keyboard shortcuts: On / Off". No single letter key locks an attempt: D and H ask once ("Lock as I do not know? Enter / Esc"). | WCAG 2.1.4. A stray key must not write to the record. |
| D18 | At most 3 due cards a day, as `record.py` `DEFAULT_DUE_LIMIT = 3`. Overflow spreads to later days. | One number in the spec and the engine. |

---

## 1. Principles

### 1. Learn at the breaks the work already has

Ask only at coarse breakpoints: when the agent starts a long step, while it
works, and when a build passes (Adamczyk and Bailey 2004; Iqbal and Bailey;
Cai et al. 2015, R1, R2). *Rule:* the prediction goes out with "Starting the
build now", and the learner answers while the agent works.

### 2. The learner thinks first, the agent explains second

Every learning moment starts with the learner generating something: a
prediction, a hypothesis, an explanation, one line of code. The agent's
explanation comes after (Shen and Tamkin 2026; Bastani et al. 2025). *Rule:*
answers, code and old feedback stay hidden until the lock (R17, R19). "How does
this work?" questions are answered at once (R16).

### 3. Every prediction gets its comparison

The learning comes from the gap, named with evidence (Sinha and Kapur 2021;
Metcalfe 2017). *Rule:* a `predict` card is done only after "You said / It did /
The gap" with a `path:line` (R6, R8). The gap names what the card showed and the
answer left out, never something the card hid.

### 4. Confidence is part of every answer

A confident wrong answer is the most useful event in the record
(hypercorrection, Metcalfe 2017), and calibration is what AI use erodes
(Prather et al. 2024). *Rule:* Lock is disabled until a confidence is chosen or
"I do not know" is pressed. The Map shows calibration against target bands.

### 5. One card, one state, every door

The learner never copies, never re-explains, never sees two states for one
question. *Rule:* every door shows the same topic, reason line and state word;
the earliest lock wins, and a later answer is named before the verdict.

### 6. Calm by default, the learner moves things to the centre

The learning layer lives in the periphery and comes to the centre only at the
two research moments or on the learner's gesture (Weiser and Brown 1995; N1).
*Rule:* one open card at a time, at most one unprompted learning turn per 10
minutes, at most one push a day, no sound, never a push while the learner is at
the machine. "Not now" and "just do it" work at once and cost nothing (R20).

### 7. Plain feedback about the task, then the way back

"Correct." / "Not quite." / "No." Then the reason in the learner's own terms,
the evidence, when it returns, and the resume cue (Kluger and DeNisi 1996;
Hattie and Timperley; Altmann and Trafton 2002). No praise (R14, R26, R27).

### 8. An honest record that can go down

The record shows what the learner can do without the agent, and it drops when a
review is missed. No streaks, points or percent bars (R32, R34 to R36). The
level rule (D10) is the only way up. *Rule:* best level as an outline, latest
as the fill; the only number on the Inbox is the due count.

---

## 2. Journeys

### 2.0 The example used in every journey

The learner, Sam, is building `orbit-pay`, a payments service, with Claude Code
in the Claude app, in a cloud session opened on the laptop and on the phone. The
repo is public, so the record lives in a private `learning-record` repo. Today
is 7 Nov. Sam first met `idempotency` and `retry-budget` on 7 Oct. Dimensions:
Distributed systems, Data and storage, Debugging and diagnosis, Correctness and
testing, Security, Reading code. The one story every page tells is in
`assets/orbit-pay.json`.

"Agent and system" names tool calls as `lwb_*`. Each `lwb_*` call is one row in
the transcript.

### 2.a Start a learning task: the prediction, the answer, the build continues

Sam asks for retries in the payment worker. `retry-budget` is at "With help".

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Sam: "Add retries with backoff to the charge call in the payment worker. Three attempts max." | Chat, laptop | Skill rule (P1) or `UserPromptSubmit` hook (P2) matches topic `retry-budget`. No card is open; the rate rule allows one. |
| 2 | The agent's plan line: "I'll wrap `charge()` in a retry with backoff and add `test_retry_budget`." | Chat | A subagent writes the rubric from the code and calls `lwb_post`, which seals and posts in one call. One row: `lwb_post · question posted, answer fixed 13:58`. |
| 3 | "Starting the build now." then the text card (3.1): **Question · retry-budget · before the build** / "With a dead gateway and the test's fixed clock, how long does test_retry_budget wait before charge() gives up?" / `billing/charge.py:41-52` / `Answer + how sure · not now · Open card` | Chat | The excerpt shows line 41, `@retry(attempts=3, backoff=(0.5, 1.0), jitter=0.1)`, and line 49, `timeout=0.8`. The fake clock makes the result exactly 4.1 s, so the answer is computable from the card. The agent starts editing at once. |
| 4 | Tool rows stream as usual. | Chat | Card stays answerable. |
| 5 | Sam: "about 3.9 s, fairly sure". | Chat | At the next turn boundary the agent calls `lwb_lock` with the time of Sam's message. One line: "Locked. Shown after test_retry_budget runs." |
| 6 | The agent runs `pytest -k test_retry_budget`. | Chat | `lwb_reveal` (P2: `PostToolUse` injects the reveal). |
| 7 | Compare in chat: `You said: about 3.9 s (fairly sure)` / `It did: gave up at 4.1 s` / `The gap: you added three timeouts and two backoffs, 3.9 s, and left out the jitter on line 41, 0.1 s per backoff. billing/charge.py:41.` / `Back to: retries in the payment worker. Next: the cap on total retry time.` | Chat | `lwb_grade` type prediction, no level change (D9). Compared, consolidated. |
| 8 | Build continues. | Chat | No new unprompted learning turn for 10 minutes. |

Branches:

- **Sam does not answer before the observable runs.** The agent holds the result
  only when the card is marked as a misconception check. Otherwise it shows the
  result and records `not_now`. Held copy: "The test ran. Your prediction is
  still open. Answer now, or say 'show result'."
- **"Not now" or "just do it".** One line: "OK. Back to: retries in the payment
  worker. Next: the backoff loop." No more questions this session for this task.
  Time to next tool call under 5 s.
- **"How does jitter work?"** Answered at once, then one line: "Your prediction
  is still open: how long until charge() gives up?"
- **"I do not know".** "Write your best guess in a few words. It costs nothing.
  Or say 'show the answer'."
- **Your line (completion problem, Not yet and With help).** In a task Sam chose
  to learn from, the agent writes everything but one marked line and stops at
  it: "Your line: billing/charge.py:47 is marked `# YOUR LINE`. Write the
  `idempotency_key=` value so a retry cannot charge twice. Say 'write it' and I
  will. test_idempotent_retry grades it." The test result is the grade
  (`lwb_grade kind=completion`). "write it" is free and immediate. At most one
  per task.
- **Not yet.** A worked example with labelled steps from this repo, then a
  completion question after the build.

### 2.b Step away, answer on the phone, return without friction

The build passed. The turn ended with the explain-back. Sam leaves the laptop.

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Last chat message: **Question · idempotency · after it works** / "Why can the worker retry charge() without charging the customer twice?" / `Answer + how sure · not now · Open card` | Chat, laptop | `lwb_post moment=after`. Room db: `cards/<id>` written by the agent; the key in `keys/<id>`, never subscribed by the page. |
| 2 | P1: nothing on the phone. P2 (E-PUSH): when the laptop is idle, one push: "1 question about idempotency. About 1 minute." | Phone | One push a day at most. |
| 3 | Sam opens the Room in the Claude app. Inbox: **Now** row "After it works · idempotency · About 1 min". | Room, phone | Only the due count is a number. |
| 4 | Focused card view, no tab bar. Reason line, prompt, answer field directly under the prompt, confidence, then **Show the code** (collapsed; opening it shows "This attempt now counts as With help.") | Room, phone | Card state `delivered(room)`. |
| 5 | Sam writes "The idempotency key is the order id, so the gateway sees the same key and returns the first charge." Chooses **Sure**. **Lock my answer**. "Locked." | Room, phone | Page creates `answers/<id>/<uuid>` once, with `sha256(answer)`. Then it reads `keys/<id>` once. |
| 6 | "Grading..." for 1 to 4 s, then **Correct.** "The key is the order id (billing/charge.py:47), and the gateway returns the stored result for a repeated key." "This counts when it holds at your review on 10 Nov." The idempotency cell shows a faint pending ring, not a fill. | Room, phone | `sample` grades on the page; `grades/<id>` written by the page. |
| 7 | Under it: **Back to the build**, caption "Claude adds this on your next message." (P2: "Sent to your session.") | Room, phone | P2 bell ladder (architecture 8): Claude Code Remote `send_message`, then `sendToClaudeSession`, then the pull rule. |
| 8 | Back at the laptop: "Now add a dead letter queue for failed charges." | Chat, laptop | Pull rule: one `lwb_sync` row reads the Room docs, imports (hash checked) and checks the seal. |
| 9 | The reply starts: "From the Room: idempotency, Correct. It counts at your review on 10 Nov." Then the work. | Chat | No extra turn. |

Branches:

- **Answered in both places.** Earliest lock wins, named first: "You answered in
  chat at 14:01 and in the Room at 14:02. I graded the chat answer." Then the
  verdict, then the resume cue last.
- **Phone offline.** "Not sent yet. Keep this page open until it says Sent."
  Chip **Not sent**. "Sent" shows only after a confirmed write (E-OFFLINE).
- **Session gone.** The Room grade stands. The next session imports it at start:
  "1 answer from the Room added: idempotency."

### 2.c The explain-back after it works

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | "Retries are in. test_retry_budget and test_idempotent_retry pass." No mechanism explained. | Chat | Skill rule (P1) or `Stop` hook (P2). Key fixed first. |
| 2 | One specific question (R11): "Why can the worker retry charge() without charging twice?" | Chat | The turn ends with the question. P2 (E-AUQ): confidence as three taps. |
| 3a | "Correct. The key is the order id and the gateway returns the stored result for a repeated key (billing/charge.py:47). This counts when it holds at your review on 10 Nov." + resume cue | Chat | Consolidation. Level stays With help (D10). |
| 3b | "Not quite. The key is what makes it safe, yes. It must be the order id, not a new value per attempt. billing/charge.py:47. Back tomorrow." Then: "Say it again in one line if you like. Not graded. It helps it stick." + resume cue | Chat | Partial returns next day. Restatement not graded (D11). |
| 3c | "No. A timeout only means the reply did not arrive; the charge may have run. The key at billing/charge.py:47 is what stops a second charge. Back tomorrow." | Chat | Miss returns next day. |
| 3d | As 3c, plus "You chose Sure. This one returns tomorrow and is marked on your map." | Chat | Sure-miss mark. |
| 4 | "explain it" gives the full explanation after the grade. | Chat | Never changes the grade. |

### 2.d A review session days later

10 Nov. Two reviews are due.

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | At session start, once: "2 reviews due. About 3 minutes. Say 'review' or open the Room." | Chat | P1 skill rule `learning.py due --count`; P2 `SessionStart` hook. |
| 2 | Or the Room: Inbox **Due 2**. Rows "Review · idempotency · 3 days" and "Review · retry-budget · 3 days". **Start review**. | Room | P2 (E-SCHED) daily task writes cards. No lateness counts. |
| 3 | Card 1, free recall in new words: "After a timeout, why is it safe for charge() to send the same request again? Say what the gateway uses and what it does with it." No code, no old answer. | Room | New instance (R18), not the old prompt. |
| 4 | **Correct.** "The gateway sees the same order id as the key and returns the stored result." "Now Without help." The cell lights: this is a review, a month after Sam met the idea. Reveal: "What you wrote on 7 Nov". "Back on 17 Nov." | Room | Level rule D10. `reviews.jsonl` row. |
| 5 | Card 2, retry-budget, a number field: "Same retry, but backoff is 1 s then 2 s. With the fixed clock, how long until charge() gives up?" | Room | Recall, not options (D12). |
| 6 | "Done. 2 reviewed. Next review on 14 Nov." **Back to the build** if a session is linked. | Room | Week dot fills. |

On 17 Nov idempotency, now at Without help, returns as a new case with the
topic hidden: "Review · a new case · Distributed systems". "A webhook handler
saves each event, then emails the customer. The sender retries when it gets no
200 within 5 s. Some customers get two emails. What would you change, and why?"
Its key holds a distance note (new object, new failure, new code shape). Right
gives New situation. When the record shows confusion between two ideas, an
interleaved case asks without a menu (R19): "A job runs twice after a worker
restarts. The charge inside it ran once. Why?"

At most 3 due cards a day (D18): "1 more moves to tomorrow." A delayed
self-judgment is asked once per topic at the 21-day review, stored as
self-report only (R25).

### 2.e "What am I weak at?" and the Map

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | "what am I weak at?" | Chat | `lwb_map`. |
| 2 | `Weakest: Debugging and diagnosis. 1 of 4 topics without help. timeouts-vs-failures was a sure miss on 4 Nov.` / `Since 31 Oct: retry-budget dropped from Without help to With help at its review on 2 Nov.` / `Due: 2. Map: Open map` / "Want a drill on timeouts-vs-failures? About 10 minutes." | Chat | Text grid on request. |
| 3 | Map: "Weakest now", then the record grid, then "How sure vs how right", then "Last 4 weeks". The only control above the fold is the grid's own Grid / Table switch. | Room | `map.json`, no answers. |
| 4 | A dimension row expands to topic cells. A dimension's level is its lowest current topic level, with the count: "Without help · 2 of 3 topics". | Room | Rollup rule. |
| 5 | Topic sheet: dated attempts with verdict words, next review, "Answer fixed 14:15. You locked 14:22.", **Review now**, **Drill this**. Modal on the phone. | Room | No answer shown for a due card. |

### 2.f A debugging drill

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | **Drill this** on `timeouts-vs-failures`, or "drill me on timeouts". | Room or chat | Scratch worktree; plants a bug from this project's history that exercises the topic: `except GatewayTimeout: return Declined(order.id)`. Key: cause and a check. |
| 2 | "Drill · Debugging and diagnosis" (topic hidden). Symptom: "A customer was charged, but the order shows Declined and the shop sent 'payment declined'. test_lost_reply fails." No code yet. | Room or chat | `lwb_post kind=repair`. |
| 3 | Step 1: "What do you think causes it?" Step 2: "What check would show it?" Confidence. **Lock my hypothesis**. | Room | Hypothesis before code (E7). |
| 4 | The agent runs Sam's check and shows its output. "You can change your cause once." Then the file list and the module open; an optional line pick. | Room, session linked | The learner tests their own hypothesis (R14, R16). |
| 5 | Verdict per part: "Cause: Correct. A timeout is read as a decline (billing/charge.py:51)." "Check: Not quite. Your print shows the status, but the test that proves it makes the fake gateway charge and drop the reply." Then the topic name. | Room | Credits `timeouts-vs-failures`. Hints cap at With help. |
| 6 | "Back on 10 Nov. The safe copy is deleted when you close this drill." **Back to the build**. | Room | |

In a real build, when a learning-task test fails: "test_no_double_charge fails.
Call the cause first? Say it in a line, or say 'not now'." Once per failing test.

### 2.g An explainer

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | "explain PR 128". | Chat | Built from `assets/explainer-template.html`. At New situation: a summary and a hard question instead. |
| 2 | "Explainer ready: How the retry path works. 6 minutes, 3 questions inside. Open explainer" | Chat | Private artifact. |
| 3 | Sections with neutral headings until their question locks ("1. When the reply is lost"). The diagram comes after question 1. Options, when used, are of similar length. No hint control on prediction cards. | Explainer | Embedded cards are sealed. |
| 4 | After the lock, the section opens, its real heading shows ("A timeout is not a failure"), Compare inline. | Explainer | Prediction, no level change. |
| 5 | "3 questions from this page are in your reviews. First one on 10 Nov." | Explainer | |

### 2.h First run and onboarding

No tour, no welcome modal (O1). First value is one real question on Sam's code.

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | "use learning while building on this project" | Chat | `learning.py init`; `gh repo view --json visibility`. |
| 2 | "This repo is public. A record in it would be public too. I can keep your record in a private repo, learning-record. Create it? Reply 'yes' or 'keep it local'." | Chat | E-REPO is a phase 1 gate. "keep it local" in a cloud session adds: "A cloud session forgets local files. Your record then lives in the Room only." |
| 3 | "I'll track these areas. Change them now or later: Distributed systems, ..." | Chat | Detected from code. |
| 4 | "Mode: Normal (one question before a build you choose to learn from, one after). Also: Quiet (reviews only), Deep (adds drills)." | Chat | `config.json`. |
| 5 | Nothing else until the next real task. | Chat | |
| 6 | After the first grade, once: "To see waiting questions, say /learn. To stop questions for now, say not now. Your Room: Open Room" | Chat | Room published, private. |
| 7 | First Room visit: empty Inbox, faint map, "Your record is empty. It fills when you answer questions about this project." | Room | No fake data. |

### 2.i A missed or skipped question

| Case | Learner sees | System |
|---|---|---|
| Not now in chat | "OK. Back to: <task>. Next: <step>." | Card to Later; no more questions on this task. |
| Not now in the Room | The card's place in Now shows "Moved to Later. Undo", and focus goes there. It stays until the next action. | Never a miss (I2). |
| Snooze | **After this build**, **Tomorrow**, **Next week**. | |
| Never seen | Nothing. Removed from Later after 7 days. | `skipped`. |
| I do not know (prediction) | "Write your best guess in a few words. It costs nothing." / **Show the answer** | D16. |
| I do not know (review) | "Not known yet. This is the answer: <one or two lines>. Back tomorrow." | Miss for scheduling; not in calibration. |
| Miss at review | "No. <reason, evidence>. Back tomorrow." Fill drops, best stays as outline. | Next day, then 3 days. A miss on a harder variant is marked "uncertain" and drops only if it repeats. |
| Away three weeks | "Due 3" and "9 more over the next 3 days." No "welcome back". | Cap 3 (D18). |
| Three ignored pushes (P2) | "Reminders are off. They come back when you turn them on in Settings or say /learn." | Nudge ledger. |
| Pause | "Reviews paused until 14 Nov. Resume" | Dates shift. |

### 2.j Ending a project and seeing growth

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | "this project is done" or `/learn wrap`. | Chat | `lwb_map` plus history. |
| 2 | `orbit-pay, 7 Oct to 7 Nov. 31 questions, 9 topics.` / `Without help or better: 5 topics (was 0). New situation: 1 (outbox).` / `At Sure you were right 9 of 11 times (target 4 in 5).` / `Still weakest: timeouts-vs-failures.` / `Growth page: Open` / "Reviews continue after the project. Keep them, or stop them?" | Chat | |
| 3 | Growth (a link from the Map's record card): "Start (7 Oct)" and "Now (7 Nov)" panels, a timeline per dimension, calibration then and now, "Lines you wrote: 4 marked lines, 3 passed first time". Drops are named: "retry-budget was Without help on 20 Oct. It is With help now." | Room | Every number links to its attempts. |
| 4 | **Export**: Markdown and JSON. | Room | `downloads`. |

No certificate, no celebration animation.

---

## 3. Surfaces, states and copy

### 3.0 The shared state set

| State | Meaning | State chip |
|---|---|---|
| empty | Nothing to show yet. | (none) |
| loading | Data is being fetched. | (none) |
| waiting | Delivered and open. | **Open** |
| answered | Locked, not graded yet. | **Locked** |
| compared | A prediction met its observable. | **Compared** |
| graded right / partial / wrong | "Correct." / "Not quite." / "No." | **Correct** / **Not quite** / **No** |
| confident and wrong | "No." at Sure. | **No · sure** |
| not sent | Offline, write not confirmed. | **Not sent** |
| error | Say what failed and what still works. | (none) |

Also handled: **dont_know**, **not_now**, **skipped**, **also_answered**,
**held result**, **paused**. Copy rules: plain words, one idea per sentence, no
praise, no exclamation marks, no em dashes, no "Oops", no loss framing, no
lateness counts. Level words never wrap (`white-space:nowrap`).

### 3.1 Chat text card (Claude Code, Codex, terminal, push bodies)

Plain markdown that every harness renders: one bold line, the prompt, the path
in code format, one instruction line. No colour, no chips, no tinted boxes.

```
**Question · <topic> · <moment words>**
<prompt, one or two sentences>
`<path:line range>`
Answer + how sure · not now · Open card
```

On the learner's first 3 cards only, the last line is the long form: "Reply
with your answer and how sure you are: guess, fairly sure or sure. Or 'not now'.
Or answer in the Room: Open card". On transfer and drill cards the header shows
the area instead of the topic. Moment words: "before the build", "after it
works", "review", "drill", "your line".

| State | Exact copy |
|---|---|
| waiting | the card, sent with "Starting the build now." for predictions |
| answered (prediction) | "Locked. Shown after test_retry_budget runs." |
| from the Room (P1) | first line of the next reply: "From the Room: <topic>, <verdict word>. <counts line or Back on date>." |
| graded right (same session) | "Correct. <what holds, path:line>. This counts when it holds at your review on <date>.\nBack to: <task>. Next: <step>." |
| graded right (review) | "Correct. <what holds>. Now <level>. Back on <date>.\nBack to: ..." |
| partial | "Not quite. <what holds>. <what is missing, path:line>. Back tomorrow.\nSay it again in one line if you like. Not graded. It helps it stick.\nBack to: ..." |
| wrong | "No. <which inference fails>. <evidence>. Back tomorrow.\nBack to: ..." |
| confident and wrong | wrong copy plus "You chose Sure. This one returns tomorrow and is marked on your map." |
| compared (prediction) | "You said: <answer> (<confidence>)\nIt did: <observed>\nThe gap: <one sentence, path:line>.\nBack to: ..." |
| dont_know (prediction) | "Write your best guess in a few words. It costs nothing. Or say 'show the answer'." |
| not_now | "OK. Back to: <task>. Next: <step>." |
| held result | "The test ran. Your prediction is still open. Answer now, or say 'show result'." |
| also_answered | before the verdict: "You answered in chat at 14:01 and in the Room at 14:02. I graded the chat answer." |
| your line | "Your line: <path:line> is marked `# YOUR LINE`. <what it must do>. Say 'write it' and I will. <test> grades it." |
| error: seal failed | "I could not fix the answer before asking, so I will not ask this one. Back to: <task>." |
| error: Room unreachable | "The Room did not answer. Answer here instead, or later. Nothing is lost." |
| error: import rejected | "An answer from the Room did not match its sealed card, so I did not add it. It is in learning/rejected.log." |
| session start | "2 reviews due. About 3 minutes. Say 'review' or open the Room." |

Terminal: the same text, then `Answer:` and `How sure? [1] guess [2] fairly sure
[3] sure [d] don't know [n] not now`. Transcript rows: one per learning event
(D14): `lwb_post · question posted, answer fixed 13:58`, `lwb_sync · 1 answer
from the Room`.

### 3.2 Room shell

Top bar (56px): "Room" wordmark and the project name in mono; the learner's
initial on the right (Settings). Tab bar on Inbox, Map, Drills and Explainers
only: on the desktop under the top bar, aligned to the content column; on the
phone fixed at the bottom, 64px with safe area, hidden on focused views (D6).
Content width 640px (Inbox, Card, Drill), 960px (Map). Grain over the page.

| State | Exact copy |
|---|---|
| loading | Three faint rows, no spinner; `aria-busy`; "Loading your Room." for screen readers |
| offline | Banner, `--card` background: "You are offline. Answers you lock now are not sent until you are back online. Keep this page open." |
| error: db unreachable | "The Room cannot reach its data. Your answers in chat still work. Try again" |
| error: no permission | "This Room belongs to another account. Open your own Room from the chat." |
| paused | "Reviews paused until 14 Nov. Resume" |

### 3.3 Inbox

Three groups (I1): **Now** (at most 1), **Due** (at most 3), **Later**. Empty
groups are not shown. Each row: reason, topic or area in mono, cost, state chip.
Keys (when on): J and K move, Enter opens. The Inbox has no "Back to the build"
button; its linked line reads "Linked to orbit-pay · cloud session".

| State | Exact copy |
|---|---|
| empty, first run | "Questions appear here before and after a build. Start a task you want to learn from, and the agent asks one." **Ask me one now** |
| empty, later | "Nothing is due. The next review is on 14 Nov." |
| waiting | Now: "After it works · idempotency · About 1 min · Open". Due: "Review · retry-budget · 3 days", "Review · a new case · Distributed systems". **Start review** |
| answered | Chip **Locked**, line "Grading..." or "Shown after the test runs." |
| graded | Row leaves after 2 s (no fade under reduced motion). Status line: "Correct. Back on 14 Nov." / "Not quite. Back tomorrow." / "No. Back tomorrow." |
| overflow | "1 more moves to tomorrow." / after time away: "9 more over the next 3 days." |
| Later | "Later · outbox ordering · Not now on 6 Nov" |
| not sent | Chip **Not sent**, "Keep this page open until it says Sent." |
| error: one card | "This question did not load. It is still in your record. Try again" |

### 3.4 Card (question)

Kinds: predict, explain, review, transfer, diagnose, completion (repair has 3.6).
Shapes: text, number, line-pick (second step only), order (at Not yet only),
choice (predictions at Not yet only).

Anatomy, top to bottom: reason line (eyebrow), topic or area and level in mono,
prompt, answer field, confidence, **Lock my answer**, one row of secondary
actions ("Not now", "I do not know", "Hint" where allowed), then the excerpt:
shown above the answer on predict cards; behind **Show the code** on explain,
review and transfer cards, where opening it is recorded as H1.

Confidence fieldset: legend "How sure are you?"; radios **Guess**, **Fairly
sure**, **Sure** with meanings; keys 1 2 3 (when on).

Hint: at With help and on drills only. Never on predictions, never at New
situation.

| State | Exact copy and behaviour |
|---|---|
| loading | Prompt skeleton; "Loading the question." |
| waiting | Lock disabled, helper "Choose how sure you are first." |
| answered (prediction) | Read only. "Locked. Shown after the test runs." and "You said" quote. |
| answered (explain, on page) | "Locked." then "Grading..." in the page's one live region |
| answered (session grades, P1) | "Locked. Claude grades it on your next message." |
| graded | Verdict (3.5) |
| dont_know (prediction) | "Write your best guess in a few words. It costs nothing." field, **Lock my guess**, **Show the answer** |
| not_now | Back to the Inbox; the Now slot says "Moved to Later. Undo" |
| show the code (explain, review) | Code opens. Line: "This attempt now counts as With help." |
| not sent | Chip **Not sent**. "Not sent yet. Keep this page open until it says Sent." |
| error: no key yet | "Locked. The grader cannot reach the answer key right now. Claude grades it on your next message." |
| error: already locked | "This question was answered in chat at 14:01. Open the result" |
| error: grader failed | "Locked. Grading failed. Try again, or Claude grades it on your next message." |

Phone: no tab bar. Only Lock is sticky (one 50px row). Below 560px of height
nothing is sticky. The secondary row hides while the answer field has focus.

### 3.5 Verdict and Compare

Compare (predictions): "You said" (quoted, with confidence) and "It did" (output
in mono with its command), then "The gap", the "Where the time went" bar when the
observable is a duration, and **Back to the build** with the resume cue.

Verdict (other kinds): the word, the reason with `path:line`, the record line,
the next date, the belief line when sure and wrong, the reveal ("What you wrote
on <date>", the topic name for hidden-topic cards), **Back to the build**.

| State | Exact copy |
|---|---|
| loading | "Waiting for the test output." |
| compared | chip **Compared**, "The gap: <sentence>." "Predictions do not change your record." |
| right, same session | **Correct.** "<what holds>." "This counts when it holds at your review on 10 Nov." Pending ring on the cell. |
| right, review | **Correct.** "<what holds>." "Now Without help." Cell lights. "Back on 17 Nov." |
| right, no level change | **Correct.** + the level rule (D10) as one line |
| partial | **Not quite.** "<what holds>. <what is missing>." "Back tomorrow." Say it again field: "Not graded. It helps it stick." |
| wrong | **No.** "<inference that fails>. <evidence>." "Back tomorrow." |
| confident and wrong | adds "You chose Sure. It returns tomorrow and is marked on your map." |
| record down | "retry-budget: Without help to With help." No red. |
| appeal | quiet link: "I think this grade is wrong" sends answer and key to the session for a second look |
| not sent | "Not sent yet. The result shows when it is sent." |
| error: output missing | "The test ran, but I could not read its output. Your prediction stays locked." |

"Correct." is ink; "Not quite." and "No." are `--accent-text`. The word always
carries the meaning.

### 3.6 Drill

Steps: Symptom, Hypothesis (cause and check, locked), Your check runs, one
revision, Reveal. Topic hidden until the reveal.

| State | Exact copy |
|---|---|
| empty | "No drills yet. Drills use bugs from this project. Ask for one from a topic on your map, or say 'drill me' in chat." |
| loading | "Setting up a safe copy of the code. About 20 seconds." |
| waiting | Symptom. "What do you think causes it?" "What check would show it? A log line, a test or a value to print." |
| check ran | "Your check printed: <output>." "You can change your cause once." |
| graded right | "Cause: Correct. <path:line>." "Check: Correct. <why it proves it>." |
| partial / wrong | per part, "Not quite." / "No." with evidence |
| hint ladder | "Hints used: 1 of 3", numbered dots, "This attempt now counts as With help." |
| offline | "You are offline. You can write your answer. Grading waits until you are back online." |
| error: worktree | "I could not make a safe copy of the code, so this drill did not start. Your code is unchanged." |
| done | "Back on 10 Nov. The safe copy is deleted when you close this drill." |

### 3.7 Map

Order (R30): Weakest now, the record card (grid, with Grid / Table in its
header and "See growth" as a link), How sure vs how right, Last 4 weeks. Scope
is quiet text: "This project · All projects".

| State | Exact copy |
|---|---|
| empty | Unlit grid. "Your record is empty. It fills when you answer questions about this project." |
| normal | "Weakest now: Debugging and diagnosis. timeouts-vs-failures was a sure miss on 4 Nov." **Review now**, **Drill this** (secondary). "Since 31 Oct: retry-budget is With help (was Without help)." |
| calibration | "How sure vs how right". Each bar has a target band: Guess under 1 in 2, Fairly sure about 2 in 3, Sure 4 in 5 or better. Under 10 answers at a level: "Too few answers to tell." First: "Sure but wrong: 2. timeouts-vs-failures, right since on 6 Nov. retry-budget, not yet." |
| last 4 weeks | 28 ink dots, filled on days with practice. "Days with practice, last 4 weeks." |
| topic sheet | "idempotency · Distributed systems". "Best: With help. Now: With help." "Next review: 10 Nov." "Answer fixed 14:15. You locked 14:22." |
| decay | outline ring at best, fill at latest |
| offline | "Showing your map from 14:20. It updates when you are back online." |
| error | "The map did not load. Your record is safe in learning-record. Try again" |

### 3.8 Explainer page

| State | Exact copy |
|---|---|
| empty | "No explainers yet. Ask in chat: 'explain PR 128'." |
| waiting | "Before you read on: <question>." Neutral heading. Section dimmed. **Lock my answer**, **Show without answering** |
| answered | "Locked." Section opens with its real heading. Compare inline. |
| show without answering | "Not answered. This question is not added to your reviews." |
| end | "3 questions from this page are in your reviews. First one on 10 Nov." |
| offline | Page works. "Not sent yet." |
| error: stale | "This explainer is out of date: billing/retry.py changed after it was built. Rebuild" |

### 3.9 Settings

| Control | Copy |
|---|---|
| Mode | **Quiet** "Reviews only." **Normal** "One question before a build you choose to learn from, one after." **Deep** "Normal, plus drills." |
| Your line | "Leave one line for me to write at Not yet and With help: On / Off" |
| Pause | **Pause reviews for a week** / "Paused until 14 Nov. Resume" |
| Reminders (P2) | "Phone reminders. At most one a day. Never while you are at your computer." |
| Keyboard shortcuts | "Keyboard shortcuts: On / Off". "Letter keys never lock an answer." |
| Record location | "Your record is in: 0xfauzi/learning-record (private)." |
| Privacy note | "Answer keys are fixed before each question and kept apart from the questions. You can read your own Room data, so the Room cannot stop you from looking." |
| Export | **Download my record** |

### 3.10 Onboarding, 3.11 Growth, 3.12 Push

Room first open: "This is your Room. Questions wait here, and your map shows what
you can do without the agent." with **Ask me one now**. Privacy choice: "Where
should your record live? This project is public." **Private repo
(learning-record)** / **This device only** (in a cloud session: "Room only").
Growth empty: "Growth shows after two weeks of answers on this project." Push:
"1 question about idempotency. About 1 minute." / "2 reviews due. About 3
minutes." Push bodies never hold code, answers or keys. Badge: due count only.
The mod band and pane (P3, local desktop) reuse the same components and copy.

---

## 4. Prototype pages

Eight static pages in `prototypes/`, one per surface. All load
`assets/room.css` (tokens and base) and `assets/grain.png`, so they work served
from this folder, from the repo root and on GitHub Pages. The story is
`assets/orbit-pay.json`. Each page has a dashed, mono "Prototype state" strip
(select, Prev and Next, `?state=`), a width switch that includes 640 by 360,
and a theme switch. The strip is not product UI.

| File | Shows | Journeys |
|---|---|---|
| `prototypes/flow.html` | Chat at real harness fidelity (Claude Code, Codex, terminal) beside the Room on a phone. Prediction, Compare, your line, explain-back on the phone, `lwb_sync` on return, the phase 2 bell ladder, also answered, not sent, Room down. | a, b, c, i |
| `prototypes/inbox.html` | Shell and Inbox: Now, Due, Later, cap, status lines, pause, not sent, errors. | b, d, i |
| `prototypes/card.html` | Every kind and shape, confidence, I do not know with best guess, Not now with Undo in place, show the code as H1, hint, locked, grading, not sent, errors. | a, b, c, d |
| `prototypes/verdict.html` | Compare with the gap and "Where the time went", verdicts with the level rule, pending ring, review lighting, decay, appeal. | a, c, d |
| `prototypes/map.html` | Weakest, the record card with Grid / Table and See growth, topic sheet, calibration with target bands, week dots, Growth. | e, j |
| `prototypes/drill.html` | Symptom, hypothesis first, your check runs, one revision, code after, two-part verdict. | f |
| `prototypes/explainer.html` | Neutral headings, diagram after question 1, no hints on predictions, show without answering, stale. | g |
| `prototypes/onboarding.html` | Chat first run, Room first open, privacy choice, areas, Settings with shortcuts and your line. | h, i |
