# Build step 2: the core loop in Claude Code

Part of `../PRODUCT.md` section 8. It follows `build-1.md`. This step builds the loop end to end for one agent and the clearest moments, in three parts that each ship:

- **2a. Revert test** with How sure, the fact line, the record and a minimal Room.
- **2b. Call it**, on the same runner.
- **2c. Brief**, which reuses the Revert test's check on a named done check.

`SKILLS.md` names these as the moments with the clearest feedback. The fourth it names, predict before running, was cut as an asked moment (`learning.md` section 13). 2a is specified in full. 2b and 2c are given as what they add.

The hook contract in sections 3 and 4 was checked against the Claude Code hooks reference and skills page (`code.claude.com/docs/en/hooks`, `hooks-guide` and `skills`, read on 2026-11-15, Claude Code 2.1.325). One thing was read from the reference and not yet seen in a live session: how the `Stop` line is drawn in the terminal (section 10, item 1 checks it).

---

## 1. What 2a delivers

A person runs `uvx firsthand init` inside Claude Code in a Python project with pytest. When the agent next finishes a change that adds or edits tests, one line asks which new test would still pass with the change undone. The person replies in chat or in the Room. The result shows what a real run found. On a high-stakes path the finding is printed as a fact even if nobody answers. Everything is recorded in `~/.firsthand/record`. Nothing is written to the project.

Out of scope for 2a: every other moment, reviews, drills, the phone, the inline card, the MCP server, model providers, focus skills and fading beyond the daily limit, other agents, other test runners than pytest and the generic fallback.

## 2. Package and commands

A Python package `firsthand/` at the repo root, with a `[project]` table added to `pyproject.toml` (name `firsthand`, Python 3.11 or later, no runtime dependencies, console script `firsthand = firsthand.cli:main`). Layout as in `architecture.md` section 1.3, with only these modules in 2a: `cli.py`, `daemon.py`, `hooks.py`, `adapters/claude_code.py`, `timeline.py`, `gitwatch.py`, `runner/snapshot.py`, `runner/scratch.py`, `runner/pytest_adapter.py`, `runner/generic_adapter.py`, `moments/revert_test.py`, `keys.py`, `record.py`, `room/`.

| Command | Does |
| :- | :- |
| `firsthand init` | Section 3 |
| `firsthand hook claude-code <Event>` | The dispatcher. Reads stdin, appends one spool line, starts the daemon if needed, prints the hook's JSON output if the daemon left one ready, exits |
| `firsthand daemon` | Internal. The background process |
| `firsthand room` | Opens the Room in the browser with a one-time URL. `--tty` prints the open question and reads an answer in the terminal |
| `firsthand answer <text>`, `firsthand skip` | Answer or skip the open question from a shell |
| `firsthand status` | The open question, today's count, the dial, the test command, whether the daemon runs |
| `firsthand journal`, `firsthand skills` | Text views |
| `firsthand quiet [session\|today\|here]`, `firsthand off`, `firsthand on` | Controls |
| `firsthand config test-command "<cmd>"`, `firsthand config high-stakes "<glob>"` | Project settings |
| `firsthand uninstall` | Restores backed-up files. Leaves the record |

## 3. `init` for Claude Code

1. Install the engine to `~/.firsthand/engine/<version>/` and resolve the absolute path of its `firsthand` executable.
2. Create `~/.firsthand/record` (`git init -q`, write `FORMAT` with `firsthand-record 1`), `~/.firsthand/run` (0700), `~/.firsthand/cache` (0700), `~/.config/firsthand/` with a chosen free port in `port`.
3. Show the files to be written and ask `Go ahead? [Y/n]`. Back up each file to `~/.config/firsthand/backups/<timestamp>/` first.
4. Merge into `~/.claude/settings.json`, keeping every existing entry:

```json
{
  "hooks": {
    "SessionStart":       [{"hooks": [{"type": "command", "timeout": 5, "command": "/abs/firsthand hook claude-code SessionStart"}]}],
    "UserPromptSubmit":   [{"hooks": [{"type": "command", "timeout": 5, "command": "/abs/firsthand hook claude-code UserPromptSubmit"}]}],
    "PreToolUse":         [{"matcher": "*", "hooks": [{"type": "command", "timeout": 5, "command": "/abs/firsthand hook claude-code PreToolUse"}]}],
    "PostToolUse":        [{"matcher": "*", "hooks": [{"type": "command", "timeout": 5, "command": "/abs/firsthand hook claude-code PostToolUse"}]}],
    "PostToolUseFailure": [{"matcher": "*", "hooks": [{"type": "command", "timeout": 5, "command": "/abs/firsthand hook claude-code PostToolUseFailure"}]}],
    "Stop":               [{"hooks": [{"type": "command", "timeout": 5, "command": "/abs/firsthand hook claude-code Stop"}]}]
  }
}
```

   Notes on this shape:

   - All six event names exist. Each event holds a list of matcher groups, and each group holds a `hooks` list of handlers.
   - `matcher` is optional. `"*"`, `""` or no matcher all mean every occurrence. On the three tool events it filters by tool name. `UserPromptSubmit` and `Stop` have no matcher support and always fire. On `SessionStart` a matcher would filter by how the session started (`startup`, `resume`, `clear`, `compact`, `fork`), so none is set.
   - `timeout` is in seconds. The default for a command hook is 600, lowered to 30 on `UserPromptSubmit`. A hook that is not `async` holds the agent until it exits, so 5 is set as a ceiling. A hook cancelled at its timeout has its output discarded and blocks nothing. `async: true` is not used: an async hook's `systemMessage` is not shown to the person.
   - With no `args` field the command string runs through `sh -c`, so `init` shell-quotes the absolute path.
   - `onFailure` is never set. Left unset, a hook that fails or cannot start is a non-blocking error.

5. Write the personal skill `~/.claude/skills/firsthand/SKILL.md`. The file is YAML frontmatter between `---` lines, then markdown. No frontmatter field is required: `name` defaults to the folder name, and `description` is what Claude Code uses to decide when to load the skill, so it is set (it is cut at 1,536 characters in the skill listing). `user-invocable: false` hides it from the `/` menu. The body says: print a Firsthand line unchanged, treat "skip" as final, never answer for the person, never read `~/.firsthand`. Claude Code watches `~/.claude/skills/`, so the skill loads without a restart. It is not read by cloud sessions.
6. Ask `Is this a work computer? [Y/n]` and store `config/work_computer.json`.
7. Find the test command: `[tool.pytest.ini_options]` or a `pytest.ini`, `tox.ini` or `conftest.py` gives `pytest -q`. Otherwise ask once. Store it in `projects/<project-id>.json`.
8. Print the install copy of `experience.md` section 3.1.

The history scan and the "What works here" note are added after 2a works end to end.

## 4. Events

**Mapping.** `SessionStart` to `session_start`, `UserPromptSubmit` to `prompt_submit`, `PreToolUse` to `before_tool`, `PostToolUse` to `after_tool`, `PostToolUseFailure` to `tool_failed`, `Stop` to `turn_end`.

`PostToolUse` fires only when a tool succeeds. A Bash command that exits non-zero fires `PostToolUseFailure` instead, so a failing test run arrives as `tool_failed` and a passing one as `after_tool`. `Stop` fires when the main agent finishes responding, not on a user interrupt and not on an API error. `UserPromptSubmit` also fires for prompts the person did not type (a scheduled task, a background subagent reporting back).

**Fields read from the hook's stdin** (one JSON object):

- Every event: `session_id`, `cwd`, `hook_event_name`. `agent_id` when present, which marks a call made inside a subagent.
- `SessionStart`: `source`.
- `UserPromptSubmit`: `prompt`.
- `PreToolUse`, `PostToolUse`, `PostToolUseFailure`: `tool_name`, `tool_use_id`, `tool_input.command` for Bash, `tool_input.file_path` for Edit and Write (always absolute).
- `PostToolUse` for Bash: `tool_response.stdout` and `tool_response.stderr`. `tool_response` is an object with `stdout`, `stderr`, `interrupted` and `isImage`. It has no exit code field: the event itself means the command exited 0, so `exit` is written as 0.
- `PostToolUseFailure`: `error`, a string. For Bash its first line is `Exit code N` and the rest is the command's stdout and stderr interleaved. Long output is cut in the middle by Claude Code. `exit` is parsed from the first line, and is null when that line is missing (the shell could not start). `is_interrupt` when present.
- `Stop`: nothing more. `last_assistant_message` is not read.

`transcript_path` is never read or stored.

**Spool line**, appended to `~/.firsthand/run/spool.jsonl` (0600):

