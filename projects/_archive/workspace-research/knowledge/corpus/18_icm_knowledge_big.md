---
type: Concept
id: 18_icm_knowledge_big
title: "ICM_knowledge.md (part 19/259)"
source: "ICM_knowledge_big.md"
tags: [1, agentic, agents, anti-leakage, context-engineering, defines, icm, memory, planning, prompt-engineering, reflection, short-id, show-your-work]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Example: Code Review

(Desk) Ask Claude to review a PR, enable Remote Control, walk to a meeting

(Mobile) During a break, check Claude's findings

(Mobile) "Focus on the authentication logic, ignore the styling issues for now"

(Desk) Read the detailed analysis when you're back

------

The "Don't Check" Option

Sometimes the best mobile workflow is not checking at all.

If Claude has a clear PRD and you're doing something else, let it run. You don't need to monitor constantly. The work will be there when you get back.

Mobile access is a capability. It's not an obligation to use it.

------

When to Check vs When to Wait

#### Check when:

The task has decision points Claude can't make alone

You're expecting it to finish soon

You gave Claude something ambiguous and want to course-correct early

Claude has a clear spec and doesn't need input

You're doing something that needs your full attention

You'll be back at your desk in 30 minutes anyway

The remote session persists. Claude keeps working. You don't have to watch.

------

Mobile Decision Tree

#### When you open the Claude app to check on a session:

Is it an error/blocker? → Assess: can I fix this in 2 messages?

Yes → Fix it (Mode 2)

No → Acknowledge and wait for desk

Is it asking for a decision? → Answer if it's clear cut

Clear decision → Respond (Mode 2)

Needs thought → "Continue with other tasks, I'll decide on this later"

Is it just a status update? → Glance and close the app (Mode 1)

Handoff Prompts

#### Before leaving desk:

I'm stepping away. Continue with [current task]. If you hit a blocker, describe it clearly and wait for my input.

#### When returning to desk:

What happened while I was away? Summarize progress and what you need from me.

------

#### Setting up Remote Control:

2.2 Using Remote Control

https://www.skool.com/quantum-quill-lyceum-1116/classroom/2a86a1d1?md=f305a93c1be949d3b3bcdbc2aa22a3f5&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

#### The workspace structure that makes handoffs clean:

3.1 The Full Walkthrough

https://www.skool.com/quantum-quill-lyceum-1116/classroom/036893d9?md=2b4a8ab7461c4f6d828e21c0eb196a6a&utm\_campaign=skool\_link\_classroom&utm\_content=9a42d1d697754c499c3effeee8135e03

------

You can control Claude from anywhere. But how do you maintain context when you switch devices or start fresh sessions? The answer is in how you structure your workspace.

------

Jake's content\Building Your Stack\2.4 Session Persistence Across Devices.md

What You'll Get From This

The ability to pick up exactly where you left off, even when sessions end.

------

[VIDEO: Coming Soon]

------

Two Kinds of Persistence

Remote Control gives you one kind of persistence: within a session, everything syncs across devices. You send a message from your phone, it appears in your terminal. Context carries over. The conversation is continuous.
