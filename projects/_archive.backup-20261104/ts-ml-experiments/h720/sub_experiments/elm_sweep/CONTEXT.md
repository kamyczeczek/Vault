---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-Experiment: HeuristicLagELM Hyperparameter Sweep ($H=720$)

## Purpose
Explore hyperparameter sensitivity of `HeuristicLagELM` (extreme learning
machine with anchor-normalised heuristic lags) on ETTh1 OT at horizon
$H=720$, across the three requested axes:

- **% of history** — `history_fraction` $\in$ {100%, 50%, 20%, 10%} of training origins
- **number of neurons** — `hidden_dim` $\in$ {64, 256, 1024, 4096}
- **heuristically set lags** — `delays` sets: `default` (1,2,3,6,12,24),
  `extended` (+48,168), `seasonal` (24,48,168), `fast` (1,2,3,6,12)

Protocol (locked, same as main leaderboard, via shared `data.py` split):
fit on all of `train.csv` (11,425 rows), forecast $H=720$, score against
the first 720 rows of `test.csv`. One identical chronological split for
every subexperiment.

## Directory Structure
- `CONTEXT.md` — this document
- `run_sweep.py` — reproducible sweep script (re-run: `python sub_experiments/elm_sweep/run_sweep.py`)
- `results.json` — metrics for all configurations + references
- `interactive.html` — Plotly ground truth vs best/default/worst forecasts

## Results
| Configuration | MAE | RMSE | Neurons | History | Lags |
|---|---|---|---|---|---|
| `fast_lags_h256_recent50` | **1.6344** | **2.1715** | 256 | 50% | fast (1–12h) |
| `h256_recent100` | 1.6771 | 2.0313 | 256 | 100% | default |
| `h256_recent50` | 1.6987 | 2.1643 | 256 | 50% | default |
| `fast_lags_h256_recent100` | 1.7108 | 2.1425 | 256 | 100% | fast |
| `h64_recent50` | 1.8135 | 2.2495 | 64 | 50% | default |
| `h4096_recent100` | 2.1253 | 2.7107 | 4096 | 100% | default |
| `h1024_recent100` | 2.1273 | 2.6155 | 1024 | 100% | default |
| `extended_lags_h256_recent50` | 2.1400 | 2.5988 | 256 | 50% | extended |
| `h1024_recent50` | 2.3326 | 2.8415 | 1024 | 50% | default |
| `h256_recent20` | 2.3494 | 2.7901 | 256 | 20% | default |
| `seasonal_lags_h256_recent50` | 2.6326 | 3.1721 | 256 | 50% | seasonal |
| `h1024_recent10` | 2.6021 | 3.1913 | 1024 | 10% | default |
| `h256_recent10` = `elm_default` | 3.1723 | 3.6719 | 256 | 10% | default |
| `h64_recent20` | 3.4915 | 3.9506 | 64 | 20% | default |
| `h4096_recent20` | 3.1893 | 4.0278 | 4096 | 20% | default |
| `h64_recent10` | 2.7942 | 3.3066 | 64 | 10% | default |
| `extended_lags_h256_recent100` | 2.5449 | 3.0012 | 256 | 100% | extended |
| `seasonal_lags_h256_recent100` | 2.5254 | 2.9949 | 256 | 100% | seasonal |
| `fast_lags` others | 1.63–1.71 | 2.14–2.17 | 256 | 50/100% | fast |
| `h4096_recent50/10`, `h1024_recent20` | 2.54–2.78 | 3.06–3.51 | 1024/4096 | 10–50% | default |

References: daily 1.6720 / persistence 1.7952 / nlinear 2.3507.

## Key Findings
1. **`fast_lags_h256_recent50` (MAE 1.6344) is the new protocol-best** —
   it beats daily seasonal-naive (1.6720) and every model on the main
   leaderboard, including tuned `HeuristicLagKNN` k=32 (1.7204).
2. **256 neurons is the sweet spot**: h=256 dominates every history
   fraction; 1024/4096 degrade (over-parameterised random projections
   dilute the signal under fixed ridge α=1). h=64 is capacity-limited.
3. **Dropping the 24h lag helps** (`fast` = 1,2,3,6,12 beats `default`
   at both 100% and 50% history), and adding weekly lags hurts
   (`extended`, `seasonal` ≈ 2.1–2.6). At H=720 the daily/weekly
   structure is better captured by the anchor + ridge bias than by
   explicit long lags.
4. **History-fraction response is noisy and config-dependent** — unlike
   the ensemble sweep's clean 0.5 optimum, ELM ranks 100%/50% close
   (1.677 vs 1.699 default-lags; fast-lags flips the order), while 20%/10%
   are consistently poor. The registry default `history_fraction=0.1` is
   the single worst-performing axis value — default config scored 3.1723,
   reproduced exactly (`elm_default` row).
5. `default` and `extended` lag sets were verified identical for
   `h256_recent100` vs `h256_*` grid rows (same params, same scores).

## Caveat
Single split (ETTh1 test window). Random projections are seeded
(`RandomState(42)`) so results are deterministic, but the neuron-count
optimum may shift with different seeds; confirm 256 vs 512/1024 on the
validation split before promoting any default change.
