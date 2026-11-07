---
flag: bigdict-lasso-rerun-stopped-2026-11-07
since: 2026-11-07
owner: mateusz
agent: dsh
model: cx/gpt-5.6-luna-low
---

# BigDict-LASSO rerun stopped — 2026-11-07

The documented BigDict-LASSO regeneration was started and intentionally stopped at the owner's request after the full 3-task × 10-arm grid proved much slower than the smoke estimate. The partial artifact is retained at `projects/research/benchmark-core/results/bigdict_lasso_rerun.json`; it contains complete results for `thomas_H24` and `seasonal_H48`, and partial progress for `multiscale_H96` (the process was stopped during that task). The console log is `projects/research/benchmark-core/run_bigdict_lasso_rerun.log`.

## Protocol and runner corrections made before the run

- The runner uses the declared frozen-fit W=5 rolling-origin protocol from `bench.py:320-330`: fit on `series[:2000]`, then score origins at `2000 + i*H` with a 96-step context.
- `BigDictLASSO.fit()` trains on delta targets (`values[e:e+H] - values[e-1]`) and `predict_hist()` returns the delta; the runner now re-adds the last context value before scoring. Without this correction, the initial smoke result was invalid (MAE 2.842 on thomas); after correction it was 0.004985 for approx alpha 0.01.
- `selected_features` now counts distinct feature columns with any nonzero coefficient, while `nonzero_coefficients` preserves coefficient-entry sparsity.
- The runner records convergence warnings, iteration counts, and `converged`; the grid emitted `ConvergenceWarning` for several low-alpha fits, so low-alpha results must not be presented as fully converged optima.
- `preflight.py` was corrected from the nonexistent `results/results_s47.json` to the actual committed evidence path `results_s47.json`; preflight then reported READY (0 hard missing). This is a real path correction, not a change to a gate.

## Results captured before stop

All values are MAE point estimates under the runner's protocol. `bigdict_elm_default` is the stock BigDictELM/Ridge arm, not the stale docs' undocumented “BigDict-Ridge (Opt)”.

### thomas_H24 (complete)

| arm | MAE | fit seconds | selected / width |
|---|---:|---:|---:|
| BigDictELM default | 0.005104 | 3.01 | — |
| compact α=.001 | 0.008984 | 90.45 | 70/672 |
| compact α=.01 | 0.014608 | 26.18 | 19/672 |
| compact α=.1 | 0.025188 | 3.97 | 15/672 |
| approx α=.001 | 0.002359 | 73.95 | 209/1440 |
| approx α=.01 | 0.004985 | 35.60 | 70/1440 |
| approx α=.1 | 0.012428 | 39.01 | 3/1440 |
| full α=.001 | 0.000439 | 189.29 | 93/1824 |
| full α=.01 | 0.002052 | 167.97 | 27/1824 |
| full α=.1 | 0.010709 | 50.17 | 4/1824 |

### seasonal_H48 (complete)

| arm | MAE | fit seconds | selected / width |
|---|---:|---:|---:|
| BigDictELM default | 0.132940 | 3.23 | — |
| compact α=.001 | 0.126709 | 171.88 | 219/672 |
| compact α=.01 | 0.128683 | 151.84 | 129/672 |
| compact α=.1 | 0.155015 | 104.74 | 62/672 |
| approx α=.001 | 0.127282 | 350.97 | 412/1440 |
| approx α=.01 | 0.130789 | 235.97 | 240/1440 |
| approx α=.1 | 0.155360 | 42.68 | 67/1440 |
| full α=.001 | 0.127303 | 448.17 | 531/1824 |
| full α=.01 | 0.130991 | 239.13 | 322/1824 |
| full α=.1 | 0.153026 | 74.99 | 79/1824 |

### multiscale_H96 (partial — 8/10 arms)

The artifact has `bigdict_elm_default`, compact α=.001/.01/.1, approx α=.001/.01/.1, and **full α=.001** recorded (8 of 10 arms). Missing: `full α=.01` and `full α=.1`. The process was re-run with the new `--resume` path (commit `0365dee` added `--resume`; this session completed `full α=.001` for multiscale and then the runner process exited before the two remaining heavy-light full arms were written) — so the multiscale task remains incomplete and must not be used as a final 3-task comparison until `full α=.01` and `full α=.1` are backfilled. `elapsed_seconds` for the partial artifact is 3880 s.

## Important conclusion / next step

The original “full grid ≈ 76s” smoke projection was wrong because it projected only the thomas smoke task and assumed comparable fit times. Seasonal fits reached ~448s and multiscale approx α=.001 reached ~703s; low-alpha fits also emitted convergence warnings. The planned three-task × ten-arm run was therefore not a bounded quick rerun. Do not update stale result documents with an incomplete grid. Next owner decision: either backfill the two missing multiscale full arms (`full α=.01`, `full α=.1`) to complete the 3-task grid, or use the complete two-task evidence (thomas_H24, seasonal_H48) plus a deliberately reduced, converged configuration.

The old documents remain stale and intentionally were not overwritten: `projects/research/benchmark-core/results_bigdict_lasso_final.md`, `projects/research/benchmark-core/results_ultimate_summary.md`, and `projects/research/benchmark-core/CONTEXT.md` still require an owner-approved evidence policy.

## Not checked

- multiscale_H96 is at 8/10 arms; the two missing heavy arms (`full α=.01`, `full α=.1`) need a targeted `--resume` backfill to complete the 3-task grid.
- The stale result documents were not rewritten because the 3-task evidence is incomplete.
- The `--resume` capability and this partial artifact are now committed and pushed for owner review; completing the grid remains the next run step.
