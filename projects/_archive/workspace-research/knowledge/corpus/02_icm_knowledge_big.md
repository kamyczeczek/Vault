---
type: Concept
id: 02_icm_knowledge_big
title: "ICM_knowledge.md (part 3/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Have Claude create a product requirements document. Phases. Stacks. What to cut. What to keep. Edit it before any code exists.

1. Build inside your     workspace

Don't create a separate folder. Build where your context already lives. Claude can reference your actual workflow while building the tool for it.

1. Work in sessions

Claude runs out of tokens. You run out of energy. Break the build into sessions. Each session picks up where the last one left off because the PRD and workspace context persist.

------

Who This Is For

#### This course is for people who:

Have completed the Foundation course (or equivalent)

Are comfortable with Claude Code

Want to see how a real build happens, not just the polished result

Are considering building their own tools around Claude

If you haven't set up Claude Code yet, go to [Foundation 4.1: Install and First Use] first.

If you're not sure whether you need a custom front-end, you probably don't. Stay at Level 3 until you hit a wall that VS Code can't solve.

------

PRD Prompt Template

I want to build [describe what you're building].

Here's my current folder structure and workflow: [paste CLAUDE.md or describe]

Here are repos that do something similar: [paste links]

Make a PRD markdown for Claude Code to read and build from. Include:

\-    What we're building and why

\-    Target user (me, for now)

\-    Existing repos we're pulling from and what we're taking

\-    Tech stack recommendations

\-    What features to cut (keep it minimal)

\-    Phases from MVP to full version

Break it into early phase (get something working) and late phase (polish and features).

------

#### Should you even build this? Review the Ladder:

2.4 The Ladder That Explains Every AI Failure

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

Need Claude Code set up first?

4.1 Install and First Use

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

How does the folder architecture inform this?

3.1 The Full Walkthrough

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

Ready for the full build templates?

https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

------

The first build session. You'll see the PRD get created, the workspace get set up, and the research phase that happens before any code exists.

------

Jake's content\Building Your Stack\1.2 How I Use Claude Code in the Build Process.md

What You'll Get From This
