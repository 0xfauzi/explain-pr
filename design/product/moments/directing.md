# Moments: directing the work

> **Superseded.** The rules in this file (budgets, fading, scoring, levels, what counts) are replaced by `../spec/learning.md`. Several moments here were merged, renamed or cut: `../spec/learning.md` section 13 maps every name. Use this file for worked examples and wording ideas only. On-screen copy is in `../spec/experience.md`.

Skills 5, 6 and 7 from `design/skills/SKILLS.md`: framing the problem and writing the brief, delegating and supervising work, breaking work into small reversible changes.

These three skills are about directing a builder. They are practised before and during a run, where skills 1 to 3 are practised after it. That makes them the cheapest to place: the person is already deciding what to ask for, how closely to watch and how big the change should be. The tool asks them to make that decision explicit, then shows what happened.

Running example: **orbit-pay**, a payments service with a `POST /charges` endpoint, a `charges` table, a ledger, and a webhook handler for the card processor. The task used in most examples: clients retry on timeout and some customers are charged twice, so the person asks the agent to add idempotency keys.

---

## 1. What every moment here shares

### 1.1 Two kinds of input

- **Work product.** The brief, the checkpoint, the split. This is real engineering output. It goes to the agent, because the build should benefit from it.
- **Sealed call.** A prediction about what will happen: where the result will be wrong, what the builder will have to guess, whether a part can land alone. It is typed in the Room or an inline card, stored in the record before the outcome exists, and never passed to the agent. This keeps the agent from steering towards or away from it, and gives the check something fixed to compare with.

Every moment below says which kind it uses.

### 1.2 The task timeline

The engine already maps each agent's hooks to seven events: session_start, prompt_submit, before_tool, after_tool, tool_failed, turn_end, session_end (`spec/architecture.md` section 1). The moments here need one new derived object built from those events plus git: the **task timeline**.

A task starts at a prompt that begins new work and ends at merge, abandon, or a prompt that starts different work. The engine derives it, it is never committed. It holds:

| Field | Source |
| :- | :- |
| Brief, verbatim | prompt_submit hook. On surfaces without hooks, the agent relays it through the `moment` tool and the record marks it "relayed" |
| Plan steps | The agent's plan or todo tool call, read at after_tool |
| Questions the builder asked | Ask-user tool calls, and turns that end with a question |
| Correction prompts | Later prompt_submit events inside the task |
| Test runs | after_tool and tool_failed on the project's test command, with failing test ids |
| First "done" claim | turn_end whose report says the work is complete |
| Diff at each turn_end | `git diff --stat` and paths against the task's base commit |
| Rework after "done" | Lines changed between the first "done" claim and the merge commit, from `git diff --numstat` |
| Pull request events | `gh pr create` seen at before_tool, then `gh pr checks` and `gh pr view` read at the next session_start |
| Reverts | `git revert`, `git restore`, `git checkout -- <path>` or `git reset` seen at before_tool, and revert commits found in `git log` |

**Rework events** is the name used below for: a test failing after the first "done" claim, a correction prompt after it, a failed CI check on the pull request, a review comment that leads to a commit, and a revert. All five are read from the timeline. None is a model's opinion.

### 1.3 The scratch runner

Several checks apply part of a change and run the tests. The existing Runner does this in a scratch copy made from committed files plus the working diff (`spec/architecture.md` section 1). It never touches the working tree, and it runs after the turn, so the build does not wait for it. If the project has no test command the engine can run, the moment says so and falls back to the static facts named in its check, or is not asked.

### 1.4 Path categories

The engine tags changed paths by pattern: schema and migrations, money movement, auth, public interface (routes, API schema files), config and infrastructure, tests, everything else. Patterns come from a default list plus the project's own layout, and the person can correct a tag in the Room. Tags are used to pick moments and to check stakes calls. They are deliberately coarse: a tag only says "this kind of file changed".

### 1.5 Selection, and the build always winning

- At most one moment from this file per task. If two triggers fire, the engine takes the one with an executable check, then the one whose skill has gone longest without practice.
- These moments count against the same moment cap as every other in-build moment (`spec/learning.md`). This file adds triggers. It adds no extra interruptions.
- Nothing here blocks a tool call. The hook dispatcher never returns allow or deny. If the person has not answered when the agent is ready, the agent continues and the moment is recorded as skipped.
- "skip" in the agent, or one tap in the Room, always dismisses with no follow-up. The pressure rule and the quiet controls (`spec/experience.md` 3.17, 3.18) apply unchanged.
- **Matching the person.** The engine asks more where a person's past calls missed and less where they matched. When a person's last three sealed calls for a moment matched the outcome, that moment drops to its one-line form and is asked only on tasks that touch a high-stakes path category. A miss brings the full form back once.
- **Variation.** Each moment has two or three prompt forms (a free line, a pick from real options, a prediction) and the engine rotates them. The research on repeated warnings in SKILLS.md, "Rules for the practice moments", is the reason.

