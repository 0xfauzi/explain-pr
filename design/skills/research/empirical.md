# Skills for building software with coding agents: the empirical evidence

Scope: what 2025 and 2026 studies of AI-assisted and agentic software development say about which skills erode, which matter more, and what separates people who get good results from agents.

Date of research: November 2026.

## How to read this report

- The user asked for evidence about a 2025+ phenomenon, not lessons borrowed from other fields. So this report uses only studies of software work with AI tools, almost all from 2025 and 2026.
- Older or adjacent work (2024 chat-era studies, general knowledge-work surveys, aviation or medicine automation research) is left out of the skill list. A short section at the end names what was excluded and why.
- Each claim is tagged:
  - **[Evidence: RCT]** randomized controlled trial.
  - **[Evidence: observational]** usage logs, repository mining, telemetry, quasi-experiments.
  - **[Evidence: survey/qualitative]** self-report, interviews, video analysis.
  - **[Opinion]** expert or author interpretation, not measured.
- Vendor research (Anthropic, OpenAI, GitHub, CodeRabbit, Veracode, Faros) is flagged as vendor research. It is often the only large-scale data, but the authors have an interest in the result.
- Numbers come from the cited source. Where a number came only from secondary coverage, that is said.

## Summary

1. Agents now do most execution, and people keep the planning. In about 400,000 Claude Code sessions, users made about 70% of planning decisions and about 20% of execution decisions [Evidence: observational, vendor] (https://www.anthropic.com/research/claude-code-expertise). The human job is shifting toward directing and checking.
2. The time people spend shifts from writing code to verifying it. A six-month longitudinal survey found a significant shift from creation tasks to verification tasks (review, testing, debugging) [Evidence: survey] (https://arxiv.org/html/2605.23135).
3. Expertise still predicts results. Novice-rated Claude Code sessions reached verified success in 15% of cases versus 28% to 33% for intermediate and above, and were abandoned far more often (19% versus 5% to 7%) [Evidence: observational, vendor] (https://www.anthropic.com/research/claude-code-expertise). Low-experience "vibe coders" on GitHub produced larger PRs with a 31% lower acceptance rate and 4.52 times more review comments [Evidence: observational] (https://arxiv.org/html/2602.23905v1).
4. Delegating everything while learning hurts learning. In an RCT, people learning a new library with AI scored 17% lower on a skills quiz, with the biggest gap in debugging. People who asked conceptual questions or asked for explanations kept their learning [Evidence: RCT] (https://arxiv.org/abs/2601.20245).
5. People misjudge their own speed with AI. In METR's 2025 RCT, experienced developers were 19% slower with AI but believed they were 20% faster [Evidence: RCT] (https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/). METR's late-2025 follow-up could not produce a reliable new estimate because of selection effects [Evidence: RCT with acknowledged bias] (https://metr.org/blog/2026-02-24-uplift-update/).
6. Quality and review are the bottleneck. Cursor adoption in open-source projects brought a short velocity spike and lasting increases in static analysis warnings (about 30%) and code complexity (about 41%) [Evidence: observational, quasi-experimental] (https://arxiv.org/abs/2511.04427).
7. Experienced professionals control agents tightly: they plan first, run agents in small steps, and review every change [Evidence: field observation and survey] (https://arxiv.org/html/2512.14012).

## Part 1: The studies

### 1.1 Shen and Tamkin 2026: How AI Impacts Skill Formation

- Source: https://arxiv.org/abs/2601.20245 (HTML: https://arxiv.org/html/2601.20245). Anthropic Fellows. Submitted 28 January 2026.
- Design: RCT. 52 participants (26 per group) learned Trio, a Python async library, with or without an AI assistant, then took a 27-point quiz. [Evidence: RCT]
- Results:
  - The AI group scored 4.15 points lower, about 17% (Cohen's d = 0.738, p = 0.010).
  - AI did not significantly reduce completion time.
  - Debugging questions showed the biggest gap between groups. Code reading showed the smallest.
  - Some AI participants spent up to 11 minutes composing queries.
- Six interaction patterns (24 of 25 AI participants classified):
  - Low scorers (about 24% to 39%): AI Delegation (n=4), Progressive AI Reliance (n=4), Iterative AI Debugging (n=4). Iterative AI Debugging means using AI to fix and check code with many queries, without building understanding.
  - High scorers (about 65% to 86%): Generation-Then-Comprehension (n=2), Hybrid Code-Explanation (n=3), Conceptual Inquiry (n=7).
  - Conceptual Inquiry participants asked only conceptual questions, hit many errors, fixed them themselves, and were the second fastest group.
- Limits: small subgroups (n=2 to 7). One library, one short session. Secondary coverage describes the tool as a chat assistant, not an autonomous agent. The direction of the result is likely to hold or strengthen with agents, but that is [Opinion], not measured.
- What it means for skills: learning a new area while delegating to AI costs understanding, and debugging is hit hardest. The way you use the tool matters more than whether you use it.

### 1.2 METR 2025 RCT and 2026 update

- Source: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ and paper https://arxiv.org/abs/2507.09089
- Design: 16 experienced open-source maintainers, 246 real issues in their own large repositories, randomized to AI-allowed or AI-disallowed. Tools were mainly Cursor Pro with Claude 3.5/3.7 Sonnet. [Evidence: RCT]
- Results:
  - Developers took 19% longer with AI allowed.
  - Before the study they forecast a 24% speedup. Afterwards they still believed AI had sped them up by 20%.
- 2026 update: https://metr.org/blog/2026-02-24-uplift-update/
  - Late-2025 estimates: original developers -18% time (CI -38% to +9%), new developers -4% (CI -15% to +9%). Neither is statistically conclusive.
  - 30% to 50% of developers said they skipped submitting some tasks they did not want to do without AI.
  - METR says the study now misses the most AI-optimistic developers and the highest-uplift tasks, so the estimate is likely a lower bound. METR now considers the design a poor proxy.
  - Time tracking was unreliable when developers worked on other things while agents ran.
- What it means for skills: self-assessment of AI's value is unreliable. The 2025 gap between perceived and measured speed is the strongest measured case. The 2026 update shows the speed picture is changing fast and is now hard to measure. It does not show the perception gap has closed.

### 1.3 Anthropic: Claude Code expertise study (2026)

- Source: https://www.anthropic.com/research/claude-code-expertise [Evidence: observational, vendor]
- Data: about 400,000 interactive Claude Code sessions from about 235,000 people, October 2025 to April 2026. Expertise and success were judged by a model reading transcripts. "Verified success" needs a hard signal such as a commit, PR, passing tests, or explicit user confirmation.
- How expertise was judged: how precisely the user frames directions, what they ask Claude to verify, and who corrects whom.
- Results:
  - Verified success: 15% for novice-rated sessions, 28% to 33% for intermediate and above.
  - Abandonment (failed with no code written): 19% for novices, 5% to 7% for others.
  - In troubled sessions, verified success rose from 4% for novices to 15% for experts.
  - Most of the gain is from novice to intermediate. The expert gap over intermediate is small.
  - Users made about 70% of planning decisions and about 20% of execution decisions.
  - Software occupations reached verified success in about 30% of sessions versus about 26% for other occupations. In code-producing sessions the ten largest occupations were all within seven points of software engineers.
  - Expertise is task-specific: a senior engineer asking a first Rust question counts as a beginner.
  - The authors write that "part of the value of expertise appears to be the ability to steer the agent." [Opinion, by the authors]
- Limits: model-judged labels; no view of whether code was used later; experts may take on harder problems.
- What it means for skills: the markers of expertise the classifier uses (precise framing, asking for verification, correcting the agent) are themselves the skills. Domain knowledge of the task matters about as much as a software job title.

### 1.4 Anthropic: How AI is transforming work at Anthropic (December 2025)

- Source: https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic [Evidence: survey of 132 engineers and researchers, 53 interviews, internal Claude Code usage data; vendor, and the subjects are the vendor's own staff]
- Usage data (February to August 2025):
  - Consecutive tool calls per transcript rose 116%, from 9.8 to 21.2.
  - Human turns per transcript fell 33%, from 6.2 to 4.1.
  - Design and planning rose from 1.0% to 9.9% of transcripts.
- Survey:
  - Self-reported share of work using Claude: 59%, up from 28%. Self-reported productivity gain: about 50%. These are self-reports.
  - More than half said they can "fully delegate" only 0% to 20% of their work.
  - People delegate tasks that are easy to verify, low-stakes, or repetitive. They keep "high-level thinking and design."
- Qualitative themes:
  - The "paradox of supervision": supervising Claude needs the coding skills that may atrophy from using Claude.
  - Worry about skill atrophy: "When producing output is so easy and fast, it gets harder and harder to actually take the time to learn something."
  - A security engineer caught a solution that was "really smart in the dangerous way."
  - Engineers report becoming more full-stack, working in areas they used to avoid.
- What it means for skills: the people who use agents most heavily name verification, design and judgment as what they keep, and name supervision skill as the thing at risk.

### 1.5 Anthropic Economic Index: software development (April 2025)

- Source: https://www.anthropic.com/research/impact-software-development [Evidence: observational, vendor]
- 79% of Claude Code conversations were classed as automation, versus 49% on Claude.ai.
- "Directive" use (hand over the task, minimal back-and-forth) was 43.8% on Claude Code versus 27.5% on Claude.ai. "Feedback loop" use was 35.8% versus 21.3%.
- All augmentation patterns, including "Learning", were much lower on Claude Code than on Claude.ai.
- What it means for skills: agentic tools by default push people toward automation and away from learning interactions. A tool that wants to train skill has to work against that default. [Opinion]

### 1.6 Anthropic AI Fluency Index (February 2026)

- Source: https://academy.claude.com/tutorials/the-ai-fluency-index (redirect from https://www.anthropic.com/research/AI-fluency-index) [Evidence: observational, vendor]
- Data: 9,830 Claude.ai conversations from one week in January 2026. This is general Claude.ai use, not only coding, so treat it as supporting evidence.
- Results:
  - Only 15.8% of conversations showed the user questioning Claude's reasoning, 8.7% checking facts, and 10.1% consulting the AI on approach before execution.
  - Iterative conversations showed questioning reasoning in 17.9% versus 3.2% for non-iterative ones.
  - When Claude produced an artifact (code, documents), users were less likely to check facts (5.5% versus 9.2%), question reasoning (13% versus 16.2%), or identify missing context (15.8% versus 21%).
- Limits: correlations only; behaviors outside the chat (running tests, reading code in an editor) are not visible.
- What it means for skills: polished output lowers scrutiny. That is directly relevant to agent-produced code.

### 1.7 OpenAI: The Shift to Agentic AI: Evidence from Codex (June 2026)

- Source: https://arxiv.org/abs/2606.26959 [Evidence: observational, vendor with academic coauthors]
- Results from the abstract:
  - Active users grew more than fivefold in the first half of 2026.
  - More than 10% of users manage three or more concurrent Codex agents at some point each week.
  - 26.6% of users use skills (shared instructions for complex workflows).
  - The share of individual users submitting at least one request estimated to take an experienced human more than eight hours rose nearly tenfold since the start of 2026.
- The authors describe work moving from executing tasks to orchestrating several agents at once. [Opinion, by the authors]
- What it means for skills: running several agents and writing reusable instructions are now common behaviors. No study found here measures how well people do this.

### 1.8 Professional developers don't vibe, they control (December 2025)

- Source: https://arxiv.org/abs/2512.14012 (HTML: https://arxiv.org/html/2512.14012). Huang, Reyna, Lerner, Xia, Hempel (UC San Diego). [Evidence: 13 field observations, 99-person survey]
- Observed control strategies:
  - 11 of 13 controlled design by writing plans, revising agent drafts, or editing plans. Some kept plans in files.
  - Median of 1.8 steps per prompt. Two participants with plans of over 70 steps never ran more than 6 at once.
  - 9 of 13 reviewed every agent change, using diffs, tests, UI checks or debuggers.
  - 12 observed and 43 surveyed participants said prompts need clear context and explicit instructions.
  - 18 surveyed and 3 observed participants used rules files to enforce project standards.
- Survey:
  - 50 respondents said they drive architecture and design themselves.
  - 65 surveyed and 11 observed participants said domain expertise was critical, including code comprehension, debugging, and turning product specs into plans.
  - Tasks seen as unsuitable for agents: complex tasks (3 suitable : 16 unsuitable), legacy integration (3:17), business logic needing domain knowledge (2:15), one-shotting code without verification (5:23), replacing human decisions (0:12). High-level architecture was split (13:23).
- Limits: small observation sample; survey skewed toward AI-positive developers; no novice control group.

### 1.9 Novice vibe coders create review overhead (MSR 2026)

- Source: https://arxiv.org/abs/2602.23905 (HTML: https://arxiv.org/html/2602.23905v1). Asdaque et al. [Evidence: observational, repository mining]
- Data: 22,953 AI-assisted PRs from 1,719 developers in the AIDev dataset, split by an experience score.
- Low-experience versus high-experience:
  - 2.15 times more commits per PR and 1.47 times more files changed.
  - 31% lower acceptance rate.
  - 5.16 times longer resolution time.
  - 4.52 times more review comments.
- Qualitative cause of friction: AI code that ignored build and CI constraints, and code that lacked project-specific architectural context.
- Limits: experience is measured by commits per account age, which is a rough proxy.
- What it means for skills: knowing the project's constraints and making small, reviewable changes are what experienced people do and novices do not.

### 1.10 Agentic PRs on GitHub

- On the Use of Agentic Coding: 567 Claude Code PRs across 157 projects. 83.8% accepted versus 91.0% for human PRs. Rejections were mostly about project context (other approaches preferred, PR size), not code defects. https://arxiv.org/abs/2509.14745 [Evidence: observational]
- AIDev dataset: 932,791 agent PRs from Codex, Devin, Copilot, Cursor and Claude Code up to 1 August 2025. https://arxiv.org/abs/2602.09185 [Evidence: dataset]
- Earlier AIDev preprint: agent PRs are accepted less often than human PRs, a "trust and utility gap", and are structurally simpler. https://arxiv.org/abs/2507.15003 [Evidence: observational]
  - Secondary coverage reports that accepted Codex PRs were reviewed in a median 0.3 hours versus 3.9 hours for human PRs, and that the authors suggest this may mean shallow review. I did not confirm this number in the primary text.
- What it means for skills: rejection is mostly about fit with the project, which points to project context and scoping more than code-writing skill. Very fast reviews of agent PRs raise the question of whether review is real. That is [Opinion] until measured.

### 1.11 Cursor adoption: speed now, complexity later (MSR 2026)

- Source: https://arxiv.org/abs/2511.04427. He, Miller, Agarwal, Kästner, Vasilescu (Carnegie Mellon). [Evidence: observational, staggered difference-in-differences against matched controls, about 806 repositories]
- Results:
  - Large increase in lines added in the first month after adoption. The gain faded after about two months.
  - Static analysis warnings rose about 30% and code complexity about 41%, and stayed up.
  - Accumulated warnings and complexity later reduced velocity.
- The authors conclude quality assurance is a major bottleneck. [Opinion, by the authors, grounded in the data]
- What it means for skills: someone has to own long-term code health. Agents do not do this by default.

### 1.12 Longitudinal study of professional engineers (ACM TOSEM 2026)

- Source: https://arxiv.org/abs/2605.23135 (HTML: https://arxiv.org/html/2605.23135). Vella and Blincoe (University of Auckland). [Evidence: survey, two waves six months apart, October 2024 and April 2025, 95 matched participants]
- Results:
  - 82% reported spending less time writing code by the second wave.
  - Perceived time moved from creation (design, writing, refactoring) to verification (review, testing, debugging). The shift was significant (r = 0.39, adjusted p = 0.006).
  - 84% reported productivity gains, while the share with a negative developer-experience rating rose from 14% to 27%. Flow declined most.
  - Maintainability as a primary concern rose from 3% to 19%.
  - The authors name a new category: "supervisory engineering work", meaning directing AI, evaluating its output, and correcting it.
- Limits: self-report; single-item measures. Skill data was collected but not reported.

### 1.13 Coding agents versus copilots (2025)

- Source: https://arxiv.org/abs/2507.08149 [Evidence: within-subjects user study, 20 students experienced with Copilot but new to agents, April to May 2025]
- Results:
  - The agent (OpenHands with Claude 3.7 Sonnet) improved task correctness by about 35 percentage points (p = 0.02).
  - Human time on correct solutions fell from 25.1 to 12.5 minutes.
  - Copilot was preferred for understanding outputs, though not significantly.
  - Users found agent changes hard to follow, felt less in control, and sometimes could not tell when work was done.
- What it means for skills: agents raise output for novices, but the cost is understanding what changed. Following and checking an agent's changes is a skill that has to be learned.

### 1.14 Vibe coding studies (2025)

- Building Software by Rolling the Dice: grounded theory of 20 vibe-coding videos (7 live sessions, about 16 hours, 254 prompts). https://arxiv.org/abs/2512.22418 [Evidence: qualitative]
  - Low-reliance coders were professionals with a background in the project's domain. They read diffs and code.
  - One high-reliance coder never opened a file in nearly five hours.
  - Copy-pasting error messages straight to the AI: 43 of 79 prompts for one high-reliance coder versus 5 of 54 for a low-reliance coder.
  - Coders anchored on the first output instead of seeking alternatives.
  - Debugging felt stochastic ("throwing a dice"). Coders coped with undo, version control, small changes, tests and linters.
  - Limits: public videos may be performative; small sample.
- Good Vibrations: interviews and posts, over 190,000 words. Trust moves people along a range from delegation to co-creation. Pain points and strategies cluster around communication, planning and abstraction, verification, and code quality. https://arxiv.org/abs/2509.12491 [Evidence: qualitative]
- Vibe coding: programming through conversation with AI: over 8 hours of video. Trust is built through repeated verification, not given up front. https://arxiv.org/abs/2506.23253 [Evidence: qualitative]

### 1.15 Context files for agents (2025 and 2026)

- 253 CLAUDE.md files from 242 repositories: shallow structure; build instructions most common. https://arxiv.org/abs/2509.14744 [Evidence: observational]
- 2,303 agent context files from 1,925 repositories across Claude Code, Codex and Copilot. https://arxiv.org/abs/2511.12884 [Evidence: observational]
- 2,923 repositories: context files dominate agent configuration; AGENTS.md is becoming a shared standard. https://arxiv.org/abs/2602.14690 [Evidence: observational]
- Impact of AGENTS.md on agent efficiency: https://arxiv.org/abs/2601.20404. I did not confirm its results.
- What it means for skills: people now write durable instructions for agents. These studies describe the practice but do not show which kinds of context improve outcomes.

### 1.16 Industry surveys and telemetry (2025)

- DORA 2025 State of AI-assisted Software Development: nearly 5,000 respondents. AI acts as an amplifier of existing strengths and dysfunctions. AI adoption now improves delivery throughput, but stability remains a concern. About 90% use AI at work. https://dora.dev/research/ai and https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf [Evidence: survey, Google]
  - Secondary coverage reports only 3% of respondents have "high trust" in AI output (https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025). Not checked in the primary PDF.
- Stack Overflow 2025 Developer Survey, via secondary coverage (https://www.infoworld.com/article/4031673/): 66% cite "AI solutions that are almost right, but not quite"; 45.2% say debugging AI code takes more time; 46% distrust AI accuracy. [Evidence: survey; numbers not checked against the primary page]
- Faros AI telemetry (10,000+ developers, 1,255 teams), via secondary coverage: about 91% longer PR review time on high-adoption teams, about 98% more PRs merged, no significant company-level improvement. [Evidence: vendor telemetry; primary report not accessed; correlation only]
- CodeRabbit State of AI vs Human Code Generation (December 2025): 470 open-source PRs; AI-coauthored PRs had about 1.7 times more issues, with logic and correctness the largest category. https://coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report [Evidence: vendor analysis, small sample, labeling assumptions]
- Veracode 2025 GenAI Code Security Report: over 100 models on 80 tasks; code introduced a security flaw in 45% of cases. https://www.veracode.com/genai-code-security-report [Evidence: vendor benchmark of model output, not of human-agent workflows]
- GitHub Octoverse 2025: 518.7 million PRs merged in the year (+29%). https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/ [Evidence: platform data, vendor]
  - Coverage of Octoverse 2026 reports agents initiated more than 40% of PRs in September 2026, up from 17% in March. I could not open the primary source, so treat this as unverified.

## Part 2: Skills, ranked by strength of evidence

Each skill lists: why it matters, evidence, strength, whether it erodes with agents, and a concrete moment during a build with an agent where a tool could train it.

Strength key:
- **Strong**: at least one RCT or large observational study plus consistent support from other studies.
- **Moderate**: several observational or qualitative studies agree, no RCT.
- **Weak**: early evidence, mostly description of practice, or mostly opinion.

### Skill 1. Verifying agent output against hard evidence

- Why: agents produce plausible code that is often almost right. The human job has shifted toward checking. Polished output reduces scrutiny.
- Evidence:
  - Verified success needs hard signals, and asking the agent to verify is one marker of expertise (https://www.anthropic.com/research/claude-code-expertise) [observational, vendor].
  - 9 of 13 professionals reviewed every agent change (https://arxiv.org/html/2512.14012) [qualitative].
  - Significant shift of time toward verification (https://arxiv.org/html/2605.23135) [survey].
  - Artifacts reduce fact checking and questioning (https://academy.claude.com/tutorials/the-ai-fluency-index) [observational, vendor].
  - AI-coauthored PRs carry more issues (CodeRabbit) and complexity rises after adoption (https://arxiv.org/abs/2511.04427) [observational].
- Strength: strong.
- Erodes: yes. The supervision paradox (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [survey and opinion].
- Train it when: the agent says "done". Before the user accepts, ask them to name what evidence shows it works (a test that failed before and passes now, a run, a screenshot), and to predict one way it could still be wrong.

### Skill 2. Debugging and reasoning about failure causes

- Why: debugging was the skill most damaged by AI use while learning. People who handed errors back to the AI without thinking learned least.
- Evidence:
  - Largest quiz gap was on debugging; "Iterative AI Debugging" was a low-scoring pattern (https://arxiv.org/html/2601.20245) [RCT].
  - High-reliance vibe coders pasted raw error messages to the AI far more often (https://arxiv.org/abs/2512.22418) [qualitative].
  - Debugging is the most common daily use at Anthropic (55%) (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [survey].
  - 45.2% say debugging AI code takes more time (Stack Overflow 2025, secondary) [survey].
- Strength: strong.
- Erodes: yes, measured in the RCT.
- Train it when: a test fails or an error appears. Before forwarding it to the agent, ask the user for their hypothesis of the cause. Then compare it with the agent's diagnosis.

### Skill 3. Building conceptual understanding while delegating (learning-mode use)

- Why: the same tool can preserve or destroy learning depending on how it is used. Asking for explanations and concepts kept quiz scores high at similar speed.
- Evidence:
  - Conceptual Inquiry, Hybrid Code-Explanation and Generation-Then-Comprehension scored about 65% to 86% versus 24% to 39% for delegation patterns (https://arxiv.org/html/2601.20245) [RCT, small subgroups].
  - Claude Code shows much less "Learning" interaction than Claude.ai (https://www.anthropic.com/research/impact-software-development) [observational].
  - Engineers say fast output makes it harder to take time to learn (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [survey].
- Strength: strong for the effect of interaction pattern on learning; the subgroup sizes are small.
- Erodes: yes, the default agent workflow is automation.
- Train it when: the agent first touches a library, API or part of the codebase the user has not used. Offer a short "explain the key idea" step, or ask the user to explain the change back before moving on.

### Skill 4. Planning and specifying before execution

- Why: users keep about 70% of planning decisions. Professionals write or edit plans before letting agents run.
- Evidence:
  - 11 of 13 observed professionals controlled design through plans (https://arxiv.org/html/2512.14012) [qualitative].
  - Precise framing of directions is a marker of expertise linked to higher verified success (https://www.anthropic.com/research/claude-code-expertise) [observational, vendor].
  - Design and planning transcripts at Anthropic rose from 1.0% to 9.9% (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [observational, vendor].
  - Only 10.1% of Claude.ai conversations consult the AI on approach before execution (Fluency Index) [observational].
  - The "directing" part of supervisory engineering work (https://arxiv.org/html/2605.23135) [survey].
- Strength: moderate. Consistent across studies, but no experiment isolates the effect of planning.
- Erodes: unclear. Planning share is rising, not falling.
- Train it when: before a multi-file change starts. Ask the user to write or approve a short plan with goals, non-goals and acceptance checks, then compare the result against it.

### Skill 5. Scoping and decomposing work into reviewable pieces

- Why: experienced people run agents in small steps. Large agent changes are rejected more and cost reviewers more.
- Evidence:
  - Median 1.8 steps per prompt; long plans executed at most 6 steps at a time (https://arxiv.org/html/2512.14012) [qualitative].
  - Low-experience coders produced bigger PRs with 31% lower acceptance and 4.52 times more review comments (https://arxiv.org/html/2602.23905v1) [observational].
  - PR size was a common reason for rejecting Claude Code PRs (https://arxiv.org/abs/2509.14745) [observational].
  - Small changes and version control were the main coping strategies for stochastic agent behavior (https://arxiv.org/abs/2512.22418) [qualitative].
  - Secondary reports of Faros data cite larger PRs on high-AI teams [vendor, unverified].
- Strength: moderate.
- Erodes: likely, because agents make large changes cheap. This is [Opinion] supported by the PR size data.
- Train it when: the diff passes a size threshold. Show its size and ask whether it should be split, and into what.

### Skill 6. Holding project and domain context the agent lacks

- Why: rejections and review friction come mostly from missing project context: CI and build constraints, architecture, preferred approaches, business rules.
- Evidence:
  - Friction from code ignoring CI constraints and lacking architectural context (https://arxiv.org/html/2602.23905v1) [observational plus qualitative].
  - Claude Code PR rejections mostly tied to project context (https://arxiv.org/abs/2509.14745) [observational].
  - Business logic and legacy integration seen as unsuitable for agents; 65 survey respondents called domain expertise critical (https://arxiv.org/html/2512.14012) [survey].
  - Task-specific expertise predicts success; domain experts outside software do nearly as well as engineers (https://www.anthropic.com/research/claude-code-expertise) [observational, vendor].
  - Engineers keep tasks needing organizational context (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [survey].
- Strength: moderate.
- Erodes: possibly. If agents explore the codebase for you, you may never build a mental model of it. That is [Opinion]; the RCT supports it only for a new library.
- Train it when: the agent proposes a change that touches a module boundary, a CI rule, or a business rule. Ask the user what constraint applies here before showing whether the agent respected it.

### Skill 7. Steering and correcting the agent mid-task

- Why: novices give up when sessions go wrong. Experts recover more often. Who corrects whom is a marker of expertise.
- Evidence:
  - Abandonment 19% for novices versus 5% to 7% for others; troubled-session verified success 4% versus 15% (https://www.anthropic.com/research/claude-code-expertise) [observational, vendor].
  - Users found agents hard to steer and overly proactive (https://arxiv.org/html/2507.08149) [user study].
  - Coders anchored on the first output (https://arxiv.org/abs/2512.22418) [qualitative].
- Strength: moderate.
- Erodes: unknown.
- Train it when: the agent loops, repeats a failed fix, or drifts from the plan. Prompt the user to stop it and restate the goal or a constraint, instead of asking it to "try again".

### Skill 8. Calibrated delegation and trust

- Why: knowing which tasks to delegate, and how much to check, separates control from vibing. Overconfidence is common.
- Evidence:
  - Developers believed AI sped them up by 20% when it slowed them by 19% (https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) [RCT].
  - Engineers delegate tasks that are easy to verify and low-stakes, and can fully delegate only 0% to 20% of work (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [survey].
  - Clear task-suitability patterns among professionals (https://arxiv.org/html/2512.14012) [survey].
  - Trust ranges from "purposive" acceptance without reading to selective checking by stakes (https://arxiv.org/abs/2512.22418); trust built through repeated verification (https://arxiv.org/abs/2506.23253) [qualitative].
- Strength: moderate. The METR perception gap is strong evidence of miscalibration; the rest is qualitative.
- Erodes: likely. Developers in METR's 2026 update avoided tasks they did not want to do without AI. That is a change in behavior, not proof of lost skill.
- Train it when: at task start. Ask the user to rate how easy this will be to verify and how costly a mistake is, then set the review depth to match. Later, show them their own forecast against what happened.

### Skill 9. Owning design, architecture and long-term code health

- Why: agents raise short-term output and long-term complexity. People keep design for themselves and say agents are weak at it.
- Evidence:
  - About 30% more static analysis warnings and about 41% more complexity after Cursor adoption; that debt later slowed velocity (https://arxiv.org/abs/2511.04427) [quasi-experimental].
  - 50 respondents drive architecture themselves; architecture split 13:23 on agent suitability (https://arxiv.org/html/2512.14012) [survey].
  - Engineers keep "high-level thinking and design" (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [survey].
  - Maintainability concern rose from 3% to 19% (https://arxiv.org/html/2605.23135) [survey].
  - DORA: AI amplifies existing strengths and weaknesses; stability is a concern [survey].
- Strength: moderate.
- Erodes: possible, unmeasured.
- Train it when: the agent adds a new abstraction, dependency or duplicated logic. Ask the user whether it fits the existing design and what it will cost to change later.

### Skill 10. Reading and understanding code changes

- Why: needed to verify. Agents make changes hard to follow. Note: in the RCT, code reading showed the smallest gap of the measured skills.
- Evidence:
  - Users found agent changes hard to follow; Copilot preferred for understanding (https://arxiv.org/html/2507.08149) [user study].
  - Low-reliance coders read diffs; one high-reliance coder never opened a file (https://arxiv.org/abs/2512.22418) [qualitative].
  - Code comprehension named as part of critical expertise (https://arxiv.org/html/2512.14012) [survey].
  - Code reading impaired by AI use, though less than debugging (https://arxiv.org/html/2601.20245) [RCT].
- Strength: moderate.
- Erodes: yes, measured in the RCT.
- Train it when: before approving a diff. Ask one question about it ("what happens if this input is empty?") that can only be answered by reading the code.

### Skill 11. Security and risk judgment

- Why: model-generated code often has security flaws. Experts catch solutions that are clever in a dangerous way. Agents may run risky commands.
- Evidence:
  - 45% of benchmark tasks produced a security flaw (https://www.veracode.com/genai-code-security-report) [vendor benchmark].
  - The "really smart in the dangerous way" example (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic) [qualitative].
  - Security-critical work seen as unsuitable for agents (https://arxiv.org/html/2512.14012) [survey].
  - A high-reliance coder enabled a mode that ran terminal commands without permission (https://arxiv.org/abs/2512.22418) [qualitative].
- Strength: moderate for the risk, weak for which human skill fixes it.
- Erodes: unknown.
- Train it when: the agent touches authentication, input handling, secrets, or asks for broad permissions. Ask the user to name the threat before the agent proceeds.

### Skill 12. Writing durable context and instructions for agents

- Why: context files and shared skills are now common. Clear explicit context is something professionals stress.
- Evidence:
  - Large-scale adoption of CLAUDE.md and AGENTS.md (https://arxiv.org/abs/2509.14744, https://arxiv.org/abs/2511.12884, https://arxiv.org/abs/2602.14690) [observational, descriptive].
  - 26.6% of Codex users use skills (https://arxiv.org/abs/2606.26959) [observational, vendor].
  - Rules files used to enforce standards (https://arxiv.org/html/2512.14012) [survey].
- Strength: weak. No study found here shows which context improves outcomes.
- Erodes: not applicable; this is a new skill.
- Train it when: the user corrects the agent on the same point a second time. Suggest writing it into the project's context file and show the wording.

### Skill 13. Managing several agents and your own attention

- Why: more than 10% of Codex users run three or more concurrent agents weekly. Time tracking broke down when developers did other work while agents ran.
- Evidence:
  - Concurrency figure (https://arxiv.org/abs/2606.26959) [observational, vendor].
  - Multitasking during agent runs complicated METR's measurement (https://metr.org/blog/2026-02-24-uplift-update/) [RCT design note].
  - Flow declined in the longitudinal study (https://arxiv.org/html/2605.23135) [survey].
  - No 2025+ study found that measures how well humans supervise parallel agents.
- Strength: weak.
- Erodes: unknown.
- Train it when: the user returns to an agent that finished while they were elsewhere. Show a short summary of what changed and ask them to confirm the plan still holds before continuing.

### Skill 14. Judging your own productivity honestly

- Why: perceived and measured speed diverged sharply in the one RCT of experienced developers. Self-reported gains dominate industry data.
- Evidence:
  - Forecast +24%, believed +20%, measured -19% (https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) [RCT].
  - 84% report productivity gains while experience worsens (https://arxiv.org/html/2605.23135) [survey].
  - Faros: more PRs, no company-level improvement [vendor telemetry, secondary].
- Strength: moderate. One strong RCT, the rest correlational. The 2026 METR data is inconclusive.
- Erodes: not applicable.
- Train it when: at the end of a session. Show time spent waiting, reviewing and reworking next to the user's own estimate.

## Part 3: What separates people who get good results

From the studies above, people who get good results with agents:

1. Plan first and keep design decisions [qualitative and observational: 2512.14012, claude-code-expertise].
2. Run agents in small steps and keep changes small [qualitative and observational: 2512.14012, 2602.23905].
3. Check every change against hard evidence [observational and qualitative: claude-code-expertise, 2512.14012, 2512.22418].
4. Bring task-specific domain and project knowledge [observational: claude-code-expertise, 2602.23905, 2509.14745].
5. Correct the agent and keep going when it struggles [observational: claude-code-expertise].
6. When learning, ask for concepts and explanations instead of finished code [RCT: 2601.20245].

People who get poor results, or learn less:

1. Hand over whole tasks and accept the result [RCT: 2601.20245; qualitative: 2512.22418].
2. Paste errors back to the AI without forming a hypothesis [RCT pattern "Iterative AI Debugging"; qualitative: 2512.22418].
3. Produce large changes that ignore project constraints [observational: 2602.23905].
4. Give up when the agent goes wrong [observational: claude-code-expertise].
5. Trust their sense of speed [RCT: METR 2025].

## Part 4: Gaps and open questions

- No RCT of skill formation with autonomous agents (as opposed to chat assistants) was found. The Shen and Tamkin result is the closest.
- No longitudinal measure of skill loss in working engineers. Vella and Blincoe collected skill data but did not report it.
- No study measures whether reviewers actually understand agent PRs. Fast review times are suggestive only.
- No study found here measures how well people supervise several agents in parallel.
- Most large-scale data is vendor research. Independent replication is thin.
- METR says its own design no longer measures current productivity well. Speed numbers from 2025 are already dated.

## Part 5: Sources excluded and why

The user asked for evidence specific to the 2025+ agent era, not ideas borrowed from other fields. These were left out of the skill list:

- Automation research from aviation, medicine and other industries (for example the "ironies of automation" literature). Relevant ideas, but not about software agents.
- General knowledge-worker studies, such as the CHI 2025 survey of 319 knowledge workers linking confidence in AI to less critical thinking (https://advait.org/files/lee_2025_ai_critical_thinking_survey.pdf). It is 2025 but not software-specific.
- Essay-writing or brain-imaging studies of ChatGPT use. Not software work.
- Pre-2025 studies of Copilot autocomplete and novices, such as The Widening Gap (https://arxiv.org/abs/2405.17739), and the cognitive engagement techniques study (https://arxiv.org/abs/2410.08922, IUI 2025, built on chat-era code generation). These predate agents. Kazemitabaar et al. found that a "Lead-and-Reveal" technique, where learners state each step before code is shown, worked best. It is consistent with Shen and Tamkin, and noted here only as background.

## Source list

Randomized controlled trials
- Shen and Tamkin 2026, How AI Impacts Skill Formation: https://arxiv.org/abs/2601.20245
- METR 2025 RCT: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ and https://arxiv.org/abs/2507.09089
- METR 2026 update: https://metr.org/blog/2026-02-24-uplift-update/

Observational and quasi-experimental
- Anthropic, Claude Code expertise: https://www.anthropic.com/research/claude-code-expertise
- Anthropic Economic Index, software development: https://www.anthropic.com/research/impact-software-development
- Anthropic AI Fluency Index: https://academy.claude.com/tutorials/the-ai-fluency-index
- OpenAI and coauthors, The Shift to Agentic AI: Evidence from Codex: https://arxiv.org/abs/2606.26959
- He et al., Cursor difference-in-differences: https://arxiv.org/abs/2511.04427
- Asdaque et al., novice vibe coders and review overhead: https://arxiv.org/abs/2602.23905
- Agentic PRs from Claude Code: https://arxiv.org/abs/2509.14745
- AIDev dataset: https://arxiv.org/abs/2602.09185 and https://arxiv.org/abs/2507.15003
- Context file studies: https://arxiv.org/abs/2509.14744, https://arxiv.org/abs/2511.12884, https://arxiv.org/abs/2602.14690, https://arxiv.org/abs/2601.20404

Surveys, interviews, user studies
- Anthropic, How AI is transforming work at Anthropic: https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- Huang et al., Professional developers don't vibe, they control: https://arxiv.org/abs/2512.14012
- Vella and Blincoe, longitudinal study: https://arxiv.org/abs/2605.23135
- Coding agents versus copilots user study: https://arxiv.org/abs/2507.08149
- Rolling the Dice: https://arxiv.org/abs/2512.22418
- Good Vibrations: https://arxiv.org/abs/2509.12491
- Vibe coding through conversation: https://arxiv.org/abs/2506.23253
- DORA 2025: https://dora.dev/research/ai
- Stack Overflow 2025 survey (secondary): https://www.infoworld.com/article/4031673/

Vendor reports
- CodeRabbit: https://coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- Veracode: https://www.veracode.com/genai-code-security-report
- GitHub Octoverse 2025: https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/
- Faros AI: primary report not accessed; figures from secondary coverage only.
