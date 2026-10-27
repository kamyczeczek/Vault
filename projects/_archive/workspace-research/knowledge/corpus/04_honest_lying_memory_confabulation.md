---
type: Concept
id: 04_honest_lying_memory_confabulation
title: "Honest Lying: Understanding Memory Confabulation in Reflexive Agents"
source: "arxiv 2605.29463 (Dixit et al., 2026)"
tags: [reflection, agents, memory, self-evolution, anti-leakage, determinism]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Honest Lying — the documented error can itself be false, and then it never comes back the wrong way

**Core claim:** reflective memory does not merely fail to fix errors — it can *create* persistent ones.
Across ALFWorld and HumanEval, Reflexion-style agents write confident but incorrect interpretations of the
task into memory and keep acting on them across trials, even though the environment resets to the correct
task each time. The paper calls this **memory confabulation**: persistent, self-reinforcing false beliefs,
stored and reused despite contradictory evidence.

This is the direct counter-example to "document the error so it never comes back." If the *documentation* is
wrong, you have guaranteed the error's return rather than prevented it.

**Detecting it: Reflection Repetition Rate (RRR).** A log-based metric measuring repeated reliance on
incorrect reflective content. RRR=0.64 means the agent is re-reading its own wrong diagnosis most of the time.

**Measured severity:** 16 frozen ALFWorld environments where **0 of 121 reflections mentioned the correct
target object** — every reflection was confabulated, with no signal pointing at reality. 4 analogous cases
in HumanEval.

**The mitigation — constrain the diagnosis, don't trust it.** Replace open-ended self-diagnosis with
*programmatic extraction of trajectory-level failure signals*. The environment, not the agent's own
reasoning, supplies the error content. Result: correct-object mention 0% → 86%, RRR 0.64 → 0.10,
3 of 16 frozen environments solved.

**Design rule derived:** error documentation must be **grounded in environment evidence**, not in the
agent's self-narrative. An unconstrained reflection can fabricate a cause, and once fabricated it is stored,
retrieved, and defended — the agent becomes certain of a falsehood it wrote itself. The paper solves 3/16,
not 16/16, so grounding is necessary but not sufficient.

**Implication for any error-logging system:** a reflection ledger with no external check is a
confidence-amplifier. Every stored lesson needs either an environment-derived provenance or an eviction
mechanism (see `02_expel_experiential_insight_extraction`'s downvote-to-zero) — otherwise a false lesson
outlives the error it was written about.
