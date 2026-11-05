---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# NLinear + KNN Residual Hybrid — S-16 (user proposal)

**Directory**: `sub_experiments/nlinear_knn_hybrid/` — `rolling_arm.py` (2,161 stride-1 origins, frozen fit `train.csv` 11,425).

**Model**: `methods/nlinear_knn.py` `NLinearKNNHybrid` — `NLinear L=336 ridge 1.0` frozen global baseline + `KNN` on residuals `R = Y - Ŷ_N` (raw space). `KNN` `q=3 k=32 MI lags 14,28,42,56,70 norm1440 EMA0.9 distance` (best kNN 2.2503). `α` weighting: `Ŷ = Ŷ_N + α·R̂_KNN`.

**Configs**:
| Config | t0 | Rolling MAE | Rolling RMSE | Note |
|--------|----|-------------|--------------|------|
| NLinear L336 | 2.3507 | **2.0571** | 2.5071 | leader |
| KNN MI EMA0.9 | 3.5848 | 2.2503 | 2.7431 | best kNN |
| Hybrid residual α=1.0 | 3.2237 | 2.3491 | 2.8977 | full residual hurts (+0.29) |
| Hybrid residual α=0.5 | 2.7223 | **2.1157** | 2.5797 | **½ residual beats kNN, #3 overall** |
| daily | — | 2.5491 | 3.1120 | anchor |
| persistence | — | 2.5985 | 3.1282 | anchor |

**Gates**: `NLinear 2.0571` and `KNN 2.2503` reproduced, `daily/persistence` anchors OK, shape 720.

**Findings**:
1. **Full residual (α=1) hurts** `2.3491` vs `KNN 2.2503` and `NLinear 2.0571` — `KNN` over-corrects `NLinear` globally; `t0` also `3.22` vs `2.35`.
2. **Half residual (α=0.5) helps**: `2.1157` beats `KNN 2.2503` by `0.13` and **beats `DLinear 2.1163`** by `0.0006`, landing `#3` behind `NLinear L336 2.0571` and `L96 2.0925`. First hybrid to crack top-3 since `S-06`.
3. Implication: `α` is the lever — `1.0` overfits residual, `0.5` regularises. Adaptive `α(X)=softmax(-d̄)` (distance-based trust, as proposed) should interpolate `2.1157` → `2.0571`.

**Next**: `α` sweep `0.25/0.5/0.75` and adaptive `α(d̄)` at `MI+EMA0.9` to close the `0.058` gap to `NLinear`.
