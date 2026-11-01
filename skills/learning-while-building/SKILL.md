---
name: learning-while-building
description: Turns building software with Claude into deliberate practice, so the learner's own engineering ability grows instead of eroding. Has the learner attempt designs, predictions and diagnoses before Claude explains, has them explain finished changes back, schedules spaced retrieval and transfer questions, builds interactive explainer pages that make the learner predict before revealing, runs debugging drills on injected bugs, and keeps a per-dimension record of what the learner has shown they can do unaided. Use when the user wants to learn from the work rather than only finish it - "make this a learning task", "teach me as we build", "help me understand what PR 128 did", "quiz me", "test whether I still understand X", "what am I weak at", "give me a debugging drill", "draw me how this works". Do not use for ordinary implementation, defect review or code review requests that show no learning intent.
---

# Learning while building

The target is what the learner can do without Claude: predict, design, debug and
extend the system unaided. Finishing the task matters too, so Claude still does
most of the building. The learner does the thinking at a few chosen points.

Terms used throughout:

- **learner**: the user, in the role of someone building skill
- **topic**: one transferable concept tied to code in this repository
- **attempt**: one question posed to the learner and graded
- **rubric**: the expected answer points, written before the question is asked
- **hint level**: H0 none, H1 a nudge toward what matters, H2 a pointer to the
  file, boundary or observation, H3 the worked answer
- **record**: the data kept by `scripts/learning.py`

Requires Python 3.9+ and git. Explainer checks also need node, and Playwright
for node for the browser half; without them, say which checks did not run.

## Ground rules

These apply in every mode.

1. **Ask, then stop.** One question per message. End the message with the
   question. Never put the answer, the rubric or a hint in the same message.
2. **Fix the rubric first.** Run `ask` with the rubric before posing the
   question. Grade against that rubric, not against how good the answer sounds.
3. **Ask for confidence** (low, medium, high) with every answer.
4. **Climb the hint ladder one rung per request.** Give a hint only when the
   learner asks or after a wrong answer, and record the highest level used.
5. **Grade plainly.** Say correct, partial or wrong. A confident wrong answer
   gets told it is wrong, directly, with the reason. Never praise an answer the
   rubric does not support.
6. **Explain the why, with evidence.** Feedback cites `path:line` in the current
   code and says what the learner's answer missed.
7. **Answer conceptual questions directly.** Asking how something works is the
   learner doing the right thing. Withhold only the answer to a question Claude
   has just posed, and the diagnosis during a debugging drill.
8. **Respect "skip" and "just do it".** Comply at once, grade any open attempt
   as `skipped`, and do not ask again during that task.
9. **One interruption per task.** Routine tasks get none. Learning is opt-in per
   task, never imposed on every change.
10. **Ground every question in code read this session.** If Claude cannot
    verify the right answer from the code or a command, it says so and does not
    grade.

## Set up the record

On first use in a repository, run:

    python3 ${CLAUDE_SKILL_DIR}/scripts/learning.py init

Run all commands from the repository root. Before running `init`, show the
learner the default dimensions (run `init --help` to print them) and ask which to keep, drop or add. Pass their list with
`--dimensions a,b,c`. Then tell the learner to commit `.learning/`, because a
cloud session's container is reclaimed and uncommitted files go with it. If they
want the record out of the project repository, pass `--dir` to point elsewhere.

## Choose the mode

- **The learner is about to build something they want to learn from**: follow
  Build mode below.
- **A change already exists** (a PR, a commit range, or work just finished):
  read [references/studying-a-change.md](references/studying-a-change.md).
- **"Quiz me", "test me", or the start of a session**: follow Practice mode.
- **"What am I weak at?"**: follow Map mode.
- **A debugging drill is requested or due**: read
  [references/repair-drills.md](references/repair-drills.md).
- **A mechanism needs a picture** (state over time, ordering, a threshold,
  topology) and the learner has already attempted it in chat: build an
  explainer page by following
  [references/explainers.md](references/explainers.md). Also when the learner
  asks for one.

Before writing any question, read
[references/questions.md](references/questions.md). It covers question kinds,
what makes a case novel, rubrics, hints and grading.

## Build mode

Copy this checklist and track it:

```
Build mode:
- [ ] 1. Confirm the task is learning-critical
- [ ] 2. Attempt first: one question before any design is shown
- [ ] 3. Decide who writes the critical piece
- [ ] 4. Build; offer the learner the first diagnosis of any bug
- [ ] 5. Explain-back once it works
- [ ] 6. Record topics
```

