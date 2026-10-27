"""Ranking eval Fazy 8 (baseline Fazy 7 + delty). Read-only, bez zapisu proofow.

Uruchomienie z katalogu pilots/graphrag:
    python.exe eval/ranking_eval.py
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
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?",
     []),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?",
     []),
]

K = 5


def main() -> int:
    mrrs: list[float] = []
    recs: list[float] = []
    ref_ok = 0
    for qid, pytanie, oracle in PYTANIA:
        plan = g.zbuduj_plan(pytanie)
        wyniki = g.retrieve(plan, [])
        ranked = [w["id"] for w in wyniki]
        mrr = g.mrr_at_k(oracle, ranked, K)
        rec = g.recall_at_k(oracle, ranked, K)
        ndcg = g.ndcg_at_k(oracle, ranked, K)
        pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)
        wynik = g.syntezuj_odpowiedz(pytanie, pokryte)
        odmowa = bool(wynik.get("odmowa"))
        if oracle:
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
    print(f"BASELINE in-corpus (Q1-Q3): MRR@5={sum(mrrs) / len(mrrs):.3f} "
          f"Recall@5={sum(recs) / len(recs):.3f}")
    print(f"BASELINE refusal (Q4-Q5): {ref_ok}/2")
    print("BASELINE_DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
