---
type: Concept
id: 10_icm_knowledge_big
title: "ICM_knowledge.md (part 11/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

: Claude delegates tasks to smaller agents to manage token limits

🎓 Future Content & Teaching

This session

Free, informal “live stream” style walkthrough

Shows real daily workflow

Upcoming courses

Structured, college‑level with workbooks

Deep dives into: JavaScript, Python, Git, GitHub, reading PRDs

Paid content will be separate, more comprehensive

: Break every concept into digestible pieces for all skill levels

------

Jake's content\Building Your Stack\1.4 Repo Tour Open Source References.md

What You'll Get From This

A curated list of open-source AI UI projects worth studying, with notes on what to learn from each.

------

How to Use This Page

This isn't a tutorial. It's a research resource.

Each repo below does something interesting with AI interfaces. Some wrap Claude Code. Some build custom chat UIs. Some solve problems you haven't thought of yet.

#### For each one, I've noted:

What it does

What's worth studying

What you might borrow for your own builds

You don't need to clone all of these. Pick the ones relevant to what you're building. Read their code. See how they solved problems. Take what's useful.

This page gets updated as I find new repos worth studying.

------

Claude Code Interfaces

#### What it does:

A web-based front-end for Claude Code. Lets you run Claude Code through a browser interface instead of the terminal.

#### What's worth studying:

How they handle session persistence

The websocket connection between front-end and Claude Code CLI

Their approach to streaming responses

#### What I borrowed:

The session persistence patterns. Being able to close the browser and come back to the same conversation.

------

#### What it does:

Another Claude Code wrapper with a focus on project management. Tracks usage, manages multiple projects, provides a cleaner interface than raw terminal.

#### What's worth studying:

Usage tracking implementation

Multi-project switching

How they structured the settings/config system

#### What I didn't use:

Most of the UI complexity. Too many features for what I needed. But the underlying patterns are solid.

------

#### What it does:

A terminal UI (TUI) for Claude Code. Still in the terminal, but with better visual organization.

#### What's worth studying:

How they parse and display Claude's output

Keyboard shortcuts and navigation patterns

The balance between terminal simplicity and added features

People who want to stay in the terminal but want a better experience than raw CLI.

------

Custom AI Chat Interfaces

#### What it does:

A self-hosted web interface for various LLMs. Supports multiple providers, local models, and has a clean chat UI.

#### What's worth studying:

Multi-provider architecture (how they abstract different AI backends)

The conversation management system

Their approach to system prompts and presets

#### What you might borrow:
