# Spec: security and privacy

Part of `../PRODUCT.md` (sections 3, 6.9 and 6.10). Written in response to `../redteam/privacy-security.md` (cited as "RT privacy n"). It holds the threat model, the rules each component follows, and the copy the product uses about privacy.

---

## 1. What we protect, and from whom

| Asset | Threat | Rules |
| :- | :- | :- |
| The user's machine and credentials | Untrusted code in Checkup repos and old commits; a compromised release | Sections 2 and 3 |
| The user's misses and levels | Employers, teammates, reviewers, chat logs, backups | Sections 5, 6 and 8 |
| The user's agent configs | A bad installer or update | Section 3 |
| The claim instruments (unseen items, Checkup, study pool) | The agent, the user, leaks | Section 4 |
| The product's voice | Text written by repo contributors | Section 7 |

Stated limit for the whole spec: an attacker who controls the user's device, or the binary the user runs, can read everything. The product reduces exposure and says where it ends.

---

## 2. Running code the user did not write (RT privacy 2)

### 2.1 Classes of code

| Code | Example | Where it may run |
| :- | :- | :- |
| A stranger's repo | Checkup task | Container only, no network |
| The user's old commits | Replay | Container only, no network after dependency install |
| The user's current committed code | Trace | Scratch copy; container if present |
| The project's own tests, now | Your-line check, Review-first test | Where the user and agent already run them, no change |

### 2.2 Container rules

- Runtime: a local container runtime (Docker, Podman) or a VM runtime the user already has [unverified: which runtimes on which OS; tested in v1]. The engine never installs one silently.
- Network: none while project code runs. Dependency install is a separate step. For Checkup images, dependencies are resolved by the product in advance and baked into a pinned image, so no install runs on the user's machine at all.
- Mounts: only the scratch folder, read-write. Never the home folder, `~/.ssh`, `~/.aws`, `~/.config`, the record, or the agent's config.
- Image pinning: by digest, from a signed manifest. `firsthand verify` checks it.
- No container runtime: Checkup and Replay are not offered. The user is told what to install.

### 2.3 Scratch copy rules

