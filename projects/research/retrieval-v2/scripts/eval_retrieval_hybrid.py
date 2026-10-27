"""Hybrid retrieval evaluation for retrieval-v2 using attune-rag HybridRetriever
+ sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2).
"""
import json
import sys
from pathlib import Path
import numpy as np

PILOT_ROOT = Path(__file__).resolve().parents[2] / "knowledge-retrieval" / "pilots" / "graphrag"
sys.path.insert(0, str(PILOT_ROOT))
import graphrag as g  # for metrics (mrr_at_k, recall_at_k)

from sentence_transformers import SentenceTransformer
from attune_rag import RagPipeline, DirectoryCorpus, KeywordRetriever
from attune_rag.embedding import EmbeddingRetriever
from attune_rag.hybrid import HybridRetriever

class STEncoder:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        print(f"Loading SentenceTransformer: {model_name}...")
        self.model = SentenceTransformer(model_name)
    def encode(self, texts):
        return np.asarray(self.model.encode(texts, show_progress_bar=False), dtype="float32")

CORPUS_DIR = Path(__file__).resolve().parents[1] / "corpus"
print(f"Loading corpus from {CORPUS_DIR}...")
corpus = DirectoryCorpus(CORPUS_DIR)

encoder = STEncoder()
embedding_retriever = EmbeddingRetriever(encoder=encoder)
keyword_retriever = KeywordRetriever(min_score=5.0)
hybrid_retriever = HybridRetriever(
    keyword=keyword_retriever,
    embedding=embedding_retriever,
    keyword_weight=1.0,
    embedding_weight=1.0,
    gate_threshold=5.0
)

pipeline = RagPipeline(corpus=corpus, retriever=hybrid_retriever)
K = 5

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

canary_path = PILOT_ROOT / "eval" / "canary.json"
CANARY = json.loads(canary_path.read_text(encoding="utf-8"))["questions"]
CANARY = [(c["qid"], c["text"], []) for c in CANARY]

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

print("Running Hybrid Evaluation...")
ic_pl = []
for qid, q, oracle in IN_CORPUS_PL:
    r = run_q(q, oracle)
    ic_pl.append({"qid": qid, "question": q, **r})

ooc_pl = []
for qid, q, oracle in OOC_PL:
    r = run_q(q, oracle)
    ooc_pl.append({"qid": qid, "question": q, **r})

canary_res = []
for qid, q, oracle in CANARY:
    r = run_q(q, oracle)
    canary_res.append({"qid": qid, "question": q, **r})

mrrs = [x["mrr"] for x in ic_pl if x["mrr"] is not None]
recs = [x["recall"] for x in ic_pl if x["recall"] is not None]
summary = {
    "in_corpus_pl": {
        "n": len(ic_pl),
        "n_refusal": sum(1 for x in ic_pl if x["refusal"]),
        "mrr": sum(mrrs)/len(mrrs) if mrrs else 0.0,
        "recall": sum(recs)/len(recs) if recs else 0.0,
    },
    "ooc_pl": {
        "n": len(ooc_pl),
        "n_refusal": sum(1 for x in ooc_pl if x["refusal"]),
    },
    "canary": {
        "n": len(canary_res),
        "n_refusal": sum(1 for x in canary_res if x["refusal"]),
    }
}

print(json.dumps(summary, indent=2))
out_path = Path(__file__).resolve().parent.parent / "reports" / "retrieval_v2_hybrid_results.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps({"summary": summary, "ic_pl": ic_pl, "ooc_pl": ooc_pl, "canary": canary_res}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"HYBRID EVAL DONE: {out_path}")
