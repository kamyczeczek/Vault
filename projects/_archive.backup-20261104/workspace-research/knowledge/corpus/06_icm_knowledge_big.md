---
type: Concept
id: 06_icm_knowledge_big
title: "ICM_knowledge.md (part 7/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Working Backwards

Gave Claude the markdown file of the folder structure

"What if we built a front-end around this exact system?"

Claude generated architecture ideas

📄 The PRD Approach

What is a PRD?

Product Requirements Document

Used in software development

Integrations

Goals & targeting

Avoid building everything at once

Break work into

(Early → Late)

editable, readable document

🔄 Workflow Strategy

Claude generates the PRD markdown

Creator reviews & edits (leveraging software background)

#### Step 3 (Optional):

Feed PRD into another Claude instance as an

Drop PRD into workspace

#### Open Claude Code and say:

"Read the PRD for the front end"

Claude builds the front-end

inside the workspace

🎬 Upcoming Content

Quick update video

(this content)

Full course

on both topics coming soon

🔑 Key Principles

existing tools

, don't start from scratch

before building

Phase-based

development

Claude can act as both

Desktop app for heavy lifting; PRD for structured planning

------

Jake's content\Building Your Stack\1.3 Designing for Your Use Case.md

What You'll Get From This

A look inside a real build session: how Claude Code works through a PRD, uses plan mode and sub-agents, and sometimes makes better decisions than what you asked for.

------

What You're Watching

This is less of a lecture and more of a live stream. You're watching me work.

The PRD is done. The workspace is set up. Now I'm letting Claude Code run through the build while I observe, intervene when needed, and explain what's happening.

If parts of this feel fast or technical, that's fine. The goal isn't to follow along step by step. The goal is to see how a real build actually happens.

------

I'm working inside my Animation Studio workspace. The front-end folder is created. The PRD is dropped in.

#### The PRD describes:

What I'm building (a control surface for my workflow)

The repos I'm pulling from

What to cut from those repos

The panel layout I want (workflow map, file editor, Claude chat)

The phases and steps

Claude Code can read all of this. It knows where we are. It knows what we're building.

------

Starting the Build

I tell Claude to read the PRD and confirm it understands.

Hey, read this PRD and make sure you're up to speed on everything.

Claude summarizes back what it understood. I clarify the parts that matter most:

I want to clean and edit stuff easily

I want control over files and routing

I want to automate things and swap files around

The abstract goal isn't a prettier Claude front-end. It's a control surface where I can fluidly switch between "I'm driving" and "Claude's driving."

That last part is the key. Sometimes I want to edit every individual file manually. Sometimes I want to automate the whole pipeline and trust Claude to run it. The interface should let me switch between those modes without friction.

------

Plan Mode vs Execution Mode

When I say "let's go ahead and start," Claude enters plan mode.
