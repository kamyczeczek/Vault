---
type: Concept
id: 02_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 3/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
role via prompting and few-shot in-context learning (ICL). The resulting MAP algorithm (Algo-
rithm 1) is implemented via the recurrent interaction of these modules, combining the strengths of
classical planning and search algorithms with the use of LLMs as general-purpose world models
and planning functions.
We evaluate MAP on four challenging decision-making tasks that require planning and multi-step
reasoning. First, we performed controlled experiments on a set of graph traversal tasks according
to the CogEval protocol (Momennejad et al., 2023). These tasks require goal-directed navigation
in novel environments (MDPs) described in natural language, of which we selected an environment
that was most challenging for LLMs, including GPT-4. Second, we investigate Tower of Hanoi
(ToH), a classic problem solving task that requires multi-step planning (Simon, 1975). Third, we
investigate the two most challenging tasks in the PlanBench benchmark: mystery BlocksWorld and
Logistics (Valmeekam et al., 2023). Finally, we investigate a challenging NLP task that requires
multi-step reasoning, StrategyQA (Geva et al., 2021). We find that, when implemented with GPT-4,
MAP significantly improves performance on all four tasks (Figures 2 and 3, Tables 1 and 2), and
that the approach can also be effectively implemented with a smaller and more cost-efficient LLM
(Llama3-70B, Table 10). Transfer experiments further indicate that MAP displays an improved
ability to generalize between tasks, and ablation experiments indicate that each of the individual
modules plays an important role in the overall architecture’s performance (Figure 3). Taken together,
these results indicate the potential of a modular agentic approach to improve the reasoning and
planning capabilities of LLMs.
2 APPROACH
What follows first describes the functions performed by each MAP module, and then how they
interact to generate a plan.
2.1 MODULES
MAP contains the following specialized modules, each constructed from a separate LLM instance
through a combination of prompting and few-shot (≤3examples) in-context learning (described in
greater detail in section A.7):
•T askDecomposer. TheTaskDecomposerreceives the current statexand a goalyand gen-
erates a set of subgoalsZthat will allow the agent to gradually work toward its final goal. In the
present work, theTaskDecomposeris only utilized to generate a single intermediate goal, though
in future work we envision that it will be useful to generate a series of multiple subgoals.
•Actor. TheActorreceives the current statexand a subgoalzand proposesBpotential actions
A=a b=1 . . . ab=B. TheActorcan also receive feedbackϵfrom theMonitorabout its proposed
actions.
•Monitor. TheMonitorgates the actions proposed by theActorbased on their validity (e.g.,
whether they violate the rules of a task). It emits an assessment of validityσ, and also feedbackϵin
the event the action is deemed invalid.
•Predictor. ThePredictorreceives the current statexand a proposed actionaand predicts the
resulting next state˜x.
•Evaluator. TheEvaluatorreceives a next-state prediction˜xand produces an estimate of its
valuevin the context of goaly. This is accomplished by prompting theEvaluator(and demonstrat-
ing via a few in-context examples) to estimate the minimum number of steps required to reach the
goal (or subgoal) from the current state.
•Orchestrator. TheOrchestratorreceives the current statexand a subgoalzand emits an
assessmentΩof whether the subgoal has been achieved. When theOrchestratordetermines that
all subgoals (including the final goal) have been achieved, the plan is emitted to the environment as
a series of actions.
3
