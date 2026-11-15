# Changelog

All notable changes to this plugin. Versions follow the plugin manifest.

## Unreleased: Firsthand preview

- Licence changed from MIT to Apache-2.0. Versions already published under MIT stay under MIT.

`firsthand/` is a separate tool from the skill, not yet published. See the
README section "Firsthand preview".

### Added
- Revert test (build step 2a): when Claude Code finishes a change with new or
  edited tests, one question asks which test would still pass with the change
  undone, checked by undoing the change in a scratch copy and running the tests.
  With How sure, the fact line for high-stakes paths and the Room.
- Call it (build step 2b): on a pasted failure, or a turn that ends with an
  existing test failing, one question asks where the cause is before a fix
  exists. Checked by where the fix landed and by undoing the fix. Symptom
  patches (a sleep, a broad `except`, a skip, a loosened assertion) are not
  scored. A Waiting group in the Room's Inbox.
- Brief (build step 2c): at the start of a task that touches two or more kinds
  of file and names no test, one question asks for a check that fails now and
  will pass when the task is done. The line goes to the agent. At the done
  signal the first test added is shown back ("Is this your check?") and run
  with the change and with the change undone. The result lists correction
  prompts sent after the agent finished and questions the agent asked.
- `firsthand status`, `journal` and `skills` show all three. Skills has rows for
  Verification, Debugging and diagnosis, and Framing the problem and the brief.

## 0.6.0 (2026-11-15)

### Changed
- The record no longer lives in the project. Earlier versions kept it in
  `.learning/` and said to commit it, but that folder holds every answer the
  learner got wrong, and in a shared repository anyone with access, or with a
  clone or fork, can read it. The record is now a local git repo at
  `~/.learning-while-building/` (or `$LEARNING_HOME`), one folder per project,
  with no remote. Each write is committed there. Nothing is written to the
  project and nothing tells you to commit.
- The record directory is chosen in this order: `--dir`, `$LEARNING_DIR`, an
  existing `./.learning` record while the home has none for the project, then
  the home folder for the project.

### Added
- `move`: run from the project root to copy an existing `./.learning` record to
  the home record. It checks the copy, changes nothing in the project, and
  prints how to remove the old folder and what that does not undo, read from
  the project's git history and remotes. Until the record is moved, every
  writing command ends with a line saying it is inside the project.
- `export` and `import-bundle`: a cloud session prints its record as one JSON
  document, and the learner merges it into the record on their own machine.
  `init` in a cloud session says to do this.
- `where`: prints the record directory in use and which rule chose it.

### Removed
- The branch note after writes, and the instruction to commit and push the
  record.

## 0.5.0 (2026-11-06)

### Added
- Questions that don't block the build. `post` leaves a question for the
  learner; `inbox` and `grade --feedback` grade what is waiting and store the
  feedback so it can be read outside chat.
- `questions` and `answer`, so the learner can answer from a terminal with no
  model involved.
- The learning room page (`assets/room.html`). `serve` runs it on 127.0.0.1
  using only the standard library; `room-push` and `room-pull` sync it when a
  harness can host it privately, where it grades answers on the spot.
- A test suite (`tests/`) and a CI workflow running it on Python 3.10 and 3.14.

### Changed
- The minimum supported Python is now 3.10. Python 3.9 is past its end of
  life and GitHub no longer provides it for current runners, so it can no
  longer be tested in CI.
- Script paths no longer depend on Claude Code: `<skill>/scripts/...` replaces
  `${CLAUDE_SKILL_DIR}`.

### Fixed
- Two answers to the same question sent at the same moment could both be
  saved. The room server now serialises answer writes.
- `room-pull` reported only the last change when a document brought both an
  answer and a grade.

## 0.4.0 (2026-11-06)

### Changed
- Practice sends up to three independent review questions in one message and
  grades them in one reply (`ask --batch`), and suggests a fresh session.
  Measured on one comparison: 11 model requests instead of 21, about 30% fewer
  weighted tokens.
- Explainer pages are built only on request or after two failed chat attempts.
- `map` shows only topics that are not holding by default; `--topic` and
  `--all` give detail.
- `SKILL.md` routes to per-mode reference files.

## 0.3.0 (2026-11-01)

### Added
- `map` separates the highest level ever demonstrated from current evidence.
- Field work counts only with an inspected artifact (`--evidence`); without one
  it is kept as a self-report.
- The Human-Outward writing style, restored and applied to all learner-facing
  text.

### Changed
- One file per topic and per attempt, with collision-resistant ids, so records
  from separate sessions merge cleanly. `migrate` converts 0.2 records.
- Repair drills never force-delete the learner's work.

## 0.2.0 (2026-11-01)

### Changed
- Replaced `explain-pr` with `learning-while-building`: the learner attempts,
  diagnoses and explains first, answers are graded against a rubric fixed
  before the question, and topics return on a spaced schedule.

### Added
- Interactive explainer pages that reveal nothing until the learner commits an
  answer, with a checker that drives them in a headless browser.

## 0.1.0 (2026-08-19)

- `explain-pr`: a skill that turned a pull request into a lesson, with the
  Human-Outward style and prose checkers. Retired in 0.2.0; it remains in the
  git history.
