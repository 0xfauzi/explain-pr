# Firsthand: product specification

Status: revised 7 November 2026. Nothing is built yet, except the existing skill in `skills/learning-while-building/`.

How to read this:

- This file is the whole product in short form. Detail lives in `spec/`. Each section links to the spec file that holds the rest.
- Claims about a product or harness carry [verified: source] or [unverified]. "[verified: research/x.md]" means the claim is verified, with its URL, in that report.
- The research reports in `research/`, the concepts in `concepts/` and the red-team reviews in `redteam/` are inputs. This spec cites them.
- Defaults are design choices. Each one says why it was chosen. Numbers come from a cited source, the current engine, or a founder decision.

Spec files:

| File | Holds |
| :- | :- |
| `spec/learning.md` | The moves, drills, items, levels, reviews, grading, cold start, and the one open question |
| `spec/experience.md` | First run, every exchange, all copy, the pad, the map, waiting and failure states, accessibility |
| `spec/surfaces.md` | Every coding surface, tiers, parity of outcome, install scope, conformance |
| `spec/architecture.md` | Engine, record format, sealing, grading interface, cloud sessions, phone |
| `spec/security.md` | Threats, sandboxing, supply chain, prompt injection, secrets, work computers |
| `spec/shared-repos.md` | Rules for repos other people share, and the codebase guide |

---

## 1. What Firsthand is

**The problem.** Developers who build with AI coding agents lose real engineering skill, or never form it. In a randomised study of people learning a new library, those who let AI write the code scored 50% on a quiz against 67% for those who coded by hand, with the largest gap on debugging (Shen and Tamkin 2026, https://arxiv.org/html/2601.20245v2; summary https://www.anthropic.com/research/AI-assistance-coding-skills). The AI users who kept their learning were the ones who asked conceptual questions or wrote code and then checked their understanding. The harm comes from AI replacing the learner's thinking, not from AI being present (Lehmann, Cornelius and Sting 2025, https://arxiv.org/abs/2409.09047).

**The answer.** Firsthand is an open-source tool anyone can install into the coding agent they already use: Claude Code, Codex, Cursor, Copilot, Gemini CLI, Devin, Amp, and anything that reads an instruction file and can run a shell command. You keep building at agent speed. At a few natural breaks, it asks you to do the part of the thinking that builds skill: predict what will happen, name the cause of a failing test, write the one line that carries a new idea, explain what changed, or review an agent's pull request before reading its summary. Days later it brings the idea back, in a new form, at most 3 times a day. Away from the build, it offers short drills made from your own history: real bugs to replay with the agent off, old code to trace, past diffs to check, and tasks in a repo you have never opened. A private map, in a git repo on your machine, shows what you can do without the agent and how recently you showed it.

**Why this design.** It follows the research on how people learn, applied to building with an agent:

| The product does | Because |
| :- | :- |
| Asks you to think first, at a few chosen points | High scorers in Shen and Tamkin asked conceptual questions or checked their understanding. Generating an answer beats reading one (d = 0.40, Bertsch et al. 2007, https://pubmed.ncbi.nlm.nih.gov/17645161/). Stating the step before seeing the AI's code aligned perceived and real ability best (Kazemitabaar et al. 2025, https://arxiv.org/abs/2410.08922) |
| Brings ideas back days later, as free recall | Practice testing and spacing are the two "high utility" techniques (Dunlosky et al. 2013). Testing beats restudy more on delayed tests (g = 0.69, Rowland 2014). Daily spaced questions during a working life still showed an effect two years later (Kerfoot 2009, https://pubmed.ncbi.nlm.nih.gov/19375095/) |
| Spends practice on debugging and checking agent output | Debugging showed the largest gap in Shen and Tamkin. Monitoring automation is not practice, and the unpractised cognitive part decays first (Bainbridge 1983; Casner et al. 2014; research/learning-science.md A.1 item 3) |
| Asks in new forms, with the topic name hidden | Transfer fails mostly because nothing cues the principle. Comparing two cases that share it nearly tripled its use (Gentner, Loewenstein and Thompson 2003; research/learning-science.md D.4) |
| Counts only delayed answers given without help | Immediate performance is not learning (Soderstrom and Bjork 2015, https://pubmed.ncbi.nlm.nih.gov/25910388/). People cannot feel which condition taught them more (Deslauriers et al. 2019) |
| Stays silent on what you know | What helps a novice can hurt someone who already knows the topic (expertise reversal, Kalyuga 2007). A senior is a novice in a new domain, so it adapts per idea, not per person |
| Has no streaks, points or badges | A 16-week study with leaderboards and badges found lower motivation and lower exam scores (Hanus and Fox 2015). Controlling rewards crowd out the reason professionals came (Ryan and Deci 2000) |
| Offers drills on rare, high-stakes skills away from the build | Real work gives too few reps of rare failures. Pilots train them in simulators; SRE teams rehearse past outages (research/learning-science.md D.3) |

The design rules L1 to L19 in `research/learning-science.md` Part A.3 are the full list. Each spec section cites the rules it uses.

**Name.** Working name: **Firsthand** (command `firsthand`, short alias `fh`). It says what the product builds: what you can do yourself. Fallback: **Ownline**. Both are [unverified] for trademark and package registries. The name is a founder decision (section 13).

---

## 2. Who it is for, and the first hour

### 2.1 Users

1. **Engineers in their first years who build with an agent every day.** They have the most to form and the least reason to notice it. In a vendor survey, 85% of juniors said AI improved their understanding, while 16% of seniors said juniors fully understand the AI code they submit (BairesDev Q2 2026, https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/).
2. **Experienced engineers moving into a new domain:** a new language, stack or kind of system. This is closest to Shen and Tamkin's setting. The product must never ask them about what they already know (section 5.7).

Out of scope: hiring and any use of the record to judge people. The record is for the person who owns it.

### 2.2 The first hour

- **Install, about a minute.** `firsthand init` adds itself to the agent it was launched from, shows every file it will change, and asks four questions (section 6.1).
- **First questions, a few minutes.** If the user added a repo, the first drill is a Trace on code in that repo from at least 7 days ago: predict what a real function returns for a real input, then see it run. Otherwise, three questions from the open question bank. Both happen in the pad, so they count under the normal rules.
- **First session.** One or two moments in the build, on ideas new to the user. A first map at the end.
- **First week.** The first reviews come back, in new forms. The first Monday brings the weekly line.

---

## 3. Principles

Each principle is a rule the product is built and tested against.

1. **The build always wins.** No learning moment blocks the agent's next step, except a "your line" the user accepted, and even that is handed back in one word. The product never leaves a build, a commit or CI red. Interruptions raise stress even when people work faster (Mark et al., https://www.ics.uci.edu/~gmark/chi08-mark.pdf).
2. **The user thinks first, at a few chosen points.** Predict, diagnose, write the key line, review before reading the summary, explain. L1, L4, L5, L18.
3. **Spend practice where skill erodes.** Debugging and checking agent output come first. L4, L17.
4. **Only delayed, unaided, new-instance performance counts.** A level rises on two right delayed answers on different items. L2.
5. **Grade by running code first.** Tests decide wherever they can. Model grading is for feedback, and moves a level only if the grader check passes (section 12).
6. **No pressure mechanics.** At most 3 due reviews a day by default, at most one reminder a day at the user's time, no streaks, points, badges or guilt. L14, founder decisions 3 and 7.
7. **Silent on what you know, and silent when unsure.** L10.
8. **One record across every agent, owned by the user, in local git, outside any project.** Founder decision 1.
9. **Parity of outcome on every surface,** with what each surface can count shown plainly (section 7). Founder decision 6, reframed with evidence.
10. **No new surface unless it does a job no agent surface can.** One is added: the pad, a terminal prompt the engine owns, because no agent chat can take an answer the agent cannot see.
11. **Show how every grade was made.** Every result shows how it was graded and how long ago. Clear feedback on the task is what builds calibration (L12, L13).
12. **Design for durable learning, not for how it feels.** Effortful practice feels worse and works better (Bjork and Bjork 2011; Deslauriers et al. 2019). The product does not soften moves to make them feel easier.
13. **Accessible by default.** Plain text first, verdict word first, voice dictation for every answer, no timers.
14. **The user's machine is not a sandbox.** Code the user did not write runs only in a container with no network, or not at all.
15. **Repo text is data, never the product's voice.** Text written by contributors is shown quoted and attributed, and can never widen a setting.
16. **Say exactly what leaves the machine, and to whom.**

---

## 4. The learning loop at a glance

Full detail: `spec/learning.md`.

| Layer | When | What happens |
| :- | :- | :- |
| In the build | At the agent's natural breaks | Predict, Call it, Your line, Explain back |
| At review time | When the user reviews an agent's pull request | Review first |
| Away from the build | Session start (offered, never a gate), the reminder, or when the user asks | Reviews (3 a day by default) and drills: Trace, Check, Replay, Compare, Fresh repo |
| Over time | Every answer | The map: what you have shown without the agent, and how recently |

Rules for every move:

- **Confidence in the same reply as the answer:** sure, think so, guess, or don't know. Sure misses are the most useful event for learning, so they bring an idea back soonest (L12).
- **Predictions are compared with what happened, never graded** (L6).
- **"Just tell me" always works.** It records that the attempt had help.
- **Every exchange carries a why-now and a one-word skip, and ends with the resume cue** `Back to: <task>. Next: <step>.`

---

## 5. The learning loop

### 5.1 The moves

| Move | Trigger | User does | Graded by | Can move a level? |
| :- | :- | :- | :- | :- |
| **Predict** | Before a deterministic step (test run, migration, query plan), on a new idea | One line: what will happen | Compared with the outcome, gap shown at `path:line` | No. It builds code reading and calibration; prediction accuracy is its own line on the map |
| **Call it** | A test fails, and the user's debugging is still forming or the agent has diagnosed most recent failures alone | A cause and the first check | The check and the cause, fed back at once | No, because the agent's visible work often shows the cause. It queues a Replay of the same bug, agent off, which can |
| **Your line** | The agent is about to write the one line that carries an idea new to the user | Writes it, before reading the test | The project's tests | Not in the session. It queues a delayed review, test hidden, which can |
| **Explain back** | After a step passes, once per task the user chose to learn from | Two or three sentences | Model feedback against points written from the code; the user self-marks | Not in the session. Delayed explain items in a new instance can |
| **Review first** | The user opens an agent's PR to review, with their agent or `firsthand pr <url>` | Lists defects or says "looks clean", before seeing the agent's summary | Tests the user writes, CI, later fix commits | Yes, for defects confirmed by a test |

**Review first** matters because coding is moving to background agents. Copilot cloud agent has no live user [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent]. The human is present at review time, and code review is already a main channel of knowledge transfer (Bacchelli and Bird 2013, research/learning-science.md D.3). The engine fetches the diff, hides the PR body and the agent's summary, and asks for findings. A finding is confirmed when the user writes a test that fails on the PR. That test is useful review work in its own right. Findings are private. The user may post one as an ordinary review comment in their own words.

**At Deep, two more:** *Plan first*, where the user lists the steps and what done looks like before the agent plans (Lead-and-Reveal, Kazemitabaar et al. 2025), and *design calls*, where the user's choice between two designs records a predicted consequence that comes back when that code is next touched (research/learning-science.md D.3, Kahneman and Klein on feedback).

### 5.2 Your line

Founder decision 2 stands.

- **Write first, then read the test.** The marker names the goal and the test, and says "try before reading the test". The marker states the goal and never describes the computation. The engine rejects markers with operators or formula words.
- **The delayed item carries the learning.** On "line done", the engine queues a review for a later day: the same goal in a new instance where possible, with the test hidden. That review, graded by the hidden test, can move a level.
- **In repos the user does not own,** the marker is a plain `TODO:` with the goal and the test, and is handed back before commit (section 10).
- Hint and "write it" are always free. Under pressure, on quiet branches, or on a failing deploy, an open marker is handed back.
- At Deep, your line grows from a line into a function into a design choice (L5).

### 5.3 When the engine speaks

The engine decides, in code. Inputs: the break, the idea tags, the user's levels, their debugging profile, pressure signals, quiet settings and the budget.

- **Novelty** decides Predict, Your line and Explain back: they come only on ideas new to the user.
- **Debugging profile** decides Call it: how many recent failures the agent diagnosed with no user hypothesis.
- **Fast delegation is not a silencer.** When the user moves fast, the engine asks nothing in the moment and queues one later item from the episode.
- **Pressure silences:** "urgent", "prod is down", a failing deploy, or a hotfix branch.
- **Explicit quiet beats guessing:** "quiet for 2h", "quiet today", "quiet in this repo", `firsthand quiet`.

### 5.4 The budget

| Limit | Default | Why |
| :- | :- | :- |
| Due reviews a day | 3; the user can lower it or raise it | Founder decision 3 |
| Reminders a day | At most 1, at a time the user picks. The install question has no pre-selected answer | Founder decision 7 |
| Unprompted moments in the build a day | 3, shown and set by the user | Keeps the whole product to a handful of asks a day, matching the review cap |
| Your line | At most one per task | Founder decision 2 |
| New ideas entering the review queue | Only when a slot is free or the idea is in a growth area | With 3 slots and a 5-step interval ladder, unlimited entry would leave most ideas unreviewed |
| Two skips in a session | End questions for that session, say so once | research/experience-design.md P3 |
| Three ignored reminders in a row | Ask once: keep, move or stop. Stop if no answer | A reminder nobody opens is noise |

### 5.5 Drills away from the build

Opt-in, inside the daily cap when due, never in the same week as the source material. Rare and high-stakes skills need reps that real work does not supply (L16).

| Drill | Built from | Runs in | Graded by | Builds |
| :- | :- | :- | :- | :- |
| **Trace** | The user's committed code, at least 7 days old | A scratch copy of committed files, agent config stripped | Running the code | Code reading |
| **Check** | A past agent-written diff with a known later fix, or none | Text only | Test-confirmed defects. A finding no test confirms stays "unconfirmed" and never counts against the user | Checking agent output |
| **Replay** | A fix commit whose test fails on the parent | A container with no network | The check named before the fix, then the commit's own test | Debugging |
| **Compare** | The same idea met in two projects, topic name hidden | Text only | Model feedback; self-marked for levels unless the grader check passes | Transfer |
| **Fresh repo** | A real change in a public repo the user has never opened | A container with no network | The change's own tests, kept sealed until the user submits | Transfer and reading unfamiliar code |

**Fresh repo** is the old Checkup, made local and turned into practice. Transfer is the hard part of learning, and it depends on meeting an idea in a new context (Barnett and Ceci 2002; research/learning-science.md D.4). Developers spend about 58% of their time understanding code (Xia et al. 2018, research/learning-science.md Part G). A task in an unfamiliar repo with the agent off practises both. The user starts it. The engine picks a task that uses an idea the user has practised, sets up the repo at the parent commit in a container, and hides the tests. The user works with any editor, agent off, then submits. The engine applies the sealed tests and shows the result, then the real commit for comparison. Tasks come from two places: an open task set written by contributors, and changes mined from public repos where a new test fails on the parent and passes on the commit (`spec/learning.md` section 3.5).

### 5.6 Growth areas

The user can name up to three ideas or skills to grow. They get extra drills beyond what is due and first claim on review slots. Autonomy over goals supports motivation (L15).

### 5.7 Cold start

A new record must not ask a senior about everything, and must not hide a junior's gaps. Commits with no agent trailer may still be agent-written, since inline completions and pasted chat code usually leave none.

1. Ideas found in the user's own commits are asked about less often, never silenced on inference alone.
2. "I know X" asks two quick questions: one direct, one in a new form with the topic hidden. Both right, and the idea goes quiet in every project.
3. Silenced ideas get an occasional re-check in a review slot.
4. A gentle first week: fewer moments, and your line only for ideas with no prior authorship found.

### 5.8 The dial

Off, Light, Standard (default), Deep, plus "just build" and "teach me this one". Light gives reviews and explain back. Standard runs all five moves within the budget. Deep adds Plan first, design calls, and your line that grows.

### 5.9 Levels

| Level | Earned by |
| :- | :- |
| **Not yet** | Default, or one step down after a delayed miss or "don't know" |
| **Recalled** | Two right delayed answers on two different items, on different days |
| **Applied** | Two right delayed answers on new instances: another function, file or project, topic name hidden |
| **Held** | Applied, then right at a longer gap, plus one other kind of evidence: a Fresh repo task, a confirmed Review-first finding, field evidence, or another item family |

**Met** is not a level. It lists ideas the user explained, wrote a line for, answered with help, or answered in the session. It sits under its own heading on the map.

An answer moves a level only when it is delayed, in free recall, code or number form (choice caps at Recalled), not marked "guess", typed in the pad or captured verbatim by a hook, and graded by tests, a person, or a grader that passed the check. Every level shows how long ago it was checked. Past its next due date plus a margin, the map shows "not checked lately" instead.

Six skills stay separate and are never combined into one score: code reading, debugging, design judgment, explaining a change, transfer, and calibration.

### 5.10 Field evidence

`firsthand field <commit or PR> "what I did"` logs real work done without the agent. Doing the thing for real is the strongest signal there is (research/learning-science.md Part G). It is one of the kinds of evidence that can complete Held.

### 5.11 Coming back

- **The weekly line.** In the first session of each week, one fact from the user's own record: "Last week you named the cause of 2 of 5 failing tests before the agent did. The week before, 0 of 4." Facts about the task and the user's own trend are the kind of feedback that helps (L13). No praise, no comparison with others. Off with one word.
- **The reminder is a real choice.** At install: "A daily reminder? Type a time, or none."
- **Fresh repo, when it has been a while.** The weekly line mentions once that a Fresh repo task is ready, if the user has done one before.

---

## 6. The experience

Full detail: `spec/experience.md`.

### 6.1 First install

```
npx firsthand@<version> init     (or: uvx, brew)
```

`init` installs into the agent it was launched from only. It lists other agents it found and adds each one only after a separate yes. Before writing, it shows every file and the exact diff, keeps byte-exact backups, and `firsthand uninstall` restores them. Hooks and MCP entries call an absolute, pinned path to the installed engine.

It says, in plain lines: where the record lives; what leaves the machine (nothing by default, but answers typed in the agent's chat are part of that chat); the size of the instruction text it adds to every session; and what this surface can count toward a level. Then four questions: Is this a work computer? How much learning (Standard)? A daily reminder (a time, or none)? Which repos may it read for drills (none by default)?

### 6.2 One exchange

```
New idea: retries with a payment API. Why now: this test runs it. Say "skip" to skip.
If the first two calls time out and the third succeeds, how many charges does the provider see?
Answer, then: sure, think so, guess, or don't know.
```

After three exchanges the header fades to one clause. Prediction reveals have no verdict word. Graded answers lead with Correct, Partly or Not yet, then the missing piece at `path:line`, when it comes back, how it was graded, and the resume cue. When the pad is open, the chat shows one line, "Question in your pad (skip ok)".

### 6.3 A normal week

- **Session start.** One ignorable line: "2 reviews due, about 2 minutes. Say 'review' now, or later."
- **In the build.** Maybe one prediction and one explain back on new ideas, one Call it if the profile says so. On known ideas, nothing.
- **Reviewing an agent's PR.** "Look first? Note any defects, or say clean, before I show the summary. Or skip."
- **Pressure.** Silence, and one offer to save it for later.
- **Evening.** One reminder with no content, if the user chose a time.
- **Monday.** The weekly line.
- **After a gap.** At most 3 reviews, chosen by priority, no backlog count.
- **When the user wants.** A drill, or a Fresh repo task.

### 6.4 The pad

The pad is a terminal prompt the engine owns: `firsthand pad`, in any terminal or an IDE's terminal panel.

- **The agent cannot see it.** An answer typed in the pad never enters the agent's context, so the agent cannot answer for the user or leak the key.
- **It counts.** An answer is "typed" when the engine opened the terminal itself and no agent is its parent process. Typed answers can move levels on every surface with a local terminal.
- **It stays private.** Answers in the pad never enter the agent's chat logs.
- **Drills run there.** Replay, Fresh repo and bank items are shown in the pad.

It is plain text, works with screen readers and dictation, has no timers and no letter shortcuts (founder decision 5). When it is closed, the chat path works, and chat answers record as Met.

---

## 7. Surfaces and parity of outcome

Full detail: `spec/surfaces.md`.

**Founder decision 6, reframed.** Decision 6 asks for feature parity on all coding surfaces. Parity of mechanism is impossible: Aider has no MCP and no hooks [verified: https://aider.chat/docs/config/options.html]; Copilot cloud agent supports MCP tools only and has no live user [verified: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp]; Copilot in Visual Studio, JetBrains, Eclipse and Xcode has no hooks [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet].

**The commitment: parity of outcome.** Every learning outcome is reachable on every surface in plain text plus a CLI call, and every surface with a local terminal can count toward a level through the pad. Where the only channel is the agent's chat, answers count as Met, and the product says so at install, on the map and at session start.

Tiers: T0 instruction file and shell; T1 MCP tools; T2 hooks; T3 native ask; T4 designed UI; T5 away from the keyboard; plus the pad. Each surface's tiers are in `spec/surfaces.md` section 3. Each adapter has a conformance test run on every release, and a public table shows which surfaces pass.

One record follows the user everywhere. Open lines and due reviews show up in whichever agent they open next.

---

## 8. Architecture

Full detail: `spec/architecture.md`.

### 8.1 Shape

```
any coding agent
   |  instruction block, skill folder, MCP tools, hooks (absolute pinned path)
   v
firsthand engine (on the user's computer, signed release)
   |-- CLI and pad   review | drill | fresh | pr | map | quiet | field | verify
   |-- MCP server    stdio, tools only; agent tools can only narrow settings
   |-- hook dispatch never returns allow or deny decisions
   |-- miner         read-only scan of added repos
   |-- runner        scratch copies from committed files; containers for code the user did not write
   |-- grader        tests first; model feedback with named recipient
   v
record: ~/.firsthand/record   (git, append-only events, signed, optionally encrypted)
   +-- optional: the user's own private git remote
```

No server is run by the product. The only network calls are ones the user causes: a model grader they turned on, cloning a public repo for a Fresh repo task, and their own git remote.

### 8.2 The record

- A per-user git repo outside any project tree. One JSON file per event, ULID names, union merge [verified: research/platform.md].
- Derived state (schedule, map) is never committed.
- Encrypted at rest with age on work computers, optional elsewhere.
- Every free-text field is secret-scanned before it is written. Private keys never live in the record.
- `forget <idea>` removes a whole idea and rewrites history.
- `firsthand export --plain` writes a readable copy, so the record outlives the product.

### 8.3 Sealing

The key's hash is committed before the question is shown. The engine releases a key only after the answer is locked. Keys are written by a separate context where the surface has one, and a second blind context solves each model-written item; if it disagrees with the key, the item is discarded. A sure miss triggers a re-check of the key, and a wrong key refunds the miss. This keeps the agent from grading its own teaching, and keeps a key from bending to fit an answer.

### 8.4 Grading

Providers in order: executable; a person; a model in a separate context (subagent, headless agent CLI, or the user's API key); self-marked.

- Tests decide wherever they can: Trace, Replay, your-line reviews, Review-first findings, Check confirmations, Fresh repo.
- Open answers (explain back, Compare, the check in Replay) get model feedback with a quote for every point, graded twice in shuffled order. Whether those grades move levels is the one open question (section 12). Until it is answered, the user self-marks against the sealed points and the answer records Met.
- Rubrics are written from the code and diff, by a context that has not read the agent's explanation, so repeating the agent's words earns nothing.
- Each model grader names who receives what before first use. Work computers default to local grading only.
- `firsthand cost` shows calls and tokens. No model call happens without consent.

### 8.5 The idea catalog and question bank

An open, versioned catalog of ideas with stable IDs, aliases and known confusions. The engine proposes a fixed candidate list per diff and the agent picks from it. When tags disagree, the engine stays silent.

The open question bank holds item families written by people: a template, a parameter generator and a key function, per idea. The engine makes a fresh instance for each use. Bank items are mixed into reviews. They are written independently of the agent that taught the idea, so they check understanding rather than the agent's phrasing. Anyone can contribute families through pull requests.

### 8.6 Cloud sessions and phone

Cloud agent disks do not survive. A cloud session ends with a `firsthand import <blob>` line to paste at home, or pushes to the user's own private record remote if they attached one. Imported answers record as Met. Whether to add a carry branch is a founder decision (section 13).

Phone: in the first stages, vendor phone apps, where answers are relayed and record as Met, plus a content-less calendar reminder. Later, a device link on the local network, paired with one confirmation tap (founder decision 4), rendering cards the engine owns so phone answers count.

### 8.7 What leaves the machine

| Path | What travels | Who receives it | Default |
| :- | :- | :- | :- |
| Answers in the agent's chat | The question, answer, verdict | The agent's company, and an employer's logs on work plans [unverified per vendor] | Chat on personal computers; the pad on work computers |
| Model grader | Answer, rubric, short code excerpt | The company and account the user names | Off until the user allows it; local only on work computers |
| Fresh repo task | A clone request for a public repo | That repo's host | Only when the user starts one |
| Private git remote | The record, encrypted if the record is | The user's host | Off |

Telemetry does not exist.

---

## 9. Security and privacy

Full detail: `spec/security.md`. The product touches every agent a user runs, so it must not become the weak point.

- **Untrusted code.** Replay and Fresh repo run only in a container with no network, from a pinned image. Without a container runtime they are not offered. Trace runs the user's own committed code in a scratch copy made from committed files only, never `.env` or untracked files, with agent and editor config stripped.
- **Supply chain.** Signed releases with registry provenance; hooks and MCP entries call an absolute pinned path; `firsthand verify`; updates only through `firsthand upgrade`, which shows the config diff. Hooks never return allow or deny.
- **Prompt injection.** Repo text is shown quoted and attributed, with commands and URLs stripped. Agent-callable tools can only narrow settings. Anything that widens (budget, grader, import, delete, remote) needs a confirmation typed in the pad.
- **Work computers.** Install says plainly what an employer can and cannot see. Answers go to the pad, the record is encrypted, and grading stays local by default. An employer that controls the device can, in the end, read anything on it, and the copy says so.
- **Secrets.** Every free-text field is scanned and redacted before write, and the user is told.

---

## 10. Shared repos and the codebase guide

Full detail: `spec/shared-repos.md`.

- **No learning data in shared branches.** In a repo the user does not own, your-line markers are a plain `TODO:` with no product or user name, handed back before commit. Nothing about learning goes in commits, trailers or PR bodies. Review-first findings are private.
- **The codebase guide.** Plain files in `.firsthand/guide/`, committed if the team wants: the ideas that matter in this codebase, where they live, how they break, and who is willing to help. Guide ideas become items on the map under "This codebase". Postmortems become rehearsal drills with the real resolution sealed. Guides are read only in repos the user marks as trusted.

---

## 11. Build order

The order puts real value in a developer's hands soonest, on one agent first, then widens. There are no phases to pass. Each step ships when it works.

1. **Fix the existing skill.** It tells users to commit `.learning/` to the project repo (`skills/learning-while-building/SKILL.md` line 103), which puts misses in shared history. Change the default to a folder outside the repo, and tell current users how to remove old copies. Reserve the package names and check the name's trademark.
2. **The core loop in Claude Code.** Engine, CLI, the pad, the record (with encryption), sealing, test grading, MCP tools and hooks. Predict, Call it, Your line, Explain back. Reviews with the cap, the map, the dial and quiet controls, cold start, the reminder, the weekly line. `firsthand import-lwb` for current skill users. This is where a developer first gets the whole loop. Claude Code first because it has every tier, including hooks and native ask [verified: research/surfaces.md 8.7].
3. **Review first and Trace.** `firsthand pr` and the `pr_review` break. Trace on the user's own code. Both need no container and use the most common daily work.
4. **Codex and Cursor adapters, and the floor for every agent.** Adapters generated from one manifest. Conformance tests run in CI through each agent's headless mode. Cloud sessions get the import line.
5. **The container runner, Replay and Fresh repo.** Debugging with the agent off and work in unfamiliar code, where the research says practice matters most. Build the miner, run it on public repos per language, and seed the open task set.
6. **The question bank, Check and Compare.** The first families per catalog idea, Check drills on past diffs, Compare across projects. Model feedback on open answers. Run the grader check (section 12).
7. **More surfaces and the guide.** Tested adapters for VS Code Copilot, Copilot CLI and Gemini CLI, then Devin, Amp, OpenCode, Kiro and Cline. The codebase guide and postmortem drills. Plan first and design calls at Deep.
8. **The phone device link.** Pairing with one confirmation tap, cards rendered by the engine.

Steps that check a fact belong inside the step that needs it: whether native ask content reaches the model on a host, whether a package manager can disable install scripts, which container runtimes work on which OS, hook latency per agent, grading cost per agent. Each is checked once while building that piece, and the result goes in the adapter manifest or the docs.

---

## 12. The one open question

Every other choice in this spec is decided from research, first principles or a stated assumption. One question passes the bar for an experiment: we can get the data, the research cannot answer it, and the answer changes the design.

**Does a model grader agree with people on open answers, in our rubric format?**

- *Why research cannot answer it.* Reported agreement between model graders and people ranges from near the level of two people to a kappa of 0.295, by model, rubric and domain. The evidence report concludes that reliability must be measured for this product's items, not assumed (research/evidence.md A.2 item 7). The answer depends on our rubric format, our quote-per-point rule and the models people actually have.
- *Why we can get the data.* Contributors write answers of mixed quality to a set of explain-back, Compare and Replay items. Two people grade each answer against the sealed points. The grader grades the same answers.
- *Why it changes the design.* If the grader agrees with people about as well as two people agree with each other, open answers can move levels, and explaining a change and transfer get real level evidence. If it does not, those skills stay at self-marked feedback, and levels for them rest on tests and field evidence only.

The graded set then stays in the repo as a regression test for the grader prompt and for each new model version.

---

## 13. Founder decisions

### 13.1 The founder's seven decisions

| # | Decision | Where it landed |
| :- | :- | :- |
| 1 | The record lives in a local git repo, no remote unless asked | Kept, outside any project tree |
| 2 | "Your line" is on | Kept. Write first, then read the test; a delayed hidden-test review carries the learning |
| 3 | At most 3 due reviews a day by default | Kept. The product limits how many new ideas enter the queue, not the reviews. The user may raise the cap; the product does not suggest it |
| 4 | One confirmation tap on the phone, where no tap is impossible | Kept for the device link |
| 5 | Keyboard letter shortcuts off by default | Kept. The pad has none |
| 6 | Feature parity on all coding surfaces | Reframed as parity of outcome, on evidence (section 7). Needs the founder's yes (13.2) |
| 7 | At most one reminder a day, at a time the user chooses | Kept. The install question has no pre-selected answer |

### 13.2 Open decisions, with a recommendation each

1. **The name.** Firsthand or Ownline. *Recommendation:* Firsthand, if the trademark and registry check in build step 1 finds no blocking conflict. It says what the tool builds.
2. **Parity of outcome as the meaning of decision 6,** including that answers given only in an agent's chat record as Met, and the pad is how every terminal surface counts. *Recommendation:* accept. Without it, either the agent can see and answer every question, or some surfaces cannot be supported at all.
3. **Cloud sessions: add a carry branch, or not.** A carry branch is an encrypted branch in a private repo the user owns that cloud sessions append to, which is an exception to decision 1. *Recommendation:* do not add it. The import line and the user's own private record remote cover cloud sessions, keep decision 1 clean, and avoid a branch that collaborators can see and that GitHub keeps readable after deletion [verified: https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github].
4. **Licences.** *Recommendation:* the engine under Apache-2.0; the catalog, question bank and task set under CC BY 4.0, so anyone can use and extend them and contributions flow back.
5. **Engine language.** *Recommendation:* Python, reusing `record.py` and `learning.py`, shipped with `uvx`, `pipx` and an npm shim. Revisit a static binary only if install trouble shows up on a platform.
6. **The claude.ai artifact Room** from the earlier design. *Recommendation:* retire it. The pad and the text map do its job on every surface, and the device link covers the phone.

---

## 14. What changed in this revision

From the earlier design (`design/learning-experience/`): any agent instead of Claude Code only; record outside project trees; separate-context sealing; item families; human-written bank items; Check drills on real diffs instead of injected bugs; diagnosis offered by debugging profile.

From the previous version of this document:

- **Cut:** the business model, pricing, paid tiers and paid Sync; funding plans and buyers; scarce assets, moats and vendor-copy risk; launch claims and the claims ladder; the team admin contract, team reports, SSO, SCIM, courses and proctoring; the v0 phase and every gate; week estimates; 18 experiments (E0 to E17), the study, the study-only pool and within-person experiments; the Checkup service and the Checkup as a measurement; signed results and proof packs; telemetry plans.
- **Restored or added, on research or first principles:** Fresh repo as a local transfer drill; Check drills without a label audit first, since only test-confirmed defects ever count; Replay without a yield gate, offered wherever a bug reproduces; Compare in the build order rather than last, since comparison is the best-supported route to transfer; model feedback on every open answer; Plan first and design calls at Deep; the phone device link without a gate; a first drill on the user's own code that counts under the normal rules.
- **Kept:** the five moves, the dial and quiet controls, the pad, the local git record, sealed keys, grading by running code, tiers per agent, parity of outcome, the founder's seven decisions, and the security and privacy design, cut to what protects users.
