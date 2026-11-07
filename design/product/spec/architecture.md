# Spec: architecture

Part of `../PRODUCT.md` (section 8). Builds on `../research/platform.md` and the current engine in `../../../skills/learning-while-building/scripts/`. Security detail is in `security.md`.

---

## 1. Components

| Component | Job |
| :- | :- |
| CLI | Every action, for users and for hosts without MCP |
| The pad | Engine-owned prompt in a terminal; the place for drills, bank items and widening confirmations |
| MCP server | stdio, tools only (`surfaces.md` section 7) |
| Hook dispatcher | `<absolute path>/firsthand hook <agent> <event>`; maps each agent's events to seven canonical ones: session_start, prompt_submit, before_tool, after_tool, tool_failed, turn_end, session_end [verified: research/surfaces.md section 5]. Never returns allow or deny |
| Moment engine | Decides ask or stay quiet, in code |
| Miner | Read-only scans of added repos, and of public repos for Fresh repo tasks |
| Runner | Scratch copies from committed files; containers for Replay and Fresh repo |
| Grader | Pluggable providers, off the critical path |
| Scheduler | Derived due list; one calendar file |
| Device link | Local-network cards for the phone (build step 8) |

There is no server run by the product.

Language: Python, reusing `record.py` and `learning.py`, shipped with `uvx` and `pipx`, with an npm shim [unverified: shim on Windows]. Founder decision (`../PRODUCT.md` section 13.2).

**Pinned execution:** `init` resolves the installed engine to an absolute path and writes that path into every hook and MCP entry. No hook or MCP entry ever calls `npx`, `uvx` or a bare `firsthand` on PATH. `firsthand upgrade` is the only way the engine changes.

---

## 2. Record layout

```
~/.firsthand/record/
  FORMAT                         "firsthand-record 1"
  devices/<device-id>.json       public keys and names only
  config/<key>.json              one file per preference
  projects/<project-id>.json     name, keyed hash of remote URL, ownership flag; never code
  ideas/<idea-id>.json           local view of catalog ideas, aliases, private ideas
  events/<yyyy>/<mm>/<ulid>.json one file per event, append-only (or .age when encrypted)
  sealed/<item-id>.age           keys and Fresh repo tests, encrypted to the device key
derived, never committed: schedule, due list, map, open items, budget state
outside the record: ~/.config/firsthand/ (private keys if no keychain, mode 0600), scratch dirs (0700)
```

An event:

```json
{
  "format": 1,
  "id": "01JC8Y3W8Q5V7N2K4T6R9X1M0B",
  "type": "answer.locked",
  "item": "01JC8Y2F7H3QZ5W8N1P4R6T9KD",
  "device": "dev_7f3a",
  "surface": "codex-cli",
  "engine": "firsthand/1.0.0",
  "at": "2026-11-07T14:02:11Z",
  "body": {"answer": "the key must be the same on every retry", "confidence": "think so", "help": "none", "answer_source": "typed", "format": "free"},
  "prev": "sha256:9c1e...",
  "x": {}
}
```

Event types:

- Items: `item.drafted`, `item.sealed`, `item.key_checked`, `item.shown`, `item.queued`, `item.expired`, `item.retired`.
- Answers: `answer.locked`, `key.revealed`, `grade.issued`, `grade.disputed`, `grade.uncertain`, `grade.refunded`.
- Your line: `line.opened`, `line.attempted`, `line.agent_edit`, `line.handed_back`, `line.checked`.
- PR review: `pr.findings_locked`, `pr.finding_confirmed`, `pr.settled`.
- Deep: `plan.locked`, `design.call`, `design.checked`.
- Ideas: `idea.tagged`, `idea.likely_known`, `idea.probed`, `topic.merged`, `idea.forgotten`.
- Evidence: `field.logged`, `fresh.started`, `fresh.submitted`.
- Setup: `config.set`, `device.paired`, `device.revoked`, `consent.given`, `consent.withdrawn`, `import.done`, `export.made`, `install.changed`.

Rules:

- One file per event, ULID names, union merge [verified: research/platform.md].
- Conflict rules: earliest lock wins; last `config.set` wins per key; the budget is computed per user from all devices' events.
- `x` holds extension fields keyed by reverse domain. Readers ignore unknown keys.
- **Never stored:** source code (unless excerpts are on per project, after a secret scan), secrets, keystrokes, screen contents, time spent typing, hook payloads, debug logs. Debug output goes to stderr only, when the user asks for it.
- **Secret scan on every free-text field** before write: answers, notes, field logs, PR findings. Matches are replaced with `[redacted: <kind>]` and the user is told in one line. The scanner is a maintained library or rule set, chosen in build step 2.
- **Commit guard:** the engine refuses to commit any file to the record that looks like private key material.
- **Project ids:** HMAC-SHA256 of the normalised remote URL with a per-record secret held outside the record, so a repo cannot be guessed from its id.
- The format is published as a documented spec, so other tools can read it.

