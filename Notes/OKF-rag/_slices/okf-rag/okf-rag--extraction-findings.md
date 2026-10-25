---
type: source-slice
title: "OKF-RAG — findings: non-deterministic concept extraction, near-duplicate deduplication, pruning layer"
generated: true
origin: "Notes/OKF-rag/okf-rag.md"
origin_hash: ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5
source_lines: [1134, 1141]
source_heading: "Findings"
slice_hash: 464f7bb992ab0aa0f0cc244e7b99f50fa17247cb96cf083cb2eded1f130892b9
generator: "scripts/generate_source_slices.py@1"
---

<!-- GENERATED FILE: do not edit by hand. -->

# OKF-RAG — findings: non-deterministic concept extraction, near-duplicate deduplication, pruning layer

## Source excerpt

Findings:

- Warm daemon bookkeeping is about 100-220 ms. The configured debounce and remote LLM latency dominate end-to-end update time.
- Before fast-skip, an unchanged full pass cost about 4.25 seconds because llmwiki refreshed its index and probed page embeddings. Source/content and publication-option checks now bypass llmwiki entirely: P50 dropped to 115.36 ms, about a 97% reduction.
- File-level source synchronization is incremental and deletion-aware.
- Concept extraction is not deterministic: the same original source produced 5 concepts in an earlier clean run and 6 concepts in the clean benchmark rebuild.
- Concept-level pruning is incomplete in `llm-wiki-compiler@1.1.0`: after changing and reverting the source, three historical near-duplicate pages remained until the project was reset. Automatic OKF generation is operational, but automatic dedupe/pruning needs another layer before production use.

## Provenance

- Origin: `Notes/OKF-rag/okf-rag.md:1134-1141`
- Origin hash: `ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5`
- Regenerate with `python scripts/generate_source_slices.py`.
