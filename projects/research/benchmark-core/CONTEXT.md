---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — benchmark-core

One job: define the model interface, the evaluation protocol, and the rules that
make a benchmark number trustworthy.

## Inputs

- Working (this run): `members/<model>.py`, the runner script under test
- Reference (every run): `AGENTIC_DISCOVERY.md` — standing comparison table
- Reference (every run): `REFLECTION_PROMISING_METHODS.md` — what is promoted, frozen, or dead
- Reference (every run): `../../_archive/datasets/data/` — the series being evaluated

## Process

1. Read the model's own docstring for what it claims.
2. Fit on the training window only. Freeze parameters.
3. Predict the horizon. Never let a statistic from the prediction window reach
   the fit — scaling, normalization, and dictionary construction are all fit-time.
4. Score against the frozen baselines in `bench.py`.
5. Write metrics to `results/`, figures to `plots/`.

## Outputs

- `results/<experiment>.json` — per-task, per-origin metrics
- `results/<experiment>.md` — the human-readable summary
- `plots/<experiment>.png` — figures, generated from results, never hand-edited

## Human check

Read the results table and answer: does the model win on the task it was designed
for, and by how much relative to run-to-run variance? A win smaller than the std
across origins is not a win. Check the fit window in the log before believing any
number from a new runner.

## The model interface

Every file in `members/` exposes the same two entry points:

```python
def fit_<name>(history, **kwargs) -> Model
def pred_<name>(model, history, horizon) -> np.ndarray
```

Class-based members follow the same shape via `.fit()` / `.predict()`. A model
that cannot be expressed in this interface does not belong in `members/`.

## Evaluation protocol

- Rolling origins, not a single split. W=5 origins minimum.
- Frozen fit per origin; the fit is not repeated per horizon.
- Horizons are evaluated independently — no information flows from horizon h to
  horizon h+1.
- Chaos and sunspot tasks use the horizon-wise protocol in `chaos_protocol.py`
  and `sunspot_eval.py`; these are not interchangeable with the LTSF protocol.

## Significance

Paired forecasts are compared with `scripts/diebold_mariano_test.py`. A
p-value above 0.05 means the two models are indistinguishable on that data, and
the result should be written up that way. `AGENTIC_DISCOVERY.md` records several
models demoted on exactly this basis.

## Open work

Recorded 2026-09-27 by reading the code and the committed results, not the
roadmap. Items are what is *unfinished*, in the order that blocks a result from
being trusted.

### Unreproducible or unwired evidence

- **The BigDict standardization control does not reproduce.**
  `results/results_bigdict_std_control.json` carries `"repro_ok": false` and its
  own note says "directional control, not magnitude". Worse, its
  `std: "detail_only"` rows are numerically identical to the `std: "none"` rows
  on both tasks (thomas 0.5434, trending 1.8243), so the arm that was supposed
  to isolate detail-coefficient scaling is behaving like a no-op. Its verdict
  ("details intrinsically toxic") therefore rests on a control that is not
  isolating what it claims, and it contradicts the recommendation in
  `results_root_cause_analysis.md` §For Implementation.
- **`members/big_dict_lasso.py` has no result.** Its own docstring says the first
  experiment was hard to reproduce, and the file was rewritten (fixed-length
  anchored windows, train-window-only feature and target scaling, multi-task
  LASSO). No runner imports it, so `results_bigdict_lasso_final.md` and
  `results_ultimate_summary.md` Part 2 still report the *old* numbers
  (thomas_H24 0.7961) from the run that silently dropped 365 of 665 windows.
  Those two documents are stale until the new member is benchmarked.
- **RESOLVED 2026-09-27: `bench.py` loops over seeds.** `CLAUDE.md` §Rules
  requires mean ± std for anything stochastic; every committed number used to
  be one draw of the random BigDict/ESN dictionary. `bench.py --seeds N`
  (default 5) now re-runs the whole suite per seed and reports mean ± std for
  every pool, every member and every aggregate. Data generators keep their
  fixed seeds, so the spread measures the model and not the sample. Two
  further gates were added for the same reason: a win must clear the std of
  its own per-seed gap, and the BigDict gates must hold on *every* seed, not
  on an average that can hide one bad draw.
- **RESOLVED 2026-09-27: `harness.log` is committed.** `bench.py` writes it
  next to `results_s47.json`; the run that produced the committed artifact is
  now the log that ships with it, so the fit-window check this file's
  §Human check depends on can actually be performed.

  What the sweep settled: the subband family does **not** clear its own bar.
  Its win over Pool A is real and larger than its spread (−0.0249 ± 0.0147) and
  it wins the majority of tasks on every seed, but G2 fails on **every** seed:
  mean rank 2.225 ± 0.205 over 8 tasks against a threshold of 2.0. The verdict
  is REJECTED, unanimously. The BigDict arm is the opposite case: gap −0.2514 ±
  0.0205, mean rank 1.35 ± 0.16, 7/8 wins with zero variance, all BigDict gates
  true on all 5 seeds. So the subband promotion rested on a single draw whose
  rank happened to land under the bar; BigDict's margin is 12x its own spread.
