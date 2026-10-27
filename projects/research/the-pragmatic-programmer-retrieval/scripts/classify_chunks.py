#!/usr/bin/env python3
"""Session 5 FAZA 2: classify all 855 chunks into
{heading-only, related-sections, code-listing, challenge, prose}
using the pre-registered priority rules (first match wins), write
data/chunks_classified.json (NEW file, chunks.json untouched), and report
per-type counts + how many chunks of each type landed in session-4 top-8
(results.json variants A and B).

Rules (priority order):
1. heading-only: text contains only headings (**Topic N**, ####, #####) and < 100 chars prose
2. related-sections: contains "RELATED SECTIONS INCLUDE" or >= 3 lines starting "- Topic N"
3. code-listing: contains "```" or >= 5 lines starting with whitespace/code
4. challenge: text starts with "#### CHALLENGES" or "#### **CHALLENGES**"
5. prose: fallback
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CHUNKS = PROJECT / "data" / "chunks.json"
OUT = PROJECT / "data" / "chunks_classified.json"
RESULTS = PROJECT / "handoff" / "en-vs-pl-tier3-2026-10-18" / "results.json"

HEADING_LINE = re.compile(r"^\s*(\*\*Topic \d+\*\*|#{4,6} |#\d+ )")
RELATED_LINE = re.compile(r"^\s*-\s*Topic \d+")


def classify(text: str) -> str:
    lines = text.splitlines()
    # 1. heading-only: strip headings/blank; whatever remains is prose
    prose_left = "\n".join(l for l in lines if l.strip() and not HEADING_LINE.match(l))
    if len(prose_left.strip()) < 100:
        return "heading-only"
    # 2. related-sections
    if "RELATED SECTIONS INCLUDE" in text:
        return "related-sections"
    if sum(1 for l in lines if RELATED_LINE.match(l)) >= 3:
        return "related-sections"
    # 3. code-listing
    if "```" in text:
        return "code-listing"
    code_lines = sum(1 for l in lines if l.startswith("    ") or l.startswith("\t"))
    if code_lines >= 5:
        return "code-listing"
    # 4. challenge
    if re.match(r"^#### (\*\*)?CHALLENGES", text.strip()):
        return "challenge"
    return "prose"


def main() -> int:
    chunks = json.loads(CHUNKS.read_text(encoding="utf-8"))
    classes = [classify(c["text"]) for c in chunks]
    n_classified = sum(1 for c in chunks if c.get("type"))
    out = [
        {**c, "type_src": c.get("type"), "class": cls}
        for c, cls in zip(chunks, classes)
    ]
    assert all("class" in c for c in out)
    if sum(classes.count(t) for t in set(classes)) != len(chunks):
        print(f"STOP: class sum != {len(chunks)}", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    total = len(chunks)
    counts = Counter(classes)
    print(f"chunks total={total} (src type present on {n_classified})")
    for t in ["prose", "related-sections", "heading-only", "code-listing", "challenge"]:
        n = counts.get(t, 0)
        print(f"{t}\tcount={n}\tpct={n/total*100:.1f}%")

    # cross-tab with source type for provenance
    xtab = Counter((c.get("type", "?"), cls) for c, cls in zip(chunks, classes))
    print("--- src type x class ---")
    for (src, cls), n in sorted(xtab.items(), key=lambda kv: -kv[1]):
        print(f"{src}\t{cls}\t{n}")

    # top-8 overlap with session 4 (variants A and B), keyed by chunk id via topic? results.json stores topics only.
    res = json.loads(RESULTS.read_text(encoding="utf-8"))
    # map chunk -> class for topic lookup: count class distribution of all chunks in top8 (by topic)
    by_topic: dict = {}
    for c, cls in zip(chunks, classes):
        by_topic.setdefault(c["topic"], []).append(cls)
    for variant in ["A", "B"]:
        # results.json stores topics, not chunk ids => composition is weighted by
        # each topic's chunk-class mix (proxy, not per-slot exact). Exact per-slot
        # counts come from FAZA 3 (eval_en_filtered.py logs filtered_out).
        print(f"--- top-8 class composition, variant {variant} (weighted by topic chunk mix) ---")
        w = Counter()
        for row in res[variant]["rows"]:
            for t in row["top8topics"]:
                members = by_topic.get(t, ["?"])
                # each slot's expected class = average distribution of chunks for that topic
                for cls in set(members):
                    w[cls] += members.count(cls) / len(members)
        tot = sum(w.values())
        for cls, n in w.most_common():
            print(f"{cls}\t{n:.2f}\t{n/tot*100:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
