One changed part and the parts outside the change. Use it for a question about a system, not about a line of code: Who is affected.

- The changed part is the dark block. Say in one or two plain sentences what changed. Do not show code.
- Each part outside the change is a box with its name and what it does. A part that can be the answer is a button. A tap locks that answer.
- Before the answer is locked, draw no line between the changed part and any other part. A line is a fact from the run.
- "Nobody" and "Don't know" are word cells under the parts.
- On a result, print the same picture with `fh-map--result`. Draw a solid arrow to a part whose old test fails (`is-ref is-fail`). Draw a dashed arrow to a part that uses the changed part and whose old tests pass (`is-ref`). A part with no use says "no use found".
- Mark the person's answer with the flag "your answer" (`is-said`).
- Put the map in a `fh-mapbox`. The box measures the width and chooses the layout.
- This question is designed and does not run yet. Say so wherever the map appears on the site.
