---
type: Concept
id: 72_icm_knowledge_big
title: "ICM_knowledge.md (part 73/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

"Now that you have all sections, summarize the three strongest arguments and the two weakest."

This works better than pasting 50 pages into one message. Claude handles structured, sequential input more reliably than a wall of text with no markers.

One more trick: if your data is in a spreadsheet or table format, keep it in that format. Do not convert it to paragraphs before giving it to Claude. Tables and structured data are already token-efficient. Let Claude read them as-is.

------

A real example: one prompt, five parts

Here is what it looks like when you put all five parts together. This is a single prompt:

You are a technical writer who explains complex topics to a non-technical audience. (Identity)

Write a 300-word explanation of how API keys work and why someone would need one. (Task)

This is for a community of people who are learning to use AI tools. Most of them have never written code. They are encountering API keys for the first time because they are setting up Claude Code. (Context)

Do not use jargon without explaining it. Do not assume they know what a server is. Keep sentences short. (Constraints)

Start with a one-sentence analogy, then explain the concept, then give them the three steps to get their first API key. End with a one-line reassurance that this is easier than it sounds. (Output Format)

You will not always write prompts this long. But when you are getting vague or unhelpful responses, you can look at this structure and ask: which part am I missing?

------

------

This framework is how you talk to Claude. The folder structure from

1.2: Your First Folder

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

is how you give Claude memory across conversations. Identity and Context live in your files. Task and Constraints live in your prompts.

Want to understand why structured input changes these output at a fundamental level?

2.3: How a 1953 Word Game Explains AI Memory

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

traces prompting back to fill-in-the-blank word games and context windows.

Learning the Abstraction

series (Section 2) goes deeper into how AI processes information and why specific structure matters at every level. Start with the overview at

2.1: Video Text Guide

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=e171154adddc431ea52ff98a20f61d4f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

In Premium and Level 2+ courses, we apply this framework to specific use cases: building automations, writing production content, working with code. Everything builds on what you learned here.

------

Next Up: Section 2 —

Why This Works (The Abstraction Series)
