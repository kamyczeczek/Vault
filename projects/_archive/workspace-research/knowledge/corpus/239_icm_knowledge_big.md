---
type: Concept
id: 239_icm_knowledge_big
title: "ICM_knowledge.md (part 240/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

| **Entry format**                      | **Action**                                                   |
| ------------------------------------- | ------------------------------------------------------------ |
| Loose bullet with no `#short-id` tag  | Skip — leave in place                                        |
| Single bullet tagged `#short-id`      | Append to `[project]-ideas.md`                               |
| `#short-id` block (multiple bullets)  | Append each bullet to that project's ideas file              |
| Category + `#short-id` block          | Append as grouped entry with category label preserved        |
| `[short-id]-[category]` compound tag  | Create new row in PROJECTS.md ## Seed and add to ##  Short-Ids |
| `## Project-name` header with bullets | Seed new project at Seed stage, create  `[project]-ideas.md` |
| `## Project-name` header, no bullets  | Create Idea stage row in PROJECTS.md only (no directory)     |
| `## Project-name` already exists      | Abort with message: "project already exists — use  tagged bullets instead" |

------

## Short-Ids Section

\-    Maintained by Claude at the top of `ideas.md`.

\-    Auto-updated when projects are created or removed.

\-    Read-only for the user — Claude manages this list.

------

## Naming

\-    Project names are lowercase-hyphenated: `my-project`

\-    Format in PROJECTS.md: `my-project — brief description`

------

## After Processing

Report what was routed where. Leave untagged loose bullets in place — they are not ready to be assigned yet.

------

FILE: ProjectOS/[Q5-project-name]/[Q5-project-name]-ideas.md

Derive one open question about this project from Q5's description.

# [project name] Ideas

\-    [open question derived from Q5 description]

------

FILE: ProjectOS/[Q5-project-name]/[Q5-project-name]-tasks.md

# [project name] Tasks

| **ID**  | **Task**                                 | **Energy** | **Priority** | **Status** | **Notes** |
| ------- | ---------------------------------------- | ---------- | ------------ | ---------- | --------- |
| [Q6]-01 | Define initial scope and first milestone | Med        | P2           | Open       | Seed task |

------

FILE: ProjectOS/[Q5-project-name]/[Q5-project-name]-resources.md

# [project name] Resources

| **Title** | **Description** | **Path** |
| --------- | --------------- | -------- |
|           |                 |          |

------

Step 4: Finalize

#### If Q5 was answered, tell the user:

"[Q7], your TaskSystem is live.

'give me today'

— get your focus list (I'll ask your energy level)

'add task: [description]'

— add something to the board

'process ideas'

— route anything in ideas.md to your projects

You have [N] recurring tasks and one active project: [Q5 name].

Type 'give me today' to start."

#### If Q5 was skipped, tell the user:

"[Q7], your TaskSystem is live.

'give me today'

— get your focus list (I'll ask your energy level)

'add task: [description]'

— add something to the board
