# Practice

Spaced review of topics that are due. Independent review questions go out
together in one message and come back in one reply, which costs fewer turns and
fewer waits for the learner.

## Where to run it

Practice needs only this skill, the record and a few code files. Inside a long
build conversation, every turn re-reads that whole conversation. If practice is
asked for deep into a build, say once, in one line, that a new session is
cheaper and faster for it, and carry on here if the learner prefers.

## Workflow

```
Practice:
- [ ] 1. Run `due`
- [ ] 2. Re-read each topic's anchor files
- [ ] 3. Send the batch: all questions in one message
- [ ] 4. Grade the whole reply in one message
- [ ] 5. Close with two lines
```

**1. Run `due`.** `python3 <skill>/scripts/learning.py due` shows at
most three topics, mixed across dimensions. If it reports an ungraded attempt,
grade it first (`skipped` if the learner never answered). If nothing is due,
say so and offer one transfer question or a repair drill on the weakest
dimension from `map`.

**2. Re-read the anchors.** The code may have changed since the topic was
recorded. If an anchor is missing or the concept no longer applies, tell the
learner and retire the topic with a reason.

**3. Send the batch.** Write one question per topic, of the kind `due`
suggests, following `questions.md`. Record them all in one command before
sending:

    L="python3 <skill>/scripts/learning.py"
    $L ask --batch --topic A ... && $L ask --batch --topic B ... && $L ask --batch --topic C ...

Then send one message: the questions numbered, each in two or three lines, and
one line asking for an answer and a confidence (low, medium, high) for each. Ask
the learner not to open the code for retrieval questions.

**4. Grade in one message.** Grade every answer against its rubric, then run all
the `grade` commands in one chained command. Reply with one block per question:
the outcome word, and for a miss the evidence and the missing idea, as
`questions.md` describes. A confident wrong answer gets the full correction. A
correct one gets "Correct." and nothing more. If any answer was wrong, end with
the one-line restatement request for the most important miss only.

If the learner wants to answer later or away from the conversation, post the
batch instead of sending it (`learning.py post`, one per topic) and grade it
from `inbox` next time; see `room.md`.

**5. Close** with two lines: what the learner showed unaided, and the one gap to
work on next.

## When to ask one at a time instead

A batch only works when the questions are independent. Ask one at a time when:

- a question builds on the answer to the previous one
- two due topics are close enough that one answer would give away the other
- the learner asks for hints on a question; finish that question alone, with
  the hint ladder, before grading the rest
- the activity is a diagnosis or a repair drill

## Order within a session

- Start with the oldest due topic, so retrieval comes before anything new.
- Mix dimensions within a session (`due` already interleaves them). Mixing makes
  the learner decide which idea applies, which a run of same-topic questions
  never asks of them.
- Keep the hard question hard. If an answer is wrong, give feedback and a hint
  rung if they want one; do not swap in an easier question to end on a success.
- End on the single most important gap, stated in one line.