### 1.6 Where grading by a model is used

Most checks below are mechanical: a test run, a diff property, a count from the timeline. Where a model has to read text (for example, whether a correction was already covered by the brief), it follows `spec/learning.md` section 12: the key is real text from the timeline, each point must quote the person's words, two passes must agree, and an uncertain result is shown as uncertain and moves nothing.

### 1.7 Ideas and how they come back

Each moment records one system-level idea in the record's `ideas/`. The idea returns as a review item under the existing limits: at most 3 a day, at the existing intervals in `record.py`. The return is always in a new form: a different part of orbit-pay, a different kind of system, or the decision turned around. It never repeats the original prompt. Skills decide when the tool asks. Ideas decide what comes back.

---

## 2. Skill 5: framing the problem and writing the brief

Four moments. The first is the one to build first (section 5).

### 2.1 Brief against result

**Trigger.** prompt_submit that starts a task, where the agent's first response is a plan or todo tool call, or the first edit touches more than one path category. A one-line fix does not trigger it. SKILLS.md records the counterpoint that heavy specs are overkill for small changes, and the design follows it.

**What the person does.** About 60 to 90 seconds, before the run.

1. Work product: the brief must contain a goal, one thing that is out of scope, and how they will know it is done. If the prompt already has all three, the tool adds nothing. If one is missing, the tool asks for that one only.
2. Sealed call: one line naming what the builder will most likely have to guess.

In the agent, when the prompt has no done check:

```
Firsthand: before it starts, how will you know this is done? One line. Or "skip".
```

In the Room, the moment card:

```
BRIEF  orbit-pay  idempotency for POST /charges

Your brief
  Goal          A retried charge request never charges twice.
  Out of scope  Refunds and the webhook handler.
  Done when     [ type here ]

Sealed, not sent to the agent
  What will the builder most likely have to guess?
  [ type here ]

[ Send brief ]   [ Skip ]
```

Example answers: "Done when: two POST /charges with the same Idempotency-Key header create one row in charges and return the same charge id." Sealed call: "How long a key stays valid."

**The check.** Run at the first "done" claim, from the timeline.

- **Done check.** If the done line names something runnable (a test name, a command, a request), the engine runs it in the scratch runner at the task's base commit and at the result. It should fail before and pass after. A check that passes before the change cannot tell done from not done, and the card says so.
- **Out of scope.** The engine compares the diff's paths with the out-of-scope line. If the line names a path, module or route, this is a path match. If not, a model reads the diff summary against the line under section 1.6.
- **Guesses.** Three sources, in order of trust: questions the builder asked during the run, sentences in its reports that state an assumption ("I assumed", "since it was not specified"), and decisions in the diff that the brief does not determine. The third is extracted by a separate context and each one must cite a `file:line`. Entries whose cited line does not exist are dropped.
- **Cost.** Correction prompts and rework lines after "done", from the timeline.

**Shown afterwards.**

```
BRIEF AGAINST RESULT  idempotency for POST /charges

Done check     Failed before, passes now. It can tell done from not done.
Out of scope   Held. No changes under webhooks/ or refunds/.

The builder had to guess 3 things
  1. Keys expire after 24 hours            charges/idempotency.py:18
  2. Same key, different amount: returns the first charge, no error
                                           charges/handlers.py:52
  3. Keys are stored in a new table        migrations/0031_idempotency_keys.py:1

Your call      "How long a key stays valid."  Matched guess 1.
Not predicted  Guess 2. You corrected it in your next prompt:
               "same key with a different body must be a 422".
Cost           1 correction, 41 lines reworked after "done".
```

**Idea recorded.** "A brief must say what happens on the conflicting case, not only the happy case" with the instance: same idempotency key, different request body.

**How it comes back.** Days later, in a different part of the system, as a brief to complete: "You are about to ask for retry handling on processor webhooks in orbit-pay. Write the one line of the brief that covers the conflicting case." The key is a short list of acceptable conflicts for that surface (same event id with a different payload, events out of order), written by a separate context from the webhook code with `file:line` citations. Later still, further away: a brief for a file upload endpoint, the same question.

### 2.2 Done check first

**Trigger.** prompt_submit that asks for a behaviour change or bug fix, in a project where the engine knows the test command, and the prompt names no test, command or observable result. Used in place of 2.1 once 2.1 has faded for this person, and for smaller tasks.

**What the person does.** About 30 seconds. Work product: one line naming an observable check, sent to the agent with the brief.

