"""Porownanie baseline (FTS) vs hybryda (FTS5+wektory RRF) — Faza 8 Krok 4.

Uruchomienie z katalogu pilots/graphrag:
    python.exe eval/hybrid_eval.py
Wymaga fixtures/graph_vec.db (fixtures/build_vector_index.py).
Bez indeksu hybryda == baseline (fallback w wyszukaj_hybrydowo).
Read-only, bez zapisu proofow.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import graphrag as g

PYTANIA = [
    ("Q1", "Czym jest SEVerA i jak sie ma do self-evolving agents?",
     ["00_severa_verified_synthesis_of_self_evolving_agent"]),
    ("Q2", "What trust tiers does this lab use for evidence, and what does tier 3 mean?",
     ["00_okf_methodology_research"]),
    ("Q3", "Jakie sa metody kompresji sesji agentow?",
     ["00_session_compaction_for_ai_agents",
      "00_session_compaction_for_ai_agents_research",
      "01_session_compaction_for_ai_agents",
      "01_session_compaction_for_ai_agents_research"]),
    ("Q6", "Jakie wzorce pamięci stosują agenci?",
     ["00_agent_memory_hierarchies"]),
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?",
     []),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?",
     []),
]

K = 5


def ewaluuj(uzyj_wektorow: bool, uzyj_semantycznego: bool = True) -> tuple[float, float, int]:
    mrrs: list[float] = []
    recs: list[float] = []
    ref_ok = 0
    for qid, pytanie, oracle in PYTANIA:
        plan = g.zbuduj_plan(pytanie)
        plan.uzyj_wektorow = uzyj_wektorow
        wyniki = g.retrieve(plan, [])
        ranked = [w["id"] for w in wyniki]
        if uzyj_semantycznego:
            pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe, pytanie=pytanie)
        else:
            pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)
        wynik = g.syntezuj_odpowiedz(pytanie, pokryte)
        odmowa = bool(wynik.get("odmowa"))
        if oracle:
            mrr = g.mrr_at_k(oracle, ranked, K)
            rec = g.recall_at_k(oracle, ranked, K)
            ndcg = g.ndcg_at_k(oracle, ranked, K)
            mrrs.append(mrr)
            recs.append(rec)
            print(f"{qid} MRR@5={mrr:.3f} Recall@5={rec:.3f} "
                  f"NDCG@5={ndcg:.3f} odmowa={odmowa} top3={ranked[:3]}")
        else:
            ok = odmowa is True
            ref_ok += 1 if ok else 0
            stan = "OK" if ok else "REGRESJA"
            print(f"{qid} (refusal) odmowa={odmowa} oczekiwana=TAK "
                  f"{stan} top3={ranked[:3]}")
    mrr_avg = sum(mrrs) / len(mrrs)
    rec_avg = sum(recs) / len(recs)
    print(f"in-corpus (Q1-Q3): MRR@5={mrr_avg:.3f} Recall@5={rec_avg:.3f}")
    print(f"refusal (Q4-Q5): {ref_ok}/2")
    return mrr_avg, rec_avg, ref_ok


def main() -> int:
    print("== 1. BASELINE (FTS, semantyczny OFF) == obatained old coverage logic")
    b0_mrr, b0_rec, b0_ref = ewaluuj(False, False)
    print("== 2. BASELINE (FTS, semantyczny ON) ==")
    b1_mrr, b1_rec, b1_ref = ewaluuj(False, True)

    print("== 3. HYBRYDA (RRF, semantyczny OFF) ==")
    h0_mrr, h0_rec, h0_ref = ewaluuj(True, False)
    print("== 4. HYBRYDA (RRF, semantyczny ON) ==")
    h1_mrr, h1_rec, h1_ref = ewaluuj(True, True)

    try:
        from vec_index import indeks_gotowy
        print(f"indeks_gotowy={indeks_gotowy()}")
    except Exception as e:
        print(f"vec_index niedostepny: {e}")

    print(f"DELTAS semantic ON vs OFF (Baseline): MRR={b1_mrr - b0_mrr:+.3f}, Recall={b1_rec - b0_rec:+.3f}, refusal={b1_ref} (base {b0_ref})")
    print(f"DELTAS semantic ON vs OFF (Hybrid): MRR={h1_mrr - h0_mrr:+.3f}, Recall={h1_rec - h0_rec:+.3f}, refusal={h1_ref} (base {h0_ref})")
    print("HYBRID_DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
