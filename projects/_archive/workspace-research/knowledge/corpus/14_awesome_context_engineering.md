---
type: Concept
id: 14_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 15/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

### 编程智能体的高级上下文工程实践

- [GitHub](https://github.com/humanlayer/humanlayer)
- [YouTube](https://humanlayer.dev/youtube)

在复杂代码库中使用AI解决难题的指南。

### 不要构建多智能体（Cognition）

- 📄 原文：[Cognition 博客](https://cognition.ai/blog/dont-build-multi-agents)

构建可靠智能体的原则：共享完整上下文，避免脆弱的并行多智能体架构。

### AI 的新技能不是提示工程，而是上下文工程（Philipp Schmid）

- 📄 原文：[philschmid.de](https://www.philschmid.de/context-engineering)

指出多数智能体失败源于 context 不足而非模型能力，将 context 拆解为指令、历史、长期记忆、RAG、工具与输出格式。

### 上下文工程（Simon Willison）

- 📄 原文：[simonwillison.net](https://simonwillison.net/2025/jun/27/context-engineering/)

论述为何 "context engineering" 比 "prompt engineering" 更贴切，梳理并串联了该术语的奠基性讨论。

### 宽度研究：超越上下文窗口（Manus）

- 📄 原文：[Manus 博客](https://manus.im/blog/manus-wide-research-solve-context-problem)

通过将任务拆分给多个专职子智能体并行处理，避免单一超载上下文窗口在处理大量条目时出现的编造问题。

### SWE-grep：面向快速上下文检索的强化学习（Cognition）

- 📄 原文：[Cognition 博客](https://cognition.ai/blog/swe-grep)

用强化学习训练、每轮最多 8 路并行检索的模型，在最小化 context 污染的同时将代码上下文检索速度提升一个数量级。

### 压缩是一种有损操作

- https://loopandretry.github.io/posts/compaction-is-a-lossy-operation/

为什么压缩智能体的 context 是有损压缩，而非免费的摘要——哪些信息被保留、哪些被悄悄丢弃，以及它如何逐渐劣化长的多轮运行。

## 📑 研究论文

### 综述论文

**大语言模型Context工程综述**
- 📄 arXiv：[2507.13334](https://arxiv.org/abs/2507.13334)
- 📊 对1400+研究论文的综合分析
- 🎯 建立了context工程组件的正式分类法

> *大语言模型(LLM)的性能从根本上由推理过程中提供的上下文信息决定。本综述介绍了Context工程，这是一门超越简单prompt设计的正式学科，涵盖了对LLM信息负载的系统性优化。*

**Context Engineering 2.0：上下文工程的语境**
- 📄 arXiv：[2510.26493](https://arxiv.org/abs/2510.26493)
- 🎯 将上下文工程追溯二十余年，系统性给出定义，并梳理从人机交互到人-智能体范式的设计原则

**Agentic Context Engineering：面向自我改进语言模型的演化式上下文**
- 📄 arXiv：[2510.04618](https://arxiv.org/abs/2510.04618)
- 🎯 将 context 视为可演化的 playbook（生成器/反思器/整理器），避免 context 坍塌；智能体任务 +10.6%、金融 +8.6%（ICLR 2026）

**AI 智能体时代的记忆：综述**
- 📄 arXiv：[2512.13564](https://arxiv.org/abs/2512.13564)
- 🎯 提出"形态-功能-动态"多维记忆分类法，并厘清 agent memory 与 RAG、上下文工程的区别

### 核心研究领域

- **记忆系统**：[Reflexion](https://arxiv.org/abs/2303.11366)、[生成式智能体](https://ar5iv.labs.arxiv.org/html/2304.03442)、[StructMem](https://arxiv.org/abs/2604.21748)（[代码](https://github.com/zjunlp/LightMem)）
- **检索增强生成**：[RAG综述](https://github.com/langchain-ai/rag-from-scratch)
- **工具集成**：[工具选择](https://arxiv.org/abs/2410.14594)、[BigTool](https://arxiv.org/abs/2505.03275)
- **Context压缩**：[递归摘要](https://arxiv.org/pdf/2308.15022)、[Context修剪](https://arxiv.org/abs/2501.16214)、[TokenPilot](https://arxiv.org/abs/2606.17016)（[代码](https://github.com/zjunlp/LightRSI)）
- **长Context局限**：[Lost in the Middle](https://arxiv.org/abs/2307.03172)

## 🛠️ 工具与项目

### 综合资源

1. **[提示工程指南](https://github.com/dair-ai/Prompt-Engineering-Guide)**
   - 提示工程、上下文工程、RAG 与 AI 智能体综合指南
   - 涵盖技术、论文、工具与最佳实践
   - 广泛使用的教学资源

2. **[Awesome Context工程综述](https://github.com/Meirtz/Awesome-Context-Engineering)**
   - context工程技术的综合调研
   - 方法论和应用概述
   - 学术研究重点

3. **[Context工程入门](https://github.com/coleam00/context-engineering-intro)**
   - AI编程助手的实用指南
   - 以Claude Code为中心的方法
   - 实践实施策略
