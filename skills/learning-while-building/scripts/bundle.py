"""Moving the record: out of the project (`move`), between machines (`export`,
`import-bundle`), and saying where it is (`where`).

An older version of the skill kept the record in `.learning/` inside the
project and told people to commit it. That folder holds every answer the
learner got wrong, so in a shared repo anyone with access can read it. `move`
copies it to the home record and says plainly what removing the old folder does
and does not undo. It changes nothing in the project itself.

A cloud session's container is thrown away when the session ends. `export`
prints the record as one JSON document, and `import-bundle` merges that document
into the record on the learner's own machine.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

from record import (
    LEGACY_DIR,
    RULE_HOME,
    TOPIC_ID,
    RecordError,
    after_write,
    commit_home,
    ensure_home,
    git,
    holds_record,
    home_dir,
    home_record_dir,
    inside_home,
    is_legacy,
    load_attempts,
    load_record,
    project_key,
    read_json,
    record_problems,
    resolve_dir,
    save_attempt,
    save_dimensions,
    save_topic,
)

BUNDLE_FORMAT = "learning-bundle 1"
# An attempt id becomes a file name, so a bundle may not carry a path in one.
ATTEMPT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def shown(path: Path) -> str:
    """A path with the home folder written as ~, as people type it."""
    try:
        return "~/" + str(path.resolve().relative_to(Path.home().resolve()))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------- move


def removal_commands(tracked: bool) -> list[str]:
    if not tracked:
        return ["  rm -rf .learning"]
    return [
        "  git rm -r --cached .learning",
        "  rm -rf .learning",
        '  git commit -m "Remove learning record"',
    ]


def history_lines(commits: int, remote: str | None) -> list[str]:
    """What removing the folder does not undo, read from git."""
    if not commits:
        return ["It was never committed, so no copy exists in git."]
    times = "1 time" if commits == 1 else f"{commits} times"
    lines = ["That removes it from now on. It does not remove it from history."]
    if remote:
        lines += [
            f".learning/ was committed {times} and this repo has a remote ({remote}),",
            "so copies exist in history, on the remote, and in any clone or fork.",
            "If you own this repo and want it gone from history:",
            "  git filter-repo --invert-paths --path .learning",
            "  then force-push, and ask every collaborator to clone again.",
            (
                "If you do not own it, the owner has to do this. "
                "Until then the old answers stay readable there."
            ),
        ]
    else:
        lines += [
            f".learning/ was committed {times} and this repo has no remote,",
            "so copies exist in this repo's history and in any clone of it.",
            "If you want it gone from history:",
            "  git filter-repo --invert-paths --path .learning",
        ]
    return lines


def git_facts() -> tuple[int, str | None, bool]:
    """Commits that touched .learning, the first remote, and whether it is tracked."""
    count = git("rev-list", "--count", "HEAD", "--", LEGACY_DIR)
    remotes = (git("remote") or "").split()
    tracked = bool(git("ls-files", LEGACY_DIR))
    return (
        int(count) if count and count.isdigit() else 0,
        (remotes[0] if remotes else None),
        tracked,
    )


def copy_checked(source: Path, target: Path) -> tuple[int, int]:
    """Copy the record and run `check` on the copy. A bad copy is deleted."""
    shutil.copytree(source, target, dirs_exist_ok=True)
    try:
        data, attempts = load_record(target), load_attempts(target)
        problems = record_problems(data, attempts)
    except RecordError as exc:
        problems = [str(exc)]
    if problems:
        shutil.rmtree(target)
        raise RecordError(
            "The record in ./.learning has problems, so nothing was moved. "
            "Run `learning.py check` to see them: " + "; ".join(problems)
        )
    return len(data["topics"]), len(attempts)


def cmd_move(args: argparse.Namespace) -> None:
    source = Path(LEGACY_DIR)
    if not is_legacy(Path.cwd()):
        raise RecordError(
            "No record in ./.learning here. Run `move` from the project root "
            "that holds it. Nothing was changed."
        )
    if not (source / "dimensions.json").exists():
        raise RecordError(
            "./.learning uses the old single-file format. Run `learning.py migrate` "
            "first, then `move`. Nothing was changed."
        )
    target = home_record_dir()
    if holds_record(target):
        raise RecordError(
            f"A record for this project already exists at {target}. Nothing was changed."
        )
    ensure_home()
    topics, attempts = copy_checked(source, target)
    commit_home(target, f"move {target.name}")
    commits, remote, tracked = git_facts()
    lines = [
        (
            f"Moved {plural(topics, 'topic')} and {plural(attempts, 'attempt')} "
            f"to {shown(target)}"
        ),
        "From now on the record is read from there.",
        "",
        "The old folder is still in your project. To remove it:",
        *removal_commands(tracked),
        "",
        *history_lines(commits, remote),
    ]
    print("\n".join(lines))
    if os.environ.get("LEARNING_DIR"):
        print(
            f"LEARNING_DIR is set, so commands still read {os.environ['LEARNING_DIR']} "
            "until you unset it."
        )


# ---------------------------------------------------------------- export, import


def bundle_key(root: Path) -> str:
    """The project key: the record's folder name in the home, else from git."""
    if inside_home(root) and root.resolve().parent.name == "projects":
        return root.resolve().name
    return project_key()


