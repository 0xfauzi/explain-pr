The route of a failure, drawn. Use it for Call it: the question and the result.

- The first box is the test. It is not an answer.
- Each file in the trace is one stop, in the order of the trace. The last stop has the red mark and the note "The failure shows here".
- A file that can be the answer is a button. A tap locks that answer.
- A file that is an answer but is not in the trace has a dashed outline. It goes under the path with the line "Not on the path of the failure."
- "Somewhere else" and "Don't know" are word cells under the picture.
- Use `fh-path--flow` (boxes and arrows across the page) only when the top row has three boxes. In all other cases the path goes down the page as a line with a square at each stop.
- Put the path in a `fh-pathbox`. The box measures the width and chooses the layout.
- On a result, print the same picture again with `fh-path--result`. Mark the person's answer with the flag "your answer" and the fix with the flag "the fix is here".
- Do not show why a file is in the list before the answer is locked.
