# Design system: the Room, explainers and chat cards

Status: revised 2026-11-07 after the panel review. Moved out of
`experience.md` so both files stay short. The token values live in one file,
`assets/room.css`. It is inlined at build time into
`skills/learning-while-building/assets/room.html` and
`assets/explainer-template.html`, and every prototype links it, so the shipped
pages and the prototypes cannot drift. The grain is `assets/grain.png`, a copy
of `docs/assets/grain.png`.

## 1. Tokens

Taken from `docs/assets/site.css`. Names are new; values are the site's, except
where marked. One naming scheme everywhere: `--accent-text`, `--text-2` to
`--text-dim`, never short names. Eyebrows are 13px sans, as on the site.

```css
:root{
  /* surfaces */
  --paper:#F5F4F0; --card:#FFFFFF; --field:#ECE9E1; --rule:#EFEDE6; --border:#DAD8D0;
  /* ink and text */
  --ink:#16161A; --text-2:#45454D; --text-3:#5F5F68; --text-4:#6E6E77; --text-dim:#7A7A83;
  /* accent */
  --accent:#E8541E;          /* fills, focus ring, live edge; never body text */
  --accent-text:#C2410C;     /* text-safe accent, 4.71:1 on paper */
  --accent-wash:rgba(232,84,30,.16);
  /* record ramp */
  --lv1:#F6C9AF;  /* With help */
  --lv2:#EE8B5B;  /* Without help (recalls) */
  --lv3:#C2410C;  /* New situation (transfers) */
  --lv0:#EFEDE6;  /* Not yet */
  --control-border:#7A7A83;  /* changed from #8E8E96 (D8) */
  /* type */
  --sans:"Instrument Sans",system-ui,sans-serif; --mono:"JetBrains Mono",ui-monospace,monospace;
  /* radii */
  --r-cell:3px; --r-sm:10px; --r-md:14px; --r-lg:18px; --r-pill:999px;
  /* motion */
  --ease-out:cubic-bezier(.2,.7,.2,1); --ease-spring:cubic-bezier(.3,1.6,.5,1);
}
```

Dark mode (new; artifact contract requires it). Paper and ink swap; the ramp is
kept. Measured in this session [T]:

```css
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){ /* same block under :root[data-theme="dark"] */
  --paper:#141417; --card:#1D1D21; --field:#26262B; --rule:#2A2A30; --border:#3A3A40;
  --ink:#F2F1EC; --text-2:#B4B3AE; --text-3:#9A9AA2; --text-4:#9A9AA2; --text-dim:#8A8A92;
  --accent-text:#F07A4A;     /* 6.64:1 on #141417, 6.07:1 on #1D1D21 */
  --control-border:#8A8A92;
}}
```

Grain in dark mode: the same `grain.png` with `mix-blend-mode:screen` at opacity
.08. `--lv3` on dark is 3.55:1 on paper and 3.24:1 on card: passes 3:1.

Type scale:

| Role | Desktop | Phone | Weight and settings |
|---|---|---|---|
| Page title | 46px / 1.06 | 31px | 650, wdth 88, -0.02em |
| Section title | 24px / 1.3 | 20px | 650, wdth 88 |
| Prompt (`.qq`) | 24px / 1.3 | 20px | 600, -0.01em |
| Body | 17px / 1.6 | 16px | 400, `--text-2` |
| Small | 14px / 1.6 | 14px | `--text-3` |
| Eyebrow / reason | 13px | 13px | 500, `--accent-text` |
| Verdict | 26px | 22px | 700 |
| Mono (code, ids, paths, keys) | 13px / 1.8 | 12.5px | JetBrains Mono 500 |

Spacing: 4px base. Steps 4, 8, 12, 16, 24, 32, 48, 72. Card padding 24px (16px
on phone). Side gutter 32px desktop, 16px at 375px. No horizontal scroll at
375px; code blocks scroll inside themselves.

## 2. Components

Each component lists anatomy, sizes, states and semantics.

**Record segments (dimension row).** The site's `.row`: name, three `.seg`
cells (With help, Without help, New situation), level word on the right. Each
filled segment: fill from the ramp, plus `box-shadow: inset 0 0 0 1.5px
var(--ink)` (D7). Height 14px, radius 3px, gap 4px. Semantics: the row is a
`li` with text "Debugging and diagnosis: Without help"; segments are
`aria-hidden`. Lit animation: 550ms background and scaleY(1.15) (site), off
under reduced motion.

