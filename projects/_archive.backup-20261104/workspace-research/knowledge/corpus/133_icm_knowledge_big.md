---
type: Concept
id: 133_icm_knowledge_big
title: "ICM_knowledge.md (part 134/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

VS Code (Visual Studio Code) is a coding environment made by Microsoft. If you have never opened it, do not worry. It is simpler than it looks and we will walk through setup. You do not need to know how to code. VS Code just lets you see your folders as a file tree and open documents without clicking through layers of windows.

If you are familiar with Cursor, Windsurf, Copilot, or Antigravity, those are all built on top of VS Code. They support different models and different processes. Some use Claude, some do not. This course is specifically for Claude's tools inside the Anthropic environment.

Claude Code in the terminal

The same engine under the hood, just a different wrapper. The terminal version is better for when your work does not live in a code project. Processing a folder of documents. Managing files. Cleaning up your downloads folder. Anything where you just need Claude to read a bunch of files and do something with them.

You do not need the terminal version to get value from this course. But if you are already comfortable in the terminal, it is faster for some jobs.

------

The real difference

The desktop is a conversation layer. VS Code is an editor layer. The terminal is a command line layer. Same brain behind all three.

Interface Best for Can see your files? Can edit your files? Claude Desktop /

http://claude.ai/

Thinking, planning, quick questions, drafting Only if you upload them No Claude Code in VS Code Building, editing, working inside a project Yes, automatically Yes Claude Code in terminal File processing, quick tasks, non-code projects Yes, in the current folder Yes

------

Let me show you the difference

Here is the same task across all three.

#### In Claude Desktop:

You want to summarize a document. You go find the file on your computer. You upload it. You type "Summarize this PDF and suggest three improvements." Claude processes it and gives you a good answer. Works fine. But you had to go find the file, upload it, and then the summary lives in the chat. If you want it in a file, you copy and paste it somewhere.

#### In VS Code:

You open the folder where the document lives. You type "Summarize python breakdown PDF and suggest three improvements." Claude immediately knows which file you mean because it can see the folder. It reads the file, gives you the summary, and can write the output directly to a new file in the same folder. One less step. No uploading. No copy-paste.

#### In the terminal:

You open a terminal in the folder, type

, and give the same instruction. Same result as VS Code, just a different window. Better for quick one-off tasks where you do not need to see the file tree.

The model gives the same quality answer in all three. The difference is how much manual work you do around it.

------

Installing everything

Let's get all three working.

Step 1: Claude Desktop

#### If you do not have it already:

claude.ai/download

http://claude.ai/download
