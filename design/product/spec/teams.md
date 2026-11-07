# Spec: teams, business model and distribution

Part of `../PRODUCT.md` (sections 7 and 8). Draws on `../concepts/teams.md`. Teams come after the individual loop shows retention (E1, E7). Nothing in this file is v1 except the shared-repo rules in section 3, which protect individuals.

---

## 1. Who and why

- Users: engineers on a team who build with agents, and the seniors and area owners who mentor them.
- Buyer: engineering managers and developer experience leads. 38% of leaders say AI cut the mentoring juniors get (https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles).
- What the buyer already pays for: onboarding and coverage of areas, not "skill scores".
- Why vendors are unlikely to build it: it spans rival agents, and it must refuse to show individuals to the buyer.

---

## 2. The codebase guide (v2, free)

### 2.1 Files

```
.firsthand/guide/
  guide.toml            areas, owners willing to mentor, settings
  ideas/<idea>.md       one file per codebase idea
  lines.toml            nominated "lines worth writing by hand once"
  drills/<id>.md        rehearsals drafted from postmortems; keys not here
```

Each idea file has: the idea in one sentence, where it lives (paths), why it matters here, how it breaks, an optional owner "how I debug this" note, and who is willing to help. No personal data, ever. The guide is committed only if the team chooses; it is reviewed in PRs like code.

### 2.2 Writing it

- `firsthand guide draft` reads structure, ADRs, READMEs, most-changed files and any postmortems the team points to, and proposes ideas with paths as a PR. Seniors edit and delete. How long a useful guide takes needs to be measured.
- `firsthand drill from <postmortem>` drafts a rehearsal: symptoms as first seen, logs, "what would you check first?", and the real resolution sealed as the key.
- `firsthand handover <area>` drafts guide entries from what the engineer built when rotating off.
- Guide health: `firsthand guide check` lists ideas whose paths no longer exist. It runs in CI if the team wants. It is not a chore the product pushes.

### 2.3 How the guide feeds the loop

- Guide ideas are private catalog entries in the team's namespace. They are shown on the map under their own heading, "This codebase", apart from transferable engineering ideas.
- After a learner calls the cause on a failing test in a guide area, the reveal can include the owner's "how I debug this" note. Never before the attempt (cognitive apprenticeship, L18).
- Nominated lines become your-line offers when a learner works in that area and the idea is new to them.
- Guide items ship without answer keys. The engine writes keys in a separate context, as for personal items. With the paid relay, owners can write sealed rubric points that travel encrypted to each learner's device; the stated limit is that a decrypted key on a learner's machine can be read by an agent with shell access.

### 2.4 First run in a guided repo

The guide's existence adds at most one line to the session-start offer, inside the bundled setup question for that repo: `This repo has a codebase guide with 12 ideas. Use it? Yes, or no.` At most one bundle per repo and one a day across repos (`../PRODUCT.md` 4.5).

---

## 3. Shared-repo rules (v1)

- No readable learning data in any branch. The carry branch (architecture section 8) is encrypted, side-only, never merged, and not offered in public repos.
- The optional merge check (`firsthand ci`) fails a PR only when it contains an open your-line marker that nobody chose to resolve. Its message: `Open your-line marker in retry.py:42. Write it, or comment "write it" to hand it back.` A hotfix branch pattern skips the check.
- The CI check also fails any PR containing a carry file.
- Who wrote a line is never written to commits, trailers or PRs.
- Optional PR walkthrough: the author writes a short walkthrough for reviewers. The engine grades it privately as an explain-back. Reviewers see the plain text only, never a grade. This is an explain-back to a real audience.

---

## 4. The admin contract

| Control | Allowed |
| :- | :- |
| Deploy engine and adapters (`firsthand team install` in a dev image) | Yes. Turns nothing on. First run still asks the engineer |
| Set defaults for dial, review cap (up to 3), reminder | Yes, as defaults the engineer can change |
| Require the team relay or a self-hosted relay | Yes |
| Pin relay region | Yes |
| Turn excerpt storage off for a project | Yes |
| Turn telemetry off for everyone | Yes |
| Turn telemetry, sharing or reports on for anyone | No |
| Raise the review cap above 3 | No |
| See who has the tool on, or who uses it | No. Seat counts come from SCIM, not from use |
| Read or export any record | No. No key exists |
| Lower the group floor | No |

