"""Answer-layer pilot v2 grader — strict only, terms pre-registered in
preregistration-v2.md BEFORE spawn #1 ( sesja 3, Tier 3 ). No semantic map.

Matching rule (frozen pre-registration): norm(term) in norm(answer),
norm = NFKD + lowercase. Refusal = exact marker "BRAK W KSIĄŻCE" present.
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = json.loads((ROOT / "handoff" / "pilot-answer-layer-2026-10-18" / "answers-raw-v2.json").read_text(encoding="utf-8"))["answers"]

# Pre-registered Polish stems (preregistration-v2.md, frozen before spawn #1)
TERMS: dict[str, list[str]] = {
    "q001":  ["wiedz", "intenc", "duplikac", "reprezentac"],
    "q002":  ["szkielet", "prototyp", "wyrzuc", "tracer"],
    "q003":  ["coupling", "delegow", "mixin", "interfejs"],
    "q004":  ["warto", "zasad", "zmian"],
    "q005":  ["napraw", "zaraz"],
    "q006":  ["precond", "postcond", "caller", "invariant"],
    "q007":  ["obserwat", "pub", "reaktywn", "automata"],
    "q008":  ["martw", "uszkod", "supervisor"],
    "q009":  ["asercj", "testow", "zostaw"],
    "q010":  ["duplikac", "ortogonal", "współzależ", "zmian"],
    "q011":  ["binarn", "połow", "zawęż"],
    "q012":  ["aktor", "blackboard", "wiadomost"],
    "q013":  ["przypadk", "świadom", "szczęści"],
    "q015":  ["kontrol", "test", "automatyz"],
}
MARKER = "brazil".replace("brazil", "BRAK W KSIĄŻCE")  # exact marker


def norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).lower()


def main() -> None:
    rows = []
    strict_ok = 0
    ref_ok = 0
    for qid, terms in sorted(TERMS.items()):
        ans = RAW[qid]
        a = norm(ans)
        refused = norm(MARKER) in a
        detail = {t: norm(t) in a for t in terms}
        ok = (not refused) and all(detail.values())
        strict_ok += ok
        rows.append({"qid": qid, "refused": refused, "terms": detail, "pass": ok})
    unanswerable = [f"u{i:03d}" for i in range(1, 9)]
    ref_rows = []
    for uid in unanswerable:
        refused = norm(MARKER) in norm(RAW[uid])
        ref_ok += refused
        ref_rows.append({"qid": uid, "refusal": refused})
    canary = norm(MARKER) in norm(RAW["canary"])
    n = len(TERMS)
    print(f"strict={strict_ok}/{n} refusal={ref_ok}/8 canary_refusal={canary} (threshold >=10/14, >=6/8)")
    for r in rows:
        state = "".join("+" if v else "-" for v in r["terms"].values())
        cat = "REFUSAL(answer-layer)" if r["refused"] else ("pass" if r["pass"] else "missing-terms")
        print(f"{r['qid']}: [{state}] {cat}  missing={[t for t, v in r['terms'].items() if not v]}")
    for r in ref_rows:
        print(f"{r['qid']}: refusal={r['refusal']}")
    out = {"strict_pass": strict_ok, "answerable_denominator": n, "refusal": ref_ok, "canary": canary, "rows": rows, "refusal_rows": ref_rows}
    p = ROOT / "handoff" / "pilot-answer-layer-2026-10-18" / "grading-results-v2.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
