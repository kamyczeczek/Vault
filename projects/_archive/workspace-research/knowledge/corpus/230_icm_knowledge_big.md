---
type: Concept
id: 230_icm_knowledge_big
title: "ICM_knowledge.md (part 231/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Initially I proposed, that anyone who wanted to implement @Deacon Wardlow's session memory layer on PMM could simply tell the LMM what it needed to be done (PMM is extensible that way). But I forgot that the agentic plugins and skills building skill I developed was a separate plugin than PMM. It would work without, but not as well as it should with the plugin. So I pushed it as a memory feature in v2.8.

Based on his feedback, I integrated session awareness into PMM (and duly credited him with the idea and methodology for the fix). The feature is live for Claude Code CLI and Co-work (but I haven't gotten around to doing it for the OpenCode plugin, yet).

You can install PMM v 2.8 from the github repo.

#### Here are the changes that were implemented:

timeline.md doesn't just capture session summaries and updates at the end of every session

It now captures what changed and indexes / refers to the entries in the other memory files

This includes entries in the newly introduced threads-open.md and threads-closed.md which tracks issues and projects user is working on (what it is, why you're working on it, what needs to be done, what's been done, success criteria etc). Doesn't require you to say explicitly (but it will help).

When completed, a summary is retained in threads-open.md with a reference to the completed project or issue (archived) in threads-closed.md

Loaded at every session start or after every compact or clear

Saved at every session end (I still recommend manually /pmm:save)

#### How PMM is different form the other memory systems out there:

Other systems are passive, like filing cabinets, and only as smart as the retrieval assistant searching through them and deciding what is relevant to hand off to the LLM that speaks to the user.

Retrieval system like RAG and a storage system like Graph or Vectors decide what is relevant from past conversations and hands it to the LLM

PMM autonomously decides what's relevant, what to save and what to retrieve

PMM makes the LLM an active participant in its own memory.

It was an experiment in "what happens when I just tell the LLM about memories and where they are" instead of trying so hard to stuff what I (or some other system) think is relevant into context memory.

I've been working on something more polished: a more organic memory system that strips PMM down to core essentials with more autonomy for the LLM. But that's a discussion for another day....

------

david vogel\David and Jake's Picks V2\START HERE.md

What this is?

A quick explainer on how curated posts in David's & Jake's Picks now work --- what's changed, why, and how to read them.

Why it matters

You can now decide in five seconds whether a post is worth your time instead of clicking through and hoping for the best.

#### David's note:
