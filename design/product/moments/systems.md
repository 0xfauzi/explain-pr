# Moments: the system and its risks

> **Superseded.** The rules in this file (budgets, fading, scoring, levels, what counts) are replaced by `../spec/learning.md`. Several moments here were merged, renamed or cut: `../spec/learning.md` section 13 maps every name. Use this file for worked examples and wording ideas only. On-screen copy is in `../spec/experience.md`.

Skills 4, 8 and 9 from `design/skills/SKILLS.md`: security and risk judgment, operating software in production, and design, architecture and data modelling.

These three skills are about the system that outlives the change: who can reach it, how it behaves when it runs, and what shape it is left in. An agent's change usually works on the day. These moments ask about the request nobody meant to allow, the failure nobody sees, and the structure nobody chose. Almost every check here is run, not judged: a request is sent, a fault is injected, a row is written to a scratch database.

Running example: **orbit-pay**, the payments service used in `directing.md`. It has `POST /charges`, a `charges` table, a ledger, a webhook handler and a client for the card processor. Each charge belongs to a merchant, and merchants call the API with their own key. The task used in most examples here: the person asks the agent to add partial refunds. That brings a `POST /refunds` endpoint, a `refunds` table and a refund worker that calls the processor.

File names, figures and output inside the example cards are illustrations of the format. They are not measurements.

---

## 1. What every moment here shares

### 1.1 Reused from `directing.md`

Section 1 of `directing.md` applies here without change:

- **Work product and sealed call** (1.1). A sealed call is typed in the Room or an inline card, stored before the outcome exists, and never passed to the agent.
- **The task timeline** (1.2), including rework events.
- **The scratch runner** (1.3). Checks run in a copy, after the turn. The build never waits.
- **Path categories** (1.4).
- **Selection** (1.5). At most one moment per task across all moments files. Nothing blocks a tool call. "skip" always works. A moment fades to its one-line form after the person's last three sealed calls for it matched, and a miss brings the full form back once. Each moment has two or three prompt forms and the engine rotates them.
- **Model grading** (1.6) only where text must be read, under `spec/learning.md` section 12.
- **Ideas** (1.7). Each moment records one system-level idea, and it returns as a review item in a new form, under the limit of 3 a day.

### 1.2 New pieces this file needs

| Piece | What it does | Used by |
| :- | :- | :- |
| **Probe runner** | A probe is a small test in the project's own test harness. It sends one request or input and records the response and the rows left behind. Every probe has a **control**: the same request in its legitimate form, which must succeed. A probe whose control fails is dropped and never shown, so a 404 from a wrong URL is never reported as "refused". Common probes are templates in the engine. Others are written by a separate context that never saw the build conversation | 2.1, 2.5, 3.4, drills |
| **Scratch database** | A local or container database loaded with the project's seed or fixture rows, or a sample the person has pointed the engine to. The Runner already has this for Replay and for Undo plan | 2.2, 2.4, 4.2, drills |
| **Fault injector** | In the scratch copy, the engine makes one named call raise, time out or return its failure value, then runs the tests that reach that call. It captures log records with their levels, metric calls, responses, exceptions that were caught, and database rows | 3.1, 3.2, drills |
| **Signal inventory** | A static list, built by the Miner, of what the project can show about itself: log calls and their levels, the log configuration, metric calls, alert rule files, health endpoints. Each entry has a `file:line` | 3.1, 3.3 |
| **Target resolver** | For a command seen at before_tool, works out which host and database it would act on, from its arguments, the environment and the config files it loads. It records the host and database name only, never a credential. Hosts are classed as local or not local. The person can label a host once in the Room ("staging", "production") | 2.2 |
| **Ship events** | A deploy command, or a merge or push to the deploy branch, seen at before_tool. The engine then reads what followed at the next session_start: reverts, commits and branches named as fixes that touch the same files, and failed deploy runs from `gh run list` | 3.3, 3.4 |
| **Import graph** | Which package imports which, and which modules reference a table or an outside client. Built from the source by the Miner, compared before and after a change | 4.1, 4.3 |
| **Decisions journal** | The Room's list of decisions the person made, each with the reason they gave, the facts at the time and what happened after. Stored in the record | 2.2, 4.1, 4.4 |

### 1.3 What the tool cannot see, said plainly

- **Production.** The engine sees the repo, git, the session and the commands the agent runs. It does not see dashboards, pagers or a hosting provider's console. A production event exists for the tool only when it passes through a session (a pasted log, a log command, a revert) or leaves a trace in git. An incident handled entirely elsewhere is invisible, and no moment is asked about it.
- **Before a risky step.** The hook dispatcher never returns allow or deny. The pause before an irreversible command is the agent's own approval prompt, where the person has one. The tool shows its card beside that prompt. If the command runs with no pause, the same moment is asked afterwards and is headed "already ran". The tool does not teach or change approval settings.
- **Provider state.** The engine cannot see a managed database's snapshots or a cloud account's real permissions. Where a check depends on those, the card says what was not seen.

