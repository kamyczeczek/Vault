---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Hybrid MultiRateRBF — S-13 (user-selected #1)

**Directory**: `sub_experiments/hybrid_rbf_multirate/` — `rolling_arm.py` (2,161 stride-1 origins, frozen fit on `train.csv` 11,425 rows).

**Model**: `methods/multirate_rbf.py` `MultiRateRBF` — per-rate MaxPool views (S-10) + per-rate Gaussian RBF experts (S-11), mean ensemble. `rates=(1,)` ≡ `RBFELM` byte-identically (identity gate 0.0); `rates` must include 1; centers iid `RandomState(42)` sequential across rates, global σ = mean pairwise distance, Ridge readout.

**Configs scored (rolling)**:
| Config | t0 MAE | Rolling MAE | Rolling RMSE | Note |
|--------|--------|-------------|--------------|------|
| hybrid (1,) | 1.7271 | 2.2812 | 2.7684 | identity with RBFELM raw |
| hybrid (1,2) | 1.6450 | 2.2568 | 2.7460 | |
| hybrid (1,4) | 1.6249 | **2.2265** | 2.7186 | **best hybrid** |
| hybrid (1,2,4) | 1.6055 | 2.2338 | 2.7268 | main bet (S-10 winner rates) |
| hybrid (1,2,4,8) | 1.6539 | 2.2268 | 2.7235 | 8 doesn't hurt hybrid (unlike S-10) |
| RBFELM raw | — | 2.2812 | 2.7684 | parent |
| MultiRate (1,2,4) | — | 2.2744 | 2.7743 | parent |
| NLinear L336 | — | 2.0571 | 2.5071 | leader |

**Disjoint windows** (hybrid 1,4 best):
- W1 1.6249 / W2 1.5631 / W3 1.6333 / W4 2.4399 — W2 excellent, W4 weak (inherits multirate W4 drift; RBF alone W4 2.054). Hybrid (1,2) keeps RBF W4 2.07.

**Gates**: identity 0.0, determinism refit 0.0, shape 720, daily 2.5491 / persistence 2.5985 anchors OK (0.02 slack).

**Findings**:
1. Hybrid **beats both parents** (2.2265 vs 2.2744 vs 2.2812, -2.1% over best parent) — complementarity hypothesis confirmed at rolling mean, but **does not beat NLinear 2.0571** (-8.2% gap remains) and **loses to ELMTree 2.1706** — second-best ELM-family row, #8 overall behind NLinear/DLinear/RLinear/FITS×2.
2. S-10 rate-8 collapse does **not** transfer to hybrid (1,2,4,8 2.2268 ≈ 1,4 2.2265) — RBF experts tolerate coarser blocks better than tanh ELM experts.
3. W4 inversion persists: RBF W4 robustness is lost when rate 4 is included — hybrid trades W4 drift for W2 gain. Pure RBF W4 2.05 remains the drift-robust family champion (S-11).
4. t0 ordering does not transfer (t0 best 1,2,4 1.6055 → rolling 2.2338; rolling best 1,4 t0 1.6249) — third rank flip after S-08/S-09.

**Verdict**: Promising as *ELM-family refinement*, not as *leader challenger*. Next step is **linear-residual correction (direction #2)** if beating NLinear is the goal.
