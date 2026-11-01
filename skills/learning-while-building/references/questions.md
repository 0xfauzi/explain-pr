# Writing, hinting and grading questions

## Contents

- Rules for every interaction
- Choosing a format for the learner's level
- Kinds of question
- Question shapes by dimension
- What makes a case novel
- Sequencing a session
- Writing the question
- Writing the rubric
- The hint ladder
- Grading and feedback
- Examples

## Rules for every interaction

1. **Commit before reveal.** The learner answers before seeing anything that
   contains the answer, including a code walkthrough.
2. **Produce rather than recognise.** Ask for a prediction, a cause, a design or
   a fix. Multiple choice is for explainer pages and quick checks only.
3. **Confidence with every answer.** It turns a wrong answer into a located
   misconception and shows whether the learner's sense of knowing is reliable.
4. **Explain why after the reveal.** After feedback on a correct answer, ask
   "why does that hold?" once in a while, not every time. After a wrong one, the
   learner restates the corrected model in their own words.
5. **Feedback that says why.** The outcome, the evidence, the idea that was
   missing. Never only right or wrong.
6. **One question in flight.** Do not stack questions or ask a second before the
   first is graded.

## Choosing a format for the learner's level

Pick by what the record and the learner's answers show, not by habit:

- **New to the domain or the language** (the record has nothing in this
  dimension and the attempt showed no working model): show one short worked
  example from this codebase, then ask the learner to complete a near-identical
  case with one step missing. Remove more steps on each later question until they
  write the whole thing.
