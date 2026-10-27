"""Measurement script for GraphRAG after fixes (in-corpus PL, OOC EN, etc.).
"""
import json, sys
from pathlib import Path

PILOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PILOT))
sys.path.insert(0, str(PILOT / "eval"))

import graphrag as g
from frozen_eval_sets_v2 import IN_CORPUS_PL, IN_CORPUS_EN, OOC_PL, CANARY
from diagnose_refusal import OOC_EN

K = 5

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
    ("ooc_en", OOC_EN, False),
    ("canary", CANARY, False),
]:
    summary, rows = run_group(name, items, has_oracle)
    results[name] = {"summary": summary, "rows": rows}
    print(f"{name}: n={summary['n']} refused={summary['n_refused']} "
          f"MRR={summary['mrr_mean']:.3f} Recall={summary['recall_mean']:.3f}")

OUT = PILOT / "eval" / "baseline_measurements_v2"
OUT.mkdir(exist_ok=True)
(OUT / "graphrag_fixed_v2.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"SAVED: {OUT / 'graphrag_fixed_v2.json'}")
