---
type: Concept
title: reflection_retrieval_dominates_write
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Retrieval quality dominates write sophistication — so keep the lossless source beside any distilled index

taxonomy: #retrieval #memory #context-engineering #persistence

**Problem.** Write-time intelligence (distil, summarize, extract facts) is sold as the lever.
The measurement says the lever is elsewhere.

**Symptom (measured).** arXiv 2603.02473 (ICLR 2026) crossed 3 write strategies (raw chunks /
Mem0-style fact extraction / MemGPT-style summaries) with 3 retrieval methods (cosine / BM25 /
hybrid+rerank) on 1,540 questions. Retrieval method moved accuracy **14–23 points**; write
strategy moved it **3–8**. The *cheapest* write — raw chunks, **zero LLM calls** — matched or
beat both lossy alternatives under every retrieval method (81.1% best overall). Retrieval
precision predicted accuracy at **r = 0.98**. Failure analysis: retrieval failure 11–46% of
questions, utilization failure a stable 4–8%, hallucination 0.4–1.4%.

**Root cause.** Lossy write strategies "discard contextual nuances useful at inference time."
The loss is paid at retrieval time, where nothing compensates for a fact that was dropped.

**Design rule.** Spend on the retrieval side, not the write side. Where a distilled index is
worth building, the graph-memory-starter's guardrail is what makes it safe: the distilled entry
is verified against the source word-for-word (`normalise(quote) not in normalise(body)` →
drop, and the failure is named) and is indexed **alongside** the raw chunk, never instead of
it. That is the configuration the benchmark does not test: *lossless write + supplementary
query-shaped index*. The distil adds question-shaped retrieval anchors; it does not become the
store.

**Consequence for this workspace.** The corpus keeps full chunks with `source:` provenance;
nothing is replaced by a summary. This chunk's own contract — every claim traceable — is the
same invariant as the quote-grounding check.

**Boundary.** Single backbone (GPT-5-mini), one benchmark (LoCoMo), fixed k=5. The authors note
raw chunking's advantage may shrink under tight context budgets where compression is required
to fit.

**Source.** `RESEARCH/2026-09-03_knowledge-architecture-research/` §7.3, reopened 2026-09-16.
