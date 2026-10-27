import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import graphrag as g
print("OK")

"""Test hypothesis for Faza 8d: evaluating 30 questions with alternative thresholds.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import graphrag as g

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
    ("Q3", "Jakie sa metody kompresji sesji agentow?", ["00_session_compaction_for_ai_agents", "00_session_compaction_for_ai_agents_research", "01_session_compaction_for_ai_agents", "01_session_compaction_for_ai_agents_research"]),
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

def run_evaluation(min_matches: int):
    mrrs_en, recs_en, mrrs_pl, recs_pl = [], [], [], []
    ref_pl, ref_en = 0, 0
    conn = g.polacz_baze()
    try:
        for qid, pytanie, oracle in TEST_QUESTIONS:
            plan = g.zbuduj_plan(pytanie)
            plan.uzyj_wektorow = True
            wyniki = g.retrieve(plan, [])
            ranked = [w["id"] for w in wyniki]
            covered = []
            for w in wyniki:
                body = (w.get("body") or "").lower()
                n_matches = sum(1 for sw in plan.slowa_kluczowe if sw in body)
                if n_matches < min_matches:
                    covered.append({
                        "id": w["id"],
                        "title": w.get("title", ""),
                        "source_family": w.get("source_family", ""),
                        "trust_tier": w.get("trust_tier"),
                        "pokrycie": False,
                        "cytaty": [],
                        "n_trafien": n_matches,
                    })
                    continue
                has_cov, cyts = g.pokrycie_cytatem(w.get("body") or "", plan.slowa_kluczowe)
                covered.append({
                    "id": w["id"],
                    "title": w.get("title", ""),
                    "source_family": w.get("source_family", ""),
                    "trust_tier": w.get("trust_tier"),
                    "pokrycie": has_cov,
                    "cytaty": cyts[:3],
                    "n_trafien": n_matches,
                })
            wynik = g.syntezuj_odpowiedz(pytanie, covered)
            odmowa = bool(wynik.get("odmowa"))
            if oracle:
                mrr = g.mrr_at_k(oracle, ranked, 5)
                rec = g.recall_at_k(oracle, ranked, 5)
                if qid in ["Q3", "Q14", "Q15", "Q16", "Q17", "Q18", "Q19", "Q20", "Q21", "Q22"]:
                    mrrs_pl.append(mrr); recs_pl.append(rec)
                else:
                    mrrs_en.append(mrr); recs_en.append(rec)
            else:
                if qid in ["Q4", "Q5", "Q23", "Q24", "Q25"]:
                    if odmowa: ref_pl += 1
                else:
                    if odmowa: ref_en += 1
    finally:
        conn.close()
    print(f"MIN_KEYWORD_MATCHES = {min_matches}: EN_in=(MRR {sum(mrrs_en)/len(mrrs_en):.3f}), PL_in=(MRR {sum(mrrs_pl)/len(mrrs_pl):.3f}), RefPL={ref_pl}/5, RefEN={ref_en}/5")

def main():
    for m in [2, 3, 4, 5]:
        run_evaluation(m)

if __name__ == "__main__":
    main()
