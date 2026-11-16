Three ledger rows the Room needs beside the entry row. All are rows between rules, never cards.

- **A row not yet written** (`fh-row--blank`) is the empty state. The margin shows the number the next entry will take and the word "next", in `ink-3`. The body says in one `voice` line what is not there, then the product's sentence in `ui`. Its rule is dashed. Never center it and never put it in a box.
- **A waiting row** is an entry row with no verdict: the margin shows the number and when the answer was locked, the YOU line is the answer in blue italic, and the RUN line says what the run is waiting for.
- **A note** (`fh-row--note`) is a fact from a run with no question. Its margin says "Note" and the time. Everything in it is `fact`, because a machine produced all of it: the fact as the title at weight 500, then each named test joined to its path and line by a leader, then how it was checked. A note has no YOU line and no verdict.
- `fh-row__kind` is the small label over a title that names the moment: Revert test, Call it, Brief. On a note it names the task, when the note has one.
- A title that opens a page is a link inside `fh-row__title`. It turns `call` on hover.
