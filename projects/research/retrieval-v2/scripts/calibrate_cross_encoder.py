"""Kalibracja cross-encodera jako drugiego etapu abstention.

Hybryda (Keyword + multilingual embedding) zwraca top-k kandydatów.
Cross-encoder (sdadas/polish-reranker-large-ranknet) ocenia każdą parę
query-document. Odrzucamy, gdy top-1 score cross-encodera < próg.

Próg kalibrujemy na zbiorach pozytywów (in-corpus) i negatywów (canary + OOC).
"""
import json
import sys
from pathlib import Path
import numpy as np
import torch.nn as nn

PROJECT = Path(__file__).resolve().parents[1]
WS = PROJECT.parents[2]
PILOT = WS / "projects" / "research" / "knowledge-retrieval" / "pilots" / "graphrag"
sys.path.insert(0, str(PILOT))
sys.path.insert(0, str(PROJECT / "scripts"))

import graphrag as g  # noqa: E402
from sentence_transformers import SentenceTransformer, CrossEncoder
from attune_rag import (
    RagPipeline, DirectoryCorpus, KeywordRetriever,
)
from attune_rag.embedding import EmbeddingRetriever
from attune_rag.hybrid import HybridRetriever
from calibration_sets import (
    POSITIVES_PL, POSITIVES_EN,
    NEGATIVES_CANARY, NEGATIVES_OOC_PL,
)

CORPUS = DirectoryCorpus(PROJECT / "corpus")
K = 5

class STEncoder:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        print(f"Loading SentenceTransformer: {model_name}...")
        self.model = SentenceTransformer(model_name)
    def encode(self, texts):
        return np.asarray(self.model.encode(texts, show_progress_bar=False), dtype="float32")

print("Initializing hybrid retriever...")
encoder = STEncoder()
embedding = EmbeddingRetriever(encoder=encoder)
keyword = KeywordRetriever(min_score=0.0)
hybrid = HybridRetriever(
    keyword=keyword,
    embedding=embedding,
    rrf_k=60,
    candidate_pool=20,
    keyword_weight=2.0,
    embedding_weight=1.0,
    gate_threshold=None,
)
pipeline = RagPipeline(corpus=CORPUS, retriever=hybrid)

print("Loading cross-encoder: sdadas/polish-reranker-large-ranknet...")
cross_encoder = CrossEncoder(
    "sdadas/polish-reranker-large-ranknet",
    default_activation_function=nn.Identity(),
    max_length=512,
)

def get_candidates(query, k=5):
    res = pipeline.run(query, k=k)
    return [h.template_path.replace(".md", "") for h in res.citation.hits]

def get_documents(query, k=5):
    res = pipeline.run(query, k=k)
    docs = []
    for h in res.citation.hits:
        path = PROJECT / "corpus" / h.template_path
        if path.exists():
            text = path.read_text(encoding="utf-8")[:1000]
            docs.append((query, text))
        else:
            docs.append((query, ""))
    return docs

def cross_encoder_score(query):
    pairs = get_documents(query)
    if not pairs:
        return 0.0
    scores = cross_encoder.predict(pairs)
    return float(max(scores)) if len(scores) > 0 else 0.0

print("Probing cross-encoder scores for positives and negatives...")
pos_scores = sorted(cross_encoder_score(q) for q in POSITIVES_PL + POSITIVES_EN)
neg_scores = sorted(cross_encoder_score(q) for q in NEGATIVES_CANARY + NEGATIVES_OOC_PL)

print(f"positives (n={len(pos_scores)}): min={pos_scores[0]:.3f} max={pos_scores[-1]:.3f}")
print(f"negatives (n={len(neg_scores)}): min={neg_scores[0]:.3f} max={neg_scores[-1]:.3f}")

separation = neg_scores[-1] < pos_scores[0]
print(f"Separation: {separation} (neg_max={neg_scores[-1]:.3f}, pos_min={pos_scores[0]:.3f})")

reports_dir = PROJECT / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

if not separation:
    idx = max(0, int(len(pos_scores) * 0.05))
    threshold_5pct = pos_scores[idx]
    print(f"WARNING: No clean separation. 5th percentile positives: {threshold_5pct:.3f}")
    print(f"Negatives above threshold: {sum(1 for s in neg_scores if s >= threshold_5pct)}/{len(neg_scores)}")
    print("STOP GATE: Cross-encoder also does not separate. Ścieżka 2 failed.")
    (reports_dir / "cross_encoder_calibration.json").write_text(
        json.dumps({
            "separation": False,
            "pos_min": float(pos_scores[0]),
            "pos_max": float(pos_scores[-1]),
            "neg_min": float(neg_scores[0]),
            "neg_max": float(neg_scores[-1]),
            "reason": "negatives max >= positives min — no clean threshold",
        }, indent=2),
        encoding="utf-8",
    )
    sys.exit(0)

threshold = (neg_scores[-1] + pos_scores[0]) / 2
print(f"CHOSEN cross-encoder threshold: {threshold:.3f}")

(reports_dir / "cross_encoder_calibration.json").write_text(
    json.dumps({
        "separation": True,
        "threshold": float(threshold),
        "pos_min": float(pos_scores[0]),
        "pos_max": float(pos_scores[-1]),
        "neg_min": float(neg_scores[0]),
        "neg_max": float(neg_scores[-1]),
    }, indent=2),
    encoding="utf-8",
)

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

def eval_group(questions, name):
    rows = []
    for qid, q, oracle in questions:
        ce_score = cross_encoder_score(q)
        refused = ce_score < threshold
        candidates = get_candidates(q)
        mrr = g.mrr_at_k(oracle, candidates, K) if oracle and not refused else (0.0 if oracle else None)
        rec = g.recall_at_k(oracle, candidates, K) if oracle and not refused else (0.0 if oracle else None)
        rows.append({
            "qid": qid, "question": q,
            "refusal": refused, "ce_score": ce_score,
            "top5": candidates, "mrr": mrr, "recall": rec,
        })
    refusals = sum(1 for r in rows if r["refusal"])
    mrrs = [r["mrr"] for r in rows if r["mrr"] is not None]
    recs = [r["recall"] for r in rows if r["recall"] is not None]
    summary = {
        "name": name, "n": len(rows),
        "n_refusal": refusals,
        "mrr": (sum(mrrs) / len(mrrs)) if mrrs else None,
        "recall": (sum(recs) / len(recs)) if recs else None,
    }
    print(f"{name}: n={len(rows)} refusal={refusals}/{len(rows)} "
          f"MRR={summary['mrr']} Recall={summary['recall']}")
    return {"summary": summary, "rows": rows}

res_ic_pl = eval_group(IN_CORPUS_PL_FULL, "in_corpus_pl")
res_ic_en = eval_group(IN_CORPUS_EN_FULL, "in_corpus_en")
res_ooc_pl = eval_group(OOC_PL_FULL, "ooc_pl")
res_canary = eval_group(CANARY_FULL, "canary")

results = {
    "in_corpus_pl": res_ic_pl,
    "in_corpus_en": res_ic_en,
    "ooc_pl": res_ooc_pl,
    "canary": res_canary,
}

out_results = reports_dir / "retrieval_v2_cross_encoder_results.json"
out_results.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"CROSS-ENCODER EVAL RESULTS SAVED: {out_results}")
print("CROSS_ENCODER_CALIBRATION_DONE")
