# Build the Room

This is the build spec for the Room in the Firsthand design system. It is written for a builder who has never seen the Room. Every design decision is made here. Where this file and `design/system/README.md` disagree, the README wins and this file has a bug.

The rebuild changes presentation only. Product behaviour, the fixed product words, scoring, the API routes and the key rule (nothing shows a result before the answer is locked) do not change.

## 0. How to use this file

- Read `design/system/README.md` first, all of it.
- Each screen below names a rendered reference. Render them with `python3 design/system/render.py <out dir>` and look at the PNG before building the screen. The preview HTML in `design/system/components/<Name>/preview.html` holds the exact markup. Copy the structure and the class names. Do not copy inline `style` attributes from a preview: section 2.3 says what replaces each one.
- All class names are in `design/system/components/bundle.css`. The Room's own additions are the block that starts "The Room. Everything below was added for the Room's own screens."
- Every string in this file that is in "double quotes" is exact copy. Strings marked (API) come from the engine and are set as given.

Files to change:

| File | What happens to it |
| --- | --- |
| `firsthand/room/page.html` | Rewritten (section 2.1) |
| `firsthand/room/static/room.css` | Rewritten: tokens, `@font-face`, then the component rules (section 1) |
| `firsthand/room/static/room.js` | Rewritten against the same API (sections 2 to 12). If it passes 800 lines of concern, split it into `room.js` (shell, API, routing, helpers) and `room-views.js` (the screens), both served from `/static/`. |
| `firsthand/room/static/fonts/` | New: 9 font files and 3 licence files (section 1.2) |
| `firsthand/room/server.py` | Serves the fonts, adds `font-src 'self'` (section 1.3) |
| `firsthand/views.py`, `views_callit.py`, `views_brief.py`, `views_skills.py` | New view fields (section 3). No existing field is removed or changed. |
| `pyproject.toml` | `package-data` gains `static/fonts/*` |
| `tests/firsthand/test_room_page.py` and other Room tests | Updated (section 14) |

## 1. Stylesheet, fonts and server

### 1.1 The stylesheet

`room.css` is, in this order:

1. The `@font-face` rules of section 1.2.
2. The contents of `design/system/tokens.css`, unchanged. Add a test that the token block in `room.css` equals `design/system/tokens.css` byte for byte. It replaces the old test against `design/learning-experience/assets/room.css`.
3. A small base: `html{scroll-padding-top:24px}`, `body{margin:0;background:var(--paper)}`, `button,input,select,textarea{font:inherit;color:inherit}`.
4. From `design/system/components/bundle.css`: everything from line 1 up to and including the section "Motion", then the whole block "The Room". Leave out the sections that are only for the site: Terminal, Site, Site page, Steps, Status ledger, Command block, Notes, Colophon, Site demo. Keep two rules from those sections because the Room uses them: the `.fh-status` rules (section "Site") and these two from "Site demo": `.fh-spread--wait .fh-wait{padding-left:14px}` and the `.fh-spread[data-play] ~ .fh-finding,.fh-spread[data-play] ~ .fh-acts` animation rule.

No rule in `room.css` may contain `url(` except the nine font `src` lines, and those must be relative paths starting `fonts/`. No `@import`.

The `body` element carries class `fh`. There is no theme switch: the dark theme follows `prefers-color-scheme` through the token block.

### 1.2 Fonts

The Room loads nothing from outside, so the three families are bundled as woff2 files. Source: the fontsource packages on npm, version 5.3.0, all under the SIL Open Font License 1.1. They are reachable from the build machine (checked: `npm pack @fontsource-variable/newsreader @fontsource/ibm-plex-mono @fontsource/ibm-plex-sans` downloaded all three). Get them with `npm pack` in a scratch directory, untar, and copy exactly these files from each `package/files/` into `firsthand/room/static/fonts/`:

| Package | File | Used for |
| --- | --- | --- |
| `@fontsource-variable/newsreader` | `newsreader-latin-opsz-normal.woff2` (132 kB) | Newsreader roman, weights 200 to 800, optical sizes 6 to 72 |
| `@fontsource-variable/newsreader` | `newsreader-latin-opsz-italic.woff2` (147 kB) | Newsreader italic, same axes |
| `@fontsource/ibm-plex-mono` | `ibm-plex-mono-latin-300-normal.woff2` | `fh-fig__n` figures |
| `@fontsource/ibm-plex-mono` | `ibm-plex-mono-latin-400-normal.woff2` | `fact` |
| `@fontsource/ibm-plex-mono` | `ibm-plex-mono-latin-400-italic.woff2` | `fact` italic |
| `@fontsource/ibm-plex-mono` | `ibm-plex-mono-latin-500-normal.woff2` | labels, key facts |
| `@fontsource/ibm-plex-sans` | `ibm-plex-sans-latin-400-normal.woff2` | `ui` |
| `@fontsource/ibm-plex-sans` | `ibm-plex-sans-latin-500-normal.woff2` | tabs, cells |
| `@fontsource/ibm-plex-sans` | `ibm-plex-sans-latin-600-normal.woff2` | buttons, current tab |

Copy each package's `package/LICENSE` beside them as `OFL-Newsreader.txt`, `OFL-IBM-Plex-Mono.txt` and `OFL-IBM-Plex-Sans.txt`.

Only the latin subset is bundled. A character outside it (in a task name, a path or a person's line) falls back to Georgia, ui-monospace or system-ui through the token stacks. That is accepted.

The `@font-face` rules, at the top of `room.css`. The family names must be exactly the names in the tokens:

```css
@font-face{font-family:Newsreader;font-style:normal;font-weight:200 800;font-display:swap;src:url(fonts/newsreader-latin-opsz-normal.woff2) format("woff2")}
@font-face{font-family:Newsreader;font-style:italic;font-weight:200 800;font-display:swap;src:url(fonts/newsreader-latin-opsz-italic.woff2) format("woff2")}
@font-face{font-family:IBM Plex Mono;font-style:normal;font-weight:300;font-display:swap;src:url(fonts/ibm-plex-mono-latin-300-normal.woff2) format("woff2")}
@font-face{font-family:IBM Plex Mono;font-style:normal;font-weight:400;font-display:swap;src:url(fonts/ibm-plex-mono-latin-400-normal.woff2) format("woff2")}
@font-face{font-family:IBM Plex Mono;font-style:italic;font-weight:400;font-display:swap;src:url(fonts/ibm-plex-mono-latin-400-italic.woff2) format("woff2")}
@font-face{font-family:IBM Plex Mono;font-style:normal;font-weight:500;font-display:swap;src:url(fonts/ibm-plex-mono-latin-500-normal.woff2) format("woff2")}
@font-face{font-family:IBM Plex Sans;font-style:normal;font-weight:400;font-display:swap;src:url(fonts/ibm-plex-sans-latin-400-normal.woff2) format("woff2")}
@font-face{font-family:IBM Plex Sans;font-style:normal;font-weight:500;font-display:swap;src:url(fonts/ibm-plex-sans-latin-500-normal.woff2) format("woff2")}
@font-face{font-family:IBM Plex Sans;font-style:normal;font-weight:600;font-display:swap;src:url(fonts/ibm-plex-sans-latin-600-normal.woff2) format("woff2")}
```

`font-optical-sizing:auto` is already on `.fh`. Do not preload fonts: `page.html` may reference only the stylesheet and the script.

### 1.3 The server

In `firsthand/room/server.py`:

- `STATIC` gains the nine font names as `fonts/<file>.woff2` with type `font/woff2`, and the three licence files with `text/plain; charset=utf-8`. The lookup stays an exact match against that table: no path joining from the request, so no traversal. `_public` already strips `/static/` and looks the rest up, so a key such as `fonts/newsreader-latin-opsz-normal.woff2` works as it is. If the script is split, add `room-views.js`.
- Font responses keep `SECURITY_HEADERS` (so `Cache-Control: no-store` stays: the files are local and small).
- The Content-Security-Policy gains `font-src 'self'`. Nothing else in it changes. `style-src 'self'` stays, which is why no inline `style` attribute or `style` element may exist in the page or be written by the script.
- `pyproject.toml`: `"firsthand.room" = ["page.html", "static/*", "static/fonts/*"]`.

## 2. The frame of every page

Reference: `Shell`, `Notice`, `ScreenInboxAll`.

### 2.1 `page.html`

```html
<body class="fh">
<div class="fh-page">
<header class="fh-folio">
  <a class="fh-wordmark" href="/" aria-label="Firsthand, the Room"><i>First</i>hand</a>
  <span class="fh-folio__place"><b>The Room</b><span id="proj"></span></span>
  <span class="fh-folio__right" id="folio"></span>
</header>
<nav class="fh-tabs" id="tabs" aria-label="Room">
  <a href="/" data-tab="inbox">Inbox<span class="n" id="count" hidden></span></a>
  <a href="/journal" data-tab="journal">Journal</a>
  <a href="/skills" data-tab="skills">Skills</a>
  <span class="fh-tabs__end">
    <button type="button" class="fh-toggle" id="quiet" aria-pressed="false" hidden>Quiet <b>off</b></button>
    <a href="/settings" data-tab="settings">Settings</a>
  </span>
</nav>
<div id="notice" hidden></div>
<main class="fh-main" id="main"></main>
<footer class="fh-pagefoot"><span>Served by this computer at 127.0.0.1.</span><span id="asked"></span></footer>
<p class="fh-vh" aria-live="polite" id="live"></p>
</div>
</body>
```

The `head` keeps the charset, viewport and referrer metas, `<title>Room</title>`, the one stylesheet link and the deferred script. There is no bottom tab bar any more: the tab line fits a phone.

### 2.2 What the script fills in

- **Folio place** (`#proj`). With one project: the text ` / ` then the project name (API `inbox.project.name`). With more than one: ` / ` then `<select class="fh-select" aria-label="Project">` with one option per `inbox.projects`, the current one chosen. Changing it sets `location.search` to `?project=<id>` as today. With no project: nothing.
- **Folio right** (`#folio`). The date and where the page is served from: `Mon 16 Nov 2026 · 127.0.0.1:4127`. Date from the browser clock: three-letter weekday, day without a leading zero, three-letter month, year. English names from a fixed table in the script, not from `toLocale*`. Then ` · ` (a middle dot, U+00B7) and `location.host`.
- **Tabs.** `aria-current="page"` goes on Inbox for `/` and `/q/<ref>`, on Journal for `/journal` and `/r/<ref>`, on Skills for `/skills`, on Settings for `/settings`. Every tab `href` keeps the `?project=` parameter, as today.
- **Inbox count** (`#count`). The number of items in `inbox.now`. Hidden when it is 0. This is the only `mark-bright` on any Room page.
- **Quiet toggle** (`#quiet`). Hidden with no project. `aria-pressed` is true when `inbox.state.quiet` is not null, and its `b` reads "on" or "off". Disabled when the scope is `session` (it cannot be undone from the Room). A click posts exactly what `toggleQuiet` posts today.
- **Page foot** (`#asked`). API `inbox.closing`, for example "Asked today: 0 of 1.".
- **Live region** (`#live`). As today: one polite region, set through the `say()` helper.

### 2.3 Rules for the script

- Build DOM with `createElement` and `textContent` only. Never `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `localStorage`.
- Never write a `style` attribute. Two things the previews do with inline styles are done through the CSSOM instead, which the CSP allows: custom properties (`el.style.setProperty('--i', 3)`, `'--n'`) and grid placement in a skill track (`el.style.gridRow`, `el.style.gridColumn`). Every other inline style in a preview has a class: page padding is `fh-page`, a section label line is `fh-sec`, a result head is `fh-head` and `fh-head__title`, an action line is `fh-acts` and `fh-acts__note`, body text is `fh-text`, an inline machine name is `fh-fact` inside `fh-text` or `fh-finding`.
- The verdict marks are inline SVG built with `createElementNS`. The three drawings are in `components/Verdict/preview.html`. One helper `mark(kind)` returns the `svg`; `verdict(kind, words)` returns `span.fh-verdict.fh-verdict--<kind>` holding the mark and the words. Map API `chip` to kind: `matched` to `match`, `did_not_match` to `miss`, `not_scored` to `none`. `chip` `pending` has no mark.
- **Two hands.** One helper `mixed(text, names)` returns a fragment in which every occurrence of a string from `names` is wrapped in `span.fh-fact`, longest name first. Use it wherever an engine sentence is set in `voice` or `ui` and may contain a test name or a path: the finding sentence, the cue sentence, the wait line. A second helper `counts(text)` wraps every `\d+ of \d+` in `span.fh-fact`. Sentences set whole in `fact` (the RUN line of a row, a note) need neither.
- **Entry numbers** print as `No. ` and the number padded to four digits: `No. 0042`.
- **Times.** The API gives UTC stamps (`2026-11-16T14:02:11Z`). The script prints them in the browser's zone: `HH:MM:SS` on a spread and a held stub, `HH:MM` in a margin for today, `D Mon HH:MM` in a margin for another day. Where the API already gives a formatted `time` or `date`, prefer the API's.
- **No key handlers.** The script has no `keydown`, `keypress` or `keyup` listener. See section 13.
- A re-render must never replay motion (section 12) and must keep focus: after any action that redraws a sheet, focus returns to the control that was pressed if it still exists, else to the first control of what replaced it.

### 2.4 Notices

Reference: `Notice`. `#notice` holds at most one `fh-notice`, chosen in this order:

| Condition | Margin label | Text | Action | Role |
| --- | --- | --- | --- | --- |
| The event stream or a request failed | "Not reachable" | "The Room cannot reach Firsthand on this computer. Start it with: " then `firsthand room` in `span.fh-fact` | none | `alert` |
| `inbox.state.dial` is `off` | "Off" | (API) `state.notice` without its last two words "Turn on" | `a.fh-btn.fh-btn--quiet` "Turn on" to `/settings` | `status` |
| `inbox.state.quiet` is set | "Quiet" | (API) `state.notice` without its last word "Undo" | `button.fh-btn.fh-btn--quiet` "Undo", unless the scope is `session` | `status` |

Markup: `div.fh-notice[role]` holding `span.fh-label > b`, `p.fh-notice__text`, then the action. With no notice, `#notice` is hidden and takes no space.

### 2.5 Errors and refusals

- A failed action on a sheet, a result or a settings row shows the engine's message (API `error.message`) as `p.fh-err[role=alert]`: `b` "Not taken", then a `span` with the message. It goes directly under the control that was used: under the cells on a sheet, under the field in a form, under the row's control in Settings. It is removed at the next successful action on that screen. The message is also sent to the live region.
- After a failed action the view is fetched again and redrawn, as today, and the error is shown on the redrawn view.
- A whole page that cannot load (`not_found` for a reference, or any other error at first load) is drawn as the page in section 10.
- `miss` red is never used for an error.

## 3. Data the views must add

Every field below is derived from recorded events or from state the views already read. Nothing here changes an event, the record format or scoring. Add each to the view named, with a test.

### 3.1 Entry numbers

There is no entry number in the record. It is derived: **the number of a moment is its 1-based position among the distinct moments that have a `moment.offered` event, in record order** (events are ordered by id, which is ordered by time). Add to `ViewInput.__post_init__`:

```python
self.numbers: dict[str, int] = {}
for e in self.events:
    if e["type"] == "moment.offered" and e.get("moment") and e["moment"] not in self.numbers:
        self.numbers[e["moment"]] = len(self.numbers) + 1
```

The number is counted across all projects, because the record is one logbook. A question closed as a wrong start keeps its number and is not shown, so numbers on a page can skip. That is honest and needs no comment on screen.

| View | Field | Value |
| --- | --- | --- |
| `question_view` (all three kinds) | `no` | `v.numbers.get(m.id)` (int or null) |
| `inbox_view` `now[]`, `waiting[]`, `results[]` | `no` | the same |
| `inbox_view` | `next_no` | `len(v.numbers) + 1` |
| `journal_view` moment entries | `no` | the same. Note entries have `no: null`. |

### 3.2 The question view (all three kinds)

| Field | Value and source |
| --- | --- |
| `kind_label` | `KIND_LABELS[m.kind]`: "Revert test", "Call it", "Brief" |
| `skill` | "Verification" for `revert_test`, "Debugging" for `call_it`, "Framing" for `brief`. These are the first words of the three existing `context_line` functions. Put them in one table in `views.py`. |
| `where` | `{"project": <project name>, "task": m.task_name, "since": words.clock_time(m.base_at, v.tz)}`. `since` is null for Call it and the Brief, whose context lines have no "change since". |
| `held.at` | `m.pending["at"]`, the stamp written when the answer was picked in the Room. Added to the dict `_held` returns. |
| `held.said`, `held.names` | As `call.said` and `call.names` below, computed from `m.pending["answer"]`. |
| `call.locked_at` | `body["picked_at"]` of the moment's last `call.sealed` event, else that event's `at`. This is the time the person locked, even when the Room sealed it later at Show the result. |
| `call.said` | The answer in words with no test name, no path and no confidence. Revert test, several tests: the numbers joined as `words._and` joins them ("1", "1 and 3"), or "None", or "Don't know". Revert test, one test: "Fails", "Still passes" or "Don't know". Call it: the number ("2"), or the number then ", somewhere else" for the last pick ("4, somewhere else"), or "Don't know". Brief: the line in double quotes as `words_brief.answer_text` gives it, or "Don't know". No full stop at the end. |
| `call.names` | The machine names the answer refers to, as a list. Revert test: the names of the picked tests. Call it: the picked path (empty for somewhere else). Brief: `[words_brief.test_name(m)]` when `extra["test"]` is set, else empty. |
| `call.confirm` | Brief only: `{"value": "yes" or "no", "at": <stamp>}` from the moment's last `call.confirmed` event, else null. |
| `prompt_text`, `prompt_name` | Brief confirm only: "Is this your check?" and `words_brief.test_name(m)`. `prompt` stays as it is. For every other sheet `prompt_text` equals `prompt` and `prompt_name` is null. |
| `result.fresh` | True when `m.opened` is false at the moment the view is built, which is before `question` or `show` sets it. It means: this is the first time this result is put on a screen. |

`call.confidence_label` already exists ("Sure", "Not sure"). The answer line on screen is `said` + "." + (" " + confidence_label + "." when set).

### 3.3 The result view

| Field | Value and source |
| --- | --- |
| `result.ran_at` | The `at` of the `check.ran` event the result was built from. Null when the Brief settled with no run. |
| `result.run_label` | "change undone" for Revert test and the Brief, "fix undone" for Call it. |
| `result.facts` | The run's lines as `[{"k": str, "v": str, "key": bool}]`. Revert test: one per test in `k.tests`, `k` the test name, `v` `words.more_row(t)`, `key` true when `t.result == "still_passes"`. Call it: first one per path in the key's `fix_paths` with `k` "the fix", `v` the path, `key` true; then one for the failing test with `k` its name, `v` `words_callit.more_row(k)`, `key` false. Brief: one for the test, `v` `words_brief.more_row(k)`, `key` true when it still passes. Empty when there was no run. |
| `result.names` | Every test name and path that can appear inside the result's sentences: the `k` of each test fact, the fix paths, the cue's evidence paths. For `mixed()`. |
| `result.counts` | The value now in `more.counts`, moved up because it is shown on the page. Keep `more.counts` too. |
| `more.why` | Call it only: the rows `pick_more_rows` returns, which today are appended to `more.rows`. Give them their own key so they can be drawn as their own list. Keep `more.rows` as it is. |

**The second time on a spread is not "finished".** The reference screens label it "finished 14:02:19". The record cannot support that. A `check.ran` event is written when the result is released from the key store, which happens only once the call is sealed. For Revert test the run has usually finished earlier and been held unseen, and the time it finished is not recorded. So the Room prints the time the result was written to the record, labelled **"recorded"**: `recorded 14:02:19`. It is never earlier than the lock time, and that is the true proof that the call came first.

### 3.4 The inbox view

| Field | Value and source |
| --- | --- |
| `now[].kind_label` | `KIND_LABELS[m.kind]` |
| `now[].since` | `words.clock_time(m.base_at, v.tz)` for Revert test, else null |
| `waiting[].task` | `m.task_name` |
| `waiting[].said` | `call.said` + "." + confidence, as the answer line of 3.2 |
| `waiting[].locked_at` | as `call.locked_at` |
| `results[].at` | the `at` of the moment's `moment.offered` event |
| `results[].said` | `words.you_said(m)` reduced as in 3.5 |
| `results[].happened` | the journal's "What happened" text for the moment (`_moment_entry` computes it) |
| `results[].ran` | true when that text came from a run (a result view exists) |
| `notes[].task` | the task name of the note's change, as `journal_view` already derives it (`tasks.get(note["change"])`), or "" |
| `asked` | `{"today": asked_today(v), "limit": v.settings.daily_limit}` |

### 3.5 The journal view

Each moment entry gains `no`, `time` (`words.short_date` and `words.clock_time` joined: "16 Nov 14:02"), `said` (the answer line of 3.2: said, full stop, confidence; "Skipped." or "No answer." when there was no answer, as `words.answer_text` gives), `happened` (the text now in `rows[1].text`) and `ran` (as 3.4). Each note entry gains `time`, `evidence` (the note body's evidence list: `test`, `path`, `line`) and keeps `task`. `rows` stays for the CLI.

### 3.6 The skills view

Each row gains:

| Field | Value and source |
| --- | --- |
| `matched`, `total`, `fixed` | the three ints `_counts(v, kind)` returns |
| `fixed_answer` | the fixed answer text ("none", "the file changed in this task") or null for the Brief |
| `calls` | One per scored call, oldest first: `[{"at": stamp, "day": "11 Nov", "you": "match" or "miss", "easy": bool or null, "catch": bool}]`. Source: the last `call.scored` event of each moment of this kind whose `result` is not `unscored` (exactly the set `_counts` counts). `you` is `body["result"]`. `easy` is `body["outcome_kind"] == "common"`, or null for the Brief. `catch` is `bool(body.get("catch"))`. `day` is `words.short_date(e["at"], v.tz)`. |
| `since` | `day` of the first call, or null |
| `days` | the number of distinct local days with a matched call, capped at 2 (the `have` in `_level`) |
| `shown_since` | the date `_shown_since` returns when the level is `shown`, else null |

**Only scored calls get a cell.** The reference Skill card mentions a dashed cell for Don't know. A Don't know, a skip and an unscored call are not in `_counts`, so a cell for them would make the cells disagree with the figures beside them. They are counted in the existing `asked` sentence and shown there.

**The level text.** The reference reads "Shown · a catch on 3 days". The record supports it, but the product's level sentence is "Shown since 13 Nov.", and product wording does not change. The Room prints `Shown` then ` · since 13 Nov`.

### 3.7 Nothing new for settings

`settings_view` already gives every value the Settings page shows.

## 4. Inbox (`/`)

References: `ScreenInboxAll`, `ScreenInboxEmpty`, `Rows`. Data: `GET /api/inbox`.

Structure inside `main`, in this order. A section with nothing in it is not drawn, except Now.

1. `h1.fh-vh` "Inbox".
2. **Now.** `div.fh-sec > span.fh-label > b` "Now". Then:
   - With an item in `now`: the sheet stub. `section.fh-sheet.fh-sheet--stub`; bar left (API) `reason` ("Your agent finished", "A test is failing", "Starting a task"), bar right `No. 0042 · skip ok`; body: `p.fh-sheet__ctx` project name then ` / change since 09:12` when `since` is set; `h2.fh-sheet__title` the task; `div.fh-sheet__act` holding `a.fh-btn` "Open" to `href` and `span.fh-sheet__size` with `kind_label · size` ("Revert test · One tap"). No footer, no evidence, no question, no highlighter. The stub does not fetch `/api/q/<ref>`: opening the sheet is what marks a question seen, and that must not change.
   - With none: `ol.fh-ledger.fh-ledger--head` holding one `li.fh-row.fh-row--blank`: margin `b` `No. <next_no>` then "next"; body `h3.fh-row__title` "No question is open."; then, only when `inbox.empty` is set, `p.fh-text` (API) `empty`.
3. **Waiting.** `fh-sec` label "Waiting", count on the right in `fh-sec__n`. A ledger of waiting rows (`Rows`): margin `No.` and "locked HH:MM"; `div.fh-row__kind` (API) `kind`; `h3.fh-row__title > a` task to `href`; `dl.fh-row__lines` with YOU `dd.you` `said` and RUN `dd.run` (API) `text`. No verdict. All rows are shown: the old "3 more" disclosure is gone.
4. **Notes.** `fh-sec` label "Notes", right `<shown> of <shown + older_notes>` when `older_notes > 0`. A ledger of note rows: `li.fh-row.fh-row--note`; margin `b` "Note" then (API) `time`; `div.fh-row__kind` the task when there is one; `h3.fh-row__title` (API) `title`; `ul.fh-facts` with one `li` per evidence item: `span.k` the test name (the part after the last `::`), `span.ld`, `span.v` `path:line`; `p.fh-row__foot` (API) `checked`. Notes are always open: the old `details` is gone. When `older_notes > 0`, after the ledger: `p.fh-acts > a.fh-btn.fh-btn--quiet` "Older notes" to `/journal`.
5. **Results.** `fh-sec` label "Results", right `<n> not opened`. A ledger of entry rows as in the Journal (section 8), built from `results[]`.
6. **Today**, only when Now is blank: `fh-sec` label "Today", then `ul.fh-status` with three `li`, each a label, `span.ld` and `b`: "Asked today" and `<today> of <limit>`; "The dial" and Off, Notes only, Standard or Deep; "Quiet" and off, this session, today or this project.

Behaviour: redrawn on an `inbox` or `settings` notice from the event stream, as today. Nothing on this page animates.

Phone: the ledger rows move their margin above the row (already in the stylesheet). The stub's bar and body tighten to 16px.

## 5. The question sheet (`/q/<ref>`, state `open`)

References: `Question`, `ScreenInbox` (several tests), `ScreenOneTest`, `ScreenCallIt`, `ScreenBrief`, `ScreenBriefConfirm`, `PicksColumn`, `Field`, `Disclosure`. Data: `GET /api/q/<ref>`.

`main` holds `h1.fh-vh` with `kind_label`, then one `section.fh-sheet[aria-labelledby=q]`. The order inside the sheet is fixed:

1. **Bar** `div.fh-sheet__bar`: left `kind_label`; right `No. 0042 · skip ok` (the words "skip ok" only when `skip_ok`).
2. **Body** `div.fh-sheet__body`, wrapped in a `form` whose `submit` is handled (section 13):
   1. `p.fh-sheet__ctx`: `where.project / where.task`, then ` / change since <since>` when set.
   2. `p.fh-sheet__lead`: (API) `reason`, a full stop, then (API) `lead` when there is one. "Your agent finished. It added 3 tests. Read them first." "A test is failing." "Starting a task."
   3. Brief confirm only: the person's line, as a stub. `div.fh-held` holding `div.fh-spread__head` (`span.fh-label > b` "Your check", `time` "locked HH:MM:SS" from `call.locked_at`) and `p.fh-answer.fh-answer--line` with `call.said`.
   4. Call it only: `div.fh-trace[tabindex=0][aria-label="The failing test and its trace"]`: `p.fh-trace__title` (API) `trace.title`; `ol` with one `li` per frame: `span.k` `path:line`, `span.ld`, `small` (API) `where`.
   5. Evidence, when `evidence` is not empty: `ol.fh-evidence[tabindex=0]` labelled by the lead. Per test: `span.n` its number; `span.t` holding `span.hd` (`b` the name, `span.ld`, `small` `path:line`), one `code` per assert line, and when `source` is not empty `details.fh-more.fh-more--in` with `summary` "Full test" and the listing of section 5.1.
   6. The question: `h2.fh-q#q > mark` with `prompt_text`. When `prompt_name` is set: `p.fh-q__name` with it, directly after.
   7. The answer control (5.2).
   8. `p.fh-keys` (5.2).
   9. `p.fh-err` when an action failed.
   10. `div.fh-sheet__act`: the primary button when the sheet has one, then `button.fh-btn.fh-btn--quiet` "Skip" when `can.skip`, then "Wrong start" when `can.wrong_start`.
3. **Footer** `div.fh-sheet__foot > span` (API) `footer`.

### 5.1 Full test

`ol.fh-code`, one `li` per line of `source`: `span.n` the real line number (the test's `line` plus the index), `code` the line with its leading spaces kept. A line whose number is in the test's `asserts[].line` gets class `is-key`. Closed by default. Opening is instant.

### 5.2 The answer control, by sheet

| Sheet | Control | Under it in `fh-keys` | Primary button |
| --- | --- | --- | --- |
| Revert test, several tests (`multi`) | `div.fh-picks[role=group][aria-labelledby=q]`: a number cell per test, then "None" with `fh-pick--word fh-pick--gap`, then "Don't know" with `fh-pick--word`. Cells toggle. None and Don't know clear the numbers and each other; a number clears them. | "Turn on any number of tests, then Lock." | `button.fh-btn[type=submit]` "Lock", disabled until a cell is on |
| Revert test, one test | `div.fh-picks`: "Fails", "Still passes" (`fh-pick--word`), then "Don't know" (`fh-pick--word fh-pick--gap`) | "A tap locks your answer. You can undo it before the result." | none |
| Call it | `div.fh-picks.fh-picks--col`: per pick with a `path`, `span.n` the number and `span.t` the path; then "Somewhere else" with its number, `fh-pick--word fh-pick--gap`; then "Don't know" with an empty `span.n`, `fh-pick--word`. The API `label` holds number and text joined by two spaces: split on the first run of spaces. | the same sentence as one test | none |
| Brief, the line (`form: "line"`) | `label.fh-field`: `span.fh-label` (API) `said_label` ("Your check"), `input.fh-input.fh-input--write[type=text][maxlength=500][autocomplete=off]` described by `#q` | none | `button.fh-btn[type=submit]` "Send to my agent" with `span.fh-kbd` holding the return sign U+21B5 |
| Brief, the confirm (`form: "pick"`) | `div.fh-picks`: "Yes", "No", both `fh-pick--word` | "A tap locks your answer." | none |

Every cell is a `button[type=button]` with `aria-pressed`. On sheets with no primary button a press posts `lock` at once with that cell's `value`, as today. On the several-tests sheet a press only toggles; Lock posts `lock` with the numbers ascending and comma-joined, or `none`, or `dont_know`. The Brief posts `lock` with the field's text; an empty field focuses the field and posts nothing.

Live region after a lock: "Locked." (Brief line: "Given to your agent."). After Skip: "Skipped.". After Wrong start: the new view's `status_line`, and if the engine returned a different `ref`, `history.replaceState` to `/q/<new ref>` as today.

Motion: the highlighter stroke, once (section 12). Nothing else.

Phone: the sheet's padding drops to 16px, the question to 28px, evidence heads stack (in the stylesheet). The column picks are full width. Buttons wrap.

## 6. Locked, before the result (`/q/<ref>`, state `held` with a pick)

References: `Locked`, `ScreenHeld`. Applies to Revert test and Call it. The Brief is never held.

The sheet of section 5 stays, with these changes:

- Bar right reads `No. 0042 · locked`.
- Every cell is `disabled`. The cells named by `held.answer` keep `aria-pressed="true"`.
- `h2.fh-q` gets `data-still`, so the highlighter does not pass again.
- `fh-keys` and the old action line are gone. In their place `div.fh-held`:
  1. `div.fh-spread__head`: `span.fh-label > b` "Your call"; `time` "locked HH:MM:SS" from `held.at`.
  2. `p.fh-answer`: `held.said`, a full stop, then " Sure." or " Not sure." when `held.confidence` is set; then `small` with `held.names` joined by ", " when not empty.
  3. `div.fh-held__sure`: `span.fh-label#sure` "How sure?"; `div.fh-picks[role=group][aria-labelledby=sure]` with two `fh-pick--word` cells "Sure" and "Not sure". A press posts `confidence` with `high` or `low`; pressing the one that is on posts `null`. The answer line above is redrawn from the returned view, so the word appears in the person's hand.
  4. `div.fh-sheet__act`: `button.fh-btn` "Show the result" (posts `show`); `button.fh-btn.fh-btn--quiet` "Undo" when `can.undo` (posts `undo`; live region "Undone.").
- The footer stays.

Nothing about the run is on this screen. After "Show the result" the returned view either has a result (section 7, and the result prints) or is sealed and waiting (section 7.5).

Phone: `fh-held__sure` wraps: the label, then the two cells on their own line if needed.

## 7. Results and what stands in for one (`/q/<ref>` and `/r/<ref>`)

References: `Spread`, `ScreenResult`, `ScreenResultMiss`, `ScreenResultMore`, `ScreenResultNotScored`, `ScreenWaiting`, `Waiting`, `ScreenClosed`, `Disclosure`, `Motion`.

Which layout, from the view:

| View | Layout |
| --- | --- |
| `result` set and `result.ran_at` set | 7.1 the result |
| `state` `sealed`, no `result`, `call` set, and the Brief is not asking for its confirm | 7.5 waiting |
| `held.kind` is `skip` | 7.6 with "Skipped." and Undo |
| anything else that is not open or held (skipped or closed with no run, a Brief settled with no run, a dropped check) | 7.6 |

### 7.1 The result

1. `div.fh-head`: left a `div` holding `div.fh-label` `No. 0042 · <kind_label> · <skill>` and `h1.fh-head__title` the task (`where.task`); right `verdict(chip, chip_label)`.
2. `div.fh-spread#res[tabindex=-1]` with `aria-label` = `chip_label`, a full stop, then the first `what_happened` sentence:
   - `div.fh-spread__side.fh-spread__call`: `div.fh-spread__head` (`span.fh-label > b` "Your call", or (API) `said_label` "Your check" for the Brief; `time` "locked HH:MM:SS" from `call.locked_at`); `p.fh-answer` built as in section 6 from `call` (the Brief's line takes `fh-answer--line`); for the Brief with `call.confirm`: a second `div.fh-spread__head` (`span.fh-label > b` "Is this your check?", `time` "locked HH:MM:SS" from `confirm.at`) and a second `p.fh-answer.fh-answer--line` "Yes." or "No.". When there was no answer (`call` is null): `p.fh-answer` with (API) `you_said` ("Skipped.", "No answer.") and no time.
   - The mark: `mark(kind)` as a direct child of the spread, between the sides.
   - `div.fh-spread__side.fh-spread__run`: `div.fh-spread__head` (`span.fh-label`: `b` "The run" then ` · <run_label>`; `time` "recorded HH:MM:SS" from `ran_at`); `ul.fh-facts` with one `li` per `result.facts`: `span.k`, `span.ld`, `span.v`, class `is-key` when `key`, and `--i` set to its index.
3. The finding: `div.fh-finding`: `span.fh-label` (API) `chip_label`; a `div` holding `p.fh-finding__text` = `mixed(what_happened[0], names)`, then one `p` for each further `what_happened` sentence, then one `p` with (API) `reason` when set.
4. Only when `cue` is set: `div.fh-finding.fh-finding--text`: `span.fh-label` "What would have shown it"; `p.fh-text` = `mixed(cue.text, names)`; then for each `cue.evidence` item with `text`: `ol.fh-code` holding one `li.is-key` (`span.n` the line number, `code` the text).
5. Only when `result.counts` is set: `div.fh-finding.fh-finding--text`: `span.fh-label` "Your record"; `p.fh-text` = `counts(result.counts)`.
6. More (7.2), when it has any content.
7. The recheck row (7.3), hidden until asked for.
8. `p.fh-err` when an action failed.
9. `div.fh-acts`: `a.fh-btn` "Back to the build" to `/`; `button.fh-btn.fh-btn--quiet` "Open the commands" when `more.commands` is not empty; `button.fh-btn.fh-btn--quiet` "This result looks wrong" when `can.dispute`; `span.fh-acts__note` (API) `more.checked`.

There is no button inside the spread. Back to the build is the one primary action. The old "Back to: ... Next: read the summary." line is not on this page: it is a line for the agent's chat.

On first draw of a result, focus goes to `#res` with `preventScroll`, and the live region says `chip_label`, a full stop and the first `what_happened` sentence, as today.

### 7.2 More

`details.fh-more`, closed by default, `summary` "More" then `span.ld`. Inside, one `div.fh-finding.fh-finding--text` per item that has content, in this order:

| Margin label | Content | Source |
| --- | --- | --- |
| "Why listed" | `ul.fh-facts`: `k` the pick ("1  pricing/pricing.py"), `v` why | `more.why` (Call it) |
| "How sure" | `p.fh-text` = `counts(more.sure)` | `more.sure` |
| "Sent" | `p.fh-text` | `more.sent` |
| "Recheck" | `p.fh-text` | `more.dispute` |
| "Notes" | one `p.fh-text` per line | `more.notes` (Brief) |
| "Commands" | `ol.fh-cmds#cmds`, one `li` per command | `more.commands` |

"Open the commands" opens the `details` and moves focus to `#cmds` (give it `tabindex=-1`). It does not animate.

### 7.3 Recheck

"This result looks wrong" reveals, between More and the action line, `div.fh-finding.fh-finding--text`: `span.fh-label` "Recheck"; `label.fh-field` (`span.fh-label` "This result looks wrong", `textarea.fh-input.fh-input--note[rows=3][maxlength=4000]`); `div.fh-acts` with `button.fh-btn.fh-btn--second` "Recheck" and `button.fh-btn.fh-btn--quiet` "Cancel". Focus moves to the textarea. Recheck with an empty field focuses the field. Otherwise it posts `dispute` with `reason`; the returned view is drawn (without replaying motion) and the live region says `more.dispute`. Cancel hides the row and returns focus to "This result looks wrong".

### 7.4 Verdicts

| `chip` | Mark | Notes |
| --- | --- | --- |
| `matched` | aligned bars on `call` | No green anywhere. |
| `did_not_match` | struck bars, `miss` | The only place `miss` appears. The cue row is present. |
| `not_scored` | dashed bars | `reason` says why, in the finding. No cue. No recheck. |

All three moments use the same page. They differ only in `kind_label`, `skill`, `run_label`, the facts, the Brief's two-part call and Call it's "Why listed".

### 7.5 Waiting

The page of 7.1 with these differences:

- The head has no verdict.
- The spread has class `fh-spread--wait`, no mark, and its run side holds `div.fh-spread__head` with only `span.fh-label > b` "The run", then `p.fh-wait` = (API) `status_line`, with any name from `call.names` or the Call it test name wrapped in `b`.
- No finding, no record, no More.
- `div.fh-acts`: `a.fh-btn.fh-btn--second` "Back to the build".

When a `question` notice arrives and the new view has a result, the page is **not** rebuilt from nothing: the call side stays in the DOM untouched, the spread loses `fh-spread--wait`, gains the mark, the run side's content and `data-play`, and the rows below are appended. This is what makes "your call was already there" true on screen. The same in-place update applies when the page was drawn waiting after "Show the result".

### 7.6 No run to show

`div.fh-head` as in 7.1, with `verdict('none', 'Not scored')` only when the view has a `result` (a Brief that settled unscored). Then one `div.fh-finding`: `span.fh-label` "Skipped" when the state is `skipped` or the held kind is `skip`, else "Closed"; `p.fh-finding__text` the sentence:

| Case | Sentence |
| --- | --- |
| held skip | "Skipped." |
| `result.reason` set | (API) `result.reason` |
| else | (API) `status_line`, or "Skipped." for state `skipped` with none |

Then `div.fh-acts`: `a.fh-btn.fh-btn--second` "Back to the build"; `button.fh-btn.fh-btn--quiet` "Undo" when `can.undo`. Wrong start, fix started, moved on, shown first and a dropped check all land here with their own `status_line`.

Phone, all of section 7: the spread stacks, call above run, with the perforation across and the mark on it (in the stylesheet). `fh-finding` rows put their label above. `fh-acts__note` takes its own line.

## 8. Journal (`/journal`)

References: `ScreenJournal`, `Ledger`, `Rows`. Data: `GET /api/journal`.

1. `h1.fh-vh` "Journal".
2. `div.fh-sec`: `span.fh-label` (`b` "Journal" then ` · ` and (API) `scope`); `span.fh-sec__n` `<n> entries, newest first` ("1 entry" for one).
3. `ol.fh-ledger.fh-ledger--head`, one `li` per entry, in the API's order:
   - **A call**: `li.fh-row`; margin `b` `No. 0042` then (API) `time`; `div.fh-row__kind` (API) `kind`; `div.fh-row__head` with `h3.fh-row__title > a` task to `href` and `verdict(chip, chip_label)` (no verdict for `pending`); `dl.fh-row__lines`: `dt` "You", `dd.you` `said`; `dt` "Run", `dd` `happened` with class `run` when `ran` is true and `say` when false.
   - **A note**: the note row of section 4, with (API) `time` as the margin time and `rows[0].text` as the title.
4. Empty: the ledger holds one `li.fh-row.fh-row--blank`: margin `b` `No. <next number>` when known (fetch it from the inbox view already held), else "No entries"; `h3.fh-row__title` "No calls or notes yet.".

Redrawn on any notice, as today. No motion. The link's accessible name is the task; the verdict words follow it in the row, so nothing more is needed.

## 9. Skills (`/skills`)

References: `Skill`, `SkillStates`, `ScreenSkills`. Data: `GET /api/skills`.

1. `h1.fh-vh` "Skills".
2. `div.fh-sec`: `span.fh-label` (`b` "Skills" then " · all projects"); `span.fh-sec__n` "Checked by a run.".
3. The key, `ul.fh-key[aria-label=Key]`, five `li`, each an `i` then text: `i.on` "your call matched"; `i.miss` "did not match"; `i.easy` "the easy answer would have matched"; `i` "it would not"; `i.catch` holding U+25BE then "a catch: you matched and the easy answer did not".
4. `ol.fh-ledger.fh-ledger--head`, one `li.fh-row` per API row:
   - Margin: `b` `Skill <n>`; then `<total> calls since <since>` ("1 call"), or "no calls yet".
   - `div.fh-row__head`: `h3.fh-row__title` (API) `name`; the level:
     - `shown`: `span.fh-level`: `b` "Shown" then ` · since <shown_since>`.
     - `too_few`: `span.fh-level`: "Too few calls · " then `b` `<days> of 2`.
     - `none`: `span.fh-level.fh-level--none > b` "No level yet".
   - `div.fh-skill__top`:
     - The track, `div.fh-track[role=img]`, only when `calls` is not empty. Show the newest 24 calls. `--n` is the number shown. Children, placed through the CSSOM: row 1 one `span.catch` per column holding U+25BE when `catch`; row 2 `span.lb.lb--you` "You" in column 1 then one `i.you` per call with class `on` for a match and `miss` for a miss; row 3, only when `fixed_answer` is set, `span.lb` "Easy" then one `i.easy` per call with class `on` when `easy`; row 4 one `span.date` per run of calls on the same `day`, spanning those columns, reading the full `day` when it spans two columns or more and only the day number when it spans one. Each `i` gets `--i` = its column index from 0. `aria-label`: "<n> calls. You matched <matched>." then, with an easy answer, " The easy answer would have matched <fixed>. <c> of yours were catches." (counts over all calls, not only those shown).
     - `div.fh-figs`: `div.fh-fig.fh-fig--you` (`div.fh-fig__n`: `b` matched, a space, `span` `of <total>`; `p.fh-fig__cap` "of your calls matched"); and with an easy answer `div.fh-fig` (`fixed`, `of <total>`, caption `if you had always said "<fixed_answer>"`).
   - `p.fh-track__more` `newest 24 of <total>` when more than 24.
   - `p.fh-skill__counts`: (API) `asked`, then (API) `newest` with its first letter in upper case and a full stop, when set.
   - For level `none`: `p.fh-text` (API) `level_line`.
   - `div.fh-skill__note`: two `div`, each `span.fh-label` then text: "Covers" (API) `covers`; "No evidence on" (API) `no_evidence`.
5. After the ledger: `div.fh-finding.fh-finding--text`: `span.fh-label` "Shown"; one `p.fh-text` per (API) `legend` line.

The row's `li` gets `aria-label`: name, level line, newest, as today.

Motion: the tallies fill (section 12). Phone: the track's cells shrink to fit (in the stylesheet), the figures go under the track, the two notes stack.

## 10. No session, not found, cannot start

Reference: `ScreenNoSession`.

When `/api/session` answers `no_session`, or any request does later: hide `#tabs`, `#notice` and `#quiet`, set `#proj` to " / not signed in", clear `#asked`, and draw in `main`: `h1.fh-vh` "The Room"; `ol.fh-ledger` with one `li.fh-row.fh-row--blank`: margin `b` "No session"; `h2.fh-row__title` "This page needs a session."; `p.fh-text` "Run in a terminal:"; `ol.fh-cmds` with one `li`: the command. Take the command from the server's message: it is the text after "Run in a terminal: " (API `error.message`, which names the command as it is typed on this computer). If the message does not contain that phrase, show the whole message in `p.fh-text` and no command line. Keep the constant `'This page needs a session. Run: firsthand room'` as the fallback when there is no message.

Other whole-page states use the same row:

| Case | Margin | Title | Text |
| --- | --- | --- | --- |
| First load cannot reach the server | "Not reachable" | "The Room cannot reach Firsthand on this computer." | "Start it with:" then `ol.fh-cmds` "firsthand room" |
| `/q/<ref>` or `/r/<ref>` not found | "Not found" | (API) `error.message` | `a.fh-btn.fh-btn--second` "Back to the build" to `/` |
| Any other error at load | "Error" | (API) `error.message`, or "Something went wrong inside Firsthand. Nothing was changed." | none |

For the last three the tabs stay.

The `/enter` page with a used ticket stays plain text from the server. It is not part of the page.

## 11. Settings (`/settings`)

References: `ScreenSettings`, `Choice`, `Field`, `Notice`. Data: `GET /api/settings`, `POST /api/settings`.

`h1.fh-vh` "Settings", then three sections. Each is a `div.fh-sec` and an `ol.fh-ledger.fh-ledger--head` of `li.fh-row` whose margin `b` names the setting and whose body is `div.fh-set`.

**How much** (`fh-sec` label "How much")

| Margin | Body | Posts |
| --- | --- | --- |
| "The dial" | `fieldset.fh-seg` with `legend.fh-vh` "The dial" and four `label > input[type=radio][name=dial] + span`: "Off", "Notes only", "Standard", "Deep". Then `ul.fh-facts`, four `li`: `k` the position, `ld`, `v` its sentence, `is-key` on the current one: "Nothing is asked, run or recorded." "No questions. Checks run and post notes." "Questions within the daily limit." "As Standard. You may also write a line of code on some questions." | `{dial}` |
| "Questions" | `p.fh-inline`: "Questions while building: " then `span.fh-seg.fh-seg--num[role=radiogroup][aria-label="Questions while building, a day"]` with radios 1, 2, 3, then " a day (up to 3)." | `{daily_limit}` as a number |
| "Quiet" | `label.fh-check > input[type=checkbox] + span` "Today"; and with a project, a second "This project" | `{quiet_today}`; `{quiet}` with the project id |
| "Findings" | `label.fh-check` "Send findings to my agent" | `{findings_to_agent}` |

**This project** (label `b` "This project" then ` · <name>`), only when `project` is set

| Margin | Body | Posts |
| --- | --- | --- |
| "Test command" | `div.fh-field`: `label.fh-vh[for=cmd]` "Test command"; `div.fh-fieldrow` with `input.fh-input#cmd[type=text][spellcheck=false]` and `button.fh-btn.fh-btn--second[type=button]` "Change"; `p.fh-field__hint` "Checks stop after 2 minutes." (the number from `check_time_limit_s`: whole minutes as "1 minute" or "n minutes", else "n seconds") | `{test_command}` with the project id |
| "High-stakes paths" | `ul.fh-list`, one `li` per pattern: `span.k` the pattern, `span.ld`, `button.fh-btn.fh-btn--quiet[aria-label="Remove <pattern>"]` "Remove". Then `div.fh-field`: `label.fh-vh[for=glob]` "Add a path"; `div.fh-fieldrow` with `input.fh-input#glob[type=text][spellcheck=false]` and `button.fh-btn.fh-btn--second[type=button]` "Add a path" | `{high_stakes_remove}`; `{high_stakes_add}` (trimmed, not when empty), with the project id |

**Your record** (label "Your record"): one row, margin "Kept at", `p.fh-text`: `span.fh-fact` (API) `record`, then ". A git repo on this computer. Plain files. No remote."

Behaviour:

- Every control posts on change (the two text fields on their button), with `confirm: false`. On success the returned view is drawn, the live region says "Saved.", and the frame is refreshed (`loadShell`), as today. Focus returns to the control that was used.
- **The confirm step.** When the engine answers `confirm` (code 409 `confirm`), the view is fetched and drawn again (so the control shows its saved value, not the requested one), and the row that was changed is followed by `li.fh-confirm[role=group][aria-label=Confirm]`: `span.fh-label > b` "Confirm"; `p.fh-confirm__text` (API) `error.message` ("This change asks or sends more. Confirm it."); `ul.fh-facts` with one `li`: `k` the setting, `ld`, `v` the change; `div.fh-acts` with `button.fh-btn` "Confirm" and `button.fh-btn.fh-btn--quiet` "Cancel". Focus goes to Confirm and the live region says the message. Confirm posts the same change with `confirm: true`. Cancel removes the step and returns focus to the control. Only one confirm step is open at a time. The change line reads:

  | Setting | `k` | `v` |
  | --- | --- | --- |
  | dial | "The dial" | `<from> to <to>` ("Standard to Deep") |
  | daily_limit | "Questions while building" | `<from> to <to> a day` |
  | findings_to_agent | "Send findings to my agent" | "off to on" |
  | test_command | "Test command" | the new command |

- Any other error is `p.fh-err` under the control (section 2.5).
- The page is not redrawn from the event stream while a text field has focus, as today.

No motion beyond the press. Phone: margins move above rows, `fh-fieldrow` stays one line (the input shrinks), the dial's four cells wrap to two lines if they must and still share borders.

## 12. Motion

All motion uses the tokens and the keyframes already in the stylesheet. Nothing loops in the Room. Nothing plays twice.

| What | Where | When | How |
| --- | --- | --- | --- |
| The highlighter stroke | the `mark` in `h2.fh-q` | The first time the sheet for a given `ref` is drawn in this page load | Plays from the stylesheet (`fh-stroke`, `dur-stroke`, `ease-pen`, 180ms delay). Keep a set of refs already drawn. Every later draw of that sheet (after a toggle, an error, Undo, a lock) sets `data-still` on the `h2`. |
| A press | answer cells, buttons, `fh-seg` cells, tick boxes, the quiet toggle | on press | Color in `dur-state`, 1px settle on `:active`. From the stylesheet. |
| The result prints | the spread and the rows after it | Once per result, ever: only when `result.fresh` is true, or when a waiting page receives its result (7.5). | Set `data-play` on `div.fh-spread`. The stylesheet does the rest in order: the perforation draws (`dur-line`), the mark lands (`dur-stamp`, `ease-stamp`), the run head appears, each fact prints `stagger` apart with its leader, then the finding and every row after the spread (cue, record, More, actions) appear together. The call side has no animation: it is drawn complete. |
| | | A result opened later (from the Journal, a reload, a redraw after a recheck or an error) | No `data-play`. Everything is in its final state. |
| Tallies fill | each `fh-track` | The first time that row is at least 60% in view in this page load | An `IntersectionObserver` sets `data-play` on the track. Keep a set of skill numbers already played. A redraw from the event stream draws those tracks without `data-play`. Before a row has played, its track is drawn without `data-play` too, so with no observer support it is simply final. |

A redraw must not cut a sequence short. When a notice from the event stream brings a view for the result already on screen, compare it with the view that was drawn (as JSON, ignoring `result.fresh`) and do nothing when they are equal.

Never: animate layout, height or a disclosure; fade a page or a tab in; move anything the person has to click; animate a notice, an error, the confirm step, the held stub or the empty rows.

**Reduced motion.** `@media (prefers-reduced-motion:reduce)` in the stylesheet removes every animation and transition under `.fh`. The script must not depend on `animationend` or `transitionend` for anything. Focus and the live region are set at once, never after an animation. With reduced motion a fresh result is simply complete when it is drawn.

## 13. Keys

- The Room has no single-key shortcuts. The reference Question card shows `1 2 3 toggle · N none · ? don't know` under the cells. The product's rule is that letter and number shortcuts are off by default, and there is no setting to turn them on, so the Room does not have them and does not print that line. The `fh-keys` line carries the one-sentence instruction of section 5.2 instead.
- Everything works with Tab, Shift+Tab, Space and Enter as the browser provides. Cells are buttons: Space or Enter presses the focused one. An arrow key never chooses an answer.
- The sheet's body is a `form`. Its `submit` handler calls `preventDefault` and then does what the sheet's primary button does (Lock, or Send to my agent). This is why Enter in the Brief's line sends it, and why "Send to my agent" carries the Enter keycap. The several-tests Lock button does not carry a keycap: Enter on a focused cell presses that cell, so the cap would be untrue.
- In Settings the radio groups use the browser's arrow keys. A change by arrow key posts like any change, and a widening one stops at the confirm step, so no key can widen a setting on its own.
- Focus is always visible: the 2px `call` outline from the stylesheet. Do not remove an outline anywhere.

## 14. What to delete, and tests

Delete from `room.css`: everything. No old class survives. In particular the old token block (`--card`, `--accent`, `--lv0` and the rest, copied from `design/learning-experience`), every rounded card and pill (`.card`, `.pill`, `.chip`, `.btn`, `.tbtn`, `.qbtn`, `border-radius` of 10px and above), the sticky top bar and the bottom tab bar (`.top`, `.bar`, `.tabbar`, `body.hastabs`), `.quietbar`, `.crumb`, `.grp`, `.it`, `.rw`, `.ev`, `.lock`, `.sure`, `.cue`, `.jl`, `.je`, `.sl`, `.sr`, `.sg`, `.opt`, `.fld`, `.globs`, `.confirm`, the grain variables and the orange accent.

Delete from `room.js`: `chip()`, `rows()`, `pill()`, `group()`, `nowItem()`, `noteItem()` (the `details` form), `waitingGroup()` and its "more" disclosure, `sureRow()`, `lockRow()`, `renderSkipped()`, `cueRow()`, the "Inbox" crumb, the page `h1.pg` titles, `option()`, the `select` for the daily limit, and `askConfirm()`'s floating box. Keep, unchanged in behaviour: `api()`, `route()`, `withProject()`, `say()`, the draft logic for several tests (`chosenOf`, `draftFor`, `draftAnswer`, `toggle`), `act()` and its refetch on error, `save()`, `toggleQuiet()` and `quietOff()`, `typing()`, `refresh()`, `onNotice()`, `listen()` and its reconnect, `boot()`.

Remove from `page.html`: the sticky header, the bottom `nav.tabbar`, `body.hastabs`, the `.quietbar`.

Tests to update in `tests/firsthand/test_room_page.py`:

- `test_page_references_only_static_urls`: the asset list stays `room.css` and `room.js` (plus `room-views.js` if split).
- `test_page_shell`: ids are now `main`, `live`, `notice`, `quiet`, `proj`, `folio`, `tabs`, `count`, `asked`. The labels are "Inbox", "Journal", "Skills", "Settings", and the wordmark replaces "Room" (the `title` stays "Room"). The footer sentence stays.
- `test_css_and_js_hold_no_remote_url`: `url(` is now allowed only in the nine `@font-face` lines and only for paths that start `fonts/`. `@font-face` is now required, nine times. `@import` stays forbidden.
- `test_token_block_equals_the_design_system`: compare against `design/system/tokens.css`.
- `test_component_rules_are_present`: replace the list with the new names: `.fh-folio{`, `.fh-tabs{`, `.fh-sheet{`, `.fh-q{`, `.fh-picks{`, `.fh-pick{`, `.fh-held{`, `.fh-spread{`, `.fh-answer{`, `.fh-facts{`, `.fh-finding{`, `.fh-m{`, `.fh-verdict{`, `.fh-ledger{`, `.fh-row{`, `.fh-track{`, `.fh-more{`, `.fh-notice{`, `.fh-confirm{`, `.fh-err{`, `.fh-input{`, `.fh-seg{`, `.fh-check{`, `@media (prefers-reduced-motion:reduce)`.
- `test_js_fixed_copy`: every line in the list is still in the script. Add "Lock", "Send to my agent", "Recheck", "Turn on any number of tests, then Lock.".
- `test_no_em_dash_or_letter_shortcut`: unchanged. The script still has no `keydown` and no `keypress`.
- New: no `style=` in `page.html`; no `setAttribute('style'` and no `.style.cssText` in the script.

Tests to add or update elsewhere: the static route serves each font with `font/woff2` and the security headers; a font name not in the table is 404; the CSP contains `font-src 'self'`; each new view field of section 3 (entry numbers stable when a later moment is offered, `locked_at` from `picked_at`, `ran_at`, `facts` and `key` for each moment, `fresh` true once then false, `calls` equal in length to `total`).

## 15. Checks before calling it done

- `python -m unittest discover -s tests` passes.
- `ruff` is clean and `complexipy` reports no function over 15 on every changed Python file. No Python file is over 800 lines: `views.py` is at 763 now, so put the new view helpers in a new module (for example `firsthand/views_room.py`) and call them from the views.
- With a temporary `HOME` (as `tests/firsthand/support.py` does), drive each screen of sections 4 to 11 in Chromium at 960 and 390 wide, in both themes, and compare each with its reference render. No request leaves 127.0.0.1. No console error. No CSP violation. No horizontal scroll at 390.
- Play a result once and check the order: perforation, mark, lines, finding. Reload: nothing moves. Set reduced motion: nothing moves at all.
- Tab through an open sheet, a held sheet, a result and Settings: every control is reached, the outline is visible, and no arrow key answers a question.
