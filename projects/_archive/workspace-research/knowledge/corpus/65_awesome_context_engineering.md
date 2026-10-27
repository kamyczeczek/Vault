---
type: Concept
id: 65_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 66/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

智能体交互可以跨越[数百轮](https://www.anthropic.com/engineering/built-multi-agent-research-system?ref=blog.langchain.com)并使用token密集的工具调用。摘要是管理这些挑战的一种常见方法。如果你使用过Claude Code，你已经看到了这一点的实际应用。Claude Code在你超过context窗口的95%后运行"[自动压缩](https://docs.anthropic.com/en/docs/claude-code/costs?ref=blog.langchain.com)"，它将摘要用户-智能体交互的完整轨迹。这种跨[智能体轨迹](https://langchain-ai.github.io/langgraph/concepts/memory/?ref=blog.langchain.com#manage-short-term-memory)的压缩类型可以使用各种策略，如[递归](https://arxiv.org/pdf/2308.15022?ref=blog.langchain.com#:~:text=the%20retrieved%20utterances%20capture%20the,based%203)或[分层](https://alignment.anthropic.com/2025/summarization-for-monitoring/?ref=blog.langchain.com#:~:text=We%20addressed%20these%20issues%20by,of%20our%20computer%20use%20capability)摘要。

![Image 8](https://blog.langchain.com/content/images/2025/07/image-7.png)

可以应用摘要的几个地方

在智能体设计的特定点[添加摘要](https://github.com/langchain-ai/open_deep_research/blob/e5a5160a398a3699857d00d8569cb7fd0ac48a4f/src/open_deep_research/utils.py?ref=blog.langchain.com#L1407)也可能很有用。例如，它可以用于后处理某些工具调用（例如，token密集的搜索工具）。作为第二个例子，[Cognition](https://cognition.ai/blog/dont-build-multi-agents?ref=blog.langchain.com#a-theory-of-building-long-running-agents)提到在智能体-智能体边界处进行摘要，以减少知识交接期间的token。如果需要捕获特定事件或决策，摘要可能是一个挑战。[Cognition](https://cognition.ai/blog/dont-build-multi-agents?ref=blog.langchain.com#a-theory-of-building-long-running-agents)为此使用了一个fine-tuned模型，这强调了这一步可能需要多少工作。

**Context修剪**

而摘要通常使用LLM来提取context的最相关部分，修剪通常可以过滤或，正如Drew Breunig指出的，"[修剪](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html?ref=blog.langchain.com)"context。这可以使用硬编码启发式，如从列表中删除[较旧的消息](https://python.langchain.com/docs/how_to/trim_messages/?ref=blog.langchain.com)。Drew还提到了[Provence](https://arxiv.org/abs/2501.16214?ref=blog.langchain.com)，一个用于问答的训练过的context修剪器。

### 隔离Context

_隔离context涉及将其分割以帮助智能体执行任务。_

**多智能体**

隔离context最流行的方法之一是将其分割到子智能体中。OpenAI [Swarm](https://github.com/openai/swarm?ref=blog.langchain.com)库的动机是[关注点分离](https://openai.github.io/openai-agents-python/ref/agent/?ref=blog.langchain.com)，其中智能体团队可以处理特定的子任务。每个智能体都有特定的工具集、指令和自己的context窗口。

![Image 9](https://blog.langchain.com/content/images/2025/07/image-8.png)

在多个智能体之间分割context

Anthropic的[多智能体研究员](https://www.anthropic.com/engineering/built-multi-agent-research-system?ref=blog.langchain.com)为此提出了理由：具有隔离context的多个智能体优于单智能体，主要是因为每个子智能体context窗口可以分配给更窄的子任务。正如博客所说：

> _[子智能体]并行操作，拥有自己的context窗口，同时探索问题的不同方面。_

当然，多智能体的挑战包括token使用（例如，据Anthropic报告，比聊天多达[15倍的token](https://www.anthropic.com/engineering/built-multi-agent-research-system?ref=blog.langchain.com)），需要仔细的[prompt工程](https://www.anthropic.com/engineering/built-multi-agent-research-system?ref=blog.langchain.com)来规划子智能体工作，以及子智能体的协调。

**使用环境进行Context隔离**
