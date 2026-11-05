---
type: Concept
title: 2026-09-12_omega-h720-integration
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Spectral Predictability Ω → h720 Integration Design

**Date:** 2026-09-12
**Author:** omega-h720 (worker)
**Source paper:** Wang et al., *Spectral Predictability as a Fast Reliability Indicator for Time Series Forecasting Model Selection*, arXiv:2511.08884 (12 Nov 2025), AAAI AI4TS Workshop 2026 — definition confirmed from `RESEARCH/2026-09-12_spectral-predictability-omega.md` (§2–§3, §A.4; repo `gift_eval/compute_metrics_fast.py:77–135`).
**Source doc status:** `RESEARCH/2026-09-12_spectral-predictability-omega.md` **present** — §§1 and 5.3 below are now **paper-exact** (no longer provisional). Ω>0.5 TSFM wins by 60%, Ω<0.4 simple models suffice, computable in seconds. Prior provisional flags removed; repo deviation explicitly noted.
**h720 state:** ETTh1 H=720 rolling-origin (2 161 origins), incumbent S-26 Ridge mixture (2-member NLinear L336 a=1+a=10, per-horizon stack α=10000, no-intercept) **1.9909 MAE / 2.4710 RMSE**. Univariate linear family on OT alone **SATURATED per H2** (wavelet DWT basis rotation + H2-KNN successor both rejected; stop rule fired — basis/shrinkage on OT alone closed).
**Input docs read:** `h720/CONTEXT.md` (S-26 + H2 + S-21/S-24/S-34/S-35/S-36 scars), `h720/data.py` (split/protocol), `RESEARCH/next-frontier-scout-2026-09-12.md` (bets 1–3), `brains/ts_brain/corpus/*.md` (01 protocol, 02 anti-leakage, 03 registry, 04 leaderboard, 05 principles).

---

## 1. What Ω Is (Paper-Exact Definition — Wang et al. arXiv:2511.08884 §3, §A.4)

> Source: `RESEARCH/2026-09-12_spectral-predictability-omega.md` §2 (paper §3, §A.4) and `gift_eval/compute_metrics_fast.py:77–135`. No longer provisional.

Let `x ∈ ℝ^T` be a univariate window/series (for h720: a single history window `L ∈ {96,336,720}` on OT, history-only). Paper-exact steps:

1. **DC removal:** `x ← x - mean(x)` (subtract mean).
2. **Hann taper (spectral-leakage control, §A.4):** `x ← x · w_Hann` where `w_Hann[n]=0.5(1-cos(2πn/(T-1)))` (numpy: `x * np.hanning(T)`). Applied **before** FFT; required for paper-exact Ω.
3. **One-sided PSD via FFT (DC bin excluded):** `P_k = |x̂_k|²` for `k=1..K`, `K = floor(T/2)`, where `x̂_k` is the k-th FFT coefficient (DC `k=0` dropped from sum).
4. **Normalize to distribution:** `p_k = P_k / Σ_j P_j`.
5. **Spectral entropy:** `H = -Σ_k p_k log p_k` (nats), `H_max = log K`.
6. **Spectral predictability:**
   ```
   Ω = 1 - H / H_max    ∈ [0,1]
   ```
   Ω→1: energy in few bins (peaked/periodic, predictable). Ω→0: energy spread uniformly (flat/white-noise-like, unpredictable). `Ω ∈ [0,1]` by construction; `H/H_max` is the normalized spectral entropy (wavelet-entropy analogue per paper §2–3, refs Guntu et al. 2020; Wang et al. 2025).

**Preconditions (paper §5.3, §6.2):**
- `T > 1000` recommended for FFT stability (short-series estimates are unstable; GIFT-Eval truncates at 4096 steps per stream for tractability).
- Series should be **(approximately) stationary** — no regime shifts / structural breaks (Ω assumes stable spectrum; high LLE / chaos is a warning sign and coincides with low Ω but is not captured by Ω alone).
- Intrinsic temporal structure should dominate over exogenous shocks (if shocks dominate, Ω is weak — e.g. traffic accidents, policy events).

**Multivariate extension (paper §A.2 / GIFT-Eval):** Per-covariate Ω computed independently, then **averaged** across variates for a dataset-level score: `mean_Ω = mean_i Ω(x^{(i)})`.

