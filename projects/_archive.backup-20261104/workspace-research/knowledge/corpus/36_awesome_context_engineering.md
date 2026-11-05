---
type: Concept
id: 36_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 37/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

这些方法之间的选择取决于任务特征。例如：
- **压缩**维持需要大量来回的任务的对话流；
- **笔记**擅长有明确里程碑的迭代开发；
- **多智能体架构**处理并行探索有回报的复杂研究和分析。

即使模型持续改进，在扩展交互中保持连贯性的挑战仍将是构建更有效智能体的核心。

## 结论

上下文工程代表了我们如何使用LLM构建的根本转变。随着模型变得更强大，挑战不仅仅是制作完美的提示——而是在每一步深思熟虑地策划什么信息进入模型有限的注意力预算。无论您是为长时程任务实施压缩、设计token高效工具，还是让智能体即时探索环境，指导原则都是一样的：**找到最小的高信号token集，最大化期望结果的可能性**。

我们概述的技术将随着模型改进而持续演变。我们已经看到更智能的模型需要更少的规定性工程，允许智能体以更多自主性运行。但即使能力扩展，**将上下文视为珍贵、有限的资源仍将是构建可靠、有效智能体的核心**。

立即在Claude开发者平台开始上下文工程，并通过我们的记忆和上下文管理cookbook访问有用的技巧和最佳实践。

---

**致谢**
由Anthropic应用AI团队撰写：Prithvi Rajasekaran、Ethan Dixon、Carly Ryan和Jeremy Hadfield，团队成员Rafi Ayub、Hannah Moran、Cal Rueb和Connor Jennings有所贡献。特别感谢Molly Vorwerck、Stuart Ritchie和Maggie Vo的支持。

================================================
FILE: docs/dbreunig/how-contexts-fail-and-how-to-fix-them.md
================================================
Title: How Long Contexts Fail

URL Source: https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html

Published Time: 2025-06-22T16:19:00-07:00

Markdown Content:
![Image 1](https://www.dbreunig.com/img/overload.jpg)

### Managing Your Context is the Key to Successful Agents

As frontier model context windows continue to grow[1](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:longcontext), with many supporting up to 1 million tokens, I see many excited discussions about how long context windows will unlock the agents of our dreams. After all, with a large enough window, you can simply throw _everything_ into a prompt you might need – tools, documents, instructions, and more –and let the model take care of the rest.

Long contexts kneecapped RAG enthusiasm (no need to find the best doc when you can fit it all in the prompt!), enabled MCP hype (connect to every tool and models can do any job!), and fueled enthusiasm for agents[2](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:googledocs).

But in reality, longer contexts do not generate better responses. Overloading your context can cause your agents and applications to fail in suprising ways. Contexts can become poisoned, distracting, confusing, or conflicting. This is especially problematic for agents, which rely on context to gather information, synthesize findings, and coordinate actions.

Let’s run through the ways contexts can get out of hand, then review methods to mitigate or entirely avoid context fails.

Context Fails
-------------