```
Firsthand: name one check that fails now and will pass when this is fixed. Or "skip".
```

Example: "tests/charges/test_retry.py::test_same_key_charges_once".

**The check.** Executable. The scratch runner runs the named check at the base commit and at the result. Four outcomes, each stated plainly: fails then passes (the check works), passes then passes (it never tested the change), fails then fails (not done), or the named check did not exist at the end (the builder did not write it or renamed it). If the check is a sentence and not runnable, the engine says it could not run it and shows the tests the builder added next to the sentence. That is a comparison the person makes, not a grade.

**Shown afterwards.**

```
DONE CHECK  test_same_key_charges_once
Before the change  did not exist
After              passes
With the fix undone, test kept   fails   (the test depends on the fix)
```

The last line is the revert test from skill 1, run on the person's own named check. It is the same runner call, so the two skills share it.

**Idea recorded.** "A done check is only evidence if it fails without the change."

**How it comes back.** As a judgment on a different change: "Refunds in orbit-pay must never exceed the original charge. Here are three candidate done checks. Which one would still pass if the limit were missing?" The key is executable: the bank family (`spec/learning.md` 4.1) carries a small fixture where each candidate is run with and without the limit.

### 2.3 Missing line

**Trigger.** A correction prompt inside a task that undoes work: the prompt is followed by the agent removing or rewriting lines it added earlier in the same task (diff property: lines added since the task base are deleted again), or the agent runs `git restore`, `git checkout -- <path>` or `git revert` right after the prompt. The trigger is the undo, not the wording of the prompt, so it does not depend on reading tone.

**What the person does.** About 20 seconds, after the correction is sent, so the build is not delayed. Sealed call:

```
Firsthand: the builder just undid 58 lines. What one line in your brief would have prevented that? Or "skip".
```

Example: "Store keys in the existing charges table, do not add a table."

**The check.**

- Mechanical: the lines discarded, from the diff before and after the correction.
- Text check under section 1.6: was the stated constraint in the original brief? The key is the verbatim brief. The result is "absent", "present" with the quoted sentence, or "uncertain". "Present" is the interesting case: the brief said it and the builder missed it, which is a supervision finding, not a framing one, and the card says that.
- Later, mechanical: on the person's next task in the same path category, the engine checks whether a constraint of the same kind appears in the brief, and reports it once.

**Shown afterwards.**

```
MISSING LINE
Undone        58 lines, migrations/0031_idempotency_keys.py and 2 others
Your line     "Store keys in the existing charges table, do not add a table."
In the brief  Absent. The brief did not mention storage.
Kind          A constraint from the existing design.
```

**Idea recorded.** "State the constraints the existing system imposes: where data lives, what must not change." The kind is one of a short fixed list: goal, out of scope, existing-design constraint, conflict case, done check. Over time the Room shows which kind this person's corrections cluster in. That is a count of real corrections, not a score.

**How it comes back.** As a reading task in a new place: "You want the ledger export in orbit-pay to include refunds. Name two things about the existing system the builder must not change." Checked against a key cited from the ledger code and its tests.

### 2.4 Scope check

**Trigger.** turn_end with a "done" claim where the diff touches paths the brief and plan did not name: a diff property computed from the plan's file list, or from the path categories of the first edits. It fires when the unplanned paths are in a different path category from the planned ones.

**What the person does.** About 30 seconds. Sealed call, a pick for each of up to three unplanned paths:

```
SCOPE  idempotency for POST /charges
The change also touched files your brief did not mention.

  ledger/posting.py      +22 -9     Needed for the goal?   [ Needed ] [ Not needed ] [ Not sure ]
  config/retry.yaml      +3  -1     Needed for the goal?   [ Needed ] [ Not needed ] [ Not sure ]
```

**The check.** Executable. For each unplanned path the scratch runner reverts that path's changes only, keeps the rest, and runs the tests, including the person's done check from 2.1 or 2.2 if there is one. If everything passes, the change to that path was not needed to meet the goal as tested. If something fails, the failing test is shown. The limit is stated on the card: "not needed" means no test needed it, and a missing test would give the same result.

**Shown afterwards.**

```
ledger/posting.py   Reverted alone: 2 tests fail (test_ledger_posts_once, test_same_key_charges_once).
                    Needed. Your brief put the ledger outside the task, the goal did not.
config/retry.yaml   Reverted alone: all tests pass.
                    No test needed it. You said "Needed".
```

**Idea recorded.** "A goal can require changes the brief did not name. Find the dependency before the run, or decide the extra change is out." Instance: a charge is not idempotent unless the ledger posting is too.

**How it comes back.** As a prediction before a different task: "You will ask for a currency field on refunds in orbit-pay. Besides refunds/, name one other part of the system that has to change." Checked when that task or a drill version of it runs: the paths the change needed, found by the same revert-and-test method.

