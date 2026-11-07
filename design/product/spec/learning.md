# Spec: the learning loop

Part of `../PRODUCT.md` (section 4). Evidence codes L1 to L19 are the design rules in `../research/learning-science.md` Part A.3. Task and construct codes (C1 to C6, G1 to G5) are from `../research/evidence.md`.

---

## 1. Constructs

The product measures six constructs separately and never combines them (evidence B.1; Lister 2004 and Fitzgerald 2008 show the skills come apart, evidence A.2 items 5 and 6).

| Code | Construct | Main moves and drills |
| :- | :- | :- |
| C1 | Code reading | Predict, Trace, Check |
| C2 | Debugging | Call it, Replay, Checkup seeded bug |
| C3 | Design judgment | Your line (at Deep), design-call reviews |
| C4 | Explaining a change | Explain back, PR walkthrough |
| C5 | Transfer | Applied-level items, Compare, Checkup task |
| C6 | Calibration | Confidence on every answer |

A construct with no recent evidence shows "no evidence yet", not a level.

---

## 2. Moves in the build

### 2.1 Predict

- Trigger: before a step whose result the user can reason about (test run, migration, query plan), on an idea at Not yet or Seen, within the moment cap.
- The observable must be deterministic. Timing, randomness and network make the key unstable (earlier critique M1), so the engine refuses to offer predictions on steps it marks non-deterministic.
- Closed against the real outcome with the gap at `path:line`. Never graded, never moves a level. It is recorded for calibration only.
- Copy has no verdict word (see `experience.md` section 3.2).

### 2.2 Call it

- Trigger: a test or build fails, and either the user's C2 level is below Applied, or their delegation rate is above the threshold. Delegation rate: the share of the last 10 failures in the user's sessions that the agent diagnosed with no user hypothesis. The window and threshold are design defaults, needs to be measured.
- The agent keeps diagnosing in parallel. It holds back only its conclusion until one of: the user answers, the user skips, or the agent's own diagnosis is ready and the user has not started typing. The agent never waits idle.
- The user gives a cause and the first check they would run.
- Grading is process first (evidence C.1, "graded on whether the check would discriminate"):
  - Point 1: the check distinguishes the user's hypothesis from at least one plausible alternative. Graded by a blind model against a sealed list of plausible causes written in a separate context before the question.
  - Point 2: the check was named before any fix was shown. Recorded by the engine from event order.
  - Point 3: the cause matches the actual cause, once known. Recorded, but a lucky right cause without points 1 and 2 scores below a sound process with a wrong cause.
- The engine runs the user's check first where it is executable, then the agent's.

### 2.3 Your line

- Trigger: the agent is about to write the one line (later a function, then a design choice) that carries an idea new to the user. At most one per task. Not under pressure or quiet.
- The agent calls `line open` with: file, marker location, idea ID, and the sealed check (which tests must pass). The engine returns the marker text.
- Marker rules: it states the goal in outcome terms and names the test. It never describes the computation. The engine checks marker text against a short rule set (no operators, no formula words such as "multiply", "add", "base times"), and rejects a marker that fails, asking the agent to restate the goal.
- Example good marker: `FIRSTHAND(you): the delay before retry n. Test: test_backoff.py::test_delays.` Example rejected marker: `compute base * 2**n with jitter`.
- Graded by the project's tests. Same session caps at Seen. Signals: first-try pass, hints used, `line.survived` at next commit and at 30 days.
- Handback: "write it" at any time; automatic under pressure, on quiet branches, or on a failing deploy.
- Growth: at Deep and as the level rises, the gap grows from a line to a function to a design choice (fading, L5).
- Team nominations: a guide can nominate "lines worth writing by hand once" (`teams.md` section 2).

### 2.4 Explain back

- Trigger: after a step passes, at most once per task the user chose to learn from ("teach me this one", or Standard and Deep defaults on new ideas).
- Two or three sentences. Blind model grader against a sealed rubric of binary points. Same session caps at Seen. An echo flag when quoted spans nearly copy the agent's own words: the point counts, the level cannot rise.

### 2.5 "Later" items from fast work

