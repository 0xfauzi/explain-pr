"""Count the documented signatures of unedited LLM prose in a draft.

This is a style meter, not a detector. It cannot tell you who wrote something,
and published work is clear that per-text detection is unreliable and getting
worse. What it does is give a draft a number you can compare against another
draft, and against a sample of your own writing.

Read the number as a direction, not a grade. A count with no human reference is
a change detector: it tells you the prose moved, not that it improved. Pass
--baseline with a file you know a person wrote to get a scale.

Sources, all fixed before any of our own prose was measured:

- Wikipedia, "Signs of AI writing". The era-stratified word lists below are
  taken from it, and the era matters: the 2023 markers have largely washed out.
- Kobak et al., "Delving into LLM-assisted writing in biomedical publications
  through excess vocabulary", Science Advances 2025. Method: excess frequency
  against a pre-LLM counterfactual. Finding used here: 66% of excess style
  words are verbs and 14% adjectives, so the tell is stylistic verbs, not
  subject-matter nouns.
- Liang et al., "Human-LLM Coevolution: Evidence from Academic Writing",
  arXiv 2502.09606. Finding used here: publicised markers decay, because people
  avoid them AND adopt them. Any fixed list has a shelf life, which is why the
  lists here carry their era.
- "The Last Fingerprint: How Markdown Training Shapes LLM Prose",
  arXiv 2603.27006. Finding used here: structural habits from markdown
  training survive explicit instructions to write differently. So the
  structural counters matter more than the lexical ones, because they are the
  part a style prompt does not fix.
- The burstiness literature. Human prose alternates short and long sentences;
  model prose is uniform. Burstiness here is the standard deviation of sentence
  length in words, reported with the coefficient of variation so documents of
  different average length can be compared.
"""

from __future__ import annotations

import argparse
import re
import statistics
from pathlib import Path

# Era matters. A 2023 marker that everybody has since learned to avoid is weak
# evidence today, so the current-era list is scored separately and is the one to
# watch. Source: Wikipedia, "Signs of AI writing".
WORDS_2023 = [
    "delve", "delves", "delving", "tapestry", "testament", "intricate",
    "meticulous", "meticulously", "pivotal", "underscore", "underscores",
    "underscoring", "boasts", "garner", "garnered", "landscape", "vibrant",
    "interplay", "bolstered", "enduring", "realm", "navigating", "multifaceted",
]
WORDS_2024 = [
    "align with", "aligns with", "crucial", "enhance", "enhances", "enhancing",
    "fostering", "foster", "highlighting", "showcasing", "showcase", "seamless",
    "leverage", "leveraging", "robust", "comprehensive", "notably", "moreover",
]
#: The current set, and the one that carries the most weight. It is short
#: because the earlier ones washed out as people learned to avoid them.
WORDS_2025 = ["emphasizing", "emphasises", "emphasizes", "enhance", "highlighting", "showcasing"]

#: Copula avoidance: replacing "is" with something that sounds weightier.
COPULA_DODGE = [
    "serves as", "stands as", "functions as", "operates as", "represents a",
    "marks a", "boasts a", "features a", "offers a", "maintains a",
]

#: Significance inflation: telling the reader a thing matters instead of showing it.
INFLATION = [
    "testament to", "plays a crucial role", "plays a key role", "plays a vital role",
    "underscores the importance", "highlights the importance", "a turning point",
    "evolving landscape", "indelible mark", "deeply rooted", "at the forefront",
    "paving the way", "setting the stage", "in the realm of", "it is important to note",
    "it is worth noting", "when it comes to", "in today's", "ever-evolving",
]

#: Negative parallelism, the "not just X, it's Y" move. Named across every source
#: as the single most reliable current tell, because it survived the vocabulary
#: washout: it is a shape, not a word.
NEGATIVE_PARALLELISM = re.compile(
    r"\b(?:it'?s|its|this is|that'?s|they'?re|we'?re|is)\s+not\s+(?:just|only|merely|simply)\b"
    r"|\bnot\s+(?:just|only|merely|simply)\s+[^.;:!?]{2,60}?,\s*(?:it'?s|but|they'?re)\b"
    r"|\bnot\s+[^.;:!?]{2,40}?,\s*but\s+(?:rather\s+)?\b",
    re.I,
)

#: Participial tails that assert significance without evidence. Source: Wikipedia,
#: "superficial analysis" patterns. Matched only when they follow a comma, which
#: is the construction, rather than the ordinary verb.
PARTICIPIAL_TAIL = re.compile(
    r",\s+(?:highlighting|underscoring|emphasizing|emphasising|reflecting|"
    r"symbolizing|symbolising|showcasing|demonstrating|illustrating|"
    r"contributing to|fostering|cultivating|encompassing|enhancing|ensuring|"
    r"allowing|enabling|making it|solidifying|cementing)\b",
    re.I,
)

#: The tricolon. Three items where two would do, or four would be honest.
TRICOLON = re.compile(r"\b\w+(?:\s+\w+){0,2},\s+\w+(?:\s+\w+){0,2},\s+and\s+\w+(?:\s+\w+){0,2}\b")

