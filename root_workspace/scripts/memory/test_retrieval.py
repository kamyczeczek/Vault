"""Sanity tests for `scripts/memory/retrieval_v1.py` (config K1, engine B1).

Run:
    python scripts/memory/test_retrieval.py          # 5 sanity questions
    python scripts/memory/test_retrieval.py -v       # + per-hit dump

5 questions (3 answerable, 2 unanswerable), stdlib only. Exit 1 on any failure.

Ground truth is at the **family** level, not the doc level. That is the definition
the deployed config was selected on (`refusal_filter_v2.fam_hit`, report §10/§17):
a question is a hit if a *family-relevant* row appears in the top-5. The doc-level
`expected` field in the gold set (e.g. Q1 -> `lessons:1`) is **not** met by any
measured config — Q1's family hit is `problems:65`, and `lessons:1` is not
retrieved at all. That gap is a pre-existing measurement caveat (see SCARS S64:
`recall@5` on this corpus measures annotation, not retrieval), not something this
test should paper over. It is printed as a non-fatal NOTE.

Unanswerable questions are the two new-domain ones (Q36 history, Q37 mechanics)
from `gold_set_extended_v2.json`: refusal (empty hit list) is the expected and only
refusal mechanism, since H5 was rejected (report §19).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import retrieval_v1 as rv  # noqa: E402

# Family definition, mirrored from scripts/_scratch/refusal_filter_v2.py::fam_hit
BRAMKA = {("lessons", 1), ("problems", 65), ("problems", 62)}

CASES = [
    {
        "qid": 1, "expect": "hit", "family": "bramka_integrity", "want": BRAMKA,
        "q": "Dlaczego sprawdzanie integralności workspace zgłasza błąd po dodaniu nowego pliku w root?",
        "doc_note": "gold 'expected' is lessons:1; the family hit actually retrieved is problems:65",
    },
    {
        "qid": 3, "expect": "hit", "family": "adr_brain_db", "want": "decisions",
        "q": "Jaki ADR wprowadził jedną bazę brain.db jako jedyne źródło prawdy w repozytorium?",
        "doc_note": "gold 'expected' is decisions:1; any decisions row satisfies the family",
    },
    {
        "qid": 4, "expect": "hit", "family": "bramka_integrity", "want": BRAMKA,
        "q": "Jakie zasady wymuszają testy oraz bramki pre-commit w architekturze workspace?",
        "doc_note": "gold 'expected' is decisions:2; family hit comes from problems:62",
    },
    {
        "qid": 36, "expect": "refusal", "want": None,
        "q": "Kto dowodził wojskami francuskimi pod Waterloo?",
        "doc_note": "history; absent from the corpus",
    },
    {
        "qid": 37, "expect": "refusal", "want": None,
        "q": "Jak działa silnik wysokoprężny z zapłonem samoczynnym?",
        "doc_note": "mechanics; absent from the corpus",
    },
]


def family_hit(want, hits) -> bool:
    if want == "decisions":
        return any(h["table"] == "decisions" for h in hits)
    return any((h["table"], h["id"]) in want for h in hits)


def main(argv: list[str]) -> int:
    verbose = "-v" in argv
    conn = rv.connect()
    failures = 0
    try:
        for case in CASES:
            result = rv.search(case["q"], conn=conn)
            hits = result["hits"]
            if case["expect"] == "refusal":
                ok = not hits
                got = "REFUSAL" if ok else f"RETURNED {len(hits)}"
            else:
                ok = family_hit(case["want"], hits)
                got = "HIT" if ok else "MISS"
            tag = "PASS" if ok else "FAIL"
            failures += not ok
            print(f"[{tag}] Q{case['qid']:<3} expect={case['expect']:<7} got={got:<10} "
                  f"tokens={result['tokens']}")
            if not ok or verbose:
                for i, h in enumerate(hits, 1):
                    print(f"        {i}. {h['table']}:{h['id']} rank={h['rank']:.3f} {h['preview'][:80]}")
                print(f"        NOTE: {case['doc_note']}")
    finally:
        conn.close()

    total = len(CASES)
    print(f"\n{total - failures}/{total} sanity checks passed")
    if failures:
        print("FAILED — the deployed config does not behave as validated; do not ship.")
        return 1
    print("OK — retrieval_v1 behaves as validated (K1/B1). "
          "Full-set parity: scripts/_scratch/parity_retrieval_v1.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
