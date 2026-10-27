---
type: Concept
id: 59_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 60/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

It’s worth calling out that an agent’s runtime [state object](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state) can also be a great way to isolate context. This can serve the same purpose as sandboxing. A state object can be designed with a [schema](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#schema) that has fields that context can be written to. One field of the schema (e.g., `messages`) can be exposed to the LLM at each turn of the agent, but the schema can isolate information in other fields for more selective use.

### Context Engineering with LangSmith / LangGraph

So, how can you apply these ideas? Before you start, there are two foundational pieces that are helpful. First, ensure that you have a way to [look at your data](https://hamel.dev/blog/posts/evals/?ref=blog.langchain.com) and track token-usage across your agent. This helps inform where best to apply effort context engineering. [LangSmith](https://docs.smith.langchain.com/?ref=blog.langchain.com) is well-suited for agent [tracing / observability](https://docs.smith.langchain.com/observability?ref=blog.langchain.com), and offers a great way to do this. Second, be sure you have a simple way to test whether context engineering hurts or improve agent performance. LangSmith enables [agent evaluation](https://docs.smith.langchain.com/evaluation/tutorials/agents?ref=blog.langchain.com) to test the impact of any context engineering effort.

**Write context**

LangGraph was designed with both thread-scoped ([short-term](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#short-term-memory)) and [long-term memory](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#long-term-memory). Short-term memory uses [checkpointing](https://langchain-ai.github.io/langgraph/concepts/persistence/?ref=blog.langchain.com) to persist [agent state](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state) across all steps of an agent. This is extremely useful as a “scratchpad”, allowing you to write information to state and fetch it at any step in your agent trajectory.

LangGraph’s long-term memory lets you to persist context _across many sessions_ with your agent. It is flexible, allowing you to save small sets of [files](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#profile) (e.g., a user profile or rules) or larger [collections](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#collection) of memories. In addition, [LangMem](https://langchain-ai.github.io/langmem/?ref=blog.langchain.com) provides a broad set of useful abstractions to aid with LangGraph memory management.

**Select context**
