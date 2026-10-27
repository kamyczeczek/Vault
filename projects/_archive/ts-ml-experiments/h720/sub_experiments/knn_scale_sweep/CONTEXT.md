---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# kNN Scale-Window × Weights Sweep — direction #1 for kNN family

**Directory**: `sub_experiments/knn_scale_sweep/` — `rolling_arm.py` (2,161 stride-1 origins, frozen fit on `train.csv` 11,425 rows, q=3 k=32 recent10% delays 1,2,3,6,12,24).

**Model**: `methods/knn_models.py` `HeuristicLagKNN` extended with `weights {uniform, distance 1/d, softmax exp(-d/σ)}` (σ = mean kNN distance across training). `scale_window` grid tests the scale-sensitive distance hypothesis (S-04: norm helps kNN strongly).

**Configs scored (rolling)**:
| Config | t0 MAE | Rolling MAE | Rolling RMSE | Note |
|--------|--------|-------------|--------------|------|
| knn_raw (no norm) | 1.7204 | 2.5583 | 3.0994 | baseline |
| knn_norm24 distance | 2.2438 | 2.4068 | 2.9176 | |
| knn_norm72 distance | 1.7061 | 2.4508 | 2.9728 | |
| knn_norm168 distance | 1.7909 | 2.4440 | 2.9532 | S-04 value |
| knn_norm336 distance | 1.6065 | 2.4050 | 2.9044 | |
| knn_norm720 distance | 1.7045 | 2.3815 | 2.8745 | S-04 best — reproduced |
| knn_norm1440 distance | 1.7170 | **2.3466** | 2.8347 | **new best kNN** |
| knn_norm720 uniform | 1.6966 | 2.3716 | 2.8628 | beats distance at 720 |
| knn_norm720 softmax | 1.7050 | 2.3862 | 2.8805 | |
| daily | — | 2.5491 | 3.1120 | anchor |
| persistence | — | 2.5985 | 3.1282 | anchor |

**Disjoint windows** (best knn_norm1440):
- W1 1.717 / W2 3.89 / W3 2.02 / W4 2.41 — W2 still fragile (4.90 → 3.89 improvement) but not eliminated.

**Gates**: `knn_raw 2.5583` and `knn_norm720 2.3815` reproduced 4-decimal, daily/persistence anchors OK.

**Findings**:
1. **Window 1440 beats 720** (2.3466 vs 2.3815, -1.5%) — longer trailing window helps kNN more than ELM; the S-04 “optimum 720” was not the ceiling. Uniform weighting at 720 (2.3716) also beats distance, suggesting `1/d` over-weights the nearest neighbour in noisy high-horizon regime.
2. Softmax `2.3862` does not help — global σ not the right scale; distance weighting remains best for most windows except 720 where uniform wins.
3. t0 ordering does not transfer (t0 best 336 1.6065 → rolling 2.4050; rolling best 1440 t0 1.717) — same rank flip as prior families.
4. Even best kNN 2.3466 still > hybrid 2.2265 > RBF 2.2812 > NLinear 2.0571 — kNN alone remains behind linear family, but as a *scaled* member it could improve cross-family ensembles.

**Next**: history-fraction × k joint grid (direction #2) or robust readout (direction #3).