### 2.1 Encryption at rest

- On by default on work computers, opt-in elsewhere.
- Each event file is encrypted with age to the user's record key. The key is held in the OS keychain, or behind a passphrase where there is none. File names stay ULIDs, so union merge still works.
- Derived state is rebuilt in memory, or cached encrypted.
- `firsthand export --plain` writes a readable copy on request, so the record outlives the product.

### 2.2 Grade fields

```json
{
  "type": "grade.issued",
  "body": {
    "points": [{"id": "p1", "met": true, "quote": "same on every retry"}],
    "graded_by": "tests",
    "grader": {"provider": "executable", "version": "1.0.0"},
    "seal": "separate-context",
    "answer_source": "typed",
    "format": "code",
    "confidence": "sure",
    "echo": false,
    "uncertain": false,
    "counts_for_level": true,
    "cap_reason": null
  }
}
```

`graded_by`: tests, model, model-pair, person, self. `answer_source`: typed, captured, relayed, imported. `cap_reason` names why a right answer did not count: same-session, relayed, guess, choice-format, grader-not-checked, asking-context, echo, imported.

### 2.3 Typed provenance

An answer is `typed` only when:

- the engine itself opened the controlling terminal (`/dev/tty`, or the Windows console) for the pad; and
- the pad process's ancestors include no known agent process and no agent environment markers (such as `CLAUDECODE`, `CLAUDE_CODE_REMOTE`) [unverified per agent: list kept in the adapter manifest and tested in conformance].

`firsthand answer` run from an agent's shell is `relayed`. A placeholder answer locked by an agent cannot release a bank or Fresh repo key, because those keys release only for typed answers.

---

## 3. Signing and tamper evidence

- `init` generates a per-device SSH signing key. The public key goes in `devices/`. The private key goes in the OS keychain, or in `~/.config/firsthand/keys/` with mode 0600, never in the record.
- Commits are signed where Git supports SSH signing (Git 2.34 or later [unverified: check in build step 2]).
- Each device keeps a hash chain in `prev`. `firsthand check` verifies signatures, chains and key hashes.
- If signing is unavailable, the engine keeps the unsigned chain and warns once.

---

## 4. Sealing

1. `item.drafted`.
2. The key is written by a context that will not ask the question: a subagent where the surface has one; else an engine-started separate process through a grader provider; else the asking context, labelled `asking-context` (cannot count).
3. **Key check:** a second blind context solves the item, executable where possible. If it disagrees, the item is discarded. `item.key_checked` records the result.
4. `item.sealed` commits the key's sha256. Only then does the item reach the user.
5. `answer.locked`. Only now is `key.revealed` possible. For bank and Fresh repo items, only after a typed lock.
6. `firsthand check` verifies hashes after reveal.

Bank items are keyed by the family's key function, written by people. Fresh repo keys are the task's tests, stored in `sealed/` and copied into the container only at grading.

---

## 5. Grading interface

```
grade(item, rubric_sealed, excerpt_shown, answer) -> GradeResult
```

| # | Provider | Used for | Moves levels | Who receives data |
| :- | :- | :- | :- | :- |
| 1 | Executable | Trace, Replay fix, your-line review, Review-first tests, Check confirmation, Fresh repo | Yes | No one |
| 2 | Person | A mentor or guide owner the user invites | Yes | That person |
| 3 | Subagent of the user's agent | Open answers | Yes, under the accuracy rules | The agent's company, under the agent's account |
| 4 | Headless agent CLI (Claude Code `-p`, Codex `exec`, Gemini CLI, Copilot CLI [verified: research/surfaces.md 10.6]) | Open answers | Yes, under the accuracy rules | The agent's company, under the agent's account |
| 5 | User API key | Open answers | Yes, under the accuracy rules | The key's company, under that key |
| 6 | Self-mark | Open answers, and the fallback | No | No one |

Rules:

- **Named recipient:** before a model provider is first used, the engine shows one line: "This sends your answer, the rubric and a short code excerpt to <company>, under <account>. Yes, or no." Consent is per provider and recorded. The excerpt is the lines the question refers to, and the user can see it.
- **`grader = local-only`** allows only providers 1, 2 and 6. Default on work computers.
- Input is exactly four fields: prompt, sealed rubric, excerpt shown, answer marked as data that may contain instructions.
- No quote, no point. Grade twice with points shuffled; disagreement sets `uncertain`.
- Providers 3 to 5 move levels under the accuracy rules (`learning.md` section 12). The regression set ships in the repo and runs as a regression test for each grader prompt and model version.
- Off the critical path: model grading is batched at session end or review time.
- Cloud sandboxes: open answers wait for the next local session.

