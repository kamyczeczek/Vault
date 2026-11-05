---
type: Concept
title: references
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# References — Graph Brain for Project-Wide Knowledge, Fast Problem Detection & Direction

All URLs fetched 2026-09-11 via `agent-reach` / Exa unless marked `local:`. Access date is fetch date.

## Primary sources — live code graphs queried via Exa

- rosshhun/graphy (GitHub) — code intelligence engine: 15-phase pipeline, GIR IR, 20 node / 17 edge types, hybrid BM25+fuzzy search, taint/dead-code/hotspots, MCP server + web dashboard (Sigma.js), 13 languages. URL: https://github.com/rosshhun/graphy
- OpenCortex (peter-j-thompson/opencortex) — structural intelligence: symbols / call graph / communities (label propagation) / cross-community dependencies / execution flows. URL: https://github.com/peter-j-thompson/opencortex
- GitNexus (Joaquin-Boilet/gitnexus) — zero-server graph+vector, KuzuDB WASM + transformers.js (snowflake-arctic-embed-xs, 22M), 7-phase indexing, Leiden clustering, confidence-scored CALLS, hybrid BM25+semantic+1-hop + RRF, worker-thread parallel parsing. URL: https://github.com/Joaquin-Boilet/gitnexus
- CodeGraph (ChrisRoyse/CodeGraph) — Neo4j-backed universal code intelligence: two-pass AST, cross-language analysis, MCP (Neo4j Cypher translate) + Neo4j schema management. URL: https://github.com/chrisroyse/codegraph
- graphify (gomoblaqo-faris/graphify) — multimodal (code+docs+papers+images) — deterministic AST (19 langs via tree-sitter) + Claude-inferred semantic edges, Leiden, confidence-tagged EXTRACTED/INFERRED/AMBIGUOUS, SHA256 cache, PreToolUse hook wiring. URL: https://github.com/gomoblaqo-faris/graphify
- CKB (TechCodinz/CKB) — CKB/MCP: 6 langs, graph + freshness delta, causal path / failure cone, architecture heartbeat (Code DNA), Louvain+dwell, SARIF/JUnit output. URL: https://github.com/TechCodinz/CKB
- grafel (cajasmota/grafel) — 50+ langs, 22 MCP tools, HTTP/path/message-bus/IaC/Solidity/Terraform surfaces, single `.graph.fb` in-memory graph, dashboard :47274. URL: https://github.com/cajasmota/grafel
- Cognee CodeGraph (docs.cognee.ai/examples/code-assistants) — Python CodeGraph: functions/classes/modules/services/configs + Who-calls-what/imports/version-history/ownership/semantic links, graph skeleton → triplets + LLM enrichment. URL: https://docs.cognee.ai/examples/code-assistants
- codebase-memory-mcp (moctes/codebase-memory-mcp) — C/Rust: kernel 28M LOC 3 min (2.1M nodes/4.9M edges), 66 langs, 14 MCP tools, Louvain, HTTP linking, 99.2% token reduction. URL: https://github.com/moctes/codebase-memory-mcp
- coregraph (simplecore-inc/coregraph) — Rust + tree-sitter + stack-graphs, IPC daemon + MCP/LSP/HTTP, confidence-tagged edges, token-budgeted LLM rendering (8000/2000/16000), monorepo-native, inconsistency categories (enum/api-path/config-key/doc-drift). URL: https://github.com/simplecore-inc/coregraph
- codegraph-rust (gavlooth/codegraph-rust) — Rust, SurrealDB, tiered indexing (fast/balanced/full), LSP-aware tiers (rust-analyzer/pyright/tsserver/gopls/jdtls/clangd), 4 agentic tools (context/impact/architecture/quality). URL: https://github.com/gavlooth/codegraph-rust
- slop0 (berkantay/slop0) — Go, deterministic quality rubric: 100+ rules, 6 graph algorithms (Brandes, Tarjan, Louvain, topological layering, DSM), LSP-typed where available. URL: https://github.com/berkantay/slop0
- code-graph-mcp (sdsrss/code-graph-mcp) — TypeScript/SQLite: AST (10 langs full), BM25+vector+RRF, Merkle incremental, 6 tools (project_map/search/ast_search/get_ast_node/get_call_graph/refs), this-param constructor nuance documented. URL: https://github.com/sdsrss/code-graph-mcp
- ast-graph (quocln/ast-graph) — tree-sitter + SQLite/FalkorDB pluggable backends, confidence-tiered edges, 10 CLI/MCP tools, AST compression, cross-file qualified `ClassName.method` resolution. URL: https://github.com/quocln/ast-graph
- ttsc Code Graph MCP (@ttsc/graph) — TypeScript-native: compiler-resolved (type checker) graph, graph shards + content-addressed manifest, declaration-shape closure, outside-boundary de-ranking, bound truncation accounting. URL: https://ttsc.dev/docs/graph/

## Primary sources — git-indexed daemons & pipelines (Exa page fetches)

- GitNexus — Indexing Pipeline (6 phases, KuzuDB, chunked byte-budget, worker threads) — https://abhigyanpatwari-gitnexus.mintlify.app/concepts/indexing-pipeline
- GitNexus — Architecture (multi-label schema: File/Code/Community/Process/CodeEmbedding; 7 smart tools) — https://abhigyanpatwari-gitnexus.mintlify.app/advanced/architecture
- GitCortex (bharath03-a/GitCortex) — branch-aware KuzuDB graph, git-hook incremental (<500 ms), `GraphStore` trait boundary, Windows/KuzuDB MSVC note. URL: https://github.com/bharath03-a/gitcortex
- Lattice (iAmLakshya/Lattice) — Memgraph + Qdrant, adaptive hybrid RRF (graph 0.8→0.2 by intent), multi-hop scoring with distance decay, 7 MCP tools. URL: https://github.com/iAmLakshya/Lattice
- Infigraph — ARCHITECTURE.md (KuzuDB columnar, 62 langs, SHA-256 incremental, model2vec 256-dim, 59 MCP tools). URL: https://github.com/intuit/infigraph/blob/843eeb48/ARCHITECTURE.md
- Infigraph — docs/CODE-PARSING.md (entities.scm/relations.scm, Parquet bulk load, incremental hashing, multi-repo groups with prefixed IDs + cross-repo resolve). URL: https://github.com/intuit/infigraph/blob/843eeb48/docs/CODE-PARSING.md
- TheYellowDuck/RAG-codebase — AST-boundary chunking (tree-sitter) + hybrid dense+BM25+RRF + code graph + PageRank + HNSW + LLM-judge faithfulness + rigorous eval harness (164 golden, bootstrap CIs). URL: https://github.com/TheYellowDuck/RAG-codebase
- tahasiddiquii/hybrid-graph-rag — BM25+dense+RRF + property-graph BFS (BEIR SciFact 5,183 / 300 q), weighted-RRF lesson (0.7/0.3), offline determinism. URL: https://github.com/tahasiddiquii/hybrid-graph-rag
- Graph Memory — concepts/search.md (hybrid BM25+vector → RRF → BFS `Contains:0.95 / Extends:0.85 / Imports:0.70` decay, per-graph search tools). URL: https://github.com/graph-memory/graphmemory/blob/main/site/docs/concepts/search.md
- CodeJury — backend/app/services/knowledge/retriever.py (`fuse → expand → refine → rerank → snippets`, weighted RRF `dense+ ≥2×` measurement 8/10 vs 6/10, per-stage disclosure). URL: https://github.com/krishagarwal314/CodeJury/blob/b235cad3/backend/app/services/knowledge/retriever.py

## Papers (Exa)

