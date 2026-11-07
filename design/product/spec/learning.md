# Spec: the learning loop

Part of `../PRODUCT.md` (section 4). Evidence codes L1 to L19 are the design rules in `../research/learning-science.md` Part A.3. Task and construct codes (C1 to C6, G1 to G5) are from `../research/evidence.md`. Red-team items are cited as "RT efficacy n", "RT market n" or "RT privacy n" (reviews in `../redteam/`).

---

## 1. Constructs

The product measures six constructs separately and never combines them (evidence B.1).

| Code | Construct | Practice | Level-bearing evidence |
| :- | :- | :- | :- |
| C1 | Code reading | Predict, Trace | Trace and delayed reviews |
| C2 | Debugging | Call it | Replay, Checkup bug |
| C3 | Design judgment | Your line at Deep | Delayed design reviews |
| C4 | Explaining a change | Explain back, PR walkthrough | Delayed explain items, new instance |
| C5 | Transfer | Compare | Applied-level items, Checkup task |
| C6 | Calibration | Confidence on every answer | Delayed items only |

A construct with no recent evidence shows "no evidence yet". Prediction accuracy is reported as its own line, never mixed into calibration (RT efficacy 19).

---

## 2. Moves in the build

### 2.1 Predict

- Trigger: before a deterministic step (test run, migration, query plan) on an idea at Not yet, within the moment cap.
- The engine refuses predictions on steps it marks non-deterministic (timing, randomness, network).
- Compared with the real outcome, with the gap at `path:line`. Never graded. Never moves a level. Recorded as prediction accuracy.

### 2.2 Call it

- Trigger: a test or build fails, and either C2 is below Applied or the delegation rate is above the threshold. Delegation rate: the share of the last 10 failures the agent diagnosed with no user hypothesis (window and threshold are design defaults, need to be measured).
- The agent keeps diagnosing in parallel and holds back only its conclusion until the user answers, skips, or its own diagnosis is ready and the user has not started typing.
- The user gives a cause and the first check.
- **Call it never moves a level** (RT efficacy 6). The agent's file reads and command output are visible while the user answers, and often show the cause. The engine records what the user could see: on T2 surfaces, the agent tool events between the failure and the answer; elsewhere "unknown".
- Uses: the answer updates the delegation signal; a sound check is fed back at once ("Good check"); and the episode can queue a Replay of the same failure, with the agent off, at a later date. Replay is where diagnosis counts.

### 2.3 Your line

- Trigger: the agent is about to write the one line (later a function, then a design choice) that carries an idea new to the user. At most one per task. Not under pressure or quiet.
- The agent calls `line open` with file, location, idea ID and the sealed check. The engine returns the marker text.
- **Marker text by repo ownership** (RT privacy 7):
  - Repos the user owns: `FIRSTHAND(you): the delay before retry n. Test: test_backoff.py::test_delays. Try it before reading the test.`
  - Repos the user does not own: `TODO: the delay before retry n. Test: test_backoff.py::test_delays.` No product name, no user name. The engine finds it by location and region hash.
  - Ownership: the user's own account owns the remote, or the user marked the repo as theirs. Unknown counts as shared.
- Marker rules: goal in outcome terms, names the test, never describes the computation. The engine rejects markers with operators or formula words.
- **Write first** (RT efficacy 7). The copy asks the user to try before reading the test. At `line done` the pad asks: "Did you read the test first? yes or no." First-try pass rate is reported split by that answer.
- **The evidence is a delayed item.** On `line done` the engine queues an executable review for a later date: the same goal, in a new instance where the item family allows (a different function in the same repo, or a bank family), with the test hidden. The user writes the line in a scratch copy; the hidden test grades it. That review can move a level. The in-session line records Met.
- `line.survived` is dropped as a learning signal. It may be kept as a product signal for how often lines get rewritten.
- Handback: "write it" any time; automatic under pressure, on quiet branches, on a failing deploy, and **at commit in shared repos**, so a marker is never committed there.
- Growth at Deep: a line, then a function, then a design choice (L5).

### 2.4 Explain back

- Trigger: after a step passes, at most once per task the user chose to learn from.
- Two or three sentences.
- **Rubric** (RT efficacy 12): written in a separate context from the code and the diff only. That context never reads the agent's explanation in the session. Points are about the mechanism, plus one "what changes if" point that cannot be answered by repeating a description.
- **Grading in v1:** after the answer locks, the sealed points are revealed and the user self-marks them. This records Met. A gated model grader (section 6) may grade later; even then the in-session answer records Met.
- **Delayed explain items** always use a new instance: a different function or a bank family with the same mechanism. These can move C4.
- The echo flag stays: if quoted spans nearly copy the agent's own words, the attempt is marked "echo" and cannot count even when graded.

### 2.5 Review first

Coding is moving to background agents, so the human is present at review time, not at breakpoints (RT market 3). Copilot cloud agent has no live user [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent].

- **Triggers:**
  - The user asks their agent to review a PR, or opens a PR branch with the agent. The skill tells the agent to call `moment` with breakpoint `pr_review` before it starts its own review.
  - `firsthand pr <url or number>` from any terminal. It fetches the diff with the host's CLI (for GitHub, `gh`), and shows it in the pad with the PR body, the agent's summary and review comments hidden.
- **The user does:** lists defects with a location and a severity, or says "looks clean". Confidence as usual. Then the PR body and the agent's review are shown.
- **Confirming a finding:** the engine offers "Show it with a test?" The user writes a test that fails on the PR head. If the PR is later fixed, the test should pass on the fix. A finding with a failing test on the head is "confirmed" at once.
- **Settling the rest later:** CI results on the PR, and any later commit that changes the flagged lines with a fix-style message or a failing-then-passing test within 60 days (design default), mark findings "likely right" or leave them "unconfirmed". A "looks clean" call on a PR that later needed a fix is a miss.
- **Grading for levels:** only confirmed findings and confirmed misses move C1 or C2. "Unconfirmed" never counts against the user.
- **Privacy:** findings are private, in the record. The user may post a finding as an ordinary review comment, in their own words, with no grade or product name attached. On work installs, Review first runs in the pad by default.
- **Budget:** counts as an unprompted moment, at most once per PR, never on the user's own PRs.

### 2.6 "Later" items from fast work

