"""The `firsthand` command.

`hook` is routed before anything else is imported, so a hook costs one
interpreter start and a few small imports. Every other command talks to the
daemon through `client.call`, except `init`, `uninstall` and `daemon`.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence

MAX_ANCESTORS = 16
DIAL_LABELS = {
    "off": "Off",
    "notes": "Notes only",
    "standard": "Standard",
    "deep": "Deep",
}
OFF_LINE = 'Firsthand is off. It asks, runs and records nothing. It keeps your record. Say "firsthand on" to turn it on.'


# ------------------------------------------------------------- agent check


def _proc_parent(pid: int) -> tuple[int, str] | None:
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8", errors="replace") as handle:
            stat = handle.read()
    except OSError:
        return None
    left, right = stat.find("("), stat.rfind(")")
    if left < 0 or right < 0:
        return None
    fields = stat[right + 2 :].split()
    return (int(fields[1]), stat[left + 1 : right]) if len(fields) > 1 else None


def _ps_parent(pid: int) -> tuple[int, str] | None:
    import subprocess

    try:
        done = subprocess.run(
            ["ps", "-o", "ppid=,comm=", "-p", str(pid)],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    parts = done.stdout.strip().split(None, 1)
    if len(parts) != 2 or not parts[0].isdigit():
        return None
    return int(parts[0]), os.path.basename(parts[1].strip())


def _ancestor_names() -> list[str]:
    lookup = _proc_parent if os.path.isdir("/proc/self") else _ps_parent
    names: list[str] = []
    pid = os.getppid()
    for _ in range(MAX_ANCESTORS):
        if pid <= 1:
            break
        found = lookup(pid)
        if found is None:
            break
        parent, name = found
        names.append(name)
        pid = parent
    return names


def under_agent(
    environ: Mapping[str, str] | None = None, ancestors: Sequence[str] | None = None
) -> bool:
    """True when this process runs inside a coding agent."""
    from firsthand.hooks import ADAPTERS

    environ = os.environ if environ is None else environ
    markers = [m for adapter in ADAPTERS.values() for m in adapter.ENV_MARKERS]
    if any(environ.get(m) not in (None, "", "0") for m in markers):
        return True
    names = {n for adapter in ADAPTERS.values() for n in adapter.PROCESS_NAMES}
    found = _ancestor_names() if ancestors is None else ancestors
    return any(os.path.basename(a) in names for a in found)


# --------------------------------------------------------------- printing


def _out(*lines: str) -> None:
    for line in lines:
        print(line)


def _err(message: str) -> None:
    print(message, file=sys.stderr)


def tilde(path: object) -> str:
    """A path under the home folder written with ~."""
    from firsthand import paths

    text = str(path)
    home = str(paths.user_home())
    if text == home:
        return "~"
    if text.startswith(home.rstrip("/") + "/"):
        return "~" + text[len(home.rstrip("/")) :]
    return text


def _call(op: str, args: Mapping[str, object] | None = None, **kw: object) -> dict:
    from firsthand import client

    return client.call(op, args, cwd=os.getcwd(), **kw)  # type: ignore[arg-type]


# --------------------------------------------------------------- commands


def _cmd_answer(ns: object) -> int:
    result = _call("answer", {"text": " ".join(ns.text)}, agent=under_agent())  # type: ignore[attr-defined]
    _out(*result.get("lines", []))
    return 0


def _cmd_skip(ns: object) -> int:
    result = _call("skip", agent=under_agent())
    _out(*result.get("lines", []))
    return 0


def _status_lines(view: Mapping[str, object]) -> list[str]:
    lines = []
    question = view.get("question")
    if isinstance(question, dict) and question.get("line"):
        lines.append(f"Open question: {question['line']}")
    else:
        lines.append("No question is open.")
    lines.append(
        f"Asked today: {view.get('asked_today', 0)} of {view.get('daily_limit', 1)}."
    )
    dial = str(view.get("dial", "standard"))
    lines.append(f"Dial: {DIAL_LABELS.get(dial, dial)}.")
    scopes = view.get("quiet_scopes") or ([view["quiet"]] if view.get("quiet") else [])
    if scopes:
        labels = {"session": "this session", "today": "today", "here": "this project"}
        lines.append(f"Quiet: {', '.join(labels.get(x, x) for x in scopes)}.")
    lines.extend(_project_lines(view.get("project")))
    room = view.get("room")
    lines.append(
        f"Firsthand is running. Room: {room}"
        if room
        else "Firsthand is running. The Room is not."
    )
    return lines


def _project_lines(project: object) -> list[str]:
    if not isinstance(project, dict):
        return ["This folder is not in a git project."]
    lines = [f"Project: {project.get('name')}."]
    command = project.get("test_command")
    if command:
        lines.append(f"Test command: {command}")
    else:
        lines.append(
            "No test command is set, so most questions cannot run here. "
            'Set one with: firsthand config test-command "<command>"'
        )
    if project.get("watched") is False and project.get("why_not"):
        lines.append(f"Not watched: {project['why_not']}.")
    return lines


def _cmd_status(ns: object) -> int:
    from firsthand import client

    try:
        view = _call("status", start=False, agent=under_agent())
    except client.DaemonUnavailable:
        _out("Firsthand is not running. It starts at the next prompt in your agent.")
        return 0
    _out(*_status_lines(view))
    return 0


def _journal_lines(view: Mapping[str, object]) -> list[str]:
    entries = view.get("entries") or []
    if not entries:
        return ["Nothing in the journal yet."]
    lines = [f"Journal: {view.get('scope')}"]
    for entry in entries:
        chip = f"  {entry['chip_label']}" if entry.get("chip_label") else ""
        lines.append(
            f"{entry.get('date')}  {entry.get('kind')}  {entry.get('task')}{chip}"
        )
        for row in entry.get("rows") or []:
            lines.append(f"  {row.get('label')}: {row.get('text')}")
    return lines


def _cmd_journal(ns: object) -> int:
    _out(*_journal_lines(_call("journal", {"limit": 200}, agent=under_agent())))
    return 0


_SKILL_FIELDS = ("level_line", "counts", "fixed", "asked", "newest", "checked")


def _skills_lines(view: Mapping[str, object]) -> list[str]:
    lines: list[str] = [str(x) for x in view.get("legend") or []]  # type: ignore[union-attr]
    if lines:
        lines.append("")
    for row in view.get("rows") or []:
        lines.append(f"{row.get('n')}. {row.get('name')}")
        lines.extend(f"  {row[k]}" for k in _SKILL_FIELDS if row.get(k))
        if row.get("covers"):
            lines.append(f"  Covers: {row['covers']}")
        if row.get("no_evidence"):
            lines.append(f"  No evidence yet on: {row['no_evidence']}")
    return lines


def _cmd_skills(ns: object) -> int:
    _out(*_skills_lines(_call("skills", agent=under_agent())))
    return 0


def _cmd_quiet(ns: object) -> int:
    result = _call("quiet", {"scope": ns.scope, "on": True}, agent=under_agent())  # type: ignore[attr-defined]
    _out(*result.get("lines", []))
    return 0


def _cmd_off(ns: object) -> int:
    _call("settings_set", {"changes": {"dial": "off"}}, agent=under_agent())
    _out(OFF_LINE)
    return 0


def _cmd_on(ns: object) -> int:
    from firsthand.config import ConfigStore

    before = ConfigStore().load().dial_before_off
    dial = before if before != "off" else "standard"
    view = _call("settings_set", {"changes": {"dial": dial}}, agent=under_agent())
    dial = str(view.get("dial", dial))
    _out(f"Firsthand is on: {DIAL_LABELS.get(dial, dial)}.")
    return 0


def _here_project() -> dict:
    from firsthand.model import FirsthandError

    project = _call("status", agent=under_agent()).get("project")
    if not isinstance(project, dict) or not project.get("id"):
        raise FirsthandError(
            "This folder is not in a git project with a commit. Run it from inside your project."
        )
    return project


def _cmd_config(ns: object) -> int:
    project = _here_project()
    key = "test_command" if ns.what == "test-command" else "high_stakes_add"  # type: ignore[attr-defined]
    changes = {key: ns.value}  # type: ignore[attr-defined]
    view = _call(
        "settings_set",
        {"changes": changes, "project": project["id"]},
        agent=under_agent(),
    )
    shown = view.get("project") if isinstance(view.get("project"), dict) else {}
    name = shown.get("name") or project.get("name")
    if key == "test_command":
        _out(f"Test command for {name}: {shown.get('test_command') or ns.value}")  # type: ignore[attr-defined]
    else:
        globs = ", ".join(shown.get("high_stakes") or [ns.value])  # type: ignore[attr-defined]
        _out(f"High stakes for {name}: {globs}")
    return 0


def _cmd_room(ns: object) -> int:
    if ns.tty:  # type: ignore[attr-defined]
        return _room_tty()
    import webbrowser

    # The CLI keeps the one-time URL out of an agent itself: it opens the browser
    # and prints the URL only when no agent is reading this output.
    url = _call("room_ticket", {"next": "/"}, agent=False)["url"]
    opened = webbrowser.open(url)
    if opened:
        _out("The Room is open in your browser.")
    elif under_agent():
        from firsthand import install

        _out(
            "No browser could be opened from here. In a terminal you opened, run: "
            f"{install.command()} room"
        )
    else:
        _out(url)
    return 0 if opened or not under_agent() else 1


def _cmd_uninstall(ns: object) -> int:
    from firsthand import install, paths

    _stop_daemon()
    report = install.uninstall()
    for path in report.restored:
        _out(f"Restored {tilde(path)}")
    for path in report.removed:
        _out(f"Removed {tilde(path)}")
    for path, diff in report.refused:
        _out(
            f"Not restored, because it changed since install: {tilde(path)}",
            diff.rstrip("\n"),
        )
    if report.refused:
        _out(
            "Nothing was removed or restored, so Firsthand stays installed as it was.",
            "Undo those changes or restore the file by hand, then run: firsthand uninstall",
        )
    _out(f"Your record is kept at {tilde(paths.record_dir())}.")
    return 1 if report.refused else 0


def _cmd_daemon(ns: object) -> int:
    from firsthand import daemon

    return daemon.main()


def _stop_daemon() -> None:
    import time

    from firsthand import client, daemon
    from firsthand.model import FirsthandError

    if not daemon.is_running():
        return
    try:
        client.call("stop", start=False)
    except FirsthandError:
        return
    deadline = time.monotonic() + 3.0
    while daemon.is_running() and time.monotonic() < deadline:
        time.sleep(0.05)


# --------------------------------------------------------------- room --tty


def _reply_words(view: Mapping[str, object]) -> str:
    words = [
        "don't know" if p.get("value") == "dont_know" else str(p.get("value"))
        for p in view.get("picks") or []
    ]
    return ", ".join(words)


def _question_text(view: Mapping[str, object]) -> list[str]:
    lines = [str(view.get("context") or ""), str(view.get("lead") or "")]
    for item in view.get("evidence") or []:
        lines.append(
            f"  {item.get('n')}. {item.get('name')}  {item.get('path')}:{item.get('line')}"
        )
        lines.extend(
            f"       {a.get('line')}: {a.get('text')}"
            for a in item.get("asserts") or []
        )
    lines.append(str(view.get("prompt") or ""))
    if view.get("multi"):
        from firsthand.moments import revert_test

        lines.append(revert_test.SET_HINT)
    else:
        lines.append(f"Reply with one of: {_reply_words(view)}. Or skip.")
    return [line for line in lines if line]


def _result_lines(result: Mapping[str, object]) -> list[str]:
    lines = [f"{result.get('headline')}  {result.get('chip_label')}"]
    if result.get("reason"):
        lines.append(str(result["reason"]))
    lines.append(f"You said: {result.get('you_said')}")
    lines.extend(str(x) for x in result.get("what_happened") or [])  # type: ignore[union-attr]
    cue = result.get("cue")
    if isinstance(cue, dict) and cue.get("text"):
        lines.append(f"What would have shown it: {cue['text']}")
    lines.append(str(result.get("back") or ""))
    return [line for line in lines if line]


def _result_text(view: Mapping[str, object]) -> list[str]:
    result = view.get("result")
    if isinstance(result, dict):
        return _result_lines(result)
    if view.get("say"):
        return [str(x) for x in view["say"]]
    return [str(view["status_line"])] if view.get("status_line") else []


def _room_tty() -> int:
    from firsthand.model import FirsthandError

    if under_agent():
        from firsthand import install

        raise FirsthandError(
            "This reads your answer from a terminal. In a terminal you opened, run: "
            f"{install.command()} room --tty"
        )
    view = _call("question", agent=False)
    if view.get("result"):
        _out(*_result_text(view))
        return 0
    _out(*_question_text(view))
    try:
        text = input("> ").strip()
    except EOFError:
        text = ""
    if not text:
        return 0
    if text.lower() == "skip":
        _out(*_call("skip", agent=False).get("lines", []))
        return 0
    _out(
        *_result_text(
            _call("answer_room", {"ref": view["ref"], "text": text}, agent=False)
        )
    )
    return 0


# ------------------------------------------------------------------- init

WORK_QUESTION = (
    "Is this a work computer? [Y/n]",
    "  Enter means yes: answers stay out of your agent's chat by default,",
    "  and nothing is sent to a model without asking you.",
)
WORK_NOTICE = (
    "This is a work computer. Here is what your employer can and cannot see.",
    "Can: that Firsthand is installed, and the files it adds to your agents.",
    "Can, through your agent's logs: anything typed or printed in your agent's chat,",
    "  including Firsthand's question lines and findings.",
    "Can, if they manage this computer: your record. It is plain files in ~/.firsthand.",
    "So on this computer, question links come first and the inline card is off,",
    "  and no text is sent to a model unless you say yes.",
    "Firsthand has no admin view, no reports and no account.",
)
NO_TEST_COMMAND = (
    "No test command is set, so most questions cannot run here. Set one in Settings."
)
TEST_COMMAND_QUESTION = "What command runs this project's tests? (Enter to skip) "


def _plan_lines(writes: Sequence[object]) -> list[str]:
    from firsthand import paths

    shown = []
    for w in writes:
        path = w.path  # type: ignore[attr-defined]
        label = (
            tilde(path.parent) + "/"
            if path == paths.claude_skill_file()
            else tilde(path)
        )
        shown.append((label, w.summary))  # type: ignore[attr-defined]
    width = max(len(label) for label, _ in shown) + 2
    lines = ["Firsthand will add itself to Claude Code. It will write these files:"]
    lines.extend(f"  {label.ljust(width)}{summary}" for label, summary in shown)
    lines.append(
        f'Backups go to {tilde(paths.backups_dir())}. "firsthand uninstall" restores them.'
    )
    lines.append(
        "Hooks only report what happened. They never allow, deny or block anything."
    )
    return lines


def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return ""


def _confirm_plan(writes: Sequence[object]) -> bool:
    from firsthand import install

    while True:
        answer = _ask("Go ahead? [Y/n]  (d shows the exact changes) ")
        if answer in ("", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        if answer == "d":
            for w in writes:
                _out(install.diff_text(w).rstrip("\n"))  # type: ignore[arg-type]


def _work_computer(choice: str | None, interactive: bool) -> bool:
    if choice is not None:
        return choice == "yes"
    if not interactive:
        return True
    _out(*WORK_QUESTION)
    while True:
        answer = _ask("")
        if answer in ("", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False


def _set_up_project(store: object, test_command: str | None, interactive: bool) -> None:
    from firsthand import gitwatch

    root = gitwatch.project_root(os.getcwd())
    pid = gitwatch.project_id(root) if root is not None else None
    if pid is None:
        return
    project = store.ensure_project(pid, str(root))  # type: ignore[attr-defined]
    if not test_command and project.test_command is None and interactive:
        test_command = input(TEST_COMMAND_QUESTION).strip() or None
    if test_command:
        project = store.set_project(pid, "test_command", test_command)  # type: ignore[attr-defined]
    if project.test_command is None:
        _out(NO_TEST_COMMAND)


def _dial_sentence(settings: object) -> str:
    dial = settings.dial  # type: ignore[attr-defined]
    limit = settings.daily_limit  # type: ignore[attr-defined]
    if dial in ("standard", "deep"):
        noun = "question" if limit == 1 else "questions"
        return f"It is on {DIAL_LABELS[dial]}: at most {limit} {noun} a day."
    if dial == "notes":
        return "It is on Notes only: the checks with no questions."
    return "It is off."


def _closing_lines(settings: object, room: str) -> list[str]:
    from firsthand import paths

    return [
        f"Firsthand is set up in Claude Code. {_dial_sentence(settings)}",
        '"Notes only" gives you the checks with no questions. Change it in Settings.',
        "",
        f"Your record: {tilde(paths.record_dir())}. A git repo on this machine, outside your projects,",
        "with no remote. Plain files: anyone who can read your home folder can read it.",
        f"Your Room: {room}  A page served by this computer, for you only.",
        # 2a has no package-name lookups and no "firsthand privacy" command, so the
        # experience.md sentence that names them is cut to what is true now.
        "Firsthand sends nothing anywhere except the lines it adds to your agent's chat.",
        "",
        'Say "skip" to pass on a question. Say "firsthand off" to stop everything.',
        *_command_lines(),
    ]


def _command_lines() -> list[str]:
    """Where the firsthand command is, when it is not on PATH."""
    from firsthand import install

    cmd = install.command()
    if cmd == "firsthand":
        return []
    folder = cmd.rsplit("/", 1)[0]
    return [
        f"In a terminal the command is {cmd}, for example: {cmd} status",
        f"Add {folder} to your PATH to type just firsthand.",
    ]


def _cmd_init(ns: object) -> int:
    from datetime import UTC, datetime

    from firsthand import __version__, config, install, paths, record

    launcher = install.launcher_path(__version__)
    writes = install.plan(launcher)
    interactive = sys.stdin.isatty()
    _out(*_plan_lines(writes))
    if not ns.yes and not interactive:  # type: ignore[attr-defined]
        _out("Run again with --yes to write these files.")
        return 0
    if not ns.yes and not _confirm_plan(writes):  # type: ignore[attr-defined]
        _out("Nothing was written.")
        return 0
    work = _work_computer(ns.work_computer, interactive and not ns.yes)  # type: ignore[attr-defined]
    _stop_daemon()
    launcher = install.install_engine(__version__)
    paths.ensure_private_dirs()
    rec = record.Record(record.ensure_record())
    store = config.ConfigStore(commit=rec.commit)
    port = config.read_port()
    if port is None:
        port = config.choose_port()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    install.apply(install.plan(launcher), launcher=launcher, stamp=stamp)
    settings = store.set("work_computer", work)
    if work:
        _out("", *WORK_NOTICE)
    _out("")
    _set_up_project(store, ns.test_command, interactive and not ns.yes)  # type: ignore[attr-defined]
    _out(*_closing_lines(settings, f"http://127.0.0.1:{port}"))
    return 0


# ----------------------------------------------------------------- parser


def _parser() -> object:
    import argparse

    parser = argparse.ArgumentParser(
        prog="firsthand", description="Firsthand, on this computer."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Add Firsthand to Claude Code")
    init.add_argument(
        "--yes", action="store_true", help="Write the files without asking"
    )
    init.add_argument("--work-computer", choices=("yes", "no"))
    init.add_argument("--test-command")
    room = sub.add_parser("room", help="Open the Room")
    room.add_argument(
        "--tty", action="store_true", help="Show the open question in this terminal"
    )
    answer = sub.add_parser("answer", help="Answer the open question")
    answer.add_argument("text", nargs="+")
    for name in (
        "skip",
        "status",
        "journal",
        "skills",
        "off",
        "on",
        "uninstall",
        "daemon",
    ):
        sub.add_parser(name)
    quiet = sub.add_parser("quiet", help="Stop questions for a while")
    quiet.add_argument(
        "scope", nargs="?", default="session", choices=("session", "today", "here")
    )
    config = sub.add_parser("config", help="Project settings")
    config.add_argument("what", choices=("test-command", "high-stakes"))
    config.add_argument("value")
    return parser


_COMMANDS = {
    "init": _cmd_init,
    "room": _cmd_room,
    "answer": _cmd_answer,
    "skip": _cmd_skip,
    "status": _cmd_status,
    "journal": _cmd_journal,
    "skills": _cmd_skills,
    "quiet": _cmd_quiet,
    "off": _cmd_off,
    "on": _cmd_on,
    "config": _cmd_config,
    "uninstall": _cmd_uninstall,
    "daemon": _cmd_daemon,
}


def _run_hook(args: Sequence[str]) -> int:
    from firsthand import hooks

    if len(args) != 2:
        return 0
    return hooks.main(args[0], args[1], sys.stdin.buffer, sys.stdout)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["hook"]:
        return _run_hook(args[1:])
    ns = _parser().parse_args(args)  # type: ignore[attr-defined]
    from firsthand.model import FirsthandError

    try:
        return _COMMANDS[ns.command](ns)
    except FirsthandError as exc:
        _err(exc.message)
        return 1
