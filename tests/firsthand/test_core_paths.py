"""firsthand.paths: overrides, id guards, the socket fallback, private writes."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import support

from firsthand import paths


class PathsTest(support.TempHome):
    def test_defaults_follow_home(self) -> None:
        os.environ.pop("FIRSTHAND_HOME")
        self.assertEqual(paths.user_home(), self.home)
        self.assertEqual(paths.home(), self.home / ".firsthand")
        self.assertEqual(paths.config_home(), self.home / ".config" / "firsthand")
        self.assertEqual(paths.claude_dir(), self.home / ".claude")

    def test_firsthand_home_moves_config_home(self) -> None:
        self.assertEqual(paths.home(), self.fh)
        self.assertEqual(paths.config_home(), self.fh / "dotconfig")
        self.assertEqual(paths.record_dir(), self.fh / "record")
        self.assertEqual(paths.spool_file(), self.fh / "run" / "spool.jsonl")
        self.assertEqual(
            paths.snapshot_store("prj_1"), self.fh / "cache" / "snapshots" / "prj_1.git"
        )

    def test_each_override(self) -> None:
        os.environ["FIRSTHAND_CONFIG_HOME"] = str(self.tmp / "cfg")
        os.environ["FIRSTHAND_CLAUDE_DIR"] = str(self.tmp / "cl")
        self.assertEqual(paths.config_home(), self.tmp / "cfg")
        self.assertEqual(paths.port_file(), self.tmp / "cfg" / "port")
        self.assertEqual(paths.claude_settings(), self.tmp / "cl" / "settings.json")
        self.assertEqual(
            paths.claude_skill_file(),
            self.tmp / "cl" / "skills" / "firsthand" / "SKILL.md",
        )

    def test_unread_variables(self) -> None:
        os.environ.pop("FIRSTHAND_HOME")
        os.environ["XDG_CONFIG_HOME"] = str(self.tmp / "xdg")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.tmp / "ccd")
        self.assertEqual(paths.config_home(), self.home / ".config" / "firsthand")
        self.assertEqual(paths.claude_dir(), self.home / ".claude")

    def test_no_function_creates_a_folder(self) -> None:
        for name in dir(paths):
            fn = getattr(paths, name)
            if (
                not callable(fn)
                or name.startswith("_")
                or name in ("ensure_private_dirs", "write_private", "Path")
            ):
                continue
            if getattr(fn, "__module__", None) != "firsthand.paths":
                continue
            try:
                fn("abc") if fn.__code__.co_argcount else fn()
            except TypeError:
                continue
        self.assertFalse(self.fh.exists())

    def test_id_validation(self) -> None:
        for bad in ("", ".hidden", "../x", "a/b", "x" * 65, "a b"):
            for fn in (
                paths.reply_file,
                paths.key_file,
                paths.scratch_dir,
                paths.snapshot_store,
                paths.engine_dir,
            ):
                with self.assertRaises(ValueError, msg=f"{fn.__name__}({bad!r})"):
                    fn(bad)
        self.assertEqual(paths.key_file("01ABC").name, "01ABC.json")
        self.assertEqual(paths.engine_dir("0.1.0").name, "0.1.0")

    def test_socket_fallback_for_long_path(self) -> None:
        self.assertEqual(paths.control_socket(), self.fh / "run" / "daemon.sock")
        long_home = self.tmp / ("x" * 100)
        os.environ["FIRSTHAND_HOME"] = str(long_home)
        sock = paths.control_socket()
        self.assertLessEqual(len(str(sock)), 96)
        self.assertTrue(sock.parent.name.startswith(f"fh-{os.getuid()}-"))
        self.assertEqual(sock.name, "d.sock")
        self.assertEqual(sock, paths.control_socket())

    def test_ensure_private_dirs(self) -> None:
        paths.ensure_private_dirs()
        for d in (
            paths.home(),
            paths.run_dir(),
            paths.out_dir(),
            paths.keys_dir(),
            paths.scratch_root(),
            paths.index_dir(),
            paths.cache_dir(),
            paths.config_home(),
        ):
            self.assertTrue(d.is_dir(), d)
            self.assertEqual(stat.S_IMODE(d.stat().st_mode), 0o700, d)

    def test_write_private(self) -> None:
        target = self.tmp / "f.json"
        paths.write_private(target, b"one")
        self.assertEqual(target.read_bytes(), b"one")
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
        inode = target.stat().st_ino
        paths.write_private(target, b"two")
        self.assertEqual(target.read_bytes(), b"two")
        self.assertNotEqual(
            target.stat().st_ino, inode
        )  # replaced, not rewritten in place
        self.assertFalse(Path(str(target) + ".tmp").exists())
