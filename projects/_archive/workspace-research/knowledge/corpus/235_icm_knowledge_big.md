---
type: Concept
id: 235_icm_knowledge_big
title: "ICM_knowledge.md (part 236/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

\-    **Med** — Structured output with clear direction

\-    **Low** — Admin, routine, light reading, logistics

------

## Active

| **ID** | **Task**                       | **Category**        | **Deadline** | **Energy** | **Priority** | **Status** | **Notes**                                  |
| ------ | ------------------------------ | ------------------- | ------------ | ---------- | ------------ | ---------- | ------------------------------------------ |
| T01    | Define scope for first project | [first Q1 category] | —            | Med        | P2           | Open       | Seed task — complete or replace when ready |

------

## Recurring

*One row per recurring task. Update `Last Done` on completion — never archive these rows.*

| **ID** | **Task** | **Cadence** | **Last Done** | **Energy** | **Notes** |
| ------ | -------- | ----------- | ------------- | ---------- | --------- |
|        |          |             |               |            |           |

------

## Creative / Outlet

| **ID** | **Task** | **Category** | **Notes** |
| ------ | -------- | ------------ | --------- |
|        |          |              |           |

------

## Energy Restorers

*For unexpected free time. These recharge rather than drain.*

| **Activity** | **Best time** | **Why it works** |
| ------------ | ------------- | ---------------- |
|              |               |                  |

------

## Flags

*(none)*

------

FILE: ideas.md

Derive one open question or seed idea about the project from Q5's description. Write it as a bullet under the project's short-ID. If Q5 was skipped, use

example idea

as the bullet.

# Ideas

## Short-Ids

[Q6]

\-    [open question about Q5 project derived from its description]

------

FILE: TaskOS/CONTEXT.md

The FOCUS.md Format section inside this template uses ``` fences — the outer template uses ~~~ to prevent nesting conflicts.

# TaskOS — Context

TaskOS is the daily task management and focus system. Claude manages all files in this directory.

------

## Files

| **File**          | **Purpose**                                          |
| ----------------- | ---------------------------------------------------- |
| TASKS.md (root)   | Master task board — single source of truth           |
| archive/done.md   | Completed tasks, organized by month                  |
| ENERGY_LOG.md     | Daily energy level log                               |
| RETROSPECTIVES.md | Weekly retrospective summaries                       |
| FOCUS.md (root)   | Session-cache derived from TASKS.md — auto-generated |

------

## Generating FOCUS.md

Trigger: session start, "give me today", "what's my focus", or "refresh focus."
