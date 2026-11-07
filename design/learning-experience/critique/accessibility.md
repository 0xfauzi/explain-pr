# Accessibility review of the learning experience package

Reviewer lens: accessibility specialist (WCAG 2.2 AA, keyboard, screen readers, low vision, motion).
Date: 2026-11-07. Scope: `experience.md` (section 4.4 and the state tables), `architecture/recommended.md` (sections 2, 6.3, 6.4, 12), `index.html` and the eight pages in `prototypes/`.

## How I tested

- Served the package with `python3 -m http.server` and drove Chromium with Node Playwright.
- Every state of every prototype (13 to 16 states per page, 111 in total) in light and dark colour schemes: computed text contrast against the real composited background, accessible names of all controls, broken `aria-*` and `for` references, duplicate ids, target sizes.
- Keyboard only: Tab walks with a check for a visible focus ring and for focus covered by sticky bars; scripted key flows (confidence keys, Ctrl Enter, H, D, J and K, Esc, order moves, hint, topic sheet).
- Screen reader announcements: a MutationObserver on every `aria-live`, `status`, `alert` and `log` region plus `focusin` logging, recording what would be spoken after each action.
- `reducedMotion: reduce` against `no-preference`: every CSS animation, transition and Web Animation started while stepping through all states.
- Reflow and zoom: 1440, 390, 320 wide; 720 by 450 (1440 by 900 at 200%); 640 by 360 (1280 by 720 at 200%, also a phone in landscape); WCAG 1.4.12 text spacing override at 390.
- Screenshots in `/tmp/claude-0/-home-user-explain-pr/074e39f7-08cf-5ec8-b66b-62906beb6d01/scratchpad/le-shots/` (files named `a11y-*.png`).

## What already passes (measured)

These are strong and should be kept as they are.

- No horizontal page scroll on any page at 390, 320 or 720 wide. Code blocks and the table view scroll inside themselves.
- No console errors. The only failed request is `docs/assets/grain.png` (404), and only because the server root was the package folder; the relative path `../../../docs/assets/grain.png` is right inside the repo.
- Reduced motion: with `reduce`, no animation or transition starts on any page in any state, except a 0.2 s colour transition on the Map tabs (harmless). The explainer diagram plays once per press, never loops.
- Text spacing (1.4.12) at 390: no clipped text.
- Focus ring: 2px `#E8541E` outline on every stop I reached. Measured 3.34:1 on paper, 3.67:1 on white, 4.91:1 on ink buttons, 5.01:1 on dark paper.
- Every visible control has an accessible name. The avatar is "Sam. Open settings".
- Confidence is native radios in a `fieldset` with legend "How sure are you?". Lock is `aria-disabled`, stays in the focus order, has `aria-describedby="helper"`, and Enter on it moves focus to the confidence group.
- Order shape: "Move up" and "Move down" buttons per item; focus stays on the moved item; "Moved to 3 of 6." is announced.
- Line pick: native radios named "Line 42: for attempt in range(3):"; arrow keys work.
- Hint: "Hint 2 of 3 shown. This attempt now counts as With help." is announced. This also tells the learner the honest cost of the hint. Good.
- Map: cells are buttons named "timeouts-vs-failures: now With help, best Without help, sure miss"; ramp fills carry an ink outline, 1 to 3 bar glyphs and a legend; the table view has a caption and `scope="col"` headers; week cells are `role="img"` "Practice on 16 of the last 28 days."; calibration shows "right 9 of 11" in text.
- Topic sheet: Enter opens it, focus goes to the sheet heading, Esc closes it and returns focus to the cell.
- Light theme text contrast is clean on every state except the line numbers (M5). Dark theme is clean except one banner (M4).
- No em dashes in any file of the package.

## Findings

Ranked blocker, major, minor. Each has the file, what I saw or measured, and a fix.

### Blocker

**B1. On short viewports the sticky bars cover most of the card. The learner cannot see the question while typing.**
`prototypes/card.html` and `prototypes/drill.html`, phone layout.
- At 640 by 360 (a 1280 by 720 laptop at 200% zoom, or a phone in landscape) the fixed chrome is: top bar 57px + action bar 161px + tab bar 65px = 283px of 360px (79%). With focus in the answer field, the field spans y 86 to 208 and the action bar starts at y 135, so the caret and the focus ring are under the bar. The prompt is off screen. Screenshot `a11y-land-640-card.png`.
- At 320 by 640: 283px of 640px (44%). In the drill, the heading "Find the cause of the double charge." is hidden behind the action bar on first view. Screenshot `a11y-drillstate3-w320.png`.
- The `scroll-padding-bottom: 208px` rule protects Tab focus at 390 by 844, but on a 360px tall viewport the padding is bigger than the space left.
- Why it is a blocker: answering a card is the core task. A low-vision learner at 200% zoom on a common laptop, or anyone on a phone in landscape, can see about 75px of content. This fails the intent of 1.4.10 Reflow and puts 2.4.11 Focus Not Obscured at risk.
- Fix: `@media (max-height: 560px) { .abar, .tabs { position: static } }`, or keep only the Lock button sticky (one 50px row) and put Not now and I do not know in the flow. Add the 640 by 360 viewport to the prototype width switcher and to the acceptance checks.

