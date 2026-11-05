---
type: Concept
id: 130_icm_knowledge_big
title: "ICM_knowledge.md (part 131/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Treat context files like working notes. When the project changes, edit the context. When you learn something new about what Claude needs to know, add it. When a constraint no longer applies, remove it. This takes 30 seconds per edit. It is the single highest-leverage habit in the whole system.

Some people add a "Last updated" line at the top of each context file. Simple but effective. When you open a workspace and see "Last updated: six weeks ago," you know to review it before working.

------

Mistake 6: Putting everything in one folder and hoping the CLAUDE.md sorts it out

The opposite of too many workspaces. Everything lives in one flat directory. Fifty files. No subfolders. The CLAUDE.md tries to route between them using file names alone. Claude reads the whole directory listing, picks what it thinks is relevant, and often picks wrong.

This is the equivalent of dumping every document on one desk and asking someone to find the right one. They can do it. It just takes longer, they make more mistakes, and they get frustrated.

If you have more than 8-10 files at the same level, you need subfolders. Group by workspace (what kind of work), then by stage or type within the workspace. The folder structure is the architecture. It tells Claude what belongs together. Let it do that job.

------

Mistake 7: Building the whole system before using it

The most common mistake. Someone reads 3.1 and 3.2, gets inspired, and spends an entire weekend building a perfect folder architecture with six workspaces, detailed context files, naming conventions, skills wired into every workspace, and a routing table with twenty rows. They have not used Claude once during this process. They built the factory without ever making a product.

Then they start using it and realize half the decisions they made do not match how they actually work. The workspace boundaries are wrong. The context files describe what they thought they would need, not what they actually need. They have to rebuild.

Build the minimum. One CLAUDE.md, one or two workspaces, one CONTEXT.md per workspace. Start working. After a few days, you will know what is missing. Add it then. After a week, you will know what is wrong. Fix it then.

The best folder setups in the community were all built incrementally. They started simple and grew based on real work. The ones that stalled were the ones that tried to be complete before day one.

Your first version should take 15 minutes. If it took longer, you over-built.

------

The pattern across all seven

If you look at these together, they all point in the same direction. Keep the system small. Keep it focused on the work, not on Claude. Update it as you go. Let the structure grow from use, not from planning.
