# Spec: the experience

Part of `../PRODUCT.md`. This file says what the person sees and does, on every surface, from install to the end of a project. It is the source for anything on screen: where `architecture.md` or `surfaces.md` differ on wording, a command name or a screen, this file wins. It now also holds every Room screen and the phone, which were in a separate file.

The learning model is in `learning.md`: the moments, the checks, the budget, the levels. This file gives them a face. The visual language is `../../learning-experience/design-system.md` and `../../learning-experience/assets/room.css`.

The running example is orbit-pay, a payments service. The person is Sam. All counts, dates and paths, and the address `127.0.0.1:4127`, are example values.

---

## 1. What the experience must do

1. **Give a true fact about the person's own project when they need it.** Every result is useful to the build even if nothing is learned. A fact is never held behind a question.
2. **Take a call before the outcome is shown, then show both.** The person's words, what happened, the evidence.
3. **Stay out of the way.** The agent never waits. One word skips. By default one short exchange a day, and many days none.
4. **Return the person to the work.** Every exchange ends with `Back to: <task>. Next: <step>.`
5. **Be the same on every agent.** The words are identical everywhere, and an answer counts the same wherever it is typed.
6. **Tell the truth about the record.** Counts, what one fixed answer would have scored, the age of the evidence.

---

## 2. Copy rules

- Plain words, short lines, one idea per line. No exclamation marks, no praise, no mascot.
- **Five nouns** for the person: **question** (asked while building), **review** (an idea coming back), **note** (a fact with no question), **drill**, **decision**. The words "moment", "sealed" and "fixed answer" never appear on screen. The fixed answer is always the full sentence: "Always answering 'none' would have scored 4 of 8."
- A result reports what happened. The words are **Matched** and **Did not match**, never right or wrong. Other chips: **Not scored**, **Practised**.
- Reviews graded by a reader use **Correct**, **Not quite**, **No**. Reviews checked by a run use Matched and Did not match.
- Evidence is a command that was run or a `path:line`.
- Every question says why now in a few words and carries `skip ok`.
- Every result says how it was checked: by a run, by a search, from the timeline, or model-read.
- "Not seen" is stated only where it changes what the person should do.
- Every error ends with the one reply or command that fixes it.
- A fact is stated once. No line reassures, explains the loop or tells the person how to feel.
- Banned: streaks, points, badges, ranks, countdowns, backlog counts, loss framing, "time saved".
- Never claim what is not true about data. Name who can see what.
- Confidence words: **Sure**, **Not sure**. "Don't know" is a separate answer, never a confidence. It locks at once, with no confirmation.
- The button that commits a typed answer is **Lock my answer**. A pick locks when selected, with **Undo** until the result is opened.

---

## 3. Install and the first minutes

No tour and no welcome screen. The first value is a set of facts about the person's own project, with no question attached.

### 3.1 Install

The person runs `uvx firsthand init` from inside the agent they use. `init` installs only into that agent.

```
Firsthand will add itself to Claude Code. It will write these files:
  ~/.claude/CLAUDE.md          adds 3 lines
  ~/.claude/skills/firsthand/  new folder
  ~/.claude/settings.json      adds 6 hooks that call /home/sam/.firsthand/engine/0.1.0/bin/firsthand
Backups go to ~/.config/firsthand/backups. "firsthand uninstall" restores them.
Hooks only report what happened. They never allow, deny or block anything.
Go ahead? [Y/n]  (d shows the exact changes)
```

Then one question and the facts:

```
Is this a work computer? [Y/n]
  Enter means yes: answers stay out of your agent's chat by default,
  and nothing is sent to a model without asking you.

Firsthand is set up in Claude Code. It is on Standard: at most 1 question a day.
"Notes only" gives you the checks with no questions. Change it in Settings.

Your record: ~/.firsthand/record. A git repo on this machine, outside your projects,
with no remote. Plain files: anyone who can read your home folder can read it.
Your Room: http://127.0.0.1:4127  A page served by this computer, for you only.
By default Firsthand sends nothing anywhere except the lines it prints in your
agent's chat and package-name lookups. "firsthand privacy" lists everything.

Say "skip" to pass on a question. Say "firsthand off" to stop everything.
I am reading this project's recent history. Nothing in the project is changed.
```

- Nothing else is asked. The reminder is offered the first time a review is due. Other agents are added from Settings or `firsthand add <agent>`.
- On a work computer the notice in section 13.2 is shown.

### 3.2 What works here, and the history scan

Within a few minutes two notes land in the Room. The agent prints one line, once: `Firsthand: 2 notes about this project are in your Room: http://127.0.0.1:4127`

```
WHAT WORKS HERE  orbit-pay

Test command      pytest -q          found in pyproject.toml. Runs on a copy: yes.
Can run           Revert test, Call it, Brief, Who is affected, Where to look,
                  Split point, Your experiment, Already there, Decide and date it
Needs a yes       Missing case writes a test from your sentence. That needs a model.
                  Allow one in Settings, or use Deep and write the test yourself.
Off here          Way back, Invariant: no scratch database. Docker or Podman turns them on.
                  Silent failure: not built for this stack yet.
One step that unlocks the most: install Docker or Podman.
```

