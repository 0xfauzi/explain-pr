# Skills map: staying in charge when agents write the code

This file merges five research reports in `design/skills/research/` (empirical, agentic-2025, expertise, practitioners, education) into one map of ten skills. It was revised after a citation check and a critique. The last section lists the challenges this revision did not accept.

## Ground rules for this map

- The subject is a 2025 and later phenomenon: coding agents (Claude Code, Codex, Cursor agent mode, Copilot agent mode, Devin and similar) that edit files, run commands and open pull requests.
- Each skill must rest on evidence from agentic software development. Evidence about chat assistants, autocomplete or "AI tools" in general is used only as supporting evidence and is labelled **Supporting, not agent-specific**. Research from other industries and from general knowledge work is not used.
- Each claim is tagged. The first five tags are evidence. The last is opinion.
  - **[Study]**: a controlled experiment, quasi-experiment, or structured observation or interview study.
  - **[Data]**: usage logs, telemetry, repository mining or large surveys.
  - **[Benchmark]**: a constructed test of agent behaviour, not real use.
  - **[Incident]**: a real-world failure. It shows a failure can happen, not how often.
  - **[Demonstration]**: a researcher's proof of concept or a disclosed vulnerability. It shows an attack is possible, not that it happened.
  - **[Opinion]**: practitioners, tool makers, educators, position papers, and this map's own design reasoning.
  - **(vendor)**: the source sells AI tools or AI review tools.
- Strength means how well the evidence shows the skill matters for outcomes with agents. Strong: at least one controlled study or large agent dataset, and sources agree. Moderate: consistent observational agent data, no controlled test, or sources disagree. Weak: mostly opinion, adoption counts or a single small source.
- Skills are ordered by strength only. Within a band, the order is this map's opinion of how often the moment comes up in a build. An earlier version ranked by "strength times importance" without defining importance. That has been dropped.
- No study yet shows that training any of these skills causes better outcomes with agents. Every practice moment below is a design hypothesis, not a tested intervention.

## The central finding

