The states of a Skill row that the Skill card does not show, and the key that opens the Skills page.

- **The key** (`fh-key`) draws each kind of cell at 14px beside what it means. It replaces a paragraph of legend. It sits once, above the ledger.
- **Too few calls.** The level reads "Too few calls" then the count in `call`: "1 of 2". The count is days with a matched call, and Shown needs 2. The tracks still show every call.
- **No level** (the Brief). There is no easy answer to a made check, so there is one track, one figure and no catch marks. The level reads "No level yet" in `ink-3` (`fh-level--none`), and the product's sentence explains why, in `ui`, under the tracks.
- **Only scored calls get a cell**, so the cells always add up to the figures beside them. Don't know, skipped and not scored calls are counted in the `fh-skill__counts` line and nowhere else. The dashed cell (`you none`) is kept in the stylesheet for a later build and is not used by the Room.
- `fh-skill__counts` is one `fact` line under the tracks: asked, answered, don't know, skipped, and how old the newest call is.
- A track shows the newest 24 calls. With more, say so under it in `fh-track__more`: "newest 24 of 31". The figures always count every call.
