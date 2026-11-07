# Concept: Unaided, a learning companion fed by your coding agents

Status: product concept, round 2. Angle: a dedicated companion app (desktop,
web, phone) that turns the user's own codebase and agent history into a
personal training ground. The agents feed it.

Inputs: `design/product/research/` and, as evidence only, the earlier round in
`design/learning-experience/`.

Tags: [verified: URL] was checked in this round's research, which cites the URL.
[unverified] was not. A number with no source is "needs to be measured".

---

## 1. The concept in one page

**Name:** Unaided. Working name. A trademark and package-name search has not
been done [unverified].

**Promise, one sentence:** Build at agent speed, and Unaided shows you, and
grows, what you can do without the agent.

**What it is.** Two halves that share one record.

1. **In the build (thin).** A skill, an MCP server, hooks and a CLI that every
   coding agent can load. They do three things inside real work: ask the user
   to predict or diagnose first at the agent's own breakpoints, leave one
   marked "your line" for the user when an idea is new to them, and log what
   happened. They never block the build.
2. **The companion (deep).** A local app on desktop, in the browser and on the
   phone. It reads the record and the user's own git history and turns them
   into a training ground: due reviews, drills replayed from the user's real
   bugs, reading drills on code the agent wrote this week, short explainers
   given after an attempt, and a skill map that can go down as well as up.

**Why a companion and not only a plugin.** The research says the skill that
erodes most is the one the agent now does: diagnosis. In Shen and Tamkin's
trial the largest gap between the AI group and the hand-coding group was on
debugging, and users who let the AI debug scored 24% [verified:
https://www.anthropic.com/research/AI-assistance-coding-skills]. Real work
supplies few repetitions of diagnosis and the agent usually takes them. A plugin
inside the session can only ask about the bug in front of the user. A
companion can replay last month's bug, in a scratch copy, days later, with the
agent switched off. That is practice the session cannot give, and it is also
the honest measure: delayed, unaided, on a new instance (learning-science L2).

**Who it is for first.** Junior engineers who build with agents every day, then
seniors moving into a new domain (users-market ranking).

**The wedge.** "Your real bugs, replayed." Every user already has a git history
full of fixes. Unaided turns a fix commit with a test into a drill: here is the
failing test from the commit before the fix, find the cause before you look.
No competitor in the users-market report does this. The learning modes inside
the assistants keep no record and schedule nothing [verified:
https://code.claude.com/docs/en/output-styles]. Community plugins such as
VibeWise slow the build and have no spaced repetition [verified:
https://github.com/nykooi1/vibe-wise]. Learning platforms use made-up exercises.

**What it refuses to be.** No streaks, points, badges or leaderboards
(learning-science L14). No hiring use. No manager view of an individual. No
selling of records. No network by default.

---

## 2. Users and jobs

### 2.1 Segments in order

| Order | Segment | Job they hire it for | Why this order |
|---|---|---|---|
| 1 | Junior engineers using agents daily | "Prove to myself I can debug and read this code without the agent." | Pain is personal and daily. Privacy sells. Senior doubt is documented: in a vendor survey 16% of seniors say juniors fully understand the AI code they submit [verified: https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/]. |
| 2 | Seniors in a new domain | "Learn this new stack while I ship in it, without being talked down to." | Closest to the Shen and Tamkin setting. The silence rule (only engage on new ideas) is built for them. |
| 3 | Teams | "Rebuild mentoring that AI took away, without surveillance." | Budget exists. 38% of engineering leaders say AI cut the mentoring juniors get [verified: https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles]. |
| 4 | Career switchers and bootcamp graduates | "Show I can engineer." | Real need, shrinking channel. |
| 5 | Students and educators | "Use AI in the course without losing the learning." | Reach and credibility, slow money. |
| Never | Hiring | | A record used to judge people stops being honest. |

### 2.2 The user's three questions

- "Am I getting better, or is the agent?" The map counts only delayed, unaided,
  new-instance results, and shows the gap to a hidden audit set.
- "Will this slow me down?" No. Every question skips at once, the agent keeps
  building, and slow practice lives in the companion at a time the user picks.
- "Who sees this?" Only the user. Anything shared is a pack the user sends.

---

## 3. The learning loop, step by step, with the evidence

The loop has two rings. The inner ring runs inside the build. The outer ring
runs in the companion, days later.

```
INNER RING (in the build, any agent)        OUTER RING (companion, later)
1 Notice a new idea                         6 Review: free recall, 3 a day max
2 Predict or diagnose first                 7 Drill: replay a real bug, unaided
3 Your line                                 8 Read: trace code the agent wrote
4 Explain back at the breakpoint            9 Explainer, only after an attempt
5 Log the event, seal the keys             10 Map: per-topic level, can go down
```

### 3.1 Inner ring

**Step 1. Notice a new idea.** The engine keeps a per-topic level for each user.
When the agent is about to use an idea the user has not shown they know, it
may engage. On ideas the user already holds, it stays silent. Evidence:
expertise reversal, support helps novices and hurts experts (learning-science
L10). A self-declared expert is placed with one probe question.

**Step 2. Predict or diagnose first.** At an agent breakpoint (before a long
step, when a test fails, before commit) the agent asks one question: "What do
you expect this migration to do to existing rows?" or "Test failed. Your
guess at the cause, in one line?" The agent keeps working in the meantime where
the surface allows. Evidence: generation effect about d = 0.40 [verified:
https://pubmed.ncbi.nlm.nih.gov/17645161/]; Lead-and-Reveal brought perceived
and real ability closest together [verified: https://arxiv.org/abs/2410.08922];
interruptions cost least at task breakpoints [verified:
https://www.interruptions.net/literature/Iqbal-CHI08.pdf]. Predictions are
compared against the build's real outcome, never graded, and never move the
record (experience-design rule "mistakes are safe").

**Step 3. Your line (founder decision 2).** When an idea is new, the agent
writes the code around it and leaves one marked line for the user:

```
# YOUR LINE (unaided): compute the retry delay with jitter. Test: test_backoff.py
```

The project's tests grade it. A hint and "write it for me" are always free and
are logged as help. The line grows into a function, then a design choice, as
the topic level rises. Evidence: fading completion problems (learning-science
L5); Claude Code's Learning style already leaves `TODO(human)` gaps [verified:
https://code.claude.com/docs/en/output-styles]. It needs no protocol, so it is
the most portable feature (surfaces 9.4).

**Step 4. Explain back.** After a step passes, at most one explain-back per
chosen task: "In two lines, why does the lock go before the read?" Same-day
explain-backs only ever confirm "with help", never unaided skill (evidence
rule). Evidence: self-explanation g = 0.55 (learning-science digest); Shen and
Tamkin's high scorers generated code and then checked understanding [verified:
https://arxiv.org/html/2601.20245v2].

**Step 5. Log and seal.** Every learning moment writes an event through the
engine. Every answer key is written in a separate context, committed by hash
before the question is shown, and released only after an `answer.locked` event
(platform section 9). A prompt alone does not hold a guardrail: CS50's own
tutor still returns code blocks despite instructions [verified:
https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/].
So the engine enforces order, not the agent.

### 3.2 Outer ring (the companion)

**Step 6. Review.** At most 3 due items a day (founder decision 3). Free recall
in a new instance: no code, no old answer and no options until the user
commits. Confidence is asked in the same action as the answer. Sure misses come
back first. Evidence: testing beats re-study, g = 0.50, and 0.69 on delayed
tests [verified: https://doi.org/10.1037/a0037559]; spaced beats massed,
g = 0.74 [verified: https://link.springer.com/10.1007/s10648-020-09572-8];
daily emailed questions for residents still showed an effect two years later
[verified: https://pubmed.ncbi.nlm.nih.gov/19375095/].

**Step 7. Drill: replay a real bug.** The companion's signature. Section 4.

**Step 8. Read.** "Here are 30 lines the agent wrote on Tuesday. What does
`merge_windows([(1,3),(2,5)])` return?" Graded by running it. Evidence:
developers spend about 58% of their time understanding code [verified:
https://xin-xia.github.io/publication/TSE17.pdf]; reading and writing are
separable skills (evidence report, Lister 2004).

**Step 9. Explainer, after the attempt.** Once the user has committed an
answer, the companion can show a short explainer built from the user's own
code, with `path:line` references and the principle named. It is never shown
first. Evidence: cognitive apprenticeship and the order effect (learning-science
L18); principle prompts give far transfer (L11). Viewing an explainer counts as
"Seen", never as skill.

**Step 10. Map.** Section 6.

### 3.3 What counts as skill

| Level | What earns it | Can it be earned in the session where the agent wrote the code? |
|---|---|---|
| Not yet | Default, or a miss on a delayed item | n/a |
| Seen | Explainer viewed, or explain-back on the same day | Yes |
| With help | Correct with a hint, or same-day | Yes |
| Unaided | Correct on a delayed, sealed, new-instance item with no help shown first | No |
| Holds | Unaided again after a longer gap, or on a transfer item | No |

A level can fall. The best level stays visible as an outline and the latest as
a fill (experience-design). Decay is shown as a fact and a next step, never
pushed as a notification.

---

## 4. Drills from your own history (the wedge)

### 4.1 Where drills come from

The agents feed the companion through three sources, all local.

1. **The record.** Every inner-ring event: predictions, your lines, explain-
   backs, test failures the agent hit and how they were fixed.
2. **Git history of the user's projects.** Commits that fix a failing test,
   reverts, and commits whose message names a bug. Read only from repos the
   user has added. Code never enters the record; the record stores a project
   id, a commit hash and paths.
3. **Agent transcripts, opt-in per agent.** Many agents keep local session
   logs. Where they do, an importer can find moments where the agent diagnosed
   a bug the user never looked at. Paths and formats differ per agent and are
   [unverified]; each importer is an opt-in adapter with its own probe test.
   The product works fully without them.

### 4.2 Drill kinds

| Drill | Built from | User does | Graded by | Construct |
|---|---|---|---|---|
| Replay a bug | A fix commit with a test | Reads the failing test in a scratch worktree at the parent commit, writes a one-line hypothesis and the check they would run, then fixes it | The commit's test passing; hypothesis checked against a sealed key naming the cause | Debugging |
| Trace | Code the agent wrote this week | Predicts an output for a given input | Running the code | Code reading |
| Spot the issue | An agent diff, with one seeded issue, scratch copy only, with consent | Finds the issue before tests run | The seeded location and a test | Checking agent output |
| Explain a change | A real commit | Writes the commit's "why" for a teammate | Sealed rubric of binary points, separate grader | Explaining a change |
| Compare | The same principle met in two projects | Names the shared principle and one difference | Sealed rubric | Transfer |
| Design call | A real decision point from the record | Picks and justifies an option before seeing what was done | Sealed rubric, plus "what happened next" from history | Design judgment |
| Rehearsal (opt-in) | A replayed incident from the user's history | Talks through triage steps in order | Process rubric | Operating in production |

Evidence for the set: the six constructs and their separate reporting come from
the evidence report (code reading, debugging, design judgment, explaining a
change, transfer, calibration). Rare high-stakes skills are best rehearsed in
simulations built from one's own history (learning-science L16, SRE Wheel of
Misfortune). Seeded issues follow L17, which is marked speculative.

### 4.3 How a replay drill is built (mechanism)

1. The miner scans added repos for commits where a test went from failing to
   passing, using the test files touched in the commit.
2. For each candidate, in a throwaway worktree, it checks out the parent and
   runs only that test. If it fails and passes again on the fix commit, the
   candidate is reproducible.
3. A separate model context (Section 8.3) reads the diff and writes the sealed
   key: the cause, the location and the principle, as binary points. The key is
   committed by hash before the drill is ever offered.
4. The drill is scheduled for the topic it trains, never in the same week the
   user met the bug, so it is a delayed item.

How many fix commits in a typical repo reproduce this way needs to be measured.
It is the second riskiest assumption (Section 13).

### 4.4 A replay drill, as the user sees it (any surface, plain text)

```
Drill: a real bug from payments-api, three weeks ago. Agent off.
The test below failed before commit 4f2a1c. It now runs in a scratch copy.

  test_refund_twice_is_noop  FAILED  expected 1 refund, got 2

1) Your hypothesis, one line:
2) The check you would run first:
3) How sure are you? sure / fairly / guessing / don't know

Skip costs nothing. Hint is free and marks this "with help".
```

After the answer locks: verdict word first, what was right as information, the
missing piece with `path:line`, when the topic returns, then the way back
(experience-design feedback order). The user may then fix it in the scratch
copy; the commit's test is the verdict.

---

## 5. Surfaces and parity

### 5.1 Founder decision 6, challenged with evidence

Founder decision 6 asks for feature parity on all coding surfaces. Exact
parity of mechanism is not possible. MCP Apps do not render in Claude Code
[verified: https://modelcontextprotocol.io/extensions/apps/overview.md]; Zed's
own agent and Gemini CLI document no elicitation [verified:
https://zed.dev/docs/ai/mcp; https://geminicli.com/docs/tools/mcp-server/];
Aider documents no MCP [verified: https://aider.chat/docs/config/options.html];
Copilot cloud agent supports MCP tools only [verified:
https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp].

The concept keeps the intent and changes the definition: **parity of
outcomes**. Every surface can run the full loop: question, answer with
confidence, grade, your line, review, drill, map. The floor is plain chat text
plus a CLI call. Richer UI is a faster door to the same action, detected at
run time. A conformance suite proves each row per release (surfaces 10.6).

The companion makes parity easier, not harder. The deep work (drills, map,
explainers) happens in one app the product owns, so it is identical whatever
agent fed it. Each agent only needs the thin inner ring.

### 5.2 What each agent surface does in the inner ring

| Surface | How the inner ring runs | Native ask | Where review and drills happen |
|---|---|---|---|
| Claude Code CLI, desktop, IDE | Skill in `.claude/skills`, MCP tools, hooks | MCP elicitation [verified, surfaces 8.7] | Companion; or `unaided review` in chat |
| Claude Code web and phone | Same, visitor mode (5.4) | Cards [verified, surfaces 8.7] | Companion on phone; chat |
| Codex CLI and app | Skill in `.agents/skills`, MCP, hooks [verified: https://learn.chatgpt.com/docs/hooks] | Elicitation | Companion; chat |
| Codex cloud | AGENTS.md block plus your-line markers | None | Companion after import |
| Cursor IDE and cloud | Skill, MCP, hooks [verified: https://cursor.com/docs/agent/hooks] | Elicitation; MCP Apps card | Companion; card in Cursor |
| VS Code Copilot | Skill, MCP, hooks (preview) | Elicitation; MCP Apps | Companion; card |
| Copilot in JetBrains, Visual Studio, Eclipse, Xcode | MCP tools, instructions; no hooks [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet] | Unknown | Companion; chat |
| Copilot cloud agent | Tools only, hooks subset | None | Companion after import |
| Gemini CLI | Skill, MCP, hooks [verified: https://geminicli.com/docs/hooks/reference/] | None (text) | Companion; chat |
| Devin Local and Desktop | AGENTS.md, `.agents/skills`, MCP, hooks [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] | Unknown | Companion; chat |
| Zed agent | Skill, MCP tools; no hooks | None (text) | Companion; chat |
| Amp | Skill, MCP, plugin UI [verified: https://ampcode.com/docs/customize/plugins] | Plugin UI | Companion; chat |
| OpenCode, Cline, Roo, Kiro, goose, Junie | Skill or MCP per surfaces report; several cells [unverified] | Varies | Companion; chat |
| Aider | Instruction file plus your-line markers; `unaided` CLI by hand | None | Companion |

Where hooks are missing, the agent calls the MCP tool or CLI itself from the
skill's instructions. Where MCP is missing, the agent runs the CLI. Where
nothing runs, your-line markers in code and `unaided scan` after the session
still feed the record.

### 5.3 The companion's own surfaces

| Surface | What it is | v |
|---|---|---|
| Local web | `unaided open` serves the companion on localhost from the engine. Works in any browser on the machine. | v1 |
| Chat | Every companion action has a text form any agent can drive: `unaided review`, `unaided drill`, `unaided map`. | v1 |
| Phone (paired web app) | A web app installed to the home screen, paired to the computer by QR, holding a sealed pack of due cards (5.5). | v1 |
| Desktop app | A wrapper around the same local web UI with a tray icon and OS notifications. | v2 |
| Native phone app | Local scheduled notifications, background sync through the relay if opted in. | Later |
| In-agent cards | An MCP App card on hosts that declare the UI extension, for one review at session start. | v2 |

One UI codebase serves local web, desktop wrapper and phone web app. The engine
is the only writer of the record on every surface (platform rule).

### 5.4 Cloud agents: visitor mode (founder decision 1, clarified)

Founder decision 1 says the record lives in a local git repo with no remote
unless the user asks. Cloud sessions have disks that are thrown away: Claude
Code on the web uses an isolated VM per session [verified:
https://support.claude.com/en/articles/12618689-claude-code-on-the-web];
Codex caches containers for up to 12 hours [verified:
https://developers.openai.com/codex/cloud/environments]; Copilot cloud agent
sessions stop at 59 minutes [verified:
https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent].

So in a cloud session the engine runs in **visitor mode**. It asks once, in one
line, and offers: keep new attempts as an encrypted file in the session output
for the user to carry home (default), or use the user's private remote or relay
if already set up. Your-line markers in the branch work with no consent at all,
because the local engine reads them from the merged code later. The full record
never goes into a project repo. This keeps decision 1 intact; it only says
plainly what a cloud disk cannot do.

### 5.5 Phone with no server

The phone cannot run git, so the computer remains the system of record. The
phone holds a pack and returns an outbox (platform 6.3).

- Pairing by QR; private keys never leave a device, following the Tailscale
  pattern [verified: https://tailscale.com/kb/1232/derp-servers].
- The pack carries up to 7 days of due cards and no answer keys.
- Choice and number cards can be graded on the phone after lock; open answers
  say "graded when you next sync".
- Sync is one tap, "sync phone", over the local network (founder decision 4).
  File and QR fallbacks exist.
- Drills that need code to run stay on the computer. The phone gets reviews,
  trace items with short excerpts, and confidence checks.

How much delayed grading on the phone hurts learning needs to be measured. If
it hurts a lot, that is the reason to opt in to the relay.

### 5.6 The one reminder (founder decision 7)

At most one reminder a day, at a time the user chooses, only when something is
due. In v1 there is no server, and every web push path needs a sender [verified:
https://webkit.org/blog/16535/meet-declarative-web-push/]; scheduled local web
notifications never shipped [verified:
https://developer.chrome.com/docs/web-platform/notification-triggers]. So v1
writes one recurring calendar event with no learning content ("Review time.").
The desktop app (v2) uses a local OS notification that fires only if items are
due and the user is not at the machine. Reminders stop after three are ignored,
with one line saying so (experience-design rule).

---

## 6. The skill map

The map is the companion's home screen. It answers "what can I do without the
agent?" and nothing else.

**Layout.** Six constructs as rows: code reading, debugging, design judgment,
explaining a change, transfer, calibration. Topics the user has met appear
under each, grouped by project. No combined score (evidence rule).

**Per topic:** best level as an outline, latest as a fill, last unaided date,
next due date, and the evidence behind it (the items, each linked). Every level
can be traced to sealed events.

**Two honest numbers, and only these:**

1. **Reviews due today**, at most 3. The only count in the product.
2. **Audit gap.** The difference between practised items and the hidden audit
   set (Section 8.4), shown per construct once enough items exist. Below a
   minimum count the map says "too few answers to tell".

**Calibration panel.** Appears only with enough delayed items. Uses a proper
scoring rule [verified: https://www.ucl.ac.uk/lapt/REAP_CBM.htm] and lists sure
misses for correction. "Don't know" is never counted against the user.

**First-week value.** The map must change visibly after the first few answers:
the first predictions and your lines place topics at Seen or With help on day
one, and the first delayed reviews on day two or three can move a topic to
Unaided. Whether users notice this change needs to be measured.

**Growth areas.** The user picks up to a few topics to grow in. Only those get
extra drills. Autonomy first (learning-science L15).

---

## 7. The experience end to end

### 7.1 First install

One command per ecosystem, generated from one manifest: a Claude plugin, a
Codex plugin, a Cursor plugin, a Gemini extension, an npm and a PyPI package,
and a single static binary for everything else (surfaces 10.3). Then:

```
$ unaided init
Three questions. Enter keeps the default.
1) How much learning while you build? off / light / standard / deep  [standard]
2) One reminder a day, when?  [18:30, only if something is due]
3) Where should your record live?  [~/.local/share/unaided/record, local git, no remote]
Done. Nothing else happens until your agent hits a natural pause.
Add projects for drills from your history: unaided add ~/code/payments-api
```

No account. No network call. The engine writes a three-line block into
AGENTS.md (or CLAUDE.md where that is read instead [verified:
https://code.claude.com/docs/en/memory.md]) pointing to the skill.

### 7.2 First question

The first real question is the tutorial. In a normal build, the agent reaches a
test failure and asks:

```
Test failed: test_parse_dates. Before I look: your guess at the cause, one line?
(Why: you have not worked with timezone parsing yet. Skip: say "skip".)
I am reading the stack trace meanwhile.
```

The user answers. The agent shows its diagnosis, names where the user's guess
matched, and ends: `Back to: date import. Next: fix the parser and rerun.`

### 7.3 A normal day

- **Session start, any agent.** If reviews are due, the agent offers one line:
  "2 reviews due. Do them now, or later in Unaided." Default is later.
- **During the build.** One or two moments at most: a prediction before a
  migration, a your line in the retry logic. On a pressure signal ("prod is
  down", "hotfix") the agent goes quiet and offers "teach me this later" once.
- **Evening, at the chosen time.** If something is due, one reminder. The user
  opens the companion on the phone: 3 cards, about five minutes (needs to be
  measured), confidence on each. Nothing else is suggested. No "one more".
- **Weekend, optional.** One replay drill from a bug the agent fixed two weeks
  ago, on the computer, agent off.

### 7.4 A week later

A week page, opened by the user and never pushed: topics that moved with
evidence links, one sure miss framed once as the most useful kind of miss
(hypercorrection, L12), your lines written with test results, and one drill
suggestion from the week's history that can be dismissed.

**Coming back after two weeks away:** at most 3 reviews, the rest spread over
the next days with no backlog count, and one line saying forgetting is expected.

### 7.5 End of a project

The companion offers a **project retrospective**, built from the record and git:

- The ideas the user met in this project and their levels now.
- The three bugs that cost the most agent time, each offered as a future drill.
- A **compare drill** queued for the next project that uses the same principle
  (learning-science L11).
- A **proof pack**, if the user wants one: a sealed bundle of chosen items with
  hashes, grades and grader versions, which the user can hand to a mentor. It
  is a guide, not a credential (Section 8.5).

### 7.6 A team

Teams are where the money is and where trust breaks most easily. The design
rebuilds mentoring without surveillance.

- **Drill library.** A senior turns a postmortem or a tricky fixed bug in the
  team repo into a drill, with a sealed key, and shares the drill (not any
  result) to the team library. Juniors do it in their own companion. Results
  stay in their own record. This is the mentoring channel: seniors author,
  juniors practise, nobody watches.
- **Asking for help.** A user can share one item, with their answer, to one
  named teammate. User-initiated, one item at a time.
- **Aggregates only.** The team page shows opt-in aggregates (for example,
  share of the team that completed the new-hire drills) only above a minimum
  group size of 5, following Viva Insights [verified:
  https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings].
  No admin key to individual records exists. No admin can turn on telemetry for
  anyone. A manager never sees an individual's weak areas.
- **Onboarding pack.** A team ships a starter set of drills from its own
  codebase for new hires: "here are five bugs this service has had".

---

## 8. Architecture

### 8.1 Shape

```
  coding agents (any)                     the user's machine
  ------------------                      ----------------------------------------
  skill + AGENTS.md  ---.                 unaided engine (one static binary)
  MCP tools (stdio)  ----+--> engine -->  record: local git repo (append-only events)
  hooks              ---'      |          derived cache: sqlite (schedule, map, due)
  your-line markers  ----------+          miner: reads added project repos
                               |          grader runner: headless agent or executable
                               v
                    companion UI (local web, desktop wrapper, paired phone web app)
                               |
                    optional, opt-in: private git remote, or blind relay (E2E)
```

One engine, five faces: CLI, MCP server (both protocol revisions), hook
dispatcher (`unaided hook <agent> <event>`), the local companion page, and an
OS scheduler entry (surfaces 10.2). Adapters only translate event names and
output shapes; all learning logic lives in the engine.

### 8.2 The record (founder decision 1)

- A per-user git repo outside any project tree, so one history spans projects
  and nothing leaks into a public repo (platform 4.1).
- Append-only event files with ULID names. Schedules, map and due list are
  derived and never committed.
- Two devices only ever add different files, so a union merge never conflicts
  on content. No CRDT library is needed. Three rules cover the rest: earliest
  lock wins, last write wins per config key, the daily cap is per user.
- Code is never stored. Events hold project ids, commit hashes, paths and the
  user's own answers.
- Commits are signed with a device SSH key and each device keeps a hash chain.
  `unaided check` verifies both.
- Readable, exportable and deletable by the user. The format is a published
  spec so other tools can read it.

### 8.3 Generating and grading items without our server

The companion needs a model to write keys and grade open answers. It does not
ship one and does not call our servers. Order of preference:

1. **Executable grading first.** Run the code, run the test, run the user's
   check. Trace, replay and your-line items are graded this way.
2. **The user's own agent, headless, in a fresh context.** Most agents have a
   non-interactive mode (Claude Code `-p`, Codex `exec`, Gemini CLI
   non-interactive, Copilot CLI) [verified: surfaces 10.6 lists these modes].
   The engine starts a separate run that sees only the question, the sealed
   rubric, the shown code and the answer, never the teaching session. The
   answer is passed as data. Every point awarded must quote a span of the
   answer (evidence D.3). Cost falls on the user's existing agent plan; how
   much needs to be measured.
3. **A user-supplied API key**, if the user prefers, for the same grader call.
4. **Offline fallback.** The key is revealed after lock and the user marks
   themselves against binary points. The grade is tagged "self-graded" and
   counts at most as With help.

Grader protections from the evidence report: double grading on open items with
disagreement marked "uncertain", a check for answers that echo the agent's own
words, grader version stored with each grade, and one free "I think that grade
is wrong" regrade against the fixed rubric. Model judges show position,
verbosity and self-enhancement bias [verified:
https://arxiv.org/abs/2306.05685v1], and agreement with human graders varies
widely across studies [verified: https://ceur-ws.org/Vol-3772/paper10short.pdf].
So grader agreement with trained humans is measured and published per item
type before any open item counts toward Unaided.

Stated limit: an agent with the code can always reconstruct an answer. Sealing
stops the key leaking by accident; it cannot stop a determined user. That is
fine for a personal record.

### 8.4 The audit bank

A hidden set of items per topic that the teaching agent never sees and that is
never used for practice, following self-monitoring assessments [verified:
https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/].
Audit items are generated in their own context and sealed. The map always shows
the gap between practised and audit results. If practice scores rise and audit
scores do not, the product is teaching to its own test, and it says so.

### 8.5 Trust beyond the user

A self-graded local record can never prove skill to a third party. The proof
pack (7.5) carries sealed hashes, optionally timestamped externally on the
user's action. For stronger evidence a later "live check" runs a short
proctored set of audit items. Both are guides for mentors and teachers, never
for hiring.

### 8.6 Sync (opt-in only)

- **None** (default): one computer, plus a paired phone by local network.
- **Private git remote**: the user's own, any host. The engine refuses a public
  remote unless forced.
- **Blind relay** (paid, v2): an encrypted mailbox and push sender, no
  accounts. It holds ciphertext and public keys only. We publish a plain list
  of everything it can see, including fire times, sizes and IPs, as Obsidian
  does for its sync [verified: https://obsidian.md/help/sync/security].
  Encryption uses maintained libraries (age, libsodium), never custom crypto.
  Self-hosting is documented.

---

## 9. Privacy and ethics

- No network call the user did not cause. The full loop works on one offline
  computer, except open-item grading, which then falls back as in 8.3.
- Telemetry off by default. Opt-in aggregates only, through Prio3 over DAP,
  private if one of two aggregators is honest [verified:
  https://docs.divviup.org/how-it-works]. Never code, answers, rubrics or topic
  names. The user previews exactly what is sent.
- Agent transcripts are read only by opt-in importers, locally, and only to
  find moments; the transcript text is not copied into the record.
- No keystroke or screen tracking.
- No hiring use, no sale, no ads. Stated in the licence terms and on the site.
- Regulatory note: the EU AI Act may class learning-outcome grading and worker
  evaluation as high-risk [unverified: https://casrai.org/news/ai-act-high-risk-classification].
  The team plan's aggregate-only design and the ban on employer individual
  views are partly a response to this. Legal review is needed before the team
  plan ships in the EU.

---

## 10. Business model

Pricing is not set here. Comparable prices are from the users-market report and
are [unverified]: Pluralsight about $399 to $779 per user per year, CodeRabbit
about $24 to $48 per developer per month. What users will pay for this product
needs to be measured.

| Tier | Who | What | Network |
|---|---|---|---|
| Free, open source | Individuals | Engine, all adapters, record, companion on local web, paired phone web app, all drills, map, calendar reminder | None |
| Personal plus (paid) | Individuals with several devices | Blind relay sync, phone push reminder at the chosen time, native phone app later, desktop app auto-update | Relay, opt-in |
| Team (per seat) | Engineering teams | Shared drill library, onboarding packs, SSO and SCIM, region-pinned or self-hosted relay, aggregate page above the group floor | Team relay |
| Education licence | Courses, bootcamps | Course drill packs, instructor aggregates above the floor, student-held proof packs | Relay |
| Sponsorship | Open-source supporters | Funds the open core | n/a |

What is never sold: records, access to individuals, hiring signals, ads.

**Why individuals stay free.** The wedge is trust: local, auditable, no
network. That also helps plugin directory review (users-market). Charging for
the core would hand the space to free look-alikes.

**Why it is not just a free vendor toggle.** The assistants' learning modes are
per session, per vendor [verified: https://code.claude.com/docs/en/output-styles].
Unaided's value is the cross-agent record, delayed unaided measurement, and
drills from history. A vendor can copy a mode; it has less reason to build a
record that works across its competitors. This is the first business risk and
is tested in Section 13.

---

## 11. Metrics

The product's real metrics come first. Engagement numbers are guards only.

| Kind | Metric | Target |
|---|---|---|
| Learning (primary) | Delayed unaided accuracy on audit items, per construct, at 3 and 21 days | Needs to be measured |
| Learning | Audit gap (practised minus audit) | Should not widen |
| Learning | Calibration on delayed items | Needs to be measured |
| Learning | Your line passes first try, by topic level | Needs to be measured |
| Retention | Share of offered questions answered | Needs to be measured |
| Retention | Share of due reviews done | Needs to be measured |
| Retention | 30-day return to the companion | Needs to be measured |
| Guard | Task time with and without the inner ring | No worse than a margin set in advance |
| Guard | Skips, opt-outs, reminder dismissals | Watched, never optimised up |
| Guard | Score match across surfaces (phone, CLI, IDE) | Checked before comparing |

All metrics are computed on the device. Opt-in aggregates leave only as in
Section 9. Efficacy is estimated within each person by randomly holding back a
share of new topics from the inner-ring techniques and comparing delayed audit
results (learning-science L19). No efficacy claim before a preregistered
randomised study with a delayed, unaided, blind-graded test (evidence report).

---

## 12. What ships when

### v1: the loop on one computer, any agent (target: first public release)

- Engine binary, record spec, CLI, MCP server (tools only core), hook
  dispatcher with the canonical event set.
- Adapters generated from one manifest for Claude Code, Codex, Cursor, Copilot
  (VS Code and CLI), Gemini CLI, Devin Local, Amp, OpenCode, Cline; plain
  AGENTS.md path for the rest.
- Inner ring: predict and diagnose first, your line, explain-back, pressure
  silence, budget rules.
- Companion on local web: map, reviews (3 a day), trace drills, replay drills
  from git history, explainers after attempts.
- Grading: executable first, headless agent second, self-graded fallback.
- Phone: paired home-screen web app, sealed pack, one-tap local sync.
- Reminder: one recurring calendar event.
- Conformance suite for each adapter.
- Local metrics page for the user; no telemetry.

Explicitly not in v1: relay, team plane, transcript importers, seeded issues,
rehearsals, native apps.

### v2: across devices and deeper drills

- Desktop app wrapper with a local due-only notification.
- Blind relay (paid), push reminder, encrypted phone sync.
- Transcript importers, one per agent, each opt-in and probe-tested.
- Spot-the-issue drills on scratch copies, explain-a-change, compare drills,
  design calls.
- Audit bank shown on the map once the grader agreement study is done.
- MCP App card for one review at session start on hosts that declare it.
- Visitor mode encrypted carry-out for cloud sessions.
- Opt-in research cohort with preregistered study.

### Later

- Team plane: drill library, onboarding packs, SSO and SCIM, aggregates.
- Native phone app with local notifications.
- Incident rehearsals from the user's history.
- Education licence and course packs.
- Proof pack with external timestamps; proctored live check.

---

## 13. The five riskiest assumptions and the cheapest test for each

**1. People will open a separate companion at all.** The research warns users
say they want to learn and then skip (users-market risk 2; Lehmann et al.
found students prefer to substitute [verified: https://arxiv.org/abs/2409.09047]).
A separate app adds a trip.
Cheapest test: a two-week concierge test with a small group of juniors. Half
get reviews and one drill only inside their agent at session start; half get
the same items only in the companion with the one reminder. Compare share of
due items done and 14-day return. If the companion arm is clearly worse, make
the in-agent path the main door and the companion the depth layer.

**2. Real git history yields enough reproducible bug drills.** The wedge depends
on fix commits that have a test which fails on the parent and passes on the fix.
Cheapest test: run the miner (a script, no UI) on the team's own repos and on a
sample of public repos in several languages. Count reproducible drills per
hundred commits and the time to reproduce each. No users needed.

**3. Headless agent grading is close enough to trained human grading.** If it
is not, open items cannot count toward Unaided, and the map narrows to
executable constructs.
Cheapest test: collect a set of real open answers from the earlier round's
pilots and the concierge test, have two trained humans grade them against the
sealed rubrics, then grade with two different headless agents. Report agreement
per item type. Published per grader version.

**4. The inner ring holds on agents we do not control.** Agents may ignore the
skill, ask mid-edit, or delete your-line markers.
Cheapest test: the scripted conformance session per agent (surfaces 10.6):
check a question is asked only at a breakpoint, a your-line marker survives the
turn, the record gets a commit, and no more than 3 reviews appear next session.
Run headless where possible, by hand elsewhere. Pass rates per surface are the
result.

**5. The product produces delayed, unaided gains without slowing the build.**
Everything else is pointless if this fails, and users cannot feel it either
way: METR's developers were slower with AI but believed they were faster
[verified: https://arxiv.org/abs/2507.09089].
Cheapest test: within-person topic randomisation, on the device, from v1.
New topics are randomly assigned to get the inner-ring techniques or not; both
arms get the same delayed audit items. Task time is logged as the guard. This
needs no server and no new UI, only the engine. Effect sizes and required
counts need to be measured; the preregistered trial follows only if this
signal is there.

---

## 14. Founder decisions: status in this concept

| Decision | Status | Note |
|---|---|---|
| 1. Local git record, no remote by default | Kept | Clarified for cloud sessions: visitor mode (5.4). |
| 2. Your line on | Kept | Central to the inner ring; tests grade it. |
| 3. At most 3 due reviews a day | Kept | Drills count toward the 3 when they are due items; optional drills are only shown if the user asks. |
| 4. One phone tap where no-tap is impossible | Kept | Used for "sync phone" in v1. |
| 5. Letter shortcuts off by default | Kept | The companion registers none unless the user turns them on. |
| 6. Feature parity on all surfaces | Challenged | Changed to parity of outcomes with a conformance suite, with evidence in 5.1. |
| 7. At most one reminder a day at the user's time | Kept | Only when something is due; stops after three ignored. |

---

## 15. Open questions

- Is "Unaided" free as a name and package name? Which agents keep local
  transcripts, and in what format? [unverified]
- Does delayed feedback on the phone weaken learning? What does headless
  grading cost per week? Do empty-day reminders hurt? All need to be measured.
- Will team buyers accept aggregate-only views? Test in sales conversations.
  If they ask for more, the answer is no.
