# Learning science for learning while building

Research track: how to put learning into real work without breaking flow.
Date: 2026-11-07. Author: research agent 1 of 5 (learning science and interaction research).

This report turns research on interruptions, flow, pretesting, retrieval, spacing, calibration, feedback, worked examples, dashboards and gamification into design rules for the learning-while-building skill and its surfaces (chat, terminal, local page, hosted page, explainers). Each rule has a citation and an evidence label.

## How to read the evidence labels

| Label | Meaning |
|---|---|
| **Strong** | Several experiments or a meta-analysis, effect replicated, mechanism understood. |
| **Moderate** | Replicated in the lab or in one field study, but boundary conditions are open or the setting is far from software work. |
| **Weak** | One small study, self-report, correlational data, or company blog data on engagement, not learning. |
| **Speculative** | My inference from the research to this product. No direct test. |

Source status follows the brief's terms. "Documented" means a primary paper, official docs or a source repository that I read in abstract or full text. "Reported" means a secondary summary that I could not check against the primary text. I ran no experiments with learners in this track, so nothing below is "verified by test". Where I give a number from my own memory of a paper and did not re-read it today, I say so.

## The short version: twenty design rules

| # | Rule | Main evidence | Strength |
|---|---|---|---|
| 1 | Ask only at coarse breakpoints: before a build starts, while the agent works, and after a build passes. Never in the middle of a subtask the learner is doing. | Adamczyk and Bailey 2004; Iqbal and Bailey 2007/2008 | Strong (lab), Speculative (agent setting) |
| 2 | Use agent wait time as learning time. The prediction is asked when the agent starts a long step, and it is answered while the agent works. | Cai et al. 2015 wait-learning | Moderate |
| 3 | After any learning detour, show a one-line resume cue: what the learner was doing and the next step. | Altmann and Trafton 2002; Parnin and Rugaber 2011; DeLine/Parnin cue study | Strong (mechanism), Moderate (dev tools) |
| 4 | One question per checkpoint, and a fixed budget per task (one before, one after). The budget is visible and the learner can spend it or skip it. | Mark et al. 2008; Zuger et al. 2017; Shen and Tamkin 2026 | Moderate |
| 5 | Make the prediction about exactly what the build will show. Prequestion benefits are specific to the questioned content. | St. Hilaire, Chan and Ahn 2024 (g = 0.54 specific, near zero general) | Strong |
| 6 | After the build, put the prediction next to the outcome and name the difference. A failed prediction only pays off if the gap is then explained. | Sinha and Kapur 2021; Metcalfe 2017 | Strong |
| 7 | Explain-back is the core post-build check. The learner states why it works, in their own words, against a fixed rubric. | Bisra et al. 2018; Shen and Tamkin 2026 ("generation then comprehension" 86%) | Strong |
| 8 | Debugging drills are the highest-value drill: the learner forms the hypothesis before the agent diagnoses. | Shen and Tamkin 2026 (largest gap; "iterative AI debugging" group 24%) | Moderate |
| 9 | Keep the expanding schedule (3, 7, 21, 60, 180 days, miss returns next day). It sits on the Cepeda ridgeline for retention of months to a year. | Cepeda et al. 2008; Rawson and Dunlosky (successive relearning) | Strong (facts), Moderate (complex skills) |
| 10 | Log every review in a format a modern scheduler (FSRS) can read later, but do not switch schedulers until there are hundreds of reviews per learner. | open-spaced-repetition srs-benchmark | Documented |
| 11 | Interleave reviews across dimensions that are easy to confuse (for example retries vs idempotency, lock vs lease). | Brunmair and Richter 2019 (g = 0.42, stronger for similar categories) | Strong (lab) |
| 12 | Collect confidence before the answer is graded, every time. Treat a high-confidence miss as the most important event in the record. | Metcalfe 2017 (hypercorrection) | Strong |
| 13 | Show calibration (confidence against outcome), not just accuracy. AI users drift into an illusion of competence. | Prather et al. 2024; Lee et al. 2025 | Moderate |
| 14 | Feedback is about the task, never the person. No praise, no ranks, no comparison with others. | Kluger and DeNisi 1996 (over a third of feedback interventions lowered performance) | Strong |
| 15 | Fade support as the level rises: worked answer at "not yet", completion and hints at "with help", recall at "recalls", new situations at "transfers". | Kalyuga 2007 (expertise reversal); Margulieux and Morrison (subgoal labels) | Strong |
| 16 | Answer "how does this work" questions at once. Inquiry is the behaviour that protects skill. | Shen and Tamkin 2026 ("conceptual inquiry" 65%) | Moderate |
| 17 | No streaks, no loss framing, no guilt notifications. If consistency is shown at all, show a week view with slack and no counter that can break. | Silverman and Barasch 2023; Deci, Koestner and Ryan 1999; Duolingo blog | Moderate |
| 18 | The record page answers three questions in this order: what is due, what changed, what is the one gap. Everything else is one tap away. | Mayer coherence principle; dashboard practice | Weak to moderate |
| 19 | Retrieval happens without the agent's help on screen. Reviews hide the code and the earlier answer until the learner commits. | Bastani et al. 2025; Fan et al. 2025; testing effect literature | Strong |
| 20 | "Skip" and "just do it" always work, at once, with no cost. Autonomy is what keeps people using the tool. | Deci, Koestner and Ryan 1999; Shen and Tamkin 2026 discussion | Moderate |

The sections below give the evidence and the reasoning, then list where the evidence is weak and the cheapest experiments to close the gaps.

## 1. The problem this skill exists to solve

### 1.1 AI help can lower what people learn

