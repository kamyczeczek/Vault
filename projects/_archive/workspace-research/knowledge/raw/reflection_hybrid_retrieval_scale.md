---
type: Concept
title: reflection_hybrid_retrieval_scale
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Hybrid retrieval is corpus-scale dependent — RRF helps where vocabulary differs, hurts where it adds noise

taxonomy: #retrieval #context-engineering #knowledge-graph

**Problem.** "Keyword + vector + rank fusion" is presented as a settled upgrade. The evidence
points the other way at scale.

**Symptom (measured, both directions).** arXiv 2603.11513, on a 500K-passage Wikipedia corpus:
hybrid with reciprocal rank fusion k=60 scored **hit@5 14.9%** — *worse* than pure dense at
**16.3%**, with BM25 at 10.5%. Their reading: "the BM25 signal adds noise at this corpus
scale." arXiv 2603.02473 (ICLR 2026), on LoCoMo-scale conversational memory: hybrid+rerank
averaged **77.2%** vs cosine 73.4% and BM25 57.1%, and *halved* retrieval failures (35.3% →
11.4% for raw chunks). Same fusion idea, opposite verdict — the difference is the corpus.

**Root cause.** The lexical leg earns its place when relevant items share no vocabulary with
the question — a notes corpus where titles and prose diverge from how a question is asked. At
large scale, a keyword match becomes a cheap way to retrieve a wrong-but-term-sharing passage,
and the fusion then promotes it.

**Design rule.** Choose the retrieval legs by corpus scale, not by fashion: at hundreds of
chunks, keep the lexical leg; at hundreds of thousands of passages, distrust it. The
graph-memory-starter sits firmly in the first regime — FTS5 BM25 plus a 384-d local embedding
(bge-small-en-v1.5, 67 MB, no API key), fused with RRF k=60 — as does this workspace's own
`ask.py` (FTS5-based). SQLite-native hybrid search is a studied primitive, not an oddity:
arXiv 2608.24060 (scrydb) evaluates FTS5 + sqlite-vec + rerank/fuse on IR benchmarks with
published latency/efficiency trade-offs.

**Boundary.** Neither study fixes the crossover scale; the trigger to re-measure is the corpus
growing roughly an order of magnitude. Hybrid is also not free at query time when a reranker
is an LLM call — the ICLR result bought its 20 points with one judge call per query.

**Source.** `RESEARCH/2026-09-03_knowledge-architecture-research/` §7.2 and §7.6, reopened
2026-09-16.
