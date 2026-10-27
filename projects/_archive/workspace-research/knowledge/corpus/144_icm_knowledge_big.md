---
type: Concept
id: 144_icm_knowledge_big
title: "ICM_knowledge.md (part 145/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

3.3: Common Mistakes and How to Fix Them

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=7b1919bbe3af42aa859b6060e4e7513f&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

. Every one of those mistakes applies to CLAUDE.md files too.

If you have multiple projects or different types of work,

Session 4.5

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=dd5a0adc38a440f29b48354a3a9da667&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

shows how to scale this with workspace routing.

------

You have one CLAUDE.md for one project. What happens when you have ten projects? Or a complex workflow with different types of tasks? Session 5 shows the full architecture and where all of this scales.

------

Jake's content\The Foundation\4.5 Where This Goes.md

4.5: Where This Goes

What You'll Get From This

You will see how the CLAUDE.md scales from one project to a full workspace architecture. You will set up two scoped contexts and watch Claude behave differently in each one. And you will know exactly where to go next.

------

Video: Session 5 — Where This Goes

#### Coming Soon

------

What you have built so far

Across the first four sessions, you set up three interfaces (Desktop, VS Code, Terminal), ran real tasks on your own files, used Desktop for thinking and Code for building, and wrote a CLAUDE.md that gives Claude project-level context.

That is more than most people will ever set up. And it works.

------

But what if...

You have 10 projects. Or a complex workflow with different types of tasks. Or a team that needs the same quality from Claude across everyone's work.

One CLAUDE.md per project still works. But there is a level above that.

------

Task routing

In my workspace, different tasks load different context. Automatically.

"Write a script" → loads voice docs only. "Build an animation" → loads the design system and component library. "Build a course module" → loads the curriculum and guidelines.

Same Claude. Same context window. Different context per task. The routing table in the CLAUDE.md decides what loads based on what you ask for.

This is the three-layer architecture from

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

in full operation:

Layer 1 (CLAUDE.md)

— The map. Routes every task to the right workspace.

Layer 2 (Workspace context files)

— The rooms. Each workspace has its own CONTEXT.md describing what happens there.

Layer 3 (Skills and tools)

— Plug-and-play. Loaded per workspace, not globally.

If you went through Section 3, this is what it looks like when you run it with Claude Code. If you skipped Section 3 and jumped straight to the Claude Code sessions, this is your introduction to the architecture. Go back to

Section 3.1
