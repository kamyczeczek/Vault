---
type: Concept
id: 04_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 5/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
graph are provided with each node assigned to a room (e.g., ‘room 4 is connected to room 7’). The
tasks included Valuepath, involving finding the shortest path between a given room and the largest
of two possible rewards (but without going through the room with the smaller reward); Steppath,
involving finding the shortest path between two rooms; Detour, in which the Valuepath task is first
described, after which an edge is subsequently removed from the graph; and Reward Revaluation,
in which the Valuepath task is first described, and the value associated with two reward locations is
subsequently changed. Please see Section A.4 in the Appendix for more details.
Tower of Hanoi.We also investigated a classic multi-step planning task called the Tower of Hanoi
(ToH) (Figure 5). In the original task, there are three pegs and a set of disks of different sizes. The
disks must be moved into a particular goal configuration, while observing a set of constraints that
prevent simple solutions. In our experiments, we designed an alternative (but isomorphic) formula-
tion of this task in which the inputs are text-based rather than visual. This text-based formulation
made it possible to evaluate language models on the task, but it also resulted in a task that does
not share any surface features with the original task, making it unlikely that GPT-4 could rely on
exposure to descriptions of ToH in its training data to solve the problem. Please see Section A.4 in
the Appendix for more details.
PlanBench.To assess the generality and robustness of our approach, we also investigated a more ex-
tensive planning benchmark, PlanBench, consisting of synthetically generated problems in a number
of distinct domains. We specifically investigated the Logistics domain, involving the transportation
of goods between cities using airplanes and trucks, and the Mystery Blocksworld (deceptive) do-
main, which involves arbitrary names for entities and actions, and is the most challenging domain
in the dataset (more details can be found in Valmeekam et al. (2023)).
StrategyQA.Finally, to test the extent to which MAP can be applied to more real-world tasks, we
investigated StrategyQA, an NLP task that requires multi-step reasoning, and has proven challenging
for standard LLM methods (Geva et al., 2021). In this task, an unusual question is posed (e.g. ‘Did
Aristotle own a laptop?’) that requires multi-step reasoning. The question must be decomposed into
sub-questions which must be successively solved in order to arrive at a final answer (more details
can be found in Geva et al. (2021))
3.2 BASELINES
We compared our model to several baseline methods. The first method involved asking GPT-4 (zero-
shot) to provide the solution step by step. For the second method, in-context learning (ICL), we
provided GPT-4 with a few in-context examples of a complete solution. We provided two examples
for ToH, Valuepath, Detour, and Reward Reval, and three examples for Steppath (one each for 2, 3,
and 4 steps) and PlanBench. The third method was chain-of-thought (CoT) (Wei et al., 2022b). For
this method, the in-context examples were annotated with a series of intermediate computations that
break down the planning process into multiple steps (see Sections A.7.7-A.7.9 for example baseline
prompts). The fourth method was multi-agent debate (MAD), using the codebase from Du et al.
(2023). In this approach, similar to MAP, a solution is generated through the interaction between
multiple LLM instances (each instance was equivalent to the GPT-4 ICL baseline); however, unlike
MAP, these instances are not specialized to perform specific functions. Finally, we investigated tree-
of-thought (ToT), using the original codebase from Yao et al. (2023). Similar to MAP, ToT uses
multiple LLM modules to perform tree search, although MAP incorporates additional modules and
control processes (see Section A.2). To ensure that ToT was given the best chance of performing
well on our tasks, we tested two versions, one with prompts that were similar to those in the original
implementation (shown in the main results Section 4), and one that incorporated prompts from
MAP (ToT-MAP, see Appendix Table 8). For ToT, multiple potential plans are generated for each
problem, and a method is required to select one of these plans (a problem-specific heuristic was used
in the original work). To ensure a fair comparison, we evaluated using two metrics, 1) the best plan
(according to a groundtruth evaluation) for each problem, 2) the average performance of all plans
for each problem. We report both of these metrics for both ToT and MAP.
5
