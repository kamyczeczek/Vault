---
type: Concept
id: 63_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 64/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

考虑到这一点，[Cognition](https://cognition.ai/blog/dont-build-multi-agents?ref=blog.langchain.com)指出了context工程的重要性：

> _"Context工程"...实际上是构建AI智能体的工程师的#1工作。_

[Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system?ref=blog.langchain.com)也明确表达了这一点：

> _智能体经常进行跨越数百轮的对话，需要仔细的context管理策略。_

那么，人们今天是如何应对这一挑战的呢？我们将智能体context工程的常见策略分为四个类别——**写入、选择、压缩和隔离**——并通过回顾一些流行的智能体产品和论文给出每种策略的示例。然后我们解释LangGraph是如何设计来支持它们的！

![Image 5](https://blog.langchain.com/content/images/2025/07/image-4.png)

Context工程的一般类别

### 写入Context

_写入context意味着将其保存在context窗口之外，以帮助智能体执行任务。_

**Scratchpad**

当人类解决任务时，我们会做笔记并记住未来相关任务的事情。智能体也在获得这些能力！通过"[scratchpad](https://www.anthropic.com/engineering/claude-think-tool?ref=blog.langchain.com)"做笔记是在智能体执行任务时持久化信息的一种方法。其想法是将信息保存在context窗口之外，以便智能体可以使用。[Anthropic的多智能体研究员](https://www.anthropic.com/engineering/built-multi-agent-research-system?ref=blog.langchain.com)说明了一个清晰的例子：

> _LeadResearcher首先思考方法并将其计划保存到Memory中以持久化context，因为如果context窗口超过200,000个token，它将被截断，保留计划很重要。_

Scratchpad可以通过几种不同的方式实现。它们可以是一个[工具调用](https://www.anthropic.com/engineering/claude-think-tool?ref=blog.langchain.com)，简单地[写入文件](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem?ref=blog.langchain.com)。它们也可以是运行时[状态对象](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state)中的一个字段，在会话期间持久存在。无论哪种情况，scratchpad都让智能体保存有用的信息来帮助它们完成任务。

**记忆**

Scratchpad帮助智能体在给定会话（或[线程](https://langchain-ai.github.io/langgraph/concepts/persistence/?ref=blog.langchain.com#threads)）内解决任务，但有时智能体受益于跨_多个_会话记住事情！[Reflexion](https://arxiv.org/abs/2303.11366?ref=blog.langchain.com)引入了在每个智能体轮次后进行反思并重新使用这些自生成记忆的想法。[生成式智能体](https://ar5iv.labs.arxiv.org/html/2304.03442?ref=blog.langchain.com)从过去智能体反馈的集合中定期合成记忆。

![Image 6](https://blog.langchain.com/content/images/2025/07/image-5.png)

可以使用LLM来更新或创建记忆

这些概念进入了流行产品，如[ChatGPT](https://help.openai.com/en/articles/8590148-memory-faq?ref=blog.langchain.com)、[Cursor](https://forum.cursor.com/t/0-51-memories-feature/98509?ref=blog.langchain.com)和[Windsurf](https://docs.windsurf.com/windsurf/cascade/memories?ref=blog.langchain.com)，它们都有基于用户-智能体交互自动生成可跨会话持久存在的长期记忆的机制。

### 选择Context

_选择context意味着将其拉入context窗口以帮助智能体执行任务。_

**Scratchpad**

从scratchpad选择context的机制取决于scratchpad的实现方式。如果它是一个[工具](https://www.anthropic.com/engineering/claude-think-tool?ref=blog.langchain.com)，那么智能体可以通过进行工具调用来简单地读取它。如果它是智能体运行时状态的一部分，那么开发者可以选择在每一步向智能体暴露状态的哪些部分。这为在后续轮次中向LLM暴露scratchpad context提供了细粒度的控制级别。

**记忆**