```
FROM YOUR HISTORY  orbit-pay, last 40 commits

Changes that added tests       12
  Every new test passes with the change undone      4 of 12
Schema changes                 3
  With no down step in the files                    1    migrations/0029_drop_legacy.py
Largest change                 31 files, 6 kinds of path
Changes followed by a fix commit within a week      5 of 40

Any of these commits may have been written by an agent.
I use this to choose what to ask first: verification, then debugging, then framing.
Checked by a run, in a container, on each commit. Open the commands
```

- With no container runtime the scan reads only what needs no run, and the note says: "Old commits were not run. That needs Docker or Podman."
- With no test command, the first note leads with: "I found no test command, so most checks cannot run. Set one in Settings. Brief still works and tends to produce the first tests."

### 3.3 The first Room visit

The Room opens on the Inbox. Nothing is faked.

- Before the notes land: "Nothing here yet. Notes about this project arrive in a few minutes. Your first question comes when your agent next finishes a change with tests."
- Under the history note, one offer: **Try one now**. It opens a Proof audit drill on one of the twelve commits. It is a drill, so it uses no slot.
- The Skills tab shows eleven rows reading "Too few calls. 0 of 2." One line on top: "Already do some of these? Select 'I do this already' on a skill. It goes quiet at once and only posts notes."
- The System tab already shows the project's parts with the history facts pinned to them.

---

## 4. A question, end to end

Five steps on every surface. The example is the Revert test on idempotent refunds.

| Step | In the agent | In the Room | Engine |
| :- | :- | :- | :- |
| 1. The break | The agent finishes its turn | Nothing yet | The done signal. The revert check has usually started already |
| 2. The ask | An inline card, or one line with a link | The card is the Now item in the Inbox | Shown once the control run passes. If the control fails, nothing is ever asked |
| 3. The lock | Sam replies `2` | Or Sam selects a test in the Room | The call is stored. The earliest lock wins |
| 4. The result | Chip, what Sam said, the one fact, the resume cue | The same, with **More** | One journal line |
| 5. The way back | `Back to: idempotent refunds. Next: read the summary.` | **Back to the build** | Nothing more is asked on this change |

What never changes:

- **The agent does not wait.** If Sam sends the next prompt without answering, the question closes. The result opens in the Room at once and nothing is scored.
- **One place, one state.** The inline card, the text line and the Room card are the same item. Answered in one, it is locked in all.
- **An answer counts the same wherever it is typed.** The Room keeps it out of the agent's chat, which matters on a work computer. That is the only difference.
- **What the agent is given.** After the lock, a finding goes to the agent as one line, because it is about the agent's own work. Sam's call and whether it matched are never given to the agent. Settings can turn the line off.
- **What the tool cannot hide.** The agent's own summary may already be on screen. The card asks Sam to read the tests, which is the evidence the call needs.

---

## 5. The words for every moment

One row per moment. "Reply" is what the one-line form accepts in chat. Sizes are counts of things, never times.

| Moment | Reason line | Prompt | Answer | Size | Reply | Result headline |
| :- | :- | :- | :- | :- | :- | :- |
| Revert test | Your agent finished | Which one would still pass with the change undone? | The test names, None, Don't know | One tap | `1`, `2`, `none` | REVERT TEST |
| Call it | A test is failing | Before any fix: where is the cause? | Three components, Somewhere else, Don't know. Or one line | One tap, or one line | `1` to `4`, or a line | CALL IT |
| Brief | Starting a task | Name one check that fails now and will pass when this is done | One line | One line | A line | DONE CHECK |
| Who is affected | Your agent finished | This changes `<symbol>`. Name one caller or user outside the change who sees something different | One line, or Nobody | One line | A line, `nobody` | WHO IS AFFECTED |
| Missing case | Your agent finished | Name one case these tests miss, and what should happen. Does the code handle it today? | One line, then Handles it, Does not, Don't know | One line and one tap | A line, then `yes`, `no` | MISSING CASE |
| Where to look | Your agent finished | If something is wrong in this change, where? | The changed files, Nothing is wrong | One tap | `1` to `n`, `nothing` | WHERE TO LOOK |
| Split point | This change has grown | Which files could land first? Would that part pass the tests alone? | Files, then Passes, Does not | A few taps | In the Room | SPLIT POINT |
| Your experiment | Still failing after two tries | Name two causes. Pick one experiment. What does each cause predict? | Two lines, one pick, two taps | A few lines | In the Room | YOUR EXPERIMENT |
| Already there | A new file: `<path>` | Does the project already have something that does this? | Yes with a name, Nothing | One tap | A name, `nothing` | ALREADY THERE |
| Decide and date it | Your agent is asking you to choose | Your choice, the cost you accept, what would show it was wrong, a date to look again | Four short fields | A few lines | In the Room | DECISION |
| Way back | A step a revert does not undo | If this is wrong, what gets you back? | Revert the commit, Run the down migration, Restore a backup, Nothing does | One tap | `1` to `4` | WAY BACK |
| Invariant | A schema change | One rule every row must keep. What enforces it? | One line, then The database, Application code, Nothing yet | One line and one tap | In the Room | INVARIANT |
| Silent failure | Before this merges | If `<function>` breaks, what shows it first? | An error to the caller, An error log, A metric, Nothing | One tap | `1` to `4` | SILENT FAILURE |
| Time call | In the Room only | Of the active time on this change, what share comes after your agent first finishes? | Four bands | One tap | In the Room | TIME CALL |

