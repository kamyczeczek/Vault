---
type: Concept
id: 33_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 34/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
B = []
C = [0]
I need to move 1 from A to C. But before that I need to move the
number present to the right of 1, which is 2 to B.
Move 2 from A to B.
A = [1]
B = [2]
C = [0]
There is no number to the right of 1 in A, and there is no number
larger than 1 in C. Hence, I can move 1 from A to C.
Move 1 from A to C.
A = []
B = [2]
C = [0, 1]
There is no number to the right of 2 in B, and there is no number
larger than 2 in C. Hence, I can move 2 from B to C.
Move 2 from B to C.
A = []
B = []
C = [0, 1, 2]
Here is the task:
This is the starting configuration:
A = [0, 1, 2]
B = []
C = []
This is the goal configuration:
A = []
B = []
C = [0,1,2]
Give me the sequence of moves to solve the puzzle from the
starting configuration, updating the lists after each move.
Please try to use as few moves as possible, and make sure to
follow the rules listed above. Please limit your answer to a
maximum of 10 steps.
Please format your answer as below:
Step 1. Move <N> from <src> to <tgt>.
A = []
B = []
C = []
A.8 COMPUTATIONALCOST: THINKINGFAST AND(VERY) SLOW
Tables 16 and 17 show various cost metrics for both MAP vs. baseline models, and compares
these cost metrics with performance. To address the significant computational cost of MAP, we also
developed a more efficient version that cached and re-used results for redundant prompts. This was
done for all modules except theActorand theTaskDecomposer. This version of the model was
significantly more efficient, while retaining the same level of performance.
38

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
Table 16: Average per-problem computational cost (±the standard error of the mean) on ToH with
3 disks. 5 runs were done for MAP.
Model Num. calls Num. input tokens Num. output tokens % solved
GPT-4 ICL 1±0.0 810.88±0.1 190.38±15.4 46
GPT-4 CoT 1±0.0 1309.88±0.1 422.42±22.8 42
ToT 45.75±0.6 26649.88±454.0 7523.96±322.4 6
MAP 148.6±8.2 109,090.025±6,567.2 14,543.57±844.6 74±3
MAP (efficient) 41.99±3.6 47242.43±3848.4 2766.34±324.5 77±3
Table 17: Average per-problem computational cost (±the standard error of the mean) incurred by
each module of MAP on ToH with 3 disks.
Module Num. calls Num. input tokens Num. output tokens
Actor 24.68±1.5 38,274.62±2,796.8 758.69±54.1
Monitor 46.26±2.8 32,135.44±1,933.2 7,131.85±429.6
Predictor 29.48±1.6 11,284.65±601.3 477.48±25.7
Evaluator 22.52±1.2 17,054.15±917.6 5,730.11±334.3
Orchestrator 24.67±1.2 9,553.3±466.7 316.0±16.0
Task Decomposer 1±0.0 787.88±0.0 129.44 ± 2.0
39
