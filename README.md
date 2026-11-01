# learning-while-building

A Claude Code skill for building a real project with Claude while getting better
as an engineer, rather than only getting faster.

Claude still does most of the building. At a few chosen points the skill makes
you do the thinking: commit to a design before seeing one, diagnose a bug before
Claude fixes it, explain a change back once it works. For mechanisms that need a
picture, it builds an interactive explainer page that will not show you an
answer until you have committed to one. It brings topics back on a spaced
schedule, with new cases rather than repeats, and keeps a record of what you
showed you could do without help, split by engineering dimension.

## Install

    /plugin marketplace add 0xfauzi/explain-pr
    /plugin install learning-while-building@learning-while-building

Then, in a project repository:

    /learning-while-building:learning-while-building

or say "make this a learning task", "quiz me", "help me understand what PR 128
did", "draw me how this works", or "what am I weak at".

The first run creates `.learning/` in the repository. Commit it. Cloud session
containers are reclaimed, and an uncommitted record goes with them.

The plugin also ships **Human-Outward**, a writing style: plain words, the idea
before its name, the real technical term once the idea is clear, honest about
what is known, and no performed warmth. The skill applies it to everything it
says to you whether or not you select it. To use it for all of Claude's writing:

    /output-style learning-while-building:Human-Outward

Requires Python 3.9+ and git. Checking explainer pages also needs node, and
Playwright for node (`npm i -g playwright`) to drive the page in a browser.

## What it does

| You say | What happens |
|---|---|
| "Make this a learning task" | You sketch the design or name the invariant first. Claude builds, offers you the critical piece to write, offers you first go at any bug, then asks you to explain the result. |
| "Help me understand PR 128" | You explain or predict first. Claude reads the diff, separates what the description claims from what the code does, and explains only what you missed. Then one question the PR did not answer. |
| "Draw me how this works" | After your attempt in chat, an explainer page aimed at what you missed: predictions first, a step-through diagram that stops before the decisive step, a simulation locked until you predict, then you explain it back. You paste your answers into the chat. |
| "Quiz me" | Due topics come back, mixed across dimensions. Recall first, then new cases. |
| "Give me a debugging drill" | Claude breaks one thing in a throwaway worktree and shows you only the failing output. |
| "What am I weak at?" | Per-dimension evidence, misconceptions you held with high confidence, and how well the schedule is holding. |

Saying "skip" or "just do it" always works.

## Why it is built this way

Each rule traces to a finding. Most of these studies used students or junior
developers on short tasks, so the design is a hypothesis to test on yourself,
not a proven method.

### Working with AI

- **How you use AI matters more than whether you use it.** In Anthropic's
  randomised study of 52 developers learning a new library
  ([Shen and Tamkin, 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)),
  the AI group scored 50% on a follow-up quiz against 67% for hand-coders, with
  the largest gap on debugging. Asking conceptual questions, and generating code
  and then questioning it, kept scores high; full delegation and letting AI
  debug lost the most (24%). So the skill answers conceptual questions freely,
  makes you explain generated code back, and gives you first go at bugs.
