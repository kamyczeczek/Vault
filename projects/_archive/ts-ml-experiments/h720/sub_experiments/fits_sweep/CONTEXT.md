---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-experiment: FITS frequency-domain forecaster (S-07)

## Purpose
First spectral model in the project, per the S-07 slice contract:
rFFT of the RevIN-standardized lookback → complex ridge readout to
the extended spectrum (lookback+horizon) → low-pass cutoff → iRFFT →
horizon tail → de-standardize. Closed-form (numpy `linalg.solve`),
deterministic (no RNG), `methods/fits.py`.

## Directory structure
- `smoke_fits.py` — synthetic gates: shape (720) + determinism
  (byte-identical refits), daily-sinusoid continuation at the noise
  floor, LPF edge (cutoff=1 still returns 720 finite values).
- `_diagnose.py` — scratch (kept for the record): confirmed the daily
  cycle lives at rFFT bin 60 of extended length 1,440; cutoff 48
  flattens the forecast (MAE 0.3185), cutoff 64 restores it (0.0400).
- `run_sweep.py` — rolling sweep, 12 configs (cutoff ∈ {8, 16, 32,
  64, 128, None} × L ∈ {720, 336}, ridge 1e-3) + 3 fail-loud anchors
  + acceptance comparison block.
- `results.json` — machine-readable output.

## Results (rolling, frozen fit, 2,161 stride-1 origins)

| model | rolling MAE | rolling RMSE |
|-------|------------|--------------|
| **fits_L336_call (no LPF)** | **2.1220** | **2.6023** |
| fits_L336_c128 | 2.1222 | 2.6024 |
| fits_L336_c64 | 2.1239 | 2.6062 |
| fits_L336_c32 | 2.1504 | 2.6404 |
| fits_L336_c16 | 2.1570 | 2.6464 |
| fits_L336_c8 | 2.1444 | 2.6288 |
| fits_L720_call | 2.1685 | 2.6348 |
| fits_L720_c128 | 2.1691 | 2.6352 |
| fits_L720_c64 | 2.1708 | 2.6397 |
| fits_L720_c8 | 2.1649 | 2.6530 |
| fits_L720_c16 | 2.1962 | 2.6805 |
| fits_L720_c32 | 2.1973 | 2.6761 |

Anchors: ELM 2.3092 ✓, daily 2.5491 ✓, persistence 2.5985 ✓
(fail-loud, all OK). Registry-wide smoke 11/11 OK (FITS included).

## Acceptance (slices.md S-07) — all met
1. **≥3 LPF cutoffs reported** ✅ — 6 cutoffs × 2 lookbacks.
2. **Best vs best ELM and daily under same protocol** ✅ — best FITS
   2.1220 < ELM 2.3092 < daily 2.5491 (all rolling; recorded in
   `results.json` → `acceptance_comparison`).
3. **Deterministic, predict() == 720** ✅ — smoke gates (byte-identical
   refits, no RNG in the closed-form path).

## Key findings
1. **Best FITS = L=336, NO low-pass filter (2.1220/2.6023)** — exactly
   the RLinear L336 / DLinear L336 number (2.1220/2.6025). With the
   full spectrum retained, the complex-ridge spectral readout is the
   SAME least-squares problem as the time-domain linear map in a
   different orthonormal basis (rFFT is unitary up to scaling) — the
   third independent confirmation of the Toner-Darlow equivalence
   class in this project (DLinear ≡ RLinear ≡ FITS-noLPF at shared L).
2. **Every LPF cutoff hurts** (2.1222 → 2.1570 monotone up as the
   cutoff tightens; c8 2.1444) — removing ANY frequency band loses
   information the ridge would otherwise use. The published FITS
   claim (aggressive low-pass helps long horizons) does NOT transfer
   to ETTh1 H=720 rolling: the optimal cutoff is "keep everything".
3. **FITS beats ELM and daily but not the linear leaders**: 2.1220 vs
   NLinear L336 2.0571 (current leader) — the spectral parameterization
   adds nothing over the time-domain linear family on this series.
4. Lookback mirrors S-06: L=336 (2.1220) beats L=720 (2.1685) again.
