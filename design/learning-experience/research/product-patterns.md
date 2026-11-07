# Research track: product and UX patterns from the best tools

A pattern library for the learning-while-building experience. It studies how tools that developers trust move a person between contexts (desk, phone, notification, deep link), how they design inboxes, command palettes, quiet signals, progress, empty states and onboarding, and how adult learning products that experts respect structure practice. For each pattern it says what to copy, what to avoid, and why, and then maps it onto this skill.

Researcher: product and UX patterns track, one of five. Date: 2026-11-07. Sibling reports in this folder ([claude.md](claude.md), [codex-others.md](codex-others.md), [protocols.md](protocols.md)) cover the mechanisms (mods, Remote Control, deep links, push, MCP). This report covers the product behaviour those mechanisms should carry, and cites the siblings where a pattern depends on a mechanism.

## How to read the evidence marks

| Mark | Meaning |
| :- | :- |
| **[T]** | Verified by a test I ran in this session. The command and result are given. |
| **[D]** | Documented officially by the vendor or in a peer-reviewed or primary source I fetched. |
| **[D-lit]** | Established learning-science literature, cited from the canonical paper; I fetched the abstract or index but not the full text. |
| **[R]** | Reported by a third party (teardown, review, forum, press). |
| **[S]** | Speculative: my design inference. Needs a prototype or a test. |

## The ten findings that matter most

1. **The best tools do not move the user to the work; they move a small, complete unit of work to wherever the user is, and keep one source of truth behind it.** GitHub notifications sync read state across web, mobile and email [D]; Claude Code Remote Control keeps one session in sync across terminal, browser and phone [D]; Cursor agents run in the cloud and are picked up with "Open in Cursor" [D]. For us, the unit is one question card (prompt, context excerpt, answer field, confidence, "I don't know", "Not now"), and the truth is `.learning/` in the repo. Every door renders the same card.
2. **Calm technology is a design requirement, not a tone.** Weiser and Brown: "The individual, not the environment, must be in charge of moving things from center to periphery and back" [D]. Amber Case: "Technology should require the smallest possible amount of attention" and "can communicate, but doesn't need to speak" [D]. The learning layer must default to periphery (a count, a band, a badge) and come to the centre only on the learner's gesture or at the two moments that research supports: just before a build (prediction) and just after it works (explain-back).
3. **Suppress signals when the person is present.** Claude Code skips phone pushes while the learner is typing in or focused on the connected terminal, and a presence file extends that to "any time you are at the machine" [D]. This is the single most important notification rule to inherit: never ping the phone about a question the learner can see on the screen in front of them.
4. **Back off when ignored, and say so once.** Duolingo's own KDD paper shows that repeating the same reminder template loses its effect, so they apply a recency penalty [D]; third parties report a final "These reminders don't seem to be working. We'll stop sending them for now." [R]. For us: at most one review nudge a day, a different question each time, and after three ignored nudges, stop and leave a single line in the inbox.
5. **Progress should show retention and transfer, not activity.** GitHub's PR "Viewed" bar counts real units and un-ticks a file when it changes [D]; Quantum Country reports "days of demonstrated retention" per card [D]; Anki shows due counts, not points [D]. Execute Program is a cautionary note: Andy Matuschak observed its "progress mechanics emphasize completing new lessons over increasing recall duration" [R]. Our record (not yet, with help, recalls, transfers, per dimension) is already the right shape. Add decay: a cell that was "recalls" in March and missed last week shows as weak, as the site already promises.
6. **Streaks are the wrong lever for this audience.** Duolingo reports that a 7-day streak predicts continuation (2.4 times) and that "streak freeze" slack motivates [D, vendor-reported correlation], but streaks shift attention to protecting the number [R], and the learner here is building a large project with uneven days. Use Anki's model instead: work arrives when due, a backlog is capped and smoothed ("Easy Days", review limits) [D], and missing a day costs nothing but a slightly later review.
7. **Teach the expert interface in context, once, with the real action.** Linear asks the new user to press the Cmd K shortcut on a big keycap during onboarding and teaches C for "create issue" by doing it [R]; Raycast puts every action's shortcut on the action bar so it is learnt by use [D]. Arc's founder said Arc was "too different, with too many new things to learn, for too little reward" [D]. Our onboarding is one real question on the learner's real code within the first session, plus one line that names the two commands. Nothing else.
8. **Agents must show their state and step back when asked.** Linear's Agent Interaction Guidelines: disclose identity, "inhabit the platform natively", acknowledge instantly, make internal state visible (thinking, waiting, executing, finished), "respect requests to disengage", and keep a human accountable [D]. The learning layer is an agent behaviour and should follow all six. "Not now" must be a first-class action that stops questions for the session and is honoured exactly.
9. **Confidence is a product feature, not a form field.** Metcalfe's review: high-confidence errors are corrected more readily than low-confidence ones (hypercorrection) [D-lit]. Anki's four buttons are a self-rated confidence scale shown with the next interval [D]. Our card should take confidence as one tap, in the same row as submit, and the feedback for a confident miss should say plainly that it was a confident miss and that it returns tomorrow, exactly as the approved site demo already does.
10. **The record ramp is not accessible on its own colour.** I computed WCAG contrast for the approved palette [T]: the "with help" segment #F6C9AF is 1.37:1 on paper and 1.51:1 on white; "recalls" #EE8B5B is 2.25:1 and 2.48:1; only "transfers" #C2410C (4.71:1 on paper) passes the 3:1 non-text minimum (WCAG 1.4.11). Every record cell needs a second cue: a 1.5px ink outline on filled cells, a level glyph or a text label, and a table alternative. The colours stay; they stop being the only carrier.

## 1. Handoffs between contexts

The question is how a learning moment that starts in a build (desk, terminal, Claude Code in the Claude app) can be finished on the phone, in a notification, or later, without the learner losing their place in either the build or the learning.

### 1.1 What the leaders do

| Product | Handoff mechanism | What it gets right | Mark |
| :- | :- | :- | :- |
| Claude Code Remote Control | One local session, driven from terminal, claude.ai/code and the Claude app; QR code from `/rc`; `/rc active` indicator in the terminal; push "when a long-running task finishes or when Claude needs a decision"; pushes skipped while the user is typing or focused on the terminal; `CLAUDE_CLIENT_PRESENCE_FILE` extends suppression to the whole machine | The work stays where it is; every surface is a window onto it. Presence-aware suppression. | [D] [docs](https://code.claude.com/docs/en/remote-control) |
| GitHub notifications | Web inbox, GitHub Mobile inbox and email share read state; "Done" and "Saved" states; a reason label on each item (review requested, mention); push only for mentions, assignments, review requests and deployment approvals; working-hours schedule for push | Push is reserved for items addressed to you. Reason labels tell you why it is here before you open it. | [D] [docs](https://docs.github.com/en/subscriptions-and-notifications/get-started/configuring-notifications) |
| GitHub Copilot coding agent | Sessions start from issues, chat, the Agents tab, or mobile; session logs; cloud sandbox sessions "can move between web, mobile, and local clients"; Actions-based sessions are web only | Long work runs off-device and is reviewable from anywhere; the log is the shared state. | [D] [docs](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) |
| Cursor web and mobile agents | PWA with push "when agents complete tasks"; "Open in Cursor" continues the agent's work in the IDE; Slack trigger and completion notice | A single, obvious button that carries the work back to the desk. | [D] [docs](https://docs.cursor.com/background-agent/web-and-mobile) |
| Linear agents | Delegation sets a `delegate`, not the assignee, so "humans keep ownership"; the agent must emit a `thought` within 10 seconds; session state shown to users automatically | Ownership never moves to the agent; acknowledgement is fast and visible. | [D] [developers](https://linear.app/developers/agents), [AIG](https://linear.app/developers/aig) |
| Raycast | Deep links into extensions and commands; the action panel shows shortcuts | Any command is addressable from outside. | [D] for action panel ([blog](https://www.raycast.com/blog/a-fresh-look-and-feel)); deeplink manual page returned 404 to my fetch, so the link format is [R] here |
| Arc | Little Arc (a separate small window for a link opened from elsewhere) and Peek (preview a link without leaving the pinned tab) | Open the foreign thing in a lightweight container that dismisses back to where you were. | [R] (third-party guides; Arc is in maintenance) |

### 1.2 Patterns to copy

**H1. One unit, many doors.** Define the question card once: id, dimension, prompt, code excerpt with `path:line`, answer field, confidence (low, medium, high), "I don't know", "Not now", and a link to the build context. Render the identical card in chat, in the Claude Code mod pane, in the terminal (`learning.py answer`), on the local page, on the hosted artifact, and in a push body (prompt only). Every door writes the same event to `.learning/` (or the artifact `db`, pulled into it). This is how GitHub keeps web, mobile and email consistent. [S, built on D]

**H2. Peek, then return.** Copy Arc's Peek and Cursor's "Open in Cursor": the learning card opens as a lightweight overlay (mod pane, sheet on the phone, a modal on the hosted page) that closes back to exactly the build context it came from. After the answer, the overlay shows the one-line feedback and a single button whose label names where it returns: "Back to the build". No second screen, no dashboard detour. [S]

**H3. A reason on every item.** GitHub labels why a notification is in the inbox. Every learning item should carry its reason in four words or fewer: "Before: checkout emails", "After: retry fix", "Review: 21 days", "Missed yesterday", "Drill: injected bug". This replaces any need for the learner to remember why they are being asked. [S, pattern D]

**H4. Presence decides the door.** Copy Claude Code's rule exactly: if the learner is at the machine (typing, focused, or presence file present), show the question in the build surface and do not push. If a Remote Control device is attached and the terminal is idle, push one line to the phone and open the hosted card. If nothing is attached, the item waits in the inbox and a scheduled cloud task delivers due reviews later. The mod API exposes `session.attach` and `detach` events for this (see [claude.md](claude.md) finding on surfaces). [D mechanism, S policy]

**H5. Acknowledge at once, grade fast.** Linear's agents must emit a thought within 10 seconds. A submitted answer should show "Saved." immediately (local write), then the grade as soon as it is ready, in place, without a page change. When grading has to wait for the build session, say "Saved. Graded at the next pause." so the learner is not left wondering. [D pattern, S application]

**H6. The learner owns the record; the agent is the delegate.** Linear keeps humans as assignees and agents as delegates. Mirror it in language and UI: "Your record", "The agent graded this against the answer it wrote before asking". Never show the agent as the author of progress. The approved site already says this ("What it cannot prove"). [D pattern]

### 1.3 Patterns to avoid

- **Handoff by re-explanation.** Making the learner re-read the context on the phone because the card did not carry it. Every card carries its own excerpt and diagram, sized for a phone.
- **Deep links that do work on open.** Claude's deep links fill a prompt and never send it [D, see [claude.md](claude.md)]; keep that. A link opens the card; only the learner's tap commits an answer.
- **Different state on different doors.** If the terminal says a question is waiting and the phone says it is answered, trust is gone. One store, append-only events, last-writer conflict shown as "Answered on phone at 14:02".
- **Custom-scheme links on the public site.** GitHub strips custom schemes, so the Pages site can only use https links to hosted cards [D, see [claude.md](claude.md)].

## 2. Inbox design

### 2.1 What the leaders do

**Linear Inbox** [D] ([docs](https://linear.app/docs/inbox)): two tabs, Priority (default) and Other; J and K to move; U for read and unread; H to snooze or set a reminder, with free-text times ("next quarter"); Backspace to delete, Shift Backspace to delete all read; a cap of 2,000 open items; reminders that land in the inbox at a chosen time.

**GitHub notifications** [D]: Done and Saved; bulk triage; preview the source item without leaving the inbox; custom filters; grouping by repository or date; inbox items kept 3 months, saved items indefinitely.

**Anki deck list** [D] ([docs](https://docs.ankiweb.net/studying.html)): three counts per deck (New, Learn, Due), "Study Now", and a daily review limit that "smooths out spikes in due cards and prevents a flood of reviews after time away" ([deck options](https://docs.ankiweb.net/deck-options.html)).

### 2.2 Patterns to copy

**I1. A learning inbox with exactly three groups.** "Now" (before or after the current build, at most one), "Due" (reviews whose gap has passed, capped), "Later" (snoozed). Counts in mono beside each group, like Anki's three numbers. No "Other" tab: everything here is addressed to the learner. [S]

**I2. Snooze as a first-class verb, with plain-language times.** Linear's H. "Not now" on a card snoozes it to the next natural pause (end of the current build), "Tomorrow", or a typed time. Snooze never counts as a miss. [D pattern]

**I3. Done means graded, and done items leave.** GitHub's Done. After grading, the item leaves the inbox and its effect shows in the record. History lives in the record view, not the inbox. [D pattern]

**I4. Cap and smooth.** Anki's lesson: a flood of due items after time away is the commonest reason people quit SRS [D]. Cap Due at five shown items a day; overflow moves forward with a note "3 more tomorrow". Never show a frightening backlog number. [D pattern, S cap]

**I5. Keyboard grammar that matches Linear and GitHub.** J and K (or arrows) to move, Enter to open, H to snooze, number keys 1 to 3 for confidence, Cmd Enter to lock the answer, Esc to close. Show the keys on the action bar (see Raycast below). Learners who live in Linear will have these in their hands already. [D pattern]

### 2.3 Patterns to avoid

- **Unbounded inboxes** that grow while the learner is away.
- **Mixing build notifications with learning items.** The build already has its own signals (turn complete, permission). Learning items must not compete; they wait for the pause.
- **Red badges for learning.** Red means something is broken. A count in ink or the accent colour, never a red dot.

## 3. Command palettes and keyboard-first entry

### 3.1 What the leaders do

Raycast's redesign [D] ([blog](https://www.raycast.com/blog/a-fresh-look-and-feel)): the search bar is the main entry because "almost every interaction goes through it"; a bottom action bar shows the navigation title and toasts on the left and context actions with their shortcuts on the right, so users learn shortcuts by seeing them; Cmd K opens the full action list; a compact mode; toasts inside the window. Linear teaches Cmd K during onboarding [R]. Arc's command bar is a Spotlight-style search for sites, tabs and history [R].

Accessibility of a palette is the WAI-ARIA combobox pattern with a listbox popup [D] ([APG](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/)): DOM focus stays in the input, the active option is exposed by `aria-activedescendant`, Down and Up move, Enter runs the default action, Escape closes and returns focus, `aria-expanded` reflects visibility, and the input has an accessible name.

### 3.2 Patterns to copy

**C1. One verb namespace across harnesses.** Every harness gets the same small set of commands, spelled the same: `/learn` (show the waiting card), `/learn quiz`, `/learn drill`, `/learn record`, `/learn explain <PR or path>`, `/learn not-now`. In Claude Code these are a plugin command and a mod command; in Codex, a prompt or skill alias; in a terminal, `learning.py` subcommands with the same names. Consistency is what makes a palette learnable. [S]

**C2. The action bar teaches the keys.** On every card, a bottom bar like Raycast's: left, where you are ("Review: retry backoff, 21 days"); right, the actions with keys ("Lock answer Cmd Enter", "Hint H", "I don't know", "Not now Esc"). The site's pill buttons carry the label; a mono key cap sits beside each label. [D pattern]

**C3. On the hosted page, a real palette.** Cmd K on the hosted record page opens a combobox over dimensions, topics and due items ("debugging", "idempotency", "due"). Built to the APG pattern above. [S]

### 3.3 Patterns to avoid

- **Palettes as the only route.** Every palette action also needs a visible button for touch and for people who do not use shortcuts.
- **Shortcuts that collide with the host.** In Claude Code, the prompt owns most keys. Inside the build surface, the card takes keys only while it has focus.

## 4. Quiet notifications and calm technology

### 4.1 Principles and evidence

- Calm Technology principles (Amber Case) [D] ([calmtech.com](https://calmtech.com/)): smallest possible attention; inform and create calm; use the periphery; communicate without speaking; work even when it fails; the minimum technology needed; respect social norms. "A calm technology will move easily from the periphery of our attention, to the center, and back."
- Weiser and Brown, "Designing Calm Technology" (1995) [D] ([paper](https://calmtech.com/papers/designing-calm-technology)): centre and periphery; "locatedness" (the feeling of knowing what is happening around you); the Dangling String that twitches with network traffic; inner office windows; "Less is more, when less bandwidth provides more calmness."
- Duolingo's notification bandit (Yancey and Settles, KDD 2020) [D] ([paper](https://research.duolingo.com/papers/yancey.kdd20.pdf)): novelty effects mean templates the user has not seen recently work better; a recency penalty with a decay half-life beat the baseline; one practice reminder a day is the frame.
- Badging API [D] ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/Badging_API)): `navigator.setAppBadge(n)` and `clearAppBadge()` show a count or flag on an installed web app's icon, "less intrusive than a notification", usable from a service worker on push; limited browser availability.
- Apple interruption levels (passive, active, time-sensitive, critical): the HIG page did not render for my fetch, so this is from Apple's `UNNotificationInterruptionLevel` API as I know it [S, check against the HIG]. The useful idea: a learning nudge is always "passive" (no sound, no screen wake), never time-sensitive.

### 4.2 Patterns to copy

**N1. Four rungs of signal, chosen by the learner's presence.** From most peripheral to most central:

| Rung | Signal | When | Example copy |
| :- | :- | :- | :- |
| 0 | Nothing visible; item in inbox | Learner busy in the build, mid-turn | (none) |
| 1 | A faint count in the periphery: mod band above the prompt, spinner suffix, tab title or app badge | A question is waiting and the build is idle | "1 question" |
| 2 | One passive push or desktop notice | Learner away from the machine, a Remote Control device attached, a pause in the build | "1 question about the retry fix. About 1 minute." |
| 3 | Question in the centre (chat message, `AskUserQuestion`) | Only at the two research-backed moments: before a build starts and right after it works, and only if the learner opted into that mode | "Before I write this: the API stops after the save. What does the customer see?" |

The learner moves things between rungs, never the environment: "Not now" drops to rung 0 for the session. [D principles, S table]

**N2. One push a day, maximum, and a new question each time.** Duolingo's recency result says the same template stops working [D]. Each push names a different topic. [D, S cap]

**N3. Back off and say so once.** After three ignored pushes, send nothing more and leave one inbox line: "Reviews paused. Run /learn when you want them back." Third-party reports say Duolingo does a version of this [R]; our version carries no guilt. [S]

**N4. Push copy states the cost.** "About 1 minute" tells the learner what they are agreeing to. Never a teaser ("You won't believe..."), never a mascot voice. [S]

**N5. The badge is the dangling string.** On the hosted page installed to the phone home screen, `setAppBadge(dueCount)` gives a peripheral signal with no interruption at all; clear it as items are graded. Feature-detect; it fails quietly where unsupported, which is calm principle six ("work even when it fails"). [D API, S use]

**N6. Silence at the machine.** Inherit Claude Code's presence rule and `CLAUDE_CLIENT_PRESENCE_FILE` [D]. A learning push while the learner is at the desk is a bug.

### 4.3 Patterns to avoid

- **Loss-framed copy** ("Your streak is about to end!"). It works on engagement and against calm.
- **Sound** for any learning signal.
- **Notifications during a build turn.** The prediction question is asked before the build starts, or not at all for that build.
- **Notifications the learner cannot turn off in one step.** Every push carries "Pause reviews" as its action.

## 5. Progress visualisation without gamification

### 5.1 What the leaders do

| Product | Progress shown | Lesson | Mark |
| :- | :- | :- | :- |
| GitHub PR review | "Viewed" checkbox per file, a header bar counting viewed files; a file un-ticks when it changes | Progress counts real units and decays honestly when the ground changes | [D] [docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request) |
| Anki | New, Learn and Due counts; next interval shown on each answer button | Shows the consequence of an answer before you commit it | [D] |
| Quantum Country | "Demonstrated retention" in days per card; after six reviews most users near 6,000 days over 112 cards; a miss drops one level | Measures what matters (retention), and a miss is a step back, not a reset | [D] [Matuschak and Nielsen](https://numinous.productions/ttft/) |
| Execute Program | Lessons unlock only after prerequisite reviews pass; failing a review lowers the item's level rather than resetting it [R]; progress emphasises finished lessons over recall duration [R] | Gate on retention, not completion; but the visible progress still rewards new content | [R] [notes](https://notes.andymatuschak.org/Execute_Program) |
| Brilliant | Streak: 3 problems or one lesson a day; "streak charge" protects a missed day | Low bar plus slack; still a streak | [D] [help](https://brilliant.org/help/using-brilliant/what-is-a-streak) |
| Duolingo | 7-day streak predicts continuation 2.4 times; separating the streak from a daily goal; streak freeze | Strong for habit formation in daily consumer practice; vendor correlations | [D, vendor-reported] [blog](https://blog.duolingo.com/how-duolingo-streak-builds-habit) |

### 5.2 Patterns to copy

**P1. The record grid is the progress view.** Rows are dimensions (design, data, concurrency, debugging, security, and the learner's own); each row is a strip of topic cells; each cell's fill is the level reached without help (not yet, with help, recalls, transfers) using the approved ramp. This is the site's existing visual. [D in repo]

**P2. Best and latest, side by side.** The site promises: "If your answer was good in March and wrong last week, the record shows that idea as weak." Show it like GitHub's un-ticked Viewed: the cell keeps its best level as a thin outline and its current fill drops to the latest level. One glance shows decay. [S]

**P3. Show the consequence on the button, like Anki.** After grading, the feedback line names when this returns: "Correct. Back in 21 days." "No. Back tomorrow." This is information, not reward, and it makes the schedule legible. [D pattern]

**P4. A miss steps back one gap, not to zero.** Quantum Country and (reportedly) Execute Program drop one level on a miss. The skill's rule ("a miss returns next day") is compatible if the next success restores the prior gap rather than restarting at 3 days. Check this against `learning.py` scheduling before promising it in UI copy. [D pattern, S for our scheduler]

**P5. Unaided work counts and is marked.** The site says commits or tests that show unaided work count. Mark those cells with a small "own work" tick (the site's `tick` class) so the learner sees evidence that does not come from quizzes. [S]

**P6. Weekly summary, not daily score.** Once a week, a three-line summary: "This week: 4 recalls, 1 transfer (idempotency in the payment worker). Weakest: debugging timeouts. 2 due tomorrow." Plain, no comparison to others. [S]

### 5.3 Patterns to avoid

- **Streaks, XP, levels-as-points, leagues, badges for activity.** Brilliant and Duolingo use them for daily consumer habits; our learner is doing deep work on uneven days, and the Shen and Tamkin result is about understanding, not frequency.
- **Percent-complete bars.** There is no completion in engineering skill. Show levels, not percentages.
- **Celebration animations.** The approved motion is "faint record cells that light up". A cell lighting from "with help" to "recalls" is the whole celebration.
- **Hiding decay.** A record that only goes up is not a record.

## 6. Empty states

Empty states are where a quiet product explains itself. The best ones (Linear, GitHub) say what will appear, why it is empty, and the one action that fills it. Linear also avoids a truly empty first workspace by pre-populating demo data [R] ([teardown](https://www.candu.ai/blog/linear-onboarding-teardown)).

| Surface | Empty state copy (plain, STE style) | Action |
| :- | :- | :- |
| Inbox, nothing due | "Nothing is due. The next review is on 14 November." | none, or "Quiz me now" |
| Inbox, first run | "Questions appear here before and after a build. Start a task and the agent asks one." | "Ask me one now" |
| Record, first run | "Your record is empty. It fills when you answer questions about this project." Show the grid with faint cells for the dimensions the learner picked, not a blank page. | "Pick areas" |
| Record, dimension with no topics | "No topics yet in security. The agent adds one when a change touches it." | none |
| Explainer list | "No explainers yet. Ask: 'explain PR 128'." | copy-to-clipboard of the prompt |
| Phone, offline | "You are offline. Your answer is saved on this phone and sent when you are back online." | none |

Patterns: **E1.** Show the shape of the full state faintly (the record grid with unlit cells), like the site's faint cells, so the empty page teaches the layout. **E2.** Name the date of the next thing. **E3.** One action, or none. [S, Linear pattern R]

Avoid: illustrations with mascots, "Nothing here yet!" with an exclamation mark, and fake demo data in the learner's own record (Linear's demo data is right for a team tool; in a record of what you can do, fake data would be a lie).

## 7. Onboarding that respects expert users

### 7.1 Evidence

- Linear: drops users into a workspace with content, asks them to press Cmd K on a large keycap, teaches C for create by doing it; shortcuts shown on hover [R] ([teardown](https://www.candu.ai/blog/linear-onboarding-teardown), [growth dives](https://growth-dives.kit.com/posts/growth-dives-inside-linear-s-onboarding-3-things-i-didn-t-expect)).
- Raycast: shortcuts on the action bar teach by repetition [D].
- Arc: "too different, with too many new things to learn, for too little reward"; "Only 5.52% of daily active users regularly use more than one Space" [D] ([letter](https://browsercompany.substack.com/p/letter-to-arc-members-2025)).
- Anki: you can use only Again and Good "if four buttons are too many" [D]. Respecting experts includes letting them simplify.

### 7.2 Patterns to copy

**O1. First value in the first build.** No tour. Install, then on the learner's next real task the agent asks one prediction question about their own code. The first thing the learner sees from the skill is a good question, not a settings page. [S]

**O2. One setup question, asked when it is needed.** Dimensions are chosen the first time the record is shown, prefilled from the repo (languages, presence of queues, auth code), editable in one line. [S]

**O3. Name two commands, once.** After the first answer: "To see waiting questions: /learn. To stop questions for now: /learn not-now." Then never repeat it. [S]

**O4. Modes, not settings.** Offer three plainly named modes the learner can switch with one command: "Quiet" (reviews only, no build questions), "Normal" (one before, one after), "Deep" (adds drills and explainers). This is the Anki "two buttons are fine" lesson: let the expert pick the load. [S]

**O5. Spend the novelty budget in one place.** Arc's lesson. The new idea here is "the agent asks you before it builds". Everything else (inbox, palette, keys, cards) should feel like Linear and GitHub so nothing else needs learning. [D lesson, S application]

### 7.3 Avoid

Product tours, coach marks over the terminal, a welcome modal, email drip onboarding, and asking for preferences before showing any value.

## 8. Learning products for adults that experts respect

### 8.1 Anki

What to copy [D] ([studying](https://docs.ankiweb.net/studying.html), [deck options](https://docs.ankiweb.net/deck-options.html)): the question alone first, answer revealed on a gesture; four self-graded buttons with the next interval printed on each; the advice that partial recall counts as a fail "if it would fail in real life"; FSRS desired retention defaulting to 90% and the warning that workload climbs steeply near 100%; daily limits that prevent review floods; Easy Days. What to avoid: self-grading as the only grade (our rubric-first grading by the agent is stronger for open answers, and confidence plays the role of Anki's buttons); card-only prompts with no context.

### 8.2 Execute Program

What to copy [R] ([Matuschak notes](https://notes.andymatuschak.org/Execute_Program), [site](https://www.executeprogram.com/spaced-repetition)): every prompt is executable, so prompts are both application and recall; lessons are short; prose unfolds in response to interaction; later lessons gate on reviews of their prerequisites; missed answers carry no penalty unless the learner gives up. For us, the debugging drill and code-level prediction are our executable prompts: the learner can run the code to check a prediction after locking it. What to avoid: progress that rewards new lessons over recall duration (Matuschak's critique). The Execute Program pages themselves returned only a title to my fetch, so their claims here come through Matuschak's notes and search snippets.

### 8.3 Quantum Country and Orbit (the mnemonic medium)

What to copy [D] ([Matuschak and Nielsen](https://numinous.productions/ttft/), [Orbit repo](https://github.com/andymatuschak/orbit)): prompts embedded in the reading itself (our explainer pages: predict before reveal); review sessions delivered by email a few days later; intervals of in-text, 5 days, 2 weeks, a month, rising to 4 months after five successes; a miss drops one level; about 95 minutes of review for about 4 hours of reading; in a small test, delayed reviews made 40% of users worse. Orbit is open source (Apache 2.0 libraries, a `web-component` for embedding prompts in any page), which makes it a reference implementation for embedding review prompts in our explainer pages. What to avoid: the authors themselves retracted one early claim after a data error; keep our "What it cannot prove" honesty.

### 8.4 Brilliant

What to copy [D]: problem first, explanation second ("learn by doing"); a low daily bar (3 problems or one lesson); slack (streak charge). What to avoid: the streak, and generic content. Our questions come from the learner's own code, which is the advantage no course product has. Brilliant's "6x more effective" claim is marketing, not a study [R].

### 8.5 Exercism mentoring

What to copy [D] ([mentoring FAQ](https://exercism.org/docs/mentoring/faqs)): the student asks for review of a specific iteration; discussion is attached to that iteration; the student can submit a new iteration in response; either side can end the discussion. Exercism also tested renaming "Request mentoring" to "Submit for Code Review" [R] ([forum](https://forum.exercism.org/t/renaming-mentoring-to-code-review/4236/49)), which shows that naming the action as engineers name it matters. For us: the explain-back is an "iteration" the learner can revise once after feedback, and the restatement after a miss is a second iteration of the same attempt (the skill already says it is part of the attempt). What to avoid: open-ended threads; ours are one question, one answer, one feedback, at most one restatement. My fetches of two Exercism docs pages returned 404, so detail on the current request flow is thin.

### 8.6 Duolingo learning team

What to copy [D]: notification optimisation with a recency penalty; "lowering the barriers to building a consistent daily habit is more important ... than how much you learn each day, at least early on" (vendor finding); slack beats rigid rules. What to avoid: the mascot voice, guilt, and leaderboards. Take their science of timing and novelty, not their tone.

## 9. Learning-science constraints that the UI must enforce

These are not product patterns from tools, but every pattern above must respect them, and they decide several UI details.

| Principle | Source | UI consequence | Mark |
| :- | :- | :- | :- |
| Retrieval practice beats re-reading (testing effect) | Roediger and Karpicke 2006, Psychological Science | The card asks before it shows. The answer and the rubric are never on the same screen as the question until the answer is locked. | [D-lit] |
| High-confidence errors are corrected more readily (hypercorrection) | Metcalfe 2017, Annual Review of Psychology 68:465-489 ([PubMed](https://pubmed.ncbi.nlm.nih.gov/27648988/)) | Confidence is collected before reveal, in one tap. Feedback for a confident miss names it and shows the reason with evidence. | [D-lit] |
| Generating before instruction helps later transfer (productive failure) | Kapur 2008 and later, Cognition and Instruction | The prediction question comes before the agent builds. "I don't know" is allowed and is graded as a miss without penalty. | [D-lit] |
| Desirable difficulties: spacing, interleaving, generation | Bjork and Bjork 2011, "Making things hard on yourself, but in a good way" | Review queue interleaves dimensions; the schedule gaps (3, 7, 21, 60, 180) are shown, not hidden. | [D-lit] |
| Delayed review loses retention | Matuschak and Nielsen, Quantum Country data | A gentle nudge when items are overdue is justified, within the caps above. | [D] |

## 10. Accessibility patterns

**A1. Second cue for every colour.** Verified [T]: contrast of the approved colours on paper #F5F4F0 and white:

| Colour | Role | On paper | On white | Passes 3:1 non-text? | Passes 4.5:1 text? |
| :- | :- | :- | :- | :- | :- |
| #16161A | ink | 16.40 | 18.04 | yes | yes |
| #C2410C | text-safe accent, transfers | 4.71 | 5.18 | yes | yes |
| #E8541E | accent | 3.34 | 3.67 | yes | no (large text only) |
| #EE8B5B | recalls | 2.25 | 2.48 | no | no |
| #F6C9AF | with help | 1.37 | 1.51 | no | no |
| #DAD8D0 | card border | 1.30 | 1.43 | no (decorative) | no |

Adjacent ramp steps are also close: #F6C9AF against #EE8B5B is 1.64:1, #EE8B5B against #C2410C is 2.09:1. Command: a Python WCAG relative-luminance calculation run in this session. Fix without changing the palette: outline filled cells in ink at 1.5px, add a level glyph (for example one, two, three short bars) or the level word in the cell's accessible name, and give the grid a table view. Never use #E8541E for body text.

**A2. Live regions for grades.** The site already uses `role="status"` for the demo result [T: found in docs/index.html line 216]. Every door that grades in place should announce "Correct." or "No." through a polite live region, and move focus to the feedback only when the learner requested the grade.

**A3. Reduced motion.** The site respects `prefers-reduced-motion` in both site.css and site.js [T: one match in each]. Carry the same rule into the hosted artifact and the local page: cells change state without animation when reduced motion is set.

**A4. Keyboard and target size.** Palette per APG combobox [D]. Pill buttons at least 24 by 24 CSS px (WCAG 2.2 target size minimum), 44 by 44 on the phone card. Confidence options are a radio group, not three loose buttons.

**A5. Plain language as accessibility.** STE-style copy, one idea per sentence, is also the right reading level for a tired engineer on a phone. The skill's Voice section already requires messages "short enough to read on a phone".

## 11. Putting it together: the seamless loop, as a storyboard

This is the composite behaviour the patterns imply. It depends on mechanisms documented in the sibling reports; it has not been built. [S throughout]

1. **At the desk, before a build.** The learner asks Claude Code for a change. Before writing code, the agent asks one prediction question in chat (rung 3), or, in Quiet mode, puts it in the inbox and shows "1 question" in the mod band (rung 1). The card carries reason "Before: checkout emails", the diagram, three options plus free text, confidence, "I don't know", "Not now".
2. **Answer locks; build proceeds.** "Saved." appears at once. The agent builds. The answer is graded against the pre-written rubric when the build pauses, so the build is never blocked by grading.
3. **After it works.** One explain-back card. Feedback: "Not quite. The retry is safe because the charge is idempotent on order id (payments.py:41). Your answer said the timeout makes it safe. Back tomorrow." Plus one restatement field.
4. **Away from the desk.** The learner leaves. The presence file is gone, a Remote Control device is attached. Due review exists. One passive push: "1 question about idempotency. About 1 minute." Tapping opens the hosted card (artifact) on the phone, the same card. Answer, confidence, lock. Grade on the page. Badge clears.
5. **Back at the desk.** The mod band reads nothing, because the inbox is empty. The record cell for idempotency has lit from "with help" to "recalls". `/learn record` shows it with best and latest.
6. **Weeks later, nothing open.** A scheduled cloud task reads `.learning/`, finds the 21-day review, updates the hosted card and pushes once. If ignored three times, it stops and leaves a line.

Transitions are seamless because the same card, the same keys, the same copy and the same store appear at every step; the only thing that changes is the rung of signal, and presence decides it.

## 12. Anti-pattern list (summary)

| Anti-pattern | Seen in | Why it is wrong here |
| :- | :- | :- |
| Streaks and loss-framed reminders | Duolingo, Brilliant | Rewards frequency over understanding; guilt breaks calm. |
| Percent-complete progress | Course products | Skill has no completion; hides decay. |
| Interrupting mid-task | Most push systems | Destroys flow; research moments are before and after, not during. |
| Pushing to the phone while the learner is at the desk | Naive notifiers | Duplicates the signal; Claude Code already solved this. |
| Novel interface everywhere | Arc | Novelty tax; spend it once. |
| Praise and mascots | Consumer learning apps | Violates the skill's Voice; carries no information. |
| Self-grade only | Anki for open answers | Learners over-rate; rubric-first grading is the fix. |
| Fake demo data in the record | Linear (fine there) | A record of ability must contain only real evidence. |
| Colour as the only level cue | Many heatmaps | Fails WCAG 1.4.11 with this ramp [T]. |
| Backlog floods after time away | Early Anki users | The commonest reason people quit SRS. |

## 13. Cheapest experiments

| Experiment | Cost | What it settles |
| :- | :- | :- |
| Static HTML of the question card at 375px and 1280px in the site language, with the action bar and key caps; screenshot both | 1 hour | Whether one card works on every door before any plumbing. |
| Add ink outlines and level glyphs to the record grid on a copy of the site, re-run the contrast script, test with a greyscale filter | 30 minutes | Fixes A1 without changing the palette. |
| Hosted artifact card on the phone with `setAppBadge` feature-detected; install to home screen on iOS and Android | 1 hour | Whether the peripheral badge works on the owner's phone (limited availability per MDN). |
| Mod band "1 question" plus `/learn` opening the pane, with `session.attach` switching to push | 2 hours (probe mod exists per [claude.md](claude.md)) | Presence-driven rung selection end to end. |
| Seven-day diary: owner uses Quiet, Normal and Deep modes on real work and logs every interruption that felt wrong | 7 days, low effort | Calibrates caps (one push a day, five due items) to a real engineer. |
| Check `learning.py` behaviour after a miss followed by a success (does the gap restore or restart?) | 15 minutes | Whether UI copy "back in N days" is truthful (P4). |

## Sources

Primary and official: [Linear Inbox](https://linear.app/docs/inbox), [Linear agents in Linear](https://linear.app/docs/agents-in-linear), [Linear agent developer docs](https://linear.app/developers/agents), [Linear Agent Interaction Guidelines](https://linear.app/developers/aig), [Linear Method](https://linear.app/method), [GitHub notifications](https://docs.github.com/en/subscriptions-and-notifications/get-started/configuring-notifications), [GitHub PR review](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request), [GitHub Copilot coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent), [Cursor web and mobile agents](https://docs.cursor.com/background-agent/web-and-mobile), [Claude Code Remote Control](https://code.claude.com/docs/en/remote-control), [Raycast redesign post](https://www.raycast.com/blog/a-fresh-look-and-feel), [Browser Company letter to Arc members](https://browsercompany.substack.com/p/letter-to-arc-members-2025), [Calm Technology principles](https://calmtech.com/), [Weiser and Brown, Designing Calm Technology](https://calmtech.com/papers/designing-calm-technology), [Yancey and Settles, KDD 2020](https://research.duolingo.com/papers/yancey.kdd20.pdf), [Duolingo streak post](https://blog.duolingo.com/how-duolingo-streak-builds-habit), [Brilliant streak help](https://brilliant.org/help/using-brilliant/what-is-a-streak), [Anki studying](https://docs.ankiweb.net/studying.html), [Anki deck options](https://docs.ankiweb.net/deck-options.html), [Matuschak and Nielsen, How can we develop transformative tools for thought](https://numinous.productions/ttft/), [Orbit](https://github.com/andymatuschak/orbit), [Exercism mentoring FAQ](https://exercism.org/docs/mentoring/faqs), [MDN Badging API](https://developer.mozilla.org/en-US/docs/Web/API/Badging_API), [WAI-ARIA APG combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/), [Metcalfe 2017 on PubMed](https://pubmed.ncbi.nlm.nih.gov/27648988/).

Third party: [Andy Matuschak's notes on Execute Program](https://notes.andymatuschak.org/Execute_Program), [Execute Program spaced repetition page](https://www.executeprogram.com/spaced-repetition) (title only rendered), [Candu Linear onboarding teardown](https://www.candu.ai/blog/linear-onboarding-teardown), [Growth Dives on Linear onboarding](https://growth-dives.kit.com/posts/growth-dives-inside-linear-s-onboarding-3-things-i-didn-t-expect), [Exercism forum on renaming mentoring](https://forum.exercism.org/t/renaming-mentoring-to-code-review/4236/49), [Medium, "Duolingo needs to chill"](https://debugger.medium.com/duolingo-needs-to-chill-8f1832745ca0), [Mobbin study of streak designs](https://mobbin.com/blog/streaks-are-about-losing-a-study-of-859-streak-designs), [Arc on Wikipedia](https://en.wikipedia.org/wiki/Arc_(web_browser)).

Fetches that failed and so are not relied on: the Apple HIG notifications page (title only), the Raycast deeplinks manual page (404), two Exercism docs pages (404), the Execute Program "why" page (title only).