### 1.4 Triggers shared with other files

| Signal | Moments that could fire | Rule |
| :- | :- | :- |
| A step a revert does not undo | Undo plan (`directing.md` 4.2), Target call (2.2) | Undo plan while the step is in a diff being shaped. Target call when the command is about to run against a host that is not local |
| A migration in the diff | Undo plan, Landing order (`directing.md` 4.3), Invariant (4.2) | Invariant when the migration adds a table, a column that holds money or state, or a relationship. Undo plan when it drops, renames or changes a type |
| A new dependency | Real package (2.3), Second way (4.1) | Real package the first time a name is seen and the person has not said they know it. Second way when an existing dependency or module already covers the purpose |
| First "done" claim | Skill 1's revert test, Boundary probe (2.1), others | The one whose changed paths carry the highest-stakes tag, then the skill longest without practice |

---

## 2. Skill 4: security and risk judgment

Five moments. The first is the one to build first (section 5).

### 2.1 Boundary probe

**Trigger.** The first "done" claim at turn_end, where the diff adds or changes a route handler, or changes lines in a path tagged auth, input handling or personal data. The diff property is a new route registration, or changed lines inside a function that reads the request body, parameters or headers.

**What the person does.** About 60 seconds. Two sealed lines: what the handler takes on trust, and one request that must be refused.

In the agent, on a surface with no inline card:

```
Firsthand: POST /refunds is new. One sealed question about who can call it: <Room link>   ("skip" to pass)
```

In the Room:

```
BOUNDARY  orbit-pay  POST /refunds  (new in this change)

Sealed, not sent to the agent
  Who can send this request, and what does the handler take on trust?
  [ type here ]
  One request that must be refused. Be specific.
  [ type here ]

[ Seal and test ]   [ Skip ]
```

Example answers: "Any merchant with an API key. It trusts the charge_id in the body." and "A refund for a charge that belongs to another merchant."

**The check.** Executable, in the scratch runner, on the code as the agent left it.

1. A separate context turns the person's request into a probe with its control. If the line is too vague to become a request, the card says so, shows step 2 only and moves nothing.
2. The engine adds template probes for the kind of boundary it found. A handler that loads a record by an id from the request: another owner's id. An amount field: zero, negative, more than the original. Any write: the same request twice.
3. Each result is a response and the rows left behind. No model judges whether the code is secure.

**Shown afterwards.**

```
BOUNDARY, TESTED  POST /refunds

Control        merchant A refunds its own charge         201, 1 row in refunds
Your request   merchant A refunds merchant B's charge    201, refund created
               The handler loads the charge by id and does not compare its merchant.
               refunds/handlers.py:31
Also sent
  amount greater than the charge       422, refused
  amount of -500                       201, refund of -500 created
  the same request twice               2 refunds created

You named 1 of the 3 that got through.
[ Send these 3 to the agent as failing tests ]   [ Not now ]
```

The last line is the moment paying for itself: the probes are real tests, and the build gets them.

**Idea recorded.** "Knowing who is calling is not knowing what they may touch. Every record loaded by an id from the request needs an ownership check." Instance: refund on another merchant's charge.

**How it comes back.** Days later, on a different route: "GET /charges/{id}/receipt in orbit-pay. Which line decides that this merchant may read this charge? Give the file, or say there is none." The key is the probe result for that route plus the `file:line` of the check, if it exists. Later, turned around: three handlers are shown and one lacks the check. Later still, further away: a download link for an invoice file, the same question.

### 2.2 Target call

**Trigger.** before_tool on a command from the irreversible list, where the target resolver says the host is not local or cannot tell. The list: migration commands (`alembic upgrade`), SQL sent with a drop, truncate, delete, or update with no where clause, `terraform apply` and `destroy`, `git push --force`, deletes of stored files, and deploy commands.

**What the person does.** About 20 seconds, beside the agent's approval prompt.

```
BEFORE IT RUNS  alembic upgrade head

Sealed
  Which database will this change?
  [ Local ]  [ Staging ]  [ Production ]  [ Not sure ]
  If it is wrong, what gets you back, and when was that last tried?
  [ type here ]
```

**The check.** Read from the system, and partly executable.

- **Target.** The resolver's host and database name, with where it came from (`file:line` or the name of the environment variable).
- **What will run.** The pending migrations rendered as SQL without connecting (`alembic upgrade --sql`), and which statements destroy data.
- **Way back.** Whether a down migration exists, and the result of running up then down on the scratch database, as in Undo plan.
- **Backup.** Any backup command or dump file seen in the timeline or the repo, with its age. If none: the card says none was seen and that the engine cannot see the provider's snapshots.

**Shown afterwards.**

