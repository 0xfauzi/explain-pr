"""firsthand.moments.revert_test: match, score, cue, finding, replies, and real runs."""

from __future__ import annotations

import itertools
import subprocess
import sys
import threading
import unittest

import support

from firsthand import gitwatch, paths
from firsthand.model import FileChange, Key, KeyItem, ProjectSettings, Reply, TestItem
from firsthand.moments import REGISTRY
from firsthand.moments import revert_test as rt
from firsthand.runner.snapshot import SnapshotStore


def _ids():
    counter = itertools.count(1)
    return lambda: f"01CHECK{next(counter):04d}"


def _key(*results: str, how: str = "pytest") -> Key:
    tests = tuple(
        KeyItem(
            id=f"tests/test_a.py::test_{i}",
            result=r,
            assert_line=10 + i,
            assert_text=f"assert x == {i}",
            fail_line=20 + i if r != "still_passes" else None,
        )
        for i, r in enumerate(results, start=1)
    )
    return Key(
        moment="M",
        kind="revert_test",
        how=how,
        base_tree="b",
        head_tree="h",
        made_at="2026-11-14T09:40:02Z",
        tests=tests,
        steps=(),
        undone_paths=(),
        duration_s=1.0,
    )


class SurfaceTest(support.TempHome):
    def test_registry_and_constants(self) -> None:
        self.assertEqual(REGISTRY[0], rt)
        self.assertEqual(
            [m.KIND for m in REGISTRY], ["revert_test", "call_it", "brief"]
        )
        self.assertEqual(
            (rt.KIND, rt.SKILL, rt.HEADLINE, rt.BREAKS),
            ("revert_test", 1, "REVERT TEST", ("test_run", "done")),
        )
        for name in (
            "match",
            "run",
            "score",
            "cue",
            "finding",
            "reply_words",
            "parse_reply",
            "plan",
            "key",
        ):
            self.assertTrue(callable(getattr(rt, name)), name)

    def test_reply_words(self) -> None:
        self.assertEqual(rt.reply_words(1), ("fails", "passes", "don't know"))
        self.assertEqual(rt.reply_words(3), ("1", "2", "3", "none", "don't know"))

    def test_parse_reply(self) -> None:
        table = [
            ("2", 3, Reply("2", None)),
            (" 2 sure ", 3, Reply("2", "high")),
            ("2 Not Sure.", 3, Reply("2", "low")),
            ("NONE  not   sure", 3, Reply("none", "low")),
            ("none.", 2, Reply("none", None)),
            ("don’t know", 3, Reply("dont_know", None)),
            ("Don't know sure", 2, Reply("dont_know", None)),
            ("fails", 1, Reply("fails", None)),
            ("passes sure", 1, Reply("passes", "high")),
            ("4", 3, None),
            ("fails", 3, None),
            ("1", 1, None),
            ("sure", 2, None),
            ("2 please", 3, None),
            ("", 2, None),
            ("skip", 2, None),
        ]
        for text, n, want in table:
            self.assertEqual(rt.parse_reply(text, n), want, (text, n))

    def test_plan(self) -> None:
        self.assertEqual(rt.plan(None), ("scratch", "control", "undo", "undone"))


class ScoreTest(support.TempHome):
    def test_several_tests(self) -> None:
        k = _key("fails_on_assertion", "still_passes", "cannot_run")
        hit = rt.score("2", k)
        self.assertEqual(
            (hit.result, hit.outcome_kind, hit.catch, hit.unscored_reason),
            ("match", "uncommon", True, None),
        )
        self.assertEqual(rt.score("1", k).result, "miss")
        self.assertEqual(rt.score("3", k).result, "miss")
        self.assertEqual(rt.score("none", k).result, "miss")
        self.assertFalse(rt.score("none", k).catch)
        common = _key("fails_on_assertion", "cannot_run")
        none = rt.score("none", common)
        self.assertEqual(
            (none.result, none.outcome_kind, none.catch), ("match", "common", False)
        )
        self.assertEqual(rt.score("1", common).result, "miss")
        self.assertIsNone(rt.score("dont_know", k))
        self.assertIsNone(rt.score("4", k))
        self.assertIsNone(rt.score("fails", k))

    def test_one_test(self) -> None:
        for result, fails_matches in (
            ("fails_on_assertion", True),
            ("cannot_run", True),
            ("does_not_pass", True),
            ("still_passes", False),
        ):
            k = _key(result, how="exit_code" if result == "does_not_pass" else "pytest")
            self.assertEqual(
                rt.score("fails", k).result, "match" if fails_matches else "miss"
            )
            self.assertEqual(
                rt.score("passes", k).result, "miss" if fails_matches else "match"
            )
            self.assertEqual(
                rt.score("passes", k).outcome_kind,
                "common" if fails_matches else "uncommon",
            )
        self.assertTrue(rt.score("passes", _key("still_passes")).catch)
        self.assertIsNone(rt.score("none", _key("still_passes")))
        self.assertIsNone(rt.score("dont_know", _key("still_passes")))

    def test_finding(self) -> None:
        k = _key("fails_on_assertion", "still_passes", "cannot_run")
        self.assertEqual(
            [t.result for t in rt.finding(k)], ["still_passes", "cannot_run"]
        )
        self.assertEqual(rt.finding(_key("fails_on_assertion")), ())
        self.assertEqual(rt.finding(_key("does_not_pass", how="exit_code")), ())


def _item(n: int, asserts: tuple[int, ...], line: int = 5) -> TestItem:
    return TestItem(
        n=n,
        id=f"tests/test_a.py::test_{n}",
        name=f"test_{n}",
        path="tests/test_a.py",
        line=line,
        status="new",
        assert_lines=asserts,
        assert_line=asserts[-1] if asserts else None,
        assert_text=None,
    )


class CueTest(support.TempHome):
    def test_none_on_match_or_unscorable(self) -> None:
        k = _key("fails_on_assertion", "still_passes")
        self.assertIsNone(rt.cue("2", k))
        self.assertIsNone(rt.cue("dont_know", k))
        self.assertIsNone(rt.cue("fails", k))

    def test_still_passing_test_assertions(self) -> None:
        k = _key("fails_on_assertion", "still_passes")
        text, items = rt.cue("1", k)
        self.assertEqual(text, "Its only assertion is at tests/test_a.py:12.")
        self.assertEqual(items, (k.tests[1],))
        text, _ = rt.cue("1", k, [_item(2, (30, 31, 32))])
        self.assertEqual(text, "Its assertions are at tests/test_a.py:30, 31 and 32.")
        text, _ = rt.cue("none", k, [_item(2, (30, 31))])
        self.assertEqual(text, "Its assertions are at tests/test_a.py:30 and 31.")
        text, _ = rt.cue("1", k, [_item(2, (), line=7)])
        self.assertEqual(text, "It has no assert statement: tests/test_a.py:7.")

    def test_said_passes_and_it_fails(self) -> None:
        k = _key("fails_on_assertion", "cannot_run")
        text, items = rt.cue("2", k)
        self.assertEqual(text, "It fails at tests/test_a.py:22.")
        self.assertEqual(items, (k.tests[1],))
        one = _key("fails_on_assertion")
        self.assertEqual(rt.cue("passes", one)[0], "It fails at tests/test_a.py:21.")
        no_fail_line = Key(
            **{
                **one.__dict__,
                "tests": (
                    KeyItem(
                        "tests/test_a.py::test_1", "fails_on_assertion", 11, None, None
                    ),
                ),
            }
        )
        self.assertEqual(
            rt.cue("passes", no_fail_line)[0], "It fails at tests/test_a.py:11."
        )

    def test_one_test_said_fails(self) -> None:
        k = _key("still_passes")
        self.assertEqual(
            rt.cue("fails", k)[0], "Its only assertion is at tests/test_a.py:11."
        )

    def test_generic(self) -> None:
        k = _key("does_not_pass", how="exit_code")
        self.assertEqual(
            rt.cue("passes", k)[0], "It was checked by exit code only: tests/test_a.py."
        )


class MatchTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "proj"
        support.make_repo(
            self.repo,
            {
                "app.py": "def f():\n    return 1\n",
                "tests/test_old.py": "def test_old():\n    assert 1\n",
                "refunds/svc.py": "x = 1\n",
            },
        )
        self.store = SnapshotStore(self.repo, gitwatch.project_id(self.repo))
        self.base = self.store.head_tree()

    def candidate(self, files, command="pytest -q", high=("refunds/**",)):
        support.write_files(self.repo, files)
        head = self.store.take()
        m = rt.MatchInput(
            project_id="prj",
            project_root=str(self.repo),
            task_id="T",
            change_id="C",
            base_tree=self.base,
            head_tree=head,
            changes=self.store.diff(self.base, head),
            test_command=command,
            high_stakes=high,
        )
        return rt.match(m, self.store, _ids())

    def test_none_without_test_change(self) -> None:
        self.assertIsNone(self.candidate({"app.py": "def f():\n    return 2\n"}))

    def test_none_without_source_change(self) -> None:
        self.assertIsNone(
            self.candidate({"tests/test_new.py": "def test_n():\n    assert 1\n"})
        )

    def test_none_without_test_command(self) -> None:
        self.assertIsNone(
            self.candidate(
                {
                    "app.py": "y = 2\n",
                    "tests/test_new.py": "def test_n():\n    assert 1\n",
                },
                command=None,
            )
        )

    def test_none_when_only_unchanged_tests(self) -> None:
        self.assertIsNone(
            self.candidate(
                {
                    "app.py": "y = 2\n",
                    "tests/test_old.py": "def test_old():\n    # c\n    assert 1\n",
                }
            )
        )

    def test_renamed_test_file_with_unchanged_tests_is_not_new(self) -> None:
        support.write_files(self.repo, {"tests/test_old.py": None})
        self.assertIsNone(
            self.candidate(
                {
                    "app.py": "y = 2\n",
                    "tests/test_moved.py": "def test_old():\n    assert 1\n",
                }
            )
        )
        c = self.candidate(
            {
                "tests/test_moved.py": (
                    "def test_old():\n    assert 1\n\n\ndef test_n():\n    assert 2\n"
                )
            }
        )
        self.assertEqual([t.name for t in c.tests], ["test_n"])

    def test_four_test_cap_and_order(self) -> None:
        c = self.candidate(
            {
                "app.py": "def f():\n    return 2\n",
                "tests/test_old.py": "def test_old():\n    assert 2\n",
                "tests/test_new.py": "".join(
                    f"def test_n{i}():\n    assert {i}\n\n" for i in range(5)
                ),
            }
        )
        self.assertEqual(
            [(t.n, t.name, t.status) for t in c.tests],
            [
                (1, "test_n0", "new"),
                (2, "test_n1", "new"),
                (3, "test_n2", "new"),
                (4, "test_n3", "new"),
            ],
        )
        c = self.candidate({"tests/test_new.py": "def test_n0():\n    assert 0\n"})
        self.assertEqual(
            [(t.n, t.name, t.status) for t in c.tests],
            [(1, "test_n0", "new"), (2, "test_old", "edited")],
        )
        self.assertEqual(c.kind, "revert_test")
        self.assertEqual(c.check_id, "01CHECK0001")
        self.assertEqual(c.how, "pytest")
        self.assertEqual(c.source_changes, (FileChange("app.py", "M"),))
        self.assertIsNone(c.high_stakes)

    def test_high_stakes_and_generic(self) -> None:
        c = self.candidate(
            {"refunds/svc.py": "x = 2\n", "tests/test_new.js": "t\n"},
            command="npm test",
        )
        self.assertEqual(c.how, "exit_code")
        self.assertEqual(c.high_stakes, "refunds/**")
        self.assertEqual([t.id for t in c.tests], ["tests/test_new.js"])


APP_BASE = "def total(a, b):\n    return a - b\n"
APP_HEAD = "def total(a, b):\n    return a + b\n\n\ndef double(x):\n    return 2 * x\n"
TEST_APP = (
    "from app import total\n\n\n"
    "def test_total():\n    assert total(1, 2) == 3\n\n\n"
    "def test_type():\n    assert isinstance(total(1, 2), int)\n"
)
TEST_NEW = "from app import double\n\n\ndef test_double():\n    assert double(2) == 4\n"


