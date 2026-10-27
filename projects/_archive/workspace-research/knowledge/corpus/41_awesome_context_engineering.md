---
type: Concept
id: 41_awesome_context_engineering
title: "Repository: yzfly/awesome-context-engineering (part 42/77)"
source: "awesome-context-engineering.txt"
tags: [1, 1-, 1234, 1工作, 2, L1407, a-theory-of-building-long-running-agents, adding-semantic-search-to-the-store, agentic, agents, anti-leakage, automate-ci-and-infra-workflows, collection, context-clash, context-confusion, context-distraction, context-engineering, context-offloading, context-poisoning, context-pruning, context-quarantine, context-summarization, contributing, english, expert-insights, featured-articles, fn, fnref, long-form-text, long-term-memory, manage-short-term-memory, memory, memory-types, model-context-protocol-mcp, notification-setup, planning, profile, prompt-engineering, rag, reflection, research-papers, schema, short-term-memory, star-history, star历史, state, threads, tool-loadout, tools--projects, what-is-context-engineering, yzfly, 专家观点, 中文, 什么是context工程, 工具与项目, 模型context协议-mcp, 研究论文, 精选文章, 贡献指南]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Following up on our earlier post, “[How Long Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)”, let’s run through the ways we can mitigate or avoid these failures entirely.

But before we do, let’s briefly recap some of the ways long contexts can fail:

*   **Context Poisoning:** When a hallucination or other error makes it into the context, where it is repeatedly referenced.
*   **Context Distraction:** When a context grows so long that the model over-focuses on the context, neglecting what it learned during training.
*   **Context Confusion:** When superfluous information in the context is used by the model to generate a low-quality response.
*   **Context Clash:** When you accrue new information and tools in your context that conflicts with other information in the prompt.

Everything here is about information management. Everything in the context influences the response. We’re back to the old programming adage of, “[Garbage in, garbage out](https://en.wikipedia.org/wiki/Garbage_in,_garbage_out).” Thankfully, there’s plenty of options for dealing with the issues above.

Context Management Tactics
--------------------------

*   [**RAG:** Selectively adding relevant information to help the LLM generate a better response](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#rag)
*   [**Tool Loadout:** Selecting only relevant tool definitions to add to your context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#tool-loadout)
*   [**Context Quarantine:** Isolating contexts in their own dedicated threads](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-quarantine)
*   [**Context Pruning:** Removing irrelevant or otherwise unneeded information from the context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-pruning)
*   [**Context Summarization:** Boiling down an accrued context into a condensed summary](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-summarization)
*   [**Context Offloading:** Storing information outside the LLM's context, usually via a tool that stores and manages the data](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html#context-offloading)

* * *

![Image 2: A stack of papers.](https://www.dbreunig.com/img/rag.png)

### RAG

_Retrieval-Augmented Generation (RAG) is the act of selectively adding relevant information to help the LLM generate a better response._

So much has been written about RAG, we’re not going to cover it today beyond saying: it’s very much alive.

Every time a model ups the context window ante, a new “RAG is Dead” debate is born. The last significant event was when Llama 4 Scout landed with a _10 million token window_. At that size it’s _really_ tempting to think, “Screw it, throw it all in,” and call it a day.
