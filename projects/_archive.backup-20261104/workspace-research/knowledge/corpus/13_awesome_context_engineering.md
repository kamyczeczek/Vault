---
type: Concept
id: 13_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 14/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![GitHub stars](https://img.shields.io/github/stars/yzfly/awesome-context-engineering.svg?style=social&label=Star)](https://github.com/yzfly/awesome-context-engineering)
[![GitHub forks](https://img.shields.io/github/forks/yzfly/awesome-context-engineering.svg?style=social&label=Fork)](https://github.com/yzfly/awesome-context-engineering)

精心整理的**Context工程**资源集合，涵盖AI智能体和大语言模型(LLM)的相关资源、论文、工具和最佳实践。

> Context工程是在智能体轨迹的每一步中，用恰当的信息填充context窗口的艺术和科学。

[中文版本](README_CN.md) | [English](README.md)

## 📚 目录

- [什么是Context工程？](#什么是context工程)
- [精选文章](#精选文章)
- [研究论文](#研究论文)
- [工具与项目](#工具与项目)
- [专家观点](#专家观点)
- [模型Context协议 (MCP)](#模型context协议-mcp)
- [贡献指南](#贡献指南)
- [Star历史](#star历史)

## 什么是Context工程？

Context工程是对大语言模型(LLM)信息负载的系统性优化。它包括：

- **Context检索与生成**：选择和创建相关信息
- **Context处理**：组织和构建context以实现最佳消费
- **Context管理**：处理context窗口、内存和跨交互状态
- **Context压缩**：在保留关键信息的同时减少token使用
- **Context隔离**：在不同context空间中分离关注点

## 📖 精选文章

### Context Rot：增加输入token如何影响LLM性能
- https://research.trychroma.com/context-rot

### Manus Context工程
**AI智能体的Context工程：构建Manus的经验教训**
- 📄 原文：[Manus博客](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- 🇨🇳 中文翻译：[AI智能体的Context工程：构建Manus的经验教训.md](docs/manus/AI智能体的Context工程：构建Manus的经验教训.md)

构建生产级AI智能体的关键洞察：
- 围绕KV-Cache进行设计以优化性能
- 掩码而非移除工具以改善动作选择
- 使用文件系统作为外部context内存
- 通过复述技术操纵注意力

### Claude Code 最佳实践
**Claude Code 最佳实践指南**
- 📄 原文：[Anthropic 官方文档](https://www.anthropic.com/engineering/claude-code-best-practices)
- 🇨🇳 中文翻译：[claude-code-best-practices](docs/claudecode/claude-code-best-practices-zh.md)

### Claude 有效上下文工程
**AI智能体的有效上下文工程**
- 📄 原文：[Anthropic 官方文档](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- 🇨🇳 中文翻译：[有效上下文工程.md](docs/claudecode/effective-context-engineering-for-ai-agents.md)
- 📄 [Context 编辑与 memory 工具](https://www.anthropic.com/news/context-management)
- [我们如何构建多智能体研究系统](https://www.anthropic.com/engineering/multi-agent-research-system)
- [为 AI 智能体编写高效工具](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [通过代码执行使用 MCP：构建更高效的智能体](https://www.anthropic.com/engineering/code-execution-with-mcp)

### LangChain Context工程
**智能体的Context工程**
- 📄 原文：[LangChain博客](https://blog.langchain.com/context-engineering-for-agents/)
- 🇨🇳 中文翻译：[智能体的Context工程-中文版.md](docs/langchain/智能体的Context工程-中文版.md)

涵盖四大关键策略的综合指南：
- **写入Context**：将信息保存在context窗口之外
- **选择Context**：将相关信息拉入context
- **压缩Context**：仅保留必要的token
- **隔离Context**：在不同空间中分割context

### dbreunig Context工程系列
**长Context的失效原理和解决方案**
- 📄 原文 Part 1：[长Context如何失效](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)
- 🇨🇳 中文翻译：[长上下文的失效原理及解决方案.md](docs/dbreunig/长上下文的失效原理及解决方案.md)
- 📄 原文 Part 2：[如何修复你的Context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html)
- 🇨🇳 中文翻译：[上下文修复的实用指南.md](docs/dbreunig/上下文修复的实用指南.md)

深入探讨context失效模式和管理策略：
- Context污染、分散、混乱和冲突模式分析
- RAG、工具配置、context隔离、修剪、总结和卸载技术
