---
type: Concept
id: 56_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 57/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Embeddings and / or [knowledge](https://arxiv.org/html/2501.13956v1?ref=blog.langchain.com#:~:text=In%20Zep%2C%20memory%20is%20powered,subgraph%2C%20and%20a%20community%20subgraph)[graphs](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/?ref=blog.langchain.com#:~:text=changes%20since%20updates%20can%20trigger,and%20holistic%20memory%20for%20agentic) for memory indexing are commonly used to assist with selection. Still, memory selection is challenging. At the AIEngineer World’s Fair, [Simon Willison shared](https://simonwillison.net/2025/Jun/6/six-months-in-llms/?ref=blog.langchain.com) an example of selection gone wrong: ChatGPT fetched his location from memories and unexpectedly injected it into a requested image. This type of unexpected or undesired memory retrieval can make some users feel like the context window “_no longer belongs to them_”!

**Tools**

Agents use tools, but can become overloaded if they are provided with too many. This is often because the tool descriptions overlap, causing model confusion about which tool to use. One approach is[to apply RAG (retrieval augmented generation) to tool descriptions](https://arxiv.org/abs/2410.14594?ref=blog.langchain.com) in order to fetch only the most relevant tools for a task. Some [recent papers](https://arxiv.org/abs/2505.03275?ref=blog.langchain.com) have shown that this improve tool selection accuracy by 3-fold.

**Knowledge**

[RAG](https://github.com/langchain-ai/rag-from-scratch?ref=blog.langchain.com) is a rich topic and it[can be a central context engineering challenge](https://x.com/_mohansolo/status/1899630246862966837?ref=blog.langchain.com). Code agents are some of the best examples of RAG in large-scale production. Varun from Windsurf captures some of these challenges well:

> _Indexing code ≠ context retrieval … [We are doing indexing & embedding search … [with] AST parsing code and chunking along semantically meaningful boundaries … embedding search becomes unreliable as a retrieval heuristic as the size of the codebase grows … we must rely on a combination of techniques like grep/file search, knowledge graph based retrieval, and … a re-ranking step where [context] is ranked in order of relevance._

### Compressing Context

_Compressing context involves retaining only the tokens required to perform a task._

**Context Summarization**
