# Spec: security and privacy

Part of `../PRODUCT.md` (section 9). Informed by `../redteam/privacy-security.md`. One package touches every agent a user runs, and holds a record of what they did not know. These rules keep it from becoming the weak point.

---

## 1. What we protect, and from whom

| Asset | Threat | Rules |
| :- | :- | :- |
| The user's machine and credentials | Code in old commits and public repos; a compromised release | Sections 2 and 3 |
| The user's agent configs | A bad installer or update | Section 3 |
| The user's misses and levels | Employers, teammates, chat logs, backups | Sections 4, 6 and 7 |
| The product's voice | Text written by repo contributors | Section 5 |

Stated limit: an attacker who controls the user's device, or the binary the user runs, can read everything. The product reduces exposure and says where it ends.

---

## 2. Running code the user did not write

### 2.1 Classes of code

| Code | Example | Where it may run |
| :- | :- | :- |
| A stranger's repo | Fresh repo task | Container only, no network |
| The user's old commits | Replay | Container only, no network after dependency install |
| The user's current committed code | Trace | Scratch copy; container if present |
| The project's own tests, now | Your-line check, Review-first test | Where the user and agent already run them, no change |

Trace runs without a container because the user and their agent already run that code every day. Requiring a container would remove the first drill for most users without reducing real risk.

### 2.2 Container rules

- Runtime: a local container runtime (Docker, Podman) the user already has. Which runtimes work on which OS is checked in build step 5. The engine never installs one silently.
- Network: none while project code runs. Dependency install is a separate step, with install scripts disabled where the package manager allows [unverified per package manager]. Fresh repo tasks in the task set use pinned images with dependencies baked in where possible.
- Mounts: only the scratch folder, read-write. Never the home folder, `~/.ssh`, `~/.aws`, `~/.config`, the record, or the agent's config.
- Images pinned by digest, from a signed manifest. `firsthand verify` checks it.
- No container runtime: Replay and Fresh repo are not offered, and the user is told what to install.

### 2.3 Scratch copy rules

