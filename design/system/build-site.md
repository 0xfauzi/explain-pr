# Build spec: the public site

This file tells the builder how to rebuild `docs/index.html`, `docs/assets/site.css` and `docs/assets/site.js` in the Firsthand design system. It replaces the visual parts of `design/product/spec/site.md`. The claims and facts in that file still hold. Where the two differ on layout, class names, motion or behaviour, this file wins.

Read `design/system/README.md` first. Then open the reference and keep it open while you build.

## 0. The target

The page to match is `design/system/components/ScreenSiteFull/preview.html`. It is the whole page with final copy and a working example. Its markup is the source for `docs/index.html`. Its inline script is the model for `site.js`.

Rendered references (run `python3 design/system/render.py <dir>` to make them again):

| What | File in the render directory |
| :- | :- |
| Whole page, first state | `ScreenSiteFull-{light,dark}-{960,390}.png` |
| Every state of the example | `SiteDemo-{light,dark}-{960,390}.png` |
| Part head | `Part-*.png` |
| Step rows | `Steps-*.png` |
| Status ledger | `StatusLedger-*.png` |
| Command blocks and the list of what a command does | `Command-*.png` |
| Citation and notes | `Notes-*.png` |
| Colophon | `Colophon-*.png` |
| First screen alone | `ScreenSite-*.png` |
| A result that did not match, and the print order | `Spread-*.png`, `Motion-*.png` |

Each component has a `README.md` beside its preview with its usage rules. They are part of this spec.

The built page must match the reference at 1280, 960 and 390 wide, in both themes. Compare screenshots side by side before you say it is done.

## 1. Files

| File | What it is |
| :- | :- |
| `docs/index.html` | One page. The markup of the reference, with the head in section 2. |
| `docs/assets/site.css` | The tokens, then the component rules the page uses. Nothing else. |
| `docs/assets/site.js` | The example and the Copy buttons. No library. |
| `docs/.nojekyll` | Keep. |

### 1.1 Delete

- `docs/assets/grain.png`. No texture, no background image.
- Everything now in `site.css`. No rule survives: not `.tex`, `.field`, `.fc`, `.stage`, `.wrap`, `.h1`, `.h2`, `.p`, `.small`, `.sec`, `.hero`, `.two`, `.cols`, `.ctitle`, `.habit`, `.num`, `.cmd`, `.btn`, `.prompt`, `.ctas`, `.rise`, `.reveal`, `.sv`, `.vh`, `.needs-js`, `.demo` and its children, `.term`, `.mark`, `.chip`, `.pill`.
- Everything now in `site.js`: `renderField`, the `.sv` and `.rise` motion, the old card state machine. Keep only the idea of `copyText` (section 7).
- The fonts Instrument Sans and JetBrains Mono, the orange accent `#E8541E` and `#C2410C`, every rounded card, pill and number circle, the load animation and every scroll animation.
- From the copy: the two hero buttons ("Install the preview", "What works today"), the dashed caption "Try it: the question, with example data", the `More` disclosure in the result, "Try again".

