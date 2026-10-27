# FEV protocol — benchmark-core

## Scope

Run the project's pool-blend forecasters on the real `fev-bench-mini` suite
(20 tasks) published by the `fev` package. Each task is a time series with
multiple rolling windows; the runner caps windows to 5 per task.

## Models / pools

- Pool A: `nlinear_a1`, `nlinear_a10`, `rff_h64`
- Pool B: Pool A + `subband_cA1`, `subband_d1`
- Pool C: Pool A + `wavelet_pooled` (when available)
- Pool I: Pool A + `knn_forecaster` (when available)

Per task, every model is fit on that window's own past (per-origin fit) and
scores that window's future. MAE is averaged over targets and windows.

## Metrics

- `meanA`, `meanB`, `meanC`, `meanI`: mean MAE across tasks per pool.
- `winsB`: number of tasks where Pool B MAE < Pool A MAE.
- `mean_rankB`: mean, over tasks, of Pool B's rank among {A, B, C, I}
  (1 = best). G2 requires `mean_rankB < 2.0`.

## Reporting

- Artifact: `bench_fev_mini.json` (+ `.log`) in the output directory.
- `data_source = "real"`, `confirmatory = True`.
- Verdict `PROMOTE subband` only if `meanB < meanA - 0.005` and G2 holds.

## G2 (pre-registered)

Pool B's mean rank across the 20 tasks is strictly below 2.0. A majority
win count alone is not sufficient.
