"""Weryfikacja artefaktu graphrag_fixed_v2.json wobec tabeli D2 z Sesji 1.
Read-only. Nie modyfikuje żadnego pliku.
"""
import json
from pathlib import Path

EVAL = Path(__file__).resolve().parent
FIXED = EVAL / "baseline_measurements_v2" / "graphrag_fixed_v2.json"
BASELINE = EVAL / "baseline_measurements_v2" / "graphrag_baseline_v2.json"

EXPECTED = {
    "in_corpus_pl": {"refused": 0,  "n": 10, "mrr": 0.783, "recall": 0.900},
    "in_corpus_en": {"refused": 0,  "n": 10, "mrr": 0.817, "recall": 1.000},
    "ooc_pl":       {"refused": 5,  "n": 5,  "mrr": 0.000, "recall": 0.000},
    "ooc_en":       {"refused": 5,  "n": 5,  "mrr": 0.000, "recall": 0.000},
    "canary":       {"refused": 5,  "n": 5,  "mrr": 0.000, "recall": 0.000},
}

def load(p):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def summarize(group):
    s = group.get("summary", group)
    return {
        "n": s.get("n"),
        "n_refused": s.get("n_refused", s.get("refused")),
        "mrr": s.get("mrr_mean", s.get("mrr")),
        "recall": s.get("recall_mean", s.get("recall")),
    }

fixed = load(FIXED)
baseline = load(BASELINE)

print("=== FILE EXISTENCE ===")
print(f"FIXED exists: {FIXED.exists()}  size: {FIXED.stat().st_size if FIXED.exists() else 0} bytes")
print(f"BASELINE exists: {BASELINE.exists()}")

if fixed is None:
    print("FIXED is None — STOP")
    raise SystemExit(1)

print("\n=== FIXED GROUPS ===")
print(f"top-level keys: {sorted(fixed.keys())}")

print("\n=== PER-GROUP COMPARISON (fixed vs D2) ===")
mismatches = []
for gname, exp in EXPECTED.items():
    if gname not in fixed:
        print(f"{gname}: MISSING in fixed")
        mismatches.append((gname, "missing"))
        continue
    got = summarize(fixed[gname])
    ok = (got["n"] == exp["n"]
          and got["n_refused"] == exp["refused"]
          and abs((got["mrr"] or 0) - exp["mrr"]) < 1e-3
          and abs((got["recall"] or 0) - exp["recall"]) < 1e-3)
    print(f"{gname}: fixed={got}  expected={exp}  {'OK' if ok else 'MISMATCH'}")
    if not ok:
        mismatches.append((gname, got))

print("\n=== BASELINE (for delta sanity) ===")
if baseline is not None:
    for gname in EXPECTED:
        if gname in baseline:
            print(f"{gname}: baseline={summarize(baseline[gname])}")
        else:
            print(f"{gname}: baseline MISSING")

print("\n=== VERDICT ===")
if not mismatches:
    print("OK: all groups match D2")
else:
    print(f"DISCREPANCY: {len(mismatches)} group(s) diverge")
    for g, v in mismatches:
        print(f"  - {g}: {v}")
