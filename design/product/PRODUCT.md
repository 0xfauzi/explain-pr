# Firsthand: product specification

Status: final product specification, 7 November 2026. Written by the head of product from the research in `research/`, the four concepts in `concepts/`, and the verdicts of five expert judges. Nothing here is built yet, except the existing skill in `skills/learning-while-building/`.

How to read this:

- Detail lives in `spec/`. This file is the whole product in short form. Each section links to the spec file that holds the rest.
- Claims about a product or harness carry [verified: source] or [unverified]. "[verified: research/x.md]" means the claim is verified, with its URL, in that report.
- No number here is invented. A number with no source is either a design default (marked "design default, needs to be measured") or a pass threshold for an experiment (marked "threshold, a decision").
- Every must-fix item from the judges is traced to the place it is fixed, or to the reason it is not, in `spec/traceability.md`.

Spec files:

| File | Holds |
| :- | :- |
| `spec/learning.md` | The loop, every move, item families, levels, the unseen-question bank, the checkup, dose |
| `spec/experience.md` | Every exchange, all copy, waiting and failure states, the map, first run, accessibility gate |
| `spec/surfaces.md` | Every coding surface, tiers, the parity model, conformance, "your line" per tier |
| `spec/architecture.md` | Engine, record format, sealing, grading interface, cloud sessions, phone, privacy, cost |
| `spec/teams.md` | The codebase guide, shared-repo rules, the admin contract, the team plan |
| `spec/measurement.md` | Metrics, the study, within-person experiments, power, the claims ladder, experiment protocols |
| `spec/traceability.md` | Every judge must-fix item, and where it is handled |

---

## 1. The product in one paragraph, and its name

Firsthand is a free, open-source learning layer for people who build software with any AI coding agent. It installs once, at user scope, into the agents a person already uses (Claude Code, Codex, Cursor, Copilot, Gemini CLI, Devin, Amp, and anything that reads an instruction file and can run a shell command). Most of the time it is silent. At a few natural breaks it asks the user to think first: predict a result, name the cause of a failing test before the agent does, or write one marked line of the real build. Days later it asks again, cold, in a new form, at most 3 times a day. It also offers short drills built from the user's own history: trace code the agent wrote this week, find the defect in a past agent diff, and replay a real bug from the user's repos with the agent off. Every answer is graded against a key fixed before the question was asked, by running code wherever possible. The result is a private map, kept in a git repo on the user's machine, of what the user can now do without the agent. It goes down when they forget. It is measured against questions the teaching agent never saw, and, once a month if the user wants, against a task in a repo they have never seen.

**Name.** Working name: **Firsthand** (command `firsthand`, short alias `fh`). It says what the product measures, what you can do yourself, without naming a lack of aid. The judges rejected "Unaided": two concepts used it, it collided with a level name, and the designer flagged that it may read as stigmatising any aid, including assistive technology. Fallback name: **Ownline**, which points at the anchor feature. Both are [unverified] for trademark, package registry (npm, PyPI, Homebrew), plugin directory and domain availability. "Firsthand" may collide with an existing careers product of that name [unverified]. The name is a founder decision (section 13) and is gated by experiment E0 (section 11).

