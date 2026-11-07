# Red team: market skeptic

Reviewer lens: why Firsthand fails commercially or never gets used, what a large lab could ship next quarter that kills it, and what is easy to copy.

Scope: `design/product/PRODUCT.md`, `spec/teams.md`, `research/users-market.md`, and the parts of `spec/architecture.md` and `spec/measurement.md` that PRODUCT.md links for cost, grading and claims.

Rules used here: no invented numbers. A claim about a product carries [verified: source] or [unverified]. Where a number is needed and not known, it says "needs to be measured".

Summary verdict: the learning design is careful. The business design is not. The spec has no reason a user comes back that it is allowed to use, no thing a buyer can pay for that it is allowed to sell, and no part a vendor or an open-source rival cannot copy in weeks. It also bets on a live user at the keyboard just as coding work moves to background agents. Each problem below has a small fix. None of the fixes needs the learning loop to change.

---

## 1. The habit has no engine (critical)

**What fails.** The spec removes every habit mechanic that keeps people in learning products, and puts nothing in their place. Reminders are off by default (PRODUCT.md 4.5). No streaks, no points, no counts (principle 7). After a gap there is "no backlog count" (5.3). Three ignored reminders stop reminders for good (4.5). Two skips end questions for the session (4.5). The session-start offer defaults to "later" (5.3). Each rule is defensible alone. Together they mean the product's default behaviour, for a busy user, is to fade out and never say so.

The research the spec cites says this is the main risk. Users prefer substitution and overrate AI help (Lehmann 2025, cited in PRODUCT.md section 12). The value is long term and the cost is now (research/users-market.md section 8, risk 2). Duolingo reaches scale with the exact mechanics the founder ruled out [verified: research/users-market.md 3.3, Duolingo Q2 2026 filing]. I agree with ruling them out. But the spec has not designed a replacement.

**Scenario.** A junior installs it after reading the Shen and Tamkin post. Day 1: does the Trace drill, finds it interesting. Days 2 to 4: a deadline. Says "later" four times, skips twice. Day 5: the session-start line is still there, but now it is noise. Never set a reminder because the default was off. Week 3: the instruction file still loads in every session. The user never opens the map. They uninstall when they notice the extra tokens, or they just forget it exists. Nothing in the product notices or reacts, by design.

**Why this is commercial, not only learning.** E1 (PRODUCT.md section 11) measures answer rate and review completion in week 3 of a 20-person design-partner cohort. Design partners are paid in attention by the founder. They are not the market. 14-day and 30-day return are listed as product metrics (9.1) but no experiment gates the engine rewrite on them.

