Numbered steps as ledger rows: the explanation on the left, two facts with leaders on the right. Site only.

- Each step is a `fh-row`. The margin holds the step number as a figure (`fh-step__n`, `fact` at weight 300) and under it who acts: "Your agent", "You", "The run".
- The body is a `fh-step`: a title in `voice-md` that is a full sentence, one paragraph of `fh-text`, and beside it a `fh-status` list of exactly two facts that a reader can check ("Blocks a tool call ... never").
- The step about the person ("You make one call.") is roman, like the others. Blue italic is used once on the page, in the headline.
- A closing row with a `fh-label` in the margin and no number may follow the steps for what does not fit in one.
- Below 860px the facts move under the paragraph. Below 760px the figure becomes "Step 1" on one line with the note.
- On the site the list sits inside a part and opens with a `rule` line. The double rule in this preview is only there because the list stands alone.
