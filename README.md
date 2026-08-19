# explain-pr

A Claude Code skill that turns a pull request into a lesson, and then keeps it.

A code review asks what is wrong with a change. This asks something different.
What does somebody need to understand, and in what order, before the next change
here is safe to make?

What comes out is one self-contained HTML file, kept in your repository. A line in
a register records what it taught. Six months later, whoever picks up that part of
the system can read it.

## Install

    /plugin marketplace add 0xfauzi/explain-pr
    /plugin install explain-pr@explain-pr

Then, in a repository with an open or merged PR:

    /explain-pr 128

## What it actually does

1. **Fixes the diff range against the PR's own base**, not the default branch.
   Stacked PRs and merged PRs each get this wrong by default, in opposite
   directions, and both mistakes are silent.
2. **Hands the writing to a reader who did not make the change.** An author
   explains a change as they intended it. They cannot see which parts of their
   reasoning never reached the diff.
3. **Builds the lesson as one arc:**
   - where this sits in the system
   - why each decision went the way it did
   - what you need to make the next change here
   - what would make it wrong
4. **Prefers a widget the reader can operate over a picture of a rule.** A
   picture states the rule. It does not let anybody try it and be surprised.
5. **Records what was taught.** The set eventually reads as one account of the
   system, rather than a pile of files.

`skills/explain-pr/SKILL.md` is the procedure. The detail lives in
`references/`:

- **`writing.md`** carries the writing rules, each with the draft that failed
  without it. It also covers the trap of meeting a sentence limit by chopping,
  and the one-word technique that avoids it.
- **`widgets.md`** covers what to draw and when, and the archetypes worth
  reaching for. It also shows how to prove a widget is not lying.
- **`register.md`** has the entry format and the supersession rule.

## The checker

Bundled inside the skill, at `skills/explain-pr/scripts/lesson_lint.py`. It does
two jobs:

    python lesson_lint.py <lesson.html> [--glossary <register.md>]
    python lesson_lint.py --register <register.md>

The first reads the writing rules so they cannot rot: sentence length, paragraph
length, forbidden characters, and whether every inline script parses. Point it at
your register and it also flags the banned aliases in your `_Avoid_` lines.
Figures marked `data-generated` are left alone, since their labels answer to
whatever produced them.

The second checks the register rules no repository can opt out of. Every lesson
file has an entry, every entry names a file that exists, every `reverses:`
resolves, and a reversed lesson carries both its `superseded-by:` field and its
banner. Each of those three supersession rules was mutation-tested: break it and
the checker fires, restore it and the check passes.

What neither can do is tell you whether a widget teaches the truth. Nothing can.

## Does it work?

Partly measured, and the measurement is unflattering. That seems worth putting in
the README rather than leaving somebody to discover it.

`evals/` holds `claude plugin eval` cases for the cheap half of the question. Does
the skill fire when somebody asks to understand a PR? Does it stay out of the way
when they ask for a defect review? Both are useful, and both are discovery tests.
Neither says anything about whether the lesson teaches.

The expensive half was measured separately, on one repository and one PR, with
three runs per arm. A reader was given a single packet and nothing else, then
examined on questions about the change.

Those questions came from the diff and the code, and they were written before the
lesson was opened. A question written from the lesson would score the lesson
against itself.

A control arm, whose packet described nothing at all, scored 0 of 16 on every
run. So the reader was not answering from prior knowledge. Every point elsewhere
came from the page.

On that PR the shipped lesson scored **10 of 16**. A plain explanation of the same
change, written without this procedure, scored **13.7**. The raw diff on its own
scored **14.0**. The lesson passed the checker above with zero findings.

The cause turned up by grepping the lesson, not by trusting the exam. It never
named the two fields the PR's own description calls the point of the change. So
this was a content omission rather than a style problem, and no style checker was
going to catch it.

Read that as a demonstration that the measurement works, not as a verdict on the
procedure. It is one PR. The exam's questions were written by somebody who had
read the diff, which tilts them toward what the diff emphasises.

The procedure's own closing section already said the checker counts sentences
rather than teaching. This is what that looks like once somebody attaches a number
to it.

## Licence

MIT. See `LICENSE`.
