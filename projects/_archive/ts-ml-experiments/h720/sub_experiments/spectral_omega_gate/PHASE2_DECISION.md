---
type: Concept
title: PHASE2_DECISION
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Phase 2 Decision — Spectral Omega-Gated TSFM Ensemble (Chronos-Bolt Base)

**Date:** 2026-09-13
**Slice:** `spectral_omega_gate_phase2`
**Harness:** `rolling_arm_phase2.py --origins disjoint4` + `rolling_arm_phase2.py --origins sampled`
**Protocol:** S-20-clean — members frozen train 8545 for val, refit 11425 for test; TSFM Chronos-Bolt Base zero-shot; hard gate Omega_336 > 0.5
**Artifacts:** `results_tsfm_phase2.json` · `harness.log`
**Harness commands:**
- `C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/rolling_arm_phase2.py --origins disjoint4`
- `C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/rolling_arm_phase2.py --origins sampled`

---

## 1. Verdict Table

| Scope | Metric | Value | Threshold | Verdict |
|---|---|---|---|---|
| **Disjoint-4** (decision path) | `disjoint_4_mae` (gated) | **1.8739** | ≤ 1.9696 (S-26 disjoint cap) | **PROMOTED (disjoint4)** |
| S-26 anchor disjoint-4 | `disjoint_4_mae` (S-26) | 1.9696 | — | — |
| **Sampled (weighted full estimate)** | `full_mae` (gated, weighted) | **2.1218** | ≤ 1.9859 (≥0.0050 vs S-26 1.9909) | **REJECTED** |
| S-26 anchor full | `full_mae` (S-26) | 1.9909 | — | — |
| Sampled 95% CI | bootstrap B=2000 | **[1.9733, 2.2847]** | must exclude 1.9859 on low side to claim | **FAIL — lower bound 1.9733 < 1.9859 but point 2.1218 ≫ threshold; CI straddles/inc. threshold from above** |
| Guards (all individually) | stationarity / correlation / call-rate / disjoint | pass | — | **PASS** |
| Primary accuracy guard | sampled full MAE ≤ 1.9859 | **2.1218 > 1.9859** | ≤ 1.9859 | **FAIL on sampled** |

**Combined verdict:** **REJECTED for full-mode promotion.** Disjoint-4 PROMOTED (1.8739 ≤ 1.9696) remains true in isolation, but **sampled REJECTED overrides disjoint-only promotion for full-mode promotion** per `TSFM_SLICE_SPEC.md` §3 (all four gates required, primary accuracy gate is sampled/full). `results_tsfm_phase2.json` now records `mode: sampled`, `estimated: true`, `metrics.verdict: REJECTED`, `estimated_full_mae: 2.1218` (null before sampled run). **S-26 (1.9909) remains the terminal full-2161 incumbent.**

### Latency

- **Disjoint-4 run:** harness **25.1 s** wall, TSFM **11.1 s** over **2 calls** (disjoint origins 0 and 2 gated; origins 1,3 routed to S-26), warmup 5.56 s.
- **Sampled run:** harness **104.4 s** wall, TSFM **94.7 s** over **22 calls** (64 origins = 60 stratified + 4 disjoint, seed=0; 22 gated where Omega>0.5), warmup 4.09 s. Per-origin serial ≈4.3 s avg (94.7/22).
- **Gate:** Omega_336 > 0.5, call_rate **0.5391** (1165/2161 projected; sampled 22/64 gated), consistent across both modes.

---

## 2. Guard Status

| Guard | Value | Threshold | Status |
|---|---|---|---|
| Disjoint stability (Guard 2) | disjoint-4 MAE **1.8739** ≤ 1.9696 | ≤ 1.9696 | **PASS** (−0.0957 vs S-26 disjoint) — still true after sampled |
| Val→test stationarity (Guard 3) | |Ω_test − Ω_val|/σ_val = **0.3832** | < 0.5 | **PASS** (val 0.4755±0.0862, test 0.5086±0.0661) |
| Correlation orthogonality (Guard 4) | Spearman ρ(Ω_336, S-26 MAE) = **−0.0802**, p=1.89e-04; partial ρ|σ = −0.2252, p=2.97e-26 | ρ < 0, p < 0.01 | **PASS** |
| Call-rate sanity | **0.5391** (1165/2161; sampled 22/64) | ≥ 0.10 | **PASS** |
| **Primary accuracy (Guard 1)** | **sampled weighted full MAE 2.1218** vs 1.9859 cap (S-26 1.9909) | ≤ 1.9859 | **FAIL on sampled** |

