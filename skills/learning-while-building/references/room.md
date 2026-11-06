# Questions that don't block the build

A posted question waits for the learner while the build carries on. The learner
answers when it suits them: in chat, in a terminal, or on the learning room
page. The next checkpoint grades whatever is waiting. Everything goes through
the same record, so it works in any harness that can run Python.

## Contents

- When to post instead of ask
- Posting
- Telling the learner where to answer
- Grading what is waiting
- The learning room page
- Rules that hold on every route

## When to post instead of ask

Post when the learner is not in the conversation right now, has said they will
answer later, or is working from a phone. Ask in chat when they are present:
a chat answer is graded at once, and immediate feedback on a miss is worth more
than a later one.

Some questions only work in order. The question before a build (kind `attempt`)
is a prediction, and an answer given after seeing the change is not one. If the
learner is present, ask it in chat. If they are away, post it with "Answer
before you look at the change" at the start of the question, and accept that
it may be answered late; `attempt` results never move a level anyway.
Explain-backs, review questions and transfer questions suit posting well.

## Posting

    learning.py post --topic ID --kind K --question TEXT --rubric TEXT [--context TEXT]

The rubric is written from the code before posting, exactly as for `ask`.
`--context` carries a short excerpt or situation shown with the question,
under about 20 lines so it reads on a phone. Post at most three questions at a
time, for the same reason practice batches stop at three.

Posting does not interrupt anything: say in one line that a question is
waiting and where to answer it, then carry on with the build.

## Telling the learner where to answer

Offer the routes this harness supports, cheapest first:

1. **In chat**, whenever they are next here. Record their reply with
   `learning.py answer --attempt ID --text TEXT --confidence C` (or
   `--dont-know`), then grade it.
2. **In a terminal**, without any model: `learning.py questions` lists what is
   waiting and shows recent feedback; `learning.py answer` asks the oldest
   question, takes the answer and a confidence, and locks it.
3. **On the local page**: `learning.py serve` starts it on this machine at
   http://127.0.0.1:8765/. Only from a machine the learner can reach; from a
   phone, that means their own SSH tunnel or port forward. Do not bind it to a
   public address: anyone who can reach it can read the questions.
4. **On a hosted page**, only when this harness can publish a private page
   with its own data store (see below). This is the one route where grading
   happens on the spot.

## Grading what is waiting

At each checkpoint, and at the start of a session, run `learning.py inbox`. It
lists every saved answer with its question and rubric. Grade them together, as
in practice: decide each outcome against its rubric, then run all the `grade`
commands in one chained call, each with `--feedback`:

    learning.py grade --attempt ID --outcome O --hint 0 --feedback TEXT --gap TEXT

`--answer` and `--confidence` come from the saved answer. `--feedback` is what
the learner will read on the page or with `questions`, so write it exactly as
the chat feedback in `questions.md`: the outcome word first ("Correct.", "Not
quite.", "No."), the learner's reasoning addressed, the evidence with
`path:line`, the belief named when a confident answer was wrong, no praise, and
no more than about 120 words. If the learner is in the conversation, also tell
them in two lines what was graded and where to read it.

## The learning room page

`assets/room.html` is one page for both page routes. It shows one question at a
time, takes an answer and a confidence, offers "I don't know" and "Not now",
locks the answer on submit, then shows the verdict and asks for a one-line
restatement after a miss. It needs no changes per project.

**Local:** `learning.py serve` serves it with the record behind it. Grading
waits for the next session; the page checks for feedback every few seconds
while an answer is waiting and shows it when it arrives.

**Hosted:** when this harness can publish an HTML page with a private document
store that the session can read and write, the page grades answers itself
against the stored rubric. To use it:

1. Publish `assets/room.html` privately with the store and the ability to call
   the model from the page enabled. Publish once per project and reuse the page.
2. Push posted questions: `learning.py room-push --out DIR` writes one JSON file
   per ungraded question; write each into the page's `questions` collection,
   with the file name (without `.json`) as the document id.
3. Pull answers back: save the `questions` collection as one JSON file per
   document into a folder, then `learning.py room-pull --from DIR`. Answers the
   page graded are recorded as graded by Claude on the page; anything only
   answered appears in `inbox`.

The hosted store holds the rubric, so the learner, as owner, could read it
there. The page never shows it before an answer is locked. For a personal
record this is acceptable; say so if the learner asks.

## Rules that hold on every route

- The rubric is fixed before the question is posted.
- One question at a time is shown; the answer locks when saved.
- Confidence comes with every answer; "I don't know" is recorded as a real,
  low-confidence answer, and "Not now" leaves the question open.
- Feedback follows the voice in `SKILL.md` and is stored with the grade.
- After a miss, the learner is invited to restate the idea in one line.
- Nothing about this route may stop or slow the build.
