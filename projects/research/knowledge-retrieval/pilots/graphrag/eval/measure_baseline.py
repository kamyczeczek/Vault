"""Frozen baseline measurement for graphrag.
Runs the frozen pilot on frozen_eval_sets and produces verifiable artifacts.
Does NOT modify pilot code (read-only import).
"""
import json, sys
from pathlib import Path

PILOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PILOT))
sys.path.insert(0, str(PILOT / "eval"))

import graphrag as g   # frozen pilot — read-only
from frozen_eval_sets import IN_CORPUS_PL, IN_CORPUS_EN, OOC_PL, CANARY

K = 5
OUT = PILOT / "eval" / "baseline_measurements"
OUT.mkdir(exist_ok=True)

def run_group(name, items, has_oracle=True):
    rows = []
    for qid, q, *rest in items:
        oracle = rest[0] if rest and has_oracle else None
        plan = g.zbuduj_plan(q)
        plan.uzyj_wektorow = True
        wyniki = g.retrieve(plan, [])
        ranked = [r["id"] for r in wyniki]
        pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)
        wynik = g.syntezuj_odpowiedz(q, pokryte)
        refused = bool(wynik.get("odmowa"))
        mrr = g.mrr_at_k(oracle, ranked, K) if oracle else None
        recall = g.recall_at_k(oracle, ranked, K) if oracle else None
        rows.append({
            "qid": qid, "question": q, "refused": refused,
            "top_k": ranked, "mrr": mrr, "recall": recall,
        })
    summary = {
        "n": len(rows),
        "n_refused": sum(1 for r in rows if r["refused"]),
        "mrr_mean": (sum(r["mrr"] for r in rows if r["mrr"] is not None)
                     / max(1, sum(1 for r in rows if r["mrr"] is not None))),
        "recall_mean": (sum(r["recall"] for r in rows if r["recall"] is not None)
                        / max(1, sum(1 for r in rows if r["recall"] is not None))),
    }
    return summary, rows

results = {}
for name, items, has_oracle in [
    ("in_corpus_pl", IN_CORPUS_PL, True),
    ("in_corpus_en", IN_CORPUS_EN, True),
    ("ooc_pl", OOC_PL, False),
    ("canary", CANARY, False),
]:
    summary, rows = run_group(name, items, has_oracle)
    results[name] = {"summary": summary, "rows": rows}
    print(f"{name}: n={summary['n']} refused={summary['n_refused']} "
          f"MRR={summary['mrr_mean']:.3f} Recall={summary['recall_mean']:.3f}")

(OUT / "graphrag_baseline.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"SAVED: {OUT / 'graphrag_baseline.json'}")
