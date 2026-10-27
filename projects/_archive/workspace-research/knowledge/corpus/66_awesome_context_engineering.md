---
type: Concept
id: 66_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 67/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

HuggingFace的[深度研究员](https://huggingface.co/blog/open-deep-research?ref=blog.langchain.com#:~:text=From%20building%20,it%20can%20still%20use%20it)展示了context隔离的另一个有趣例子。大多数智能体使用[工具调用API](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview?ref=blog.langchain.com)，它返回可以传递给工具（例如，搜索API）以获取工具反馈（例如，搜索结果）的JSON对象（工具参数）。HuggingFace使用[CodeAgent](https://huggingface.co/papers/2402.01030?ref=blog.langchain.com)，它输出包含所需工具调用的代码。然后代码在[沙箱](https://e2b.dev/?ref=blog.langchain.com)中运行。来自工具调用的选定context（例如，返回值）然后传递回LLM。

![Image 10](https://blog.langchain.com/content/images/2025/07/image-9.png)

沙箱可以将context从LLM中隔离出来。

这允许context在环境中与LLM隔离。Hugging Face注意到这是隔离token密集对象的绝佳方式：

> _[代码智能体允许]更好地处理状态...需要存储这个图像/音频/其他以供以后使用？没问题，只需将其分配为状态中的变量，你[以后可以使用它]。_

**状态**

值得指出的是，智能体的运行时[状态对象](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state)也可以是隔离context的绝佳方式。这可以与沙箱化起到相同的作用。状态对象可以设计为具有[模式](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#schema)，该模式具有可以写入context的字段。模式的一个字段（例如，`messages`）可以在智能体的每一轮中暴露给LLM，但模式可以将信息隔离在其他字段中以供更有选择性的使用。

### 使用LangSmith / LangGraph进行Context工程

那么，你如何应用这些想法呢？在开始之前，有两个基础部分是有帮助的。首先，确保你有一种方法来[查看你的数据](https://hamel.dev/blog/posts/evals/?ref=blog.langchain.com)并跟踪智能体的token使用情况。这有助于告知在哪里最好地应用context工程努力。[LangSmith](https://docs.smith.langchain.com/?ref=blog.langchain.com)非常适合智能体[跟踪/可观察性](https://docs.smith.langchain.com/observability?ref=blog.langchain.com)，并提供了一个很好的方法来做到这一点。其次，确保你有一个简单的方法来测试context工程是否损害或改善智能体性能。LangSmith启用[智能体评估](https://docs.smith.langchain.com/evaluation/tutorials/agents?ref=blog.langchain.com)来测试任何context工程努力的影响。

**写入context**

LangGraph设计时考虑了线程范围的（[短期](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#short-term-memory)）和[长期记忆](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#long-term-memory)。短期记忆使用[检查点](https://langchain-ai.github.io/langgraph/concepts/persistence/?ref=blog.langchain.com)来在智能体的所有步骤中持久化[智能体状态](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state)。这作为"scratchpad"非常有用，允许你将信息写入状态并在智能体轨迹的任何步骤中获取它。

LangGraph的长期记忆让你能够跨智能体的_多个会话_持久化context。它很灵活，允许你保存小的[文件](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#profile)集（例如，用户配置文件或规则）或更大的记忆[集合](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#collection)。此外，[LangMem](https://langchain-ai.github.io/langmem/?ref=blog.langchain.com)提供了一套广泛的有用抽象来帮助LangGraph记忆管理。

**选择context**

在LangGraph智能体的每个节点（步骤）内，你可以获取[状态](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state)。这为你在每个智能体步骤中向LLM呈现什么context提供了细粒度的控制。