- **Six members are imported by nothing.** `anchored_wavelet_elm`,
  `big_dict_lasso`, `new_big_dict_elm`, `signal_adaptive_bigdict`,
  `meta_ensemble_stacker`, and `members/bigdict_ablation` have no importer in
  any script. `signal_adaptive_bigdict` is the specific gap: the
  signal-adaptive-vs-fixed-compact head-to-head that would test whether routing
  adds value has not been run here, so the BigDict promotion rests on a fixed
  configuration.

### Dead decisions not carried out

- **The 2026-09-24 kill/archive list was never executed.**
  `REFLECTION_PROMISING_METHODS.md` §5 ends with
  `amr_dynamo_attractor.py` and `amr_tree_elm.py` frozen and
  `meta_ensemble_stacker.py` / `lasso_lag_mutation.py` moved to
  `members/_archive/`. `members/_archive/` does not exist and all four files are
  still in `members/`, still imported by `evaluate_multi_origin_sunspot.py` and
  others. The recorded verdicts and the tree disagree.

### Methodological gaps, unchanged

- **No multiplicity correction on the DM grid.**
  `scripts/diebold_mariano_test.py` thresholds raw p at 0.05/0.10 and emits
  significance stars. Across ~16 methods × several protocols this is the case
  where 5–10 "significant" wins appear at true parity. `results_dm_tests.json`
  carries no correction field.
- **The "real dataset" results are generated.**
  `results/real_datasets_metadata.json` and
  `results_comprehensive_real_datasets.json` cover `ETT_Load_Synthetic`,
  `Solar_Activity_SIDC`, `Weather_Temperature_Realistic`, `Financial_Returns_GARCH`,
  `Industrial_Sensor_A/B`. The first is labelled synthetic in its own name; the
  rest are produced by `../../_archive/datasets/new_datasets_catalog.py` and the metadata
  records only a `source` string — nothing marks them as generated. Every
  "beats real data" claim currently rests on synthetic series.
- **The financial thread is still in-sample.** The 60% directional-sign result
  on `log(AAPL) - log(SPY)` has no walk-forward split, no out-of-sample test and
  no DM comparison against buy-and-hold. The backtest scripts under this
  project produce plots only.

### Code defects blocking a run

- **`evaluate_adaptive_hybrid.py` cannot start.** It imports
  `new_datasets_catalog` at module level with no `sys.path` setup. Run from this
  project it fails with `ModuleNotFoundError: No module named
  'new_datasets_catalog'` (that module lives in `../../_archive/datasets`).
- **`bench.py --fev` cannot write its output.** Lines 468–469 write to
  `projects/ts-diverse/results/bench_{tag}.{json,log}`, a path from before the
  project was renamed. That directory does not exist in the workspace, so the
  run dies at the write. (`fev` is also not installed here.)

### Docs that will mislead the next session

- **`README.md` §Layout describes a project that no longer exists.** It lists a
  `tasks/` directory (absent) and describes `members/` as
  "NLinear, RFF, SubbandExpert, PooledELM" — none of which are member files;
  the directory holds 24 forecasters under different names.
- **`README.md` §Quick start undercounts the suite.** It says `bench.py` is a
  "7-task" mini suite and `AGENTIC_DISCOVERY.md` calls it 6 tasks;
  `bench.py`'s `TASKS` and `results_s47.json` both have 8
  (`tasks.evaluated == 8`).
- **Cross-project references read as local.** `AGENTIC_DISCOVERY.md` points at
  `LONGTERM_ETTH1_H720_DESIGN.md` and `SAB_L_H720_RESULT.md`, which live in
  `../etth1-h720/`, not here. `REFLECTION_PROMISING_METHODS.md` cites
  `HANDOFF.md` for a known-issue list; no such file exists in this project at
  all, in any sibling, or in `_archive/`.

### Out of scope but load-bearing

The ETTh1 H720 long-horizon line has moved to `../etth1-h720/`, which holds its
own `members/h2k.py`, `sab_l.py` and `amr_24_168.py`. The last result in this
project's `results/` for that line is H2K at 2.727 MAE against
`bigdict_elm` 2.4777, with 3/12 origins under the S44 incumbent 1.9781 — i.e.
it did not clear the bar. Whether it gets a second iteration or is killed is
decided in the sibling project, and nothing here re-runs it.
