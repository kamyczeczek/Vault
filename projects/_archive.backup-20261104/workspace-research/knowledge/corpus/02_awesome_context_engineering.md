---
type: Concept
id: 02_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 3/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

### Don't Build Multi-Agents (Cognition)

- 📄 Original: [Cognition Blog](https://cognition.ai/blog/dont-build-multi-agents)

Principles for building reliable agents: share full context and avoid fragile parallel multi-agent architectures.

### The New Skill in AI is Not Prompting, It's Context Engineering (Philipp Schmid)

- 📄 Original: [philschmid.de](https://www.philschmid.de/context-engineering)

Argues most agent failures stem from poor context, not the model; breaks context into instructions, history, long-term memory, RAG, tools, and output format.

### Context Engineering (Simon Willison)

- 📄 Original: [simonwillison.net](https://simonwillison.net/2025/jun/27/context-engineering/)

Why "context engineering" is a better framing than "prompt engineering", curating the foundational discussion of the term.

### Wide Research: Beyond the Context Window (Manus)

- 📄 Original: [Manus Blog](https://manus.im/blog/manus-wide-research-solve-context-problem)

Parallel sub-agent architecture that avoids fabrication when processing many items, by decomposing tasks across dedicated sub-agents instead of one overloaded context window.

### SWE-grep: RL for Fast Context Retrieval (Cognition)

- 📄 Original: [Cognition Blog](https://cognition.ai/blog/swe-grep)

RL-trained models that run up to 8 parallel searches per turn to retrieve code context an order of magnitude faster while minimizing context pollution.

### Compaction Is a Lossy Operation

- https://loopandretry.github.io/posts/compaction-is-a-lossy-operation/

Why compacting an agent's context is lossy compression, not free summarization — what survives, what silently drops, and how it degrades long multi-turn runs.

## 📑 Research Papers

### Survey Papers

**A Survey of Context Engineering for Large Language Models**
- 📄 arXiv: [2507.13334](https://arxiv.org/abs/2507.13334)
- 📊 Comprehensive analysis of 1400+ research papers
- 🎯 Establishes formal taxonomy of context engineering components

> *The performance of Large Language Models (LLMs) is fundamentally determined by the contextual information provided during inference. This survey introduces Context Engineering, a formal discipline that transcends simple prompt design to encompass the systematic optimization of information payloads for LLMs.*

**Harness Engineering for Language Agents: The Harness Layer as Control, Agency, and Runtime**
- 📄 Preprints: [202603.1756](https://www.preprints.org/manuscript/202603.1756/v2)
- 📊 Audits 63 harness-relevant works across academia and public engineering practice
- 🎯 Decomposes the agent harness layer into Control, Agency, and Runtime (CAR); proposes HarnessCard as a reporting artifact

> *Situates harness engineering in the arc from software engineering through prompt and context engineering, arguing that the harness — the runtime loop wrapping tool execution, control, and agency around an LLM — is a first-class layer whose effects are often mistaken for model-driven gains.*
