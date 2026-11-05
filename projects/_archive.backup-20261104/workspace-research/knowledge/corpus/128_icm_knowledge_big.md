---
type: Concept
id: 128_icm_knowledge_big
title: "ICM_knowledge.md (part 129/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Before you finalize your setup, take five minutes to read the mistakes people make most often. Easier to avoid them now than fix them later.

------

Jake's content\The Foundation\3.3 Common Mistakes and How to Fix Them.md

3.3 Common Mistakes and How to Fix Them

What You'll Get From This

The seven mistakes people make most often when setting up the folder architecture, and how to fix each one before it wastes your time.

------

Every one of these comes from real community members. People post their setups, run into walls, and ask for help. The same problems show up over and over. If you read this before you finalize your structure from 3.2, you will skip most of them.

------

Mistake 1: Making the CLAUDE.md too long

The CLAUDE.md is a routing file. It tells Claude where things are and where to go. That is its job. It is not a project brief. It is not a style guide. It is not a brain dump of everything you want Claude to know.

When the CLAUDE.md gets too long, two things happen. First, Claude burns tokens reading information that is not relevant to the current task. Second, the signal gets buried in noise. The routing instructions (the part that actually matters) get lost in paragraphs of background context.

Your CLAUDE.md should fit on one screen. Identity, folder structure, routing table, naming conventions. That is it. Everything else belongs in a workspace CONTEXT.md where it only gets loaded when Claude is actually working in that area. If your CLAUDE.md is longer than 40-50 lines, you have context files hiding inside it. Pull them out.

------

Mistake 2: Skipping the routing table

Some people set up the folders, write the context files, and never put a routing table in the CLAUDE.md. They assume Claude will figure it out.

Sometimes Claude does figure it out. But "sometimes" is the problem. Without a routing table, Claude has to guess which files to read and which to skip. It might read everything (wasting tokens) or read the wrong context file (getting confused about what workspace it is in). The output gets inconsistent. Some responses are great, some are off, and you cannot tell why.

The routing table does not need to be complicated. Three columns: task, where to go, what to read. One row per type of work. Claude reads the table, matches the task, goes to the right place. Every time.

| **Task**            | **Go to**     | **Read**   |
| ------------------- | ------------- | ---------- |
| Write content       | /script-lab   | CONTEXT.md |
| Build something     | /production   | CONTEXT.md |
| Publish or schedule | /distribution | CONTEXT.md |

If you added skills (Layer 3), add a fourth column. Otherwise, three is enough.

------

Mistake 3: Too many workspaces