def cmd_export(args: argparse.Namespace) -> None:
    root = data_dir_checked(args.dir)
    data = load_record(root)
    attempts = {
        p.stem: read_json(p) for p in sorted((root / "attempts").glob("*.json"))
    }
    bundle = {
        "format": BUNDLE_FORMAT,
        "project_key": bundle_key(root),
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dimensions": data["dimensions"],
        "topics": data["topics"],
        "attempts": attempts,
    }
    print(json.dumps(bundle, indent=2))


def data_dir_checked(arg: str | None) -> Path:
    root = resolve_dir(arg)[0]
    load_record(root)
    return root


def parse_bundle(text: str) -> dict:
    try:
        bundle = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RecordError(
            f"The bundle is not valid JSON ({exc}). Nothing was imported."
        ) from exc
    if not isinstance(bundle, dict) or bundle.get("format") != BUNDLE_FORMAT:
        raise RecordError(
            f'The bundle\'s format is not "{BUNDLE_FORMAT}". Nothing was imported.'
        )
    shapes = (("dimensions", list), ("topics", dict), ("attempts", dict))
    for field, kind in shapes:
        if not isinstance(bundle.get(field), kind):
            raise RecordError(
                f"The bundle has no valid {field!r}. Nothing was imported."
            )
    return bundle


def bundle_problems(bundle: dict, merged: dict) -> list[str]:
    """The field checks `check` runs, plus ids that are safe as file names."""
    problems = [
        f"dimension {d!r} is not a name"
        for d in bundle["dimensions"]
        if not isinstance(d, str)
    ]
    for tid, topic in bundle["topics"].items():
        if not TOPIC_ID.match(tid) or not isinstance(topic, dict):
            problems.append(f"topic {tid!r} is not a valid topic")
    for key, attempt in bundle["attempts"].items():
        if not ATTEMPT_ID.match(key) or not isinstance(attempt, dict):
            problems.append(f"attempt {key!r} is not a valid attempt")
    if problems:
        return problems
    attempts = {
        k: dict(a, graded=a.get("graded")) for k, a in bundle["attempts"].items()
    }
    return record_problems(merged, attempts)


def current_record(root: Path) -> tuple[dict, dict]:
    if not holds_record(root):
        return {"dimensions": [], "topics": {}}, {}
    return load_record(root), load_attempts(root)


def merge_bundle(root: Path, bundle: dict) -> tuple[int, int, int]:
    """Union the dimensions; keep existing topics and attempts. Refuses before writing."""
    data, attempts = current_record(root)
    dims = data["dimensions"] + [
        d for d in bundle["dimensions"] if d not in data["dimensions"]
    ]
    merged = {"dimensions": dims, "topics": {**bundle["topics"], **data["topics"]}}
    problems = bundle_problems(bundle, merged)
    if problems:
        raise RecordError(
            "The bundle was refused, nothing was imported: " + "; ".join(problems)
        )
    new_topics = [t for t in bundle["topics"] if t not in data["topics"]]
    new_attempts = [a for a in bundle["attempts"] if a not in attempts]
    if not holds_record(root) and inside_home(root):
        ensure_home()
    if not holds_record(root):
        for sub in ("topics", "attempts"):
            (root / sub).mkdir(parents=True, exist_ok=True)
    save_dimensions(root, dims)
    for tid in new_topics:
        save_topic(root, tid, bundle["topics"][tid])
    for key in new_attempts:
        save_attempt(root, bundle["attempts"][key])
    skipped = (
        len(bundle["topics"])
        + len(bundle["attempts"])
        - len(new_topics)
        - len(new_attempts)
    )
    return len(new_topics), len(new_attempts), skipped


def cmd_import_bundle(args: argparse.Namespace) -> None:
    root = resolve_dir(args.dir)[0]
    text = (
        sys.stdin.read()
        if args.file == "-"
        else Path(args.file).read_text(encoding="utf-8")
    )
    topics, attempts, skipped = merge_bundle(root, parse_bundle(text))
    print(
        f"Imported {plural(topics, 'topic')} and {plural(attempts, 'attempt')}. "
        f"Skipped {skipped} already recorded."
    )
    after_write(args.dir, "import-bundle")


# ---------------------------------------------------------------- where


def cmd_where(args: argparse.Namespace) -> None:
    root, rule = resolve_dir(args.dir)
    print(root.resolve())
    print(f"Chosen by: {rule}" + (f" ({home_dir()})" if rule == RULE_HOME else ""))
    if not holds_record(root):
        print("No record there yet. Run `learning.py init` to create it.")
    if rule == RULE_HOME and is_legacy(Path.cwd()):
        print("An old record is still in ./.learning. It is no longer read.")


# ---------------------------------------------------------------- cli


def add_commands(sub: argparse._SubParsersAction) -> None:
    sub.add_parser(
        "move",
        help="move a ./.learning record out of the project, into the home record",
    ).set_defaults(func=cmd_move)
    sub.add_parser("export", help="print the record as one JSON document").set_defaults(
        func=cmd_export
    )
    p = sub.add_parser(
        "import-bundle", help="merge a document printed by `export` into the record"
    )
    p.add_argument("file", help="the exported document, or - for stdin")
    p.set_defaults(func=cmd_import_bundle)
    sub.add_parser(
        "where", help="print the record directory and which rule chose it"
    ).set_defaults(func=cmd_where)