- **Unguarded help raises practice scores and lowers later unaided ones.**
  [Bastani et al., 2025](https://doi.org/10.1073/pnas.2422633122): students with
  plain ChatGPT did 17% worse once it was removed; a tutor that gave hints rather
  than answers removed most of the harm. Hence the hint ladder, and no question
  shares a message with its answer.

### Explainer pages and diagrams

- **Watching teaches little; predicting first does.** Students who watched
  physics demonstrations understood them no better than students who never saw
  them, while students who predicted the outcome first understood significantly
  more ([Crouch et al., 2004](https://doi.org/10.1119/1.1707018)). So every
  interaction on a page locks until you commit an answer.
- **What you do with a visualisation matters more than what it shows.** A
  meta-study of 24 algorithm-visualisation experiments found how learners used
  the visualisation predicted its effect better than its graphics
  ([Hundhausen, Douglas and Stasko, 2002](https://doi.org/10.1006/jvlc.2002.0237)).
  So pages are built from questions, with diagrams in service of them.
- **Animation helps less than it looks.** Meta-analyses find small gains over
  static pictures, d = 0.37
  ([Höffler and Leutner, 2007](https://doi.org/10.1016/j.learninstruc.2007.09.013))
  and later estimates near g = 0.23, and continuous motion is often too fast to
  follow ([Tversky et al., 2002](https://doi.org/10.1006/ijhc.2002.1017)). So
  mechanisms are discrete frames you step through at your own pace, with only the
  change between frames highlighted.
- **Multimedia design principles** ([Mayer and Fiorella, eds., Cambridge
  Handbook of Multimedia Learning, 2021](https://doi.org/10.1017/9781108894333)):
  no decoration (coherence), highlight what matters (signalling), labels on the
  parts rather than in a legend (spatial contiguity), learner-paced steps
  (segmenting), key terms before the mechanism (pre-training).
- **Guidance that helps a novice can hinder an expert**
  ([Kalyuga et al., 1998](https://doi.org/10.1518/001872098779480587);
  [Kalyuga, 2007](https://doi.org/10.1007/s10648-007-9054-3)). So pages do not
  narrate what a diagram already shows, and worked examples appear only where
  your record shows you are new to the area.

### Questions and feedback

- **Testing before teaching helps.** Pre-instruction questions improve later
  learning even when answered wrongly
  ([Pan and Carpenter, 2023](https://doi.org/10.1007/s10648-023-09814-5)). Hence
  attempt-first in chat and predictions at the top of every page.
- **Explaining to yourself helps**: a meta-analysis of 64 reports found g = 0.55
  for prompted self-explanation
  ([Bisra et al., 2018](https://doi.org/10.1007/s10648-018-9434-x)). Hence
  explain-backs, and the write-then-compare block on pages.
- **Confident errors are the ones most likely to be corrected** once feedback
  arrives ([Butterfield and Metcalfe, 2001](https://doi.org/10.1037/0278-7393.27.6.1491)),
  and felt understanding is a poor guide to real understanding
  ([Deslauriers et al., 2019](https://doi.org/10.1073/pnas.1821936116)). Hence
  confidence on every answer, and confident wrong answers surfaced as
  misconceptions to discuss.
- **Feedback works on average, but varies widely; informative feedback works
  best** ([Wisniewski et al., 2020](https://doi.org/10.3389/fpsyg.2019.03087),
  d = 0.48). Hence feedback with evidence, and on pages a separate explanation
  for each wrong option.
- **Retrieval, spaced out, makes things stick**
  ([Roediger and Karpicke, 2006](https://doi.org/10.1111/j.1467-9280.2006.01693.x);
  [Cepeda et al., 2008](https://doi.org/10.1111/j.1467-9280.2008.02209.x)), and
  transfers to new cases better with elaborated feedback
  ([Pan and Rickard, 2018](https://doi.org/10.1037/bul0000151)). Hence the review
  schedule, moving from recall to new cases.
- **Programming tasks have an order.** Tracing code and explaining it in plain
  English predicted code-writing performance
  ([Lopez et al., 2008](https://doi.org/10.1145/1404520.1404531); the strict
  hierarchy has been questioned since), and ordering tasks gave the same gains
  as writing code in less time
  ([Ericson et al., 2017](https://doi.org/10.1145/3141880.3141895)). Hence trace,
  then explain, then modify for unfamiliar code, and ordering tasks on pages.
- **Attempting before instruction helps transfer**
  ([Kapur, 2014](https://doi.org/10.1111/cogs.12107)). Hence you write the
  critical piece when you choose to.

## How the record judges evidence

- **Highest demonstrated** (not yet, with help, recalls, transfers) is the best
  answer you have ever produced in chat, graded by Claude against a rubric fixed
  before the question. It is history, not a claim about today.
- **Current evidence** reads only your latest review: holding, unverified
  (review overdue), or uncertain (the latest answer was wrong, partial or
  needed a hint). A topic that once reached "transfers" and then failed a review
  shows as uncertain.
- **Page results** are multiple choice, ordering or self-graded, which is weaker
  evidence. They are recorded and surface misconceptions, but do not raise a
  level.
- **Field work**, something you did alone in real work, counts when Claude has
  inspected an artifact of it: a commit, PR, test output or trace. Without one
  it is kept as a self-report and does not change your level.

## Several sessions, one record

Each topic and each attempt is its own file with a random id, so sessions on
different branches add different files and git merges them cleanly. A session
only sees what is on its branch; when it records something on an unmerged
branch it says so. If two branches change the same topic or grade the same
attempt, git reports a conflict and `learning.py` explains how to resolve it.
Records from version 0.2 are converted once with `learning.py migrate`.

## What changed from explain-pr

This repository used to ship `explain-pr`, which turned a pull request into a
long HTML lesson to read, plus a writing style and four prose checkers. The
current design keeps HTML pages but changes their job. Before, a page was an
explanation you read. Now it is a set of questions, each locked until you
answer, built after your own attempt and aimed at what you missed. The PR range
handling for stacked and merged PRs, separating claims from code, and sweeping
a simulation's rule outside the browser all came across. The register and prose
checkers did not; they improved the document, and the target is you. The
Human-Outward style was removed in 0.2 and restored in 0.3, with three changes:
keep the correct technical term once the idea is clear, respond to the learner's
actual reasoning, and drop the passages about measuring how human prose sounds. The old files are in the git history.

No evaluations ship. The real outcome is your capability, which nothing
automated here can measure. This departs from Anthropic's skill guidance, which
asks for at least three behavioural evaluations of the skill itself; those
would be measurable and could be added.

## What it cannot do

- Grading is Claude's judgement against a rubric Claude wrote. Treat the record
  as evidence, not a certificate.
- The page checker finds broken behaviour (answers visible early, locks that do
  not lock, network requests, layout overflow). It cannot find a simulation that
  runs correctly and teaches something false; only sweeping the rule against the
  code does that, and that step relies on Claude doing it.
- Nothing reminds you. Reviews happen when you run the skill.
- An explainer page needs a way to reach you. In a cloud session it is published
  privately when the session has a tool for that; otherwise the same questions
  run in the chat.
- The review intervals (1, then 3, 7, 21, 60 and 180 days) are starting values.
  `map` prints the success rate at each step, so your own data can say whether
  they fit you.

## Licence

MIT. See `LICENSE`.
