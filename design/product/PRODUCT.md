# Firsthand: product design

Status: revised 15 November 2026, after five reviews. Nothing is built yet except the existing skill in `skills/learning-while-building/`. Firsthand is a working name, pending a trademark check.

This file is the front door. Detail lives in `spec/`:

| File | Holds |
| :- | :- |
| `spec/learning.md` | Skills, the moment catalog, the engine's rules, feedback, levels, recall, accuracy rules |
| `spec/experience.md` | Everything on screen: install, every question and result, the agent lines, the Room, the phone, accessibility |
| `spec/architecture.md` | Engine, record format, signals, the check runner, the Room server, install, cloud import |
| `spec/surfaces.md` | Every coding agent, tiers, parity of outcome, conformance |
| `spec/security.md` | Running code safely, install, work computers, what leaves the machine |
| `spec/build-1.md` | Build step 1, ready to code: move the existing skill's record out of the project |
| `spec/build-2.md` | Build step 2, ready to code: the core loop in Claude Code |

Inputs: `../skills/SKILLS.md` (the researched skills map, the foundation), `research/`, `concepts/`, `redteam/`, and `moments/` (earlier wording and worked examples only, superseded by `spec/learning.md`). `index.html` is a one-page visual summary of this file. `tour.html` is a step-by-step walkthrough of the screens in `prototypes/`.

---

## 1. What Firsthand is

Firsthand is a free, open-source tool you install into the coding agent you already use: Claude Code, Codex, Cursor, Copilot, Gemini CLI and others. The agent writes the code. Firsthand trains the engineering judgment you still need, while you build. At the few points where the work needs a human decision (the agent says it is done, a test fails, a migration cannot be undone, a change has grown too large) it asks for one short call, then runs a real check on your project and shows what happened next to what you said: the change undone and the tests rerun, the fix undone, the migration rehearsed on a scratch database. Facts are never held behind a question, and a hazard is printed at once. By default it asks once a day at most, never makes the agent wait, and goes quiet on a skill once your calls prove reliable. A local web app, the Room, keeps your questions, results, notes, decisions and drills. The record is a git repo on your machine, outside any project, with no remote.

Why it is built this way: `SKILLS.md` reports that delegating work can weaken the understanding needed to check it, that committing to a prediction before seeing the answer keeps learning, and that prompts should be rare, varied, matched to the person and tied to checkable feedback. It also says no study has tested practice of this kind as an intervention. The design does not wait for one: every result is a true fact about your own project, which is useful either way.

It does not train prompting, context files, permissions or agent settings. Those change with each tool release.

---

## 2. The eleven skills

From `SKILLS.md`, in its order. Each skill's evidence is limited to what its moments can check, and the map says so on every row.

| # | Skill | Scored moments | Drill |
| :-: | :- | :- | :- |
| 1 | Verification | Revert test, Missing case, Brief | Proof audit |
| 2 | Reading systems you did not write | Who is affected | Map it |
| 3 | Debugging and diagnosis | Call it, Your experiment | Replay |
| 4 | Security and risk judgment | Missing case (boundary form), Way back | Break it |
| 5 | Framing the problem and the brief | Brief | Rebrief |
| 6 | Delegating and supervising | Where to look | Supervise a past run |
| 7 | Small, reversible changes | Split point, Way back | Split a past change |
| 8 | Operating in production | Silent failure, Way back | Break it, Replay |
| 9 | Design and data modelling | Invariant, Already there. Decide and date it is practised, not scored | Looking back |
| 10 | Calibrating your own judgment | How sure, Time call | Looking back |
| 11 | Product judgment | None. Nothing in a build can check whether a change was worth building, and the map says so | Looking back |

---

## 3. The moment catalog

Thirteen moments are asked in the build. Every one names what triggers it, what the person does, and the check that gives feedback. Triggers are tests on observable facts (hook events, the git diff, test results), never a model's reading. Full definitions: `spec/learning.md` section 4. Exact words: `spec/experience.md` section 5.

| Moment | Trigger | The person does | The check |
| :- | :- | :- | :- |
| **Revert test** | The agent finishes a change that adds or edits tests | Reads the new tests, picks the one that would still pass with the change undone, or none | The change is undone in a scratch copy, the tests are kept and run |
| **Call it** | A prompt holds a pasted failure, or a turn ends with a test still failing | Picks where the cause is, before a fix exists | Where the fix landed, then the fix undone and the test rerun. Not scored if the fix is a sleep, a broad catch or a loosened test |
| **Brief** | A multi-part task starts and the prompt names no check | One line: a check that fails now and will pass when done. It goes to the agent | That check is run with the change and with the change undone |
| **Who is affected** | Done, and the diff changes something referenced outside it | Names one caller or user who sees a difference, or nobody | A reference search, and the old tests run on the new code |
| **Missing case** | Done, with new tests for something that takes input | Names a case the tests miss. Taps whether the code handles it | The case is written as a test, shown back, and run |
| **Where to look** | Done, on three or more source files | Picks the file where a fault would be, or nothing | Faults found before landing by something other than the person: a failing test, CI, a revert, another reviewer |
| **Split point** | The diff is larger than most of the person's landed changes | Picks the files that could land first. Taps whether they pass alone | That part is applied alone at the base and the tests run |
| **Your experiment** | The same test fails at two turn ends in a row | Names two causes, picks one runnable experiment, says what each cause predicts | The experiment is run: undo one file, run another test, or bisect |
| **Already there** | The diff adds a new source file or shared function | Taps whether something existing already does this, and names it | A name search, the manifest and open pull requests |
| **Decide and date it** | The agent asks the person to choose, on a schema, interface or dependency change | Records the choice, its cost, a warning sign and a look date | None at the time, and the card says so. On the date: facts from the repo |
| **Way back** | The change holds a migration a revert does not undo | Picks what gets them back | The migration, the old tests and the down step are rehearsed on a scratch database |
| **Invariant** | A migration adds a table, relationship or money or state column | States one rule every row must keep, and what enforces it | The rule is shown back as a query. The breaking write is tried directly and twice at once |
| **Silent failure** | A pull request for code reached by a route or job | Picks what would show a failure first | A fault is injected in a scratch copy and the signals captured |

Two more are not interruptions. **How sure** is one optional tap after a call is locked (Sure, Not sure). **Time call** is a row in the Room during a change: a band for the share of active time that will come after the agent first finishes, checked by the timeline when the change lands.

Three kinds of fact arrive with no question. A **hazard line** prints in the agent at once when an irreversible command is about to run against a target that is not local. A **fact line** prints when a check finds something on a high-stakes change. A **note** in the Room carries everything else.

What runs where: ten of the thirteen need only git and a test command. Way back and Invariant need support for the project's migration tool, built first for pytest with Alembic or Django. Silent failure needs a capture shim per language, Python first. At install a "What works here" note says which moments can run in this project.

Eight drills in the Room train the same skills away from the build, on the person's own history: Proof audit, Map it, Replay, Rebrief, Supervise a past run, Split a past change, Break it, Looking back.

---

## 4. How feedback works

1. **A call, then what happened.** The person answers before the result is shown. The result opens with four things: Matched or Did not match, what the person said, the one fact that matters, and `Back to: <task>. Next: <step>.`
2. **The check is something that ran.** Each run has a control: the same tests on an unchanged scratch copy must behave as they do on the real tree, or nothing is asked.
3. **A miss shows the cue.** One mechanical line on what would have shown it: "Its only assertion reads the status code, at tests/test_refunds.py:41."
4. **Facts first.** A finding goes to the person whether they answer, skip or ignore the question, and to the agent as one line so the build benefits. The person's call and whether it matched never go to the agent.
5. **A call is scored when** it was made before the result was shown, a real check produced the outcome, the engine chose the case, and the outcome arrived. It counts the same in the Room and in chat. "Don't know" is never a miss.
6. **A model is used only where text must be read or written,** and then under the accuracy rules of `spec/learning.md` section 12: a separate context, keys that cite their source, a blind check of every key, two readings that must agree. Otherwise the call is unscored.
7. **The build always wins.** One question a day by default, one per change, one-word skip, nothing on the first prompt of the day, nothing under pressure except a hazard line. Nothing blocks a tool call and the agent is never asked to wait.
8. **Questions fade.** Three matched calls on a skill give the one-line form. A skill at Reliable, or marked "I do this already", goes quiet: its checks still run and post notes.
9. **Levels are coarse.** Too few calls, Shown, Reliable. They never go down. The row leads with counts and with what always giving one answer would have scored.
10. **Recall supports, it does not lead.** An idea is scheduled for review only after a miss, a "don't know" or an unsure match. It comes back at 7, 21, 60 and 180 days as a new case with a real key, at most three a day, with at most one reminder a day.

---

## 5. The Room

A local web app the engine serves at `127.0.0.1`. No account, nothing loaded from the network. Screens are specified in `spec/experience.md` section 7.

| Tab | Holds |
| :- | :- |
| **Inbox** | The open question, today's reviews, calls waiting on an outcome, notes, results |
| **Journal** | Every call, decision and note, newest first, never rewritten |
| **System** | The project's parts, with what happened in each: notes, calls, decisions, saved failures. Useful on day one |
| **Skills** | Eleven rows with counts, levels, what the evidence covers and what it does not. No overall score |
| **Drills** | The eight drills, each with a size and no timer |

In the agent, a question is an inline card where the agent can show UI, else one line of text with the reply words and a Room link. Answers typed in the Room do not pass through the agent. A paired phone opens the same Room after one tap on a QR code page, on the same network only.

There are no streaks, points, ranks or percentages on small counts. Keyboard letter shortcuts are off by default.

---

## 6. Architecture in brief

One Python daemon per user, reusing the existing engine's record, schedule and Room server code. Hooks, MCP tools and the CLI are thin clients. Detail: `spec/architecture.md`.

```
  coding agent (any)                            the person
  +-----------------------------+               +------------------------+
  | hooks     MCP tools   shell |               | browser      phone     |
  +---+----------+----------+---+               +----+-----------+-------+
      | events   | moment,  | firsthand ...          | 127.0.0.1 | same network,
      | (spool)  | answer   |                        | session   | paired
      v          v          v                        v           v
  +-------------------------------------------------------------------------+
  |  ENGINE DAEMON (one per user)                                           |
  |                                                                         |
  |  timeline <-- git watch          Room server (inbox, cards, journal,    |
  |     |                            system, skills, drills)                |
  |     v                                 ^             |                   |
  |  moment engine -- picks one --> check runner        | call              |
  |     |                                 |             v                   |
  |     |  question text + link only      +--> key store --> score          |
  |     v                                 |                    |            |
  |  agent line / card              scratch copies             v            |
  |  scheduler (reviews, reminder)  containers            the record        |
  +-------------------------+------------+--------------------+-------------+
                            |            |                    |
                 reads only v            v                    v
              project repo (never   ~/.firsthand/cache   ~/.firsthand/record
              written by the engine) snapshots, deps,    local git repo, plain
                                     scratch (0700)      JSON, no remote
```

- **Signals.** Hooks where the agent has them, the agent's own reports where it does not, and git watch everywhere. A hook only appends one line to a spool file and exits, so no event is lost and no hook is slow. Hooks never return a permission decision.
- **Task and base.** A task starts at the first prompt after the last finished turn, commit or branch switch. Its base is a snapshot of the tree at that prompt. Every card shows the base and can correct it.
- **Checks.** Run on a scratch copy built from a snapshot, with a scrubbed environment. The engine never writes to the project. Old commits run in a container.
- **Keys.** One rule in one function: nothing given to the agent carries a result before the person has answered. No signing, no hash chain, no key encryption: the record is the person's own.
- **Same outcome on every agent.** The check needs only a shell and git, and an answer counts the same wherever it is typed. Richer agents change timing and convenience.
- **Cloud sessions.** No engine runs there and there is no carry branch. `firsthand import <branch or PR>` reviews the fetched work at the next local session.
- **Privacy.** No server, no telemetry. The install copy names everything that leaves the machine.

---

## 7. Founder decisions already made

1. The record is a local git repo outside any project. No remote unless the person asks.
2. At most 3 reviews a day. At most one reminder a day, at a chosen time.
3. Keyboard letter shortcuts are off by default. One confirmation tap on the phone is fine.
4. The same learning outcome on every coding agent surface.
5. Apache-2.0 for code, CC BY 4.0 for content. A Python engine reusing the existing one.
6. No carry branch for cloud sessions. An import step instead.
7. The name Firsthand, pending a trademark check.

---

## 8. Build order

Each step ships on its own and is chosen for the machinery it adds.

| Step | Build | Adds | Spec |
| :-: | :- | :- | :- |
| 1 | **Fix the existing skill.** Its record moves to a git repo outside the project. It stops telling users to commit `.learning/`. Existing users get `move`, which says what removing the folder does and does not undo. Cloud sessions export and import | The record location every later step uses | `spec/build-1.md` |
| 2a | **Revert test in Claude Code**, with How sure, the fact line and a minimal Room | Hooks and the spool, the timeline and base, snapshots, the scratch runner, the pytest adapter, the key rule, the record, the card and result | `spec/build-2.md` |
| 2b | **Call it** | Failure triggers, red and green snapshots, undo-the-fix, symptom patterns, saved failures | `spec/build-2.md` |
| 2c | **Brief** | A question at task start, work product sent to the agent, the done check | `spec/build-2.md` |
| 3 | The history scan, the "What works here" note, the System tab, focus skills, fading and levels | The first ten minutes, and the rules that keep it rare | |
| 4 | Who is affected, Where to look, Split point, Already there, Decide and date it | Reference search, old tests on new code, outside events through `gh`, partial apply, dated returns | |
| 5 | Reviews and the reminder. Proof audit, Replay, Split a past change, Looking back | The recall loop, container runs on history | |
| 6 | Codex and Cursor adapters, the MCP server, the inline card, `firsthand import` | The second and third agents. Conformance runs | |
| 7 | Missing case, Your experiment, Rebrief, the question bank | The writer and reader under the accuracy rules | |
| 8 | Way back, Invariant, the hazard line | Migration extractor, scratch database, target lookup | |
| 9 | Silent failure, Break it, Map it, Supervise a past run | The capture shim, the fault injector | |
| 10 | The phone. The remaining agents | Pairing | |

