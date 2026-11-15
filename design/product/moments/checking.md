# Moments: verification, reading systems, debugging

> **Superseded.** The rules in this file (budgets, fading, scoring, levels, what counts) are replaced by `../spec/learning.md`. Several moments here were merged, renamed or cut: `../spec/learning.md` section 13 maps every name. Use this file for worked examples and wording ideas only. On-screen copy is in `../spec/experience.md`.

Part of the Firsthand design. This file designs the practice for three skills from `../../skills/SKILLS.md`:

- Skill 1: verification. Checking work and claims against evidence.
- Skill 2: reading and understanding systems you did not write.
- Skill 3: debugging and diagnosis.

It replaces the code-level moves in `../spec/learning.md` section 2 for these skills. It reuses the engine, the record, sealing, the levels and the accuracy rules from `../spec/`. Where a rule is reused, the section is named.

Every moment below names its trigger, what the person does, the check, what is shown, the idea it records and how the idea comes back. All example wording uses one project: orbit-pay.

---

## 1. Decisions in this file

1. **The check is run by the engine, on real code, wherever that is possible.** All fourteen moments get feedback from something that is actually run: a test, a revert, a coverage run, a reference search, a bisect, the person's own experiment. Two of them (R4 and D1) add a part read by a model, under the accuracy rules in `../spec/learning.md` section 12, and say so on screen.
2. **One shared piece of machinery does most of the work: the scratch runner** (section 4). It copies the current tree to a scratch folder, changes one thing, and runs tests there. The revert test, the missing case, unrun lines, the path trace, the bisect and the cause check all use it.
3. **In-build answers are predictions. They are compared, never graded, and never move a level.** This is the existing rule (`learning.md` section 2.1). The agent's output is on screen during a build, so an in-build answer cannot show what the person knows alone. Levels move on the delayed return and on drills.
4. **At most one moment per break, one per task, three a day across all skills.** The three a day is the existing budget (`../PRODUCT.md` section 5.4). Section 9 says which moment wins when several fire.
5. **The first moment to build is V2, the revert test.** Reasons in section 10.
6. **No experiments are proposed.** Each choice is made from the research in `SKILLS.md` or from how git and test runners work.

---

## 2. The running example: orbit-pay

orbit-pay is a payments service the person is building with a coding agent. Python, pytest, Postgres.

| Component | Path | What it does |
| :- | :- | :- |
| API | `orbit_pay/api/` | `POST /charges`, `POST /refunds` |
| Refunds | `orbit_pay/refunds/service.py` | Refund rules, partial refunds |
| Idempotency | `orbit_pay/idempotency/store.py` | One result per idempotency key |
| Ledger | `orbit_pay/ledger/post.py`, `balance.py` | Double-entry postings, balances |
| Webhooks | `orbit_pay/webhooks/handler.py` | Events from the card processor |
| Reconciliation | `orbit_pay/recon/job.py` | Nightly match of ledger against the processor's settlement file |
| Money | `orbit_pay/money.py` | Amounts, currency, rounding |

Three pieces of work recur in the examples:

- **Task A:** make refunds idempotent, so a retried refund request does not refund twice.
- **Bug B:** the webhook `charge.settled` sometimes arrives before the charge row is committed, and the handler drops it.
- **Regression C:** after a change to rounding in `money.py`, the reconciliation totals are off by one cent for some currencies.

---

## 3. What the tool can detect

These are the signals the triggers below use. Hook names differ per agent. The adapters in `../spec/surfaces.md` map them.

| Code | Signal | Source on hook tiers (T2) | Source on T0 and T1 |
| :- | :- | :- | :- |
| S1 | A prompt is submitted | Prompt-submit hook, text captured verbatim | The skill tells the agent to call `moment task_start` |
| S2 | A tool call starts or ends | Pre and post tool hooks: command text, exit code, paths read and edited | The agent calls `moment` at the named break |
| S3 | A turn ends | Stop hook, with the agent's final message | The agent calls `moment done` with its report text |
| S4 | Git state | The engine reads it: diff against the base branch, changed paths, added and edited tests, commit log | Same |
| S5 | Test results | Exit code plus failing test ids parsed from runner output (pytest, jest, go test, cargo test, or JUnit XML where configured) | The engine runs the test command itself |
| S6 | A pull request opens or is reviewed | Tool call `gh pr create` or a push to a branch with an open PR | `moment pr_open`, `moment pr_review`, or `firsthand pr` |

Two facts keep the learning outcome the same on every surface:

- Every trigger has a T0 form: the agent reports the break, and the engine confirms it from git and from its own test run. Hooks make the trigger reliable. They do not change the moment.
- Every check is an engine command. It needs a local shell and git, nothing from the agent. In cloud sessions with no local shell, the moment is queued and runs at the next local session through the import step.

The engine learns the project's test command once, at `init`: from `pyproject.toml`, `package.json`, `Makefile`, `go.mod`, `Cargo.toml` or the CI file. If it cannot find one it asks once. Without a test command, moments that need a test run are not offered in that project, and the Room says why.

---

## 4. The scratch runner

Most checks below are one call to this runner.

