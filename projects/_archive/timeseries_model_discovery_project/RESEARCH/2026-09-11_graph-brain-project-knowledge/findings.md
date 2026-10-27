---
type: Concept
title: findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Findings — Graph Brain for Project-Wide Knowledge, Fast Problem Detection & Good Direction

Every claim cited. Primary sources fetched 2026-09-11 via `agent-reach` (Exa) unless marked `local:`.

---

## 0. What exists in this workspace today (local grounding, verified 2026-09-11)

| Layer | Where | What it does | How queried |
|---|---|---|---|
| `brains/icm_brain/` | `brains/icm_brain/rag.db` (SQLite FTS5, 117 chunks) | ICM methodology & workspace architecture | `python brains/icm_brain/ask.py "<q>"` |
| `brains/ts_brain/` | `brains/ts_brain/rag.db` (4 corpus chunks + auto leaderboard row) | h720 ETTh1 protocol, model registry, empirical findings | `python brains/ts_brain/ask.py "<q>"` |
| `brains/skills_brain/` | `skills_index.json` + digest in `.jcode/prompt-overlay.md` | Up-to-date skill knowledge + routing signal | auto-loaded every session |
| `brains/reflection_brain/` | `reflection_index.json` (75 files, 139 scars, 69 cards) + digest + memory cards | Scar/prevention-rule knowledge | auto-loaded every session; `ask.py "<q>"` |
| `MONITORING/KNOWLEDGE/problems/` | 26 problem files (all `recovered/closed`) | Problem lifecycle + no-circles finger-printing | `python PROCESS/check_problems.py check "<tokens>"` |
| `RESEARCH/` | 6 records (R-01..R-06) | Standalone research, deterministic routing | `RESEARCH/check_catalog.py` gate |

What is **missing**: a code-graph brain. Current brains index *prose* (markdown chunks) via FTS5 + passage windows. No AST, no call graph, no import graph, no community detection, no blast-radius tool. The three capabilities the user asked for (project omniscience / fast problem surfacing / direction recommendation) are not served by any current brain. The opportunity is to add a new brain that stores *code-derived structure* alongside *prose-derived knowledge*, with the same two desiderata the existing brains satisfy: (a) freshness-gated (fail-loud on staleness) and (b) auto-loaded + on-demand queryable.

---

## 1. What the web says good code-knowledge graphs look like (2024-2025 consensus)

### 1.1 The canonical pipeline (unanimous across projects)

Across Graphy, GitNexus, CodeGraph, GitCortex, Infigraph, CoreGraph, Cognee CodeGraph, and CKB the pipeline is the same, only tunings differ:

```
Source Files → Tree-sitter AST (parallel, rayon/worker threads)
  → Symbol table (Functions/Classes/Methods/Interfaces/Enums/Fields)
  → Import resolution (dotted paths, relative imports, crate maps)
  → Call tracing (type-aware disambiguation, confidence-scored)
  → Heritage (inheritance / implements / overrides)
  → Data-flow / taint (optional, language-conditional)
  → Community detection → Centrality / hotspots → Taint / dead-code → Persistence
```

* **Graphy**: 15-phase pipeline with explicit phase table (file discovery → structure → AST → import → call → phantom cleanup → LSP enhancement → heritage → type → data-flow → taint → complexity → communities → flows → dead code → change coupling) [Exa: rosshhun/graphy].
* **GitNexus**: 7-phase indexing (Structure → Parse → Imports → Calls → Heritage → Communities → Processes) with KuzuDB WASM / KuzuDB native, chunked 10 MB byte-budget, Leiden clustering, process tracing from entry points [Exa: gh AbhigyanPatwari GitNexus indexing-pipeline + architecture].
* **Infigraph**: Tree-sitter (59 langs) + ANTLR4 (3 langs) → cross-file call resolution → KuzuDB (columnar, Cypher-native, `COPY FROM CSV` bulk load, incremental via SHA-256 hash skip) → embeddings (Model2Vec) [Exa: intuit/infigraph ARCHITECTURE.md + CODE-PARSING.md].
* **CoreGraph**: Tree-sitter + stack-graphs (one `coregraph index` pass), IPC daemon, confidence-tagged edges, LSP + MCP + HTTP bridges, token-budgeted LLM rendering [Exa: simplecore-inc/coregraph].
* **code-graph-mcp / ast-graph**: Merkle-tree incremental, KuzuDB/SQLite/FalkorDB, recursive CTE traversals, confidence scores [Exa: sdsrss/code-graph-mcp, quocln/ast-graph].

