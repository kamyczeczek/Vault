---
type: Concept
id: 13_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 14/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
Shun Zhang, Zhenfang Chen, Yikang Shen, Mingyu Ding, Joshua B Tenenbaum, and Chuang Gan.
Planning with large language models for code generation.arXiv preprint arXiv:2303.05510,
2023b.
Yifei Zhou, Andrea Zanette, Jiayi Pan, Sergey Levine, and Aviral Kumar. Archer: Training language
model agents via hierarchical multi-turn rl.arXiv preprint arXiv:2402.19446, 2024.
14

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
A APPENDIX
A.1 SUPPLEMENTARYALGORITHMS
Algorithm 2:Action proposal loop.ProposeActiontakes a statexand a goalyand generatesB
potential actionsA=a b=1 . . . ab=B. This is implemented via a loop, in which theActorfirst proposes
potential actions, and theMonitorthen assesses those actions according to certain constraints (e.g., task
rules), providing feedback if any of the actions are deemed to be invalid. This continues until the proposed
actions are considered valid. See Sections A.7.2 and A.7.3 for more details.
FunctionProposeAction(x, y, B):
σ←false// Initialize validity
E← {}// Initialize feedback
whileσis falsedo
A←Actor(x, y, E, B)// Sample B actions
σ, ϵ←Monitor(x, A)// Determine validity and provide feedback
E←E∪ {ϵ}// Accumulate feedback
end
returnA
Algorithm 3:Search loop.Tree search with a depth ofLlayers, withBbranches at each layerl. For each
branch, a proposed action is sampled, and thePredictorpredicts the next state˜x. This process continues
recursively until the terminal layerL, at which point the valuev l=L of the terminal states is estimated by
theEvaluator. The values are backpropagated to their parent states in the first layer, and the action that
leads to the most valuable state is selected. In our implementation, we accelerate this process by caching
the actions and predicted states from deeper search layers and then reusing them in subsequent searches.
We also employ theOrchestratorto prematurely terminate search if the goal state is achieved.
FunctionSearch(l, L, B, x, y):
Vl ← {}// Initialize value record
˜Xl ← {}// Initialize next-state record
Al ←ProposeAction(x, y, B)// Propose B actions
forbin1. . . Bdo
˜xlb ←Predictor(x, Alb)// Predict next state
˜Xl ← ˜Xl ∪ {˜xlb}// Update next-state record
Ω←Orchestrator(˜xlb, y)// Terminate search if goal achieved
ifl < LandΩis falsethen
al+1,˜xl+1, vl+1 ←Search(l+ 1, L, B,˜xlb, y)// Advance search depth
Vl ←V l ∪ {vl+1}// Update value record
else
vlb ←Evaluator(˜xlb, y)// Evaluate predicted state
Vl ←V l ∪ {vlb}// Update value record
end
end
vl ←max(V l)// Maximum value (randomly sample if equal value)
al ←A largmax(V l) // Select action
˜xl ← ˜Xlargmax(Vl) // Predicted next-state
returna l,˜xl, vl
15