1. **Copy.** The runner makes a scratch folder outside the project (mode 0700). It adds a detached git worktree at the current commit, then copies in the uncommitted tracked changes and the untracked files that are not ignored. The real working tree is never changed, nothing is committed, nothing is pushed.
2. **Baseline.** It runs the target tests in the scratch copy with nothing changed. The result must match the result in the real tree. If it does not (the tests need a service or a setting the scratch copy lacks), the check ends as "cannot run here" and the moment is not asked.
3. **Change one thing.** Revert the source files to the base, add one test case, turn on coverage, or check out an earlier commit.
4. **Run and record.** It runs the tests again and stores the result as a `check.ran` event: the command, the exit code, the failing test ids and a hash of the output. No source code goes into the record.
5. **Clean up.** The scratch folder is deleted when the task ends.

Rules:

- It runs only the project's own tests, the same code the person and the agent already run. This is the "project's own tests, now" class in `../spec/security.md` section 2.1, so no container is needed. Drills that run old commits use the container rules there.
- It never runs while the agent's own test command is running, so the two do not collide on a shared test database.
- It starts in the background as soon as the trigger fires. If the result is not ready when the person answers, the reveal arrives in the Room inbox and the build goes on.
- It has a time limit per project, set by the person. Design default: two minutes, because a check slower than that arrives after the person has moved on. Past the limit the check is dropped and nothing is asked.

---

## 5. Skill 1: verification

The system-level point: "done" is a claim. The work is to decide what evidence would support it and to look at that evidence, not at the report.

### V1. Name the proof

- **Trigger:** S1 on the first prompt of a task: the branch has no commits ahead of the base, or the agent presents a plan, or `moment task_start`. Skipped for prompts the engine classes as questions or one-line edits.
- **The person does:** writes the one observable check that would prove the task worked, with its expected result. Target: under a minute.
- **Prompt:**

```
Before the agent starts on idempotent refunds (skip ok):
What one check would prove it worked? Give the action and the result you expect.
```

Example answer: "Send the same refund request twice with the same key. Expect one refund row and the same response both times."

- **The check:** when the agent reports done, a separate context writes the person's sentence as one test against the finished interface. The runner runs it twice: on the base (source files reverted) and on the head. A proof should fail on the base and pass on the head.
- **Shown after:**

```
Your check, as a test: two POST /refunds with key "r-1", then count refunds.
On the code before the change: fails (2 refunds).
On the code now: passes (1 refund, same response).
This check tells the old code from the new. It is in tests/refunds/test_idempotent.py if you want to keep it.
Back to: idempotent refunds. Next: open the pull request.
```

If it passes on both: "Your check passes on the old code too. It does not show that this change did anything." If the test does not match what the person meant, they say "not what I meant" and nothing is recorded.

- **Idea recorded:** a proof is a check that gives a different result with and without the change.
- **Comes back:** days later, for a different piece of work in the project. "The reconciliation job must flag a settlement the ledger does not have. Which check proves that: (free text)". The key is a set of sealed tests the engine has already run on that change's base and head. The person's answer is made executable and run the same way.
- **Notes:** the person's check is theirs to give to the agent as part of the brief. That is good practice and the feedback is unchanged, because base and head still have to differ.

### V2. Revert test

- **Trigger:** S3, where the agent's final message makes a completion claim ("done", "fixed", "implemented", "all tests pass"), and S4 shows the task's diff changes source files and adds or edits at least one test.
- **The person does:** before reading the summary, picks the test they think proves the change and predicts what happens if the change is undone and the test is kept. One tap or one word. Target: twenty seconds.
- **Prompt:**

```
The agent reports the refund change is done. Before you read its summary (skip ok):
It added 3 tests. If the change to refunds/service.py and idempotency/store.py were undone,
would test_same_key_refunds_once still pass?
Fails without the change / Still passes / Don't know
```

- **The check:** the runner reverts every non-test file in the diff to the base, keeps the test files, and runs each added or edited test. No model is involved.
- **Shown after:**

```
You expected: fails without the change.
What happened, with the change undone:
  test_same_key_refunds_once       fails on the assertion (2 refunds, expected 1)
  test_refund_response_is_stable   still passes
  test_refund_amount_validated     cannot run (imports a name the change added)
One test proves this change. One would pass whether or not the change exists.
Back to: idempotent refunds. Next: read the summary.
```

Three outcomes are reported differently on purpose. "Fails on the assertion" is proof. "Still passes" is no proof. "Cannot run" is weak proof: it shows the test depends on new code, not that the behaviour is right.

- **Idea recorded:** a test that passes without the change is not evidence for the change.
- **Comes back:** days later, with a change the person has not been asked about, taken from project history. "Three weeks ago the ledger began rejecting postings that do not balance. This is the test added with it (test shown, source hidden). Would it fail without that change? Say what you looked at." The key is the runner's result on that commit, sealed before the question is shown.
- **Fades:** after the person's calls have been right on two different days, the prompt drops to the short form (`Revert test, 3 new tests: which one would still pass?`). Once the idea is at Applied it is asked only on high-stakes diffs (section 9). The runner still runs silently, and a "still passes" result on a high-stakes diff is always put in the Room inbox.

### V3. Claim check

- **Trigger:** S3, where the final message contains a claim of a fixed, checkable kind: tests pass, the build passes, lint is clean, a migration ran, a named file or endpoint exists. The engine matches these with a pattern list per claim kind.
- **The person does:** reads the claims as a short list and marks the one they would want evidence for before accepting. Target: fifteen seconds.
- **Prompt:**

```
The agent's report makes three claims (skip ok):
  1. All 214 tests pass.
  2. The migration adding refunds.idempotency_key was applied.
  3. No other code calls create_refund directly.
Which one would you check first?
```

- **The check:** the engine tests each claim itself. Tests: it runs the full test command. Migration: it runs the project's migration status command. "No other callers": the reference search from R2. On hook tiers it also reads the session's tool log: was the supporting command run at all, and was it run after the last edit.
- **Shown after:**

```
You chose: 3.
  1. Tests: 214 pass. Checked now by running them. The agent last ran them before its final edit.
  2. Migration: applied. Checked with the migration status command.
  3. Other callers: 1 found, recon/job.py:88. The claim does not hold.
Back to: idempotent refunds. Next: look at recon/job.py:88.
```

- **Idea recorded:** a report is a claim. Evidence is a command and its result, run after the last change.
- **Comes back:** as a new case from the person's own history, with the report text and a list of the commands that were run. "Which claim in this report had no run behind it?" The key is the tool log and the engine's own run, sealed. On projects with no hook log, the return uses a bank family with the same structure.
- **Notes:** claims outside the fixed kinds are not checked and not listed. The card says "claims the tool can check", so the person does not read the list as complete.

### V4. The missing case

- **Trigger:** S4 at a done break: the diff adds or edits tests for a function or endpoint that takes input (the test file calls it with literal values).
- **The person does:** names one input or situation the tests do not cover, with the result they expect. Target: one minute.
- **Prompt:**

```
The agent's refund tests cover: full refund, a repeated key, an unknown charge (skip ok).
Name one case they miss, and what should happen.
```

Example answer: "Refund 30.00, then refund 80.00, on a 100.00 charge. The second should be rejected."

- **The check:** the case is written as one more test in the shape of the existing ones. In the build the working agent may write it, because the case is useful to the build anyway. The runner runs it.
- **Shown after:**

```
I ran: refund 30.00, then 80.00, on a 100.00 charge. You expected: second one rejected.
What happened: second refund accepted. Total refunded 110.00.
The tests did not cover this, and the code does not handle it.
Back to: idempotent refunds. Next: decide whether to fix it in this change.
```

Other outcomes: "Handled as you expected. The tests did not cover it; the code was right. Keep the test?" and "An existing test already runs this input: test_partial_then_over." The third is found by comparing the literal inputs of existing tests, and is labelled as a match by value.

- **Idea recorded:** tests show the cases someone thought of. The useful question is which case nobody thought of: boundaries, sequences, repeats, failures in the middle.
- **Comes back:** with a different feature. "These are the test names for webhook signature checking (names only). Name one case they miss." The answer is made executable and run against the current code. A case that fails, or that passes and is not matched by an existing test's inputs, counts as a found gap.
- **Notes:** the tool reports what happened, not who is right. If the code does something other than the person expected, the behaviour may be correct and the expectation wrong. The card says so and leaves the decision to the person.

### V5. Unrun lines

- **Trigger:** S6, or a done break with green tests, where the diff changes at least two source files and the project has a coverage tool the runner can turn on (coverage.py, c8, `go test -cover`, cargo-llvm-cov).
- **The person does:** predicts which changed file has changed lines that no test runs. One tap. Target: twenty seconds.
- **Prompt:**

```
Tests are green on the refund change. Green covers only what ran (skip ok).
Which changed file has changed lines that no test runs?
  refunds/service.py / idempotency/store.py / webhooks/handler.py / None of them
```

- **The check:** the runner runs the tests with coverage and intersects the unrun lines with the diff's changed lines.
- **Shown after:**

```
You chose: none of them.
What ran: 41 of 52 changed lines.
Never run by any test: idempotency/store.py:61-71, the branch taken when two requests
with the same key arrive at the same time.
Back to: idempotent refunds. Next: your call on whether that branch needs a test.
```

- **Idea recorded:** a passing suite says nothing about lines it did not run. The unrun lines are usually the error and concurrency paths.
- **Comes back:** as a system-level question on another change. "The reconciliation change went in with green tests. Which kind of path is least likely to have been run by them: the happy path, the missing-file path, or the currency conversion?" The key is the coverage result for that commit, sealed. Because this form is a choice, it caps at Recalled (`learning.md` section 5.1).
- **Notes:** asked on clean diffs as well (section 9), so the question does not give away its answer.

### Drills for skill 1

**Proof audit.** Away from the build, in the Room.

- Source: commits in the person's projects, at least 7 days old, that changed source and tests together.
- The engine picks a commit, runs the revert test on it in a container, and seals the result.
- The person sees the commit message and the tests, not the source diff, and marks each test: proves the change, or would pass anyway.
- Check: the sealed runner result. Executable, so it can move the level.
- Shown: the result per test, then the source diff.

**Escaped defect review.** A decision review against what happened after.

