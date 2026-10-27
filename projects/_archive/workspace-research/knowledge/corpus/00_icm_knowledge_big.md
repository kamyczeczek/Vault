---
type: Concept
id: 00_icm_knowledge_big
title: "ICM_knowledge.md (part 1/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# ICM_knowledge.md

Merged notes — part 1 of the collection.

------

Jake's content\Building Your Stack\1.1 Starting the Build Process.md

What You'll Get From This

A framework for deciding whether to build a custom UI and how to scope it before writing any code.

------

Before You Build Anything: The Tool Ladder

This methodology works at different levels. You don't always need to build custom.

Level 1: Claude Projects (

http://claude.ai/

Use project instructions and knowledge files. Upload your

http://claude.md/

, your context docs, your templates. Claude reads them at the start of every conversation. No code required.

Level 2: Claude Cowork (in-app)

More control, still inside Anthropic's interface. Good for workflows that need more than chat but don't require full file system access.

Level 3: VS Code + Claude Code

Full readability. Quick navigation. You see your folders, your files, your code. Claude operates inside your actual workspace. This is where most people should land.

Level 4: Custom Front-End

Build your own interface around Claude Code. Full control. Designed specifically for your workflow.

#### Each level adds complexity. Each level adds capability. But here's the thing:

Anthropic keeps improving their native UI.

Features that required custom builds a year ago now exist in the default interface. Projects didn't exist. Cowork didn't exist. By the time you finish building a custom front-end, Anthropic might ship something that does the same thing.

#### The philosophy for this course:

know HOW to build custom, so you can when you need to. But always ask whether you need to. The best tool is the simplest one that solves your problem.

------

What This Course Is

This isn't a step-by-step tutorial. This is a behind-the-scenes project.

I'm building a custom front-end for my animation workflow. You're watching me do it. Every decision, every mistake, every time Claude does something unexpected.

The lessons in this course are session recordings with written companions that explain what's happening and why. You'll see:

How I research what already exists before building

How I write a PRD (product requirements document) so Claude knows what we're making

How I set up the workspace so Claude has context

How Claude Code uses plan mode and sub-agents

What happens when things break

How the project evolves session by session

This is the highest-skill content in the community. If some of it feels over your head, that's fine. Watch it anyway. You'll understand more than you think, and the parts that don't click now will click later.

------

The Project: A Control Surface for My Workflow

Here's what I'm building and why.

I have a workflow for turning scripts into animations. It lives in folders. Script Lab holds my scripts. Animation Studio turns them into specs, then builds, then renders. The whole thing runs on Claude Code.

#### VS Code works fine for this. But I want something better. I want:
