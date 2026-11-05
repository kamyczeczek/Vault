---
type: Concept
source: "Architectural Reflection: Evaluating and Improving Our SQLite FTS5 Knowledge Graph"
title: graph_database_architectural_reflection
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Architectural Reflection: Evaluating and Improving Our Knowledge Graph Database

Our current knowledge graph architecture (`knowledge/graph/`) relies on a deterministic SQLite FTS5 database (`graph.db`) populated from canonical corpus markdown files. It builds nodes, sequence edges, source part-of edges, and shared-tag edges (`SHARES_TAG`), backed by strict verification gates (`watch.py`, `audit_workspace.py`).

While this minimalist design ensures deterministic zero-hallucination routing and lightning-fast execution, a critical architectural evaluation reveals three high-leverage improvement vectors to elevate agentic reasoning.

---

## 1. Current Strengths of the Graph Architecture
* **Zero External Dependencies:** Pure Python SQLite + FTS5 means zero heavy vector database infrastructure or complex cloud APIs required.
* **Deterministic Provenance:** Hashed corpus fingerprints (`.graph_fingerprint`) guarantee that the graph is always a 1:1 mathematical function of the corpus.
* **Tag-Intersection Routing:** Precise vocabulary-gated routing prevents noise and keeps agent context windows clean.

---

## 2. Proposed Architectural Improvements

### A. Explicit Citation Edges (`REFERS_TO`)
* **Current Limitation:** Edges are primarily built via chunk sequence (`SEQUENCE`) and shared metadata tags (`SHARES_TAG`). Direct backticked citations between corpus chunks (e.g., [`00_06_self_correction_grounding_requirement`]) are not materialized as graph edges.
* **Proposed Enhancement:** Parse backticked chunk IDs during graph building and insert explicit directed `REFERS_TO` edges. This enables true citation-chain traversal and orphan detection.

### B. Hybrid Search (FTS5 + Lightweight Embeddings)
* **Current Limitation:** FTS5 performs pure lexical keyword matching (BM25). If an agent queries a conceptual idea using synonyms that don't share exact keywords with corpus text, retrieval fails.
* **Proposed Enhancement:** Integrate a lightweight local embedding index (or SQLite vector extension) alongside FTS5 to enable hybrid keyword-plus-semantic vector retrieval.

### C. Incremental Graph Rebuilding
* **Current Limitation:** `build_graph.py` drops and rebuilds the entire SQLite database from scratch on every corpus modification.
* **Proposed Enhancement:** Implement file-hash tracking per chunk so the graph builder only re-parses and re-inserts modified or new corpus markdown files.