**Lesson for this workspace:** the graph must be a *two-backend* asset from day one — SQLite for zero-dependency local operation, KuzuDB/FalkorDB as an opt-in fast path — because the Windows/KuzuDB native story is not clean yet (GitCortex documents MSVC link failure for KuzuDB 0.11.3 on Windows; Infigraph uses the `lbug` fork with a cmake dep). A SQLite-first core that can bulk-load into KuzuDB when available survives all hosts.

### 1.2 Node and edge types (convergence is tight)

* **20 node types** in Graphy (Module/File/Folder/Class/Struct/Enum/Interface/Trait/Function/Method/Constructor/Field/Property/Parameter/Variable/Constant/TypeAlias/Import/Decorator/EnumVariant); **17 edge types** (Contains, Calls, Imports, Inherits, Implements, Overrides, ReturnsType, ParamType, FieldType, Instantiates, DataFlowsTo, TaintedBy, CrossLangCalls, AnnotatedWith, CoupledWith, SimilarTo) [Exa: rosshhun/graphy].
* CoreGraph's edge set is the universal subset most graphs share: `CALLS`, `IMPORTS`, `EXTENDS`, `IMPLEMENTS`, `CONTAINS`, `REFERENCES`, `OVERRIDES`, `HANDLES_ROUTE`, `STEP_IN_PROCESS`, `ENTRY_POINT_OF` plus `confidence ∈ [0.5, 1.0]` per edge [Exa: quocln/ast-graph].
* **Infigraph 62 languages** is the current ceiling; most production graphs cover 6-15 (Graphy 13, GitNexus 11, code-graph-mcp 10 full + 6 smoke-tested). Each language is a separate `LanguagePack` with `entities.scm` + `relations.scm` tree-sitter queries feeding the same pipeline [Exa: Infigraph docs].

### 1.3 Framework awareness is TOML-driven, not hardcoded

Graphy ships 15 framework plugins as TOML configs (Express, Django, Rails, Spring Boot, React, Next.js, Laravel …) that tag entry points and route nodes so process tracing can start from handlers [Exa: rosshhun/graphy]. GitNexus scores entry points with framework detection; Infigraph supports 22 frameworks for HTTP route/endpoint extraction [Exa: Infigraph]. The pattern is: *declare frameworks in config, detect at index time, materialize `Route` and `Process` nodes with `HANDLES_ROUTE` / `STEP_IN_PROCESS` edges*. This workspace should follow the same doctrine — `projects(ts-ml-experiments)/.graph/frameworks/*.toml` rather than code changes.

### 1.4 Persistence & query surface

