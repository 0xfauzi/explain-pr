# Studying a change that already exists

Use this for a pull request, a commit range, or work Claude and the learner just
finished. The learner explains or predicts first, then Claude fills the gaps.

```
Study a change:
- [ ] 1. Fix the exact range
- [ ] 2. The learner goes first
- [ ] 3. Read the change and separate claims from code
- [ ] 4. Explain only what the learner missed
- [ ] 5. One question the change did not answer
- [ ] 6. Record topics
```

## 1. Fix the exact range

For a pull request:

    gh pr view <n> --json number,title,body,baseRefName,headRefName,state,mergeCommit

- **Open PR:** `git fetch origin <baseRefName> <headRefName>`, then diff
  `$(git merge-base origin/<baseRefName> origin/<headRefName>)..origin/<headRefName>`.
  Diff against the PR's own base, not the default branch: a stacked PR diffed
  against `main` includes its parent's changes.
- **Merged PR:** use `gh pr diff <n>`. After a merge, `git merge-base` returns the
  head commit and the diff comes back empty.
- **No `gh`, or the branch was deleted:** for a merged PR, diff the merge commit
  against its first parent (`git diff <mergeCommit>^1 <mergeCommit>`). For a
  squash merge, the squash commit alone is the change. If neither can be found,
  tell the learner what is missing rather than guessing a range.

Read files from the remote ref (`git show origin/<headRefName>:<path>`), not from
the working tree, which may hold uncommitted edits.

For work just finished in this session, the range is the commits made for it, or
the uncommitted diff.

Done when you can state the base and head commits and the diff is non-empty.

## 2. The learner goes first

Before showing any explanation:

- **The learner built it, or watched Claude build it:** ask an `explain-back`
  question. "In your own words, what does this change make true that was not
  true before, and which part of the code enforces it?"
- **Someone else built it:** show only the title and the list of changed files,
  and ask an `attempt` question. "From the title and these files, what problem do
  you expect this solves, and where would you expect the core of the fix to be?"

Add the topic first if needed (`topic add`), then `ask`, and wait for the answer.

## 3. Read the change and separate claims from code

Read the full diff and the PR description. Keep two lists:

- what the code does, confirmed in the diff, with `path:line`
- what the description claims and the diff does not confirm, such as "fixes the
  race" with no test that exercises the race

Look for a rejected alternative in the PR discussion, review comments and commit
history. Only report one that is evidenced there. If none is recorded, say so.

If tests exist for the claimed behaviour, run them and report the result. If not,
say the behaviour is untested.

## 4. Explain only what the learner missed

Grade the learner's answer against the rubric, then explain, in this order,
skipping anything they already had right:

1. The problem the change solves, in one or two sentences.
2. The mechanism that makes it work, with a short code excerpt.
3. The evidenced rejected alternative, if any, and why it lost.
4. The claims from step 3 that the code does not back up.
5. What would make this change wrong: the assumption it depends on.

Keep it conversational and short. A long explanation read passively teaches less
than the learner's own attempt plus targeted correction.

## 5. One question the change did not answer

Ask one `transfer` question: a case the change and the explanation did not
cover, built as described in `questions.md`. Grade it.

## 6. Record topics

Add one to three topics, anchored to the files that embody each concept.
