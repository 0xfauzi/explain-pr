"""The Room page loads nothing from outside, builds no markup from text, and keeps
the design tokens identical to the design system's."""

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

import support

import firsthand.room

ROOM = Path(firsthand.room.__file__).resolve().parent
REPO = ROOM.parent.parent
TOKENS_SOURCE = REPO / "design" / "learning-experience" / "assets" / "room.css"
REMOTE = re.compile(r"(?i)(https?:)?//[a-z0-9.-]+\.[a-z]{2,}|\burl\(")


def token_block(text: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(":root{"))
    end = next(i for i, line in enumerate(lines) if line.startswith(".lvw"))
    return "\n".join(lines[start : end + 1])


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []
        self.inline_scripts = 0
        self.styles = 0
        self.style_attrs = 0
        self.handlers = 0
        self.in_script = False
        self.ids: list[str] = []
        self.text: list[str] = []
        self.live_regions = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        for key in ("href", "src", "action"):
            if a.get(key):
                self.urls.append(a[key] or "")
        if tag == "style":
            self.styles += 1
        if tag == "script":
            self.in_script = True
            if not a.get("src"):
                self.inline_scripts += 1
        if "style" in a:
            self.style_attrs += 1
        self.handlers += sum(1 for k in a if k.startswith("on"))
        if a.get("id"):
            self.ids.append(a["id"] or "")
        if a.get("aria-live"):
            self.live_regions += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_script = False

    def handle_data(self, data: str) -> None:
        if self.in_script and data.strip():
            self.inline_scripts += 1
        if data.strip():
            self.text.append(data.strip())


class RoomPageTest(support.TempHome):
    def setUp(self) -> None:
        super().setUp()
        self.page = (ROOM / "page.html").read_text(encoding="utf-8")
        self.css = (ROOM / "static" / "room.css").read_text(encoding="utf-8")
        self.js = (ROOM / "static" / "room.js").read_text(encoding="utf-8")
        self.parsed = PageParser()
        self.parsed.feed(self.page)

    def test_page_references_only_static_urls(self) -> None:
        assets = [u for u in self.parsed.urls if u.startswith("/static/")]
        self.assertEqual(sorted(assets), ["/static/room.css", "/static/room.js"])
        for url in self.parsed.urls:
            self.assertTrue(url.startswith("/") and not url.startswith("//"), url)
        self.assertIsNone(REMOTE.search(self.page))

    def test_page_has_no_inline_script_or_style(self) -> None:
        self.assertEqual(self.parsed.inline_scripts, 0)
        self.assertEqual(self.parsed.styles, 0)
        self.assertEqual(self.parsed.style_attrs, 0)
        self.assertEqual(self.parsed.handlers, 0)

    def test_page_shell(self) -> None:
        for needed in ("main", "live", "notice", "quiet", "proj"):
            self.assertIn(needed, self.parsed.ids)
        self.assertEqual(self.parsed.live_regions, 1)
        self.assertIn('aria-live="polite"', self.page)
        self.assertIn("Served by this computer at 127.0.0.1.", self.parsed.text)
        for label in ("Room", "Inbox", "Journal", "Skills", "Settings"):
            self.assertIn(label, self.parsed.text)

    def test_css_and_js_hold_no_remote_url(self) -> None:
        self.assertIsNone(REMOTE.search(self.css))
        self.assertIsNone(REMOTE.search(self.js))
        self.assertNotIn("@import", self.css)
        self.assertNotIn("@font-face", self.css)

    def test_token_block_equals_the_design_system(self) -> None:
        source = TOKENS_SOURCE.read_text(encoding="utf-8")
        self.assertEqual(token_block(self.css), token_block(source))

    def test_component_rules_are_present(self) -> None:
        for selector in (
            ".top{",
            ".bar{",
            ".tabs{",
            ".tab{",
            ".main{",
            ".card{",
            ".eb{",
            ".ctx{",
            ".lead{",
            ".ev{",
            ".q{",
            ".picks{",
            ".pill{",
            ".lock{",
            ".sure{",
            ".foot{",
            ".rh{",
            ".rt{",
            ".chip{",
            ".rw{",
            ".cue{",
            "details.more{",
            ".grp{",
            ".it{",
            "details.note{",
            ".close{",
            ".btn{",
            ".tbtn{",
            "@media (max-width:640px)",
            "@media (prefers-reduced-motion:reduce)",
        ):
            self.assertIn(selector, self.css)

    def test_js_never_builds_markup_from_text(self) -> None:
        self.assertNotIn("innerHTML", self.js)
        self.assertNotIn("outerHTML", self.js)
        self.assertNotIn("insertAdjacentHTML", self.js)
        self.assertNotIn("document.write", self.js)
        self.assertNotIn("eval(", self.js)
        self.assertNotIn("localStorage", self.js)

    def test_js_fixed_copy(self) -> None:
        for line in (
            "This page needs a session. Run: firsthand room",
            "The Room cannot reach Firsthand on this computer. Start it with: firsthand room",
            "Nothing is asked, run or recorded.",
            "No questions. Checks run and post notes.",
            "Questions within the daily limit.",
            "As Standard. You may also write a line of code on some questions.",
            "Show the result",
            "How sure?",
            "This result looks wrong",
            "Open the commands",
            "Back to the build",
            "What would have shown it",
            "Wrong start",
            "Send findings to my agent",
            "A git repo on this computer. Plain files. No remote.",
        ):
            self.assertIn(line, self.js)

    def test_no_em_dash_or_letter_shortcut(self) -> None:
        for text in (self.page, self.css, self.js):
            self.assertNotIn(chr(0x2014), text)
        self.assertNotIn("keydown", self.js)
        self.assertNotIn("keypress", self.js)


if __name__ == "__main__":
    unittest.main()
