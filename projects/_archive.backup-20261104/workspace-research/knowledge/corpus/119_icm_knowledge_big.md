---
type: Concept
id: 119_icm_knowledge_big
title: "ICM_knowledge.md (part 120/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

What files are in here and how they are organized

What skills or tools to use in this workspace

You can write these by hand or have Claude help you write them. They are plain English. Short documents. A few paragraphs.

In the video, you can see what happens with almost no prompting at all. You say "go to writing room, let's start making something" and the AI immediately reads the context file, understands the workspace, loads the right voice and style, and asks what you want to build. One prompt. That is the power of Layer 2.

Layer 3: The Tools (Skills, MCP Servers, and Plug-and-Play)

Layer 3 is where skills and tools live. Skills are processes that someone figured out and packaged into a set of files that tell Claude how to do a specific thing. A PowerPoint skill. A humanizer skill. A doc co-authoring skill.

The key here: you do not load every skill into every workspace. You wire skills into the workspaces where they are needed. Your Production workspace might reference a front-end design skill and a web app testing skill. Your Writing Room might reference a humanizer skill and a doc co-authoring skill.

You can reference 15, 20, or 100 skills in a project, but each workspace only loads the ones it needs. That is the plug-and-play idea. And if you need Claude to find a new skill or create one, you can wire that ability in too.

------

Naming conventions that replace databases

One more thing that makes this system work without any code or databases. In your CLAUDE.md, you add naming conventions.

#### If a blog draft is created, it gets named like:

api-auth-guide_draft.md

#### If it is a newsletter, it gets named like:

2026-03-launch-week.md

#### If it is a demo script version 2, it gets named like:

The AI knows how to find, organize, and move files because the naming tells it everything. You can say "pull my demo v2 and build a spec from it" and Claude knows exactly where to look, what to pull, and what to do next. No SQL. No vector database. No Python injection. Just naming conventions.

------

How to make this yours

The template in the video uses a fake project with fake blog posts and demo scripts. That is intentional. You swap the names and rewrite the context files for your own work. The layers stay the same.

#### If you are a content creator:

Writing Room → Script Lab

Production → Edit Bay

Community → Distribution Hub

#### If you are a freelancer:

Swap workspaces for: Client Intake, Delivery, Admin

Your context files describe your client process instead of content production

#### If you are a developer:

Swap workspaces for: Frontend, Backend, Docs

Wire in the skills you actually use (testing, deployment, code review)

The three-layer routing system (map → rooms → tools) works the same way no matter what you do. You change the labels and the context. The architecture holds.

------

The research behind this