- Source: a past change whose lines were later fixed, found by blame plus a test that fails on the original commit and passes on the fix (the rule from Check, `learning.md` section 3.2).
- The person sees the original change and the tests it shipped with, and answers: "This shipped and was later fixed. What check at the time would have caught it?"
- Check: the answer is written as a test and run on the original commit. If it fails there, the check would have caught the defect. The fix's own test is then shown for comparison.
- If the answer cannot be made executable, a model reader compares it with the fix's test under the accuracy rules, and the result is labelled as model-read.

---

## 6. Skill 2: reading and understanding systems you did not write

The system-level point: understanding means being able to say what a part does, what reaches it and what depends on it. The checks here are the running system and the reference graph, not a description.

### R1. Predict the run

- **Trigger:** S2, before a deterministic step runs for the first time on code the agent wrote this session and the person has not yet opened or been asked about: a new entry point, a script, a migration dry run, a job. The engine refuses steps it marks non-deterministic (timing, randomness, network), as in `learning.md` section 2.1.
- **The person does:** predicts the observable result in one line. Target: thirty seconds. The step is not held: if no answer comes before it finishes, the output stays folded in the Room until the person answers or skips.
- **Prompt:**

```
The agent is about to run the new reconciliation job on the sample settlement file,
which has 40 rows, 2 of them not in the ledger (skip ok).
What will the job report?
```

- **The check:** the real run. The key is the command's output.
- **Shown after:**

```
You expected: 2 flagged, 38 matched.
What happened: 3 flagged, 37 matched.
The gap: recon/job.py:52 compares amounts as floats, so one matching row differs by rounding.
Back to: reconciliation job. Next: the agent is looking at the third flag.
```

The "gap" line is written by a model reader, cites `path:line`, and is checked mechanically for the cited line existing (accuracy rule 1).

- **Idea recorded:** the system-level idea behind the gap, here: money compared as floats gives false mismatches. If the prediction was right, the idea recorded is the mechanism the run confirmed.
- **Comes back:** as a new instance. "The ledger balance check sums postings per account. Given these 3 postings (shown), what balance does it report?" The key is the sealed output of running it.

### R2. Who else is affected

- **Trigger:** S4 at a done break or S6: the diff changes the signature, return shape or stored format of a function, endpoint, table or message that has at least one reference outside the changed files.
- **The person does:** names one caller or consumer outside the diff that the change affects. Free text, a file or a component name. Target: thirty seconds.
- **Prompt:**

```
This change makes create_refund return the existing refund when the key repeats,
where it used to raise (skip ok).
Name one place outside this diff that depends on the old behaviour.
```

- **The check:** two engine steps. First a reference search for the changed symbols: the language server if the project has one, else tree-sitter tags, else a name search labelled "by name, may include false matches". Second, the runner runs the full tests with coverage to see which references are exercised by a test that ran.
- **Shown after:**

```
You named: the webhook handler.
References to create_refund outside this diff:
  recon/job.py:88             catches DuplicateRefund to count retries. No test runs this line.
  api/refunds.py:31           updated in this diff's tests.
  webhooks/handler.py         no reference found.
The reconciliation job still expects the old error.
Back to: idempotent refunds. Next: decide what recon/job.py:88 should do now.
```

- **Idea recorded:** the reach of a change is its callers and consumers, not its diff.
- **Comes back:** on another shared part, days later, with no diff in front of the person. "If `money.round_amount` changed from half-up to half-even, name two components that would see different numbers." The key is the sealed reference list. Each named component is marked present or absent.
- **Notes:** static search misses dynamic calls, queue consumers and other services. The card lists what was searched, so "none found" is not read as "none exist".

### R3. Trace the path

- **Trigger:** S2 at the start of a task: the agent's first reads and edits fall in a component where the person has no commits and no earlier moments in the record. Asked once per component.
- **The person does:** lists, in order, the components one request passes through. Free text. Target: one to two minutes. The agent explores in parallel and is not held.
- **Prompt:**

```
This task changes webhook handling, a part of orbit-pay you have not worked in (skip ok).
A charge.settled event arrives from the processor.
List the components it passes through, in order, until the ledger changes.
```

- **The check:** the runner runs an existing test for that entry point under a tracer and records which components are entered and in what order. Python uses coverage contexts or `sys.settrace`. Where the language gives coverage but not order, the comparison is on the set only, and the card says so. A component is a top-level package by default. The person can rename or regroup components in the Room.
- **Shown after:**

```
Your path:   webhooks, ledger
Traced path: webhooks, idempotency, api (charge lookup), money, ledger
Missing from yours: idempotency (duplicate events are dropped here), money (amount is converted here).
Traced with tests/webhooks/test_settled.py::test_settled_posts_to_ledger.
Back to: Bug B. Next: the agent is reading webhooks/handler.py.
```

- **Idea recorded:** the request path for that entry point, as a system fact about this project, plus the general idea it shows (here: every external event passes a duplicate check before it changes state).
- **Comes back:** in a new form: a what-if on the same path. "If the idempotency store were unavailable, at which step would a charge.settled event stop, and would the ledger change?" The key comes from a sealed runner result with that component stubbed to fail. A second return uses a different entry point (`POST /refunds`) with the same listing task.

### R4. Review first

