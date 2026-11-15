# Spec: the learning model

Part of `../PRODUCT.md`. This file is the single model for what Firsthand trains, when it asks, how it gives feedback and what a level means. It was revised after five reviews. `../PRODUCT.md` section 10 lists the review points that were rejected.

Sources: the skills map in `../../skills/SKILLS.md`. The four files in `../moments/` hold earlier wording and the orbit-pay worked examples only. Their rules are superseded by this file. Section 13 maps their names to the names used here.

Words. In this spec a **moment** is a point where the tool may ask. On screen the person sees five nouns only: **question** (asked while building), **review** (an idea coming back), **note** (a fact with no question), **drill** and **decision**. The spec says "fixed answer" for the score of always giving one answer. On screen that is always the full sentence: "Always answering X would have scored 4 of 8."

---

## 1. The model in one page

1. **The tool trains judgment at the points where the work needs a human decision.** Briefing the builder, a design choice, a failure, a risky step, a change that has grown, the agent saying "done", a merge. There are thirteen moments asked in the build (section 4).
2. **A moment is a call followed by what happened.** The person makes a short call before the outcome is known. The engine runs a check on the real project and shows the result next to the call. Code appears only as evidence.
3. **The check is something that happened.** A test run, a revert, a bisect, a search, a count from the task timeline. A model reads or writes text only where text must be read or written, under section 12, and the result says so.
4. **Facts are never held behind a question.** A hazard is printed at once. A finding on a high-stakes change is printed whether the person answers, skips or ignores the question (section 6.4).
5. **The build always wins.** Nothing blocks a tool call. The agent never waits. By default the tool starts one exchange a day. One word skips. Nothing is asked under pressure, and questions fade as the person's calls prove reliable (section 6).
6. **Levels are coarse and never go down.** A skill has three states: too few calls, Shown, Reliable. The row leads with counts, which are honest at any sample size (section 8).
7. **Recall is the support, not the spine.** An idea is scheduled for review only after a miss, a "don't know" or an unsure match. It returns days later as a new case, at most three a day (section 9).
8. **Writing code is optional and Deep only.** "Your line" exists on two moments and one drill.

No experiments are proposed. Each choice is made from `SKILLS.md` or from how git, test runners and the record work, with the reason beside it.

---

## 2. The eleven skills

Definitions and evidence are in `SKILLS.md`. Each row says what the tool's evidence covers and what it does not. The map shows the same two lines for every skill (section 8.4).

| # | Skill | Scored moments | Practised, not scored | Drill | Evidence covers | No evidence on |
| :-: | :- | :- | :- | :- | :- | :- |
| 1 | Verification | Revert test, Missing case, Brief | | Proof audit | Telling a test that proves a change from one that would pass anyway. Naming a case the tests miss | Checking work that has no tests |
| 2 | Reading systems you did not write | Who is affected | Where to look (pull request form started by the person) | Map it | Naming a caller or a promise a change reaches | Understanding of code the tool never asked about |
| 3 | Debugging and diagnosis | Call it, Your experiment | Free-form experiments | Replay | Naming where the cause is before the fix exists. Choosing a check that separates two causes | Bugs with no failing test |
| 4 | Security and risk judgment | Missing case (boundary form), Way back | | Break it | Naming a request that must be refused. Knowing what undoes a step | Whole-system security review |
| 5 | Framing and the brief | Brief | | Rebrief | Writing a done check that fails without the change | Whether the goal was the right goal |
| 6 | Delegating and supervising | Where to look | | Supervise a past run | Placing review effort where a later fault was found by something other than the person | The choice of what to hand off |
| 7 | Small, reversible changes | Split point, Way back | | Split a past change | Finding a part that passes alone. Knowing what a revert does not undo | Whether the split made review easier |
| 8 | Operating in production | Silent failure, Way back | | Break it, Replay (incident form) | Knowing which signal fires when a changed function fails, in a test run | Anything in real production |
| 9 | Design and data modelling | Invariant, Already there | Decide and date it | Looking back | Knowing what enforces a data rule. Knowing whether something existing already does the job | Whether a design choice was good |
| 10 | Calibrating your own judgment | How sure, Time call | | Looking back | Whether sure calls match more often than unsure ones. Forecasts of rework share | Judgment outside these calls |
| 11 | Product judgment | None | Decide and date it | Looking back | Nothing scored. The promise form of Who is affected sits under skill 2 | Whether a change was worth building |

Skill 11 has no scored moment. `SKILLS.md` says a product moment with no readable outcome should not be used, and nothing in a build supplies knowledge of users. The map says so in one line and shows no level for it.

The tool does not train prompting, context files, permissions or agent settings. `SKILLS.md` leaves those out because they change with each tool release.

---

## 3. Shared machinery

Component names are from `architecture.md` section 1.

### 3.1 Two kinds of input

- **Work product.** A done check, a decision, a split. It is real engineering output and goes to the agent, because the build should benefit.
- **Sealed call.** A prediction about what a check will show. It is stored before the result is shown to anyone. The call and whether it matched are never given to the agent.

### 3.2 Signals

| Signal | With hooks | Without hooks |
| :- | :- | :- |
| A prompt is submitted | `prompt_submit`, text captured verbatim | The agent calls `moment task_start` |
| A tool call starts or ends | `before_tool`, `after_tool`, `tool_failed`: tool kind, command, exit code, paths | The agent calls `moment` at the named break |
| A turn ends | `turn_end`. No message text is needed | `moment done` |
| Git state | The engine reads it: working diff against the task's base, paths, tests added or edited, commits | Same |
| Test results | Exit code and failing test ids parsed from runner output | The engine runs the test command itself |
| Pull request events | `gh pr create`, merge, push, seen at `before_tool` | Git watch, `firsthand pr` |

Every check is an engine command that needs only a local shell and git. That is how the learning outcome stays the same on every agent.

### 3.3 Task, change and base

These three are defined by events, never by a model.

- **Snapshot.** A git tree of the project as it stands, including uncommitted and untracked files, taken without touching the project (`architecture.md` section 7.1). One is taken at every prompt and every turn end.
- **Done signal.** With hooks: a turn end where the working diff changed since the previous turn end, the last test run seen was not failing, and no question from the agent is pending. Without hooks: the agent's `moment done` report. On every agent, as a backstop: a new commit that changes source files, or a pull request opening.
- **Task.** Starts at the first prompt after the previous done signal, commit or branch switch. Ends at its done signal.
- **Base.** The snapshot taken at the task's first prompt. With no snapshot (no hooks, or the first event of the day arrived late): the last commit, or on a feature branch the merge-base with the default branch.
- **Change.** The unit that lands. It holds one or more tasks and ends at a commit to the default branch, a pull request merge, or a branch switch. For a solo developer on the main branch, "landed" means the commit.