**Smallest fix.**
- Give the user one artifact they want to open without a reminder. Candidate: a short weekly line in the first session of the week, "This week you diagnosed 2 of 5 failing tests before the agent did. Last week 0 of 4." It is a fact about their own work, not a streak. Whether it pulls people back needs to be measured.
- Add 30-day return of users recruited cold (from a directory listing, not from the founder's network) as a pass rule in E1 or a new E13, before the 16 to 24 week engine build. Threshold is a founder decision.
- Turn the reminder question at install into a real choice with no pre-selected answer, instead of "off" as default. This stays inside decision 7 (at most one a day, at the user's time).

---

## 2. A vendor can ship 80% of this next quarter (critical)

**What fails.** The spec's defence against vendors (PRODUCT.md section 8, "Why a vendor toggle does not end the business") lists four moats: one record across rival agents, drills from your own history, an honest measure, a record the user owns. Three of the four are features a vendor already has the parts for.

What exists today:
- Claude Code's Learning output style already leaves `TODO(human)` gaps for the user to write and waits [verified: https://code.claude.com/docs/en/output-styles]. That is "your line".
- Claude Code has built-in memory files and an auto memory feature that persists across sessions [unverified: third-party guides, for example https://blog.memoryplugin.com/claude-code-memory/ and https://www.engineerscodex.com/claude-code-auto-memory; official doc not checked].
- Claude Code already runs subagents and headless mode (`-p`) [verified: research/surfaces.md 10.6]. Those are a separate grading context.
- Anthropic published the research this product is built on, and its own post recommends learning modes [verified: https://www.anthropic.com/research/AI-assistance-coding-skills].

**Scenario.** In Q1 2027 Anthropic ships "Learning style v2": `TODO(human)` gaps plus a `/review` command that asks three questions a day from memory about code the user wrote in past sessions, graded by a subagent that runs the tests. It is one toggle, free with the plan, on the surface most Firsthand users came from. The plugin directory listing for Firsthand now reads as a duplicate. This is [unverified] as a prediction, but every component in it already ships in some form.

**Why the remaining moats are weak.**
- "One record across rival agents." It matters only to people who switch agents often. How many do is not in the research: it needs to be measured. A user who lives in one agent gets nothing from it. And cross-agent memory is already a crowded third-party category (Cognee says its Claude Code and Codex plugins share memory [unverified: https://docs.cognee.ai/integrations/claude-code-integration], also claude-mem and Walrus Memory [unverified: https://blog.walrus.xyz/how-to-add-portable-memory-to-claude-code-and-codex-with-walrus-memory/]).
- "An honest measure that could show a vendor's own agent eroding skill." This is a reason for a researcher to like the product. It is not a reason for a user to choose it over a free toggle.
- "A record the user owns." Users rarely pay or switch for data ownership in learning tools. No evidence in the research shows they do.

**The one moat a vendor has weak reasons to build** is the human-written unseen-question bank and the Checkup (PRODUCT.md 6.4, 9.2): content a lab will not author per idea, and a measure a lab may not want published about its agent. The spec treats this as a measurement instrument and leaves its funding as open founder decision 4. Commercially, it is the product.

**Smallest fix.** Reorder the value story. Lead with the Checkup and the unseen bank as the thing nobody else has ("a monthly test, in a repo you have never seen, written by people, that your agent never saw"). Move funding of a first small bank from "founder decision" to v0, and run a cheap test of whether users want the Checkup at all before building the engine.

---

## 3. Coding moves to background agents; the in-build loop loses its user (critical)

**What fails.** Three of the four build moves (Predict, Call it, Your line) need a live user at the moment the agent hits a breakpoint (PRODUCT.md 4.2). The surfaces where that is weakest are the ones growing: Copilot cloud agent has "no live user in the loop" and ends at 59 minutes [verified: PRODUCT.md 5.4, https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent]; Codex cloud and Claude Code on the web run in remote containers or VMs [verified: PRODUCT.md 5.4]. The spec handles these as edge cases (a carry branch, "your line via PR body", "Floor, untested").

How fast work moves to background agents is not in the research and needs to be measured. But the direction is the one the vendors are investing in: Anthropic found 79% of Claude Code conversations were automation [verified: research/users-market.md 1.2, https://anthropic.com/research/impact-software-development].

**Scenario.** A team lead in 2027 assigns five issues to cloud agents in the morning and reviews five PRs after lunch. There is no breakpoint with a human present. Firsthand's in-build layer never fires. The only moment the human is present is PR review, and the spec's PR features are a v2 "optional walkthrough" for authors (spec/teams.md section 3), not a reviewer drill.

**Smallest fix.** Make review time a first-class trigger, not an edge case. The Check drill already exists (PRODUCT.md 4.6): "lists defects and severity, or says clean". Run it on the live agent PR the user is about to review, before they see the agent's own summary, with the key being the CI result and any later fix commit. This needs no new surface, works on every cloud agent that opens a PR, and matches where the human actually is. It also fixes the weakest rows in the parity table.

---

## 4. The team plan has nothing a buyer can buy (critical for revenue)

**What fails.** Team is "the planned revenue line" (PRODUCT.md section 8, spec/teams.md 6.2). The admin contract (spec/teams.md 4) says admins cannot see who uses the tool, cannot turn reports on, cannot read records, and get counts only for opted-in groups of at least 8. The report shows guide coverage, and "is never sold as a skill measure until a power check shows it can detect a change at the group floor" (5). The claims ladder (PRODUCT.md 9.5) allows no efficacy claim until a randomised study.

So a manager is asked to pay per seat for: a guide (which is free in v2, spec/teams.md section 2), SSO and SCIM, a relay, and a coverage count they may never see if fewer than 8 people opt in. They cannot see adoption, which is the first thing a buyer checks at renewal. The comparables in the research sell visible outcomes: CodeRabbit reviews PRs, Pluralsight shows skill assessments [unverified: pricing, research/users-market.md 3.4].

**Scenario.** A 12-person team trials Firsthand Team. 5 engineers opt in to sharing. The report shows "too few to show". The manager cannot tell whether anyone uses it. At renewal, finance asks what changed. The answer is "we cannot say, by design". The seat licence is cut.

**Smallest fix.**
- Pick one team outcome the buyer can see that exposes no individual: for example, time from a new hire's start to their first merged PR in an area with a guide, computed from git history the company already owns. Whether it moves needs to be measured.
- Let the admin see an aggregate install and active count above the floor. This is not individual data, and without it no seat product renews. This is a challenge to the current admin contract, not to a founder decision.
- Run E9 (manager interviews) in v0, before the v1 engine, not "before any team-plane code". If no buyer exists, the free product needs a different funding plan (see problem 6), and the founder should know that before spending 16 to 24 engineer-weeks.

---

## 5. Everything is copyable, by design (major)

**What fails.** Engine, adapters, catalog, guide and record format are free and open source, and the format is published as a spec (PRODUCT.md 6.2, section 8). The research says the core must be open "or it will be forked or ignored" [research/users-market.md 3.2, point 5]. I agree. But the spec then names no part that stays scarce.

VibeWise has about 4.2k stars and is listed in the Anthropic plugin directory [verified: https://github.com/nykooi1/vibe-wise]. It lacks spaced review. Adding a scheduler like `record.py` with fixed intervals (3, 7, 21, 60, 180 days) is days of work, not months [unverified: estimate]. learn-while-build already has graded review and intervals of 1 to 60 days [verified: https://github.com/Pranavraut033/learn-while-build].

**Scenario.** Firsthand launches with a careful spec and a conformance table. Within a month VibeWise adds "Daily review: 3 questions from what you built". It already has the stars, the directory slot and the brand. Firsthand's better grading is invisible to a user browsing a directory.

**Smallest fix.** Name the scarce assets and protect them: the human-written unseen bank and Checkup tasks (licence them separately, as decision 9 already hints), the conformance results across surfaces (a public, maintained table is costly to copy because it must be re-run each release), and the brand. Launch only when at least one of these exists. Do not lead the launch with mechanics a rival can add.

---

## 6. Cost to build and maintain, with no funding line (major)

**What fails.** v0 is est. 4 to 6 engineer-weeks, v1 est. 16 to 24, v2 est. 20 to 30 (PRODUCT.md section 10). That is the spec's own estimate. The individual product is "free, forever", Sync is v2, Team is "later" and gated on interviews. There is no money before v2 at the earliest. On top, the unseen bank needs contracted authors, cost "needs to be measured" (6.4).

Maintenance is the larger cost. The parity table has about 20 surface rows (5.4). Hooks in VS Code Copilot are "in preview" [verified: research/surfaces.md, cited in PRODUCT.md 5.4], and Windsurf is now Devin per press [unverified]. Each surface change can break a conformance row. Founder decision 6 promises parity on all of them.

**Scenario.** A two-person team ships v1 after six months. In the next quarter, three vendors change hook event names or skill folder paths. Two "Tested" rows go red. The team spends the quarter on adapters instead of the bank or the team plan. Users on those surfaces see breakage and leave reviews in the directory.

**Smallest fix.**
- State a funding plan for the free product before v1: sponsorship (Exercism's model is in the research [verified: https://exercism.org/insiders]), a grant, or an approach to a vendor or a foundation. The research lists "sell to an agent vendor" as a possible exit (research/users-market.md section 5). Treat it as a plan option, not a footnote.
- Generate adapters from the one manifest (already in 6.1) and run conformance automatically in CI against each agent's headless mode, so a vendor change shows as a red row within a day, not a user report. Where a surface has no headless mode, it stays "Floor, untested". This keeps decision 6 as a promise with a visible status, which the spec already accepts.

---

## 7. The users most in need do not feel the need (major)

**What fails.** Segment 1 is juniors who "feel the pain" (PRODUCT.md 2.1). The spec's own source says the opposite: 85% of juniors say AI improved their understanding, while only 16% of seniors say juniors fully understand their AI code (BairesDev, a vendor survey [verified: https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/]). The research names this as "the gap the product sits in" (research/users-market.md 1.3). As a market, it means the people who need it most believe they do not.

Who will install it is a self-selected group: people already worried about their skill. They are the ones who would read diffs and ask why anyway. The research notes a "strong counter-voice: developers who read every diff and ask why say they stay sharp" [unverified: research/users-market.md 1.3]. A product used only by the already careful has a small market and a weak effect.

**Scenario.** Launch posts get strong engagement from senior engineers who like the idea and from a few anxious juniors. The juniors on deadline-driven teams, the actual target, never hear of it or skip it as "a second course" (research/users-market.md 2.1 quit reasons).

**Smallest fix.** Make the first touch a measurement, not a lesson, because the gap is between belief and fact. The first-session drill already exists. Frame it as "Can you still do this without your agent? Two minutes, on your own code." and show the result plainly. Then test which framing gets more installs and more day-7 return on the site (an extension of E9's button test). Separately, revisit the order of segments: the people who feel this pain and hold a budget are managers and course instructors, not juniors.

---

## 8. Model grading spends the user's plan, quietly (major)

**What fails.** Open answers (Explain back, Compare, parts of Call it) are graded by a model, graded twice with shuffled points (PRODUCT.md 6.5). Providers 2 and 3 run on the user's own agent plan. On top of that, the instruction file and skill load into every session on every agent. The spec makes cost visible (`firsthand cost`) and opt-in, which is good. But the user experiences cost as rate limits and slower sessions, not as a number on a screen. Whether headless grading is allowed by each vendor's terms is [unverified] (PRODUCT.md section 12).

**Scenario.** A user on a capped plan hits their limit on a Friday afternoon. They check `firsthand cost` and see grading and context use they did not think about. They uninstall. Or a vendor changes its terms for headless use and grading provider 3 stops working on that surface.

**Smallest fix.** v1 grades only what can be run (Trace, Check against fix commits, Replay, your line by tests). Model-graded moves wait until E8 reports cost per week per agent. This also removes the E5 dependency from v1 and shortens the build. State the token cost of the always-loaded instruction file at install; it needs to be measured.

---

## 9. Install touches every agent's user config; trust and review risk (major)

**What fails.** `firsthand init` writes to the user-level skill folder and instruction file of every agent it finds, plus an MCP server and hooks (PRODUCT.md 5.1). A tool that edits `~/.claude`, `~/.codex`, Cursor and Copilot settings in one command is what security teams block and what plugin directory reviewers look at hardest. The research says directories "warn that the user trusts what plugins run" and that the product must be easy to audit (research/users-market.md section 4). Review rules are [unverified] (PRODUCT.md 2.2). Hooks run shell commands on agent events, which is the most sensitive extension point on each surface.

**Scenario.** A company's endpoint security flags a new binary that registers hooks in four agents. IT blocks it. The engineer, who installed it privately, now has to explain it to IT, which is the exact surveillance-adjacent moment the spec works to avoid. Or a directory rejects the listing because the plugin installs into other agents.

**Smallest fix.** Default `init` to the one agent it was launched from (via that agent's own plugin directory), and offer "add Firsthand to Codex too?" as a second, per-agent yes. Publish exactly which files each adapter writes. This keeps decision 6 (every surface reachable) and lowers the trust cost of the first install.

---

## 10. No growth loop, because nothing can be shown (major)

**What fails.** The record is private, local and has no remote (decision 1, which I accept). The proof pack is "labelled self-graded" (5.3). "Only proctored live checks are evidence for anyone else" (4.9), and proctoring is "Later". Hiring is out of scope. So a user cannot show anyone what they gained. VibeWise grew through GitHub stars [verified: research/users-market.md 4], not through its product. Firsthand has no in-product reason for a user to tell someone else.

**Scenario.** A user's map shows real progress after three months. They have no way to share a result that anyone else believes. Word of mouth stays at "I use this thing", which is what every rival plugin also gets.

**Smallest fix.** Make the Checkup result shareable as a signed, verifiable statement: "Completed Checkup 2026-11, task pinned to commit X in repo Y, tests passed, graded by tests." Graded-by-tests results on a human-written task in a public repo are checkable by a third party without trusting the user's record. This stays inside decision 1 (the user chooses to export) and stays clear of hiring because it shows a task result, not a level.

---

## 11. Nothing to say at launch (major)

**What fails.** The claims ladder allows only "Designed around research on how people learn with AI" until a randomised study (PRODUCT.md 9.5). The study needs a power calculation from pilot data that does not exist yet (9.3). Rivals face no such rule and will claim freely. In a directory, "designed around research" loses to "learn while you vibe code".

**Scenario.** Launch day. The Firsthand listing says what it does and that no efficacy is proven. VibeWise's listing says it makes you a better engineer. Users pick the bolder claim.

**Smallest fix.** Keep the ladder; it is the brand. But use the rung below the study better: publish the method, the conformance table and the on-device numbers design partners chose to share, as data with their sample size stated. "We measure on you, and here is what 20 people saw" is honest and specific. Also make honesty itself the claim: "the only tool that tells you when you got worse". That claim is checkable from the product (levels go down) and needs no study.

---

## 12. The name and the space are crowded (minor)

**What fails.** "Firsthand" may collide with an existing careers product [unverified, PRODUCT.md 1]. The fallback "Ownline" is untested. The category already has at least five similar free plugins with near-identical names (research/users-market.md 3.2). E0 tests the name with 8 interviews but not with search: can a user find the product by typing its name plus "AI coding" in a directory?

**Smallest fix.** Add a findability check to E0: search the name in the Claude Code plugin directory, skills.sh, npm and a general web search, and record whether the product would be the first result. Pass rule is a founder decision.

---

## 13. Reading vendor learning modes as input ties the product to vendor formats (minor)

**What fails.** Firsthand reads vendor `TODO(human)` gaps as your-line events (PRODUCT.md section 8). This depends on an undocumented-as-stable output format of a vendor feature [verified that the feature exists: https://code.claude.com/docs/en/output-styles; stability unverified]. If the vendor changes the marker, events silently stop arriving.

**Smallest fix.** Treat vendor-mode import as a best-effort adapter with its own conformance row, shown as "Floor, untested" until tested, like every other surface.

---

## What I did not challenge

I accept founder decisions 1 to 7. Problems 1, 4 and 9 propose changes to spec defaults (reminder default, admin contract, init scope), not to the decisions. Problem 4 challenges the admin contract in `spec/teams.md` section 4, which is a spec choice, not a founder decision.

## Sources used in this review

- Shen and Tamkin, Anthropic: https://www.anthropic.com/research/AI-assistance-coding-skills
- Claude Code output styles: https://code.claude.com/docs/en/output-styles
- Claude Code memory, third-party guides: https://blog.memoryplugin.com/claude-code-memory/, https://www.engineerscodex.com/claude-code-auto-memory
- Cross-tool memory plugins: https://docs.cognee.ai/integrations/claude-code-integration, https://blog.walrus.xyz/how-to-add-portable-memory-to-claude-code-and-codex-with-walrus-memory/
- VibeWise: https://github.com/nykooi1/vibe-wise
- learn-while-build: https://github.com/Pranavraut033/learn-while-build
- BairesDev Dev Barometer Q2 2026: https://www.bairesdev.com/blog/dev-barometer-q2-2026-ai-career-reset/
- Anthropic Economic Index on software: https://anthropic.com/research/impact-software-development
- Copilot cloud agent: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent
- Exercism Insiders: https://exercism.org/insiders
