# learning-while-building

A Claude Code skill for building a real project with Claude while getting better
as an engineer, rather than only getting faster.

Claude still does most of the building. At a few chosen points the skill makes
you do the thinking: commit to a design before seeing one, diagnose a bug before
Claude fixes it, explain a change back once it works. It then brings topics back
on a spaced schedule, with new cases rather than repeats, and keeps a record of
what you showed you could do without help, split by engineering dimension.

## Install

    /plugin marketplace add 0xfauzi/explain-pr
    /plugin install learning-while-building@learning-while-building

Then, in a project repository:

    /learning-while-building:learning-while-building

or just say "make this a learning task", "quiz me", "help me understand what PR
128 did", or "what am I weak at".

The first run creates `.learning/` in the repository. Commit it. Cloud session
containers are reclaimed, and an uncommitted record goes with them.

## What it does

| You say | What happens |
|---|---|
| "Make this a learning task" | You sketch the design or name the invariant first. Claude builds, offers you the critical piece to write, offers you first go at any bug, then asks you to explain the result. |
| "Help me understand PR 128" | You explain or predict first. Claude reads the diff, separates what the description claims from what the code does, and explains only what you missed. Then one question the PR did not answer. |
| "Quiz me" | Due topics come back, mixed across dimensions. Retrieval first, then new cases. |
| "Give me a debugging drill" | Claude breaks one thing in a throwaway worktree and shows you only the failing output. |
| "What am I weak at?" | Per-dimension evidence, misconceptions you held with high confidence, and how well the schedule is holding. |

Saying "skip" or "just do it" always works.

## Why it is built this way

Each rule traces to a finding. Most of these studies used other populations
(students, junior developers, short tasks), so the design is a hypothesis to
test on yourself, not a proven method.

- **How you use AI matters more than whether you use it.** In Anthropic's
  randomised study of 52 developers learning a new library
  ([Shen and Tamkin, 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)),
  the AI group scored 50% on a follow-up quiz against 67% for the hand-coding
  group, with the largest gap on debugging. The patterns that kept scores high
  were asking conceptual questions, and generating code and then questioning it.
  The patterns that lost the most were full delegation and letting AI do the
  debugging (24%). So the skill answers conceptual questions freely, makes you
  explain generated code back, and gives you first go at bugs.
- **Unguarded help raises practice scores and lowers later unaided ones.**
  [Bastani et al., 2025](https://doi.org/10.1073/pnas.2422633122) found students
  with plain ChatGPT did 17% worse once it was removed, while a tutor that gave
  hints rather than answers removed most of the harm. Hence the hint ladder, and
  the rule that a question and its answer never share a message.
- **Attempting before instruction helps understanding and transfer**
  ([Kapur, 2014](https://doi.org/10.1111/cogs.12107)), and producing an answer
  beats reading one. Hence attempt-first, explain-back, and you writing the
  critical piece when you choose to.
- **Retrieval, spaced out, is what makes things stick**
  ([Roediger and Karpicke, 2006](https://doi.org/10.1111/j.1467-9280.2006.01693.x);
  [Cepeda et al., 2008](https://doi.org/10.1111/j.1467-9280.2008.02209.x)), and it
  transfers better to new cases when feedback explains why
  ([Pan and Rickard, 2018](https://doi.org/10.1037/bul0000151)). Hence scheduled
  reviews that move from recall to new cases, with feedback citing the code.
- **Feeling that you understood is a poor guide to whether you did**
  ([Deslauriers et al., 2019](https://doi.org/10.1073/pnas.1821936116)). Hence
  confidence is recorded beside every answer, and confident wrong answers are
  surfaced as misconceptions.
- **Guidance that helps a novice can slow down someone experienced**
  ([Kalyuga, 2007](https://doi.org/10.1007/s10648-007-9054-3)). Hence the hint
  ladder starts at nothing, and one interruption per task at most.

## What changed from explain-pr, and why

This repository used to ship `explain-pr`, which turned a pull request into an
interactive HTML lesson, plus a writing style and four prose checkers. A
proposal suggested keeping all of that and adding a learning layer beside it.
That proposal was reviewed, and most of it was not adopted:

- **Kept:** attempt before explanation, the hint ladder, grading that separates
  unassisted from assisted answers, transfer questions on new cases, repair
  drills, separating what a PR claims from what the code shows, and the PR range
  handling for stacked and merged PRs.
- **Dropped: Claude writing polished lessons for you to read.** Reading a good
  explanation is the passive pattern the research above warns about, and
  fluency of the page is what makes it feel learned. Your attempt plus targeted
  correction does the work instead.
- **Dropped:** HTML widgets, the lesson register, the prose checkers, the output
  style, mobile briefs and evidence packets. They measured or improved the
  document, and the target is you.
- **Added, not in the proposal:** engineering dimensions, so practice targets
  where your record is thin; confidence capture; a rubric fixed before each
  question, so grading cannot drift toward whatever you said; mixing dimensions
  within a session; and field evidence, for when you solve something alone.
- **Evaluations:** none ship. The real outcome is your capability, which no
  automated check here can measure. Note that this departs from Anthropic's skill
  guidance, which asks for at least three behavioural evaluations of the skill
  itself (does Claude stop after asking, does it stay quiet on routine work).
  Those are measurable and could be added later.

The old files are in the git history.

## What it cannot do

- Grading is Claude's judgement against a rubric Claude wrote. Treat the record
  as evidence, not a certificate.
- Nothing reminds you. Reviews happen when you run the skill.
- The review intervals (1, then 3, 7, 21, 60 and 180 days) are starting values.
  `map` prints the success rate at each step, so after a few weeks your own data
  says whether they fit you.

## Licence

MIT. See `LICENSE`.
