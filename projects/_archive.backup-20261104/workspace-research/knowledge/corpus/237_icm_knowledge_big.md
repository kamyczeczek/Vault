---
type: Concept
id: 237_icm_knowledge_big
title: "ICM_knowledge.md (part 238/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

ProjectOS manages long-term project lifecycle alongside TaskOS. Claude manages PROJECTS.md and all project child files.

------

## Files

| **File**                         | **Purpose**                                    |
| -------------------------------- | ---------------------------------------------- |
| PROJECTS.md                      | Master project index — single source of truth  |
| _rules/schemas.md                | Schema for project child files                 |
| _rules/ideas-processing.md       | Rules for routing ideas.md entries to projects |
| [project]/[project]-ideas.md     | Project-scoped ideas and open questions        |
| [project]/[project]-tasks.md     | Project-scoped task backlog                    |
| [project]/[project]-resources.md | Links and reference materials                  |

------

## Project Status Stages

| **Stage** | **Meaning**               | **Has directory?**    |
| --------- | ------------------------- | --------------------- |
| Idea      | Name captured only        | No                    |
| Seed      | Ideas being collected     | ideas.md only         |
| Scoped    | Task backlog defined      | All three child files |
| Active    | Currently being worked    | All three child files |
| Paused    | Stopped, intent to resume | All three child files |

------

## PROJECTS.md Schema

Sections in order: `## Active`, `## Scoped`, `## Seed`, `## Idea`, `## Paused`

Each section (except Idea) is a table with columns: Name, Description, Short-IDs, Dir

Idea stage has no Dir column.

------

## Transitions

| **Command**             | **Action**                                                |
| ----------------------- | --------------------------------------------------------- |
| "seed project [name]"   | Create [project]-ideas.md, add row to ## Seed             |
| "scope project [name]"  | Create -tasks.md and -resources.md, move row to ## Scoped |
| First task marked done  | Move row to ## Active                                     |
| "pause project [name]"  | Move row to ## Paused                                     |
| "resume project [name]" | Move row back to ## Active                                |

------

## Protocols

**Adding an idea to a project:** Append bullet to [project]-ideas.md. Do not restructure existing content.

**Adding a task to a project:** Append row to [project]-tasks.md. Use scoped ID format: [short-id]-01, -02, etc.

**Adding a resource:** Append row to [project]-resources.md.

**Reading active projects:** Load PROJECTS.md ## Active section only. For detailed work, load the project's child files.

**Unified work query:** Combine TASKS.md and active project task files, filter by Energy column matching current session energy.

------

## Stable Interface

TaskOS unified work query reads only the `## Active` section from PROJECTS.md. Do not restructure that section header.

------

FILE: ProjectOS/PROJECTS.md

# Projects

## Active
