---
type: Concept
id: 32_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 33/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
I need to move 0 from A to C. There is a number larger than 0
already present in list C. Hence I first need to move 2 from C
to B.
Move 2 from C to B.
A = [0]
B = [1, 2]
C = []
There is no number to the right of 0 in A, and there is no number
larger than 0 in C. Hence, I can move 0 from A to C.
Move 0 from A to C.
A = []
B = [1, 2]
C = [0]
I need to move 1 from B to C. But before that I need to move the
number present to the right of 1, which is 2 to A.
Move 2 from B to A.
A = [2]
B = [1]
C = [0]
There is no number to the right of 1 in B, and there is no number
larger than 1 in C. Hence, I can move 1 from B to C.
Move 1 from B to C.
A = [2]
B = []
C = [0, 1]
There is no number to the right of 2 in A, and there is no number
larger than 2 in C. Hence, I can move 2 from A to C.
Move 2 from A to C.
A = []
B = []
C = [0, 1, 2]
Example 2:
This is the starting configuration:
A = [1]
B = [0]
C = [2]
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Here is the sequence of minimum number of moves along with
reasoning for each move to reach the goal configuration from the
starting configuration:
I need to move 0 from B to C. There is a number larger than 0
already present in list C. Hence I first need to move 2 from C
to A.
Move 2 from C to A.
A = [1, 2]
B = [0]
C = []
There is no number to the right of 0 in B, and there is no number
larger than 0 in C. Hence, I can move 0 from B to C.
Move 0 from B to C.
A = [1, 2]
37
