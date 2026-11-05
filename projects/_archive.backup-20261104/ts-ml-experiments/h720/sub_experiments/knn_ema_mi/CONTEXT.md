---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# kNN EMA Anchor × MI Lags — Heuristic vs FNN/MI

**Directory**: `sub_experiments/knn_ema_mi/` — `rolling_arm.py` (2,161 stride-1 origins, frozen fit `train.csv` 11,425 rows, q=3 k=32 recent10% norm1440 distance, weights distance).

**Model**: `HeuristicLagKNN` with `ema_alpha` (EMA anchor `α·x_t+(1-α)·EMA_{t-1}`, `α∈{0.9,0.7,0.5,0.3}` vs SMA `q=3`) × lags `heuristic (1,2,3,6,12,24)` vs `MI (14,28,42,56,70)` from S-09 (`τ=14,m=5` via AMI/FNN).

**Results (rolling MAE)**:
| Config | t0 | Rolling | Note |
|--------|----|---------|------|
| heur SMA q3 | 1.717 | 2.3466 | prior best kNN (S-14) |
| heur EMA 0.9 | 1.830 | 2.3287 | EMA helps heuristic (-0.018) |
| heur EMA 0.7 | 1.735 | 2.3361 | |
| heur EMA 0.5 | 1.666 | 2.3454 | |
| heur EMA 0.3 | 1.935 | 2.3521 | |
| **mi SMA q3** | 3.965 | **2.2610** | MI beats heuristic by 0.085 |
| **mi EMA 0.9** | 3.584 | **2.2503** | **new best kNN** (-0.010 vs MI SMA) |
| mi EMA 0.7 | 3.774 | 2.2565 | |
| mi EMA 0.5 | 3.965 | 2.2669 | |
| mi EMA 0.3 | 3.834 | 2.2847 | |
| daily | — | 2.5491 | anchor |
| persistence | — | 2.5985 | anchor |

**Findings**:
1. **MI lags beat heuristic for kNN** (2.2610 vs 2.3466, -3.6%) — *inverts* S-09 ELM finding where `fast 2.88` beat `MI 3.74 (+29%)` with same lags but ridge readout. For kNN (geometry, not ridge), sparse 14h grid captures MI-optimal delays better than dense recent grid. `t0` vs rolling flip is extreme: MI `t0 3.96` worst → rolling `2.26` best.
2. **EMA helps both lag sets** — heuristic `SMA 2.3466 → EMA0.9 2.3287 (-0.018)`, MI `2.2610 → 2.2503 (-0.011)`. `α=0.9` (half-life ~6.5h) best for both — recent level still dominates, but EMA smooths vs boxcar SMA(3).
3. **New kNN ceiling 2.2503** is still `+9.4%` vs `NLinear 2.0571` and `+3.6%` vs `ELMTree 2.1706`, but now `hybrid 2.2265` is only `0.023` ahead — kNN with MI+EMA is ELM-family competitive (#7 overall, best kNN ever).
4. **Next tinker**: MI lags at `norm1440` only — test other `scale_window` (1000/2000) and `k {24,48}` at MI lags, and `history 5%/20%` at MI+EMA 0.9.

**Gates**: heur SMA 2.3466 reproduced, daily/persistence anchors OK, shape 720.