### 2.5 Drills for skill 5

**Rebrief.** From the record: a past task of the person's that had at least one correction prompt. The Room shows the original brief and a two-line description of the repo state, hides everything after, and asks the person to rewrite the brief. About 3 minutes. Check: the key is the list of corrections that really followed, verbatim from the timeline. For each one, a model checks under section 1.6 whether the new brief covers it, with a quote. Shown: "Your new brief covers 2 of the 3 corrections that followed. Not covered: the 422 on a mismatched body." The drill does not rerun the agent on the new brief. A rerun is slow and varies between runs, so it would not be a clean check.

**Cold reader.** The person picks any brief they wrote, or writes one for a task they plan to do. A fresh context with no access to the repo or the conversation reads it and lists the questions it would need answered before starting. Before seeing the list, the person predicts the top question. About 2 minutes. Check: the list itself. This is not a grade. It is what a reader without the person's context actually asked, which is the definition of the skill. Stated plainly: the reader is a model, so its questions are one sample of what a context-free builder would ask, and the card shows them as such.

---

## 3. Skill 6: delegating and supervising work

SKILLS.md warns that "rate the stakes" is easy to answer and hard to fault. So every moment here turns the rating into a call that the timeline can confirm or contradict: where the problem will be, where to stop, which file to read.

### 3.1 Review depth call

**Trigger.** The first "done" claim at turn_end on a task that has a diff, before the person has looked at it. Alternates with 2.1 at task start so one task never gets both.

**What the person does.** About 20 seconds. Sealed call with two picks, built from the real diff:

```
REVIEW DEPTH  idempotency for POST /charges   9 files, +312 -40

How closely will you check this?
  [ Read the report ]  [ Read the diff ]  [ Run it myself ]  [ Try to break it ]

If something is wrong, where?
  [ charges/handlers.py ]  [ charges/idempotency.py ]  [ ledger/posting.py ]
  [ migrations/0031 ]      [ tests/ ]                  [ Nothing is wrong ]
```

**The check.** From the timeline, between this call and the merge.

- Rework events, each with its file: tests failing after "done", correction prompts, failed CI checks, review comments that led to a commit, reverts.
- The depth actually used, from events: whether the person opened the diff (a diff tool call or Room diff view), ran anything (their own commands, where the hook can tell a user command from an agent one), or sent the next prompt within seconds. Where the surface cannot show this, the card says "depth not observed" and checks only the "where".
- The path categories the change touched, shown next to the chosen depth.

This is feasible within a session and a pull request. Linking a call to a production defect weeks later is not attempted, as SKILLS.md advises.

**Shown afterwards.** At merge, or at the next session start if the merge happened elsewhere:

```
REVIEW DEPTH, AFTER THE FACT
You chose     Read the report. You expected nothing wrong.
This change   Touched money movement and a migration.
What turned up before merge
  CI failed: test_concurrent_same_key (charges/idempotency.py)
  1 correction prompt, 27 lines reworked in charges/idempotency.py
Your last 6 calls on money-movement changes: 4 had rework. On test-only changes: 0 of 5.
```

The last line appears only when the person has enough past calls in that category for a count to mean something. It reports counts, never a percentage from a handful of cases.

**Idea recorded.** "Review depth follows what the change touches and how hard the result is to check, not how confident the report sounds." Instance: two requests arriving at the same time with the same key, which the report did not mention and one read of the diff would not show.

**How it comes back.** As a sort, away from the build: "Four changes waiting in orbit-pay: a copy change on the receipt email, a new index on charges, a retry on processor timeouts, a rename of an internal helper. Put them in order of how closely you would check them and give one reason for the top one." The key for the order is a bank family written by people. The reason is checked for one concrete point: it names what breaks or what is hard to observe.

### 3.2 Checkpoint

**Trigger.** after_tool on the agent's plan or todo tool call, when the plan has more steps than this person usually lets run between prompts. The threshold is the person's own median from past timelines, so it adapts. With no history it is a plan that spans more than one path category.

**What the person does.** About 20 seconds. Work product, sent to the agent, because a real stopping point is good practice: pick the step after which the builder should stop and report. Sealed call: what they will look at there.

```
CHECKPOINT  the plan has 8 steps
  1 Add idempotency_key column to charges
  2 Backfill existing rows
  3 Look up key in POST /charges
  4 Return stored response on repeat
  5 Make ledger posting idempotent
  6 Expire old keys
  7 Tests
  8 Update API docs

Stop and report after step [ 2 ]
Sealed: what will you check there?  [ that the backfill did not lock the table ]
```

**The check.** From the timeline.

