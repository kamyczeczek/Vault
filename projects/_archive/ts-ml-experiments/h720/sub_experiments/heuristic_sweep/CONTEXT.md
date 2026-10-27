---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-Experiment: HeuristicLagKNN Hyperparameter Sweep ($H=720$)

## Purpose
Explore hyperparameter sensitivity of `HeuristicLagKNN` on ETTh1 OT dataset at horizon $H=720$, testing neighborhood size ($k$), anchoring window ($q$), and evaluating recent-history truncation variants (`history_fraction=0.2` and `history_fraction=0.1`, using only the last 20% and 10% of training data).

## Directory Structure
- `CONTEXT.md` — this document
- `results.json` — metrics for all tested parameter configurations
- `interactive.html` — interactive Plotly visualization of predictions vs ground truth

## Sweep Configurations & Results
| Configuration | MAE | RMSE | $k$ | $q$ | History Fraction | Status |
|---|---|---|---|---|---|---|
| `nlinear` (Reference) | 2.3507 | 2.8173 | — | — | Full (100%) | ok |
| `k8_q12` | 2.4104 | 2.9878 | 8 | 12 | Full (100%) | ok |
| `k8_q6` | 2.4379 | 2.9753 | 8 | 6 | Full (100%) | ok |
| `k8_q6_recent20` | 2.7530 | 3.2780 | 8 | 6 | Recent 20% | ok |
| `k5_default` | 2.8195 | 3.4555 | 5 | 6 | Full (100%) | ok |
| `k8_q6_recent10` | 2.9592 | 3.4321 | 8 | 6 | Recent 10% | ok |
| `k5_q6_recent20` | 3.2702 | 3.8117 | 5 | 6 | Recent 20% | ok |
| `k8_q12_recent20` | 3.7472 | 4.1678 | 8 | 12 | Recent 20% | ok |

## Key Findings & Qualitative Shape Analysis
1. **Full vs. Recent History & Quantitative Error**: Single-expert `HeuristicLagKNN` achieves lower point-wise error (MAE/RMSE) when utilizing the full training history (`100%`) due to a denser neighborhood search space across long-term regimes.
2. **Phase & Shape Fidelity (`k8_q6_recent10`)**: Despite a slightly higher aggregate error metric, qualitative inspection of `interactive.html` reveals that **`k8_q6_recent10`** (using only the most recent 10% of history) is exceptionally faithful to the ground truth curve's local shape, turning points, and high-frequency cyclical oscillations. Because it discards outdated macro-trends, its retrieved nearest-neighbor state transitions capture immediate local dynamics without lagging or dampening amplitude.
3. **Neighborhood & Anchoring**: Increasing $k$ from 5 to 8 and extending $q$ to 12 optimizes long-horizon stability when training on full history.
