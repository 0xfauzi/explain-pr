# Moments: calibration, product judgment, and what a level means

> **Superseded.** The rules in this file (budgets, fading, scoring, levels, what counts) are replaced by `../spec/learning.md`. Several moments here were merged, renamed or cut: `../spec/learning.md` section 13 maps every name. Use this file for worked examples and wording ideas only. On-screen copy is in `../spec/experience.md`.

Part of the Firsthand design. This file does three things:

- Designs the practice for skill 10, calibrating your own judgment.
- Designs the practice for skill 11, product judgment.
- Answers one question for all eleven skills: what a level means for a judgment skill, how it goes up and down, and how progress is shown honestly.

The skills are defined in `../../skills/SKILLS.md`. This file reuses the signals and the scratch runner from `checking.md` sections 3 and 4, the task timeline and path categories from `directing.md` sections 1.2 and 1.4, and the record, sealing and accuracy rules from `../spec/`. All example wording uses one project: orbit-pay.

---

## 1. Decisions in this file

1. **Calibration is mostly a rider, not a new interruption.** The main calibration moment (C1) is one extra tap on a call the person is already making in another moment. It adds no trigger and no prompt. Reason: calibration needs many paired calls and outcomes, and the cap is three moments a day.
2. **Calibration is trained on things the tool can time or count.** The tool cannot measure "time saved", because it never sees the same task done without the agent. It can measure how long a task took and where the time went. So the moments ask for forecasts of those.
3. **Product judgment is trained on four things that can be checked inside a build:** whether the success signal can be read at all, whether the thing already exists, which parts the stated outcome needs, and who notices the change. A fifth moment checks whether the feature helped, and it is asked only where the project has a source the tool can read. `SKILLS.md` says a product moment without feedback should not be used. This file follows that.
4. **Ideas and skills have separate levels.** An idea keeps the existing ladder (`../spec/learning.md` section 5). A skill gets a level from a record of calls compared with outcomes. Section 6 gives the rules.
5. **A skill level must beat the fixed answer.** If most changes are clean, a person who always says "clean" is right most of the time and has shown nothing. Every skill record is shown next to what one fixed answer would have scored on the same cases.
6. **Progress is shown as counts with their age, per skill, never as one score.** Section 7.
7. **The first thing to build from this file is C1, How sure.** Reasons in section 9.
8. **No experiments are proposed.** Each choice is made from `SKILLS.md` or from what git, the test runner and the record can actually report.

---

## 2. The running example

orbit-pay is the payments service described in `checking.md` section 2: Python, pytest, Postgres, with refunds, idempotency, a ledger, webhooks and a nightly reconciliation job. The person has marked `orbit_pay/ledger/` and `orbit_pay/money.py` as high stakes.

This file uses Task A from that file and adds one feature task:

- **Task A:** make refunds idempotent, so a retried refund request does not refund twice.
- **Task D:** merchants ask support for a list of their settled charges. Add `GET /settlements/export`, which returns a CSV of settled charges for a date range.

Facts about orbit-pay used below:

- `orbit_pay/recon/settlement_file.py` already reads and writes settlement rows as CSV for the reconciliation job.
- Open pull request #41, "Email merchants a weekly settlement report", is unmerged.
- The table `api_requests` logs every API call with its route and merchant id.

---

## 3. Signals and shared machinery

| Used here | Defined in | What it gives |
| :- | :- | :- |
| S1 to S6 | `checking.md` section 3 | Prompt submitted, tool call, turn end, git state, test results, pull request events |
| Scratch runner | `checking.md` section 4 | A copy of the tree where one thing is changed and tests are run |
| Task timeline | `directing.md` section 1.2 | Brief, plan steps, test runs, first "done" claim, rework events, merge, with times |
| Rework events | `directing.md` section 1.2 | A test failing after "done", a correction prompt, a failed CI check, a review comment that leads to a commit, a revert |
| Path categories | `directing.md` section 1.4 | Money movement, auth, schema and migrations, public interface, config, tests, other |
| Sealed call | `directing.md` section 1.1 | A prediction typed in the Room or an inline card, stored before the result is shown, never passed to the agent |

Two things are new in this file.

**Active time.** The timeline has a time on every event. Active time for a task is the sum of the gaps between consecutive events, leaving out any gap longer than the idle limit. Design default for the idle limit: ten minutes, set per person, because a longer gap is more likely a break than work. Active time is split into three parts:

| Part | From | To |
| :- | :- | :- |
| Agent working | A prompt is submitted | The turn ends |
| Person deciding | A turn ends | The next prompt is submitted |
| After "done" | The first "done" claim | The merge commit |

The third part overlaps the first two. It is the time spent on review, correction and rework after the agent first said the work was complete. The tool cannot see what the person does while the agent works, and says so on the card.

**Outcome sources.** A source is a command the person registers that prints one number. Section 5 uses it for product outcomes.

```
firsthand source add settlement-exports -- \
  psql "$ORBIT_RO" -Atc "select count(distinct merchant_id) from api_requests
                         where route = '/settlements/export' and ts > now() - interval '30 days'"
```

Rules for sources:

- The command is written by the person and runs only on their machine, with a time limit, when a moment needs it.
- The engine stores the command text, the first number in the output and the time. It stores no other output.
- Secrets stay in the person's environment. The engine refuses to save a command that contains a literal password or token pattern (`../spec/security.md` section 7).
- A source is per project and lives in the record's `config/`. `../spec/security.md` section 2.1 needs one new row for this class: "the person's own registered command".

---

## 4. Skill 10: calibrating your own judgment

The system-level point: a feeling of speed, quality or understanding is a forecast. It can be written down before the fact and compared with what happened. The evidence in `SKILLS.md` is that experienced developers forecast a 24% speedup, believed afterwards they had been 20% faster, and were measured 19% slower. Both the forecast and the memory were off, so the moments below cover both.

