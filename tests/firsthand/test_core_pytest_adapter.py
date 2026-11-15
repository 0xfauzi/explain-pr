"""firsthand.runner.pytest_adapter: test listing, changed tests, junit reading, real runs."""

from __future__ import annotations

import subprocess
import textwrap
import unittest
from pathlib import Path

import support

from firsthand.runner import pytest_adapter as pa

SOURCE = textwrap.dedent("""\
    import pytest

    def helper():
        assert False

    def test_one():
        x = 1
        assert x == 1
        assert x > 0

    async def test_async():
        assert True

    def test_no_assert():
        def test_nested():
            assert 1
        pass

    class TestThing:
        def test_method(self):
            assert "a" == "a"

        def helper(self):
            pass

    class Other:
        def test_ignored(self):
            assert 1
""")


def _case(name: str, classname: str, child: str = "") -> str:
    return f'<testcase classname="{classname}" name="{name}" time="0.001">{child}</testcase>'


def _junit(tmp: Path, *cases: str) -> Path:
    path = tmp / "j.xml"
    body = "".join(cases)
    path.write_text(
        '<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest">'
        f"{body}</testsuite></testsuites>"
    )
    return path


class ListTestsTest(support.TempHome):
    def test_list_tests(self) -> None:
        items = pa.list_tests(SOURCE, "tests/test_x.py")
        self.assertEqual(
            [i.id for i in items],
            [
                "tests/test_x.py::test_one",
                "tests/test_x.py::test_async",
                "tests/test_x.py::test_no_assert",
                "tests/test_x.py::TestThing::test_method",
            ],
        )
        one = items[0]
        self.assertEqual(
            (one.n, one.status, one.name, one.path, one.line),
            (0, "new", "test_one", "tests/test_x.py", 6),
        )
        self.assertEqual(one.assert_lines, (8, 9))
        self.assertEqual(one.assert_line, 9)
        self.assertEqual(one.assert_text, "assert x > 0")
        no_assert = items[2]
        # the nested function's assert is inside the test's body, so ast.walk sees it
        self.assertEqual(no_assert.assert_lines, (16,))
        self.assertEqual(items[3].name, "test_method")

    def test_syntax_error(self) -> None:
        self.assertEqual(pa.list_tests("def test_x(:\n", "t.py"), ())

    def test_long_assert_text_cut(self) -> None:
        src = "def test_x():\n    assert " + "a" * 300 + "\n"
        item = pa.list_tests(src, "t.py")[0]
        self.assertEqual(len(item.assert_text), 200)

    def test_changed_tests(self) -> None:
        base = "def test_a():\n    assert 1\n\ndef test_b():\n    assert 2\n\ndef test_c():\n    assert 3\n"
        head = (
            "def test_new_first():\n    assert 0\n\n"
            "def test_a():\n    # a comment only\n\n    assert 1\n\n"
            "def test_b():\n    assert 20\n\n"
            "def test_c():\n    assert 30\n\n"
            "def test_new_last():\n    assert 9\n"
        )
        items = pa.changed_tests(base, head, "t.py")
        self.assertEqual(
            [(i.name, i.status) for i in items],
            [
                ("test_new_first", "new"),
                ("test_new_last", "new"),
                ("test_b", "edited"),
                ("test_c", "edited"),
            ],
        )
        self.assertEqual(
            [i.name for i in pa.changed_tests(None, base, "t.py")],
            ["test_a", "test_b", "test_c"],
        )
        self.assertEqual(pa.changed_tests(base, "def broken(:\n", "t.py"), ())

    def test_argv(self) -> None:
        self.assertEqual(
            pa.argv(Path("/v/bin/python"), ["t.py::a", "t.py::b"], Path("/o/j.xml")),
            [
                "/v/bin/python",
                "-m",
                "pytest",
                "t.py::a",
                "t.py::b",
                "-q",
                "-p",
                "no:cacheprovider",
                "--maxfail=0",
                "--tb=long",
                "--junitxml=/o/j.xml",
            ],
        )

    def test_unittest_case_class_by_any_name(self) -> None:
        src = textwrap.dedent("""\
            import unittest

            class RefundCase(unittest.TestCase):
                def test_once(self):
                    self.assertEqual(1, 1)

            class Helper:
                def test_not_collected(self):
                    pass
        """)
        self.assertEqual(
            [i.id for i in pa.list_tests(src, "tests/test_r.py")],
            ["tests/test_r.py::RefundCase::test_once"],
        )

    def test_classify(self) -> None:
        self.assertEqual(pa.classify("passed"), "still_passes")
        self.assertEqual(pa.classify("assert"), "fails_on_assertion")
        for other in ("other", "skipped", "missing"):
            self.assertEqual(pa.classify(other), "cannot_run")