**1. Confirm the task is learning-critical.** Either the learner said so, or the
task touches a dimension where `map` shows little evidence. In the second case,
propose it once in one line ("This touches concurrency, where the record is
thin. Make it a learning task?"). If they decline, build normally and stop here.

**2. Attempt first.** Before showing a design, ask one question that makes the
learner commit: sketch the approach, name the invariant that must hold, or
predict where it will break. Do not walk through the relevant code first: point
to the files and let the learner read them, because a walkthrough is a hint
(H1 or H2) given before the attempt. Add the topic if it is new (`topic add`), then
`ask` with kind `attempt`. A wrong attempt is expected and useful; it sets up
the explanation. After grading, give the design and say where it differs from
theirs and why.

**3. Decide who writes the critical piece.** If there is a small piece on the
critical path that carries the concept, offer the learner the chance to write it
while Claude writes the rest. Review their code as a peer would. If they decline,
Claude writes it.

**4. Build, and offer the first diagnosis.** When a bug or failing test appears,
show the symptom and ask in one line whether the learner wants to diagnose it
first. If yes, run it as a `diagnosis` attempt with the hint ladder. If no, fix
it.

**5. Explain-back.** Once the change works, ask the learner to explain the
mechanism that makes it correct, or what change would break it. Use kind
`explain-back`. Do not summarise the change first; the learner's explanation
comes before Claude's. If their answer shows a gap in a mechanism with a visual
shape, offer an explainer page aimed at that gap.

**6. Record topics.** Keep one to three topics per task: the concepts worth
having in a month. Each one needs a `--concept` a stranger could understand and
`--anchor` paths to the code that embodies it. Topics are scheduled
automatically.

## Practice mode

```
Practice mode:
- [ ] 1. Run `due`
- [ ] 2. For each topic shown: re-read the anchors, ask, grade, give feedback
- [ ] 3. Close with a two-line summary
```

**1.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/learning.py due`. If it reports
an ungraded attempt, grade it (`skipped` if the learner never answered) before
anything else. If nothing is due, say so and offer a transfer question or a
repair drill on the weakest dimension from `map`.

**2.** For each topic, re-read its anchor files first, since the code may have
changed. If an anchor is missing or the concept no longer applies, tell the
learner and retire the topic with a reason. Then use the suggested kind from
`due`: `retrieval` until the learner has one unassisted correct answer, then
`transfer` or `repair`. Ask one at a time.

**3.** Close with two lines: what the learner showed unaided, and the one gap to
work on next.

## Map mode

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/learning.py map`. Report the two
weakest dimensions with the evidence the map gives, any confident-and-wrong
answers (these are misconceptions, not gaps), and suggest the next practice
item. Dimensions with no evidence are unknown, not weak; say so.

## Script reference

Run, do not read. Prefix each command with
`python3 ${CLAUDE_SKILL_DIR}/scripts/learning.py`. All commands take `--dir`
(default `.learning`). Every write
goes through the script; never edit the data files by hand.

| Command | Use |
|---|---|
| `init [--dimensions a,b]` | Create the record |
| `topic add --id ID --dimension D --concept TEXT --anchor PATH` | Add a topic; `--anchor` repeats |
| `topic add-dimension --name D` | Add a dimension the learner asked for |
| `topic retire --id ID --reason TEXT` | Stop scheduling a topic |
| `ask --topic ID --kind K --question TEXT --rubric TEXT` | Fix the rubric and open an attempt; prints its number |
| `grade --attempt N --outcome O --hint H --confidence C --answer TEXT --gap TEXT` | Close an attempt; prints the next review date |
| `import --file F` | Record results pasted from an explainer page (`-` reads stdin) |
| `due [--limit N]` | Topics due now, mixed across dimensions |
| `map` | Per-dimension evidence, misconceptions, and how the schedule is holding up |
| `check` | Validate the record; exits 1 with each problem named |

Kinds: `attempt`, `explain-back`, `retrieval`, `transfer`, `diagnosis`,
`repair`, `field`. Outcomes: `correct`, `partial`, `wrong`, `skipped`. The script
refuses `correct` at H3, and refuses a new `ask` while one is ungraded.

Explainer pages are checked with
`python3 ${CLAUDE_SKILL_DIR}/scripts/check_explainer.py PAGE`; see
`references/explainers.md`. Page results count as weaker evidence: they surface
misconceptions but do not raise a topic's level.

Record `--answer` as a short paraphrase of what the learner said, not a
transcript.

**Field evidence.** When the learner reports doing real work on a topic alone
(fixed a bug, designed a change, answered a colleague), record it: `ask` with
kind `field`, a one-line description as the question, the criterion as the
rubric, then `grade`. This is the strongest evidence the record can hold.

## What this cannot do

Say these when they matter, rather than working around them.

- Grading is Claude's judgement against a rubric Claude wrote. The record is
  evidence about the learner, not a certificate.
- Levels count unassisted answers, nothing more. "Transfers" means one correct
  unassisted answer on a novel case, not mastery.
- Nothing reminds the learner. Reviews happen only when the skill runs.
- The review intervals are starting values from spacing research on other
  material. `map` prints the success rate at each step so they can be checked
  against this learner's record.
