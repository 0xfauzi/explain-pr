The controls of the Settings page. They are filled `ink`, never `call`: a setting is not an answer, and blue stays the color of an answer.

- `fh-seg` is one of several: native radio inputs inside flush 48px cells that share borders, like answer cells. The chosen cell is filled `ink`. Use `fh-seg--num` for numbers, set in `fact`.
- Under the dial, list what each position does as `fh-facts` with leaders, and mark the current one `is-key`.
- `fh-check` is on or off: a native checkbox drawn as a 22px box. On is an `ink` square inside the box. A second line of explanation, if one is needed, goes in `small`.
- `fh-inline` sets a control inside a sentence: "Questions while building: 1 2 3 a day." The cells and "a day." sit in one `fh-inline__unit`, so they wrap together.
- The inputs are real `input` elements, so the keyboard works as it does everywhere: arrows move within a radio group, Space ticks a box.
- A press settles 1px in `dur-press`. Nothing slides.
