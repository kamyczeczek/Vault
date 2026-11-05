---
type: Concept
id: 47_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 48/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

![Image 1](https://www.dbreunig.com/img/overload.jpg)

### 缓解和避免上下文失效

作为我们之前文章"[长上下文如何失效](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)"的后续，让我们看看如何缓解或完全避免这些失效。

在开始之前，让我们简要回顾一下长上下文可能失效的几种方式：

* **上下文污染：** 当幻觉或其他错误进入上下文，并被反复引用时。
* **上下文分散：** 当上下文变得太长，导致模型过度关注上下文，忽略了在训练期间学到的知识时。
* **上下文混乱：** 当上下文中的多余信息被模型用来生成低质量响应时。
* **上下文冲突：** 当你在上下文中积累的新信息和工具与上下文中的其他信息发生冲突时。

这一切都与信息管理有关。上下文中的一切都会影响响应。我们又回到了古老的编程格言："[垃圾进，垃圾出](https://en.wikipedia.org/wiki/Garbage_in,_garbage_out)"。幸运的是，有很多选项来处理上述问题。

上下文管理策略
--------------

* [**RAG：** 有选择地添加相关信息以帮助LLM生成更好的响应](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#rag)
* [**工具配置：** 仅选择相关的工具定义添加到你的上下文中](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#tool-loadout)
* [**上下文隔离：** 在各自专用的线程中隔离上下文](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-quarantine)
* [**上下文修剪：** 从上下文中移除不相关或不需要的信息](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-pruning)
* [**上下文总结：** 将累积的上下文压缩成精简摘要](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-summarization)
* [**上下文卸载：** 将信息存储在LLM上下文之外，通常通过存储和管理数据的工具](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-offloading)

* * *

![Image 2: A stack of papers.](https://www.dbreunig.com/img/rag.png)

### RAG

*检索增强生成（RAG）是有选择地添加相关信息以帮助LLM生成更好响应的行为。*

关于RAG已经写了太多，我们今天不会深入讨论，只是说：它非常活跃。

每当一个模型提高上下文窗口的标准时，就会诞生一个新的"RAG已死"辩论。最后一个重大事件是Llama 4 Scout推出了*1000万标记窗口*。在这个规模下，真的很诱人去想，"算了，全部扔进去"，然后收工。

但是，正如我们上次所说：如果你把上下文当作杂物抽屉，杂物就会[影响你的响应](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-confusion)。如果你想了解更多，这里有一个[看起来很棒的新课程](https://maven.com/p/569540/i-don-t-use-rag-i-just-retrieve-documents)。

![Image 3: A selection of guns from the videogame Destiny](https://www.dbreunig.com/img/tool_loadout.png)

### 工具配置

*工具配置是仅选择相关工具定义添加到你的上下文中的行为。*

"配置"这个术语是游戏术语，指你在关卡、匹配或回合之前选择的能力、武器和装备的特定组合。通常，你的配置是根据上下文量身定制的——角色、关卡、团队其他成员的构成，以及你自己的技能组合。

在这里，我们借用这个术语来描述为给定任务选择最相关的工具。

也许选择工具最简单的方法是将RAG应用于你的工具描述。这正是Tiantian Gan和Qiyao Sun所做的，他们在论文"[RAG MCP](https://arxiv.org/abs/2505.03275)"中详细介绍了这一点。通过将工具描述存储在向量数据库中，他们能够根据输入提示词选择最相关的工具。

在提示DeepSeek-v3时，团队发现当你有超过30个工具时，选择正确的工具变得至关重要。超过30个，工具的描述开始重叠，造成混乱。超过*100个工具*，模型几乎肯定会在他们的测试中失败。使用RAG技术选择少于30个工具产生了显著更短的提示词，并导致工具选择准确性提高了多达3倍。

对于较小的模型，问题在我们达到30个工具之前就开始了。我们在上一篇文章中提到的一篇论文"[少即是多](https://arxiv.org/abs/2411.15399)"表明，当给出46个工具时，Llama 3.1 8b在基准测试中失败，但只给出19个工具时成功。问题是上下文混乱，*不是*上下文窗口限制。

为了解决这个问题，"少即是多"背后的团队开发了一种使用LLM驱动的工具推荐器动态选择工具的方法。LLM被提示推理"它'认为'需要回答用户查询的工具数量和类型"。然后对此输出进行语义搜索（再次是工具RAG）以确定最终配置。他们用[伯克利函数调用排行榜](https://gorilla.cs.berkeley.edu/leaderboard.html)测试了这种方法，发现Llama 3.1 8b的性能提高了44%。

"少即是多"论文指出了较小上下文的另外两个好处：降低功耗和提高速度，这些是在边缘操作（意思是在你的手机或PC上运行LLM，而不是在专用服务器上）时的关键指标。即使他们的动态工具选择方法*未能*改善模型的结果，功耗节省和速度提升也是值得的，分别产生了18%和77%的节省。

幸运的是，大多数智能体的表面积较小，只需要几个手工策划的工具。但如果功能的广度或集成的数量需要扩展，总是要考虑你的配置。

![Image 4: A belljar](https://www.dbreunig.com/img/context_quarantine.png)

### 上下文隔离
