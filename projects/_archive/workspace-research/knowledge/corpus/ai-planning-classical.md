---
type: Concept
id: ai-planning-classical
title: "Classical Planning: State Model, STRIPS, Search, Complexity"
source: "ai_planning.txt (Aiello & Georgievski, Introduction to AI Planning, Dec 2024) + arXiv 2412.11642"
tags: [planning, classical-planning, state-model, strips, search, complexity, icm, context-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Classical planning is search in a state-transition system under strong assumptions: finite, fully observable, deterministic, static world, goal satisfaction, sequential plans. From Shakey (1966) and STRIPS (1971). Model M=<S,s0,SG,A,delta> as labelled digraph; trajectory s0[a1]...[an] in SG. Example: keys/door with Inside/Owns/Locked booleans.

STRIPS/PDDL framing: P=<F,O,I,G> where F atoms, O operators <pre,add,del>, s'=(s U add(a))\\del(a). Complexity: PlanEx/PlanLen PSPACE-complete even bounded; delete-free NP-hard, no negative preconditions drops to P. Algorithms: forward-search (applicableActions, nondet choice), backward search, planning graphs. For ICM: task_plan.md phases are operators, completion is goal test G in s[pi]; route.py + spawn_recursive.py act as classical planner over corpus states.
