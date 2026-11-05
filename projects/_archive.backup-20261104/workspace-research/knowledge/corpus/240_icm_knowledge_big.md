---
type: Concept
id: 240_icm_knowledge_big
title: "ICM_knowledge.md (part 241/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

'seed project [name]'

— add your first real project when ready

You have [N] recurring tasks. I've set up example-project as a placeholder to show the structure — replace it with your first real project when ready.

Type 'give me today' to start."

------

david vogel\David and Jake's Picks V2\I run four phases before any AI builds anything\I run four phases before any AI builds anything.md

I run four phases before any AI builds anything.

📝 What this is: A four-phase planning methodology (Brainstorm, Plan, Hand off Doc, Dispatch) that front-loads all thinking before any AI generates code or content.

💡 Why it matters: If you skip structured planning and jump straight to prompting, you spend 90% of your time babysitting outputs instead of getting clean results on the first pass.

🏷️ Tags: workflow-design, prompting, folder-architecture, templates, ai-philosophy

⏱️ 5 min read | 🔓 Free

✍️ David's note: Ari nails the thing most people get backwards — the build is the easy part, the thinking is the work. This four-phase approach maps cleanly onto the folder architecture we teach and proves why CONTEXT.md and spec docs exist. If you keep getting garbage outputs, the fix is upstream.

------

david vogel\David and Jake's Picks V2\I run four phases before any AI builds anything\advisor-driven-development.md

------

description: Advisor-driven development — Opus plans, cheap models execute, escalation on complexity

argument-hint: "[task or plan] — what to build, fix, or execute"

Advisor-Driven Development

You are the

(Opus). You plan, review, and provide strategic guidance. You dispatch

executor subagents

(Haiku or Sonnet) for all file I/O, code generation, and mechanical work. When executors hit complexity, they escalate back to you for guidance.

This mirrors Anthropic's advisor tool pattern — but inside Claude Code. Opus stays in the orchestrator seat. Cheap models burn through the mechanical turns. You only spend Opus tokens on judgment.

Read and understand the task or plan provided. If a file path is given, read it. If it's a description, internalize it.

Dispatch paths

New default: background dispatch via

dispatch.py

Main Opus session

fires detached workers and keeps talking to Ari. Workers log to files, surface

questions through a file-based protocol, and the main session calls

dispatch.py questions

on each turn to surface anything pending.

Four paths for getting work done. Mix freely in parallel — they don't conflict.

dispatch.py start

— spawn a detached Claude Code worker in the

background.

The new default for all executor work.

python3 tools/dispatch.py start --executor <minimax|haiku|sonnet> --task-file --cwd --label

Returns a worker id immediately (well under a second). The main session

never blocks.

The executor runs one of the three wrappers in path 3 below under the

hood, fully detached, with its stream-json log going to

~/dispatch/logs/.log

Workers that need Ari's judgment write a structured question file to
