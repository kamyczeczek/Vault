---
type: Concept
id: 00_tool_orchestration_multi_tool
title: "tool-orchestration-multi-tool.md"
source: "tool-orchestration-multi-tool.md"
tags: [agentic, agents, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Multi-tool orchestration shifts focus from single-call correctness to end-to-end executability of tool chains under state, feedback, safety, cost, verifiability constraints. Retrieved 2026-09-15 from arXiv 2603.22862v2 (Mar 2026, single→multi-tool), arXiv 2508.17692 (Agentic Reasoning taxonomy), Springer 10.1007/s41019-025-00296-9 (Tool Learning survey Jun 2025).

Key shifts: serial chain-of-thought → topological/graph planning, dual-system architectures (fast parse + slow deliberation, e.g., MARS), structured intermediate representations for verifiability (CodeTool), and procedural memory (DeepAgent/MACLA/HiAgent reusable workflows). Dynamic tool discovery/routing (HuggingGPT semantic routing, Tool-to-Agent Retrieval indexing both tools and parent agents, Gradientsys multi-executor coordination under capacity). Framework: perceiver/validator/controller/retriever/executor loop with iterative adjustment — mirrors ICM's single-agent + single-AGENTS pipeline with watch.py as validator.

Evaluation moved from API-Bank/MetaTool/ToolBench call accuracy to system-level trajectory repair and persistence (sustain, adapt, repair extended chains). Central lesson: the orchestrator (ICM's AGENTS.md + WORKFLOW.md + watch.py gate) should stay out of tool semantics; toolset expansion (retrieve-then-rerank, then plan ordering) belongs in dedicated retrieval/management layers, not the orchestrator prompt.

Implication for this brain: treat `pipeline/06_reflect/spawn.py` + `watch.py` + `check_reflection.py` as tool-orchestration with explicit gates, not implicit LLM "tool calling" inside one window. Keep tool discovery queryable via topics/tags (route.py), not pasted lists.

Provenance: exa "LLM tool integrated reasoning function calling agent environment interaction survey" → top Survey hits 2603.22862v2, 2508.17692, 10.1007/s41019..., retrieved 2026-09-15 via agent-reach Exa.
