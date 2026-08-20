# explain-pr

Two things for explaining engineering work, and the measurements that check them.

- **`explain-pr`**, a skill that turns a pull request into a lesson somebody can
  read in a sitting, with widgets they can operate, kept in your repository.
- **`Human-Outward`**, a writing style that changes how the model explains
  everything else: simple words, varied sentences, the idea before its name, the
  rejected approach shown, and a clear mark on how each claim is known.

A code review asks what is wrong with a change. Both of these ask something
different. What does somebody need to understand, and in what order, before the
next change here is safe to make?

## Install

    /plugin marketplace add 0xfauzi/explain-pr
    /plugin install explain-pr@explain-pr

Then, in a repository with an open or merged PR:

    /explain-pr:explain-pr 128

Both artefacts are namespaced by the plugin, which is worth knowing before you go
looking for them. Measured on a fresh clone, the skill lists as
`explain-pr:explain-pr`, and the style is selected as:

    /output-style explain-pr:Human-Outward

The namespace matters most for the style, because a bare name resolves to a local
style first if you have one.

`Human-Outward` replaces the earlier `Teacher` style. It says the same things
about teaching and adds what the research found, most importantly that simple
words and varied sentences are separate dials and only the first should be turned
down.

## What the skill does

1. **Fixes the diff range against the PR's own base**, not the default branch.
   Stacked PRs and merged PRs each get this wrong by default, in opposite
   directions, and both mistakes are silent.
2. **Hands the writing to a reader who did not make the change.** An author
   explains a change as they intended it, and cannot see which parts of their
   reasoning never reached the diff.
3. **Builds the lesson as one arc:**
   - where this sits in the system
   - why each decision went the way it did
   - what you need to make the next change here
   - what would make it wrong
4. **Prefers a widget the reader can operate over a picture of a rule.** A
   picture states the rule. It does not let anybody try it and be surprised.
5. **Records what was taught**, so the set eventually reads as one account of
   the system rather than a pile of files.

`skills/explain-pr/SKILL.md` is the procedure. The detail lives in
`references/`:

- **`writing.md`** carries the writing rules, each with the draft that failed
  without it, plus the measurement that overturned one of them.
- **`widgets.md`** covers what to draw and when, the archetypes worth reaching
  for, and how to prove a widget is not lying.
- **`register.md`** has the entry format and the supersession rule.

## The two checkers

    python lesson_lint.py <lesson.html> [--glossary <register.md>]
    python lesson_lint.py --register <register.md>
    python ai_tells.py <draft> <a file a person wrote>

Both live in `skills/explain-pr/scripts/`.

`lesson_lint.py` reads the writing rules so they cannot rot: sentence length,
paragraph length, forbidden characters, and whether every inline script parses.
Its register mode checks the rules no repository can opt out of, and all three
supersession rules were mutation-tested, so breaking one makes it fire and
restoring it makes it pass.

`ai_tells.py` counts the documented signatures of unedited model prose. It has no
pass mark on purpose. See below for why, and for what it found.

## What the tells meter measures, and why it has no pass mark

The battery was fixed from published work before any of our own prose was
measured, because a list built by looking at your own writing can only confirm
it. Sources are named in the script.

Three classes, and they behave differently.

**Vocabulary washes out.** The words people learned to spot in 2023, "delve" and
"tapestry" and the rest, have largely gone. Writers avoid them once they are
publicised, and humans have picked some of them up from reading model output, so
the marker decays from both ends. Any fixed word list has a shelf life measured
in months, so the lists here carry their era and the current one is short.

**Shapes persist.** Negative parallelism ("it is not just X, it is Y"), the rule
of three used because three sounds complete, participial tails that assert
significance without evidence. These survived the vocabulary washout because they
are constructions rather than words.

**Structure persists hardest.** Heading, bullet and bold habits learned from
markdown-heavy training survive an explicit instruction to write differently,
which makes them the honest test of whether a style prompt changed anything.

A count on its own is a change detector, not a quality measure. Pass a file you
know a person wrote and the number becomes a direction.

## The measurement that changed one of our own rules

The writing rules used to set a hard twenty-word sentence cap. Measured, it was
doing the opposite of its job.

Two explanations of the same pull request, same prompt and same model, differing
only in whether the Teacher style was on:

| | mean words | longest | rhythm (cv) |
| --- | ---: | ---: | ---: |
| style off | 26.2 | 114 | 0.874 |
| style on | 26.4 | 64 | **0.606** |
| the repository owner's own writing | 20 to 22 | 78 to 129 | 0.76 to 0.81 |

The cap did not shorten the average sentence at all. It clipped the long tail,
and the long tail is what makes prose read like a person. Uniform sentence length
is the one signature word choice cannot disguise, so the rule was pushing the
prose toward the thing it was meant to avoid. A separate comprehension test on
the same two documents found no detectable difference either way.

Both the style and the skill now steer the distribution rather than the maximum,
and `lesson_lint.py` reports the rhythm figure beside the sentence count.

The target depends on register, and there is no single number. Measured on text
with hard publication dates, so the human label is a date and not a judgement:

| register | human | machine | separates? |
| --- | ---: | ---: | --- |
| specs, docs, procedures | 0.78 (n=18) | 0.49 (n=5) | yes, perfectly |
| essays | 0.63 (n=8) | 0.60 (n=16) | no |

Rhythm tells human from machine writing only where human writers actually vary.
Specification authors vary enormously. Good essayists often do not, so chasing
the number in an essay moves you away from how the best of them write.

**Two caveats, both found by an independent review and both reproduced.** The
measure is trivially gameable: a short script that joins sentences with ", and"
raises cv by between +0.148 and +0.409 while preserving every word and making the
prose worse. And the separation above depends on an undisclosed preprocessing
choice, because 30% of what the instrument calls a sentence in the human corpus is
document furniture like "Table of Contents". Stripping that furniture leaves the
result intact; dropping every sentence under 8 words collapses it to chance.
Treat cv as a diagnostic, never as a target. `research/results.md` has the
numbers.

`research/design.md` and `research/results.md` carry the full programme, including
the three levers that failed and one place where a pre-registered rule passed and
a better test refuted it.

## Does the skill work?

Partly measured, and the measurement is unflattering. That seems worth putting in
the README rather than leaving somebody to discover it.

`evals/` holds `claude plugin eval` cases for the cheap half: does the skill fire
when somebody asks to understand a PR, and does it stay out of the way when they
ask for a defect review. Those are discovery tests and say nothing about
teaching. Measured separately by hand on Opus, in a repository with real PRs and
no competing skill of the same name, the description scored 5 of 6, with all
three near-miss negatives correctly staying quiet.

The expensive half was measured on one repository and one PR, three runs per arm.
A reader was given a single packet and nothing else, then examined on questions
drawn from the diff and the code, written before the lesson was opened. A control
arm whose packet described nothing scored 0 of 16 on every run, so no answer came
from prior knowledge.

On that PR the shipped lesson scored **10 of 16**. A plain explanation of the same
change scored **13.7**, and the raw diff on its own scored **14.0**. The lesson
passed `lesson_lint.py` with zero findings.

The cause turned up by grepping the lesson rather than by trusting the exam. It
never named the two fields the PR's own description calls the point of the
change. That is a content omission, not a style problem, and no style checker was
going to catch it.

Read those numbers as a demonstration that the measurements work, not as a
verdict. It is one PR, and the exam's questions were written by somebody who had
read the diff, which tilts them toward what the diff emphasises.

## Licence

MIT. See `LICENSE`.
