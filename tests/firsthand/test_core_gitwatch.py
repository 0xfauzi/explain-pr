"""firsthand.gitwatch: project root and id, HEAD, and the path and command tables."""

from __future__ import annotations

import support

from firsthand import gitwatch
from firsthand.model import FileChange, HeadState


class GitwatchRepoTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "proj"
        support.make_repo(self.repo, {"pkg/a.py": "x = 1\n", "README": "r\n"})

    def test_root_from_subfolder_and_worktree(self) -> None:
        self.assertEqual(gitwatch.project_root(self.repo / "pkg"), self.repo)
        wt = self.tmp / "wt"
        support.git(self.repo, "worktree", "add", "-q", str(wt))
        self.assertEqual(gitwatch.project_root(wt), self.repo)
        self.assertIsNone(gitwatch.project_root(self.tmp))
        self.assertIsNone(gitwatch.project_root(self.tmp / "missing"))

    def test_one_id_for_a_clone(self) -> None:
        pid = gitwatch.project_id(self.repo)
        self.assertRegex(pid, r"^prj_[0-9a-f]{12}$")
        clone = self.tmp / "clone"
        support.git(self.tmp, "clone", "-q", str(self.repo), str(clone))
        self.assertEqual(gitwatch.project_id(clone), pid)

    def test_none_with_no_commit(self) -> None:
        empty = self.tmp / "empty"
        empty.mkdir()
        support.git(empty, "init", "-q")
        self.assertIsNone(gitwatch.project_id(empty))
        self.assertEqual(gitwatch.project_root(empty), empty.resolve())
        state = gitwatch.head(empty)
        self.assertIsNone(state.commit)

    def test_head_and_dirs(self) -> None:
        state = gitwatch.head(self.repo)
        self.assertRegex(state.commit, r"^[0-9a-f]{40}$")
        self.assertEqual(state.branch, "main")
        support.git(self.repo, "checkout", "-q", "--detach")
        self.assertEqual(gitwatch.head(self.repo), HeadState(state.commit, None))
        git_dir, objects = gitwatch.git_dirs(self.repo)
        self.assertEqual(git_dir, self.repo / ".git")
        self.assertEqual(objects, self.repo / ".git" / "objects")
        with self.assertRaises(gitwatch.GitError):
            gitwatch.git_dirs(self.tmp)


class GitwatchTablesTest(support.TempHome):
    def test_is_test_path(self) -> None:
        table = {
            "test_a.py": True,
            "pkg/test_a.py": True,
            "a_test.py": True,
            "tests/helpers.py": True,
            "tests/data/x.json": True,
            "src/tests/conftest.py": True,
            "a.py": False,
            "testing/a.py": False,
            "test_a.txt": False,
            "pkg/contest.py": False,
            "tests": False,
        }
        for path, want in table.items():
            self.assertEqual(gitwatch.is_test_path(path), want, path)

    def test_glob_match(self) -> None:
        table = [
            ("db/migrations/0001.py", "**/migrations/**", True),
            ("migrations/0001.py", "**/migrations/**", True),
            ("a/b/migrations/x/y.py", "**/migrations/**", True),
            ("migrationsx/a.py", "**/migrations/**", False),
            ("refunds/service.py", "refunds/**", True),
            ("refunds/deep/a.py", "refunds/", True),
            ("x/refunds/a.py", "refunds/**", False),
            ("src/a.py", "src/*.py", True),
            ("src/b/a.py", "src/*.py", False),
            ("src/ab.py", "src/a?.py", True),
            ("src/a/b.py", "src/a?b.py", False),
        ]
        for path, pattern, want in table:
            self.assertEqual(gitwatch.glob_match(path, pattern), want, (path, pattern))
        self.assertEqual(
            gitwatch.first_match(
                ["a.py", "refunds/x.py"], ["**/auth/**", "refunds/**"]
            ),
            "refunds/**",
        )
        self.assertIsNone(gitwatch.first_match(["a.py"], ["**/auth/**"]))

    def test_split_changes(self) -> None:
        changes = [FileChange("a.py", "M"), FileChange("tests/test_a.py", "A")]
        source, tests = gitwatch.split_changes(changes)
        self.assertEqual(source, (changes[0],))
        self.assertEqual(tests, (changes[1],))

    def test_runner_token(self) -> None:
        table = {
            "pytest -q": "pytest",
            "cd api && uv run python -m pytest -q": "pytest",
            "python3 -m pytest tests/x.py": "pytest",
            "PYTHONPATH=. FOO=1 pytest": "pytest",
            "poetry run pytest": "pytest",
            "/home/x/.venv/bin/pytest -x": "pytest",
            "npm test": "npm",
            "python -m unittest": "unittest",
            "make test": "make",
            "": None,
            "'unterminated": None,
        }
        for command, want in table.items():
            self.assertEqual(gitwatch.runner_token(command), want, command)

    def test_is_test_run(self) -> None:
        self.assertTrue(gitwatch.is_test_run("uv run pytest tests/x.py", "pytest -q"))
        self.assertFalse(gitwatch.is_test_run("ls", "pytest -q"))
        self.assertFalse(gitwatch.is_test_run("pytest", None))
