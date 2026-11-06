# learning-while-building

[![tests](https://github.com/0xfauzi/explain-pr/actions/workflows/tests.yml/badge.svg)](https://github.com/0xfauzi/explain-pr/actions/workflows/tests.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An Agent Skill for building a real project with an AI agent while getting
better as an engineer, rather than only faster.

The agent still does most of the building. At a few chosen points the skill
makes you do the thinking: commit to a design before seeing one, diagnose a bug
before the agent fixes it, explain a change back once it works. Topics come
back on a spaced schedule, with new cases rather than repeats, and a record in
your repository keeps what you showed you could do without help.

**Site and full rationale:** https://0xfauzi.github.io/explain-pr/

## Quick start

In Claude Code:

    /plugin marketplace add 0xfauzi/explain-pr
    /plugin install learning-while-building@learning-while-building

Then, in your project, say "make this a learning task", "quiz me", "help me
understand what PR 128 did", or "what am I weak at". The first run creates a
`.learning/` folder in the repository; commit it.

Other harnesses that support the Agent Skills format can use
`skills/learning-while-building/` directly. The skill needs only a shell,
Python 3.9 or later, and git.

## How it works

| You say | What happens |
|---|---|
| "Make this a learning task" | You sketch the design or name the invariant first. The agent builds, then asks you to explain the result. Writing the critical piece or diagnosing a bug first are offered once, never forced. |
| "Help me understand PR 128" | You explain or predict first. The agent reads the diff, separates what the description claims from what the code does, and explains only what you missed. |
| "Quiz me" | Due topics come back in one batch, mixed across dimensions: recall first, then new cases. |
| "Give me a debugging drill" | The agent breaks one thing in a throwaway worktree and shows you only the failing output. |
| "What am I weak at?" | Per-dimension evidence, misconceptions you held with high confidence, and how the schedule is holding. |
| Nothing, while you're away | The agent posts a question and keeps building. You answer later in chat, in a terminal (`learning.py answer`) or on the learning room page (`learning.py serve`); the next checkpoint grades it. |

Saying "skip" or "just do it" always works.

Every question follows the same rules: the expected answer is written from the
code before you see the question, you give a confidence with each answer, your
answer locks before any feedback, and feedback says what held, what didn't and
where in the code to look, without praise.

## Why it is built this way

How people use AI decides whether they learn. In Anthropic's randomised study
of developers learning a new library, the AI-assisted group scored 50% on a
follow-up quiz against 67% for people coding by hand, and the gap was largest
on debugging. Developers who asked conceptual questions, or questioned the code
they generated, kept their scores; those who delegated fully or let the AI
debug lost the most
([Shen and Tamkin, 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)).
The skill is built around the patterns that kept learning intact, plus
well-replicated findings on retrieval practice, spacing, prediction before
instruction and feedback. The site lists each rule with its source.

Most of those studies used students or junior developers on short tasks. Treat
the design as a hypothesis to test on yourself; the record is built to let you
do that.

## What's in the repository

| Path | Contents |
|---|---|
| `skills/learning-while-building/` | The skill: instructions, per-mode references, scripts and page templates |
| `output-styles/Human-Outward.md` | The writing style the skill's voice follows; selectable on its own |
| `tests/` | Behaviour tests for the scripts |
| `docs/` | The project site |

## Limits

- Grading is the agent's judgement against a rubric it wrote. Treat the record
  as evidence, not a certificate.
- Nothing reminds you. Reviews happen when you run the skill.
- The review intervals (1, then 3, 7, 21, 60 and 180 days) are starting values;
  `map` shows how well they fit you.
- Cost was measured once per practice mode, with a simulated learner. Batching
  cut model requests from 21 to 11; see the site for the numbers.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes are listed in
[CHANGELOG.md](CHANGELOG.md).

## Licence

MIT. See [LICENSE](LICENSE).
