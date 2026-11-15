# Build step 1: move the existing skill's record out of the project

Part of `../PRODUCT.md` section 8. This step changes only the existing skill in `skills/learning-while-building/`. It ships on its own, before any Firsthand code exists.

**The problem.** The skill tells people to commit `.learning/` to their project repo (`SKILL.md` line 103, `README.md` line 26, the last line `init` prints). That folder holds every answer the person got wrong. In a shared repo, teammates and anyone with the remote can read it. Founder decision: the record lives in a local git repo outside any project, with no remote unless the person asks.

**The change in one line.** The record's default home becomes a git repo in the person's home folder, the skill stops saying "commit", and existing users get one command that moves their record and tells them the truth about history.

---

## 1. Where the record lives

```
~/.learning-while-building/              a git repo, created by init, no remote
  FORMAT                                 "learning-record 2"
  projects/
    <project-key>/                       what .learning/ held before
      dimensions.json
      topics/<id>.json
      attempts/<id>.json
      explainers/<topic-id>.html
```

- **Home.** `$LEARNING_HOME`, else `~/.learning-while-building`. Created with mode 0700.
- **Project key.** `<slug>-<8 hex>`. The slug is the git top-level folder name, lower case, with every run of characters outside `a-z0-9` replaced by `-`. The hex is the first 8 characters of the SHA-256 of the root commit hash (`git rev-list --max-parents=0 HEAD`, last line). Clones and worktrees of one repo share a key. Outside a git repo, or with no commits, the hash is of the resolved absolute path. A record started before the repo's first commit keeps its path-keyed folder: while the commit key's folder holds no record and the path key's folder does, the path key's folder is used.
- **Resolution order** for the record directory, in `record.data_dir()`:
  1. `--dir`
  2. `$LEARNING_DIR`
  3. `./.learning`, if it already holds a record (`dimensions.json` or `topics.json`). Existing users keep working.
  4. `<home>/projects/<project-key>`
- **Legacy notice.** When rule 3 is used, every command that writes ends with one line: `This record is inside your project. Run "learning.py move" to move it out.`

## 2. Commands

All commands keep their current arguments. Changes and additions:

| Command | Behaviour |
| :- | :- |
| `init [--dimensions a,b]` | Creates the home repo if missing (`git init -q`, write `FORMAT`). Creates the project folder. Prints `Created <path>. It is outside your project. There is nothing to commit in your project.` The line "Commit and push this directory" is removed |
| every writing command (`topic add`, `topic add-dimension`, `topic retire`, `ask`, `grade`, `import`, `post`, `answer`, `migrate`, the room's writes) | After the write, if the record directory is inside the home repo: `git -C <home> add -A` and `git -C <home> -c user.name=learning -c user.email=learning@localhost commit -q -m "<command> <topic or id>"`. If git is missing or the commit fails, the write still succeeds and nothing is printed. `branch_note()` is deleted along with its three call sites |
| `move` (new) | Section 3 |
| `export` (new) | Prints the record as one JSON document on stdout (section 4) |
| `import-bundle FILE` (new) | Merges an exported document into the record. `-` reads stdin |
| `where` (new) | Prints the resolved record directory and which rule chose it |

`room.py` calls the same `data_dir()` and the same commit helper, so the learning room page follows without other changes.

## 3. `move`: for people who already committed `.learning/`

Run from the project root.

1. Stop with a clear message if `./.learning` holds no record, or if the target folder already holds one (`A record for this project already exists at <path>. Nothing was changed.`).
2. Copy `./.learning` to `<home>/projects/<project-key>`. Run the existing `check` on the copy. If it reports a problem, delete the copy and stop.
3. Commit in the home repo.
4. Change nothing in the project. Print what was done and what the person can do next. The text depends on three facts read from git: whether `.learning` was ever committed (`git log --oneline -1 -- .learning`), whether the repo has a remote (`git remote`), and whether `.learning` is still tracked (`git ls-files .learning`).

```
Moved 14 topics and 52 attempts to ~/.learning-while-building/projects/orbit-pay-3b9f52c1
From now on the record is read from there.

The old folder is still in your project. To remove it:
  git rm -r --cached .learning
  rm -rf .learning
  git commit -m "Remove learning record"

That removes it from now on. It does not remove it from history.
.learning/ was committed 31 times and this repo has a remote (origin),
so copies exist in history, on the remote, and in any clone or fork.
If you own this repo and want it gone from history:
  git filter-repo --invert-paths --path .learning
  then force-push, and ask every collaborator to clone again.
If you do not own it, the owner has to do this. Until then the old answers stay readable there.
```

- Never committed: the history paragraph is replaced by `It was never committed, so no copy exists in git.` and the first command is just `rm -rf .learning`.
- The skill tells the agent to show this text unchanged and to run none of the project commands unless the person asks.

## 4. Cloud sessions: export and import, no carry branch

A cloud session's container is thrown away, which is why the skill used to say "commit". The replacement is an explicit import step.

- A cloud session starts with an empty home, so no reviews are due there. `init` detects it (`CLAUDE_CODE_REMOTE=true`) and adds one line: `This is a cloud session. Its record is lost when the session ends. Before you finish, run "learning.py export" and keep the output.`
- `export` prints:

```json
{
  "format": "learning-bundle 1",
  "project_key": "orbit-pay-3b9f52c1",
  "exported_at": "2026-11-15T10:02:00Z",
  "dimensions": ["design", "data", "debugging"],
  "topics": {"idempotency-keys": {"...": "the topic file as stored"}},
  "attempts": {"20261115T100100-a1b2": {"...": "the attempt file as stored"}}
}
```

- `import-bundle` at home: dimensions are unioned. A topic id that already exists is kept as it is at home. An attempt id that already exists is skipped. It prints `Imported 2 topics and 5 attempts. Skipped 1 already recorded.` A bundle whose `format` is not `learning-bundle 1`, or that fails the same field checks `check` runs, is refused whole.
- The skill's end-of-session text in a cloud session: show the export block and say `Paste this into "learning.py import-bundle -" on your own machine.`

## 5. Files to change

| File | Change |
| :- | :- |
| `skills/learning-while-building/scripts/record.py` | `home_dir()`, `project_key()`, new `data_dir()` order, `commit_home(message)`, `is_legacy(root)`. Module docstring paths updated |
| `skills/learning-while-building/scripts/learning.py` | `cmd_init` text. Delete `branch_note`. Call `commit_home` after each write. Add `cmd_move`, `cmd_export`, `cmd_import_bundle`, `cmd_where` and their parsers. `--dir` help text |
| `skills/learning-while-building/scripts/room.py` | Call `commit_home` after each write |
| `skills/learning-while-building/SKILL.md` | Rewrite "Set up the record" (lines 95 to 108): no "commit `.learning/`". New text: the record is outside the project, nothing is committed to the project, run `move` if `.learning/` exists. Replace "Records across sessions" (lines 110 to 116) with the cloud export text. Script reference: default for `--dir`, the four new commands |
| `skills/learning-while-building/references/explainers.md` | Lines 66 and 289: save under `<record>/explainers/`, found with `learning.py where`. Drop "so it is committed with the record" |
| `skills/learning-while-building/references/questions.md` | Line 61: the attempts live in the record directory, not `.learning/attempts.jsonl` |
| `README.md` | Line 26: "The first run creates a record in `~/.learning-while-building/`, outside your repository. Nothing is added to your project." Add a short "If you used an earlier version" section pointing at `move` |
| `docs/index.html` | Line 244: "plain files in your repository" becomes "plain files in a folder outside your repository" |
| `CHANGELOG.md`, `.claude-plugin/plugin.json` | Version 0.6.0. The changelog entry leads with the privacy reason and the `move` command |
| `tests/test_learning.py` | Section 6 |

## 6. Tests

Added to `tests/test_learning.py`, using a temporary `LEARNING_HOME` and a temporary git repo as the project.

1. `init` with no `--dir` creates `<home>/projects/<key>/dimensions.json`, creates nothing under the project, and its output does not contain the word "commit" followed by "this directory".
2. Two clones of one fixture repo resolve to the same project key. Two unrelated repos with the same folder name resolve to different keys.
3. After `topic add` and `ask`, `git -C <home> log --oneline` has one commit per write and `git -C <project> status --porcelain` is empty.
4. With an existing `./.learning` record and no flags, commands read it and print the legacy notice.
5. `move` copies the record, leaves `./.learning` and the project's git state untouched, and prints the "committed N times" paragraph for a repo where it was committed and the "never committed" line where it was not.
6. `move` refuses when the target already holds a record.
7. `export` then `import-bundle` into an empty home reproduces the record. Importing twice adds nothing the second time. A bundle with a wrong `format` is refused and nothing is written.
8. The existing tests pass unchanged, since they all pass `--dir`.

## 7. Done means

- `grep -rn "commit" skills/learning-while-building/SKILL.md README.md` finds no instruction to commit the record.
- A fresh install in a project writes nothing inside the project: `git status --porcelain` is empty after `init`, `ask` and `grade`.
- An existing user with a committed `.learning/` runs one command, keeps every topic and attempt, and is shown, in plain words, what removing the folder does and does not undo.
- A cloud session ends with an export block, and that block imports at home.
- `python -m unittest discover -s tests -v` and the repo's pre-commit checks pass.
- Version 0.6.0 is tagged with a changelog entry.

What this step does not do: rename anything to Firsthand, add hooks, or change how questions are asked. Those start in `build-2.md`. Firsthand's later `import-lwb` reads from `~/.learning-while-building/` (`architecture.md` section 12).
