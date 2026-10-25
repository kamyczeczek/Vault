---
type: source-slice
title: "OKF-RAG — end-to-end flow: embeddings, hybrid retrieval, lexical reranking"
generated: true
origin: "Notes/OKF-rag/okf-rag.md"
origin_hash: ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5
source_lines: [231, 266]
source_heading: "End-to-End Knowledge Flow"
slice_hash: 29808293cb694a8405b31477271f88e8d4f9b329c284bf5f9e67751421cc48e0
generator: "scripts/generate_source_slices.py@1"
---

<!-- GENERATED FILE: do not edit by hand. -->

# OKF-RAG — end-to-end flow: embeddings, hybrid retrieval, lexical reranking

## Source excerpt

### End-to-End Knowledge Flow

```text
+---------------------------- Producer plane: Node + LLM -----------------------------+
|                                                                                      |
|  Agent / user                                                                        |
|      |                                                                               |
|      v                                                                               |
|  raw/<topic>/*.md                                                                    |
|      |  fs.watch + debounce                                                          |
|      v                                                                               |
|  daemon supervisor -> worker -> source manifest v2                                  |
|                                      |                                               |
|                                      v                                               |
|                         llm-wiki-compiler candidates + links                         |
|                                      |                                               |
|                                      v                                               |
|  ownership/prune -> exact dedupe -> directed graph -> validate -> staged publish    |
|                                      |                                               |
+--------------------------------------|-----------------------------------------------+
                                       v
                     okfs/<topic>/index.md + concept Markdown
                                       |
+--------------------------------------|-----------------------------------------------+
|                       Consumer plane: Rust, local only                               |
|                                      v                                               |
|  ingest -> MiniLM ONNX -> embedding cache -> inactive zvec slot                     |
|                                                   | successful build                 |
|                                                   v                                  |
|  Codex / agent <- MCP query <- hybrid recall + lexical rerank <- active slot pointer |
|                                                                                      |
+--------------------------------------------------------------------------------------+
```

For stream-only OpenAI-compatible providers, `openai_stream_adapter.js` runs on loopback, converts llmwiki requests to streamed upstream calls, and reassembles text and tool-call responses. Secrets stay in environment variables and are redacted from daemon state and diagnostics.

## Provenance

- Origin: `Notes/OKF-rag/okf-rag.md:231-266`
- Origin hash: `ef423bb7c17343562e0c514daa1d1338148de49d3046b2bdb4ec44a1c6d831c5`
- Regenerate with `python scripts/generate_source_slices.py`.
