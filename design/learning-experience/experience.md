# Product experience specification: learning while building

Status: specification for prototypes, 2026-11-07. Nothing here is built yet.
Inputs: `research/learning-science.md` (rules R1 to R38), `research/product-patterns.md`
(patterns H, I, C, N, P, E, O, A), `architecture/recommended.md` ("Room first,
agent native"), the approved site (`docs/index.html`, `docs/assets/site.css`,
`docs/assets/site.js`) and the skill's Voice section in
`skills/learning-while-building/SKILL.md`.

This document says what the learner sees, on which surface, at each moment, and
what the agent does. It gives the exact copy for every state. Section 5 lists the
prototype pages to build. The architecture (`lwb` server, the card schema, the
lifecycle, the Room artifact, the phases) is taken as given. Where this document
depends on a phase 2 or phase 3 mechanism, it says so and gives the phase 1
behaviour next to it.

Tags used where a claim depends on a mechanism: **[T]** tested in this project,
**[D]** documented, **[S]** our inference, not tested. **P1**, **P2**, **P3** mark the
phase that makes a step possible.

---

## 0. The product in one paragraph

You build with the agent in chat. At two moments in a task you choose to learn
from, the agent asks you one question: before it builds (a prediction about
something the build will show) and after it works (explain why it works). You
answer in chat with one line, or in the Room, a private page that opens beside
the session on the desktop and in the Claude app on the phone. The same question
card is in both places, in the same state. When you answer, you say how sure you
are. The agent grades against an answer it fixed before it asked. Then you see
what you said next to what happened, and one line puts you back in the build.
Days later the same idea comes back as a new question. The Map shows what you
can do without the agent, and it goes down when you forget.

### 0.1 Decisions this document makes

These close gaps between the inputs. Each one is applied everywhere below.

| # | Decision | Why |
|---|---|---|
| D1 | Level words shown to the learner follow the site: **Not yet**, **With help**, **Without help**, **New situation**. The data keeps the skill's names (`not yet`, `with help`, `recalls`, `transfers`). | The site is the approved language. "Recalls" and "transfers" are terms of the method, not words a learner uses about themselves. |
| D2 | Confidence labels are **Guess**, **Fairly sure**, **Sure**, each with its meaning shown. "I do not know" is a separate action, not a confidence level. The site demo changes "Not sure" to "Guess" and "Almost sure" to "Fairly sure" so that every surface matches. | Certainty-based marking needs defined levels (R21). "Not sure" overlaps "I do not know". |
| D3 | Interface labels use STE style with no contractions ("I do not know", "Not now", "Lock my answer"), like the site. Feedback prose follows the skill's Voice, which allows contractions. | Two registers, each already approved in its place. |
| D4 | The button that commits an answer is **Lock my answer** everywhere (site wording). After it: "Locked." | One verb across doors (C1). "Lock" tells the learner the answer cannot change, which is the rule. |
| D5 | The resume cue has one form: `Back to: <task>. Next: <step>.` | One shape is easy to scan and to test (architecture section 2). |
| D6 | The Room tab bar has four items: **Inbox**, **Map**, **Drills**, **Explainers**. Settings is behind the learner's initial in the top bar. Card and Compare are views, not tabs. | Four items fit a 375px phone at 44px targets. A card is always reached from a reason (an inbox row, a link, a chat line). |
| D7 | The record ramp keeps its colours, and every filled cell also gets a 1.5px ink outline and a bar glyph (1, 2 or 3 bars). The best level is shown as an outline ring, the latest level as the fill. | Two of three ramp colours fail 3:1 [T]. Decay must be visible (P2). |
| D8 | The `.sure` pill border changes from `#8E8E96` (2.95:1 on paper, fails 1.4.11) to `#7A7A83` (3.86:1). | Measured in this session [T]. |
| D9 | Predictions are never graded as right or wrong in the record's level evidence. They are compared ("You said / It did") and the gap is named. Only explain-back, review, transfer and drill answers move a level. | R9: errors on predictions must be safe. |

---

## 1. Principles

Eight principles. Each names its evidence and the rule it turns into.

### 1. Learn at the breaks the work already has

Ask only at coarse breakpoints: when the agent starts a long step, while it
works, and when a build passes. Never in the middle of something the learner is
doing. The agent's wait time is the cheapest learning time there is.
*Evidence:* Adamczyk and Bailey 2004; Iqbal and Bailey 2007/2008; Cai et al.
2015 wait-learning (R1, R2). *Rule:* the prediction goes out with "Starting the
build now", and the learner answers while the agent works.

### 2. The learner thinks first, the agent explains second

Every learning moment starts with the learner generating something: a
prediction, a hypothesis, an explanation. The agent's explanation comes after.
This is the pattern that separated high and low scorers in Shen and Tamkin 2026,
and the hint tutor in Bastani et al. 2025. *Rule:* answers, code and old
feedback stay hidden until the learner locks (R17, R19). "How does this work?"
questions are always answered at once (R16), because asking is the protective
habit.

### 3. Every prediction gets its comparison

A prediction that is never compared with the outcome is only a delay. The
learning comes from the gap, named with evidence (Sinha and Kapur 2021; Metcalfe
2017). *Rule:* a `predict` card is not done until the learner has seen "You
said / It did" with one sentence on the difference and a `path:line` (R6, R8).

### 4. Confidence is part of every answer

Say how sure you are in the same action as the answer. A confident wrong answer
is the most useful event in the record (hypercorrection, Metcalfe 2017), and
calibration is the skill AI use erodes (Prather et al. 2024). *Rule:* the lock
button is disabled until a confidence is chosen or "I do not know" is pressed.
The Map shows calibration as three bars (R12, R13, R21 to R24).

### 5. One card, one state, every door

The learner never copies, never re-explains, never sees two states for one
question. The same card is in chat, in the Room on the desktop and in the Room on
the phone (GitHub notifications, Remote Control: pattern H1). *Rule:* every door
shows the card id, the reason line and the same state word; earliest lock wins,
and a later answer is shown as "You also answered on your phone".

### 6. Calm by default, the learner moves things to the centre

The learning layer lives in the periphery (a count, a line) and comes to the
centre only at the two research moments or on the learner's gesture (Weiser and
Brown 1995; Amber Case; pattern N1). "Not now" and "just do it" work at once
and cost nothing (R20; Linear agent guidelines). *Rule:* one open card at a
time, at most one unprompted learning turn per 10 minutes, at most one push a
day, no sound, never a push while the learner is at the machine.

### 7. Plain feedback about the task, then the way back

"Correct." / "Not quite." / "No." Then the reason in the learner's own terms,
the evidence, when it returns, and the resume cue (Kluger and DeNisi 1996;
Hattie and Timperley; Altmann and Trafton 2002). No praise, no warmth that
carries no information, no comparison with others (R14, R26, R27). *Rule:* every
graded message ends with "Back on <date>." and `Back to: <task>. Next: <step>.`

### 8. An honest record that can go down

The record shows what the learner can do without the agent, per dimension, and
it drops when a review is missed. No streaks, no points, no totals that only go
up, no percent bars (Silverman and Barasch 2023; Deci, Koestner and Ryan 1999;
Matuschak on Execute Program; R32, R34 to R36). Support fades as the level rises
(Kalyuga 2007; R15). *Rule:* best level as an outline, latest as the fill; the
only number on the Inbox is the due count; the only "levels" are the record
levels.

---

## 2. Journeys

### 2.0 The example used in every journey

The learner, Sam, is building `orbit-pay`, a payments service, with Claude Code
in the Claude app. The session is a cloud session that Sam opens on the laptop
and on the phone. The repo is public, so the record lives in a private
`learning-record` repo (architecture 4.4). Dimensions in the record: Distributed
systems, Data and storage, Debugging and diagnosis, Correctness and testing,
Security, Reading code.

Each storyboard is a table. "Surface" is where the learner looks. "Agent and
system" is what the agent does (tool calls named as `lwb_*`) and what changes in
the store. Phase notes say what is different before and after an experiment
passes.

### 2.a Start a learning task in a build: the question, the answer, the build continues

