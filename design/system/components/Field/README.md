Three fields, told apart by who reads what is typed.

- `fh-input--write` is the person's own answer in words (the Brief's line). It is a single rule to write on, no box, and the text is `voice-answer`: italic Newsreader in `call`, with a `call` caret. It is the only field that is blue.
- `fh-input` is for text a machine reads: a command, a path pattern. A 48px box in `fact`. Join it to its button with `fh-fieldrow` so the two share a border.
- `fh-input--note` is a few words to a person or the record that are not an answer (why a result looks wrong). Roman `voice` on ruled lines, 32px apart.
- Every field has a visible `fh-label` above it. A hint under it is `fh-field__hint` in `fact`.
- An error goes directly under the field as `fh-err`.
- Enter in a one-line field does what its button does. Show the Enter keycap in that button.
- Focus is the 2px `call` outline, as everywhere.