```
TARGET  alembic upgrade head

You said        Staging
It points at    db.orbit-pay.example / orbit_prod
                from DATABASE_URL, set by .env.production:3
Will run        2 migrations. 0033 drops charges.legacy_ref. Those values are destroyed.
Way back        The down migration recreates the column, empty. Tried on a scratch database.
Backup          None seen in this session or the repo.
                Firsthand cannot see your provider's snapshots.
```

If the command had already run when the person answered, the same card is headed ALREADY RAN. The decision and these facts go to the decisions journal.

**Idea recorded.** "Before a step that cannot be undone, read the target from the system, not from memory, and know whether the way back has ever been tried."

**How it comes back.** A new command in a new place: "The agent proposes `redis-cli FLUSHALL` to clear a test cache in orbit-pay. Name the one fact you check before it runs, and where you read it." The key is the host in the cache config, with `file:line`. Later, turned around, so the idea does not become fear of every command: "Three commands. Which one needs no check at all?" where one acts only on the scratch copy.

### 2.3 Real package

**Trigger.** after_tool on an install command (`pip install`, `uv add`, `npm install <name>`), or a manifest or lockfile diff at turn_end that adds a top-level name the project did not have.

**What the person does.** About 20 seconds, sealed.

```
NEW DEPENDENCY  acquirer-sig   (added for webhook signature checks)

Sealed
  Do you know this package?
  [ Used it before ]  [ Heard of it ]  [ Never seen it ]
  It will run inside the webhook service. Name one thing that process holds
  that you would not want a stranger's code to read.
  [ type here ]
```

**The check.** A registry lookup and facts from the repo. The lookup sends the package name to the public registry, which the install already did. Nothing else leaves the machine.

- Whether the name exists, its first release date and release count, and whether its linked source repo declares the same package name.
- Names one edit away that are far more widely used.
- Whether installing it runs a script.
- From the lockfile diff: how many other packages came with it.
- From the repo: where it is imported, and the names (not values) of the secrets that service reads.

SKILLS.md cites the reason this moment exists: models recommend packages that do not exist, and the same wrong names recur.

**Shown afterwards.**

```
ACQUIRER-SIG, LOOKED UP

Exists            Yes. First release 3 weeks ago, 2 releases.
Source repo       None linked.
Similar name      acquirer-signature: same purpose, 6 years of releases.
Install script    Yes, runs at install.
Came with it      4 more packages.
Runs in           webhooks/verify.py:3. That service reads PROCESSOR_SECRET and DATABASE_URL.

You said: Heard of it. You named: the processor secret. It is in reach.
[ Tell the agent to use acquirer-signature ]   [ Keep ]   [ Remove ]
```

**Idea recorded.** "A dependency runs with everything its process can reach, and installing it can already run its code. Check it is the one you meant first."

**How it comes back.** As a different event: "A minor update to an existing orbit-pay dependency adds new packages underneath it. What two facts do you look at before accepting the lockfile?" The key is a bank family. Later: "Which orbit-pay service could do its job without the processor secret in its environment?" The key comes from the import graph and the secret names each service reads.

### 2.4 Smallest grant

**Trigger.** A diff property at turn_end: the change adds or widens a grant. The engine matches SQL grants and role names in migrations, compose files and connection settings, a `permissions:` block in a CI workflow, a cloud policy file, and a new service reading an existing secret.

**What the person does.** About 45 seconds. Work product, since the answer is a real configuration choice.

```
ACCESS  refunds/worker.py connects as role orbit_admin

What does the refund worker need? List tables and what it does to each.
  [ type here ]
```

Example answer: "Read charges. Insert and update refunds."

**The check.** Executable for database roles. On the scratch database the engine creates a role with exactly the stated grants and runs the worker's tests under it.

- Tests that fail with a permission error show what the person left out.
- The role actually configured is then compared with the stated one: everything it can do beyond the list.

For CI permission blocks and policy files the check is static: what is granted against what the code uses, each with a `file:line`. The card then says "read from the files, not run".

**Shown afterwards.**

```
ACCESS, TRIED on a scratch database

Your list        charges: read.  refunds: insert, update.
Worker tests     2 fail: permission denied on ledger_entries (insert)
                 The worker writes the ledger entry. refunds/worker.py:74
With that added  All worker tests pass.
Configured now   orbit_admin: owner of every table. Can drop charges.
                 The worker uses 3 of those rights.
[ Send the narrower role to the agent ]   [ Not now ]
```

**Idea recorded.** "Grant what the job uses. The gap between granted and used is what a bug or a leaked credential gets for free."

**How it comes back.** In another place where grants live: "orbit-pay's deploy workflow has a token with write access to the repo. Which steps use it, and what could a step that does not need it do with it?" The key is read from the workflow file. Later: the question from the other side, "the webhook handler only verifies and enqueues: what should its role be unable to do?"

