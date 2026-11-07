# Durable engineering skills when agents write the code

Status: research note, November 2026.
Scope: lasting engineering skills that strong senior and staff engineers use when they are not typing code. Skills for operating AI tools (prompting, context files, permissions, agent settings) are out of scope on purpose. The user asked for skills that are not specific to AI. Every skill below was valuable before coding agents and would stay valuable if the tools changed tomorrow.

## How to read this note

Each claim is labelled:

- **Evidence**: a study, survey or dataset. The source and its limits are named.
- **Opinion**: a practitioner or expert view. It may be well informed, but it is not measured.

Numbers come from the cited source. Where a number is not known, the note says so. Vendor studies are marked as vendor studies, because the vendor sells a product linked to the finding.

## Summary

Cheap code moves the hard part of the job. Writing a correct-looking patch is no longer scarce. Knowing what to build, knowing whether the result is right, and understanding the system well enough to change it safely are now the scarce parts.

The evidence is strongest for four skills:

1. Verification and test strategy.
2. Reading and understanding code and systems.
3. Debugging and diagnosis.
4. Security judgment.

For these, there are controlled studies or large datasets from 2023 to 2026 that show either (a) agent output has defects a human must catch, or (b) heavy delegation weakens the human skill needed to catch them.

The evidence is moderate for problem framing, system design, operating in production and technical writing. Here the support is mostly large surveys, telemetry and strong practitioner agreement, not controlled trials.

The evidence is weak (mostly opinion) for product judgment and data modeling as such. They are widely named by senior practitioners as more important now, but no study measures them directly.

A key finding cuts across all of them: the skill that supervising an agent needs is the same skill that delegating to an agent can erode. Anthropic's internal report calls this the supervision problem. A tool that trains these skills while people build must make them do some of the thinking, not only approve output.

## Cross-cutting evidence

These sources support several skills at once. Later sections refer back to them.

### Skill formation drops when people delegate (Evidence)

