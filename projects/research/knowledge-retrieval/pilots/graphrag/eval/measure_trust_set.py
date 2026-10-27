"""Pomiar retrieval na pełnym test secie (in-corpus + OOC + boundary).
Read-only. Wynik: eval/trust_set_results.json + stdout.
"""
import sys, json, sqlite3
from pathlib import Path

PILOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PILOT))
import graphrag as g

# Wczytaj questions.md — parsuj tabele
Q = PILOT / "eval" / "questions.md"
lines = Q.read_text(encoding="utf-8").splitlines()
questions = []
for line in lines:
    if not line.startswith("| Q") and not line.startswith("| O") and not line.startswith("| B"):
        continue
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 5:
        continue
    qid = parts[1]
    pytanie = parts[2]
    typ = parts[3]
    oracles_raw = parts[4]
    # oracles w backtickach
    import re
    oracles = re.findall(r"`([a-z0-9_]+)`", oracles_raw)
    questions.append({"id": qid, "pytanie": pytanie, "typ": typ, "oracles": oracles})

K = 10
results = []
for q in questions:
    plan = g.zbuduj_plan(q["pytanie"])
    plan.uzyj_wektorow = True  # hybryda ON
    wyniki = g.retrieve(plan, [])
    ranked = [w["id"] for w in wyniki]
    pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)  # semantic OFF
    wynik = g.syntezuj_odpowiedz(q["pytanie"], pokryte)
    odmowa = bool(wynik.get("odmowa"))

    row = {
        "id": q["id"],
        "typ": q["typ"],
        "pytanie": q["pytanie"],
        "odmowa": odmowa,
        "top10": ranked[:K],
        "oracles": q["oracles"],
    }
    if q["oracles"]:
        row["recall@1"] = g.recall_at_k(q["oracles"], ranked, 1)
        row["recall@3"] = g.recall_at_k(q["oracles"], ranked, 3)
        row["recall@10"] = g.recall_at_k(q["oracles"], ranked, 10)
        row["mrr"] = g.mrr_at_k(q["oracles"], ranked, 10)
        row["mrr@5"] = g.mrr_at_k(q["oracles"], ranked, 5)
        row["recall@5"] = g.recall_at_k(q["oracles"], ranked, 5)
        row["ndcg@5"] = g.ndcg_at_k(q["oracles"], ranked, 5)
        row["family_recall@5"] = g.family_recall_at_k(q["oracles"], ranked, 5)
    results.append(row)

# Podsumowanie
in_corpus = [r for r in results if r["typ"] == "in-corpus"]
ooc = [r for r in results if r["typ"] == "out-of-corpus"]
boundary = [r for r in results if r["typ"] == "boundary"]

print("=== IN-CORPUS ===")
for r in in_corpus:
    print(f"{r['id']}: R@1={r.get('recall@1',0):.3f} R@3={r.get('recall@3',0):.3f} R@10={r.get('recall@10',0):.3f} MRR={r.get('mrr',0):.3f} MRR@5={r.get('mrr@5',0):.3f} odmowa={r['odmowa']}")

print("\n=== OUT-OF-CORPUS ===")
for r in ooc:
    print(f"{r['id']}: odmowa={r['odmowa']} (oczekiwana=True)")

print("\n=== BOUNDARY ===")
for r in boundary:
    print(f"{r['id']}: odmowa={r['odmowa']} (oczekiwana=True)")

# Metryki zbiorcze
mrr_avg = sum(r.get("mrr", 0) for r in in_corpus) / len(in_corpus) if in_corpus else 0
recall_1_avg = sum(r.get("recall@1", 0) for r in in_corpus) / len(in_corpus) if in_corpus else 0
recall_3_avg = sum(r.get("recall@3", 0) for r in in_corpus) / len(in_corpus) if in_corpus else 0
recall_10_avg = sum(r.get("recall@10", 0) for r in in_corpus) / len(in_corpus) if in_corpus else 0
recall_avg = sum(r.get("recall@5", 0) for r in in_corpus) / len(in_corpus) if in_corpus else 0
ooc_ref = sum(1 for r in ooc if r["odmowa"]) / len(ooc) if ooc else 0
bound_ref = sum(1 for r in boundary if r["odmowa"]) / len(boundary) if boundary else 0
false_ref = sum(1 for r in in_corpus if r["odmowa"]) / len(in_corpus) if in_corpus else 0

print(f"\n=== ZBIORCZO ===")
print(f"IN-CORPUS (n={len(in_corpus)}): Recall@1={recall_1_avg:.3f} Recall@3={recall_3_avg:.3f} Recall@10={recall_10_avg:.3f} MRR={mrr_avg:.3f} MRR@5={sum(r.get('mrr@5', 0) for r in in_corpus) / len(in_corpus) if in_corpus else 0:.3f} Recall@5={recall_avg:.3f}")
print(f"OOC refusal (n={len(ooc)}): {ooc_ref:.1%}")
print(f"BOUNDARY refusal (n={len(boundary)}): {bound_ref:.1%}")
print(f"FALSE REFUSAL in-corpus (n={len(in_corpus)}): {false_ref:.1%}")

# Zapisz
out = PILOT / "eval" / "trust_set_results.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nZapisano: {out}")