When the engine sees rapid delegation (short imperative prompts, quick turns, the user editing while the agent works; modes from Barke et al., https://arxiv.org/abs/2206.15000), it asks nothing and queues one later item from the episode, only if a review slot is free or the idea is in a growth area (section 7.3).

---

## 3. Drills

All drills: opt-in, inside the 3-a-day cap when due, never in the same week as the source material, keys sealed before offering.

### 3.1 Trace

- Source: the user's own committed code, at least 7 days old, in added repos.
- The engine picks a pure function or a small deterministic block and an input, runs it, and seals the output.
- **Where it runs** (RT privacy 2): a scratch copy built from committed files only (`git archive` of a commit), never `.env` or untracked files; agent and editor config stripped (`.claude/`, `.mcp.json`, `.cursor/`, `AGENTS.md`, `.vscode/`, `.idea/`); folder mode 0700; deleted after sealing. A container is used if present. Trace without a container is allowed only on repos the user added as their own, because the user and their agent already run that code.
- The user predicts the output, in the pad where possible. Running the code is possible and is the user's honour; the map's self-attested line covers it.
- Item family: the same function with a new input is a surface variant (caps at Recalled); a different function using the same idea is a new instance.

### 3.2 Check

- Source: past agent-written diffs in added repos. "Defective": a later commit fixed lines it introduced, detected by blame plus a failing-then-passing test, or a fix-style message. "Clean": no later commit changed its lines within 60 days (design default).
- **Labels are uncertain by construction** (RT efficacy 5). A defect may not have been found yet.
- Grading:
  - A finding that matches a known defect: right.
  - Missing a known defect that a test confirmed: a miss.
  - A finding in a diff labelled "clean", or not on the known list: "unconfirmed", with an offer to write a test that shows it. With a failing test on that code, it becomes confirmed and right, and the diff's label changes.
  - Only test-confirmed defects move levels. Defects known only from a commit message are practice.
- E15 hand-checks label accuracy on a sample before Check ships.
- No seeded bugs in user code, ever.

### 3.3 Replay

- Source: commits where a test went from failing on the parent to passing on the fix.
- **Runs only in a container with no network** (RT privacy 2), built from the parent commit's committed files, with dependencies installed from the lockfile in a separate step that has network, then network cut before any project code runs. If dependency install itself runs project scripts (for example npm install scripts), they run with network off or install scripts are disabled [unverified per package manager]. Without a container runtime, Replay is not offered.
- Old lockfiles can pin versions later found malicious. The engine checks the lockfile against a known-advisory list before install where one is available [unverified: which advisory sources, per ecosystem], and refuses on a match.
- The user enables Replay per repo with a plain warning.
- Gated by E2.
- Flow: in the pad, agent off: hypothesis, first check, then fix. Graded by process (does the check tell hypotheses apart; was it named before the fix), then the commit's own test. Process points are model-graded and so record Met in v1 until a grader passes the gate; the executable fix grades at once.
- Not reproducible: dropped, a Trace offered, nothing recorded against the user.

### 3.4 Compare

- Source: the same catalog idea met in two projects. Topic name hidden.
- Self-marked in v1 (Met), gated model grader later.

### 3.5 Explainers after an attempt

After an attempt locks, the user can ask for an explainer from their own code. Never first. Viewing it records Met.

### 3.6 Growth areas

Up to three ideas or constructs. They get extra drills beyond what is due, and priority when review demand exceeds slots (section 7.3). Default: none.

---

## 4. Items, families and distance

Every review, drill and unseen question comes from an item family (evidence C.2).

| Field | Meaning | Set by |
| :- | :- | :- |
| `family` | The deep structure, one sentence | Author or model |
| `surface` | Domain object, code shape, failure mode | Author or model |
| `distance` | same code, same function new input, same project other function, other file, other project, other domain | **The engine**, from paths, function names and a normalised AST hash, never from the model (RT efficacy 11) |
| `topic_name_shown` | Whether the idea's name appears | Engine checks the text |
| `format` | free recall, code, number, choice | Engine |
| `difficulty` | Author tag, replaced by an estimate from pilot or pooled data | Data |
| `source` | practice, unseen family, checkup, study pool, guide | Engine |
| `seal` | separate context, or asking context | Engine |
| `key_check` | Whether a second blind context solved it and agreed | Engine |

Rules:

- **Key check** (RT efficacy 11): every model-written practice key is solved again by a second blind context (executable where possible). Disagreement discards the item.
- **Bad-key refund:** a "sure" miss triggers a re-check of the key. If the re-check disagrees, the miss is refunded and the item retired. With pooled opt-in data, items that most "sure" answers miss are flagged for review.
- Distance "same code" or "same function new input" caps at Recalled.
- Applied needs distance "same project other function" or further, and the topic name hidden.

---

## 5. Levels

Ladder: `../PRODUCT.md` section 4.9. Not yet, Recalled, Applied, Held. Met is a separate list.

### 5.1 What an answer must have to count

All of these:

1. Delayed: at least the counting delay after the user last met the material (starts at 7 days, `DURABLE_AFTER_DAYS` in `record.py`; needs to be measured).
2. Format: free recall, code or number. Choice can count only up to Recalled.
3. Confidence: not "guess".
4. Provenance: typed (the pad, or a native ask form verified not to pass content to the model) or captured (a hook recorded the user's own prompt verbatim). Never relayed or imported.
5. Grade: tests, a person, or a grader model and version that passed the gate.
6. Seal: separate context.
7. Not an echo.

An answer that fails any rule is recorded with its correctness and a `cap_reason`, and shows under Met if right.

### 5.2 Moving up and down

- **Up one step:** two counting right answers on two different items, on different days (RT efficacy 2).
  - Not yet to Recalled: any two different items.
  - Recalled to Applied: two items at distance "same project other function" or further, topic hidden.
  - Applied to Held: right at a longer gap (starts at 21 days, needs to be measured) on an unseen family item, plus one other source: a Checkup result, field evidence, or another item family.
- **Down one step:** each counting delayed miss, and each "don't know" on a delayed item. Never more than one step per answer.
- "Don't know" copy: "Don't know is an honest answer. It counts as not recalled yet, and the idea comes back sooner." It is not counted as a sure miss in calibration.
- Imported legacy records cap at Recalled and need one new counting answer to move.

### 5.3 Evidence age

- Every level shows when it was last checked.
- Past the next due interval plus a margin (design default: half the interval), the map shows "not checked lately" in place of the level.
- Levels show "based on N of M due items answered" in `map all`.

### 5.4 What each surface can count

| Channel | Provenance | Counts |
| :- | :- | :- |
| The pad | typed | Yes |
| Native ask verified not to reach the model [unverified per host] | typed | Yes |
| Hook prompt capture (T2) | captured | Yes for practice items; never for unseen items |
| Agent chat on T0 and T1 | relayed | Met only |
| Vendor phone app | relayed | Met only |
| Cloud carry import | relayed, unauthenticated | Met only |

`init`, the map and the session-start line say this per surface (RT efficacy 15).

---

## 6. Grading and the grader gate

- Order: executable, person, gated model, self-mark.
- **v1:** only executable grades and people move levels (RT market 8). Model-graded task types are self-marked against sealed points and record Met.
- **The gate, per grader model and version** (RT efficacy 3):
  - A shipped calibration set of human-graded answers per task type.
  - Before a grader can move levels, the engine runs it on the calibration set (with the user's consent and cost shown).
  - Pass needs all of: Cohen's kappa against the human consensus at or above an absolute floor (threshold, a decision; 0.6 proposed); within 0.1 of human-human kappa; mean leniency against humans within a set margin (threshold, a decision).
  - A new grader version must pass again.
- **Audit sampling:** a share of undisputed grades (design default, needs to be measured) is regraded by a second grader or queued for the user to self-check against the points, so disputes are not the only regrade path.
- Disputes: one per grade, regraded against the same key, both readings shown. Two readings that disagree hold the level.

---

## 7. Reviews and scheduling

### 7.1 Basics

- Up to 3 due a day by default (decision 3). The user can lower it or raise it with an explicit setting.
- Offered after the first prompt of a session, default "later", also through the reminder or `firsthand review`.
- In the pad where open. Free recall, no code, no old answer, no options until commit (L7).
- Interleaving: easily confused ideas scheduled near each other, names hidden (L9).
- Intervals start from the current engine: 3, 7, 21, 60, 180 days after success, 1 day after a miss.

### 7.2 Slot mix

- Unseen family items take one slot on days with 3 due, at most (design default, needs to be measured).
- Cold-start re-checks and Review-first follow-ups share the remaining slots.

### 7.3 When demand exceeds slots

RT efficacy 9: with 2 practice slots and a 5-step ladder, one new idea a day needs about 5 reviews a day at steady state.

- **Entry control:** a new idea enters the queue only if projected demand fits the slots or the idea is in a growth area. Otherwise it is listed as "met, not scheduled".
- **Priority:** growth areas, then sure misses, then ideas one answer from a level change, then the rest.
- **Disclosure:** `map all` says "12 ideas are not being reviewed. Pick growth areas to choose which."
- **Bias tracking:** skip and expiry rates per item difficulty are reported in `stats`.

---

## 8. Dose and its test

Design targets for a user who builds daily on Standard. All are design targets, not findings. E1 measures the real numbers.

| Rep kind | Design target per week | Ceiling set by |
| :- | :- | :- |
| Retrieval (reviews, unseen items) | Up to 21 | 3 a day (decision 3) |
| Generation in the build | Up to 21 | 3 unprompted moments a day |
| Diagnosis practice (Call it) and evidence (Replay) | Eligible failures, plus Replay when due | Debugging profile, review cap |
| Checking agent output (Review first, Check) | One per PR reviewed, plus Check when due | Moment cap, review cap |

If E1 or E7 shows the dose does not move delayed outcomes: (1) offer more user-started drills, (2) raise the share of diagnosis and check items in due slots, (3) never raise interruptions in the build.

---

## 9. Unseen questions and the Checkup

### 9.1 Unseen family items (in product)

- Written by contracted engineers, per catalog idea, as **parameterised families**: a template, a generator for parameters, and a key function. Two writers review each family. Writers never see user data.
- The engine makes a fresh instance per user. A family is retired for a user after a set number of uses (design default).
- **Not encrypted in any meaningful sense.** The generator ships in the package. The spec says so (RT privacy 4).
- Shown only in the pad. Keys released only for typed answers.
- Labelled "unseen by your agent, not proctored". They guard against the teaching agent tuning to its own items. They do not guard against a user who asks the agent to answer.
- **The gap** between practised and unseen results shows "not yet calibrated" until family difficulty is equated with practice difficulty from pilot or pooled data (RT efficacy 10). `map all` lists which ideas have unseen coverage.

### 9.2 Study-only pool

Never shipped. Served by the study server inside the study only. Exposure tracked per item; items retired after use. It is the primary outcome instrument (G1-S, `measurement.md`).

### 9.3 The Checkup

- User-started, at most monthly, never due, never reminded.
- Served by the Checkup service on the user's request: an anonymous token, no account. The service records which task went to which token, so tasks can be retired and exposure counted.
- Contents: one small task in a real public repo the user has never opened, pinned to a commit; one bug to localise; two agent-style diffs to check, one clean.
- **Runs in a container with no network,** from a pinned image with dependencies resolved in advance, agent and editor config stripped (RT privacy 2). Without a container runtime, the Checkup is not offered, and the user is told what to install.
- Agent off. Steps in the pad. The user may edit files in the mounted folder with any editor.
- **Hidden tests run on the service.** The user's patch is sent when they submit. The tests never reach the machine.
- **Every task is piloted** before release, and its difficulty stored (RT efficacy 14).
- **Results** show against task difficulty, per construct, with a count. No trend is shown until a minimum number of Checkups (needs to be measured).
- **Signed result** (RT market 10): the service signs the task id, commit, patch hash, test outcome and date. A third party can check the signature and re-run the tests. The statement says it does not show who wrote the patch or with what help, and is "not a performance measure".
- Written by people. Never used for practice.

### 9.4 The sampler

Three unseen family items in the pad at install. Records Met only. Labelled "first look, not proctored".

---

## 10. Field evidence

`firsthand field <ref> "<what I did>"`. The engine checks the commit exists and is authored by the user. A missing agent trailer does not prove no agent was used (RT efficacy 8), so field evidence is labelled "self-reported" and counts as the second source for Held only alongside an unseen item. Within-person only.

---

## 11. Cold start

RT efficacy 8: commits with no agent trailer may be agent-written, so inference must not silence.

1. **Inference lowers frequency only.** Ideas found in the user's own commits (no agent trailer, before an optional cut-off) are marked `idea.likely_known`. They are offered less often (design default: a quarter as often, needs to be measured). They are never silent on inference alone.
2. **Silence needs two probes:** "I know X" asks one direct item and one new instance with the topic hidden. Both right, the cluster goes quiet in every project. One wrong, it becomes a normal idea.
3. **Re-check:** silenced clusters get one re-check item every few months (design default) in a review slot.
4. **First week:** a low moment cap; your line only for ideas with no prior authorship found.
5. E11 runs on juniors and seniors and measures trailer coverage per tool.