class ReadJunitTest(support.TempHome):
    ids = ("tests/test_a.py::test_x", "tests/test_a.py::TestK::test_m")

    def read(self, *cases: str) -> dict:
        return pa.read_junit(_junit(self.tmp, *cases), self.ids)

    def test_passed_and_missing(self) -> None:
        got = self.read(_case("test_x", "tests.test_a"))
        self.assertEqual(got[self.ids[0]], ("passed", None))
        self.assertEqual(got[self.ids[1]], ("missing", None))

    def test_assert_shapes(self) -> None:
        bare = '<failure message="assert 1 == 2">def test_x():\n&gt; assert 1 == 2\nE assert\n\ntests/test_a.py:5: AssertionError</failure>'
        failed = '<failure message="Failed: no">tests/test_a.py:6: Failed</failure>'
        got = self.read(
            _case("test_x", "tests.test_a", bare),
            _case("test_m", "tests.test_a.TestK", failed),
        )
        self.assertEqual(got[self.ids[0]], ("assert", 5))
        self.assertEqual(got[self.ids[1]], ("assert", 6))

    def test_assert_read_from_message_when_the_text_is_short(self) -> None:
        # --tb=short, --tb=native and --tb=no leave no "path:line: AssertionError" line.
        native = '<failure message="assert 1 == 2">Traceback (most recent call last):\n  File "x"\nAssertionError: assert 1 == 2</failure>'
        empty = '<failure message="Failed: DID NOT RAISE ValueError"></failure>'
        got = self.read(
            _case("test_x", "tests.test_a", native),
            _case("test_m", "tests.test_a.TestK", empty),
        )
        self.assertEqual(got[self.ids[0]][0], "assert")
        self.assertEqual(got[self.ids[1]][0], "assert")
        other = '<failure message="KeyError: 1"></failure>'
        self.assertEqual(
            self.read(_case("test_x", "tests.test_a", other))[self.ids[0]][0], "other"
        )

    def test_other_shapes(self) -> None:
        imp = '<failure message="ModuleNotFoundError">tests/test_a.py:7: ModuleNotFoundError</failure>'
        setup = (
            '<error message="failed on setup">tests/test_a.py:9: RuntimeError</error>'
        )
        got = self.read(
            _case("test_x", "tests.test_a", imp),
            _case("test_m", "tests.test_a.TestK", setup),
        )
        self.assertEqual(got[self.ids[0]], ("other", 7))
        self.assertEqual(got[self.ids[1]], ("other", 9))

    def test_line_only_from_the_test_file(self) -> None:
        elsewhere = '<failure message="x">app/service.py:12: AssertionError</failure>'
        got = self.read(_case("test_x", "tests.test_a", elsewhere))
        self.assertEqual(got[self.ids[0]], ("assert", None))

    def test_skipped(self) -> None:
        got = self.read(
            _case("test_x", "tests.test_a", '<skipped message="s">s</skipped>')
        )
        self.assertEqual(got[self.ids[0]], ("skipped", None))

    def test_parametrized(self) -> None:
        fail = '<failure message="a">tests/test_a.py:13: AssertionError</failure>'
        err = '<failure message="b">tests/test_a.py:13: KeyError</failure>'
        both_pass = self.read(
            _case("test_x[1]", "tests.test_a"), _case("test_x[2]", "tests.test_a")
        )
        self.assertEqual(both_pass[self.ids[0]], ("passed", None))
        one_assert = self.read(
            _case("test_x[1]", "tests.test_a"), _case("test_x[2]", "tests.test_a", fail)
        )
        self.assertEqual(one_assert[self.ids[0]], ("assert", 13))
        mixed = self.read(
            _case("test_x[1]", "tests.test_a", fail),
            _case("test_x[2]", "tests.test_a", err),
        )
        self.assertEqual(mixed[self.ids[0]][0], "other")

    def test_wrong_class_or_module_does_not_match(self) -> None:
        got = self.read(
            _case("test_x", "tests.test_b"), _case("test_m", "tests.test_a.TestOther")
        )
        self.assertEqual(got[self.ids[0]], ("missing", None))
        self.assertEqual(got[self.ids[1]], ("missing", None))

    def test_collection_failure(self) -> None:
        err = '<error message="collection failure">E   ModuleNotFoundError</error>'
        got = self.read(_case("tests.test_a", "", err))
        self.assertEqual(got, {i: ("other", None) for i in self.ids})

    def test_missing_or_broken_file(self) -> None:
        self.assertEqual(
            pa.read_junit(self.tmp / "nope.xml", self.ids),
            {i: ("missing", None) for i in self.ids},
        )
        broken = self.tmp / "b.xml"
        broken.write_text("<testsuites><testsuite")
        self.assertEqual(
            pa.read_junit(broken, self.ids), {i: ("missing", None) for i in self.ids}
        )


