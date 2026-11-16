The frame of every Room page: the folio, the tab line with its end group, and the page foot.

- `fh-page` is the page column: 920px at most, 32px side padding, 16px under 600px.
- The tab line ends with `fh-tabs__end`: the quiet toggle, then Settings. They are set lighter than the tabs because they are not places in the record.
- The quiet toggle is `fh-toggle`, a button with `aria-pressed`. Its state is a small `fact` cell: outlined for off, filled `ink` for on. It is never `call`: quiet is a setting, not an answer.
- With more than one project the place in the folio is a native `select` with class `fh-select`: a `fact` word on a rule with a drawn caret. With one project it is plain text.
- `fh-pagefoot` closes every page: on the left where the page is served from, on the right today's count. Both are `fact`.
- `fh-sec` is the label line that opens a section. It may carry a count on the right in `fh-sec__n`.
- Nothing in the frame moves.
