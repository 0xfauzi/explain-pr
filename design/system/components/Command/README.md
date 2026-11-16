A command to copy, with what it needs and what it does. Site only.

- `fh-cmd` is a `code` line with a Copy button. The `$` prompt sign is drawn by the style and is not part of the text that is copied. A wrapped line hangs under its first word, not under the sign.
- A `fh-cmd__cap` line above it says where to type it on the left and what kind of command it is on the right, in `fact-sm`.
- Mark the places a long command may break with `<wbr>`, after a `/`. Never let it break inside a word.
- `fh-cmd--stack` puts the Copy button under the command as a bar. Use it where the column is narrower than the command, as in the first screen. Below 600px every command is stacked.
- `fh-cmd--chat` is for commands typed inside the agent: no prompt sign, one command a line.
- Copy changes its label to "Copied" for two seconds and keeps its width.
- What the command needs is a `fh-status` list with leaders. What it does is `fh-does`: a numbered list in the order it happens, sentences in `ui-md`, paths in `fact`, the numbers in `fact-sm` `ink-3`.
- Print only a command that has been run and seen to work. If the published command differs from today's, show today's and name the later one as a fact.
