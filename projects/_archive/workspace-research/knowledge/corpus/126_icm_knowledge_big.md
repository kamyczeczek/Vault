---
type: Concept
id: 126_icm_knowledge_big
title: "ICM_knowledge.md (part 127/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

— The actual codebase. The CONTEXT.md here describes the code structure, naming conventions, patterns you use (and patterns you avoid), testing requirements, and any libraries or frameworks that are standard in the project. Claude writes code that fits your codebase because it read the rules first.

— API documentation, user guides, changelogs. The CONTEXT.md describes your documentation standards, the audience for each type of doc, and how docs relate to the code.

— Deployment, monitoring, operational scripts. The CONTEXT.md describes your infrastructure, deploy process, and any runbook conventions.

#### What the CLAUDE.md looks like:

# My App

[APP NAME] — [One sentence description]

## Tech Stack

\-    Frontend: [framework]

\-    Backend: [language/framework]

\-    Database: [type]

\-    Deploy: [platform]

## Workspaces

\-    /planning — Specs, architecture, decisions

\-    /src — Application code

\-    /docs — Documentation

\-    /ops — Deployment and operations

## Routing

| **Task**        | **Go to** | **Read**   | **Skills**          |
| --------------- | --------- | ---------- | ------------------- |
| Spec a feature  | /planning | CONTEXT.md | —                   |
| Write code      | /src      | CONTEXT.md | testing-skill       |
| Write docs      | /docs     | CONTEXT.md | doc-authoring-skill |
| Deploy or debug | /ops      | CONTEXT.md | —                   |

## Naming conventions

\-    Specs: feature-name_spec.md

\-    Components: PascalCase

\-    Tests: feature-name.test.ts

\-    Decision records: YYYY-MM-DD-decision-title.md

Developers will notice the routing table has a Skills column. This is Layer 3 from 3.1. You can wire testing skills, documentation skills, or code review skills into specific workspaces so they only load when relevant. Your planning workspace does not need the testing skill. Your src workspace does

------

How to build yours

You do not need to match any of these exactly. The process is the same regardless of what you do.

Step 1: List your workspaces.

Think about the 2-4 major areas of your work. What are the modes you shift between? Writing and building are different workspaces. Client A and Client B are different workspaces. Planning and executing might be different workspaces. If you find yourself wishing Claude would "forget" what it was just doing and focus on something else, that is a workspace boundary.

Step 2: Write a CONTEXT.md for each one.

Describe what happens in this workspace, what the process is, what files live here, and what good work looks like. Keep it under a page. You can always add more later.

Step 3: Write your CLAUDE.md.

List the workspaces and build the routing table. For each type of task, tell Claude where to go and what to read. Add naming conventions so Claude knows how to organize files.

Step 4: Start working.