**Record cell (topic).** 28 by 28px square (44 by 44px hit area via padding),
radius 6px. Fill = latest level. Outline ring 2px offset 2px in ink = best
level when best is higher than latest. Glyph: 1, 2 or 3 short vertical bars in
ink (on `--lv3` the bars are `--paper`) at the bottom left, 2px wide; none for
Not yet. Mark for a sure miss: a 6px ink dot at top right. Pending (a same-session Correct that counts only at its review): a 1.5px dashed ink ring with no new fill, name "<topic>: With help, Without help pending the review on 10 Nov". A `button` with
accessible name "<topic>: now <level>, best <level>, <mark>". Grid is a `role
="grid"`-free list of buttons grouped by dimension `h3`; the table view is the
semantic alternative.

**Question card.** `form` with `aria-labelledby` the prompt. Parts in 3.4.
White card, 1.5px `--border`, radius 18px (14px phone). The Now card has a 3px
left edge in `--accent` (the one live element).

**Confidence control.** `fieldset` with `legend` "How sure are you?"; three
radio inputs styled as `.sure` pills (min-height 44px); the meaning text is
visible under the selected pill and is the radio's `aria-describedby`. Keys 1 2
3. Selected: ink fill, paper text. "I do not know" is a separate `button`
styled as `.sure` with a dashed border, so it reads as a different kind of
choice.

**Verdict.** A `section` with an `h2` that holds the verdict word. The page has
one polite live region, present and empty at load; each state change writes one
short line into it ("Not quite. Back tomorrow. Record unchanged."). Focus moves
to the verdict heading only when the grade returns within about 1 s of the
learner's Lock and focus is still on the card; then the live region stays
silent, so nothing is spoken twice. Body: reason, evidence link (mono, underlined), next date, belief
line if confident and wrong, record delta, resume cue, Back button.

**Compare.** Two `figure` blocks with `figcaption` "You said" and "It did".
Desktop 2 columns, gap 24px; phone stacked. "It did" content in mono on
`--paper` inside the card.

**Hint ladder.** Three numbered 10px dots in ink outline (never the record's
segment shape, so nobody reads it as a level); used hints fill ink. Label "Hints used: 1 of 3". Button
**Hint** shows the next hint in a `details`-like block. Each hint is a list
item, numbered H1 to H3 in mono. Announces "Hint 1 of 3 shown."

**Inbox item.** A `li` containing one `a` (whole row is the target, min-height
64px): reason (eyebrow), topic (mono), cost and state chip on the right. Focus
ring 2px accent offset 3px. Rows are ordinary Tab stops; J and K also move
focus when shortcuts are on. Hidden separators make the name read as
"After it works. idempotency. About 1 min. State: Open."

**State chip.** Pill, 24px tall (inside a 44px row), 12px mono, 1.5px border.
Open: ink border. Locked: ink fill. Correct: ink border with tick glyph. Not
quite and No: `--accent-text` border and text. Saved here: dashed border.

**Map row.** Dimension name, three segments, level word, expand button (44px)
that reveals the topic cells. `aria-expanded`.

**Timeline.** Horizontal on desktop (one track per dimension, dates on a mono
axis), vertical on the phone (one list per dimension). Dots 10px: filled with
the level reached in that attempt, ink outline; a sure miss is a hollow dot with
a ring. Level changes get a text label. Semantics: an ordered list per
dimension with dated items; the drawn track is `aria-hidden`.

**Calibration bars.** Three horizontal bars, track `--field`, fill ink, labels
in text with the fraction ("right 9 of 11"). Never a percentage alone.

**Week dots.** 28 dots 10px, ink outline, filled ink on days with practice
(never the ramp colours, which mean levels only). `aria-label` on the group: "Practice on 9 of the last 28 days."
(This is the one place a count appears, only for screen readers, because the
visual has no number.)

**Action bar (key caps).** On the desktop: Lock with its key cap, one row of
secondary actions. Key caps (mono 12px, 1.5px border, radius 6px) are hidden on
touch devices (`@media (hover:none)`) and when shortcuts are off. Buttons with
keys carry `aria-keyshortcuts`. The Cmd or Ctrl label comes from one shared
function. On the phone only Lock is sticky, and below 560px of height nothing
is sticky.

**Status line in place.** No timed toasts. A change that has an action ("Moved
to Later. Undo") is written where the card was, focus moves to it, and it stays
until the next learner action. The key list opens in a dialog that stays open.

**Buttons.** Site `.btn` (50px, pill, ink fill; hover accent with ink text),
`.btn.ghost`. Phone primary: full width. Minimum 44 by 44px everywhere.

**Text field.** White, 1.5px `--control-border`, radius 14px, 16px text (no
iOS zoom), focus ring accent.

**Code excerpt.** Site `.code` with `.ln` line numbers in `--text-3` (5.74:1
on paper, 4.73:1 on a highlighted line). Header `path:line` in mono
`--text-3`. Highlighted lines wrap instead of being cut, and the block fades its
right edge when it scrolls. Line-pick turns lines into radios, only as a
second step after a written hypothesis.

**Back to the build.** One primary pill at the end of every learning exchange,
full width on the phone, with the resume cue under it in mono as its caption.
It is the only way back drawn on card, verdict and drill views.

**Sheet.** The topic sheet is a `dialog` opened with `showModal()` below 768px;
on the desktop it pushes the content aside. Its heading is always in the DOM.

## 3. Motion

| What | Motion | Duration and easing | Reduced motion |
|---|---|---|---|
| Record cell lights after a grade | background fades from `--lv0` to the level; scaleY 1.15 then back | 400ms `--ease-out` (site uses 550ms for segments; keep 550 for rows) | instant colour change |
| Card on Lock | translateY(-8px) and back, controls fade to read only | 300ms `--ease-out` | none |
| Verdict arrives | opacity 0 to 1, translateY 10px to 0 (site `.reveal`) | 600ms `--ease-out` | appears |
| Inbox row leaves after grading | height and opacity to 0 | 250ms | removed |
| Page sections on first load | site `.rise` | 800ms | none |
| Background record field | site `.field` glow, Room first-run and empty states only | site timings | none |
| Anything else | no motion | | |

No celebration animation, no confetti, no sound, no looping motion near a
question.

## 4. Accessibility (WCAG 2.2 AA)

- **Contrast.** Body text `--text-2` 8.63:1; small text never lighter than
  `--text-4` (4.59:1). Line numbers `--text-3`. `--accent` never used for text.
  Control borders 3.86:1 (D8). Ramp cells carry outline and glyph. Every
  banner uses `--card`, so it follows the theme.
- **Targets.** 44 by 44px minimum for every control.
- **Keyboard.** Every action has a visible button. Shortcuts (when on): J/K
  move, Enter open, 1/2/3 confidence, Cmd or Ctrl Enter lock, Esc back, G then M
  map, ? key list. D and H ask once before they act (2.1.4). Settings turns all
  letter keys off. Keys never act inside a text field except Cmd Enter and Esc.
- **Focus.** 2px `--accent` outline, offset 3px. Never covered by sticky bars
  (2.4.11): on short viewports nothing is sticky. Sheets are modal on the phone
  and return focus on close.
- **Screen readers.** One polite live region per page; one line per state
  change; focus moves only after the learner's own action. Demo transcripts
  append new messages and never rebuild the log. Every grid has a table view.
  Diagrams have a text description and a static frame that draws every mark the
  caption names.
- **No timers.** No question has a time limit (2.2.1). Nothing with an action
  disappears on a timer.
- **Reduced motion.** All motion in section 3 off under `prefers-reduced-motion`.
- **Reflow.** Works at 320px width, 200% zoom and 640 by 360 (1.4.10). Every
  prototype's width switch includes 640 by 360.
- **Words.** Device neutral ("Select", not "Tap", on the desktop). `lang="en"`.
- **Redundant entry (3.3.7).** The restatement field is prefilled.
- **Host check.** The Room runs in an iframe in the Claude app. Keyboard focus
  from chat into the artifact and back, which keys the host takes first, and
  VoiceOver and TalkBack in the phone app are untested: experiment E-A11Y in
  `architecture/recommended.md`.
- **Dark mode** at the same contrast rules.
