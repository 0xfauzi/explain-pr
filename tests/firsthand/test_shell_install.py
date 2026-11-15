"""SHELL: engine install, the settings merge, apply and uninstall."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path

import support

from firsthand import __version__, install, paths
from firsthand.adapters import claude_code

LAUNCHER = Path("/home/sam/.firsthand/engine/0.1.0/bin/firsthand")

EXISTING = {
    "permissions": {"allow": ["Bash(ls:*)"]},
    "model": "opus",
    "hooks": {
        "PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": "audit.sh"}]}
        ],
        "Notification": [{"hooks": [{"type": "command", "command": "notify-send hi"}]}],
    },
}


def fragment() -> dict:
    return claude_code.settings_fragment(LAUNCHER)


class MergeHooksTest(support.TempHome):
    def test_into_nothing(self) -> None:
        for text in (None, "", "  \n"):
            merged = json.loads(install.merge_hooks(text, fragment()))
            self.assertEqual(merged, fragment())

    def test_keeps_unrelated_hooks_and_keys(self) -> None:
        merged = json.loads(install.merge_hooks(json.dumps(EXISTING), fragment()))
        self.assertEqual(merged["permissions"], EXISTING["permissions"])
        self.assertEqual(merged["model"], "opus")
        self.assertEqual(
            merged["hooks"]["Notification"], EXISTING["hooks"]["Notification"]
        )
        pre = merged["hooks"]["PreToolUse"]
        self.assertEqual(pre[0], EXISTING["hooks"]["PreToolUse"][0])
        self.assertEqual(pre[1], fragment()["hooks"]["PreToolUse"][0])
        self.assertEqual(set(merged["hooks"]), {*claude_code.EVENTS, "Notification"})

    def test_idempotent(self) -> None:
        once = install.merge_hooks(json.dumps(EXISTING), fragment())
        twice = install.merge_hooks(once, fragment())
        self.assertEqual(once, twice)
        self.assertTrue(once.endswith("}\n"))

    def test_replaces_an_older_launcher(self) -> None:
        old = install.merge_hooks(
            None, claude_code.settings_fragment(Path("/old/firsthand"))
        )
        merged = install.merge_hooks(old, fragment())
        self.assertNotIn("/old/firsthand", merged)
        self.assertEqual(json.loads(merged), fragment())

    def test_invalid_settings_raise(self) -> None:
        for text in ("{not json", "[1, 2]", '{"hooks": []}'):
            with self.assertRaises(install.InstallError):
                install.merge_hooks(text, fragment())


class ApplyUninstallTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.claude = self.home / ".claude"
        self.claude.mkdir()
        self.settings = self.claude / "settings.json"
        self.original = (json.dumps(EXISTING, indent=4) + "\n").encode()
        self.settings.write_bytes(self.original)

    def _apply(self, stamp: str = "20261114T091000Z") -> Path:
        return install.apply(install.plan(LAUNCHER), launcher=LAUNCHER, stamp=stamp)

    def test_plan_writes_nothing(self) -> None:
        writes = install.plan(LAUNCHER)
        self.assertEqual(
            [w.path for w in writes],
            [paths.claude_skill_file(), paths.claude_settings()],
        )
        self.assertEqual(writes[0].summary, "new folder")
        self.assertEqual(writes[1].summary, f"adds 6 hooks that call {LAUNCHER}")
        self.assertFalse(paths.claude_skill_file().exists())
        self.assertEqual(self.settings.read_bytes(), self.original)
        self.assertFalse(paths.config_home().exists())
        self.assertIn("+", install.diff_text(writes[1]))

    def test_apply_then_uninstall_restores_byte_for_byte(self) -> None:
        backup = self._apply()
        self.assertEqual((backup / "settings.json").read_bytes(), self.original)
        self.assertIn(" hook claude-code Stop", self.settings.read_text())
        self.assertEqual(
            paths.claude_skill_file().read_text(), claude_code.skill_text(LAUNCHER)
        )
        self.assertIn(
            f"run `{LAUNCHER}` in place of `firsthand`",
            claude_code.skill_text(LAUNCHER),
        )
        manifest = json.loads(paths.install_manifest().read_text())
        self.assertEqual(manifest["agent"], "claude-code")
        self.assertEqual(manifest["launcher"], str(LAUNCHER))
        self.assertEqual(manifest["backup"], str(backup))
        by_path = {f["path"]: f for f in manifest["files"]}
        self.assertTrue(by_path[str(self.settings)]["existed"])
        self.assertEqual(by_path[str(self.settings)]["backup"], "settings.json")
        self.assertFalse(by_path[str(paths.claude_skill_file())]["existed"])
        self.assertIsNone(by_path[str(paths.claude_skill_file())]["sha256_before"])

        report = install.uninstall()
        self.assertEqual(report.restored, (self.settings,))
        self.assertEqual(report.removed, (paths.claude_skill_file(),))
        self.assertEqual(report.refused, ())
        self.assertEqual(self.settings.read_bytes(), self.original)
        self.assertFalse((self.claude / "skills").exists())
        self.assertFalse(paths.install_manifest().exists())

    def test_uninstall_keeps_an_existing_skills_folder(self) -> None:
        (self.claude / "skills" / "other").mkdir(parents=True)
        self._apply()
        install.uninstall()
        self.assertTrue((self.claude / "skills" / "other").is_dir())
        self.assertFalse((self.claude / "skills" / "firsthand").exists())

    def test_changed_file_is_refused_with_a_diff(self) -> None:
        self._apply()
        edited = self.settings.read_text().replace('"opus"', '"sonnet"')
        self.settings.write_text(edited)
        report = install.uninstall()
        self.assertEqual([p for p, _ in report.refused], [self.settings])
        diff = report.refused[0][1]
        self.assertIn('-  "model": "opus"', diff)
        self.assertIn('+  "model": "sonnet"', diff)
        self.assertEqual(self.settings.read_text(), edited)
        # All or nothing: the skill file stays with the hooks that print through it.
        self.assertEqual((report.restored, report.removed), ((), ()))
        self.assertTrue(paths.claude_skill_file().exists())
        self.assertTrue(paths.install_manifest().exists())

    def test_symlinked_settings_stay_a_symlink(self) -> None:
        dotfiles = self.tmp / "dotfiles"
        dotfiles.mkdir()
        target = dotfiles / "claude-settings.json"
        target.write_bytes(self.original)
        self.settings.unlink()
        self.settings.symlink_to(target)
        self._apply()
        self.assertTrue(self.settings.is_symlink())
        self.assertIn(" hook claude-code Stop", target.read_text())
        report = install.uninstall()
        self.assertEqual(report.restored, (self.settings,))
        self.assertTrue(self.settings.is_symlink())
        self.assertEqual(os.readlink(self.settings), str(target))
        self.assertEqual(target.read_bytes(), self.original)

    def test_command_names_the_launcher_when_not_on_path(self) -> None:
        old_path = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", old_path)
        empty = self.tmp / "nobin"
        empty.mkdir()
        os.environ["PATH"] = str(empty)
        self.assertEqual(
            install.command(), f"~/.firsthand/engine/{__version__}/bin/firsthand"
        )
        on_path = self.tmp / "bin"
        on_path.mkdir()
        (on_path / "firsthand").write_text("#!/bin/sh\n")
        os.chmod(on_path / "firsthand", 0o755)
        os.environ["PATH"] = str(on_path)
        self.assertEqual(install.command(), "firsthand")

    def test_backups_are_private(self) -> None:
        backup = self._apply()
        for path in [backup, *backup.rglob("*")]:
            mode = path.stat().st_mode & 0o777
            self.assertEqual(mode, 0o700 if path.is_dir() else 0o600, path)

    def test_second_apply_keeps_the_first_backup(self) -> None:
        self._apply("20261114T091000Z")
        second = self._apply("20261115T080000Z")
        self.assertEqual((second / "settings.json").read_bytes(), self.original)
        manifest = json.loads(paths.install_manifest().read_text())
        entry = next(f for f in manifest["files"] if f["path"] == str(self.settings))
        self.assertEqual(entry["sha256_before"], install._sha(self.original))
        install.uninstall()
        self.assertEqual(self.settings.read_bytes(), self.original)
        self.assertFalse(paths.claude_skill_file().exists())

    def test_uninstall_without_install(self) -> None:
        with self.assertRaises(install.InstallError):
            install.uninstall()

    def test_writes_stay_inside_the_three_homes(self) -> None:
        self._apply()
        homes = (paths.claude_dir(), paths.config_home(), paths.home())
        for path in self.tmp.rglob("*"):
            if path.is_file():
                self.assertTrue(any(path.is_relative_to(h) for h in homes), path)


class InstallEngineTest(support.TempHome):
    def test_launcher_runs_a_hook(self) -> None:
        launcher = install.install_engine("0.1.0")
        self.assertEqual(launcher, paths.engine_dir("0.1.0") / "bin" / "firsthand")
        self.assertTrue(os.access(launcher, os.X_OK))
        self.assertTrue(launcher.read_text().startswith("#!/"))
        lib = paths.engine_dir("0.1.0") / "lib" / "firsthand"
        self.assertTrue((lib / "cli.py").is_file())
        self.assertTrue((lib / "adapters" / "claude_code_skill.md").is_file())
        self.assertFalse(list(lib.rglob("__pycache__")))
        self.assertEqual(install.install_engine("0.1.0"), launcher)  # idempotent
        done = subprocess.run(
            [str(launcher), "hook", "claude-code", "Stop"],
            input=b"",
            capture_output=True,
            env=support.child_env(),
            cwd=self.tmp,
            timeout=30,
            check=False,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout, b"")
        self.assertEqual(done.stderr, b"")


if __name__ == "__main__":
    unittest.main()