### 2.5 What leaves

**Trigger.** A diff property at turn_end: the change adds a log call, an error response body or an outbound request whose arguments include a whole request or record, or a field tagged as personal or secret. Tags come from field names (email, card, token, secret, authorization) and the person's corrections in the Room.

**What the person does.** About 30 seconds. A sealed prediction.

```
WHAT LEAVES  refunds/worker.py  (new log line on processor errors)

A refund fails at the processor. Which of these end up in the log?
  [ refund id ]  [ amount ]  [ customer email ]  [ card last 4 ]
  [ processor API key ]  [ none of these ]
```

**The check.** Executable. The engine runs the tests for the failing path in the scratch runner, captures the log output and the requests the harness's fake services received, and searches the captured text for the literal fixture values of every tagged field.

**Shown afterwards.**

```
WHAT LEFT, CAPTURED from the failing-path tests

Log line     "refund failed: <ProcessorError request=...>"   refunds/worker.py:61
Found in it  refund id, amount, customer email
             processor API key: the error carries the request headers
You said     refund id, amount
Log config   This logger ships to the outside log service. config/logging.yaml:12
```

**Idea recorded.** "Logging a whole object logs every field it has now and every field added later. Choose the fields by name."

**How it comes back.** As an inventory question: "orbit-pay is adding error reporting to an outside service. Name the places customer data can leave orbit-pay through." The key is the signal inventory's list of outbound sinks. Later, in another system: an analytics event built from a user record.

### 2.6 Drills for skill 4

**Break in.** The engine picks an existing orbit-pay route, favouring ones with few tests on their refusal paths. The person lists up to three requests it should refuse. About 5 minutes. Check: each becomes a probe with a control and is run, with the template probes beside them. Shown: which were refused, which got through, and which template probes the person did not think of. Any that got through can be sent to the agent as failing tests.

**Key walk.** The person lists every place the processor secret can be read: files, services, CI jobs, images, logs. About 4 minutes. Check: a mechanical search of environment files, compose and CI config, the secret names each service reads, the captured log output from 2.5, and a pattern scan of git history. The card shows locations only, never values. Shown: places named and found, places found and not named, and places named that the engine could not confirm, marked as not checked.

---

## 3. Skill 8: operating software in production

Four moments. The limit in section 1.3 applies to all of them.

### 3.1 Silent failure

**Trigger.** `gh pr create`, `gh pr merge`, or a push to the deploy branch seen at before_tool, where the diff changes non-test code reached by a route, a worker or a scheduled job.

**What the person does.** About 45 seconds, sealed.

```
BEFORE IT MERGES  refunds/worker.py  send_refund()

Sealed
  If this breaks in production, what is the first thing that shows it?
  [ An error response to the caller ]  [ An error-level log line ]
  [ A metric or alert: which? ]  [ Nothing would show ]
  Who or what sees that?
  [ type here ]
```

**The check.** Executable. The fault injector breaks the changed function two ways in the scratch copy: it raises, and it times out. The engine runs the tests that reach it and captures what the system showed. It then looks each captured signal up in the signal inventory: is that log level shipped anywhere, does any alert rule name that metric.

This is the revert test turned around. The revert test asks whether a test notices the fix missing. This asks whether anything notices the code failing.

**Shown afterwards.**

```
BROKEN ON PURPOSE  refunds/worker.py  send_refund()

Fault        the processor call times out
Caller sees  Nothing. The worker catches the error and moves on.  worker.py:58
Log          1 line at DEBUG: "refund attempt failed"
             DEBUG is not shipped.  config/logging.yaml:12
Metric       None
Refund row   Stays "pending". Nothing retries it.

You said     "An error-level log line. I would see it in the worker logs."
```

**Idea recorded.** "A failure that is caught and not counted is invisible. Every failure path needs one signal that a person or an alert will see."

**How it comes back.** As the design of a signal: "Refunds in orbit-pay can stay pending forever. Name the query or number that would show stuck refunds, and the age at which one counts as stuck." The key is a bank family, with the tables read from the schema. Later, in another system: a nightly export job that fails without a trace.

### 3.2 Half done

**Trigger.** A diff property at turn_end: the change adds or alters a function that both writes to the database and calls an outside system (the processor client, a queue, a mailer), found from the import graph. Also a config diff that changes a timeout or retry count on such a call.

**What the person does.** About 45 seconds. A sealed prediction.

```
HALF DONE  refunds/worker.py  send_refund()

The processor accepts the refund. The response is lost on the way back.
  What does the refunds row say?     [ pending ]  [ failed ]  [ succeeded ]
  The worker retries. How many refunds does the processor now have?
                                     [ 1 ]  [ 2 ]
```

**The check.** Executable, where the project has a fake processor in its tests. The fault injector lets the fake record the call and then raise a timeout. The engine reads the rows, runs the retry path, and counts the calls the fake received. Where there is no fake, the moment is not asked.

