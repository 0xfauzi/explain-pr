# What practitioners say engineers need when agents write the code

Scope: guidance from 2025 and 2026 on working with coding agents (Claude Code, Codex, Cursor, Copilot and similar). This file covers what leading practitioners, tool makers and engineering organizations say, plus large developer surveys and the hiring changes that followed.

Per the user request, this file does not borrow from other industries (aviation, medicine, chess and so on). Every source here is about software built with LLM agents, and almost all of it dates from 2025 or 2026.

## How to read this file

Each claim is labelled:

- **Study**: a controlled experiment or measured data.
- **Survey**: self-reported data from many respondents. It shows what people believe or do, not what works.
- **Opinion**: a named practitioner or organization saying what they think. Credible, but not proof.

Most of the material in this angle is opinion and survey. The few studies that exist are flagged where they back an opinion up or contradict it. Where I could not open a primary page and relied on a secondary summary, I say so.

## Short answer

Practitioners agree on a short list. When agents write the code, the human job moves to:

1. Proving the change works (verification).
2. Reading and reviewing agent output well, at higher volume.
3. Saying clearly what you want before the agent starts (specification, decomposition).
4. Shaping the agent's environment so it fails less (context and harness engineering).
5. Keeping a working mental model of the system (fighting "cognitive debt").
6. Design and architecture judgment ("taste").
7. Choosing what to delegate, how much autonomy to give, and in what size of change.
8. Debugging and diagnosis when the agent is wrong.
9. Calibrated trust: noticing when you are over-trusting the tool.
10. Learning on purpose while using the agent, not just shipping.
11. Owning outcomes: security, user value, accountability.

The rest of the file gives the sources for each.

---

## 1. Sources reviewed

### 1.1 Tool makers

**Anthropic, "How AI is transforming work at Anthropic" (December 2025).** Survey of 132 engineers and researchers, 53 interviews, plus Claude Code usage data. https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic

- Survey: engineers report using Claude in about 60% of their work, with a self-reported productivity gain of about 50%.
- Survey: more than half said they can "fully delegate" only 0 to 20% of their work.
- Survey/usage data: 27% of Claude-assisted work is work that would not have been done otherwise.
- Opinion (interviews): the report names a "paradox of supervision". Using Claude well needs supervision, and supervising well needs the coding skills that heavy AI use may erode.
- Opinion (interviews): engineers delegate tasks that are easy to verify. One said it is "amazing for everything where validation effort isn't large in comparison to creation effort."
- Opinion (interviews): engineers tend to keep "high-level thinking and design" for themselves. Usage data shows design and planning use of Claude Code rose from 1.0% to 9.9% over six months, so this line is moving.
- Opinion (interviews): a security engineer described a Claude proposal as "really smart in the dangerous way", the kind of thing only an experienced engineer would catch.
- Opinion (interviews): some engineers deliberately practise tasks without Claude to avoid skill atrophy. Others think the skills "could come back if they ever needed to."
- Limits: self-reports, one company, staff who build the tool.

**Anthropic, "How AI Impacts Skill Formation" (Shen and Tamkin, January 2026, arXiv 2601.20245).** Randomized trial, about 52 developers learning the Trio async Python library. I relied on secondary summaries (InfoQ, DevClass) and did not read the paper itself. https://infoq.com/news/2026/02/ai-coding-skill-formation/ and https://devclass.com/2026/02/02/anthropic-research-skilled-devs-make-better-use-of-ai-but-using-ai-is-bad-for-learning-skills/

- Study: the AI group scored 17% lower on a follow-up skills test covering concepts, debugging and code reading. The largest gap was in debugging.
- Study: the AI group was not significantly faster.
- Study: the authors describe six interaction patterns. Three involved cognitive engagement (asking for explanations, follow-up questions) and preserved learning even with AI.
- Limits: small sample, short-term measurement, a single unfamiliar library.

