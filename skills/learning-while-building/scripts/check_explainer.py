#!/usr/bin/env python3
"""Check an explainer page before the learner sees it.

Usage:
  python3 check_explainer.py PAGE.html [--shots DIR] [--no-browser]
  python3 check_explainer.py PAGE.html --extract-rules OUT.cjs

Static checks (always run, standard library only):
  - nothing is loaded from the network: no http(s) src/href, no @import, no fetch
  - body carries data-topic
  - every interaction has a unique data-id, a question, and a hidden answer
  - every prediction's data-answer names one of its options
  - every simulation names a rule defined in <script id="ex-rules">
  - the runtime block is present and unchanged in shape
  - no EXAMPLE or TODO markers are left from the template
  - every inline script parses (needs node; skipped with a note otherwise)

Then, unless --no-browser, it runs check_explainer_browser.mjs, which drives the
page in headless Chromium and saves screenshots to --shots (default: a folder
next to the page named <page>-shots). Look at the screenshots: the checks find
broken behaviour, not a confusing page.

--extract-rules writes the ex-rules script as a CommonJS module so a rule can be
swept in node, outside the browser:

  node -e "const R=require('./rules.cjs'); for (let v=0; v<=2000; v+=100) console.log(v, R.charges({latency:v,key:false}).text)"

Exit 0 when clean, 1 with each problem listed.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
INTERACTIONS = ("ex-predict", "ex-explain", "ex-order")
EXTERNAL = re.compile(r"^(https?:)?//", re.IGNORECASE)
NETWORK_JS = re.compile(
    r"\bfetch\s*\(|XMLHttpRequest|\bimport\s*\(|@import|WebSocket", re.IGNORECASE
)
LEFTOVER = re.compile(r"\bEXAMPLE\b|\bTODO\b")


class Page(HTMLParser):
    """Collect the elements and scripts the checks need, with their classes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict] = []
        self.elements: list[dict] = []
        self.scripts: list[dict] = []
        self.body: dict = {}
        self._script: dict | None = None
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = {k: (v or "") for k, v in attrs}
        el = {
            "tag": tag,
            "attrs": a,
            "classes": a.get("class", "").split(),
            "parents": [p["id"] for p in self.stack],
            "id": len(self.elements),
            "line": self.getpos()[0],
        }
        self.elements.append(el)
        if tag == "body":
            self.body = a
        if tag == "script":
            self._script = {"attrs": a, "text": "", "line": el["line"]}
        if tag not in (
            "meta",
            "link",
            "input",
            "br",
            "img",
            "hr",
            "path",
            "rect",
            "circle",
            "line",
        ):
            self.stack.append(el)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script is not None:
            self.scripts.append(self._script)
            self._script = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._script["text"] += data
        else:
            self.text_parts.append(data)

    def inside(
        self, root: dict, cls: str | None = None, tag: str | None = None
    ) -> list[dict]:
        return [
            e
            for e in self.elements
            if root["id"] in e["parents"]
            and (cls is None or cls in e["classes"])
            and (tag is None or e["tag"] == tag)
        ]

    def with_class(self, cls: str) -> list[dict]:
        return [e for e in self.elements if cls in e["classes"]]


def check_network(page: Page) -> list[str]:
    problems = []
    for el in page.elements:
        for attr in ("src", "href"):
            if EXTERNAL.match(el["attrs"].get(attr, "")):
                problems.append(
                    f"line {el['line']}: <{el['tag']} {attr}> loads from the network"
                )
    for script in page.scripts:
        if script["attrs"].get("src"):
            problems.append(
                f"line {script['line']}: external script {script['attrs']['src']}"
            )
        if NETWORK_JS.search(script["text"]):
            problems.append(
                f"line {script['line']}: script uses fetch, import(), XMLHttpRequest or WebSocket"
            )
    return problems


def check_interaction(page: Page, el: dict, seen: set[str]) -> list[str]:
    where = f"line {el['line']}"
    problems = []
    ident = el["attrs"].get("data-id")
    if not ident:
        problems.append(f"{where}: {el['classes'][0]} has no data-id")
    elif ident in seen:
        problems.append(f"{where}: data-id {ident!r} is used twice")
    seen.add(ident or "")
    if not page.inside(el, "ex-q"):
        problems.append(f"{where}: no .ex-q question")
    reveals = page.inside(el, "ex-reveal")
    if not reveals:
        problems.append(f"{where}: no .ex-reveal answer")
    elif "hidden" not in reveals[0]["attrs"]:
        problems.append(
            f"{where}: .ex-reveal lacks the hidden attribute, so the answer shows on load"
        )
    return problems


def check_predict(page: Page, el: dict) -> list[str]:
    where = f"line {el['line']} ({el['attrs'].get('data-id', '?')})"
    values = [
        li["attrs"].get("data-value")
        for li in page.inside(el, tag="li")
        if "data-value" in li["attrs"]
    ]
    if len(values) < 2:
        return [f"{where}: a prediction needs at least two options with data-value"]
    if el["attrs"].get("data-answer") not in values:
        return [
            f"{where}: data-answer {el['attrs'].get('data-answer')!r} is not one of {values}"
        ]
    return []


def check_order(page: Page, el: dict) -> list[str]:
    items = [
        li
        for li in page.inside(el, tag="li")
        if any("ex-items" in page.elements[p]["classes"] for p in li["parents"])
    ]
    if len(items) < 3:
        return [f"line {el['line']}: an ordering task needs at least three steps"]
    return []


def rules_source(page: Page) -> str:
    for script in page.scripts:
        if script["attrs"].get("id") == "ex-rules":
            return script["text"]
    return ""


def check_sims(page: Page) -> list[str]:
    problems = []
    source = rules_source(page)
    for el in page.with_class("ex-sim"):
        rule = el["attrs"].get("data-rule", "")
        if not rule:
            problems.append(f"line {el['line']}: ex-sim has no data-rule")
        elif not re.search(rf"\b{re.escape(rule)}\s*[(:]", source):
            problems.append(
                f'line {el["line"]}: rule {rule!r} is not defined in <script id="ex-rules">'
            )
        if not [e for e in page.inside(el) if "data-param" in e["attrs"]]:
            problems.append(f"line {el['line']}: ex-sim has no [data-param] control")
        if not page.inside(el, "ex-predict"):
            problems.append(
                f"line {el['line']}: ex-sim has no prediction inside it, so the learner can play "
                "without committing to an answer first"
            )
    if source and re.search(r"\bdocument\b|\bwindow\b", source):
        problems.append(
            "ex-rules touches document or window; keep rules pure so they can be swept in node"
        )
    return problems


def check_structure(page: Page) -> list[str]:
    problems = []
    if not page.body.get("data-topic"):
        problems.append(
            "<body> has no data-topic; results cannot be imported without it"
        )
    if not any(s["attrs"].get("id") == "ex-runtime" for s in page.scripts):
        problems.append(
            'no <script id="ex-runtime">; copy it unchanged from assets/explainer-template.html'
        )
    seen: set[str] = set()
    for cls in INTERACTIONS:
        for el in page.with_class(cls):
            problems += check_interaction(page, el, seen)
    for el in page.with_class("ex-predict"):
        problems += check_predict(page, el)
    for el in page.with_class("ex-order"):
        problems += check_order(page, el)
    if not seen - {""}:
        problems.append(
            "no interaction at all; a page the learner only reads belongs in the chat, not here"
        )
    return problems


def check_leftovers(raw: str) -> list[str]:
    problems = []
    for number, line in enumerate(raw.splitlines(), 1):
        if LEFTOVER.search(line):
            problems.append(
                f"line {number}: template marker left in: {line.strip()[:70]}"
            )
    return problems


def check_scripts_parse(page: Page) -> tuple[list[str], list[str]]:
    node = shutil.which("node")
    if not node:
        return [], ["node not found, so inline scripts were not parse-checked"]
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, script in enumerate(page.scripts):
            path = Path(tmp) / f"script{i}.js"
            path.write_text(script["text"], encoding="utf-8")
            done = subprocess.run(
                [node, "--check", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if done.returncode:
                errs = done.stderr.strip().splitlines()
                first = next(
                    (ln for ln in errs if "Error" in ln), errs[0] if errs else "?"
                )
                problems.append(
                    f"script at line {script['line']} does not parse: {first}"
                )
    return problems, []


def run_browser(page_path: Path, shots: Path) -> tuple[list[str], list[str]]:
    node = shutil.which("node")
    if not node:
        return [], ["node not found, so the page was not run in a browser"]
    done = subprocess.run(
        [node, str(HERE / "check_explainer_browser.mjs"), str(page_path), str(shots)],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = done.stdout.strip().splitlines()
    if done.returncode == 2:
        return [], lines
    problems = [ln[len("PROBLEM: ") :] for ln in lines if ln.startswith("PROBLEM: ")]
    notes = [
        ln.removeprefix("NOTE: ")
        for ln in lines
        if not ln.startswith(("PROBLEM: ", "OK:", "FAILED:"))
    ]
    if done.returncode not in (0, 1):
        problems.append(
            "browser check crashed: " + (done.stderr.strip().splitlines() or ["?"])[-1]
        )
    return problems, notes


def extract_rules(page: Page, out: Path) -> None:
    source = rules_source(page)
    if not source:
        sys.exit('ERROR: no <script id="ex-rules"> in this page.')
    out.write_text(source + "\nmodule.exports = RULES;\n", encoding="utf-8")
    print(
        f"Wrote {out}. Sweep a rule with node -e \"const R=require('{out.resolve()}'); ...\""
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("page", type=Path)
    parser.add_argument(
        "--shots", type=Path, help="screenshot folder (default <page>-shots/)"
    )
    parser.add_argument("--no-browser", action="store_true", help="static checks only")
    parser.add_argument("--extract-rules", type=Path, metavar="OUT.cjs")
    args = parser.parse_args()
    if not args.page.exists():
        sys.exit(f"ERROR: {args.page} does not exist.")
    raw = args.page.read_text(encoding="utf-8")
    page = Page()
    page.feed(raw)
    if args.extract_rules:
        extract_rules(page, args.extract_rules)
        return
    problems = (
        check_network(page)
        + check_structure(page)
        + check_sims(page)
        + check_leftovers(raw)
    )
    parse_problems, notes = check_scripts_parse(page)
    problems += parse_problems
    if not args.no_browser and not problems:
        shots = args.shots or args.page.with_name(args.page.stem + "-shots")
        browser_problems, browser_notes = run_browser(args.page, shots)
        problems += browser_problems
        notes += browser_notes
    elif problems and not args.no_browser:
        notes.append("browser check not run: fix the static problems first")
    print(f"{args.page}: {len(raw.encode()) // 1024} KB")
    for note in notes:
        print(f"NOTE: {note}")
    for problem in problems:
        print(f"PROBLEM: {problem}")
    print("FAILED" if problems else "OK")
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