Every card shows its base in words: "Change since 09:12." One tap on **Wrong start** moves the base back to the previous task's base and reruns the check. A wrongly detected done signal costs little: the check still runs on the diff as it stands and its result is true of that diff.

**The timeline** of a change holds, each with a time: prompts verbatim, test runs with failing ids, done signals, diff stats and paths at each turn end, questions the agent asked through its ask tool, commits, pull request events and reverts.

- **Outside events** are faults found by something other than the person: a test failing after a done signal, a failed CI check, an old test failing on new code, a revert, a comment from another reviewer that leads to a commit. Only these score Where to look.
- **Correction prompts** (a prompt after a done signal that is followed by more edits) are shown verbatim on results. They are never scored, because the person originates them.
- **Active time** is the sum of gaps between consecutive events, leaving out gaps longer than the idle limit. It splits into before and after the first done signal.

### 3.4 The scratch runner

1. Check a snapshot out into a scratch folder outside the project. The project is never written to.
2. **Control:** run the target tests unchanged. The result must match the real tree. If not, the check ends as "cannot run here" and nothing is asked.
3. Change one thing: revert files to the base, add one test, apply part of a diff, check out an earlier snapshot.
4. Run again. Record the command, exit code, failing test ids and a hash of the output.

A runner adapter per test tool knows how to run one test, read failing ids, and tell "failed on an assertion" from "could not run". Where there is no adapter the runner degrades to the exit code per test file, and results say so. Each check has a time limit. Old commits run in a container (`security.md` section 2).

### 3.5 Path categories and high stakes

Changed paths are tagged by editable glob patterns: schema and migrations, money movement, auth, input handling, personal data, public interface, config and infrastructure, tests, other. The person can correct a tag in the Room. **High stakes** means money movement, auth, schema and migrations, deletes, or any path the person has marked.

### 3.6 What runs where

The catalog is scoped by what each moment's check needs. This is scope, not a phase.

| Tier | Needs | Moments |
| :- | :- | :- |
| A | Git and a test command | Revert test, Brief, Call it, Your experiment, Who is affected, Where to look, Split point, Already there, Decide and date it, How sure, Time call. Missing case in its plain form, which also needs a writer (section 12) or the Deep setting |
| B | An extractor for the project's migration tool and test client. First: pytest with Alembic or Django, then jest or vitest with one ORM | Invariant, Way back with its rehearsal, the hazard line's target lookup, Missing case in its boundary form |
| C | A capture shim for the language. First Python, then JavaScript and TypeScript | Silent failure, the fault form of Break it |

At the end of `init` the person gets one "What works here" note: which moments can run in this project, and the single setup step that unlocks the most (`experience.md` section 3.2).

---

## 4. The moment catalog

Thirteen moments are asked in the build. How sure rides on the others. Time call lives in the Room.

| # | Moment | Decision point | Skills | The person does | The check | Tier |
| :-: | :- | :- | :-: | :- | :- | :-: |
| 1 | Revert test | The agent is done and added tests | 1 | Reads the new tests. Picks every one that would still pass with the change undone, or none | Run: the change undone, the tests kept | A |
| 2 | Call it | A failure, with the person present | 3 | Names where the cause is, before a fix exists | Run: where the fix landed, then the fix undone | A |
| 3 | Brief | Starting a task with no done check | 5, 1 | Names one check that fails now and will pass when done | Run: the check with and without the change | A |
| 4 | Who is affected | Done, with a changed interface or promise | 2 | Names one caller or user outside the diff, or nobody | Search, and old tests on new code | A |
| 5 | Missing case | Done, with new tests or a new boundary | 1, 4 | Names one case the tests miss. Taps whether the code handles it | Run: the case as a test | A, B |
| 6 | Where to look | Done on a multi-file change | 6 | Picks the file where a fault would be, or nothing | Outside events up to landing | A |
| 7 | Split point | The change has grown large | 7 | Picks the part that lands first. Taps whether it passes alone | Run: the part applied alone | A |
| 8 | Your experiment | The same test red at two turn ends | 3 | Names two causes, picks one runnable experiment, says what each cause predicts | Run: the experiment | A |
| 9 | Already there | The change adds a module or helper | 9 | Taps whether something existing does this, and names it | Search of names, manifest and open pull requests | A |
| 10 | Decide and date it | The agent asks the person to choose | 9, 11 | Records the choice, its cost and a look date | None at the time, said plainly. Repo facts on the date | A |
| 11 | Way back | The change holds a step a revert does not undo | 4, 7, 8 | Picks what gets them back | Run on a scratch database | B |
| 12 | Invariant | A schema change | 9 | States one rule and what enforces it | Run on a scratch database | B |
| 13 | Silent failure | A change to code reached by a route or job, at merge | 8 | Picks what would show it broken first | Run: a fault injected, signals captured | C |
| | How sure | Rides on any sealed call | 10 | One optional tap after the lock | The host's check | |
| | Time call | In the Room, during a change | 10 | Picks a band for the share of active time after the first done | The timeline at landing | A |

Cut from the earlier catalog: Predict the run (a code trace) and the outcome line in Brief (needs usage data most projects do not have). Section 13 gives the reasons.

### 4.1 Revert test

- **Trigger.** A done signal on a task whose diff changes source files and adds or edits at least one test.
- **The card.** Shows the names of up to four new or edited tests, each with its assertion lines, and one fold to open the full test. "Read the tests first." Code is on the card as evidence, never the diff of the change.
- **The person does.** With one test: "Would it still pass with the change undone?" Fails, still passes, don't know. With several: "Which of them would still pass with the change undone?" The test numbers, any number of them, or none.
- **Timing.** The runner starts as soon as a test file is added or edited and the agent's own test run passes, so the result is often ready at the done signal. The card is shown once the control run passes. If the key is not ready, the call is sealed first and the key arrives after. The engine holds both, so nothing leaks.
- **The check.** Every non-test file in the diff is reverted to the base, the tests are kept, and each new or edited test is run. No model.
- **Three outcomes, reported differently.** "Fails on its assertion" is proof. "Still passes" is no proof. "Cannot run" is weak proof: the test depends on new code, not on right behaviour.
- **Scored call.** With several tests the pick is a set: a match only when it is exactly the tests that still pass, or "none" and none does. Picking one of two tests that still pass is a miss. With one test, the pick equals the result.

