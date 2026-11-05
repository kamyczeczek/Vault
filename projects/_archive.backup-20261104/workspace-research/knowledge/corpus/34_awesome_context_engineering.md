---
type: Concept
id: 34_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 35/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

1.   Call `claude -p “<your prompt>” --json | your_command`, where `your_command` is the next step of your processing pipeline
2.   That’s it! JSON output (optional) can help provide structure for easier automated processing.

For both of these use cases, it can be helpful to use the `--verbose` flag for debugging the Claude invocation. We generally recommend turning verbose mode off in production for cleaner output.

What are your tips and best practices for working with Claude Code? Tag @AnthropicAI so we can see what you're building!

Acknowledgements
----------------

Written by Boris Cherny. This work draws upon best practices from across the broader Claude Code user community, whose creative approaches and workflows continue to inspire us. Special thanks also to Daisy Hollman, Ashwin Bhat, Cat Wu, Sid Bidasaria, Cal Rueb, Nodir Turakulov, Barry Zhang, Drew Hodun and many other Anthropic engineers whose valuable insights and practical experience with Claude Code helped shape these recommendations.

================================================
FILE: docs/claudecode/effective-context-engineering-for-ai-agents.md
================================================
# AI智能体的有效上下文工程

**发布于2025年9月29日**

上下文是AI智能体的关键但有限的资源。本文探讨如何有效管理和策划驱动智能体的上下文。

经过几年对提示工程的关注后，一个新术语开始凸显：**上下文工程**。使用语言模型的重点正从寻找合适的提示词和短语，转向回答更广泛的问题："什么样的上下文配置最有可能产生模型的期望行为？"

上下文是指从大语言模型(LLM)采样时包含的全部token。工程问题在于：在LLM固有约束下，优化这些token的效用以持续达成期望结果。有效驾驭LLM通常需要**从上下文角度思考**——即考虑LLM在任何时刻可用的整体状态及该状态可能产生的行为。

本文将探讨上下文工程这门新兴艺术，并提供构建可控、有效智能体的精细化思维模型。

## 上下文工程 vs. 提示工程

在Anthropic，我们视上下文工程为提示工程的自然演进。**提示工程**指编写和组织LLM指令以获得最佳结果的方法。**上下文工程**则指在LLM推理期间策划和维护最优token集（信息）的策略，包括提示之外的所有其他信息。

早期，提示是AI工程工作的最大组成部分，因为多数用例需要针对单次分类或文本生成任务优化的提示。然而，随着我们转向构建可多轮推理、长时程运行的智能体，我们需要管理整个上下文状态的策略（系统指令、工具、MCP、外部数据、消息历史等）。

循环运行的智能体会生成越来越多可能与下一轮推理相关的数据，这些信息必须循环精炼。上下文工程就是从不断演变的可能信息中，策划什么将进入有限上下文窗口的艺术和科学。

![alt text](image.png)
**[图：提示工程 vs. 上下文工程对比图]**

与编写提示的离散任务不同，上下文工程是迭代的，每次决定传递给模型什么内容时都会进行策划。

## 为什么上下文工程对构建强大智能体至关重要

尽管LLM速度快且能处理越来越大的数据量，但我们观察到它们像人类一样，在某个点会失去焦点或感到困惑。"大海捞针"式基准测试研究发现了**上下文衰减**现象：随着上下文窗口中token数量增加，模型从该上下文准确回忆信息的能力下降。

虽然不同模型的降级程度不同，但这一特征在所有模型中都会出现。因此，**上下文必须被视为边际收益递减的有限资源**。像人类工作记忆容量有限一样，LLM有"注意力预算"，解析大量上下文时会消耗这一预算。每引入一个新token都会在一定程度上消耗预算，增加了仔细策划LLM可用token的必要性。

这种注意力稀缺源于LLM的架构约束。LLM基于Transformer架构，使每个token能够关注整个上下文中的其他所有token，产生n个token的n²对配对关系。

随着上下文长度增加，模型捕捉这些配对关系的能力被拉伸变薄，在上下文大小和注意力聚焦之间产生自然张力。此外，模型从训练数据分布中形成注意力模式，其中短序列通常比长序列更常见。这些现实意味着**深思熟虑的上下文工程对构建强大智能体至关重要**。

## 有效上下文的构成

鉴于LLM受限于有限的注意力预算，良好的上下文工程意味着找到**最小的高信号token集**，最大化某种期望结果的可能性。

### 系统提示

应极其清晰，使用简单直接的语言，在适当的高度呈现想法。**适当高度**是两种常见失败模式之间的黄金地带：一个极端是硬编码复杂、脆弱的逻辑；另一极端是提供模糊的高级指导。最优高度在两者之间取得平衡：既足够具体以有效指导行为，又足够灵活以提供强启发式引导。

![alt text](image-1.png)

**[图：系统提示校准图]**
一端是脆弱的硬编码提示，另一端是过于笼统或错误假设共享上下文的提示。

我们建议将提示组织成不同部分（如`<background_information>`、`<instructions>`、`## Tool guidance`等），使用XML标签或Markdown标题划分这些部分。

无论如何构建系统提示，都应追求**充分概述期望行为的最小信息集**。（注意：最小不等于简短；仍需预先提供足够信息）。最好从用最佳模型测试最小提示开始，然后根据初始测试中发现的失败模式添加清晰的指令和示例。

### 工具
