---
type: Concept
id: 19_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 20/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

*   **仓库的根目录**，或您运行 `claude` 的任何地方（最常见的用法）。将其命名为 `CLAUDE.md` 并检入 git，这样您可以在会话之间和团队中共享它（推荐），或将其命名为 `CLAUDE.local.md` 并将其添加到 `.gitignore`
*   **运行 `claude` 的目录的任何父目录**。这对于单体仓库最有用，您可能从 `root/foo` 运行 `claude`，并在 `root/CLAUDE.md` 和 `root/foo/CLAUDE.md` 中都有 `CLAUDE.md` 文件。这两个都会自动拉入上下文
*   **运行 `claude` 的目录的任何子目录**。这与上面相反，在这种情况下，当您在子目录中处理文件时，Claude 会按需拉入 `CLAUDE.md` 文件
*   **您的主文件夹**（`~/.claude/CLAUDE.md`），这会将其应用到您的所有 _claude_ 会话

当您运行 `/init` 命令时，Claude 会自动为您生成一个 `CLAUDE.md`。

### b. 调优您的 `CLAUDE.md` 文件

您的 `CLAUDE.md` 文件会成为 Claude 提示的一部分，因此应该像任何经常使用的提示一样进行优化。一个常见的错误是添加大量内容而不迭代其有效性。花时间实验并确定什么能从模型中产生最佳的指令遵循效果。

您可以手动向 `CLAUDE.md` 添加内容，或按 `#` 键给 Claude 一个指令，它会自动将其合并到相关的 `CLAUDE.md` 中。许多工程师在编程时频繁使用 `#` 来记录命令、文件和风格指南，然后在提交中包含 `CLAUDE.md` 更改，以便团队成员也能受益。

在 Anthropic，我们偶尔通过[提示改进器](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver)运行 `CLAUDE.md` 文件，并经常调整指令（例如添加"重要"或"您必须"的强调）以提高遵循度。

![图片 1：Claude Code 工具允许列表](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F6961243cc6409e41ba93895faded4f4bc1772366-1600x1231.png&w=3840&q=75)

### c. 管理 Claude 的允许工具列表

默认情况下，Claude Code 会为任何可能修改您系统的操作请求权限：文件写入、许多 bash 命令、MCP 工具等。我们故意采用这种保守的方法来设计 Claude Code，以优先考虑安全性。您可以自定义允许列表以允许您知道安全的其他工具，或允许容易撤销的潜在不安全工具（例如，文件编辑、`git commit`）。

有四种方式管理允许的工具：

*   **在会话期间出现提示时选择"始终允许"**。
*   **启动 Claude Code 后使用 `/permissions` 命令**来添加或删除允许列表中的工具。例如，您可以添加 `Edit` 以始终允许文件编辑，`Bash(git commit:*)` 以允许 git 提交，或 `mcp__puppeteer__puppeteer_navigate` 以允许使用 Puppeteer MCP 服务器进行导航。
*   **手动编辑**您的 `.claude/settings.json` 或 `~/.claude.json`（我们建议将前者检入源代码控制以与团队共享）。
*   **使用 `--allowedTools` CLI 标志**进行会话特定的权限设置。

### d. 如果使用 GitHub，请安装 gh CLI

Claude 知道如何使用 `gh` CLI 与 GitHub 交互，用于创建问题、打开拉取请求、阅读评论等。没有安装 `gh` 的情况下，Claude 仍然可以使用 GitHub API 或 MCP 服务器（如果您已安装）。

2. 为 Claude 提供更多工具
-------------------------

Claude 可以访问您的 shell 环境，您可以在其中为它构建便利脚本和函数集合，就像您为自己做的那样。它还可以通过 MCP 和 REST API 利用更复杂的工具。

### a. 将 Claude 与 bash 工具一起使用

Claude Code 继承您的 bash 环境，使其能够访问您的所有工具。虽然 Claude 了解常见的实用程序，如 unix 工具和 `gh`，但没有说明它不会了解您的自定义 bash 工具：

1.   告诉 Claude 工具名称和使用示例
2.   告诉 Claude 运行 `--help` 查看工具文档
3.   在 `CLAUDE.md` 中记录经常使用的工具

### b. 将 Claude 与 MCP 一起使用

Claude Code 既作为 MCP 服务器又作为客户端运行。作为客户端，它可以连接到任意数量的 MCP 服务器，通过三种方式访问它们的工具：

*   **在项目配置中**（在该目录中运行 Claude Code 时可用）
*   **在全局配置中**（在所有项目中可用）
*   **在检入的 `.mcp.json` 文件中**（对在您的代码库中工作的任何人都可用）。例如，您可以将 Puppeteer 和 Sentry 服务器添加到您的 `.mcp.json`，这样在您的仓库中工作的每个工程师都可以开箱即用地使用这些。

使用 MCP 时，使用 `--mcp-debug` 标志启动 Claude 也很有帮助，以帮助识别配置问题。

### c. 使用自定义斜杠命令

对于重复的工作流程——调试循环、日志分析等——将提示模板存储在 `.claude/commands` 文件夹内的 Markdown 文件中。当您输入 `/` 时，这些会通过斜杠命令菜单变得可用。您可以将这些命令检入 git，使其对团队的其他成员可用。

自定义斜杠命令可以包含特殊关键字 `$ARGUMENTS` 来从命令调用传递参数。

例如，这里是一个您可以用来自动拉取和修复 Github 问题的斜杠命令：

```
请分析并修复 GitHub 问题：$ARGUMENTS。

按照以下步骤：

1. 使用 `gh issue view` 获取问题详情
2. 理解问题中描述的问题
3. 搜索代码库中的相关文件
4. 实施必要的更改来修复问题
5. 编写并运行测试来验证修复
6. 确保代码通过 linting 和类型检查
7. 创建描述性的提交消息
8. 推送并创建 PR

记住对所有 GitHub 相关任务使用 GitHub CLI（`gh`）。
```