- **Unfamiliar code, familiar domain**: start with tracing ("what does this
  return for input X?"), then "explain this function in one sentence", then a
  modification. Each step needs the one before it.
- **New syntax or framework, known concepts**: an ordering task (put these
  lines in order) teaches structure faster than writing from scratch.
- **Familiar territory**: skip examples. Go straight to prediction, design and
  diagnosis. Worked examples slow experienced engineers down.

Move the learner down this list as their answers improve.

## Kinds of question

| Kind | When | The learner must |
|---|---|---|
| `attempt` | Before any explanation | Commit to a design, invariant or prediction |
| `explain-back` | Right after a change works | Explain the mechanism that makes it correct |
| `retrieval` | First reviews of a topic | Reconstruct the mechanism from memory, without opening the code |
| `transfer` | After one unassisted correct retrieval | Apply the mechanism to a case not yet discussed |
| `diagnosis` | A real bug during the build | Name the cause from the symptom and propose a test that distinguishes it |
| `repair` | A debugging drill | Find and fix an injected bug (see `repair-drills.md`) |
| `field` | The learner reports real solo work | Nothing new; the record captures what they did |

Prefer questions that make the learner produce something: a prediction, a
design, a cause, a fix. Recognition questions (multiple choice, "is it A or B")
test less and should be rare.

## Question shapes by dimension

| Dimension | Question shapes that make the learner reason |
|---|---|
| architecture-and-design | "When would the rejected design have been the right one?"; "Where would you add X, and what would it couple to?" |
| domain-model | "Which rule in the domain does this check enforce, and what happens to a record that violates it?" |
| correctness-and-testing | "Which existing test would fail if line N were deleted? If none, write the test." |
| debugging-and-diagnosis | Symptom and log only: "What is your first hypothesis, and what single check would rule it out?" |
| performance | "Predict how this scales with 10x the rows, then let's measure it." Measure before grading; do not grade against an estimate. |
| reliability-and-operations | "The process dies between line A and line B. What state is left, and what does restart do with it?" |
| security | "Who can reach this function, and what stops an unauthenticated caller?" |
| data-and-storage | "What does this migration do to rows written before it ran?" |
| concurrency | "Two requests run lines A to B interleaved like this. What is the final value?" |
| code-reading | "What does this function return for this input?" (trace, without running it) |

Avoid questions answerable by matching words in the question, trivia such as
function names, and anything the previous message already said.

## What makes a case novel

A `transfer` question must change at least one thing the earlier discussion held
fixed, so that recalling the earlier answer is not enough:

- a different failure point (the crash happens after the write, not before)
- a different input or load (two writers instead of one, a full disk, a clock
  jump)
- a different part of the system that uses the same mechanism
- the reverse direction (what change to the code would break this invariant?)
- a design extension (add a feature without violating the invariant)

Before asking, check the case against earlier questions on the topic (they are in
`.learning/attempts.jsonl`). If the answer to the new question appears in an
earlier rubric, it is retrieval, not transfer. Record it with the right kind.

## Sequencing a session

- Start with the oldest due topic, so retrieval comes before anything new.
- Mix dimensions within a session (`due` already interleaves them). Mixing makes
  the learner decide which idea applies, which a run of same-topic questions
  never asks of them.
- Keep the hard question hard. If an answer is wrong, give feedback and a hint
  rung if they want one; do not swap in an easier question to end on a success.
- End on the single most important gap, stated in one line.

## Writing the question

- Ground it in this repository's code, using real names, paths and values.
- State the situation, not the mechanism. "The process is killed after line 84
  runs and before line 91. On restart, what happens to the order?" not "Explain
  the idempotency key."
- Ask for one thing. If the rubric needs two unrelated points, split it into two
  questions.
- For `retrieval`, ask the learner not to open the code first. Reading it turns
  retrieval into recognition.
- Keep code excerpts short, under about 20 lines, so the question reads on a
  phone.

## Writing the rubric

Write the rubric before the question goes out, and pass it to `ask`. It lists the
points a correct answer must contain, each traceable to code or a command run in
this session:

    1. Charge sent but ack lost leaves the outcome unknown (gateway.py:88-97)
    2. Retry without the idempotency key would double-charge
    3. Correct recovery queries the gateway by key before retrying (recover.py:40)
    Correct = 1 and 3. Partial = 1 only.

Say in the rubric what counts as correct and what counts as partial. If the
right answer cannot be confirmed from the code or a command, do not ask the
question.

## The hint ladder

Give a hint only when the learner asks, or after a wrong answer when they want to
try again. One rung per request:

- **H1, a nudge.** Name the kind of thing that matters, without pointing at it.
  "Think about what the caller knows when the timeout fires."
- **H2, a pointer.** Point at the file, boundary or observation. "Look at what
  `send()` returns when the socket closes before the ack."
- **H3, the answer.** Give the worked answer with evidence. The attempt can be
  graded `partial` or `wrong` at most.

Record the highest rung used. A correct answer after H1 or H2 is a correct answer
with help, and the record treats it that way.

## Grading and feedback

1. Compare the answer to the rubric, point by point.
2. Say the outcome in the first sentence: correct, partial or wrong.
3. Respond to the learner's reasoning, not just the conclusion. Say which part
   holds, which inference fails, and the evidence that settles it, citing
   `path:line`. A right answer reached by a wrong route is partial, and the
   route is what to correct.
4. If the confidence was high and the answer wrong, say plainly that this is a
   misconception, name the belief that produced it, and show the evidence
   against it. Correcting a confident error is the most valuable feedback in the
   session.
5. If the answer was right for a reason the rubric did not anticipate, check the
   reason against the code. If it holds, grade it correct and say the rubric was
   incomplete.
6. Run `grade`, with `--gap` naming the missing idea in one line.

Feedback is short: the outcome, the evidence, the missing idea. Do not restate
the parts the learner got right. No praise or encouragement that carries no
information; a correct answer is acknowledged in a word and the session moves on.
Write it in the voice set out in `SKILL.md`:

> Not quite. You assumed the timeout means the charge failed. A timeout only
> means the reply didn't arrive; the gateway may have finished the charge
> (`worker/charge.py:41`). What would you check before retrying?

## Examples

**Retrieval** on topic `crash-recovery`:

> Without opening the code: when the worker restarts after a crash, how does it
> decide whether a job that was in flight already charged the customer?
> Confidence: low, medium or high?

**Transfer** on the same topic, changing the failure point:

> New case. The gateway accepted the charge, and our database write recording it
> failed with a disk-full error. The worker did not crash. What does the
> current code do next, and does the customer get charged twice? Confidence?

**Attempt** before building a rate limiter:

> Before I write anything: requests arrive at three API replicas and the limit
> is 100 per minute per customer across all of them. Sketch where the count
> lives and what happens when two replicas check it at the same moment.
> Confidence?
