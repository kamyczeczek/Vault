---
type: Concept
id: 48_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 49/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

*上下文隔离是在各自专用的线程中隔离上下文的行为，每个线程由一个或多个LLM单独使用。*

当我们的上下文不太长且不包含不相关内容时，我们会看到更好的结果。实现这一点的一种方法是将我们的任务分解为较小的、隔离的工作——每个都有自己的上下文。

有[许多](https://arxiv.org/abs/2402.14207)[这种策略的例子](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/)，但这种策略的一个易于理解的描述是Anthropic的[详细介绍其多智能体研究系统的博客文章](https://www.anthropic.com/engineering/built-multi-agent-research-system)。他们写道：

> 搜索的本质是压缩：从庞大的语料库中提炼见解。子智能体通过在各自的上下文窗口中并行操作来促进压缩，在将最重要的标记凝聚给主要研究智能体之前，同时探索问题的不同方面。每个子智能体还提供关注点分离——不同的工具、提示词和探索轨迹——这减少了路径依赖性并支持彻底、独立的调查。

研究适合这种设计模式。当给出一个问题时，可以识别几个子问题或探索领域，并使用多个智能体分别提示。这不仅加快了信息收集和提炼（如果有可用的计算资源），而且防止每个上下文积累太多信息或与给定提示词不相关的信息，从而提供更高质量的结果：

> 我们的内部评估显示，多智能体研究系统在涉及同时追求多个独立方向的广度优先查询方面特别出色。我们发现，以Claude Opus 4为主智能体、Claude Sonnet 4子智能体的多智能体系统在我们的内部研究评估中比单智能体Claude Opus 4系统表现好90.2%。例如，当被要求识别信息技术标普500公司的所有董事会成员时，多智能体系统通过将此分解为子智能体的任务找到了正确答案，而单智能体系统在缓慢的顺序搜索中未能找到答案。

这种方法也有助于工具配置，因为智能体设计者可以创建几个智能体原型，每个都有自己专用的配置和如何使用每个工具的指令。

那么，智能体构建者的挑战是找到将隔离任务分离到单独线程的机会。需要在多个智能体之间共享上下文的问题不太适合这种策略。

如果你的智能体领域在任何程度上都适合并行化，一定要[阅读整个Anthropic的文章](https://www.anthropic.com/engineering/built-multi-agent-research-system)。它非常出色。

![Image 5: Pruning shears](https://www.dbreunig.com/img/context_pruning.png)

### 上下文修剪

*上下文修剪是从上下文中移除不相关或不需要信息的行为。*

智能体在启动工具和组装文档时积累上下文。有时，值得暂停评估已组装的内容并移除垃圾。这可能是你分配给主LLM的任务，或者你可以设计一个单独的LLM驱动工具来审查和编辑上下文。或者你可以选择更针对修剪任务的东西。

上下文修剪有（相对）悠久的历史，因为在ChatGPT之前的自然语言处理（NLP）领域，上下文长度是一个更成问题的瓶颈。基于这一历史的当前修剪方法是[Provence](https://arxiv.org/abs/2501.16214)，"一个用于问答的高效且鲁棒的上下文修剪器"。

Provence快速、准确、易于使用且相对较小——只有1.75 GB。你可以用几行代码调用它，像这样：

```python
from transformers import AutoModel

provence = AutoModel.from_pretrained("naver/provence-reranker-debertav3-v1", trust_remote_code=True)

# 读取阿拉米达，加州维基百科条目的markdown版本
with open('alameda_wiki.md', 'r', encoding='utf-8') as f:
    alameda_wiki = f.read()

# 根据问题修剪文章
question = '离开阿拉米达我有什么选择？'
provence_output = provence.process(question, alameda_wiki)
```

Provence编辑了文章，删减了95%的内容，只留下[这个相关的子集](https://gist.github.com/dbreunig/b3bdd9eb34bc264574954b2b954ebe83)。它做得很好。

可以使用Provence或类似功能来删减文档或整个上下文。此外，这种模式有力地支持维护上下文的*结构化*[1](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#fn:structure)版本，使用字典或其他形式，在每次LLM调用之前从中组装编译的字符串。这种结构在修剪时会派上用场，允许你确保保留主要指令和目标，而文档或历史部分可以被修剪或总结。

![Image 6: A duck press](https://www.dbreunig.com/img/context_summarization.png)

### 上下文总结

*上下文总结是将累积的上下文压缩成精简摘要的行为。*

上下文总结最初出现是为了处理较小的上下文窗口。当你的聊天会话接近超出最大上下文长度时，会生成摘要并开始新的线程。聊天机器人用户在ChatGPT或Claude中手动执行此操作，要求机器人生成简短的回顾，然后将其粘贴到新会话中。

然而，随着上下文窗口的增加，智能体构建者发现总结除了保持在总上下文限制内之外还有好处。随着上下文的增长，它变得分散注意力，导致模型较少依赖在训练期间学到的知识。我们称之为[上下文分散](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#context-distraction)。玩宝可梦的Gemini智能体背后的团队发现，超过100,000个标记的任何内容都会触发这种行为：

> 虽然Gemini 2.5 Pro支持100万+标记上下文，但在智能体中有效利用它是一个新的研究前沿。在这种智能体设置中，观察到当上下文显著超过10万标记时，智能体表现出倾向于重复其庞大历史中的动作，而不是综合新颖的计划。这种现象虽然是轶事性的，但突出了检索用长上下文和多步骤生成推理用长上下文之间的重要区别。
