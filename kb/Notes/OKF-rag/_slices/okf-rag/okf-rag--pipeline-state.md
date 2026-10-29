---
type: source-slice
title: "OKF-RAG — persistent pipeline state"
generated: true
origin: "Notes/OKF-rag/okf-rag.md"
origin_hash: ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5
source_lines: [461, 475]
source_heading: "Generate OKF with llm-wiki-compiler"
slice_hash: 5913adce1f0e099d71d6629c3095d460e2f6c36f8d2d854f57423d1757ce71c2
generator: "scripts/generate_source_slices.py@1"
---

<!-- GENERATED FILE: do not edit by hand. -->

# OKF-RAG — persistent pipeline state

## Source excerpt

The persistent state is split by responsibility:

| Path | Contents |
|---|---|
| `.okf-rag/llmwiki-projects/<topic>/` | Persistent llmwiki source and concept state. |
| `.okf-rag/llmwiki-source-sync/<topic>.json` | Source manifest v2: adapter, stable source identity, raw/compiler hashes, timestamps, ownership, and deletion propagation. |
| `.okf-rag/llmwiki-exports/<topic>/` | Temporary OKF export candidates. |
| `.okf-rag/publish-staging/` | Complete bundle assembled and validated before publication. |
| `.okf-rag/llmwiki-sync/<topic>.json` | Reconcile manifest v3: generations, canonical IDs, aliases, ownership, directed relations, duplicates, orphans, and hashes. |
| `okf-rag-workspace/okfs/<topic>/` | Atomically published OKF bundle. |

Publication performs authoritative pruning of managed concepts, conservative exact dedupe, source ownership reconciliation, directed relationship extraction, broken-link validation, host-absolute-path rejection, graph audit, deterministic folder indexes, and an atomic directory switch. Generated relationship blocks use Obsidian `[[file|title]]` links with separate Outgoing and Backlinks sections. Semantic direction remains in `outbound_relations` and `inbound_relations`; a navigation backlink does not create a reverse semantic edge. Concept `source_refs` point to bundle-local `references/` documents, while mirrored source documents use portable `okf-source://` URIs. Modified stale generated files are recovered under the bundle's `references/recovered/` directory, which Rust skips during ingest.

Each generated topic contains an OKF v0.1 bundle-root `index.md`; `okfs/index.md` is a deterministic catalog of bundles. `okf-rag-workspace/index.md` is not generated because that workspace also contains runtime artifacts.

## Provenance

- Origin: `Notes/OKF-rag/okf-rag.md:461-475`
- Origin hash: `ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5`
- Regenerate with `python scripts/generate_source_slices.py`.
