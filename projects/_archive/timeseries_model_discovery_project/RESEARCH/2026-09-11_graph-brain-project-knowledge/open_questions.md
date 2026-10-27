---
type: Concept
title: open_questions
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Open Questions — Graph Brain for Project-Wide Knowledge, Fast Problem Detection & Direction

## Q1. SQLite vs KuzuDB for the primary store on Windows hosts
**Why unresolved:** Infigraph uses the `lbug` fork of KuzuDB (adds a cmake build dep) and GitCortex documents KuzuDB 0.11.3 failing to link under MSVC on Windows (LNK1169/LNK2038). Our workspace core is Windows_NT (win32). Primary source fetched but the Windows-native path would need a real build test to confirm liveness; doing a build test would cross the research read-only boundary. So the recommendation is the dual-backend `GraphStore` trait with SQLite-first default, but the final backend choice is deferred to P1's build spike.

## Q2. Whether this repo needs vectors at all for the L1 hybrid pipeline
**Why unresolved:** The web evidence is conditional, not absolute. RAG-codebase measured BM25 adding +0.10 recall@5 on Django (40K chunks, significant), but the `graph` rerank's lift overlapped CIs (0.900 → 0.920) in the pooled result and was conditional (Go/cobra 0.824 → 0.941 p=0.019, Python/FastAPI null). Sourcegraph/Cody actually *removed* embeddings for Enterprise because the operational cost (freshness, vector-DB scale at 100K repos) outweighed the measured gain vs BM25+graph alone. A decision for our repo (a few dozen sub-experiments + docs, not 40K chunks) needs a local golden-set eval, not a literature vote. The honest posture is: ship BM25+graph first, add dense+RRF where the golden-set bootstrap shows a disjoint-CI win (as TheYellowDuck's `eval/` harness demands).

## Q3. GNN (CGFuse / GNN-Coder) cost/benefit for direction recommendation
**Why unresolved:** CGFuse reports +10-16% BLEU / +6-11% CodeBLEU across 9 PLMs (every PLM improved, CodeT5-family most) and GNN-Coder documents the specific `ASTGPool` pooling trick, but both involve per-graph GNN pre-training (node-classification on AST/DataFlow) and token-level fusion into the LLM's intermediate layers. That workload violates the workspace's "no grid searches or heavy things" memory fact and the deterministic-math-before-LLM posture. L2 is therefore explicitly sequenced as optional phase P4, gated on P3's measured ceiling.

## Q4. Tree-sitter grammar set for the first index
**Why unresolved:** Most live graphs converge to 10-15 languages; Infigraph covers 62, but our repo is predominantly Python (h720 sub-experiments, methods, data.py), TypeScript/JavaScript (Brains, extensions), and Markdown. Deciding whether to ship 4 or 15 grammars in P1 trades `node_modules` tree-sitter build weight against "it already knew about this language" surprise. The research does not pin a list; P1's spike chooses the minimal set that covers `projects/` + `brains/` + `PROCESS/` with correctness on `this` parameter mismatch (constructor `this` vs `FUNCTION` node, see sdsrss/code-graph-mcp note) as the acceptance test.

## Q5. Where the health dashboard lives (CLI vs web vs IDE panel)
**Why unresolved:** Web dashboards exist for Graphy (Sigma.js), Grafel (19 surfaces at :47274), and Infigraph (localhost:9749), but our workspace's current brains surface only via CLI (`ask.py`) + auto-loaded digests. Introducing a web or IDE surface is a UX scope decision rather than a research finding; the recommendation proposes a deterministic CLI `graph health` artifact that the existing gate infrastructure can consume first (aligns with `verify_*_sync` doctrine), with a web surface deferred to P2.
