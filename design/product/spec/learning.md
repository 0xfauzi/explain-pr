# Spec: the learning loop

Part of `../PRODUCT.md` (sections 4, 5 and 12). Evidence codes L1 to L19 are the design rules in `../research/learning-science.md` Part A.3. Skill codes C1 to C6 are from `../research/evidence.md`.

---

## 1. Skills

The product tracks six skills separately and never combines them into one score (evidence B.1). Debugging and programming ability are related but distinct: good programmers are not all good debuggers (Fitzgerald et al. 2008, research/evidence.md A.2 item 6).

| Code | Skill | Practice | Evidence that can move a level |
| :- | :- | :- | :- |
| C1 | Code reading | Predict, Trace | Trace, delayed reviews, Review-first findings |
| C2 | Debugging | Call it | Replay, Fresh repo tasks that start from a failing test |
| C3 | Design judgment | Your line at Deep, design calls | Delayed design items, design calls checked against what happened |
| C4 | Explaining a change | Explain back | Delayed explain items in a new instance |
| C5 | Transfer | Compare, Fresh repo | Applied-level items, Fresh repo |
| C6 | Calibration | Confidence on every answer | Delayed items only |

A skill with no recent evidence shows "no evidence yet". Prediction accuracy is its own line, never mixed into calibration, because a prediction is made before the outcome is known and a review is not.

---

## 2. Moves in the build

### 2.1 Predict

- Trigger: before a deterministic step (test run, migration, query plan) on an idea at Not yet, within the moment cap.
- The engine refuses predictions on steps it marks non-deterministic (timing, randomness, network), because a prediction that cannot be checked teaches nothing (L6).
- Compared with the real outcome, with the gap at `path:line`. Never graded. Recorded as prediction accuracy.

### 2.2 Call it

- Trigger: a test or build fails, and either C2 is below Applied or the agent has diagnosed most recent failures with no user hypothesis. The window is the user's recent failures in the record.
- The agent keeps diagnosing in parallel and holds back only its conclusion until the user answers, skips, or its own diagnosis is ready and the user has not started typing. The build never waits.
- The user gives a cause and the first check.
- Feedback at once: whether the check tells the likely causes apart, then the real cause. Diagnosis is a process, and forming a testable hypothesis before fixing is what good debuggers do (research/learning-science.md Part G).
- **Call it never moves a level.** The agent's file reads and command output are visible while the user answers, and often show the cause. Instead, the episode can queue a Replay of the same failure, with the agent off, on a later day. Replay is where diagnosis counts.

### 2.3 Your line

- Trigger: the agent is about to write the one line (later a function, then a design choice) that carries an idea new to the user. At most one per task. Not under pressure or quiet.
- The agent calls `line open` with file, location, idea ID and the sealed check. The engine returns the marker text.
- **Marker text by repo ownership:**
  - Repos the user owns: `FIRSTHAND(you): the delay before retry n. Test: test_backoff.py::test_delays. Try it before reading the test.`
  - Repos the user does not own: `TODO: the delay before retry n. Test: test_backoff.py::test_delays.` No product name, no user name. The engine finds it by location and region hash.
  - Ownership: the user's own account owns the remote, or the user marked the repo as theirs. Unknown counts as shared.
- Marker rules: goal in outcome terms, names the test, never describes the computation. The engine rejects markers with operators or formula words, so the marker does not give the answer away.
- **Write first.** The copy asks the user to try before reading the test, because reading the test first turns generation into copying.
- **The delayed item.** On `line done` the engine queues a review for a later day: the same goal, in a new instance where the item family allows (another function in the same repo, or a bank family), with the test hidden. The user writes the line in a scratch copy; the hidden test grades it. That review can move a level. The in-session line records Met.
- Handback: "write it" any time; automatic under pressure, on quiet branches, on a failing deploy, and at commit in shared repos, so a marker is never committed there.
- Growth at Deep: a line, then a function, then a design choice (L5).

### 2.4 Explain back

- Trigger: after a step passes, at most once per task the user chose to learn from.
- Two or three sentences. Self-explanation has one of the larger effects in the research (g = 0.55, Bisra et al. 2018, research/learning-science.md A.1 item 4).
- **Rubric:** written in a separate context from the code and the diff only. That context never reads the agent's explanation. Points are about the mechanism, plus one "what changes if" point that cannot be answered by repeating a description.
- **Feedback:** after the answer locks, a model grader marks each point with a quote from the answer, or "missing". The sealed points are shown, and the user self-marks. The in-session answer records Met.
- **Delayed explain items** always use a new instance: another function, or a bank family with the same mechanism. These can move C4 (accuracy rules, section 12).
- Echo check: if quoted spans nearly copy the agent's own words, the attempt is marked "echo" and cannot count.

