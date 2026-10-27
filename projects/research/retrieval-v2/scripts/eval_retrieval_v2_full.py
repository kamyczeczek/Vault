"""Full evaluation of retrieval-v2 (attune-rag) on test questions from frozen pilot.
"""
import json
import sys
from pathlib import Path

PILOT_ROOT = Path(__file__).resolve().parents[2] / "knowledge-retrieval" / "pilots" / "graphrag"
sys.path.insert(0, str(PILOT_ROOT))
import graphrag as g  # for metrics calculation (mrr_at_k, recall_at_k)

from attune_rag import RagPipeline, DirectoryCorpus, KeywordRetriever

corpus = DirectoryCorpus(Path(__file__).resolve().parents[1] / "corpus")
pipeline = RagPipeline(corpus=corpus, retriever=KeywordRetriever(min_score=5))

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
    ("Q1", "What is SEVerA and how does it relate to self-evolving agents?",
     ["00_severa_verified_synthesis_of_self_evolving_agent"]),
    ("Q2", "What trust tiers does this lab use for evidence, and what does tier 3 mean?",
     ["00_okf_methodology_research"]),
]

OOC_PL = [
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?", []),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?", []),
    ("Q23", "Jaka będzie prognoza pogody w Warszawie jutro o 14:00?", []),
    ("Q24", "Jaki jest tradycyjny przepis na domowe pierogi ruskie?", []),
    ("Q25", "Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia?", []),
]

CANARY = json.loads((PILOT_ROOT / "eval" / "canary.json").read_text(encoding="utf-8"))["questions"]
CANARY = [(c["qid"], c["text"], []) for c in CANARY]

K = 5

def run_q(question, oracle):
    res = pipeline.run(question, k=K)
    refused = res.fallback_used or (len(res.citation.hits) == 0)
    ranked = [hit.template_path.replace(".md", "") for hit in res.citation.hits]
    mrr = g.mrr_at_k(oracle, ranked, K) if oracle else None
    recall = g.recall_at_k(oracle, ranked, K) if oracle else None
    return {
        "mrr": mrr,
        "recall": recall,
        "refusal": refused,
        "top5": ranked[:K]
    }

def group_metrics(rows):
    mrrs = [r["mrr"] for r in rows if r["mrr"] is not None]
    recs = [r["recall"] for r in rows if r["recall"] is not None]
    refusals = [r["refusal"] for r in rows]
    out = {
        "n": len(rows),
        "n_refusal": sum(1 for x in refusals if x),
    }
    if mrrs:
        out["mrr"] = sum(mrrs) / len(mrrs)
        out["recall"] = sum(recs) / len(recs)
    return out

def main():
    ic_pl = []
    for qid, q, oracle in IN_CORPUS_PL:
        ic_pl.append({"qid": qid, "question": q, **run_q(q, oracle)})

    ooc_pl = []
    for qid, q, oracle in OOC_PL:
        ooc_pl.append({"qid": qid, "question": q, **run_q(q, oracle)})

    canary = []
    for qid, q, oracle in CANARY:
        canary.append({"qid": qid, "question": q, **run_q(q, oracle)})

    results = {
        "in_corpus_pl": ic_pl,
        "in_corpus_pl_metrics": group_metrics(ic_pl),
        "ooc_pl": ooc_pl,
        "ooc_pl_metrics": group_metrics(ooc_pl),
        "canary": canary,
        "canary_metrics": group_metrics(canary),
    }

    out_path = Path(__file__).resolve().parent.parent / "reports" / "retrieval_v2_full_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results["in_corpus_pl_metrics"], indent=2))
    print(json.dumps(results["ooc_pl_metrics"], indent=2))
    print(json.dumps(results["canary_metrics"], indent=2))
    print(f"FULL EVAL DONE: {out_path}")

if __name__ == "__main__":
    main()
