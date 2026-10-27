---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# retrieval-v2 — CONTEXT.md

grade: active

## Open work
- [x] Install attune-rag, multilingual embeddings, polish-reranker
- [x] Run hybrid retrieval evaluation (HybridRetriever + paraphrase-multilingual-MiniLM-L12-v2)
- [x] Calibrate dynamic abstention threshold for hybrid retrieval (Result: Path 1 gate_threshold calibration failed due to score overlap: positives min 1.0, max 14.0 vs negatives min 0.0, max 6.0; separation failure, STATUS: STOP GATE)

## Results (Hybrid Stack vs Graphrag Baseline)

| Metryka | Graphrag Baseline (Faza 8S) | Retrieval-v2 (HybridRetriever) |
|---------|-----------------------------|--------------------------------|
| In-corpus PL MRR@5 | 0.507 | **0.688** |
| In-corpus PL Recall@5 | 0.708 | **0.833** |
| OOC PL refusal | 5/5 (100%) | 0/5 (pure hybrid / RRF fallback) |
| Canary refusal | 5/5 (100%) | 0/5 (pure hybrid / RRF fallback) |

## Conclusion
Hybrid retrieval (attune-rag `HybridRetriever` with multilingual embeddings) substantially outperforms Graphrag baseline on in-corpus retrieval quality (MRR@5 0.688 vs 0.507, Recall@5 0.833 vs 0.708). However, pure embedding fusion without keyword confidence gating yields 0/5 refusals on OOC and canary queries. Path 1 (gate_threshold calibration) failed due to score overlap (positives min 1.0 vs negatives max 6.0). Path 2 (cross-encoder reranking / abstention) was evaluated as overengineering (~5.5 GB dependencies, slow inference, overlapping score distributions) and abandoned in favor of the frozen Graphrag baseline, which provides lightweight, reliable 100% refusal (5/5 on OOC and canary) without heavy ML dependencies.

## Status końcowy (2026-10-11)
- Ścieżka 1 (gate_threshold): FAIL — brak separacji (pos 1.0-14.0 vs neg 0.0-6.0)
- Ścieżka 2 (cross-encoder): ABORTED — overengineering (~5.5 GB, ~500 ms/query)
- Rekomendacja: powrót do graphrag (Ścieżka 3)

## Stan po sesjach DeepSeek (2026-10-11)
- v2 ewaluacji przygotowana (`frozen_eval_sets_v2.py`, 10/10 split)
- Pomiar v2 zablokowany przez shell (`0xC0000142`)
- Pełna instrukcja domknięcia: `RESUME_PROTOCOL.md`
- Stan pętli: `LOOP_STATUS.md`
- Otwarte: refusal 5/12 na in-corpus PL — artefakt czy realny problem?
