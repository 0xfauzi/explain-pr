# Concept: Unaided (agent-native)

A product concept for a learning layer that lives inside whatever coding agent
a person already uses. It stays quiet until a moment worth learning, adds as few
new surfaces as possible, and keeps one honest record of what the person can do
without the agent.

This is one of several concepts. It treats the earlier round in
`design/learning-experience/` as evidence, not as the answer. It draws on the
six research reports in `design/product/research/`. Claims about products are
tagged [verified: source] or [unverified]. "[verified: research/x.md]" means the
claim is verified, with its URL, in that report. Numbers without a source are
not used; where a number is a design guess, it says "needs to be measured".

---

## 1. The product in one page

**Name: Unaided.** The name is the promise. It measures, and grows, what you can
do without the agent. It sets the product apart from look-alike plugins whose
names describe learning while building (for example learn-while-build
[verified: research/users-market.md]). Trademark and package-name availability
for "unaided" is [unverified] and must be checked before launch. The command is
`unaided`.

**One sentence:** Build at full speed with any coding agent; Unaided keeps your
pace and keeps a private record of what you can now do without it.

**What it is, concretely:** a small open-source engine (`unaided`) on the user's
computer, one binary with five faces (CLI, MCP server, hook dispatcher, local
page, OS scheduler entry); a skill and a three-line instruction block every
major agent reads; thin adapters generated from one manifest; and a record that
is a git repository the user owns. No account. No network by default.

**What the user notices:** most of the time, nothing; the agent builds as usual.
A few times a day, at a natural break, one short question about an idea new to
them, drawn from code the agent just wrote, free to skip. Sometimes one marked
line of the real build to write. When a test fails on an idea they are
learning, one offer to call the cause first. At session start, at most 3 cold
reviews a day. A map, any time, of what they have shown they can do unaided.

**What makes it different from the free learning modes and plugins:**

| | Assistant learning modes | Community plugins | Learning platforms | Unaided |
| :- | :- | :- | :- | :- |
| Works on your real code | Yes | Yes | No | Yes |
| Keeps a record across sessions | No [verified: research/users-market.md] | Some | Yes | Yes |
| Works across agents | No | Some (Claude Code, Codex) | n/a | Every agent with a file and a shell |
| Measures skill days later, without the agent | No | No | Partly | Yes, the core measure |
| Keeps your build speed | Partly | Often slows it (VibeWise asks for your design first) [verified: research/users-market.md] | n/a | Yes, every step skippable, build continues |
| Answer key fixed before asking | No | No | Yes | Yes, sealed by hash |

---

## 2. Who it is for, and the wedge

**Primary segment: engineers in their first years who build with an agent every
day.** The pain is personal and they feel it. In the BairesDev Q2 2026 survey,
85% of juniors say AI improved their understanding, but only 16% of seniors say
juniors fully understand the AI code they submit
(https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/, a vendor
survey). 38% of engineering leaders say AI cut the mentoring juniors get
(https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles). For this
group, a private record is a feature: they can admit gaps safely.

