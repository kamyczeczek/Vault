---
type: Concept
title: "Layered AI Work Engineering Control Stack"
source: "https://arxiv.org/html/2608.21156v1; https://developers.openai.com/api/docs/guides/agents/sandboxes; https://arxiv.org/html/2601.12580"
tags: [ai-work-engineering, prompt-engineering, context-engineering, loop-engineering, harness-engineering, graph-engineering, attention-engineering, ontology-engineering, self-healing]
trust_tier: 1
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---
# Layered AI Work Engineering Control Stack

## Scope and central claim
Graph Engineering is a system-level coordination layer, not a complete theory of AI work engineering. It organizes tasks, agents, dependencies, communication, and runtime state, but it depends on lower layers that shape individual model behavior and execution, and it interacts with higher or cross-cutting layers that govern attention allocation and shared semantics.

The layers are complementary. Higher layers build upon rather than replace lower layers:

```text
Ontology / shared semantics
        ↓
Attention / resource allocation
        ↓
Graph / multi-agent organization
        ↓
Harness / permissions and runtime environment
        ↓
Loop / local execution and recovery
        ↓
Context / evidence and memory selection
        ↓
Prompt / single model interaction
        ↓
Model and tools
```

This is an analytical stack, not a claim that all systems implement these names as standardized products. Attention Engineering and the exact boundaries between layers remain emerging design categories.

## Layer contracts

### Prompt Engineering
Controls a single model interaction through instructions, output schemas, role framing, and local reasoning constraints. Typical failures include format violations, unsupported assertions, prompt injection susceptibility, and ambiguous task interpretation. Validation includes schema checks, targeted examples, and independent evaluation.

### Context Engineering
Controls which tokens, retrieval fragments, memory items, and evidence spans enter the finite model context. Typical failures include irrelevant retrieval, stale memory, missing evidence, context dilution, and unsupported synthesis. Validation includes evidence-ID resolution, bounded spans, provenance checks, retrieval precision, and negative controls.

### Loop Engineering
Controls an individual agent's observe–reason–act–verify cycle. It owns stop conditions, retry budgets, local reflection, action validation, and escalation. Typical failures include infinite retries, premature termination, unverified actions, and symptom-level correction. Validation includes replay tests, explicit termination receipts, and counterfactual root-cause checks.

### Harness Engineering
Controls the operational environment around an agent: tools, MCP endpoints, approvals, tracing, recovery, files, commands, ports, mounts, credentials, and sandbox boundaries. A graph may request an action, but the harness must enforce whether that action is permitted and what state it can affect. Validation includes least-privilege tests, sandbox escape tests, network allowlist tests, and state snapshot verification.

### Graph Engineering
Controls system-level organization through explicit graph structures. Its central concerns are task organization, agent coordination, and runtime state management. It represents decomposition, dependencies, concurrency, delegation, communication, synchronization, progress, provenance, fault localization, and recovery. Typical failures include duplicated work, illegal transitions, lost subproblems, inconsistent state, and unbounded fan-out. Validation includes graph invariants, state-transition checks, reachability, deterministic replay, and checkpoint rollback.

### Attention Engineering
Allocates limited reasoning, token, latency, and tool budgets across a graph. It addresses attention dilution by prioritizing high-impact nodes, evidence paths, unresolved defects, and critical joins. This layer is emerging and should be treated as a resource policy over graph state rather than as a replacement for graph orchestration. Validation includes budget accounting, priority regression tests, and outcome-versus-cost measurements.

### Ontology Engineering
Defines shared machine-interpretable meanings for entities, states, evidence, relations, permissions, and transitions. It prevents agents from using connected terms with incompatible meanings. Ontology-scoped update validation and local revalidation are mechanisms for preserving semantic coherence in distributed agent systems. Validation includes schema validation, semantic consistency checks, conflict detection, and scoped update tests.

## Cross-layer failure routing

A failure should be routed to the earliest layer that explains it:

| Failure | Primary layer | Typical repair |
|---|---|---|
| Invalid output format | Prompt | Improve instruction or schema |
| Unsupported or stale evidence | Context | Repair retrieval, provenance, or memory |
| Repeated retry / unverified action | Loop | Change stop, retry, or verification policy |
| Unauthorized command or data access | Harness | Tighten sandbox, approval, or permission policy |
| Duplicate work or illegal dependency | Graph | Repair topology, scheduling, or state transition |
| Context or compute dilution | Attention | Change priority and budget allocation |
| Conflicting meanings or state schemas | Ontology | Repair shared semantic contract |

Recurrence can promote a local repair into a higher-level policy change. A one-off malformed response is a prompt issue; the same failure across many agents may indicate a schema, context, or ontology defect.

## Independent verification boundary

Graph agreement is not sufficient verification. Agents reviewing each other's claims can reproduce a shared blind spot. High-reliability work requires external anchors such as tests, compiler output, build receipts, provenance manifests, live telemetry, deterministic replay, or environment state. The graph records and routes these receipts, but does not make them true by itself.

## Workspace design implication

The knowledge graph should model the layered stack as a set of typed concepts and dependencies while Markdown and raw artifacts remain canonical. Failure and repair records should carry:

- `layer`
- `earliest_cause`
- `affected_nodes`
- `evidence_ids`
- `validation_boundary`
- `rollback_to`
- `recurrence_count`

The autonomous loop should classify before repairing, quarantine unsupported state, validate at the responsible layer, and commit only reversible changes.

## Limitations and open questions

The stack is a useful engineering taxonomy, not yet a universally accepted standard. Graph Engineering has clearer recent survey grounding than Attention Engineering. Layer boundaries can overlap: context affects loops, harnesses shape loops, ontology constrains graphs, and attention policies operate across all layers. Future evaluation should measure whether layer-aware routing reduces recurrence, cost, and unsafe state changes compared with generic retry or graph-only repair.

## Sources

- Graph Engineering in the Era of LLM Agents, arXiv:2608.21156, https://arxiv.org/html/2608.21156v1
- OpenAI Agents SDK Sandbox Guide, https://developers.openai.com/api/docs/guides/agents/sandboxes
- Semantic Fusion: Verifiable Alignment in Decentralized Multi-Agent Systems, arXiv:2601.12580, https://arxiv.org/html/2601.12580
- Model-driven engineering of multi-agent systems based on ontologies, https://smart-pucrs.github.io/publications/pdf/ao2017ArturFreitas.pdf
