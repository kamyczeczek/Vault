---
type: Concept
title: GATES
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Gates: GraphRAG Trust Set & Semantic Gate Decision

OWNS: projects/research/knowledge-retrieval/pilots/graphrag/**

Scope: Execute Corpus Inventory (Phase A), Annotation Expansion (Phase B), Trust Set Measurement (Phase C), Interpretation & Owner Decision (Phase D), and Freeze (Phase E).

- [ ] G1: Corpus inventory script runs successfully and generates corpus_inventory.md with 30 selected nodes
  CHECK: python projects/research/knowledge-retrieval/pilots/graphrag/eval/_tmp_corpus_inventory.py
  EXPECT: === source_family ===
  EVIDENCE: pending

- [ ] G2: Verification script confirms all oracle IDs exist in graph.db
  CHECK: python projects/research/knowledge-retrieval/pilots/graphrag/eval/_tmp_verify_oracles.py
  EXPECT: Wszystkie oracle ID istnieją w korpusie
  EVIDENCE: pending

- [ ] G3: Trust set measurement runs successfully and outputs metrics
  CHECK: python projects/research/knowledge-retrieval/pilots/graphrag/eval/measure_trust_set.py
  EXPECT: ZBIORCZO
  EVIDENCE: pending

- [ ] G4: Artifact verification and integrity check pass
  CHECK: python projects/research/knowledge-retrieval/pilots/graphrag/eval/verify_artifacts.py
  EXPECT: Artifact verification passed
  EVIDENCE: pending