- **Trigger:** S6: the person asks the agent to review a pull request, opens a PR branch, or runs `firsthand pr`. Reused from `learning.md` section 2.5, raised to system level.
- **The person does:** before the PR body, the agent's summary or any comments are shown, writes two lines on what the change does to the system, and lists any defect with a location. Or says "looks clean". Target: three to five minutes. The person starts this one, so it does not count against the unprompted budget when started with `firsthand pr`.
- **Prompt:**

```
PR 212, 9 files. The description and the agent's review are hidden until you answer.
1. In two lines: what does this change do to the system?
2. Anything wrong? Give a location for each, or say "looks clean".
```

- **The check:** two parts.
  - Findings: "Show it with a test?" A test that fails on the PR head confirms the finding at once. Later CI results and later commits to the flagged lines settle the rest as "likely right" or "unconfirmed". A "looks clean" on a PR that later needed a fix confirmed by a test is a miss.
  - The two lines: the engine lists the components the diff touches (from paths). A model reader marks which of them the person's two lines mention, with a quote for each, under the accuracy rules. This part is model-read and is labelled so.
- **Shown after:**

```
Your summary mentions: refunds, idempotency.
The diff also changes: ledger/post.py (posting order), a migration on refunds.
Your finding at idempotency/store.py:61: confirmed, your test fails on the PR head.
Now showing the PR description and the agent's review.
```

- **Idea recorded:** what the person missed, as a system idea (here: a change to posting order is a ledger change, even inside a refunds PR).
- **Comes back:** as a Check drill item on a different past change, and as a short recall: "A refunds change reorders ledger postings. What would you want to know before accepting it?" The recall is model-graded against sealed points that cite `file:line`.

### Drills for skill 2

**Map it.** Mapping an unfamiliar system.

- Source: a component in the person's projects that they did not write (agent-authored or inherited, at least 7 days old), or a public repo from the open task set.
- The person, without the agent, answers three things in the Room: the entry points, the data it reads and writes, and the path of one named request.
- Check: entry points and data stores are compared with facts the engine extracts (route tables, CLI definitions, table names in queries and migrations). The path is compared with a sealed tracer run, as in R3.
- Shown: the person's map next to the extracted one, with each difference linked to `path:line`. No timer. The drill shows a size ("one component, about 6 files").

**Blast radius.** What depends on this.

- Source: a shared function or table in the person's project.
- The engine applies one small sealed change in a scratch copy (for example, `round_amount` returns one cent less for one currency), runs the whole suite in a container, and seals which tests fail, grouped by component.
- The person sees the function and the change, and names the components whose tests will fail.
- Check: the sealed run. Executable, so it can move the level.
- Shown: components named and hit, named and not hit, and hit but not named.
- The change exists only in the scratch copy. Nothing is ever seeded into the person's code.

---

## 7. Skill 3: debugging and diagnosis

The system-level point: name a cause before changing anything, and choose a check whose result would differ between that cause and the next most likely one.

### D1. Call it

- **Trigger:** either of two signals.
  - S5: a test fails that exists on the base branch and is not edited in the diff. This leaves out the expected red of a test written first.
  - S1: the person's prompt contains a pasted stack trace or raw error output. In the cited live streams, pasting raw errors to the agent was the mark of high reliance (`SKILLS.md` skill 3).
- **The person does:** one line for the cause and one line for the first check. Target: under a minute. The agent keeps diagnosing in parallel and holds back only its conclusion until the person answers, skips, or its diagnosis is ready and the person has not started typing (`learning.md` section 2.2).
- **Prompt:**

```
test_settled_posts_to_ledger failed: expected 1 posting, found 0 (skip ok).
Before any fix: one line for the cause, one line for the first thing you would check.
The agent keeps looking meanwhile.
```

Example answer: "The handler looks up the charge before the charge row is committed. Check: log whether the lookup returns None when the event arrives."

- **The check:** three parts, from what happens next.
  - Where the fix landed: the engine records the tree at the red run and at the first green run for that test, and lists the files and functions that changed between them.
  - Whether the fix is the cause: the runner undoes only those changes and runs the test. If it fails again, the fix is causal.
  - Whether the named cause matches: location is compared mechanically (did the person name the component where the fix landed). The mechanism is compared by a model reader against points drawn from the fix diff, each citing `file:line`, under the accuracy rules. Labelled model-read.
- **Shown after:**

```
You said: the handler looks up the charge before the charge row is committed.
The fix landed in: webhooks/handler.py (retry on missing charge) and api/charges.py (commit before notifying).
With the fix undone, the test fails again: the fix is the cause.
Your cause matches on location and on mechanism (model-read: "before the charge row is committed").
Your named cause has matched the fix in 5 of your last 8 failures.
Saved to replay later with the agent off.
Back to: Bug B. Next: run the full suite.
```

- **Idea recorded:** the mechanism of the failure as a system idea (here: an event can arrive before the write it refers to is visible).
- **Comes back:** as a new instance. "A refund webhook sometimes reports 'unknown refund' for a refund the API has just returned. Name the most likely cause and the first check." Sealed points, model-graded under the accuracy rules. The episode also queues a Replay (drill below), which is where diagnosis moves a level.
- **Notes:** Call it never moves a level, because the agent's reads and output are visible while the person answers. The running tally is shown as a count, with no judgment attached.

