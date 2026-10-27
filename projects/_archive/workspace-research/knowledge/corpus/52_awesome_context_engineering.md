---
type: Concept
id: 52_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 53/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

As Andrej Karpathy puts it, LLMs are like a [new kind of operating system](https://www.youtube.com/watch?si=-aKY-x57ILAmWTdw&t=620&v=LCEmiRjPEtQ&feature=youtu.be&ref=blog.langchain.com). The LLM is like the CPU and its [context window](https://docs.anthropic.com/en/docs/build-with-claude/context-windows?ref=blog.langchain.com) is like the RAM, serving as the model’s working memory. Just like RAM, the LLM context window has limited [capacity](https://lilianweng.github.io/posts/2023-06-23-agent/?ref=blog.langchain.com) to handle various sources of context. And just as an operating system curates what fits into a CPU’s RAM, we can think about “context engineering” playing a similar role. [Karpathy summarizes this well](https://x.com/karpathy/status/1937902205765607626?ref=blog.langchain.com):

> _[Context engineering is the] ”…delicate art and science of filling the context window with just the right information for the next step.”_

![Image 2](https://blog.langchain.com/content/images/2025/07/image-1.png)

Context types commonly used in LLM applications

What are the types of context that we need to manage when building LLM applications? Context engineering as an [umbrella](https://x.com/dexhorthy/status/1933283008863482067?ref=blog.langchain.com) that applies across a few different context types:

*   **Instructions** – prompts, memories, few‑shot examples, tool descriptions, etc
*   **Knowledge** – facts, memories, etc
*   **Tools** – feedback from tool calls

### Context Engineering for Agents

This year, interest in [agents](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com) has grown tremendously as LLMs get better at [reasoning](https://platform.openai.com/docs/guides/reasoning?api-mode=responses&ref=blog.langchain.com) and [tool calling](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com). [Agents](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com) interleave [LLM invocations and tool calls](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com), often for [long-running tasks](https://blog.langchain.com/introducing-ambient-agents/). Agents interleave [LLM calls and tool calls](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com), using tool feedback to decide the next step.

![Image 3](https://blog.langchain.com/content/images/2025/07/image-2.png)

Agents interleave[LLM calls and](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com)[tool calls](https://www.anthropic.com/engineering/building-effective-agents?ref=blog.langchain.com), using tool feedback to decide the next step
