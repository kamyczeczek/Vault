---
type: Concept
id: 229_icm_knowledge_big
title: "ICM_knowledge.md (part 230/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

TLDR: LLMs forget everything between sessions. You re-explain yourself constantly, lose progress on long-running work, and have no reliable way to pick up where you left off — especially when switching between models or tools. I built PMM to fix that. @Deacon Wardlow helped me improve it by identifying a specific gap: session continuity — what changed, what’s still open, where you stopped. That’s now live in PMM v 2.8.

Edit: I figured screenshots tell a better story => same memory on three different tools with 3 different models, where I've asked the LLM to basically recall outstanding tasks across the 4-5 current projects. Slightly different perspectives because I'm working a slightly different project with each model.

I initially built PMM to remember stuff beyond the context window to fix an issue i had with the LLMs I use failing to remember and recall over long conversations. I used it to have the same conversation, while switching between Claude Code CLI and Co-work.

Eventually it became a tool for helping me with continuity in my conversations with different LLMs on different apps and harnesses ( I switch a lot between Claude, OpenCode and GitHub Co-Pilot). I now use it to give multiple agents long-term memory (while they switch between different models on Claude, Gemini, Model Ark and a couple of smaller local models) without the use of model routing.

I currently deploy it (along with with another agentic plugin I developed) to give agents long-term individual and collective organisaitonal memory in their conversations with multiple users over telegram in a small pilot.

@Deacon Wardlow tested PMM in his own workflows, identified a gap in session memory management, and tried a couple of changes, which he outlined in another thread discussing Session Memory Layer + PMM.

The problem: your work changes between sessions, and you need the LLM to remember progress, granular task completion and what changed.

PMM already retains knowledge about you, your work and what you're working on

However, there was a gap where session awareness and continuity was lacking

It didn't retain knowledge of files and facts that change between sessions: what did you work on, what you did, where you stopped, what needs to be done at the next session and why.

#### Deacon proposed:

What was worked on in the last 10 sessions (rolling log)

What's still open and needs follow-up (persistent thread tracker)

Some of these were already implemented partially in existing memory files. I figured we also needed:

Resource tracking (what repos, directories, files belong to which thread / projects)

An archive of sorts for completed threads to minimise context usage for completed threads

Additional info (context, notes, blockers, dependencies) for threads
