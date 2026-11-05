---
type: Concept
id: 04_icm_knowledge_big
title: "ICM_knowledge.md (part 5/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

\-    Most of the front-end complexity from those repos. I don't need all their features. I need a clean, minimal interface.

#### What I actually want:

A workflow map on the left (visual, like a mind map, not just folders)

A file editor in the middle

Claude Code chat on the right

Ability to open multiple chats

Ability to collapse panels

Clean, minimal design

\-    What to build first (get something working) vs. what to add later (polish and features).

\-    Clone the repos, strip away what I don't need, implement the front-end basics, then add the workflow visualization.

All of this goes into a markdown file. That file lives in the workspace. Claude reads it at the start of every session.

------

Why a PRD Matters

If I just told Claude "build me a front-end for my workflow," it would build something. It probably wouldn't be right.

#### The PRD does three things:

1. Forces decisions before     code

What features do I actually want? What's out of scope? Easier to edit a document than refactor built code.

1. Creates persistent     context

Claude Code reads the PRD every time I start a session. It knows where we are in the project. It knows what we're building. I don't have to re-explain.

1. Allows auditing

If you're not sure about the technical choices, you can feed the PRD into another Claude session and ask it to review. "What's overcomplicated? What's missing? What would you simplify?"

------

The PRD Prompt

#### Here's roughly what I asked:

Make a PRD markdown of this for Claude Code (as in, Claude Code will read it to build the project).

Describe what we are trying to do and break down steps and structure for early phase to late phase.

#### I included:

The repos I wanted to reference

My existing folder structure (my

http://claude.md/

What I wanted the front-end to do

What I wanted to cut from the existing repos

Claude generated a document. I read through it, edited the parts that weren't right, and saved it to my workspace.

------

Building Inside the Workspace

Here's a detail that matters: I'm building this front-end inside my Animation Studio workspace, not in a separate folder.

Why? Because that workspace already has all my context. The folder structure. The processes. The

http://claude.md/

that describes how everything works.

If I built in a separate folder, Claude would have to fetch context from somewhere else. By building inside the workspace, Claude can reference my actual workflow while building the tool that wraps around it.

I created a new folder called "front-end" inside my existing workspace. The PRD goes there. The code will go there. But Claude can still see the animation pipeline it's building an interface for.

------

What Comes Next

Once the PRD is set, the actual build starts. That's

https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=fdb1ae130aec49d28eba9142efb5762f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### You'll see:
