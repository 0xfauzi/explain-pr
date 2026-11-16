Firsthand is a logbook. A person writes a call before a result exists, a run prints what happened, and the two sit side by side on one spread. Every rule below follows from that.

## Content fundamentals

- Write in the second person, present tense, sentence case. "Your answer", "The run", "Your agent finished". No title case, no exclamation marks, no emoji.
- A result is a fact about one change, never a judgement of the person. Write "Did not match", never "Wrong". Write the product's sentence: "Don't know" does not count as Did not match.
- Name the mechanism plainly: "Checked by a run, no model." "Served by this computer at 127.0.0.1."
- Keep the product's fixed words exact: Revert test, Call it, Brief, the Room, Matched, Did not match, Not scored, Skip, Lock, Show the result.
- Buttons say what happens: "Lock", "Show the result", "Back to the Inbox". Never "OK" or "Continue".
- Numbers are counts with their base: "3 of 4", "Asked today: 0 of 1". Never a percentage or a score.
- Every entry has a number and two times: when the answer was locked and when the run was recorded. Show both. They are the proof that the call came first.

## Words

Write in plain English, close to ASD-STE100 (Simplified Technical English). The reader is in the middle of work.

- One idea in a sentence. 20 words at most in an instruction, 25 in a description.
- Active voice, present tense. "Firsthand runs your tests", not "your tests are run".
- One word for one thing. It is always "answer", "run", "result", "fix", "change", "test". Do not swap in "call", "response", "check-in" or "verdict" for variety.
- Use the short common verb: use, make, show, run, keep, tell. Not leverage, surface, ensure, enable.
- Say what happens and who does it. No slogans, no sentences in threes for rhythm, no "not X, but Y" turns.
- Write the condition first: "If you do not want to answer, say skip."
- No idioms and no figures of speech. A sentence must mean the same thing when translated word by word.
- Give the example, not the adjective. "A test fails with the fix undone", not "a rigorous check".

## Two hands on one page

This is the core of the system. Every screen keeps the two apart.

- **The person writes in `voice` (Newsreader).** The question put to them and the name they gave a task are roman. **Their own answer is always `voice-answer`: italic, in `call` blue,** like ballpoint on the page. Nothing else on any screen is blue italic.
- **The run prints in `fact` (IBM Plex Mono).** Anything a machine produced or that can be pasted into a terminal: test names, paths, commands, times, counts, entry numbers. Use tabular figures and no ligatures.
- **`ui` (IBM Plex Sans) is the interface:** buttons, tabs, explanations. It never carries the call or the result.
- Never set a test name in `voice` or a person's answer in `fact`.

## Color

- The ground is `paper`. Text is `ink`, `ink-2` for body, `ink-3` for labels.
- **`call` is the person's hand.** Their answer, a pick they turned on, the Matched mark, links and the focus ring. Nothing a machine produced is ever `call`.
- **`mark` is a highlighter stroke and appears once per screen at most.** It sits behind the words of the open question and covers the lower three quarters of each line, like a real stroke, never a full box. In the dark theme it is a wash with `on-mark` text. A screen with no open question has no highlighter.
- `mark-bright` is the same yellow at full strength in both themes. Use it only for the inbox count, the bar and prompt sign in a terminal, and the cover.
- A terminal block is its own surface: `screen` with `on-screen` text, dark in both themes.
- `miss` is only for the Did not match mark and its words.
- There is no green and no success color. Matched is the person's own blue: the call held.
- `paper-raised` is the body of the question sheet. `paper-sunk` is evidence. Do not raise or sink anything else.
- The dark theme is blue-black with warm white text. Do not tint it green or brown, and do not put a saturated fill behind text there.

## The page

- **Folio.** Every page opens with a folio line: the wordmark, the place, and on the right the date and where the page is served from, closed by a double rule (2px `ink`, 3px gap, 1px `ink`). The double rule appears only there and at the head of a ledger.
- **Margin column.** On screens 760px and wider, every row has a margin column of `margin-col` on the left holding its entry number, time or label in `fact-sm` or `label`. Below 760px the margin note moves above the row.
- **Rows, not cards.** A journal entry, a skill and a note are rows between `rule` lines. Only the open question is a bordered sheet.
- **Leaders.** A fact and its outcome are joined by a dotted leader in `rule-strong`, with the outcome flush right: `test_name ...... still passes`.
- **The spread.** A result puts "Your answer" on the left and "The run" on the right, divided by a vertical perforation (a dashed `rule-strong` line). The verdict mark sits on the perforation. Each side is headed by its time. Below 600px the sides stack and the perforation runs across.
- The system is square. Use `radius-sm` everywhere. No pills, circles, shadows, gradients or rounded cards.
- Controls are 48px tall. Answer cells are 48px squares that sit flush and share borders, like boxes on a form.
- A key that does the same thing is shown as a keycap inside the control: `Send to my agent` with its Enter cap.
- Focus is a 2px solid `call` outline with a 2px offset on every surface.

## Verdict marks

Three drawn marks, each two bars in a 28px square. They are the only pictorial elements in the system. Do not add an icon set.

| Mark | Verdict | Drawing |
| --- | --- | --- |
| two aligned bars | Matched | `on-call` bars on a `call` square |
| two bars with a stroke through them | Did not match | `miss` bars and border on `miss-tint` |
| two dashed bars | Not scored | `ink-3` bars in a dashed `rule-strong` square |

Always show the words with the mark.

## Motion

Motion shows one thing: the order of events. The call is already on the page; the run arrives after it. Nothing moves for decoration, nothing loops, and nothing moves twice.

- **The highlighter stroke.** When a question sheet appears, the highlighter passes behind the question once, left to right, in `dur-stroke` with `ease-pen`. It is the only thing on the sheet that moves.
- **A press.** A cell or button answers in `dur-press`: the fill arrives and the control settles 1px. No ripple, no bounce.
- **The result prints.** When a result is shown, your call is already there. Then, in this order: the perforation draws from the top (`dur-line`), the verdict mark lands on it (`dur-stamp`, `ease-stamp`), the run's lines print one after another from the left, `stagger` apart, each leader drawing out to its outcome, and last the finding sentence appears. The whole sequence takes about one second.
- **Tallies fill.** On the Skills page, the cells of a track fill in order, `stagger` apart, the first time the row is seen.
- **The cursor.** A terminal block's cursor blinks. It is the only repeating motion, and only on the site.
- Hover and focus change color in `dur-state`. Tabs do not slide.
- With `prefers-reduced-motion: reduce`, everything is in its final state at once and the cursor does not blink.
- Never animate layout, never fade a whole page in, never move something the person has to click.

## Fonts

Newsreader, IBM Plex Mono and IBM Plex Sans load from Google Fonts. The Room is served by the person's own computer and must work offline, so it bundles the three as font files and falls back to Georgia, ui-monospace and system-ui. Set `font-optical-sizing: auto` so Newsreader uses its display cut at large sizes.