- Where the first problem actually appeared: the step during which the first failing test, first correction prompt or first undo occurred. Steps are matched to events by the plan tool's own status updates.
- How much was built on top of it before it was caught: lines added between the step where the fault was introduced and the moment it surfaced. The introducing step is found mechanically where possible: the engine checks out the diff as of each step's end in the scratch runner and runs the test that later failed. This works when the agent commits or the hook recorded the diff per step. Otherwise the card says "introducing step not known" and shows only where it surfaced.
- Whether what the person said they would check was the thing that went wrong: a text match under section 1.6, shown as matched, not matched or uncertain.

**Shown afterwards.**

```
CHECKPOINT, AFTER THE RUN
You stopped after step 2. Nothing was wrong there.
The first failure surfaced in step 7: test_concurrent_same_key.
It was introduced in step 3: the lookup and the insert are separate statements.
4 steps and 190 lines were built on top of it before a test caught it.
A stop after step 3 or 4, with a concurrency test, would have caught it with 0 steps on top.
```

**Idea recorded.** "Place the checkpoint after the step that carries the most risk, and move the test for that risk forward to it." Instance: check-then-insert without a unique constraint is a race.

**How it comes back.** As a plan to mark, in a different area: "Here is a 6-step plan to move orbit-pay's webhook handler to a queue. Mark one checkpoint and say what you would run there." The key comes from a bank family with the plan's risky step identified by its authors. A later form asks the same about a plan in a non-payments system.

### 3.3 One file

**Trigger.** A "done" claim at turn_end with a diff of several files, on a task where the person's review depth has been "read the report" on recent tasks, or where 3.1 has faded. It is the fast form for people who will not read everything, which SKILLS.md says is most people most of the time.

**What the person does.** About 10 seconds. Sealed call:

```
Firsthand: 9 files changed. If you read only one, which? Type a name or pick in the Room. Or "skip".
```

**The check.** Two mechanical lists, shown side by side.

- Where the trouble actually was: files touched by rework events up to merge.
- Where it was most likely to be, from the diff alone: files in high-stakes path categories, and changed lines that no test run in the session executed. The second needs the project's coverage tool. Without it, only the path categories are used and the card says so.

No model judges the pick.

**Shown afterwards.**

```
ONE FILE
You picked            charges/handlers.py
Rework before merge   charges/idempotency.py (27 lines)
Changed, never run by a test this session
                      charges/idempotency.py:40-61   the expiry path
                      ledger/posting.py:88-97        the repeat-posting branch
```

**Idea recorded.** "When you can only sample, sample where a fault costs most and where nothing else is looking." Instance: the untested expiry path.

**How it comes back.** As a different sampling choice: "The builder says the refund flow is done: 6 files, all tests pass. You have five minutes. Which one thing do you run or read?" Free answer, checked for naming a specific risk and a specific observation. Later, the idea returns inside the skill 1 moments, since choosing what to verify is where the two skills meet.

### 3.4 Third failure

**Trigger.** tool_failed on the test command three times in a row with the same failing test id inside one task, or a test file edited between a failing run and the next passing run of the same test (diff property on the tests path category). Both are signs that the run needs a supervising decision.

**What the person does.** About 20 seconds. This is a real decision, so the pick is work product and acts on the build. The reason is the sealed call.

```
SUPERVISE  test_concurrent_same_key has failed 3 times
The builder's last three attempts changed: idempotency.py, idempotency.py, the test itself.

  [ Let it continue ]   [ Stop and re-brief ]   [ I will take this one ]

Sealed: what do you think is going wrong?  [ type here ]
```

**The check.**

- What happened on the path taken, from the timeline: whether the test passed, after how many more attempts, and how many lines changed.
- How it came to pass: the engine diffs the test file across the span and reports assertions removed, tests skipped or marked expected-fail, and timeouts or sleeps added. These are pattern matches on the test diff with `file:line`.
- The scratch runner runs the test as it was when it first failed against the final code. If the original test still fails, the pass came from changing the test.
- The person's stated cause is compared with the final fix under section 1.6.

Stated plainly: there is no check on the path not taken. If the person stops the run, the tool cannot say whether continuing would have worked, and it does not pretend to.

**Shown afterwards.**

```
You let it continue. The test passed 2 attempts later.
The original test, run against the final code: still fails.
What changed in the test   tests/charges/test_retry.py:71  the second request now waits 200 ms before sending
Your call: "it is a race in the lookup". The final code has no change to the lookup.
```

**Idea recorded.** "When a builder repeats a failed approach, the cheapest fix is often changing the test. Check which side moved." Instance: a sleep that hides a race, which SKILLS.md names under fundamentals.

**How it comes back.** As a replay from another project area or the question bank: a short timeline of four attempts at a flaky webhook test, with the question "At which attempt would you have stepped in, and what would you have asked for?" Checked against the attempt where the test was first weakened.

