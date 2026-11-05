---
type: Concept
title: hornet_dev_bergum_bm25_agentic_search
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Raw Notes: The Unreasonable Effectiveness of BM25 for Agentic Search (Jo Kristian Bergum)

**Speaker:** Jo Kristian Bergum, CEO of Hornet.dev (formerly Chief Scientist at Vespa.ai, Distinguished Engineer at Yahoo)
**Context:** AI Engineer conference talk; Bergum has 20+ years in search and retrieval

## Summary
Agentic search is "search inside the agent loop" — a multi-step retrieval process operating within an AI agent's reasoning cycle (formulate query, receive results, evaluate, reformulate).
While neural embeddings have gained popularity, BM25 remains remarkably effective for agents because LLMs are hyper-active searchers that generate long, structured queries, deploy syntax operators (`site:`, quotes), and rely heavily on exact term/phrase matching (names, entities, zip codes, SKUs).
Furthermore, tuning BM25 parameters for long documents ($k_1=10, b=1.0$) yields a 77% recall improvement on benchmarks like BrowseComp-Plus (ACL 2026).
Combined with `grep` and virtual file system (VFS) workspaces ("code mode"), BM25 + grep forms a powerful agentic retrieval paradigm.