class RunTest(support.TempHome):
    @classmethod
    def setUpClass(cls) -> None:
        cls.python = support.pytest_python()
        if cls.python is None:
            raise unittest.SkipTest(support.pytest_python_reason())

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.tmp / "proj"
        support.make_repo(self.repo, {"app.py": APP_BASE, "tests/conftest.py": ""})
        self.store = SnapshotStore(self.repo, gitwatch.project_id(self.repo))
        self.base = self.store.head_tree()
        self.controls: list[bool] = []

    def make(self, files, command="pytest -q"):
        support.write_files(self.repo, files)
        head = self.store.take()
        m = rt.MatchInput(
            "prj",
            str(self.repo),
            "T",
            "C",
            self.base,
            head,
            self.store.diff(self.base, head),
            command,
            (),
        )
        c = rt.match(m, self.store, _ids())
        self.assertIsNotNone(c)
        return c

    def ctx(
        self, command="pytest -q", limit=120.0, venv=None, cancel=None, on_control=None
    ):
        project = ProjectSettings(
            id="prj",
            name="proj",
            roots=(str(self.repo),),
            test_command=command,
            high_stakes=(),
        )
        return rt.RunContext(
            store=self.store,
            project=project,
            venv_hint=venv or str(self.python.parent.parent),
            time_limit_s=limit,
            on_control=on_control or self.controls.append,
            cancel=cancel or threading.Event(),
        )

    def test_three_results(self) -> None:
        c = self.make(
            {
                "app.py": APP_HEAD,
                "tests/test_app.py": TEST_APP,
                "tests/test_new.py": TEST_NEW,
            }
        )
        before = support.repo_fingerprint(self.repo)
        out = rt.run(c, self.ctx())
        self.assertIsNone(out.unavailable, out)
        results = {t.id.split("::")[-1]: t.result for t in out.key.tests}
        self.assertEqual(
            results,
            {
                "test_total": "fails_on_assertion",
                "test_type": "still_passes",
                "test_double": "cannot_run",
            },
        )
        self.assertEqual(self.controls, [True])
        self.assertFalse(paths.scratch_dir(c.check_id).exists())
        self.assertEqual(support.repo_fingerprint(self.repo), before)
        k = out.key
        self.assertEqual(k.moment, c.check_id)
        self.assertEqual(k.undone_paths, ("app.py",))
        self.assertEqual(
            [s.step for s in k.steps], ["control", "control", "undone", "undone"]
        )
        total = next(t for t in k.tests if t.id.endswith("test_total"))
        self.assertEqual(total.fail_line, 5)
        self.assertEqual(total.assert_text, "assert total(1, 2) == 3")
        self.assertEqual(rt.score("2", k).result, "match")

    def test_control_fails(self) -> None:
        c = self.make(
            {
                "app.py": APP_HEAD,
                "tests/test_app.py": "def test_bad():\n    assert False\n",
            }
        )
        out = rt.run(c, self.ctx())
        self.assertEqual(
            (out.key, out.unavailable, out.step),
            (None, "does not match here", "control"),
        )
        self.assertEqual(self.controls, [False])
        self.assertFalse(paths.scratch_dir(c.check_id).exists())

    def test_time_limit(self) -> None:
        c = self.make(
            {
                "app.py": APP_HEAD,
                "tests/test_app.py": "import time\n\ndef test_slow():\n    time.sleep(30)\n",
            }
        )
        out = rt.run(c, self.ctx(limit=3))
        self.assertEqual(out.unavailable, "time limit")
        self.assertEqual(out.step, "control")
        self.assertFalse(paths.scratch_dir(c.check_id).exists())

    def test_cancel(self) -> None:
        c = self.make({"app.py": APP_HEAD, "tests/test_app.py": TEST_APP})
        cancel = threading.Event()

        def on_control(ok: bool) -> None:
            self.controls.append(ok)
            cancel.set()

        out = rt.run(c, self.ctx(cancel=cancel, on_control=on_control))
        self.assertEqual((out.key, out.unavailable), (None, None))
        self.assertEqual(self.controls, [True])
        self.assertFalse(paths.scratch_dir(c.check_id).exists())

    def test_pytest_not_found(self) -> None:
        bare = self.tmp / "bare"
        subprocess.run(
            [sys.executable, "-m", "venv", "--without-pip", str(bare)], check=True
        )
        c = self.make({"app.py": APP_HEAD, "tests/test_app.py": TEST_APP})
        out = rt.run(c, self.ctx(venv=str(bare)))
        self.assertEqual((out.unavailable, out.step), ("pytest not found", "setup"))
        self.assertEqual(self.controls, [False])

    def test_generic(self) -> None:
        unit = (
            "import unittest\nfrom app import total\n\n\n"
            "class T(unittest.TestCase):\n    def test_total(self):\n"
            "        self.assertEqual(total(1, 2), 3)\n"
        )
        command = f"{sys.executable} -m unittest"
        c = self.make({"app.py": APP_HEAD, "tests/test_unit.py": unit}, command=command)
        self.assertEqual(c.how, "exit_code")
        out = rt.run(c, self.ctx(command=command))
        self.assertIsNone(out.unavailable, out)
        self.assertEqual([t.result for t in out.key.tests], ["does_not_pass"])
        self.assertEqual(out.key.how, "exit_code")
