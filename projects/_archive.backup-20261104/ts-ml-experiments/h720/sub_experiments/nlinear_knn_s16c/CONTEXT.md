---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-16c — Validation-Correct α*/k Selection (S-02 Protocol)

**Split**: train `8,545` / val `2,880` / test `2,880` (`data.py` `TRAIN_END=8,545`, `VAL_END=11,425`). Fit `NLinear L336 ridge1` + `KNN_R` on `train 8,545` only, validate on `val 2,880` rolling `2,161` origins, then freeze best on `fit_history 11,425` and score on `test`.

**Frozen**: `NLinear L336`, residual `R=Y-Ŷ_N`, `MI 14,28,42,56,70`, `EMA 0.9`, `norm1440`, `10k` residual database.

**Validation grid**: `k {16,32,48,64}` × fixed `α {0.05,0.10,0.15,0.20}` + analytical `α* = clip(Σ e·r / Σ r², 0,1)`.

**Results on val (2,880 rolling)**:
| k | α* (analytical) | Fixed α 0.05 | 0.10 | 0.15 | 0.20 | Best on val |
|---|-----------------|--------------|------|------|------|-------------|
| 16 | **0.0000** | 2.8981 | 2.9013 | 2.9067 | 2.9140 | **α*=0.0 2.8970** |
| 32 | **0.0000** | 2.8982 | 2.9012 | 2.9060 | 2.9124 | **α*=0.0 2.8970** |
| 48 | **0.0000** | 2.8983 | 2.9013 | 2.9059 | 2.9121 | **α*=0.0 2.8970** |
| 64 | **0.0000** | 2.8984 | 2.9013 | 2.9057 | 2.9116 | **α*=0.0 2.8970** |

All `α* = 0.0` (numer `Σ e·r` negative: `-168k` to `-219k` / denom `4.2M–5.9M`), clipped to `0`.

**Frozen test (full train 11,425 → test 2,880)**:
- `NLinear` on test: **2.0571 / 2.5071**
- Frozen best (`k16 α*=0.0`): **2.0571 / 2.5071**, `W4 1.9626`, `Δ 0.0000`
- Conclusion: validation says **no KNN contribution** (`α=0`).

**Interpretation**:
1. `S-16b` `2.0546` at `α=0.1` was **test-selected** — optimistically biased, as warned. Validation-correct selection gives `α*=0.0` (KNN residual variance > signal on `val`).
2. `Σ e·r < 0` for all `k` means `KNN_R` is **negatively correlated** with `NLinear`'s error on `val` — the small `test` gain was search noise on the `70-row` leaderboard, exactly the selection bias warned about in the prior discussion.
3. `k` not the lever: `0.05` best fixed across `k`, all within `0.003`.

**Next**: If pursuing `NLinear+KNN`, the only remaining lever is **distance-weighted residual** (`w_i=1/(d+ε)`) already in `HeuristicLagKNN` `weights=distance` — but S-16c shows even that has `α*=0`.