## 2. Head

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Firsthand (preview)</title>
<meta name="description" content="A free, open-source tool for your coding agent. When the agent finishes a change, Firsthand asks you one short question, then runs a real check on your project and shows the result next to your answer.">
<meta property="og:title" content="Firsthand (preview)">
<meta property="og:description" content="(the same sentence)">
<meta property="og:type" content="website">
<meta name="color-scheme" content="light dark">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400..600&display=swap">
<link rel="stylesheet" href="assets/site.css">
</head>
<body class="fh">
```

- `site.js` loads at the end of `body` with `defer`.
- The page has no theme switch. The theme follows `prefers-color-scheme`.

## 3. The stylesheet

1. Start `site.css` with the whole of `design/system/tokens.css`, unchanged. It already holds the light values on `:root`, the dark values under `@media (prefers-color-scheme: dark)`, and the space, radius, duration, easing and font tokens. Do not retype a hex value anywhere below it.
2. Add `html{background:var(--paper)}body{margin:0;background:var(--paper)}` and `html{scroll-behavior:auto}`.
3. Copy these blocks from `design/system/components/bundle.css`, in this order, unchanged:
   - the base (`.fh`, focus, `.fh-link`, `.fh-fact`, `.fh-label`, `.fh-kbd`), Wordmark, Folio
   - Button, Answer cells, Verdict mark, Leaders, The spread, The question sheet
   - Ledger (only `.fh-ledger`, `.fh-ledger--head` is not used, `.fh-row`, `.fh-row__margin`, `.fh-row__head`, `.fh-row__title` and the 760px rule)
   - Terminal
   - Motion (all of it)
   - Site (`.fh-nav`, `.fh-hero`, `.fh-cmd`, `.fh-status` and the three lines after them)
   - every block from "Site page: parts in the margin grid" to "Site demo" (Part, Steps, Status ledger, Command block, Notes, Colophon, Site demo)
   - from the Room's blocks, only these rules: `.fh-vh`, `.fh [hidden]`, `.fh-text`, `.fh-text + .fh-text`, `.fh-text .fh-fact,.fh-finding .fh-fact`, `.fh-finding > .fh-label`, `.fh-finding--text > .fh-label`, `.fh-acts`, `.fh-acts__note` and its 600px rule, `.fh-q[data-still] mark`, the five `.fh-held` rules, `.fh-spread--wait::before`, `.fh-wait`, `.fh-wait b`, and the 600px rule for `.fh-spread--wait .fh-spread__run`
4. Do not copy Tabs, Skill, or any other Room block. Do not add a rule that is not in the bundle. If the page needs one, add it to the bundle and to the component's preview first.
5. Keep the order of the bundle. Later rules override earlier ones on purpose (for example the Motion block moves the perforation to `::before`).

No inline `style` attribute in `index.html`, except `style="--i:0"` (and 1, 2) on the three fact rows of the spread, which the print order reads.

## 4. Grid and rhythm

- **Page.** `.fh-site`: max width 1120px, centred, padding `28px 32px 64px`. Below 600px: `20px 16px 48px`.
- **Columns.** A margin column of `--margin-col` (132px), a 24px gap, then the main column. Part numbers, step numbers and row labels are in the margin column. Titles, text, lists and blocks start at the main column. The folio, the hero, the entry line, the spread and every rule run the full width.
- **The hero** is the only place with its own columns: 5 to 7, 48px gap, one column below 860px.
- **Rules.** The double rule closes the folio and appears nowhere else on the page. A part opens with one 1px `ink` rule. Rows inside a part are separated by 1px `rule` lines. The status ledger's two columns open with a 2px `ink` rule (works) and a 1.5px dashed `rule-strong` rule (designed). The colophon opens with one 1px `ink` rule.
- **Vertical rhythm.** 64px from the folio to the headline. 48px from the headline to the hero columns. 96px above each part's rule (64px below 760px). 16px from the rule to the part head, 32px under the head. 24px above and below the content of a row. 96px above the colophon.
- **Type.** Headline `voice-xl` (72/72, 44/46 below 860px). Part titles `voice-lg` (36/44, 28/36 below 760px). Row and item titles `voice-md`. Reading text `voice-sm` in `ink-2`, at most 34em wide. Explanations inside rows `ui-md` in `ink-2`, at most 40em. Everything a machine made or that can be pasted is `fact`.
- **No decoration.** No background image, pattern, grain, gradient, shadow, icon or illustration. The only pictorial elements are the three verdict marks.

## 5. Structure and copy

The copy below is final. Take the exact markup, attribute for attribute, from `ScreenSiteFull/preview.html`. This section names each part so you can find it and check nothing is missing.

Wrapper: `<div class="fh-site" id="top" data-demo="nojs">`, followed at once by `<script>document.currentScript.parentNode.setAttribute("data-demo","ask")</script>`. This is the only inline script. It runs before the first paint, so a visitor with JavaScript never sees the fallback.

Inside it: `header.fh-folio`, `main`, `footer.fh-colophon`, and `p.fh-vh#live[aria-live=polite]`.

### 5.0 Folio

`header.fh-folio`: `a.fh-wordmark` (`<i>First</i>hand`, to `#top`), `nav.fh-nav[aria-label=Sections]` with `How it works` (`#how`), `What works today` (`#status`), `Install` (`#install`), `Source` (`https://github.com/0xfauzi/explain-pr`), then `span.fh-folio__right`: `Preview · free and open source`.

### 5.1 First screen

`section.fh-hero`:

- `h1`: `Your agent says it is done. <em>You make one call.</em> Firsthand runs the check.` The `em` is the one sentence on the page in blue italic.
- `div.fh-hero__cols`, left:
  - `p.fh-hero__lead`: `When your coding agent finishes a change, Firsthand asks you one short question about it. Then it undoes the change in a scratch copy, runs your tests, and sets the result beside your answer.`
  - `div.fh-cmd.fh-cmd--stack` with `code[data-cmd=install]` and a Copy button. The command is in section 8.
  - `p.fh-cap`: `Installs from the git repository. Not on PyPI yet.` then a `fh-link` to `#install`: `What the command does`
  - `ul.fh-status`: `Works today in ... Claude Code, pytest`, `Asks at most ... once a day`, `Your record stays ... on your machine`, `Checked by ... a run, no model`
