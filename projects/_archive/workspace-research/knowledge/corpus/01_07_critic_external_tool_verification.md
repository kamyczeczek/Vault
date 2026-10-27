---
type: Concept
id: 01_07_critic_external_tool_verification
title: "CRITIC — verify-then-correct with external tools: the ablation that quantifies grounding (part 2/2)"
source: "07_critic_external_tool_verification.md"
tags: [agentic, agents, context-engineering, memory, prompt-engineering]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**Design rules derived.**
1. The critique must be **observable output from the environment**, concatenated verbatim into the context —
   not the model's summary of what a tool would say. This is what makes the correction evidence rather than
   opinion; it is also what makes the loop reproducible.
2. Corrections should be **targeted at known-bad outputs**. A blanket revise-everything policy pays the
   oracle gap; a cheap external gate that decides *whether to correct* recovers most of the headroom.
3. Iterate with a stop condition on unchanged output, not a fixed round count — unbounded revision rounds
   re-expose correct answers to critique noise.

**Why it completes the picture.** Reflexion documents errors into memory; AgentDebug finds the root cause;
Honest Lying shows stored diagnoses can be confabulated; Huang et al. shows ungrounded correction is
net-negative. CRITIC is the constructive counterpart: **the environment, not the agent, is the author of the
critique**, and the ablation measures exactly what that is worth.
