---
type: Concept
id: 42_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 43/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

But, as we covered last time: if you treat your context like a junk drawer, the junk will [influence your response](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-confusion). If you want to learn more, here’s a [new course that looks great](https://maven.com/p/569540/i-don-t-use-rag-i-just-retrieve-documents).

![Image 3: A selection of guns from the videogame Destiny](https://www.dbreunig.com/img/tool_loadout.png)

### Tool Loadout

_Tool Loadout is the act of selecting only relevant tool definitions to add to your context._

The term “loadout” is a gaming term that refers to the specific combination of abilities, weapons, and equipment you select before a level, match, or round. Usually, your loadout is tailored to the context – the character, the level, the rest of your team’s makeup, and your own skillset.

Here, we’re borrowing the term to describe selecting the most relevant tools for a given task.

Perhaps the simplest way to select tools is to apply RAG to your tool descriptions. This is exactly what Tiantian Gan and Qiyao Sun did, which they detail in their paper, “[RAG MCP](https://arxiv.org/abs/2505.03275).” By storing their tool descriptions in a vector database, they’re able to select the most relevant tools given an input prompt.

When prompting DeepSeek-v3, the team found that selecting the the right tools becomes critical when you have more than 30 tools. Above 30, the descriptions of the tools begin to overlap, creating confusion. Beyond _100 tools_, the model was virtually guaranteed to fail their test. Using RAG techniques to select less than 30 tools yielded dramatically shorter prompts and resulted in as much as 3x better tool selection accuracy.

For smaller models, the problems begin long before we hit 30 tools. One paper we touched on last post, “[Less is More](https://arxiv.org/abs/2411.15399),” demonstrated that Llama 3.1 8b fails a benchmark when given 46 tools, but succeeds when given only 19 tools. The issue is context confusion, _not_ context window limitaions.

To address this issue, the team behind “Less is More” developed a way to dynamically select tools using a LLM-powered tool recommender. The LLM was prompted to reason about, “number and type of tools it ‘believes’ it requires to answer the user’s query.” This output was then semantically searched (tool RAG, again) to determine the final loadout. They tested this method with the [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html), finding Llama 3.1 8b performance improved by 44%.
