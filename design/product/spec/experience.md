# Spec: the experience

Part of `../PRODUCT.md` (section 5). Copy rules come from `../research/experience-design.md`. All copy below is the copy the engine returns as plain text on every surface. Richer tiers render the same words.

---

## 1. Copy rules

- Plain words, short lines, one idea per line.
- Verdict word first on graded answers: Correct, Partly, Not yet. Never on predictions.
- Feedback is about the work, never the person. No praise, no mascot, no exclamation marks.
- Banned: streak counts, points, badges, "great job", loss framing, countdowns, backlog counts (experience-design section 9).
- Code references are `path:line`.
- Every exchange ends with `Back to: <task>. Next: <step>.`
- Every question carries a why-now and a one-word skip. Conformance checks both.
- Every error ends with the one reply or command that fixes it (https://clig.dev/, verified in experience-design 10.1).

---

## 2. First run

```
Firsthand is set up.
Your record: ~/.firsthand/record. A git repo on this machine. Nothing leaves it.
Found: Claude Code (full support), Cursor (full support), Copilot in JetBrains (no hooks: breaks rely on the agent following instructions and may be missed).
Three questions. Press enter for the default.
1. How much learning while you build? Light, Standard (default), Deep.
2. A daily reminder for reviews? A time like 18:30, or none (default).
3. Which repos may I read for drills? Paths, or none (default).
Want a 2-minute drill on code your agent wrote this week? Say yes, or later.
```

Work install addition, one line, before the questions:

```
Your employer installed this, and cannot see your record, levels, skips, or whether you use it. No key allows it.
```

Cold start line, if repos were added:

```
I read your own commits in 2 repos. I will stay quiet on 14 ideas you have clearly used. Say "show known" to check the list.
```

End of first session, once: `Say "show my map" to see what you have shown. Say "learning off" any time.`

---

## 3. Exchanges

### 3.1 Question, full form (first three exchanges)

```
New idea: retries with a payment API. Why now: this test runs it. Say "skip" to skip.
If the first two calls time out and the third succeeds, how many charges does the provider see?
Answer, then: sure, think so, guess, or don't know.
```

### 3.2 Question, faded (after three)

```
Retries, since this test runs it (skip ok):
If the first two calls time out and the third succeeds, how many charges does the provider see?
```

Reading load budget: at most two lines of instruction around the question after the first three exchanges (experience-design 10.5). Confidence words are listed again only if the user answers without one.

### 3.3 Prediction reveal

```
What happened: the provider saw 3 charges.
You expected: 1.
The gap: client.py:42 builds a new request on each retry, with no idempotency key.
This comes back in 2 days.
Back to: add retries. Next: add the idempotency key.
```

### 3.4 Graded answer

```
Partly. You named the key as the fix.
Missing: the key must be the same on every retry of one charge. See client.py:40.
Graded by a model, sealed in a separate context. Comes back Friday.
Back to: add retries. Next: run the tests.
```

### 3.5 Call it

```
Test failed: test_refund_twice_is_noop. Want to call the cause first? One line for the cause, one for your first check. I keep looking meanwhile. Or "skip".
```

After the user answers:

```
Your check (log the request id on both calls) tells a duplicate request apart from a double write. Good check.
Cause: two requests, same charge, no key. You said a race in the ledger, which this check would have ruled out.
Back to: fix refunds. Next: I will run your check first.
```

### 3.6 Your line

Open:

```
Your line: retry.py:42. The delay before retry n. Test: test_backoff.py::test_delays.
Hint is free. "write it" hands it back. No timer.
Back to: add retries. Next: I build the rest around your line.
```

Turn end or commit with the line open:

```
Your line in retry.py:42 is open. Write it, or say "write it".
```

Handed back under pressure:

```
Hotfix branch, so I wrote your line in retry.py:42. Saved for later as a review.
```

### 3.7 Session start offer

After the first prompt has been handled, one line:

```
2 reviews due, about 2 minutes. Say "review" now, or later.
```

If an open line exists in this repo, it comes first: `Your line in retry.py:42 is still open, from Tuesday.`

### 3.8 Review

```
Review 1 of 2. Payments, from last week.
A client retries a charge after a timeout. What must stay the same across retries, and why?
Answer, then: sure, think so, guess, or don't know.
```

### 3.9 Drills

```
Drill: a real bug from payments-api, three weeks ago. Agent off for this one.
Checking this bug still reproduces (8s). Say "cancel" to stop.
```

```
test_refund_twice_is_noop FAILED: expected 1 refund, got 2.
1. Your hypothesis, one line.
2. The check you would run first.
3. Sure, think so, guess, or don't know.
Skip costs nothing. A hint is free and marks this "with help".
```

Not reproducible: `This bug no longer reproduces here, so I dropped it. Want a trace drill instead? Yes, or later.`

### 3.10 Pressure

```
Sounds urgent. No learning questions this session. Say "save it" to keep this for later.
```

### 3.11 Quiet controls

`quiet for 2h`, `quiet today`, `quiet in this repo`, `quiet on this branch`, `learning off`. Each confirms in one line and says how to undo.

---

## 4. Waiting and failure states

Every state has plain copy and a next step. Never a spinner without text.

| State | Copy |
| :- | :- |
| Model grading queued | `Saved. Graded at the end of this session. You will see it at your next review.` |
| Grading in progress (shown only if the user waits) | `Grading against the sealed key (5s).` |
| Graders disagree | `Two readings disagree. Reading A: ... Reading B: ... Your level does not change on this one.` |
| Grader unavailable here | `I cannot grade this here. It will be graded at your next local session.` |
| Cost budget reached | `This week's grading budget is used. Open answers wait until Monday, or raise it with firsthand cost set.` |
| Phone answer waiting | `Graded when you next open your computer.` |
| Cloud session, no carry | `This is a cloud session. Today's answers stay only until it ends.` |
| Record locked by another process | `Another agent is writing your record. Trying again in a moment.` then success or `Run firsthand check.` |
| Signing unavailable | `Commit signing is not available here, so I keep an unsigned hash chain. Your record still works.` (once) |
| Tag unclear | Silence. Nothing is shown. |

---

## 5. The map

Designed for a terminal and a screen reader first. A linear list, no grid, no table, no colour carrying meaning.

```
What you can do without the agent, last 30 days.
Recalled or better: idempotency keys (Applied), exponential backoff (Recalled), N+1 queries (Recalled).
Getting there: database migrations. Seen twice, not yet recalled.
Slipped: SQL indexes. Was Recalled, missed on Tuesday. Next: a review on Friday.
Reviews due today: 2.
Unseen-question gap: too few answers to tell.
Your results are self-reported practice. Say "map all" for constructs, sources and grading.
```

Rules:

- Only two numbers on the first view: reviews due today, and the unseen-question gap. No other counts.
- Only constructs and ideas with evidence appear. "Needs more evidence" is a normal state.
- Best and latest levels in words: `idempotency keys: latest Recalled, best Applied`. This is the text equivalent of the earlier outline and fill pattern.
- `map all` expands, still linearly: per construct, per idea, with the grading label, seal label and answer-source label on each piece of evidence, calibration once enough delayed answers exist, the field list, and the Checkup line.
- Codebase-specific guide ideas are listed under their own heading.

---

## 6. Accessibility release gate

A release ships only if every item passes on at least one agent per tier (surfaces T0 to T4), recorded in the conformance table.

1. Full loop with a screen reader (VoiceOver and NVDA) and keyboard only.
2. Every answer can be given by voice dictation: free-text paths everywhere, no custom input widgets that block the system keyboard.
3. No timers anywhere. No timed toasts.
4. No single-key actions that write to the record. Letter shortcuts off by default (decision 5).
5. `NO_COLOR` respected wherever the engine controls output.
6. No tables, box art or ASCII diagrams in learning messages.
7. Verdict word first; resume cue last.
8. Every question restates its context in one line, so no memory of earlier messages is needed (https://www.w3.org/TR/coga-usable/, verified in experience-design 10.5).
9. Undo for every record change that is not a sealed answer; confirmation before "don't know" locks.
10. For any page or phone UI (v2): 320px reflow, 200% zoom, reduced motion, 44px targets for the one phone tap, one polite live region, focus moves only after the user acts (earlier `design-system.md` section 4).

---

## 7. Moving between surfaces

| From | To | What the user does | What they see |
| :- | :- | :- | :- |
| Agent A | Agent B, same repo | Opens it | Open line first, then the due offer after the first prompt |
| Laptop | Phone vendor app | Opens a session there | Due reviews offered the same way |
| Phone | Laptop | Nothing | One line at next session: `From your phone: 2 answers, graded now.` |
| Cloud session | Laptop | Nothing (with carry) | One line: `Imported 3 answers from a cloud session.` |
| Any | Offline | Nothing | Saved locally; one notice, once |

---

## 8. Turning it off

"learning off" stops all questions and reminders at once, keeps the record, and says how to turn it back on. `firsthand uninstall` removes every adapter file it wrote, leaves the record, and prints where it is.
