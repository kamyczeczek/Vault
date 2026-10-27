---
type: Concept
id: 234_icm_knowledge_big
title: "ICM_knowledge.md (part 235/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

| **When asked about**                         | **Directory** | **Read first**             |
| -------------------------------------------- | ------------- | -------------------------- |
| Tasks, today's focus, energy, prioritization | /TaskOS       | CONTEXT.md                 |
| Projects, ideas, project lifecycle           | /ProjectOS    | CONTEXT.md                 |
| "process ideas"                              | /ProjectOS    | _rules/ideas-processing.md |

------

## Key Files

| **File**              | **What it is**                                           |
| --------------------- | -------------------------------------------------------- |
| TASKS.md              | Master task board — Claude-managed, never edit directly  |
| FOCUS.md              | Session-generated focus list — auto, never edit manually |
| ideas.md              | Capture inbox — process with "process ideas"             |
| ProjectOS/PROJECTS.md | Master project index — Claude-managed                    |

------

## Commands

| **Say this**                         | **What happens**                                        |
| ------------------------------------ | ------------------------------------------------------- |
| `give me today` / `what's my focus`  | Generate FOCUS.md — Claude asks energy level if unknown |
| `refresh focus`                      | Regenerate FOCUS.md mid-session                         |
| `[task ID] done` / `[task] complete` | Claude archives the task                                |
| `add task: [description]`            | Claude adds task to TASKS.md                            |
| `Sunday check-in` / `retrospective`  | Weekly review written to TaskOS/RETROSPECTIVES.md       |
| `process ideas`                      | Route ideas.md entries to project files                 |
| `seed project [name]`                | Create new project at Seed stage in ProjectOS           |

------

## Rules

\-    Read this file first, then the relevant CONTEXT.md before starting any task.

\-    Never edit TASKS.md or PROJECTS.md directly — report changes in chat, Claude updates.

\-    FOCUS.md and ideas.md live at root.

\-    Check in before writing in all cases. Propose structure first, wait for confirmation.

\-    Ask before creating files outside designated project directories.

------

FILE: TASKS.md

Build the Recurring section from Q4 answers — one row per task, IDs R01, R02, etc. Infer Energy level from the task type. Leave Last Done blank. Set Next R-ID to one above the last ID used.

# Task Board

*Managed by Claude. Last updated: [today's date].* *To add a task: tell Claude in chat. To update: report what changed. Never edit this file directly.* *Next ID: T02 · Next R-ID: [next R-ID]*

------

## Priority Key

\-    **P1** — This week or deadline-critical

\-    **P2** — Important, 2–4 week horizon

\-    **P3** — Backlog / someday

## Energy Key

\-    **High** — Requires creativity, decisions, or drafting
