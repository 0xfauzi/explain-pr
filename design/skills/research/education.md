# How computing education is responding to coding agents (2025 to 2026)

Angle: what universities, ACM and IEEE bodies, CS education researchers, bootcamps and company training programs now prioritise, and which teaching methods have evidence behind them.

Scope note. This report stays inside software and computing education. It uses sources from 2025 and 2026 wherever possible, because the shift from chat assistants to agents (Claude Code, Codex, Cursor agent mode, Copilot agent) is a 2025 change. A few 2024 papers are cited only where 2025 to 2026 work builds directly on them, and they are marked as such. Analogies from other professions (medicine, aviation, and so on) are not used as evidence.

Labels used throughout:
- **Evidence**: a study with data (experiment, survey, log analysis, course evaluation).
- **Experience report**: an instructor describing a course they ran, with little or no measured outcome.
- **Opinion**: expert or committee judgement, workshop consensus, or a proposed curriculum.

---

## 1. Summary

1. The education community has moved, in 2025 and 2026, from "ban or allow" to "allow, but make students prove they understand." The ACM task force survey of 763 educators (2025) found 64% had changed their teaching and 68% had changed their assessment.
2. The skills that institutions now push up the priority list are, in order of how much evidence supports them:
   - verifying agent output (reading, reviewing and testing code you did not write),
   - debugging and diagnosis without leaning on the AI,
   - explaining and defending your own code and design choices,
   - self-monitoring of AI use (knowing when you do not understand),
   - specifying and decomposing problems before delegating,
   - system design and working inside existing codebases,
   - foundational CS knowledge as the basis for judgement.
3. "Prompt engineering" is the skill most often taught (ITiCSE 2025 survey), but both students and faculty doubt it lasts. It ranks low as a durable skill.
4. The teaching methods with the best support are: oral code review interviews, reflection plus disclosure of AI transcripts, peer review and test-sharing activities, "friction" designs that make the learner think before the AI reveals code, and a shift of grade weight towards in-person and process-based assessment.
5. Agent-specific evidence is still thin. Most measured studies use chat assistants or Copilot in CS1. Agent-based courses (Stanford CS146S, Brown Agentic Studio, UC Riverside CS 180, UT Austin CS 378, FHNW) started in late 2025 or 2026 and have published experience reports, not controlled outcomes.

---

## 2. What official bodies say

### 2.1 ACM, IEEE-CS and AAAI: CS2023

