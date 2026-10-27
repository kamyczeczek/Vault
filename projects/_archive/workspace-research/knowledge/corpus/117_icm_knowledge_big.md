---
type: Concept
id: 117_icm_knowledge_big
title: "ICM_knowledge.md (part 118/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

------

Jake's content\The Foundation\3.1 The Full Walkthrough (23 Min Video).md

3.1 The Full Walkthrough (23 Min Video)

What You'll Get From This

A working folder system that tells Claude where it is, what to do, and where to put the work. Three layers. Plain English. No code, no frameworks, no agents.

------

Video: Folder Architecture (23 Min)

If you want the written version first, keep reading. If you learn better by watching, start the video above and come back here for reference. Both cover the same ground.

------

The problem with how most people use AI

Right now, most people open Claude or ChatGPT, type something, get a response, and start over. Maybe they save a good prompt somewhere and paste it in again next time. Maybe they hit the token limit and have to start a new conversation. Maybe they spend half the message just re-explaining who they are and what they are working on.

That works for quick questions. It falls apart the moment you try to do real, ongoing work. You are burning tokens on stuff that does not matter. You cannot edit what the AI produces at each step. And every conversation starts from zero.

The folder structure fixes all of that.

------

What tokens are and why this matters

Before we get into the structure, you need to understand one thing: tokens.

A token is roughly three quarters of a word. Sometimes a single word. Sometimes a long word like "hamburger" is three tokens. The term comes from NLP research in the 1990s. Researchers needed a unit smaller than a word because language does not break the same way across every language. They borrowed "token" from linguistics, which borrowed it from old English "taken," meaning a sign or a symbol. A token is just the smallest meaningful chunk of a sentence.

There are only so many tokens an AI can hold in its context window before it starts failing. When people say "context window," they mean how many tokens the AI can see at once. That window is finite.

So if you dump everything into one conversation, an AI writing a blog post is also reading your video production notes. You are wasting tokens on information that has nothing to do with the task. The folder structure solves this by separating your work into areas and only loading what is needed for the task at hand.

------

The workspace blueprint: three workspaces for three kinds of work

Here is the concept. Instead of one giant conversation or one massive file, you break your work into separate workspaces. Each workspace handles a different kind of work.

#### For example:

— content, docs, community management

— scripts, animations, code, builds

Writing Room

— blog posts, newsletters, thinking, client work

These are just examples. Your workspaces will look different depending on what you do. A freelancer might have Client Intake, Delivery, and Admin. A developer might have Frontend, Backend, and Docs. The names change. The structure stays the same.

------

What VS Code is (and why you do not need it)
