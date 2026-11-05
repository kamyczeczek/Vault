---
type: Concept
id: 29_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 30/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
B = []
C = [0, 1, 2]
Answer: The current configuration doesn’t match the goal
configuration. Hence no.
Here is the task:
This is the current configuration:
A = []
B = [0, 1, 2]
C = []
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Answer:
A.7.7 ZERO-SHOT PROMPT
An example prompt for the GPT-4 zero-shot baseline is shown below:
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
33
