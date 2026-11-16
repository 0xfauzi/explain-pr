> Out of date. The site is docs/index.html and its rules are in design/system/README.md.

# Spec: the public site

Part of `../PRODUCT.md`. This file specifies the update to `docs/index.html`, `docs/assets/site.css` and `docs/assets/site.js`. It is a design: the copy here is final, and the builder changes it only where a check in section 12 says the build differs.

The current page describes the old `learning-while-building` skill as if it were the whole product. That is now wrong. The page keeps its look and gets new content.

---

## 1. The one job, and the reader

**Reader.** An engineer who builds with a coding agent and worries that they are losing the judgment needed to check its work. They arrive from a link, on a laptop or a phone, and give the page a few seconds.

**The one job.** In the first screen the reader understands what Firsthand does: the agent finishes, they make one call, a real check runs. They can try that call on the page. Then the page tells them plainly what works today, what is only designed, and how to install the preview.

**What the page is not.** It is not a sales page. No pricing, no sign-up, no email field, no testimonials, no logos, no numbers about learning. Firsthand is free and open source, and the name is a working name. The page says both.

**Length.** Six sections and a close. About four screens on a laptop.

---

## 2. What stays, what goes

### 2.1 Keep (the visual language)

- Fonts: Instrument Sans (width 88 on headings) and JetBrains Mono, loaded as now.
- Colours: paper `#F5F4F0`, card `#FFFFFF`, ink `#16161A`, text `#45454D` and `#5F5F68`, borders `#DAD8D0` and `#EFEDE6`, accent `#E8541E` (fills and outlines only), accent text `#C2410C`.
- The grain overlay (`.tex::after` with `grain.png`).
- The background field of cells that light up and fade (`.field`, `renderField`), behind the hero and behind the close.
- Classes `.wrap`, `.h1`, `.h2`, `.p`, `.small`, `.sec`, `.hero`, `.two`, `.cols`, `.ctitle`, `.habit`, `.num`, `.cmd`, `.btn`, `.btn.ghost`, `.prompt`, `.ctas`, `footer`, `.rise`, `.reveal`, `.sv`, `.vh`, `.needs-js`.
- The page stays light only. A dark theme is out of scope for this update.

### 2.2 Remove (content that is now wrong or unused)

| Remove | Why |
| :- | :- |
| The hero panel "What you can do without the agent" with ten areas, three levels and the Week 1 and Month 3 toggle | It shows a record with levels per area. Firsthand has no such record, and the numbers were an invented example |
| The whole "Why" section: the 67% and 50% figures, the meters, the two columns of study behaviours | The page must be short and carry no statistics. One sentence in section 8 keeps the source link |
| The "How it works" list of four habits | It describes the old skill |
| The "Try a question" section: the two tabs, the component diagram, the code question, the four confidence buttons, the record delta | Replaced by the Revert test card |
| "You can see your progress" and "What it cannot prove" | Rewritten as sections 7 and 8 below |
| The close prompt "Make this a learning task" | Old skill |
| CSS for: `.panel`, `.phead`, `.ptitle`, `.dims`, `.row`, `.segs`, `.seg`, `.pfoot`, `.legend`, `.count`, `.toggle`, `.tg`, `.opt`, `.sure`, `.tab`, `.tabs`, `.stats`, `.bignum`, `.meter`, `.eyebrow`, `.qpanel`, `.qctx`, `.qq`, `.opts`, `.sure-l`, `.confs`, `.lockrow`, `.result`, `.verdict`, `.why`, `.belief`, `.delta`, `.code`, `.ln`, `.flow`, `.dot`, `.cut`, `.flownote`, and the `div.opt` rule on the last line | Dead after the content change. Removing `.sure`, `.tab`, `.tabs` and `.result` also prevents clashes with the ported card rules |
| JS for: `CMD`, `FILLS`, `LEVEL_NAMES`, `CODE`, `EXAMPLES`, `DIMS`, the record rows, the tabs and the old question | Dead. Keep `el`, `renderField` and the copy-button code (changed as in section 9.3) |

---

## 3. Page structure

| # | Section | id | Purpose |
| :-: | :- | :- | :- |
| 0 | Header | | Brand and four links |
| 1 | Hero, with the live question card | `top`, card `try` | What it is, in one screen. One call to try |
| 2 | How it works | `how` | Three steps, and the same question as one line in the agent |
| 3 | What works today | `status` | Built and not built, side by side |
| 4 | Install the preview | `install` | The command, what it writes, how to remove it |
| 5 | The earlier skill | `skill` | learning-while-building 0.6.0, still available |
| 6 | Limits | `limits` | What the tool does not show |
| 7 | Close and footer | | Licence, the working name, links |

Head:

- `<title>`: `Firsthand (preview)`
- `meta description` and `og:description`: `A free, open-source tool for your coding agent. When the agent finishes a change, Firsthand asks you one short question, then runs a real check on your project and shows the result next to your answer.`
- `og:title`: `Firsthand (preview)`

---

## 4. Section 0: header

- Brand (links to `#top`): `Firsthand`
- Nav links: `How it works` (`#how`), `What works today` (`#status`), `Install` (`#install`), `GitHub` (`https://github.com/0xfauzi/explain-pr`, class `gh`).
- The nav is hidden at 640px and below, as now.

---

## 5. Section 1: hero

Layout: the existing `.hero` grid inside `.stage` with the field behind it. Left column: text. Right column: the question card, where the record panel was. The card is the product screen of the page, and it is on the first screen.

### 5.1 Left column copy

- **H1:** `Your agent says it is done. You make one call. Firsthand runs the check.`
- **Lead** (`.p.lead`): `A free, open-source tool for your coding agent. When the agent finishes a change, Firsthand asks you one short question about it. Then it undoes the change in a scratch copy, runs your tests, and shows the result next to your answer.`
- **Status line** (`.small`, a plain paragraph under a 1px `#DAD8D0` top rule, with 16px above the rule and 14px below it): `Preview. It works today in Claude Code, on Python projects that use pytest. More agents and more questions are designed and not built yet. Firsthand is a working name.`
- **Buttons** (`.ctas`):
  - `.btn`, link to `#install`: `Install the preview`
  - `.btn.ghost`, link to `#status`: `What works today`

The install command is not in the hero. It needs two lines of explanation, and the hero has room for one idea.

### 5.2 Right column: the question card

A caption above the card, then the card, then a note below it.

- **Caption above** (`.mark`, the dashed rule with centred mono text from the prototypes): `Try it: the question, with example data`
- **Note below** (`.small`): `This page runs nothing. On your machine the tests are from your own project and the result is from a real run.`

The card is the Revert test from `prototypes/revert.html`, without the Room shell (no top bar, no Inbox crumb, no prototype controls, no footer line). Markup and class names are reused as they are, inside one wrapper `<div class="demo" id="try">`, and every ported CSS rule is scoped under `.demo` (section 9.2).

**Question state.** Exact text:

```
Your agent finished                                                  skip ok
Verification | orbit-pay | idempotent refunds | change since 09:12

It added 3 tests. Read them first.

  1  test_same_key_refunds_once
       assert len(ledger.refunds(charge)) == 1
  2  test_refund_response_is_stable
       assert resp.status_code == 200
  3  test_refund_amount_validated
       assert exc.value.code == "amount_too_large"

Which of them would still pass with the change undone?

  [ ] 1    [ ] 2    [ ] 3    [ ] None    [ ] Don't know

  [ Lock ]

Skip
Checked by a run: the change undone, the tests kept.
```

- Markup: `form.card.open` labelled by the legend, `p.eb`, `p.ctx`, `p.lead`, `ol.ev` (labelled "The 3 new tests and their assertion lines"; not a tab stop, since its lines wrap and it never scrolls), `fieldset` with `legend.q`, `div.picks` of five `button.pill.pk` with `aria-pressed` (section 13), `p.acts.send` with the `Lock` button (`.btn.sm`, disabled until something is chosen), `div.acts.quiet` with the `Skip` text button, `p.foot`.
- Left out, because they do nothing on a web page: `Open a test`, `Wrong start`.

**Choosing.** The numbers are toggles: several can be on. `None` and `Don't know` each clear the numbers and the other one; a number clears them. No pick locks. `Lock` locks what is chosen.

**Locked state.** `Lock` locks the chosen picks. All picks are disabled and the chosen ones stay pressed; focus moves to `Undo`. A row appears under the picks:

- Status: `Locked.` and a text button `Undo`
- `How sure?` with two pills: `Sure`, `Not sure`. Optional.
- Button (`.btn.sm`): `Show the result`
- For `Don't know`, the How sure label and its two pills are hidden. Only `Locked.`, `Undo` and `Show the result` show.

**Skipped state.** The form is replaced by a small card: `Skipped.` and a text button `Undo`, then on a new line in mono: `Back to: idempotent refunds. Next: read the summary.`

**Result state.** The form is replaced by `section.card.in` (it rises in). Header: `REVERT TEST` on the left, a chip on the right. Context line: `Verification | orbit-pay | idempotent refunds`.

| Pick | Chip | You said | What happened | What would have shown it |
| :- | :- | :- | :- | :- |
| 2 | `Matched` with a tick | `2, test_refund_response_is_stable.` | `It still passes with the change undone. It would pass whether or not the change exists.` | Row hidden |
| 1 | `Did not match` | `1, test_same_key_refunds_once.` | `test_refund_response_is_stable still passes with the change undone.` | `Its only assertion is at tests/test_refunds.py:41.` (the build's wording, `words._assert_cue`) |
| 3 | `Did not match` | `3, test_refund_amount_validated.` | As for 1 | As for 1 |
| 2 and 3 (any set holding 2 and more) | `Did not match` | `2 and 3, test_refund_response_is_stable and test_refund_amount_validated.` | As for 1 | About the first other pick: `It fails at tests/test_refunds.py:29.` for 1, `With the change undone it stops at tests/test_refunds.py:52 with an error, not on an assertion.` for 3 |
| 1 and 3 | `Did not match` | `1 and 3, test_same_key_refunds_once and test_refund_amount_validated.` | As for 1 | As for 1 |
| None | `Did not match` | `None.` | As for 1 | As for 1 |
| Don't know | `Not scored` (dashed chip) | `Don't know.` | `test_refund_response_is_stable still passes with the change undone. It would pass whether or not the change exists.` | As for 1 |

- When a How sure pill was chosen, `You said` ends with it: `2, test_refund_response_is_stable. Sure.`
- For `Don't know`, a line under the context line reads `"Don't know" is not counted as a miss.` (`words.DONT_KNOW_REASON`).
- The More rows and the `Sent to your agent` line use the build's own words (`words._MORE_ROWS`, `words.note_fact`).
- Under the rows, the cue block. The prototype's button `Back to the build` has nowhere to go on this page, so the button reads `Try again` (`.btn.ghost.sm`, full width of the card) and resets the card to the question state, with focus moved to the first pick. Under it, in mono: `Back to: idempotent refunds. Next: read the summary.`
- `details.more` with summary `More`, closed at first. Inside:

```
test_same_key_refunds_once       fails on its assertion
test_refund_response_is_stable   still passes
test_refund_amount_validated     cannot run without the new code, which is weak proof

Checked by a run, no model.
Sent to your agent: "tests/test_refunds.py::test_refund_response_is_stable passes with the change undone. tests/test_refunds.py::test_refund_amount_validated cannot run with the change undone."
```

- Left out of the result, with reasons: the lines `Your calls of this kind: 5 of 7 matched...` and `Sure: 6 of 8 matched...` (they are counts for a made-up person, and on a public page they read as statistics); the line about a review coming back on a date (reviews are not built); `Open the commands`, `This result looks wrong`, `Say it again in one line`, `Ask my agent to walk me through this` (they need the real engine).

**Without JavaScript.** The question card is shown with its picks disabled and with no Skip row. Under it a second `.mark` reads `The result, for the answer 2`, followed by the Matched result card with `More` available (a `details` element works without script) and no `Try again` button.

---

## 6. Section 2: how it works

Layout: `.sec`, then `.two`. Left: heading and three `.habit` rows with the orange number circles. Right: one terminal block (`.term` from the prototypes) showing the same question as text in the agent.

- **H2:** `How it works`

**Steps:**

1. **Title:** `Your agent finishes a change.`
   **Text:** `Firsthand reads the events your agent reports and the git diff. If the change added or edited tests, it prepares one question. It never blocks a tool call and the agent never waits for you.`
2. **Title:** `You make one call.`
   **Text:** `One line appears in the agent's chat. Reply there, answer in the Room (a page served by your own computer), or say "skip". By default it asks at most once a day, and not on the first prompt of the day.`
3. **Title:** `A real check runs.`
   **Text:** `Firsthand copies the project to a scratch folder, undoes the change, keeps the tests and runs them. The result shows what you said and what happened. Nothing is written to your project.`

**Paragraph under the steps** (`.small`, max-width 720px): `What the check found also goes to your agent as one line, because it is about the agent's own work. A switch in Settings turns that line off. An answer given in the Room does not pass through the agent. A reply typed in the chat is part of the chat: the agent sees it and prints the result there.`

**Terminal block.** Title bar: `Claude Code` then, dimmer, `orbit-pay`. Body, as `pre` elements with `white-space: pre-wrap`. Lines starting with `>` use the `.u` colour, the note in brackets uses `.d`, and the two Firsthand blocks use `.fh` (the 3px accent bar on the left). The URLs are plain text, not links.

```
> Make refunds idempotent on the idempotency key.

(the agent works, then finishes)

Firsthand (skip ok): your agent finished and added 3 tests. Which of them would still pass with the change undone? 1 test_same_key_refunds_once, 2 test_refund_response_is_stable, 3 test_refund_amount_validated. Reply the numbers, or none. With the tests shown: http://127.0.0.1:4127/q/7f3

> 2

Firsthand, revert test. Matched. You said 2.
test_refund_response_is_stable still passes with the change undone. It would pass whether or not the change exists.
More: http://127.0.0.1:4127/r/7f3
Back to: idempotent refunds. Next: read the summary.
```

- **Caption under the block** (`.small`): `The same question as one line in Claude Code. Example data.`

---

## 7. Section 3: what works today

Layout: `.sec`, heading, one paragraph, then `.cols` with two columns. The left column has the 3px ink top border, the right the 3px `#C2410C` top border, as the two study columns had. Each column is a `.ctitle` and a `ul`.

- **H2:** `What works today, and what does not yet`
- **Paragraph:** `Firsthand is being built in steps. This is the state of the repository now.`

**Left column**

- **Title:** `Works today`
- **Line under the title** (`.small`): `In Claude Code, on Python projects that use pytest.`
- Items:
  - `Revert test. When the agent finishes a change with tests, you pick the new test that would still pass with the change undone. Checked by undoing the change and running the tests.`
  - `Call it. When a test is failing, you pick where the cause is, before a fix exists. Checked by where the fix landed, and by undoing the fix and running the test again.`
  - `Brief. At the start of a larger task, you name one check that fails now and will pass when the task is done. Checked by running it with the change and with the change undone.`
  - `The Room. A page served at 127.0.0.1 with the open question, results, a journal of every call, and settings.`
  - `The record. A git repo at ~/.firsthand/record: on your machine, outside your projects, with no remote.`

**Right column**

- **Title** (in `#C2410C`): `Designed, not built`
- **Line under the title** (`.small`): `Specified in the repository. None of this runs yet.`
- Items:
  - `Ten more questions. Examples: who is affected by a change, whether a migration can be undone, what would show a failure first.`
  - `Other agents: Codex, Cursor, Copilot, Gemini CLI and others.`
  - `Other languages and test runners.`
  - `Drills on your own history, and reviews that bring an idea back some days later.`
  - `Questions that fade as your calls on a skill prove reliable.`
  - `The Room on your phone.`

**Line under both columns** (`.p`, ink colour): `The full design is in the repository:` then a link `design/product/PRODUCT.md` to `https://github.com/0xfauzi/explain-pr/blob/main/design/product/PRODUCT.md`.

Each item starts with its name in weight 600 (`<b>`), then the sentence in normal weight.

---

## 8. Sections 4 to 6

### 8.1 Section 4: install the preview

Layout: `.sec`, `.two`. Left: heading, paragraph, the command block, the requirements line. Right: the list of what the command does.

- **H2:** `Install the preview`
- **Paragraph:** `Firsthand is not on PyPI yet, so the preview installs from the git repository. Run this in a terminal, at the root of a Python project that uses pytest.`
- **Command block** (`.cmd` with a `Copy` button):

```
uvx --from git+https://github.com/0xfauzi/explain-pr firsthand init
```

- **Requirements** (`.small`): `You need Python 3.11 or later, git, uv and Claude Code. When Firsthand is published, the command will be: uvx firsthand init`

**Right column**

- **Title** (`.ctitle`): `What the command does`
- Items (a `ul`, styled as in `.cols`):
  - `It lists every file it will write and asks before it writes any of them.`
  - `It asks whether this is a work computer and which command runs your tests.`
  - `It adds six hooks to ~/.claude/settings.json and one skill folder at ~/.claude/skills/firsthand/. It backs up each file first.`
  - `The hooks only report what happened. They never allow, deny or block anything your agent does.`
  - `It creates your record at ~/.firsthand/record. These are plain files: anyone who can read your home folder can read them.`
  - `There is no account and no telemetry. Nothing leaves your machine except the lines added to your agent's chat. The only server is the local page at 127.0.0.1.`
- **After the list** (`.p`): `The first question comes when your agent next finishes a change that adds or edits tests. Say "skip" to pass on a question.`
- **Remove it** (`.small`), then a second, smaller `.cmd` block with its own `Copy` button:
  - Text: `To remove it, run this. It restores the backed-up files. Your record and the engine copy stay in ~/.firsthand; delete that folder to remove them.`
  - Command: `uvx --from git+https://github.com/0xfauzi/explain-pr firsthand uninstall`

### 8.2 Section 5: the earlier skill

Layout: `.sec`, `.two`. Left: heading. Right: text and the command block.

- **H2:** `The earlier skill is still here`
- **Paragraph 1:** `This repository also holds learning-while-building, version 0.6.0. It is an Agent Skill for Claude Code and other agents that read Agent Skills. On tasks you choose, it asks you a question before the agent builds, asks you to explain the code after, and asks again some days later.`
- **Paragraph 2:** `It installs separately and does not need Firsthand. From 0.6.0 its record is kept in ~/.learning-while-building, outside your project. If an earlier version left a .learning folder in your repository, the README says how to move it.` The words `the README` link to `https://github.com/0xfauzi/explain-pr#readme`.
- **Command block** (`.cmd` with `Copy`):

```
/plugin marketplace add 0xfauzi/explain-pr
/plugin install learning-while-building@learning-while-building
```

- **Under it** (`.small`): `Run these inside Claude Code. You need Python 3.10 or later and git.`

### 8.3 Section 6: limits

Layout: `.sec`, `.two`. Left: heading. Right: three paragraphs.

- **H2:** `What it does not show`
- **Paragraph 1:** `A result is a fact about one change: this test passes with the change undone, or it does not. It is not a score of you as an engineer, and the page that lists your calls shows counts, not a grade.`
- **Paragraph 2:** `One study reports that handing work to an AI assistant can weaken the understanding needed to check that work. Other research on learning reports that committing to an answer before you see the result helps. No study has tested questions of this kind during real work with a coding agent. The design does not depend on one: each result is true about your own project and is useful either way.` The words `One study reports` link to `https://www.anthropic.com/research/AI-assistance-coding-skills`; the words `Other research on learning` link to `design/product/research/learning-science.md` on GitHub. Paths, the address and inline commands on the page are set in mono (`code.mono`, 0.9em).
- **Paragraph 3:** `The check is only as good as your tests can be run. If the new tests do not pass in a scratch copy exactly as they do in your project, Firsthand asks nothing.`

---

## 9. Section 7: close and footer

Layout: the existing `.stage.close` with the low field.

- **H2** (class `h1`): `Free and open source.`
- **Paragraph:** `There is nothing to buy and no account. The code, the design and the research notes are in one repository. Firsthand is a working name and may change.`
- **Buttons** (`.ctas`):
  - `.btn` with copy behaviour: `Copy the install command` (copies the section 8.1 install command)
  - `.btn.ghost` link to GitHub: `See it on GitHub`
- **Footer left:** `Firsthand (preview)` and the licence name, read from `LICENSE` at build time. Today that is `MIT licence`.
- **Footer links:** `Source` (the repository), `Design` (`.../blob/main/design/product/PRODUCT.md`), `Changelog` (`.../blob/main/CHANGELOG.md`).

---

## 10. Building the card and the terminal block

### 10.1 Tokens

Add a `:root` block at the top of `site.css` with the light values from `design/product/assets/room.css`: `--paper`, `--card`, `--rule`, `--border`, `--ink`, `--on-ink`, `--text-2`, `--text-3`, `--text-dim`, `--accent`, `--accent-text`, `--control-border`, `--sans`, `--mono`, `--ease-out`. These are the same hex values the site already uses. No dark block.

### 10.2 Ported rules

Copy these rules from the `<style>` block of `prototypes/revert.html` into `site.css`, each selector prefixed with `.demo` (for the card) or left as `.term` (for the terminal block, which has no clash):

`.card`, `.card.open`, `.eb`, `.eb .sk`, `.ctx`, `.lead`, `.ev` and its children, `.q`, `legend.q`, `.picks`, `.pill` and its states, `.lock`, `.lock .st`, `.sure` and its children, `.quiet`, `.acts`, `.tbtn`, `.foot`, `.rh`, `.rt`, `.chip` and its variants, `.rw` and its children, `.cue`, `details.more` and its children, `.mb`, `.mark`, `.in`, `.btn.sm`, and the `.term` rules.

- `fieldset`, `dl`, `dd`, `ol`, `ul`, `legend` and `p` inside `.demo` get `margin: 0; padding: 0`, `fieldset` gets `border: 0; min-width: 0`, and lists get `list-style: none`, as in the prototype's reset.
- `.demo .lead` must set its own `font-size: 16px` and `animation: none`, because the site already has a hero `.lead`.
- `.rt` is an `h2` on this page, not an `h1`.
- In the 640px media query, port: `.card` padding and radius, `.q` size, `.rw > div` to one column, `.sure .btn` to full width, `.term .bd` padding.

### 10.3 Script

One small state machine in `site.js`, modelled on the prototype's script: states `ask`, `locked`, `skipped`, `result`; `pick` and `sure` variables; `show(state)` toggles elements by `data-v`. Text for the result rows is set from the table in section 5.2. The prototype's `boot`, state selector, theme selector and Quiet button are not ported.

Copy buttons: each `Copy` button copies the text of the `pre` inside its own `.cmd`. The close button carries `data-copy-from="install"` and copies the install command. The label changes to `Copied` for two seconds, as now.

---

## 11. Motion

The page keeps the existing motion and adds nothing new in kind.

- **Load:** hero heading, lead, status line, buttons and the card use `.rise` with delays of 0, .1, .2, .25 and .3 seconds.
- **Scroll:** section headings, the three steps, the two status columns and the terminal block use `.sv` (fade and 28px rise on entry, where `animation-timeline: view()` is supported; static elsewhere).
- **Field:** the cells behind the hero and the close keep lighting up and fading on their slow cycles.
- **Card:** a pick fills with ink in .15s. The lock row and the result card rise 8px and fade in over .5s (`.in`). The chevron on `More` turns in .2s. The number circles on the steps keep their hover turn.
- **Removed with their content:** the travelling dot, the record segments growing, the meters filling.
- No motion carries meaning. Every state change is also text.

---

## 12. Phone layout (390px wide)

- The hero is one column in this order: heading, lead, status line, buttons, caption, card, note. The first screen holds the heading, the lead and the status line. To make that fit, at 640px and below: hero top padding 24px, `.h1` 42px (as now), `.lead` 18px.
- The two hero buttons sit side by side if they fit, else stack at full width.
- The card: 18px by 16px padding. Picks wrap to two rows (`1 2 3 None`, then `Don't know`). An assertion line that is too long wraps inside the test list (`pre-wrap`, `overflow-wrap: anywhere`); the page itself never scrolls sideways. Result rows stack the label above the value. `Show the result` and `Try again` are full width.
- How it works: steps first, the terminal block under them. Its text wraps (`pre-wrap`, `overflow-wrap: anywhere`), 12.5px.
- What works today: one column, `Works today` first.
- Install: the command wraps inside its block (`overflow-wrap: anywhere`, as `.cmd pre` does now), and the `Copy` button takes the full width under it.
- Every target is at least 44px high. The page must reflow at 320px and at 200% zoom.

---

## 13. Accessibility

- **Contrast.** Body text `#45454D` and small text `#5F5F68` on `#F5F4F0` and on white are above 4.5 to 1. `#E8541E` is used only for fills, the card's left bar, the number circles (with ink text on top) and the focus ring, never for text. Orange text is `#C2410C`. The "Did not match" chip uses `#C2410C` for its text and border and also carries the words.
- **Meaning never rests on colour.** Chips carry words. The two status columns are told apart by their titles, not by the border colour.
- **Focus.** The existing rule stays: a 2px `#E8541E` outline at 3px offset on `:focus-visible`. For the How sure radio pills the outline is drawn on the visible label (`input:focus-visible + span`). The result section takes focus but draws no ring, since it is not a control.
- **Semantics.** The card is a `form` labelled by its question. Picks are five `button type="button"` elements with `aria-pressed` in a `fieldset` with a `legend`, each its own tab stop: Enter or Space toggles one, and only the `Lock` button locks. Once locked all are disabled and the chosen ones keep `aria-pressed="true"`. They are not radios, because arrow keys in a radio group check the next radio and would choose an answer the person did not pick. How sure is a radio group (`role="radiogroup"`) labelled by `How sure?`. The result is a `section` whose accessible name starts with the chip word: `Matched. Revert test`. The result rows are a `dl`. `More` is a `details` element. The terminal block is plain text in `pre`.
- **Live region.** One `aria-live="polite"` paragraph for the page, one line per change: `Locked.`, `Undone.`, `Skipped.`. A result is not announced here: focus moves to the result section, whose name starts with the chip word.
- **Focus moves.** `Lock` moves focus to `Undo`. `Show the result` moves focus to the result section (`tabindex="-1"`). `Try again` and both `Undo` buttons move focus to the first pick. `Skip` moves focus to the skipped card's `Undo`. Nothing else moves focus, and nothing scrolls the page except bringing the result into view (`block: 'nearest'`).
- **Keyboard.** Every control is a native radio, button, link or summary. No letter shortcuts.
- **No timers.** Nothing on the page times out. The `Copied` label is the only timed change and loses no information.
- **Reduced motion.** Under `prefers-reduced-motion: reduce`: `.rise`, `.reveal`, `.sv`, `.in` and the field cells do not animate, all transitions are off, and scrolling to the result is instant.
- **Headings.** One `h1` (the hero). Section headings are `h2`. The result title is an `h2` styled as `.rt`. Column and list titles are `h3`.
- **Language.** No sentence on the page depends on an image. The grain and the field are decorative and hidden from assistive technology.

---

## 14. Checks before the site ships

The copy above states things about the build. The builder confirms each one against the working tree, in a temporary `HOME`, and changes the copy where the build differs. Nothing is left on the page that was not seen to work.

1. **The install command.** `pyproject.toml` has no `[project]` table at the time of writing: `build-2.md` section 2 adds it (name `firsthand`, console script `firsthand`). Once it exists, run the section 8.1 command against the repository with a temporary `HOME` and confirm `init` starts. The command reads the default branch, so it works for visitors only after this work is merged. If the package cannot be installed with `uvx --from git+...`, replace the block with the commands that do work (clone, then `python -m firsthand init` from the clone) and keep the "not on PyPI yet" sentence.
2. **The uninstall command.** Confirm it restores `settings.json` and leaves the record. If `init` puts `firsthand` on the `PATH`, shorten the command to `firsthand uninstall`.
3. **What `init` writes.** The list in section 8.1 follows `build-2.md` section 3 (six hooks, one skill folder, backups, a confirmation prompt). `experience.md` section 3.1 also lists three lines added to `~/.claude/CLAUDE.md`. If the build writes that file, add it to the second list item.
4. **The three questions.** "Works today" names Revert test, Call it and Brief. If Call it or Brief did not ship in this build, move that item to "Designed, not built" and change "Ten more questions" to the right count.
5. **The Room.** The Room item names the open question, results, a journal and settings. Remove any that the built Room does not have.
6. **Fading.** "Questions that fade" is listed as not built, following `build-2.md` section 1. Keep it there unless it shipped.
7. **The skill version.** `.claude-plugin/plugin.json` reads 0.5.0 at the time of writing. Section 8.2 says 0.6.0, which `build-1.md` delivers. Confirm the manifest, and confirm the README has the section on moving a `.learning` folder.
8. **The licence.** The footer names the licence in `LICENSE`. Founder decision F may change it to Apache-2.0.
9. **Text rules.** No em dash and no emoji anywhere in the three files. Run codespell and the repo's local pre-commit hooks on them.
10. **Screens.** Screenshot at 1280 and 390 wide. At both sizes the first screen shows the heading, the lead and the status line, and at 1280 it also shows the card down to the picks. Check the card in all four states, with the keyboard alone, with reduced motion, and with JavaScript off.
