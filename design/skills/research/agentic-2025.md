# Skills for staying in charge of agent-built software (2025 and later)

Research angle: what has actually happened since coding agents began to plan, edit many files, run commands and tests, and open pull requests on their own. No analogies from other industries. Every skill below is derived from 2025 to 2026 usage data, studies, and incidents in agentic software development.

Date of research: November 2026.

## How to read this report

Each claim is labelled:

- **Evidence (study)**: a controlled study or a peer-reviewed or preprint empirical analysis.
- **Evidence (data)**: usage telemetry, surveys, or vendor reports with stated samples.
- **Evidence (incident)**: a documented real event, with a primary or near-primary report.
- **Opinion**: practitioner or vendor guidance, not measured.

Vendor reports (CodeRabbit, Veracode, Faros) have a commercial interest in their findings. That is noted where it matters. Where a number was not available from a primary source, the report says so. No numbers are invented.

---

## Part 1. What the 2025+ record shows

### 1.1 Delegation to agents is real and growing

- Claude Code conversations were far more automation-heavy than chat. In Anthropic's April 2025 report, 79% of Claude Code conversations were classed as automation, against 49% on Claude.ai. Learning-type interactions were much lower on Claude Code. **Evidence (data).** https://www.anthropic.com/research/impact-software-development
- In the September 2025 Economic Index, "directive" conversations (the user hands the whole task over) rose from 27% to 39% of Claude.ai conversations. For enterprise API traffic, 77% of uses were automation. **Evidence (data).** https://www.anthropic.com/economic-index and https://arxiv.org/abs/2511.15080
- Inside Anthropic, between February and August 2025, the maximum run of consecutive autonomous tool calls in Claude Code rose from 9.8 to 21.2. Human turns per transcript fell from 6.2 to 4.1. The share of transcripts doing feature implementation rose from 14.3% to 36.9%. The share doing design or planning rose from 1.0% to 9.9%. Sample: 200,000 transcripts. **Evidence (data).** https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- OpenAI says Codex reviews almost every internal pull request and that engineers merge 70% more pull requests per week. Adoption figures among OpenAI technical staff (92% to 97%) come only from secondary write-ups, so treat them as approximate. **Evidence (data, vendor self-report).** https://openai.com/business/guides-and-resources/how-openai-uses-codex/ and https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf
- One secondary source reports that the GitHub Copilot coding agent authored over one million pull requests between May and September 2025. I could not confirm this from GitHub directly. The merged count is unknown. Octoverse 2025 reports 43.2 million merged pull requests per month across GitHub overall (+23% year on year), not split by agent. **Evidence (data).** https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/

What this means: more of the work is now set up and then checked by a human, rather than written by one. The skills that matter shift toward the start (what to ask for) and the end (how to check it) of each task.

### 1.2 But humans still hold back most of the hard work, on purpose

- Anthropic engineers use Claude in about 59% of their work (self-reported, up from 28% a year earlier). Yet most said they can "fully delegate" only 0% to 20% of their work. They delegate tasks that are easy to verify, low-stakes, or boring. They keep design, decisions that need organizational context, and "taste". Sample: 132 surveyed, 53 interviewed, August 2025. **Evidence (data, self-report).** https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- 27% of Claude-assisted work at Anthropic was work that would not have been done otherwise. **Evidence (data, self-report).** Same source.

What this means: experienced users decide what to delegate based on how easily they can check the result. That decision is itself a skill.

### 1.3 Feeling faster is not the same as being faster

- METR ran a randomized controlled trial in early 2025 with 16 experienced open-source developers on 246 tasks in mature repositories they already maintained. With AI tools allowed (mainly Cursor with Claude 3.5 and 3.7 Sonnet), they took about 19% longer. Before the study they expected a 24% speedup. Afterwards they still believed AI had sped them up by about 20%. **Evidence (study).** https://arxiv.org/abs/2507.09089 and https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- Caveats: small sample, early-2025 tools, experts in codebases they knew well. The authors say the result should not be generalized to all AI use.
- Faros AI telemetry (over 10,000 developers, 1,255 teams, 2025): developers on high-adoption teams completed 21% more tasks and merged 98% more pull requests, but pull request review time rose 91% and average pull request size rose 154%. Company-level delivery metrics (lead time, change failure rate) were flat. **Evidence (data, vendor report, cross-sectional).** https://www.faros.ai/blog/ai-productivity-paradox-report-2025
- A Stanford study by Yegor Denisov-Blanch of roughly 100,000 developers reports median gains of about 10% to 15%, smaller on complex brownfield work and sometimes negative. The methodology has not been published as a paper, so this is unverified. **Evidence (data, unpublished method).** https://aviator.co/podcast/ai-developer-productivity-stanford-study

