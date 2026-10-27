"""Extended benchmark (30 questions) — Faza 8c."""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import graphrag as g
try:
    import vec_index as vi
except Exception:
    vi = None

TEST_QUESTIONS = [
    ("Q1", "What is SEVerA and how does it relate to self-evolving agents?", ["00_severa_verified_synthesis_of_self_evolving_agent"]),
    ("Q2", "What trust tiers does this lab use for evidence, and what does tier 3 mean?", ["00_okf_methodology_research"]),
    ("Q6", "What are the core structures of agent memory hierarchies?", ["00_agent_memory_hierarchies"]),
    ("Q7", "How do agent execution hooks provide deterministic loop interception and guardrails?", ["00_agent_execution_hooks_guardrails"]),
    ("Q8", "What is the isolate build prove ship methodology in software factories?", ["00_00_software_factory_isolate_build_prove_ship"]),
    ("Q9", "How does the engineering workspace function as an adaptive search environment?", ["00_adaptive_search_workspace_architecture"]),
    ("Q10", "What are the key version control paradigms and git discipline patterns for autonomous agents?", ["00_agentic_git_discipline_patterns"]),
    ("Q11", "How is modular graph structured in agentic RAG?", ["00_agentic_rag_modular_graph"]),
    ("Q12", "What is the CRITIC framework for verify-then-correct with external tools?", ["00_07_critic_external_tool_verification"]),
    ("Q13", "How does lesson persistence and eviction work in ExpeL?", ["00_08_lesson_persistence_eviction_requirement"]),
    ("Q3", "Jakie sa metody kompresji sesji agentow?", [
        "00_session_compaction_for_ai_agents",
        "00_session_compaction_for_ai_agents_research",
        "01_session_compaction_for_ai_agents",
        "01_session_compaction_for_ai_agents_research"
    ]),
    ("Q14", "Czym jest agentic engineering i jak prowadzi od chaosu do świadomego projektowania?", ["00_agentic_engineering_od_chaosu_do_wiadomego_proje"]),
    ("Q15", "Dlaczego ponowne wymyślanie koła w vibe coding jest problemem?", ["00_00_bend2_vibe_coding_reinventing_wheels"]),
    ("Q16", "Jakie są techniki, żeby wycisnąć 2-3x wydajności z AI w kodowaniu?", ["00_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods"]),
    ("Q17", "Jak działa routowanie narzędzi oparte na grafie z samonaprawą?", ["00_32ecfce36290_graph_based_self_healing_tool_routi"]),
    ("Q18", "Do czego służy message passing w analizie i odpornym projektowaniu systemów samonaprawczych?", ["00_524ade10f990_message_passing_for_analysis_and_re"]),
    ("Q19", "Jak działa rozproszona detekcja zmian o odporności bizantyjskiej?", ["00_32e1be065210_byzantine_fault_tolerant_distribute"]),
    ("Q20", "Czym charakteryzuje się energetycznie oszczędne uczenie federacyjne z kwantyzacją?", ["00_225c8527385d_energy_efficient_quantized_federate"]),
    ("Q21", "Jak wygląda taksonomia błędów agentów i frameworki debugowania?", ["00_agent_error_taxonomy_debugging_web_research"]),
    ("Q22", "Jak realizowana jest niskonarzutowa odporność na błędy dla kwantowej uniwersalności?", ["00_0d780aefeb5f_low_overhead_transversal_fault_tole"]),
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?", []),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?", []),
    ("Q23", "Jaka będzie prognoza pogody w Warszawie jutro o 14:00?", []),
    ("Q24", "Jaki jest tradycyjny przepis na domowe pierogi ruskie?", []),
    ("Q25", "Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia?", []),
    ("Q26", "What is the latest release date and new features of Python 3.15?", []),
    ("Q27", "What was Tesla's stock price at market close yesterday?", []),
    ("Q28", "What is the status of flight UA123 from New York to London?", []),
    ("Q29", "Who is the current elected President of Mars colony in 2026?", []),
    ("Q30", "Which company announced quantum supremacy with 1 million qubits today?", []),
]

def main():
    print("== EXTENDED EVAL DETAIL (Faza 8c) ==")
    conn = g.polacz_baze()
    try:
        for qid, pytanie, oracle in TEST_QUESTIONS:
            plan = g.zbuduj_plan(pytanie)
            plan.uzyj_wektorow = True
            wyniki = g.retrieve(plan, [])
            ranked_ids = [w["id"] for w in wyniki]
            top5_ids = ranked_ids[:5]

            top5_cosine = []
            if vi and vi.indeks_gotowy():
                try:
                    model, tok = vi.laduj_model()
                    q_emb = vi.embedding_tekstu(model, tok, pytanie).numpy()
                    import sqlite3
                    vec_db = ROOT / "fixtures" / "graph_vec.db"
                    vec_con = sqlite3.connect(f"file:{vec_db}?mode=ro", uri=True) if vec_db.exists() else None
                    try:
                        import numpy as np
                        for nid in top5_ids:
                            row = vec_con.execute("SELECT embedding FROM nodes WHERE id=?", (nid,)).fetchone() if vec_con else None
                            if row and row[0]:
                                vec = np.frombuffer(row[0], dtype=np.float32)
                                sc = float(np.dot(vec, q_emb))
                            else:
                                sc = 0.0
                            top5_cosine.append(f"{sc:.3f}")
                    finally:
                        if vec_con:
                            vec_con.close()
                except Exception:
                    top5_cosine = ["err"] * len(top5_ids)
            else:
                top5_cosine = ["n/a"] * len(top5_ids)

            pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe, pytanie=pytanie)
            wynik = g.syntezuj_odpowiedz(pytanie, pokryte)
            odmowa = bool(wynik.get("odmowa"))

            print(f"QID: {qid} | Refusal: {odmowa}")
            print(f"  Pytanie: {pytanie}")
            print(f"  Top5 IDs: {top5_ids}")
            print(f"  Top5 Cosine: {top5_cosine}")
            print("-" * 60)

        # --- Canary validation (Faza 8f) ---
        print("== CANARY EVALUATION (Faza 8f) ==")
        canary_path = ROOT / "eval" / "canary.json"
        canary_data = json.loads(canary_path.read_text(encoding="utf-8"))
        canary_failed = False
        for c in canary_data.get("questions", []):
            qid = c["qid"]
            pytanie = c["text"]
            plan = g.zbuduj_plan(pytanie)
            plan.uzyj_wektorow = True
            wyniki = g.retrieve(plan, [])
            pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe, pytanie=pytanie)
            wynik = g.syntezuj_odpowiedz(pytanie, pokryte)
            odmowa = bool(wynik.get("odmowa"))
            status = "OK" if odmowa else "FAIL"
            if not odmowa:
                canary_failed = True
            print(f"CANARY_{qid if 'qid' in locals() else c['qid']}: refusal={odmowa} [{status}]")
            print(f"  Pytanie: {pytanie}")
            print("-" * 60)

        if canary_failed:
            print("CANARY EVALUATION FAILED: some canary questions did not refuse.")
            sys.exit(1)
        else:
            print("CANARY EVALUATION PASSED: all canary questions refused successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