Moments marked "In the Room" print one line with the link and take no chat reply, because their answer has several parts. A question is never split across two places.

On the full form, the first time each moment is met, one folded **Example** shows a sample answer from the idea catalog, not from the person's code. A term new to the person carries a short gloss: "Invariant: a rule the data must always keep."

### 5.1 Revert test

Room card:

```
Your agent finished                                                  skip ok
Verification | orbit-pay | idempotent refunds | change since 09:12

It added 3 tests. Read them first.

  1  test_same_key_refunds_once
       assert len(ledger.refunds(charge)) == 1
  2  test_refund_response_is_stable
       assert resp.status_code == 200
  3  test_refund_amount_validated
       assert exc.value.code == "amount_too_large"
  Open a test

Which one would still pass with the change undone?

  ( ) 1    ( ) 2    ( ) 3    ( ) None    ( ) Don't know

Skip     Wrong start
Checked by a run: the change undone, the tests kept.
```

After a pick: "Locked. Undo" and one optional row: `How sure?  Sure   Not sure   Show the result`.

Result:

```
REVERT TEST                                                         Matched
You said        2, test_refund_response_is_stable. Sure.
What happened   It still passes with the change undone.
                It would pass whether or not the change exists.

[ Back to the build ]
Back to: idempotent refunds. Next: read the summary.

More
```

Under **More**:

```
  test_same_key_refunds_once       fails on its assertion (2 refunds, expected 1)
  test_refund_response_is_stable   still passes
  test_refund_amount_validated     cannot run without the new code, which is weak proof
Checked by a run, no model. Open the commands
Your calls of this kind: 5 of 7 matched. Always answering "none" would have scored 4 of 7.
Sure: 6 of 8 matched. Not sure: 3 of 6.
Sent to your agent: "test_refund_response_is_stable passes without the change."
This result looks wrong
```

When it does not match, two lines change and one is added:

```
REVERT TEST                                                   Did not match
You said        None.
What happened   test_refund_response_is_stable still passes with the change undone.
What would have shown it
                Its only assertion reads the status code: tests/test_refunds.py:41.
                The change does not alter the status code.

Say it again in one line (not graded)     Ask my agent to walk me through this
```

Short form, after fading: the one-line form only, with no worked example. The Room page still shows the assertion lines. Silent: no question. A new test that passes without the change on a high-stakes path is printed as a fact line.

### 5.2 Call it

```
A test is failing                                                    skip ok
Debugging | orbit-pay | webhook: charge.settled

test_settled_posts_to_ledger: expected 1 posting, found 0.

Before any fix: where is the cause?
  ( ) 1  webhooks/handler.py      named in the trace
  ( ) 2  api/charges.py           changed in this task
  ( ) 3  ledger/postings.py       named in the trace
  ( ) 4  Somewhere else
  ( ) Don't know

Your agent keeps working. If it starts a fix before you answer, this closes
and the failure is saved as a Replay. Its theory may already be on screen.
Checked by a run, once the test passes again.
```

After the lock: "Locked. Shown when test_settled_posts_to_ledger passes again." The row sits under **Waiting**.

Endings, at the first green run or before:

| Case | Copy |
| :- | :- |
| Matched | "You said 1, webhooks/handler.py. The fix landed in webhooks/handler.py and api/charges.py. With the fix undone, the test fails again." |
| The agent started a fix first | "Your agent got there first. Nothing was scored. Saved as a Replay, to try with the agent off." |
| Did not match | "What would have shown it: the fix is in api/charges.py, which the trace names at line 4." |
| Symptom patch | "Not scored. The fix adds a sleep at webhooks/handler.py:31. That can turn the test green without touching the cause, so where it landed proves nothing about your call." |
| Never green | "Not scored. The change ended before the test passed." |

### 5.3 Brief

In the agent, at the start of a multi-part task whose prompt names no check:

```
Firsthand (skip ok): starting a task. Name one check that fails now and will pass when this is done. Reply here starting with "check:".
```

Sam replies: `check: a retried POST /charges with the same key returns the first charge id`. A reply that does not start with `check:` is a message to the agent, not the check: the line is printed at a turn end, where the agent also asks its own questions. On a work computer the Room link comes first, as in section 6.2. The agent receives: "Done when: a retried POST /charges with the same key returns the first charge id. Write this check as a failing test first."

Result, at the done signal, after "Is this your check? test_retry_returns_first_charge. Yes / No":

```
DONE CHECK                                                          Matched
Your check      test_retry_returns_first_charge
What happened   Passes now. Fails on its assertion with the change undone.
                It can tell done from not done.

[ Back to the build ]
Back to: idempotency for POST /charges. Next: read the summary.

More
  After your agent finished, you sent 1 correction:
    "same key with a different body must be a 422"
  Your agent asked 1 question: "How long should a key stay valid?"
```