### D2. Reproduce it

- **Trigger:** S1: the prompt reports a bug with no failing test: bug words ("broken", "wrong", "sometimes", "used to"), an issue link, or a `fix/` branch, and S5 shows the suite is green.
- **The person does:** states the smallest reproduction: the steps and the wrong result. Target: one minute.
- **Prompt:**

```
You reported: reconciliation totals are off by a cent. The tests are green, so nothing reproduces it yet (skip ok).
What is the smallest input that should show it? Give the input and the wrong result you expect.
```

Example answer: "One charge of 10.005 in a three-decimal currency, settled. Ledger total should differ from the settlement file by 0.001."

- **The check:** the reproduction is written as a test and the runner runs it on the current tree. A reproduction is real only if the test fails, and fails in the way described.
- **Shown after:**

```
I ran: one settled charge of 10.005 KWD, then reconciliation.
You expected: totals differ. What happened: totals match. This input does not reproduce the bug.
Tried the nearest variants: 2 charges of 10.005 KWD in one batch: totals differ by 0.001.
The bug needs a sum of rounded amounts, not one amount.
Back to: Regression C. Next: the failing test is in tests/recon/test_rounding.py.
```

The "nearest variants" are the agent's own continued work, shown only after the person's attempt is locked.

- **Idea recorded:** without a failing reproduction there is no way to know a fix worked. The reproduction also carries the first fact about the cause.
- **Comes back:** with a different report. "Report: 'refund sometimes returns 500 on retry'. What is the smallest reproduction you would try first, and what would its passing tell you?" Sealed points, model-graded. Where the report comes from project history with a known failing test, the answer is made executable and run on the commit before the fix.

### D3. Your experiment

- **Trigger:** S5 with S2: the same test id has failed after two edit-and-run cycles in this task. The engine counts: fail, edits, fail, edits, fail.
- **The person does:** chooses one experiment and says what result each of two candidate causes predicts. Target: one to two minutes. This is the moment where stopping the build briefly is right, because the build is already stuck.
- **Prompt:**

```
Two fixes have not changed test_recon_totals_match. Time for one experiment of yours (skip ok).
Pick one: log a value / shrink the input / bisect the changes / check one assumption.
Then say what you expect to see if the cause is A, and if it is B.
```

Example answer: "Log the per-row rounded amount in recon/job.py and in ledger/balance.py. If the two sides round differently, the rows differ. If the conversion rate is the cause, the rows match and only the total differs."

- **The check:** the experiment is run exactly as specified, by the agent for a log line or a smaller input, by the runner for a bisect. The result is set against both predictions.
- **Shown after:**

```
Your experiment: log the rounded amount per row on both sides.
Result: rows differ on 2 of 40. Ledger rounds half-even, recon rounds half-up.
This fits your cause A (two rounding rules) and rules out B (conversion rate).
Back to: Regression C. Next: the agent proposes one rounding rule in money.py.
```

If both causes predicted the same result: "Both of your causes predict this result, so the experiment could not separate them."

- **Idea recorded:** an experiment is worth running only if the candidate causes predict different results.
- **Comes back:** as a choice between experiments on a new failure. "Charges are slow only for one merchant. Two candidate causes: a missing index, or a slow call to the processor. Which single measurement separates them?" Sealed points, model-graded.

### D4. Symptom or cause

- **Trigger:** S5 turns green and S4 shows the fix has a shape that often hides a symptom. The engine keeps a pattern list per language: an added sleep, retry or longer timeout; a broad exception catch; a skip or expected-failure marker; an expected value edited in the test; a deleted test; an early return on a null at the crash site.
- **The person does:** says whether the fix removes the cause, and names one condition under which the failure would come back. Target: thirty seconds.
- **Prompt:**

```
test_settled_posts_to_ledger is green. The fix adds a 200 ms wait before the charge lookup (skip ok).
Does this remove the cause? Name one condition where the failure would return.
```

Example answer: "No. If the commit takes longer than 200 ms, for example under load."

- **The check:** the named condition is written as a test and run: here, the commit is delayed by 300 ms in the test. For timing patterns the runner also repeats the original test many times and reports how many runs fail. For an edited expected value, the check is a fact from the diff: the test's expected value and the code changed in the same commit.
- **Shown after:**

```
You said: fails again if the commit takes longer than 200 ms.
I ran: the same test with the commit delayed 300 ms. It fails: 0 postings.
The wait moves the failure. It does not remove it.
Back to: Bug B. Next: ask for a fix that does not depend on timing.
```

- **Idea recorded:** a fix that changes when a failure shows up has not removed it.
- **Comes back:** as a new instance with the pattern changed. "A flaky reconciliation test was fixed by catching the timeout and returning an empty result. What does the system now do when the processor is slow?" Sealed points with `file:line`, model-graded.
- **Notes:** the pattern list has false positives: a retry is sometimes the right fix. The prompt asks a question and does not say the fix is wrong.

### D5. Where it came from

- **Trigger:** S5: a test that passed at a known earlier point now fails, and at least three changes lie between. The earlier point is the base branch or the last green run in the record. The changes are commits. Where the work is uncommitted, they are the turn snapshots the runner keeps in its scratch folder for the task. A second signal is S1 with "used to work" or "since".
- **The person does:** picks the change they think introduced the failure. One tap. Target: twenty seconds.
- **Prompt:**