### C1. How sure

- **Trigger:** none of its own. It rides on any moment in any file whose answer is a sealed call with an event check: the revert test, the review depth call, the split point, and the product moments below. The engine adds it to about half of those calls, chosen by the engine, so that it does not become a reflex tap.
- **The person does:** after making the host call, one tap. About three seconds.
- **Prompt** (here on the revert test from `checking.md` V2):

```
You said: fails without the change.
How sure?   [ A guess ]  [ Fairly sure ]  [ Sure ]
```

- **The check:** the host moment's check. Here the runner reverts the source files and runs the test. C1 adds no check of its own. It stores the confidence with the call, so the record holds a pair: how sure, and whether the call matched.
- **Shown after:** the host moment's reveal, plus one line:

```
You were sure, and the call matched.
Your "sure" calls on orbit-pay so far: 7 of 9 matched. "Fairly sure": 4 of 8. "A guess": 2 of 5.
```

The counts line is shown only when each band it prints has at least five calls. Design default: five, because a smaller count reads as a rate when it is not one. Before that the card says "3 sure calls so far. Counts appear after 5."

- **Idea recorded:** "sure" is a claim that can be scored. If your sure calls are right about as often as your guesses, the feeling carries no information.
- **Comes back:** days later, as a number recalled from the person's own record. "Before you look: of your last 10 'sure' calls on orbit-pay, how many matched what happened? Type a number." The key is a count from the record, so no model is involved. Within one of the true count is a match.
- **Notes:** this is forecast confidence. It is kept apart from confidence on delayed review items, which `../spec/learning.md` section 1 already tracks. A forecast is made before the outcome exists and a recall is not, so the two never share a line on the map.

### C2. Time call

- **Trigger:** S1 on the first prompt of a task, or `moment task_start`. Offered only when the record holds at least five merged tasks for this project, so there is something to compare with. Never on the same task as C5.
- **The person does:** picks a band for active time until the change is merged, and a band for how much of it will come after the agent first says done. Two taps. Target: fifteen seconds.
- **Prompt:**

```
Before the agent starts on idempotent refunds (skip ok):
Active time until this is merged?
  [ Under 30 min ]  [ 30 to 90 min ]  [ 90 min to 3 h ]  [ More than 3 h ]
How much of that will come after the agent first says "done"?
  [ Under a quarter ]  [ A quarter to a half ]  [ More than half ]
```

- **The check:** at the merge commit, the engine reads the task timeline and computes active time and its three parts (section 3). No model is involved. If the task is abandoned or the timeline has a gap the engine cannot account for (work done on another machine with no import), the call is dropped unscored and the journal says why.
- **Shown after:** at merge, or at the next session start if the merge happened elsewhere:

```
TIME CALL, AFTER THE FACT   idempotent refunds
You expected   30 to 90 min, under a quarter of it after "done".
What happened  2 h 10 min active.
               Agent working     48 min
               You deciding      1 h 22 min
               After "done"      1 h 15 min (more than half)
After "done":  CI failed on test_concurrent_same_key, 2 correction prompts, 1 review comment.
The tool cannot see what you did while the agent worked, and cannot say how long this
would have taken without it.
```

- **Idea recorded:** the first "done" is a point inside the task, not its end. A forecast that stops there leaves out review and rework.
- **Comes back:** as a forecast on a described task, with the key from the person's own history. "A task like these three (list of three past orbit-pay tasks that touched migrations) is about to start. Which part of the active time was largest across them: agent working, you deciding before 'done', or after 'done'?" The key is computed from the timelines of those tasks. A second form is a bank item written by people: a short account of a project plan with a schedule, and the question of which stage the schedule left out.

### C3. Where it went

- **Trigger:** the merge commit of a task with at least thirty minutes of active time and no C2 call. Seen in S4, or as `gh pr merge` in S2. If the person is not in a session, it waits in the Room inbox and is offered at the next session start. Design default for thirty minutes: shorter tasks have too few events for the split to mean much.
- **The person does:** recalls, without looking, how the time split. One tap. Target: ten seconds.
- **Prompt:**

```
The settlement export just merged. From memory (skip ok):
What share of your active time on it came after the agent first said "done"?
  [ Under a quarter ]  [ A quarter to a half ]  [ More than half ]
```

- **The check:** the same timeline computation as C2. The difference is direction: C2 scores a forecast, C3 scores a memory. `SKILLS.md` reports that both were wrong in the same study, so both are practised.
- **Shown after:**

```
You remembered: under a quarter.
The timeline:   3 h 05 min active, 1 h 40 min of it after the first "done" (more than half).
Largest item after "done": 3 rounds on the CSV column order, 52 min.
```

- **Idea recorded:** memory of a task keeps the fast part, the generation, and loses the slow part spread across review and rework. Read the log before trusting the memory.
- **Comes back:** as a number from the record. "Across your last five merged tasks on orbit-pay, was more time spent before the first 'done' or after it?" The key is the sum over those timelines. A later form turns it around: "Name the one task this month where the time after 'done' was longest." The key is the task at the top of that list. Naming either of the top two is a match.

### C4. Understanding call

- **Trigger:** S6, a pull request opens (`gh pr create`) or `moment pr_open`, on a change that touches a high-stakes path, where the timeline shows the person has not opened the diff (no diff tool call and no Room diff view). The second condition is dropped on surfaces that cannot observe it.
- **The person does:** two steps in the Room, where the diff is not on screen. First a self-rating, one tap. Then one question about what the change does, with a key that comes from running the code. Target: two minutes.
- **Prompt:**

```
The refund change is about to go up for review (skip ok).
Could you say what it does to the ledger without looking?
  [ Yes ]  [ Partly ]  [ No ]
```

Then, whatever the rating:

```
A refund request for charge ch_81 arrives twice with the same key, one second apart.
After both finish, how many rows does the ledger hold for that refund? Type a number.
```

- **The check:** the question is a Predict item from `checking.md` R1. Its key is the output of actually running that case in the scratch runner, sealed before the question is shown. The calibration check is the pair: the self-rating and whether the answer matched the key. No model grades anything.
- **Shown after:**

```
You said: Yes.
Your answer: 2 rows. The run: 4 rows (a debit and a credit for the refund, and the same
pair again, because the second request reached the ledger before the key was stored).
You were sure you understood this change, and the prediction missed.
Your "Yes" ratings so far: 3 of 6 predictions matched.
Back to: the pull request. This case is worth a look before review.
```

In this example the check also found a real defect. That is expected: a question with an executable key about a high-stakes path sometimes does.

- **Idea recorded:** the feeling of understanding a change comes from reading a clear summary. It is tested only by predicting what the change does and comparing.
- **Comes back:** as the same two steps on a different component, away from the build, at least seven days later: a self-rating on a part of orbit-pay the person has not touched lately (the webhook handler), then one Predict item on it with a sealed key. The rating is scored against the result. A bank form uses a short system description written by people in place of the person's own code.
- **Notes:** the Predict answer is given in the build, so it moves no idea level (`checking.md` decision 3). The pair of rating and result is a scored call for skill 10, under the rules in section 6.

### C5. Outside view

- **Trigger:** S1 at task start, where the plan or the brief names paths in a category for which the record holds at least five merged tasks with outcomes. Where the category is not known at the first prompt, the trigger moves to the first edit of a tagged path (S2). Never on the same task as C2.
- **The person does:** types one number from memory. Target: ten seconds.
- **Prompt:**

```
This task touches orbit_pay/ledger/. Before the agent starts (skip ok):
Your last 8 tasks that touched the ledger: how many needed rework after the agent said "done"?
Type a number from 0 to 8.
```

- **The check:** a count from the record: tasks in that category with at least one rework event between the first "done" claim and the merge. No model is involved.
- **Shown after:**

```
You said: 2 of 8.
The record: 6 of 8 had rework after "done". Median active time 1 h 50 min.
The two without rework were both test-only changes.
```

- **Idea recorded:** start a forecast from how similar work actually went, then adjust for what is different this time. The feeling about this task comes second.
- **Comes back:** as a choice between two ways of forecasting, in a new setting. "The reconciliation job needs a new currency. You feel it is a one-hour change. Your last four changes to reconciliation took 2 h, 3 h, 50 min and 4 h. What is your forecast, and which number did you start from?" The check is one concrete point read by a model under the accuracy rules: the answer starts from the past four and names an adjustment. A second form asks the base rate for a different category and is keyed from the record.

### Drills for skill 10

**Ten calls.** Away from the build, about ten minutes. The engine draws ten Predict items from the person's project, each with a key from a sealed runner result, at distance "same project other function" or further. For each the person answers and marks A guess, Fairly sure or Sure. Check: the sealed keys. Shown: the three rows of counts for this run next to the same three rows from the person's in-build calls. Example:

```
TEN CALLS   orbit-pay, 14 Nov
            This run      In the build, last 30 days
Sure        4 of 4        7 of 9
Fairly sure 2 of 4        4 of 8
A guess     1 of 2        2 of 5
```

It counts as evidence away from the build for skill 10 (section 6.4).

**Looking back.** About five minutes. The engine picks one decision from the journal that is at least thirty days old and has a known outcome: a time call, a review depth call, a product forecast. It shows the task name only. The person types what they predicted at the time and what then happened. Check: the sealed call and the recorded outcome, both already in the record. The match is on the prediction: did they remember what they actually said? Shown: their words then, their memory now, and the outcome. The point is the well-known pull towards remembering that one "knew it all along". Where the recalled prediction is free text, a model reads whether it matches the sealed call, under the accuracy rules, and an uncertain reading is shown as uncertain.

---

## 5. Skill 11: product judgment

The system-level point: a change can be correct and still be the wrong thing to ship. `SKILLS.md` reports that among rejected agent pull requests, duplicates of existing work were a larger group than code-level failures, and that where a reason was given, a preferred alternative was more common than a technical flaw. The moments below train the checks that catch those cases before the work is done.

Product judgment depends on domain knowledge, which `SKILLS.md` says a prompt in a build cannot supply. So these moments do not test knowledge of the market or the user. They test four habits that can be checked from the project itself, and one outcome check where a source exists.

### P1. Who and signal

- **Trigger:** S1 on the first prompt of a task the engine classes as a feature: the prompt asks for behaviour a user of the product would see. The class is confirmed at "done" from S4: the diff touches the public interface category. If it does not, the call is dropped unscored.
- **The person does:** writes two lines in the Room or an inline card. Who the change is for, and what they will be able to look at after it ships that would show it helped. Target: under a minute. This is work product: it goes to the agent as part of the brief, because the build benefits.
- **Prompt:**

```
Before the agent starts on the settlement export (skip ok):
Who is this for?
What will you be able to look at, a month after it ships, that shows it helped? Say where.
```

Example answer: "Merchants who ask support for settlement lists. Fewer support tickets tagged settlements, and merchants calling the export route."

- **The check:** three parts, the first two mechanical.
  1. **Now.** The engine tries to read each signal the person named. A registered source is run and its number stored as the baseline. A metric, log or event name is searched for in the code. An issue label is looked up with `gh issue list --label`.
  2. **At "done".** The engine checks the diff for whatever the signal needs: the route is logged, the event is emitted, the column exists.
  3. **Later.** P5.
- **Shown after** (part 1, within seconds):

