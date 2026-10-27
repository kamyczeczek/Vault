---
type: Concept
id: 05_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 6/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
ValuepathSteppathDetourReward Revaluation
Figure 2:Graph traversal results.‘% solved’ indicates percentage of problems solved without
proposing invalid actions (↑better). GPT-4 Zero-shot, ICL, COT, and MAD baselines are determin-
istic, and therefore a single run was performed on all problems. Note that MAP did not employ tree
search on the Steppath task, and did not employ task decomposition on any of the graph traversal
tasks. Without tree search, MAP’s performance is deterministic, and therefore only a single run was
performed on the Steppath task, whereas we performed 5 runs with ToT. Gray error bars reflect 95%
binomial confidence intervals (for models evaluated on a single run). Dots reflect values of 0%. Dark
bars indicate average performance over multiple plans/runs. Light bars indicate best performance.
For Valuepath, Detour, and Reward Revaluation we performed 10, 10, and 5 runs respectively with
MAP and ToT, and present average performance±the standard error of the mean (black error bars).
Figure 3:Tower of Hanoi (ToH) results.‘% solved’ indicates percentage of problems solved
without proposing invalid actions (↑better). ‘% invalid’ indicates percentage of moves that are
invalid (↓better). Note that 4-disk problems are out-of-distribution (OOD). GPT-4 Zero-shot, ICL,
CoT, and MAD baselines are deterministic and reflect a single run. Gray error bars reflect 95%
binomial confidence intervals. Dots reflect values of 0%. Dark bars indicate average performance
over multiple plans/runs. Light bars indicate best performance. MAP results for 3-disk problems
reflect the average over 5 runs±the standard error of the mean (black error bars). MAP results for
4-disk problems reflect a single run, due to the high computational cost of multiple runs.
4 RESULTS
Figure 2 shows the results on the four graph traversal tasks (see Section A.5 for all results in tabular
form). On the Valuepath task, MAP solved 100% of problems, outperforming all baselines. On
the Steppath task, MAP displayed perfect performance for 2-step and 3-step paths, and near-perfect
performance for 4-step paths, again outperforming all baselines. MAP also outperformed all base-
lines on the Detour task, and performed on par with the baselines on the Reward Revaluation task
(while still outperforming GPT-4 zero-shot). This demonstrates that MAP can flexibly adjust to new
circumstances when generating plans. Finally, the model did not propose any invalid actions in any
of the four tasks (i.e., it did not hallucinate the presence of non-existent edges), due to the filtering
of invalid actions by theMonitor(Figure 6).
Figure 3 shows the results on Tower of Hanoi (ToH). MAP demonstrated a significant improvement
both in terms of the number of problems solved (left) and the number of invalid actions proposed
(right). On 3-disk problems, MAP yielded a nearly seven-fold improvement in the number of prob-
lems solved over zero-shot performance, and significantly outperformed standard in-context learning
(ICL), chain-of-thought (CoT), multi-agent debate (MAD), and tree-of-thought (ToT). When con-
sidering the best plan (out of 5 runs) for each problem, MAP achieved a perfect score of 100%.
MAP’s improved performance relative to MAD demonstrates the importance of interaction between
specializedLLM instances (i.e., a modular approach), whereas MAD involves interactions between
6
