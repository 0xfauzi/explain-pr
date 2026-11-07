# Red team: learning efficacy skeptic

Reviewer lens: where the design produces the feeling of learning without the learning, where grading is unreliable, and where the record says something that is not true.

Scope: `design/product/PRODUCT.md`, `spec/learning.md`, `spec/measurement.md`, the grading and cold-start parts of `spec/architecture.md`, the map in `spec/experience.md`, and `spec/traceability.md`.

Rules used here: no invented numbers. Where I do arithmetic, it uses only the spec's own design defaults and says so. Claims about a product or harness carry [verified: source] or [unverified].

Summary verdict: the spec is unusually honest about what it cannot know. Provenance labels, sealing, caps and the claims ladder are good. But the honesty is applied to the source of an answer, not to how much a single answer can mean. Levels move on one binary response. The study's primary outcome is drawn from the same bank users practise against in the product. The grader gate is relative, not absolute. And every experiment before the 16 to 24 week engine build measures engagement, not learning. The record will look rigorous and still be mostly noise. Each problem below has a small fix.

---

## 1. The study measures the treatment arm on items it has practised (critical)

**What fails.** The study's primary outcome is G1, "held-out unaided battery from unseen questions" (PRODUCT.md 9.1 and 9.4; `measurement.md` section 4). In the product, unseen questions are mixed into reviews, one slot in three (`learning.md` 7.1). So the treatment arm sees the bank's items, its format, its item families and its "topic name hidden" style for weeks. The control arm never does. Any gap on G1 then mixes learning with instrument familiarity. There is also a contradiction: PRODUCT.md 9.1 says "the primary outcome is transfer" and names G2 as "lagging, primary", while 9.4 and `measurement.md` 4 name G1 as primary.

**Scenario.** The study runs. The treatment arm scores higher on G1. A reviewer asks whether treatment users had answered items from the same families. They had, by design. The result cannot be published as learning, and the claims ladder's first real rung is lost after months of work.

**Severity.** Critical. It voids the only evidence that can support the product's central claim.

**Smallest fix.**
- Split the human-written bank into two disjoint pools before any user sees it: an in-product pool and a study-only pool that never ships in the package.
- Give the control arm the same number of exposures to the item format, on unrelated content, so format familiarity is balanced.
- Pick one primary outcome and write it in both places. Given principle 6 and the founder's goal, make G2 primary, or state plainly that G1 is primary because G2 is too costly, and say G2 is secondary.

---

## 2. A level moves on one binary answer, in both directions (critical)

**What fails.** Recalled is "right on a sealed item at least a few days later" (PRODUCT.md 4.9). One item. Levels "move down on a miss at any delayed item" (`learning.md` 5), and Not yet is "a miss on a delayed item" (4.9). So one lucky answer raises a level, and one hard item drops it. Three gaps make this worse:

- **Guessing.** The user can mark "guess" and still be right. The spec does not say a right guess counts less. Choice cards on the phone (PRODUCT.md 6.8, v2) are recognition, not free recall, and the spec does not say they count less either. `learning.md` 6 requires free recall for reviews, but the phone path contradicts it.
- **"Don't know".** PRODUCT.md 4.1 says "'Don't know' never counts against the user." If that means it does not lower a level, a user at Held can answer "don't know" forever and stay Held. If it does lower the level, the copy is false. The spec does not say which.
- **The headline.** The map's first line is "What you can do without the agent, last 30 days", followed by ideas at Recalled (`experience.md` 5). A single correct delayed answer about one function the user saw is reported as something they can do.

**Scenario.** A user sees a Trace review on `merge_windows` six days later, types a guess, and is right. The map now says "What you can do without the agent: interval merging (Recalled)." A week later they miss one hard unseen item on the same idea and drop to Not yet. The map swings each week. The user learns that the map is noise, or worse, believes it.

**Severity.** Critical. This is the record lying, in the product's main view.