### 3.5 Drills for skill 6

**Supervise a past run.** An incident replay built from the person's own record: a past task with rework. The Room steps through the timeline one event at a time (plan, edits by file, test results, reports), hiding what came next. The person presses "I would stop here" once and types what they would have asked. About 4 minutes. Check: mechanical. The step where the fault was introduced and the step where it surfaced, found as in 3.2, are shown against the person's stop. Stopping between the two is the target. Stopping before the fault existed is early, after it surfaced is late. Their own past runs are used after enough time that they do not recall the details. The record holds the dates.

**Delegation review.** A decision review against what happened after. The Room lists the person's last several merged tasks with only the title and the brief. For each the person marks: checked too lightly, about right, more than it needed. About 3 minutes. Then the outcomes are revealed from the timeline: rework events before merge, and from `git log` afterwards, any later commit that reverts or fixes lines the task added. The fix link is the standard one: a later commit that deletes or rewrites those lines and whose message names a fix or revert. The card says that this link is a heuristic. Shown as a table of call against outcome, with no score. The idea it feeds is 3.1's.

---

## 4. Skill 7: breaking work into small, reversible changes

The advantage of this skill for the tool is that "can this part stand alone" and "can this be undone" are questions a machine can answer by trying it.

### 4.1 Split point

**Trigger.** after_tool where the task's working diff passes the person's own size line: larger, in files and changed lines, than most of their past merged changes in this repo. The Miner computes this from `git log --numstat`. With too little history it fires when one diff spans three or more path categories. It fires once per task. The size evidence for this trigger is in SKILLS.md, skill 7.

**What the person does.** About 45 seconds. The split is work product. They can tell the agent to act on it. The call that it stands alone is sealed.

```
SPLIT  this change is now 14 files, +460 -52. Larger than most of your merged changes here.

Which part could land first, on its own?
  [ ] migrations/0031_add_idempotency_key.py
  [ ] charges/idempotency.py, charges/handlers.py
  [ ] ledger/posting.py
  [ ] tests/charges/
  [ ] docs/api/charges.md

Sealed: will that part pass the tests alone?   [ Yes ] [ No ] [ Not sure ]
[ Check it ]   [ Skip ]
```

In the agent, on surfaces with no card:

```
Firsthand: this change is bigger than most of yours. Which part could land first on its own? Name the files, or "skip".
```

**The check.** Executable. The scratch runner starts from the task's base commit, applies only the chosen paths and runs the tests. Then it applies the remainder on top and runs them again. Results: the first part passes alone (a real split point), or it fails, and the failing test and the import or reference that crosses the line are shown. Splits are by file. A split that cuts through a file is not checked in this version, and the card says so when the person's line needs one.

**Shown afterwards.**

```
SPLIT, TRIED
Part 1  migrations/0031 alone                 tests pass. It can land first.
Part 2  + charges/idempotency.py, handlers.py tests pass.
Part 3  + ledger/posting.py                   tests pass.
You said the migration could stand alone: correct.

Your past changes in orbit-pay
  5 files or fewer     23 merged, 2 needed a fix commit after opening the pull request
  More than 12 files   6 merged, 5 needed a fix commit after opening the pull request
```

The history block is counted from the person's own repo by the Miner, appears only when both groups have enough changes to count, and is labelled as a description of their past, not proof of cause.

**Idea recorded.** "A schema change that only adds can land before the code that uses it." The general form: find the part with no dependents and land it first.

**How it comes back.** As a split to propose in another area: "orbit-pay needs partial refunds: a new column, a changed endpoint, a ledger rule, and an email. Give an order in which each step could ship alone." Checked against a bank family whose fixture runs each proposed order. Later, the opposite case: a change that should not be split, because its two halves are only correct together, and the question of how to tell.

### 4.2 Undo plan

**Trigger.** A diff property seen at after_tool or at `git commit` in before_tool: the change includes a step that a `git revert` does not undo. The engine matches migration files containing a drop, a rename, a type change or a new not-null constraint, data backfill scripts, deletions of stored files, and calls that send money or messages to an outside system. This skill shares the trigger with skill 4 (the risky step). The engine asks only one of the two moments for a given step. This one is chosen when the step is part of a larger change the person is shaping, and skill 4's when the step is about to run against something real.

**What the person does.** About 30 seconds. Sealed call:

```
UNDO  migrations/0032_rename_amount_to_amount_minor.py

If this ships and is wrong, what gets you back?
  [ Revert the commit ]  [ Run the down migration ]  [ Restore from backup ]  [ Nothing does ]

What would be lost?  [ type here, or "nothing" ]
```

