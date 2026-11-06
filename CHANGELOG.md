# Changelog

All notable changes to this plugin. Versions follow the plugin manifest.

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