| Study | Setting | Finding | Status |
|---|---|---|---|
| [Shen and Tamkin 2026, "How AI Impacts Skill Formation"](https://arxiv.org/abs/2601.20245), [Anthropic summary](https://www.anthropic.com/research/AI-assistance-coding-skills) | RCT, 52 mostly junior Python developers learning the Trio async library | AI group 50% vs hand-coding 67% on the later quiz (Cohen's d = 0.738, p = 0.01). Time gain about 2 minutes, not significant (p = 0.391). Largest gap on debugging questions. | Documented |
| Same study, interaction patterns | Qualitative clusters | Low scorers: AI delegation (39%), progressive AI reliance (35%), iterative AI debugging (24%). High scorers: generation then comprehension (86%, n = 2), hybrid code and explanation (68%, n = 3), conceptual inquiry (65%, n = 7). | Documented, small groups, associational |
| [Bastani et al. 2025, PNAS](https://papers.ssrn.com/abstract=4895486) | Field experiment, about 1,000 high school maths students | Plain GPT-4 chat raised practice scores 48% but lowered later exam scores 17% vs control. A tutor that gave hints and not answers raised practice 127% and left exam scores about equal to control. | Documented (abstract and summaries) |
| [Fan et al. 2025, BJET, "Beware of metacognitive laziness"](https://arxiv.org/abs/2412.09315) | RCT, 117 university students, essay writing | ChatGPT group had the best essays but no better knowledge gain or transfer, and less metacognitive activity. | Reported |
| [Prather et al. 2024, ICER, "The Widening Gap"](https://arxiv.org/abs/2405.17739) | Lab study, 21 novice programmers, eye tracking | Strong students used AI to go faster. Struggling students got an illusion of competence: they thought they did better than they did. | Documented (abstract) |
| [Lee et al. 2025, CHI](https://www.microsoft.com/en-us/research/uploads/prod/2025/01/lee_2025_ai_critical_thinking_survey.pdf) | Survey, 319 knowledge workers, 936 examples | More confidence in the AI went with less critical thinking. More self-confidence went with more. | Documented, self-report |

What this means for design:

- The harm is not "using AI". It is a pattern: handing off the thinking, especially diagnosis. The protective pattern is the learner generating something (a prediction, a hypothesis, an explanation) and the agent responding to it. This is the whole basis for the skill's checkpoints.
- The Bastani result is the cleanest proof that a guardrail works without losing the gains: the hint tutor kept the practice benefit and removed the exam harm. The skill's hint ladder (H0 to H3) is the same mechanism.
- The Shen and Tamkin groups are tiny (2 to 7 people each). Use them as direction, not as effect sizes. The authors also note they did not test agentic tools like Claude Code, where they expect the effect could be larger.

### 1.2 Why the obvious fix fails

The obvious fix is "quiz the user a lot". That breaks flow, people skip, and they stop using the tool. The rest of this report is about where to put a small amount of effortful thinking so that it costs little and returns a lot.

## 2. When to ask: interruptions, breakpoints and resumption

### 2.1 Evidence

| Finding | Source | Status | Strength |
|---|---|---|---|
| Interruptions at subtask boundaries cost less (performance, annoyance, blame) than interruptions mid-subtask. | [Adamczyk and Bailey 2004, CHI, "If not now, when?"](https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p271.pdf) | Documented (abstract), effect reported in later work | Strong |
| Breakpoints come in coarse, medium and fine grain. Models can detect them from activity with 69 to 87% accuracy. Deferring notifications to breakpoints cuts frustration and reaction time. Coarse breakpoints cost about the same as no interruption; fine ones raise workload and frustration. | [Iqbal and Bailey 2007](https://researchr.org/publication/IqbalB07), Iqbal and Bailey 2008 (TOCHI), summary in [Mehrotra and Musolesi survey](https://arxiv.org/pdf/1711.10171) | Reported | Strong |
| Goals decay in memory over time. Resumption is fast when a cue in the environment re-primes the suspended goal. | [Altmann and Trafton 2002, Cognitive Science](https://philpapers.org/rec/ALTMFG) | Documented (abstract) | Strong |
| Programmers often take 15 to 30 minutes to rebuild context after an interruption. They resume by returning to the last edit, re-running the program and re-reading the task. | [Parnin and Rugaber 2011, Software Quality Journal](https://sites.cc.gatech.edu/reverse/repository/resumptionstrategies.pdf) | Documented (abstract) | Moderate |
| Resumption cues (for example a view of recent edits) doubled task success over note-taking alone. | [DeLine and Parnin, "Evaluating cues for resuming interrupted programming tasks"](https://www.microsoft.com/en-us/research/publication/evaluating-cues-for-resuming-interrupted-programming-tasks/) | Reported | Moderate |
| Interrupted people work faster to compensate, with more stress, frustration and effort. Error rate did not change. | [Mark, Gudith and Klocke 2008, CHI](https://www.ics.uci.edu/~gmark/chi08-mark.pdf) | Documented (abstract) | Moderate |
| A desk light showing "busy" from keyboard and mouse activity cut interruptions by 46% in a field study with about 450 people. | [Zuger et al. 2017, CHI, FlowLight](https://researchr.org/publication/ZugerCMLFSAFKS17) | Reported | Moderate |
| People learned about 57 words in two weeks from micro-quizzes shown while waiting for a chat reply, and were most receptive right after sending a message. | [Cai, Guo, Glass and Miller 2015, CHI, Wait-learning](https://sls.csail.mit.edu/publications/2015/Cai_CHI-2015.pdf) | Documented (abstract) | Moderate |

### 2.2 The key insight for agentic building

Working with a coding agent has a rhythm that the interruption research did not have: **the human sends a request, then waits while the agent works**. That wait is a coarse breakpoint that already exists. The learner has just finished a unit of intent (the prompt) and has nothing to do until the agent returns. This is the "moment after sending a message" that Cai et al. found most receptive.

So the cheapest place to learn is not "after the work" (when the learner wants to move on) and not "before the work" (when they want to start). It is **during the agent's work**. The prediction question fills dead time. Its answer is revealed by the work the learner is waiting for. This turns the learning checkpoint from a cost into a use of time that was already lost. (Speculative: no study has tested this with coding agents. Experiment E1 below tests it.)

The second natural breakpoint is **after tests pass and before the next request**. The learner has a finished unit and a small reward (it works). The explain-back fits here. It must be short, because the next intent is already forming.

### 2.3 Design rules

- **R1. Breakpoint only.** The agent asks at three moments: when it starts a long step (prediction), when a build passes (explain-back), and at the start of a session (due reviews, if the learner opts in). It never asks mid-edit, mid-debug by the learner, or while the learner is typing a request. In a harness with hooks (Claude Code `PostToolUse`, `Stop`, `UserPromptSubmit`) these moments map to events the skill can detect.
- **R2. Wait-time prediction.** The prediction goes out together with "starting the build now". The learner answers while the agent works. If the agent finishes first, the agent holds the result summary until the prediction is in or skipped, so the outcome cannot spoil the prediction. (This last part is a product choice that needs testing: holding results could annoy. Offer "show result" as a one-tap escape.)
- **R3. Resume cue after every detour.** Any learning exchange longer than one message ends with one line that restores the build goal, for example "Back to the build: next is the retry wrapper in `client.py`." This is the Altmann and Trafton prime. On the hosted page and phone, the same cue is the top line when the learner returns.
- **R4. Visible budget.** Show the per-task budget ("1 before, 1 after") so the learner can predict the cost. Predictable interruptions cost less than surprise ones (Iqbal and Bailey's defer-to-breakpoint results; speculative transfer to this product).
- **R5. Defer, don't drop.** If a learning moment arrives at a bad time (the learner is mid-flow, sends several prompts in a row, or says "later"), queue it to the next coarse breakpoint or to the review queue. Never ask twice in one task.
- **R6. Detect flow cheaply.** Short gaps between learner prompts, several prompts without reading output, or "just do it" are signs of flow or time pressure. In those turns, skip the checkpoint and log "deferred". This is the FlowLight idea with the agent's own signals.

## 3. Flow versus desirable difficulties

These two ideas look opposed. Flow ([Csikszentmihalyi 1990](https://en.wikipedia.org/wiki/Flow_(psychology))) needs clear goals, quick feedback and a balance of challenge and skill. Desirable difficulties ([Bjork and Bjork 2011, "Making things hard on yourself, but in a good way"](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf)) says the conditions that make practice feel smooth (massed, blocked, re-reading, being shown) often produce poor long-term learning, while effortful conditions (spacing, retrieval, interleaving, generation) produce good learning and feel worse.

They can be reconciled. Flow is about the **build task**. Desirable difficulty is about the **learning moments**. The design separates them in time: keep the build in flow, and put a small, effortful retrieval or generation at the breakpoints. A prediction question has the properties of a flow task in miniature: a clear goal, quick feedback (the build answers it), and a challenge that is matched to the learner's level.

Two consequences:

- **The learner will rate the effortful moments lower than they deserve.** Bjork's work and Kornell's fluency studies show that people judge learning by how easy it felt. Do not tune the product on "did you like this question" alone. Track later retrieval. (Strong for the general effect; speculative for how big the bias is here.)
- **Difficulty must be germane.** A hard question about the core mechanism is desirable. A hard question about trivia, wording, or a file path the learner never needs is just load. The rubric should name the transferable idea, and the question should be hard only on that idea. (Moderate: cognitive load theory, Sweller.)

## 4. Before the build: prediction, pretesting and productive failure

### 4.1 Evidence

| Finding | Source | Status | Strength |
|---|---|---|---|
| Problem solving before instruction beat instruction first, with g = 0.87 after a publication bias correction, over 53 studies and 166 comparisons. Effects were larger with fidelity to the design (a real consolidation phase after the failure) and older learners; younger children and domain-general skills favoured instruction first. | [Sinha and Kapur 2021, Review of Educational Research](https://doi.org/10.3102/00346543211019105) | Reported (abstract, press) | Strong, with the caveat that adjusted effects are model-dependent |
| A guess before study helps learning of the guessed content: g = 0.54 over 97 effects in a preregistered meta-analysis. The benefit for other content in the same lesson was close to zero. | [St. Hilaire, Chan and Ahn 2024, Psychonomic Bulletin and Review](https://doi.org/10.3758/s13423-023-02353-8) | Documented (abstract) | Strong |
| Pretesting and prequestioning often help, with size depending on procedure. A three-stage account: the question changes what the learner attends to in the study that follows. | [Pan and Carpenter 2023, Educational Psychology Review](https://link.springer.com/10.1007/s10648-023-09814-5) | Documented (abstract) | Strong |
| Wrong guesses followed by feedback do not harm later memory, and often help (errorful generation). | Kornell, Hays and Bjork 2009, JEP:LMC (from memory, not re-read today) | Reported | Strong |

### 4.2 Design rules

- **R7. Predict the observable.** The prediction must be about something the build will show: which test fails first, what the log line says, what the status code is, which of two designs the agent will need. St. Hilaire's result says the benefit is specific: a prediction about X helps learn X and little else. So the question must target the one idea the task is really about.
- **R8. Close the loop, every time.** When the build finishes, show the prediction and the outcome side by side in one short block, and name the difference in one sentence with evidence (`path:line`, test output). Kapur's effect depends on the consolidation phase. A prediction that is never compared with the outcome is just a delay.
- **R9. Low stakes, explicit.** Say that a wrong prediction is expected and costs nothing. Kapur and Metcalfe both depend on errors being safe. This fits the Voice rules: no praise when right, no softening when wrong, and no penalty in the record for a wrong prediction (predictions are a separate attempt type from recall).
- **R10. Make prediction cheap to enter.** Offer two to four concrete options plus "other" when the domain allows it, plus a confidence chip. A one-tap answer on the phone, a single key in the terminal. Free text stays available. (Speculative: multiple-choice prequestions are what most of the St. Hilaire studies used, so this keeps the format close to the evidence.)

## 5. After the build: explain-back and generation

| Finding | Source | Status | Strength |
|---|---|---|---|
| Prompting learners to explain to themselves improves learning, with a moderate positive effect over 64 studies and about 6,000 participants, and the effect holds when time on task is controlled. | [Bisra et al. 2018, Educational Psychology Review](https://doi.org/10.1007/s10648-018-9434-x); I recall the overall effect as about g = 0.55 but did not confirm the number today | Documented (abstract) | Strong |
| The best-scoring AI users generated code, then asked follow-up questions to understand it. | Shen and Tamkin 2026 | Documented | Weak (n = 2) but in direction of the strong literature |
| Generating an answer beats reading it (generation effect). | Slamecka and Graf 1978; Bertsch et al. 2007 meta-analysis (from memory) | Reported | Strong |

Design rules:

- **R11. Explain-back is short and specific.** One question: "Why does the retry not double-charge?" not "Explain what we built." The rubric has two or three points fixed in advance.
- **R12. The agent's explanation comes after the learner's.** If the learner asks the agent to explain first, the agent does (rule 7 of the skill: conceptual questions are answered), and the explain-back becomes a restatement later in review. The order matters for learning, but autonomy matters for use.
- **R13. Feedback cites the learner's own words.** "You said the lock stops the second write. It does not: the lease expires at `lease.py:41`." This is the Metcalfe point that feedback should analyse the reasoning that led to the error, and it is the skill's Voice rule.

## 6. Debugging drills

The largest gap in Shen and Tamkin was debugging, and the lowest-scoring group (24%) was the one that let the AI debug and verify. This is the strongest signal for the product: **the agent's default behaviour when a test fails (read the error, find the cause, fix it) is exactly the behaviour that removes the learning**.

Design rules:

- **R14. Hypothesis first, at most once per task.** When a test fails in a learning task, the agent offers (one line) "Want to call the cause first?" If yes, the learner names a hypothesis and a check that would confirm it. The agent then runs that check, not its own. This keeps the diagnosis with the learner without slowing a fix they don't want to make.
- **R15. Drills from real bugs.** Repair drills reuse the project's own bugs (reverted in a scratch branch), which gives transfer to the real codebase. Debugging instruction that teaches a systematic hypothesis-test loop improves debugging (reported: Michaeli and Romeike 2019, Koli Calling; Ko and Myers' Whyline work on asking "why" questions). Evidence specific to professional developers is weak.
- **R16. Grade the process, not only the cause.** The rubric for a drill has two parts: was the hypothesis testable, and was the cause right. A right guess with no check counts as "with help" at best.

## 7. Retrieval, spacing and scheduling

### 7.1 Evidence

| Finding | Source | Status | Strength |
|---|---|---|---|
| Retrieval practice beats re-study for long-term retention (testing effect). | Roediger and Karpicke 2006; Rowland 2014 meta-analysis; Adesope et al. 2017 meta-analysis (from memory) | Reported | Strong |
| The best gap between study and review grows with how long you need to remember. As a share of the retention interval it falls from about 20 to 40% (1-week test) to about 5 to 10% (1-year test). Too short a gap hurts more than too long. | [Cepeda et al. 2008, Psychological Science](https://pubmed.ncbi.nlm.nih.gov/19076480/) | Documented (abstract) | Strong (facts and simple materials) |
| Successive relearning (retrieve to a criterion, then relearn in later sessions) gives durable learning for low extra cost. Benefit for maths procedures was small (pooled d = 0.28). | [Rawson and Dunlosky line of work](https://openscholarship.wustl.edu/circle_book/8); Rawson, Dunlosky and Janes 2020 | Reported | Strong (facts), Moderate (procedures) |
| Duolingo's half-life regression cut recall prediction error by over 45% against baselines and raised daily engagement 12% in an operational test. | [Settles and Meeder 2016, ACL](https://aclanthology.org/P16-1174), [code](https://github.com/duolingo/halflife-regression) | Documented | Strong (prediction), Weak (learning outcome) |
| On 10k Anki collections, FSRS-6 predicts recall better than HLR (log loss 0.346 vs 0.469; RMSE 0.065 vs 0.128). Neural models (RWKV, GRU) do better still. Optimised parameters beat defaults (FSRS-7: 0.340 vs 0.362). | [open-spaced-repetition/srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark) | Documented | Strong (for card-style recall) |
| FSRS models memory with stability, difficulty and retrievability, and schedules to a "desired retention" (default 90%). Higher retention means many more reviews. | [FSRS optimal retention wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention), [Anki manual](https://docs.ankiweb.net/deck-options.html) | Documented | Documented |
| Interleaving beats blocking, g = 0.42 over 59 studies, stronger when categories are similar to each other and for complex material; blocking won for word lists. | [Brunmair and Richter 2019, Psychological Bulletin](https://pubmed.ncbi.nlm.nih.gov/31556629/) | Documented (abstract) | Strong |

### 7.2 What this means for the current schedule

The skill's ladder (3, 7, 21, 60, 180 days; a miss returns next day) is a fixed expanding schedule. Against the evidence:

- **It is in the right range.** If the target is "can still do it in a year", Cepeda's ridgeline puts the best single gap at around 3 to 5 weeks, and expanding gaps after successful retrieval are standard. The 21 and 60 day steps carry most of the value. (Strong for facts; moderate for the kind of conceptual and transfer questions this skill asks.)
- **The miss rule is right.** "Miss returns next day" is successive relearning: retrieve again soon after a failure, then expand. Consider one change: after a miss, the next step after the next-day review should restart at 3 days, not jump back to where it was. (Moderate.)
- **A modern scheduler is not worth it yet.** FSRS and HLR shine with thousands of reviews of atomic items. A learner here will have tens of topics and maybe a few hundred reviews a year, and the items are not atomic flashcards: a transfer question about idempotency is a new question each time. FSRS defaults would work, but would not clearly beat the fixed ladder at this data size, and its parameters cannot be fitted per user until there are many reviews. (Documented that defaults are worse than fitted; speculative about the crossover point.)
- **But log for it now.** Store each review as (topic id, timestamp, outcome on a 4-point scale, confidence, hint level, question id). That is a superset of the FSRS review-log format (card, time, rating 1 to 4). Then a later version can replay the log through `py-fsrs` or `fsrs-rs` and compare its predicted recall with real outcomes, at no cost to the learner. The mapping is natural: miss = Again, partial or with-hint = Hard, correct = Good, correct with high confidence and fast = Easy.
- **Let the learner set a target, not a schedule.** FSRS's "desired retention" is a good user-facing idea in plain words: "How sure do you want to be that you can still do this?" with two or three settings (for example "most of the time", "almost always"). It changes the review load. (Speculative for this product.)

### 7.3 Design rules

- **R17. Reviews are retrieval, not re-reading.** The review shows the question only. The code, the old answer and the old feedback appear after the learner commits. This is the Bastani lesson in a different place: help on screen during retrieval removes the benefit.
- **R18. Vary the question at each review.** A review of a topic at 21 or 60 days should be a new instance (a different file, a variation, a debugging version), not the same text. This gives transfer and stops answer memorisation. Successive levels: recall the idea, apply it to new code, spot it in a bug, design with it.
- **R19. Interleave confusable topics.** When two topics are often confused (the record will show it), put them in the same review session and ask which one applies. Brunmair and Richter's moderator is exactly "similar between categories".
- **R20. Reviews go where the learner is.** Due reviews are a phone-sized task (one question, one confidence, one answer). This is where the hosted page matters: it is the surface that reaches the learner away from the desk. Review timing should respect the same breakpoint rule: at session start, or as a quiet "2 due" line, never a push in the middle of work.

## 8. Confidence and calibration

### 8.1 Evidence

| Finding | Source | Status | Strength |
|---|---|---|---|
| Errors made with high confidence are corrected more readily after feedback than low-confidence errors (hypercorrection). Feedback that analyses the reasoning behind the error is key. Errors in low-stakes practice are useful. | [Metcalfe 2017, Annual Review of Psychology](https://doi.org/10.1146/annurev-psych-010416-044022) | Documented (abstract) | Strong |
| Certainty-based marking: a 3-level confidence scale with marks 1, 2, 3 for right and 0, -2, -6 for wrong. It is a proper scoring rule: the best choice is the honest one (thresholds about 67% and 80% likely correct). Practised students become well calibrated. | [Gardner-Medwin, UCL LAPT](https://www.ucl.ac.uk/lapt/REAP_CBM.htm); [Moodle CBM docs](https://docs.moodle.org/28/en/Using_certainty-based_marking) | Documented | Moderate |
| Judgments of learning made after a delay predict later recall much better than judgments made right after study. | [Rhodes and Tauber 2011, Psychological Bulletin](https://doi.org/10.1037/a0021705) | Documented (citation), effect from memory | Strong |
| Novices with AI overrate their own performance; trust in AI goes with less checking. | Prather et al. 2024; Lee et al. 2025 | Documented | Moderate |

### 8.2 Design rules

- **R21. Three levels, with meaning.** Keep low, medium, high, but define them on the UI in plain words tied to stakes, borrowing CBM thresholds: "low: a guess", "medium: probably", "high: I would bet on it (4 in 5 or better)". A defined scale is what lets calibration be measured.
- **R22. Confidence before the answer is revealed, in the same action.** The confidence chip is part of the answer submit, not a separate step. No answer without confidence on the page surfaces; in chat, missing confidence is graded "unknown" as the skill already says.
- **R23. High-confidence misses are first-class.** A high-confidence wrong answer gets (a) the plainest correction, with the reason and evidence, (b) an earlier return (next day, then 3 days), and (c) a mark on the record. These are the moments with the best chance of a lasting fix.
- **R24. Show calibration, not a score.** On the record page, a small chart: for each confidence level, how often the learner was right. A calibrated learner sees roughly 40%, 70%, 90%. This is the single best counter to the AI illusion of competence, because it is about the learner's judgment, which is the thing AI erodes. Keep it to three bars; no percentile, no comparison with others.
- **R25. Ask for a delayed self-judgment at review time, not right after the build.** "How well could you do this without the agent?" is far more accurate days later (Rhodes and Tauber). Right after a build, the fluency of the agent's work inflates it.

## 9. Feedback voice

| Finding | Source | Status | Strength |
|---|---|---|---|
| Feedback interventions improve performance on average (d = 0.41), but over a third lowered performance. Effects drop as feedback moves attention away from the task and toward the self. | [Kluger and DeNisi 1996, Psychological Bulletin](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/) | Documented (abstract) | Strong |
| Praise for ability ("you're smart") led to worse persistence after failure than praise for effort or no praise. | Mueller and Dweck 1998 (from memory) | Reported | Moderate (replication debate) |
| Feedback is most useful when it answers "where am I going, how am I going, where to next" at the task and process level. | Hattie and Timperley 2007 (from memory) | Reported | Strong (as a framework) |

The skill's Voice section ("Correct." / "Not quite." / "No.", no praise, reason and evidence) is well supported. It keeps attention on the task. Two additions:

- **R26. Every correction ends with "where next".** One line: the one thing to look at, or the next review date. This is the Hattie and Timperley third question and doubles as the resume cue.
- **R27. No social comparison, ever.** No leaderboards, no "better than 80% of learners". Kluger and DeNisi found normative feedback among the most harmful.

## 10. Worked examples and expertise reversal

| Finding | Source | Status | Strength |
|---|---|---|---|
| Methods that help novices (worked examples, full guidance) can hurt learners with more knowledge, and vice versa. Instruction should change as knowledge grows. | [Kalyuga 2007, Educational Psychology Review](https://doi.org/10.1007/s10648-007-9054-3) | Documented (abstract) | Strong |
| Worked examples with subgoal labels (the purpose of each step) improved early assessment in CS1 and are aimed at retention and transfer. | [Margulieux, Morrison and Decker 2019, ITiCSE](https://par.nsf.gov/servlets/purl/10171487); [2020, IJ STEM Ed](https://doaj.org/article/9a2c85d66fd54ec9ab019e9a510bbf17) | Documented (abstract) | Moderate |

Map the record levels to the kind of support, so the product changes with the learner:

| Record level | What the agent does in a learning task | Question type |
|---|---|---|
| not yet | Shows a worked example from this repo, with the purpose of each step labelled. Explain-back after. | "Which step stops X, and why?" |
| with help | Completion problem: the agent writes all but the key piece; the learner writes or describes it. Hints available. | Predict, then fill the gap |
| recalls | No example. Prediction before the build, explain-back after. | Recall the mechanism, apply to this change |
| transfers | The learner designs first; the agent reviews. Questions use a new context or a bug. | Transfer, debugging, design trade-off |

- **R28. Fade on evidence, not on time.** Move a topic up only on an unaided correct answer at the current level (the skill's record already does this). Move it down on a miss at review.
- **R29. Explainer pages for "not yet" and "with help" only.** For a learner at "transfers", a long explainer is redundant load (expertise reversal). Offer a one-paragraph summary and a hard question instead.

## 11. The record page: cognitive load and dashboards

Evidence on dashboard design is mostly practitioner guidance (Stephen Few, "Information Dashboard Design") and multimedia learning principles ([Mayer, coherence and signalling principles](https://www.cambridge.org/core/books/cambridge-handbook-of-multimedia-learning/)), not experiments on learning records. Treat these as weak to moderate.

- **R30. Three questions, in order.** The top of the page answers: what is due now (count and one button), what changed since last visit (one line), and the one gap (the topic with the worst recent result or a high-confidence miss). This is the skill's "end on the single most important gap" rule as a layout.
- **R31. The per-dimension record as a grid of cells, one per topic, coloured by level** using the site's ramp (#F6C9AF with help, #EE8B5B recalls, #C2410C transfers, empty for not yet). This is a small-multiples view: it shows breadth and depth at once without numbers. Each cell opens the topic's history. Never encode level by colour alone: add the level word or an icon shape for colour-blind and screen reader users (WCAG 1.4.1).
- **R32. No totals that only go up.** "Questions answered: 340" rewards volume. Show what the learner can do without the agent (topics at recalls or transfers), which can also go down at review. Honest numbers that can fall are what make the record trustworthy.
- **R33. Due work is bounded.** Cap a review session at a small number (for example 5) with "more" available. An unbounded due count is a source of guilt (see section 12).

## 12. Streaks, gamification and dark patterns

| Finding | Source | Status | Strength |
|---|---|---|---|
| Showing an intact streak raises later engagement, showing a broken one lowers it; people treat the streak as a goal in itself; the drop is larger when they blame themselves and smaller when the streak can be repaired. Authors warn of drop-off after a broken streak. | [Silverman and Barasch 2023, Journal of Consumer Research](https://doi.org/10.1093/jcr/ucac029), [CU Boulder summary](https://www.colorado.edu/business/faculty-research/2023/04/19/or-track-how-broken-streaks-affect-consumer-decisions) | Documented (abstract) | Moderate |
| Duolingo reports streak milestones raised 7-day retention by 1.7%, allowing two freezes raised daily active learners 0.38%, and 7-day-streak learners were 3.6 times more likely to finish a course (correlation). Strict streaks can backfire; slack helps people return. The post reports engagement, not learning. | [Duolingo blog, streak research](https://blog.duolingo.com/duolingo-streak-research/) | Documented (company blog) | Weak for learning |
| Tangible, expected rewards undermine intrinsic motivation; informational feedback does not. | [Deci, Koestner and Ryan 1999, Psychological Bulletin](https://depts.washington.edu/techdocs/papers/deciExtrinsicRewardsAndIntrinsicMotivation99.pdf) | Documented | Strong (with a long debate, Cameron and Pierce) |
| Dark patterns are common even in apps seen as benign. | [Aagaard et al. 2022, CHI EA](https://orbit.dtu.dk/en/publications/a-game-of-dark-patterns-designing-healthy-highly-engaging-mobile-games-); [Gray et al. 2018, CHI, "The dark (patterns) side of UX design"](https://doi.org/10.1145/3173574.3174108) | Documented | Moderate |
| Duolingo's Birdbrain models both learner skill and item difficulty to set challenge; A/B tests favoured it. | [Duolingo blog, Birdbrain](https://blog.duolingo.com/learning-how-to-help-you-learn-introducing-birdbrain), [IEEE Spectrum](https://spectrum.ieee.org/duolingo) | Documented (company) | Weak to moderate |

What Duolingo learned, read carefully: streaks move engagement by small percentages at enormous scale, they work through loss aversion, they need slack to avoid churn, and the company's own posts do not show that streaks improve learning. For a tool whose target is "what you can do without the agent", engagement is not the goal. A streak would reward the wrong thing: answering any question daily, including easy ones, to keep a number.

Design rules:

- **R34. No streak counter.** If a consistency signal helps, show the last 7 or 28 days as faint cells that light when a review happened (this matches the site's "faint record cells that light up" motion) with no number, no "broken" state and no reset. A missed day is just an unlit cell.
- **R35. No loss framing in copy or notifications.** Never "you'll lose", "don't break", "your record is at risk". Reminders, if any, are opt-in, at most once a day, at a time the learner chose, and say only what is due: "2 reviews due. About 3 minutes."
- **R36. No points, badges or levels that are not the record.** The record levels are the only "levels". They mean a real capability and can go down.
- **R37. Challenge matching is the real engagement engine.** What Birdbrain and flow both point to is right-sized difficulty. Use the record level to pick question difficulty (section 10). That is engagement that serves learning.
- **R38. Easy exit and pause.** "Pause reviews for a week" is one tap and costs nothing. Returning after a gap shows what is due, capped, with no guilt text.

## 13. Just-in-time learning in software engineering: evidence is thin

I looked for controlled evidence that learning "at the moment of need" during real software work produces durable skill. I found little:

- Practitioner and vendor claims (for example secure-coding "just in time training") report preference surveys, not learning outcomes. (Reported, weak.)
- HCI studies show developers spend much of their time seeking information (Ko, DeLine and Venolia 2007, "Information needs in collocated software development teams", ICSE; from memory) and that resumption is costly (Parnin). These motivate JIT help but do not show it builds skill.
- The strongest direct evidence is Shen and Tamkin 2026 (learning a new library during a real task) and Bastani 2025 (guardrailed vs unguarded help). Both say help at the moment of need **can** harm learning unless the learner generates first.
- Wait-learning (Cai et al. 2015) shows micro-learning in natural pauses works for vocabulary. Nobody has tested it for engineering concepts.

Conclusion: "just-in-time" is a good delivery idea and a weak learning idea on its own. Just-in-time **retrieval and generation** (predict, explain, diagnose) is supported. Just-in-time **explanation** alone is close to what the low-scoring Shen and Tamkin groups did. This is a speculative synthesis but it is the most important framing in this report.

## 14. Seamless transitions: putting it together

The owner wants seamless movement between building and learning. Learning science gives a concrete meaning to "seamless": **the learning moment uses a breakpoint that already exists, takes one action, needs no context switch, and returns the learner to the build with a cue.** Each of those has evidence behind it (sections 2, 4, 5, 8).

A task with the skill on, step by step:

| Moment | Breakpoint type | Learning action | Cost to learner | Evidence |
|---|---|---|---|---|
| Learner sends a request | Coarse (intent done) | None. Agent plans. | 0 | Iqbal and Bailey |
| Agent starts the long step | Coarse, waiting | Prediction: one question, options plus confidence, sent with "starting now". | One tap or one line, during dead time | Cai et al.; St. Hilaire et al. |
| Agent working | Waiting | Learner can answer, ask "how does X work" (answered at once), or ignore. | 0 to 1 action | Shen and Tamkin (inquiry) |
| Test fails (learning task) | Coarse, problem found | Offer once: "Call the cause first?" | 0 if declined | Shen and Tamkin (debugging gap) |
| Build passes | Coarse (unit done) | Prediction vs outcome, one line. Explain-back: one question, confidence. | One short answer | Kapur; Bisra et al. |
| Feedback | Within learning | "Correct." / "Not quite." / "No." plus reason, evidence, where next. Resume cue. | Read 2 to 3 lines | Kluger and DeNisi; Altmann and Trafton |
| Session start, phone, or idle | Coarse | "2 due, about 3 minutes." Retrieval without help on screen, varied question. | Opt-in | Cepeda; testing effect |

Across surfaces, the same attempt must be continuous: a prediction asked in Claude Code can be answered on the phone page, and the outcome comparison appears wherever the learner is next. That requires one attempt store that every surface reads and writes (the hosted artifact's db is the current candidate). The interaction design is the same on every surface: question, options or text, a confidence chip, submit. (The protocol side is covered by the other research tracks.)

### Accessibility notes that come from this track

- Confidence and level are never shown by colour alone (WCAG 1.4.1). Use the words.
- Timers are never used on questions (WCAG 2.2.1, and time pressure raises stress per Mark et al.). The "held result" in R2 must have a visible "show result" control.
- Motion for lighting cells respects `prefers-reduced-motion`.
- Questions and feedback fit a phone screen without scroll where possible, which is also the skill's Voice rule.

## 15. Where the evidence is weak

| Claim the product relies on | Evidence state | Risk |
|---|---|---|
| Wait time during agent work is a good moment to learn | Analogy from wait-learning (vocabulary) and breakpoint research. No test with coding agents. | Learners may prefer to watch the agent, or switch to other work during waits. |
| Spacing helps conceptual and transfer questions as much as facts | Most spacing studies use facts, words or simple procedures. Rawson et al. found smaller effects for maths procedures (d = 0.28). | The schedule may need fewer, longer gaps for deep topics. |
| Shen and Tamkin's patterns are causal | The authors say associational. Groups of 2 to 7 people. Measured right after the task. | The 86% "generation then comprehension" number should not be quoted as an effect. |
| Explain-back with an LLM grader is as good as with a teacher | Self-explanation evidence uses human or fixed prompts. LLM grading reliability against a fixed rubric is not established here. | Grading drift; the fixed rubric is the mitigation. |
| No-praise feedback keeps people using the tool | Kluger and DeNisi support task focus for performance. Long-term use of a no-praise tool is untested. | Some learners may find it cold. Measure drop-off. |
| Removing streaks does not hurt return rates | Duolingo shows small engagement gains from streaks. Unknown for professional developers. | Fewer reviews done. Weekly cells are the compromise. |
| JIT learning builds skill in software work | Thin. Mostly preference surveys. | Section 13: rely on generation, not on explanation. |
| Calibration charts change behaviour | CBM practice suggests learners calibrate with feedback; no test of a chart alone. | It may be ignored. Cheap to test. |

## 16. Cheapest experiments

All can run on the owner and a few colleagues with the existing record, since the record already stores outcome, confidence and hint level.

| ID | Question | Method | Cost |
|---|---|---|---|
| E1 | Does wait-time prediction cost less than before-build prediction? | Alternate the two placements across learning tasks for two weeks. Log time to answer, skips, and learner's next-prompt delay (a resumption proxy). | Small: one flag in the skill |
| E2 | Does showing prediction vs outcome improve later recall? | For half of predictions, show the side-by-side comparison; for the other half, just the outcome. Compare 7-day review results on those topics. | Small |
| E3 | Is the fixed ladder close to FSRS on this data? | Export review logs in FSRS format, replay through py-fsrs with default parameters, compare predicted recall with real outcomes (log loss) against the ladder's implied recall. | Very small: offline script |
| E4 | Do high-confidence misses get fixed more often (hypercorrection here)? | From the existing record, compare next-review success after high vs low confidence misses. | Very small: query |
| E5 | Does a calibration chart improve calibration? | Show the chart to the learner for a month; compare confidence-accuracy gap before and after. | Small |
| E6 | Do weekly cells without a counter keep review rates? | Owner self-trial: four weeks with only a due count, four weeks with weekly cells. Count reviews done. | Very small |
| E7 | Does "call the cause first" change debugging scores? | Offer it on every failing test in learning tasks for a month; give debugging review questions at 7 and 21 days; compare with topics where it was not offered. | Medium |

## 17. Source list

Primary or official sources read today (abstract or full text):

- Shen and Tamkin 2026, [arXiv 2601.20245](https://arxiv.org/abs/2601.20245); [Anthropic research post](https://www.anthropic.com/research/AI-assistance-coding-skills)
- Bastani et al. 2025, [SSRN 4895486](https://papers.ssrn.com/abstract=4895486) (PNAS 122(26))
- Fan et al. 2025, [arXiv 2412.09315](https://arxiv.org/abs/2412.09315)
- Prather et al. 2024, [arXiv 2405.17739](https://arxiv.org/abs/2405.17739)
- Lee et al. 2025, [CHI paper PDF](https://www.microsoft.com/en-us/research/uploads/prod/2025/01/lee_2025_ai_critical_thinking_survey.pdf)
- Adamczyk and Bailey 2004, [CHI PDF](https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p271.pdf)
- Iqbal and Bailey 2007, [record](https://researchr.org/publication/IqbalB07); [notification survey](https://arxiv.org/pdf/1711.10171)
- Altmann and Trafton 2002, [record](https://philpapers.org/rec/ALTMFG)
- Parnin and Rugaber 2011, [PDF](https://sites.cc.gatech.edu/reverse/repository/resumptionstrategies.pdf); [DeLine and Parnin cues](https://www.microsoft.com/en-us/research/publication/evaluating-cues-for-resuming-interrupted-programming-tasks/)
- Mark, Gudith and Klocke 2008, [CHI PDF](https://www.ics.uci.edu/~gmark/chi08-mark.pdf)
- Zuger et al. 2017, [record](https://researchr.org/publication/ZugerCMLFSAFKS17)
- Cai et al. 2015, [CHI PDF](https://sls.csail.mit.edu/publications/2015/Cai_CHI-2015.pdf)
- Sinha and Kapur 2021, [DOI](https://doi.org/10.3102/00346543211019105)
- St. Hilaire, Chan and Ahn 2024, [DOI](https://doi.org/10.3758/s13423-023-02353-8)
- Pan and Carpenter 2023, [Springer](https://link.springer.com/10.1007/s10648-023-09814-5)
- Bisra et al. 2018, [DOI](https://doi.org/10.1007/s10648-018-9434-x)
- Cepeda et al. 2008, [PubMed](https://pubmed.ncbi.nlm.nih.gov/19076480/)
- Rawson and Dunlosky, [chapter](https://openscholarship.wustl.edu/circle_book/8)
- Settles and Meeder 2016, [ACL](https://aclanthology.org/P16-1174); [duolingo/halflife-regression](https://github.com/duolingo/halflife-regression)
- [open-spaced-repetition/srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark); [FSRS optimal retention](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention)
- Brunmair and Richter 2019, [PubMed](https://pubmed.ncbi.nlm.nih.gov/31556629/)
- Metcalfe 2017, [DOI](https://doi.org/10.1146/annurev-psych-010416-044022)
- Gardner-Medwin CBM, [UCL](https://www.ucl.ac.uk/lapt/REAP_CBM.htm); [Moodle docs](https://docs.moodle.org/28/en/Using_certainty-based_marking)
- Rhodes and Tauber 2011, [DOI](https://doi.org/10.1037/a0021705)
- Kluger and DeNisi 1996, [record](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/)
- Kalyuga 2007, [DOI](https://doi.org/10.1007/s10648-007-9054-3)
- Margulieux, Morrison and Decker 2019, [PDF](https://par.nsf.gov/servlets/purl/10171487)
- Silverman and Barasch 2023, [DOI](https://doi.org/10.1093/jcr/ucac029)
- Deci, Koestner and Ryan 1999, [PDF](https://depts.washington.edu/techdocs/papers/deciExtrinsicRewardsAndIntrinsicMotivation99.pdf)
- Duolingo, [streak research](https://blog.duolingo.com/duolingo-streak-research/); [Birdbrain](https://blog.duolingo.com/learning-how-to-help-you-learn-introducing-birdbrain)
- Aagaard et al. 2022, [record](https://orbit.dtu.dk/en/publications/a-game-of-dark-patterns-designing-healthy-highly-engaging-mobile-games-)

Cited from memory, not re-read today (treat as reported): Bjork and Bjork 2011; Csikszentmihalyi 1990; Kornell, Hays and Bjork 2009; Roediger and Karpicke 2006; Rowland 2014; Adesope et al. 2017; Slamecka and Graf 1978; Bertsch et al. 2007; Mueller and Dweck 1998; Hattie and Timperley 2007; Ko, DeLine and Venolia 2007; Michaeli and Romeike 2019; Gray et al. 2018; Mayer's multimedia principles; Few's dashboard guidance.
