---
type: Concept
title: "LLM Agents for Interactive Workflow Provenance: Reference Architecture and Evaluation Methodology"
source: "http://arxiv.org/abs/2509.13978v2"
tags: [agentic, scientific-discovery]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# LLM Agents for Interactive Workflow Provenance: Reference Architecture and Evaluation Methodology

**Source:** http://arxiv.org/abs/2509.13978v2
**Tags:** `agentic, scientific-discovery`

## Core Methodology & Findings

**Authors:** Renan Souza, Timothy Poteet, Brian Etz, Daniel Rosendo, Amal Gueroudji

### Abstract
Modern scientific discovery increasingly relies on workflows that process data across the Edge, Cloud, and High Performance Computing (HPC) continuum. Comprehensive and in-depth analyses of these data are critical for hypothesis validation, anomaly detection, reproducibility, and impactful findings. Although workflow provenance techniques support such analyses, at large scale, the provenance data become complex and difficult to analyze. Existing systems depend on custom scripts, structured queries, or static dashboards, limiting data interaction. In this work, we introduce an evaluation methodology, reference architecture, and open-source implementation that leverages interactive Large Language Model (LLM) agents for runtime data analysis. Our approach uses a lightweight, metadata-driven design that translates natural language into structured provenance queries. Evaluations across LLaMA, GPT, Gemini, and Claude, covering diverse query classes and a real-world chemistry workflow, show that modular design, prompt tuning, and Retrieval-Augmented Generation (RAG) enable accurate and insightful LLM agent responses beyond recorded provenance.
