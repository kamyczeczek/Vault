---
type: Concept
id: 49_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 50/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

总结你的上下文很容易做到，但对于任何给定的智能体来说很难完善。知道应该保留什么信息，并将其详细说明给LLM驱动的压缩步骤，对智能体构建者来说至关重要。值得将此功能分解为自己的LLM驱动阶段或应用程序，这允许你收集评估数据，可以直接告知和优化此任务。

![Image 7: A banker's box](https://www.dbreunig.com/img/context_offload.png)

### 上下文卸载

*上下文卸载是将信息存储在LLM上下文之外的行为，通常通过存储和管理数据的工具。*

这可能是我最喜欢的策略，如果只是因为它是如此*简单*，你不相信它会工作。

同样，[Anthropic对该技术有很好的描述](https://www.anthropic.com/engineering/claude-think-tool)，详细介绍了他们的"think"工具，它基本上是一个草稿板：

> 使用"think"工具，我们让Claude能够包含一个额外的思考步骤——完整的专用空间——作为获得最终答案的一部分……这在执行长链工具调用或与用户进行长时间多步骤对话时特别有用。

我真的很欣赏Anthropic发布的研究和其他文章，但我不喜欢这个工具的名字。如果这个工具叫`scratchpad`，你会*立即*知道它的功能。这是模型写下不会污染其上下文、可供以后参考的笔记的地方。"think"这个名字与"[扩展思维](https://www.anthropic.com/news/visible-extended-thinking)"冲突，并且不必要地将模型拟人化……但我离题了。

有一个记录笔记和进度的空间*是有效的*。Anthropic显示将"think"工具与特定于领域的提示词配对（无论如何你都会在智能体中这样做）会产生显著收益，在专业智能体基准上提高多达54%。

Anthropic确定了三种上下文卸载模式有用的场景：

> 1. 工具输出分析。当Claude需要在行动前仔细处理先前工具调用的输出，并且可能需要回溯其方法时；
> 2. 策略繁重的环境。当Claude需要遵循详细指导原则并验证合规性时；以及
> 3. 顺序决策制定。当每个行动都建立在先前行动基础上且错误代价高昂时（通常出现在多步骤领域中）。

* * *

上下文管理通常是构建智能体最困难的部分。如Karpathy所说，编程LLM"[恰到好处地打包上下文窗口](https://x.com/karpathy/status/1937902205765607626)"，智能地部署工具、信息和常规上下文维护是智能体设计者的*工作*。

上述所有策略的关键洞察是*上下文不是免费的*。上下文中的每个标记都会影响模型的行为，无论好坏。现代LLM的大规模上下文窗口是一种强大的能力，但它们不是信息管理马虎的借口。

当你构建下一个智能体或优化现有智能体时，问问自己：这个上下文中的一切都在发挥其作用吗？如果没有，你现在有六种方法来修复它。

* * *

1. 见鬼，这整个策略列表有力地支持[你应该编程你的上下文](https://www.dbreunig.com/2025/06/10/let-the-model-write-the-prompt.html)。[↩](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#fnref:structure)

================================================
FILE: docs/dbreunig/长上下文的失效原理及解决方案.md
================================================
标题：长上下文如何失效

来源地址：https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html

发布时间：2025-06-22T16:19:00-07:00

![Image 1](https://www.dbreunig.com/img/overload.jpg)

### 管理上下文是成功构建智能体的关键

随着前沿模型上下文窗口的不断扩大[1](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:longcontext)，许多模型现在支持多达100万个标记，我看到了许多令人兴奋的讨论，认为长上下文窗口将解锁我们梦想中的智能体。毕竟，有了足够大的窗口，你可以简单地将可能需要的一切——工具、文档、指令等等——都扔进提示词中，让模型来处理剩下的事情。

长上下文削弱了RAG的热情（当你可以将所有文档都放入提示词时，就不需要寻找最佳文档了！），推动了MCP的炒作（连接到每个工具，模型就能做任何工作！），并激发了对智能体的热情[2](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:googledocs)。

但实际上，更长的上下文并不会产生更好的响应。过载你的上下文可能会导致智能体和应用程序以令人意外的方式失效。上下文可能会被污染、分散注意力、造成混乱或产生冲突。这对于依赖上下文来收集信息、综合发现和协调行动的智能体来说尤其成问题。

让我们回顾一下上下文可能失控的方式，然后介绍缓解或完全避免上下文失效的方法。

上下文失效
---------

* [上下文污染：当幻觉进入上下文时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-poisoning)
* [上下文分散：当上下文压倒训练时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-distraction)
* [上下文混乱：当多余的上下文影响响应时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-confusion)
* [上下文冲突：当上下文的某些部分产生分歧时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-clash)

* * *

### 上下文污染

*上下文污染是指幻觉或其他错误进入上下文，并被反复引用。*
