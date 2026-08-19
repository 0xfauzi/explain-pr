---
name: explain-pr
description: Teach a pull request. Turns a change into a lesson with widgets the reader can operate, and records what it taught in a register. Use whenever somebody wants to understand a change rather than find defects in it - "walk me through this PR", "explain what this change actually did", "help me understand PR 128", onboarding someone to a part of the system, or writing up what a change taught so it survives. Reach for it even when the request never says lesson or explain, as long as the goal is understanding a landed or proposed change and where it sits in the system. Defect-hunting is a different job and belongs in a code review.
license: MIT
compatibility: Requires git and the gh CLI. The bundled checker needs Python 3, and node to parse widget scripts.
---

# Explaining a pull request

Turn one pull request into a **lesson**: a self-contained HTML page somebody can
read in a sitting, with widgets they can operate, plus one register entry
recording what it taught.

A review and a lesson pull in opposite directions. A review hunts for what is
wrong, and hedging serves it well. A lesson that hedges to stay defensible
teaches nothing. Keep this job separate from defect-hunting, which belongs in a
code review.

Paths below are relative to this skill's directory.

## How the work splits

You do steps 1 to 3, then hand the writing to a **fresh reader**: a subagent that
did not make the change. It does steps 4 to 7. You take its output and do step 8.

That split is the point, not a convenience. An author explains a change as they
intended it, not as it landed, and cannot see which reasoning never reached the
diff. In their head it is still there.

It also keeps the reference files out of your context. The fresh reader reads
them; you dispatch it.

## 1. Fix the subject

Establish exactly which range you are teaching, before reading a line of it.

    gh pr view <n> --json number,title,body,headRefName,baseRefName,state
    git fetch origin <headRefName> <baseRefName>
    git merge-base origin/<baseRefName> origin/<headRefName>

Diff against the PR's own base, because PRs stack. Diff a stacked PR against the
default branch and you fold the parent's change into the lesson, so the reader
learns about work nobody in this PR did.

For a merged PR, reach for `gh pr diff <n>`. Once a branch merges,
`git merge-base` returns the head commit itself and the diff comes back empty.

Read code from the remote refs, with `git show origin/<headRefName>:<path>`. The
author may still be editing, so their tree can hold untracked or evolved copies
of these files. An untracked file appears in no diff, and against the tree that
absence looks exactly like a deletion. Teach the branch.

**Done when** you can state the base sha, the head sha and the changed-file
count, and the diff you hold is non-empty.

## 2. Read what has already been taught

Repositories that keep a register of lessons keep the agreed vocabulary there
too, alongside one entry per lesson. Read it before anything gets written twice.

Three things to establish:

- whether this PR already has a lesson, since a PR that grew under review gets a
  second one teaching only the delta
- which glossary entries this change contradicts
- which terms the lesson can rely on rather than explain again

A contradicted entry gets revised where it stands, and the new entry records
that it reverses the old one. This matters more than it sounds. One lesson
taught a constant, and taught that a value was deliberately absent from a type.
Later commits deleted the constant and put the value back. A reader would have
learned two false things from a file that still looked current.

Read `references/register.md` when the repository keeps a register, for the entry
format and the supersession rule. Skip it when there is none, and create one at
step 8.

**Done when** every glossary entry has been checked against this diff, and you
can name the ones it contradicts, even if that list is empty.

## 3. Dispatch the fresh reader

Spawn one subagent to write the lesson. Hand it the raw material and let it form
its own account:

- the PR number, title and body
- the diff range, and the command that produces it
- the repository's own conventions file
- the register, if there is one
- this file, and `references/writing.md`, `references/widgets.md`,
  `references/register.md`

Hand over raw inputs only. A summary from you carries the exact framing you
spawned a second reader to escape, and you would not notice it happening.

Ask it to list every claim it took from the PR description but could not confirm
in the diff. What somebody says a change does and what it does are two claims,
and a lesson keeps them apart.

**Done when** the fresh reader returns a lesson file plus that list of
unconfirmed claims.

## 4. Build it as one arc

Four jobs, in this order, as one flowing piece rather than four sections.

1. **Locate.** Open with the problem the change solves, in a few short
   paragraphs, before naming a single file. Then a small vocabulary table. Then
   the whole job as one diagram the reader can walk.
2. **Justify.** One heading per decision, worded as a question somebody would
   really ask. Under each heading: the question in plain sentences, a widget
   answering it by hand, then the **dead end** - the first answer the author
   tried and the evidence that killed it.
3. **Operate.** What somebody needs to know to make the next change here.
4. **Judge.** What would make this change wrong, built as retrieval practice so
   the reader commits to an answer before seeing yours.

The dead end is the most instructive thing in the lesson, and it is the part
authors leave out. It is usually the answer your reader would have picked,
because it was the obvious one.

Here is the shape of one Justify heading:

> ### Why is the spacing computed before anything is written?
>
> [widget: drag the paragraph, watch the fit verdict flip]
>
> The first attempt computed it in the writer, where the value was already
> needed. That shipped a box whose contents overflowed it, because the check and
> the file disagreed by 12 points and each half was self-consistent.

Close by naming what the change deletes. A change that only adds is worth less
than it looks, and the deletion is often the clearest statement of the point.

Length follows working memory, not diff coverage. One thing the reader genuinely
takes away beats five they skimmed.

**Done when** all four parts exist, and every Justify heading carries its widget
and its dead end. A decision with no dead end is either trivial or
under-examined, and saying which is itself teaching.

## 5. Draw it, and let them operate it

Most of a lesson is picture. Prose carries the argument joining one picture to
the next. Reach for these in order:

1. a widget the reader can operate
2. a figure, when the thing has a shape but nothing to move
3. a table, when the content is honestly just pairs
4. prose, last

Generate every picture of the system and paste in what the generator emits. A
hand-drawn topology becomes a second definition that **drifts** the moment
somebody moves a part, with nothing to announce it. Regenerated output cannot
drift.

Then prove each widget teaches the truth. A widget carries more authority than
any sentence, because the reader watched it happen, and that cuts both ways.
Pull its rule into a standalone script, feed it the widget's own data, sweep the
whole range, and read the output against every claim the prose makes.

Read `references/widgets.md` before building any of them. It carries the three
classes of visual, five widget archetypes with when to reach for each, and the
worked verification loop.

**Done when** every Justify heading has a widget, and every widget's rule has
been run outside the page with its output read.

## 6. Write it self-contained, into the repository

One HTML file named for the PR. Inline the CSS and the SVG, fetch nothing, load
no fonts. Aim for clean typography, a generous measure, and a page that prints.

Then keep it in the repository. A lesson written to a scratchpad and discarded
cannot be read by whoever joins this work next month, and the set never
accumulates into an account of the system. Measured on one repository, a lesson
runs to about 76 KB, so a hundred cost a few megabytes.

A shipped lesson stays as it was on the day it landed. The one edit it takes is
a supersession banner, added when a later lesson reverses it.

**Done when** the file renders with the network disabled.

## 7. Write it as a teacher, then run the checker

Your reader built this system and knows it better than you do. What they do not
know is this change, and that is the whole gap. Write for the person meeting it
for the first time, because writing for the expert they are produces a document
they cannot read.

Read `references/writing.md` before drafting. It carries every rule with the
draft that failed without it, and the checker below enforces a subset of them.
The two habits that decide most of the quality: teach an idea before naming it,
and put the join at the front of the next sentence rather than chopping a long
one in half.

    python scripts/lesson_lint.py <lesson.html> [--glossary <register.md>]

It reads those rules so they cannot rot, and it parses every inline script, so a
widget that cannot run is caught here.

    python scripts/ai_tells.py <lesson.html> <a file a person wrote>

That one counts the documented signatures of unedited model prose, and it has no
pass mark on purpose. Read it beside writing you know a person produced, because
a count with no human reference tells you the prose changed rather than improved.

Watch the rhythm figure hardest. Uniform sentence length is the signature word
choice cannot disguise, and human technical prose sits near 0.76 to 0.81. If your
draft is well under that, you have written to a limit rather than to a reader.

Whether a widget teaches the truth is step 5's job, and no checker can take it.

**Done when** `lesson_lint.py` exits 0 and you have read the tells report.

## 8. Record what it taught

Add one register entry naming the file, the range, the parts of the system the
change reaches, and any earlier lesson it reverses. Then the prose: say what the
lesson taught, rather than what the PR did.

Add the terms this lesson introduced to the glossary, defining what each term is
rather than how to use it. A wrong entry gets revised where it stands, since a
glossary is a definition and not a record.

    python scripts/lesson_lint.py --register <register.md>

That checks the rules no repository can opt out of: every lesson file has an
entry, every entry names a file that exists, every `reverses:` resolves, and a
reversed lesson carries both the `superseded-by:` field and the banner. Whether
a `parts:` value names something real is your repository's own checker's job.

**Done when** that command exits 0.

## What this procedure cannot do

Say these out loud when they bite, rather than working around them quietly.

- The register records what was taught, never what the reader retained. Asking
  them is the only way to learn the second thing.
- The lesson teaches the range it was given, and review can change a PR
  afterwards. Nothing regenerates it. A later lesson teaches the delta and names
  what it reverses.
- The checker counts sentences, not teaching. Two drafts passed it cleanly and
  taught nothing. The `evals/` suite in this plugin measures the other thing, by
  examining a reader rather than re-reading the rules.
- Your fresh reader is fresh but not independent. It sees the same diff the
  author wrote, so reasoning that never reached the tree stays invisible.