Sam asks for retries in the payment worker. The topic `retry-budget` is at
"With help". Mode is Normal.

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Sam types: "Add retries with backoff to the charge call in the payment worker. Three attempts max." | Chat, laptop | Skill rule (P1) or `UserPromptSubmit` hook (P2) matches the prompt to topic `retry-budget`, level "With help". No card is open, rate rule allows one. |
| 2 | Nothing new yet. The agent's normal plan text: "I'll wrap `charge()` in a retry with exponential backoff and add `test_retry_budget`." | Chat | The agent writes the rubric first and calls `lwb_seal` (rubric as tool input, never in Bash). The transcript shows one collapsed line: `Card sealed · sha256 9c1e…`. Then `lwb_post` with `moment=before`, `mode=wait`. |
| 3 | The text card (layout in 3.1), sent together with "Starting the build now.": <br>`Question · retry-budget · before the build`<br>`Each attempt times out at 0.8 s and the backoff is 0.5 s, then 1 s. When test_retry_budget runs against a dead gateway, how long until charge() gives up?`<br>`billing/charge.py:41-58`<br>`Reply with your answer and how sure you are: guess, fairly sure or sure. Or "don't know" or "not now". Or answer in the Room: Open card` | Chat | The agent starts the edit at once. It does not wait for the answer. The card is in `open.json` and in the Room db as Now. |
| 4 | The agent's tool calls stream as usual (reads, edits). | Chat | Agent works. Card stays answerable. |
| 5 | Sam replies mid-build: "about 3.9 s, fairly sure". | Chat | Next turn boundary: the agent calls `lwb_lock` with the text and confidence. Replies in one line: "Locked. Shown after test_retry_budget runs." Then continues the build. |
| 6 | Build continues. The agent runs `pytest -k test_retry_budget`. | Chat | The observable ran. `lwb_reveal` (P1 skill rule; P2 `PostToolUse` hook injects "Reveal c_3f9c now."). |
| 7 | A Compare block in chat (layout in 3.1): <br>`You said: about 3.9 s (fairly sure)`<br>`It did: gave up at 4.1 s`<br>`Not quite. You added three timeouts and the two backoffs: 2.4 + 1.5 = 3.9 s. The test also waits for the jitter, up to 0.1 s per backoff. billing/retry.py:22.`<br>`Back on 10 Nov.`<br>`Back to: retries in the payment worker. Next: the cap on total retry time.` | Chat | `lwb_grade` writes the comparison. Prediction attempt type, no level change (D9). `consolidated` recorded. Review scheduled at 3 days. Room Now card moves to Done and leaves the inbox. |
| 8 | Build continues to the next step. | Chat | Rate rule: no new unprompted learning turn for 10 minutes. |

Branches:

