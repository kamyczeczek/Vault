---
type: Concept
id: 118_icm_knowledge_big
title: "ICM_knowledge.md (part 119/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

In the video, you will see me working inside VS Code. VS Code is an IDE, a developer environment that lets you see all your folders and files in a sidebar and open them without double-clicking through your file system. It makes it easier to bounce between files.

You do not need VS Code to do any of this. You can work inside your regular file explorer, create folders, create text files, and edit them in Notepad or any text editor. You can also use Claude Cowork, which operates inside folders the same way. VS Code is just cleaner for managing lots of files. If it feels overwhelming, skip it for now and use whatever you are comfortable with.

------

What markdown is and why we use it

Every file in this system is a markdown file (.md). If you have never seen one before, markdown is just a text file with some lightweight formatting.

Dashes make bullets

Hashtags (pound signs) make headers

Asterisks make

That is it. When you talk to Claude and see its responses with bolding, headers, and clean formatting, it is already writing in markdown. Copy a Claude response and paste it into a plain text file. All the formatting turns into markdown symbols. That is how it was making it look that way.

A man named John Gruber created markdown in 2004. The idea was: write something readable as plain text that can also render into a formatted document. He named it "markdown" as a play on "markup language" (like HTML). Markdown strips away all the tags and complexity and makes it look like plain English with a few symbols.

Claude reads markdown cleanly. That is why we use it for every file in the system.

------

The three layer routing system

This is the core of the whole thing. Three layers. Each one has a job.

Layer 1: The Map (CLAUDE.md)

This is the top-level file. It sits at the root of your project folder. Every time Claude enters this workspace, it reads this file first.

Think of it as the floor plan. You walk into any building, the floor plan is on the wall, and you know where to go. The CLAUDE.md file tells the AI:

What this project is

What the folder structure looks like

Naming conventions for files

Where things go

This is the most important pattern in the whole system. Inside it, you put a simple table that tells the AI: for this task, read these files, skip those files, you might need these skills.

Without this, the AI either reads everything and wastes tokens, guesses wrong about what matters, or produces work you cannot edit along the way. This table eliminates all of those problems.

Layer 2: The Rooms (Workspace Context Files)

Each workspace has its own context file. When you tell Claude to work in the Writing Room, it reads the Writing Room context file. When you are in Production, it reads the Production context file. It only loads what it needs for where it is.

#### These context files describe:

What this workspace is for

What the process looks like (first I do this, then I do that)
