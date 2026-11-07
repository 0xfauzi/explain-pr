# Users, market and competitors

Track: users, market and competitors. Written 7 Nov 2026.

This report asks who would install a tool that keeps and grows real engineering
skill while they build with an AI coding agent, what they would pay, what makes
them quit, who else is in the space, and how such a tool reaches people. It
treats the earlier design in `design/learning-experience/` as evidence, not as
the answer.

## How to read the tags

- **[verified: source]** I read the claim on that page, or on a primary report
  of it, during this research. For prices from third-party aggregators I say so.
- **[unverified]** I could not confirm the claim from a primary source. It may
  still be true. Treat it as a lead.
- **needs to be measured** The number does not exist yet. We would have to
  measure it ourselves.

No number in this report is invented. Where I give a number, a source follows.

---

## 1. The problem, in evidence

### 1.1 The research that started this

Shen and Tamkin (Anthropic, January 2026) ran a randomised trial with 52 mostly
junior Python developers learning the Trio async library. The AI group scored
50% on the later quiz, the hand-coding group 67% (Cohen's d = 0.738, p = 0.01).
The AI group was about 2 minutes faster, which was not significant (p = 0.391).
The largest gap was on debugging questions.
[verified: https://www.anthropic.com/research/AI-assistance-coding-skills,
paper https://arxiv.org/abs/2601.20245]

The usage patterns matter most for product design:

| Pattern | n | Avg quiz score |
|---|---|---|
| Generation then comprehension | 2 | 86% |
| Hybrid code and explanation | 3 | 68% |
| Conceptual inquiry | 7 | 65% |
| AI delegation | 4 | 39% |
| Progressive AI reliance | 4 | 35% |
| Iterative AI debugging | 4 | 24% |

[verified: same Anthropic page]

Caveats the authors state: groups of 2 to 7 people, associations not causes, the
quiz was taken right after the task, and they tested a chat assistant, not an
agent like Claude Code, where they expect the effect "could be larger".
[verified: same page]

**What this means for the product.** The harm is not "using AI". It is letting
the AI do the thinking, and the worst case is letting it debug. The product's
job is to keep a small amount of the user's own thinking in the loop at the
right moments, without slowing the build much.

### 1.2 Supporting evidence

- **Guardrails decide the outcome.** Bastani et al. (PNAS 2025): about 1,000
  high school maths students. An unguarded GPT-4 tutor raised practice scores
  but students then did 17% worse on the exam than students who never had it. A
  tutor with learning safeguards removed most of that harm.
  [verified: https://papers.ssrn.com/abstract=4895486,
  https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education]
- **Agents automate more than chat.** Anthropic found 79% of Claude Code
  conversations were automation (the AI does the task), against 49% on
  claude.ai. [verified: https://anthropic.com/research/impact-software-development]
  So the drift toward delegation is strongest in exactly the tools our users
  build with.
- **Perceived speed is not real speed.** METR's 2025 trial: 16 experienced
  open-source developers, 246 tasks. AI made them 19% slower, yet they believed
  they were 20% faster. [verified: https://arxiv.org/abs/2507.09089] Users
  cannot trust their own sense of how much they are learning either. This
  supports measuring skill directly, away from the session.
- **Confidence in AI lowers critical thinking effort.** Lee et al. (CHI 2025),
  319 knowledge workers, self-reported. Higher confidence in the AI went with
  less critical thinking effort.
  [verified: https://advait.org/files/lee_2025_ai_critical_thinking_survey.pdf]

### 1.3 What developers say

Survey data:

- Stack Overflow 2025: 84% use or plan to use AI tools. 47.1% use them daily.
  About 33% trust AI accuracy and about 46% distrust it. 66% name "AI solutions
  that are almost right, but not quite" as a frustration. 45.2% say debugging
  AI-generated code takes more time.
  [verified: https://survey.stackoverflow.co/2025/ai]
- Same survey: early-career developers (1 to 5 years) use AI daily more than
  experienced ones (55.5% against 47.3%).
  [verified: https://survey.stackoverflow.co/2025/ai]
- Same survey, on agents: 14.1% use AI agents daily, 37.9% do not and do not
  plan to. [verified: same page] This is 2025 data. Agent use has very likely
  grown since, but the current figure needs to be measured or sourced.
- BairesDev Dev Barometer Q2 2026: 1,569 developers, 1,059 juniors and 510
  seniors. 85% of juniors say AI improved their understanding of software
  development. Only 16% of seniors say juniors fully understand the AI code they
  submit. 64% of seniors name over-reliance on AI without understanding as the
  most common graduate mistake, 50% name weak debugging. 24% of juniors say they
  feel least confident writing code from scratch without AI.
  [verified: https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/]
  This is a vendor survey, so read it as direction.
- LeadDev AI Impact Report 2025: 38% of engineering leaders agree "AI tools have
  reduced the amount of direct mentoring junior engineers receive from senior
  engineers". 54% think AI coding tools will reduce junior hiring over the longer
  term. [verified: https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles]

Forum sentiment:

- 404 Media (May 2026) collected anonymous developer accounts. One: "I forgot how
  to implement a Laravel API and it scared the shit out of me." Another: their
  "critical thinking and ability to sit and reason about a problem or a design
  has degraded". A new FAANG engineer said heavy AI generation made it hard to
  build a mental model of the codebase.
  [verified via the Slashdot excerpt:
  https://developers.slashdot.org/story/26/05/13/1949225/software-developers-say-ai-is-rotting-their-brains,
  original https://www.404media.co/software-developers-say-ai-is-rotting-their-brains/]
- r/ExperiencedDevs and r/ClaudeAI threads describe the same fear, with a strong
  counter-voice: developers who read every diff and ask why say they stay sharp.
  [unverified: seen through mirror sites and summaries, not reddit.com directly]

**The gap the product sits in.** Juniors believe they are learning (85%).
Seniors do not believe it (16%). Users overestimate their own gains (METR). No
one in the loop has an honest measure. A tool that gives the user a true,
private measure of what they can do without the agent fills that gap.

### 1.4 The labour market around it

- Brynjolfsson, Chandar and Chen (Stanford, August 2025, ADP payroll data):
  workers aged 22 to 25 in the most AI-exposed jobs, including software
  development, saw a 13% relative fall in employment. Older workers in the same
  jobs held steady or grew. Working paper, not peer reviewed.
  [verified: https://www.theregister.com/2025/08/26/ai_hurts_recent_college_grads_jobs/]
  Later figures of 16% to 19% circulate. [unverified]
- AWS CEO Matt Garman (August 2025) called replacing junior staff with AI "the
  dumbest thing I've ever heard" and framed juniors as the talent pipeline.
  [verified: https://www.theregister.com/2025/08/21/aws_ceo_entry_level_jobs_opinion/]
- Bootcamps contracted. General Assembly stopped new consumer enrolment in April
  2026, App Academy's immersive closed in June 2025, Turing School filed for
  Chapter 7 in June 2025. [unverified: aggregator reporting,
  https://hakia.com/news/bootcamp-market-2026/]
- Meta began AI-enabled coding interviews, where candidates use an assistant
  inside CoderPad, from late 2025. Meta said it is "more representative of the
  developer environment that our future employees will work in".
  [verified: Business Insider report via
  https://www.techradar.com/pro/meta-is-going-to-let-candidates-use-ai-in-job-interviews;
  scope of rollout unverified]

**What this means.** Entry-level people are under pressure to show they are more
than an agent operator. Interviews are starting to test judgment while using AI.
That is the skill this product trains: predict, explain, debug, with the agent
present.

---

## 2. User segments

Each segment has: the job to be done, the moment they reach for a tool, what
they would pay, and what makes them quit. "Pay" is my reading of the evidence,
not a measured willingness to pay. Real willingness to pay needs to be measured.

### 2.1 Students (university and self-taught, pre-job)

- **Job to be done.** "Use the AI tools everyone uses, and still pass the exam,
  the interview and the first job."
- **Trigger.** A failed exam or interview after doing well on AI-assisted
  coursework. A course that bans or restricts AI. A professor who requires a
  learning mode.
- **What they use now.** Free AI learning modes: ChatGPT Study Mode, Gemini
  Guided Learning, Claude learning mode. Copilot is free for verified students.
  [verified: https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/enable-copilot/set-up-for-students]
  Google gave US and some other college students a free year of AI Pro.
  [verified: https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/]
- **Would pay.** Little or nothing. Their tools are free. The institution may
  pay (see 2.7).
- **Quits when.** It slows down homework that is due tonight. It feels like a
  second course. Streak pressure turns into guilt. It needs setup they do not
  understand.
- **Fit.** Medium. Large numbers, low revenue, strong word of mouth. Most
  students do not yet build "a large project with an agent", which is the
  founder's core use.

### 2.2 Bootcamp graduates and career switchers

- **Job to be done.** "Prove I can really engineer, not just prompt, so I get
  and keep a first job."
- **Trigger.** Job search stalls. A take-home or live interview exposes gaps.
  The first code review at a first job says "explain this".
- **What they use now.** LeetCode, Boot.dev, Exercism, YouTube, AI chat.
- **Would pay.** Yes, modestly. They already pay for learning: Boot.dev about
  $399 a year [unverified: third-party review, https://dev.to/royce_fabbd83cb268312e928/bootdev-review-2026-backend-developer-path-pricing-verdict-hk8],
  LeetCode Premium $35 a month or $159 a year [unverified: aggregator,
  https://prachub.com/resources/leetcode-pricing].
- **Quits when.** It does not visibly help the job search. Progress cannot be
  shown to anyone. Money is tight.
- **Fit.** High on need, small and shrinking as a channel (bootcamps are
  contracting, see 1.4). The "proof" job conflicts with a private record. It
  needs a share or export the user controls.

### 2.3 Junior engineers (0 to 3 years, employed)

- **Job to be done.** "Ship at the pace my team expects with an agent, and still
  grow into a senior who understands the system."
- **Trigger.** A production incident they could not debug. A senior asking
  "why does this work?" in review. Feeling, as the 404 Media developer put it,
  that they "forgot how". Promotion feedback about depth.
- **What they use now.** The company's agent (Claude Code, Copilot, Cursor,
  Codex). Claude Code's Learning output style, which leaves `TODO(human)` spots
  to fill in. [verified: https://code.claude.com/docs/en/output-styles]
- **Would pay.** Some would pay personally, a few dollars a month. Many would
  rather the employer pays. Needs to be measured.
- **Quits when.** It slows them when a deadline is near and they cannot skip at
  no cost. Their manager might see their weak areas. It nags. It interrupts flow
  in the middle of a hard task.
- **Fit.** The best segment. Highest daily AI use (1.3). They build real things
  with agents every day. The pain is felt and personal. Privacy matters a lot:
  a local record they own is a selling point, not a constraint.

### 2.4 Seniors moving to a new domain

- **Job to be done.** "Get fluent in a new stack (Rust, async, ML, a new
  codebase) fast, using the agent, without becoming the senior who cannot review
  their own team's code."
- **Trigger.** A new job or team. Inheriting a codebase. Being asked to review
  code in a language they do not know.
- **What they use now.** Docs, the agent in explain mode, books, Exercism tracks
  for the language.
- **Would pay.** Yes, or expense it. They pay for O'Reilly and courses already.
  Needs to be measured.
- **Quits when.** Questions are too basic. The tool talks down. It asks about
  things they already know. It costs focus during work they are expert in.
- **Fit.** High and underserved. Shen and Tamkin's setting (an experienced
  Python user learning a new library) matches this segment closely. The tool
  must stay silent on what the user knows and only engage on new ideas. "Your
  line" (founder decision 2) suits this group well.

### 2.5 Engineering managers and teams

- **Job to be done.** "Adopt agents for speed, and still have engineers who can
  own, review and debug what ships. Keep juniors growing."
- **Trigger.** An incident nobody understood. Juniors who cannot explain their
  PRs. Promotion cases that are thin. Leadership asking whether AI is hollowing
  out the bench.
- **Evidence of the pain.** 38% of leaders say AI reduced mentoring of juniors
  (LeadDev). 16% of seniors say juniors fully understand their AI code
  (BairesDev). Anthropic's paper tells managers to "build in systems that keep
  engineers learning". [verified: sources in 1.3]
- **Would pay.** Yes. This is where most of the revenue is. Benchmarks for team
  spend: Pluralsight Skills about $399 to $779 per user per year
  [unverified: aggregator, https://g2.com/products/pluralsight-skills/pricing];
  CodeRabbit about $24 to $48 per developer per month annual
  [unverified: CodeRabbit FAQ via search, https://docs.coderabbit.ai/about/pricing].
- **Quits when.** No one can show it changed anything. Engineers hate it or see
  it as surveillance. It slows delivery. Legal or security will not approve a
  tool that sends code out.
- **Fit.** High revenue, high risk. A tool that lets managers see individuals'
  weak areas will be rejected by the engineers (2.3). The team product must give
  managers aggregate, opt-in signals only, and give engineers control over what
  they share.

### 2.6 Educators and universities

- **Job to be done.** "Let students use AI agents, as industry does, and still
  know they learned."
- **Trigger.** Course redesign. Academic integrity cases. A department AI policy.
- **What exists.** CS50's Duck tutor with "pedagogical guardrails". Malan says
  that even told not to, it still returns blocks of code "up to a quarter of the
  time". [verified: https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/]
  Claude for Education with learning mode, at Northeastern, LSE and Champlain.
  [verified: https://www.anthropic.com/news/introducing-claude-for-education]
- **Would pay.** Institutions pay slowly, with procurement, privacy and
  accessibility reviews. Individual instructors adopt free, open tools fast.
- **Quits when.** It cannot be graded or reported. It does not fit the LMS. It
  stores student data somewhere the university has not approved.
- **Fit.** Good for reach and credibility, slow for revenue. The CS50 finding is
  important: a prompt alone does not hold a guardrail. The product's sealed
  answer keys and engine-side grading (from the earlier design) are a real
  advantage here.

### 2.7 Hiring (candidates and employers)

- **Job to be done.** For candidates: "show I can think with an agent". For
  employers: "tell apart engineers who understand from those who only prompt".
- **Trigger.** AI-enabled interview rounds (Meta). Take-homes done with agents.
- **Would pay.** Employers pay assessment vendors. Candidates pay for prep.
- **Quits when.** Any hint that a private learning record is used to judge
  people. Gaming makes the signal worthless.
- **Fit.** Low now, and dangerous. A learning record that feeds hiring stops
  being honest: people will stop admitting what they do not know. Keep hiring
  out of scope, except a candidate's own practice mode. Revisit later.

### 2.8 Segment summary

| Segment | Pain | Agent use today | Will pay | Fit |
|---|---|---|---|---|
| Junior engineers | High, personal | Daily | Some, or employer | Best first segment |
| Seniors in a new domain | High, focused | Daily | Yes, or expense | Best second segment |
| Teams and managers | High, organisational | Daily | Yes, budget exists | Revenue, later |
| Bootcamp grads, switchers | High | Mixed | Modest | Need proof, shrinking |
| Students | Medium | Chat more than agents | No | Reach, not revenue |
| Educators | Medium | Varies | Slow | Credibility |
| Hiring | Low now | n/a | Employers | Out of scope |

---

## 3. Competitors and adjacent products

### 3.1 AI "learning modes" built into the assistants

| Product | What it does | Where | Tag |
|---|---|---|---|
| Claude Code Learning style | Adds Insight blocks, leaves `TODO(human)` spots for the user to write, waits, then gives one Insight on their code. Set with `/config` or `outputStyle`. | Claude Code | [verified: https://code.claude.com/docs/en/output-styles] |
| Claude Code Explanatory style | Default behaviour plus short explanations of why. | Claude Code | [verified: same] |
| Claude learning mode (education) | Asks questions instead of answering, asks for evidence. | claude.ai Projects | [verified: https://www.anthropic.com/news/introducing-claude-for-education] |
| ChatGPT Study Mode | Asks questions to test understanding, sometimes withholds direct answers. Easy to switch off. Launched July 2025. | ChatGPT | [verified: https://techcrunch.com/2025/07/29/openai-launches-study-mode-in-chatgpt] |
| Gemini Guided Learning | Toggle in the prompt box. Scaffolded questions, visuals, quizzes, on LearnLM. August 2025. | Gemini app | [verified: https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/] |
| Copilot, Cursor | Explain and Ask modes exist. I found no learning mode with retention tracking. | IDEs | [unverified: absence not proven] |

**What they share.** All are in-session only. None keeps a record of what you
can do, none schedules review days later, none measures skill without the AI.
All are tied to one vendor. Each is free and one toggle away, so they set the
user's price expectation at zero for "the AI asks me questions".

**What this means.** Do not compete on "the AI asks you questions". That is
free and built in. Compete on what they lack: a durable, honest, portable
measure of skill, spaced review, debugging practice, and one record across every
agent the user uses. Claude's Learning style is closest to "your line". Our
version must differ by being graded by tests, rarer, and tied to the record.

### 3.2 Direct community competitors (plugins and skills)

This space is filling fast. All were found in November 2026.

| Project | What it does | Agents | Traction | Tag |
|---|---|---|---|---|
| VibeWise (nykooi1/vibe-wise) | Asks your approach first, discusses trade-offs, checkpoints (Build, Design, Implementation), three levels, notes in `.vibe-wise/`. No spaced repetition mentioned. In the Anthropic plugin directory. MIT. | Claude Code, Codex | About 4.2k stars, 171 forks | [verified: https://github.com/nykooi1/vibe-wise] |
| learn-while-build (Pranavraut033) | Per-repo teaching rules, end-of-session concept log, graded review, local flashcard page, intervals 1 to 60 days. MIT. | Claude Code only | 0 stars when checked | [verified: https://github.com/Pranavraut033/learn-while-build] |
| claude-tutor (kirilxd) | Learning plans, adaptive quizzes, SM-2 spaced repetition, web dashboard. General topics, not tied to the build. | Claude Code | not checked | [unverified: search summary, https://github.com/kirilxd/claude-tutor] |
| vibe-learn, VibeLearning, no-vibe, slow-engineering, learn-faster-kit | Explain-then-quiz skills, "intentional friction" tutors. | Mostly Claude Code, some Codex | not checked | [unverified: directory listings, https://awesomeclaude.ai/awesome-claude-code] |

**What this means.**

1. The demand is real: one of these reached thousands of stars.
2. The name space is crowded. "learn-while-build" is almost our skill's name
   ("learning-while-building"). Naming and brand need care.
3. VibeWise owns "slow down and design first". Its cost is that it slows the
   build. Our position should be the opposite promise: the build keeps its pace,
   and the learning happens in a few chosen moments and in short review later.
4. Nobody combines all of: honest measurement away from the session, spaced
   review with transfer questions, debugging drills, tests grading the user's
   own line, and one record across many agents. That combination is the gap.
5. These are free and MIT. The core must be free and open too, or it will be
   forked or ignored.

### 3.3 Learning platforms

| Product | Model | Lesson for us | Tag |
|---|---|---|---|
| Exercism | 100% free; Insiders for $10 a month donation or more; human mentoring on each iteration. | Free core plus voluntary support works for a mission product. Naming the action as engineers name it ("code review") matters. | [verified: https://exercism.org/insiders]; mentoring lesson from earlier research `design/learning-experience/research/product-patterns.md` |
| Boot.dev | Gamified backend course, about $399 a year. | Developers pay for game-like progress that leads to a job. | [unverified: third-party pricing] |
| Codecademy | Plus and Pro tiers, frequent discounts. | Course content is a commodity; prices keep dropping. | [unverified: https://pricingsaas.com/companies/codecademy] |
| LeetCode | Premium $35 a month or $159 a year. | People pay for interview outcomes, not for learning as such. | [unverified: aggregator] |
| Brilliant | Streak of 3 problems or one lesson a day, with a "streak charge" for a missed day. | Low daily bar plus slack. | [verified: https://brilliant.org/help/using-brilliant/what-is-a-streak] |
| Duolingo | 58.7M daily active users, 12.7M paid subscribers in Q2 2026. | Daily habit at scale is possible, but its methods (streak anxiety, frequent nudges) conflict with founder decision 7. | [verified: https://www.sec.gov/Archives/edgar/data/0001562088/000162828026053299/q2fy26duolingo6-30x26share.htm] |
| Anki | Free desktop; daily review limits to prevent review floods; FSRS scheduler. | The cap on daily reviews (our 3 a day) has precedent. Self-grading alone is weak for open answers. | [verified: https://docs.ankiweb.net/deck-options.html] |

**Common weakness.** All of these teach in a separate place, on made-up
exercises. None uses the user's own real project. Our edge is that every
question comes from code the user shipped this week.

### 3.4 Code review and team tools

| Product | Relevance | Tag |
|---|---|---|
| CodeRabbit | AI PR review with "learnings" that adapt to a team. About $24 to $48 per developer per month annual. It learns the team's preferences; it does not grow the engineer. | [unverified: pricing via search, https://docs.coderabbit.ai/about/pricing] |
| GitHub PR review | "Viewed" checkbox per file, which un-ticks when the file changes. | [verified: earlier research, product-patterns.md] |
| Pluralsight Skills | Team skill assessments and courses, about $399 to $779 per user per year. Shows team budgets for "skill" exist. | [unverified: aggregator] |

**What this means.** Teams already pay per seat for review and for skills
platforms. A team product that sits in the PR ("the author can explain this
change") is a natural bridge, but it must be the author's choice to attach it.

### 3.5 Competitive map

Two axes decide position:

- **Where learning happens**: separate exercises, or inside the user's real build.
- **What is measured**: nothing, in-session answers, or retained skill without
  the agent, days later.

| | Nothing measured | In-session only | Retained skill, later |
|---|---|---|---|
| Separate exercises | YouTube, docs | Codecademy, LeetCode, Boot.dev | Anki, Exercism (partly) |
| Inside the real build | Explanatory style | Claude Learning style, Study Mode, Guided Learning, VibeWise | learn-while-build (small), **our target** |

The top right cell is nearly empty. Only one tiny project tries it, on one
agent.

---

## 4. Distribution channels

The founder requires parity on all coding surfaces (decision 6). The channels
below are where users of each surface look.

| Channel | Reach | State | Tag |
|---|---|---|---|
| Agent Skills open standard (agentskills.io) | One `SKILL.md` folder loads in many agents. Published by Anthropic December 2025. | Adopted by Codex, Cursor, Copilot, Gemini CLI and others, with different folder paths per tool. | [unverified for the count; per-tool paths verified in earlier research `codex-others.md`, e.g. https://cursor.com/docs/context/skills, https://geminicli.com/docs/cli/skills/] |
| skills.sh (Vercel Labs) | Install and discovery hub for skills across many agents. | Launched January 2026. | [unverified: https://www.firecrawl.dev/blog/agent-skills] |
| Claude Code plugin directory (claude-plugins-official) | Loads automatically in Claude Code. Install with `/plugin install name@claude-plugins-official`. Reviewed submissions. | VibeWise is listed. | [unverified: mirrors of the official repo, https://www.morphllm.com/claude-code-marketplace] |
| Codex plugin marketplace | Bundles skills, MCP servers and apps; works in Codex app, CLI and IDE. Curated directory plus repo and personal marketplaces. Launched March 2026. | Self-serve publishing to the official directory was not available as of May 2026. | [unverified: https://the-decoder.com/openais-codex-gets-a-plugin-marketplace-for-slack-notion-figma-and-more/] |
| Official MCP registry | Lists MCP servers for any MCP host. Preview from September 2025. | Counts in sources conflict (about 2,000 in May 2026, about 30,000 in September 2026 with mirroring). | [unverified: https://dev.to/amareswer/the-mcp-registry-by-the-numbers-38nc] |
| Package managers (PyPI via `pipx`/`uvx`, npm via `npx`) | How MCP servers and CLIs are usually installed. | Standard. | [verified: common practice; the earlier plan uses `uvx lwb`] |
| VS Code Marketplace and Open VSX | Copilot, Cursor, Windsurf users. | Needed only if we ship an editor extension. | [unverified for our need] |
| GitHub itself | Stars, READMEs, "awesome" lists. VibeWise's growth came through GitHub. | Main discovery path for this category. | [verified: star counts above] |
| Education channels | GitHub Education, course adoption, CS50-style instructors. | Slow, high trust. | [verified: GitHub Education student page above] |

**What this means.**

1. One source, many outputs. The skill, an MCP server and a rules file
   (`AGENTS.md` section) cover nearly every agent. Ship to the Claude plugin
   directory, Codex marketplace, skills.sh and the MCP registry from one repo.
2. GitHub is the storefront. The README and a 60-second demo matter more than a
   marketing site.
3. Plugin directories review submissions and warn that the user trusts what
   plugins run. The product must be easy to audit: small, open source, local,
   no network by default. Founder decision 1 (local git, no remote) helps here.

---

## 5. Business models that fit

Constraints: the core competes with free, built-in learning modes and free MIT
plugins. The record is local and private by default (decision 1). Engineers
will reject anything that feels like surveillance.

| Model | How it works | Fit | Risk |
|---|---|---|---|
| Open core, free forever for individuals | Engine, skill, MCP server, local Room, local record all free and open. | Required. Matches Exercism and the community competitors. | No revenue alone. |
| Paid sync and phone | End-to-end encrypted sync, phone app, daily reminder (the earlier plan's "lwb Sync"). | Good. A real cost we bear, so a real reason to pay. Matches decisions 4 and 7. | Must work flawlessly; a hosted service to secure. |
| Team plan | Shared topic packs for a codebase, onboarding paths, aggregate opt-in signals, PR "explained by author" attachment. Per seat. | Strongest revenue. Budgets exist (Pluralsight, CodeRabbit). | Surveillance perception. Must be engineer-controlled. |
| Education licence | Instructor packs, course-level aggregate reports, LMS export, data stays on student machines. | Credibility and reach. | Slow procurement. |
| Topic packs (paid content) | Curated packs for a stack (async Rust, Postgres internals) that the agent draws questions from. | Possible later. | Content is a commodity; AI generates questions anyway. |
| Donations or sponsorship | GitHub Sponsors, Exercism-style supporter tier. | Fits mission. | Small. |
| Sell to an agent vendor | Anthropic, OpenAI, Google already ship learning modes. | Possible exit. | Not a plan. |

Ruled out: selling learning records, ads, using records for hiring. Each
destroys the honesty the record depends on.

Price points are not set here. Willingness to pay needs to be measured, for
example with a pricing page test against the comparables in 3.3 and 3.4.

---

## 6. What the founder decisions mean for the market

I accept all seven decisions. Two have market consequences worth stating, and
for one I raise a challenge with evidence.

- **Decision 1 (local git record, no remote).** A strong trust signal for
  individuals and for reviewed plugin directories. It conflicts with the team
  and education products, which need some shared signal. Resolution: shared
  data is always a user-initiated export or opt-in aggregate, never a pull.
- **Decision 6 (feature parity on all surfaces). Challenge, with evidence.**
  The surfaces differ in what they can show. VS Code MCP Apps are inline only
  and "send message" only fills the input box; Zed supports MCP tools and
  prompts only, with no MCP Apps; Gemini CLI documents no elicitation or MCP
  Apps. [verified: https://code.visualstudio.com/api/extension-guides/mcp,
  https://zed.dev/docs/ai/mcp, https://geminicli.com/docs/tools/mcp-server/,
  summarised in `design/learning-experience/research/codex-others.md`]
  Pixel-level parity is not possible. I propose defining parity as **parity of
  outcomes**: every surface can run the full learning loop (question, answer
  with confidence, grade, your line, review, map) through plain chat text plus
  the local Room, even where rich inline UI is missing. This keeps the
  founder's intent (general users, any agent) and is testable. The founder
  should confirm this reading.
- **Decisions 3 and 7 (3 reviews a day, one reminder a day).** These are a
  market advantage. The main reason people quit learning apps is pressure. These
  limits are the opposite of Duolingo's approach and match Anki's review caps.
  Say so in marketing.

---

## 7. The 3 strongest product opportunities

### Opportunity 1: The honest measure of what you can do without the agent

Juniors think they learn (85%), seniors doubt it (16%), and users misjudge their
own speed by a wide margin (METR). Built-in learning modes only act in the
session. No product gives a private, honest, durable measure of skill without
the agent, that goes down when you forget. This is the core of the product and
its clearest difference from every competitor in section 3. It turns a vague
fear ("am I getting worse?") into a map the user can act on.

### Opportunity 2: One learning record across every agent

Users switch between Claude Code, Codex, Cursor and Copilot, and vendors' own
learning modes are locked to one tool. The Agent Skills standard and MCP make
one engine reachable from all of them. A single local record that follows the
user across agents is something no vendor will build, because each wants lock-in.
This also makes the product safe from any one vendor shipping a better learning
mode: we sit on top of all of them.

### Opportunity 3: The team product that rebuilds mentoring, without surveillance

38% of leaders say AI cut mentoring. Seniors cannot see whether juniors
understand their PRs. Teams already pay per seat for skills and review tools.
A team plan that gives a codebase its own topic packs, onboarding paths, and an
author-attached "I can explain this change" on PRs, with engineer-controlled
sharing and aggregate-only manager views, addresses a budgeted problem. Seniors
moving to a new domain and new hires onboarding to a codebase are the same
mechanism.

---

## 8. The 3 biggest market risks

### Risk 1: The vendors make it a free toggle

Anthropic, OpenAI and Google all ship learning modes, and Anthropic's own paper
recommends them. If one adds spaced review and a skill record, our core looks
like a feature. Mitigation: cross-agent record (Opportunity 2), local ownership,
measurement rigor (sealed answer keys, tests grading your line), and moving fast
on the team product, which vendors are slower to build.

### Risk 2: Users say they want to learn, then skip every question

The stated value is long-term. The cost (a question now) is immediate. The worst
learning pattern in Shen and Tamkin was also the most natural agent behaviour.
VibeWise's design slows the build, and we do not know its retention. Our own
retention needs to be measured from the first release: share of offered
questions answered, share of due reviews done, 30-day return. Mitigation: very
few questions, free skip, value visible within the first week (the map moves),
and the user's real code as content.

### Risk 3: A crowded, free, look-alike field with no clear name

At least five free plugins claim "learn while you vibe code", one with a name
almost the same as ours. Directory reviewers and users will struggle to tell
them apart, and free MIT tools set the price at zero. Mitigation: a distinct
name and one-sentence promise ("keeps your pace, measures what you can do
without the agent"), a public method page that shows the evidence, a short
demo, and early presence in each marketplace. Monetise only what costs us to run
(sync, phone) and what teams budget for.

Other risks worth tracking: the hiring market turning the record into a
credential, which would make it dishonest; privacy reviews blocking a team
product; and the cost of keeping parity across a dozen fast-changing surfaces.

---

## 9. Open questions that need research or measurement

1. Willingness to pay for individuals, for sync and phone. Needs a pricing test.
2. Retention of VibeWise and similar plugins. Not public. Could be asked of
   maintainers.
3. Current share of developers using agents daily in late 2026. The 14.1% figure
   is from 2025.
4. Whether employers would buy a tool whose individual data they cannot see.
   Needs interviews with engineering managers.
5. Whether universities will accept a record that stays on the student's
   machine, given grading and integrity needs.
6. Whether Copilot and Cursor have added retention-based learning features since
   this research. Absence was not proven.
7. Whether the founder accepts "parity of outcomes" as the reading of decision 6.

## 10. Sources

Primary or first-hand: Anthropic skill-formation study
(https://www.anthropic.com/research/AI-assistance-coding-skills,
https://arxiv.org/abs/2601.20245); Anthropic Economic Index on software
(https://anthropic.com/research/impact-software-development); Stack Overflow
2025 AI survey (https://survey.stackoverflow.co/2025/ai); METR
(https://arxiv.org/abs/2507.09089); Bastani et al.
(https://papers.ssrn.com/abstract=4895486); Lee et al. CHI 2025
(https://advait.org/files/lee_2025_ai_critical_thinking_survey.pdf); BairesDev
Dev Barometer (https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/);
LeadDev (https://leaddev.com/hiring/junior-devs-still-have-path-senior-roles);
Claude Code output styles (https://code.claude.com/docs/en/output-styles);
Claude for Education (https://www.anthropic.com/news/introducing-claude-for-education);
Harvard Gazette on CS50 Duck
(https://news.harvard.edu/gazette/story/2026/09/taming-the-duck-for-starters/);
VibeWise (https://github.com/nykooi1/vibe-wise); learn-while-build
(https://github.com/Pranavraut033/learn-while-build); Exercism Insiders
(https://exercism.org/insiders); Brilliant streak
(https://brilliant.org/help/using-brilliant/what-is-a-streak); Anki deck
options (https://docs.ankiweb.net/deck-options.html); Duolingo Q2 2026 8-K
(https://www.sec.gov/Archives/edgar/data/0001562088/000162828026053299/q2fy26duolingo6-30x26share.htm);
GitHub Copilot for students
(https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/enable-copilot/set-up-for-students).

Press: TechCrunch on Study Mode
(https://techcrunch.com/2025/07/29/openai-launches-study-mode-in-chatgpt) and
Guided Learning
(https://techcrunch.com/2025/08/06/google-takes-on-chatgpts-study-mode-with-new-guided-learning-tool-in-gemini/);
The Register on Stanford entry-level study
(https://www.theregister.com/2025/08/26/ai_hurts_recent_college_grads_jobs/)
and on AWS CEO
(https://www.theregister.com/2025/08/21/aws_ceo_entry_level_jobs_opinion/);
TechRadar on Meta AI interviews
(https://www.techradar.com/pro/meta-is-going-to-let-candidates-use-ai-in-job-interviews);
404 Media via Slashdot
(https://developers.slashdot.org/story/26/05/13/1949225/software-developers-say-ai-is-rotting-their-brains);
The Decoder on Codex plugins
(https://the-decoder.com/openais-codex-gets-a-plugin-marketplace-for-slack-notion-figma-and-more/).

Third-party and aggregators (lower confidence): Boot.dev review
(https://dev.to/royce_fabbd83cb268312e928/bootdev-review-2026-backend-developer-path-pricing-verdict-hk8),
LeetCode pricing (https://prachub.com/resources/leetcode-pricing), Codecademy
pricing (https://pricingsaas.com/companies/codecademy), Pluralsight pricing
(https://g2.com/products/pluralsight-skills/pricing), CodeRabbit pricing
(https://docs.coderabbit.ai/about/pricing), bootcamp market
(https://hakia.com/news/bootcamp-market-2026/), Agent Skills overview
(https://www.firecrawl.dev/blog/agent-skills), Claude plugin marketplace guide
(https://www.morphllm.com/claude-code-marketplace), MCP registry numbers
(https://dev.to/amareswer/the-mcp-registry-by-the-numbers-38nc), Awesome Claude
Code directory (https://awesomeclaude.ai/awesome-claude-code).

Earlier repo research used as input: `design/learning-experience/research/learning-science.md`,
`product-patterns.md`, `codex-others.md`.