**Smallest fix.**
- Raise a level only on two correct delayed answers on different items, at least one marked "sure" or "think so". A correct "guess" updates the schedule but not the level.
- Drop a level by one step per miss, not to Not yet. Only two misses in a row drop to Not yet.
- Decide "don't know": it carries no verdict word and no penalty in tone, but it counts as not recalled for the level and the schedule. Change the copy to "Don't know is a normal answer. It brings the idea back sooner."
- Tag every answer with its response format (free recall, choice, executable). Choice answers cap at Seen until a format study says otherwise.
- Change the headline to "Recalled in the last 30 days", not "What you can do without the agent". Keep "can do" for Applied and above.

---

## 3. The grader gate passes graders that are close to noise, and validates the wrong grader (critical)

**What fails.** E5 passes a task type if "model-human Cohen's kappa within 0.1 of human-human kappa" (`measurement.md` E5; `architecture.md` 5). Three problems:

- **No absolute floor.** If two trained humans agree at a low kappa on, say, Call it process points, a model 0.1 below that passes. A rubric humans cannot agree on is not fit to move a level, however well the model matches the humans.
- **The validated grader is not the deployed grader.** In production the grader is whichever provider is available: a subagent of the user's agent, the user's headless CLI, or the user's own API key (`architecture.md` 5). These are different models from different vendors, and they change version without notice. E5 measures one. The spec records the grader version per grade, but nothing blocks an unvalidated version from moving levels.
- **"Grade twice with points shuffled" measures self-consistency.** The same model graded twice will agree with itself on a systematic leniency. Disagreement catches noise, not bias. And the user-initiated regrade (PRODUCT.md 6.5) is one-directional: users dispute only grades they think are too low.

**Scenario.** The Claude Code subagent passes E5 on explain back. A Cursor user's grades come from a different model through their API key. That model gives credit for vague answers that name the right words. Their explain-back items look strong at delayed review. Nobody checks, because the gate was passed once.

**Severity.** Critical. Every open-answer level on the map rests on this gate.

**Smallest fix.**
- Add an absolute floor for both human-human and model-human agreement per task type. The value is a founder decision, set before E5 runs.
- Make the gate per grader model and version. An unvalidated grader can record attempts and give feedback, but cannot move a level. Ship a small fixed calibration set with known human grades, run it when a new grader version is first seen, and refuse level moves if it fails.
- Add a leniency check on that set (share of points given versus humans), not only kappa.
- Make disputes symmetric: when the engine regrades, it also sometimes regrades grades the user did not dispute, and reports both directions in `map all`.

---

## 4. Nothing before the engine build tests whether anyone learns (critical)

**What fails.** The v0 experiments that gate the 16 to 24 week v1 build (PRODUCT.md 10) are E0 to E5, E8, E9 and E11. E1 passes on answer rate and review completion. E4 passes on agreement with a person and felt cost. E7, the only learning-shaped pilot, says "No effect claim" and passes on whether 80% of delayed items were taken. So a v1 can be built on a loop that people answer and do not learn from. Worse, the E1 gate ("at least half of offered moments answered") rewards the product for asking easy, short questions, which is the feeling of learning that principle 13 warns about.

**Scenario.** E1 passes because Predict moments are quick and fun. E7 completes. Six months later the study shows no effect on G1. The engine, adapters and catalog were built around moves that never had a learning check.

**Severity.** Critical for the product's purpose, though not for the code.

**Smallest fix.**
- Add a cheap learning check to v0: a small lab study with the existing skill, in the Shen and Tamkin setting (a new library, one session, a delayed quiz a week later), skill on versus off. It will be underpowered. Its job is a go or no-go on direction, with the threshold fixed before the run.
- Add to E1 a guard: item difficulty is measured (delayed accuracy per move), and a pass with answer rate rising while delayed accuracy is near ceiling counts as a warning, not a pass.

---

## 5. The Check drill's answer key is wrong by construction (major)

