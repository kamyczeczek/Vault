---
type: Concept
title: "LLMoxie: Exploring Agentic AI for Scientific Software Development"
source: "http://arxiv.org/abs/2607.02703v1"
tags: [agentic, scientific-discovery]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# LLMoxie: Exploring Agentic AI for Scientific Software Development

**Source:** http://arxiv.org/abs/2607.02703v1
**Tags:** `agentic, scientific-discovery`

## Core Methodology & Findings

**Authors:** Landung Setiawan, Anant Mittal, Cordero Core, Anshul Tambay, Carlos Garcia Jurado Suarez

### Abstract
In this paper, we describe LLMoxie, an institutional AI platform whose three-tiered architecture supports multi-cloud and on-premise inference, a LiteLLM/MLflow control plane for authentication, budgeting, PII masking, and observability, and an application augmentation layer for AI coding agents. Layered on top, an open-source RSE-Plugins ecosystem encodes accumulated RSE knowledge as a Plugin-Agent-Skill hierarchy spanning scientific Python practice, domain-specific knowledge, a six-phase research-and-implement workflow, and project lifecycle management. Scientific software is judged less by raw code quality than by whether it can be cited, audited, reproduced, and extended. Off-the-shelf AI coding agents, optimized against commercial software benchmarks, are poorly calibrated for this setting: they ignore the conventions of the scientific Python libraries they invoke, mishandle sensitive or embargoed data, and leave decision trails that are difficult to reconstruct after the fact. We report on twenty months of practice at a university-based research software engineering (RSE) center, where RSEs embedded across astronomy, earth and climate science, agriculture, and health projects worked to close this gap. We characterize the recurring infrastructure, governance, and process challenges of adopting Agentic AI inside a multi-domain RSE center, describe the platform and plugin design, and distill operational lessons from real scientific software deployments. Together, the platform and plugins shift AI coding agents from generic code generators into domain-aware collaborators that respect community norms and produce auditable provenance of technical reasoning.
