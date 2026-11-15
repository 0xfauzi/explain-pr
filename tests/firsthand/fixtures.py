"""Fixture projects and recorded spool sequences for the integrator's tests.

Each fixture is a small git repo built in a temporary folder: a base commit, then
an uncommitted change the test writes between the two halves of a session. The
spool lines are built in code, with the fixture's path as cwd and the shared test
virtualenv as venv, and go through events.encode and events.decode so that they
are exactly what the dispatcher would have appended.

Every sequence begins with one earlier prompt and turn end on the same day in
another session, so the fixture's task is not started by the first prompt of the
day (build-2a-contract.md section 10.5).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import support

from firsthand import events
from firsthand.model import SpoolEvent

PYPROJECT = '[project]\nname = "fixture"\nversion = "0"\n\n[tool.pytest.ini_options]\n'

BASE_REFUNDS = '''def refunds(keys):
    """One refund per key, in order."""
    return list(keys)
'''

FIXED_REFUNDS = '''def refunds(keys):
    """One refund per key, in order."""
    return list(dict.fromkeys(keys))
'''

NEW_FUNCTION = (
    FIXED_REFUNDS
    + """

def refund_total(amounts):
    return sum(amounts)
"""
)

TEST_PROVES = """from refunds import refunds


def test_same_key_refunds_once():
    assert refunds(["a", "a"]) == ["a"]
"""

TEST_PASSES_ANYWAY = """from refunds import refunds


def test_refund_response_is_stable():
    assert isinstance(refunds(["a"]), list)
"""

TEST_NEEDS_NEW = """from refunds import refund_total


def test_refund_total_adds_up():
    assert refund_total([1, 2]) == 3
"""

TEST_FAILS_ON_HEAD = """from refunds import refunds


def test_refunds_are_reversed():
    assert refunds(["a", "b"]) == ["b", "a"]
"""

BASE_TEST_OLD = """from refunds import refunds


def test_refunds_keep_order():
    assert refunds(["a", "b"]) == ["a", "b"]


def test_duplicate_keys():
    assert refunds(["a", "a"]) == ["a", "a"]
"""

HEAD_TEST_EDITED = """from refunds import refunds


def test_refunds_keep_order():
    assert refunds(["a", "b"]) == ["a", "b"]


def test_duplicate_keys():
    assert refunds(["a", "a"]) == ["a"]
"""

DAY = "2026-11-14"


@dataclass(frozen=True)
class Fixture:
    name: str
    base: Mapping[str, str]
    change: Mapping[str, str | None]
    test_run: bool = True  # the agent ran the test command and it passed
    expected: tuple[str, ...] = ()  # key results in card order
    source: str = "refunds.py"
    extra: Mapping[str, str] = field(default_factory=dict)


def _base(**more: str) -> dict[str, str]:
    return {"pyproject.toml": PYPROJECT, "refunds.py": BASE_REFUNDS, **more}


FIXTURES: dict[str, Fixture] = {
    "proves": Fixture(
        "proves",
        _base(),
        {"refunds.py": FIXED_REFUNDS, "tests/test_refunds.py": TEST_PROVES},
        expected=("fails_on_assertion",),
    ),
    "passes_anyway": Fixture(
        "passes_anyway",
        _base(),
        {"refunds.py": FIXED_REFUNDS, "tests/test_refunds.py": TEST_PASSES_ANYWAY},
        expected=("still_passes",),
    ),
    "needs_new_code": Fixture(
        "needs_new_code",
        _base(),
        {"refunds.py": NEW_FUNCTION, "tests/test_total.py": TEST_NEEDS_NEW},
        expected=("cannot_run",),
    ),
    "mixed3": Fixture(
        "mixed3",
        _base(),
        {
            "refunds.py": NEW_FUNCTION,
            "tests/test_a.py": TEST_PROVES,
            "tests/test_b.py": TEST_PASSES_ANYWAY,
            "tests/test_c.py": TEST_NEEDS_NEW,
        },
        expected=("fails_on_assertion", "still_passes", "cannot_run"),
    ),
    "edited_test": Fixture(
        "edited_test",
        _base(**{"tests/test_refunds.py": BASE_TEST_OLD}),
        {"refunds.py": FIXED_REFUNDS, "tests/test_refunds.py": HEAD_TEST_EDITED},
        expected=("fails_on_assertion",),
    ),
    "control_fails": Fixture(
        "control_fails",
        _base(),
        {"refunds.py": FIXED_REFUNDS, "tests/test_refunds.py": TEST_FAILS_ON_HEAD},
        test_run=False,
    ),
    "no_tests": Fixture(
        "no_tests",
        _base(),
        {"refunds.py": FIXED_REFUNDS},
    ),
    "high_stakes": Fixture(
        "high_stakes",
        {"pyproject.toml": PYPROJECT, "payments/refunds.py": BASE_REFUNDS},
        {
            "payments/refunds.py": FIXED_REFUNDS,
            "tests/test_refunds.py": TEST_PASSES_ANYWAY.replace(
                "from refunds import", "from payments.refunds import"
            ),
        },
        expected=("still_passes",),
        source="payments/refunds.py",
    ),
}


def build(root: Path, fx: Fixture) -> Path:
    """The fixture repo with its base commit. The change is written later."""
    root.mkdir(parents=True, exist_ok=True)
    support.make_repo(root, fx.base)
    return root


def write_change(root: Path, fx: Fixture) -> None:
    support.write_files(root, fx.change)


class Clock:
    """Spool times one second apart, from a start time on the fixture day."""

    def __init__(self, start: str = "09:00:00") -> None:
        h, m, s = (int(x) for x in start.split(":"))
        self.t = h * 3600 + m * 60 + s

    def __call__(self, step: int = 1) -> str:
        self.t += step
        h, rest = divmod(self.t, 3600)
        m, s = divmod(rest, 60)
        return f"{DAY}T{h:02d}:{m:02d}:{s:02d}Z"


def line(
    clock: Clock, cwd: Path, session: str, event: str, **keys: object
) -> SpoolEvent:
    raw = {
        "v": 1,
        "id": events.new_event_id(),
        "at": clock(),
        "agent": "claude-code",
        "session": session,
        "cwd": str(cwd),
        "event": event,
        **keys,
    }
    ev = events.decode(events.encode(raw))
    assert ev is not None, raw
    return ev


def warmup(clock: Clock, cwd: Path, venv: str | None) -> list[SpoolEvent]:
    """The day's first prompt and its turn end, in another session."""
    return [
        line(clock, cwd, "s0", "session_start", source="startup", venv=venv),
        line(clock, cwd, "s0", "prompt_submit", prompt="good morning", venv=venv),
        line(clock, cwd, "s0", "turn_end"),
    ]


def task_start(
    clock: Clock, cwd: Path, venv: str | None, prompt: str = "fix the refund bug"
) -> list[SpoolEvent]:
    """The prompt that starts the fixture's task, before the change exists."""
    return [
        line(clock, cwd, "s1", "session_start", source="startup", venv=venv),
        line(clock, cwd, "s1", "prompt_submit", prompt=prompt, venv=venv),
    ]


def edits_and_stop(
    clock: Clock, cwd: Path, fx: Fixture, session: str = "s1"
) -> list[SpoolEvent]:
    """The agent's edits, its test run if any, and the turn end."""
    out: list[SpoolEvent] = []
    for i, path in enumerate(sorted(fx.change)):
        target = str(cwd / path)
        use = f"toolu_{fx.name}_{i}"
        out.append(
            line(
                clock,
                cwd,
                session,
                "before_tool",
                tool="edit",
                tool_use=use,
                paths=[target],
            )
        )
        out.append(
            line(
                clock,
                cwd,
                session,
                "after_tool",
                tool="edit",
                tool_use=use,
                paths=[target],
            )
        )
    if fx.test_run:
        out.append(
            line(
                clock,
                cwd,
                session,
                "after_tool",
                tool="shell",
                tool_use=f"toolu_{fx.name}_run",
                command="python -m pytest -q",
                exit=0,
                failing=[],
            )
        )
    out.append(line(clock, cwd, session, "turn_end"))
    return out


def prompt(
    clock: Clock, cwd: Path, text: str, session: str = "s1", venv: str | None = None
) -> SpoolEvent:
    return line(clock, cwd, session, "prompt_submit", prompt=text, venv=venv)