- **Sam does not answer before the observable runs.** The agent holds the
  result summary (R2) and posts: "The test ran. Your prediction is still open.
  Answer now, or say 'show result'." "Show result" reveals and records
  `not_now`. In P1 this is a skill rule; in P3 the `PreToolUse` gate does it
  before the test runs instead ("Prediction c_3f9c is open. Ask it now or mark
  it not now, then rerun.").
- **Sam says "not now" or "just do it".** One line: "OK. Back to: retries in the
  payment worker. Next: the backoff loop." The card moves to Later. No more
  questions this session for this task. Time to next tool call under 5 s.
- **Sam asks "how does jitter work?"** The agent answers at once (principle 2),
  then repeats the open question in one line: "Your prediction is still open:
  how long until charge() gives up?"
- **Learner at "Not yet".** Instead of a prediction, the agent shows a worked
  example with labelled steps from this repo, then asks a completion question
  after the build (support table in architecture section 5).

### 2.b Step away mid-build, answer on the phone, return without friction

Same task, later. The build passed. The agent asked the explain-back and the
turn ended. Sam leaves the laptop.

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Last message in chat: the explain-back card: `Question · idempotency · after it works`<br>`Why can the worker retry charge() without charging the customer twice?`<br>`…Or answer in the Room: Open card` | Chat, laptop | `lwb_post moment=after`. Room db row written: Now, kind `explain`, rubric sealed outside the db. |
| 2 | P1: nothing on the phone until Sam opens it. P2 (E-PUSH passes): after the laptop is idle and a phone is attached, one passive push: "1 question about idempotency. About 1 minute." | Phone lock screen | Presence rule: no push while Sam is at the machine. One push per day maximum. |
| 3 | Sam opens the Claude app on the phone. Two ways in: the session itself (the card is the last chat message, and Sam can reply there), or the pinned Room. Sam opens the Room. Inbox: **Now** row "After: idempotency · About 1 min". | Room, phone | Room reads its db. Only the due count is a number on the page. |
| 4 | Card view. Reason line "After it works · idempotency". Prompt. Excerpt `billing/charge.py:41-58` in a scrollable mono block (collapsed by default on the phone for explain cards so the code does not do the thinking; "Show the code" opens it). Text field. Confidence radios. **Lock my answer** disabled until a confidence is chosen. | Room, phone | Card state `delivered(room)`. |
| 5 | Sam writes: "The idempotency key is the order id, so the gateway sees the same key and returns the first charge." Chooses **Sure**. Taps **Lock my answer**. Card moves up 8px. "Locked." | Room, phone | db row `locked`, `locked_at`, door `room-phone`. Then the page asks the server for the rubric doc (written only after a lock). |
| 6 | "Grading…" for 1 to 4 s, then the verdict: **Correct.** "The key is the order id (billing/charge.py:47), and the gateway returns the stored result for a repeated key. Back on 10 Nov." Then the record delta: a cell "Idempotency" lights from With help to Without help, one 400 ms fade. Then: "Saved. Claude adds this to your record on your next message." | Room, phone | `sample` grades on the page against the rubric [T]. Grade written to db as `graded_on_page`. |
| 7 | Sam puts the phone away. | | P2 (E-SEND): the Lock tap also calls `room.sendToClaudeSession`. The session wakes, imports, posts the grade to chat. P1: nothing until Sam's next message. |
| 8 | Back at the laptop, Sam types the next request: "Now add a dead letter queue for failed charges." | Chat, laptop | Pull rule: `open.json` lists a Room card, so the agent reads it with ArtifactData before replying. `learning.py import --from-room` (idempotent on card id), `learning.py check` verifies the seal. |
| 9 | The agent's reply starts with one line: "From the Room: idempotency, Correct, now Without help. Back on 10 Nov." Then it works on the dead letter queue. | Chat | One extra turn allowed by the phase 1 acceptance test; here it is folded into the reply, so zero extra turns. |

Branches:

- **Sam answered in both places** (chat on the phone and the Room). Earliest
  lock wins. Chat line: "You also answered in the Room at 14:02. I graded the
  first answer (chat, 14:01)."
- **The phone is offline.** The Lock tap saves on the page: "You are offline.
  Your answer is saved on this phone and sent when you are back online." The
  card shows state "Saved here, not sent". Retries on `online`.
- **The session is gone** (ended, archived). The Room grade stands. The next
  session imports it at `SessionStart`: "1 answer from the Room added: idempotency."

### 2.c The explain-back after it works

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Tests pass. The agent's turn summary is short and does not explain the mechanism: "Retries are in. test_retry_budget and test_idempotent_retry pass." | Chat | Skill rule (P1) or `Stop` hook (P2): tests passed, topic touched, no explain-back yet. Rubric sealed before asking (2 or 3 points). |
| 2 | The explain-back card. One specific question (R11): "Why can the worker retry charge() without charging twice?" | Chat | The turn ends with the question. The work is done, so nothing waits on it. |
| 3a | Correct: "Correct. The key is the order id and the gateway returns the stored result for a repeated key (billing/charge.py:47). Back on 10 Nov. Back to: retries in the payment worker. Next: the dead letter queue." | Chat | Level evidence: unaided correct at "With help" moves the topic to "Without help". |
| 3b | Partial: "Not quite. The key is what makes it safe, yes. But the key must be the order id, not a new UUID per attempt; a new UUID per attempt charges twice. billing/charge.py:47. Say it again in one line with that part, or say 'next'." | Chat | One restatement allowed (Exercism iteration pattern). The restatement is part of the same attempt. |
| 3c | Wrong: "No. The timeout does not make it safe. A timeout only means the reply did not arrive; the charge may have run. The key at billing/charge.py:47 is what stops a second charge. Back tomorrow." | Chat | Miss returns next day. |
| 3d | Confident and wrong (chose Sure): as 3c, plus one line: "You chose Sure. This one returns tomorrow and is marked on your map." | Chat | Map mark on the topic cell (small ring). |
| 4 | Resume cue in every case. | Chat | |
| 5 | If Sam wants the agent's explanation: "explain it" gives the full explanation after the grade. | Chat | Explanation after grading never changes the grade. |

### 2.d A review session days later

Five days later. Two reviews are due: `retry-budget` (3 days) and
`idempotency` (3 days). One is overdue by two days.

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | At the start of the next session, one line before anything else the agent says: "2 reviews due. About 3 minutes. Say 'review' or open the Room." | Chat | P1: skill rule runs `learning.py due --count`. P2: `SessionStart` hook. Shown once per session. |
| 2a | Sam ignores it and keeps building. Nothing else happens. | Chat | Line not repeated. |
| 2b | Or Sam opens the Room on the phone that evening. Inbox: **Due 2**. Rows: "Review: retry-budget · 3 days" and "Review: idempotency · 3 days, 2 days late". A button **Start review · 2**. | Room | P2 (E-SCHED): a daily cloud scheduled task wrote the cards and sent one push. |
| 3 | Review card 1. No code, no old answer, no old feedback on screen (R17). It is a new instance (R18): "A refund call now retries too. It uses a new UUID as its key on every attempt. What happens when the first attempt times out but the refund ran?" Confidence. Lock. | Room | Question varies by level: at Without help, apply to new code. |
| 4 | Verdict, then the reveal: only now the original answer and code are shown under "What you wrote on 7 Nov". Next date on the verdict: "Correct. Back on 28 Nov." (21 days). | Room | `reviews.jsonl` row (FSRS form: topic, ts, rating, confidence, door). |
| 5 | Card 2. Interleaved with a confusable topic if the record shows confusion (R19): "Which of these two makes the retry safe: the lease on the job, or the key on the charge?" | Room | |
| 6 | End of session: "Done. 2 reviewed. Next review on 14 Nov." The Map cell changes only if a level changed. "Back to the build" button if a session is linked. | Room | Weekly cell for today lights (no counter). |

Rules: at most 5 due cards shown per day; overflow line "3 more move to
tomorrow." A delayed self-judgment is asked once per topic at the 21-day review
only: "How well could you do this without the agent? Not yet / With help /
Without help." Stored as self-report, never counted toward a level (R25).

### 2.e "What am I weak at?" and the Map

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Sam types in chat: "what am I weak at?" | Chat | `lwb_map`. |
| 2 | A short text answer, three parts in this order (R30): <br>`Weakest: Debugging and diagnosis. 1 of 4 topics without help. timeouts-vs-failures was a sure miss on 9 Nov.`<br>`Changed since 7 Nov: idempotency is now Without help. retry-budget dropped from Without help to With help at its review.`<br>`Due: 2. Map: Open map`<br>Then an offer: "Want a drill on timeouts-vs-failures? About 10 minutes." | Chat | Text grid fallback available: "say 'show grid'". |
| 3 | Sam opens the Map. Top: the one gap card ("Weakest now"). Then the record grid: one row per dimension, three segments (With help, Without help, New situation) like the site, plus a row of topic cells under each row when expanded. Then "How sure vs how right": three bars. Then "Last 4 weeks": 28 faint cells. | Room, desktop or phone | `map.json` snapshot, no answers, no rubrics. |
| 4 | Sam taps the Debugging row. Topic cells with glyphs and outlines. `timeouts-vs-failures` cell: fill With help, outline ring Without help (best was higher), small mark "sure miss". | Room | |
| 5 | Sam taps the cell. Topic sheet: level history as a timeline (dated dots per attempt with the verdict word), next review date, the rubric commit times ("Answer fixed 14:15. You locked 14:22."), and two actions: **Review now** and **Drill this**. | Room | Answers in history are shown only after their review (no spoiler for a due card). |
| 6 | **Table view** toggle shows the same data as an HTML table: Dimension, Topic, Best, Latest, Last result, Next review. | Room | Accessibility alternative (A1). |

### 2.f A debugging drill

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Sam taps **Drill this** on `timeouts-vs-failures`, or says "drill me on timeouts". | Room or chat | The agent creates a scratch worktree, plants a bug from the project's own history (R15), seals the rubric (cause + a check that would confirm it, R16). |
| 2 | Drill card. "Symptom": a failing test output in mono, and one line of context: "A customer was charged twice after a gateway timeout. test_no_double_charge fails." No hint shown. Hint ladder control: "Hints used: 0 of 3". | Room or chat | `lwb_post kind=repair`. Code is in the worktree; the card links the file list. |
| 3 | Step 1: "What do you think causes it?" text field. Step 2: "What check would show it?" text field ("A log line, a test, a value to print"). Optional line picker: tap the line you suspect in the excerpt. Confidence. Lock. | Room | Two-part rubric. |
| 4 | Sam taps **Hint** once. H1: "Look at what the key is made from." Ladder shows 1 of 3 used. Each hint costs nothing in tone, but the record level for this attempt is capped at With help (R16). Copy under the ladder: "Using a hint is fine. This attempt then counts as With help." | Room | `lwb_hint(card)` records the hint level. |
| 5 | Verdict, two lines, one per rubric part: "Cause: Correct. The key is built from the attempt number (billing/charge.py:45)." "Check: Not quite. Printing the key shows it changes, but the test that proves it is two calls with one order id." | Room | Graded per part. |
| 6 | "Run your check" (only on surfaces with the session linked): the agent runs Sam's check, not its own (R14), and posts the output. Then: "Back on 10 Nov. The worktree is deleted when you close this drill." | Chat or Room | |

The drill offer during a real build (when a test fails in a learning task) is
lighter: one line, once per failing test: "test_no_double_charge fails. Call
the cause first? Pick the line, or say 'not now'." "Not now" means the agent
debugs and says nothing more about it.

### 2.g An explainer

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Sam: "explain PR 128" (or `/learn explain billing/`). | Chat | The agent builds an explainer artifact from `assets/explainer-template.html`, in the site language. Offered only at Not yet and With help; at New situation it offers a one-paragraph summary and a hard question instead (R29). |
| 2 | Chat line: "Explainer ready: How the retry path works. 6 minutes, 3 questions inside. Open explainer" | Chat | Published as a private artifact; also listed in Room Explainers. |
| 3 | The page. Title, a one-line "What this explains", a reading-time estimate, a diagram of the component path (site `.flow` style), then sections. Before each key section, an embedded question card: "Before you read on: the gateway times out after the charge ran. What does the worker do next?" The section below is dimmed and collapsed until the learner locks or presses "Show without answering". | Explainer artifact | Mnemonic medium (Orbit, Quantum Country). Embedded cards are real cards with seals. |
| 4 | After the lock, the section opens and the card shows the comparison inline. | Explainer | Prediction type; no level change (D9). |
| 5 | At the end: "3 questions from this page are in your reviews. First one on 10 Nov." | Explainer | Embedded explain cards enter the ladder. |

### 2.h First run and onboarding

No tour, no welcome modal (O1, pattern 7.3). First value is one real question on
Sam's own code.

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Sam installs the skill (site install line) and says "use learning while building on this project". | Chat | `learning.py init`. Privacy check: `gh repo view --json visibility`. |
| 2 | If the repo is public: "This repo is public. A record in it would be public too. I can keep your record in a private repo, learning-record. Create it? Reply 'yes' or 'keep it local'." | Chat | P2 (E-REPO) for the private repo. Until then: "keep it local" keeps it in local files and the Room db, never committed to the public repo. |
| 3 | Dimensions, prefilled from the repo, in one message (O2): "I'll track these areas. Change them now or later: Distributed systems, Data and storage, Debugging and diagnosis, Correctness and testing, Security, Reading code." | Chat | Detected from code: queues, SQL, auth. |
| 4 | Mode in one line: "Mode: Normal (one question before a build you choose to learn from, one after). Also: Quiet (reviews only), Deep (adds drills)." | Chat | `config.json`. |
| 5 | Nothing else. Sam's next real task is a learning task if it touches a tracked area, and the first question appears as in 2.a. | Chat | |
| 6 | After the first answer is graded, once and never again (O3): "To see waiting questions, say /learn. To stop questions for now, say not now. Your Room: Open Room" | Chat | Room artifact published, private. Offer to pin once. |
| 7 | First visit to the Room: Inbox empty state with the faint grid behind it (E1); Map shows the six dimensions with unlit cells and "Your record is empty. It fills when you answer questions about this project." | Room | No fake data. |

### 2.i A missed or skipped question

| Case | Learner sees | Surface | System |
|---|---|---|---|
| Not now on a build question | "OK. Back to: <task>. Next: <step>." | Chat | Card to Later. No more questions this session for this task. |
| Not now on a Room card | Card leaves Now. Toast in the Room's action bar: "Moved to Later." with **Undo** (8 s, also reachable by keyboard; no timer on anything else). | Room | Snooze never counts as a miss (I2). |
| Snooze to a time | "Not now" menu: **After this build**, **Tomorrow**, **Next week**. | Room | |
| Never seen (session ended) | Nothing. After 7 days the card is removed from Later with no message. | | `skipped`, no penalty. |
| I do not know | Verdict: "Not known yet. This is the answer: <one or two lines>. Back tomorrow." | Any | Locks as a real answer at Guess; graded as a miss for scheduling, no tone of failure. |
| Miss at review | "No. <reason, evidence>. Back tomorrow." Map: fill drops one level, best stays as the outline. | Any | Miss returns next day, then 3 days. |
| Away three weeks | Inbox: "Due 5". Line under it: "9 more over the next 4 days." No "welcome back", no "you missed". | Room | Cap 5 per day, overflow spread (I4). |
| Three ignored pushes (P2) | No more pushes. One inbox line: "Reminders are off. They come back when you turn them on in Settings or say /learn." | Room | Nudge ledger in `config.json` (N3). |
| Pause | Settings: **Pause reviews for a week**. Inbox shows "Reviews paused until 14 Nov. Resume" | Room | Due dates shift by the pause; nothing is lost. |

### 2.j Ending a project and seeing growth

| # | Learner sees | Surface | Agent and system |
|---|---|---|---|
| 1 | Sam: "this project is done" or `/learn wrap`. | Chat | `lwb_map` plus history. |
| 2 | Chat summary, five lines: <br>`orbit-pay, 7 Oct to 7 Nov. 31 questions, 9 topics.`<br>`Without help or better: 6 topics (was 0). New situation: 2 (idempotency, outbox).`<br>`How sure vs how right: at Sure you were right 9 of 11 times (was 4 of 7).`<br>`Still weakest: Debugging and diagnosis, timeouts-vs-failures.`<br>`Growth page: Open`<br>Then: "Reviews continue after the project. The last one is on 6 May. Keep them, or stop them for this project?" | Chat | |
| 3 | Growth view in the Room (Map, "Project" toggle): two record panels side by side, "Start (7 Oct)" and "Now (7 Nov)", same grid. Below: a timeline of the month: one track per dimension, dots at each graded answer, filled by level, and labels at level changes ("idempotency: Without help, 14 Oct"). Below: calibration then vs now. Below: "Evidence of your own work": commits and tests marked as unaided (P5). | Room | Every number links to its attempts. Numbers can be lower at the end than in the middle, and the page says so when it happens: "retry-budget was Without help on 20 Oct. It is With help now." |
| 4 | **Export** button: a Markdown and JSON copy of the record for this project. | Room | `downloads` capability. |

No certificate, no celebration animation. The record lighting is the whole
celebration (pattern 5.3).

---

## 3. Surfaces, states and copy

### 3.0 The shared state set

Every surface handles the states below. Not every state applies to every
surface; tables mark "n/a". The state word in bold is what a learner sees as the
card's state chip where one is shown.

| State | Meaning | State chip |
|---|---|---|
| empty | Nothing to show yet. | (none) |
| loading | The page or data is being fetched. | (none) |
| waiting | A card is delivered and open. No answer yet. | **Open** |
| answered | Locked. Not graded yet (prediction waits for the observable; explain waits for the grader or the session). | **Locked** |
| graded right | "Correct." | **Correct** |
| partial | "Not quite." | **Not quite** |
| wrong | "No." | **No** |
| confident and wrong | "No." at Sure. | **No · sure** |
| offline | No network. Local actions still work. | **Saved here** |
| error | Something failed. Say what, and what still works. | (none) |

Also handled: **dont_know**, **not_now**, **skipped**, **also_answered**, **held
result**, **paused**.

Copy rules for every state: plain words, one idea per sentence, no praise, no
exclamation marks, no em dashes, no "Oops", no "Great", no "Awesome", no mascot,
no loss framing. Errors say what happened and what still works.

### 3.1 Chat text card (build surface; also the terminal and push bodies)

Purpose: the card at the machine, in every harness. Plain text, so it works in
Claude Code (cloud and local, desktop and phone), Codex, Cursor and a terminal.

Layout (fixed parts, always this order):

```
Question · <topic> · <moment words>
<prompt, one or two sentences>
<path:line range>
Reply with your answer and how sure you are: guess, fairly sure or sure.
Or "don't know" or "not now". Or answer in the Room: Open card
```

Moment words: "before the build", "after it works", "review, 21 days",
"drill", "while I build" (wait mode).

| State | Exact copy |
|---|---|
| waiting | the card above, sent with "Starting the build now." for wait-mode predictions |
| answered (prediction) | "Locked. Shown after test_retry_budget runs." |
| answered (Room, P1) | on the next message: "From the Room: <topic>, <verdict word>. Back on <date>." |
| graded right | "Correct. <one sentence: what holds, with path:line>. Back on <date>.\nBack to: <task>. Next: <step>." |
| partial | "Not quite. <what holds>. <what is missing, with path:line>. Say it again in one line with that part, or say 'next'.\nBack to: …" |
| wrong | "No. <which inference fails>. <evidence path:line>. Back tomorrow.\nBack to: …" |
| confident and wrong | wrong copy, plus before "Back to": "You chose Sure. This one returns tomorrow and is marked on your map." |
| dont_know | "Not known yet. This is the answer: <one or two lines, path:line>. Back tomorrow.\nBack to: …" |
| not_now | "OK. Back to: <task>. Next: <step>." |
| held result | "The test ran. Your prediction is still open. Answer now, or say 'show result'." |
| also_answered | "You also answered in the Room at 14:02. I graded the first answer (chat, 14:01)." |
| Compare (prediction) | "You said: <answer> (<confidence>)\nIt did: <observed, quoted from output>\n<verdict word> <one sentence on the gap with path:line>.\nBack on <date>.\nBack to: …" |
| offline | n/a (chat is the session) |
| error: seal failed | "I could not fix the answer before asking, so I will not ask this one. Back to: <task>." |
| error: Room unreachable | "The Room did not answer. Answer here instead, or later. Nothing is lost." |
| error: seal mismatch on import | "An answer from the Room did not match its sealed card, so I did not add it. It is in learning/rejected.log." |
| session start line | "2 reviews due. About 3 minutes. Say 'review' or open the Room." / with Room answers: "1 answer from the Room added: idempotency, Correct." |
| first-run commands (once) | "To see waiting questions, say /learn. To stop questions for now, say not now. Your Room: Open Room" |

Terminal (`learning.py answer`): same text, then prompts `Answer:`, then
`How sure? [1] guess  [2] fairly sure  [3] sure  [d] don't know  [n] not now`.

### 3.2 Room shell

Top bar (56px): left "Room" wordmark in Instrument Sans 650 and the project
name in mono; right the learner's initial (opens Settings). Tab bar: on the
desktop under the top bar, left aligned, `.tab` style; on the phone fixed at the
bottom, 64px with safe-area padding, four equal items, icon plus label.
Content max width 640px (Inbox, Card, Drill), 960px (Map). Grain over the page
as on the site. Linked session line, when the session is known: "Linked to:
orbit-pay · cloud session" with **Back to the build** (opens the session).

| State | Exact copy |
|---|---|
| loading | Skeleton: three faint rows at #ECE9E1, no spinner; `aria-busy="true"`; screen reader text "Loading your Room." |
| offline | Banner at top, ink text on #FFFFFF, 1.5px border: "You are offline. Answers are saved on this device and sent when you are back online." |
| error: db unreachable | "The Room cannot reach its data. Your answers in chat still work. Try again" |
| error: no permission | "This Room belongs to another account. Open your own Room from the chat." |
| paused | Line under the top bar: "Reviews paused until 14 Nov. Resume" |

### 3.3 Inbox

Purpose: what is waiting, in three groups (I1): **Now** (at most 1), **Due**
(at most 5 shown), **Later**. Each row: reason (four words or fewer, H3), topic
in mono, cost ("About 1 min"), state chip. The only number on the page is the
due count. Keys: J and K move, Enter opens, H "Not now", G then M map.

| State | Exact copy |
|---|---|
| empty, first run | Heading "Inbox". Body: "Questions appear here before and after a build. Start a task you want to learn from, and the agent asks one." Button: **Ask me one now** |
| empty, later | "Nothing is due. The next review is on 14 Nov." Secondary: **Review something now** |
| loading | skeleton rows |
| waiting | Now row: "After: idempotency · About 1 min · Open". Due group header "Due · 2". Row: "Review: retry-budget · 3 days". Overdue row adds ", 2 days late" (ink, never red). Button **Start review · 2** |
| answered | Row stays with chip **Locked** and line "Grading…" or for predictions "Shown after the test runs." |
| graded right / partial / wrong | Row leaves the inbox after 2 s with a fade (none under reduced motion). Toast: "Correct. Back on 10 Nov." / "Not quite. Back on 8 Nov." / "No. Back tomorrow." with **Open** |
| confident and wrong | Toast: "No. You chose Sure. Back tomorrow." |
| overflow | Under Due: "3 more move to tomorrow." |
| Later group | Row: "Later: outbox ordering · Not now on 6 Nov". Items older than 7 days drop off silently. |
| offline | Rows answered offline show chip **Saved here** and line "Sent when you are back online." |
| error: one card failed to load | Row: "This question did not load. It is still in your record. Try again" |
| also_answered | Row line: "Answered in chat at 14:01." |

### 3.4 Card (question)

Purpose: one question, answered without help on screen. Kinds: predict,
explain, review, transfer, diagnose (repair has its own view, 3.6). Answer
shapes: text, choice, line-pick, order.

Anatomy, top to bottom: reason line (eyebrow, #C2410C, 13px), topic and level in
mono ("idempotency · With help"), prompt (`.qq`, 24px desktop, 20px phone),
excerpt block with `path:line` header (hidden behind **Show the code** for
explain and review cards; shown for predict and line-pick), answer control,
confidence fieldset, actions, action bar with key caps.

Answer controls:
- text: textarea, 4 rows, label "Your answer", placeholder none. Character
  counter not shown.
- choice: `.opt` rows with letter keys A to D, plus "Other" which opens a text
  field.
- line-pick: the excerpt becomes a listbox of lines; selected line highlighted
  with `rgba(232,84,30,.16)` and a left ink bar; label "Tap the line".
- order: a list with move up and move down buttons on each item (no drag
  only); label "Put these in order".

Confidence fieldset: legend "How sure are you?"; radios **Guess** ("I would
not bet on it"), **Fairly sure** ("More likely right than wrong"), **Sure** ("I
would be surprised to be wrong"); keys 1 2 3. Separate button: **I do not
know** (key D).

Actions: primary **Lock my answer** (Cmd or Ctrl Enter), secondary **Not now**
(H), tertiary text button **Hint** (only at With help and on drills; at Without
help shown as "Hint" under a "More" menu; never at New situation).

Under the actions, one quiet line: "A wrong guess here costs nothing." on
predict cards only (R9).

| State | Exact copy and behaviour |
|---|---|
| empty | n/a (a card always has content) |
| loading | Prompt skeleton; "Loading the question." for screen readers |
| waiting | As above. Lock disabled with helper text "Choose how sure you are first." until confidence or I do not know |
| answered (prediction) | Controls become read only. Line: "Locked. Shown after the test runs." Your answer and confidence shown as a quoted block "You said". |
| answered (explain, grading on page) | "Locked." then "Grading…" (`aria-live=polite`) |
| answered (explain, grading by session, P1) | "Saved. Claude adds it to your record on your next message." |
| graded right | Verdict block (3.5) with "Correct." |
| partial | Verdict with "Not quite." and a **Say it again** text field, one use, label "Your answer, with the missing part" |
| wrong | Verdict with "No." |
| confident and wrong | Verdict with "No." plus the belief line: "You chose Sure. This is the kind of error that is easiest to fix when you see the reason. It returns tomorrow." |
| dont_know | Verdict "Not known yet." plus the answer. No red, no "No." |
| not_now | Card closes to Inbox. Toast "Moved to Later. Undo" |
| offline | Lock works. Chip **Saved here**. Line "You are offline. Your answer is saved on this phone and sent when you are back online." |
| error: rubric not available after lock | "Locked. The grader cannot reach the answer key right now. Claude grades it on your next message." |
| error: card already locked elsewhere | "This question was answered in chat at 14:01. Open the result" |
| error: grader failed | "Locked. Grading failed. Try again, or Claude grades it on your next message." |
| hint ladder | "Hints used: 1 of 3". After first hint: "This attempt now counts as With help." |

Phone: the action bar sits above the tab bar, sticky; Lock is full width; Not
now and I do not know are a row of two pills above it.

### 3.5 Verdict and Compare

Purpose: the consolidation step. For predictions, Compare is required; for
other kinds the verdict stands alone with the answer revealed below.

Compare: two columns on desktop, stacked on the phone. Left "You said" (the
learner's words, quoted, with confidence chip). Right "It did" (the observed
output in mono, quoted from the test or log, with its command). Below both: the
verdict word, one sentence on the gap, evidence link `path:line`, next date,
record delta row (the site's `.delta` pattern), resume cue, **Back to the
build** button.

| State | Exact copy |
|---|---|
| empty | n/a |
| loading | "Waiting for the test output." (prediction locked, observable not run yet) |
| waiting | n/a |
| answered | "Locked. Shown after the test runs." |
| graded right | **Correct.** "<what holds, path:line>." "Back on 28 Nov." |
| partial | **Not quite.** "<what holds>. <what is missing>." "Back on 10 Nov." |
| wrong | **No.** "<inference that fails>. <evidence>." "Back tomorrow." |
| confident and wrong | **No.** + "You chose Sure. It returns tomorrow and is marked on your map." |
| prediction compared | Predictions use the same three words ("Correct.", "Not quite.", "No."), applied to the prediction, plus the line "Predictions do not change your record. The gap is what you learn from." |
| record delta | "Your record: idempotency  With help → Without help" with the cell lighting. Arrow is a drawn SVG chevron, not a character. Down: "retry-budget  Without help → With help" with no colour change beyond the fill, no red. |
| offline | "Saved here. The result is shown when you are back online." |
| error: output missing | "The test ran, but I could not read its output. Your prediction stays locked. Claude shows the result in chat." |

Verdict word colours: "Correct." ink #16161A; "Not quite." and "No." #C2410C
(the site's `.verdict`). The verdict is never colour only: the word carries it.

### 3.6 Drill

Purpose: debugging with the hypothesis before the diagnosis. Steps: Symptom,
Cause, Check, Reveal.

| State | Exact copy |
|---|---|
| empty | Drills tab: "No drills yet. Drills use bugs from this project. Ask for one from a topic on your map, or say 'drill me' in chat." |
| loading | "Setting up a safe copy of the code. About 20 seconds." |
| waiting | Symptom block. "What do you think causes it?" "What check would show it? A log line, a test or a value to print." |
| answered | "Locked. Grading…" |
| graded right | "Cause: Correct. <path:line>." "Check: Correct. <why it proves it>." |
| partial | One of the two parts "Not quite." with the missing part |
| wrong | "Cause: No. <evidence>." |
| confident and wrong | adds "You chose Sure. It returns tomorrow." |
| hint ladder | "Hints used: 0 of 3" / H1, H2, H3 texts revealed one at a time; "This attempt now counts as With help." |
| run check | "Run my check" (session linked only) / result "Your check printed: <output>." |
| offline | "You are offline. You can write your answer. Grading waits until you are back online." |
| error: worktree failed | "I could not make a safe copy of the code, so this drill did not start. Your code is unchanged." |
| done | "Back on 10 Nov. The safe copy is deleted when you close this drill." |

### 3.7 Map

Purpose: what Sam can do without the agent, with decay visible, and calibration.
Order (R30): Weakest now, Changed since <date>, Due, then the grid, then
calibration, then the last 4 weeks. A **Grid / Table** toggle (the site's
`.toggle`). A **This project / All projects** toggle. A **Growth** view for
journey j.

| State | Exact copy |
|---|---|
| empty | Grid with all dimensions and unlit cells. "Your record is empty. It fills when you answer questions about this project." Button: **Change areas** |
| dimension with no topics | Row label + "No topics yet. The agent adds one when a change touches this area." |
| loading | Grid skeleton with unlit cells (the same as empty but with `aria-busy`) |
| normal | Weakest card: "Weakest now: Debugging and diagnosis. timeouts-vs-failures was a sure miss on 9 Nov." Buttons **Review now** **Drill this**. Changed: "Since 7 Nov: idempotency is Without help. retry-budget is With help (was Without help)." Count line at the foot (site `.count`): "6 of 9 topics without help" |
| calibration | Heading "How sure vs how right". Three bars: "Guess: right 2 of 6", "Fairly sure: right 5 of 8", "Sure: right 9 of 11". Note: "If you are well calibrated, Sure is right almost every time." Shown only after 10 answers with confidence: "Shown after 10 answers. You have 4." |
| last 4 weeks | 28 cells, lit on days with a review or answer. No number, no "broken" state. Caption: "Days with practice, last 4 weeks." |
| topic sheet | "idempotency · Distributed systems". "Best: Without help. Now: Without help." "Next review: 28 Nov." "Answer fixed 14:15. You locked 14:22." Timeline of attempts. |
| decay | Cell with outline ring at best and fill at latest; accessible name "retry-budget: now With help, best Without help". |
| offline | "Showing your map from 14:20. It updates when you are back online." |
| error | "The map did not load. Your record is safe in learning-record. Try again" |

### 3.8 Explainer page

Purpose: a page that explains a change, with questions before the reveal.
Built on request; separate artifact; same design system.

| State | Exact copy |
|---|---|
| empty (Explainers tab) | "No explainers yet. Ask in chat: 'explain PR 128'." Button **Copy the prompt** |
| loading | "Building the explainer. About a minute." (in chat) |
| waiting (embedded card) | "Before you read on: <question>." Section below dimmed and collapsed. Buttons **Lock my answer**, **Show without answering** |
| answered | "Locked." Section opens. Compare inline. |
| graded right / partial / wrong / confident and wrong | as 3.5, compact |
| show without answering | Section opens. Line: "Not answered. This question is not added to your reviews." |
| end | "3 questions from this page are in your reviews. First one on 10 Nov." |
| level at New situation | Not built. Chat: "You know this area well. Here is a one-paragraph summary and a harder question instead." |
| offline | Page works (static). Locks saved: "Saved here." |
| error | "This explainer is out of date: the code changed after it was built. Rebuild" |

### 3.9 Settings

| Control | Copy |
|---|---|
| Mode | "Mode". Radios: **Quiet** "Reviews only. No questions during builds." **Normal** "One question before a build you choose to learn from, one after." **Deep** "Normal, plus drills and a question at each build step." |
| Pause | **Pause reviews for a week**. When paused: "Paused until 14 Nov. Resume" |
| Reminders (P2) | "Phone reminders". Toggle. "At most one a day, at a time you choose. Never while you are at your computer." Time picker. |
| How sure to be (FSRS target, later) | "How sure do you want to be that you can still do this? Most of the time / Almost always". Note: "Almost always means more reviews." |
| Areas | List of dimensions, add and remove. |
| Record location | "Your record is in: 0xfauzi/learning-record (private)." or "local files only". |
| Privacy note | "Answer keys are sealed before each question. You can read your own Room data, so the Room cannot stop you from looking. The record shows when each key was fixed and when you locked." |
| Export | **Download my record** |
| States | loading skeleton; saved: "Saved."; error: "Not saved. Try again." |

### 3.10 Onboarding (first run)

Chat copy is in 2.h. Room first-run states:

| State | Exact copy |
|---|---|
| Room first open | Top: "This is your Room. Questions wait here, and your map shows what you can do without the agent." Below: the empty Inbox and a faint map. One button: **Ask me one now** |
| privacy choice pending | "Where should your record live? This project is public." **Private repo (learning-record)** / **This device only** |
| areas | "Areas to track. Detected from your code." chips, each removable, **Add an area** |
| done | Nothing; the first-open text does not show again. |

### 3.11 Growth (project end)

Part of Map, view "Growth".

| State | Exact copy |
|---|---|
| empty | "Growth shows after two weeks of answers on this project." |
| normal | "orbit-pay · 7 Oct to 7 Nov". Panels "Start" and "Now". Timeline with level-change labels. Calibration then and now. "Evidence of your own work: 4 commits and 2 tests you wrote without the agent." |
| a drop | "retry-budget was Without help on 20 Oct. It is With help now." |
| reviews after the project | "Reviews continue for this project until 6 May. Keep them / Stop them" |
| export | **Download this project's record** |

### 3.12 Push and badge (P2, P3)

| State | Exact copy |
|---|---|
| one card | "1 question about idempotency. About 1 minute." Action: **Pause reviews** |
| reviews | "2 reviews due. About 3 minutes." |
| graded on page (P2 bell) | none to the phone; the session posts in chat |
| after 3 ignored | no push; inbox line in 2.i |
| badge | `setAppBadge(dueCount)` where supported; cleared at 0. No badge for Later. |

Push bodies never hold code, answers or rubric text.

### 3.13 Mod band and pane (P3, local desktop only)

Band above the prompt, mono 12px: "1 question · press 1" / "2 due" / nothing
when empty. Pane: the same Card, Compare and Map components as the Room, same
copy. Offline and error states as the Room. Shown here only to say the
components must be portable; it is not prototyped.

---

## 4. Design system

### 4.1 Tokens

Taken from `docs/assets/site.css`. Names are new; values are the site's, except
where marked.

```css
:root{
  /* surfaces */
  --paper:#F5F4F0; --card:#FFFFFF; --field:#ECE9E1; --rule:#EFEDE6; --border:#DAD8D0;
  /* ink and text */
  --ink:#16161A; --text-2:#45454D; --text-3:#5F5F68; --text-4:#6E6E77; --text-dim:#7A7A83;
  /* accent */
  --accent:#E8541E;          /* fills, focus ring, live edge; never body text */
  --accent-text:#C2410C;     /* text-safe accent, 4.71:1 on paper */
  --accent-wash:rgba(232,84,30,.16);
  /* record ramp */
  --lv1:#F6C9AF;  /* With help */
  --lv2:#EE8B5B;  /* Without help (recalls) */
  --lv3:#C2410C;  /* New situation (transfers) */
  --lv0:#EFEDE6;  /* Not yet */
  --control-border:#7A7A83;  /* changed from #8E8E96 (D8) */
  /* type */
  --sans:"Instrument Sans",system-ui,sans-serif; --mono:"JetBrains Mono",ui-monospace,monospace;
  /* radii */
  --r-cell:3px; --r-sm:10px; --r-md:14px; --r-lg:18px; --r-pill:999px;
  /* motion */
  --ease-out:cubic-bezier(.2,.7,.2,1); --ease-spring:cubic-bezier(.3,1.6,.5,1);
}
```

Dark mode (new; artifact contract requires it). Paper and ink swap; the ramp is
kept. Measured in this session [T]:

```css
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){ /* same block under :root[data-theme="dark"] */
  --paper:#141417; --card:#1D1D21; --field:#26262B; --rule:#2A2A30; --border:#3A3A40;
  --ink:#F2F1EC; --text-2:#B4B3AE; --text-3:#9A9AA2; --text-4:#9A9AA2; --text-dim:#8A8A92;
  --accent-text:#F07A4A;     /* 6.64:1 on #141417, 6.07:1 on #1D1D21 */
  --control-border:#8A8A92;
}}
```

Grain in dark mode: the same `grain.png` with `mix-blend-mode:screen` at opacity
.08. `--lv3` on dark is 3.55:1 on paper and 3.24:1 on card: passes 3:1.

Type scale:

| Role | Desktop | Phone | Weight and settings |
|---|---|---|---|
| Page title | 46px / 1.06 | 31px | 650, wdth 88, -0.02em |
| Section title | 24px / 1.3 | 20px | 650, wdth 88 |
| Prompt (`.qq`) | 24px / 1.3 | 20px | 600, -0.01em |
| Body | 17px / 1.6 | 16px | 400, `--text-2` |
| Small | 14px / 1.6 | 14px | `--text-3` |
| Eyebrow / reason | 13px | 13px | 500, `--accent-text` |
| Verdict | 26px | 22px | 700 |
| Mono (code, ids, paths, keys) | 13px / 1.8 | 12.5px | JetBrains Mono 500 |

Spacing: 4px base. Steps 4, 8, 12, 16, 24, 32, 48, 72. Card padding 24px (16px
on phone). Side gutter 32px desktop, 16px at 375px. No horizontal scroll at
375px; code blocks scroll inside themselves.

### 4.2 Components

Each component lists anatomy, sizes, states and semantics.

**Record segments (dimension row).** The site's `.row`: name, three `.seg`
cells (With help, Without help, New situation), level word on the right. Each
filled segment: fill from the ramp, plus `box-shadow: inset 0 0 0 1.5px
var(--ink)` (D7). Height 14px, radius 3px, gap 4px. Semantics: the row is a
`li` with text "Debugging and diagnosis: Without help"; segments are
`aria-hidden`. Lit animation: 550ms background and scaleY(1.15) (site), off
under reduced motion.

**Record cell (topic).** 28 by 28px square (44 by 44px hit area via padding),
radius 6px. Fill = latest level. Outline ring 2px offset 2px in ink = best
level when best is higher than latest. Glyph: 1, 2 or 3 short vertical bars in
ink (on `--lv3` the bars are `--paper`) at the bottom left, 2px wide; none for
Not yet. Mark for a sure miss: a 6px ink dot at top right. A `button` with
accessible name "<topic>: now <level>, best <level>, <mark>". Grid is a `role
="grid"`-free list of buttons grouped by dimension `h3`; the table view is the
semantic alternative.

**Question card.** `form` with `aria-labelledby` the prompt. Parts in 3.4.
White card, 1.5px `--border`, radius 18px (14px phone). The Now card has a 3px
left edge in `--accent` (the one live element).

**Confidence control.** `fieldset` with `legend` "How sure are you?"; three
radio inputs styled as `.sure` pills (min-height 44px); the meaning text is
visible under the selected pill and is the radio's `aria-describedby`. Keys 1 2
3. Selected: ink fill, paper text. "I do not know" is a separate `button`
styled as `.sure` with a dashed border, so it reads as a different kind of
choice.

**Verdict.** A `section` with `role="status"` `aria-live="polite"`; heading
`h2` holds the verdict word (focus moves to it after Lock when the grade is
immediate). Body: reason, evidence link (mono, underlined), next date, belief
line if confident and wrong, record delta, resume cue, Back button.

**Compare.** Two `figure` blocks with `figcaption` "You said" and "It did".
Desktop 2 columns, gap 24px; phone stacked. "It did" content in mono on
`--paper` inside the card.

**Hint ladder.** A row of three 10px-tall segments like record segments but in
ink outline only; used hints fill ink. Label "Hints used: 1 of 3". Button
**Hint** shows the next hint in a `details`-like block. Each hint is a list
item, numbered H1 to H3 in mono. Announces "Hint 1 of 3 shown."

**Inbox item.** A `li` containing one `a` (whole row is the target, min-height
64px): reason (eyebrow), topic (mono), cost and state chip on the right. Focus
ring 2px accent offset 3px. J and K move focus between rows (roving tabindex in
the list).

**State chip.** Pill, 24px tall (inside a 44px row), 12px mono, 1.5px border.
Open: ink border. Locked: ink fill. Correct: ink border with tick glyph. Not
quite and No: `--accent-text` border and text. Saved here: dashed border.

**Map row.** Dimension name, three segments, level word, expand button (44px)
that reveals the topic cells. `aria-expanded`.

**Timeline.** Horizontal on desktop (one track per dimension, dates on a mono
axis), vertical on the phone (one list per dimension). Dots 10px: filled with
the level reached in that attempt, ink outline; a sure miss is a hollow dot with
a ring. Level changes get a text label. Semantics: an ordered list per
dimension with dated items; the drawn track is `aria-hidden`.

**Calibration bars.** Three horizontal bars, track `--field`, fill ink, labels
in text with the fraction ("right 9 of 11"). Never a percentage alone.

**Week cells.** 28 cells 12px, lit `--lv2` with ink outline on days with
practice. `aria-label` on the group: "Practice on 9 of the last 28 days."
(This is the one place a count appears, only for screen readers, because the
visual has no number.)

**Action bar (key caps).** Bottom of every card: left the reason, right the
actions with key caps (mono 12px, 1.5px border, radius 6px, 22px tall). Key
caps are hidden on touch devices (`@media (hover:none)`).

**Toast.** Bottom of the content, white card, ink text, one line plus one
action. Stays 8s, pauses on hover and focus, dismissable, `role="status"`.

**Buttons.** Site `.btn` (50px, pill, ink fill; hover accent with ink text),
`.btn.ghost`. Phone primary: full width. Minimum 44 by 44px everywhere.

**Text field.** White, 1.5px `--control-border`, radius 14px, 16px text (no
iOS zoom), focus ring accent.

**Code excerpt.** Site `.code` with `.ln` line numbers, header line with
`path:line` in mono `--text-3`. Line-pick mode turns lines into options.

### 4.3 Motion

| What | Motion | Duration and easing | Reduced motion |
|---|---|---|---|
| Record cell lights after a grade | background fades from `--lv0` to the level; scaleY 1.15 then back | 400ms `--ease-out` (site uses 550ms for segments; keep 550 for rows) | instant colour change |
| Card on Lock | translateY(-8px) and back, controls fade to read only | 300ms `--ease-out` | none |
| Verdict arrives | opacity 0 to 1, translateY 10px to 0 (site `.reveal`) | 600ms `--ease-out` | appears |
| Inbox row leaves after grading | height and opacity to 0 | 250ms | removed |
| Page sections on first load | site `.rise` | 800ms | none |
| Background record field | site `.field` glow, Room first-run and empty states only | site timings | none |
| Anything else | no motion | | |

No celebration animation, no confetti, no sound, no looping motion near a
question.

### 4.4 Accessibility (WCAG 2.2 AA)

- **Contrast.** Body text `--text-2` 8.63:1; small text never lighter than
  `--text-4` (4.59:1 on paper). `--accent` never used for text. Control borders
  `--control-border` 3.86:1 (D8). Ramp cells carry outline and glyph (1.4.1,
  1.4.11).
- **Targets.** 44 by 44px minimum for every control on every surface (stricter
  than 2.5.8's 24px). Record cells have 44px hit areas.
- **Keyboard.** Every action has a visible button. Keys: J/K move, Enter open,
  1/2/3 confidence, D I do not know, H Not now, Cmd or Ctrl Enter lock, Esc
  back, G then M map, ? shows the key list. Keys work only when focus is not in
  a text field (except Cmd Enter and Esc). Focus order follows reading order.
  Focus is never trapped; the topic sheet is a `dialog` with focus return.
- **Focus visible.** 2px `--accent` outline, offset 3px (site rule). Not
  obscured by sticky bars (2.4.11): content gets scroll padding equal to the
  sticky bar heights.
- **Screen readers.** Verdict in a polite live region; focus moves to the
  verdict heading after Lock. Grading progress is announced once ("Grading."),
  not repeated. Cells and rows have text names with the level words. Every grid
  has a table view. Diagrams have a text description.
- **No timers.** No question has a time limit (2.2.1). The held result has a
  visible **Show result**. The Undo toast pauses on focus.
- **Reduced motion.** All motion in 4.3 off under `prefers-reduced-motion`.
- **Text resize and reflow.** Works at 320px width and 200% zoom without loss
  (1.4.10). No text in images.
- **Language.** Plain, one idea per sentence, `lang="en"`.
- **Redundant entry (3.3.7).** A partial answer's restatement field is
  prefilled with the learner's first answer.
- **Accessible authentication (3.3.8).** No login inside the Room beyond the
  claude.ai session.
- **Dark mode** at the same contrast rules, measured values in 4.1.

---

## 5. Prototype pages

Eight static pages in `design/learning-experience/prototypes/`, one per
surface, together covering journeys a to j. All share
`prototypes/proto.css` (the tokens and components in section 4) and
`prototypes/fixture.js` (the orbit-pay data below). Each page has a **state
switcher**: a fixed strip at the bottom-right, outside the product layout,
labelled "Prototype state", a `select` plus the `?state=` query parameter and
keys `[` and `]` to step through states. The switcher is visually distinct (mono,
dashed border) so that nobody mistakes it for product UI. Each page also has a
viewport toggle (375, 768, 1280) and a theme toggle (light, dark).

Shared fixture (`fixture.js`): project `orbit-pay`; learner Sam; 6 dimensions;
9 topics with best and latest levels (`idempotency` Without help,
`retry-budget` latest With help best Without help, `timeouts-vs-failures` With
help with a sure miss, `outbox` New situation, others); 31 attempts with dates
from 7 Oct to 7 Nov, verdicts and confidence; cards `c_3f9c` (predict,
retry-budget), `c_7a21` (explain, idempotency), `c_9b04` and `c_9b05` (reviews),
`c_d311` (repair drill); calibration counts (Guess 2 of 6, Fairly sure 5 of 8,
Sure 9 of 11); 28 days of practice flags; an explainer "How the retry path
works" with 3 embedded cards.

| File | Title | Purpose | Journeys |
|---|---|---|---|
| `prototypes/flow.html` | Build and learn flow | Two panes side by side: a Claude Code chat transcript (laptop) and the Room on a phone frame. Steps through journeys a, b and c with the text card, Locked, the held result, Compare in chat, the phone answer, and the "From the Room" line on the next message. Also shows phase 1 vs phase 2 (bell) as a toggle. | a, b, c, i |
| `prototypes/inbox.html` | Room inbox | The Room shell and Inbox with Now, Due, Later, the cap and overflow, toasts, pause, offline and errors. | b, d, i |
| `prototypes/card.html` | Question card | Every card kind and answer shape, the confidence control, I do not know, Not now, hint ladder, locked and grading states. | a, b, c, d |
| `prototypes/verdict.html` | Verdict and compare | Compare for predictions and the verdict for all kinds, every grade, the record delta (up and down), the resume cue. | a, c, d |
| `prototypes/map.html` | Map and growth | Weakest, changed, the record grid with outlines and glyphs, table view, topic sheet with timeline, calibration, week cells, and the Growth view for project end. | e, j |
| `prototypes/drill.html` | Debugging drill | Symptom, cause, check, hint ladder, two-part verdict, run my check, setup and failure states. | f |
| `prototypes/explainer.html` | Explainer | An explainer page with the flow diagram and embedded predict-before-reveal cards, show without answering, the end summary, stale state. | g |
| `prototypes/onboarding.html` | First run and settings | Chat onboarding messages, the Room first open, privacy choice, areas, and the Settings page with modes, pause and reminders. | h, i |

```json
[
  {
    "file": "prototypes/flow.html",
    "title": "Build and learn flow",
    "purpose": "Show the seamless move between building and learning: a Claude Code chat transcript on a laptop frame beside the Room on a phone frame, stepping through a prediction during a build, the reveal and Compare in chat, the explain-back answered on the phone, and the grade arriving in chat on the next message. A toggle shows phase 1 (pull on next message) and phase 2 (Submit rings the session). Uses fixture.js cards c_3f9c and c_7a21.",
    "states": ["waiting: prediction posted with Starting the build now", "answered: Locked, shown after the test runs", "held result: test ran, prediction still open, show result", "graded partial: Compare in chat with resume cue", "not now: OK, back to the build", "explain-back waiting in chat and in Room Now", "answered on phone: Locked, grading", "graded right on phone with record cell lighting", "next message: From the Room line in chat (phase 1)", "bell: grade posted with no extra turn (phase 2)", "also answered: earliest lock wins", "offline on phone: saved here", "error: Room unreachable, answer here instead"]
  },
  {
    "file": "prototypes/inbox.html",
    "title": "Room inbox",
    "purpose": "The Room shell (top bar, tab bar, linked session line) and the Inbox with its three groups Now, Due and Later, the due cap with overflow, toasts after grading, pause and away states. Uses fixture.js open cards, due reviews and later items.",
    "states": ["empty first run", "empty nothing due with next date", "loading skeleton", "waiting: Now plus 2 due", "answered: row locked, grading", "graded right toast", "graded partial toast", "graded wrong toast", "confident and wrong toast", "overflow: 5 due, 9 more over 4 days", "later items", "paused until date", "reminders off after 3 ignored", "offline: saved here rows", "error: card did not load", "error: db unreachable"]
  },
  {
    "file": "prototypes/card.html",
    "title": "Question card",
    "purpose": "One question card with every kind (predict, explain, review, transfer, diagnose) and answer shape (text, choice, line-pick, order), the confidence fieldset with meanings, I do not know, Not now, the hint ladder and the action bar with key caps, on desktop and phone. Uses fixture.js cards c_3f9c, c_7a21, c_9b04, c_9b05.",
    "states": ["loading", "waiting: lock disabled until confidence", "waiting: confidence chosen", "choice shape", "line-pick shape", "order shape", "hint 1 of 3 shown", "answered: prediction locked, shown after the test runs", "answered: explain locked, grading", "answered: saved, Claude adds it on your next message", "dont know", "not now with undo", "offline: saved here", "error: grader failed", "error: already answered in chat"]
  },
  {
    "file": "prototypes/verdict.html",
    "title": "Verdict and compare",
    "purpose": "The consolidation step: You said / It did for predictions and the verdict block for every kind, with reason, evidence link, next date, belief line, record delta up and down, resume cue and Back to the build. Uses fixture.js graded attempts.",
    "states": ["loading: waiting for the test output", "graded right", "graded partial with say it again", "graded wrong", "confident and wrong", "dont know: not known yet, this is the answer", "prediction compared: gap named, record unchanged", "record delta up with cell lighting", "record delta down (decay)", "offline: result shown when back online", "error: output missing"]
  },
  {
    "file": "prototypes/map.html",
    "title": "Map and growth",
    "purpose": "What the learner can do without the agent: weakest now, changed since, the record grid with ink outlines, glyphs and best-versus-latest rings, the table view, a topic sheet with its attempt timeline, calibration bars, week cells, and the Growth view for the end of a project. Uses fixture.js dimensions, topics, attempts, calibration and practice days.",
    "states": ["empty first run with faint grid", "loading", "normal grid", "table view", "dimension expanded with topic cells", "topic sheet with timeline", "decay: best ring above latest fill", "sure miss mark", "calibration hidden under 10 answers", "calibration shown", "growth: start vs now with timeline", "growth: a drop explained", "growth empty under two weeks", "offline: map from 14:20", "error: map did not load", "dark theme"]
  },
  {
    "file": "prototypes/drill.html",
    "title": "Debugging drill",
    "purpose": "A repair drill on a planted bug from the project: symptom, cause and check fields, optional line picker, the hint ladder that caps the attempt at With help, a two-part verdict, and Run my check. Uses fixture.js card c_d311.",
    "states": ["empty drills tab", "loading: setting up a safe copy", "waiting: symptom shown", "hint 1 of 3 used", "hint 3 of 3 used", "answered: locked, grading", "graded right on both parts", "graded partial: check not quite", "graded wrong: cause", "confident and wrong", "run my check output", "done: back on date, copy deleted", "offline: grading waits", "error: safe copy failed", "in-build offer: call the cause first"]
  },
  {
    "file": "prototypes/explainer.html",
    "title": "Explainer",
    "purpose": "An explainer page for a change in the site language: what it explains, reading time, the component flow diagram, sections gated by embedded predict-before-reveal cards that enter the review schedule. Uses fixture.js explainer How the retry path works.",
    "states": ["empty explainers tab", "loading: building the explainer", "waiting: embedded card, section collapsed", "answered: locked, section open with compare", "graded right inline", "graded wrong inline", "confident and wrong inline", "show without answering", "end summary: 3 questions in your reviews", "offline: saved here", "error: out of date, rebuild"]
  },
  {
    "file": "prototypes/onboarding.html",
    "title": "First run and settings",
    "purpose": "First run without a tour: the chat messages for init, the public repo privacy choice, prefilled areas and mode, the one-time commands line, the Room first open, and the Settings page with modes, pause, reminders, record location, privacy note and export. Uses fixture.js dimensions and config.",
    "states": ["chat: public repo privacy question", "chat: areas and mode", "chat: first-run commands line", "Room first open", "privacy choice pending", "areas editing", "settings normal", "settings paused", "settings reminders on", "settings saved", "settings error: not saved", "loading", "offline"]
  }
]
```
