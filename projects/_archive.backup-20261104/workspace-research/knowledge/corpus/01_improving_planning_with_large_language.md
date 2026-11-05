---
type: Concept
id: 01_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 2/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
Actor Monitor
Predictor
Environment
Evaluator
Task
Decomposer
States
SubgoalsGoals Actions
Proposed
actions
FeedbackAction
proposal
Predicted
states
Predicted
value
Search
Proposed
actions
Orchestrator
Subgoals
Modular Agentic Planner (MAP)
Predicted
states
Selection
Figure 1:Modular Agentic Planner (MAP).The agent receives states from the environment and
high-level goals. These are processed by a set of specialized LLM modules. TheTaskDecomposer
receives high-level goals and generates a series of subgoals. TheActorgenerates proposed actions
given a state and a subgoal. TheMonitorgates these proposed actions based on whether they violate
certain constraints (e.g., task rules) and provides feedback to theActor. ThePredictorpredicts the
next state given the current state and a proposed action. TheEvaluatoris used to estimate the value
of a predicted state. ThePredictorandEvaluatorare used together to perform tree search. The
Orchestratordetermines when each subgoal has been achieved, and when the final goal has been
achieved, at which point the plan is emitted to the environment as a series of actions.
This work raises the question of how LLMs might be improved so as to enable a capacity for plan-
ning, especially given the ubiquity of sequential decision making, reasoning, and planning problems
across the wide application of generative AI and LLMs.
Here, we take a step toward improving planning with LLMs, by taking inspiration from both cog-
nitive neuroscience and formal theories of decision-making and planning. In traditional theories of
planning, such as those found in the field of reinforcement learning (RL) (Sutton & Barto, 2018),
planning is carried out via the interaction of several specialized functions or modules, rather than
through the activity of a single, monolithic system. For instance, many approaches involve distinct
functions for action proposal, state evaluation, subgoal identification, or state prediction, many of
which have also been related to the function of specific brain regions (see Section 6 for discussion).
An interesting observation is that LLMs are often able to carry out these functions when probed
in isolation, but are unable to reliably integrate and orchestrate these capacities in the service of a
goal. For instance, Momennejad et al. (2023) noted that LLMs often attempt to traverse invalid or
hallucinated paths in planning problems (e.g., to move between rooms that are not connected), even
though they can correctly identify these paths as invalid when probed separately. This suggests the
possibility of an agentic approach using LLMs, in which planning is carried out through the coordi-
nated and recurrent interaction of multiple LLM modules, each of which is specialized to perform a
distinct process.
With this goal in mind, we propose the Modular Agentic Planner (MAP) (Figure 1), an agentic archi-
tecture composed of modules that are specialized to perform specific functions within the planning
process. Specifically, we have identified and implemented the following key modules: error moni-
toring, action proposal, state prediction, state evaluation, task decomposition, and task coordination.
Action proposal, state prediction, and state evaluation are further combined to perform tree search.
All modules are implemented using an LLM, which receives instructions describing the module’s
2