- right: the question sheet (`section.fh-sheet#sheet[tabindex=-1][aria-labelledby=q]`) and two `p.fh-cap` lines under it, one per state group (section 6).

The sheet, top to bottom:

```
REVERT TEST                                   NO. 0042 · SKIP OK
orbit-pay / idempotent refunds / change since 09:12
Your agent finished and added 3 tests. Read them first.

 1  test_same_key_refunds_once ........ tests/test_refunds.py:29
    assert len(ledger.refunds(charge)) == 1
 2  test_refund_response_is_stable .... tests/test_refunds.py:41
    assert resp.status_code == 200
 3  test_refund_amount_validated ...... tests/test_refunds.py:52
    assert exc.value.code == "amount_too_large"

Which of them would still pass with the change undone?      (highlighted)

[1][2][3]  [None][Don't know]
1 2 3 toggle · N none · ? don't know
[Lock Enter]  Skip
----
Checked by a run: the change undone, the tests kept.    Nothing is written to your project.
```

"Wrong start" is not on the site: it has nothing to do here.

### 5.2 Part 01, the result (`section.fh-part#result`)

- Margin: `01` / `The result`
- Title: `Your call, then the run, on one spread.`
- Lead: `A result is one spread. What you said is on one side, with the time you locked it. What the run found is on the other, with the time it finished.`
- Then two blocks, one for the states before a result and one for the result (section 6.2).

### 5.3 Part 02, how it works (`section.fh-part#how`)

- Margin: `02` / `Three steps`. Title: `How it works`
- `ol.fh-ledger` of three `li.fh-row`, each with `b.fh-step__n` and a note in the margin, and a `div.fh-step` (title `h3.fh-row__title`, `p.fh-text`, `ul.fh-status` of two facts):

| No. | Margin note | Title | Text | Facts |
| :- | :- | :- | :- | :- |
| 1 | Your agent | Your agent finishes a change. | Firsthand reads the events your agent reports and the git diff. If the change added or edited tests, it prepares one question. It never blocks a tool call and the agent never waits for you. | `Reads ... agent events, git diff`, `Blocks a tool call ... never` |
| 2 | You | You make one call. | One line appears in the agent's chat. Reply there, answer in the Room (a page served by your own computer), or say "skip". By default it asks at most once a day, and not on the first prompt of the day. | `Asks at most ... once a day`, `To pass ... say "skip"` |
| 3 | The run | A real check runs. | Firsthand copies the project to a scratch folder, undoes the change, keeps the tests and runs them. The result shows what you said and what happened. Nothing is written to your project. | `Runs in ... a scratch folder`, `Written to your project ... nothing` |

- A fourth row, margin label `What your agent sees`, `p.fh-text`: `What the check found also goes to your agent as one line, because it is about the agent's own work. A switch in Settings turns that line off. An answer given in the Room does not pass through the agent. A reply typed in the chat is part of the chat: the agent sees it and prints the result there.`

The title of step 2 is roman. Do not set it in blue italic.

### 5.4 Part 03, in the chat (`section.fh-part#chat`)

- Margin: `03` / `In the chat`. Title: `The same moment, as one line in your agent.`
- In `div.fh-part__body`: one `div.fh-term`. Bar: `claude code · ~/src/orbit-pay` and `main`. Body, one `p` each:

```
› Make refunds idempotent on the idempotency key.                                   (p.me)
  Edited ledger/refunds.py and api/refunds.py. Added 3 tests in tests/test_refunds.py. 14 passed.   (p.dim)
| Firsthand (skip ok): your agent finished and added 3 tests. Which of them would still pass with the change undone? 1 test_same_key_refunds_once, 2 test_refund_response_is_stable, 3 test_refund_amount_validated. Reply the numbers, or none. With the tests shown: http://127.0.0.1:4127/q/7f3   (p.fh-line)
› 2                                                                                  (p.me)
| Firsthand, revert test. Matched. You said 2.
| test_refund_response_is_stable still passes with the change undone. It would pass whether or not the change exists.
| More: http://127.0.0.1:4127/r/7f3
| Back to: idempotent refunds. Next: read the summary.                               (one p.fh-line, four lines)
› (cursor)                                                                           (p.me > span.cur)
```

