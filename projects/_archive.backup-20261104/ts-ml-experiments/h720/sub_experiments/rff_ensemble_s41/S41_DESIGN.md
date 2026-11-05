---
type: Concept
title: S41_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-41 — RFF-MoE: Random Fourier Feature Expert Ensemble for ETTh1 H=720

**Lane:** FRONTIER — new architecture, non-linear readout via RFF, zero-tuning router.
**Status:** DESIGN / skeleton implementation.
**Protocol:** S-20-clean (train 8545 fit, val 1080/1081 split, test 11425 refit, 2161 rolling origins).
**Target:** full MAE < 1.9909 and disjoint-4 MAE < 1.9696 vs S-26 incumbent.

---

## 1. Expert Pool (4 experts)

All experts are Ridge regressors on deterministic, fixed feature views.

### Expert 1 — NLinear-L336-a1 (anchor-differenced L336 window)
- **View:** last-value-anchored L336 window → feature vector length 336.
- **Model:** Ridge α=1, intercept=True, predict + anchor back-add.
- **Rationale:** S-26 incumbent member; captures medium-term linear structure.

### Expert 2 — NLinear-L336-a10 (anchor-differenced L336 window)
- Same view as Expert 1, stronger shrinkage.
- **Rationale:** S-26 incumbent member; pairs with a1 for diversity in regularization strength.

### Expert 3 — RFF-L336 (raw L336 window → Random Fourier Features → Ridge)
- **View:** raw L336 window (no anchor subtraction) → RFF projection → D=500 random Fourier features.
- **Model:** Ridge α=1, intercept=False on φ vector; predict output is horizon-wide vector fit per origin.
- **Rationale:** RFF is a KERNEL method approximation, not just a linear model. Mapping to high-dim space via random sinusoidal projections enables the linear readout to capture nonlinear structure in the raw window. S-35 failed because RF was on deltas, not raw window — RFF operates on the raw window, avoiding the delta trap.

### Expert 4 — Calendar-RFF-L336 (raw L336 window + calendar features → RFF → Ridge)
- **View:** raw L336 window concatenated with 7-dim calendar features [hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos, holiday] → RFF projection → D=500 random Fourier features.
- **Model:** Ridge α=1, intercept=False on φ vector; predict output is horizon-wide vector fit per origin.
- **Rationale:** Calendar features feed into RFF expert, not linear, avoiding the S-40 collapse where calendar-aware linear members reduced to OT-only combinations. RFF can exploit the nonlinear interaction between calendar phase and raw window values.

---

## 2. Feature Encoder Spec

### RFF Projection (Experts 3 & 4)
- **Input dimension (Expert 3):** L=336 (raw window)
- **Input dimension (Expert 4):** L=336 + 7 = 343 (raw window + calendar features)
- **Output dimension:** D=500 random Fourier features
- **Random seed:** 42 (fixed, deterministic)
- **Projection:** φ(x) = sqrt(2/D) * cos(Wx + b), where W ~ N(0, σ²I), b ~ Uniform(0, 2π), σ = 1.0 / gamma, gamma = 1/input_dim (median heuristic)
- **No learned encoder:** RFF weights are sampled once from fixed seed and frozen.

### Calendar Features (Expert 4 only)
- Source: precomputed `calendar_features.npy` from S-40 (7-dim: hour sin/cos, dow sin/cos, month sin/cos, holiday flag).
- Origin-only: features at the origin timestamp are broadcast over the horizon.
- Deterministic: no learned calendar embedding.

### Lag set
- Raw L336 window for all RFF experts (no anchor subtraction).
- Anchored L336 window for linear experts (S-26 pattern: last-row subtraction).

---

## 3. Router Design

**Router:** Uniform weights (1/M for M experts).
- **Rationale:** Zero-tuning, avoids S-39's EWA collapse and S-36/S-38's learned gating instability. Uniform weights are the most robust baseline for a fixed diverse pool.

---

## 4. Stack Head (optional)

**Per-horizon Ridge stack head** with fixed α=10000, no intercept, fitted on validation region only.
- **Rationale:** Identical to S-26 stack head; proven interior α. Applied on top of uniform-blended expert predictions.

---

## 5. Protocol Summary

| Component | Setting |
|-----------|---------|
| Train fit | 8545 rows (train.csv[:8545]) |
| Validation search | Chronological split: fit on val[0:1080), select on val[1080:2161) |
| Test refit | 11425 rows (train.csv full) |
| Rolling origins | 2161 stride-1 origins |
| Disjoint windows | t=0, 720, 1440, 2160 |
| Member fit | Frozen on train 8545 for val, refrozen on 11425 for test |
| Stack head | Optional per-horizon Ridge α=10000, no intercept |
| Router | Uniform weights |

---

## 6. Acceptance Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **Primary** | full rolling MAE < 1.9909 | Must beat S-26 incumbent |
| **Stability** | disjoint-4 MAE < 1.9696 | S-26 disjoint-4 cap; RFF must not fragment |
| **Transfer guard** | val_full MAE - test_full MAE ∈ [-0.02, +0.02] | S-36/S-39 scars |
| **Runtime** | full 2161 rolling < 300 seconds | CPU bound |

**Rejection criteria (any one fires → REJECT):**
- full MAE ≥ 1.9909
- disjoint-4 > 1.9696
- transfer delta > 0.02
- runtime > 300s

---

## 7. Why This Might Beat S-26

1. **RFF is genuinely non-linear:** Unlike S-35's delta-RF and S-39's linear-only pool, RFF maps raw window to a kernel-induced space, enabling the linear readout to capture nonlinear temporal structure.
2. **Calendar features in non-linear expert:** Avoids S-40's linear collapse; RFF can exploit calendar-raw interactions.
3. **Diverse expert types:** Mix of linear (S-26) + kernel-approximate (RFF) + calendar-RFF provides orthogonal signal sources.
4. **Uniform router stability:** Avoids S-39's EWA instability and S-36/S-38's learned gating regime fragility.

---

## 8. Skeleton File Map

- `rff_ensemble_s41/S41_DESIGN.md` — this file.
- `rff_ensemble_s41/rolling_arm.py` — skeleton implementation.
- `CONTEXT.md` — S-41 section appended.

---

*Design complete. Skeleton pending implementation.*
