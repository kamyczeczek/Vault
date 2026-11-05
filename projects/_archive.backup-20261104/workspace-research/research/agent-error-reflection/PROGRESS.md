---
type: Concept
title: PROGRESS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Research Progress — Agent Error Documentation, Reflection & Prevention

Evolving record of work. Updated as each phase completes.

- **Started:** 2026-09-15
- **Project:** projects/workspace-research
- **Goal:** Research scientific literature on LLM agents documenting encountered errors, reflecting on errors, and preventing recurrence; then reflect on findings using the project's graph-injected reflection pipeline.

## Phases

1. **Research** — locate and read primary papers; extract claims + evidence. ✅
2. **Corpus** — write findings as markdown chunks; rebuild knowledge graph. ✅
3. **Reflect** — graph-injected reflection agent; evolve this file with results. ✅

---

## 1. Research — five primary papers

| Paper | Chunk | Contribution |
|---|---|---|
| **Reflexion** (Shinn 2023, NeurIPS) | `01_reflexion_verbal_reinforcement` | Learn from failures by *verbal* reinforcement; policy is `{M_a, mem}`, not weights |
| **ExpeL** (Zhao 2024, AAAI) | `02_expel_experiential_insight_extraction` | Persist lessons across tasks; ADD/EDIT/UPVOTE/DOWNVOTE ledger evicts wrong insights |
| **AgentDebug** (Zhu 2025) | `03_agentdebug_root_cause_attribution` | Failures are a causal cascade; fix only the *critical* (root-cause) error |
| **Honest Lying** (Dixit 2026) | `04_honest_lying_memory_confabulation` | **The counterpoint:** the documented error can itself be false |
| **Self-Debug** (Chen 2023) | `05_self_debug_rubber_duck` | Rubber-duck explanation finds errors with *zero* external feedback |

Selection rationale: these five cover the full mechanism space — endogenous diagnosis with no signal (Self-Debug), with environment signal (Reflexion), with causality (AgentDebug), with persistence (ExpeL), and the failure of all of the above (Honest Lying). Each was read at full text, not abstract-only.

## 2. Corpus

Five chunks written to `knowledge/corpus/`, frontmatter `id`/`title`/`source`/`tags` per the project convention, then the graph rebuilt:

- fingerprint moved `17a3297a22fc → 9ca53157d727` (597 → 602 chunks)
- `.graph_fingerprint` matches live corpus; all 8 prior outputs re-stamped, gate still green
- all five new chunks queryable via tag intersection (`reflection` + `self-evolution`)

## 3. Reflect — the synthesis

**The finding that no single paper states alone:**

> An error-logging system is only recurrence-preventing if every stored lesson has **(a) provenance in environment evidence**, not agent self-narrative, and **(b) an eviction path**. (a) without (b) freezes a good lesson; (b) without (a) lets a confabulated one reinforce forever. Reflexion has neither; ExpeL has (b) only; Honest Lying proves (a) is the load-bearing half; AgentDebug supplies the granularity at which (a) is even extractable.

Supporting measurements, all cited to chunks:

- **0 of 121 reflections** mentioned the correct target object in 16 frozen ALFWorld environments — every reflection confabulated, RRR = 0.64 (`04_honest_lying_memory_confabulation`)
- grounding the diagnosis in environment signal moved correct-object mention **0% → 86%**, RRR **0.64 → 0.10** — but solved only 3 of 16, so grounding is necessary, not sufficient
- ungrounded vs grounded diagnosis costs **2–3% vs 12%** baseline gain (`05_self_debug_rubber_duck`)
- counterfactual root-cause detection reaches **24.3% vs 0.3%** all-correct vs baseline (`03_agentdebug_root_cause_attribution`)

**How this lands on the project:** this workspace's reflection stage already has (a) — every claim cites a chunk id, enforced by `check_reflection.py` — and the candidate ledger has (b) via `proposed → rejected`. The gap is the **determinism of the eviction trigger**: nothing decides when a stored lesson is stale except a human or a re-run. `04_honest_lying_memory_confabulation` is the only chunk co-tagged `reflection` + `determinism`, and it diagnoses that gap rather than closing it.

## 4. Outcome — four new candidates

Written to `reflection/candidates/agent-error-reflection.jsonl`, all `proposed`, all passing the provenance gate:

1. **`agent-error-reflection-1`** — the three-mechanism split (document / reflect / evict); most systems stop after step 2. *high impact*
2. **`agent-error-reflection-2`** — the documented error can be the error; grounding is load-bearing. *high impact*
3. **`agent-error-reflection-3`** — eviction must be deterministic, not human-only; RRR is the precedent. *medium*
4. **`agent-error-reflection-4`** — errors are a cascade; classify by taxonomy module and fix only the critical one. *medium*

