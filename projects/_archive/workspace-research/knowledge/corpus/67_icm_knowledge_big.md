---
type: Concept
id: 67_icm_knowledge_big
title: "ICM_knowledge.md (part 68/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

------

Want the full Claude Code walkthrough? Head to

4.1: Install and First Use

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=fd76648c16ad429fb6e828b01bfa9177&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

— that covers everything from install to your first real use BUT through the lense of a use case in my animations as well so you not only understand the how, but the why.

------

You just got your tools. Now you are going to build something with them.

------

Jake's content\The Foundation\1.2 Your First Folder.md

1.2 Your First Folder

What You'll Get From This

A working folder that changes how Claude responds to you. Three files. Five minutes. You will see the difference immediately.

------

Right now, most people open Claude, type a question, and start over every time. Every conversation begins from zero. You spend half the message explaining who you are, what you are working on, and what you need. Then you hit the token limit, start a new chat, and do it all again.

The folder fixes that.

You give Claude a small set of files. Those files tell it who you are, what the project is, and what good work looks like. Claude reads them and its responses change. You will notice it in the first message.

This is the quick version. We are getting you a win right now. If you want to understand why this works (context windows, tokens, routing, the full architecture), that is all shown and explained in

. You do not need any of that to start. You just need three files.

------

Step 1: Make the Folder

Open your code editor (VS Code or Cursor from Lesson 1.1). Create a new folder. Name it after whatever you are working on.

my-first-workspace/

------

Step 2: Create Three Files

Inside that folder, create three files. Use

) if you can. Plain

File 1: CLAUDE.md

This tells Claude who it is working for and how to behave.

# Identity

You are helping [YOUR NAME] with [WHAT YOU DO].

## Rules

\-    Write in plain, clear language

\-    Ask clarifying questions before making assumptions

\-    When you are unsure, say so

Replace the brackets with your info. Keep it short.

File 2: CONTEXT.md

This tells Claude what you are working on right now.

# Current Project

## What we are building

[Describe your project in 2-3 sentences]

## What good looks like

[What does a successful output look like?]

## What to avoid

[Common mistakes or things you do not want]

File 3: REFERENCES.md

Background material. Examples, links, notes, anything Claude should know about but does not need to act on directly.

# References

## Examples of good work

[Paste an example or describe what you liked about it]

## Relevant links

[URLs, docs, resources for this project]

## Notes

[Anything else Claude should know]

That is it. Three files.

------

Step 3: Point Claude At It

#### If you are using Claude Code (terminal):

Navigate to the folder, type

. It reads the files automatically.
