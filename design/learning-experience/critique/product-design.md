# Critique: product design

Reviewer lens: a principal product designer from a tool that developers love.
Scope: `index.html`, the 8 prototypes, `experience.md`, `architecture/recommended.md`.
Method: I served the package with `python3 -m http.server`. I used Playwright
(Chromium) at 1440x900 and 390x844 with deviceScaleFactor 1. I opened every
state in every prototype through its state select (107 states at 390, the main
states at 1440), plus dark mode for three pages. Screenshots are in
`/tmp/claude-0/-home-user-explain-pr/074e39f7-08cf-5ec8-b66b-62906beb6d01/scratchpad/le-shots/`.
I did not change any package file.

Measured:

- No page has horizontal scroll at 390, in any state (`scrollWidth == 390` for all 107 states).
- No em dashes (U+2014) in any file in the package.
- Each prototype logs one console error: `404` for `../../../docs/assets/grain.png`.
  `index.html` has no errors.
- Fonts load on every page: Instrument Sans and JetBrains Mono.
- Dark mode works on the pages I checked (verdict, map, index).

## What already works (keep it)

- **"You said / It did" with "Where the time went"** (verdict.html state 7). The
  timeline bar shows the timeouts, the backoffs and the jitter the learner left
  out. This is delight that teaches. It is the best screen in the package.
- **Record cell lighting** at the verdict (state 8), and decay shown as an
  outline ring (state 9). Both have a meaning, and the ramp matches the site.
- **The copy register.** "Correct." / "Not quite." / "No.", "Not known yet.",
  "A wrong guess here costs nothing.", and no praise anywhere. The error copy
  says what failed and what still works.
- **The state coverage.** Offline, error, also-answered and held-result states
  all exist. Most products do not get here until v3.
- **The privacy question comes first at onboarding** (onboarding.html states 1 and 5).

## Findings

### Blocker

**B1. The chat door is drawn richer than any harness can draw it, so the
prototype does not show if the main handoff is seamless.**
Location: `prototypes/flow.html`, all 13 states, and `onboarding.html` states 1 to 3.

- The "agent chat" pane shows features that no harness in the surface table
  (`recommended.md` section 3) has:
  - verdict words in accent colour at a larger size ("Not quite." in state 4);
  - a card with an orange left rule and a tinted background;
  - pill suggestion chips under the composer ("Try: about 3.9 s, fairly sure",
    "not now", "don't know", "show result");
  - a state chip in the window title ("Room · c_7a21 changed", state 10).
- Claude Code in the Claude app renders markdown and tool-call rows. Codex and
  a terminal render less.
- The build surface is where the learner spends 95% of the time. If its
  prototype is idealised, the package cannot answer the owner's main question:
  is the move between building and learning seamless?
- Fix: redraw the chat pane at real fidelity, with one variant per harness:
  - Claude Code in the Claude app: markdown and collapsed tool rows.
  - Codex: plain text.
  - Terminal: monospace.
- Then judge the copy and the length again, against what the learner will
  really see.

### Major

**M1. The return trip shows its plumbing.**
Location: `flow.html` state 9 ("Next message: From the Room line").

- Before the agent starts on Sam's new request, the transcript shows three
  tool rows:
  1. `lwb_status · 1 Room card in open.json`
  2. `ArtifactData read cards/c_7a21 …`
  3. `Bash python3 scripts/learning.py import --from-room · 1 answer imported · seal ok`
- Every prediction card also starts with `lwb_seal · Card sealed · sha256 9c1e4b07`.
- `experience.md` 2.a.2 promises "one collapsed line", but each tool call is
  its own row in Claude Code.
- Fix: make one `lwb_sync` tool. It does the status read, the db read, the
  import and the seal check. Its result line is the copy itself: "From the
  Room: idempotency, Correct, now Without help. Back on 10 Nov."
- Fold `lwb_seal` into `lwb_post`, so that one row both seals and posts.
- Rule: one learning event, one transcript row.

**M2. The text card is mostly instructions, and confidence is free text that
the agent must parse.**
Location: `experience.md` 3.1; `flow.html` state 1.

- Every card ends with the same two lines: "Reply with your answer and how
  sure you are: guess, fairly sure or sure. Or "don't know" or "not now". Or
  answer in the Room: Open card".
- At 390 this is 5 of the card's 9 lines.
- The surface table lists AskUserQuestion [D] and an elicitation card [D] for
  this exact session type. `experience.md` does not use either one.
- Fix, part 1: use AskUserQuestion or elicitation where the turn ends anyway
  (the explain-back, the review line at session start). The learner taps
  Guess, Fairly sure or Sure. The agent has nothing to parse.
- Fix, part 2: for wait-mode predictions, keep text. Show the full
  instructions on the first 3 cards only. After that, use one line: `Answer +
  how sure · not now · Open card`.
- This is the Linear pattern: teach the shortcut, then get out of the way.

**M3. Internal ids show in the learner's interface.**

- Examples:
  - chat card header: `c_3f9c` (flow.html);
  - Room Now row: "While I build · c_3f9c" (flow.html, phone);
  - verdict eyebrow: "Review, 7 days · c_9b04", "After it works · c_7a21"
    (verdict.html, all states);
  - explainer cards: "c_e1a1 · answer fixed 14:10" (explainer.html).
- The "About this state" notes are the right place for ids. The product
  surface is not.
- Ids make the product feel like a debug view. They also invite copying, which
  goes against principle 1, "No copying".