```
Signals you named
  Merchants calling the export route   Readable. api_requests logs every route.
                                       No source registered yet. One line adds it:
                                       firsthand source add settlement-exports -- <query>
  Support tickets tagged settlements   Not readable from here. No issue label "settlements"
                                       exists, and no ticket system is connected.
One of your two signals can be read today.
Back to: the settlement export.
```

- **Idea recorded:** decide what you will look at to know a feature helped before it is built. A signal nobody can read is a hope, not a signal.
- **Comes back:** for a different feature in the same project, days later. "orbit-pay is adding an email to merchants when a payout fails. Name one thing that exists in orbit-pay today that could show the email helped." The engine checks the named thing the same way as part 1: it exists or it does not. A bank form gives four candidate signals for a described feature and asks which one tells "used" from "shipped". Its key is written by people, and as a choice item it counts up to Recalled.
- **Notes:** the "who" line has no check and the card says so: "The tool cannot check who this is for. It is kept in the journal with the outcome."

### P2. Already there

- **Trigger:** S2 inside a feature task, at the first of: the agent's plan names a new module, a tool call creates a new source file, or a tool call edits the dependency manifest (`pyproject.toml`, `package.json`). On surfaces without hooks, `moment plan`.
- **The person does:** a sealed call, typed in the Room or an inline card. Target: thirty seconds.
- **Prompt:**

```
The agent plans a new module, orbit_pay/export/csv_writer.py, and a new dependency, pandas.
Before it does (skip ok):
Does orbit-pay, or an open pull request, already have something that does part of this?
Name it, or say "nothing".
```

- **The check:** a search the engine runs, in three places.
  1. The repository: files and symbols whose names share the plan's key terms (csv, export, settlement), using the reference search from `checking.md` R2.
  2. The dependencies: whether the manifest or the standard library already provides what the new dependency is for.
  3. Open and recently closed work: `gh pr list --search` and `gh issue list --search` with the same terms.

  The hits are facts. Whether a hit really does the same job is a reading, so the card lists hits and does not rule on them. The call is scored at merge from what happened: it matches if the person named something and the merged diff uses it (an import of the named path, or the new dependency dropped), or if the person said "nothing", the search found nothing, and no review comment pointed to a duplicate. Anything else is unscored.
- **Shown after:**

```
You said: nothing.
The search found
  orbit_pay/recon/settlement_file.py   write_rows() writes settlement rows as CSV. Used by the nightly job.
  Python standard library              csv module. pandas would be a new dependency for this alone.
  Pull request #41 (open)              "Email merchants a weekly settlement report". Same data, different delivery.
Searched: file and symbol names, pyproject.toml, open and closed pull requests and issues.
Not searched: code behind dynamic imports, other repositories.
```

- **Idea recorded:** before building, look in three places: the code, the dependencies, and the work other people already have open.
- **Comes back:** as a locate question with an executable key. "orbit-pay calls the card processor over the network in several places. Name one file where a retry with backoff already exists." The key is the reference search result, sealed. A later form uses the pull request list: "Name an open pull request that touches the same table as a change to payout scheduling would." The key is the list of open pull requests whose diffs touch that table.

### P3. Cut line

