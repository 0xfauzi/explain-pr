# Platform: local-first data, sync, privacy

Track: local-first data, sync, privacy and platform.
Date: 2026-11-07. Author role: systems architect for local-first and
privacy-preserving products.

This report designs the data plane for a general product: anyone installs it
on any coding surface, builds a large project with an AI agent, and becomes a
better engineer. The earlier design round (`design/learning-experience/`) was
built for one person on Claude Code with a claude.ai artifact as the Room. I
used it as evidence, mainly its platform critique
(`design/learning-experience/critique/platform-engineering.md`), which found
that the store was undefined for cloud sessions, the artifact db is
last-writer-wins, and the rubric reached the page before the answer. Those
three findings are the starting constraints here, not side notes.

## How to read the tags

- **[verified: source]** I read the source in this session, or a search result
  quoted it. The URL is in the tag or in section 15.
- **[unverified]** From memory or a secondary source I did not open. Treat as a
  hypothesis to check.
- **needs to be measured** No number exists yet. I do not invent one.

---

## 1. The answer in twelve lines

1. The record is an append-only event log of plain files in a local git repo
   the tool owns. Everything else (schedule, map, due list) is derived.
2. One local engine, `lwb`, is the only writer. Every surface reaches it the
   same way: a CLI, an MCP server, and an Agent Skill that tells the agent to
   use them.
3. No account, no server and no remote by default. A user who never asks for
   sync gets a complete product on one computer.
4. A phone works with no remote through a device link: the computer hands the
   phone a sealed pack of due cards, and the phone hands back sealed answers.
   Transport is a QR code, a file, or the local network.
5. The one daily reminder, with no remote, comes from the phone's own
   scheduler: a recurring calendar event in phase 1, local notifications in a
   native app later. Web push always needs a sender server.
6. Sync across machines is opt-in, in two kinds: a git remote the user already
   trusts, or an end-to-end encrypted mailbox relay we run (or they self-host).
7. Cloud coding sessions have disks that are thrown away. They cannot keep a
   record without some remote. The product says so at first use and asks once.
8. Encryption follows the pattern of Tailscale and 1Password: keys are made on
   devices and never leave them; servers move ciphertext and public keys only.
9. Answer keys are sealed by commit-and-reveal plus an ordering rule enforced
   by the engine: no key leaves the engine until the answer is locked.
10. The record cannot prove skill to anyone else, because the learner owns it.
    We make it tamper-evident (hash chain, signed commits) and offer a separate
    "live check" when a third party needs trust.
11. Telemetry is off by default. Efficacy is measured with opt-in aggregate
    protocols (Prio3 over DAP) or by consented studies, never by collecting
    answers or code.
12. Teams get SSO, region-pinned ciphertext relays and aggregate views with a
    minimum group size. No admin can read an individual record.

---

## 2. Requirements this design must meet

### 2.1 From the founder decisions

| # | Decision | What it forces in the data plane |
|---|---|---|
| 1 | Record in a local git repo the tool commits to; no remote unless asked | `lwb` owns a repo and commits. Sync is a separate opt-in layer. Cloud sessions need an explicit ask (section 6). |
| 2 | "Your line": the agent leaves one marked line for the learner | The record must store the marker, the learner's line, its diff hash and the outcome, without storing project code (section 4.4). |
| 3 | At most 3 due reviews a day by default | The daily cap is computed in one place (the engine) and copied into every pack, so a phone and a laptop never show 3 each. |
| 4 | One confirmation tap on the phone is acceptable | Pairing, and returning answers to the computer, may each cost one tap. |
| 5 | Keyboard letter shortcuts off by default | Not a data concern. Stored in `config/` like other preferences, synced with them. |
| 6 | Feature parity on all coding surfaces | The engine must not depend on any one harness feature (hooks, artifacts, subagents). Section 8 lists the floor every surface gets. |
| 7 | At most one reminder a day, at a time the user chooses | The reminder lives on the device that shows it, and holds no content. The engine records which device owns the reminder, so two devices never both ring. |

I accept all seven. I do not challenge any of them. Two need clarifying, with
evidence, and I say so explicitly:

- **Decision 1 and cloud sessions.** A cloud session's disk does not survive.
  OpenAI says Codex cloud caches container state "for up to 12 hours"
  [verified: https://developers.openai.com/codex/cloud/environments]. Claude
  Code on the web gives "an isolated virtual machine" per session
  [verified: https://support.claude.com/en/articles/12618689-claude-code-on-the-web].
  With no remote, a record written there is lost. This is not a reason to
  change the decision. It is a reason to make "asks" a single clear step the
  first time the product runs on a surface with no lasting disk.
- **Decision 1 and the phone.** A phone cannot practically run git. So "the
  record lives in git" means: the system of record is git on a computer, and
  the phone holds a projection plus an outbox. The phone never becomes a git
  peer.

### 2.2 From the product, not the founder

- Works offline, fully, on one computer.
- Account-free use with no feature hidden behind an account.
- Readable without our software: plain JSON and Markdown, a published format.
- Survives the product's death: a user can stop using us and keep everything.
- Safe in a public project: the record must never land in a public repo by
  accident (the earlier round found explain-pr itself is public).
- Two writers can never lose an answer.

---

## 3. Threat model

What we protect, from whom, in order of how likely it is.

| Threat | Likely? | What we do |
|---|---|---|
| The learner sees the answer key before answering (accidental glance) | High | Seal keys; never render them before lock (section 9). |
| The asking agent leaks the key in a hint, or reads it from disk | High | Keys never enter the asking context; engine refuses reveal before lock; separate grader context where the surface allows (section 9). |
| The record is committed to a public project repo | Medium | Record lives in its own repo outside the project tree by default (section 4.1). |
| A cloud session ends and the record is lost | High on cloud surfaces | First-run ask; outbox export; optional remote (section 6). |
| Two devices answer the same card; one answer is lost | Medium | One writer per file; answers are append-only; earliest lock wins (section 4.3). |
| A sync server is breached or subpoenaed | Low per user, high impact | Relay holds ciphertext only; keys on devices (section 7). |
| An employer uses the tool to rank or surveil staff | Medium in teams | No individual views for admins; minimum group size; learner-held keys (section 11). |
| The learner edits their own record to look better | Low, and their right | Tamper-evidence, not prevention. Third-party trust comes from a live check (section 10). |
| An agent hand-edits the record files | Medium | Engine is the only writer; `lwb check` detects edits; hash chain (section 10). |
| Telemetry identifies a person | Medium if we collect it | Off by default; aggregate-only protocols; no content ever (section 12). |

Out of scope: a malicious agent with full shell access that is trying to
cheat on the learner's behalf. It can read the source code from which every
rubric is derived. No local scheme stops that, and we say so in Settings.

---

## 4. The record

### 4.1 Where it lives

Default: one record repo per user, not per project.

```
~/.local/share/lwb/record/          (Linux; macOS and Windows use their app-data folder)
  .git/
  FORMAT                            "lwb-record 1"
  devices/<device-id>.json          public keys and names of paired devices
  config/<key>.json                 one file per preference (cap, reminder time, shortcuts)
  projects/<project-id>.json        name, local path hint, remote URL hash; never code
  topics/<topic-id>.json            the concept, its dimension, where it was met
  events/<yyyy>/<mm>/<event-id>.json  one file per event, append-only
  sealed/                           encrypted answer keys (section 9)
  .gitattributes, .gitignore
derived, never committed:
  ~/.cache/lwb/state.sqlite         schedule, due list, map, open cards
```

Why per user and outside the project:

- A learner meets the same concept (idempotency, a retry budget) in many
  projects. Spacing and transfer need one history across them.
- It removes the public-repo leak by construction. The current skill keeps the
  record in `.learning/` inside the project, which the earlier critique
  flagged for public repos.
- A project can still opt in to a project-local record (`lwb init --here`) for
  teams that want it reviewed with the code. Then `lwb` checks the project's
  remote visibility first and refuses a public one unless forced.

### 4.2 The event log

Every change is an event file. Nothing is updated in place except derived
state, which is rebuilt.

```json
{
  "v": 1,
  "id": "01JC8Y3W8Q5V7N2K4T6R9X1M0B",
  "type": "answer.locked",
  "card": "01JC8Y2F...",
  "device": "dev_7f3a",
  "surface": "codex-cli",
  "at": "2026-11-07T14:02:11Z",
  "body": {"answer_sha256": "...", "answer": "The write is durable first...", "confidence": "fairly sure"},
  "prev": "sha256:...",
  "sig": null
}
```

- IDs are ULIDs, so files sort by time and two devices never collide.
- One file per event means git merges never conflict on content: two devices
  add different files. This is the same idea the current `record.py` uses
  (one file per attempt), extended to every change.
- `prev` is the hash of the same device's previous event: a per-device hash
  chain (section 10). Per device, not global, so offline devices never need to
  agree on an order.
- Event types (first set): `card.drafted`, `card.sealed`, `card.delivered`,
  `answer.locked`, `key.revealed`, `grade.recorded`, `review.scheduled`,
  `line.offered`, `line.written`, `config.set`, `device.paired`,
  `device.revoked`, `topic.added`, `topic.retired`.
- Derived state is a fold over events. The scheduler (FSRS or the current
  ladder) reads the fold. A new scheduler can be swapped in by replaying the
  log, which is what Anki-style review logs allow [unverified].

### 4.3 Conflict rules

There are only three, and each is a pure function of the events:

1. **Earliest lock wins.** If two devices lock answers to one card, the one
   with the earlier `at` is the attempt. The other is kept and shown as
   "also answered". Clocks drift, so ties within 2 minutes are broken by
   device id and both are shown; the 2 minutes is a choice, not a measured
   value.
2. **Last `config.set` wins per key.** Preferences are the only "update"
   semantics. Each key is its own file, so two keys never clash.
3. **Daily cap is per user, not per device.** The engine assigns each due card
   to a day when it builds a pack. A card in a phone pack is marked
   `delivered(phone)` so the laptop does not also offer it that day.

This is why the design does not need a CRDT library: the data is an
append-only set of immutable events, which is already conflict-free when
merged as a union. CRDTs earn their cost when many people edit one shared
structure (text, lists). A learning record has one author and immutable
facts. Section 5.2 compares the options anyway.

### 4.4 What is never stored

- Project source code. A card stores a path, a line range and a hash of the
  excerpt, plus the excerpt text only if the user turns on "keep excerpts"
  (needed for review after the code changes). Default: keep excerpts, because
  a review card is useless without them; the user can turn it off per project.
- For "your line": the marker location, the learner's line, the agent's
  reference line hash, test outcome, and whether the line survived the next
  commit. Not the surrounding file.
- Secrets. The engine runs a secret scanner over excerpts before writing
  [unverified: choice of scanner].

---

## 5. Sync: options compared

### 5.1 The jobs sync must do

| Job | Example |
|---|---|
| J1 | Two computers, same user, both offline sometimes |
| J2 | A cloud coding session (disk discarded) writes to the record |
| J3 | A phone shows today's due cards and sends back answers |
| J4 | One daily reminder on the device the user chose |
| J5 | A team sees aggregate progress, never individuals |

### 5.2 Comparison

| Option | J1 | J2 | J3 | J4 | E2E | Cost to user | Verdict |
|---|---|---|---|---|---|---|---|
| **Plain git remote** (GitHub, GitLab, own server) | Yes | Yes, if the session can reach the remote | No (phone cannot run git) | No | No: host reads plain files | Has to own a private repo | Ship as the first opt-in for developers. They already have this. |
| **Encrypted git remote** (git-remote-gcrypt, git-agecrypt) | Yes | Needs the key in the cloud session | No | No | Yes for content | Key handling in every session | Offer as advanced. git-agecrypt is "a modern, portable replacement for git-crypt" using age [verified: https://github.com/bartei/git-agecrypt]. Filter tools can leak plaintext through `git log -p` [verified: same search], and revoking a recipient needs a history rewrite. |
| **Automerge + automerge-repo** | Yes | Yes with a sync server | Yes in a web app | No | Not by default | Runs a sync server | Strong for collaborative documents. Automerge 3 cut memory use and kept the file format [verified: https://automerge.org/blog/automerge-3/]. The docs say to run your own server in production [verified: https://automerge.org/docs/tutorial/network-sync/]. Not needed for an append-only log. |
| **Yjs + y-indexeddb** | Yes | With a provider | Yes in a web app | No | Not by default | Provider server | Good offline story in the browser [verified: https://docs.yjs.dev/getting-started/allowing-offline-editing]. Same verdict as Automerge. |
| **Keyhive / Beelay** (Ink & Switch) | Yes | Yes | Yes | No | Yes, by design | Pre-alpha | Watch. "Pre-alpha" [verified: https://www.inkandswitch.com/newsletter/dispatch-010]. Its goal, a server that only sees encrypted data, is ours. |
| **Jazz** | Yes | Yes | Yes | No | Yes, "encrypted and signed by default" [unverified: secondary source] | Jazz Cloud or self-host | Credible, but adopting a framework for an event log adds a dependency we do not need. |
| **ElectricSQL, PowerSync** | Yes | Yes | Yes | No | No | Postgres backend | Server-authoritative sync engines [unverified: https://powersync.com/blog/electricsql-electric-next-vs-powersync]. Wrong shape: they assume our server holds plaintext. |
| **Our blind mailbox relay** (section 7) | Yes | Yes | Yes | Yes (push) | Yes | Optional free tier or self-host | Recommended second opt-in. Small, auditable, and reuses the event log as is. |
| **Device link, no server** (section 6.3) | Partly (manual) | Export only | Yes | Via calendar | Yes | One tap or scan | Recommended default for the phone. |

### 5.3 What the comparison says

The record's shape decides the sync tool. It is an append-only set of small
immutable files with one human author. Any transport that can move files and
union them works: git, a mailbox, a QR code. So we keep the format fixed and
make the transport pluggable. We do not adopt a CRDT library or framework for
the record. If a future feature needs live shared editing (a team's shared
topic map, say), Automerge is the first candidate for that feature alone.

---

## 6. Devices and surfaces

### 6.1 Computers with a lasting disk

CLI, desktop and IDE surfaces of every agent (Claude Code, Codex, Cursor,
Copilot in VS Code, Gemini CLI, Windsurf). The engine runs locally and owns
the record repo. Nothing leaves the machine. This is the default and the
whole product works here.

### 6.2 Cloud coding sessions (ephemeral disks)

Claude Code on the web, Codex cloud, Copilot coding agent, Cursor background
agents, and similar. Facts that shape the design:

- The session gets a fresh VM or container [verified: https://support.claude.com/en/articles/12618689-claude-code-on-the-web;
  https://developers.openai.com/codex/cloud/environments].
- Network is restricted by default on both. Codex: "Agent internet access is
  off by default"; setup scripts have internet [verified: Codex environments
  page]. Claude Code on the web: admins choose None or Trusted (allowlist)
  [verified: support article above].
- Only the project repo is reliably there, and it may be public.

So with no remote there is nowhere durable to write. Three ways out, offered
in this order the first time `lwb` detects an ephemeral session (detected by
environment markers, [unverified] per surface, needs a probe per surface):

1. **Carry out by hand (no remote, default).** The session writes events to
   an outbox and, at the end of each learning moment, prints a one-line
   `lwb import` command holding a compressed, encrypted bundle. The user
   pastes it on their computer, or the agent writes it to a file the user
   downloads. Cost: one paste per session. Honest weakness: users forget.
2. **Use a private git remote they already have.** `lwb remote add` with a
   private repo. The session must have that repo attached (Claude Code on the
   web lets a session attach further repositories [verified: this session's
   tool list includes add_repo]; other surfaces [unverified]). The engine
   commits and pushes after each event: `git pull --rebase`, retry once.
3. **Use the blind relay.** The session needs one allowed host
   (`relay.<product>.dev`, name to be chosen) and a device key. The key is a
   secret, so it goes through the surface's secret store, never a file in the
   repo. Events are encrypted on the way out.

The product never silently picks 2 or 3. That satisfies decision 1: the user
asks, once, in one step.

What never happens: writing the record to the project repo of a cloud
session, and never to a branch of it, because branches of a public repo are
public.

### 6.3 The phone with no remote: the device link

The phone gets a **pack** and gives back an **outbox**.

- **Pack:** today's due cards (at most 3 by default) and up to 6 days ahead,
  each with prompt, excerpt and confidence scale, but **no answer keys**.
  Encrypted to the phone's key. Size target: small enough for a QR sequence
  or a single file; the exact size needs to be measured.
- **Outbox:** the learner's locked answers, encrypted to the user's computers.
- **Pairing:** the computer shows a QR code holding a one-time pairing secret
  and its public key; the phone app scans it and returns its own public key.
  This is the Tailscale pattern: private keys "never leave the local device"
  [verified: https://tailscale.com/kb/1232/derp-servers].
- **Transport, no server:** (a) same Wi-Fi: the engine listens on the local
  network for a few minutes after the user taps "sync phone" (one tap, within
  decision 4); (b) file: AirDrop, Nearby Share, a USB cable, or a file in a
  folder they already sync; (c) QR: the phone shows answers as a QR the
  laptop camera reads. The pack lasts 7 days, so the phone works through a
  week away from the computer.
- **Grading on the phone:** without keys, the phone cannot grade. It locks the
  answer and shows "graded when you next sync". For `choice` and `number`
  cards, a key can travel in the pack encrypted under a per-card key that the
  phone only derives after the answer is locked locally; this protects
  against a glance, not a determined learner, and Settings says so.

This trades instant feedback on the phone for no server. Delayed feedback is
not free: the learning-science track should confirm how much immediacy
matters for these card kinds (see `design/product/research/learning-science.md`
section C.7). If it matters a lot, that is the strongest reason to opt in to
the relay.

### 6.4 The one daily reminder

A reminder at a chosen time needs something on the phone to fire at that
time. Options:

| Option | Server needed | iOS | Android | Content in reminder | Verdict |
|---|---|---|---|---|---|
| Web push from a PWA | Yes, a push sender | Only for Home Screen web apps, iOS 16.4+, permission after a user gesture [verified: https://documentation.onesignal.com/docs/safari-web-push-for-ios; https://mjtsai.com/blog/2023/02/21/web-push-for-web-apps-on-ios-and-ipados] | Yes | Optional, encrypted payload | Needs the relay. Phase 2. |
| Declarative Web Push | Yes, a push sender | iOS 18.4+, Home Screen web apps, no service worker needed [verified: https://webkit.org/blog/16535/meet-declarative-web-push/] | Partly | As above | More reliable display on iOS, same server need. |
| Notification Triggers (local, scheduled, from the web) | No | No | Not shipped: origin trial complete, launch "not started" [verified: https://developer.chrome.com/docs/web-platform/notification-triggers] | n/a | Not available. |
| Native app local notifications | No | Yes [unverified: iOS UNUserNotificationCenter supports local scheduled notifications, from memory] | Yes [unverified] | Count only | Best no-server path. Phase 3. |
| Recurring calendar event, imported once | No | Yes | Yes | None ("Review, 5 minutes") | Phase 1 default. Works today on every phone. |
| Subscribed calendar feed | Yes, a feed host | Refresh interval varies | Google refreshes slowly, 12 to 24 hours reported [unverified: https://usecarly.com/blog/google-calendar-ics-refresh-rate/] | Due count | Too slow and needs a host. No. |
| Self-hosted ntfy | Their server, plus ntfy.sh upstream on iOS | iOS needs an upstream poll through ntfy.sh [unverified: secondary guides] | Yes | Optional | Option for self-hosters; document, do not build. |

Phase 1 reminder: `lwb reminder set 18:30` writes a single `.ics` file with
one recurring event at that time, which the user opens once on the phone.
The event says only "Review time. Open the app." It does not know the due
count, so on a day with nothing due it still fires. To avoid ringing on
empty days, the PWA shows "nothing due" and the engine shifts work so most
days have at least one item; whether empty-day reminders hurt the habit
needs to be measured.

The engine records `reminder.owner = device` so only one device holds the
reminder, which keeps decision 7 across devices.

---

## 7. The blind mailbox relay (opt-in)

The smallest server that unlocks J1 to J4 without seeing data.

### 7.1 What it is

- A store of encrypted envelopes, addressed to device public keys.
- A push sender (Web Push, Declarative Web Push, APNs and FCM for a native
  app later) that sends content-free or encrypted pushes.
- No accounts. A "user" is a set of device keys that vouch for each other.
  Optional email only for team billing.

### 7.2 What the relay can see

| Sees | Does not see |
|---|---|
| Device public keys, envelope sizes, times, which keys exchange envelopes, IP addresses, the daily push fire time | Answers, rubrics, topics, code, names, scores, due counts, what the push is for |

To send a push at 18:30 the relay must know 18:30, so the fire time is
visible. Nothing else about the reminder is. Obsidian makes the same kind of trade openly: its server sees what it
needs "to route changes" and hashes are deterministic [verified:
https://obsidian.md/help/sync/security]. We publish our own list of what the
relay sees in the same plain way.

Padding: envelopes are padded to fixed size buckets so size does not reveal
how many answers were sent. Bucket sizes need to be measured against real
packs.

### 7.3 Keys

- Each device makes an X25519 key pair (age-compatible) at install. Private
  keys never leave it.
- A **record key** (random, 256 bits) encrypts events at rest in the relay.
  It is wrapped to each device's public key.
- Pairing a new device: an existing device shows a QR code; the new device
  receives the wrapped record key. No password needed.
- Recovery: at setup the user is shown a **recovery key** (random, printed or
  saved), the same idea as 1Password's high-entropy Secret Key mixed into key
  derivation so a stolen server copy cannot be cracked [verified:
  https://agilebits.github.io/security-design/apsk.html]. Lose all devices and
  the recovery key, and the relay copy is unreadable. That matches Obsidian:
  "We're not able to recover your password, or any encrypted data"
  [verified: https://obsidian.md/help/sync/security]. The local git repo is
  still the primary copy, so loss of the relay copy is not loss of data for
  most users.
- Ciphers: XChaCha20-Poly1305 for envelopes, as Standard Notes uses
  [verified: https://standardnotes.com/help/security/encryption], via a
  maintained library (libsodium or age). We do not write our own crypto.
- Revocation: `lwb device revoke` writes a `device.revoked` event and rotates
  the record key; old envelopes stay readable only by the remaining devices
  after re-wrap. Tailscale's note applies: without the coordinator, keys
  cannot be revoked [verified: https://tailscale.com/docs/reference/coordination-server-down.md];
  for us, revocation needs one online device, not our server.

### 7.4 Self-hosting and regions

The relay is open source and runs as one container with a small database.
Teams can pin a hosted relay to a region or run their own. Anki shows the
cost of an unofficial self-host path: third-party servers "tend to take time
to catch up" when the protocol changes [verified:
https://docs.ankiweb.net/sync-server.md]. So we ship and test the self-host
build ourselves, and version the protocol with explicit compatibility.

### 7.5 What we copy from each product

| Product | What we copy | What we avoid |
|---|---|---|
| Anki | Review log as the source; schedule derived; official self-host server [verified: docs.ankiweb.net] | Version lockstep between client and server breaking sync [verified: same page] |
| Obsidian Sync | Plain-language list of what the server sees; E2E as the recommended default [verified: obsidian.md/help/sync/security] | A "standard encryption" mode where the vendor holds keys |
| Standard Notes | Item-level keys so a password change re-wraps a few keys, not all data; signed items [verified: standardnotes.com/help/3] | Password as the only root secret |
| 1Password | High-entropy device secret mixed into key derivation [verified: agilebits.github.io/security-design] | Account-first onboarding |
| Tailscale | Keys born on devices; server only moves public keys and ciphertext; relay as fallback [verified: tailscale.com/kb/1232] | Hard dependency on the coordinator for joining |

---

## 8. Platform and parity

### 8.1 The parity floor

Decision 6 asks for parity on every surface. Harness features differ (hooks,
subagents, artifacts, rendering). So parity is defined at the data plane:
every surface gets the same record, the same cards, the same cap and the same
sealing, through mechanisms all of them share.

| Layer | Mechanism | Coverage |
|---|---|---|
| Instructions | Agent Skill folder (`SKILL.md` + scripts) | Codex reads `SKILL.md` skills from repo, user and admin locations [verified: https://developers.openai.com/codex/skills]; the open standard lists Claude Code, Cursor, Codex, Gemini CLI, Copilot, VS Code and others [unverified: secondary summaries of https://agentskills.io]. Also emit `AGENTS.md` and per-tool rule files for tools without skills. |
| Tools | Local MCP server over stdio (`lwb mcp`) | Most listed agents support stdio MCP [unverified per agent; needs a probe matrix]. |
| Fallback | Plain CLI (`lwb ask`, `lwb lock`, `lwb due`) | Any agent with a shell. |
| Cloud | Same CLI and MCP, plus the outbox or a remote (section 6.2) | Depends on network policy per surface. |
| Phone | PWA in phase 1, native app later | Same pack format on both. |

The engine is one static binary per OS (Go or Rust; [unverified] choice), so
install is one download with no Python or Node runtime. The current skill
needs Python 3.10+, which some cloud images have and some do not [unverified].

### 8.2 Install paths

- `curl | sh`, Homebrew, Scoop, npm wrapper and a pip wrapper, all fetching
  the same signed binary.
- `lwb setup` detects installed agents and writes their config (MCP entry,
  skill folder) after showing the user each file it will change.
- In a cloud session, the project's setup script runs `lwb setup --ephemeral`.
  The engine then refuses to pretend the record is durable.

---

## 9. Sealing the answer key

### 9.1 What we must prevent

1. The learner sees the key before answering.
2. The asking agent puts the key, or a giveaway, into a hint.
3. The key is changed after the answer, to fit it.

### 9.2 Mechanism

1. **Separate author.** The key (rubric) is written by a context that does
   not talk to the learner: a subagent where the surface has them, or a
   separate model call made by the engine through the agent's own tool call.
   On surfaces with neither, the main agent writes it in a single tool call
   and the skill tells it not to restate it; this is weaker and Settings says
   so per surface.
2. **Commit.** `lwb seal` stores `sha256(salt || rubric)` in a `card.sealed`
   event and the rubric, encrypted to the engine's local key, in `sealed/`.
   The tool returns only the hash. So the transcript shows a hash, not text.
3. **Order enforced by the engine.** `lwb reveal <card>` refuses unless an
   `answer.locked` event exists for that card. This is the fix for the
   earlier round's "rubric in page memory before the answer" finding: the
   key never reaches any page, pack or context before the lock.
4. **Grade in a fresh context.** Where possible the grader sees the rubric
   and the answer but not the conversation, so a hint-leaking agent cannot
   also be the grader. Where not possible, the main agent grades after
   reveal.
5. **Verify.** `lwb check` recomputes the hash for every revealed key. A
   changed key fails loudly.

Honest limit: the rubric is derived from code the agent can read. An agent
can always rebuild the answer from the code. Sealing protects the learner
from accidental exposure and makes the key provably fixed. It is not
protection against a determined cheat, and nothing local can be.

### 9.3 Sealing on the phone

Covered in 6.3. Keys for free-text cards never go to the phone. For choice
and number cards, a per-card key is released by the phone's local app only
after a local lock, which only guards against a glance.

---

## 10. Tamper resistance of a self-graded record

### 10.1 Who it is for

- The learner: trust that the map reflects real attempts, not agent edits.
- Third parties (a mentor, a team lead, a hiring panel): only if the learner
  chooses to share.

### 10.2 Mechanisms

| Mechanism | Detects | Cost |
|---|---|---|
| Engine as only writer; files carry a schema version | Agent hand-edits that break schema | None |
| Per-device hash chain (`prev`) | Deleted or edited events within a device's history | None |
| Signed commits with a device SSH key (`gpg.format ssh`, `gpg.ssh.allowedSignersFile`) [verified: https://docs.gitlab.com/user/project/repository/signed_commits/ssh.html] | Commits not made by a paired device | Needs Git 2.34+ and OpenSSH 8.1+ [verified: same page] |
| Grade events carry rubric hash, answer hash, grader surface and model | Changed keys; grades without a sealed key | None |
| `lwb check` | All of the above, on demand and before any share | Seconds; time needs to be measured |

Signing is on by default when the engine can make a key; it is a nice to
have, not a gate.

### 10.3 What it cannot do

The learner owns every key, so they can rewrite history and re-sign it. A
self-graded record can never be proof to someone else. For that, offer a
**live check**: a short, proctored session (a teammate or interviewer sends a
challenge seed; the engine generates fresh cards on the learner's topics
from code the reviewer chooses; answers and grades are signed by both). The
live check is evidence; the record is a guide to what to check. This keeps
us from building a credential on data that cannot carry one.

---

## 11. Teams and enterprise

### 11.1 What teams ask for

- SSO (OIDC, SAML) and SCIM for seats.
- Data residency.
- Proof the tool improves skill, at team level.
- Control over which surfaces and relays are used.

### 11.2 What teams do not get

- Any individual's answers, grades, map or calibration. Ever, by default.
- Per-person activity counts.

This is a product rule, not a setting an admin can flip. If managers can see
individuals, learners will answer for the manager, not for themselves, and
the record stops measuring learning. That is a reasoned claim from the
self-determination literature cited by the learning-science track, not a
measured effect for this product; it needs to be measured.

### 11.3 How team views work

- **Aggregate only, minimum group size.** Precedent: Microsoft Viva Insights
  will not show group insights below a minimum group size, and the floor
  cannot be set below five [verified:
  https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings].
  We use the same floor of five, default higher (the default value is a
  choice for the team-track designer; I propose ten, unmeasured).
- **Computed without a plaintext server copy.** Each learner's engine
  computes a few numbers locally (reviews done this week, share correct at
  7+ days, calibration gap) and submits them through Prio3 over DAP, so no
  single server sees an individual's value; privacy holds "as long as at
  least one of the aggregators operates according to the protocol"
  [verified: https://docs.divviup.org/how-it-works]. Divvi Up runs this in
  production [verified: https://divviup.org/blog/dap-update/].
- **Learner-initiated sharing.** A learner can send a signed snapshot of
  their map to a named person (a mentor). It is a copy, revocable only by
  asking, and the UI says so.

### 11.4 Admin controls

| Control | Allowed | Notes |
|---|---|---|
| Require the team relay or a self-hosted relay | Yes | Prevents use of the public relay. |
| Pin relay region | Yes | Relay holds ciphertext only, which simplifies residency, but metadata (IPs, times) is still personal data under GDPR [unverified legal reading]. |
| Turn telemetry off for everyone | Yes | |
| Turn telemetry on for everyone | No | Opt-in stays per person. |
| Set default daily cap or reminder | Yes, as a default | Learner can change it. |
| Read records, export records | No | No key exists for admins. |
| Delete a departing user's relay data | Yes | Deletes ciphertext; the local repo is theirs. |

Who owns the record when someone leaves? The learner. It is about their
skill, not company code; it stores excerpts of company code, though, so
"keep excerpts" can be turned off by an admin policy for a project. That is
the one place a team policy reaches into the record, and it removes data
rather than exposing it.

Works councils and employee-monitoring law in the EU may restrict even the
aggregate view [unverified]. The team plane must ship with a plain data
sheet so a works council can review it.

---

## 12. Telemetry and efficacy

### 12.1 Defaults

- No telemetry. No crash reports unless the user sends one.
- The engine never makes a network call the user did not cause, except
  update checks, which are off by default and one switch away.

### 12.2 Opt-in levels

| Level | What leaves the device | Protocol |
|---|---|---|
| 0 Off | Nothing | n/a |
| 1 Aggregate | A few bounded numbers per week (reviews done, share correct at long delay, calibration gap, cards skipped) | Prio3 over DAP via Divvi Up or a self-run pair of aggregators [verified: https://docs.divviup.org/how-it-works] |
| 1b Local DP | Yes/no flags with randomized response, for features where two aggregators are too heavy | Local differential privacy, as Apple describes for its count mean sketch [verified: https://machinelearning.apple.com/research/learning-with-privacy-at-scale] |
| 2 Study | Pseudonymous event summaries for a pre-registered study, with consent text, an end date and deletion | Separate consent, separate key, IRB or ethics review where the partner needs one |

Never collected at any level: code, excerpts, prompts, answers, rubrics,
project names, repo URLs, topic names.

Privacy budgets (epsilon) for 1b must be set and published before launch.
Apple's published budgets vary by feature [verified: Apple paper above]; we
do not copy a number, it needs to be chosen with the sample size in hand.

### 12.3 How to know it works

The founder's claim is that the product counters the skill loss found when
developers use AI to write code. The data plane must make that testable
without surveillance:

- **Within-person comparison.** The engine holds back a random share of
  eligible topics from review (a control set) for users who opt in to level
  1. Later delayed checks on both sets estimate the effect of review. The
  hold-back share and its cost to the learner need the learning-science
  track's sign-off.
- **Delayed transfer.** Share correct on transfer cards at 21+ days, by
  whether the topic had "your line" or not.
- **Calibration.** Gap between confidence and correctness over time.

All three are computable from the event log on the device, so only the
aggregate leaves.

---

## 13. Recommended layered architecture

```
L4  Team plane (opt-in, paid)      SSO, SCIM, aggregate views (DAP), policy, region relays
L3  Blind relay (opt-in)           encrypted mailbox, push sender, device keys, self-host build
L2  Device link (default for phone) pairing by QR, sealed packs and outboxes, LAN/file/QR transport
L1  Local engine (default)          lwb binary: CLI + stdio MCP + skill, sealing, scheduler, git commits
L0  Record format (spec)            event files, folder layout, conflict rules, versioned, public
```

Each layer works without the ones above it. A user who stops at L1 has the
whole learning loop on one computer.

### 13.1 What ships first (phase 1)

Goal: a general user on any computer surface gets the full loop, and a phone
gets due cards and one reminder, with no server we run.

1. L0 spec v1 published in the repo, with a migration from the current
   `.learning/` layout (one-shot `lwb migrate`).
2. L1 engine: one binary; record repo per user; event log; sealing with
   reveal-after-lock; per-device hash chain; daily cap; `lwb check`.
3. Parity floor: skill folder plus `AGENTS.md` plus stdio MCP plus CLI,
   with a tested matrix of at least Claude Code CLI, Codex CLI, Cursor,
   Copilot in VS Code and Gemini CLI. Each row tested, not assumed.
4. Cloud sessions: detection, the first-run ask, and option 1 (carry out by
   hand) and option 2 (private git remote).
5. L2 device link: PWA for the phone, QR pairing, pack and outbox over file
   and QR; LAN transport if it passes a test on iOS Safari (HTTPS on a local
   address is the hard part [unverified]).
6. Reminder: recurring calendar event from `lwb reminder set`.
7. Telemetry: none.

### 13.2 Phase 2

- L3 relay: encrypted mailbox, Web Push and Declarative Web Push to the
  Home Screen PWA, device revocation, self-host container, published "what
  the relay sees" sheet, external audit before general availability.
- Signed commits on by default.
- Level 1 aggregate telemetry through DAP, opt-in.
- Live check (section 10.3).

### 13.3 Phase 3

- Native phone app with local notifications (reminder without relay) and
  instant grading for choice cards.
- L4 team plane.
- Evaluate Keyhive/Beelay or Automerge for any feature that needs live
  shared editing.

---

## 14. Open questions and experiments

| ID | Question | Cheapest test |
|---|---|---|
| E1 | Which surfaces load a stdio MCP server and a skill folder from a project or user path? | Probe matrix: install on each, ask the agent to call `lwb ping`. One day. |
| E2 | Can each cloud surface reach a private second repo or one allowed host? | One session per surface with option 2 and option 3. |
| E3 | Do learners actually paste the carry-out bundle? | Count imports against sessions for opted-in testers; needs to be measured. |
| E4 | Does delayed grading on the phone hurt learning compared with instant? | Learning-science track to design; A/B in phase 2 when the relay exists. |
| E5 | Does an empty-day calendar reminder erode the habit? | Opt-in testers, compare reminder dismissals; needs to be measured. |
| E6 | Pack and outbox sizes for QR transport | Build packs from real records and measure. |
| E7 | Can a PWA on iOS reach the laptop over the LAN with a valid certificate? | Prototype; if not, drop LAN transport on iOS. |
| E8 | What do admins accept as a team view with no individuals? | Five interviews with engineering managers (users-market track). |
| E9 | Is the record format readable by a learner without the tool? | Ask three testers to answer "what did I get wrong last week" from the files alone. |

---

## 15. Sources

- Codex cloud environments: https://developers.openai.com/codex/cloud/environments
- Codex skills: https://developers.openai.com/codex/skills
- Claude Code on the web: https://support.claude.com/en/articles/12618689-claude-code-on-the-web
- Agent Skills standard: https://agentskills.io (client list from secondary summaries)
- iOS web push requirements: https://documentation.onesignal.com/docs/safari-web-push-for-ios
- Apple 16.4 web push notes, quoted: https://mjtsai.com/blog/2023/02/21/web-push-for-web-apps-on-ios-and-ipados
- Declarative Web Push: https://webkit.org/blog/16535/meet-declarative-web-push/
- Notification Triggers status: https://developer.chrome.com/docs/web-platform/notification-triggers
- Automerge 3: https://automerge.org/blog/automerge-3/
- Automerge network sync: https://automerge.org/docs/tutorial/network-sync/
- Yjs offline: https://docs.yjs.dev/getting-started/allowing-offline-editing
- Keyhive and Beelay: https://www.inkandswitch.com/newsletter/dispatch-010
- ElectricSQL vs PowerSync (vendor view): https://powersync.com/blog/electricsql-electric-next-vs-powersync
- git-agecrypt: https://github.com/bartei/git-agecrypt
- Obsidian Sync security: https://obsidian.md/help/sync/security
- Standard Notes encryption: https://standardnotes.com/help/security/encryption
- Standard Notes overview: https://standardnotes.com/help/3/how-does-standard-notes-secure-my-notes
- 1Password Security Design, account password and Secret Key: https://agilebits.github.io/security-design/apsk.html
- Tailscale DERP: https://tailscale.com/kb/1232/derp-servers
- Tailscale coordination server outage: https://tailscale.com/docs/reference/coordination-server-down.md
- Anki self-hosted sync server: https://docs.ankiweb.net/sync-server.md
- Git SSH commit signing: https://docs.gitlab.com/user/project/repository/signed_commits/ssh.html
- Viva Insights privacy settings: https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings
- Divvi Up, how it works: https://docs.divviup.org/how-it-works
- Divvi Up DAP update: https://divviup.org/blog/dap-update/
- DAP draft: https://datatracker.ietf.org/doc/html/draft-ietf-ppm-dap-01
- Apple local differential privacy: https://machinelearning.apple.com/research/learning-with-privacy-at-scale
- Google ICS refresh (vendor blog): https://usecarly.com/blog/google-calendar-ics-refresh-rate/
- Earlier round, platform critique: `design/learning-experience/critique/platform-engineering.md`
