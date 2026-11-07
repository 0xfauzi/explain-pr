# Critique: the learning scientist's lens

Reviewer stance: retrieval practice, generation, spacing, metacognition and
transfer (Bjork, Roediger, Metcalfe, Kapur). Question asked of every moment:
does it produce durable learning, and does the record tell the truth about it?

Read: `experience.md` (all), `architecture/recommended.md` sections 2, 5, 9,
`research/learning-science.md` sections 0 to 16, the skill's `SKILL.md` and
`scripts/record.py` (level and schedule rules), and every state of the eight
prototypes plus `index.html`. Pages were served locally and driven with
Playwright through all 224 prototype states at 1440 and 390 wide. No
horizontal scroll at 390 on any state. The only console error is a 404 for
`../../../docs/assets/grain.png`, which resolves only when the server root is
the repo root; serve from the repo root or copy the grain into the package.

## Verdict in one paragraph

The skeleton is sound and better than most products in this space: the
answer key is sealed before the question, confidence is part of the same
action, reviews hide the code and the old answer, decay is visible, there are
no streaks or praise, and predictions are kept out of level evidence (D9). The
problem is the record. As specified, the record will say "Without help" about
things the learner explained minutes after watching the agent write the code,
"New situation" about near copies of feedback they just read, and it will
credit a drill to a topic the drill did not test. Several cards also let the
learner recognise instead of recall: answer-bearing headings, choice options at
review, a 13-line excerpt with one odd line, and topic names printed on
transfer questions. The design measures friction carefully and learning not at
all. Fix the evidence rules first; the surfaces are mostly right.

---

## Blocker

### B1. An immediate explain-back raises the level to "Without help"

