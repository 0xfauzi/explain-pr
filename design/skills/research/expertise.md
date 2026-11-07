# Engineering expertise when agents write the code

Research angle: what makes expert software engineers beyond writing code, and which of those skills matter more now that coding agents write most of the code.

Scope rule from the user: this is a 2025 and later phenomenon. The report rests on studies of engineers working with AI coding tools and agents from 2025 onward. Older expertise research (Li, Ko and Zhu; Klein) is used only as a frame, and only where a 2025+ study supports the same point. Nothing is borrowed from other industries.

Labels used throughout:

- **Study**: a controlled experiment, field observation, interview study or survey with a stated method.
- **Data**: large-scale mining or telemetry (GitHub PRs, session logs, industry surveys).
- **Opinion**: position papers, vendor posts, practitioner writing.

Numbers are only given where a source states them. Where something is not measured, the report says so.

---

## 1. Summary

The 2025 and 2026 evidence points the same way across very different methods. When agents write code, the engineer's job shifts from producing code to directing and checking it. The skills that decide outcomes are the ones that sit around the code:

1. Verifying agent output (reading diffs, testing, running, debugging).
2. Planning and decomposing work into steps an agent can do and a human can check.
3. Specifying intent and context precisely.
4. Holding a mental model of the system (comprehension), so you can change and debug it later.
5. Design and architecture judgment, including recording why a decision was made.
6. Calibrated trust: knowing when to delegate, when not to, and noticing your own drift into rubber-stamping.
7. Domain knowledge: knowing what the software is for.
8. Error recovery and debugging when the agent goes wrong.
9. Security and quality judgment on generated code.

The strongest single finding: domain and engineering expertise still predicts success with agents (Anthropic Economics, 2026, about 400,000 Claude Code sessions). The strongest single warning: delegating without engaging lowers understanding and debugging ability (Anthropic RCT, 2026; Balepur et al., 2026), and human review attention appears to decline over time (Yu et al., 2026).

The core tension: the skills needed to supervise agents are the same skills that erode when you let agents do the work. Anthropic's internal study of its own engineers names this directly (Anthropic, Dec 2025). A tool that trains engineers while they build has to work against that erosion.

---

## 2. Older expertise research, used only as a frame

These are cited only to name concepts. Each is paired with 2025+ evidence later in the report.

