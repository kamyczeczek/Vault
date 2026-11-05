---
type: Concept
id: 24_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 25/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
only action in the buffer. If the buffer was empty, we used the action(s) proposed by theActorat
the last attempt. The following text was used as a prompt and in-context examples in the ToH task:
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
Goal: The goal is to check if the proposed move satisfies or
violates Rule #1 and Rule #2 and based on that if it is a valid
or invalid move.
Here are two examples:
Example 1:
This is the initial configuration:
A = []
B = [1]
C = [0, 2]
Proposed move:
Move 0 from C to B.
Answer:
First check whether the move satisfies or violates Rule #1. Index
of 0 in list C is 0. Length of list C is 2. The difference in
length of list C and index of 0 in list C is 2, which is not equal
to 1. Hence 0 is not at the rightmost end of list C, and the move
violates Rule #1.
Next check whether the move satisfies or violates Rule #2. For
that compute the maximum of list B, to which 0 is moved. Maximum
of list B is 1. 0 is not larger than 1. Hence the move violates
Rule #2.
Since the Move 0 from list C to list B violates both Rule #1 and
Rule #2, it is invalid.
Example 2:
This is the initial configuration:
A = []
B = [1]
C = [0, 2]
Proposed move:
Move 2 from C to B.
Answer:
First check whether the move satisfies or violates Rule #1. Index
of 2 in list C is 1. Length of list C is 2. The difference in
length of list C and index of 2 in list C is 1. Hence 2 is at the
rightmost end of list C, and the move satisfies Rule #1.
Next check whether the move satisfies or violates Rule #2. For
28
