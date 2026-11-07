# Spec: traceability

Every must-fix item from the five judges and every item from the three red-team reviews, and where `../PRODUCT.md` (P) or a spec file handles it. Items not fixed as asked say why. Red-team reviews are in `../redteam/`.

---

## Part A. Red-team reviews

### A.1 Privacy and security (`../redteam/privacy-security.md`)

| # | Sev. | Item | Where | Status |
| :- | :- | :- | :- | :- |
| 1 | Critical | Work-install promise is false | P 5.1, 6.9; `security.md` 5; `experience.md` 2.1; `architecture.md` 2.1 | Fixed: accurate copy; pad by default on work installs; encryption at rest; relay requirement removed; `firsthand verify`. Limit stated: a device owner can read anything (P 15) |
| 2 | Critical | Untrusted code runs with full privileges | P 6.10; `security.md` 2; `learning.md` 3.1, 3.3, 9.3 | Fixed for Checkup and Replay (container, no network, pinned, deps resolved in advance). Trace runs without a container on the user's own committed code, with stripped config (P 15) |
| 3 | Critical | Installer multiplies supply-chain risk | P 5.1, 6.10; `security.md` 3; `surfaces.md` 4, 9 | Fixed: names reserved in v0; pinned absolute paths; signed releases with provenance; explicit upgrade with diff; byte-exact backups; hooks never return permission decisions, tested |
| 4 | Critical | Unseen bank not sealed from the agent | P 6.4; `security.md` 4; `learning.md` 9; `architecture.md` 2.3 | Fixed: spec admits local encryption gives no protection; parameterised per-user families labelled not proctored; study pool never ships; Checkup tests on a server; typed provenance needs an engine-opened terminal with no agent parent; keys release only on typed locks. Server for every item not adopted (P 15) |
| 5 | Major | Prompt injection through repo content | P 3 (16), 6.10; `security.md` 7; `teams.md` 2.2 | Fixed: quoted and attributed; commands and URLs stripped; guides only in trusted repos; tools narrow only; widening confirmed in the pad |
| 6 | Major | "Nothing leaves the machine" is false | P 3 (17), 6.5, 6.9; `security.md` 6; `architecture.md` 5 | Fixed: accurate copy; named receiver per grader; `grader = local-only`, default on work installs |
| 7 | Major | Shared repos learn what a person is new to | P 4.3, 7; `security.md` 8; `teams.md` 3; `learning.md` 2.3 | Fixed: neutral `TODO:` marker; handback at commit; nothing in PR bodies; neutral CI text; no carry in repos the user does not own; neutral branch names |
| 8 | Major | Secrets and keys can land in the record | P 6.2; `security.md` 9; `architecture.md` 2, 3; `teams.md` 2.3 | Fixed: scan every free-text field; private keys outside the record with a commit guard; postmortem scan with author-approved redactions |
| 9 | Major | Team plane surveillance paths | P 7; `teams.md` 4, 5.3; `security.md` 11 | Fixed: fixed groups; suppression on small changes; no opted-in count; fixed outcome list; admin defaults capped at Standard with no reminder; relay requirement removed; proof packs stamped; legal review |
| 10 | Major | Carry import trusts anyone with push | P 6.7; `architecture.md` 8; `security.md` 10 | Fixed: local engine creates the branch; allowlist; strict validation; unauthenticated label, capped at Met; delete only own branches; deletion-is-not-erasure disclosed. Moved to v1.1 |
| 11 | Major | Existing misses are in project history | P 8, 10, 15; `security.md` 13; `architecture.md` 11 | Fixed in design: disclosure and history rewrite at migration. The skill change is the first v0 task, not done in this revision (P 15) |
| 12 | Minor | Hardening gaps | `security.md` 12; `architecture.md` 2, 9 | Fixed: keyed hash; forget expires reflog and prunes, warns on remotes; payloads and logs never stored; 0700 scratch; device link on one interface with authenticated pairing |

### A.2 Market (`../redteam/market.md`)

