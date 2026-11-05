---
type: Concept
id: 43_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 44/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The “Less is More” paper notes two other benefits to smaller contexts: reduced power consumption and speed, crucial metrics when operating at the edge (meaning, running an LLM on your phone or PC, not on a specialized server). Even when their dynamic tool selection method _failed_ to improve a model’s result, the power savings and speed gains were worth the effort, yielding savings of 18% and 77%, respectively.

Thankfully, most agents have smaller surface areas that only require a few, hand-curated tools. But if the breadth of functions or the amount of integrations needs to expand, always consider your loadout.

![Image 4: A belljar](https://www.dbreunig.com/img/context_quarantine.png)

### Context Quarantine

_Context Quarantine is the act of isolating contexts in their own dedicated threads, each used separately by one or more LLMs._

We see better results when our contexts aren’t too long and don’t sport irrelevant content. One way to achieve this is to break our tasks up into smaller, isolated jobs – each with their own context.

There are [many](https://arxiv.org/abs/2402.14207)[examples](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/) of this tactic, but an accessible write up of this strategy is Anthropic’s [blog post detailing their multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system). They write:

> The essence of search is compression: distilling insights from a vast corpus. Subagents facilitate compression by operating in parallel with their own context windows, exploring different aspects of the question simultaneously before condensing the most important tokens for the lead research agent. Each subagent also provides separation of concerns—distinct tools, prompts, and exploration trajectories—which reduces path dependency and enables thorough, independent investigations.

Research lends itself to this design pattern. When given a question, several subquestions or areas of exploration can be identified and separately prompted using multiple agents. This not only speeds up the information gathering and distillation (if there’s compute available), but it keeps each context from accruing too much information or information not relevant to a given prompt, delivering higher quality results:
