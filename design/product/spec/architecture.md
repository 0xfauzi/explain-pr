# Spec: architecture

Part of `../PRODUCT.md` (section 6). Builds on `../research/platform.md` and the current engine in `../../../skills/learning-while-building/scripts/`. Security detail is in `security.md`. Red-team items are cited as "RT privacy n" and so on (reviews in `../redteam/`).

---

## 1. Components

| Component | Job | v1 |
| :- | :- | :- |
| CLI | Every action, for users and for hosts without MCP | Yes |
| The pad | Engine-owned prompt in a terminal; the only place for unseen items, Checkup steps and widening confirmations | Yes |
| MCP server | stdio, tools only (`surfaces.md` section 7) | Yes |
| Hook dispatcher | `<absolute path>/firsthand hook <agent> <event>`; maps each agent's events to seven canonical ones: session_start, prompt_submit, before_tool, after_tool, tool_failed, turn_end, session_end [verified: research/surfaces.md section 5]. Never returns allow or deny | Yes |
| Moment engine | Decides ask or stay quiet, in code | Yes |
| Miner | Read-only scans of added repos | Yes |
| Runner | Scratch copies from committed files; containers for Replay and Checkup | Yes |
| Grader | Pluggable providers, off the critical path | Yes (executable and people move levels) |
| Checkup client | Talks to the Checkup service when the user starts a Checkup | Yes |
| Scheduler | Derived due list; one calendar file | Yes |
| Local page, device link, relay | | No (v2 at most) |

Language: Python for v1, reusing `record.py` and `learning.py`, shipped with `uvx` and `pipx`, with an npm shim [unverified: shim on Windows]. Hook latency needs to be measured per agent in conformance.

**Pinned execution** (RT privacy 3): `init` resolves the installed engine to an absolute path and writes that path into every hook and MCP entry. No hook or MCP entry ever calls `npx`, `uvx` or a bare `firsthand` on PATH. `firsthand upgrade` is the only way the engine changes.

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
  sealed/<item-id>.age           practice keys, encrypted to the device key
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
- Your line: `line.opened`, `line.attempted`, `line.read_test_first`, `line.agent_edit`, `line.handed_back`, `line.checked`.
- PR review: `pr.findings_locked`, `pr.finding_confirmed`, `pr.settled`.
- Ideas: `idea.tagged`, `idea.likely_known`, `idea.probed`, `topic.merged`, `idea.forgotten`.
- Evidence: `field.logged`, `checkup.started`, `checkup.result`, `livecheck.recorded`.
- Experiments: `experiment.assigned` (sealed, never shown on cards).
- Setup: `config.set`, `device.paired`, `device.revoked`, `consent.given`, `consent.withdrawn`, `import.done`, `export.made`, `install.changed`.

Rules:

- One file per event, ULID names, union merge [verified: research/platform.md].
- Conflict rules: earliest lock wins; last `config.set` wins per key; the budget is computed per user from all devices' events.
- `x` holds extension fields keyed by reverse domain. Readers ignore unknown keys.
- **Never stored:** source code (unless excerpts are on per project, after a secret scan), secrets, keystrokes, screen contents, time spent typing, hook payloads, debug logs (RT privacy 12). Debug output goes to stderr only, when the user asks for it.
- **Secret scan on every free-text field** before write: answers, notes, field logs, PR findings (RT privacy 8). Matches are replaced with `[redacted: <kind>]` and the user is told in one line. The scanner is a maintained library or rule set [unverified: which one; choose in v1].
- **Commit guard:** the engine refuses to commit any file to the record that looks like private key material, and never writes keys there.
- **Project ids:** HMAC-SHA256 of the normalised remote URL with a per-record secret held outside the record (RT privacy 12).
- The format is published as a documented spec in v1.

### 2.1 Encryption at rest

- **On by default on work installs, opt-in elsewhere** (RT privacy 1).
- Each event file is encrypted with age to the user's record key. The key is held in the OS keychain, or behind a passphrase where there is none. File names stay ULIDs, so union merge still works.
- Derived state is rebuilt in memory, or cached encrypted.
- `firsthand export --plain` writes a readable copy on request, so the record outlives the product.
- Stated limit: an employer that controls the device and the binary can read the record while the user has it unlocked. `firsthand verify` checks the running binary is a signed release; it cannot defeat a hostile device owner.

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

`graded_by`: tests, model, model-pair, person, proctored, self. `answer_source`: typed, captured, relayed, imported, carried. `cap_reason` names why a right answer did not count: same-session, relayed, guess, choice-format, ungated-grader, asking-context, echo, imported, carried.

### 2.3 Typed provenance

An answer is `typed` only when (RT privacy 4):

- the engine itself opened the controlling terminal (`/dev/tty`, or the Windows console) for the pad; and
- the pad process's ancestors include no known agent process and no agent environment markers (such as `CLAUDECODE`, `CLAUDE_CODE_REMOTE`) [unverified per agent: list kept in the adapter manifest and tested in conformance].

`firsthand answer` run from an agent's shell is `relayed`. A placeholder answer locked by an agent cannot release an unseen or Checkup key, because those keys release only for typed answers.

Stated limit: a user can start the pad and paste what the agent told them. Typed provenance shows the agent did not type it, not that the user worked alone.

---

## 3. Signing and tamper evidence

- `init` generates a per-device SSH signing key. The public key goes in `devices/`. **The private key goes in the OS keychain, or in `~/.config/firsthand/keys/` with mode 0600, never in the record** (RT privacy 8).
- Commits are signed where Git supports SSH signing [unverified: Git 2.34 or later; check before v1].
- Each device keeps a hash chain in `prev`. `firsthand check` verifies signatures, chains and key hashes.
- If signing is unavailable, the engine keeps the unsigned chain and warns once.

---

## 4. Sealing

1. `item.drafted`.
2. The key is written by a context that will not ask the question: a subagent where the surface has one; else an engine-started separate process through a grader provider; else the asking context, labelled `asking-context` (cannot count).
3. **Key check:** a second blind context solves the item, executable where possible. If it disagrees, the item is discarded. `item.key_checked` records the result (RT efficacy 11).
4. `item.sealed` commits the key's sha256. Only then does the item reach the user.
5. `answer.locked`. Only now is `key.revealed` possible. For unseen and Checkup items, only after a typed lock.
6. `firsthand check` verifies hashes after reveal.

Unseen family items are keyed by the family's key function, written by people. Checkup keys are hidden tests on the service.

---

## 5. Grading interface

```
grade(item, rubric_sealed, excerpt_shown, answer) -> GradeResult
```

| # | Provider | Used for | Moves levels in v1 | Who receives data |
| :- | :- | :- | :- | :- |
| 1 | Executable | Trace, Replay fix, your-line review, Review-first tests, Check confirmation | Yes | No one |
| 2 | Person | Studies, courses, owners in guides | Yes | That person |
| 3 | Subagent of the user's agent | Open answers | No, until gated | The agent's company, under the agent's account |
| 4 | Headless agent CLI (Claude Code `-p`, Codex `exec`, Gemini CLI, Copilot CLI [verified: research/surfaces.md 10.6]) | Open answers | No, until gated | The agent's company, under the agent's account |
| 5 | User API key | Open answers | No, until gated | The key's company, under that key |
| 6 | Self-mark | Fallback | No | No one |

Rules:

- **Named recipient** (RT privacy 6): before a model provider is first used, the engine shows one line: "This sends your answer, the rubric and up to 40 lines of code (design default) to <company>, under <account>. Yes, or no." Consent is per provider and recorded.
- **`grader = local-only`** allows only providers 1, 2 and 6. Default on work installs.
- Input is exactly four fields: prompt, sealed rubric, excerpt shown, answer marked as data that may contain instructions.
- No quote, no point. Grade twice with points shuffled; disagreement sets `uncertain`.
- **The gate** is per grader model and version, from `learning.md` section 6. Results are published per task type and grader version.
- **Audit sampling** of undisputed grades (`learning.md` section 6).
- Off the critical path: model grading batched at session end or review time.
- Cloud sandboxes: open answers wait for the next local session.

### 5.1 Cost

- `firsthand cost` shows this week's model calls by provider, tokens where reported, and time added.
- `init` prints the instruction block's size in characters and an estimated token count for each agent it installs into (RT market 8). The estimate method (characters divided by a fixed ratio) is shown and is approximate.
- Default: no model calls until the user allows one, with an estimate.

---

## 6. Idea catalog

- Public, versioned data. Each entry: stable ID, definition, aliases, language and keyword hints, known confusions, transferable or codebase-specific.
- Seed size: a few hundred common web and backend ideas (design default).
- `candidates(diff)` returns a fixed short list. The agent picks with a confidence. It never mints IDs.
- Disagreement or missing tags: silence.
- Cluster silence needs two probes (`learning.md` section 11).

---

## 7. Cold start inference