### 2.5 Review first

The human is present at review time, even when the agent ran in the background. Copilot cloud agent has no live user [verified: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent]. Checking agent output is a skill in its own right (L17), and code review is already a main channel of knowledge transfer (Bacchelli and Bird 2013).

- **Triggers:**
  - The user asks their agent to review a PR, or opens a PR branch with the agent. The skill tells the agent to call `moment` with break `pr_review` before it starts its own review.
  - `firsthand pr <url or number>` from any terminal. It fetches the diff with the host's CLI (for GitHub, `gh`) and shows it in the pad, with the PR body, the agent's summary and review comments hidden.
- **The user does:** lists defects with a location and a severity, or says "looks clean". Confidence as usual. Then the PR body and the agent's review are shown.
- **Confirming a finding:** the engine offers "Show it with a test?" The user writes a test that fails on the PR head. A finding with a failing test on the head is confirmed at once.
- **Settling the rest later:** CI results on the PR, and any later commit that changes the flagged lines with a fix, mark findings "likely right" or leave them "unconfirmed". A "looks clean" call on a PR that later needed a fix, confirmed by a test, is a miss.
- **Levels:** only confirmed findings and confirmed misses move C1 or C2. "Unconfirmed" never counts against the user.
- **Privacy:** findings are private. The user may post one as an ordinary review comment, in their own words, with no grade or product name attached.
- **Budget:** counts as an unprompted moment, at most once per PR, never on the user's own PRs.

### 2.6 Deep only: Plan first and design calls

- **Plan first.** Before the agent plans a task, the user lists the steps and what done looks like. The agent then plans, and the engine shows the gaps between the two. This is the Lead-and-Reveal pattern, the best of seven techniques tested for aligning perceived and real ability (Kazemitabaar et al. 2025, research/learning-science.md A.1 item 5). Practice and feedback only; never moves a level.
- **Design calls.** When the user chooses between two designs, the engine asks for one predicted consequence ("this will make adding a second currency hard"). When the code is next touched in a way that tests the prediction, the engine asks once whether it held. Real work gives slow feedback on design; this creates it (research/learning-science.md D.3). A design call checked later is C3 evidence.

### 2.7 "Later" items from fast work

