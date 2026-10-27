---
type: Concept
title: "SBOMs into Agentic AIBOMs: Schema Extensions, Agentic Orchestration, and Reproducibility Evaluation"
source: "http://arxiv.org/abs/2603.10057v1"
tags: [agentic, scientific-discovery]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# SBOMs into Agentic AIBOMs: Schema Extensions, Agentic Orchestration, and Reproducibility Evaluation

**Source:** http://arxiv.org/abs/2603.10057v1
**Tags:** `agentic, scientific-discovery`

## Core Methodology & Findings

**Authors:** Petar Radanliev, Carsten Maple, Omar Santos, Kayvan Atefi

### Abstract
Software supply-chain security requires provenance mechanisms that support reproducibility and vulnerability assessment under dynamic execution conditions. Conventional Software Bills of Materials (SBOMs) provide static dependency inventories but cannot capture runtime behaviour, environment drift, or exploitability context. This paper introduces agentic Artificial Intelligence Bills of Materials (AIBOMs), extending SBOMs into active provenance artefacts through autonomous, policy-constrained reasoning. We present an agentic AIBOM framework based on a multi-agent architecture comprising (i) a baseline environment reconstruction agent (MCP), (ii) a runtime dependency and drift-monitoring agent (A2A), and (iii) a policy-aware vulnerability and VEX reasoning agent (AGNTCY). These agents generate contextual exploitability assertions by combining runtime execution evidence, dependency usage, and environmental mitigations with ISO/IEC 20153:2025 Common Security Advisory Framework (CSAF) v2.0 semantics. Exploitability is expressed via structured VEX assertions rather than enforcement actions. The framework introduces minimal, standards-aligned schema extensions to CycloneDX and SPDX, capturing execution context, dependency evolution, and agent decision provenance while preserving interoperability. Evaluation across heterogeneous analytical workloads demonstrates improved runtime dependency capture, reproducibility fidelity, and stability of vulnerability interpretation compared with established provenance systems, with low computational overhead. Ablation studies confirm that each agent contributes distinct capabilities unavailable through deterministic automation.
