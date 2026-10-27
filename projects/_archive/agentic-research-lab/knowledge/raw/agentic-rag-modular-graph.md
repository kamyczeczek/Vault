---
type: Concept
title: "Agentic RAG: Modular and Graph-Enhanced Retrieval for Agents"
source: "https://arxiv.org/html/2501.09136v4 + https://arxiv.org/html/2507.13334"
tags: [context-engineering, icm, rag, graph-rag, agents, planning]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Agentic RAG turns static retrieval into an autonomous loop: the agent decides when to retrieve, what to retrieve, and how to interleave retrieval with reasoning. Retrieved 2026-09-15 from arXiv 2501.09136v4 (Apr 2026, Agentic RAG survey) and the Context Engineering survey 2507.13334.

Evolution: Naïve RAG → Advanced RAG → Modular RAG → Graph RAG → Agentic RAG. Modular RAG decomposes the pipeline into reusable components (hybrid retrieval, composable pipelines, tool integration) for domain-specific optimization. Graph RAG adds graph-structured retrieval (nodes/edges capturing relations) enabling multi-hop reasoning and contextual enrichment; mitigates hallucinations on structured tasks but depends on knowledge-graph quality.

Agentic RAG (paradigm shift): autonomous agent with adaptive retrieval, iterative refinement, multi-domain handling. Taxonomy by cardinality/control: single-agent (low latency, weak on multi-domain), multi-agent (parallelism at coordination cost), hierarchical/corrective (reliability via oversight, higher latency), graph-based (Agent-G, GeAR: graph expansion + agent loop for multi-hop retrieval). RAG-Reasoning synergy (survey 2608.xxxx pattern: Reasoning-Enhanced RAG vs RAG-Enhanced Reasoning vs synergized interleaving) maps directly to the ICM planner/executor split: planner chooses retrieval strategy, executor grounds generation.

Implication for this brain: keep `knowledge/graph/graph.db` as the Graph RAG layer (SHARES_TAG edges + FTS5), `route.py --tag` as the deterministic retriever, and any external Exa/Jina fetch as the agentic retriever behind an explicit tool. Do not mix them implicitly in prompts.

Provenance: exa "graph RAG agentic RAG modular retrieval survey 2024 2025" → arXiv 2501.09136v4 + 2507.13334, retrieved 2026-09-15 via agent-reach Exa.