**The check.** Executable where the project can run its migrations against a local or container database, which the Runner already supports for Replay.

1. Apply the migration to a scratch database loaded with the project's fixture or seed rows.
2. Run the tests of the previous commit against the new schema. This answers: if the code is rolled back and the schema is not, does the service still work?
3. Run the down migration if there is one, and compare schema and rows with the start.

Where the migrations cannot be run, the check falls back to static facts with `file:line`: whether a down migration exists, which statements destroy data, which other code reads the changed column. The card then says "not run, read from the files".

**Shown afterwards.**

```
UNDO, TRIED on a scratch database
Up migration          applied
Old code, new schema  14 tests fail: column "amount" does not exist
Down migration        applied. Rows match the start.
You said: revert the commit. A revert alone leaves the renamed column, and the old code fails against it.
What gets you back: the down migration, then the revert. In that order.
```

**Idea recorded.** "Code rolls back in seconds, data and schema do not. A rename is two changes: add the new, move readers, then remove the old."

**How it comes back.** As a classification with a reason, on new cases: "Three steps in orbit-pay: add a nullable column, send the refund to the processor, change a config flag. For each: what undoes it, and how long does that take?" The key is from a bank family. Later, the idea returns in production form through the skill 8 moments.

### 4.3 Landing order

**Trigger.** after_tool on a plan or todo call, or a diff at turn_end, that contains both a schema change and code that reads or writes the changed column or table. The engine finds the reference by searching the diff's code hunks for the names in the migration.

**What the person does.** About 45 seconds. Work product: put the steps in an order where the service works after each one. In the Room this is a list to reorder. In the agent it is a typed order.

```
ORDER  rename charges.amount to amount_minor
Put these in an order where orbit-pay works after every step.

  A  Drop the old column amount
  B  Add amount_minor, write to both columns
  C  Switch reads to amount_minor
  D  Backfill amount_minor for old rows
```

**The check.** Executable when the agent has produced the pieces as separate commits or files. The scratch runner applies them in the person's order and runs the tests after each. The first failing step is the answer. When the pieces do not exist yet, because the person is ordering a plan, the order is stored sealed and checked when the work is done. If the builder is told to follow the person's order, the check is the real run.

**Shown afterwards.**

```
ORDER, TRIED
Your order   B, C, D, A
After B      tests pass
After C      3 tests fail: old rows have no amount_minor yet (test_list_charges_before_migration)
An order that passes at every step: B, D, C, A
```

**Idea recorded.** "Expand, migrate, contract: add, backfill, switch readers, then remove. Each step is safe to stop after."

**How it comes back.** In another shape with the same structure: "orbit-pay is changing the webhook payload it sends to merchants from v1 to v2. Order these four steps so no merchant breaks." No database is involved, so it tests the idea and not the memory of the instance. Key from a bank family.

### 4.4 Mixed change

**Trigger.** before_tool on `git commit` or `gh pr create`, where the staged diff mixes kinds: moves and renames that leave behaviour unchanged, together with behaviour changes. The engine detects the first kind from git's rename detection and from files whose normalised AST hash is unchanged apart from identifiers. The hash is the one the engine already computes for item distance (`spec/learning.md` section 4). The hook never delays the commit. The question appears after it.

**What the person does.** About 20 seconds. Sealed call:

```
Firsthand: this commit renames ChargeService to PaymentService in 11 files and also changes retry behaviour. If the retry change has to be reverted next week, what else goes with it? Or "skip".
```

**The check.** Executable. The scratch runner reverts the commit and reports what a revert takes with it: the list of files and kinds. It then applies the rename-only part alone and the behaviour part alone, each from the base, and runs the tests. If both pass alone, they could have been two commits, each revertable without the other.

**Shown afterwards.**

```
MIXED CHANGE
A revert of this commit removes   the retry change (2 files) and the rename (11 files)
Rename alone                      tests pass
Retry change alone                tests pass
They can be two commits. Reverting the retry change would then leave the rename in place.
[ Ask the builder to split this commit ]
```

The button gives the person a sentence to send to the agent. The tool does not rewrite history itself.

**Idea recorded.** "One commit, one reason to revert. Changes that only move code travel separately from changes that alter behaviour."

**How it comes back.** When a real revert happens: `git revert` or a restore is seen in the timeline. That is the strongest feedback this skill gets, so the engine uses it. The card shows what the revert took with it that the person did not ask to undo, counted from the reverted diff, and links back to this idea. If no real revert comes, the idea returns as a review item: "This pull request in orbit-pay has three commits. Which one would you be unable to revert cleanly, and why?" with the answer found by trying each revert in the runner.

### 4.5 Drills for skill 7

