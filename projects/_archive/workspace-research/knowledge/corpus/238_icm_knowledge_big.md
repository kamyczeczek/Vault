---
type: Concept
id: 238_icm_knowledge_big
title: "ICM_knowledge.md (part 239/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

| **Name**          | **Description**  | **Short-IDs** | **Dir**    |
| ----------------- | ---------------- | ------------- | ---------- |
| [Q5 project name] | [Q5 description] | [Q6]          | [Q5-name]/ |

## Scoped

| **Name** | **Description** | **Short-IDs** | **Dir** |
| -------- | --------------- | ------------- | ------- |
|          |                 |               |         |

## Seed

| **Name** | **Description** | **Short-IDs** | **Dir** |
| -------- | --------------- | ------------- | ------- |
|          |                 |               |         |

## Idea

| **Name** | **Description** | **Short-IDs** |
| -------- | --------------- | ------------- |
|          |                 |               |

## Paused

| **Name** | **Description** | **Short-IDs** | **Dir** |
| -------- | --------------- | ------------- | ------- |
|          |                 |               |         |

------

FILE: ProjectOS/_rules/schemas.md

This file contains nested code blocks — the outer template uses ~~~ to prevent nesting conflicts.

# ProjectOS — Schemas

Read this file before creating or writing to any project child file (`[project]-ideas.md`, `[project]-tasks.md`, `[project]-resources.md`).

------

## [project]-ideas.md

\```

# [project] Ideas

\-    single idea

category

\-    grouped idea 1

\-    grouped idea 2 ```

Idea groups use a plain-text label on its own line (no `#`, no markdown heading) followed by a bullet list.

------

## [project]-tasks.md

\```

# [project] Tasks

| **ID**  | **Task**         | **Energy** | **Priority** | **Status** | **Notes** |
| ------- | ---------------- | ---------- | ------------ | ---------- | --------- |
| proj-01 | task description | Low        | P2           | Open       | —         |
| ```     |                  |            |              |            |           |

Energy: High / Med / Low. Priority: P1 / P2 / P3. Status: Open / Done. Task IDs use scoped prefix: `[short-id]-01`, `[short-id]-02`, etc., incrementing.

------

## [project]-resources.md

\```

# [project] Resources

| **Title** | **Description** | **Path**         |
| --------- | --------------- | ---------------- |
| Label     | What it is      | url or file path |
| ```       |                 |                  |

------

FILE: ProjectOS/_rules/ideas-processing.md

# Ideas Processing Rules

Run these rules when the user says "process ideas."

Source file: `ideas.md` at the root of your TaskSystem directory.

------

## Entry Types
