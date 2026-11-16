# Higher-level engineering skills that matter when coding agents write the code

Notes compiled 16 November 2026.

How to read the tags on each finding:

- **Type**: controlled study / observational data / survey / interview study / opinion.
- **Vendor**: "yes" means the publisher sells AI coding tools (or, for review-tool vendors, AI review tools).
- **P** = how well the source shows the problem is real. **S** = how well it shows the skill reduces the problem. Scale: strong / moderate / weak / none.
- **Verified** = I read the figure in the primary source in this session (through a page fetch or the PDF text). **Unverified** = the figure came from a search summary or secondary coverage only; check before quoting.

One overall caution for the report writer: almost every source shows that a problem exists. Almost none shows that a named skill, once trained, reduces it. The S column is weak or empty nearly everywhere.

## 1. Which candidate skills does the evidence support, and how do they rank?

### Takeaway
Three skills have the best support: holding a model of the system, stating intent and acceptance before work starts, and judging results against evidence (including knowing how far to trust your own sense of progress). Evidence that training any of them improves outcomes with agents is weak for all, and for rollout and production operation it is close to absent at the level of the individual developer.

### Cited Findings

**System model (architecture, data flow, where state lives)**
- Great engineers were described as building "an accurate mental model of dependencies and connections", which informants saw as "critical". The paper lists "Handles complexity", "Sees the forest and the trees", "Updates their mental models" and "Knowledgeable about their technical domain" among 53 attributes from 59 interviews at Microsoft. [Type: interview study; Vendor: no for the 2015 paper's subject, though authors include Microsoft staff; P: moderate; S: none; Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- Code and change understanding is "the key aspect of code reviewing", and most understanding needs are not met by tools. [Type: interview study plus survey plus comment classification at Microsoft; Vendor: no (pre-AI); P: moderate; S: none; Unverified, taken from the abstract as returned by search] — [Bacchelli and Bird 2013](https://2013.icse-conferences.org/content/expectations-outcomes-and-challenges-modern-code-review.html)
- Experienced developers "cited their existing domain expertise as critical for effective agent use (11x Observations, 65x Survey)"; six observed participants "stressed the necessity of human codebase understanding for production reviews". Integrating with existing or legacy code was rated unsuitable for agents 17 to 3. [Type: interview/observation study (N=13) plus qualitative survey (N=99); Vendor: no; P: moderate; S: weak, self-report; Verified] — [Huang et al. 2025, arXiv 2512.14012](https://www.arxiv.org/abs/2512.14012)
- In a randomised trial with 52 mostly junior engineers learning a new library, the AI-assisted group scored 50% on a comprehension quiz against 67% for hand-coders (Cohen's d = 0.738, p = 0.01). The largest gap was on debugging questions. [Type: controlled study; Vendor: yes (Anthropic); P: strong for short-term comprehension of new material, weak for system-level models in real codebases; S: weak; Verified] — [Anthropic, AI assistance and coding skills, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)
- "Cognitive debt" is defined as "the erosion of shared understanding across a team", alongside "intent debt", the loss of explicit goals and constraints. No measurement is offered. [Type: opinion (position paper); Vendor: no; P: weak; S: none; Verified from abstract] — [Storey 2026, arXiv 2603.22106](https://arxiv.org/abs/2603.22106)

**Specifying intent and acceptance (what done means)**
- Agents were rated suitable for "following well-defined plans" 28 to 2; respondents reported agents "performed poorly with vague/unclear/open-ended tasks". One respondent: "if you don't lead [or] plan then you will [get] stuck". [Type: qualitative survey; Vendor: no; P: moderate; S: weak, self-report; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- Across 20,574 real coding-agent sessions from 1,639 repositories, seven recurring forms of misalignment were found, covering how agents read projects, interpret developer intent, follow rules and bound their actions. 91.49% of visible resolutions still required explicit user correction. [Type: observational data; Vendor: not established, the author list includes one industry affiliation I did not check; P: strong that intent misreading is common; S: none; Verified from abstract only] — [Tang et al. 2026, arXiv 2605.29442](https://arxiv.org/abs/2605.29442)
- Anthropic engineers said they delegate where checking is cheap: "It's absolutely amazing for everything where validation effort isn't large in comparison to creation effort." [Type: survey (132) plus interviews (53); Vendor: yes; P: weak; S: weak; Verified] — [Anthropic, How AI is transforming work at Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)
- An interview study of spec-driven development reports more reliable agent behaviour with specs, at higher planning and review cost, and that participants could not separate the spec's effect from other factors. [Type: interview study; Vendor: unknown; P: weak; S: weak; Unverified, search summary only] — [arXiv 2608.25202](https://arxiv.org/pdf/2608.25202)

**Evaluating outcomes rather than output**
- "One-shotting code without modification/verification" was rated unsuitable 23 to 5. Survey respondents reported modifying agent code "about half the time on average". [Type: qualitative survey; Vendor: no; P: moderate; S: weak; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- Overall misalignment rates fell over time, but constraint violations and inaccurate self-reporting by agents grew as a share of cases. [Type: observational data; Vendor: see above; P: moderate; S: none; Verified from abstract] — [Tang et al. 2026](https://arxiv.org/abs/2605.29442)
- Merged pull requests rose about 24% for adopters of command-line agents at Microsoft; the authors treat merged PRs as a proxy for output, not business value. [Type: observational data; Vendor: yes (Microsoft); P: weak, shows only that output rose; S: none; Unverified, abstract and secondary summaries] — [Murphy-Hill, Butler, Savelieva 2026, arXiv 2607.01418](https://arxiv.org/abs/2607.01418)

**Calibration of one's own confidence**
- Sixteen experienced open-source developers forecast a 24% speed-up from AI, were measured as 19% slower across 246 tasks, and afterwards still believed they had been 20% faster. [Type: controlled study; Vendor: no; P: strong for this group and early-2025 tools; S: none; Verified] — [METR, July 2025](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- METR's follow-up says the 2025 result is out of date and that self-reported speed-ups "may be very high but are unreliable". [Type: controlled study with acknowledged selection problems; Vendor: no; P: moderate; S: none; Verified] — [METR, Feb 2026](https://metr.org/blog/2026-02-24-uplift-update/)
- Knowledge workers with higher confidence in the AI reported less critical thinking; those with higher confidence in themselves reported more. Survey of 319 workers. [Type: survey; Vendor: yes (Microsoft Research); P: moderate; S: weak; Unverified, from summaries] — [Lee et al., CHI 2025](https://advait.org/files/lee_2025_ai_critical_thinking_survey.pdf)

**Decomposing and sequencing work**
- All 13 observed developers controlled implementation at some level; 11 controlled design by writing or revising plans; one prompt restricted the agent to "do just step 1". "Big tasks (not necessarily complex)" were rated unsuitable 7 to 1. [Type: observation study; Vendor: no; P: moderate; S: weak; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- Li et al. list "Evolving—structure the software to be efficiently delivered iteratively or in pieces" as an attribute of great engineers. [Type: interview study; Vendor: no; P: weak; S: none; Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- DORA 2025 is reported to find small batches especially valuable with AI. [Type: survey; Vendor: yes (Google); P: moderate; S: weak, organisation-level correlation; Unverified, secondary write-up] — [DORA 2025 report](https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf)

**Deciding what to delegate**
- More than half of surveyed Anthropic engineers said they can "fully delegate" only 0 to 20% of their work. They keep high-level design and anything needing organisational context or "taste". [Type: survey; Vendor: yes; P: moderate; S: weak; Verified] — [Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)
- Experienced developers disagree on using agents for high-level plans (13 suitable, 23 unsuitable); 12 respondents said agents cannot replace human expertise or decision making, none said they can. [Type: qualitative survey; Vendor: no; P: moderate; S: none; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)

**Judging the reach of a change; stating and protecting invariants and contracts**
- "Fitted" designs take other components into account: "if I tweaked this here I'm not going to break something else." [Type: interview study; Vendor: no; P: weak; S: none; Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- Agents "often wrote custom code for pre-existing functions in core libraries" (survey respondent S80); one respondent said agents' "architectural decisions [...] can come to bite back". [Type: qualitative survey; Vendor: no; P: weak to moderate; S: none; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- Constraint violations are a growing share of developer-agent misalignment. [Type: observational data; P: moderate; S: none; Verified from abstract] — [Tang et al. 2026](https://arxiv.org/abs/2605.29442)

**Risk, reversibility and rollout; operating in production**
- 90.50% of misalignment episodes cost effort and trust "rather than irreversible system damage", which implies a minority of under 10% did not fit that description. [Type: observational data; P: moderate; S: none; Verified from abstract] — [Tang et al. 2026](https://arxiv.org/abs/2605.29442)
- DORA 2025 (nearly 5,000 respondents) is reported to find delivery instability still rising with AI adoption while throughput rises, and no evidence that speed offsets instability through fast repair. [Type: survey; Vendor: yes (Google); P: moderate at organisation level; S: none for individual skill; Unverified, read via InfoQ] — [InfoQ on DORA 2025](https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025)
- "Handling CI/deployment infrastructure" rated unsuitable for agents 8 to 3. [Type: qualitative survey; Vendor: no; P: weak; S: none; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- Review-tool vendors report more issues per AI-co-authored pull request (10.83 against 6.45 in 470 open-source PRs) and rising incidents and review times. [Type: observational data; Vendor: yes (CodeRabbit and Faros sell AI review or analytics products); P: weak to moderate, small or uncontrolled samples; S: none; Unverified] — [CodeRabbit report](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report), [Faros AI](https://www.faros.ai/blog/ai-code-quality-senior-engineer-review-burden)

**Product and domain judgment**
- "Business logic or tasks requiring domain knowledge" rated unsuitable for agents 15 to 2. [Type: qualitative survey; Vendor: no; P: moderate; S: none; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- "Knowledgeable about customers and business" and "Makes tradeoffs" are listed attributes: "Really understanding the point like who is the customer, why are we doing this." [Type: interview study; Vendor: no; P: weak; S: none; Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- DORA 2025 is reported to find that organisations with a user-centric focus see amplified benefits from AI and those without often see negative effects on team performance. [Type: survey; Vendor: yes (Google); P: moderate; S: weak to moderate, the only moderator finding located, at organisation level; Unverified, via InfoQ] — [InfoQ on DORA 2025](https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025)

### Inferences

Proposed ranking. The order weighs problem evidence first, then whether anything suggests the skill is trainable. It is my judgment, not a result from any single source.

| Rank | Skill | Definition (no reference to agents) | What goes wrong without it | P | S |
|---|---|---|---|---|---|
| 1 | System model | Being able to say what the parts are, how data moves between them and where state is kept | Changes that pass checks but do not fit; nobody can safely change the system later | moderate to strong | weak |
| 2 | Specifying intent and acceptance | Saying what a change must do and what evidence would show it is done, before work starts | Work that satisfies the words of a request and misses its purpose; repeated correction | moderate to strong | weak |
| 3 | Evaluating outcomes | Judging a change by whether the intended effect occurred, not by volume or by passing checks | More merged work with no gain, or with hidden defects | moderate | weak |
| 4 | Calibration | Knowing how far your own sense of progress or correctness can be trusted, and checking when it cannot | Confident acceptance of work that is slower or worse than believed | strong in one small trial | none |
| 5 | Decomposition and sequencing | Splitting work into steps that can each be checked, in an order that limits rework | Large changes that cannot be reviewed or undone piece by piece | moderate | weak |
| 6 | Deciding what to delegate | Matching a task to whoever can do it at acceptable cost of checking | Time lost supervising unsuitable tasks, or unsupervised work on risky ones | moderate | weak |
| 7 | Reach of a change, invariants and contracts | Knowing who and what depends on the thing being changed, and which properties must stay true | Breakage in distant parts; duplicated or contradictory behaviour | weak to moderate | none |
| 8 | Product and domain judgment | Knowing who the user is and why the work is worth doing | Correct software that solves the wrong problem | moderate | weak (organisation level) |
| 9 | Risk, reversibility, rollout and production operation | Knowing what could fail, how it would show, and how to undo it | Instability and incidents | moderate (organisation level) | none |

- Candidate 7 merges two listed skills (reach of a change; invariants and contracts) because no source separates them. Candidate 9 merges rollout and production operation for the same reason.
- "Data flow and where state lives" has no evidence of its own; it rides on the system-model evidence.
- Two additions the evidence supports as candidates: making trade-offs explicitly (Li et al.), and recording rationale so shared understanding survives (Storey's "intent debt"; Li et al.'s "creates shared context"). Both are opinion or interview level.
- No candidate should be dropped on evidence of irrelevance. Rollout and production operation should be marked as resting on organisation-level surveys and practitioner opinion.
- Skills 1 to 3 are also the ones where a tool could plausibly test the learner, since each has an observable product: an explanation, a statement of done, a verdict backed by evidence.

### Gaps
- No study compares these skills against each other. The ranking cannot be validated from the literature.
- No study isolates "knowing where state lives" or "stating invariants" as a separate skill in agent-assisted work.
- I did not open the full DORA 2025 PDF or the full text of Tang et al., Lee et al., or the Microsoft rollout study.

## 2. What do studies of expert engineers show distinguishes them?

### Takeaway
The best-known study finds that what separates great engineers lies mostly in decision making and in how they model systems, people and outcomes. It is interview-based, from one company, and does not measure outcomes.

### Cited Findings
- 59 semi-structured interviews across 13 Microsoft divisions produced 53 attributes, grouped under personal characteristics, decision making, teammates and software product. [Type: interview study; Vendor: no; P: moderate; S: none; Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- Decision-making attributes include "Models states and outcomes—building mental models linking the current state, alternative actions, probabilistic outcomes, and value of outcomes", "Sees the forest and the trees", "Handles complexity" and "Updates their mental models". [Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- Software-product attributes include "Anticipates needs", "Makes tradeoffs", "Fitted", "Evolving" and "Long-termed". [Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- Informants said it was rare for anyone to have complete understanding of a large system, so great engineers had to stay open to changing their understanding. [Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- The authors state threats to validity: a small sample for a company of that size, only 3 women among 59 informants, Seattle only, and uncertain generalisation to start-ups or non-software firms. They suggest improvement "might come from trainings, projects at work, mentoring, or self-adjustments" and call for research on interventions. [Verified] — [Li, Ko, Zhu 2015](https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf)
- A 2020 follow-up survey (Li, Ko, Begel, Empirical Software Engineering) is reported to rank the attributes and to find that being a competent coder remained among the most important. [Type: survey; Vendor: no; Unverified, secondary summary] — [Li, Ko, Begel 2020](https://link.springer.com/10.1007/s10664-019-09773-y)
- In code review, understanding the change is the central difficulty, and review yields knowledge transfer and team awareness more than defect finding. [Type: interview study plus survey; Unverified, abstract via search] — [Bacchelli and Bird 2013](https://2013.icse-conferences.org/content/expectations-outcomes-and-challenges-modern-code-review.html)

### Inferences
- The attributes that survive when typing is removed map closely onto the candidate list: mental models (1), trade-offs and outcomes (3, 8), fit with surroundings (7), delivering in pieces (5), customer knowledge (8).
- The 2020 follow-up's reported emphasis on coding competence is a counterweight: expert engineers did not regard higher-level skill as separable from the ability to code. That matters for a tool that trains only above the code level.
- Li et al. treat the attributes as learnable but offer no evidence that they are.

### Gaps
- I found no empirical study of software architects in this session; the search did not return one. This part of the question is unanswered.
- I found no senior-versus-junior behavioural study with measured outcome differences. Huang et al. studied only experienced developers, with no novice comparison group.

## 3. How does the human share of work shift with agents (2024 to 2026)?

### Takeaway
Usage data and field studies agree that people move toward planning, supervision and checking, and that experienced developers keep control of design. Most large datasets come from vendors, and they measure what people do, not whether it works.

### Cited Findings
- Anthropic internal Claude Code transcripts (200,000, February to August 2025): average human turns per transcript fell from 6.2 to 4.1; maximum consecutive tool calls rose from 9.8 to 21.2; feature implementation rose from 14.3% to 36.9% of tasks; code design or planning rose from 1.0% to 9.9%. [Type: observational data; Vendor: yes; P: moderate; S: none; Verified] — [Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)
- Same study, survey of 132 staff: self-reported use rose from 28% to 59% of daily work; 27% of assisted work would not otherwise have been done. Authors note selection, social desirability and recall bias. [Type: survey; Vendor: yes; Verified] — [Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)
- Experienced developers "plan before implementing and validate all" agent output; 50 of 99 survey respondents mentioned driving architectural requirements and design. The authors note a deliberate selection bias toward people positive about AI. [Type: observation study plus survey; Vendor: no; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- Anthropic Economic Index, March 2026: coding is moving from the chat product to the API, described as a move from augmentative use toward "more automated workflows". [Type: observational data; Vendor: yes; Verified] — [Anthropic Economic Index, March 2026](https://www.anthropic.com/research/economic-index-march-2026-report)
- Earlier Economic Index work reported about four in five Claude Code conversations as automation against about half on the chat product. [Type: observational data; Vendor: yes; Unverified, search summary] — [Anthropic, impact on software development, 2025](https://www.anthropic.com/research/impact-software-development)
- Microsoft's rollout study covers tens of thousands of engineers over about four months and reports about 24% more merged pull requests for adopters. [Type: observational data; Vendor: yes; Unverified] — [arXiv 2607.01418](https://arxiv.org/abs/2607.01418)
- Agent-authored pull requests are accepted at rates that vary more by task type than by agent (a 29 point gap between task types across 7,156 PRs). [Type: observational data; Vendor: unknown; Unverified, search summary] — [arXiv 2602.08915](https://arxiv.org/html/2602.08915v2)
- A figure circulating as DORA 2025, that higher AI adoption went with a 91% rise in review time and a 154% rise in pull request size, reached me only through a secondary blog; I believe it may originate from Faros AI, not DORA. [Type: observational data; Vendor: yes either way; Unverified and attribution uncertain] — [Exceeds AI blog](https://blog.exceeds.ai/ai-vs-human-code-contributions/)

### Inferences
- Human input per unit of agent work is falling (fewer turns, longer autonomous runs). Each human decision therefore covers more generated work, which raises the value of the decisions made before and after a run: what to ask for and whether the result is acceptable.
- Review is becoming the constraint. This is consistent across vendor data but not shown by any independent controlled study I located.

### Gaps
- I found no large usage study from OpenAI or GitHub that reports the human share of work in comparable terms. Not located is not the same as not existing; the searches did not surface one.
- No dataset reports time spent on specification versus review versus rework for agent-assisted work in a way that is comparable across companies.

## 4. Which skills weaken under heavy delegation, and is that measured?

### Takeaway
Only short-term comprehension of new material has been measured in a controlled way, in one small vendor-run trial. Claims that system understanding, design ability or judgment erode over months rest on self-report and opinion.

### Cited Findings
- Randomised trial, 52 mostly junior engineers: AI group 50% against 67% on a post-task quiz (d = 0.738, p = 0.01); time saved about two minutes, not significant (p = 0.391). [Type: controlled study; Vendor: yes; P: strong for immediate comprehension; Verified] — [Anthropic, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)
- Within the AI group, patterns differed: "AI delegation" (n=4) averaged 39%, "iterative AI debugging" (n=4) 24%, "conceptual inquiry" (n=7) 65%, "generation-then-comprehension" (n=2) 86%. The authors say this analysis "does not draw a causal link". [Type: controlled study, exploratory sub-analysis; Vendor: yes; S: weak; Verified] — [Anthropic, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)
- The authors' limits: small sample, one library, a sidebar assistant and not an agent, comprehension measured immediately; whether quiz scores predict long-term skill "this study does not resolve". They expect effects with agentic tools "are likely to be more pronounced", which is a prediction, not a finding. [Verified] — [Anthropic, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)
- Anthropic staff reported worry about atrophy: "When producing output is so easy and fast, it gets harder and harder to actually take the time to learn something." The report names a "paradox of supervision": supervising requires the skills that heavy use may erode. [Type: interview study; Vendor: yes; P: weak, self-report; Verified] — [Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)
- A study of student projects describes accepting and committing generated code without understanding why it worked. [Type: observational/qualitative; Vendor: no; Unverified, search summary] — [arXiv 2604.13277](https://arxiv.org/html/2604.13277)
- Storey's and Osmani's accounts of cognitive or comprehension debt cite the Anthropic trial and an anecdote of a student team that by week seven could not make simple changes safely. [Type: opinion; Vendor: Osmani works at Google, which sells AI tools; P: weak; Verified] — [Osmani, March 2026](https://addyosmani.com/blog/comprehension-debt/), [Storey 2026](https://arxiv.org/abs/2603.22106)
- METR's perception gap (believed 20% faster, measured 19% slower) shows miscalibration under AI use but not that calibration declines with use. [Type: controlled study; Vendor: no; Verified] — [METR 2025](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

### Inferences
- The skill most often said to weaken is the first-ranked one (system understanding), and it is also the precondition for supervising. That is the strongest argument for training it, but the argument is a chain of reasoning, not a measured effect.
- The interaction-pattern result suggests that how one works with the assistant matters more than whether one uses it. This is the nearest thing to evidence of improvability, and it rests on groups of two to seven people.

### Gaps
- No longitudinal measurement of skill change in working engineers was found. Unknown: whether experienced engineers lose system understanding, at what rate, and whether it recovers.
- No peer-reviewed replication of the Anthropic trial was found.
- No measurement exists, that I could find, of erosion in design, decomposition, risk judgment or product judgment.

## 5. What do engineering leaders and practitioners say are the durable skills, and where do they disagree?

### Takeaway
Practitioners largely agree that system understanding, clear intent, verification and judgment gain value. They disagree on whether code-level skill is still required to exercise them, and on whether planning and design can be handed over. All of this is opinion.

### Cited Findings
- Addy Osmani argues the engineer with deep system understanding becomes more valuable, and lists knowing which behaviours in a change are load-bearing, recalling design rationale, judging whether a refactor is safe, and stating intent before a change is written. [Type: opinion; Vendor: yes (Google employee); Verified] — [Osmani, March 2026](https://addyosmani.com/blog/comprehension-debt/)
- Simon Willison's "vibe engineering" post is reported to argue that the practices that make agents effective (strong tests, planning, review) are already the traits of senior engineers. [Type: opinion; Vendor: no; Unverified, search summary] — [Willison, Oct 2025](https://simonwillison.net/2025/Oct/07/vibe-engineering/)
- Kent Beck is reported as saying the leverage of "having big thoughts" has grown relative to language-level detail. [Type: opinion; Vendor: no; Unverified, search summary] — [Willison quoting Beck, Dec 2025](https://simonwillison.net/2025/Dec/16/kent-beck/)
- Charity Majors is reported to argue that AI "demands more engineering discipline", and has long held that no change should be accepted unless its author can answer "How will I know if this breaks?" [Type: opinion; Vendor: yes in a broad sense (Honeycomb sells observability tools); Unverified, search summary; I did not find the essay's URL, so this link is to the index where it was listed] — [Willison's tag page for Majors](https://simonwillison.net/tags/charity-majors/)
- Margaret-Anne Storey argues that health of a codebase now depends on shared understanding and recorded intent as much as on code quality. [Type: opinion; Vendor: no; Verified from abstract] — [Storey 2026](https://arxiv.org/abs/2603.22106)
- Experienced developers disagree among themselves on handing over high-level planning: 13 found agents suitable and 23 unsuitable. [Type: qualitative survey; Vendor: no; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- Anthropic staff described the boundary for design and "taste" tasks as a "moving target". [Type: interview study; Vendor: yes; Verified] — [Anthropic, Dec 2025](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)

### Inferences
- Disagreement 1: whether higher-level skills can be held without code-level fluency. Huang et al.'s participants cited "strong code comprehension and debugging skills" as part of effective use, and one said it is vital to "first [understand] coding and then [use] AI"; Beck's reported view points the other way. A tool that excludes code-reading skills is taking a side in an open dispute.
- Disagreement 2: whether planning and design remain human work. Practitioners split, and vendors' own staff call the line a moving target.
- Agreement is strongest on production accountability (Majors) and system understanding (Osmani, Storey), which are also the areas with the least controlled evidence.

### Gaps
- I did not read the Willison, Beck or Majors pieces in full; their positions here are from search summaries and should be checked before quoting.
- I found no practitioner source arguing that these higher-level skills will themselves be automated soon, though that view exists; the searches did not surface a citable statement of it.

## 6. Is there evidence that a specific skill predicts better outcomes when working with agents?

### Takeaway
No. I found no controlled study showing that a named higher-level skill, measured or trained, improves delivery outcomes with agents. The closest results are correlational, small, self-reported or at organisation level.

### Cited Findings
- Longer-tenured Claude users had about 4 percentage points higher conversation success after controls (about 5 points uncontrolled, 3 within the same task). They iterate more and are "much less likely" to use directive, delegating patterns. Success was judged by Claude itself; the authors note self-selection and survivorship bias. This covers all users, not developers specifically. [Type: observational data; Vendor: yes; P: n/a; S: weak; Verified] — [Anthropic Economic Index, March 2026](https://www.anthropic.com/research/economic-index-march-2026-report)
- In the Anthropic trial, participants who asked conceptual questions scored higher than those who delegated, in groups of 2 to 7, with learning (not delivery) as the outcome and no causal claim. [Type: controlled study, exploratory; Vendor: yes; S: weak; Verified] — [Anthropic, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills)
- METR's 2026 update reports no measured differences in speed-up by developer or task type, and calls its own estimate "a bad proxy" for real productivity because of selection. Late-2025 estimates: -18% time (CI -38% to +9%) for 10 returning developers, -4% (CI -15% to +9%) for 47 new ones; both intervals include zero. [Type: controlled study; Vendor: no; S: none; Verified] — [METR, Feb 2026](https://metr.org/blog/2026-02-24-uplift-update/)
- Developers say domain expertise and the ability to turn product requirements into accurate implementation plans are critical (65 of 99 and 13 of 99 survey mentions). [Type: qualitative survey; Vendor: no; S: weak, self-report; Verified] — [Huang et al. 2025](https://www.arxiv.org/abs/2512.14012)
- DORA's capabilities model reports organisational practices (reported to include a clear AI policy, a healthy data ecosystem, quality internal platforms, user-centric focus, small batches) that moderate AI's effect on performance. [Type: survey; Vendor: yes (Google); S: weak to moderate at organisation level; Unverified; only some of the seven were named in the sources I read] — [DORA 2025 report](https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf), [InfoQ summary](https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025)
- A single-case report of one engineer on a brownfield project attributes good results to thorough specifications together with the engineer's institutional knowledge. [Type: case study; Vendor: unknown; S: weak; Unverified, search summary] — [arXiv 2605.18461](https://arxiv.org/html/2605.18461v1)

### Inferences
- The Economic Index finding cuts against a simple "learn to delegate more" story: the more successful users delegated less directively and iterated more. Deciding what to delegate may be better framed as staying engaged than as handing off.
- A tool that trains these skills would be working ahead of the evidence. It could also be a means of producing that evidence, if it measured a skill and a later outcome.

### Gaps
- Unknown: whether any of the nine skills, measured in an individual, predicts fewer defects, faster delivery or fewer incidents with agents.
- Unknown: whether any of them can be trained by a tool in a way that transfers to real work. No intervention study was found.
- Unknown: whether findings from 2025 tools hold for late-2026 tools. METR states its own early-2025 result no longer reflects current impact.
- I did not verify the primary text of the DORA capabilities model, the spec-driven development study or the brownfield case study.
