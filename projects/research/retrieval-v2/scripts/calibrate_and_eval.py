"""Fast calibration and evaluation script for retrieval-v2.
Evaluates HybridRetriever with calibrated gate_threshold (6.0) + multilingual embeddings.
"""
import json
import sys
from pathlib import Path
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
WS = PROJECT.parents[2]
PILOT = WS / "projects" / "research" / "knowledge-retrieval" / "pilots" / "graphrag"
sys.path.insert(0, str(PILOT))
sys.path.insert(0, str(PROJECT / "scripts"))

import graphrag as g  # noqa: E402
from sentence_transformers import SentenceTransformer
from attune_rag import (
    RagPipeline, DirectoryCorpus, KeywordRetriever,
)
from attune_rag.embedding import EmbeddingRetriever
from attune_rag.hybrid import HybridRetriever

CORPUS = DirectoryCorpus(PROJECT / "corpus")
K = 5

class STEncoder:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        print(f"Loading SentenceTransformer: {model_name}...")
        self.model = SentenceTransformer(model_name)
    def encode(self, texts):
        return np.asarray(self.model.encode(texts, show_progress_bar=False), dtype="float32")

print("Initializing encoder and retrievers...")
encoder = STEncoder()
embedding = EmbeddingRetriever(encoder=encoder)

CHOSEN_THRESHOLD = 6.0

keyword = KeywordRetriever(min_score=CHOSEN_THRESHOLD)
hybrid_retriever = HybridRetriever(
    keyword=keyword,
    embedding=embedding,
    rrf_k=60,
    candidate_pool=20,
    keyword_weight=1.0,
    embedding_weight=1.0,
    gate_threshold=CHOSEN_THRESHOLD,
)
pipeline = RagPipeline(corpus=CORPUS, retriever=hybrid_retriever)

IN_CORPUS_PL_FULL = [
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

IN_CORPUS_EN_FULL = [
    ("Q6", "What are the core structures of agent memory hierarchies?", ["00_agent_memory_hierarchies"]),
    ("Q7", "How do agent execution hooks provide deterministic loop interception and guardrails?", ["00_agent_execution_hooks_guardrails"]),
    ("Q8", "What is the isolate build prove ship methodology in software factories?", ["00_00_software_factory_isolate_build_prove_ship"]),
    ("Q9", "How does the engineering workspace function as an adaptive search environment?", ["00_adaptive_search_workspace_architecture"]),
    ("Q10", "What are the key version control paradigms and git discipline patterns for autonomous agents?", ["00_agentic_git_discipline_patterns"]),
    ("Q11", "How is modular graph structured in agentic RAG?", ["00_agentic_rag_modular_graph"]),
    ("Q12", "What is the CRITIC framework for verify-then-correct with external tools?", ["00_07_critic_external_tool_verification"]),
    ("Q13", "How does lesson persistence and eviction work in ExpeL?", ["00_08_lesson_persistence_eviction_requirement"]),
]

OOC_PL_FULL = [
    ("Q4", "Jaki wpis dodala sesja 04 do SCARS.md w sprawie CRLF (blizna R13)?", []),
    ("Q5", "Co powiedzial Jan Kowalski na spotkaniu 2026-09-15?", []),
    ("Q23", "Jaka będzie prognoza pogody w Warszawie jutro o 14:00?", []),
    ("Q24", "Jaki jest tradycyjny przepis na domowe pierogi ruskie?", []),
    ("Q25", "Jaki padł wynik w ostatnim meczu siatkówki Polska - Brazylia?", []),
]

canary_path = PILOT / "eval" / "canary.json"
CANARY_RAW = json.loads(canary_path.read_text(encoding="utf-8"))["questions"]
CANARY_FULL = [(c["qid"], c["text"], []) for c in CANARY_RAW]

def run_q(query, oracle):
    res = pipeline.run(query, k=K)
    refused = res.fallback_used or res.confidence == 0.0 or len(res.citation.hits) == 0
    ranked = [hit.template_path.replace(".md", "") for hit in res.citation.hits]
    mrr = g.mrr_at_k(oracle, ranked, K) if oracle and not refused else (0.0 if oracle else None)
    recall = g.recall_at_k(oracle, ranked, K) if oracle and not refused else (0.0 if oracle else None)
    return {
        "refusal": refused,
        "mrr": mrr,
        "recall": recall,
        "top5": ranked[:K]
    }

def eval_group(items):
    rows = []
    for qid, q, oracle in items:
        r = run_q(q, oracle)
        rows.append({"qid": qid, "question": q, **r})
    mrrs = [x["mrr"] for x in rows if x["mrr"] is not None]
    recs = [x["recall"] for x in rows if x["recall"] is not None]
    summary = {
        "n": len(rows),
        "n_refusal": sum(1 for x in rows if x["refusal"]),
        "mrr": sum(mrrs)/len(mrrs) if mrrs else 0.0,
        "recall": sum(recs)/len(recs) if recs else 0.0,
    }
    return {"summary": summary, "rows": rows}

print("Running evaluation on calibrated pipeline (threshold=6.0)...")
res_ic_pl = eval_group(IN_CORPUS_PL_FULL)
res_ic_en = eval_group(IN_CORPUS_EN_FULL)
res_ooc_pl = eval_group(OOC_PL_FULL)
res_canary = eval_group(CANARY_FULL)

results = {
    "in_corpus_pl": res_ic_pl,
    "in_corpus_en": res_ic_en,
    "ooc_pl": res_ooc_pl,
    "canary": res_canary,
}

reports_dir = PROJECT / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

(reports_dir / "calibrated_threshold.json").write_text(
    json.dumps({
        "keyword_min_score": CHOSEN_THRESHOLD,
        "hybrid_gate_threshold": CHOSEN_THRESHOLD,
    }, indent=2),
    encoding="utf-8",
)

out_results = reports_dir / "retrieval_v2_calibrated_results.json"
out_results.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"CALIBRATED EVAL RESULTS SAVED: {out_results}")
print("IN_CORPUS_PL summary:", res_ic_pl["summary"])
print("OOC_PL summary:", res_ooc_pl["summary"])
print("CANARY summary:", res_canary["summary"])
print("CALIBRATION_DONE")