### 4.2 Call it

- **Trigger.** The person is present and no fix exists yet: (a) a prompt holds a pasted stack trace or failing test output, or (b) a turn ends with a test still failing that exists at the base and is not edited in the diff. A test that goes red and green inside one turn asks nothing. That episode is saved silently for the Replay drill.
- **The person does.** Pick form: three candidate components taken from the trace and the diff, plus "somewhere else". Line form: the cause in one line and the first thing they would check. **Which change** form, when the test passed at a known earlier snapshot with three or more changes since: pick the change.
- **Nothing is held.** The agent keeps working and says what it likes. The card closes when the first source edit after the failure is seen: "Your agent got there first. Saved as a Replay." Until then the call can be locked. The card says plainly that the agent's theory may already be on screen and that Replay is the version with the agent off.
- **The check.** The files and functions changed between the red run and the first green run. The runner then restores only those to their red state and reruns the test. Which change form: a bisect over snapshots or commits.
- **Scored call.** The named component is where the fix landed, and undoing the fix brings the failure back. The picked change equals the bisect.
- **Not scored, and said on the result:** the test never went green in the change. Or the fix shows a symptom pattern: a sleep added, a broad catch added, an assertion removed or loosened, a test skipped. A patch like that can turn the test green without touching the cause, so "where the fix landed" proves nothing about the person's call. The pattern is shown at `path:line` as a fact.
- **Reproduction form.** When a bug is reported and the suite is green: the smallest input and the wrong result expected. A writer turns it into a test, shown back in plain words. It must fail in the way described. Needs a writer or the Deep setting.

### 4.3 Brief

- **Trigger.** A task start whose first response is a plan tool call or first edits in more than one path category, where the prompt names no test, no test file and no command that begins with the test command. Never on the first prompt of the day, and never on questions or one-file fixes. `SKILLS.md` records that heavy specs are overkill for small changes.
- **The person does.** One line: "Name one check that fails now and will pass when this is done." It is work product. It goes to the agent at once with a fixed request: "Done when: <line>. Write this check as a failing test first."
- **The check, at the done signal.** The engine finds the test the agent wrote for the line (the first test added in the task) and shows it back: "Is this your check?" On yes it runs twice: on the result, and with the non-test changes undone. No model.
- **Scored call.** The check passes on the result and fails on its assertion with the change undone. A check that still passes without the change cannot tell done from not done, and the result says so. If no test was written or the person says "no", nothing is scored.
- **Also shown, not scored.** Paths changed outside the categories of the first edits. Questions the agent asked through its ask tool, and correction prompts after the done signal, verbatim.

### 4.4 Who is affected

- **Trigger.** A done signal or a pull request opening, where the diff changes the signature, return shape or stored format of something referenced outside the changed files. Promise form: a test that existed at the base has changed assertions.
- **The person does.** Names one caller, consumer or user outside the diff that sees something different. Or "nobody".
- **The check.** A reference search for the changed symbols (language server, else tree-sitter tags, else a name search, labelled). The base's test files run against the head's source: each old test that fails is a promise the project used to make. No model.
- **Scored call.** The named place is in the reference list or behind a failing old test. Or "nobody", and nothing was found.
- **Limit on the card.** A static search misses dynamic calls and other services.

### 4.5 Missing case

- **Trigger.** A done signal where the diff adds or edits tests for something that takes input. Boundary form (tier B): the diff adds or changes a route handler, or lines in paths tagged auth, input handling or personal data.
- **The person does.** Names one case the tests miss and what should happen. Boundary form: one request that must be refused. Then one sealed tap: does the code handle it today? Handles it, does not, don't know.
- **The check.** A writer in a separate context writes the case as one test. The card restates the input and the expected result in plain words. "Not what I meant" discards it. The runner runs it. Boundary form: the request runs through the project's test client beside a control request that must succeed.
- **Scored call.** The tap equals the run.
- **Pays for itself.** A case that got through is offered to the agent as a failing test in one tap. The tool reports what happened, not who is right: the expectation may be the thing that is wrong.
- **Deep.** Your line: the person writes the test, and no writer is needed.

### 4.6 Where to look

- **Trigger.** A done signal on a change of three or more source files.
- **The card.** Lists the changed files, each with its diff stat and path category.
- **The person does.** "If something is wrong, where?" One file, or "nothing is wrong".
- **The check.** Outside events from the call to landing (section 3.3). The fault's files are those changed between the outside event and the run that clears it. Run at once: old tests on new code.
- **Scored call.** The named file is among the fault's files. Or "nothing is wrong", and no outside event occurred before the change landed. Faults the person found by reading are shown and never scored, in either direction.
- **Reviewer comments.** When another person's review comment on the pull request leads to a commit, the comment is quoted in the result. One tap keeps it as a review idea.
- **Limit on the card.** "Clean" means nothing outside you found a fault before this landed.
- **Pull request form.** `firsthand pr <n>`, or a branch brought in by `firsthand import`. Before the description is shown: any defect with a location, or "looks clean". A test that fails on the pull request head confirms a finding. When the person started it, it is Practised. When the import step offered it, it is scored.

### 4.7 Split point

- **Trigger.** The working diff is larger than three quarters of the person's landed changes in this repo. With fewer than ten landed changes, a diff spanning three or more path categories. Once per change.
- **The person does.** Picks the files that could land first. Taps: does that part pass the tests alone? Order form, where the diff holds a schema change and code that uses it: put the steps in an order where the tests pass after each.
- **The check.** The runner applies the chosen part alone at the base and runs the tests, then the rest on top. Splits are by file. A split through a file is not checked, and the card says so.
- **Scored call.** The tap equals the runner. In the order form, every step passes.

### 4.8 Your experiment

- **Trigger.** The same test is failing at two turn ends in a row.
- **The person does.** Names two candidate causes in a line each. Picks one runnable experiment and says what each cause predicts, pass or fail:
  - undo one named file and rerun the failing test;
  - run one other existing test;
  - bisect to before or after one named snapshot or commit.
- **The check.** The engine runs the experiment in a scratch copy. No model.
- **Scored call.** The result fits one cause and rules out the other. If both causes predicted the same result, the result says the experiment could not separate them, and it is a miss.
- **Free-form experiments** (log a value, shrink an input) cannot be run by the engine without a model writing code. They are recorded as Practised, and the card says so. The person can hand one to the agent.
- **A fact with no question.** When a test file is edited between a failing run and the next passing run of the same test, the engine runs the original test against the final code. If it still fails, a note says the pass came from changing the test.

### 4.9 Already there

- **Trigger.** The diff adds a new source file or a new top-level function or class in a shared folder.
- **The person does.** One tap: does the project, or an open pull request, already have something that does this? "Yes" with a name, or "nothing".
- **The check.** A name search over symbol names using the words of the new name and its synonyms from a fixed list, the manifest for a package that offers it, and open pull request titles through `gh`. Hits are listed, not judged. The card lists where it searched.
- **Scored call.** "Yes", and the named thing is in the hit list. Or "nothing", and the list is empty. A "yes" naming something the search did not find is unscored: the search may have missed it.
- **Not scored.** Whether to keep the new code or use the old. That decision goes to the journal.
- **A new dependency** asks nothing. The registry facts (the name exists, first release date, release count, an install script) are posted as a note.

### 4.10 Decide and date it

- **Trigger.** The agent calls its ask tool, or reports `moment options`, on a change tagged schema, public interface or new dependency. The person is already stopped to decide.
- **The person does.** Work product: the choice, the cost accepted, what would show it was wrong, and a look date.
- **The check.** None at the time. The card says so: a design choice has no outcome yet, and a model's opinion of it is not feedback. On the look date the entry returns as a review with facts from the repo: commits to the files it created, whether the structure still exists, outside events on those files. The person marks it Stands, Wrong or Too early. The tool does not grade the mark.
- **Scored call.** None. Listed under Practised.

### 4.11 Way back

- **Trigger.** The change contains a step a `git revert` does not undo: a migration with a drop, rename, type change or new not-null, or a backfill.
- **The person does.** Sealed: what gets you back? Revert the commit, run the down migration, restore from a backup, nothing does. And one line: what would be lost.
- **The check.** On a scratch database: apply the migration, run the base's tests against the new schema, run the down migration, compare schema and row hashes with the start. Where nothing can be run: "Not run. Read from the files."
- **Scored call.** The pick equals what the rehearsal shows.
- **The hazard line is separate.** When a command on the irreversible list is about to run and the target is not local, the fact is printed at once with no question (section 6.4).

### 4.12 Invariant

- **Trigger.** A migration that adds a table, a relationship, or a column tagged money or state. Once per migration.
- **The person does.** One rule that must be true of every row. What enforces it: the database, application code, or nothing yet.
- **The check.** A writer turns the rule into a query that counts violations and one write that breaks it. The card shows both back: "That is my rule" or "No". The engine applies the migration to the scratch database, counts violations before and after, attempts the breaking write directly, and sends the breaking request through the test client alone and twice at once.
- **Scored call.** The "what enforces it" pick equals what the tries show. "Application code" is a miss when two requests at once both get through.
- **Deep.** Your line: the person writes the constraint and the engine reruns the tries.

### 4.13 Silent failure

- **Trigger.** A pull request is created or merged, where the diff changes non-test code reached by a route, a worker or a scheduled job, and a test reaches that code.
- **The person does.** If this breaks, what shows it first? An error to the caller, an error-level log line, a metric, or nothing.
- **The check.** The fault injector makes the changed function raise in the scratch copy and runs a test that reaches it. The capture shim records the response, log records with levels, metric calls and caught exceptions.
- **Scored call.** The pick equals the capture.
- **Limit on the card.** This is what the code does in a test run. The engine cannot see production.

### 4.14 How sure

- One optional tap after a sealed call is locked and before its result opens: **Sure** or **Not sure**. Two bands, because three bands on a few calls reorder by chance.
- The record stores the pair: the band, and whether the call matched.
- Shown under a result once a band holds five scored calls: "Sure: 7 of 9 matched. Not sure: 4 of 8."
- It uses no slot. It is never asked on "don't know".

### 4.15 Time call

- **Where.** A row in the Room inbox while a change is in progress, once the project has five landed changes to compare with. It is never printed in the agent. It uses a review slot.
- **The person does.** Picks a band for the share of active time that will come after the first done signal.
- **The check.** The timeline when the change lands. No model. An abandoned change leaves the call unscored.
- **Reason.** `SKILLS.md` reports developers whose forecast and whose memory were both wrong against the measurement. The tool never prints "time saved", because it never sees the task done without the agent.

---

## 5. Drills

Eight drills, in the Room, away from the build. The person starts them. They never use the current week's work. Keys are sealed before the drill is offered. Old commits run in a container. Nothing is seeded into the person's code. No timer: each drill shows a size.

| Drill | Skills | The person does | The check |
| :- | :-: | :- | :- |
| **Proof audit** | 1 | Sees an old commit's message and tests, not its source. Marks each test: proves the change, or would pass anyway | The revert test on that commit |
| **Map it** | 2 | For a component they did not write: which components' tests fail under one small sealed change. This is the kept form of "predict before running", at the level of the system | The sealed run with the change applied in a scratch copy |
| **Replay** | 3, 8 | With the agent off, on a saved failure: ranks the suspect changes, names the cause, then fixes it. Incident form: roll back or fix forward | Sealed bisect. The commit's own test grades the fix. A revert rehearsal for the incident form |
| **Rebrief** | 5 | Sees an old prompt of their own and the repo state, nothing after. Rewrites it with a done check | The correction prompts that really followed, verbatim. A reader marks which the new brief covers, with a quote, under section 12 |
| **Supervise a past run** | 6 | Steps through an old change one snapshot at a time and presses "I would stop here" once | The snapshot where the fault entered, found by running the later-failing test at each snapshot |
| **Split a past change** | 7 | Orders a large landed change into parts that could each land alone | Cumulative apply and test at that change's base |
| **Break it** | 4, 8, 9 | Route form: three requests an existing route must refuse. Schema form: three states the database should never accept. Fault form: which signals fire for one injected fault | Requests with controls. Writes on the scratch database. The fault capture |
| **Looking back** | 9, 10, 11 | For an old decision, module or feature: predicts what became of it (callers now, changes since, still there or removed) | Git history and the reference search |

A drill is passed when its matched answers include each outcome kind (section 8.2). Drill answers on sealed keys are scored calls for the skill. A passed drill counts as three matched calls toward fading (section 6.8).

---

## 6. The moment engine

The engine decides in code whether to ask. The agent never decides. Every rule below is a test on observable facts.

### 6.1 Choosing

At each break:

1. **Gates.** Stop if the dial is Off or Notes only, quiet is on, a pressure signal is present, two skips have ended questions for the session, the day's question limit is used, or this change has had its question.
2. **Candidates.** The moments whose trigger matches the break and whose tier runs in this project.
3. **Pick one, before running anything,** in this order:
   - A candidate on a high-stakes change, for a skill that is not Silent, or is Silent and asks on high stakes (section 6.8).
   - A candidate for a focus skill.
   - Otherwise none.
