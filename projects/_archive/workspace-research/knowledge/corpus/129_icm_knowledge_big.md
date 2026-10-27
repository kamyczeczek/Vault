---
type: Concept
id: 129_icm_knowledge_big
title: "ICM_knowledge.md (part 130/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Someone sets up eight workspaces for a project that really only has two or three modes of work. They have a workspace for research, a workspace for notes, a workspace for drafts, a workspace for editing, a workspace for final review, a workspace for publishing. Each one has its own CONTEXT.md. The CLAUDE.md has a routing table with twelve rows.

Now the overhead of maintaining the system is bigger than the work itself. Context files go stale. Claude spends more time navigating between workspaces than working in them. The whole point of the architecture was to reduce complexity, and instead it multiplied it.

Start with two or three workspaces. You can always add more. The question to ask: "Do I shift mental modes between these tasks?" Writing and building are different mental modes. That is two workspaces. Drafting and editing are the same mental mode at different stages. That is one workspace with a process inside it, not two workspaces.

If you are not sure whether something deserves its own workspace, it does not. Keep it as a subfolder inside an existing workspace. You can always split it out later if the work grows.

------

Mistake 4: Writing context files that describe what AI should be instead of what the work is

This one is subtle. People write context files full of instructions about Claude's personality. "Be creative. Be concise. Be professional. Think step by step. Use a warm tone." They spend 30 lines describing how Claude should behave and two lines describing the actual project.

Claude responds to context about the work far more than context about itself. Telling Claude "you are a senior copywriter" gives it a role. Telling Claude "the audience is mid-market HR directors who have tried three other tools and are skeptical of AI claims" gives it something to actually work with. The second one changes the output more than the first.

Flip the ratio. Spend 80% of your context file describing the work: what the project is, who the audience is, what has already been done, what good output looks like, what to avoid. Spend 20% or less on behavioral instructions. If your context file reads like a personality quiz, rewrite it. If it reads like a project brief that a new team member could pick up and start working from, you are in the right place.

------

Mistake 5: Never updating the context files

Someone sets up the folder in week one. Writes the context files. Gets great results for two weeks. Then the project evolves. New requirements, new direction, new constraints. But the context files still say what they said on day one. The output starts drifting. Claude is still working from old context. The member thinks Claude "got worse" when really Claude is doing exactly what the context tells it to do. The context is just stale.
