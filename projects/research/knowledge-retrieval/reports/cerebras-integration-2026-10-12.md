---
type: Concept
title: cerebras-integration-2026-10-12
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# Cerebras integration assessment — 2026-10-12

## Status
**BLOKADA (częściowa) — IDF i age decay nie dodane; źródło pierwotne Cerebras niedostępne (HTTP 500).**

Pomiarowa część zadania (Recall@1/3/10 + MRR) wykonana. Główne zadanie integracyjne (§1.4 instrukcji: dodanie IDF i age decay) nie zostało wykonane.

## Executive result

GraphRAG was measured with the Cerebras-style reported retrieval metrics, without changing the retriever, questions, thresholds, or embedding model.

Source output: `pilots/graphrag/eval/cerebras_metrics_output.txt`.

```text
IN-CORPUS (n=33): Recall@1=0.159 Recall@3=0.417 Recall@10=0.515 MRR=0.303 MRR@5=0.295 Recall@5=0.455
OOC refusal (n=15): 100.0%
BOUNDARY refusal (n=10): 50.0%
FALSE REFUSAL in-corpus (n=33): 48.5%
```

`MRR` is calculated over the top 10 ranks, matching the requested Cerebras-style MRR reporting; `MRR@5` is retained for continuity with the frozen GraphRAG pilot. No new acceptance threshold was introduced.

## Confrontation table

| Component | Cerebras reference status | GraphRAG observed state | Action this session |
|---|---|---|---|
| Metrics | Recall@1/3/10 + MRR | Previously MRR@5 + Recall@5 | Added Recall@1, Recall@3, Recall@10, and MRR to `measure_trust_set.py`; retained legacy fields |
| RRF `k` | Local research evidence reports `k=60`, contribution `1/(60+rank)` | `rrf_fuse(..., k=60)`, 1-indexed ranks | Match confirmed; no change |
| FTS | Full-text retrieval | SQLite FTS5 | Match at the conceptual level; Cerebras production implementation was not locally available |
| IDF | Described in secondary/local Cerebras material | No explicit GraphRAG IDF layer; FTS5 ranking is delegated to SQLite | Not added: exact Cerebras formula/weight was not verified |
| Age decay | Described as recency/source-authority weighting | No age-decay term in GraphRAG | Not added: exact published formula was not verified |
| Rerank | Cerebras reports LLM rerank as a later pipeline stage | No LLM reranker | Not added: official implementation and reproducible local setup were unavailable |
| Embeddings | Dragon-DocChat encoders are public on Hugging Face | `paraphrase-multilingual-MiniLM-L12-v2` | Not substituted: no verified Polish-corpus comparison was run |
| Per-source cap / recency tie-break | Claimed in the supplied task description, not verified from official code | No verified analogous cap/age tie-break in current GraphRAG RRF | Not changed without primary source evidence |

## Comparison with Cerebras P1–P4 (explicit head-to-head)

Cerebras figures below are the **user-supplied context from the task instruction** (unverified in this session; official Results Appendix returned HTTP 500). They are included here explicitly because the review correctly requires the confrontation to be named, not implied.

| System / stage | Reported MRR | Reported Recall@1 | Reported test-set size |
|---|---|---|---|
| Cerebras hybrid (P3) | 0.57 | 0.39 | 31 |
| Cerebras hybrid + LLM rerank (P4) | 0.90 | 0.87 | 31 |
| **GraphRAG hybrid (this session)** | **0.303** | **0.159** | **33** |

Gap (same metric family, different corpora — not a controlled benchmark):
- GraphRAG MRR is ~1.9× lower than Cerebras hybrid P3 (0.303 vs 0.57).
- GraphRAG Recall@1 is ~2.5× lower than Cerebras hybrid P3 (0.159 vs 0.39).
- GraphRAG is ~3× lower than Cerebras P4 on both metrics.

The honest reading: **GraphRAG's hybrid is substantially weaker than the reported Cerebras hybrid on its corpus**, even before reranking. Because corpora, languages, questions, oracle definitions, and refusal policies differ, this is a directional signal, not a benchmark defeat. The component-level suspects (in order of falsifiability) are: embedding model / preprocessing for PL, FTS5 ranking vs their BM25-lite, and the absence of IDF/age-decay signals. None of these was isolated in this session.

### Recall@10 = 0.515 — first-stage alarm

The oracle reaches top-10 in only about half the in-corpus cases (0.515). **No reranker fixes missing candidates**: a reranker reorders what retrieval returns, and with half the oracles absent at rank 10, the failure is at first-stage recall (FTS5/embedding coverage), not final ranking. This matches the review's point and is recorded here as an explicit open diagnostic, not a conclusion.


The requested Cerebras P1–P4 appendix was not directly retrievable in this session. The official/probable blog URL returned HTTP 500, and no appendix artifact exists in the active repository. Therefore the following supplied figures are recorded as **unverified user-provided context**, not as measured evidence from this session:

- hybrid P3 MRR: 0.57
- hybrid + LLM rerank P4 MRR: 0.90
- P4 Recall@1: 0.87
- reported test-set size: 31 questions

GraphRAG's measured values are not directly comparable as a benchmark score because the corpora, languages, questions, oracle definition, and refusal policy differ. The valid conclusion is methodological: GraphRAG now reports the same requested metric family, while its natural-question set still shows substantial ranking and abstention failures.

## Source and model assessment

### "17/20 vs 0/20" — disposition

The secondary video transcript archived at `projects/_archive/agentic-research-lab/knowledge/raw/Cerebras Second Brain.md` reports 17/20 correct with the knowledge base vs 0/20 without. **Disposition: rejected as evidence.** It is an unverified secondary transcript with no benchmark protocol, dataset, or reproducible harness, and it is not used anywhere in this report's conclusions. It is recorded here only so it does not hang in a vacuum (review point 5).

### Dragon-DocChat — decision, not deferral

The Hugging Face cards for both encoders are tagged English-only. **Decision: not applicable to this Polish corpus without a cross-lingual validation experiment.** The experiment was not run because (a) the EN-only tag disqualifies a drop-in swap, and (b) the blocked primary source (HTTP 500) leaves no verified PL procedure to follow. Owner question if this is ever revisited: run a paired MiniLM-vs-Dragon-DocChat measurement on the 33-question trust set after a local download and index rebuild.

Verified/reported source locations:

- Cerebras knowledge-base blog candidate: `https://www.cerebras.ai/blog/how-we-built-our-knowledge-base` (retrieval returned HTTP 500 during this session).
- Dragon-DocChat query encoder: `https://huggingface.co/cerebras/Dragon-DocChat-Query-Encoder`.
- Dragon-DocChat context encoder: `https://huggingface.co/cerebras/Dragon-DocChat-Context-Encoder`.
- Related Dragon paper: `https://arxiv.org/abs/2302.07452`.
- Local secondary material: `projects/_archive/agentic-research-lab/knowledge/raw/Cerebras Second Brain.md`.

The models are public, but availability alone does not establish that they outperform multilingual MiniLM on this Polish corpus. A valid substitution requires a controlled local download, index rebuild, and paired measurement; that experiment was not performed.

## Recommendation

1. Keep the metric extension: Recall@1/3/10 + MRR, with legacy MRR@5 for continuity.
2. Keep current GraphRAG retrieval frozen for this measurement; its RRF already matches the verified `k=60` formula.
3. Do not add IDF or age decay until Cerebras primary code or an exact reproducible formula is available; the local evidence only establishes the concepts, not implementation details.
4. Treat LLM reranking and Dragon-DocChat as separate future experiments requiring explicit availability and paired baselines, not as unverified drop-in fixes.

## not checked:

- Official Results Appendix P1–P4 tables and source code were not directly verified.
- Cerebras exact IDF formula, coefficients, and normalization were not verified.
- Cerebras exact age-decay function, `tau`, and source-authority combination were not verified.
- Dragon-DocChat was not tested on the Polish GraphRAG corpus.
- No LLM reranker was implemented or measured.
- No retrieval parameters, thresholds, questions, or models were changed in this measurement.