The Revert test is first among the moments because its feedback is a fact from git and the test runner with no model, its trigger is the commonest break in a build with an agent, and it takes one tap.

---

## 9. Open founder decisions

Only real ones. Each has a recommendation.

| # | Decision | Recommendation |
| :-: | :- | :- |
| A | **Questions a day by default.** The caps of 3 reviews and 1 reminder a day are settled. The number of questions asked while building is not | 1 a day, which the person can raise to 3. The reviews found that with 3, the lines the tool printed in a day came to about double that |
| B | **Chat replies count the same as Room answers.** The earlier approach scored only answers typed in the Room | Yes. The key is a run the agent cannot change, the record is the person's own, and Room-only scoring breaks the same outcome on agents without hooks. The Room still keeps an answer out of the chat |
| C | **Findings go to the agent by default.** After the person answers or skips, a fact such as "this test passes without the change" is given to the agent as one line | Yes, with a switch in Settings. The build should benefit. The person's call stays private |
| D | **Record encryption on work computers.** The first builds store plain files | Not in the first builds. Say plainly at install that whoever manages the computer can read the record. Add encryption together with the remote feature |
| E | **The phone over plain HTTP on the local network.** A browser gives such a page no crypto and no offline mode, so cards could be read by someone attacking that network | Build it last, state the limit on the pairing screen, keep it off by default on work computers |
| F | **Licence of this repo.** It is MIT today. The decision is Apache-2.0 for code | Switch when the `firsthand/` package is added in step 2. Add CC BY 4.0 for the idea catalog and question bank when they are first published |
| G | **The name.** Firsthand needs a trademark check and the package names reserved on PyPI and npm before any install line is public | Run the check before step 2 ships. Keep Ownline as the fallback |

---

## 10. Review points rejected, and why

Everything else in the five reviews was accepted and is in the spec files.

- **Give check facts to the agent only on a tap** (staff): rejected. Another review showed this withholds useful facts from the build to protect a score. Only patches wait for a tap.
- **Count each test in a multi-test Revert test as its own scored call** (staff): rejected. One pick is one call. It says nothing about the tests not picked.
- **Demote a level after two failed re-checks** (learning science): rejected in favour of levels that never go down, with recent counts beside them. Demotion on ten calls is noise.
- **A relearning review outside the three daily slots** (learning science): rejected. Three a day is a founder decision. It takes a slot only when one is free.
- **Fading per moment** (learning science): rejected in favour of per skill. Placing a person on thirteen moments one by one is too slow to feel.
- **Keep the Brief's sealed guess as a practised line** (learning science, staff): rejected. It was a prediction about the builder, read by a model. The Rebrief drill trains it against real corrections.
- **Keep Predict the run in its high-stakes form** (senior, staff, designer): rejected. Predicting one concrete output is still a code trace. The system-level form lives in the Map it drill.
- **Score Already there by whether the named thing is used in the merged diff** (staff): rejected. The person makes that choice a minute later, so it scores itself. It is scored against the search.
- **Show the full test body on the Revert test card** (junior): partly rejected. The card shows each test's assertion lines, with the full test one fold away, so the card stays readable in one look.
- **Count opening the Call it card as having started, so the agent waits** (junior): rejected. Nothing holds the build. The card closes when a fix begins and the failure is saved as a Replay.
- **Default the work-computer setting silently** (senior): rejected in favour of one question where Enter means yes. It changes what the person is told about privacy, so they should see it.
- **Recommend Light as the default for senior engineers at install** (senior): rejected as an install question. The default is Standard at one question a day, and the install copy names "Notes only" in one line.
- **One daily cap on every line the tool prints** (designer): replaced. Questions are capped. Hazard lines and fact lines are not, because holding a hazard to keep a count is the worse failure. Everything else never prints in the agent.
- **Three confidence bands once counts are large** (learning science): rejected. Two bands, Sure and Not sure, stay. Fewer words, and each band fills sooner.
- **Offline review packs on the phone for HTTPS overlay networks** (designer): rejected. The phone is live only. One mode is simpler to build and to explain.
- **Rewrite the four `moments/` files, removing cut moments and old rule sections** (staff, junior): rejected as not worth the work. Each has a banner saying it is superseded, and `spec/learning.md` section 13 maps the names.
- **A first-week cap of one question a day** (earlier design, questioned by three reviews): removed. One a day is now the default for everyone.
