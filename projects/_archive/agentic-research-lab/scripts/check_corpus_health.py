#!/usr/bin/env python3
"""Gate: reject corpus chunks whose text lost intra-word whitespace.

PDF-derived chunks are the risk class here — extraction can drop every space
inside a line ("purposeofcopyrightistoencouragewritersandartiststoproducethe
creativeworksthatenrich") without breaking any other check. The damage is
invisible in the graph but makes the FTS index structurally blind to those
terms, which caps every retrieval measurement taken against it.

Checked on the authoritative corpus markdown, not on graph.db, so a rebuild
cannot hide the defect.

## Why the earlier version of this gate was wrong

It reported 6,401 of 10,364 chunks (62%) as damaged. The true figure is 472
chunks (4.6%), and the 13x overcount came from two signals that both fire on
legitimate text:

* **CamelCase run-ons** flagged `basePrice`, `daysOverdrawn`,
  `frequentRenterPoints`. Those are real identifiers from *Refactoring* and
  *Beginning Software Engineering*, not extraction damage.
* **Corpus-absent long tokens** flagged any word used fewer than 6 times in a
  4.5M-word corpus. In a corpus this size, ordinary technical vocabulary is
  legitimately rare, so the rule punished precision rather than recalling it.

## The signal that actually discriminates

An extraction artifact is a long **all-lowercase** token with no camelCase
boundary, no hyphen, and no underscore. That is what lost whitespace looks
like, and no real identifier or English word has that shape at that length:

    "purposeofcopyrightistoencouragewriters"   -> glue
    "basePrice"        -> legitimate camelCase, keep
    "counterfactual"   -> legitimate long word, keep
    "well-known"       -> hyphenated, keep

Requiring ``MIN_GLUE_LEN`` lowercase letters with no other character class
present separates damage from vocabulary without any frequency heuristic, so
the gate behaves identically on a real corpus and on a small test fixture.

Acronyms (``BM25``, ``PDF``) and CamelCase identifiers are explicitly exempt:
both are normal in technical prose and neither indicates lost whitespace.
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "knowledge" / "corpus"

# Longest single-token English word in ordinary technical prose is well under
# this. "antidisestablishmentarianism" (28) is the longest credible contender
# and must not be flagged; real glue runs are collapsed phrases, typically 40+
# characters. 32 leaves a safe margin over legitimate vocabulary.
MIN_GLUE_LEN = 32

# A glue token is a single unbroken run of lowercase letters. The pattern is
# anchored and excludes every other character class, so camelCase, hyphenated,
# underscored, and digit-bearing tokens cannot match.
GLUE_RE = re.compile(rf"\b[a-z]{{{MIN_GLUE_LEN},}}\b")

# A trailing \b requires a non-word character after the run, so a glue run that
# runs straight into a Capitalised word ("...describedintheIntroduction") was
# invisible to GLUE_RE. 71 such cases exist in the live corpus. The lookahead
# adds no new matches - it only lets a run end at a lowercase-to-uppercase
# boundary, which is exactly the shape extraction damage takes.
GLUE_TRAILING_CAPITAL_RE = re.compile(
    rf"\b[a-z]{{{MIN_GLUE_LEN},}}(?=[A-Z])")


def suspicious_runs(text: str, freq: collections.Counter | None = None) -> list[str]:
    """Return run-together word artifacts found in ``text``.

    ``freq`` is accepted for call-site compatibility but unused: the structural
    signal needs no corpus statistics, which is what makes it safe on small
    fixtures as well as the full corpus.
    """
    runs = [m.group(0) for m in GLUE_RE.finditer(text)]
    runs += [m.group(0) for m in GLUE_TRAILING_CAPITAL_RE.finditer(text)]
    return runs


def scan_corpus(corpus_dir: Path = CORPUS_DIR) -> tuple[dict[str, int], int]:
    """Return (per-file artifact counts, total artifact count) for a corpus dir."""
    files = sorted(corpus_dir.glob("*.md")) if corpus_dir.is_dir() else []
    offenders: dict[str, int] = {}
    total = 0
    for path in files:
        count = len(suspicious_runs(path.read_text(encoding="utf-8", errors="replace")))
        if count:
            offenders[path.name] = count
            total += count
    return offenders, total


def scan_by_source(corpus_dir: Path = CORPUS_DIR) -> dict[str, dict[str, int]]:
    """Return per-source damage, as both damaged-chunk and glue-token counts.

    Reporting only one of the two invites a misreading: 1014 glue tokens in
    *Mythical Man-month* is 98 damaged chunks, not 1014. The chunk count is the
    actionable unit for deciding what to repair; the token count explains the
    severity within it. Grouping by source is what turns a 419-chunk count
    into "two books, everything else is fine".
    """
    per_source: dict[str, collections.Counter] = {}
    if not corpus_dir.is_dir():
        return {}
    for path in sorted(corpus_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        count = len(suspicious_runs(text))
        if not count:
            continue
        source = "unknown"
        head = text.split("---", 2)
        if len(head) > 2 and "source:" in head[1]:
            source = head[1].split("source:", 1)[1].splitlines()[0].strip().strip('"')
        bucket = per_source.setdefault(source[:70], collections.Counter())
        bucket["chunks"] += 1
        bucket["tokens"] += count
    return {s: dict(v) for s, v in per_source.items()}


def _totals(by_source: dict[str, dict[str, int]]) -> tuple[int, int]:
    return (sum(v["chunks"] for v in by_source.values()),
            sum(v["tokens"] for v in by_source.values()))


def main() -> int:
    if not CORPUS_DIR.is_dir():
        print("corpus-health: no knowledge/corpus directory; nothing to check")
        return 0

    offenders, total = scan_corpus(CORPUS_DIR)
    total_files = len(list(CORPUS_DIR.glob("*.md")))

    if not offenders:
        print(f"corpus-health: PASS — {total_files} chunks, no intra-word whitespace loss")
        return 0

    by_source = scan_by_source(CORPUS_DIR)
    clean = total_files - len(offenders)
    print(
        f"corpus-health: FAIL — {len(offenders)}/{total_files} chunks "
        f"({100 * len(offenders) / total_files:.1f}%) carry run-together words; "
        f"{clean} chunks ({100 * clean / total_files:.1f}%) are clean"
    )
    print(f"  {total} artifact tokens; FTS5 cannot split these, so retrieval is capped.")
    src_chunks, src_tokens = _totals(by_source)
    print(f"  Damage is concentrated in {len(by_source)} source(s) "
          f"({src_chunks} chunks, {src_tokens} tokens):")
    for source, v in sorted(by_source.items(), key=lambda kv: -kv[1]["chunks"])[:10]:
        print(f"    {v['chunks']:4} chunks {v['tokens']:6} tokens  {source}")
    print("  See subprojects/vera/experiments/runs/C1_corpus_whitespace_defect.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
