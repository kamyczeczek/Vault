---
type: Concept
id: 175_icm_knowledge_big
title: "ICM_knowledge.md (part 176/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

For any non-trivial change: pause and ask “Is there a simpler, more observable way that lives entirely in the filesystem?”

If a fix feels hacky, implement the elegant version that makes the next human review faster.

Skip over-engineering on obvious one-line fixes. Challenge your own work before it hits output/.

Autonomous Bug Fixing

Given a bug report or failing output, go fix it in the correct stage’s CONTEXT.md or references/.

Point at the exact file, line, or contract violation—then resolve it permanently.

Zero hand-holding required. The filesystem is your only context.

Task Management

: The workspace CONTEXT.md + numbered stage folders are the plan. Update them only via human-visible edits.

Verify Plan

: Before starting any stage, confirm the Inputs/Process/Outputs table in its CONTEXT.md matches reality.

Track Progress

: Mark completion by writing the finished artifact to output/ and updating the stage’s audit section.

Explain Changes

: High-level summary lives in the output/ README or the next stage’s input table.

Document Results

: Add a review section to the stage’s CONTEXT.md after human feedback.

Capture Lessons

: Turn every correction into a durable Layer 3 update—not just a note in lessons.md.

Core Principles

Simplicity First

: Every change must be visible in a markdown file. Minimal code, maximum filesystem clarity.

No Laziness

: Find the root contract or reference that allowed the error. Fix it there forever. Senior standards only.

Minimal Impact

: Touch only the exact Layer and file necessary. Never introduce new state outside the defined output/ handoff.

Observability Above All

: If a human cannot open a folder and instantly understand the current state, you have already failed.

------

Uncategorized\notes_on_hermes.md

What it is: Open-source, self-hosted autonomous AI agent (Nous Research) that runs 24/7 on your machine/server. Not another IDE copilot it's a persistent personal colleague that actually remembers you.

Core cheat code: Built-in persistent memory + self-improving skills. It learns your preferences, projects, and workflows across sessions instead of resetting like a goldfish every time. You own the stack, no vendor lock-in.

#### Where it beats plain VS Code + Claude:

Claude wins raw coding sprints and editor integration.

Hermes wins long-term autonomy, background tasks, cross-session recall, and orchestration (duct-tape it with Claude Code for the best of both).

Great if you’re tired of re-explaining context or want an agent that evolves with you. Less essential if you prefer fresh slates every session and stay desk-bound.

------

Uncategorized\Stop feeding raw documents to your LLM\tomd\README.md

tomd — documents to token-lean Markdown

files into Markdown that's

cheap to feed an LLM. Every conversion produces two files beside the source:

— a faithful Markdown rendering of the document.

name_lean.md

— the same content, deterministically stripped to the

token-minimal version.
