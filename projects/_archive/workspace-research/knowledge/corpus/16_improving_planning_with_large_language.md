---
type: Concept
id: 16_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 17/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
A.4 ADDITIONALDESCRIPTION OFPLANNINGTASKS
Graph Traversal.We focused on a particular type of graph (Figure 4) with community structure
(Schapiro et al., 2013) previously found to be challenging for a wide variety of LLMs. The first
task, Valuepath, involves finding the shortest path from a given room to the room with the largest
reward, while avoiding the room that has a smaller reward. A smaller reward and a larger reward
are located at two different positions in the graph. We fixed the two reward locations, and created
13 problems based on different starting locations. The second task, Steppath, involves finding the
shortest path between a pair of nodes. We evaluated problems with an optimal shortest path of 2,
3, or 4 steps. We generated 20 problems for each of these conditions by sampling different starting
and target locations.
The other two tasks, Detour and Reward Revaluation, involve modifications to the Valuepath task
that test for flexibility in planning. In these tasks, the problem description and in-context examples
for the Valuepath task are presented, and a single Valuepath problem is solved as in the original task.
The task is then modified in-context in one of two ways. In the Detour task, an edge is removed from
the graph and replaced with a new edge (e.g., ‘the door from room 1 to room 11 is locked and now
room 13 is connected to room 11’). In the Reward Revaluation task, the value associated with the
two reward locations is changed (e.g., ‘the reward of the chest in room 8 has been changed to 12 and
the reward of the chest in room 15 has been changed to 48’). As with the Valuepath task, the Detour
and Reward Revaluation tasks each involved 13 problems based on different starting locations.
9
12
3
6
15
8 2 11
14 5
4
10
1
7
13
Reward = 50
Reward = 109
12
3
6
15
8 2 11
14 5
4
10
1
7
13
Steppath Valuepath
Start
Goal
Start
Figure 4:Graph Traversal.We investigated two graph traversal tasks utilizing a challenging graph
with community structure.Steppath:Find shortest path between two nodes, e.g. node 3 and node
7.Valuepath:Find shortest path from starting location (e.g., node 10) to location with maximum
reward (node 8 in depicted example).
Tower of Hanoi.In the original version of the Tower of Hanoi (ToH) task, there are three pegs and
a set of disks of different sizes. The disks are stacked in order of decreasing size on the leftmost
peg. The goal is to move all disks to the rightmost peg, such that the disks are stacked in order of
decreasing size. There are a couple of rules that determine which moves are considered valid. First,
a disk can only be moved if it is at the top of its stack. Second, a disk can only be moved to the top
of another stack if it is smaller than the disks in that stack (or if the peg is empty). More complex
versions of the task can be created by using a larger number of disks.
We designed an alternative formulation of this task in which the inputs are text-based rather than
visual. In this alternative formulation, three lists (A, B, and C) are used instead of the three pegs,
and a set of numbers (0, 1, 2, and so on) is used instead of disks of different sizes. The goal is to
move all numbers so that they are arranged in ascending order in list C. The rules are isomorphic
to ToH. First, a number can only be moved if it is at the end of a list. Second, a number can only
be moved to the end of a new list if it is larger than all the numbers in that list. Note that although
this novel formulation is isomorphic to ToH (and equally complex), it does not share any surface
features with the original ToH puzzle (disks, pegs, etc.), and thus GPT-4 cannot rely on exposure to
descriptions of ToH in its training data to solve the problem. We created multiple problem instances
18
