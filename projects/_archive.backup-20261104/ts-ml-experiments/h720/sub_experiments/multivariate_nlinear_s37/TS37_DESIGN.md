---
type: Concept
title: TS37_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-37 DESIGN — Sparse Subset Multivariate NLinear
**Lane**: MEDIUM — multivariate expansion with sparse selection and channel dropout.
**Protocol**: S-20-clean (frozen train 8545 for val, refit 11425 for frozen test; chronological validation; 2161 rolling origins).

---

## 1. What & Why

### 1.1 The S-34 scar
S-34 added multivariate NLinear members over all 7 ETTh1 channels (OT + 6 exogenous: HUFL, HULL, MUFL, MULL, LUFL, LULL). Validation selected none of them: every multivariate member scored 3.77–38.91 MAE on val, while univariate members stayed around 2.89. The tabu search discarded the entire multivariate pool and picked the exact S-26 2-member univariate subset `[NLinear L336 a=1 + a=10]`. Frozen-test MAE was 1.9909 — identical to S-26.

Root cause: the multivariate members overfit validation cross-channel correlations. With all 7 channels in a dense linear readout, the ridge solution memorizes channel pairs that happen to correlate in the validation window but do not transfer to test.

### 1.2 S-37 fixes
1. **Sparse subset selection** — members are defined by explicit channel subsets, not full 7-channel windows. The pool enumerates small subsets: `[OT+HUFL, OT+LUFL, OT+all7]`. Ridge penalties alone are not enough; the channel set itself is part of the hyperparameter.
2. **Channel dropout during training** — each training forward pass randomly masks one exogenous channel with 30% probability. This forces the readout to be robust to missing channels and reduces cross-channel memorization.
3. **Validation-to-test transfer monitoring** — if a candidate improves held-out validation MAE but regresses frozen-test MAE by more than `0.01`, it is rejected regardless of validation score.
4. **Level-free via last-row subtraction** — all members subtract the last observed OT value from the window and from the prediction target, then re-add at predict time. This keeps the linear readout on bounded-delta inputs and prevents level leakage across channels.

---

## 2. Member Pool Specification

### 2.1 Univariate members (same as S-26)
| Name | Lookback | Ridge α | Channels |
|------|----------|---------|----------|
| `nlinear_L336_a1` | 336 | 1 | OT |
| `nlinear_L336_a10` | 336 | 10 | OT |

### 2.2 Multivariate members
All multivariate members use the same NLinear architecture over the selected channel window, level-free via last-row subtraction.

| Name | Lookback | Ridge α | Channels | Dropout |
|------|----------|---------|----------|---------|
| `mv_nlinear_L336_a1_ot_hufl` | 336 | 1 | OT, HUFL | 0.3 |
| `mv_nlinear_L336_a1_ot_lufl` | 336 | 1 | OT, LUFL | 0.3 |
| `mv_nlinear_L336_a1_ot_all7` | 336 | 1 | OT, HUFL, HULL, MUFL, MULL, LUFL, LULL | 0.3 |
| `mv_nlinear_L336_a10_ot_hufl` | 336 | 10 | OT, HUFL | 0.3 |
| `mv_nlinear_L336_a10_ot_lufl` | 336 | 10 | OT, LUFL | 0.3 |
| `mv_nlinear_L336_a10_ot_all7` | 336 | 10 | OT, HUFL, HULL, MUFL, MULL, LUFL, LULL | 0.3 |

Pool size: 2 univariate + 6 multivariate = **8 members**.

### 2.3 Channel dropout rule
During `fit()` on the training window, for each training batch/sample:
- With probability 0.7 keep all channels in the member's subset.
- With probability 0.3 zero out one randomly chosen exogenous channel in the subset (keep OT always present).

This is a training-time augmentation only; predict uses all channels.

### 2.4 Level-free implementation
- Anchor `a_t = OT_{t-1}` (last value in history).
- Input window for channel c: `X_c = window_c - a_t` (broadcast).
- Target for predict: predict deltas `Δ`, then return `Δ + a_t`.
- For multivariate subsets, anchor is still the OT last row; exogenous channels are demeaned by the same anchor for consistency.

---

## 3. Protocol (S-20-clean with sparse selection)

### 3.1 Data
- Train fit history: rows `0:8545` of `train.csv`.
- Validation region: rows `8545:11425` of `train.csv`.
- Chronological split for selection: `val[0:1080]` (fit stack) vs `val[1080:2161]` (held-out select).
- Frozen test refit: rows `0:11425` of `train.csv` (concatenated train+val).
- Test: first 2880 rows of `test.csv`.

### 3.2 Member fitting
- All members fit independently on train 8545.
- Multivariate members fit with channel dropout enabled.
- No intercept in the final stack head (same as S-20/S-26).

### 3.3 Stack selection
- Per-horizon single-output Ridge over member predictions: one coefficient set per horizon step `h`.
- 11-α grid: `[0.1, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000]`.
- Select α on held-out val half (`val[1080:2161]`) minimizing pooled MAE.
- Subset selection via tabu search over the 8-member pool (tabu length 5, max iterations 7).
- Disjoint-4 diagnostic computed after selection; does not drive selection.

### 3.4 Transfer check
After frozen-test refit:
- Compute `test_mae_full` and `test_mae_disjoint`.
- Compute `delta = test_mae_full - val_mae_full` where `val_mae_full` is the stacked score on all 2161 validation origins.
- If `delta > 0.01` ⇒ reject the candidate even if it beat S-26 on held-out.

---

## 4. Acceptance Criteria

- **Full MAE < 1.9909** (incumbent S-26).
- **Disjoint-4 MAE < 1.9696** (incumbent S-26).
- **Transfer delta ≤ 0.01** (val→test regression guard).
- **Anchor fidelity**: multivariate member singletons on the 2161 validation origins must reproduce within ±0.0005 of their in-harness training-time score.

All three must hold; otherwise **REJECT** and preserve S-26.

---

## 5. Close Condition

If after the full tabu search + 11-α scan no candidate satisfies all three acceptance criteria:
- Write `REJECTED` verdict to `results_s37.json`.
- Append S-37 findings to `CONTEXT.md`.
- Update `MONITORING/reflection/2026-09-12_s37_design.md`.
- Do NOT update the leaderboard; S-26 1.9909/2.4710 remains terminal.

If a candidate does satisfy all three:
- Promote it to the leaderboard with label `**NEW INCUMBENT S-37**`.
- Update `CONTEXT.md` leaderboard table.
- Update `MONITORING/reflection/...` with acceptance.

---

## 6. Implementation Notes for `rolling_arm.py`

- Reuse `member_preds_linear` from S-20 for univariate members.
- Add `fit_multivariate_member` that takes a channel-subset mask and applies channel dropout during fitting.
- Reuse `fit_stack_map` and `score_fast` / `score_full` from S-34 with modifications:
  - `score_fast` computes the held-out score on `val[n2:]`.
  - `score_full` computes the stacked score on all 2161 validation origins.
- Add `transfer_check(test_mae, val_mae)` returning `(pass, delta)`.
- The skeleton `rolling_arm.py` provides TODOs for each of these pieces; the actual fitter/predictor implementation in `methods/` is out of scope for this design ticket.
