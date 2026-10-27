---
type: Concept
id: 20_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 21/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
Table 12: Results on ToH 3 disks with baselines also provided with the goal recursion strategy
(provided to theDecomposerof MAP).
Model % solved problems
GPT-4 Zero-shot 11
GPT-4 Zero-shot w/ goal recursion 23
GPT-4 ICL 46
GPT-4 ICL w/ goal recursion 46
GPT-4 CoT 42
GPT-4 CoT w/ goal recursion 50
MAP w/ goal recursion 74
Table 13: Results on Planbench with ToT on a subset of problems. Values within brackets indicate
best performance.
Model Logistics (30 problems) Mystery BW (100 problems)
ToT 10.4 (16.7) 0.6 (3)
MAP 53.3 35
Table 14: Results on ToH with 3 disks varying the tree search hyperparameters of MAP. Mean and
standard error are reported across 10 runs for computational cost and performance.
Model Num. calls Num. input tokens Num. output tokens % solved
MAP (B= 2, L= 1) 32.04±1.5 32,630.62±1,318.4 2,197.37±146.7 55±6
MAP (B= 2, L= 2) 43.46±2.4 49,537.37±2,563.7 2,727.55±214.2 72±2
MAP (B= 2, L= 3) 65.65±3.6 90,406.30±4,784.7 3,845.88±294.8 69±2
for these failures. The ‘incorrect decomposition’ failure mode was due to mistakes by the Decom-
poser (2/6 failures). The ‘no progress’ and ‘falling into loops’ failure modes were due to mistakes
made both by the Actor and the Evaluator. Specifically, the Actor sometimes failed to propose at
least one action that made progress toward the goal, and the Evaluator sometimes failed to select the
action that made progress toward the goal. The Actor and Evaluator made these mistakes at least
once for each of the 6 failures. Overall, we found that failures stemmed from errors made by the
Decomposer, Actor, and Evaluator modules, whereas the other modules (Monitor, Predictor, and
Orchestrator) performed perfectly.
Table 15: Results for number of failures (out of 6 total failures for a given run) of MAP on ToH with
3 disks for each of the three failure modes.
Incorrect decomposition No progress Falling into loops
2/6 6/6 5/6
23
