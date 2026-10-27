---
type: Concept
title: project-entropy
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Reflection Digest — project-entropy

## Provenance
fingerprint: 4880aab33ca4
# superseded_fingerprint: 31989e46d0a5
# superseded_fingerprint: 1f0d6e7e0b21
- plan_version: a4d9465d311f
- phase: 04_reflect, topic: project-entropy, date: 2026-09-30
- routing: deterministic tag-intersection via `ask.py` — query sets:
  - `{context-engineering, memory, planning}` ∩ `{context-engineering, icm, memory}` → cardinality 12/12
  - `{anti-leakage, reflection}` → 12; `{eviction}` → 1 (retry via `route.py --threshold 3` alias split recommended for depth 1)
- planner-selected chunks (executor read only these):
  `00_icm_implementation_pitfalls_and_failure_modes`, `00_a_complete_guide_to_managing_thousands_of_files`,
  `00_08_lesson_persistence_eviction_requirement`, `00_09_mistake_correction_abstraction_level`,
  `00_01_session_graph_research`, `00_defensive_failure_mode_hardening`, `00_06_self_correction_grounding_requirement`,
  `00_agent_memory_hierarchies`

## Claim
An agent project that only accumulates knowledge is not a project, it is a decay curve. Every stored artifact (lesson, rule, chunk) conditions future work by default and accrues an authority from having survived; without a removal mechanism the system converges to confidently-wrong state, not missing state.

## Evidence
- `00_08_lesson_persistence_eviction_requirement`: eviction is the mechanism that makes a stored lesson trustworthy; ExpeL evicts at score zero, and its own authors note the insight set grows **monotonically** — eviction solves wrong lessons, not volume. Two independent problems, two independent mechanisms (score-based eviction vs retrieval).
- `00_06_self_correction_grounding_requirement` (Huang et al., arXiv:2310.01798): intrinsic self-correction measurably degrades; the confidence a critique carries about itself is zero when critique and error share a distribution. Stored unverified critiques compound across trials (`04_honest_lying_memory_confabulation`, 0/121 reflections hit the correct object).
- `00_icm_implementation_pitfalls_and_failure_modes`: named ICM rot modes — silent promotion decay (write-only memory.md), fingerprint staleness deadlocks (additive corpus changes invalidate all prior digests), closed-vocabulary starvation (zero-hit `--tag` routes). All are entropy modes: state transitions without verification gates.
- `00_09_mistake_correction_abstraction_level`: recurrence prevention scales with abstraction level of stored unit (pattern > rule > instance). High-abstraction lessons persist longer without going stale; instance-level records rot fastest.
- `00_defensive_failure_mode_hardening`: unvalidated state transitions and ungrounded promotions are the primary degradation vector; `evict_stale.py` purges rules whose evidence IDs no longer resolve — evidence-based, not time-based.
- `00_a_complete_guide_to_managing_thousands_of_files`: four anti-rot layers (map, dated state, enforcement hooks, scheduled audit cadence); the agent reads two files, not the tree.
- `00_agent_memory_hierarchies`: write–manage–read loop; management is compression/consolidation, not just retrieval. `00_01_session_graph_research`: 5-phase: 04_reflect with `05_evict` as first-class stage.

## Decision
1. **Evict by evidence resolution, not by age.** Keep `evict_stale.py` as the hard gate: a rule whose cited chunk IDs no longer resolve is dead weight regardless of its correctness.
2. **Store at the highest abstraction level that survives verification.** Prefer pattern-level triples (failure condition → reason → correction) over instance records; instance records are disposable scaffolding, not memory.
3. **Treat monotonic growth as a defect, not a cost.** Volume and correctness are independent failure axes; a retrieval/cadence layer (audit + consolidation) must sit next to score-based eviction, per the two-mechanism requirement.
4. **Stamp-and-resolve on corpus change.** Additive ingest invalidates fingerprints; use guarded re-stamping so evidence validity is re-verified before plan stamps update, avoiding the stale-digest deadlock.

## Next bet
Run one audit cycle: `route.py` depth-1 retry for `{eviction}` (cardinality 1), then verify every accepted rule in `reflection/memory.md` still resolves against `graph.db` (fingerprint: 1f0d6e7e0b21). Predict: at least one accepted rule carries an evidence ID that no longer resolves — the write-only-loop symptom in `00_icm_implementation_pitfalls_and_failure_modes` mode 2. If zero stale rules found, the next entropy source is the digest itself: additive corpus changes re-stamp every digest, which is unbounded write traffic for bounded read value — propose re-stamp only on cited-ID resolution failure, not on any fingerprint change.
