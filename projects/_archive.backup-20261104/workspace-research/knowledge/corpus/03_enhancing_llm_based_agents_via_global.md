---
type: Concept
id: 03_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 4/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

3 Methodology
Figure 1 shows the framework of our GoalAct. Next, we introduce it in detail.
Searching
Coding
Writing
Other Skills
Global Planning
Plan step 1*    Plan step 2*Planstep3*…
Action 1*Action2*Action 3*…
Plan step 1Plan step 2Planstep3…
Action 1Action2Action 3…
User Query
Hierarchical Execution
EnvUpdate
•Reasoning...•Research…•Create…•…
•Special Process•gathering info•first draft•polishing…
•Python Code•loops•branch•max/sort/sum
•Text/Json Format•tool_name•arguments
Fig. 1 The framework of our GoalAct. It emphasizes continuously updatable global planning,
which harmonizes the clarity of long-term goals with actionable steps, and hierarchical execution,
which decomposes task execution into high-level skills.
3.1 Global Planning
In our GoalAct framework, we continuously maintain and update a global plan G,
defined as Equation (1) shows:
G = (P1A1, P2A2, P3A3, . . . , PnAn) (1)
Here, Pi denotes the i-th plan step, and Ai represents its corresponding action. Since
providing detailed action descriptions directly within the global plan is challenging,
we only require the specification of high-level skills, which will be introduced next in
the section 3.2. The final step, An, is always designated as F inish.
At each time step t, the agent updates G according to Equation (2):
Gt = π(Q | T | St) (2)
where π is the update policy (detailed in the Table 4), Q is the user query, T is the
set of available tools, and St is the historical record at time t, as Equation (3) shows:
St = (P1A1O1, P2A2O2, . . . , Pt−1At−1Ot−1) (3)
Here, Oi represents the observation from the execution of Ai. When t = 1, St is empty.
4
