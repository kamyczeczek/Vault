import sys
from pathlib import Path
PILOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PILOT))
import graphrag as g
from eval.frozen_eval_sets_v2 import IN_CORPUS_PL

conn = g.polacz_baze()
for qid, q, oracle in IN_CORPUS_PL:
    plan = g.zbuduj_plan(q)
    wyniki = g.wyszukaj_fts(conn, plan.slowa_kluczowe, plan.top_k)
    pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)
    wynik = g.syntezuj_odpowiedz(q, pokryte)
    print(f"{qid}: {q}")
    print(f"  Keywords: {plan.slowa_kluczowe}")
    print(f"  Refused: {wynik['odmowa']}, n_pokrytych: {wynik['n_pokrytych']}")
    if wynik['odmowa']:
        # Check if oracle nodes were in wyniki and why they failed
        oracle_wyniki = [w for w in wyniki if w['id'] in oracle]
        print(f"  Oracle nodes in FTS results: {[w['id'] for w in oracle_wyniki]}")
        for ow in oracle_wyniki:
            n_matches = sum(1 for sw in plan.slowa_kluczowe if sw in (ow.get('body') or '').lower())
            print(f"    - {ow['id']}: n_matches={n_matches}")
conn.close()