- The word `Firsthand` at the start of each Firsthand line is wrapped in `em`. The addresses are plain text, not links.
- `p.fh-cap` under the block: `The same question as one line in Claude Code. Example data.`
- Check the two Firsthand lines against what the build prints (`firsthand/words.py`) and correct them if they differ.

### 5.5 Part 04, what works today (`section.fh-part#status`)

- Margin: `04` / `State of the build`. Title: `What works today, and what does not yet`. Lead: `Firsthand is being built in steps. This is the state of the repository now.`
- In `div.fh-part__body`: `div.fh-twocol` of two `div.fh-state`.

Left, `fh-state`. Head: `Works today` and `runs now`. Sub: `In Claude Code, on Python projects that use pytest.` Items, each with the state `works`:

| Name | Text |
| :- | :- |
| Revert test | When the agent finishes a change with tests, you pick the new test that would still pass with the change undone. Checked by undoing the change and running the tests. |
| Call it | When a test is failing, you pick where the cause is, before a fix exists. Checked by where the fix landed, and by undoing the fix and running the test again. |
| Brief | At the start of a larger task, you name one check that fails now and will pass when the task is done. Checked by running it with the change and with the change undone. |
| The Room | A page served at `127.0.0.1` with the open question, results, a journal of every call, and settings. |
| The record | A git repo at `~/.firsthand/record`: on your machine, outside your projects, with no remote. |

Right, `fh-state fh-state--designed`. Head: `Designed, not built` and `does not run`. Sub: `Specified in the repository. None of this runs yet.` Items, each with the state `not built`:

| Name | Text |
| :- | :- |
| Ten more questions | Examples: who is affected by a change, whether a migration can be undone, what would show a failure first. |
| Other agents | Codex, Cursor, Copilot, Gemini CLI and others. |
| Other languages and test runners | (none) |
| Drills and reviews | Drills on your own history, and reviews that bring an idea back some days later. |
| Questions that fade | They fade as your calls on a skill prove reliable. |
| The Room on your phone | (none) |

- `p.fh-cap.fh-cap--gap` under both: `The full design is in the repository:` then a `fh-link` `design/product/PRODUCT.md` to `https://github.com/0xfauzi/explain-pr/blob/main/design/product/PRODUCT.md`.
- Before shipping, check each left item still works in the build (the checks in `design/product/spec/site.md` section 14). The Room item names a journal and settings: if the rebuilt Room names its pages differently, use its words.

### 5.6 Part 05, install (`section.fh-part#install`)

- Margin: `05` / `Preview`. Title: `Install the preview`. Lead: `Firsthand is not on PyPI yet, so the preview installs from the git repository. Run this in a terminal, at the root of a Python project that uses pytest and has at least one git commit.`
- `div.fh-ledger` of five `div.fh-row`, each with a `span.fh-label` in the margin:

| Margin label | Content |
| :- | :- |
| Run this | `p.fh-cmd__cap`: `Terminal, at the root of your project` and `installs from git`. Then `div.fh-cmd` with the install command and Copy. |
| It needs | `ul.fh-status.fh-status--wide`: `System ... Linux or macOS`, `Python ... 3.11 or later`, `Also ... git, uv, Claude Code`, `Once on PyPI ... uvx firsthand init` |
| What the command does | `ol.fh-does`, seven items, below |
| The first question | `p.fh-text`: `The first question comes when your agent next finishes a change that adds or edits tests. Say "skip" to pass on a question.` |
| To remove it | `p.fh-text`: `Run this. It restores the backed-up files. Your record and the engine copy stay in ~/.firsthand; delete that folder to remove them.` Then `div.fh-cmd` with the uninstall command and Copy. |

What the command does, in order (paths and the address in `code`):

1. It lists the files it will change in `~/.claude` and asks before it writes anything.
2. It asks whether this is a work computer and which command runs your tests.
3. It adds six hooks to `~/.claude/settings.json` and one skill folder at `~/.claude/skills/firsthand/`. It backs up each file first.
4. The hooks only report what happened. They never allow, deny or block anything your agent does.
5. It copies its own code to `~/.firsthand/engine`. The hooks run that copy.
6. It creates your record at `~/.firsthand/record`. These are plain files: anyone who can read your home folder can read them.
7. There is no account and no telemetry. Nothing leaves your machine except the lines added to your agent's chat. The only server is the local page at `127.0.0.1`.

### 5.7 Part 06, the earlier skill (`section.fh-part#skill`)

