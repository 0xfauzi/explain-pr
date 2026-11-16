# Evidence supports predicting system effects first

The evidence as of November 2026 points to one product shape. It is an optional tool that works across agents. At the start of an agent task, and only on selected changes, it asks the developer to mark on a small module diagram what the change will touch. After the agent finishes, it draws the computed change beside that prediction and keeps a record over months. The problem it addresses is measured: two randomised experiments found that people who let AI write the code understood the result clearly less (Cohen's d = 0.738 in one, d > 0.80 in the other), and the best-documented incidents came from misjudging what a change would reach, not from misreading lines. The method is not measured. No study in any population has tested prediction of software change impact as a way to learn. No study shows that any higher-level engineering skill, once trained, improves results with agents. The learning research supports a committed guess followed by fast feedback, but mostly in students on recall tests. It gives no support for the claim that months of practice build a skill that carries to other systems. The parts are technically possible today: every major agent exposes each edit before it lands, and a module-level before-and-after picture can be computed from git without a language model. Among the tools found, none asks for the developer's own system-level prediction before the change. The product would therefore work ahead of the evidence, and its most defensible ambition is to produce that evidence itself.

## How to read the labels

Each finding carries four labels. **Type** is one of: controlled study, observational data, survey (interview studies are included here and marked), incident, opinion. Tool facts add a sixth type, official documentation. **Sells AI** says whether the source sells AI coding tools or tools that review or measure AI code. **Strength** is how far the finding can be relied on for this question: strong, moderate or weak. **Figure status** is one of three. "Read" means the research notes record that the figure was read in the primary source. "Abstract only" means it was seen in an abstract or record, not the full text. "Unverified" means it came from a search summary or secondary coverage. Every unverified figure in this report is labelled as such. Each section keeps measured findings in a table and puts claims, opinion and inference in the prose after it.

## A. Developers lose track of system effects, and the cost is mostly inferred

### Measured findings

| Finding | Source | Type | Sells AI | Strength | Figure status |
|---|---|---|---|---|---|
| 52 mostly junior engineers learned an unfamiliar Python library. The AI group scored **50%** on a later quiz against **67%** for hand-coding (Cohen's d = 0.738, p = 0.01). The largest gap was on debugging questions. The AI group was about two minutes faster, not significant (p = 0.391). The tool was a chat sidebar, not an agent. | [Anthropic, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills) | Controlled study | Yes. The result runs against the vendor's interest. | Moderate: randomised, small, one short task, tested minutes later | Read |
| In the same study, low scorers delegated (AI delegation 39%, progressive reliance 35%, iterative AI debugging 24%; n = 4 each). High scorers engaged (generation-then-comprehension 86%, n = 2; hybrid code-explanation 68%, n = 3; conceptual inquiry 65%, n = 7). The authors draw no causal link. | [Anthropic, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills) | Controlled study, exploratory sub-analysis | Yes | Weak: groups of 2 to 7 | Read |
| 54 computer science students (59 recruited) built a small web game with either an agent (Aider with GPT-4.1) or a chatbot with no code access. Agent users were faster and more accurate at first but scored lower on comprehension of their own code (**p < 0.002, Cohen's d > 0.80**). They rated their own understanding lower (3.3 against 4.2 on a 1 to 5 scale) and the agent more helpful (4.7 against 3.3). Most still preferred the agent. | [Balepur et al., arXiv 2607.26375](https://arxiv.org/html/2607.26375v1) | Controlled study (preprint) | No | Moderate: the only randomised agent experiment on comprehension found; students, small task, quiz written and scored by a language model | Read |
| In the agent group, people who auto-accepted edits had the lowest mean comprehension (0.615, n = 6). People who accepted each file one at a time had the highest (0.777, n = 7). | [Balepur et al.](https://arxiv.org/html/2607.26375v1) | Controlled study, exploratory | No | Weak: very small groups, correlational | Read |
| 16 experienced open-source developers worked on 246 real issues. They forecast a 24% speed-up, were measured **19% slower**, and afterwards believed they had been 20% faster. This study measured time, not comprehension. | [METR, Jul 2025](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) | Controlled study | No | Strong for the gap between belief and measurement in that setting. Weak as evidence about comprehension. METR now calls the result out of date. | Read |
| METR's late-2025 follow-up (57 developers, 800+ tasks) gave estimates whose intervals both include zero. METR calls the data "an unreliable signal". 30% to 50% of developers said they withheld tasks they did not want to do without AI. | [METR, Feb 2026](https://metr.org/blog/2026-02-24-uplift-update/) | Controlled study, compromised by selection | No | Weak, by METR's own account | Read |
| 13 professional developers were observed and 99 surveyed. 9 of 13 reviewed every agent change, through diffs and tests. 8 of 13 said agents did more than asked. Six stressed that human understanding of the codebase is needed for production review. Comprehension was not measured. | [Huang et al., arXiv 2512.14012](https://arxiv.org/html/2512.14012) | Observational data plus survey | No | Weak to moderate: small, self-selected, authors note a bias toward AI-positive developers | Read |
| In "over 1,100 developers": 96% do not fully trust that AI code is functionally correct. 48% say they always check AI-assisted code before committing. 38% say reviewing AI code takes more effort than reviewing a colleague's code. | [Sonar, Jan 2026](https://www.sonarsource.com/company/press-releases/sonar-data-reveals-critical-verification-gap-in-ai-coding/) | Survey | Yes: Sonar sells code verification products | Weak to moderate: self-report, sampling method not stated | Read |
| Telemetry from 22K developers and 4K teams, high against low AI adoption: PR size +51%, bugs per developer +54%, median review time "5X", incidents per PR about 3X, deployments per week -11.7%, task throughput +33.7%. | [Faros AI, Q2 2026](https://www.faros.ai/research/ai-acceleration-whiplash) | Observational data | Yes: Faros sells engineering analytics | Weak to moderate: large and real, but correlational, method behind a download form | Read (landing page only) |
| After open-source projects adopted Cursor, velocity rose for a time. Static analysis warnings and code complexity rose and stayed up, and predicted later slowdown. | [He et al., arXiv 2511.04427](https://arxiv.org/abs/2511.04427) | Observational data (difference-in-differences) | No | Moderate to strong for direction | Abstract only; no effect sizes seen |
| 623 million analysed changes, 2023 to 2026: refactored ("moved") code fell from 21% of changed lines in 2022 to 3.8% in 2026 to date. Method calls per thousand changed lines fell 35% (343 to 223). Changes that touch code older than 12 months fell from 1.7% to 0.46%. | [GitClear, 2026](https://www.gitclear.com/write_only_mode_ai_research) | Observational data | Yes: GitClear sells developer analytics | Weak to moderate: AI is attributed by period, not by line; method paywalled | Read (public page) |
| Across 20,574 real agent sessions, 91.49% of visible resolutions of developer-agent misalignment needed explicit user correction. 90.50% of episodes cost effort and trust "rather than irreversible system damage". | [Tang et al., arXiv 2605.29442](https://arxiv.org/abs/2605.29442) | Observational data | Not established | Moderate that misreading of intent is common | Abstract only |

Four incidents are documented. The best is a first-person account by Alexey Grigorev. He let Claude Code run Terraform against a state file that was out of date, did not read the plan, and did not stop a `terraform destroy` that he assumed would remove only duplicates. It destroyed the production database and its automated snapshots, including 1,943,200 rows in one table. Recovery took about 24 hours ([Grigorev, Mar 2026](https://aishippingblog.com/p/how-i-dropped-our-production-database); incident; the author sells AI courses and has no interest in the failure; strong as a single case; read). Amazon confirmed a disruption to an AWS service in December 2025 after engineers let its Kiro agent make changes. Amazon attributes it to "misconfigured access controls - not AI" and added mandatory peer review for production access ([The Register, Feb 2026](https://www.theregister.com/2026/02/20/amazon_denies_kiro_agentic_ai_behind_outage/); incident, contested; Amazon sells Kiro; moderate; read via The Register, not the original report). Two more cases, PocketOS in April 2026 and Replit in July 2025, are founder accounts reached only through press coverage. Both are unverified ([Computing](https://www.computing.co.uk/news/2026/ai/ai-coding-agent-goes-rogue); [eWeek](https://www.eweek.com/news/replit-ai-coding-assistant-failure/); incident; weak to moderate).

### What the measurements show

The best-supported claim in this area is narrow. Handing code generation to AI lowers immediate comprehension of the result. Two randomised experiments agree in direction and size across different populations and tool types. The claim holds only for small, new, self-contained tasks, tested minutes afterwards.

The loss was not uniform. In both experiments it followed how the person worked. Pure delegation and auto-accept scored lowest. Asking conceptual questions, or generating and then questioning the output, scored highest. This is the main empirical reason to think a tool can help: the same agent output is understood or not depending on what the person does. The groups behind this result contain two to seven people.

The costly failures are not about lines of code. In each well-documented incident, the person could have read every line the agent wrote and still been surprised. What they did not know was which state the agent was working from, what its credentials allowed, what a proposed command would touch, and what could not be undone. Experienced developers do review agent output, but through diffs and tests. A diff shows lines changed, not effect on the system.

### Claims without measurement

"Cognitive debt" and "comprehension debt" are terms, not measured quantities. Margaret-Anne Storey defines cognitive debt as team-level erosion of shared understanding, and intent debt as missing rationale, goals and constraints. Her evidence is one anecdote of a student team. She asks "How do we measure cognitive debt?" herself ([Storey, Feb 2026](https://margaretstorey.com/blog/2026/02/09/cognitive-debt/); [Storey, arXiv 2603.22106](https://arxiv.org/abs/2603.22106); opinion by a senior researcher; sells AI: no; weak as evidence, useful as a definition; read, paper at abstract level). Addy Osmani describes comprehension debt as the gap between how much code exists and how much any person understands ([Osmani, Mar 2026](https://addyosmani.com/blog/comprehension-debt/); opinion; his employer Google sells AI tools; weak as evidence; read).

The research notes assemble six levels at which a developer can fail to understand an agent's change. This list is an inference from the sources. It is not published anywhere as a tested classification.

| Level | What is not understood | Evidence status |
|---|---|---|
| 1. Code | What the new lines do | Measured; lowered by delegation |
| 2. Behaviour and edge cases | Implicit choices on errors, data structures, performance | Argued; partly measured through debugging scores |
| 3. Scope | What the agent did beyond the request | Observed in the field (8 of 13); not counted at scale |
| 4. System effect | What else the change touches: coupling, duplication, drift | Visible in repository data; never measured as human comprehension |
| 5. Operational effect | Environment, state, credentials, what cannot be undone | The cause of the documented incidents |
| 6. Intent | Why this approach, what was rejected | Argued by Storey; unmeasured |

Diffs and tests cover level 1 and part of level 2. The owner's constraint, nothing at the level of code lines, places the product at levels 3 to 6. That is where the evidence of harm sits and where measurement is thinnest.

### What it costs

The cost is inferred, not priced. The signals are longer review, more incidents per change, and later slowdown from complexity. They come from one independent quasi-experiment and two vendors' telemetry. Sources with different interests agree on direction. That raises confidence in the direction and not in any figure. No study links a measured comprehension deficit to a later measured cost in the same people or team.

### Unknown

No controlled study measures comprehension by experienced engineers using an agent on a large existing codebase. No study asks a developer to state what an agent's change touched and scores the answer. Retention beyond minutes is unmeasured. There is no long-run measurement of skill loss in working engineers: "skill atrophy" in professionals is a hypothesis. No telemetry reports the share of agent changes accepted without being read. Public incidents are almost all data destruction. Quiet failures such as security holes or slow architecture drift are poorly documented. There is no base rate for destructive agent actions.

## B. Three skills have the best support, and none is shown to be trainable

### Measured and reported findings

The notes rate each skill twice. **P** is how well the sources show the problem is real. **S** is how well they show that the skill reduces the problem. The ranking is the note-writer's judgment. No study compares these skills with each other.

| Rank | Skill | Main sources | P | S |
|---|---|---|---|---|
| 1 | System model: what the parts are, how data moves, where state is kept | Li, Ko, Zhu 2015; Huang et al. 2025; Anthropic trial | Moderate to strong | Weak |
| 2 | Stating intent and acceptance before work starts | Huang et al.; Tang et al. 2026 | Moderate to strong | Weak |
| 3 | Judging outcomes against evidence, not output volume | Huang et al.; Tang et al. | Moderate | Weak |
| 4 | Calibration: knowing how far to trust your own sense of progress | METR 2025 | Strong in one small trial | None |
| 5 | Splitting and ordering work into steps that can each be checked | Huang et al.; Li et al. | Moderate | Weak |
| 6 | Deciding what to delegate | Anthropic staff survey; Huang et al. | Moderate | Weak |
| 7 | Judging the reach of a change; protecting invariants and contracts | Li et al.; Huang et al.; Tang et al. | Weak to moderate | None |
| 8 | Product and domain judgment | Huang et al.; Li et al. | Moderate | Weak, at organisation level only |
| 9 | Risk, reversibility, rollout and production operation | Tang et al.; DORA 2025 (unverified) | Moderate, at organisation level | None |

The sources behind the top of the table are these. In 59 interviews at Microsoft, engineers described great colleagues as building "an accurate mental model of dependencies and connections". The study lists 53 attributes and measures no outcomes ([Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf); survey by interview; sells AI: not as the subject of the paper, though authors include Microsoft staff; P moderate, S none; read). Experienced developers cited their own domain expertise as critical for agent use (65 survey mentions). They rated integration with existing or legacy code unsuitable for agents 17 to 3, and "following well-defined plans" suitable 28 to 2. They rated "one-shotting code without verification" unsuitable 23 to 5 ([Huang et al.](https://www.arxiv.org/abs/2512.14012); observational data plus survey; sells AI: no; moderate as attitude data; read). The METR gap between belief and measurement is the basis for calibration ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/); controlled study; sells AI: no; read). It shows miscalibration under AI use. It does not show that calibration can be trained.

Usage data shows where human effort is moving. In 200,000 internal Claude Code transcripts from February to August 2025, average human turns per transcript fell from 6.2 to 4.1, and the longest run of consecutive tool calls rose from 9.8 to 21.2. More than half of surveyed Anthropic engineers said they can fully delegate only 0 to 20% of their work ([Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic); observational data plus survey; sells AI: yes; moderate; read). Each human decision now covers more generated work. That raises the weight of the decisions made before a run and after it. This last sentence is an inference.

### Claims and disagreements

Practitioner writing agrees that system understanding, clear intent, verification and judgment gain value. All of it is opinion, and several positions (Willison, Beck, Majors) reached the notes only through search summaries, so they are unverified here. Two disputes are open.

The first dispute is whether higher-level skill can be held without code-level fluency. Participants in the Huang study named strong code comprehension and debugging as part of effective agent use ([Huang et al.](https://www.arxiv.org/abs/2512.14012); read). A 2020 follow-up survey to Li et al. is reported to rank coding competence among the most important attributes ([Li, Ko, Begel 2020](https://link.springer.com/10.1007/s10664-019-09773-y); survey; unverified). A product that excludes code-level work takes one side of an unsettled question. The owner should know this.

The second dispute is whether planning and design stay human work. Experienced developers split 13 suitable to 23 unsuitable on agents for high-level plans ([Huang et al.](https://www.arxiv.org/abs/2512.14012); read). Anthropic staff called the line for design and taste a "moving target" ([Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic); survey by interview; sells AI: yes; read).

### The central weakness

Almost every source shows that a problem exists. Almost none shows that a named skill, once trained, reduces it. The closest results are correlational. Longer-tenured Claude users had about 4 percentage points higher conversation success after controls, they iterated more, and they were "much less likely" to use directive, delegating patterns. Success was judged by the model itself and the sample is all users, not developers ([Anthropic Economic Index, Mar 2026](https://www.anthropic.com/research/economic-index-march-2026-report); observational data; sells AI: yes; weak; read). METR found no measured difference in speed-up by developer or task type ([METR, Feb 2026](https://metr.org/blog/2026-02-24-uplift-update/); read).

### Unknown

Whether any of the nine skills, measured in a person, predicts fewer defects or incidents with agents. Whether any can be trained by a tool so that it carries into real work. Whether findings from 2025 tools hold for late-2026 tools. No empirical study of software architects and no measured senior-against-junior comparison was found. No measurement exists of erosion in design, decomposition, risk judgment or product judgment.

## C. Learning research backs a committed guess with fast feedback, asked rarely

### Measured findings

Strength here is rated for this product: experienced engineers and system-level judgment. Most of the sources below do not sell AI tools. The exception is noted.

| Claim | Main source | Type and population | Strength for this product | Figure status |
|---|---|---|---|---|
| A committed guess before the answer improves retention of the thing guessed: **g = 0.54**. With a generated answer g = 0.65. With only reading the question g = 0.22. | [St. Hilaire et al. 2024](https://doi.org/10.3758/s13423-023-02353-8) | Meta-analysis of controlled studies; mostly undergraduates; recall and comprehension tests | Moderate | Read |
| The benefit does not spread to material not asked about: **g = 0.04**. | Same | Same | Moderate | Read |
| Conceptual questions gave a smaller effect than factual ones: g = 0.28 against 0.58 (p = .073, marginal). | Same | Same | Moderate | Read |
| Higher prior knowledge tended to give a smaller effect. The adult experts in the data sat at the low-benefit end. | Same | Same | Weak (β = -0.49, p = .094) | Read |
| Guessing helps only when the correct answer follows soon after. Surprise at the answer rises with confidence in the guess. | [Brod 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8642250/) | Narrative review; children and university students | Weak to moderate for mechanism | Read; no effect sizes in source |
| Spaced scenario questions with immediate feedback changed clinicians' real behaviour. 95 clinicians received zero to two emails a week for 36 weeks. Inappropriate screening was **7.8% against 13.1%** over the 72 weeks after the programme ended (p = 0.011). | [Kerfoot et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2994103) | Controlled study; practising clinicians. The lead author holds equity in the company that sells the method. | Strong for one simple rule. Moderate as an analogy for engineers. | Read |
| A similar programme with Australian general practitioners found "no evidence" of an effect. | [JMIR 2014](https://www.jmir.org/2014/2/e63) | Controlled study; practising doctors | Moderate, as a counter-example | Abstract only |
| Scored predictions with training improved forecasting accuracy: "about a 10% advantage" for the training condition. | [Tetlock et al. 2014](https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2014---forecasting-tournaments-tools-for-increasing-transparency-and-improving-debate.pdf) | Controlled experiments within a tournament; adult volunteers | Moderate to strong for discrete events that resolve clearly | Read |
| 20 professional developers maintaining a real system made changes with 54% higher functional correctness when they had UML documentation (p = 0.03). | [Dzidek et al. 2008, via summary](https://neverworkintheory.org/2011/08/17/three-empirical-evaluations-of-uml.html) | Controlled study; professionals | Moderate: one study, human-made diagrams | Abstract only |
| Building a concept map helped more than studying one: g = 0.72 against 0.43. | [Schroeder et al. 2018](https://summit.sfu.ca/item/17789) | Meta-analysis; students | Moderate | Abstract only |
| Feedback improves performance on average (d = 0.41) and lowers it in over a third of cases. It works worse as attention moves toward the self and away from the task. | [Kluger and DeNisi 1996](https://scholars.huji.ac.il/node/1802) | Meta-analysis; mixed settings including workplaces | Moderate to strong | Abstract only |
| Clinicians override most frequent alerts: average override rates from 46.2% to 96.2% across 23 articles. | [JMIR Medical Informatics 2020](https://medinform.jmir.org/2020/7/e15653/) | Systematic review; practising clinicians | Strong in that field. It concerns alerts, not learning prompts. | Abstract only |
| Repeated identical security warnings were tuned out within a session. Warnings that changed appearance resisted this over five days. | [Vance et al., MIS Quarterly 2018](https://misq.org/tuning-out-security-warnings-a-longitudinal-examination-of-habituation-through-fmri-eye-tracking-and-field-experiments.html) | Controlled lab and field studies | Moderate | Abstract only |
| After an interruption, only about 10% of programming sessions resumed coding in under a minute. | [Parnin and Rugaber 2011](https://sites.cc.gatech.edu/reverse/repository/resumptionstrategies.pdf) | Observational data; professional programmers | Moderate | Abstract only |
| Students with unrestricted GPT-4 did better in practice and 17% worse on a later unaided exam. A version that gave hints and no answers largely removed the harm. Students misjudged their own learning. | [Bastani et al. 2025](https://papers.ssrn.com/abstract=4895486) | Controlled field study; nearly 1,000 high-school students | Moderate, for students | Abstract only |

### Building and keeping a mental model of a system

Professional developers keep most system knowledge in their heads and pass it on in conversation, not in documents ([LaToza, Venolia, DeLine 2006](https://www.st.cs.uni-saarland.de/edu/empirical-se/2006/PDFs/latoza06.pdf); survey and interviews at Microsoft; moderate, descriptive; abstract only). The questions they find hardest are about design rationale and about what code can reach. In one survey, 82% of developers rated at least one of 12 reachability questions as at least somewhat hard ([LaToza and Myers 2010](https://memphis-cs.github.io/comp-7085-8085-2012-fall/papers/LaToza2010ICSE.pdf); survey plus observation; moderate; abstract only). Familiarity with code fades with time, and the number of edits a developer made correlates with familiarity ([Krüger et al. 2018](https://jacobkrueger.github.io/assets/papers/Krueger2018Remember.pdf); survey of 60 open-source developers, self-rated; weak to moderate; abstract only).

Two inferences follow. First, the questions a system-level prediction asks are the ones professionals already find hardest, so the target is well chosen. Second, agent-written changes remove the editing that correlates with familiarity. That is a plausible mechanism for loss of understanding. No study has measured it. The classic models of program comprehension come from small think-aloud studies and have never been tested as a training target.

### Prediction before the outcome

The benefit of a guess attaches to what was guessed and requires a committed answer. A prompt that asks "what will this change touch?" should improve retention of what that change touched. On this evidence it will not improve understanding of parts of the system the prediction did not mention. System-level predictions are conceptual, so the expected effect is below the headline figure. For experienced engineers the memory benefit of predicting what they already know will be small. The value has to come from the misses.

This supports collecting a confidence rating with each prediction. Errors made with high confidence are more likely to be corrected after feedback. One study found that such errors were more likely to return on a delayed test, so durability is not settled ([Butler, Fazio and Marsh 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3079415); controlled study; students; moderate short-term, weak long-term; abstract only). That argues for asking again later about a miss.

The step after the prediction has its own support. Prompted self-explanation has a pooled effect of g = 0.55 ([Bisra et al. 2018](https://summit.sfu.ca/item/34322); meta-analysis; mostly undergraduates; moderate; abstract only). Comparing cases has d = 0.50, with larger effects when a principle is given after the comparison ([Alfieri et al. 2013](https://www.lrdc.pitt.edu/Schunn/papers/ContrastingCasesMeta-AlfieriEtAl2013.pdf); meta-analysis; mostly students; moderate; abstract only). The inference is that explaining the gap between prediction and outcome is where learning is most likely, and that the tool's own explanation should come after the developer has compared the two.

The closest study in software is with novices. A technique that made learners explain each step before the corresponding line of AI code was revealed "significantly improves alignment between perceived and actual coding ability". Its learning gain over baseline did not reach significance in the first study (b = 26.8, p = .058) ([Kazemitabaar et al. 2025](https://austinhenley.com/pubs/Kazemitabaar2025IUI_AIFriction.pdf); controlled study; novices, line level, chat tool; sells AI: no; weak for this product; read).

### Diagrams

For professionals, the content of a diagram matters more than its notation. Interviews with 50 engineers found most do not use UML, and those who do use it informally ([Petre 2013](https://2013.icse-conferences.org/content/uml-practice.html); survey by interview; moderate, descriptive; abstract only). In a family of experiments, class diagrams and text comments gave similar comprehension benefits, which suggests the information mattered and not the graphical form ([Gravino et al.](https://www.academia.edu/22417252/Documenting_Design_Pattern_Instances_a_Family_of_Experiments_on_Source_Code_Comprehensibility); controlled studies; students and professionals; moderate; abstract only).

Node-link diagrams lose readability as they grow. In one experiment, matrix views did better than node-link views on most tasks for graphs above about twenty nodes. Path finding was the exception and stayed better in node-link form ([Ghoniem et al. 2004](https://www.lisn.upsaclay.fr/publications/a-comparison-of-the-readability-of-graphs-using-node-link-and-matrix-based-representations/); controlled study; moderate; abstract only; later studies partly disagree on where the crossover lies). A change diagram should therefore show the touched neighbourhood and not the whole system.

The owner's constraint says diagrams are drawn for the developer. The evidence is compatible with that, with one addition. Learner drawing does not reliably beat a good provided illustration ([Fiorella and Zhang 2018](https://ifp.nyu.edu/2018/journal-article-abstracts/s10648-018-9444-8/); systematic review; students; moderate; abstract only). Building a representation does beat studying one in the concept-map data. The combination that fits both is a drawn diagram on which the developer makes a cheap mark, then a drawn diagram of the result. This combination is an inference across separate bodies of research. Nobody has tested it. No study was found on diagrams of changes, on automatically generated diagrams, on the C4 notation, or on the harm done by an inaccurate diagram.

### Building skill over months in experienced engineers

The Kerfoot programme is the closest working model: short scenario questions with an immediate explanation, at most two a week, repeated with changed context, over months, sent to busy mid-career professionals. It changed practice and not only test scores. The analogy has limits. The clinical target was a simple rule with a known right answer. A system-level prediction has a less exact right answer, and the content changes with every change. A similar programme with general practitioners found no effect.

Transfer evidence is discouraging. The general effect of pre-questions is g = 0.04. Problem solving before instruction reversed for domain-general skills in a meta-analysis ([Sinha and Kapur 2021](https://www.x-mol.com/paper/1406031499744456704); students; abstract only). Self-reported hours of deliberate practice explained less than 1% of performance differences in professions in one meta-analysis ([Macnamara et al. 2014](https://pubmed.ncbi.nlm.nih.gov/24986855/); abstract only), a figure that rests on few studies and is disputed ([Ericsson and Harwell 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6824411)). The plain reading: months of predictions will most plausibly build knowledge of this system. The claim that they build a general, portable skill has no direct support.

Calibration has the best evidence for improvement in adults over years, from forecasting tournaments. The conditions were questions that resolve without dispute, a proper score, quick and frequent feedback, and short training. Skilled intuition needs a regular environment with prompt, accurate feedback ([Kahneman and Klein 2009](https://pubmed.ncbi.nlm.nih.gov/19739881/); opinion in the form of an expert review; moderate; abstract and secondary accounts only). "Which parts did this change touch" meets that test. "Who is affected" and "what must stay true" get true feedback only when something breaks, often weeks later. Feedback on those will be a proxy, and training on a proxy risks confident wrong intuition.

Guidance that helps novices hinders people who know more. A 2025 meta-analysis confirms the effect; its pooled size is unverified ([Tetzlaff et al. 2025, via summary](https://www.learningandthebrain.com/blog/one-size-doesnt-fit-all-teaching-experts-and-novices/); meta-analysis; "experts" are mostly better-prepared students; unverified). Practising clinicians "have an aversion towards taking tests", which causes dropout ([Feldman et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6104310); controlled study and review; abstract only). The inference is that feedback for experienced engineers should be short and expandable, and that the prompt must not feel like a quiz. No study of what experienced professionals find patronising was found.

### How often to ask

No evidence gives a safe frequency. The one reference point from a successful programme with professionals is zero to two short items a week, and its authors still raised fatigue as a concern. Asking on every agent change would be far more frequent than anything shown to work, and it matches the conditions under which clinicians override most alerts. Varying the form of a prompt slowed tuning-out in the security-warning studies. A prompt placed before an agent run sits at a task boundary the developer chose, which is the least costly place to interrupt. That placement is supported by inference only. Any number the product picks is a design guess to be tested.

### Unknown

Whether predict-then-see works at all for system-level judgment in experienced engineers. Whether effects accumulate over months: almost all prediction, generation and drawing studies are single sessions. Whether gains carry beyond the specific system and the specific things predicted. Whether a delay of minutes between prediction and feedback matters. Whether calibration trained on change-impact predictions carries to other engineering judgments.

## D. Existing tools draw, explain or quiz after the change

### What was found

All product facts were checked on 16 November 2026. "Read" means the page was opened. "Unverified" means only a search summary was seen. All vendors named here sell AI tools unless marked otherwise.

| Group | Example | When | Who states the expectation | Level | Record of the developer | Status |
|---|---|---|---|---|---|---|
| Vendor learning modes | Claude Code Explanatory and Learning styles | During and after each piece | Nobody. Learning leaves "a few lines" marked `TODO(human)` for the developer to write. | Code lines | None. The docs say "nothing enforces it". | [Docs](https://code.claude.com/docs/en/output-styles); official documentation; read |
| Plan modes | Claude Code, Cursor, Copilot | Before | The agent. The developer approves or edits. | Plan text, sometimes with Mermaid | None | [Claude Code docs](https://code.claude.com/docs/en/permission-modes), read; [Cursor](https://cursor.com/changelog/2-2) and [Copilot](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-plan-mode), unverified |
| Plan and diff visualisers, open source | [visual-explainer](https://github.com/nicobailon/visual-explainer) (MIT, 11.1k stars, many agents) | Before (visual plan) and after (diff review, "a view of what was built afterward") | The agent's plan | System and code | None | Open-source project; sells AI: no; read |
| PR explainers | CodeRabbit walkthrough with sequence diagrams | After | Nobody | Component interactions and code | None | [Docs](https://docs.coderabbit.ai/pr-reviews/walkthroughs); unverified |
| Whole-system pictures | DeepWiki, Google Code Wiki, [Codemaps](https://docs.devin.ai/desktop/codemaps) | Independent of any change | Nobody | System | None | Codemaps docs read; others unverified |
| Quiz tools on a diff, open source | [lgtm-quiz](https://github.com/JoaoBRBR/lgtm-quiz) (MIT, 2 stars, Claude Code only) | After the change, before commit | The tool asks; answers are right or wrong | Code by default; optional "Architecture" level | Yes: per-concept confidence that halves after about 60 days | Open-source project; sells AI: no; read |
| Spec-first workflows | Kiro, spec-kit, Tessl | Before | The developer, as requirements | Requirements and design documents | None | [Böckeler, Oct 2025](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html); opinion from a hands-on trial; read |
| Research prototype | [Lead-and-Reveal](https://austinhenley.com/pubs/Kazemitabaar2025IUI_AIFriction.pdf) | Before each line is revealed | The learner | Code lines; novices | None | Controlled study; sells AI: no; read |

One more neighbour needs direct reading before anything is said about it. "Learning Opportunities" by Cat Hicks is an open-source skill for Claude Code and Codex that offers optional exercises after architectural work. Its README could not be opened, so its exercise design is unverified ([listing](https://www.everydev.ai/tools/learning-opportunities); unverified). If it already asks for predictions, the gap below is narrower.

### The gap

Sort the tools by timing and by who states the expectation. Before the change, the agent states its plan or the developer states requirements. After the change, a tool explains or the developer is tested. Among everything found, no tool or paper combines four things: a prediction written by the developer, made before the agent acts, at system level only, with a diagram of the actual change beside it and a record over time. Each part exists somewhere on its own.

This finding is "not found", not "does not exist". It rests on roughly 40 searches and page reads on one day. Conference proceedings, extension marketplaces and non-English sources were not searched systematically. Vendor roadmaps were not checked.

Two consequences follow, both inferences. Drawing a diagram of what an agent changed is no longer new: a paid reviewer does it on PRs by default and free skills do it locally across agents. And the existing tool with the widest use, visual-explainer, already shows a plan and then what was built. It could add a prediction step at low cost. A vendor could also ship a predict-first option inside a plan mode with no installation. What would be new in the proposed product is the pairing, not the parts.

### What developers accept and reject

In a survey of 1,100 developers and professionals in April 2026, 60% block agents from making unapproved system changes and 63% rarely or never let agents run without supervision ([Stack Overflow, May 2026](https://stackoverflow.blog/2026/05/27/agents-on-a-leash-agentic-ai-remains-mostly-monitored-at-work); survey; Stack Overflow sells AI data products; moderate; read). Larger 2026 survey figures from Stack Overflow and JetBrains reached the notes only through secondary coverage and are not quoted here.

The reactions to a merge-blocking quiz on Hacker News show the reception risk. Supporters said "We've got a huge LGTM problem". Critics said "Cute but I wouldn't actually use it", and that people will "just get AI to answer the quiz instead" ([Hacker News, Jul 2025](https://news.ycombinator.com/item?id=44726672); opinion from individual comments, not representative; read). A hands-on review of spec tools concluded "I'd rather review code than all these markdown files" ([Böckeler](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html); opinion; read). In the student agent experiment, people knew they understood less and still preferred the agent.

Not all added effort helps. A student thesis that slowed acceptance of AI suggestions and highlighted AI code found no significant difference on any measure ([Aalborg University](https://projekter.aau.dk/exploring-the-effect-of-friction-in-ai-programming-tools-on-cognitive-load-29d0e971.html); controlled study, not peer reviewed; 38 students; unverified). The positive results share one feature: the person produces something.

### Unknown

No study measures whether any vendor learning mode improves comprehension or skill in coding. No data shows how many developers turn those modes on. No survey asks developers whether they would accept a prediction step. No independent evaluation was found of the accuracy of generated change diagrams in any tool. Demand for the proposed product is inferred, not measured.

## E. Agents expose each edit before it lands, and a module-level check needs no model

### What agents expose before a change

These facts come from vendor documentation read on 16 November 2026. Type: official documentation. Sells AI: yes for every vendor except Aider. Strength: strong for what the documents state. None of them promises that payload formats will stay stable.

| Agent | Event at prompt submission | Event before each edit, with arguments, can deny | Agent's full plan readable before any edit | Source |
|---|---|---|---|---|
| Claude Code | `UserPromptSubmit`: receives the prompt, can block, can add context | `PreToolUse`: `Edit` carries `file_path`, `old_string`, `new_string` | **Yes.** The `ExitPlanMode` payload carries `plan` and `planFilePath`. | [Hooks reference](https://code.claude.com/docs/en/hooks) |
| Codex CLI | `UserPromptSubmit`: can block and add context | `PreToolUse` covers `apply_patch`. The docs say: "a useful guardrail, not a complete enforcement boundary." | Unverified: secondary sources only | [Codex hooks](https://learn.chatgpt.com/docs/hooks) |
| Cursor | `beforeSubmitPrompt`: can stop submission | `preToolUse` can deny. The input for `Write` is not described. `afterFileEdit` gives the edits after the fact. | Plans are saved as files. No "plan ready" event was found. | [Cursor hooks](https://cursor.com/docs/agent/hooks) |
| GitHub Copilot | `userPromptSubmitted`: receives the prompt, cannot block | `preToolUse` can allow, deny or modify. "Command hook timeouts are always fail-open". | Plan mode exists in the CLI. No readable plan was found for the cloud agent. | [Hooks reference](https://docs.github.com/en/copilot/reference/hooks-configuration) |
| Devin CLI and Devin Local (formerly Windsurf) | `UserPromptSubmit` | `PreToolUse`. Reads Claude Code hook files by default. | Not found | [Devin CLI hooks](https://docs.devin.ai/cli/extensibility/hooks/overview) |
| Gemini CLI | `BeforeAgent` | `BeforeTool` | Not documented. The page says Gemini CLI was replaced by Antigravity CLI on 18 June 2026. Antigravity was not researched. | [Gemini CLI hooks](https://geminicli.com/docs/hooks/reference/) |
| Cline | `beforeRun` | `beforeTool` can skip a call. Hook errors are ignored by default. | Not found | [Cline SDK plugins](https://docs.cline.bot/sdk/plugins.md) |
| Aider | No hook mechanism found | None found | Architect mode proposes changes; no interception documented | [Aider modes](https://aider.chat/docs/usage/modes.html) |

Three moments exist to ask for a prediction before any edit. At prompt submission the tool knows the request but not the agent's intent, and this works in almost every agent. At plan approval the full intended change exists as text, but this is documented only for Claude Code. At the first write call the tool can hold the call, but knows only the first edit. A working precedent exists for the second: the Plannotator tool holds `ExitPlanMode` open, opens a browser page, and returns the person's decision ([Plannotator docs](https://docs.plannotator.ai/open-source/agents/claude-code); official documentation of a third-party tool; read).

After the change, everything needed for a mechanical check is available without the agent's cooperation. A stop event fires and `git diff` gives the actual change. Session transcripts are readable, but both Claude Code and Codex warn that the format is not a stable interface.

Rich display inside the conversation is not confirmed for terminal agents. MCP Apps let a server return an interactive page inside the chat, but the hosts listed do not include Claude Code, Cursor, Codex or Gemini CLI ([MCP Apps overview](https://modelcontextprotocol.io/extensions/apps/overview); official documentation; read). A browser page opened by a hook is the confirmed route.

### What can be computed to draw a system-level picture of a change

| Capability | Tool or study | Finding | Type; sells AI; strength; status |
|---|---|---|---|
| Module dependency graph from imports | [dependency-cruiser](https://github.com/sverweij/dependency-cruiser); [import-linter](https://import-linter.readthedocs.io/en/stable/) | Deterministic, from source alone. JavaScript family and Python respectively. dependency-cruiser outputs dot and mermaid. | Official documentation; no; strong for what they state; read |
| Function-level call graph, Python | [PyCG, ICSE 2021](https://arxiv.org/abs/2103.00587) | Precision about 99.2%, recall about **69.9%**, 0.38 seconds per 1k lines on average | Controlled evaluation; no; moderate; abstract only |
| API contract change | [buf breaking](https://buf.build/docs/breaking/); [oasdiff](https://github.com/oasdiff/oasdiff) | Mechanical verdict on protobuf and OpenAPI files against a git ref | Official documentation; no; strong where a schema file exists; read |
| Destructive database migration | [Atlas lint](https://atlasgo.io/lint/analyzers) | Flags drops, data-dependent changes and backward-incompatible changes. Several analyzers are paid. No reversibility analyzer on the page. | Official documentation; AI features unknown; moderate; read |
| Which other parts are affected | [Musco et al. 2017](https://arxiv.org/abs/1812.06286) | On 17,000 mutants in 10 Java projects, richer call graphs raised completeness, and "the most basic call graph gives the best trade-off between precision and recall". | Controlled evaluation; no; moderate; abstract only, no numbers seen |
| Architecture recovered by a model alone | [Liljas et al., ESEM 2026](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESEM.2026.62) | Best agent reached mean F1 of **0.604** on 17 Java microservice systems. Precision exceeded recall: models left relationships out more than they invented them. | Controlled evaluation; no; moderate; abstract only |
| Architecture views drawn by a model | [Sathvika et al., arXiv 2603.21178](https://arxiv.org/html/2603.21178v1) | Across 340 repositories and 4,137 views, completeness failures exceeded 82% for most zero-shot models. Models worked "at the code level rather than architectural abstractions". The models tested are older than those current in November 2026. | Controlled evaluation (preprint); no; moderate; read |

The reliable base layer is a module graph built from imports at the base commit and again at the end of the run. The system-level difference is the set difference of nodes and edges, plus cycle detection on each. Its error is exactly the error of the import graph: dynamic imports, dependency injection and reflection are missed, and no measured miss rate was found. The set of modules that depend on what changed can be computed, but it overstates actual impact. It should be shown as "could be affected", not "is affected".

A language model alone is not reliable for drawing the system. The measured failures are omission and the wrong level of detail. Studies that ground the model in computed dependency facts report improvement, though those reached the notes only through search summaries and are unverified. The inference is a division of work: nodes and edges come only from computed facts, and a model is allowed to group, name and describe them. Any edge a model mentions that is not in the computed graph is dropped.

Drawing limits are known. Mermaid's default configuration stops at 500 edges ([Mermaid config](https://mermaid.js.org/config/schema-docs/config.html); official documentation; read). A change-focused diagram of changed modules and their direct neighbours stays small.

### Checking a prediction

A prediction made as a closed choice over computed objects can be scored without a model. The table is the note-writer's synthesis. Error notes are reasoned, not measured, unless a source is named above.

| Prediction | Fact that scores it | Main error source |
|---|---|---|
| Which files or modules will change | `git diff --name-only`, mapped to modules | None for files. Module mapping depends on the grouping chosen. |
| Whether a new dependency between modules, or a cycle, appears | Import-graph difference | Dynamic imports, dependency injection, reflection |
| Whether a third-party dependency is added | Manifest and lockfile difference | Close to exact |
| Whether a public interface changes and breaks clients | oasdiff or buf on schema files | Works only if a schema file exists and matches the code |
| Whether the database schema changes destructively | Migration diff plus lint | Data-dependent cases; reversibility not analysed |
| Which other modules could be affected | Reverse-dependency closure | Overstates; also misses where edges are missed |
| Which tests will fail | Run tests on old and new code | Needs a runnable environment |
| "This is a contained change" | No single fact | Needs a model, or a rewording as a closed choice |

This has a direct design consequence. If the developer marks expected modules and edges on the computed "before" diagram, scoring is set comparison. Free text needs a model to map it onto facts, and no study measures the error rate of that mapping.

### What is not possible today, on this evidence

A third-party tool cannot read the agent's complete intended change before any edit, in a documented way, outside Claude Code plan mode. It cannot force a prediction in cloud or headless runs where nobody is present. Claude Code's `--bare` flag skips hooks, and the docs say it "will become the default for `-p` in a future release" ([Claude Code headless](https://code.claude.com/docs/en/headless); official documentation; read). It cannot enforce anything reliably: Copilot fails open on timeouts and Cline ignores hook errors by default, so a hook is a prompt and not a control. It cannot get a complete, precise call graph for Python or JavaScript without running the code. The main build-free library for precise name resolution, stack-graphs, was archived in September 2025 ([github/stack-graphs](https://github.com/github/stack-graphs); read).

### Unknown

Mechanical checks for the operational level, the level of the documented incidents, were not researched. `terraform plan -json` as a source of infrastructure facts is background knowledge only and unverified. No timing was found for building an import graph of a mid-sized repository. How each agent behaves while a hook waits minutes for a person is unknown beyond the one Claude Code example. Whether the developer has already seen the plan text when the plan hook fires is not established in the notes. It matters, because a prediction made after reading the agent's plan is not the developer's own.

## Conclusion: what to build, what not to claim, what to measure, and the risks

### Design implications the evidence supports

| Implication | Basis | Strength |
|---|---|---|
| Work at the level of system effect, scope and operational effect, not lines. | Documented incidents; field reports of agents doing more than asked; diffs do not show system effect | Moderate that the harm sits there. No measurement of comprehension at this level. |
| Require a committed prediction. Reading a question is not enough. | g = 0.65 with a generated answer against 0.22 without (read) | Moderate; students, recall |
| Collect the prediction as marks on a drawn diagram of computed modules. | It makes scoring mechanical; it keeps the effort low; building a representation beats studying one in student data | Moderate for scoring. Weak for learning: the combination is untested. |
| Show the result soon after, as task-level feedback: the predicted picture beside the actual one. No scores about the person, no streaks, no rankings. | Brod 2021 on feedback timing; Kluger and DeNisi on self-focused feedback | Moderate |
| Ask for a confidence rating, and ask again later when a new change touches an area that was missed. | Confident errors are corrected more often but can return after a delay; Kerfoot's repeated cycles with changed context | Weak to moderate; other populations |
| Ask rarely, and choose the cases: unfamiliar area, change across module boundaries, past miss. Vary the form. | The only working reference with professionals is zero to two items a week; alert override rates; smaller benefit when the person already knows the answer | Moderate that asking on every change will fail. No evidence for any specific rate. |
| Make it optional and non-blocking. | Reactions to merge-blocking quizzes and spec documents; fail-open hooks make enforcement unreliable anyway | Moderate, from opinion and documentation |
| Draw from computed facts only. Let a model name and group, never add edges. State what the graph cannot see. | Measured model failures in architecture recovery; 69.9% recall for Python call graphs (abstract only) | Moderate |
| Keep the diagram to the changed modules and their direct neighbours, in informal box-and-arrow form. | Node-link readability falls with size; professionals use informal sketches | Moderate |
| Keep feedback short and expandable for experienced users. | Expertise reversal; clinicians' aversion to tests | Weak to moderate; effect size unverified |
| Support several agents through hooks, with prompt submission as the common moment and the plan event where it exists. | Hook documentation for seven agents; open-source skills in this area already support many hosts | Strong for feasibility |

The ambitious version of this product is supported by the evidence in one specific sense. Every section of this report ends on the same missing measurement: what developers understand about the system-level effect of agent changes, over time, in real work. A tool that records a prediction, a computed outcome and a later result for the same person is the instrument that measurement needs. An open-source tool can publish its method and, with consent, its data. No vendor study and no academic study found has done this. The second ambitious direction is the operational level: state, credentials and what cannot be undone. That is where the documented damage occurred. It has the least research behind it in these notes, on both the learning side and the technical side.

### Design implications the evidence does not support

The evidence does not support a claim that the product builds a general, portable engineering skill. The transfer findings point the other way. The supported claim is narrower: it builds and keeps knowledge of this system, in the areas the developer predicted.

It does not support asking on every change. It does not support any quiz that blocks a commit or merge. It does not support a diagram drawn by a model alone. It does not support scoring free-text predictions, or predictions about who is affected and what must stay true, as if they resolved cleanly. It does not support whole-system maps as the main view. It does not support passive measures such as slowing acceptance or highlighting AI code. It does not support any claim that the product "works", that it reduces incidents, or that it prevents skill loss. Skill loss in working engineers has not itself been measured.

It also does not settle the owner's first constraint. Excluding code-level work is consistent with where the harm is. It takes a side in an open dispute about whether higher-level skill can be held without code-level fluency.

### Open questions the product itself would have to measure

Does prediction accuracy on a given system rise over months, and does it rise for areas the developer has not predicted before? Does accuracy on one system carry to another? Does calibration improve, measured as the match between stated confidence and scored accuracy? Do developers who predict understand the result better than those who only see the diagram? Does the explanation step add anything over seeing the two pictures? What asking rate keeps people using it after three and six months, and does varying the form help? Do experienced engineers and juniors differ? Does the computed diagram agree with what expert reviewers judge to be the real effect of a change, and how often does a missed edge mislead? Does any of this relate to later outcomes: rework, review time, defects, incidents? Does a delay of minutes between prediction and result weaken the effect? Do people hand the prediction to an AI? Each of these is answerable only with the product's own data, and none is answered in the literature found.

### Risks

**The method does not work for this population.** There is no direct evidence. The nearest study is with novices at line level, and its learning gain was not significant in the first study.

**Low voluntary use.** Students knew they understood less with an agent and still preferred it. Any effortful step competes with speed. Usage of existing vendor learning modes is unknown.

**Training on a wrong picture.** The feedback is only as good as the computed outcome. Import graphs miss dynamic links at an unmeasured rate. A developer whose correct prediction is marked wrong, or the reverse, learns the wrong thing. No study quantifies the harm of an inaccurate diagram.

**Training on a proxy.** Structural reach is not real consequence. Confidence built on structural feedback could be misplaced on questions of behaviour and downstream effect.

**Tuning out.** Repeated prompts are ignored in other fields within days to weeks. Nothing is known about learning prompts in developer tools over months.

**Attention on the self.** Any element that reads as a judgment of the engineer falls where feedback more often harms. The record of skill over time must be handled with this in mind.

**Dependence on vendor interfaces.** Hook payloads carry no stability promise. Headless Claude Code runs are set to skip hooks by default. Products were renamed or replaced twice in 2026 in the documentation read. Cloud and unattended runs have nobody to ask.

**Limited reach of the prediction moment.** The full intended change is readable before edits only in Claude Code. Elsewhere the prediction is made against the request alone.

**Absorption by existing tools.** A widely used open-source visualiser or a vendor plan mode could add a prediction step. For a free open-source product this is a risk to adoption, not to the aim. If the idea spreads, the aim is served.

**Gaming.** Critics of quiz tools expect people to have an AI answer for them. An optional tool reduces the motive and does not remove it.

**The evidence base is dated and partial.** METR calls its own 2025 result out of date. The two quantitative studies of model-drawn architecture used older models. Much of the telemetry comes from vendors who sell review or analytics products. The absence of a matching tool rests on one day of keyword search.

The plain summary of what is unknown: whether this kind of practice works, whether it lasts, whether it transfers, how often to ask, and whether understanding more leads to measurably better outcomes. The problem is measured in two small experiments and several incidents. The remedy is not measured at all.
