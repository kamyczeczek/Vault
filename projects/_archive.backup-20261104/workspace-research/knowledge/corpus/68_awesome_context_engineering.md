---
type: Concept
id: 68_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 69/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

LangGraph使实现每种方法变得容易，LangSmith提供了测试智能体和跟踪context使用的简单方法。LangGraph和LangSmith一起为识别应用context工程的最佳机会、实现它、测试它并重复这一过程提供了良性反馈循环。

================================================
FILE: docs/manus/AI智能体的Context工程：构建Manus的经验教训.md
================================================
# AI智能体的Context工程：构建Manus的经验教训

原文链接：https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus

2025/7/18 --Yichao 'Peak' Ji

在[Manus](https://manus.im/app)项目的最初阶段，我和我的团队面临一个关键决策：我们应该使用开源基础模型训练一个端到端的智能体模型，还是基于前沿模型的[in-context learning](https://arxiv.org/abs/2301.00234)能力构建智能体？

回顾我在NLP领域的第一个十年，我们没有这样的选择余地。在[BERT](https://arxiv.org/abs/1810.04805)的遥远时代（是的，已经过去七年了），模型必须经过fine-tuning和评估才能迁移到新任务。即使模型相比今天的LLM来说非常小，这个过程每次迭代通常需要数周时间。对于快速发展的应用，特别是在产品市场契合度（PMF）之前，如此缓慢的反馈循环是致命的。这是我上一个创业公司的痛苦教训，当时我从零开始训练模型用于[开放信息抽取](https://en.wikipedia.org/wiki/Open_information_extraction)和语义搜索。然后[GPT-3](https://arxiv.org/abs/2005.14165)和[Flan-T5](https://arxiv.org/abs/2210.11416)出现了，我的内部模型一夜之间变得无关紧要。讽刺的是，正是这些模型标志着in-context learning的开始——以及一条全新的前进道路。

这个来之不易的教训让选择变得明确：Manus将押注于context工程。这使我们能够在几小时而不是几周内发布改进，并保持我们的产品与底层模型正交：如果模型进步是涨潮，我们希望Manus是船，而不是固定在海床上的柱子。

然而，context工程绝非简单直接。这是一门实验科学——我们已经重建了四次智能体框架，每次都是在发现更好的context塑造方法之后。我们亲切地将这种手动的架构搜索、prompt调整和经验猜测过程称为"随机梯度下降"（Stochastic Graduate Descent）。虽然不够优雅，但确实有效。

这篇文章分享了我们通过自己的"SGD"达到的局部最优解。如果你正在构建自己的AI智能体，我希望这些原则能帮助你更快地收敛。

### 围绕KV-Cache进行设计

如果我必须选择一个指标，我认为KV-cache命中率是生产阶段AI智能体最重要的单一指标。它直接影响延迟和成本。要理解原因，让我们看看[典型智能体](https://arxiv.org/abs/2210.03629)是如何运作的：

在接收到用户输入后，智能体通过一系列工具使用来完成任务。在每次迭代中，模型基于当前context从预定义的动作空间中选择一个动作。然后在环境中执行该动作（例如，Manus的虚拟机沙箱）以产生观察结果。动作和观察结果被附加到context中，形成下一次迭代的输入。这个循环持续进行，直到任务完成。

可以想象，context随着每一步而增长，而输出——通常是结构化的函数调用——保持相对较短。这使得智能体中的预填充与解码比率相比聊天机器人高度倾斜。例如，在Manus中，平均输入与输出token比率约为100:1。

幸运的是，具有相同前缀的context可以利用[KV-cache](https://medium.com/@joaolages/kv-caching-explained-276520203249)，这大大减少了首token时间（TTFT）和推理成本——无论你使用的是自托管模型还是调用推理API。我们说的不是小幅节省：例如，使用Claude Sonnet时，缓存的输入token成本为0.30美元/MTok，而未缓存的成本为3美元/MTok——相差10倍。

![Image 1](https://d1oupeiobkpcny.cloudfront.net/user_upload_by_module/markdown/310708716691272617/OhdKxGRSXCcuqOvz.png)

从context工程的角度来看，提高KV-cache命中率涉及几个关键实践：

1. **保持prompt前缀稳定**。由于LLM的[自回归](https://en.wikipedia.org/wiki/Autoregressive_model)特性，即使是单个token的差异也可能使该token之后的缓存失效。一个常见错误是在系统prompt开头包含时间戳——特别是精确到秒的时间戳。当然，这让模型能够告诉你当前时间，但也会破坏你的缓存命中率。

2. **使你的context仅追加**。避免修改之前的动作或观察结果。确保你的序列化是确定性的。许多编程语言和库在序列化JSON对象时不保证稳定的键排序，这可能会悄无声息地破坏缓存。

3. **在需要时明确标记缓存断点**。一些模型提供商或推理框架不支持自动增量前缀缓存，而是需要在context中手动插入缓存断点。分配这些断点时，要考虑潜在的缓存过期，至少确保断点包含系统prompt的结尾。

此外，如果你使用[vLLM](https://github.com/vllm-project/vllm)等框架自托管模型，请确保启用[前缀/prompt缓存](https://docs.vllm.ai/en/stable/design/v1/prefix_caching.html)，并使用会话ID等技术在分布式worker之间一致地路由请求。

### 掩码，而非移除

随着你的智能体承担更多能力，其动作空间自然变得更加复杂——简单来说，工具数量激增。最近[MCP](https://modelcontextprotocol.io/introduction)的流行只是火上浇油。如果你允许用户可配置的工具，相信我：总会有人将数百个神秘工具插入你精心策划的动作空间。结果，模型更可能选择错误的动作或采取低效的路径。简而言之，你的重装智能体变得更愚蠢了。