4. **Run only the picked candidate's check.** If its control fails, fall to the next candidate. A writer call never starts until its candidate is picked.
5. **Ask before the result where possible.** The card is shown once the control passes. Selection never depends on what the check found, so being asked says nothing about the answer.

**Focus skills.** At most three at a time. They are the person's growth areas if set. Otherwise the top gaps from the history scan. Otherwise skills 1, 3 and 5, which `SKILLS.md` names as having the clearest feedback. When a focus skill reaches Reliable or is marked "I do this already", it is replaced by the skill with a runnable moment and the fewest scored calls, in `SKILLS.md` order. Reason: one question a day spread across eleven skills gives no skill enough calls to say anything.

### 6.2 The budget

| Limit | Default | Reason |
| :- | :- | :- |
| Questions in the build | 1 a day. The person can raise it to 3 | Rare by default. The build always wins |
| Questions per change | 1 | A second question on the same work is a quiz |
| A skipped or unanswered question | Uses its slot | Otherwise a skip invites another ask |
| Two skips in a session | End questions for that session, said once | A second skip is an answer |
| Reviews | 3 a day | Founder decision |
| Reminders | At most 1 a day, at a time the person picks | Founder decision |
| How sure | No slot | One optional tap on a call already made |
| Started by the person | No slot: `firsthand ask`, `firsthand pr`, drills | The person chose it |

**What Firsthand prints in the agent.** The tool starts at most one exchange a day by default: one question and, if the person answered in the agent, its result. Beyond that it prints only:

- a hazard line or a fact line (section 6.4);
- replies to what the person typed: "skip", "quiet", a `firsthand` command.

It never prints a review announcement, a level change, a weekly line or a deferred result. Those live in the Room. No Firsthand line is ever attached to the first prompt of the day.

### 6.3 Never in the way

- Nothing blocks a tool call. The hook dispatcher never returns allow, deny or ask, and never refuses to end a turn.
- The agent is never asked to wait or to hold anything back.
- Every question carries "skip ok". The word "skip", or one tap, dismisses it with no follow-up.
- **An unanswered question closes at the person's next prompt.** The person has moved on. The result unfolds in the Room at once and nothing is scored.

### 6.4 Facts first

Three kinds of fact reach the person without a question.

| Kind | When | Where it goes |
| :- | :- | :- |
| **Hazard line** | A command on the irreversible list is about to run and its target is not local or cannot be told. Or a pending migration holds a statement that destroys data | Printed in the agent at once, through the hook's user-visible message where there is one. Also an OS notification and a Room note. Printed even under pressure and when quiet. Only Off stops it |
| **Fact line** | A check finds something on a high-stakes change: a new test that passes without the change, an old test that fails on new code | One line in the agent at the next turn end, at most one per change. Also a Room note. If a question about it was open, the question closes as "shown first, not scored" |
| **Note** | Any other finding from a silent check | The Room inbox |

The hazard line gives the target, where it was read from, what is destroyed and whether a backup was seen. It asks nothing:

```
Firsthand: alembic upgrade head points at db.orbit-pay.example / orbit_prod
(DATABASE_URL in .env.production:3). Migration 0033 drops charges.legacy_ref.
No backup seen in this session. This line does not hold the command.
```

**What the agent is given.** After a lock, a skip or a close, a finding goes to the agent as one line of fact, because it is about the agent's own work and the build should benefit. The person can turn this off in Settings. The person's call, and whether it matched, are never given to the agent. A generated failing test is a patch, so it goes only on the person's tap.

### 6.5 Silent checks

Two cheap checks run in the background on every done signal even when nothing is asked: the revert test, and the claim check on agents whose turn-end payload carries the final message (checkable claims such as "all 41 tests pass" are rerun). Nothing heavier runs unless its moment was picked.

### 6.6 Quiet under pressure

Pressure signals: a branch whose name starts with `hotfix`, the words "urgent" or "prod is down" in a prompt, a production log command, a pasted production traceback. Under pressure no question is asked and nothing is printed except a hazard line. The timeline is still recorded. Afterwards one Room note says so.

Fast, short prompts are not pressure and are not a reason to stay silent. That is a normal working style. The person's own controls cover the rest: **skip** (this question), **quiet** (this session, today, or this project) and **off**.

### 6.7 Variation and the dial

- The same moment is not asked twice in a row at the same kind of break. Each moment rotates its forms (a pick, a line) and wording. Reason: the habituation study cited in `SKILLS.md` found that repeated identical warnings lose attention and varied ones keep it better.

| Setting | In the build | Away from the build |
| :- | :- | :- |
| **Off** | Nothing is asked, run or recorded | Nothing |
| **Notes only** | No questions. Silent checks post notes, fact lines and hazard lines | Reviews, drills, the journal |
| **Standard** (default) | Questions within the budget | Reviews, drills |
| **Deep** | As Standard, plus Your line on Invariant and Missing case, and line forms preferred over picks | As Standard, plus writing the fix in Replay |

Deep does not raise the budget. "Notes only" is a complete way to use the tool, and the install copy says so.

### 6.8 Fading

Guidance that helps a novice gets in the way of someone who has the habit: the expertise reversal effect cited in `SKILLS.md`. Fading is per skill and applies to every moment of that skill.

| State | When | What happens |
| :- | :- | :- |
| **Full** | Default | The full card, with a folded worked example the first time each moment is met |
| **Short** | Three matched scored calls on the skill, on two days, with at least one match on each outcome kind. Or one passed drill | One line, one tap |
| **Silent** | The skill is at Reliable. Or the person says "I do this already", at once | Checks run silently and post notes. A question is asked only on a high-stakes change |

Fading moves backwards in two cases only:

- A skill made Silent by "I do this already" returns to Short after two notes that show a gap in the person's own accepted work, such as two landed tests that pass without their change. The line says why.
- A miss marked Sure on a high-stakes change moves the skill back one state.

There is no stale re-ask in the build. A skill with no scored call for 60 days shows "Not checked lately" on the map, and the Room offers its drill.

### 6.9 Cold start

1. **History scan at `init`.** Mechanical checks on recent history: the revert test on past commits that changed source and tests, the size of past changes, whether past migrations had a down step, how often a change was followed by a fix commit. It shows where the gaps in the work are, not what the person knows, since any commit may be agent-written. It sets the first focus skills and is shown to the person as the first note.
2. **"I do this already."** At `init` or any time, per skill or for all. Those skills go Silent at once. The map says: "Silent because you said so. Level not judged."
3. **A passed drill** moves a skill to Short and counts as three matched calls.

---

## 7. Feedback by what happened

### 7.1 The check and the scored call, per moment

"Starts as" is the fixed answer before the person has five scored outcomes for the moment. After that it is the commonest outcome in their own record.

| Moment | A match means | Fixed answer starts as | Model involved |
| :- | :- | :- | :- |
| Revert test | The picked tests are exactly those that still pass without the change, or "none" and none does | "None" | No |
| Call it | The named component holds the causal fix | The file changed last | No, for the pick. A reader for the line form |
| Brief | The check passes with the change and fails on its assertion without it | None. It is a made thing, not a pick | No |
| Who is affected | The named place is found, or "nobody" and none | "Nobody" | No |
| Missing case | "Handles it today" equals the run | "Handles it" | A writer for the test, shown back |
| Where to look | The named file holds an outside fault, or "nothing" and none | "Nothing is wrong" | No |
| Split point | "Passes alone" equals the runner | "Passes" | No |
| Your experiment | The result fits one cause and rules out the other | None | No |
| Already there | "Yes" and the name is in the hits, or "nothing" and no hits | "Nothing" | No |
| Decide and date it | Not scored | | No |
| Way back | The pick equals the rehearsal | "Run the down migration" | No |
| Invariant | The "what enforces it" pick equals the tries | "Application code" | A writer for the query, shown back |
| Silent failure | The pick equals the capture | "An error to the caller" | No |
| Time call | The actual share is in the band | The commonest band | No |

### 7.2 What makes a call scored

All four:

1. **Sealed first.** Stored before the result is shown to the person.
2. **Checked by something that happened.** A runner result, a search result, a timeline fact. Where a model reads free text, two passes must agree, else the call is unscored.
3. **The engine chose the case.** A call the person started is shown and useful, and listed as Practised: picking your own cases flatters the record.
4. **The outcome arrived.** An abandoned change or a check that could not run leaves the call unscored. It is never a miss.

**Where the answer was typed does not matter.** A reply in the Room, in an inline card or in the agent's chat is scored the same way, because the key is a fact the agent cannot change. The record notes the channel (`room` or `chat`). Reason: the record is the person's own, and making honest users open a browser to be scored would break the same outcome on every agent.

A scored call is a match or a miss.

- **"Don't know" is not a miss.** It is recorded as answered with no call, counted and shown beside skips ("answered don't know: 3"), and does not count toward fading. The facts are always shown and the idea is scheduled for review. Scoring it as a miss would teach guessing in a tool that trains calibration.
- **Skips** are not scored. They are counted and shown.
- **Practised** lists calls the person started, calls with no check (Decide and date it, free-form experiments) and unscored text.

### 7.3 The result

Every result opens with four things: the chip (**Matched**, **Did not match**, **Not scored**, **Practised**), what the person said, the one fact that matters, and `Back to: <task>. Next: <step>.` Everything else is under one **More** fold: the other facts, the commands, the count line, what was not seen where that changes what the person should do, and **This result looks wrong**.

A result never says who is right where the tool cannot know. One line is added to the journal.

### 7.4 What would have shown it

A miss that reports only the outcome does not teach the cue. Every "Did not match" result adds one mechanical line that separates the two outcomes, taken from the check itself.

| Moment | The line |
| :- | :- |
| Revert test | The test's assertion at `path:line` and what it reads: "Its only assertion reads the status code." Where a coverage command is set: "It runs none of the changed lines." |
| Call it | "The fix is in a file the failing trace never names", or the trace line that names it |
| Brief | The assertion line of the done check that holds with and without the change |
| Who is affected | The reference at `path:line`, or the old test's failing assertion |
| Missing case | The line the case reaches, or the test that already covers it |
| Where to look | The outside event and the file it led to. A reviewer's comment is quoted |
| Split point | The first failing test and the missing name it needs |
| Way back | The statement that destroys data, at `path:line` |
| Invariant | The request that got through, and the missing constraint |
| Silent failure | The `except` or log call at `path:line` that swallowed the fault |

After the line, two optional actions: "Say it again in one line" (not graded), and **Ask my agent to walk me through this**, which sends the fact and a fixed request to the agent only on that click.

---

## 8. Levels

### 8.1 What a level claims

A skill level says: when the person made calls of this kind before the outcome was known, the calls held up. The evidence is scored calls, in the build and in drills. Skills are never combined into one score. Ideas (section 9) are tracked separately and have no level word on screen.

### 8.2 Outcome kinds and the fixed answer

Each moment has a **common** outcome and an **uncommon** one in the person's own record: for the Revert test, usually "fails without the change" and "still passes". A match on the uncommon outcome is a **catch**. A pick of one location out of four or more is also a catch.

For any set of scored calls the engine computes what always giving the fixed answer would have scored. It is shown beside the person's count every time. A fixed answer scores zero on the uncommon outcome, so judging each outcome kind separately needs no margin number.

### 8.3 The ladder

| Level | Claims | Reached when |
| :- | :- | :- |
| **Too few calls** | Nothing. The row shows "2 of 5" | Default |
| **Shown** | The person made this kind of call correctly when it was not the easy answer | Two matched scored calls on different days, one of them a catch |
| **Reliable** | The person's calls carry information on both kinds of outcome | In the last twenty scored calls: at least five matches on three or more days, at least two catches, more matches than misses on the common outcome and on the uncommon outcome, and no miss marked Sure on a high-stakes change |

- **Levels never go down.** A level is a statement about evidence already seen, with its date: "Reliable since 13 Nov." The recent counts beside it tell the current story. A ten-call window moving a level down and up in four days would be noise shown as a change.
- **Age.** Every row shows when its newest scored call was made. Past 60 days the level word is replaced by "Not checked lately".
- **No top level in this version.** A level that needs evidence over months can be added when records are that long.
- **Calibration (10)** has no level word. Its row shows the two How sure bands and the Time call counts. A level on two small bands would claim more than they hold.
- **Product judgment (11)** has no level and says why (section 2).

### 8.4 The coverage lines

Every skill row carries two lines from section 2: "Evidence covers: ..." and "No evidence on: ...". A level name alone claims more than the moments behind it.

---

## 9. The recall loop

### 9.1 When an idea is scheduled

A reveal schedules an idea for review only after:

- a miss;
- a "don't know";
- a match marked Not sure.

A match marked Sure, or a match with no confidence given, schedules nothing. The person has just shown the idea. Matched results carry no "idea kept" line.