- CS2023 is still the current curriculum standard. It was endorsed in early 2024, before agents were common. It gives generative AI one chapter and raises AI to a core knowledge area. Source: [ACM bulletin on CS2023](https://www.acm.org/articles/bulletins/2024/june/cs2023-curricular-guidelines). (Opinion, committee guidance.)
- There is no ACM/IEEE addendum on agents as of this report. The NUS-Google white paper (section 2.3) says CS2023 "does not explicitly foreground" what it calls a verification spectrum. Source: [arXiv 2606.07545](https://arxiv.org/abs/2606.07545). (Opinion.)

### 2.2 ACM Task Force on Generative AI and Programming Assessment (final report, February 2026)

Source: [ACM Taskforce GenAI Report, 16 Feb 2026](https://acm-education-genai-task-force.github.io/ACM_Taskforce_GenAI_Report_16Feb26.pdf). Authors include Gordon, Denny, Kiesler, Kumar, Keuning, Leinonen, Kumar and Prather.

Method: a global survey, May to October 2025, 763 responses. About 500 answered most questions. Open answers were themed with Claude 4.5 Sonnet and then manually checked. (Evidence, survey.)

Findings relevant to skills:
- 69% of 512 respondents think the skills needed to create software have changed (32% "definitely", 37% "probably"). 17% think they have not.
- Teaching of small-scale coding, debugging and documentation changed "a lot" most often.
- 64% of 469 had changed their course; 68% of 459 had changed assessment.
- Top concern: "increased dependency on technology to complete coursework", 87% of 510.
- Named shifts in emphasis (counts of open responses): focus on code comprehension (15), debugging and testing of AI code (17), problem solving and design over syntax (16), critical evaluation of AI output (11), required disclosure of AI use (9), explicit AI use and prompting (39).
- Assessment changes: more in-person or proctored exams (56), oral assessment or defence (36), paper exams (35), project work (34), process over product (19), AI disclosure with prompts and transcripts (16), explain-all-code requirements (15), more debugging and comprehension questions (12).
- Educators reported "Skill atrophy: Students producing overly complex code they cannot understand, debug, or explain" and that less-skilled students use AI more but benefit less.
- The report notes a move away from trying to make assignments "AI-proof".

Caveat: counts of open-text themes are small, and the theming was done by an LLM with manual validation. The survey covers generative AI broadly, not agents specifically.

### 2.3 NUS-Google workshops white paper (June 2026)

Source: [Reshaping Undergraduate Computer Science Education in the Generative AI Era, arXiv 2606.07545](https://arxiv.org/abs/2606.07545). 24 authors from many universities. Two workshops: 30 faculty and industry attendees in November 2025, and a student workshop in January 2026. (Opinion, workshop consensus. The authors list their own limits: self-selected participants, perceptions not outcomes.)

Key positions:
- AI now does many tasks once given to junior engineers. Humans should take the role of the "senior software engineer" who verifies.
- Three higher-level skills named by faculty: **abstraction**, **verification**, and **taking responsibility for systems**.
- Verification is defined as a spectrum: informal code review and testing, then static analysis and type-guided development, then formal verification. The paper calls specification and verification "arguably the most durable technical skill a CS graduate can possess."
- Recommends "lightweight formal specification (such as preconditions, postconditions, and contracts)" so students learn "to express intent precisely."
- Students named **specification writing**, **critical code review** and **troubleshooting edge cases** as skills whose importance has grown. They doubted the long-term value of prompt engineering.
- Proposed methods: "reverse-engineering" (extract specifications from existing solutions), larger real-world projects, assessing the process of AI interaction, and submission of AI interaction history.
- Raises a "Junior Engineer problem": graduates may need senior-level architecture skills on day one, because the junior apprenticeship tasks are now done by AI.

### 2.4 ITiCSE 2025 working group: post-introductory courses

Source: Bouvier et al., [The Rest of the Robots: Generative AI in Post-introductory Computing Education](https://doi.org/10.1145/3760545.3783970), ITiCSE-WGR 2025 (open copy at [Swansea repository](https://cronfa.swansea.ac.uk/Record/cronfa71419)). (Evidence: systematic review plus a survey of 118 instructors.)

- 56 of 118 instructors (47%) had integrated GenAI in upper-level courses.
- Among those, the GenAI skill most taught was prompt engineering (26), then artifact generation (17), refinement (15) and evaluation (14). Only 8 taught using GenAI for problem decomposition, and 25 taught no GenAI skill at all.
- The authors flag the low rate of decomposition teaching as a gap, because it is "a higher-order, transferable skill."
- Assessment changes being considered: oral explanation of deliverables (28), responsible use over AI-proofing (23), more reflection (20), more points for the development process (19), in-person feature changes to delivered code (13), more attention to evidence of testing (12).
- In software testing courses, GenAI handled basic test generation but struggled with more formal testing concepts.

### 2.5 Industry voice in an ACM venue: Russinovich and Hanselman (2026)

Source: coverage in [The Register, 23 Feb 2026](https://www.theregister.com/2026/02/23/microsoft_ai_entry_level_russinovich_hanselman/) of "Redefining the Engineering Profession for AI" (ACM Digital Library). (Opinion. The authors say it is not official Microsoft research.)

- Agents give seniors a boost but impose "an AI drag on early-in-career (EiC) developers" who must steer, verify and integrate AI output.
- Failure modes juniors may miss, while the agent reports success: serious bugs, inefficient algorithms, duplicated code, dismissed crashes and hangs, leftover debug code, code that passes the given tests but fails in general.
- Main example: an agent "fixed" a race condition by inserting a sleep. Only an engineer who understands synchronisation could point this out.
- Proposal: keep hiring early-career engineers, accept lower early output, pair them with seniors who direct agents together, and make their growth an explicit goal. Russinovich said Microsoft is piloting this. The authors also suggest some university classes where AI use counts as cheating.

---

## 3. University courses built around agents (2025 to 2026)

These are the first courses designed for agents rather than chat assistants. Almost all evidence here is experience reports.

### 3.1 Brown University: Agentic Studio (Spring 2026)

Sources: [Brown news, 11 June 2026](https://www.brown.edu/news/2026-06-11/agentic-studio-ai-programming); [course visitors page](https://cs.brown.edu/courses/csci1970kf/agentic-spr-2026/visitors.html). Instructors: Kathi Fisler, Shriram Krishnamurthi, Michael Littman. About 20 students chosen from about 80 applicants. (Experience report.)

- Hypothesis: "teaching early stages of agentic coding amounts to teaching core principles of software engineering and design."
- Students built projects with Claude (Tetris variants including an "upside-down" version, a graduation requirements checker, a chat client and others).
- Methods: chat transcripts submitted through GitHub; reflection journals on how work was split between student and Claude; test writing; code reviews and design critiques; a "TestFest" where each student's code ran against every other student's tests.
- Observed: the agent made frequent errors once a task left familiar patterns ("Just flipping the game over caused things to get interesting", Fisler). Code often worked but was messy and hard to extend.
- Most students set their own limits on agent use. A majority worried about not understanding their own codebases. Peer review and critique were the most valued part. Students took up testing and design practices well but engaged less with "externalization" (writing their reasoning down) than hoped.
- Blind spots found: students often did not understand how websites work; differences in prior experience mattered more than expected.

### 3.2 Stanford CS146S: The Modern Software Developer (Fall 2025, Fall 2026)

Sources: [course site](https://themodernsoftware.dev); [Stanford Bulletin entry](https://bulletin.stanford.edu/courses/2274401); public assignment repository summarised at [this mirror](https://courses-dn9.pages.dev/modern-software-dev-assignments/index.html). Instructor: Mihail Eric. (Course design only. No published outcomes.)

- Fall 2025 topics (from the assignment repository, a secondary source): prompting, building an MCP server, Claude Code automations (commands, hooks, subagents), multi-agent workflows, security scanning with Semgrep and fixing OWASP-type flaws, manual versus AI-assisted code review, and building the same app on three stacks to compare choices.
- Fall 2026 site lists spec-driven development, agent skills, "loop engineering" and "the software factory", framed as humans and agents planning, building, evaluating and improving software together.
- Prerequisites are systems and algorithms courses (CS111/CS161 equivalent). The course assumes fundamentals first.

### 3.3 Other agent-era course redesigns

- **UC Riverside CS 180, Spring 2026** ([course page](https://www.cs.ucr.edu/~qzhang/cs180-spring2026.html)): the intro software engineering course follows the lifecycle (requirements, design, implementation, testing and CI, verification and release), with agents used in each phase. A stated outcome is to "Evaluate coding agent outputs and integrate them safely into engineering workflows." Milestones include a design review and a testing milestone. (Course design.)
- **UT Austin CS 378 Agentic Software Engineering, Fall 2026** ([course page](https://www.cs.utexas.edu/~witchel/378AC/), unavailable when checked; description from search snippet): teaches students to split a problem into "what you specify, what you delegate, and what you verify." (Course design. Not verified against the live page.)
- **FHNW, AI-assisted Software Development** ([arXiv 2609.24348](https://arxiv.org/abs/2609.24348), accepted at URAI 2026): a "lean and spec-driven" lifecycle using specifications, AGENTS.md files and phase-specific skill files so agents work "with bounded autonomy in an explicit, reviewable, test-oriented lifecycle." Evaluated by a student survey; numbers not in the abstract. (Experience report.)
- **ASE-26 curriculum proposal** ([arXiv 2606.01152](https://arxiv.org/abs/2606.01152), Gorsky, May 2026): a 21-module undergraduate curriculum for agentic software engineering. Principles include "verification before trust" and an audit trail linking intent, specification, context, agent trajectory and verification. Students are graded on the design of verification gates, not only on final correctness. I only read abstracts and summaries. (Opinion, proposed curriculum.)
- **Northeastern Vancouver "CS 1.5"** ([arXiv 2604.16365](https://arxiv.org/abs/2604.16365), 2026): merges CS1 with discrete structures in a 4-hour studio, shifting from code generation to code comprehension and linking proofs to implementation. No outcome numbers in the abstract. (Experience report.)
- **Virginia Tech CS2 "DURA"** ([arXiv 2606.30908](https://arxiv.org/abs/2606.30908), SIGCSE Virtual 2026): Demystify how LLMs work, Use with attribution, Reflect three times a semester, Assess with more weight on proctored exams that test assignment skills. Office hour use rose slightly; students described strategic use. (Experience report.)

---

## 4. CS education research, 2025 to 2026 (with two 2024 anchors)

### 4.1 Learning loss when AI writes the code

**Anthropic randomized trial, January 2026.** Source: [Anthropic research post](https://www.anthropic.com/research/AI-assistance-coding-skills); [arXiv 2601.20245](https://arxiv.org/abs/2601.20245). (Evidence, RCT.)
- 52 mostly junior developers learned an unfamiliar async library (Trio). AI group had a sidebar assistant.
- Quiz: AI group 50%, hand-coding group 67% (Cohen's d = 0.738, p = 0.01). Time saved was about 2 minutes and not significant.
- Largest gap was on **debugging** questions.
- Usage pattern mattered (small groups, correlational): "generation-then-comprehension" (about 86%, n=2), "hybrid code-explanation" (about 68%, n=3) and "conceptual inquiry" (about 65%, n=7) scored high. "AI delegation" (about 39%), "progressive AI reliance" (about 35%) and "iterative AI debugging" (about 24%) scored low.
- Limits stated by the authors: small sample, immediate quiz only, sidebar assistant rather than an agent. They expect agents could have a stronger effect.

**Koli Calling 2025: "pseudo-apprenticeship".** Source: Hak et al., [arXiv 2510.04986](https://arxiv.org/abs/2510.04986). (Evidence, think-aloud, n=14 CS1 students.)
- 79% asked for a full solution at least once. No participant used a debugger; 57% relied on the LLM to debug.
- Students said they used LLMs as a "last resort" but most used them right after the first compiler error.
- Core pattern: students stay in the "watch the expert" phase, reading without refining, skipping productive struggle and giving up ownership of the problem.
- Teaching suggestions: require written reasoning before coding, make AI-written and student-written code visible, do early struggle in supervised labs.

**ICER 2025: Copilot on brownfield tasks.** Source: Shihab et al., [arXiv 2506.10051](https://arxiv.org/abs/2506.10051). (Evidence, n=10 upper-year students, 3,818-line legacy app.)
- 34.9% less time on one task and about 50% more tests passed with Copilot.
- Manual coding fell from 95.6% to 52.5% of coding time. The workflow changed from read, understand, implement to prompt, read response, implement.
- Higher performers pasted less AI code wholesale. Students worried they did not understand the code ("it's not your own logic").
- Recommends learning outcomes for code comprehension and critical evaluation of AI output in existing codebases.

**2024 anchor: Prather et al., "The Widening Gap", ICER 2024.** Source: [arXiv 2405.17739](https://arxiv.org/abs/2405.17739). (Evidence, 21 lab sessions with eye tracking.) Struggling novices kept their metacognitive problems, which AI could make worse, and often left with an "illusion of competence." Students who did well used AI to write code they had already planned. The 2026 ACM report confirms educators still see this gap.

**Professional developers, 2025: METR trial.** Source: [METR blog post](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/); [arXiv 2507.09089](https://arxiv.org/abs/2507.09089). (Evidence, RCT, 16 experienced developers, 246 tasks.) Developers took 19% longer with AI tools but believed they were 20% faster. Cited in the NUS-Google paper as a reason to teach calibration of one's own judgement. Not an education study, but it is the same population students are joining.

### 4.2 Course outcomes when AI is allowed

**UC San Diego CS1-LLM.** Source: Vadaparty et al., [Evaluating CS1-LLM, arXiv 2510.18806](https://arxiv.org/abs/2510.18806) (2025, ACM 2026). (Evidence, course evaluation.)
- CS1 redesigned to reduce syntax and writing from scratch, and teach skills for producing software with an LLM, including large open-ended projects.
- Exam outcomes, including across demographic groups, were "largely similar" to historical non-LLM offerings. Equity gaps persisted.
- About a quarter of students (23.9% mid-term, 25.4% end of term) worried about over-reliance.

**Utah State CS1-CR: code review interviews.** Source: Fowles et al., [Combating Harms of Generative AI in CS1 with Code Review Interviews and a Flipped Classroom, arXiv 2605.21374](https://arxiv.org/abs/2605.21374). (Evidence, quasi-experiment, Fall 2025, 96 students.)
- AI allowed freely. Each week a trained TA held a 15-minute interview covering the plan, a plain-English explanation and a code explanation, including reflection on AI use. The interview was 70% of each assignment grade. Missing it gave zero.
- Pasted characters rose from 61.0% to 68.1% of input (p < 0.0001), so AI use went up.
- Exam scores did not drop. Differences against earlier years were not significant (for example +2.38%, p = 0.078).
- 65% said reviews helped them avoid over-reliance; 90% said they were motivated to understand their code better; 72% wanted to keep the reviews.
- Problems: TA inconsistency (31 of 92), scheduling (20). Scaling to 200+ students with the same 11 TAs is unstudied.
- Best reading: high AI use plus mandatory explanation produced no measurable learning loss. It did not prove gains.

**SIGCSE 2026 poster: peer code review.** Source: Du, Pei and Yan, [SIGCSE TS 2026 poster](https://sigcse2026.sigcse.org/details/sigcse-ts-2026-posters/49/Learning-as-a-Reviewer-but-not-a-Reviewee-Understanding-Students-Perceptions-of-Pee). (Evidence, preliminary survey.) Seniors valued reviewing others' code, found giving good feedback hard, and were mixed about being reviewed.

### 4.3 Designing AI so that learners stay engaged

**Kazemitabaar et al., IUI 2025.** Source: [arXiv 2410.08922](https://arxiv.org/abs/2410.08922); [author PDF](https://austinhenley.com/pubs/Kazemitabaar2025IUI_AIFriction.pdf). (Evidence, two experiments, N=82 then N=42.)
- Tested seven ways to add friction before or around AI-generated code.
- **Lead-and-Reveal** (the AI walks through the problem and reveals code only after the learner states their reasoning) best matched learners' perceived and actual ability, without raising cognitive load.
- **Trace-and-Predict** (learner traces the code with a sample input and predicts variable values) was the other balanced technique.
- Direct design lesson for a tool: ask for the learner's plan or prediction before showing the agent's code.

**Usage data: Anthropic Education Report, April 2025.** Source: [Anthropic](https://www.anthropic.com/news/anthropic-education-report-how-university-students-use-claude). (Evidence, about 1 million education conversations, 18 days, Claude.ai.) Computer science students made up 36.8% of student conversations. About 47% of conversations were "direct" (asking for answers or outputs with little back-and-forth). Claude's responses were mostly at the "creating" (39.8%) and "analyzing" (30.2%) levels of Bloom's taxonomy, which the report flags as possible offloading of higher-order thinking. Caveat: early adopters, one product, no learning outcomes.

---

## 5. Bootcamps and company onboarding

The evidence here is weak. I looked for primary sources and found few.

- **Bootcamps.** I found no primary curriculum announcement from major bootcamps (Launch School, Turing, App Academy, Codesmith, Hack Reactor) describing an agent-era redesign. Many short commercial courses now teach Claude Code or Cursor (for example [Codecademy](https://www.codecademy.com/learn/ai-assisted-development-with-claude-code), [Nashville Software School](https://nashvillesoftwareschool.com/programs/agentic-ai-tools-for-developers)), but they teach tool use, not the higher skills, and report no outcomes. Unknown: whether bootcamps have changed what they assess.
- **Company onboarding.** The most substantive source is the Russinovich and Hanselman proposal (section 2.5): seniors and early-career engineers directing agents together, with the junior's growth as an explicit goal. Microsoft is piloting it; no results are public. A claim that AI use cuts time to tenth pull request from about 91 to 49 days is attributed to a DX 2025 study by [a secondary post](https://codepipelines.pages.dev/guides/developer-onboarding-ai-2026); I could not verify it, so treat it as unknown. Most other onboarding content I found was vendor marketing.
- **Tool vendors' learning modes.** Anthropic's 2026 RCT recommends learning-oriented modes (it names Claude Code's Learning and Explanatory output styles and ChatGPT Study Mode). No outcome study of these modes was found. (Opinion.)

Gap: there is no published controlled study of how early-career engineers learn while onboarding with agents.

---

## 6. Skills now prioritised, with strength of evidence

Strength key: **strong** = several measured studies from 2025 to 2026 point the same way; **moderate** = one measured study plus consistent institutional moves; **weak** = mainly opinion or course design.

### 6.1 Verifying agent output: reading, reviewing and testing code you did not write
- Why: the ACM survey, the ITiCSE survey, the NUS-Google workshops and every agent course name it. The human becomes the reviewer.
- Evidence: ACM 2026 survey (comprehension, debugging and testing of AI code as shifts in emphasis); ICER 2025 brownfield study (workflow becomes prompt then read response; stronger students paste less); Anthropic RCT (code reading and debugging scores fall when AI writes); Brown TestFest and code review. NUS-Google calls it the most durable skill (opinion).
- Strength: strong.
- Erodes with agents: yes. Reading output without refining it is the "pseudo-apprenticeship" pattern.

### 6.2 Debugging and diagnosis without handing the bug back to the agent
- Evidence: Anthropic RCT, largest gap on debugging; "iterative AI debugging" was the lowest-scoring pattern (about 24%). Koli 2025: no student used a debugger. Russinovich and Hanselman: the sleep-for-a-race-condition example (opinion).
- Strength: strong.

### 6.3 Explaining and defending your own code and design decisions (ownership)
- Evidence: Utah State CS1-CR (no learning loss despite more AI use; 90% motivated to understand their code). ACM survey: oral defence is the second most common assessment change. ITiCSE: oral explanation of deliverables is the top assessment change considered (28). Brown: students worried they did not understand their own codebases.
- Strength: moderate to strong.

### 6.4 Self-monitoring and calibration of AI use (metacognition)
- Evidence: Prather 2024 illusion of competence; METR 2025 perception gap (19% slower, felt 20% faster); Kazemitabaar 2025 (Lead-and-Reveal improved calibration); Koli 2025 (self-report did not match behaviour); Anthropic RCT (usage pattern linked to learning). NUS-Google students named self-regulation and metacognition as key meta-skills (opinion).
- Strength: strong for the problem, moderate for the fix.

### 6.5 Specifying and decomposing the problem before delegating
- Evidence: mostly opinion and course design. NUS-Google (specification writing, contracts, "teaching up the abstraction ladder"); UT Austin "specify, delegate, verify"; Stanford CS146S spec-driven development; FHNW spec-driven lifecycle; Brown "defining tasks". ITiCSE 2025 found only 8 of 56 integrators teach decomposition, a named gap.
- Strength: moderate (wide agreement, little measured outcome).

### 6.6 Designing tests and verification gates
- Evidence: Brown TestFest; ASE-26 grades the design of verification gates (opinion); NUS-Google verification spectrum including property-based testing and static analysis (opinion); ITiCSE: GenAI handles basic tests but not formal testing concepts; ITiCSE assessment change "evidence of testing" (12).
- Strength: moderate.

### 6.7 System design, architecture and working in existing codebases
- Evidence: Brown (agent code works but is hard to extend; "start with the fundamentals of what makes a good program", a student); ICER 2025 brownfield study; NUS-Google "Junior Engineer problem"; UC Riverside design review milestone; He et al. (cited in NUS-Google) found Cursor adoption raised static analysis warnings and code complexity.
- Strength: moderate.

### 6.8 Foundational CS knowledge as the basis for judgement
- Evidence: NUS-Google faculty and students both say fundamentals matter more (opinion); Russinovich (synchronisation knowledge needed to catch the agent, opinion); Stanford CS146S requires systems and algorithms first; CS 1.5 merges discrete maths with CS1. Anthropic RCT: conceptual inquiry linked to higher scores.
- Strength: moderate.

### 6.9 Making your reasoning and process visible
- Evidence: ACM and ITiCSE surveys (process over product, AI transcript disclosure, reflection); Brown journals and transcripts, with low student uptake of externalisation; DURA reflections; Koli 2025 recommends written reasoning before coding.
- Strength: moderate as a teaching method. Weak as a direct measure of skill gain.

### 6.10 Responsibility, security and ethics of what gets shipped
- Evidence: NUS-Google "taking responsibility for systems" (opinion); Stanford CS146S security week; ITiCSE ethics working group. No outcome data found.
- Strength: weak.

### 6.11 Prompting and agent configuration
- Evidence: most taught GenAI skill in ITiCSE 2025 (26 of 56); ACM survey (39 responses). NUS-Google students doubt its long-term value. Agent configuration (AGENTS.md, skills, hooks) appears in Stanford and FHNW. No evidence links it to better engineering judgement.
- Strength: weak as a durable higher-level skill.

---

## 7. Teaching methods and what the evidence says

| Method | Where used | Evidence type | What was found |
|---|---|---|---|
| Weekly oral code review interview, heavily weighted | Utah State CS1-CR, Fall 2025 | Quasi-experiment | More AI use, no exam drop, 90% more motivated to understand code |
| Oral defence and in-person exams | ACM survey (36 and 56 responses), ITiCSE (28) | Survey | Most common assessment change |
| Reveal AI code only after learner states reasoning (Lead-and-Reveal) | Kazemitabaar, IUI 2025 | Controlled experiment | Better calibration, no extra load |
| Trace and predict AI code before running it | Kazemitabaar, IUI 2025 | Controlled experiment | Balanced engagement |
| Ask the AI conceptual questions, generate then interrogate | Anthropic RCT 2026 | Correlational within RCT | Patterns linked to 65 to 86% quiz scores vs 24 to 39% |
| Submit transcripts plus reflection journals | Brown, DURA, ACM survey | Experience report | Valued; students resist writing reasoning down |
| Peer review, design critique, shared test suites (TestFest) | Brown, SIGCSE 2026 poster | Experience report, survey | Most valued part of Brown course; reviewing valued more than being reviewed |
| Use AI-generated code as debugging and review material | ACM survey | Survey | Reported practice, no outcome data |
| "+X" work: extend the codebase with AI, report what else you did | ACM approaches site | Experience report | No outcome data |
| Large open-ended projects with AI allowed | UCSD CS1-LLM, NUS-Google | Course evaluation, opinion | Exam outcomes held steady |
| Reverse-engineer specs from existing solutions | NUS-Google | Opinion | Untested |
| Spec-driven lifecycle with repo-local agent guidance | FHNW, Stanford CS146S | Experience report | Survey only |
| Senior plus junior directing agents together | Microsoft pilot | Opinion | No results yet |

---

## 8. Open questions and gaps

- Nearly all measured studies use chat assistants or Copilot autocompletion, not autonomous agents. The Anthropic RCT authors expect agents to hurt skill formation more, but this is untested.
- Agent courses (Brown, Stanford, UCR, UT Austin, FHNW) have no published learning outcomes yet.
- "Verification" is underspecified. The NUS-Google paper says neither workshop separated informal review from formal methods.
- No controlled data on company onboarding or bootcamp outcomes in the agent era.
- Oral interviews work but cost TA time. Scaling is unstudied.
- Equity: CS1-LLM found that existing gaps persisted; ACM educators report weaker students use AI more and gain less.

---

## 9. Implications for a tool that trains people while they build with agents

These are inferences from the sources above, not findings.

1. Before the agent writes code, ask the user to state the plan, the spec or the expected behaviour (Lead-and-Reveal, Koli "reasoning before coding", spec-driven courses).
2. After the agent writes code, ask the user to predict behaviour on an input, or to explain a chosen part, before accepting (Trace-and-Predict, CS1-CR interview).
3. When a bug appears, prompt the user to form a hypothesis before the agent is asked to fix it (Anthropic debugging gap, "iterative AI debugging" pattern).
4. Ask for the tests or acceptance checks that would show the change is right, and compare them to what the agent wrote (TestFest, verification gates).
5. Ask a short "why this design" question on structural changes (Brown extensibility findings, oral defence).
6. Show the user how often they accepted code without reading it, to counter the perception gap (METR, Koli self-report mismatch).
7. Keep a light journal of decisions and AI use (Brown, DURA), but expect low uptake unless it is short.

---

## Sources

- ACM Task Force on Generative AI and Programming Assessment, final report, Feb 2026: https://acm-education-genai-task-force.github.io/ACM_Taskforce_GenAI_Report_16Feb26.pdf
- ACM task force shared approaches: https://acm-education-genai-task-force.github.io/approaches.html
- CS2023 announcement: https://www.acm.org/articles/bulletins/2024/june/cs2023-curricular-guidelines
- NUS-Google white paper, arXiv 2606.07545: https://arxiv.org/abs/2606.07545
- Bouvier et al., The Rest of the Robots, ITiCSE-WGR 2025: https://doi.org/10.1145/3760545.3783970 and https://cronfa.swansea.ac.uk/Record/cronfa71419
- Russinovich and Hanselman coverage: https://www.theregister.com/2026/02/23/microsoft_ai_entry_level_russinovich_hanselman/
- Brown Agentic Studio news: https://www.brown.edu/news/2026-06-11/agentic-studio-ai-programming
- Brown Agentic Studio visitors page: https://cs.brown.edu/courses/csci1970kf/agentic-spr-2026/visitors.html
- Stanford CS146S: https://themodernsoftware.dev and https://bulletin.stanford.edu/courses/2274401
- CS146S assignments summary (secondary): https://courses-dn9.pages.dev/modern-software-dev-assignments/index.html
- UC Riverside CS 180 Spring 2026: https://www.cs.ucr.edu/~qzhang/cs180-spring2026.html
- UT Austin CS 378: https://www.cs.utexas.edu/~witchel/378AC/
- FHNW AI-SDLC, arXiv 2609.24348: https://arxiv.org/abs/2609.24348
- ASE-26, arXiv 2606.01152: https://arxiv.org/abs/2606.01152
- CS 1.5, arXiv 2604.16365: https://arxiv.org/abs/2604.16365
- DURA, arXiv 2606.30908: https://arxiv.org/abs/2606.30908
- Anthropic, AI assistance and coding skills, Jan 2026: https://www.anthropic.com/research/AI-assistance-coding-skills and https://arxiv.org/abs/2601.20245
- Hak et al., pseudo-apprenticeship, Koli Calling 2025: https://arxiv.org/abs/2510.04986
- Shihab et al., Copilot brownfield, ICER 2025: https://arxiv.org/abs/2506.10051
- Prather et al., The Widening Gap, ICER 2024: https://arxiv.org/abs/2405.17739
- METR 2025 developer RCT: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ and https://arxiv.org/abs/2507.09089
- Vadaparty et al., Evaluating CS1-LLM: https://arxiv.org/abs/2510.18806
- Fowles et al., CS1-CR: https://arxiv.org/abs/2605.21374
- Du, Pei, Yan, SIGCSE 2026 poster: https://sigcse2026.sigcse.org/details/sigcse-ts-2026-posters/49/Learning-as-a-Reviewer-but-not-a-Reviewee-Understanding-Students-Perceptions-of-Pee
- Kazemitabaar et al., IUI 2025: https://arxiv.org/abs/2410.08922
- Anthropic Education Report, Apr 2025: https://www.anthropic.com/news/anthropic-education-report-how-university-students-use-claude