- Fix: remove ids from every learner-facing string. If a card needs a
  reference in chat, use the topic and the moment ("the retry-budget
  prediction").
- Keep "answer fixed 14:10". It is the trust signal, and it is good.

**M4. The way back to the build is drawn four ways, and the verdict shows it
three times.**

- The four treatments:
  1. Inbox: "Linked to:" text with a pill button under it.
  2. Card: "‹ Inbox" on the left, linked text on the right, no button.
  3. Verdict and Map: an underlined text link on the right.
  4. Explainer: a pill with a chevron in the top bar.
- On the verdict at 390, the "Back to the build" link is at the top. A
  full-width primary button with the same label is at the bottom. Above that
  button is the mono resume cue (verdict.html states 2 to 9).
- "Back to the build" is the product's signature action. It needs one form,
  in one place, on every surface.
- Fix: put one primary "Back to the build" at the end of every learning
  exchange, with the resume cue as its caption. Remove the top link on the
  card and verdict views.

**M5. On the phone, card views keep the global tab bar and a tall action
block.**
Location: `card.html` at 390, measured.

- The tab bar is fixed: 65px tall, top at y=779.
- The sticky action block is about 165px tall (Not now, I do not know, Lock my
  answer, helper text).
- Together they cover about 230 of 844px (27%) of the screen, before the
  keyboard opens.
- With a 300px keyboard, the answer field and the code share about 260px.
- D6 itself says Card and Compare are views, not tabs.
- Fix: hide the tab bar on the card, drill and verdict views. Put "Not now"
  and "I do not know" in one row, or under a "More" menu.
- The answer is the only job on this screen. Give it the screen.

**M6. The also-answered state breaks the product's own acceptance test.**
Location: `flow.html` state 11.

- The chat order is:
  1. "Correct. …"
  2. "Back to: retries in the payment worker. Next: the dead letter queue."
  3. "You also answered in the Room at 14:02. I graded the first answer (chat, 14:01)."
- `recommended.md` section 2 says every learning exchange ends with the resume
  cue, and it tests for that.
- Fix: put the also-answered line before the verdict, or fold it into the
  verdict line.

**M7. The demo story contradicts itself across pages.**

- One excerpt has three different ranges: `billing/charge.py:41-52` (flow,
  inbox), `41-53` (card, drill) and `41-58` (onboarding, `experience.md` 2.a).
- The scenario date is 7 Nov (the flow clock reads 13:58 to 14:20). But the
  Map's Weakest card says "a sure miss on 9 Nov".
- The Map says "Since 7 Nov: retry-budget is With help (was Without help)".
  In the flow on 7 Nov, retry-budget is already at With help.
- The verdict reveal says "What you wrote on 31 Oct" in one state and "on 17
  Oct" in another, for related topics.
- A polished product demo is judged on details like these.
- Fix: one `fixtures/orbit-pay.json` that every prototype reads.

**M8. There is no shared design system. Two naming schemes and two grain
sources already exist.**

- Each of the 9 pages defines 22 to 27 tokens inline.
- `index.html` and `flow.html` use `--at` for the text-safe accent. The other
  six use `--accent-text`.
- The eyebrow differs: the site and the prototypes use 13px sans, but
  `index.html` uses 13px JetBrains Mono.
- Grain: every prototype links `../../../docs/assets/grain.png`, which resolves
  only when you serve from the repo root. Served from the package or from
  GitHub Pages (docs/ is the root), it gives a 404 and the paper has no grain.
  `index.html` uses an inline SVG noise instead.
- The Room will ship as `assets/room.html`, and explainers will ship from
  `assets/explainer-template.html`. Without one tokens and components file,
  these two will drift from the prototypes in the first week.
- Fix: one `room.css` (tokens plus components) that is inlined at build time
  into the Room, the explainer template and the prototypes. Embed the grain as
  a data URI.

**M9. The overdue copy uses the loss framing that the spec bans.**
Location: `inbox.html` state 10.

- The rows say "After 3 days, **18 days late**", "**16 days late**" and
  "**20 days late**", in bold ink.
- `experience.md` 3.0 says "no loss framing". Rows that count days late are
  the backlog guilt that makes people quit spaced-repetition tools.
- Fix: no lateness count. Sort by due date. The overflow line "9 more over the
  next 4 days" already handles the backlog.

**M10. The explainer offers hints on prediction cards.**
Location: `explainer.html` state 3, Question 1 of 3, kind predict.

- The card shows "Hints used: 0 of 3 · Hint".
- `experience.md` 3.4 allows hints only at With help and on drills. D9 says
  predictions do not change the record, so a hint cap on a prediction has no
  meaning.
- Fix: no hint control on predict cards.

**M11. The Map's controls compete with its one action.**
Location: `map.html` at 1440, state 3.

- Three segmented toggles (Record/Growth, Grid/Table, This project/All
  projects) make 6 pills with 3 solid-black selected states. They sit directly
  above "Weakest now", whose primary button "Review now" is the same solid
  black.
- Fix: make Growth a link from the record card ("See growth"). Move Grid/Table
  into the record card's header. Keep the project scope as quiet text.

### Minor

1. **"Last 4 weeks" uses the record ramp colours for practice days**
   (`map.html`). This makes orange mean two things. Use ink dots for practice.
2. **The hint ladder glyph uses the record's three-segment shape**
   (`card.html` states 2 and 8, drill, explainer). Learners will read it as a
   level. Use numbered dots.
3. **The record-delta glyph** (a square with 1 or 2 bars, `verdict.html`) has
   no label and no legend. The bars from D7 work in the grid, but alone they
   mean nothing.
4. **Keyboard hints show at 390** ("J K move · Enter open · H not now · ?
   keys", `inbox.html`). Hide them on touch devices with `(hover:none)`.
5. **"Ctrl Enter" is hard-coded** in `explainer.html` and `drill.html`.
   `card.html` already detects Cmd vs Ctrl. Use the same code everywhere.
6. **Empty group headers.** On the flow phone, "Now" shows with nothing under
   it, and "Due · 0" shows above "Nothing is due." (states 4 and 5). Leave out
   an empty group and a zero count.
7. **The offline message shows twice** (`flow.html` state 12): the banner and
   the inline line under the card say the same sentence.
8. **At 390 the highlighted line in the code is cut off**: "sleep(backoff(attem"
   (`card.html` line 52). The scroll has no cue. Wrap the highlighted lines,
   or fade the right edge.
9. **"With help" wraps to two lines in the card meta at 390**
   (`flow.html` state 12). Add `white-space:nowrap` on level words.
10. **Spacing in the eyebrows.** "Prototype·orbit-pay·cards" in `flow.html` has
    no space around the dots. "·Learning experience" in the `index.html` brand
    has no space after the dot. The site uses " · ".
11. **The prototype strip wraps at 1440** in `flow.html`: "Reset answers" goes
    to a second row. Also, its "[" and "]" buttons look like stray brackets.
    Use "Prev" and "Next" with key caps.
12. **The `index.html` footer is crowded.** The legend sits 8px above the rule.
    The brand line starts at x=162, but the legend starts at x=130.
13. **The hero mini-mocks are too small at 390.** The text in the phone mock is
    about 9.5px (`.pill{font-size:9.5px}`), so the phone mock cannot be read.
    At this width, show one frame (the card) at a readable size.
14. **The desktop Room alignment differs from the content.** The brand and the
    tabs start at x=162, but the content column is centred (x=372 to 1068 on
    the card and the verdict). Align the tab bar with the content column, as
    the site's `.wrap` does.
15. **The explainer diagram caption names a cross** ("The cross is where the
    reply is lost"). In the reduced-motion frame, only the dot shows. The
    static state must also draw the cross.

## Seamlessness, handoff by handoff

| Handoff | Verdict | Why |
|---|---|---|
| Build to prediction (chat) | Good concept, not proven | The card does not block the build ("Starting the build now."). The rendering is idealised (B1), and two tool rows come before it (M1). |
| Prediction to reveal | Good | "Locked. Shown after test_retry_budget runs." and the held-result branch are well designed. |
| Chat to phone Room | Good | The same card, the same state chip, the "Now" row on the phone. Zero copying. |
| Phone verdict back to laptop (P1) | Weak | Three plumbing rows before the work starts (M1). The pull happens only when the learner sends a message, so an idle laptop shows nothing. |
| Phone verdict back to laptop (P2 bell) | Good | State 10 is the real seamless moment. Make it the hero of `index.html` instead of P1. |
| Room exit to the build | Weak | Four treatments, and three on one screen (M4). |
| Review at session start | Good | One line, shown once, can be ignored. |
| Double answer | Breaks own rule | The resume cue is not last (M6). |

## The 3 changes that would most improve the product

1. **Design the chat door honestly, and make every transition one row.**
   - Redraw `flow.html` at the fidelity each harness really has.
   - Fold seal+post and status+read+import+check into single `lwb_post` and
     `lwb_sync` calls. Each call's result line is the learner-facing copy.
   - Use AskUserQuestion or elicitation for confidence taps where the turn ends.
   - Shorten the card to one instruction line after the first three cards.
   - This is where seamlessness is won or lost (B1, M1, M2, M6).
2. **Ship one design system and one story.**
   - One `room.css` (tokens, components, grain as a data URI), inlined into
     `room.html`, `explainer-template.html` and every prototype.
   - One `orbit-pay` fixture that all pages read.
   - No card ids in learner-facing strings.
   - This removes the drift that already exists (M3, M7, M8, minor items 1 to 3).
3. **Make the phone card a focused mode with one exit.**
   - No tab bar on the card, verdict and drill views.
   - One row of secondary actions.
   - One "Back to the build" at the end, with the resume cue as its caption,
     the same on every surface.
   - No lateness counts in the Inbox.
   - The phone is where the owner learns away from the desk, and it must feel
     as calm as the site (M4, M5, M9, minor item 4).
