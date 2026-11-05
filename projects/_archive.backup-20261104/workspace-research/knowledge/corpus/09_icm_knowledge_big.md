---
type: Concept
id: 09_icm_knowledge_big
title: "ICM_knowledge.md (part 10/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Improve on existing tools

(Claude CLI, Claude Code Web, Opcode)

Too complex / not fitting personal workflow

Extract good ideas, discard clutter

📋 The PRD (Product Requirements Document)

Single source of truth for Claude Code

Describe full vision, constraints, references

Break work into phases, avoid building everything at once

Reference to GitHub repos (stacks, liked features, unwanted features)

Visual layout specs (workflow map, editor, chat panel)

Pipeline definitions (JavaScript mapping actual folder structure)

#### Step-by-step instructions:

Clone and analyze repos

Strip unwanted features

Add session persistence (like VS Code extension)

Implement front-end

Implement visual workflow (hardest)

Why PRD first?

Editable markdown, easy for Claude to read

Avoids Claude rushing into code

Acts as persistent, non‑stateless prompt (can be reused across sessions)

🖥️ Desired UI & Features

Three-panel layout

Workflow Map

(node-based, mind‑map style)

File Editor

Claude Chat Panel

(multiple collapsible chats)

Workflow Map

Visual representation of folder structure and animation pipeline

Click nodes to navigate, edit, or trigger actions

Moves from Script Lab → Animation Studio → Specs → Renders

Interaction model

“Fluid switch between me driving or Claude driving”

Sometimes manual edit, sometimes full automation

Trust that automation follows the defined workflow

🔧 Technical Strategy

Don’t reinvent the wheel

Clone existing open‑source repos (Claude Code Web, Opcode)

Strip down to essentials, keep the “good parts”

Reuse session persistence, chat infrastructure

JavaScript (pipeline definitions), potentially React

All built within the existing workspace context

Leverage Claude’s own infrastructure (no separate app)

Implementation phases

(from PRD):

Download & analyze reference repos (web fetches, not full clones)

Remove unwanted UI elements, keep backend connections

Integrate workflow map (hardest part)

Final polish and modularity

⚙️ Current Execution (Live Session)

Using Claude Code in plan mode

Claude reads the PRD markdown, confirms understanding

Creates sub‑agents to save tokens (inspect workspace, fetch data)

Actions observed

commands to examine folder structure

Web fetches pulling specific files from reference repos (package.json, etc.)

Sending secondary agents for parallel tasks

Workspace is key

All work done inside the actual project folder

Gives Claude direct context without uploading files repeatedly

Context only pulled when instructed (not everything at once)

📚 Core Concepts Explained

Stateless vs Persistent Prompts

Normal chat: stateless, context lost after session

Markdown PRD: persistent file, can be re‑read, edited, and reused

Markdown advantages

Low token cost, highly structured

Easy for AI to parse, easy to export (Google Docs, etc.)

Will be used directly in the front‑end

Bash commands

: Claude uses terminal commands to explore workspace
