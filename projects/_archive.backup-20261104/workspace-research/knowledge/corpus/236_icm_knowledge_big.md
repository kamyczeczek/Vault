---
type: Concept
id: 236_icm_knowledge_big
title: "ICM_knowledge.md (part 237/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

1. Read TASKS.md fresh.
2. Ask energy level if not     stated: High / Med / Low.
3. Select 2–3 tasks matched     to energy level and deadlines.
4. Apply deadline override:     P1 tasks and tasks due within 3 days always appear regardless of energy.
5. Include Recurring     Reminders — flag overdue or due-soon recurring tasks.
6. Include Deadline     Pressure section — all P1 tasks visible even on Low days.
7. Write to FOCUS.md at     root.

### FOCUS.md Format

\```

# FOCUS — [Date] ([Day])

*Energy: [High/Med/Low]*

## Today's Picks ([energy] energy)

| **#** | **Task** | **Energy** | **Why** |
| ----- | -------- | ---------- | ------- |
|       |          |            |         |

## This Week — Action Required

[P1 tasks and tasks due within 7 days]

## Deadline Pressure (visible even on Low days)

[All P1 tasks with deadlines]

## Recurring Reminders

[Overdue or due-soon recurring tasks]

## Standing Awareness

[Short bullets: key context, deadlines, blockers] ```

------

## Task Updates

When a task is reported (new, complete, or status change):

1. Update TASKS.md     immediately using the Next ID counter.
2. When marking done: move     the row to archive/done.md under the current month.
3. For recurring tasks:     update `Last Done` date only — never archive recurring rows.
4. Bump the Next ID counter     in the TASKS.md header after adding a task.

------

## Recurring Tasks

\-    Live in the Recurring section of TASKS.md.

\-    Check cadence when generating FOCUS.md — surface tasks overdue or due within 2 days.

\-    Never archive recurring rows; only update `Last Done`.

------

## Retrospective

Trigger: "Sunday check-in" or "retrospective."

1. Read TASKS.md and     ENERGY_LOG.md.
2. Summarize: what was     completed, what slipped, energy patterns observed.
3. Identify one pattern and     one suggested adjustment.
4. Write to     TaskOS/RETROSPECTIVES.md under the current week's date.

------

## Energy Pattern

[Q2 answer — verbatim or lightly cleaned up]

Typical session start: [Q3].

------

## Priority Key

\-    **P1** — This week or deadline-critical

\-    **P2** — Important, 2–4 week horizon

\-    **P3** — Backlog / someday

## Energy Key

\-    **High** — Requires creativity or decisions

\-    **Med** — Structured output with clear direction

\-    **Low** — Admin, routine, light reading, logistics

------

FILE: TaskOS/ENERGY_LOG.md

# Energy Log

*Updated by Claude when energy level is reported at session start.*

------

## Log

| **Date** | **Energy** | **Notes** |
| -------- | ---------- | --------- |
|          |            |           |

------

FILE: TaskOS/RETROSPECTIVES.md

# Retrospectives

*Written by Claude on "Sunday check-in" or "retrospective" command. One entry per week.*

------

FILE: TaskOS/archive/done.md

# Archive — Completed Tasks

*Managed by Claude. Tasks are moved here when marked done, organized by month.*

------

FILE: ProjectOS/CONTEXT.md

# ProjectOS — Context