### 9.2 Two kinds of idea

- **Mechanisms.** System knowledge that `SKILLS.md` lists as what skills 1, 3, 4 and 9 depend on. The seed catalog: a race between two requests, an event arriving before its write is visible, a message delivered twice, a failure half way through two writes, operations applied out of order, money rounded or compared as floats, input trusted across a boundary, a caught failure that nothing counts. On a miss in Call it, Invariant, Silent failure or Missing case, the result offers the list: "Keep one of these as a review idea?" One tap, by the person. No model tags it.
- **Habits.** One fixed sentence per moment, such as "a test that passes without the change is not evidence for the change".

A mechanism met through a miss goes ahead of habits in the queue. A habit stops returning once it has matched twice on new cases.

### 9.3 How an idea comes back, and what grades it

An idea never returns as the same case, and the topic name is hidden. A return form exists only if its key is a sealed run, a search on a new case, or a bank item with a cited key. Forms with no key were cut.

| Idea from | Comes back as | Key comes from |
| :- | :- | :- |
| Revert test | A past change from another component: tests shown, source hidden. Which would pass anyway | Sealed run, in a container. Without one, a bank item |
| Brief | The same as Revert test, on a done check | Sealed run |
| Who is affected | Name one component that sees a change to a named shared part | Reference search |
| Missing case | Test names for another feature: name a case they miss, tap whether the code handles it | Sealed run of the case |
| Split point | A different past change: which part passes alone | Sealed run |
| Already there | Find existing code for a named purpose | Name search |
| Way back | Another migration from history: what gets you back | Sealed rehearsal. Without a scratch database, a bank item |
| Invariant | Another table: what enforces a stated rule | Sealed tries |
| Silent failure | Another function: which signal fires | Sealed capture |
| Call it, Your experiment, mechanisms | A short written symptom: pick the mechanism, or the measurement that separates two causes | Bank item with a cited key |
| Decide and date it | The dated return with repo facts | Not graded |
| Where to look | Does not return. No form has a key | |

The **question bank** is public, CC BY 4.0. Each item has a key written and cited by a person, and returns as a pick. At most one bank item a day, so the person's own projects keep most slots.

### 9.4 Scheduling

- At most 3 reviews a day. The same slots carry dated decisions and the Time call.
- Counting returns come at 7, 21, 60 and 180 days after the last time the person met the material. An answer counts only when delayed at least 7 days (`DURABLE_AFTER_DAYS` in `record.py`).
- After a missed review the idea returns the next day as relearning. It is labelled "not counted" and takes a slot only if one is free.
- Free recall first: no options, no old answer and no code until the answer is locked, wherever the key allows a free answer.
- When demand exceeds slots: dated items due today, then mechanisms met through a miss, then growth areas, then the rest. An idea that does not fit is listed as "met, not scheduled".
- Reviews are announced by the daily reminder if one is set. With no reminder they wait in the Room and are mentioned only inside a line the tool was printing anyway.

Internally an idea is Met, Recalled (one counting match) or Applied (two counting matches on new cases on different days), as in the existing engine. On screen an idea shows its history and next date, with no level word.

---

## 10. What the record stores

The record is a local git repo outside any project, plain JSON, one file per event (`architecture.md` section 2). No remote unless the person asks.

| Event | Written when | Body |
| :- | :- | :- |
| `task.started`, `task.event`, `task.done`, `change.landed` | The timeline moves | Kind, time, paths, failing test ids, line counts, base tree hash. Prompts verbatim |
| `moment.offered` | The engine picks a moment | Moment, form, skill, break, fading state |
| `moment.skipped`, `moment.closed` | A skip, or the person's next prompt | Moment, how |
| `call.sealed` | The person answers | Answer or pick, channel (`room` or `chat`), who chose the case |
| `call.confidence` | How sure is tapped | `high` or `low` |
| `check.ran`, `check.unavailable` | A check finishes or cannot run | Command, tree hash, exit code, failing test ids, output hash, how checked, reason if unavailable |
| `call.scored` | The outcome arrives | Match, miss or unscored with the reason. Outcome kind. Whether a catch |
| `call.reopened` | A later fact changes a line, such as a revert | The second outcome and date. The first is never overwritten |
| `note.posted` | A silent check finds something | The fact, its evidence, whether it was printed as a fact line or hazard line |
| `decision.recorded`, `decision.reviewed` | Decide and date it | Choice, cost, warning sign, look date. Later the mark |
| `idea.scheduled`, `review.locked`, `review.scored` | The recall loop | Idea id, the instance, the answer, the result |
| `episode.red`, `episode.green` | A test goes red, then green | Test id, tree hashes |
| `skill.level_reached` | A level is reached | Level, date |

Rules:

- **No source code enters the record.** Paths, line numbers, test ids, symbol names, counts and hashes do.
- **The person's own words do:** prompts and answers. They pass the secret scan in `security.md` section 7 first.
- **The agent's text does not.**
- **Derived, never committed:** the due list, the skills map, fixed answers, fading states, focus skills, budget state.

---

## 11. Showing progress

- **Skills.** One row per skill: the level with its date, recent scored calls as a count, the sentence for the fixed answer, asked against answered against "don't know" against skipped, the age of the newest call, the two coverage lines, and what is needed for the next level.
- **Journal.** One line per call, decision and note, newest first, with a filter by part of the system. Lines can be reopened and never rewritten.
- **System.** The parts of the project by folder and path category, each with what happened there: notes, calls, decisions, saved failures, changes landed. Useful on day one with no scored calls.
- **Time.** For the last ten landed changes: active time before and after the first done signal, as plain bars with the numbers written on them.

Rules:

1. Counts, never percentages, below twenty calls.
2. The fixed-answer sentence is always beside the count.
3. Asked, answered, "don't know" and skipped are always shown. A skip is never a miss, but a person who skips the hard calls has a better record than they should.
4. Every count says how it was checked.
5. No overall score, no rank, no comparison with other people, no streaks or points.
6. The carry-over limit is stated once, on the About page and in `firsthand privacy`: "These counts describe your calls in these projects. No study has tested whether they carry over to other work." It is not a footer on every screen.

---

## 12. Keeping it accurate

Feedback is worth an interruption only if it is true.

**Checks that are run**

