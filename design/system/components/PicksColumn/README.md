Answer cells as a column, for a Call it that has no trace frames to draw, and the failing test that comes before them. When the trace has frames, use the Path component.

- Add `fh-picks--col` to `fh-picks`. Each cell is still a `button` with `aria-pressed`, 48px tall at least, sharing borders with its neighbours.
- A cell has a numbered gutter (`n`) and the path (`t`) in `fact`. A long path wraps inside its cell.
- "Somewhere else" keeps its number and takes `fh-pick--word fh-pick--gap`, so the words stand apart from the paths. "Don't know" has an empty gutter.
- One cell at a time. A tap locks the answer at once, so there is no Lock button on this sheet. Say so under the cells in `fh-keys`.
- Why a file is listed is never shown here. It can mark the answer. It is shown after the result, under More.
- `fh-trace` is the failing test: `paper-sunk`, the test and its message in `fact` at weight 500. With no frames it has no frame lines.