**Revert replay.** From project history: the Miner picks a commit a few weeks old that later commits have built on. The person predicts what happens if it is reverted today: reverts cleanly, conflicts, or reverts and breaks tests, and names one thing that would break. About 2 minutes. Check: executable. The runner runs `git revert --no-commit` on a scratch copy at the current head, records conflicts by file, and runs the tests if it applied. Shown: the real result next to the prediction, with the conflicting files or failing tests. This turns "is my history reversible" from a belief into an observation on the person's own repo.

**Split a past change.** From project history: a large merged change, the person's or a teammate's. The Room shows its file list with per-file summaries and asks for an order of two to four parts, each of which could have landed alone. About 4 minutes. Check: executable, the same cumulative apply-and-test as 4.1, at that change's base commit. Where a part fails, the crossing reference is shown. Old commits whose tests no longer run in a container are skipped by the Miner, so the drill is offered only where the check works.

---

## 5. What to build first

**Brief against result (2.1), with the done check from 2.2 inside it.**

Reasons:

- SKILLS.md names "brief against result" among the four moments with the clearest feedback, and it is the only one of the four in this file.
- Its trigger is a prompt, which every surface has: a hook where hooks exist, a relayed call where they do not. That keeps the founder decision of the same learning outcome on every agent.
- It forces the task timeline (section 1.2) to exist. Every other moment in this file reads that timeline, so building 2.1 builds their shared base.
- Its work product improves the build itself. A done check and an out-of-scope line make the agent's run better whether or not the person ever opens the Room. A moment that pays for its own interruption is the right one to meet first.
- Its done-check part is executable and reuses the revert-test runner call that skill 1 needs anyway.

Second: **Split point (4.1)**, because its check is fully executable and its trigger is a plain diff statistic. Third: **Checkpoint (3.2)**, once per-step diffs are in the timeline.

---

## 6. Summary table

| Moment | Skill | Trigger signal | Person does | Check | Kind of check |
| :- | :-: | :- | :- | :- | :- |
| Brief against result | 5 | Task-starting prompt followed by a plan call or multi-category edit | Goal, out of scope, done line. Sealed: what the builder will guess | Done check run before and after, diff paths against out of scope, builder's questions and cited assumptions, corrections and rework lines | Executable and timeline, model for the uncited guesses |
| Done check first | 5 | Behaviour-change prompt that names no check | Names one check | Check run at base and at result, and with the fix undone | Executable |
| Missing line | 5 | Correction prompt followed by the agent undoing its own lines | One line the brief lacked | Lines discarded, constraint absent from the verbatim brief | Timeline, model text check |
| Scope check | 5 | "Done" with a diff touching unplanned path categories | Needed or not, per path | Revert each path alone, run tests | Executable |
| Review depth call | 6 | First "done" claim, before the person looks | Picks depth and where a fault would be | Rework events by file up to merge, depth observed, path categories | Timeline |
| Checkpoint | 6 | Plan call longer than the person's usual run | Picks the stop step. Sealed: what to check there | Step where the fault was introduced and where it surfaced, lines built on top | Timeline and executable |
| One file | 6 | "Done" with a multi-file diff, for light reviewers | Picks one file to read | Files with rework, changed lines no test ran | Timeline and coverage |
| Third failure | 6 | Same test fails three times, or a test edited between fail and pass | Continue, stop or take over. Sealed: the cause | Outcome of the path taken, original test against final code, test-diff patterns | Executable. No check on the path not taken |
| Split point | 7 | Diff larger than most of the person's merged changes | Picks the part that lands first. Sealed: passes alone? | Apply that part alone, run tests, then the rest | Executable |
| Undo plan | 7 | Diff contains a step a revert does not undo | Picks what gets them back, names what is lost | Up migration, old tests on new schema, down migration, on a scratch database | Executable, static fallback |
| Landing order | 7 | Schema change plus code that uses it | Orders the steps | Apply in that order, run tests after each | Executable |
| Mixed change | 7 | Commit or pull request mixing pure moves with behaviour changes | Says what a revert would take with it | Revert in scratch, apply each kind alone, run tests | Executable |

Drills: Rebrief and Cold reader (skill 5), Supervise a past run and Delegation review (skill 6), Revert replay and Split a past change (skill 7).

## 7. What this file leaves to others

- The "done" claim itself, and whether the tests prove it, belong to skill 1. This file only uses the claim as a trigger and reuses the revert-test runner.
- The risky step about to run against something real belongs to skill 4. Section 4.2 says how the two share one trigger.
- Whether the person's sense of their own review depth and speed is accurate over time belongs to skill 10. Sections 3.1 and 3.5 produce the paired calls and outcomes that skill needs.
- The Room screens for the cards above follow `design/learning-experience/design-system.md`. The blocks in this file fix the wording and the content, not the layout.
