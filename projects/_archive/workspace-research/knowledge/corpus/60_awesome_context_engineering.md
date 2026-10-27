---
type: Concept
id: 60_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 61/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Within each node (step) of a LangGraph agent, you can fetch [state](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state). This give you fine-grained control over what context you present to the LLM at each agent step.

In addition, LangGraph’s long-term memory is accessible within each node and supports various types of retrieval (e.g., fetching files as well as [embedding-based retrieval on a memory collection).](https://langchain-ai.github.io/langgraph/cloud/reference/cli/?ref=blog.langchain.com#adding-semantic-search-to-the-store) For an overview of long-term memory, see [our Deeplearning.ai course](https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/?ref=blog.langchain.com). And for an entry point to memory applied to a specific agent, see our [Ambient Agents](https://academy.langchain.com/courses/ambient-agents?ref=blog.langchain.com) course. This shows how to use LangGraph memory in a long-running agent that can manage your email and learn from your feedback.

![Image 11](https://blog.langchain.com/content/images/2025/07/image-10.png)

Email agent with user feedback and long-term memory

For tool selection, the [LangGraph Bigtool](https://github.com/langchain-ai/langgraph-bigtool?ref=blog.langchain.com) library is a great way to apply semantic search over tool descriptions. This helps select the most relevant tools for a task when working with a large collection of tools. Finally, we have several [tutorials and videos](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/?ref=blog.langchain.com) that show how to use various types of RAG with LangGraph.

**Compressing context**

Because LangGraph [is a low-level orchestration framework](https://blog.langchain.com/how-to-think-about-agent-frameworks/), you [lay out your agent as a set of nodes](https://www.youtube.com/watch?v=aHCDrAbH_go&ref=blog.langchain.com), [define](https://blog.langchain.com/how-to-think-about-agent-frameworks/) the logic within each one, and define an state object that is passed between them. This control offers several ways to compress context.

One common approach is to use a message list as your agent state and [summarize or trim](https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/?ref=blog.langchain.com#manage-short-term-memory) it periodically using [a few built-in utilities](https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/?ref=blog.langchain.com#manage-short-term-memory). However, you can also add logic to post-process [tool calls](https://github.com/langchain-ai/open_deep_research/blob/e5a5160a398a3699857d00d8569cb7fd0ac48a4f/src/open_deep_research/utils.py?ref=blog.langchain.com#L1407) or work phases of your agent in a few different ways. You can add summarization nodes at specific points or also add summarization logic to your tool calling node in order to compress the output of specific tool calls.

**Isolating context**
