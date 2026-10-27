---
type: Concept
id: 08_icm_knowledge_big
title: "ICM_knowledge.md (part 9/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

The PRD turns a stateless tool into something with memory. The memory lives in the file system, not in Claude's context window.

------

When Claude Runs Out of Tokens

Long builds hit token limits. Claude gets slower. Responses get shorter. Eventually it stops being useful.

When this happens, I start a new session. The PRD is still there. The code that's been written is still there. I tell Claude to read the PRD, look at what's been built, and continue from where we left off.

This is working in sessions. Each session picks up where the last one stopped. The workspace is the continuity.

------

What Got Built This Session

#### By the end of this session:

Both repos analyzed (Claude Code Web and the CLI UI)

Key patterns identified

Initial structure started

Foundation laid for the panel layout

The workflow visualization (the hardest part) comes later. That's probably a separate session. Maybe multiple.

------

The Reality of Building

This isn't clean. Claude makes decisions I didn't expect. Some are better than what I asked for. Some need correction.

The PRD keeps us aligned. When Claude drifts, I point back to the document. "Hey, that's not what we said we wanted." Claude adjusts.

You're not going to get a perfect build in one session. You're going to get progress. The workspace accumulates that progress. The next session builds on it.

------

Commands You'll See

What Claude Says What It Means "Entering plan mode" Claude is thinking through steps before acting "Task: agent" A sub-agent is being spawned for a specific task "bash: find..." Claude is running a terminal search command "web_fetch" Claude is pulling a file from the internet "read_file" Claude is reading a file from your workspace

Session Management

#### When you hit token limits:

Note where you stopped

Start a new Claude Code session

Tell Claude to read the PRD

Tell Claude to look at what's been built

Continue from where you left off

The workspace persists. Claude's memory doesn't. Use the workspace as memory.

------

#### Folder architecture that makes this possible:

3.1 The Full Walkthrough

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

Want the actual PRD and workspace files?

https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

------

A curated list of open-source AI UI projects worth studying, with notes on what to learn from each.

🧠 Building a Custom Front-End for Claude Code Animation Workflow – Mind Map

🎯 Project Goal

Custom front-end

for managing animation workspace

Not calling Claude API (avoid fees)

Navigate and organize project folders visually

Maintain existing workflow

Scripts → Animation Studio → Specs → Renders

Keep it clean, modular, personal
