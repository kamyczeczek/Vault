---
type: Concept
id: ai-planning-htn-pddl
title: "HTN Planning and PDDL: Task Networks, Methods, Decomposition"
source: "ai_planning.txt HTN ch.4 + PDDL + HDDL (Holler AA AI20) + arXiv 2412.11642"
tags: [planning, htn, task-network, decomposition, pddl, hddl, icm, context-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

HTN planning targets an initial task network tn0, not a goal state. Tasks T = primitive (executable) U compound (decomposed via methods m=<c(m),tn(m)> where tn=<T',psi>). Decompose tn0 recursively until primitive network executable; fringe tasks executed or decomposed. Problem P_HTN=<Q,T,O,M,tn0,s0>; solution is primitive linearizable network. Restricted TSTN translates linearly to classical PDDL (Alford et al.), speeding FF by orders of magnitude. HDDL extends PDDL2.1 STRIPS with :htn, compound/primitive sets, VC, supported by PANDA/SAT/progression. Maps to spawn_recursive.py depth 1/2: topic -> topic__coTag leaves = HTN decomposition with SHARES_TAG methods; task_plan.md phases are task network.
