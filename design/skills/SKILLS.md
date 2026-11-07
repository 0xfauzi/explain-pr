# Skills map: lasting engineering skills

This map lists engineering skills that would still matter if the tools changed next year. Each one made someone a better engineer before coding agents existed. The test for every skill is simple: its definition must make sense without the word "agent". Agents appear only in two places: the evidence for why a skill matters now, and the moments in a build where the tool can ask a person to practise it.

The earlier version of this map was built around operating AI tools. The founder's point was that this is too specific to AI. A second review found the same problem in the framing, so this revision also moves agent-only reasoning out of the definitions.

It merges six research reports in `design/skills/research/`: empirical, agentic-2025, expertise, practitioners, education and durable. Two reviews of the previous draft were applied. The closing section lists what was rejected and why.

## How to read this map

- Each claim carries a tag.
  - **[Study]**: a controlled experiment, quasi-experiment, or structured observation or interview study.
  - **[Data]**: usage logs, telemetry, repository mining or large surveys.
  - **[Incident]**: a documented real-world failure. It shows a failure can happen, not how often.
  - **[Opinion]**: practitioners, tool makers, educators, position papers, and this map's own reasoning.
  - **(vendor)**: the source sells AI tools or AI review tools, or its authors work for such a company.
  - **(model-rated)**: a language model, not a person, judged expertise or outcome.
  - **Supporting**: the source is older than 2025, or studies chat assistants or autocomplete rather than agents.
  - **Secondary**: the figure comes from coverage of a report, not from the report itself.
- **Strength** has two parts where the evidence allows it.
  - *Problem*: how well the evidence shows the risk is real. For example, that unchecked work fails.
  - *Skill*: how well the evidence shows the human skill reduces that risk.
  - Strong: at least one controlled study or large dataset, and sources agree. Moderate: consistent observational data or broad expert agreement, no controlled test. Weak: mostly opinion.
- **Order** is strength of evidence times importance. Importance is this map's opinion of how often the skill decides whether a change is right in an ordinary build. Whether a skill weakens under heavy delegation is noted, but it does not set the order.
- No study yet shows that practising any of these skills while building leads to better outcomes. Every practice moment below is a design hypothesis.

## The finding behind the whole map