REAL = textwrap.dedent("""\
    import pytest

    def test_passes():
        assert 1 == 1

    def test_bare_assert():
        x = 1
        assert x == 2

    def test_failed():
        pytest.fail("no")

    def test_import_error():
        import not_a_module_anywhere

    @pytest.fixture
    def broken():
        raise RuntimeError("setup")

    def test_setup_error(broken):
        pass

    def test_skipped():
        pytest.skip("s")

    @pytest.mark.parametrize("v", [1, 2])
    def test_param(v):
        assert v == 1

    class TestK:
        def test_method(self):
            assert False
""")


class RealRunTest(support.TempHome):
    @classmethod
    def setUpClass(cls) -> None:
        cls.python = support.pytest_python()
        if cls.python is None:
            raise unittest.SkipTest(support.pytest_python_reason())

    def test_one_real_run_per_shape(self) -> None:
        proj = self.tmp / "p"
        (proj / "tests").mkdir(parents=True)
        (proj / "tests" / "test_a.py").write_text(REAL)
        items = pa.list_tests(REAL, "tests/test_a.py")
        ids = [i.id for i in items]
        junit = self.tmp / "out.xml"
        env = {
            "PATH": "/usr/bin:/bin",
            "HOME": str(self.tmp),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.assertTrue(pa.has_pytest(self.python, env, proj))
        subprocess.run(
            pa.argv(self.python, ids, junit),
            cwd=proj,
            env=env,
            capture_output=True,
            timeout=120,
            check=False,
        )
        got = pa.read_junit(junit, ids)
        short = {i.split("::")[-1]: v for i, v in got.items()}
        self.assertEqual(short["test_passes"], ("passed", None))
        self.assertEqual(short["test_bare_assert"], ("assert", 8))
        self.assertEqual(short["test_failed"], ("assert", 11))
        self.assertEqual(short["test_import_error"][0], "other")
        self.assertEqual(short["test_setup_error"][0], "other")
        self.assertEqual(short["test_skipped"], ("skipped", None))
        self.assertEqual(short["test_param"], ("assert", 28))
        self.assertEqual(short["test_method"], ("assert", 32))

    def test_project_addopts_do_not_change_the_result(self) -> None:
        # A stop-early option or a short traceback style in addopts must not turn
        # an assertion failure, or a test after the first failure, into "cannot run".
        expected = None
        items = pa.list_tests(REAL, "tests/test_a.py")
        ids = [i.id for i in items]
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp)}
        for n, addopts in enumerate(
            [
                "",
                "-x",
                "--maxfail=1",
                "--tb=short",
                "--tb=native",
                "--tb=no",
                "--tb=line",
            ]
        ):
            proj = self.tmp / f"p{n}"
            (proj / "tests").mkdir(parents=True)
            (proj / "tests" / "test_a.py").write_text(REAL)
            (proj / "pyproject.toml").write_text(
                f'[tool.pytest.ini_options]\naddopts = "{addopts}"\n'
            )
            junit = self.tmp / f"out{n}.xml"
            subprocess.run(
                pa.argv(self.python, ids, junit),
                cwd=proj,
                env=env,
                capture_output=True,
                timeout=120,
                check=False,
            )
            got = pa.read_junit(junit, ids)
            if expected is None:
                expected = got
                self.assertNotIn("missing", {o for o, _ in got.values()})
            self.assertEqual(got, expected, addopts)

    def test_real_collection_failure(self) -> None:
        proj = self.tmp / "p"
        (proj / "tests").mkdir(parents=True)
        src = "from nowhere_at_all import thing\n\ndef test_x():\n    assert thing\n"
        (proj / "tests" / "test_b.py").write_text(src)
        junit = self.tmp / "out.xml"
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp)}
        subprocess.run(
            pa.argv(self.python, ["tests/test_b.py::test_x"], junit),
            cwd=proj,
            env=env,
            capture_output=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(
            pa.read_junit(junit, ["tests/test_b.py::test_x"]),
            {"tests/test_b.py::test_x": ("other", None)},
        )

    def test_has_pytest_false(self) -> None:
        import sys

        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "PYTHONNOUSERSITE": "1"}
        probe = subprocess.run(
            [sys.executable, "-c", "import pytest"],
            env=env,
            capture_output=True,
            check=False,
        )
        if probe.returncode == 0:
            self.skipTest("the base interpreter has pytest installed")
        self.assertFalse(pa.has_pytest(Path(sys.executable), env, self.tmp))
