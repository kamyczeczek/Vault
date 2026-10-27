"""Run and save extended eval and refusal audit for Faza 8c.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import graphrag as g
import vec_index as vi

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
        "00_session_compaction_for_ai_agents", "00_session_compaction_for_ai_agents_research",
        "01_session_compaction_for_ai_agents", "01_session_compaction_for_ai_agents_research"
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
    audit_path = Path(__file__).resolve().parent / "refusal_audit.md"
    ooc = [t for t in TEST_QUESTIONS if not t[2]]

    lines = [
        "# Refusal Audit — Out-of-Corpus (Faza 8c)",
        "",
        "| qid | pytanie | refusal (hybrid) | refusal (base) | top5_ids | top5_cosine |",
        "|---|---|---|---|---|---|"
    ]
    diag = []
    for qid, q, _ in ooc:
        plan = g.zbuduj_plan(q)
        plan.uzyj_wektorow = True
        w_h = g.retrieve(plan, [])
        ranked_h = [w["id"] for w in w_h]
        res_h = g.syntezuj_odpowiedz(q, g.oblicz_pokrycie(w_h, plan.slowa_kluczowe))
        ref_h = bool(res_h.get("odmowa"))
        np_h = res_h.get("n_pokrytych", 0)

        plan.uzyj_wektorow = False
        w_b = g.retrieve(plan, [])
        res_b = g.syntezuj_odpowiedz(q, g.oblicz_pokrycie(w_b, plan.slowa_kluczowe))
        ref_b = bool(res_b.get("odmowa"))
        np_b = res_b.get("n_pokrytych", 0)

        cos = []
        if vi.indeks_gotowy():
            try:
                cos = [f"{n}:{s:.3f}" for n, s in vi.wyszukaj_wektorowo(q, 5)]
            except:
                pass
        lines.append(f"| {qid} | {q} | {ref_h} | {ref_b} | `{', '.join(ranked_h[:5])}` | `{', '.join(cos)}` |")
        diag.append((qid, np_b, np_h, ref_h))

    lines.extend([
        "", "## Diagnoza n_pokrytych", "",
        "| qid | n_pokrytych (base) | n_pokrytych (hybrid) | refusal (hybrid) | stan |",
        "|---|---|---|---|---|"
    ])
    for qid, np_b, np_h, ref_h in diag:
        reason = "Odmówił" if ref_h else f"Nie odmówił: base={np_b}, hybrid={np_h}"
        lines.append(f"| {qid} | {np_b} | {np_h} | {ref_h} | {reason} |")

    audit_path.write_text("\n".join(lines), encoding="utf-8")
    print("AUDIT_DONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

import sys
from pathlib import Path
eval_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(eval_dir))
import extended_eval

out_path = eval_dir / "extended_eval_output.txt"
import io
class Tee:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Tee(out_path)
extended_eval.main()
