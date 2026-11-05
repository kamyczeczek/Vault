---
type: Concept
id: 120_icm_knowledge_big
title: "ICM_knowledge.md (part 121/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

This is not a prompt trick. The thinking behind it comes from decades of software engineering, all the way back to 1972. Separation of concerns. Modular composition. The idea that systems work better when each part does one job and the routing between parts is clear.

There is a full research paper on this if you want to go deep. It traces the history from early programming principles through to modern AI workflows and lays out a five-layer architecture (this video covers the three most important layers). You can download it and give it to Claude to explain it to you.

#### Research Paper:

[ ICM PAPER ]

------

Quick start: your first three files

If you want to start right now with the simplest possible version, here it is. Make a folder. Put three files in it.

— Tell Claude who you are, what this project is, and where things go.

# Identity

You are helping [YOUR NAME] with [WHAT YOU DO].

# Folder Structure

\-    /drafts — work in progress

\-    /final — finished outputs

\-    /references — background material

# Rules

\-    Read this file first on every new task

\-    Ask before creating files outside of /drafts

\-    When unsure, ask

— Describe the current project.

# Current Project

[What you are building or working on. 2-3 sentences.]

# What good looks like

[What a successful output looks like.]

# What to avoid

[Common mistakes or things you do not want.]

REFERENCES.md

— Background material Claude should know about.

# References

[Examples, links, style guides, notes. Anything Claude should have access to but does not need to act on directly.]

Point Claude at the folder (using Claude Code, or upload the files to a Claude Project, or paste the contents into your first message). Ask it something related to your project. Notice the difference.

------

Want to customize this for your specific use case?

3.2: Customizing for Your Use Case

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=1285fe09df7943e79e5d71c68b8b3ccb&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

walks through three real examples.

Want to understand

structured context changes AI output at a fundamental level?

2.3: How a 1953 Word Game Explains AI Memory

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=0964ed75790a415b909838050ecad3ea&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

traces it back to Mad Libs.

The concept of "value lives above whatever just got commoditized" shows up in

2.4: The Ladder That Explains Every AI Failure

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=d8d7d437b5c74dc4a026d1dbadbeeba2&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

Ready to see this running in the terminal?

4.1: Install and First Use
