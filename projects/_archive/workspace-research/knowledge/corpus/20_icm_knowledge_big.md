---
type: Concept
id: 20_icm_knowledge_big
title: "ICM_knowledge.md (part 21/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

#### During a Remote Control session:

You don't need to update constantly. The session persists across devices automatically. Update when you're about to end the session or when you hit a major milestone.

#### Before walking away:

If there's any chance the session might end while you're gone (laptop sleeps too long, battery dies, terminal crashes), update

PROGRESS.md

http://progress.md/

before you leave.

#### After any significant decision:

If you made a choice that future-you needs to remember, write it down. "We decided X because Y."

#### When you hit token limits:

Long sessions hit context limits. Before you lose coherence, have Claude summarize progress and update the files.

------

The Reconnection Workflow

#### When you start a fresh session after the previous one ended:

Step 1: Orient

Read CLAUDE.md and PROGRESS.md. Summarize where we are.

Claude reads the context. You verify it matches your understanding.

Step 2: Verify

Look at the actual code/files. Does the progress file match reality?

Sometimes sessions end unexpectedly. The progress file might say something is done that isn't. A quick check catches this.

Step 3: Continue

Let's continue with [specific next task from progress file].

You're back in context. You didn't waste time re-explaining the project.

------

Remote Control + Workspace Persistence

#### These two systems work together:

Remote Control

handles persistence within a session. You can switch devices freely. Context carries over automatically.

Workspace files

handle persistence across sessions. When a session ends and a new one starts, the files catch you.

#### Think of it like this:

Remote Control = short-term memory (within a conversation)

Workspace files = long-term memory (across conversations)

You need both.

------

When Sessions End Unexpectedly

Sometimes you lose connection. Sometimes your laptop dies. Sometimes Claude runs out of tokens mid-task.

#### When you reconnect or start fresh:

Don't assume the last task completed.

Look at the files.

Did Claude write what it said it would?

Ask Claude to assess.

"Look at the code. Did the last task finish successfully?"

PROGRESS.md

http://progress.md/

with the actual state, not what you expected.

Unexpected ends are normal. The workspace catches you.

------

Making It Automatic

You can build the persistence habit into your prompts.

#### Session start prompt (save this):

Read CLAUDE.md and PROGRESS.md. Summarize: what is this project, where are we, and what should we work on next?

#### Session end prompt (save this):

Update PROGRESS.md with what we accomplished this session and what's next. Then give me a one-sentence summary of today's progress.

#### Before stepping away:

Update PROGRESS.md with current status in case this session ends.

These become reflexes. You stop thinking about it.

------

The Bigger Pattern

This is the same principle from Foundation. The folder architecture is the source of truth.

http://claude.md/
