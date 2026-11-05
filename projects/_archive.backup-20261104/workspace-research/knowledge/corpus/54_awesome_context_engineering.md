---
type: Concept
id: 54_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 55/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

When humans solve tasks, we take notes and remember things for future, related tasks. Agents are also gaining these capabilities! Note-taking via a “[scratchpad](https://www.anthropic.com/engineering/claude-think-tool?ref=blog.langchain.com)” is one approach to persist information while an agent is performing a task. The idea is to save information outside of the context window so that it’s available to the agent. [Anthropic’s multi-agent researcher](https://www.anthropic.com/engineering/built-multi-agent-research-system?ref=blog.langchain.com) illustrates a clear example of this:

> _The LeadResearcher begins by thinking through the approach and saving its plan to Memory to persist the context, since if the context window exceeds 200,000 tokens it will be truncated and it is important to retain the plan._

Scratchpads can be implemented in a few different ways. They can be a [tool call](https://www.anthropic.com/engineering/claude-think-tool?ref=blog.langchain.com) that simply [writes to a file](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem?ref=blog.langchain.com). They can also be a field in a runtime [state object](https://langchain-ai.github.io/langgraph/concepts/low_level/?ref=blog.langchain.com#state) that persists during the session. In either case, scratchpads let agents save useful information to help them accomplish a task.

**Memories**

Scratchpads help agents solve a task within a given session (or [thread](https://langchain-ai.github.io/langgraph/concepts/persistence/?ref=blog.langchain.com#threads)), but sometimes agents benefit from remembering things across _many_ sessions! [Reflexion](https://arxiv.org/abs/2303.11366?ref=blog.langchain.com) introduced the idea of reflection following each agent turn and re-using these self-generated memories. [Generative Agents](https://ar5iv.labs.arxiv.org/html/2304.03442?ref=blog.langchain.com) created memories synthesized periodically from collections of past agent feedback.

![Image 6](https://blog.langchain.com/content/images/2025/07/image-5.png)

An LLM can be used to update or create memories

These concepts made their way into popular products like [ChatGPT](https://help.openai.com/en/articles/8590148-memory-faq?ref=blog.langchain.com), [Cursor](https://forum.cursor.com/t/0-51-memories-feature/98509?ref=blog.langchain.com), and [Windsurf](https://docs.windsurf.com/windsurf/cascade/memories?ref=blog.langchain.com), which all have mechanisms to auto-generate long-term memories that can persist across sessions based on user-agent interactions.

### Select Context

_Selecting context means pulling it into the context window to help an agent perform a task._

**Scratchpad**