**Second segment: experienced engineers moving into a new domain** (a new
language, a new stack, a first distributed system). This is close to the
setting of Shen and Tamkin, where people learned a new library with AI help
(https://arxiv.org/html/2601.20245v2). The product's silence on known ideas
matters most here: it must never talk down to a senior.

**Third segment, for revenue: teams.** Budgets exist for developer learning and
review tools. The product rebuilds part of the mentoring that leaders say AI
removed, without surveillance (section 7.6).

**Later: education.** Courses that let students use agents need a way to see
whether skill forms. CS50's own tutor still returned code blocks up to a
quarter of the time despite being told not to
(https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/).
That supports the design choice to hold guardrails in the engine, not in a
prompt.

**Out of scope, on purpose: hiring.** A record used to judge people stops being
honest. The product never sells or exposes records for hiring.

**The wedge.** One install that works in the agent the user already has, today,
with a visible change to their map within the first week. Distribution is where
agents already find extensions: the Claude plugin directory, the Codex plugin
marketplace, skills.sh, the MCP registry, npm and PyPI, and GitHub itself
[unverified: directory review rules; research/users-market.md]. Being local,
small and auditable makes directory and security review easier.

---

## 3. Principles

These are the product's rules. Each traces to the research reports.

1. **The build always wins.** No learning moment blocks the agent's next step,
   except a "your line" the user accepted. An unanswered question expires into
   the review queue. (research/experience-design.md)
2. **Silent by default.** Speak only about ideas that are new to this user, at
   the agent's own breakpoints. Silence on what the user already knows is a
   feature. (Expertise reversal, Kalyuga 2007, in research/learning-science.md
   L10.)
3. **The user thinks first, at a few chosen points.** Predict before, diagnose
   before the agent, write the key line, explain after. (L1, L4, L5.)
4. **Only delayed, unaided, new-instance performance counts as skill.** A level
   never rises in the session where the agent wrote the code. (L2.)
5. **Grade with a key fixed before asking, held in the engine.** Run tests first;
   use a model grader only for what cannot be run. (research/evidence.md.)
6. **No pressure mechanics.** At most 3 reviews a day, at most one reminder a
   day at the user's chosen time, no streaks, no points, no badges, no guilt.
   Say this openly. (L14, founder decisions 3 and 7.)
7. **One record across every agent, owned by the user, in local git.**
   (Founder decision 1, research/platform.md.)
8. **Parity of outcome.** Every surface runs the full loop in plain text. Richer
   UI only makes it faster. (research/surfaces.md, challenged in section 13.)
9. **No new surface unless the agent's own surface cannot do the job.** This is
   the agent-native angle. Each new surface must name the job no agent surface
   can do.
10. **Tune on delayed learning and felt cost, never on satisfaction.** People
    cannot feel learning happen (Deslauriers 2019; METR 2025; research/
    learning-science.md L3).

---

## 4. The core loop and the evidence behind each step

The loop has five moves inside the build, two optional practice moves, and one
honest map. Every move is skippable at once, at no cost.

### 4.1 The five moves

| Move | When | What the user does | What the agent does meanwhile | Evidence |
| :- | :- | :- | :- | :- |
| **Predict** | Before a step whose result the user can reason about (a test run, a migration, a query plan) | States in one line what will happen, with confidence | Runs the step | Prediction and generation effects; Lead-and-Reveal narrowed the gap between perceived and actual ability (https://arxiv.org/abs/2410.08922) |
| **Call it** | A test fails on an idea the user is learning | Names the likely cause and one check, before the agent diagnoses | Waits once, briefly; then runs the user's check first, then its own | Largest gap in Shen and Tamkin was debugging; users who let the AI debug scored 24% (https://www.anthropic.com/research/AI-assistance-coding-skills); L4 |
| **Your line** | The agent is about to write the one line that carries a new idea | Writes that line; the project's tests grade it | Builds everything around it | Generation effect, about d = 0.40 (https://pubmed.ncbi.nlm.nih.gov/17645161/); fading worked examples; Claude Code's Learning style leaves TODO(human) gaps [verified: https://code.claude.com/docs/en/output-styles] |
| **Explain back** | After a step passes, or at commit | Says in two or three sentences why the change works | Continues to the next step | Self-explanation g = 0.55 (research/learning-science.md); Shen and Tamkin's "generation then comprehension" pattern scored 86% |
| **Review** | Session start, or one reminder at the user's time | Answers up to 3 cold questions from last week's real code, with confidence | Nothing; reviews happen before work starts or away from it | Testing effect g = 0.50, 0.69 delayed (https://doi.org/10.1037/a0037559); spacing g = 0.74 (https://link.springer.com/10.1007/s10648-020-09572-8); daily emailed questions still showed an effect two years later (https://pubmed.ncbi.nlm.nih.gov/19375095/) |

Rules that hold for every move:

- **Confidence in the same action.** Every answer carries "sure", "think so" or
  "guess". Sure misses come back sooner and are listed first. (L12; Metcalfe,
  https://doi.org/10.1146/annurev-psych-010416-044022.)
- **Predictions are compared, never graded.** A wrong prediction is closed
  against the real outcome with the gap shown at `path:line`. It never moves the
  record. (L6.)
- **"Just tell me" always works.** It answers at once and only records that the
  attempt had help. Adults are never refused. (research/experience-design.md.)
- **The agent shows its own reasoning after the user tries, or when asked.**
  Conceptual questions get answered at once. (L18.)

### 4.2 Two optional practice moves

These cover skills that real work exercises rarely or with poor feedback.

- **Rehearse.** An opt-in drill built from the user's own history: a reverted
  bug replayed on a scratch branch, or an incident timeline from their logs. The
  user diagnoses; the engine grades the process (what they checked, in what
  order). Evidence: simulator practice for rare skills and the SRE Wheel of
  Misfortune pattern; moderate for the practice, weak for outcomes (L16).
- **Spot.** With consent, on a scratch or reversible change only, the agent
  seeds one issue in a diff and the user tries to find it before the tests run.
  This trains checking agent output, the skill most at risk when an agent does
  the writing. Speculative but well motivated (L17; Bainbridge,
  https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf). Off by
  default.

### 4.3 The map

The map is the product's one view. It shows, per idea and per dimension:

- **Best level** as an outline and **latest level** as a fill. Levels can go
  down. Decay is shown as a fact plus a next step, never pushed as a
  notification.
- **Dimensions reported separately, never one score:** code reading, debugging,
  design judgment, explaining a change, transfer, calibration
  (research/evidence.md). Skills come apart in the evidence (Lister 2004,
  Fitzgerald 2008), so a single number would mislead.
- **The audit gap:** the difference between scores on practised items and on a
  hidden audit bank the teaching agent never sees. It is always shown. This is
  the product's own check against teaching to its own test (Koretz and Beguin,
  in research/evidence.md).
- **Calibration** only once there are enough delayed answers; below that the map
  says "too few answers to tell". The minimum count needs to be measured.

Levels per idea:

| Level | Meaning | How it is earned |
| :- | :- | :- |
| Not yet | No evidence, or only with help | Default |
| Seen | Explained back or wrote "your line" the same day | Same-session evidence only, never counts as unaided |
| Recalled | Answered a cold review correctly days later | A sealed, delayed item, no hints |
| Transferred | Applied the idea in a different project or form, topic name hidden | A transfer item with recorded surface distance |
| Owns it | Recalled and transferred across at least two gaps, and calibrated | The gap lengths need to be measured |

### 4.4 Ideas, not files: the open idea catalog

To keep one record across projects and agents, the product needs stable names
for ideas. Unaided ships an **open idea catalog**: a public, versioned list of
engineering ideas with stable IDs (for example `concurrency/idempotency-key`,
`db/n-plus-one`), each with a short definition and known confusions with other
ideas. Agents tag code they write with catalog IDs through one tool call. Users
and teams can add private ideas. The catalog is what makes these possible:

- Silence on known ideas, across every project and agent.
- Interleaving of easily confused ideas (L9).
- Comparing the same idea in two projects, which aids transfer (Gentner,
  research/learning-science.md L11).
- Team aggregates that say "idempotency is a common gap" without naming anyone.

The catalog is data, not code, and is open to contributions. How well agents
tag ideas consistently needs to be measured (section 12).

---

## 5. The moment engine: when it speaks and when it stays silent

The agent-native angle depends on picking moments well. The engine, not the
model's goodwill, decides. A prompt alone does not hold a guardrail (CS50
evidence above), so the rules live in code.

### 5.1 Inputs

- **Breakpoints** from hooks where they exist: session start, prompt submit,
  before tool, after tool, tool failed, turn end, session end. These five to
  seven moments exist in Claude Code, Codex, Cursor, Copilot CLI and cloud
  agent, Gemini CLI, Devin, Kiro and Amp [verified: research/surfaces.md
  section 5]. Where hooks do not exist, the skill tells the agent to call
  `unaided moment` at the same points.
- **Novelty:** the idea IDs in the current diff, checked against the user's
  record. Only ideas at Not yet or Seen are candidates.
- **Mode:** acceleration or exploration. Barke et al. describe both modes of
  working with a coding assistant (https://arxiv.org/abs/2206.15000). Signals of
  acceleration: short imperative prompts, repeated quick turns, the user editing
  while the agent works. In acceleration the engine stays quiet.
- **Pressure signals:** words like urgent, prod down, hotfix, failing deploy, or
  a user-driven error loop. Then the engine goes silent and offers "teach me
  this later" once.
- **Budget** for today (below).

### 5.2 Budget, not schedule

| Limit | Default | Source |
| :- | :- | :- |
| Due reviews a day | 3 | Founder decision 3 |
| Reminders a day | At most 1, at a time the user chooses, only when something is due | Founder decision 7 |
| Unprompted learning turns | One per chosen task for predict and explain back; at most one per 10 minutes overall (needs to be measured) | research/experience-design.md |
| "Your line" | At most one per task, only for ideas at Not yet or Seen, never on the Light dial or under pressure | Founder decision 2, L5 |
| Two skips in a session | End questions for that session | research/experience-design.md |
| Ignored reminders | Three in a row stops reminders, with one line saying so | research/experience-design.md |

### 5.3 The dial

One setting with four positions: **Off, Light, Standard, Deep**. Plus two
per-task phrases any agent understands: "just build" and "teach me this one".

Off records and asks nothing. Light gives reviews and explain back only, with
no "your line" or "call it". Standard (default) runs all five moves within the
budget. Deep adds predictions, and "your line" grows from a line into a function
into a design as the level rises (L5).

### 5.4 Every exchange has the same shape

Every learning exchange, on every surface, follows one shape so that it reads
the same in a terminal, a chat, a screen reader or a phone:

```
Learning: <idea in plain words>. Why now: <one clause>. Skip: say "skip".
<the question>
(answer, then sure / think so / guess)
...
<verdict word>. <what was right, as information>. <missing piece, path:line>.
Comes back: <when>.
Back to: <task>. Next: <step>.
```

The last line is a resume cue. Only about 10% of programming sessions resumed
editing within a minute of an interruption
(https://sites.cc.gatech.edu/reverse/repository/resumptionstrategies.pdf), so
the cue is required, not decoration.

---

## 6. Surfaces: parity of outcome on every coding agent

### 6.1 The floor and the tiers

Every surface reaches a common floor: an instruction file, a skill folder, and a
shell or MCP tools. AGENTS.md lists 23 agents that read it [verified:
https://agents.md]. Claude Code reads AGENTS.md only when no CLAUDE.md exists
[verified: https://code.claude.com/docs/en/memory.md]. The `.agents/skills/`
path is read by Codex, Cursor, VS Code Copilot, Gemini CLI, Zed, Roo, Amp,
OpenCode, goose and Devin [verified: research/surfaces.md section 3]. MCP tools
work everywhere except Aider [verified: https://aider.chat/docs/config/options.html].

| Tier | Mechanism | What it adds | Required? |
| :- | :- | :- | :- |
| T0 | Text, a file, a shell | The whole loop as chat replies and `unaided` commands | Yes, the floor |
| T1 | Skill plus MCP tools | The agent calls `unaided` without shell quoting; tools only, no prompts or resources | Yes where MCP exists |
| T2 | Hooks | Breakpoints arrive without relying on the model to remember | Enhancement |
| T3 | Native ask (MCP or ACP elicitation, question cards) | Answer and confidence in one form | Enhancement |
| T4 | Designed UI (MCP Apps, plugin UI) | Map and review cards inline | Enhancement |
| T5 | Away from the keyboard (vendor phone app, device link) | Reviews and "your line" on the phone | Enhancement |

The engine detects tiers at run time and always returns complete text as well.

### 6.2 How the loop runs on each surface

Each row says how every outcome is reached. "Text" means the outcome runs as a
chat reply and an `unaided` call. Tier facts come from research/surfaces.md
section 8.7; "?" there means untested and is an experiment.

| Surface | Predict, explain back, call it | Your line | Review | Map | Record | Notes |
| :- | :- | :- | :- | :- | :- | :- |
| Claude Code CLI, desktop, IDE | Hooks plus native ask [verified: research/surfaces.md] | Marked comment, turn-end hook check | Session-start hook | Text, or local page | Local | Phone via Remote Control [verified: https://code.claude.com/docs/en/mobile.md] |
| Claude Code web and phone | Hooks; question cards [verified: research/surfaces.md] | Marked comment, listed in PR body | Session start | Text | Visitor mode (section 8.6) | VM reclaimed after inactivity [verified: https://code.claude.com/docs/en/claude-code-on-the-web.md] |
| Codex CLI and app | Hooks plus elicitation [verified: https://learn.chatgpt.com/docs/hooks] | Marked comment | Session start | Text; app panels [unverified] | Local | Phone through ChatGPT mobile [verified: research/surfaces.md] |
| Codex cloud | Text only [unverified for skills and MCP] | Marked comment, PR body | Next local session | n/a | Visitor mode | Containers cached up to 12 hours [verified: https://developers.openai.com/codex/cloud/environments] |
| Cursor IDE and cloud | Hooks with followup_message; elicitation; MCP Apps [verified: https://cursor.com/docs/agent/hooks, https://cursor.com/docs/context/mcp] | Marked comment | Session start | MCP App card | Local, or visitor in cloud | Cursor iOS and web for cloud [verified: research/surfaces.md] |
| VS Code Copilot | Hooks (preview); elicitation; MCP Apps [verified: https://code.visualstudio.com/api/extension-guides/ai/mcp] | Marked comment | Session start | MCP App card or webview | Local | |
| Copilot in Visual Studio, JetBrains, Eclipse, Xcode | Text via skill; no hooks [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet] | Marked comment, pre-commit check | Agent calls `unaided due` at start, per instruction | Text or local page | Local | Weakest local tier; the floor carries it |
| Copilot CLI | Hooks [verified: https://docs.github.com/en/copilot/concepts/agents/hooks] | Marked comment | Session start | Text | Local | |
| Copilot cloud agent | Tools only, no live user [verified: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp] | Marked comment, listed in PR body | Next local session | n/a | Visitor mode | Sessions end at 59 minutes [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent] |
| Gemini CLI | Hooks; no elicitation [verified: https://geminicli.com/docs/hooks/reference/] | Marked comment | Session start | Text or local page | Local | |
| Devin Desktop and CLI (formerly Windsurf, per press [unverified]) | Hooks via .devin/hooks.v1.json [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] | Marked comment | Session start | Text | Local | |
| Amp | Hooks with continue; plugin UI [verified: https://ampcode.com/docs/customize/plugins] | Marked comment | Session start | Plugin UI | Local | Amp phone apps [verified: https://ampcode.com/manual] |
| OpenCode | Hooks; npm plugin [verified: https://opencode.ai/docs/plugins/] | Marked comment | Session start | Text; desktop UI experimental | Local | |
| Kiro | Hooks [verified: https://kiro.dev/docs/hooks/] | Marked comment | Session start | Text | Local | |
| Cline, Roo, goose, Junie, Zed agent | Text via skill and MCP tools; no hooks in Roo, goose, Junie, Zed [verified: research/surfaces.md] | Marked comment, pre-commit check | Agent calls `unaided due`, per instruction | Text; goose MCP Apps | Local | Zed's agent has no elicitation [verified: https://zed.dev/docs/ai/mcp] |
| Zed or JetBrains with an ACP agent | ACP elicitation [verified: https://www.jetbrains.com/help/ai-assistant/acp.html] | Marked comment | The agent's own | Text | Local | |
| Aider | Text; no MCP, no hooks; lint and test commands only [verified: https://aider.chat/docs/config/options.html] | Marked comment checked by Aider's test command | `unaided review` in terminal | Text or local page | Local | The pure floor case |
| Claude chat, ChatGPT (no code agent) | MCP Apps render [verified: https://modelcontextprotocol.io/extensions/apps/overview.md] | n/a | Review cards | MCP App map | Device link only | Optional review surface, not a build surface |

### 6.3 Why "your line" is the anchor feature

"Your line" needs no protocol. The agent writes the build and leaves one marked
comment, for example `UNAIDED(you): compute the retry delay from attempt n`,
then calls `unaided line open`. The engine records the file, the marker, the
idea ID, and the sealed check: which tests must pass. Then:

- On surfaces with a turn-end hook, the hook refuses to end the turn if the
  agent filled the line itself.
- Everywhere else, a pre-commit check run by `unaided` catches a filled line
  that has no user attempt event.
- On cloud agents that open a PR, the line is listed in the PR body, where the
  user meets it.
- The project's own tests are the grader. That makes it the strongest
  evidence the product collects: real work graded by executable checks. Work
  sample tests remain among the stronger predictors of job performance, though
  a 2022 reanalysis lowered estimates
  (https://ink.library.smu.edu.sg/lkcsb_research/6894).

A hint is free, and "write it" hands it back to the agent at once, recorded as
with help. No timer.

### 6.4 Conformance, so parity is tested, not claimed

Parity of outcome is a promise per outcome per surface. A scripted session runs
each agent headless where it allows (Claude Code `-p`, Codex `exec`, Gemini CLI
non-interactive, Copilot CLI [verified: research/surfaces.md section 10.6]) and
checks that each outcome is reached and that the record events match. Surfaces
without a headless mode get a manual checklist each release. The results are
published as a public table. A row with a failing outcome is labelled, not
hidden.

Grading parity matters too: before scores from the phone, CLI and IDE are
compared, the engine checks that they agree (research/evidence.md).

---

## 7. The experience end to end

The example user is Priya, an engineer in her second year, building a payments
service with an agent. Every surface below is one she already has, except the
optional local page and the optional phone link.

### 7.1 First install

One command in her terminal, or one click in her agent's plugin directory:

```
npx unaided init
```

Homebrew, pip and a static binary ship too. Package names are [unverified].

`init` does four things and says each in one line:

1. Creates the record at `~/.unaided/record` as a git repo. No remote.
2. Writes the skill to `.agents/skills/unaided/` and links it where an agent
   does not read that path (`.claude/skills`, `.cline/skills`).
3. Adds a three-line block to AGENTS.md (or CLAUDE.md where that exists) that
   points to the tool. Long rules never go in the instruction file, since every
   session of every agent pays for them.
4. Registers the MCP server and hooks for each agent it finds on the machine,
   and lists which ones it found.

Then three questions, each with a default: dial (Standard), daily reminder (off,
or a time she picks), record location (`~/.unaided/record`).

Nothing else happens until the first natural breakpoint. There is no tutorial.
The first real question is the tutorial.

### 7.2 First question

She asks the agent to add retries to the payment client. The diff tags
`network/exponential-backoff` and `api/idempotency-key`. Her record has neither.
Before the test run, the engine offers a prediction:

```
Learning: retries with a payment API. Why now: this run tests it. Skip: say "skip".
If the first two calls time out and the third succeeds, how many charges does
the provider see without an idempotency key?
(answer, then sure / think so / guess)
```

She answers "one, sure". The test runs. The engine compares:

```
Not quite. You were right that only one call returns a success.
The provider may still have processed the timed-out calls: see
client.py:42, where each retry builds a new request with no key.
A sure miss like this is the most useful kind; it comes back in 2 days.
Back to: add retries. Next: add the idempotency key.
```

The agent continues. Her answer is not graded; it is the start of a record.

### 7.3 A normal day

- **Session start.** In whichever agent she opens, the session-start hook adds
  one line: "2 reviews due, about 2 minutes, or skip." She answers both, cold.
  Nothing is shown until she commits.
- **During the build.** Maybe one prediction and one explain back, on new ideas
  only. On ideas she owns, nothing.
- **Your line.** For a new idea, the agent leaves one line. She writes it. The
  tests pass on the second try. The engine records Seen, not Recalled: this was
  the same session.
- **A failing test.** On an idea she is learning: "Want to call the cause
  first? One line, or skip." She guesses a race; the engine runs her check
  first, then the agent's.
- **Pressure.** She types "prod is down". The engine goes silent for the
  session and offers once: "teach me this later?"
- **Evening.** If she set a reminder and something is due, one notification at
  her time: "1 review due". No question text in the notification.

### 7.4 A week later

- Her map has changed: two ideas moved from Not yet to Recalled, one sure miss
  is now right. The map shows this the first time she opens it in the week, as
  a fact, not a celebration.
- Reviews now interleave easily confused ideas (retry versus idempotency), with
  the topic name hidden until she commits (L9).
- She can say "I think that grade is wrong" on any verdict. The engine regrades
  once against the fixed rubric, in a separate context, and shows both.
- If she was away for days, she sees at most 3 reviews and the rest are spread
  out. No backlog count.

### 7.5 End of a project

- `unaided wrap` writes a short, factual summary to her record: ideas met, what
  she has shown unaided, what is still with help, and the audit gap.
- It offers transfer questions for her next project: "You used an idempotency
  key in payments. Where would the same idea apply in the job queue?"
- She can export a **proof pack**: sealed items she chooses, with their hashes,
  answers and grades, for a mentor or a portfolio. It is labelled as
  self-graded evidence, not a credential. A credential needs a proctored live
  check (section 9).

### 7.6 A team

Her team buys the team plan. What changes:

- **Shared idea catalog** for their codebase: "our retry policy", "our event
  schema rules". Reviews draw on these.
- **Aggregate view for leads**, only for groups of at least 5, following the
  Viva Insights pattern [verified:
  https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings]:
  "which ideas in our codebase are commonly Not yet". Never who.
- **Ask a person.** Priya can send one item, with her answer, to a named
  teammate for a human review. It is her action, one item at a time.
- **No admin can read an individual record.** There is no admin key for it.
  No admin can turn on telemetry for anyone.

---

## 8. Architecture

### 8.1 Shape

```
  any coding agent
     |  instruction file (3 lines), skill folder, MCP tools, hooks
     v
  unaided engine (one static binary, on the user's computer)
     |-- CLI           unaided due | review | line | map | wrap | check ...
     |-- MCP server    stdio; tools only for the core; both MCP revisions
     |-- hook dispatch unaided hook <agent> <event>
     |-- local page    127.0.0.1, map and review, optional
     |-- scheduler     launchd / systemd timer / Task Scheduler, one reminder
     v
  record: ~/.unaided/record (git, append-only event files, signed commits)
     |
     +-- optional: private git remote, or end-to-end encrypted relay (paid)
     +-- optional: device link to phone (QR pairing)
```

All learning logic lives in the engine and the skill: state, rubrics,
scheduling, the daily cap, "your line" checks. Adapters only translate event
names and output shapes, and are generated from one manifest so they cannot
drift: Claude plugin, Codex plugin, Cursor plugin, Gemini extension, Kiro
power, Amp plugin, OpenCode npm package, Devin plugin, Cline MCP listing
(research/surfaces.md section 10).

### 8.2 The model the engine uses

The engine ships with no model and no API key. Every model call goes through the
user's own agent:

- **Asking context:** the user's agent, as usual.
- **Rubric author:** a separate context. On surfaces with subagents (Claude
  Code, Devin [verified: research/surfaces.md]) the skill tells the agent to
  spawn one that writes the question and key and returns only the question.
  Elsewhere, the engine can call the agent's headless mode as a separate
  process. Where neither exists, the key is written in the same context and
  sealed before asking, and the map labels these items as weaker.
- **Grader:** a separate call that sees only the question, the sealed rubric,
  the code shown, and the answer, never the teaching session. The answer is
  treated as data. Each point awarded must quote the span that earns it
  (research/evidence.md).
- **Executable checks first.** Tests for "your line", the real build outcome
  for predictions. A model grades only what cannot be run.

Stated limit: an agent can always rebuild the answer from the code. Sealing
stops the key leaking before the answer; it does not stop a determined user.

### 8.3 The record

- **Append-only event files**, one per event, ULID names, in a per-user git
  repo outside any project tree. Event types include `item.sealed`,
  `item.shown`, `answer.locked`, `grade.issued`, `grade.disputed`,
  `line.opened`, `line.attempted`, `config.set`.
- **Everything else is derived and never committed:** the schedule, the map,
  the due list. They are rebuilt from events, so a future scheduler such as
  FSRS can replay the log (L8).
- **Union merge never conflicts on content**, because two devices only add
  different files. Three rules cover every conflict: earliest lock wins, last
  write wins per config key, the daily cap is per user (research/platform.md).
  No CRDT library is needed.
- **Sealing:** each key's sha256 is committed before the question is shown.
  `unaided reveal` refuses to release a key until an `answer.locked` event
  exists. `unaided check` verifies hashes after reveal. This fixes the earlier
  round's finding that the key reached the page before the answer.
- **Tamper evidence:** each device keeps its own hash chain; commits are signed
  with SSH keys [verified:
  https://docs.gitlab.com/user/project/repository/signed_commits/ssh.html].
- **Readable:** events are plain JSON. `unaided export` writes everything;
  `unaided forget <idea>` and `unaided delete` remove data, with a git history
  rewrite the user confirms.

### 8.4 MCP tools (the core works with tools alone)

Copilot cloud agent supports MCP tools only, with no prompts or resources
[verified: research/surfaces.md], so the core is eight tools:

| Tool | Purpose |
| :- | :- |
| `moment` | Agent reports a breakpoint and idea IDs; engine replies ask or stay quiet, with full text |
| `seal` | Rubric author commits a question and key; returns the question only |
| `answer` | Records an answer and confidence; locks it |
| `grade` | Runs executable checks, or returns the grading packet for a separate grader |
| `line` | Opens, checks, or hands back a "your line" |
| `due` | Lists today's reviews within the cap |
| `map` | Returns the map as text, and as an MCP App where the host declares it |
| `config` | Dial, reminder, per-task overrides |

Elicitation is used only when the client declares it; an MCP App card only when
the host declares the UI extension. Both MCP revisions are spoken
(research/surfaces.md). The design does not depend on MCP sampling or on MCP
Apps as the main UI.

### 8.5 Phone

A phone cannot run git, so it holds a projection plus an outbox
(research/platform.md).

- **Through the vendor's app** where it exists: the Claude app Code tab, ChatGPT
  mobile for Codex, Cursor iOS and web, GitHub Mobile, Amp's apps [verified:
  research/surfaces.md section 7]. Reviews arrive as part of a normal session.
- **Device link**, optional: QR pairing in the Tailscale pattern, where keys
  never leave the device [verified: https://tailscale.com/kb/1232/derp-servers].
  The computer gives the phone a sealed pack of due cards with no answer keys.
  The phone returns encrypted answers by local network, file or QR. This costs
  one tap (founder decision 4). Grading is delayed until the computer sees the
  answers; the effect of that delay on learning needs to be measured.
- **Reminder** with no relay: one recurring calendar event with no content,
  created by `unaided reminder set`. Web push always needs a sender server
  [verified: https://webkit.org/blog/16535/meet-declarative-web-push/], and
  scheduled local web notifications never shipped [verified:
  https://developer.chrome.com/docs/web-platform/notification-triggers]. A
  native app with local notifications is a later phase. On iOS, reminders use
  the passive or active level, never time-sensitive.

### 8.6 Cloud sessions: visitor mode

Cloud agent disks do not survive, and there is no local record there. The
engine detects a cloud session (for example `CLAUDE_CODE_REMOTE=true`
[verified earlier: research/surfaces.md]) and runs in visitor mode:

- It keeps today's attempts in memory. It does not read the full record.
- With one yes from the user, it writes only new attempts to
  `.learning-inbox/<ulid>.json` in the project branch. Keys stay sealed by
  hash. The local engine imports and deletes the inbox the next time it sees
  the branch.
- Silence on known ideas is weaker here, because the engine cannot see the
  record. A small, user-approved summary of known idea IDs (no answers) can
  travel with the inbox, opt-in.
- A private remote for the record is the other option, and is exactly the
  "unless the user explicitly asks" path in founder decision 1.

On first run the engine says plainly: "This is a cloud session. Without your
yes, today's answers will be lost when it ends."

### 8.7 Telemetry and product measurement

- Off by default. Opt-in aggregates use Prio3 over DAP via Divvi Up, which stays
  private if one of the two aggregators is honest [verified:
  https://docs.divviup.org/how-it-works]. Code, answers, rubrics and idea names
  are never collected.
- **The product's real metrics**, computed on the device and shown to the user
  in `unaided stats`: share of offered questions answered, share of due reviews
  done, 30-day return, and delayed unaided accuracy at 3 and 21 days.
  Engagement numbers are guard metrics only.
- **Efficacy, within each person:** new ideas are randomly assigned to get a
  move (say "your line") or not, and delayed unaided results are compared on
  the device (L19). No server is needed for the user to see whether a move
  helps them.

---

## 9. Privacy and trust

**What leaves the machine by default: nothing.** No account, no server, no
network call the user did not cause.

**What the user can choose to send, one item or one stream at a time:**

| Choice | What travels | Who can read it |
| :- | :- | :- |
| Private git remote | The record, as the user's own repo | Whoever the user's host allows |
| Encrypted relay (paid) | Ciphertext of new events and due packs | Only the user's devices; the relay sees sizes, times and IPs, and a plain list says so (Obsidian pattern [verified: https://obsidian.md/help/sync/security]) |
| Visitor inbox | New attempts from one cloud session | Anyone with the project branch; keys sealed |
| Proof pack | Items the user picks | Whoever the user gives it to |
| Team aggregate | Counts above a group of 5 | The team lead |
| Telemetry | Private aggregates | No one individually |

**Trust rules:**

- Private keys are generated on devices and never leave them. Cryptography uses
  maintained libraries (age, libsodium); no custom crypto.
- A self-graded record is a guide, never a credential. A third party who needs
  evidence uses a **live check**: a short proctored session with fresh sealed
  items, run with the user present. This is a later product.
- The record is never used for hiring and never sold. This is written into the
  licence for the hosted services and into the team contract.
- The EU AI Act may class worker evaluation and learning-outcome grading as
  high-risk [unverified, secondary source:
  https://casrai.org/news/ai-act-high-risk-classification]. The team plan avoids
  individual evaluation by design, and legal review is required before the team
  and education plans launch.

---

## 10. Business model

The individual product is free and open source, forever. Revenue comes from
the things that need a server or an organisation.

| Offer | Who pays | What it adds | Price |
| :- | :- | :- | :- |
| Unaided (core) | No one | Engine, all moves, map, local page, every adapter, device link on local network | Free |
| Unaided Sync | Individuals | End-to-end encrypted relay across computers, phone reminders via push, phone review without the computer on | Needs to be measured by a price test |
| Unaided Team | Companies, per seat | Shared idea catalog for the codebase, aggregate view (group of 5 or more), ask-a-person routing, SSO and SCIM, region-pinned or self-hosted relay | Needs to be measured; comparable budgets exist for learning and review tools (Pluralsight and CodeRabbit prices in research/users-market.md are [unverified]) |
| Unaided Education | Courses and schools | Course idea catalogs, opt-in class aggregates, live checks | Needs to be measured |
| Sponsorship | Agent vendors, foundations | Funds the open idea catalog and the conformance table | n/a |

**Ruled out:** selling records, ads, hiring use, paid streak repair or any paid
pressure mechanic (a catalogued dark pattern, research/experience-design.md).

**Why a vendor toggle does not end the business.** The largest risk is that an
agent vendor ships its own version for free (research/users-market.md). The
defensible parts are the ones a single vendor has weak reasons to build: one
record across rival agents, an open idea catalog, a record the user owns
outside any vendor, and an honest measure that could show the vendor's own
agent eroding skill. If a vendor ships a good learning mode, Unaided should
work with it: read its TODO(human) gaps as "your line" events.

---

## 11. Roadmap: v1, v2, later

### v1: the engine and the floor (first public release)

Goal: one install, works in the five most used agents, the map changes in week
one.

- Engine binary with CLI, MCP server (tools only), hook dispatcher, scheduler.
- The five moves, the budget, the dial, pressure silence.
- Sealing, separate grading, executable checks, disputes.
- Record in local git with signed commits and `unaided check`.
- Adapters for Claude Code, Codex, Cursor, VS Code Copilot and Gemini CLI, plus
  the plain skill and AGENTS.md block for everything else.
- Visitor mode for Claude Code web and Codex cloud.
- Text map, plus the local page.
- Open idea catalog, first version, scoped to common web and backend ideas.
- On-device metrics and `unaided stats`.
- Public conformance table for the v1 agents.
- Migration from the current `learning-while-building` skill's record.

### v2: everywhere, and the phone

- Adapters for Devin, Amp, OpenCode, Kiro, Cline, Copilot CLI and cloud agent,
  goose, Zed and JetBrains via ACP, Aider.
- MCP App map and review cards where hosts render them.
- Device link (QR pairing) and phone reviews; calendar reminder.
- Unaided Sync (paid relay).
- Rehearse drills from the user's own history.
- Interleaved and transfer items across projects.
- On-device within-person experiments switched on by default for new ideas,
  with results shown to the user.
- Opt-in private telemetry.

### Later

- Unaided Team and Unaided Education.
- Spot (seeded issues in agent diffs), after an ethics review.
- Native phone app with local notifications.
- Live checks for third-party evidence.
- A proposed open spec for agents: a small "learning moments" interface in
  which an agent reports breakpoints and idea tags, and offers a user-attempt
  slot. Unaided would be the reference implementation. Proposing it to the
  Agentic AI Foundation, which stewards AGENTS.md [verified: https://agents.md],
  is a stretch goal.
- A preregistered randomised study (section 12, assumption 1) before any
  efficacy claim in marketing.

### Claims ladder for marketing

What the product may say at each stage (research/evidence.md):

| Stage | Allowed claim |
| :- | :- |
| v1, no study | "Built on published research on learning with AI. Keeps your pace. Keeps a private record." |
| On-device results | "Shows you which moves help you, measured on you." |
| After a preregistered trial with a positive delayed, unaided result | The specific result, with the study link |

---

## 12. The five riskiest assumptions, and the cheapest test for each

| # | Assumption | Why it is risky | Cheapest test |
| :- | :- | :- | :- |
| 1 | The moves make people better unaided, days later, not just better at the product's questions | The founding study tested immediately after one hour, with 52 people (https://arxiv.org/html/2601.20245v2). No one has tested this loop with agents over weeks | Within-person test on the existing skill: for 10 users over 3 weeks, randomly assign new ideas to "moves on" or "moves off"; at day 21, a cold, blind-graded item per idea from the hidden audit bank. Cost: one script and a small recruited group. Effect size needs to be measured |
| 2 | Users will answer, not skip everything | People choose the easy path and overrate the benefit of AI help (Lehmann 2025, https://arxiv.org/abs/2409.09047) | Ship v1's answer-rate counter to 20 early users; watch share of offered questions answered and share of due reviews done over 2 weeks, by dial. No server: users paste `unaided stats` |
| 3 | The engine can pick moments well enough that users feel no flow cost | Interruptions raise stress even when people work faster (Mark et al., https://www.ics.uci.edu/~gmark/chi08-mark.pdf). Mode detection from prompts is untested | Wizard-of-Oz: 5 users, a person decides moments by watching the transcript, then compare with the engine's rules on the same transcripts. Ask one felt-cost question at session end |
| 4 | Agents tag ideas consistently enough for one record across projects and agents | If tags drift, silence on known ideas fails and the record fragments | Take 30 real diffs, ask three agents to tag each from the catalog, measure agreement. Takes an afternoon |
| 5 | Parity of outcome holds on the weak tiers (no hooks, tools only, cloud) | If the loop only works on Claude Code and Cursor, the "every agent" promise fails | Run the scripted conformance session on Copilot in JetBrains, Gemini CLI, Aider and Copilot cloud agent with the v1 skill; fill every "?" in research/surfaces.md section 8.7 |

Other risks: model graders disagree with humans (kappa as low as 0.295,
research/evidence.md); a name collision; a vendor toggle; teams reading
aggregates as surveillance.

---

## 13. Founder decisions: accepted, and two challenged

| # | Decision | Position |
| :- | :- | :- |
| 1 | Record in local git, no remote unless asked | **Accepted, with a clarification challenged on evidence.** On cloud agents the disk does not survive (Claude Code web VMs reclaimed [verified: https://code.claude.com/docs/en/claude-code-on-the-web.md]; Codex containers cached up to 12 hours [verified: https://developers.openai.com/codex/cloud/environments]; Copilot cloud sessions end at 59 minutes [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent]). Without an exception, cloud answers are lost. Visitor mode (section 8.6) asks once, sends only new attempts in the project branch, and keeps the full record local |
| 2 | "Your line" on | Accepted. It is the anchor feature and the most portable one (section 6.3) |
| 3 | At most 3 due reviews a day | Accepted. A gap that runs long costs less than one that is too short (Cepeda 2008, research/learning-science.md) |
| 4 | One confirmation tap on the phone where no-tap is impossible | Accepted. Used for device-link answer return and for allowing push |
| 5 | Letter shortcuts off by default | Accepted. No UI the product draws registers letter shortcuts unless the user turns them on |
| 6 | Feature parity on all surfaces | **Challenged on evidence.** Parity of mechanism is impossible: Aider has no MCP or hooks [verified: https://aider.chat/docs/config/options.html]; Copilot cloud agent has tools only and no live user [verified: GitHub docs above]; Zed's agent and Gemini CLI have no elicitation [verified: https://zed.dev/docs/ai/mcp, https://geminicli.com/docs/tools/mcp-server/]; Claude Code does not render MCP Apps [verified: research/surfaces.md]. Proposed: parity of outcome, every outcome on every surface, tested by a public conformance table |
| 7 | At most one reminder a day at a time the user chooses | Accepted. Also: only when something is due, and stop after three are ignored |

---

## 14. Open questions

- How much does delayed grading on the phone (device link) weaken feedback?
  Needs to be measured.
- What is the smallest audit bank that gives a stable audit gap per user?
  Needs to be measured.
- Does silence on known ideas make seniors trust the product, or forget it is
  installed? Retention by segment needs to be measured.
