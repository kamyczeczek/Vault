---
type: Concept
id: 00_memory_eviction_forgetting_web_research
title: "Memory Eviction and Forgetting in Agent Systems"
source: "memory_eviction_forgetting_web_research.md"
tags: [agentic, agents, context-engineering, memory]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Memory Eviction and Forgetting in Agent Systems

## Core concepts

Memory eviction decides which stored lessons remain retrievable. Forgetting is the active removal or decay of low-value or stale memories. The key tension: too little eviction floods context with marginal lessons; too much deletes knowledge before it generalizes. Good systems separate *stale* from *wrong*: stale lessons need revalidation, wrong lessons need immediate removal.

## Evidence from web sources

- ExpeL uses importance scoring with DOWNVOTE-to-zero eviction and explicit reversibility. The authors observe that insight sets grow monotonically in practice, so retrieval must eventually supplement eviction. This confirms two independent axes: quality control via eviction, volume control via retrieval.
- Memory-based RL agents (e.g., Differential Neural Computer, Memory-Augmented NN) use content-based addressing and least-recently-used eviction. The finding relevant here: eviction by access recency alone is weaker than eviction by reinforcement signal, because the most-used memory may be the most confidently wrong one.
- LLM context compaction literature distinguishes between summarizing versus selective eviction. Summarization preserves wrong lessons in softened form; selective eviction removes them. The empirical finding is that selective eviction plus citation checking yields better long-horizon accuracy than summarization alone.
- "Forgetting" as a feature: controlled forgetting prevents catastrophic interference in continual learning. In agents, this maps to removing lessons whose evidence ids no longer resolve in the knowledge graph, which is already implemented in `scripts/evict_stale.py`.

## Why it matters for this workspace

This project already separates stale from superseded and rejects at stale evidence rather than deleting. The missing piece is retrieval-side volume control: even correct lessons can crowd context. Adding a retrieval gate that limits recalled candidates by relevance threshold would complete the second axis ExpeL identified.

## Source

Web research: ExpeL eviction, memory-augmented networks, context compaction selective eviction.