**What fails.** A diff is "defective" if a later commit fixed its lines, found by blame and a fix-style message or a failing-then-passing test. A diff is "clean" if no later commit changed its lines within 60 days (`learning.md` 3.2). Both labels are noisy. Commits called "fix" are often style, rename or refactor work. "Clean" means "nobody found the bug yet", which the spec admits. The grading then uses precision against this list, and "clean diffs make 'always find something' cost points". So a user who finds a real, unreported defect in a "clean" diff loses points. The drill punishes the best checkers most.

**Scenario.** A user spots a missing null check in a two-month-old agent diff marked clean. They are graded down for a false positive. They learn to say "clean" more often. The C1 and G4-style practice trains the wrong habit.

**Severity.** Major.

**Smallest fix.**
- A defect the user reports on a "clean" diff is graded "unconfirmed", never wrong. Offer: "Write a test that shows it" (executable, can confirm), or "save it as a note".
- Use only diffs whose fix commit has a failing-then-passing test as "defective" items that can move a level. Message-only labels can be practice with feedback, not level evidence.
- Measure label precision on a sample by hand before Check moves levels, as a new experiment.

---

## 6. Call it leaks the answer through the agent's visible work (major)

**What fails.** During Call it, "the agent keeps diagnosing in parallel" and "holds back only its conclusion" until the user answers, skips, or "the agent's own diagnosis is ready and the user has not started typing" (`learning.md` 2.2). On every surface I know of, the agent's investigation is visible as it happens: it reads files, runs commands and prints output [unverified per surface]. That stream often shows the cause before any conclusion. And the window closes as soon as the agent is ready, which for a simple failure may be seconds. Point 2, "the check was named before any fix was shown", is recorded from event order, but reading the agent's tool output is not a fix being shown.

**Scenario.** A test fails. The agent opens `client.py`, greps for `idempotency`, and prints the line. The user types "missing idempotency key, I'd check the request headers". Points 1 and 2 are awarded. The user read the answer.

**Severity.** Major. C2, the largest gap in Shen and Tamkin, is the construct this drill is meant to fix.

**Smallest fix.**
- Record what the user could see at answer time: the number of agent tool calls and files touched since the failure. Grade Call it as process evidence only when the answer arrived before the agent's first investigation step, or on surfaces where hooks can hold the agent's tool output until the user answers.
- Otherwise record it as "answered while the agent was investigating", which caps at Seen.
- Move level-bearing diagnosis practice to Replay, where the agent is off by design.

---

## 7. "Your line" is fill-in-the-blank against a visible test (major)

**What fails.** The marker names the test (`test_backoff.py::test_delays`, PRODUCT.md 4.3). The agent wrote that test and the code around the gap. The test usually contains the expected values. The function signature and variable names (`base_delay`, `attempt`) give the shape. The marker linter forbids formula words in the marker, but not in the surrounding code. So the user can often read the test and type the line that makes it pass, with little generation. First-try pass rate then measures test reading. `line.survived` (the line still exists at next commit and 30 days later) measures whether anyone touched the file, not learning.

**Scenario.** The test asserts `delays == [1, 2, 4, 8]`. The user reads it and writes `return 2 ** n`. It passes first try. The record shows a your-line success on exponential backoff. The user could not have written it without the test.

**Severity.** Major. The founder's anchor feature records more than it teaches. Same-session lines cap at Seen, so the level is not inflated, but `first-try pass rate` is a leading indicator in `measurement.md` 2.2 and will be read as learning.

**Smallest fix.**
- Name the test, but tell the user "Write it before you read the test. Say 'show the test' if you need it." Record whether the test was opened first (hook surfaces can see the file read; elsewhere self-reported).
- Report first-try pass rate split by "test seen before writing" and "not seen".
- Drop `line.survived` from the learning indicators. Keep it as a product signal only.
- Feed each your-line idea into a delayed review with the test hidden. That review, not the line, is the learning evidence.

---

## 8. Cold-start inference silences the gaps it should find (major)

**What fails.** Ideas in commits by the user "with no agent co-author trailer" are marked likely known and go silent (`architecture.md` 7). Many ways of using AI leave no trailer: inline completions, code pasted from a chat window, agents that do not add one by default [unverified per tool]. For segment 1, juniors who build with an agent every day, much of their "own" history may be AI-written with no trailer. Those ideas go silent. The same check underlies field evidence (PRODUCT.md 4.10), so AI-written fixes can also be logged as unaided field evidence. E11 tests only seniors.

"I know X" (PRODUCT.md 4.7) silences a whole cluster in every project after one right answer to one probe, and nothing re-checks it. Silence is permanent and unmeasured.

**Scenario.** A junior adds their repo. Their last year of commits came from Copilot completions and pasted ChatGPT code. The engine marks retries, pagination and SQL joins as likely known. The product never asks about any of them. The map shows nothing wrong, because silent ideas carry no level.

**Severity.** Major.

**Smallest fix.**
- Inference lowers how often an idea is offered. It never silences on its own. Silence needs a passed probe.
- A probe silences only the idea probed, not its cluster, and needs two right answers, one of them a new instance with the topic name hidden.
- Every silenced idea gets one low-frequency unseen item after a long gap (interval a design default, needs to be measured). A miss lifts the silence.
- Run E11 on juniors too, and measure trailer coverage per tool before trusting the trailer as a signal.
- Field evidence from a commit with no trailer is labelled "no agent trailer found", not "unaided".

---

## 9. The review cap cannot keep up, and the map hides it (major)

**What fails.** Arithmetic from the spec's own defaults: 3 due reviews a day (decision 3); one slot in three goes to unseen questions on days with 3 due (`learning.md` 7.1), leaving 2 practice slots. Intervals after success are 3, 7, 21, 60 and 180 days (`learning.md` 6), so each idea needs 5 reviews to complete the ladder. If one new idea a day enters the queue, steady-state demand is about 5 reviews a day against 2 practice slots. The first month alone needs about 3 a day. "After a gap: at most 3, rest spread, no backlog count" (PRODUCT.md 5.3). So most ideas will be reviewed late or never, and nothing on the map says so.

Two consequences for the record. First, levels go stale: an idea at Recalled from months ago still shows Recalled in `map all`. Second, the answered set is not random. Users skip, say "later", and let items expire. If hard items are skipped more, the levels on the map are computed from the easy ones.

**Scenario.** A user on Standard meets about one new idea a day for two months. Review slots are always full. Their early ideas never reach the 21-day review. `map all` still lists them at Recalled from a 7-day review weeks ago.

**Severity.** Major. Founder decision 3 is fine. The spec just has to admit what it implies.

**Smallest fix.**
- Show evidence age next to every level: "Recalled, last checked 40 days ago". Past the next due interval plus a margin, show "not checked lately" instead of the level.
- When demand exceeds slots, the engine picks which ideas to keep reviewing (growth areas first, then sure misses, then the rest) and says so in `map all`: "12 ideas are not being reviewed. Pick growth areas to choose which."
- Track skip and expiry rate per item difficulty, and report levels with "based on N of M due items answered".
- Lower the new-idea rate rather than the review rate: "your line" and Explain back on an idea add it to the review queue only if there is room or it is in a growth area.

---

## 10. The unseen-question gap is not interpretable (major)

**What fails.** The map's headline number is the gap between practised and unseen results per construct (`learning.md` 7.1; `experience.md` 5). It is meant as a Goodhart alarm. But the two sets differ in more than "seen by the teaching agent". Practice items are about the user's own code, with context. Unseen items are generic, written per catalog idea, with no project context. They differ in format and difficulty. A gap may mean inflation, or it may mean the unseen items are harder. In addition:

- The v1 bank covers "a small set of ideas" (PRODUCT.md 10). For every other idea there is no gap and no Held.
- Unseen items are reused across months and are not retired after use (only Checkup tasks are). After one exposure, an unseen item is a practised item.
- The bank ships in the package; a determined user can read it. The spec says so, which is honest.

**Scenario.** A user's practice accuracy on C1 is high and unseen accuracy is lower. The map shows a gap. The user reads it as "the product is inflating me" or "I am bad at transfer". Neither is supported, because the item sets were never equated.

**Severity.** Major.

