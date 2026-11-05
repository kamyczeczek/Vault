---
type: Concept
id: 51_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 52/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

> 我们发现LLM经常在早期轮次中做出假设并过早地尝试生成最终解决方案，然后过度依赖这些解决方案。简单来说，我们发现当LLM在对话中走错方向时，它们会迷失并不会恢复。

这对智能体构建者来说不是好兆头。智能体从文档、工具调用和其他被分配子问题的模型中组装上下文。所有这些上下文，从不同来源提取，都有可能与自身产生分歧。此外，当你连接到不是你创建的MCP工具时，它们的描述和指令与你提示词的其余部分发生冲突的可能性更大。

* * *

百万标记上下文窗口的到来感觉是变革性的。能够将智能体可能需要的一切扔进提示词的能力激发了对超智能助手的愿景，这些助手可以访问任何文档，连接到每个工具，并保持完美记忆。

但正如我们所看到的，更大的上下文创造了新的失效模式。上下文污染嵌入随时间复合的错误。上下文分散导致智能体严重依赖其上下文并重复过去的动作，而不是向前推进。上下文混乱导致不相关的工具或文档使用。上下文冲突创造内部矛盾，使推理脱轨。

这些失效对智能体的冲击最大，因为智能体恰好在上下文会膨胀的场景中运行：从多个来源收集信息，进行顺序工具调用，参与多轮推理，并积累广泛的历史记录。

幸运的是，有解决方案！在即将发布的文章中，我们将介绍缓解或避免这些问题的技术，从动态加载工具的方法到建立上下文隔离。

**阅读后续文章，"[如何修复你的上下文](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html)"**

* * *

1. Gemini 2.5和GPT-4.1有100万标记上下文窗口，大到足以把[无尽玩笑](https://en.wikipedia.org/wiki/Infinite_Jest)扔进去，还有大量空间剩余。[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:longcontext)

2. Gemini文档中的"[长形式文本](https://ai.google.dev/gemini-api/docs/long-context#long-form-text)"部分很好地总结了这种乐观情绪。[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:googledocs)

3. 事实上，在上面引用的Databricks研究中，当给定长上下文时模型失效的一个常见方式是它们会返回提供的上下文的摘要，而忽略提示词中包含的任何指令。[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:summarization)

4. 如果你在排行榜上，请注意"Live (AST)"列。[这些指标使用企业向产品贡献的真实工具定义](https://gorilla.cs.berkeley.edu/blogs/12_bfcl_v2_live.html)，"避免了数据集污染和有偏基准的缺点。"[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:live)

================================================
FILE: docs/langchain/context-engineering-for-agents.md
================================================
Title: Context Engineering

URL Source: https://blog.langchain.com/context-engineering-for-agents/

Published Time: 2025-07-02T15:52:42.000Z

Markdown Content:
### TL;DR

Agents need context to perform tasks. Context engineering is the art and science of filling the context window with just the right information at each step of an agent’s trajectory. In this post, we break down some common strategies — **write, select, compress, and isolate —** for context engineering by reviewing various popular agents and papers. We then explain how LangGraph is designed to support them!

**Also, see our video on context engineering**[**here**](https://youtu.be/4GiqzUHD5AA?ref=blog.langchain.com)**.**

![Image 1](https://blog.langchain.com/content/images/2025/07/image.png)

General categories of context engineering

### Context Engineering
