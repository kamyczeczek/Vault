---
type: Concept
id: 15_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 16/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

4. **[Context-Engineering（davidkimai）](https://github.com/davidkimai/Context-Engineering)**
   - 上下文工程第一性原理手册
   - 从基础原理到进阶技术

5. **[Context-Engineering（jasontang-ai）](https://github.com/jasontang-ai/Context-Engineering)**
   - 受 Karpathy 启发的第一性原理手册
   - 从提示工程迈向上下文设计、编排与优化

6. **[The Context Course（HuggingFace）](https://github.com/huggingface/context-course)**
   - HuggingFace 面向代码 agent 的上下文工程课程
   - 涵盖 skills、MCP、插件、子智能体、hooks，以及从零构建自己的 agent
   - 参考智能体：Claude Code、Codex、OpenCode

7. **[Agent Systems Handbook](https://github.com/Prompthon-IO/agent-systems-handbook)**
   - 实战 AI agents 手册，涵盖 agentic 工作流与多智能体架构
   - 横跨 LangGraph、MCP/A2A、上下文工程、agent 记忆、评估与可观测性

### 2026 上下文工程新动向：Harness、Skills 与协议

- **[deepseek-harness (dsh)](https://github.com/deepseek-ai/deepseek-harness)**：DeepSeek 官方开源 Agent 框架（2026-08）。追加式会话日志是模型上下文的*唯一*来源（"模型可见即已记录"），提示分节、工具 schema、技能与子 Agent 全部以可替换插件组合——上下文装配的参考设计
- **[Agent Skills 开放标准](https://agentskills.io/)**：以 `SKILL.md` 目录通过渐进式披露加载（名称/描述 → 完整指令 → 附带文件），已被 40+ Agent 采纳（Claude Code、Codex、Gemini CLI、Cursor、OpenCode、dsh…），是*程序性*上下文的可移植单元
- **[MCP 2026-07-28 规范](https://blog.modelcontextprotocol.io/posts/2026-07-28/)**：无状态核心、带 `ttlMs` 的可缓存 `tools/list`、头部路由——都是为了让工具上下文更便宜、更新鲜
- **[Claude Code 上下文文档](https://code.claude.com/docs/en/memory)**：CLAUDE.md 记忆层级、`/compact`、子 Agent 与 Hooks——被广泛借鉴的实用上下文管理模型

### Context工程系统与工具包
