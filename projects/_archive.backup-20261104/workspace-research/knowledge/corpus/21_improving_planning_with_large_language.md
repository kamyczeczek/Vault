---
type: Concept
id: 21_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 22/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
A.7 PROMPTS ANDIN-CONTEXTEXAMPLES
A.7.1 TASKDECOMPOSER
For ToH, theTaskDecomposergenerated a single subgoal per problem. The in-context examples
included chain-of-thought reasoning (Wei et al., 2022b) based on the goal recursion strategy (Simon,
1975), which is sometimes provided to human participants in psychological studies of problem
solving (Carpenter et al., 1990). The specific prompt and in-context examples are shown below:
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
Goal: The goal is to generate a single subgoal from the current
configuration, that helps in reaching the goal configuration using
minimum number of moves.
To generate subgoal use the goal recursion strategy. First if the
smallest number isn’t at the correct position in list C, then set
the subgoal of moving the smallest number to its correct position
in list C.But before that, the numbers larger than the smallest
number and present in the same list as the smallest number must
be moved to a list other than list C. This subgoal is recursive
because in order to move the next smallest number to the list
other than list C, the numbers larger than the next smallest
number and present in the same list as the next smallest number
must be moved to a list different from the previous other list and
so on.
Note in the subgoal configuration all numbers should always be in
ascending order in all the three lists.
Here are two examples:
Example 1:
This is the current configuration:
A = [0,1]
B = [2]
C = []
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Answer:
I need to move 0 from list A to list C.
Step 1. Find the numbers to the right of 0 in list A. There is 1
to the right of 0.
Step 2. Find the numbers larger than 0 in list C. There are none.
I will move the numbers found in Step 1 and Step 2 to list B.
24
