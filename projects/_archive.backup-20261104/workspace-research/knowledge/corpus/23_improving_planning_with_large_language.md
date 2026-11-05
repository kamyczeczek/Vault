---
type: Concept
id: 23_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 24/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
This is the starting configuration:
A = [1]
B = [0]
C = [2]
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Here is the sequence of minimum number of moves to reach the goal
configuration from the starting configuration:
Move 2 from C to A.
A = [1, 2]
B = [0]
C = []
Move 0 from B to C.
A = [1, 2]
B = []
C = [0]
Move 2 from A to B.
A = [1]
B = [2]
C = [0]
Move 1 from A to C.
A = []
B = [2]
C = [0, 1]
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
A = [0]
B = [1, 2]
C = []
Give me only two different valid next moves possible from the
starting configuration that would help in reaching the goal
configuration using as few moves as possible.
Your answer should be in the format as below:
1. Move <N> from <src> to <trg>.
A.7.3 MONITOR
TheMonitorwas prompted with chain-of-thought reasoning in which each of the rules of the task
were checked before determining action validity. We stored the actions deemed valid by theMonitor
in a separate buffer, and we terminated the action proposal loop (Algorithm 2) when there were two
distinct actions in this buffer, or exceeded a maximum of 10 interactions with theMonitor. After
termination of the action proposal loop, if the buffer didn’t contain two distinct actions, we used the
27
