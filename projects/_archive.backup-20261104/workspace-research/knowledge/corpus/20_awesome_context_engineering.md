---
type: Concept
id: 20_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 21/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

将上述内容放入 `.claude/commands/fix-github-issue.md` 使其在 Claude Code 中作为 `/project:fix-github-issue` 命令可用。然后您可以例如使用 `/project:fix-github-issue 1234` 让 Claude 修复问题 #1234。类似地，您可以将自己的个人命令添加到 `~/.claude/commands` 文件夹，用于您希望在所有会话中可用的命令。

3. 尝试常见工作流程
-----------------------

Claude Code 不强制特定的工作流程，给您使用它的灵活性。在这种灵活性提供的空间内，我们用户社区中出现了几种有效使用 Claude Code 的成功模式：

### a. 探索、计划、编码、提交

这种多功能工作流程适合许多问题：

1.   **要求 Claude 读取相关文件、图像或 URL**，提供一般指针（"读取处理日志记录的文件"）或特定文件名（"读取 logging.py"），但明确告诉它暂时不要编写任何代码。
    1.   这是工作流程中您应该考虑大量使用子代理的部分，特别是对于复杂问题。告诉 Claude 使用子代理来验证细节或调查它可能有的特定问题，特别是在对话或任务的早期，往往会保留上下文可用性，而在效率损失方面没有太多缺点。

2.   **要求 Claude 制定如何处理特定问题的计划**。我们建议使用"思考"这个词来触发扩展思考模式，这给 Claude 额外的计算时间来更彻底地评估替代方案。这些特定短语直接映射到系统中增加的思考预算级别："think" < "think hard" < "think harder" < "ultrathink"。每个级别为 Claude 分配逐渐增加的思考预算。
    1.   如果这一步的结果看起来合理，您可以让 Claude 创建一个文档或 GitHub 问题来记录其计划，这样如果实施（步骤 3）不是您想要的，您可以重置到这个点。

3.   **要求 Claude 在代码中实施其解决方案**。这也是要求它在实施解决方案的各个部分时明确验证其解决方案合理性的好地方。
4.   **要求 Claude 提交结果并创建拉取请求**。如果相关，这也是让 Claude 更新任何 README 或变更日志以解释它刚才所做的事情的好时机。

步骤 #1-#2 至关重要——没有它们，Claude 倾向于直接跳到编码解决方案。虽然有时这就是您想要的，但要求 Claude 首先研究和计划显著提高了需要前期深入思考的问题的性能。

### b. 编写测试，提交；编码，迭代，提交

这是 Anthropic 最喜欢的工作流程，用于可以通过单元、集成或端到端测试轻松验证的更改。测试驱动开发（TDD）在智能编程中变得更加强大：

1.   **要求 Claude 基于预期的输入/输出对编写测试**。明确说明您正在进行测试驱动开发，这样它就会避免创建模拟实现，即使对于代码库中尚不存在的功能也是如此。
2.   **告诉 Claude 运行测试并确认它们失败**。在这个阶段明确告诉它不要编写任何实现代码通常很有帮助。
3.   **当您对测试满意时，要求 Claude 提交测试**。
4.   **要求 Claude 编写通过测试的代码**，指示它不要修改测试。告诉 Claude 继续直到所有测试通过。Claude 通常需要几次迭代来编写代码、运行测试、调整代码并再次运行测试。
    1.   在这个阶段，要求它用独立的子代理验证实现没有过度拟合测试可能会有帮助

5.   **一旦您对更改满意，要求 Claude 提交代码**。

Claude 在有明确目标进行迭代时表现最佳——视觉模拟、测试用例或其他类型的输出。通过提供像测试这样的预期输出，Claude 可以进行更改、评估结果并逐步改进直到成功。

### c. 编写代码，截图结果，迭代

类似于测试工作流程，您可以为 Claude 提供视觉目标：

1.   **为 Claude 提供截取浏览器截图的方法**（例如，使用 [Puppeteer MCP 服务器](https://github.com/modelcontextprotocol/servers/tree/c19925b8f0f2815ad72b08d2368f0007c86eb8e6/src/puppeteer)、[iOS 模拟器 MCP 服务器](https://github.com/joshuayoes/ios-simulator-mcp)，或手动复制/粘贴截图到 Claude）。
2.   **通过复制/粘贴或拖放图像，或给 Claude 图像文件路径来为 Claude 提供视觉模拟**。
3.   **要求 Claude 在代码中实现设计**，截取结果的截图，并迭代直到其结果与模拟匹配。
4.   **当您满意时要求 Claude 提交**。

像人类一样，Claude 的输出往往通过迭代显著改善。虽然第一个版本可能不错，但经过 2-3 次迭代后通常会看起来好得多。为 Claude 提供查看其输出的工具以获得最佳结果。

![图片 2：安全 YOLO 模式](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F6ea59a36fe82c2b300bceaf3b880a4b4852c552d-1600x1143.png&w=3840&q=75)

### d. 安全 YOLO 模式

您可以使用 `claude --dangerously-skip-permissions` 绕过所有权限检查，让 Claude 不间断地工作直到完成，而不是监督 Claude。这适用于修复 lint 错误或生成样板代码等工作流程。

让 Claude 运行任意命令是有风险的，可能导致数据丢失、系统损坏，甚至数据泄露（例如，通过提示注入攻击）。为了最小化这些风险，在没有互联网访问的容器中使用 `--dangerously-skip-permissions`。您可以按照这个[参考实现](https://github.com/anthropics/claude-code/tree/main/.devcontainer)使用 Docker Dev Containers。

### e. 代码库问答

在接触新代码库时，使用 Claude Code 进行学习和探索。您可以向 Claude 询问在结对编程时会向项目中其他工程师询问的相同类型问题。Claude 可以智能地搜索代码库来回答一般问题，如：