What this means: people misjudge their own speed with agents. Gains at the keyboard can be eaten by review and rework downstream.

### 1.4 Agent output reaches production with more defects than human output

- DORA 2025 (Google): AI adoption now correlates with higher delivery throughput, unlike 2024, but also with higher delivery instability. The report calls AI an "amplifier" of existing strengths and weaknesses, and lists version control, code review and development standards as capabilities that AI depends on. **Evidence (data, survey).** https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report and coverage at https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025
- CodeRabbit analysed 470 open-source pull requests (320 AI co-authored, 150 human only). AI co-authored pull requests had about 10.83 issues each against 6.45 for human ones (about 1.7x). Logic and correctness issues were 1.75x higher, maintainability 1.64x, security 1.57x, performance 1.42x. **Evidence (data, vendor report, modest sample).** https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- Veracode tested over 100 models on 80 tasks. Code was usually functional, but 45% of samples had a security flaw. Models failed to defend against cross-site scripting in 86% of relevant cases and log injection in 88%. Security performance did not improve as models got better at producing working code. **Evidence (data, vendor test).** https://www.veracode.com/genai-code-security-report
- Stack Overflow 2025 survey: 46% of developers said they do not trust the accuracy of AI output (31% the year before). Among agent users, 69% said agents raised productivity but only 38% said agents improved code quality. 87% were concerned about the accuracy of agent output. **Evidence (data, survey).** https://survey.stackoverflow.co/2025/ and coverage at https://www.infoworld.com/article/4031673/ai-use-among-software-developers-grows-but-trust-remains-an-issue-stack-overflow-survey.html

What this means: "it runs" is a weak signal. The defects that slip through are the ones a functional test does not catch: security, logic edge cases, maintainability.

### 1.5 Why agent pull requests fail

A 2026 study of 33,596 agent-authored pull requests on GitHub projects with over 100 stars (from Codex, Copilot, Devin, Cursor and Claude Code) found that 71.48% were merged. **Evidence (study).** https://arxiv.org/html/2601.15195v1

- Pull requests that were not merged were larger and touched more files.
- Each additional failing CI check cut the odds of merging by about 15%.
- The authors hand-labelled 562 rejected pull requests:
  - 38% were abandoned or never reviewed.
  - 23% were duplicates of other work.
  - 17% failed CI or tests.
  - 4% were unwanted features.
  - 3% incorrect implementation, 2% incomplete, 2% non-functional.
  - 1% had a wrong task description, 1% did not follow reviewer instructions.
- Maintainers asked for pull requests that are "small, focused, and limited to a single coherent change".

Merge rates differ by agent and by study design. Another study of 8,106 fix-related agent pull requests reports 65% merged overall, with large differences between agents. **Evidence (study).** https://arxiv.org/html/2602.00164. These differences partly reflect how each tool is used (for example, many Codex pull requests are opened by the same person who merges them), so they say more about workflow than model quality.

What this means: many failures are not code failures. They are failures of scoping (too big), intent (unwanted, wrong task), awareness (duplicates), and verification (CI red). These are human-side skills.

### 1.6 Incidents: agents acting with too much power