When the engine sees rapid delegation (short imperative prompts, quick turns, the user editing while the agent works; modes from Barke et al., https://arxiv.org/abs/2206.15000), it asks nothing and queues one later item from the episode, if a review slot is free or the idea is in a growth area (section 7.3).

---

## 3. Drills

All drills: opt-in, inside the daily cap when due, never in the same week as the source material, keys sealed before offering. Drills put errors where they are free: a scratch copy, not the real branch (research/learning-science.md D.3).

### 3.1 Trace

- Source: the user's committed code, at least 7 days old, in added repos.
- The engine picks a pure function or a small deterministic block and an input, runs it, and seals the output.
- Where it runs: a scratch copy built from committed files only (`git archive` of a commit), agent and editor config stripped, folder mode 0700, deleted after sealing (`security.md` section 2). A container is used if present.
- The user predicts the output in the pad.
- Same function with a new input is a surface variant and caps at Recalled. Another function using the same idea is a new instance.

### 3.2 Check

- Source: past agent-written diffs in added repos. "Has a known defect": a later commit fixed lines it introduced, found by blame plus a failing-then-passing test, or a fix-style message. "No known defect": no later commit fixed its lines.
- "No known defect" is not "clean". A defect may not have been found yet. So:
  - A finding that matches a known defect: right.
  - Missing a known defect that a test confirmed: a miss.
  - A finding in a diff with no known defect: "unconfirmed", with an offer to write a test that shows it. With a failing test, it becomes confirmed and right.
  - Only test-confirmed defects move levels. Defects known only from a commit message are practice.
- No seeded bugs in user code, ever.

### 3.3 Replay

- Source: commits where a test went from failing on the parent to passing on the fix.
- Runs only in a container with no network (`security.md` section 2), built from the parent commit's committed files. Dependencies install from the lockfile in a separate step with network and install scripts disabled where the package manager allows, then network is cut before any project code runs.
- The user turns Replay on per repo, with a plain warning.
- Flow, in the pad, agent off: hypothesis, first check, then fix. Feedback on the check (does it tell hypotheses apart; was it named before the fix) is model-graded. The fix is graded by the commit's own test and can move C2 at once.
- If the bug does not reproduce: dropped, a Trace offered, nothing recorded against the user. Repos where few bugs reproduce simply offer fewer Replays.

### 3.4 Compare

- Source: the same catalog idea met in two projects, or in a project and a bank family. Topic name hidden.
- The user says what is the same and what differs. Comparing two cases is the most reliable route to using a principle in a new place (Gentner, Loewenstein and Thompson 2003, research/learning-science.md D.4). A record that spans every repo the user works in is what makes this possible.
- Model feedback with quotes. Can move C5 (accuracy rules, section 12).

### 3.5 Fresh repo

A task in a public repo the user has never opened, agent off. The user starts it. It is practice for transfer and for reading unfamiliar code, the two skills that matter most when the agent is not there (research/learning-science.md D.4 and Part G).

- **Task sources:**
  - *The open task set:* tasks written by contributors, each pinned to a public repo and commit, tagged with catalog ideas, with a goal statement and tests. Reviewed like code.
  - *Mined tasks:* the miner scans public repos in a curated list for commits where a new test fails on the parent and passes on the commit, and the diff touches a small number of files. The goal is written from the test name and a separate-context summary of the behaviour, checked so it does not describe the computation.
- **Choice:** the engine picks a task that uses an idea the user has practised elsewhere, with the topic name hidden, so it practises transfer. The user can also ask for a language or an idea.
- **Setup:** the engine clones the repo at the parent commit, builds the container from a pinned image, installs dependencies, then cuts the network. The tests that grade the task are sealed in the record and are not in the working folder.
- **Work:** steps in the pad; the user edits files in the mounted folder with any editor. The pad asks the user not to open their agent there, and the stripped config means opening it runs no project hooks.
- **Grading:** on submit, the engine copies in the sealed tests and runs them. The result shows which tests passed, then the real commit for comparison, and one question: what did the real change do that yours did not?
- **No timer.** The task shows a size ("small: one function and its caller"), never a time limit.
- **Levels:** a passing Fresh repo task is C5 evidence and can complete Held for the ideas it was tagged with.

### 3.6 Explainers after an attempt

After an attempt locks, the user can ask for an explainer built from their own code. Never first: the attempt comes before the explanation (L18). Viewing it records Met.

### 3.7 Rehearsals from postmortems

In repos with a codebase guide (`shared-repos.md` section 2), a postmortem becomes a rehearsal: the symptoms and logs, the real resolution sealed. The user gives a first hypothesis and a first safe action. Rare, high-stakes work needs simulated reps (L16).

### 3.8 Growth areas

Up to three ideas or skills. They get extra drills beyond what is due, and priority when review demand exceeds slots (section 7.3). Default: none.

---

## 4. Items, families and distance

Every review, drill and bank item comes from an item family (evidence C.2).

| Field | Meaning | Set by |
| :- | :- | :- |
| `family` | The deep structure, one sentence | Author or model |
| `surface` | Domain object, code shape, failure mode | Author or model |
| `distance` | same code, same function new input, same project other function, other file, other project, other domain | **The engine**, from paths, function names and a normalised AST hash, never from the model |
| `topic_name_shown` | Whether the idea's name appears | The engine checks the text |
| `format` | free recall, code, number, choice | The engine |
| `source` | practice, bank, fresh repo, guide | The engine |
| `seal` | separate context, or asking context | The engine |
| `key_check` | Whether a second blind context solved it and agreed | The engine |

Rules:

- **Key check:** every model-written key is solved again by a second blind context, executable where possible. Disagreement discards the item.
- **Bad-key refund:** a "sure" miss triggers a re-check of the key. If the re-check disagrees, the miss is refunded and the item retired.
- Distance "same code" or "same function new input" caps at Recalled.
- Applied needs distance "same project other function" or further, and the topic name hidden (L9, research/learning-science.md D.4).

### 4.1 The open question bank

- Families written by people, per catalog idea: a template, a parameter generator and a key function. Two reviewers approve each family in a pull request.
- The engine makes a fresh instance for each use, and retires a family for a user after it has used each of its forms.
- Bank items are mixed into review slots. They come from authors who never saw the user's session, so they check the idea itself, not the agent's way of teaching it.
- Shown in the pad. Keys released only for typed answers, so an agent cannot see the key by locking a placeholder.

---

## 5. Levels

Ladder: `../PRODUCT.md` section 5.9. Not yet, Recalled, Applied, Held. Met is a separate list.

### 5.1 What an answer must have to count

All of these:

1. Delayed: at least 7 days after the user last met the material (`DURABLE_AFTER_DAYS` in `record.py`). Immediate performance shows what the user can do now, not what they learned (Soderstrom and Bjork 2015).
2. Format: free recall, code or number. Choice can count only up to Recalled, because recognition is easier than recall.
3. Confidence: not "guess".
4. Provenance: typed (the pad, or a native ask form verified not to pass content to the model) or captured (a hook recorded the user's own prompt verbatim). Never relayed or imported.
5. Grade: tests, a person, or a model grader under the accuracy rules (section 12).
6. Seal: separate context.
7. Not an echo.

An answer that fails any rule is recorded with its correctness and a `cap_reason`, and shows under Met if right.

### 5.2 Moving up and down

- **Up one step:** two counting right answers on two different items, on different days. One right answer can be luck; two on different items is a pattern.
  - Not yet to Recalled: any two different items.
  - Recalled to Applied: two items at distance "same project other function" or further, topic hidden.
  - Applied to Held: right at a longer gap (21 days, the third step of the interval ladder in `record.py`), plus one other kind of evidence: a Fresh repo task, a confirmed Review-first finding, field evidence, or another item family.
- **Down one step:** each counting delayed miss, and each "don't know" on a delayed item. Never more than one step per answer.
- "Don't know" copy: "Don't know is an honest answer. It counts as not recalled yet, and the idea comes back sooner." It is not counted as a sure miss in calibration.
- Imported legacy records cap at Recalled and need one new counting answer to move.

### 5.3 Evidence age

- Every level shows when it was last checked.
- Past the next due interval plus half that interval, the map shows "not checked lately" in place of the level. Skills decay without use, cognitive ones faster (Arthur et al. 1998, research/learning-science.md A.1 item 3).
- `map all` shows "based on N of M due items answered".

### 5.4 What each channel can count

| Channel | Provenance | Counts |
| :- | :- | :- |
| The pad | typed | Yes |
| Native ask verified not to reach the model [unverified per host] | typed | Yes |
| Hook prompt capture (T2) | captured | Yes, except bank items |
| Agent chat on T0 and T1 | relayed | Met only |
| Vendor phone app | relayed | Met only |
| Cloud import | relayed | Met only |

A relayed answer passed through the agent, which could have shaped it. `init`, the map and the session-start line say what counts on each surface.

---

## 6. Grading

- Order: executable, person, model, self-mark.
- **Executable first.** Trace, Replay fixes, your-line reviews, Review-first and Check confirmations, and Fresh repo are graded by running code.
- **Model feedback** on every open answer: each rubric point is marked with a quote from the answer or "missing". No quote, no point. Graded twice with points shuffled; disagreement marks the grade "uncertain" and it does not move a level.
- **Model grades and levels.** Model grades move levels under the accuracy rules in section 12.
- **Disputes:** one per grade, regraded against the same key, both readings shown. Two readings that disagree hold the level.
- Rubric inputs are exactly four fields: prompt, sealed rubric, excerpt shown, and the answer marked as data that may contain instructions.

---

## 7. Reviews and scheduling

### 7.1 Basics

- Up to 3 due a day by default (founder decision 3). The user can lower it or raise it.
- Offered after the first prompt of a session, default "later", and through the reminder or `firsthand review`.
- In the pad where open. Free recall, no code, no old answer, no options until the answer is locked (L7).
- Interleaving: easily confused ideas are scheduled near each other, names hidden (L9).
- Intervals from the current engine: 3, 7, 21, 60, 180 days after success, 1 day after a miss (`record.py`). Spacing matters more than the exact ladder (L8).

### 7.2 Slot mix

- At most one bank item a day, so practice on the user's own code keeps most slots.
- Cold-start re-checks and Review-first follow-ups share the remaining slots.

### 7.3 When demand exceeds slots

With 3 slots a day and a 5-step ladder, each new idea needs several reviews over its first months, so a steady stream of new ideas will outrun the slots.

- **Entry control:** a new idea enters the queue only if projected demand fits the slots or the idea is in a growth area. Otherwise it is listed as "met, not scheduled".
- **Priority:** growth areas, then sure misses, then ideas one answer from a level change, then the rest.
- **Disclosure:** `map all` says "12 ideas are not being reviewed. Pick growth areas to choose which."

### 7.4 Dose

On Standard, a user who builds daily gets up to 3 retrieval reps and up to 3 generation reps a day, plus diagnosis and checking reps from real failures and PRs, plus any drills they start. If they want more, the way to get it is drills and a raised review cap, never more interruptions in the build.

---

## 8. Field evidence

`firsthand field <ref> "<what I did>"`. The engine checks the commit exists and is authored by the user. A missing agent trailer does not prove no agent was used, so field evidence is the user's own statement. It can be the "other kind of evidence" for Held. Doing the thing for real is the strongest signal there is (research/learning-science.md Part G).

---

## 9. Cold start

Commits with no agent trailer may be agent-written: inline completions and pasted chat code usually leave no trailer. So inference must not silence.

1. **Inference lowers frequency only.** Ideas found in at least two of the user's own commits with no agent trailer, before an optional cut-off date, are marked `idea.likely_known` and offered less often. They are never silent on inference alone.
2. **Silence needs two probes:** "I know X" asks one direct item and one new instance with the topic hidden. Both right, the cluster goes quiet in every project. One wrong, it becomes a normal idea.
3. **Re-check:** silenced clusters get one re-check item every few months in a review slot.
4. **First week:** a lower moment cap; your line only for ideas with no prior authorship found.

---

## 10. How the user sees progress

The map is the feedback. It shows, per idea and skill, what the user has shown without the agent, how it was graded, and how long ago. The weekly line picks one fact from the record. `firsthand stats` shows the user's own answer rate, skips and dose, on their machine only.

The product does not run studies, collect telemetry or compute effects per user. The design follows the research cited in each section. If the research moves, the design moves with it.

---

## 11. Design defaults and their reasons

| Default | Value | Reason |
| :- | :- | :- |
| Counting delay | 7 days | `record.py`; long enough that the answer is retrieval, not short-term memory |
| Review intervals | 3, 7, 21, 60, 180 days; 1 after a miss | `record.py`; spacing at all matters more than the exact ladder (L8) |
| Reviews a day | 3 | Founder decision 3 |
| Moments in the build a day | 3 | Same as the review cap; the build always wins |
| Your line per task | 1 | Founder decision 2 |
| Two skips | End questions for the session | research/experience-design.md P3 |
| Growth areas | Up to 3 | Matches the daily cap, so each can get a slot |
| Silenced idea re-check | Every few months | Catches decay in ideas the user thought they knew, at little cost |
| "Not checked lately" margin | Half the next interval | Past that, the last check says little about now |

---

## 12. Keeping the agents accurate

Model grading moves levels. There is no grader experiment. Instead the design makes wrong grades rare, visible and cheap:

1. **Keys come from the code, not from the model's belief.** A prediction's key is the output of actually running the code, sealed before the question is shown. Every point in an explain key cites a `file:line`, and the engine checks mechanically that the cited lines exist and say what the key quotes. A key that fails this check is thrown away and the question is not asked.
2. **Every key is answered blind before it is used.** A second agent, given only the code and the question, answers it. If its answer does not match the key, the question is dropped. This catches ambiguous questions and wrong keys before a user ever sees them.
3. **Rubric points are concrete claims, not quality judgments.** Each point is one fact the answer must contain ("the key is the order id"), so grading is a presence check, not an opinion. Length earns nothing.
4. **The grader is isolated.** It runs in a fresh context that never saw the build conversation. It gets exactly four fields: the question, the sealed points, the code excerpt, and the answer marked as untrusted data.
5. **No quote, no point.** Each awarded point must quote the answer. The engine checks that the quote is really in the answer.
6. **Two passes must agree.** The answer is graded twice with the points in a different order. If the passes disagree, the grade is marked uncertain and does not move a level.
7. **One wrong grade cannot move a level.** A level goes up only after two right delayed answers on different items, on different days. A wrong "right" costs one early promotion at most. A wrong "miss" only brings the idea back sooner.
8. **The user sees the evidence and can dispute.** Every grade shows the quotes and the `file:line` behind each point. A dispute regrades with the user's reason. If the readings disagree, the level holds.
9. **Grader changes are tested like code.** A set of answers graded by people lives in the repo as a regression suite. A new grader prompt or model version must pass it in CI before it ships.
