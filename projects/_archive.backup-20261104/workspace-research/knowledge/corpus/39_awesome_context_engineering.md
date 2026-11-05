---
type: Concept
id: 39_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 40/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The problem is: if you put something in the context _the model has to pay attention to it._ It may be irrelevant information or needless tool definitions, but the model _will_ take it into account. Large models, especially reasoning models, are getting better at ignoring or discarding superfluous context, but we continually see worthless information trip up agents. Longer contexts let us stuff in more info, but this ability comes with downsides.

### Context Clash

_Context Clash is when you accrue new information and tools in your context that conflicts with other information in the context._

This is a more problematic version of _Context Confusion_: the bad context here isn’t irrelevant, it directly conflicts with other information in the prompt.

A Microsoft and Salesforce team documented this brilliantly in a [recent paper](https://arxiv.org/pdf/2505.06120). The team took prompts from multiple benchmarks and ‘sharded’ their information across multiple prompts. Think of it this way: sometimes, you might sit down and type paragraphs into ChatGPT or Claude before you hit enter, considering every necessary detail. Other times, you might start with a simple prompt, then add further details when the chatbot’s answer isn’t satisfactory. The Microsoft/Salesforce team modified benchmark prompts to look like these multistep exchanges:

![Image 3](https://www.dbreunig.com/img/sharded_prompt.png)

All the information from the prompt on the left side is contained within the several messages on the right side, which would be played out in multiple chat rounds.

The sharded prompts yielded dramatically worse results, with an average drop of 39%. And the team tested a range of models – OpenAI’s vaunted o3’s score dropped from 98.1 to 64.1.

What’s going on? Why are models performing worse if information is gathered in stages rather than all at once?

The answer is _Context Confusion_: the assembled context, containing the entirety of the chat exchange, contains early attempts by the model to answer the challenge _before it has all the information_. These incorrect answers remain present in the context and influence the model when it generates its final answer. The team writes:

> We find that LLMs often make assumptions in early turns and prematurely attempt to generate final solutions, on which they overly rely. In simpler terms, we discover that when LLMs take a wrong turn in a conversation, they get lost and do not recover.

This does not bode well for agent builders. Agents assemble context from documents, tool calls, and from other models tasked with subproblems. All of this context, pulled from diverse sources, has the potential to disagree with itself. Further, when you connect to MCP tools you didn’t create there’s a greater chance their descriptions and instructions clash with the rest of your prompt.

* * *
