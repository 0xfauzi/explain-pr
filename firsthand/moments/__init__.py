"""The moments the engine can ask. Each module has the same public surface."""

from firsthand.moments import brief, call_it, revert_test

REGISTRY = (revert_test, call_it, brief)
