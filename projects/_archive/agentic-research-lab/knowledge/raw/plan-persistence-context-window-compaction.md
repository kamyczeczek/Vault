---
type: Concept
title: "Plan Persistence and Context-Window Pressure: Threshold-Triggered Compaction and the COMPASS Evaluation"
source: "https://www.agentnative.dev/patterns/context-compaction-pattern-for-long-running-agents"
tags: [context-engineering, icm, planning, memory, reflection, anti-leakage]
retrieved: 2026-09-15
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

Plan persistence under context-window pressure requires treating durable plans as external state, not as in-window text that can be compacted away. Retrieved 2026-09-15 from https://www.agentnative.dev/patterns/context-compaction-pattern-for-long-running-agents (updated 2026-07-26) and corroborated by https://arxiv.org/html/2608.06663v1 (The Horizon Gap, Aug 2026) and https://arxiv.org/pdf/2402.02716 (Understanding the Planning of LLM Agents: A Survey).

Long trajectories hit two walls. The hard wall is the context limit ending the task mid-flight. The soft wall arrives earlier as context rot: Chroma 2025 across 18 frontier models found performance degrading at every increment of context growth even on trivial tasks, and Liu et al. measured 20+ point drops on multi-document QA when relevant material sits mid-context. Planning over dozens of subtasks compounds this; the planning survey notes trajectories are forgotten when planning is constrained by context length.

Context compaction pattern (2026): intervene at 60-70% window utilization, not 90%+, because summaries generated inside the rot regime are themselves degraded. Keep-verbatim zones preserve byte-stable system prompts, tool schemas, task statements, acceptance criteria, and last 5-7 turns (also for prefix-cache hits). The cheapest lever is tool-result clearing or observation masking — replacing stale re-fetchable outputs with a one-line placeholder — which JetBrains (arXiv 2508.21433) measured as ~52% cost cut with ~2.6% solve-rate gain on SWE-bench, beating pure LLM summarization that lengthened trajectories up to 15% by obscuring stop signals.

When still above threshold, summarize the evicted middle against an explicit schema: decisions and reasons, discovered constraints, current plan state, artifacts (exact paths and IDs verbatim), approaches ruled out and why, open questions. Freeform summaries drop the dead-end record and invite loops retrying failed approaches.

Durable external memory is the persistence answer: a plan file, scratchpad, NOTES.md, or platform memory tool outside the window that survives any number of compactions. Anthropic triad treats compaction, structured note-taking, and multi-agent isolation as distinct levers. For long horizons, escalation is architectural — sub-agents whose full trajectories stay out of the orchestrator window, returning only distilled results.

For trajectory-aware planning evaluation, COMPASS (arXiv 2512.02559, Aug 2025) parametrizes task complexity across 11 features (decomposition structure, operator dependencies, constraints) and evaluates planning during execution, not just final success. It exposes that success rates do not predict correct planning trajectory; agents recover after early errors, so plan quality must be measured step-by-step against execution feedback, not by outcome alone.

Provenance: agentnative.dev compaction pattern + arXiv 2608.06663 + arXiv 2402.02716, retrieved 2026-09-15.