If the check passes with the change undone: "Did not match. Your check passes with the change undone. It cannot tell done from not done."

### 5.4 Way back, and the hazard line

The question, when the change gains a migration with a drop, uses the words in the table above and adds one line: "What would be lost?"

Result:

```
WAY BACK                                                      Did not match
You said        Run the down migration. Nothing lost.
What happened   Tried on a scratch database. The down migration recreates the
                column, empty. The values are gone.
What would have shown it
                migrations/0033_drop_legacy_ref.py:14  op.drop_column("charges", "legacy_ref")
Not seen        Your provider's backups. Firsthand cannot see them.
```

The hazard line is not a question. Later, when the agent is about to run the migration against a target that is not local, this prints at once beside the agent's own approval prompt, whether or not anything was asked or answered:

```
Firsthand: alembic upgrade head points at db.orbit-pay.example / orbit_prod
(DATABASE_URL in .env.production:3). Migration 0033 drops charges.legacy_ref.
No backup seen in this session. This line does not hold the command.
```

If the command had already run: "This ran at 14:06. It pointed at orbit_prod." The same facts become a Room note.

---

## 6. In the agent

### 6.1 The inline card

Where the agent can show a form, the question appears as a card in the conversation, 360px wide at least, built from the Room's components. On a work computer the default is the one-line form with the Room link first.

### 6.2 The one-line form

One line: `skip ok`, why now, the question, the reply words and the Room link. No tables, no boxes, no colour.

```
Firsthand (skip ok): your agent finished and added 3 tests. Which one would still pass with the change undone? 1 test_same_key_refunds_once, 2 test_refund_response_is_stable, 3 test_refund_amount_validated. Reply 1, 2, 3 or none. With the tests shown: http://127.0.0.1:4127/q/7f3

Firsthand (skip ok): test_settled_posts_to_ledger is failing. Before any fix, where is the cause? 1 webhooks/handler.py, 2 api/charges.py, 3 ledger/postings.py, 4 somewhere else. Reply 1 to 4, or: http://127.0.0.1:4127/q/7f5
```

- A reply here and an answer in the Room are scored the same way.
- On a work computer the link comes first and the line adds once: "A reply here is part of your agent's chat. The Room is not."
- On the first three questions one more line follows: "The tests are shown on the Room page."

### 6.3 The result in text

Chip, what the person said, the one fact, the resume cue.

```
Firsthand, revert test. Matched. You said 2.
test_refund_response_is_stable still passes with the change undone. It would pass whether or not the change exists.
More: http://127.0.0.1:4127/r/7f3
Back to: idempotent refunds. Next: read the summary.
```

When the call was made in the Room, the chat gets only the finding and no "You said".

### 6.4 Every other line Firsthand prints in the agent

| When | Exact copy |
| :- | :- |
| Skip | `Skipped. Back to: <task>. Next: <step>.` |
| Second skip in a session | `Skipped. No more questions this session. Back to: <task>. Next: <step>.` |
| "quiet" | `Quiet for this session. Checks still run and post notes. "quiet today" and "quiet here" also work.` |
| A fact line, high-stakes finding | `Firsthand: test_refund_response_is_stable passes without the change. refunds/ is marked high stakes.` |
| A hazard line | Section 5.4 |
| The person asks for one | `firsthand ask` gives the best available question now. It is listed as Practised |
| Review a pull request | `firsthand pr 482` opens Where to look in its pull request form |
| A branch from a cloud session | `firsthand import feature/refund-keys` |
| Off | `Firsthand is off. Nothing is asked, run or recorded. Your record is kept. "firsthand on" to return.` |

Never printed in the agent: review announcements, level changes, weekly lines, deferred results, notes, and anything on the first prompt of the day. When Firsthand is printing a line anyway and something waits in the Room, it adds a few words: "Also in your Room: 1 result, 2 reviews."

Under pressure only a hazard line is printed.

### 6.5 No browser

`firsthand room --tty` is the Room's text view, in a terminal the person opened. `firsthand skills`, `firsthand journal` and `firsthand review` print those screens as linear text. `firsthand answer <text>` is what an agent without hooks runs to pass on a chat reply.

---

## 7. The Room

The Room is a local web app served by the engine on the person's computer. It needs no account and loads nothing from the network.

### 7.1 Shell

- **Top bar**, 56px: the wordmark "Room", the project name in mono, a quiet button ("Quiet: off") and **Settings**.
- **Tabs**: **Inbox**, **Journal**, **System**, **Skills**, **Drills**. Cards, results, reviews and drill runs are focused views with no tabs.
- **Widths**: 640px for Inbox, cards, results, Journal and drill runs. 960px for System and Skills. Gutter 32px, 16px on the phone.
- **Surface**: `--paper` page, `--card` cards with a 1.5px `--border` and 18px radius. At most one element carries the 3px `--accent` left edge: the open question.
- **Footer**, small: "Served by this computer at 127.0.0.1." and a link to About.
- **Scope**, on Journal and Skills: "This project" or "All projects".

States: "The Room cannot reach Firsthand on this computer. Start it with: firsthand room". "Firsthand is off. Your record is kept. Turn on". "Quiet for this session. Checks still run and post notes. Undo".

