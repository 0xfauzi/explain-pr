# Spec: architecture

Part of `../PRODUCT.md`. This is the technical design for the model in `learning.md`: thirteen moments, eight drills, checks run on the real project, and the Room. Anything a person sees on screen is defined in `experience.md`, which wins where the two differ.

It builds on `../research/platform.md`, `../research/surfaces.md` and the current engine in `../../../skills/learning-while-building/scripts/`. Security detail is in `security.md`. Per-agent detail is in `surfaces.md`. The first two build steps are specified in `build-1.md` and `build-2.md`.

Hook facts marked [unverified] come from memory of each agent's documentation, not from the research files. They are confirmed against the hook reference when that adapter is written.

---

## 1. Components

| Component | Job |
| :- | :- |
| Engine daemon | One background process per user. Owns the record, the timeline, the runner queue, the Room server and the scheduler. Everything else is a thin client |
| Hook dispatcher | `<absolute path>/firsthand hook <agent> <event>`. Reads the agent's JSON on stdin, keeps an allowlist of fields, appends one line to a spool file and exits. Never returns allow, deny or ask. Never blocks |
| MCP server | stdio, tools only (`surfaces.md` section 7). A client of the daemon |
| CLI | Every action, for the person and for agents with only a shell |
| Timeline | Turns events and git state into tasks, changes and bases (`learning.md` section 3.3) |
| Git watch | Reads the project's git state on each event and on a slow poll while a session is live |
| Moment engine | Decides in code whether to ask (`learning.md` section 6). One module per moment |
| Check runner | Runs checks in scratch copies and containers. Never writes to the project (section 7) |
| Key store | Holds check results until the call is locked (section 3) |
| Reader and writer | Isolated model contexts: one writes a test from a sentence, one reads free text against points (section 4) |
| Scheduler | The due list for reviews, dated decisions and the one daily reminder |
| Room server | Local web app on 127.0.0.1 (section 8) |

There is no server run by the product. There is no telemetry. Language: Python, reusing the existing engine. Founder decision.

### 1.1 The shape

```
  coding agent (any)                            the person
  +-----------------------------+               +------------------------+
  | hooks     MCP tools   shell |               | browser      phone     |
  +---+----------+----------+---+               +----+-----------+-------+
      | events   | moment,  | firsthand ...          | 127.0.0.1 | same network,
      | (spool)  | answer   |                        | session   | paired
      v          v          v                        v           v
  +-------------------------------------------------------------------------+
  |  ENGINE DAEMON (one per user)                                           |
  |                                                                         |
  |  timeline <-- git watch          Room server (inbox, cards, journal,    |
  |     |                            system, skills, drills)                |
  |     v                                 ^             |                   |
  |  moment engine -- picks one --> check runner        | call              |
  |     |                                 |             v                   |
  |     |  question text + link only      +--> key store --> score          |
  |     v                                 |                    |            |
  |  agent line / card              scratch copies             v            |
  |  scheduler (reviews, reminder)  containers            the record        |
  +-------------------------+------------+--------------------+-------------+
                            |            |                    |
                 reads only v            v                    v
              project repo (never   ~/.firsthand/cache   ~/.firsthand/record
              written by the engine) snapshots, deps,    local git repo, plain
                                     scratch (0700)      JSON, no remote
```

### 1.2 Process model

- **The daemon starts on demand.** The first hook, MCP call or CLI call starts it detached. It exits after a period with no live session, no open Room tab and no queued check.
- **Hooks never lose an event and never wait.** The dispatcher appends the allowlisted event as one JSON line to `~/.firsthand/run/spool.jsonl` and exits. If no daemon is running it starts one, detached, and still exits at once. The daemon tails the spool. The first prompt of the day sets a task's base, so it must not be dropped.
- **Local socket.** A Unix domain socket in `~/.firsthand/run/` (mode 0700) for the MCP server and the CLI. On Windows a named pipe limited to the user [unverified: checked when the Windows build is made].
- **One writer.** Only the daemon writes the record.
- **Sessions.** Keyed by agent, the agent's session id and the project root, found by walking up from the event's working directory to the git root.

### 1.3 Code layout and reuse

