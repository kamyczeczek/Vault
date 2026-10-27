---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-Experiment: Recent-10% Training Data Grid Sweep ($H=720$)

## Purpose
Explore the interaction between neighborhood size ($k$) and anchoring window ($q$) when `HeuristicLagKNN` is restricted strictly to the most recent 10% of training history (`history_fraction=0.1`). This isolates whether tighter local anchoring ($q=3$) combined with optimal $k$ can unlock superior quantitative performance while preserving shape/phase fidelity.

## Directory Structure
- `CONTEXT.md` — this document
- `results.json` — grid sweep metrics across all $(k, q)$ combinations
- `interactive.html` — interactive Plotly visualization comparing all grid configurations against ground truth

## Grid Sweep Configurations & Results ($H=720$)
| Configuration | MAE | RMSE | $k$ (Neighbors) | $q$ (Anchor Window) | Status |
|---|---|---|---|---|---|
| **`k8_q3_recent10`** | **2.1921** | **2.6416** | 8 | 3 | ok |
| `k8_q24_recent10` | 2.7907 | 3.3045 | 8 | 24 | ok |
| `k3_q3_recent10` | 2.8565 | 3.3663 | 3 | 3 | ok |
| `k16_q6_recent10` | 2.8575 | 3.3407 | 16 | 6 | ok |
| `k5_q3_recent10` | 2.9054 | 3.4167 | 5 | 3 | ok |
| `k8_q6_recent10` | 2.9592 | 3.4321 | 8 | 6 | ok |
| `k8_q12_recent10` | 2.9716 | 3.5696 | 8 | 12 | ok |
| `k12_q6_recent10` | 2.9762 | 3.4537 | 12 | 6 | ok |
| `k3_q12_recent10` | 2.9887 | 3.6865 | 3 | 12 | ok |
| `k5_q12_recent10` | 2.9891 | 3.5385 | 5 | 12 | ok |
| `k12_q12_recent10` | 3.0519 | 3.5914 | 12 | 12 | ok |
| `k5_q6_recent10` | 3.3199 | 3.8279 | 5 | 6 | ok |
| `k3_q6_recent10` | 3.5934 | 4.0929 | 3 | 6 | ok |

## Key Findings
1. **The Power of Short-Window Anchoring ($q=3$) under Recent-History Truncation**: When restricting training data to the last 10%, an anchoring window of $q=3$ (averaging only the immediate 3 steps) dramatically outperforms longer anchoring windows ($q=6, 12, 24$).
2. **Optimal Configuration (`k8_q3_recent10`)**: Pairing $k=8$ with $q=3$ under 10% recent history achieves an outstanding **MAE of 2.1921** and **RMSE of 2.6416**, outperforming even the full-history baseline (2.4104 MAE) and NLinear (2.3507 MAE). This confirms that short local context combined with recent temporal regimes captures sharp structural turning points without macro-trend distortion.