The product shows the engineer, in the product, at the moment of a work install, what the employer can and cannot see (`experience.md` section 2).

---

## 5. The team report (later, paid)

- Each engineer can opt in to share a few counts their engine computes locally: guide ideas reached Recalled or better, by idea; onboarding milestones they chose to share.
- Transport: opt-in sharing through the team relay with a group floor. Counts appear only for groups of at least 8 opted-in people (design default; Viva Insights uses a floor that cannot go below five [verified: https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings]). No Prio3 or DAP in v1 or v2: it needs two independent, non-colluding aggregator operators [verified: https://datatracker.ietf.org/doc/draft-ietf-ppm-dap/]. Revisit only when paying customers ask for more.
- What it shows: guide coverage by area (how many guide ideas have any learners at Recalled or better), and onboarding outcomes the team defines.
- What it never shows: any individual, any skip rate, any level by person, who opted in.
- Never sold as a skill measure until a power check shows it can detect a change at the group floor. Codebase ideas and transferable ideas are reported apart.
- Legal review before launch: the EU AI Act may class worker evaluation and learning-outcome grading as high-risk [unverified, secondary: https://casrai.org/news/ai-act-high-risk-classification]. The report avoids individual evaluation by design.

---

## 6. Business model

### 6.1 Offers

| Offer | Stage | Price |
| :- | :- | :- |
| Firsthand (engine, moves, drills, map, every adapter, the guide) | v1, v2 | Free, open source |
| Firsthand Sync (relay, phone push, device link without the computer awake, cloud sessions without the carry branch) | v2 | Needs to be measured by a price test |
| Firsthand Team (sealed guide items through the relay, team report, SSO, SCIM, region-pinned or self-hosted relay) | Later | Needs to be measured |
| Firsthand Education (course catalogs, opt-in class reports, proctored live checks) | Later | Needs to be measured |

### 6.2 Why Team is the planned revenue line

- Individual willingness to pay is low for this category: free learning modes set the expectation at zero (research/users-market.md section 3.1).
- Team budgets exist for developer learning and review tools (Pluralsight and CodeRabbit price ranges, [unverified] in research/users-market.md).
- The guide spreads inside a company by itself: once committed, every engineer who opens the repo with any agent can use it.

### 6.3 Tests before team-plane code

- Ten manager interviews on the onboarding and coverage problem, and on whether an aggregate-only report is worth paying for (the teams concept's own assumption 2).
- A "talk to us about teams" button on https://0xfauzi.github.io/explain-pr/, counting clicks against visits (E9). The founder sets the pass threshold before it runs.

### 6.4 Ruled out

Selling records, ads, hiring use, paid streak repair, any paid pressure mechanic.

---

## 7. Distribution

| Channel | Role | Status |
| :- | :- | :- |
| Claude Code plugin directory | Main door for Claude Code users | Review rules [unverified]; VibeWise is listed there [verified: research/users-market.md] |
| Codex plugin marketplace, Cursor plugins, Gemini extensions, Kiro, Amp, OpenCode listings | One per adapter | [unverified] per directory |
| skills.sh, MCP registry | Skill and MCP discovery | [unverified] |
| npm, PyPI, Homebrew | `npx` / `uvx` / `brew` install | Names [unverified] until E0 |
| GitHub | README, the conformance table, the spec | VibeWise's growth came through GitHub [verified: star counts in research/users-market.md] |
| The site | The five-minute promise, the claims ladder, the team button | Existing at https://0xfauzi.github.io/explain-pr/ |

Launch screenshot: the first-session Trace drill in a terminal, with its verdict and the resume cue. It is real, on the user's own code, and checkable.