```
firsthand/
  record.py     from scripts/record.py: JSON read and write, intervals, DURABLE_AFTER_DAYS,
                DEFAULT_DUE_LIMIT. Extended with the event store and the skill ladder
  schedule.py   from learning.py: due rows, interleave. Extended with dated items
  room/         from room.py: the stdlib HTTP server, size limits, the write lock.
                Extended with sessions, live updates and pairing
  daemon.py     spool reader, socket, session table, single writer
  hooks.py      dispatcher and the per-agent event tables
  adapters/     one manifest per agent: files written, event names, output shapes, flags
  timeline.py   tasks, changes, bases, outside events, active time
  gitwatch.py   diff against base, path categories, commits and refs
  moments/      one module per moment: match, plan, key, score, cue
  runner/       snapshot, scratch, test adapters, database, fault, container
  extract/      optional extractors per stack (section 6)
  keys.py       the key store and the one output rule (section 3)
  reader.py     isolated writer and reader providers
  mcp.py, cli.py
```

Every moment is one module with five functions:

| Function | Does |
| :- | :- |
| `match(break, timeline)` | Returns a candidate if the trigger in `learning.md` section 4 holds |
| `plan(candidate)` | The runner steps for the check, with its control, and the extractors it needs |
| `key(result)` | Turns the runner result into the key |
| `score(call, key)` | Match, miss or unscored with a reason. The outcome kind |
| `cue(call, key)` | The "what would have shown it" line (`learning.md` section 7.4) |

Dependencies: the standard library, and a tree-sitter binding for the reference search. The MCP server is plain JSON-RPC over stdio.

**Pinned execution.** `init` installs the engine to `~/.firsthand/engine/<version>/` and writes that absolute path into every hook and MCP entry. No hook or MCP entry calls `npx`, `uvx` or a bare `firsthand` on PATH. `firsthand upgrade` is the only way the engine changes.

---

## 2. Record layout

The record is a local git repo outside any project. No remote unless the person asks. Founder decision.

```
~/.firsthand/record/
  FORMAT                           "firsthand-record 1"
  config/<key>.json                one file per setting
  projects/<project-id>.json       name, test command, path patterns, marks. Never code
  ideas/<idea-id>.json             ideas met, with their history
  events/<yyyy>/<mm>/<ulid>.json   one file per event, append-only
```

An event:

```json
{
  "format": 1,
  "id": "01JC8Y3W8Q5V7N2K4T6R9X1M0B",
  "type": "call.sealed",
  "project": "prj_3b9f52c1a7e0",
  "change": "01JC8XZ0M4T1A7C3E5G8J2K6P9",
  "moment": "01JC8Y2F7H3QZ5W8N1P4R6T9KD",
  "surface": "claude-code",
  "engine": "firsthand/0.1.0",
  "at": "2026-11-07T14:02:11Z",
  "body": {
    "moment_kind": "revert_test",
    "form": "pick",
    "answer": "none",
    "channel": "room",
    "case_chosen_by": "engine"
  },
  "x": {}
}
```

Event types are the table in `learning.md` section 10, plus setup events: `config.set`, `device.paired`, `device.revoked`, `consent.given`, `import.done`, `install.changed`.

Rules:

- One file per event, ULID names. The daemon commits in batches: at each lock, at each done signal and when a change lands. Plain git commits, unsigned.
- `x` holds extension fields keyed by reverse domain. Readers ignore unknown keys.
- **What an event may hold** follows `learning.md` section 10: paths, line numbers, test ids, symbol names, counts, hashes, commands and the person's own words. Never source code, the agent's text, secrets, hook payloads or debug logs.
- **Tree references.** `check.ran` and `episode.*` name trees by git hash. The trees live in the snapshot store (section 7.1), outside the record. If a snapshot has been pruned the event still stands and the drill that needs it is not offered.
- **Secret scan on every free-text field** before write. Matches are replaced with `[redacted: <kind>]` and the person is told in one line.
- **Project ids:** `prj_` plus the first twelve hex characters of the SHA-256 of the repo's root commit hash. Clones and worktrees share one id. The record is local, so the id does not need to hide anything.
- The format is published as a documented spec, so other tools can read it.

### 2.1 Score fields

```json
{
  "type": "call.scored",
  "body": {
    "result": "match",
    "checked_by": "runner",
    "check": "01JC8Y2H...",
    "outcome_kind": "uncommon",
    "catch": true,
    "unscored_reason": null
  }
}
```

`checked_by`: runner, search, timeline, model-read. `unscored_reason`: outcome-never-arrived, check-unavailable, person-chose-case, shown-first, symptom-patch, readers-disagree, not-my-case.

`channel` on a call is `room` or `chat`. It is recorded for the person's information and does not affect scoring (`learning.md` section 7.2).

### 2.2 Outside the record

