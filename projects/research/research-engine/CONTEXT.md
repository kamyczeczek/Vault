---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — research-engine

One job: turn a corpus of literature and results into candidate architectures, and
prove each candidate honestly before it is allowed near the model library.

## Inputs

- Reference (every run): `../brain/` — the derived corpus and graph this reads
- Reference (every run): `../benchmark-core/CONTEXT.md` — the bar a candidate clears
- Working (this run): `s47_ref/` — the reference mini-suite
- Working (this run): `mutation_proposals.json` — the queue

## Process

1. **Discover.** `research_engine.py` reads the index and names model families
   that have not been tried. Nothing is invented here; the output is a shortlist
   with citations.
2. **Mutate.** `mutation_engine.py` applies heuristic variations to a seed model
   and writes a proposal. Every proposal records its parent and its change.
3. **Screen.** `AntiLeakageHarness` runs before any accuracy is reported.
4. **Hand off.** Proposals go to `../benchmark-core` for evaluation. This project
   does not score them.

## Outputs

- `mutation_proposals.json` — the queue, one record per proposal
- Query results written to the console, or into the corpus of whichever project
  the findings belong to. `sync_results_to_corpus.py` writes to the research
  loop's corpus; a result about this project belongs in this project's own index.
- Eviction records when stale reflections are dropped

## Human check

Read the proposal queue and ask: does each proposal state what it changed and what
evidence says the change should help? A proposal that cannot be justified from
the corpus is noise — delete it rather than evaluating it. Confirm the leakage
harness ran before believing any number attached to a proposal.

## The leakage harness

`AntiLeakageHarness` exists because a discovery engine reads the same corpus it
evaluates against. Design intent, in order:

1. No statistic from the prediction window reaches the fit — scaling, means,
   dictionary construction.
2. No target-derived feature is available at fit time.
3. Selection on early origins does not select on test origins.

Status 2026-09-27: the harness enforces all three — `folds()` asserts
disjoint train/validation geometry with embargo (C1), `check_window_isolation`
fails a fit whose predictions move under future perturbation (C1), `check_features`
rejects target-derived names and future-sensitive builders (C2),
`screened_decision` locks the choice on select origins before test origins are
scored (C3). Each check fails on a leaking fixture in `test_research_engine.py`
(5 passed). The `s47_ref/` scoring path runs through it: C1+C2 screen every fit
family up front (abort = non-zero exit, no results), C3 locks the per-task pool
choice on select origins with G4 test-origin confirmation. A number that skips
the harness is void.

A failure is not a warning. It invalidates the run, and the fix is in the harness,
not in the reported number.

## Open work

The project split out of `ts-diverse` broke more entry points than it fixed.
Verified by running each one (2026-09-27):

- **RESOLVED 2026-09-27: `s47_ref/rolling_arm.py` runs again.** The lost
  pre-split modules (`data.get_protocol_data`,
  `anchored_wavelet_elm_s46/`) are gone from the workspace, so the repair
  repoints rather than restores: `AnchoredWaveletELM` + `_ridge_multioutput`
  import from `../benchmark-core/members/` (interface-compatible: same
  constructor, `fit`/`predict`/`history_`), and the ETTh1 leg reads the
  canonical `../../_archive/datasets/data/ETTh1_h1.csv` OT column, failing loud when the
  fetch is absent. Fresh run (7.6s) reproduces the recorded verdict —
  PROMOTE subband family, G1/G2/G3 all true, wins 4/6 — and
  `results_s47.json` / `harness.log` are now a reproducible run, not a
  frozen one. Note: Pool C's `wavelet_pooled` is benchmark-core's graduated
  member, not the original S-46 code, so Pool C numbers are not comparable
  to the pre-split run; Pools A/B are self-contained and identical logic.
- **RESOLVED 2026-10-25: S-47 now refits and gates on select origins.**
  `rolling_arm.py` fits each member on the trailing 2000 points at each of
  five origins. The first three origins drive G1-G3; each select blend score
  uses Ridge weights fit on the other two select origins. The last two are
  scored only after the aggregate choice locks, with weights fit on all three
  select origins. MAE is normalized by the population std of the initial
  training window. Corrected result: select means A=1.084936, B=1.021247,
  C=1.085290; mean ranks A=2.167, B=1.500; B wins 4/6. G1-G3 pass and lock B.
  The post-lock G4 diagnostic is −0.077304 normalized, 4/6 wins. The prior run
  had already reported all five origins, so G4 is exposed and cannot establish
  confirmation; `all_binding=false`, no candidate advances.
- **S-47 task margins remain fragile.** On select-only normalized MAE, B's
  differences from A are +5.6e-6 on `spiky_H48`, +0.000136 on `ou_H24`, and
  −0.000866 on `seasonal_H48`. There is no minimum-margin gate, so origin
  variation can still change G3. The 2026-10-26 window-policy sensitivity
  (below) flipped none of these tasks, so the fragility is not a window
  artifact — it is a no-margin gate.
