# Concept: Groundwork, for engineering teams that build with agents

Status: product concept, round 2. Angle: teams and organizations. Groundwork
helps engineering teams adopt coding agents and still have engineers who can
own, review and debug what the agents write. It onboards people to a real
codebase, rebuilds mentoring at scale, and is built so that it can never be
used as surveillance. Individuals use it free, forever, with or without a team.

Inputs: the six reports in `design/product/research/` and, as evidence only,
the earlier round in `design/learning-experience/`. This concept is not a
retrofit of the earlier plan. The earlier plan served one person in one agent.
This one serves a team of fifty people on six different agents.

Tags. [verified: URL] means the claim was checked in this round's research,
which cites the URL. [verified: research/x.md] means the claim and its URL are
in that report. [unverified] means not checked. A number with no source is
marked "needs to be measured". Prices for other products are all unverified.

---

## 1. The product on one page

**Name: Groundwork.** The promise in the name is plain: the understanding
under the code. It is distinct from look-alike plugins named for learning
while building, such as learn-while-build [verified: research/users-market.md].
Trademark and package names are [unverified] and must be checked before launch.
The command is `groundwork`.

**One sentence for an engineer:** Build at full speed with any agent;
Groundwork keeps your pace and keeps a private record of what you can now do
without it.

**One sentence for an engineering leader:** Your team keeps shipping with
agents and stays able to own, review and debug what ships, and you can see
that it is working without seeing anyone.

**What it is:** an open-source local engine, one binary with five faces (CLI,
MCP server, hook dispatcher, a local page called the Room, an OS scheduler
entry) [research/surfaces.md, research/platform.md]. A personal record in a
local git repo outside every project tree, written only by the engine
(founder decision 1). A **codebase guide**, a folder the team commits to its
own repo (`.groundwork/`) naming the ideas the codebase depends on, where they
live and who will mentor on them, with no personal data. A paid **team
plane**: SSO, SCIM, a ciphertext-only relay, and aggregate views no server can
break down by person.

**What changes for each person:**

| Person | Before | With Groundwork |
|---|---|---|
| New hire | Reads stale docs, asks in chat, lets the agent write code they cannot explain | Learns the codebase's real ideas from the code the agent writes for them in week one, with one marked line to write themselves |
| Engineer | Delegates debugging, loses the skill without noticing | Calls the cause before the agent does, a few times a week, and sees what they can do unaided |
| Senior | Mentors one junior at a time, by hand, in review | Writes a handful of questions about their area once; they reach every new person who touches it |
| Reviewer | Approves agent diffs no one fully understands | Sees an author-written walkthrough on the PR when the author chooses to add one |
| Manager | Hears "the bench is hollowing out" and has no measure | Sees team-level delayed unaided results, coverage risk by codebase area, and nothing about any one person |

**What it will not do, ever, on any plan:** show any individual's answers,
grades, map, activity or weak areas to anyone else; be used for hiring or
performance ratings; sell or mine records; add points, streaks or
leaderboards; slow the build.

---

## 2. The problem, for teams

The evidence that agents can erode skill is strong for individuals.

- Shen and Tamkin's randomised trial (52 developers): the AI group scored 50%
  on an immediate quiz against 67% by hand, was not significantly faster, and
  the biggest gap was debugging. Those who let the AI debug scored 24%; those
  who asked how generated code worked scored 86% [verified:
  https://www.anthropic.com/research/AI-assistance-coding-skills]. Pattern
  groups were 2 to 7 people, so those numbers are suggestive.
- METR: developers were 19% slower with AI but believed they were 20% faster
  [verified: https://arxiv.org/abs/2507.09089].

For teams the problem compounds, and nobody in the loop can see it.

- 38% of engineering leaders say AI cut the mentoring juniors get [verified:
  https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles].
- 85% of juniors say AI improved their understanding; 16% of seniors say
  juniors fully understand the AI code they submit. This is a vendor survey
  [verified: https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/].
- Bainbridge's ironies of automation: the operator keeps the rare, hard
  failures and loses the practice for them [verified:
  https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf]. For a team,
  that is the 2am incident in agent-written code no one owns.

The team problem in one line: **velocity is visible and ownership is not.** A
team can see PRs merged. It cannot see whether anyone could fix them. Managers
reach for the only tools they have, which are activity counts, and engineers
rightly read those as surveillance.

---

## 3. Users and wedge

### 3.1 Who it is for

1. **Engineers on teams that use agents daily.** Juniors first, then seniors
   moving into a new area or stack [research/users-market.md].
2. **New hires in their first 90 days.** A new codebase, an agent that can
   write in it, and nobody with time to explain it.
3. **Senior and staff engineers who own areas** and want others able to cover.
4. **Engineering managers and directors.** They pay, and need evidence the
   agent rollout is not hollowing out the team.
5. **Platform and developer-experience teams.** The likely champion and
   installer.

### 3.2 Who it is not for

Not for hiring or performance review: a record that can hurt you stops being
honest [research/users-market.md], so this is in the team contract. Not for
mandatory compliance training, which is the opposite of this design.

### 3.3 The wedge

**Free for individuals, adopted bottom up, paid for when a team wants the
aggregate view.** (1) An engineer installs Groundwork alone; it works fully,
offline, with no account. (2) Someone commits a codebase guide, free, and now
every new person who opens the repo with any agent gets questions about this
codebase's own ideas. (3) The team buys the team plane for SSO, the coverage
view and the onboarding outcome report. Step 2 is the key: the guide lives in
the team's repo and works across every agent its people use, which a vendor's
built-in learning mode does not.

### 3.4 Why vendors are unlikely to build this

The assistants' learning modes are free and session-bound: Claude Code's
Learning style with `TODO(human)` spots [verified:
https://code.claude.com/docs/en/output-styles], ChatGPT Study Mode, Gemini
Guided Learning [verified:
https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/].
None keeps a record, schedules review or measures unaided skill. A vendor is
less likely to ship a record and guide that span its competitors' agents, with
a privacy design where the vendor cannot read the data. That is a bet
[unverified].

---

## 4. Principles

Every later section follows these. Each traces to a research report.

1. **The build always wins.** Every moment is skippable at once and never
   blocks the agent, except a "your line" the engineer accepted.
2. **Think first where it matters most:** predict, explain back, and above all
   call the cause before the agent diagnoses [research/learning-science.md L1, L4].
3. **Skill is unaided, delayed and in a new instance.** A level never rises in
   the session where the agent wrote the code [L2].
4. **Silent on what you know.** Support fades per topic from evidence, never by
   job title [L10].
5. **Real code, this week,** from the engineer's work or the team's guide.
6. **One record across every agent,** owned by the engineer, in local git.
7. **Graded by the engine, not a prompt:** sealed keys, tests for your line.
8. **No pressure mechanics, said out loud:** 3 reviews a day, one reminder,
   no streaks or points (Hanus and Fox 2015 [verified:
   https://dblp.org/rec/journals/ce/HanusF15]).
9. **Privacy is structural.** No admin key to individual records exists.
10. **Measure delayed outcomes, never satisfaction** [verified:
    https://openlab.citytech.cuny.edu/gamelab/files/2023/01/Deslauriersa-et-al-2019.pdf].

---

## 5. The core learning loop

The loop is the same for an individual and for a team member. The team adds
better source material (the codebase guide) and better people (mentors). It
never adds visibility.

### 5.1 The seven moments

| # | Moment | When | What the engineer does | Evidence |
|---|---|---|---|---|
| 1 | Predict | Before a long step on a new idea | States what will happen, with confidence | Prediction and generation; Lead-and-Reveal brought perceived and actual ability closest [verified: https://arxiv.org/abs/2410.08922] |
| 2 | Your line | During a build on a not-yet idea | Writes one marked line that carries the idea; tests grade it | Generation effect d about 0.40 [verified: https://pubmed.ncbi.nlm.nih.gov/17645161/]; fading worked examples (Atkinson et al. 2003) |
| 3 | Call the cause | A test fails on an idea being learned | Names a hypothesis and a check before the agent diagnoses | Shen and Tamkin's debugging gap; Bainbridge |
| 4 | Explain back | After a step passes or at commit | Explains the change in two sentences | Self-explanation g = 0.55 [research/learning-science.md] |
| 5 | Review | Session start, at most 3 a day | Free recall, cold, no code on screen until committed | Testing effect g = 0.50, 0.69 delayed [verified: https://doi.org/10.1037/a0037559]; spacing g = 0.74 [verified: https://link.springer.com/10.1007/s10648-020-09572-8] |
| 6 | Compare | When an idea appears in a second place | Names the principle shared by two real cases | Analogical encoding [verified: https://dedregentner.owlstown.net/publications/38525-learning-and-transfer-a-general-role-for-analogical-encoding] |
| 7 | Drill | Opt-in, weekly at most | Rehearses a rare event from the team's own history | SRE Wheel of Misfortune; Kahneman and Klein [research/learning-science.md L16] |

Every moment ends with one line: `Back to: <task>. Next: <step>.` Only about
10% of programming sessions resume editing within a minute of an interruption
[verified: https://sites.cc.gatech.edu/reverse/repository/resumptionstrategies.pdf],
so the resume cue is a requirement, not polish.

### 5.2 When it asks, and when it is silent

Groundwork asks only at the agent's own breakpoints: before a long step, after
tests pass, at commit, at session end, and at session start for reviews.
Holding interruptions until a breakpoint lowers frustration [verified:
https://www.interruptions.net/literature/Iqbal-CHI08.pdf]. It goes quiet on
pressure signals (urgent, prod down, hotfix, failing deploy) and offers
"teach me this later" once. Two skips end questions for the session.

It is silent on ideas the record shows the engineer already has at an unaided
level. A senior who says "I know Postgres locking" gets one probe question. If
they get it right, the topic is placed and never asked again. This follows the
expertise reversal effect [research/learning-science.md L10].

### 5.3 Your line, on a team

"Your line" (founder decision 2) is on. On a team it has two extra rules.

- **It never lands in a PR unfinished.** The marker is a comment
  (`groundwork:your-line`). A pre-commit check and a CI check both refuse a
  commit or merge that still contains an open marker. The agent offers "write
  it for me" at any point, free.
- **It never shows up as a signal to reviewers.** Whether a line was written
  by the engineer or the agent is recorded only in the personal record. The
  commit carries no trailer and no tag. A reviewer sees normal code.

A codebase guide can also nominate lines. A senior can mark an idea as "worth
writing by hand once" (for example, the retry policy in the payments client).
When a new person builds near it, the agent offers that line as theirs.

### 5.4 Call the cause, on a team

When a test fails on an idea the engineer is learning, the agent offers once:
"Want to call the cause first?" The engineer writes a hypothesis and the check
they would run. The engine runs their check before the agent's. The agent then
shows its own hypothesis and check (cognitive apprenticeship: expert process
after the learner tries [research/learning-science.md L18]).

The team twist: when the failure is in an area the codebase guide covers, the
reveal can include the area owner's own note on how they debug it, written
once. That is mentoring at scale without the mentor in the loop.

### 5.5 Grading

Grading follows the evidence track's protocol [research/evidence.md].
Executable checks come first: tests for "your line", the engineer's own check
for "call the cause". Open answers get a sealed rubric of binary points,
written in a separate context, with its sha256 hash committed to the record
before the question is shown. A separate grader sees only question, rubric,
shown code and answer, never the teaching session, and treats the answer as
data. Every point awarded quotes the span that earns it. Every verdict accepts
"I think that grade is wrong" and regrades once. Guide items are graded the
same way.

### 5.6 What the record calls skill

The record reports six constructs separately, never one combined score: code
reading, debugging, design judgment, explaining a change, transfer, and
calibration [research/evidence.md]. Each topic has a level that can go down:
Seen, With help, Unaided, Transfers. Same-session work caps at With help.
Unaided needs a delayed, sealed, cold item. Transfers needs success on a case
in a different place than the one practised.

A hidden audit bank per topic, which the teaching agent never sees and never
uses for practice, measures whether practised scores are inflating [verified:
https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/].
The engineer always sees the gap between practised and audit results.

---

## 6. The codebase guide

This is the core team feature, and it is free.

### 6.1 What it is

A folder in the project repo, reviewed in PRs like any other code.

```
.groundwork/
  guide.toml          # areas, owners willing to mentor, settings
  ideas/
    payments-idempotency.md
    event-ordering.md
    tenant-isolation.md
  items/              # questions by seniors; rubric points encrypted (6.2)
  drills/             # incident rehearsals built from postmortems
```

Each idea file names: the idea in one sentence, the paths where it lives, why
it matters here, the common mistake, and who is willing to help. Example
heading set: "What it is", "Where it lives", "How it breaks", "Ask".

### 6.2 Where the answer keys go

Keys must not sit readable in the working tree. They also cannot be hidden
from an agent with shell access, and an agent can always rebuild an answer
from the code [research/platform.md]. The aim is to keep keys out of the
asking context, not to make them secret.

- Guide rubric points are encrypted with `age` to a team guide key (the
  platform track recommends age and libsodium). The engine keeps decrypted
  copies in the personal sealed store, never in the project tree.
- Without the team plane, guide items ship without points and the engine
  writes the rubric in a separate context, as for personal items.
- A guide's hidden audit bank is never committed. With the team plane it lives
  on the relay as ciphertext; without it there is none, and the product says so.

### 6.3 How a guide gets written

Nobody will write a guide from a blank page. Groundwork drafts one.

1. `groundwork guide draft` reads the repo (structure, ADRs, READMEs, the most
   changed files, past incident postmortems if the team points to them) and
   proposes ten ideas with paths.
2. A senior edits and deletes. The draft is a PR, reviewed by the team.
3. Owners add one "how I debug this" note per idea, optional.
4. After each incident, `groundwork drill from <postmortem>` drafts a
   rehearsal: the symptoms as they first appeared, the logs, the question
   "what would you check first?" and the real resolution sealed as the key.

How long a useful guide takes to write needs to be measured. That is assumption
4 in section 13.

### 6.4 Onboarding with a guide

On a starter ticket, at a breakpoint, Groundwork asks about a guide idea the
ticket touched, drawn from the code the agent just wrote, with the guide's
context ("this is why we use an idempotency key here"). The onboarding plan is
a path, not a course: the guide's ideas, ordered by how often new work touches
them, shown in the engineer's own map. The engineer chooses which to grow next
(L15).

---

## 7. Every surface, and how parity works

### 7.1 Parity of outcomes: a challenge to decision 6

Founder decision 6 asks for feature parity on all surfaces. This concept
challenges it explicitly: exact feature parity is not possible. VS Code shows
MCP Apps inline only and Zed and Gemini CLI have none [verified:
https://code.visualstudio.com/api/extension-guides/mcp, https://zed.dev/docs/ai/mcp].
Copilot cloud agent supports MCP tools only [verified:
https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp].
Copilot in Visual Studio, JetBrains, Eclipse and Xcode has no hooks [verified:
https://docs.github.com/en/copilot/reference/customization-cheat-sheet]. Aider
documents no MCP [verified: https://aider.chat/docs/config/options.html].

So Groundwork commits to **parity of outcomes**: every surface runs the full
loop (question, answer with confidence, grade, your line, review, map) in plain
chat text plus a CLI call. Richer UI is detected at run time and only makes the
same action faster. A scripted conformance session per agent per release
proves it, and the results are published. This matters more for a team: a team
of fifty uses several agents, and a guide that worked in one would split it.

### 7.2 The common floor

- An AGENTS.md block of about three lines that points to the tool. AGENTS.md
  lists 23 agents that read it [verified: https://agents.md]. Claude Code reads
  it only when there is no CLAUDE.md [verified:
  https://code.claude.com/docs/en/memory.md], so the installer writes the same
  three lines into CLAUDE.md when one exists.
- A skill at `.agents/skills/groundwork/`, copied to `.claude/skills/` and
  `.cline/skills/` where needed [research/surfaces.md].
- An MCP server whose core tools work with tools alone.
- A CLI for anything the agent cannot do through MCP.

### 7.3 Surface table

Tiers: T0 text and CLI only; T1 hooks (breakpoint detection); T2 native forms
(MCP or ACP elicitation); T3 cards (MCP Apps). "Room" is the local page.

| Surface | Tier | How breakpoints are found | Answer path | Notes |
|---|---|---|---|---|
| Claude Code CLI, desktop, IDE | T1 + T2 | Hooks; turn end can continue the turn | Elicitation form, or chat | No MCP Apps in Claude Code [research/surfaces.md] |
| Claude Code on the web and mobile | T1 + T2, cloud | Hooks | Chat; phone via the Claude app Code tab [verified: https://code.claude.com/docs/en/mobile.md] | Disk not kept; visitor mode (7.4) |
| Codex CLI, IDE | T1 + T2 | Hooks [verified: https://learn.chatgpt.com/docs/hooks] | Elicitation or chat | Reads SKILL.md [verified: https://developers.openai.com/codex/skills] |
| Codex app and cloud | T1, cloud | Hooks | Chat; ChatGPT mobile | Containers cached up to 12 hours [verified: https://developers.openai.com/codex/cloud/environments] |
| Cursor editor | T1 + T2 + T3 | Hooks, followup_message [verified: https://cursor.com/docs/agent/hooks] | Form or card | |
| Cursor cloud agents | T1, cloud | Hooks | Chat; Cursor web and iOS | Isolated VMs [verified: https://cursor.com/docs/cloud-agent] |
| Copilot in VS Code | T2 + T3 | Instruction-driven | Form or inline card | |
| Copilot CLI | T1 | Hooks [verified: https://docs.github.com/en/copilot/concepts/agents/hooks] | Chat | |
| Copilot cloud agent | T1 tools only, cloud | Hooks | PR comment and chat; GitHub Mobile | 59 minute sessions [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent] |
| Copilot in JetBrains, Visual Studio, Xcode, Eclipse | T0 | Instruction only | Chat and CLI | No hooks |
| Gemini CLI | T1 | Hooks [verified: https://geminicli.com/docs/hooks/reference/] | Chat | No elicitation documented |
| Devin Local (formerly Windsurf) | T1 | Hooks [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] | Chat | Rename per press [unverified] |
| Zed agent | T0 | Instruction only | Chat | ACP elicitation only for external agents [research/surfaces.md] |
| JetBrains ACP agents | T2 | Instruction | ACP form [verified: https://www.jetbrains.com/help/ai-assistant/acp.html] | |
| Amp | T1 + native UI | Plugin hooks, continue [verified: https://ampcode.com/docs/customize/plugins] | Plugin confirm and input; Amp mobile | |
| Kiro | T1 | Hooks [verified: https://kiro.dev/docs/hooks/] | Chat | |
| OpenCode, goose, Roo, Cline, Junie | T0 or T1 | Varies | Chat | Probe each [unverified] |
| Aider | T0 | None | Chat plus CLI; your line works as a comment | No MCP |

Every row is tested by the conformance suite before the table is published.
Rows not yet tested say so.

### 7.4 Cloud agents and shared repos: a second challenge, to decision 1

Decision 1 keeps the record in local git with no remote unless asked. A cloud
session's disk is thrown away, so a record written there is lost
[research/platform.md]. The surfaces track proposed "visitor mode": attempts
travel in the project branch under `.learning-inbox/` for later import.

On a team that has a flaw: **the project branch is visible to teammates.** An
inbox file in a PR would show a colleague's misses to every reviewer. So:

1. The cloud session asks once: carry nothing (default in a team repo), an
   encrypted inbox, or the team relay.
2. An inbox file is sealed with `age` to the engineer's own public key.
   Teammates see a blob and a file name.
3. CI and a pre-merge hook refuse any merge containing `.learning-inbox/`. The
   engine imports and deletes it on the next local pull.
4. With the team plane, sealed attempts go to the relay and the branch is
   untouched.

The full record still lives only in local git and nothing leaves unless the
engineer chooses. Whether engineers accept even an encrypted file in a shared
branch needs to be measured.

### 7.5 Packaging

All adapters are generated from one manifest: a Claude plugin, a Codex plugin,
a Cursor plugin, a Gemini extension, a Kiro power, an Amp plugin, an OpenCode
npm package, a Devin plugin and a Cline MCP listing [research/surfaces.md].
For teams, there is one more: `groundwork team install`, a script a platform
team can run in a dev container or a golden image. It installs the engine and
the adapters for whatever agents are present. It does not turn anything on for
the engineer: first run still asks the three onboarding questions.

---

## 8. The experience, end to end

### 8.1 First install, alone

```
$ pipx install groundwork     # or npx, brew, a plugin directory
$ groundwork init
```

Three questions with defaults, no account [research/experience-design.md]:
how much to ask (Off, Light, Standard by default, Deep); a daily reminder time,
used only if something is due (default: none); and where the record lives
(default `~/groundwork-record`, local git, no remote). Then: "Done. I will stay
quiet until a natural break in your work." The first real question is the
tutorial.

### 8.2 First question

The agent finishes a retry wrapper and tests pass. At that breakpoint:

```
Quick one, since retries are new in your record (skip any time):
If the payment call times out after the server committed, what does
this wrapper do on the second attempt? How sure are you: sure, fairly
sure, guessing?
```

The verdict comes in a fixed order: verdict word, what was right as
information, the missing piece at `path:line`, when it comes back, the way
back. Then `Back to: retry wrapper. Next: wire it into checkout.` The map
shows its first topic at Seen.

### 8.3 A normal day

Session start: "2 reviews due. About 3 minutes. Now, later, or skip." In the
build: one prediction on a new idea, one explain-back at commit, and when a
test fails on a learning idea, one offer to call the cause. A hotfix with the
word "urgent" makes Groundwork go silent, with one "teach me this later" at
the end. The optional reminder comes at the chosen time, only if something is
due, never while the engineer is at the machine. Most of the day the engineer
sees nothing.

### 8.4 A week later

The map has visibly changed: several topics at Seen, two at With help, the
first at Unaided after a cold review five days on. A topic that slipped back is
shown as fact plus next step, never red, never pushed. "Sure and wrong" items
come first, framed once as the most useful kind of miss [verified:
https://doi.org/10.1146/annurev-psych-010416-044022]. Calibration stays hidden
until there are enough delayed items: "too few answers to tell".

### 8.5 A new hire's first month on a team

Day 0: nothing. Groundwork is never a requirement in the welcome email.

Day 1: the dev image has Groundwork installed. First run asks the three
questions and a fourth: "This repo has a codebase guide. Use it for questions?
Yes (default) / No." There is no line about the manager, because the manager
sees nothing.

Week 1: starter tickets. Questions come from guide ideas the agent touches.
One "your line" in the idempotency code, nominated by the payments owner. The
tests fail, the new hire asks for a hint, the tests pass.

Week 2: the Room shows the guide as a path: twelve ideas, four Seen, two With
help. They pick tenant isolation to grow next.

Week 3: an opt-in drill from last quarter's queue backlog incident, graded on
process: what they checked first, in what order.

Week 4: they choose to send a mentor snapshot (9.4) to their onboarding buddy
and talk through the two ideas still at With help. It is the first time anyone
has seen their record, and they chose it.

### 8.6 Code review

When an author opens a PR, the agent may offer: "Add a two-sentence
walkthrough of why this works, in your words?" If written, it goes into the PR
description under "Walkthrough", as ordinary text a person wrote. The personal
record grades it privately as an explain-back. The reviewer sees the text and
nothing else: no grade, no level. Groundwork never prompts reviewers to demand
walkthroughs and a team cannot make them mandatory through the product.
Whether authors add them voluntarily needs to be measured.

### 8.7 End of a project, or leaving an area

`groundwork wrap` gives a private summary: ideas met, what is now Unaided,
what is still With help, and the reviews still to come. Before rotating off an
area, `groundwork handover <area>` drafts guide entries for the ideas the
engineer built most, for them to edit and commit. Their knowledge goes into the
shared guide. Their record stays theirs.

### 8.8 Leaving the company

The record is the engineer's local git repo and they keep it. A team policy can
turn off storing code excerpts per project, so the record holds only paths,
topic names and the engineer's own words [research/platform.md 11.4]. That is
the one place policy reaches into a record, and it removes data. The relay
deletes the leaver's ciphertext. Guide items they wrote stay in the repo.

### 8.9 A manager's month

The manager opens the team view (9.3). They learn that "event ordering" has low
demonstrated coverage and ask a senior to add a drill. They cannot learn who
is weak at it.

---

## 9. Privacy, and why this is never surveillance

### 9.1 The rule

No one but the engineer can see their individual record: not a manager, an
admin, or Groundwork the company. Records live on the engineer's machine, sync
is end-to-end encrypted with device-generated keys, and no admin key exists
[research/platform.md]. If managers could see individuals, engineers would
answer for the manager and the record would stop measuring learning. That is a
reasoned claim from self-determination theory; it needs to be measured.

### 9.2 What admins can and cannot do

| Control | Allowed | Notes |
|---|---|---|
| Deploy the engine and adapters | Yes | Install only. First run still asks the engineer. |
| Require the team relay or a self-hosted relay | Yes | Blocks the public relay. |
| Pin the relay region | Yes | Ciphertext only, but metadata is still personal data under GDPR [unverified legal reading]. |
| Set defaults for the dial, cap and reminder | Yes, as defaults | The engineer can change each one. Cannot set the cap above 3. |
| Turn excerpt storage off for a project | Yes | Removes data from records. |
| Turn telemetry off for everyone | Yes | |
| Turn telemetry or team aggregates on for anyone | No | Opt-in per person. |
| See who has Groundwork turned on | No | Seat counts come from SCIM, not from use. |
| Read or export records | No | No key exists. |
| Lower the group-size floor below 5 | No | Default 8 [design choice, needs to be measured]. |

### 9.3 What the team view shows

Each engineer who opts in has their engine compute a few numbers locally and
submit them through Prio3 over DAP; privacy holds if one of the two
aggregators is honest [verified: https://docs.divviup.org/how-it-works]. Views
appear only above a minimum group size, as in Microsoft Viva Insights, whose
floor cannot go below five [verified:
https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings].
For the team as a whole it shows:

1. **Delayed unaided accuracy, by construct**: share of cold reviews correct
   at 7 or more days, for debugging, code reading and the rest, over months.
2. **Coverage risk by guide area**: levels per idea as bands (low, medium,
   high), with noise added before release. "Which parts of our codebase does
   too little of the team understand without the agent?"
3. **Onboarding outcome**: for a joining cohort above the floor, share of
   guide ideas at Unaided by day 30 and day 90.
4. **The audit gap**: practised against hidden audit results.
5. **Engagement, labelled as a guard metric only**: share of offered
   questions answered, share of due reviews done.
6. **Guide health**: ideas with no items, stale paths, no owner note.

It never shows anything per person, time spent, sessions, or which agent
anyone uses. A team below the floor gets no view; aggregates can roll up to a
department instead, and setup says so up front.

### 9.4 What an engineer can choose to share

- **Mentor snapshot**: a signed copy of chosen topics, sent to one named
  person. The UI says "once sent, you cannot take it back".
- **Proof pack**: chosen sealed items, answers, grades with quoted spans and
  rubric hashes [research/evidence.md I.2]. Evidence, not a level.
- **Ownership claim**: "list me as able to cover payments", volunteered into
  the guide's owners list like a CODEOWNERS entry.

The team contract forbids requiring any of these, for example in a
performance review. Contracts alone do not stop pressure, so the product never
shows anyone whether a person has shared, and every proof pack says on page
one that it is a self-selected sample, not a measure of the person.

### 9.5 Law and works councils

EU monitoring law and works councils may restrict even aggregate views, and
the EU AI Act may class learning-outcome grading or worker evaluation as
high-risk [unverified: https://casrai.org/news/ai-act-high-risk-classification].
Legal review comes before the team plane ships. It ships with a plain data
sheet for works councils listing what each component sees, metadata included,
modelled on Obsidian's list for its sync server [verified:
https://obsidian.md/help/sync/security].

---

## 10. Architecture

### 10.1 Layers

- **L0 Record format**, an open spec: append-only event files with ULID
  names in a per-user git repo. Maps, schedules and the due list are derived,
  never committed. Devices only add different files, so a union merge never
  conflicts [research/platform.md].
- **L1 Local engine**: the only writer. Holds sealed rubrics, grades, enforces
  the cap and the single reminder, imports inboxes, and signs commits with SSH
  keys [verified:
  https://docs.gitlab.com/user/project/repository/signed_commits/ssh.html].
  `groundwork check` verifies the hash chain and rubric commitments.
- **L2 Device link**: QR-paired, keys on devices only, Tailscale pattern
  [verified: https://tailscale.com/kb/1232/derp-servers]. The computer sends
  due cards with no answer keys; the phone returns encrypted answers.
- **L3 Blind relay** (opt-in): encrypted mailbox and push sender, item keys
  as in Standard Notes [verified:
  https://standardnotes.com/help/security/encryption].
- **L4 Team plane** (paid): SSO, SCIM, region-pinned or self-hosted relays,
  two DAP aggregators, the guide key service, the team view.

The codebase guide is plain files in the team's repo, read by L1.

### 10.2 Guide key service

With the team plane, the engine fetches the team guide key after SSO into the
personal sealed store, with rotation on edits and departures. It hides keys
from the asking context, not from a person reading their own sealed store, and
the docs say so. Anyone who cheats only cheats their own private record. When
no one is watching, there is little reason to cheat.

### 10.3 Phone

The phone is optional and never holds the record. The first reminder is a
recurring calendar event with no content (`groundwork reminder set`), because
web push needs a sender server and local scheduled web notifications never
shipped [verified:
https://developer.chrome.com/docs/web-platform/notification-triggers]. A phone
review costs one tap to send the encrypted answer back (decision 4). Grading
waits until the computer imports it; how much that delay hurts needs to be
measured. Reminders carry a count, never question text.

### 10.4 Telemetry

Off by default. Opt-in product aggregates use the same Prio3 over DAP path.
Code, answers, rubrics and topic names are never collected. Admins can switch
telemetry off for everyone, never on for anyone.

### 10.5 Measuring whether it works, inside one team

Within-person randomisation by topic [research/evidence.md J.1]: each new
topic gets a technique or not by a seeded coin, and each engine compares
delayed unaided results for that person. Teams can opt in to aggregating these
estimates through DAP, a team-level "is this helping us?" with no individual
data. Small teams see "not enough data to tell"; the size needed must be
measured.

---

## 11. Business model

### 11.1 Free, forever, for individuals

The engine, adapters, record, device link, codebase guide and drafting tools
are open source and free. A team that never pays still gets the full loop and
a shared guide.

### 11.2 Paid

| Plan | For | What it adds | Price |
|---|---|---|---|
| Personal sync | Individuals | Hosted blind relay, phone push, encrypted backup | Needs to be measured |
| Team | Teams of 8 or more | SSO, SCIM, team relay, guide key service, encrypted guide audit bank, team view, onboarding outcome report, drill authoring from postmortems, support | Per seat; needs to be measured |
| Enterprise | Large orgs | Self-hosted relay and aggregators, region pinning, data sheet and DPA, works council pack, conformance results for their agent mix | Contract |
| Education | Universities, bootcamps | Course guides; cohort aggregates above the floor | Licence; needs to be measured |

Price anchors are [unverified]: Pluralsight Skills about $399 to $779 per user
per year, CodeRabbit about $24 to $48 per developer per month
[research/users-market.md]. These show budgets exist for skills and review
tools, not what this product should charge.

### 11.3 Ruled out

Selling records, ads, hiring products, per-person reports, and any feature
that makes an individual visible to an employer. These are in the terms, and
the architecture makes most of them impossible rather than merely forbidden.

### 11.4 Why the team plan sells

The buyer gets an onboarding outcome measured days later without the agent, a
coverage-risk view of their codebase, and evidence the agent rollout is not
hollowing out skill. The engineer gets a free tool and a guarantee their
manager cannot see them. Both must hold: if engineers distrust it, they skip
every question and the team view is empty.

---

## 12. What ships, and when

### v1: the individual loop and the guide (free)

- Engine (CLI, stdio MCP server on both protocol revisions, hook dispatcher,
  Room, scheduler entry), record spec, sealed rubrics, separate grader, quoted
  spans, disputes.
- Moments 1 to 5, the cap of 3, one reminder, the dial, two-skips rule and
  pressure signals.
- Adapters that pass conformance at launch: Claude Code, Codex CLI, Cursor,
  Copilot (VS Code, CLI), Gemini CLI. Others marked "text tier, untested".
- Guide format, `guide draft`, unsealed guide items, open-marker checks.
- Cloud sessions: ask once, carry nothing in team repos by default, encrypted
  inbox optional, merge check.
- Retention measures from day one, on device: share of offered questions
  answered, share of due reviews done, 30-day return.

### v2: phone, sync, the team plane

- Device link and phone review pack with one-tap send.
- Blind relay, personal sync.
- Team plane: SSO, SCIM, team relay, guide key service, DAP aggregation, team
  view items 1, 2, 5 and 6. Data sheet. Legal review done first.
- PR walkthrough offer. Mentor snapshot. Ownership claim.
- Moment 6 (compare across two places) and the hidden audit bank.

### Later

- Onboarding outcome report, drills from postmortems, opt-in "check the
  agent" drills on scratch branches [research/learning-science.md L17], native
  phone app, team efficacy estimate, education plan.
- A preregistered randomised trial with a delayed, unaided, blind-graded
  held-out test and a speed guard [research/evidence.md]. Until it reports,
  marketing says what the product does, never that it makes people better.

---

## 13. The five riskiest assumptions, and the cheapest test for each

### 1. Engineers will trust a tool their employer pays for

If engineers think the team view can identify them, they skip or answer for
the manager. **Cheapest test:** show the data sheet and team view mock to ten
engineers at companies using agents. Ask what their manager could learn about
them, then whether they would turn it on. Set the pass threshold first.

### 2. Managers will pay for a view with no individuals in it

An aggregate-only view may feel like paying for nothing. **Cheapest test:**
five manager interviews [research/platform.md E8] with the 9.3 mock: what
decision would you make with it this quarter? Then a "talk to us" team plan
button on the existing marketing site, counting clicks against visits.

### 3. Engineers will answer questions at all, at work, under delivery pressure

People say they want to learn, then skip every question
[research/users-market.md]. **Cheapest test:** ten engineers use the existing
skill for two weeks on real work. Measure on device the share of offered
questions answered and of due reviews done, plus a one-line felt-cost rating
per session, since interrupted people can work faster but feel more stress
[verified: https://www.ics.uci.edu/~gmark/chi08-mark.pdf].

### 4. Seniors will write and maintain a codebase guide

Without a guide, a team gets only the free individual loop. **Cheapest
test:** run a hand-made `guide draft` (prompt plus template) on two real repos
with one senior each. Time the edit to a committable guide; check a month later
whether it was updated. If seniors will not spend the time, the guide must be
fully generated, with seniors only approving.

### 5. Delayed unaided gains are big enough to see in a team view

If the effect is small, the team view shows noise. **Cheapest test:**
within-person randomisation by topic for the test 3 engineers who continue past
four weeks [research/evidence.md J.1]. It will not be precise; it shows whether
an effect is plausibly visible and how large a team must be to show a trend.

---

## 14. Open questions

The group floor default (8 proposed; Viva's minimum is 5); whether a guide
audit bank can exist at all; how to run conformance across 20 or more agents.

---

## 15. Founder decisions: how this concept treats each

| # | Decision | Status here |
|---|---|---|
| 1 | Local git record, no remote unless asked | Kept. Clarified for cloud sessions (7.4): an encrypted inbox or the team relay, each only if the engineer chooses, and never a readable file in a shared branch. |
| 2 | Your line is on | Kept. Team rules added: open markers block merges; authorship is never visible to reviewers; guides can nominate lines. |
| 3 | At most 3 due reviews a day | Kept. Admins cannot raise it. |
| 4 | One tap on the phone where no-tap is impossible | Kept, for sending a phone answer back. |
| 5 | Letter shortcuts off by default | Kept on every UI Groundwork draws. |
| 6 | Feature parity on all surfaces | Challenged with evidence (7.1). Replaced with parity of outcomes, proven by a published conformance suite. |
| 7 | At most one reminder a day at a chosen time | Kept. Admins can set a default time, not force a reminder on. Reminders stop after three are ignored. |