**Repo deviation — `compute_metrics_fast.py` does not apply Hann internally:**
> `_safe_rfft_power` / `spectral_entropy()` / `omega_from_arr()` in `gift_eval/compute_metrics_fast.py:77–135` implement DC removal and rFFT power + `H/log(len(p))` normalization but **do not** multiply by the Hann window internally. For **paper-exact** Ω the **caller must apply Hann before calling**:
> ```python
> x_exact = (x - x.mean()) * np.hanning(len(x))  # paper-exact per §A.4
> omega = omega_from_arr(x_exact)               # then equals §A.4 definition
> # or equivalently: x_hann = x * np.hanning(len(x)); omega_from_arr(x_hann)
> # (omega_from_arr also subtracts mean internally, so double-subtraction is harmless)
> ```
> Omitting Hann preserves Ω ordering for large T and changes absolute Ω only slightly, but **thresholds 0.4/0.5 are calibrated to the Hann-tapered definition** — h720 prototype MUST apply Hann for threshold transfer.

**Computation cost:** For L=720, K=360 bins; per-window rFFT ~ microseconds. 2 161 origins × 3 L values ≈ 6.5k FFTs → <0.1 s in numpy, O(T log T) per window, satisfying "seconds" claim even in a Python loop.

---

## 2. Why Ω Matters to h720 Right Now

### 2.1 The saturation context
H2 proved the univariate linear family on OT is saturated under current protocol: orthogonal basis rotations (wavelet, FITS/rFFT), subband-dependent penalties, and non-linear readouts on the same L=336 window all fail the ≥0.005 full-rolling improvement bound. Remaining bets per scout are exogenous channels, non-linear heads on orthogonal bands, or **protocol/predictability changes**. Ω is of the third kind: it does **not** propose a new regressor — it proposes a **pre-training gate** that tells you *when* a heavier model class (TSFM) is worth paying for.