- **S-47 has no held-out-task test.** All six tasks contribute to the
  cross-task family choice, and five are synthetic. A fresh evaluation on
  unseen real tasks in `benchmark-core` is required before promotion.
- **S-47 never swapped in real `fev` data.** 5 of 6 tasks are the synthetic
  generators in `rolling_arm.py:28-56`; the fallback the design doc allows.
  `test_deterministic_targets.py` and `run_textbook_validated_experiment.py`
  are also dead: both `import members.*`, and `members/` lives in
  `../benchmark-core/`.
- **`mutation_engine.py` reads the wrong path — RESOLVED 2026-09-27.** It
  pointed at `Path("results_s47.json")` from the repo root, but the file is at
  `s47_ref/results_s47.json`, so it exited with "results_s47.json not found.
  Run `python bench.py` first." and there is no `bench.py` in this project. It
  now reads `s47_ref/results_s47.json` and runs. Still open, and separate from
  the entry point: proposal *quality*. `mutation_proposals.json` holds a
  `thomas_H24` proposal whose task is not in `TASKS`, and its `rff_h64` target
  records the *worst* member from an older run (MAE 0.662, where
  `subband_cA1` at 0.479 is the real spiky incumbent). A fresh run still
  reports `wavelet_pooled` as the worst incumbent on every task it scores,
  which is the same defect expressed as output rather than as a stale file.
- **`run_s47_suite.py` step 2 is a no-op failure.** It invokes a missing
  `thomas_compare.py`, and treats "s47 or thomas succeeded" as enough to
  re-sync. Run in a clean checkout today, `sync_results_to_corpus.py` writes a
  corpus file with `Slice: N/A`, `Suite: N/A`, no per-task table, and a
  hard-coded `Generated on: 2026-09-21` — it silently publishes an empty
  results record while asserting the subband family was promoted.
- **RESOLVED 2026-09-27: the KG query surface is one module.** The 8 dead
  scripts (`query_graph_db.py`, `query_graph_nodes.py`, `query_kg.py`,
  `verify_with_kg.py`, `investigate_methodology.py`, `check_schema.py`,
  `read_kg_reflections.py`, `test_kg_query.py`) are deleted; `kg.py` exposes
  `resolve` / `expand` / `resolve_and_expand` over the ARL graph read-only,
  and `eval_kg.py` scores them against a LIKE baseline (latest:
  structured family hit rate 1.0 vs baseline 0.857, all arms consistency
  1.0, log in `evals/`). `mutation_engine.py` now reads
  `s47_ref/results_s47.json` and runs. Remaining below is untouched.
- **`evict_stale_reflections.py` cannot evict anything.** It keys on
  `importance` and `validated`, but the 9 records in
  `../../_archive/agentic-research-lab/reflection/candidates/*.jsonl` carry `id`, `state`,
  `Rule`, `Evidence`, `Action`, `Target`, `provenance` and no importance field —
  so `record.get("importance", 1)` defaults to 1 for every record. The contract's
  third rule ("stale reflections are evicted, not merged") has no working
  mechanism behind it.
- **RESOLVED 2026-10-25: S-47 protocol correction and rerun.** The runner now
  refits each model on the trailing 2000 observations at each of five origins,
  computes G1-G3 from the first three select origins with task-normalized MAE
  and mean rank, and locks the aggregate choice before scoring the last two.
  The harness checks origin geometry, feature declarations, and disjoint fit /
  score origins; `test_research_engine.py` passes 12 tests, including the
  window-policy cases added 2026-10-26. The 55.2s corrected
  rerun passes G1-G3 and selects B. Its G4 result is diagnostic only: the
  earlier run had already exposed all five origins, so no candidate advances.
  See `s47_ref/S47_DESIGN.md` and `s47_ref/results_s47.json`.

- **RESOLVED 2026-10-26: S-47 Q9-Q11.** Q9 (fit window): the rule was written
  before the sensitivity numbers — both policies must agree on the locked
  candidate and on G1-G3. They do: locked choice B, wins 4/6, identical ranks,
  and 0/6 per-task winner flips, so fixed trailing 2000 stays the protocol and
  expanding is a recorded check (`results_s47_expanding.json`,
  `python s47_ref/compare_window_policies.py` exits 0). Q10 (origin reuse): the
  five W=5 origins are burned for confirmation, so this suite cannot promote
  anything; a promotion decision needs new origins or new tasks in
  `benchmark-core`. Q11 (runtime): 26.7 s fixed / 26.2 s expanding on
  2026-10-26, 55.2 s recorded earlier — inside the `<5 min` target.

Next: run a fresh, unexposed evaluation in `benchmark-core` on unseen real
tasks before making a promotion decision. Five of the six S-47 tasks are
synthetic, so this rerun does not establish real-task generalization.
