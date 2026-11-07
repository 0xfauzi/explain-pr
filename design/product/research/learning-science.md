# Learning science of skill formation with AI

Track: learning science (cognitive psychology, expertise research).
Date: 2026-11-07.
Input: `design/learning-experience/research/learning-science.md` (the earlier round, called "R1" below) and `design/learning-experience/critique/learning-scientist.md` (called "the critique"). This report does not repeat R1. It widens the frame from "one person in Claude Code" to a general product for anyone who builds with any coding agent, and it adds the parts R1 did not cover: what skill AI erodes and why, learning during real work versus separate practice, cognitive apprenticeship, deliberate practice, transfer, motivation, and a measurable definition of "a much better engineer".

## How to read this report

Evidence labels:

| Label | Meaning |
|---|---|
| **Strong** | Several experiments or a meta-analysis, replicated, mechanism understood. |
| **Moderate** | Replicated in the lab, or one good field study, but the setting is far from software work or the boundaries are open. |
| **Weak** | One small study, self-report, correlational data, or company data on engagement rather than learning. |
| **Speculative** | My inference for this product. No direct test. |

Source status:

- **Read today**: I read the abstract, a summary that quotes it, or the full text in this session.
- **Carried**: taken from R1, which marked it as documented. I did not re-read it today.
- **Memory**: from my own knowledge of the literature. Treat as reported, not checked.

Product and harness claims carry **[verified: source]** or **[unverified]**.
Numbers are only given where a source gives them. Where the product needs a number nobody has, the text says "needs to be measured".

---

## Part A. The short version

### A.1 Ten findings that should shape the product

