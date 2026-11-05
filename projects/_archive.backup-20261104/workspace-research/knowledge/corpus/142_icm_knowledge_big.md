---
type: Concept
id: 142_icm_knowledge_big
title: "ICM_knowledge.md (part 143/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Jake's content\The Foundation\4.4 Making Claude Understand Your Project.md

4.4 Making Claude Understand Your Project

What You'll Get From This

You will write a CLAUDE.md file that makes Claude Code behave like it has been on your project for a month. One file. Ten minutes. The difference is immediate.

------

Video: Session 4 — Making Claude Code Understand Your Project

#### Coming Soon

------

One file changes everything

In Session 1 you installed Claude Code. In Session 2 you used it on real tasks. In Session 3 you used Desktop for thinking. All of that worked. But there is a problem you have probably already noticed: Claude Code does not know your project.

It does not know your conventions. It does not know your file structure. It does not know which libraries you use, which commands to run, or what you consider good work. Every time you start a new conversation, Claude is a smart stranger. It can do the work, but it guesses at all the things a team member would already know.

#### The fix is one file:

------

What a CLAUDE.md is

A markdown file that sits in the root of your project folder. Claude Code reads it automatically every time it starts. It tells Claude what this project is, how it works, and what matters. Think of it as an onboarding document for a new hire. Except the new hire reads the entire thing in two seconds and follows every word.

------

Before vs after

Run the same task on the same project. First without a CLAUDE.md. Then with one. The difference:

Without CLAUDE.mdWith CLAUDE.mdGeneric code styleMatches your conventionsGuesses at file structureKnows where things liveDoes not know your commandsRuns your actual test suiteSuggests wrong librariesUses your dependencies

This is the same principle from

Section 1.2

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fdee3f73c53b46049078494c0cfb2e54&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

: structured context changes the output. The CLAUDE.md is a more focused, project-specific version of the identity and context files you set up in Section 1. If you skipped Section 1 and jumped straight to Section 4, this lesson still works. But go back to 1.2 afterward to understand the bigger picture.

[📌 JAKE: The before/after demo is the most important visual in this lesson. Same task, same project. Show the generic output without CLAUDE.md, then the specific output with it. Side by side if possible.]

------

What goes in it

Five things. Keep it short. 15 lines is enough. 10 minutes to write.

1. Project overview

— Two to three sentences. What is this? What does it do?

1. Tech stack

— What languages, frameworks, databases, tools.

1. How to run things

— Dev server, tests, build commands. The commands Claude needs to know.

1. Key conventions

— Naming patterns, file structure, architectural patterns you follow.

1. What to avoid
