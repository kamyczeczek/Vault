---
type: Concept
id: 67_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 68/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

此外，LangGraph的长期记忆在每个节点内都是可访问的，并支持各种类型的检索（例如，获取文件以及[对记忆集合进行基于embedding的检索](https://langchain-ai.github.io/langgraph/cloud/reference/cli/?ref=blog.langchain.com#adding-semantic-search-to-the-store)）。有关长期记忆的概述，请参阅[我们的Deeplearning.ai课程](https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/?ref=blog.langchain.com)。有关应用于特定智能体的记忆入门点，请参阅我们的[Ambient Agents](https://academy.langchain.com/courses/ambient-agents?ref=blog.langchain.com)课程。这展示了如何在可以管理你的电子邮件并从你的反馈中学习的长期运行智能体中使用LangGraph记忆。

![Image 11](https://blog.langchain.com/content/images/2025/07/image-10.png)

具有用户反馈和长期记忆的电子邮件智能体

对于工具选择，[LangGraph Bigtool](https://github.com/langchain-ai/langgraph-bigtool?ref=blog.langchain.com)库是对工具描述应用语义搜索的绝佳方式。这有助于在处理大量工具集合时为任务选择最相关的工具。最后，我们有几个[教程和视频](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/?ref=blog.langchain.com)展示如何在LangGraph中使用各种类型的RAG。

**压缩context**

因为LangGraph[是一个低级编排框架](https://blog.langchain.com/how-to-think-about-agent-frameworks/)，你[将智能体布局为一组节点](https://www.youtube.com/watch?v=aHCDrAbH_go&ref=blog.langchain.com)，[定义](https://blog.langchain.com/how-to-think-about-agent-frameworks/)每个节点内的逻辑，并定义在它们之间传递的状态对象。这种控制提供了几种压缩context的方法。

一种常见方法是使用消息列表作为智能体状态，并使用[一些内置实用程序](https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/?ref=blog.langchain.com#manage-short-term-memory)定期[摘要或修剪](https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/?ref=blog.langchain.com#manage-short-term-memory)它。但是，你也可以添加逻辑来后处理[工具调用](https://github.com/langchain-ai/open_deep_research/blob/e5a5160a398a3699857d00d8569cb7fd0ac48a4f/src/open_deep_research/utils.py?ref=blog.langchain.com#L1407)或智能体的工作阶段，有几种不同的方法。你可以在特定点添加摘要节点，或者也可以向工具调用节点添加摘要逻辑，以压缩特定工具调用的输出。

**隔离context**

LangGraph围绕[状态](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state)对象设计，允许你指定状态模式并在每个智能体步骤中访问状态。例如，你可以将工具调用的context存储在状态的某些字段中，将它们与LLM隔离，直到需要该context。除了状态之外，LangGraph还支持使用沙箱进行context隔离。请参阅此[repo](https://github.com/jacoblee93/mini-chat-langchain?tab=readme-ov-file&ref=blog.langchain.com)以获取使用[E2B沙箱](https://e2b.dev/?ref=blog.langchain.com)进行工具调用的LangGraph智能体示例。请参阅此[视频](https://www.youtube.com/watch?v=FBnER2sxt0w&ref=blog.langchain.com)以获取使用Pyodide进行沙箱化的示例，其中状态可以持久化。LangGraph还对构建多智能体架构有很多支持，如[supervisor](https://github.com/langchain-ai/langgraph-supervisor-py?ref=blog.langchain.com)和[swarm](https://github.com/langchain-ai/langgraph-swarm-py?ref=blog.langchain.com)库。你可以[查看](https://www.youtube.com/watch?v=4nZl32FwU-o&ref=blog.langchain.com)[这些](https://www.youtube.com/watch?v=JeyDrn1dSUQ&ref=blog.langchain.com)[视频](https://www.youtube.com/watch?v=B_0TNuYi56w&ref=blog.langchain.com)以获取有关在LangGraph中使用多智能体的更多详细信息。

### 结论

Context工程正在成为智能体构建者应该努力掌握的一门技艺。在这里，我们涵盖了今天许多流行智能体中看到的几种常见模式：

* _写入context - 将其保存在context窗口之外以帮助智能体执行任务。_
* _选择context - 将其拉入context窗口以帮助智能体执行任务。_
* _压缩context - 仅保留执行任务所需的token。_
* _隔离context - 将其分割以帮助智能体执行任务。_