**The one-sentence promise, checkable in five minutes:** "Install it, and in your first session it gives you one short drill on code your agent wrote this week, graded by running the code; tomorrow, in any agent you use, it remembers what you got right and asks only about what you have not shown yet." A user can check both halves: the drill runs in the first session, and the next day a different agent reads the same record. Vendor learning modes keep no record across sessions [verified: research/users-market.md], and VibeWise, the best-known plugin, asks for your design first and keeps notes in the project, with no spaced review [verified: https://github.com/nykooi1/vibe-wise].

---

## 2. Who it is for, and the wedge

### 2.1 Segments, in order

1. **Engineers in their first years who build with an agent every day.** They feel the pain. In a vendor survey, 85% of juniors said AI improved their understanding, while 16% of seniors said juniors fully understand the AI code they submit (BairesDev Q2 2026, https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/). For them a private record is a feature: they can admit gaps safely.
2. **Experienced engineers moving into a new domain** (new language, new stack, first distributed system). This is closest to the setting of Shen and Tamkin, who studied people learning a new library (https://arxiv.org/html/2601.20245v2). For them the product must never ask about what they know. Cold start (section 4.7) exists for them.
3. **Teams, for revenue.** 38% of engineering leaders say AI cut the mentoring juniors get (https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles). The team product is a codebase guide plus an onboarding report with no individual data (section 7).
4. **Later: courses** that let students use agents. CS50's own tutor still returned code blocks despite instructions (https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/), which is why guardrails live in the engine, not in a prompt.

Out of scope on purpose: hiring. A record used to judge people stops being honest.

### 2.2 The wedge

The wedge is a first-session drill on the user's own code, inside the agent they already use, plus a record that persists across sessions and agents. Concretely:

- On `firsthand init`, the engine scans the repos the user adds (read-only) and the code the agent wrote in the last week (from git history and co-author trailers where present). It builds one trace drill: "Here are 20 lines your agent wrote on Tuesday. What does `merge_windows([(1,3),(2,5)])` return?" It is graded by running the code in a scratch copy.
- Where the yield experiment passes (E2), it can instead offer one replayed bug: a fix commit whose test fails on the parent becomes a diagnosis drill in a scratch worktree.
- The drill runs in the agent's own chat or terminal. There is no separate app to open. The companion concept's separate app was rejected because users skip extra trips (Lehmann 2025, https://arxiv.org/abs/2409.09047; judges product-strategist, designer, target-users).

Activation is defined as an event in the first session: the user attempts the first drill, or the first "your line". Section 9 defines retention.

Distribution is where agents already find extensions: the Claude Code plugin directory, the Codex plugin marketplace, Cursor's plugin listing, skills.sh, the MCP registry, npm, PyPI, Homebrew and GitHub [unverified: directory review rules, research/users-market.md].

---

## 3. Principles

Each principle is a rule the product is tested against. The evidence codes (L1 to L19) are the design rules in `research/learning-science.md` Part A.3.

1. **The build always wins.** No learning moment blocks the agent's next step, except a "your line" the user accepted, and even that is handed back in one word. An unanswered question expires into the review queue. The product never leaves a build, a commit or CI red. Evidence: interruptions raise stress even when people work faster (Mark et al., https://www.ics.uci.edu/~gmark/chi08-mark.pdf); research/experience-design.md P1.
2. **The user thinks first, at a few chosen points.** Predict, diagnose, write the key line, explain. The agent explains after, or when asked. Evidence: Shen and Tamkin's high scorers generated code then checked understanding, or asked conceptual questions (https://arxiv.org/html/2601.20245v2); generation beats reading at about d = 0.40 (https://pubmed.ncbi.nlm.nih.gov/17645161/). L1, L4, L5, L18.
3. **Spend practice where skill erodes, not only where ideas are new.** Debugging and checking agent output erode on ideas the user already knows. Diagnosis practice is offered by the user's debugging level and how much they delegate debugging, not by topic novelty. Evidence: the largest gap in Shen and Tamkin was debugging, and users who let the AI debug iteratively scored 24% (https://www.anthropic.com/research/AI-assistance-coding-skills); monitoring automation is not practice (Bainbridge 1983, https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf). L4, L17.
4. **Only delayed, unaided, new-instance performance counts as skill.** A level never rises in the session where the agent wrote the code. A delayed question about the same function counts as Recalled at most. Evidence: immediate tests measure performance, not learning (Soderstrom and Bjork 2015, https://pubmed.ncbi.nlm.nih.gov/25910388/). L2.
5. **Grade with a key fixed before asking, by running code first.** A model grades only what cannot be run, blind, with quoted spans, and only task types whose agreement with humans has been measured can move a level. Evidence: model grader agreement ranges from near human to kappa 0.295 (research/evidence.md A.2 item 7).
6. **Separate the teaching instrument from the claim instrument.** Practice items tune the product. Human-written unseen questions and the checkup support claims. The teaching agent never sees them. Evidence: Koretz and Beguin's audit items (https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/); research/evidence.md Part G.
7. **No pressure mechanics.** At most 3 due reviews a day, at most one reminder a day at the user's time, a hard daily cap on unprompted moments, no streaks, points, badges or guilt. Evidence: leaderboards and badges lowered motivation and exam scores in a 16-week study (Hanus and Fox 2015, research/learning-science.md A.1 item 9). L14. Founder decisions 3 and 7.
8. **Silent on what you know, and silent when unsure.** If the engine cannot tell whether an idea is new to this user, it says nothing. Evidence: expertise reversal (Kalyuga 2007, https://doi.org/10.1007/s10648-007-9054-3). L10.
9. **One record across every agent, owned by the user, in local git.** Founder decision 1.
10. **Parity of outcome, tested and published per surface.** Every surface can reach every learning outcome in plain text. Richer UI only makes it faster. No surface is called supported until its conformance row passes. Founder decision 6, reframed with evidence in section 5.4.
11. **No new surface unless it names a job no agent surface can do.** v1 has the agent's own chat or terminal and the CLI. Nothing else.
12. **Honest about what it cannot know.** Every grade shows how it was graded, how strongly its key was sealed, and how the answer reached the engine. Every unaided result in a personal tool is self-attested, and the map says so.
13. **Tune on delayed learning and felt cost, never on satisfaction.** People cannot feel learning happen: students rated learning lower where they learned more (Deslauriers 2019, research/learning-science.md A.1 item 2); developers believed AI made them faster when it made them slower (METR 2025, https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/). L3.
14. **Accessible by default, as a release gate.** Plain text first, verdict word first, no tables or box art in learning messages, voice dictation for every answer, no timers. research/experience-design.md section 10.

---

## 4. The learning loop

Full detail: `spec/learning.md`.

### 4.1 Shape

The loop has three layers. All of them run in the agent's own surface.

| Layer | When | Moves |
| :- | :- | :- |
| In the build | At the agent's breakpoints | Predict, Call it, Your line, Explain back |
| Away from the build | Session start (offered, never a gate), the reminder, or when the user asks | Review (3 a day max), Drills (Trace, Check, Replay) |
| Measured | Mixed into reviews, and once a month if the user starts it | Unseen questions, the Checkup |

Rules for every move:

- **Confidence in the same action as the answer:** sure, think so, guess, or don't know. "Don't know" never counts against the user. Sure misses come back sooner and are listed first (L12; Metcalfe, https://doi.org/10.1146/annurev-psych-010416-044022).
- **Predictions are compared, never graded.** The reveal says what happened and where, with no verdict word.
- **"Just tell me" always works.** It answers at once and records that the attempt had help.
- **Every exchange carries a why-now and a one-word skip, and ends with the resume cue** `Back to: <task>. Next: <step>.` (research/experience-design.md P8). Both are conformance checks.

### 4.2 The four moves in the build

| Move | Trigger | User does | Agent does meanwhile | Graded by |
| :- | :- | :- | :- | :- |
| **Predict** | Before a step whose result can be reasoned about, on an idea at Not yet or Seen | One line: what will happen | Runs the step | Compared with the real outcome. Never graded |
| **Call it** | A test fails, and the user's debugging level is low or their recent delegation of debugging is high (4.4) | A cause and the first check they would run | Keeps diagnosing in parallel. Holds back only its conclusion until the user answers, skips, or the agent finishes its own diagnosis | Process: would the first check tell the hypotheses apart, and was it named before the fix. Then whether the cause matched |
| **Your line** | The agent is about to write the one line that carries an idea new to the user | Writes that line | Builds everything around it | The project's tests. Same session caps at Seen |
| **Explain back** | After a step passes, at most once per task the user chose to learn from | Two or three sentences on why it works | Continues | Blind model grader, sealed rubric. Same session caps at Seen |

"Call it" never stalls the agent. This fixes the target users' objection that waiting is a block on the critical path.

### 4.3 Your line

The marker states the goal and names the test. It never describes the computation, or the generation effect is lost.

```
# FIRSTHAND(you): the delay before retry n. Test: test_backoff.py::test_delays. Say "write it" to hand back.
```

- Hint and "write it" are always free. "Write it" hands the line to the agent at once and records "handed back".
- Under pressure signals, on a branch matching the user's quiet patterns (default `hotfix/*`), or when a deploy is failing, an open marker is handed back to the agent before any check can fire.
- The product never blocks a commit or a build. At turn end or commit, an open marker gets one line: "Your line in retry.py:42 is open. Write it, or say 'write it'." The optional team merge check (section 7) applies only to a marker nobody chose to resolve, and its failure message names the one word that clears it.
- Signals tracked: first-try pass rate, and `line.survived` (the user's line still exists at the next commit, and 30 days later). Neither is a level.
- An open line follows the user: any agent's next session in that repo names it first. No timer, ever.
- Who wrote a line is never written to commits, trailers or PRs.

How attribution works per surface is in `spec/surfaces.md` section 5. Because same-session lines cap at Seen, attribution errors cannot inflate a level.

### 4.4 When the engine speaks, and when it stays silent

The engine decides, in code, not the model. Inputs: the breakpoint, the idea tags in the diff, the user's levels, their debugging profile, pressure signals, the quiet settings and the budget.

- **Novelty** gates Predict, Your line and Explain back: only ideas at Not yet or Seen.
- **Debugging profile** gates Call it: the user's debugging level, plus their delegation rate, the share of recent test failures the agent diagnosed with no user hypothesis. A user at Held on idempotency who always lets the agent debug still gets Call it offers.
- **Rapid delegation is not a silencer.** The earlier concept went quiet in "acceleration mode". That is exactly when the user hands work to the agent, the behaviour tied to the lowest scores (judge learning-scientist). Now: when the user is moving fast, the engine asks nothing in the moment, and queues one "later" item from that episode, so it still produces retrieval later.
- **Pressure silences.** Words such as "urgent", "prod is down", "hotfix", a failing deploy, or a branch matching the quiet patterns. The engine offers once: "Save this for later?" On hookless surfaces this depends on the model following the skill, which is stated at install, and the explicit quiet controls always work.
- **Explicit quiet beats guessing:** "quiet for 2h", "quiet today", "quiet in this repo", "quiet on this branch", and `firsthand quiet` in any terminal.

### 4.5 The budget

The budget is defined once, in the record, per user. Two agents or two engines writing to the same record cannot double it.

| Limit | Default | Source |
| :- | :- | :- |
| Due reviews a day | 3, user can lower, never raise past 3 without an explicit setting | Founder decision 3 |
| Reminders a day | At most 1, at a time the user picks, off by default | Founder decision 7 |
| Unprompted in-build moments a day | 3, shown to the user, set by the user | Design default, needs to be measured (E4 felt-cost question) |
| Your line | At most one per task | Founder decision 2 |
| Two skips in a session | End questions for that session, say so once | research/experience-design.md P3 |
| Three ignored reminders in a row | Stop reminders, say so once | research/experience-design.md |
| Setup questions | At most one bundled setup question per repo, and one bundle a day | Judge designer |

### 4.6 Drills away from the build

All drills are opt-in, run in the agent's chat or the terminal, count inside the 3-a-day cap when they are due, and never run in the same week the user met the material.

| Drill | Built from | User does | Graded by | Construct |
| :- | :- | :- | :- | :- |
| **Trace** | Code the agent wrote this week | Predicts an output for a given input | Running the code in a scratch copy | Code reading |
| **Check** | A past agent-written diff. Some later needed a fix commit (a real defect), some did not | Lists defects and severity, or says "clean" | Precision and recall against the sealed list. Clean diffs penalise "always find something" | Checking agent output |
| **Replay** | A fix commit whose test fails on the parent and passes on the fix | In a scratch worktree, agent off: writes a hypothesis and the first check, then fixes | Process first, then the commit's own test | Debugging |
| **Compare** | The same catalog idea met in two projects | Names the shared principle and one difference | Sealed rubric, blind grader | Transfer |

The Check drill uses real history, so nothing is ever seeded into the user's code. A seeded-bug variant exists only inside an engine-created throwaway directory, and is not in v1. Replay ships only if the yield experiment passes (E2). While a replay is set up, the user sees "Checking this bug still reproduces" with an elapsed count and a cancel word. If it does not reproduce, the drill is dropped quietly and a trace drill is offered instead.

After an attempt locks, the user can ask for an explainer built from their own code with `path:line` references. It is never shown first, and viewing it counts as Seen.

Teams can add owner-written "how I debug this" notes, shown after the learner calls the cause, and drills drafted from real postmortems (section 7).

### 4.7 Cold start

A new record must not treat every idea as new. Three mechanisms, all in v1:

1. **Inference from the user's own history.** In repos the user adds, commits authored by the user's email with no agent co-author trailer, before a date the user may set, mark the ideas they contain as "likely known". Likely-known ideas are silent. They carry no level. Whether this inference is accurate needs to be measured (E11).
2. **"I know X".** One probe question. Right, and the idea cluster goes silent in every project. Wrong, and it becomes a normal idea.
3. **A gentle first week.** The unprompted-moment cap starts at the low end, and "your line" is offered only for ideas the inference marked new with no prior authorship. This keeps decision 2 on while protecting seniors. (The target users asked for the Light dial in week one; Light turns "your line" off, which would contradict decision 2, so this is the narrower version.)

### 4.8 The dial

Four positions: **Off, Light, Standard (default), Deep.** Plus per-task phrases any agent understands: "just build" and "teach me this one". Light gives reviews and explain-back only. Standard runs all moves within the budget. Deep adds predictions, and "your line" grows from a line into a function into a design as the level rises (L5).

### 4.9 Levels: one vocabulary everywhere

| Level | Earned by | Can be earned in the session where the agent wrote the code? |
| :- | :- | :- |
| **Not yet** | Default, or a miss on a delayed item | n/a |
| **Seen** | Explained back, wrote "your line", answered with help, or self-marked | Yes |
| **Recalled** | Right on a sealed item at least a few days later, no help shown first. A question on the same code the user saw before caps here | No |
| **Applied** | Right on a new instance from the idea's item family, with a recorded surface distance and the topic name hidden | No |
| **Held** | Applied again at a longer gap, including at least one unseen question, from at least two different item sources | No |

Gap lengths start from the current engine (`DURABLE_AFTER_DAYS = 7`, `skills/learning-while-building/scripts/record.py`) and need to be measured. The best level shows next to the latest. Levels go down.

Every grade carries three labels, shown next to the level in plain words:

- **How it was graded:** by tests, by a model, by two models that disagreed (uncertain), by a person, proctored, or self-marked.
- **How the key was sealed:** in a separate context, or in the asking context (weaker).
- **How the answer arrived:** typed by you into the engine, captured from your prompt by a hook, or relayed by the agent.

Caps: a self-marked grade, an asking-context seal, or an agent-relayed answer caps the item at Seen. Grades from a task type below human-human agreement cannot move a level. A disagreement between two graders shows both readings and does not move the level. Only proctored live checks are evidence for anyone else.

The six constructs (code reading, debugging, design judgment, explaining a change, transfer, calibration) stay separate in the data and are never combined into one score (research/evidence.md B.1).

### 4.10 Field evidence

`firsthand field <commit or PR> "what I did"` logs an unaided fix, design or incident handled without the agent. The engine checks that the commit exists, is authored by the user, and has no agent co-author trailer. Field evidence shows in its own list on the map. Linked field evidence can be one of the two sources that Held needs. It is within-person and never leaves the record.

### 4.11 Dose

The judges asked what the default dial actually delivers. The design targets for a user who builds daily on Standard are below. All are design targets, not findings, and E1 measures the real numbers.

| Rep kind | Design target per week | Ceiling set by |
| :- | :- | :- |
| Retrieval (reviews, unseen questions) | Up to 21 | 3 a day (decision 3) |
| Generation in the build (predict, your line, explain back) | Up to 21 | 3 unprompted moments a day |
| Diagnosis (Call it, Replay) | Every eligible test failure, plus opt-in Replay when due | Debugging profile, review cap |
| Checking agent output (Check drills) | Opt-in, when due | Review cap |

Rule: if E1 shows the dose does not move delayed, unaided outcomes, the product raises practice through drills the user starts, never through more interruptions.

---

## 5. The experience end to end, and the parity model

Full detail: `spec/experience.md` (all copy and states) and `spec/surfaces.md` (every surface).

### 5.1 First install

```
npx firsthand init        (or: uvx firsthand init, brew install firsthand)
```

`init` installs at user scope: the user-level skill folder and instruction file for each agent it finds, the MCP server, and hooks where the agent supports them. It never touches a project's AGENTS.md, CLAUDE.md or skills folder without a per-repo yes. Nothing appears in a team repo's `git status`.

It says, in plain lines:

1. Where the record lives (`~/.firsthand/record`, a git repo, no remote) and that nothing leaves the machine.
2. Which agents it found, and for each, what that surface can do. For example: "Copilot in JetBrains: no hooks. Breaks rely on the agent following instructions and may be missed."
3. Three questions with defaults: dial (Standard), reminder (off, or a time), which repos to read for drills and cold start (none by default).
4. One offer: "Want a 2-minute drill on code your agent wrote this week? Say yes, or later."

If the install is on a work machine set up by an admin, one more line: "Your employer cannot see your record, your levels, your skips, or whether you use this. There is no key that allows it."

### 5.2 One exchange, full form then faded

First three exchanges:

```
New idea: retries with a payment API. Why now: this test runs it. Say "skip" to skip.
If the first two calls time out and the third succeeds, how many charges does the provider see?
Answer, then: sure, think so, guess, or don't know.
```

After three, the header fades to one clause: `Retries, since this test runs it (skip ok):` then the question.

The prediction reveal, with no verdict word:

```
What happened: the provider saw 3 charges.
You expected: 1.
The gap: client.py:42 builds a new request on each retry, with no idempotency key.
This comes back in 2 days.
Back to: add retries. Next: add the idempotency key.
```

A graded answer leads with the verdict word (Correct, Partly, Not yet), then what was right as information, the missing piece at `path:line`, when it returns, how it was graded, and the resume cue.

### 5.3 A normal day, a week, a project

- **Session start.** After the user's first prompt has been handled, one ignorable line: "2 reviews due, about 2 minutes. Say 'review' now, or later." Later is the default. It never appears before the first prompt is handled.
- **In the build.** Maybe one prediction and one explain back on new ideas, and one Call it on a failing test if the debugging profile says so. On known ideas, nothing.
- **Pressure.** "prod is down": silence, and one offer to save it for later.
- **Evening.** If the user set a reminder: one calendar alert at their time, with no content. It cannot know whether anything is due, and says so in settings.
- **A week later.** Reviews interleave easily confused ideas with the topic name hidden (L9). "I think that grade is wrong" triggers one regrade against the same key, and both readings show.
- **After a gap.** At most 3 reviews, the rest spread out, no backlog count.
- **End of a project.** `firsthand wrap` writes a factual summary to the record and offers compare items for the next project. `firsthand export` writes a proof pack of items the user chooses, labelled self-graded.
- **Once a month, if the user starts it.** The Checkup (section 9.2).

### 5.4 The parity model, and a challenge to founder decision 6

**Challenge, stated explicitly.** Decision 6 asks for feature parity on all coding surfaces. Parity of mechanism is impossible on the evidence: Aider has no MCP and no hooks [verified: https://aider.chat/docs/config/options.html]; Copilot cloud agent supports MCP tools only and has no live user in the loop [verified: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp]; Copilot in Visual Studio, JetBrains, Eclipse and Xcode has no hooks [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet]; Zed's agent and Gemini CLI have no elicitation [verified: https://zed.dev/docs/ai/mcp, https://geminicli.com/docs/tools/mcp-server/]; Claude Code does not render MCP Apps [verified: research/surfaces.md]. All four concepts and all five judges reached the same conclusion.

**What we commit to instead: parity of outcome, as a tested promise per surface.** Every learning outcome (be asked at a break, answer with confidence, get graded, write your line, review, see the map, have it all land in the one record) is reachable on every surface in plain text plus a CLI call. Richer tiers make it faster, never different. Grading is part of parity: the same rubric format, the same blind grading step, and the grader version recorded everywhere (research/evidence.md Part L).

Each surface has a public support level:

| Level | Meaning |
| :- | :- |
| **Tested** | Its conformance row passes the threshold over repeated runs in this release |
| **Floor, untested** | The plain-text floor should work; no conformance run yet. Shown as untested, never as supported |
| **Known gap** | A named outcome fails or is weaker; the gap is listed |

The tiers, from `research/surfaces.md` section 8:

| Tier | Mechanism | Adds |
| :- | :- | :- |
| T0 | Instruction file, skill folder, shell | The whole loop as chat replies and `firsthand` commands |
| T1 | MCP tools | The agent calls the engine without shell quoting |
| T2 | Hooks | Breakpoints arrive without relying on the model, prompts are captured verbatim, pressure is read by the engine |
| T3 | Native ask (MCP or ACP elicitation, question cards) | Answer and confidence in one form, typed straight to the engine |
| T4 | Designed UI (MCP Apps, plugin UI) | Map and cards inline |
| T5 | Away from the keyboard | Reviews on the phone through the vendor's app |

Where each surface sits, with every "?" from the research marked as an experiment:

| Surface | Highest tier | v1 support target | Notes |
| :- | :- | :- | :- |
| Claude Code CLI, desktop, IDE | T3, T5 via Remote Control | Tested adapter | [verified: research/surfaces.md 8.7] |
| Claude Code web and phone | T3 cards, cloud | Tested adapter | VM reclaimed [verified: https://code.claude.com/docs/en/claude-code-on-the-web.md] |
| Codex CLI and app | T3, T5 via ChatGPT mobile | Tested adapter | Hooks [verified: https://learn.chatgpt.com/docs/hooks] |
| Codex cloud | T0, skills and MCP "?" | Floor, untested | Containers cached up to 12 hours [verified: https://developers.openai.com/codex/cloud/environments] |
| Cursor IDE | T4 | Tested adapter | Hooks, elicitation, MCP Apps [verified: https://cursor.com/docs/agent/hooks] |
| Cursor cloud agents | T2, several "?" | Floor, untested | |
| VS Code Copilot, Copilot CLI | T4 (VS Code), T2 (CLI) | v1.1 adapter | Hooks in preview [verified: research/surfaces.md] |
| Copilot in VS, JetBrains, Eclipse, Xcode | T1 | Floor, untested, known gap: no hooks | |
| Copilot cloud agent | T1 tools only, no live user | Known gap: no in-the-moment questions; your line via PR body | 59-minute sessions [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent] |
| Gemini CLI | T2 | v1.1 adapter | No elicitation |
| Devin Desktop and CLI (formerly Windsurf, per press [unverified]) | T2 | v2 adapter | Hooks [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] |
| Amp, OpenCode, Kiro, Cline | T2 or higher | v2 adapters | [verified: research/surfaces.md] |
| Roo, goose, Junie, Zed agent, ACP agents | T1 to T3 | Floor, untested | |
| Aider | T0 | Floor, untested | The pure floor case |

### 5.5 Moving between surfaces

One event has one identity and one state wherever it is shown. The record is the source of truth. Open lines and due reviews follow the user into whichever agent they open next. Answers given on the phone through a vendor app arrive in the record at the next local session, with one summary line.

---

## 6. Architecture

Full detail: `spec/architecture.md`.

### 6.1 Shape

```
any coding agent
   |  user-level instruction file (3 lines), skill folder, MCP tools, hooks
   v
firsthand engine (on the user's computer)
   |-- CLI            firsthand review | drill | map | quiet | field | check | export
   |-- MCP server     stdio, tools only for the core, both MCP revisions
   |-- hook dispatch  firsthand hook <agent> <event>
   |-- miner          read-only scan of added repos; builds drills in scratch dirs
   |-- grader         pluggable providers, run off the critical path
   v
record: ~/.firsthand/record   (git, append-only events, signed commits)
   +-- optional, only if the user asks: their own private git remote
   +-- optional, v2, paid: end-to-end encrypted relay
```

All learning logic lives in the engine: state, sealing, scheduling, the budget, quiet rules, "your line" checks. Adapters only translate event names and output shapes, generated from one manifest.

Language: v1 keeps Python, so `record.py` and `learning.py` carry over, shipped through `uvx` and `pipx`, with an npm shim. A static binary is a later option (section 13).

### 6.2 The record

- A per-user git repo outside any project tree. One JSON file per event, ULID names, so two devices only ever add different files and a union merge never conflicts on content [verified: research/platform.md]. Three conflict rules: earliest lock wins, last config write wins per key, the budget is per user.
- Everything else (schedule, map, due list) is derived, never committed, and rebuilt from events.
- Code is never stored by default. Events hold project ids, commit hashes, paths and the user's own words. Excerpts are opt-in per project and pass a secret scan first.
- Every event has a format version and namespaced extension fields (`x.<reverse-domain>`). The format is published as a documented spec so the record outlives the product. It is not a governed standard until a second implementer exists.
- Commits are signed with a per-device key generated at init. SSH commit signing needs a recent Git [unverified: Git 2.34 or later, from memory; check]. If signing is unavailable the engine keeps an unsigned per-device hash chain and says so once.
- `firsthand export`, `forget <idea>` and `delete` give the user full control, with a history rewrite they confirm.

### 6.3 Sealing

- Each answer key's sha256 is committed before the question is shown. The engine refuses to release a key until an `answer.locked` event exists. `firsthand check` verifies hashes after reveal.
- Keys are written in a separate context where the surface has one (a subagent, or a separate engine-run process). Elsewhere the key is written in the asking context, sealed before asking, and labelled weaker. Those items cap at Seen.
- Stated limit: an agent with the code can always rebuild an answer. Sealing protects against a lenient grader that adapts the key to the answer. It does not protect a third party from the user.

### 6.4 The unseen-question bank

The audit bank, called "unseen questions" in the product.

- Written by people: engineers contracted to write item families per catalog idea, with transfer items, surface variants and recorded distances. Never generated from the user's code by the teaching agent. Cost needs to be measured.
- Ships sealed in the package, each item encrypted with `age`, decrypted only inside the engine process at display time.
- Served only where the engine renders straight to the user: `firsthand review` in a terminal, or a native ask form where it is verified that the content does not enter the model's context [unverified per host]. Never on text-only surfaces through the agent.
- Mixed into reviews within the 3-a-day cap. The share of slots needs to be measured.
- Reported with item counts and an uncertainty band. Below a minimum count the map says "too few answers to tell". The minimum needs to be measured.

### 6.5 Grading interface

The grader is pluggable. Providers in order:

1. **Executable:** run the code, the test, or the user's check. Immediate.
2. **A separate context in the user's agent:** a subagent where the surface has one.
3. **The user's agent headless,** as a separate process (Claude Code `-p`, Codex `exec`, Gemini CLI non-interactive, Copilot CLI [verified: research/surfaces.md 10.6]). Opt-in, because it spends the user's plan.
4. **A user-supplied API key.**
5. **Self-marked** against the sealed binary points after reveal. Caps at Seen.

Rules: blind four-field input (prompt, sealed rubric, excerpt shown, answer marked as data); no quote, no point; graded twice with points shuffled, disagreement marks the grade uncertain; an echo flag when the answer copies the agent's words; one free regrade. Model grading runs off the critical path, batched at session end or review time. Per-surface support for each provider, its cost, auth and terms are [unverified] until E8. In cloud sandboxes where nested agent calls are impossible, open answers wait for the next local session.

**Cost is visible.** `firsthand cost` shows model calls, tokens where the agent reports them, and time added this week. The user sets a weekly budget. The engine never spends the plan without consent.

### 6.6 The idea catalog

An open, versioned catalog of engineering ideas with stable IDs (for example `concurrency/idempotency-key`), short definitions, aliases and known confusions. It makes silence across projects, interleaving and compare items possible.

Drift handling, designed before relying on it:

- The engine proposes a fixed candidate list per diff (matched by language, files and catalog keywords). The agent picks from that list; it never invents free-form tags.
- Tags carry a confidence. Aliases and `topic.merged` events join ideas without rewriting history.
- If tags disagree or are missing, the engine stays silent rather than guessing.
- Once a probe passes on any alias in a cluster, the whole cluster is silent. A known idea is never asked twice because agents disagree about tags.
- Codebase-specific ideas from a team guide live in a separate namespace and show separately on the map.
- The tag agreement test (E3) runs before v1 depends on cross-agent silence.

### 6.7 Cloud sessions

Cloud agent disks do not survive. Decision 1 keeps the record local with no remote unless asked. Clarification, with evidence (Claude Code web VMs are reclaimed, Codex containers last up to 12 hours, Copilot cloud sessions end at 59 minutes, sources in 5.4): without a way out, cloud answers are lost.

- **Default: no write to any project branch.** The engine keeps today's attempts in memory.
- **Once per repo, one confirmation** (decision 4 used for the same reason): "Keep today's answers? Yes: they travel encrypted to your key on a side branch `firsthand-carry/<random>`, never merged; your computer imports it and deletes the branch. No: they are kept only until this session ends." This option is not offered in public repos. The engine ships a CI check that refuses any merge containing a carry file.
- **If the user has a private record remote or (v2) the relay,** it is used automatically with no question.
- **Fallback:** at session end, a one-line `firsthand import <blob>` the user can paste at home.
- The first cloud run says plainly which of these will happen.

This departs from `research/platform.md`, which said never to use a branch. The designer's must-fix (no silent loss, at most one confirmation) and the staff engineer's (encrypted, merge-blocked) are both met only this way. The founder must accept it (section 13).

### 6.8 Phone

- **v1:** the vendor phone apps (the Claude app Code tab, ChatGPT mobile for Codex, Cursor iOS and web [verified: research/surfaces.md section 7]), where reviews arrive inside a normal session, plus a content-less recurring calendar event created by `firsthand reminder set 18:30`. The event says "Review time" and cannot know whether anything is due.
- **v2:** the device link (QR pairing, sealed packs with no keys, encrypted answers back), only after a working one-tap pairing has been demonstrated (E12). An http LAN origin will not get a service worker [unverified for every browser], so the prototype must solve secure context first. Choice and number cards grade on the phone after the answer locks; open answers say "graded when you next sync".
- **v2, paid:** the relay adds web push for the one reminder, which needs a sender server [verified: https://webkit.org/blog/16535/meet-declarative-web-push/].

### 6.9 Privacy

Default: nothing leaves the machine. No account. No network call the user did not cause.

| Choice | What travels | Who can read it |
| :- | :- | :- |
| Private git remote | The record | Whoever the user's host allows |
| Carry branch (cloud, private repos) | New attempts, encrypted | Only the user's devices; collaborators see a branch name and ciphertext |
| Relay (v2, paid) | Ciphertext | Only the user's devices; a published list says what the relay sees (sizes, times, IPs), as Obsidian does [verified: https://obsidian.md/help/sync/security] |
| Proof pack | Items the user picks | Whoever the user gives it to |
| Team sharing (later) | Counts the user opts in to, above a group floor | The team lead |
| Design-partner stats | Pasted `firsthand stats` output | The product team |

Telemetry is off by default. There is no Prio3 or DAP in v1 or v2: it needs two independent, non-colluding aggregator operators [verified: https://datatracker.ietf.org/doc/draft-ietf-ppm-dap/], which a small company cannot credibly provide. Cryptography uses maintained libraries (age, libsodium), never custom code.

---

## 7. Teams

Full detail: `spec/teams.md`. Teams come after the individual loop shows retention.

- **The codebase guide (v2, free).** Plain files in `.firsthand/guide/` in the repo, committed only if the team chooses. `firsthand guide draft` reads the repo and proposes ideas with paths. Seniors edit, they do not author from scratch. Each idea can carry an owner's "how I debug this" note, shown only after the learner's own attempt, and nominated "lines worth writing by hand once". `firsthand drill from <postmortem>` drafts a rehearsal with the real resolution sealed. `firsthand handover <area>` drafts guide entries when someone rotates off. No personal data is ever in the guide.
- **Shared-repo rules (v1, because they protect individuals).** No readable learning data in any branch. The optional merge check refuses an open your-line marker only if no one chose to resolve it, and names the word that clears it. Who wrote a line is never visible.
- **Optional PR walkthrough.** The author writes a short walkthrough for reviewers. It is graded privately as an explain-back. Reviewers see plain text, never a grade.
- **The admin contract.** `firsthand team install` deploys and turns nothing on. Admins can set defaults, require a relay, and turn excerpts off. Admins can never read records, turn telemetry or sharing on for anyone, raise the review cap above 3, lower the group floor, or see who uses the tool. There is no admin key. The product says this inside the product at the moment of a work install.
- **The team report (later, paid).** Opt-in counts, shown only above a group floor (Viva Insights' floor cannot go below five [verified: https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings]; ours starts at 8, a design default). It shows guide coverage and onboarding outcomes. It is never sold as a skill measure until a power check shows it can detect a change at the group floor. Codebase-specific ideas are reported apart from transferable engineering ideas, so local recall is never reported as engineering skill.

---

## 8. Business model and distribution

Full detail: `spec/teams.md` section 6.

| Offer | Who pays | Adds | Price |
| :- | :- | :- | :- |
| Firsthand | No one, forever | Engine, every move, drills, map, every adapter, the guide | Free, open source |
| Firsthand Sync (v2) | Individuals | Encrypted relay across computers, cloud sessions without the carry branch, phone push and device link without the computer awake | Needs to be measured |
| Firsthand Team (later) | Companies, per seat | Private guide catalog entries, sealed guide items through the relay, the team report, SSO and SCIM, region-pinned or self-hosted relay | Needs to be measured |
| Firsthand Education (later) | Courses | Course catalogs, opt-in class reports, proctored live checks | Needs to be measured |

The planned revenue line is Team. Individual Sync is thin: juniors' price expectation for "the AI asks me questions" is near zero, because free learning modes exist (research/users-market.md section 3.1). Budgets for developer learning tools do exist (Pluralsight and CodeRabbit price ranges in research/users-market.md are [unverified]).

Before any team-plane code: manager interviews, and a "talk to us about teams" button on the existing site at https://0xfauzi.github.io/explain-pr/, counting clicks against visits (E9).

Ruled out: selling records, ads, hiring use, paid streak repair or any paid pressure mechanic.

**Why a vendor toggle does not end the business.** Vendors ship learning modes (Claude Code's Learning output style leaves `TODO(human)` gaps [verified: https://code.claude.com/docs/en/output-styles]; ChatGPT Study Mode [verified: https://techcrunch.com/2025/07/29/openai-launches-study-mode-in-chatgpt]). Firsthand reads vendor `TODO(human)` gaps as your-line events, so vendor modes feed the record. The defensible parts are the ones one vendor has weak reasons to build: one record across rival agents, drills from your own history, an honest measure that could show a vendor's own agent eroding skill, and a record the user owns.

**Migration of current users.** `firsthand import-lwb` reads an existing `.learning/` record from `skills/learning-while-building`, writes events with provenance "imported, before sealing", and caps imported levels at Recalled (the old records have no item families or distances). It then offers to remove `.learning/` from the project repo, since the new record lives outside project trees. The current skill keeps working until the user migrates, and its SKILL.md becomes the T0 skill for the new engine.

---

## 9. Measuring that it works

Full detail: `spec/measurement.md`.

### 9.1 The primary outcome is transfer

The claim the product wants to earn: people who build with it can do more without the agent, weeks later, on problems they have not practised, than comparable people using the same agent without it, with no meaningful loss of speed (research/evidence.md A.1).

| Kind | Indicator | Role |
| :- | :- | :- |
| Lagging, primary | G2: a task in an unfamiliar real repo pinned to a commit, needing ideas the user met elsewhere, no topic names, graded by tests plus blind human review | Supports claims |
| Lagging | G1: held-out unaided battery from unseen questions; G3: seeded-bug localisation in an unfamiliar repo; G4: defect finding in agent diffs that include clean ones | Supports claims |
| Leading | Delayed unaided recall, retention curve, calibration, your-line first-try rate, hint depth, the unseen-question gap | Tunes the product. Never marketed as "better engineer" |
| Product | Activation (first drill or first your-line attempted in the first session); share of offered moments answered; share of due reviews done; 14-day and 30-day return | Tunes the product |
| Guard | Task time on versus off, with a margin set in advance; skip and "just build" rate; reminder dismissals; model cost per week; measurement invariance across surfaces | Must not get worse past the margin |

### 9.2 The Checkup

The Checkup turns G2 to G4 into something a user can take. Once a month, only if the user starts it, never due, never reminded: one small task in a real public repo the user has never opened, pinned to a commit, cloned into a throwaway directory, with no topic names, graded by tests; plus one seeded bug to localise in that throwaway copy; plus two diffs to check, one of them clean. Checkup tasks are written by people, sealed, and never used for practice. The result shows on the map as its own line. Checkup tasks are the only course-like content in the product, and they exist to measure, not to teach.

### 9.3 Within-person experiments, done right

- Randomise at the level of idea clusters from the catalog, so related ideas do not contaminate each other.
- Have sealed delayed items of equal quality ready for both arms, from the unseen-question bank, before assignment.
- Never show the condition on the card.
- Results are computed on the device and shown to the user in `firsthand stats`.
- Sample size: unknown until effect sizes are measured. Lehr's rule gives about 16 divided by the squared standardised effect per arm (research/evidence.md J.3); for illustration only, d = 0.5 gives about 64 per arm. Within-person designs need fewer people, by an amount that depends on the correlation between a person's clusters, which E7 measures. No claim is made before a power calculation from pilot data.

### 9.4 The study before any efficacy claim

A preregistered randomised two-arm study (product on versus off, same agents), across at least two agents and two surfaces, over several weeks of real building, with G1 at a fixed delay as the primary outcome, G2 to G4 secondary, task time as the guard, two blind human graders, and ideally independent researchers (research/evidence.md K.1).

### 9.5 Claims ladder

| Evidence in hand | Allowed claim |
| :- | :- |
| Research only | "Designed around research on how people learn with AI." No efficacy claim |
| On-device results | "Shows you which moves help you, measured on you." |
| The study, positive on G1 | The specific result, effect size and link |
| Independent replication with G2 to G4 | "People who use it become better engineers," with scope stated |

`docs/index.html` is checked against this ladder before each release. The current site is checked first, in v0.

---

## 10. Roadmap

All sizes are rough estimates in engineer-weeks for a small team, marked "est.". They are planning guesses, not measurements.

### v0: experiments on the existing skill (est. 4 to 6 weeks)

Run E0 to E5, E8, E9 and E11 (section 11) on the current `learning-while-building` skill and on scripts, before the engine is rewritten. Fix the site's claims against the ladder.

### v1: the smallest thing that is still the product (est. 16 to 24 weeks)

- Engine with CLI, MCP server (tools only), hook dispatcher, record, sealing, the grading interface with all five providers, cost meter. Est. 6 to 8.
- The four build moves, the budget, the dial, quiet controls, pressure silence, cold start. Est. 3 to 4.
- Trace and Check drills; Replay only if E2 passes, limited to the languages that passed. Est. 3 to 5.
- Seed idea catalog with drift handling; a first unseen-question bank for a small set of ideas, human-written. Est. 2 to 3 engineering, plus authoring cost that needs to be measured.
- Tested adapters for Claude Code, Codex and Cursor. The T0 skill and user-level instruction file for every other agent, shown as "Floor, untested". Est. 2 to 3.
- Cloud carry branch and its CI check, for Claude Code web and Codex cloud. Est. 1 to 2.
- Text map, `stats`, `cost`, `export`, `field`, migration from the old skill, the accessibility gate, the public conformance table. Est. 2 to 3.

Not in v1: any local page, the device link, the relay, Spot with seeded bugs in user code, the team plane, packs, transcript importers.

### v1.1 (est. 4 to 6 weeks)

Tested adapters for VS Code Copilot, Copilot CLI and Gemini CLI. Within-person experiments on by default for new idea clusters.

### v2 (est. 20 to 30 weeks)

Adapters for Devin, Amp, OpenCode, Kiro and Cline; the codebase guide and its commands; the device link (if E12 passes); Firsthand Sync (relay, push); MCP App cards where hosts render them; the Room local page, only if research shows the text map is not enough; the Checkup at full size; compare items across projects.

### Later

Firsthand Team (report, SSO, SCIM) after manager interviews and the pay test; Education; proctored live checks; a native phone app with local notifications; a seeded-bug variant of Check, only in throwaway directories; a static binary engine; proposing the record format to a neutral steward if a second implementer appears.

---

## 11. Experiments to run first

Full protocols: `spec/measurement.md` section 6. Thresholds are decisions, not findings, and the founder can change them before a run starts, never after.

| # | Question | Method | Pass rule |
| :- | :- | :- | :- |
| E0 | Is the name usable and does it land well? | Trademark, registry, directory and domain checks for Firsthand and Ownline; 8 short user interviews, including disabled developers | No blocking conflict in software classes; packages available; no more than 1 of 8 reads the name negatively. Else use the fallback |
| E1 | Do people answer, and what dose do they get? | Design-partner cohort, 20 users, 3 weeks, current skill with the v1 budget rules; users paste `stats` weekly | At least half of offered moments answered and at least half of due reviews done in week 3; dose per rep kind reported. Fail: rework the moments before the engine |
| E2 | How many real bugs can be replayed? | Run the miner script over the founder's repos and 30 public repos in at least 4 languages | At least 2 reproducible drills per 100 commits in a language, median setup under 2 minutes, under half needing external services. Replay ships only for languages that pass |
| E3 | Do agents tag ideas consistently? | 30 real diffs, three agents, tag from a fixed candidate list | Fleiss kappa of at least 0.6. Fail: silence stays per project, cross-agent silence waits |
| E4 | Does the engine pick moments as well as a person? | Wizard of Oz, 5 users; a person picks moments from transcripts; compare with the engine rules; felt-cost question at session end | Engine and person agree on at least 70% of moments; median felt cost "a little" or less. Sets the moment cap default |
| E5 | Does the model grader agree with people? | 200 answers per task type, two trained humans and the grader | Model-human kappa within 0.1 of human-human kappa. Fail: that task type cannot move levels |
| E6 | Does the floor work on weak tiers? | Conformance script on Copilot in JetBrains, Gemini CLI, Aider, Copilot cloud agent, 10 runs each | Each outcome passes in at least 8 of 10 runs, else the row shows a known gap |
| E7 | Pilot of within-person randomisation | 10 users, 3 weeks, cluster-level assignment, day-21 unseen questions | At least 80% of delayed items taken; gives the correlation estimate for the power calculation. No effect claim |
| E8 | What does grading cost, and where can it run? | Headless grading on each v1 agent, 50 items | Cost and quota per week reported per agent; each provider marked available or not; no surprise spend |
| E9 | Will teams pay? | 10 manager interviews; a "talk to us" button on the site | Threshold set by the founder before the test. No team-plane code before it passes |
| E10 | Will people accept the cloud carry branch? | 10 cloud users, prompt shown once | At least 7 of 10 say yes or choose their own remote. Fail: default to the import line |
| E11 | Does cold-start inference spare seniors? | 10 seniors add repos; compare inferred known ideas with a probe on each | At least 80% of inferred-known ideas pass the probe |
| E12 | Can the phone pair in one tap? | Prototype device link on iOS and Android | Pairing with at most one confirmation tap on both. Device link ships only then |

---

## 12. Risks

| Risk | Why it matters | Mitigation |
| :- | :- | :- |
| The loop does not make people better unaided weeks later | The founding study measured immediately, with 52 people (https://arxiv.org/html/2601.20245v2) | E7, then the study; claims ladder; raise practice through drills, not interruptions |
| Users skip everything | People prefer substitution and overrate AI help (Lehmann 2025) | E1 before the engine; dial; drills that show value in session one |
| Moments cost flow | Interruptions raise stress (Mark et al.) | Breakpoints only, non-blocking Call it, hard cap, quiet controls, E4 |
| Tag drift breaks silence and nags seniors | The calm promise rests on it | Fixed candidate list, silence when unsure, cluster silence after a probe, E3 |
| Replay yield is low | Old commits often do not build | E2 gates it; Trace and Check carry the wedge |
| Model graders disagree with people | Kappa as low as 0.295 has been reported | Executable first, agreement gate per task type, E5 |
| Self-attested "agent off" inflates the record | The agent is one tab away | Held needs two sources including unseen questions; the map says results are self-attested; only proctored checks count for others |
| Headless grading burns the user's plan or breaks terms | Each vendor differs [unverified] | Opt-in, visible cost, budget, E8 |
| A vendor ships the same thing free | Vendors already ship learning modes | Cross-agent record, own-history drills, honest measure, read vendor gaps as input |
| Team use feels like surveillance | Employer-installed tools get distrust | No admin key, nothing on by default, said in the product at install, no individual data ever |
| Name collision or a name that reads badly | Search and trust | E0, fallback name |
| A cloud carry branch leaks usage | Collaborators see that a branch exists | Not offered in public repos; disclosed in the prompt; own remote or import line instead |
| EU AI Act may class learning-outcome grading or worker evaluation as high-risk [unverified, secondary: https://casrai.org/news/ai-act-high-risk-classification] | A team or education plan could be regulated | Evaluation stays in the user's hands; legal review before Team and Education |
| Scope creep | Every concept's v1 was too big | v1 is cut to three tested adapters and text only |

---

## 13. Decisions only the founder can make

1. **The name.** Firsthand, Ownline, or another, after E0.
2. **Accept parity of outcome** (section 5.4) as the meaning of decision 6, with a public per-surface support table, and accept that v1 tests three agents and labels the rest "Floor, untested".
3. **Accept the cloud carry branch** (section 6.7) as an exception to decision 1 and to `research/platform.md`, or choose the import line as the cloud default and accept that some answers will be lost.
4. **Fund the human-written unseen-question bank and Checkup tasks.** Without them the product has no independent measure. Cost needs to be measured.
5. **Pass thresholds** for every experiment in section 11, fixed before each run.
6. **Revenue path:** whether to plan for Team as the revenue line and run E9, and the prices after it.
7. **Publish the record format as a documented spec at v1,** or later.
8. **The default moment cap** after E4, and whether a first-week Light dial is wanted despite turning "your line" off.
9. **Licence** for the engine, catalog and unseen-question bank (the bank cannot be fully open without losing its purpose).
10. **Who runs the efficacy study,** and whether to seek independent researchers.
11. **Engine language** for v1 (Python, as recommended) and whether to fund a static binary later.
12. **The future of the claude.ai artifact Room** from the earlier design: keep as an optional adapter, or retire.

Founder decisions 2, 3, 4, 5 and 7 are accepted as written. Decision 5 means no UI the product draws registers letter shortcuts unless the user turns them on, and even then no single letter writes to the record.

---

## 14. What changes from the earlier design, and what is kept

The earlier round (`design/learning-experience/`) was designed for one person using Claude Code and a claude.ai artifact as the Room.

**Kept:**

- The order of who thinks first: predict, explain back, your line, reviews with confidence, comparison not grading for predictions.
- The resume cue `Back to: <task>. Next: <step>.` on every exchange.
- Levels change only at delayed reviews; best and latest levels both shown; levels go down.
- The record as one file per event in git, union-merged.
- The engine code in `record.py` and `learning.py`, its interval ladder (3, 7, 21, 60, 180 days) and seven-day durability gap, as starting values to be measured.
- The accessibility work on the Room (`design-system.md` section 4, `critique/accessibility.md`), applied to v2 if the Room returns.
- The fix that the key must not reach any page before the answer is locked.

**Changed:**

| Earlier | Now | Why |
| :- | :- | :- |
| One person, Claude Code, claude.ai Room | Any agent, user-scope install, text first | Founder decision 6; research/surfaces.md |
| The Room as the main place to answer | No page in v1; the agent's own surface is the place | Users skip extra trips; judge designer and target users |
| Record in `.learning/` in the project repo | `~/.firsthand/record`, outside every project | Project branches leak misses to reviewers (research/platform.md) |
| Model writes key and grades in the same context | Separate context where possible, sealing strength shown, executable first, agreement gate | research/evidence.md Part D |
| Levels: not yet, with help, recalls, transfers | Not yet, Seen, Recalled, Applied, Held; three provenance labels on every grade | One vocabulary; item families and distance (evidence C.2) |
| Practice set only by the agent from this repo | Item families, human-written unseen questions, the Checkup in an unfamiliar repo | Teaching and claim instruments must be separate (evidence Part G) |
| Debugging drills on injected bugs in the user's code | Check drills on real past agent diffs; Replay of real bugs; seeding only in throwaway copies of other repos | Trust; judge target users |
| Diagnosis offered when the idea is new | Offered by debugging level and delegation rate | Judge learning-scientist |
| Phone through lwb Sync | v1: vendor apps and a content-less calendar event; v2: device link after E12 | Secure-context limits; judge staff engineer |
| Quiet when the user moves fast | Ask nothing then, queue a later item | Judge learning-scientist |
| Name `lwb` | Firsthand (working) | Crowded namespace (research/users-market.md) |