- Margin: `06` / `Version 0.6.0`. Title: `The earlier skill is still here`
- In `div.fh-part__body`, two `p.fh-prose`:
  - `This repository also holds learning-while-building, version 0.6.0. It is an Agent Skill for Claude Code and other agents that read Agent Skills. On tasks you choose, it asks you a question before the agent builds, asks you to explain the code after, and asks again some days later.`
  - `It installs separately and does not need Firsthand. From 0.6.0 its record is kept in ~/.learning-while-building, outside your project. If an earlier version left a .learning folder in your repository, the README says how to move it.` `the README` is a `fh-link` to `https://github.com/0xfauzi/explain-pr#readme`.
- `div.fh-cmd__wrap`: `p.fh-cmd__cap` (`Inside Claude Code` and `needs Python 3.10 or later and git`), then `div.fh-cmd.fh-cmd--chat` with two lines in one `code` and Copy:

```
/plugin marketplace add 0xfauzi/explain-pr
/plugin install learning-while-building@learning-while-building
```

- The version in the margin and in the text is read from `.claude-plugin/plugin.json` (0.6.0 today).

### 5.8 Part 07, limits (`section.fh-part#limits`)

- Margin: `07` / `Limits`. Title: `What it does not show`
- `div.fh-ledger` of three `div.fh-row`, text in `p.fh-prose`:

| Margin label | Text |
| :- | :- |
| A result | A result is a fact about one change: this test passes with the change undone, or it does not. It is not a score of you as an engineer, and the page that lists your calls shows counts, not a grade. |
| The research | `One study reports` [1] that handing work to an AI assistant can weaken the understanding needed to check that work. `Other research on learning` [2] reports that committing to an answer before you see the result helps. No study has tested questions of this kind during real work with a coding agent. The design does not depend on one: each result is true about your own project and is useful either way. |
| The check | The check is only as good as your tests can be run. If the new tests do not pass in a scratch copy exactly as they do in your project, Firsthand asks nothing. |

- The two quoted phrases are `fh-link`s, each followed by `span.fh-ref` (`[1]`, `[2]`). Under the paragraph, `ol.fh-status.fh-notes`:
  - `1` `The study` ... `anthropic.com/research/AI-assistance-coding-skills` (to `https://www.anthropic.com/research/AI-assistance-coding-skills`)
  - `2` `Research notes` ... `design/product/research/learning-science.md` (to `https://github.com/0xfauzi/explain-pr/blob/main/design/product/research/learning-science.md`)

### 5.9 Part 08, the close (`section.fh-part#close`)

- Margin: `08` / `Apache-2.0` (the licence in `LICENSE`). Title: `Free and open source.` Lead: `There is nothing to buy and no account. The code, the design and the research notes are in one repository. Firsthand is a working name and may change.`
- `div.fh-acts`: `button.fh-btn[data-copy][data-copy-from=install]` `Copy the install command`, and `a.fh-btn.fh-btn--quiet` `See it on GitHub` to the repository.

### 5.10 Colophon

`footer.fh-colophon`: `p` with `<b>Firsthand (preview)</b> · Apache-2.0 licence`; `nav.fh-nav[aria-label=Repository]` with `Source` (the repository), `Design` (`.../blob/main/design/product/PRODUCT.md`), `Changelog` (`.../blob/main/CHANGELOG.md`); `p.fh-colophon__set`: `Set in Newsreader, IBM Plex Mono and IBM Plex Sans.`

### 5.11 Headings

One `h1`. Each part title is an `h2` and names its `section` with `aria-labelledby`. The question is an `h2` inside the sheet. Step titles and the two status column heads are `h3`.

## 6. The example

One sheet in the first screen, one spread in part 01. The state is the attribute `data-demo` on `.fh-site`. An element that belongs to some states lists them in `data-v`. The stylesheet hides the others. The script changes the attribute and writes the words of the answer and the verdict. It builds and removes nothing else.

The key rule holds on this page as in the product: **no part of the run is in view before the call is locked and Show the result is pressed.** The printed spread is in the HTML for the fallback, hidden by the state rule. It must never be visible in `ask`, `locked` or `skipped`.

### 6.1 States of the sheet

