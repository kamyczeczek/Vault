---
type: Concept
id: 111_icm_knowledge_big
title: "ICM_knowledge.md (part 112/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

This maps onto something we already understand. Think about the difference between a function call and a running process. A function takes an input and returns an output. It does not decide what to do next. The program that called the function makes that decision. Each call to a language model works the same way. Prompt in, text out. The agentic behavior, the appearance of autonomy, emerges from the orchestration code that wraps those calls.

There are systems beginning to emerge where models genuinely operate in autonomous loops. That is a real and meaningful evolution. But it is not what the vast majority of deployed systems are doing today. Conflating the two makes it harder to understand what is actually happening when these systems work.

------

The orchestration layer: async programming and concurrency

So let us look at what is actually happening. Open the Ethics Engine and the first thing you find is not a model. It is a traffic controller.

The Ethics Engine needs to administer dozens of psychometric items across multiple models simultaneously: Claude, GPT, Llama, Gemini. Each provider has different rate limits, different response formats, different failure modes. So there is an orchestration layer that manages all of this. It is written in Python and it is doing something that would be immediately recognizable to anyone who has built a web scraper, a trading system, or a ticket reservation platform.

It manages concurrency. It handles retries when requests fail. It queues prompts and dispatches them in order. It tracks which items have been completed and which are still pending.

None of this is AI. This is async programming. Concurrency management. These are patterns that existed long before language models and they work the same way here as they do anywhere else.

The model at the other end of each request has no awareness that any of this is happening. It receives a prompt. It returns text. That is the full extent of its involvement in this layer.

------

How systems talk to each other: APIs

How does the prompt even get to the model? When we say "called an API," there is a concept buried in that sentence that tends to get skipped when people teach this.

An API (application programming interface) is a contract. Two pieces of software agree in advance on the shape of their conversation. What the request will look like. What the response will look like. What is allowed and what is not. Neither side needs to understand the other's internals. They just need to honor the agreement.

When the Ethics Engine sends a prompt to Claude, what actually happens is an HTTP request carrying JSON (a structured text format) that goes to an endpoint at Anthropic's servers. That JSON contains the prompt, the model name, and some parameters. The server processes it and returns JSON containing the model's response.