| Place | Holds | Why not in the record |
| :- | :- | :- |
| `~/.firsthand/cache/snapshots/<project-id>.git` | Tree objects for snapshots | Source code |
| `~/.firsthand/cache/deps/<project-id>/` | Carried dependency folders for the runner | Large, rebuildable |
| `~/.firsthand/cache/extract/<project-id>/` | Extractor output (section 6) | Derived |
| `~/.firsthand/run/` | Spool, socket, scratch folders (0700), pending keys (0600), lock files | Short-lived |
| `~/.config/firsthand/` | The Room port, paired device tokens (0600), install backups | Settings and secrets |
| `~/.firsthand/engine/<version>/` | The installed engine | Code |

`firsthand forget --project <name>` removes that project's cache folders along with its events.

---

## 3. Keys and the one output rule

A key is what the person's call will be compared with: a check result. The requirement is small: **nothing the engine gives the agent carries a key or a result before the call is locked, skipped or closed.**

- **One function enforces it.** Every output to an agent (MCP tool result, hook output, CLI output when an ancestor process is an agent) passes through `keys.agent_output()`. Before a lock it can return only question text and a link.
- **Where a key lives.** In the daemon's memory, and in `~/.firsthand/run/keys/<moment-id>.json` (mode 0600) so a daemon restart does not lose it. It is deleted after scoring. It is never in the record before the lock.
- **Call before key.** For most runner checks the card is shown once the control passes. If the person locks first, the call is stored and the key is produced after. The engine holds both. Keys that arrive later (Where to look, Time call, Brief) are timeline facts that do not exist yet when the call is made.
- **Shown first.** If a fact line or hazard line about the same check is printed before the lock (`learning.md` section 6.4), the call is unscored with reason `shown-first`.
- **After the lock** the result is the person's. A finding goes to the agent as one line unless the person turned that off. The call and whether it matched never go.

What this does and does not stop: it stops a key reaching the agent's context by accident, which is what would spoil a call. It does not stop a process running as the person from reading the daemon's files. The record is the person's own and cheating it gains nothing, so no more machinery is spent here: no signing, no hash chain, no encryption of keys. `firsthand privacy` states the limit once.

A conformance test fails any adapter where a key string appears in the agent's context before the lock.

---

## 4. Reading and writing with a model

Most checks use no model. `learning.md` section 7.1 lists where one is involved.

```
write(kind, material, sentence)                 -> a test or query, restated in plain words
read(question, points, excerpt, answer)         -> points met, each with a quote
```

| # | Provider | Started by | Who receives data |
| :- | :- | :- | :- |
| 1 | Headless agent CLI (Claude Code `-p`, Codex `exec`, Gemini CLI, Copilot CLI [verified: research/surfaces.md 10.6]) | The daemon, in an empty temp folder, with no tools and none of the person's agent config | The agent's company, under the person's account |
| 2 | Local model endpoint the person names | The daemon | No one outside the machine |
| 3 | The person's API key | The daemon | The key's company |
| 4 | None | | Text parts are shown unscored. Missing case and Invariant are offered at Deep, where the person writes the test or constraint |

Rules:

- **Isolation.** The daemon starts the provider itself. The building agent is never asked to grade or to write a key.
- **Four fields in for a read:** the question, the points, the excerpt, and the answer marked as untrusted data that may contain instructions.
- **No quote, no point. Two passes must agree.** Disagreement leaves the call unscored.
- **Named recipient, asked once.** Before a provider is first used the Room shows one line: "This sends your answer and a short excerpt to <company>, under <account>. Yes, or no." On a work computer the question is put in terms the person can judge: "Your agent already sends this code to <company>. Use the same account to read your text answers?"
- **Default:** no model call until the person says yes.
- **Off the critical path.** A writer starts only after its moment is picked. Reading is batched when the outcome arrives or at review time.
- `firsthand cost` shows this week's model calls by provider.

---

## 5. Signals and trigger detection

### 5.1 Three sources

| Source | Gives | Available on |
| :- | :- | :- |
| **Hooks** | Seven canonical events: `session_start`, `prompt_submit`, `before_tool`, `after_tool`, `tool_failed`, `turn_end`, `session_end` [verified: research/surfaces.md section 5]. Prompt text verbatim, tool kinds, commands, exit codes, edited paths | Agents with hooks |
| **Agent reports** | The agent calls the `moment` tool, or runs `firsthand moment <break>`, at five named breaks: `task_start`, `failure`, `options`, `risky_step`, `done` | Every agent |
| **Git watch** | The working diff against the task's base, path categories, new files, tests added or edited, commits, merges, pull requests through `gh` where the person has it | Every agent with a local repo |

Most triggers are conditions on the diff, and the engine reads those directly, whatever the agent. Hooks add timing and the prompt.

