# Spec: architecture

Part of `../PRODUCT.md` (section 6). Builds on `../research/platform.md` and the current engine in `../../../skills/learning-while-building/scripts/`.

---

## 1. Components

| Component | Job | v1 |
| :- | :- | :- |
| CLI | Every action, for users and for hosts without MCP | Yes |
| MCP server | stdio, tools only for the core (`surfaces.md` section 7) | Yes |
| Hook dispatcher | `firsthand hook <agent> <event>`; maps each agent's events to seven canonical ones: session_start, prompt_submit, before_tool, after_tool, tool_failed, turn_end, session_end [verified: research/surfaces.md section 5] | Yes |
| Moment engine | Decides ask or stay quiet, in code | Yes |
| Miner | Read-only scans of added repos; builds Trace, Check and Replay drills in scratch directories | Yes (Replay gated by E2) |
| Grader | Pluggable providers, off the critical path | Yes |
| Scheduler | Derived due list; one OS-level reminder entry or calendar file | Yes (calendar file) |
| Local page (Room) | Map and drills in a browser | No, v2 at most |
| Device link | Phone pairing | No, v2 after E12 |
| Relay | Encrypted mailbox and push | No, v2 paid |

Language: Python for v1, reusing `record.py` and `learning.py`, shipped with `uvx` and `pipx`, with an npm shim that runs the Python package [unverified: shim approach to be tested on Windows]. Hook latency must stay small; it needs to be measured per agent in conformance.

---

## 2. Record layout

```
~/.firsthand/record/
  FORMAT                         "firsthand-record 1"
  devices/<device-id>.json       public keys and names
  config/<key>.json              one file per preference
  projects/<project-id>.json     name, path hint, hash of remote URL; never code
  ideas/<idea-id>.json           local view of catalog ideas, aliases, private ideas
  events/<yyyy>/<mm>/<ulid>.json one file per event, append-only
  sealed/<item-id>.age           encrypted keys
derived, never committed: schedule, due list, map, open items, budget state
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
  "body": {"answer": "the key must be the same on every retry", "confidence": "think so", "help": "none", "answer_source": "typed"},
  "prev": "sha256:9c1e...",
  "x": {}
}
```

Event types:

- Items: `item.drafted`, `item.sealed`, `item.shown`, `item.queued`, `item.expired`.
- Answers: `answer.locked`, `key.revealed`, `grade.issued`, `grade.disputed`, `grade.uncertain`.
- Your line: `line.opened`, `line.attempted`, `line.agent_edit`, `line.handed_back`, `line.checked`, `line.survived`.
- Ideas: `idea.tagged`, `idea.likely_known`, `idea.probed`, `topic.merged`.
- Evidence: `field.logged`, `checkup.taken`, `livecheck.recorded`.
- Experiments: `experiment.assigned` (sealed, never shown on cards).
- Setup: `config.set`, `device.paired`, `device.revoked`, `consent.given`, `consent.withdrawn`, `import.done`, `export.made`.

Rules:

- One file per event, ULID names, union merge, no CRDT library [verified: research/platform.md].
- Conflict rules: earliest lock wins; last `config.set` wins per key; the budget is computed per user from all devices' events.
- `x` holds extension fields keyed by reverse domain. Readers ignore unknown keys.
- Never stored: source code (unless excerpts are turned on per project, after a secret scan), secrets, keystrokes, screen contents, time spent typing.
- The format is published as a documented spec in v1 (open question 7 in `../PRODUCT.md` section 13).

### 2.1 Grade fields

```json
{
  "type": "grade.issued",
  "body": {
    "points": [{"id": "p1", "met": true, "quote": "same on every retry"}],
    "graded_by": "model",
    "grader": {"provider": "headless-agent", "agent": "claude-code", "version": "1.0.0"},
    "seal": "separate-context",
    "answer_source": "typed",
    "echo": false,
    "uncertain": false,
    "counts_for_level": true,
    "cap_reason": null
  }
}
```

`graded_by`: tests, model, model-pair, person, proctored, self. `seal`: separate-context, asking-context. `answer_source`: typed, captured, relayed, imported. `cap_reason` names why a correct answer did not move the level.