When the engine sees rapid delegation (short imperative prompts, repeated quick turns, the user editing while the agent works; modes from Barke et al., https://arxiv.org/abs/2206.15000), it asks nothing in the moment and writes one `item.queued` event from the episode: an idea from the diff, to be asked as a delayed review. At most one per session. This replaces the earlier "stay quiet in acceleration mode" rule.

---

## 3. Drills

All drills: opt-in, in the agent's chat or terminal, inside the 3-a-day cap when due, never in the same week as the source material, keys sealed before offering.

### 3.1 Trace

- Source: code the agent wrote in the last 7 days in added repos (from commits with agent co-author trailers, or from engine-recorded agent edits).
- The engine picks a pure function or a small deterministic block, picks an input, runs it in a scratch copy, and seals the output.
- The user predicts the output. Graded by comparison. This is the default first-session drill.
- Item family: the same function with a different input is a surface variant; a different function using the same idea is a new instance.

### 3.2 Check

- Source: past agent-written diffs in added repos. A diff is "defective" if a later commit fixed lines it introduced (detected by blame and a fix-style message or a failing-then-passing test). A diff is "clean" if no later commit changed its lines within 60 days (design default). Clean labels are uncertain: a defect may simply not have been found. The map says so.
- The user lists defects with severity, or says "clean".
- Graded by precision and recall against the sealed defect list. Clean diffs make "always find something" cost points.
- No seeded bugs in user code, ever. A seeded variant exists later only in an engine-created throwaway copy of a different repo.

### 3.3 Replay

- Source: commits where a test went from failing on the parent to passing on the fix.
- Build steps (from `../concepts/companion.md` section 4.3): find candidates by tests touched; in a throwaway worktree, check out the parent and run only that test with a time limit; confirm it fails, and passes on the fix; seal the key (cause, location, principle as binary points, plus a list of plausible causes) in a separate context.
- Safety: runs only the project's own test command, in a worktree outside the repo, with network off where the OS allows, under a time limit. Historical code is the user's own code, but it may still run arbitrary scripts, so the user enables Replay per repo with a plain warning.
- Gated by E2: ships only for languages and repos that pass the yield rule.
- User flow: hypothesis, first check, then fix in the scratch copy. Graded by process (as Call it) then the commit's own test.
- States: "Checking this bug still reproduces (12s). Say 'cancel' to stop." If not reproducible: dropped, a Trace drill offered, nothing recorded against the user.

### 3.4 Compare

- Source: the same catalog idea met in two projects.
- "You used an idempotency key in payments. Where would the same idea apply in the job queue, and what is one difference?" Topic name hidden in the question.
- Graded by sealed rubric, blind grader. Construct C5. Analogical encoding is the strongest transfer lever in the evidence (Gentner et al., research/learning-science.md A.1 item 7).

### 3.5 Explainers after an attempt

After an attempt locks, the user can ask for an explainer from their own code, with `path:line` and the principle named. Never first. Viewing counts as Seen. In v1 this is plain text in the agent; a designed page is a v2 option.

### 3.6 Growth areas

The user can pick up to three growth areas (ideas or constructs). Only those get extra drills beyond what is due. Autonomy first (L15). Default: none, and drills follow what is due.

---

## 4. Items, families and distance

Every review, drill and unseen question comes from an item family (evidence C.2). The sealing step records:

| Field | Meaning |
| :- | :- |
| `family` | The deep structure, one sentence |
| `surface` | Domain object, code shape, failure mode |
| `distance` | Which earlier items and feedback it differs from, and how: same code, same project new code, other project, other domain |
| `topic_name_shown` | Whether the idea's name appears. Transfer items: never |
| `difficulty` | Author tag, later replaced by an estimate from outcomes |
| `source` | practice, unseen (human-written), checkup, guide |
| `seal` | separate context, or asking context |

Rules:

- An item with distance "same code" can earn at most Recalled.
- Applied needs distance "same project new code" or further, and the topic name hidden.
- Held needs an unseen-question item at a longer gap, plus one other source (practice family, linked field evidence, or Checkup).

---

## 5. Levels

Ladder and caps: `../PRODUCT.md` section 4.9. Additional rules:

- Only delayed items move levels. The delay at which an item counts starts at 7 days (`DURABLE_AFTER_DAYS` in the current `record.py`). Needs to be measured.
- Levels move down on a miss at any delayed item. Best level is kept and shown.
- Caps that apply regardless of correctness: self-marked; asking-context seal; agent-relayed answer; task type below the grader agreement gate; grader disagreement. Each of these records the attempt and its correctness for the user, but holds the level.
- Imported legacy records cap at Recalled.
- The map shows, in one line, that unaided results in a personal tool are self-attested.

---

## 6. Reviews and scheduling

- Up to 3 due a day, offered after the first prompt of a session has been handled, default "later". Also through the reminder, or `firsthand review`.
- Free recall in a new instance: no code, no old answer, no options until the user commits (L7).
- Interleaving: easily confused ideas from the catalog (`confusions` field) are scheduled near each other, names hidden until commit (L9).
- Intervals start from the current engine: 3, 7, 21, 60, 180 days after success, 1 day after a miss (`record.py`). Derived state is a fold over events, so FSRS or another scheduler can replace it by replaying the log [unverified until tested].
- After a gap: at most 3, rest spread, no backlog count.
- Sure misses are listed first.

---

## 7. The unseen-question bank and the Checkup

### 7.1 Unseen questions (the audit bank)

- Written by contracted engineers, per catalog idea, as item families with transfer variants. Two writers review each item. Writers never see user data.
- Shipped sealed and encrypted; decrypted only in the engine process when displayed; never passed to the agent's context.
- Served only on surfaces where the engine renders directly: the terminal CLI, and native ask forms verified not to pass content to the model [unverified per host]. On other surfaces they wait.
- Share of review slots: starts at one slot in three on days with 3 due (design default, needs to be measured).
- The map reports the gap between practised and unseen results per construct, with item counts and an uncertainty band. Below the minimum count: "too few answers to tell".
- Stated limit: a determined user can read the package. The design records honesty, it cannot force it.

### 7.2 The Checkup

- User-started, at most monthly, never due, never reminded.
- Contents: one small task in a real public repo the user has never opened, pinned to a commit, in a throwaway clone, needing an idea the user has met elsewhere, no topic name, graded by tests plus an optional blind human review in study settings (G2); one seeded bug in that throwaway clone to localise (G3); two agent-style diffs to check, one clean (G4).
- Written by people. Sealed. Never used for practice. Retired after use by that user.
- Result: its own line on the map, by construct, with a count.

---

## 8. Dose and its test

Design targets in `../PRODUCT.md` section 4.11. E1 measures for each user per week: generation reps, retrieval reps, diagnosis reps, check reps, and the share of each that was unaided. E7 then tests whether that dose moves delayed outcomes. If it does not, the response order is: (1) offer more user-started drills, (2) raise the share of diagnosis and check drills in due slots, (3) never raise interruptions in the build.

---

## 9. Field evidence

`firsthand field <ref> "<what I did>"`, where ref is a commit or PR URL. The engine checks authorship and the absence of agent co-author trailers. The user tags constructs. Shown in its own list. Can be one source for Held. Within-person only, never compared across people (evidence H.2 G5).
