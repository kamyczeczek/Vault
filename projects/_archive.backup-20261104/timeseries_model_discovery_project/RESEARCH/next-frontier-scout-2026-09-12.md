---
type: Concept
title: next-frontier-scout-2026-09-12
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Next Frontier Scout Note (2026-09-12)

**Subproject:** `.` (ETTh1 H=720 Long-Horizon Forecasting)
**Current Incumbent:** S-26 Ridge Mixture (2 univariate linear members: NLinear L336 a=1 + a=10, per-horizon stack $\alpha=10000$, no-intercept) — **1.9909 MAE / 2.4710 RMSE**.
**Frontier Status:** Univariate linear family on OT alone is formally **SATURATED** (H2 wavelet DWT / rFFT basis rotation closed out; stop rule fired). Further gains require moving beyond univariate linear lookbacks on OT.

---

## Concrete Next Bets

### 1. Exogenous-Channel Multivariate Linear Members (Multivariate Expansion)
- **Concept:** Extend the S-26 linear pool with multi-channel NLinear/RLinear members operating across all 7 ETTh1 channels (OT, HUFL, HULL, MUFL, MULL, LUW, LUL), using last-row anchoring (level-free) and strict chronological validation selection.
- **Why not closed by S-24 scar:** S-24 (`sub_experiments/multivariate_ridge_s24/`) failed (+0.0559 test regression) because it used raw chronological validation splitting that allowed cross-channel temporal leakage and val-local correlation fitting. A rigorous protocol with strict out-of-sample regularization, channel-dropout / sparse subset selection, and explicit validation-to-test transfer checks overcomes the val-local regime trap.
- **Falsifiable Acceptance Criteria:**
  - Full 2161 rolling MAE < 1.9909 (target $\le 1.9850$).
  - Validation-to-test transfer check: Validation improvement must transfer monotonically to frozen test (no val MAE gain accompanied by test regression $> +0.01$).

### 2. Level-Free Non-Linear Heads / KAN Readout on Orthogonal Spectral Bands
- **Concept:** Replace or supplement the per-horizon linear ridge stack with a regularized non-linear readout (e.g., Kolmogorov-Arnold Networks or shallow MLPs with strong weight decay and dropout) operating strictly on level-free delta features or non-overlapping frequency/latent bands (avoiding the DWT/rFFT basis rotation trap).
- **Why not closed by S-21b / S-21 / S-33 scars:** S-21/S-21b failed because decision trees and leaf-linear delta mixtures memorized per-region levels or overfitted leaf regimes (test 3.04–8.57). S-33 (AFITS) failed because spectral low-pass filters duplicated existing linear lookback frequency coverage. A non-linear head is not closed if: (a) inputs are strictly level-free deltas, (b) feature representations are non-overlapping with the incumbent linear lookback span, and (c) model capacity is bounded by strong $\ell_2$ regularization.
- **Falsifiable Acceptance Criteria:**
  - Full 2161 rolling MAE < 1.9909 (target $\le 1.9850$).
  - Held-out validation MAE improvement $> 0.005$ over S-26 without triggering validation-test divergence.

### 3. Volatility-Gated / Regime-Conditional Dynamic Weighting over S-26 Members
- **Concept:** Implement a volatility- or trend-conditioned gating mechanism over the S-26 base members (or member predictions) using rolling variance / window-scale features rather than point-to-point kNN distance.
- **Why not closed by S-23 / S-19 scars:** S-23 (KNN-disagreement-gated blend) failed because discrete kNN distance metrics introduced noise-fits on validation (+0.0134 test regression). S-19 (CycleESN val-weighted ensemble) failed because simplex optimization drifted toward regime-fragile members. A regime-conditional bet is not closed if conditioning is based on global macro-volatility / rolling window scale (as validated in S-04) rather than local neighborhood distances, combined with entropy regularization on mixture weights.
- **Falsifiable Acceptance Criteria:**
  - Full 2161 rolling MAE < 1.9909 (target $\le 1.9850$).
  - Stability check: Must exhibit superior or equal stability across the hardest seasonal window (W4) compared to S-26 (W4 MAE $\le 1.84$).
