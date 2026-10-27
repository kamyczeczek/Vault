---
type: Concept
id: 64_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 65/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

如果智能体有保存记忆的能力，它们也需要选择与正在执行的任务相关的记忆的能力。这可能有几个原因很有用。智能体可能选择few-shot示例（[情节性](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#memory-types)[记忆](https://arxiv.org/pdf/2309.02427?ref=blog.langchain.com)）作为期望行为的示例，指令（[程序性](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#memory-types)[记忆](https://arxiv.org/pdf/2309.02427?ref=blog.langchain.com)）来引导行为，或事实（[语义](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#memory-types)[记忆](https://arxiv.org/pdf/2309.02427?ref=blog.langchain.com)）用于任务相关的context。

![Image 7](https://blog.langchain.com/content/images/2025/07/image-6.png)

一个挑战是确保选择相关的记忆。一些流行的智能体简单地使用一组狭窄的文件，这些文件_总是_被拉入context。例如，许多代码智能体使用特定文件来保存指令（"程序性"记忆）或在某些情况下保存示例（"情节性"记忆）。Claude Code使用[`CLAUDE.md`](http://claude.md/?ref=blog.langchain.com)。[Cursor](https://docs.cursor.com/context/rules?ref=blog.langchain.com)和[Windsurf](https://windsurf.com/editor/directory?ref=blog.langchain.com)使用规则文件。

但是，如果智能体存储更大的事实和/或关系[集合](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#collection)（例如，[语义](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#memory-types)记忆），选择就更困难了。[ChatGPT](https://help.openai.com/en/articles/8590148-memory-faq?ref=blog.langchain.com)是一个流行产品的好例子，它存储并从大量用户特定记忆中进行选择。

Embedding和/或[知识](https://arxiv.org/html/2501.13956v1?ref=blog.langchain.com#:~:text=In%20Zep%2C%20memory%20is%20powered,subgraph%2C%20and%20a%20community%20subgraph)[图](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/?ref=blog.langchain.com#:~:text=changes%20since%20updates%20can%20trigger,and%20holistic%20memory%20for%20agentic)用于记忆索引通常用于协助选择。尽管如此，记忆选择仍然具有挑战性。在AIEngineer World's Fair上，[Simon Willison分享了](https://simonwillison.net/2025/Jun/6/six-months-in-llms/?ref=blog.langchain.com)一个选择出错的例子：ChatGPT从记忆中获取了他的位置并意外地将其注入到请求的图像中。这种意外或不期望的记忆检索可能让一些用户感觉context窗口"_不再属于他们_"！

**工具**

智能体使用工具，但如果提供太多工具可能会过载。这通常是因为工具描述重叠，导致模型对使用哪个工具感到困惑。一种方法是[对工具描述应用RAG（检索增强生成）](https://arxiv.org/abs/2410.14594?ref=blog.langchain.com)，以便仅获取任务最相关的工具。一些[最近的论文](https://arxiv.org/abs/2505.03275?ref=blog.langchain.com)表明这将工具选择准确性提高了3倍。

**知识**

[RAG](https://github.com/langchain-ai/rag-from-scratch?ref=blog.langchain.com)是一个丰富的主题，它[可能是一个核心的context工程挑战](https://x.com/_mohansolo/status/1899630246862966837?ref=blog.langchain.com)。代码智能体是大规模生产中RAG的一些最佳示例。来自Windsurf的Varun很好地捕捉了其中一些挑战：

> _索引代码 ≠ context检索...我们正在进行索引和embedding搜索...[使用]AST解析代码并沿着语义有意义的边界进行分块...随着代码库规模的增长，embedding搜索作为检索启发式变得不可靠...我们必须依赖grep/文件搜索、基于知识图的检索等技术的组合，以及...一个重新排序步骤，其中[context]按相关性顺序排序。_

### 压缩Context

_压缩context涉及仅保留执行任务所需的token。_

**Context摘要**
