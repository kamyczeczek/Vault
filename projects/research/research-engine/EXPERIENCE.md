---
type: Concept
title: EXPERIENCE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# EXPERIENCE.md — research-engine

Distilled on demand 2026-09-27 from `CONTEXT.md` Open work + `CLAUDE.md` Rules.
Each lesson names its evidence. Root links here (D11).

## Verified practices

1. **A proposal is a hypothesis with a parent and a change.**
   No entry into `benchmark-core/members/` without beating the incumbent on
   that project's protocol. Evidence: `CLAUDE.md` Rules; `CONTEXT.md` Process §4.
2. **A number that skips the leakage harness is void.**
   The harness checks, in order: no prediction-window statistic in the fit; no
   target-derived feature at fit time; no selection on test origins. A failure
   invalidates the run — fix the harness, not the number. Evidence:
   `CONTEXT.md` "The leakage harness".
3. **Evict stale reflections; never merge them.**
   Keeping a reflection whose evidence no longer resolves is how the index
   rots. Evidence: `CLAUDE.md` Rules. Counter-evidence the mechanism is dead:
   `evict_stale_reflections.py` keys on `importance`/`validated`, records
   carry neither — every record defaults to 1, nothing is ever evicted.
4. **Consolidate the query surface to one module.**
   Eight dead scripts (`query_graph_db`, `query_graph_nodes`, `query_kg`,
   `verify_with_kg`, `investigate_methodology`, `check_schema`,
   `read_kg_reflections`, `test_kg_query`) deleted; `kg.py`
   (`resolve`/`expand`/`resolve_and_expand`, read-only) + `eval_kg.py` vs LIKE
   baseline (structured family hit 1.0 vs 0.857). Evidence: Open work
   RESOLVED 2026-09-27.
5. **Repoint, don't restore, when the pre-split modules are gone.**
   `s47_ref/rolling_arm.py` runs again via interface-compatible imports from
   `benchmark-core/members/` + archived ETTh1 data at
   `projects/_archive/datasets/data/ETTh1_h1.csv`, failing loud when it is
   absent. Evidence: corrected S47 rerun, 2026-10-25.
6. **A gate with no margin rule flips on noise.**
   In the corrected select set, B's normalized-MAE edge is only 0.000866 on
   seasonal; A narrowly wins spiky (5.6e-6) and OU (0.000136). Keep these
   margins visible instead of treating task wins as equally robust.
7. **Settle a protocol variant with a rule written before the numbers.**
   Q9 (fixed vs expanding fit window) was decided by one stated rule — both
   policies must agree on the locked candidate and on every gate — and then
   run. They agree (0/6 winner flips), so the protocol stands and the variant
   is recorded as a sensitivity check. Deciding after seeing one number is how
   a gate becomes a preference. Evidence: `S47_DESIGN.md` Q9,
   `s47_ref/compare_window_policies.py`.

## Known-unresolved (do not promote yet)

- S-47's corrected 2026-10-25 rerun uses task-normalized MAE, mean rank,
  trailing-window refits, and select-only choice locking. G1-G3 pass and B is
  selected, but all five origins were exposed by the earlier run; G4 is
  diagnostic only and no candidate advances. Require a fresh, unexposed
  benchmark-core evaluation before promotion. Q9-Q11 are decided
  (2026-10-26): fixed 2000 is robust to an expanding window, the origin set is
  burned for confirmation, runtime is 26-56 s.
- Five of six S-47 tasks are synthetic. These results do not establish
  performance on unseen real tasks.
- `mutation_engine.py` runs but proposal quality open (stale `thomas_H24`
  task, `rff_h64` target is the worst member of an old run).
- `run_s47_suite.py` step 2 invokes missing `thomas_compare.py`;
  `sync_results_to_corpus.py` publishes `Slice: N/A`, `Suite: N/A`,
  hard-coded date — an empty record asserting a promotion.

## Skills used

None vendored (D8 lazy).
