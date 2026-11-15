# Build step 2a: the module contract

Part of `../PRODUCT.md` section 8. It turns `build-2.md` (2a only) into a contract that three engineers can build against in parallel: who owns each file, every public signature, every on-disk format, the Room HTTP API, the daemon loop and the test plan. Where this file and `build-2.md` differ, section 12 says so and gives the reason. Screen copy still comes from `experience.md`.

Sources read for this contract: `build-2.md`, `architecture.md`, `learning.md` sections 3, 4, 6, 7, 10 and 12, `experience.md` sections 2 to 7 and 13, `security.md`, `skills/learning-while-building/scripts/room.py` and `record.py`, `design/learning-experience/assets/room.css`, and the prototypes `revert.html` and `inbox.html`.

Four facts in this contract were checked by running the tools on 2026-11-15 (git 2.43.0, pytest 9.2.0, Python 3.13) and are marked [measured]. Nothing else here was run.

---

## 0. Rules for all three owners

1. **Three groups, disjoint files.** CORE, SHELL and ROOM (section 1). Nobody edits a file outside their group. A fourth role, the integrator, works after the three and owns only the fixture and end-to-end tests.
2. **Dependency direction.** CORE imports nothing from SHELL or ROOM. SHELL imports CORE, and `daemon.py` imports `firsthand.room.server` and `firsthand.engine` only inside its default factories. ROOM imports nothing from CORE or SHELL at run time: it receives an object that satisfies `EngineAPI` (section 2.6) and treats it by duck typing. Names from `firsthand.model` that ROOM wants for annotations go under `if TYPE_CHECKING:`.
3. **Step 0 comes first.** The CORE owner writes these files before anything else, exactly as specified in sections 2, 3 and 4.1: `firsthand/__init__.py`, `firsthand/model.py`, `firsthand/paths.py`, `firsthand/events.py`, `tests/test_firsthand.py`, `tests/firsthand/support.py`. They are small and fully pinned here. SHELL needs them to import. If the workflow cannot sequence step 0, SHELL writes against the signatures and reports any test that cannot import as blocked on step 0, not as a defect. A SHELL test that needs a CORE module beyond step 0 at run time (only `init`, which calls `record.ensure_record`) guards itself with `unittest.skipUnless` on that import. The integrator's full run must show no skipped test of that kind.
4. **Stubs.** Every cross-group call goes through a Protocol or a plain function named in this file. A unit test of one group replaces the other side with a fake written in the test file. Fakes live only under `tests/` (the repo's `no-mocks-in-production` hook enforces this).
5. **Platform.** POSIX only in 2a (Linux, macOS). Python 3.11 or later, standard library only at run time.
6. **Size limits from the repo's pre-commit hooks.** No Python file over 800 lines. No function over cyclomatic complexity 10 or cognitive complexity 15. The module split below is made with those limits in mind. Split further inside your own group if a file would pass 800 lines, and say so in your report.
7. **Temporary homes in every test.** No test reads or writes the real `~/.claude`, `~/.firsthand`, `~/.config/firsthand` or `~/.learning-while-building`. Every test class uses `support.TempHome` (section 3.2). Production code reaches the file system only through `firsthand.paths`.
8. **Text.** No em dashes, no emoji, plain prose. Exact strings shown to a person or an agent are in section 9 and in `experience.md`. Do not invent others without listing them in your report.

---

## 1. Package tree and ownership

```
firsthand/
  __init__.py                 CORE   __version__ = "0.1.0", ENGINE = "firsthand/0.1.0"
  __main__.py                 SHELL  python -m firsthand
  model.py                    CORE   shared dataclasses and Protocols (section 2)        [added]
  paths.py                    CORE   every path, FIRSTHAND_HOME and HOME (section 3)
  events.py                   CORE   spool line codec, secret scan (section 4.1)
  record.py                   CORE   the record: event store, ULIDs, commits
  gitwatch.py                 CORE   project root and id, HEAD and branch, path tests, globs
  timeline.py                 CORE   tasks, bases, the done signal: a pure state machine
  ask.py                      CORE   gates, the moment state table, chat control words    [added]
  keys.py                     CORE   the key store and the one output rule
  words.py                    CORE   every exact line the engine produces                 [added]
  views.py                    CORE   read models for the Room and the CLI                 [added]
  engine.py                   CORE   orchestration: implements EngineAPI                  [added]
  runner/
    __init__.py               CORE
    snapshot.py               CORE   snapshots, diff, file reads, checkout
    scratch.py                CORE   scratch copies, scrubbed environment, timed runs
    pytest_adapter.py         CORE   ast test listing, argv, junit parsing
    generic_adapter.py        CORE   per-file runs classified by exit code
  moments/
    __init__.py               CORE   REGISTRY = (revert_test,)
    revert_test.py            CORE   match, plan, key, score, cue, run, replies
  cli.py                      SHELL  argparse entry point, every command, init
  client.py                   SHELL  control socket client                                [added]
  daemon.py                   SHELL  process shell: spool tail, socket, reply files, lifecycle
  hooks.py                    SHELL  the hook dispatcher
  config.py                   SHELL  settings files, ConfigStore (implements SettingsStore)
  install.py                  SHELL  engine install, settings merge, backups, uninstall
  adapters/
    __init__.py               SHELL
    claude_code.py            SHELL  event table, payload to spool line, output shapes
    claude_code_skill.md      SHELL  the SKILL.md text installed for the agent
  room/
    __init__.py               ROOM
    server.py                 ROOM   HTTP server, sessions, request checks, routes, SSE
    page.html                 ROOM   the one page shell
    static/room.css           ROOM   tokens copied from design/learning-experience/assets/room.css
    static/room.js            ROOM   Inbox, card, result, Journal, Skills, Settings

pyproject.toml                SHELL  [build-system], [project], [project.scripts], package data,
                                     and "firsthand" added to [tool.vulture] paths
uv.lock                       SHELL  regenerated by the uv-lock hook once [project] exists

tests/
  test_firsthand.py           CORE   loader shim (section 10.1)
  firsthand/                         NOT a package: no __init__.py here, ever (section 10.1)
    support.py                CORE   TempHome and small git helpers (section 3.2)
    test_core_*.py            CORE
    test_shell_*.py           SHELL
    test_room_*.py            ROOM
    fixtures.py               integrator
    test_e2e_*.py             integrator
  fixtures/                   integrator  recorded spool sequences, if kept as files
```

Changes to the file list in `build-2.md` section 2, all inside the same three groups:

- **Added to CORE:** `model.py` (the shared vocabulary. Not named `types.py`, which would shadow the standard library module if a file in the package were ever run as a script), `engine.py` (the orchestration that `build-2.md` places in the daemon), `ask.py`, `words.py`, `views.py`. Reason: the loop of section 8 uses only CORE modules, the fixture tests of `build-2.md` section 9 replay spool lines against it without a process or a socket, and one file holding all of it would pass the 800 line limit.
- **Added to SHELL:** `client.py` (so `cli.py` and tests share one socket client), `__main__.py`.
- **`daemon.py` stays in SHELL** and is the process around the engine: it tails the spool, serves the control socket, writes reply files, starts the Room server and exits when idle.

CORE is the largest group. If it is worked as two halves the seam is `moments.revert_test.run()` and `runner.snapshot.SnapshotStore`: one half is `model`, `paths`, `events`, `record`, `gitwatch`, `runner/*`, `moments/revert_test`. The other is `timeline`, `ask`, `keys`, `words`, `views`, `engine`.

---

## 2. Shared types (`firsthand/model.py`, CORE)

All dataclasses are frozen unless marked. Type aliases are `typing.Literal`.

### 2.1 Vocabulary

```python
EventKind  = Literal["session_start", "prompt_submit", "before_tool", "after_tool", "tool_failed", "turn_end"]
ToolKind   = Literal["edit", "shell", "ask", "plan", "other"]
Dial       = Literal["off", "notes", "standard", "deep"]
TestResult = Literal["fails_on_assertion", "still_passes", "cannot_run", "does_not_pass"]
How        = Literal["pytest", "exit_code"]
Answer     = Literal["1", "2", "3", "4", "none", "fails", "passes", "dont_know"]
Confidence = Literal["high", "low"]
Channel    = Literal["room", "chat"]
MomentState = Literal["open", "held", "sealed", "settled", "skipped", "closed"]
CloseHow   = Literal["moved-on", "shown-first", "check-dropped", "wrong-start", "quiet", "off", "unseen"]
Want       = Literal["question", "pending", "result", "finding", "fact", "ack"]

REVEALED: frozenset[str] = frozenset({"sealed", "settled", "skipped", "closed"})
PRINT_PREFIX = "Firsthand result for the reply above. The firsthand skill prints these lines unchanged:"
```

`does_not_pass` is produced only by the generic adapter. `dont_know` is the stored form of the answer "don't know".

### 2.2 Errors

```python
class FirsthandError(Exception):
    """Base. Carries a code for the Room and the control socket."""
    code: str = "internal"
    def __init__(self, message: str, code: str | None = None) -> None: ...
    @property
    def message(self) -> str: ...

class EngineError(FirsthandError): ...   # codes: not_found, state, invalid, confirm, refused, no_question
class KeyLocked(FirsthandError): ...     # code "locked": a result was asked for before it may be shown
```

ROOM and the daemon map any exception that has string attributes `code` and `message` to an error response (sections 5.2 and 7.1). They do not import these classes.

### 2.3 Spool event

```python
@dataclass(frozen=True)
class SpoolEvent:
    id: str                      # 12 lower-case hex characters, made by the dispatcher
    at: str                      # UTC, "2026-11-14T09:12:03Z"
    agent: str                   # "claude-code"
    session: str
    cwd: str
    event: EventKind
    tool: ToolKind | None = None
    tool_use: str | None = None  # the agent's tool_use_id
    command: str | None = None   # shell only, secret-scanned
    exit: int | None = None      # see section 4.1
    failing: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()  # edit only, absolute
    prompt: str | None = None    # prompt_submit only, secret-scanned
    prompt_cut: bool = False
    source: str | None = None    # session_start only
    venv: str | None = None      # session_start and prompt_submit: VIRTUAL_ENV of the hook process
    sub: bool = False            # the call was made inside a subagent
    interrupted: bool = False    # tool_failed with is_interrupt
```

### 2.4 Git and check values

```python
@dataclass(frozen=True)
class FileChange:
    path: str                    # relative to the project root, forward slashes
    status: Literal["A", "M", "D"]

@dataclass(frozen=True)
class HeadState:
    commit: str | None           # None in a repo with no commit
    branch: str | None           # None when detached

@dataclass(frozen=True)
class TestItem:
    n: int                       # 1-based position on the card
    id: str                      # pytest node id, or a test file path under the generic adapter
    name: str                    # last part of the id
    path: str
    line: int                    # def line; 1 under the generic adapter
    status: Literal["new", "edited"]
    assert_lines: tuple[int, ...]   # every assert statement in the test, in order
    assert_line: int | None      # the last one, or None
    assert_text: str | None      # its source text, one line, at most 200 characters

@dataclass(frozen=True)
class Candidate:
    kind: str                    # "revert_test"
    check_id: str                # a ULID. If a question is asked, it is also the moment id
    project_id: str
    project_root: str
    task_id: str
    change_id: str
    base_tree: str
    head_tree: str
    source_changes: tuple[FileChange, ...]   # the non-test files of the diff
    tests: tuple[TestItem, ...]              # 1 to 4
    how: How
    high_stakes: str | None      # the first matching glob as stored, or None

@dataclass(frozen=True)
class StepRun:
    step: Literal["control", "undone"]
    command: str                 # shell-quoted, secret-scanned
    exit: int | None             # None when killed at the time limit
    failing: tuple[str, ...]
    output_sha256: str

@dataclass(frozen=True)
class KeyItem:
    id: str
    result: TestResult
    assert_line: int | None
    assert_text: str | None
    fail_line: int | None        # line in the test file where the undone run failed, if read

@dataclass(frozen=True)
class Key:
    moment: str                  # equals Candidate.check_id
    kind: str
    how: How
    base_tree: str
    head_tree: str
    made_at: str
    tests: tuple[KeyItem, ...]
    steps: tuple[StepRun, ...]
    undone_paths: tuple[str, ...]
    duration_s: float

@dataclass(frozen=True)
class CheckOutcome:
    key: Key | None              # None when unavailable
    unavailable: str | None      # a reason from section 4.6, or None
    step: Literal["setup", "control", "undone"] | None = None   # where it stopped
    steps: tuple[StepRun, ...] = ()

@dataclass(frozen=True)
class Reply:
    answer: Answer
    confidence: Confidence | None

@dataclass(frozen=True)
class Score:
    result: Literal["match", "miss", "unscored"]
    outcome_kind: Literal["common", "uncommon"]
    catch: bool
    unscored_reason: str | None
```

### 2.5 Moment, settings, hook reply

```python
@dataclass
class Moment:                    # mutable, owned by the engine
    id: str
    kind: str
    state: MomentState
    project_id: str
    change_id: str
    task_id: str
    session: str                 # the agent session whose turn end produced it
    task_name: str
    base_at: str
    base_tree: str
    head_tree: str
    tests: tuple[TestItem, ...]
    how: How
    high_stakes: str | None
    offered_at: str
    seen: bool = False
    pending: dict | None = None  # held only: {"kind": "pick"|"skip", "answer", "confidence", "at"}
    answer: Answer | None = None
    confidence: Confidence | None = None
    channel: Channel | None = None
    close_how: CloseHow | None = None
    opened: bool = False         # the person opened the result

@dataclass(frozen=True)
class Settings:
    dial: Dial = "standard"
    dial_before_off: Dial = "standard"
    daily_limit: int = 1                 # 1 to 3
    findings_to_agent: bool = True
    work_computer: bool = True
    quiet_today: str | None = None       # a local date, "2026-11-14"
    check_time_limit_s: int = 120

@dataclass(frozen=True)
class ProjectSettings:
    id: str
    name: str
    roots: tuple[str, ...]
    test_command: str | None
    high_stakes: tuple[str, ...]
    quiet: bool = False
    env: tuple[tuple[str, str], ...] = ()   # runner.env: declared test variables
    carry: tuple[str, ...] = ()             # runner.carry: always empty in 2a

DEFAULT_HIGH_STAKES = ("**/migrations/**", "**/auth/**", "**/payments/**", "**/billing/**")

class SettingsStore(Protocol):
    def load(self) -> Settings: ...
    def set(self, key: str, value: object) -> Settings: ...                 # raises EngineError("invalid")
    def project(self, project_id: str) -> ProjectSettings | None: ...
    def ensure_project(self, project_id: str, root: str) -> ProjectSettings: ...
    def set_project(self, project_id: str, key: str, value: object) -> ProjectSettings: ...

@dataclass(frozen=True)
class HookReply:
    event_id: str
    session: str
    event: Literal["turn_end", "prompt_submit"]
    visible: str | None = None   # one line for the person at a turn end
    context: str | None = None   # text added to the model's context at a prompt
```

### 2.6 `EngineAPI`

The one interface SHELL and ROOM call. `engine.Engine` implements it. Every method is safe to call from any thread. Every method that takes `ref` accepts a moment id or the six-character short form (section 7.2) and raises `EngineError("not_found")` otherwise.

```python
class EngineAPI(Protocol):
    # events
    def handle(self, ev: SpoolEvent, reply: Callable[[HookReply], None]) -> None: ...
    def delivered(self, event_id: str, ok: bool) -> None: ...
    def tick(self) -> None: ...
    def idle(self) -> bool: ...
    def close(self) -> None: ...
    def subscribe(self, fn: Callable[[dict], None]) -> Callable[[], None]: ...
    # views (plain JSON-ready dicts, section 7.2)
    def inbox(self, project: str | None = None) -> dict: ...
    def question(self, ref: str | None = None, *, cwd: str | None = None, seen: bool = True) -> dict: ...
    def journal(self, project: str | None = None, limit: int = 200) -> dict: ...
    def skills(self, project: str | None = None) -> dict: ...
    def settings(self, project: str | None = None) -> dict: ...
    def status(self, cwd: str | None = None) -> dict: ...
    # actions (each returns the question view after the action, unless noted)
    def lock(self, ref: str | None, answer: str, *, channel: Channel, final: bool,
             cwd: str | None = None) -> dict: ...
    def undo(self, ref: str) -> dict: ...
    def show(self, ref: str) -> dict: ...
    def confidence(self, ref: str, value: str | None) -> dict: ...
    def skip(self, ref: str | None, *, channel: Channel, final: bool, cwd: str | None = None) -> dict: ...
    def wrong_start(self, ref: str) -> dict: ...
    def dispute(self, ref: str, reason: str) -> dict: ...
    def quiet(self, scope: Literal["session", "today", "here"], on: bool = True, *,
              cwd: str | None = None, session: str | None = None) -> dict: ...      # returns {"lines": [...]}
    def set_settings(self, changes: Mapping[str, object], *, project: str | None = None,
                     source: Literal["room", "cli", "agent"], confirm: bool = False) -> dict: ...  # the settings view
```

Behaviour, one line each:

| Method | Behaviour | Raises |
| :- | :- | :- |
| `handle` | Applies one spool event (section 8). For `prompt_submit` and `turn_end` it calls `reply` exactly once, as early as the output is known. That can be after `handle` has returned, from `tick` or from the check thread, so `reply` must be safe to call from any thread. For other events it never calls `reply`. An event whose `id` was already applied is ignored | Never. Errors are logged and the event is dropped |
| `delivered` | The daemon reports whether the dispatcher claimed the reply file for `event_id`. On `ok` the engine marks the question seen, the fact printed, the findings sent. On not `ok` they stay queued | Never |
| `tick` | Called by the daemon about every 50 ms. Answers deferred replies whose 250 ms budget is spent, and closes unseen questions when the local day ends | Never |
| `idle` | True when no check runs or waits, no moment is `open`, `held` or `sealed`, and no reply is deferred | |
| `close` | Seals held picks, finalises held skips, writes the checkpoint, commits the record if dirty. The engine is unusable after | |
| `subscribe` | Registers a listener for change notices: a dict with `seq` (a rising integer), `topic` (`inbox`, `question` or `settings`) and `id` (a moment id or None). Returns the function that removes it. Listeners are called on the engine's thread and must not block | |
| `inbox`, `journal`, `skills`, `settings`, `status` | Read models, section 7.2. `project=None` means the project of the newest event | |
| `question` | The question view. With `ref=None`, the open question for the project at `cwd`, or `EngineError("no_question")`. `seen=True` marks an open question as seen | `not_found`, `no_question` |
| `lock` | `answer` is a canonical `Answer` or raw reply text (parsed by the moment's `parse_reply`). `final=False` (the Room): `open` to `held`, undoable. `final=True` (chat, CLI, or "don't know"): seals at once. `dont_know` always seals | `invalid` (not a reply word, message lists them), `state` (not `open`) |
| `undo` | `held` back to `open`, for a pick or a skip | `state` |
| `show` | Seals a held pick if there is one, marks the result opened. Returns the view with `result` filled when the outcome is known | `state` if `open` |
| `confidence` | Sets or clears How sure on a held pick. `value` is `"high"`, `"low"` or `None` | `state` unless `held` with a pick, `invalid` |
| `skip` | `final=False`: `open` to `held` with a pending skip. `final=True`: `open` to `skipped` | `state` |
| `wrong_start` | Only while `open`, and only when the base would move (the earlier start differs from the task base; otherwise `state` and nothing changes). Drops the open check's result unseen, closes the moment as `wrong-start`, moves the task base (section 12, decision 18) and reruns the check. Returns the replacement question's view when one was offered at once. A question closed as `wrong-start` has no result view | `state` |
| `dispute` | Only when `settled` with a score, once per moment. Reruns the check on the stored trees | `state`, `invalid` (empty reason) |
| `quiet` | Sets or clears quiet for a session, today, or the project at `cwd`. Closes an open question of that scope as `quiet` | `invalid` |
| `set_settings` | Validates and stores. A widening change (section 4.5) needs `confirm=True` from `"room"`, is allowed from `"cli"`, and is refused from `"agent"` | `invalid`, `confirm`, `refused` |

---

## 3. Paths (`firsthand/paths.py`, CORE)

Every path in the product comes from this module. No other module builds a path under a home folder, reads `HOME`, or calls `Path.home()`.

### 3.1 Functions

Environment read on every call, never cached, so a test can change it:

| Variable | Effect |
| :- | :- |
| `HOME` | The user's home. Read as `os.environ["HOME"]`, falling back to `Path.home()` only when unset |
| `FIRSTHAND_HOME` | Replaces `~/.firsthand` |
| `FIRSTHAND_CONFIG_HOME` | Replaces `~/.config/firsthand`. When unset and `FIRSTHAND_HOME` is set, the config home is `<FIRSTHAND_HOME>/dotconfig` |
| `FIRSTHAND_CLAUDE_DIR` | Replaces `~/.claude` |

`XDG_CONFIG_HOME` and `CLAUDE_CONFIG_DIR` are not read (section 12, decision 2).

```python
def user_home() -> Path
def home() -> Path                              # FIRSTHAND_HOME or <HOME>/.firsthand
def config_home() -> Path
def claude_dir() -> Path
def record_dir() -> Path                        # home()/record
def run_dir() -> Path                           # home()/run
def cache_dir() -> Path                         # home()/cache
def engine_dir(version: str) -> Path            # home()/engine/<version>
def spool_file() -> Path                        # run/spool.jsonl
def spool_offset_file() -> Path                 # run/spool.offset
def daemon_lock_file() -> Path                  # run/daemon.lock
def daemon_info_file() -> Path                  # run/daemon.json
def daemon_log_file() -> Path                   # run/daemon.log
def hook_log_file() -> Path                     # run/hook.log
def control_socket() -> Path                    # run/daemon.sock, or the fallback below
def state_file() -> Path                        # run/state.json
def out_dir() -> Path                           # run/out
def reply_file(event_id: str) -> Path           # run/out/<event-id>.json
def keys_dir() -> Path                          # run/keys
def key_file(moment_id: str) -> Path            # run/keys/<moment-id>.json
def scratch_root() -> Path                      # run/scratch
def scratch_dir(check_id: str) -> Path          # run/scratch/<check-id>
def index_dir() -> Path                         # run/index (temporary git index files)
def snapshot_store(project_id: str) -> Path     # cache/snapshots/<project-id>.git
def port_file() -> Path                         # config_home()/port
def backups_dir() -> Path                       # config_home()/backups
def install_manifest() -> Path                  # config_home()/install.json
def room_sessions_file() -> Path                # config_home()/room-sessions.json
def claude_settings() -> Path                   # claude_dir()/settings.json
def claude_skill_file() -> Path                 # claude_dir()/skills/firsthand/SKILL.md
def ensure_private_dirs() -> None               # creates home, run, out, keys, scratch, index, cache
                                                # with mode 0700, and config_home with 0700
def write_private(path: Path, data: bytes) -> None   # write to <path>.tmp with mode 0600, then os.replace
```

- No function creates anything except `ensure_private_dirs` and `write_private`.
- `reply_file`, `key_file`, `scratch_dir`, `snapshot_store` and `engine_dir` raise `ValueError` when their argument is not `[A-Za-z0-9_.-]{1,64}` or starts with a dot. This is the guard against a path built from an id that came from outside.
- `control_socket()`: a Unix socket path is limited to about 100 bytes. If `run/daemon.sock` is longer than 96 bytes the function returns `/tmp/fh-<uid>-<first 8 hex of sha256(str(run_dir()))>/d.sock` (`tempfile.gettempdir()` only when `/tmp` does not exist; section 13). The daemon creates that folder with mode 0700. Both sides compute the same path.

### 3.2 `tests/firsthand/support.py` (CORE, step 0)

```python
class TempHome(unittest.TestCase):
    """Base class for every Firsthand test. Nothing under the real home is read or written."""
    tmp: Path            # a fresh temporary folder, removed at teardown
    home: Path           # tmp/home, set as HOME
    fh: Path             # tmp/home/.firsthand, set as FIRSTHAND_HOME

    def setUp(self) -> None: ...
```

`setUp` sets `HOME`, `FIRSTHAND_HOME` and `LEARNING_HOME` (`tmp/home/.learning-while-building`), removes `FIRSTHAND_CONFIG_HOME`, `FIRSTHAND_CLAUDE_DIR`, `CLAUDE_CONFIG_DIR`, `XDG_CONFIG_HOME`, `VIRTUAL_ENV`, `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE`, sets `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` to `os.devnull`, sets `FIRSTHAND_NO_DAEMON=1`, restores the environment at teardown, and then asserts that `paths.home()`, `paths.config_home()` and `paths.claude_dir()` are all inside `tmp`. A test that needs a real daemon removes `FIRSTHAND_NO_DAEMON` itself.

Helpers, all plain functions:

```python
def child_env() -> dict[str, str]                       # os.environ as set above, for subprocess calls
def git(cwd: Path, *args: str) -> str                   # runs git with a fixed identity, returns stdout, raises on failure
def make_repo(root: Path, files: Mapping[str, str]) -> None      # git init, write files, one commit "base"
def write_files(root: Path, files: Mapping[str, str | None]) -> None   # None deletes the file
def repo_fingerprint(root: Path) -> str                 # sha256 over the working tree file contents, every file under .git,
                                                        # `git status --porcelain=v2` and the object count
```

---

## 4. On-disk formats

Every file under `run/` and `config_home()` has mode 0600 and is written with `paths.write_private` unless stated. All JSON is UTF-8. A reader ignores keys it does not know.

### 4.1 The spool line (`firsthand/events.py`, CORE)

`run/spool.jsonl`, one JSON object per line, appended by the dispatcher, read by the daemon.

```json
{"v": 1, "id": "3fa94c0b71de", "at": "2026-11-14T09:12:03Z", "agent": "claude-code", "session": "abc123",
 "cwd": "/home/sam/orbit-pay", "event": "after_tool", "tool": "shell", "tool_use": "toolu_01",
 "command": "pytest -q", "exit": 0, "failing": [], "paths": []}
```

| Event | Keys beyond `v`, `id`, `at`, `agent`, `session`, `cwd`, `event` |
| :- | :- |
| `session_start` | `source` (string), `venv` (string or null) |
| `prompt_submit` | `prompt` (secret-scanned, cut to 20,000 characters), `prompt_cut` (only when true), `venv` |
| `before_tool` | `tool`, `tool_use`, `command` (shell, else null), `exit` null, `failing` [], `paths` (edit, else []) |
| `after_tool` | As `before_tool`, with `exit` 0 for shell and `failing` parsed from `tool_response.stdout` |
| `tool_failed` | As `before_tool`, with `exit` parsed from the first line of `error` (`Exit code N`), null when absent, `failing` parsed from `error`, `interrupted` (only when true) |
| `turn_end` | Nothing more |

`sub: true` is added to any line whose payload had an `agent_id`. No other key is ever written. `failing` holds at most 50 ids of at most 300 characters each. The dispatcher parses `failing` for every shell call and the engine reads it only when the command is a test run (section 12, decision 5).

```python
SPOOL_VERSION = 1
MAX_PROMPT_CHARS = 20_000
MAX_LINE_BYTES = 65_536

def now_stamp(now: datetime | None = None) -> str              # "2026-11-14T09:12:03Z"
def new_event_id() -> str                                      # secrets.token_hex(6)
def encode(line: Mapping[str, object]) -> bytes                # one JSON line ending in "\n"; drops unknown keys;
                                                               # raises ValueError over MAX_LINE_BYTES after cutting
def decode(raw: bytes | str) -> SpoolEvent | None              # None for a blank, malformed or unknown-version line
def scan_secrets(text: str) -> tuple[str, list[str]]           # (text with matches replaced, kinds found)
```

`scan_secrets` replaces each match with `[redacted: <kind>]`. Kinds and patterns: `aws-key` (`AKIA[0-9A-Z]{16}`), `github-token` (`gh[pousr]_[A-Za-z0-9]{36,}` and `github_pat_[A-Za-z0-9_]{40,}`), `slack-token` (`xox[abprs]-[A-Za-z0-9-]{10,}`), `api-key` (`sk-[A-Za-z0-9_-]{20,}`), `private-key` (a `-----BEGIN ... PRIVATE KEY-----` block), `bearer` (`Bearer\s+[A-Za-z0-9._~+/=-]{20,}`), `jwt` (three base64url parts starting `eyJ`), `assignment` (a name holding `secret`, `token`, `password`, `passwd` or `credential` anywhere, or ending in an `api`, `access`, `private`, `auth` or `signing` key, then `:` or `=` not followed by a second `:`, then `\S{8,}`; case-insensitive, value replaced), `url-password` (the password in `scheme://user:password@host`), `mysql-password` (the value of `-p<password>` on a `mysql` command line). The same function is used on every free-text field before it enters the spool or the record.

**Appending** (the dispatcher): open with `O_WRONLY | O_APPEND | O_CREAT`, mode 0600, take `flock(LOCK_EX)`, write the line with one `os.write`, release.

**Reading** (the daemon): under `flock(LOCK_EX)` read from the saved offset to the last newline, release, hand each decoded event to `engine.handle`, save the new offset to `run/spool.offset` (`{"offset": 1234}`) after each event. When the offset equals the file size, take the lock again and, if the size is unchanged, truncate to zero and save offset 0. A crash can replay at most the events after the last saved offset, and `engine.handle` ignores an `id` it has already applied (it remembers the last 512).

### 4.2 The reply file (the ready line the dispatcher reads)

`run/out/<event-id>.json`, written by the daemon when the engine calls `reply`, for every `prompt_submit` and `turn_end`, including when there is nothing to say.

```json
{"v": 1, "id": "3fa94c0b71de", "session": "abc123", "event": "turn_end",
 "visible": "Firsthand (skip ok): your agent finished and added 3 tests. ...", "context": null}
```

- `visible` is non-null only on `turn_end`. `context` is non-null only on `prompt_submit`. Both null means "print nothing".
- **Claim.** The dispatcher polls for the file every 10 ms for at most 300 ms after its append. It claims it with `os.rename(<id>.json, <id>.claimed)`, reads it, deletes it, and prints what `adapters.claude_code.render` returns.
- **Confirm.** A reply file with text that the dispatcher has already taken (the file is gone) is confirmed at once with `engine.delivered(id, True)` (section 13). Otherwise, one second after writing a reply file the daemon tries `os.rename(<id>.json, <id>.expired)`. If that fails with `FileNotFoundError` the dispatcher has it and the daemon calls `engine.delivered(id, True)`. If it succeeds the daemon deletes the file and calls `engine.delivered(id, False)`. Replies with both fields null are deleted without a call.
- The dispatcher does not wait when it had to start the daemon itself, and never waits on other events.

### 4.3 Daemon files

`run/daemon.lock`: an empty file. The daemon holds `flock(LOCK_EX | LOCK_NB)` on it for its whole life. A dispatcher or CLI tests for a running daemon by trying the same lock and releasing it at once.

`run/daemon.json`, written after the socket listens and the Room is bound, removed at exit:

```json
{"v": 1, "pid": 4242, "started": "2026-11-14T09:12:03Z", "engine": "firsthand/0.1.0",
 "socket": "/home/sam/.firsthand/run/daemon.sock", "port": 4127, "room": "http://127.0.0.1:4127"}
```

`port` and `room` are null when the Room port could not be bound. `config_home()/port` holds the chosen port as decimal text. The value `0` means "any free port" and is for tests.

### 4.4 The control socket protocol

A Unix stream socket at `paths.control_socket()`, mode 0600. One request and one response per connection, each one JSON object on one line, at most 65,536 bytes.

```json
{"v": 1, "op": "answer", "args": {"text": "2 sure"}, "cwd": "/home/sam/orbit-pay", "agent": false}
{"ok": true, "result": {"lines": ["Firsthand, revert test. Matched. You said 2. Sure.", "..."]}}
{"ok": false, "error": {"code": "no_question", "message": "No question is open. Nothing to answer."}}
```

`agent` is true when the CLI found an agent among its ancestors (section 5.2, `cli.under_agent`).

| `op` | `args` | Calls | `result` |
| :- | :- | :- | :- |
| `ping` | | | `{"pid", "engine", "room"}` |
| `status` | | `engine.status(cwd)` | The status view |
| `inbox` | `project?` | `engine.inbox` | The inbox view |
| `question` | `ref?` | `engine.question(ref, cwd=cwd)` | The question view |
| `answer` | `text` | `engine.lock(None, text, channel="chat", final=True, cwd=cwd)` | `{"lines": view["say"]}` |
| `answer_room` | `ref`, `text` | `engine.lock(ref, text, channel="room", final=True)` (used by `room --tty`) | The question view |
| `skip` | | `engine.skip(None, channel="chat", final=True, cwd=cwd)` | `{"lines": view["say"]}` |
| `quiet` | `scope`, `on` | `engine.quiet` | `{"lines": [...]}` |
| `journal` | `limit?` | `engine.journal` | The journal view |
| `skills` | | `engine.skills` | The skills view |
| `settings_get` | | `engine.settings` | The settings view |
| `settings_set` | `changes`, `project?` | `engine.set_settings(..., source="agent" if agent else "cli")` | The settings view |
| `room_ticket` | `next?` | `RoomServer.new_ticket` | `{"url": "http://127.0.0.1:4127/enter?t=..."}` |
| `stop` | | The daemon exits after replying | `{}` |

The daemon refuses `journal`, `skills`, `answer_room` and `room_ticket` with code `refused` when `agent` is true: those hold the person's calls or a session credential.

The status view:

```json
{"dial": "standard", "quiet": null, "asked_today": 0, "daily_limit": 1, "room": "http://127.0.0.1:4127",
 "project": {"id": "prj_3b9f52c1a7e0", "name": "orbit-pay", "test_command": "pytest -q", "watched": true, "why_not": null},
 "question": {"ref": "r6t9kd", "line": "Firsthand (skip ok): ..."}}
```

`project` is null outside a git repo. `watched` is false with `why_not` set to `no commit yet` or `no test command`. `question` is null when none is open. It never holds a result.

### 4.5 Config files

In the record, written only through `config.ConfigStore`:

`record/config/<key>.json`, one file per setting:

```json
{"key": "daily_limit", "value": 1, "at": "2026-11-14T09:12:03Z"}
```

Keys and values: `dial` (`off`, `notes`, `standard`, `deep`), `dial_before_off` (a dial), `daily_limit` (1, 2 or 3), `findings_to_agent` (bool), `work_computer` (bool), `quiet_today` (a local date or null), `check_time_limit_s` (30 to 600). A missing file means the default in `Settings`.

`record/projects/<project-id>.json`:

```json
{"format": 1, "id": "prj_3b9f52c1a7e0", "name": "orbit-pay", "roots": ["/home/sam/orbit-pay"],
 "test_command": "pytest -q", "high_stakes": ["**/migrations/**", "refunds/**"], "quiet": false,
 "runner": {"env": {}, "carry": []}}
```

**Widening changes:** raising `daily_limit`, moving `dial` up the order off, notes, standard, deep, turning `findings_to_agent` on, and any change of `test_command`. Everything else narrows or is neutral.

Outside the record: `config_home()/port` (section 4.3), `config_home()/room-sessions.json` (private to ROOM: SHA-256 of each session id, its token and expiry) and the install manifest `config_home()/install.json`:

```json
{"v": 1, "agent": "claude-code", "installed_at": "2026-11-14T09:10:00Z", "engine": "0.1.0",
 "launcher": "/home/sam/.firsthand/engine/0.1.0/bin/firsthand",
 "backup": "/home/sam/.config/firsthand/backups/20261114T091000Z",
 "files": [{"path": "/home/sam/.claude/settings.json", "existed": true, "backup": "settings.json",
            "sha256_before": "...", "sha256_after": "..."},
           {"path": "/home/sam/.claude/skills/firsthand/SKILL.md", "existed": false, "backup": null,
            "sha256_before": null, "sha256_after": "..."}]}
```

### 4.6 The key file

`run/keys/<moment-id>.json`, written when the undone run finishes, deleted when its results have entered the record (or the check is discarded). The file name is the check id, which is the moment id whenever a question is asked.

```json
{"v": 1, "moment": "01JC8Y2F7H3QZ5W8N1P4R6T9KD", "kind": "revert_test", "how": "pytest",
 "base_tree": "9d1c...", "head_tree": "fbc5...", "made_at": "2026-11-14T09:40:02Z",
 "tests": [
  {"id": "tests/test_refunds.py::test_same_key_refunds_once", "result": "fails_on_assertion",
   "assert_line": 23, "assert_text": "assert len(ledger.refunds(charge)) == 1", "fail_line": 23},
  {"id": "tests/test_refunds.py::test_refund_response_is_stable", "result": "still_passes",
   "assert_line": 41, "assert_text": "assert resp.status_code == 200", "fail_line": null}],
 "steps": [{"step": "control", "command": "...", "exit": 0, "failing": [], "output_sha256": "..."},
           {"step": "undone", "command": "...", "exit": 1, "failing": ["tests/test_refunds.py::test_same_key_refunds_once"], "output_sha256": "..."}],
 "undone_paths": ["refunds/service.py"], "duration_s": 3.2}
```

`check.unavailable` reasons: `does not match here`, `editable install`, `time limit`, `no test command`, `no interpreter`, `pytest not found`, `snapshot failed`.

### 4.7 The engine checkpoint

`run/state.json`: private to `engine.py`, versioned, rewritten after each handled event and each action. It holds sessions, tasks, open moments, queued agent lines, the last 512 spool ids and the first prompt of the day. It never holds a key result. Other groups do not read it.

### 4.8 The record

`record/` is created by `record.ensure_record`: mode 0700, `git init -q`, `FORMAT` holding `firsthand-record 1` and a newline, and a first commit `init`. Layout as `architecture.md` section 2: `events/<yyyy>/<mm>/<ulid>.json`, one file per event, `json.dumps(indent=2, sort_keys=True)` plus a newline.

Envelope, the same for every type:

```json
{"format": 1, "id": "01JC8Y3W8Q5V7N2K4T6R9X1M0B", "type": "call.sealed", "project": "prj_3b9f52c1a7e0",
 "change": "01JC8XZ0M4T1A7C3E5G8J2K6P9", "moment": "01JC8Y2F7H3QZ5W8N1P4R6T9KD",
 "surface": "claude-code", "engine": "firsthand/0.1.0", "at": "2026-11-14T09:41:11Z", "body": {}, "x": {}}
```

`change`, `moment` and `surface` are null where they do not apply. `<yyyy>/<mm>` comes from `at`.

Bodies of the eleven types 2a writes:

| Type | Body |
| :- | :- |
| `task.started` | `task` (ULID), `session`, `name` (section 9.1), `prompt` (verbatim, scanned), `base_tree`, `base_at`, `head` (commit or null), `branch` (or null), `first_of_day` (bool), `spool_id` |
| `task.event` | `task`, `kind`, `spool_id` (or null), plus by kind. `prompt`: `prompt`. `test_run`: `command`, `exit`, `failing`, `tree` (or null). `done`: `tree`, `paths` (changed since the base, at most 200), `files` (count), `tests_changed` (count). `ask`: nothing. `base_moved`: `from`, `to`, `why` (`wrong-start`). `line_delivered`: `line` (`question`, `fact`, `result`, `finding`), `check` (id or null) |
| `moment.offered` | `moment_kind` (`revert_test`), `form` (`pick` for several tests, `single` for one), `skill` (1), `break` (`done`), `fading` (`full`), `task`, `base_tree`, `head_tree`, `how`, `tests` (list of `{n, id, path, line, status, assert_lines}`), `high_stakes` (glob or null), `replaces` (moment id or null) |
| `call.sealed` | `moment_kind`, `form`, `answer` (an `Answer`), `channel` (`room` or `chat`), `case_chosen_by` (`engine`), `picked_at` |
| `call.confidence` | `value` (`high` or `low`) |
| `check.ran` | `check_kind`, `check` (the check id), `how`, `base_tree`, `head_tree`, `steps` (list of `{step, command, exit, failing, output_sha256}`), `results` (list of `{id, result, assert_line, fail_line}`), `undone_paths`, `duration_s`, `rerun_of` (event id or null), `reason` (the person's dispute text, scanned, or null) |
| `check.unavailable` | `check_kind`, `check`, `reason` (section 4.6), `step` (`setup`, `control`, `undone`), `base_tree`, `head_tree`, `command` (or null), `exit` (or null) |
| `call.scored` | `result` (`match`, `miss`, `unscored`), `checked_by` (`runner`), `check` (the `check.ran` event id), `outcome_kind` (`common`, `uncommon`), `catch` (bool), `unscored_reason` (null, `shown-first`, `check-unavailable`), `supersedes` (an earlier `call.scored` id, or null) |
| `moment.skipped` | `moment_kind`, `how` (`chat`, `room`, `cli`), `session_skips` (count in that session) |
| `moment.closed` | `moment_kind`, `how` (a `CloseHow`), and for `fix-started` also `seen` (bool: its line was delivered or its card opened) |
| `note.posted` | `note_kind` (`revert_test`), `check` (the `check.ran` event id), `fact` (the engine's sentence), `evidence` (list of `{test, path, line}`), `printed` (`fact` when a fact line was due for it at write time, else null), `high_stakes` (glob or null) |

Rules that bind every writer:

- No source text in any body. `assert_text` and test source are never written to the record. Views read them from the snapshot store by tree, path and line.
- `check.ran` and `note.posted` are written only after `keys.KeyStore.reveal` has returned the key (section 5.1, `keys`). That is what keeps a result out of the record before the lock.
- Free text (`prompt`, `reason`, `command`) passes `events.scan_secrets` first.
- **Commits.** One commit per question, made when the question's last event is written, with the subject `question <moment-id> <outcome>` where outcome is `match`, `miss`, `unscored`, `dont-know`, `skipped` or `closed`. Other commits use other subjects: `init`, `config: <key>`, `project: <project-id>`, and `events` for anything still uncommitted when the daemon exits. A reader that wants "one commit per question" counts subjects that start with `question `.

---

## 5. Module contracts

For each module: public names only. Anything not listed is private and may change.

### 5.1 CORE

#### `record.py`

Reuses from `skills/learning-while-building/scripts/record.py`: the `git()` helper, `read_json`, `write_json`, `CONFLICT_MARKER`, `RecordError`, and the constants `INTERVALS_AFTER_SUCCESS`, `DURABLE_AFTER_DAYS`, `DEFAULT_DUE_LIMIT` (carried for step 5, unused in 2a). Copy the code. Do not import from `skills/`.

```python
FORMAT_LINE = "firsthand-record 1"

class RecordError(FirsthandError): ...                    # code "record"

def new_ulid(at: datetime | None = None) -> str            # 26 characters, Crockford base 32, sortable by time
def ensure_record(root: Path | None = None) -> Path        # default paths.record_dir(); idempotent
def read_json(path: Path) -> dict                          # raises RecordError on conflict markers or bad JSON
def write_json(path: Path, data: Mapping) -> None

class Record:
    def __init__(self, root: Path | None = None, engine: str = ENGINE) -> None   # raises RecordError if FORMAT is missing or wrong
    def append(self, type: str, body: Mapping[str, object], *, project: str | None = None,
               change: str | None = None, moment: str | None = None, surface: str | None = None,
               at: str | None = None) -> dict              # writes one event file, returns the event
    def events(self, *, types: Collection[str] | None = None, project: str | None = None,
               moment: str | None = None, since: str | None = None) -> list[dict]   # oldest first, by id
    def get(self, event_id: str) -> dict | None
    def commit(self, subject: str) -> bool                 # git add -A, commit unsigned as "firsthand <firsthand@localhost>";
                                                           # False when there was nothing to commit
    def dirty(self) -> bool
```

- `append` keeps an in-memory index, so `events` does not rescan the disk. `Record.__init__` loads the index once.
- `append` raises `RecordError` for a type not in section 4.8. It does not scan bodies: the caller scans free text.
- One writer: only the daemon process constructs a `Record` once `init` has finished.

#### `gitwatch.py`

```python
class GitError(FirsthandError): ...                        # code "git"

def project_root(cwd: str | Path) -> Path | None           # the main worktree's top level, None outside a repo
def project_id(root: Path) -> str | None                   # "prj_" + first 12 hex of sha256(root commit hash); None with no commit
def git_dirs(root: Path) -> tuple[Path, Path]              # (absolute git dir, absolute objects dir); raises GitError
def head(root: Path) -> HeadState
def is_test_path(path: str) -> bool                        # test_*.py, *_test.py, or any path part equal to "tests"
def glob_match(path: str, pattern: str) -> bool            # "**" spans folders, "*" and "?" stay inside one part,
                                                           # a pattern ending in "/" matches everything below
def first_match(paths: Iterable[str], patterns: Sequence[str]) -> str | None   # the first pattern any path matches
def split_changes(changes: Sequence[FileChange]) -> tuple[tuple[FileChange, ...], tuple[FileChange, ...]]   # (source, tests)
def runner_token(command: str) -> str | None               # "pytest" for "cd api && uv run python -m pytest -q"
def is_test_run(command: str, test_command: str | None) -> bool
```

- Every function only reads. None runs a git command that can write to the project.
- `runner_token` drops a leading `cd <dir> &&`, leading `NAME=value` words, and the wrappers `uv run`, `poetry run`, `pipenv run`, `hatch run`, `python -m`, `python3 -m`, then returns the base name of the next word. `is_test_run` is true when both commands have the same token.

#### `runner/snapshot.py`

```python
class SnapshotError(FirsthandError): ...                   # code "snapshot"

class SnapshotStore:
    def __init__(self, project_root: Path, project_id: str) -> None   # creates the bare store on first use
    def take(self) -> str                                  # the tree hash of the project as it stands
    def diff(self, base: str, head: str) -> tuple[FileChange, ...]   # sorted by path, no rename detection
    def read_file(self, tree: str, path: str) -> str | None          # None if absent, binary or over 1 MB
    def read_bytes(self, tree: str, path: str, limit: int | None = None) -> bytes | None  # [added] binary-safe read
    def checkout(self, tree: str, dest: Path) -> None      # dest must not exist or be empty
    def has(self, tree: str) -> bool
    def head_tree(self) -> str | None                      # the tree of HEAD, None with no commit
```

`take`, the recipe [measured: the project's `.git` folder was byte-identical before and after, and its object count did not change]:

1. Copy the project's index file to a fresh file under `paths.index_dir()` (an empty file if the project has none).
2. Run `git add -A` then `git write-tree` with `cwd` at the project root and `GIT_INDEX_FILE` set to that copy, `GIT_OBJECT_DIRECTORY` set to `<store>/objects`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` set to the project's objects folder.
3. Delete the copy.

`diff`, `read_file`, `checkout` and `has` run with `--git-dir=<store>` and the same alternate. `checkout` uses `read-tree` into a temporary index and `checkout-index -a` with `--work-tree=<dest>`. Ignored files are never in a snapshot. Every method raises `SnapshotError` when git fails. No method writes to the project: not the tree, the index, refs, `.git/objects` or `.git/worktrees`.

#### `runner/scratch.py`

```python
STRIPPED = (".claude", ".mcp.json", ".cursor", ".codex", ".gemini", "AGENTS.md", "CLAUDE.md",
            ".vscode", ".idea", ".devcontainer")
ENV_ALLOW = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ")

@dataclass(frozen=True)
class RunResult:
    argv: tuple[str, ...]
    exit: int | None              # None when killed at the time limit
    timed_out: bool
    duration_s: float
    output_sha256: str            # of stdout and stderr together; the output itself is dropped

class Scratch:
    def __init__(self, store: SnapshotStore, tree: str, check_id: str) -> None
    root: Path                    # paths.scratch_dir(check_id), mode 0700
    tree: Path                    # root/tree: the checkout, with STRIPPED removed
    out: Path                     # root/out: junit files
    def undo(self, base_tree: str, changes: Sequence[FileChange]) -> tuple[str, ...]
    def run(self, argv: Sequence[str], *, env: Mapping[str, str], timeout_s: float,
            cancel: threading.Event | None = None) -> RunResult
    def close(self) -> None       # deletes root; safe to call twice

def scrubbed_env(scratch: Scratch, *, python: Path | None, extra: Iterable[tuple[str, str]] = ()) -> dict[str, str]
def find_python(project_root: Path, venv_hint: str | None) -> Path | None
def source_wins(python: Path, scratch: Scratch, env: Mapping[str, str], changes: Sequence[FileChange],
                project_root: Path) -> bool
def sweep() -> int                # removes every folder under paths.scratch_root(); called at daemon start
```

- `Scratch.__init__` creates `root/tree`, `root/home`, `root/tmp`, `root/out`, checks the tree out and removes every `STRIPPED` entry at the top level. Raises `SnapshotError`.
- `undo` restores, for each given change, the base version of the file into `tree` (status M or D) or deletes it (status A). Returns the paths it touched. The caller passes only non-test changes.
- `run` starts the command in `tree` as a new process group with stdin at `/dev/null`. At `timeout_s`, or when `cancel` is set, it kills the whole group. It never raises for a failing command.
- `scrubbed_env` returns only: the `ENV_ALLOW` names copied from the daemon's environment, `HOME=root/home`, `TMPDIR=root/tmp`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=<tree>` (and `<tree>/src` first when that folder exists), `VIRTUAL_ENV` when `python` sits in a virtualenv, and the pairs in `extra`. Nothing else, so no token, cloud credential, `GH_TOKEN` or `SSH_AUTH_SOCK` can pass.
- `find_python`: `<venv_hint>/bin/python` if it exists, else `<project_root>/.venv/bin/python`, else `<project_root>/venv/bin/python`, else the first `python3` on `PATH`, else None.
- `source_wins` asks the interpreter, with the scratch environment, where the module of each changed non-test `.py` file would load from (`importlib.util.find_spec`). It returns False if any resolves inside `project_root`. A module that cannot be found is skipped. This is the "editable install" test (section 12, decision 9).

#### `runner/pytest_adapter.py`

```python
def list_tests(source: str, path: str) -> tuple[TestItem, ...]
def changed_tests(base_source: str | None, head_source: str, path: str) -> tuple[TestItem, ...]
def argv(python: Path, ids: Sequence[str], junit: Path) -> list[str]
def has_pytest(python: Path, env: Mapping[str, str], cwd: Path) -> bool
def read_junit(junit: Path, ids: Sequence[str]) -> dict[str, tuple[str, int | None]]
def classify(outcome: str) -> TestResult
```

- `list_tests`: module-level `def test_*` and `async def test_*`, and methods named `test_*` of module-level classes named `Test*`. Node ids are `path::name` and `path::Class::name`. Returns `()` on a syntax error. Items come back with `n=0` and `status="new"`.
- `changed_tests`: a test is `new` when its id is absent from the base, `edited` when `ast.dump` of its function node differs from the base (so a change in comments or blank lines is not an edit). Unchanged tests are left out. Order: new first, then edited, each in file order.
- `argv`: `[python, "-m", "pytest", *ids, "-q", "-p", "no:cacheprovider", "--junitxml=<junit>"]`. All `ids` must be in one file: the caller makes one run per test file (section 12, decision 7) [measured: with ids from two files, a file that cannot be collected makes pytest exit 4 and run none of them].
- `read_junit` returns, for each id, an outcome and a line: `("passed", None)`, `("assert", line)`, `("other", line)`, `("skipped", None)` or `("missing", None)`. Matching: a `testcase` belongs to an id when its `name`, with any `[...]` parameter suffix removed, equals the function name, and the last part of its `classname` equals the class name (for a method) or the module stem (for a function). A `testcase` with an `error` child whose message is `collection failure` makes every id of the file `("other", None)`. A missing or unreadable file makes every id `("missing", None)`.
- The exception type is the text after the final `": "` on the last non-blank line of the `failure` element's text [measured: pytest 9.2.0 writes `tests/test_a.py:4: AssertionError` there, and its `failure` element has no `type` attribute]. `AssertionError` and `Failed` give `"assert"`. Anything else, and any `error` child, gives `"other"`. The line is the number in that last line when its path ends with the test file's path.
- A parametrized test is `passed` only if every case passed, `assert` if every case that did not pass is `assert`, else `other`.
- `classify`: `passed` to `still_passes`, `assert` to `fails_on_assertion`, everything else to `cannot_run`.

#### `runner/generic_adapter.py`

```python
def test_files(changes: Sequence[FileChange]) -> tuple[TestItem, ...]    # one item per added or modified test file, at most four
def argv(test_command: str, test_file: str) -> list[str]                 # shlex.split(test_command) + [test_file]
def classify(exit_code: int | None) -> TestResult                        # 0: still_passes, else does_not_pass
```

Items have `id=path`, `name=` the file name, `line=1`, no assertion lines.

#### `moments/revert_test.py`

The five functions of `architecture.md` section 1.3, plus `run` and the reply grammar. `engine.py` reaches every moment only through these names, so 2b and 2c add modules with the same surface.

```python
KIND = "revert_test"
SKILL = 1
HEADLINE = "REVERT TEST"
BREAKS = ("test_run", "done")

@dataclass(frozen=True)
class MatchInput:
    project_id: str
    project_root: str
    task_id: str
    change_id: str
    base_tree: str
    head_tree: str
    changes: tuple[FileChange, ...]
    test_command: str | None
    high_stakes: tuple[str, ...]

@dataclass(frozen=True)
class RunContext:
    store: SnapshotStore
    project: ProjectSettings
    venv_hint: str | None
    time_limit_s: float
    on_control: Callable[[bool], None]     # called once: True when the control run passed
    cancel: threading.Event

def match(m: MatchInput, store: SnapshotStore, new_id: Callable[[], str]) -> Candidate | None
def plan(c: Candidate) -> tuple[str, ...]
def run(c: Candidate, ctx: RunContext) -> CheckOutcome
def key(c: Candidate, results: Mapping[str, tuple[TestResult, int | None]], steps: Sequence[StepRun],
        undone_paths: Sequence[str], duration_s: float, made_at: str) -> Key
def score(answer: Answer, k: Key) -> Score | None
def cue(answer: Answer, k: Key, tests: Sequence[TestItem] = ()) -> tuple[str, tuple[KeyItem, ...]] | None   # tests: section 13
def finding(k: Key) -> tuple[KeyItem, ...]
def reply_words(n_tests: int) -> tuple[str, ...]
def parse_reply(text: str, n_tests: int) -> Reply | None
```

- `match` returns None unless the diff has at least one changed non-test file and at least one added or edited test and `test_command` is set. `how` is `pytest` when `gitwatch.runner_token(test_command) == "pytest"`, else `exit_code`. Under pytest the tests come from `pytest_adapter.changed_tests` over each added or modified test file (base and head text from `store.read_file`), at most four, new ones first, numbered 1 to 4. Under the generic adapter they come from `generic_adapter.test_files`. `check_id` is `new_id()`. `high_stakes` is `gitwatch.first_match` over every changed path.
- `plan` returns the step names for logs: `("scratch", "control", "undo", "undone")`.
- `run` performs `build-2.md` section 6 steps 2 to 8 and never raises:
  1. `Scratch(ctx.store, c.head_tree, c.check_id)`. `find_python`. None gives `unavailable="no interpreter"`. Under pytest, `has_pytest` false gives `"pytest not found"`, and `source_wins` false gives `"editable install"`. Each of these ends with `step="setup"`.
  2. Control: one run per test file, junit at `out/control-<n>.xml`. Every test must be `passed` (pytest) or exit 0 (generic). Otherwise `ctx.on_control(False)` and `unavailable="does not match here"`, `step="control"`.
  3. `ctx.on_control(True)`.
  4. `scratch.undo(c.base_tree, c.source_changes)`.
  5. Undone: the same runs with junit at `out/undone-<n>.xml`. Classify each test. A test with no testcase in a junit file that exists was never run (a stop-early option, a crash): the outcome is `unavailable="does not match here"`, `step="undone"`. `pytest_adapter.argv` appends `--maxfail=0 --tb=long` after the ids, so the project's `addopts` cannot stop the run early or shorten the failure text the reader parses; the junit `message` attribute is also read for an assertion (`assert ...`, `AssertionError`, `Failed:`).
  6. `scratch.close()` in a `finally`. The whole of `run` shares one deadline of `ctx.time_limit_s`: when it passes, the outcome is `unavailable="time limit"`. When `ctx.cancel` is set the outcome is `CheckOutcome(None, None)` and nothing is recorded.
- `score`: None for `dont_know`. With several tests: a match when the picked test's result is `still_passes`, or the pick is `none` and no test's is. With one test: `fails` matches `fails_on_assertion`, `cannot_run` and `does_not_pass`. `passes` matches `still_passes`. `outcome_kind` is `uncommon` when any test still passes, else `common`. `catch` is `result == "match" and outcome_kind == "uncommon"`.
- `cue` returns the "what would have shown it" sentence and the items it cites, or None on a match. Wording in section 9.3.
- `finding` returns the tests whose result is `still_passes` or `cannot_run`.
- `reply_words(1)` is `("fails", "passes", "don't know")`. For `n >= 2` it is `("1", ..., str(n), "none", "don't know")`.
- `parse_reply` normalises (strip, lower case, inner whitespace collapsed, U+2019 to `'`, one trailing full stop removed), takes an optional trailing ` not sure` (low) or ` sure` (high), and returns None unless the rest is one of `reply_words(n_tests)`. `don't know` gives `Reply("dont_know", None)`.

#### `keys.py`

```python
class KeyStore:
    def __init__(self, directory: Path | None = None) -> None      # default paths.keys_dir(); loads the files found
    def put(self, k: Key) -> None                                  # memory and file (0600); replaces an older key of the same id
    def has(self, check_id: str) -> bool
    def reveal(self, check_id: str, moment: Moment | None, *, silent: bool = False) -> Key
    def discard(self, check_id: str) -> None                       # memory and file; no error if absent
    def pending(self) -> tuple[str, ...]

@dataclass(frozen=True)
class OutputContext:
    room_url: str | None
    work_computer: bool
    work_notice: bool             # add the one-time work computer sentence
    task_name: str
    high_stakes: str | None = None   # the matching glob, for want="fact"
    ack: str | None = None        # for want="ack": "skip", "skip2", "quiet", "quiet-today", "quiet-here", "off"

def agent_output(want: Want, *, moment: Moment | None, store: KeyStore, check_id: str | None = None,
                 silent: bool = False, ctx: OutputContext) -> str | None
```

- `reveal` is the gate. It raises `KeyLocked` unless `moment is not None and moment.state in REVEALED`, or `moment is None and silent`. It raises `KeyError` when no key is stored for the id. There is no other way to read a key's results. The engine passes `silent=True` only for a check it has decided not to ask about (section 8).
- `agent_output` is the one output rule. Every string that goes to an agent channel (a hook reply's `visible` or `context`, and CLI output when `agent` is true) is a return value of this function. Its body is section 8.3.

#### `ask.py`

```python
@dataclass(frozen=True)
class GateInput:
    dial: Dial
    quiet: bool                   # session, today or project
    pressure: bool
    asked_today: int
    daily_limit: int
    change_asked: bool
    first_prompt_turn: bool       # this turn was started by the day's first prompt
    session_stopped: bool         # two skips in this session

def gates(g: GateInput) -> str | None      # None means ask. Else the first failing gate:
                                           # "dial", "quiet", "pressure", "limit", "change", "first-prompt", "session-skips"
def fact_allowed(g: GateInput) -> bool     # dial is not off, not quiet, no pressure, not the first-prompt turn
def is_pressure(branch: str | None, prompts: Iterable[str]) -> bool
def control_word(text: str) -> str | None  # "skip", "quiet", "quiet today", "quiet here", else None
def step(state: MomentState, action: str) -> MomentState   # the table in section 8.2; raises EngineError("state")
```

`gates` passes only when the dial is `standard` or `deep`. `is_pressure` is true when the branch starts with `hotfix` or any prompt holds `urgent` or `prod is down`, case-insensitive.

#### `timeline.py`

A pure state machine. It runs no git command and writes nothing. The engine feeds it what it observed.

```python
@dataclass
class Task:
    id: str
    change_id: str
    name: str
    started_at: str
    base_tree: str
    base_at: str
    first_prompt_id: str
    prompts: list[str]
    last_test_exit: int | None = None
    test_seen: bool = False
    pending_ask: set[str] = field(default_factory=set)
    done: bool = False
    first_of_day: bool = False

@dataclass
class SessionState:
    agent: str
    session: str
    project_id: str
    project_root: str
    task: Task | None = None
    previous_base: str | None = None      # the base of the task before this one, same change
    change_id: str | None = None
    change_asked: bool = False
    fact_printed: bool = False            # for this change
    last_turn_end_tree: str | None = None
    head: HeadState | None = None
    venv: str | None = None
    skips: int = 0
    quiet: bool = False
    turn_first_of_day: bool = False

@dataclass(frozen=True)
class Observed:
    tree: str | None              # a snapshot taken for this event, when needs_snapshot said so
    head: HeadState

@dataclass(frozen=True)
class Effect:
    kind: Literal["change_ended", "task_started", "task_event", "test_passed", "done"]
    body: Mapping[str, object]

def needs_snapshot(s: SessionState, ev: SpoolEvent, test_command: str | None) -> bool
def step(s: SessionState, ev: SpoolEvent, obs: Observed, *, test_command: str | None,
         first_of_day: bool, new_id: Callable[[], str]) -> list[Effect]
```

- `needs_snapshot` is true for `prompt_submit`, for `turn_end`, and for an `after_tool` shell event that is a test run.
- `step` mutates `s` and returns effects in order:
  - **Any event:** if `obs.head` differs from `s.head` in commit or branch, emit `change_ended`, clear `task`, `change_id`, `change_asked`, `fact_printed`, `previous_base` and `last_turn_end_tree`, then set `s.head`.
  - **`session_start`, `prompt_submit`:** store `ev.venv` when present.
  - **`prompt_submit`:** if there is no task, the task is done, or a turn of the task has ended with `obs.tree` still equal to its `base_tree` and no ask pending (nothing was built: the earlier prompt was a question, not the task), start one: `change_id` kept or made, `base_tree = obs.tree`, `previous_base` set from a finished task (kept as it was when nothing was built). Emit `task_started`. Otherwise append the prompt and emit `task_event` of kind `prompt`. Set `s.turn_first_of_day = first_of_day`. The engine does not pass reply words and control words to `step`: they are not task prompts.
  - **`before_tool`:** an `ask` adds `ev.tool_use` to `pending_ask` and emits `task_event` of kind `ask`.
  - **`after_tool`, `tool_failed`:** an `ask` is removed from `pending_ask`. A test run sets `last_test_exit` (a null exit is stored as -1, so it counts as failing and is not mistaken for "no test was run"; an exit 0 with failing ids read from its output, as through `pytest -q | tail`, is stored as 1) and emits `task_event` of kind `test_run`. An `after_tool` test run with exit 0 and no failing ids also emits `test_passed` with the tree.
  - **`turn_end`:** the done signal holds when `obs.tree` differs from `last_turn_end_tree` (or from `base_tree` when there was no earlier turn end in this change), `last_test_exit` is None or 0, and `pending_ask` is empty. Then mark the task done and emit `done` with the tree. Always set `last_turn_end_tree = obs.tree`.
  - Events with no task (a tool call before any prompt was seen) are ignored, except that `turn_end` still sets `last_turn_end_tree`.

#### `words.py`

Pure functions that return the exact strings of section 9. No I/O. Listed there with their signatures.

#### `views.py`

Pure functions from the record index, the live moments and the snapshot store to the JSON-ready dicts of section 7.2. Results come only from `check.ran` events in the record, never from the key store: `views` rebuilds a `Key` from the event body (its `assert_text` is None there) and reads source lines from the snapshot store.

```python
def short_ref(moment_id: str) -> str                       # the last six characters, lower case
def inbox_view(...) -> dict
def question_view(...) -> dict
def result_view(...) -> dict | None
def journal_view(...) -> dict
def skills_view(...) -> dict
def settings_view(...) -> dict
def status_view(...) -> dict
```

Arguments are CORE's own business. The shapes returned are fixed by section 7.2. As built, every view takes a `views.ViewInput` (the record's events, the engine's moments, settings, projects, the local zone and day, the Room URL, a source reader and the question lines made by `agent_output`).

#### `engine.py`

```python
class Engine:                                              # implements EngineAPI
    def __init__(self, *, record: Record, settings: SettingsStore, room_url: str | None,
                 clock: Callable[[], datetime] | None = None,           # default: now, in UTC
                 tz: tzinfo | None = None,                               # default: the local zone; fixes "today"
                 executor: Callable[[Callable[[], None]], None] | None = None,   # default: one worker thread
                 moments: Sequence[ModuleType] | None = None,            # default: moments.REGISTRY
                 log: Callable[[str], None] | None = None) -> None
```

- With `executor=lambda fn: fn()` a check runs inside `handle`, which makes replay tests deterministic.
- With `moments=[fake]` a test can drive the whole loop without git or pytest: a fake module needs `KIND`, `SKILL`, `HEADLINE`, `BREAKS`, `match`, `run`, `score`, `cue`, `finding`, `reply_words`, `parse_reply`.
- The constructor loads `run/state.json` and the key files, so a restarted daemon resumes open questions.
- Time for timeline facts comes from `ev.at`. `clock` is used only where no spool event exists (a Room lock).

### 5.2 SHELL

#### `adapters/claude_code.py`

```python
NAME = "claude-code"
EVENTS = {"SessionStart": "session_start", "UserPromptSubmit": "prompt_submit", "PreToolUse": "before_tool",
          "PostToolUse": "after_tool", "PostToolUseFailure": "tool_failed", "Stop": "turn_end"}
MATCHER_EVENTS = ("PreToolUse", "PostToolUse", "PostToolUseFailure")
TOOL_KINDS = {"Edit": "edit", "Write": "edit", "MultiEdit": "edit", "Bash": "shell",
              "AskUserQuestion": "ask", "ExitPlanMode": "plan", "EnterPlanMode": "plan"}
HOOK_TIMEOUT_S = 5
PROCESS_NAMES = ("claude",)
ENV_MARKERS = ("CLAUDECODE",)

def to_spool(event_name: str, payload: Mapping[str, object], *, at: str, event_id: str,
             environ: Mapping[str, str]) -> dict | None
def parse_exit(error: str) -> int | None                   # from a first line "Exit code N"
def parse_failing(text: str) -> list[str]                  # lines matching ^FAILED (\S+), cut to 50 by 300
def render(event: str, reply: Mapping[str, object]) -> str
def hook_command(launcher: Path, event_name: str) -> str   # shlex.quote(str(launcher)) + " hook claude-code " + event_name
def settings_fragment(launcher: Path) -> dict              # the "hooks" object of build-2.md section 3 step 4
def skill_text() -> str                                    # the contents of claude_code_skill.md
```

- `to_spool` returns None for an unknown event name or a payload with no `session_id`. It reads only the fields listed in `build-2.md` section 4, never `transcript_path` or `last_assistant_message`, runs `events.scan_secrets` on `prompt` and `command`, and returns a dict ready for `events.encode`. `venv` is `environ.get("VIRTUAL_ENV")`.
- `render` is the only place that shapes hook stdout. For `turn_end` with a `visible` string it returns `json.dumps({"systemMessage": visible})`. For `prompt_submit` with a `context` string it returns that text, with one leading space added if it starts with `{`. In every other case it returns `""`. It never returns `decision`, `permissionDecision`, `continue` or `hookSpecificOutput`, and a string over 10,000 characters is replaced by `""`.

#### `hooks.py`

```python
def main(agent: str, event_name: str, stdin: BinaryIO, stdout: TextIO,
         environ: Mapping[str, str] | None = None) -> int
```

Always returns 0. Steps: read stdin (at most 5 MB) and parse it. Build the line with the adapter. Append it (section 4.1). If no daemon holds the lock, start one unless `FIRSTHAND_NO_DAEMON` is set. If the event is `prompt_submit` or `turn_end` and a daemon was already running, wait for the reply file (section 4.2) and write `adapter.render(...)` to `stdout`. Any exception is caught, one line goes to `paths.hook_log_file()`, nothing is printed, and the result is still 0. Nothing is ever written to stderr.

This module imports only the standard library, `firsthand.paths`, `firsthand.events`, the adapter and `daemon.spawn` (`daemon.py` keeps its own heavy imports inside functions). `cli.main` routes the `hook` command before importing anything else, so a hook costs one interpreter start and a few small imports.

#### `daemon.py`

```python
@dataclass(frozen=True)
class DaemonContext:
    record_dir: Path
    room_url: str | None

class Daemon:
    def __init__(self, *, engine_factory: Callable[[DaemonContext], EngineAPI] | None = None,
                 room_factory: Callable[[EngineAPI, int], object] | None = None,
                 idle_exit_s: float = 1800.0, poll_s: float = 0.05) -> None
    def run(self) -> int                    # 0 on a clean exit, 0 at once if another daemon holds the lock
    def stop(self) -> None                  # asks run() to return; safe from any thread

def is_running() -> bool
def spawn() -> bool                         # start a detached daemon; False if one is running
def main() -> int                           # the "firsthand daemon" command: Daemon().run()
```

- Default factories: the engine is `Engine(record=r, settings=ConfigStore(commit=r.commit), room_url=...)` with `r = Record()`. The Room is `firsthand.room.server.RoomServer(engine, port=<port file value>)`. A room factory returns an object with `port`, `url`, `start()`, `shutdown()`, `clients()` and `new_ticket(next_path)`. If binding fails the daemon runs with no Room and `room_url=None`.
- `run`: take the lock, `paths.ensure_private_dirs()`, `runner.scratch.sweep()`, build the engine and the Room, listen on the control socket, write `daemon.json`, then loop as in section 8.1. At exit: `engine.close()`, shut the Room down, remove the socket and `daemon.json`.
- `spawn` starts, with the caller's environment, `sys.executable` running `firsthand.cli.main(["daemon"])` with the same package folder first on `sys.path`, `start_new_session=True`, stdin at `/dev/null`, stdout and stderr appended to `paths.daemon_log_file()`, and `close_fds=True`. It does not wait.
- Idle exit: when `engine.idle()` has been true, no spool event has arrived and the Room has had no SSE client for `idle_exit_s`.
- The daemon ignores `SIGHUP` and exits cleanly on `SIGTERM` and `SIGINT`.

#### `client.py`

```python
class DaemonUnavailable(FirsthandError): ...            # code "unavailable"
class RemoteError(FirsthandError): ...                  # carries the daemon's error code and message

def call(op: str, args: Mapping[str, object] | None = None, *, cwd: str | None = None, agent: bool = False,
         start: bool = True, timeout_s: float = 5.0) -> dict
```

With `start=True` and no daemon, `call` spawns one and retries the connection for up to three seconds. Raises `DaemonUnavailable` or `RemoteError`.

#### `config.py`

```python
class ConfigStore:                                       # satisfies SettingsStore
    def __init__(self, record_dir: Path | None = None, commit: Callable[[str], object] | None = None) -> None
    def load(self) -> Settings
    def set(self, key: str, value: object) -> Settings
    def project(self, project_id: str) -> ProjectSettings | None
    def ensure_project(self, project_id: str, root: str) -> ProjectSettings
    def set_project(self, project_id: str, key: str, value: object) -> ProjectSettings

def detect_test_command(root: Path) -> str | None
def read_port() -> int | None
def choose_port() -> int                                 # a free loopback port, written to paths.port_file()
```

- `set` and `set_project` validate against section 4.5 and raise `EngineError("invalid")` with a message that names the allowed values. After writing they call `commit("config: <key>")` or `commit("project: <id>")` when a `commit` function was given. The daemon passes `Record.commit`. `init` passes its own.
- `ensure_project` creates the project file when absent: `name` is the root folder's name, `test_command` from `detect_test_command`, `high_stakes` from `DEFAULT_HIGH_STAKES`. It adds `root` to `roots` when missing.
- `detect_test_command` returns `"pytest -q"` when the root has `[tool.pytest.ini_options]` in `pyproject.toml`, or a `pytest.ini`, `tox.ini` or `conftest.py`. Else None.
- `set_project(id, "high_stakes_add", glob)` and `"high_stakes_remove"` edit the list. `"test_command"`, `"quiet"` and `"name"` replace values.

#### `install.py`

```python
class InstallError(FirsthandError): ...                  # code "install"

@dataclass(frozen=True)
class PlannedWrite:
    path: Path
    existed: bool
    summary: str                 # "adds 6 hooks that call <launcher>" or "new folder"
    old: bytes | None
    new: bytes

@dataclass(frozen=True)
class UninstallReport:
    restored: tuple[Path, ...]
    removed: tuple[Path, ...]
    refused: tuple[tuple[Path, str], ...]     # a file changed since install, with a unified diff

def install_engine(version: str) -> Path                 # returns the launcher path
def merge_hooks(settings_text: str | None, fragment: Mapping[str, object]) -> str
def plan(launcher: Path) -> list[PlannedWrite]
def diff_text(w: PlannedWrite) -> str
def apply(writes: Sequence[PlannedWrite], *, launcher: Path, stamp: str) -> Path   # returns the backup folder
def uninstall() -> UninstallReport
```

- `install_engine` copies the running `firsthand` package folder to `engine/<version>/lib/firsthand` and writes `engine/<version>/bin/firsthand` (mode 0755): a Python script whose first line is `#!<real path of the base interpreter> -IS` and which puts `engine/<version>/lib` first on `sys.path` and calls `firsthand.cli.main()`. Idempotent. No network, no pip (section 12, decision 14).
- `merge_hooks` parses the existing text (None or empty means `{}`), raises `InstallError` when it is not a JSON object, removes every handler whose command contains ` hook claude-code ` from every event, appends the fragment's groups, keeps every other key and entry, and returns `json.dumps(indent=2)` plus a newline.
- `plan` returns the writes for `paths.claude_settings()` and `paths.claude_skill_file()`. It writes nothing.
- `apply` copies each existing file byte for byte into `backups/<stamp>/`, writes the new bytes, and writes the manifest (section 4.5). If a manifest already exists, a file whose current hash equals its `sha256_after` keeps its original backup and `sha256_before`.
- `uninstall` restores each file whose current hash equals `sha256_after` (or deletes it and its now-empty folders when it did not exist before), refuses any other file and returns its diff, and removes the manifest only when nothing was refused. It never touches the record.
- Nothing in this module writes outside `paths.claude_dir()`, `paths.config_home()` and `paths.home()`.

#### `cli.py`

```python
def main(argv: Sequence[str] | None = None) -> int
def under_agent(environ: Mapping[str, str] | None = None, ancestors: Sequence[str] | None = None) -> bool
```

`under_agent` is true when any adapter `ENV_MARKERS` name is set to a non-empty value other than `0`, or a parent process up the tree has a name in `PROCESS_NAMES` (read from `/proc/<pid>/stat` on Linux, `ps -o ppid=,comm=` elsewhere, at most 16 levels). Both inputs can be passed in, so a test does not depend on what started it.

| Command | Behaviour | Exit |
| :- | :- | :- |
| `hook claude-code <Event>` | `hooks.main` | Always 0 |
| `daemon` | `daemon.main` | 0 |
| `init [--yes] [--work-computer yes\|no] [--test-command CMD]` | `build-2.md` section 3. Without a terminal on stdin and without `--yes` it prints the plan and the line `Run again with --yes to write these files.` and writes nothing. Stops a running daemon first. Prints the install copy of section 9.5 | 0, or 1 on `InstallError` |
| `room [--tty]` | Asks the daemon for a one-time URL and opens it with `webbrowser`. Prints the URL only if no browser could be opened and `under_agent()` is false. `--tty` prints the open question as text and reads one answer line | 0, or 1 |
| `answer <text...>`, `skip` | The control ops of the same name. Prints `result["lines"]` | 0, or 1 with the error message and the fix |
| `status` | Prints the status view: open question line, asked today, dial, test command, daemon state. With `start=False`: a stopped daemon is reported, not started | 0 |
| `journal`, `skills` | Text forms of those views. Refused under an agent | 0, or 1 |
| `quiet [session\|today\|here]`, `off`, `on` | `quiet` and `settings_set` (`dial`). `on` restores `dial_before_off` | 0, or 1 |
| `config test-command "<cmd>"`, `config high-stakes "<glob>"` | `settings_set` on the project at the current folder | 0, or 1 |
| `uninstall` | `install.uninstall`, prints what was restored, any diff, and where the record is | 0, or 1 if anything was refused |

Every error message ends with the one reply or command that fixes it. `off` prints the Off line of `experience.md` section 6.4.

#### The skill text (`adapters/claude_code_skill.md`)

Frontmatter: `name: firsthand`, `description:` one sentence under 1,536 characters that says when it applies (a message that starts with "Firsthand"), `user-invocable: false`. Body, in plain statements:

- A block that starts with the line `model.PRINT_PREFIX` (section 2.1) is followed by lines to print to the person exactly as they are, with nothing added. The file holds that line word for word, and a SHELL test compares the two.
- A line that starts `Firsthand finding:` is a fact about the work in progress. Use it. Do not print it as your own claim about the person.
- If the person types a `firsthand ...` command as a message, run it and print its output unchanged.
- "skip" is final. Do not ask why and do not bring the question back.
- Never answer a Firsthand question for the person, never run `firsthand answer` unless the person typed the answer, never read anything under `~/.firsthand`.

#### `pyproject.toml`

Adds `[build-system]` (setuptools, a build-time requirement only), `[project]` (`name = "firsthand"`, `version = "0.1.0"`, `requires-python = ">=3.11"`, `dependencies = []`), `[project.scripts]` (`firsthand = "firsthand.cli:main"`), package discovery limited to `firsthand*`, package data for `room/page.html`, `room/static/*` and `adapters/*.md`, and `"firsthand"` in `[tool.vulture] paths`. The comment at the top of the file that says the repo ships no package is updated. The licence field is left as the repo stands (section 12, decision 22).

### 5.3 ROOM

#### `room/server.py`

Starts from `skills/learning-while-building/scripts/room.py`: the `ThreadingHTTPServer` shape, the quiet `log_message`, `MAX_BODY_BYTES = 20_000`, `MAX_ANSWER_CHARS = 4000`, `Cache-Control: no-store`, and one write lock around every POST.

```python
MAX_BODY_BYTES = 20_000
MAX_ANSWER_CHARS = 4000
TICKET_TTL_S = 60
SESSION_TTL_S = 30 * 24 * 3600

class RoomServer:
    def __init__(self, engine: EngineAPI, *, port: int, host: str = "127.0.0.1",
                 sessions_file: Path | None = None, clock: Callable[[], float] = time.time) -> None
    port: int                                  # the bound port (useful when 0 was asked for)
    url: str                                   # "http://127.0.0.1:<port>"
    def new_ticket(self, next_path: str = "/") -> str      # the full one-time URL
    def start(self) -> threading.Thread        # serve in a daemon thread
    def shutdown(self) -> None
    def clients(self) -> int                   # open event streams

def handle(server: RoomServer, method: str, path: str, headers: Mapping[str, str], body: bytes) -> Response
```

- The constructor binds and raises `OSError` when the port is taken. `host` other than `127.0.0.1` raises `ValueError`.
- `handle` is the whole request path as a pure function of its arguments and the server's state, so tests need no socket. `Response` is a small dataclass: `status`, `headers`, `body` (bytes), and `stream` (true for the event stream).
- `sessions_file=None` keeps sessions in memory (tests). The daemon passes `paths.room_sessions_file()`. ROOM takes that path as an argument and does not import `firsthand.paths`.
- Engine errors: any exception with string attributes `code` and `message` becomes the error body of section 7.1. Any other exception becomes 500 with code `internal` and no detail.

#### `room/page.html`, `room/static/room.css`, `room/static/room.js`

- `page.html` is a shell: the top bar, the tab row (Inbox, Journal, Skills, and Settings in the bar), one `<main>`, the footer line "Served by this computer at 127.0.0.1.", and one polite live region. It links `/static/room.css` and `/static/room.js` and holds no inline script or style.
- `room.css` begins with the token block of `design/learning-experience/assets/room.css` (from `:root{` through the `.lvw` rule), copied unchanged, followed by the component rules lifted from `prototypes/revert.html` and `prototypes/inbox.html`: `.top`, `.bar`, `.tabs`, `.tab`, `.main`, `.card`, `.eb`, `.ctx`, `.lead`, `.ev`, `.q`, `.picks`, `.pill`, `.lock`, `.sure`, `.foot`, `.rh`, `.rt`, `.chip`, `.rw`, `.cue`, `details.more`, `.grp`, `.it`, `details.note`, `.close`, `.btn`, `.tbtn`, and the 640px and reduced-motion rules. The prototype controls (`.proto`), the grain image and the web font links are not used: no font, image or script is loaded from anywhere but this server.
- `room.js` renders, from the JSON of section 7.2 and nothing else: the Inbox (Now, Notes, Results and the closing line), the question card with lock on pick, Undo, the How sure row and Show the result, the result with More, Wrong start and This result looks wrong, the Journal, the Skills row, and Settings. Every string from the API is set with `textContent`, never as markup. Fixed labels (button names, group headings) come from `experience.md` sections 7.2 to 7.4 and 7.9.
- Routes in the browser: `/`, `/q/<ref>`, `/r/<ref>`, `/journal`, `/skills`, `/settings`. `/q/<ref>` shows the card until a result exists, then the result. `/r/<ref>` shows the result, or the card if none exists yet.
- Accessibility items that apply in 2a (`experience.md` section 12): a card is a `form` labelled by its prompt, picks are radios in a `fieldset`, the chip word comes first in a result's accessible name, targets are 44px, no letter shortcut exists, one live region line per state change ("Locked.", "Skipped.", the chip and the fact).
- States with fixed copy: no session (`This page needs a session. Run: firsthand room`), and a lost event stream (`The Room cannot reach Firsthand on this computer. Start it with: firsthand room`).

---

## 6. Who calls whom

```
Claude Code hook --> hooks.main --> adapters.claude_code.to_spool --> events.encode --> run/spool.jsonl
                         |                                                                  |
                         | waits <= 300 ms for run/out/<id>.json                            v
                         +<------------ daemon writes reply file <----- engine.handle(ev, reply)
                                                                          |   timeline.step
firsthand <command> --> client.call --> control socket --> daemon ------->|   moments.revert_test.match / run
browser --> room.server.handle ------------------------------------------>|   keys.KeyStore, keys.agent_output
                                                                          |   record.Record.append / commit
                                                                          v   views.*, words.*
                                                                     run/state.json, run/keys, record/
```

---

## 7. The Room HTTP API

### 7.1 Checks on every request, in this order

1. `Host` must be `127.0.0.1:<port>` or `localhost:<port>`. Else 403 `forbidden`.
2. `/static/*`, `/enter` and the page routes need no session. Every `/api/*` route needs a valid `fh_session` cookie. Else 401 `no_session`.
3. A POST also needs `Origin` equal to `http://127.0.0.1:<port>` or `http://localhost:<port>` (a missing Origin fails), the header `X-Firsthand-Token` equal to the session's token, `Content-Type: application/json`, and a body of at most `MAX_BODY_BYTES` that parses to a JSON object. Else 403 `forbidden`, 413 `too_large` or 400 `bad_request`.

Every response carries `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` and `Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`. No response carries any `Access-Control-*` header.

Error body, for every non-2xx JSON response:

```json
{"error": {"code": "state", "message": "This question is already locked."}}
```

| Engine or request code | Status |
| :- | :- |
| `bad_request`, `invalid` | 400 |
| `no_session` | 401 |
| `forbidden`, `refused` | 403 |
| `not_found`, `no_question` | 404 |
| `state`, `confirm` | 409 |
| `too_large` | 413 |
| anything else | 500, code `internal` |

### 7.2 Routes

Routes added to the list in `build-2.md` section 8 are marked [added]. The reasons are in section 12, decision 16.

**Pages and session**

| Route | Response |
| :- | :- |
| `GET /`, `GET /q/<ref>`, `GET /r/<ref>`, `GET /journal`, `GET /skills`, `GET /settings` | 200, `page.html`. No data in it |
| `GET /static/room.css`, `GET /static/room.js` [added] | 200 with the right content type. Any other name is 404 |
| `GET /enter?t=<ticket>&next=<path>` [added] | A ticket is single use and lasts `TICKET_TTL_S`. Valid: 303 to `next` (it must start with one `/` and is `/` otherwise) with `Set-Cookie: fh_session=<id>; HttpOnly; SameSite=Strict; Path=/`. Invalid: 403, a plain page that says `This link has been used or has expired. Run: firsthand room` |
| `GET /api/session` [added] | `{"token": "<per-session token>", "room": "http://127.0.0.1:4127"}` |
| `GET /api/events` | `text/event-stream`. One message per engine notice: `data: {"seq": 12, "topic": "inbox", "id": null}`. A comment line `: keep` every 15 seconds. The page refetches what the topic names |

**Reads** (each is the engine view of the same name, returned as is)

`GET /api/inbox?project=<id>`:

```json
{"project": {"id": "prj_3b9f52c1a7e0", "name": "orbit-pay"},
 "projects": [{"id": "prj_3b9f52c1a7e0", "name": "orbit-pay"}],
 "state": {"dial": "standard", "quiet": null, "notice": null},
 "now": [{"id": "01JC8Y2F7H3QZ5W8N1P4R6T9KD", "ref": "r6t9kd", "reason": "Your agent finished",
          "task": "idempotent refunds", "size": "One tap", "href": "/q/r6t9kd"}],
 "notes": [{"id": "01JC8Z...", "at": "2026-11-14T11:42:00Z", "time": "11:42",
            "title": "test_refund_response_is_stable passes with the change undone",
            "text": "tests/test_refunds.py::test_refund_response_is_stable passes with the change undone.",
            "evidence": [{"test": "tests/test_refunds.py::test_refund_response_is_stable", "path": "tests/test_refunds.py", "line": 41}],
            "printed": false, "checked": "Checked by a run, no model."}],
 "older_notes": 0,
 "results": [{"id": "01JC8Y...", "ref": "r6t9kd", "kind": "Revert test", "task": "idempotent refunds",
              "chip": "matched", "chip_label": "Matched", "href": "/r/r6t9kd"}],
 "closing": "Asked today: 1 of 1.",
 "empty": null}
```

- `project` is null and the lists are empty before any project has been seen. `empty` is then the first-visit line of `experience.md` section 3.3, else null.
- `state.quiet` is null, `"session"`, `"today"` or `"here"`. `state.notice` is null or one of the shell lines of `experience.md` section 7.1 (off, quiet).
- `now` holds at most one item: a moment in `open` or `held`.
- `notes` holds the newest five `note.posted` events. `older_notes` counts the rest. A note's `printed` is true only when a `line_delivered` event shows its fact line reached the agent.
- `results` holds moments in `sealed`, `settled`, `skipped` or `closed` whose result the person has not opened. `chip` is `matched`, `did_not_match`, `not_scored` or `pending` (sealed, the check still running, label `Locked`).

`GET /api/q/<ref>`:

```json
{"id": "01JC8Y2F7H3QZ5W8N1P4R6T9KD", "ref": "r6t9kd", "kind": "revert_test", "state": "open",
 "reason": "Your agent finished", "skip_ok": true,
 "context": "Verification | orbit-pay | idempotent refunds | change since 09:12",
 "lead": "It added 3 tests. Read them first.",
 "evidence": [{"n": 1, "id": "tests/test_refunds.py::test_same_key_refunds_once", "name": "test_same_key_refunds_once",
               "path": "tests/test_refunds.py", "line": 18, "status": "new",
               "asserts": [{"line": 23, "text": "assert len(ledger.refunds(charge)) == 1"}],
               "source": "def test_same_key_refunds_once(...):\n    ..."}],
 "prompt": "Which of them would still pass with the change undone?",
 "picks": [{"value": "1", "label": "1"}, {"value": "2", "label": "2"}, {"value": "3", "label": "3"},
           {"value": "none", "label": "None"}, {"value": "dont_know", "label": "Don't know"}],
 "footer": "Checked by a run: the change undone, the tests kept.",
 "line": "Firsthand (skip ok): your agent finished and added 3 tests. ...",
 "can": {"lock": true, "undo": false, "confidence": false, "show": false, "skip": true,
         "wrong_start": true, "dispute": false},
 "held": null,
 "call": null,
 "status_line": null,
 "say": null,
 "result": null}
```

- `evidence[].asserts` and `source` are read from the head snapshot. `source` is the test function's text, at most 200 lines. Both are omitted when the snapshot has been pruned. Under the generic adapter `asserts` is empty.
- `held` is null or `{"kind": "pick", "answer": "2", "confidence": "high"}` or `{"kind": "skip"}`.
- `call` is null or `{"answer": "2", "label": "2, test_refund_response_is_stable", "confidence": "high", "confidence_label": "Sure", "channel": "room", "at": "..."}`. It is set from `sealed` on.
- `status_line` is null or one of the state lines of `experience.md` section 7.3: `Locked. The check is still running.`, `You moved on, so nothing was scored.`, `This was printed in your agent as a fact, so the question is closed.`, `The check could not finish, so there is nothing to show. Nothing was scored.`, `The check took longer than 2 minutes, so I dropped it. Nothing was scored.`
- `say` is null on a read. On the response to an action it is the list of lines a text channel prints next (the chat form of the result, the pending line, or the skip line), or null. The Room ignores it.
- **`result` is null unless `state` is in `REVEALED` and a `check.ran` event exists for the moment.** The Room never has to decide this: it shows what it is given.

`result`, when present:

```json
{"headline": "REVERT TEST", "chip": "matched", "chip_label": "Matched", "reason": null,
 "you_said": "2, test_refund_response_is_stable. Sure.",
 "what_happened": ["It still passes with the change undone.", "It would pass whether or not the change exists."],
 "cue": null,
 "back": "Back to: idempotent refunds. Next: read the summary.",
 "more": {"rows": [{"id": "tests/test_refunds.py::test_same_key_refunds_once", "name": "test_same_key_refunds_once",
                    "text": "fails on its assertion"}],
          "checked": "Checked by a run, no model.",
          "commands": ["python -m pytest tests/test_refunds.py::test_same_key_refunds_once ... -q -p no:cacheprovider"],
          "counts": "Your calls of this kind: 5 of 7 matched. Always answering \"none\" would have scored 4 of 7.",
          "sure": null,
          "sent": "Sent to your agent: \"tests/test_refunds.py::test_refund_response_is_stable passes with the change undone.\"",
          "dispute": null}}
```

- `chip` is `matched`, `did_not_match` or `not_scored`. `reason` is the one line that explains a `not_scored` chip.
- `cue` is null or `{"text": "Its only assertion is at tests/test_refunds.py:41.", "evidence": [{"path": "tests/test_refunds.py", "line": 41, "text": "assert resp.status_code == 200"}]}`.
- `more.sure` is null until a band holds five scored calls. `more.sent` is null when nothing was sent. `more.dispute` is null or the outcome line of a dispute (section 9.3).

`GET /api/journal?project=<id>&limit=<n>`:

```json
{"scope": "orbit-pay",
 "entries": [{"id": "01JC8Y...", "at": "2026-11-14T09:41:11Z", "date": "14 Nov", "task": "idempotent refunds",
              "kind": "Revert test", "chip": "matched", "chip_label": "Matched", "href": "/r/r6t9kd",
              "rows": [{"label": "You said", "text": "2, test_refund_response_is_stable. Sure."},
                       {"label": "What happened", "text": "It still passes with the change undone. Checked by a run."}]},
             {"id": "01JC8Z...", "at": "2026-11-14T11:42:00Z", "date": "14 Nov", "task": "retry backoff",
              "kind": "Note", "chip": null, "chip_label": null, "href": null,
              "rows": [{"label": "Fact", "text": "tests/test_retry.py::test_backoff passes with the change undone."}]}]}
```

Newest first. One entry per settled, skipped or closed question and per note.

`GET /api/skills?project=<id>` [added]:

```json
{"rows": [{"n": 1, "name": "Verification", "level": "too_few", "level_line": "Too few calls. 1 of 2.",
           "counts": "Your calls of this kind: 1 of 1 matched.",
           "fixed": "Always answering \"none\" would have scored 0 of 1.",
           "asked": "Asked 2. Answered 1. Don't know 0. Skipped 1.",
           "newest": "newest call today",
           "covers": "Telling a test that proves a change from one that would pass anyway.",
           "no_evidence": "Checking work that has no tests.",
           "checked": "Checked by a run."}]}
```

One row in 2a. `level` is `too_few` or `shown`. `shown` needs two matched scored calls on different local days, one of them a catch, and its `level_line` is `Shown since 9 Nov.`

`GET /api/settings?project=<id>` [added]:

```json
{"dial": "standard", "daily_limit": 1, "findings_to_agent": true, "work_computer": true,
 "quiet": {"today": false, "here": false},
 "project": {"id": "prj_3b9f52c1a7e0", "name": "orbit-pay", "test_command": "pytest -q",
             "high_stakes": ["**/migrations/**", "refunds/**"], "check_time_limit_s": 120},
 "record": "~/.firsthand/record"}
```

**Writes.** Each `q` route returns the question view after the action.

| Route | Body | Engine call |
| :- | :- | :- |
| `POST /api/q/<ref>/lock` | `{"answer": "2"}` (a pick value, at most `MAX_ANSWER_CHARS`) | `lock(ref, answer, channel="room", final=False)`. `dont_know` seals at once |
| `POST /api/q/<ref>/undo` [added] | `{}` | `undo(ref)` |
| `POST /api/q/<ref>/confidence` | `{"value": "high"}`, `"low"` or `null` | `confidence(ref, value)` |
| `POST /api/q/<ref>/show` [added] | `{}` | `show(ref)` |
| `POST /api/q/<ref>/skip` | `{}` | `skip(ref, channel="room", final=False)` |
| `POST /api/q/<ref>/wrong-start` | `{}` | `wrong_start(ref)` |
| `POST /api/q/<ref>/dispute` | `{"reason": "..."}` | `dispute(ref, reason)` |
| `POST /api/settings` | `{"changes": {"dial": "notes"}, "project": "prj_...", "confirm": false}` | `set_settings(changes, project=..., source="room", confirm=...)`. Returns the settings view. A widening change without `confirm` is 409 `confirm`, and the page asks for the second click |

Keys accepted in `changes`: `dial`, `daily_limit`, `findings_to_agent`, `quiet_today` (bool), and with `project`: `test_command`, `quiet`, `high_stakes_add`, `high_stakes_remove`.

---

## 8. The loop

### 8.1 The daemon process (`daemon.py`, SHELL)

```
run():
    take run/daemon.lock, or return 0
    ensure_private_dirs(); scratch.sweep()
    engine = engine_factory(ctx); room = room_factory(engine, port); room.start()
    listen on control_socket(); write run/daemon.json
    offset = read run/spool.offset (0 if missing or past the end of the file)
    waiting = {}                          # event id -> (time the reply file was written, whether it holds text)
    loop until stop:
        wait up to poll_s for the control socket to be readable
        for each waiting control connection:
            read one request line, dispatch it (section 4.4), write one response line, close
        for ev in read_spool(offset):     # section 4.1
            engine.handle(ev, reply=write_reply)
            offset = ev's end; save offset
        truncate the spool if fully read
        engine.tick()
        for each id in waiting written at least 1.0 s ago:
            if it holds text: confirm delivery (section 4.2); engine.delivered(id, ok)
            else: delete the file if it is still there
        if idle for idle_exit_s: stop
    engine.close(); room.shutdown(); remove socket and daemon.json

write_reply(r: HookReply):               # may be called from the check thread: guard `waiting` with a lock
    paths.write_private(paths.reply_file(r.event_id), json of section 4.2)
    waiting[r.event_id] = (now, bool(r.visible or r.context))
```

`engine.handle` can take as long as a snapshot takes. The control socket and the Room are answered between events, and Room requests run on their own threads against the engine's lock.

### 8.2 The engine (`engine.py`, CORE)

State per project: at most one live moment (`open`, `held` or `sealed`), at most one running check, one queued check. State per session: a `timeline.SessionState`, the tree of its last done signal, a queue of agent-only lines, the text of a fact line that is due, and a reply being deferred.

```
handle(ev, reply):
    if ev.id in seen_ids: return
    root = gitwatch.project_root(ev.cwd); pid = project_id(root)
    if no project, or the dial is off:
        if ev.event in (prompt_submit, turn_end): reply(empty)
        return
    P = project state; S = session state for (ev.agent, ev.session, pid)
    proj = settings.ensure_project(pid, root)
    replied = False

    if ev.event == prompt_submit:
        consumed, context = on_prompt_fast(P, S, ev)       # no git here
        reply(HookReply(context=context)); replied = True  # early: the prompt is not held up by a snapshot
        if consumed: checkpoint(); return                  # a reply word is not a task prompt
    if ev.event == turn_end and not may_speak(P, S):
        reply(empty); replied = True                       # early: nothing can be said at this stop

    obs = Observed(tree = store.take() if timeline.needs_snapshot(S, ev, proj.test_command) else None,
                   head = gitwatch.head(root))
    for fx in timeline.step(S, ev, obs, ...):
        change_ended -> end_change(P, S)
        task_started -> record task.started
        task_event   -> record task.event
        test_passed  -> start_check(P, S, fx.tree)
        done         -> record task.event(done); S.done_tree = fx.tree
                        start_check(P, S, fx.tree); try_offer(P, S, ev)

    if ev.event == turn_end and not replied:
        if S's check is in its control run on S.done_tree and has not been decided:
            defer the reply for 250 ms                     # the check thread or tick() answers it
        else:
            reply(HookReply(visible=stop_line(P, S, ev)))
    checkpoint()

on_prompt_fast(P, S, ev) -> (consumed, context):
    printable = []; consumed = False
    m = P.moment
    if m and m.state == held: settle_held(P, S, m)         # the person moved on: a held pick is sealed,
                                                           # a held skip becomes final
    if m and m.state == open:
        r = module.parse_reply(ev.prompt, len(m.tests)); word = ask.control_word(ev.prompt)
        if r:                                              # a reply word
            printable += [seal(P, S, m, r.answer, r.confidence, channel="chat", at=ev.at)]; consumed = True
        elif word == "skip":
            printable += [skip_final(P, S, m, how="chat")]; consumed = True
        elif word in ("quiet", "quiet today", "quiet here"):
            printable += [set_quiet(P, S, word)]; consumed = True      # closes m as "quiet"
        elif m.seen:
            close(P, S, m, "moved-on")
        # an unseen open question stays open (decision 11)
    agent_only = the lines queued for S                    # findings; each was made by agent_output when queued
    return consumed, words.context_text(printable, agent_only)

seal(P, S, m, answer, confidence, channel, at) -> str | None:        # returns what a text channel says next
    m.state = ask.step(m.state, "seal"); store the answer, confidence and channel on m
    record call.sealed; record call.confidence if one was given
    said = revealed(P, S, m)
    return said or agent_output("pending", moment=m, ...)

skip_final(P, S, m, how) -> str:
    m.state = skipped; S.skips += 1; record moment.skipped
    revealed(P, S, m)
    return agent_output("ack", ctx with ack = "skip2" if S.skips >= 2 else "skip")

close(P, S, m, how):
    m.state = closed; m.close_how = how; record moment.closed
    revealed(P, S, m)

revealed(P, S, m) -> str | None:                           # called whenever a moment enters sealed, skipped or closed
    if keystore.has(m.id): return release(P, S, P.check)
    if the check is over with no key (unavailable, cancelled, replaced): commit("question <id> <outcome>")
    return None                                            # else on_finished will call release

may_speak(P, S) -> bool:                                   # cheap, no git
    a fact line is due for S, or P.moment is open and unseen and belongs to S,
    or S's task has a check that is running or finished and has not been decided,
    or this stop may be the done signal: S's task is not done, no ask is pending and
    its last test run exited 0 or none ran                 # [integration] see section 13

start_check(P, S, tree):
    if proj.test_command is None: return
    cand = module.match(MatchInput(base_tree=S.task.base_tree, head_tree=tree,
                                   changes=store.diff(base, tree), ...), store, new_ulid)
    if cand is None: return
    if P.check and P.check.head_tree == tree and P.check.task == S.task.id: return   # already on it
    if P.check belongs to the same task: cancel it, keystore.discard(its id)
    else if a check of another task is running: queue this one behind it      # one check at a time per project
    P.check = Check(cand, status="control")
    executor(lambda: worker(P, S, cand))

worker(P, S, cand):                                        # off the main thread; takes the lock only in callbacks
    outcome = module.run(cand, RunContext(on_control=lambda ok: on_control(P, S, cand, ok), ...))
    on_finished(P, S, cand, outcome)

on_control(P, S, cand, ok):
    P.check.status = "undoing" if ok else "failed"
    if ok: try_offer(P, S, None)

try_offer(P, S, ev):                                       # ask, or decide not to. It never looks at a result
    c = P.check
    if c is None or c.decided or c.status == "control" or c.head_tree != S.done_tree: return
    c.decided = True
    reason = ask.gates(GateInput(...)) if P.moment is None else "change"
    if reason is None:
        m = Moment(id=c.check_id, state="open", ...); P.moment = m; S.change_asked = True
        m.offered_in = the event being handled, if any     # so this stop can carry its line
        record moment.offered; notify("inbox")
    else:
        c.silent = True                                    # this check will never be asked about
        if keystore.has(c.check_id): release(P, S, c)
    answer a deferred reply for S, if there is one, with stop_line(P, S, its event)

on_finished(P, S, cand, outcome):
    if outcome is cancelled: return
    m = P.moment if P.moment and P.moment.id == cand.check_id else None
    if outcome.unavailable:
        record check.unavailable
        if m and m.state in (open, held): close(P, S, m, "check-dropped")
        elif m and m.state == sealed:
            record call.scored(unscored, check-unavailable); m.state = settled
            commit("question <id> unscored")
        return
    keystore.put(outcome.key); P.check.status = "finished"
    if m and m.state in REVEALED: release(P, S, P.check)   # sealed, skipped or closed while the check ran
    elif m is None and P.check.silent: release(P, S, P.check)
    # else: the key waits in the store. Nothing reads it

release(P, S, c) -> str | None:                            # the only place a result leaves the key store
    m = the moment for c, or None
    k = keystore.reveal(c.check_id, m, silent=c.silent)    # raises KeyLocked if this is too early
    ran = record check.ran
    said = None
    if m and m.state == sealed:
        sc = module.score(m.answer, k)
        if sc: record call.scored(sc, check=ran.id)
        m.state = settled
        if m.channel == "chat": said = agent_output("result", moment=m, store=keystore, ctx=...)
    found = module.finding(k)
    fact = k has a still_passes test and c.high_stakes and not S.fact_printed
           and (m is None or m.state in (skipped, closed))            # nobody answered
    if found and (m is None or fact): record note.posted(printed = "fact" if fact else None)
    if found and settings.findings_to_agent and not (m and m.channel == "chat"):
        queue for S: agent_output("finding", moment=m, store=keystore, check_id=c.check_id, silent=c.silent, ctx=...)
    if fact: S.fact_due = agent_output("fact", ...)        # the text is made now and sent at a later stop
    keystore.discard(c.check_id)
    if m: record.commit("question <id> <outcome>")
    notify("inbox"); notify("question", m.id if m else None)
    return said

stop_line(P, S, ev) -> str | None:                         # one stop carries at most one line
    m = P.moment if it is open, unseen and belongs to S, else None
    1. if m was offered while handling ev: return agent_output("question", moment=m, ...)
    2. if m and its check is high stakes and finished:
           close m and release its check, then record moment.closed with how = "shown-first" if that
           set S.fact_due, else "unseen"; m = None         # decision 12: this never depends on what the key holds
    3. if S.fact_due and ask.fact_allowed(...): return S.fact_due
    4. if m, on the same change and local day, and quiet, pressure, dial and first-prompt gates still pass:
           return agent_output("question", moment=m, ...)
    return None

delivered(event_id, ok):
    for each item the reply carried:
        question -> if ok: m.seen = True; record task.event(line_delivered)
        fact     -> if ok: S.fact_printed = True; S.fact_due = None; record task.event(line_delivered)
        finding  -> if ok: drop it from the queue; record task.event(line_delivered)
        result   -> if ok: m.opened = True                 # the person has it in chat
    # not ok: the item stays where it was and goes out with the next reply that can carry it

tick():
    answer every deferred reply older than 250 ms with stop_line(...)
    close unseen questions whose local day has ended, as "unseen"

end_change(P, S):                                          # a commit or a branch switch
    if P.moment is open and unseen: close(P, S, it, "unseen")          # does not use the day's slot
    cancel a running check of S's task; a finished, undecided check becomes silent and is released
```

Room and CLI actions use the same helpers: `lock(final=True)` is `seal`, `lock(final=False)` stores `m.pending` and moves to `held`, `show` seals a held pick, `skip(final=True)` is `skip_final`, and `quiet`, dial off and `wrong_start` call `close`.

**Moment states** (`ask.step`):

| From | Action | To | Record |
| :- | :- | :- | :- |
| `open` | `pick` (Room) | `held` | nothing yet |
| `open` | `skip_room` | `held` | nothing yet |
| `held` | `undo` | `open` | nothing |
| `held` (pick) | `show`, the next prompt, engine close | `sealed` | `call.sealed` with `picked_at`, then `call.confidence` if set |
| `held` (skip) | the next prompt, a new offer, engine close | `skipped` | `moment.skipped` |
| `open` | `seal` (chat reply, `firsthand answer`, "don't know") | `sealed` | `call.sealed`, `call.confidence` |
| `open` | `skip_final` (chat, CLI) | `skipped` | `moment.skipped` |
| `open` | `close` | `closed` | `moment.closed` |
| `sealed` | the key arrives, or is already there | `settled` | `check.ran`, `call.scored` (not for `dont_know`) |
| `sealed` | the check is unavailable | `settled` | `call.scored` unscored, `check-unavailable` |

`skipped` and `closed` are final. Once a moment is in `REVEALED` and its key exists, `release` writes `check.ran` and the result becomes visible in the Room. A session's second final skip sets `session_stopped`.

**Budget.** "Asked today" is the number of `moment.offered` events with a local date of today whose moment was not closed as `unseen` or `wrong-start`, nor as `fix-started` with `seen` false (such a close also clears the change's one question). It is computed from the record, across all projects.

**The first prompt of the day** is the first `prompt_submit` the engine applies on a local date, across all sessions and projects, not counting consumed reply words. The turn it starts gets no question and no fact line.

### 8.3 The key rule, as one function (`keys.agent_output`)

```
agent_output(want, *, moment, store, check_id=None, silent=False, ctx) -> str | None:
    if want == "question":
        if moment is None or moment.state != "open": return None
        return words.question_line(moment, ctx)            # built from the moment alone: never touches the store
    if want == "ack":
        return words.ack_line(ctx.ack, ctx.task_name)      # fixed copy
    if want == "pending":
        if moment is None or moment.state != "sealed": return None
        return words.pending_line(moment, ctx)             # says only that the call is locked
    # "result", "finding" and "fact" carry a result
    try:
        key = store.reveal(check_id or moment.id, moment, silent=silent)
    except (KeyLocked, KeyError):
        return None                                        # too early, or nothing to say
    if want == "result":  return "\n".join(words.result_lines(moment, key, ctx))
    if want == "finding": return words.finding_line(key)
    if want == "fact":    return words.fact_line(key, ctx.high_stakes)
    return None
```

Rules that make this the only door:

1. Everything the engine hands to an agent channel is made of `agent_output` return values and nothing else: `HookReply.visible` is one of them, `HookReply.context` is `words.context_text(printable, agent_only)` over lists of them, and the `say` list of an action's view (section 7.2) is one of them split into lines. A unit test reads the source of `engine.py` and fails if it calls `words.question_line`, `words.result_lines`, `words.finding_line`, `words.fact_line`, `words.pending_line` or `words.ack_line` itself.
2. `views.py` reads results only from `check.ran` events, and `check.ran` is written only inside `release`, after `reveal` succeeded. So the Room cannot show a result early either.
3. `store.reveal` raises unless the moment is sealed, settled, skipped or closed, or the check was decided silent. A held pick is not revealed: the result waits for Show the result.
4. A reply typed in chat is sealed inside `on_prompt_fast` before `agent_output("result")` is called for it, in the same call.
5. Lines that are sent later (a queued finding, a fact line that is due) are made by `agent_output` at release time and stored as text. The key is gone by the time they are sent.

---

## 9. Words (`words.py`, CORE)

Exact strings. `<...>` marks a value. Where `experience.md` gives the line, it is quoted. Lines this contract had to add are marked [new] and listed in section 12, decision 20.

### 9.1 Helpers

```python
def context_text(printable: Sequence[str], agent_only: Sequence[str]) -> str | None
def task_name(prompt: str) -> str          # the first clause of the prompt: up to the first of . , ; : ? ! or a newline,
                                           # cut to 6 words and 48 characters; "this task" when empty
def clock_time(at: str, tz: tzinfo) -> str # "09:12"
def short_date(at: str, tz: tzinfo) -> str # "14 Nov"
def back_line(task: str) -> str            # "Back to: <task>. Next: read the summary."
def glob_label(pattern: str) -> str        # "refunds/**" -> "refunds/", "**/migrations/**" -> "migrations/"
```

`context_text` builds the text added to the model's context at a prompt: the agent-only lines first, one per line, then, if there is anything to print, `model.PRINT_PREFIX` on its own line followed by the printable lines. It returns None when both lists are empty. Agent-only lines come first so that nothing after the prefix is anything but text to print.

### 9.2 The question

```python
def question_line(m: Moment, ctx: OutputContext) -> str
def lead(m: Moment) -> str
def prompt(m: Moment) -> str
def context_line(m: Moment, project_name: str, tz: tzinfo) -> str
```

| Piece | Several tests | One test |
| :- | :- | :- |
| `lead` | `It added <n> tests. Read them first.` (`It added or edited <n> tests. Read them first.` when any is edited) | `It added 1 test. Read it first.` (or `It edited 1 test. Read it first.`) |
| `prompt` | `Which of them would still pass with the change undone?` | `Would it still pass with the change undone?` |
| Picks | `1` to `<n>` (toggles), `None`, `Don't know`, then Lock (section 16) | `Fails`, `Still passes`, `Don't know` (values `fails`, `passes`, `dont_know`) |
| Footer | `Checked by a run: the change undone, the tests kept.` | The same |

`context_line`: `Verification | <project> | <task> | change since <HH:MM>`.

`question_line`, several tests:

```
Firsthand (skip ok): your agent finished and added 3 tests. Which of them would still pass with the change undone? 1 test_same_key_refunds_once, 2 test_refund_response_is_stable, 3 test_refund_amount_validated. Reply the numbers, or none. With the tests shown: http://127.0.0.1:4127/q/r6t9kd
```

One test [new]:

```
Firsthand (skip ok): your agent finished and added 1 test, test_refund_response_is_stable. Would it still pass with the change undone? Reply fails or passes. With the test shown: http://127.0.0.1:4127/q/r6t9kd
```

- `added` becomes `added or edited` when any test is edited, and `edited` when all are.
- On a work computer the link comes first: `Firsthand (skip ok): http://127.0.0.1:4127/q/r6t9kd Your agent finished and added 3 tests. ...`, and when `ctx.work_notice` is true the line ends with ` A reply here is part of your agent's chat. The Room is not.`
- With no Room (`ctx.room_url` is None) the last clause is `With the tests shown: run firsthand room` [new].
- Always one line, no newline, under 10,000 characters. Test names are the last part of the id.

### 9.3 The result

```python
def result_lines(m: Moment, k: Key, ctx: OutputContext, result: str | None = None) -> list[str]   # the chat form; result defaults to revert_test.score
def you_said(m: Moment) -> str
def what_happened(m: Moment, k: Key) -> list[str]
def cue_text(m: Moment, k: Key) -> str | None
def more_row(item: KeyItem) -> str
def checked_line(how: How) -> str
def counts_line(matched: int, scored: int, fixed: int) -> str
def sure_line(sure_matched: int, sure_total: int, unsure_matched: int, unsure_total: int) -> str
def pending_line(m: Moment, ctx: OutputContext) -> str
def dispute_line(stands: bool) -> str
```

Chat form, from `experience.md` section 6.3:

```
Firsthand, revert test. Matched. You said 2.
test_refund_response_is_stable still passes with the change undone. It would pass whether or not the change exists.
More: http://127.0.0.1:4127/r/r6t9kd
Back to: idempotent refunds. Next: read the summary.
```

The first line is `Firsthand, revert test. <chip>. You said <answer>.` with ` Sure.` or ` Not sure.` added when How sure was given. Chips: `Matched`, `Did not match`, `Not scored`. On `Did not match` one line is added after the fact: `What would have shown it: <cue>`.

| Piece | Text |
| :- | :- |
| `you_said`, a numbered pick | `2, test_refund_response_is_stable.` |
| `you_said`, others | `None.` `Fails.` `Still passes.` `Don't know.` `Skipped.` [new] |
| `what_happened`, the pick still passes | `It still passes with the change undone.` `It would pass whether or not the change exists.` |
| `what_happened`, "none" and none passes | `None of them passes with the change undone.` [new] |
| `what_happened`, a miss and test Y still passes | `<Y name> still passes with the change undone.` |
| `what_happened`, a miss and none passes | `<picked name> does not pass with the change undone: it fails on its assertion.` or `...: it cannot run without the new code.` [new] |
| `what_happened`, one test | `It still passes with the change undone.` plus `It would pass whether or not the change exists.`, or `It fails on its assertion with the change undone.`, or `It cannot run with the change undone, which is weak proof.`, or `It does not pass with the change undone.` [new for the last three] |
| `more_row` | `fails on its assertion`, `still passes`, `cannot run without the new code, which is weak proof`, `does not pass` |
| `checked_line` | `Checked by a run, no model.` or `Checked by a run, by exit code, no model.` |
| `counts_line` | `Your calls of this kind: 5 of 7 matched. Always answering "none" would have scored 4 of 7.` |
| `sure_line` | `Sure: 6 of 8 matched. Not sure: 3 of 6.` |
| `pending_line` | `Firsthand: locked. The check is still running. The result will be at http://127.0.0.1:4127/r/r6t9kd` [new] |
| `dispute_line` | `Rechecked. The result stands, and here is why.` or `Rechecked. The check was wrong. This call is removed from your record.` |
| Not scored, "don't know" | reason `"Don't know" is not counted as a miss.` |
| Not scored, skipped | reason `Skipped, so nothing was scored.` [new] |

`cue_text` is mechanical, built from line numbers only:

| Case | Text |
| :- | :- |
| The test that still passes has one assert | `Its only assertion is at <path>:<line>.` |
| It has several | `Its assertions are at <path>:<l1>, <l2> and <l3>.` |
| It has none | `It has no assert statement: <path>:<def line>.` |
| The person said it passes and it fails | `It fails at <path>:<fail line>.` (the assertion line when no fail line was read) |
| Generic adapter | `It was checked by exit code only: <path>.` |

The cue is about the test that still passes when there is one, else about the picked test. The Room shows the cited source line beside it. The chat form does not.

The fixed answer is always "none" in 2a (section 12, decision 21). A scored call counts for it when its `outcome_kind` is `common`.

### 9.4 Lines with no question

```python
def finding_line(k: Key) -> str
def fact_line(k: Key, pattern: str) -> str
def note_fact(k: Key) -> str
def ack_line(ack: str, task: str) -> str
```

| Line | Text |
| :- | :- |
| `finding_line`, one test still passes | `Firsthand finding: <test id> passes with the change undone.` |
| several | `Firsthand finding: <id>, <id> pass with the change undone.` |
| tests that cannot run | A second sentence on the same line: `<id> cannot run with the change undone.` [new] |
| `fact_line` | `Firsthand: <test name> passes without the change. <glob label> is marked high stakes.` |
| `note_fact` | The finding text without the `Firsthand finding: ` prefix |
| `ack_line("skip")` | `Skipped. Back to: <task>. Next: read the summary.` |
| `ack_line("skip2")` | `Skipped. No more questions this session. Back to: <task>. Next: read the summary.` |
| `ack_line("quiet")` | `Quiet for this session. Checks still run and post notes. "quiet today" and "quiet here" also work.` |
| `ack_line("quiet-today")`, `("quiet-here")` | `Quiet for today. Checks still run and post notes.` and `Quiet for this project. Checks still run and post notes.` [new] |
| `ack_line("off")` | `Firsthand is off. Nothing is asked, run or recorded. Your record is kept. "firsthand on" to return.` |

An ack that answers a chat word goes in the printable list of `context_text`, so the agent prints it.

### 9.5 Install copy (SHELL prints it, from `experience.md` section 3.1)

The file list names the files actually written: `~/.claude/skills/firsthand/` (new folder) and `~/.claude/settings.json` (adds 6 hooks that call `<launcher>`). There is no `CLAUDE.md` line in 2a (section 12, decision 15). The rest of the copy is `experience.md` section 3.1 unchanged, without its last sentence about reading recent history, which belongs to the history scan in step 3.

---

## 10. Test plan

### 10.1 Layout and commands

- Unit tests live in `tests/firsthand/test_<group>_<module>.py`. `tests/firsthand/` has no `__init__.py`: with one, `python -m unittest discover -s tests` imports it as the package `firsthand` and hides the real one [measured].
- `tests/test_firsthand.py` (CORE, step 0) makes the standard command find them:

```python
"""Loads tests/firsthand, which is not a package so that it cannot shadow the firsthand package."""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent / "firsthand"

def load_tests(loader, standard_tests, pattern):
    return unittest.TestLoader().discover(str(HERE), pattern="test_*.py", top_level_dir=str(HERE))
```

- Everything: `python -m unittest discover -s tests -v`, run from the repo root.
- One group: `python -m unittest discover -s tests/firsthand -t tests/firsthand -p "test_core_*.py" -v` (or `test_shell_*.py`, `test_room_*.py`, `test_e2e_*.py`).
- Tests import helpers as `import support`.
- Every test class extends `support.TempHome`. Nothing is mocked inside the group under test. Other groups are replaced by fakes defined in the test file.
- The build runs under an agent, so `cli.under_agent()` is true in the test process. A test that needs the person's view calls `client.call(..., agent=False)` or passes `environ` and `ancestors` to `under_agent`.
- pytest is not a dependency of the product. Tests that need it (some CORE runner tests and the integrator's) build one virtualenv in a temporary folder in `setUpModule` (`python -m venv`, then `pip install pytest`) and skip with a clear reason if that cannot be done.

### 10.2 CORE

| File | Asserts |
| :- | :- |
| `test_core_paths.py` | Each override. No function creates a folder. Id validation raises. The socket fallback for a long path. `write_private` gives mode 0600 and replaces atomically |
| `test_core_events.py` | Encode and decode round trip for each event kind. Unknown keys dropped. A malformed line decodes to None. Prompt cut at the limit. Each `scan_secrets` kind, and that clean text is unchanged |
| `test_core_record.py` | `ensure_record` layout, modes and first commit. ULIDs sort by time. `append` writes the envelope and path of section 4.8 and refuses an unknown type. `events` filters. `commit` subject, author, False when clean |
| `test_core_gitwatch.py` | Project root from a subfolder and from a worktree. One id for a clone. None with no commit. `is_test_path`, `glob_match` and `runner_token` tables |
| `test_core_snapshot.py` | A snapshot holds tracked, modified, staged and untracked files and no ignored file. `support.repo_fingerprint` is equal before and after `take`, `diff`, `read_file` and `checkout`. `diff` statuses. `read_file` on a missing path |
| `test_core_scratch.py` | Every `STRIPPED` entry is gone. `undo` restores, and deletes added files. `scrubbed_env` holds none of `GH_TOKEN`, `ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `SSH_AUTH_SOCK` when they are set in the caller. A run past its limit is killed with its children. `close` removes the folder. `sweep` |
| `test_core_pytest_adapter.py` | `list_tests` on functions, classes, async tests, nested functions (ignored), a syntax error. `changed_tests`: new, edited, comment-only change (not edited), order and status. `read_junit` on junit text for each shape in section 5.1 (passed, bare assert, `AssertionError`, `Failed`, `ImportError`, setup error, skipped, parametrized, collection failure, missing file). With the virtualenv: one real run per shape |
| `test_core_generic_adapter.py` | Items per test file, argv, exit code classes |
| `test_core_revert_test.py` | `match` returns None for no test change, no source change, no test command. Four-test cap and order. `score` over every answer and key combination, including one test and the generic result. `cue` cases. `finding`. `parse_reply` table with confidence words and a curly apostrophe. With the virtualenv: `run` on a small repo gives each of the three results, calls `on_control` once, removes the scratch folder, respects the time limit and the cancel event |
| `test_core_keys.py` | `put` writes mode 0600 and reloads. `reveal` raises `KeyLocked` for `open` and `held` and for no moment without `silent`, returns the key for each state in `REVEALED`. `agent_output` returns None for `result`, `finding` and `fact` in every unrevealed state, and returns only `words.question_line` for `question` |
| `test_core_ask.py` | `gates` returns each reason in order. `fact_allowed`. `is_pressure`. `control_word`. `step` over the whole table of section 8.2, and `EngineError("state")` for every other pair |
| `test_core_timeline.py` | The first prompt starts a task with its base. A second prompt in a task is a `prompt` event. The done signal's three conditions, one failing at a time. The first turn end compares with the base. A changed HEAD or branch ends the change. A pending ask blocks done and clears on the result. A null exit counts as failing |
| `test_core_words.py` | The lines of `experience.md` sections 5.1, 6.2, 6.3 and 6.4 are reproduced character for character from the example values. No output holds an em dash. `task_name` cases. The work computer form |
| `test_core_views.py` | Each view has exactly the keys of section 7.2. `result` is null without a `check.ran` event. Inbox groups and the closing line. Skills levels `too_few` and `shown` |
| `test_core_engine.py` | With a fake moment module, a fake `SettingsStore` and the inline executor: the question is offered at the done signal and its line is in the reply. Each gate keeps it silent and a note is written. A chat reply seals, scores and returns result lines. A Room pick is held, undone, re-picked, shown. `dont_know` writes no `call.scored`. The next prompt closes a seen question and leaves an unseen one. An unseen question's line goes out at the next stop. A fact line is never in the same stop as its question: it goes at the stop after the question was closed or skipped unanswered, and at the done-signal stop when no question was offered. An unseen question on a high-stakes change whose check has finished closes at the next stop. Findings wait for delivery and are re-queued when `delivered(id, False)`. Two skips stop the session. `wrong_start` and `dispute`. A repeated spool id is ignored. A new `Engine` over the same folders resumes an open question. The record holds one `question ` commit per question. No reply's `visible` or `context` and no view holds a result while the moment is `open` or `held` |

### 10.3 SHELL

| File | Asserts |
| :- | :- |
| `test_shell_adapter.py` | `to_spool` for one payload of each of the six events, built from the confirmed hook facts: Bash success (`exit` 0, failing ids from `tool_response.stdout`), Bash failure (`Exit code 1` parsed, ids from `error`, null when the first line is missing), Edit and Write paths, `AskUserQuestion`, a subagent call (`sub`), a prompt with a token (redacted). `transcript_path` and `last_assistant_message` never appear. `render`: only `systemMessage` on `turn_end`, plain text on `prompt_submit`, the leading-brace guard, the 10,000 character guard. `settings_fragment` equals the JSON of `build-2.md` section 3 |
| `test_shell_hooks.py` | One line appended per call, file mode 0600. Exit code 0 and empty stdout for garbage stdin, an unknown event, a missing home. Nothing on stderr. With a reply file written by the test: its `visible` comes out as `{"systemMessage": ...}` and the file is claimed. With none: returns within the budget and prints nothing. No output ever holds `decision`, `permissionDecision`, `continue` or `hookSpecificOutput`. `FIRSTHAND_NO_DAEMON` stops the spawn |
| `test_shell_install.py` | `merge_hooks` keeps unrelated hooks, permissions and other keys, is idempotent, and raises on invalid JSON without writing. `apply` then `uninstall` restores `settings.json` byte for byte and removes the skill folder. A file edited after install is refused with a diff and left alone. A second `apply` keeps the first backup. `install_engine` produces a launcher that runs `hook claude-code Stop` on empty input and exits 0 |
| `test_shell_config.py` | Defaults with no files. Each key's validation. The file shapes of section 4.5. `detect_test_command` cases. `ensure_project` defaults. The commit callback is called with the right subject |
| `test_shell_daemon.py` | With a fake engine and a fake Room: the spool is read in order, the offset is saved, a fully read spool is truncated, a partial last line waits. A reply becomes a reply file. A claimed file gives `delivered(id, True)`, an unclaimed one `delivered(id, False)`. Each control op calls the right engine method and maps errors. The refused ops under `agent`. A second daemon exits at once. `daemon.json` appears and is removed. Idle exit |
| `test_shell_cli.py` | Each command's arguments reach `client.call` (a fake). `under_agent` from an environment marker and from an ancestor name, both passed in. `journal` under an agent is refused. `init --yes --work-computer no --test-command "pytest -q"` in a temporary home writes the two files, the manifest, the record and the port, and `init` with no terminal and no `--yes` writes nothing. `uninstall` after it leaves the record |

### 10.4 ROOM

All against a fake engine that records calls and returns canned views.

| File | Asserts |
| :- | :- |
| `test_room_security.py` | A wrong `Host` is 403 on every route. `/api/*` without a session is 401. A POST with no Origin, a foreign Origin, a wrong token or a non-JSON body is refused. A ticket works once and expires. `next` cannot leave the site. The cookie is HttpOnly and SameSite=Strict. Every response has the CSP and no `Access-Control-*` header. A body over the limit is 413. A non-loopback host raises |
| `test_room_routes.py` | Each route of section 7.2 calls the engine method in its table with the right arguments and returns the view unchanged. Each error code maps to its status. An unknown path is 404 |
| `test_room_events.py` | An engine notice reaches an open stream as one `data:` line. `clients()` counts streams. A closed stream is removed |
| `test_room_page.py` | `page.html` references only `/static/` URLs and has no inline script, inline style or remote URL. `room.css` and `room.js` hold no remote URL. The token block of `room.css` equals the block in `design/learning-experience/assets/room.css`. `room.js` never assigns `innerHTML` from API data (a source check for the string `innerHTML`) |
| `test_room_served.py` | One real `RoomServer` on port 0: enter with a ticket, read the inbox, lock, undo, show, through `urllib` |

### 10.5 Integrator: fixtures and end to end (`build-2.md` section 9)

`tests/firsthand/fixtures.py` builds each fixture as a git repo in a temporary folder (a base commit, then an uncommitted change) and returns the spool lines that replay a session on it: `session_start`, `prompt_submit`, an `after_tool` test run where the fixture has one, `turn_end`. Lines are built in code with the fixture's path as `cwd` and the shared test virtualenv as `venv`. Each sequence begins with one earlier prompt and turn end on the same day, so the fixture's task is not started by the first prompt of the day.

| Fixture | Expected |
| :- | :- |
| `proves` | Key `fails_on_assertion` |
| `passes_anyway` | Key `still_passes` |
| `needs_new_code` | Key `cannot_run` (the test file imports the new function at module level, so collection fails after the undo) |
| `mixed3` | One of each |
| `edited_test` | The edited test is found. `fails_on_assertion` |
| `control_fails` | `check.unavailable`, reason `does not match here`. No `moment.offered`. No line |
| `no_tests` | No candidate, no check |
| `high_stakes` | With the day's question already used: the fact line is the line of the done-signal stop, and a note is written. With a question offered and not answered: the question line at that stop, then after an unrelated prompt the question closes as `moved-on` and the fact line is the line of the next stop |

`test_e2e_replay.py`, against a real `Engine` with a real `ConfigStore`, the inline executor and a fixed clock. For each fixture it asserts: the record events written, in order. The `visible` line of the stop reply. The score for a given reply. `support.repo_fingerprint` equal before and after. Plus:

1. No reply and no view holds `decision`, and none holds a result string before the lock. The test scans every `HookReply` and every view for the key's result words and for `passes with the change undone`.
2. A second finished change on the same day asks nothing and writes a note.
3. `skip`, `quiet`, dial off and the next prompt each end a question with no further line.
4. A reply `2`, a Room `lock` plus `show`, and `answer 2` through the control op each produce the same `call.scored` body on the same fixture.

`test_e2e_process.py`, with real processes in a temporary home:

5. With no daemon, `firsthand hook claude-code UserPromptSubmit` leaves the line in the spool, starts a daemon, and the record gets `task.started` with a base.
6. With the daemon killed mid-session, the next hook restarts it and every spool line is applied once.
7. A `Stop` hook whose question is ready prints exactly one JSON object with the single key `systemMessage`. Every other hook call prints nothing.
8. `init --yes` then `uninstall` leaves `settings.json` byte for byte as it was, with a pre-existing file that already had other hooks.
9. One browser path through the real Room: ticket, inbox, lock, show.

Item 1 of `build-2.md` section 10 (the line appears once in a live Claude Code session with no extra model turn) cannot be checked by a unit test. The integrator runs it by hand in a session with a temporary `HOME` and reports what the terminal showed.

---

## 11. Seams for 2b and 2c

**2b, Call it.**

- A new module `moments/call_it.py` with the same public surface as `revert_test.py`, added to `moments.REGISTRY`. `engine.py` already reaches moments only through that surface and already carries `BREAKS`. 2b adds break names (`failure_prompt`, `failure_turn_end`) and a `pick` step in `try_offer` for when two modules match one break.
- `timeline.step` already sees `tool_failed` test runs and their failing ids. 2b adds the effects `test_failed` and `went_green`, and `needs_snapshot` becomes true for a failing test run (the red snapshot). `Task` gains the red and green trees.
- The key that arrives later: `sealed` already waits for a key with no time limit. 2b's key is put in the store when the timeline sees green, and `release` runs unchanged. The Inbox gains the Waiting group for `sealed` moments whose key depends on a timeline event. In 2a those show under Results with the chip `pending`.
- "Closing the card at the first edit": `after_tool` edit events already reach the engine with relative paths. 2b adds one `close` reason to `CloseHow`.
- `KeyItem` is specific to the Revert test. 2b adds its own item type. `Key.tests` should then become `Key.items` with a `kind` discriminator. `views.result_view` and `words` dispatch on `Key.kind`, which is already stored.
- New record types `episode.red` and `episode.green` are added to `Record.append`'s allowed set.

**2c, Brief.**

- The question is agent-only text on the next `UserPromptSubmit`. The per-session queue that carries findings in 2a carries it: 2c adds a `Want` value and one branch in `agent_output` that needs no key.
- Work product goes to the agent: a new route `POST /api/q/<ref>/send-to-agent` and an `EngineAPI.send_to_agent(ref)` method that queues the person's line through the same queue. `agent_output` gets a `work` want that carries the person's own words and no result.
- The check is the Revert test's on one named test: `revert_test.run` takes its tests from `Candidate.tests`, so 2c builds a `Candidate` with the one confirmed test. Nothing in `run` reads the diff's test list again.
- The trigger needs path categories. `gitwatch.is_test_path` is the only category in 2a. 2c adds `gitwatch.category(path)` beside it and a `task_start` break fed by `prompt_submit` plus the first `after_tool` edits, which `timeline.step` already receives.
- "Is this your check?" is a second card state. The moment table in section 8.2 gains a `confirm` action before `open`. `ask.step` is a table so that this is one row.

**Both.** New agents (step 6) add a module under `adapters/` with the names `claude_code.py` exports. `hooks.main` and `daemon` pick the adapter by the `agent` argument, and `HookReply` is already free of Claude Code's output shapes.

---

## 12. Decisions made where the spec was silent or contradictory

Each says what was chosen and why. Items 5 to 9 change something `build-2.md` states.

1. **The loop lives in `engine.py` (CORE), not in `daemon.py`.** `build-2.md` lists `daemon.py` only. The fixture tests replay spool lines with no process, and the loop uses only CORE modules. `daemon.py` is the process around it.
2. **`paths` reads `HOME`, `FIRSTHAND_HOME`, `FIRSTHAND_CONFIG_HOME` and `FIRSTHAND_CLAUDE_DIR` only.** `XDG_CONFIG_HOME` and `CLAUDE_CONFIG_DIR` are not read. A test that sets a temporary `HOME` would otherwise still write to a real folder named by an inherited variable. A person who relocates Claude Code's folder sets `FIRSTHAND_CLAUDE_DIR`.
3. **The hook reply is one file per event, claimed by rename.** `build-2.md` says the dispatcher prints the output "if the daemon left one ready" and waits 300 ms. A file per spool event id lets the dispatcher know the reply is for this event, and the rename tells the daemon whether a line was really delivered, so an undelivered question or finding is offered again.
4. **A reply file is written for every prompt and stop, even an empty one.** Otherwise every prompt and every turn end would wait the full 300 ms.
5. **The dispatcher parses failing ids from every shell call.** `build-2.md` section 4 says it does so for commands that start with the project's test command. That needs a project lookup and a config read inside the hook. The engine now decides whether a command was a test run and ignores the ids otherwise. The spool still holds only matched ids, never output.
6. **"Starts with the test command" became "has the same runner".** `python -m pytest tests/x.py` and `uv run pytest` are test runs for a project whose command is `pytest -q` (`gitwatch.is_test_run`).
7. **One pytest run per test file.** `build-2.md` section 6 step 3 shows one command with every id. Measured on pytest 9.2.0: when one of the named files cannot be collected, pytest exits 4 and runs none of the ids. That is the normal case after the undo when a test file imports new code at module level.
8. **The assertion test reads the last line of the failure text.** `build-2.md` section 6 step 7 says "a `failure` whose type is `AssertionError`". Measured: pytest's junit `failure` element has no `type` attribute. The exception name is on the last line of its text.
9. **"Editable install" is decided by a probe.** `build-2.md` says an editable install ends the check. The contract asks the interpreter where each changed module would load from and ends the check only when one loads from the project instead of the scratch copy. That is the actual hazard, and it lets the common case run where `PYTHONPATH` wins.
10. **Room picks are held until shown.** `experience.md` gives Undo "until the result is opened" and `build-2.md` lists no route for it. A Room pick is stored in a `held` state, nothing is revealed and nothing is written to the record until Show the result or the next prompt. Chat replies and "don't know" seal at once. Two routes were added: `undo` and `show`.
11. **An unseen question survives the next prompt.** `build-2.md` says a question closes at the next prompt, and also that a line not ready in time is "delivered at the next Stop". Both cannot hold. A question whose line was never claimed and whose card was never opened stays open through prompts, is offered at each later stop of that session, and closes as `unseen` when the change or the day ends. An `unseen` close does not use the day's slot.
12. **What one stop may carry, and when a fact line goes.** One line at most: a question offered at this done signal, else a fact line that is due, else an unseen question. A fact line is never sent in the same stop as its own question, because that would give the answer away. `build-2.md` section 7 has the fact line close an open question as `shown-first`. With hooks, a question the person has seen is always answered or closed by the next prompt, before the next stop. So in practice the fact line goes at the next stop after the question was skipped or closed, and only when nobody answered. The `shown-first` close remains for one case: an unseen question on a high-stakes change whose check has finished is closed at the next stop whatever its key holds, and the reason recorded is `shown-first` if a fact line follows and `unseen` if not. Closing it without looking keeps the rule that being asked never depends on the result.
13. **Findings from silent checks also go to the agent.** `build-2.md` section 7 queues a finding "when any test still passes or cannot run". With no question open there is no call to protect, so the line is queued at once when "Send findings to my agent" is on. After a chat reply no separate finding is queued: the result lines the agent prints already hold it.
14. **`init` installs the engine by copying the package.** `architecture.md` describes a virtual environment and a release checksum. There is no published release in 2a and the product has no dependencies, so the engine folder holds a copy of the package and a launcher with an absolute interpreter path. The checksum arrives with the first release.
15. **`init` writes two files, not three.** `experience.md` section 3.1 lists `~/.claude/CLAUDE.md`. `build-2.md` section 3 writes only `settings.json` and the skill. The install copy lists what is written.
16. **Routes added:** `/enter`, `/api/session`, `/static/*`, `/api/skills`, `/api/settings`, and `undo` and `show`. `build-2.md` section 8 specifies sessions, a Skills screen and a Settings screen but lists no route that could serve them.
17. **`init` without a terminal.** Run from inside the agent there is no terminal to answer `Go ahead? [Y/n]`. Without `--yes` it prints the plan and writes nothing.
18. **Wrong start.** `learning.md` moves the base to the previous task's base. The prototype says "your last commit". The base moves to the previous task's base in the same change, or to the tree of HEAD when there is none. The open question closes as `wrong-start`, the check reruns, and a new question may replace it without using a second slot. It is offered only before a pick.
19. **Dispute uses only the listed event types.** The rerun writes a second `check.ran` with `rerun_of` and the person's reason. If its results differ, a second `call.scored` with `result: unscored`, `unscored_reason: check-unavailable` and `supersedes` is written, and readers take the last score. The record stays append-only.
20. **Copy added.** `experience.md` has no one-test question line, no text for several of the result facts, no cue wording that a program can produce, and no line for a locked call whose check is still running. Section 9 marks each added line [new]. The cue cites line numbers only: "the change does not alter the status code" cannot be derived mechanically and is not printed. The extra line "The tests are shown on the Room page" is not sent in Claude Code, because the stop message must stay one line and the link clause already says it.
21. **Small rules the spec left open.** A change ends at any change of HEAD or branch. The fixed answer is always "none" in 2a. A chat word (`skip`, `quiet`, a reply word) is acted on only while a question is open for that project. Two skips in a session end its questions. A prompt Claude Code submits on its own (a background subagent reporting back) cannot be told from a typed one and is treated as the person's. A repo with no commit is not watched. `note.posted` is written for a silent check only when it found something. Default high-stakes globs are `**/migrations/**`, `**/auth/**`, `**/payments/**` and `**/billing/**`, the categories `learning.md` section 3.5 names. Tests are compared by `ast.dump`, so a comment change is not an edit. The daemon exits after 30 idle minutes. `journal`, `skills`, `room --tty` and the one-time Room URL are refused under an agent.
22. **Not decided here.** `../PRODUCT.md` section 9 item F recommends switching the licence when the package is added. That is an open founder decision, so `pyproject.toml` leaves the licence as the repo stands. Item G (the name) is also open: the package is named `firsthand` and nothing is published.

---

## 13. As built: integration changes

The three groups built against sections 1 to 12. The integrator then built the four CORE modules no group had been given (`ask.py`, `words.py`, `views.py`, `engine.py`), joined the groups and ran the whole loop end to end. This section records every place where the code now differs from or adds to the sections above. Where they disagree, this section describes the code.

### 13.1 Files added

| File | Group | Holds |
| :- | :- | :- |
| `firsthand/engine_checks.py` | CORE | A mixin of `Engine`: checks, `try_offer`, `release`, the moment changes (`seal`, `skip_final`, `close_moment`, `settle_held`, `revealed`, `end_change`) and delivery |
| `firsthand/engine_actions.py` | CORE | A mixin of `Engine`: the read models and every Room and CLI action |
| `firsthand/state.py` | CORE | The checkpoint `run/state.json` and the engine's live objects (`Check`, `Project`, `Session`, `PendingReply`) |
| `tests/firsthand/fixtures.py`, `test_e2e_replay.py`, `test_e2e_process.py` | integrator | Section 10.5 |
| `tests/firsthand/test_core_ask.py`, `test_core_words.py`, `test_core_engine.py` | integrator | Parts of sections 10.2 for the modules the integrator built. There is no separate `test_core_views.py`: the view shapes are checked in `test_core_engine.py` and the result rule in `test_e2e_replay.py` |

`engine.py` was split into three files to stay under the 800 line limit. `Engine` is `class Engine(Checks, Actions)` and its public surface is unchanged: it implements `EngineAPI`. The moment-closing helper is `close_moment`, because `close()` is the `EngineAPI` method that ends the engine.

### 13.2 Signatures that changed

- `runner.snapshot.SnapshotStore.read_bytes(tree, path, limit=None) -> bytes | None` is added. `Scratch.undo` restores binary files with it.
- `moments.revert_test.cue(answer, k, tests=())`: a `KeyItem` has neither every assertion line nor the def line, so the card's `TestItem`s may be passed. `words.cue_text` builds the same sentence from the moment's tests and is what the engine and the views use.
- `timeline.task_name(prompt)` holds the section 9.1 rule, because `Task.name` is set inside the pure timeline. `words.task_name` delegates to it.
- `words.result_lines(m, k, ctx, result=None)`: the chip comes from `revert_test.score` unless `result` is given. Added helpers: `answer_text`, `chip_label`, `cue_target`, `note_title`, `short_ref`.
- `keys.agent_output` has the same signature and rule; its body is split into two private helpers to keep each function under complexity 10.
- `timeline` effect bodies: `change_ended` is `{from_commit, from_branch, to_commit, to_branch, change, task}`; `test_passed` and `done` are `{task, tree}`. The engine builds the `task.event` done body (`paths`, `files`, `tests_changed`) from the diff.

### 13.3 Behaviour fixed or decided during integration

1. **The done-signal stop could not speak.** Section 8.2 replied early and empty to a `turn_end` when `may_speak` was false, and `may_speak` was false at the very stop that becomes the done signal when no test run had started a check earlier. `may_speak` is now also true when the stop may be the done signal (pseudo-code updated in place).
2. **`try_offer` never offers on a failed control run.** It requires the check's status to be `undoing` or `finished`. It answers a deferred stop reply only when it offered or released; `on_finished` also answers it, so a fact from a silent check can reach the stop that was waiting.
3. **A finding is sent once.** When a prompt reply carries queued findings they are marked as sent with that event id. `delivered(id, False)` clears the mark so they go out with the next prompt. Without this a prompt within one second of the last one sent the same finding twice.
4. **The daemon confirms a claimed reply at once** (section 4.2 updated). Before, a reply was confirmed only after one second, so a prompt typed within a second of the question still saw the question as unseen.
5. **The control socket fallback is under `/tmp`, not `TMPDIR`** (section 3.1 updated). Found in the manual run: with a long `TMPDIR` the fallback path was itself too long and the daemon could not start. A hook-spawned daemon and a CLI in the person's own terminal can also have different `TMPDIR` values.
6. **The daemon's log handler sits on the `firsthand` logger**, so lines from `firsthand.engine` and `firsthand.room` reach `run/daemon.log`. `firsthand.room` keeps its `NullHandler` when no daemon runs.
7. **The Room answers `GET /favicon.ico` with 204.** Browsers ask for it on their own, and the 404 was the only console error on the page.
8. **`release(..., commit=False)`** is used by the high-stakes close of section 8.2 step 2, so that question still gets exactly one `question <id> closed` commit, made after its `moment.closed` event.
9. **Daemon start order.** The Room is built first with a proxy for the engine, the engine is built with the Room's real URL, then `room.start()` runs. `RoomServer` subscribes to the engine in `start()` and unsubscribes in `shutdown()`.
10. **`quiet(scope="session", session=None)`**, which is what the CLI sends, applies to the most recently active session in the project at `cwd`. `quiet(..., on=False)` returns `{"lines": ["Quiet is off."]}`.
11. **`set_settings`** accepts `dial`, `daily_limit`, `findings_to_agent`, `quiet_today` (a bool: today's local date or null), `work_computer` and `check_time_limit_s`, and with `project`: `test_command`, `quiet`, `high_stakes_add`, `high_stakes_remove` and `name`. Turning the dial off stores `dial_before_off` and closes open questions as `off`, so `firsthand on` can restore it.
12. **`status(cwd)` calls `ensure_project`** for the project at `cwd`, so `firsthand config` works in a project the engine has not seen an event from yet.
13. **`question(ref, seen=True)` also marks a shown result as opened**, so it leaves the Inbox's Results group.
14. **`skip()` through the control socket** (the CLI) records `moment.skipped` with `how: "cli"`. A chat word records `chat`, the Room `room`.
15. **The first prompt of the day** is counted only for prompts the engine applies: in a git project with a commit, with the dial not off, not a consumed reply word. Agent-only findings are held back on that prompt too.
16. **The one-time work computer sentence** is added until the first question line on a work computer is confirmed delivered. The flag is kept in `run/state.json`.
17. **Results and Journal leave out a question closed by Wrong start**: the new question replaces it. A dispute reruns the check under a new check id and commits with the subject `events`; if the rerun cannot finish it writes `check.unavailable` for that check and the score stands.
18. **A restarted engine** resumes each live question: from its key file when one is there, else by running its check again from the stored trees with the moment id as the check id. Key files of checks that are not a live question's are discarded.
19. **`tests/test_firsthand.py` loads nothing on Python 3.10.** The repo's CI also runs the skill's tests on 3.10, and the package needs 3.11.
20. **`SnapshotStore.take` copies the project's index with its mtime** (`shutil.copy2`). A copy with a fresh mtime defeats git's racy-clean check, so a same-size edit made within the file system's timestamp granularity of the last `git add` was left out of the snapshot. Found as an intermittent failure of `test_core_scratch`.
21. **The install copy** no longer says "and package-name lookups" or `"firsthand privacy" lists everything`: neither exists in 2a. It now reads `Firsthand sends nothing anywhere except the lines it adds to your agent's chat.`

### 13.4 Copy added during integration

Engine and view lines not in `experience.md` or section 9, for the founder to review: `No answer.` (You said, for a question closed unanswered), `Quiet is off.`, the Inbox notices `Quiet for today. Checks still run and post notes. Undo` and `Quiet for this project. Checks still run and post notes. Undo`, `The result will be in the Room: run firsthand room` (the pending line with no Room), and the engine's error messages: `No question has the reference <ref>.`, `No question is open. Nothing to answer.`, `Reply with one of: <words>. Or skip.`, `Pick an answer first.`, `How sure is set after a pick, before the result.`, `Wrong start is offered only before a pick.`, `Say in a few words what looks wrong.`, `This result can be rechecked once, after it is scored.`, `This change asks or sends more, so it is not taken from inside an agent. Run it in a terminal you opened.`, `This change asks or sends more. Confirm it.`, `Name at least one setting to change.`, `Not a setting: <keys>. Use: <keys>.`, `A project setting needs the project.`, `This folder is not a project Firsthand has seen.`, `scope must be session, today or here.`, `value must be high, low or null.`, `No settings for project <id>.` The SHELL and ROOM reports list their own added copy.

### 13.5 Known limits found end to end

- **The question can arrive one stop late.** The Stop hook waits at most 300 ms and the engine defers a stop reply 250 ms for a check in its control run. The control run takes about half a second for two test files (measured: whole checks took 1.1 to 1.2 s). When the agent's test run happens well before its turn ends, the check has finished and the line is on the done-signal stop. When the turn ends within about half a second of starting the check, the question stays open and goes out at the session's next stop (decision 11).
- Item 1 of `build-2.md` section 10 still needs a live Claude Code session: how the `systemMessage` line is drawn in the terminal has not been seen.

---

## 14. As built: step 2b, Call it

Step 2b adds Call it on the 2a loop, following section 11. Where this section and sections 1 to 13 disagree, this section describes the code.

### 14.1 Files

| File | Holds |
| :- | :- |
| `firsthand/moments/call_it.py` | The moment surface: `KIND = "call_it"`, `SKILL = 3`, `HEADLINE = "CALL IT"`, `BREAKS = ("failure_prompt", "failure_turn_end")`, the failure-prompt patterns, trace frames, the "exists at the base and unedited" test, the picks, the symptom scan, `score`, `cue_path`, `reply_words`, `parse_reply` |
| `firsthand/moments/call_it_run.py` | The red run and the fix run, each in a scratch copy, each never raising |
| `firsthand/engine_callit.py` | A mixin of `Engine`: episodes, the two runs, the offer, the close at the first edit, green, `release_call`, the end of a change, resume after a restart |
| `firsthand/words_callit.py` | Every Call it line. `words.question_line`, `pending_line`, `result_lines` and `answer_text` dispatch to it on `m.kind` |
| `firsthand/views_callit.py`, `firsthand/views_skills.py` | The Call it card, result and Waiting rows; the Skills rows (moved out of `views.py` to stay under 800 lines) |
| `tests/firsthand/test_core_call_it.py`, `test_e2e_callit.py` | Unit tests, and the four fixtures replayed end to end |

`moments.REGISTRY` is `(revert_test, call_it)`. `Engine.module` is still the first entry; `Engine.mod(m)` picks a moment's module by `m.kind`, and `Engine.reply_n(m)` counts its reply picks.

### 14.2 Shared types and formats that changed

- `Key.extra` and `Moment.extra` (optional dicts, default None). Call it's key holds `test`, `picks`, `frames`, `fix_paths`, `changed` and `patterns`. The moment holds `episode`, `test`, `picks`, `frames`, `message` and `trigger`. Neither holds source text.
- `CloseHow` gains `fix-started`. `call.scored.unscored_reason` gains `symptom-patch`, `no-fix`, `fix-not-causal` and `never-green`.
- `Record` accepts `episode.red` (`episode`, `task`, `trigger` (`prompt` or `test_run`), `test`, `tree`, `command`) and `episode.green` (`episode`, `task`, `test`, `red_tree`, `green_tree`, `command`). They are written whether or not a question is asked, so every failure is saved for the Replay drill. `episode.green` holds trees only: the fix paths and patterns are part of the key and reach the record only in `check.ran`, after the lock.
- `check.ran` for Call it: `base_tree` is the red tree, `head_tree` the green tree, `results` holds the one test with its result after the fix is undone, and `extra` holds the key's extra.
- `moment.offered` for Call it: `form: "pick"`, `skill: 3`, `break`, `tests: []`, plus `episode`, `test` and `picks` (`n`, `path`, `traced`, `changed`; records from before section 16 hold a `note` string instead, and still read).
- `timeline`: `needs_snapshot` is also true for a failing test run (the red snapshot), and a failing test run emits `test_failed` (`task`, `tree`, `failing`, `command`). No `went_green` effect: the engine reads green from `test_passed`.
- `Session.episode` is kept in `run/state.json`.
- Views: the question view gains `trace` (null for the Revert test) and each Call it file pick gains `path`. No view of an open, held or sealed question says why a file is listed; the result's `more.rows` does, after the test row. The Inbox gains `waiting` (`id`, `ref`, `kind`, `text`, `href`). Skills has two rows: Verification and Debugging and diagnosis. Counts, the fixed answer and How sure are per moment kind.

### 14.3 Behaviour

1. **Triggers.** A prompt holding `Traceback (most recent call last)` or a line `FAILED <id>` starts a `prompt` episode: its red tree is the prompt's snapshot, its test the first FAILED id whose file exists, else the first failing id of the next failing run. A failing run whose failing ids include a test that exists at the task base and is not edited at red starts a `test_run` episode. Only pytest projects. One episode per change is followed until it goes green.
2. **Selection first.** The gates of 2a (dial, quiet, pressure, the daily limit, one per change, first prompt, two skips) are checked before the red run starts. If they fail, nothing runs and the episode is saved silently.
3. **The red run is the control.** The test is run on the red snapshot in a scratch copy and must not pass, else `check.unavailable` (`does not match here`) and nothing is asked. Its junit failure text gives the trace frames and the message line the card shows.
4. **The offer.** A `prompt` episode is offered as soon as the red run passes; its line goes out at the next stop if the card is still open and unseen. A `test_run` episode is offered at a turn end whose last test run failed, with the line on that stop. A turn that goes red and green asks nothing.
5. **The picks.** Non-test files named in the trace (innermost first) and non-test files changed in the task before red, interleaved, at most three, then sorted by path so a position says nothing. Then "Somewhere else" and "Don't know". Why each file is listed is stored as `traced` and `changed` and never shown before the result: when the agent's own edit broke the test, "changed in this task" would mark the answer. With fewer than two files there is no choice, so nothing is asked; the episode is still recorded. The decision reads the pick list only, never a result.
6. **The first edit closes the card.** An `after_tool` edit to a non-test file after red closes an open card as `fix-started`, seals a held Room pick, and cancels a red run that has not been decided.
7. **Green** is the first passing test run after red whose command names the test, its file or folder, or no path at all. The fix files are the non-test files changed between the red and green snapshots. The fix run starts only for a held or sealed question: control on green (must pass), then the fix files put back as they were at red, then the test again.
8. **Score.** Not scored when the symptom scan finds an added sleep, an added bare or broad `except`, an added skip or xfail, or a removed or changed assert in a test file; when no non-test file changed; or when the test still passes with the fix undone. Otherwise a match when the picked file is a fix file, or the pick is "Somewhere else" and no listed file is. The fixed answer is "the file changed in this task": `outcome_kind` is `common` when a pick with `changed` (or, in an old record, a `note` holding "changed in this task") holds the fix.
9. **Never green.** A commit or branch switch with a sealed call still waiting writes `call.scored` unscored `never-green` and commits the question.
10. **Nothing goes to the agent but the question and the pending line.** The result arrives after the fix, so it is a deferred result and lives in the Room only. No finding is sent: the agent made the fix itself.
11. **Not built in 2b:** the line form (needs a reader), the Which change form (needs a bisect), the reproduction form, "Keep one of these as a review idea?", Wrong start and This result looks wrong on a Call it question (the Room hides both; the engine refuses them).

### 14.4 Copy added in 2b, for review

Lines `experience.md` does not give: the one-line form with fewer than three files (`Reply 1 to <n>`) and its work-computer form (link first, ending `Reply 1 to 4.`), the pending line `Firsthand: locked. Shown when <test> passes again. The result will be at <url>`, the Waiting row `shown when <test> passes again`, the trace title `<test>: <first line of the failure message>`, the result's More rows for the picks, `<n>  <path>` with `named in the trace`, `changed in this task` or both joined as `named in the trace, changed in this task` (never on the card), `What happened` as `The fix landed in <files>.` plus `With the fix undone, the test fails again.` or `... still passes.`, the cue `The fix is in <path>, which the trace names at line <n>.` or `The fix is in <path>, a file the failing trace never names.`, the symptom verbs `adds a broad except`, `removes or changes an assertion` and `adds a skip` beside the given `adds a sleep`, `Not scored. The test passed again with no change outside the tests, so there is no fix to undo.`, `Not scored. With the fix undone, the test still passes, so where the fix landed proves nothing about your call.`, the chat head `Firsthand, call it. <chip>. You said <answer>.`, the More row `fails again with the fix undone` or `still passes with the fix undone`, the Skills row texts `Naming where the cause is before the fix exists.` and `Bugs with no failing test.` (from `learning.md` section 2), and the engine errors `Wrong start is not offered on this question.` and `A Call it result cannot be rechecked yet.`

### 14.5 Known limits

- **A pasted failure is mostly closed before it is seen.** At `UserPromptSubmit` nothing can be shown to the person, only added to the model's context, so the question line waits for the next stop. An agent that starts editing in that turn closes the card first. The card is in the Room's Now group from the moment it is offered.
- **The question can arrive one stop late**, as in 13.5: the red run takes about a second, and the stop waits at most 300 ms.
- **A sealed call keeps the daemon awake** until its test goes green or the change ends, because the engine is not idle while a question is live.
- Green is read from the agent's passing run and its command line. A run that names the test with `-k` counts as covering it; the fix run's control catches a run that did not.

---

## 15. As built: step 2c, Brief

Step 2c adds the Brief on the 2a and 2b loop, following section 11. Where this section and sections 1 to 14 disagree, this section describes the code.

### 15.1 Files

| File | Holds |
| :- | :- |
| `firsthand/moments/brief.py` | The moment surface: `KIND = "brief"`, `SKILL = 5`, `HEADLINE = "DONE CHECK"`, `BREAKS = ("task_start",)`, `names_check`, `is_question`, `categories`, `qualifies`, `new_tests`, `first_test`, `score`, `finding`, `clean_line`, `is_dont_know`, `reply_words` and `parse_reply` (the confirm: yes or no) |
| `firsthand/engine_brief.py` | A mixin of `Engine`: the trigger watch, the offer, the line, the early and done-signal checks, the confirm, `release_brief`, the end of a change, resume after a restart |
| `firsthand/words_brief.py` | Every Brief line. `words.question_line`, `pending_line`, `result_lines` and `answer_text` dispatch to it on `m.kind` |
| `firsthand/views_brief.py` | The Brief card (line form and confirm form), its result, its Now and Waiting rows, the corrections and ask-tool questions |
| `tests/firsthand/test_core_brief.py`, `test_e2e_brief.py`, `fixtures_brief.py` | Unit tests, and the three fixtures replayed end to end with the rules |

`moments.REGISTRY` is `(revert_test, call_it, brief)`. `gitwatch.category(path)` gives the path categories of `learning.md` section 3.5 from fixed globs (`gitwatch.CATEGORIES`); the person cannot edit them yet.

### 15.2 Shared types and formats that changed

- `SpoolEvent.question`: on `before_tool` for the ask tool only, the texts of `tool_input.questions[].question` joined with ` / `, secret-scanned, cut to 2,000 characters. The spool's `before_tool` line gains the key `question`. `timeline` copies it onto the `task.event` of kind `ask`.
- `Want` gains `work` (the person's line for the agent, no key) and `confirm` ("Is this your check?", which names a test and carries no result). Both are no-key branches of `keys.agent_output`.
- `Record` accepts `call.confirmed` (`moment_kind`, `value` yes or no, `channel`, `test`).
- `call.sealed` for the Brief: `form: "line"`, `answer: "line"` (or `dont_know`), and `line`, the person's text after the secret scan, one line, at most 500 characters.
- `moment.offered` for the Brief: `form: "line"`, `skill: 5`, `break: "task_start"`, `tests: []`, plus `categories` and `plan`.
- `call.scored.unscored_reason` gains `no-test`, `no-change`, `not-your-check`, `never-done`, `no-confirm`, `moved-on` and `skipped`.
- `Session.brief` (the watch of the current task's first response, and a pending stop note) is kept in `run/state.json`. `Moment.extra` holds `phase` (`line`, `building`, `checking`, `confirm`, `done`), `line`, `categories`, `red_ids`, `early_tree`, `done_event`, `done_tree`, `test`, `confirm`, `confirm_channel` and `confirm_seen`.
- Queue items on `Session.queue` may carry `kind: "work"`; carried delivery kinds gain `work`, `sent`, `confirm` and `brief_note`, recorded as `line_delivered` with `line` `work`, `sent`, `question` and `result`.
- Views: the question view gains `form` (`line` or `pick`) and `said_label`; the result's `more` gains `notes` (corrections and agent questions). The Inbox's Now group holds the Brief while it asks for the line or the confirm, and Waiting holds it while the agent works. Skills gains the row "Framing the problem and the brief", whose `fixed` is null.

### 15.3 Behaviour

1. **Trigger.** A prompt that starts a task opens a watch, unless it names a test id, a test path or the runner of the test command, or ends with a question mark. Within the task's first response (until its first turn end), edits to non-test files in two or more path categories, or a plan tool call, offer the Brief. The 2a gates apply (dial, quiet, pressure, one a day across all moments, one per change, not on the first prompt of the day, two skips), and only pytest projects are asked.
2. **The line goes out at the next stop**, as a `systemMessage` like every other question (see 15.4 item 1).
3. **The reply.** While the line is open and has been seen, a next prompt that starts with `check:` is the answer (the marker is dropped), and `skip` or a quiet word act as usual. Any other prompt is a message to the agent: the line closes as `moved-on` and nothing is sent. "Don't know" seals with no line and sends nothing. Otherwise the line is sealed and the prompt reply adds, as agent-only context, `Done when: <line>. Write this check as a failing test first.`, then the print prefix and `Given to your agent: "<that line>"` with `Back to: <task>. Next: your agent has started.` The prompt is not consumed: it is the person's message to the agent and goes through the timeline. A line typed in the Room or with `firsthand answer` is queued and goes out with the next prompt.
4. **The check.** While the agent works, the Revert test asks nothing on this change. At the done signal the Brief owns, the Revert test's check still runs, silently and never offered, on the other new or edited tests since the Brief's base, so its note, its finding and a high-stakes fact line still come (`learning.md` 6.4 and 6.5). The first failing test run after the line records its failing ids. When the agent's own test run passes, the check starts early on that tree. At the next done signal the first test added since the task base is chosen: the first new test that failed first, else the first by path and line. The check is `revert_test.run` on a Candidate holding that one test (control on the result, then the non-test changes undone). If the done tree differs from the early run's tree, it runs again on the done tree.
5. **The confirm.** Once the control run passes, the stop carries `Firsthand: is this your check? <test>. Reply yes or no, or: <url>`. The key stays locked until yes or no. Yes: a match when the test fails on its assertion with the change undone, a miss when it still passes or cannot run. No: not scored, with the facts kept in `check.ran`. A next prompt that is not yes or no, or skip, settles it unscored (`moved-on`, `skipped`), facts kept.
6. **No test, no change.** At the done signal with no new test, or no non-test change, the call is settled unscored at once and that stop carries one line saying so.
7. **The result** in chat after yes or no, and in the Room. The Room's More lists correction prompts sent in the change after the done signal the check ran at, verbatim, and questions the agent asked through its ask tool after the offer.
8. **Endings.** A commit or branch switch settles a Brief still waiting: `never-done` before the done signal, `no-confirm` after it. Wrong start and This result looks wrong are refused for the Brief.
9. **After a restart** a live Brief in its checking or confirm phase keeps its key file, or runs its check again from the stored trees.

### 15.4 Where this differs from build-2.md and learning.md

1. **The question is a `systemMessage` at the next stop, not context on the next `UserPromptSubmit`.** Sections 4 and 11 of `build-2.md` and section 11 of this contract call it agent-only text. The person has to see the line to answer it, and context added to a prompt reaches only the model, at a prompt that comes after the turn has ended. The stop is the first point the person can see it, and `experience.md` section 5.3 shows it as a Firsthand line in the agent. The work product (the person's line) does go to the agent as context on `UserPromptSubmit`, as specified.
2. **No `send-to-agent` route.** The Room sends the line with the existing `POST /api/q/<ref>/lock`, which for the Brief is always final: the line is work product, not a prediction, so decision 10's held pick does not apply. The confirm is final too.
3. **The check is run before the confirm, the result shown after it.** `learning.md` section 4.3 says the check runs "on yes". It runs as soon as the done signal (or the agent's passing run) gives a tree, and the confirm is asked once its control run passes, so the result is usually ready when the person says yes. Being asked never depends on what the undone run finds.
4. **"Cannot run" is a miss.** `learning.md` section 7.1 scores a match only when the check fails on its assertion without the change. A test that cannot run without the new code shows the code exists, not that it is right.
5. **The Brief counts only on the Framing row.** `PRODUCT.md` lists it under Verification too. The Skills view shows it under skill 5 alone, so one call is not counted twice.
6. **Path categories are fixed globs** and tests do not count as a category, so a one-file fix with its test never triggers.
7. **The Framing row has no level.** A Brief has no fixed answer, so no call of it is a catch and `learning.md` 8.3's "Shown" could never be reached. The row says "No level yet" until what a catch is for a made check is decided (`learning.md` 8.2).
8. **Paths changed outside the first edits' categories** are listed as one More note, from the check's undone paths.

### 15.5 Copy added in 2c, for review

Lines `experience.md` and `prototypes/brief.html` do not give: the confirm line's ending `Reply yes or no, or: <url>`; the Room card's footers `It goes to your agent as written. Checked by a run when your agent finishes: your test with the change, then with the change undone.` and `Checked by a run, no model: the change undone, your test kept.`; the Room button `Send to my agent`; the field label `Your check`; the status lines `Given to your agent. Shown when your agent finishes.` and `Locked. The check is still running.`; the Waiting rows `shown when your agent finishes` and `the check is still running`; `What happened` for a check that cannot run, `Passes now. It cannot run with the change undone, which is weak proof.` (without `It cannot tell done from not done.`, which experience.md 5.3 gives only to a check that passes with the change undone); the More row texts `fails on its assertion with the change undone`, `still passes with the change undone`; the counts line without a fixed answer; the unscored reasons `Not scored. No test was added in this task, so your check was not run.`, `Not scored. Nothing outside the tests changed, so there was no change to undo.`, `Not scored. The change ended before your agent finished.`, `Not scored. The change ended before you said whether this is your check.`; the stop lines `Firsthand: your agent finished, and no test was added for your check, so it was not run. Nothing was scored.` and the no-change form; the chat head for "no", `Firsthand, done check. Not scored.` followed by the prototype's `I could not find your check among the new tests.`; the Skills row texts `Writing a done check that fails without the change.` and `Whether the goal was the right goal.` (from `learning.md` section 2); and the engine errors `Write your check in one line.`, `Reply with one of: yes, no. Or skip.` and `A done check result cannot be rechecked yet.` The skill file gains a "Done when" section.

### 15.6 Known limits

- **The Brief usually arrives after the first response.** Claude Code agents often finish a whole task in one turn. The line still comes at that turn end and the check still runs at the next done signal, but "fails now" may no longer be true by then. Plan mode and a turn that ends on a question give it its intended place.
- **The line needs the `check:` marker in chat.** Without it a reply cannot be told from an answer to the agent's own question at the same turn end, which used to be sent as the done check. A person who types the check without the marker loses the question for this change.
- **The confirm can arrive one stop late**, as in 13.5, when the control run has not passed within the stop's 300 ms.
- **A live Brief keeps the daemon awake** until the done signal or the end of the change.

---

## 16. As built: two scoring fixes

Where this section and sections 1 to 15 disagree, this section describes the code.

### 16.1 Revert test with several tests: the answer is a set

The question used to ask "Which one would still pass with the change undone?", as if at most one could. With two tests that still pass, either pick was a match.

- **The rule.** With two or more tests the answer is a set of test numbers, possibly empty. It is a match only when it equals the set of tests whose result is `still_passes`; anything else is a miss. "Don't know" is never scored. The one-test form (fails, passes, don't know) is unchanged. `outcome_kind` is still `uncommon` when any test still passes, so "Always answering none" is still the fixed answer and its counts line is unchanged.
- **The stored form.** `Answer` is now a plain `str`. A set is its numbers ascending, joined by commas (`"1,3"`); one number stays `"2"`; the empty set is `"none"`. `revert_test.picked_numbers` reads it back and refuses duplicates and numbers out of range. A record from before this change holds one number and reads as a set of one.
- **Where answers enter.** Chat replies, the Room's `POST /api/q/<ref>/lock` and `firsthand answer` all go through `revert_test.parse_reply`, which accepts `1`, `1 3`, `1,3`, `1 and 3`, `1, 2 and 3`, `none` and `don't know`, each optionally followed by `sure` or `not sure`. A reply it refuses gets `Reply the numbers, none or don't know. Or skip.`
- **Copy.** The prompt is `Which of them would still pass with the change undone?` and the chat line ends `Reply the numbers, or none.` `You said` names every pick: `1 and 3, test_a and test_c.` What happened names every test that still passes (`test_a and test_c still pass with the change undone.`), keeps `It still passes with the change undone. It would pass whether or not the change exists.` when the one test that still passes is exactly the pick, and with none passing gives each picked test's result in one line. The miss cue is about a still-passing test the person left out, else about a picked test that does not still pass (the fail cue).
- **The Room.** The question view gains `multi` (true for the several-tests form, false elsewhere). With `multi` the numbers are toggle buttons with `aria-pressed`; None and Don't know are exclusive and clear them; a Lock button sends the answer. No toggle and no key press locks. The held, Undo, How sure and Show the result flow is unchanged, and the held and sealed card shows the chosen toggles pressed. `firsthand room --tty` prints the same reply hint.

### 16.2 Call it: the picks say nothing before the result

Each pick used to carry a note, "named in the trace" or "changed in this task". When the agent's own edit broke the test, the note marked the answer.

- The picks store `traced` and `changed` (booleans) in `moment.offered`, `Moment.extra` and the key's extra. No card, chat line or API view of an open, held or sealed question shows them. Old records with a `note` string still read (`call_it.pick_facts`), for scoring the fixed answer.
- After the result, `more.rows` lists each pick after the test row: `<n>  <path>` with its facts.
- Nothing is asked when fewer than two files would be listed (`call_it.worth_asking`, which reads the pick list only). The episode is still recorded.