### 7.2 Inbox

Five groups. Empty groups are not drawn.

| Group | Holds | At most |
| :- | :- | :- |
| **Now** | The open question for the change in progress | 1 |
| **Reviews** | Ideas coming back, a decision's look date, a Time call for the change in progress | 3 a day |
| **Waiting** | Locked calls whose outcome has not arrived | Collapsed past three |
| **Notes** | Facts with no question | Newest five, then "Older notes" |
| **Results** | Results not yet opened, including any that arrived later | Until opened |

```
NOW
  Your agent finished        idempotent refunds           One tap         Open
REVIEWS
  Review                     a new case                   One tap         Open
  Look again                 one table per currency       Three facts     Open
  Time call                  idempotent refunds           One tap         Open
WAITING
  Call it                    shown when test_settled_posts_to_ledger passes again
NOTES
  stripe-retry: on the registry since 2 Nov, 3 releases, has an install script     11:42
RESULTS
  Done check                 idempotency for POST /charges        Matched
```

One small line closes the Inbox: "Asked today: 1 of 1. Reviews: 2 of 3."

| State | Exact copy |
| :- | :- |
| Empty, later | "Nothing is waiting. The next review is on 21 Nov." |
| More reviews than slots | "1 more moves to tomorrow." |
| Question closed unanswered | "You moved on, so nothing was scored. The result is in Results." |
| Skip in the Room | "Skipped. Undo" |
| A note | Opens to the fact and its evidence. **Give this to my agent** and **Dismiss** |
| After pressure | "Quiet during the hotfix on 14 Nov." |
| A reviewer's comment led to a commit | A note quoting the comment, with **Keep as a review idea** |

### 7.3 Question card

Top to bottom:

1. **Reason line**, eyebrow: why now. On the right: "skip ok".
2. **Context line**, mono: skill, project, task, and "change since 09:12".
3. **Evidence** the call needs: test names with assertion lines, a trace line, file names with diff stats. Never the diff of the change.
4. **Prompt**.
5. **The answer**: picks as radio pills (44px), or a text field.
6. Quiet actions: **Skip**, **Wrong start**, and **Example** on a first meeting.
7. **Footer**: how it will be checked.

Behaviour:

- A pick locks when selected. "Locked. Undo" stays until the result is opened. A typed answer locks with **Lock my answer**.
- After the lock, one optional row: How sure, with **Show the result** beside it. It is not shown after "Don't know".
- A sentence the engine turned into a test is shown back before it runs: "This is the case I will run: refund 0.00 on a settled charge, expecting a 422." **That is my case** / **Not what I meant**.
- A work product field (a done check, a decision) has **Send to my agent**.
- Deep only, on Invariant and Missing case: a **Your line** block, a mono field of a few lines.

| State | Exact copy |
| :- | :- |
| Locked, outcome pending | "Locked. Shown when <event>." |
| Check still running | "Locked. The check is still running." |
| Closed by the next prompt | "You moved on, so nothing was scored." with the result open |
| Shown first | "This was printed in your agent as a fact, so the question is closed." |
| Check dropped | "The check could not finish, so there is nothing to show. Nothing was scored." |

### 7.4 Result

Opens with four things: the chip, **You said**, **What happened** (the one fact), and **Back to the build** with the resume cue. On "Did not match", **What would have shown it** follows What happened.

**More** holds: the other facts, **Open the commands**, the count line with the fixed-answer sentence, the How sure line, "Not seen" where it matters, what was sent to the agent, and **This result looks wrong**.

| Chip | Meaning | Style |
| :- | :- | :- |
| **Matched** | The call equalled the outcome | Ink border, tick glyph |
| **Did not match** | It did not | `--accent-text` border and text |
| **Not scored** | No outcome, a symptom patch, a fact shown first, or two readings that disagree. The reason is on the next line | Dashed border |
| **Practised** | A call the person started, or one with no check | Dashed border |

- **This result looks wrong** opens one field. One recheck. "Rechecked. The result stands, and here is why." or "Rechecked. The check was wrong. This call is removed from your record."
- An action that helps the build is offered where the check produced one: "Your case got through. **Give it to my agent as a failing test**."
- On a miss in Call it, Invariant, Silent failure or Missing case: "Keep one of these as a review idea?" with the mechanism list as picks.

### 7.5 Journal

Every call, decision and note, newest first. Width 640px.

```
14 Nov  idempotent refunds | Revert test                                  Matched
  You said        2, test_refund_response_is_stable. Sure.
  What happened   Still passes with the change undone. Checked by a run.

13 Nov  currency columns | Decision                                     Practised
  You chose       One table per currency. Cost: reports across currencies get harder.
  Wrong if        A cross-currency report is asked for.        Look again on 12 Dec

9 Nov   charge retries | Where to look                              Did not match
  You said        Nothing is wrong. Not sure.
  What happened   CI failed on charges/retry.py before this landed.
  Reopened 16 Nov The commit was reverted. First outcome kept above.
```

- Filters: skill, part of the system, and kind (Matched, Did not match, Not scored, Practised, Decisions, Notes).
- Entries are never rewritten. A later fact adds a "Reopened" line.
- On a decision's look date the review shows the repo facts and **Stands**, **Wrong**, **Too early**. The tool does not grade the choice.
- **Download** gives the journal as Markdown or JSON.

### 7.6 System

The project's parts, with what happened in each. Width 960px. It is useful on the first day, before any call is scored.

```
orbit-pay

refunds/            money movement, high stakes          9 changes landed
  Notes      2     test_refund_response_is_stable passed without its change (14 Nov)
  Calls      3     2 matched, 1 did not
  Failures   1     saved as a Replay
api/                public interface                     14 changes landed
  Decisions  1     one table per currency. Look again on 12 Dec
migrations/         schema, high stakes                  3 changes landed
  Notes      1     0029 has no down step
webhooks/           input handling                       6 changes landed
```

- Parts are top-level folders, named by path. The person can rename a part and correct its category.
- Every count opens the journal filtered to that part.
- It has no score and asks nothing. Where a migration extractor exists, tables are listed under their part.

### 7.7 Skills

Eleven rows in the order of `SKILLS.md`. Never one score. Each row: number and name, two segments (**Shown**, **Reliable**), the level with its date, the age of the newest scored call, and an expand button.

```
1  Verification                    Reliable since 13 Nov        newest call 2 days ago

   Your last 9 scored calls       7 matched
   Always answering "none"        would have scored 5 of 9
   Asked 14. Answered 10. Don't know 1. Skipped 3.
   Evidence covers                Telling a test that proves a change from one that would
                                  pass anyway. Naming a case the tests miss.
   No evidence on                 Checking work that has no tests.
   Questions                      Quiet now. Asked only on high-stakes changes.
   Ideas                          A test that passes without the change is not evidence.
                                  Came back twice, both matched. Not scheduled again.
   Practised, not scored          2      Open in the journal
   [ Start a Proof audit ]   [ Make this a focus ]   I do this already
```

| State | Row shows |
| :- | :- |
| No level yet | "Too few calls. 1 of 2." No segments filled |
| Shown | "Shown since 9 Nov. For Reliable: 2 more matches, one of them when the easy answer is wrong." |
| Quiet by the person's word | "Quiet because you said you do this already. Level not judged." |
| Brought back | "Asking again in the short form: 2 landed tests passed without their change." |
| Stale | Past 60 days: "Not checked lately." The Proof audit is offered |
| Calibration (10) | No level word. "Sure: 6 of 8 matched. Not sure: 3 of 6. Time call: 2 of 4 in the band." Bands below five calls read "Too few to show" |
| Product judgment (11) | No level. "Firsthand has no check for whether a change was worth building. Decisions you dated: 7." |
| Off for this project | "Silent failure cannot run here: not built for this stack yet." |
| Focus | A small "Focus" mark on up to three rows |

- Counts, never percentages, below twenty calls.
- A **Table** switch gives the same content as a plain table.
- A **Time** block sits under the rows once ten changes have landed: one bar per change, split into before and after the first finish, with the numbers written on them. "I cannot see what you do while your agent works. I never estimate time saved."

### 7.8 Drills

Eight drills, started by the person. One card per drill: the name, the skills, what the person does, the check, the size, and whether it can run.

```
Proof audit                                          Verification
  Mark each test of an old change: proves it, or would pass anyway.
  Checked by a run on that commit.          Size: 1 commit, 4 tests       [ Start ]
```

A drill run is a focused view: a step line ("Step 2 of 4"), one question at a time, the same controls as a card, and a result per step. The end:

```
PROOF AUDIT                                                   3 of 4 matched
Always answering "proves the change" would have scored 2 of 4.
Passed: you matched on a test that proves its change and on one that does not.
The scratch copy is deleted.
[ Back to the Room ]
```

Not passed: "Not passed this time. Nothing changes because of a drill."

A drill that cannot run says what is missing: "Needs Docker or Podman. None found." A drill left half way reads "Saved at step 2. Continue, or discard."

### 7.9 Settings and About

| Group | Control | Copy |
| :- | :- | :- |
| How much | The dial | **Off** "Nothing is asked, run or recorded." **Notes only** "No questions. Checks run and post notes." **Standard** "Questions within the daily limit." **Deep** "As Standard. You may also write a line of code on some questions." |
| How much | Daily limits | "Questions while building: 1 a day (up to 3)." "Reviews: 3 a day." |
| How much | Quiet | "This session", "Today", "This project". Each says how to undo |
| How much | Findings | "Send findings to my agent: On" |
| Reminder | Time | "One reminder a day at most, at 18:30. Off". The notification reads "Firsthand: reviews" |
| Skills | Per skill | "I do this already" and "Focus (up to 3)" |
| This project | Test command | "pytest -q". "Checks stop after 2 minutes. Change" |
| This project | Paths | The path patterns, each with a kind. High-stakes marks. "Add a path" |
| This project | What works here | The note from section 3.2, kept current |
| Model | Reading and writing text | "Off. Text answers are kept as practice. Missing case needs Deep." **Allow one** names the company and account first |
| Phone | Pairing | "Pair a phone" and the paired devices, each with **Remove** |
| Keyboard | Shortcuts | "Letter shortcuts: Off". "No single key ever locks an answer." |
| Your record | Location | "~/.firsthand/record. A git repo on this computer. Plain files. No remote." **Add a remote** asks for confirmation here |
| Your record | Export and delete | **Download my record**. **Delete my record** asks twice |
| Agents | Installed in | Each agent, what it can do there, **Add** and **Remove** |

Any change that widens what Firsthand does is confirmed in the Room on this computer and cannot be made from the agent's chat.

**About** holds, once: who can see what (`firsthand privacy`), and "These counts describe your calls in these projects. No study has tested whether they carry over to other work."

---

## 8. The phone

Pairing: in Settings, **Pair a phone** shows a QR code and "Scan this with your phone's camera. Both must be on the same network." The phone shows "Pair with sam-laptop? This phone will be able to read and answer your Firsthand questions." **Pair**. One tap.

| Where the phone is | What works |
| :- | :- |
| Same network as the computer, computer awake | The Inbox, questions, results, reviews, the journal, the skills |
| Anywhere else | Nothing. "Your computer is not reachable from here. Firsthand on the phone works on the same network only." |
| Any | Not offered: Your line, Replay's fix step, Settings. "On your computer" |

The pairing screen says: "This page is not encrypted on your network. Someone attacking this network could read it."

Layout: one column, 16px gutters, no horizontal scroll at 320px. A bottom tab bar, 64px with the safe area: **Inbox**, **Journal**, **Skills**, **More** (System, Drills). Evidence blocks scroll inside themselves. Targets 44px. Text fields 16px.

---

## 9. Returning to the build

Every exchange ends with one line in one shape: `Back to: <task>. Next: <step>.`

- `<task>` is the first clause of the person's prompt, cut to a few words. It can be renamed in the Room.
- `<step>` comes from a fixed table, never from a model:

| Break | Next step |
| :- | :- |
| Starting a task | "your agent has started" |
| Your agent finished | "read the summary" |
| A failure, before the fix | "your agent is on it" |
| A failure, after the fix | "run the full suite" |
| A step a revert does not undo | "decide whether to keep the down step" |
| The agent asked you to choose | "tell your agent your choice" |
| The change has grown | "decide whether to land the first part" |
| Before a merge | "merge when you are ready" |

**Back to the build** is the one primary button on every result and drill end. A web page cannot bring the agent's window forward, and the Room does not claim to.

A skip costs one line and nothing asks why.

---

## 10. Being wrong

A call that does not match is the most useful event in the record, and the point where a person decides whether to keep the tool.

1. **The result reports.** "You said. What happened." The words "wrong", "incorrect" and "mistake" are never applied to the person.
2. **The fact comes first and is useful either way.**
3. **The cue comes next.** One line on what would have shown it, from the check itself.
4. **Nobody else sees the call.** Not the agent, and the record has no remote.
5. **"Don't know" is not a miss.** It is counted as answered, the facts are shown, and the idea comes back as a review.
6. **A level never goes down.** The counts on the row show how recent calls went.
7. **The tool admits its own errors.** "This result looks wrong" rechecks once. A bad check removes the call.
8. **The tool does not judge where it cannot.** "Practised. There is no check for this now. It comes back on 12 Dec with facts from the repo."
9. **What happens next is small.** The idea comes back as a review in a week. Nothing else changes.

---

## 11. A day, a week, the end of a project

### 11.1 A normal day

Saturday 14 Nov. Sam is on Standard, one question a day, with a reminder at 18:30.

| Time | What Sam sees | Count |
| :- | :- | :- |
| 09:10 | First prompt of the day. Nothing from Firsthand | |
| 09:12 | Sam asks for idempotent refunds and names the test that should pass. No Brief | |
| 09:40 | The agent finishes. Revert test, one reply in chat. Result: one of three tests would pass anyway. The agent is given that fact and fixes the test | Question 1 of 1 |
| 13:15 | A webhook test fails. Nothing is asked: the day's question is used. The failure is saved for Replay | |
| 15:00 | The agent is about to run a migration against a database that is not local. The hazard line prints. Sam refuses the command | A fact, not a question |
| 18:30 | The reminder: "Firsthand: reviews". Sam does two in the Room | Reviews 2 of 3 |

One exchange in the build, one hazard line, two reviews. On a day of urgent work: nothing but hazard lines.

### 11.2 A few weeks

- **Week one.** Verification, debugging and framing are the focus skills, from the history scan. Most days hold one question, some none. Notes arrive in the Room without being asked for.
- **Week two.** Three verification calls have matched on two days, at least one on each kind of outcome, so its questions are in the short form.
- **Week three.** Verification reaches Reliable: five matches on three days with two catches. Its questions go quiet and a new focus skill takes its place. Sam notices fewer questions about tests and the first one about a migration.
- **Reviews.** A missed Revert test from week one returned a week later as a different change from the project's history with the source hidden.
- **One dated decision** comes due: three facts from the repo and **Stands**, **Wrong** or **Too early**.
- **If Sam chooses:** a drill at the weekend.
- **After time away.** No "welcome back" and no count of what was missed. The Inbox shows today's reviews and "The rest are spread over the next few days." A skill with no scored call for 60 days shows "Not checked lately" and offers its drill. Nothing is asked in the build because of the gap.

