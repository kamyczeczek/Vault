---
type: Concept
id: 23_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 24/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

1.   **创建 worktrees**：`git worktree add ../project-feature-a feature-a`
2.   **在每个 worktree 中启动 Claude**：`cd ../project-feature-a && claude`
3.   **根据需要创建额外的 worktrees**（在新的终端标签中重复步骤 1-2）

一些提示：

*   使用一致的命名约定
*   为每个 worktree 维护一个终端标签
*   如果您在 Mac 上使用 iTerm2，[设置通知](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview#notification-setup)以便在 Claude 需要注意时收到通知
*   为不同的 worktrees 使用单独的 IDE 窗口
*   完成后清理：`git worktree remove ../project-feature-a`

### d. 使用带有自定义工具的无头模式

`claude -p`（无头模式）将 Claude Code 程序化地集成到更大的工作流程中，同时利用其内置工具和系统提示。使用无头模式有两种主要模式：

1. **扇出**处理大型迁移或分析（例如，分析数百个日志中的情感或分析数千个 CSV）：

1.   让 Claude 编写脚本生成任务列表。例如，生成需要从框架 A 迁移到框架 B 的 2k 文件列表。
2.   循环遍历任务，为每个任务程序化地调用 Claude，给它一个任务和一组可以使用的工具。例如：`claude -p "将 foo.py 从 React 迁移到 Vue。完成后，如果成功您必须返回字符串 OK，如果任务失败则返回 FAIL。" --allowedTools Edit Bash(git commit:*)`
3.   多次运行脚本并优化您的提示以获得所需的结果。

2. **管道化**将 Claude 集成到现有的数据/处理管道中：

1.   调用 `claude -p "<您的提示>" --json | your_command`，其中 `your_command` 是处理管道的下一步
2.   就是这样！JSON 输出（可选）可以帮助为更容易的自动化处理提供结构。

对于这两种用例，使用 `--verbose` 标志调试 Claude 调用可能会有帮助。我们通常建议在生产中关闭详细模式以获得更清洁的输出。

您使用 Claude Code 的技巧和最佳实践是什么？标记 @AnthropicAI，这样我们就能看到您正在构建什么！

致谢
----------------

作者：Boris Cherny。这项工作借鉴了更广泛的 Claude Code 用户社区的最佳实践，他们的创造性方法和工作流程继续激励着我们。特别感谢 Daisy Hollman、Ashwin Bhat、Cat Wu、Sid Bidasaria、Cal Rueb、Nodir Turakulov、Barry Zhang、Drew Hodun 和许多其他 Anthropic 工程师，他们宝贵的见解和使用 Claude Code 的实践经验帮助塑造了这些建议。

================================================
FILE: docs/claudecode/claude-code-best-practices.md
================================================
Title: Claude Code Best Practices

URL Source: https://www.anthropic.com/engineering/claude-code-best-practices

Markdown Content:
[Engineering at Anthropic](https://www.anthropic.com/engineering)

We recently [released Claude Code](https://www.anthropic.com/news/claude-3-7-sonnet), a command line tool for agentic coding. Developed as a research project, Claude Code gives Anthropic engineers and researchers a more native way to integrate Claude into their coding workflows.

Claude Code is intentionally low-level and unopinionated, providing close to raw model access without forcing specific workflows. This design philosophy creates a flexible, customizable, scriptable, and safe power tool. While powerful, this flexibility presents a learning curve for engineers new to agentic coding tools—at least until they develop their own best practices.

This post outlines general patterns that have proven effective, both for Anthropic's internal teams and for external engineers using Claude Code across various codebases, languages, and environments. Nothing in this list is set in stone nor universally applicable; consider these suggestions as starting points. We encourage you to experiment and find what works best for you!