Anthropic ran a randomized controlled trial with 52 mostly junior engineers learning an unfamiliar Python library (Trio). The AI group scored 50% on a later quiz, the hand-coding group 67% (Cohen's d = 0.738, p = 0.01). The AI group was not significantly faster (about 23 vs 25 minutes, p = 0.391). The largest gap was on debugging questions. Source: https://www.anthropic.com/research/AI-assistance-coding-skills (paper: arXiv 2601.20245, January 2026).

How people used the AI mattered. Participants who generated code and then asked questions to understand it averaged 86% (n = 2). Those who asked only conceptual questions and fixed errors themselves averaged 65% (n = 7). Those who fully delegated averaged 39% (n = 4), and those who used AI to debug iteratively averaged 24% (n = 4). These subgroups are tiny and the authors say the patterns are not causal.

Limits: one hour, one library, immediate test only. Long-term effects are unknown.

### Supervision needs the skills delegation erodes (Evidence, qualitative)

Anthropic surveyed 132 of its engineers and researchers and interviewed 53 (August 2025). Engineers worried about skill atrophy. Some practise tasks without AI on purpose. One said: "I worry much more about the oversight and supervision problem than I do about my skill set specifically." More than half said they could fully delegate only 0 to 20% of their work. Engineers delegate tasks that are easy to verify and tend to keep design and "taste" work. Source: https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic (December 2025).

Limits: one company, self-report, staff of an AI vendor.

### Perceived speed is not real speed (Evidence)

METR's randomized trial (early 2025) had 16 experienced open-source developers do 246 real tasks on large, mature repositories. With AI allowed they took 19% longer, yet afterwards believed they had been 20% faster. METR named high quality standards and many implicit requirements (documentation, tests, formatting) as likely factors. Source: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/

METR's late-2025 follow-up (57 developers, 800+ tasks) estimated a speedup of 18% for returning participants and 4% for new ones, but every confidence interval included zero, and METR called the data an "unreliable signal" due to selection effects. Source: https://metr.org/blog/2026-02-24-uplift-update/

Takeaway for skills: self-judgement of how well things are going is unreliable. Engineers need external checks (tests, measurements, review) rather than feel.

### Agent output often passes tests but is not acceptable (Evidence)

METR had active maintainers review 296 AI-generated pull requests that the SWE-bench grader scored as correct. Roughly half would not have been merged into main. Source: https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/ (March 2026).

Takeaway: "the tests pass" is not the same as "this is right for this codebase". Judging the difference is a human skill.

### Defect and quality data (Evidence, mixed quality)

- CodeRabbit analysed 470 open-source PRs (320 AI co-authored, 150 human). AI PRs had about 1.7 times more issues (10.83 vs 6.45 per PR), logic and correctness issues about 75% more common, and error-handling gaps nearly twice as common. Vendor study; CodeRabbit sells AI code review and says it cannot guarantee the human PRs were human-only. Source: https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report (December 2025).
- GitClear analysed 211 million changed lines from 2020 to 2024. Moved lines (a sign of refactoring) fell as a share of changes, and in 2024 copy-pasted lines exceeded moved lines for the first time. This is a trend over the period AI tools spread, not proof of cause. Vendor study. Source: https://leaddev.com/software-quality/how-ai-generated-code-accelerates-technical-debt and GitClear's 2025 report.
- DORA 2024: for each 25% increase in AI adoption, estimated delivery stability fell 7.2% and throughput fell 1.5%. Correlational survey data. Source: https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
- DORA 2025 (about 5,000 respondents): AI acts as an amplifier of existing practices. Platform quality correlated with whether teams got value from AI. Secondary reports say the throughput link turned positive while instability remained. Source: https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf
- Faros AI telemetry (over 10,000 developers): more tasks completed and many more PRs merged with AI, but PR review time rose about 91%, with no clear company-level gain. Vendor data; figures on PR size and bugs differ between secondary sources. Source: summarized at https://www.augmentcode.com/guides/ai-productivity-paradox-engineering-delivery (primary report not verified).

### Developers distrust the output and spend time fixing it (Evidence, survey)

Stack Overflow 2025 survey (49,009 responses): 29% trust AI accuracy, down from 40%. 45% named "AI solutions that are almost right, but not quite" as their top frustration. 66% say they spend more time fixing almost-right AI code. 75% would still ask a person when they do not trust the AI. Source: https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here

Limit: respondents are self-selected Stack Overflow users.

### Confidence in the tool lowers critical thinking (Evidence, survey)

Lee et al. (CHI 2025, 319 knowledge workers, Microsoft Research and CMU): higher confidence in generative AI was associated with less critical thinking; higher self-confidence was associated with more. Critical thinking shifted toward verifying information, integrating responses and "task stewardship". Source: https://advait.org/files/lee_2025_ai_critical_thinking_survey.pdf

### The apprenticeship path is narrowing (Evidence, labour data)

Brynjolfsson, Chandar and Chen used ADP payroll data. Workers aged 22 to 25 in the most AI-exposed occupations saw a 13% relative employment decline (later revised to 16%). Employment for the youngest software developers in July 2025 was about 20% below its late-2022 peak. The authors say causes are mixed and the work is early. Source: https://digitaleconomy.stanford.edu/news/canaries-interest-rates-and-timinga-more-on-recent-drivers-of-employment-changes-for-young-workers

Why it matters here: many durable skills are learned by apprenticeship on real work. If fewer juniors are hired, and juniors ask seniors fewer questions (Anthropic report: "more junior people don't come to me with questions as often"), the usual path to these skills weakens. A tool may need to supply some of that practice.

### Code was always only part of the knowledge (Opinion, foundational)

Peter Naur's 1985 essay "Programming as Theory Building" argues that the real product of programming is the programmers' theory of the system: why it is the way it is and how it should change. Code is a partial record. Several 2025 essays apply this to agents, arguing that agents rebuild their theory from scratch each session, so the human must hold the theory. Sources: https://www.seangoedecke.com/programming-with-ai-agents-as-theory-building and https://carsten-j.github.io/2025/12/17/programming-as-theory-building.html

Charity Majors makes the same point in 2026: "The real product of a software team is shared understanding" and "Code becomes precious when it is the only place knowledge lives." Source: https://www.oreilly.com/radar/ai-demands-more-engineering-discipline-not-less/ (July 2026).

### What we know about how expert skill is learned (Evidence, older)

- Deliberate practice matters, but less than often claimed in professions. A meta-analysis of 88 studies found it explained 26% of performance variance in games, 21% in music, 18% in sports, 4% in education and under 1% in professions. Critics dispute how practice was defined. Source: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/ (Macnamara, Hambrick, Oswald, 2014). Implication: in professional work, practice must be tied to real tasks with feedback, not drills alone.
- Developers spend about 58% of their time on program comprehension, and seniors spend a smaller share than juniors. Source: Xia et al., IEEE TSE 2018, https://xin-xia.github.io/publication/TSE17.pdf
- At Google, developers name education (teaching and learning) and keeping norms as main reasons for code review. Study: 12 interviews, 44 survey responses, logs of 9 million changes. Source: https://research.google/pubs/modern-code-review-a-case-study-at-google/ (Sadowski et al., 2018).

## The skills

Each section gives: what it is, why it matters more now, the evidence, how it is learned, and a concrete moment in a build with an agent where it can be practised.

### 1. Verification and test strategy

**What it is.** Deciding what "correct" means for a change, choosing the cheapest checks that would catch the likely failures, and getting real proof that the change works. It includes test design (unit, integration, property, characterization), choosing what to check by hand, and knowing what the tests do not cover.

**Why it matters more now.** When generating code is nearly free, the cost moves to checking it. Engineers in Anthropic's report delegate work "where validation effort isn't large in comparison to creation effort". So the ability to make validation cheap decides how much can be safely delegated.

**Evidence.**
- About half of test-passing agent PRs would not be merged by maintainers (METR, March 2026, link above). Evidence.
- AI PRs had more logic and error-handling issues (CodeRabbit, vendor). Evidence.
- 66% of developers spend more time fixing almost-right AI code (Stack Overflow 2025). Evidence.
- Developers felt 20% faster while being 19% slower (METR 2025). Evidence that feel is not a check.
- Simon Willison: "Your job is to deliver code you have proven to work." He argues that you must have seen the code do the right thing, and that the human is accountable. Source: https://simonwillison.net/2025/Dec/18/code-proven-to-work (December 2025). Opinion.
- Charity Majors: no pull request should be accepted unless the engineer can answer "How will I know if this breaks?" Quoted via https://feeds.simonwillison.net/tags/charity-majors/ (exact original context not verified). Opinion.
- Majors (2026): "Human brains are not good at validation", so humans should design checks that machines run. Opinion.

**How it is learned.** Writing tests before or with code (test-driven development), mutation testing (seeing which bugs your tests miss), code review where reviewers ask "how was this tested?", and incidents that expose untested paths. Kent Beck's "augmented coding" keeps tests and design quality central while an AI writes code (https://tidyfirst.substack.com/). Opinion on method; no controlled study found on which method trains this best.

**Practice moment while building.** Before the agent writes code, the person writes down the acceptance checks and two or three failure cases they expect. After the agent finishes, they compare: which of their cases did the agent's tests cover, and which did it miss? They then try to break the change on purpose before accepting it.

### 2. Reading and understanding code and systems

**What it is.** Building an accurate mental model of code you did not write: data flow, control flow, invariants, side effects, and how a change ripples. Includes reading unfamiliar systems quickly and knowing where to look.

**Why it matters more now.** More of the code in a system is written by something other than the person responsible for it. Engineers in Anthropic's report describe their work moving "70%+ to being a code reviewer/reviser". Reading becomes the main way of staying in charge.

**Evidence.**
- Comprehension already took about 58% of developer time before agents (Xia et al. 2018). Evidence.
- The Anthropic trial tested code reading as a core part of its quiz. Delegators scored lowest; those who asked questions to understand generated code scored highest. Evidence, small subgroups.
- Thoughtworks Technology Radar (April and November 2025) lists "complacency with AI-generated code" as an antipattern and calls for sustained human judgment. Source: https://www.thoughtworks.com/about-us/news/2025/thoughtworks-technology-radar-highlights-genai-s-impact-and-key- . Opinion (expert panel).
- Addy Osmani (Google) argues the developer whose name is on a change is responsible for understanding it, and that AI reliably gets about 70% of the way while the last part stays hard. Source: https://zed.dev/blog/ai-70-problem-addy-osmani . Opinion.
- Majors: if code nobody understands goes to production, it was likely not written to be understandable. Opinion.

**How it is learned.** Code review (Google names education as a main purpose of review), pairing with someone who knows the system, tracing a real request end to end, reading the history (commits, design docs) behind odd code, and explaining code back to someone else.

**Practice moment while building.** After the agent produces a change, the person explains it in their own words before seeing the agent's summary: what it changes, what could break, what it assumes. The tool then points out what they missed. This mirrors the "generation then comprehension" pattern that scored highest in the Anthropic trial.

### 3. Debugging and diagnosis

**What it is.** Going from a symptom to a cause through hypotheses and experiments: reproduce, narrow down, form a theory, test it, confirm the fix explains all the symptoms.

**Why it matters more now.** Agents can make bugs less frequent in the moment but leave people less able to find them later. When an agent's fix fails, someone has to understand why.

**Evidence.**
- In the Anthropic trial, the largest gap between groups was on debugging. The AI group hit fewer errors during the task but did worse at diagnosing problems afterwards. The "iterative AI debugging" pattern scored lowest (24%). Evidence. Quote from the authors: "Cognitive effort, and even getting painfully stuck, is likely important for fostering mastery."
- Osmani reports that asking AI to fix one bug can introduce several new ones. Opinion.
- A critic of spec-first approaches: "If your application crashes at 3 am, you'll still be debugging the actual code, not the Markdown document." Opinion, cited at https://medium.com/@delimiterbob/the-emperors-new-code-hype-vs-reality-of-ai-executable-specs-ff64d961e8ab

**How it is learned.** Being on call, working real bugs from report to fix, writing down hypotheses and what ruled them out, and reviewing others' debugging in incident reviews. Getting stuck and recovering is part of the learning (Anthropic trial). No 2024 or later study found that compares debugging training methods.

**Practice moment while building.** When a test fails or the agent's change breaks something, the tool asks the person for their hypothesis and the next experiment before the agent tries a fix. Afterwards it shows whether the hypothesis was right.

### 4. Security judgment

**What it is.** Seeing where trust boundaries are, what an attacker could control, and which defaults are unsafe. Knowing when a change touches authentication, secrets, input handling or permissions, and needs extra care.

**Why it matters more now.** Generated code often looks correct while being insecure, and using an assistant can make people more confident than they should be.

**Evidence.**
- Perry et al. (ACM CCS 2023): participants with an AI assistant wrote insecure code more often on four of five tasks and were more likely to believe their code was secure. Participants who trusted the AI less wrote code with fewer vulnerabilities. Source: https://arxiv.org/abs/2211.03622 . Evidence.
- Veracode (July 2025, 80 tasks, 100+ models): 45% of generated samples introduced an OWASP Top 10 flaw; security did not improve as syntax accuracy improved. Vendor study. Source: https://www.veracode.com/genai-code-security-report . Evidence.
- OX Security (October 2025, 300+ repositories) describes AI code as functional but lacking architectural and security judgment, and recommends humans own architecture and security oversight. Vendor study; some coverage says it found vulnerabilities at similar rates to humans but reaching production faster. Source: https://www.ox.security/army-of-juniors . Mixed.

**How it is learned.** Threat modelling sessions, security review of real changes, studying past vulnerabilities and incident reports, capture-the-flag and red-team exercises. No 2024 or later study found on which method transfers best.

**Practice moment while building.** When a change touches input handling, auth or secrets, the tool asks the person to name the trust boundary and one way it could be abused, before showing a security review of the change.

### 5. Problem framing and requirements

**What it is.** Turning a vague need into a clear problem: who it is for, what success looks like, what is out of scope, which constraints are real, and which questions must be answered before building.

**Why it matters more now.** An agent will build whatever it is told, quickly. A poorly framed problem now produces a lot of wrong software fast. Implicit requirements are where agents fail.

**Evidence.**
- METR (2025) named implicit requirements (documentation, tests, formatting, unstated standards) as a likely reason AI slowed experienced developers down. Evidence (factor analysis within one study).
- Ambig-SWE (CMU, 2025) built underspecified versions of real software tasks. Models had trouble telling well-specified instructions from underspecified ones, and results depended on the quality of clarifying questions. Source: https://arxiv.org/abs/2502.13069 . Evidence. (This is about agents, but it shows the gap a human must fill.)
- Sean Grove (OpenAI, 2025) argues that specifications, not code, are the main artifact, and that "the person who communicates the best will be the most valuable programmer". Source: https://ai.engineer/talks/specifications-are-the-new-code . Opinion.
- Birgitta Böckeler (Thoughtworks, October 2025) reviewed spec-driven tools and found all were "spec-first" but few kept the spec as a living artifact. Source: https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html . Opinion and hands-on review.

**How it is learned.** Writing problem statements and design docs that others review, talking to users, sitting in on support, having requirements questioned in design review, and looking back at projects where the wrong thing was built.

**Practice moment while building.** Before the agent starts, the person writes a short brief: the goal, two non-goals, the acceptance checks, and the open questions. The tool flags gaps (for example, no error case, no stated user) and asks the person to resolve them, not the agent.

### 6. System design and architecture

**What it is.** Choosing the structure of a system: boundaries between parts, interfaces, where state lives, how it scales and fails, and how it will change over time.

**Why it matters more now.** Agents optimise locally, one change at a time. Without a human holding the overall shape, systems drift: duplication grows, refactoring falls, and structure decays.

**Evidence.**
- GitClear: refactoring (moved code) fell and copy-paste rose over 2020 to 2024 as AI tools spread. Vendor, correlational. Evidence.
- Kent Beck: today's AI assistants lack design taste; for example, they keep adding lines to an already giant function. Source: https://kentbeck.com/ and his "Tidy First?" newsletter. Opinion.
- In Anthropic's report, engineers keep "high-level thinking and design" for themselves. Opinion and self-report.
- DORA 2025: AI amplifies what is already there; good platforms and practices get more benefit. Evidence (survey), indirect.
- OX Security recommends humans own architecture. Vendor opinion.

**How it is learned.** Writing design docs and getting them reviewed (Google's design-doc practice: short documents that explain trade-offs before code is written, https://simonwillison.net/2020/Aug/7/design-docs-google), architecture decision records, reviewing others' designs, studying how real systems failed, and living with the consequences of your own designs over months.

**Practice moment while building.** When a task touches more than one module or adds a new component, the tool asks the person to sketch the boundaries and interfaces first and to say where the new code belongs. After the agent works, it compares the result with the sketch and highlights drift (new duplication, a new dependency across a boundary).

### 7. Trade-off decisions

**What it is.** Choosing between options that each cost something: speed vs safety, simple now vs flexible later, build vs buy, consistency vs availability. Making the choice explicit and recording why.

**Why it matters more now.** Agents can produce several working options quickly. That raises the number of choices a human must judge. The cost of a wrong choice is often not visible in the code.

**Evidence.**
- No direct study found that measures trade-off skill with agents. Unknown.
- Kent Beck's work on the economics of design ("Tidy First?") treats when to tidy and when to ship as an explicit trade-off. Opinion.
- Design docs at Google are built around recording trade-offs considered. Practitioner account (Malte Ubl). Opinion.

**How it is learned.** Writing decision records with options and reasons, design review, and later revisiting decisions to see which assumptions held.

**Practice moment while building.** When the agent proposes an approach, the tool asks for one alternative and the main cost of each, and saves a one-paragraph decision note with the change. Weeks later it can show the note again when that code changes.

### 8. Operating systems in production

**What it is.** Knowing how software behaves under real load and real failure: observability, safe rollout, rollback, capacity, on-call, and incident response.

**Why it matters more now.** More code reaches production faster, and some of it nobody has read closely. Production becomes the place where correctness is finally tested.

**Evidence.**
- DORA 2024: more AI adoption correlated with lower delivery stability. DORA 2025: instability remained. Evidence (survey, correlational).
- Faros: PR review time up about 91% with AI. Vendor telemetry. Evidence that review and release, not writing, become the bottleneck.
- Majors (2026): "Production is not what happens after development is over, production is a stage of development." She argues for behavioural tests, capture and replay, and observability. Opinion.
- Majors (2025): engineers will ship code they never looked at, so observability is how they will know what it does. Source: https://newsletter.pragmaticengineer.com/p/observability-the-present-and-future . Opinion.

**How it is learned.** On-call rotations, blameless post-incident reviews (Google SRE book: https://sre.google/sre-book/postmortem-culture/ ), game days and chaos exercises, and reading other teams' incident reports.

**Practice moment while building.** Before merging, the tool asks: what signal will show this is broken in production, and how do you roll it back? If the change adds no log, metric or alert for a new failure path, the tool points that out.

### 9. Data modeling

**What it is.** Choosing how data is shaped and stored: entities, relationships, keys, invariants, migrations, and how the model will change as the product changes.

**Why it matters more now.** Data models are expensive to change once real data exists. Code can be regenerated; a bad schema with years of data cannot. So this is one of the places where cheap code does not help.

**Evidence.**
- No 2024 or later study found that measures data modeling with agents. Unknown.
- Majors: code becomes a "disposable cache" while durable things (specs, behaviour, data) keep value. Opinion, indirect.
- Thoughtworks Radar 2025 stresses "data product thinking". Opinion, indirect.

**How it is learned.** Schema review, writing and reviewing migrations, working through a painful data migration, and studying how a model held up as requirements changed.

**Practice moment while building.** When the agent proposes a schema change or migration, the tool asks the person to state the invariants (what must always be true about this data) and how existing rows will be migrated, before accepting.

### 10. Product judgment

**What it is.** Knowing what is worth building, for whom, and what "good enough" means for users. Spotting when a technically correct change is the wrong thing to ship.

**Why it matters more now.** When building is cheap, deciding what to build is a larger share of the value. It is also a skill agents do not have context for.

**Evidence.**
- No direct study found. Unknown.
- Anthropic report: engineers keep "taste" tasks for themselves. Self-report.
- A 2026 practitioner essay argues customer impact, not code output, is what counts for staff engineers. Opinion, weak source.

**How it is learned.** Talking to users, watching usage data, owning a feature end to end, working closely with product managers and designers, and reviewing launches that missed.

**Practice moment while building.** At the start of a task, the tool asks who the change is for and how the person will know it helped. At the end it asks whether the result still matches that answer.

### 11. Technical communication and writing

**What it is.** Explaining a problem, design, change or incident clearly enough that others can review it, decide on it and maintain it later. Includes design docs, PR descriptions, incident write-ups and decision records.

**Why it matters more now.** Specs and briefs now steer the work, and reviewers face more and larger changes. A clear description is how a reviewer can keep up. Written records are also where shared understanding can live outside code.

**Evidence.**
- Faros: more PRs and longer review times. Vendor data. Indirect evidence that clear explanations of changes are worth more.
- Grove: the best communicators will be the most valuable programmers. Opinion.
- Majors: shared understanding should be written down explicitly, not left in code or heads. Opinion.
- Google's design-doc and code-review practice treat writing as a core engineering activity. Practitioner account and Sadowski et al. study.

**How it is learned.** Writing design docs, PR descriptions and postmortems that get real feedback; editing others' writing; presenting designs in review.

**Practice moment while building.** Before a change is shared, the person writes the PR description: what changed, why, how it was tested and what the risks are. The tool compares it with the diff and points out anything the description leaves out.

### 12. Calibrated trust and owning the outcome

**What it is.** Knowing how much to trust a result based on evidence, not on how confident it sounds, and accepting responsibility for what you ship. This is a general professional skill (it applies to trusting a colleague's code or a library too), not an AI tool skill.

**Why it matters more now.** Generated output is fluent and plentiful, which makes overtrust easy.

**Evidence.**
- Perry et al.: AI users were more confident in less secure code; those who trusted the AI less did better. Evidence.
- Lee et al. (CHI 2025): more confidence in the tool, less critical thinking. Evidence (survey).
- METR 2025: a 39-point gap between felt and measured speed. Evidence.
- Only 3% of developers report high trust in AI output (DORA 2025 and Stack Overflow 2025). Evidence (survey).
- Willison: "a computer can't be held accountable", so the human is. Opinion.

**How it is learned.** Making predictions and checking them (for example, estimating risk before review and comparing with what review found), and reviewing past mistakes.

**Practice moment while building.** Before reviewing a change, the person rates how confident they are that it is correct and why. After tests, review or production, the tool shows how that rating compared with what happened. Over time this builds calibration.

## Strength of evidence at a glance

| Skill | Strength | Main support |
|---|---|---|
| Verification and test strategy | Strong | METR merge study, CodeRabbit, Stack Overflow, METR perception gap |
| Reading and understanding code | Strong | Anthropic RCT, Xia 2018, Anthropic internal report |
| Debugging and diagnosis | Strong | Anthropic RCT (largest gap on debugging) |
| Security judgment | Strong | Perry et al. CCS 2023, Veracode 2025 |
| Calibrated trust and ownership | Moderate | Perry et al., Lee et al. CHI 2025, METR |
| Problem framing and requirements | Moderate | METR implicit requirements, Ambig-SWE, practitioner agreement |
| System design and architecture | Moderate | GitClear trend, DORA amplifier, practitioner agreement |
| Operating in production | Moderate | DORA 2024 and 2025 stability, Faros, practitioner views |
| Technical communication | Moderate | Indirect: review load, design-doc practice, opinion |
| Trade-off decisions | Weak | Opinion only |
| Data modeling | Weak | Opinion only |
| Product judgment | Weak | Opinion and self-report only |

"Weak" means no measurement was found, not that the skill matters less. These skills are hard to measure, and practitioners rank them highly.

## Implications for a tool that trains these skills while building

These are design implications drawn from the evidence above. They are this note's reasoning, not findings of the cited studies.

1. **Ask before showing.** The highest-scoring patterns in the Anthropic trial involved the person thinking first or questioning the output. A prompt like "what do you expect this to change?" before revealing the diff turns review into practice.
2. **Make the person predict, then compare.** Prediction followed by feedback is the closest thing to deliberate practice inside real work, and real work is where professional skill is built (Macnamara 2014 suggests drills alone help little in professions).
3. **Keep some struggle.** "Getting painfully stuck" helped mastery in the Anthropic trial. A tool should not always offer the fix first, especially for debugging.
4. **Put the check before the code.** Acceptance checks, failure cases and rollout signals written first train verification and framing, and they make agent output cheaper to review.
5. **Record decisions and revisit them.** Short decision notes, shown again when the code changes, train trade-off judgment over time, the way design reviews and postmortems do.
6. **Replace some lost apprenticeship.** Juniors are hired less and ask seniors less. The tool can surface the questions a senior reviewer would ask ("how will you know this breaks?") and link to the team's past incidents and design docs.
7. **Measure calibration, not speed.** Felt speed is unreliable (METR). A tool should show people how often their own confidence matched reality.

## Gaps and unknowns

- No long-term study found of skill change over months of agent use. The Anthropic trial measured one hour.
- No study found that compares training methods (for example, design review vs deliberate drills) for these skills in the agent era.
- Product judgment, data modeling and trade-off skill have no direct measurement in any source found.
- Many quality datasets (CodeRabbit, GitClear, Veracode, OX, Faros) come from vendors with a product to sell.
- METR's own follow-up says productivity measurements are now hard to trust because of selection effects. Effects of newer tools may differ from 2025 data.
- The VOID incident report and Will Larson's recent writing were searched for but not found in usable form, so they are not cited.

## Sources

Studies and data:
- Anthropic, AI assistance and coding skills RCT (2026): https://www.anthropic.com/research/AI-assistance-coding-skills
- Anthropic, How AI is transforming work at Anthropic (2025): https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
- METR early-2025 RCT: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- METR uplift update (2026): https://metr.org/blog/2026-02-24-uplift-update/
- METR, SWE-bench-passing PRs not mergeable (2026): https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/
- Stack Overflow 2025 survey: https://stackoverflow.blog/2025/07/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here
- DORA 2024: https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
- DORA 2025: https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf
- Lee et al., CHI 2025: https://advait.org/files/lee_2025_ai_critical_thinking_survey.pdf
- Perry et al., CCS 2023: https://arxiv.org/abs/2211.03622
- Veracode 2025 (vendor): https://www.veracode.com/genai-code-security-report
- CodeRabbit 2025 (vendor): https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- GitClear 2025 (vendor), summary: https://leaddev.com/software-quality/how-ai-generated-code-accelerates-technical-debt
- OX Security 2025 (vendor): https://www.ox.security/army-of-juniors
- Faros AI (vendor), summary: https://www.augmentcode.com/guides/ai-productivity-paradox-engineering-delivery
- Ambig-SWE (2025): https://arxiv.org/abs/2502.13069
- Brynjolfsson et al., Canaries (2025, 2026 note): https://digitaleconomy.stanford.edu/news/canaries-interest-rates-and-timinga-more-on-recent-drivers-of-employment-changes-for-young-workers
- Xia et al., program comprehension (2018): https://xin-xia.github.io/publication/TSE17.pdf
- Sadowski et al., code review at Google (2018): https://research.google/pubs/modern-code-review-a-case-study-at-google/
- Macnamara et al., deliberate practice meta-analysis (2014): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/

Practitioner and expert opinion:
- Simon Willison, code proven to work (2025): https://simonwillison.net/2025/Dec/18/code-proven-to-work
- Charity Majors, AI demands more engineering discipline (2026): https://www.oreilly.com/radar/ai-demands-more-engineering-discipline-not-less/
- Charity Majors on observability (2025): https://newsletter.pragmaticengineer.com/p/observability-the-present-and-future
- Addy Osmani, the 70% problem: https://zed.dev/blog/ai-70-problem-addy-osmani
- Kent Beck, augmented coding: https://tidyfirst.substack.com/ and https://kentbeck.com/
- Birgitta Böckeler, spec-driven tools (2025): https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- Sean Grove, The New Code (2025): https://ai.engineer/talks/specifications-are-the-new-code
- Thoughtworks Technology Radar 2025: https://www.thoughtworks.com/about-us/news/2025/thoughtworks-technology-radar-highlights-genai-s-impact-and-key-
- Sean Goedecke, agents as theory building: https://www.seangoedecke.com/programming-with-ai-agents-as-theory-building
- Google SRE book, postmortem culture: https://sre.google/sre-book/postmortem-culture/
- Design docs at Google (via Simon Willison): https://simonwillison.net/2020/Aug/7/design-docs-google
