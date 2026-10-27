---
type: Concept
id: 62_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 63/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

正如Andrej Karpathy所说，LLM就像一种[新型操作系统](https://www.youtube.com/watch?si=-aKY-x57ILAmWTdw&t=620&v=LCEmiRjPEtQ&feature=youtu.be&ref=blog.langchain.com)。LLM就像CPU，其[context窗口](https://docs.anthropic.com/en/docs/build-with-claude/context-windows?ref=blog.langchain.com)就像RAM，作为模型的工作内存。就像RAM一样，LLM context窗口的[容量](https://lilianweng.github.io/posts/2023-06-23-agent/?ref=blog.langchain.com)有限，无法处理各种context来源。正如操作系统策划适合CPU RAM的内容一样，我们可以考虑"context工程"发挥类似的作用。[Karpathy很好地总结了这一点](https://x.com/karpathy/status/1937902205765607626?ref=blog.langchain.com)：

> _[Context工程是]"...用恰当的信息为下一步填充context窗口的精妙艺术和科学。"_

![Image 2](https://blog.langchain.com/content/images/2025/07/image-1.png)

LLM应用中常用的context类型

在构建LLM应用时，我们需要管理哪些类型的context？Context工程作为一个[总括概念](https://x.com/dexhorthy/status/1933283008863482067?ref=blog.langchain.com)，适用于几种不同的context类型：

* **指令** – prompt、记忆、few-shot示例、工具描述等
* **知识** – 事实、记忆等
* **工具** – 工具调用的反馈

### 智能体的Context工程

今年，随着LLM在[推理](https://platform.openai.com/docs/guides/reasoning?api-mode=responses&ref=blog.langchain.com)和[工具调用](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)方面变得更好，对[智能体](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)的兴趣大幅增长。[智能体](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)交替进行[LLM调用和工具调用](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)，通常用于[长期运行的任务](https://blog.langchain.com/introducing-ambient-agents/)。智能体交替进行[LLM调用和工具调用](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)，使用工具反馈来决定下一步。

![Image 3](https://blog.langchain.com/content/images/2025/07/image-2.png)

智能体交替进行[LLM调用和](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)[工具调用](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)，使用工具反馈来决定下一步

然而，长期运行的任务和工具调用的累积反馈意味着智能体通常使用大量token。这可能导致许多问题：可能[超过context窗口的大小](https://cognition.ai/blog/kevin-32b?ref=blog.langchain.com)，成本/延迟激增，或降低智能体性能。Drew Breunig[很好地概述了](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html?ref=blog.langchain.com)更长context可能导致性能问题的几种具体方式，包括：

* [Context中毒：当幻觉进入context时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html?ref=blog.langchain.com#context-poisoning)
* [Context分心：当context压倒训练时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html?ref=blog.langchain.com#context-distraction)
* [Context混乱：当多余的context影响响应时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html?ref=blog.langchain.com#context-confusion)
* [Context冲突：当context的部分内容不一致时](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html?ref=blog.langchain.com#context-clash)

![Image 4](https://blog.langchain.com/content/images/2025/07/image-3.png)

工具调用的context在多个智能体轮次中累积
