---
type: Concept
id: 233_icm_knowledge_big
title: "ICM_knowledge.md (part 234/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Step 1: Questionnaire

#### Ask all 7 questions below in a single message. Tell the user:

"I'll set up your TaskSystem. Answer these questions and I'll build everything in one pass — you can answer all at once."

------

Q1 — Work categories

What areas of work do you track? These become the Category column in your task board.

Work, Personal, Admin, Creative

Client, Internal, Learning, Side Projects

Q2 — Energy pattern

When do you do your best focused or creative work? When do you handle low-energy tasks?

Example: "Sharp in the morning for deep work. Admin tasks mid-afternoon. Mental battery low by 8pm."

Q3 — Work start time

What time do you typically start a session?

after lunch

Q4 — Recurring tasks

List 2–4 recurring tasks and how often they repeat.

Weekly team standup (7 days). Expense report (monthly). Meal prep (every 4 days).

Q5 — First project

Name your first project and describe it in one sentence. Use lowercase-hyphenated format.

portfolio-site — Redesign and rebuild my personal website.

If you don't have a first project yet, say "skip" — I'll create an example project to show the structure, and you can replace it when ready.

Q6 — Short-ID prefix

What 2–5 letter prefix for that project? Used to tag ideas and tasks.

Skip if Q5 was skipped — the example project will use

as its short-ID.

Q7 — Name or handle

What's your name or handle? Used to personalize the system.

------

Step 2: Confirm Before Building

#### After collecting answers, confirm back to the user:

"Here's what I'm building:

#### Categories:

#### Energy pattern:

[brief summary of Q2]

#### Session start:

#### Recurring tasks:

[N from Q4]

#### First project:

[Q5 name] (

example-project

) if Q5 was skipped

I'll create 14 files in

[current directory]

. Is that correct?"

Wait for confirmation before writing anything. If the user corrects the directory, use the path they provide.

------

Step 3: Create All Files

If no working directory is established, ask the user where to create the files before proceeding.

Fill in every

marker in the templates below with the corresponding answer from Step 1. Parse Q4 into individual recurring task rows. Name the first project folder and files using Q5's project name.

#### If Q5 was skipped:

example-project

as the project name,

as the short-ID, and

example project

as the description for all project files and folders. Proceed with all 14 files as normal.

------

FILE: CONTEXT.md

# TaskSystem

*Read this file first, then the relevant CONTEXT.md for each subsystem.*

------

## Routing
