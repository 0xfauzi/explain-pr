# Research track: experience design and developer flow

Status: research report, 2026-11-07. Track owner: experience design. Nothing here is built. This
report designs the experience for a general product that anyone can install on any coding agent.
It uses the earlier round in `design/learning-experience/` as evidence, not as the answer.

Inputs read: `design/learning-experience/experience.md`, `design-system.md`,
`critique/accessibility.md`, `critique/product-design.md`, `critique/learning-scientist.md`,
`research/product-patterns.md`, `skills/learning-while-building/SKILL.md` (Voice), and the sibling
reports in this folder, mainly `surfaces.md` (capability tiers). Web sources are listed inline and
again in section 16.

## How to read the tags

- **[verified: source]** a claim about a product, harness or study that a source in this session
  supports. "surfaces.md" means the sibling report verified it with the source it names.
- **[unverified]** a claim about a product or harness that no source here confirms.
- **[inference]** my design judgment, not a fact.
- "Needs to be measured" means no number should be used until we measure it.

---

## 1. Findings that matter most

1. **Interruptions cost most when they land mid-task, and least at task boundaries.** Iqbal and
   Bailey found that delivering notifications at breakpoints lowers frustration and reaction time
   against immediate delivery, and coarser breakpoints lower the cost more [verified:
   https://www.interruptions.net/literature/Iqbal-CHI08.pdf], [verified:
   https://www.interruptions.net/literature/Iqbal-TOCHI10.pdf]. An agent knows its own breakpoints
   exactly: "starting a long step", "tests passed", "about to commit". No other product has such
   clean signals. The design must use them and nothing else.
2. **Interrupted people work faster but feel worse.** Mark, Gudith and Klocke found that
   interrupted participants finished faster but reported more stress, frustration, time pressure
   and effort [verified: https://www.ics.uci.edu/~gmark/chi08-mark.pdf]. So a learning question
   that "costs no time" can still cost the user. Measure felt cost, not just time.
3. **Developers resume by reconstructing context, so a resume cue is part of the interruption
   design.** Parnin and Rugaber studied about 10,000 recorded sessions from 85 programmers and
   found only 10% of sessions started editing within a minute of resuming [verified:
   https://sites.cc.gatech.edu/reverse/repository/resumptionstrategies.pdf]. Altmann and Trafton's
   memory-for-goals model predicts that cues encoded before the interruption speed resumption
   [verified: https://www.interruptions.net/literature/Trafton-IJHCS03.pdf]. Every learning
   exchange must end with the way back, in one line.
4. **Interruptions are not bad in every phase.** Meyer, Barr, Bird and Zimmermann (5,971 responses
   at Microsoft) found meetings and interruptions are unproductive in development phases but
   constructive in planning, specification and release, and that control over the day (agency) is
   key to a good day [verified:
   https://discovery.ucl.ac.uk/10090507/1/Barr_Today%20was%20a%20Good%20Day.%20The%20Daily%20Life%20of%20Software%20Developers_AAM2.pdf].
   Learning questions fit planning and wrap-up better than deep debugging. The user decides; the
   product never takes agency away.
5. **The learning that AI erodes is kept by the user's own thinking.** In Shen and Tamkin, 52
   participants learned the Trio library; the AI group scored 4.15 points lower on a 27-point quiz
   (Cohen's d = 0.738, p = 0.010). The three high-scoring patterns were Conceptual Inquiry, Hybrid
   Code-Explanation and Generation-Then-Comprehension; the low-scoring ones were AI Delegation,
   Progressive AI Reliance and Iterative AI Debugging [verified:
   https://arxiv.org/html/2601.20245v2]. Our product does not need to slow the build. It needs to
   change the user's interaction pattern from delegation to inquiry and explanation.
6. **Developers use coding agents in two modes, and only one tolerates questions.** Barke, James
   and Polikarpova describe acceleration (the programmer knows what to do and is "in the zone",
   distracted by long suggestions) and exploration (novel tasks, unexpected behaviour) [verified:
   https://arxiv.org/abs/2206.15000]. Learning questions belong in exploration. In acceleration
   the product should go quiet and keep a note for later.
7. **Streaks and points move attention to the number.** Rewards contingent on doing a task
   undermine free-choice intrinsic motivation (Deci, Koestner and Ryan, 128 studies) [verified:
   https://depts.washington.edu/techdocs/papers/deciExtrinsicRewardsAndIntrinsicMotivation99.pdf].
   Paid streak repair is catalogued as a deceptive pattern [verified:
   https://deceptive.design/articles/when-a-user-uses-duolingo-on-a-series-of-consecutive-days-this-is-called-a-streak-if-users-miss-a-day-they-can-pay-to-repair-it].
   Boot.dev's founder calls weekly streaks its most important game feature and names the downside:
   they fully reset if you miss a week [verified:
   https://blog.boot.dev/news/bootdev-beat-2024-03]. For people building real projects on uneven
   days, no streak at all.
8. **Learners judge effortful learning as worse, even when it works better.** Yan, Bjork and Bjork
   found learners keep believing blocked practice is better even after interleaving helped them
   more [verified:
   https://sites.lifesci.ucla.edu/psych-bjorklab/wp-content/uploads/sites/13/2016/11/YanBjorkBjork2016.pdf].
   So satisfaction ratings will push the product toward less learning. Tune by delayed outcomes,
   not by how a session felt.
9. **Feedback about the person does little; feedback about the task and the next step works.**
   Hattie and Timperley separate task, process, self-regulation and self levels; self-level
   feedback (praise) is weak, and "feed forward" (what to do next) is the least given and among
   the most useful [unverified: secondary summaries, e.g.
   https://sola.kau.se/keeponteaching/about-feedback-feed-up-feed-back-och-feed-forward/?lang=en].
   Error management training, which frames errors as a normal part of learning and encourages
   exploration, outperforms error-avoidant training in Keith and Frese's meta-analysis [verified:
   https://www.humanw.tu-darmstadt.de/media/orgpsy/preversioneffectivenessoferrormanagement.pdf].
   This sets the tone of being told you are wrong.
10. **Parity on every surface is parity of outcome, not of pixels.** The sibling report finds
    every surface can show text and take a reply (tier 0), most can run MCP tools, only some can
    show a native question form, and only a few can show designed UI [verified: surfaces.md
    sections 1 and 8]. The experience must be complete in plain text, and each richer surface must
    only make the same actions faster.

---

## 2. What the earlier round learned, and what changes

The earlier round designed for one person in Claude Code with a claude.ai artifact as the Room.
Its critics found real problems. This table says what to keep for a general product and what to
change.

| Earlier decision or finding | Keep, change or drop | Why |
|---|---|---|
| Ask only at breakpoints; prediction before a long step, explain-back after it works | Keep, and widen to all agents through hooks or instructions | Strongest evidence in section 1 (findings 1, 3, 5). |
| "Not now" and "just do it" free and instant | Keep | Agency (finding 4). |
| No streaks, points, praise, confetti or sound | Keep | Findings 7 and 9. |
| Best level as outline, latest as fill; decay visible | Keep | An honest record is the product. |
| Same-session explain-back confirms "With help" at most (D10) | Keep, and explain it in the UI, because users will read it as unfair | Learning scientist B1. Emotional design in section 7. |
| One learning event, one transcript row (D14) | Keep, and make it a cross-agent rule | Product design M1. |
| Chat door drawn richer than any harness can draw it | Drop. Design the plain-text door first | Product design B1. |
| The Room is a claude.ai artifact | Change. The Room is a local web page served from the user's machine, plus any host UI tier that exists | Decision 6 and decision 1. A claude.ai artifact exists on one vendor only [inference]. |
| Phone through the Claude app | Change. Phone through each vendor's own app where one exists, and a local-network or one-tap page otherwise | surfaces.md finding 7. |
| Keyboard shortcuts with a settings switch (D17) | Change. Off by default | Founder decision 5. Accessibility B2. |
| Sticky bars and toasts | Keep the fixes: nothing sticky below 560px height, no timed toasts | Accessibility B1, M2. |
| One live region, focus moves only after the user's action | Keep, and add the terminal equivalent (section 10) | Accessibility M1. |
| Internal ids in the UI | Drop | Product design M3. |
| Demo person "Sam", a payments service | Change. Design for at least five user types (section 3) | General product. |
| Acceptance tests measure friction only | Change. Add learning outcomes and felt cost | Learning scientist M11 and finding 2. |

---

## 3. Who this is for

A general product must work for people who differ in skill, time, and why they learn. These five
types cover the range. They are design targets, not market sizes; `users-market.md` holds the
market evidence.

| Type | Situation | What they need from the experience | The risk to design against |
|---|---|---|---|
| New developer | First job or bootcamp, builds with an agent from day one | Being asked to think first; plain words; safe mistakes | Shame. Being wrong often, in front of a tool, must not feel like failing an exam. |
| Career switcher or hobbyist | Builds a side project at night, uneven days | No backlog guilt; reviews that fit a phone; one reminder at most | Dropping out after a missed week. |
| Senior engineer in a new domain | Expert in one stack, new to another (for example a web developer writing a database) | Questions at their level; no tutorial voice; "just build" respected | Feeling patronised. Arc's founder said the product was "too different, with too many new things to learn, for too little reward" [verified: product-patterns.md, Browser Company letter]. |
| Engineer keeping skills sharp | Uses agents all day, worried about decay | A record that shows decay honestly; debugging drills | Treating the record as a score to protect. |
| Disabled developer | Screen reader, voice control, low vision, ADHD, dyslexia, RSI | Every action in plain text; no timers; no single-key actions; low reading load | Any step that needs a mouse, colour or fast reaction. |

One rule for all five: **the record is private to the user.** If it ever becomes a manager's
performance metric, users will protect the number instead of learning [inference, supported by
finding 7]. The product never shares it by default, never offers a team leaderboard, and says so
in onboarding.

---

## 4. The experience in one page

You install it with one command or one marketplace click. Next time you build, nothing changes
until the agent reaches a natural break on something new to you. Then it asks one short question,
says why, and says how to skip. You answer in a line, or skip. The agent keeps building either
way. When it works, it may ask you to explain why in your own words, or leave one marked line of
the real code for you to write. You see what you said next to what happened, plainly, with the
evidence, then one line puts you back in the build. Days later, at most three old ideas come back
as new questions, at the start of a session, in a page on your machine, or on your phone after one
reminder at the time you chose. A map shows what you can do without the agent. It goes down when
you forget, and comes back when you review. It lives in a git repo on your machine that only you
control.

The same loop, the same words and the same record exist on every agent. A surface with more UI
makes it faster; a surface with less makes it plainer. Nothing is missing anywhere.

---

## 5. Principles

Each principle has a rule the product can be tested against. These are the design rules returned
in the summary.

### P1. The build always wins

The user came to build. A learning moment never blocks the build unless the user chose a "your
line" (section 6.4). The agent keeps working while a question is open, and a question left open
simply expires into the review queue. *Test:* in every flow, the agent's next build step does not
wait on a learning answer, except a chosen "your line".

### P2. Ask only at the agent's own breakpoints

The only moments a question may appear: just before a long step starts, just after a step passes
(tests green, build runs), at commit or session end, and at session start for due reviews. Never
in the middle of an edit, never while the user is typing, never during an error loop the user is
driving (acceleration mode, finding 6). *Test:* every question event is tagged with one of these
four breakpoints.

### P3. A budget, not a schedule

The default budget per session: at most one prediction and one explain-back per task the user
chose to learn from, at most one unprompted learning turn per 10 minutes (kept from the earlier
round, and it needs to be measured), at most 3 due reviews a day (decision 3), at most one
reminder a day at the user's time (decision 7). The budget shrinks when the user skips: two skips
in a session and the agent stops asking for that session and says so once. *Test:* counted in the
record; a session never exceeds the budget.

### P4. Read the room

The agent goes quiet without being told when the signals say the user is under pressure: words
such as "urgent", "prod is down", "hotfix", "deadline"; a failing deploy; repeated quick
corrections. It says once: "I will skip learning questions for this one. Say 'teach me this later'
to save it." This is an inference rule and needs to be measured for false positives [inference].
*Test:* a scripted urgent prompt produces no question.

### P5. Think first, then the agent explains

Every learning moment starts with the user producing something: a prediction, an explanation, a
hypothesis, one line of code. The agent's explanation comes after. This is the Conceptual Inquiry
and Generation-Then-Comprehension pattern from Shen and Tamkin made into a habit [verified:
https://arxiv.org/html/2601.20245v2]. Khanmigo is built on the same refusal to hand over answers
[unverified: secondary, e.g.
https://ai.engineer/talks/scaling-ai-in-education-a-khanmigo-case-study]. We differ in one way:
the user can always say "just tell me", and the agent does, at once, and records that the attempt
had help. A tutor that refuses a working adult loses them [inference].

### P6. Complete in plain text, faster with more UI

Every action exists as a short reply in chat: an answer, "sure", "skip", "don't know", "just tell
me", "later", "show my map". A native question form, a designed card, a local page and a phone are
faster doors to the same action. *Test:* the full loop passes on a tier 0 surface (surfaces.md
8.1) with a screen reader and no mouse.

### P7. One event, one line

A learning event takes one line in the transcript when collapsed, and its result line is the
user-facing copy. No plumbing rows. *Test:* count rows per event in each agent.

### P8. Always end with the way back

Every learning exchange ends with one line: `Back to: <task>. Next: <step>.` On every surface, in
the same words. This is the resumption cue that Altmann and Trafton's model predicts will help
[verified: https://www.interruptions.net/literature/Trafton-IJHCS03.pdf]. *Test:* the last line of
every exchange matches the pattern.

### P9. Feedback about the work, never about the person

"Correct.", "Not quite.", "No." Then what was right, what was missing, the evidence (`path:line`
or the test output), when it comes back, and the way back. No praise, no "Great job", no mascot.
*Test:* a word list check on all copy (section 8.3).

### P10. Mistakes are safe and expected

Predictions are compared, never graded, and never move the record. A wrong answer costs nothing
but an earlier review. The copy says this the first three times, then stops saying it. *Test:* no
prediction outcome changes a level.

### P11. An honest record that can go down

The record shows what the user did without help, at a delay. It drops when a review is missed and
returns when one is passed. No streaks, points, badges, leaderboards or percent bars. The only
count on any surface is how many reviews are due today. *Test:* banned pattern list (section 9).

### P12. The user controls the dial

One setting with four positions, shown in onboarding and always one reply away: **Off** (record
only reviews you start), **Light** (reviews only, no questions during builds), **Standard**
(default: questions on new ideas at breakpoints), **Deep** (questions on every task you mark,
"your line" more often, drills). Plus per task: "just build" and "teach me this one". *Test:* each
position changes behaviour on every surface.

### P13. Accessible by default, not by setting

Every default is the accessible choice: shortcuts off, no timers, no motion that cannot be
stopped, no colour-only meaning, plain language. A setting can add speed; no setting is needed to
make it usable. *Test:* section 10 checks on every release.

### P14. Private by default, portable always

The record is a local git repo (decision 1). The user can read it as plain files, export it,
delete it, and point it at a remote only if they ask. The experience never asks for an account to
start [inference: reduces first-run friction; see section 11].

---

## 6. The moments, designed

Each moment says what the user sees on a plain-text surface first, then what richer surfaces add.
Copy is exact. Words in angle brackets are filled in.

### 6.1 A question before a long step (prediction)

Trigger: the agent is about to run a long step (a test suite, a migration, a build) and the task
touches an idea the record marks Not yet or With help.

Plain text, first three times:

```
Starting the tests now. While they run, one question on retries (new to you):
If the gateway times out on attempt 1 but charged the card, what does attempt 2 do?
Answer in a line and say how sure: guess, fairly sure or sure.
Or say skip. A wrong guess here costs nothing.
```

After three, the last two lines shrink to: `Answer + how sure, or skip.`

Richer surfaces: a native question form (MCP elicitation, AskUserQuestion, `request_user_input`)
shows the confidence as three choices [verified: surfaces.md 8.4]. A designed card (MCP App, IDE
webview, local page) adds the code excerpt. None of them blocks the build.

Why it works: it lands at a coarse breakpoint (finding 1), names the reason ("new to you"), names
the cost of being wrong (nothing), and gives the exit.

### 6.2 The reveal after a prediction

```
You said: attempt 2 charges again. It did: the gateway returned the first charge (billing/charge.py:48).
The gap: the idempotency key makes the retry safe. That is the idea we use next.
Back to: retries in the payment worker. Next: the dead letter queue.
```

No verdict word, because predictions are compared, not graded (P10).

### 6.3 Explain it back after it works

Trigger: tests pass on a task the user chose to learn from.

```
It works. Before we move on: in one or two lines, why does the retry not charge twice?
Say how sure. Or later, and it comes back as a review.
```

Verdict, correct but same session:

```
Correct. This counts on your record when it holds at your review on <date>.
Back to: ...
```

The user will find this rule unfair at first ("I got it right"). Say why, once, the first time:
`Right after building it, an idea is easy to explain. The review checks it stuck.` [inference from
learning scientist B1; Rhodes and Tauber are cited there].

### 6.4 Your line (decision 2)

Trigger: a new idea, Standard or Deep dial, and a line in the build that carries the idea (the key
line, or the assert that proves it).

```
I left one line for you: billing/charge.py:48, marked # YOUR LINE.
It sets the idempotency key. The tests will tell you if it works.
Write it when you are ready, then say done. Or say write it, and I will.
```

Design rules for "your line":

- One line, never a function. It must be testable by tests that already exist or that the agent
  writes first.
- The agent builds everything else around it, so the user writes in context, not in a blank file.
- The agent may work on other files while the line is open, but does not run steps that need it.
- "write it" is always free. The record notes the attempt had help. No other cost.
- No timer, ever (WCAG 2.2.1). If the session ends, the line stays marked in the working tree with
  a comment, and the next session start says so first.
- On failure, the test output is the feedback. The agent offers one hint ladder: `Want a hint? Say
  hint. Or say write it.` Never the answer unasked.
- The marker is a code comment in the language's syntax, so it is visible in every editor,
  terminal and diff, and screen readers read it as text.

This is the strongest generation event available, and it costs no extra interruption because it is
inside the build [verified: learning scientist M10, which cites completion problems]. Its risk is
frustration for users in acceleration mode, so it never appears on the Light dial and never under
P4 signals.

### 6.5 Reviews

When: at session start (one line, ignorable), in the local Room page, or on the phone after the
daily reminder. At most 3 a day (decision 3). Overflow spreads over later days, as Anki's load
balancing does for reviews [unverified: Anki load balancer behaviour from forum and add-on docs,
https://github.com/open-spaced-repetition/fsrs4anki-helper].

Session start, plain text:

```
2 reviews are due (about one line each). Say review, or ignore this.
```

A review shows no code, no old answer and no old feedback until the answer is locked. Reviews are
free text or a number, never options.

### 6.6 The daily reminder (decision 7)

One reminder a day at most, at a time the user picks in onboarding, only if something is due, and
never while the user is at the machine (presence rule kept from the earlier round). On iOS a
reminder should use a passive or active level, never time-sensitive, so it cannot break through
Focus [verified: https://www.wwdcnotes.com/notes/wwdc21/10091]. After three ignored reminders in a
row, it stops and leaves one line at next session start: `Reminders paused, since they were not
helping. Say remind me to turn them on.` This is Duolingo's own finding that repeated reminders
lose effect, used to stop rather than to escalate [verified: product-patterns.md, Yancey and
Settles KDD 2020].

Copy: `2 short reviews are ready. About a minute.` The time estimate is shown only after it is
measured from the user's own history; until then the reminder says `2 short reviews are ready.`

### 6.7 Coming back after weeks away

No backlog, no count of missed days. At most 3 reviews that day, chosen by what matters most for
the current project, the rest spread out.

```
3 reviews are ready today. The rest are spread over the next days.
```

Never "You missed 23 reviews". Backlog guilt makes people quit spaced-repetition tools [verified:
product-patterns.md finding 6 and the critique M9].

---

## 7. Emotional design

The product will tell people they are wrong many times. How that feels decides whether they stay.
Four moments matter most.

### 7.1 Being told you are wrong

Goals: the user feels informed, not judged; the error feels like the normal cost of learning
(error management, finding 9); the next step is obvious.

Rules:

1. Lead with the verdict word, plain. Hedging ("Almost!") reads as patronising to experts and
   confusing to novices [inference].
2. Then what was right, in one clause, as information, not praise: `You had the timeout right.`
3. Then the missing piece, with evidence.
4. Then when it returns, and the way back.
5. Never compare to other people. Never count misses in the message.

```
Not quite. You had the timeout right. The missing part: the key must stay the same on every attempt (billing/charge.py:48).
This comes back tomorrow.
Back to: ...
```

A sure miss (the user said "sure" and was wrong) is the most useful event: confident errors are
corrected more readily than unsure ones (hypercorrection) [verified: product-patterns.md, Metcalfe
2017, https://pubmed.ncbi.nlm.nih.gov/27648988/]. Say it plainly and frame it as useful, once:

```
No. You were sure, so this one is worth a second look: sure answers that turn out wrong are the ones people tend to fix best.
```

Grade disputes: every verdict accepts `I think that grade is wrong`. The agent shows the fixed
answer and the rubric, regrades once, and records both. A system that cannot be argued with feels
unfair, and the dispute data shows grader drift [verified: learning scientist minor 8].

### 7.2 Seeing a skill decay

Goals: decay feels expected and fixable, not like a loss.

Rules:

- Show decay as fact plus next step, never as loss: no red, no down arrow, no "lost".
- Keep the best level visible as an outline, so the user sees they knew it once.
- Tie the explanation to how memory works, in one line, the first time.

```
Retries: you had this without help on 3 Oct. Today's review missed it.
Forgetting is expected after a gap; that is why reviews exist. It comes back on Thursday.
```

Never notify about decay. The user sees it when they look at the map or answer a review.

### 7.3 Being asked a question mid-task

Goals: the user feels the question is worth it, that they are in control, and that the build did
not stop.

Rules:

- Name the reason in a few words ("new to you", "you missed this last week"). A question with a
  reason feels chosen; one without feels like a quiz [inference].
- Say the exit in the same breath.
- Never stack questions. One open at a time.
- Never ask in acceleration mode (finding 6) or under pressure (P4).
- After a skip, say nothing more about it.

### 7.4 Writing your line and failing the tests

Goals: a failed test feels like normal engineering, because it is.

```
Tests: 1 failed. test_retry_charges_once: charged 2 times.
That is what the line controls. Want a hint? Say hint. Or say write it.
```

No verdict word here: the test is the verdict. If the user asks the agent to write it, the agent
writes it without comment beyond one line naming the idea.

### 7.5 The overall tone

The tone is an engineer teaching a capable colleague who has not met this mechanism yet, as the
skill's Voice section already says. Not a teacher, not a coach, not a game. Calm, short, specific.
The product's personality is the absence of noise.

---

## 8. Session, feedback and progress patterns from learning products

What the best learning products do, and what we take. Product claims carry their tag.

### 8.1 What each product teaches us

| Product | What it does well | What we take | What we refuse |
|---|---|---|---|
| Duolingo | Tests reminder timing at scale; reminders lose effect when repeated [verified: product-patterns.md, KDD 2020] | One reminder, varied, stop when ignored | Streaks, paid streak repair [verified: deceptive.design link above], guilt notifications [unverified: press] |
| Brilliant | Problem first, explanation second; a small daily bar [unverified: https://brilliant.org/help/using-brilliant/what-is-a-streak returned little] | Think first, explain second | The streak |
| Anki | Answer hidden until the user acts; daily review limits; load balancing and Easy Days; desired retention default 0.9 [unverified: FSRS docs and forums, https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm] | Daily cap, spread overflow, show only the due count | Self-grading as the only grade; cards with no context |
| Exercism mentoring | The student asks for feedback on a specific iteration; can submit a new iteration; either side can end it [verified: product-patterns.md, https://exercism.org/docs/mentoring/faqs] | One answer, one feedback, at most one revision; the user starts deep feedback | Open-ended threads |
| Khanmigo | A tutor that guides toward the answer and does not hand it over [unverified: https://ai.engineer/talks/scaling-ai-in-education-a-khanmigo-case-study] | Think first by default | Refusing an adult who asks for the answer |
| Boot.dev | Game features (weekly streaks, XP) that beginners report as motivating [verified for streaks: https://blog.boot.dev/news/bootdev-beat-2024-03; XP and leagues unverified] | Nothing from the game layer | All of it, for the reasons in finding 7 |
| Quantum Country and Orbit | Prompts embedded in the reading; reviews arrive days later [verified: product-patterns.md, https://numinous.productions/ttft/] | Questions embedded in the real work | None |
| Execute Program | Every prompt is executable [unverified: product-patterns.md via Matuschak notes] | "Your line" and predictions checked by real tests | Progress that rewards new lessons over recall |

### 8.2 Session design

- **There is no session to start.** The build is the session. Reviews are the only separate
  activity, and they are three items at most. This is the main difference from every product in
  8.1, and our advantage: questions come from the user's own code [inference].
- **A review session is one screen per item and ends itself.** After the last due item: `Done for
  today.` and the way back. No "keep going" upsell, no "practise more" button on the end screen.
  Extra practice exists (drills on the map) but is never offered at the end.
- **Length.** A review should take about a line to answer. How long that really takes needs to be
  measured.

### 8.3 Feedback copy rules

Banned words and patterns in learner-facing copy: "Great", "Awesome", "Amazing", "Well done",
"Oops", "Uh oh", exclamation marks, emoji, mascots, "you failed", "you lost", "streak", "XP",
counts of misses, comparisons to others. Allowed verdict words: Correct, Not quite, No, Compared.
A lint check runs over all copy in the skill, the MCP server and the Room.

### 8.4 Progress design

- **What is shown:** per idea and per area, the four levels (Not yet, With help, Without help, New
  situation), best as outline, latest as fill; a calibration view (how often "sure" was right,
  with "too few answers to tell" under a minimum that needs to be measured); a list of sure misses
  and whether each has since been answered right.
- **What is never shown:** streaks, days in a row, points, percent complete, rank, time spent as a
  score.
- **When it is shown:** only when the user opens it. The map is never pushed.
- **Weekly line (optional, off by default):** at session start on Monday: `Last week: 2 ideas
  moved to Without help. 1 came back for review.`

---

## 9. Banned patterns

A design review rejects any of these. Each is tied to evidence or a decision.

1. Streaks, streak freezes or repair; points, XP, badges, leaderboards (finding 7).
2. Guilt or loss copy, sad mascots, "you missed" counts (6.7).
3. More than one reminder a day, outside the chosen time, or while the user is at the machine
   (decision 7, presence rule).
4. A timer on any question, or a toast with an action that vanishes (WCAG 2.2.1).
5. A single key that writes to the record (WCAG 2.1.4, decision 5).
6. A question during an edit, while typing, or under pressure signals (P2, P4).
7. A question that blocks the build, except a chosen "your line" (P1).
8. More than 3 due reviews offered a day by default (decision 3).
9. "Keep going" or "one more" prompts at the end of a review.
10. Sharing the record by default, or a team view of individual records (3).
11. Praise or self-level feedback (finding 9).
12. Colour as the only carrier of a level (product-patterns.md finding 10).

---

## 10. Accessibility by default, on every surface

The earlier round's WCAG 2.2 AA work on the Room is kept in full (`design-system.md` section 4 and
`critique/accessibility.md`). A general product adds surfaces the earlier round did not cover.

### 10.1 Chat and terminal

- Every learning message is plain text first. Formatting (bold, colour) is extra and never carries
  meaning alone. Respect `NO_COLOR` where the agent's renderer allows it [inference: the
  convention is widely used; the product's control over host rendering varies by agent,
  unverified].
- No box-drawing art, tables or ASCII diagrams in learning messages. Screen readers read them as
  noise [inference].
- Short lines. One idea per line. The verdict word first, so a screen reader user hears the result
  first.
- The resume cue is always last, so a user who stops listening after the verdict loses nothing.
- Code references are `path:line`, which every editor and terminal can open [inference].
- The command-line guidelines say "Catch errors and rewrite them for humans" and that discoverable
  tools "suggest what command to run next" [verified: https://clig.dev/]. Every error from the
  tool ends with the one reply or command that fixes it.

### 10.2 Native question forms

- Prefer them where they exist: they are host UI, so the host's accessibility applies. Whether
  each host's form works with VoiceOver, NVDA and voice control is untested and needs to be
  measured per agent.
- Every form has a free-text path, so a user can always type.

### 10.3 The Room (local page) and designed cards

Keep: 44px targets, one polite live region, focus moves only after the user acts, modal sheets on
phones, nothing sticky below 560px height, 320px reflow, dark mode at the same contrast, reduced
motion, no timed toasts, table views for every grid. Shortcuts are off by default (decision 5)
and, when turned on, never single letters that write to the record.

### 10.4 Phone

- One confirmation tap is allowed only where no tap-free path exists (decision 4). The tap target
  is the full-width primary button, 44px or more.
- Answers by voice dictation must work: free-text fields, no custom input widgets that block the
  system keyboard [inference].
- Reminder copy readable on a lock screen without opening the app, with no answer content shown
  (privacy).

### 10.5 Cognitive accessibility

The W3C cognitive accessibility guidance asks designs to help users understand what things are,
find what they need, avoid mistakes, keep focus, and not rely on memory [verified:
https://www.w3.org/TR/coga-usable/]. Applied:

- Every question restates its context in one line; the user never needs to remember an earlier
  message to answer.
- Plain words, short sentences, the technical term introduced once and then used consistently (the
  skill's Voice).
- Undo for every record change that is not a sealed answer, and confirmation before "I do not
  know" locks.
- One task per screen in the Room.
- Reading load is a design budget: a question card's instructions take at most two lines after the
  first three cards (product design M2).

### 10.6 Testing

Each release runs, on at least one agent per tier (surfaces.md 8.7): the full loop with a screen
reader and keyboard only; the Room at 320px, 640 by 360 and 200% zoom; voice control answering one
review; reduced motion. Results are a release gate, not a report.

---

## 11. Onboarding and progressive disclosure

### 11.1 What good developer tools do

- Discoverable command-line tools have full help, many examples, and suggest the next command
  [verified: https://clig.dev/].
- Linear teaches its key action by having the user do it, in context, once [unverified:
  third-party teardowns cited in product-patterns.md].
- The fastest path to value is the real action on the user's own work, not a tour [inference,
  supported by product-patterns.md finding 7].

### 11.2 Install and first run

1. **Install.** One command, or one marketplace click where the agent has a marketplace. No
   account. The install creates the local record repo (decision 1) and prints where it lives.
2. **Three questions, once, in chat, each with a default:**
- `How much learning while you build? Light, Standard (default) or Deep.`
- `A daily reminder for reviews? Pick a time, or none (default).`
- `Your record stays in <path>, in git, on this machine only. OK?`
3. **Then nothing**, until the first natural breakpoint on something new to the user. The first
   question is the onboarding. Its copy is the long form in 6.1, which teaches skip, confidence
   and cost by use.
4. **One line at the end of the first session:** `Say show my map to see what you have learned.
   Say learning off any time.`

Time to first learning moment: the first breakpoint in the first session. How long that is in
practice needs to be measured.

### 11.3 Progressive disclosure ladder

| When | What the user meets for the first time | How it is introduced |
|---|---|---|
| First session | A prediction, skip, confidence | By use, in the question itself |
| First passing task | Explain-back; the same-session rule | One line in the verdict, once |
| First new idea on Standard | "Your line" | The line's own message (6.4) |
| First due review (day 3 or later) | Reviews, the daily cap | One line at session start |
| First week | The map | One line after the first review |
| After 10 graded answers | Calibration | One line on the map, not pushed |
| On request | Drills, settings, export, remote | Help text and `show settings` |

Each feature is introduced once, in context, and never again unless the user asks. Help text lists
everything at all times.

### 11.4 Turning it off

"learning off" stops all questions and reminders at once, keeps the record, and says how to turn
it back on. Uninstall leaves the record repo in place and says where it is. Leaving is easy, so
staying is a choice [inference].

---

## 12. Moving between surfaces without friction

### 12.1 The rule

One learning event has one identity and one state, wherever it is shown. The user never copies
text between surfaces and never sees two states for one question (kept from the earlier round).
The record repo is the source of truth; every surface reads and writes it through the same tool
(surfaces.md section 10 owns the mechanism).

### 12.2 Handoffs

| From | To | What the user does | What they see on arrival |
|---|---|---|---|
| Chat | Room page | Says `open` or follows the link the agent prints | The same question, same state, the code excerpt |
| Room page | Chat | Answers, then the "Back to the build" button | In chat, on the next turn, one line: `From the Room: <topic>, <verdict>.` then the resume cue |
| Reminder | Phone | Taps the reminder | The first due review, nothing else |
| Phone | Desk | Nothing | At next session start, one line summarising phone answers |
| Any | Any, with no network | Nothing | Answers saved locally and synced when possible; a one-line notice, once |

### 12.3 The phone without a vendor app

Some agents have no phone path (surfaces.md finding 7). Options, in order of preference, all
needing measurement before choosing: a page served on the local network when the phone is on the
same network; a one-time pairing tap (decision 4); review by email or calendar reminder that opens
a static page with the questions only, where answers are typed back at the desk. Which works best
for general users needs to be measured. This is an open question (section 13).

### 12.4 The same words everywhere

One copy file holds every string: verdict words, reasons, resume cue, skip words. Every surface
renders from it. Skip words accepted in chat: `skip`, `not now`, `later`, `just build`, `just tell
me`, `write it`, `don't know`. The parser accepts close variants; the exact list needs testing
with real users.

---

## 13. How we will know it works

The earlier round measured friction only. A general product needs three kinds of measure, computed
locally from the record and shared only if the user opts in.

| Measure | What | Target |
|---|---|---|
| Flow cost | Time from a question to the agent's next build step; share of questions skipped; share of sessions where the agent went quiet under P4 | Needs to be measured, then set |
| Felt cost | A once-a-week optional one-line question: `Did the learning questions get in the way this week? Not at all, a little, a lot.` | Needs to be measured. Finding 2 says time alone misses this. |
| Learning | Unaided success at the first review (3 days or more) and at 21 days; share of "sure" answers that are right over time; "your line" written by the user versus by the agent | Needs to be measured. Finding 8 says do not tune by satisfaction. |
| Retention of the product | Share of users still on Standard or Deep after 4 weeks | Needs to be measured |

Cheapest experiments, in order:

1. **Breakpoint fit.** Run the 6.1 prediction at "before tests" versus "before a long edit" with
   10 or more users; compare skip rate and felt cost.
2. **Your line acceptance.** Share of "your line" offers the user writes, split by dial and by
   user type.
3. **Same-session rule.** Show the D10 explanation or not; measure disputes and drop-off after the
   first explain-back.
4. **Plain-text door.** Run the full loop on a tier 0 surface with a screen reader user; record
   every failure.
5. **Reminder.** Reminder at a chosen time versus none; compare review completion and opt-outs.

---

## 14. Founder decisions, checked against this track

| # | Decision | This track's position |
|---|---|---|
| 1 | Local git record, no remote unless asked | Supported for experience: private by default helps emotional safety. Cloud agents cannot write to it [verified: surfaces.md finding 6]; the experience must say this plainly and offer a choice, not fail silently. |
| 2 | "Your line" on | Supported, with the rules in 6.4. Off on the Light dial and under pressure signals, or it will feel like a toll. |
| 3 | At most 3 due reviews a day | Supported. Matches the earlier engine and Anki-style limits. |
| 4 | One confirmation tap on the phone where needed | Supported. |
| 5 | Letter shortcuts off by default | Supported (WCAG 2.1.4). |
| 6 | Feature parity on all surfaces | Challenged in wording only, with evidence: parity of mechanism is impossible (Aider has no hooks or documented MCP) [verified: surfaces.md finding 9]. This track designs for parity of outcome: every action available in plain text, faster where UI exists. |
| 7 | At most one reminder a day, at the user's time | Supported, plus: only if something is due, never while present, stop after three ignored. |

---

## 15. Open questions

1. Can an agent reliably tell acceleration from exploration from its own signals (prompt length,
   edit rate, error loops)? Needs to be measured.
2. How often do pressure signals (P4) misfire, and does a missed quiet moment cost more trust than
   an unneeded one?
3. Which phone path works for agents with no vendor app, for general users who do not run a
   server?
4. Do native question forms in each host work with screen readers and voice control? Untested per
   host.
5. Will users accept the same-session rule (D10), or read it as the product doubting them?
   Experiment 3.
6. Does "your line" raise learning enough to justify its felt cost for senior users? Needs to be
   measured by user type.
7. How should the product behave for unattended cloud agents, where nobody is present to answer?
   Proposal: queue questions to the next attended session, never ask into the void [inference].
8. Is a per-repo dial needed (Deep on a learning project, Light at work)?
9. What minimum number of answers makes the calibration view honest?

---

## 16. Sources

Every source is cited inline with its URL where it is used. The sibling report `surfaces.md` holds
the sources for surface capability claims, and the earlier round
(`design/learning-experience/research/product-patterns.md`, `critique/*.md`) holds the sources it
is cited for. Searches that returned only secondary or weak sources, and so are tagged
[unverified]: Khanmigo design details, Brilliant streak mechanics, Boot.dev XP and leagues,
Duolingo notification tone, Anki load balancer behaviour, and the original Hattie and Timperley
article.
