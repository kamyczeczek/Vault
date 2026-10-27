---
type: Concept
id: 72_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 73/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

1.Keep your prompt prefix stable. Due to the [autoregressive](https://en.wikipedia.org/wiki/Autoregressive_model) nature of LLMs, even a single-token difference can invalidate the cache from that token onward. A common mistake is including a timestamp—especially one precise to the second—at the beginning of the system prompt. Sure, it lets the model tell you the current time, but it also kills your cache hit rate.

2.Make your context append-only. Avoid modifying previous actions or observations. Ensure your serialization is deterministic. Many programming languages and libraries don't guarantee stable key ordering when serializing JSON objects, which can silently break the cache.

3.Mark cache breakpoints explicitly when needed. Some model providers or inference frameworks don't support automatic incremental prefix caching, and instead require manual insertion of cache breakpoints in the context. When assigning these, account for potential cache expiration and at minimum, ensure the breakpoint includes the end of the system prompt.

Additionally, if you're self-hosting models using frameworks like [vLLM](https://github.com/vllm-project/vllm), make sure [prefix/prompt caching](https://docs.vllm.ai/en/stable/design/v1/prefix_caching.html) is enabled, and that you're using techniques like session IDs to route requests consistently across distributed workers.

### Mask, Don't Remove

As your agent takes on more capabilities, its action space naturally grows more complex—in plain terms, the number of tools explodes. The recent popularity of [MCP](https://modelcontextprotocol.io/introduction) only adds fuel to the fire. If you allow user-configurable tools, trust me: someone will inevitably plug hundreds of mysterious tools into your carefully curated action space. As a result, the model is more likely to select the wrong action or take an inefficient path. In short, your heavily armed agent gets dumber.

A natural reaction is to design a dynamic action space—perhaps loading tools on demand using something [RAG](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)-like. We tried that in Manus too. But our experiments suggest a clear rule: unless absolutely necessary, avoid dynamically adding or removing tools mid-iteration. There are two main reasons for this:

1.In most LLMs, tool definitions live near the front of the context after serialization, typically before or after the system prompt. So any change will invalidate the KV-cache for all subsequent actions and observations.

2.When previous actions and observations still refer to tools that are no longer defined in the current context, the model gets confused. Without [constrained decoding](https://platform.openai.com/docs/guides/structured-outputs), this often leads to schema violations or hallucinated actions.
