---
type: Concept
id: 167_icm_knowledge_big
title: "ICM_knowledge.md (part 168/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Embeddable anywhere. The core is a small, zero-dependency engine, so it doesn't have to live in a terminal. Picture an Obsidian plugin that versions your vault with attribution and time travel, and the same for Logseq, VS Code, or Zed.

Where it's headed, and how to get in

Today GiTeam is a repo-level safety net for AI: everything that happens to your code, recorded, attributed, reversible. The longer plan reaches past a single repo, toward a safety net for your whole machine, repos you can mount like drives, and that engine living inside the tools you already use.

It's an internal tool right now, and we dogfood it daily, bugs and all. If this resonates and you'd want to kick the tires, we'd like to talk about alpha testing.

That's GiTeam.

------

Uncategorized\Vibe-Coding Masterclass in 30 Minutes Flat.md

Introduction

Speaker: Boris, Member of Technical Staff at Anthropic

Creator of "Quad Code" (Claude Code)

Focus: practical tips and tricks

What is Quad Code?

New kind of AI assistant for coding

Agentic: builds features, entire functions, files, fixes bugs

Works with all IDEs & environments: VS Code, Xcode, JetBrains, Vim, terminal, SSH, tmux

No indexing, code stays local

Getting Started

Environment setup

Terminal setup: shift+enter for new lines

Theme: light/dark/daltonize

#### GitHub app:

/install github app

Customize allowed tools to reduce prompts

Dictation (Mac accessibility): speak prompts

Recommended first use: Codebase Q&A

Ask questions about the codebase

Onboarding: reduced from 2–3 weeks to 2–3 days

"How is this class used?" (finds deep examples)

"Explain git history of this function/arguments" (summarizes commits, issues)

Fetch GitHub issues via web

"What did I ship this week?" (standup summary)

Editing Code

Tools: edit files, run bash, search files

Agent strings them together automatically

Workflow tips

Plan first: "Before you write code, make a plan"

Ask for approval before writing

"commit push": auto branch, commit, PR

Advanced workflows

Let it check its work (unit tests, screenshots via Puppeteer/iOS simulator)

Iterate 2–3 times → near-perfect results

Integrating Your Tools

Two types: bash tools, MCP tools

Teach Claude: use

, add MCP servers in config

Share tools via project config (e.g., Puppeteer MCP for end-to-end tests)

Providing Context

Project root (shared, checked in): common commands, style guide, architecture, core files – keep short

Local (personal, not checked in)

Nested directories (auto-pulled on demand)

Enterprise route (company-wide)

Slash commands (

): automate tasks (e.g., label GitHub issues)

@mention files to pull into context

Context hierarchy: project → global → enterprise policies

Auto-approve/block commands, manage MCP servers

#### Manage context:

/slashmemory

, pound sign (

) to remember

Key Bindings & Tips

Shift+Tab: auto-accept edits (bash still requires approval)

: remember something into CLAUDE.md

: drop to bash (output in context)
