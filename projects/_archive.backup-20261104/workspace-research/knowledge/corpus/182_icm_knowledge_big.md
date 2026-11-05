---
type: Concept
id: 182_icm_knowledge_big
title: "ICM_knowledge.md (part 183/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

The output must be a file the user can press a download button to retrieve. Use your file creation tool to write it to the outputs directory, then present it. Do not produce a code block in the chat.

------

Uncategorized\logbook\OB1_openbrain.md

Interesting take, every coding decision I make every commit is captured into my open Brain which allows for full semantic searching. This is accomplished with supaBase DB and mCP. The main advantage I see to this method is it allows for remote connections similar to an obsidian graph

I use OB1 with Supabase because it's actually built for how I work with AIs now. Obsidian is fantastic for writing and linking notes by hand, but it doesn't solve the real problem: every new chat starts blank.

With OB1, I have one Postgres database where all my AIs can read and write the same long-term memory. pgvector handles the semantic search so they actually find relevant stuff by meaning, not just keywords. I connect them once via MCP and they stay in sync—no copy-pasting context, no forgetting between sessions.

It's simple infrastructure that does exactly what I need: persistent shared memory without the extra layers. I still drop stuff into Obsidian when I want nice graphs or daily notes, and I can import the vault anytime. But OB1 is where the real work happens.

Solid questions.

#### Permissions:

Most agents get broad read access via pgvector semantic search. Write access is scoped -- different Supabase tables/collections (project_memory, code_decisions, sensitive). I use RLS policies + per-agent JWT tokens. New agent? Assign the right token and done.

They’re rare. Every record has last_updated_by + timestamp. On clash, the newer one wins by default and a conflict branch gets created. My orchestrator flags them for review.

#### Sensitive info:

Stays in a locked sensitive collection with RLS + client-side encryption for keys and private data. Only my inner agent can touch it, and even then the prompts block output unless I explicitly approve.

This setup means every AI starts with real shared memory instead of a blank slate. No more copy-paste hell.

Yes - agents get a mandatory baseline context packet (system prompt + latest canonical maps) on every new session. Semantic search pulls supporting history on top of that.

Orchestrator flags conflicts and pauses the loop for me to review. It doesn’t auto-resolve. I want the human judgment layer on anything that touches core truth.

This keeps the logbook pure history while the maps stay clean for active work.

#### Hope I'm reading your mind:

BASELINE CONTEXT — CURRENT TRUTH

Last refreshed: [YYYY-MM-DD HH:MM]

Project: [One line project name + goal]

Core Objective: [Single sentence north star]

#### Canonical Maps (Active Truth):

[Link or paste key map/file] Product roadmap

[Link or paste] Folder structure and naming rules

[Link or paste] Tech stack and constraints

[Link or paste] Decision log (latest 5 only)

#### Current Rules and Standards:
