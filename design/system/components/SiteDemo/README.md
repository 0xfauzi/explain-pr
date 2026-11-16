The example on the site: one question sheet in the first screen and one spread under it, shown by state. Site only. A result that did not match looks as it does in Spread.

- The state is one attribute, `data-demo`, on the page: `ask`, `locked`, `skipped`, `result`, or `nojs` as written in the HTML. An element that belongs to some states lists them in `data-v`. The style hides the rest. Nothing is built or removed by script except the words of the answer and the verdict.
- **ask.** The sheet as in Question, with nothing chosen and Lock disabled until a cell is on. The spread is `fh-spread--wait` with a blank dotted line where the call will be written (`fh-blank`) and one `fh-wait` line on the right. No perforation, no mark, no test results anywhere on the page.
- **locked.** The cells close. `fh-held` opens under them with the call in `fh-answer`, How sure, Show the result and Undo, as in Locked. The same call is written on the left of the spread. The right side still says nothing about the run. The highlighter leaves the question: it is no longer open.
- **skipped.** The cells close and one `fh-sheet__state` line says so, with Undo.
- **result.** The sheet keeps the held call and says the result is printed below. The spread prints once, in the order in Motion: perforation, mark, the run's lines, then the finding and the line sent to the agent. The verdict in words arrives with the mark.
- **nojs.** Cell 2 is on, all cells are disabled, and the result for the answer 2 is shown without motion.
- The bar of the sheet carries the state on the right: "skip ok", "locked 14:02:11", "skipped".
- Never show a result in the sheet, and never show any of the run before the call is locked.
