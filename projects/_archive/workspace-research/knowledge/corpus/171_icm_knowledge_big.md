---
type: Concept
id: 171_icm_knowledge_big
title: "ICM_knowledge.md (part 172/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

♻️ Restructure. Point it at a folder, repo, or vault you already have. It reads every file, sorts each one by role, shows you a migration map, waits for your yes, then moves and checks the result.

🧩 The five forms

Pipeline, umbrella, record library, knowledge bundle, context map. They mix and nest, so most real workspaces use more   than one.

✅ The walk test

Every result gets checked cold. An agent with no memory has to open the root, find its way, act, and report status from the     files alone. If it can't, the structure gets fixed until it can.

⚙️ How to use it

You can honestly just tell claude to download it from the link, but if you're using codex or something else it will just have to  restructure the claude.md to

http://agents.md/

Or if you want to do more Hands-On install

Claude Code: drop the folder in ~/.claude/skills/icm-architect/, then say "ICM this" or "build me a workspace for X."

Claude apps: zip the folder and upload it under Settings, then Capabilities.

Maya ICM interactive tutorial

https://claude.ai/public/artifacts/7c9618f4-8324-4048-902c-cbcf77c9c102

Article on how to spot ai writing

https://en.wikipedia.org/wiki/Wikipedia:Signs\_of\_AI\_writing

eve framework

https://vercel.com/changelog/introducing-eve-an-open-source-agent-framework

claude cookbook

https://platform.claude.com/cookbook/

------

Uncategorized\logbook.md

Planes keep a black box so that when something goes wrong there is a full recording of what happened and when. Build the same thing into your ICM system: a logbook it writes itself, every job and every journal, that you can hand back to Claude at any point.

The setup is simple. Every Claude Code job writes a short record when it finishes - what it did, how it went, a grade, and any errors. Every design chat writes a journal when it is done drafting your ideas out. Every handover is stored in a set space.

All of the above - ORGANISED

Nothing is thrown away. The record just builds on its own in the background.

Then, any time you have spare usage, point Claude at the whole logbook: pull the bits that ran slow, the bits that failed, and the improvements worth making.

#### Once the logbook exists, here is what it gives you:

Query anything - ask in plain language what happened, when, and why.

Find the mistakes - surface exactly where and when something went wrong.

Improve the whole system - point at the record and tell it to fix the system as a whole

Security audits - every change that was made, timestamped and ready to review.

Client work - hard evidence and the answer already sitting there if a client complains.

Investor conversations - the same record holds up when you are showing what you have built.

Older systems - go back and read what a system used to do long after you have moved on from it.

Across projects - copy edits and systems from one project directly into another with ease
