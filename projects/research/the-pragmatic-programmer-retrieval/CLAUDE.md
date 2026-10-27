---
type: Concept
grade: candidate
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — the-pragmatic-programmer-retrieval

Local RAG & knowledge retrieval benchmark over "The Pragmatic Programmer" (20th Anniversary Edition).
Measures hybrid retrieval (FTS5 + FastEmbed + RRF), cross-encoder reranking, RAPTOR hierarchical summaries, and knowledge graph recall against a frozen gold set of 60 questions.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | Project entry file |
| `CONTEXT.md` | Contract (L1) | Current pipeline phase, open work, gates, evaluation results |
| `pragmatic-programmer.pdf` | Source (L2) | Input PDF monograph (497 pages, 9 chapters, 53 topics) |
| `starter/` | Input (L2) | Starter plans, reference gold set text, graph memory starter |
| `data/` | Artifacts (L3) | Extracted structure (`book_structure.json`), chunks (`chunks.json`), RAPTOR trees |
| `db/` | Database (L3) | `rag.db` (FTS5 BM25 + dense vectors), `graph.db` (entity-relation CTE graph) |
| `scripts/` | Tooling (L3) | Extraction, validation, chunking, hybrid recall, reranking, eval |
| `eval/` | Benchmark (L3) | Frozen gold sets (`gold_set_hard.json`, `gold_set_generated.json`) |
| `preflight.py` | Health (L0) | Standalone preflight test (stdlib only) |

## Route by intent

| Intent | Action / Command |
|---|---|
| Verify environment | `python preflight.py` |
| View plan & progress | `CONTEXT.md` |
| View original starter plan | `starter/plan_retrieval_z_ksiazki.txt` |

## Planned tooling

- `scripts/extract_structure_pdf.py` — Phase 0.1 PDF extraction to `data/book_structure.json`
- `scripts/validate_chunks.py` — Phase 0.3 hygiene & damaged chunks quarantine
- `scripts/chunk_semantic.py` — Phase 0.4 semantic paragraph chunking
- `scripts/build_hybrid.py` — Phase 1.1 FTS5 BM25 + FastEmbed vector index
- `scripts/recall_hybrid.py` — Phase 1.2 hybrid search + RRF fusion
- `scripts/rerank.py` — Phase 1.3 cross-encoder reranking
- `scripts/eval_retrieval.py` — Phase 2.2 retrieval metrics (recall@8, MRR)

## Rules

- Frozen gold set: queries and reference answers never change after index fingerprint freeze.
- Citation contract: retrieved chunks must carry chapter, topic, topic title, and book page.
- Stop gate at Phase 2: if `recall@8` and `MRR` meet target on hard set, stop at hybrid. Enter RAPTOR/Graph only if multi-hop recall fails.