```
test_recon_totals_match passed on main and fails now. Six changes since then (skip ok).
Which one broke it?
  1 refund idempotency  2 webhook retry  3 money: half-even rounding
  4 recon: batch sums   5 logging        6 dependency bump
```

- **The check:** the runner bisects the range with the failing test and reports the first bad change. No model.
- **Shown after:**

```
You chose: 4, recon batch sums.
Bisect, 3 runs: the first failing change is 3, money: half-even rounding.
Change 4 is where the symptom shows. Change 3 is where it started.
Back to: Regression C. Next: read change 3.
```

- **Idea recorded:** when something used to work, search the changes before reading the code. The place the symptom shows is often not the place it started.
- **Comes back:** as "Rank the suspects" (drill below) on another regression, and as a short recall: "A test passed last week and fails today. What is the cheapest way to find the change responsible, and what does it need?" Model-graded against sealed points.

### Drills for skill 3

**Replay.** Incident replay from project history. Reused from `learning.md` section 3.3.

- Source: commits where a test went from failing on the parent to passing on the fix, and episodes saved by D1.
- Runs in a container with no network, built from the parent commit. The person turns Replay on per repo.
- In the Room, agent off: the person sees the failing output, writes a hypothesis and a first check, runs what they like in the scratch copy, then writes a fix.
- Check: the fix is graded by the commit's own test. Executable, so it can move the level at once. The hypothesis and first check are compared with the real fix, model-read.
- If the bug does not reproduce, the Replay is dropped and nothing is recorded against the person.

**Rank the suspects.** Regression search from history.

- Source: a past regression where the engine has already bisected a failing test to one commit, in a container. The result is sealed.
- The person sees the symptom and the list of commit titles in the range, with no diffs, and ranks the top two suspects with a one-line reason.
- Check: the sealed bisect result. Executable.
- Shown: the first bad commit, its diff, and the person's record over time: how often the real cause was in their top two.

---

## 8. How ideas are recorded and return

- **What is recorded.** Each moment writes a `moment.asked` event, a `prediction.locked` event with the person's answer, a `check.ran` event with the result, and an `idea.tagged` event naming the system-level idea. The idea is stated without code: one sentence a person could apply in another project. No source code enters the record.
- **Who names the idea.** For executable moments the idea is fixed per moment (the lines marked "Idea recorded" above), plus the project fact where there is one, as in R3. For R1 and D1 the idea depends on the gap or the cause. A separate context writes it, and it enters the review queue only after the key check in `../spec/architecture.md` section 4.
- **When it returns.** At least 7 days after the moment, inside the cap of 3 review items a day, on the existing interval ladder (`learning.md` section 7).
- **In what form.** Never the same case. The engine sets the distance from paths and names (`learning.md` section 4): another component of the same project, or another project, or a bank family. The topic name is hidden.
- **What counts.** The table below.

| Evidence | Checked by | Can move a level |
| :- | :- | :- |
| An in-build answer on any moment | The real outcome | No. Recorded as prediction accuracy and shown in the journal |
| A delayed return with an executable key (V1, V2, V4, R1, R2, R3) | Sealed runner result | Yes |
| A delayed return in choice form (V5) | Sealed runner result | Up to Recalled |
| A delayed return with a model-graded key (V3 bank form, R4, D1 to D5 recalls) | Model grader under the accuracy rules | Yes, under those rules |
| Proof audit, Blast radius, Replay fix, Rank the suspects | Sealed runner result | Yes |
| Escaped defect review, Map it | Runner where the answer is executable, else model-read | Yes where executable |

Answers that can move a level are typed in the Room, so they do not pass through the agent. In-build predictions can be answered in the agent chat with one word, because nothing is graded.

Every in-build moment also adds a line to the decisions journal in the Room: what the person predicted, what happened, and the link to the check output. The journal is the person's own record of calls against outcomes. It is also the source for the calibration skill, which is designed elsewhere.

---

## 9. Keeping it rare

**One per break.** Several moments can fire at the same break. The engine picks one, in this order:

1. A moment the build is already stopped for: D3 (two failed fixes), then D1 (a failure).
2. A moment whose check has found something on a high-stakes diff.
3. The moment for the skill with the least recent evidence in the person's record.
4. Otherwise none.

**High stakes** means the diff touches paths the person has marked, or paths matching the default list: money movement, authentication, migrations, deletes. In orbit-pay the person marked `orbit_pay/ledger/` and `orbit_pay/money.py`.

**Ask on clean cases too.** The runner often knows the result before the question is shown. If moments were asked only when the check found a problem, the question would give away its answer. So a share of asks is drawn from clean results. Design default: about one in three, so that "nothing is wrong" stays a live answer.

**Silent runs.** When the budget is spent, cheap checks (V2, V3, V5, R2) still run in the background. A result that matters on a high-stakes diff goes to the Room inbox as a plain note with no question. The person gets the fact without the interruption. One later review item may be queued from it, as in `learning.md` section 2.7.

**Fading.** Each moment has three forms, chosen per person and per idea:

| Form | When | What it looks like |
| :- | :- | :- |
| Full | The idea is at Not yet | The prompts shown above |
| Short | The person's calls were right on two different days | One line, one tap |
| Silent | The idea is at Applied or above | Asked only on high-stakes diffs; otherwise the check runs silently |

This follows the expertise reversal finding cited in `SKILLS.md`: guidance that helps a novice gets in the way of someone who already has the habit. A sure miss on a delayed return moves the moment back one form.

**Variety.** The same moment is not asked twice in a row at the same kind of break, and the wording rotates across a small set per moment. The reason is the habituation finding in `SKILLS.md`: repeated identical prompts get less attention.

**Always.** Every prompt carries "skip ok" and the word "skip" always works. Two skips end questions for the session. Pressure signals (a hotfix branch, "urgent", a failing deploy) silence every moment except the silent runs. D3 is offered under pressure only as the short form, because the build is stuck anyway.

---

## 10. What to build first

**Build V2, the revert test, first.**

- Its feedback is a fact from git and the test runner. No model writes the question, the key or the grade, so nothing about accuracy has to be solved before it works.
- Its trigger is the most common break in any build with an agent: the agent says it is done.
- It needs only a local shell, git and a test command, so it gives the same outcome on every agent.
- It takes one tap and about twenty seconds.
- It often tells the person something they did not know about their own project: which of the new tests would pass without the change. `SKILLS.md` lists it first among the moments with the clearest feedback.
- Building it builds the scratch runner, which V1, V4, V5, R2, R3, D1, D4, D5 and the drills reuse.

**Then D1, Call it.** It adds the red-to-green episode record, the fix location and the cause check on top of the runner, and it feeds Replay. After those two, the order is V4, R2, D5, V3, then the rest.

Order by what each adds to the engine:

| Step | Moment | New machinery |
| :- | :- | :- |
| 1 | V2 Revert test | Scratch runner, done trigger, base and head comparison, reveal card, journal line |
| 2 | D1 Call it | Failure trigger, red-to-green episodes, undo-the-fix check, model reader for mechanism |
| 3 | V4 Missing case, V1 Name the proof, D2 Reproduce it | Turning a sentence into one test, the "not what I meant" path |
| 4 | R2 Who else, V3 Claim check | Reference search, claim patterns, tool log reading |
| 5 | D5 Where it came from, Rank the suspects, Proof audit | Bisect, turn snapshots, container runs on history |
| 6 | V5 Unrun lines, R3 Trace the path, Map it, Blast radius | Coverage and tracer adapters per language |
| 7 | R1, R4, D3, D4, Replay, Escaped defect review | Remaining triggers and pattern lists |

---

## 11. What this asks of the engine

New `moment` breaks: `task_start`, `done`, `test_failed`, `fix_green`, `pr_open`, `pr_review`.

New check commands, each mirrored as an MCP tool and each a call to the scratch runner:

| Command | Used by | Does |
| :- | :- | :- |
| `check revert` | V1, V2, Proof audit | Reverts non-test files to the base, runs named tests |
| `check claim` | V3 | Runs the test, build, lint or migration status command; reads the tool log on hook tiers |
| `check case` | V1, V4, D2, D4, Escaped defect review | Runs one added test case on a named tree |
| `check lines` | V5 | Coverage run intersected with the diff |
| `check refs` | R2, V3 | Reference search for changed symbols |
| `check trace` | R3, Map it | Tracer run for one test, components in order |
| `check undo-fix` | D1 | Undoes the changes between a red and a green run, runs the test |
| `check bisect` | D5, Rank the suspects | Bisects commits or turn snapshots with one test |
| `check mutate` | Blast radius | Applies one sealed change in a scratch copy, runs the suite |

New event types: `moment.asked`, `moment.skipped`, `prediction.locked`, `check.ran`, `check.unavailable`, `episode.red`, `episode.green`. They follow the event format in `../spec/architecture.md` section 2.

Per-project settings, kept in the record's `config/`: the test command, the coverage command if any, the high-stakes paths, the component names, the runner time limit.

---

## 12. Limits, stated plainly

- **No test command, no executable moments.** In a project with no tests, V2, V4, V5, R3, D1's cause check and D5 cannot run. V1, V3 and D2 still work and will tend to produce the project's first tests. The Room says which moments are off and why.
- **Tests that need live services.** If the baseline run in the scratch copy does not match the real tree, the check is skipped. The moment is not asked with a made-up answer.
- **Slow suites.** Checks run on the named tests, not the whole suite, wherever the moment allows. V3's full run and D5's bisect can exceed the time limit on large projects. They are then dropped for that break.
- **Static reference search is incomplete.** R2 and V3 say what was searched and how.
- **Sentence to test.** V1, V4, D2 and D4 depend on a model turning a sentence into a test. The card always restates the input and the expected result in plain words, and "not what I meant" discards the result.
- **Model-read parts.** R4's summary comparison and D1's mechanism match are read by a model. They are labelled, they follow the accuracy rules, and in the build they move nothing.
- **Does practising these moments make someone better at the skill elsewhere?** `SKILLS.md` says no study has tested this. The design does not wait for one. Each moment gives the person a true fact about their own project at the time they need it, which is useful whether or not it transfers.