**Shown afterwards.**

```
HALF DONE, TRIED

After the lost response   refunds row: "failed". Processor: 1 refund made.
After the retry           refunds row: "succeeded". Processor: 2 refunds made.
                          The retry sends no idempotency key.  processor/client.py:88
You said                  pending, then 1.
```

**Idea recorded.** "Between two systems there is always a moment where one has done the work and the other does not know. Decide what your record says in that moment, and make the retry safe to repeat."

**How it comes back.** In the opposite direction: "The processor sends orbit-pay the same webhook twice, and the second arrives before the first is committed. What must be true so the ledger gets one entry?" The key is a bank family. Later: an order email that is sent before the order's transaction commits.

### 3.3 Watch call

**Trigger.** A ship event at before_tool: a deploy command, or a merge or push to the deploy branch.

**What the person does.** About 20 seconds, sealed.

```
SHIPPING  refunds worker

After this is live, what will you look at, and what would make you roll back?
  [ type here ]
How do you roll back? Name the command or the step.
  [ type here ]
```

**The check.** Two parts, and a limit.

- **Now.** Whether the named rollback is real: the command or script exists in the repo or the timeline, a revert of the change applies cleanly in the scratch copy, and whether a migration sits between this release and the last one.
- **Later, at the next session_start.** From the timeline: whether any log or status command ran after the ship event, and the ship events read from git (section 1.2).
- **Limit.** If nothing went wrong, there is no check on whether the watching was good. The card says so. It shows only whether a look happened.

**Shown afterwards, at the next session.**

```
AFTER SHIP  refunds worker, shipped Tuesday 16:10

You said you would watch   "refund failures in the worker log for ten minutes"
Seen in the session        No log or status command after the deploy. Session ended 16:12.
Rollback you named         "fly releases rollback". Not found in this repo or session.
Since then                 Wednesday 09:40, commit "fix: refund worker crashes on
                           charges with no merchant_id"
Ship to fix                17 h 30 min
```

**Idea recorded.** "Shipping ends when you have seen it work, not when the deploy command returns."

**How it comes back.** As a choice of what to watch: "orbit-pay is about to ship a change to webhook verification. Name the one number that would tell you in the first minutes that real webhooks are being rejected." The key is a bank family, checked against the signal inventory. If the number does not exist in orbit-pay, the card says that too.

### 3.4 Roll back or fix forward

**Trigger.** A production event passing through a session. Signals: a prompt containing a pasted traceback or log lines whose paths or hosts are not local, the agent running a production log command (`fly logs`, `kubectl logs`), a `git revert` of a commit already on the deploy branch, or a branch named as a hotfix.

**During the event the tool asks nothing.** It records the timeline. The moment is asked after the fix has merged, at the next session_start.

**What the person does.** About 90 seconds.

```
AFTER THE INCIDENT  refunds failing, Wednesday

1. Which change introduced it?
   [ #212 partial refunds ]  [ #214 worker retries ]  [ #215 merchant cleanup ]  [ Older ]
2. Would rolling that change back have stopped the harm sooner than the fix did?
   [ Yes ]  [ No ]   Why, in one line:  [ type here ]
```

**The check.** Executable.

1. **Which change.** The engine takes the test the fix added, or builds a probe from the failing request in the pasted log. It runs it against each merge since the last clean ship, in the scratch runner, and finds the first one where it fails.
2. **Rollback.** It reverts that change on top of the commit that was live, then runs that test and the full suite. It also checks for a migration in between, since a revert that leaves a schema the old code cannot read is not a rollback.
3. **Times.** From the timeline: first error in the pasted log, first prompt about it, fix merged.

**Shown afterwards.**

```
INCIDENT, REPLAYED

Introduced by    #215 merchant cleanup. The fix's test passes before it, fails after.
You said         #212 partial refunds.
Rollback tried   Revert of #215 applies cleanly. The test passes. Full suite passes.
                 No migration in between.
Times            First error 09:02. Fix merged 09:40.
                 A revert was available from the first minute.
You said         No: "the fix was simple".
```

The result also counts for skill 3, whose check is whether the named cause was right.

**Idea recorded.** "In an incident, stop the harm first. When the last change is the cause and the data allows it, rolling back is quicker than understanding."

**How it comes back.** With the condition that changes the answer: "Same incident, but #215 also dropped a column the old code reads. Is rollback still the first move? What do you do instead?" The key is a bank family. This links back to the Undo plan idea from `directing.md`.

### 3.5 Drills for skill 8

**Incident replay.** From the project's own history. The Miner finds fix commits that added a test, and reverts on the deploy branch. The Runner restores the state just before the fix in a container. The Room shows only the symptom: the failing request and the log output. The person names where they would look first, which change introduced it, and whether to roll back or fix forward. About 10 minutes. Check: the same bisection and rollback rehearsal as 3.4, plus what was actually done, from the commit history. Shown side by side: the person's call, what the replay found, what happened at the time.