| State | Bar, right | Cells | Under the cells |
| :- | :- | :- | :- |
| `ask` | `No. 0042 · skip ok` | Enabled. None on at first. | The key legend. `Lock` with its Enter keycap (disabled until a cell is on) and `Skip` (quiet). |
| `locked` | `No. 0042 · locked 14:02:11` | Disabled, chosen ones filled. | `div.fh-held`: `Your call` and `locked 14:02:11`, the answer in `p.fh-answer#held`, `How sure?` with two word cells `Sure` and `Not sure`, then `Show the result` with its Enter keycap and `Undo` (quiet). |
| `result` | as `locked` | as `locked` | `div.fh-held` with the head and the answer only, then `p.fh-sheet__state`: `The result is printed below.` |
| `skipped` | `No. 0042 · skipped` | Disabled, none on. | `p.fh-sheet__state`: `<b>Skipped.</b> Back to: idempotent refunds. Next: read the summary.` and `Undo` (quiet). |
| `nojs` | `No. 0042 · skip ok` | Disabled, cell 2 on (as written in the HTML). | `p.fh-sheet__state`: `This page takes an answer only with JavaScript on. <b>The result for the answer 2 is shown below.</b>` |

- Caption under the sheet: `Example data. Pick, then Lock: the result prints below.` in `ask`, `locked`, `skipped`. `Example data. This page runs nothing.` in `result` and `nojs`.
- **Choosing.** The numbers toggle and several can be on. `None` and `Don't know` each clear everything else. A number clears `None` and `Don't know`. No cell locks.
- **How sure** is optional. The two cells are buttons with `aria-pressed`. Pressing one turns the other off. Pressing it again turns it off. Each press rewrites the answer line at once. For `Don't know` the How sure row is hidden.
- **The answer line** (`fh-answer`): the numbers joined with commas and "and", a full stop, then How sure if chosen: `2.`, `1 and 3. Not sure.`, `1, 2 and 3. Sure.`, `None.`, `Don't know.` Under it in `small`: the names of the chosen tests, joined with a comma and a space. No `small` for `None` and `Don't know`.
- **The highlighter.** Behind the question in `ask` and `nojs` only. The stylesheet removes it in the other states. On the first change of state the script sets `data-still` on the `h2`, so the stroke does not pass again when the visitor comes back to `ask`.
- The times are fixed example data: locked `14:02:11`, finished `14:02:19`.

### 6.2 States of the spread (part 01)

Before a result (`data-v="ask locked skipped"`):

- `div.fh-entry`: label `No. 0042 · Revert test · idempotent refunds`, and on the right the label `Not shown yet`.
- `div.fh-spread.fh-spread--wait` (no perforation, no mark):
  - left, `Your call`. In `ask` and `skipped`: the time reads `not locked`, then `div.fh-blank` (an empty dotted line) and a note. `ask`: `Answer the question above. Your call is written here when you lock it.` `skipped`: `Skipped. Nothing is written here.` In `locked`: the time reads `locked 14:02:11` and the answer is written in `p.fh-answer#waitcall`, exactly as in the sheet.
  - right, `The run · change undone`, the time reads `not shown`, then `p.fh-wait`: `Nothing here is shown before your call is locked.`

The result (`data-v="result nojs"`):

- `div.fh-entry#entry[tabindex=-1]` with the same label and, on the right, the verdict: mark and words (`span.fh-verdict#verdict`). Its `aria-label` is the verdict, then `Revert test, No. 0042`: `Matched. Revert test, No. 0042`.
- `div.fh-spread#spread`: left `Your call`, `locked 14:02:11`, `p.fh-answer#answer`. The verdict mark `svg#stamp` on the perforation. Right `The run · change undone`, `finished 14:02:19`, and `ul.fh-facts`, the same for every answer:

```
  test_same_key_refunds_once ......... fails on its assertion      (--i:0)
▸ test_refund_response_is_stable ..... still passes                (--i:1, is-key)
  test_refund_amount_validated ....... cannot run                  (--i:2)
```

- `div.fh-finding`: the verdict in words as the margin label (`#f-label`), `p.fh-finding__text`: `Test 2 still passes with the change undone.`, then one `p#f-more` (table below).
- `div.fh-finding.fh-finding--text`: margin label `Sent to your agent`, `p.fh-finding__sent`: `tests/test_refunds.py::test_refund_response_is_stable passes with the change undone. tests/test_refunds.py::test_refund_amount_validated cannot run with the change undone.`
- `div.fh-acts`: `button.fh-btn.fh-btn--second#again` `Try another answer` (in `result`), or the label `The result for the answer 2` (in `nojs`), and `span.fh-acts__note`: `Checked by a run, no model. On this page it is example data.`

In the example only test 2 still passes. The result for every answer:

| Answer | Verdict | Mark | The sentence in `#f-more` |
| :- | :- | :- | :- |
| 2 | Matched | `fh-m--match` | It would pass whether or not the change exists. |
| 1 | Did not match | `fh-m--miss` | Its only assertion is at `tests/test_refunds.py:41`. |
| 3 | Did not match | `fh-m--miss` | as for 1 |
| 1 and 3 | Did not match | `fh-m--miss` | as for 1 |
| None | Did not match | `fh-m--miss` | as for 1 |
| 1 and 2, or 1, 2 and 3 | Did not match | `fh-m--miss` | Test 1 fails at `tests/test_refunds.py:29` with the change undone. |
| 2 and 3 | Did not match | `fh-m--miss` | With the change undone test 3 stops at `tests/test_refunds.py:52` with an error, not on an assertion. |
| Don't know | Not scored | `fh-m--none` | "Don't know" is not counted as a miss. Its only assertion is at `tests/test_refunds.py:41`. |

- The rule: if 2 is not among the picks, the sentence is about test 2. If 2 is among them with others, it is about the lowest other pick.
- The path in the sentence is a `span.fh-fact`. Build it with text nodes, not `innerHTML`.
- The three marks are the SVGs in `design/system/components/Verdict/preview.html`. Matched has its square at `0,0,28,28`. The other two have it inset by `.75`. The miss adds the stroke `M17.5 6.5l-7 15`.
- The verdict words, the margin label, the `aria-label` of `#entry` and both marks always change together.

### 6.3 Show the result: the result prints

On `Show the result`:

1. Write the answer, the verdict and the sentence.
2. Set `data-demo="result"`.
3. Remove `data-play` from `#spread` and `#entry`, force a reflow, and set it again. This plays the sequence once.
4. Focus `#entry` with `preventScroll`, then `document.getElementById('result').scrollIntoView({block:'start'})`. The scroll is instant. Do not use `behavior: 'smooth'`.

The sequence is the one in the bundle's Motion block. Do not write new keyframes and do not change a duration:

| Order | What | Token |
| :- | :- | :- |
| 0 | Your call is already on the left. It does not move. | |
| 1 | The perforation draws from the top (across, below 600px). | `dur-line`, `ease-out` |
| 2 | The verdict mark lands on it, and the verdict in words fades in at the head of the entry. | `dur-stamp`, `ease-stamp`, after `dur-line` |
| 3 | The run's head appears, then its three lines print from the left, `stagger` apart, each leader drawing out to its outcome. | `dur-line`, `ease-out` |
| 4 | The finding, the line sent to the agent and the button row appear. | `dur-line` |

