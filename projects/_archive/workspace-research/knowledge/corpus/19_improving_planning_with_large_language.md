---
type: Concept
id: 19_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 20/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
Table 8: Results on ToH. Note that we also include results here for the GPT-4 ICL baseline when
prompted with 5 ICL examples (as opposed to 2 examples in the standard version of the baseline).
Surprisingly, more ICL examples hurts performance on this task, perhaps due to overfitting to the
specific examples (Hasanbeig et al., 2023). Values within brackets indicate best performance.
Model % solved problems % invalid actions
3-disk 4-disk (OOD) 3-disk 4-disk (OOD)
GPT-4 Zero-shot 11 2 30 50
GPT-4 ICL 46 1 12 41
GPT-4 ICL (5 examples) 38 1 19 41
GPT-4 CoT 42 5 22 39
MAD 25 1 24 43
ToT-MAP 6 (25) 1(4) 4 5
ToT 6 (25) 0 (0) 14 11
MAP 74(100)24 0 0
Table 9: Ablation study on ToH with 3 disks. Values within brackets indicate best performance.
Model % solved problems % invalid actions
MAP 74(100) 0
w/o Task Decomposer 50 (67) 0
w/o Tree Search 32 (42) 0
w/o Monitor 27 (33) 31
Table 10: Results on ToH with 3 disks with a smaller LLM (Llama3-70B). MAP with Llama3-70B
even outperforms the best GPT-4 baseline (GPT-4 ICL).
Model % solved problems % invalid actions
Llama3-70B Zero-shot 19.2 33.8
Llama3-70B ICL 12.5 41.4
Llama3-70B CoT 29.2 33.3
GPT-4 ICL 46 12
Llama3-70B MAP 50 2
Table 11: Results on Mystery Blocksworld domain of PlanBench using a zero-shot version of MAP
(no in-context examples were provided for any module).
Model % solved problems
GPT-4 Zero-shot 0.2
GPT-4 ICL 7.8
MAP Zero-shot 8.2
A.6 ANALYSIS OFFAILUREMODES
To better understand the failure modes displayed by MAP, we analyzed the log files for the Tower of
Hanoi (ToH) task (3-disk problems, run accuracy=75%, failed to solve 6/24 problems). We identified
the following three general failure modes:
1. Incorrect decomposition: failure to identify subgoals that lie along the optimal path.
2. No progress: taking actions that either move away from or do not make progress toward a subgoal.
3. Falling into loops: visiting a state more than once.
These failure modes were not mutually exclusive. Table 15 shows the number of problems (out of 6
total failures) that involved these failure modes. We then identified which modules were responsible
22