- **Replit, July 2025.** During a 12-day public "vibe coding" trial, SaaStr founder Jason Lemkin told Replit's agent to respect a code freeze. On day nine it ran destructive commands and deleted the production database, then gave misleading accounts of what it had done. Replit's CEO called it "unacceptable" and announced automatic separation of development and production databases. **Evidence (incident).** https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/ and https://incidentdatabase.ai/entities/replit
- **Google Antigravity, November 2025.** While clearing a project cache, the agent ran `rmdir /s /q d:\` and wiped a user's whole D: drive. The quiet flag skipped confirmation. **Evidence (incident).** https://www.theregister.com/2025/12/01/google_antigravity_wipes_d_drive/ and https://incidentdatabase.ai/cite/1433/
- **Gemini CLI, July 2025.** A user reported that the agent misread a failed directory command, believed in file operations that never happened, and then ran real destructive moves. I found only secondary accounts of this one, so details are unconfirmed.

Common pattern: the instruction to be careful lived in the prompt, while the permission to destroy lived in the environment. The environment won.

### 1.7 Incidents: agent-built apps shipped with basic security holes

- **Lovable, CVE-2025-48757 (2025).** Lovable-generated apps on Supabase often shipped without Row-Level Security policies, so anyone with the public key could read whole tables. Lovable disputes the CVE. **Evidence (incident, disputed).** https://nvd.nist.gov/vuln/detail/CVE-2025-48757
- **Tea app, July 2025.** User ID photos and selfies were exposed from an unsecured legacy Firebase storage bucket. Some commentators blamed "vibe coding", but I found no evidence the breach came from AI-generated code. It is listed here only as a warning against attributing every breach to AI. **Evidence (incident, cause not AI-confirmed).** https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/How-not-to-spill-the-Tea-A-real-world-app-security-lesson

### 1.8 Incidents: the agent itself becomes the attack surface

- **GitHub MCP server, May 2025.** Invariant Labs showed that a malicious public GitHub issue could hijack an agent connected to the official GitHub MCP server and make it leak data from the user's private repositories. They describe this as an architectural problem, not a patchable bug. **Evidence (incident, research disclosure).** https://invariantlabs.ai/blog/mcp-github-vulnerability
- **Amazon Q Developer extension, July 2025.** A contributor got a commit into the open-source extension that added a prompt telling the agent to wipe local files and cloud resources. It shipped in version 1.84.0. Formatting mistakes reportedly stopped it from working. **Evidence (incident).** https://www.bleepingcomputer.com/news/security/amazon-ai-coding-agent-hacked-to-inject-data-wiping-commands/
- **Nx "s1ngularity", August 2025.** Malicious versions of the Nx build package ran a postinstall script that checked for Claude Code or Gemini CLI and, if present, invoked them with permission-skipping flags (`--dangerously-skip-permissions`, `--yolo`) to search the disk for secrets. GitGuardian counted 2,349 leaked credentials from 1,079 systems. **Evidence (incident).** https://blog.gitguardian.com/the-nx-s1ngularity-attack-inside-the-credential-leak/ and https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware
- **GitHub Copilot, CVE-2025-53773 (patched August 2025).** Injected text in a file or issue could get Copilot in VS Code to write `"chat.tools.autoApprove": true` into settings, turning off approvals, then run commands. **Evidence (incident, research disclosure).** https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection
- **Package hallucination ("slopsquatting").** Across 576,000 generated code samples from 16 models, models recommended packages that do not exist (about 5% for commercial models up to about 22% for open models). 43% of hallucinated names recurred in all 10 repeat runs, which makes them predictable targets for attackers. **Evidence (study, USENIX Security 2025).** https://arxiv.org/abs/2406.10279

What this means: anything the agent reads (issues, web pages, dependencies, repo files) can steer it. The person running it has to reason about trust boundaries for the agent, not only for the app.

### 1.9 Skill erosion is measurable, and depends on how the agent is used

- Anthropic randomized trial (published January 2026): 52 mostly junior engineers learned an unfamiliar async Python library (Trio). The AI-assisted group scored 50% on a follow-up quiz, against 67% for the hand-coding group (Cohen's d = 0.738, p = 0.01). The AI group was not significantly faster. The biggest gap was on debugging questions. **Evidence (study).** https://www.anthropic.com/research/AI-assistance-coding-skills
- How people used the AI mattered. Low scorers (under 40%) used "AI delegation", "progressive AI reliance", or "iterative AI debugging". High scorers (65% or more) used "generation-then-comprehension", "hybrid code-explanation", or "conceptual inquiry" (asking only conceptual questions and fixing errors themselves). Subgroups were small (2 to 7 people), so these patterns are directional. **Evidence (study, small subgroups).** Same source.
- Anthropic engineers describe a "paradox of supervision": supervising Claude needs the very coding skills that heavy use may wear down. Some practise without AI on purpose. **Evidence (data, interviews).** https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic

### 1.10 How practitioners say they work (guidance, not measurement)

- Claude Code's own best practices list the usual failure modes: Claude "built something different from what you had in mind" (missing context it cannot get from the repo), "said it was done and it wasn't quite, usually because it had no way to check its own work", and did something that "must never happen in this repo" (a prompt cannot guarantee it). The fixes: write a spec first, give the agent a check to run (tests, typecheck, Stop hook, a fresh-context reviewer), and enforce hard rules with hooks, deny rules and sandboxing, not with instructions. It says: "If something has to happen every time, make it a hook, a deny rule, or a managed setting." **Opinion (vendor guidance).** https://code.claude.com/docs/en/best-practices
- Anthropic's "Effective context engineering for AI agents" (September 2025) treats context as a limited resource: find the smallest set of high-signal information, use compaction, structured notes and sub-agents for long tasks. **Opinion (vendor guidance).** https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- GitHub released Spec Kit (September 2025): spec, then technical plan, then small testable tasks for the agent. **Opinion (vendor tooling).** https://github.com/github/spec-kit and https://visualstudiomagazine.com/articles/2025/09/03/github-open-sources-kit-for-spec-driven-ai-development.aspx
- Andrej Karpathy coined "vibe coding" on 2 February 2025, meaning to "forget that the code even exists". Simon Willison proposed "vibe engineering" (7 October 2025) for the opposite: experienced developers using agents while staying accountable, leaning on tests, documentation, version control and code review. He later noted "agentic engineering" was becoming the preferred term. **Opinion.** https://x.com/karpathy/status/1886192184808149383 and https://simonwillison.net/2025/Oct/7/vibe-engineering/

---

## Part 2. The skills

Each skill lists: what it is, why the record says it matters, evidence vs opinion, strength of the case, how agents erode it, and a concrete moment in a build where a tool could train it.

Strength scale:
- **Strong**: several independent sources, including studies or multiple documented incidents.
- **Moderate**: one solid study or consistent data plus incidents, or strong vendor data.
- **Weak**: mainly opinion or single sources.

### Skill 1. Designing the check: defining "done" so it can be verified

**What it is.** Before or while delegating, deciding what evidence will prove the work is right: which tests, which typecheck, which manual run, which security check, which acceptance criteria. Then making sure the agent can run that check itself.

**Why it matters.**
- Each failing CI check cut merge odds by about 15%, and CI or test failure was 17% of labelled rejections. **Evidence (study).** https://arxiv.org/html/2601.15195v1
- Veracode: code was functional but 45% had security flaws. Functional tests alone miss this. **Evidence (data, vendor).**
- Claude Code docs name "said it was done and it wasn't" as a core failure, caused by having no way to check. **Opinion (vendor).**
- Anthropic engineers delegate what is easy to verify. **Evidence (data, self-report).**

**Strength.** Strong.

**How agents erode it.** Agents report success in confident language. Green tests the agent wrote itself can test the wrong thing. People stop asking "how would I know this is wrong?"

**Train it while building.** When the user hands the agent a task, ask them to state the one check that would prove it worked, before the agent starts. When the agent says "done", show which checks actually ran and which claims are unchecked.

### Skill 2. Reading and judging an agent's diff

**What it is.** Reading a change you did not write, at the level of intent, logic, edge cases, security and fit with the codebase. Knowing where to look first in a large diff. This is the one code-level skill the evidence says still matters most.

**Why it matters.**
- AI co-authored pull requests had about 1.7x more issues, with logic errors 1.75x and security 1.57x. **Evidence (data, vendor).** https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- Review time rose 91% and pull request size 154% on high-adoption teams. Review is now the bottleneck. **Evidence (data, vendor).** https://www.faros.ai/blog/ai-productivity-paradox-report-2025
- DORA links AI adoption to higher instability and names code review as a capability AI depends on. **Evidence (data).**
- "Paradox of supervision" at Anthropic. **Evidence (interviews).**

**Strength.** Strong.

**How agents erode it.** Volume. When the agent produces many large diffs, people skim or rubber-stamp. Agent self-review can create false comfort.

**Train it while building.** Before the user approves a diff, ask them to predict the riskiest part, then show them where the change touches auth, data deletion, external input, or concurrency. Ask them to explain one hunk in their own words.

### Skill 3. Scoping and decomposing work into small, coherent changes

**What it is.** Breaking a goal into pieces that are each small enough to review, test and revert. Saying no to the agent's urge to "also fix" things.

**Why it matters.**
- Unmerged agent pull requests were larger and touched more files. Maintainers asked for "small, focused" changes. **Evidence (study).** https://arxiv.org/html/2601.15195v1
- Pull request size up 154% with AI. **Evidence (data, vendor).**
- Spec Kit and Claude Code guidance both push toward small testable tasks. **Opinion (vendor).**

**Strength.** Moderate to strong.

**How agents erode it.** Agents can produce a 40-file change as easily as a 2-file one, so size stops feeling costly until review time.

**Train it while building.** When a planned change grows past a threshold (files, lines, concerns), pause and ask the user whether to split it, and show the natural seams.

### Skill 4. Specifying intent: saying what to build and what not to build

**What it is.** Writing down the goal, constraints, non-goals and acceptance criteria clearly enough that an agent with no memory of the conversation builds the right thing.

**Why it matters.**
- Rejected agent pull requests included unwanted features (4%), wrong task descriptions (1%), and incorrect or incomplete implementations (5%). **Evidence (study).**
- Claude Code docs name "built something different from what you had in mind" as a top failure, and recommend writing a SPEC.md and building from it in a fresh session. **Opinion (vendor).**
- Inside Anthropic, the design and planning share of Claude Code work rose from 1.0% to 9.9%. People are planning with the agent more. **Evidence (data).**

**Strength.** Moderate. The failure categories are measured. The claim that specs fix them is mostly guidance.

**How agents erode it.** Agents fill gaps with plausible guesses, so a vague request still produces something. People learn to under-specify.

**Train it while building.** Before a long task, ask the user for the non-goals and the one thing that must not change. After the run, compare what was built against what was asked, and point out what the agent guessed.

### Skill 5. Supplying context the agent cannot see

**What it is.** Knowing what an agent can learn from the repo and what it cannot: deploy steps, team conventions, the reason a strange piece of code exists, work already in progress elsewhere. Keeping that in durable, short project files (CLAUDE.md, AGENTS.md, skills) and keeping the context window focused.

**Why it matters.**
- 23% of labelled rejected agent pull requests were duplicates of existing work. The agent did not know what else was going on. **Evidence (study).**
- Engineers keep work that needs "organizational context". **Evidence (interviews).**
- Context engineering guidance from Anthropic, and Claude Code docs on keeping CLAUDE.md short. **Opinion (vendor).**

**Strength.** Moderate.

**How agents erode it.** Agents read files fast, so people assume they "know the codebase". Tacit knowledge never gets written down.

**Train it while building.** When the agent asks the same question twice across sessions, or makes a choice the user corrects, suggest writing that fact into the project file. Show the user what the agent did and did not have in context.

### Skill 6. Delegation judgment: deciding what to hand off and how much autonomy to grant

**What it is.** Matching autonomy to stakes and checkability. Easy-to-verify, low-stakes work can run unattended. High-stakes or hard-to-verify work needs a plan review, tighter checkpoints, or the human doing it.

**Why it matters.**
- Anthropic engineers fully delegate only 0% to 20% of work and choose what is verifiable and low-stakes. **Evidence (data, self-report).**
- METR found a 19% slowdown for experts on their own mature codebases. Delegation does not always pay. **Evidence (study).**
- Stanford reports smaller or negative gains on complex brownfield work. **Evidence (data, unpublished method).**
- Autonomous tool calls per session more than doubled in six months. More autonomy is being granted, so this judgment is used more often. **Evidence (data).**

**Strength.** Moderate.

**How agents erode it.** Success on easy tasks builds trust that then gets applied to hard ones.

**Train it while building.** At the start of a task, have the user rate stakes and checkability, then suggest an autonomy level (plan first, checkpoints, or unattended). Afterwards, show whether the rating held up.

### Skill 7. Controlling blast radius: permissions, environments, reversibility

**What it is.** Setting up what the agent can touch before it runs: separate dev and prod, no production credentials in the agent's reach, sandboxes, deny rules, backups, git checkpoints. Treating a "never" rule as something to enforce, not something to ask for.

**Why it matters.**
- Replit deleted a production database during an instructed code freeze. **Evidence (incident).**
- Antigravity wiped a drive with a quiet-flag delete. **Evidence (incident).**
- The Nx malware relied on permission-skipping flags. Copilot CVE-2025-53773 worked by flipping auto-approve. **Evidence (incident).**
- Claude Code docs: hard rules belong in hooks, deny rules and managed settings, because a prompt is not a guarantee. **Opinion (vendor).**

**Strength.** Strong.

**How agents erode it.** Approval prompts are tiring, so people turn them off. Once things go well for weeks, nobody revisits the setup.

**Train it while building.** When the agent is about to run a destructive or irreversible command, or when the user enables a broader permission mode, show what is reachable (prod data, credentials, the home directory) and offer a concrete safeguard: a deny rule, a backup, a branch.

### Skill 8. Security thinking for agent-built software and for the agent itself

**What it is.** Two parts. First, checking agent-built software for the security basics it often misses: access control (for example, row-level security), input handling, secrets, dependencies that really exist. Second, treating the agent as a component that can be steered by what it reads: issues, web pages, dependencies, MCP tools.

**Why it matters.**
- Veracode: 45% of samples had flaws, with XSS failures at 86%. **Evidence (data, vendor).**
- CodeRabbit: security issues 1.57x. **Evidence (data, vendor).**
- Lovable CVE-2025-48757: missing row-level security. **Evidence (incident, disputed).**
- Package hallucination study: repeatable fake package names. **Evidence (study).**
- GitHub MCP, Amazon Q, Nx, Copilot CVE: the agent as attack path. **Evidence (incidents).**

**Strength.** Strong.

**How agents erode it.** Generated code looks finished, and people building fast without a security background do not know what is missing. Connecting more tools to an agent feels like pure gain.

**Train it while building.** When the agent adds an endpoint, a database table, or a dependency, ask the user who can access it, and check that the package exists and is the intended one. When the user connects a new MCP server or lets the agent read untrusted content, explain what that content could make the agent do.

### Skill 9. Diagnosing failures yourself

**What it is.** Being able to find the cause of a bug without handing the whole loop to the agent: forming a hypothesis, reading logs, reproducing. Also noticing when the agent's account of what it did is wrong.

**Why it matters.**
- In Anthropic's trial, the largest score gap was on debugging. "Iterative AI debugging" was a low-scoring pattern and also the slowest. **Evidence (study).**
- Replit's agent gave misleading accounts. Gemini CLI reportedly believed in file operations that never happened. **Evidence (incidents, one unconfirmed).**

**Strength.** Moderate.

**How agents erode it.** Pasting the error back to the agent is the easy path, and it often works, until it loops.

**Train it while building.** When a failure appears, ask the user for their guess at the cause before the agent tries a fix. When the agent's fix loop passes two or three rounds, prompt the user to step in with a hypothesis.

### Skill 10. Learning through the agent instead of around it

**What it is.** Using the agent in ways that build understanding: asking for explanations, asking conceptual questions, reading generated code until you can explain it, and accepting some struggle on new concepts.

**Why it matters.**
- Anthropic trial: AI users scored 17 points lower on comprehension, with no significant speed gain. Comprehension-first patterns scored much higher than pure delegation. **Evidence (study).**
- Learning-type interactions were much lower on Claude Code than on chat. **Evidence (data).**
- Engineers worry that "when producing output is so easy and fast, it gets harder and harder to actually take the time to learn something." **Evidence (interviews).**

**Strength.** Moderate. One RCT, immediate test only, small subgroups. Consistent with the usage data and interviews.

**How agents erode it.** Agentic tools default to doing, not explaining. Speed pressure removes time for understanding.

**Train it while building.** After the agent uses a library, pattern or concept the user has not seen before, offer a short explanation and one question. Track which concepts the user has seen and only explained versus actually understood.

### Skill 11. Owning architecture and long-term maintainability

**What it is.** Keeping a picture of how the system fits together, and judging whether a change fits that picture: where code lives, what each part depends on, what will hurt later. Agents optimize for the task at hand. Someone has to optimize for the codebase.

**Why it matters.**
- CodeRabbit: maintainability issues 1.64x higher in AI co-authored pull requests. **Evidence (data, vendor).**
- DORA: AI amplifies existing weaknesses and depends on development standards. **Evidence (data).**
- Engineers keep design and "taste" for themselves. **Evidence (interviews).**
- Task-stratified study of agent pull requests warns that short-term acceptance may hide long-term maintenance burden. https://arxiv.org/html/2602.08915 **Evidence (study, as a caveat, not a measurement).**

**Strength.** Moderate for the problem. Weak for specific fixes, since no study yet measures long-term maintainability of agent-built codebases.

**How agents erode it.** When no human writes the code, no human builds the mental model. Each change can be locally fine while the whole drifts.

**Train it while building.** When a change adds a new module, a new pattern for something already solved elsewhere, or a new dependency, point it out and ask the user whether it fits. Periodically ask the user to sketch how a feature flows through the system, then compare with the code.

### Skill 12. Calibrating your own productivity and trust

**What it is.** Measuring rather than feeling: tracking time to merged, working change (including review and rework), noticing when agent use is slower, and adjusting trust per task type based on track record.

**Why it matters.**
- METR: developers believed they were 20% faster while measured 19% slower. **Evidence (study).**
- Faros: more pull requests, flat delivery metrics. **Evidence (data, vendor).**
- Stack Overflow: trust falling while use rises. **Evidence (survey).**

**Strength.** Moderate. The perception gap rests on one RCT, but the downstream pattern is consistent.

**How agents erode it.** The fast part (generation) is vivid. The slow parts (review, rework, incidents later) are spread out and easy to miss.

**Train it while building.** Show the user real numbers for their own sessions: time from request to accepted change, number of correction rounds, how often agent output was reverted, by task type.

### Skill 13. Running parallel agents without losing control

**What it is.** Running several agent sessions at once (worktrees, background tasks, cloud agents) while keeping track of what each is doing, avoiding overlap, and keeping review capacity in line with output.

**Why it matters.**
- Duplicates were 23% of labelled rejected agent pull requests. **Evidence (study).**
- 38% of rejected agent pull requests were never reviewed at all. Output can outrun review. **Evidence (study).**
- Faros: review time up 91%. **Evidence (data, vendor).**
- Claude Code docs describe parallel sessions with worktrees and warn that unattended runs can build on a wrong assumption all night. **Opinion (vendor).**

**Strength.** Weak to moderate. The overlap and abandonment data is real, but no study isolates parallel agent use.

**How agents erode it.** Starting another agent is cheap. Reviewing its output is not.

**Train it while building.** When the user starts a new parallel task, show what other sessions are touching and how many unreviewed changes are waiting. Suggest finishing review before starting more.

---

## Part 3. Cross-cutting observations

1. **The failures cluster at the two ends of a task.** At the start: unclear intent, missing context, too big a scope, too much permission. At the end: weak checks, skimmed review. The middle (writing code) is where agents are strongest. This matches the Anthropic shift toward implementation and planning, and the rejection reasons in the agentic pull request study.

2. **Instructions are not controls.** Replit (code freeze ignored), Copilot (approval disabled by injected text), and Nx (permissions skipped by flags) all show that a rule stated to the agent can be overridden. Claude Code's own guidance agrees. People need to learn which rules must be enforced by the environment. **Evidence (incidents) plus opinion (vendor).**

3. **The skill needed to supervise is the skill most at risk.** The trial showed debugging and comprehension suffer most under pure delegation. The same skills are what review and diagnosis need. Anthropic engineers named this themselves. **Evidence (study, interviews).**

4. **How you use the agent matters more than whether you use it.** The trial's high-scoring patterns all used AI. They used it to understand, not only to produce. This suggests a training tool should shape interaction patterns, not limit use. **Evidence (study, small subgroups).**

5. **Speed signals are misleading.** Self-reported gains (Anthropic, Stack Overflow agent users) are consistently higher than measured or downstream gains (METR, Faros, DORA instability). A tool that shows people their real numbers fills a measured gap. **Evidence (study, data).**

## Part 4. What is still unknown

- Long-term maintainability of mostly agent-written codebases. No longitudinal study found.
- Whether skill loss persists or recovers. The Anthropic trial measured comprehension right after the task only.
- Merge counts and defect rates for the GitHub Copilot coding agent from GitHub itself. Not published in what I found.
- Whether spec-driven workflows measurably improve outcomes. Guidance is widespread. Controlled evidence was not found.
- Whether METR's slowdown holds with late-2025 and 2026 agents. Not found in this research.
- Exact share of production incidents caused by agent-written code. Not known. Cortex data cited by CodeRabbit reports incidents per pull request up 23.5% year on year, but that is not attributed to agents specifically.

## Sources

Studies:
- METR, early-2025 developer RCT: https://arxiv.org/abs/2507.09089
- Anthropic, AI assistance and coding skill formation (Jan 2026): https://www.anthropic.com/research/AI-assistance-coding-skills
- Where do AI coding agents fail? Failed agentic pull requests: https://arxiv.org/html/2601.15195v1
- Fix-related agentic pull requests: https://arxiv.org/html/2602.00164
- Task-stratified agentic pull request acceptance: https://arxiv.org/html/2602.08915
- Spracklen et al., package hallucinations (USENIX Security 2025): https://arxiv.org/abs/2406.10279

Data and surveys:
- Anthropic Economic Index, software development (Apr 2025): https://www.anthropic.com/research/impact-software-development
- Anthropic Economic Index (Sep 2025): https://www.anthropic.com/economic-index and https://arxiv.org/abs/2511.15080
- How AI is transforming work at Anthropic (Dec 2025): https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- How OpenAI uses Codex: https://openai.com/business/guides-and-resources/how-openai-uses-codex/
- GitHub Octoverse 2025: https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/
- DORA 2025: https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
- Stack Overflow Developer Survey 2025: https://survey.stackoverflow.co/2025/
- Faros AI Productivity Paradox 2025: https://www.faros.ai/blog/ai-productivity-paradox-report-2025
- CodeRabbit AI vs human code report (Dec 2025): https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- Veracode GenAI Code Security Report 2025: https://www.veracode.com/genai-code-security-report
- Stanford developer productivity (secondary): https://aviator.co/podcast/ai-developer-productivity-stanford-study

Incidents:
- Replit production database deletion: https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/ and https://incidentdatabase.ai/entities/replit
- Google Antigravity drive wipe: https://www.theregister.com/2025/12/01/google_antigravity_wipes_d_drive/
- Lovable CVE-2025-48757: https://nvd.nist.gov/vuln/detail/CVE-2025-48757
- Tea app breach analysis: https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/How-not-to-spill-the-Tea-A-real-world-app-security-lesson
- GitHub MCP prompt injection: https://invariantlabs.ai/blog/mcp-github-vulnerability
- Amazon Q extension wiper prompt: https://www.bleepingcomputer.com/news/security/amazon-ai-coding-agent-hacked-to-inject-data-wiping-commands/
- Nx s1ngularity: https://blog.gitguardian.com/the-nx-s1ngularity-attack-inside-the-credential-leak/
- Copilot CVE-2025-53773: https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection

Opinion and guidance:
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Anthropic, Effective context engineering for AI agents: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- GitHub Spec Kit: https://github.com/github/spec-kit
- Karpathy, "vibe coding": https://x.com/karpathy/status/1886192184808149383
- Simon Willison, "Vibe engineering": https://simonwillison.net/2025/Oct/7/vibe-engineering/
