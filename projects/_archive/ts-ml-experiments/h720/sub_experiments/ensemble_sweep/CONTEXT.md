---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-Experiment: BalancedLagEnsembleKNN Hyperparameter Sweep ($H=720$)

## Purpose
Explore hyperparameter sensitivity of `BalancedLagEnsembleKNN` (16-expert
balanced-lag grid) on ETTh1 OT at horizon $H=720$: anchor window ($q$),
expert neighborhood size ($k$), recent-history truncation
(`history_fraction`), and a reduced fast-lags grid (no 168h weekly lags).

Protocol (locked, same as main leaderboard, via shared `data.py` split):
fit on all of `train.csv` (11,425 rows), forecast $H=720$, score against
the first 720 rows of `test.csv`. One identical chronological split for
every subexperiment.

## Directory Structure
- `CONTEXT.md` — this document
- `run_sweep.py` — reproducible sweep script (re-run: `python sub_experiments/ensemble_sweep/run_sweep.py`)
- `results.json` — metrics for all configurations + references
- `interactive.html` — Plotly ground truth vs best/worst/default forecasts

## Results
| Configuration | MAE | RMSE | $q$ | $k$ | History | Lag grid |
|---|---|---|---|---|---|---|
| `q6_k8_recent50` | **1.7639** | **2.1945** | 6 | 8 | Recent 50% | 16 experts |
| `q6_k8_full_fastlags` | 1.8077 | 2.2132 | 6 | 8 | Full | 6 fast-lag experts |
| `q12_k8_full` | 1.9976 | 2.3832 | 12 | 8 | Full | 16 experts |
| `q6_k16_full` | 2.0147 | 2.4208 | 6 | 16 | Full | 16 experts |
| `q24_k8_full` | 2.0236 | 2.4390 | 24 | 8 | Full | 16 experts |
| `q6_k8_full` (default) | 2.0333 | 2.4536 | 6 | 8 | Full | 16 experts |
| `q6_k4_full` | 2.0585 | 2.4882 | 6 | 4 | Full | 16 experts |
| `q3_k16_full` | 2.4267 | 2.8494 | 3 | 16 | Full | 16 experts |
| `q3_k8_full` | 2.5216 | 2.9585 | 3 | 8 | Full | 16 experts |
| `q3_k4_full` | 2.5717 | 3.0063 | 3 | 4 | Full | 16 experts |
| `q6_k8_recent10` | 3.0662 | 3.5667 | 6 | 8 | Recent 10% | 16 experts |
| `q6_k8_recent20` | 3.6974 | 4.0426 | 6 | 8 | Recent 20% | 16 experts |

References: daily 1.6720 / persistence 1.7952 / nlinear 2.3507.

## Key Findings
1. **Recent 50% is the sweet spot** — not full history. Truncating to the
   last 50% of origins drops MAE from 2.033 to **1.764** (−13%), beating
   persistence (1.795) and all linear models; only daily seasonal-naive
   (1.672) remains ahead. The 20%/10% windows are far worse (3.70/3.07):
   the tuning curve in `history_fraction` is non-monotone with an optimum
   near 0.5 on this split.
2. **Weekly (168h) lags hurt at H=720 on recent data**: dropping the ten
   168h-containing experts and keeping 6 fast-lag sets gives 1.808 full-
   history — nearly matching the best truncated run while training 10
   fewer experts.
3. **q=6..12 plateau**: anchor windows 6–24 all land 2.00–2.03 on full
   history; q=3 is uniformly ~0.5 MAE worse. More neighbors (16) helps
   slightly (2.015).
4. `q6_k8_recent50` ensemble is the best non-trivial model so far on this
   protocol; still behind the tuned `HeuristicLagKNN` k=32/q=3/recent-10%
   leaderboard entry (1.7204).

## Caveat
Single split (ETTh1 test window). The `history_fraction` optimum is
likely regime-dependent; confirm on validation split before promoting
`0.5` to the registry default.
