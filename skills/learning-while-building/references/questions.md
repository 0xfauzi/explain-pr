# Writing, hinting and grading questions

## Contents

- Kinds of question
- What makes a case novel
- Writing the question
- Writing the rubric
- The hint ladder
- Grading and feedback
- Examples

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
3. For each missed point, say what was missing and cite `path:line`.
4. If the confidence was high and the answer wrong, say plainly that this is a
   misconception, name the belief that produced it, and show the evidence
   against it. Correcting a confident error is the most valuable feedback in the
   session.
5. If the answer was right for a reason the rubric did not anticipate, check the
   reason against the code. If it holds, grade it correct and say the rubric was
   incomplete.
6. Run `grade`, with `--gap` naming the missing idea in one line.

Feedback is short: the outcome, the evidence, the missing idea. Do not restate
the parts the learner got right.

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