Where: `experience.md` 2.c row 3a ("unaided correct at With help moves the
topic to Without help"), 2.b row 6 ("lights from With help to Without help"),
`verdict.html` state 8 ("Without help for the first time"), `flow.html` state
8 and 9, and the `index.html` hero ("From the Room: idempotency, Correct, now
Without help").

What is wrong: the explain-back comes minutes after the agent wrote and ran
the code, often with the diff still in the chat transcript (`flow.html` state
9 shows `Edit billing/worker.py +9 -3` directly above the question). That
answer measures working memory and comprehension of a just-read solution, not
retrieval. Rhodes and Tauber (cited as R25 in the package's own research) is
the same effect from the judgment side: immediate performance and immediate
judgments are inflated by fluency. The Map promises "What you can do without
the agent" and "It goes down when you forget, so it stays true". The first
evidence that lights a cell is the least diagnostic one in the whole flow.

The package contradicts itself here, which is good evidence that the authors'
intuition was right in one place: the Map fixture in `map.html` (line 304)
records the 7 Oct explain-back correct as level 1 (With help), and
`scripts/record.py` already has `DURABLE_AFTER_DAYS = 7` ("A success counts as
durable only if it came at least this long after the topic was first
recorded"). The spec, the verdict prototype, the flow and the index ignore
both.

Fix: an explain-back in the same session is consolidation, not level
evidence. It can confirm "With help" at most. "Without help" needs an unaided
correct answer at a gap of 3 days or more (the first review). Change the
verdict copy to: "Correct. This counts when it holds at the first review on
10 Nov." The cell can show a faint pending state, not a fill.

---

## Major

### M1. The prediction targets arithmetic, then grades the learner on information it hid

Where: `experience.md` 2.a rows 3 and 7, `card.html` state 2, `verdict.html`
state 7, `flow.html` state 4.

The question gives two numbers and asks for a sum. The excerpt shown
(`billing/charge.py:41-53`) calls `backoff(attempt)` and never shows the
jitter, which lives in `billing/retry.py:22`. Sam's reasoning (3 x 0.8 + 0.5 +
1 = 3.9) is fully correct for what was shown. The verdict then says "Not
quite" and names "jitter, the part you left out" as the gap. This is
misleading feedback in Metcalfe's sense: it attributes the gap to the
learner's model when the cause is the question. The observable is also
non-deterministic (random jitter), so "It did 4.1 s" varies run to run. The
explainer (question 3) puts the jitter in the stem, so the same item has two
different correct answers across surfaces.

Deeper problem: the package's own section 3 says difficulty must be germane.
The germane idea in this task is not the sum; it is the misconception the
fixture already contains, `timeouts-vs-failures` ("A timeout means the
gateway rejected it", a sure miss). A prediction about that ("The gateway
charges the card but the reply is lost. What does test_retry_budget see on
attempt 2?") would test the mental model and let hypercorrection work.

Fix: add a question-quality rule to the card spec: (a) the prediction must be
answerable from what the card shows plus the concept, (b) the observable must
be deterministic, (c) the question targets the topic's known misconception
when there is one. Predictions get a "Compared" chip, not the verdict words,
which also keeps D9 honest.

### M2. Recognition where recall was intended

Four places hand the learner the answer or the candidate set:

1. **Explainer headings and diagram give away the predictions.**
   `explainer.html` state 3: the sidebar ("On this page") and section heading
   for question 1 read "A timeout is not a failure"; question 2 sits under
   "The key makes the retry safe"; question 3 under "The budget stops the
   loop". The animated diagram above question 1 shows "reply lost" and an
   "Attempt 2" toggle. Option C of question 3 is the longest and repeats the
   jitter clause from the stem. Each prediction is answerable from the page
   chrome. Fix: neutral headings until the lock ("1. When the reply is
   lost"), diagram placed after question 1, options of similar length.
2. **Choice options at review.** `card.html` state 4: the 3-day review of
   `retry-budget` is multiple choice (3.2, 3.5, 6.7, 10.7 s). R10 justified
   options for prequestions; reviews are retrieval (R17), and recognition
   produces weaker testing effects than recall (Roediger and Karpicke; Glover
   1989). Fix: free text or a numeric field at review; options only at Not
   yet, and only for predictions.
3. **The order shape tells the story.** `card.html` state 6: the 1-day review
   after a sure miss on `timeouts-vs-failures` lists six events, one of which
   is "The gateway returns the stored result. No second charge." The learner
   reconstructs a causal chain that is printed on the card, and the item that
   carries the misconception is stated as fact. Fix: after a sure miss, the
   next-day item asks the learner to generate the distinction (timeout versus
   decline, what the worker can know).
4. **Line-pick on a 13-line excerpt.** `card.html` state 5 and `drill.html`
   state 3: the excerpt contains exactly one unusual line
   (`idempotency_key=f"{order.id}:{attempt}"`), and the same 13 lines with
   `idempotency_key=order.id` were shown on the prediction card earlier. This
   is spot-the-difference. Localisation is the hardest part of debugging and
   the skill Shen and Tamkin found most eroded. Fix: write the hypothesis
   before any code is shown; then offer the file list or the whole module;
   line-pick only as a second step.

### M3. Topic names on transfer and drill cards remove the hard part of transfer

Where: `card.html` state 7 ("In new code · idempotency · Without help"),
`drill.html` all states ("Drill · ... timeouts-vs-failures"), Inbox rows
("Review: idempotency").

Far transfer fails mainly because people do not notice which principle
applies (Gick and Holyoak; Barnett and Ceci). Printing the topic id on a
transfer item tells the learner which principle to use, so a correct answer
is near transfer at best. Fix: for kinds `transfer`, `diagnosis`, `repair` and
interleaved reviews, the reason line shows the area only ("In new code ·
Distributed systems") and the topic appears after the lock. Inbox rows for
these kinds say "Review: a new case" with the area.

### M4. "New situation" is credited for near copies of the feedback

Where: `experience.md` 2.c row 3b feedback ("a new UUID per attempt charges
twice") and 2.d row 3, `card.html` state 7, `verdict.html` state 2. The
"transfer" question is "A refund call now retries too. It uses a new UUID as
its key on every attempt. What happens...?" That is the corrective feedback
from the explain-back, restated as a question. Answering it shows the learner
remembered the feedback, not that they can carry the idea to a new situation.
`record.py` counts any clean success of kind `transfer`, `diagnosis` or
`repair` as level 3, so this item would light the darkest cell.

`verdict.html` state 2 then shows the same answer as "No change. A level moves
when a review is right at a longer gap, or when you use the idea in a new
situation", a rule that exists nowhere in the spec or in `record.py`. The
learner is shown two different models of how the record works.

Fix: a transfer item must differ from every earlier item and feedback for the
topic in surface features (different domain object, different code shape,
different failure) while keeping the deep structure. The sealing step should
store the item's "distance" note in the rubric, and the grader should refuse
level 3 credit when the item quotes earlier feedback. Write one rule for level
moves and use the same sentence everywhere.

### M5. The drill credits the wrong topic and runs the check after the reveal

Where: `drill.html` states 3 and 7, `experience.md` 2.f.

The drill is filed under `timeouts-vs-failures`, but the planted bug is in
how the idempotency key is built. A correct answer says nothing about the
timeout-versus-failure misconception, yet state 7 moves `timeouts-vs-failures`
from With help to Without help ("record: with help -> recalls"). Under
`record.py`, a clean `repair` success is level 3, so the spec, the prototype
and the engine disagree about which cell lights and how far.

Second, "Run my check" comes after the two-part verdict and next to "Show the
fix". The hypothesis-test loop is the skill being trained (R14, R16). Running
the learner's check after the answer is revealed removes the loop. Fix: lock
the hypothesis and check, the agent runs the learner's check, the learner
sees the output and may revise the cause once, then the reveal. Credit the
topic the bug actually exercises.

### M6. "I do not know" is a one-tap exit from generation, with an equal-weight button

Where: `card.html` all waiting states (at 390 x 844 the first view of a
question shows "Not now" and "I do not know" as the two large pills, with the
answer field and confidence below the fold), the chat card copy ("Or 'don't
know' or 'not now'") on every card, `verdict.html` state 6.

Errorful generation followed by feedback beats being shown the answer, even
when the guess is wrong (Kornell, Hays and Bjork 2009; Potts and Shanks 2014),
and pretesting works through the attempt itself (Pan and Carpenter 2023, cited
in the package). A visible "I do not know" on every prediction invites the
learner to skip exactly the moment the research says is free learning. The
spec also disagrees with itself on what it does to calibration: 2.i says it
"locks as a real answer at Guess", `verdict.html` state 6 says it "counts as a
Guess for your reviews", while `map.html` `calib()` (line 310) excludes it.
Counting it as a Guess would push the Guess bar toward 0 and make the learner
look calibrated at Guess when they are not.

Fix: on predictions, "I do not know" first asks for a one-line best guess
("Write your best guess in a few words. It costs nothing."), with "Show the
answer" behind it. Keep it on reviews (an honest "I do not know" is valid
retrieval evidence). Never count it in calibration. Put the answer field above
the exits on the phone.

### M7. "Show the code" is free during an explain-back and does not cap the level

Where: `experience.md` 2.b row 4 and 3.4, `card.html` line 451 (a plain
`details` element; no hint is recorded).

The design rightly collapses the code on explain cards "so the code does not
do the thinking", but opening it costs nothing and is not recorded. An
explain-back answered with the code open is reading comprehension. Fix: opening
the code on explain, review and transfer cards is recorded as H1 (`lwb_hint`),
with the same line as the hint ladder ("This attempt now counts as With
help."). On predict cards the code stays visible, as now.

### M8. The restatement after "Not quite" grades copying

Where: `experience.md` 2.c row 3b, `verdict.html` state 3. The feedback gives
the missing part ("the key must be the order id, not a new UUID per
attempt"), then asks the learner to "say it again in one line with that part"
inside the same attempt. Repeating the feedback seconds later is not evidence
of anything. If it can lift the grade, it inflates; if it cannot, the spec
does not say so. Fix: the restatement is ungraded consolidation, stated on
the card ("Not graded. It helps it stick."), and the topic returns tomorrow,
as `record.py` already schedules a partial. The prototypes show "Back on 10
Nov." for this partial (3 days) while the Inbox toast says "Back on 8 Nov."
(next day); the engine says next day.

### M9. Calibration bars cannot be read as calibration

Where: `map.html` states 3 and 10, `experience.md` 3.7. Three bars with
"right 2 of 6", "5 of 8", "9 of 11" and the note "If you are well calibrated,
Sure is right almost every time." There is no reference mark for what each
level should hit, so the learner cannot see over- or under-confidence at
Guess or Fairly sure, which is half the signal. The confidence meanings ("I
would not bet on it", "More likely right than wrong", "I would be surprised to
be wrong") have no numbers, but R21 in the package recommends CBM-style
thresholds. With n of 6 to 11, the bars will swing on one answer.

Fix: give each level a target band on the bar (Guess under 1 in 2, Fairly
sure about 2 in 3, Sure 4 in 5 or better), say "Too few answers to tell" under
about 10 per level, and lead with the specific evidence that drives
hypercorrection: the list of sure misses and whether each has since been
answered right.

### M10. With help never asks the learner to build anything

Where: `experience.md` 2.a (Sam is at With help; the agent writes all of the
retry code) against `research/learning-science.md` section 10 and
`architecture/recommended.md` section 5, which both say With help means a
completion problem: "the agent writes all but the key piece; the learner
writes or describes it". No journey or prototype shows a completion problem.
Every generation act in the product is verbal (predict, explain, order,
pick). The Shen and Tamkin quiz measured code reading and debugging, and the
owner's goal is to come out a better engineer. Fix: at Not yet and With help,
in tasks the learner chose to learn from, the agent leaves one marked gap (the
key line or the test that proves it), the learner writes it, the tests grade
it. This is the strongest generation event available and it lives inside the
build, so it costs no extra interruption.

### M11. Every acceptance test measures friction; none measures learning

Where: `architecture/recommended.md` section 2 and the `index.html`
"What seamless means" band: zero copies, same state at three doors, Not now
under 5 s, resume in one line. The research file lists seven cheap
experiments (E1 to E7, section 16) and none is in a phase plan. A product can
pass all four seamless tests and teach nothing; learners will also rate the
effortful moments lower than they deserve (Bjork; Kornell), so any tuning by
feel will drift toward less learning.

Fix: add learning gates to each phase, computed from the record the product
already writes: first-review (3 day) unaided success rate on topics with and
without an explain-back; 21-day success rate; share of Sure answers that are
right, month over month; debugging drill unaided success at 7 and 21 days.
Run E2 (compare shown versus not shown) and E7 (call the cause first) from
phase 1; they need one flag each.

---

## Minor

1. **Dimension rollup is undefined.** `map.html` shows "Data and storage: New
   situation. 2 of 2 topics without help." The skill says "Transfers means one
   correct unassisted answer on a novel case, not mastery", but the Map gives
   a whole area the top level with no caveat and no stated rule (max? median?
   all topics?). Use the lowest current topic level, or show the count only.
2. **Decay can be item difficulty, not forgetting.** `verdict.html` state 9
   drops `retry-budget` on a harder 5-attempt webhook variant at 21 days. If
   variants differ in difficulty, the decay signal mixes forgetting with item
   hardness, and "It goes down when you forget, so it stays true" overclaims.
   Store a difficulty tag per sealed variant and treat a miss on a harder
   variant as "uncertain", not a drop, unless it repeats.
3. **Interleaving is a two-option choice.** 2.d row 5 ("the lease on the job,
   or the key on the charge?") names the candidates. Discrimination practice
   works when the learner must identify which idea applies in a mixed set
   without the menu (Brunmair and Richter). Ask the case; grade which idea
   they reach for.
4. **Waiting predictions can be read off the live diff.** In 2.a the learner
   answers "while I build" while `Edit billing/retry.py` streams in chat.
   That is fine for predictions (no level change) but should be named:
   answers locked after the first edit to the observed file get a "late" tag
   so E1 can compare them.
5. **The held result stalls the build for a computable question.** 2.a branch
   one and `flow.html` state 3: the agent withholds test output until the
   learner answers or says "show result". Worth it for a misconception item,
   not for arithmetic. Hold only when the card is marked as a misconception
   check; otherwise reveal and record `not_now`.
6. **Daily cap disagrees with the engine.** `experience.md` 2.d caps at 5 per
   day; `record.py` `DEFAULT_DUE_LIMIT = 3` with a stated reason. Pick one.
7. **Fixture schedule does not follow the ladder.** The `idempotency` topic
   sheet in `map.html` shows a miss on 28 Oct, a correct on 8 Nov and "Next
   review: 28 Nov"; after a miss the streak restarts, so the engine gives 11
   Nov. Learners read these dates as the rules.
8. **No grade appeal.** On-page grading by `sample` decides level moves on
   free text. A one-tap "I think this grade is wrong" that sends the answer
   and rubric to the session for a second look would catch grader drift and
   give the owner the agreement data that research section 15 says is missing.
9. **Hint text at With help.** `card.html` state 8: the hint "Look at what the
   worker sends with every charge call" plus "Show the code" together give
   most of the answer. Fine, as long as M7 records both.

## What works and should stay

- Rubric sealed before the question, with commit times shown on the topic
  sheet ("Answer fixed 14:15. You locked 14:22.").
- Confidence required in the same action as the answer; sure misses marked
  and returned next day (R12, R23).
- Reviews show no code, no old answer and no old feedback until the lock;
  "What you wrote on 31 Oct" appears after.
- Best as outline, latest as fill: decay is visible without shame.
- Predictions never move the record (D9); "A wrong guess here costs nothing."
- Delayed self-judgment asked once, at the 21-day review, as self-report only.
- Questions only at breakpoints, "Not now" free and immediate, one
  unprompted learning turn per 10 minutes. The interruption budget is about
  right; the issue is what each question measures, not how many there are.
- Answering the explain-back later on the phone is a small spacing gain. Keep
  it and say so.

## The three changes that would most improve the product

1. **Make the record's evidence rules honest and single.** Same-session
   explain-backs confirm at most "With help"; "Without help" needs an unaided
   correct at the first spaced review (3 days or more); "New situation" needs a
   transfer item that is far from earlier items and feedback; opening the code
   or a hint caps the attempt; drills credit the topic the bug exercises. Write
   the rule once and use the same sentence in the verdict, the Map and the
   engine (B1, M4, M5, M7).
2. **Remove recognition cues from every retrieval moment.** Free recall at
   review, hypothesis before code in drills, topic names hidden on transfer,
   drill and interleaved cards until the lock, neutral explainer headings and
   diagrams after the question, a best-guess step before "I do not know" on
   predictions, and predictions that target the known misconception with
   everything needed on the card (M1, M2, M3, M6).
3. **Put a production task and a learning gate into phase 1.** At Not yet and
   With help, the agent leaves one marked gap for the learner to write inside
   the real build; and each phase ships with outcome gates from the existing
   record (3-day and 21-day unaided success, Sure accuracy, drill success) plus
   experiments E2 and E7 (M10, M11).
