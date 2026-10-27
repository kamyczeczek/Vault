---
type: Concept
id: 22_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 23/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
Hence I will move 1 from list A to list B. Also numbers should
be in ascending order in list B.
Subgoal:
A = [0]
B = [1, 2]
C = []
Example 2:
This is the current configuration:
A = [1]
B = [0]
C = [2]
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Answer:
I need to move 0 from list B to list C.
Step 1. Find the numbers to the right of 0 in list B. There are
none.
Step 2. Find the numbers larger than 0 in list C. There is 2
which is larger than 0.
I will move the numbers found in Step 1 and Step 2 to list A.
Hence, I will move 2 from list C to list A. Also numbers should
be in ascending order in list A.
Subgoal:
A = [1, 2]
B = [0]
C = []
Here is the task:
This is the current configuration:
A = [0, 1, 2]
B = []
C = []
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Answer:
A.7.2 ACTOR
TheActorwas prompted to proposeB= 2distinct actions. In some instances, theActorfailed
to propose two distinct actions. In those cases, we iteratively scaled the temperature by a factor of
0.1. This was done for a maximum of 10 attempts or until two distinct actions were produced. If
theActorwas not able to propose two distinct actions even after 10 attempts, we then used only a
single action. The specific prompt and in-context examples for the ToH task are shown below:
Consider the following puzzle problem:
Problem description:
- There are three lists labeled A, B, and C.
- There is a set of numbers distributed among those three lists.
- You can only move numbers from the rightmost end of one list to
25

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
the rightmost end of another list.
Rule #1: You can only move a number if it is at the rightmost end
of its current list.
Rule #2: You can only move a number to the rightmost end of a
list if it is larger than the other numbers in that list.
A move is valid if it satisfies both Rule #1 and Rule #2.
A move is invalid if it violates either Rule #1 or Rule #2.
Goal: The goal is to end up in the goal configuration using
minimum number of moves.
Here are two examples:
Example 1:
This is the starting configuration:
A = [0, 1]
B = [2]
C = []
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Here is the sequence of minimum number of moves to reach the goal
configuration from the starting configuration:
Move 2 from B to C.
A = [0, 1]
B = []
C = [2]
Move 1 from A to B.
A = [0]
B = [1]
C = [2]
Move 2 from C to B.
A = [0]
B = [1, 2]
C = []
Move 0 from A to C.
A = []
B = [1, 2]
C = [0]
Move 2 from B to A.
A = [2]
B = [1]
C = [0]
Move 1 from B to C.
A = [2]
B = []
C = [0, 1]
Move 2 from A to C.
A = []
B = []
C = [0, 1, 2]
Example 2:
26
