---
type: Concept
id: 04_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 5/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

3. **[Context Engineering Intro](https://github.com/coleam00/context-engineering-intro)**
   - Practical guide for AI coding assistants
   - Claude Code centered approach
   - Hands-on implementation strategies

4. **[Context-Engineering (davidkimai)](https://github.com/davidkimai/Context-Engineering)**
   - First-principles handbook for context engineering
   - From foundations to advanced techniques

5. **[Context-Engineering (jasontang-ai)](https://github.com/jasontang-ai/Context-Engineering)**
   - Karpathy-inspired first-principles handbook
   - From prompt engineering toward context design, orchestration, and optimization

6. **[The Context Course (HuggingFace)](https://github.com/huggingface/context-course)**
   - HuggingFace course on context engineering for code agents
   - Covers skills, MCP, plugins, subagents, hooks, and building your own agent
   - Reference agents: Claude Code, Codex, OpenCode

7. **[Agent Systems Handbook](https://github.com/Prompthon-IO/agent-systems-handbook)**
   - Practical AI agents handbook covering agentic workflows and multi-agent architecture
   - Spans LangGraph, MCP/A2A, context engineering, agent memory, evaluation, and observability

### Context Engineering in 2026: Harnesses, Skills & Protocols

- **[deepseek-harness (dsh)](https://github.com/deepseek-ai/deepseek-harness)**: DeepSeek's official open-source agent harness (Aug 2026). Its append-only session log is the *only* source of model context ("model-visible means logged"), with prompt sections, tool schemas, skills and sub-agents all composed as swappable plugins — a reference design for context assembly
- **[Agent Skills open standard](https://agentskills.io/)**: `SKILL.md` folders loaded via progressive disclosure (name/description → full instructions → bundled files), adopted by 40+ agents (Claude Code, Codex, Gemini CLI, Cursor, OpenCode, dsh...). Skills are the portable unit of *procedural* context
- **[MCP 2026-07-28 spec](https://blog.modelcontextprotocol.io/posts/2026-07-28/)**: stateless core, cacheable `tools/list` results with `ttlMs`, and header-based routing — all aimed at keeping tool context cheap and fresh for agents
- **[Claude Code context docs](https://code.claude.com/docs/en/memory)**: CLAUDE.md memory hierarchy, `/compact`, subagents and hooks — the most widely copied practical context-management model

### Context Engineering Systems & Kits
