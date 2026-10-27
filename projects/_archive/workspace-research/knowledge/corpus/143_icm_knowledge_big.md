---
type: Concept
id: 143_icm_knowledge_big
title: "ICM_knowledge.md (part 144/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

— Things Claude should not do. Libraries you do not use. Patterns you have moved away from.

------

Example CLAUDE.md

# My Web App

React 18 + Express + PostgreSQL + TypeScript

## Commands

npm run dev | npm run api | npm test

## Conventions

Functional components only. Routes in src/api/. All database queries go through src/db/queries/.

## Avoid

No class components. Don't modify db/migrations directly. Don't use Moment.js (we use date-fns).

That is it. Fifteen lines. Ten minutes. The difference in Claude's behavior is immediate.

------

Write it for a smart person who just joined your project.

That is literally what Claude is. If a new team member would need to know it on day one, put it in the CLAUDE.md.

Update it when your project changes.

The CLAUDE.md is a living document. When you add a new convention, change a library, or shift your architecture, update the file. This is the same advice from

3.3 (Common Mistakes)

: stale context files are the most common reason Claude starts "getting worse."

Do not overthink it.

A mediocre CLAUDE.md beats no CLAUDE.md every time. You can always improve it later. The first version takes 10 minutes. Each edit takes 30 seconds. Start now.

This is not just for code projects.

If your project is a folder full of documents, the CLAUDE.md describes what those documents are, how they are organized, and what you are using them for. The same principle applies to any structured folder, whether it contains code, writing, research, or client files.

------

Write your CLAUDE.md

Do this now.

Pick a project. Work project, side project, or even a document folder.

Create a file called

in the root of the folder.

#### Fill it in using the template:

# [Project Name]

## Overview

[2-3 sentences. What is this? What does it do?]

## Tech Stack

[Languages, frameworks, tools. Or "document types" if not a code project.]

## Commands

[Dev, test, build. Or "how to use these files" if not code.]

## Conventions

[Patterns, naming, structure.]

## Avoid

[Things Claude should not do.]

Save it. Open Claude Code in the folder. Run a task.

(Optional) Temporarily move the CLAUDE.md out of the folder. Run the same task. Compare the outputs. Move it back.

The comparison is what makes the value click. You will not go back.

------

The CLAUDE.md is a project-specific version of the identity file from

1.2: Your First Folder

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

. If you want to understand the full three-layer architecture (identity → workspace context → skills), go to

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

Common mistakes with context files (too long, too focused on personality, never updated) are covered in