---

## 3. Signing and tamper evidence

- `init` generates a per-device SSH signing key in the record's device folder, with the private key in the OS keychain where available. It does not depend on the user's existing SSH setup.
- Commits are signed with it where Git supports SSH signing [unverified: Git 2.34 or later and a recent OpenSSH, from memory; check before v1].
- Each device keeps a hash chain in `prev`. `firsthand check` verifies signatures, chains and key hashes.
- If signing is unavailable, the engine keeps the unsigned chain and warns once. It never fails.
- External timestamping of key hashes is opt-in, for study participants.

---

## 4. Sealing

1. `item.drafted`.
2. The key is written by a context that will not ask the question: a subagent where the surface has one; else an engine-started separate process through a grader provider; else the asking context, labelled `asking-context`.
3. `item.sealed` commits the key's sha256. Only after that commit does the item reach the user.
4. `answer.locked`. Only now does `key.revealed` become possible. Any request for a key before lock gets a refusal.
5. `firsthand check` verifies hashes after reveal.

Asking-context items cap at Seen. Stated limit: an agent with the code can always rebuild an answer.

---

## 5. Grading interface

```
grade(item, rubric_sealed, excerpt_shown, answer) -> GradeResult
```

Providers, in order of preference; the engine uses the first available and allowed one for the task type.

| # | Provider | Used for | Availability |
| :- | :- | :- | :- |
| 1 | Executable | Trace, Replay fix, your line, predictions, Check against known defect lines | Everywhere with a shell |
| 2 | Subagent of the user's agent | Open answers | Surfaces with subagents (Claude Code, Devin [verified: research/surfaces.md]); others [unverified] |
| 3 | Headless agent CLI | Open answers, rubric authoring | Claude Code `-p`, Codex `exec`, Gemini CLI non-interactive, Copilot CLI [verified: research/surfaces.md 10.6]; cost, quota and terms [unverified] until E8 |
| 4 | User API key | Open answers | Wherever the user sets one |
| 5 | Self-mark | Fallback | Everywhere; caps at Seen |

Rules (from `../concepts/open-standard.md` 4.6 and `../research/evidence.md` D.3):

- Input is exactly four fields: prompt, sealed rubric, excerpt shown, answer marked as data that may contain instructions. Not the session, confidence, help level, history or name.
- No quote, no point.
- Grade twice with points shuffled; disagreement sets `uncertain`, shows both, holds the level.
- Echo flag when quoted spans nearly copy agent text from the session.
- One dispute per grade, one regrade against the same key.
- **Agreement gate:** a task type moves levels only after its model-human agreement is measured (E5) and is within the margin of human-human agreement. Results are published per task type and grader version.
- **Off the critical path:** model grading is batched at session end or at review time. Only executable grading is immediate.
- **Cloud sandboxes:** if no provider can run (no nested agent call, no key), open answers wait for the next local session.

### 5.1 Cost

- `firsthand cost` shows, for this week: model calls by provider, tokens where the agent reports them, and wall time added to sessions.
- The user sets a weekly budget. Default: no headless or API-key calls until the user allows them at first need, with an estimate shown.
- Task time with the product on versus off is a guard metric (`measurement.md`).

---

## 6. Idea catalog

- Public, versioned data, not code. Each entry: stable ID, one-sentence definition, aliases, language and keyword hints, known confusions, transferable or codebase-specific.
- Seed size: a few hundred common web and backend ideas (design default, the right size needs to be measured), plus the topics the current skill already records.
- `candidates(diff)` returns a fixed short list from the catalog by language, file and keyword matching. The agent picks from it with a confidence. It never mints free-form IDs.
- Disagreement or missing tags: silence.
- Cluster silence: a passed probe silences the idea and all its aliases in every project.
- `topic.merged` joins ideas without rewriting history.
- Private ideas: users and teams add them under their own namespace.

---

## 7. Cold start inference

- Input: repos the user adds; the user's author emails; an optional cut-off date ("before I used agents").
- Commits by the user with no agent co-author trailer, before the cut-off, are scanned with the same `candidates` matcher.
- Ideas found in at least two such commits are marked `idea.likely_known` (design default, needs to be measured in E11). They carry no level and cause silence.
- `firsthand known` lists them; the user can remove any.

---

## 8. Cloud sessions

Detection: environment markers per surface (`CLAUDE_CODE_REMOTE=true` [verified: research/surfaces.md]; others [unverified], probed in conformance).

Order of paths:

1. The user's own private record remote, if attached to the session (Claude Code on the web can attach further repositories [verified: research/platform.md 6.2]; others [unverified]). Push after each event.
2. (v2) The relay, if the user has Sync and the session allows its host.
3. The carry branch, if the user said yes once for this repo and the repo is not public: events encrypted with age to the user's device keys, committed on `firsthand-carry/<random>` only, never on the working branch. The local engine fetches, imports, verifies, and deletes the branch. A shipped CI check fails any PR that contains a carry file. Detection of a public repo uses the host's API where available [unverified per host]; if unknown, the option is not offered.
4. Fallback: a `firsthand import <blob>` line printed at session end.
5. Otherwise: in memory only, and the user was told on first run.

Silence on known ideas is weaker in cloud sessions, because the full record is not there. With the user's yes, a small list of known idea IDs (no answers, no levels) travels into the session through path 1 or 2.

---

## 9. Phone

v1: vendor apps (sessions arrive as normal sessions), plus `firsthand reminder set HH:MM`, which writes one `.ics` with a recurring event "Review time". It cannot know whether anything is due, and settings say so (research/platform.md 6.4). `reminder.owner = device` keeps one reminder across devices (decision 7).

v2, after E12: device link. Pack of due cards with no keys, encrypted to the phone; outbox of locked answers encrypted to the computers; QR pairing in the Tailscale pattern, keys never leave devices [verified: https://tailscale.com/kb/1232/derp-servers]. Transport by local network, file or QR. Secure context for a web app must be solved in the prototype: a plain http LAN origin does not get a service worker [unverified per browser]. Choice and number cards grade on the phone after lock; open answers wait.

v2, paid: relay with web push for the reminder, which needs a sender [verified: https://webkit.org/blog/16535/meet-declarative-web-push/]. Scheduled local web notifications never shipped [verified: https://developer.chrome.com/docs/web-platform/notification-triggers]. On iOS, reminders use the passive or active level, never time-sensitive.

---

## 10. Privacy and threat model summary

| Threat | Mitigation |
| :- | :- |
| Teammates or reviewers see a user's misses | No record data in project branches; carry branch encrypted, side-only, merge-blocked, not offered in public repos |
| Employer reads records | No admin key exists; nothing on by default; sharing is per person, opt-in |
| Lenient grader adapts key to answer | Sealing before asking; blind grader input |
| Prompt injection inside an answer | Answer passed as delimited data; quoted spans required (Li et al. 2026 preprint, research/evidence.md A.2 item 8) |
| Agent reads unseen questions | Encrypted at rest, decrypted only in engine process, served only on direct-render surfaces; stated limit |
| Replay runs hostile historical code | User's own repos only, per-repo opt-in, throwaway worktree, time limit, network off where possible |
| Relay operator (v2) | Ciphertext only; published list of visible metadata |
| Silent plan spend | Grading budget, consent at first need, visible cost |

Cryptography: age and libsodium, no custom crypto.

---

## 11. Migration from `learning-while-building`

1. `firsthand import-lwb [path]` finds `.learning/` (or a `--dir` record), checks it with the old `learning.py check`, and runs the old `migrate` first if it is single-file.
2. Each topic becomes an idea (mapped to a catalog ID where the name matches an alias, else private). Each attempt becomes `answer.locked` plus `grade.issued` with `answer_source: imported`, `graded_by: model`, `seal: asking-context`.
3. Old levels map: not yet to Not yet, with help to Seen, recalls to Recalled, transfers to Recalled (capped: no family or distance recorded).
4. The engine offers to remove `.learning/` from the project repo in a commit the user reviews.
5. The skill's SKILL.md is rewritten as the T0 skill that calls `firsthand`. The old scripts stay available for one release.
