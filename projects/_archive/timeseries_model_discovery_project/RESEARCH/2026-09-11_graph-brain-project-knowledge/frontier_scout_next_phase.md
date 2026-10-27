---
type: Concept
title: frontier_scout_next_phase
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Frontier Scout — Next-Horizon Exploration Beyond S-26 (1.9909 MAE)

Date: 2026-09-11 | Graph fingerprint: 627189679626 (nodes 273, edges 1411, files 16)
Protocol Invariant: S-20-clean (members fit on train 8545 for validation search, refit on 11425 for frozen test; chronological n2=1080/1081 split; zero future leakage).
Incumbent Benchmark: **S-26** 2-member NLinear (L=336, ridge a=1 + a=10, per-horizon ridge α=10000, no-intercept): **1.9909 MAE / 2.4710 RMSE (Disjoint-4: 1.9696)**.

---

## 1. Executive Context & Closed Failure Modes

Recent sweeps systematically mapped and closed multiple failure corridors around the S-26 terminal boundary:
1. **Regime Overfitting & Memorization (S-21, S-21b)**: Non-linear/tree heads memorize local offsets (val 2.33 in-sample vs held-out 3.59 → test 8.57). Closed.
2. **Multivariate Correlation Collapse (S-24)**: Raw 7-channel windows heavily overfit val regimes (val 2.24 vs test 2.0539). Closed.
3. **Band & Intercept Discontinuities (S-27, S-28)**: 3-band alpha optimization failed held-out transfer (test delta −0.0045, disjoint regressed to 1.9709). Intercept caused catastrophic collapse (MAE 5.9116). Closed.
4. **Horizon Loss Weighting (S-29)**: Loss reweighting over horizons ($\gamma = -0.5, \alpha=30000$) regressed disjoint-4 diagnostic to 1.9852 (+0.0156). Closed.
5. **Direct Feature Concatenation / Scalars (S-30, S-32)**: Calendar hour phase $\sin(2\pi(t+h)/24)$ yielded exactly $\Delta = +0.0000$. Local window variance scale $\sigma_t$ regressed test to 1.9928. Both signals are already spanned by the linear lookback. Closed.
6. **Longer Lookbacks under RevIN (S-31)**: RevIN-NLinear at $L=512$ diluted the $L=336$ linear combination, regressing test to 2.0036. Closed.

### Graph-Brain Health & Touchpoint Mapping
- Hotspot `fit @ nlinear_knn.py:65` (degree 48) and `_lag_dataset @ base.py:197` (degree 27) are completely decoupled from pure linear window forecasters (`neural_models.py:165`).
- The univariate linear subspace (NLinear, DLinear, RLinear) operates on direct 2D window slices `(N, L)` rather than calling `_lag_dataset`. Adding structural spectral/wavelet decomposition or multi-rate residuals incurs **zero blast risk** to the 14 callers of `_lag_dataset`.

---

## 2. Novel High-EV Hypotheses for Next Phase

To break the 1.9909 barrier without triggering closed failure modes, any new candidate MUST:
- Retain univariate OT last-value anchoring (level-free, immune to non-stationary mean drift).
- Avoid piecewise-constant partitions and cross-channel multivariate matrices.
- Introduce genuinely orthogonal basis representations or multi-scale structural decomposition.

---

### Hypothesis 1: Spectral-Anchored FITS with Dominant Harmonic Truncation (rFFT-Linear at L=336)

- **Mechanism / Architecture**:
  Past FITS implementations (S-07: 2.1220 MAE) used RevIN standardization $(x - \mu)/\sigma$ and global spectrum mapping. We propose **Anchored-FITS (AFITS)** at lookback $L=336$:
  1. Window anchoring: $x_{anchored} = x_{t-336:t} - x_t$ (strictly level-free, identical to NLinear).
  2. Compute real-valued Fourier coefficients via rFFT on $x_{anchored}$ (169 complex bins).
  3. Harmonic Band-Pass / Truncation: Zero out noisy high-frequency bins while retaining the top $K$ dominant diurnal/weekly harmonics (periods 24h, 12h, 168h, 84h, 56h, 42h, 33.6h; corresponding to rFFT frequency indices $\{2, 4, 6, 7, 8, 10, 14, 28\}$).
  4. Learn a linear mapping in the compact spectral domain (or back-projected filtered time domain) to the 720-step horizon via complex or dual-channel real Ridge regression.
- **Why It Avoids Closed Failure Modes**:
  - Unlike S-30 (which provided a single scalar phase), spectral decomposition retains amplitude, phase, and multi-harmonic interactions across the full 2-week history.
  - Unlike S-24, it is strictly univariate (zero cross-channel overfitting).
  - Unlike S-07, it uses last-value anchoring rather than mean standardization, eliminating boundary edge artifacts in the inverse transform.
- **Falsifiable Acceptance Criteria (S-20-clean)**:
  - **Full 2161 rolling MAE < 1.9859** ($\ge 0.0050$ improvement over S-26 1.9909).
  - **Disjoint-4 diagnostic MAE $\le 1.9696$** (no regression vs S-26).
  - Selected purely via held-out validation half ($n_2=1080/1081$).

---

### Hypothesis 2: Multi-Rate Wavelet / Multi-Scale Decimated Residual (Denoised Dyadic Subband NLinear)

