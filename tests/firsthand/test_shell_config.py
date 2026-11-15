"""SHELL: settings files and ConfigStore."""

from __future__ import annotations

import json
import unittest

import support

from firsthand import config, paths
from firsthand.model import DEFAULT_HIGH_STAKES, EngineError, Settings

PID = "prj_3b9f52c1a7e0"


class ConfigStoreTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.record = self.fh / "record"
        self.record.mkdir(parents=True)
        self.commits: list[str] = []
        self.store = config.ConfigStore(self.record, commit=self.commits.append)

    def test_defaults_with_no_files(self) -> None:
        self.assertEqual(self.store.load(), Settings())
        self.assertIsNone(self.store.project(PID))
        self.assertEqual(self.commits, [])

    def test_set_writes_one_file_per_key_and_commits(self) -> None:
        settings = self.store.set("daily_limit", 2)
        self.assertEqual(settings.daily_limit, 2)
        data = json.loads((self.record / "config" / "daily_limit.json").read_text())
        self.assertEqual(set(data), {"key", "value", "at"})
        self.assertEqual((data["key"], data["value"]), ("daily_limit", 2))
        self.assertRegex(data["at"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(self.commits, ["config: daily_limit"])
        self.assertEqual(config.ConfigStore(self.record).load().daily_limit, 2)

    def test_each_key_validates(self) -> None:
        good = {
            "dial": ["off", "notes", "standard", "deep"],
            "dial_before_off": ["notes"],
            "daily_limit": [1, 3],
            "findings_to_agent": [False],
            "work_computer": [True],
            "quiet_today": ["2026-11-14", None],
            "check_time_limit_s": [30, 600],
        }
        bad = {
            "dial": ["loud", None],
            "dial_before_off": [3],
            "daily_limit": [0, 4, True, "1"],
            "findings_to_agent": [1, "yes"],
            "work_computer": [None],
            "quiet_today": ["14 Nov", "2026-13-01", 5],
            "check_time_limit_s": [29, 601, 120.5],
            "colour": ["red"],
        }
        for key, values in good.items():
            for value in values:
                self.assertEqual(getattr(self.store.set(key, value), key), value)
        for key, values in bad.items():
            for value in values:
                with self.assertRaises(EngineError) as caught:
                    self.store.set(key, value)
                self.assertEqual(caught.exception.code, "invalid", (key, value))
        message = self._error("daily_limit", 9)
        self.assertIn("1, 2 or 3", message)
        self.assertIn("off, notes, standard, deep", self._error("dial", "x"))

    def _error(self, key: str, value: object) -> str:
        with self.assertRaises(EngineError) as caught:
            self.store.set(key, value)
        return caught.exception.message

    def test_a_broken_file_reads_as_the_default(self) -> None:
        folder = self.record / "config"
        folder.mkdir()
        (folder / "dial.json").write_text("{not json")
        (folder / "daily_limit.json").write_text(
            json.dumps({"key": "daily_limit", "value": 9})
        )
        self.assertEqual(self.store.load(), Settings())

    def test_ensure_project_defaults(self) -> None:
        root = self.tmp / "orbit-pay"
        root.mkdir()
        (root / "pyproject.toml").write_text(
            "[tool.pytest.ini_options]\naddopts = '-q'\n"
        )
        p = self.store.ensure_project(PID, str(root))
        self.assertEqual(p.name, "orbit-pay")
        self.assertEqual(p.roots, (str(root),))
        self.assertEqual(p.test_command, "pytest -q")
        self.assertEqual(p.high_stakes, DEFAULT_HIGH_STAKES)
        self.assertFalse(p.quiet)
        data = json.loads((self.record / "projects" / f"{PID}.json").read_text())
        self.assertEqual(
            data,
            {
                "format": 1,
                "id": PID,
                "name": "orbit-pay",
                "roots": [str(root)],
                "test_command": "pytest -q",
                "high_stakes": list(DEFAULT_HIGH_STAKES),
                "quiet": False,
                "runner": {"env": {}, "carry": []},
            },
        )
        self.assertEqual(self.commits, [f"project: {PID}"])

    def test_ensure_project_adds_a_root_once(self) -> None:
        self.store.ensure_project(PID, "/a/orbit-pay")
        self.store.ensure_project(PID, "/a/orbit-pay")
        p = self.store.ensure_project(PID, "/b/orbit-pay-wt")
        self.assertEqual(p.roots, ("/a/orbit-pay", "/b/orbit-pay-wt"))
        self.assertEqual(len(self.commits), 2)

    def test_set_project(self) -> None:
        self.store.ensure_project(PID, "/a/orbit-pay")
        p = self.store.set_project(PID, "test_command", "uv run pytest -q")
        self.assertEqual(p.test_command, "uv run pytest -q")
        p = self.store.set_project(PID, "high_stakes_add", "refunds/**")
        self.assertEqual(p.high_stakes[-1], "refunds/**")
        p = self.store.set_project(PID, "high_stakes_add", "refunds/**")
        self.assertEqual(p.high_stakes.count("refunds/**"), 1)
        p = self.store.set_project(PID, "high_stakes_remove", "**/auth/**")
        self.assertNotIn("**/auth/**", p.high_stakes)
        p = self.store.set_project(PID, "quiet", True)
        self.assertTrue(p.quiet)
        p = self.store.set_project(PID, "name", "orbit")
        self.assertEqual(p.name, "orbit")
        self.assertEqual(self.store.project(PID), p)
        self.assertEqual(self.commits[-1], f"project: {PID}")

    def test_set_project_rejects(self) -> None:
        self.store.ensure_project(PID, "/a/orbit-pay")
        cases = [
            ("quiet", "yes", "invalid"),
            ("high_stakes_remove", "nope/**", "invalid"),
            ("test_command", "  ", "invalid"),
            ("colour", "red", "invalid"),
        ]
        for key, value, code in cases:
            with self.assertRaises(EngineError) as caught:
                self.store.set_project(PID, key, value)
            self.assertEqual(caught.exception.code, code, key)
        with self.assertRaises(EngineError) as caught:
            self.store.set_project("prj_000000000000", "quiet", True)
        self.assertEqual(caught.exception.code, "not_found")
        with self.assertRaises(EngineError):
            self.store.set_project("../escape", "quiet", True)
        self.assertIsNone(self.store.project("../escape"))


class DetectAndPortTest(support.TempHome):
    def test_detect_test_command(self) -> None:
        root = self.tmp / "p"
        root.mkdir()
        self.assertIsNone(config.detect_test_command(root))
        (root / "pyproject.toml").write_text("[project]\nname = 'x'\n")
        self.assertIsNone(config.detect_test_command(root))
        (root / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")
        self.assertEqual(config.detect_test_command(root), "pytest -q")
        (root / "pyproject.toml").unlink()
        for name in ("pytest.ini", "tox.ini", "conftest.py"):
            (root / name).write_text("")
            self.assertEqual(config.detect_test_command(root), "pytest -q", name)
            (root / name).unlink()

    def test_ports(self) -> None:
        self.assertIsNone(config.read_port())
        port = config.choose_port()
        self.assertTrue(0 < port < 65536)
        self.assertEqual(config.read_port(), port)
        self.assertEqual(paths.port_file().stat().st_mode & 0o777, 0o600)
        paths.write_private(paths.port_file(), b"0\n")
        self.assertEqual(config.read_port(), 0)
        paths.write_private(paths.port_file(), b"abc")
        self.assertIsNone(config.read_port())


if __name__ == "__main__":
    unittest.main()