- Built from committed files only (`git archive` of a named commit). Never untracked files, never `.env`, never the working tree.
- Agent and editor config stripped before anything runs or anyone opens it: `.claude/`, `.mcp.json`, `.cursor/`, `.codex/`, `.gemini/`, `AGENTS.md`, `CLAUDE.md`, `.vscode/`, `.idea/`, `.devcontainer/`. These can carry hooks and MCP servers that run when an agent opens the folder [verified: https://code.claude.com/docs/en/hooks].
- Folder mode 0700, in a per-user temp location, deleted after use.
- The pad tells the user not to open their agent in a Checkup or Replay folder, and the stripped config means opening it runs no project hooks.

### 2.4 Old dependencies

Old lockfiles can pin versions later found malicious. Before a Replay install, the engine checks the lockfile against an advisory source where one exists for the ecosystem [unverified: which sources], refuses on a known-malicious match, and runs install scripts with network off or disabled [unverified per package manager].

---

## 3. Supply chain and install (RT privacy 3, RT market 9)

### 3.1 Names and releases

- Reserve `firsthand` and the fallback name on npm, PyPI and Homebrew in v0 week one, before the site shows an install line.
- Releases are signed. Publish with registry provenance (npm provenance, PyPI trusted publishing and attestations) [unverified: check current support at release time].
- The site's install line pins a version.

### 3.2 What install writes

- Only into the agent it was launched from. Others: one yes per agent.
- Before writing, the engine prints each file path and the exact diff. Every adapter's file list is published in the repo and on the site.
- Byte-exact backups of every file it changes, kept outside the record. `firsthand uninstall` restores them, and refuses to overwrite a file the user changed since, showing the diff instead.
- `install.changed` events record each write, so `firsthand verify` can show what the product has touched.

### 3.3 Hooks

- Every hook entry calls an absolute path to the installed, verified engine.
- **Hooks never return permission decisions.** No `allow`, no `deny`, no `ask`. Claude Code PreToolUse hooks accept `permissionDecision` values including `allow` [verified: https://code.claude.com/docs/en/hooks]; whether `allow` skips the user's prompt is [unverified]. We never use it, and a conformance test fails any adapter that does.
- Hooks never block a tool call and never refuse to end a turn.
- Hooks read their payload, act, and discard it. Payloads are never written to disk.

### 3.4 Updates

- Only through `firsthand upgrade`. It shows the changelog and the diff to every agent config file before applying.
- Never from a hook, never in the background.
- Plugin directories may auto-update plugins [unverified per directory]. Where they do, the plugin package contains only the T0 skill and points to the pinned engine, so a directory update cannot change hooks.

### 3.5 Verify

`firsthand verify` checks: the running binary's signature and provenance; the hook and MCP entries point to that binary; container image digests; the adapter files match what install wrote. It prints what it checked and what it cannot check.

---

## 4. Claim instruments (RT privacy 4)

### 4.1 What local encryption cannot do

A bank shipped in the package with its key in the package is obfuscation. One extraction makes it public for every user. The engine runs as the user, so any agent with a shell can run the engine or read its files. The spec states this and does not claim otherwise.

### 4.2 What the design does instead

| Instrument | Protection | Label |
| :- | :- | :- |
| Practice items | Sealed hash before asking; key check by a second context | "practice" |
| In-product unseen families | Fresh per-user instances from human-written generators; retired after use; pad only; typed only | "unseen by your agent, not proctored" |
| Checkup | Hidden tests on the service; tasks retired after use per token; container | "Checkup, not proctored" |
| Study-only pool | Never shipped; served in the study only; exposure tracked; retired | Used in the study |
| Proctored live check (later) | A person present | "proctored" |

### 4.3 Provenance

`typed` only under the conditions in `architecture.md` section 2.3. Keys for unseen and Checkup items release only after a typed lock. An agent that runs `firsthand answer` produces `relayed`, which cannot count and cannot release those keys.

---

## 5. Work installs (RT privacy 1)

### 5.1 What the employer can see

| Channel | Can the employer see it? |
| :- | :- |
| That Firsthand is installed; hooks, config files, instruction blocks | Yes |
| The record folder on a managed laptop | Yes if not encrypted, through device management or backup [unverified per product] |
| Questions, answers and verdicts in the agent's chat | Possibly: enterprise agent plans can keep logs admins can export [unverified per vendor] |
| Model grading calls on the work account | Possibly, through the vendor's admin tools [unverified per vendor] |
| Carry branches in work repos | Yes, as branch names, times and sizes |
| A relay the employer runs | Device sync times and sizes |

### 5.2 Defaults on a work install

- Answers go to the pad, not the chat. The chat shows only "Question in your pad".
- The record is encrypted at rest.
- `grader = local-only`.
- No carry branch in repos the user does not own.
- Admins cannot require a relay, including a self-hosted one. This control is removed.

### 5.3 The copy

The work-install copy in `experience.md` section 2 replaces "Your employer cannot see ... No key allows it." It lists what the employer can see, what it cannot, and the limit. It never promises that use is invisible.

---

## 6. What leaves the machine (RT privacy 6)

The table in `../PRODUCT.md` section 6.9 is the source. Rules:

- No copy anywhere says "nothing leaves the machine". The install copy says "Firsthand sends nothing by default" and then names the chat and the grader.
- Every model grader names the receiving company and account before first use.
- The Checkup client names what it sends before each first call.
- `firsthand privacy` prints the current table for this install, with each path's state.

---

## 7. Repo content and prompt injection (RT privacy 5)

Text written by repo contributors: guide files, owner notes, postmortem drills, commit messages, code excerpts, PR bodies.

- **Quoted and attributed.** Shown inside a block that starts "From this repo, written by contributors:", never in the product's own voice, and never as an instruction to the agent.
- **Stripped.** Owner notes and drill text have commands, URLs and code fences removed before display. A note that was mostly a command shows "This note had a command, removed for safety."
- **Trusted repos only.** Guides are read only in repos the user marks as theirs or trusted, once per repo, in the pad.
- **Narrow-only tools.** Agent-callable tools (`config`, `import`, `forget`, `delete`, `consent`, `grader`, `remote`) can only narrow: quieter, lower budget, fewer providers, less sharing. Any widening needs a typed confirmation in the pad, which the engine opens itself. On surfaces with no local terminal, widening waits for the next local session.
- **Grader input** marks the answer and any excerpt as data that may contain instructions.

---

## 8. Shared repos (RT privacy 7)

- Neutral `TODO:` markers in repos the user does not own, handed back at commit by default.
- No marker, no product name and no learning text in PR bodies. A cloud agent opening a PR keeps open lines only in its private carry or import blob.
- CI message: `Open TODO in retry.py:42.` No product name, no "your line".
- No carry branches in repos the user does not own. Carry branch names are neutral (`sync/<random>`).
- Review-first findings are private. Posting is the user's own comment.

---

## 9. Secrets and keys (RT privacy 8)

- Every free-text field is secret-scanned before write (`architecture.md` section 2).
- Private keys live in the OS keychain or `~/.config/firsthand/keys/` (mode 0600), never in the record. A commit guard refuses key material in the record.
- Postmortem drills: logs and text are scanned for secrets and personal data (emails, names from the git author list, IP addresses, tokens). The author sees each redaction and approves the drill before it is saved.
- Excerpts stay off by default, and pass the scan when on.

---

## 10. Cloud carry (RT privacy 10)

Rules in `architecture.md` section 8. Summary: the local engine creates the branch; cloud only appends; allowlisted event types; strict validation; labelled unauthenticated; capped at Met; deletes only its own branches by recorded name; the prompt says deletion is not erasure.

---

## 11. Team plane (RT privacy 9)

Rules in `teams.md` sections 4 and 5. Summary: fixed group definitions; suppression when the opted-in set changes by fewer than the floor; no opted-in count; no admin-defined outcomes; admin defaults capped at Standard with no reminder; no relay requirement; proof packs stamped "not a performance measure"; legal review of the consent basis before launch, since employee consent is rarely freely given [verified: https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_202005_consent_en.pdf].

---

## 12. Hardening (RT privacy 12)

- Project ids: keyed HMAC of the remote URL.
- `forget <idea>`: removes every event for the idea, rewrites record history, expires the reflog, runs a prune, and warns that any remote or backup keeps old copies until rewritten there.
- Hook payloads and debug logs: never stored.
- Scratch folders: mode 0700, per user, deleted after use.
- Device link (v2): one interface, authenticated pairing (`architecture.md` section 9).

---

## 13. Live today: the existing skill (RT privacy 11)

`skills/learning-while-building/SKILL.md` line 103 tells users to commit `.learning/` to the project repo. Existing users' misses may be in project history now. Actions:

1. v0 week one: change the skill to recommend `--dir` outside the repo by default, and to explain the risk of committing `.learning/` in a shared repo.
2. A short note to current users, on the site and in the skill's README, saying what the old default did and how to rewrite history in repos they own.
3. Migration (`architecture.md` section 11) repeats this plainly and offers the rewrite.

---

## 14. Conformance checks for security

Each release, per tested surface: hooks return no permission decision; hook and MCP entries point to the verified binary; no hook payload is written to disk; widening tools refuse without a pad confirmation; scratch copies contain no stripped config and no untracked files; carry import rejects a non-allowlisted event; work-install defaults are set.