| # | Sev. | Item | Where | Status |
| :- | :- | :- | :- | :- |
| 1 | Critical | Nothing brings users back | P 4.5, 4.12; `experience.md` 3.10, 3.11; `measurement.md` E13 | Fixed: weekly line; reminder question with nothing pre-selected; ignored-reminder check-in; Checkup pull; v1 gated on cold 30-day return |
| 2 | Critical | A vendor can ship most of this | P 1, 2.3, 8; `teams.md` 7.2; `measurement.md` E16 | Fixed: the Checkup and bank lead; bank funded in v0; Checkup demand tested before the engine |
| 3 | Critical | Coding moves to background agents | P 4.2; `learning.md` 2.5; `surfaces.md` 1 (O11) | Fixed: Review first at PR time, keyed by tests, CI and later fixes |
| 4 | Critical | Team plan has nothing to buy | P 7; `teams.md` 4, 5.1; `measurement.md` E9 | Partly: onboarding outcome from company git; E9 in v0 with instructors added. Admin active count not adopted, conflicts with privacy 9 (P 15) |
| 5 | Major | Everything is copyable | P 2.3; `teams.md` 7.2 | Fixed: scarce assets named; separate content licence; launch only once the bank and Checkup service exist |
| 6 | Major | Large build, no funding line | P 8, 13; `teams.md` 7.3; `surfaces.md` 8, 9 | Partly: options and cost controls stated; the choice is a founder decision before v1 (P 15) |
| 7 | Major | Target users do not feel the need | P 2.1, 2.2; `measurement.md` E17, E9 | Fixed: measurement-first touch; framing A/B; buyers (instructors, managers) tested in v0 |
| 8 | Major | Model grading spends the plan | P 6.5; `architecture.md` 5, 5.1; `learning.md` 6 | Fixed: v1 moves levels only on executable grades and people; token cost of the instruction block shown at install |
| 9 | Major | Install edits every agent | P 5.1; `surfaces.md` 4; `security.md` 3.2 | Fixed: launched-from agent only; one yes per further agent; published file lists |
| 10 | Major | No growth loop | P 8; `learning.md` 9.3; `architecture.md` 10 | Fixed: signed Checkup result a third party can verify, stating what it does not show |
| 11 | Major | Nothing to say at launch | P 1, 9.5; `measurement.md` 5; `teams.md` 8 | Fixed: honesty claim; cohort data with sample size allowed |
| 12 | Minor | Name crowding | P 1; `measurement.md` E0 | Fixed: findability check in E0 |
| 13 | Minor | Vendor `TODO(human)` format may change | P 5.4; `surfaces.md` 3 | Fixed: own adapter row, Floor, untested |

### A.3 Efficacy (`../redteam/efficacy.md`)

| # | Sev. | Item | Where | Status |
| :- | :- | :- | :- | :- |
| 1 | Critical | Study measures practised items; two primary outcomes | P 9.1, 9.4; `measurement.md` 1, 2.3, 4; `learning.md` 9.2 | Fixed: study-only pool never ships; control gets format practice; one primary, G1-S, everywhere |
| 2 | Critical | A level moves on one answer | P 4.1, 4.9; `learning.md` 5 | Fixed: two right on different items; one step down per miss; guess cannot raise; "don't know" counts as not recalled; format tagged; headline retitled |
| 3 | Critical | Grader gate near noise, wrong grader | P 6.5; `learning.md` 6; `measurement.md` E5 | Fixed: absolute floor; per grader model and version with a shipped calibration set; leniency check; audit sampling of undisputed grades |
| 4 | Critical | No learning test before the engine | P 10, 11; `measurement.md` E1, E14 | Fixed: E14 lab check gates v1; ceiling guard on E1 |
| 5 | Major | Check key wrong by construction | P 4.6; `learning.md` 3.2; `measurement.md` E15 | Fixed: unconfirmed findings with a test offer; only test-confirmed defects move levels; label audit first |
| 6 | Major | Call it leaks the answer | P 4.2; `learning.md` 2.2 | Fixed differently: Call it never moves a level; visibility recorded; Replay carries diagnosis (P 15) |
| 7 | Major | Your line is fill-in-the-blank | P 4.3; `learning.md` 2.3 | Fixed: write first; read-first question and split rate; `line.survived` dropped; delayed hidden-test review is the evidence |
| 8 | Major | Cold start silences gaps | P 4.7; `learning.md` 11; `architecture.md` 7; `measurement.md` E11 | Fixed: inference lowers frequency only; two probes to silence; re-checks; E11 on juniors with trailer coverage |
| 9 | Major | Review cap cannot keep up | P 4.5, 4.11; `learning.md` 5.3, 7.3; `experience.md` 5 | Fixed: evidence age; "not checked lately"; priority and disclosure; N of M; new-idea entry control |
| 10 | Major | Unseen gap uninterpretable | P 6.4; `learning.md` 9.1 | Fixed: "not yet calibrated" until equated; retired after use; coverage listed |
| 11 | Major | Model certifies its own items | P 6.3; `learning.md` 4; `architecture.md` 4 | Fixed: engine computes distance; second blind key check; bad-key refund |
| 12 | Major | Explain back rewards paraphrase | P 6.5; `learning.md` 2.4 | Fixed: rubric author never reads the agent's explanation; mechanism and "what changes if" points; delayed items new instance |
| 13 | Major | On-device experiments are noise | P 9.3, 9.5; `measurement.md` 3.2, 5 | Fixed: no per-user effect below minimum; pool first; rung removed. Pooling depends on opt-in sharing (P 15) |
| 14 | Major | Checkup read as a trend | P 9.2; `learning.md` 9.3 | Fixed: piloted tasks with stored difficulty; results against difficulty; no trend below a minimum |
| 15 | Major | Levels depend on surface | P 5.4, 5.6; `learning.md` 5.4; `surfaces.md` 1, 3 | Fixed: the pad gives every terminal surface typed answers; what counts is shown per surface at install, on the map and at session start |
| 16 | Minor | Seen looks like progress | P 4.9; `experience.md` 5 | Fixed: Met, listed apart; best level only in `map all` |
| 17 | Minor | First drill contradicts rules | P 2.2; `learning.md` 9.4 | Fixed: demo and sampler record Met; promise reworded |
| 18 | Minor | User can curate the record | P 6.2; `experience.md` 6 | Fixed: forget removes whole ideas; proof pack header states attempt counts |
| 19 | Minor | Calibration mixes predictions | P 4.9; `learning.md` 1; `measurement.md` 2.2 | Fixed: delayed items only; prediction accuracy separate |

