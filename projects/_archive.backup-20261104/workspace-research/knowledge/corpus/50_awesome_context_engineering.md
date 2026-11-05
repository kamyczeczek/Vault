---
type: Concept
id: 50_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 51/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

DeepMind团队在[Gemini 2.5技术报告](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf)中指出了上下文污染问题，我们[上周对此进行了分析](https://www.dbreunig.com/2025/06/17/an-agentic-case-study-playing-pok%C3%A9mon-with-gemini.html)。在玩宝可梦时，Gemini智能体偶尔会在游戏过程中产生幻觉，从而污染其上下文：

> 这个问题的一个特别严重的形式可能是"上下文污染"——上下文的许多部分（目标、摘要）被关于游戏状态的错误信息"污染"，这往往需要很长时间才能撤销。因此，模型可能会固着于实现不可能或不相关的目标。

如果其上下文的"目标"部分被污染，智能体会制定荒谬的策略，并重复行为来追求无法实现的目标。

### 上下文分散

*上下文分散是指上下文变得太长，导致模型过度关注上下文，忽略了在训练期间学到的知识。*

在智能体工作流程中，随着模型收集更多信息并建立历史记录，上下文会增长——这种累积的上下文可能变得分散注意力而不是有帮助。玩宝可梦的Gemini智能体清楚地展示了这个问题：

> 虽然Gemini 2.5 Pro支持100万+标记上下文，但在智能体中有效利用它是一个新的研究前沿。在这种智能体设置中，观察到当上下文显著超过10万标记时，智能体表现出倾向于重复其庞大历史中的动作，而不是综合新颖的计划。这种现象虽然是轶事性的，但突出了检索用长上下文和多步骤生成推理用长上下文之间的重要区别。

智能体不是使用其训练来制定新策略，而是固着于重复其广泛上下文历史中的过去动作。

对于较小的模型，分散注意力的上限要低得多。[Databricks研究](https://www.databricks.com/blog/long-context-rag-performance-llms)发现，Llama 3.1 405b的模型正确性在大约32k标记左右开始下降，而较小模型的下降更早。

如果模型在其上下文窗口被填满之前就开始异常行为，那么超大上下文窗口的意义何在？简而言之：总结[3](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:summarization)和事实检索。如果你不是在做这两件事，要小心你选择的模型的分散注意力上限。

### 上下文混乱

*上下文混乱是指上下文中的多余内容被模型用来生成低质量响应。*

有那么一段时间，似乎*每个人*都要发布一个[MCP](https://www.dbreunig.com/2025/03/18/mcps-are-apis-for-llms.html)。一个强大的模型连接到你*所有的*服务和*东西*，完成你所有的平凡任务，这个梦想似乎触手可及。只需将所有工具描述扔进提示词然后开始。[Claude的系统提示词](https://www.dbreunig.com/2025/05/07/claude-s-system-prompt-chatbots-are-more-than-just-models.html)为我们指明了道路，因为它主要是工具定义或使用工具的指令。

但即使[整合和竞争不会减缓MCP](https://www.dbreunig.com/2025/06/16/drawbridges-go-up.html)，*上下文混乱*也会。事实证明，工具太多可能是个问题。

[伯克利函数调用排行榜](https://gorilla.cs.berkeley.edu/leaderboard.html)是一个工具使用基准，评估模型有效使用工具响应提示词的能力。现在已经是第三版，排行榜显示*每个*模型在提供超过一个工具时性能都会下降[4](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html#fn:live)。此外，伯克利团队"设计了没有提供的函数相关的场景……我们期望模型的输出是不调用函数。"然而，所有模型偶尔都会调用不相关的工具。

浏览函数调用排行榜，你可以看到随着模型变小，问题会变得更糟：

![Image 2](https://www.dbreunig.com/img/gemma_irrelevance.png)

上下文混乱的一个显著例子可以在[最近的一篇论文](https://arxiv.org/pdf/2411.15399?)中看到，该论文评估了小模型在[GeoEngine基准](https://arxiv.org/abs/2404.15500)上的性能，这是一个包含*46个不同工具*的测试。当团队给量化（压缩）的Llama 3.1 8b一个包含所有46个工具的查询时，它失败了，尽管上下文远在16k上下文窗口之内。但当他们只给模型19个工具时，它成功了。

问题是：如果你把某些东西放在上下文中，*模型就必须关注它*。它可能是不相关的信息或不必要的工具定义，但模型*会*考虑它。大型模型，特别是推理模型，在忽略或丢弃多余上下文方面越来越好，但我们持续看到无价值信息让智能体跌倒。更长的上下文让我们可以塞入更多信息，但这种能力伴随着缺点。

### 上下文冲突

*上下文冲突是指你在上下文中积累的新信息和工具与上下文中的其他信息发生冲突。*

这是*上下文混乱*的一个更有问题的版本：这里的坏上下文不是不相关的，它直接与提示词中的其他信息冲突。

微软和Salesforce团队在[最近的一篇论文](https://arxiv.org/pdf/2505.06120)中出色地记录了这一点。团队从多个基准中获取提示词，并将其信息"分片"到多个提示词中。这样想：有时，你可能会坐下来在ChatGPT或Claude中输入段落，在点击回车之前考虑每个必要的细节。其他时候，你可能从一个简单的提示词开始，然后当聊天机器人的答案不满意时添加进一步的细节。微软/Salesforce团队修改了基准提示词，使其看起来像这些多步骤交流：

![Image 3](https://www.dbreunig.com/img/sharded_prompt.png)

左侧提示词中的所有信息都包含在右侧的几条消息中，这些消息将在多轮聊天中播放。

分片提示词产生了显著更差的结果，平均下降39%。团队测试了一系列模型——OpenAI备受赞誉的o3的分数从98.1下降到64.1。

这是怎么回事？为什么当信息分阶段收集而不是一次性全部收集时，模型的表现会更差？

答案是*上下文混乱*：组装的上下文，包含整个聊天交换的内容，包含模型在拥有所有信息*之前*试图回答挑战的早期尝试。这些错误答案仍然存在于上下文中，并在模型生成最终答案时影响模型。团队写道：
