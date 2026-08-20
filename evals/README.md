# What we measure, and what we cannot

The goal is that a person understands something they did not understand before.

That is the hard part to say honestly: **we cannot measure it.** Understanding
happens inside a particular person, and whether it happened depends on what they
already knew, what they needed it for, and whether they were tired when they read
it, none of which any number here can see. So anybody telling you their writing
tool is measured has picked a proxy and stopped mentioning the gap.

So here is the gap, stated plainly, and the four things that can actually be
measured, ordered by how close each gets to the thing we want.

## 1. Does a reader end up knowing more? The closest we get

    python skills/explain-pr/scripts/comprehension.py exam.toml draft-a.md draft-b.md

A reader is put in an empty directory with one document and no access to the
subject. It answers questions written from the primary source. A separate judge
scores the answers without knowing which document produced them. A control arm
with an empty packet runs automatically, so you can see how much the reader knew
already.

This is the only measurement here aimed at the real goal, and it is still a proxy,
because the reader is a model standing in for a person and that substitution has
never been validated by anybody. Use it to compare two drafts of one thing. Do not
use it to certify that a document is good.

One rule decides whether it means anything: **write the answer key from the
source before you open the document you are testing.** A key taken from the
document scores the document against itself. `comprehension/example-exam.toml`
shows the shape.

What it found on the one real case we ran: a shipped lesson scored 10 of 16 while
the raw diff of the same change scored 14. Grepping the lesson afterwards showed
it never named the two fields the change was actually about. That is the kind of
thing this catches and nothing else here does.

## 2. Does the writing follow its own rules?

    python skills/explain-pr/scripts/lesson_lint.py <document> [--glossary <register.md>]
    python skills/explain-pr/scripts/lesson_lint.py --register <register.md>

Sentence and paragraph length, forbidden characters, banned aliases from your
glossary, and whether every inline script parses. The register mode checks that
every lesson has an entry, every entry names a real file, and every reversal is
recorded at both ends.

**This is circular and worth having anyway.** The rules and the checker come from
the same place, so passing only means the document agrees with itself, and yet it
still catches real defects: a widget that cannot run, a superseded lesson with no
banner. What it cannot do is tell you whether anybody learned anything. The
document that scored 10 of 16 above passed it with zero findings.

The three supersession rules were mutation-tested: break each one and the checker
fires, restore it and it passes.

## 3. Does the skill fire when it should?

    claude plugin eval .

Two cases: does `explain-pr` trigger when somebody asks to understand a pull
request, and does it stay quiet when they ask for a defect review. Discovery only,
but discovery decides everything else, because a skill nobody reaches is worth
nothing and a skill that fires on everything is worse than nothing.

Measured by hand on Opus in a repository with real PRs: 5 of 6, with all three
near-miss negatives correctly staying quiet. `claude plugin eval` itself is in
early access and may not be enabled on your account.

## 4. Does the prose carry machine signatures? A diagnostic, never a target

    python skills/explain-pr/scripts/ai_tells.py <document> <something a person wrote>

Counts documented signatures of unedited model prose: era-stratified vocabulary,
negative parallelism, unearned rule-of-three, significance inflation, and the
spread of sentence length. Sources are named in the script.

**Read this next part before using it.** A forty-line script that welds sentences
together with ", and" beats this measure by more than any writing advice does,
while producing run-ons nobody would read. So it can diagnose a flat draft. It
can never be a target, and anything trained or tuned to maximise it will find the
welding trick before it finds good writing.

It is also register-specific, because human specifications vary hugely in sentence
length while good essayists often do not, so a number that means something for a
manual means nothing at all for an essay. The separation we measured also depends
on a preprocessing choice we did not originally disclose. Strip document furniture
like "Table of Contents" and it holds. Drop every sentence under eight words
instead and it collapses to chance.

Pass a document you know a person wrote, so the number has a scale.

## What we tried and gave up on

`research/` has the full record, including a pre-registered design and the results
that killed most of it. The short version, because the failures cost more to find
than they cost to read:

- **Rewriting a draft to sound more human**: rejected. Across four sources and
  three revisers, twelve rewrites, the median change made the rhythm worse.
- **Writing it several times and keeping the best**: rejected. The best of eight
  drafts fell well short of the human range.
- **Perplexity as a provenance signal**: rejected. It tracks how ordinary and how
  widely published the text is. A hand-written file scored the most machine-like
  of anything measured.
- **Revision by a different model family**: rejected. That family writes flatter
  prose than this one.
- **Fine-tuning a local model**: not attempted. An independent review returned a
  no-go, principally because the measure it would optimise is the gameable one
  above.

The workstream is closed. What survives is the writing style, the skill, and the
four measurements on this page with their limits attached.
