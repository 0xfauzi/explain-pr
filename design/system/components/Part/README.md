A part of the site: one ink rule, a number and a note in the margin column, a title in `voice-lg`. Site only: the Room does not use it.

- The double rule opens the page and is not repeated. Every part after the first screen opens with a single 1px `ink` rule and 96px of paper above it (64px below 760px).
- The margin column holds the part's number in `ink` and a two or three word note under it in `ink-3`, both `fact-sm`. The note says what kind of part this is ("Three steps", "State of the build", "Version 0.6.0"). It never repeats the title.
- The title is `fh-part__title`, an `h2`. One optional `fh-part__lead` in `voice-sm` follows it. Both sit in the main column.
- Content that has no margin note of its own goes in `fh-part__body`, which starts at the main column. Content that has margin notes is a `fh-ledger` of `fh-row`s placed directly in the part, with a `fh-label` in each `fh-row__margin`.
- Long reading text is `fh-prose` (`voice-sm`, at most 612px). An explanation inside a row is `fh-text` (`ui-md`). Paths, addresses and commands inside either are `code`, set in `fact`.
- A caption under a block is `fh-cap`, in `fact-sm`.
- Below 760px the number and note move above the title on one line and the title drops to 28px.