**Game day.** The engine picks one fault from a list (the processor is down, the database is slow, a webhook arrives twice) and applies it in the scratch copy. Before it runs, the person predicts which signals fire and what state a customer's charge or refund ends in. About 5 minutes. Check: the captured run from the fault injector. Shown: the prediction beside the logs, metrics and rows that resulted, with the signals that stayed silent marked.

---

## 4. Skill 9: design, architecture and data modelling

Four moments. These are the moments where the tool is most careful about claiming a right answer. Three have mechanical checks on a fact the decision depends on. One (4.4) has no check at the time, and says so.

### 4.1 Second way

**Trigger.** A diff property at turn_end: the change adds a new module file, a new class or helper, or a new top-level dependency. Also a phrase in the agent's report: "I created a new", "added a helper", "introduced a".

**What the person does.** About 30 seconds. One sealed pick, then a decision with a reason.

```
NEW IN THIS CHANGE  refunds/retry.py  retry_with_backoff()

Sealed
  Does orbit-pay already have something that does this?
  [ Yes, I know where ]  [ No ]  [ Not sure ]

Then
  [ Keep it ]  [ Use what exists ]  [ Merge the two ]     Why, in one line:  [ type here ]
```

**The check.** Mechanical search, shown as facts.

- Existing code that makes the same outside calls in the same shape, has high token similarity, or has a near name. Each candidate is shown with its `file:line` and its number of callers.
- An existing dependency in the lockfile that covers the same purpose as a new one.
- A separate context may propose more candidates. Each must cite a `file:line`, and the engine confirms the lines exist before showing them.

If nothing is found, the card says "nothing found" and lists what was searched. The tool does not say whether keeping or merging is right. It shows what the decision was made against.

**Shown afterwards.**

```
ALREADY IN ORBIT-PAY

New            refunds/retry.py  retry_with_backoff()       1 caller
Already there  common/http.py:44  with_retries()            6 callers
               Both: loop, catch ProcessorTimeout, sleep, double the delay.
Difference     The new one has no limit on attempts.
Also new       dependency "backoff". orbit-pay already locks "tenacity".  common/http.py:9

You said       No, nothing existing.
Your decision  Use what exists. "One retry policy for every processor call."
[ Tell the agent to use with_retries() ]
```

The decision and its reason go to the decisions journal. The Decision review drill (4.5) later shows what became of it.

**Idea recorded.** "Two ways to do one thing means every fix has to be made twice, and one day it will be made once."

**How it comes back.** As a consequence to predict: "orbit-pay converts amounts to minor units in two places. A rounding fix lands in one. Which requests now disagree with the ledger?" The key is read from the two call sites. Later, turned around so the idea does not become "always share": "A proposed shared helper would have one caller. What does it cost to add it now?"

### 4.2 Invariant

**Trigger.** A diff property at turn_end: a new migration file or a changed schema or model definition, where the change adds a table, a relationship, or a column that holds money or state. Asked at most once per migration.

**What the person does.** About 60 to 90 seconds.

```
SCHEMA  migrations/0034_create_refunds.py

One rule that must be true of every row, always.
  [ type here ]
What enforces it?
  [ The database ]  [ Application code ]  [ Nothing yet ]
Rows that already exist: what happens to them?
  [ type here, or "none affected" ]
```

Example answers: "Refunds for a charge never add up to more than the charge." and "Application code."

**The check.** Executable, on the scratch database.

1. A separate context turns the rule into a query that counts violations, and one write that would break it. The card shows the query with "That is my rule" and "No". On "No", nothing is graded.
2. The engine applies the migration to the seed or sample rows and counts violations before and after.
3. It attempts the breaking write directly on the database.
4. Where the harness can do it, it sends the breaking request through the API, once alone and twice at the same time.

**Shown afterwards.**

```
RULE, TRIED on a scratch database

Your rule        Refunds for a charge never add up to more than the charge.
Read as          SELECT r.charge_id FROM refunds r JOIN charges c ...
                 HAVING SUM(r.amount_minor) > c.amount_minor
                 [ That is my rule ]  [ No ]
Existing rows    0 break the rule before. 0 after.
Direct write     Second refund of 800 on a 1000 charge already refunded 800:
                 accepted by the database.
Through the API  One at a time: refused, 422.
                 Two at the same time: both accepted.
You said         Enforced by application code. True for one request at a time only.
```

At the Deep setting only, the card offers "Your line": the person writes the constraint or the locking line themselves and the engine reruns steps 3 and 4.

**Idea recorded.** "A rule kept only in application code holds until two requests race or something else writes to the table. State the rule, then put it where every writer must pass."