### 5.1 Cost

- `firsthand cost` shows this week's model calls by provider, tokens where reported, and time added.
- `init` prints the instruction block's size in characters and an estimated token count for each agent it installs into. The estimate method is shown and is approximate.
- Default: no model calls until the user allows one, with an estimate.

---

## 6. Idea catalog

- Public, versioned data. Each entry: stable ID, definition, aliases, language and keyword hints, known confusions, transferable or codebase-specific.
- Seed: the common ideas of web and backend work, grown by contributors.
- `candidates(diff)` returns a fixed short list, from imports, keywords and the diff's shape. The agent picks with a confidence. It never mints IDs.
- Disagreement or missing tags: silence. A wrong tag would ask about the wrong idea or silence a real one, so silence is the safe default.
- Cluster silence needs two probes (`learning.md` section 9).

---

## 7. Cold start inference

Input: repos the user adds; author emails; an optional cut-off date. Ideas found in at least two of the user's commits with no agent trailer are marked `idea.likely_known`. They are offered less often, never silenced on inference alone. `firsthand known` lists them.

---

## 8. Fresh repo tasks

- **Task format:** a directory in the open task set with `task.toml` (repo URL, parent commit, catalog ideas, size, language, image digest), `goal.md`, and `tests/`. The tests are encrypted to the user's device key when the task is fetched, and stored in `sealed/`.
- **Mining:** `firsthand fresh mine <repo>` (and a CI job over the curated list) finds commits where a new or changed test fails on the parent and passes on the commit, with a small diff. It writes the goal in a separate context from the test names and behaviour, and rejects goals that describe the computation. Each mined task is built and run once in a container before it enters the set, so the user never gets one that does not reproduce.
- **Fetching:** the task set is a git repo the engine clones and updates on `firsthand fresh`. The user's network call goes to the public host only.
- **Running:** container rules in `security.md` section 2.

---

## 9. Cloud sessions

Detection: environment markers per surface (`CLAUDE_CODE_REMOTE=true` [verified: research/surfaces.md]; others checked in each adapter's first conformance run).

Paths, in order:

1. **The user's own private record remote,** if attached to the session. Push after each event. Events are encrypted if the record is.
2. **The import line:** `firsthand import <blob>` printed at session end, encrypted to the user's key.
3. Otherwise: in memory only, and the user was told on first run.

Imported events are checked against an allowlist of event types (answers, items shown and queued, line events, PR findings; never config, consent, grades, devices or keys), validated strictly, and capped at Met.

With the user's yes, a small list of known idea IDs (no answers, no levels) travels into the session through path 1, so silence still works.

A carry branch (encrypted events appended to a branch in a private repo the user owns) is a founder decision (`../PRODUCT.md` section 13.2, item 3). The recommendation is not to build it.

---

## 10. Phone

First: vendor apps (answers relayed, Met only), plus `firsthand reminder set HH:MM`, which writes one `.ics` with a recurring content-less event. `reminder.owner = device` keeps one reminder across devices (founder decision 7).

Build step 8, the device link:

- Binds to one chosen interface, never all interfaces. The current `room.py` binds to 127.0.0.1 by default, which is right for a laptop and cannot reach a phone.
- Pairing with one confirmation tap (founder decision 4): the QR code carries a one-time secret for a password-authenticated key exchange, from a maintained library chosen in this step, so a device on the same network cannot pair without the code.
- Packs of due cards with no keys, encrypted to the phone. Answers return encrypted to the computer. Cards are rendered by the engine's own page, so answers count as typed once the page's origin and pairing are verified.
- A secure context for the web page on each mobile browser is solved in this step [unverified per browser].

---

## 11. Migration from `learning-while-building`

1. `firsthand import-lwb [path]` finds `.learning/`, checks it with the old `learning.py check`, and runs the old `migrate` first if needed.
2. Each topic becomes an idea. Each attempt becomes `answer.locked` plus `grade.issued` with `answer_source: imported`.
3. Old levels map: not yet to Not yet, with help to Met, recalls and transfers to Recalled (capped).
4. **History disclosure:** "Your old record was committed to this repo. Removing the folder now does not remove it from git history, from forks, or from any remote." For repos the user owns, it offers a history rewrite with a maintained tool (git filter-repo [unverified: check current recommendation]) and explains that collaborators must re-clone. For repos the user does not own, it explains what to ask the owner.
5. The skill's SKILL.md becomes the T0 skill. The old scripts stay for one release.
