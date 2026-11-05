---
type: Concept
title: "Experience Graphs and Self-Evolving Agent Memory"
source: "web: https://arxiv.org/abs/2605.17721v1 + https://arxiv.org/abs/2603.24639"
tags: [agentic, agents, memory, reflection, retrieval, knowledge-graph]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Experience Graphs and Self-Evolving Agent Memory

## EXG: Self-Evolving Agents with Experience Graphs (Jin et al., 2026)

**Paper:** *EXG: Self-Evolving Agents with Experience Graphs* — Yuxin Jin et al., arXiv:2605.17721v1, 2026.

**Core idea:** organize accumulated successes and failures into a structured relational graph rather than a flat ledger or unstructured memory.

### Case abstraction
Each attempt within a trajectory is abstracted into a case:
```
c = (task, input, output, success_flag, execution_signals)
```
- **Golden case** — successful attempt
- **Warning case** — failed attempt with failure type and signature

### Experience graph structure
- **Nodes:** case nodes, task anchor nodes
- **Edges:** containment, similarity, correction
- **Growth:** incremental during execution; online reuse within inference, offline reuse as external memory

### Key properties
1. **Online cross-task reuse** — experience from one task is immediately available to subsequent tasks
2. **Offline memory module** — the consolidated graph serves as an external memory without retraining
3. **Plug-and-play** — operates at inference time, external to agent's internal reasoning
4. **Unified representation** — bridges online self-evolution and offline self-evolution

**Results:** higher pass@1 exceeding 150%, up to 45.7% fewer LLM calls, up to 30.5% lower inference latency.

**Relation to workspace:** the existing `graph.db` is the right substrate for this pattern. The workspace already has case-like nodes in `reflection/candidates/*.jsonl` with typed states; EXG provides the missing relational edges and retrieval protocol.

---

## ERL: Experiential Reflective Learning (Allard et al., 2026)

**Paper:** *Experiential Reflective Learning for Self-Improving LLM Agents* — Marc-Antoine Allard et al., arXiv:2603.24639, ICLR 2026 MemAgents Workshop.

**Core mechanism:** reflect on task trajectories and outcomes to generate heuristics, then retrieve and inject relevant heuristics at test time.

### Process
1. **Reflect** — after each task, extract actionable lessons as heuristics
2. **Store** — persist heuristics in a retrievable format
3. **Retrieve** — at test time, select relevant heuristics based on current task
4. **Inject** — add selected heuristics to agent context

### Ablation findings
- Selective retrieval is essential — injecting all heuristics degrades performance
- Heuristics provide more transferable abstractions than few-shot trajectory prompting
- Single-attempt experience reflection is sufficient for effective self-improvement

**Relation to workspace:** ERL's selective retrieval aligns with the workspace's one-level progressive disclosure. The workspace's `check_reflection.py` already gates which heuristics are allowed into the candidate set.