### A.4 Conflicts between red-team items

| Conflict | Resolution |
| :- | :- |
| Market 4 (admin active count) against privacy 9 (no opted-in count) | Privacy wins. Buyer signal comes from company git instead |
| Market 1 (bring users back) against principle 7 (no pressure) | A weekly factual line about the user's own work, and the Checkup; no streaks or counts of missed days |
| Market 3 (Review first on live PRs) against privacy 7 (teammates learn what a person is new to) | Findings are private; posting is the user's own plain comment |
| Privacy 2 (containers everywhere) against the first-session drill | Containers for code the user did not write; Trace on own committed code without one |
| Efficacy 2 (two answers per step) against efficacy 9 (too few slots) | Entry control on new ideas and a priority order, so slots go to ideas near a level change |

---

## Part B. Judge must-fix items

These were traced before the red-team revision. Where the revision changed the fix, the status says so.

### Learning scientist

| # | Must fix | Where | Status |
| :- | :- | :- | :- |
| 1 | Primary outcome is transfer; preregister G2 to G4 | P 9.1; `measurement.md` 2.3 | Fixed. Primary is now G1-S, a held-out transfer battery; G2 to G4 secondary |
| 2 | Item families, distance; same-function caps at Recalled | P 4.9; `learning.md` 4 | Fixed. Distance now computed by the engine |
| 3 | Independent audit bank | P 6.4; `learning.md` 9 | Fixed, revised: parameterised families in product, study pool never ships |
| 4 | Gate diagnosis on debugging level and delegation | P 4.4; `learning.md` 2.2 | Fixed |
| 5 | Remove acceleration-mode silence | `learning.md` 2.6 | Fixed |
| 6 | Grade diagnosis on process | `learning.md` 2.2, 3.3 | Fixed in Replay. Call it is practice only |
| 7 | State and measure dose; drills not interruptions | P 4.11; `learning.md` 8 | Fixed |
| 8 | Cluster-level within-person design, power | P 9.3; `measurement.md` 3 | Fixed |
| 9 | Your-line marker free of answers; signals | P 4.3; `learning.md` 2.3 | Fixed. `line.survived` dropped; delayed hidden-test review added |
| 10 | Log field evidence | P 4.10; `learning.md` 10 | Fixed, labelled self-reported |
| 11 | Teams: no skill claims before power check | P 7; `teams.md` 5 | Fixed |

### Product strategist

