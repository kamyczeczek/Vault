---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Stage 05_evict — Close the loop. Document → reflect → **evict**.

The reflection stage is terminal today: it writes lessons and stops. The five corpus chunks on agent
error (`01_reflexion_verbal_reinforcement` … `05_self_debug_rubber_duck`) agree that writing a lesson is
not the same as preventing recurrence. `04_honest_lying_memory_confabulation` measures what happens when
you stop: in 16 frozen ALFWorld environments **0 of 121 reflections mentioned the correct target object**,
and those reflections were *reused across trials* — a stored false belief, defended by the same memory that
was meant to correct it.

This stage is the missing half of the loop: it decides when a stored lesson is no longer trustworthy and
removes it. It is the mechanism `02_expel_experiential_insight_extraction` calls DOWNVOTE-to-zero eviction,
applied to this project's own candidate ledger.

## Budget
- `scripts/evict_stale.py` — one pass over `reflection/candidates/*.jsonl`. Runs in seconds; cost is
  bounded by candidate count (currently 12 open candidates), not corpus size.

## Inputs
- `reflection/candidates/*.jsonl` (the stored lessons — the memory being maintained)
- `knowledge/graph/graph.db` (ground truth: every evidence id must still resolve)
- `knowledge/graph/.graph_fingerprint` (the trigger signal — it moves on every corpus edit)
- `stages/05_evict/CONTEXT.md` (this file — single disclosure level)

## Outputs
- `reflection/candidates/<topic>.jsonl` — in place; stale rows transition `* → rejected`
- `reflection/evictions/<run-iso>.jsonl` — audit trail: what was rejected and why
- `reflection/digests/eviction-log.md` — human-readable summary, provenance-stamped

## Invoke
```
python scripts/evict_stale.py                    # evict ungrounded/stale candidates
python scripts/check_eviction.py                 # exit gate
python scripts/check_reflection.py               # re-verify all remaining candidates
```

## Contract
- **Grounding is load-bearing, not decorative.** A candidate whose evidence ids no longer resolve in
  `graph.db` is a lesson about a chunk that no longer exists — the exact `04_honest_lying` failure mode in
  this project's own terms. Such a row is `rejected`, state `stale_evidence`. Corroborated by
  `03_agentdebug_root_cause_attribution`: a document that describes a graph that no longer exists is a
  symptom being treated as a root cause.
- **The corpus move is the eviction trigger.** `.graph_fingerprint` changes on every corpus edit. A
  candidate whose `provenance.fingerprint` differs from the live fingerprint is *stale*, not automatically
  wrong — it is queued for re-validation, and rejected only if its evidence no longer resolves. This is
  the deterministic trigger the backlog called `icm_reflection_determinism_gap`: previously nothing decided
  when a lesson was stale except a human or a re-run.
- **Eviction is reversible, deletion is not.** Rejected rows stay in the file with `state: rejected` and a
  `why` field; they are never removed from the JSONL. `02_expel_experiential_insight_extraction` evicts at
  importance zero, and the same paper warns the insight set must remain inspectable as it grows.
- **No free recall.** Eviction is decided by id resolution against `graph.db` and fingerprint comparison —
  both programmatic. `04_honest_lying_memory_confabulation` shows why: replacing open-ended self-diagnosis
  with programmatic extraction of failure signals moved correct-object mention **0% → 86%** and RRR
  **0.64 → 0.10**. The lesson is to let the environment supply the signal, not the agent's self-narrative.
- **Critical-error discipline (`03_agentdebug`).** Only the *root cause* of a failure is worth evicting
  for; a downstream symptom being wrong does not invalidate the lesson. The script therefore distinguishes
  `stale_evidence` (ids no longer resolve — root cause of the candidate's grounding) from
  `superseded` (a later candidate on the same topic was accepted and contradicts it).
- **Determinism:** hash-gated on `knowledge/graph/.graph_fingerprint` + `pipeline/WORKFLOW.md` sha12.
  Both values move on every corpus/plan edit — read them live from those two files at gate time; never
  hardcode either value here, or this contract silently describes a graph that no longer exists.
- **Provenance:** eviction records embed `fingerprint + plan_version + phase + reason`, same stamp format
  as the digests they invalidate (P5). Missing provenance ⇒ gate failure.

## Handoff
Next consumer is `scripts/promote_candidate.py`: a candidate that survives eviction is eligible for
`proposed → experimental → accepted`. A rejected candidate's audit row in `reflection/evictions/` is the
handoff for post-mortem — the paper's own precedent is ExpeL's ledger, which remains queryable after eviction.
