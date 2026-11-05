---
type: Concept
title: DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-39 — ZTL-MoE: Zero-Tuning Linear Mixture-of-Experts for ETTh1 H=720

**Lane:** FRONTIER — new architecture, no grid search, no validation-fitted thresholds.
**Status:** DESIGN / skeleton implementation only. Prototype shape only; execution pending.
**Protocol:** S-20-clean (train 8545 fit, val 1080/1081 split, test 11425 refit, 2161 rolling origins).
**Target:** beat S-26 1.9909 MAE or explain why impossible.
**Zero-tuning constraint:** no grid search, no validation-fitted thresholds, no learned non-linear gating parameters.

---

## 1. Expert Pool (max 5 experts)

All experts are linear Ridge regressors on deterministic, fixed feature views.
Expert definitions are fixed by formula; no data-dependent initialization or learned feature encoder.

### Expert 1 — NLinear-L336-a1 (anchor-differenced L336 window)
- **View:** last-value-anchored L336 window → feature vector length 336.
- **Model:** Ridge α=1, intercept=True, predict + anchor back-add.
- **Rationale:** S-26 incumbent member; captures medium-term linear structure.

### Expert 2 — NLinear-L336-a10 (anchor-differenced L336 window)
- Same view as Expert 1, stronger shrinkage.
- **Rationale:** S-26 incumbent member; pairs with a1 for diversity in regularization strength.

### Expert 3 — NLinear-L720-a1 (anchor-differenced L720 window)
- **View:** last-value-anchored L720 window → feature vector length 720.
- **Model:** Ridge α=1.
- **Rationale:** long-range linear trend; S-06 leaderboard row 2.1534 (singleton); provides longer-memory linear expert.

### Expert 4 — RLinear-L336-a0 (RevIN-standardized L336 window)
- **View:** trailing-window standardized L336 window (mean/std per window), no decomposition.
- **Model:** Ridge α=0 (OLS), intercept=False, de-standardize at predict.
- **Rationale:** linear map on standardized features; orthogonal normalization to Expert 1/2; S-06 leaderboard row 2.1687.

### Expert 5 — Lag-Fourier Linear Expert (RFF-then-linear, fixed frequencies)
- **View:** deterministic fixed-frequency Fourier features on the anchored L336 window.
  - Lag set: delays D = {1, 2, 3, 6, 12, 24, 48, 96, 168, 336} (10 lags).
  - For each lag τ, compute z_τ = (y_{t-τ} - anchor) / scale.
  - Fixed Fourier frequencies: ω = {2π/24, 4π/24, 6π/24, 8π/24} (4 hourly harmonics).
  - RFF projection: φ_τ = cos(ω * τ) for each frequency; stack into 10 × 4 = 40-dim fixed feature vector.
  - Deterministic weights: fixed seed-free cosines; no learned RFF matrix.
- **Model:** Ridge α=100 (strong), intercept=False on φ vector; predict output is horizon-wide vector fit per origin.
- **Rationale:** deterministic frequency specialization without learned gating; provides an orthogonal linear expert on periodic structure. Zero-tuning because frequencies and lag set are fixed.

**Hard cap:** max 5 experts. Pool is fixed; no member addition/subtraction during run.

---

## 2. Router Design

**Router:** EWA (Exponentially Weighted Average) on per-expert validation residuals, with a fixed deterministic schedule.

### Per-origin expert weights
For rolling origin t (starting at validation region start), let e_{j,t} be expert j's absolute error on the held-out validation window immediately following t. Initialize w_{j,0} = 1/M (uniform). Update:

w_{j,t+1} = (1 - η_t) * w_{j,t} + η_t * exp(-β * e_{j,t})

with:
- β = 1.0 (fixed inverse-temperature; zero-tuning).
- η_t = min(1.0, C / (C + t)) where C = 1080 (val-half length). This is a deterministic annealed learning rate: early origins trust uniform; later origins trust residual evidence.

Normalize weights to sum to 1 after each update.

### Deterministic schedule
No learned parameters; schedule parameters C=1080, β=1.0 are derived from protocol constants, not searched.

### Pooled fallback
If all expert errors are equal (or weights become degenerate), fallback to uniform weights.

---

## 3. Feature Encoder Spec

