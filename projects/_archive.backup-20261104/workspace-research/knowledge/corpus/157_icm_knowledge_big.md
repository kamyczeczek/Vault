---
type: Concept
id: 157_icm_knowledge_big
title: "ICM_knowledge.md (part 158/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The whole spirit of my submission was that building can be as simple as bringing Claude what you want, and that's exactly how I did it. A few weeks in, feeling unqualified the entire time.

You don't need to be ready. You just need to start. Go build yours. 🛠️

------

See the build and my original thoughts during the build below. Leave a comment on the companion post to share your thoughts. 👇

Diana Agency Assistant](https://github.com/donroy26/Diana-Agency-Assistant)

------

Uncategorized\A Living ICM System Folder-Structure-as-Interface.md

This is a summary of the system that I've been working on since joining Clief Notes. This has been made by drawing off of a lot of different posts, weekly competitions, David's Corner, and the work @Ari Evergreen has shared with the community. This post specifically was made to address a question that has been pretty common with a lot of members: How a folder of plain text files becomes an operating system for AI work?

The whole philosophy in one line: This is not automation — it's orchestration through structure. The folders are the framework; the files are the code; a human reads and audits all of it.

#### What this is (plain-language version):

Most people drive AI with one giant prompt: they dump everything they know into a chat box and hope. That breaks down the moment a task has more than one step, because the AI has no map — it improvises, forgets, and contradicts itself.

This is a live implementation of ICM — Interpretable Context Methodology — the principle that structured files delivered at the right moment replace a framework telling the AI what to do. Instead of one giant prompt, the workflow lives in a folder of plain text files, and the folder structure itself is the interface. The way the folders are laid out tells the AI what to do, in what order, and where the boundaries are. There's no app, no code required, no cloud account. An AI agent walks into the folder, reads a small "you are here" file, and the structure routes it to exactly the right instructions at the right moment.

Everything below is ICM in practice. The toolkit isn't a new theory — it's what ICM looks like when you actually build it and run it every day.

One sentence: Structured files at the right moment replace a framework telling the AI what to do.

The payoff: instead of loading 30,000–50,000 words of context for every task, the AI loads only the 2,000–8,000 words relevant to the current step. It's faster, cheaper, more consistent, and — crucially — a human can read the whole system and audit it, because the files are the documentation.

The one rule that governs everything: 60 / 30 / 10

#### Before any task, ask three questions in order:

Is the answer deterministic? (a calculation, a lookup, a file operation) → write a script. Stop. Don't involve AI.

Can it be written as an if/this-then/that rule? (sorting, routing, categorizing) → a small automation or script. Stop.