**Smallest fix.**
- Equate before reporting: pilot every unseen item and a sample of practice items on the same people, and report the gap only after adjusting for item difficulty. Until then, show "gap not yet calibrated" instead of a number.
- Retire each unseen item for a user after first use. Track bank exhaustion per idea and say "no unseen items left for this idea".
- Show on the map which ideas have unseen coverage at all.

---

## 11. Practice items, keys and "distance" are certified by the model that wrote them (major)

**What fails.** Applied needs "a new instance from the idea's item family, with a recorded surface distance and the topic name hidden" (PRODUCT.md 4.9). For practice items, the family, surface and distance fields are written at sealing time (`learning.md` 4), by the agent in a separate context. Nothing checks them. A model can label a near-copy as "same project new code". Open-answer keys from a model can also be wrong, which marks a right user wrong. There is no item analysis: no check that an item is answerable, that its key is right, or that experienced users get it right.

**Scenario.** The subagent writes a "new instance" for idempotency keys that is the same function with a renamed variable, labelled "same project new code". The user answers right and reaches Applied. The record now claims transfer on what was recall of one function.

**Severity.** Major.

**Smallest fix.**
- Compute distance in the engine, mechanically: different file, different function (by AST hash or similar), different project ID. The model may propose a lower distance, never a higher one.
- For model-keyed items, run the key once through a second context that answers the item blind. If it disagrees with the key, the item is practice only.
- Track per-item outcomes across a user's history; flag items most "sure" answers miss as possibly bad keys, and refund the miss.

---

## 12. Explain back rewards paraphrasing the agent (major)

**What fails.** The rubric for Explain back is written by a model from the change and the agent's own explanation. Its binary points tend to follow the agent's framing. The echo flag catches answers that "nearly copy" agent text (`architecture.md` 5), not close paraphrase. So a user who restates what the agent just said scores well, and a user who explains correctly in their own terms may miss points. This is the illusion of explanatory depth in its simplest form: fluency that sounds like understanding.

**Scenario.** The agent explains a race condition. Three days later the user's review answer reuses its phrasing with new words. The grader awards every point. Asked to find the same race in other code, the user cannot.

**Severity.** Major. Same-session caps at Seen, but delayed explain items can move levels.

**Smallest fix.**
- Rubric points must be about the mechanism and its consequences, not about the words, and must include one "apply" point: predict what changes if one condition changes. The rubric author is told not to read the agent's explanation, only the diff and the tests.
- Delayed explain items always use a different instance (distance at least "same project new code"), so recall of the agent's sentence does not help.

---

## 13. On-device experiment results will mostly be noise, and the claims ladder lets the product show them (major)

**What fails.** Within-person experiments randomise idea clusters, and the outcome is unseen questions on that cluster at 21 days (`measurement.md` 3). Per user, that is a handful of binary outcomes per arm. Clusters without bank coverage are not enrolled, which in v1 is most of them. The "off" arm still gets reviews, drills and Trace items on the same cluster, and retrieval practice is itself a strong effect, so the difference being tested is small. Yet the claims ladder allows "Shows you which moves help you, measured on you" from on-device experiments, and `firsthand stats` shows per-user results.

**Scenario.** After two months a user has 4 enrolled clusters. `stats` shows explain back "on" at 2 of 2 and "off" at 1 of 2. The user concludes explain back works for them and turns Deep on. The result is chance.

**Severity.** Major.

**Smallest fix.**
- Show no per-user effect until a minimum count per arm, set from E7's power calculation. Before that, show only "collecting: N of M".
- Use on-device results only pooled across opted-in users, through the design-partner path, until the minimum is reached.
- Remove the "measured on you" rung from the claims ladder until a per-user minimum exists.

---

## 14. The Checkup will be read as a trend it cannot show (major)

**What fails.** The Checkup is once a month: one task, one seeded bug, two diffs (PRODUCT.md 9.2). That is one or two items per construct per month. Each task is a different repo with different difficulty, and nothing equates them. The map shows "its own line, by construct, with a count".