**Anthropic, Claude Code best practices (current docs, fetched November 2026).** https://code.claude.com/docs/en/best-practices

- Opinion (vendor guidance): "If it has nothing to run that tells it whether the work actually is done, 'looks done' is all it has to go on. In practice that makes you the test suite."
- Opinion: ask for evidence: "'All tests pass' on its own tells you very little." Ask for the command and its output, or a screenshot.
- Opinion: write a specific prompt that names the file, the symptom and what "fixed" looks like. When you do not know what you want, have the agent interview you and write a SPEC.md first.
- Opinion: review against the spec, with a reviewer that did not write the code, and tell it to "skip style". "A reviewer that's asked to find problems will always find something."
- Opinion: separate instructions the model may ignore (prompt, CLAUDE.md, skills) from deterministic controls that always run (hooks, tests, CI, deny rules).

**OpenAI, "Harness engineering: leveraging Codex in an agent-first world" (Ryan Lopopolo, 11 February 2026).** I could not open the page and relied on search excerpts and mirrors. https://openai.com/index/harness-engineering/

- Opinion/case report: a small team built an internal product of about a million lines over five months with no hand-written code, as a forcing function. The framing is "humans steer, agents execute."
- Opinion: early progress was slow because the environment was underspecified, not because the model was weak. The human job became building the tools, docs and checks the agent needs.
- Opinion: keep repository knowledge (architecture docs, execution plans, quality grades) as short, versioned files the agent can read.

### 1.2 Thoughtworks and martinfowler.com

**Thoughtworks Technology Radar, "Complacency with AI-generated code" (Hold, last on the November 2025 edition).** https://www.thoughtworks.com/radar/techniques/complacency-with-ai-generated-code

- Opinion: coding agents produce larger change sets that are harder to review, so speeding up writing moves pressure onto review.
- Opinion, citing data: the blip cites GitClear (2024) on rising duplication and churn and falling refactoring, and a Microsoft study of knowledge workers that found AI-driven confidence can come at the expense of critical thinking.
- Opinion: the recommended response is to reinforce TDD and static analysis and build them into the workflow, for example with shared, curated instructions.

**Thoughtworks Technology Radar Vol. 34 (April 2026).** Via iTWire coverage, not the Radar itself. https://itwire.com/business-it-news/data/as-ai-accelerates-software-complexity,-thoughtworks-technology-radar-urges-a-return-to-engineering-fundamentals-to-combat-cognitive-debt.html

- Opinion: warns of "accumulating cognitive debt as AI generates increasingly larger amounts of code", and says teams must make sure developers "still understand the systems they are building."
- Opinion: theme "Retaining principles, relinquishing patterns". AI speed pushes teams back to zero trust, DORA metrics and testability.
- Opinion: teams "iterate on coding agent harnesses": feedforward controls (Agent Skills, spec-driven development) and feedback controls (mutation testing).

**Birgitta Böckeler, "Harness engineering" (martinfowler.com, 2 April 2026).** https://martinfowler.com/articles/harness-engineering.html

- Opinion: a harness is made of guides (steer before the agent acts) and sensors (check after). "The human's job in this is to steer the agent by iterating on the harness."
- Opinion: when a failure repeats, the human improves a guide or a sensor so it does not happen again.
- Opinion: "Correctness is outside any sensor's remit if the human didn't clearly specify what they wanted in the first place."
- Opinion: the agent has "no organisational memory". The human supplies conventions, context and judgment about which debt is acceptable.

**Birgitta Böckeler, "Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl" (15 October 2025).** https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html

- Opinion: "spec-driven development" covers three different ideas: spec-first, spec-anchored, spec-as-source.
- Opinion: heavy spec tooling was overkill for small and mid-sized changes. She would "rather review code than all these markdown files."
- Opinion: agents still ignored instructions in the spec and duplicated existing code. Small, iterative steps keep the engineer in control.
- Implied skill: separating functional intent from technical design, and sizing the spec to the problem.

### 1.3 Individual practitioners

**Simon Willison, "Vibe engineering" (7 October 2025).** https://simonwillison.net/2025/Oct/7/vibe-engineering/

Opinion. He lists what makes experienced engineers effective with agents:

- Automated tests: "If your project has a robust, comprehensive and stable test suite agentic coding tools can fly with it."
- Planning before the agent writes code.
- Good documentation.
- Version control habits, to undo mistakes and see what changed.
- Automation: CI, formatting, linting, preview deploys.
- A culture of code review, and being fast at it.
- Management skills: clear instructions, context, actionable feedback.
- Manual QA, including probing edge cases.
- Research skills: proving an approach before handing it off.
- Judgment about what to outsource, which shifts as models improve.
- Re-learning estimation.

He later noted (February 2026) that "agentic engineering" has become the more common name.

**Simon Willison, "Your job is to deliver code you have proven to work" (18 December 2025).** https://simonwillison.net/2025/Dec/18/code-proven-to-work/

- Opinion: "If you haven't seen the code do the right thing yourself, that code doesn't work."
- Opinion: every change should ship with an automated test that "should fail if you revert the implementation", and you should still test manually.
- Opinion: dumping large, untested LLM pull requests on reviewers is "a waste of other people's time." The human carries accountability because a computer cannot.
- Opinion: teach the agent to prove its own changes too.

**Simon Willison, "Cognitive debt" (15 February 2026).** https://simonwillison.net/2026/Feb/15/cognitive-debt

- Opinion/first-person report: after prompting whole features without reviewing them, "I no longer have a firm mental model of what they can do and how they work", which made it harder to decide what to build next.

**Margaret-Anne Storey, cognitive and intent debt (October 2025 onward; paper March 2026).** https://www.alphaxiv.org/abs/2603.22106 , coverage at https://leaddev.com/ai/ai-coding-creates-two-kinds-of-debt-youre-only-measuring-one

- Opinion/framework: a "Triple Debt Model": technical debt in code, cognitive debt in people (lost shared understanding of the system), intent debt in missing written rationale.
- Opinion: her student-team example: the team blamed messy code, but the real problem was that nobody could explain why design decisions were made.
- Opinion: she warns against rushing to a single metric for this.

**Andrej Karpathy.** Mostly via secondary coverage of talks and X posts.

- Opinion (YC AI Startup School, June 2025): the "autonomy slider": choose how much autonomy to give an agent per task, keep the AI "on a leash", verify its work in small chunks. https://www.youonai.ai/fieldguide/txt/autonomy_slider.html (secondary)
- Opinion/self-report (X, 26 January 2026): he moved from about 80% manual coding to about 80% agent coding in a few weeks, and wrote "I've already noticed that I am slowly starting to atrophy my ability to write code manually." https://the-decoder.com/former-tesla-ai-chief-andrej-karpathy-now-codes-mostly-in-english-just-three-months-after-calling-ai-agents-useless/ (secondary)

**Kent Beck (2025).** Pragmatic Engineer podcast, 11 June 2025, https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent and his newsletter, https://newsletter.kentbeck.com/p/taming-the-genie-like-kent-beck

- Opinion: TDD is a "superpower" with agents because agents introduce regressions. He reports agents deleting tests to make them pass, so the human has to guard the tests.
- Opinion: prompting the agent to act "like Kent Beck" improved naming and test style but "didn't change the fundamental structural decisions." Structure stays a human job.