The engine does not read agents' transcript files, and it does not need the text of the agent's messages. Not every agent's turn-end hook carries that text [unverified per agent], so no trigger depends on it.

### 5.2 Canonical event fields

The dispatcher keeps only an allowlist per event and drops the rest of the payload.

| Event | Kept |
| :- | :- |
| `prompt_submit` | The prompt text (secret-scanned before any write), time |
| `before_tool`, `after_tool`, `tool_failed` | Tool kind (edit, shell, plan, ask, other), paths for edits, the command line for shell, exit code, failing test ids parsed from output. Not the output |
| `turn_end` | Time. On adapters flagged `turn_end_has_message`, the checkable claims in the final message ("all N tests pass") drawn by fixed patterns, after which the message is dropped |
| `session_start`, `session_end` | Agent, session id, working directory, cloud marker |

### 5.3 The done signal

Defined in `learning.md` section 3.3. In code:

- **With hooks:** a `turn_end` where the snapshot differs from the one at the previous turn end, the last test run seen was not failing, and no `ask` tool call is pending.
- **Without hooks:** `moment done`.
- **Backstop on every agent:** git watch sees a new commit that changes source files, or a pull request opening.

### 5.4 Trigger detection by moment

| Moment | With hooks | Without hooks | The engine confirms with |
| :- | :- | :- | :- |
| Revert test | The done signal. The runner starts earlier, at an `after_tool` test run that passes after a test file changed | `moment done`, or the commit backstop | Git: the diff changes source and adds or edits a test |
| Call it | `prompt_submit` holding a trace or failing-test pattern. Or `turn_end` with the last test run failing | `moment failure` | Git: the failing test exists at the base and is not edited in the diff |
| Brief | `prompt_submit`, then a plan tool call or first edits in more than one path category | `moment task_start` | The prompt holds no test id, test path or test command |
| Who is affected | The done signal. `before_tool` on `gh pr create` | `moment done`. Git watch | The reference search |
| Missing case | The done signal | `moment done` | Git: tests added for a path that takes input, or a tagged path |
| Where to look | The done signal | `moment done` | Git: three or more source files |
| Split point | Git watch at each `after_tool` | Git watch on poll | The size line from landed history |
| Your experiment | Two `turn_end` events in a row with the same failing test id | Two `moment failure` reports for the same test | The engine's own rerun in scratch |
| Already there | Git watch: a new source file or top-level name | Same | The name search |
| Decide and date it | `before_tool` on the agent's ask tool | `moment options` | Path categories of the diff |
| Way back | Git watch: a migration with a destructive or one-way step | Same | The migration extractor |
| Invariant | Git watch: a migration adding a table, relationship or tagged column | Same | The migration extractor |
| Silent failure | `before_tool` on `gh pr create` or `gh pr merge` | Git watch: a merge | The test map: a test reaches the changed function |
| Hazard line | `before_tool`: a shell command on the irreversible list | `moment risky_step` | The target lookup: host not local, or unknown |

What differs without hooks is timing and reliability, not the outcome. The engine learns of a break when the agent reports it or at the next git watch poll. Three things depend on the agent following the skill: Call it, Decide and date it and the hazard line. `init` says so in one line.

### 5.5 Delivering a question

The engine has decided to ask. Which routes exist depends on when.

**At a turn end on a hook agent** the agent's turn is over, so the agent cannot relay anything without a new model turn. The routes, in order:

1. The inline card, where the agent can draw UI (section 8.4).
2. The hook's user-visible message field, where the agent's turn-end hook has one. On Claude Code this is `systemMessage` in the Stop hook's JSON output [unverified]. The hook never uses a field that blocks the stop or submits a follow-up.
3. An OS notification, if the person turned those on.
4. The Room inbox and its tab badge, always.

**Inside a turn** (a `moment` tool call from an agent without hooks, or hook-added context at `prompt_submit` or `before_tool`): the engine returns one fixed line and the skill tells the agent to print it unchanged.

The line is always the same shape. Exact wording per moment is in `experience.md` section 5.

```
Firsthand (skip ok): 3 new tests. Which one would still pass with the change undone? Reply 1, 2, 3 or none, or answer here: http://127.0.0.1:4127/q/7f3
```

The link carries no credential.

**A reply in the agent's chat.** On hook agents the `prompt_submit` hook sees a prompt that is exactly one of the open question's reply words (or "skip"). The engine records the call and adds context for the agent: the result lines, to print unchanged. On agents without hooks the agent passes the reply to the `answer` tool. Either way the call is scored like a Room answer (`learning.md` section 7.2).