### 11.3 The end of a project

Sam runs `firsthand wrap`.

```
orbit-pay, 7 Oct to 14 Nov. 46 changes landed.

Questions    24 asked. 17 answered. 2 don't know. 5 skipped. 14 scored.
Skills       Reliable: Verification.  Shown: Debugging, Framing.
             Too few calls: 6. Not asked at all: Operating in production.
How sure     Sure: 6 of 8 matched. Not sure: 3 of 6.
Notes        31 facts found with no question asked. 3 hazard lines.
Decisions    7 dated. 3 looked at again: 2 stand, 1 wrong. 4 still to come.
Time         Share of active time after the first finish, last ten changes: 31%.

Reviews and dated decisions continue after the project. Keep them, or stop them?
Full page: http://127.0.0.1:4127/wrap/orbit-pay
```

The wrap page links every number to its journal entries and offers **Download**. There is no certificate and no celebration.

---

## 12. Accessibility

A release ships only when every item passes in the Room, on the phone, and in the text form on at least one agent per tier.

1. **Full loop with a screen reader** (VoiceOver, NVDA, TalkBack) and with the keyboard alone: install, a question, its result, a review, the skills, a drill, settings.
2. **Text first.** Every screen has a linear text form. The text form of a question is one line.
3. **Order of words.** The chip word comes first in a result's accessible name. The resume cue comes last.
4. **Every question restates its context** in one line.
5. **No timers.** Sizes are counts. Status lines stay until the next action.
6. **No single key writes to the record.** Letter shortcuts are off by default. When on, they never act inside a field, and no letter locks an answer.
7. **Voice.** Every answer can be dictated. Every pick has a short spoken form ("one", "none", "don't know").
8. **Targets** 44 by 44px. **Focus** is a 2px `--accent` outline at 3px offset.
9. **Contrast** per the design system. `--accent` is never used for text. Dark mode at the same rules.
10. **Meaning never rests on colour.** Chips carry words. `NO_COLOR` is respected in the terminal.
11. **One polite live region per page**, one line per state change: "Locked.", "Matched. Still passes with the change undone.", "Skipped."
12. **Semantics.** A card is a `form` labelled by its prompt. Picks are radios in a `fieldset`. A skills row is a list item whose name reads "Verification: Reliable since 13 November, newest call 2 days ago". Bars are `aria-hidden` and their numbers are text.
13. **Reflow** at 320px, at 200% zoom and at 640 by 360. **Reduced motion** turns off all motion.
14. **Undo** for a pick until its result is opened, and for skip, dismiss and settings changes.

---

## 13. Other states and notices

### 13.1 Waiting and failure

| State | Exact copy |
| :- | :- |
| Check over its time limit | "The check took longer than 2 minutes, so I dropped it. Nothing was scored." |
| Scratch run differs from your tree | Never shown. Nothing is asked |
| No model allowed | "The text part cannot be read here. The run results are shown." |
| Secret found in an answer | "Your answer had something that looked like a token. I saved it as [redacted]." |
| A branch from a cloud session | "A branch arrived from elsewhere: feature/refund-keys, 4 commits. Review it here?" Cards from it say: "Built in a cloud session. Firsthand did not see the prompts." |
| Two agents, one record | Nothing. The budget is shared across them |
| No test command | "No test command is set, so most questions cannot run here. Set one in Settings." |

### 13.2 Work computer notice

Shown at install on "yes", and by `firsthand privacy`.

```
This is a work computer. Here is what your employer can and cannot see.
Can: that Firsthand is installed, and the files it adds to your agents.
Can, through your agent's logs: anything typed or printed in your agent's chat,
  including Firsthand's question lines and findings.
Can, if they manage this computer: your record. It is plain files in ~/.firsthand.
So on this computer, question links come first and the inline card is off,
  and no text is sent to a model unless you say yes.
Firsthand has no admin view, no reports and no account.
```

### 13.3 Turning it off

- "firsthand off" stops all questions, checks, notes, reviews and the reminder at once. It keeps the record.
- `firsthand uninstall` restores every file it changed from its backups, shows a diff for any file the person changed since, leaves the record, and prints where it is.

---

## 14. Additions to the design system

The tokens, type scale, spacing, motion and accessibility rules of `design-system.md` are kept. These components change or are added. The prototypes in `../../learning-experience/prototypes/` (`card.html`, `verdict.html`, `inbox.html`, `map.html`) are the starting points.

| Component | Change |
| :- | :- |
| Record segments | Two segments per skill: Shown, Reliable. No segments for ideas |
| Question card | Adds the context line with the base, the evidence block, lock-on-pick with Undo, the optional How sure row after the lock |
| Result | Four parts first, everything else under one More fold. Adds "What would have shown it" |
| State chip | Matched, Did not match, Not scored, Practised |
| Inbox item | Size replaces cost: "One tap", "One line", "A few lines". Never a time |
| Count pair | New. The person's count and the fixed-answer sentence, always drawn together |
| System part | New. A part name in mono, its category, and counted rows that link to the journal |
| Week dots, hint ladder, explainers | Removed. The hint ladder stays only in the Replay drill |