1. **AI help lowers learning when it replaces the learner's thinking, not when it is present.** The same tool helps or harms depending on use. Substituting AI for practice widens coverage and lowers depth; using it to explain and check raises understanding ([Lehmann, Cornelius and Sting 2025](https://arxiv.org/abs/2409.09047), read today). In Shen and Tamkin, the AI group scored 50% against 67% on a quiz right after the task (d = 0.738), with the largest gap on debugging, and the high-scoring AI users were the ones who asked conceptual questions or generated then checked understanding ([Anthropic summary](https://www.anthropic.com/research/AI-assistance-coding-skills), read today). Strong in direction, moderate in size.
2. **People cannot feel this happening.** Students rated their learning lower in the condition where they learned more ([Deslauriers et al. 2019, PNAS](https://openlab.citytech.cuny.edu/gamelab/files/2023/01/Deslauriersa-et-al-2019.pdf), read today). Experienced developers believed AI made them 20% faster when it made them 19% slower ([METR 2025](https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/), read today via summary). LLM users overestimate the learning benefit ([Lehmann et al.](https://arxiv.org/abs/2409.09047)). So the product cannot be tuned on how learning feels. It has to measure unaided performance. Strong.
3. **Monitoring automation is not practice, and the unpractised cognitive part decays first.** Bainbridge's "ironies of automation" ([1983](https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf), read today), pilots who kept motor skills but lost cognitive ones such as tracking position without a map ([Casner et al. 2014](https://journals.sagepub.com/doi/10.1177/0018720814535628), read today), and endoscopists whose unaided detection rate fell from 28.4% to 22.4% after months with AI ([Budzyń et al. 2025](https://wrap.warwick.ac.uk/id/eprint/191005), read today, observational). Cognitive skills decay faster than physical ones ([Arthur et al. 1998](https://Www.Gwern.net/doc/psychology/spaced-repetition/1998-arthur.pdf), read today via summary). Moderate (none of these is software).
4. **Retrieval, spacing and generation are the best-supported tools in all of learning science.** Practice testing and distributed practice are the only two "high utility" techniques in [Dunlosky et al. 2013](https://www.psychologicalscience.org/news/releases/which-study-strategies-make-the-grade.html) (read today). Testing beats restudy at g = 0.50, and more so on delayed tests (g = 0.69) ([Rowland 2014](https://doi.org/10.1037/a0037559), read today via summary). Spaced retrieval beats massed retrieval at g = 0.74 ([Latimier et al. 2021](https://link.springer.com/10.1007/s10648-020-09572-8), read today). Generation beats reading at about d = 0.40 ([Bertsch et al. 2007](https://pubmed.ncbi.nlm.nih.gov/17645161/), read today). Self-explanation g = 0.55 ([Bisra et al. 2018](https://www.Gwern.net/doc/psychology/spaced-repetition/2018-bisra.pdf), read today). Strong.
5. **Engagement with AI code can be designed in, and the best-tested pattern is "state the step, then see the code".** Of seven techniques, "Lead-and-Reveal" (the learner says what each step should do before the AI's code is revealed) aligned perceived and actual ability best without raising cognitive load ([Kazemitabaar et al. 2025, IUI](https://arxiv.org/abs/2410.08922), read today). A hint-only tutor removed the exam harm that plain chat caused ([Bastani et al. 2025](https://papers.ssrn.com/abstract=4895486), carried). Moderate.
6. **Real work is a good place to learn, but it does not by itself produce deliberate practice.** Deliberate practice predicts under 1% of performance variance in professions in the main meta-analysis, from few studies ([Macnamara et al. 2014](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/), read today). But current deliberate practice at work did predict insurance agents' rated performance ([Sonnentag and Kleine 2000](https://kops.uni-konstanz.de/entities/publication/3137afd2-22a3-448a-a3b8-e6a8e7d21e2f), read today). Intuitive expertise only forms where cues are valid and feedback is fast ([Kahneman and Klein 2009](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/strategic-decisions-when-can-you-trust-your-gut), read today via interview). Moderate.
7. **Transfer is the hard part, and it fails mostly because people do not notice which principle applies.** Comparing two cases side by side made business students nearly three times more likely to use a strategy than studying the same cases apart ([Loewenstein, Thompson and Gentner 1999; Gentner et al. 2003](https://dedregentner.owlstown.net/publications/38525-learning-and-transfer-a-general-role-for-analogical-encoding), read today). Fading worked steps helps near transfer; adding "name the principle" prompts helps far transfer ([Atkinson, Renkl and Merrill 2003](https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/), read today). Strong (lab).
8. **Support must fade as knowledge grows, per topic.** What helps novices (worked examples) can hurt more knowledgeable learners (expertise reversal, [Kalyuga 2007](https://doi.org/10.1007/s10648-007-9054-3), carried). A senior engineer is a novice in a new domain. Adaptation must be per topic, never per person. Strong.
9. **Points, badges, leaderboards and streaks are a poor fit for this goal.** The meta-analysis is positive on average for gamification (cognitive g = 0.49, [Sailer and Homner 2020](https://link.springer.com/article/10.1007/s10648-019-09498-w), read today), but a 16-week classroom study with leaderboards and badges found lower motivation and lower exam scores ([Hanus and Fox 2015](https://dblp.org/rec/journals/ce/HanusF15), read today). Normative feedback is among the most harmful feedback types ([Kluger and DeNisi 1996](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/), carried). For professionals whose motivation is the work, self-determination theory predicts that controlling rewards crowd out the reason they came ([Ryan and Deci 2000](https://bibbase.org/network/publication/ryan-deci-selfdeterminationtheoryandthefacilitationofintrinsicmotivationsocialdevelopmentandwellbeing-2000), read today). Moderate.
10. **Short spaced questions delivered during a working life work, and the effect lasts.** Urology residents who got daily emailed questions on a spaced schedule still scored higher two years later (70.2% vs 66.8%, effect size 0.35) ([Kerfoot 2009](https://pubmed.ncbi.nlm.nih.gov/19375095/), read today; author has a commercial interest; self-selected follow-up). This is the closest existing evidence for "a few review items a day while you work". Moderate.

### A.2 What this means for the product in one paragraph

The product should not teach. It should make the user **generate** at the few points where the agent would otherwise think for them (predict, diagnose, write the key line, explain, decide), close each generation with evidence from the real build, and then **re-test** the idea later, unaided, in a new form. It should measure what the user can do without the agent, delayed and in new code, and show that honestly, including when it falls. Everything that feels like learning but does not require generation (reading explanations, watching the agent debug, recognising the right option, collecting points) should be treated as zero evidence. This holds on every coding surface, because none of it depends on a particular UI: it depends on the order of who thinks first.

### A.3 Design rules at a glance

The full rules, with evidence and strength, are in Part F. Short form:

| # | Rule | Strength |
|---|---|---|
| L1 | The user thinks first at chosen points; the agent responds to what the user produced. | Strong |
| L2 | Count only unaided, delayed, novel-instance performance as skill. | Strong |
| L3 | Never tune on self-reported learning or satisfaction alone. | Strong |
| L4 | Spend the generation budget on diagnosis and verification first. | Moderate |
| L5 | "Your line" targets the one germane decision, is graded by the build, and fades. | Moderate |
| L6 | Every prediction is closed against the real outcome, with the gap explained. | Strong |
| L7 | Reviews are free recall in a new instance, with no help on screen. | Strong |
| L8 | Space reviews; the exact ladder matters less than spacing at all. | Strong |
| L9 | Interleave confusable ideas; hide the topic name on transfer items. | Strong (lab) |
| L10 | Fade support per topic, on evidence. | Strong |
| L11 | Teach transfer by comparison and by naming the principle. | Strong (lab) |
| L12 | Collect confidence with every answer; treat sure misses as the key event. | Strong |
| L13 | Feedback is about the task and the reasoning, never the person or others. | Strong |
| L14 | No points, streak counters, badges, leaderboards, or loss framing. | Moderate |
| L15 | Autonomy first: the user picks goals and can skip at no cost. | Moderate |
| L16 | Rehearse rare, high-stakes work (incidents, rollbacks) by simulation. | Moderate (practice), Weak (outcomes) |
| L17 | Practise verifying agent output as a skill in its own right. | Speculative, well motivated |
| L18 | Make the agent model expert process aloud only when asked or after the user tried. | Moderate |
| L19 | Measure the product with within-person, randomized topic designs. | Strong (method) |

---

## Part B. What AI assistance does to skill formation

### B.1 Studies in programming and nearby fields

| Study | Design | Finding | Status | Strength |
|---|---|---|---|---|
| [Shen and Tamkin 2026, arXiv 2601.20245](https://arxiv.org/abs/2601.20245); [Anthropic summary](https://www.anthropic.com/research/AI-assistance-coding-skills) | RCT, 52 mostly junior developers learning the Trio async library; 35-minute task, 25-minute quiz right after | AI group 50% vs 67% (d = 0.738, p = 0.01). Time difference about 2 minutes, not significant (p = 0.391). Largest gap on debugging. Low-scoring patterns: delegation (n = 4, 39%), progressive reliance (n = 4, 35%), iterative AI debugging (n = 4, 24%). High-scoring: generation then comprehension (n = 2, 86%), hybrid code and explanation (n = 3, 68%), conceptual inquiry (n = 7, 65%). Authors: did not test agentic tools such as Claude Code and expect a larger effect there; measured only immediately; patterns are associational. | Read today | Moderate (one RCT, immediate test) |
| [Lehmann, Cornelius and Sting 2025, arXiv 2409.09047](https://arxiv.org/abs/2409.09047) | Field data from university programming courses plus two preregistered lab experiments | No overall effect of LLM access on learning. Using the LLM as a substitute for practice covers more topics with shallower understanding; as a complement (explain, tutor) it improves understanding. Students prefer substitution. Perceived benefit exceeds actual benefit. LLM access widens the gap between low and high prior knowledge. | Read today (abstract and summary) | Moderate |
| [Kazemitabaar et al. 2023, CHI](https://arxiv.org/abs/2302.07427) | 69 novices aged 10 to 17, with or without Codex, retention test after one week | Codex raised code-writing performance and did not lower manual code-modification performance. Retention one week later: slightly better with Codex, not significant. Learners with more prior experience benefited significantly. | Read today | Moderate (young novices, early tool) |
| [Kazemitabaar et al. 2025, IUI](https://arxiv.org/abs/2410.08922) | Study 1 N = 82 between subjects (seven techniques); Study 2 N = 42 within subjects | Lead-and-Reveal and Trace-and-Predict were the most balanced. Revised Lead-and-Reveal (short answers with LLM feedback) best aligned perceived and actual ability without raising cognitive load. Authors propose "friction-induced AI". | Read today | Moderate |
| [Prather et al. 2024, ICER, "The Widening Gap"](https://arxiv.org/abs/2405.17739) | Lab study, 21 novices, eye tracking | Strong students used AI to go faster; struggling students got an illusion of competence. | Carried | Weak to moderate |
| [Bastani et al. 2025, PNAS](https://papers.ssrn.com/abstract=4895486) | Field experiment, about 1,000 high school maths students | Plain GPT-4 raised practice scores 48% and lowered exam scores 17% against control. A hint tutor raised practice 127% with exam scores about equal to control. | Carried | Strong (large field RCT) |
| [Darvishi et al. 2024, Computers and Education](https://digital.library.adelaide.edu.au/items/99e9a0ee-4feb-405c-8e66-062c6b67aa11) | 1,625 students, peer review with AI prompts, then prompts removed | Students relied on the AI rather than learning from it: when prompts were removed, quality fell. Self-monitoring checklists only partly compensated. | Read today (abstract) | Moderate |
| [Fan et al. 2025, BJET, "metacognitive laziness"](https://arxiv.org/abs/2412.09315) | RCT, 117 students, essay writing | Best essays with ChatGPT, but no better knowledge gain or transfer, and less metacognitive activity. | Carried | Moderate |
| [Kosmyna et al. 2025, "Your Brain on ChatGPT"](https://arxiv.org/abs/2506.08872) | 54 participants, essays, EEG, three groups; preprint | Lowest brain connectivity in the LLM group; LLM users struggled to quote their own essays and reported the lowest ownership. Not peer reviewed at time of reading; small sample; essay writing only. | Read today | Weak |
| [Gerlich 2025, Societies](https://doaj.org/article/d5c17dd91ce64775a065095d8af730ce) | Survey and interviews, 666 participants | Heavier AI use went with lower critical thinking, mediated by cognitive offloading. Correlational. | Read today | Weak |
| [Lee et al. 2025, CHI](https://www.microsoft.com/en-us/research/uploads/prod/2025/01/lee_2025_ai_critical_thinking_survey.pdf) | Survey, 319 knowledge workers | More confidence in AI went with less critical thinking; more self-confidence with more. | Carried | Weak |
| [METR 2025](https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/) | RCT, 16 experienced open-source developers, 246 tasks in their own repos | AI allowed: 19% longer completion. Developers expected 24% faster and afterwards believed 20% faster. | Read today (summary) | Moderate (productivity, not learning; included for the perception gap) |
| [Kestin et al. 2025, Scientific Reports](https://library.kab.ac.ug/Record/doaj-art-594959a5f4f94bd8a7ad3d534581f3ec/Details) | Crossover RCT, 194 physics students, AI tutor built on pedagogy vs in-class active learning | Larger post-test gains with the designed AI tutor. No delayed test reported (per a later review). | Read today (summaries) | Moderate |

### B.2 Evidence from other automated professions

| Study | Finding | Status | Strength for software |
|---|---|---|---|
| [Bainbridge 1983, Automatica](https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf) | Unused skills deteriorate. A formerly experienced operator who has been monitoring may now be inexperienced. Later generations cannot be expected to have the skills the automation was built on. | Read today | Strong as theory; widely applied |
| [Casner et al. 2014, Human Factors](https://journals.sagepub.com/doi/10.1177/0018720814535628) | 16 airline pilots in a simulator: hand-flying skills mostly intact; cognitive skills such as tracking position without a map display eroded. Retention tied to how actively pilots stayed engaged in supervising the automation. | Read today | Moderate (small, but the split is the point) |
| [Budzyń et al. 2025, Lancet Gastroenterology and Hepatology](https://wrap.warwick.ac.uk/id/eprint/191005) | 19 endoscopists: unaided adenoma detection fell from 28.4% to 22.4% three months after AI was introduced. | Read today | Moderate (observational) |
| [Arthur et al. 1998, Human Performance](https://Www.Gwern.net/doc/psychology/spaced-repetition/1998-arthur.pdf) | Skill decay grows with time without use; cognitive tasks decay more than physical ones; decay is lower when the retention context resembles the learning context. | Read today (quoted summary) | Strong (meta-analysis, older) |

### B.3 Synthesis: what exactly erodes

Reading across B.1 and B.2, the skills that erode are the ones the agent now performs: **diagnosis** (Shen and Tamkin's largest gap), **comprehension of code you did not write** (their code-reading items; Kosmyna's ownership and quoting result), **checking** (Lee; Darvishi), and **self-assessment** (Prather; Lehmann; METR). The skills that do not erode are the ones the human still performs. Casner's pilots kept what they still did by hand and lost what the computer did for them.

So the design principle is not "use less AI". It is: **keep the human doing the cognitive part of the job at a dose that maintains it, at the moments the agent would otherwise do it.** That is the generalisable product idea, and it does not depend on any one harness.

Two cautions from the same evidence:

- **Prior knowledge decides who benefits.** Lehmann (widening gap), Prather, and Kazemitabaar 2023 (prior experience predicted benefit) agree. A general product will reach people far from the founder's level. The weakest users are the most at risk and the least able to self-assess. Design for them by default; let stronger users turn the dose down. (Moderate.)
- **The tool can be the tutor.** Bastani's hint tutor and Kestin's designed tutor show that the same models used with pedagogy help. The product is that pedagogy, wrapped around the user's real work. (Moderate.)

---

## Part C. Core mechanisms, briefly, with what is new beyond R1

R1 covered retrieval, spacing, interleaving, pretesting, productive failure, self-explanation, calibration, feedback, worked examples and gamification in depth. This section adds sizes checked today and the points R1 missed.

### C.1 Retrieval practice and spacing

- Testing vs restudy: g = 0.50 overall, g = 0.69 when the final test is a day or more later ([Rowland 2014](https://doi.org/10.1037/a0037559), read today via summary). Practice testing: g = 0.61 fixed effects, 0.70 random effects ([Adesope et al. 2017](https://doi.org/10.3102/0034654316689306), read today via summary). Strong.
- Spaced vs massed retrieval: g = 0.74 ([Latimier et al. 2021](https://link.springer.com/10.1007/s10648-020-09572-8), read today). A secondary summary reports no advantage for expanding over uniform gaps (g = 0.034); I could not confirm that number in the paper. **New implication:** the exact ladder (3, 7, 21, 60, 180 days) is less important than reviewing at spaced gaps at all. Do not spend product effort on schedule tuning before the basics work. Strong for spacing; moderate for the null on expanding schedules.
- The best gap grows with how long the skill must last, and too short hurts more than too long ([Cepeda et al. 2008](https://pubmed.ncbi.nlm.nih.gov/19076480/), carried). **This supports founder decision 3 (at most 3 due items a day).** When a cap delays an item past its due date, the cost is small, because overshooting a gap is the cheaper error. Strong.

### C.2 Interleaving

Interleaving beats blocking (g = 0.42), more for similar categories ([Brunmair and Richter 2019](https://pubmed.ncbi.nlm.nih.gov/31556629/), carried). **New point:** interleaving works partly because the learner has to decide *which* idea applies. Printing the topic name on the item removes that decision (the critique's M3). On a general product, items from different repos and different domains can be mixed, which is a natural source of interleaving that a single-repo tool lacks. Strong (lab).

### C.3 Desirable difficulties and the feeling of learning

Effortful conditions produce better long-term learning and feel worse ([Bjork and Bjork 2011](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf), carried). Deslauriers et al. measured the gap directly: active-learning students scored higher and rated their learning lower, and the authors attribute part of this to effort being read as poor learning ([PNAS 2019](https://openlab.citytech.cuny.edu/gamelab/files/2023/01/Deslauriersa-et-al-2019.pdf), read today). They also describe an early intervention that tells students this. **New implication:** onboarding should say plainly, once, that the effortful moments will feel slower and are the ones that work, and the product should show the user later evidence (a held review) rather than ask them to trust the feeling. Strong.

### C.4 Generation, self-explanation, prediction and error correction

- Generation effect about d = 0.40 over 86 studies ([Bertsch et al. 2007](https://pubmed.ncbi.nlm.nih.gov/17645161/), read today). Self-explanation g = 0.55 over 64 reports ([Bisra et al. 2018](https://www.Gwern.net/doc/psychology/spaced-repetition/2018-bisra.pdf), read today). Prequestions help the questioned content (g = 0.54), not the rest ([St. Hilaire et al. 2024](https://doi.org/10.3758/s13423-023-02353-8), carried). High-confidence errors corrected with feedback are fixed more readily (hypercorrection, [Metcalfe 2017](https://doi.org/10.1146/annurev-psych-010416-044022), carried). Strong.
- **ICAP** orders engagement as passive (receive), active (manipulate), constructive (generate), interactive (co-generate in dialogue), and predicts learning rises in that order ([Chi and Wylie 2014](https://chilab.asu.edu/sites/default/files/lcl/chiwylie2014icap_2.pdf), read today). Tests of the hypothesis are mixed, and one found passive learners did best, so treat it as a useful classification, not a law. Moderate. **Implication:** an "Insight" box or explanation the user reads is passive. Claude Code's Explanatory style adds such boxes [verified: https://code.claude.com/docs/en/output-styles]. By ICAP it is the weakest mode. Its Learning style adds `TODO(human)` gaps the user writes [verified: same page], which is constructive. The product's core moments should all be constructive or interactive.

### C.5 Worked examples, fading and expertise reversal

- Fading worked steps improves near transfer over example-problem pairs; it did not reliably improve far transfer until learners were also prompted to name the principle behind each step ([Atkinson, Renkl and Merrill 2003](https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/), read today). Backward fading (learner does the last step first) was better in earlier work, but not in every later study (Renkl and Atkinson 2002, Journal of Experimental Education, known only from secondary summaries read today). Strong (lab).
- **Implication for "your line" (founder decision 2):** "your line" is a completion problem, the agent's code is the worked example around it, and the evidence says three things: (a) the gap should be the step that carries the idea, (b) the user should name the principle the line serves, in one phrase, and (c) as the topic's level rises the gap should grow (one line, then the function, then the design) until the user writes it and the agent reviews. That is fading inside real work. Strong for the mechanism, speculative for the exact steps.

### C.6 Metacognition and calibration

- Judgments of learning made after a delay are far more accurate than immediate ones ([Rhodes and Tauber 2011](https://doi.org/10.1037/a0021705), carried).
- AI users overrate themselves (Prather; Lehmann; METR in productivity). Lead-and-Reveal narrowed the gap between perceived and actual ability ([Kazemitabaar 2025](https://arxiv.org/abs/2410.08922)). Moderate.
- **New implication:** calibration is a measurable skill in its own right and a direct counter to the main AI harm. Score it with a proper scoring rule (for example a Brier score over confidence levels), and show it only once there are enough answers to mean something. The threshold "needs to be measured"; the critique suggested about 10 per level as a starting point.

### C.7 Feedback

Feedback improves performance on average, but over a third of interventions lowered it, and effects drop as feedback shifts attention from the task to the self or to others ([Kluger and DeNisi 1996](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/), carried). Feedback that analyses the reasoning behind an error is what makes hypercorrection work (Metcalfe). R1's voice rules hold. Strong.

---

## Part D. Expertise, apprenticeship and learning during real work

### D.1 Cognitive apprenticeship: the agent as master, the user as apprentice

[Collins, Brown and Newman 1989](https://en.wikipedia.org/wiki/Cognitive_apprenticeship) (read today via summaries) named six methods for teaching cognitive crafts: **modeling** (the expert performs and makes thinking visible), **coaching** (hints and feedback during practice), **scaffolding** (support that is withdrawn as the learner takes over), **articulation** (the learner puts reasoning into words), **reflection** (the learner compares their process to an expert's), and **exploration** (the learner poses and tests their own problems).

A coding agent is the first tool that can play the master role inside the apprentice's real work at any hour. Mapped to the product:

| Method | In the product | Evidence link |
|---|---|---|
| Modeling | The agent says its hypothesis and the check it will run before running it, but only after the user has offered theirs, or when asked. | Expert process is invisible in finished code (Collins et al.); order matters (Kazemitabaar 2025). Moderate. |
| Coaching | Hint ladder, one rung per request. | Bastani hint tutor. Strong. |
| Scaffolding and fading | "Your line" that grows with level; worked example at "not yet", design-first at "transfers". | Atkinson et al.; Kalyuga. Strong. |
| Articulation | Explain-back; "name the principle" for your line; predictions in words. | Bisra; Chi. Strong. |
| Reflection | Prediction next to outcome; the user's diagnosis next to the agent's; calibration over time. | Metcalfe; Sinha and Kapur. Strong. |
| Exploration | The user can ask "what if" and have the agent build a throwaway variant to test their own hypothesis. | Collins et al. Weak (little direct evidence). |

**Speculative but important:** the traditional failure of apprenticeship is that the master does the hard parts because it is faster. The agent has the same incentive, set by its default instructions to finish the task. The product must be the counterweight that hands over the right parts.

### D.2 Deliberate practice: what it is, and what the evidence really says

Ericsson's deliberate practice is effortful, designed to improve a specific weakness, done with immediate feedback, and usually separate from performance (Ericsson, Krampe and Tesch-Römer 1993, memory). Two things follow from the newer evidence:

- **The size claim was overstated.** Across 88 studies, deliberate practice explained about 12% of performance variance overall and under 1% in professions, though the professions estimate rests on few studies and Ericsson's group disputes how practice was measured ([Macnamara et al. 2014](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/), read today). Do not sell the product as "10,000 hours" or as a guaranteed path to expertise.
- **Practice at work can count, if it is current and targeted.** Insurance agents' current deliberate practice predicted supervisor ratings; accumulated past practice did not ([Sonnentag and Kleine 2000](https://kops.uni-konstanz.de/entities/publication/3137afd2-22a3-448a-a3b8-e6a8e7d21e2f), read today). Moderate.

What the product can take from deliberate practice that is well grounded: **target the weakest dimension**, **give immediate, specific feedback**, and **make each repetition effortful**. What it should not take: long separate practice sessions as the main mode. Most users will not do them (Lehmann's students preferred the easy path), and the evidence for their size in professional work is thin.

### D.3 Learning during real work versus separate practice

This is the central question for a "learn while building" product. The honest answer is that neither alone is enough, and the evidence says which parts belong where.

**Arguments for learning inside real work:**

- **Transfer to the job is easier when the learning context resembles the use context.** Skill decay is lower when the retention context matches the learning context ([Arthur et al. 1998](https://Www.Gwern.net/doc/psychology/spaced-repetition/1998-arthur.pdf)). Learning on the user's own code is as close as it gets. Moderate.
- **Motivation and relevance.** Training transfer relates more to motivation and work environment for open skills (judgment-heavy) than closed skills ([Blume et al. 2010](https://kops.uni-konstanz.de/bitstreams/c871fed9-39d7-429b-a953-3c817c60a254/download), read today via summary). Engineering judgment is an open skill. Moderate.
- **The breakpoints already exist.** Agent wait time and build completion are natural pauses (R1 section 2). Moderate.
- **Spaced questions during a working life last.** Kerfoot's residents, two years on ([2009](https://pubmed.ncbi.nlm.nih.gov/19375095/)). Moderate.
- **Code review is already a learning channel.** At Microsoft, knowledge transfer was one of the main real outcomes of review, and understanding the change was the central challenge ([Bacchelli and Bird 2013](https://huang.isis.vanderbilt.edu/cs4278/readings/codereview.pdf), read today). Moderate.

**Arguments for separate practice:**

- **Real work gives the wrong distribution of reps.** Most work repeats the common case. The skills that matter most in a crisis (rare failures, incidents, rollbacks) occur rarely. Pilots train rare emergencies in simulators; Casner's authors recommend simulator practice for the eroded cognitive skills ([2014](https://journals.sagepub.com/doi/10.1177/0018720814535628)). Google SRE runs "Wheel of Misfortune" role-play of past outages for on-call training ([SRE book material via community write-ups](https://dastergon.github.io/wheel-of-misfortune/instructions.html), read today) [verified: practice exists; learning outcomes unverified]. Moderate for the practice; weak for measured outcomes.
- **Real work has bad feedback for many judgments.** Kahneman and Klein: intuition becomes trustworthy only where cues predict outcomes and feedback is fast and clear ([2009](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/strategic-decisions-when-can-you-trust-your-gut)). A design decision's outcome may surface months later, or never. The product can **create** fast feedback by asking for a prediction that the build resolves in minutes, and **create** delayed feedback by asking "you predicted this design would make X hard; was it?" when the code is next touched. Moderate (theory), speculative (the mechanism).
- **Real work punishes errors, and learning needs safe errors.** Productive failure and errorful generation need low stakes (Sinha and Kapur 2021, carried; Kornell et al. 2009, memory). A drill on a scratch branch makes errors free. Moderate.
- **Work pressure pushes out learning.** Under deadline the user will choose "just do it", correctly. Some practice must live outside those moments. Speculative.

**Conclusion (moderate, partly speculative):** put **generation** inside real work (predict, your line, diagnose first, explain back), because that is where transfer and motivation are best and the cost is lowest. Put **retrieval** in short spaced reviews between work (founder decision 3), varied into new instances, because spacing needs time away. Put **rare and high-stakes skills** in occasional, opt-in simulations made from the user's own code and history (reverted real bugs, replayed incidents), because real work will not supply the reps. Never rely on real work alone for skills the agent now performs end to end, because that is exactly the Bainbridge trap.

### D.4 Transfer

- Far transfer is rare and depends on many dimensions of distance (domain, context, time, modality) (Barnett and Ceci 2002, memory). Strong as a framework.
- People often fail to use a principle they know because nothing cues it (Gick and Holyoak 1980, 1983, memory). Strong.
- Comparing two cases that share a principle is a reliable way to abstract it ([Gentner, Loewenstein and Thompson 2003](https://dedregentner.owlstown.net/publications/38525-learning-and-transfer-a-general-role-for-analogical-encoding), read today). Strong (lab).

Product implications:

- **Cross-project comparison is the product's unfair advantage.** A user who builds several projects meets the same principle (idempotency, backpressure, cache invalidation) in different code. The record can say "you met this in project A and in project B; what is the same?" A single-repo tool cannot do this. This favours a record that is **per user, across repos** (which founder decision 1, a local git repo for the record, allows). Speculative application of strong evidence.
- **Transfer items must hide the principle's name** until the user commits (the critique's M3). Strong.
- **"Transfers" as a level must be earned on a different context**, not a near copy (the critique's M4). Strong.

---

## Part E. Motivation and the risk of gamification

### E.1 Self-determination theory applied

SDT says intrinsic motivation is supported when three needs are met: **autonomy**, **competence**, **relatedness** ([Ryan and Deci 2000](https://bibbase.org/network/publication/ryan-deci-selfdeterminationtheoryandthefacilitationofintrinsicmotivationsocialdevelopmentandwellbeing-2000), read today). Expected tangible rewards undermine intrinsic motivation; informational feedback does not ([Deci, Koestner and Ryan 1999](https://depts.washington.edu/techdocs/papers/deciExtrinsicRewardsAndIntrinsicMotivation99.pdf), carried). Strong.

| Need | Supports it | Undermines it |
|---|---|---|
| Autonomy | User chooses which areas to grow in; skip and "just do it" are instant and free; the user sets the reminder time and the daily cap (founder decisions 3 and 7); the user decides if a task is a learning task. | Forced quizzes; held results the user cannot release; guilt copy; reminders they did not ask for. |
| Competence | Questions at the right difficulty (per-topic level); feedback that says what to do next; a record that shows real capability growing on hard things. | Questions far above or below level; praise that carries no information; a score that only goes up and so means nothing. |
| Relatedness | Optional: share a snapshot of the record with a mentor or team, by the user's choice; the agent's voice treats the user as a capable colleague. | Leaderboards and rankings; comparison with "other learners". |

Relatedness is the need the product serves least. A general product could let a user export a read-only snapshot of their record or a "learning PR" to a mentor. That must stay opt-in and local by default (founder decision 1). Speculative.

### E.2 Gamification: what the evidence supports

- On average, gamification has small positive effects on cognitive (g = 0.49), motivational (g = 0.36) and behavioural outcomes, with unresolved moderators ([Sailer and Homner 2020](https://link.springer.com/article/10.1007/s10648-019-09498-w), read today). Moderate.
- A 16-week course with leaderboards and badges lowered motivation, satisfaction and exam scores, with the exam effect running through intrinsic motivation ([Hanus and Fox 2015](https://dblp.org/rec/journals/ce/HanusF15), read today). Moderate.
- Streaks raise engagement while intact and lower it after a break; people pursue the streak for its own sake ([Silverman and Barasch 2023](https://doi.org/10.1093/jcr/ucac029), carried). Duolingo's own data is about engagement, not learning ([Duolingo blog](https://blog.duolingo.com/duolingo-streak-research/), carried). Moderate.

**Judgment:** the average positive effect comes mostly from school settings where the baseline motivation is low and the activity is assigned. This product's users came for the work and for their own growth. That is the population where SDT predicts controlling rewards do the most harm. And any counter that rewards volume will reward easy questions, which is the opposite of desirable difficulty. So: no points, no streak counter, no badges, no levels other than the record's real levels, no leaderboards. Moderate (inference from strong components).

The one "game" mechanic with good support is **challenge matched to skill** (flow; Duolingo's Birdbrain, carried). That is just good adaptive difficulty and should be kept.

---

## Part F. Design rules

Each rule: what to do, why (evidence), strength, and how a general product implements it on any surface.

**L1. The user thinks first at chosen points; the agent responds to what the user produced.**
Why: generation, self-explanation and prediction effects (C.4); Shen and Tamkin's high scorers generated or asked first; Lead-and-Reveal (Kazemitabaar 2025); Bastani's hint tutor. Strong.
How: at a learning point the agent asks one question and stops, then builds on the answer. On every surface this is just message order, so it needs no special UI.

**L2. Count only unaided, delayed, novel-instance performance as skill.**
Why: immediate judgments and performance are inflated (Rhodes and Tauber); testing effects are larger at a delay (Rowland: g = 0.69 vs 0.41); Darvishi's reliance result (performance with AI says little about performance without it). Strong.
How: an explain-back minutes after the build is consolidation and can confirm "with help" at most. "Without help" needs an unaided correct answer at the first spaced review. "Transfers" needs a correct answer in a different context. Any help (hint, code shown, agent explanation first) caps the attempt's level. This carries the critique's B1, M4 and M7 into the general product.

**L3. Never tune the product on self-reported learning or satisfaction alone.**
Why: Deslauriers (feeling and learning anti-correlated); Lehmann (perceived benefit exceeds actual); METR (perceived 20% faster, measured 19% slower). Strong.
How: product metrics are delayed unaided accuracy, calibration, and field evidence. Satisfaction and drop-off are guardrails, not goals.

**L4. Spend the generation budget on diagnosis and verification first.**
Why: debugging showed the largest gap and "iterative AI debugging" the lowest score in Shen and Tamkin; Casner and Bainbridge say the eroded skills are the cognitive ones the automation performs; experts spend more of debugging on comprehension and build fuller models of the program ([Gugerty and Olson 1986](https://www.academia.edu/72477661/Expertise_in_debugging_computer_programs_A_process_analysis), read today; [Vessey 1985](https://www.cs.kent.edu/~jmaletic/cs69995-PC/papers/vessey85.pdf), read today). Moderate.
How: when a test fails in a learning task, offer once: "Want to call the cause first?" The user names a hypothesis and a check. The agent runs the user's check first. The user's hypothesis and the actual cause are shown side by side.

**L5. "Your line" targets the one germane decision, is graded by the build, and fades.**
Why: completion problems and fading (Atkinson, Renkl and Merrill 2003); generation (Bertsch); germane vs extraneous load (Sweller, memory); a working precedent exists in Claude Code's Learning style, which leaves `TODO(human)` for "a piece with a real design decision" [verified: https://code.claude.com/docs/en/output-styles]. Moderate.
How (founder decision 2): only when the user is new to the idea ("not yet" or "with help" on that topic). The line is the one that carries the concept, never boilerplate, names, or a path. The user writes it and, in a phrase, names the principle it serves. The tests grade it. If the user is stuck: hint ladder, then the agent writes it and the attempt is recorded as worked example, not success. As the topic level rises, the gap grows (line, then function, then design). At "transfers" there is no gap; the user designs first and the agent reviews. A user in flow can decline with one word, and the agent writes it.

**L6. Every prediction is closed against the real outcome, with the gap explained.**
Why: productive failure needs the consolidation phase (Sinha and Kapur 2021, carried); hypercorrection needs feedback on the reasoning (Metcalfe). Strong.
How: the prediction must be answerable from what the user was shown, and the outcome must be deterministic (the critique's M1). When the build ends, one block: "You said X. It did Y. The difference is Z, at `path:line`."

**L7. Reviews are free recall in a new instance, with no help on screen.**
Why: recall beats recognition for the testing effect (Roediger and Karpicke, memory; Dunlosky's practice testing); Bastani (help on screen removes the benefit); varied instances support transfer (D.4). Strong.
How: the review shows only the question. Code, the old answer and feedback appear after the user commits. Each review of a topic is a new instance: a different file, a variation, a bug, a design choice. Multiple-choice options only for first-exposure predictions.

**L8. Space reviews; the exact ladder matters less than spacing at all.**
Why: spacing g = 0.74 (Latimier); overshooting gaps costs less than undershooting (Cepeda); reported null for expanding vs uniform (Latimier, unconfirmed); spaced questions during work lasted two years (Kerfoot). Strong.
How: keep a simple expanding ladder. When the daily cap (founder decision 3, at most 3) leaves items waiting, choose by highest forgetting risk and sure misses first, and let the rest wait. Log every review in a format a modern scheduler can replay later (R1 rule 10). Do not build adaptive scheduling before there is data per user; when to switch "needs to be measured".

**L9. Interleave confusable ideas; hide the topic name on transfer items.**
Why: interleaving (Brunmair and Richter); noticing which principle applies is the transfer bottleneck (Gick and Holyoak, memory). Strong (lab).
How: mix the 3 daily items across areas and across projects. On transfer, diagnosis and interleaved items show only the area until the user commits.

**L10. Fade support per topic, on evidence.**
Why: expertise reversal (Kalyuga); a general product serves everyone from first-year to staff engineer in a new domain. Strong.
How: support depends on the topic's current evidence, not on years of experience or a global "level". A self-declared expert gets one probe question on a new topic to place them, not a tutorial.

**L11. Teach transfer by comparison and by naming the principle.**
Why: analogical encoding (Gentner et al.); fading plus principle prompts gave far transfer (Atkinson et al.). Strong (lab).
How: when the same principle appears in a second project or file, the review asks the user to compare the two and name what is shared. "Your line" asks for the principle's name. The record links topics across repos.

**L12. Collect confidence with every answer; treat sure misses as the key event.**
Why: hypercorrection (Metcalfe); AI-driven overconfidence (Prather, Lehmann). Strong.
How: confidence is part of the same answer action, on a 3-level scale with plain meanings. Sure misses return sooner and are listed first in the record. Calibration is scored with a proper scoring rule and shown only with enough data; an "I don't know" is never counted in calibration.

**L13. Feedback is about the task and the reasoning, never the person or others.**
Why: Kluger and DeNisi; ability praise (Mueller and Dweck 1998, memory; replication debate). Strong.
How: "Correct." / "Not quite." / "No." plus the reason, evidence from the code, and where next. No praise, no comparison, no percentiles.

**L14. No points, streak counters, badges, leaderboards, or loss framing.**
Why: Hanus and Fox; Kluger and DeNisi (normative feedback); Silverman and Barasch (broken streaks); SDT. Moderate.
How: the only "level" is the record's level per topic, which can go down. A consistency view, if any, is unlit and lit cells with no counter and no broken state. The one daily reminder (founder decision 7) says only what is due and how long it takes.

**L15. Autonomy first: the user picks goals and can skip at no cost.**
Why: SDT; Lehmann (people choose the easy path, so the product must make the good path cheap rather than forced). Moderate.
How: at setup the user chooses areas to grow in (from the skill model in Part G). "Skip" and "just do it" always work at once. The user chooses whether a task is a learning task, with a sensible default that the user sets once.

**L16. Rehearse rare, high-stakes work by simulation.**
Why: aviation practice and Casner's recommendation; SRE Wheel of Misfortune [verified: practice exists, https://dastergon.github.io/wheel-of-misfortune/instructions.html; outcomes unverified]; Kahneman and Klein (real work gives poor feedback on rare judgments). Moderate (practice), weak (measured outcomes).
How: opt-in drills built from the user's own history: a reverted real bug on a scratch branch, a replayed incident timeline with logs revealed step by step, a rollback decision with the outcome hidden. Each drill grades process (testable hypothesis, safe first action) as well as the answer.

**L17. Practise verifying agent output as a skill in its own right.**
Why: Bainbridge (the monitor becomes deskilled and monitoring is hard); Lee et al. (trust in AI goes with less checking); Bacchelli and Bird (understanding the change is the core of review). Speculative as a training target, well motivated.
How: occasionally, in a learning task, the agent tells the user "one thing in this diff is wrong or risky; find it before I run the tests." Only with consent, only on a scratch branch or a reversible change, never shipping a seeded defect. Measure the find rate over time.

**L18. Make the agent model expert process aloud only when asked or after the user tried.**
Why: cognitive apprenticeship (modeling, reflection); the order effect in Lead-and-Reveal. Moderate.
How: after the user's own hypothesis or design, the agent shows how it would approach the same thing ("I would first check X because Y"). Before the user tries, it does not, unless the user asks; conceptual questions are always answered at once (R1 rule 16).

**L19. Measure the product with within-person, randomized topic designs.**
Why: standard experimental method; self-report is unreliable (L3); between-user comparisons are confounded by who opts in. Strong (method).
How: for a given technique (for example "your line" or "call the cause first"), randomly assign each new topic for a user to get it or not, then compare delayed unaided review results between the two sets of topics within the same person. Runs locally on the user's own record; pooled results only from users who opt in to share.

### F.1 Founder decisions checked against the evidence

| Decision | Verdict |
|---|---|
| 1. Local git repo for the record | No learning-science conflict. It makes a cross-project, per-user record possible, which L11 needs. |
| 2. "Your line" on | Supported (completion problems, generation, Claude Code Learning style precedent). Add: germane line only, principle named, graded by tests, fades, declinable (L5). |
| 3. At most 3 due items a day | Supported. Kerfoot's design was short daily questions; overshooting a gap is the cheaper error (Cepeda). Add a priority order (L8). |
| 4. One confirmation tap on phone | No learning-science bearing. |
| 5. Letter shortcuts off | No learning-science bearing. |
| 6. Parity on all surfaces | Supported indirectly: none of the rules above need a special UI, only message order, a record, and a review channel. |
| 7. At most one reminder a day at a chosen time | Supported by SDT (autonomy) and the streak evidence. |

I do not challenge any founder decision.

---

## Part G. What "a much better engineer" means, measurably

Code recall ("what does `asyncio.gather` return") is the least important target. The evidence says the eroding skills are diagnosis, comprehension, checking and self-assessment (Part B). Developers spend about 58% of their time on program comprehension, and seniors less than juniors ([Xia et al. 2018](https://xin-xia.github.io/publication/TSE17.pdf), read today). Interviews with 59 Microsoft engineers found that great engineers are described mostly by decision-making and how they affect others, not by language knowledge ([Li, Ko and Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf), read today via summary).

The product should model skill as **dimensions with observable tasks**. Each dimension below says what to measure and how, unaided. None of these measures exists as a validated instrument for this product; every threshold "needs to be measured".

| Dimension | What it means | Observable measure (unaided) | Where the evidence comes from |
|---|---|---|---|
| **Reading unfamiliar code** | Build an accurate model of code you did not write, quickly. | Trace-and-predict accuracy on a function from the repo; locating where a behaviour lives in a module; explaining a module's job in two sentences graded against a rubric. | Xia et al. (time share); Kazemitabaar 2025 (Trace-and-Predict); Shen and Tamkin (code-reading items). |
| **Debugging** | Form testable hypotheses, localise, and confirm cause before fixing. | On an injected or reverted real bug: was the first hypothesis testable; was the check informative; was the cause right; how many steps to localise. | Gugerty and Olson; Vessey; Shen and Tamkin. |
| **Testing** | Write tests that would catch the bugs that matter, and predict what tests will show. | Predict which test fails and why; write a test that fails before a fix and passes after; whether the user's tests catch a seeded mutation (mutation testing as a proxy, speculative as a learning measure). | Mutation testing practice (memory); prediction research (St. Hilaire). |
| **Verifying agent output** | Review a change for correctness and risk without running it first. | Find rate for one seeded issue in a diff (L17); quality of review comments against a rubric. | Bainbridge; Lee et al.; Bacchelli and Bird. Speculative as a dimension. |
| **System design judgment** | Choose between designs with reasons, and foresee failure modes. | Given two designs, pick and give the trade-off; predict which will make a stated future change hard; later, check the prediction when that change happens. | Kahneman and Klein (feedback is what builds judgment); Petre and van der Hoek on design expertise (memory). Weak to moderate. |
| **Operating in production** | Triage from telemetry, choose a safe first action, roll back well. | In a replayed incident: first hypothesis from logs and metrics, first action and its risk, time to a safe mitigation in the drill. | SRE practice (Wheel of Misfortune); Casner (simulator practice). Weak for outcomes. |
| **Decomposition and specification** | Break a goal into steps and state what done looks like. | Before the agent plans: the user lists the steps and acceptance checks; compare with what the build needed. | Lead-and-Reveal (state the step first). Speculative as a measure. |
| **Calibration** | Know what you know. | Brier score of confidence against outcome across reviews; rate of sure misses. | Metcalfe; Rhodes and Tauber; Prather. |
| **Conceptual knowledge** | Know the transferable ideas (idempotency, backpressure, consistency models). | Spaced free-recall and transfer items in new contexts. | Retrieval and transfer literature. |

Rules for measuring these:

- **Unaided, delayed, new instance** (L2). A skill shown only with the agent's help, or only on the day, is not yet a skill.
- **Process and outcome both.** A right diagnosis guessed with no check is "with help" at best (R1 rule 16).
- **Field evidence counts most.** The strongest signal is the user doing the thing for real without the agent: fixing a production bug, designing a change, answering a colleague. The record should let the user log that, with a link to the commit or PR. Moderate.
- **Never measure skill by activity.** Questions answered, minutes in the product, or number of reviews are not skill.
- **Show decay honestly.** A topic that held at one review and failed the next is uncertain now. The record says so.

---

## Part H. What never to do: things that feel like learning but are not

Each item is common in learning products or coding tools. Each produces the feeling of learning with little durable effect, or actively harms.

| Do not | Why | Evidence | Strength |
|---|---|---|---|
| Treat reading the agent's explanation as learning. | Passive mode; low-utility techniques like rereading do not reliably help. | Dunlosky 2013; Chi and Wylie 2014 | Strong |
| Let the agent debug while the user watches, in a learning task. | Lowest-scoring pattern in Shen and Tamkin. | Shen and Tamkin 2026 | Moderate |
| Count an explain-back right after the build as mastery. | Measures working memory of a just-read solution. | Rhodes and Tauber; critique B1 | Strong |
| Use multiple choice for reviews. | Recognition, not recall; the options carry the answer. | Testing-effect literature; critique M2 | Strong |
| Show the answer, hint or code in the same message as the question. | Removes the generation. | Bastani; R1 | Strong |
| Print the principle's name on a transfer question. | Removes the hard part of transfer. | Gick and Holyoak (memory); critique M3 | Strong |
| Ask "does that make sense?" and treat "yes" as evidence. | Self-assessment of understanding is unreliable, more so with AI. | Lehmann; Prather; Deslauriers | Moderate |
| Optimise for time in app, questions answered, or streak length. | Rewards volume and easy items; streaks become the goal. | Silverman and Barasch; Hanus and Fox | Moderate |
| Add points, badges, leaderboards, or "better than X% of users". | Normative feedback harms; controlling rewards crowd out intrinsic motivation. | Kluger and DeNisi; Deci et al. 1999; Hanus and Fox | Moderate to strong |
| Praise ability ("you're a natural"). | Shifts attention to self. | Kluger and DeNisi; Mueller and Dweck (memory) | Moderate |
| Match content to "learning styles". | No good evidence that matching helps. | Pashler et al. 2008 (memory) | Strong |
| Give long tutorials to people who already know the area. | Expertise reversal. | Kalyuga 2007 | Strong |
| Make "your line" a trivial or boilerplate line. | Extraneous load; no germane idea to learn. | Sweller (memory) | Moderate |
| Leave a gap or prediction without closing it against the outcome. | No consolidation, so a wrong idea can stick. | Sinha and Kapur; Metcalfe | Strong |
| Use loss framing, guilt, or more than one reminder a day. | Undermines autonomy; broken streaks lower engagement. | SDT; Silverman and Barasch | Moderate |
| Claim the product makes users "10x" or "expert". | Not supported; deliberate practice effects are smaller than claimed. | Macnamara et al. 2014 | Strong |
| Ship a seeded defect to a real branch for a drill. | Safety and trust; not a learning question but a hard line. | Product rule | Not applicable |

---

## Part I. Where the evidence is weak, and the cheapest ways to learn more

### I.1 Weak points

| Product assumption | State of evidence | Risk |
|---|---|---|
| The harm in Shen and Tamkin lasts and grows with agentic tools | Immediate test only; authors expect a larger effect with agents but did not test it. | The size of the problem is unknown. Needs to be measured. |
| Learning inside the user's own real work transfers better than separate practice | Indirect (Arthur et al. context similarity; Blume et al.). No direct test in software. | Users may learn the codebase, not the principle. L11 is the mitigation. |
| "Your line" improves learning more than explain-back alone | Completion problems are well supported in instruction; no test inside agent workflows. Claude Code's Learning style exists but I found no published outcome data for it [unverified]. | Users may find it annoying and turn it off. Measure with L19. |
| Verification of agent output is trainable and transfers | No direct study found. | Could be a near-transfer skill tied to one codebase. |
| Simulations of incidents build production skill | Widely practised; I found no controlled outcome study for software. | Effort without proven gain; keep opt-in. |
| LLM grading against a fixed rubric is reliable | Not established here. | Grade drift; record the rubric before the question; spot-check. |
| Three items a day is enough for retention across many topics | Kerfoot used daily short questions; the right load per topic count needs to be measured. | Backlog grows for heavy users; priority order mitigates. |
| No gamification does not hurt return rates for this population | No evidence for professional developers. | Fewer reviews done. Measure return rate as a guardrail. |
| The weakest users benefit | Lehmann and Prather suggest they are most at risk and least able to self-assess. | The product may help strong users most. Design defaults for the weakest. |

### I.2 Cheapest experiments (local, on users who opt in)

| ID | Question | Method | Measure |
|---|---|---|---|
| X1 | Does "your line" beat explain-back alone? | L19: randomize new topics to "your line + explain-back" vs "explain-back". | 7- and 21-day unaided review accuracy per arm. |
| X2 | Does "call the cause first" improve debugging? | Randomize failing-test moments in learning tasks to offer or not. | Debugging items at 7 and 21 days; process score in later drills. |
| X3 | Does cross-project comparison improve transfer? | For topics seen in two repos, randomize a comparison review vs two separate reviews. | Accuracy on a third-context transfer item. |
| X4 | Does the calibration view improve calibration? | Show it to half of opted-in users for a month. | Change in Brier score. |
| X5 | Does verification practice raise find rate? | Opt-in seeded-issue reviews over several weeks. | Find rate on new seeded issues, and on real defects found in later reviews. |
| X6 | What daily cap holds retention without backlog? | Users choose 1, 2 or 3; observe. | Overdue count and review accuracy over time. Observational. |
| X7 | Does a one-time "effort feels slow" onboarding line reduce skipping? | Randomize onboarding copy. | Skip rate at learning points in the first two weeks. |

---

## Part J. Sources

Read in this session (abstract, summary quoting the paper, or full text):

- Shen and Tamkin 2026, [arXiv 2601.20245](https://arxiv.org/abs/2601.20245); [Anthropic summary](https://www.anthropic.com/research/AI-assistance-coding-skills)
- Lehmann, Cornelius and Sting 2025, [arXiv 2409.09047](https://arxiv.org/abs/2409.09047)
- Kazemitabaar et al. 2023, [arXiv 2302.07427](https://arxiv.org/abs/2302.07427)
- Kazemitabaar et al. 2025, [arXiv 2410.08922](https://arxiv.org/abs/2410.08922)
- Darvishi et al. 2024, [Adelaide record](https://digital.library.adelaide.edu.au/items/99e9a0ee-4feb-405c-8e66-062c6b67aa11)
- Kosmyna et al. 2025, [arXiv 2506.08872](https://arxiv.org/abs/2506.08872)
- Gerlich 2025, [DOAJ](https://doaj.org/article/d5c17dd91ce64775a065095d8af730ce)
- METR 2025, [summary by Simon Willison](https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/)
- Kestin et al. 2025, [record](https://library.kab.ac.ug/Record/doaj-art-594959a5f4f94bd8a7ad3d534581f3ec/Details)
- Bainbridge 1983, [PDF](https://gwern.net/doc/sociology/technology/1983-bainbridge.pdf)
- Casner et al. 2014, [Human Factors](https://journals.sagepub.com/doi/10.1177/0018720814535628)
- Budzyń et al. 2025, [Warwick record](https://wrap.warwick.ac.uk/id/eprint/191005)
- Arthur et al. 1998, [PDF](https://Www.Gwern.net/doc/psychology/spaced-repetition/1998-arthur.pdf)
- Dunlosky et al. 2013, [APS release](https://www.psychologicalscience.org/news/releases/which-study-strategies-make-the-grade.html)
- Rowland 2014, [DOI](https://doi.org/10.1037/a0037559); Adesope et al. 2017, [DOI](https://doi.org/10.3102/0034654316689306)
- Latimier, Peyre and Ramus 2021, [Springer](https://link.springer.com/10.1007/s10648-020-09572-8)
- Bertsch et al. 2007, [PubMed](https://pubmed.ncbi.nlm.nih.gov/17645161/)
- Bisra et al. 2018, [PDF](https://www.Gwern.net/doc/psychology/spaced-repetition/2018-bisra.pdf)
- Chi and Wylie 2014, [PDF](https://chilab.asu.edu/sites/default/files/lcl/chiwylie2014icap_2.pdf)
- Atkinson, Renkl and Merrill 2003, [record](https://asu.elsevierpure.com/en/publications/transitioning-from-studying-examples-to-solving-problems-effects-/)
- Deslauriers et al. 2019, [PDF](https://openlab.citytech.cuny.edu/gamelab/files/2023/01/Deslauriersa-et-al-2019.pdf)
- Collins, Brown and Newman 1989, [summary](https://en.wikipedia.org/wiki/Cognitive_apprenticeship)
- Macnamara, Hambrick and Oswald 2014, [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/)
- Sonnentag and Kleine 2000, [record](https://kops.uni-konstanz.de/entities/publication/3137afd2-22a3-448a-a3b8-e6a8e7d21e2f)
- Kahneman and Klein 2009, via [McKinsey interview](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/strategic-decisions-when-can-you-trust-your-gut)
- Blume et al. 2010, [PDF](https://kops.uni-konstanz.de/bitstreams/c871fed9-39d7-429b-a953-3c817c60a254/download)
- Gentner, Loewenstein and Thompson 2003, [record](https://dedregentner.owlstown.net/publications/38525-learning-and-transfer-a-general-role-for-analogical-encoding)
- Kerfoot 2009, [PubMed](https://pubmed.ncbi.nlm.nih.gov/19375095/)
- Bacchelli and Bird 2013, [PDF](https://huang.isis.vanderbilt.edu/cs4278/readings/codereview.pdf)
- Xia et al. 2018, [PDF](https://xin-xia.github.io/publication/TSE17.pdf)
- Li, Ko and Zhu 2015, [PDF](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- Gugerty and Olson 1986, [record](https://www.academia.edu/72477661/Expertise_in_debugging_computer_programs_A_process_analysis); Vessey 1985, [PDF](https://www.cs.kent.edu/~jmaletic/cs69995-PC/papers/vessey85.pdf)
- Ryan and Deci 2000, [record](https://bibbase.org/network/publication/ryan-deci-selfdeterminationtheoryandthefacilitationofintrinsicmotivationsocialdevelopmentandwellbeing-2000)
- Sailer and Homner 2020, [Springer](https://link.springer.com/article/10.1007/s10648-019-09498-w)
- Hanus and Fox 2015, [dblp](https://dblp.org/rec/journals/ce/HanusF15)
- Wheel of Misfortune, [instructions](https://dastergon.github.io/wheel-of-misfortune/instructions.html)
- Claude Code output styles, [docs](https://code.claude.com/docs/en/output-styles)

Carried from R1 (documented there, not re-read today): Bastani et al. 2025; Fan et al. 2025; Prather et al. 2024; Lee et al. 2025; Cepeda et al. 2008; Brunmair and Richter 2019; St. Hilaire et al. 2024; Sinha and Kapur 2021; Metcalfe 2017; Rhodes and Tauber 2011; Kluger and DeNisi 1996; Kalyuga 2007; Deci, Koestner and Ryan 1999; Silverman and Barasch 2023; Duolingo blog posts; Bjork and Bjork 2011.

From memory, not checked (treat as reported): Ericsson, Krampe and Tesch-Römer 1993; Barnett and Ceci 2002; Gick and Holyoak 1980 and 1983; Roediger and Karpicke 2006; Kornell, Hays and Bjork 2009; Mueller and Dweck 1998; Pashler et al. 2008; Sweller on cognitive load; Petre and van der Hoek on design expertise; mutation testing practice.