**Addy Osmani (2025 to 2026).** Book *Beyond Vibe Coding* (O'Reilly, 2025), https://www.oreilly.com/library/view/beyond-vibe-coding/9798341634749/ , and "The next two years of software engineering" (January 2026). Mostly secondary summaries.

- Opinion: the "70% problem": agents get you most of the way fast. The last part (edge cases, security, integration with production) stays hard and needs durable skills.
- Opinion: code review is becoming one of the most valuable skills in the profession. The engineer owns architecture and reviews every change.

**Gene Kim and Steve Yegge, *Vibe Coding* (IT Revolution, October 2025).** https://bookshop.org/p/books/vibe-coding-building-production-grade-software-with-genai-chat-agents-and-beyond-gene-kim/b6e53e37eeba8cac

- Opinion: engineers move toward directing and integrating many agents' output. I did not read the book and found little specific skill guidance in available summaries, so it carries little weight here.

### 1.4 Surveys

**DORA, "State of AI-assisted Software Development" (2025).** Nearly 5,000 respondents. https://dora.dev/research/2025/dora-report/ and https://blog.google/technology/developers/dora-report-2025/

- Survey: 90% of respondents use AI at work. Median two hours a day.
- Survey: over 80% say AI improved their productivity.
- Survey: 30% have little or no trust in AI output (23% "a little", 7% "not at all").
- Survey (correlational): AI use is now linked to higher delivery throughput, but also to higher instability.
- Opinion of the authors: AI is "an amplifier", it magnifies existing strengths and weaknesses.
- The DORA AI Capabilities Model names seven capabilities. From search results (I could not open the report), they include: a clear and communicated AI stance, healthy data ecosystems, AI-accessible internal data, strong version control practices, working in small batches, a user-centric focus, and quality internal platforms. https://cloud.google.com/blog/products/ai-machine-learning/introducing-doras-inaugural-ai-capabilities-model
- Survey (correlational): teams with a strong user focus gain from AI. Teams with weak user focus see performance decline after adopting AI.

**Stack Overflow Developer Survey 2025, AI section.** https://survey.stackoverflow.co/2025/ai

- Survey: 84% use or plan to use AI tools. 50.6% of professional developers use them daily.
- Survey: 46% distrust AI accuracy (19.6% highly). 33% trust it. 3.1% highly trust it.
- Survey: top frustration, 66%: "AI solutions that are almost right, but not quite." 45.2%: "Debugging AI-generated code is more time-consuming."
- Survey: 75.3% would still ask a person "when I don't trust AI's answers."
- Survey: most do not plan to use AI for deployment and monitoring (75.8%), project planning (69.2%), or committing and reviewing code (58.7%).
- Survey: about 31% use agents at least monthly. Among agent users, 63.2% say agents sped up learning about new tech or codebases, but only 37.5% say agents improved code quality.
- Survey: 72% say they do not vibe code at work.

**Pragmatic Engineer AI tooling survey (January to February 2026, nearly 1,000 respondents).** https://newsletter.pragmaticengineer.com/p/ai-tooling-2026 (partly paywalled; summaries only)

- Survey: Claude Code is the most used tool. Staff and principal engineers are the heaviest agent users. Leaders are more positive than engineers.
- Interpretation (mine): heaviest use by the most senior engineers is consistent with the view that agents reward existing judgment. This is not proof.

### 1.5 The one strong counter-study

**METR, randomized trial of experienced open-source developers (July 2025, arXiv 2507.09089).** https://arxiv.org/abs/2507.09089

- Study: 16 developers, 246 tasks in large, mature repositories they knew. With early-2025 AI tools (mostly Cursor with Claude 3.5/3.7 Sonnet) they took 19% longer.
- Study: before the trial they forecast a 24% speedup. Afterwards they still believed they had been 20% faster.
- This is pre-agent-era tooling and a narrow setting. Its lasting lesson is about self-assessment: developers misjudged their own speed in both directions.

---

## 2. Hiring, interviews and job expectations

All of this is company policy or reporting, not evidence that the new formats predict job performance.

**Canva (June 2025).** "Yes, you can use AI in our interviews." https://canva.dev/blog/engineering/yes-you-can-use-ai-in-our-interviews

- Policy: backend, frontend and ML candidates are expected to use Copilot, Cursor, Claude or similar. An "AI-Assisted Coding" interview replaced the computer science fundamentals screen.
- What they assess (company statement): judging when and how to use AI, breaking down "complex, ambiguous requirements", making sound technical decisions, spotting and fixing problems in AI-generated code, and checking that output meets production standards.
- Reporting (The Register, https://www.theregister.com/2025/06/11/canva_coding_assistant_job_interviews/): successful candidates did not just accept what the AI produced.
- Canva says early results give "strong predictive signals" but publishes no data. Unknown.

**Meta (pilot from mid to late 2025).** https://hellointerview.com/blog/meta-ai-enabled-coding and https://coderpad.io/blog/hiring-developers/ai-in-the-interview-is-not-cheating-it-is-the-job-according-to-meta/ (secondary)

- Reporting: one onsite coding round is replaced by an AI-enabled round in CoderPad with a choice of models. Candidates reportedly get a multi-file codebase with partial features, failing tests and bugs.
- Implied skills: navigating unfamiliar code, using tests to find bugs, directing an assistant, and judging its output.
- Scope and rollout details vary across reports. Treat as unconfirmed beyond "a pilot exists".

**interviewing.io survey via Pragmatic Engineer (September 2025).** https://newsletter.pragmaticengineer.com/p/the-pulse-146 (secondary)

- Survey: 81% of Big Tech interviewers said they had suspected candidates of using AI to cheat.
- Reporting: startups are replacing algorithm puzzles and take-homes with AI-assisted, screen-shared interviews. Big Tech has changed less.

**Shopify (Tobi Lütke memo, April 2025).** https://www.tomshardware.com/tech-industry/artificial-intelligence/shopify-ceo-teams-must-prove-ai-cant-do-a-task-before-asking-for-new-hires-resources

- Policy: "Reflexive AI usage is now a baseline expectation at Shopify." AI use questions added to performance and peer reviews. Teams must show why AI cannot do the work before asking for headcount.
- Note: this sets an expectation of use, not a definition of the higher skills. It is evidence of pressure, not of what works.

**Early-career labour data.** Brynjolfsson, Chandar and Chen, "Canaries in the Coal Mine?" (Stanford, August 2025). https://digitaleconomy.stanford.edu/publications/canaries-in-the-coal-mine/

- Data (payroll, observational): employment of software developers aged 22 to 25 fell nearly 20% from its late-2022 peak by July 2025, while older developers held steady.
- Causation is debated. Relevance here: if fewer juniors get hired to learn on the job, skill growth has to happen while building with agents. That raises the stakes for training during the build.

**What the hiring changes point to (my synthesis, opinion).** Interviews that allow AI now test: decomposing a vague problem, reading unfamiliar code, finding defects in generated code, judging production readiness, and explaining your solution. These are the same skills practitioners name below.

---

## 3. The skills, with evidence

Strength rating, for this angle:

- **Strong**: many independent practitioners agree, and at least one study or large survey points the same way.
- **Moderate**: broad practitioner agreement, survey support, little or no study evidence.
- **Weak**: a few voices, or mostly my inference.

### Skill 1. Verification: proving the change works

- What it is: running the code, exercising the change, checking edge cases, and demanding evidence (commands, output, screenshots) from the agent. Making sure tests would fail if the change were reverted.
- Opinion: Willison (Dec 2025), Anthropic Claude Code docs, Böckeler, Beck, Thoughtworks Radar all put this first.
- Survey: Stack Overflow 2025: 66% cite "almost right" output as their top frustration, 45.2% say debugging AI code takes longer.
- Survey: DORA 2025 links AI use to more instability.
- Study: Anthropic internal report (interviews) shows engineers delegate what is easy to verify. Verification cost decides what can be delegated.
- Strength: strong.

### Skill 2. Reading and reviewing agent output

- What it is: reading diffs critically, at volume, against intent. Catching code that is "smart in the dangerous way". Reviewing specs and plans, not just code.
- Opinion: Osmani (review as a core skill), Willison (review culture), Thoughtworks (larger change sets are harder to review), Böckeler (review burden moves to specs), Anthropic interviews ("the skill to meaningfully review AI's work will take longer").
- Study: Anthropic skill-formation RCT measured code reading as one of the skills that drops when people lean on AI.
- Hiring: Canva and Meta test spotting and fixing defects in AI code.
- Strength: strong.

### Skill 3. Specifying intent and decomposing problems

- What it is: saying what "done" means before the agent starts. Breaking vague requirements into checkable pieces. Writing a short spec, separating what the system must do from how.
- Opinion: Anthropic docs (specific prompts, interview-me-then-SPEC.md), Willison (plan first), Böckeler ("correctness is outside any sensor's remit if the human didn't clearly specify"), Thoughtworks (spec-driven development on the Radar).
- Counter-opinion: Böckeler warns that heavy specs are overkill for small changes. Sizing the spec is part of the skill.
- Hiring: Canva tests breaking down "complex, ambiguous requirements".
- Strength: moderate.

### Skill 4. Context and harness engineering

- What it is: shaping what the agent sees and what checks it runs: project instruction files, rules, tests, linters, hooks, CI. Turning a repeated failure into a permanent guard.
- Opinion: OpenAI harness engineering post, Böckeler harness article, Thoughtworks Vol. 34, Anthropic docs (deterministic controls vs instructions the model may ignore), Willison (tests and automation let agents "fly").
- Survey: DORA capabilities include AI-accessible internal data and quality internal platforms.
- Strength: moderate. This is a new practice. Little outside data yet.

### Skill 5. Keeping a mental model of the system (avoiding cognitive debt)

- What it is: still being able to explain how and why the system works when you did not type it. Keeping the design rationale written down.
- Opinion: Storey (cognitive and intent debt), Willison (lost his own mental model), Thoughtworks Vol. 34, Karpathy (atrophy).
- Study: Anthropic RCT: AI users scored 17% lower on conceptual understanding, debugging and code reading of the library they just used.
- Strength: moderate to strong. The RCT is small and short-term but points the same way as the practitioners.

### Skill 6. Design, architecture and "taste"

- What it is: structural decisions, choosing boundaries, deciding which technical debt is acceptable, rejecting over-engineering.
- Opinion: Beck (persona prompting did not change structure), Anthropic interviews (engineers keep high-level design), Böckeler (agent has no organisational memory), Osmani (engineer owns architecture), Anthropic docs (an unconstrained reviewer pushes extra abstraction).
- Usage data: Anthropic design/planning use of Claude Code rose from 1.0% to 9.9% in six months, so agents are moving into this area too.
- Strength: moderate.

### Skill 7. Delegation judgment: what to hand off, how much autonomy, what batch size

- What it is: deciding which tasks to give an agent, at what autonomy, in what size of change, and when to take over.
- Opinion: Karpathy (autonomy slider, small chunks), Willison (judgment about what to outsource), Anthropic interviews (delegate what is easy to verify), Canva (judging when and how to use AI).
- Survey: DORA names working in small batches as a capability that amplifies AI's benefit. Anthropic survey: most can fully delegate only 0 to 20% of work.
- Strength: moderate.

### Skill 8. Debugging and diagnosis

- What it is: finding the real cause when agent output fails, rather than re-prompting until symptoms go away.
- Study: Anthropic RCT: debugging showed the largest drop for AI users.
- Survey: Stack Overflow: 45.2% say debugging AI code takes longer.
- Opinion: Anthropic docs (fix root causes, do not suppress errors), Anthropic interviews (loss of learning from hands-on debugging).
- Hiring: Meta's AI round reportedly includes bugs and failing tests.
- Strength: moderate to strong.

### Skill 9. Calibrated trust and self-assessment

- What it is: knowing when you are over-trusting the agent, and checking your own sense of speed and quality against facts.
- Study: METR: developers believed they were 20% faster while measured 19% slower.
- Survey: Stack Overflow: 46% distrust, only 3.1% highly trust. DORA: 30% little or no trust.
- Opinion: Thoughtworks "complacency with AI-generated code" (Hold), citing the Microsoft finding that AI-driven confidence can reduce critical thinking.
- Strength: strong.

### Skill 10. Learning on purpose while using the agent

- What it is: asking the agent to explain, asking follow-up questions, predicting before reading, and sometimes doing parts by hand, so the build also teaches.
- Study: Anthropic RCT: three of six interaction patterns, the ones with active engagement, preserved learning.
- Opinion: Anthropic interviews (deliberate practice without Claude), Karpathy (noticing atrophy).
- Survey: Stack Overflow: 63.2% of agent users say agents sped up their learning about new tech or codebases. Note the tension with the RCT: people feel they learn faster, the test shows they learned less. Both can be true for different kinds of learning.
- Context: Stanford payroll data suggest fewer junior roles, so on-the-job learning with agents matters more.
- Strength: moderate.

### Skill 11. Owning outcomes: user value, security, accountability

- What it is: keeping the user problem central, judging security and operational risk, and taking responsibility for what ships.
- Survey: DORA: user-centric teams gain from AI, teams without user focus lose. Stack Overflow: most developers do not plan to hand deployment, monitoring or planning to AI.
- Opinion: Willison ("a computer cannot be held accountable"), Anthropic security engineer quote, Thoughtworks Vol. 34 (zero trust, defense in depth for agents), Osmani (enforce security and maintainability before merge).
- Strength: moderate for user focus (survey), weak to moderate for the rest (opinion).

---

## 4. Where sources disagree or are uncertain

- **Will these skills stay human?** Anthropic usage data shows agents moving into design and planning. Some Anthropic engineers have "very low confidence" about which skills will matter. Treat the list as current, not permanent.
- **Do people need to keep writing code by hand?** Karpathy and some Anthropic staff report atrophy and some practise without AI. Others say the skill comes back when needed. No study measures long-term recovery. Unknown.
- **How much spec is enough?** Thoughtworks lists spec-driven development, but Böckeler found the tools heavy and agents still ignoring specs.
- **Is review the bottleneck or should agents review agents?** Anthropic docs and Karpathy suggest a fresh-context AI reviewer. Willison and Thoughtworks insist the human still owns proof. Both seem to agree a human must see evidence.
- **Productivity numbers conflict.** Anthropic staff self-report about 50% gains. DORA respondents over 80% say productivity improved. METR measured a 19% slowdown in early 2025. These measure different things in different settings. The true effect for agent-era tools is unknown.

---

## 5. Moments in a build where each skill can be trained

These are design suggestions drawn from the practices above. They are opinion, not tested interventions.

| Skill | Moment in an agent build |
|---|---|
| Verification | Agent says "done". Ask the user what command or check would prove it, before showing the agent's own test output. |
| Review | A diff arrives. Ask the user to name the riskiest hunk and why, then compare with a fresh-context review. |
| Specification | Before the first prompt of a task, ask for one sentence on what "fixed" looks like and one edge case. |
| Harness | The same correction is given a second time. Prompt the user to turn it into a rule, test or hook. |
| Mental model | After a merge, ask the user to explain in two sentences how the changed part now works, without looking. |
| Design | Agent proposes a new abstraction or dependency. Ask whether it is needed and what the simpler option is. |
| Delegation | A large task is about to be handed off. Ask the user to split it into the smallest verifiable step. |
| Debugging | A test fails after an agent change. Ask the user to state a hypothesis for the cause before re-prompting. |
| Calibrated trust | End of session. Show time spent and rework counts against the user's own estimate. |
| Deliberate learning | Agent uses an unfamiliar library or pattern. Offer "explain this before I continue" or "predict what this does". |
| Ownership | Change touches auth, data, money or deploy. Require the user to state the risk and the rollback. |

---

## 6. Source list

Tool makers
- Anthropic, How AI is transforming work at Anthropic (Dec 2025): https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- Anthropic, How AI Impacts Skill Formation (Jan 2026), coverage: https://infoq.com/news/2026/02/ai-coding-skill-formation/
- Anthropic, Claude Code best practices: https://code.claude.com/docs/en/best-practices
- OpenAI, Harness engineering (Feb 2026): https://openai.com/index/harness-engineering/

Thoughtworks and martinfowler.com
- Radar, Complacency with AI-generated code: https://www.thoughtworks.com/radar/techniques/complacency-with-ai-generated-code
- Radar Vol. 34 coverage (Apr 2026): https://itwire.com/business-it-news/data/as-ai-accelerates-software-complexity,-thoughtworks-technology-radar-urges-a-return-to-engineering-fundamentals-to-combat-cognitive-debt.html
- Böckeler, Harness engineering (Apr 2026): https://martinfowler.com/articles/harness-engineering.html
- Böckeler, Understanding spec-driven development (Oct 2025): https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html

Practitioners
- Willison, Vibe engineering (Oct 2025): https://simonwillison.net/2025/Oct/7/vibe-engineering/
- Willison, Code proven to work (Dec 2025): https://simonwillison.net/2025/Dec/18/code-proven-to-work/
- Willison, Cognitive debt (Feb 2026): https://simonwillison.net/2026/Feb/15/cognitive-debt
- Storey, Triple Debt Model (2026): https://www.alphaxiv.org/abs/2603.22106
- Karpathy coverage (Jan 2026): https://the-decoder.com/former-tesla-ai-chief-andrej-karpathy-now-codes-mostly-in-english-just-three-months-after-calling-ai-agents-useless/
- Beck, Pragmatic Engineer podcast (Jun 2025): https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent
- Beck, Taming the Genie: https://newsletter.kentbeck.com/p/taming-the-genie-like-kent-beck
- Osmani, Beyond Vibe Coding (2025): https://www.oreilly.com/library/view/beyond-vibe-coding/9798341634749/
- Kim and Yegge, Vibe Coding (Oct 2025): https://bookshop.org/p/books/vibe-coding-building-production-grade-software-with-genai-chat-agents-and-beyond-gene-kim/b6e53e37eeba8cac

Surveys and studies
- DORA 2025 report: https://dora.dev/research/2025/dora-report/
- Google summary of DORA 2025: https://blog.google/technology/developers/dora-report-2025/
- DORA AI Capabilities Model: https://cloud.google.com/blog/products/ai-machine-learning/introducing-doras-inaugural-ai-capabilities-model
- Stack Overflow 2025 AI: https://survey.stackoverflow.co/2025/ai
- Pragmatic Engineer AI tooling 2026: https://newsletter.pragmaticengineer.com/p/ai-tooling-2026
- METR RCT (Jul 2025): https://arxiv.org/abs/2507.09089
- Stanford, Canaries in the Coal Mine (Aug 2025): https://digitaleconomy.stanford.edu/publications/canaries-in-the-coal-mine/

Hiring
- Canva (Jun 2025): https://canva.dev/blog/engineering/yes-you-can-use-ai-in-our-interviews
- The Register on Canva: https://www.theregister.com/2025/06/11/canva_coding_assistant_job_interviews/
- Meta AI-enabled round: https://hellointerview.com/blog/meta-ai-enabled-coding
- interviewing.io via Pragmatic Engineer: https://newsletter.pragmaticengineer.com/p/the-pulse-146
- Shopify memo coverage: https://www.tomshardware.com/tech-industry/artificial-intelligence/shopify-ceo-teams-must-prove-ai-cant-do-a-task-before-asking-for-new-hires-resources