### 2.2 The project cost the gate addresses
- S-24/S-34 (multivariate) + S-25 (tabu mixed) + S-36 (volatility gate) all failed by fitting val-local structure that did not transfer. Each cost a full ridge sweep + 2 161×720 scoring.
- Ω is **unsupervised** (no training, no val-fitting): one FFT per window, thresholds are paper-fixed (0.4/0.5), not learned on h720 val. This is orthogonal to S-23/S-36 scars by construction (those learned a gate coefficient on val; Ω's thresholds are external).

### 2.3 The decision rule the paper enables

| Regime | Ω range | Paper claim | h720 action (frozen thresholds, not tuned on val) |
|--------|---------|-------------|---------------------------------------------------|
| **A — Simple-sufficient** | Ω < 0.4 | Simple (DLinear-class) suffices; TSFM does not beat by meaningful margin | **Keep S-26** (2-member NLinear L336 ridge). Do not pay TSFM inference. Document Ω-stratified residual check (see §4). |
| **B — Indeterminate** | 0.4 ≤ Ω ≤ 0.5 | Transition / dataset-dependent | Keep S-26; optionally log for future calibration. No model switch. |
| **C — TSFM-favored** | Ω > 0.5 | TSFM wins by ~60% (paper's aggregate) | **Justify TSFM zero-shot attempt** — gated inference only on C-windows. Compare pooled vs. gated ensemble under S-20-clean protocol. |

This is a **compute-gating** claim, not an accuracy-guarantee claim. Even if the 60% figure does not transfer to ETTh1 H=720 (long-horizon ETTh1 is notoriously hard for zero-shot), regime A still saves 100% of TSFM cost on low-Ω windows, which is a win if Ω mass is in A.

---

## 3. Compute Ω on ETTh1 OT — Stratification Plan

### 3.1 Data source (anti-leakage clean)
- Load via `h720/data.py:get_protocol_data()` only — never direct CSV read in methods.
- Raw series: `ETTh1.csv` 17 420 hourly OT values.
- For every rolling origin `t ∈ [0, 2160]` (frozen fit on `train.csv` 11 425 rows, history = `eval_series[:11425+t]`, scoring window `test[t:t+720]`):
  - Extract **history-only** windows `w_L(t) = history[t+11425-L : t+11425]` for `L ∈ {96, 336, 720}` (the three S-26-relevant lookbacks — 96≈4 days, 336≈14 days matching S-26, 720≈30 days matching horizon). Each Ω_L(t) sees **no future** — same containment as `methods/base.py:_window_scale`.
  - Compute Ω_L(t) independently per L (three stratifications). Primary: **L=336** (matches S-26 span); 96/720 are sensitivity arms testing whether shorter/longer spectral context changes regime assignment.

### 3.2 Per-window recipe (paper-exact, numpy)

Paper-exact per §A.4 (DC removal → Hann taper → one-sided PSD k=1..K, K=floor(T/2) → p_k → H → Ω):

```python
import numpy as np

def omega_paper_exact(window: np.ndarray) -> float:
    """Spectral predictability Ω ∈ [0,1] — paper-exact per §A.4.
    window: 1-D, length T, history-only, OT series.
    Precondition: T > 1000 recommended for FFT stability (paper §5.3);
    h720 windows use T ∈ {96,336,720} — sensitivity arms; paper-exact but
    below the T>1000 stability recommendation — report with stationarity caveat.
    Stationarity: Ω assumes stable spectrum; do not use across regime shifts.
    """
    x = np.asarray(window, float).ravel()
    if x.size < 4:
        return float("nan")
    if np.allclose(x.std(), 0):
        return 1.0  # constant → H=0 → Ω=1 (by convention, cf. repo)
    x = x - x.mean()              # 1. DC removal (§A.4)
    x = x * np.hanning(len(x))    # 2. Hann taper (§A.4) — REQUIRED for paper-exact
    spec = np.fft.rfft(x, n=x.size)
    power = spec.real**2 + spec.imag**2  # |x̂_k|²
    power = np.clip(power, 0, None)
    # 3. One-sided PSD: exclude DC bin k=0
    power = power[1:]             # k=1..K, K=floor(T/2)
    if power.sum() == 0:
        return float("nan")
    p = power / power.sum()       # 4. normalize
    p = np.clip(p, 1e-12, 1.0)
    H = -np.sum(p * np.log(p))    # 5. spectral entropy
    K = len(p)                    # = floor(T/2)
    Hmax = np.log(K)
    return float(1.0 - H / Hmax)  # 6. Ω = 1 - H/Hmax ∈ [0,1]

# Repo-deviation note: gift_eval/compute_metrics_fast.py:77–135 does NOT
# apply Hann internally. For paper-exact via repo helper, caller must do:
#   x_hann = (x - x.mean()) * np.hanning(len(x))
#   omega = omega_from_arr(x_hann)   # or x * np.hanning(len(x)) before omega_from_arr

# Multivariate (paper §A.2): mean Ω across covariates
#   mean_omega = np.mean([omega_paper_exact(series[:, i]) for i in range(C)])
```

All three L arms share the function — no hyperparameters, no fitting. For strict reproduction use `omega_paper_exact`; for repo-fast path document whether Hann was applied.
### 3.3 Stratification outputs
- Per-origin scalars: `Ω_96(t), Ω_336(t), Ω_720(t)` for t=0..2160 (arrays length 2 161).
- Empirical distribution per split: histogram + CDF + mass in A/B/C. Report separately for **val region** (train 8 545 fit, 2 880 val origins — the S-20-clean held-out half) vs. **test region** (full 2 161 test origins) to test **S-36-style distribution shift** (S-36's volatility gate failed because vol shifted −0.48 to −0.90σ val→test; Ω must be checked the same way — if Ω mass shifts across the 0.4/0.5 cut, the gate is non-stationary).
- Horizon-relevant aggregation (ledger-friendly):
  - `Ω̄_val(L), Ω̄_test(L), std, IQR, P(Ω<0.4), P(Ω>0.5)` per L.
  - Per-disjoint window W1–W4 (t=0/720/1440/2160) Ω means — tests W4 hardness alignment.
  - Spearman correlation `corr(Ω_L, σ_window)` to show Ω is not just volatility (S-04/S-32/S-36 orthogonality).

**Hypothesis to test (informational, not a promotion gate):** If ETTh1 OT at H=720 is saturated and S-26 already captures the linear spectral structure, test windows should concentrate in **A or B** (Ω<0.5 mass dominant). If mass is in C yet S-26 still wins, the paper's 60% TSFM claim does **not** transfer to ETTh1 H=720 zero-shot — important negative result.

---

## 4. Decision Justification Per Regime

### 4.1 If Ω < 0.4 on test windows → Justify Keeping S-26
- Paper rule says simple models suffice — TSFM expected gain ≤ noise.
- h720 mapping: S-26 **is** the paper's "simple model" exemplar — DLinear-class last-value anchored linear Ridge (S-26 is two NLinear L336 ridges, which = per-horizon linear map; FITS ≡ RLinear ≡ DLinear per Toner-Darlow equivalence proven in S-06/S-07). No extra capacity is justified.
- Supporting evidence already in h720: S-27–S-32 + H2 + S-35 all show no orthogonal signal in OT window alone — consistent with low-Ω unpredictability where extra parameters only fit val noise.
- Action: Freeze S-26 as routed model for A-windows, report Ω-stratified S-26 MAE (should be highest error in A, confirming hard-to-predict regime) and note compute saving: 0 TSFM calls on A-mass.

### 4.2 If Ω > 0.5 on test windows → Justify TSFM Zero-Shot Attempt
- Paper rule says TSFM wins by 60% on high-Ω data — the linear family's inductive bias (fixed-L linear map) cannot capture the peaked spectral structure as efficiently as a pretrained foundation model.
- h720 mapping: Zero-shot means **no ETTh1 fine-tuning** (frozen TSFM weights, history window as prompt, no gradient on train.csv — avoids S-24 val-local overfit). Candidate TSFMs (pick one frozen, document version pin): Chronos, TimesFM, Moirai, or TimeGPT — whichever exposes hourly H=720 zero-shot via API/local weights. Input: same L=336 or L=720 history window Ω was computed on (no extra data vs. S-26).
- Gating evaluation (S-20-clean compliant):
  - Members for val search: S-26 predictions (frozen 8 545) vs. TSFM predictions (frozen zero-shot, also history-only). Stack is **not** a learned Ridge — it is the Ω gate: `ŷ(t) = TSFM(t) if Ω_336(t)>0.5 else S26(t)` (hard gate, thresholds frozen from paper). No α search; no val fitting → no S-36 non-stationarity risk.
  - Select nothing on val (gate is fixed). Report val full MAE as diagnostic only.
  - Frozen test (1 425 refit for S-26 members; TSFM stays zero-shot): score **full 2 161** and **disjoint-4** — same selectors as H2. Compare gated ensemble vs. pure S-26.
  - Cost metric: TSFM call rate = P(Ω>0.5) on test — the efficiency claim.

---

## 5. Prototype: `h720/sub_experiments/spectral_omega_gate/`

### 5.1 Goal
A **no-training** harness that (i) computes Ω per window, (ii) correlates Ω with S-26 residuals, (iii) implements the frozen Ω gate — all under `data.py` protocol and failing loud on leakage.

### 5.2 Layout

```
h720/sub_experiments/spectral_omega_gate/
  compute_omega.py       # omega(window)->float, batch over origins, L∈{96,336,720} — paper-exact
  rolling_arm.py         # S-20-clean harness: val Ω dist, test Ω dist, residual corr, gate scoring
  tsfm_adapter.py        # (stub until TSFM chosen) zero-shot predict(history)->ndarray(720); pinned version
  results_omega.json     # artifact: omega arrays, dist stats, correlations, gate MAE
  harness.log            # stdout + anchor checks
  README.md              # one-line re-run + interpretation
```

### 5.3 `compute_omega.py` — contract (paper-exact)
- Inputs: `window: np.ndarray (L,)` history-only, univariate OT.
- Output: `float Ω ∈ [0,1]` per §A.4: DC removal (subtract mean) → Hann taper (`x * np.hanning(L)`) → one-sided PSD `k=1..K, K=floor(L/2)` → normalize `p_k` → `H=-Σ p log p`, `Hmax=log K`, `Ω=1-H/Hmax`.
- Preconditions: `T>1000` recommended for FFT stability (paper §5.3) — h720 windows `L∈{96,336,720}` are **below** this; report with stationarity caveat and do not treat Ω as high-confidence for `L<1000`. Stationarity: Ω assumes stable spectrum; flag/high-LLE or regime-shift windows.
- Multivariate: per-channel Ω then `mean_Ω = mean_i Ω(x^{(i)})` (§A.2).
- Repo deviation: `gift_eval/compute_metrics_fast.py:77–135` (`omega_from_arr` / `spectral_entropy`) **does not apply Hann internally** — caller must apply `x * np.hanning(len(x))` before `omega_from_arr` for paper-exact; document deviation if omitted.
- Dependencies: `numpy.fft.rfft` only; no torch, no training. Deterministic (no RNG).
- Must expose `--condition` flag retained for ablation, but **default MUST be paper-exact** (`dc + Hann + rfft k=1..K`); non-default modes must log "non-paper-exact".
- Unit tests (throwaway, not permanent): `Ω(white_noise) < 0.3`, `Ω(sine) > 0.8`, `Ω(const)≈1` (variance≈0 convention) — pin expected branch.

### 5.4 `rolling_arm.py` — protocol (mirrors S-20-clean / H2)

1. **Load** `get_protocol_data()` → `history_all = train.csv` (11 425), `eval_series`, `test.csv`.
2. **Val phase** (train 8 545 frozen):
   - Fit S-26 members on 8 545 (reuse `methods/neural_models.NLinear` L336 a=1/a=10; fit via Ridge — same as `sub_experiments/greedy_linear_mixture_s26/`).
   - Roll over val 2 880 origins: for each origin collect Ω_L(t) (L=96/336/720) + S-26 forecast + val target → per-origin MAE_resid(t)=MAE(S26 vs target).
   - Compute val Ω distributions + Spearman `ρ(Ω_L, MAE_resid)` (expect negative: higher Ω → lower MAE if predictability claim holds). Also `ρ(Ω_L, |D|)` where `D = P_L96-P_L336` (S-36 disagreement) to prove orthogonality.
3. **Test phase** (full 11 425 frozen):
   - Refit S-26 members on 11 425.
   - Roll over full 2 161 test origins: Ω_L(t) + gated prediction (S-26 vs. TSFM stub) + scoring.
   - Frozen insight: report **Ω-stratified MAE** — bin origins by Ω_336 quantile/ threshold and show S-26 MAE per bin (A/B/C). This is the S-01/W4-style stratification but on predictability, not calendar.
4. **Guards** (fail-loud, per 01/02 corpus):
   - Anchor reproduction: re-derive S-26 1.9909/2.4710 on frozen 11 425 full 2 161 before any Ω scoring — hard fail on >1e-4 dev (same as S-20b 8/8 anchors).
   - Anti-leakage: assert Ω windows end at `history_end-1`, never include `test[t+k]`.
   - Determinism: rerun SHA check on `results_omega.json` (H2-style verify).
5. **Outputs** (`results_omega.json`):
```json
{
  "omega": {"L96": [...2161...], "L336": [...], "L720": [...]},
  "dist": {"val": {"mean336": 0.0, "p_lt_04": 0.0, "p_gt_05": 0.0}, "test": {}},
  "shift": {"delta_mean_sigma": 0.0},
  "correlation": {"rho_omega336_mae": 0.0, "pval": 0.0, "rho_omega336_sigma": 0.0},
  "stratified_mae": {"A_lt04": 0.0, "B_04_05": 0.0, "C_gt05": 0.0},
  "gate": {"full_mae_gated": 0.0, "full_mae_s26": 1.9909, "disjoint_gated": 0.0, "call_rate": 0.0}
}
```

### 5.5 Correlation-with-residuals (no training)
- Primary diagnostic: `ρ(Ω_336, S26_MAE)` and `ρ(Ω_336, S26_MAE_rank)` across 2 161 test origins. Expect significant negative correlation if high predictability → low error.
- Secondary: `ρ(Ω_336, |S26 - persistence|)` to test whether high-Ω windows are where simple persistence already wins (would imply Ω gates into trivial regime).
- Tertiary: Per-horizon Ω vs. per-horizon MAE(h) (720 curves) — tests whether Ω predicts *which horizons* are hard (early vs. late tail).
- All correlations are **Spearman** (rank, robust) + Pearson for reference, with two-sided p-value; no fitting.

### 5.6 TSFM adapter (deferred)
- Phase 1 of prototype ships **without** TSFM calls — Ω stratification + S-26 residual correlation only (zero external dependency, seconds). Gated MAE is reported as S-26-only until a TSFM backend is pinned; `call_rate` still reports.
- Phase 2 plugs one frozen TSFM (pinned `requirements` + model hash) behind `tsfm_adapter.predict(history)->ndarray(720)` and re-scores the gate. No retraining on ETTh1.

---

## 6. Two Concrete Next Slices (Falsifiable, MAE vs. 1.9909)

Both slices are **MEDIUM lane**, no new trained members beyond the frozen TSFM zero-shot, S-20-clean (val members frozen 8 545 for diagnostics, test refit 11 425 for scoring; chronological; full 2 161 selector, disjoint-4 diagnostic only; anchor-checked; zero val-fitting of Ω thresholds).

### Slice 1 — `spectral_omega_gate` (no-training gate): Ω-correlated regime check + cost-saved routing

**What:** Ship the prototype (§5) end-to-end with TSFM adapter enabled (one frozen TSFM, zero-shot, history-only). Hard gate `Ω_336>0.5 → TSFM else S-26` (primary); sensitivity arms `L=96/720` and `Ω_720` reported. No learned weights.

**Falsifiable acceptance (all must hold; else REJECT, S-26 stays 1.9909):**
- **Primary (accuracy):** `MAE_gated(full 2161) ≤ 1.9859` — i.e. **≥0.0050 improvement** over S-26 1.9909 (same bound as H2). This is the only promotion gate.
- **Guard 1 (no disjoint regression):** `MAE_gated(disjoint-4) ≤ 1.9696` (disjoint cap = S-26 disjoint). Prevents sparse-window noise-fitting (S-25 lesson).
- **Guard 2 (val→test stationarity):** `|Ω̄_test - Ω̄_val| / σ_val < 0.5` for L=336 (S-36 scar: distribution shift killed the volatility gate; Ω must not shift >0.5σ). If violated, gate is declared non-stationary — REJECT even if MAE wins (reports as protocol issue, not SOTA).
- **Guard 3 (correlation sanity):** `ρ(Ω_336, MAE_S26)` significantly negative (p<0.01, Spearman) — confirms Ω predicts error direction; else the gate win is coincidental.

**Why this slice matters even if REJECTED:** If Ω mass on ETTh1 H=720 test is dominantly <0.4 (≈ S-36-style low-volatility test), the slice **documents** that S-26 is compute-optimal and TSFM cost is unjustified — a citable negative result that closes the TSFM-expansion question without a training run. `call_rate = P(Ω>0.5)` quantifies the saving.

**Re-run:** `python h720/sub_experiments/spectral_omega_gate/rolling_arm.py` (CPU-only, <10 s without TSFM, + TSFM inference time with adapter).

### Slice 2 — `omega_stratified_eval` (diagnostic-only, no TSFM): Prove H2 saturation is Ω-conditional

**What:** Purely observational — no TSFM, no gate scoring. Compute Ω_336 per test origin and **stratify S-26 MAE by Ω regime** (A/B/C). This isolates whether H2's "no further OT-linear gains" is uniform or regime-specific.

**Falsifiable acceptance (promotion is not the goal — insight is; but scored as a slice with MAE bounds):**
- **Primary (no-regression hold):** Re-derive S-26 `MAE(full 2161)=1.9909±0.0001` inside this harness (anchor check) — else harness is broken, REJECT.
- **Insight condition (informational, not promotion):** Report `MAE_A - MAE_C` (A=Ω<0.4 vs C=Ω>0.5). Three mutually exclusive outcomes, each closes a question:
  - (i) `MAE_A ≫ MAE_C` + `p(C)<0.15` → ETTh1 H=720 is dominantly unpredictable; saturation is expected; TSFM unlikely to help (justifies not paying for Slice 1).
  - (ii) `MAE_A ≈ MAE_C` (Δ<0.05) → Ω does not stratify error on ETTh1 — paper's regime partition does not transfer (negative result, publishable).
  - (iii) `MAE_A ≪ MAE_C` inverted → Ω anti-correlated (would indicate conditioning bug — e.g. detrending mismatch).
- **Falsifiable bound for future TSFM justification:** Slice 2 **passes** (as a gate-opener) if `P(Ω>0.5) ≥ 0.20` AND `MAE_C(S-26) - MAE_A(S-26) > 0.10` (high-Ω windows exist and are meaningfully harder/easier for S-26) — then Slice 1's TSFM attempt is justified. Otherwise Slice 1 is deprioritized as low-yield.

**Lane & cost:** SMALL (no TSFM, no ridge fits beyond S-26 re-derivation). Seconds.

---

## 7. Anti-Leakage & Protocol Notes

- **History-only Ω:** Same containment as `BaseForecaster.history_` — Ω window must be `history[-L:]` before the scored horizon, never `eval_series[t:t+L]` straddling the test window. The harness asserts `window_end < forecast_start`.
- **No val-tuned threshold:** 0.4/0.5 are paper constants, not grid-searched on val. This is load-bearing — S-16c/S-21/S-36 all failed by val-tuning a scalar gate. Ω's value is that thresholds are external.
- **Three L arms, one primary:** L=336 is primary (matches S-26 lookback). L=96/720 are diagnostic — if regime mass flips with L, report it; do not pick the best L post-hoc (that would be S-27-style banding, which H2 already rejected at p=0.0045).
- **No new trained parameters:** Slice 1's gate has 0 learned weights; Slice 2 has 0. This keeps the comparison to S-26 protocol-clean.

---

## 8. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ETTh1 windows below T>1000 (L=720 < 1000) → Ω higher variance | High | Paper §5.3 precondition: T>1000 for stability. Report with caveat; do not over-interpret thresholds on short windows. Sensitivity arms L=96/336/720 surface variance. |
| ETTh1 H=720 is mostly Ω<0.4 (no C mass) → Slice 1 has no TSFM calls | Medium | Expected per H2 saturation; Slice 2 documents it as a negative result with `call_rate`; still a successful slice (saves cost). |
| TSFM zero-shot weaker than S-26 even on C windows (60% claim from shorter horizons) | Medium | Gate still reports; if `MAE_gated > 1.9909`, REJECT and document non-transfer. No promotion. |
| Ω correlates with volatility, not orthogonal spectral info (S-36 déjà vu) | Medium | Report `ρ(Ω, σ)` in §5.4; if |ρ|>0.6, gate is volatility-gating relabeled — compare to S-36 rejected result. |
| Ω distribution shifts val→test (S-36 failure mode) | Medium | Guard 2 in Slice 1 fails loud; declare non-stationary. |
| Non-stationarity / regime shifts (paper §6.2 strongest failure mode) | Medium | Paper: Ω assumes stationary spectrum; high LLE / structural breaks mislead aggregate Ω. Flag windows with regime-shift warnings; high-LLE check. |

---

## 9. References (Paper-Exact)

- Wang et al. arXiv:2511.08884 — §§2–3, §A.4 definition; §5.3 preconditions (T>1000, stationarity); §A.2 multivariate mean Ω; `gift_eval/compute_metrics_fast.py:77–135` repo deviation; `RESEARCH/2026-09-12_spectral-predictability-omega.md` — paper-exact verification source.
- Additional verification: `h720/data.py` — split/rolling protocol; `brains/ts_brain/corpus/01_h720_evaluation_protocol.md`, `02_anti_leakage_invariants.md`; `RESEARCH/next-frontier-scout-2026-09-12.md` bets 1–3.

---

## 10. Immediate Action

1. Land `h720/sub_experiments/spectral_omega_gate/compute_omega.py` + `rolling_arm.py` (phase 1: no TSFM) and publish `results_omega.json` with Ω distributions and S-26 residual correlations.
2. If Slice 2 opener holds (`P(C)≥0.20` and stratified Δ>0.10), proceed to Slice 1 with one pinned TSFM adapter; else document Ω-gated "keep S-26" result and close.

*Paper-exact per Wang et al. §A.4 — DC removal → Hann taper → one-sided PSD k=1..K K=floor(T/2) → p_k → H → Ω=1-H/Hmax; repo `compute_metrics_fast.py` requires caller-side `x*np.hanning` for paper-exact; T>1000 + stationarity preconditions + mean-Ω multivariate (§A.2).*