| # | Must fix | Where | Status |
| :- | :- | :- | :- |
| 1 | Cut v1 | P 10 | Fixed. Model-graded level moves and the carry branch also left v1 |
| 2 | Parity of outcome as a tested promise | P 5.4; `surfaces.md` 1, 8 | Fixed, with O10 and O11 added |
| 3 | Measure replay yield first | E2 | Fixed, now in containers |
| 4 | Activation, retention, cohort | P 2.2, 9.1 | Fixed; cold cohort added |
| 5 | Self-attested; honour system cannot reach the top | P 4.9 | Fixed |
| 6 | Cost of headless grading | P 6.5 | Fixed |
| 7 | No Prio3/DAP | P 6.9 | Fixed |
| 8 | Team as revenue line; tests first | P 8; `teams.md` 7 | Revised: courses and Team both tested in v0; founder chooses |
| 9 | One-sentence differentiation | P 1 | Revised to the measurement promise |
| 10 | Name checks | E0 | Fixed, findability added |
| 11 | Migration | `architecture.md` 11 | Fixed, with history disclosure |
| 12 | First map view readable in seconds | `experience.md` 5 | Fixed |

### Staff engineer

| # | Must fix | Where | Status |
| :- | :- | :- | :- |
| 1 | Answer provenance; relayed capped | `architecture.md` 2.3; `learning.md` 5.4 | Fixed: relayed counts as Met; typed needs the pad |
| 2 | No plaintext branch inbox | P 6.7; `architecture.md` 8 | Fixed, redesigned, v1.1 |
| 3 | Your-line attribution per tier | `surfaces.md` 5 | Fixed |
| 4 | Pluggable grader with matrix | `architecture.md` 5 | Fixed, with named recipients |
| 5 | Conformance pass rates | `surfaces.md` 8 | Fixed, run in CI |
| 6 | Catalog drift | P 6.6 | Fixed |
| 7 | Pressure on hookless surfaces | `surfaces.md` 6 | Fixed |
| 8 | Phone path | P 6.8 | Fixed |
| 9 | Calendar reminder content-less | `architecture.md` 9 | Fixed |
| 10 | Cut v1 | P 10 | Fixed |
| 11 | Sealing strength shown | P 6.3 | Fixed |
| 12 | Per-device signing key | `architecture.md` 3 | Fixed, private key outside the record |

### Designer

| # | Must fix | Where | Status |
| :- | :- | :- | :- |
| 1 | One vocabulary, at most five plain words | P 4.9 | Fixed: Not yet, Recalled, Applied, Held, plus Met as a separate list |
| 2 | Fade the header | `experience.md` 3.2 | Fixed |
| 3 | No verdict on predictions | `experience.md` 3.3 | Fixed |
| 4 | Session start never a gate | `experience.md` 3.9 | Fixed |
| 5 | Map for terminal and screen reader | `experience.md` 5 | Fixed |
| 6 | No silent cloud loss, one confirmation | P 6.7 | Fixed: import line in v1, carry in v1.1 |
| 7 | Easy way out of your line | P 4.3 | Fixed |
| 8 | Your-line continuity | P 4.3 | Fixed |
| 9 | Cap setup prompts | P 4.5 | Fixed |
| 10 | Waiting and failure states | `experience.md` 4 | Fixed |
| 11 | Conservative silence | P 6.6 | Fixed |
| 12 | Accessibility gate | `experience.md` 7 | Fixed, pad included |
| 13 | Test the name | E0 | Fixed |
| 14 | Honest surface count | P 3 (11) | Revised: v1 adds the pad, with the job it does named |

### Target users

| # | Must fix | Where | Status |
| :- | :- | :- | :- |
| 1 | Cold start for seniors | P 4.7; `learning.md` 11 | Revised: inference lowers frequency only; two quick probes silence a cluster. Seniors are asked a little more in week one than before, to avoid hiding juniors' gaps |
| 2 | Hard daily cap | P 4.5 | Fixed |
| 3 | Explicit quiet | `experience.md` 3.15 | Fixed |
| 4 | Call it non-blocking | `learning.md` 2.2 | Fixed |
| 5 | Never leave build or CI red | P 4.3 | Fixed |
| 6 | User-scope install | `surfaces.md` 4 | Fixed, one agent at a time |
| 7 | No plaintext branch inbox | P 6.7 | Fixed |
| 8 | Cost visible, off critical path | P 6.5 | Fixed |
| 9 | Silent rather than guess | P 6.6 | Fixed |
| 10 | No seeded bugs in own code | `learning.md` 3.2 | Fixed |
| 11 | Tell each user what their surface can do | `experience.md` 2 | Fixed, including what counts |
| 12 | Cut v1 | P 10 | Fixed |
| 13 | Never show an employer the junior's record; say so | P 5.1, 7; `teams.md` 4 | Revised: the employer still never sees the record, levels or skips through the product. The claim that it cannot see whether you use it was false and is replaced by accurate copy |
| 14 | Why-now and skip on every question | P 4.1 | Fixed |
