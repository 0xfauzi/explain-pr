# Build mode

For a task the learner wants to learn from. The build still comes first: two
checkpoints, everything else optional.

Copy this checklist and track it:

```
Build mode:
- [ ] 1. Confirm the task is learning-critical
- [ ] 2. Attempt first: one question before any design is shown (required)
- [ ] 3. Optional: offer the learner the critical piece
- [ ] 4. Build; optional: offer the first diagnosis of a bug
- [ ] 5. Explain-back once it works (required, short)
- [ ] 6. Record topics
```

Steps 2 and 5 are the two checkpoints. If the learner is not in the
conversation, post the question instead of asking it and keep building; grade
it from `inbox` at the next checkpoint (`room.md`). Prefer asking the step 2
question in chat when they are present, since it only works as a prediction if
it is answered before they see the change.

 Steps 3 and 4 are single one-line offers;
skip them when the learner is working remotely, has said they are busy, or has
declined an offer earlier in the task.

**1. Confirm the task is learning-critical.** Either the learner said so, or the
task touches a dimension where `map` shows little evidence. In the second case,
propose it once in one line ("This touches concurrency, where the record is
thin. Make it a learning task?"). If they decline, build normally and stop here.

**2. Attempt first.** Before showing a design, ask one question that makes the
learner commit: sketch the approach, name the invariant that must hold, or
predict where it will break. Do not walk through the relevant code first: point
to the files and let the learner read them, because a walkthrough is a hint
(H1 or H2) given before the attempt. Add the topic if it is new (`topic add`), then
`ask` with kind `attempt`. A wrong attempt is expected and useful; it sets up
the explanation. After grading, give the design and say where it differs from
theirs and why.

**3. Optional: offer the critical piece.** If there is a small piece on the
critical path that carries the concept, offer the learner the chance to write it
while Claude writes the rest. Review their code as a peer would. If they decline,
Claude writes it.

**4. Build, and optionally offer the first diagnosis.** When a bug or failing
test appears that bears on the topic, show the symptom and ask in one line
whether the learner wants to diagnose it first. If yes, run it as a `diagnosis`
attempt with the hint ladder. If no, or for bugs unrelated to the topic, fix it
and carry on.

**5. Explain-back.** Once the change works, ask the learner to explain the
mechanism that makes it correct, or what change would break it. Use kind
`explain-back`. Do not summarise the change first; the learner's explanation
comes before Claude's. If their answer shows a gap, correct it in chat. Offer an
explainer page only under the conditions in `SKILL.md` ("Choose the mode").

**6. Record topics.** Keep one to three topics per task: the concepts worth
having in a month. Each one needs a `--concept` a stranger could understand and
`--anchor` paths to the code that embodies it. Topics are scheduled
automatically.
