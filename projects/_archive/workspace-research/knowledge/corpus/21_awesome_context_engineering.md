---
type: Concept
id: 21_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 22/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

*   日志记录是如何工作的？
*   如何创建新的 API 端点？
*   `foo.rs` 第 134 行的 `async move { ... }` 是做什么的？
*   `CustomerOnboardingFlowImpl` 处理哪些边缘情况？
*   为什么我们在第 333 行调用 `foo()` 而不是 `bar()`？
*   `baz.py` 第 334 行在 Java 中的等价物是什么？

在 Anthropic，以这种方式使用 Claude Code 已成为我们的核心入职工作流程，显著改善了上手时间并减少了其他工程师的负担。不需要特殊的提示！只需提问，Claude 就会探索代码来找到答案。

![图片 3：使用 Claude 与 git 交互](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2Fa08ea13c2359aac0eceacebf2e15f81e8e8ec8d2-1600x1278.png&w=3840&q=75)

### f. 使用 Claude 与 git 交互

Claude 可以有效处理许多 git 操作。许多 Anthropic 工程师使用 Claude 进行 90%+ 的 _git_ 交互：

*   **搜索 _git_ 历史**来回答诸如"v1.2.3 中包含了哪些更改？"、"谁拥有这个特定功能？"或"为什么这个 API 是这样设计的？"等问题。明确提示 Claude 查看 git 历史来回答这类查询会有帮助。
*   **编写提交消息**。Claude 会自动查看您的更改和最近的历史来编写考虑所有相关上下文的消息
*   **处理复杂的 git 操作**，如还原文件、解决变基冲突以及比较和移植补丁

### g. 使用 Claude 与 GitHub 交互

Claude Code 可以管理许多 GitHub 交互：

*   **创建拉取请求**：Claude 理解简写"pr"，并会基于差异和周围上下文生成适当的提交消息。
*   **为简单的代码审查评论实施一次性解决方案**：只需告诉它修复您 PR 上的评论（可选地，给它更具体的指示），完成后推送回 PR 分支。
*   **修复失败的构建**或 linter 警告
*   **通过要求 Claude 循环遍历开放的 GitHub 问题来分类和分流开放问题**

这消除了记住 `gh` 命令行语法的需要，同时自动化例行任务。

### h. 使用 Claude 处理 Jupyter notebooks

Anthropic 的研究人员和数据科学家使用 Claude Code 来读写 Jupyter notebooks。Claude 可以解释输出，包括图像，提供了一种快速探索和与数据交互的方式。没有必需的提示或工作流程，但我们推荐的工作流程是在 VS Code 中并排打开 Claude Code 和 `.ipynb` 文件。

您也可以要求 Claude 在向同事展示之前清理或对您的 Jupyter notebook 进行美学改进。具体告诉它使 notebook 或其数据可视化"美观"往往有助于提醒它正在为人类观看体验进行优化。

4. 优化您的工作流程
-------------------------

以下建议适用于所有工作流程：

### a. 在指令中要具体

Claude Code 的成功率通过更具体的指令显著提高，特别是在首次尝试时。预先给出明确的方向减少了后续需要纠正路线的需要。

例如：

| 差 | 好 |
| --- | --- |
| 为 foo.py 添加测试 | 为 foo.py 编写新的测试用例，涵盖用户注销时的边缘情况。避免模拟 |
| 为什么 ExecutionFactory 有这么奇怪的 api？ | 查看 ExecutionFactory 的 git 历史并总结其 api 是如何形成的 |
| 添加日历小部件 | 查看主页上现有小部件的实现方式以了解模式，特别是代码和接口是如何分离的。HotDogWidget.php 是一个很好的开始示例。然后，按照模式实现一个新的日历小部件，让用户选择月份并向前/向后翻页选择年份。从头构建，不使用代码库中已使用的库之外的库。 |

Claude 可以推断意图，但它不能读心术。具体性导致与期望更好的对齐。

![图片 4：给 Claude 图像](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F75e1b57a0b696e7aafeca1ed5fa6ba7c601a5953-1360x1126.png&w=3840&q=75)

### b. 给 Claude 图像

Claude 通过几种方法在图像和图表方面表现出色：

*   **粘贴截图**（专业提示：在 macOS 中按 _cmd+ctrl+shift+4_ 截图到剪贴板，按 _ctrl+v_ 粘贴。注意这不是您通常在 mac 上用来粘贴的 cmd+v，并且不能远程工作。）
*   **直接拖放**图像到提示输入
*   **提供图像的文件路径**

这在使用设计模拟作为 UI 开发的参考点以及用于分析和调试的视觉图表时特别有用。如果您没有向上下文添加视觉效果，明确告诉 Claude 结果的视觉吸引力有多重要仍然会有帮助。

![图片 5：提及您希望 Claude 查看或处理的文件](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F7372868757dd17b6f2d3fef98d499d7991d89800-1450x1164.png&w=3840&q=75)

### c. 提及您希望 Claude 查看或处理的文件

使用 tab 补全快速引用仓库中任何地方的文件或文件夹，帮助 Claude 找到或更新正确的资源。

![图片 6：给 Claude URL](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2Fe071de707f209bbaa7f16b593cc7ed0739875dae-1306x1088.png&w=3840&q=75)

### d. 给 Claude URL

在提示中粘贴特定 URL 供 Claude 获取和阅读。为了避免对相同域（例如，docs.foo.com）的权限提示，使用 `/permissions` 将域添加到您的允许列表。
