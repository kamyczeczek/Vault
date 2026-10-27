---
type: Concept
id: 30_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 31/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
A.7.8 ICLPROMPT
An example prompt for the GPT-4 ICL baseline is shown below:
Consider the following puzzle problem:
Problem description:
- There are three lists labeled A, B, and C.
- There is a set of numbers distributed among those three lists.
- You can only move numbers from the rightmost end of one list to
the rightmost end of another list.
Rule #1: You can only move a number if it is at the rightmost end
of its current list.
Rule #2: You can only move a number to the rightmost end of a
list if it is larger than the other numbers in that list.
A move is valid if it satisfies both Rule #1 and Rule #2.
A move is invalid if it violates either Rule #1 or Rule #2.
Goal: The goal is to end up in the configuration where all
numbers are in list C, in ascending order using minimum number
of moves.
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
34

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
B = []
C = [0, 1]
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
A = []
B = []
C = [0,1,2]
Give me the sequence of moves to solve the puzzle from the
starting configuration, updating the lists after each move.
Please try to use as few moves as possible, and make sure to
35
