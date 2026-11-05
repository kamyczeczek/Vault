---
type: Concept
title: TSFM_SLICE_SPEC
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# TSFM Gated Slice Specification (Slice 1) — Spectral Predictability Ω Gate

**Date:** 2026-09-12
**Target Directory:** `projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/`
**Parent Integration Design:** `RESEARCH/2026-09-12_omega-h720-integration.md` §6 Slice 1
**Phase 1 Empirical Baseline:** `results_omega.json` (S-20-clean rolling origin, ETTh1 H=720 OT)

---

## 1. What (Core Mechanism & Gate Design)

- **Rule:** Hard threshold gate based on spectral predictability $\Omega_{336}$ computed on the history-only window ($L=336$):
  $$\Omega_{336} > 0.5 \implies \text{Frozen Zero-Shot TSFM},\quad \Omega_{336} \le 0.5 \implies \text{Incumbent S-26}$$
- **Threshold Origin:** Fixed externally from Wang et al. (arXiv:2511.08884 §5.2); **zero validation fitting** (no learned thresholds, no grid search on validation split) to prevent S-21/S-25/S-36 val-local overfit scars.
- **Protocol Compliance:** S-20-clean (members frozen on train 8,545 for val checks, refit on 11,425 for test scoring; chronological evaluation; full 2,161 rolling origins).

---

## 2. Candidate TSFM Pinned Version (Phase 2)

To move from Phase 1 (diagnostic-only) to Phase 2 (gated inference), exactly one foundation model is pinned:
- **Selected Model:** **Chronos-Bolt (Base)** (`amazon/chronos-bolt-base`, pinned via `transformers==4.40.0` / `chronos forecasting` stable tag).
- **Execution Mode:** Pure **zero-shot** (weights frozen, no ETTh1 fine-tuning, history window fed directly as context, generating 720-step horizon).
- **Justification:** Balances inference speed and open weights while matching GIFT-Eval taxonomy for zero-shot forecasting.

---

## 3. Falsifiable Acceptance Criteria (All Must Hold)

Promotion of the gated TSFM ensemble over the S-26 incumbent requires passing **all four** rigorous gates simultaneously:
1. **Primary Accuracy (Full 2161):** $\text{MAE}_{\text{gated}}(\text{full } 2161) \le 1.9859$ (representing a **$\ge 0.0050$ improvement** over S-26 incumbent $1.9909$). This is the same strict hurdle applied in H2.
2. **Disjoint Stability Guard:** $\text{MAE}_{\text{gated}}(\text{disjoint-4}) \le 1.9696$ (matching or beating S-26 disjoint cap). Prevents sparse-window noise-fitting (S-25 lesson).
3. **Val-to-Test Stationarity Guard:** $|\bar{\Omega}_{\text{test}} - \bar{\Omega}_{\text{val}}| / \sigma_{\text{val}} < 0.5$ for $L=336$.
   *Empirical status from Phase 1 (`results_omega.json`):* Observed shift is **$0.3832$**, which **passes** the $<0.5$ threshold ($\delta = 0.3832 < 0.5$).
4. **Correlation & Orthogonality Sanity:** Spearman rank correlation $\rho(\Omega_{336}, \text{MAE}_{\text{S26}}) < 0$ with $p < 0.01$.
   *Empirical status from Phase 1:* $\rho(\Omega_{336}, \text{MAE}) = -0.0802$ ($p = 0.000189$). Furthermore, controlling for rolling volatility ($\sigma$), the partial correlation $\rho(\Omega, \text{MAE} \mid \sigma) = -0.2252$ ($p = 2.97 \times 10^{-26}$), proving significant orthogonal predictive power beyond volatility ($\rho(\Omega_{336}, \sigma) = 0.5722, p = 3.5 \times 10^{-188}$).

---

## 4. Stratified Performance Baseline (Phase 1)

Performance of S-26 across $\Omega_{336}$ regimes:
- **Regime A ($\Omega_{336} < 0.4$, $n=113$):** MAE = $2.1229$
- **Regime B ($0.4 \le \Omega_{336} \le 0.5$, $n=883$):** MAE = $1.9905$
- **Regime C ($\Omega_{336} > 0.5$, $n=1165$):** MAE = $1.9784$

---

## 5. Why It Is Blocked Now

1. **Phase 1 Diagnostic Passed:** All Phase 1 guards passed successfully (shift $0.3832 < 0.5$, significant orthogonal correlation $\rho = -0.2252$).
2. **TSFM Unpinned / Not Integrated in Harness:** Phase 1 established the $\Omega$ distribution and residual correlations without running external foundation models. Chronos-Bolt inference harness and weights are not yet wired into `rolling_arm.py`.
3. **Status:** TSFM integration remains blocked purely on pinning and executing an external TSFM weight/runtime dependency (e.g. `chronos-bolt-base`).

---

## 6. Close Condition if REJECTED / Terminal Incumbent

If Phase 2 execution fails MAE acceptance ($\le 1.9859$) or Guard 2/3 fails:
- **Outcome:** **REJECTED**.
- **Action:** Officially document **keep S-26** as the terminal incumbent ($1.9909 / 2.4710$).
- **Compute-Saving Documentation:** Even when rejected for accuracy promotion, the $\Omega$ stratification proves that regime C baseline S-26 MAE is already highly optimized ($1.9784$). Document that paying zero-shot TSFM compute costs requires careful cost-benefit justification given S-26's strong low-level linear performance.
