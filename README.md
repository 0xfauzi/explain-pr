# explain-pr

Tools for writing so that a person understands.

Not so that it sounds human, which is a different thing and a trap. The goal is
that somebody finishes reading and knows something they did not know before.

## What is here

**`Human-Outward`**, a writing style. Simple words and varied sentences, the idea
before its name, the answer you rejected shown, a clear mark on how each claim is
known, and kindness that is not performed. It applies to anything you write: an
essay, a letter, a document, an explanation of your own work.

**`explain-pr`**, a skill that applies those rules to one job. It turns a pull
request into a lesson somebody can read in a sitting, with widgets they can
operate, kept in the repository so the next person finds it.

**Four checkers**, each with its limits written down, in `evals/README.md`.

The style is the general case. The skill is one application of it. If you only
want one thing, take the style.

## Install

    /plugin marketplace add 0xfauzi/explain-pr
    /plugin install explain-pr@explain-pr

Turn the style on:

    /output-style explain-pr:Human-Outward

Use the skill, in a repository with an open or merged pull request:

    /explain-pr:explain-pr 128

Both are namespaced by the plugin. A bare `Human-Outward` will find a local style
of that name first, if you have one.

## The style, in one screen

- **Say why it matters** before any name, number or detail.
- **Teach the idea, then name it.** The word should be a label for something the
  reader is already holding.
- **Assume no context and full capability.** They know none of your background
  and can follow anything once you hand it over. Explaining is kind. Talking down
  is not.
- **Show the answer you rejected**, with the evidence that killed it. This is the
  most useful thing you will write and the thing people leave out.
- **Say how you know**, every time: measured, reasoned, judged, or unknown.
- **Simple words, varied sentences.** These are separate dials and most people
  turn down both. Turn down the first one only.
- **Be kind and mean it.** Cut the words that blame the reader. Say the hard thing
  and aim it at the work. Never leave a reader stuck.

Full text in `output-styles/Human-Outward.md`.

## The skill, in one screen

1. **Fix the diff range against the PR's own base**, not the default branch.
   Stacked and merged PRs each get this wrong by default, in opposite directions,
   and both mistakes are silent.
2. **Hand the writing to a reader who did not make the change.** An author
   explains a change as they meant it, and cannot see the reasoning that never
   reached the diff.
3. **Build one arc**: where this sits, why each decision went that way, what you
   need for the next change, and what would make it wrong.
4. **Prefer a widget the reader can operate** over a picture of a rule. A picture
   states the rule. It does not let anybody try it and be surprised.
5. **Record what it taught**, so the set becomes an account of the system rather
   than a pile of files.

`skills/explain-pr/SKILL.md` is the procedure. `references/` holds the writing
rules with the draft that failed without each one, a guide to what to draw, and
the register format.

## About measurement, honestly

We cannot measure whether you understood something. That happens inside you, and
it depends on what you already knew and what you needed it for.

So every number here is a proxy, and `evals/README.md` says how far each one falls
short. The closest is `comprehension.py`, which examines a reader who has only the
document and no access to its subject. It is the only measurement aimed at the
real goal, and it still substitutes a model for a person.

One warning worth repeating from that page. The prose meter, `ai_tells.py`, is a
diagnostic and never a target. A short script that welds sentences together beats
it more thoroughly than any writing advice does, while producing text nobody would
want to read.

A long research programme tried to make generated prose measurably human and
mostly failed. `research/` has the record, including everything that did not work
and the two findings that qualify the ones that did. It is closed now, and it is
kept because the failures cost far more to find than they cost to read.

## Licence

MIT. See `LICENSE`.
