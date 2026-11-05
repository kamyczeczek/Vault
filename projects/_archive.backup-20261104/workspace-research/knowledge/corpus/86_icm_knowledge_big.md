---
type: Concept
id: 86_icm_knowledge_big
title: "ICM_knowledge.md (part 87/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

— This is the closest analog to read-only memory. Fixed at training time. It encodes patterns, knowledge, capabilities. You cannot change it during a conversation. It is just what the model knows.

Context window

— This is working memory. Everything the model can attend to when generating a response: the system prompt, the conversation history, any documents or data that have been included. It is temporary. It exists only for this interaction. When the conversation ends, it is gone.

System prompt

— This functions like firmware. It sets the operating parameters. It tells the model what it is, who it is, what it should do, what constraints to follow. The user typically does not see it, but it shapes everything in the conversation.

Retrieved context

— Things pulled dynamically based on a query. A relevant document. A skill file with specialized instructions. This is like loading from disk into RAM. It happens on demand.

Persistent memory

— Information stored between conversations and selectively loaded when relevant. Summaries, key facts, preferences. Not everything, just what seems useful. It is retrieved the same way as other context, but the concept is slightly different: it carries across sessions.

If you squint, this looks like a traditional hierarchy. Speed versus capacity trade-offs. Data moving between levels. Locality patterns determining what gets loaded.

But there is a difference, and it is not a small one.

------

Code and data are the same thing

In AI systems, code and data are the same thing.

The system prompt is not compiled separately from the user's message. The skill file is not executed through a different pathway than the conversation history. They are all just text. All processed identically. All tokens in a sequence that the model attends to and continues.

When you write an instruction in a system prompt, you are not giving the model a command that it executes. You are adding words to a document that the model will read and then continue. The instructions become part of the context. Reading it is the execution.

This is why prompt injection works. If someone puts text in a document that says "ignore your previous instructions" and that document gets loaded into the context, the model reads those words the same way it reads everything else. There is no separate layer that validates code versus data. There is no boundary to cross. It is all just text.

This is not a bug. It is the architecture.

------

The Grace Hopper pivot

In 1952, Grace Hopper had a working compiler. It could take instructions written in something closer to English and translate them into machine code. Nobody believed her. She said: "I had a running compiler and nobody would touch it. They told me computers could only do arithmetic."

She spent years trying to convince people that this kind of abstraction was truly possible. People were, in her words, allergic to change.
