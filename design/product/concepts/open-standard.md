# Concept: Open Learning Layer (the standard) and Tally (the reference product)

A product concept written from one angle: make "learning while you build with an agent" an open protocol that any agent, IDE, course or employer can implement, ship the reference implementation ourselves, and grow an ecosystem on top of it.

This is one of several concepts in `design/product/concepts/`. It treats the earlier round in `design/learning-experience/` as evidence, not as the answer. It draws on the six reports in `design/product/research/`. Claims about products are tagged [verified: source] or [unverified]. "[verified: research/x.md]" means the claim is verified, with its URL, in that report. Where a number would be a design guess, the text says "needs to be measured". Prices quoted from the research are [unverified] because the research tagged them so.

---

## 1. The concept in one page

**The standard: Open Learning Layer (OLL).** A small, versioned, openly licensed specification with four parts:

1. **Record format.** How a person's learning history is stored: an append-only set of event files in a local git repo the person owns.
2. **Card format.** How a learning moment is described: the question, the code it is about, a sealed answer key, and the item's family and distance.
3. **Moment interface.** The events an agent reports (breakpoints, test failures, commits) and the tools it calls to offer, answer, review and check "your line". It works with MCP tools alone, and with a CLI where there is no MCP.
4. **Grading contract.** What a grader receives, what it must return (a quoted span for every point), how grades record their provenance, and what a grader must publish about its own accuracy.

**The reference product: Tally.** An open-source engine (`tally`) that implements every part of OLL, plus generated adapters for each coding agent, a local page (the Room), a phone companion and paid optional services. The name says what it does: it keeps an honest count of what you can do without the agent. Trademark and package-name availability for "tally" is [unverified] and must be checked before launch; a generic word may be hard to protect, and a fallback name should be shortlisted.

**One sentence for users:** Build at full speed with any coding agent. Tally keeps your pace and keeps one private record, across every agent, of what you can now do without it.

**One sentence for the ecosystem:** OLL is to learning what AGENTS.md is to instructions: one small file format and one interface, so that a course, a repo maintainer, a mentor or an employer can plug into whatever agent a learner already uses.

**Why a standard and not only a plugin.** Three findings from the research make the standard the strategy rather than a side project:

- The largest threat is that AI vendors ship a free learning toggle [verified: research/users-market.md]. They already have: Claude Code's Learning style leaves TODO(human) gaps [verified: https://code.claude.com/docs/en/output-styles], and ChatGPT and Gemini have study modes [verified: https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/]. None of them keeps a record, schedules review, or measures unaided skill [verified: research/users-market.md]. A vendor toggle cannot give one record across vendors. A neutral format can. If vendors adopt OLL, Tally wins as the reference engine and the services layer. If they do not, Tally still works on their surfaces through adapters.
- The field is crowded with free look-alikes with similar names, such as learn-while-build [verified: https://github.com/Pranavraut033/learn-while-build] and VibeWise [verified: https://github.com/nykooi1/vibe-wise]. A plugin competes on features. A format that others write to is harder to copy, because the value is in the records and packs already written in it.
- The common floor across agents is already open and shared: AGENTS.md [verified: https://agents.md], the `.agents/skills/` folder, and MCP tools [verified: research/surfaces.md]. OLL sits on that floor and adds only what learning needs.

**What OLL deliberately is not.** It is not a credential, not a hiring signal, and not a surveillance feed. A self-graded record cannot prove skill to a third party [verified: research/platform.md], so the standard says so in its first section and defines a separate, proctored "live check" for the rare case where third-party evidence is needed.

---

## 2. Users and the wedge

### 2.1 Who it is for

Ranked by fit, from research/users-market.md:

1. **Junior engineers using an agent daily.** The pain is personal, and a private, local record is a selling point. Seniors doubt that juniors understand the code they submit: in one vendor survey, 85% of juniors say AI improved their understanding while 16% of seniors say juniors fully understand the AI code they submit [verified: https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/].
2. **Seniors moving into a new domain.** This is the setting of Shen and Tamkin almost exactly: experienced developers learning an unfamiliar library with AI [verified: https://www.anthropic.com/research/AI-assistance-coding-skills].
3. **Teams and engineering managers.** This is where the money is, and the risk is that engineers see it as surveillance. 38% of engineering leaders say AI cut the mentoring juniors get [verified: https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles].
4. **Open-source maintainers** who want newcomers to understand the repo before they send patches. This segment is new in this concept; demand is [unverified] and is risky assumption 3 in section 13.
5. **Educators, bootcamps and course authors.** Credibility, slow buying. CS50's own tutor still returns code blocks up to a quarter of the time despite instructions not to [verified: https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/], which shows a prompt alone does not hold a guardrail. OLL's engine-side sealing and grading is the answer to that.

Out of scope, by design: **hiring**. A record used to judge people stops being honest, because people stop admitting gaps [verified: research/users-market.md].

### 2.2 The wedge

The wedge has two halves that feed each other.

- **For individuals: one record that follows you across agents.** People switch agents and run several at once. Install Tally once; it works in Claude Code, Codex, Cursor, Copilot, Gemini CLI and the rest, and the map is the same everywhere. No vendor toggle can offer this.
- **For the ecosystem: "learn this repo" packs.** A maintainer adds a small `learn/` folder to their repository (section 6.2). Any OLL engine on any agent then knows the repo's key ideas, where they live in the code, and which "your line" tasks the repo's tests can grade. GitHub is the real storefront for developer tools [verified: research/users-market.md], so every repo with a pack is a distribution point that costs us nothing.

The first launch targets the first half alone. The pack format ships in v1 so that early adopters can write packs, but the ecosystem is a v2 bet (section 12).

---

## 3. The core learning loop, with evidence

The loop is the same in the standard and the product. OLL defines it as six required outcomes. A conformant host must let the user complete each one, at minimum in plain chat text.

| # | Outcome | What happens | Evidence |
|---|---|---|---|
| O1 | **Think first at a breakpoint** | At a natural breakpoint the agent offers one question about what it is about to do or just did: predict, choose, or explain. The agent keeps building while the user thinks. One word skips. | Generation effect d about 0.40 [verified: https://pubmed.ncbi.nlm.nih.gov/17645161/]; Lead-and-Reveal brought perceived and actual ability closest [verified: https://arxiv.org/abs/2410.08922]; breakpoints are where interruptions cost least [verified: https://www.interruptions.net/literature/Iqbal-CHI08.pdf] |
| O2 | **Diagnose first** | When a test fails, the user may name the cause first, once, before the agent diagnoses. The agent then runs the user's check before its own. | The largest gap in Shen and Tamkin was debugging; users who let the AI debug scored lowest [verified: https://www.anthropic.com/research/AI-assistance-coding-skills] |
| O3 | **Answer with confidence** | Every answer carries a confidence in the same action. Sure misses come back first. | Hypercorrection and calibration [verified: research/learning-science.md, L12] |
| O4 | **Graded against a sealed key** | The key was written and committed before the question appeared. A separate grader quotes the answer span for each point. | Model graders are uneven and biased [verified: https://arxiv.org/abs/2306.05685v1]; per-question rubrics help [verified: research/evidence.md] |
| O5 | **Your line** | On an idea the user is new to, the agent leaves one marked line of the real build for the user to write, and the project's tests grade it. "Write it" is always free. | Founder decision 2; fading worked steps [verified: research/learning-science.md, L5]; Claude Code's Learning style precedent [verified: https://code.claude.com/docs/en/output-styles] |
| O6 | **Review later, unaided** | At most 3 due reviews a day, free recall, no code or old answer shown until the user commits. A level rises only on a delayed, unaided, new-instance answer. | Spaced retrieval g = 0.74 [verified: https://link.springer.com/10.1007/s10648-020-09572-8]; testing effect larger on delayed tests [verified: https://doi.org/10.1037/a0037559]; daily questions to residents still showed an effect two years later [verified: https://pubmed.ncbi.nlm.nih.gov/19375095/] |

Plus one view, the **map**: per topic, the latest level and the best level, across all projects and agents. Levels can go down. There are no points, streaks or badges [verified: research/learning-science.md, L14; https://dblp.org/rec/journals/ce/HanusF15].

The levels are defined in the standard so that every engine means the same thing:

- **met**: the idea came up; nothing was asked or the user skipped.
- **seen**: the user answered in the same session, or with any help. This is the ceiling for anything in the session where the agent wrote the code [verified: research/evidence.md, Part B].
- **recalled**: correct on a delayed, unaided review.
- **transferred**: correct on a delayed item at a declared surface distance (a different project, or the topic name hidden).
- **checked**: confirmed in a proctored live check. Only this level is meant for anyone other than the user.

The **budget** is part of the standard, not a product setting, so that a second engine cannot spam a user who installed two: at most one prediction and one explain-back per task the user chose, two skips end questions for the session, 3 reviews a day by default, one reminder a day at the user's time. The 10-minute gap between unprompted learning turns is a starting value that needs to be measured [verified: research/experience-design.md].

---

## 4. The standard: OLL 1.0

### 4.1 Shape of the specification

OLL is one repository with a spec text, JSON Schemas, a conformance suite, and example records and packs. It is versioned with semantic versioning. Every file in a record names its format version. The spec text is licensed CC BY 4.0 and the schemas and suite Apache-2.0; the choice of licence is [unverified] as to fit with any future steward and needs legal review.

Five conformance roles. A product can claim one or several.

| Role | Must do | Example |
|---|---|---|
| **Record reader** | Read and render a record and its map. Never write. | A portfolio viewer, an editor extension, a course dashboard |
| **Engine** | Be the only writer of a record. Seal keys, schedule, enforce the budget, run your-line checks, apply conflict rules. | `tally` |
| **Host adapter** | Connect one agent surface to an engine, mapping its events and rendering cards at the best tier it has, always with full text. | Tally's Claude Code plugin; a vendor's native integration |
| **Grader** | Accept the grading input, return point-by-point grades with quotes, publish agreement numbers per task type. | Tally's default model grader; a human mentor tool |
| **Pack publisher** | Ship topics, detectors, item templates and your-line tasks in the pack format, signed. | A repo maintainer, a course, an employer's onboarding team |

The conformance suite is a set of scripted sessions. For a host adapter it plays a fake engine and checks that all six outcomes can be completed in text, that no key reaches the asking context before lock, and that no letter shortcuts are registered by default (founder decision 5). For an engine it replays a fixed event log and checks the derived map, due list and budget. For a grader it runs a public calibration set and reports agreement. Passing is what "OLL conformant" means; there is no other badge.

### 4.2 The record format

Taken from research/platform.md section 4, with two changes for multiple implementers: every event names the engine that wrote it, and extension fields live under a namespace.

```
<record>/                              one per user, outside any project tree
  OLL                                  "oll-record 1"
  devices/<device-id>.json             public keys and names of paired devices
  config/<key>.json                    one file per preference
  projects/<project-id>.json           name, path hint, hash of remote URL; never code
  topics/<topic-id>.json               the idea, its construct, where it was met
  events/<yyyy>/<mm>/<ulid>.json       one file per event, append-only
  sealed/<card-id>.age                 encrypted answer keys
  packs/<pack-id>@<version>.lock       which pack versions this record has used
derived, never committed: schedule, due list, map, open cards
```

An event:

```json
{
  "oll": 1,
  "id": "01JC8Y3W8Q5V7N2K4T6R9X1M0B",
  "type": "answer.locked",
  "card": "01JC8Y2F7H3QZ5W8N1P4R6T9KD",
  "device": "dev_7f3a",
  "surface": "codex-cli",
  "engine": "tally/1.0.0",
  "at": "2026-11-07T14:02:11Z",
  "body": {"answer": "The write is durable before the event is published", "confidence": "sure", "help": "none"},
  "prev": "sha256:9c1e...",
  "x": {}
}
```

Rules:

- One file per event, ULID names, so two devices only ever add different files and a union merge never conflicts on content [verified: research/platform.md]. No CRDT library is needed.
- Three conflict rules, each a pure function of the events: earliest lock wins; last `config.set` wins per key; the daily cap is per user, assigned when a pack is built.
- `prev` is a per-device hash chain. Commits are signed with SSH keys where the user has one [verified: https://docs.gitlab.com/user/project/repository/signed_commits/ssh.html].
- `x` holds extension fields, keyed by a reverse domain name. Readers must ignore unknown keys. This is how a vendor adds features without forking the format.
- Never stored: project source beyond the card's excerpt (which the user can turn off per project), secrets (a scanner runs over excerpts first), keystrokes, screen contents, or time spent typing.

Event types in 1.0, grouped:

- Cards: `card.drafted`, `card.sealed`, `card.delivered`, `card.expired`.
- Answers: `answer.locked`, `key.revealed`, `grade.recorded`, `grade.disputed`, `grade.uncertain`.
- Your line: `line.offered`, `line.declined`, `line.written`, `line.checked`, `line.survived` (the line still exists at the next commit).
- Schedule and record: `review.scheduled`, `level.changed`, `topic.added`, `topic.merged`, `topic.retired`.
- Setup: `config.set`, `device.paired`, `device.revoked`, `pack.added`, `pack.removed`, `consent.given`, `consent.withdrawn`.
- Evidence: `livecheck.recorded`, `export.made`.

Derived state is a fold over events. A new scheduler, such as FSRS, can be swapped in by replaying the log; that FSRS replays this format is [unverified] until we test it.

### 4.3 The card format

A card is one learning moment. It is bound to the user's own code, never a made-up exercise, except audit items (section 4.6).

```json
{
  "oll": 1,
  "id": "01JC8Y2F7H3QZ5W8N1P4R6T9KD",
  "kind": "predict",
  "construct": "debugging",
  "topic": "oll:topic/distributed.idempotency",
  "prompt": "The retry fires after a timeout. Will the charge run twice? Why?",
  "shown": [{"path": "billing/charge.py", "lines": "41-58", "sha256": "4be0...", "excerpt": "..."}],
  "answer_form": "text",
  "confidence_scale": ["guess", "unsure", "fairly sure", "sure"],
  "key": {"sealed": "sealed/01JC8Y2F.age", "sha256": "e17a...", "points": 3},
  "family": "retry-without-idempotency-key",
  "distance": {"project": "same", "topic_name_shown": false, "since_last_seen_days": 4},
  "help_allowed": ["hint1", "hint2", "worked"],
  "source": {"pack": null, "drafted_by": "agent", "sealed_by": "tally/1.0.0"}
}
```

Kinds in 1.0: `predict`, `choose` (pick between two designs and say why), `explain` (explain a finished change), `diagnose` (name the cause of a failure first), `trace` (what value results), `review` (spot the issue in an agent-written diff, opt-in only, on a scratch or reversible change), `line` (your line), `compare` (the same principle in two projects; this is the transfer item [verified: research/learning-science.md, L11]).

Constructs are the six the evidence track says to report separately: code reading, debugging, design judgment, explaining a change, transfer, calibration [verified: research/evidence.md]. There is no combined score anywhere in the standard.

### 4.4 Topic identifiers

Records from different engines and packs must agree that two cards are about the same idea, or spacing and transfer break. OLL defines an open topic namespace, `oll:topic/<area>.<idea>`, maintained in the spec repo as a plain list with short definitions and aliases. Packs and engines may mint private topics under their own domain (`com.example:topic/...`) and propose a mapping. An engine merges topics with a `topic.merged` event, never by rewriting history.

The starting list needs to be written. A reasonable seed is the topics the current skill already records, plus the debugging and reading dimensions from research/learning-science.md. Whether an existing skills framework can serve as the top level is [unverified].

### 4.5 The moment interface

This is how any agent talks to an engine. It has two halves.

**Events the host reports.** One canonical set, mapped per agent by a generated table: `session_start`, `prompt_submit`, `before_tool`, `after_tool`, `tool_failed`, `turn_end`, `session_end` [verified: research/surfaces.md]. Hosts without hooks report through the agent itself, which calls `moment` at the breakpoints named in the skill text.

**Tools the agent calls.** Seven tools, usable with MCP tools alone because Copilot cloud agent supports only tools [verified: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp], and mirrored one to one as CLI subcommands for hosts without MCP, such as Aider [verified: https://aider.chat/docs/config/options.html].

| Tool | Input | Returns |
|---|---|---|
| `moment` | breakpoint kind, task summary, files touched, pressure signals | Nothing (stay quiet) or one card as complete text plus a structured copy |
| `draft_key` | card id, rubric points (called by a separate context where the surface allows it) | Hash of the sealed key. The rubric never comes back. |
| `answer` | card id, answer text, confidence, help used | Grade as text: verdict word first, what was right, the missing piece at `path:line`, when it returns, then the resume line |
| `line` | `offer`, `check` or `decline`, with the marker location | The marker comment to insert, or the test outcome |
| `review` | `next` or an answer | The next due item, or "Nothing due today." |
| `map` | optional topic | The map as plain text, and a link to the Room if it is running |
| `dispute` | card id, reason | Second grading result |

Every tool result ends with one line: "Back to: <task>. Next: <step>." [verified: research/experience-design.md]. That line is part of the conformance suite, because it is what makes a learning moment cost the build little.

**Upgrade by declared capability.** The engine returns full text always, then adds richer forms only when the client declares them: an MCP elicitation form where the client declares elicitation (Claude Code, Codex, Cursor, VS Code Copilot [verified: research/surfaces.md]), an MCP App card where the host declares the UI extension (VS Code Copilot, Cursor, goose, Claude chat, ChatGPT [verified: https://modelcontextprotocol.io/extensions/apps/overview.md]), and ACP elicitation in Zed and JetBrains ACP agents [verified: https://www.jetbrains.com/help/ai-assistant/acp.html]. OLL does not build on MCP sampling (deprecated) or require MCP Apps [verified: research/surfaces.md].

**Two protocol revisions.** The reference MCP server speaks both the 2025-11-25 handshake and the 2026-07-28 stateless discovery [verified: research/surfaces.md].

### 4.6 The grading contract

The contract turns the evidence track's protocol [verified: research/evidence.md, D.3] into an interface any grader can implement, human or model.

**Order, enforced by the engine.**

1. `card.drafted`, then the key is written by a context that will not ask the question, then `card.sealed` with the key's sha256 committed to git.
2. Only after that commit exists does the card reach the user.
3. `answer.locked`. Only now will the engine release the key (`key.revealed`). Any page, phone pack or asking context that requests a key before lock gets a refusal. This fixes the earlier round's finding that the rubric reached the page before the answer [verified: research/platform.md].

**Grader input.** Exactly four fields: the prompt, the sealed rubric, the excerpt the card showed, and the answer in a delimited field marked as data that may contain instructions. Not the session, the confidence, the help level, the history or the name.

**Grader output.**

```json
{
  "points": [{"id": "p1", "met": true, "quote": "durable before the event is published"},
             {"id": "p2", "met": false, "quote": null}],
  "grader": {"id": "tally-model-grader", "version": "1.0.0", "model": "<model id>"},
  "echo": false,
  "uncertain": false
}
```

Rules every grader must follow:

- No quote, no point.
- Executable checks run first. A prediction is compared with the build's real outcome; a your-line task is graded by the project's tests. A model grades only what cannot be run.
- Grade twice with the rubric points shuffled. Disagreement means `uncertain`, which shows both readings and does not move the level.
- If a quoted span nearly copies text the agent wrote in the session, the point counts but the level cannot rise (`echo: true`).
- One dispute per grade, which triggers one regrade against the same sealed key.

**Grade provenance.** Every grade names its grader kind: `executable`, `model`, `model-pair`, `human` (a mentor), or `proctored`. Readers display the kind next to the level. A map can then say "recalled (graded by tests)" or "recalled (model, uncertain)".

**What a grader must publish.** Agreement with trained human graders per task type and grader version, measured on a public calibration set, with leniency in both directions. Below human-human agreement on a task type, grades of that type do not count toward lagging outcomes [verified: research/evidence.md, D.4]. Published agreement numbers for model graders range widely, from near human-human [verified: https://pdf.arxiv.org/pdf/2412.06910] to a kappa of 0.295 [verified: https://ceur-ws.org/Vol-3772/paper10short.pdf]. So OLL makes the number public rather than assuming it.

**The audit bank.** OLL reserves an `audit` card source. Audit items are written by people, never used for practice, never shown to the teaching agent, and mixed into reviews within the 3-a-day cap. Every reader shows the gap between practised and audit results per construct. This is the Goodhart alarm [verified: https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/]. The share of review slots spent on audit items needs to be measured. Stated limit: in a local tool, a determined user can read an audit item early. The design records honesty, it cannot force it.

**Stated limit of sealing.** A coding agent can always rebuild the answer from the code it can read [verified: research/platform.md]. Sealing protects the user from a lenient grader that adapts the key to the answer. It does not protect a third party from the user, which is why only `proctored` grades count as evidence for anyone else.

### 4.7 Live checks: the only third-party evidence

A live check is a short, timed-by-the-user (not by us), proctored session: a mentor, instructor or interviewer the user invited watches the user answer two or three sealed items drawn from the user's own recalled topics, with no agent running. The proctor signs a `livecheck.recorded` event with their key. The user decides whether to include it in an export. OLL defines the event and the signature, not the business process. Hiring uses remain out of scope for Tally's marketing even though nothing stops a user sharing their own export.

### 4.8 Governance

- The spec lives in a public repo under an open licence, with an RFC process and a small editors group. Tally's company holds one seat, not a majority, from v2 onward.
- The aim is to offer OLL to a neutral steward once two or more independent implementations exist. The Agentic AI Foundation is a candidate; its launch with MCP, goose and AGENTS.md is [unverified] (press reports only), while AGENTS.md's site states it is "stewarded by the Agentic AI Foundation under the Linux Foundation" [verified: https://agents.md]. Whether such a body would accept a learning spec is [unverified].
- No conformance fee. The suite is free to run. A certification business would make Tally a gatekeeper and slow adoption, and it is not needed for revenue (section 11).

---

## 5. The reference implementation

### 5.1 The engine

`tally` is one static binary with five faces [verified: research/surfaces.md, proposed architecture]:

1. **CLI**: every outcome as a subcommand (`tally moment`, `tally answer`, `tally review`, `tally line`, `tally map`). This is the floor for every surface.
2. **MCP server** over stdio: the seven tools.
3. **Hook dispatcher**: `tally hook <agent> <event>`, reading each agent's hook JSON and mapping it to the canonical set.
4. **The Room**: a local page served on demand, read-only for keys until lock, for reviews, the map and the record.
5. **Scheduler**: one OS-level daily reminder at the user's chosen time, carrying only a count, never question text.

All learning logic lives in the engine: state, sealing, scheduling, the budget, your-line checks. Adapters only translate event names and output shapes.

The existing skill in this repository (`skills/learning-while-building/`, with `scripts/learning.py`, `record.py`, `room.py` and `assets/room.html`) is the prototype of the engine and the Room. The concept keeps its voice rules and question design and moves its state logic into the engine.

### 5.2 Adapters, generated from one manifest

One description file generates every package, so they cannot drift: a Claude Code plugin, a Codex plugin, a Cursor plugin, a Gemini CLI extension, a Kiro power, an Amp plugin, an OpenCode npm package, a Devin plugin and a Cline MCP listing [verified: research/surfaces.md, proposed list]. Each package installs:

- the skill once at `.agents/skills/tally/`, copied or linked only where an agent does not read that path (`.claude/skills`, `.cline/skills`) [verified: research/surfaces.md];
- a three-line block in AGENTS.md pointing to the tool, never long rules, because every session of every agent pays for them;
- the MCP server entry;
- the hook mapping where hooks exist.

### 5.3 The open pack toolchain

`tally pack init`, `tally pack lint`, `tally pack test` (runs the pack's detectors against a corpus of public repos and reports how many real instances each topic finds) and `tally pack sign`. These are part of the reference implementation because the ecosystem only grows if authoring a pack is cheap.

---

## 6. The ecosystem

### 6.1 Principle: packs bind to the learner's code, never replace it

The design rule "draw every question from the user's own real code from this week" [verified: research/users-market.md] rules out the classic flashcard deck. An OLL pack is not a deck of fixed questions. It is knowledge an engine uses to ask better questions about whatever code the user is building.

A pack contains:

- **Topics**: ids, short definitions, common misconceptions, and the principle to name.
- **Detectors**: patterns that find an instance of a topic in real code or in an agent's diff (for example, a retry around a non-idempotent call). Detectors are declarative queries in a sandboxed pattern language; which one is [unverified] and must be chosen for safety and language coverage.
- **Item templates**: question shapes per card kind, with rubric templates the engine fills from the detected code. The engine still seals each filled key before asking.
- **Your-line tasks**: for a repo pack, specific lines the repo's own tests can grade.
- **Audit items** (optional): human-written, encrypted, never shown to the teaching agent.

A pack cannot read the record, call the network, run code, or see any project other than the one being built. The engine runs detectors in a sandbox and only passes the pack excerpts it has matched. Every pack is signed by its publisher; the engine shows the publisher on first use and asks once.

### 6.2 Repo packs: "learn this repo"

A maintainer adds `learn/pack.json` to their repository:

```json
{
  "oll_pack": 1,
  "id": "io.github.example.payments",
  "version": "0.3.0",
  "publisher": {"name": "Example maintainers", "key": "ssh-ed25519 AAAA..."},
  "topics": ["oll:topic/distributed.idempotency", "io.github.example:topic/ledger.double-entry"],
  "detectors": "learn/detectors/",
  "templates": "learn/templates/",
  "lines": [{"path": "ledger/post.py", "symbol": "post_entry", "test": "tests/test_post.py::test_balances", "topic": "io.github.example:topic/ledger.double-entry"}]
}
```

When a contributor's agent opens the repo, the engine notices the pack, asks once whether to use it, and from then on prefers the repo's own key ideas when choosing what to ask about. The contributor's answers go to the contributor's own record. The maintainer sees nothing unless the contributor chooses to share.

For maintainers, the value is newcomers who understand the parts of the code that matter before they send patches. Whether maintainers want this enough to write a pack is [unverified] and is risky assumption 3.

### 6.3 Course packs built on real repos

A course is a pack plus a **route**: an ordered list of real tasks in a real open-source repo at a pinned commit. The learner builds the real feature with their agent, and the route's your-line tasks and audit items do the teaching and measuring. A course author never writes toy exercises. This answers the market gap that learning platforms teach on made-up exercises [verified: research/users-market.md].

Cohort aggregates for an instructor follow the team rules in section 6.5: aggregate only, minimum group size of 5, no individual weak areas.

### 6.4 Mentors as graders

A human mentor is a grader under the same contract. The learner exports a grading bundle for one attempt (prompt, sealed key, excerpt, answer), sends it however they like, and imports the mentor's signed grade. The mentor's grade sits next to the model's with `grader.kind = human`. A mentor can also run a live check (section 4.7).

This rebuilds a piece of mentoring that leaders say AI has cut [verified: https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles], without the mentor needing access to the learner's record or code beyond one excerpt.

### 6.5 Employers

An employer can do three things, and only three:

1. **Publish internal packs** for their own codebase: onboarding to a service, its failure modes, its on-call runbooks. Packs are distributed in the company's repos like any repo pack.
2. **See opt-in aggregates** per team and per topic, above a minimum group size of 5, following the Viva Insights pattern [verified: https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings]. Typical questions it answers: "which ideas in our payments service are new to most of the team", "is review uptake falling". It never shows an individual.
3. **Pay** for seats, relays pinned to a region or self-hosted, and SSO and SCIM.

An employer cannot read an individual record, cannot switch telemetry on for anyone, and has no admin key to a record, because none exists [verified: research/platform.md, section 11].

### 6.6 What other implementers could build

To make "ambitious" concrete, these are products a third party could build on OLL without asking us:

- A vendor adds native OLL to its agent: its learning mode writes to the user's existing record instead of a session-only memory.
- An IDE ships a record reader that shows a gutter mark on code the user once wrote as "your line".
- A bootcamp runs cohorts on course packs and uses live checks for its own completion certificate.
- A research group runs a preregistered trial using the in-record randomisation (section 9.4).
- A different engine with a different scheduler, for example one tuned for people who use the phone more than the desk, reading and writing the same record.

---

## 7. Surfaces and parity

### 7.1 Parity of outcome, verified by the suite

Founder decision 6 asks for feature parity on all coding surfaces. **I challenge the wording, with evidence, and keep its intent.** Exact parity of mechanism is impossible: VS Code MCP Apps render inline only, Zed and Gemini CLI document no MCP Apps or elicitation, Claude Code does not render MCP Apps, and Copilot cloud agent supports tools only [verified: https://code.visualstudio.com/api/extension-guides/mcp, https://zed.dev/docs/ai/mcp, https://geminicli.com/docs/tools/mcp-server/, research/surfaces.md]. The standard therefore defines parity as **parity of outcome**: on every surface the user can complete O1 to O6 and see the map, in plain text at minimum, verified by the conformance suite per agent per release. Richer UI is a faster door to the same action. Grading parity is part of it: the same answer must get the same grade whatever surface it was typed on, and the suite checks this [verified: research/evidence.md].

### 7.2 Tiers per surface

| Surface | Floor reached through | Best tier | Phone | Notes |
|---|---|---|---|---|
| Claude Code CLI and desktop | skill in `.claude/skills`, MCP, hooks | Elicitation form; turn end can continue | Claude app Code tab [verified: https://code.claude.com/docs/en/mobile.md] | No MCP Apps |
| Claude Code on the web | same, cloud session | Elicitation | Claude app | Ephemeral VM: visitor mode [verified: https://code.claude.com/docs/en/claude-code-on-the-web.md] |
| Codex CLI, app, IDE | `.agents/skills`, MCP, hooks [verified: https://learn.chatgpt.com/docs/hooks] | Elicitation; app panels need a re-test [unverified] | ChatGPT mobile [verified: research/surfaces.md] | |
| Codex cloud | same, cloud | Text | ChatGPT mobile | Containers cached up to 12 hours [verified: https://developers.openai.com/codex/cloud/environments] |
| Cursor editor and CLI | skills, MCP, hooks [verified: https://cursor.com/docs/agent/hooks] | Elicitation and MCP Apps | Cursor iOS and web [verified: research/surfaces.md] | `followup_message` continues a turn |
| Cursor cloud agents | MCP, skills | Text | Cursor web | Isolated VMs [verified: https://cursor.com/docs/cloud-agent] |
| VS Code Copilot | skills, MCP, hooks | Elicitation and inline MCP Apps | GitHub Mobile | |
| Copilot CLI and cloud agent | MCP tools only on cloud; hooks [verified: https://docs.github.com/en/copilot/concepts/agents/hooks] | Text | GitHub Mobile | Cloud sessions stop at 59 minutes [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent] |
| Copilot in Visual Studio, JetBrains, Eclipse, Xcode | MCP and instructions; no hooks [verified: https://docs.github.com/en/copilot/reference/customization-cheat-sheet] | Text | GitHub Mobile | Breakpoints come from the agent calling `moment` |
| Gemini CLI | skills, MCP, hooks [verified: https://geminicli.com/docs/hooks/reference/] | Text | None documented | No elicitation documented |
| Windsurf / Devin Local | AGENTS.md, skills, MCP, hooks [verified: https://docs.devin.ai/desktop/devin-local/customizations.md] | Text [unverified for richer tiers] | [unverified] | Rebrand from Windsurf is [unverified] |
| Zed agent and ACP agents | skills, MCP [verified: https://zed.dev/docs/ai/skills] | ACP elicitation for external agents | None | Zed's own agent has no hooks |
| JetBrains Junie and AI Assistant | MCP, ACP | ACP elicitation [verified: https://www.jetbrains.com/help/ai-assistant/acp.html] | None | No hooks in Junie [verified: research/surfaces.md] |
| Amp | skills, MCP, plugins [verified: https://ampcode.com/docs/customize/plugins] | Plugin UI (confirm, select) | Amp iOS and Android [verified: https://ampcode.com/manual] | |
| OpenCode | skills, MCP, npm plugin [verified: https://opencode.ai/docs/skills/] | Desktop plugin UI, experimental | None | |
| Cline, Roo, goose, Kiro | MCP, skills where read, hooks where present [verified: research/surfaces.md] | goose renders MCP Apps | None | Roo and goose have no hooks |
| Aider | CLI and AGENTS.md only; no MCP documented [verified: https://aider.chat/docs/config/options.html] | Text through CLI | None | Your line still works: it is a code comment plus a test |

Any surface not in this table gets the floor: an AGENTS.md pointer and the CLI. Every row is tested by the conformance suite, not assumed. Several cells come from the research rather than a fresh check today, as tagged.

### 7.3 Cloud sessions: visitor mode

Founder decision 1 says the record lives in local git with no remote unless the user asks. Cloud sessions have disks that are thrown away [verified: research/platform.md, 6.2]. **This is a clarification of decision 1, not a challenge:** on an ephemeral surface, the engine says on first run that the record will be lost without a way home, and asks once, offering three options. The default keeps decision 1 intact.

1. **Carry out by hand (default).** Events go to an in-memory outbox. At session end, the agent prints one `tally import` line holding an encrypted bundle, or writes it to a file the user downloads. Cost: one paste. Weakness: people forget, and how often needs to be measured.
2. **A private git remote the user already has**, attached to the session.
3. **The blind relay** (paid or self-hosted), with its key in the surface's secret store.

The research tracks disagree on one point and I side with the stricter one. research/surfaces.md proposes letting new attempts travel in the project branch under `.learning-inbox/`; research/platform.md says never to write the record to a cloud session's project repo or any branch of it, because branches of a public repo are public. OLL forbids writing record data to any project repo by default. A repo pack in `learn/` is not record data and is allowed.

### 7.4 The phone

The phone cannot run git, so the system of record stays on a computer and the phone holds a projection plus an outbox [verified: research/platform.md, 6.3]:

- **Pairing** by QR, keys generated on the device and never leaving it, following the Tailscale pattern [verified: https://tailscale.com/kb/1232/derp-servers].
- **Pack**: up to 7 days of due cards with no answer keys, encrypted to the phone. **Outbox**: locked answers, encrypted to the user's computers.
- **Transport with no server**: same Wi-Fi after one tap (within decision 4), a file, or a QR.
- **Grading** happens at the next sync. That delay may cost learning; how much needs to be measured, and it is the strongest reason a user might choose the relay.
- **The reminder**: in v1, one recurring calendar event with no content, at the user's time, because every web push path needs a sender server and local scheduled web notifications never shipped [verified: https://developer.chrome.com/docs/web-platform/notification-triggers; https://webkit.org/blog/16535/meet-declarative-web-push/]. A native app with local notifications comes later. On iOS it uses the passive or active level, never time-sensitive [verified: https://www.wwdcnotes.com/notes/wwdc21/10091].

Inside the vendor phone apps (Claude Code tab, ChatGPT, Cursor, GitHub Mobile, Amp), the floor is the same text loop, because those apps drive the same agents.

---

## 8. The experience end to end

### 8.1 First install

The user runs one command from the agent's marketplace or a package manager. Directory and registry details are [unverified] per marketplace. The first run asks three questions, each with a default, and no account [verified: research/experience-design.md]:

```
Tally keeps a private record of what you can do without the agent.
It lives in a git repo on this computer. Nothing leaves it unless you ask.

1. How much should I ask?   Light / Standard / Deep / Off      [Standard]
2. One reminder a day, when? (or "none")                        [none]
3. Keep the record at ~/.local/share/oll/record ?               [yes]

Done. I will stay quiet until a natural break in your work.
```

Nothing else happens until the first breakpoint. There is no tour.

### 8.2 First question

The agent finishes a step that introduced a retry around a payment call. The engine's `moment` decides the idea is new to this user and returns one card:

```
While I write the tests: one question, skip any time.
Before I run them: if the network times out after the charge succeeds,
what happens on the retry?  (billing/charge.py:41-58)
Answer, and say how sure you are (guess / unsure / fairly sure / sure).
Back to: add payment retries. Next: writing tests.
```

The agent keeps building. The user replies "it charges twice, fairly sure". The tests run; the outcome settles the prediction, because predictions are compared, never graded, and never move the record [verified: research/experience-design.md]. The reply is the verdict word first, the evidence at `path:line`, when the idea returns, and the resume line. The first question is the onboarding: below the reply, one line says what just happened and how to turn it down.

### 8.3 Your line

Later in the same task the engine offers your line on the idempotency key, because the topic is at `met`:

```python
    # YOUR LINE (tally): pass a key so a retried charge is not charged twice.
    # Topic: idempotency. Test: tests/test_charge.py::test_retry_once. Say "write it" to skip.
    response = client.charges.create(amount=amount, currency=currency)
```

The agent builds the code around it and moves on. When the user writes the line, `tally line check` runs the named test. A failing test is normal engineering: the test is the verdict, a hint is free, and "write it" is free. The engine later records `line.survived` if the line is still there at the next commit. Your line never appears on Light or under pressure signals.

### 8.4 A normal day

- Session start: if reviews are due, one line: "2 reviews due. Say 'review' when you have a minute." Reviews are free recall, no code shown until the user commits.
- During work: at most one prediction and one explain-back per chosen task. On "urgent", "prod down", "hotfix" or a failing deploy, the engine goes quiet and offers "teach me this later" once.
- "Just tell me" always works at once, and only records that the attempt had help.
- The user's chosen reminder, if any, fires only when something is due and never while the user is at the machine where that can be detected. After three ignored reminders it stops and says so in one line [verified: research/experience-design.md].

### 8.5 A week later

The map has visibly changed: the retry topic moved from `met` to `seen` on day one and to `recalled` after a delayed review on day four. One sure miss from earlier in the week came back first. A transfer item appears with the topic name hidden, about the same idea in a different project. The map shows best level as an outline and latest as a fill, decay as a fact plus next step, never pushed as a notification. The only count anywhere is reviews due today.

### 8.6 End of a project

`tally map --project` writes a plain summary: the ideas met in this project, the levels reached, the lines the user wrote that survived, and the audit gap per construct. If the project had a repo pack, the summary shows which of the repo's key ideas the user now recalls. The user may export a **proof pack**: a signed bundle of chosen sealed items, grades and any live checks, for their own use [verified: research/evidence.md, I.2].

### 8.7 After a gap

Coming back after three weeks shows at most 3 reviews and spreads the rest over the following days. There is no backlog count and no missed-day message.

### 8.8 A team

An engineering manager buys seats. Each engineer installs Tally as usual and sees one new consent question: "Share anonymous team totals with Acme? You can see exactly what is sent first." The team adds internal packs to their repos. The manager sees, for groups of 5 or more who opted in: which pack topics are most often new, review uptake, and the audit gap per construct. The manager never sees a name next to a weak area. Mentors in the team grade attempts their mentees choose to send them.

### 8.9 A pack author

A maintainer runs `tally pack init` in their repo, names four key ideas, marks two lines the tests can grade, and runs `tally pack test`, which reports how many real instances the detectors find in the repo and in a public corpus. They sign and commit the pack. Contributors' agents pick it up on next open, with one consent each.

---

## 9. Architecture

### 9.1 Layers

From research/platform.md section 13, renamed to match the standard:

| Layer | What | Ships |
|---|---|---|
| L0 | OLL spec: record, card, moment interface, grading contract, pack format, conformance suite | v1 (1.0 of record and card; pack format as 0.x) |
| L1 | Local engine: CLI, MCP server, hook dispatcher, Room, scheduler | v1 |
| L2 | Device link to the phone: QR pairing, packs and outboxes, no server | v1 (calendar reminder), native app v2 |
| L3 | Blind relay: encrypted mailbox plus push sender, no accounts, self-hostable | v2 |
| L4 | Team plane: SSO, SCIM, region-pinned or self-hosted relays, aggregates | v2 to v3 |
| L5 | Ecosystem services: pack index, grader calibration sets, research cohort tooling | v2 onward |

### 9.2 The record and sync

- One record repo per user, outside any project tree. A project-local record (`tally init --here`) is allowed for teams that want it reviewed with the code, and refuses a public remote unless forced [verified: research/platform.md].
- The engine is the only writer. Agents never hand-edit record files.
- Sync is pluggable and opt-in: a private git remote, or the blind relay. The product never picks one silently.
- The relay uses maintained libraries (age, libsodium), never custom crypto, and publishes a plain list of everything it can see, including fire times, sizes and IP addresses, following Obsidian's practice [verified: https://obsidian.md/help/sync/security]. Self-hosting is supported from day one of the relay, learning from Anki's self-host server and its warnings about version drift [verified: https://docs.ankiweb.net/sync-server.md].

### 9.3 Pack index

An open, static index of signed packs (a git repo of pointers, not a hosted store), so any engine can search it. Ranking shows the pack's audit gap across users who opted into aggregate reporting, so a pack that teaches its own questions is visible. Whether this ranking is robust to gaming needs to be measured.

### 9.4 Efficacy built in

The standard defines a `trial` extension: when the user opts in, the engine randomly assigns new topics to receive a technique or not (for example your line on or off for that topic) and compares delayed unaided results within the person, on the device [verified: research/learning-science.md, L19; research/evidence.md, J]. Opt-in aggregates go through Prio3 over DAP via Divvi Up, which stays private if one of the two aggregators is honest [verified: https://docs.divviup.org/how-it-works]. This gives every OLL implementer, and every outside researcher, the same method for honest claims.

---

## 10. Privacy and safety

- **No network by default.** The full loop works on one offline computer. The only network calls are ones the user caused: model calls through their own agent, a remote they added, the relay they chose.
- **Telemetry off by default.** Opt-in data is aggregate only, previewed before sending, and never includes code, answers, rubrics or topic names [verified: research/platform.md, 12].
- **No keystroke, screen or time-on-task tracking.**
- **Never for hiring, never sold, no ads.** This is in the spec's purpose section and in Tally's terms. Nothing in the spec can stop a user sharing their own export, and nothing should.
- **Managers see aggregates only**, minimum group size 5, opt-in per person.
- **Packs are sandboxed**: no record access, no network, no code execution, signed, consented once.
- **Readable, exportable, deletable.** The record is plain JSON in git. `tally export` and `tally forget <topic>` (which writes a tombstone and rewrites the derived state; full history removal is the user's own git operation, documented).
- **Regulation.** The EU AI Act may treat learning-outcome grading and worker evaluation as high-risk; this is [unverified], from secondary sources such as https://casrai.org/news/ai-act-high-risk-classification. The team plane and any education licence need legal review before sale in the EU.

---

## 11. Business model

The standard and the engine stay free and open source for everyone. Money comes from things that cost us to run or that organisations need, never from the record.

| Line | Who pays | What they get | Price |
|---|---|---|---|
| Sync | Individuals | Blind relay, push reminders, native phone app with instant grading on the phone | Needs to be measured |
| Teams | Employers, per seat | Internal pack tooling, aggregates above group size 5, SSO, SCIM, region-pinned or self-hosted relay, support | Needs to be measured; comparables: Pluralsight about $399 to $779 per user per year and CodeRabbit about $24 to $48 per developer per month [unverified, from research/users-market.md] |
| Education | Bootcamps, universities, course authors | Course routes, cohort aggregates, live-check tooling for instructors | Needs to be measured |
| Grading service | Anyone who wants it | A hosted grader that meets the contract and publishes its agreement numbers; users can always bring their own agent's model instead | Needs to be measured |
| Sponsorship | Vendors, foundations | Funding for the spec, calibration sets and audit banks | n/a |

Ruled out: selling records, ads, hiring products, paid conformance certification, and paid pack placement in the index. Paid packs by third parties are allowed through their own channels; the index does not take a cut in v1, to keep incentives clean. Whether this leaves enough revenue needs to be measured.

The strategic bet is plain: if OLL becomes the format, the company that runs the best relay, team plane and grader for it has a durable business even when vendors ship their own learning modes, because those modes would write to records our services already serve.

---

## 12. What ships when

### v1: the engine and the format (individuals)

- OLL 1.0: record format, card format, moment interface, grading contract, conformance suite for engines and host adapters. Pack format as 0.x, marked experimental.
- `tally` engine with all five faces; generated adapters for Claude Code, Codex, Cursor, VS Code Copilot, Copilot CLI, Gemini CLI, Devin Local, Amp, OpenCode and Cline; the CLI floor for everything else including Aider.
- All six outcomes and the map in text on every surface, with elicitation forms where declared.
- Sealed keys, model grader with quotes, double grading, disputes, executable grading for predictions and your line.
- Visitor mode with carry-out bundles. Phone via device link and a calendar reminder.
- A small human-written audit bank for two constructs (debugging and code reading); which languages needs to be decided.
- Retention instrumentation computed locally and shown to the user: share of offered questions answered, share of due reviews done, 30-day return. Sent nowhere unless the user opts in.

### v2: the ecosystem and the services

- Pack format 1.0, pack toolchain, the open pack index, the first ten repo packs written with willing maintainers.
- Mentor grading bundles and signed live checks.
- Blind relay (paid and self-hosted), native phone app with local notifications.
- Team plane beta: internal packs, aggregates, SSO.
- Public grader calibration set and the first published agreement numbers.
- In-record trial extension and an opt-in research cohort; a preregistered randomised study begins (section 13.2).
- Offer the spec to a neutral steward if a second independent engine exists.

### Later

- Course routes on real repos with an education partner.
- Opt-in simulations built from the user's own history (reverted bugs, replayed incidents) [verified: research/learning-science.md, L16].
- Checking-agent-output drills on scratch or reversible changes, with consent [verified: research/learning-science.md, L17].
- Native OLL in at least one vendor agent, written by that vendor.

### Claims ladder

Marketing may claim only what the evidence stage allows [verified: research/evidence.md]. In v1 Tally may say what it does and what the research it builds on found. It may not say it makes people better engineers until a preregistered randomised study with a delayed, unaided, blind-graded held-out test and a speed guard set in advance has reported.

---

## 13. The five riskiest assumptions and the cheapest test for each

### 13.1 Users will answer when asked, inside real work

If people skip everything, nothing else matters. People prefer the easy path and overrate it [verified: https://arxiv.org/abs/2409.09047].

**Cheapest test:** give the current skill in this repository, packaged as a v0 engine, to 15 to 20 junior and senior volunteers on their own projects for two weeks. Measure locally: share of offered questions answered, share of due reviews done, return after 14 days, and a one-question felt-cost rating after each session. Decide the go threshold before starting; the right value needs to be measured, so set it with the volunteers' own expectations as a reference, not ours.

### 13.2 The loop makes people better without the agent, weeks later, with no real speed loss

The founding study measured immediately after one hour [verified: https://arxiv.org/html/2601.20245v2]. Delayed effects in real work are unknown.

**Cheapest test:** a within-person randomisation inside the v0 cohort: half of each person's new topics get the full loop, half are only logged. At 3 and 21 days, a short sealed unaided item per topic, graded blind. This needs no server and gives a direction, not a claim. The full preregistered trial comes in v2.

### 13.3 Third parties will write packs and adopt the format

The whole ecosystem rests on maintainers, course authors and at least one other tool writing OLL. There is no evidence for this yet [unverified].

**Cheapest test:** two parts, both cheap. First, write three repo packs ourselves for popular open-source repos and open an issue or PR on each offering it; count accepts and comments. Second, publish the 1.0 draft and ask two independent tools (for example an OpenCode or Cline plugin author, and one course author) whether they would implement the record reader role; count yeses. If neither moves, fall back to a product strategy where OLL stays our internal format with a published spec, which still gives users portability.

### 13.4 Packs can bind to real code often enough to matter

If detectors rarely fire on a learner's actual code, packs add nothing and questions stay agent-generated.

**Cheapest test:** write detectors for ten common topics and run `tally pack test` over 20 public repos of different sizes and languages. Report instances found per topic per thousand lines, and hand-check a sample for false matches. No users needed.

### 13.5 Model grading under the contract agrees with humans well enough on short answers

If grades are noisy, levels mislead and users lose trust. Published agreement varies widely [verified: https://ceur-ws.org/Vol-3772/paper10short.pdf; https://pdf.arxiv.org/pdf/2412.06910].

**Cheapest test:** collect 100 consented answers from the v0 cohort across three card kinds. Two trained people grade each against the sealed rubric. Run the contract grader twice with shuffled points. Report human-human and model-human kappa per kind and leniency in each direction, separately for phone-length and desk-length answers. Any kind below human-human agreement stays out of level changes until fixed.

---

## 14. Founder decisions: position on each

| # | Decision | Position |
|---|---|---|
| 1 | Record in local git, no remote unless asked | Accepted and written into the standard. Clarified for cloud sessions (visitor mode, ask once, carry-out by default) and the phone (projection plus outbox). OLL forbids record data in project repos by default. |
| 2 | Your line on | Accepted. A first-class card kind and outcome O5, graded by tests, declinable with one word, never on Light or under pressure. |
| 3 | At most 3 due reviews a day | Accepted and made part of the standard's budget, so two engines cannot double it. Audit items come from inside the 3. |
| 4 | One confirmation tap on the phone where no-tap is impossible | Accepted. Used for local-network phone sync. |
| 5 | Letter shortcuts off by default | Accepted and checked by the conformance suite for every host adapter that draws UI. |
| 6 | Feature parity on all surfaces | **Challenged on wording, with evidence (section 7.1).** Replaced by parity of outcome, including grading parity, verified per agent per release by the conformance suite. |
| 7 | At most one reminder a day, at the user's time | Accepted and part of the standard's budget. Reminders carry only a count and stop after three are ignored. |

---

## 15. Open questions

- Which sandboxed pattern language for detectors gives enough language coverage while staying safe to run on untrusted packs?
- How should topic merges work when two packs define the same idea differently?
- How many audit items per construct are needed, given how long users stay? Needs to be measured.
- Does delayed grading on the phone measurably hurt learning compared with instant grading? Needs to be measured.
- Will a neutral steward take a learning spec, and when should we offer it?
- Does showing the audit gap to users motivate or discourage them? Needs to be measured with felt-cost ratings, not satisfaction.

---

## 16. Sources

Research reports in this repository, each with its own sources: `design/product/research/users-market.md`, `learning-science.md`, `surfaces.md`, `platform.md`, `experience-design.md`, `evidence.md`.

External sources cited above:

- Shen and Tamkin 2026: https://www.anthropic.com/research/AI-assistance-coding-skills and https://arxiv.org/html/2601.20245v2
- Lehmann et al. 2025: https://arxiv.org/abs/2409.09047
- Kazemitabaar 2025, Lead-and-Reveal: https://arxiv.org/abs/2410.08922
- Generation effect: https://pubmed.ncbi.nlm.nih.gov/17645161/
- Testing effect: https://doi.org/10.1037/a0037559
- Spaced retrieval: https://link.springer.com/10.1007/s10648-020-09572-8
- Kerfoot 2009: https://pubmed.ncbi.nlm.nih.gov/19375095/
- Hanus and Fox 2015: https://dblp.org/rec/journals/ce/HanusF15
- Iqbal and Bailey 2008: https://www.interruptions.net/literature/Iqbal-CHI08.pdf
- Model judge bias: https://arxiv.org/abs/2306.05685v1
- Grader agreement: https://pdf.arxiv.org/pdf/2412.06910 and https://ceur-ws.org/Vol-3772/paper10short.pdf
- Koretz and Beguin, self-monitoring assessments: https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/
- BairesDev Q2 2026: https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/
- LeadDev: https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles
- CS50 tutor: https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/
- Claude Code output styles: https://code.claude.com/docs/en/output-styles
- Study and guided learning modes: https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/
- VibeWise: https://github.com/nykooi1/vibe-wise ; learn-while-build: https://github.com/Pranavraut033/learn-while-build
- AGENTS.md: https://agents.md
- Copilot cloud agent MCP: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/extend-cloud-agent-with-mcp
- Copilot hooks and cheat sheet: https://docs.github.com/en/copilot/concepts/agents/hooks and https://docs.github.com/en/copilot/reference/customization-cheat-sheet
- Copilot cloud agent limits: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent
- MCP Apps: https://modelcontextprotocol.io/extensions/apps/overview.md
- VS Code MCP: https://code.visualstudio.com/api/extension-guides/mcp
- Zed MCP and skills: https://zed.dev/docs/ai/mcp and https://zed.dev/docs/ai/skills
- Gemini CLI MCP and hooks: https://geminicli.com/docs/tools/mcp-server/ and https://geminicli.com/docs/hooks/reference/
- Codex hooks and cloud environments: https://learn.chatgpt.com/docs/hooks and https://developers.openai.com/codex/cloud/environments
- Cursor hooks and cloud agents: https://cursor.com/docs/agent/hooks and https://cursor.com/docs/cloud-agent
- Claude Code mobile and web: https://code.claude.com/docs/en/mobile.md and https://code.claude.com/docs/en/claude-code-on-the-web.md
- Devin Local customizations: https://docs.devin.ai/desktop/devin-local/customizations.md
- JetBrains ACP: https://www.jetbrains.com/help/ai-assistant/acp.html
- Amp: https://ampcode.com/docs/customize/plugins and https://ampcode.com/manual
- OpenCode skills: https://opencode.ai/docs/skills/
- Aider options: https://aider.chat/docs/config/options.html
- Tailscale DERP: https://tailscale.com/kb/1232/derp-servers
- Notification triggers: https://developer.chrome.com/docs/web-platform/notification-triggers
- Declarative Web Push: https://webkit.org/blog/16535/meet-declarative-web-push/
- iOS interruption levels: https://www.wwdcnotes.com/notes/wwdc21/10091
- SSH signed commits: https://docs.gitlab.com/user/project/repository/signed_commits/ssh.html
- Obsidian Sync security: https://obsidian.md/help/sync/security
- Anki sync server: https://docs.ankiweb.net/sync-server.md
- Divvi Up: https://docs.divviup.org/how-it-works
- Viva Insights privacy: https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings
- EU AI Act secondary source: https://casrai.org/news/ai-act-high-risk-classification
