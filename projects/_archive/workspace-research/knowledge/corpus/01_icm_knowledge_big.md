---
type: Concept
id: 01_icm_knowledge_big
title: "ICM_knowledge.md (part 2/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

A visual workflow map instead of just folders

A file editor in the middle

Claude Code chat on the right

The ability to switch between "I'm driving" and "Claude's driving"

That last one is the key insight. Sometimes I want to edit every individual file. Sometimes I want to automate the whole thing and trust Claude to run the pipeline. A good control surface lets me switch between those modes fluidly.

------

Why Not Just Use Existing Repos?

There are open-source projects that do parts of this. Claude CLI interfaces. Claude Code web UIs. Tools for session persistence and usage tracking.

I looked at them. They're good, but they're not MY workflow. They have features I don't need. They're missing features I want. They don't map to how I actually work.

#### So instead of using them directly, I'm doing this:

Study what they built

Pull the parts that work

Strip away everything I don't need

Build around my existing folder structure

Don't reinvent the wheel. Make a better wheel. Make the wheel yours.

------

The PRD Approach

Before any code gets written, I have Claude create a PRD.

PRD = Product Requirements Document

#### The PRD describes:

What we're building

What existing repos we're pulling from

What stacks those repos use

What I want to keep and what I want to cut

The phases from start to finish

This becomes a markdown file that lives in the workspace. Claude Code reads it at the start of every session. It's persistent context. Stateful prompting.

Why markdown? Because markdown files are small (low token cost), easy for Claude to read, and I can edit them in any text editor. If I want to format them later, I can upload to Google Docs and it converts automatically.

------

#### What the Lessons Cover

1.2: How I Use Claude Code in the Build Process

The initial thinking. David's question that started this. Researching existing repos. Creating the PRD. Setting up the workspace inside my actual project folder so Claude has context.

1.3: Building the Front End (Session 1)

Watching Claude work. Plan mode vs execution mode. Sub-agents that fetch repos and study workspace structure. What happens when Claude makes better decisions than what I told it to do.

1.4: [Coming Soon]

More build sessions as the project continues. This is an ongoing build. New lessons drop as I finish sections.

------

The Build Process Framework

Whether you follow along with my project or build something completely different, the process is the same:

1. Define what you actually     need

Not what sounds cool. What workflow pain are you solving? Can you solve it at Level 1, 2, or 3 instead of Level 4?

1. Research what exists

What repos already do part of this? What can you borrow? What's worth building vs. taking?

1. Map your existing     structure

What folder architecture are you building around? Give Claude your

http://claude.md/

. Let the front-end wrap around what you already have.

1. Write a PRD
