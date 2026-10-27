---
type: Concept
id: 22_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 23/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

### e. 及早且经常地纠正路线

虽然自动接受模式（shift+tab 切换）让 Claude 自主工作，但通过成为积极的协作者并指导 Claude 的方法，您通常会获得更好的结果。您可以通过在开始时向 Claude 彻底解释任务来获得最佳结果，但您也可以随时纠正 Claude 的路线。

这四个工具有助于路线纠正：

*   **要求 Claude 在编码前制定计划**。明确告诉它在您确认其计划看起来不错之前不要编码。
*   **在任何阶段按 Escape 中断** Claude（思考、工具调用、文件编辑），保留上下文，这样您可以重定向或扩展指令。
*   **双击 Escape 跳回历史**，编辑之前的提示，并探索不同的方向。您可以编辑提示并重复，直到获得您要寻找的结果。
*   **要求 Claude 撤销更改**，通常与选项 #2 结合使用以采取不同的方法。

虽然 Claude Code 偶尔在第一次尝试时完美解决问题，但使用这些纠正工具通常能更快地产生更好的解决方案。

### f. 使用 `/clear` 保持上下文聚焦

在长时间会话期间，Claude 的上下文窗口可能会填满无关的对话、文件内容和命令。这可能会降低性能，有时会分散 Claude 的注意力。在任务之间频繁使用 `/clear` 命令来重置上下文窗口。

### g. 对复杂工作流程使用检查清单和草稿本

对于具有多个步骤或需要详尽解决方案的大型任务——如代码迁移、修复大量 lint 错误或运行复杂构建脚本——通过让 Claude 使用 Markdown 文件（甚至 GitHub 问题！）作为检查清单和工作草稿本来提高性能：

例如，要修复大量 lint 问题，您可以执行以下操作：

1.   **告诉 Claude 运行 lint 命令**并将所有结果错误（带有文件名和行号）写入 Markdown 检查清单
2.   **指示 Claude 逐一解决每个问题**，修复和验证后再勾选并移至下一个

### h. 将数据传递给 Claude

有几种方法为 Claude 提供数据：

*   **直接复制粘贴**到您的提示中（最常见的方法）
*   **管道传输到 Claude Code**（例如，`cat foo.txt | claude`），特别适用于日志、CSV 和大数据
*   **告诉 Claude 通过 bash 命令、MCP 工具或自定义斜杠命令拉取数据**
*   **要求 Claude 读取文件**或获取 URL（也适用于图像）

大多数会话涉及这些方法的组合。例如，您可以管道传入日志文件，然后告诉 Claude 使用工具拉入额外的上下文来调试日志。

5. 使用无头模式自动化您的基础设施
-------------------------------------------

Claude Code 包含用于非交互式上下文（如 CI、预提交钩子、构建脚本和自动化）的[无头模式](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview#automate-ci-and-infra-workflows)。使用 `-p` 标志和提示来启用无头模式，使用 `--output-format stream-json` 进行流式 JSON 输出。

注意无头模式不会在会话之间持续。您必须在每个会话中触发它。

### a. 使用 Claude 进行问题分流

无头模式可以支持由 GitHub 事件触发的自动化，例如在您的仓库中创建新问题时。例如，公共 [Claude Code 仓库](https://github.com/anthropics/claude-code/blob/main/.github/actions/claude-issue-triage-action/action.yml)使用 Claude 检查新问题并分配适当的标签。

### b. 使用 Claude 作为 linter

Claude Code 可以提供传统 linting 工具检测不到的[主观代码审查](https://github.com/anthropics/claude-code/blob/main/.github/actions/claude-code-action/action.yml)，识别诸如拼写错误、过时评论、误导性函数或变量名等问题。

6. 使用多 Claude 工作流程提升水平
--------------------------------------

除了独立使用，一些最强大的应用涉及并行运行多个 Claude 实例：

### a. 让一个 Claude 编写代码；使用另一个 Claude 验证

一个简单但有效的方法是让一个 Claude 编写代码，而另一个审查或测试它。类似于与多个工程师合作，有时拥有单独的上下文是有益的：

1.   使用 Claude 编写代码
2.   运行 `/clear` 或在另一个终端中启动第二个 Claude
3.   让第二个 Claude 审查第一个 Claude 的工作
4.   启动另一个 Claude（或再次 `/clear`）来阅读代码和审查反馈
5.   让这个 Claude 基于反馈编辑代码

您可以对测试做类似的事情：让一个 Claude 编写测试，然后让另一个 Claude 编写代码使测试通过。您甚至可以通过给它们单独的工作草稿本并告诉它们写入哪一个和读取哪一个来让您的 Claude 实例相互通信。

这种分离通常比让单个 Claude 处理所有事情产生更好的结果。

### b. 拥有仓库的多个检出

许多 Anthropic 工程师做的事情是，而不是等待 Claude 完成每个步骤：

1.   **在单独的文件夹中创建 3-4 个 git 检出**
2.   **在单独的终端标签中打开每个文件夹**
3.   **在每个文件夹中启动 Claude**，执行不同的任务
4.   **循环检查**进度并批准/拒绝权限请求

### c. 使用 git worktrees

这种方法对于多个独立任务表现出色，为多个检出提供了更轻量级的替代方案。Git worktrees 允许您将同一仓库的多个分支检出到单独的目录中。每个 worktree 都有自己的工作目录和隔离的文件，同时共享相同的 Git 历史和 reflog。

使用 git worktrees 使您能够在项目的不同部分同时运行多个 Claude 会话，每个都专注于自己的独立任务。例如，您可能有一个 Claude 重构您的身份验证系统，而另一个构建完全不相关的数据可视化组件。由于任务不重叠，每个 Claude 都可以全速工作，而不必等待另一个的更改或处理合并冲突：
