---
type: Concept
id: 138_icm_knowledge_big
title: "ICM_knowledge.md (part 139/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

------

Jake's content\The Foundation\4.2 Claude Code in Practice.md

4.2: Claude Code in Practice

What You'll Get From This

You will understand what makes Claude Code different from the chat interface, see the iteration loop in action, and walk away with a real deliverable built from your own files.

------

Video: Session 2 — Claude Code in Practice

#### Coming Soon

------

The real power

Claude Code is not smarter than Claude Desktop. It is the same model. The difference is what it can reach. Claude Code can see your work, touch your files, and iterate on its own output. That changes everything about how you work with it.

The loop looks like this: Read → Think → Write → Check → Adjust. Claude reads your files, thinks about the task, writes output, checks its own work, and adjusts. In the chat interface, that loop runs once and stops. In Claude Code, it runs until the job is done.

------

Example: meeting notes

Here is a task that shows the difference clearly.

You have 15 meeting notes. You want every decision made this quarter, organized by project.

#### The Desktop approach:

Open file 1. Copy the text. Paste it into Claude. Ask for analysis. Repeat 15 times. Then manually combine all 15 responses into one document. About an hour of work.

#### The Claude Code approach:

One prompt: "Read every file in /meeting-notes/ and summarize all decisions, organized by project." One prompt. 15 files. 90 seconds.

The model gives you the same quality analysis either way. The difference is how much manual work you do around it. Claude Code eliminates the copy-paste layer entirely.

------

Claude's context window is roughly 200K tokens. A typical meeting note is about 2,000 tokens. 15 notes is about 30,000 tokens. Well within the window.

In Desktop, you paste one file at a time and lose context between chats. Each conversation starts fresh. You are working against the architecture.

In Claude Code, it loads what it needs from your file system and keeps full context across the task. You are working with the architecture.

#### This is the same principle from

2.3 (How a 1953 Word Game Explains AI Memory)

: the context window is working memory. Claude Code lets you fill that working memory from your actual files instead of from your clipboard.

------

Tips that save hours

Be specific.

"Analyze this" is weak. "Identify the three largest cost items and format as a table" is strong. The more specific your instruction, the less Claude has to guess. This is the Task part of the prompting framework from

Tell it where to put the output.

"Save the result as summary.md in this folder." Claude Code can write files. Let it. If your output lives in a chat window, you still have to copy it somewhere. If Claude writes it directly to a file, it is already where it needs to be.

Output wrong? Do not start over.
