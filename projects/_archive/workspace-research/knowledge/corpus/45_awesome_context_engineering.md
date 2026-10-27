---
type: Concept
id: 45_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 46/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

One could employ Provence or a similar function to cull down documents or the entire context. Further, this pattern is a strong argument for maintaining a _structured_[1](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#fn:structure) version of your context in a dictionary or other form, from which you assemble a compiled string prior to every LLM call. This structure would come in handy when pruning, allowing you to ensure the main instructions and goals are preserved while the document or history sections can be pruned or summarized.

![Image 6: A duck press](https://www.dbreunig.com/img/context_summarization.png)

### Context Summarization

_Context Summarization is the act of boiling down an accrued context into a condensed summary._

Context Summarization first appeared as a tool for dealing with smaller context windows. As your chat session came close to exceeding the maximum context length, a summary would be generated and a new thread would begin. Chatbot users did this manually, in ChatGPT or Claude, asking the bot to generate a short recap which would then be pasted into a new session.

However, as context windows increased, agent builders discovered there’s benefits to summarization beyond staying within the total context limit. As the context grows, it becomes distracting and causes the model to rely less on what it learned during training. We called this [Context Distraction](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-distraction). The team behind the Pokémon-playing Gemini agent discovered anything beyond 100,000 tokens triggered this behavior:

> While Gemini 2.5 Pro supports 1M+ token context, making effective use of it for agents presents a new research frontier. In this agentic setup, it was observed that as the context grew significantly beyond 100k tokens, the agent showed a tendency toward favoring repeating actions from its vast history rather than synthesizing novel plans. This phenomenon, albeit anecdotal, highlights an important distinction between long-context for retrieval and long-context for multi-step, generative reasoning.

Summarizing your context is easy to do, but hard to perfect for any given agent. Knowing what information should be preserved, and detailing that to an LLM-powered compression step, is critical for agent builders. It’s worth breaking out this function as it’s own LLM-powered stage or app, which allows you to collect evaluation data that can inform and optimize this task directly.

![Image 7: A banker's box](https://www.dbreunig.com/img/context_offload.png)

### Context Offloading

_Context Offloading is the act of storing information outside the LLM’s context, usually via a tool that stores and manages the data._

This might be my favorite tactic, if only because it’s so _simple_ you don’t believe it will work.
