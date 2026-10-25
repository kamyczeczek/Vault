---
type: Concept
flag: graphrag-phase8-semantic-coverage
since: 2026-10-11
owner: Mateusz
agent: pi-bolt
model: default
title: graphrag-phase8-semantic-coverage
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# Handoff Flag: GraphRAG Trust Set (55 questions) & Semantic Gate Decision (Wariant 1)

## State & Results
- **Corpus Inventory**: 10,373 nodes analyzed in `graph.db`, `corpus_inventory.md` created.
- **Annotated Test Set**: 55 questions in `eval/questions.md` (30 in-corpus across 6 source families, 15 out-of-corpus, 10 boundary).
- **Measurement**: `measure_trust_set.py` executed with Wariant 1 (calibrated `prog_cosine = 0.45`, hybrid FTS5 + MiniLM + RRF).
  - In-corpus (n=33): MRR@5 = 0.207 (baseline template structure), False Refusal = 0.0%
  - Out-of-corpus (n=15): Refusal = 100.0% (15/15)
  - Boundary (n=10): Refusal = 50.0% (5/10)
- **Pilot Frozen**: Trust set evaluation results saved in `trust_set_results.json` and `trust_set_report.md`. Pilot graphrag frozen with Wariant 1 calibrated threshold.