### Lag set
All lag-based experts (1,2,3,4) share:
- Delays: {1, 2, 3, 6, 12, 24, 48, 96, 168, 336} (10 lags).
- Anchor: mean of last q=1 values before origin (last-value anchor; q=1).
- Scale: trailing-window std over L_window = 336 steps before origin, clamped to 1e-8.

### Fourier frequencies (Expert 5)
- Base period: 24 (hourly seasonality).
- Frequencies: ω_k = 2π k / 24, k ∈ {1, 2, 3, 4}.
- No learned phase or amplitude; deterministic cosine projection.

### RFF dimension
- Fixed 40-dimensional feature vector (10 lags × 4 frequencies).
- Deterministic; no random seed, no learned projection matrix.

### No learned encoder
All encoders are fixed algebraic transforms of the anchored window; no neural encoder, no embedding, no trained feature projection.

---

## 4. Zero-Tuning Rules

1. **No grid search over any parameter.** Expert α values are fixed: {1, 10, 1, 0, 100} for Experts 1–5.
2. **No validation-fitted thresholds.** The EWA schedule uses C=1080 and β=1.0 derived from protocol constants; the weights are updated deterministically from residual magnitudes, not thresholded.
3. **No learned gating.** The router is a fixed-function EWA over scalars; no linear/softmax gate with learned coefficients.
4. **No data-dependent initialization.** All expert hyperparameters are fixed constants; no seed search, no random projection.
5. **Protocol-locked splits.** Train 8545, val 1080/1081 chronological, test 11425 refit, 2161 rolling origins — all via `data.py` accessors.
6. **No intercept on stack.** If a mixture layer is added on top of expert forecasts, it is Ridge without intercept (S-20/S-28 scar).

---

## 5. Router-Only Mixture Layer (optional stacking head)

After expert forecasts, a **per-horizon Ridge without intercept** may be fitted on the validation region to combine the 5 expert forecasts. This is a *linear stack map*, identical to S-20, with fixed α=10000 (interior of the S-26 grid). The stack coefficients are fit once on val[0:1080) and frozen for the held-out select and test. This is optional; the EWA router alone may serve as the readout.

**Zero-tuning rule:** α=10000 is fixed; no α search.

---

## 6. Falsifiable Acceptance Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **Primary** | full rolling MAE < 1.9909 | Must beat S-26 incumbent |
| **Stability** | disjoint-4 MAE < 1.9696 | S-26 disjoint-4 cap; gated weighting must not fragment |
| **Transfer guard** | val_full MAE - test_full MAE ∈ [-0.02, +0.02] | Val→test divergence must be bounded; S-36 scar |
| **Time** | full 2161 rolling runtime < 300 seconds | Must run on CPU in seconds; O(NMH) linear in origins |
| **Determinism** | re-run byte-identical results | No random projection; no stochastic gating |

**Rejection criteria (any one fires → REJECT):**
- full MAE ≥ 1.9909 (no improvement).
- disjoint-4 > 1.9696 (stability guard fails).
- transfer delta > 0.02 (val→test divergence scar).
- runtime > 300s (CPU-seconds bound violated).
- non-deterministic outputs across runs.

**If prototype fails:** explain which scar it hits (basis saturation / vol-regime shift / val contamination) and close the frontier for the linear-only family under current protocol.

---

## 7. Why This Might Beat S-26

S-26 is a 2-member static stack. ZTL-MoE adds:
1. **Longer-memory linear expert** (L720) orthogonal to L336 pair.
2. **Normalization-orthogonal expert** (RLinear) that bypasses last-value anchoring.
3. **Deterministic frequency expert** (Fourier lags) that captures hourly harmonics.
4. **Online EWA router** that adapts weights to recent residual regimes without learned parameters.

The S-38 gated weighting scar is avoided because the router is not learned on validation residuals; EWA is a fixed-function deterministic updater with annealed learning rate, not a regression on vol terciles. The S-36 vol-regime shift scar is avoided because the router does not learn coefficients on a conditioning variable whose distribution shifts; it reweights by scalar error magnitudes that are origin-local and normalized by schedule.

---

## 8. Skeleton File Map

- `ztl_moe_s39/DESIGN.md` — this file.
- `ztl_moe_s39/rolling_arm.py` — skeleton with clear TODOs.
- `CONTEXT.md` — S-39 section appended.

---

*Design complete. Skeleton pending implementation.*
