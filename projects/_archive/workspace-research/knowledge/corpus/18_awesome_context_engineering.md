---
type: Concept
id: 18_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 19/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

1. **KV-Cache优化**：设计以提高缓存命中率，降低延迟和成本
2. **仅追加Context**：避免修改之前的context以保持缓存有效性
3. **外部内存**：使用文件系统和数据库作为扩展context存储
4. **错误保留**：保留失败轨迹用于模型学习和适应
5. **多样性胜过统一性**：避免导致模型漂移的重复模式

## 🔗 模型Context协议 (MCP)

### Context7 MCP服务器
**为LLM和AI代码编辑器提供最新的代码文档**
- 🔗 仓库：[upstash/context7](https://github.com/upstash/context7)
- 🎯 开发工作流的实时代码context
- 🚀 与流行AI编程助手集成

### MCP生态系统
- **[模型Context协议](https://modelcontextprotocol.io/introduction)**：标准化context共享
- **[文件系统服务器](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)**：基于文件的context管理
- **工具集成**：工具间无缝context流动

## 🤝 贡献指南

我们欢迎贡献！请查看我们的[贡献指南](CONTRIBUTING.md)了解详情。

### 如何贡献

1. **添加资源**：提交与context工程相关的论文、工具或文章
2. **改进翻译**：帮助将内容翻译成不同语言
3. **分享见解**：贡献专家意见和最佳实践
4. **报告问题**：帮助我们保持准确性和相关性

### 贡献类别

- 📄 研究论文
- 🛠️ 工具与库
- 📖 文章与教程
- 💡 专家见解
- 🔧 实现示例
- 🌐 翻译

## ⭐ Star历史

[![Star History Chart](https://api.star-history.com/svg?repos=yzfly/awesome-context-engineering&type=Date)](https://star-history.com/#yzfly/awesome-context-engineering&Date)

## 📄 许可证

本项目采用[CC0 1.0](LICENSE)。

## 🙏 致谢

特别感谢所有贡献者和推进context工程领域发展的研究社区。

---

**维护者**：[yzfly](https://github.com/yzfly) | **云中江树（微信公众号: 云中江树）**

*如果您觉得这个仓库有帮助，请考虑给它一个⭐！*

================================================
FILE: docs/claudecode/claude-code-best-practices-zh.md
================================================
标题：Claude Code 最佳实践

原文链接：https://www.anthropic.com/engineering/claude-code-best-practices

Markdown 内容：
[Anthropic 工程团队](https://www.anthropic.com/engineering)

我们最近[发布了 Claude Code](https://www.anthropic.com/news/claude-3-7-sonnet)，这是一个用于智能编程的命令行工具。作为一个研究项目开发，Claude Code 为 Anthropic 的工程师和研究人员提供了一种更原生的方式来将 Claude 集成到他们的编程工作流程中。

Claude Code 故意设计得低层次且不带偏见，提供接近原始模型访问的能力，而不强制特定的工作流程。这种设计理念创造了一个灵活、可定制、可脚本化且安全的强大工具。虽然功能强大，但这种灵活性对于刚接触智能编程工具的工程师来说存在学习曲线——至少在他们形成自己的最佳实践之前是这样。

本文概述了已被证明有效的通用模式，这些模式适用于 Anthropic 内部团队以及在各种代码库、语言和环境中使用 Claude Code 的外部工程师。这个列表中的内容都不是一成不变的，也不是普遍适用的；请将这些建议视为起点。我们鼓励您进行实验，找到最适合您的方法！

_想要更详细的信息？我们在 [claude.ai/code](https://claude.ai/redirect/website.v1.26d5e13f-bc1f-432b-b15a-bdc59c1b87b0/code) 的综合文档涵盖了本文提到的所有功能，并提供了额外的示例、实现细节和高级技术。_

1. 自定义您的设置
-----------------------

Claude Code 是一个智能编程助手，会自动将上下文拉入提示中。这种上下文收集会消耗时间和令牌，但您可以通过环境调优来优化它。

### a. 创建 `CLAUDE.md` 文件

`CLAUDE.md` 是一个特殊文件，Claude 在开始对话时会自动将其拉入上下文。这使其成为记录以下内容的理想位置：

*   常用 bash 命令
*   核心文件和实用函数
*   代码风格指南
*   测试说明
*   仓库礼仪（例如，分支命名、合并 vs 变基等）
*   开发环境设置（例如，pyenv use，哪些编译器有效）
*   项目特有的任何意外行为或警告
*   您希望 Claude 记住的其他信息

`CLAUDE.md` 文件没有必需的格式。我们建议保持简洁和人类可读。例如：

```
# Bash 命令
- npm run build: 构建项目
- npm run typecheck: 运行类型检查器

# 代码风格
- 使用 ES 模块（import/export）语法，而不是 CommonJS（require）
- 尽可能解构导入（例如 import { foo } from 'bar'）

# 工作流程
- 完成一系列代码更改后，请确保进行类型检查
- 为了性能考虑，优先运行单个测试，而不是整个测试套件
```

您可以将 `CLAUDE.md` 文件放在几个位置：
