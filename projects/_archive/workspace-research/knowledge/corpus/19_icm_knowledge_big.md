---
type: Concept
id: 19_icm_knowledge_big
title: "ICM_knowledge.md (part 20/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

But sessions end. Your terminal closes. You hit token limits. Your laptop restarts. The Remote Control session dies.

When you start a new session, Claude doesn't remember the old one. You're starting fresh.

This lesson is about the second kind of persistence: making sure YOU don't lose context even when Claude does.

------

The Problem

Claude doesn't remember between sessions.

You have a productive session. You make real progress. The session ends. You start a new one the next day. Claude has no idea what you were working on.

You can re-explain. But that's slow and you'll miss details.

Or you can put the context in files that persist.

------

The Solution: Workspace as Memory

Claude's memory doesn't persist. But your files do.

#### Everything Claude needs to know should live in your workspace:

The PRD that describes the project

http://claude.md/

that maps the folder structure

The progress notes that track what's been done

The specs, the code, the outputs

#### When you start a new session, you tell Claude:

Read the PRD and CLAUDE.md. Look at what's been built. Tell me where we are.

Claude reads the files. Claude knows where you are. The workspace becomes the memory.

------

What to Persist

#### Not everything needs to be saved. Here's what matters:

Project definition (always persist)

The PRD or project spec

http://claude.md/

or context file

The folder structure itself

This is the "what are we building" layer. It exists before you start and stays consistent throughout.

Progress markers (persist regularly)

PROGRESS.md

http://progress.md/

http://status.md/

Notes on what's done, what's in progress, what's blocked

Updated after significant milestones

This is the "where are we" layer. Update it when something meaningful changes.

Session notes (persist when important)

Key decisions made during a session

Reasons for specific choices

Things to remember for later

This is the "why did we do that" layer. You don't need to log everything, but log what you'd be frustrated to forget.

------

#### Keep a simple progress file at the root of each project:

# Progress

## Current Status

Building the panel layout. Workflow map is next.

## Last Session (2024-01-15)

\-    Completed: Basic server setup, connection to Claude Code CLI

\-    In Progress: Panel components

\-    Blocked: None

\-    Next: Add collapse/expand for panels

## Decisions Made

\-    Using React instead of Vue (faster for our timeline)

\-    Skipping dark mode for v1 (add later)

\-    Panel order: workflow left, editor middle, chat right

## Open Questions

\-    How to handle multiple simultaneous chats?

\-    Should workflow map be tree or graph?

#### At the start of each session:

Read PROGRESS.md. What's the status? What should we work on next?

#### At the end of each session:

Update PROGRESS.md with what we accomplished and what's next.

This takes 30 seconds and saves you 10 minutes of re-orienting next time.

------

When to Update
