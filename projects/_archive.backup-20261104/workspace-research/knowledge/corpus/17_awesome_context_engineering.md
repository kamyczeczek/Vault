---
type: Concept
id: 17_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 18/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

### 开发框架

- **[LangGraph](https://langchain-ai.github.io/langgraph/)**：用于context管理的低级编排框架
- **[LangSmith](https://docs.smith.langchain.com/)**：智能体追踪和评估平台
- **[LangMem](https://langchain-ai.github.io/langmem/)**：内存管理抽象

### 记忆与压缩

- **[claude-mem](https://github.com/thedotmack/claude-mem)**：面向 Claude Code 的跨会话持久记忆，自动捕获、压缩并在会话间回注上下文
- **[GoodMemory](https://github.com/hjqcan/GoodMemory)**：面向 AI 应用与编程智能体的本地优先、可审计记忆层，支持 Codex/Claude Code 主机集成、独立 MCP 服务、TypeScript/Python 客户端，以及 SQLite 或 Postgres 存储
- **[LeanCTX (lean-ctx)](https://github.com/yvgude/lean-ctx)**：面向 AI agent 的上下文智能层——单个本地 Rust 二进制决定 agent 读取、记忆与保存什么；token 减少 60–90%，提供 76 个 MCP 工具，本地优先
- **[headroom](https://github.com/chopratejas/headroom)**：在内容进入 LLM 前压缩工具输出/日志，节省 60-95% 的 token
- **[Accordion](https://github.com/a-Fig/Accordion)**：一个 pi 扩展,将 agent 的整个上下文窗口渲染为实时"地图",并通过可插拔的"conductor"(对各块相关性打分)在后台折叠(可逆地压缩)相关性较低的块,替代有损的全量压缩
- **[Letta (MemGPT)](https://github.com/letta-ai/letta)**：构建具备长期记忆的有状态智能体框架
- **[Mem0](https://github.com/mem0ai/mem0)**：面向AI智能体和助手的记忆层
- **[Vestige](https://github.com/samvallad33/vestige)**：“本地优先的记忆 MCP 服务器（单个约 23MB Rust 二进制，数据保留在本地），支持实体/因果检索——通过共享的文件、环境变量、服务、符号关联记忆，回溯出导致后续故障、相似度检索可能遗漏的更早改动”
- **[Tree Ring Memory](https://github.com/TerminallyLazy/Tree-Ring-Memory)**：面向 AI 智能体的生命周期感知、本地优先记忆框架，支持 recall、audit、forgetting、consolidation，以及项目级 `.tree-ring` 存储
- **[LLMLingua](https://github.com/microsoft/LLMLingua)**：prompt压缩，加速并降低LLM推理成本
- **[Cognee](https://github.com/topoteretes/cognee)**：开源 AI 记忆平台，通过自托管知识图谱引擎为智能体提供跨会话的持久长期记忆
- **[Graphiti](https://github.com/getzep/graphiti)**：为 AI 智能体构建实时、时序感知知识图谱的框架（Zep 记忆基础设施的核心引擎）
- **[Supermemory](https://github.com/supermemoryai/supermemory)**：快速、可扩展的记忆与上下文引擎，提供统一 Memory API，支持完全本地运行
- **[skillreaper](https://github.com/thousandflowers/skillreaper)**：基于会话记录统计智能体加载的 context 中真正被调用的比例（技能、MCP 服务器、子智能体、hooks），并可逆地清理未使用的部分
- **[LWC](https://github.com/JanYork/llm-wiki-cli)**：面向编码智能体的主动式、来源可追溯项目记忆，保存不可变原始资料、引用、来源链与原子变更集，提供 SQLite/FTS5 检索、可选文档图与代码图、生命周期 Hook，以及受限的单工具 MCP 接口
- **[billion-context-dsh](https://github.com/Tyan66666/billion-context-dsh)**：面向 DeepSeek Harness 的模型驱动上下文压缩（Active Context Pruning）——由模型决定何时压缩、压缩什么

### 生产工具

- **Claude Code**：自动压缩context管理
- **ChatGPT**：跨会话长期记忆
- **[Puppyone](https://github.com/puppyone-ai/puppyone)**：面向智能体的文件系统式context存储
- **Cursor**：基于规则的context工程
- **Windsurf**：高级代码context检索

## 💡 专家观点

### 行业领袖

**Andrej Karpathy**

```
+1 支持“上下文工程”优于“提示工程”。

人们通常把“提示”理解为你在日常使用大语言模型（LLM）时给出的简短任务描述。而在每一个工业级的LLM应用中，“上下文工程”才是真正的精细艺术与科学——它是在上下文窗口中为下一步填充恰到好处的信息。说它是科学，是因为做好这件事需要任务描述与解释、few-shot 示例、RAG、相关（可能是多模态的）数据、工具、状态与历史、信息压缩……信息太少或形式不对，LLM就无法获得最佳表现所需的上下文；信息太多或太无关，LLM的成本会上升，性能反而可能下降。要做好这件事绝非易事。而说它是艺术，则是因为这背后有着对LLM“心理”与人类精神的直觉把握。

除了上下文工程本身，LLM应用还需要：
 • 恰当地将问题拆解为控制流
 • 恰当地填充上下文窗口
 • 调度合适类型和能力的LLM
 • 处理生成-验证的UI/UX流程
 • 还有很多其他工作——安全防护、评估、并行处理、预取……

所以，上下文工程只是正在兴起的一整套复杂软件体系中的一小部分，这套体系将单次LLM调用（以及更多内容）协调成完整的LLM应用。“ChatGPT封装器”这个说法已经过时，而且真的非常不准确。
```

### 关键原则