* **KuzuDB** is the plurality choice (GitNexus, Infigraph, CodeGraph/Neo4j, Lattice/Memgraph+Qdrant, ast-graph's FalkorDB option are the variants). Reason cited repeatedly: embedded, Cypher-native, single-file, variable-length path queries (`MATCH (a)-[:CALLS*1..5]->(b)`) for blast-radius without recursive CTE contortions [Exa: intuit/infigraph ARCHITECTURE.md].
* **SQLite** is the portability choice (code-graph-mcp, ast-graph, Infigraph incremental doc all show SQLite exists; graphy-core uses `redb` + `petgraph`). The right abstraction is a `GraphStore` trait with SQLite and KuzuDB backends so the host decides, not the code (GitCortex documents exactly this seam: "GraphStore trait is the extensibility boundary" [Exa: bharath03-a/GitCortex]).
* Query tools converge to 6-8 primitives: `symbol`, `call_chain`, `blast_radius`/`impact`, `hotspots`, `dead_code`, `search` (BM25), `routes`/`processes`, `query` (Cypher/SQL escape hatch) [Exa: quocln/ast-graph ten tools; sdsrss/code-graph-mcp six core tools]. Token budgets on the LLM rendering path are load-bearing (CoreGraph `--token-budget 8000/2000/16000`, with live counter; codebase-memory-mcp cites 99.2% / 120x token saving via graph) [Exa: simplecore-inc/coregraph + moctes/codebase-memory-mcp].

---

## 2. Extremely fast problem detection — how the graph earns its keep

### 2.1 Raw speed numbers (reported, not measured here)

* **Indexing:** Linux kernel (28 M LOC, 75K files → 2.1 M nodes / 4.9 M edges) in 3 min on codebase-memory-mcp's C pipeline; Django (49K nodes) ~6 s; GitCortex Django 520 K LOC full index ~4 s with sub-500 ms incremental diffs; CoreGraph ~280 files in 2.3 s; TheYellowDuck RAG-codebase Django 521 K LOC 84 s with AST-boundary chunking [Exa: moctes/codebase-memory-mcp, bharath03-a/GitCortex, simplecore-inc/coregraph, TheYellowDuck/RAG-codebase].
* **Queries:** Cypher <1 ms, name search <10 ms, dead-code scan ~150 ms, call-path BFS <10 ms on the kernel graph [Exa: moctes/codebase-memory-mcp]. These are *graph* times; the workspace's current FTS5 `ask.py` is comparable for prose, but for code the graph replaces `grep | read | follow import | grep` chains that cost seconds and tokens.

### 2.2 Incremental freshness is non-negotiable

The fast-detection promise is only credible if the graph is never stale.

* **File-hash gate**: every file's SHA-256 is stored on its `File`/`Module` node; on re-index only changed-file hashes mismatch → only those files are re-parsed and their nodes/edges `DETACH DELETE`d and reinserted; cross-file call resolution re-reads the full symbol table but only re-resolves callers from changed files [Exa: intuit/infigraph ARCHITECTURE.md — Incremental Indexing section; also sdsrss/code-graph-mcp Merkle hash, ast-graph `file_hashes` table].
* **Watchers / git hooks**: graphy `graphy-watch` (file watcher + incremental re-index), GitCortex `post-commit/post-merge/post-rewrite/post-checkout` hooks firing on HEAD change, code-graph-mcp filesystem watcher, Infigraph `watch_project` tool [Exa: rosshhun/graphy (Live watch mode), bharath03-a/GitCortex, sdsrss/code-graph-mcp, Infigraph].
* **Background daemon**: CoreGraph auto-spawns a daemon on first use, warm-loads snapshots when no file changed, self-terminates when idle — "fast repeat queries, no resident cost when unused" [Exa: simplecore-inc/coregraph].
* **Sync gossip**: Infigraph demonstrates multi-repo groups with a combined store built from per-repo Parquet exports and cross-repo edge resolution [Exa: Infigraph multi/ combined.rs]. Useful for this workspace's `projects/` fan-out.

**Implication for this workspace:** the graph brain must ship `graph-brain watch` and `graph-brain diff` as first-class commands. The pre-commit gate (`verify_graph_sync`) should compare stored file hashes to current hashes (fail-loud on staleness), mirroring `verify_sync.py` in `ts_brain` and `reflection_brain`.

### 2.3 What "find problems" decomposes into (with detectors per problem class)

| Problem class | Graph detector | Concrete signal | Representative source |
|---|---|---|---|
| **Dead code** | Orphan scan: zero incoming `CALLS` excluding entry points (`main`, `Route` handlers, `test_*`) | `orphans` / `dead-code` commands; probabilistic scoring with 13 heuristics in Graphy | [Exa: rosshhun/graphy `graphy dead-code`, simplecore-inc/coregraph `orphans`, quocln/ast-graph] |
| **Circular deps / architecture drift** | Tarjan SCC on file-import or call graph; Louvain/Leiden community vs declared layers | Package cycle detection, community-label → file-path mismatch (`Misplaced file` flag) | [Exa: TechCodinz/CKB, slop0 graph algorithms (Tarjan, Louvain)] |
| **God objects / hotspots** | Centrality: PageRank, betweenness, degree × complexity coupling; Louvain community overlap | `hotspots`, `Code DNA`, `centrality` ranked list; Infigraph `centrality` tool | [Exa: rosshhun/graphy hotspots, sdsrss/code-graph-mcp `project_map include_centrality`, slop0 `Graph Algorithms`] |
| **Inconsistencies** | Cross-file enum/API-path/config-key/doc-drift matchers over graph nodes | `inconsistencies --category enum-mismatch|api-path|config-key|doc-drift` with per-category tuning | [Exa: simplecore-inc/coregraph `inconsistencies`] |
| **Blast radius / regression risk** | Transitive `CALLS` BFS (depth-bounded) + `TESTED_BY` edges; risk scoring by caller count × centrality | `impact` / `blast_radius` / `diff` commands; GitCortex `gcx blast-radius` PR comment | [Exa: quocln/ast-graph `blast-radius`, bharath03-a/GitCortex] |
| **Layer violations** | Import-edge direction vs topological layer assignment (layer-skip edge = `L → L+2+`) | DSM matrix above-diagonal entries = violations | [Exa: slop0 — Topological Layer Assignment, DSM] |
| **Taint / security** | Source→sink propagation on `DataFlowsTo` / `TaintedBy` edges | `taint` tool; Graphy's taint analysis phase 9 | [Exa: rosshhun/graphy `graphy taint`] |

**Measured token leverage for problem detection:** codebase-memory-mcp documents 5 structural queries at ~3,400 tokens vs ~412,000 via file-by-file grep (99.2% reduction, 120x fewer tokens) [Exa: moctes/codebase-memory-mcp]. The workspace should budget for that same rendering discipline: `--min-confidence`, `--token-budget`, `--compact` on every query.

### 2.4 LSP enrichment vs pure tree-sitter (accuracy tradeoff)

* **Pure tree-sitter**: zero build-system dependency, fast, portable, but name-based resolution is approximate (confidence 0.5 on fuzzy fallback). Every project above defaults to this tier for indexing speed.
* **LSP-enhanced** (code-graph-rust `balanced`/`full`, slop0 optional `gopls/pyright/tsserver`, Graphy phase 5.7): adds type-aware disambiguation, interface satisfaction, and data-flow edges at the cost of requiring `rust-analyzer`, `pyright-langserver`, `typescript-language-server`, `gopls`, `clangd` at index time. code-graph-rust documents the explicit tradeoff table: `fast` (AST only) < `balanced` (LSP symbols + module linking) < `full` (all analyzers + LSP definitions + dataflow) [Exa: gavlooth/codegraph-rust Indexing tiers].
* The right default for this workspace is **tree-sitter-first with opt-in LSP**: ship the graph without build-system coupling, enable `--lsp` as an augment pass that annotates edges with higher confidence (mirrors Graphy's optional LSP phase and code-graph-rust's tiering).

---

## 3. Finding good direction for the next work — graph-native recommendation

### 3.1 The two retrieval channels and why both matter

Every mature code-RAG system now ships **hybrid retrieval**: BM25 (exact identifiers) + vector (vocabulary bridging) fused by **Reciprocal Rank Fusion (RRF)**, because neither channel alone dominates.

* **BM25 alone** wins on identifiers (`HTTPException`, `HTTPException`, `HTTPException`); **vectors alone** win on intent ("validate user input" → `authenticate_session`); RRF fuses them without score normalization.
* **Weighting is load-bearing:** CodeJury documents equal-weight RRF scoring 6/10 on 10 vocabulary-mismatch queries while dense alone scores 8/10 — BM25's confident-but-wrong top rank suppresses dense's correct 4th/5th. Weighting dense ≥2× restores 8/10 [Exa: krishagarwal314/CodeJury retriever.py `fuse`/`_rrf`]. TheYellowDuck's hybrid-graph-rag similarly shows symmetric RRF degrades nDCG when retrievers are unequal strength [Exa: tahasiddiquii/hybrid-graph-rag benchmark table].
* **Sources that adopted this verbatim:** Graph Memory (`hybrid BM25 + vector + RRF + BFS expansion`), RAG-codebase (`dense + BM25 + RRF + PageRank`), Infigraph (hybrid), CodeJury (hybrid + 1-hop expansion + ripgrep refine + rerank), Lattice (Memgraph + Qdrant, adaptive RRF weights 0.8/0.2 for structural queries, 0.2/0.8 for semantic) [Exa: abhigyanpatwari-gitnexus mintlify search, TheYellowDuck/RAG-codebase, krishagarwal314/CodeJury, iAmLakshya/Lattice].

**Design rule borrowed from CodeJury's honest pipeline factorization:** the retrieval primitive is **five stages, each switchable**, so its contribution is measurable rather than assumed: `fuse → expand (1-hop call-graph) → refine (ripgrep over identifiers) → rerank → snippets`. With all off it collapses to plain hybrid search, which is how you know whether graph expansion actually helped [Exa: krishagarwal314/CodeJury `retrieve_context` docstring]. This workspace's direction recommender must adopt the same stage-disclosed, toggle-per-stage design.

### 3.2 Reranking after fusion

* CodeJury and RAG-codebase both instrument **graph-aware rerankers**: personalized PageRank (PPR) over the call/import graph seeded by the fused hits. RAG-codebase shows `graph` rerank lifting recall@5 0.900 → 0.920 (overlapping CIs; conditional win: Go/cobra 0.824 → 0.941 p=0.019, Python/FastAPI null) [Exa: TheYellowDuck/RAG-codebase eval table]. CodeJury documents PPR but measures that the deterministic score across four incomparable score scales must not share a mixed pool's position rank [Exa: krishagarwal314/CodeJury `rerank._deterministic_score`].
* The current SOTA code embedder CodeRankEmbed mean nDCG@10 0.619 on the full CoIR leaderboard (beating Voyage-Code-002 0.563); **code-trained embeddings** matter more than model size — `st-codesearch-distilroberta-base` recall@5 0.95 vs general `all-MiniLM-L6-v2` 0.70 on the same FastAPI golden set [Exa: TheYellowDuck/RAG-codebase Embedder lever table].

### 3.3 Direction recommendation — three levels of graph reasoning (pick one per budget)

| Level | Mechanism | Input | Output | When to use | Source grounding |
|---|---|---|---|---|---|
| **L0 — Heuristic over graph health** | Score hotspots × dead-code × cycles × layer violations into a ranked remediation list | Heartbeat + hotspot + orphan + cycle detectors | `Next: extract module X from god-class Y (confidence 0.92)` | Immediate, zero LLM cost, deterministic, gateable | [Exa: moctes/codebase-memory-mcp `get_architecture` + `Code DNA`, slop0 `Graph Algorithms` (Brandes/Louvain/Tarjan/DSM)] |
| **L1 — LLM over curated graph evidence** | Agent tool with curated subgraph (BM25+vector→RRF→graph expansion→rerank→snippets), synthesis with citations | Retrieval pipeline output (ranked hits + 1-hop neighbors + snippets + notes) | Grounded proposal with `[[file:line]]` cites + failure cone | Default direction recommendation; balances cost and grounding | [Exa: krishagarwal314/CodeJury answer pipeline, sdsrss/code-graph-mcp MCP tools, Lattice synthesis with citations] |
| **L2 — GNN + LLM fusion** | Train a GNN on AST/CPG (AST + CFG + DFGmerged as a code graph) and fuse its embeddings into the LLM's intermediate layers at token level | AST-augmented data-flow graph per snippet → GNN node-classification pre-training → intermediate-layer cross-attention fusion | Up to +10-16% BLEU / +6-11% CodeBLEU over the same PLM without graph; sample-efficient (NL models match code models with fewer samples) | Research-grade, expensive, worthwhile only when generation quality dominates latency | [Exa: Deep Graph-Language Fusion — CGFuse framework (9 PLMs, 3 GNNs) + GNN-Coder (AST + GNN-integrated Transformer)] |

**Measured anchors:** CGFuse evaluated across 9 PLMs + 3 GNN architectures; every PLM improved, CodeT5-style most. GNN-Coder's tailored `ASTGPool` (pooling that respects AST child-count bias, unlike TopKPool/SAGPool) is the concrete GNN detail to lift if L2 is pursued [Exa: CGFuse paper §1-3, GNN-Coder paper §§Graph Pooling].

### 3.4 Sourcegraph / Cody's honest lesson (relevant to "good direction")

Sourcegraph originally shipped embeddings for Cody (OpenAI `text-embedding-ada-002` per chunk) and then **removed them** for Enterprise: sending code to an embedding processor, maintaining freshness, and vector-DB scale at 100K+ repos were net-negative vs their BM25 + Code Intelligence Platform (Kythe/SCIP/LSIF-derived graph) with BM25 ranking + signal tuning [Exa: sourcegraph/blog how-cody-understands-your-codebase + lifecycle of a code AI completion]. This is the correct warning for this workspace: **lean on the graph first, add vectors where measured wins justify the operational cost** (TheYellowDuck's measured win: BM25 adds +0.10 recall@5 on Django at 40K chunks; vectors alone insufficient for identifiers [Exa: TheYellowDuck/RAG-codebase Scale—Django row]).

---

## 4. The synthesis — what to build for this workspace (ranked, falsifiable)

### 4.1 Target shape: `brains/graph_brain/` as a first-class sibling to `ts_brain` / `reflection_brain`

Reuse the workspace's proven brain invariants verbatim — they already encode the self-correcting mechanics the web's best graphs independently converged on:

* **Deterministic build index**: `reflection_index.json` / `skills_index.json` → `graph_index.json` (files × symbols × edges × file hashes × fingerprint), same `fingerprint = sha256(files:hash …)[:12]` scheme.
* **Marker-delimited digest**: `SCAR-BRAIN-DIGEST` → `GRAPH-BRAIN-DIGEST` inside `.jcode/prompt-overlay.md` (auto-loaded every session, token-budgeted, newest-first). Pre-commit fails loud if digest ≠ fresh render.
* **Memory channel**: per-graph card seeded into Jcode native memory (project scope, `graph` tag) so the auto-recall surface that today's scars ride carries graph hotspots and direction nuggets without any code change to the harness.
* **Integrity gate**: `verify_graph_sync.py` checks index↔disk + digest↔fresh render + memory cards↔overlay, patterned on `verify_reflection_sync.py` / `verify_sync.py` (ts_brain). Also asserts file-hash freshness (no silent staleness à la GitCortex).

What the graph brain adds that the prose brains do not: **a code-derived node/edge store** plus **graph-native query tools** consumed by agents. The minimal viable substrate is the same three-table idiom that Glitch Cat Club's `graph-memory-starter` uses for its prose graph (Display: `select prompt, hops, top_k` → `recursive CTE` → `additionalContext` [local: `RESEARCH/2026-09-03_knowledge-architecture-research/findings.md` §2.1]), now for code.

### 4.2 Phased delivery that mirrors the web's measured rollout

| Phase | What ships | How quality is proved | Web precedent that this is the right phase |
|---|---|---|---|
| **P1 — Tree-sitter index + SQLite store + 7 tools (sub-second goals)** | `index` (parallel tree-sitter, SHA-256 incremental, confidence-tagged `CALLS`) → SQLite (`nodes/edges/file_hashes`) with optional KuzuDB bulk port → tools: `graph_lookup` (symbol + callers/callees + location), `graph_search` (BM25, RRF weights 1.0/dense≥2.0 tunable), `graph_call_chain`, `graph_blast_radius`, `graph_hotspots`, `graph_dead_code`, `graph_stats` → `MCP` surface (stdio) + CLI. All answers cite `file:line`. | kernel-style stressor (this repo's file count) indexed in <5 s; any symbol lookup <10 ms after warm load; `dead_code` and `blast_radius` ranked outputs compared to `grep` baseline on three real churns | [Exa: sdsrss/code-graph-mcp 7 tools + KuzuDB RAG, quocln/ast-graph 10 tools, slop0 Tarjan/Louvain/Brandes] |
| **P2 — Community + centrality + route tracing + watch + fast problem dashboard** | Louvain/Leiden on `CALLS`, betweenness/PageRank chokepoints, file `CONTAINS` rollup, `Route→Process→STEP_IN_PROCESS` tracing (framework TOML), file-watcher daemon (`graph-brain watch` / `--watch`), git-hook refresh, health dashboard (`graph health` — dead-code %, orphan rate, hotspot top-N, cycle list, layer-violation list) | `graph health` output is the single artifact the `check_problems.py`-class gate consumes; watcher re-indexes single-file change in <500 ms; `hotspots` matches `slop0` centrality top-k | [Exa: bharath03-a/GitCortex (hooks + per-branch), simplecore-inc/coregraph (daemon), rosshhun/graphy (hotspots + patterns), iAmLakshya/Lattice (hotspots + routes + docs linking)] |
| **P3 — Hybrid retrieval + direction recommender (L1)** | Embedder (sentence-transformers + code-trained model, e.g. `st-codesearch-distilroberta-base` or CodeRankEmbed) → HNSW optional → `fuse( BM25 + dense → weighted RRF ) → expand(1-hop call-graph, edge-decay 0.95/0.85/0.70) → refine(ripgrep over identifiers) → rerank(PPR + lexical + LLM-rerank --accurate)` pipeline with per-stage disclosure and toggling → `graph_recommend_direction` (grounded answer with citations + failure cone + ADR pointer) | Hybrid vs BM25-only delta on a workspace-labeled golden set (recall@5 with bootstrap CIs + significance test à la RAG-codebase `eval/`); payload cited per answer (`[[file:line]]`), and a `graph recall` mode that can operate without LLM when one isn't desired | [Exa: TheYellowDuck/RAG-codebase (golden set + eval harness), krishagarwal314/CodeJury (5-stage pipeline), iAmLakshya/Lattice (adaptive graph/vector weights)] |
| **P4 (optional) — L2 GNN augmentation** | Per-snippet AST+data-flow graph → GNN pre-trained (node classification over syntax/terminal nodes, ASTGPool pooling) → token-level fusion into the code LLM's intermediate layers (warmup GNN then joint fine-tune) | +BLEU/CodeBLEU delta on a workspace commit-derived benchmark; CGFuse's measured window +10-16% BLEU provides the falsifiable bar | [Exa: CGFuse + GNN-Coder] |

### 4.3 Non-negotiable design constraints borrowed from the workspace's own scars

* **No silent staleness** (`MONITORING/KNOWLEDGE/problems/2026-09-02_extension_injection_staleness.md`): file-hash gate fails loud; `watch` or hook is the only auto-refresh — polling without hashes is forbidden.
* **No guessing** (`PROBLEM_ROUTING.md` Rule 4): every graph edge that is a fuzzy fallback carries `confidence` and is filterable by `--min-confidence` (default 0.7) before it reaches an LLM, per CoreGraph's doctrine.
* **Every graph answer carries provenance.** Like `RESEARCH/`'s "every claim cited to a URL, file path, or local document" rule and code-graph-mcp's `AST-verified positions` block header, the graph brain's rendering is `real, AST-verified positions` or it says nothing.
* **Determinism before intelligence.** The graph is deterministic math (Brandes/Tarjan/Louvain/RRF/PPR/deterministic score across incomparable scales); the LLM is the last consumer, never the traversal engine. This matches slop0's "graph algorithms — pure math" posture and CodeJury's rigged deterministic reranker [Exa: berkantay/slop0 Graph Algorithms, krishagarwal314/CodeJury rerank].

---

## 5. Risks that would make the graph lie (and how each candidate graph mitigates)

| Risk | Which live graphs show the footprint | Mitigation to demand in spec |
|---|---|---|
| `this` parameter mismatch (constructor `this` as first param ills scope) | sdsrss/code-graph-mcp documents the `CONSTRUCTOR_PROPERTY`-vs-`FUNCTION` split and the existing ad-hoc save | Config flag for constructor-`this` adapter, not a code delta per edge |
| Windows native KuzuDB | GitCortex + Infigraph both flag Windows as non-trivial (MSVC link, cmake dep) | SQLite-first core, KuzuDB as optional `GRAPH_BACKEND` env |
| LSP live-server hang on cold start | code-graph-rust benchmarks `LSP_INIT_TIMEOUT 15 s + LSP_REQUEST_TIMEOUT 15 s` after deadlock fixes | Hard 15 s timeouts, fallback to AST-only on deadline |
| Language granularity drift (Graphy's 20 node types vs CoreGraph's focused few) | Graphy's full 20-type / 17-edge schema vs CoreGraph's `CALLS/IMPORTS/EXTENDS/...` minimal set | Start with CoreGraph's minimal edge set; add types only when a detector consumes them |
| Equal-weight RRF degrading the stronger retriever | Both hybrid-graph-rag and CodeJury measure symmetric RRF below BM25-only on uneven strengths | Ship RRF weights as first-class config (`rrf_dense_weight`, `rrf_k`) with measured defaults (BM25 1.0 / dense ≥2.0) |

---

## 6. Local sketch (never implement here — research stays read-only)

A sketch that the planning slices would harden (one slice per crate/tool, S5-gated):

```
/brains/graph_brain/
  corpus/                  ← graph-derived prose corpus for ask.py FTS5 (arch map, health report, hotspot docs)
  graph.db | graph/        ← SQLite (default) / KuzuDB (optional) — the real store
  build_graph.py           ← parallel tree-sitter extract → import/call resolve → community/centrality → persist
  verify_graph_sync.py     ← index↔disk + digest↔render + file-hash freshness (fail-loud)
  ask.py                   ← FTS5 over derived corpus + direct graph queries (structured mode)
  topics.md                ← router keywords (graph, callers, callees, hotspots, blast, dead-code, etc.)
  gen_digest.py            ← GRAPH-BRAIN-DIGEST for .jcode/prompt-overlay.md
  framework/               ← 15 TOML framework configs (route/ORM/DI patterns)
/.jcode/skills/graph-brain/ ← SKILL.md + tools: graph_lookup/search/call_chain/blast_radius/hotspots/dead_code/stats/recommend_direction
/workspaces/graph-brain/   ← isolated worker owns the graph store (two-tier doctrine)
```

The two-tier isolation invariant (`WORKFLOW.md` K-26/K-27/K-28) applies: the orchestrator never loads the graph store; isolated workers do, the orchestrator reads result **files** only.