**How it comes back.** On another table: "Every charge in orbit-pay should have exactly one ledger entry. Where would you enforce that, and what single write would test it?" The key is the result of that write on the scratch database. Later, as migration judgment: "You add a not-null merchant_id to charges. Old rows have none. Name the three steps and what the table looks like between them." Later still, in another domain: stock that must not go below zero.

### 4.3 New edge

**Trigger.** An import graph difference at turn_end: the first import between two top-level packages, an import that closes a cycle, or a module outside a table's owning package that now queries that table directly.

**What the person does.** About 40 seconds.

```
NEW LINK  refunds/handlers.py now reads the processor's response fields directly

Sealed
  If orbit-pay changed card processor, how many modules would have to change?
  [ 1 ]  [ 2 or 3 ]  [ 4 or more ]

Then
  [ Accept the link ]  [ Move it behind processor/client.py ]     Why:  [ type here ]
```

**The check.** Mechanical. The engine counts the modules that reference the processor client's types or response fields, before and after this change, and lists them with `file:line`. It reports a cycle if one now exists. The count is a fact. Whether the link is acceptable stays the person's call, and the card does not grade it.

**Shown afterwards.**

```
WHO KNOWS THE PROCESSOR'S FORMAT

Before this change   2 modules: processor/client.py, webhooks/handler.py
After                4 modules: + refunds/handlers.py:40, refunds/worker.py:66
You said             1
Cycle                None.
Your decision        Move it. "Refunds should get our own result type."
```

**Idea recorded.** "Count who knows a detail. Every module that knows another system's format changes when that system does."

**How it comes back.** On a different detail: "Which orbit-pay modules know the layout of the ledger table? Name them." The key is the reference list from the import graph. Later, as a prediction checked against history: "The charges table gains a currency column. Which files will the change touch?" using a real past change of the same kind where the repo has one.

### 4.4 Decide and date it

**Trigger.** The agent presents options: an ask-user tool call with choices, or plan text with "Option A", "alternatively", "we could either". Also a prompt in which the person picks an approach for something tagged schema, public interface or new dependency.

**What the person does.** About 60 seconds. Work product: it goes to the agent as the decision and to the journal as the record.

```
DECISION  where idempotency keys live

Your choice           [ Postgres table ]  [ Redis with expiry ]
The cost you accept   [ type here ]
What would show this was the wrong choice, and when will you look?
                      [ type here ]      Look again in  [ 2 weeks ]  [ 1 month ]  [ 3 months ]
```

Example: "Postgres table. Cost: one more write inside every charge. Wrong if the keys table needs its own cleanup job that keeps failing, or charges slow down. Look in 1 month."

**The check.** Stated plainly: there is no check at the time. A design choice has no outcome yet, and a model's opinion of it is not feedback. The check is delayed and comes from the repo.

On the look date the entry returns as one of the day's review items, with facts gathered since the decision:

- commits that touched the files the decision created, and how many were named as fixes
- rework events on those files from the timeline
- whether the chosen structure still exists or was replaced
- whether the thing named as the sign of a wrong choice can be seen in the repo (for example, a cleanup job was added and then changed repeatedly)

The person then marks it Held, Wrong or Too early. That mark is theirs. The tool supplies the facts and does not grade the mark. The pair of decision and outcome feeds skill 10.

**Shown on the look date.**

```
DECISION, ONE MONTH ON  idempotency keys in a Postgres table

You accepted   "one more write inside every charge"
You said it would be wrong if   "the keys table needs its own cleanup job that keeps failing"
Since then     charges/idempotency.py changed 4 times, 1 named as a fix.
               jobs/expire_keys.py was added 9 days after the decision and changed twice.
               The table and its code still exist.
[ Held ]  [ Wrong ]  [ Too early to say ]
```

**Idea recorded.** "A design decision is a bet. Write down the cost you accepted and what would change your mind while you still remember the alternatives."

**How it comes back.** The dated return above is the main form. The idea also returns ahead of a new decision: "You are choosing between a queue and a scheduled job for the refund worker. Before you pick, name the main cost of the one you prefer." The key is a bank family of costs for each option. This item is marked as practice and moves no level, because it has no outcome to check against.

### 4.5 Drills for skill 9

**Decision review.** From the decisions journal, or mined from history where the journal is still thin: a module, dependency or table that was added some weeks ago. Before seeing anything, the person predicts what became of it: how many callers it has now, how often it changed, whether something similar was added beside it, whether it still exists. About 5 minutes. Check: each prediction against git history and the import graph. Then one ungraded question: "Would you decide the same today?" Shown: the predictions beside the facts.

**Break the schema.** The Room shows the current schema of one area of orbit-pay, for example charges, refunds and ledger entries. The person names up to three states that should never exist and that they think the database would accept. About 5 minutes. Check: the engine attempts each as writes on the scratch database. Shown: accepted or refused for each, with the constraint that refused it. A variant uses a public repo from the Fresh repo list, so the schema is one the person has never seen.

