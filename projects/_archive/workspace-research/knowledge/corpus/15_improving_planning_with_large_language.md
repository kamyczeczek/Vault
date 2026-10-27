---
type: Concept
id: 15_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 16/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
A.3 EXPERIMENTDETAILS
We implemented each of the modules using a separate GPT-4 (32K context, ‘2023-03-15-preview’
model index for ToH and cogeval tasks, and 128K context, ‘0125-preview‘ model index for strate-
gyQA and planbench tasks from Microsoft Azure openAI service) instance through a combination
of prompting and few-shot in-context examples. We set Top-p to 0 and temperature to 0, except for
theActor(as detailed in section A.7.2). TheSearchloop exploredB= 2branches recursively for
a depthL= 2.
For ToH, we used two randomly selected in-context examples of three-disk problems, and a de-
scription of the problem in the prompts for all the modules. For the graph traversal tasks, we used
two in-context examples for all modules, except for theActorandEvaluatorin the Steppath task,
where we used three in-context examples, one each for 2-, 3-, and 4-step paths. For strategyQA, we
didn’t use any in-context examples. For the logistics task from Planbench, we used two incontext
examples for all modules except forActorwhich used three in-context examples. For the mys-
tery blocksworld (deceptive) task from Planbench, we used two incontext examples for all modules
except forActorandPredictorwhich used three in-context examples. For both the tasks from
Planbench, we extracted the goal from the initial state conditions, and the state and the goal was
separately fed as input to the modules as required. The prompt also described the specific task that
was to be performed by each module (e.g., monitoring, task decomposition). For more details about
the prompts and specific procedures used for each module, see Section A.7.
For three-disk problems, we allowed a maximum ofT= 10actions per problem, and evaluated on
24 out of 26 possible problems (leaving out the two problems that were used as in-context examples
for theActor). We also evaluated on four-disk problems, for which we allowed a maximum of
T= 20actions per problem. The same three-disk problems were used as in-context examples,
meaning that the four-disk problems tested for out-of-distribution (OOD) generalization. For the
graph traversal tasks, we allowed a maximum ofT= 6actions per problem. For strategyQA we
allowedT= 1action per problem. For the Planbench tasks we allowed a maximum ofT= 4+
number of actions in the ground truth plan.
We didn’t use a separatePredictorfor the graph traversal tasks, since the action proposed by the
Actorgives the next state. We also did not include theTaskDecomposerfor these tasks, and did not
use theSearchloop for the Steppath task, as the model’s performance was already at ceiling without
the use of these components. For strategyQA we didn’t use theEvaluatoror theOrchestrator. For
the Planbench tasks we didn’t use tree search, and for mystery blocksworld task we didn’t use the
TaskDecomposer.
17
