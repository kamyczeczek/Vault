---
type: Concept
title: long_horizon_planning_decomposition_web_research
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Long-Horizon Planning and Recursive Decomposition

## Core concepts

Long-horizon planning fails when the planner tries to detail the full trajectory upfront. Recursive decomposition splits a task into subtasks only when the executor fails, which keeps planning cost proportional to actual difficulty rather than worst-case. The central insight: planning effort should track failure, not task size.

## Evidence from web sources

- ADAPT (2311.05772): decomposes only on failure. Success rates up to +28.3% in ALFWorld, +27% in WebShop, +33% in TextCraft versus strong plan-and-execute baselines. The mechanism is failure-triggered recursion, not pre-decomposition.
- Planning-with-files and file-based contracts: explicit stage contracts in files act as pre-committed sub-task interfaces. The executor cannot silently redefine the contract; the contract file is the stable handoff. This is a filesystem-level version of ADAPT's decomposition.
- Classical HTN/PDDL planning: hierarchical task networks pre-decompose everything, which is expensive when the hierarchy is wrong. LLM-based decomposition tends toward ad-hoc decomposition with no explicit re-composition contract. ADAPT's failure-triggered approach is a middle path.

## Why it matters for this workspace

The stage system is already a decomposition mechanism, but decomposition is static rather than failure-triggered. Adding explicit failure triggers between stages—where a failed check causes re-decomposition instead of halting—would make the pipeline adaptive in the ADAPT sense.

## Source

Web research: ADAPT, hierarchical task networks, planning-with-files stage contracts.
