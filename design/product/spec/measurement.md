# Spec: measuring that it works

Part of `../PRODUCT.md` (sections 9 and 11). Built on `../research/evidence.md` Parts G to K.

---

## 1. Instruments

| Instrument | Written by | Seen by the teaching agent | Used for |
| :- | :- | :- | :- |
| Practice items (reviews, drills, moves) | The engine, keys in a separate context | Yes | Teaching and tuning |
| Unseen questions | Contracted engineers | No | Leading Goodhart alarm; G1 battery in the study |
| Checkup | Contracted engineers | No | G2, G3, G4 for users; lagging, user-held |
| Field evidence | The user | No | Within-person real-work signal (G5) |
| Proctored live check | Fresh unseen items, a person present | No | The only evidence for third parties (later) |

Rule: the teaching instrument and the claim instrument are separate (evidence G, structural rule 1). Every view that shows a practised score shows the unseen score next to it (rule 2).

---

## 2. Metrics

### 2.1 Product metrics (tune the product)

| Metric | Definition |
| :- | :- |
| Activation | First drill or first your-line attempted in the first session |
| Answer rate | Offered moments answered, not skipped or expired |
| Review completion | Due reviews done the day they are due |
| Return | Any learning event on day 14 and day 30 after install |
| Dose | Weekly reps by kind: retrieval, generation, diagnosis, check; share unaided |

### 2.2 Leading learning indicators (tune, never market as "better engineer")

From evidence H.1: generation before reveal; delayed unaided recall at first review; retention curve per interval; calibration (Brier score and sure-miss correction rate on delayed items); your-line first-try rate; hint depth; the unseen-question gap.

### 2.3 Lagging outcomes (claims)

From evidence H.2. Primary: **G2**, the fresh-codebase task. Also G1 (held-out battery), G3 (seeded-bug localisation in an unfamiliar repo), G4 (defect finding in agent diffs including clean ones). G5 real-work signals are within-person only.

These are preregistered as the study outcomes before any study starts.

### 2.4 Guard metrics

Task time with the product on versus off (non-inferiority margin set in advance); skip and "just build" rate and its trend; reminder dismissals; model cost per user per week; measurement invariance across surfaces (the same item type should score the same for the same person on CLI, IDE and phone).

### 2.5 Where metrics come from without a server

- On device: `firsthand stats` computes all of the above for the user.
- Design-partner cohort: users paste `firsthand stats --share` output, which holds counts and rates only, no answers, no code, no idea names unless they choose.
- Telemetry stays off by default. No central analytics in v1.

---

## 3. Within-person experiments

### 3.1 Design

- Unit: an idea cluster from the catalog (an idea plus its aliases and listed confusions). Related ideas share an arm, so they do not contaminate each other.
- Assignment: a seeded coin per new cluster, recorded as a sealed `experiment.assigned` event, never shown on cards.
- Before assignment, the engine checks that sealed delayed items of equal quality exist for the cluster in both arms (from the unseen bank). Clusters without them are not enrolled.
- Outcome: unseen questions on that cluster at a fixed delay (21 days to start; design default).
- Results on the device: per user, per experiment, with counts. Below the minimum: "too few ideas to tell".

### 3.2 First experiments

| Experiment | Arms | Outcome |
| :- | :- | :- |
| Explain back after the build | On, off | Unseen-question correct at 21 days |
| Your line | Offered, not offered | Unseen-question correct; task time guard |
| Call it | Offered, not offered | Unseen C2 items; Checkup G3 |
| Topic name on transfer items | Shown, hidden | Unseen transfer items |

Between-person questions (the daily cap, reminder timing, onboarding) need the opt-in cohort, because they cannot be split by idea.

### 3.3 Power

Effect sizes for this product are unknown, so no sample size is claimed. Lehr's rule gives about 16 divided by the squared standardised effect per arm for a two-arm test at 80% power and two-sided alpha 0.05 (https://www.columbia.edu/~cjd11/charles_dimaggio/DIRE/styled-4/code-12/, via evidence J.3). For illustration only: d = 0.5 gives about 64 per arm. Within-person designs need fewer people, by an amount that depends on the correlation between a person's clusters. E7 estimates that correlation and the delayed-test completion rate. The minimum clusters per person and the cohort size are then computed and written down before any claim. Until then: needs to be measured.

---

## 4. The study before any efficacy claim

From evidence K.1:

- Preregistered, randomised, two arms: the agent with Firsthand on at defaults, and the same agent with it off.
- Participants: working developers and advanced students who already use an agent, across at least two agents and two surfaces. Pretest excludes people who know the target library.
- Period: several building sessions across weeks in an unfamiliar realistic codebase with a library new to them. Length set from a pilot.
- Primary: G1 at a fixed delay (two weeks or more after the last session). Secondary: G2, G3, G4, calibration. Guard: build task time, non-inferiority margin set in advance.
- Grading: executable where possible; open answers by two humans blind to arm, with the model grader run in parallel to measure its agreement on study data.
- Analysis: intention to treat; effect sizes with intervals; report who missed the delayed test and whether they differ by arm.
- Independence: ideally run or audited by researchers who do not work on the product.

---

## 5. Claims ladder

| Evidence | Allowed claim |
| :- | :- |
| Research only | "Designed around research on how people learn with AI." |
| Leading indicators | "Users recall X at Y days", with definition and the unseen gap shown |
| On-device experiments | "Shows you which moves help you, measured on you." |
| Study positive on G1 | The specific result with effect size and link |
| Independent replication with G2 to G4 | "People who use it become better engineers", with scope |

Neither the site nor the map may present delayed review accuracy or the unseen gap as "better engineer". The site is checked against this ladder in v0 and before each release.

---

## 6. Experiment protocols

Thresholds below are decisions, not findings. The founder fixes them before a run, never after.

### E0. Name

Checks: trademark search in software classes for Firsthand and Ownline; npm, PyPI, Homebrew, plugin directories, domains; search for existing products using the name (a careers product named Firsthand may exist [unverified]). Interviews: 8 developers, including at least 2 disabled developers, asked what the name suggests. Pass: no blocking conflict, packages free, at most 1 of 8 reads it negatively.

### E1. Answer rate and dose

20 design partners, 3 weeks, current skill with the v1 budget rules added by script. Weekly pasted stats. Felt-cost question at session end: "How much did the questions slow you today? none, a little, a lot." Pass: at least half of offered moments answered and at least half of due reviews done in week 3. Report dose per rep kind.

### E2. Replay yield

Run the miner as a script over the founder's repos and 30 public repos in at least 4 languages. Report per language: candidates per 100 commits, reproducible drills per 100 commits, median setup time, share needing services, databases or secrets, share flaky (passes and fails on reruns). Pass per language: at least 2 reproducible per 100 commits, median setup under 2 minutes, under half needing external services. Fallback if no language passes: Trace and Check carry the wedge, Replay waits.

### E3. Tag agreement

30 real diffs, three agents (Claude Code, Codex, Cursor), each picks tags from the same `candidates` list. Pass: Fleiss kappa at least 0.6. Fail: silence stays per project, and cross-agent silence uses only probed and cold-start ideas.

### E4. Moment choice

Wizard of Oz with 5 users: a person watching the transcript picks moments; the engine's rules run on the same transcripts; compare. Felt-cost question at session end. Pass: engine and person agree on at least 70% of moments; median felt cost "a little" or less. Output: the default moment cap.

### E5. Grader agreement

Per task type (explain back, Call it process point, Compare, Check severity): 200 answers, two trained human graders, the model grader. Pass: model-human Cohen's kappa within 0.1 of human-human kappa, and no leniency bias above a margin set in advance. Fail: that task type cannot move levels. Results published.

### E6. Weak-tier conformance

Conformance script on Copilot in JetBrains, Gemini CLI, Aider and Copilot cloud agent, 10 runs each. Fill every "?" in research/surfaces.md 8.7. Pass per outcome: 8 of 10 runs, else listed as a known gap.

### E7. Within-person pilot

10 users, 3 weeks, cluster-level assignment for explain back, unseen questions at day 21. Pass: at least 80% of delayed items taken. Output: within-person correlation and completion rate for the power calculation. No effect claim.

### E8. Grading cost and availability

On each v1 agent: run 50 grading calls through each available provider. Report tokens or quota used, wall time, rate limits hit, and whether terms allow it [unverified until read]. Pass: every provider marked available or not, with a weekly cost estimate shown to users.

### E9. Team pay test

10 manager interviews; a "talk to us" button on the site. Founder sets the click threshold before it runs. No team-plane code before it passes.

### E10. Cloud carry acceptance

10 users of cloud agents see the carry prompt once. Pass: at least 7 of 10 choose carry or their own remote. Fail: the import line becomes the default.

### E11. Cold start

10 seniors add repos; for each inferred-known idea, ask one probe. Pass: at least 80% pass the probe. Fail: inference only lowers the moment cap, it does not silence.

### E12. Phone pairing

Prototype the device link on iOS and Android, including secure context for the web app. Pass: pairing with at most one confirmation tap on both. Device link ships only then.