All non-accuracy guards pass individually; the primary accuracy guard **FAILs on the sampled estimate**, which is the binding gate for full-mode promotion. The guards table is retained as all-pass-individually with this explicit primary FAIL note.

---

## 3. Sampled Estimate Detail (new — overrides disjoint-only narrative)

- **Mode:** `sampled` — 64 origins = 60 stratified (20 per Omega bucket A/B/C) + 4 disjoint anchors (seed=0, union 64 distinct). Weighted full MAE via population weights (pop N_A=113, N_B=883, N_C=1165; w_A=0.0523, w_B=0.4086, w_C=0.5391).
- **Weighted full MAE (gated):** **2.1218** (was `null` before sampled run; `metrics.full_mae: 2.1218`, `estimated_full_mae: 2.1218`, `estimated: true`, `mode: sampled`, `truncated: false`). Simple sampled mean 2.1304 for reference.
- **Bootstrap 95% CI:** **[1.9733, 2.2847]**, **B=2000**. Lower bound sits below the 1.9859 cap but the point estimate is 0.1359 above it and 0.1309 above S-26; CI does not support a sub-threshold claim.
- **TSFM calls:** **22** (sampled gated), wall **104.4 s**, TSFM **94.7 s** (vs disjoint4: 2 calls, 25.1 s wall, 11.1 s TSFM).
- **Bucket MAEs (stratified, gated):** **A 2.1993** (n=21, w=0.0523) / **B 1.9109** (n=21, w=0.4086) / **C 2.2741** (n=22, w=0.5391). **Bucket C worst — TSFM degrades where gate fires.** The gate routes to TSFM precisely where Omega>0.5 (C), yet C's MAE is the highest of the three buckets and the dominant weight (53.9%) drives the weighted mean upward. B (mid-Omega, S-26-routed majority) is the only bucket beating S-26.
- **Projected full-array MAE (S-26 fallback for missing origins):** 1.9956 (diagnostic; not the decision metric — weighted estimate is binding).
- **Disjoint-4 within sampled run:** **1.8739 / RMSE 2.4448** — unchanged from disjoint-only run, still PROMOTED on that path.

---

## 4. Combined Verdict — Why Sampled Overrides Disjoint

> **Sampled REJECTED overrides disjoint-only PROMOTED for full-mode promotion.**

- Disjoint-4 passing is **necessary but not sufficient** for a full promotion; it is sufficient to reject a bad regime, but a full promotion must still clear Guard 1 (≤ 1.9859) on the full set. This was stated as PENDING in the disjoint-only version.
- The sampled run **is that Guard-1 test**: weighted 2.1218 ≥ 1.9859 and ≥ S-26 1.9909 (`improvement_vs_s26: -0.1309`), so the slice is **REJECTED for full-mode promotion** despite retaining its disjoint-4 PROMOTED status in isolation.
- Per `TSFM_SLICE_SPEC.md` §3 and `phase2_inspect.md` Option A/B, the sampled estimate with CI is the legitimate decision path on this CPU; the full-2161 rollout (~108 min at 6.16 s/origin serial, 9.0× batch overhead) remains the GPU ground truth but is not required to finalize the REJECTED outcome — the sampled point is already 0.13 above S-26.
- **S-26 (1.9909/2.4710) remains the terminal full-2161 incumbent.** `plan_impact.invalidates: "Omega-gated TSFM as SOTA promotion ..."` and `confirms: "S-26 remains terminal ..."` in `results_tsfm_phase2.json` reflect this.

---

## 5. Next Steps

- **No further TSFM promotion attempt on this gate/threshold** — bucket C result shows the Omega>0.5 gate is anti-selective (TSFM worst where it fires). Any follow-up must propose a different gate, a fine-tuned TSFM, or a non-zero-shot adaptation; re-running disjoint-4 or sampled with the same Chronos-Bolt Base + 0.5 threshold will not change the verdict.
- **Full-2161 GPU run (`--origins full --device cuda`)** remains the optional ground-truth validation of the sampled estimate, not a promotion path for this configuration.
- **Fast CI smoke (`smoke_tsfm.py`, <2 min, H=64 native + 1×H=720)** still useful as a pre-merge API regression guard, not a promotion gate.
- **Document negative result** and close univariate-linear + zero-shot TSFM gating under this protocol (see `results_tsfm_phase2.json: plan_impact.opens`).