- **Li, Ko and Zhu (ICSE 2015), "What makes a great software engineer?"** Interviews with 59 experienced Microsoft engineers. Great engineers were described in terms of decision making, mental models of the system, handling complexity, continuous learning, and working with others, not only code output. URL: https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf. (Study, pre-agent.)
- **Klein, recognition-primed decision making.** Experts in naturalistic settings recognise situations from experience and judge options by mentally simulating them. Relevant here only because the 2025+ studies show experts deciding fast which tasks to delegate and spotting wrong output. (Study tradition, pre-agent. No 2025+ study applies Klein's methods to agent use that I found. Unknown.)

Where these older ideas have no 2025+ support, this report does not use them.

---

## 3. The 2025+ evidence base

### 3.1 Field and survey studies of professionals using agents

**Huang, Reyna, Lerner, Xia, Hempel (Dec 2025). "Professional Software Developers Don't Vibe, They Control: AI Agent Use for Coding in 2025."** https://arxiv.org/html/2512.14012 (Study)

- Method: 13 field observations (45 min each plus 30 min interview) of developers with 3+ years experience (median 9), and a qualitative survey of 99 developers (mean 12.8 years).
- 11 of 13 observed participants controlled design themselves: writing plans, revising agent plans or polishing them.
- 50 of 99 survey respondents mentioned driving architecture and design themselves.
- All 13 controlled implementation to some degree. 9 carefully reviewed every change using diffs, tests, UI checks, CLI runs and debuggers.
- Participants ran agents on small chunks. Two participants with plans over 70 steps never ran more than 6 steps at once. Median about 1.8 steps per prompt.
- 12 observed participants and 43 survey respondents said prompts need clear context and explicit instructions.
- 11 observed participants and 65 survey respondents said existing expertise was critical: code comprehension, debugging, and turning product specs into plans.
- Tasks seen as unsuitable for agents: complex logic, business logic needing domain knowledge, security-critical code.

**Vella and Blincoe (May 2026). "The Impact of AI Coding Assistants on Software Engineering: A Longitudinal Study."** https://arxiv.org/html/2605.23135v1 (Study)

- Two questionnaires six months apart (Oct 2024, Apr 2025). Matched cohort of 95.
- 82% reported spending less time writing code by the second wave.
- Reviewing was the only task rated above the neutral midpoint.
- The balance between creation and verification tasks shifted significantly toward verification (adjusted p = 0.006).
- The authors name this "supervisory engineering work": directing, evaluating and correcting AI output.
- Maintainability as a primary concern rose from 3% to 19%.
- Limits: self-report, current AI users only, 40% attrition.

**Anthropic (Dec 2, 2025). "How AI is transforming work at Anthropic."** https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic (Study, internal survey of 132 engineers and researchers plus 53 interviews and Claude Code usage data. Vendor studying its own staff.)

- Engineers delegate tasks that are easily verifiable, low-stakes or boring.
- Use of Claude "generally involves active supervision and validation, especially in high-stakes work."
- Some engineers worry about erosion of the deeper skills needed to write and critique code. Quote: "When producing output is so easy and fast, it gets harder and harder to actually take the time to learn something."
- Some staff reported less collaboration with colleagues.

**Petridis, Liu, Fiannaca, Cai, Terry (Google DeepMind, Jan 2026). "Compass vs Railway Tracks."** https://arxiv.org/html/2601.11848v1 (Study)

- 16 lead users wrote one spec for a human colleague and one for an AI.
- Human specs gave high-level intent. AI specs were rigid and exhaustive: about 346 words versus 175.
- AI specs had prescriptive output templates, explicit information sources, and check-in policies to stop the AI "steamrolling" ahead.
- Participants saw the AI as a literal executor lacking judgment.

### 3.2 Large-scale telemetry and mining

**Hitzig, Massenkoff, Lyubich, Zhang, Heller, McCrory (Anthropic Economics, June 16, 2026). "Agentic coding and persistent returns to expertise."** https://www.anthropic.com/research/claude-code-expertise (Data. Vendor data, model-based classifiers, preliminary.)

- About 400,000 interactive Claude Code sessions from about 235,000 people, Oct 2025 to Apr 2026.
- Verified success (needs a hard signal such as passing tests or a commit): about 15% for novice-rated sessions versus 28 to 33% for intermediate and above.
- At least partial success: 77% novice versus 91 to 92%.
- Abandonment: 19% for novices versus 5 to 7% for others.
- In troubled sessions, verified success rises from 4% (novice) to 15% (expert). Experts recover from errors more easily.
- Most of the gain is from novice to intermediate. The intermediate to expert gap is modest.
- Users make about 70% of planning decisions and about 20% of execution decisions.
- Experts get about 12 agent actions per prompt versus about 5 for novices.
- Caveat: the expertise classifier scores precise framing, asking the agent to verify, and correcting the agent. So the skills and the expertise label are partly the same thing. Real-world use of the code is not observed.

**Yu et al. (June 2026). "Habituation at the Gate: Rising Approval and Declining Scrutiny in Human Review of AI Agent Code."** https://arxiv.org/html/2606.22721v1 (Data)

- AIDev dataset. 400 repeat reviewers who each reviewed 10+ agent PRs (11,429 reviews).
- Approval rate rose from 30.1% to 36.8% between each reviewer's early and late reviews (p < 10^-6).
- Inline comments per review fell 22%. Words per review fell 28%.
- Approval shift and comment effort were strongly negatively correlated (Spearman rho = -0.556).
- PR size stayed flat.
- In January 2025 agent PRs were approved less often than human PRs (30.7% vs 37.8%). By June agent approval was about 10 points higher, while human PR approval was flat or falling.
- The authors favour habituation over rational trust calibration but cannot rule calibration out. No direct measure of agent code quality over time.

**Duma, Wróblewski, Bobińska, Winiarska, Przymus (EASE 2026). "These Aren't the Reviews You're Looking For."** https://arxiv.org/html/2605.02273v1 (Data)

- 61.38% of agent PRs in the broader repository set had no recorded review.
- Of reviewed agent PRs, 58.77% had agent-only review and 10.14% human-only.
- 25.92% of human comments on agent PRs were steering the agent (for example "fix lint", "rerun tests"), versus 1.63% on human PRs.
- Caveat: off-platform review is invisible in the data.

**Watanabe, Li, Kashiwa, Reid, Iida, Hassan (2025, ACM). "On the Use of Agentic Coding: An Empirical Study of Pull Requests on GitHub."** https://arxiv.org/html/2509.14745v3 (Data)

- 567 Claude Code PRs across 157 projects. 83.77% merged versus 91.01% for matched human PRs.
- 45.1% of merged agent PRs needed revision. Of those, 47.7% of revisions were bug fixes, 27.1% refactoring, 29.0% documentation.
- 3.3% of rejections were for PRs too large to review.

**He, Miller, Agarwal, Kästner, Vasilescu (MSR 2026). "Does AI-Assisted Coding Deliver? / Speed at the Cost of Quality."** https://arxiv.org/abs/2511.04427 (Data, difference-in-differences)

- 806 to 807 repositories that adopted Cursor, against matched controls.
- Large but short-lived jump in lines added, fading after about two months.
- Static analysis warnings up about 30% and code complexity up about 41% (v2 estimates), described as persistent in v3.
- The rise in warnings and complexity is estimated to drive the later slowdown.

**Stack Overflow Developer Survey 2025.** https://survey.stackoverflow.co/2025/ (Data, survey of 49,000+)

- 66% cited "AI solutions that are almost right, but not quite" as a top frustration.
- 45% said debugging AI-generated code takes more time.
- Trust in AI accuracy reported at about 33%, down from 43% in 2024, per most coverage (one outlet gives 29%). Exact figure should be checked against the primary report.

**DORA 2025, State of AI-assisted Software Development (Google).** https://blog.google/technology/developers/dora-report-2025/ (Data, survey of nearly 5,000)

- About 90% use AI at work.
- About 24% report a great deal or a lot of trust in AI. About 30% trust it a little or not at all.
- AI is framed as an amplifier of existing strengths and weaknesses. AI adoption is linked to higher throughput but still affects stability.

**Veracode 2025 GenAI Code Security Report.** https://www.veracode.com/press-release/ai-generated-code-poses-major-security-risks-in-nearly-half-of-all-development-tasks-veracode-research-reveals/ (Data, vendor benchmark)

- 100+ LLMs, 80 tasks. Models chose the insecure option 45% of the time.
- Failure to defend against cross-site scripting in 86% of samples, log injection in 88%.
- A Nov 2025 update reported the best pass rate at 72% (GPT-5 Mini), with Claude Sonnet 4.5 at 50%. https://www.veracode.com/press-release/veracode-research-reveals-openais-gpt-5-models-lead-the-way-in-secure-code-while-wider-industry-progress-stalls/

### 3.3 Controlled experiments on learning and understanding

**Shen and Tamkin (Anthropic, Jan 29, 2026). "How AI assistance impacts the formation of coding skills."** https://www.anthropic.com/research/AI-assistance-coding-skills, paper arXiv:2601.20245 (Study, RCT)

- 52 mostly junior engineers learned the Python library Trio, with or without AI.
- AI group quiz average 50% versus 67% hand-coding (Cohen's d = 0.738, p = 0.01).
- Largest gap: debugging questions.
- Speed gain not statistically significant.
- Interaction style mattered (small groups, association only):
  - AI delegation: 39%. Progressive reliance: 35%. Iterative AI debugging: 24%.
  - Generation then comprehension: 86%. Hybrid code plus explanation: 68%. Conceptual inquiry: 65%.
- Caveat: chat assistant, not an agent. The authors expect agents could have larger effects.

**Balepur, Baumler, Chen, Choi, Rudinger, Boyd-Graber (July 2026). "(Im)Paired Programming: Coding Agents Improve Productivity but Harm Understanding."** https://arxiv.org/abs/2607.26375 (Study)

- 54 students building a website. Agent that edits code directly versus chatbot.
- Agents helped finish the first task but reduced comprehension and left students less able to extend their code without AI.
- Low-effort interactions (pasting prompts, accepting edits without review) were linked to weaker comprehension.
- Students knew they understood less but still preferred agents.
- Caveat: students, not professionals.

**METR (July 2025). "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity."** https://arxiv.org/abs/2507.09089 (Study, RCT)

- 16 experienced developers, 246 tasks in their own mature repositories.
- Tasks took about 19% longer with AI allowed. Developers still believed AI made them about 20% faster.
- Relevance here: self-assessment of AI benefit is unreliable. That is an argument for measured feedback, not for any particular skill.
- METR's Feb 2026 follow-up on late-2025 agents (57 developers, 800+ tasks) found estimates closer to a speedup, but METR called this "only very weak evidence", and many developers refused to work without AI. Primary post: https://metr.org/blog/ (secondary coverage only was read for this report: https://birchtree.me/blog/an-update-from-the-study-that-said-devs-were-actually-slower-with-coding-agents/).

### 3.4 Conceptual and practitioner work (opinion)

- **Storey (Mar 2026). "From Technical Debt to Cognitive and Intent Debt."** https://arxiv.org/abs/2603.22106 (Opinion, position paper.) Cognitive debt: loss of shared understanding in the team. Intent debt: missing written rationale, goals and constraints that both people and agents need.
- **Tavantzis, Trinkenreich, Greiler, Storey, Baldassarre et al. (2026). "Cognitive Debt in the GenAI Era."** https://arxiv.org/html/2610.37888 (Study of opinion: grey literature review of 76 practitioner sources, Feb 2025 to Sep 2026.) Cognitive debt stays hidden while "the code works, the tests pass, the features ship." Proposed practices: comprehension gates, review-sized changes, decision records, explaining generated code before commit. No prevalence figures.
- **Konrad et al. (ICSA 2026 workshop). "Architecture Without Architects."** https://arxiv.org/html/2604.04990v1 (Opinion, position paper with an illustrative case.) Agents make architectural choices with little justification or record ("vibe architecting"). Changing only the prompt produced structurally different systems for the same task.

---

## 4. The skills, ranked by strength of 2025+ evidence

Each skill lists: why it matters more with agents, the evidence and its type, how it erodes with agents, and a concrete moment in a build where a tool can train it.

### 4.1 Verifying agent output

**Why more important.** Work has shifted from creating code to checking it. The engineer is the last line of defence and agent code has real defect rates.

**Evidence.**
- Vella and Blincoe 2026: significant shift toward verification work (Study).
- Huang et al. 2025: 9 of 13 professionals reviewed every change with diffs, tests, runs and debuggers (Study).
- Anthropic Economics 2026: asking the agent to verify is one cue of expertise, and verified success is roughly double for non-novices (Data, classifier caveat).
- Watanabe et al. 2025: 45.1% of merged Claude Code PRs needed revision, nearly half of those for bugs (Data).
- Stack Overflow 2025: 66% frustrated by "almost right" output (Data).
- Veracode 2025: insecure choice in 45% of tasks (Data, vendor).

**How it erodes.** Yu et al. 2026: approval goes up and comment effort goes down as reviewers see more agent PRs (Data). Duma et al. 2026: many agent PRs get no human review at all (Data).

**Strength.** Strong.

**Train while building.** When the agent finishes a change, before the diff is accepted, ask the engineer to predict what the change does and how it could fail, then run the check (test, UI, log) that would show it. Track whether their review comments thin out over the session.

### 4.2 Planning and decomposing work

**Why more important.** Agents do well on small, well-described tasks. Humans make most planning decisions. Breaking work into checkable steps is what keeps control.

**Evidence.**
- Huang et al. 2025: 11 of 13 controlled design through plans. Median about 1.8 steps per prompt even with 70-step plans (Study).
- Anthropic Economics 2026: users make about 70% of planning decisions and about 20% of execution decisions (Data).
- Watanabe et al. 2025: some agent PRs rejected as too large to review (Data, small share: 3.3%).
- Tavantzis et al. 2026: "review-sized changes" proposed as prevention (Opinion).

**How it erodes.** Letting the agent plan and execute large chunks in one go. No direct measure of planning skill decline found. Unknown.

**Strength.** Strong.

**Train while building.** Before a multi-file task, ask the engineer to write or edit the plan and mark which step they will check after each agent run. Flag runs where the diff is bigger than the engineer can review.

### 4.3 Specifying intent and context

**Why more important.** The agent acts literally. It needs goals, constraints, sources and stopping rules a human colleague would infer.

**Evidence.**
- Petridis et al. 2026: AI specs about twice as long, with templates, sources and check-in rules (Study).
- Huang et al. 2025: 12 of 13 and 43 of 99 stressed clear context and explicit instructions (Study).
- Anthropic Economics 2026: precise framing is an expertise cue. Experts get about 12 actions per prompt versus about 5 (Data, classifier caveat).
- Storey 2026: missing rationale ("intent debt") hurts both people and agents (Opinion).

**How it erodes.** Low-effort prompting (pasting the task) was linked to weaker understanding in Balepur et al. 2026 (Study).

**Strength.** Moderate to strong. The evidence shows experts specify more precisely. It does not yet show that training specification causes better results.

**Train while building.** When the engineer writes a prompt, point out the missing constraint the agent then guessed at (for example a library choice or an edge case), so they see the link between spec gap and output.

### 4.4 Holding a mental model of the system (comprehension)

**Why more important.** Code produced faster than it is understood leaves a team that cannot safely change or debug it. Comprehension is also what makes verification possible.

**Evidence.**
- Shen and Tamkin 2026 RCT: AI group 17 points lower on comprehension, biggest gap on debugging (Study).
- Balepur et al. 2026: agents reduced comprehension and the ability to extend code without AI (Study).
- Huang et al. 2025: 65 of 99 named expertise including code comprehension as critical (Study).
- Tavantzis et al. 2026, Storey 2026: cognitive debt (Opinion).

**How it erodes.** Directly by delegation. In Shen and Tamkin, "generation then comprehension" and "conceptual inquiry" patterns kept scores at 65% or higher, while full delegation fell below 40% (Study, small groups).

**Strength.** Strong for the erosion effect. Moderate for which habits protect it.

**Train while building.** After an agent change lands, ask one short question about it ("what calls this?", "what happens if this input is empty?"). Offer an explanation only after the engineer tries.

### 4.5 Debugging and recovering from agent errors

**Why more important.** When the agent goes wrong, someone must diagnose it. Experts recover. Novices abandon.

**Evidence.**
- Anthropic Economics 2026: in troubled sessions verified success 4% for novices versus 15% for experts. Abandonment 19% versus 5 to 7% (Data).
- Shen and Tamkin 2026: largest skill gap on debugging. "Iterative AI debugging" pattern scored lowest (24%) (Study).
- Stack Overflow 2025: 45% say debugging AI code takes longer (Data).
- Tavantzis et al. 2026: practitioners spend time rebuilding mental models to debug generated code (Opinion).

**How it erodes.** Handing every failure back to the agent. Shen and Tamkin's lowest pattern is exactly this.

**Strength.** Strong.

**Train while building.** When a test fails after an agent change, ask the engineer for a hypothesis before re-prompting the agent. Record whether their hypothesis was right.

### 4.6 Calibrated trust and delegation judgment

**Why more important.** Engineers must decide, many times a day, what to hand over and how much to check. Both over-trust and blanket distrust cost.

**Evidence.**
- Anthropic Dec 2025: engineers delegate easily verifiable, low-stakes, boring tasks (Study, internal).
- Huang et al. 2025: complex logic, domain business logic and security-critical code judged unsuitable (Study).
- Yu et al. 2026: rising approval with falling scrutiny (Data).
- METR 2025: developers believed they were 20% faster while being 19% slower (Study). Self-perception of AI benefit is unreliable.
- DORA 2025, Stack Overflow 2025: low reported trust alongside high use (Data).

**How it erodes.** Habituation (Yu et al. 2026). Klein-style recognition of "this looks wrong" depends on experience, which delegation reduces. No study tests this link directly. Unknown.

**Strength.** Moderate. Strong evidence that calibration drifts. Weak evidence on how to train it.

**Train while building.** Show the engineer their own record: how often their accepted agent changes later needed fixes, by task type. That gives measured feedback in place of a feeling.

### 4.7 Design and architecture judgment, with recorded rationale

**Why more important.** Agents make architectural choices silently. Quality and complexity drift. Someone has to own the shape of the system.

**Evidence.**
- Huang et al. 2025: 50 of 99 drive architecture and design themselves (Study).
- He et al. 2026: persistent rise in warnings and complexity after Cursor adoption, linked to later slowdown (Data).
- Vella and Blincoe 2026: maintainability concern rose from 3% to 19% (Study).
- Konrad et al. 2026: "vibe architecting" (Opinion).
- Storey 2026: intent debt (Opinion).

**How it erodes.** Accepting the agent's default framework, structure and dependencies without a decision. No direct measure of design-skill decline found. Unknown.

**Strength.** Moderate. Good evidence the problem is real. Little evidence on the skill itself.

**Train while building.** When an agent adds a dependency, new module or new pattern, stop and ask the engineer to accept or reject it as a decision and write one line of why.

### 4.8 Domain knowledge (what the software is for)

**Why more important.** Agents lack the business and user context. Tasks needing domain knowledge are the ones professionals keep for themselves.

**Evidence.**
- Anthropic Economics 2026: expertise in the task's domain, not occupation, predicts success. Software-occupation users only slightly ahead (34% versus 29% verified success) (Data).
- Huang et al. 2025: business logic needing domain knowledge judged unsuitable for agents. Turning product specs into plans named as a critical skill (Study).

**How it erodes.** Not measured. Unknown.

**Strength.** Moderate.

**Train while building.** When the engineer writes a spec, ask what the user of the feature needs to be true, and whether a test captures it.

### 4.9 Security and quality judgment on generated code

**Why more important.** Generated code makes insecure choices often, and few agent PRs get human review.

**Evidence.**
- Veracode 2025: 45% insecure choice rate (Data, vendor).
- Huang et al. 2025: security-critical code kept away from agents (Study).
- Duma et al. 2026: most agent PRs have no recorded human review (Data).

**How it erodes.** Not measured directly. Unknown.

**Strength.** Moderate. This is a specialised form of 4.1.

**Train while building.** When an agent change touches input handling, auth or logging, prompt the engineer to name the likely attack and check for it before accepting.

---

## 5. Cross-cutting findings

**The supervision paradox.** Supervising agents needs the expertise that delegation erodes. Named by Anthropic engineers (Dec 2025, Study, internal), measured for comprehension and debugging in two experiments (Shen and Tamkin 2026; Balepur et al. 2026), and seen in review behaviour (Yu et al. 2026). The experiments use juniors and students. Whether experienced engineers lose existing skills is not measured. Unknown.

**How you use the agent matters more than whether you use it.** In Shen and Tamkin 2026, asking for explanations or asking conceptual questions kept learning outcomes close to or above the no-AI group. In Balepur et al. 2026, low-effort accepting was linked to weaker understanding. Both are associations within small groups (Study).

**Self-assessment is unreliable.** METR 2025: perceived speedup while measured slowdown (Study). Balepur et al. 2026: students knew they understood less but still preferred agents (Study). A training tool should give measured feedback, not rely on how engineers feel.

**Most gain is from novice to intermediate.** Anthropic Economics 2026 (Data). Basic engineering competence still pays off. Deep code-writing skill beyond that shows smaller returns in that data.

---

## 6. What older expertise research still adds, and what it does not

| Older idea | 2025+ support | Use |
| --- | --- | --- |
| Experts hold mental models of the system (Li, Ko, Zhu 2015) | Shen and Tamkin 2026; Balepur et al. 2026; Storey 2026 | Keep. Now at risk from delegation. |
| Experts make sound decisions under uncertainty (Li, Ko, Zhu 2015) | Huang et al. 2025 delegation choices; Anthropic Economics 2026 planning share | Keep. Shows up as delegation and planning. |
| Recognition-primed decisions from experience (Klein) | Indirect only: expert recovery rates (Anthropic Economics 2026) | Frame only. No direct 2025+ test. |
| Continuous learning (Li, Ko, Zhu 2015) | Anthropic Dec 2025 worries about learning; Shen and Tamkin 2026 | Keep. Learning is now actively harder. |

---

## 7. Gaps and unknowns

- No 2025+ study measures whether experienced professionals lose skills over months of agent use. The RCTs use juniors and students, measured right after the task.
- No study shows that training any of these skills causes better agent outcomes. Most evidence is correlational.
- The largest telemetry study (Anthropic Economics 2026) is vendor data with model-based labels. Its expertise label partly encodes the behaviours being studied.
- Architecture and design judgment with agents has position papers but no rigorous empirical study found.
- Domain knowledge and security judgment erosion are not measured.
- Review-mining studies cannot see off-platform review.

---

## 8. Sources

Studies and data (2025 to 2026):

- Huang et al. 2025, Don't Vibe, They Control: https://arxiv.org/html/2512.14012
- Vella and Blincoe 2026, longitudinal study: https://arxiv.org/html/2605.23135v1
- Anthropic Dec 2025, How AI is transforming work at Anthropic: https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- Petridis et al. 2026, Compass vs Railway Tracks: https://arxiv.org/html/2601.11848v1
- Hitzig et al. 2026, Agentic coding and persistent returns to expertise: https://www.anthropic.com/research/claude-code-expertise
- Yu et al. 2026, Habituation at the Gate: https://arxiv.org/html/2606.22721v1
- Duma et al. 2026, How Humans Review AI-Generated PRs: https://arxiv.org/html/2605.02273v1
- Watanabe et al. 2025, Agentic coding PRs on GitHub: https://arxiv.org/html/2509.14745v3
- He et al. 2026, Cursor difference-in-differences: https://arxiv.org/abs/2511.04427
- Shen and Tamkin 2026, AI assistance and coding skills: https://www.anthropic.com/research/AI-assistance-coding-skills
- Balepur et al. 2026, (Im)Paired Programming: https://arxiv.org/abs/2607.26375
- METR 2025 RCT: https://arxiv.org/abs/2507.09089
- Stack Overflow Developer Survey 2025: https://survey.stackoverflow.co/2025/
- DORA 2025 report summary: https://blog.google/technology/developers/dora-report-2025/
- Veracode 2025 GenAI Code Security Report: https://www.veracode.com/press-release/ai-generated-code-poses-major-security-risks-in-nearly-half-of-all-development-tasks-veracode-research-reveals/

Opinion and reviews of opinion (2026):

- Storey 2026, Triple Debt Model: https://arxiv.org/abs/2603.22106
- Tavantzis et al. 2026, Cognitive Debt grey literature review: https://arxiv.org/html/2610.37888
- Konrad et al. 2026, Architecture Without Architects: https://arxiv.org/html/2604.04990v1

Frame only (pre-agent):

- Li, Ko, Zhu 2015, What makes a great software engineer: https://faculty.washington.edu/ajko/papers/Li2015GreatEngineers.pdf
