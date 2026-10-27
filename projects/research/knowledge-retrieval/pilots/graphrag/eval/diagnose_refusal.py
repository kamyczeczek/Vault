"""Diagnose refusal for out-of-corpus questions (Faza 8d).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import graphrag as g

OOC_EN = [
    ("Q26", "What is the latest release date and new features of Python 3.15?"),
    ("Q27", "What was Tesla's stock price at market close yesterday?"),
    ("Q28", "What is the status of flight UA123 from New York to London?"),
    ("Q29", "Who is the current elected President of Mars colony in 2026?"),
    ("Q30", "Which company announced quantum supremacy with 1 million qubits today?"),
]

OOC_PL = [
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?"),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?"),
    ("Q23", "Jaka będzie prognoza pogody w Warszawie jutro o 14:00?"),
    ("Q24", "Jaki jest tradycyjny przepis na domowe pierogi ruskie?"),
    ("Q25", "Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia?"),
]

def main():
    print("=== DIAGNOSE REFUSAL ===")
    conn = g.polacz_baze()
    try:
        for qid, q in OOC_EN + OOC_PL:
            plan = g.zbuduj_plan(q)
            plan.uzyj_wektorow = True
            wyniki = g.retrieve(plan, [])
            pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)
            wynik = g.syntezuj_odpowiedz(q, pokryte)
            print(f"QID: {qid} | Pytanie: {q}")
            print(f"  Slowa kluczowe ({len(plan.slowa_kluczowe)}): {plan.slowa_kluczowe}")
            print(f"  N_pokrytych: {wynik.get('n_pokrytych', 0)} | Odmowa: {wynik.get('odmowa')}")
            for c in pokryte[:3]:
                print(f"    - Node {c['id']}: n_trafien={c.get('n_trafien')} | pokrycie={c['pokrycie']} | cyts={len(c['cytaty'])}")
            print("-" * 50)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
