---
type: Concept
id: 27_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 28/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Answer:
The minimum number of valid moves required to reach the goal
configuration from the current configuration is 7.
Example 2:
This is the current configuration:
A = [1, 2]
B = [0]
C = []
This is the goal configuration:
A = []
B = []
C = [0, 1, 2]
Answer:
The minimum number of valid moves required to reach the goal
configuration from the current configuration is 4.
What heuristic function can be used to estimate the minimum number
of valid moves required to reach the goal configuration from a
given current configuration?
GPT-4:A suitable heuristic function for this problem is the "sum
of the distances" heuristic. This heuristic estimates the minimum
number of valid moves required to reach the goal configuration by
calculating the sum of the distances each number needs to travel
to reach its final position in the goal configuration.
Here’s how the heuristic function works:
1. For each number in the current configuration, determine its
current position (list and index) and its goal position (list and
index) in the goal configuration.
2. Calculate the distance between the current position and the
goal position for each number. The distance can be calculated
as the absolute difference between the indices of the current and
goal positions, plus a penalty if the number needs to move to a
different list.
3. Sum the distances calculated in step 2 for all numbers.
The heuristic function will return the sum of the distances, which
is an estimate of the minimum number of valid moves required to
reach the goal configuration from the current configuration.
This heuristic is admissible because it never overestimates
the cost of reaching the goal configuration. It considers the
minimum number of moves required for each number to reach its goal
position, without taking into account the constraints imposed by
the rules of the puzzle. Therefore, the actual number of moves
required to reach the goal configuration will always be greater
than or equal to the heuristic value.
31