```json
{"at": "2026-11-14T09:12:03Z", "agent": "claude-code", "session": "abc123", "cwd": "/home/sam/orbit-pay",
 "event": "after_tool", "tool": "shell", "command": "pytest -q", "exit": 0, "failing": [], "paths": []}
```

A failing run of the same command is `"event": "tool_failed"` with `"exit": 1` and the failing ids.

- `tool` is `edit` for Edit, Write and MultiEdit, `shell` for Bash, `ask` for AskUserQuestion, `plan` for ExitPlanMode and EnterPlanMode, else `other`. (The current reference lists Edit, Write, AskUserQuestion and ExitPlanMode. MultiEdit and EnterPlanMode are kept for older versions and cost nothing if they never arrive.)
- For a shell call whose command starts with the project's test command, the dispatcher parses failing test ids (lines matching `^FAILED (\S+)`) from `error` on `tool_failed`, or from `tool_response.stdout` on `after_tool`, and drops the output. Because Claude Code may cut a long `error` in the middle, the list can be incomplete. That is safe here: the exit code still says the run failed, and the revert check runs the tests itself.
- The prompt text is included on `prompt_submit` after the secret scan.

**Hook output.** The dispatcher always exits 0. It prints nothing on stdout or stderr, except:

- On `Stop`, when the daemon has a question or fact line ready for this session: one JSON object and nothing else on stdout, `{"systemMessage": "<the line>"}`. `systemMessage` is shown to the person and is not sent to the model. It does not continue the turn: at `Stop` only `decision: "block"`, exit code 2 and `hookSpecificOutput.additionalContext` do that, and none is ever used. Claude Code presents it as a warning message from the hook, so the line carries its own "Firsthand:" prefix and stays one line. The cap is 10,000 characters. The dispatcher waits for the daemon at most 300 ms. A line that is not ready is delivered at the next `Stop`, or through the Room.
- On `UserPromptSubmit`, when the prompt is exactly a reply word of the open question (`1` to `4`, `none`, `fails`, `passes`, `don't know`, `skip`): the result lines as plain text on stdout, after the prefix line `Firsthand result for the reply above. The firsthand skill prints these lines unchanged:`. Plain-text stdout on this event is added to the model's context next to the prompt, with no visible transcript entry and without blocking the prompt. `hookSpecificOutput.additionalContext` does the same and is not needed. The text must not start with `{`, or it is read as JSON. The prefix is a statement, not a command, because the reference warns that injected text written as an instruction can be treated as a prompt injection. The cap is 10,000 characters.
- Text meant for the agent only (the finding of section 7, the Brief question of 2c) goes out the same way on the next `UserPromptSubmit` of the session. It is never sent on `Stop`: context added at `Stop` makes the agent take another turn.
- Never `decision`, `permissionDecision`, `continue: false`, `hookSpecificOutput` on `Stop`, exit code 2 or any other non-zero exit code. Stdout on `SessionStart` is also added to the model's context, so nothing is printed there.

**Hook speed.** Every hook here runs synchronously, so the agent waits for the dispatcher to exit: before a tool call on `PreToolUse`, before the model sees the prompt on `UserPromptSubmit`, before the turn closes on `Stop`. The dispatcher therefore does only the spool append and, on `Stop` and `UserPromptSubmit`, the 300 ms wait. When it starts the daemon it detaches it (new session) and points the daemon's stdin, stdout and stderr at `/dev/null` or a log file. If the daemon kept the hook's stdout or stderr open, Claude Code would wait up to 10 seconds for the hook to finish.

## 5. Timeline and the done signal

Implemented as in `learning.md` section 3.3.

- A snapshot at every `prompt_submit` and `turn_end` (`architecture.md` section 7.1): a temporary `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` pointing at `~/.firsthand/cache/snapshots/<project-id>.git` with the project's object folder in `GIT_ALTERNATE_OBJECT_DIRECTORIES`, then `git add -A` and `git write-tree`.
- **Done signal:** `turn_end` where the tree hash differs from the previous `turn_end`, the last test command seen in the task exited 0 (or none was run), and no `ask` tool call is pending.
- **Task base:** the snapshot at the first `prompt_submit` after the previous done signal, commit (HEAD changed) or branch switch.
- **Test files:** paths matching `test_*.py`, `*_test.py` or under a `tests/` folder. Everything else in the diff is "the change".

## 6. The revert check

Triggered when a task's diff against its base has at least one changed non-test file and at least one added or edited test, at the earlier of: an `after_tool` test run that exits 0, or the done signal.

1. **Find the tests.** For each changed test file, list test functions with `ast`. A test is new if its node id is absent at the base, edited if its function source differs. Keep at most four, new ones first.
2. **Scratch copy** of the head snapshot under `~/.firsthand/run/scratch/<id>/` (0700), with `.claude/`, `.mcp.json`, `CLAUDE.md` and `AGENTS.md` removed. The project's virtualenv is found from `VIRTUAL_ENV` or `.venv` and its interpreter is used directly. It is not copied in 2a: the scratch copy is run with `PYTHONPATH` set to the scratch root so the scratch source wins. If the project is installed in editable mode into that virtualenv, the check ends as `check.unavailable` with reason "editable install", and the cached dependency copy of `architecture.md` section 7.2 lifts that later.
3. **Control.** Run the chosen tests in the scratch copy: `<python> -m pytest <ids> -q -p no:cacheprovider --junitxml=<scratch>/control.xml`, with the scrubbed environment. All must pass. If not: `check.unavailable`, reason "does not match here". Nothing is asked.
4. **Ask.** The question may be shown from this point.
5. **Undo the change.** For every non-test file in the diff: restore the base version, or delete it if it did not exist at the base.
6. **Run again** with `--junitxml=<scratch>/undone.xml`.
7. **Classify each test** from the XML: no `failure` or `error` child means **still passes**. A `failure` whose type is `AssertionError`, or pytest's `Failed`, means **fails on its assertion**. Anything else (an `error` child, or a failure of another exception type such as `ImportError` or `AttributeError`) means **cannot run**.
8. Delete the scratch folder. Time limit: 2 minutes for the whole check.

The generic adapter, for a non-pytest test command, runs the command once per changed test file and classifies by exit code only: **passes** or **does not pass**. Results say "by exit code".

**Key file**, `~/.firsthand/run/keys/<moment-id>.json` (0600), deleted after scoring:

```json
{"moment": "01JC8Y2F...", "tests": [
  {"id": "tests/test_refunds.py::test_same_key_refunds_once", "result": "fails_on_assertion",
   "assert_line": 23, "assert_text": "assert len(ledger.refunds(charge)) == 1"},
  {"id": "tests/test_refunds.py::test_refund_response_is_stable", "result": "still_passes",
   "assert_line": 41, "assert_text": "assert resp.status_code == 200"}]}
```

`assert_line` and `assert_text` come from the `ast` pass and feed the card's evidence and the "what would have shown it" line.

## 7. Asking, answering, scoring

- **Gates:** the dial is Standard or Deep, not quiet, no pressure signal (branch starts with `hotfix`, or the task's prompt holds "urgent" or "prod is down"), fewer than the daily limit asked today (default 1), this change not yet asked, not the first prompt of the day.
- **The line** and the card are the copy in `experience.md` sections 5.1 and 6.2. With one test the picks are `fails`, `passes`, `don't know`. With several: the numbers, `none`, `don't know`.
- **Close:** the next `prompt_submit` that is not a reply word closes the question unanswered.
- **Score:** with several tests, a match if the picked test's result is `still_passes`, or the pick is `none` and no test is. With one test, a match if `fails` meets `fails_on_assertion` or `cannot_run`, or `passes` meets `still_passes`. Outcome kind is `uncommon` when any test still passes. `don't know` writes `call.sealed` and no `call.scored`.
- **How sure:** in the Room, one optional row after the lock. In chat, the reply may carry it: `2 sure`, `none not sure`.
- **Finding to the agent:** when any test still passes or cannot run, one line is queued for the next `UserPromptSubmit` output of the session (section 4): `Firsthand finding: <test id> passes with the change undone.`
- **Fact line:** when a test still passes and any changed file matches a high-stakes glob, the line is printed at the next `Stop` whether or not a question is open, and an open question closes as `shown-first`.
- **Notes only** and **quiet:** the check still runs and writes `note.posted`.

**Events written** (format in `architecture.md` section 2), in order for one answered question: `task.started`, `task.event` (each test run, each done signal), `moment.offered`, `call.sealed`, `call.confidence` (if tapped), `check.ran`, `call.scored`. Otherwise `moment.skipped` or `moment.closed`, and `note.posted` for a finding. One git commit in the record per question.

## 8. The minimal Room

The standard-library server from `skills/learning-while-building/scripts/room.py`, moved into `firsthand/room/`, bound to `127.0.0.1:<port>`, with the session and request checks of `architecture.md` section 8.1. One HTML page built from `design/learning-experience/assets/room.css`. Screens in 2a:

- **Inbox:** Now, Notes, Results, and the line "Asked today: 0 of 1."
- **Question card** and **Result**, as `experience.md` sections 7.3 and 7.4, with **More**, **Wrong start** and **This result looks wrong** (which reruns the check once).
- **Journal:** every call and note.
- **Skills:** the Verification row with counts and the fixed-answer sentence. No level logic yet beyond "Too few calls" and "Shown".
- **Settings:** the dial, the daily limit, the test command, high-stakes globs, "Send findings to my agent".

Routes: `GET /`, `GET /q/<id>`, `GET /r/<id>`, `GET /api/inbox`, `GET /api/q/<id>`, `GET /api/journal`, `GET /api/events`, `POST /api/q/<id>/lock`, `/skip`, `/confidence`, `/wrong-start`, `/dispute`, `POST /api/settings`.

## 9. Tests

Fixture projects under `tests/fixtures/`, each a small git repo built by the test, with a base commit and an uncommitted change:

| Fixture | The change | Expected key |
| :- | :- | :- |
| `proves` | A function fixed, one new test that asserts the fix | `fails_on_assertion` |
| `passes_anyway` | A function fixed, one new test that asserts only the return type | `still_passes` |
| `needs_new_code` | A new function and a test that imports it | `cannot_run` |
| `mixed3` | Three new tests, one of each kind | One of each |
| `edited_test` | An existing test's assertion changed | The edited test is found. `fails_on_assertion` |
| `control_fails` | A new test that fails on the head tree | `check.unavailable`. Nothing asked |
| `no_tests` | Source changed, no test touched | No candidate |
| `high_stakes` | As `passes_anyway`, under a path marked high stakes | A fact line with no answer given |

Each test replays a recorded sequence of spool lines against a daemon with a temporary home, then asserts on: the events written, the line produced for the `Stop` hook, the score for a given reply, and that the fixture repo's working tree, index, refs and object count are byte-identical before and after. One test asserts that no hook output ever contains `decision` or a result before a lock. One test starts with no daemon and asserts the first `prompt_submit` is in the spool and sets the base.

## 10. Done means

1. In a real Claude Code session on a pytest project, finishing a change with a new test produces the question line once, at the turn end, with no extra model turn.
2. Replying `2`, answering in the Room, and running `firsthand answer 2` each lock the same question and produce the same score.
3. The result names the test, says what the run found, and on a miss shows the assertion line.
4. A new test that passes without the change on a high-stakes path is printed as a fact with nobody answering.
5. A second finished change the same day asks nothing and still records a note.
6. `skip`, `quiet`, `firsthand off` and the next prompt all end a question with no follow-up.
7. With the daemon killed, the next prompt restarts it and no event is lost.
8. After a week of use, `git -C <project> status` shows nothing from Firsthand, and `~/.firsthand/record` holds one commit per question.
9. `firsthand uninstall` restores `settings.json` byte for byte.
10. All fixture tests pass in CI.

## 11. 2b and 2c

**2b. Call it** adds: the trigger (a `prompt_submit` matching a traceback or `FAILED` pattern, or a `turn_end` whose last test run failed on a test that exists at the base and is unedited); snapshots at the red and green runs; the pick card built from files named in the failing output and files changed in the task; closing the card at the first `after_tool` edit to a non-test file; the fix location (files changed between the red and green snapshots); the symptom-pattern scan (added `sleep`, added bare or broad `except`, removed or loosened `assert`, added `skip`); the undo-the-fix run; `episode.red` and `episode.green` events; the Waiting group in the Inbox. Fixtures: a causal fix, a fix in an unnamed file, a sleep patch, a test that never goes green.

**2c. Brief** adds: the trigger at `prompt_submit` plus the first edits (two or more path categories, no test id, test path or test command in the prompt, not the first prompt of the day); the one-line question delivered as added context on the next `UserPromptSubmit` output (section 4); passing the done line to the agent; finding the first test added in the task; the "Is this your check?" confirm; the Revert test's check run on that one test; correction prompts and ask-tool questions listed on the result. Fixtures: a check that tells done from not done, one that passes anyway, a task where no test was written.

After 2c the order continues in `../PRODUCT.md` section 8.