**Reprioritized backlog:** the highest-leverage open item is no longer `P4`. It is closing the determinism gap in *eviction* — defining when a stored lesson is re-validated or evicted automatically. The corpus fingerprint move is the existing precedent in this project; RRR is the measurable signal from the literature. That converts the candidate ledger from human-triaged to self-correcting, which is exactly what the five papers agree is missing.

## 5. Process notes

- **The live spawn could not run.** `omp agent` hangs at the harness level — re-verified this session: `omp agent -p "PING_OK"` produced no output in 60s with no extension loaded. The spawn's own 200s timeout guard fired correctly and cleaned up its process tree. The reflection contract was executed in-process instead, using the spawn's exact deterministic tag-intersection routing and validated by the same gate. This matches the audit precedent already established for this workspace.
- **Corpus moves invalidate stamps by design.** Adding the five chunks moved the fingerprint and staled all 8 prior outputs. That is the P5 gate working as intended, not a defect — re-stamping is the correct response.
- **Gate count went 8 → 9 digests**, all grounded; manifest 41 rows / 602 chunks.


## 6. Pipeline built — phase 5 `05_evict` closes the loop

The research changed no process on its own — it produced corpus chunks, a digest, and four
*proposed* candidates. That was the gap: `stages/04_reflect/CONTEXT.md` declared itself
terminal ("Next consumer is not a stage"), but Reflexion's Algorithm 1 is a four-step loop
where the lesson is *acted upon*, and ExpeL has an explicit maintenance phase. Writing a
lesson is not the same as preventing recurrence.

**Answer to "did you change the workflow?":** the only workflow-adjacent edit in the research
commit was a pre-existing hardcoded-fingerprint bug in `stages/04_reflect/CONTEXT.md` (caught
by the stage-contract gate during re-stamping) — not a change flowing from the research. The
pipeline change came after, and it is this one:

`pipeline/WORKFLOW.md` now runs `01→02→03→04→05`. Phase 5 is **not optional**: a run that
stops at 4 has written lessons it never maintains.

| Artifact | Role |
|---|---|
| `stages/05_evict/CONTEXT.md` | Stage contract — document → reflect → **evict** |
| `scripts/evict_stale.py` | The action: reject candidates whose evidence ids no longer resolve in `graph.db` |
| `scripts/check_eviction.py` | The gate: proves every recorded rejection is grounded, not opinion |

**The deterministic trigger (closes `icm_reflection_determinism_gap`):** `.graph_fingerprint`
moves on every corpus edit, so a candidate whose `provenance.fingerprint` differs from live is
queued for re-validation. It is **rejected only if its evidence no longer resolves** — stale is
not the same as wrong. Previously nothing decided when a lesson was stale except a human or a
re-run; that was the exact gap the backlog named, and it now has a programmatic answer backed
by `04_honest_lying_memory_confabulation` (RRR as the measurable signal) and
`02_expel_experiential_insight_extraction` (DOWNVOTE-to-zero).

**Eviction is reversible, deletion is not.** Rejected rows stay in the file with `state: rejected`
and a `why` field, and `reflection/evictions/<run>.jsonl` is the audit trail — a rejected
candidate can be inspected and reinstated. Nothing is ever removed from the JSONL.

### Verification — both negative controls pass

The gate is not decorative; both failure paths were exercised against fabricated data:

1. **Eviction detects fabricated evidence.** Planted a candidate citing `99_does_not_exist_xyz`
   → `evict_stale.py` rejected it as `stale_evidence` and wrote an audit row.
2. **The gate catches an ungrounded eviction.** Fabricated an audit row rejecting over a chunk
   that *still resolves* in `graph.db` → `check_eviction.py` failed it:
   *"audit row rejects over ids that still resolve — that is an opinion eviction, not an
   evidence eviction."* This is the second-order confabulation the stage exists to prevent.

Control artifacts were removed after the test. A third consistency check also fired correctly:
deleting the negative-control candidate while leaving its audit row produced
*"audit row has no rejected candidate"* — the trail and the data must agree.

### Real defect found and fixed

The new gate surfaced two pre-existing legacy rejections with **no `why` field at all**
(`context-as-external-state.jsonl:9` → `C9`, `workspace-organization-audit.jsonl:2` →
`W-AUDIT-2`). Those were rejected before stage 5 existed and carried no cause. Their `why`
fields were backfilled rather than the gate loosened — the gate stays strict, the data gets fixed.

### Current state

57 candidates, 0 evictions, 0 revalidations pending — all evidence currently resolves, which is
the correct result for a corpus that has only grown. The eviction path is armed for the next
corpus edit that removes or renumbers a chunk.

### Gates (all rc=0)
```
scripts/check_stage_contracts.py   # 5 stage contracts — no hardcoded moving values
scripts/check_manifest.py          # manifest provenance
knowledge/graph/watch.py --once    # graph == corpus
scripts/check_reflection.py        # 9 digests / 9 candidate files — all grounded
scripts/check_eviction.py          # 2 rejected candidates / 0 audit rows — all grounded
```