- **Mechanism / Architecture**:
  Instead of pooling raw samples or computing heuristic moving averages, decompose the anchored lookback $x_{anchored} \in \mathbb{R}^{336}$ into $J=3$ dyadic orthogonal wavelet levels (e.g. Haar or db2 discrete wavelet transform):
  - Approximation subband $A_3$ (scale $2^3 = 8\text{h}$, capturing multi-day trend / weekly cycle).
  - Detail subbands $D_1, D_2, D_3$ (capturing hourly noise, diurnal swings, and sub-daily fluctuations).
  Train dedicated linear projection heads $W_{A_3}, W_{D_3}, W_{D_2}, W_{D_1}$ mapping each decomposed subband to its respective horizon frequency components, with heavier ridge shrinkage on high-frequency details:
  $$\hat{y}_{h} = \sum_{j=1}^J W_{D_j} D_j + W_{A_J} A_J$$
- **Why It Avoids Closed Failure Modes**:
  - S-10 (MultiRateELM) failed (+0.22) because ELM random projections on max-pooled windows destroy phase alignment. Linear wavelet subbands preserve exact energy conservation (Parseval's identity) and strict temporal alignment.
  - Decimation acts as an adaptive regularizer: high-frequency noise is constrained from polluting long-range (H=720) horizon weights.
- **Falsifiable Acceptance Criteria (S-20-clean)**:
  - **Full 2161 rolling MAE < 1.9859** ($\ge 0.0050$ vs 1.9909).
  - **Disjoint-4 diagnostic MAE $\le 1.9696$**.
  - Must survive refit-all-val without coefficient explosion in high-frequency detail bands.

---

### Hypothesis 3: S-26 Base-Residual Multi-Horizon Linear Booster (Linear Boosting on Anchored Horizon Residuals)

- **Mechanism / Architecture**:
  Keep the frozen S-26 2-member incumbent as an immovable base forecaster:
  $$\hat{y}^{(0)}_{t, h} = \text{S-26}(x_{t-336:t})$$
  Compute the train-set residual trajectories $r_{t, h} = y_{t+h} - \hat{y}^{(0)}_{t, h}$ over train 8545 (for val) and 11425 (for test).
  Train a secondary, highly regularized linear residual model:
  $$\hat{r}_{t, h} = \mathbf{w}_h^T \phi(x_{t-336:t})$$
  where $\phi(x)$ extracts low-dimensional structural features of the lookback:
  - Slope/curvature of the last 24h, 48h, 168h.
  - Spectral power in diurnal/semi-diurnal bands.
  Final forecast: $\hat{y}_{t, h} = \hat{y}^{(0)}_{t, h} + \lambda \hat{r}_{t, h}$, with shrinkage $\lambda \in [0.05, 0.5]$ tuned strictly on held-out validation.
- **Why It Avoids Closed Failure Modes**:
  - S-16 (NLinear+KNN hybrid) failed because KNN residual retrieval overfit noise. Here, the residual model is strictly linear and constrained to smooth, low-rank subspace projections.
  - S-28 failed because an unregularized per-horizon intercept memorized mean error. A shrinkage-boosted linear residual model with $\lambda \ll 1.0$ forces corrections to correlate with input dynamics rather than static bias.
- **Falsifiable Acceptance Criteria (S-20-clean)**:
  - **Full 2161 rolling MAE < 1.9859**.
  - **Disjoint-4 diagnostic MAE $\le 1.9696$**.
  - Secondary model must achieve non-zero weight ($\lambda^* > 0$) on held-out validation without regressing any disjoint test split.

---

## 3. Comparison Matrix & Prior Art

| Hypothesis | Representation Domain | Level-Handling | Regularization Strategy | Key Contrast vs Prior Rejection |
|---|---|---|---|---|
| **H1: Anchored-FITS (rFFT L=336)** | Frequency (rFFT) | Last-value anchor ($x_t$) | Harmonic cutoff / Band-pass | S-07 used RevIN and suffered boundary distortion; S-30 only passed scalar phase |
| **H2: Dyadic Wavelet NLinear** | Time-Scale (DWT) | Last-value anchor ($x_t$) | Subband-dependent Ridge penalty | S-10 used ELM max-pool which scrambled phase; DWT maintains exact phase reconstruction |
| **H3: S-26 Residual Linear Booster** | Trajectory Residual | Base S-26 anchored | Shrinkage multiplier $\lambda$ | S-16 used KNN (noise memorization); S-28 used intercept (static bias collapse) |

---

## 4. Execution & Falsification Sequence

1. **Step 1: Prototype Anchored-FITS (H1)** as a standalone `methods/afits.py` forecaster. Verify singleton performance against singleton NLinear ($2.0571$). If singleton passes, evaluate as a candidate in the 12-member pool under S-20-clean.
2. **Step 2: Prototype Dyadic Wavelet Linear (H2)** if H1 fails to achieve the 1.9859 boundary.
3. **Step 3: Prototype Residual Linear Booster (H3)** as an incumbent-adjacent wrapper.

Stop rule: If all 3 hypotheses fail to meet full rolling MAE < 1.9859 with disjoint-4 $\le 1.9696$, formally declare the univariate linear family at horizon H=720 fully saturated under current protocol limits.
