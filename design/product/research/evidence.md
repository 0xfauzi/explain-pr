# Evidence: assessment, measurement and proof of efficacy

Track: how the product can show, to a user and to a buyer, that people become
better engineers, and not only that they get better at its own questions.

Written 7 November 2026 for the general product (any coding agent, any
surface). Inputs read: `skills/learning-while-building/SKILL.md`,
`scripts/record.py`, `design/learning-experience/research/learning-science.md`,
`design/learning-experience/critique/learning-scientist.md`, and the headings of
the other reports in `design/product/research/`.

## How to read this report

- Each research claim carries a link. Where I read only an abstract or a
  secondary summary, I say so.
- Claims about a product, tool or harness carry [verified: source] or
  [unverified].
- No number in this report is invented. Where a value must be chosen or
  learned, it says "needs to be measured".
- "The product" means the learning layer that runs inside whatever coding
  agent the user has. "The record" means the local git repo of learning events
  (founder decision 1).

---

## Part A. The short version

### A.1 The claim we want to be allowed to make

"People who build with this product can do more without the agent, weeks
later, on problems they have not practised, than comparable people who build
with the same agent and without the product. They also lose no meaningful
amount of delivery speed."

Every word in that sentence is a measurement requirement:

| Phrase | What it forces |
|---|---|
| "do more without the agent" | Outcomes are unaided performance, not answers given with the agent present. |
| "weeks later" | Delayed tests. Immediate tests measure performance, not learning ([Soderstrom and Bjork 2015](https://pubmed.ncbi.nlm.nih.gov/25910388/), abstract). |
| "problems they have not practised" | A held-out item bank the product never uses for practice, so we can detect teaching to the test. |
| "comparable people" | Random assignment, or at minimum a within-person design. |
| "same agent" | The control is AI-assisted work, not hand coding. The question is whether the product beats plain AI use. |
| "no meaningful loss of speed" | A guard metric with a margin set in advance. |

### A.2 Ten findings that shape the measurement design

1. The founding study measured learning immediately after a one-hour task,
   with a quiz of 14 questions on conceptual understanding, code reading and
   debugging. Code writing was left out. The authors say real skill formation
   takes months and call for longitudinal studies ([Shen and Tamkin 2026,
   full text](https://arxiv.org/html/2601.20245v2)). The product's study should
   fill exactly that gap: a delayed test, over weeks, on real work.
2. In that study the high-scoring interaction patterns were
   "Generation-Then-Comprehension", "Hybrid Code-Explanation" and "Conceptual
   Inquiry" ([same source](https://arxiv.org/html/2601.20245v2)). These are
   observable in a transcript, so they can be leading indicators.
3. People misjudge how AI changes their work. In METR's trial, experienced
   developers took longer with AI allowed, yet believed afterwards that AI had
   made them faster ([METR 2025, as reported by Simon Willison](https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/)).
   Self-reported learning is therefore not evidence. The product must not
   claim efficacy from satisfaction surveys.
4. The best-known validated introductory programming test, SCS1, had a
   Cronbach's alpha of about 0.59 and was hard for students ([secondary
   summary, Parker, Guzdial and Engleman 2016](https://arxiv.org/pdf/2002.11813)).
   Even carefully built programming tests are noisy. A product-built test will
   be noisier until shown otherwise.
5. Code reading, tracing and writing are related but separable skills, and
   the literature disagrees on how strongly they correlate ([Lister et al.
   2004](https://www.cs.auckland.ac.nz/~j-hamer/ITiCSE04-wg.pdf); [Denny,
   Luxton-Reilly and Simon 2008, via a 2024 review](https://arxiv.org/pdf/2405.19460)).
   The product should report them separately, not as one score.
6. Good debuggers were mostly good novice programmers, but not all good
   programmers were good debuggers ([Fitzgerald et al. 2008](https://research.aber.ac.uk/en/publications/debugging-finding-fixing-and-flailing-a-multi-institutional-study/), abstract).
   Debugging needs its own tasks.
7. LLM graders agree with humans at rates often near human-human agreement on
   short answers, but results vary widely by model, rubric and domain, from
   near-human ([arXiv 2412.06910](https://pdf.arxiv.org/pdf/2412.06910),
   agreement 70 to 80% of cases) to poor ([Ivanova and Handschuh, CEUR](https://ceur-ws.org/Vol-3772/paper10short.pdf), kappa 0.295).
   Reliability must be measured for this product's items, not assumed.
8. LLM judges show position, verbosity and self-enhancement biases ([Zheng et
   al. 2023](https://arxiv.org/abs/2306.05685v1)), and LLM graders can be
   manipulated by text inside the answer ([Li et al. 2026, preprint](https://arxiv.org/html/2606.03090)).
   The grader must not be the same call that taught, and must treat answers as
   data.
9. When a measure carries stakes, scores rise faster than the skill
   (Campbell's law; Koretz's score inflation, [EPI volume](https://www.epi.org/?p=3203)).
   Koretz and Beguin proposed placing novel "audit" items inside the routine
   test and reading inflation from the gap ([2010](https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/)).
   This product should do the same from day one.
10. In the EU, AI systems used to evaluate learning outcomes, or to monitor
    and evaluate workers, fall in the AI Act's high-risk list (Annex III
    points 3 and 4) [unverified: secondary summary, [CASRAI](https://casrai.org/news/ai-act-high-risk-classification); check the regulation text].
    A team or employer feature that grades people is a regulated product, not
    a dashboard. This is a strong reason to keep evaluation in the user's hands.

### A.3 The proposal in one paragraph

Measure six constructs separately (code reading, debugging, design judgment,
explaining a change, transfer, calibration), each with tasks whose answers can
be checked by running code wherever possible. Seal each answer key in a git
commit before the question is shown. Grade open answers with a separate,
blind grader whose agreement with humans is measured and published. Keep a
held-out audit bank that is never used for practice, and report the gap
between practised and audit items as the product's own Goodhart alarm. Use
leading indicators (delayed unaided recall, calibration, generation before
reveal) to tune the product, and lagging indicators (unaided performance on
fresh tasks weeks later, in an unfamiliar codebase) to make claims. Before
saying "it works", run one preregistered randomised study with a delayed,
blind-graded, held-out test. Everything about a person stays local and is
shared only by that person.

---

## Part B. What "a much better engineer" means, as things we can measure

### B.1 Constructs

A construct is the skill we claim to measure. Each needs its own tasks,
because the evidence in A.2 (items 4 to 6) says these skills come apart.

| Construct | Definition | Why it matters here |
|---|---|---|
| C1 Code reading | Predict what given code does, including edge cases and failure paths, without running it. | Shen and Tamkin found AI use impaired code reading ([full text](https://arxiv.org/html/2601.20245v2)). An engineer who directs an agent must read its output. |
| C2 Debugging | From a symptom, form a hypothesis, choose a check that would test it, localise the cause and repair it. | The largest gap in Shen and Tamkin was on debugging ([Anthropic summary](https://www.anthropic.com/research/AI-assistance-coding-skills)). |
| C3 Design judgment | Choose between workable designs for a stated constraint and name the trade-off that decides it. | This is what remains the engineer's job when the agent writes most code. |
| C4 Explaining a change | Say what a change does, why, and what would break if a named part were removed. | The explain-back is the product's core act. It is also the easiest to inflate (see D.2). |
| C5 Transfer | Apply an idea in a situation that differs in surface features from every earlier case. | Without transfer, the product teaches its own repo, not engineering ([Barnett and Ceci 2002](https://pubmed.ncbi.nlm.nih.gov/12081085/)). |
| C6 Calibration | How well confidence matches correctness. | Struggling novices with AI showed an illusion of competence ([Prather et al. 2024](https://arxiv.org/abs/2405.17739)). Calibration is the skill that tells you when to check the agent. |

Not constructs, and never reported as learning: number of questions answered,
streaks, lines of code written, time in the product, topics "covered".

### B.2 Levels of evidence per construct

The current engine has four levels: not yet, with help, recalls, transfers
(`record.py` `LEVEL_NAMES`). The general product should keep a ladder of this
kind but tie each rung to the kind of evidence, not to a count:

| Rung | Evidence required | Can claim |
|---|---|---|
| Seen | Explained to the user, or the user explained it back in the same session. | Nothing about learning. Exposure only. |
| Recalled | Unaided, correct, at a gap of at least a few days, on a sealed item. | Retention of this idea. |
| Applied | Unaided, correct, on an item with a recorded surface distance from all earlier items and feedback. | Near transfer. |
| Held | Applied again on an audit item (never practised, Part E) at a longer gap. | The strongest per-person claim the product can make. |

The earlier critique already showed why the same-session explain-back cannot
count as unaided evidence ([learning-scientist critique, B1](../../learning-experience/critique/learning-scientist.md)).
The engine already encodes a seven-day durability gap
(`DURABLE_AFTER_DAYS = 7` in `record.py`). The gap length is a starting value
that needs to be measured against delayed outcomes.

---

## Part C. Task types that measure the constructs

Principle: prefer tasks whose answer is checked by running something. Use
language-model grading only where no executable check exists, and then under
the protocol in Part D.

### C.1 Task catalogue

| Task | Construct | How it is graded | Notes |
|---|---|---|---|
| Predict the output | C1 | Run the code. Compare. | The observable must be deterministic. Random jitter, timing and network calls make the key unstable (critique M1). |
| Trace the state | C1 | Run with a probe that prints the state. Compare. | Good for concurrency and data flow. |
| Explain in plain English | C1, C4 | Blind LLM grader against sealed rubric points, or code-generation grading (below). | Code-generation grading: a model writes code from the learner's explanation and tests are run on it ([Smith and Zilles 2024](https://arxiv.org/pdf/2311.14903)). Agreement with humans was moderate and the method was more lenient on low-level descriptions (search summary of the same paper). |
| Hypothesis first | C2 | The learner writes a cause and a check before any code is shown. The agent runs the check. Graded on whether the check would discriminate. | Localisation is the hardest part. Do not show a small excerpt with one odd line (critique M2.4). |
| Seeded bug | C2 | A bug is injected into a copy of real code. Tests fail. The learner localises and repairs. Graded by tests plus whether the stated cause matches the injected one. | Bugs can be generated by mutation operators. The mutation testing literature gives a catalogue ([Jia and Harman 2011, IEEE TSE](https://doi.org/10.1109/TSE.2010.62)) [unverified: cited from memory, check]. Seeded bugs are never left in the user's real branch. |
| Your line | C2, C3, C5 | One marked line or test in the real build, written by the user. Graded by the project's tests and a reviewer pass. | Founder decision 2. This is the most valid task in the product because it is the real job. See C.3. |
| Design choice | C3 | Two or three workable designs and a constraint. The learner picks and names the deciding trade-off. Graded on the trade-off, not the pick. | Rubric must list which trade-offs count. Choice alone is recognition. |
| Review a diff | C1, C2, C3 | A diff with zero or more real defects. The learner lists defects and severity. Graded by precision and recall against the sealed list. | Include clean diffs, so "always find something" is penalised. |
| Change explain-back | C4 | Blind grader. | Same session: counts as Seen only. |
| Fresh-codebase task | C5 | An unfamiliar small repo, a task that uses an idea the learner has met elsewhere, no topic name shown. Graded by tests. | The main lagging outcome. Topic names on transfer items give away the principle (critique M3; [Barnett and Ceci 2002](https://pubmed.ncbi.nlm.nih.gov/12081085/)). |
| Confidence with every answer | C6 | Scored with a proper scoring rule (Part F). | Already in the skill's ground rules. |

### C.2 Item families and distance

Each topic should have an item family: several items with the same deep
structure and different surface features. The sealing step records, per item:

- the deep structure (one sentence, the idea being tested);
- the surface features (domain object, code shape, failure mode);
- a distance note: which earlier items and which feedback it differs from, and
  how;
- a difficulty tag, set by the author and later replaced by an estimate from
  outcomes (needs to be measured).

Why: without distance notes, "applied" credit goes to near copies of feedback
the learner just read (critique M4). Without difficulty tags, a drop in score
mixes forgetting with a harder item (critique minor 2).

### C.3 "Your line" as the anchor task

Founder decision 2 is a requirement, and it is also the best measurement in
the product, for three reasons:

1. It is the real job, so its validity for "better engineer" is high by
   construction. Work-sample style assessments remain among the stronger
   predictors of job performance, although a 2022 reanalysis lowered most
   validity estimates ([Sackett et al. 2022](https://ink.library.smu.edu.sg/lkcsb_research/6894), abstract). I did not find the revised
   work-sample figure; needs to be checked in the paper.
2. The answer key is the test suite, which is executable and hard to game by
   wording.
3. It produces an artefact in the user's own git history, which the user can
   later show to others (Part I).

Measurement rules for your line:

- Record whether the line passed the tests on the first try, the hint level
  used, and whether the agent later changed it.
- Record whether the agent saw the user's line before the user committed it.
  If the agent wrote any part of it, it is not unaided.
- Do not grade by test pass alone. A line can pass weak tests. A blind reviewer
  pass checks the line against the sealed intent.
- Time to write the line is a guard metric, not an outcome.

---

## Part D. Grading open answers with a language model

### D.1 What the studies say

| Source | Setting | Finding | How I read it |
|---|---|---|---|
| [Smith and Zilles 2024](https://arxiv.org/pdf/2311.14903) | 42 explain-in-plain-English questions, 6,380 responses | Code-generation grading reached moderate agreement with other methods, more lenient on low-level descriptions | Search summary |
| [arXiv 2412.06910](https://pdf.arxiv.org/pdf/2412.06910) | Short answers, binary rubric items, GPT-4o | Agreed with human graders in 70 to 80% of cases, close to human-human agreement. Adding explanation to each rubric item helped. | Abstract and search summary. Note: an agreement rate is not a kappa. |
| [Ivanova and Handschuh, CEUR Vol-3772](https://ceur-ws.org/Vol-3772/paper10short.pdf) | Small study, two humans and an LLM | Kappa 0.295 for the LLM, below human-human | Search summary |
| [arXiv 2503.23989, summary](https://alphaxiv.org/overview/2503.23989v3) | 80 Java submissions | Question-specific rubrics agreed with humans much better than generic ones. Some setups were stricter than humans. | Secondary summary |
| [Byun et al., arXiv 2511.10819](https://arxiv.org/html/2511.10819v2) | Quiz and report grading | Correlation with humans up to 0.98, exact agreement in 55% of quiz cases | Search summary |
| [Zheng et al. 2023](https://arxiv.org/abs/2306.05685v1) | LLM as judge of chat answers | Position, verbosity and self-enhancement biases. Strong judges reach over 80% agreement with human preference. | Abstract |
| [Li et al. 2026, preprint](https://arxiv.org/html/2606.03090) | Student-side prompt injection into graded answers | Prompt injection is a real threat to LLM grading | Search summary |
| [arXiv 2601.08843](https://www.arxiv.org/pdf/2601.08843) | Rubric-conditioned grader | Resilient to injection, sensitive to synonym swaps | Search summary |

Two lessons hold across these: rubrics written per question, with each point
explained, do much better than generic rubrics; and agreement varies so much
by setting that only a measurement on this product's own items counts.

### D.2 Threats specific to this product

1. **The teacher grades its own student.** The same agent that explained the
   idea, and sometimes wrote the code, then grades the explanation. It knows
   what it meant, so it can read intent into a vague answer. This is the
   self-enhancement pattern in a new form.
2. **Leakage from the session.** The answer may echo text the agent wrote
   minutes earlier. A grader that sees the session will reward the echo.
3. **Verbosity.** Long answers that list many terms can collect rubric points
   without a model of the mechanism.
4. **Injection.** An answer can contain text addressed to the grader. On a
   personal learning tool the user mostly harms only themselves, but in a team
   or study setting this matters.
5. **Surface effects.** Answers typed on a phone are shorter than answers typed
   at a desk. A grader that rewards length will score phone answers lower for
   the same knowledge. This needs to be measured across surfaces (Part H.3).
6. **Model drift.** The grader model changes when the user's agent or vendor
   changes. Founder decision 6 (all surfaces) means many graders. Scores from
   different graders are not comparable until shown to be.

### D.3 Grading protocol

1. **Seal first.** The rubric is a list of points, each binary, each with one
   line saying what counts and one example that does not. Sealed before the
   question (Part E).
2. **Blind, separate grader.** Grading is a fresh model call that sees only:
   the question, the sealed rubric, the code excerpt the question showed, and
   the answer. It does not see the session, the confidence, the hint level,
   the user's history or name.
3. **Answer as data.** The answer is passed in a delimited field with an
   instruction that it may contain instructions and must not be obeyed. A
   cheap pre-check flags answers that address the grader.
4. **Point by point.** The grader returns, per rubric point, met or not met
   and the quoted span of the answer that meets it. A point with no quoted span
   is not met. This makes grades auditable by the user.
5. **Echo check.** If a quoted span is a near copy of text the agent wrote in
   the same session, the point counts but the attempt cannot raise the rung.
6. **Executable before judged.** Where an answer can be turned into code or a
   check (prediction, hypothesis, code-generation grading), run it first. The
   model grades only what cannot be run.
7. **Disagreement.** Grade twice with order of rubric points shuffled, or with
   two models when available. If they differ, the attempt is "uncertain": it
   is shown to the user with both readings and does not move the rung.
8. **User dispute.** The user can dispute any grade in one action. Disputes are
   logged with the grade. A dispute never changes the grade by itself; it
   sends the item to a second grading and, in a study, to a human.
9. **Grader identity in the record.** Each grade stores the grader model and
   version and the rubric hash, so grades from different graders can be
   compared or excluded.

### D.4 Measuring the grader

Before any efficacy claim, and again at every grader model change:

- Build a calibration set: real answers (consented), each graded by two
  trained humans against the sealed rubric.
- Report Cohen's kappa human-human and model-human per rubric point and per
  task type. Report leniency: the share of points the model awards that
  humans did not, and the reverse.
- Report agreement separately for phone-length and desk-length answers.
- Publish the numbers with the grader version. If model-human agreement is
  below human-human on a task type, that task type's grades do not count
  toward lagging outcomes. The threshold needs to be set in advance and
  justified; I do not propose a number here.

---

## Part E. Sealed answer keys and the audit bank

### E.1 Why seal

If the key is written after the answer is seen, the grader adapts the key to
the answer. The current skill already requires the rubric before the question
(`SKILL.md`, ground rule 2) and records "rubric written after the question"
when this was missed. The general product should make sealing verifiable,
not just a rule.

### E.2 How to seal with the founder's local git record

- At sealing, the product writes the rubric, the item metadata (C.2) and a
  random salt to the record, and commits it. The question is shown only after
  the commit exists.
- The question card carries the short hash of the rubric. The grade later
  cites the same hash. Anyone reading the record can check that the key
  predates the answer by commit order. Git identifies objects by a hash of
  their content [verified: [Git Internals, Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)].
- Commit order on a local repo can be rewritten by its owner. That is fine for
  a personal record: sealing protects the user from a lenient grader, not the
  world from the user. For anything shared (Part I) or for a study, the hash of
  the sealed key is also sent, at sealing time, to a place the user does not
  control (the study server, or a signed timestamp). That is an opt-in step and
  is the only network call in the sealing path.
- The user can see the key only after answering. In a local tool a determined
  user can open the file first. The product should not try to stop this. It
  should record whether the key file was read before the answer when the
  harness can tell [unverified: depends on the harness exposing file reads],
  and say plainly in the interface that peeking makes the record less true for
  the user.

### E.3 The audit bank

Following Koretz and Beguin's self-monitoring assessment idea
([2010](https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/);
trials reported in [2016](https://informahealthcare.com/doi/abs/10.1080/10627197.2016.1236674)):

- A bank of items per construct that the product never uses for practice,
  never shows in feedback, and never lets the teaching agent see.
- Items are written by people, in small self-contained code, so they work in
  any repo and any language family the product supports. Language coverage
  needs to be decided.
- A small share of scheduled reviews, inside the founder's cap of three a day
  (decision 3), are audit items. They look the same as practice items. The
  share needs to be set by the study; it costs practice slots.
- The product reports per user, and in aggregate for studies: the gap between
  performance on practised items and on audit items for the same construct.
  A growing gap means the product is teaching its own questions. This is the
  product's Goodhart alarm.
- Audit items are retired once used by a person, and retired globally if they
  leak (for example, published). Bank size per construct needs to be measured
  against how many users and how long they stay.

---

## Part F. Calibration

### F.1 What to compute

| Measure | What it says | Source |
|---|---|---|
| Brier score | Mean squared error of confidence as a probability. Lower is better. Decomposes into calibration and resolution. | [Brier score](https://en.wikipedia.org/wiki/Brier_score) |
| Calibration by level | For each confidence level, the share correct, against the level's target. | Gardner-Medwin's certainty-based marking gives thresholds for three levels: about 67% and 80% ([UCL LAPT](https://www.ucl.ac.uk/lapt/REAP_CBM.htm)) |
| Resolution | Whether higher confidence goes with more correct answers at all, regardless of level. Goodman-Kruskal gamma is common in metamemory research. | [Goodman and Kruskal's gamma](https://en.wikipedia.org/wiki/Goodman_and_Kruskal%27s_gamma) |
| Sure misses | Answers marked sure that were wrong, listed, with whether each was later answered right. | Hypercorrection: confident errors are corrected more readily after feedback ([Metcalfe 2017](https://doi.org/10.1146/annurev-psych-010416-044022)) |

### F.2 Rules

- Map the three words the user sees to probabilities and say so: "Guess" under
  1 in 2, "Fairly sure" about 2 in 3, "Sure" 4 in 5 or more. These follow the
  CBM thresholds cited above.
- Score with the CBM marks (right 1, 2, 3; wrong 0, -2, -6, from [UCL
  LAPT](https://www.ucl.ac.uk/lapt/REAP_CBM.htm)) because they are a proper
  scoring rule: honesty is the best policy. Show the score only to the user.
- Below a minimum count per level, show "too few answers to tell". The
  minimum needs to be measured; the earlier critique suggested about ten as a
  starting point (critique M9).
- "I do not know" is valid evidence on reviews and is never counted in
  calibration.
- Calibration must be computed on delayed items only. Judgments made right
  after study are inflated ([Rhodes and Tauber 2011](https://doi.org/10.1037/a0021705)).
- Calibration on AI output is a second, separate measure worth building: when
  the agent proposes a change, the user can state "I expect this is correct /
  I would check this". Compare to the outcome (tests, later revert). This is
  closer to the job than calibration on quiz items. It needs a design pass and
  measurement.

---

## Part G. Goodhart and teaching to the test

Every measure in this report becomes a target once the user, the product team
or an employer cares about it. The design has to assume that.

| Risk | Example | Guard |
|---|---|---|
| The product team optimises the record | A feature raises "recalled" counts because items get easier. | Difficulty tags; audit-bank gap (E.3); lagging outcomes judged by people outside the feature team. |
| The user optimises the record | Answers in the agent's words, peeks at keys, skips hard items. | Echo check (D.3.5); peeking recorded; skipped items stay due; the record is framed as the user's own map, never a score to show. |
| Practice narrows to what is graded | Items cluster on easy-to-grade predictions; design judgment withers. | Report per construct; track the share of attempts per construct; a construct with no recent evidence shows "no evidence", not a level. |
| An employer uses the record for evaluation | Managers ask for levels. | No manager view of individual records (Part I). Levels are not exportable as scores, only as evidence the user chooses. |
| Engagement stands in for learning | Daily active use rises; learning does not. | Engagement metrics are guard metrics only. No streaks. [Duolingo's own streak research](https://blog.duolingo.com/duolingo-streak-research/) reports engagement, not learning. |
| The LLM grader is gamed | Long, term-dense answers. | Point-by-point quoted spans; verbosity check in grader audits. |

Two structural rules:

1. **Separate the teaching instrument from the claim instrument.** Practice
   items tune the product. Audit items and the fresh-codebase task support
   claims. The teaching agent never sees the claim instrument.
2. **Report the gap, not just the level.** Every chart that shows a practised
   score next to it shows the audit score for the same construct.

---

## Part H. Measurement framework

### H.1 Leading indicators (weeks; use them to tune the product)

| Indicator | Definition | Source in the record | What it can and cannot claim |
|---|---|---|---|
| L1 Generation before reveal | Share of learning moments where the user committed an answer before seeing the agent's. | Attempt events with timestamps relative to reveal | Measures the behaviour that preserved learning in Shen and Tamkin. Does not show learning. |
| L2 Delayed unaided recall | Share correct at the first scheduled review after Seen, unaided, sealed, blind-graded. | Review attempts | Retention of practised ideas. Inflates if items are easy. |
| L3 Retention curve | Correct rate at each interval step (the engine uses 3, 7, 21, 60, 180 days, `record.py`). | Review attempts | Whether the schedule works. Lets intervals be tuned from data, as `record.py` already intends. |
| L4 Calibration | Brier score, calibration by level, sure-miss correction rate, on delayed items. | Attempts with confidence | Metacognitive skill. Needs enough items. |
| L5 Your line first-try rate | Share of user-written lines that pass the tests on first try, unaided. | Your-line events, test results | Closest leading signal to the real job. Depends on test quality. |
| L6 Hint depth | Mean highest hint level used, by construct, over time. | Attempt hint level | Falling hint depth suggests growing independence. Can fall because items got easier. |
| L7 Audit gap | Practised minus audit performance, by construct. | Audit attempts | Goodhart alarm. |

### H.2 Lagging indicators (months; use them to make claims)

| Indicator | Definition | Notes |
|---|---|---|
| G1 Held-out unaided score | Score on a fixed battery of audit items across C1 to C6, taken without the agent, weeks after the period of use. | Primary outcome for the study (Part J). |
| G2 Fresh-codebase task | Unaided completion and correctness on a small unfamiliar repo task that needs ideas the user practised, with no topic names. | Measures transfer. Graded by tests plus blind review. |
| G3 Debugging on seeded bugs | Localisation correct and time to localise, unaided, on seeded bugs in an unfamiliar repo. | Time is secondary to correctness. |
| G4 Agent-output judgment | Precision and recall at finding real defects in agent-written diffs, including clean diffs. | Close to the daily job with an agent. |
| G5 Real-work signals (opt-in, user-held) | In the user's own repos: share of the user's commits later reverted, rework on lines the user wrote, review comments received. | Noisy and confounded by team and project. Use only within-person over time, never across people. Never sent anywhere without the user's explicit action. |

### H.3 Guard metrics (must not get worse beyond a margin set in advance)

| Guard | Why |
|---|---|
| Task completion time with the product on versus off | The product must not tax delivery. Prior evidence on AI and speed points both ways: faster on a greenfield task ([Peng et al. 2023](https://arxiv.org/abs/2302.06590?context=cs), 55.8% faster), slower on mature repos ([METR 2025, summary](https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/)). Measure, do not assume. |
| Interruptions per task and time to resume | The skill caps interruptions (`SKILL.md`, ground rule 9). Check the cap holds on every surface. |
| Opt-out and "just do it" rate | High rates mean the product is a tax. Rising rates over time are worse than high flat rates. |
| Reminder dismissals | Founder decision 7 caps reminders at one a day. Measure whether even that one is ignored. |
| Delivery stability for teams (opt-in, aggregate) | AI adoption was associated with lower delivery stability in DORA 2024 ([Google announcement](https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report)). If the product is sold to teams, it should not be associated with worse stability. Correlational. |
| Measurement invariance across surfaces | The same item answered on phone, CLI and IDE should score the same for the same person. If not, scores carry surface noise. Founder decision 6 makes this a requirement. Needs to be measured. |

### H.4 What each audience sees

| Audience | Sees | Never sees |
|---|---|---|
| The user | All of H.1, H.2 when taken, their own audit gap, every grade with quoted spans and the sealed key. | Anything about other people. |
| The product team | Aggregates from users who opted into research, with minimum group sizes. | Individual records, answers or code. |
| A buyer (team lead, employer) | The published study results, the grader audit numbers, aggregate opt-in outcomes for their team above a minimum group size, and any evidence a user chooses to share. | Any individual's levels, attempts, misses or calibration. |

---

## Part I. Ethics: consent, no surveillance

### I.1 Principles

1. **The record belongs to the user.** Founder decision 1 already puts it in a
   local git repo with no remote unless asked. Measurement design must not
   create a second, hidden record. All telemetry is off by default.
2. **Learning is not evaluation.** The product records misses honestly so the
   user can learn. That record must never become evidence against the user.
   This matches the socio-critical point that learning analytics serves an
   unequal power relation unless designed otherwise ([Slade and Prinsloo
   2013](https://oro.open.ac.uk/36594), abstract).
3. **Consent is specific and revocable.** Research participation is a separate
   opt-in from using the product, names exactly what leaves the machine, shows
   the user the payload before each send, and can be withdrawn with deletion of
   what was sent.
4. **Data minimisation.** For research, send derived events (item id, construct,
   outcome, confidence, hint level, gap in days, grader version), never code,
   answers or repository names. Answers for grader audits are a separate,
   explicit donation, one answer at a time, reviewed by the user.
5. **No keystroke, screen or attention tracking.** The product measures what
   the user chose to answer, not how they behave between answers.
6. **No individual reports to employers.** A team plan can show aggregates
   above a minimum group size (needs to be set; small teams make aggregates
   identifying). A user can choose to share a specific piece of evidence.

### I.2 The proof pack (user-held evidence)

A user who wants to show growth, for a job application or a promotion case,
can export a proof pack: a selection of sealed items, their answers, the
grades with quoted spans, the rubric hashes and, if they opted into external
timestamping, the timestamps. The user picks what goes in. The pack shows
evidence, not a level. This gives employers something they can check without
giving them a surveillance channel.

### I.3 Regulatory note

If the product grades learners and the results steer what they learn next, it
may fall under the EU AI Act's high-risk category for education; if an
employer uses it to evaluate workers, under the employment category
[unverified: secondary summaries at [CASRAI](https://casrai.org/news/ai-act-high-risk-classification) and [Hopsworks](https://hopsworks.ai/faq-ai-act/what-are-examples-of-specific-ai-applications-that-would-be-considered-high-risk-under-the-aia); dates of application differ between sources]. Legal review is needed
before any team or employer plan ships. The design choices in I.1 (user-held
records, no individual employer view) reduce this exposure but do not settle it.

---

## Part J. Experiments inside the product

### J.1 Constraint: the record is local

Founder decision 1 rules out a central analytics database by default. Two
designs work with it.

**Within-person, topic-level randomisation (no server needed).** When a new
topic is created, the product flips a seeded coin to assign it to condition A
or B of the current experiment (for example, explain-back after the build, or
not). The assignment is sealed in the record. Outcomes are the delayed audit
items for that topic. Each user is their own control, which removes most
between-person noise. Results can be computed locally and shown to the user.
Risks: spillover between topics that share ideas; the user may change
behaviour on topics they know are in a condition, so conditions should not be
shown on the card.

**Opt-in research cohort.** Users who opt in send the minimal events in I.1.4.
This allows between-person experiments on features that cannot be split by
topic (reminder timing, onboarding, the daily cap).

### J.2 What to test first

Each needs a one-line hypothesis, a primary outcome and a stopping rule written
before it starts.

| Experiment | Unit | Primary outcome |
|---|---|---|
| Explain-back versus none | Topic | Unaided correct at first review and on audit at 21 days |
| Hypothesis before code versus code first in drills | Topic | G3-style localisation on audit items |
| Your line offered versus not | Topic | Audit performance on that topic; task time (guard) |
| Topic name shown versus hidden on transfer items | Item | Correct rate on audit transfer items |
| Daily cap of 3 versus a different cap | Person (cohort) | Audit performance at a fixed date; dismissals (guard). Decision 3 is the default; testing it does not change it for users who did not opt in. |
| Reminder at chosen time versus none | Person (cohort) | Reviews completed; audit performance |

### J.3 Sample size, honestly

I cannot say how many users each experiment needs, because the effect sizes
are unknown for this product. Lehr's rule gives a rough per-arm count for a
two-arm comparison at 80% power and two-sided alpha 0.05: about 16 divided by
the squared standardised effect ([Columbia notes, after van Belle](https://www.columbia.edu/~cjd11/charles_dimaggio/DIRE/styled-4/code-12/)).
For illustration only: an effect of d = 0.5 gives about 64 per arm; Shen and
Tamkin's observed d = 0.738 ([Anthropic summary](https://www.anthropic.com/research/AI-assistance-coding-skills)) gives about 30 per
arm, close to the 26 per arm they ran ([full text](https://arxiv.org/html/2601.20245v2)).
Within-person designs need fewer people for the same precision, by an amount
that depends on the correlation between a person's topics, which needs to be
measured. Delayed tests lose participants; the loss rate needs to be measured
in a pilot and added to the target.

### J.4 Delayed post-tests in a product

- Schedule them as ordinary reviews so they cost no extra step, within the
  daily cap.
- Fix the delay per experiment in advance. Do not analyse the first week and
  stop early because it looks good.
- Report who did not take the delayed test, and test whether they differ
  between arms.

---

## Part K. The minimum study before claiming efficacy

### K.1 Design

A preregistered, randomised, two-arm study.

- **Participants.** Working developers and advanced students who already use
  a coding agent. Recruit across at least two agents and two surfaces, because
  the claim is for a general product (decision 6). Exclude people who already
  know the target library or codebase, checked by a pretest.
- **Task period.** Participants build features in an unfamiliar but realistic
  codebase, using a library new to them, over several sessions spread across
  weeks. One session is not enough; Shen and Tamkin name the one-hour scope as
  their main limit ([full text](https://arxiv.org/html/2601.20245v2)). The
  exact length needs to be set from a pilot.
- **Arms.** A: the agent with the product on, default settings. B: the same
  agent with the product off. Both arms may ask the agent anything. A third arm
  (hand coding) is optional; it answers a different question.
- **Primary outcome.** G1, the held-out unaided battery, taken without the
  agent, after a fixed delay from the last session (needs to be set; long
  enough to be clearly outside working memory, for example two weeks or more).
  Items drawn from the audit bank, covering C1 to C6, with code reading and
  debugging weighted because they are where the gap was largest.
- **Secondary outcomes.** G2 fresh-codebase task, G3 seeded bugs, G4 agent-output
  judgment, calibration on the battery.
- **Guard outcome.** Total time to complete the build tasks, with a
  non-inferiority margin set in advance.
- **Grading.** Executable checks where possible. Open answers graded by two
  humans blind to arm, with the LLM grader run in parallel so its agreement is
  measured on study data.
- **Analysis.** Intention to treat. Primary comparison set before data is
  seen. Report effect sizes with intervals, not only p-values. Publish the
  preregistration, items after retirement, and the code.
- **Independence.** Ideally run or audited by researchers who do not work on
  the product. A claim made by a vendor about its own product is weaker.

### K.2 Claims ladder

What the product may say at each stage.

| Evidence in hand | Allowed claim |
|---|---|
| Design based on published research only | "Designed around research on how people learn with AI." Cite the research. No efficacy claim. |
| Leading indicators from users | "Users who use it recall X at Y days." Only with the definition, and with the audit gap shown. |
| Within-product experiments | "In our users, feature F improved delayed recall of practised topics." Not a claim about engineering skill. |
| The K.1 study, positive on G1 | "In a randomised study, people who used it did better on a delayed, unaided test of code reading and debugging than people using the same agent without it." With the effect size and the study link. |
| Replication, independent, with G2 to G4 | "People who use it become better engineers," with scope stated (which skills, which population, how long). |

Marketing copy on `docs/index.html` should be checked against this ladder
before each release.

---

## Part L. Founder decisions checked against measurement needs

| Decision | Effect on measurement | Verdict |
|---|---|---|
| 1. Local git record, no remote by default | Sealing is verifiable locally (E.2). Research needs a separate opt-in export. Studies need external timestamping. | Keep. It also makes the ethics case strong. |
| 2. Your line | The most valid task in the product (C.3). | Keep, and treat as the anchor measure. |
| 3. At most 3 due items a day | Limits the number of audit items and delayed tests per person. Measurement density is lower, so studies need more people or longer. | Keep as the default. Allow study participants to opt into the same cap, and draw audit items from within it. |
| 4. One confirmation tap on the phone where no-tap is impossible | Neutral for measurement. Confidence capture must still be part of the answer, not an extra tap. | Keep. |
| 5. Letter shortcuts off | Neutral. | Keep. |
| 6. Parity on all surfaces | Creates the measurement invariance problem (H.3) and many grader models (D.2.6). | Keep, but parity must include grading: same rubric format, same blind grading step, and grader version recorded everywhere. I could not verify which harnesses let a skill make a separate, session-blind model call [unverified]; where none exists, grading must fall back to executable checks or defer to a surface that can. |
| 7. One reminder a day at a chosen time | Delayed tests depend on users returning. Fine for within-person designs. | Keep. Do not add reminders for studies. |

No decision is challenged on evidence. Decision 6 needs the addition above to
hold for measurement.

---

## Part M. Design rules from this track

1. Report six constructs separately; never one combined "skill score".
2. Prefer executable grading. Use a model only for what cannot be run.
3. Seal every key in a commit before the question appears; cite its hash on
   the grade.
4. Grade in a separate, blind call that sees question, key, shown code and
   answer only.
5. Every awarded rubric point quotes the span of the answer that earns it.
6. Same-session answers count as Seen, never as unaided evidence.
7. Keep an audit bank the teaching agent never sees, and always show the
   practised-versus-audit gap.
8. Transfer items carry a recorded surface distance and never show the topic
   name before the answer.
9. Calibration uses a proper scoring rule, delayed items only, and says "too
   few answers" below a minimum.
10. Engagement numbers are guard metrics, never success metrics.
11. Claims follow the ladder in K.2; marketing is checked against it.
12. No individual record leaves the machine without the user's action;
    employers get aggregates or user-chosen evidence only.
13. Measure grader agreement on this product's items and publish it with the
    grader version.
14. Test measurement invariance across surfaces before comparing scores across
    them.

---

## Part N. Open questions

1. How many audit items per construct are needed for a user base of a given
   size and lifetime before items leak or repeat? Needs to be measured.
2. Which harnesses allow a session-blind grading call from inside a skill or
   plugin? [unverified for every surface]
3. What minimum count per confidence level makes calibration stable enough to
   show? Needs to be measured.
4. What delay should the primary outcome use? Longer is more convincing and
   loses more participants.
5. Can real-work signals (G5) ever be made comparable across people, or only
   within one person over time?
6. Does the audit-bank share of the three daily items reduce learning enough to
   matter? Needs an experiment.
7. Who runs the K.1 study, and can it be independent of the product team?
8. What legal review is needed for team plans under the EU AI Act and similar
   rules?

---

## Sources

- Shen and Tamkin 2026, [arXiv abstract](https://arxiv.org/abs/2601.20245), [full text](https://arxiv.org/html/2601.20245v2), [Anthropic summary](https://www.anthropic.com/research/AI-assistance-coding-skills)
- METR 2025, [summary by Simon Willison](https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/), [InfoWorld](https://www.infoworld.com/article/4020931/ai-coding-tools-can-slow-down-seasoned-developers-by-19.html)
- Peng et al. 2023, [arXiv 2302.06590](https://arxiv.org/abs/2302.06590?context=cs)
- Prather et al. 2024, [arXiv 2405.17739](https://arxiv.org/abs/2405.17739)
- Soderstrom and Bjork 2015, [PubMed](https://pubmed.ncbi.nlm.nih.gov/25910388/)
- Parker, Guzdial and Engleman 2016 (SCS1), via [arXiv 2002.11813](https://arxiv.org/pdf/2002.11813); [FCS1 paper](https://people.cs.vt.edu/~kafura/CS6604/Papers/FCS1-Assessment-CS1-Knowledge.pdf)
- Lister et al. 2004, [ITiCSE working group report](https://www.cs.auckland.ac.nz/~j-hamer/ITiCSE04-wg.pdf)
- Denny, Luxton-Reilly and Simon 2008, [DBLP](https://dblp.dagstuhl.de/rec/conf/icer/DennyLS08.html); later review in [arXiv 2405.19460](https://arxiv.org/pdf/2405.19460)
- Fitzgerald et al. 2008, [Aberystwyth record](https://research.aber.ac.uk/en/publications/debugging-finding-fixing-and-flailing-a-multi-institutional-study/)
- Barnett and Ceci 2002, [PubMed](https://pubmed.ncbi.nlm.nih.gov/12081085/)
- Smith and Zilles 2024, [arXiv 2311.14903](https://arxiv.org/pdf/2311.14903)
- LLM short-answer grading, [arXiv 2412.06910](https://pdf.arxiv.org/pdf/2412.06910); [arXiv 2511.10819](https://arxiv.org/html/2511.10819v2); [CEUR Vol-3772](https://ceur-ws.org/Vol-3772/paper10short.pdf); [arXiv 2503.23989 summary](https://alphaxiv.org/overview/2503.23989v3)
- Zheng et al. 2023, [arXiv 2306.05685](https://arxiv.org/abs/2306.05685v1)
- Prompt injection on graders, [arXiv 2606.03090](https://arxiv.org/html/2606.03090); [arXiv 2601.08843](https://www.arxiv.org/pdf/2601.08843); [MDPI Computers 15/1/55](https://www.mdpi.com/2073-431X/15/1/55)
- Koretz, score inflation, [EPI volume](https://www.epi.org/?p=3203); [Brookings review](https://www.brookings.edu/articles/the-costs-of-misusing-test-based-accountability-in-schools)
- Koretz and Beguin 2010, [Princeton record of the SMA pilots](https://collaborate.princeton.edu/en/publications/auditing-for-score-inflation-using-self-monitoring-assessments-fi/); [2016 follow-up](https://informahealthcare.com/doi/abs/10.1080/10627197.2016.1236674)
- Sackett et al. 2022, [SMU record](https://ink.library.smu.edu.sg/lkcsb_research/6894); [SIOP commentary](https://www.siop.org/tip-article/is-cognitive-ability-the-best-predictor-of-job-performance)
- Gardner-Medwin, certainty-based marking, [UCL LAPT](https://www.ucl.ac.uk/lapt/REAP_CBM.htm)
- [Brier score](https://en.wikipedia.org/wiki/Brier_score); [Goodman and Kruskal's gamma](https://en.wikipedia.org/wiki/Goodman_and_Kruskal%27s_gamma)
- Metcalfe 2017, [DOI](https://doi.org/10.1146/annurev-psych-010416-044022)
- Rhodes and Tauber 2011, [DOI](https://doi.org/10.1037/a0021705)
- Jia and Harman 2011, mutation testing survey, [DOI](https://doi.org/10.1109/TSE.2010.62) [unverified]
- DORA 2024, [Google announcement](https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report)
- Duolingo, [streak research](https://blog.duolingo.com/duolingo-streak-research/)
- Slade and Prinsloo 2013, [Open University record](https://oro.open.ac.uk/36594)
- EU AI Act Annex III, secondary: [CASRAI](https://casrai.org/news/ai-act-high-risk-classification), [Hopsworks](https://hopsworks.ai/faq-ai-act/what-are-examples-of-specific-ai-applications-that-would-be-considered-high-risk-under-the-aia)
- Lehr's rule, [Columbia notes after van Belle](https://www.columbia.edu/~cjd11/charles_dimaggio/DIRE/styled-4/code-12/); [Lehr 1992 PDF](https://jhanley.biostat.mcgill.ca/c607/ch07/16_s_sq_over_d_sq.pdf)
- [Git Internals, Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- Repo inputs: `skills/learning-while-building/SKILL.md`, `skills/learning-while-building/scripts/record.py`, `design/learning-experience/critique/learning-scientist.md`
