# Spec: security and privacy

Part of `../PRODUCT.md`. Informed by `../redteam/privacy-security.md`. One package touches every agent a person runs, runs their project's code on its own initiative, serves a web page, and holds a record of the calls they missed. These rules keep it from becoming the weak point.

The mechanisms are in `architecture.md`: the check runner in section 7, the key rule in section 3, the Room in section 8, install in section 9.

The effort here goes to what can hurt the person: their project, their machine, their databases, their agent configs, their privacy. It does not go to guarding the person's record against the person. The record is theirs, and cheating it gains nothing.

---

## 1. What we protect, and from whom

| Asset | Threat | Rules |
| :- | :- | :- |
| The project: working tree, index, history | The engine's own checks changing it. Learning data being committed to it | Sections 2.3 and 7 |
| The person's machine and credentials | Code in old commits. Tests run without the person asking. A compromised release | Sections 2 and 3 |
| Databases and outside systems | A check that reaches a real one | Section 2.5 |
| The person's agent configs | A bad installer or update | Section 3 |
| The person's misses and levels | Employers, teammates, chat logs, a web page in another tab, a device on the same network | Sections 4, 6, 7 and 9 |
| The product's voice | Text written by repo contributors | Section 5 |
| A fair call | A check result reaching the agent's chat before the person has answered | Section 10 |

Stated limit: an attacker who controls the person's device, or the binary the person runs, can read everything. The product reduces exposure and says where it ends.

---

## 2. Running code

The engine runs project code on its own initiative, in the background, when a trigger fires. This section governs that.

### 2.1 Classes of code

| Code | Example | Where it may run |
| :- | :- | :- |
| The person's old commits | Replay, Proof audit, Split a past change, Supervise a past run, the history scan | Container only, no network after dependency install |
| The project as it stands, and its tests | Every in-build check: the revert test, partial apply, old tests on new code, bisect over snapshots | A scratch copy, as a child process with a scrubbed environment. In an OS sandbox with no network where one exists. In a container if the person prefers |
| Tests and queries a writer generates | Missing case, Invariant | The same scratch copy as their target. Never written to the project |
| Fault edits | Silent failure, Break it | The same scratch copy. Never written to the project |
| A branch brought in by `firsthand import` | Work from a cloud session | As the person's own current code, once the person has fetched it and said yes to the import offer |

The current project runs without a container because the person and their agent already run that code and those tests many times a day. Requiring a container would turn most checks off for most people without reducing real risk. What is new is that the engine starts the run, so the engine narrows what the run can reach: sections 2.3 and 2.5.

### 2.2 Container rules

- Runtime: a local container runtime (Docker, Podman) the person already has. The engine never installs one.
- Network: none while project code runs. Dependency install is a separate step, with install scripts disabled where the package manager allows.
- Mounts: only the scratch folder. Never the home folder, `~/.ssh`, `~/.aws`, `~/.config`, the record, or the agent's config.
- Images pinned by digest.
- No container runtime: the drills on old commits are not offered and the history scan reads only what needs no run. The Room says what to install. In-build moments are not affected.

### 2.3 Scratch copy rules

**The engine never writes to the project.** Not the working tree, the index, refs, `.git/objects` or `.git/worktrees`. `git worktree add` is not used, because it writes into the project's `.git`.

