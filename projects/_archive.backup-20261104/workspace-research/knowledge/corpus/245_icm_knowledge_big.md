---
type: Concept
id: 245_icm_knowledge_big
title: "ICM_knowledge.md (part 246/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

One section per worker, even if the worker asked

multiple sub-questions. Keeps Ari's attention on one task at a time.

Verbatim is fine.

Don't paraphrase the question body — Ari reads the

worker's own words best. Strip the YAML frontmatter, keep the four sections.

dispatch.py answer

Compose Ari's answer

into a new task, re-dispatch a fresh worker, print the new worker id.

Never edit the old worker's log or try to "continue" the old session.

#### The Process

1. Plan (you do this — never     delegate planning)

Break the work into discrete, independent tasks

For each task, decide: haiku or sonnet?

Identify ordering constraints (what blocks what)

#### Create a TodoWrite checklist

1. Dispatch Executors

For each task, dispatch a subagent using the executor prompt template below. Key rules:

One task per subagent.

Fresh context each time.

Provide everything the subagent needs

in the prompt — file paths, specs, code snippets. Don't make them search.

Parallel by default.

Dispatch multiple subagents simultaneously whenever tasks don't touch the same files. Send all independent Agent calls in a single message block. This is the main speed advantage — 5 tasks in parallel finishes in the time of 1.

Mix dispatch paths in parallel.

You can dispatch Agent tool subagents and ask.py Bash calls in the same message. A Haiku subagent editing file A, a Sonnet subagent editing file B, and an ask.py call to Kimi for research — all at once.

Only serialize when there's a real dependency.

Task B reads a file Task A writes? Wait. Task B is in a completely different directory? Ship it.

ask.py calls are always safe to parallelize

— they're text-in/text-out with no file access, so they never conflict with anything.

1. Handle Escalations

#### Executors report one of four statuses:

— Move to review.

DONE_WITH_CONCERNS

— Read the concerns. If they're about correctness, address before review. If they're observations, note and proceed.

NEEDS_GUIDANCE

— The executor hit something that requires judgment. This is the advisor pattern in action:

Read what they tried and where they're stuck

Think through the strategic decision (architecture, approach, tradeoffs)

Re-dispatch with your guidance baked into the prompt: "Use approach X because Y. The relevant pattern is in [file] at [line]. Here's how it should connect..."

Same model unless the task complexity has genuinely increased

— The task is beyond the executor's capability:

If it's a context problem → provide more context, re-dispatch same model

If it needs more reasoning → upgrade to

→ do it yourself)

If the task is too large → break it down further

If the plan is wrong → revise the plan

1. Review (you do this —     never delegate final review)

#### After each task completes:

Read the subagent's report

Spot-check the actual files changed (read key files yourself)

If the work looks wrong, dispatch a fix subagent with specific instructions

Mark the task complete

#### After all tasks:
