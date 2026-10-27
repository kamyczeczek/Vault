---
type: Concept
title: "Graph-Based Self-Healing Tool Routing for Cost-Efficient LLM Agents"
source: "http://arxiv.org/abs/2603.01548v1"
tags: [research-loop,autonomous-agent]
created: "2026-09-22T18:32:31.851051Z"
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Graph-Based Self-Healing Tool Routing for Cost-Efficient LLM Agents

**Source:** http://arxiv.org/abs/2603.01548v1
**Authors:**
**Tags:** `research-loop,autonomous-agent`

## Core Methodology & Findings

Tool-using LLM agents face a reliability-cost tradeoff: routing every decision through the LLM improves correctness but incurs high latency and inference cost, while pre-coded workflow graphs reduce cost but become brittle under unanticipated compound tool failures. We present Self-Healing Router, a fault-tolerant orchestration architecture that treats most agent control-flow decisions as routing rather than reasoning. The system combines (i) parallel health monitors that assign priority scores to runtime conditions such as tool outages and risk signals, and (ii) a cost-weighted tool graph where Dijkstra's algorithm performs deterministic shortest-path routing. When a tool fails mid-execution, its edges are reweighted to infinity and the path is recomputed -- yielding automatic recovery without invoking the LLM. The LLM is reserved exclusively for cases where no feasible path exists, enabling goal demotion or escalation. Prior graph-based tool-use systems (ControlLLM, ToolNet, NaviAgent) focus on tool selection and planning; our contribution is runtime fault tolerance with deterministic recovery and binary observability -- every failure is either a logged reroute or an explicit escalation, never a silent skip. Across 19 scenarios spanning three graph topologies (linear pipeline, dependency DAG, parallel fan-out), Self-Healing Router matches ReAct's correctness while reducing control-plane LLM calls by 93% (9 vs 123 aggregate) and eliminating the silent-failure cases observed in a well-engineered static workflow baseline under compound failures.

## Algorithm / Pipeline

The methodology involves a structured approach as described in the source material.

## Data Structures

Data structures include: graph.

## Threat Model & Limitations

Known risks/challenges: risk signals, and (ii) a cost-weighted tool graph where Dijkstra's algorithm performs deterministic shortest-path routing.

## Limitations

Limitations and scope are described in the original publication.
