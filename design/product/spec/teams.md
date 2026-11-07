# Spec: teams, courses, business model and distribution

Part of `../PRODUCT.md` (sections 7 and 8). Draws on `../concepts/teams.md`. Nothing in this file is v1 except the shared-repo rules in section 3, which protect individuals. Buyer tests (E9) run in v0. Red-team items are cited as "RT market n" and so on.

---

## 1. Who and why

- Team users: engineers who build with agents, and the seniors and area owners who mentor them.
- Team buyer: engineering managers and developer experience leads. 38% of leaders say AI cut the mentoring juniors get (https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles).
- Course buyer: course leads and instructors who let students use agents and need an assessment that survives them (`../PRODUCT.md` 2.1).
- What buyers already pay for: onboarding, coverage of areas, assessment. Not "skill scores" of named people.

---

## 2. The codebase guide (v2)

### 2.1 Files

```
.firsthand/guide/
  guide.toml            areas, owners willing to mentor, settings
  ideas/<idea>.md       one file per codebase idea
  lines.toml            nominated "lines worth writing by hand once"
  drills/<id>.md        rehearsals drafted from postmortems; keys not here
```

Each idea file: the idea in one sentence, where it lives, why it matters here, how it breaks, an optional owner "how I debug this" note, who is willing to help. No personal data. Committed only if the team chooses, reviewed in PRs like code.

### 2.2 Trust rules (RT privacy 5)

- A guide is read only in repos the user marks as theirs or trusted, once per repo, confirmed in the pad.
- Guide text is shown quoted and attributed: `From this repo, written by contributors:`.
- Owner notes and drills have commands, URLs and code fences removed before display.
- Guide content can never change a setting, run a command, or widen anything.

### 2.3 Writing it

- `firsthand guide draft` proposes ideas with paths as a PR. Seniors edit and delete.
- `firsthand drill from <postmortem>` drafts a rehearsal with the real resolution sealed. **Logs and text are scanned for secrets and personal data** (tokens, emails, names from the git author list, IP addresses). The author sees each redaction and approves before save (RT privacy 8).
- `firsthand handover <area>` drafts entries when someone rotates off.
- `firsthand guide check` lists ideas whose paths no longer exist.

### 2.4 How the guide feeds the loop

- Guide ideas are private catalog entries in the team's namespace, shown on the map under "This codebase".
- Owner notes appear only after the learner's own attempt (L18).
- Nominated lines become your-line offers in that area when the idea is new to the learner.
- Guide items ship without keys. The engine writes keys in a separate context.

---

## 3. Shared-repo rules (v1)

RT privacy 7.

- No readable learning data in any branch.
- Your-line markers in repos the user does not own are plain `TODO:` comments, handed back at commit by default, so they are not committed.
- No markers, product name or learning text in PR bodies.
- The optional merge check (`firsthand ci`) message is neutral: `Open TODO in retry.py:42.` It fails only on a TODO the engine recorded and nobody resolved. A hotfix pattern skips it.
- No carry branches in repos the user does not own. The CI check also fails any PR containing a carry file.
- Who wrote a line is never written to commits, trailers or PRs.
- Review-first findings are private.
- Optional PR walkthrough: the author writes a walkthrough for reviewers. The engine grades it privately. Reviewers see the text only.

---

## 4. The admin contract

| Control | Allowed |
| :- | :- |
| Deploy engine and adapters (`firsthand team install`) | Yes. Turns nothing on. Marks the install as a work install, so work defaults apply |
| Set defaults for dial (up to Standard) and review cap (up to 3) | Yes, as defaults the engineer can change |
| Set a reminder default | No (RT privacy 9) |
| Require a relay, team or self-hosted | No. Removed (RT privacy 1) |
| Turn excerpt storage off for a project | Yes |
| Turn telemetry off for everyone | Yes |
| Turn telemetry, sharing or reports on for anyone | No |
| Raise the review cap above 3 | No |
| See who has the tool on, who uses it, or how many opted in | No |
| Define report outcomes | No. Outcomes come from a fixed list (section 5) |
| Read or export any record | No. No key exists |
| Request proof packs through the product | No. Proof packs are stamped "not a performance measure" |
| Lower the group floor or change group definitions mid-period | No |

The engineer sees, at a work install, the accurate copy in `experience.md` section 2.1.

**Not adopted: an admin active count** (RT market 4, second fix). An aggregate install or active count above the floor would let an admin infer who opted in by comparing with seat counts over time (RT privacy 9), and would contradict the work-install copy. The buyer's renewal signal is the onboarding outcome in section 5.1 instead. `../PRODUCT.md` section 15 records this.

---

## 5. What a team buyer can see

### 5.1 The onboarding outcome (no Firsthand data)

