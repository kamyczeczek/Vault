---
type: Concept
id: 08_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 9/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

### Production Tools

- **Claude Code**: Auto-compact context management
- **ChatGPT**: Long-term cross-session memory
- **[Puppyone](https://github.com/puppyone-ai/puppyone)**: File-system-based context storage for agents
- **Cursor**: Rules-based context engineering
- **Windsurf**: Advanced code context retrieval

## 💡 Expert Insights

### Industry Leaders

**Andrej Karpathy** (OpenAI)
~~~
+1 for "context engineering" over "prompt engineering".

People associate prompts with short task descriptions you'd give an LLM in your day-to-day use. When in every industrial-strength LLM app, context engineering is the delicate art and science of filling the context window with just the right information for the next step. Science because doing this right involves task descriptions and explanations, few shot examples, RAG, related (possibly multimodal) data, tools, state and history, compacting... Too little or of the wrong form and the LLM doesn't have the right context for optimal performance. Too much or too irrelevant and the LLM costs might go up and performance might come down. Doing this well is highly non-trivial. And art because of the guiding intuition around LLM psychology of people spirits.

On top of context engineering itself, an LLM app has to:
- break up problems just right into control flows
- pack the context windows just right
- dispatch calls to LLMs of the right kind and capability
- handle generation-verification UIUX flows
- a lot more - guardrails, security, evals, parallelism, prefetching, ...

So context engineering is just one small piece of an emerging thick layer of non-trivial software that coordinates individual LLM calls (and a lot more) into full LLM apps. The term "ChatGPT wrapper" is tired and really, really wrong.
~~~

### Key Principles

1. **KV-Cache Optimization**: Design for cache hit rates to reduce latency and cost
2. **Append-Only Context**: Avoid modifying previous context to maintain cache validity
3. **External Memory**: Use file systems and databases as extended context storage
4. **Error Preservation**: Keep failure traces for model learning and adaptation
5. **Diversity Over Uniformity**: Avoid repetitive patterns that lead to model drift

## 🔗 Model Context Protocol (MCP)

### Context7 MCP Server
**Up-to-date code documentation for LLMs and AI code editors**
- 🔗 Repository: [upstash/context7](https://github.com/upstash/context7)
- 🎯 Real-time code context for development workflows
- 🚀 Integration with popular AI coding assistants

### MCP Ecosystem
- **[Model Context Protocol](https://modelcontextprotocol.io/introduction)**: Standardized context sharing
- **[Filesystem Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)**: File-based context management
- **Tool Integration**: Seamless context flow between tools

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### How to Contribute
