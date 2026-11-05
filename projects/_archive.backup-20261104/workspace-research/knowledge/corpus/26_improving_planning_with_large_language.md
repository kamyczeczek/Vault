---
type: Concept
id: 26_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 27/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
B = [1]
C = [0, 2]
Proposed move:
Move 1 from list B to list A.
Answer:
A = [1]
B = []
C = [0, 2]
Here is the task:
This is the current configuration:
A = []
B = [0, 1]
C = [2]
Proposed move:
Move 1 from list B to list A.
Answer:
A.7.5 EVALUATOR
For theEvaluator, in the ToH task, GPT-4 was prompted to generate a heuristic function that could
be used to estimate the distance between the current state and the goal state. The description of this
heuristic function was then included in theEvaluator’s prompt. In the graph traversal tasks, we
used only in-context examples, with no heuristic function prompt.
The following text shows prompt and in-context examples used in the ToH task. The first User
message prompts GPT-4 to generate a heuristic function. After GPT-4’s response, another User
message prompts theEvaluatorto use this function:
USER:Consider the following puzzle problem:
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
Goal: The goal is to predict the minimum number of valid
moves required to reach the goal configuration from the current
configuration.
Here are two examples:
Example 1:
This is the current configuration:
A = [0, 1, 2]
B = []
C = []
30
