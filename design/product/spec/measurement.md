# Spec: measuring that it works

Part of `../PRODUCT.md` (sections 9 and 11). Built on `../research/evidence.md` Parts G to K, revised after `../redteam/efficacy.md` and `../redteam/market.md` (cited as "RT efficacy n", "RT market n").

---

## 1. Instruments

| Instrument | Written by | Seen by the teaching agent | Ships to users | Used for |
| :- | :- | :- | :- | :- |
| Practice items | The engine, keys in a separate context, key-checked | Yes | Yes | Teaching and tuning |
| In-product unseen families | Contracted engineers | No | Yes (generators) | The user's own Goodhart alarm, labelled not proctored |
| Checkup tasks | Contracted engineers, piloted | No | Served on request; hidden tests stay on the service | G2 to G4 for users |
| Study-only pool | Contracted engineers | No | **Never** | G1-S, the primary outcome |
| Field evidence | The user | No | n/a | Self-reported real-work signal (G5) |
| Proctored live check | Fresh items, a person present | No | n/a | The only evidence for third parties (later) |

Rules: the teaching instrument and the claim instrument are separate. **The claim instrument for public claims never ships** (RT efficacy 1).

---

## 2. Metrics

### 2.1 Product metrics

| Metric | Definition |
| :- | :- |
| Activation | Sampler or demo drill answered in the first session |
| Answer rate | Offered moments answered, not skipped or expired |
| Review completion | Due reviews done the day they are due |
| Return | Any learning event on day 14 and day 30 after install, **reported separately for cold-recruited users** (RT market 1) |
| Pad use | Share of answers typed in the pad |
| Dose | Weekly reps by kind; share that counted |

### 2.2 Leading learning indicators

Delayed recall at first counting review; retention per interval; calibration (Brier score and sure-miss correction rate) **on delayed items only**; prediction accuracy as its own line (RT efficacy 19); your-line hidden-test review pass rate, split by "read the test first"; the unseen gap, only once calibrated.

### 2.3 Lagging outcomes

**Primary: G1-S**, a held-out unaided battery from the study-only pool, made of transfer items (new instances, topic names hidden), at a fixed delay. This is the one primary outcome, named the same way in `../PRODUCT.md` 9.1 and 9.4 and here (RT efficacy 1).

Secondary: G2 (task in an unfamiliar repo), G3 (bug localisation), G4 (defect finding including clean diffs). G5 within-person only.

### 2.4 Guard metrics

Task time on versus off (non-inferiority margin set in advance); skip and "just build" rate; reminder dismissals; model cost per week; measurement invariance across channels; **delayed accuracy near ceiling** (a sign questions are too easy, RT efficacy 4).

### 2.5 Where metrics come from without a server

- On device: `firsthand stats`.
- Design partners and cold cohorts paste `firsthand stats --share`: counts and rates only.
- Telemetry stays off by default.

---

## 3. Within-person experiments

### 3.1 Design

- Unit: an idea cluster. Assignment: a seeded coin, sealed, never on cards.
- Enrolled only if equal-quality delayed items exist for both arms.
- Outcome: unseen family items on that cluster at a fixed delay (21 days to start; design default).

### 3.2 What the user sees

**No per-user effect is shown** until the minimum count from E7's power calculation is reached (RT efficacy 13). Below it: "too few ideas to tell". Each user has a handful of binary outcomes per arm, and the "off" arm still gets retrieval practice, so a per-user estimate will mostly be noise.

Results are **pooled across opted-in users first**, through pasted `stats --share` output, before any per-user display is turned on.

### 3.3 First experiments

| Experiment | Arms | Outcome |
| :- | :- | :- |
| Explain back after the build | On, off | Unseen items at 21 days |
| Your line | Offered, not offered | Unseen items; task time guard |
| Call it | Offered, not offered | Replay and Checkup bug results |
| Topic name on transfer items | Shown, hidden | Unseen transfer items |
| The weekly line | Shown, not shown (between-person, cohort) | 30-day return |

### 3.4 Power

Effect sizes are unknown, so no sample size is claimed. Lehr's rule gives about 16 divided by the squared standardised effect per arm (https://www.columbia.edu/~cjd11/charles_dimaggio/DIRE/styled-4/code-12/, via evidence J.3). For illustration only: d = 0.5 gives about 64 per arm. E7 estimates within-person correlation and completion. Until then: needs to be measured.

---

## 4. The study before any efficacy claim

- Preregistered, randomised, two arms: the agent with Firsthand on at defaults, and the same agent with it off.
- **The control arm gets the item format:** the same number of practice questions in the same format, on unrelated content, so format familiarity is equal across arms (RT efficacy 1).
- Neither arm has seen G1-S items: they come from the study-only pool.
- Participants: working developers and advanced students who use an agent, across at least two agents and two surfaces. Pretest excludes people who know the target library.
- Period: several building sessions across weeks in an unfamiliar codebase with a library new to them. Length set from a pilot.
- **Primary: G1-S** at a fixed delay (two weeks or more after the last session). Secondary: G2, G3, G4, calibration. Guard: task time.
- Grading: executable where possible; open answers by two humans blind to arm; the model grader in parallel to measure its agreement on study data.
- Analysis: intention to treat; effect sizes with intervals; report who missed the delayed test and whether they differ by arm.
- Independence: ideally run or audited by researchers who do not work on the product.

---

## 5. Claims ladder

| Evidence | Allowed claim |
| :- | :- |
| None | What it does, for example "It tells you when you got worse." "Designed around research on how people learn with AI." No efficacy claim |
| Design-partner or cold-cohort data | The number, its exact definition and its sample size, in the form "30-day return X%, n = N cold installs, recruited from Y" (RT market 11) |
| Leading indicators | "Users recall X at Y days", with definition, sample size and the unseen gap |
| The study, positive on G1-S | The specific result, effect size and link |
| Independent replication with G2 to G4 | "People who use it become better engineers," with scope |

The rung "Shows you which moves help you, measured on you" is removed (RT efficacy 13). The site and the map may not present delayed review accuracy or the unseen gap as "better engineer". The site is checked against this ladder in v0 and before each release.

---

## 6. Experiment protocols

Thresholds are decisions, not findings. The founder fixes them before a run, never after.

### E0. Name and findability

Trademark search in software classes for Firsthand and Ownline; npm, PyPI, Homebrew, plugin directories, domains; existing products using the name. **Findability:** search each name in the main plugin directories, npm and a web search, and record whether the product would come up first (RT market 12). Interviews: 8 developers, at least 2 disabled developers. Pass: no blocking conflict, packages free, findable, at most 1 of 8 reads it negatively.

### E1. Answer rate and dose

20 design partners, 3 weeks, current skill with the v1 budget rules added by script. Weekly pasted stats. Felt-cost question at session end. Pass: at least half of offered moments answered and half of due reviews done in week 3, **and** delayed accuracy per move is not near ceiling (ceiling level is a threshold, a decision). A rising answer rate with delayed accuracy at ceiling is a warning, not a pass (RT efficacy 4).

### E2. Replay yield

Run the miner over the founder's repos and 30 public repos in at least 4 languages, **inside containers with no network after install**. Report per language: candidates and reproducible drills per 100 commits, median setup time, share needing services, share flaky, share blocked by an advisory match. Pass per language: at least 2 reproducible per 100 commits, median setup under 2 minutes, under half needing external services.

### E3. Tag agreement

30 real diffs, three agents, tags from the same `candidates` list. Pass: Fleiss kappa at least 0.6.

### E4. Moment choice

Wizard of Oz with 5 users. Pass: engine and person agree on at least 70% of moments; median felt cost "a little" or less. Output: the default moment cap.

### E5. Grader agreement, per grader model and version

RT efficacy 3. Per task type (explain back, Call it process, Replay process, Compare, Check severity) and per grader model and version: 200 answers, two trained human graders, the grader.

Pass needs all of:
- Cohen's kappa against human consensus at or above an absolute floor (threshold, a decision; 0.6 proposed);
- within 0.1 of human-human kappa;
- mean leniency against humans within a set margin.

The 200 graded answers per task type become the shipped calibration set that each user's grader must pass before it can move levels (`learning.md` section 6). Results published per task type and grader version.

### E6. Weak-tier conformance

Conformance on Copilot in JetBrains, Gemini CLI, Aider and Copilot cloud agent, 10 runs each, including O10 through the pad. Pass per outcome: 8 of 10.

### E7. Within-person pilot

10 users, 3 weeks, cluster-level assignment for explain back, unseen items at day 21. Pass: at least 80% of delayed items taken. Output: correlation and completion for the power calculation. No effect claim.

### E8. Grading cost and availability

On each v1 agent: 50 grading calls per provider. Report tokens or quota, wall time, rate limits, and whether terms allow it [unverified until read]. Also measure the instruction block's token cost per session per agent (RT market 8).

### E9. Buyers

10 manager interviews and 10 instructor interviews (RT market 4 and 7), in v0. Buttons on the site for "teams" and "courses", counting clicks against visits. The founder sets thresholds before it runs. No team or course code before it passes.

### E10. Cloud carry acceptance

10 users of cloud agents see the redesigned carry prompt once, including the line about deletion. Pass: at least 7 of 10 choose carry or their own remote.

### E11. Cold start, juniors and seniors

RT efficacy 8. 10 seniors and 10 juniors add repos. For each inferred-known idea, two probes (direct, and a new instance with the topic hidden). Also measure, per tool used by the participants, the share of their agent-written commits that carry an agent trailer, from their own account of which commits were agent-written. Pass: at least 80% of inferred-known ideas pass both probes, in each group separately. Fail: inference stays frequency-only (which is already the default) and its weight is lowered.

### E12. Phone pairing

Prototype the device link on iOS and Android with authenticated pairing and secure context. Pass: one confirmation tap on both.

### E13. Cold return

RT market 1. Users recruited from a directory listing, not the founder's network, install the current skill with the v1 budget rules, the weekly line and the real reminder question. Measure 30-day return. Pass: above a threshold set by the founder before the run. The v1 build is gated on it.

### E14. A learning check

RT efficacy 4. A small lab study in the Shen and Tamkin setting (https://arxiv.org/html/2601.20245v2): one session building with a library new to the participant, skill on versus off, then a delayed quiz a week later on items neither arm practised. It will be underpowered. Its job is a go or no-go on direction, with the threshold fixed before the run. The v1 build is gated on it.

### E15. Check label audit

RT efficacy 5. Hand-check a sample of diffs labelled "defective" and "clean" by the miner. Report label accuracy for each. Pass: above a threshold. Check ships only then, and only test-confirmed defects move levels regardless.

### E16. Checkup demand

RT market 2. A concierge Checkup, run by a person, for cold-recruited users: a task in an unfamiliar repo, run in a container, graded by hidden tests. Measure who books a second Checkup a month later. Pass: above a threshold. The v1 build is gated on it.

### E17. Framing

RT market 7. A/B test on the site: "Can you still do this without your agent?" versus "Learn while you build". Measure install clicks and sampler completions among visitors who say they are in their first years. The winning framing leads the site.