- Built from committed files only (`git archive` of a named commit). Never untracked files, never `.env`, never the working tree.
- Agent and editor config stripped before anything runs or anyone opens it: `.claude/`, `.mcp.json`, `.cursor/`, `.codex/`, `.gemini/`, `AGENTS.md`, `CLAUDE.md`, `.vscode/`, `.idea/`, `.devcontainer/`. These can carry hooks and MCP servers that run when an agent opens the folder [verified: https://code.claude.com/docs/en/hooks].
- Folder mode 0700, in a per-user temp location, deleted after use.

### 2.4 Old dependencies

Old lockfiles can pin versions later found malicious. Before a Replay install, the engine checks the lockfile against an advisory source for the ecosystem where one exists, and refuses on a known-malicious match. Which sources, per ecosystem, is chosen in build step 5.

---

## 3. Supply chain and install

- **Names.** Reserve `firsthand` and the fallback name on npm, PyPI and Homebrew in build step 1, before any install line is published.
- **Releases.** Signed, published with registry provenance (npm provenance, PyPI trusted publishing) [unverified: check current support at release time]. Install lines pin a version.
- **What install writes.** Only into the agent it was launched from; one yes per further agent. Each file path and the exact diff are shown first. Byte-exact backups of every changed file, outside the record. `firsthand uninstall` restores them, and refuses to overwrite a file the user changed since, showing the diff instead. `install.changed` events record each write.
- **Hooks.** Every hook entry calls an absolute path to the installed, verified engine. Hooks never return permission decisions: no `allow`, no `deny`, no `ask`. Claude Code PreToolUse hooks accept `allow` [verified: https://code.claude.com/docs/en/hooks]; a conformance test fails any adapter that returns one. Hooks never block a tool call, never refuse to end a turn, and never write their payload to disk.
- **Updates.** Only through `firsthand upgrade`, which shows the changelog and the diff to every agent config file first. Never from a hook, never in the background. Where a plugin directory auto-updates plugins [unverified per directory], the plugin contains only the T0 skill and points to the pinned engine, so a directory update cannot change hooks.
- **Verify.** `firsthand verify` checks the running binary's signature and provenance, that hook and MCP entries point to it, container image digests, and that adapter files match what install wrote. It prints what it checked and what it cannot check.

---

## 4. Work computers

### 4.1 What an employer can see

| Channel | Can the employer see it? |
| :- | :- |
| That Firsthand is installed; hooks, config files, instruction blocks | Yes |
| The record folder on a managed laptop | Yes if not encrypted, through device management or backup [unverified per product] |
| Questions, answers and verdicts in the agent's chat | Possibly: enterprise agent plans can keep logs admins can export [unverified per vendor] |
| Model grading calls on a work account | Possibly, through the vendor's admin tools [unverified per vendor] |

### 4.2 Defaults on a work computer

- Answers go to the pad, not the chat. The chat shows only "Question in your pad".
- The record is encrypted at rest.
- `grader = local-only`.

The install copy (`experience.md` section 2.1) lists what the employer can see, what it cannot, and the limit. It never promises that use is invisible.

---

## 5. Repo content and prompt injection

Text written by repo contributors: guide files, owner notes, postmortem drills, commit messages, code excerpts, PR bodies, Fresh repo goals.

- **Quoted and attributed.** Shown inside a block that starts "From this repo, written by contributors:", never in the product's own voice, and never as an instruction to the agent.
- **Stripped.** Owner notes and drill text have commands, URLs and code fences removed before display. A note that was mostly a command shows "This note had a command, removed for safety."
- **Trusted repos only.** Guides are read only in repos the user marks as theirs or trusted, once per repo, in the pad.
- **Narrow-only tools.** Agent-callable tools can only narrow: quieter, lower budget, fewer providers, less sharing. Any widening (budget, grader, import, delete, consent, remote) needs a typed confirmation in the pad, which the engine opens itself. On surfaces with no local terminal, widening waits for the next local session.
- **Grader input** marks the answer and any excerpt as data that may contain instructions.

---

## 6. What leaves the machine

The table in `../PRODUCT.md` section 8.7 is the source. Rules:

- No copy anywhere says "nothing leaves the machine". The install copy says "Firsthand sends nothing by default" and then names the chat and the grader.
- Every model grader names the receiving company and account before first use.
- Fresh repo names the host it will clone from before the first clone.
- `firsthand privacy` prints the current table for this install, with each path's state.
- There is no telemetry.

---

## 7. Secrets, keys and history

- Every free-text field is secret-scanned before write (`architecture.md` section 2).
- Private keys live in the OS keychain or `~/.config/firsthand/keys/` (mode 0600), never in the record. A commit guard refuses key material in the record.
- Postmortem drills: logs and text are scanned for secrets and personal data (emails, names from the git author list, IP addresses, tokens). The author sees each redaction and approves the drill before it is saved.
- Code excerpts stay off by default, and pass the scan when on.
- `forget <idea>` removes every event for the idea, rewrites record history, expires the reflog, runs a prune, and warns that any remote or backup keeps old copies until rewritten there.
- **The existing skill.** `skills/learning-while-building/SKILL.md` line 103 tells users to commit `.learning/` to the project repo, so existing users' misses may be in project history. Build step 1 changes the default to a folder outside the repo, adds a note to the README on how to rewrite history in repos they own, and `firsthand import-lwb` repeats this (`architecture.md` section 11).

---

## 8. Conformance checks for security

Each release, per tested surface: hooks return no permission decision; hook and MCP entries point to the verified binary; no hook payload is written to disk; widening tools refuse without a pad confirmation; scratch copies contain no stripped config and no untracked files; containers have no network while project code runs; import rejects a non-allowlisted event; work-computer defaults are set.