- **Trigger:** S3, a "done" claim on a feature task, where an acceptance check exists (from `checking.md` V1, `directing.md` 2.2, or the person's own test for the outcome) and a coverage run shows at least one whole group of files in the diff that the acceptance check never executes.
- **The person does:** a sealed call: picks which parts the stated outcome depends on. Target: thirty seconds.
- **Prompt:**

```
The agent reports the settlement export is done. 14 files, +620 -12.
Your outcome: a merchant downloads a CSV of settled charges for a date range.
Which of these parts does that outcome depend on? Pick any (skip ok).
  [ Export route and query ]   [ CSV writer ]   [ Saved date presets ]
  [ Admin page listing exports ]   [ Background job and export_jobs table ]
```

- **The check:** the scratch runner reverts each group to the base in turn and runs the acceptance check. A part whose removal leaves the acceptance check passing is not needed for the stated outcome. No model is involved. If removing a part breaks the build for reasons unrelated to the outcome (an import in a shared file), the part is reported as "could not test alone".
- **Shown after:**

```
You picked: route and query, CSV writer, background job.
With each part removed, your acceptance check
  Export route and query            fails    needed
  CSV writer                        fails    needed
  Saved date presets                passes   not needed for this outcome   3 files, +88
  Admin page listing exports        passes   not needed for this outcome   4 files, +171
  Background job, export_jobs table passes   not needed for this outcome   3 files, +204, 1 migration
463 of the 620 added lines are outside the outcome you named. They may still be worth having.
That is your call, and the migration is the part that is hardest to take back later.
```

- **Idea recorded:** the smallest change that delivers an outcome is found by asking what the outcome's own check needs. Everything else is a separate decision.
- **Comes back:** on a past change from the project's history, in a new form. "Three months ago the webhook retry feature merged in five parts (listed). Its acceptance test was test_retry_until_acknowledged. Which one part could have been left out with that test still passing?" The key is a sealed runner result on that old change, run in a container under `../spec/security.md` section 2.2.
- **Notes:** this is not the split point in `directing.md` 4.1. That moment asks whether parts can land separately. This one asks whether a part serves the outcome at all. They share the runner and never fire on the same task.

### P4. Who notices

- **Trigger:** S6 when a pull request opens, or S3 at "done", where S4 shows at least one of: a test that existed at the base has changed assertions, the public interface category is touched (a route, a response schema, an API description file), a default value changed in config, or user-facing text changed.
- **The person does:** a sealed call. Target: thirty seconds.
- **Prompt:**

```
The refund change is ready for review (skip ok).
Who sees something different, or has to change something, the day this ships?
  [ Nobody ]  [ Existing API clients ]  [ Merchants ]  [ Support ]  [ Other: ___ ]
In one line, what changes for them?
```

- **The check:** "old tests on new code". The runner takes the test files as they were at the base and runs them against the source as it is now. Each old test that fails is a behaviour the project used to promise and no longer does. The engine adds the schema differences where the project has an API description file: fields removed or renamed, status codes changed, fields that became required. No model is involved in finding them. Scoring: "Nobody" matches when no old test fails and no schema difference exists. Any other pick matches when at least one does. The one-line reason is shown next to the facts and is not scored.
- **Shown after:**

```
You said: nobody.
Tests from before the change, run on the code now: 1 of 212 fails.
  test_two_equal_partial_refunds
    Before: two refunds of 10.00 on one charge, no key given, created 2 refunds.
    Now:    the second request returns the first refund. 1 refund.
  The agent edited this test to expect 1.
Response schema: no fields removed or renamed.
A merchant who refunds the same amount twice on purpose, without a key, now gets one refund.
```

- **Idea recorded:** an edited test is a changed promise. Before shipping, find who relied on the old one.
- **Comes back:** as a prediction on a different change, with an executable key. "money.py now rounds half to even. Which tests written before that change fail on the new code? None, ledger tests, reconciliation tests, both." The key is a sealed runner result. A later free-text form: "A change makes POST /charges return 202 where it returned 201. Name two kinds of caller that could break and how you would find them in the code." This is read by a model against sealed points under the accuracy rules.

### P5. Did it help

- **Trigger:** the date the person chose at P1 (one week, one month or three months after merge), at the next session start or in the Room inbox. Asked only if at least one P1 signal has a registered source or a readable issue label. With no readable signal it is never asked, and the journal entry for the feature says "no outcome source".
- **The person does:** predicts before the number is shown. One tap. Target: ten seconds. It takes one of the day's three review slots, not a slot in the build.
- **Prompt:**

```
The settlement export merged 30 days ago. Before you see the number (skip ok):
Merchants who called the export route in the last 30 days, out of 140 active merchants?
  [ Under 5 ]  [ 5 to 20 ]  [ 20 to 50 ]  [ More than 50 ]
```

- **The check:** the engine runs the registered source and compares the number with the baseline stored at P1 and with the band the person picked. No model is involved.
- **Shown after:**

```
You said: 20 to 50.
settlement-exports: 6 merchants in 30 days. Baseline at merge: 0.
In the journal, your line at the start: "Merchants who ask support for settlement lists."
The tool can show the count. It cannot say why it is 6.
Of the parts not needed for the outcome (P3), the admin page has had 0 requests.
```

- **Idea recorded:** shipped is not used. Look at the number you named, on the date you named.
- **Comes back:** at the next P1 on this project, the card carries one extra line: "Last feature: you expected 20 to 50 merchants, 6 used it." It also returns as a rank question: "Three features merged last quarter with sources registered. Put them in order of use." The key is the three source numbers, read fresh.

### Drills for skill 11

**Kept or cut.** About five minutes, from the project's own history. The engine picks five features merged at least sixty days ago (changes that touched the public interface category). The person predicts, for each, what happened since: untouched, extended, reworked, or removed. Check: git. The engine reads later commits on the same files, reverts, deletions, and issues that reference the pull request. Where sources are registered, the use count is shown too. The card says what this measures: what the project later did with the code, which is not the same as value to users.

**Maintainer's call.** About five minutes, from a bank. The person sees a real pull request from a public project: its description, its size, and a short account of the project written by a person. They predict merged or closed, and give one reason. Check: the actual outcome, which is a fact, and the maintainers' stated reason where one exists, compared by a model under the accuracy rules. Cases with no stated reason are scored on the outcome alone. The bank stores a link and a summary written by people, not the project's code. It is reviewed like other bank families (`../spec/learning.md` section 4.1). Reason for this drill: the rejection data in `SKILLS.md` shows fit with the project decides more rejections than code faults do, and a public history is the one place that judgment has a recorded answer.

---

## 6. What a level means for a judgment skill

### 6.1 Two things have levels

| Thing | What the level claims | Evidence | Ladder |
| :- | :- | :- | :- |
| An idea | The person can bring the idea back and use it on a new case without help | Delayed answers on review items and drills | Not yet, Recalled, Applied, Held (`../spec/learning.md` section 5, unchanged) |
| A skill | When the person made calls of this kind before the outcome was known, the calls held up against what happened | Scored calls, in the build and in drills | Not yet, Shown, Reliable, Held (this section) |

Knowing an idea and making good calls are different. A person can state that an edited test is a changed promise and still answer "nobody" at P4. So the two are never merged. On the skills map each skill row shows its own level, with its ideas listed under it at their own levels.

This extends decision 3 in `checking.md`. In-build answers still never move an idea's level. They do feed the skill's record, under the rules below. The reason they can: a sealed call is made before the result is shown to anyone, so neither the screen nor the agent can supply it.

### 6.2 What makes a scored call

A call is scored only if all of these hold:

1. **Sealed first.** It is stored before the result is shown to the person or the agent.
2. **Checked by something that happened.** A runner result, a fact from the task timeline, a count from the record, or a registered source. Where a model reads part of the check, both passes must agree (`../spec/learning.md` section 12, rule 6). Otherwise the call is unscored.
3. **Typed or tapped by the person.** In the Room or an inline card. A call relayed through the agent's chat is shown in the journal and listed under Practised. The agent could have shaped it.
4. **The engine chose the case.** The person can start any moment themselves with `firsthand call`. Those calls are shown and are useful, but they are not scored, because picking your own cases flatters the record.
5. **The outcome arrived.** A task that was abandoned, or a check that could not run, leaves the call unscored. It never counts as a miss.

Each scored call is a match or a miss. "Don't know" is scored as a miss for the skill, because the call gave no information, and is never counted as a sure miss. Skips are not scored. They are counted and shown (section 7).

**Practised** is not a level. It lists relayed calls, self-started calls and calls on moments without a check. It sits under its own heading, as Met does for ideas.

### 6.3 The fixed answer

For any set of scored calls, the engine computes what one fixed answer would have scored: always "fails without the change", always "nobody notices", always the most common time band. It is the score of not thinking. It is shown next to the person's count every time, and the level rules use it.

To make the comparison possible the record must contain both kinds of outcome. `checking.md` section 9 already asks about one in three moments on clean cases. That rule is what keeps "nothing is wrong" a live answer and keeps the fixed answer from scoring nearly everything.

### 6.4 The ladder

| Level | What it claims | Goes up when |
| :- | :- | :- |
| **Not yet** | Nothing | Default |
| **Shown** | The person has made this kind of call correctly when it was not the easy answer | Two matching scored calls on different days. At least one is a catch: the outcome was the less common one for that moment in this person's record, or the call named one location out of four or more |
| **Reliable** | The person's calls carry information: they beat the fixed answer | In the current window the person's matches exceed the fixed answer's score, the calls come from at least two moments or two path categories, and the window holds no sure miss on a high-stakes change |
| **Held** | The calls stay good over time and away from the build | Reliable at two checks at least 21 days apart, plus one piece of evidence away from the build: a drill for that skill passed on sealed keys, on another project or a bank family |

**The window.** The most recent scored calls for the skill, reaching back until there are at least ten calls and at least three of each kind of outcome. Design defaults, with reasons: ten is reachable in a few weeks under a cap of three moments a day shared across skills, and three of each outcome is the least that lets the fixed answer be beaten by more than one lucky call. Where the window cannot be filled, the level stays at Shown and the map says how many calls are missing.

**Going down.**

- Reliable to Shown: at any re-check where the window no longer beats the fixed answer, or on a sure miss on a high-stakes change.
- Held to Reliable: the same two causes.
- Shown does not drop to Not yet. It is a statement about the past and stays true. It goes stale instead (section 6.6).
- Never more than one step for one event. The map states the cause in a line: "Reliable to Shown on 12 Nov: sure miss on a ledger change."

**Why these rules.** They mirror the idea ladder: two pieces of evidence on different days to go up, one step at a time, a longer gap and a second kind of evidence for the top. One lucky call cannot move a level and one wrong check cannot either, which is the same protection as rule 7 of the accuracy rules.

### 6.5 What counts as a call, per skill

| Skill | Scored calls come from | Match means |
| :- | :- | :- |
| 1 Verification | V1, V2, V4, V5 in `checking.md` | The prediction equals the runner result |
| 2 Reading systems | R1, R2, R3 | The prediction equals the run, the reference search or the trace |
| 3 Debugging | D1, D4, D5 | The named cause passes the undo-the-fix check, or the named commit equals the bisect result |
| 5 Framing | 2.1, 2.3 in `directing.md` | The sealed prediction about the result equals the timeline |
| 6 Delegating | 3.1, 3.2 | The named location holds the rework, or "nothing wrong" and no rework |
| 7 Small changes | 4.1, 4.2, 4.3 | The part lands alone in the runner as predicted |
| 10 Calibration | C2, C3, C4, C5 and the confidence pairs from C1 | Section 6.7 |
| 11 Product judgment | P2, P3, P4, P5 | The search, the runner or the source agrees with the call |
| 4, 8, 9 | Their own files | Any moment there whose answer is a sealed call with an event check follows the same rules |

### 6.6 Evidence age and fading

- Every skill level shows when its newest scored call was made.
- Fading follows the skill level. Not yet: the full form of each moment. Shown: the one-line form. Reliable and above: asked only on high-stakes changes, with the checks otherwise running silently. This is the fading table in `checking.md` section 9, keyed to the skill.
- Fading slows the flow of new calls, so a level could go stale exactly because the person earned it. To prevent that, when the newest scored call is older than 21 days the next eligible trigger asks in the one-line form whatever the fading state, inside the daily cap. Design default 21 days: the third step of the existing interval ladder.
- Past 60 days with no scored call the map shows "not checked lately" in place of the level, as it does for ideas.

### 6.7 The level for calibration itself

Calibration is the one skill whose calls are about the person's own record, so it has its own match rules.

- C2 and C3 match when the actual value falls in the chosen band. The fixed answer is the band that was right most often.
- C5 matches when the number is within one of the record's count.
- C4 matches when the rating and the result agree: "Yes" with a right prediction, or "No" with a wrong one. "Partly" is unscored.
- C1 pairs are judged as a set, not one by one.

Reliable for skill 10 needs, in the window: the C2 to C5 calls beat the fixed answer, the order of the confidence bands holds (sure calls matched more often than fairly sure, and those more often than guesses, each band with at least five calls), and at most one sure miss. Design default for one: "sure" should mean nearly always, and a window of ten cannot support a finer rule.

Held needs Ten calls passed with the same band order on sealed keys.

### 6.8 The level for product judgment

Most of what matters in product judgment cannot be checked from a build. So its level carries a plain statement of what it covers.

- With no outcome source in any project, skill 11 can reach Reliable on P2, P3 and P4 alone. The map then reads: "Reliable at: finding what already exists, what an outcome needs, who notices a change. No evidence on: whether features helped."
- Held needs at least two P5 calls scored against a source, plus Maintainer's call passed. Without a source, Held is not available and the map says why.
- The "who is it for" line from P1 is kept in the journal next to the outcome and is never scored.

---

## 7. Showing progress honestly

### 7.1 What the Room shows

**The skills map.** One row per skill. Each row shows the level, the counts behind it, the fixed answer, how much was answered, and the age. Example:

```
SKILLS   orbit-pay and 1 other project                               14 Nov

10 Calibrating your own judgment        Shown
   Scored calls, last 30 days    6 of 11 matched     One fixed answer would score: 6 of 11
   By confidence                 Sure 7 of 9   Fairly sure 4 of 8   A guess 2 of 5
   Asked 19, answered 13, skipped 6      Newest scored call: 2 days ago
   To reach Reliable: beat the fixed answer over the window. You are level with it.
   Ideas: the first "done" is inside the task (Recalled) · start from how similar work went (Not yet)

11 Product judgment                     Reliable at: what already exists, who notices a change
   Scored calls, last 60 days    9 of 12 matched     One fixed answer would score: 7 of 12
   No evidence on: whether features helped. 1 source registered, first reading due 2 Dec.
   Asked 15, answered 12, skipped 3      Newest scored call: 5 days ago
   Ideas: an edited test is a changed promise (Applied) · look in three places before building (Recalled)
```

**The decisions journal.** One line per call, newest first: the task, what the person said, how sure, what happened, and a link to the check output. A line can be reopened: if a merged change is reverted later, or a P5 number arrives, the line gains a second outcome and the date. The first outcome is never overwritten. The journal is the raw material. The map is a count over it.

**The trend.** For each skill, this window next to the one before, as counts: "This window 9 of 12. The one before 6 of 11." No chart is drawn until both windows are full. The weekly line (`../PRODUCT.md` section 5.11) may pick one of these facts.

**Time.** For skill 10 the progress screen shows the three parts of active time per merged task for the last ten tasks, as plain horizontal bars with the numbers written on them. This is the person's own log, shown whether or not they made a call.

### 7.2 Rules for honesty

1. **Counts, not percentages, below twenty calls.** "6 of 11" cannot be mistaken for precision. Design default twenty: below it a percentage changes by five or more points with a single call.
2. **The fixed answer is always next to the count.** A count alone flatters whenever one outcome is common.
3. **The share answered is always shown.** `SKILLS.md` notes that a follow-up study was inconclusive because developers skipped the tasks they did not want. The same thing can happen here: a person who skips the hard calls has a better record than they should. A skip is never a miss, but "asked 19, answered 13" is on every row.
4. **"Clean" means "nothing found before merge".** The checks see failing tests, corrections, CI, review comments and reverts. They do not see a defect that reaches users unnoticed. Every clean outcome is labelled with what was looked at. A later revert in git reopens the line.
5. **Every count says how it was checked.** Runner, timeline, record, source, or model-read. Model-read results carry that label and their quotes, and can be disputed (`../spec/learning.md` section 12, rule 8).
6. **Age is always shown.** A level with no recent call reads "not checked lately".
7. **Levels go down in plain sight.** The drop, its date and its cause stay on the row until the level is regained.
8. **Skills are never combined.** No overall score, no rank, no comparison with other people, no streaks or points. This is the existing rule in `../PRODUCT.md` section 5.9.
9. **The map says what it does not show.** A fixed footer: "These counts describe your calls in these projects. No study has tested whether they carry over to other work." That is the open question `SKILLS.md` states.
10. **Time is reported as measured, with its blind spot.** The tool never prints "time saved". It prints time spent, in three parts, and says that it cannot see what happened while the agent worked.

### 7.3 What the person sees in the agent

Nothing new by default. The reveal for each moment is the only in-agent output. The session-start offer may carry one fact from the map when a level changed since the last session: "Product judgment moved to Reliable for what already exists. Details in the Room." It is one line, with the link, and "quiet" turns it off.

---

## 8. Keeping it rare

These moments live inside the existing limits: one moment per break, one per task, three a day across all skills, and the selection order in `checking.md` section 9. This file adds:

- **C1 costs no slot.** It is a tap on a call already being made. It is attached to about half of eligible calls and never to a call the person answered with "Don't know".
- **C2, C3 and C5 never share a task.** The engine picks the one whose match record is weakest.
- **Task start holds one moment.** At a task start the candidates are V1, the brief moments in `directing.md`, C2, C5 and P1. The existing order applies: the skill with the least recent evidence wins.
- **C3 and P5 are not in the build.** C3 arrives after a merge and P5 at a session start. Both go to the Room inbox and count against the three review items a day, not against moments in the build.
- **P2 must not stall the agent.** It fires as the agent plans. Nothing blocks the tool call. If the person has not answered when the agent creates the file, the search still runs and its result goes to the inbox as a note when it finds a strong hit on a new dependency or an open pull request.
- **Fading** follows section 6.6. Under pressure signals every moment here is silent.
- **Skip** always works, with one word or one tap, with no follow-up question.

---

## 9. What to build first

**Build C1, How sure, first.**

- It needs no trigger, no check and no key of its own. It rides on the revert test, which `checking.md` names as the first moment to build overall.
- It costs the person three seconds and the build nothing.
- It starts filling the record with pairs of confidence and outcome from the first day. Every level rule in section 6 and every count in section 7 depends on that record existing, and it takes weeks to fill.
- It forces the two pieces everything else here needs: the scored-call record with the fixed answer beside it, and the journal line.
- It is identical on every agent surface, because the tap is in the Room or an inline card and the check is the host's.

**For skill 11, build P4, Who notices, first.** Its check, old tests on new code, is one more mode of the scratch runner. It needs no model, no source and no setup, and it tells the person a true thing about their change at the moment a pull request opens.

Order by what each adds to the engine:

| Step | Moment | New machinery |
| :- | :- | :- |
| 1 | C1 How sure | Confidence on sealed calls, scored-call record, fixed answer, journal line, skill row on the map |
| 2 | P4 Who notices | Runner mode: base tests on head source. Schema diff for API description files |
| 3 | C2 Time call, C3 Where it went | Active time and its three parts from the task timeline |
| 4 | C5 Outside view | Per-category counts from the record |
| 5 | P2 Already there | Search across names, manifest and `gh` lists. Scoring at merge |
| 6 | P3 Cut line | Runner mode: revert one file group at a time against an acceptance check |
| 7 | C4 Understanding call, Ten calls | Self-rating paired with a Predict item |
| 8 | P1 Who and signal, P5 Did it help | Outcome sources, baseline, the dated follow-up |
| 9 | Looking back, Kept or cut, Maintainer's call | Journal sampling, history reading, the pull request bank |

---

## 10. Summary table

| Moment | Trigger | The person does | The check | Model involved |
| :- | :- | :- | :- | :- |
| C1 How sure | Rides on any sealed call | One tap: guess, fairly sure, sure | The host moment's check, stored as a pair | No |
| C2 Time call | First prompt of a task | Picks a band for active time and for the share after "done" | Task timeline at merge | No |
| C3 Where it went | Merge commit, no C2 on the task | Recalls the share of time after "done" | Task timeline | No |
| C4 Understanding call | Pull request opens on a high-stakes change, diff unopened | Rates own understanding, then answers one Predict item | Sealed runner result against the rating | No |
| C5 Outside view | Task start in a category with five or more past tasks | Types own past rework count | Count from the record | No |
| Ten calls (drill) | Started by the person | Ten Predict items, each with a confidence | Sealed runner results by band | No |
| Looking back (drill) | Started by the person | Recalls an old prediction and its outcome | The sealed call and outcome in the record | Only for free-text recall |
| P1 Who and signal | First prompt of a feature task | Names who it is for and a readable signal | Signal looked up now and in the diff at "done" | No |
| P2 Already there | Plan or tool call adds a module or dependency | Names existing work or says "nothing" | Search of code, manifest and open pull requests. Scored at merge | No. Hits are listed, not judged |
| P3 Cut line | "Done" with parts the acceptance check never runs | Picks the parts the outcome needs | Runner reverts each part and runs the acceptance check | No |
| P4 Who notices | Pull request opens with edited tests or interface changes | Picks who is affected | Base tests run on head source, plus schema diff | No |
| P5 Did it help | Chosen date after merge, source exists | Predicts the number's band | Registered source against baseline | No |
| Kept or cut (drill) | Started by the person | Predicts what happened to five old features | Git history and sources | No |
| Maintainer's call (drill) | Started by the person | Predicts merged or closed, with a reason | Real outcome, stated reason | For the reason only |

---

## 11. What this asks of the engine

New `moment` breaks: `merged`, `plan`, `followup_due`. The others used here (`task_start`, `done`, `pr_open`) exist in `checking.md` section 11.

New commands, each mirrored as an MCP tool:

| Command | Used by | Does |
| :- | :- | :- |
| `check time` | C2, C3, the progress screen | Computes active time and its three parts for a task from the timeline |
| `check history` | C5, Looking back | Counts past tasks by path category and rework |
| `check old-tests` | P4 | Runs the base's test files against the head's source in the scratch runner |
| `check schema` | P4 | Diffs the API description file between base and head |
| `check exists` | P1, P2 | Searches names, the manifest and `gh` pull request and issue lists for given terms |
| `check parts` | P3 | Reverts one file group at a time and runs the named acceptance check |
| `source add`, `source run`, `source list` | P1, P5, Kept or cut | Registers and runs the person's own outcome commands |
| `call` | Any moment | Lets the person start a moment themselves. Recorded as self-started, not scored |

New event types, in the format of `../spec/architecture.md` section 2: `call.confidence`, `call.scored`, `call.reopened`, `skill.level_changed`, `source.read`.

New fields on the existing call record: `confidence` (guess, fairly, sure, or none), `scored` (match, miss, unscored, with the reason), `fixed_answer` for the window it belongs to, `chosen_by` (engine or person), `provenance` (typed, captured or relayed).

Per-project settings in the record's `config/`: the idle limit, the registered sources, the follow-up interval for P5, and the API description file path if any.

Room screens touched: the moment card gains the confidence row. The skills map gains the skill rows in section 7.1. The journal gains reopened lines. The progress screen gains the time bars. Layout follows `../../learning-experience/design-system.md`. This file fixes the wording and content only.

---

## 12. Limits, stated plainly

- **Time saved is not measurable here.** The tool never sees the same task done without the agent. It reports time spent and its parts.
- **Active time is an estimate.** It is built from event times and an idle limit. Work done away from the machine, or on a machine with no import, is missing. The card says when a timeline has gaps.
- **Rework before merge is not correctness.** A change with no rework can still be wrong in production. Section 7.2 rule 4 labels this. Linking calls to production outcomes needs sparse, slow data, and `SKILLS.md` says whether that works is unknown. It is not attempted beyond reverts visible in git.
- **Small counts.** A solo builder may produce ten scored calls for a skill in a month. Levels built on that are coarse on purpose, and the counts are shown so the person can see how thin the evidence is.
- **P1's "who" has no check.** It is recorded and shown with the outcome. It is the one input in this file without checkable feedback.
- **P2 cannot rule on "the same thing".** It lists hits and says where it searched. A duplicate behind a different name can be missed.
- **P3 depends on an acceptance check.** Without one it is not asked. A weak acceptance check will mark needed parts as not needed. The card names the check it used.
- **P4 depends on the old tests.** A promise no test ever covered will not show up. The card says how many old tests ran.
- **P5 needs a source.** Most small projects will have none at first. Skill 11 then has no evidence on outcomes, and the map says exactly that.
- **Product judgment rests mostly on domain knowledge.** These moments train the checkable habits around it. They do not supply knowledge of users, and nothing in a build can.
- **Does calibration feedback improve outcomes?** `SKILLS.md` says no study tests this. The design does not wait for one. Each card shows the person a true fact about their own forecasts and their own time, which is worth having whether or not it changes anything else.