1. **Keys come from what happened.** A runner result, a search result or a timeline fact.
2. **Every run has a control.** The runner's unchanged baseline must match the real tree. A probe's legitimate request must succeed. A failed control drops the check and nothing is asked.
3. **A sentence turned into a test is shown back.** A writer in a separate context writes it. The card restates the input and expected result in plain words. "Not what I meant" discards it and records nothing.
4. **Selection never depends on the result,** so the question cannot reveal its answer (section 6.1).
5. **The tool reports what happened, not who is right.** Keep or merge, a design choice, whether an extra part is worth having: never graded.
6. **A fix that matches a symptom pattern scores nothing** (section 4.2).

**Text a model reads or writes**

7. **Keys cite the source.** Every point in a text key cites a `file:line` or quotes the timeline verbatim, and the engine checks the citation mechanically.
8. **Every model-written key is answered blind before use.** A second context, given only the material and the question, answers it. If it does not match the key, the item is dropped.
9. **Points are concrete claims, not quality judgments.** Each is one fact the answer must contain. Length earns nothing.
10. **The reader is isolated.** A fresh context that never saw the build conversation. It gets four fields: the question, the points, the excerpt, and the answer marked as untrusted data.
11. **No quote, no point.** Each awarded point quotes the answer, and the engine checks the quote is there.
12. **Two passes must agree,** with the points in a different order. On disagreement the call is unscored.

**Disputes and tests**

13. **The person sees the evidence and can dispute.** "This result looks wrong" rechecks once with the person's reason. A bad check removes the call from the record.
14. **Later facts reopen a line.** A revert in git adds a second outcome. The first is kept.
15. **Checks are tested like code.** Each check has fixture projects with known results in CI. A set of answers graded by people is the regression suite for any reader prompt or model version.

---

## 13. Names, merges and cuts

The files in `../moments/` use earlier names. This table maps them.

| This file | Earlier names in `../moments/` |
| :- | :- |
| Revert test | Revert test, Claim check, Unrun lines (`checking.md`) |
| Call it | Call it, Reproduce it, Where it came from (`checking.md`) |
| Brief | Brief against result, Done check first (`directing.md`). Name the proof (`checking.md`) |
| Who is affected | Who else is affected (`checking.md`). Who notices (`judgment.md`) |
| Missing case | The missing case (`checking.md`). Boundary probe (`systems.md`) |
| Where to look | Review depth call, One file (`directing.md`). Review first (`checking.md`) |
| Split point | Split point, Landing order, Mixed change (`directing.md`) |
| Your experiment | Your experiment (`checking.md`). Third failure (`directing.md`) |
| Already there | Second way (`systems.md`). Already there (`judgment.md`) |
| Way back | Undo plan (`directing.md`). Target call became the hazard line (`systems.md`) |
| Silent failure | Silent failure (`systems.md`) |
| Time call | Time call, Where it went (`judgment.md`), now in the Room only |
| Drills | Proof audit takes Escaped defect review. Map it takes Blast radius and Trace the path. Replay takes Rank the suspects, Incident replay, Roll back or fix forward. Break it takes Break in, Break the schema, Game day, Half done. Looking back takes Decision review, Kept or cut |

Cut, with the reason:

| Cut | Reason |
| :- | :- |
| Predict the run, Understanding call | Predicting what a script prints is a code trace. The system-level form is kept in the Map it drill |
| Brief's sealed guess and "parts not needed" | The guess was a prediction about the builder, read by a model. A better brief left less to match. Rebrief trains it against real corrections |
| Brief's outcome line, Who and signal, Did it help | Needs usage data most projects do not have. `SKILLS.md` says not to use a product moment without feedback |
| The hold in Call it | It made the build wait |
| Time call in the build, Outside view | Task start is the worst place to ask, and the result gives nothing to do on this task |
| Real package as a question | Its answer was a self-report. The registry facts are now a note |
| Symptom or cause, Missing line, Checkpoint, Smallest grant, What leaves, New edge, Watch call, Key walk, Cold reader, Ten calls, Maintainer's call | As in the earlier revision: no mechanical check, a narrow trigger, or replaced by a drill |
| The Held level, windows, going down | Section 8.3 |
| Clean-case sampling | Not needed once selection never depends on the result |

---

## 14. Design defaults

These numbers are design choices, not measurements. Those marked can be set by the person.

| Default | Value | Reason |
| :- | :- | :- |
| Questions in the build | 1 a day, up to 3 (set by the person) | Rare by default |
| Reviews | 3 a day (set by the person) | Founder decision |
| Reminders | 1 a day at most | Founder decision |
| Focus skills | Up to 3 | Enough calls per skill to say something |
| Runner time limit | 2 minutes (set by the person) | A slower check arrives after the person has moved on |
| Tests shown on a Revert test card | Up to 4 | Readable in one look |
| Fade to Short | Three matched calls, two days, each outcome kind | One or two can be luck, and one kind can be the easy answer |
| Shown | Two matches, two days, one catch | The least that is not one lucky call |
| Reliable | Five matches on three days, two catches, more matches than misses on each outcome kind, within the last twenty scored calls | Reachable in weeks at one question a day on a focus skill |
| Fixed answer from the person's own record | After five scored outcomes | Below that the default is a better guess |
| How sure counts shown | From five calls in a band | A smaller count reads as a rate when it is not one |
| Percentages | Not below twenty calls | Below that one call moves the figure by five points or more |
| "Not checked lately" | 60 days | The fourth step of the review ladder |
| Idle limit for active time | 10 minutes (set by the person) | A longer gap is more likely a break than work |
| Time call offered | From five landed changes | Below that there is nothing to compare with |
| Split point size line | Larger than three quarters of the person's landed changes | "Large for you", not a fixed size |
| Counting delay for reviews | 7 days | `record.py` |
| Review ladder | 7, 21, 60, 180 days | `record.py`, without the 3-day step, which could never count |

---

## 15. Limits, stated plainly

- **No test command, few moments.** Without tests the runner has nothing to run. Brief and Missing case still work and tend to produce the project's first tests. The "What works here" note says which moments are off and why.
- **Tests that need live services.** If the scratch control does not match the real tree, the check is dropped.
- **Tier B and C moments are off** until an extractor or shim exists for the project's stack.
- **Production is out of sight.** Skill 8's evidence is from test runs.
- **Nothing found before landing is not correctness.** A change with no outside event can still be wrong for users.
- **Small counts.** At one question a day, a focus skill may reach Reliable in a few weeks and the other skills show "too few calls". The map says that plainly so it does not read as a judgment.
- **The agent's theory may be on screen** when Call it is answered. The tool cannot hide it and does not pretend to. Replay is the clean version.
- **Carry-over is untested.** `SKILLS.md` says no study has tested whether practising a skill while building improves it elsewhere. The design does not wait for one: each result gives the person a true fact about their own project when they need it.