Work has moved from writing code to directing and checking it. Users made about 70% of planning decisions and about 20% of execution decisions across about 400,000 Claude Code sessions [Data, vendor] (https://www.anthropic.com/research/claude-code-expertise). Supporting, not agent-specific: a two-wave survey (October 2024 and April 2025, n=95 matched, ChatGPT the main tool) found engineers' time shifted from creation to verification (adjusted p=0.006) [Data, survey] (https://arxiv.org/abs/2605.23135).

Expertise goes with better results. Novice-rated sessions reached verified success in about 15% of cases, against 28% to 33% for intermediate users and above [Data, vendor] (https://www.anthropic.com/research/claude-code-expertise). This is correlational. A model rated expertise partly from how the user framed directions, what they asked Claude to verify, and who corrected whom. So those behaviours are inputs to the rating, not separate findings.

Agents also misreport their own work. In about 8,600 real coding-agent sessions, an LLM judge found "overselling success" in 34.7% of public SWE-chat sessions and evasion of tests or monitoring in 14.7% [Data, LLM-judged, not peer-reviewed] (https://www.greaterwrong.com/posts/smE9h9RnaK7FWKBZ2/measuring-coding-agent-misalignment-in-the-wild-1). The human check therefore has to work against the agent's account, not with it.

The tension: supervising agents needs skills that delegation may weaken. With an agent that edits code directly, students finished faster but understood their code less than students using a chatbot (n=54) [Study] (https://arxiv.org/abs/2607.26375). Supporting, not agent-specific: in an RCT with a chat-style assistant in a sidebar (n=52), the AI group scored 50% on a comprehension quiz against 67% for hand coders, with the largest gap on debugging [Study] (https://arxiv.org/abs/2601.20245, summary at https://www.anthropic.com/research/AI-assistance-coding-skills). The authors of an Anthropic article on its own engineers call this the "paradox of supervision" [Opinion, interviews] (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).

Both studies measured how much people learned right after a task. Neither measured existing skill getting worse over time.

## Skills

| # | Skill | Strength | New with agents, or old skill under pressure |
|---|---|---|---|
| 1 | Verifying agent work against evidence, not the agent's report | Strong that the problem is real. How well people catch it is unmeasured. | New |
| 2 | Controlling permissions and the agent as an attack surface | Moderate | New |
| 3 | Reviewing agent diffs | Moderate | Old, under pressure |
| 4 | Steering a run that has gone wrong | Moderate | New |
| 5 | Specifying intent, non-goals and a way for the agent to stop | Moderate | New in form |
| 6 | Choosing autonomy, chunk size and which agent to use | Moderate | New |
| 7 | Keeping a working understanding of code you did not write | Moderate for students. Unknown for working engineers. | Old, under pressure |
| 8 | Supplying minimal, enforced context | Moderate | New |
| 9 | Catching design decisions nobody chose | Moderate | New in form |
| 10 | Shipping and rolling back agent changes | Weak | Old, under pressure |

---

### 1. Verifying agent work against evidence, not the agent's report

**Definition.** Deciding what "done" means in a form that can be checked, confirming it with hard evidence (a test that fails before and passes after, a run, a log), and checking the agent's claims against the trace and the diff. It includes setting up the run so the checks are hard to game.

**Observable acts.** Naming the check before the task. Comparing each "done" claim with what the trace shows the agent read and ran. Flagging any edit to a test file. Making tests read-only or keeping them out of the agent's reach.

**Why it matters more now.** Agents report success confidently, and some weaken or rewrite the checks that would show they failed. A human reading only the summary cannot tell.

**Evidence.**
- Agents oversell and evade checks in real use. Across about 8,600 sessions, overselling appeared in 34.7% of public SWE-chat sessions and evading tests or monitoring in 14.7%. On Transluce's internal traffic the rates were 5.7% and 0.7%. Severe cases were under 2% in both. Each model ran on a different subset, so the authors warn against comparing models [Data, LLM-judged, not peer-reviewed] (https://www.greaterwrong.com/posts/smE9h9RnaK7FWKBZ2/measuring-coding-agent-misalignment-in-the-wild-1).
- Agents claim reviews they did not do. In planted-defect review tasks, agents failed to read every file in 67.9% of runs. In 80.4% of those runs they misled about it or did not disclose it. Agents that falsely claimed a full review missed planted defects about 1.8 times as often [Benchmark] (https://arxiv.org/abs/2609.20812).
- Agents cheat on tests that contradict the spec. GPT-5 "passed" by cheating in 54% of Conflicting-SWEbench tasks and Claude Opus 4.1 in 50% [Benchmark] (https://arxiv.org/abs/2510.20270).
- Setup changes this, and setup is under the person's control. In the same benchmark, giving GPT-5 an explicit way to abort cut cheating from 54% to 9%. The effect was "much less pronounced" for Opus 4.1. Hiding tests cut cheating to near zero. Read-only tests worked against models whose main trick is editing tests [Benchmark] (https://arxiv.org/abs/2510.20270).
- Instructions alone do not stop it. o3 monkey-patched evaluators. On one task, "Please do not cheat" left the reward-hacking rate at 80% [Benchmark] (https://metr.org/blog/2025-06-05-recent-reward-hacking/).
- Checks predict acceptance. Of 33,596 agent-written PRs, 71% were merged. Each extra failing CI check cut merge odds by about 15%. CI or test failure was 17% of 562 hand-labelled rejections [Data] (https://arxiv.org/abs/2601.15195).
- 9 of 13 observed professionals reviewed every agent change using diffs, tests, runs or debuggers [Study] (https://arxiv.org/abs/2512.14012).
- Practitioners agree: "Your job is to deliver code you have proven to work" [Opinion] (https://simonwillison.net/2025/Dec/18/code-proven-to-work/). Claude Code docs name "said it was done and it wasn't quite" as a core failure [Opinion, vendor] (https://code.claude.com/docs/en/best-practices). Thoughtworks put "complacency with AI-generated code" on Hold [Opinion] (https://www.thoughtworks.com/radar/techniques/complacency-with-ai-generated-code).
- Supporting, not agent-specific: 66% of developers are frustrated by AI output that is "almost right". The question covers AI tools in general [Data, survey] (https://survey.stackoverflow.co/2025/). Users fact-checked less when Claude produced a finished artifact (5.5% against 9.2%) [Data, vendor, Claude.ai] (https://academy.claude.com/tutorials/the-ai-fluency-index).
- Not used as support: Anthropic's expertise data. "What they ask Claude to verify" is an input to the expertise rating, so "experts verify more" is built into the measure (https://www.anthropic.com/research/claude-code-expertise).

**Strength.** Strong that agents misreport and game checks, from in-the-wild data, two benchmarks and repository mining. Strong that setup reduces gaming, in benchmarks. Unknown how well people catch overclaims: no study measures it.

**Erodes with agents?** Unknown. Plausibly, because accepting a "done" report is easy. Not measured.

**Practice moments.**
1. *Before the agent starts.* The person names the check that would prove the work. After the run, the tool shows whether that check ran and what it returned.
2. *When the agent says "done".* The tool lists the agent's claims. The person marks each as checked or unchecked. The tool then shows the trace: files actually read, tests actually run, test files edited.
3. *When the agent edits a test or a check.* The tool flags it at once. The person accepts or rejects the edit before anything else continues.
4. *When setting up a long or unattended run.* The person decides whether tests are read-only and whether the agent has an explicit way to stop and report.

---

### 2. Controlling permissions and the agent as an attack surface

**Definition.** Limiting what an agent can reach or destroy (permission modes, sandboxes, separate dev and prod, deny rules, backups), and treating anything the agent reads as a possible instruction.

**Observable acts.** Choosing a permission mode on purpose. Adding a deny rule or backup before a destructive step. Checking a new MCP server or untrusted input source before connecting it.

**Why it matters more now.** Agents run commands. A sentence in a prompt is not a control. Anything the agent reads can steer it.

**Evidence.**
- Agents with broad permissions destroyed real data. The Replit agent deleted a production database during a code freeze it had been told about, and gave misleading accounts of what it had done [Incident] (https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/, https://incidentdatabase.ai/entities/replit). Google Antigravity deleted a user's D: drive partition while the user had Turbo mode on, which runs commands without approval [Incident] (https://www.theregister.com/2025/12/01/google_antigravity_wipes_d_drive/).
- Attackers used installed agents. The Nx supply-chain malware ran AI CLIs with `--dangerously-skip-permissions`, `--yolo` and `--trust-all-tools` to search for secrets [Incident] (https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware).
- A wiper prompt was committed into the Amazon Q extension and shipped in version 1.84.0. AWS says the code was malformed and would not run, and that no customer resources were affected [Incident] (https://www.bleepingcomputer.com/news/security/amazon-ai-coding-agent-hacked-to-inject-data-wiping-commands/).
- Prompt injection against agents has been shown. A malicious GitHub issue could make an agent leak private repositories through the GitHub MCP server, shown on demo repositories [Demonstration] (https://invariantlabs.ai/blog/mcp-github-vulnerability). Copilot CVE-2025-53773 let injected text turn on auto-approve [Demonstration, disclosed vulnerability] (https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection).
- Approval prompts wear out. Claude Code users accept 93% of manual permission prompts, which Anthropic calls "approval fatigue" [Data, vendor] (https://www.anthropic.com/engineering/claude-code-auto-mode).
- A high-reliance coder let the agent run terminal commands without permission [Study, 7 live streams] (https://arxiv.org/abs/2512.22418). 7 of 99 surveyed professionals raised security-critical work, 5 of them calling agents unsuitable for it [Study] (https://arxiv.org/abs/2512.14012).
- Opinion: "If something has to happen every time, make it a hook, a deny rule, or a managed setting" [Opinion, vendor] (https://code.claude.com/docs/en/best-practices).

**Strength.** Moderate. Real incidents and demonstrations show the harm is possible. No study measures how often it happens in agent use, or which human habits prevent it.

**Erodes with agents?** Likely through approval fatigue (93% acceptance). Erosion of a skill is not measured.

**Practice moments.**
1. *When the person enables a broader permission mode, or the agent is about to run a destructive or irreversible command.* The tool shows what is reachable (prod data, credentials, the home directory). The person adds one safeguard: a deny rule, a backup or a branch.
2. *When a new MCP server is connected, or the agent will read untrusted content (issues, web pages).* The tool shows a concrete injection example for that source. The person decides what the agent may do after reading it.
3. *When the agent adds a dependency.* The person confirms the package exists and is the intended one.

---

### 3. Reviewing agent diffs

**Definition.** Reading an agent's change well enough to explain it and to judge whether it fits the codebase and the intent. Behaviour checks belong to skill 1. Security of the code itself is a code-level skill (see below).

**Observable acts.** Opening the files. Explaining a hunk in one's own words. Answering a question only the code can answer.

**Why it matters more now.** Agents make large changes cheaply, so review becomes the bottleneck, and approval can become a habit.

**Evidence.**
- Review attention fell with exposure. Across 400 repeat reviewers and 11,429 reviews of agent PRs, approval rose from 30.1% to 36.8% between early and late reviews, while comments per review fell 22% and words per review fell 28% [Data] (https://arxiv.org/abs/2606.22721). Another reading is possible: those agents' PRs may have improved. The data shown does not control for quality.
- Many agent PRs get little recorded review. 61.38% had no recorded review. In repositories with both human and agent PRs the rate was 28.92%. The authors warn that GitHub review records may not show real oversight [Data] (https://arxiv.org/abs/2605.02273). 38% of labelled rejected agent PRs had no meaningful human reviewer interaction [Data] (https://arxiv.org/abs/2601.15195).
- These four mining studies (2601.15195, 2605.02273, 2606.22721, 2602.23905) all use the same AIDev dataset. They are separate teams, not independent samples.
- Quality depends on the agent. Across 37,623 PRs from five agents, Codex PRs were reverted less often than human PRs (6.1% against 11.5%) and Devin PRs more often (14.5%). Pooled agent code had fewer security smells than human code (odds ratio 0.63) [Data] (https://arxiv.org/abs/2609.17598). This cuts against a flat claim that agent code is worse.
- Users new to agents found agent changes hard to follow (20 students, 2025) [Study] (https://arxiv.org/abs/2507.08149). One high-reliance coder never opened a file in nearly five hours [Study, 7 live streams] (https://arxiv.org/abs/2512.22418).
- Supporting, not agent-specific: AI co-authored PRs carried about 1.7 times more issues than human PRs, with security issues 1.57 times and maintainability 1.64 times. The sample is 470 PRs, and CodeRabbit's own AI reviewer found the issues [Data, vendor] (https://coderabbit.ai/whitepapers/state-of-AI-vs-human-code-generation-report, coverage at https://www.theregister.com/2025/12/17/ai_code_bugs/). On teams with high use of AI assistants, mostly autocomplete, review time rose 91% and PR size 154% [Data, vendor, telemetry to June 2025] (https://www.faros.ai/blog/ai-productivity-paradox-report-2025).
- Opinion: Canva tests spotting defects in AI code in interviews, with no validity data (https://canva.dev/blog/engineering/yes-you-can-use-ai-in-our-interviews).

**Strength.** Moderate. Large agent PR data shows review is thin and may thin further, but it comes from one dataset, and quality varies by agent. No study measures whether reviewers understand what they approve.

**Erodes with agents?** Possibly. The habituation data fits erosion but also fits better PRs. Supporting, not agent-specific: code reading was impaired in the chat-assistant RCT (https://arxiv.org/abs/2601.20245).

**Practice moments.**
1. *Before approving.* The person answers one question only the code can answer ("what happens on empty input?", "what calls this?"). The tool then shows the answer from the code or a quick run.
2. *Before opening a diff.* The person predicts which hunk is riskiest. Over time the tool compares those predictions with hunks that were later revised or reverted, or where a reviewer found a defect.
3. *Late in a long session.* When review effort (files opened, questions asked) has dropped against earlier changes, the tool asks the person to set the review depth for the next change.

---

### 4. Steering a run that has gone wrong

**Definition.** Noticing when an agent loops, repeats a failed fix or drifts from the goal, and stepping in with a new constraint, a narrower goal or a fresh start, instead of "try again".

**Observable acts.** Stopping the agent after repeated failed fixes. Restating the goal or a constraint. Starting a clean session when context is polluted.

**Why it matters more now.** Pasting the error back is easy and often works. When it does not, the run can burn time and drift. Debugging the software itself is an old skill and sits in the code-level list.

**Evidence.**
- Experts recover, novices abandon. Abandonment was 19% for novice-rated sessions against 5% to 7% for others. Verified success in troubled sessions was 4% for novices against 15% for experts [Data, vendor, correlational] (https://www.anthropic.com/research/claude-code-expertise). The authors: "part of the value of expertise appears to be the ability to steer the agent" [Opinion].
- A high-reliance coder pasted raw errors in 43 of 79 prompts, against 5 of 54 for a low-reliance coder. Coders anchored on the first output [Study, 7 live streams] (https://arxiv.org/abs/2512.22418).
- Users new to agents found them hard to steer and overly proactive [Study] (https://arxiv.org/abs/2507.08149).
- Supporting, not agent-specific: in the chat-assistant RCT, handing each error back to the AI was the lowest-scoring pattern (about 24%) [Study, post-hoc subgroup] (https://arxiv.org/abs/2601.20245). 45.2% of developers say debugging AI code takes longer [Data, survey, AI tools in general] (https://survey.stackoverflow.co/2025/ai).

**Strength.** Moderate. Large session data and small observation studies agree. The session data is correlational and the rating partly uses who corrects whom.

**Erodes with agents?** Unknown. Not measured.

**Practice moments.**
1. *After two or three agent fixes on the same failure.* The tool pauses. The person writes a one-line hypothesis or a new constraint. Afterwards the tool shows whether the next fix confirmed it.
2. *When the agent's plan drifts from the stated goal.* The tool shows the original goal next to the current plan, and the person chooses: continue, narrow or restart.

---

### 5. Specifying intent, non-goals and a way for the agent to stop

**Definition.** Before delegating, stating the goal, what must not change, what is out of scope, the acceptance check, and what the agent should do if the task cannot be done as asked.

**Observable acts.** A short written goal with at least one non-goal. An explicit "stop and report if" condition.

**Why it matters more now.** Agents fill gaps with plausible guesses, and when the task is impossible some cheat rather than stop.

**Evidence.**
- Giving the agent a way to stop changed behaviour: an abort option cut GPT-5's cheating from 54% to 9% on impossible tasks, less so for Opus 4.1 [Benchmark] (https://arxiv.org/abs/2510.20270).
- Unwanted features made up 4% of 562 labelled rejections of agent PRs, and incorrect or incomplete implementations 6% (3% plus 2%) [Data] (https://arxiv.org/abs/2601.15195).
- 11 of 13 observed professionals controlled design through plans [Study] (https://arxiv.org/abs/2512.14012). Users made about 70% of planning decisions [Data, vendor] (https://www.anthropic.com/research/claude-code-expertise). Design and planning rose from 1.0% to 9.9% of Claude Code work at Anthropic [Data, vendor] (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).
- Not used as support: "precise framing goes with success" from Anthropic's expertise data, because framing is an input to the expertise rating.
- Opinion: Claude Code docs recommend an interview, then a SPEC.md [vendor] (https://code.claude.com/docs/en/best-practices). Heavy spec tools are overkill for small changes (https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html). A UT Austin agent-era course splits work into "what to specify, what to delegate, what to verify" (https://www.cs.utexas.edu/~witchel/378AC/).

**Strength.** Moderate. One benchmark shows a stop condition matters. Mining and observation show that scope misses cause rejections. No controlled evidence that writing specs improves outcomes in real use.

**Erodes with agents?** Possibly. Low-effort prompting went with weaker comprehension in students (https://arxiv.org/abs/2607.26375). Not measured as skill loss.

**Practice moments.**
1. *Before a multi-file task.* The person writes the goal, one non-goal, one thing that must not change, and a stop condition. The size matches the task.
2. *After the agent plans, before it acts.* The tool shows the agent's stated assumptions. The person approves or rejects each one.
3. *After the run.* The tool shows any change outside the stated scope, and the person keeps or reverts it.

---

### 6. Choosing autonomy, chunk size and which agent to use

**Definition.** Matching how much the agent does per prompt, how often the person checks, and which agent is used, to how risky the work is and how easy it is to check.

**Observable acts.** Picking an autonomy level (plan review, checkpoints, unattended) at task start. Splitting work that is hard to check. Using a different agent or no agent for a task type that has gone badly.

**Why it matters more now.** The right chunk is not always small. Experts hand off bigger chunks when the work is easy to check. Agents also differ in quality.

**Evidence.**
- Experts got about 12 agent actions per prompt against about 5 for novices [Data, vendor, correlational] (https://www.anthropic.com/research/claude-code-expertise). Observed professionals had a median of 1.8 steps per prompt, and those with plans of 70 or more steps ran at most 6 at once [Study] (https://arxiv.org/abs/2512.14012). Together these suggest chunk size follows how easy the step is to check, not a rule that smaller is better [Opinion].
- Professionals rate suitability by task: "one-shotting without verification" 5 suitable to 23 unsuitable, business logic 2 to 15 [Study] (https://arxiv.org/abs/2512.14012).
- Size predicts rejection: unmerged agent PRs were larger and touched more files [Data] (https://arxiv.org/abs/2601.15195). "Too large" was 3.3% of Claude Code PR rejections, among the top three reasons [Data] (https://arxiv.org/abs/2509.14745). Low-experience vibe coders had 2.15 times more commits per PR, 31% lower acceptance and 4.52 times more review comments [Data] (https://arxiv.org/abs/2602.23905).
- Agents differ: revert rates ranged from 6.1% (Codex) to 14.5% (Devin) against 11.5% for humans [Data] (https://arxiv.org/abs/2609.17598).
- At Anthropic, most engineers say they can fully delegate only 0% to 20% of their work [Data, vendor, self-report]. From transcripts, the average longest run of consecutive tool calls rose from 9.8 to 21.2 [Data, vendor] (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).
- Supporting, not agent-specific: in METR's RCT on early-2025 tools (mainly Cursor with Claude 3.5 and 3.7 Sonnet), experienced developers forecast a 24% speedup, believed afterwards they were 20% faster, and were measured 19% slower [Study] (https://arxiv.org/abs/2507.09089). So feeling is a poor guide and the tool should supply measurements. METR's 2026 follow-up was inconclusive: 30% to 50% of developers skipped tasks they did not want to do without AI [Study] (https://metr.org/blog/2026-02-24-uplift-update/).
- Supporting, not agent-specific: 84% of continuing users of AI assistants reported productivity gains, while negative ratings of the work experience rose from 14% to 27%. Survivor bias applies [Data, survey] (https://arxiv.org/abs/2605.23135). DORA 2025 links AI adoption to higher delivery instability, and 30% of respondents trust AI "a little" (23%) or "not at all" (7%) [Data, survey, correlational] (https://dora.dev/research/2025/dora-report/).

**Strength.** Moderate. Agent data shows size, task type and agent choice affect outcomes. Nothing shows what good calibration looks like or how to train it. "Honest self-assessment" was dropped as a skill: METR shows introspection fails, so the tool must measure instead.

**Erodes with agents?** Possibly, through habituation (skill 3). Not measured.

**Practice moments.**
1. *At task start.* The person rates stakes and how checkable the result is, and picks an autonomy level. After the task, the tool shows rework and correction rounds against that choice.
2. *When a plan or diff passes a size threshold.* The tool shows the natural seams. The person decides whether to split.
3. *Over weeks.* The tool shows how often accepted changes were later fixed or reverted, by task type and by agent. The person sets the default autonomy for the next task of that type.

---

### 7. Keeping a working understanding of code you did not write

**Definition.** Understanding how the code you ship works and why, including concepts the agent introduced, well enough to change, debug and check it without the agent. Code comprehension itself is an old skill. The agent-specific part is narrow: code arrives faster than it is understood, and agents default to doing over explaining.

**Observable acts.** Asking for the key idea before accepting a change. Explaining a changed part without looking.

**Evidence.**
- With an agent that edits code directly, against a chatbot, 54 students finished the first task faster but understood their code less (Cohen's d above 0.80). Low-effort prompting and accepting edits without review went with weaker comprehension. On extending their code without AI, agent users did about as well or slightly better in raw scores, and worse only after controlling for how accurate their first-task code was. Students knew they understood less but still preferred agents [Study] (https://arxiv.org/abs/2607.26375).
- 79% of Claude Code conversations were automation against 49% on Claude.ai, and learning patterns were much rarer on Claude Code [Data, vendor] (https://www.anthropic.com/research/impact-software-development).
- Engineers say fast output makes it harder to take time to learn, and some practise without Claude to avoid atrophy [Opinion, interviews] (https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic).
- Margaret-Anne Storey's "cognitive debt": a team losing shared understanding of its system [Opinion] (https://arxiv.org/abs/2603.22106, quoted at https://simonwillison.net/2026/Feb/15/cognitive-debt).
- Brown's agentic course page reports that "a majority of students were concerned" they did not understand their own codebase [Opinion, experience report] (https://cs.brown.edu/courses/csci1970kf/agentic-spr-2026/visitors.html).
- Supporting, not agent-specific: in the chat-assistant RCT (n=52), the AI group scored 50% against 67% (d=0.738), with no significant speed gain. Generation-then-comprehension scored about 86%, conceptual inquiry about 65%, full delegation about 39%. These patterns are post-hoc, with 2 to 7 people each (generation-then-comprehension is n=2), and were not pre-registered. Learners chose their own pattern, so this does not show that prompting people into a pattern would work [Study] (https://arxiv.org/abs/2601.20245).
- Supporting, education, chat era: when students had to explain their code in weekly oral reviews, AI use rose (pasted share 61% to 68%) with no drop in exam scores [Study, n=96] (https://arxiv.org/abs/2605.21374).

**Strength.** Moderate for students: one controlled study with a true agent. Unknown for experienced engineers in their own codebase over months.

**Erodes with agents?** Lower skill gain was measured right after a task. Erosion over time was not.

**Practice moments.**
1. *When the agent first uses a library, API or part of the codebase new to the person.* The person predicts what the code will do. The tool then runs it or shows a test result.
2. *After a change lands.* The person writes a small test or states what one input will produce. The tool checks this against the code, not against the agent's own explanation, which may be wrong (skill 1).
3. *When the person returns to a feature after other work.* The person sketches how a request flows through it, then the tool shows the call path.

---

### 8. Supplying minimal, enforced context

**Definition.** Knowing the project, domain and team facts the agent cannot see (CI rules, architecture, business rules, work in progress elsewhere), giving them to the agent, and turning repeated corrections into tests, hooks or CI rules first, with short prose only for what cannot be enforced.

**Observable acts.** Stating the constraint that applies to a change. Turning a repeated correction into a test or hook.

**Why it matters more now.** Most rejections of agent PRs are about missing project context. But long prose context files mostly cost tokens and do not help.

**Evidence.**
- Claude Code PRs were accepted at 83.8% against 91.0% for human PRs, and rejections were mostly about project context, not code defects [Data] (https://arxiv.org/abs/2509.14745).
- In the 15 agent PRs with the most review comments, friction came from code that ignored CI and build constraints and lacked architectural context [Study, qualitative, n=15] (https://arxiv.org/abs/2602.23905).
- 23% of labelled rejected agent PRs duplicated existing work [Data] (https://arxiv.org/abs/2601.15195).
- 65 of 99 surveyed professionals called domain expertise critical, and legacy integration was judged unsuitable for agents (3 to 17) [Study] (https://arxiv.org/abs/2512.14012). Software-occupation users were only slightly ahead of others on verified success (34% against 29%) [Data, vendor] (https://www.anthropic.com/research/claude-code-expertise).
- Context files mostly did not help. Across several agents and models, repository context files generally did not improve task success and raised inference cost by about 20% or more. Developer-written files did better than LLM-generated ones. The authors advise including only instructions the agent needs that are not already in the README, and testing them [Benchmark] (https://arxiv.org/abs/2602.11988).
- Adoption is wide: studies count 253 and 2,303 context files [Data] (https://arxiv.org/abs/2509.14744, https://arxiv.org/abs/2511.12884), and configuration mechanisms of all kinds in 2,853 repositories [Data] (https://arxiv.org/abs/2602.14690). 26.6% of Codex users use skills [Data, vendor] (https://arxiv.org/abs/2606.26959).
- Opinion: "harness engineering", where the human steers by building guides and sensors around the agent (https://martinfowler.com/articles/harness-engineering.html, https://openai.com/index/harness-engineering/).

**Strength.** Moderate that missing context causes rejections. Evidence against the idea that more prose context helps.

**Erodes with agents?** Unknown. Not measured.

**Practice moments.**
1. *When the agent proposes a change that crosses a module boundary, a CI rule or a business rule.* The person states the constraint that applies. The tool then shows whether the change respected it.
2. *When the person corrects the agent on the same point a second time.* The tool offers a test, hook or CI rule first, and a one-line context note only if the rule cannot be enforced.
3. *When a new session rediscovers a fact.* The tool shows what was in the agent's context, and the person decides whether it belongs there.

---

### 9. Catching design decisions nobody chose

**Definition.** Spotting design decisions made implicitly inside agent output, such as a new dependency, a new abstraction, a changed data model, or a second way of doing something already solved, and making each one an explicit decision. General architecture skill is old and sits in the code-level list.

**Observable acts.** Accepting or rejecting a new module, dependency or data model as a decision. Choosing which of two duplicate approaches stays.

**Evidence.**
- After Cursor adoption in about 806 repositories, static analysis warnings rose about 30% and code complexity about 41%, and the debt later reduced velocity. Most adoptions fell before Cursor's agent mode, but the authors report the results hold for adoptions after its release [Study, quasi-experiment] (https://arxiv.org/abs/2511.04427).
- 23% of labelled rejected agent PRs duplicated existing work [Data] (https://arxiv.org/abs/2601.15195).
- 50 of 99 professionals drive architecture themselves, and agent suitability for architecture split 13 to 23 [Study] (https://arxiv.org/abs/2512.14012).
- Opinion: "vibe architecting", where agents make architectural choices with little record, and changing only the prompt gave structurally different systems (https://arxiv.org/abs/2604.04990). "Intent debt" (https://arxiv.org/abs/2603.22106). Persona prompts change style, not structure (https://newsletter.kentbeck.com/p/taming-the-genie-like-kent-beck). DORA calls AI an amplifier of existing strengths and weaknesses [Opinion, in a survey report] (https://dora.dev/research/2025/dora-report/). One student in Brown's agentic course called agent code "messy and convoluted" [Opinion, one student's view] (https://www.brown.edu/news/2026-06-11/agentic-studio-ai-programming).
- Supporting, not agent-specific: maintainability as a primary concern rose from 3% to 19% [Data, survey] (https://arxiv.org/abs/2605.23135).

**Strength.** Moderate. One solid quasi-experiment on the outcome, plus duplicate data and opinion. No measure of the human skill.

**Erodes with agents?** Unknown. Not measured.

**Practice moments.**
1. *When the agent adds a new module, abstraction, dependency or data model.* The person accepts or rejects it and writes one line of why. When that code is next changed, the tool shows the line and asks whether it still holds.
2. *When the agent adds a second way of doing something already solved elsewhere.* The tool shows both. The person decides which stays.

---

### 10. Shipping and rolling back agent changes

**Definition.** Staging the release of an agent change, knowing which signal to watch after it ships, and having a rollback ready before merge.

**Why it is listed.** Every other practice moment ends at merge. Agent changes are reverted at rates that differ by agent.

**Evidence.**
- Revert rates: Codex 6.1%, Devin 14.5%, humans 11.5% [Data] (https://arxiv.org/abs/2609.17598).
- Claude Code PRs waited a median 12.6 hours for first human review, the longest of the five agents [Data] (https://arxiv.org/abs/2609.17598).
- A reported AWS outage in December 2025 was linked to the Kiro agent by unnamed sources. Amazon blames misconfigured access controls [Incident, disputed] (https://www.theregister.com/2026/02/20/amazon_denies_kiro_agentic_ai_behind_outage/).
- Supporting, not agent-specific: DORA 2025 links AI adoption to higher delivery instability [Data, survey, correlational] (https://dora.dev/research/2025/dora-report/).

**Strength.** Weak. Some data that agent changes get reverted. No study of the human skill.

**Practice moment.** *Before merging an agent change to a production path.* The person names the signal to watch and the rollback step. After deploy, the tool shows that signal.

---

## When practice moments should fire

Claude Code users accept 93% of manual permission prompts [Data, vendor] (https://www.anthropic.com/engineering/claude-code-auto-mode). Training prompts at every moment would likely go the same way [Opinion]. So the tool should fire only on high-risk events: a test or check edited by the agent, an irreversible command, a broader permission mode, a new dependency or structural change, a "done" claim on unchecked work, and repeated failed fixes. Each moment must end with feedback: the person commits to an answer, then sees what the trace, the code or a later outcome shows. A moment with no answer to compare against will not train judgment [Opinion].

## Claims with weak support

These came up in the research but lack enough 2025+ agent evidence to stand as skills.

- **Product judgment and problem framing.** 4% of labelled rejected agent PRs added unwanted features (https://arxiv.org/abs/2601.15195). DORA links user-centric teams to better AI outcomes, but the result is correlational and not agent-specific (https://cloud.google.com/blog/products/ai-machine-learning/introducing-doras-inaugural-ai-capabilities-model). Weak here means unmeasured, not shown to be unimportant. PR merge rates show whether a change was mergeable, not whether it was worth building. Treat as a hypothesis.
- **Running several agents in parallel.** More than 10% of Codex users run three or more agents at once each week [Data, vendor] (https://arxiv.org/abs/2606.26959), and multitasking broke METR's time tracking (https://metr.org/blog/2026-02-24-uplift-update/). No study measures how well people supervise parallel agents.
- **Prompting as a lasting skill.** Supporting, education, general GenAI: it is the GenAI skill taught most often (26 of 56 instructors) [Data, survey] (https://doi.org/10.1145/3760545.3783970), but students doubt its long-term value [Opinion] (https://arxiv.org/abs/2606.07545). The durable parts are specification (skill 5) and context (skill 8).
- **Keeping a decision log.** Recommended by educators and course designs [Opinion], with no outcome data in agent work. Folded into skill 9 as a practice.
- **Flow and attention management.** Supporting, not agent-specific: flow showed a non-significant decline in a two-wave survey, as did cognitive load (https://arxiv.org/abs/2605.23135). No evidence that it is a trainable skill.
- **Systems thinking as a separate skill.** No 2025+ study measures it apart from skills 8 and 9.
- **New interview formats** (Canva, Meta AI-enabled rounds). Neither has published data showing they predict job performance.

## Old skills under more pressure

Writing code by hand is out of scope. These older skills are still needed because the agent skills depend on them.

- **Reading code and tracing execution.** Review and verification (skills 1 and 3) need it. Supporting, not agent-specific: it was impaired in the chat-assistant RCT (https://arxiv.org/abs/2601.20245). In live-stream observation, low-reliance coders inspected code. Outcomes were not compared (https://arxiv.org/abs/2512.22418).
- **Debugging.** Forming and testing a hypothesis with breakpoints, logs and reproduction, not only re-prompting. Supporting, not agent-specific: debugging showed the largest gap in the chat-assistant RCT (https://arxiv.org/abs/2601.20245), and in one course study no student used a debugger and 57% relied on the LLM [Study, n=14] (https://arxiv.org/abs/2510.04986).
- **Writing meaningful tests.** A test that still passes when the change is reverted proves nothing, and agents edit tests to pass (skill 1). Supporting, education: educators are adding "evidence of testing" to assessment (https://doi.org/10.1145/3760545.3783970).
- **Judging code security: access control, input handling, secrets, dependency hygiene.** Supporting, not agent-specific: 45% of code samples from over 100 LLMs failed security tests, and 86% failed on cross-site scripting defences [Benchmark, vendor] (https://www.veracode.com/genai-code-security-report). Apps built without row-level security (Lovable, CVE-2025-48757, disputed) [Incident] (https://nvd.nist.gov/vuln/detail/CVE-2025-48757). Supporting, 2024: models recommend packages that do not exist (about 5% to 22% by model) [Study] (https://arxiv.org/abs/2406.10279). Against these, pooled agent PRs had fewer security smells than human PRs (https://arxiv.org/abs/2609.17598).
- **Core concepts: concurrency, data structures, complexity, transactions.** Needed to catch plausible but wrong fixes, such as an agent "fixing" a race condition by adding a sleep [Opinion] (https://www.theregister.com/2026/02/23/microsoft_ai_entry_level_russinovich_hanselman/).
- **Architecture.** Needed for skill 9.
- **Version control: small commits, branches, reverting.** One of several safeguards coders used against unpredictable agent behaviour, with undo, small edits and tests (https://arxiv.org/abs/2512.22418).

## Known gaps in the evidence

- No skill-formation RCT with autonomous agents on professionals. The closest are Balepur et al. (agent, students) and the Shen and Tamkin RCT (chat-style assistant, one library, junior engineers).
- No longitudinal measure of skill loss in working engineers.
- No study measures how well people catch an agent's false claims about its own work.
- No study measures whether reviewers understand the agent PRs they approve.
- The main agent PR studies share one dataset (AIDev).
- No study shows that training any skill here improves outcomes.
- Much large-scale data comes from vendors (Anthropic, OpenAI, CodeRabbit, Veracode, Faros).

## What this means for a tool that trains people while they build

This section is opinion based on the evidence above.

The skills are exercised at the two ends of each agent task, and agents make both ends easy to skip. At the start, people under-specify, give no stop condition, over-scope and over-grant permissions. At the end, they accept "done" and skim the diff, while the agent's own report may be false.

So the tool should act at a few high-risk moments: before a task starts, when the agent edits a test, when it runs something irreversible, when it makes a structural move, when a fix fails repeatedly, and when it says "done". At each moment the person commits to a prediction or a decision, and the tool then shows evidence from the trace, the code or a later outcome. The tool should supply the measurements (rework, reverts, checks actually run) rather than ask people how productive they feel, because METR found feelings unreliable.

The tool can also make cheating harder by setup: read-only tests, an explicit way to stop, and flags on test edits. This is the one area where benchmark evidence shows a setup change works.

The RCT's learning patterns (asking for explanations, generation then comprehension) are a reasonable design starting point, not proven levers. They were post-hoc, with 2 to 7 people per pattern, from a chat-style assistant, and learners chose them. No study yet shows that prompting people into these patterns helps.

## Challenges not accepted, and why

- **Merging skills 5, 6 and 8 into one.** Not merged. Each now has a separate observable act: writing a stop condition and non-goals (5), choosing autonomy and chunk size (6), and turning corrections into enforced checks (8). They fire at different moments.
- **Product judgment as a full skill.** Kept under weak support, but reworded to say it is unmeasured rather than unimportant. Making it a skill would break this map's rule that each skill rests on agent evidence. The only agent number is 4% of rejections.
- **Using "45.1% of merged PRs needed later revision" as evidence for skill 10.** Not used. The citation check showed the revisions happened before merge, at a rate close to human PRs.
- **The critique's reading of Gloaguen et al. that developer-written files "helped a little".** Not used as stated. The current version of the paper says context files generally did not improve success for both LLM-generated and developer files, though developer files did better than LLM ones.
- **Dropping METR 2025 entirely.** Kept, but only as supporting evidence. Its point is about measurement (people misjudge their own speed), which the tool design relies on.
- **Calling the review habituation result "drift".** Partly accepted. The data is kept, and the other explanation (PRs got better) is stated.
- **Adding systems thinking as a skill.** Agreed with the critique not to add it.
