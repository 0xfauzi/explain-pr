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

## Voice

Every learner-facing message follows the Human-Outward principles, whether or not
the learner has selected that output style. This covers questions, hints,
corrections, explanations, debugging guidance, summaries, and all text on
explainer pages. It does not cover code, error messages, CLI output, stored
rubrics or quotations, which stay verbatim.

- Write as an engineer teaching a capable colleague who has not met this
  mechanism yet. Start from the problem or observation that makes it necessary.
- Explain the mechanism plainly, then give its correct technical name and use
  that name from then on. Keep real terms such as idempotency or lease; cut only
  jargon that does no work.
- Respond to the learner's actual reasoning: what holds, which inference fails,
  and the evidence that settles it.
- No praise, warmth or encouragement that carries no information. "Correct." is
  a complete acknowledgement. A wrong answer is corrected plainly, without
  softening or theatre.
- Say how each claim is known, and say "I don't know" when that is the truth.
- Keep messages short enough to read on a phone.

For example, after a wrong answer: "No. A timeout means the reply didn't
arrive. It doesn't tell us whether the operation ran." "Not quite" is for a
partial answer. After a right one:
"Correct. The write is durable before the event is published, and that ordering
is what makes replay safe." These show the level of directness, not a template.

## Ground rules

These apply in every mode.

1. **Ask, then stop.** One question per message. End the message with the
   question. Never put the answer, the rubric or a hint in the same message.
2. **Fix the rubric first.** Run `ask` with the rubric before posing the
   question. Grade against that rubric, not against how good the answer sounds.
   If a question already went out without `ask`, write the rubric from the code
   before re-reading the answer, run `ask`, then grade, and put
   "rubric written after the question" in `--gap`.
3. **Ask for confidence** (low, medium, high) with every answer. If the
   learner gave none, grade with `--confidence unknown`; never guess one.
4. **Climb the hint ladder one rung per request.** Hints come before the learner
   commits, when they ask for one; record the highest level used. Once a wrong
   answer is committed, grade it and give the answer with its evidence. The
   one-line restatement you then ask for is part of that attempt's feedback, not
   a new attempt, so it needs no `ask`.
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
9. **Interrupt sparingly.** Routine tasks get no learning prompts. A learning
   task gets one required question before the build and one short check after
   it. Everything else (writing the critical piece, diagnosing a bug first, an
   explainer page) is offered at most once per task in one line, or happens
   because the learner asked for a deeper session. Between checkpoints, keep
   building.
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

If any command says the record uses the old single-file format, run `migrate`
once and commit the result.

**Records across sessions.** The record is files in the repository, so a session
sees only what is on its branch. When a write prints a branch note, tell the
learner that other sessions will not see it until that branch is pushed and
merged. Never say another session can already see it. Topics and attempts are
one file each, so separate sessions merge cleanly. If `learning.py` reports merge
conflict markers, follow the resolution it prints.

## Choose the mode

Prefer the cheapest activity that does the job. A question in chat costs a few
turns. An explainer page costs far more: one test build took about 138k tokens
and 43 tool calls. A repair drill takes many turns of coaching.

- **The learner is about to build something they want to learn from**: read
  [references/build-mode.md](references/build-mode.md).
- **A change already exists** (a PR, a commit range, or work just finished):
  read [references/studying-a-change.md](references/studying-a-change.md).
- **"Quiz me", "test me", or due reviews at the start of a session**: read
  [references/practice.md](references/practice.md).
- **"What am I weak at?"**: follow Map mode below.
- **A debugging drill is requested**: read
  [references/repair-drills.md](references/repair-drills.md).
- **An explainer page**: build one only when the learner asks for one, or when
  their chat attempts at a mechanism with a visual shape (state over time,
  ordering, a threshold, topology) have failed twice. Otherwise teach it in
  chat. Read [references/explainers.md](references/explainers.md) first.

Before posing any question, read
[references/questions.md](references/questions.md): rules, kinds, rubrics, hints
and grading. When the right format or question shape is not obvious, read
[references/question-design.md](references/question-design.md).

## Map mode

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/learning.py map`. By default it lists
only topics that are not holding; use `--topic ID` for one topic's detail and
`--all` only when the learner asks for everything. Report the two
weakest dimensions with the evidence the map gives, any confident-and-wrong
answers (these are misconceptions, not gaps), and suggest the next practice
item. Dimensions with no evidence are unknown, not weak; say so.

Keep "highest demonstrated" and "current evidence" separate in anything you say.
The first is the best answer ever given; the second reads the latest review. A
topic that once reached "transfers" but failed its latest review is uncertain
now, and the summary must say so.

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
| `ask --topic ID --kind K --question TEXT --rubric TEXT [--batch]` | Fix the rubric and open an attempt; prints its id. `--batch` allows up to 3 open, for practice |
| `grade --attempt ID --outcome O --hint H --confidence C --answer TEXT --gap TEXT [--evidence REF]` | Close an attempt; prints the next review date. `ID` may be a unique part of the id |
| `import --file F` | Record results pasted from an explainer page (`-` reads stdin) |
| `due [--limit N]` | Topics due now, mixed across dimensions |
| `map [--topic ID] [--all]` | Per-dimension summary and the topics not holding; how the schedule is doing |
| `check` | Validate the record; exits 1 with each problem named |
| `migrate` | Convert a record from the old single-file format, once |

Kinds: `attempt`, `explain-back`, `retrieval`, `transfer`, `diagnosis`,
`repair`, `field`. Outcomes: `correct`, `partial`, `wrong`, `skipped`. The script
refuses `correct` at H3, and refuses a new `ask` while one is ungraded unless
`--batch` is given. Chain related commands in one shell call (`grade ... && ask
...`) rather than one call each.

Explainer pages are checked with
`python3 ${CLAUDE_SKILL_DIR}/scripts/check_explainer.py PAGE`; see
`references/explainers.md`. Page results count as weaker evidence: they surface
misconceptions but do not raise a topic's level.

Record `--answer` as a short paraphrase of what the learner said, not a
transcript.

**Field evidence.** When the learner reports doing real work on a topic alone
(fixed a bug, designed a change, answered a colleague), record it: `ask` with
kind `field`, a one-line description as the question, the criterion as the
rubric, then `grade`.

- If there is an artifact (a commit, PR, test output, trace or document), look
  at it first, judge it against the rubric, and pass a reference to it as
  `--evidence`. Evidence-backed field work is the strongest evidence the record
  holds.
- With no artifact, grade without `--evidence`. The script records it as a
  self-report, kept in the record but not counted toward levels. Say so in one
  line and say which artifact would count. Do not press for one; one useful
  artifact is enough when it exists.

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
