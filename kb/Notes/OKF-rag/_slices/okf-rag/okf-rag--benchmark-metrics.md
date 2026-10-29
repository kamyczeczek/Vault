---
type: source-slice
title: "OKF-RAG — benchmark metrics"
generated: true
origin: "Notes/OKF-rag/okf-rag.md"
origin_hash: ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5
source_lines: [573, 602]
source_heading: "Benchmark"
slice_hash: badd1fa6ad4a7787967e0e6eac43dfaa2af14fde60c949099026f6e7ffa72435
generator: "scripts/generate_source_slices.py@1"
---

<!-- GENERATED FILE: do not edit by hand. -->

# OKF-RAG — benchmark metrics

## Source excerpt

## Benchmark

Release benchmark on 2026-06-24, using local `minilm-l6-v2-onnx`, local zvec, 53 OKF Markdown concepts, 258 queries, `top-k=10`, and effective `candidate-k=53`.

| Metric | Result |
|---|---:|
| Recall@1 / Hit@1 | 0.9535 |
| Recall@3 / Hit@3 | 0.9845 |
| Recall@5 / Hit@5 | 0.9922 |
| Recall@10 / Hit@10 | 1.0000 |
| MRR@10 | 0.9700 |

Hot query path loads ONNX and zvec once, then runs all queries:

| Stage | Avg ms | P50 ms | P95 ms |
|---|---:|---:|---:|
| Total query | 5.327 | 5.280 | 6.285 |
| ONNX embedding | 3.474 | 3.419 | 4.355 |
| zvec + rerank | 1.853 | 1.845 | 2.016 |

Ingest benchmark:

| Run | Cache Hits | Cache Misses | Total ms |
|---|---:|---:|---:|
| Cold embedding cache, forced rebuild | 0 | 53 | 1834.119 |
| Warm embedding cache, forced rebuild | 53 | 0 | 190.061 |
| Unchanged source, skipped rebuild | 0 | 0 | 71.584 |

Full details, query-type breakdown, and ONNX thread sweep are in [OKF-RAG-BENCHMARK.md](OKF-RAG-BENCHMARK.md).

## Provenance

- Origin: `Notes/OKF-rag/okf-rag.md:573-602`
- Origin hash: `ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5`
- Regenerate with `python scripts/generate_source_slices.py`.
