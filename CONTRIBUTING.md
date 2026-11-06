# Contributing

Thanks for helping. This plugin is small, and changes are easiest to review
when they stay small too.

## Before you start

Open an issue first for anything beyond a fix or a wording change. The skill's
design rests on specific learning research (see the README), so a proposal that
changes how questions are asked, graded or scheduled should say which finding
it relies on, or what it measured.

## Layout

| Path | What it is |
|---|---|
| `skills/learning-while-building/SKILL.md` | The skill's instructions; kept under 500 lines |
| `skills/learning-while-building/references/` | Per-mode guidance the skill reads when needed |
| `skills/learning-while-building/scripts/` | `learning.py` (the record), `room.py` (posted questions and the page server), the explainer checkers |
| `skills/learning-while-building/assets/` | The learning room page and the explainer template |
| `output-styles/Human-Outward.md` | The writing style the skill's voice follows |
| `tests/` | Behaviour tests for the scripts |
| `docs/` | The project site, served by GitHub Pages |

## Checks

The scripts use only the Python standard library and support Python 3.9 and
later.

    python3 -m unittest discover -s tests

The tests drive the real scripts against temporary records; nothing is mocked.
Add a test for any behaviour you change.

The repository also runs a shared pre-commit configuration (linting,
formatting, complexity and file-length limits, secret scanning):

    pip install pre-commit
    pre-commit run --all-files

## Writing

Text the skill shows a learner follows the Voice section of `SKILL.md`: plain
words, the outcome first, evidence with `path:line`, and no praise. Documents
in this repository follow the same style.

## Measuring claims

If a change claims to save cost or improve learning, include how you measured
it. "This needs to be measured" is a fine thing to write; a guessed number is
not.
