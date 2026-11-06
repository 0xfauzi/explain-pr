# Designing questions

Read this when writing a new question and the right format or shape is not
obvious. The rules for asking and grading are in `questions.md`.

## Contents

- Choosing a format for the learner's level
- Question shapes by dimension
- Examples

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
