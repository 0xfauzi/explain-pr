# learning-while-building

[![tests](https://github.com/0xfauzi/explain-pr/actions/workflows/tests.yml/badge.svg)](https://github.com/0xfauzi/explain-pr/actions/workflows/tests.yml)
[![license: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

An Agent Skill for building a real project with an AI agent while getting
better as an engineer, rather than only faster.

The agent still does most of the building. At a few chosen points the skill
makes you do the thinking: commit to a design before seeing one, diagnose a bug
before the agent fixes it, explain a change back once it works. Topics come
back on a spaced schedule, with new cases rather than repeats, and a record on
your machine, outside your repository, keeps what you showed you could do
without help.

**Site:** https://0xfauzi.github.io/explain-pr/

## Quick start

In Claude Code:

    /plugin marketplace add 0xfauzi/explain-pr
    /plugin install learning-while-building@learning-while-building

Then, in your project, say "make this a learning task", "quiz me", "help me
understand what PR 128 did", or "what am I weak at". The first run creates a
record in `~/.learning-while-building/`, outside your repository. Nothing is
added to your project.

Other harnesses that support the Agent Skills format can use
`skills/learning-while-building/` directly. The skill needs only a shell,
Python 3.10 or later, and git.

## If you used an earlier version

Versions before 0.6.0 kept the record in a `.learning/` folder in the project
and said to commit it. That folder holds every answer you got wrong, so anyone
who can read the repository can read it. The skill still reads it, and says so
after each write. To move it out, say "move my learning record out of the
project", or run `learning.py move` from the project root yourself (the script
is in the skill's `scripts/` folder).

`move` copies the record to `~/.learning-while-building/` and changes nothing
in your project. It then prints how to remove the old folder and, if it was
committed, what that does not undo: copies stay in git history, on any remote
and in any clone.

In a cloud session the record is lost when the session ends. Before you finish,
run `learning.py export` and paste its output into
`learning.py import-bundle -` on your own machine.

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
instruction and feedback. The research behind each rule, with its sources, is in
[design/learning-experience/research/learning-science.md](design/learning-experience/research/learning-science.md).

Most of those studies used students or junior developers on short tasks. Treat
the design as a hypothesis to test on yourself; the record is built to let you
do that.

## What's in the repository

| Path | Contents |
|---|---|
| `skills/learning-while-building/` | The skill: instructions, per-mode references, scripts and page templates |
| `output-styles/Human-Outward.md` | The writing style the skill's voice follows; selectable on its own |
| `firsthand/` | The Firsthand preview package (see below) |
| `tests/` | Behaviour tests for the scripts and for `firsthand/` |
| `docs/` | The project site |

## Limits

- Grading is the agent's judgement against a rubric it wrote. Treat the record
  as evidence, not a certificate.
- Nothing reminds you. Reviews happen when you run the skill.
- The review intervals (1, then 3, 7, 21, 60 and 180 days) are starting values;
  `map` shows how well they fit you.
- Cost was measured once per practice mode, with a simulated learner. Batching
  cut model requests from 21 to 11.

## Firsthand preview

`firsthand/` is an early preview of Firsthand, a separate tool from the skill
above. It is not published on PyPI, and the name is a working name.
It needs Python 3.11 or later, git, a POSIX system (Linux or macOS) and Claude
Code, and uv for the one-line install. Design: `design/product/PRODUCT.md`.

What works in this preview (build steps 2a, 2b and 2c): three kinds of question
in Claude Code on a pytest project. Each is checked by a real test run in a
scratch copy, never by a model.

- **Revert test.** When the agent finishes a change that adds or edits tests:
  which new test would still pass with the change undone? The change is undone
  in a scratch copy, the tests are kept and run.
- **Call it.** When a pasted failure arrives, or a turn ends with an existing
  test still failing: before any fix, where is the cause? Once the test passes
  again, the result shows where the fix landed and whether undoing the fix
  brings the failure back. A fix that only adds a sleep, a broad `except`, a
  skip or a loosened assertion is not scored.
- **Brief.** When a task starts that touches two or more kinds of file and the
  prompt names no test: name one check that fails now and will pass when this
  is done. Your line goes to the agent as "Done when: ... Write this check as a
  failing test first." When the agent finishes, Firsthand shows the first test
  it added ("Is this your check?") and, on yes, runs it with the change and
  with the change undone.

The question appears as one line at the turn end. You answer with a reply in
the chat, in the Room (a local page at 127.0.0.1), or with `firsthand answer`.
It asks at most once a day by default, across all three, and never on the first
prompt of the day. "skip" is final. Everything is recorded in
`~/.firsthand/record`, a local git repo with no remote. It never writes to your
project.

Not in this preview: the other moments, reviews, drills, the phone, other
coding agents, and test runners other than pytest (the Revert test checks other
test commands by exit code only; Call it and the Brief need pytest).

Install from the git repository with uv. Run it from inside the project you
want watched: a git repo with at least one commit.

```sh
cd ~/your-project
uvx --from git+https://github.com/0xfauzi/explain-pr firsthand init
```

Without uv, install from a clone:

```sh
git clone https://github.com/0xfauzi/explain-pr ~/src/explain-pr
cd ~/your-project
PYTHONPATH=~/src/explain-pr python3 -m firsthand init
```

`init` shows the two files it will write (`~/.claude/settings.json` gets six
hooks, and `~/.claude/skills/firsthand/SKILL.md`), backs them up, and copies the
engine to `~/.firsthand/engine/`, so the clone can be moved or deleted
afterwards. Neither install puts anything on your PATH: the command is
`~/.firsthand/engine/0.1.0/bin/firsthand`, and `init` prints it at the end. Add
that folder to your PATH to type `firsthand`, or run `pip install
~/src/explain-pr`, which also gives a `firsthand` command.

Commands: `firsthand status`, `firsthand room`, `firsthand answer <reply>`,
`firsthand skip`, `firsthand journal`, `firsthand skills`, `firsthand quiet`,
`firsthand off`, `firsthand on`,
`firsthand config test-command "<cmd>"`, and `firsthand uninstall`, which
restores the backed-up files and keeps the record.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes are listed in
[CHANGELOG.md](CHANGELOG.md).

## Licence

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
