# Firsthand: product specification

Status: revised after three red-team reviews (privacy and security, market, efficacy), 7 November 2026. Every critical and major item is fixed or listed in section 15 with the reason. Nothing is built yet, except the existing skill in `skills/learning-while-building/`.

How to read this:

- Detail lives in `spec/`. This file is the whole product in short form. Each section links to the spec file that holds the rest.
- Claims about a product or harness carry [verified: source] or [unverified]. "[verified: research/x.md]" means the claim is verified, with its URL, in that report.
- No number here is invented. A number with no source is either a design default (marked "design default, needs to be measured") or a pass threshold for an experiment (marked "threshold, a decision").
- Every judge must-fix item and every red-team item is traced to where it is handled, in `spec/traceability.md`.
- The red-team reviews are in `redteam/`. They are the reason for most changes in this revision.

Spec files:

| File | Holds |
| :- | :- |
| `spec/learning.md` | The loop, every move, item families, levels, the unseen questions, the Checkup, dose and review capacity |
| `spec/experience.md` | Every exchange, all copy, the pad, the weekly line, waiting and failure states, the map, first run, accessibility gate |
| `spec/surfaces.md` | Every coding surface, tiers, the parity model, what each surface can count, conformance, install scope |
| `spec/architecture.md` | Engine, record format, sealing, grading interface, cloud sessions, phone, cost |
| `spec/security.md` | Threat model, sandboxing, supply chain, prompt injection, secrets, honest privacy copy |
| `spec/teams.md` | The codebase guide, shared-repo rules, the admin contract, the team plan, business model |
| `spec/measurement.md` | Metrics, the study, within-person experiments, the claims ladder, experiment protocols |
| `spec/traceability.md` | Every judge and red-team item, and where it is handled |

---

## 1. The product in one paragraph, and its name

Firsthand tells you what you can still do without your AI coding agent, and trains it while you build. It has three parts. **The Checkup:** once a month, if you start it, a short task in a real repo you have never opened, written and tested by people, run in a sealed sandbox, that your agent never saw. Over several Checkups it tells you, honestly, whether you got better or worse. **The loop:** a free, open-source layer that installs into the agent you already use (Claude Code, Codex, Cursor, Copilot, Gemini CLI, Devin, Amp and anything that reads an instruction file and can run a shell command). At a few natural breaks it asks you to think first: predict a result, name a cause, write one line of the real build, or look at an agent's pull request before reading its summary. Days later it asks again, cold, in a new form, at most 3 times a day. **The record:** a private map, in a git repo on your machine, of what you have shown without the agent, how it was graded, and how long ago. It goes down when you forget.

**Name.** Working name: **Firsthand** (command `firsthand`, short alias `fh`). It says what the product measures: what you can do yourself. Fallback: **Ownline**. Both are [unverified] for trademark, package registries (npm, PyPI, Homebrew), plugin directories and domains. "Firsthand" may collide with an existing careers product [unverified]. E0 now also checks findability: whether the product comes up first when the name is searched in directories, npm and on the web (red team market 12). The name is a founder decision (section 13).

**The promise, checkable in five minutes:** "Install it, and in five minutes it asks you three questions written by people, in a prompt your agent cannot read. It tells you how you did without your agent, and how it graded you. When you want, a Checkup in a repo you have never opened shows what you can do on new code." A user can check it: the questions run at once, in the pad (section 5.6), and the map records them with their date and how they were graded.

**What the launch says.** The claim the product can make on day one is about its honesty, not its efficacy: "It tells you when you got worse." This is a description of what the product does, not a claim that it makes anyone better (claims ladder, section 9.5).

---

## 2. Who it is for, and the wedge

### 2.1 Users and buyers

Users, in order:

1. **Engineers in their first years who build with an agent every day.** Their seniors see the gap more than they do. In a vendor survey, 85% of juniors said AI improved their understanding, while 16% of seniors said juniors fully understand the AI code they submit (BairesDev Q2 2026, https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/). This means the people most in need may not feel the need (red team market 7). So the first touch is a measurement, not a learning pitch: "Can you still do this without your agent?" Whether this framing beats "learn while you build" is tested on the site (E17).
2. **Experienced engineers moving into a new domain** (new language, new stack, first distributed system). This is closest to the setting of Shen and Tamkin, who studied people learning a new library (https://arxiv.org/html/2601.20245v2). The product must never ask about what they know (section 4.7).

Buyers, tested in v0, not later (red team market 4 and 7):

3. **Course leads and instructors** who let students use agents. They need an assessment that survives agents. CS50's own tutor still returned code blocks despite instructions (https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/). The Checkup and the human-written question bank are what they would buy.
4. **Engineering managers**, for onboarding. 38% of engineering leaders say AI cut the mentoring juniors get (https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles). They would buy the codebase guide and an onboarding outcome computed from their own git history (section 7).

Which buyer comes first is a founder decision after E9 (section 13).

Out of scope on purpose: hiring. A record used to judge people stops being honest. Proof packs and Checkup results are stamped "not a performance measure" (section 7).

### 2.2 The wedge

The wedge is a measurement the user cannot get anywhere else, followed by a loop that runs inside the agent they already use.

- **First five minutes.** `firsthand init` opens the pad and offers the sampler: three questions from the human-written bank, typed straight to the engine, never shown to the agent. The result is labelled "first look, not proctored". It records at most Met (section 4.9), because three items show little. It gives the user a reason to come back: "Your first Checkup is ready when you want it."
- **First session.** One demo drill on the user's own code: a Trace on code the agent wrote at least 7 days ago if the history has it, else on a bank example. It is labelled a demo and records at most Met, so it does not break the rule that only delayed answers count (red team efficacy 17).
- **First month.** The first Checkup, when the user starts it.

The promise is "remembers what you tried and how it was graded", not "remembers what you got right".

Activation is an event in the first session: the user answers the sampler or the demo drill. Retention is defined in section 9.

### 2.3 What is scarce, and what is not

Most of the loop is copyable by design. Claude Code's Learning output style already leaves `TODO(human)` gaps [verified: https://code.claude.com/docs/en/output-styles]. Claude Code has memory that persists across sessions [unverified: third-party guides, https://blog.memoryplugin.com/claude-code-memory/]. Cross-agent memory is already a third-party category (Cognee, claude-mem, Walrus) [unverified: https://docs.cognee.ai/integrations/claude-code-integration]. VibeWise is listed in the Anthropic directory [verified: https://github.com/nykooi1/vibe-wise]. A vendor could ship spaced review on top of these (red team market 2).

The assets that are scarce, and that the product is built around:

| Asset | Why it is hard to copy | Licence |
| :- | :- | :- |
| The human-written question bank | Written per idea by paid engineers, as parameterised families; a lab has weak reasons to author it | Separate content licence, not open source |
| The Checkup task set and service | Piloted tasks with measured difficulty, pinned repos, sealed tests run on a server | Separate content licence; the service is run by the product |
| The study-only pool | Never shipped; used only in the study | Not published |
| The public conformance table | Maintained per surface per release, run in CI | Open data |
| The record format and the brand | A documented format; a name that means "honest about you" | Open format; trademark |

Launch rule (red team market 5): no public launch until the first bank and the Checkup service are live. The open-source loop alone is not launched as the product.

---

## 3. Principles

Each principle is a rule the product is tested against. The evidence codes (L1 to L19) are the design rules in `research/learning-science.md` Part A.3.

1. **The build always wins.** No learning moment blocks the agent's next step, except a "your line" the user accepted, and even that is handed back in one word. The product never leaves a build, a commit or CI red. Evidence: interruptions raise stress even when people work faster (Mark et al., https://www.ics.uci.edu/~gmark/chi08-mark.pdf).
2. **The user thinks first, at a few chosen points.** Predict, diagnose, write the key line, review before reading the summary, explain. Evidence: Shen and Tamkin's high scorers asked conceptual questions or checked their understanding (https://arxiv.org/html/2601.20245v2); generation beats reading at about d = 0.40 (https://pubmed.ncbi.nlm.nih.gov/17645161/). L1, L4, L5, L18.
3. **Spend practice where skill erodes.** Debugging and checking agent output erode on ideas the user already knows. Evidence: the largest gap in Shen and Tamkin was debugging (https://www.anthropic.com/research/AI-assistance-coding-skills); monitoring automation is not practice (Bainbridge 1983, https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf). L4, L17.
4. **Only delayed, unaided, repeated, new-instance performance counts as skill.** A level rises only on two right delayed answers on different items. Evidence: immediate tests measure performance, not learning (Soderstrom and Bjork 2015, https://pubmed.ncbi.nlm.nih.gov/25910388/). L2.
5. **Grade by running code first.** In v1 only executable grades and people move levels. A model grader moves a level only after that grader model and version passes the gate (section 6.5).
6. **Separate the teaching instrument from the claim instrument.** Practice items tune the product. The human-written bank and the Checkup support claims to the user. A study-only pool, never shipped, supports public claims. Evidence: Koretz and Beguin's audit items (https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/).
7. **No pressure mechanics, but a reason to come back.** At most 3 due reviews a day, at most one reminder a day at the user's time, no streaks, points, badges or guilt (Hanus and Fox 2015, research/learning-science.md A.1 item 9). In their place: a weekly line of facts about the user's own work, and the monthly Checkup (section 4.12). Founder decisions 3 and 7.
8. **Silent on what you know, and silent when unsure.** Evidence: expertise reversal (Kalyuga 2007, https://doi.org/10.1007/s10648-007-9054-3). L10.
9. **One record across every agent, owned by the user, in local git.** Founder decision 1.
10. **Parity of outcome, tested and published per surface,** including what each surface can count toward a level (section 5.4). Founder decision 6, reframed with evidence.
11. **No new surface unless it names a job no agent surface can do.** v1 adds one: the pad, a terminal prompt the engine owns, because no agent chat can take an answer the agent cannot see.
12. **Honest about what it cannot know.** Every grade shows how it was graded, how its key was sealed, how the answer arrived, and how long ago. Every result in a personal tool is self-attested, and the map says so.
13. **Tune on delayed learning and felt cost, never on satisfaction.** Students rated learning lower where they learned more (Deslauriers 2019, research/learning-science.md A.1 item 2). L3.
14. **Accessible by default, as a release gate.** Plain text first, verdict word first, voice dictation for every answer, no timers.
15. **The user's machine is not a sandbox.** Code the user did not write runs only in a container with no network, or not at all (section 6.10).
16. **Repo text is data, never the product's voice.** Anything written by a contributor is shown quoted and attributed, and can never widen a setting (section 6.10).
17. **Say exactly what leaves the machine, and to whom.** No copy claims "nothing leaves" when a grader, a chat log or a server can see it (section 6.9).

---

## 4. The learning loop

Full detail: `spec/learning.md`.

### 4.1 Shape

| Layer | When | Moves |
| :- | :- | :- |
| In the build | At the agent's breakpoints | Predict, Call it, Your line, Explain back |
| At review time | When the user reviews an agent's pull request | Review first |
| Away from the build | Session start (offered, never a gate), the reminder, or when the user asks | Review (3 a day max), Drills (Trace, Check, Replay) |
| Measured | Mixed into reviews in the pad, and once a month if the user starts it | Unseen questions, the Checkup |

Rules for every move:

- **Confidence in the same action as the answer:** sure, think so, guess, or don't know. A right "guess" is recorded but cannot raise a level. "Don't know" counts as not recalled: it brings the idea back sooner and lowers a level like a miss, but it is not a sure miss for calibration. The copy says so plainly (red team efficacy 2).
- **Every answer records its format:** free recall, code, number, or choice. Choice formats test recognition and cannot raise a level past Recalled.
- **Predictions are compared, never graded.**
- **"Just tell me" always works.** It records that the attempt had help.
- **Every exchange carries a why-now and a one-word skip, and ends with the resume cue** `Back to: <task>. Next: <step>.`

### 4.2 The moves

| Move | Trigger | User does | Graded by | Can move a level? |
| :- | :- | :- | :- | :- |
| **Predict** | Before a deterministic step, on an idea at Not yet | One line: what will happen | Compared with the outcome | No. Prediction accuracy is its own line, apart from calibration |
| **Call it** | A test fails, and the user's delegation of debugging is high or C2 is low | A cause and the first check | Process points, then the cause | No. The agent's visible work often shows the cause (red team efficacy 6). It feeds the delegation signal and queues a Replay |
| **Your line** | The agent is about to write the one line that carries an idea new to the user | Writes it, before reading the test | The project's tests | Not in the session. It queues a delayed item with the test hidden, which can |
| **Explain back** | After a step passes, once per task the user chose to learn from | Two or three sentences | Self-marked against sealed points in v1; a gated model grader later | Not in the session. Delayed explain items use a new instance |
| **Review first** | The user opens an agent's PR to review, with their agent or `firsthand pr <url>` | Lists defects or says "looks clean", before seeing the agent's summary | Test-confirmed defects, CI, later fix commits | Only test-confirmed defects |

**Review first** is new (red team market 3). Coding is moving to background agents. Copilot cloud agent has no live user [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent]. The human is present at review time. So review time is a first-class trigger. The engine fetches the diff, hides the PR body and the agent's summary, and asks for findings. A finding becomes "confirmed" only when the user writes a test that fails on the PR and passes on a fix, which is also useful review work. Other findings stay "unconfirmed" until CI or a later fix commit settles them. Findings are private. The user may post them as an ordinary review comment in their own words, with no grade attached.

### 4.3 Your line

Founder decision 2 stands. Changes from the red team:

- **Write first, then read the test.** The marker names the goal and the test, and says "try before reading the test". At "line done" the engine asks one typed question: "Did you read the test first? yes or no." First-try pass rate is reported split by that answer (red team efficacy 7).
- **The evidence is the delayed item.** Your line queues an executable review, days later, in a new instance where possible, with the test hidden. That review, graded by the hidden test, is what can move a level. `line.survived` is dropped as a learning signal.
- **Neutral marker in shared repos** (red team privacy 7). In a repo the user does not own, the marker is a plain `TODO:` with the goal and the test. It never names the product or the user. The engine finds it by location and hash, not by text.
- **Open markers are handed back at commit by default in shared repos,** so they are never committed. In the user's own repos the user may keep them open across commits.
- **No marker in PR bodies.** A cloud agent lists open lines only in the engine's private carry, never in a PR.
- The marker states the goal and never describes the computation. The engine rejects markers with operators or formula words.
- Hint and "write it" are always free. Under pressure, on quiet branches, or on a failing deploy, an open marker is handed back before any check fires.
- The product never blocks a commit or a build.

### 4.4 When the engine speaks

The engine decides, in code. Inputs: the breakpoint, the idea tags, the user's levels, their debugging profile, pressure signals, quiet settings and the budget.

- **Novelty** gates Predict, Your line and Explain back.
- **Debugging profile** gates Call it: the share of recent failures the agent diagnosed with no user hypothesis.
- **Rapid delegation is not a silencer.** When the user moves fast, the engine asks nothing in the moment and queues one later item from the episode.
- **Pressure silences.** "urgent", "prod is down", a failing deploy, or a quiet branch pattern. On hookless surfaces this depends on the model following the skill, and the explicit quiet controls always work.
- **Explicit quiet beats guessing:** "quiet for 2h", "quiet today", "quiet in this repo", `firsthand quiet`.

### 4.5 The budget

| Limit | Default | Source |
| :- | :- | :- |
| Due reviews a day | 3; the user can lower it, or raise it with an explicit setting | Founder decision 3 |
| Reminders a day | At most 1, at a time the user picks. The install question has no pre-selected answer | Founder decision 7; red team market 1 |
| Unprompted in-build moments a day | 3, shown, set by the user | Design default, needs to be measured (E4) |
| Your line | At most one per task | Founder decision 2 |
| New ideas entering the review queue | Only when a slot is free or the idea is in a growth area | Red team efficacy 9 |
| Two skips in a session | End questions for that session, say so once | research/experience-design.md P3 |
| Three ignored reminders in a row | Ask once next session: keep, move or stop. Stop if no answer | Red team market 1 |
| Setup questions | One bundle per repo, one bundle a day | Judge designer |

### 4.6 Drills away from the build

Opt-in, inside the 3-a-day cap when due, never in the same week as the source material.

| Drill | Built from | Runs in | Graded by | Construct |
| :- | :- | :- | :- | :- |
| **Trace** | The user's own committed code, at least 7 days old | Scratch copy of committed files only, agent config stripped | Running the code | Code reading |
| **Check** | A past agent-written diff with a known outcome | Text only | Test-confirmed defects. A finding in a diff labelled "clean" is "unconfirmed", with an offer to write a test that shows it | Checking agent output |
| **Replay** | A fix commit whose test fails on the parent | A container with no network, or not offered | Process first, then the commit's own test | Debugging |
| **Compare** | The same idea met in two projects | Text only | Self-marked in v1; gated model grader later | Transfer |

Check labels are wrong by construction: "clean" only means nobody fixed it within 60 days (design default). So only defects confirmed by a failing-then-passing test move levels, and E15 hand-checks label accuracy before Check ships (red team efficacy 5).

Replay is the level-bearing diagnosis practice, because the agent is off. It ships only if E2 passes and a container runtime is present.

### 4.7 Cold start

A new record must not treat every idea as new, but it must not hide gaps either (red team efficacy 8).

1. **Inference only lowers how often an idea is offered.** It never silences. Commits with no agent trailer may still be agent-written: inline completions and pasted chat code usually leave no trailer [unverified per tool]. E11 measures trailer coverage per tool, on juniors and seniors.
2. **"I know X" needs two probes to silence:** one direct, one a new instance with the topic name hidden. Both right: the cluster goes quiet in every project.
3. **Silenced ideas get an occasional re-check item** in a review slot (design default: one every few months, needs to be measured).
4. **A gentle first week.** The moment cap starts low, and "your line" is offered only for ideas with no prior authorship found.

### 4.8 The dial

Off, Light, Standard (default), Deep, plus "just build" and "teach me this one". Light gives reviews and explain back. Standard runs all moves within the budget. Deep adds predictions, and your line grows from a line into a function into a design.

### 4.9 Levels

One ladder, four levels. Exposure is shown apart (red team efficacy 16).

| Level | Earned by |
| :- | :- |
| **Not yet** | Default, or one step down after a delayed miss or "don't know" |
| **Recalled** | Two right delayed answers on two different items, on different days |
| **Applied** | Two right delayed answers on new instances: different function, file or project, computed by the engine, topic name hidden |
| **Held** | Applied, then right at a longer gap on an unseen question, plus one other source (Checkup, field evidence, or another item family) |

**Met** is not a level. It lists ideas the user explained back, wrote a line for, saw an explainer on, answered with help, or answered in the session. It sits under its own heading on the map.

What can raise a level (all must hold): delayed; a free-recall, code or number format (choice caps at Recalled); confidence not "guess"; answer typed in the pad or captured by a hook, never relayed by the agent; graded by tests, a person, or a gated grader; key sealed in a separate context.

What lowers a level: one step per delayed miss or "don't know".

Every level shows its evidence age: "Recalled, last checked 12 days ago". Past the next due interval plus a margin, the map shows "not checked lately" instead of the level. Best level shows only in `map all`.

The six constructs (code reading, debugging, design judgment, explaining a change, transfer, calibration) stay separate and are never combined. Calibration uses delayed items only.

### 4.10 Field evidence

`firsthand field <commit or PR> "what I did"` logs work done without the agent. Since a missing trailer does not prove no agent was used, field evidence is labelled "self-reported" and can be one of the two sources for Held only alongside an unseen question.

### 4.11 Dose and review capacity

The spec's own defaults leave too few slots (red team efficacy 9): 3 reviews a day, one of them often an unseen question, against a 5-step interval ladder (3, 7, 21, 60, 180 days, from `record.py`). One new idea a day needs about 5 reviews a day at steady state. So:

- The new-idea rate is limited, not the review rate (section 4.5).
- When demand exceeds slots, the engine chooses: growth areas first, then sure misses, then ideas closest to a level change. `map all` says how many ideas are not being reviewed and lets the user pick growth areas.
- Levels show "based on N of M due items answered", and skip and expiry rates are tracked by item difficulty, so easy-item bias is visible.
- The user may raise the daily cap with an explicit setting (decision 3 says "by default").

Design targets per week on Standard are in `spec/learning.md` section 8. E1 measures them.

### 4.12 Coming back

The red team found that nothing brings users back (market 1). Replacements that are not pressure mechanics:

- **The weekly line.** In the first session of each week, one line of facts from the record about the user's own work: "Last week you named the cause of 2 of 5 failing tests before the agent did. The week before, 0 of 4." No praise, no streak, no count of missed days. Off with one word. Whether it pulls people back needs to be measured (E13).
- **The reminder question is a real choice.** At install: "A daily reminder? Type a time, or none." Nothing pre-selected.
- **The Checkup.** When a month has passed, the weekly line says once: "Your next Checkup is ready when you want it."
- **The engine build is gated on 30-day return of users recruited cold** from a directory listing, not from the founder's network (E13).

---

## 5. The experience end to end, and the parity model

Full detail: `spec/experience.md` and `spec/surfaces.md`.

### 5.1 First install

```
npx firsthand@<version> init     (or: uvx, brew)
```

`init` installs into **the agent it was launched from** only. It lists other agents it found and adds each one only after a separate yes (red team market 9). Before writing, it shows every file it will write and the exact diff, keeps byte-exact backups, and `firsthand uninstall` restores them. Hooks and MCP entries call an absolute, pinned path to the installed engine, never `npx` or `uvx` at run time (red team privacy 3).

It says, in plain lines:

1. Where the record lives (`~/.firsthand/record`, a git repo, no remote).
2. **What leaves the machine, exactly:** "By default nothing is sent anywhere by Firsthand. Answers you give in your agent's chat are part of that chat, and your agent's company sees them. If you turn on model grading, your answer, the rubric and a short code excerpt go to the company you name."
3. The size of the instruction text it adds to every session, in characters and an estimated token count (red team market 8).
4. What this surface can count toward a level (section 5.4).
5. Questions, nothing pre-selected where it matters: Is this a work computer? Dial (Standard). A daily reminder (a time, or none). Which repos may it read for drills (none by default).
6. The sampler offer: "Three questions written by people, in a prompt your agent cannot read. A few minutes. Yes, or later."

**Work installs** (the user said yes, or `firsthand team install` was used) get accurate copy instead of the old promise (red team privacy 1):

```
This is a work computer. Here is what your employer can and cannot see.
Can: that Firsthand is installed, and the files it adds to your agents.
Can, through your agent's logs: anything you type in your agent's chat.
So on this computer, answers go to the pad, not the chat, and your record is encrypted.
Cannot: your record, without your passphrase or keychain. Firsthand has no admin key.
Limit: an employer that controls this computer can, in the end, read anything on it.
Run firsthand verify to check this is a signed release.
```

### 5.2 One exchange

```
New idea: retries with a payment API. Why now: this test runs it. Say "skip" to skip.
If the first two calls time out and the third succeeds, how many charges does the provider see?
Answer, then: sure, think so, guess, or don't know.
```

After three exchanges the header fades to one clause. Prediction reveals have no verdict word. Graded answers lead with Correct, Partly or Not yet, then the missing piece at `path:line`, when it returns, how it was graded, and the resume cue. When the pad is open, the chat shows one line, "Question in your pad (skip ok)", and the agent never sees the question's answer.

### 5.3 A normal week

- **Session start.** After the first prompt is handled, one ignorable line: "2 reviews due, about 2 minutes. Say 'review' now, or later." On surfaces where chat answers cannot count, it adds: "In your pad they count toward your map."
- **In the build.** Maybe one prediction and one explain back on new ideas, one Call it if the profile says so. On known ideas, nothing.
- **Reviewing an agent's PR.** "Look first? Note any defects, or say clean, before I show the summary. Or skip."
- **Pressure.** Silence, and one offer to save it for later.
- **Evening.** One content-less reminder, if the user chose a time.
- **First session of the week.** The weekly line.
- **After a gap.** At most 3 reviews, the rest chosen by priority, no backlog count.
- **End of a project.** `firsthand wrap` and compare items for the next project.
- **Once a month, if the user starts it.** The Checkup.

### 5.4 The parity model, and a challenge to founder decision 6

**Challenge, stated explicitly.** Decision 6 asks for feature parity on all coding surfaces. Parity of mechanism is impossible on the evidence: Aider has no MCP and no hooks [verified: https://aider.chat/docs/config/options.html]; Copilot cloud agent supports MCP tools only and has no live user [verified: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp]; Copilot in Visual Studio, JetBrains, Eclipse and Xcode has no hooks [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet]; Zed's agent and Gemini CLI have no elicitation [verified: https://zed.dev/docs/ai/mcp, https://geminicli.com/docs/tools/mcp-server/].

**What we commit to instead: parity of outcome, as a tested promise per surface.** Every learning outcome is reachable on every surface in plain text plus a CLI call. And, new in this revision (red team efficacy 15): **every surface with a local terminal can count toward a level, through the pad.** Where the only channel is the agent's chat, answers are relayed and count as Met. The product says this at install, on the map and in the session-start line, and points the user to the pad. This is the honest form of parity: the same outcome everywhere, with the integrity of each channel shown.

| Support level | Meaning |
| :- | :- |
| **Tested** | Its conformance row passes the threshold over repeated runs in this release |
| **Floor, untested** | The plain-text floor should work; no conformance run yet |
| **Known gap** | A named outcome fails or is weaker; the gap is listed |

Tiers: T0 instruction file and shell; T1 MCP tools; T2 hooks; T3 native ask; T4 designed UI; T5 away from the keyboard. Where each surface sits is in `spec/surfaces.md` section 3. v1 tests Claude Code, Codex and Cursor. Vendor learning-mode gaps (`TODO(human)`) are read by their own adapter with its own conformance row, shown "Floor, untested" until tested (red team market 13).

### 5.5 Moving between surfaces

One event has one identity everywhere. Open lines and due reviews follow the user. Answers from a vendor phone app arrive as relayed answers, and count as Met.

### 5.6 The pad

The pad is a terminal prompt the engine owns: `firsthand pad`, in any terminal or an IDE's terminal panel. It solves three red-team problems at once:

- **Integrity:** an answer typed in the pad is "typed" provenance only when the engine opened the terminal itself and no agent is its parent process (red team privacy 4).
- **Privacy:** answers in the pad never enter the agent's chat, so an employer's chat logs never hold them (red team privacy 1).
- **Unseen questions:** the pad is the only place unseen questions and Checkup steps are shown.

The pad is plain text, works with screen readers and dictation, has no timers and no letter shortcuts (decision 5). When it is closed, the chat path works as before, with relayed provenance.

---

## 6. Architecture

Full detail: `spec/architecture.md` and `spec/security.md`.

### 6.1 Shape

```
any coding agent
   |  instruction block, skill folder, MCP tools, hooks (absolute pinned path)
   v
firsthand engine (on the user's computer, signed release)
   |-- CLI and pad   review | drill | pr | map | quiet | field | checkup | verify
   |-- MCP server    stdio, tools only; agent tools can only narrow settings
   |-- hook dispatch never returns allow or deny decisions
   |-- miner         read-only scan of added repos
   |-- runner        scratch copies from committed files; containers for untrusted code
   |-- grader        executable first; model graders opt-in, gated, named
   v
record: ~/.firsthand/record   (git, append-only events, signed, optionally encrypted)
   +-- optional: the user's own private git remote
   +-- optional, v2, paid: end-to-end encrypted relay
Checkup service (opt-in, user-started): serves tasks, runs hidden tests, signs results
```

### 6.2 The record

- A per-user git repo outside any project tree. One JSON file per event, ULID names, union merge [verified: research/platform.md].
- Derived state is never committed.
- **Encrypted at rest on work installs, optional elsewhere:** each event file is encrypted with age to the user's key, held in the OS keychain or behind a passphrase. File names stay ULIDs, so merge still works.
- **Private keys never live in the record.** A commit guard refuses any key material in the record (red team privacy 8).
- **Every free-text field is secret-scanned** before it is written: answers, notes, field logs. Matches are redacted and the user is told.
- Project ids use a keyed hash of the remote URL, with a per-record secret, so a repo cannot be guessed from it.
- `forget <idea>` removes a whole idea, never single attempts (red team efficacy 18). It rewrites history, expires the reflog and prunes, and warns that any remote copy remains until the user rewrites it too.
- Hook payloads and debug logs are never stored.

### 6.3 Sealing

The key's sha256 is committed before the question is shown. The engine refuses to release a key until an `answer.locked` event exists. For unseen items and Checkup steps, keys are released only for typed answers. Keys are written in a separate context where the surface has one. A second blind context solves each model-written practice item; if it disagrees with the key, the item is discarded (red team efficacy 11). A sure miss on a practice item triggers a re-check; if the re-check disagrees with the key, the miss is refunded and the item retired.

Stated limit: an agent with the code can always rebuild an answer, and the user can always ask the agent for help. Sealing protects against a grader that adapts the key to the answer. It does not prove to anyone that the user worked alone.

### 6.4 The unseen questions

The red team showed that a bank shipped in the package, with its key in the package, is obfuscation, not encryption (privacy 4). The design now says so, and changes:

- **In-product unseen questions are parameterised families,** written by people. The engine makes a fresh instance per user from each family's generator. A leaked instance is worth little, and a family is retired for that user after use.
- **They are labelled "not proctored".** They protect against the teaching agent tuning to its own items. They do not protect against a user who asks the agent to answer.
- **Shown only in the pad,** typed only.
- **The study-only pool never ships.** It is served only inside the study, from a server, with exposure tracked.
- **The gap between practised and unseen results** shows "not yet calibrated" until item difficulty is equated from pilot data (red team efficacy 10). The map lists which ideas have unseen coverage at all.

### 6.5 Grading

Providers in order: executable; a person; a model in a separate context (subagent, headless agent, or user API key); self-marked.

- **v1 moves levels only on executable grades and people** (red team market 8). Model-graded moves are recorded and self-marked against sealed points, showing as Met, until a grader passes the gate.
- **The gate is per grader model and version** (red team efficacy 3): an absolute agreement floor with people (threshold, a decision), a leniency check, run on a shipped calibration set of human-graded answers before that grader can move levels.
- A sample of undisputed grades is regraded as well, so disputes do not only push grades up.
- **Each model grader names who receives what:** "Sends your answer, the rubric and up to 40 lines of code to Anthropic, under the account your Claude Code uses." (The line count is a design default.) `grader = local-only` is the default on work installs (red team privacy 6).
- Explain-back rubrics are written from the code and diff, by a context that has not read the agent's explanation (red team efficacy 12).
- `firsthand cost` shows calls and tokens. The engine never spends a plan without consent.

### 6.6 The idea catalog

An open, versioned catalog with stable IDs, aliases and known confusions. The engine proposes a fixed candidate list per diff; the agent picks from it. Silence when tags disagree. E3 tests tag agreement before cross-agent silence is relied on.

### 6.7 Cloud sessions

Cloud agent disks do not survive. Paths, in order:

1. The user's own private record remote, if attached.
2. (v2) The relay.
3. **The carry branch, redesigned** (red team privacy 10): offered only in private repos the user owns. The local engine creates the branch in advance and records its name; a cloud session only appends to it. Imports accept only an allowlist of event types (answers, line events, queued items; never config, consent, grades or devices), validated strictly, labelled unauthenticated, capped at Met. The engine deletes only branches it created. Deleted commits stay readable by hash on GitHub [verified: https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github], so the prompt says the ciphertext and its timing persist.
4. In every other repo: a `firsthand import <blob>` line at session end.

The founder must accept the carry branch as an exception to decision 1 (section 13).

### 6.8 Phone

v1: vendor phone apps, where answers are relayed and count as Met, plus a content-less calendar event. v2: the device link, after E12, bound to one interface with authenticated pairing, rendering cards the engine owns, so answers there count as typed. v2, paid: web push through the relay.

### 6.9 What leaves the machine

| Path | What travels | Who receives it | Default |
| :- | :- | :- | :- |
| Answers in the agent's chat | The question, answer, verdict | The agent's company, and the employer's logs on work plans [unverified per vendor] | Chat on personal installs; the pad on work installs |
| Model grader | Answer, rubric, short excerpt | The named company and account | Off; local-only on work installs |
| Checkup service | An anonymous token, the task id, the user's patch to a public repo | The product's service | Only when the user starts a Checkup |
| Private git remote | The record | The user's host | Off |
| Carry branch | Encrypted events | Collaborators see ciphertext and timing | Off; private repos the user owns |
| Proof pack | Items and counts the user picks, stamped | Whoever the user gives it to | Off |
| Design-partner stats | Pasted counts | The product team | Off |

Telemetry is off. No Prio3 or DAP [verified: https://datatracker.ietf.org/doc/draft-ietf-ppm-dap/]. Cryptography uses age and libsodium.

### 6.10 Security summary

Full detail: `spec/security.md`.

- **Untrusted code** (red team privacy 2): Checkup tasks and Replay run only in a container with no network, built from a pinned image with dependencies resolved in advance. Without a container runtime they are not offered. Trace runs the user's own committed code in a scratch copy made from committed files only (never `.env` or untracked files), with agent and editor config stripped (`.claude/`, `.mcp.json`, `.cursor/`, `AGENTS.md`, `.vscode/`), in a folder only the user can read.
- **Supply chain** (red team privacy 3): reserve names now; signed releases with registry provenance; `firsthand verify`; explicit `firsthand upgrade` that shows the config diff; hooks never return allow or deny, and conformance tests check it. Claude Code hooks can return `allow` [verified: https://code.claude.com/docs/en/hooks]; whether that skips the permission prompt is [unverified], so we never do it.
- **Prompt injection** (red team privacy 5): repo text (guides, owner notes, commit messages, excerpts) is shown quoted and attributed, with commands and URLs stripped from notes. Guides are used only in repos the user marks as trusted. Agent-callable tools can only narrow settings. Anything that widens (budget, grader, import, delete, consent, remote) needs a confirmation in a pad prompt the engine opens itself.
- **Secrets** (red team privacy 8): scan every free-text field and every postmortem drill, and show authors each redaction.

---

## 7. Teams

Full detail: `spec/teams.md`. Teams come after the individual loop shows retention, but the buyer tests run in v0.

- **The codebase guide (v2).** Plain files in `.firsthand/guide/`. Used only in repos the user marks trusted. Owner notes are shown quoted and attributed, with commands and URLs removed. Postmortem drills are secret- and personal-data-scanned, and the author sees each redaction.
- **Shared-repo rules (v1).** Neutral TODO markers, handed back at commit, never in PR bodies. Neutral CI text: "Open TODO in retry.py:42." No carry branches in repos the user does not own.
- **The admin contract.** `firsthand team install` turns nothing on. Admins can set defaults up to Standard, with no reminder, and turn excerpts off. Admins cannot read records, require a relay, see who uses the tool or how many opted in, define outcomes that one person can reach, or demand proof packs through the product. Proof packs are stamped "not a performance measure".
- **The team outcome a buyer can see** (red team market 4): time from a new hire's start to their first merged PR in an area with a guide, against areas without one, computed from the company's own git history. It uses no Firsthand data at all. Whether it moves needs to be measured.
- **The team report (later, paid).** Counts above a group floor of 8 (design default), fixed group definitions, suppressed when the opted-in group changed by fewer people than the floor, no opted-in count shown. Legal review of the consent basis before launch, since employee consent is rarely freely given [verified: https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_202005_consent_en.pdf].

---

## 8. Business model, funding and distribution

Full detail: `spec/teams.md` section 6.

| Offer | Who pays | Adds | Price |
| :- | :- | :- | :- |
| Firsthand loop | No one | Engine, moves, drills, map, adapters | Free, open source |
| Firsthand Checkup, personal | No one, funded by the plan below | Monthly Checkup, sampler, unseen families | Free to individuals |
| Firsthand for courses | Course providers | Checkups for a class, proctored live checks, class reports with no individual data shown to peers | Needs to be measured |
| Firsthand Team | Companies | Guide tools, onboarding outcome, SSO | Needs to be measured |
| Firsthand Sync (v2) | Individuals | Relay, push, device link | Needs to be measured |

**Funding** (red team market 6). By the spec's own estimates, v0 to v2 is a large build with no revenue before courses or Team, plus surface rows that break when vendors change. A funding plan must be chosen before v1 (section 13). Options: a research grant (the product doubles as an instrument for studying AI and skill), a sponsor that is not an agent vendor, a foundation home, or a vendor partnership with a stated independence clause. To cut the maintenance cost: adapters are generated from one manifest, and conformance runs in CI through each agent's headless mode where it has one.

**Distribution.** Directories (Claude Code plugins, Codex, Cursor, skills.sh, the MCP registry), npm, PyPI, Homebrew, GitHub [unverified: directory rules]. The site leads with the measurement framing if E17 favours it.

**A shareable result** (red team market 10). A Checkup result can be exported as a signed statement: "Task T at commit X in repo Y; patch hash H; the hidden tests passed on the service; date." A third party can check the signature and re-run the tests on the patch, without trusting the record. It says nothing about who wrote the patch or with what help, and says so in the statement.

**Migration of current users** (red team privacy 11). The current skill tells users to commit `.learning/` to the project repo (`skills/learning-while-building/SKILL.md` line 103). So existing users' misses are in project git history. `firsthand import-lwb` says this plainly, offers a history rewrite for repos the user owns, and warns that forks and remotes keep old copies. The current skill must be changed in v0 week one to stop recommending the commit (section 15).

---

## 9. Measuring that it works

Full detail: `spec/measurement.md`.

### 9.1 One primary outcome

The claim the product wants to earn: people who build with it can do more without the agent, weeks later, on problems they have not practised, than comparable people using the same agent without it, with no meaningful loss of speed.

**Primary outcome, in every place it is named: G1-S,** a held-out unaided battery from the study-only pool, made of transfer items (new instances, topic names hidden), at a fixed delay. It never ships, so neither arm has practised its items (red team efficacy 1). The control arm gets the same practice with the item format on unrelated content, so format familiarity is equal.

| Kind | Indicator | Role |
| :- | :- | :- |
| Primary | G1-S | Supports the efficacy claim |
| Secondary | G2: task in an unfamiliar repo; G3: bug localisation; G4: defect finding including clean diffs | Supports claims |
| Leading | Delayed recall, retention, calibration on delayed items, prediction accuracy, the unseen gap once calibrated | Tunes the product |
| Product | Activation; answer rate; review completion; 30-day return of cold-recruited users | Tunes and gates |
| Guard | Task time on versus off; skip rate; reminder dismissals; cost; delayed accuracy near ceiling | Must not get worse |

### 9.2 The Checkup

Once a month, user-started, never due, never reminded. One small task in a real public repo the user has never opened, pinned to a commit, in a container with no network and dependencies resolved in advance, agent off, steps in the pad, hidden tests run on the Checkup service. Plus one bug to localise and two diffs to check, one clean. Every task is piloted and its difficulty stored. Results show against difficulty. No trend is shown until a minimum number of Checkups (needs to be measured), because one or two items per construct per month on repos of different difficulty cannot show a trend (red team efficacy 14).

### 9.3 Within-person experiments

Randomise by idea cluster, sealed assignment, never shown on cards. **No per-user effect is shown** until a minimum count from E7's power calculation is reached. Results are pooled across opted-in users first (red team efficacy 13).

### 9.4 The study

Preregistered, randomised, two arms, at least two agents and two surfaces, several weeks, G1-S primary at a fixed delay, G2 to G4 secondary, task time as the guard, blind human graders, ideally independent researchers.

### 9.5 Claims ladder

| Evidence in hand | Allowed claim |
| :- | :- |
| None | What it does: "It tells you when you got worse." "Designed around research on how people learn with AI." No efficacy claim |
| Design-partner or cold-cohort data | The number, its definition and its sample size, for example "n = 20, 3 weeks" |
| The study, positive on G1-S | The specific result, effect size and link |
| Independent replication with G2 to G4 | "People who use it become better engineers," with scope |

The rung "measured on you" is removed. `docs/index.html` is checked against this ladder in v0 and before each release.

---

## 10. Roadmap

Sizes are rough estimates in engineer-weeks, marked "est.". They are planning guesses, not measurements.

### v0: prove there is something worth building (est. 6 to 10 weeks, plus bank authoring)

- **Week one:** change the current skill to stop telling users to commit `.learning/`. Reserve the names on npm, PyPI and Homebrew. Fix the site's claims against the ladder.
- **Fund and write a small bank** of parameterised families for a few ideas, and a first few Checkup tasks. Authoring cost needs to be measured.
- **E16, Checkup demand:** a concierge Checkup, run by a person, for cold-recruited users.
- **E14, a learning check:** a small lab study with the existing skill (one session on a new library, a quiz a week later, on versus off), with a go or no-go threshold fixed in advance.
- **E13, cold return:** 30-day return of users recruited from a directory listing.
- **E9, buyers:** manager and instructor interviews.
- E0 to E5, E8, E11, E15, E17.

**Gate for v1:** E13, E14 and E16 pass their thresholds, and a funding plan is chosen.

### v1: the smallest thing that is still the product (est. 18 to 26 weeks)

- Engine, CLI, the pad, MCP server (tools only), hook dispatcher, record with encryption option, sealing, executable grading, cost meter, `verify` and signed releases. Est. 7 to 9.
- The moves including Review first, the budget, the dial, quiet controls, cold start, the weekly line. Est. 4 to 5.
- Trace and Check (after E15); Replay only if E2 passes, container only. Est. 3 to 5.
- The container runner and the Checkup client; the Checkup service with hidden tests and signed results. Est. 3 to 4.
- Seed catalog; in-product unseen families. Est. 2 to 3, plus authoring.
- Tested adapters for Claude Code, Codex and Cursor, installed one agent at a time; the floor for every other agent. Est. 2 to 3.
- Text map with evidence age, `stats`, `export`, `field`, migration, the accessibility gate, the public conformance table. Est. 2 to 3.

Not in v1: model grading that moves levels, any local page, the device link, the relay, the team plane, the cloud carry branch (the import line covers cloud in v1).

### v1.1 (est. 4 to 6 weeks)

Tested adapters for VS Code Copilot, Copilot CLI and Gemini CLI; the carry branch for private repos the user owns, if E10 passes; gated model graders, per grader version.

### v2 (est. 20 to 30 weeks)

More adapters; the codebase guide; course offer pilot; the device link (if E12 passes); Sync; compare items across projects.

### Later

Team report, SSO and SCIM after E9 and legal review; proctored live checks; a static binary engine.

---

## 11. Experiments to run first

Full protocols: `spec/measurement.md` section 6. Thresholds are decisions, not findings. The founder fixes them before a run, never after.

| # | Question | Pass rule (thresholds are decisions) |
| :- | :- | :- |
| E0 | Is the name usable, findable, and does it land well? | No blocking conflict; packages available; comes up first in directory and npm search; no more than 1 of 8 reads it negatively |
| E1 | Do people answer, and what dose do they get? | Half of offered moments answered and half of due reviews done in week 3, and delayed accuracy is not near ceiling |
| E2 | How many real bugs can be replayed in a container? | At least 2 reproducible drills per 100 commits in a language, median setup under 2 minutes |
| E3 | Do agents tag ideas consistently? | Fleiss kappa at least 0.6 |
| E4 | Does the engine pick moments as well as a person? | 70% agreement; median felt cost "a little" or less |
| E5 | Does a given grader model agree with people? | Per grader version: absolute kappa floor, within 0.1 of human-human, no leniency past a set margin |
| E6 | Does the floor work on weak tiers? | Each outcome passes in 8 of 10 runs |
| E7 | Within-person pilot | 80% of delayed items taken; gives the power inputs |
| E8 | What does grading cost? | Cost and quota per agent reported; no surprise spend |
| E9 | Will managers or instructors pay? | Threshold set by the founder |
| E10 | Will people accept the carry branch? | 7 of 10 choose carry or their own remote |
| E11 | Does cold-start inference spare seniors without hiding juniors' gaps? | 80% of inferred-known ideas pass two probes, in both groups; trailer coverage measured per tool |
| E12 | Can the phone pair in one tap? | One confirmation tap on iOS and Android |
| E13 | Do cold-recruited users come back? | 30-day return above a threshold set by the founder |
| E14 | Does the existing skill move a delayed quiz at all? | Go or no-go threshold fixed in advance |
| E15 | Are Check labels right? | Hand-checked label accuracy above a threshold |
| E16 | Do users want the Checkup? | Share of cold users who book a second Checkup above a threshold |
| E17 | Which framing pulls the target users? | "Can you still do this without your agent?" versus "Learn while you build", on the site |

---

## 12. Risks

The three biggest are first.

| Risk | Why it matters | Mitigation |
| :- | :- | :- |
| **The loop does not make people better unaided weeks later** | The founding study measured immediately, with 52 people (https://arxiv.org/html/2601.20245v2) | E14 before the engine; the study with a held-out pool; claims ladder |
| **Nobody comes back** | Value is long term, cost is now (Lehmann 2025, https://arxiv.org/abs/2409.09047) | The Checkup, the weekly line, a real reminder choice; E13 gates the build |
| **No one funds it** | Large build, no revenue before courses or Team; a vendor can ship the copyable parts | Lead with the scarce assets; test buyers in v0; choose a funding plan before v1 |
| Untrusted code or a compromised release harms users | One package touches every agent | Containers, pinned paths, signed releases, `verify`, one agent at a time |
| The employer uses it as surveillance | Work installs, chat logs, consent under employment | Accurate copy, the pad, encryption, no usage counts, legal review |
| Users ask the agent to answer the unseen questions | The agent shares the user's account | Labels, typed provenance, parameterised families, study-only pool |
| Model graders disagree with people | Kappa as low as 0.295 has been reported (research/evidence.md A.2 item 7) | No model grade moves a level in v1; per-grader gate |
| Coding moves to background agents | Fewer live breakpoints | Review first at PR time |
| Tag drift breaks silence | The calm promise rests on it | Fixed candidate list, silence when unsure, E3 |
| EU AI Act may class learning-outcome grading as high-risk [unverified: https://casrai.org/news/ai-act-high-risk-classification] | Courses and Team could be regulated | Legal review before either |

---

## 13. Decisions only the founder can make

1. **The name** after E0.
2. **Accept parity of outcome** as the meaning of decision 6, including that chat-only channels count as Met and the pad is how every terminal surface counts.
3. **Accept the carry branch** (v1.1, private repos the user owns) as an exception to decision 1, or keep the import line only.
4. **Fund the bank and the Checkup service in v0,** and accept that they ship under a separate content licence.
5. **Choose a funding plan before v1:** grant, sponsor, foundation, or vendor with an independence clause.
6. **Which buyer first:** courses or teams, after E9.
7. **Thresholds** for every experiment, fixed before each run, including the v1 gate (E13, E14, E16).
8. **Accept a Checkup service** that the product runs. It is a network call the user causes, but it is a server that logs exposure by anonymous token.
9. **Who runs the study,** and whether to seek independent researchers.
10. **Engine language** for v1 (Python recommended) and whether to fund a static binary later.
11. **The claude.ai artifact Room** from the earlier design: keep as an optional adapter later, or retire.

Founder decisions 2, 3, 4, 5 and 7 are accepted as written. Decision 3's "by default" lets a user raise the cap; the product does not suggest it.

---

## 14. What changed

From the earlier design (`design/learning-experience/`): any agent instead of Claude Code only; record outside project trees; separate-context sealing; item families; human-written unseen questions; Check drills on real diffs instead of injected bugs; diagnosis offered by debugging profile.

From the previous version of this document, after the red team:

| Before | Now | Red team item |
| :- | :- | :- |
| The loop led; the Checkup was a measurement extra | The Checkup and the bank lead; the loop is the free layer | Market 2, 5 |
| "Your employer cannot see ... No key allows it" | Accurate copy, the pad, encryption at rest, `verify` | Privacy 1 |
| Scratch copies and clones on the bare machine | Containers with no network, or not offered | Privacy 2 |
| One install writes every agent | One agent at a time, pinned paths, signed releases | Privacy 3, market 9 |
| Bank "encrypted" in the package | Parameterised families, labelled not proctored; study pool never ships | Privacy 4, efficacy 1 |
| One answer moves a level | Two right on different items; one step down per miss | Efficacy 2 |
| Model grades could move levels | Executable and people only in v1; per-grader gate | Efficacy 3, market 8 |
| Engine build gated on answer rate | Gated on a learning check, cold return and Checkup demand | Efficacy 4, market 1 |
| Seen was a level | Met is a separate list | Efficacy 16 |
| No PR-time move | Review first | Market 3 |

---

## 15. Red team items not fixed, or fixed differently

| Item | What we did instead | Why |
| :- | :- | :- |
| Market 4: show admins an aggregate active count above the floor | Not adopted. The buyer sees an onboarding outcome from their own git history instead | An active count lets an admin infer who opted in by subtraction (privacy 9), and contradicts the work-install copy. The two red-team items conflict; privacy wins because a surveillance reputation would end the individual product |
| Privacy 4: serve in-product unseen items from a server | Partly. In-product items are parameterised families, labelled "not proctored". The server is used for the Checkup and the study pool | A server for every review would make daily use depend on our uptime and send a call per review. The Checkup and the study are where proctoring-like control matters |
| Privacy 2: run all scratch work in a container | Trace runs without a container, on the user's own committed code only | The user and their agent already run this code daily. Requiring a container for Trace would remove the first-session drill for most users. Checkup and Replay still require one |
| Privacy 11: change the current skill now | Scheduled as the first v0 task, not done in this revision | This revision edits design files only. The change is small and should ship with its own commit and a note to current users |
| Privacy 1: make the employer promise fully true | Accurate copy and the strongest protections we can give | An employer that controls the device and the binary can always read it. The copy says so |
| Market 6: state a funding plan | Options listed; the choice is a founder decision before v1 | Money is not a design choice |
| Efficacy 6: cap Call it answers given after the agent started investigating | Call it never moves a level | The agent starts at once in nearly every case, so the cap would apply almost always. Simpler to say so. Replay carries level-bearing diagnosis |
| Efficacy 13: pool on-device results across users | Adopted, but pooling needs opt-in sharing of counts, so it depends on design partners until telemetry exists | Telemetry stays off by default |

Every other critical and major item is fixed. Where each one is handled is in `spec/traceability.md`.