**B2. Single key shortcuts with no way to turn them off. One stray "d" records an irreversible "I do not know".**
`prototypes/card.html` keydown handler (around line 521 to 535), `experience.md` 4.4 Keyboard, `architecture/recommended.md` 6.3.
- Keys 1, 2, 3, D, H, J, K, G then M act whenever focus is not in a text field. Focus on a radio, a button or the page body counts as not typing.
- `if(k===dkKey().toLowerCase()){lock(true);return}` locks the attempt at once with no confirm and no undo. Locks are sealed and final by design, so the record (the product's main promise) gets a false entry.
- Speech input users (Dragon, Voice Control) and people with tremor are the ones who hit this. This fails WCAG 2.1.4 Character Key Shortcuts (Level A). `experience.md` 3.9 Settings has no control to turn shortcuts off or remap them.
- Fix: (1) add "Keyboard shortcuts: On / Off" to Settings; (2) make D and H ask once ("Lock as I do not know? Enter / Esc"), or use them only with a modifier; (3) add `aria-keyshortcuts` to the buttons that have keys. Keep 1, 2, 3 because they only select and can be changed.

### Major

**M1. Verdicts and grades are not announced by a live region; they depend on a focus jump, and some text is announced twice.**
`prototypes/verdict.html` `render()` around line 380; `prototypes/card.html`; `experience.md` 4.2 Verdict and 4.4 Screen readers.
- `render()` replaces `#main.innerHTML` with a new `role="status"` region that already contains the verdict. Screen readers do not reliably announce a live region that is inserted already filled. In my log the only thing that would be spoken is the focus move to `h2#vw` "Not quite." (heading). The reason, the next date and the record change are not spoken unless the learner reads on.
- The spec says grading can take seconds (explain-back, "Grading..."). When the grade arrives later, there are two bad outcomes: focus jumps and takes the learner out of what they are reading, or focus does not move and nothing is spoken.
- After Lock in `card.html`, focus moves to `p#st1` "Locked. Shown after the test runs." and the `#live` region says the same sentence, so it is spoken twice.
- Fix: one polite live region per page, present at load and empty. Write one short line into it: "Not quite. Back on 8 Nov. Record unchanged." Move focus to the verdict heading only when the grade comes back within about 1 s of a learner action and focus is still on the locked card. Do not move focus and announce the same text.

**M2. The Undo toast cannot be reached by keyboard in 8 seconds.**
`prototypes/card.html` around line 509 and 550, `prototypes/inbox.html` line 459, `experience.md` 2.i ("also reachable by keyboard").
- After Not now, then Next week, focus goes to `main#main` (the whole region, a long reading). Undo is in `#toastslot` after the main content, about 13 Tab stops away. There is no key for Undo. After 8 s with no hover or focus, the toast is gone. I measured that it was removed.
- It pauses on focus, but a keyboard or switch user cannot get focus there in time. Risk under 2.2.1 Timing Adjustable.
- The "?" key list is shown in the same 8 s toast.
- Fix: a toast that has an action stays until the next learner action or until it is dismissed. Or put the line "Moved to Later. Undo" in the Now section where the card was, and send focus there. Show the key list in a dialog that stays open.

**M3. On the phone the topic sheet covers the whole screen but is not modal. Tab goes to hidden content behind it.**
`prototypes/map.html`, state "topic sheet with timeline". Screenshots `a11y-map-sheet-390.png` and `a11y-map-sheet-1440.png`.
- The `<dialog>` is opened with `show()` (`:modal` is false). At 390 the sheet fills the viewport. After "Drill this", Tab moves into the page behind the sheet and to the top controls, which cannot be seen. At 1440 the sheet sits over the right part of `main` (the "Weakest now" card is cut off), so links behind it can also take hidden focus. This fails 2.4.11.
- `aria-labelledby="shh"` points to an id that does not exist while the dialog is closed.
- Fix: below 768px use `showModal()`, or make the page behind `inert`. On the desktop, push the content to the side instead of covering it, or make it modal too. Render the heading at all times, or set the label when the dialog opens.

**M4. Dark mode: the stale banner stays white and the file path on it cannot be seen.**
`prototypes/explainer.html` line 412, state "error: out of date, rebuild", dark scheme. Screenshot `a11y-explainer-stale-dark-390.png`.
- `.banner.stale` keeps a `#FFFFFF` background, but `.mono` text uses `--ink`, which is `#F2F1EC` in dark mode. Measured 1.13:1. The text "billing/retry.py" cannot be seen, and that is the one fact the learner needs on this banner.
- Fix: use `var(--card)` for the banner background, so its tokens change with the theme.

**M5. Code line numbers fail text contrast, and the learner needs them.**
`prototypes/card.html`, `drill.html`, `explainer.html`: the `i` line number in the code excerpt uses `#7A7A83`.
- Measured: 3.86:1 on paper, 3.19:1 on a highlighted line (`#F3DACE`), 3.48:1 on the explainer highlight, 4.25:1 on white. All are below 4.5:1 for 13px text (1.4.3).
- Feedback cites `path:line`, and line pick uses the line numbers as the options, so these numbers are content, not decoration.
- Fix: use `--text-3` `#5F5F68`. Measured 5.74:1 on paper, 4.73:1 on `#F3DACE`, 5.18:1 on `#FBE4DB`.

**M6. The demo transcripts read the whole chat again at each step.**
`prototypes/flow.html` lines 341 and 427, `prototypes/onboarding.html` line 319.
- `#log` is `role="log" aria-live="polite"`, but every step sets `log.innerHTML` again. My announcement log shows the whole transcript again at each step, from "Add retries with backoff to the charge call..." onward. A screen reader user cannot follow `flow.html`, which is the page that shows the seamless experience.
- Fix: only add the new messages to the log. Do not rebuild it. When going back a step, set `aria-live="off"` while you rebuild, then put the new message in the page's single announcer.

**M7. The seamless definition and the phase acceptance tests do not cover assistive technology. The host behaviour that matters most has not been checked.**
`architecture/recommended.md` section 2 (tests), section 6.4, section 12 (dependency register).
- The Room is a claude.ai artifact inside an iframe in the Claude app. Nobody has checked these: VoiceOver and TalkBack in the iOS and Android app webviews; keyboard focus going from the chat link into the artifact iframe on the desktop and back; whether the host app takes keys such as 1, 2, 3, J, K and Esc before the artifact gets them. Section 6.4 is four sentences, and the register has no item for these.
- "Seamless" as defined ("no copying, no re-explaining, no stall, resume in one line") should be true for a learner who uses a screen reader or a keyboard only.
- Fix: add an experiment E-A11Y to section 12 and one check to each phase. Phase 1: keyboard only on the desktop app, from the chat "Open card" to Lock to "Back to the build", with no mouse; VoiceOver on an iPhone in the Claude app, answering one card and hearing the verdict. Record what fails as a re-plan trigger (section 13).

### Minor

- **m1. The Room tabs are links on some pages and buttons on others.** They are `button aria-current="page"` in `verdict.html`, `inbox.html` and `explainer.html`, and `a` in `card.html`, `map.html` and `drill.html`. Use links everywhere, because they navigate.
- **m2. Inbox row names run together.** Example: "After it works idempotency About 1 min Open" (`inbox.html`). "Open" is a state, but it sounds like an action. Add short hidden separators, for example "After it works. idempotency. About 1 min. State: Open."
- **m3. Map dimension buttons repeat the level.** Example: "Distributed systems : Without help. 2 of 3 topics without help. Without help". The space before the colon and the second level word come from the visible `.lvl` text. Hide the visible copy from the name.
- **m4. Some pages have no h1, or have duplicate headings.** `onboarding.html` has no h1 in the chat states. "Room first open" has headings "Inbox", "Map", "Map".
- **m5. Index card names are too long.** On `index.html`, each prototype card is one link whose name is the whole preview, for example "orbit-pay · cloud session Question · retry-budget...". Name each link with its title using `aria-labelledby`. Add a skip link.
- **m6. Going offline is not announced.** In `card.html`, when I toggled Offline in the middle of a task, no banner appeared and nothing was spoken. The banner shows only when the page loads in the offline state. Announce "You are offline. Answers are saved on this device." once.
- **m7. Device-specific word.** The Map says "Tap an area to see its topics." on the desktop. Use "Select".
- **m8. Broken reference.** `aria-controls="snz"` on Not now points to an element that is not there while the menu is closed (`card.html` line 412). Set it only when the menu is open.
- **m9. The spec and the prototypes differ.** `experience.md` 4.2 asks for a roving tabindex in the Inbox, but the rows are ordinary Tab stops. That works well, so change the spec. 4.4 says Esc works in text fields, but Esc in the card's answer field does nothing. Section 5 names shared `proto.css` and `fixture.js`, but those files do not exist (each page has its own copy).
- **m10. Ramp segments have no outline.** The Map segments have no ink outline (`.seg.f1` to `.f3` have no `box-shadow`), which is different from 4.2 D7. The level word next to each row means this is not a 1.4.1 failure, but light ramp fills on paper measure only 1.37:1 to 2.48:1. Add the outline as specified.

## The 3 changes that would most improve the product

1. **Let the card breathe on short and zoomed screens (B1).** When the viewport is short, the action bar and tab bar should not be sticky, and only Lock should stay pinned. A low-vision learner at 200% zoom, or a learner with a phone in landscape, then sees the question and their own answer at the same time. Add 640 by 360 to every prototype's width switcher so this cannot come back.
2. **Make keys safe and optional (B2 and M2).** Add a Settings switch for shortcuts. Never let one letter key lock an attempt. Toasts with an action stay until the learner acts. The key list opens in a dialog that stays open. The record is the product, so no accidental input may write to it.
3. **One announcer and one focus policy, tested in the real host (M1, M3, M6, M7).** Each page has a single polite live region at load. It says one short line for each state change: "Locked.", "Not quite. Back on 8 Nov.", "Moved to Later." Focus moves only after the learner's own action. Sheets are modal on the phone. Then add a VoiceOver and keyboard-only run of the Phase 1 acceptance test (Claude app on the phone and the desktop) to the plan, and make the result a re-plan trigger.
