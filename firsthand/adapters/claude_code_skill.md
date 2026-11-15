---
name: firsthand
description: Applies when a message, a hook line or added context starts with "Firsthand" or "Done when:". Firsthand is a tool on this computer that sometimes asks the person one short question about the work (a finished change, a failing test, or the check for a task that is starting) and checks the answer with a real test run. This skill says how to pass its lines on unchanged and what never to do for the person.
user-invocable: false
---

# Firsthand

Firsthand asks the person, not you. These rules keep its lines intact and keep the person's answers their own.

## Lines to print

A block that starts with this line is followed by lines to print to the person exactly as they are, with nothing added, removed or reworded:

Firsthand result for the reply above. The firsthand skill prints these lines unchanged:

Print every line after it in order, then carry on with the work.

## Findings

A line that starts `Firsthand finding:` is a fact about the work in progress, found by a test run. Use it in the work. Do not print it as your own claim about the person.

## Done when

A line that starts `Done when:` is the person's own reply to a Firsthand question, passed on as written. It names the check that shows the task is done. Treat it as the person's request: write that check as a failing test first, then make it pass.

## Commands

If the person types a `firsthand ...` command as a message, run it in the shell and print its output unchanged. The command is not on the shell's PATH: run `FIRSTHAND_COMMAND` in place of `firsthand`, with the same words after it.

## Skip

"skip" is final. Do not ask why and do not bring the question back.

## Never

- Never answer a Firsthand question for the person.
- Never run `firsthand answer` unless the person typed the answer.
- Never read anything under `~/.firsthand`.
