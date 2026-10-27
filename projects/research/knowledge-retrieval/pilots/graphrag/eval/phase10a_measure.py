"""Phase 10A — measurement of PL→EN translation hypothesis (read-only, no code mods).

Runs the graphrag pilot on original (baseline) and LLM-translated (EN) questions,
computes MRR@5 / Recall@5 / refusal, and writes artifacts to reports/phase10a/.

Usage (from workspace root):
    python projects/research/knowledge-retrieval/pilots/graphrag/eval/phase10a_measure.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # pilots/graphrag
sys.path.insert(0, str(ROOT))
import graphrag as g  # read-only use of the frozen pilot

OUT_DIR = ROOT / "eval" / "phase10a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

K = 5

# --- Test questions (verbatim from eval/extended_eval.py and eval/canary.json) ---

IN_CORPUS_PL = [
    ("Q3", "Jakie sa metody kompresji sesji agentow?",
     ["00_session_compaction_for_ai_agents", "00_session_compaction_for_ai_agents_research",
      "01_session_compaction_for_ai_agents", "01_session_compaction_for_ai_agents_research"]),
    ("Q14", "Czym jest agentic engineering i jak prowadzi od chaosu do świadomego projektowania?",
     ["00_agentic_engineering_od_chaosu_do_wiadomego_proje"]),
    ("Q15", "Dlaczego ponowne wymyślanie koła w vibe coding jest problemem?",
     ["00_00_bend2_vibe_coding_reinventing_wheels"]),
    ("Q16", "Jakie są techniki, żeby wycisnąć 2-3x wydajności z AI w kodowaniu?",
     ["00_jak_naprawd_wycisn_2_3x_z_ai_w_kodowaniu_na_pods"]),
    ("Q17", "Jak działa routowanie narzędzi oparte na grafie z samonaprawą?",
     ["00_32ecfce36290_graph_based_self_healing_tool_routi"]),
    ("Q18", "Do czego służy message passing w analizie i odpornym projektowaniu systemów samonaprawczych?",
     ["00_524ade10f990_message_passing_for_analysis_and_re"]),
    ("Q19", "Jak działa rozproszona detekcja zmian o odporności bizantyjskiej?",
     ["00_32e1be065210_byzantine_fault_tolerant_distribute"]),
    ("Q20", "Czym charakteryzuje się energetycznie oszczędne uczenie federacyjne z kwantyzacją?",
     ["00_225c8527385d_energy_efficient_quantized_federate"]),
    ("Q21", "Jak wygląda taksonomia błędów agentów i frameworki debugowania?",
     ["00_agent_error_taxonomy_debugging_web_research"]),
    ("Q22", "Jak realizowana jest niskonarzutowa odporność na błędy dla kwantowej uniwersalności?",
     ["00_0d780aefeb5f_low_overhead_transversal_fault_tole"]),
    # Q1 and Q2 in extended_eval.py are English but their gold nodes are Polish-corpus
    # items in this pilot's numbering; the Phase-8S frozen flag lists in-corpus PL = 13,
    # which matches: Q1, Q2, Q3, Q14-Q22.
    ("Q1", "What is SEVerA and how does it relate to self-evolving agents?",
     ["00_severa_verified_synthesis_of_self_evolving_agent"]),
    ("Q2", "What trust tiers does this lab use for evidence, and what does tier 3 mean?",
     ["00_okf_methodology_research"]),
]

IN_CORPUS_EN = [
    ("Q6", "What are the core structures of agent memory hierarchies?",
     ["00_agent_memory_hierarchies"]),
    ("Q7", "How do agent execution hooks provide deterministic loop interception and guardrails?",
     ["00_agent_execution_hooks_guardrails"]),
    ("Q8", "What is the isolate build prove ship methodology in software factories?",
     ["00_00_software_factory_isolate_build_prove_ship"]),
    ("Q9", "How does the engineering workspace function as an adaptive search environment?",
     ["00_adaptive_search_workspace_architecture"]),
    ("Q10", "What are the key version control paradigms and git discipline patterns for autonomous agents?",
     ["00_agentic_git_discipline_patterns"]),
    ("Q11", "How is modular graph structured in agentic RAG?",
     ["00_agentic_rag_modular_graph"]),
    ("Q12", "What is the CRITIC framework for verify-then-correct with external tools?",
     ["00_07_critic_external_tool_verification"]),
    ("Q13", "How does lesson persistence and eviction work in ExpeL?",
     ["00_08_lesson_persistence_eviction_requirement"]),
]

OOC_PL = [
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?", []),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?", []),
    ("Q23", "Jaka będzie prognoza pogody w Warszawie jutro o 14:00?", []),
    ("Q24", "Jaki jest tradycyjny przepis na domowe pierogi ruskie?", []),
    ("Q25", "Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia?", []),
]

CANARY = json.loads((ROOT / "eval" / "canary.json").read_text(encoding="utf-8"))["questions"]
CANARY = [(c["qid"], c["text"], []) for c in CANARY]

# --- LLM translations (agent of this session; these ARE the experiment) ---
# Baseline PL question -> translated EN question.

TRANSLATIONS = {
    # in-corpus PL (the 10 that are actually PL; Q1/Q2 are already EN and are not translated)
    "Q3": "What are the methods for compressing AI agent sessions?",
    "Q14": "What is agentic engineering and how does it lead from chaos to deliberate design?",
    "Q15": "Why is reinventing the wheel in vibe coding a problem?",
    "Q16": "What are the techniques for squeezing 2-3x efficiency out of AI in coding?",
    "Q17": "How does graph-based tool routing with self-healing work?",
    "Q18": "What is message passing used for in the analysis and resilient design of self-healing systems?",
    "Q19": "How does distributed change detection with Byzantine fault tolerance work?",
    "Q20": "What characterizes energy-efficient federated learning with quantization?",
    "Q21": "What does the taxonomy of agent errors and debugging frameworks look like?",
    "Q22": "How is low-overhead fault tolerance for quantum universality implemented?",
    # OOC PL
    "Q4": "What entry did session 04 add to SCARS.md regarding CRLF (scar R13)?",
    "Q5": "What did Jan Kowalski say at the meeting on 2026-09-15?",
    "Q23": "What will be the weather forecast in Warsaw tomorrow at 14:00?",
    "Q24": "What is a traditional recipe for homemade Russian pierogi?",
    "Q25": "What was the score in the last volleyball match Poland - Brazil?",
    # Canary
    "CANARY_01": "What is the phone number of the HR department of XYZ company?",
    "CANARY_02": "When was Krystyna from Sierpc born?",
    "CANARY_03": "How much does a monthly public transport ticket cost in Atlantis?",
    "CANARY_04": "What is the VAT number (NIP) of Widmo Sp. z o.o. company?",
    "CANARY_05": "Give the geographic coordinates of the city of Eldoria.",
}


def run_question(pytanie: str, oracle: list[str]):
    """Run the frozen pilot pipeline on one question; return per-question metrics."""
    plan = g.zbuduj_plan(pytanie)
    plan.uzyj_wektorow = True  # same config as extended_eval.py / run_and_save.py
    wyniki = g.retrieve(plan, [])
    ranked = [w["id"] for w in wyniki]
    mrr = g.mrr_at_k(oracle, ranked, K) if oracle else None
    rec = g.recall_at_k(oracle, ranked, K) if oracle else None
    pokryte = g.oblicz_pokrycie(wyniki, plan.slowa_kluczowe)
    wynik = g.syntezuj_odpowiedz(pytanie, pokryte)
    odmowa = bool(wynik.get("odmowa"))
    return {
        "mrr": mrr,
        "recall": rec,
        "refusal": odmowa,
        "top5": ranked[:K],
        "n_wynikow": len(wyniki),
    }


def group_metrics(rows: list[dict]) -> dict:
    mrrs = [r["mrr"] for r in rows if r["mrr"] is not None]
    recs = [r["recall"] for r in rows if r["recall"] is not None]
    refusals = [r["refusal"] for r in rows]
    out = {
        "n": len(rows),
        "n_refusal": sum(1 for x in refusals if x),
        "n_nonrefusal": sum(1 for x in refusals if not x),
    }
    if mrrs:
        out["mrr"] = sum(mrrs) / len(mrrs)
        out["recall"] = sum(recs) / len(recs)
        out["mrrs"] = mrrs
        out["recs"] = recs
    return out


def main() -> int:
    results = {"generated_by": "phase10a_measure.py (read-only use of frozen pilot)",
               "K": K}

    # --- in-corpus PL: baseline (original text) and translated (EN) ---
    rows_base, rows_tr = [], []
    for qid, q, oracle in IN_CORPUS_PL:
        qid_base = f"PL_{qid}"
        rows_base.append({"qid": qid_base, "question": q, **run_question(q, oracle)})
        if qid in TRANSLATIONS:
            qen = TRANSLATIONS[qid]
            rows_tr.append({"qid": f"PLT_{qid}", "question": q, "translated": qen,
                            **run_question(qen, oracle)})
        else:
            # Q1/Q2 are already English; "translated" = identical (control, no translation)
            rows_tr.append({"qid": f"PLT_{qid}", "question": q, "translated": q,
                            **run_question(q, oracle)})
    results["in_corpus_pl_baseline"] = rows_base
    results["in_corpus_pl_translated"] = rows_tr
    results["in_corpus_pl_metrics"] = {
        "baseline": group_metrics(rows_base),
        "translated": group_metrics(rows_tr),
    }

    # --- OOC PL ---
    rows_base, rows_tr = [], []
    for qid, q, oracle in OOC_PL:
        rows_base.append({"qid": qid, "question": q, **run_question(q, oracle)})
        rows_tr.append({"qid": f"T_{qid}", "question": q, "translated": TRANSLATIONS[qid],
                         **run_question(TRANSLATIONS[qid], oracle)})
    results["ooc_pl_baseline"] = rows_base
    results["ooc_pl_translated"] = rows_tr
    results["ooc_pl_metrics"] = {
        "baseline": group_metrics(rows_base),
        "translated": group_metrics(rows_tr),
    }

    # --- Canary ---
    rows_base, rows_tr = [], []
    for qid, q, oracle in CANARY:
        rows_base.append({"qid": qid, "question": q, **run_question(q, oracle)})
        rows_tr.append({"qid": f"T_{qid}", "question": q, "translated": TRANSLATIONS[qid],
                         **run_question(TRANSLATIONS[qid], oracle)})
    results["canary_baseline"] = rows_base
    results["canary_translated"] = rows_tr
    results["canary_metrics"] = {
        "baseline": group_metrics(rows_base),
        "translated": group_metrics(rows_tr),
    }

    # --- in-corpus EN (control, measured once, no translation) ---
    rows_en = []
    for qid, q, oracle in IN_CORPUS_EN:
        rows_en.append({"qid": qid, "question": q, **run_question(q, oracle)})
    results["in_corpus_en_control"] = rows_en
    results["in_corpus_en_metrics"] = group_metrics(rows_en)

    out_path = OUT_DIR / "phase10a_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- human-readable summary ---
    def fmt_group(m: dict, label: str) -> list[str]:
        lines = [f"{label}: n={m['n']}"]
        if "mrr" in m:
            lines.append(f"  MRR@5={m['mrr']:.3f} Recall@5={m['recall']:.3f}")
        lines.append(f"  refusal={m['n_refusal']}/{m['n']}")
        return lines

    lines = ["== PHASE 10A MEASUREMENT SUMMARY ==", ""]
    for m, lab in [(results["in_corpus_pl_metrics"]["baseline"], "In-corpus PL baseline"),
                   (results["in_corpus_pl_metrics"]["translated"], "In-corpus PL translated"),
                   (results["ooc_pl_metrics"]["baseline"], "OOC PL baseline"),
                   (results["ooc_pl_metrics"]["translated"], "OOC PL translated"),
                   (results["canary_metrics"]["baseline"], "Canary baseline"),
                   (results["canary_metrics"]["translated"], "Canary translated"),
                   (results["in_corpus_en_metrics"], "In-corpus EN control")]:
        lines.extend(fmt_group(m, lab))
        lines.append("")
    summary_text = "\n".join(lines)
    (OUT_DIR / "phase10a_summary.txt").write_text(summary_text, encoding="utf-8")
    print(summary_text)
    print(f"ARTIFACTS: {out_path}")
    print("PHASE10A_MEASURE_DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
