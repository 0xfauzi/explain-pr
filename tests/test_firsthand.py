"""Loads tests/firsthand, which is not a package so that it cannot shadow the firsthand package.

The firsthand package needs Python 3.11 or later (it imports tomllib). The repo's
CI also runs the skill's tests on 3.10, so there this loads nothing.
"""

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent / "firsthand"


def load_tests(loader, standard_tests, pattern):
    if importlib.util.find_spec("tomllib") is None:
        return unittest.TestSuite()
    return unittest.TestLoader().discover(
        str(HERE), pattern="test_*.py", top_level_dir=str(HERE)
    )