- **Built from a snapshot** of the tree as it stands: tracked files with their uncommitted changes, and untracked files that are not ignored. The snapshot is made with a temporary index and a separate object folder (`architecture.md` section 7.1).
- **Never ignored files.** `.env` and anything else matched by `.gitignore` is left out. A project whose tests need an ignored file names it in `runner.carry`, confirmed once in the Room. Default: none.
- **Dependency folders** are cloned or copied from an engine cache, never symlinked to the project.
- **Agent and editor config stripped** before anything runs: `.claude/`, `.mcp.json`, `.cursor/`, `.codex/`, `.gemini/`, `AGENTS.md`, `CLAUDE.md`, `.vscode/`, `.idea/`, `.devcontainer/`. These can carry hooks and MCP servers that run when an agent opens the folder [verified: https://code.claude.com/docs/en/hooks].
- **Scrubbed environment.** The child process gets an allowlist: `PATH`, a scratch `HOME`, locale, the language's own variables, and the test variables the project declares. It does not get agent tokens, cloud credentials, `GH_TOKEN` or SSH agent sockets.
- **OS sandbox where there is one:** no network and no writes outside the scratch folder. Where there is none, the run is a plain child process, and `firsthand privacy` says so.
- **Limits.** A time limit per check, after which the whole process group is killed. One check at a time per project, at low priority.
- Folder mode 0700, under `~/.firsthand/run/`, deleted after use. A crash leaves a folder that the next daemon start removes.
- **Snapshot store.** Snapshots hold source code. They live in the cache with mode 0700, are never in the record, never pushed anywhere, pruned after the period the person sets, and removed by `firsthand forget --project`.

### 2.4 Old dependencies

Old lockfiles can pin versions later found malicious. Before a drill installs dependencies for an old commit, the engine checks the lockfile against an advisory source for the ecosystem where one exists, and refuses on a known-malicious match.

### 2.5 Databases, requests and outside systems

A check must never reach a real database or a real outside service.

- **Scratch databases only.** A copied SQLite file, a database in a throwaway container, or a new database with a `firsthand_scratch_` name on a server whose host is loopback. The runner sets the project's database variable to it and unsets every other database variable it knows of.
- **Look up before run.** The target lookup reads which host the test configuration would use. If it is not loopback, or cannot be told, every check that needs a database is off for that project and the "What works here" note says why. The lookup reads names and hosts. It never opens a connection and never reads a credential's value.
- **The engine never connects to a non-loopback database.** The hazard line is built by reading files and the command line.
- **Probes go through the project's own test client** in the scratch copy. The engine never sends a request to a deployed address.
- **Generated tests and fault edits** exist only in the scratch copy. They reach the project only when the person taps "Give it to my agent", as a patch the agent applies in the open.

---

## 3. Supply chain and install

- **Names.** Reserve `firsthand` and the fallback name on PyPI, npm and Homebrew before any install line is published.
- **Releases.** Published with registry provenance (PyPI trusted publishing). Install lines pin a version. `init` verifies the release checksum.
- **What install writes.** Only into the agent it was launched from, with one yes per further agent. Each file path is shown first, with the exact diff on request. Byte-exact backups of every changed file. `firsthand uninstall` restores them, and refuses to overwrite a file the person changed since, showing the diff instead.
- **Hooks.** Every hook entry calls an absolute path to the installed engine. Hooks never return permission decisions: no `allow`, no `deny`, no `ask`. Claude Code PreToolUse hooks accept `allow` [verified: https://code.claude.com/docs/en/hooks], and a conformance test fails any adapter that returns one. Hooks never block a tool call, never block a prompt and never refuse to end a turn.
- **Hook payloads.** The dispatcher keeps an allowlist of fields per event (`architecture.md` section 5.2) and drops the rest. The spool file holds only allowlisted fields, has mode 0600, and is truncated once read. Tool output is parsed for failing test ids and then dropped.
- **The engine does not read agents' transcript or session files.**
- **Updates.** Only through `firsthand upgrade`, which shows the changelog and the diff to every agent config file first. Never from a hook, never in the background.
- **Verify.** `firsthand verify` checks that hook and MCP entries point to the installed engine, that the engine matches its release checksum, and that adapter files match what install wrote.

---

## 4. Work computers

### 4.1 What an employer can see

| Channel | Can the employer see it? |
| :- | :- |
| That Firsthand is installed: hooks, config files, instruction blocks, the daemon process | Yes |
| The record and the cache on a managed laptop | Yes, through device management or backup. The record is plain files |
| A question line, a hazard line or a finding printed in the agent's chat | Possibly: enterprise agent plans can keep logs admins can export |
| A reply typed in the agent's chat | The same |
| An answer typed in the Room, and its result | Only by reading the record as above. It does not pass through the agent |
| Model reader calls on a work account | Possibly, through the vendor's admin tools |

### 4.2 Defaults on a work computer

`init` asks one question, "Is this a work computer?", and Enter means yes.

- The question line puts the Room link first and says once that a chat reply is part of the chat. The inline card is off.
- No text is sent to a model until the person says yes to a named company and account.
- Phone pairing is off until the person turns it on.

The install notice (`experience.md` section 13.2) lists what the employer can see and says plainly that the record is readable by whoever manages the computer. It never promises that use is invisible.

Encrypting the record at rest is not in the first builds. It is an open founder decision (`../PRODUCT.md` section 9). It would protect against backups and file scanners, not against an employer who controls the device.

---

## 5. Repo content and prompt injection

Text written by repo contributors reaches the Room: commit messages, test names, pull request bodies, reviewer comments quoted in results, log lines captured by the fault injector.

- **Quoted and attributed.** Shown inside a block that starts "From this repo, written by contributors:", never in the product's own voice, and never as an instruction to the agent.
- **Escaped in the Room.** All repo text is rendered as text, never as markup. The content security policy allows no inline script.
- **Narrow-only tools.** Agent-callable tools can only narrow: quieter, a lower limit. Any widening (a limit, a model provider, carried files, import, delete, a remote, pairing) needs a confirming click in the Room on the person's computer. A phone session cannot widen.
- **Reader and writer input** marks the answer, the person's sentence and any excerpt as data that may contain instructions. The provider runs with no tools, in an empty folder, with none of the person's agent config.
- **A model-written test is code the engine will run.** It runs only in the scratch copy, under section 2.3, and is shown back to the person in plain words before it counts.
- **A line sent to the agent** (a finding, a done check) is fixed text built by the engine from test ids and paths, plus the person's own words. It never includes repo prose.

---

## 6. What leaves the machine

| Path | What travels | Who receives it | Default |
| :- | :- | :- | :- |
| Lines Firsthand prints in the agent's chat | A question, a hazard line, a fact line, a finding: test names, paths, a host and database name, a loopback link | The agent's company, and an employer's logs on work plans | On. Findings can be turned off |
| A reply in chat | Whatever the person typed there | The same | The person's choice |
| Model writer and reader | The person's sentence or answer, the points, a short excerpt | The company and account the person names | Off until the person allows it |
| Registry lookup for a new dependency | A package name | The public registry for that ecosystem | On |
| `gh` queries for pull requests and review comments | What `gh` sends, under the person's own login | The person's git host | Only where the person already has `gh` set up |
| Phone pairing | Cards and answers, in plain HTTP | The person's own phone, over the local network | Off until paired |
| A git remote for the record | The record | The person's host | Off. Not built until asked for, and then encrypted (`architecture.md` section 13) |

Rules:

- No copy anywhere says "nothing leaves the machine". The install copy says "By default Firsthand sends nothing anywhere except the lines it prints in your agent's chat and package-name lookups."
- Every model provider names the receiving company and account before first use.
- `firsthand privacy` prints this table for this install, with each path's state.
- There is no telemetry.

---

## 7. Secrets, history and the project repo

- Every free-text field is secret-scanned before write: prompts, answers, notes, decision lines. Prompts captured by a hook are scanned before they are stored.
- Commands stored in `check.ran` and task events are scanned the same way, since a command line can hold a token.
- The target lookup stores hosts and database names. It never stores a connection string.
- Code excerpts are not stored. The record holds `path:line` and the Room reads the line from the project when it shows it.
- `forget <idea>`, `forget --change <id>` and `forget --project <name>` remove every matching event, rewrite record history, expire the reflog and run a prune. The project form also removes the snapshot store and the extractor cache.
- **Nothing of the person's learning goes into a project repo.** No learning data in any branch, commit, trailer or pull request body. No markers in source files. Who wrote a line is never written anywhere. A finding the person posts on a pull request is their own plain review comment.
- **The existing skill breaks this rule today.** `skills/learning-while-building/SKILL.md` tells users to commit `.learning/` to the project repo, so existing users' misses may be in project history, forks and remotes. Fixing that is build step 1 (`build-1.md`): the record moves out of the project, the instruction is removed, and existing users are told what removing the folder does and does not undo.

---

## 8. Conformance checks for security

Each release, per tested surface:

- hooks return no permission decision, hold no tool call and block no prompt;
- hook and MCP entries point to the installed engine;
- the spool holds no field outside its allowlist;
- the project's working tree, index, refs and object store are byte-identical before and after every check;
- scratch copies hold no stripped config and no ignored file that was not carried by consent;
- the scratch environment holds none of the listed credential variables;
- no check opens a connection to a non-loopback host, tested with a fixture project whose configuration points at one;
- containers have no network while project code runs;
- no check result reaches the agent's context before the lock, skip or close;
- widening refuses from an agent tool, from an agent's shell and from a phone session;
- the Room refuses a request with a wrong Host, a wrong Origin, or no session;
- nothing is written inside a project by `init`, by a check or by a session;
- work-computer defaults are set.

---

## 9. The Room and the phone

The Room is a web server on the person's machine. The threats are a web page in another tab, another process on the machine, and a device on the same network.

- **Loopback only** for the main listener, on a fixed port.
- **A session is required for everything.** It starts from a one-time URL the CLI opens in the browser.
- **Links given to the agent hold a question id and no credential.**
- **Every request:** Host header checked (stops DNS rebinding). On writes, Origin checked and a per-session token required. No CORS headers. Cookies HttpOnly and SameSite=Strict.
- **Content security policy:** no remote scripts, fonts or images. The page works offline.
- **No route returns a result before the lock, skip or close.** Enforced in the key store, tested per route.
- **Size limits** on every body and answer, as in the existing `room.py`.

The phone:

- A second listener, opened only while pairing is on, bound to one chosen interface.
- Pairing needs the QR code's long one-time token and one tap on the phone. The token is exchanged for a device cookie. A device on the network without the code cannot pair.
- A paired phone can read and answer. It cannot widen or change settings. Removing the device ends it at once.
- **Stated limit, shown on the pairing screen:** the phone's page is plain HTTP on the local network. Someone on that network who is attacking it could read the cards and answers or alter the page. A plain HTTP page on a local address cannot use the browser's crypto or offline features, so the design does not claim to encrypt it. A person with their own HTTPS overlay network can use that instead.

---

## 10. The agent and the key rule

The agent runs as the person, with the person's shell. The key rule is designed for that fact (`architecture.md` section 3).

- No output the engine gives the agent (tool result, hook output, CLI output under an agent, link) holds a check result before the lock, skip or close. One function enforces this.
- Pending keys are held in the daemon's memory and a 0600 file under `~/.firsthand/run/`.
- CLI commands that widen refuse when an ancestor process is an agent.
- The instruction block tells the agent not to read `~/.firsthand` and not to answer for the person.
- **Stated limit:** none of this stops a process that sets out to read the daemon's files as the person. Coding agents do not do this in normal use, and the record is the person's own, so there is nothing to gain. The design aims to make leaks impossible by accident, and spends nothing beyond that: no signing, no hash chain, no key encryption.
