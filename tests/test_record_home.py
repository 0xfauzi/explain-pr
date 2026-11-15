"""Behaviour tests for where the record lives: the home repo, `move`, and bundles.

Every test runs the real script with a temporary HOME and LEARNING_HOME and a
temporary git repo as the project, so nothing reads or writes the real home
folder. Nothing is mocked.

Run with:  python3 -m unittest discover -s tests
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARNING = ROOT / "skills" / "learning-while-building" / "scripts" / "learning.py"
LEGACY_NOTICE = 'This record is inside your project. Run "learning.py move"'


@unittest.skipIf(shutil.which("git") is None, "git not installed")
class HomeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.home = self.tmp / "learning-home"
        self.env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("LEARNING_DIR", "CLAUDE_CODE_REMOTE")
            and not k.startswith("GIT_")
        }
        self.env.update(
            HOME=str(self.tmp / "user"),
            LEARNING_HOME=str(self.home),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="t",
            GIT_AUTHOR_EMAIL="t@t",
            GIT_COMMITTER_NAME="t",
            GIT_COMMITTER_EMAIL="t@t",
        )
        (self.tmp / "user").mkdir()
        self.project = self.repo(self.tmp / "work" / "orbit-pay")

    def git(self, cwd: Path, *args: str) -> str:
        done = subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )
        return done.stdout.strip()

    def repo(self, path: Path) -> Path:
        path.mkdir(parents=True)
        self.git(path, "init", "-q", "-b", "main")
        (path / "app.py").write_text(f"# {path}\n")
        self.git(path, "add", "-A")
        self.git(path, "commit", "-qm", "root")
        return path

    def run_cli(
        self,
        *args: str,
        cwd: Path | None = None,
        ok: bool = True,
        stdin: str = "",
        **env: str,
    ) -> str:
        done = subprocess.run(
            [sys.executable, str(LEARNING), *args],
            cwd=cwd or self.project,
            env={**self.env, **env},
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )
        if ok != (done.returncode == 0):
            raise AssertionError(
                f"{args} exit {done.returncode}: {done.stdout}{done.stderr}"
            )
        return done.stdout + done.stderr

    def key(self, cwd: Path) -> str:
        return Path(self.run_cli("where", cwd=cwd).splitlines()[0]).name

    def record_dir(self) -> Path:
        return self.home / "projects" / self.key(self.project)

    def add_and_ask(self, *flags: str) -> str:
        self.run_cli(
            *flags, "topic", "add", "--id", "t", "--dimension", "data", "--concept", "c"
        )
        out = self.run_cli(
            *flags,
            "ask",
            "--topic",
            "t",
            "--kind",
            "retrieval",
            "--question",
            "q",
            "--rubric",
            "r",
        )
        return out.split()[1]

    def legacy_record(self, commit: bool) -> None:
        self.run_cli("--dir", ".learning", "init", "--dimensions", "data")
        self.add_and_ask("--dir", ".learning")
        if commit:
            self.git(self.project, "add", "-A")
            self.git(self.project, "commit", "-qm", "record")

    # 1
    def test_init_writes_only_to_the_home(self) -> None:
        out = self.run_cli("init", "--dimensions", "data")
        self.assertTrue((self.record_dir() / "dimensions.json").exists())
        self.assertEqual(self.git(self.project, "status", "--porcelain"), "")
        self.assertEqual(
            sorted(p.name for p in self.project.iterdir()), [".git", "app.py"]
        )
        self.assertNotRegex(out.lower(), r"commit[^.]*this directory")
        self.assertIn("It is outside your project.", out)
        self.assertEqual(
            (self.home / "FORMAT").read_text().strip(), "learning-record 2"
        )
        self.assertEqual(self.home.stat().st_mode & 0o777, 0o700)

    def test_cloud_session_init_says_to_export(self) -> None:
        out = self.run_cli("init", CLAUDE_CODE_REMOTE="true")
        self.assertIn('run "learning.py export" and keep the output', out)

    # 2
    def test_clones_share_a_key_and_unrelated_repos_do_not(self) -> None:
        clone = self.tmp / "elsewhere" / "orbit-pay"
        clone.parent.mkdir()
        self.git(clone.parent, "clone", "-q", str(self.project), str(clone))
        self.assertEqual(self.key(self.project), self.key(clone))
        other = self.repo(self.tmp / "other" / "orbit-pay")
        self.assertNotEqual(self.key(self.project), self.key(other))
        self.assertRegex(self.key(self.project), r"^orbit-pay-[0-9a-f]{8}$")

    def test_record_started_before_the_first_commit_is_still_found(self) -> None:
        fresh = self.tmp / "work" / "my proj"
        fresh.mkdir(parents=True)
        self.git(fresh, "init", "-q", "-b", "main")
        self.run_cli("init", "--dimensions", "data", cwd=fresh)
        before = self.run_cli("where", cwd=fresh).splitlines()[0]
        (fresh / "a.py").write_text("a\n")
        self.git(fresh, "add", "-A")
        self.git(fresh, "commit", "-qm", "first")
        after = self.run_cli("where", cwd=fresh)
        self.assertEqual(after.splitlines()[0], before)
        self.assertNotIn("No record there yet", after)
        self.assertEqual(len(list((self.home / "projects").iterdir())), 1)

    def test_worktree_shares_the_key(self) -> None:
        tree = self.tmp / "orbit-pay-feature"
        self.git(self.project, "worktree", "add", "-q", str(tree))
        self.assertEqual(self.key(self.project), self.key(tree))

    # 3
    def test_each_write_is_one_home_commit_and_the_project_stays_clean(self) -> None:
        self.run_cli("init", "--dimensions", "data")
        attempt = self.add_and_ask()
        self.run_cli(
            "grade",
            "--attempt",
            attempt,
            "--outcome",
            "correct",
            "--hint",
            "0",
            "--confidence",
            "low",
            "--answer",
            "a",
        )
        log = self.git(self.home, "log", "--format=%s").splitlines()
        self.assertEqual(
            log,
            [
                f"grade {attempt}",
                f"ask {attempt}",
                "topic add t",
                f"init {self.key(self.project)}",
            ],
        )
        self.assertEqual(self.git(self.project, "status", "--porcelain"), "")

    # 4
    def test_existing_project_record_is_read_with_a_notice(self) -> None:
        self.legacy_record(commit=False)
        out = self.run_cli(
            "topic", "add", "--id", "u", "--dimension", "data", "--concept", "c"
        )
        self.assertTrue(out.strip().endswith(LEGACY_NOTICE + " to move it out."))
        self.assertTrue((self.project / ".learning" / "topics" / "u.json").exists())
        self.assertIn("2 topic(s)", self.run_cli("check"))
        self.assertFalse(self.home.exists())

    # 5
    def test_move_of_a_committed_record_explains_history(self) -> None:
        self.legacy_record(commit=True)
        self.git(
            self.project, "remote", "add", "origin", "https://example.invalid/r.git"
        )
        before = (
            self.git(self.project, "rev-parse", "HEAD"),
            self.git(self.project, "status", "--porcelain"),
        )
        out = self.run_cli("move")
        self.assertIn("Moved 1 topic and 1 attempt to", out)
        self.assertIn("git rm -r --cached .learning", out)
        self.assertIn(
            ".learning/ was committed 1 time and this repo has a remote (origin),", out
        )
        self.assertIn("It does not remove it from history.", out)
        after = (
            self.git(self.project, "rev-parse", "HEAD"),
            self.git(self.project, "status", "--porcelain"),
        )
        self.assertEqual(before, after)
        self.assertTrue((self.project / ".learning" / "dimensions.json").exists())
        self.assertEqual(len(list((self.record_dir() / "attempts").glob("*.json"))), 1)
        self.assertIn(self.record_dir().name, self.git(self.home, "log", "--format=%s"))
        self.assertNotIn(
            LEGACY_NOTICE,
            self.run_cli(
                "topic", "add", "--id", "u", "--dimension", "data", "--concept", "c"
            ),
        )
        self.assertTrue((self.record_dir() / "topics" / "u.json").exists())

    def test_move_of_a_record_never_committed(self) -> None:
        self.legacy_record(commit=False)
        out = self.run_cli("move")
        self.assertIn("It was never committed, so no copy exists in git.", out)
        self.assertIn("  rm -rf .learning", out)
        self.assertNotIn("git rm", out)
        self.assertNotIn("committed 1 time", out)
        self.assertTrue((self.project / ".learning" / "dimensions.json").exists())

    # 6
    def test_move_refuses_when_the_home_already_holds_a_record(self) -> None:
        self.run_cli("init", "--dimensions", "data")
        self.legacy_record(commit=False)
        out = self.run_cli("move", ok=False)
        self.assertIn("A record for this project already exists at", out)
        self.assertIn("Nothing was changed.", out)
        self.assertFalse((self.record_dir() / "topics" / "t.json").exists())

    # 7
    def test_export_then_import_reproduces_the_record(self) -> None:
        self.run_cli("init", "--dimensions", "data,design")
        attempt = self.add_and_ask()
        self.run_cli(
            "grade",
            "--attempt",
            attempt,
            "--outcome",
            "partial",
            "--hint",
            "1",
            "--confidence",
            "low",
            "--answer",
            "a",
        )
        bundle = self.run_cli("export")
        self.assertEqual(json.loads(bundle)["format"], "learning-bundle 1")
        source = self.record_dir()
        fresh = {"LEARNING_HOME": str(self.tmp / "home-2")}
        out = self.run_cli("import-bundle", "-", stdin=bundle, **fresh)
        self.assertIn(
            "Imported 1 topic and 1 attempt. Skipped 0 already recorded.", out
        )
        target = self.tmp / "home-2" / "projects" / source.name
        for rel in ("dimensions.json", "topics/t.json", f"attempts/{attempt}.json"):
            self.assertEqual(
                json.loads((source / rel).read_text()),
                json.loads((target / rel).read_text()),
                rel,
            )
        again = self.run_cli("import-bundle", "-", stdin=bundle, **fresh)
        self.assertIn(
            "Imported 0 topics and 0 attempts. Skipped 2 already recorded.", again
        )
        self.assertEqual(len(list((target / "attempts").glob("*.json"))), 1)

    def test_bundle_with_a_wrong_format_is_refused_whole(self) -> None:
        self.run_cli("init", "--dimensions", "data")
        self.add_and_ask()
        bundle = json.loads(self.run_cli("export"))
        fresh = {"LEARNING_HOME": str(self.tmp / "home-2")}
        wrong = dict(bundle, format="learning-bundle 2")
        self.assertIn(
            "Nothing was imported",
            self.run_cli(
                "import-bundle", "-", stdin=json.dumps(wrong), ok=False, **fresh
            ),
        )
        bad_field = json.loads(json.dumps(bundle))
        next(iter(bad_field["attempts"].values()))["kind"] = "guess"
        self.assertIn(
            "refused",
            self.run_cli(
                "import-bundle", "-", stdin=json.dumps(bad_field), ok=False, **fresh
            ),
        )
        self.assertFalse((self.tmp / "home-2").exists())

    def test_where_names_the_rule(self) -> None:
        self.assertIn("Chosen by: the default", self.run_cli("where"))
        self.assertIn("Chosen by: --dir", self.run_cli("--dir", "x", "where"))
        self.assertIn(
            "Chosen by: $LEARNING_DIR", self.run_cli("where", LEARNING_DIR="y")
        )


if __name__ == "__main__":
    unittest.main()
