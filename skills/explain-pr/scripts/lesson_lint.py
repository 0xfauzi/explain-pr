"""Check a lesson against the writing rules it ships under, and parse its widgets.

Style guidance in a procedure file decays, because nothing reads it. This reads
it. Every limit here has a source, named beside it, so the numbers can be argued
with rather than guessed at.

Two things are judged, because a lesson is made of two things. The prose answers
to ASD-STE100 and to the glossary. The widgets answer to whether they run at all:
a script that cannot parse leaves a blank panel under prose that still invites
the reader to try it. That is worse than no widget, so it is a hard finding.

What it does NOT judge: generated output. A figure emitted by a generator carries
`data-generated`, and its labels were written under different constraints.
Rewriting them to satisfy a prose rule would put the picture out of step with the
thing that generates it.

Nor does it judge whether a widget teaches the truth. Nothing can. Two false
teachings caught while writing one lesson parsed cleanly and read well: one had a
threshold its slider could not reach, and one promised an effect its own data did
not produce. `references/widgets.md` carries that rule, because only a person can
apply it.

Two checks report more than they should, and neither is worth tightening. The
passive detector matches "is complete". The alias check reads no context, so it
flags a banned word used in another sense. Both name what they matched, so a
reader can judge in one glance. Reword the prose. Do not loosen the rule to make
a false positive go away: the rule is the only thing here that does not rot.

Usage:
  python lesson_lint.py <lesson.html> [--glossary FILE] [--quiet]
"""

from __future__ import annotations

import argparse
import re
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path

# ASD-STE100 caps a procedural sentence at 20 words and a descriptive one at 25,
# and both numbers are REPORTED here rather than enforced. Measured on two
# explanations of one pull request, differing only in whether the teaching style
# was active, a hard 20-word cap left mean sentence length untouched at 26 words
# and cut the longest from 114 to 64. All it removed was the long tail, and the
# long tail is what carries the variation that human prose has. A separate
# comprehension test on the same two documents found no gain to show for it.
#
# So the cap is a reference line, not a gate. What to steer is the spread, which
# is what `rhythm` below reports. `ai_tells.py` explains the measurement.
SENTENCE_REFERENCE_WORDS = 20
PARAGRAPH_REFERENCE_SENTENCES = 6

#: Interquartile range of 18 specifications and standards published before
#: ChatGPT, so the label is a date rather than a judgement. Machine-written
#: prose in the same register sits near 0.49. Essays are a different matter:
#: good essayists write evenly, and the human essay median is 0.63, so this
#: band does not apply to them.
HUMAN_RHYTHM_BAND = (0.729, 0.827)

BLOCK_END = re.compile(
    r"</(p|li|h[1-6]|figcaption|td|th|blockquote|dd|dt|summary)\s*>|<br\s*/?>",
    re.I,
)
# A crude passive detector: a form of "be" followed by a participle. It over-
# reports ("is complete"), so it is advisory and always prints the match.
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+"
    r"(?:\w+ed|written|drawn|taken|given|shown|made|built|held|read|kept|left|"
    r"seen|known|done|sent|set|put|found|thrown|caught|bound|split|cast|meant)\b",
    re.I,
)
# Spelled as escapes on purpose: a literal dash here would be the very character
# the rule forbids, and this file would fail its own check.
BANNED_CHARS = re.compile("[\u2013\u2014]|[\U0001f300-\U0001faff\u2600-\u27bf]")


def strip_generated(html: str) -> str:
    """Drop script, style, svg, and anything marked data-generated."""
    for tag in ("script", "style", "svg"):
        html = re.sub(rf"<{tag}\b.*?</{tag}>", " ", html, flags=re.S | re.I)
    while True:
        m = re.search(r"<(\w+)[^>]*\bdata-generated\b", html, re.I)
        if not m:
            return html
        close = f"</{m.group(1)}>"
        end = html.find(close, m.end())
        if end == -1:
            return html[: m.start()]
        html = html[: m.start()] + " " + html[end + len(close) :]


def blocks(html: str) -> list[str]:
    """Authored text, one string per block-level element."""
    # A code span is one term, not a sentence boundary and not many words.
    html = re.sub(r"<code\b[^>]*>.*?</code>", " CODE ", html, flags=re.S | re.I)
    html = BLOCK_END.sub("\x00", html)
    out = []
    for chunk in html.split("\x00"):
        text = re.sub(r"<[^>]+>", " ", chunk)
        text = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text.split()) >= 3:
            out.append(text)
    return out