**Evidence.** The human share of the work has moved from writing code to deciding what to build and checking what was built. Across about 400,000 Claude Code sessions, users made about 70% of planning decisions and about 20% of execution decisions [Data, vendor, model-rated] (https://www.anthropic.com/research/claude-code-expertise). Sessions rated novice reached verified success about 15% of the time, against 28% to 33% for intermediate users and above (same source). This is correlational.

**Evidence.** Delegating the work can weaken the understanding needed to check it. In a study of 54 students, those using an agent that edits code directly understood their code less than students using a chatbot (p<0.01). The agent group was more accurate on the first task, but that lead went away when they had to extend the code without AI [Study] (https://arxiv.org/abs/2607.26375). Supporting: in a randomized trial with a chat-style assistant (n=52), the AI group scored 50% on a comprehension quiz against 67% for hand coders, with the largest gap on debugging [Study, vendor] (https://arxiv.org/abs/2601.20245). Both authors of that trial work at Anthropic.

**Opinion.** Anthropic's interviews with its own engineers call this the "paradox of supervision" [Opinion, interviews, vendor] (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).

**Unknown.** Both studies measured learning right after a task, in students. No study has measured skill loss in working engineers over months.

## The map

| # | Skill | Strength (problem / skill) | Weakens under heavy delegation? |
|---|---|---|---|
| 1 | Verification: checking work and claims against evidence | Strong / Weak | Review effort falls over time, measured once |
| 2 | Reading and understanding code you did not write | Strong for learners / Weak for working engineers | Yes for learners, measured |
| 3 | Debugging and diagnosis | Moderate / Moderate | Yes in one supporting study |
| 4 | Security and risk judgment | Strong / Weak | Likely, not measured directly |
| 5 | Framing the problem and writing the brief | Moderate / Weak | Likely, not measured |
| 6 | Delegating and supervising work | Moderate / Weak | Unknown |
| 7 | Breaking work into small, reversible changes | Moderate / Weak | Likely, not measured |
| 8 | Operating software in production | Moderate / Weak | Unknown |
| 9 | Design, architecture and data modelling | Moderate / Weak | Possibly, not measured |
| 10 | Calibrating your own judgment | Moderate / Weak | Unknown |
| 11 | Product judgment | Weak / Weak | Unknown |

"Weak" in the skill column is common because no study has tested whether people with more of a skill get better outcomes with agents. The reason is missing studies, not evidence against the skill.

---

### 1. Verification: checking work and claims against evidence

**Definition.** Deciding what "working" means in a form you can check, then comparing what was claimed with what the evidence shows. The claim can come from a colleague, a tool, a test suite or your own memory. The evidence is a test that fails before the change and passes after, a run, a log or a measurement.

**Why it matters more now.** When producing code is cheap, more of the cost sits in checking it. Generated work is often plausible but wrong, and reports of what was done can be wrong too.

**Evidence.**
- Maintainers reviewed 296 AI pull requests that passed SWE-bench tests. About half would not have been merged, for reasons including code quality and breaking other code. Maintainers could not run CI, were told to ignore testing requirements, and scores were normalised against human patches, of which they would merge about 68% [Study] (https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/). This shows that passing tests is not the same as acceptable work. It does not by itself show a failure of human checking.
- In 33,596 agent-written pull requests, each extra failing CI check cut the odds of merging by about 15%. In a hand-labelled sample of 600 rejected pull requests (562 still accessible), 99 failed CI or tests [Data] (https://arxiv.org/abs/2601.15195).
- Of merged Claude Code pull requests, 45.1% needed revision, and 47.7% of those revisions were bug fixes [Data] (https://arxiv.org/abs/2509.14745).
- AI co-authored pull requests had about 1.7 times more issues (10.83 against 6.45 per pull request). The sample was 470 open-source pull requests, and AI authorship was inferred from signals in the pull request [Data, vendor] (https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report).
- The Replit agent gave misleading accounts of what it had done, including fabricated data and a false claim that rollback was impossible [Incident] (https://incidentdatabase.ai/entities/replit).
- 9 of 13 observed professionals reviewed every agent change using diffs, tests, runs or debuggers [Study] (https://arxiv.org/abs/2512.14012). This is what experienced people do. It does not show that it improves outcomes.
- Supporting: in a CHI 2025 survey of 319 knowledge workers, higher confidence in generative AI was associated with less critical thinking [Data, survey, self-report, vendor] (https://www.microsoft.com/en-us/research/?p=1135061). 66% of developers report frustration with AI output that is "almost right" [Data, survey] (https://survey.stackoverflow.co/2025/ai). A two-wave survey found engineers' time shifted from creating code to verifying it (n=95, mostly chat tools) [Data] (https://arxiv.org/abs/2605.23135). In an ACM survey (763 responses), 17 of 243 instructors who described course changes said they now put more weight on debugging, testing and verifying AI code [Data, survey] (https://acm-education-genai-task-force.github.io/ACM_Taskforce_GenAI_Report_16Feb26.pdf).
- Opinion: "Your job is to deliver code you have proven to work" (Simon Willison) (https://simonwillison.net/2025/Dec/18/code-proven-to-work/).

**Strength.** Problem: strong. Several large datasets agree that unchecked generated work often fails. Skill: weak. How well people catch defects, and whether better checkers get better outcomes, is not measured.

**Does it weaken?** Measured once. In open-source projects, reviewer approval of agent pull requests rose from 30.1% to 36.8% over time while comments per review fell 22% and words per review fell 28% [Data] (https://arxiv.org/abs/2606.22721). Supporting: in Claude.ai chats that produced an artifact, fact-checking inside the chat was less common (5.5% against 9.2%). This is chat, not agents, one week of data, and users may have checked elsewhere [Data, vendor] (https://academy.claude.com/tutorials/the-ai-fluency-index).

**Practice moments.**
- *Before a task starts.* The person writes the one check that would prove it worked. Feedback: the tool runs that check at the end and shows the result.
- *When a change is reported done.* Before reading the summary, the person names the evidence that it works and predicts whether a key test would fail if the change were reverted. Feedback: the tool reverts the change, runs the test and shows whether it fails.
- *When tests are added or edited.* The person names one input the tests miss. Feedback: the tool runs that input.

---

### 2. Reading and understanding code you did not write

**Definition.** Reading code until you can say what it does, what calls it and what would break if it changed.

**Why it matters more now.** More of the code an engineer owns was written by someone or something else. Without understanding it, they cannot verify, debug or extend it. How a running system behaves across services belongs to skill 8.

**Evidence.**
- Students using an agent that edits code directly understood their code less than chatbot users (n=54, p<0.01). Accepting edits without review went with weaker comprehension [Study] (https://arxiv.org/abs/2607.26375).
- In 7 YouTube live streams of vibe coding, low-reliance coders read the diffs. One high-reliance coder never opened a file in about five hours [Study, observational] (https://arxiv.org/abs/2512.22418).
- Users found agent behaviour hard to understand [Study] (https://arxiv.org/abs/2507.08149).
- 65 of 99 surveyed professionals named their existing expertise as critical to working with agents. Observers noted code comprehension and debugging skill in 6 of 13 observed participants [Study] (https://arxiv.org/abs/2512.14012).
- Supporting: in the chat-assistant RCT, people who generated code and then asked questions about it scored about 86%. People who fully delegated scored about 39%. Subgroups had 2 to 7 people [Study, vendor] (https://arxiv.org/abs/2601.20245). Developers spent about 58% of their time on comprehension in a field study (Xia et al., TSE 2018) [Study, supporting] (https://xin-xia.github.io/publication/TSE17.pdf).
- Opinion: "cognitive debt", meaning code no one on the team can explain (Storey, https://arxiv.org/abs/2603.22106; Willison, https://simonwillison.net/2026/Feb/15/cognitive-debt). At Brown's agent course, a majority of students worried they did not understand their own codebase [Opinion, experience report] (https://cs.brown.edu/courses/csci1970kf/agentic-spr-2026/visitors.html).

**Strength.** Problem: strong for learners, from one agent study and one supporting vendor RCT, both on students. Skill: weak for working engineers. Their evidence is observation and opinion.

**Does it weaken?** Yes for learners, measured right after a task. How a person uses the tool matters: asking for explanations kept learning, full delegation did not (supporting RCT). Agent tools lean toward doing, not explaining: 79% of Claude Code conversations were classed as automation against 49% on Claude.ai [Data, vendor] (https://www.anthropic.com/research/impact-software-development).

**Practice moments.**
- *Before running unfamiliar code.* The person predicts what it will output or do. Feedback: the run. Supporting: in a study of 82 novices, asking learners to explain their own reasoning before seeing the AI's code (Lead-and-Reveal) gave the best match between perceived and actual ability, and Trace-and-Predict also balanced engagement and learning [Study, novices, chat-style AI] (https://arxiv.org/abs/2410.08922).
- *Before approving a diff.* The person names one caller or one input that the change affects. Feedback: the tool checks the answer against the call graph or runs the input.

---

### 3. Debugging and diagnosis

**Definition.** Finding the real cause of a failure by forming a hypothesis, running an experiment that tests it and narrowing down, rather than trying fixes until the symptom goes away.

**Why it matters more now.** Someone has to find the cause when a generated fix fails, loops or hides a symptom.

**Evidence.**
- In troubled sessions, users rated novice reached verified success 4% of the time against 15% for experts, and abandoned 19% of sessions against 5% to 7% [Data, vendor, model-rated] (https://www.anthropic.com/research/claude-code-expertise).
- In the vibe-coding live streams, a high-reliance coder pasted raw errors to the agent in 43 of 79 prompts, against 5 of 54 for a low-reliance coder [Study, observational] (https://arxiv.org/abs/2512.22418).
- Supporting: in the chat-assistant RCT, debugging showed the largest gap, and handing each error back to the AI scored about 24%, the lowest pattern [Study, vendor] (https://arxiv.org/abs/2601.20245). 45.2% of developers say debugging AI code takes longer [Data, survey] (https://survey.stackoverflow.co/2025/ai). In a 2025 student study, no student used a debugger [Study, supporting] (https://arxiv.org/abs/2510.04986).
- Opinion: an agent "fixed" a race condition by adding a sleep (Russinovich and Hanselman) (https://www.theregister.com/2026/02/23/microsoft_ai_entry_level_russinovich_hanselman/).

**Strength.** Problem: moderate. Skill: moderate. The two strongest sources are both vendor sources: a model-rated dataset and an RCT with a chat assistant. They agree with one small observational study.

**Does it weaken?** In the supporting RCT, AI users hit fewer errors during the task and were worse at diagnosis afterwards. Not measured in working engineers.

**Practice moments.**
- *When a test fails or an error appears.* Before any fix is tried, the person writes a one-line hypothesis about the cause. Feedback: once the cause is found, the tool shows the hypothesis next to it. Over time it shows how often the person's hypotheses were right.
- *After two failed fix attempts.* The person runs one experiment of their own: a log line, a smaller input or a bisect. Feedback: the experiment's result.

---

### 4. Security and risk judgment

**Definition.** Naming the trust boundary in a change and the step that cannot be undone, then limiting the damage: least privilege, separate environments, backups and a way back. This is the teachable core. Security as a whole field is too wide to be one skill.

**Why it matters more now.** Generated code often works and is insecure. Tools that act on a system run commands, install packages and touch data. Software is built faster by people who may lack a security background.

**Evidence.**
- 45% of code samples from more than 100 language models failed security tests, and models failed to defend against cross-site scripting in 86% of relevant cases. These were code snippets, not agent runs [Data, vendor benchmark] (https://www.veracode.com/genai-code-security-report).
- Security issues were up to 2.74 times more common in AI co-authored pull requests (470 pull requests, AI authorship inferred) [Data, vendor] (https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report).
- The Replit agent deleted a production database during a code freeze it had been told about [Incident] (https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/). Malware in the Nx package ran Claude, Gemini and Amazon Q command-line tools with the flags `--dangerously-skip-permissions`, `--yolo` and `--trust-all-tools` [Incident] (https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware). Text injected into a repository could switch off Copilot's approvals (CVE-2025-53773) [Incident] (https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection).
- 5 surveyed professionals called security-critical code unsuitable for agents, against 2 who called it suitable. These are open-ended comments, not votes [Study] (https://arxiv.org/abs/2512.14012). An Anthropic engineer caught a solution that was "really smart in the dangerous way" [Opinion, interview, vendor] (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).
- Supporting: models recommend packages that do not exist, averaging 5.2% of the time for commercial models and 21.7% for open-source models, and 43% of those names came back on all 10 reruns [Study] (https://arxiv.org/abs/2406.10279). People with an AI assistant wrote less secure code on 4 of 5 tasks and were more confident it was secure [Study, 2023] (https://arxiv.org/abs/2211.03622).

**Strength.** Problem: strong (vendor data, incidents, supporting study). Skill: weak. No study measures how often reviewers find these flaws.

**Does it weaken?** Likely. The supporting 2023 study found overconfidence rose with trust in the assistant. Falling review effort (skill 1) suggests security checks thin out too. That link is this map's inference [Opinion].

**Practice moments.**
- *When a change touches authentication, input handling, secrets or personal data.* The person names the trust boundary and one input that could abuse it. Feedback: the tool sends that input in a test.
- *When a new dependency is added.* The person checks the package exists and is the intended one. Feedback: the registry lookup.
- *Before an irreversible step (a migration, a delete, a deploy).* The person states how to roll back. Feedback: the tool checks that the stated rollback exists, for example a down migration or a backup.

---

### 5. Framing the problem and writing the brief

**Definition.** Turning a vague need into a clear statement of the goal, the constraints, what is out of scope, who it is for and how you will know it is done. Then writing it as a brief that someone without your context could build from.

**Why it matters more now.** A builder who lacks your context fills gaps with plausible guesses. This was true of a new colleague or a contractor before it was true of an agent. Fast builders turn a badly framed problem into a lot of wrong work quickly.

**Evidence.**
- In the hand-labelled sample of 600 rejected agent pull requests, 24 were unwanted features, 19 incorrect and 15 incomplete implementations, and 7 had a wrong task description [Data] (https://arxiv.org/abs/2601.15195).
- Users kept about 70% of planning decisions. Precise framing went with higher verified success, but framing was also an input to the expertise rating, so this is partly circular [Data, vendor, model-rated] (https://www.anthropic.com/research/claude-code-expertise). 11 of 13 observed professionals controlled design through plans [Study] (https://arxiv.org/abs/2512.14012).
- Models struggle to tell when instructions are underspecified [Study, benchmark] (https://arxiv.org/abs/2502.13069). METR names implicit requirements as a likely cause of the 2025 slowdown [Study] (https://arxiv.org/abs/2507.09089).
- Opinion: specification and verification are the most durable skills (NUS-Google white paper) (https://arxiv.org/abs/2606.07545). Counterpoint: heavy specs are overkill for small changes (Böckeler) (https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html).

**Strength.** Problem: moderate, from consistent observational data. Skill: weak. No controlled test that clearer framing improves outcomes.

**Does it weaken?** Likely, not measured. A vague request still produces something plausible, so the framing step gets skipped [Opinion].

**Practice moments.**
- *Before a non-trivial task.* The person writes the goal, one non-goal and the acceptance check. Feedback: after the run, the tool shows what was built next to the brief and lists what the builder had to guess, so the person sees which gaps in the brief caused rework.

---

### 6. Delegating and supervising work

**Definition.** Deciding what to hand off, in what size, with what checkpoints, and how closely to check the result, given the stakes and how easy the result is to check. The same judgment applies to a junior engineer, a contractor or an agent.

**Why it matters more now.** More work is handed off, and handing off badly costs more when the builder is fast.

**Evidence.**
- Anthropic engineers reported fully delegating only 0% to 20% of their work, mostly tasks that are easy to check and low-stakes [Data, self-report, vendor] (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).
- Observed professionals ran a median of about 1.8 steps per prompt, and those with plans of more than 70 steps ran at most 6 at once. "One-shotting without verification" was mentioned as unsuitable by 23 respondents and as suitable by 5 [Study] (https://arxiv.org/abs/2512.14012).
- Opinion: the same review-depth judgment is what a lead uses for a colleague's work.

**Strength.** Problem: moderate, from self-report and one observation study. Skill: weak. No study tests whether better delegation choices improve outcomes.

**Does it weaken?** Unknown.

**Practice moments.**
- *At the start of a task.* The person rates the stakes and how easy the result will be to check, and picks a review depth. Feedback: when later tests, review or rework show problems, the tool shows them next to the rating. This is feasible within a session or a pull request. Linking it to production defects is probably not.

---

### 7. Breaking work into small, reversible changes

**Definition.** Splitting a large goal into steps that are each small enough to understand, check and undo on their own.

**Why it matters more now.** Large changes are harder to check and are rejected more often. When a builder produces a large change as easily as a small one, size stops feeling expensive until review.

**Evidence.**
- Unmerged agent pull requests were larger and touched more files, and maintainers asked for "small, focused" changes [Data] (https://arxiv.org/abs/2601.15195). In a separate study, size was one of the few stated reasons for rejecting Claude Code pull requests (3 of 92 rejections) [Data] (https://arxiv.org/abs/2509.14745).
- Pull request size rose 154% on high-adoption teams [Data, vendor, secondary] (https://www.faros.ai/blog/ai-productivity-paradox-report-2025).
- In the vibe-coding live streams, undo, version control, small changes, automated tests and linters were all used as safeguards against unpredictable agent behaviour. The paper does not rank them [Study, observational, 7 streams] (https://arxiv.org/abs/2512.22418).
- Supporting: DORA lists working in small batches as a capability that shapes AI's effect [Data, survey, correlational] (https://cloud.google.com/blog/products/ai-machine-learning/introducing-doras-inaugural-ai-capabilities-model).

**Strength.** Problem: moderate. Several datasets agree. Skill: weak. No controlled test.

**Does it weaken?** Likely, not measured [Opinion].

**Practice moments.**
- *When a planned change grows past a size threshold.* The person names where it could be split. Feedback: the tool shows how review time and rework compared for the person's past large and small changes.

---

### 8. Operating software in production

**Definition.** Knowing how a running system behaves and keeping it safe to change: observability, safe rollout, rollback and learning from incidents.

**Why it matters more now.** Faster change means more changes reach production, and each one can break something that tests did not cover.

**Evidence.**
- DORA 2024 estimated a 7.2% fall in delivery stability as AI adoption rose [Data, survey, correlational] (https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report). Coverage of the report gives this as the estimate for each 25% rise in adoption [Data, secondary] (https://redmonk.com/rstephens/2024/11/26/dora2024/). The report PDF was not checked.
- DORA 2025 found AI adoption associated with higher throughput and also higher instability: "AI adoption not only fails to fix instability, it is currently associated with increasing instability" [Data, survey, correlational, secondary] (https://redmonk.com/rstephens/2025/12/18/dora2025/).
- The Replit database deletion shows what happens without separation of environments and a working rollback [Incident] (https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/).

**Strength.** Problem: moderate, from correlational survey data. Skill: weak. No study tests whether operations skill reduces this instability.

**Does it weaken?** Unknown.

**Practice moments.**
- *Before merging a change that reaches users.* The person names the signal that would show it is broken and how to roll it back. Feedback: the tool checks that the signal exists (a metric, log or alert) and that the rollback path is real.

---

### 9. Design, architecture and data modelling

**Definition.** Deciding whether a new module, abstraction, dependency or schema is justified, naming the main cost of the options, and recording why. For data: stating the invariants and how existing data migrates. This is the teachable core. Architecture as a whole is too wide to be one skill.

**Why it matters more now.** Generated changes are made one at a time and make structural choices silently. Each can be fine on its own while the codebase drifts. Code is cheap to regenerate. A schema holding real data is not.

**Evidence.**
- In about 806 repositories, static analysis warnings rose about 30% and code complexity about 41% after Cursor adoption, and the debt later slowed development [Study, quasi-experiment] (https://arxiv.org/abs/2511.04427).
- 50 of 99 surveyed professionals drive architecture themselves. Architecture was mentioned as suitable for agents by 13 respondents and as unsuitable by 23 [Study] (https://arxiv.org/abs/2512.14012). In a manual check of the 15 agent pull requests with the most review comments, friction came from missing architectural context [Data, 15 PRs inspected] (https://arxiv.org/abs/2602.23905).
- Supporting: maintainability as a primary concern rose from 3% to 19% [Data, survey] (https://arxiv.org/abs/2605.23135). DORA 2025 calls AI an amplifier: "It magnifies the strengths of high-performing organizations and the dysfunctions of struggling ones" [Data, survey, correlational] (https://research.google/pubs/dora-2025-state-of-ai-assisted-software-development-report/).
- Opinion: persona prompts "didn't change the fundamental structural decisions" (Kent Beck) (https://newsletter.kentbeck.com/p/taming-the-genie-like-kent-beck). One student in Brown's course described agent code as "messy and convoluted" [Opinion, student quote] (https://www.brown.edu/news/2026-06-11/agentic-studio-ai-programming).

**Strength.** Problem: moderate. One quasi-experiment on code health plus surveys. Skill: weak. Whether human design judgment prevents the drift is not measured. Data modelling rests on opinion only.

**Does it weaken?** Possibly, not measured. People accept the default structure without making a decision [Opinion].

**Practice moments.**
- *When a change adds a new module, dependency or a second way of doing something already solved.* The person accepts or rejects it and writes one line of why. Feedback: the tool shows the existing code that already does the same thing, if any.
- *When a change alters a schema.* The person states the invariants and how existing rows migrate. Feedback: the tool runs the migration on a copy of real or sample data and checks the stated invariants.

---

### 10. Calibrating your own judgment

**Definition.** Knowing how far to trust your own sense of speed, quality and understanding, by checking it against what actually happened.

**Why it matters more now.** Generation is fast and vivid. Review, rework and later bugs are spread out and easy to miss.

**Evidence.**
- Experienced developers forecast a 24% speedup, believed afterwards they had been 20% faster, and were measured 19% slower [Study, RCT] (https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/). The 2026 follow-up was inconclusive because 30% to 50% of developers skipped tasks they did not want to do without AI [Study] (https://metr.org/blog/2026-02-24-uplift-update/).
- More pull requests merged, but the source found "no significant correlation between AI adoption and improvements at the company level", and review time rose 91% [Data, vendor, secondary] (https://www.faros.ai/blog/ai-productivity-paradox-report-2025).
- Supporting: Lead-and-Reveal gave the best match between perceived and actual ability in novices [Study] (https://arxiv.org/abs/2410.08922).

**Strength.** Problem: moderate. One strong RCT on the perception gap, but it used chat and editor tools, not autonomous agents, and the follow-up was inconclusive. Skill: weak. No study tests whether calibration feedback improves outcomes.

**Does it weaken?** Not measured directly. Review habituation (skill 1) suggests trust grows faster than evidence, but that study measured review of other people's work, not judgment of one's own. Linking the two is this map's inference [Opinion].

**Practice moments.**
- *At the end of a session.* The person estimates the time saved. Feedback: the tool shows logged time spent waiting, reviewing and reworking next to the estimate.
- *Before reviewing a change.* The person rates confidence that it is correct. Feedback: what tests and review found in the same session. Tying ratings to production outcomes needs many paired cases and slow, sparse data, so whether that works is unknown.

---

### 11. Product judgment

**Definition.** Deciding what is worth building, and noticing when a correct change is the wrong thing to ship.

**Why it matters more now.** When building is cheap, choosing what to build is a larger share of the value [Opinion].

**Evidence.**
- In one study of 92 rejected Claude Code pull requests, 64.1% gave no reason. Where a reason was given, project context such as a preferred alternative solution (12.0%) was more common than technical flaws (4.4%) [Data] (https://arxiv.org/abs/2509.14745). Overall acceptance was 83.8% against 91.0% for human pull requests (same source).
- In a separate sample of 600 rejected agent pull requests, the largest group was left without meaningful review (228), then duplicates of existing work (142), then code-level failures (133) [Data] (https://arxiv.org/abs/2601.15195).
- Business logic was mentioned as unsuitable for agents by 15 respondents and as suitable by 2. Legacy integration was mentioned as unsuitable by 17 and suitable by 3 [Study] (https://arxiv.org/abs/2512.14012).
- DORA found that without a user focus, "AI adoption can have a negative impact on team performance" [Data, survey, correlational] (https://cloud.google.com/blog/products/ai-machine-learning/introducing-doras-inaugural-ai-capabilities-model).

**Strength.** Problem: weak to moderate. The rejection data shows misfit with the project matters, but most rejections gave no reason. Skill: weak, opinion only.

**Does it weaken?** Unknown.

**Practice moments.**
- *Before a feature task.* The person states who the change is for and what would show it helped. Feedback: only possible where the product has usage data or user feedback the tool can read. Otherwise this moment has no feedback and should not be used.

---

## Knowledge each skill depends on

These are not separate skills. They are the knowledge a person draws on to use the skills above.

- **Fundamentals** (concurrency, data structures, complexity, how networks and databases behave). Skills 1, 3, 4 and 9. They let a person spot a plausible mistake, such as a sleep that hides a race condition [Opinion] (https://www.theregister.com/2026/02/23/microsoft_ai_entry_level_russinovich_hanselman/). Both NUS-Google workshops stressed "the enduring importance of core CS theory" [Opinion] (https://arxiv.org/abs/2606.07545).
- **Test design techniques** (boundaries, failure cases, what a test proves). Skill 1.
- **Debugging tools** (debugger, logs, bisection). Skill 3.
- **Version control** (small commits, revert, branches). Skill 7.
- **Secure coding basics** (input validation, access control, secret handling). Skill 4.
- **Domain knowledge** (users, business rules, project constraints). Skills 5 and 11. It is learned by exposure: talking to users, reading tickets, owning a feature. A prompt during a build cannot supply it. The previous draft listed it as a skill. In the Anthropic data, software-occupation users were only slightly ahead of others (34% against 29% verified success), which suggests expertise is tied to the task [Data, vendor, model-rated] (https://www.anthropic.com/research/claude-code-expertise).

Writing code from scratch matters less for its own sake. It still matters as practice: the supporting RCT suggests that getting stuck and working through it is part of how understanding forms [Study, vendor].

## Claimed skills with weak support

- **Technical communication** (pull request descriptions, design docs, explaining decisions). Broad expert agreement and one supporting classroom study: when students had to explain their code weekly, AI use rose (pasted characters from 61% to 68%) with no drop in exam scores (n=96) [Study, supporting] (https://arxiv.org/abs/2605.21374). No agent data shows it changes outcomes. It has a cheap practice moment with feedback: the person writes the pull request description, and the tool lists what the diff does that the description does not mention.
- **Managing several agents at once.** More than 10% of Codex users run three or more agents in a week [Data, vendor] (https://arxiv.org/abs/2606.26959). It is a tool skill. The lasting part is skill 6.

**Tool-operation skills.** Prompting, context files, permission settings, hooks and steering a run are useful today. They are left out because they change with each tool release, and most of their value comes from the skills above. A good permission setting is risk judgment (skill 4). A good context file is a brief (skill 5) plus domain knowledge. Students at the NUS-Google workshop said prompting's long-term relevance is uncertain [Opinion] (https://arxiv.org/abs/2606.07545).

## Rules for the practice moments

These come from learning research that is mostly older than 2023 or from classrooms. It supports the design. It does not prove the design works for engineers at work.

- **Every moment needs feedback the tool can check.** Generating an answer helps memory: a meta-analysis of 86 studies found an effect of about d=0.40 (Bertsch et al. 2007) [Study, older] (https://pubmed.ncbi.nlm.nih.gov/17645161/). That work is about recall, not judgment. A moment whose answer nobody checks is likely to become a box the person ticks [Opinion]. The moments above were rewritten so each has a feedback source. Where none exists, the moment says so.
- **Build the tool around the moments with the clearest feedback first:** the revert test (skill 1), predict before running (skill 2), hypothesis before fix (skill 3), and brief against result (skill 5).
- **Ration and vary the prompts.** People paid less attention to security warnings they saw repeatedly over a five-day lab study. In a three-week field study, warnings that changed appearance kept attention better (Vance et al., MIS Quarterly 2018) [Study, older] (https://misq.org/tuning-out-security-warnings-a-longitudinal-examination-of-habituation-through-fmri-eye-tracking-and-field-experiments.html). Coverage reports adherence of 76% for varied warnings against 55% for fixed ones [Secondary] (https://campustechnology.com/articles/2018/05/29/research-slight-changes-to-appearance-of-privacy-warnings-significantly-improves-attention.aspx). Prompt only where stakes or uncertainty are high.
- **Adapt to the person.** Guidance that helps novices can hurt more expert learners: the expertise reversal effect (Kalyuga 2007) [Study, review, older] (https://www.uky.edu/~gmswan3/EDC608/Kalyuga2007_Article_ExpertiseReversalEffectAndItsI.pdf). Prompts should fade as a person's answers prove reliable.
- **Prefer answers the tool can check over self-reports.** "Rate the stakes" is easy to answer and hard to fault.
- **Unknown:** whether practice inside one codebase carries over to other work. No study found tests this.

## What this means for a tool that trains people while they build

Delegating the work can weaken the skills needed to check it, so a training tool cannot simply watch. At a few natural pauses it should ask for a prediction, a hypothesis or a check before showing the answer, and then show the person what actually happened. The supporting studies suggest that order keeps learning, while full delegation and handing errors straight back do not [Study, students, partly vendor]. Prompts should be rare, varied, matched to the person's level, and tied to checkable feedback. None of this has been tested as an intervention, so the tool should measure whether it helps.

## Changes from the reviews, and what was rejected

Accepted: every citation correction in the first review; the split of old skill 8 into calibration (10) and delegation (6); production operations (8) as a numbered skill; product judgment (11) split from domain knowledge, which moved to the knowledge section; data modelling and its invariants moment in skill 9; narrowing skills 4 and 9 to a teachable core; the brief folded into skill 5; the problem and skill split of strength for every skill; feedback for every practice moment; the code-level section replaced by a knowledge section; the METR note reworded; the "2.15 times more commits per pull request" figure removed from skill 7, because more commits is not larger changes; vendor and model-rated tags on every use of the Anthropic studies. Skill 3 was lowered from strong to moderate, because its two main sources are both vendor sources.

Rejected:
- **"Checking a claim against evidence" as a separate skill.** It is the same act as verification, applied to a report instead of code. It was merged into skill 1, whose definition now covers both. Two skills would split one practice loop.
- **Dropping the "weakens" column from the table.** The reviewer was right that it should not set the order, and it no longer does. It stays as a note because it tells the tool where prompts are most needed.
- **The second review's statement that the 54-student study showed students "less able to extend the code".** The paper's Figure 4 shows no significant difference on the extension task (p=0.45 and p=0.69). The first review was right.
- **The g=0.45 effect size for metacognitive prompts (Guo 2022).** It was cited through a blog summary that could not be checked against the paper, so it was left out.
- **Using the 61.38% "no recorded review" figure as erosion evidence** (https://arxiv.org/abs/2605.02273). It covers review of any kind, agent pull requests were reviewed slightly more often than human ones in the same repositories, and the authors warn that no record does not mean no oversight. It was removed rather than reworded, because it does not bear on any skill here.
- **The Anthropic "design and planning rose from 1.0% to 9.9%" figure.** It shows the model doing more design work, not people framing problems better, so it was removed from skill 5.