RT market 4, first fix.

- Time from a new hire's start date to their first merged PR in an area, for areas with a guide against areas without one.
- Computed from the company's own git history and HR start dates the company already holds. It reads no record and no Firsthand event.
- Reported for cohorts of at least the group floor, by area.
- Whether a guide moves it needs to be measured. It is never presented as a skill measure.

### 5.2 Guide health

Guide coverage (ideas per area, stale paths), from the guide files only.

### 5.3 The team report (later, paid)

- Each engineer can opt in to share counts their engine computes locally: guide ideas reached Recalled or better, by idea.
- **Group rules** (RT privacy 9):
  - Groups are defined once per period from a fixed list (whole team, or areas with at least the floor of engineers), and cannot change mid-period.
  - Counts appear only for groups of at least 8 opted-in people (design default; Viva Insights' floor cannot go below five [verified: https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings]).
  - A report is suppressed if the opted-in set changed by fewer people than the floor since the last report, so differencing cannot isolate one person.
  - Overlapping groups are not reported in the same period.
  - The opted-in count is never shown.
- Outcomes come from a fixed list. Admins cannot define outcomes that one person can reach.
- No Prio3 or DAP [verified: https://datatracker.ietf.org/doc/draft-ietf-ppm-dap/].
- Never sold as a skill measure until a power check shows it can detect a change at the floor.
- **Legal review of the consent basis before launch.** Employee consent is rarely freely given [verified: https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_202005_consent_en.pdf]. The EU AI Act may class worker evaluation as high-risk [unverified, secondary: https://casrai.org/news/ai-act-high-risk-classification].

---

## 6. Courses (v2 pilot)

- Course Checkups: the instructor picks Checkup tasks for a cohort. Students run them as usual. Each student sees their own result. The instructor sees the cohort's results against task difficulty, above a group floor, with no individual results unless the course runs proctored live checks.
- Proctored live checks: fresh unseen items with a person present. The only results the product labels "proctored".
- Course catalogs: the course's ideas in its own namespace.
- Legal review before launch, as for Team.
- E9 interviews instructors in v0.

---

## 7. Business model

### 7.1 Offers

| Offer | Stage | Price |
| :- | :- | :- |
| Firsthand loop (engine, moves, drills, map, adapters) | v1 | Free, open source |
| Personal Checkup and in-product unseen families | v1 | Free to individuals; funded per section 7.3 |
| Courses (cohort Checkups, proctored live checks) | v2 pilot | Needs to be measured |
| Team (guide tools, onboarding outcome, SSO, report later) | Later | Needs to be measured |
| Sync (relay, push, device link) | v2 | Needs to be measured |

### 7.2 Scarce assets (RT market 5)

The bank of parameterised families, the Checkup tasks with pilot data, the Checkup service, the study-only pool, the maintained conformance table, and the brand. The bank and Checkup tasks ship under a separate content licence, not the engine's open-source licence (founder decision). No public launch until the first bank and the Checkup service are live.

### 7.3 Funding (RT market 6)

- The build is large: by the estimates in `../PRODUCT.md` section 10, v0 to v2 is many engineer-months, with no revenue before courses or Team, plus surface rows that break when vendors change.
- A funding plan is chosen before v1 (founder decision). Options:
  - A research grant: the Checkup and the study pool are instruments for studying AI and skill.
  - A sponsor that is not an agent vendor.
  - A foundation home for the engine and record format.
  - A vendor partnership, with a published independence clause covering the Checkup and the study.
- Cost control: adapters generated from one manifest; conformance in CI through headless modes; v1 tests three agents only.

### 7.4 Ruled out

Selling records, ads, hiring use, paid streak repair, any paid pressure mechanic.

---

## 8. Distribution

| Channel | Role | Status |
| :- | :- | :- |
| Claude Code plugin directory | Main door for Claude Code users | Review rules [unverified]; VibeWise is listed there [verified: research/users-market.md] |
| Codex, Cursor, Gemini, Kiro, Amp, OpenCode listings | One per adapter | [unverified] per directory |
| skills.sh, MCP registry | Discovery | [unverified] |
| npm, PyPI, Homebrew | Install | Names reserved in v0; E0 confirms |
| GitHub | README, conformance table, spec | |
| The site | The measurement framing (if E17 favours it), the claims ladder, buyer buttons | https://0xfauzi.github.io/explain-pr/ |
| Signed Checkup results | Something a user can show (RT market 10) | v1 |

Launch screenshot: the sampler result in the pad, with its "not proctored" label, then a Checkup result against difficulty.

Launch claim: "It tells you when you got worse." Plus any cold-cohort numbers with their definition and sample size (RT market 11, `measurement.md` section 5).
