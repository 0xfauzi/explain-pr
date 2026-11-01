# Repair drills

A repair drill injects one realistic bug into a throwaway copy of the code and has
the learner find and fix it from the symptom. It practises diagnosis, the skill
that suffers most when Claude does the debugging.

A drill takes far longer than a question. Offer one; never start one unasked.

```
Repair drill:
- [ ] 1. Get the learner's go-ahead and pick the topic
- [ ] 2. Make a throwaway worktree
- [ ] 3. Inject one bug and confirm it shows
- [ ] 4. Record the attempt, then give the symptom only
- [ ] 5. Coach with the hint ladder
- [ ] 6. Verify the fix
- [ ] 7. Clean up and record
```

## 1. Get the go-ahead and pick the topic

Say what will happen in one line ("I will break something in a scratch copy and
show you only the failing output"). Pick a topic from the weakest dimension in
`map`, or one the learner names.

## 2. Make a throwaway worktree

Pick a name unique to this drill, then check neither the path nor the branch
exists:

    NAME=drill-<topic>-$(date +%Y%m%d-%H%M%S)
    git worktree list
    git branch --list "drill/$NAME"
    git worktree add "../$NAME" -b "drill/$NAME" HEAD

If either already exists, pick another name. Never reuse or overwrite one.

All drill work happens in that directory: the injected bug and every change the
learner makes. Never edit the learner's working tree or any shared branch, and
never push the drill branch.

## 3. Inject one bug and confirm it shows

Choose a bug that the topic's concept explains, of a kind that really happens:

- an off-by-one or inverted condition on a boundary
- a missing lock, or an operation moved outside a transaction
- a retry without an idempotency check
- an ordering change: an event emitted before the state it describes is saved
- a missing authorisation or validation check
- a cache that is never invalidated on one write path
- a test that passes without exercising the code (a false green)

Change as little as possible, ideally one line. Do not leave comments or names
that point at the change.

Then run the test or command that exposes it and keep the output. If nothing
fails, the drill has no symptom: either write a test that exposes it (and tell
the learner a test was added), or choose another bug.

## 4. Record the attempt, then give the symptom only

Run `ask` with kind `repair`. The rubric names the file, the line, the cause and
the correct fix.

Give the learner the failing output and the command that reproduces it, and the
worktree path. Do not name the file or the change. Ask for a hypothesis and a
quick way to test it before they start reading code.

## 5. Coach with the hint ladder

Answer questions about how the system works. Do not confirm or deny a guessed
location until the learner has tested it. Hints follow `questions.md`: H1 names
the kind of fault, H2 names the file or the boundary, H3 shows the change.

## 6. Verify the fix

The learner writes the fix. Run the failing test again, then the full suite. A
fix that differs from the original code is fine if the tests pass and it is
correct; review it as a peer would.

## 7. Clean up and record

First, see what is in the drill worktree:

    git -C "../$NAME" status --short
    git -C "../$NAME" diff

The learner's fix is work they did. Before removing anything, ask in one line
whether they want to keep it. Options: keep the patch as a file
(`git -C "../$NAME" diff > ../$NAME.patch`), commit it on the drill branch and
keep the branch, or discard it. The injected bug must never reach a real branch,
so a kept fix is kept as the drill's record, not applied to the project.

Once the learner has said the work is saved or disposable:

    git worktree remove "../$NAME"
    git branch -d "drill/$NAME"

Do not add `--force` or use `-D` as a shortcut. `worktree remove` refuses when
there are uncommitted changes, and `branch -d` refuses an unmerged branch; both
refusals mean work would be lost. Use the forcing form only after the learner has
explicitly said to discard that work. If a cleanup command fails, report the exact
path, the branch name and what is left, rather than retrying silently.

Grade the attempt. `--gap` records the step where the learner got stuck, for
example "read the code before forming a hypothesis" or "did not check the
transaction boundary".
