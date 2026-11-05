---
type: Concept
id: 05_icm_knowledge_big
title: "ICM_knowledge.md (part 6/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Claude reading the PRD and confirming it understands

Plan mode vs. execution mode

Sub-agents fetching repos and studying workspace structure

Claude making decisions that are sometimes better than what I told it to do

The reality of a long-running build session

This lesson was about research and planning. The next one is about watching Claude work.

------

PRD Template

I want to build [describe what you're building].

Here's my current folder structure and workflow: [paste CLAUDE.md or describe]

Here are repos that do something similar: [paste links]

Make a PRD markdown for Claude Code to read and build from. Include:

\-    What we're building and why

\-    Target user (me, for now)

\-    Existing repos we're pulling from and what we're taking

\-    What stacks those repos use

\-    What features to cut

\-    Phases from MVP to full version

\-    Steps to execute in order

This PRD should be readable by Claude Code so it always knows where we are in the project.

------

Haven't set up Claude Code?

4.1 Install and First Use

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### The folder architecture this wraps around:

3.1 The Full Walkthrough

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

Want the full PRD and workspace files?

https://www.skool.com/quantum-quill-lyceum-1116/classroom/7634b927?md=a7c8cac8330b4270bda9a02e75bdcdcf&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

------

The research is done. The PRD is set. Now we watch Claude work. Plan mode, sub-agents, web fetches, and what happens when Claude makes better decisions than what I asked for.

🧠 Front-End UI for Controlling Claude Code – Mind Map

🎯 The Origin

David's Question

Wanted to control Claude via a front-end UI

Currently using

(recommended setup)

Desired better

monitoring/observability

💰 Cost Considerations

Subscription vs API

Anthropic Subscription

→ Lower cost

→ Expensive for heavy usage

Front-End Challenge

Easier to use API calls in a custom UI

Controlling Claude Code directly from a front-end feels "clunky"

🔍 Research & Discovery

Open-Source Solutions

Repo 1: Downloadable front-end to control Claude

control of Claude

Remote Control

Already installed & using Claude via

Video tutorial planned

💡 The Creator's Vision

Custom Front-End Project

Navigate folders visually

Mind Map / Web Map

view (not just simple folder tree)

Potential to generate a

web service

"Don't reinvent the wheel"

Leverage existing open-source repos

Build on personal animation workflow structure

📁 Personal Animation Workflow

Existing Structure

Scripts → Animations pipeline

Complex folder/file system

Course coming to break it all down