Input: repos the user adds; author emails; an optional cut-off date. Ideas found in at least two of the user's commits with no agent trailer are marked `idea.likely_known`. They are offered less often, never silenced on inference alone (RT efficacy 8). `firsthand known` lists them.

---

## 8. Cloud sessions

Detection: environment markers per surface (`CLAUDE_CODE_REMOTE=true` [verified: research/surfaces.md]; others [unverified], probed in conformance).

Paths, in order:

1. **The user's own private record remote,** if attached to the session. Push after each event. Events are encrypted if the record is.
2. **(v2) The relay.**
3. **(v1.1) The carry branch** (RT privacy 10):
   - Offered only in private repos the user owns (host API check where available [unverified per host]; unknown means not offered).
   - **The local engine creates the branch in advance,** with a random neutral name (`sync/<random>`), and records the name in the record. A cloud session may only append to a branch whose name the user's own engine created. A cloud session that finds none uses path 4.
   - Events are encrypted with age to the user's device keys.
   - **Import:** only an allowlist of event types (`answer.locked`, `item.shown`, `item.queued`, `line.*`, `pr.findings_locked`). Never `config.set`, `consent.*`, `grade.*`, `device.*`, `key.*`. Each file is validated against a strict schema; unknown fields rejected; size limits enforced. Imported events are marked `carried, unauthenticated` and capped at Met.
   - The engine deletes only branches it created, by recorded name, never by pattern.
   - The prompt says: "Collaborators can see that this branch exists, when it was pushed and how big it is. Deleting it does not erase it: GitHub keeps commits readable by hash." [verified: https://trufflesecurity.com/blog/anyone-can-access-deleted-and-private-repo-data-github]
   - A shipped CI check fails any PR that contains a carry file.
4. **The import line:** `firsthand import <blob>` printed at session end, encrypted to the user's key. Default in every repo the user does not own, and in v1 everywhere.
5. Otherwise: in memory only, and the user was told on first run.

With the user's yes, a small list of known idea IDs (no answers, no levels) travels into the session through path 1 or 2 so silence still works.

---

## 9. Phone

v1: vendor apps (answers relayed, Met only), plus `firsthand reminder set HH:MM`, which writes one `.ics` with a recurring content-less event. `reminder.owner = device` keeps one reminder across devices (decision 7).

v2, after E12: the device link.

- Binds to one chosen interface, never all interfaces. The current `room.py` binds to 127.0.0.1 by default, which is right for a laptop and cannot reach a phone (RT privacy 12).
- Authenticated pairing: the QR code carries a one-time secret for a password-authenticated key exchange [unverified: choose a maintained library], so a device on the same network cannot pair without the code.
- Packs of due cards with no keys, encrypted to the phone. Answers back encrypted to the computers. Cards are rendered by the engine's own page, so answers count as typed only if the page's origin and pairing are verified.
- Secure context for a web app must be solved in the prototype [unverified per browser].

v2, paid: web push through the relay [verified: https://webkit.org/blog/16535/meet-declarative-web-push/].

---

## 10. The Checkup service

- Serves Checkup tasks and the study-only pool. Holds hidden tests. Runs them on a submitted patch in its own sandbox. Signs results.
- Identity: an anonymous token per install, no account, no email. The service logs token, task id, time and outcome, so tasks can be retired and exposure counted. It never receives the record.
- The user starts every call. `firsthand checkup` says what will be sent before the first call: the token, the task id, and later the patch.
- Patches are to public repos, written by the user. They are kept only as long as needed to run tests and sign (retention period is a design default, stated on the site).
- Results are signed with a published service key. `firsthand checkup verify <file>` and a small public verifier check the signature.

---

## 11. Migration from `learning-while-building`

1. `firsthand import-lwb [path]` finds `.learning/`, checks it with the old `learning.py check`, and runs the old `migrate` first if needed.
2. Each topic becomes an idea. Each attempt becomes `answer.locked` plus `grade.issued` with `answer_source: imported`.
3. Old levels map: not yet to Not yet, with help to Met, recalls and transfers to Recalled (capped).
4. **History disclosure** (RT privacy 11): "Your old record was committed to this repo. Removing the folder now does not remove it from git history, from forks, or from any remote." For repos the user owns, it offers a history rewrite with a maintained tool (git filter-repo [unverified: check current recommendation]) and explains that collaborators must re-clone. For repos the user does not own, it explains what to ask the owner.
5. The skill's SKILL.md becomes the T0 skill. The old scripts stay for one release.