def markdown_blocks(text: str) -> list[str]:
    """Same job as blocks(), for the procedure files that carry these rules.

    A checker that judged only lessons would let the document stating the rule
    break it. One list item is one block: a bullet list is not one long sentence.

    YAML frontmatter is dropped. A skill description is metadata that a matcher
    reads to decide whether to load the file, so it is written for retrieval and
    is deliberately dense. Judging it as prose fails every skill ever written.
    """
    text = re.sub(r"\A---\n.*?\n---\n", " ", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^(?: {4}|\t).*$", " ", text, flags=re.M)
    text = re.sub(r"`[^`]+`", " CODE ", text)
    text = re.sub(r"^#+ .*$", " ", text, flags=re.M)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    out = []
    for para in re.split(r"\n\s*\n", text):
        for item in re.split(r"\n(?=\s*(?:[-*+]|\d+\.)\s)", para):
            item = re.sub(r"^\s*(?:[-*+]|\d+\.)\s*", "", item)
            item = re.sub(r"[*_]{1,2}", "", item)
            item = re.sub(r"\s+", " ", item).strip()
            if len(item.split()) >= 3:
                out.append(item)
    return out


def sentences(block: str) -> list[str]:
    """Split on terminal punctuation followed by a space. Decimals survive."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", block)
    return [p.strip() for p in parts if p.strip()]


def interactive_figures(html: str) -> int:
    """Authored figures that DECLARE a control the reader can operate.

    Counted, never capped. How many a lesson needs depends on how many decisions
    the change made, and that is not a number this file can know.

    It undercounts on purpose. A figure whose buttons are built by script is not
    counted, because reading intent out of a script is guesswork. An undercount
    misleads nobody into a pass; an overcount would.
    """
    return sum(
        1
        for fig in re.findall(r"<figure\b.*?</figure>", html, re.S | re.I)
        if "data-generated" not in fig.lower()
        and re.search(r"<(input|button|select)\b", fig, re.I)
    )


def script_syntax(html: str) -> tuple[list[str], str]:
    """Parse errors in inline scripts, plus one word for what was done.

    node's absence is reported rather than passed: an unchecked widget is not a
    working one, and a silent skip reads exactly like a pass.
    """
    sources = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.S | re.I)
    if not sources:
        return [], "none"
    if shutil.which("node") is None:
        return [], "UNCHECKED, no node"
    bad: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for index, source in enumerate(sources):
            path = Path(tmp) / f"block{index}.js"
            path.write_text(source, encoding="utf-8")
            proc = subprocess.run(
                ["node", "--check", str(path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            if proc.returncode != 0:
                line = next((ln for ln in proc.stderr.splitlines() if ln.strip()), "no detail")
                bad.append(f"script {index + 1}: {line.strip()[:110]}")
    if bad:
        return bad, f"{len(bad)} of {len(sources)} WILL NOT RUN"
    return bad, f"{len(sources)} parsed"


def banned_aliases(glossary: Path) -> dict[str, str]:
    """Alias -> the term it must give way to, from the glossary's _Avoid_ lines.

    A missing glossary yields no aliases rather than an error. A repository may
    keep no register, and the writing rules still apply without one.
    """
    if not glossary.is_file():
        return {}
    out: dict[str, str] = {}
    term = ""
    for line in glossary.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\*\*(.+?)\*\*:", line.strip())
        if m:
            term = m.group(1)
            continue
        m = re.match(r"_Avoid_:\s*(.+)", line.strip())
        if m and term:
            for alias in m.group(1).split(","):
                alias = alias.strip().rstrip(".")
                if alias:
                    out[alias.lower()] = term
    return out


# --- the register --------------------------------------------------------------
#
# Prose alone cannot keep a register honest. A lesson file with no entry is
# invisible, an entry naming no file is a dead link, and a `reverses:` pointing
# at nothing quietly loses the fact that a later change overturned an earlier
# lesson. That last one is why this exists: one lesson taught two things that
# sixteen later commits reversed, and nothing in the tree said so.
#
# Only the repository-independent rules live here. Whether a `parts:` value names
# something real, and whether a `rules:` number is in range, depend on what the
# repository defines, so its own checker owns those.


def register_entries(register: Path) -> list[dict[str, str]]:
    """Parse the log's `### ` entries and their field block.

    Fields are `- name: value` lines directly under the heading. Prose starts at
    the first line that is not one, so an entry can say as much as it likes
    without confusing the parser.
    """
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in register.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^###\s+(.*\S)\s*$", line)
        if heading:
            current = {"title": heading.group(1)}
            entries.append(current)
            continue
        if current is None:
            continue
        field = re.match(r"^-\s+([a-z-]+):\s*(.*)$", line.strip())
        if field:
            current[field.group(1)] = field.group(2).strip()
    return entries


def check_register(register: Path) -> list[str]:
    """Every lesson registered, every file real, every reversal resolvable."""
    if not register.is_file():
        return [f"register missing: {register}"]
    problems: list[str] = []
    entries = register_entries(register)
    titles = {e["title"] for e in entries}
    named: set[str] = set()

    for entry in entries:
        title = entry["title"]
        listed = entry.get("file", "")
        if listed and not listed.startswith("("):
            named.add(listed)
            if not (register.parent / listed).is_file():
                problems.append(f"{title}: file {listed!r} does not exist")

        reverses = entry.get("reverses", "")
        if reverses and not reverses.startswith("("):
            for target in (t.strip() for t in reverses.split(",")):
                match = [t for t in titles if t.startswith(target)]
                if not match:
                    problems.append(f"{title}: reverses {target!r}, no such entry")
                    continue
                # A pointer in one direction only is how a stale lesson keeps
                # looking current, so the reversed entry must say it was reversed.
                for other in entries:
                    if other["title"] == match[0] and not other.get("superseded-by"):
                        problems.append(
                            f"{match[0]}: reversed by {title!r} and carries no"
                            " superseded-by field"
                        )

        # A superseded lesson says so on its own face. Somebody opening it from a
        # link in a PR never sees this register, and a file that looks current is
        # exactly how a reader learns a withdrawn claim.
        superseded = entry.get("superseded-by", "")
        body = register.parent / listed if listed and not listed.startswith("(") else None
        if (
            superseded
            and not superseded.startswith("(")
            and body is not None
            and body.is_file()
            and "superseded" not in body.read_text(encoding="utf-8").lower()
        ):
            problems.append(
                f"{title}: superseded by {superseded!r} and its body carries no"
                " banner saying so"
            )

    for lesson in sorted(register.parent.glob("*.html")):
        if lesson.name not in named:
            problems.append(f"{lesson.name} is not named by any register entry")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("lesson", nargs="?")
    ap.add_argument(
        "--glossary",
        default="",
        help="a register file whose _Avoid_ lines name banned aliases; optional",
    )
    ap.add_argument(
        "--register",
        default="",
        help="check this register against the lesson files beside it",
    )
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.register:
        problems = check_register(Path(args.register))
        for problem in problems:
            print(f"REGISTER: {problem}")
        if not args.quiet:
            print(f"RESULT: {'FAIL' if problems else 'PASS'} ({len(problems)} findings)")
        return 1 if problems else 0

    if args.lesson is None:
        ap.error("a lesson path is required unless --register is given")

    path = Path(args.lesson)
    html = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".md", ".markdown"):
        bl = markdown_blocks(html)
    else:
        bl = blocks(strip_generated(html))
    all_sents = [s for b in bl for s in sentences(b)]
    words = sum(len(s.split()) for s in all_sents)

    long_sents = [s for s in all_sents if len(s.split()) > SENTENCE_REFERENCE_WORDS]
    fat_blocks = [b for b in bl if len(sentences(b)) > PARAGRAPH_REFERENCE_SENTENCES]
    aliases = banned_aliases(Path(args.glossary)) if args.glossary else {}
    prose = " ".join(all_sents).lower()
    used_aliases = {a: t for a, t in aliases.items() if re.search(rf"\b{re.escape(a)}\b", prose)}
    chars = BANNED_CHARS.findall(html)
    passives = [m.group(0) for s in all_sents for m in PASSIVE.finditer(s)]
    broken, js_state = script_syntax(html)
    widgets = interactive_figures(html)

    print(f"{args.lesson}")
    print(f"  authored prose   : {words} words, {len(all_sents)} sentences")
    if all_sents:
        lengths = [len(s.split()) for s in all_sents]
        longest = max(lengths)
        print(f"  longest sentence : {longest} words")
        # Reported, never failed. Uniform sentence length is a documented
        # signature of generated prose, and the sentence cap above works by
        # clipping the long tail, which is what produces the variation. The two
        # rules pull against each other, so both numbers are printed and the
        # writer decides. `ai_tells.py` explains the measurement.
        if len(lengths) > 1:
            mean = statistics.mean(lengths)
            cv = statistics.stdev(lengths) / mean if mean else 0.0
            low, high = HUMAN_RHYTHM_BAND
            flag = "" if cv >= low else "  <- flat; vary sentence length"
            print(
                f"  rhythm           : cv {cv:.2f} "
                f"(human prose sits near {low} to {high}){flag}"
            )
    print(f"  over {SENTENCE_REFERENCE_WORDS} words     : {len(long_sents)}")
    blocks_over = len(fat_blocks)
    print(f"  blocks over {PARAGRAPH_REFERENCE_SENTENCES}    : {blocks_over}")
    print(f"  banned aliases   : {len(used_aliases)}")
    print(f"  dashes/emoji     : {len(chars)}")
    print(f"  widgets          : {widgets} the reader can operate, scripts {js_state}")
    print(f"  passive (advisory): {len(passives)}")

    if not args.quiet:
        for s in long_sents:
            print(f"    LONG [{len(s.split())}w] {s[:120]}")
        for b in fat_blocks:
            print(f"    BLOCK [{len(sentences(b))} sentences] {b[:110]}")
        for a, t in used_aliases.items():
            print(f'    ALIAS "{a}" -> use "{t}"')
        for b in broken:
            print(f"    BROKEN {b}")
        for p in passives[:12]:
            print(f"    passive? {p}")

    # Hard findings are the unambiguous ones: a banned character, a glossary
    # alias, a widget that will not parse. Sentence and paragraph length are
    # judgement about a distribution, so they are printed and left to the writer.
    failures = len(used_aliases) + len(chars) + len(broken)
    print(f"  RESULT: {'FAIL' if failures else 'PASS'} ({failures} hard findings)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
