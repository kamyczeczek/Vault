---
type: Concept
id: 232_icm_knowledge_big
title: "ICM_knowledge.md (part 233/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

✍️ David's note: "A prompt is a wish. A brief is a contract." That line alone is worth the click. Ari keeps hammering the same point from different angles and it keeps landing — the quality of your output is capped by the clarity of your input. Pairs well with her four-phase build post.

------

david vogel\David and Jake's Picks V2\Why your cold emails get ignored.md

Why your cold emails get ignored

📝 What this is: A cold email system that scrapes prospect websites and uses AI to generate hyper-relevant opening lines — taking reply rates from 3% to 10% and booking 9 calls per week.

💡 Why it matters: If your outreach still relies on mail-merge fields, you're getting ignored — this shows how to automate genuine relevance at scale using n8n and OpenAI.

🏷️ Tags: workflow-design, automation, prompting, client-work, n8n

⏱️ 4 min read | 🔓 Free

✍️ David's note: This is folder architecture thinking applied to outreach instead of code. Muhammad built a pipeline that does the research humans skip — scrape the site, extract what actually matters, write like you read it. The n8n workflow is the real takeaway here for anyone doing client acquisition.

------

david vogel\David and Jake's Picks V2\A completely markdown based task management system\A completely markdown based task management system.md

A completely markdown based task management system

📝 What this is: A full task management system built entirely in markdown files — syncs across machines via terminal hooks, uses AI to prioritize your day, and works offline.

💡 Why it matters: If your task system lives in a proprietary app, your AI can't read it — this keeps everything in plain text where both you and your tools have full access.

🏷️ Tags: folder-architecture, workflow-design, templates, automation, claude-code

⏱️ 5 min read | 🔓 Free

✍️ David's note: This is what happens when someone takes "your folder is your operating system" seriously. Roc built exactly what the course philosophy points toward — plain text, git-synced, AI-readable. The capture-to-prioritize loop is especially clever. GitHub repo included so you can fork it today.

------

david vogel\David and Jake's Picks V2\A completely markdown based task management system\build-instructions.md

TaskSystem — Build Instructions

Read this entire file before asking any questions. You are setting up a personal task and project management system for the user from scratch.

------

What You Are Building

#### Two integrated subsystems:

— Daily task management. You manage the task board (TASKS.md). On each session start, you generate FOCUS.md matched to the user's energy level. You track recurring tasks and run weekly retrospectives on Sundays.

— Project lifecycle management. Projects move from Idea → Seed → Scoped → Active → Paused. Each active project has its own folder with ideas, tasks, and resources files.

All files are plain markdown. The user never edits TASKS.md or PROJECTS.md directly — they report changes in chat.

------
