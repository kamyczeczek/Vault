---
type: Concept
id: 70_icm_knowledge_big
title: "ICM_knowledge.md (part 71/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

You are a research assistant helping me prepare a literature review.

You are a Python developer who writes clean, well-documented code.

If you set up a CLAUDE.md file in 1.2, this part is already handled for your project. The file does this work for you in every conversation. But for one-off tasks or tasks where you need Claude to shift roles, you add identity at the top of your prompt.

One note: identity is the part most people skip. They jump straight to "write me a blog post" without telling Claude who is writing it. The output is always more generic without it.

------

Part 2: Task — What needs to get done?

Be specific. "Help me write something" is vague. "Write a 200-word product description for [X] targeting [Y] audience" gives Claude something to work with.

#### Good tasks have three things:

A clear action — write, review, analyze, compare, build, fix, summarize

A defined scope — how long, how many, what format, what section

Enough detail that someone unfamiliar with your project could attempt it

If you read your task out loud and a stranger could not start working on it without asking you five follow-up questions, the task is too vague.

------

Part 3: Context — What does Claude need to know?

This is the background. The constraints. The audience. Prior decisions. Relevant data. Anything Claude needs to do the task well that it would not know on its own.

If you are using the folder structure from 1.2, your CONTEXT.md handles the project-level stuff. But for individual prompts, you can also give context directly:

We are a 15-person startup. Our customers are mid-market HR directors. We just launched a feature that automates onboarding checklists. Here is the feature spec: [paste spec]

The more relevant context you give, the less Claude has to guess. Guessing is where AI outputs go sideways. If the output feels generic or off-target, the fix is almost always more context, not a better prompt.

------

Part 4: Constraints — What should Claude avoid?

This is the part where most people leave value on the table. Telling Claude what you do NOT want is just as useful as telling it what you do want.

Do not use jargon. Write at an 8th grade reading level.

Do not suggest solutions that require a paid API. Everything should use free tools.

Keep it under 300 words. No bullet points. Write in paragraphs.

Do not start with "In today's world" or any variation of it.

Constraints save you editing time. Every constraint you give is a mistake Claude will not make. Think about the last three times an AI output annoyed you. Those annoyances are constraints you did not set.

------

Part 5: Output Format — What should the result look like?

Tell Claude the shape of the answer. A list? A table? Three options to choose from? A code block with comments? A draft with placeholder sections?

Give me three headline options, each under 10 words, followed by a one-sentence explanation of the angle.
