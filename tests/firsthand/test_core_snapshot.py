"""firsthand.runner.snapshot: what a snapshot holds, and that the project is never written."""

from __future__ import annotations

import os
import time

import support

from firsthand import gitwatch
from firsthand.model import FileChange
from firsthand.runner.snapshot import SnapshotError, SnapshotStore


class SnapshotTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "proj"
        support.make_repo(
            self.repo,
            {
                ".gitignore": "*.log\nbuild/\n",
                "kept.py": "kept\n",
                "mod.py": "old\n",
                "gone.py": "bye\n",
                "staged.py": "s0\n",
            },
        )
        support.write_files(
            self.repo,
            {
                "mod.py": "new\n",
                "gone.py": None,
                "untracked.py": "u\n",
                "debug.log": "ignored\n",
                "build/out.txt": "ignored\n",
                "bin.dat": None,
            },
        )
        (self.repo / "bin.dat").write_bytes(b"\x00\x01\x02")
        support.write_files(self.repo, {"staged.py": "s1\n"})
        support.git(self.repo, "add", "staged.py")
        self.store = SnapshotStore(self.repo, gitwatch.project_id(self.repo))

    def test_contents(self) -> None:
        tree = self.store.take()
        self.assertTrue(self.store.has(tree))
        self.assertEqual(self.store.read_file(tree, "kept.py"), "kept\n")
        self.assertEqual(self.store.read_file(tree, "mod.py"), "new\n")
        self.assertEqual(self.store.read_file(tree, "staged.py"), "s1\n")
        self.assertEqual(self.store.read_file(tree, "untracked.py"), "u\n")
        self.assertIsNone(self.store.read_file(tree, "gone.py"))
        self.assertIsNone(self.store.read_file(tree, "debug.log"))
        self.assertIsNone(self.store.read_file(tree, "build/out.txt"))
        self.assertIsNone(self.store.read_file(tree, "bin.dat"))  # binary
        self.assertEqual(self.store.read_bytes(tree, "bin.dat"), b"\x00\x01\x02")
        self.assertIsNone(self.store.read_file(tree, "nowhere/x.py"))

    def test_diff_statuses(self) -> None:
        base = self.store.head_tree()
        head = self.store.take()
        self.assertEqual(
            self.store.diff(base, head),
            (
                FileChange("bin.dat", "A"),
                FileChange("gone.py", "D"),
                FileChange("mod.py", "M"),
                FileChange("staged.py", "M"),
                FileChange("untracked.py", "A"),
            ),
        )
        self.assertEqual(self.store.diff(head, head), ())

    def test_project_untouched(self) -> None:
        before = support.repo_fingerprint(self.repo)
        tree = self.store.take()
        base = self.store.head_tree()
        self.store.diff(base, tree)
        self.store.read_file(tree, "mod.py")
        dest = self.tmp / "co"
        self.store.checkout(tree, dest)
        self.store.take()
        self.assertEqual(support.repo_fingerprint(self.repo), before)
        self.assertEqual((dest / "untracked.py").read_text(), "u\n")
        self.assertFalse((dest / "debug.log").exists())
        self.assertFalse((dest / ".git").exists())

    def test_checkout_needs_empty_dest(self) -> None:
        tree = self.store.take()
        dest = self.tmp / "busy"
        dest.mkdir()
        (dest / "x").write_text("x")
        with self.assertRaises(SnapshotError):
            self.store.checkout(tree, dest)

    def test_has_and_bad_tree(self) -> None:
        self.assertFalse(self.store.has("0" * 40))
        with self.assertRaises(SnapshotError):
            self.store.diff("0" * 40, "1" * 40)

    def test_no_commit(self) -> None:
        empty = self.tmp / "empty"
        empty.mkdir()
        support.git(empty, "init", "-q")
        (empty / "a.py").write_text("a\n")
        store = SnapshotStore(empty, "prj_empty")
        self.assertIsNone(store.head_tree())
        tree = store.take()
        self.assertEqual(store.read_file(tree, "a.py"), "a\n")

    def test_project_filters_never_run(self) -> None:
        # A clean filter (as Git LFS sets up) would run a project-configured command
        # and could write under .git (for LFS, .git/lfs/objects).
        log = self.tmp / "filter.log"
        support.git(
            self.repo, "config", "filter.demo.clean", f"sh -c 'echo ran >> {log}; cat'"
        )
        support.git(
            self.repo, "config", "filter.demo.smudge", f"sh -c 'echo ran >> {log}; cat'"
        )
        support.git(self.repo, "config", "filter.demo.required", "true")
        support.write_files(self.repo, {".gitattributes": "*.txt filter=demo\n"})
        support.write_files(self.repo, {"notes.txt": "hello\n"})
        store = SnapshotStore(self.repo, gitwatch.project_id(self.repo))
        before = support.repo_fingerprint(self.repo)
        tree = store.take()
        store.checkout(tree, self.tmp / "co")
        self.assertFalse(log.exists())
        self.assertEqual(support.repo_fingerprint(self.repo), before)
        self.assertEqual(store.read_file(tree, "notes.txt"), "hello\n")
        self.assertEqual((self.tmp / "co" / "notes.txt").read_text(), "hello\n")

    def test_project_objects_not_touched(self) -> None:
        # With the project's objects as an alternate, git add "freshens" a blob it
        # finds there: no bytes change, but the mtime does.
        objects = self.repo / ".git" / "objects"
        old = time.time() - 3600
        for p in objects.rglob("*"):
            if p.is_file():
                os.utime(p, (old, old))
        support.write_files(self.repo, {"copy.py": "kept\n"})  # same blob as kept.py
        before = {
            str(p): p.stat().st_mtime_ns for p in objects.rglob("*") if p.is_file()
        }
        tree = self.store.take()
        after = {
            str(p): p.stat().st_mtime_ns for p in objects.rglob("*") if p.is_file()
        }
        self.assertEqual(after, before)
        self.assertEqual(self.store.read_file(tree, "copy.py"), "kept\n")
        self.assertEqual(self.store.read_file(tree, "kept.py"), "kept\n")
