---
type: Concept
id: 73_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 74/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

To solve this while still improving action selection, Manus uses a context-aware [state machine](https://en.wikipedia.org/wiki/Finite-state_machine) to manage tool availability. Rather than removing tools, it masks the token logits during decoding to prevent (or enforce) the selection of certain actions based on the current context.

![Image 2](https://d1oupeiobkpcny.cloudfront.net/user_upload_by_module/markdown/310708716691272617/cWxINCvUfrmlbvfV.png)

In practice, most model providers and inference frameworks support some form of response prefill, which allows you to constrain the action space without modifying the tool definitions. There are generally three modes of function calling (we'll use the [Hermes format](https://github.com/NousResearch/Hermes-Function-Calling) from NousResearch as an example):

•Auto – The model may choose to call a function or not. Implemented by prefilling only the reply prefix: <|im_start|>assistant

•Required – The model must call a function, but the choice is unconstrained. Implemented by prefilling up to tool call token: <|im_start|>assistant<tool_call>

•Specified – The model must call a function from a specific subset. Implemented by prefilling up to the beginning of the function name: <|im_start|>assistant<tool_call>{"name": “browser_

Using this, we constrain action selection by masking token logits directly. For example, when the user provides a new input, Manus must reply immediately instead of taking an action. We've also deliberately designed action names with consistent prefixes—e.g., all browser-related tools start with browser_, and command-line tools with shell_. This allows us to easily enforce that the agent only chooses from a certain group of tools at a given state without using stateful logits processors.

These designs help ensure that the Manus agent loop remains stable—even under a model-driven architecture.

### Use the File System as Context

Modern frontier LLMs now offer context windows of 128K tokens or more. But in real-world agentic scenarios, that's often not enough, and sometimes even a liability. There are three common pain points:

1.Observations can be huge, especially when agents interact with unstructured data like web pages or PDFs. It's easy to blow past the context limit.

2.Model performance tends to degrade beyond a certain context length, even if the window technically supports it.

3.Long inputs are expensive, even with prefix caching. You're still paying to transmit and prefill every token.

To deal with this, many agent systems implement context truncation or compression strategies. But overly aggressive compression inevitably leads to information loss. The problem is fundamental: an agent, by nature, must predict the next action based on all prior state—and you can't reliably predict which observation might become critical ten steps later. From a logical standpoint, any irreversible compression carries risk.
