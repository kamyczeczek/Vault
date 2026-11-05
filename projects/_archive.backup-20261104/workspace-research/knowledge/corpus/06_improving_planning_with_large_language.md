---
type: Concept
id: 06_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 7/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
multiple LLM instances prompted to perform the same task. MAP’s superior performance relative
to ToT demonstrates that tree search, though an important part of the approach, is not sufficient to
explain MAP’s performance, and the other modules play an important role. For the problems that
MAP solved, the average plan length (5.4) was close to the optimal number of moves (4.4). The
model also demonstrated some ability to generalize out-of-distribution (OOD) to more complex 4-
disk problems (not observed in any in-context examples), whereas the baseline models solved close
to 0% of these problems. Notably, MAP did not propose any invalid actions, even on OOD 4-disk
problems, whereas the baselines proposed a significant number of invalid actions.
We also performed several experiments with ToH to better understand the MAP algorithm. First, we
investigated how MAP’s performance varied as a function of the depth of tree search. We found that
a depth ofL= 2provided the best tradeoff between performance and cost (Table 14). A depth of
L= 1resulted in worse performance, while a depth ofL= 3incurred greater cost without signifi-
cantly improving performance. Second, we investigated the extent to which MAP’s performance on
this task depended on being provided with an explicit strategy for task decomposition (the goal re-
cursion strategy). To address this, we provided the GPT-4 zero-shot, ICL, and CoT baselines with a
description of this strategy. We found that this strategy did improve baseline performance, but MAP
still outperformed these baselines even when they were provided with the strategy (Table 12). Third,
we investigated whether the computational costs of the MAP algorithm could be mitigated by using
a smaller LLM. We found that a version of MAP that used Llama3-70B still outperformed baselines
that used the same LLM, and even outperformed the best GPT-4 baseline, GPT-4 ICL (Table 10).
Table 1 shows the results for the PlanBench dataset, where MAP outperformed all of the baselines
that we considered. Notably, due to the complexity of the problems in this dataset, it was very costly
to perform tree search, so we evaluated a minimal version of MAP that did not involve tree search.
For this same reason, we were unable to evaluate a ToT baseline on the full set of problems, but
we include a comparison with ToT on a subset of problems in Table 13. Even without tree search,
MAP outperformed ToT. These results demonstrate that, although MAP certainly benefits from the
use of tree search, it can still provide significant performance benefits in domains where this is not
feasible. We also investigated a zero-shot version of MAP (without in-context examples) on the
most challenging PlanBench domain (mystery blocksworld), and found that it outperformed both
GPT-4 zero-shot and GPT-4 ICL (Table 11), suggesting that MAP can be useful even in settings
where in-context examples are not available.
Table 2 shows the results for the StrategyQA benchmark, where MAP outperformed both CoT and
ToT, and performed on par with human participants. This demonstrates the potential of MAP to
be beneficial in more real-world tasks, such as question-answering tasks that require multi-step
reasoning.
Table 1: PlanBench results.†
Model Logistics Mystery BW
GPT-4 Zero-shot 7 0.2
GPT-4 ICL 12 7.8
MAD 16.2 7.3
GPT-4 CoT 17 10.6
MAP 24 27.4
Table 2: StrategyQA results. †
Model Accuracy
ToT 81.7 † ±1.2
GPT-4 CoT 84.7±0.3
MAP 87.7±0.7
Human † 87.0
Finally, we performed transfer experiments to study whether few-shot in-context learning would
support generalization to different planning tasks. Table 3 shows the results for these experiments,
including results for transfer from planning on a smaller graph to planning on a larger graph (n7tree
→n15star), transfer to a semantically distinct but structurally isomorphic task (blocksworld (BW)
†Results reflect % solved problems for a single run.
†Results reflect accuracy on a fixed random subset of 100 questions averaged over 3 runs (±standard error).
†Yao et al. (2023) reported performance of 83%, but since the subset of 100 questions they used for eval-
uation is unknown, we ran ToT using the publicly released code on a fixed subset of 100 questions for fair
comparison with MAP.
†Geva et al. (2021) reported human performance on a random subset of 100 questions.
7
