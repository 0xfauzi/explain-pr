"""firsthand.runner.generic_adapter: items per test file, argv, exit code classes."""

from __future__ import annotations

import support

from firsthand.model import FileChange
from firsthand.runner import generic_adapter as ga


class GenericAdapterTest(support.TempHome):
    def test_items_per_file(self) -> None:
        changes = [
            FileChange("src/app.js", "M"),
            FileChange("tests/a.spec.js", "A"),
            FileChange("tests/b.spec.js", "M"),
            FileChange("tests/gone.spec.js", "D"),
            FileChange("tests/c.js", "A"),
            FileChange("tests/d.js", "A"),
            FileChange("tests/e.js", "A"),
        ]
        items = ga.test_files(changes)
        self.assertEqual(
            [i.id for i in items],
            ["tests/a.spec.js", "tests/b.spec.js", "tests/c.js", "tests/d.js"],
        )
        first = items[0]
        self.assertEqual(
            (first.n, first.name, first.path, first.line, first.status),
            (1, "a.spec.js", "tests/a.spec.js", 1, "new"),
        )
        self.assertEqual(items[1].status, "edited")
        self.assertEqual(
            (first.assert_lines, first.assert_line, first.assert_text), ((), None, None)
        )

    def test_argv(self) -> None:
        self.assertEqual(
            ga.argv("npm test --", "tests/a.js"), ["npm", "test", "--", "tests/a.js"]
        )
        self.assertEqual(ga.argv("go test './x y'", "t"), ["go", "test", "./x y", "t"])

    def test_classify(self) -> None:
        self.assertEqual(ga.classify(0), "still_passes")
        for code in (1, 2, 127, None):
            self.assertEqual(ga.classify(code), "does_not_pass")
