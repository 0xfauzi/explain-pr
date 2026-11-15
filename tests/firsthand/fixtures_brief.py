"""Fixture projects for the Brief (build-2.md section 11, 2c).

A small charges project with two path categories: `api/` (input handling) and
`db/models.py` (schema). The task adds idempotency to charge creation. The three
fixtures differ only in the test the agent writes for the person's line: one that
tells done from not done, one that passes anyway, and none at all.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from fixtures import PYPROJECT

TASK_PROMPT = "add idempotency to charge creation. A retried request must not create a second charge"
LINE = "a retried charge with the same key returns the first charge id"

MODELS_BASE = "CHARGES = []\n"
MODELS_NEW = "CHARGES = []\nKEYS = {}\n"

CHARGES_BASE = """from db.models import CHARGES


def create_charge(key, amount):
    CHARGES.append({"key": key, "amount": amount})
    return len(CHARGES)
"""

CHARGES_NEW = """from db.models import CHARGES, KEYS


def create_charge(key, amount):
    if key in KEYS:
        return KEYS[key]
    CHARGES.append({"key": key, "amount": amount})
    KEYS[key] = len(CHARGES)
    return KEYS[key]
"""

TEST_BASIC = """from api.charges import create_charge


def test_create_returns_an_id():
    assert create_charge("base", 5) >= 1
"""

TEST_TELLS = """from api.charges import create_charge


def test_retry_returns_first_charge():
    first = create_charge("k1", 5)
    assert create_charge("k1", 5) == first
"""

TEST_ANYWAY = """from api.charges import create_charge


def test_retry_returns_an_id():
    assert isinstance(create_charge("k2", 5), int)
"""

BASE: Mapping[str, str] = {
    "pyproject.toml": PYPROJECT,
    "db/models.py": MODELS_BASE,
    "api/charges.py": CHARGES_BASE,
    "tests/test_basic.py": TEST_BASIC,
}

FIRST_EDITS: Mapping[str, str] = {
    "api/charges.py": CHARGES_NEW,
    "db/models.py": MODELS_NEW,
}


@dataclass(frozen=True)
class BriefFixture:
    name: str
    test_file: str | None
    test_source: str | None
    test_id: str | None
    expected: str  # the key result, or "none" when no test is written


BRIEF_FIXTURES: Mapping[str, BriefFixture] = {
    f.name: f
    for f in (
        BriefFixture(
            "tells",
            "tests/test_retry.py",
            TEST_TELLS,
            "tests/test_retry.py::test_retry_returns_first_charge",
            "fails_on_assertion",
        ),
        BriefFixture(
            "passes_anyway",
            "tests/test_retry.py",
            TEST_ANYWAY,
            "tests/test_retry.py::test_retry_returns_an_id",
            "still_passes",
        ),
        BriefFixture("no_test", None, None, None, "none"),
    )
}