#: Markdown leaking into prose. The fingerprint paper's finding is that these
#: survive a style instruction, so they are the honest test of whether a style
#: changed anything structural.
EM_DASH = re.compile("[\u2013\u2014]")
BOLD_RUN = re.compile(r"\*\*[^*\n]+\*\*")
HEADING = re.compile(r"^#{1,6}\s", re.M)
BULLET = re.compile(r"^\s*[-*+]\s+\S", re.M)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"'])")


def strip_markup(text: str) -> str:
    """Prose only. Code, fences and inline spans answer to other constraints."""
    text = re.sub(r"\A---\n.*?\n---\n", " ", text, flags=re.S)
    text = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"^(?: {4}|\t).*$", " ", text, flags=re.M)
    text = re.sub(r"`[^`]+`", " CODE ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def sentences(prose: str) -> list[str]:
    out = []
    for block in re.split(r"\n\s*\n", prose):
        block = re.sub(r"\s+", " ", block).strip()
        if len(block.split()) < 3:
            continue
        out.extend(s.strip() for s in SENTENCE_SPLIT.split(block) if s.strip())
    return out


def phrase_hits(prose: str, phrases: list[str]) -> list[str]:
    found = []
    low = prose.lower()
    for phrase in phrases:
        pattern = rf"\b{re.escape(phrase.lower())}\b"
        found.extend([phrase] * len(re.findall(pattern, low)))
    return found


def measure(path: Path) -> dict[str, float | int | list[str]]:
    raw = path.read_text(encoding="utf-8")
    prose = strip_markup(raw)
    sents = sentences(prose)
    lengths = [len(s.split()) for s in sents]
    words = sum(lengths) or 1

    def per_k(n: int) -> float:
        return round(1000 * n / words, 1)

    hits_2023 = phrase_hits(prose, WORDS_2023)
    hits_2024 = phrase_hits(prose, WORDS_2024)
    hits_2025 = phrase_hits(prose, WORDS_2025)
    copula = phrase_hits(prose, COPULA_DODGE)
    inflation = phrase_hits(prose, INFLATION)
    negpar = NEGATIVE_PARALLELISM.findall(prose)
    tails = PARTICIPIAL_TAIL.findall(prose)
    tricolon = TRICOLON.findall(prose)

    mean = statistics.mean(lengths) if lengths else 0.0
    stdev = statistics.stdev(lengths) if len(lengths) > 1 else 0.0

    return {
        "words": words,
        "sentences": len(sents),
        "mean_len": round(mean, 1),
        "burstiness": round(stdev, 1),
        "cv": round(stdev / mean, 3) if mean else 0.0,
        "longest": max(lengths) if lengths else 0,
        "lex_2023": per_k(len(hits_2023)),
        "lex_2024": per_k(len(hits_2024)),
        "lex_2025": per_k(len(hits_2025)),
        "copula": per_k(len(copula)),
        "inflation": per_k(len(inflation)),
        "neg_parallel": per_k(len(negpar)),
        "participial": per_k(len(tails)),
        "tricolon": per_k(len(tricolon)),
        "em_dash": per_k(len(EM_DASH.findall(raw))),
        "bold": per_k(len(BOLD_RUN.findall(raw))),
        "heading": per_k(len(HEADING.findall(raw))),
        "bullet": per_k(len(BULLET.findall(raw))),
        "_examples": sorted(set(hits_2023 + hits_2024 + hits_2025 + copula + inflation))[:12],
    }


LEXICAL = ("lex_2023", "lex_2024", "lex_2025", "copula", "inflation")
RHETORICAL = ("neg_parallel", "participial", "tricolon")
STRUCTURAL = ("em_dash", "bold", "heading", "bullet")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--detail", action="store_true", help="print the words that matched")
    args = ap.parse_args()

    rows = [(Path(f).name, measure(Path(f))) for f in args.files]

    print(f"\n{'file':28s} {'words':>6s} {'sent':>5s} {'mean':>5s} {'burst':>6s} {'cv':>5s} {'max':>4s}")
    print("-" * 64)
    for name, m in rows:
        print(f"{name:28s} {m['words']:>6} {m['sentences']:>5} {m['mean_len']:>5} "
              f"{m['burstiness']:>6} {m['cv']:>5} {m['longest']:>4}")

    for title, keys in (("lexical", LEXICAL), ("rhetorical", RHETORICAL), ("structural", STRUCTURAL)):
        print(f"\n{title} tells, per 1000 words")
        print(f"{'file':28s} " + " ".join(f"{k:>13s}" for k in keys))
        print("-" * (29 + 14 * len(keys)))
        for name, m in rows:
            print(f"{name:28s} " + " ".join(f"{m[k]:>13}" for k in keys))

    if args.detail:
        print("\nmatched terms")
        for name, m in rows:
            print(f"  {name}: {', '.join(str(x) for x in m['_examples']) or 'none'}")

    print("\nBurstiness is the standard deviation of sentence length in words.")
    print("Model prose is uniform; human prose alternates short and long.")
    print("Higher is more human-like. Read every number against a human sample.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
