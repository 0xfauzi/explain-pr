"""firsthand.runner.scratch: the scratch copy, the scrubbed environment and timed runs."""

from __future__ import annotations

import os
import stat
import sys
import threading
import time
from pathlib import Path

import support

from firsthand import gitwatch, paths
from firsthand.model import FileChange
from firsthand.runner import scratch as scratch_mod
from firsthand.runner.scratch import (
    STRIPPED,
    Scratch,
    find_python,
    scrubbed_env,
    source_wins,
)
from firsthand.runner.snapshot import SnapshotStore

SECRETS = ("GH_TOKEN", "ANTHROPIC_API_KEY", "AWS_SECRET_ACCESS_KEY", "SSH_AUTH_SOCK")


class ScratchTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "proj"
        files = {
            "app.py": "def f():\n    return 1\n",
            "old.py": "x = 1\n",
            "tests/test_app.py": "from app import f\n",
        }
        for name in STRIPPED:
            files[f"{name}/inner" if not name.endswith((".md", ".json")) else name] = (
                "agent\n"
            )
        support.make_repo(self.repo, files)
        self.base = SnapshotStore(self.repo, gitwatch.project_id(self.repo)).head_tree()
        support.write_files(
            self.repo,
            {"app.py": "def f():\n    return 2\n", "new.py": "n\n", "old.py": None},
        )
        self.store = SnapshotStore(self.repo, gitwatch.project_id(self.repo))
        self.head = self.store.take()
        self.s = Scratch(self.store, self.head, "01CHECK")
        self.addCleanup(self.s.close)

    def test_layout_and_stripped(self) -> None:
        self.assertEqual(self.s.root, paths.scratch_dir("01CHECK"))
        self.assertEqual(stat.S_IMODE(self.s.root.stat().st_mode), 0o700)
        for sub in ("tree", "home", "tmp", "out"):
            self.assertTrue((self.s.root / sub).is_dir(), sub)
        for name in STRIPPED:
            self.assertFalse((self.s.tree / name).exists(), name)
        self.assertEqual(
            (self.s.tree / "app.py").read_text(), "def f():\n    return 2\n"
        )

    def test_undo_restores_and_deletes(self) -> None:
        changes = self.store.diff(self.base, self.head)
        source = [c for c in changes if not gitwatch.is_test_path(c.path)]
        self.assertEqual(
            source,
            [
                FileChange("app.py", "M"),
                FileChange("new.py", "A"),
                FileChange("old.py", "D"),
            ],
        )
        touched = self.s.undo(self.base, source)
        self.assertEqual(touched, ("app.py", "new.py", "old.py"))
        self.assertEqual(
            (self.s.tree / "app.py").read_text(), "def f():\n    return 1\n"
        )
        self.assertFalse((self.s.tree / "new.py").exists())
        self.assertEqual((self.s.tree / "old.py").read_text(), "x = 1\n")

    def test_env_is_scrubbed(self) -> None:
        for name in SECRETS:
            os.environ[name] = "secret-value"
        os.environ["LANG"] = "C.UTF-8"
        env = scrubbed_env(self.s, python=None, extra=[("DATABASE_URL", "sqlite://")])
        for name in SECRETS:
            self.assertNotIn(name, env)
        self.assertNotIn("secret-value", "".join(env.values()))
        self.assertEqual(env["HOME"], str(self.s.root / "home"))
        self.assertEqual(env["TMPDIR"], str(self.s.root / "tmp"))
        self.assertEqual(env["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(env["PYTHONPATH"], str(self.s.tree))
        self.assertEqual(env["LANG"], "C.UTF-8")
        self.assertEqual(env["DATABASE_URL"], "sqlite://")
        allowed = set(scratch_mod.ENV_ALLOW) | {
            "HOME",
            "TMPDIR",
            "PYTHONDONTWRITEBYTECODE",
            "PYTHONPATH",
            "DATABASE_URL",
        }
        self.assertLessEqual(set(env), allowed)
        (self.s.tree / "src").mkdir()
        env = scrubbed_env(self.s, python=None)
        self.assertEqual(
            env["PYTHONPATH"], f"{self.s.tree / 'src'}{os.pathsep}{self.s.tree}"
        )

    def test_virtualenv_named(self) -> None:
        venv = self.tmp / "venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "pyvenv.cfg").write_text("home = /usr\n")
        env = scrubbed_env(self.s, python=venv / "bin" / "python")
        self.assertEqual(env["VIRTUAL_ENV"], str(venv))
        self.assertNotIn(
            "VIRTUAL_ENV", scrubbed_env(self.s, python=Path(sys.executable))
        )

    def test_run_exit_and_output_hash(self) -> None:
        env = scrubbed_env(self.s, python=None)
        ok = self.s.run([sys.executable, "-c", "print('hi')"], env=env, timeout_s=30)
        self.assertEqual(ok.exit, 0)
        self.assertFalse(ok.timed_out)
        self.assertRegex(ok.output_sha256, r"^[0-9a-f]{64}$")
        bad = self.s.run(
            [sys.executable, "-c", "import sys; sys.exit(3)"], env=env, timeout_s=30
        )
        self.assertEqual(bad.exit, 3)
        missing = self.s.run([str(self.tmp / "no-such-binary")], env=env, timeout_s=5)
        self.assertIsNotNone(missing.exit)
        self.assertNotEqual(missing.exit, 0)
        cwd = self.s.run(
            [sys.executable, "-c", "import os; assert os.path.exists('app.py')"],
            env=env,
            timeout_s=30,
        )
        self.assertEqual(cwd.exit, 0)

    def test_time_limit_kills_children(self) -> None:
        env = scrubbed_env(self.s, python=None)
        marker = self.s.root / "child.pid"
        code = (
            "import subprocess, sys, time\n"
            f"p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
            f"open({str(marker)!r}, 'w').write(str(p.pid))\n"
            "time.sleep(60)\n"
        )
        start = time.monotonic()
        res = self.s.run([sys.executable, "-c", code], env=env, timeout_s=1.5)
        self.assertLess(time.monotonic() - start, 10)
        self.assertTrue(res.timed_out)
        self.assertIsNone(res.exit)
        child = int(marker.read_text())
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and _alive(child):
            time.sleep(0.05)
        self.assertFalse(_alive(child), "the child process outlived the time limit")

    def test_cancel(self) -> None:
        env = scrubbed_env(self.s, python=None)
        cancel = threading.Event()
        threading.Timer(0.3, cancel.set).start()
        res = self.s.run(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            env=env,
            timeout_s=60,
            cancel=cancel,
        )
        self.assertIsNone(res.exit)
        self.assertFalse(res.timed_out)

    def test_close_and_sweep(self) -> None:
        self.s.close()
        self.assertFalse(self.s.root.exists())
        self.s.close()
        Scratch(self.store, self.head, "01A")
        Scratch(self.store, self.head, "01B")
        self.assertEqual(scratch_mod.sweep(), 2)
        self.assertEqual(list(paths.scratch_root().iterdir()), [])
        self.assertEqual(scratch_mod.sweep(), 0)

    def test_close_removes_read_only_folders(self) -> None:
        # A test may leave a folder it made read-only. As root rmtree copes anyway;
        # as any other user it would leave the folder behind.
        ro = self.s.tree / "tests" / "fixtures" / "ro"
        ro.mkdir(parents=True)
        (ro / "data.txt").write_text("x")
        os.chmod(ro, 0o500)
        os.chmod(ro.parent, 0o500)
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("keep")
        os.chmod(outside, 0o500)
        (self.s.tree / "link").symlink_to(outside)
        self.s.close()
        self.assertFalse(self.s.root.exists())
        self.assertEqual(stat.S_IMODE(outside.stat().st_mode), 0o500)
        self.assertTrue((outside / "keep.txt").exists())
        os.chmod(outside, 0o700)

    def test_find_python(self) -> None:
        hint = self.tmp / "hintvenv"
        (hint / "bin").mkdir(parents=True)
        py = hint / "bin" / "python"
        py.write_text("#!/bin/sh\n")
        py.chmod(0o755)
        self.assertEqual(find_python(self.repo, str(hint)), py)
        dot = self.repo / ".venv" / "bin"
        dot.mkdir(parents=True)
        (dot / "python").write_text("#!/bin/sh\n")
        (dot / "python").chmod(0o755)
        self.assertEqual(find_python(self.repo, None), dot / "python")
        self.assertEqual(find_python(self.repo, str(self.tmp / "nope")), dot / "python")
        other = self.tmp / "other"
        other.mkdir()
        found = find_python(other, None)
        self.assertTrue(found is None or found.name.startswith("python3"))

    def test_source_wins(self) -> None:
        env = scrubbed_env(self.s, python=Path(sys.executable))
        changes = [FileChange("app.py", "M")]
        self.assertTrue(
            source_wins(Path(sys.executable), self.s, env, changes, self.repo)
        )
        # An editable install adds a finder to sys.meta_path that maps the module to the
        # project's own file, ahead of every path entry. A sitecustomize does the same here.
        hook = self.tmp / "hook"
        hook.mkdir()
        (hook / "sitecustomize.py").write_text(
            "import importlib.util, sys\n"
            "class F:\n"
            "    @staticmethod\n"
            "    def find_spec(name, path=None, target=None):\n"
            "        if name == 'app':\n"
            f"            return importlib.util.spec_from_file_location('app', {str(self.repo / 'app.py')!r})\n"
            "sys.meta_path.insert(0, F)\n"
        )
        env_bad = dict(env, PYTHONPATH=f"{env['PYTHONPATH']}{os.pathsep}{hook}")
        self.assertFalse(
            source_wins(Path(sys.executable), self.s, env_bad, changes, self.repo)
        )
        self.assertTrue(
            source_wins(
                Path(sys.executable),
                self.s,
                env,
                [FileChange("x-y.py", "A")],
                self.repo,
            )
        )


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().split()[2] != "Z"
    except OSError:
        return True