**Hazard lines and fact lines** use the same routes. A hazard line at `before_tool` is written to the hook's user-visible message. The hook returns no permission decision, so the agent's own approval prompt is unchanged.

---

## 6. Extractors and the System view

There is no single system model to build first. Each moment's `plan` declares what it needs, and a moment is offered only where those needs are met (`learning.md` section 3.6).

| Need | Used by | Works on | How |
| :- | :- | :- | :- |
| Path categories | Triggers, high stakes | Any repo | Editable glob patterns in `projects/<id>.json`, with defaults |
| Test command and runner adapter | Every run | pytest first, then jest and vitest. Any other tool through the generic adapter | Run one test, parse failing ids, tell an assertion failure from an error. The generic adapter runs per test file and reads the exit code |
| Reference search | Who is affected, Already there | Any language with a tree-sitter grammar, else a name search | Language server if installed, else tags, else names. The method is labelled on the card |
| Landed history | Split point, Time call, the history scan | Any repo | `git log` with stats |
| Migration extractor | Way back, Invariant, the hazard line | Alembic and Django first, then one JavaScript ORM | Parses migration files for drops, renames, type changes and down steps |
| Target lookup | The hazard line | Stacks with a migration extractor | Reads the command line, environment names and config files for a host and database name. Never opens a connection. Never reads a credential's value. "Cannot tell" is a result |
| Test client and scratch database | Missing case (boundary form), Invariant, Way back | Same stacks | Section 7.4 |
| Test map and capture shim | Silent failure, Break it | Python first, then JavaScript and TypeScript | A coverage run maps tests to functions. The shim records responses, log records, metric calls and caught exceptions |

Each extractor is a plug-in with fixture projects in CI. Where none covers a project, its moments are off and the "What works here" note lists them with the reason.

**The System view** in the Room needs none of the optional extractors. It lists the project's parts by top-level folder and path category, and pins to each part what the record holds: notes, calls, decisions, saved failures and landed changes. Where a migration extractor exists it adds tables. It is a reading aid. It has no score and asks nothing.

---

## 7. The check runner

The rule: **the engine never writes to the project.** Not the working tree, the index, refs or `.git/objects`. Every check runs on a copy.

### 7.1 Snapshots

A snapshot is a git tree of the project as it stands, including uncommitted and untracked files, made without touching the project:

1. A temporary index file (`GIT_INDEX_FILE` in `~/.firsthand/run/`), so the real index is not changed.
2. A separate object folder (`GIT_OBJECT_DIRECTORY` set to the snapshot store, with the project's objects as an alternate), so new blobs go to the store.
3. `git add -A` into the temporary index, then `git write-tree`. This follows `.gitignore`, so ignored files such as `.env` are left out.

The snapshot store is a bare repo per project in the cache. Snapshots are taken at every prompt, every turn end, each red and green test run, and when a check starts. They give the task's base, the tree a check ran on, the steps Call it bisects over, and the material for Replay, Rebrief and Supervise a past run. Snapshots of landed changes are kept for a period the person sets, then pruned.

### 7.2 Scratch copies

1. **Build.** Check the snapshot tree out into a fresh folder under `~/.firsthand/run/scratch/`, mode 0700. Agent and editor config is stripped (`security.md` section 2.3).
2. **Dependencies.** Ignored dependency folders are not in the snapshot. The engine keeps a copy per project in the cache, refreshed when the lockfile hash changes, and clones it in: copy-on-write where the file system supports it, a plain copy otherwise. Never a symlink into the project.
3. **Carried files.** A project whose tests need an ignored file names it in `runner.carry`, confirmed once in the Room. Default: none.
4. **Control.** Run the target tests unchanged. The result must equal the result on the real tree as last seen. If not: `check.unavailable`, reason "does not match here", and nothing is asked.
5. **Change one thing.** Revert files to the base, add one test, apply part of a diff, check out an earlier snapshot, insert a fault.
6. **Run again.** Record the command, exit code, failing test ids and a hash of the output.
7. **Delete** the folder.

The test command comes from config, else from CI config or manifest scripts, else from the command the agent was seen to run. The person confirms it once.

### 7.3 Isolation, by class of code

| Code | Runs in | Reason |
| :- | :- | :- |
| The project as it stands, and its tests | A scratch copy as a child process, with a scrubbed environment and, where the OS offers a sandbox, no network and no writes outside the scratch folder | The person and the agent already run this code many times a day. A container requirement would turn most checks off for most people |
| The person's old commits (drills, the history scan) | A container, no network after dependency install | Old lockfiles can pin versions later found malicious |
| Generated tests and fault edits | Wherever their target runs | Small edits to a scratch copy |

Scrubbed environment: an allowlist (`PATH`, `HOME` pointed at a scratch home, locale, the language's own variables, the project's declared test variables). Agent tokens, cloud credentials, SSH agent sockets and `GH_TOKEN` are not passed.

### 7.4 Extensions

| Extension | How it works | Its control | Off when |
| :- | :- | :- | :- |
| **Partial apply** | The chosen files of the diff applied at the base, then the rest | The whole diff applied gives the head tree | A split through a file |
| **Bisect** | A binary search over snapshots, or `git bisect run` in a scratch repo | The test passes at the good end and fails at the bad end | Either end does not reproduce |
| **Old tests on new code** | The base's test files checked out over the head's source, then run | The base's tests pass on the base | They do not |
| **Scratch database** | SQLite: a copy of the fixture file. Server databases: a throwaway database in a container, else a new database with a `firsthand_scratch_` name on a loopback server | The project's migrations apply cleanly from empty | No container runtime and no loopback server |
| **Probe** | One request written as a generated test through the project's own test client | A legitimate request beside it must succeed | No test client |
| **Fault injector** | A source edit in the scratch copy: the first line of the named function raises. A test that reaches it is run under the capture shim | The same test passes without the fault | No shim for the language, or no test reaches the function |

### 7.5 Scheduling and limits

- **Pick first, then run.** The moment engine picks one candidate and only its check runs. If its control fails, the next candidate's check runs (`learning.md` section 6.1).
- **Always on:** the revert test, started when a test file has changed and the agent's own test run passes. And the claim check on adapters flagged `turn_end_has_message`. Nothing heavier runs unasked.
- One check at a time per project, at low priority. A check does not start while the agent's own test command is running.
- Each check has the person's time limit. Past it the process group is killed, `check.unavailable` is written, and an open question closes with "The check could not finish."
- Each run uses its own scratch folder, its own free port in `PORT`, and its own database.
- On battery or under high load only the revert test runs. The person can turn this off.

### 7.6 Check plans

| Moment | Steps | Key |
| :- | :- | :- |
| Revert test | Snapshot. Control: the new tests on the head tree. Check out every non-test file of the diff from the base tree. Run each added or edited test | Per test: fails on its assertion, still passes, or cannot run |
| Brief | As Revert test, for the one confirmed done check | The same three outcomes |
| Call it | Snapshots at red and at green. List files and functions changed between them. Scan the fix for symptom patterns. On the green tree, restore only those files to their red state. Rerun the test | Where the fix landed. Whether undoing it brings the failure back |
| Where to look | Old tests on new code, at once. Then outside events from the timeline until the change lands | The files changed between an outside event and the run that clears it |
| Way back | Scratch database at the base schema with seed rows. Apply the migration. Run the base's tests. Run the down migration. Compare schema and row hashes with the start | What gets you back, and what is lost |

---

## 8. The Room server

### 8.1 On this computer

- **Bind.** `127.0.0.1` only, on a port chosen at `init` and kept, so links stay valid. Examples in the specs use 4127.
- **Server.** The standard-library HTTP server from `room.py`, inside the daemon, with its size limits. Live updates by server-sent events.
- **Session.** `firsthand room` opens the default browser at a one-time URL. The server swaps it for a session cookie (HttpOnly, SameSite=Strict) and redirects to a clean URL.
- **Links in the agent's chat** carry a question id and no credential. Opened in a browser with a session they show the card. Without one they show a page that says to run `firsthand room`.
- **Every request** is checked for a Host header of `127.0.0.1:<port>` or `localhost:<port>` (stops DNS rebinding), a valid session, and on writes a matching Origin and a per-session token. No CORS headers. A strict content security policy: no remote scripts, fonts or images.
- **Widening** (raise a limit, add a model provider, add a record remote, pair a device, delete) is done in the Room on this computer with a second confirming click. It is never an agent tool and never offered on a phone.
- **No browser.** `firsthand room --tty` is the Room's text view in a terminal the person opened.

Screens are defined in `experience.md` section 7: Inbox, Journal, System, Skills, Drills, Settings. Keyboard letter shortcuts are off by default. Founder decision.

```
GET  /api/inbox      GET /api/journal     GET /api/system     GET /api/skills
GET  /api/q/<id>     GET /api/reviews     GET /api/drills     GET /api/events (server-sent)
POST /api/q/<id>/lock            POST /api/q/<id>/skip        POST /api/q/<id>/confidence
POST /api/q/<id>/confirm-case    POST /api/q/<id>/dispute     POST /api/q/<id>/wrong-start
POST /api/q/<id>/send-to-agent   POST /api/review/<id>/lock   POST /api/settings
POST /api/pair
```

No route returns a result before the lock, skip or close for that question. This is enforced in the key store, not per route.

### 8.2 Phone pairing

There is no relay and no cloud. The phone reaches the daemon on the same local network, live. Nothing works offline.

1. **Start.** The person clicks "Pair a phone" in the Room. The daemon opens a second listener on one chosen network interface and shows a QR code.
2. **The code** holds the listener's address and a long one-time token, good for a few minutes and one use.
3. **One tap.** The phone's camera opens the page. It shows the computer's name and one button, "Pair". Founder decision: one confirmation tap is fine.
4. **After.** The token is exchanged for a device cookie. The daemon records `device.paired`. Later visits need no code.
5. **What the phone can do.** See and answer reviews and open questions, read the journal and the skills. It cannot change settings, widen anything or start a drill that needs a runner.
6. **Revoke.** One click in Settings.

Limits, said on the pairing screen:

- The phone works only on the same network as the computer, while the computer is awake.
- The page is plain HTTP on a local address. Someone on that network who is actively attacking it could read or alter it. Browsers do not give such a page the crypto or offline features that would fix this, so the design does not pretend to. A person who has their own private network overlay with HTTPS can point the listener at it.
- The second listener closes when the daemon exits. Pairing is off by default on work computers.

### 8.3 The reminder

At most one a day, at a time the person picks. Founder decision. It is offered the first time a review is due, not at install.

The OS scheduler (launchd, a systemd user timer, Task Scheduler) runs `firsthand remind` at the chosen time. It shows one OS notification on the computer: "Firsthand: reviews". No question, no answer, no count. There is no phone reminder in this version.

### 8.4 The inline card

Where an agent can show UI, the question card is drawn in the conversation: an MCP Apps `ui://` resource served by the MCP server, or the agent's own plug-in UI (`surfaces.md` section 2). It is the same markup as the Room's card and submits through its own path to the MCP server. On work computers the default is the Room link and no inline card, because a host may log what a card submits.

---

## 9. Install per agent

One command, from a terminal or from inside the agent. Both spec files use this form:

```
uvx firsthand init        (or: pipx run firsthand init)
```

What `init` does:

1. Installs the engine to `~/.firsthand/engine/<version>/` in its own virtual environment and verifies the release checksum.
2. Creates the record repo (`git init`, no remote) and picks the Room port.
3. Detects the agent it was launched from, by parent process and environment markers. From a plain shell it lists the agents found and asks which, with none pre-selected.
4. Shows every file it will write, then writes on a yes: byte-exact backups first, user-level locations only.
5. Asks one question: "Is this a work computer? [Y/n]". Enter means yes, the stricter setting, and it says so.
6. Finds the test command or asks for it, starts the history scan in the background, and prints the Room address.

What is written, by layer:

| Layer | What | Why |
| :- | :- | :- |
| Skill or instruction block | A short text: the five breaks at which to call `moment`, to print the engine's line unchanged, to treat "skip" as final, never to answer for the person | The floor. Works on every agent |
| MCP entry | `<absolute path>/firsthand mcp` | Tools without shell quoting. The inline card where the host supports it |
| Hooks entry | `<absolute path>/firsthand hook <agent> <event>` for each event the agent has | Timing and the prompt, without relying on the model |

Per agent, from the adapter manifests. Hook locations are from `../research/surfaces.md` section 5.

| Agent | Instruction or skill | MCP | Hooks |
| :- | :- | :- | :- |
| Claude Code | User skill folder | User MCP config | User `settings.json`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop` |
| Codex CLI and app | User skill folder | `config.toml` | `~/.codex/hooks.json`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop` |
| Cursor IDE | User rules or skill | `~/.cursor/mcp.json` | `~/.cursor/hooks.json`: `sessionStart`, `beforeSubmitPrompt`, `preToolUse`, `postToolUse`, `postToolUseFailure`, `stop` |
| Copilot CLI and app, VS Code Copilot | User instructions | User MCP config | `~/.copilot/hooks/*.json`: `sessionStart`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `errorOccurred`, `agentStop` |
| Gemini CLI | Extension context file | Extension MCP entry | User `settings.json`: `SessionStart`, `BeforeAgent`, `BeforeTool`, `AfterTool`, `AfterAgent` |
| Devin, Amp, OpenCode, Kiro, Cline | Skill, steering file or rules | MCP config | Each agent's own hook or plugin events, as listed in `../research/surfaces.md` |
| Copilot in Visual Studio, JetBrains, Eclipse, Xcode. Roo Code, goose, Junie, Zed | Instruction file | MCP config | None |
| Aider | Conventions file read at start | None | None |

Rules:

- `init` installs only into the agent it was launched from. Each further agent needs its own yes: `firsthand add <agent>`, or Settings in the Room.
- It never writes a project's `AGENTS.md`, `CLAUDE.md`, `.cursor/`, `.claude/` or skills folder without a per-repo yes. It never tells the person to commit anything of Firsthand's to a project.
- Hooks return no permission decision on any agent. A conformance test fails an adapter that does.
- `firsthand uninstall` restores the backups and refuses to overwrite a file the person changed since, showing the diff instead. The record is left in place.
- `firsthand upgrade` is the only way the engine or any agent config changes. It shows the changelog and each diff first.

---

## 10. Cloud sessions: the import step

A cloud session runs in a container the person does not control. `init` writes user-level files on the person's own machine only, so there is no engine, hook or skill in the cloud session, and nothing of Firsthand's is committed to a project to put one there. There is no carry branch. Founder decision.

The import step is git:

1. The cloud session does its work and pushes a branch or opens a pull request. No Firsthand code runs there and nothing is asked.
2. At the person's next local session, git watch sees a fetched branch with commits that no local session produced, and the Room inbox offers: "A branch arrived from elsewhere: feature/refund-keys, 4 commits. Review it here?" Or the person runs `firsthand import <branch or PR>`.
3. The engine runs the done-family checks on the fetched commits and posts inbox cards: Revert test, Who is affected, Where to look in its pull request form. Split point is offered as a drill. The engine chose the case, so these are scored. They use the day's question limit.
4. Prompts from the cloud session are not in the timeline, and the cards say so: "Built in a cloud session. Firsthand did not see the prompts."

Moments that need the person at the moment of the work (Brief, Call it, Your experiment, Decide and date it) do not exist for cloud work. If the person never imports, nothing is lost but those cards.

---

## 11. Idea catalog and question bank

- Public, versioned data, CC BY 4.0.
- **Ideas:** a stable id, one sentence at the level of systems with no code, the skill it sits under, and the forms it can return in. The seed is the mechanism list and the habit sentences of `learning.md` section 9.2.
- **Bank items:** a short written case, a pick, and a key written and cited by a person. Contributors add items by pull request.
- An idea is attached to a miss by the person's own tap on the result, never by a model.

---

## 12. Migration from `learning-while-building`

Build step 1 (`build-1.md`) already moves the old skill's record out of the project. After that:

1. `firsthand import-lwb [path]` reads the old record, checks it with the old `learning.py check`, and runs the old `migrate` first if needed.
2. Each topic becomes an idea. Each attempt becomes `review.locked` plus `review.scored` marked imported. Imported answers never count toward a skill level, because the old record holds no sealed calls.
3. The old skill's SKILL.md becomes the instruction-file layer. The old scripts stay for one release.

---

## 13. When a remote is added

Nothing in this section is built until a person asks for a record remote. The default is one device, one writer, no remote.

- **Encryption.** Event files encrypted before they leave the machine, with the key in the OS keychain. A remote holds a record of the person's misses, so it is not pushed in plain text.
- **Merging between devices.** One file per event with ULID names merges without conflict. The earliest lock wins. The last `config.set` wins per key. Budgets are computed across devices.
- **Signing** of commits per device, if the person wants to tell devices apart.

---

## 14. Limits of this design, stated plainly

- **The engine sees what passes through a session or lands in git.** Work done in an editor with no agent leaves only its diff.
- **Without hooks, three things depend on the agent reporting them** (section 5.4).
- **At a turn end the question reaches the person only through a card, a hook message, a notification or the Room.** Where an agent has none of the first three, the question waits in the Room and may be seen late or not at all. A late question is still valid when its check has not been shown.
- **The runner needs a test command that works on a copy.** Projects whose tests need live services get fewer checks, and the "What works here" note says which.
- **Coverage of stacks is uneven.** Tier A checks need only git and a test command. Tier B and C need an extractor or shim per stack (`learning.md` section 3.6).
- **The key rule guards against leaks, not against a process acting as the person** (section 3).
- **The record is plain files.** Anyone who can read the person's home folder can read it (`security.md` section 4).
- **The phone works on the local network only,** live, over plain HTTP (section 8.2).
