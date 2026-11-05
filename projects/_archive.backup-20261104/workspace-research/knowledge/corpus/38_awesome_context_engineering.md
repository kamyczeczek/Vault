---
type: Concept
id: 38_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 39/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

For smaller models, the distraction ceiling is much lower. A [Databricks study](https://www.databricks.com/blog/long-context-rag-performance-llms) found that model correctness began to fall around 32k for Llama 3.1 405b and earlier for smaller models.

If models start to misbehave long before their context windows are filled, what’s the point of super large context windows? In a nutshell: summarization[3](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:summarization) and fact retrieval. If you’re not doing either of those, be wary of your chosen model’s distraction ceiling.

### Context Confusion

_Context Confusion is when superfluous content in the context is used by the model to generate a low-quality response._

For a minute there, it really seemed like _everyone_ was going to ship an [MCP](https://www.dbreunig.com/2025/03/18/mcps-are-apis-for-llms.html). The dream of a powerful model, connected to _all_ your services and _stuff_, doing all your mundane tasks felt within reach. Just throw all the tool descriptions into the prompt and hit go. [Claude’s system prompt](https://www.dbreunig.com/2025/05/07/claude-s-system-prompt-chatbots-are-more-than-just-models.html) showed us the way, as it’s mostly tool definitions or instructions for using tools.

But even if [consolidation and competition don’t slow MCPs](https://www.dbreunig.com/2025/06/16/drawbridges-go-up.html), _Context Confusion_ will. It turns out there can be such a thing as too many tools.

The [Berkeley Function-Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) is a tool-use benchmark that evaluates the ability of models to effectively use tools to respond to prompts. Now on its 3rd version, the leaderboard shows that _every_ model performs worse when provided with more than one tool[4](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:live). Further, the Berkeley team, “designed scenarios where none of the provided functions are relevant…we expect the model’s output to be no function call.” Yet, all models will occasionally call tools that aren’t relevant.

Browsing the function-calling leaderboard, you can see the problem get worse as the models get smaller:

![Image 2](https://www.dbreunig.com/img/gemma_irrelevance.png)

A striking example of context confusion can be seen in a [recent paper](https://arxiv.org/pdf/2411.15399?) which evaluated small model performance on the [GeoEngine benchmark](https://arxiv.org/abs/2404.15500), a trial that features _46 different tools_. When the team gave a quantized (compressed) Llama 3.1 8b a query with all 46 tools it failed, even though the context was well within the 16k context window. But when they only gave the model 19 tools, it succeeded.
