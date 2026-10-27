---
type: Concept
id: 61_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 62/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

LangGraph is designed around a [state](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state) object, allowing you to specify a state schema and access state at each agent step. For example, you can store context from tool calls in certain fields in state, isolating them from the LLM until that context is required. In addition to state, LangGraph supports use of sandboxes for context isolation. See this [repo](https://github.com/jacoblee93/mini-chat-langchain?tab=readme-ov-file&ref=blog.langchain.com) for an example LangGraph agent that uses [an E2B sandbox](https://e2b.dev/?ref=blog.langchain.com) for tool calls. See this [video](https://www.youtube.com/watch?v=FBnER2sxt0w&ref=blog.langchain.com) for an example of sandboxing using Pyodide where state can be persisted. LangGraph also has a lot of support for building multi-agent architecture, such as the [supervisor](https://github.com/langchain-ai/langgraph-supervisor-py?ref=blog.langchain.com) and [swarm](https://github.com/langchain-ai/langgraph-swarm-py?ref=blog.langchain.com) libraries. You can [see](https://www.youtube.com/watch?v=4nZl32FwU-o&ref=blog.langchain.com)[these](https://www.youtube.com/watch?v=JeyDrn1dSUQ&ref=blog.langchain.com)[videos](https://www.youtube.com/watch?v=B_0TNuYi56w&ref=blog.langchain.com) for more detail on using multi-agent with LangGraph.

### Conclusion

Context engineering is becoming a craft that agents builders should aim to master. Here, we covered a few common patterns seen across many popular agents today:

*   _Writing context - saving it outside the context window to help an agent perform a task._
*   _Selecting context - pulling it into the context window to help an agent perform a task._
*   _Compressing context - retaining only the tokens required to perform a task._
*   _Isolating context - splitting it up to help an agent perform a task._

LangGraph makes it easy to implement each of them and LangSmith provides an easy way to test your agent and track context usage. Together, LangGraph and LangGraph enable a virtuous feedback loop for identifying the best opportunity to apply context engineering, implementing it, testing it, and repeating.

================================================
FILE: docs/langchain/智能体的Context工程-中文版.md
================================================
# 智能体的Context工程

原文链接：https://blog.langchain.com/context-engineering-for-agents/

发布时间：2025-07-02T15:52:42.000Z

### 摘要

智能体需要context来执行任务。Context工程是在智能体轨迹的每一步中，用恰当的信息填充context窗口的艺术和科学。在这篇文章中，我们通过回顾各种流行的智能体和论文，分解了一些常见的策略——**写入、选择、压缩和隔离**——用于context工程。然后我们解释LangGraph是如何设计来支持它们的！

**另外，请观看我们关于context工程的视频**[**这里**](https://youtu.be/4GiqzUHD5AA?ref=blog.langchain.com)**。**

![Image 1](https://blog.langchain.com/content/images/2025/07/image.png)

Context工程的一般类别

### Context工程
