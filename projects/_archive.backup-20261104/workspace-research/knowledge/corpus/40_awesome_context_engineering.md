---
type: Concept
id: 40_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 41/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The arrival of million-token context windows felt transformative. The ability to throw everything an agent might need into the prompt inspired visions of superintelligent assistants that could access any document, connect to every tool, and maintain perfect memory.

But as we’ve seen, bigger contexts create new failure modes. Context poisoning embeds errors that compound over time. Context distraction causes agents to lean heavily on their context and repeat past actions rather than push forward. Context confusion leads to irrelevant tool or document usage. Context clash creates internal contradictions that derail reasoning.

These failures hit agents hardest because agents operate in exactly the scenarios where contexts balloon: gathering information from multiple sources, making sequential tool calls, engaging in multi-turn reasoning, and accumulating extensive histories.

Fortunately, there are solutions! In an upcoming post we’ll cover techniques for mitigating or avoding these issues, from methods for dynamically loading tools to spinning up context quarantines.

**Read the follow up article, “[How to Fix Your Context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html)“**

* * *

1.   Gemini 2.5 and GPT-4.1 have 1 million token context windows, large enough to throw [Infinite Jest](https://en.wikipedia.org/wiki/Infinite_Jest) in there, with plenty of room to spare.[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:longcontext)

2.   The “[Long form text](https://ai.google.dev/gemini-api/docs/long-context#long-form-text)” section in the Gemini docs sum up this optmism nicely.[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:googledocs)

3.   In fact, in the Databricks study cited above, a frequent way models would fail when given long contexts is they’d return summarizations of the provided context, while ignoring any instructions contained within the prompt.[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:summarization)

4.   If you’re on the leaderboard, pay attention to the, “Live (AST)” columns. [These metrics use real-world tool definitions contributed to the product by enterprise](https://gorilla.cs.berkeley.edu/blogs/12_bfcl_v2_live.html), “avoiding the drawbacks of dataset contamination and biased benchmarks.”[↩](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fnref:live)

================================================
FILE: docs/dbreunig/how-to-fix-your-context.md
================================================
Title: How to Fix Your Context

URL Source: https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html

Published Time: 2025-06-26T08:23:00-07:00

Markdown Content:
![Image 1](https://www.dbreunig.com/img/overload.jpg)

### Mitigating & Avoiding Context Failures
