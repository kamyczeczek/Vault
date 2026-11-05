---
type: Concept
id: 46_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 47/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Again, [Anthropic has a good write up of the technique](https://www.anthropic.com/engineering/claude-think-tool), which details their “think” tool, which is basically a scratchpad:

> With the “think” tool, we’re giving Claude the ability to include an additional thinking step—complete with its own designated space—as part of getting to its final answer… This is particularly helpful when performing long chains of tool calls or in long multi-step conversations with the user.

I really appreciate the research and other writing Anthropic publishes, but I’m not a fan of this tool’s name. If this tool were called `scratchpad`, you’d know its function _immediately_. It’s a place for the model to write down notes that don’t cloud its context, that are available for later reference. The name “think” clashes with “[extended thinking](https://www.anthropic.com/news/visible-extended-thinking)” and needlessly anthropomorphizes the model…but I digress.

Having a space to log notes and progress _works_. Anthropic shows pairing the “think” tool with a domain-specific prompt (which you’d do anyway in an agent) yields significant gains, up to a 54% improvement against a benchmark for specialized agents.

Anthropic identified three scenarios where the context offloading pattern is useful:

> 1.   Tool output analysis. When Claude needs to carefully process the output of previous tool calls before acting and might need to backtrack in its approach;
> 2.   Policy-heavy environments. When Claude needs to follow detailed guidelines and verify compliance; and
> 3.   Sequential decision making. When each action builds on previous ones and mistakes are costly (often found in multi-step domains).

* * *

Context management is usually the hardest part of building an agent. Programming the LLM to, as Karpathy says, “[pack the context windows just right](https://x.com/karpathy/status/1937902205765607626)”, smartly deploying tools, information, and regular context maintenance is _the_ job of the agent designer.

The key insight across all the above tactics is that _context is not free_. Every token in the context influences the model’s behavior, for better or worse. The massive context windows of modern LLMs are a powerful capability, but they’re not an excuse to be sloppy with information management.

As you build your next agent or optimize an existing one, ask yourself: Is everything in this context earning its keep? If not, you now have six ways to fix it.

* * *

1.   Hell, this entire list of tactics is a strong argument [you should program your contexts](https://www.dbreunig.com/2025/06/10/let-the-model-write-the-prompt.html).[↩](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#fnref:structure)

================================================
FILE: docs/dbreunig/上下文修复的实用指南.md
================================================
标题：如何修复你的上下文

来源地址：https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html

发布时间：2025-06-26T08:23:00-07:00
