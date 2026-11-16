"""The Room page loads nothing from outside but its own fonts, builds no markup from
text, and keeps the design tokens identical to the design system's."""

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

import support

import firsthand.room

ROOM = Path(firsthand.room.__file__).resolve().parent
REPO = ROOM.parent.parent
TOKENS_SOURCE = REPO / "design" / "system" / "tokens.css"
REMOTE = re.compile(r"(?i)(https?:)?//[a-z0-9.-]+\.[a-z]{2,}|\burl\(")
SVG_NS = "'http://www.w3.org/2000/svg'"
FONT_FACE = re.compile(
    r"^@font-face\{font-family:[A-Za-z ]+;font-style:(normal|italic);"
    r"font-weight:[0-9 ]+;font-display:swap;"
    r'src:url\(fonts/[a-z0-9-]+\.woff2\) format\("woff2"\)\}$'
)


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
        self.js = "\n".join(
            (ROOM / "static" / name).read_text(encoding="utf-8")
            for name in ("room.js", "room-views.js")
        )
        self.parsed = PageParser()
        self.parsed.feed(self.page)

    def test_page_references_only_static_urls(self) -> None:
        assets = [u for u in self.parsed.urls if u.startswith("/static/")]
        self.assertEqual(
            sorted(assets),
            [
                "/static/icon.svg",
                "/static/room-views.js",
                "/static/room.css",
                "/static/room.js",
            ],
        )
        for url in self.parsed.urls:
            self.assertTrue(url.startswith("/") and not url.startswith("//"), url)
        self.assertIsNone(REMOTE.search(self.page))

    def test_page_has_no_inline_script_or_style(self) -> None:
        self.assertEqual(self.parsed.inline_scripts, 0)
        self.assertEqual(self.parsed.styles, 0)
        self.assertEqual(self.parsed.style_attrs, 0)
        self.assertEqual(self.parsed.handlers, 0)

    def test_page_shell(self) -> None:
        for needed in (
            "main",
            "live",
            "notice",
            "quiet",
            "proj",
            "folio",
            "tabs",
            "count",
            "asked",
        ):
            self.assertIn(needed, self.parsed.ids)
        self.assertEqual(self.parsed.live_regions, 1)
        self.assertIn('aria-live="polite"', self.page)
        self.assertIn("Served by this computer at 127.0.0.1.", self.parsed.text)
        for label in ("The Room", "Inbox", "Journal", "Skills", "Settings"):
            self.assertIn(label, self.parsed.text)
        self.assertIn("<title>Firsthand</title>", self.page)
        self.assertIn('<link rel="icon" id="icon" href="/static/icon.svg"', self.page)
        self.assertIn('class="fh-wordmark"', self.page)
        self.assertIn('<body class="fh">', self.page)

    def test_page_and_script_write_no_style(self) -> None:
        self.assertNotIn("style=", self.page)
        self.assertNotIn("setAttribute('style'", self.js)
        self.assertNotIn('setAttribute("style"', self.js)
        self.assertNotIn(".style.cssText", self.js)

    def test_css_and_js_hold_no_remote_url(self) -> None:
        faces = [line for line in self.css.splitlines() if "@font-face" in line]
        self.assertEqual(len(faces), 9)
        for line in faces:
            self.assertRegex(line, FONT_FACE)
            name = re.search(r"url\((fonts/[^)]+)\)", line)[1]  # type: ignore[index]
            self.assertTrue((ROOM / "static" / name).is_file(), name)
        rest = "\n".join(
            line for line in self.css.splitlines() if "@font-face" not in line
        )
        self.assertIsNone(REMOTE.search(rest))
        # The one URL in the script is the SVG namespace the verdict marks are made
        # in: a name, never fetched.
        self.assertEqual(self.js.count(SVG_NS), 1)
        self.assertIsNone(REMOTE.search(self.js.replace(SVG_NS, "")))
        self.assertNotIn("@import", self.css)

    def test_token_block_equals_the_design_system(self) -> None:
        source = TOKENS_SOURCE.read_text(encoding="utf-8")
        start = self.css.index("/* Firsthand tokens.")
        self.assertEqual(self.css[start : start + len(source)], source)

    def test_component_rules_are_present(self) -> None:
        for selector in (
            ".fh-folio{",
            ".fh-tabs{",
            ".fh-sheet{",
            ".fh-q{",
            ".fh-picks{",
            ".fh-pick{",
            ".fh-held{",
            ".fh-spread{",
            ".fh-answer{",
            ".fh-facts{",
            ".fh-finding{",
            ".fh-m{",
            ".fh-verdict{",
            ".fh-ledger{",
            ".fh-row{",
            ".fh-track{",
            ".fh-more{",
            ".fh-notice{",
            ".fh-confirm{",
            ".fh-err{",
            ".fh-input{",
            ".fh-seg{",
            ".fh-check{",
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
            "Firsthand asks, runs and records nothing.",
            "No questions. Runs still post notes.",
            "Questions within the daily limit.",
            "The same as Standard. Some questions also ask for a line of code.",
            "Show the result",
            "How sure?",
            "This result looks wrong",
            "Say what looks wrong",
            "Open the commands",
            "Back to the Inbox",
            "What would have shown it",
            "Wrong start",
            "Send findings to my agent",
            "A local git repo of plain files. No remote.",
            "Lock",
            "Send to my agent",
            "Recheck",
            "Turn on any number of tests, then Lock.",
            (
                "Tap one part of the picture. A tap locks your answer. You can undo "
                "it before the result."
            ),
            "Firsthand had an error. It changed nothing.",
            "Open Settings",
        ):
            self.assertIn(line, self.js)

    def test_no_em_dash_or_letter_shortcut(self) -> None:
        for text in (self.page, self.css, self.js):
            self.assertNotIn(chr(0x2014), text)
        self.assertNotIn("keydown", self.js)
        self.assertNotIn("keypress", self.js)


if __name__ == "__main__":
    unittest.main()
