---
type: Concept
id: 00_persistent_memory_hierarchies_agents
title: "persistent-memory-hierarchies-agents.md"
source: "persistent-memory-hierarchies-agents.md"
tags: [agentic, agents, context-engineering, icm, memory, planning, reflection, self-evolution]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Longer context windows do not obsolete external memory. A 200k window enlarges working memory but provides no cross-session persistence, structured organization, selective retrieval over months, or governance (deletion/access control), and inference cost scales quadratically with length. Targeted retrieval over a modest context outperforms brute-force long context on many tasks.

The 2026 survey formalizes agent memory as a write-manage-read loop coupled to perception and action in a POMDP cycle, with a three-dimensional taxonomy: temporal scope (working/episodic/semantic, short vs long-term), representational substrate (textual vs parametric vs structured/graph), and control policy (hand-coded paging vs learned controller, passive vs active invocation).

Five mechanism families are compared. Hierarchical/virtual-context management is the most instructive for ICM: MemGPT (Packer et al., 2023/2024) borrows OS virtual memory — LLM context is RAM (system instructions + working context + FIFO queue), archival/recall databases are disk. The LLM self-pages via function calls (e.g., archival_memory_search, core_memory_append) and chains them with request_heartbeat interrupts. JARVIS-1 extends this to multimodal tiers (visual observations, textual plans, executable skills); Cognitive Architectures for Language Agents map Baddeley-style stores (working/episodic/semantic/procedural) through a central LLM executive.

Tradeoff: paging the wrong tier wastes tokens or creates "memory blindness" where the agent cannot discover facts in cold storage. Next-generation systems add active perception — learned controllers that decide *whether* memory is needed and *which* tier to query, rather than retrieving indiscriminately.

Beyond product, evaluation has shifted from static recall (LoCoMo, LongMemEval, Recall@k/NDCG) to agentic benchmarks embedding memory in action. MemoryAgentBench tests retrieval, test-time learning, long-range understanding, and selective forgetting; MemoryArena nests subtasks so later steps depend on earlier learning. Finding: near-perfect LoCoMo models drop to 40-60% in MemoryArena — passive recall ≠ decision-relevant use. Engineering patterns now cluster into (A) single-store RAG, (B) graph-structured memory, (C) tiered memory with learned control (MemGPT/AgeMem).

For ICM workspaces, implications are direct: treat corpus as durable external store (disk), graph digest as paged-in working summary, and reflection/spawn as consolidation. Self-directed paging + active retrieval controllers are the missing control plane.

Provenance: Synthesis from Du et al., "Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers," arXiv:2603.07670 (2026), and Packer et al., "MemGPT: Towards LLMs as Operating Systems," arXiv:2310.08560 (2023/2024) via Exa search + Jina Reader, retrieved 2026-09-15. No >100-char overlap with existing corpus ids 85/90_icm_knowledge_big; those cover hierarchy concepts at ICM level only.
