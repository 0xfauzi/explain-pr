# Spec: the experience

Part of `../PRODUCT.md` (section 6). Copy rules come from `../research/experience-design.md`. All copy below is the plain text the engine returns on every surface. Richer tiers render the same words.

---

## 1. Copy rules

- Plain words, short lines, one idea per line.
- Verdict word first on graded answers: Correct, Partly, Not yet. Never on predictions.
- Feedback is about the work, never the person. No praise, no mascot, no exclamation marks (L13).
- Banned: streak counts, points, badges, "great job", loss framing, countdowns, backlog counts (L14).
- Code references are `path:line`.
- Every exchange ends with `Back to: <task>. Next: <step>.`
- Every question carries a why-now and a one-word skip.
- Every error ends with the one reply or command that fixes it (https://clig.dev/).
- Never claim what is not true about data. No "nothing leaves the machine". Name the receiver.
- Repo text is quoted and attributed: `From this repo, written by contributors:` and then the text, with commands and URLs removed.

---

## 2. First run

`init` runs for the agent it was launched from.

```
Firsthand will add itself to Claude Code. It will write these files:
  ~/.claude/CLAUDE.md          adds 3 lines (about 60 tokens per session, estimated)
  ~/.claude/skills/firsthand/  new folder
  ~/.claude/settings.json      adds 4 hooks that call /home/ana/.local/bin/firsthand
Backups go to ~/.config/firsthand/backups. "firsthand uninstall" restores them.
Show the exact changes? Yes, or go ahead.
```

The paths and token figure are examples; real values are computed per install.

Then:

```
Firsthand is set up in Claude Code.
I also found Cursor and Codex. Add Firsthand to them too? Name them, or none.
Your record: ~/.firsthand/record. A git repo on this machine, with no remote.
Firsthand sends nothing anywhere by default.
Answers you type in your agent's chat are part of that chat, so the agent's company sees them.
Answers you type in the pad stay on this machine. Open it with: firsthand pad
In Claude Code, answers in the pad or captured by hooks count toward your map.
A few questions.
1. Is this a work computer? yes or no.
2. How much learning while you build? Light, Standard (default), Deep.
3. A daily reminder for reviews? Type a time like 18:30, or none.
4. Which repos may I read for drills? Paths, or none.
```

Questions 1 and 3 have no default. The engine waits and re-asks once if the user presses enter. If the user still gives none, the reminder stays off and the work question is treated as "yes" for safety, which turns on the work defaults and says so.

Then the first drill:

```
Want a first question? I picked a function in payments-api from three weeks ago.
You predict what it returns for one input, then I run it. A minute or two, in the pad.
Yes, or later.
```

With no repo added, it offers three questions from the open question bank instead:

```
Want three first questions? They are written by people, about ideas common in backend code.
A few minutes, in the pad. Yes, or later.
```

After:

```
2 of 3 right. The one you missed, retry jitter, comes back next week in a new form.
Say "show my map" any time.
```

### 2.1 Work computer

Shown before the questions, and again by `firsthand privacy`.

```
This is a work computer. Here is what your employer can and cannot see.
Can: that Firsthand is installed, and the files it adds to your agents.
Can, through your agent's logs: anything you type in your agent's chat.
So on this computer, answers go to the pad, not the chat, and your record is encrypted.
Grading stays on this machine. No answer is sent to a model.
Cannot: your record, without your keychain or passphrase. Firsthand has no admin key.
Limit: an employer that controls this computer can, in the end, read anything on it.
Run firsthand verify to check this is a signed release.
```

### 2.2 Cold start line

```
I read your own commits in 2 repos. I will ask less often about 14 ideas you have used.
To have me stop asking about one, say "I know <idea>". I will ask two quick questions first.
```

### 2.3 End of first session

`Say "show my map" to see what you have shown. Say "learning off" any time.`

---

## 3. Exchanges

### 3.1 Question, full form

```
New idea: retries with a payment API. Why now: this test runs it. Say "skip" to skip.
If the first two calls time out and the third succeeds, how many charges does the provider see?
Answer, then: sure, think so, guess, or don't know.
```

When the pad is open, the chat shows only `Question in your pad (skip ok).` and the pad shows the full form.

### 3.2 Faded (after three)

```
Retries, since this test runs it (skip ok):
If the first two calls time out and the third succeeds, how many charges does the provider see?
```

### 3.3 Prediction reveal

```
What happened: the provider saw 3 charges.
You expected: 1.
The gap: client.py:42 builds a new request on each retry, with no idempotency key.
Back to: add retries. Next: add the idempotency key.
```

### 3.4 Graded answer

```
Correct. Your retry code passed the hidden test.
Graded by running the test. This is your second right answer on this idea: now Recalled.
Comes back in 3 weeks.
Back to: add retries. Next: run the tests.
```

When it does not count:

```
Correct. This one does not move your map: you answered in the chat, which the agent can see.
In the pad it would count. Comes back Friday.
```

### 3.5 "Don't know"

```
Don't know is an honest answer. It counts as not recalled yet, and this comes back sooner.
The key point: the idempotency key must be the same on every retry of one charge. See client.py:40.
```

### 3.6 Call it

```
Test failed: test_refund_twice_is_noop. Want to call the cause first? One line for the cause, one for your first check. I keep looking meanwhile. Or "skip".
```

After:

```
Your check (log the request id on both calls) tells a duplicate request apart from a double write. Good check.
Cause: two requests, same charge, no key.
I saved this bug to replay later with the agent off.
Back to: fix refunds. Next: I will run your check first.
```

### 3.7 Your line

Open, in a repo the user owns:

```
Your line: retry.py:42. The delay before retry n. Test: test_backoff.py::test_delays.
Try it before reading the test. Hint is free. "write it" hands it back. No timer.
Back to: add retries. Next: I build the rest around your line.
```

In a repo the user does not own, the comment in the code is a plain `TODO:`, and the chat copy is the same.

Line done:

```
Tests pass. In a week I will ask you to write it again, in a new spot, with the test hidden.
```

At commit in a shared repo with the line open:

```
Your line in retry.py:42 was open, so I filled it before the commit. Saved for later as a review.
```

### 3.8 Explain back

```
That step passed. In two or three sentences: why does the retry reuse the same key? (skip ok)
```

After:

```
Partly. You covered: same key on every retry ("reuses the key from the first call").
Missing: what the provider does when it sees a key twice. See client.py:40.
Graded by a model against points written from the code. Mark it yourself: right, partly, or missed.
```

### 3.9 Review first

```
Reviewing PR 482 from the agent. Look first?
Note any defects with file:line, or say "looks clean". I hide the PR summary until you are done. Or "skip".
```

After:

```
Locked: 2 findings.
retry.py:42, high: delay grows without a cap. Show it with a test? Yes, or later.
client.py:18, low: unused import.
Here is the PR summary and the agent's review.
Back to: review PR 482. Next: read the summary.
```

When settled later, in the next review session:

```
PR 482 settled. Your retry.py:42 finding was confirmed by your test. Counts toward your map.
client.py:18 is still unconfirmed. Unconfirmed never counts against you.
```

### 3.10 Plan first (Deep)

```
Before I plan: list the steps you would take, and how we will know it is done. (skip ok)
```

After:

```
My plan has 5 steps. Yours has 4. The one you did not list: migrate existing rows before the new column is required.
Back to: add currency. Next: step 1.
```

### 3.11 Design call (Deep)

```
You chose one table per currency. What do you expect this makes harder later? One line. (skip ok)
```

When the code is next touched:

```
Three weeks ago you chose one table per currency and said reporting across currencies would be harder.
Today's change adds a cross-currency report. Was it harder? yes, no, or not sure.
```

### 3.12 Session start offer

```
2 reviews due, about 2 minutes. Say "review" now, or later.
```

On a surface where chat answers cannot count, add: `In your pad they count toward your map: firsthand pad`.

If an open line exists in this repo, it comes first.

### 3.13 The weekly line

First session of the week, after the first prompt is handled, once:

```
Last week: you named the cause of 2 of 5 failing tests before the agent did. The week before: 0 of 4.
Say "weekly off" to stop these.
```

The engine picks one fact from a fixed list, all from the user's own record, never compared with other people: causes named before the agent; Review-first findings confirmed; ideas that moved up or down; your lines written without reading the test; Fresh repo tasks passed. If no fact exists, nothing is shown.

### 3.14 Reminders ignored

After three ignored reminders, next session, once:

```
You did not open the last 3 reminders. Keep 18:30, change the time, or stop?
```

No answer stops reminders and says so.

### 3.15 Drills

```
Drill: a real bug from payments-api, three weeks ago. Agent off for this one. It runs in a container with no network.
Checking this bug still reproduces (8s). Say "cancel" to stop.
```

No container runtime:

```
Replays need a container so old code cannot reach your files or the network. Install Docker or Podman, then say "drill" again.
```

### 3.16 Fresh repo

```
Fresh repo: a small change in a public Go project you have not opened. Agent off. It uses an idea you practised in payments-api.
Size: one function and its caller. No timer.
I will clone it from github.com and run it in a container with no network.
Start? Yes, or later.
```

On submit:

```
3 of 4 hidden tests passed. The one that failed: test_retry_after_header.
Here is the real commit. What did it do that yours did not? One line.
```

### 3.17 Pressure

```
Sounds urgent. No learning questions this session. Say "save it" to keep this for later.
```

### 3.18 Quiet controls

`quiet for 2h`, `quiet today`, `quiet in this repo`, `quiet on this branch`, `learning off`. Each confirms in one line and says how to undo. These only narrow, so they work from any channel.

### 3.19 Widening needs the pad

```
Turning on model grading needs your confirmation in the pad. Open it with: firsthand pad
```

---

## 4. Waiting and failure states

| State | Copy |
| :- | :- |
| Model feedback queued | `Saved. Feedback at the end of this session. You will see it at your next review.` |
| Graders disagree | `Two readings disagree. Reading A: ... Reading B: ... Your map does not change on this one.` |
| Grader unavailable here | `I cannot grade this here. It will be graded at your next local session.` |
| Cost budget reached | `This week's grading budget is used. Open answers wait until Monday, or raise it in the pad.` |
| Phone answer | `Saved. Answers from the phone app count as met.` |
| Cloud session, import line | `This is a cloud session. To keep today's answers, run this at home: firsthand import ...` |
| Record locked | `Another agent is writing your record. Trying again in a moment.` then success or `Run firsthand check.` |
| Signing unavailable | `Commit signing is not available here, so I keep an unsigned hash chain. Your record still works.` (once) |
| Secret found in an answer | `Your answer had something that looked like a token. I saved it as [redacted].` |
| Bad key refunded | `I re-checked that question and the key looks wrong. Your miss is removed.` |
| Fresh repo setup failed | `This task did not build here. I dropped it and nothing was recorded. Say "fresh" for another.` |
| Tag unclear | Silence. |

---

## 5. The map

Designed for a terminal and a screen reader first. A linear list, no grid, no table, no colour carrying meaning.

```
What you have shown without the agent, and how recently.
Applied: idempotency keys, checked 9 days ago.
Recalled: exponential backoff, checked 3 days ago. N+1 queries, not checked lately.
Slipped: SQL indexes. Was Recalled, missed Tuesday. Back Friday.
Met, not yet shown later: database migrations, retry jitter.
Reviews due today: 2.
Say "map all" for more.
```

Rules:

- One number on the first view: reviews due today.
- Evidence age on every level. "Not checked lately" replaces the age past the margin.
- Met is its own line, never mixed with levels.
- Best level appears only in `map all`.
- `map all` adds, linearly: per skill and idea, how each piece of evidence was graded, how it arrived, and its format; "based on N of M due items answered"; which ideas are not being reviewed and how to pick growth areas; calibration on delayed items; prediction accuracy on its own line; field evidence; Fresh repo tasks; what this surface can count.
- Codebase guide ideas under their own heading, "This codebase".

---

## 6. Accessibility requirements

A release ships only when every item passes on at least one agent per tier, and in the pad.

1. Full loop with a screen reader (VoiceOver and NVDA) and keyboard only, including the pad.
2. Every answer can be given by voice dictation.
3. No timers anywhere. Fresh repo shows a size, never a time.
4. No single-key actions that write to the record. Letter shortcuts off by default (founder decision 5).
5. `NO_COLOR` respected.
6. No tables, box art or ASCII diagrams in learning messages.
7. Verdict word first; resume cue last.
8. Every question restates its context in one line (https://www.w3.org/TR/coga-usable/).
9. Undo for every record change that is not a locked answer; confirmation before "don't know" locks.
10. For the phone device link: 320px reflow, 200% zoom, reduced motion, 44px targets, one polite live region.

---

## 7. Moving between surfaces

| From | To | What the user sees |
| :- | :- | :- |
| Agent A | Agent B, same repo | Open line first, then the due offer |
| Laptop | Phone vendor app | Due reviews offered; answers count as met |
| Phone | Laptop | `From your phone: 2 answers, saved as met.` |
| Cloud session | Laptop | `Imported 3 answers from a cloud session, saved as met.` |
| Any | Offline | Saved locally; one notice |

---

## 8. Turning it off

"learning off" stops all questions, reminders and the weekly line at once, keeps the record, and says how to turn it back on. `firsthand uninstall` restores every file it changed from its backups, shows a diff for any file the user changed since, leaves the record, and prints where it is.
