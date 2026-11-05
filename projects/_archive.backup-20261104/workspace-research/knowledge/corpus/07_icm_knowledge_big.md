---
type: Concept
id: 07_icm_knowledge_big
title: "ICM_knowledge.md (part 8/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

is where Claude thinks through what it's going to do before doing it. It creates a plan, breaks it into steps, and waits for confirmation.

Execution mode

is where Claude actually runs commands, writes code, fetches files.

You can affect which mode Claude uses, but usually it chooses on its own. For a complex build like this, it starts in plan mode. Good. I want to see the plan before anything gets built.

------

If you're using Claude 4.6 (the default), something interesting happens: Claude creates sub-agents.

Instead of doing everything in one thread, Claude sends smaller agents to handle specific tasks:

"Let me send an agent to study the workspace structure"

"Let me send an agent to fetch this repo"

"Let me send an agent to implement this component"

This saves tokens. The main Claude orchestrates while sub-agents do the fetching and studying. You'll see messages like "Task: agent" as these sub-agents spin up.

It looks like Claude is doing multiple things at once. It kind of is.

------

Watching Claude Work

Once the plan is set and I approve, Claude starts executing.

#### Bash commands

\-    Claude runs terminal commands to search the workspace, find files, check structure. When you see "bash" in the output, Claude is running a command just like you would in a terminal.

#### Web fetches

\-    Claude pulls files directly from GitHub repos. Instead of cloning the entire repo (which I told it to do), Claude searches through the repo and fetches only what it needs.

This is Claude making a better decision than what I asked for. I said "clone the repo." Claude realized it's more efficient to fetch specific files. That's fine. That's good. Let it be smarter than your instructions when it makes sense.

#### Reading and understanding

\-    Claude reads the package.json files from the repos to understand how they're structured. It reads the source files to understand the patterns. It's doing research while building.

------

Why Workspace Context Matters

Here's why I built inside my Animation Studio folder instead of a separate location:

Claude can reference my actual workflow while building the tool for it.

When Claude does a bash find command looking for folder structure, it finds my real folders. Script Lab. Animation Studio. The specs. The renders. All of it.

If I built in a separate folder, Claude would have to fetch that context from somewhere else. By building in place, the context is already there. Claude can see what it's wrapping an interface around.

------

Stateful Prompting

Normal Claude conversations are stateless. When you start a new conversation, everything from the previous one is gone.

But the PRD is a file. It persists. Every time I start a new Claude Code session in this workspace, I can say "read the PRD" and Claude is back up to speed.

#### This is why markdown files matter:

They're small (low token cost)

Claude reads them well

They're easy to edit

They persist between sessions