The whole takes about one second. With `prefers-reduced-motion: reduce` everything is in its final state at once (the bundle's rule does this) and the cursor does not blink.

Other motion on the page, and nothing more: the highlighter stroke behind the question once on load, the press of a cell or button, hover and focus colour in `dur-state`, the terminal cursor. No element fades or rises on load. Nothing animates on scroll. Nothing moves when the state changes except the print.

### 6.4 Buttons and focus

| Action | Result | Focus moves to | Live region says |
| :- | :- | :- | :- |
| `Lock` | `locked`. How sure is cleared. | `Show the result` | `Locked.` |
| `Undo` in `locked` | `ask`. The picks are kept. How sure is cleared. | the first cell that is on | `Undone.` |
| `Show the result` | `result`, and the print | `#entry` | nothing: the name of `#entry` starts with the verdict |
| `Try another answer` | `ask`. Picks and How sure are cleared. | cell 1 | nothing |
| `Skip` | `skipped`. The picks are cleared. | `Undo` | `Skipped.` |
| `Undo` in `skipped` | `ask`, with nothing chosen. | cell 1 | `Undone.` |

- The live region is one `p.fh-vh[aria-live=polite]`. Clear it, then set the text 40ms later, so the same word is announced twice in a row.
- Focus is the system's ring on every control. The sheet and `#entry` take focus by script or click and show no ring (`.fh-sheet:focus`, `.fh-entry:focus` in the bundle).
- Nothing else moves focus or scrolls the page.

### 6.5 Keyboard

The sheet has `tabindex="-1"`, so a click anywhere in it puts focus in it. The keys work when focus is on the sheet or on anything inside it, in the `ask` state only. Listen for `keydown` on the sheet.

| Key | Does |
| :- | :- |
| `1` `2` `3` | toggles that cell |
| `n` or `N` | toggles None |
| `?` | toggles Don't know |
| `Enter` | locks, if at least one cell is on and focus is on the sheet or on a cell. Ignore a repeated keydown (`event.repeat`). |
| `Space` | on a focused cell, toggles it (the browser's own behaviour for a button) |
| Arrow keys | nothing. An arrow key never moves a choice and never locks. |
| `Tab` | moves through the cells, Lock and Skip in order. Each cell is its own stop. |

- Ignore every key with Ctrl, Alt or Meta held.
- With no cell on, Enter on a focused cell is left to the browser and toggles that cell. Enter on `Skip`, `Lock` or a link is always left to the browser.
- In `locked`, focus is on `Show the result`, so Enter shows the result. The letter and number keys do nothing once locked.
- The cells are `button[aria-pressed]`, never radios. The group is `role="group"`, named by the question and described by the key legend (`aria-describedby="keys"`).

### 6.6 Without JavaScript

The HTML is written in the `nojs` state: `data-demo="nojs"`, every cell `disabled`, cell 2 `aria-pressed="true"`, and the printed spread filled in for the answer 2 with no How sure (`2.`, Matched, `It would pass whether or not the change exists.`). There is no `data-play` in the HTML, so nothing animates. Copy buttons do nothing without script, so the bundle hides them in this state (`[data-demo="nojs"] [data-copy]`) and the command can be selected by hand. Every Copy button therefore carries `data-copy`.

## 7. Copy buttons

- A button with `data-copy` copies the text of the `code` in its own `.fh-cmd`. With `data-copy-from="install"` it copies the text of `code[data-cmd=install]`.
- Use `textContent`. The `$` sign is drawn by CSS and `<wbr>` adds no character, so the copied text is the command alone.
- On click the label changes to `Copied` for two seconds. Hold the button's width while it does (`min-width` set from `offsetWidth`).
- Use `navigator.clipboard.writeText`, with the `textarea` and `execCommand('copy')` fallback from the old `site.js` when the clipboard API is missing.

## 8. The install command

The package is not on PyPI, and the default branch does not hold it until this branch is merged. The page therefore prints the command that is true once the branch is merged:

```
uvx --from git+https://github.com/0xfauzi/explain-pr firsthand init
uvx --from git+https://github.com/0xfauzi/explain-pr firsthand uninstall
```

- Write each with one `<wbr>` after `github.com/`, so it breaks there and nowhere inside a word.
- `uvx firsthand init` appears once, as a fact (`Once on PyPI ... uvx firsthand init`), never in a command block and never with a Copy button.
- Do not run `init` or `uninstall` against the real home directory to check this. Use a temporary `HOME`, as `tests/firsthand/support.py` does. If the command cannot be checked before the merge, say so in your report. Do not change it to something untested.

## 9. Phone layout (390 wide)

- **Folio.** The links wrap under the wordmark and the status moves to its own line on the right, as in the reference.
- **First screen.** One column in this order: headline (44/46), lead, command (stacked: Copy is a bar under it), caption, four facts, sheet, caption.
- **Sheet.** 16px padding. Each evidence row puts the path under the test name with no leader. The question is 28/37. The five cells stay on one row. How sure sits under its label if it does not fit beside it.
- **Spread.** The sides stack: your call, then the perforation running across with the mark on it at the left, then the run. Each fact puts its outcome under its name, with no leader.
- **Parts.** The number and note sit on one line above the title (28/36). `fh-part__body` loses its left margin. Each row's margin label moves above the row.
- **Steps.** `Step 1` and the note on one line, then the title, the text, and the two facts under it.
- **Status ledger.** One column, `Works today` first.
- **Commands.** Every command is stacked. The Copy bar is 44px tall.
- **Notes.** The address moves under its name.
- **Colophon.** Name and licence, the links, the typefaces, each on its own line.
- Every control is at least 44px tall. The page never scrolls sideways at 390 or at 320. Check `document.documentElement.scrollWidth <= innerWidth` at both.

At 960 the page is the reference render. At 1280 the page is the same grid at its full 1120px: the hero columns and the status columns are wider, the reading text keeps its 34em measure, and nothing else changes.

## 10. Checks before you say it is done

1. Screenshots at 1280, 960 and 390 in both themes, compared with the reference renders, for the whole page and for each state of the example.
2. The example with the keyboard alone: every row of the table in 6.2, Undo, Skip, Try another answer.
3. In `ask`, `locked` and `skipped`, assert that `#spread` and `.fh-facts` have no layout box.
4. An arrow key changes nothing in any state.
5. With JavaScript off: the result for the answer 2 is shown, the cells are disabled, no Copy button shows.
6. With reduced motion: no animation runs and the result is complete at once.
7. No request leaves the page except the Google Fonts stylesheet and font files.
8. No em dash, no emoji, no percentage and no score anywhere in the three files. Run codespell on them.
9. The facts in parts 04 to 06 against the build, as listed in `design/product/spec/site.md` section 14.
