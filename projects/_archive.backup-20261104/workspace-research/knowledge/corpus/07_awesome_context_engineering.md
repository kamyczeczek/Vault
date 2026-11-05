---
type: Concept
id: 07_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 8/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

- **[claude-mem](https://github.com/thedotmack/claude-mem)**: Persistent cross-session memory for Claude Code that automatically captures, compresses, and re-injects context across sessions
- **[Data Olympus](https://github.com/knaisoma/data-olympus)**: Governed project memory for coding agents. Agents can propose context, humans promote accepted rules, and retrieval serves only in-force knowledge after validity-window and supersession checks
- **[GoodMemory](https://github.com/hjqcan/GoodMemory)**: Local-first, auditable memory layer for AI apps and coding agents, with Codex/Claude Code host integration, a standalone MCP server, TypeScript/Python clients, and SQLite or Postgres storage
- **[LeanCTX (lean-ctx)](https://github.com/yvgude/lean-ctx)**: Context intelligence layer for AI agents — a single local Rust binary that decides what agents read, remember, and save; 60–90% fewer tokens, with 76 MCP tools and local-first design
- **[headroom](https://github.com/chopratejas/headroom)**: Compresses tool outputs/logs before they reach the LLM, saving 60-95% of tokens
- **[Accordion](https://github.com/a-Fig/Accordion)**: A pi extension that renders an agent's entire context window as a live "map" and folds (reversibly compacts) less-relevant blocks in the background via pluggable "conductors" that rank block relevance, instead of lossy all-or-nothing compaction
- **[Mnemoverse](https://github.com/mnemoverse/mcp-memory-server)**: Hosted persistent memory reachable over MCP from Claude Code, Cursor, VS Code and ChatGPT with one key; recall is re-ranked by whether a recalled memory helped or misled, and consolidation merges near-duplicates while protecting distinctive outliers
- **[Letta (MemGPT)](https://github.com/letta-ai/letta)**: Framework for building stateful agents with long-term memory
- **[Mem0](https://github.com/mem0ai/mem0)**: Memory layer for AI agents and assistants
- **[Vestige](https://github.com/samvallad33/vestige)**: "Local-first MCP memory server (single ~23MB Rust binary, data stays on-device) with entity/causal retrieval — links memories by shared file/env-var/service/symbol to recall the earlier change behind a later failure that similarity search can miss"
- **[Tree Ring Memory](https://github.com/TerminallyLazy/Tree-Ring-Memory)**: Lifecycle-aware local-first memory framework for AI agents with recall, audit, forgetting, consolidation, and project-scoped `.tree-ring` storage
- **[LLMLingua](https://github.com/microsoft/LLMLingua)**: Prompt compression for accelerated and cost-efficient LLM inference
- **[Cognee](https://github.com/topoteretes/cognee)**: Open-source AI memory platform giving agents persistent long-term memory via a self-hosted knowledge-graph engine
- **[Graphiti](https://github.com/getzep/graphiti)**: Framework for building real-time, temporal knowledge graphs for AI agents (the engine behind Zep's memory)
- **[Supermemory](https://github.com/supermemoryai/supermemory)**: Fast, scalable memory + context engine with a single Memory API; supports fully local runs
- **[skillreaper](https://github.com/thousandflowers/skillreaper)**: Measures what share of an agent's loaded context ever actually fires — skills, MCP servers, subagents, hooks — from session transcripts, then prunes the unused parts reversibly
- **[LWC](https://github.com/JanYork/llm-wiki-cli)**: Proactive, source-grounded project memory for coding agents, preserving immutable sources, citations, provenance, and atomic changesets with SQLite/FTS5 retrieval, optional document/code graphs, lifecycle hooks, and a bounded one-tool MCP interface
- **[billion-context-dsh](https://github.com/Tyan66666/billion-context-dsh)**: Model-driven context compression (Active Context Pruning) for the DeepSeek Harness — the model decides when and what to compress