---

## 5. What to build first

**Boundary probe (2.1).**

Reasons:

- Of the three skills here, security has the strongest evidence that the problem is real (SKILLS.md, skill 4: strong). The same section cites a study where people with an AI assistant wrote less secure code and were more confident in it. A sealed call followed by a real request is aimed directly at that gap between confidence and result.
- Its check is a test run. It needs only the scratch runner that skill 1's revert test already requires. It needs no database container and no fault injector.
- Its trigger is a diff property read from git at a "done" claim. That works the same on every agent surface, with or without hooks, which keeps the founder decision of the same outcome everywhere.
- It leaves the build better. The probes that got through are failing tests the person can hand to the agent in one tap.
- The one fallible step, turning a sentence into a request, is contained. The control request must pass or the probe is dropped, and the template probes need no model at all. The first build can ship templates only.

Second: **Invariant (4.2)**. It brings the scratch database into regular use, which Undo plan, Landing order, Target call and Smallest grant all share. Third: **Silent failure (3.1)**. It brings the fault injector, which Half done and the Game day drill reuse.

---

## 6. Summary table

| Moment | Skill | Trigger signal | Person does | Check | Kind of check |
| :- | :-: | :- | :- | :- | :- |
| Boundary probe | 4 | "Done" with a new or changed route handler, or auth, input or personal-data paths in the diff | Sealed: what is trusted, one request to refuse | That request and template probes sent as tests, each with a passing control | Executable |
| Target call | 4 | before_tool on an irreversible command whose target is not local | Sealed: which database, what gets you back | Resolved host and database, pending SQL, down migration on scratch, backups seen | Read from the system, part executable |
| Real package | 4 | Install command, or a new top-level name in the lockfile | Sealed: know it or not, what it could read | Registry facts, near names, lockfile diff, import site and secret names | Lookup and static |
| Smallest grant | 4 | Diff adds or widens a role, permission block or secret reader | Lists the least the job needs | Tests run under a role with exactly that list, then configured against used | Executable for database roles, static elsewhere |
| What leaves | 4 | Diff adds a log line, error body or outbound call carrying a record or tagged field | Sealed: which fields end up in the log | Failing-path tests run with capture, fixture values searched | Executable |
| Silent failure | 8 | Pull request, merge or push to the deploy branch with changed runtime code | Sealed: the first thing that shows it broken | Fault injected, logs, metrics, responses and rows captured, matched to the signal inventory | Executable |
| Half done | 8 | Diff changes code that writes the database and calls an outside system | Sealed: the row's state and the retry count | Fake processor records then times out, rows read, retry run, calls counted | Executable. Not asked without a fake |
| Watch call | 8 | Deploy command or merge to the deploy branch | Sealed: what to watch, how to roll back | Rollback exists and applies, look commands seen, reverts and fixes after | Timeline. No check on a clean ship |
| Roll back or fix forward | 8 | Pasted production error, production log command, revert on the deploy branch. Asked after the fix | Picks the change, says whether rollback was quicker | Fix's test bisected across merges, revert rehearsed, migrations checked | Executable |
| Second way | 9 | Diff adds a module, helper or dependency, or the report says "created a new" | Sealed: does it already exist. Then keep, reuse or merge | Search for existing code and dependencies with caller counts | Mechanical. The decision is not graded |
| Invariant | 9 | New migration or schema change adding a table, relationship, money or state column | One rule, what enforces it, what happens to old rows | Violations counted before and after, breaking write tried directly and through the API | Executable |
| New edge | 9 | New import between packages, a cycle, or a table queried from outside its package | Sealed: how many modules would change. Then accept or move | Count of modules referencing the detail, before and after | Mechanical. The decision is not graded |
| Decide and date it | 9 | Agent presents options, or the person picks a structural approach | Choice, cost accepted, sign it was wrong, look date | None at the time. Repo facts on the look date | Delayed, from history |

Drills: Break in and Key walk (skill 4), Incident replay and Game day (skill 8), Decision review and Break the schema (skill 9).

## 7. What this file leaves to others

- Whether the tests prove the "done" claim belongs to skill 1. Boundary probe and Silent failure reuse its runner and share its trigger under the rule in section 1.4.
- Naming the cause of a failure belongs to skill 3. Roll back or fix forward supplies one of its checks.
- Shaping a change so it can be undone, and the order it lands in, belong to skill 7 (`directing.md` 4.2 and 4.3). Target call takes over only when the command is about to run on a real system.
- Whether the person's confidence matches their results over time belongs to skill 10. Every sealed call here, and every dated decision from 4.4, is a pair it can use.
- The Room screens for these cards, including the decisions journal, follow `design/learning-experience/design-system.md`. The blocks in this file fix the wording and the content, not the layout.