def stop(clock: Clock, cwd: Path, session: str = "s1") -> SpoolEvent:
    return line(clock, cwd, session, "turn_end")


# ------------------------------------------------------------- Call it (2b)

RATES_OK = "RATE = 3\n"
RATES_BAD = "RATE = -3\n"
PRICING = """from rates import RATE


def price(n):
    value = n * RATE
    if value < 0:
        raise ValueError("negative price")
    return value
"""
PRICING_SLEEP = """import time

from rates import RATE


def price(n):
    time.sleep(0.01)
    value = abs(n * RATE)
    if value < 0:
        raise ValueError("negative price")
    return value
"""
SERVICE = """from pricing import price


def total(items):
    return sum(price(i) for i in items)
"""
TEST_TOTAL = """from service import total


def test_total():
    assert total([1, 2]) == 9
"""
TOTAL_ID = "tests/test_total.py::test_total"


@dataclass(frozen=True)
class CallFixture:
    """A pytest project whose old test goes red in the task, then maybe green."""

    name: str
    base: Mapping[str, str]
    broken: Mapping[str, str | None]  # written before the red run; may be empty
    fixed: Mapping[str, str | None] | None  # written before the green run; None: never
    picks: tuple[str, ...]  # the card's files, in card order


def _call_base(rates: str) -> dict[str, str]:
    return {
        "pyproject.toml": PYPROJECT,
        "rates.py": rates,
        "pricing.py": PRICING,
        "service.py": SERVICE,
        "tests/test_total.py": TEST_TOTAL,
    }


CALL_FIXTURES: dict[str, CallFixture] = {
    # The agent's change breaks the old test; the fix puts rates.py back.
    "causal_fix": CallFixture(
        "causal_fix",
        _call_base(RATES_OK),
        {"rates.py": RATES_BAD},
        {"rates.py": RATES_OK},
        ("pricing.py", "rates.py", "service.py"),
    ),
    # The bug is already at the base. The trace names pricing.py and service.py;
    # the fix is in rates.py, which it never names.
    "unnamed_file": CallFixture(
        "unnamed_file",
        _call_base(RATES_BAD),
        {},
        {"rates.py": RATES_OK},
        ("pricing.py", "service.py"),
    ),
    # The test goes green through a patch that adds a sleep.
    "sleep_patch": CallFixture(
        "sleep_patch",
        _call_base(RATES_OK),
        {"rates.py": RATES_BAD},
        {"pricing.py": PRICING_SLEEP},
        ("pricing.py", "rates.py", "service.py"),
    ),
    # The test never goes green before the change ends.
    "never_green": CallFixture(
        "never_green",
        _call_base(RATES_OK),
        {"rates.py": RATES_BAD},
        None,
        ("pricing.py", "rates.py", "service.py"),
    ),
}


def edit_events(
    clock: Clock, cwd: Path, paths: Mapping[str, object], tag: str, session: str = "s1"
) -> list[SpoolEvent]:
    out: list[SpoolEvent] = []
    for i, path in enumerate(sorted(paths)):
        use = f"toolu_{tag}_{i}"
        target = [str(cwd / path)]
        out.append(
            line(
                clock,
                cwd,
                session,
                "before_tool",
                tool="edit",
                tool_use=use,
                paths=target,
            )
        )
        out.append(
            line(
                clock,
                cwd,
                session,
                "after_tool",
                tool="edit",
                tool_use=use,
                paths=target,
            )
        )
    return out


def pytest_run(
    clock: Clock, cwd: Path, *, failing: tuple[str, ...] = (), session: str = "s1"
) -> SpoolEvent:
    """The agent's `python -m pytest -q`: a pass, or a fail with these ids."""
    if failing:
        return line(
            clock,
            cwd,
            session,
            "tool_failed",
            tool="shell",
            tool_use="toolu_red",
            command="python -m pytest -q",
            exit=1,
            failing=list(failing),
        )
    return line(
        clock,
        cwd,
        session,
        "after_tool",
        tool="shell",
        tool_use="toolu_green",
        command="python -m pytest -q",
        exit=0,
        failing=[],
    )


PASTED_FAILURE = (
    "the total test fails, can you look?\n\n"
    "FAILED tests/test_total.py::test_total - ValueError: negative price\n"
)
