---
type: Concept
id: 165_icm_knowledge_big
title: "ICM_knowledge.md (part 166/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Most optimised skills end up <500‑800 tokens – supports ICM’s “break apart” philosophy

Host working on open‑source hybrid version (combining SkillOpt + Karpathy’s AutoResearch)

Community & Collaboration

VIP Discord – connect, ask questions, find collaborators

Recordings + Downloadable Artifacts

Transcripts, slide decks, summarised markdown files

Designed to be fed into your own AI/second brain

Value of knowing everyone in the room “gets it” – skip the AI education preamble

------

Uncategorized\Stop Babysitting Your Agents.md

Stop Babysitting Your Agents (Cloud Code 301)

Prerequisites (Table Stakes)

High‑quality

file (highest leverage)

Connect tools (Slack, Asana, Linear, Datadog, BigQuery, …)

Remote environment on Cloud Code Web (decouple compute from laptop)

Why Tooling Must Change

Most tools built for humans, but agents now write most code

Good news: prettier, linters, type‑checkers work well for agents too

Bad news: humans have blind‑spot assumptions agents don’t share

Key question: “What does an agent need from your codebase that a human takes for granted?”

Verification → Multi‑Clauding → Background Loops

Stack them together → work autonomously without you at the keyboard

Verification – Teaching Claude to Check Its Own Work

Human verification loop (same pattern works for agents)

Design/write code → build/compile → run executable → check side effects (UI, logs, DB) → run unit tests → deploy to staging

Autonomous Loop for Claude

#### Give Claude tools + instructions to iterate:

Run/build it

Verify result (browser, logs, DB, tests)

If failure → debug → write more code → repeat until success

Example: fix sign‑up button – it ran dev server, opened browser, clicked, saw nothing, read logs, fixed code, reloaded, repeated until working PR

Flavours of Verification

Front‑end (UX)

End‑to‑end (incl. infra)

Core concept same: provide tools so Claude can loop

Concrete Front‑end Loop Setup

Run dev server (

npm run start

Give browser control (Chrome MCP, Playwright, etc.)

Prove behaviour (before/after screenshots)

#### Unblock common obstacles:

Auth (give Claude an identity to log in)

State (pre‑configure app state dynamically, like test fixtures)

Packaging: Self‑Improving Skills

Store verification instructions in a skill file

Include rule: “document every blocker you hit and update this skill”

Becomes self‑documenting, distributable to whole team

Demo: created a verification skill for MonkeyType app, then used it to build a new feature (confetti on mistype) – Claude auto‑fixed lint errors inside the loop

Multi‑Clauding – Managing Many Agents at Once

Problem: more than 4‑5 sessions overwhelm attention

Cloud Code Desktop App

Sidebar showing all sessions (local, cloud, across repos)

Pin, rename, colour‑code → protect attention

Cloud Agents (Terminal)

cloud agents

command → list of local sessions sorted by urgency

Pin, rename, reorder

Cloud Code on the Web
