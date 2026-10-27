---
type: Concept
title: "Agent Memory Hierarchies: Write-Manage-Read Loop and Virtual Context"
source: "https://arxiv.org/html/2512.13564v1 + https://arxiv.org/pdf/2603.07670 + https://dl.acm.org/doi/10.1145/3748302"
tags: [context-engineering, icm, memory, agents, planning]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Agent memory turns a stateless generator into a persistent agent. Three surveys converge on a write–manage–read loop coupled to perception/action (POMDP cycle), not just retrieval. Sources retrieved 2026-09-15: arxiv 2512.13564 (Dec 2025, Forms–Functions–Dynamics), arxiv 2603.07670 (2022–2026, write-manage-read + taxonomy), ACM 10.1145/3748302 (first dedicated memory survey).

Forms: token-level (flat 1D / planar 2D graph-tree / hierarchical 3D multi-layer), parametric (weights), latent. Textual form dominates for interpretability; hierarchical (MemGPT virtual memory paging between RAM/disk via archival_memory_search / core_memory_append, JARVIS-1 multimodal stores) enables vertical abstraction but risks "memory blindness" if paging is wrong.

Functions: factual (knowledge), experiential (traces), procedural (skills), working (transient context). Short vs long is insufficient; the surveys separate factual vs reflective, participation vs observation.

Dynamics: memory writing (inside-trial, across-trials, external knowledge), management (compression: sliding window, rolling summary, hierarchical summary, task-conditioned / Self-Controlled Memory; consolidation into knowledge), reading (retrieval). Few-shot prompting is long-term memory; self-reflection is inside-trial memory.

Evaluation: direct (memory module alone) vs indirect (end-to-end task success). MemBench separates factual/reflective, MemoryAgentBench/MemoryArena couple memory with action.

Implication for ICM brain: treat `knowledge/corpus/*.md` + `knowledge/graph/graph.db` as the persistent hierarchical store (Layer 3 factory), and `knowledge/graph/ask.py` + digest injection as the managed read path. Keep the loop explicit in WORKFLOW.md: when to write (INBOX→ingest), manage (build_graph fingerprint), read (route.py tags).

Provenance: exa search "LLM agent memory systems survey" → top hits above, retrieved 2026-09-15.