- CGFuse — Deep Graph-Language Fusion for Structure-Aware Code Generation (arxiv 2605.03689) — AST+data-flow graph → GNN node-classification pre-training → intermediate-layer cross-attention fusion; 9 PLMs × 3 GNNs, +10-16% BLEU / +6-11% CodeBLEU. URL: https://arxiv.org/html/2605.03689
- Code Graph Model (CGM) — Graph-Integrated LLM for Repository-Level Tasks (OpenReview 2025-09-18, no-agent open-source graph LLM). URL: https://openreview.net/forum?id=b98ODdeYq5
- GraphCodeAgent — Dual Graph-Guided LLM Agent: Requirement Graph (RG) + Structural-Semantic Code Graph (SSCG) + SSCGTraverse multi-hop. URL: https://arxiv.org/html/2504.10046
- GNN-Coder — Boosting Semantic Code Retrieval with Combined GNN-Transformer + ASTGPool (tree-aware pooling) (arxiv 2502.15202). URL: https://arxiv.org/html/2502.15202v1
- GRACE — Graph-Guided Hierarchical Code Fusion: repo/module/function multi-level hybrid graph + HGR retriever + dual node-feature/structure fusion + semantic graph serialization. URL: https://arxiv.org/html/2509.05980v1
- GraphPyRec (Sci. Comput. Program. 238, 2024, doi:10.1016/j.scico.2024.103166) — Python graph recommendation over semantic+dynamic graph (GGNN+BERT, 1M LOC corpus). URL: https://dl.acm.org/doi/10.1016/j.scico.2024.103166

## Sourcegraph / Cody (context-retrieval doctrine)

- Cody Context docs (keyword search + Sourcegraph Search + Code Graph as sources; user @mention + OpenCtx). URL: https://sourcegraph.com/docs/cody/core-concepts/context
- How Cody understands your codebase (RAG vs fine-tuning, BM25+signal-tuned ranking, removing embeddings at Enterprise due to freshness/scale). URL: https://sourcegraph.com/blog/how-cody-understands-your-codebase
- The anatomy of an AI coding assistant (per-feature context fetching: chat vs autocomplete vs test-gen vs edit; planning→retrieval→generation→post-processing). URL: https://sourcegraph.com/blog/anatomy-of-a-coding-assistant
- The lifecycle of a code AI completion (four-step: planning with Tree-sitter syntax bucketing, sliding-window Jaccard over editor context, post-processing truncation via Tree-sitter; latency under 1 s). URL: https://sourcegraph.com/blog/the-lifecycle-of-a-code-ai-completion
- AI-assisted Coding with Cody: Lessons from Context Retrieval & Evaluation (Hartman et al., KDD?/doi:10.1145/3640457.3688060 — candidate generation + pointwise ranker + crowdsourced eval, dual-stage recall→precision). URL: https://doi.org/10.1145/3640457.3688060
- The "Normsky" architecture (Beyang Liu + Steve Yegge, Latent Space, 2023-12-14) — Non-Agentic Rapid Multi-Source Code Intelligence; SCIP as "better LSIF"; latency discipline for autocomplete. URL: https://www.latent.space/p/sourcegraph

## Local context (not internet — workspace brains & docs)

- local: RESEARCH/2026-09-03_knowledge-architecture-research/findings.md — Q1/Q2/Q3 brains-vs-injection-vs-hooks commission, Glitch Cat Club graph-memory-starter two layers (rag vs graph), injection via hooks.json `additionalContext` (recursive CTE, FTS+fastembed 67 MB).
- local: brains/CONTEXT.md — brain vs native memory boundary, multi-brain routing (`brain_router.md`), skills_brain + reflection_brain as injection-signal brains, TS-brain chunk doctrine.
- local: brains/brain_router.md — registry table (ICM / TS / skills / reflection).
- local: MONITORING/reflection/reflection_index.json — 75 files, 139 scars, procedural families (D2/R-05).
