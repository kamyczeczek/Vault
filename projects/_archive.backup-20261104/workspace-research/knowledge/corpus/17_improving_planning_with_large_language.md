---
type: Concept
id: 17_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 18/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
by varying the initial state (the initial positions of the numbers). This resulted in 26 three-disk
problems and 80 four-disk problems.
Initial state
Goal
Invalid moves
Initial state
Goal
A = [0, 1, 2]
B = [ ]
C = [ ]
A = [ ]
B = [ ]
C = [0, 1, 2]
Invalid moves
A = [0, 1, 2]
B = [ ]
C = [ ]
A = [1, 2]
B = [ ]
C = [0]
A = [0, 1]
B = [2]
C = [ ]
A = [0]
B = [2, 1]
C = [ ]
Figure 5:Tower of Hanoi. Top:Depiction of the Tower of Hanoi (ToH) puzzle. Disks are stacked
in order of decreasing size on the leftmost peg. The goal is to move these disks so that they are
stacked in order of decreasing size on the rightmost peg. Only the disk on the top of the stack may
be moved, and a disk can only be placed on top of larger disks (or on an empty peg). The version
shown involves three disks, but more disks can be used (making the task significantly more difficult).
Bottom:Modified text-based version of ToH. Three lists are presented, labelled A, B and C. A set of
integers is distributed amongst these lists. The goal is to move the numbers so that they are arranged
in ascending order in list C. Only the number at the end of the list may be moved, and a number can
only be placed in front of a smaller number. Multiple problem instances were created by varying the
initial state.
19

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
A.5 SUPPLEMENTARYRESULTS
ValuepathSteppathDetourReward Revaluation
Figure 6:Graph traversal results.‘% invalid’ indicates percentage of moves that are invalid (↓
better). GPT-4 Zero-shot, ICL, CoT, and MAD baselines are deterministic, and therefore a single run
was performed on all problems. Note that MAP did not employ tree search on the Steppath task, and
did not employ task decomposition on any of the graph traversal tasks. Without tree search, MAP’s
performance is deterministic, and therefore only a single run was performed on the Steppath task,
whereas we performed 5 runs with ToT. Gray error bars reflect 95% binomial confidence intervals
(for models evaluated on a single run). Dots reflect values of 0%. For Valuepath, Detour, and Reward
Revaluation we performed 10, 10, and 5 runs respectively with MAP and ToT, and present average
performance±the standard error of the mean (black error bars).
20
