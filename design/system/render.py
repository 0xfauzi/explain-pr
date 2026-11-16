"""Render every component preview to PNG, in both themes and at two widths.

Usage: python3 design/system/render.py [OUT_DIR]

Compiles tokens.json to CSS, injects it with components/bundle.css into each
components/<Name>/preview.html, and screenshots the result with Playwright.
The images are the visual reference for anything built on this system.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent


def tokens_css(tokens: dict) -> str:
    def block(theme: str) -> str:
        return "".join(
            f"--{c['name']}:{c['value'][theme]};" for c in tokens["color"]["tokens"]
        )

    rest = "".join(
        f"--{x['name']}:{x['value']};"
        for family in ("spacing", "radius", "duration", "easing")
        for x in tokens[family]["tokens"]
    )
    fonts = "".join(f"--font-{k}:{v};" for k, v in tokens["type"]["families"].items())
    return (
        f":root,[data-theme=light]{{{block('light')}}}"
        f"[data-theme=dark]{{{block('dark')}}}:root{{{rest}{fonts}}}"
    )


def main() -> int:
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "render").resolve()
    out.mkdir(parents=True, exist_ok=True)
    tokens = json.loads((HERE / "tokens.json").read_text())
    css = tokens_css(tokens) + (HERE / "components" / "bundle.css").read_text()
    names = sorted(p.parent.name for p in HERE.glob("components/*/preview.html"))
    for name in names:
        html = (HERE / "components" / name / "preview.html").read_text()
        for theme in ("light", "dark"):
            page = html.replace("<html>", f'<html data-theme="{theme}">')
            page = page.replace("<head>", f"<head><style>{css}</style>")
            (out / f"{name}-{theme}.html").write_text(page)
    done = subprocess.run(
        ["node", str(HERE / "render-shots.cjs"), str(out), json.dumps(names)],
        check=False,
    )
    return done.returncode


if __name__ == "__main__":
    sys.exit(main())
