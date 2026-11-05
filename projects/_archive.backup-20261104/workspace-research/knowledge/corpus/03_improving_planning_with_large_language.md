---
type: Concept
id: 03_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 4/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
2.2 ACTIONPROPOSALLOOP
This section describes MAP’s algorithms, the first of which is the action proposal loop. TheActor
andMonitorinteract via theProposeActionfunction (Supplementary Algorithm 2). TheActor
proposes actions which are then gated by theMonitor. If theMonitordetermines that the actions
are invalid (e.g., they violate the rules of a task), feedback is provided to theActor, which then
proposes an alternative action.
2.3 TREESEARCH
ProposeActionis further embedded in aSearchloop (Supplementary Algorithm 3). The actions
emitted byProposeActionare passed to thePredictor, which predicts the states that will result
from these actions. A limited tree search is then performed, starting from the current state, and then
exploringBbranches recursively to a depth ofLlayers. Values are assigned to the terminal states of
this search by theEvaluator, and the action leading to the most valuable predicted state is selected.
Algorithm 1:Modular Agentic Planner (MAP).MAPtakes a statexand a goalyand generates a
planP, a series of actions with a maximum length ofT. TheTaskDecomposerfirst generates a set of
subgoalsZ. The agent then pursues each individual subgoalzin sequence, followed by the final goaly. At
each time step,Search(Algorithm 3) is called to generate an action and a predicted next-state. Actions are
added to the plan until theOrchestratordetermines that the goal has been achieved, or the plan reaches
the maximum lengthT.
FunctionMAP(x, y, T, L, B):
P←[]// Initialize plan
Z←TaskDecomposer(x, y)// Generate subgoals
forgin1. . .length(Z) + 1do
ifg≤length(Z)then
z←Z g // Update current subgoal
else
z←y// Final goal
end
Ω←Orchestrator(x, z)// Initialize subgoal assessment
whileΩis false andlength(P)< Tdo
a, x, v←Search(l= 1, L, B, x, z)// Perform search
P←P.append(a)// Update plan
Ω←Orchestrator(x, z)// Determine if subgoal is achieved
end
end
returnP
2.4 PLANGENERATION
Algorithm 1 describes the complete MAP algorithm. To generate a plan, theTaskDecomposer
component of MAP first generates a set of subgoals based on the final goal and current state. These
subgoals guide the search and are internally pursued one at a time, utilizing theSearchloop to
generate actions until theOrchestratordetermines that the subgoal has been achieved. The actions
are accumulated in a plan bufferPuntil either theOrchestratordetermines that the final goal has
been reached, or the maximum allowable number of actionsTare accumulated.
3 EXPERIMENTS
Experiment details are described in Section A.3. Code is available at:
https://github.com/MAPLLM/MAPICLR2025sub.
3.1 TASKS
Graph Traversal.We performed experiments on four multi-step planning tasks based on graph
traversal using the CogEval protocol (Momennejad et al., 2023). Natural language descriptions of a
4
