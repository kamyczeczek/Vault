---
type: Concept
id: 44_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 45/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

> Our internal evaluations show that multi-agent research systems excel especially for breadth-first queries that involve pursuing multiple independent directions simultaneously. We found that a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval. For example, when asked to identify all the board members of the companies in the Information Technology S&P 500, the multi-agent system found the correct answers by decomposing this into tasks for subagents, while the single agent system failed to find the answer with slow, sequential searches.

This approach also helps with tool loadouts, as the agent designer can create several agent archetypes with their own dedicated loadout and instructions for how to utilize each tool.

The challenge for agent builders, then, is to find opportunities for isolated tasks to spin out onto separate threads. Problems that require context-sharing among multiple agents aren’t particularly suited to this tactic.

If your agent’s domain is at all suited to parallelization, be sure to [read the whole Anthropic write up](https://www.anthropic.com/engineering/built-multi-agent-research-system). It’s excellent.

![Image 5: Pruning shears](https://www.dbreunig.com/img/context_pruning.png)

### Context Pruning

_Context Pruning is the act of removing irrelevant or otherwise unneeded information from the context._

Agents accrue context as they fire off tools and assemble documents. At times, it’s worth pausing to assess what’s been assembled and remove the cruft. This could be something you task your main LLM with, or you could design a separate LLM-powered tool to review and edit the context. Or you could choose something more tailored to the pruning task.

Context pruning has a (relatively) long history, as context lengths were a more problematic bottleneck in the natural language processing (NLP) field, prior to ChatGPT. A current pruning method, building on this history, is [Provence](https://arxiv.org/abs/2501.16214), “an efficient and robust context pruner for Question Answering.”

Provence is fast, accurate, simple to use, and relatively small – only 1.75 GB. You can call it in a few lines, like so:

```
from transformers import AutoModel

provence = AutoModel.from_pretrained("naver/provence-reranker-debertav3-v1", trust_remote_code=True)

# Read in a markdown version of the Wikipedia entry for Alameda, CA
with open('alameda_wiki.md', 'r', encoding='utf-8') as f:
    alameda_wiki = f.read()

# Prune the article, given a question
question = 'What are my options for leaving Alameda?'
provence_output = provence.process(question, alameda_wiki)
```

Provence edited down the article, cutting 95% of the content, leaving me with only [this relevant subset](https://gist.github.com/dbreunig/b3bdd9eb34bc264574954b2b954ebe83). It nailed it.
