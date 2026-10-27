---
type: Concept
title: LONGTERM_ETTH1_H720_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# S49 — ETTh1 H720 Long-Term Specialist Methods (design-first, PRE-REGISTERED)

**Status:** pre-registration (binding, S43-P1 discipline). Code + run land in the same PR as results.
**Execution status (2026-09-24):** SAB-L and H2K completed and rejected; AMR-24/168 is the next candidate. The original gates below remain the binding protocol for the next member; H2K's result is recorded in `H2K_H720_RESULT.md`.
**Motivation (per `REFLECTION_PROMISING_METHODS.md`):** H720 ETTh1 is saturated — incumbent S44 `1.9781`, S46/S48 REJECTED. Our members were tuned at H24–H336; H720 (30 days) breaks motif phase alignment and makes single-ridge 720-dim readouts ill-conditioned. The gap is a *long-horizon architecture*, not another ELM width bump.

## Suite (pre-registered)
- **Task:** ETTh1 H720 rolling, **W=20 locked eval origins** + separate dev origins for any selection (leakage-safe). Train slice identical to S44 (same cutoff, same normalization).
- **Variability:** frozen-random components (ELM/ESN-style dicts) → **5 seeds**, report mean±std.
- **Reporting:** raw MAE **and** normalized MAE (scale must always be stated — reflection finding #1).
- **Regression suite:** every member also run at H96/H336 (gate G3).

## Members (new, H720-specialized — build on proven components only)
1. **H2K — Horizon-Decomposed Drift-Corrected KNN**: split H720 into 3×240 segments. Per segment: detrended motif-KNN on residuals + linear drift carry-forward (level anchored on previous segment's last-24h mean). Exploits KNN's cyclical strength; fixes long-horizon phase drift.
2. **SAB-L — Signal-Adaptive BigDict Long**: scale-mismatch-optimized filter bank (standardized cD* + compact config per the ablation), **L=336 context**, horizon-**grouped** ridge readouts (heads H∈{24,48,96,…} — never one 720-dim ridge), 5 seeds.
3. **AMR-24/168 — Multi-Scale AMR-FBS Envelope**: FFT envelope on 24h + 168h harmonics + weekly drift anchor (7-day mean level); per-horizon ridge. Extends the only method that already wins H720 normalized (0.473 vs DLinear 0.602).
4. **Meta-H (optional, last)**: leakage-safe per-horizon-block selector over {H2K, SAB-L, AMR-24/168}, fitted on dev origins only.

## Completed candidates
- **SAB-L:** rejected after the two-iteration kill budget; final locked mean raw MAE 4.4611.
- **H2K:** implemented, tested, and evaluated under the early-dev/locked-final protocol; final mean raw MAE 2.7270, not promoted. See `H2K_H720_RESULT.md`.

## Gates (binding, pre-registered)
- **G1:** mean rolling MAE (raw) H720 **< 1.9781** (incumbent S44).
- **G2:** beat DLinear and SpectralFFT at H720 (raw).
- **G3:** no-regression — H96/H336 MAE within +5% of that member's S47-pool best (a long-term specialist must not be a regime-breaker).
- **G4 (diagnostic):** mean rank ≤ 2 across {members + SOTA baselines} at H720.
- **PASS = G1 ∧ G2 ∧ G3.** All members fail → **REJECT S49** after the 2-iteration kill budget (Fail Fast & Cheap; S46/S48 precedent).
- Null-result clause: incumbent gap < 0.02 normalized → treat as saturation, not win.

## Pre-registered risks & mitigations
- Saturation ceiling (mitigated by null-result clause + G3 regression guard) · selection leakage (dev-only, seeds locked pre-run) · 720-dim ridge conditioning (horizon-grouped heads) · KNN hyperparameter fragility (per-dataset k pinned, stability sweep k∈{5,12,24,48}).
- **Dependency:** P0 BigDict standardization control must precede SAB-L (its feature bank depends on the control's verdict).

## Effort
Each member ≈ <1 day CPU; full S49 suite ≈ 20–40 min (matches project "seconds-to-minutes" charter).
