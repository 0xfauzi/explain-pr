Answer cells: 48px squares that sit flush and share borders, like the boxes on a paper form.

- Each cell is a `button` with `aria-pressed`. An arrow key must never choose an answer.
- Numbers are set in `fact`. Word answers use `fh-pick--word`, and the first of them takes `fh-pick--gap` so the words stand apart from the numbers.
- A cell the person turned on is filled `call`. Nothing else on a sheet is filled `call`.
- "None" and "Don't know" clear the numbers, and a number clears them.
- Once locked, the cells are disabled and the chosen ones stay filled.