**Scenario.** Month 1: task passed, bug found. Month 2: task failed, bug not found. The user believes they got worse. The month 2 repo was harder.

**Severity.** Major. It is the only user-facing transfer measure.

**Smallest fix.**
- Pilot every Checkup task on a pooled sample and store a difficulty estimate with it. Show results against difficulty: "passed a task most pilot users found hard".
- Show no trend line until at least a minimum number of Checkups, a design default, needs to be measured. Say "one Checkup is one data point".

---

## 15. Levels depend on the surface, so parity of outcome breaks for the record (major)

**What fails.** Agent-relayed answers cap at Seen (PRODUCT.md 4.9). On T0 and T1 surfaces (Aider, Copilot in JetBrains, Codex cloud), every in-chat answer is agent-relayed. Unseen questions are served only in the terminal or verified native forms (`learning.md` 7.1), so users on those surfaces get none in chat, and cannot reach Held without leaving their agent. The spec says every outcome is reachable "in plain text plus a CLI call" (5.4), which is true, but the user on a weak surface is not told that their in-chat answers never move a level. Measurement invariance across surfaces is a guard metric (`measurement.md` 2.4), but the design builds non-invariance in.

**Scenario.** A JetBrains Copilot user answers 40 reviews in chat over a month, mostly right. Their map shows everything at Seen. They conclude the product thinks they learned nothing.

**Severity.** Major for honesty and for decision 6.

**Smallest fix.**
- At install, and on the map, say per surface: "Answers in this agent are relayed and can reach Seen. To move levels, run `firsthand review` in a terminal." Make this a conformance row.
- On those surfaces, the session-start line offers `firsthand review` in a terminal instead of an in-chat review.

---

## 16. Seen makes exposure look like progress (minor)

**What fails.** Seen is earned by explaining back, writing your line, answering with help, viewing an explainer, or self-marking (PRODUCT.md 4.9; `learning.md` 3.5). It is a level on the same ladder. The map lists "Getting there: database migrations. Seen twice." For a new user, Seen will be most of the map, and it grows with exposure alone. "Best level" shown beside "latest" also anchors users on their peak.

**Smallest fix.** Rename Seen on the map to "met" and list it apart from levels: "Met, not yet checked: database migrations." Show best level only in `map all`, not on the first view.

---

## 17. The first-session wedge contradicts the spec's own rules (minor)

**What fails.** The wedge is a first-session Trace drill on code the agent wrote this week (PRODUCT.md 2.2), and the promise says "tomorrow it remembers what you got right". But drills "never run in the same week the user met the material" (4.6), and "only delayed, unaided, new-instance performance counts" (principle 4). A Trace answer is also easy to get by running the function, which the user's terminal and agent can both do.

**Smallest fix.** State that the first-session drill is a demo and records at most Seen. Change the promise to "tomorrow it remembers what you tried", and make the first real evidence a delayed Trace on a different input a week later.

---

## 18. The user can curate the record (minor)

**What fails.** `forget <idea>` and `delete` rewrite history (PRODUCT.md 6.2). The proof pack contains "items the user chooses" (5.3). A user can remove misses and export only hits. Hiring is out of scope, which helps, but proof packs will still be shown to others.

**Smallest fix.** `forget` removes a whole idea, never single attempts. The proof pack states, in its header, how many attempts exist on each included idea and how many were included.

---

## 19. Calibration mixes immediate predictions with delayed answers (minor)

**What fails.** Predictions are "recorded for calibration only" (`learning.md` 2.1) and are offered only at Not yet or Seen, in the moment. Delayed reviews are also used for calibration. Mixing the two blurs a construct (C6) the spec keeps separate.

**Smallest fix.** Compute calibration on delayed items only, and report in-build prediction accuracy as its own line.

---

## What is already right

So the fixes above are read in context: the spec already caps agent-relayed, self-marked and asking-context answers; separates the teaching and claim instruments; refuses to combine constructs; tunes on delayed outcomes, not satisfaction; and has a claims ladder. The problems here are mostly about how much one answer can carry, and about checking the instruments themselves before trusting them.
