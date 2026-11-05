---
type: Concept
title: S48_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S48 — SWT Subband-Expert Stack on S-44 (H720)

**Status:** PRE-REGISTRATION (binding per S43 P1). Code + run land same PR.

## Hypothesis
S-47 proved on the 6-task mini suite that the **approximation subband `cA`** carries signal as a direct Ridge expert, while pooled ELM is noise. Apply that intelligent merge to H720: decompose the `L=336` anchored window via **SWT db4 J=3 periodization** into **4 orthogonal subband signals** `cA3, d3, d2, d1` (each length 336) and fit **4 separate per-horizon Ridge experts** directly on those signals (no pooling, no ELM). The per-horizon stack can then learn frequency-dependent weighting per horizon step, which S46's `F=12` pooled vector could not.

## Pool
`M=8`:
- S-44 frozen `M=4`: `nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L, patchtst_P48_D16_1L`
- New `4` subband experts: `subband_cA3, subband_d3, subband_d2, subband_d1` (SWT db4 J=3, `α=100` fixed, vectorized Cholesky)

`M=8` tabu on `H=720` `W=2161` rolling origins.

## Protocol
S-20-clean identical to S-44/S-46: `val` members frozen `8545`, `test` members refrozen `11425`; tabu-7 fixed-α fast 3000 aspiration `no_improve 5`; per-horizon ridge no-intercept `11-α grid [0.1..30000]` on `val[0:1080)→val[1080:2161)` chronological half-split; held-out S-44 control precondition; frozen test stack on `11425`-refit test preds; S-44 parity block `9` checks `tol 1e-4`.

## Gates (binding BLEND-based vs in-harness S-44, per S43 P1)
- G1 `full ≤ 1.9731` (S-44 full `1.9781` minus 0.005)
- G2 `full < 1.9781`
- G3 `disjoint-4 ≤ 1.8634`
- G4 `paired Δ 95% CI upper < 0` (B=2000, vs re-derived S-44)

All four → PROMOTE; otherwise REJECTED. Close conditions: tabu picks no subband, or `G1–G3` any fails.

## Member fit
Per subband: `X_band = SWT_band(anchored_window)` shape `(n,336)`, `Y = anchored deltas (n,720)`, `W_band = _ridge_multioutput(X_band, Y, 100.0)` shape `(336,720)`. Predict: `SWT(hist_anchored)[band] @ W_band + anchor`.
Reuse `anchored_wavelet_elm._ridge_multioutput` and `pywt.swt` periodization.

## Expected wall
~6h (same as S-44 + 4 small Ridge fits per fold). No ELM overhead.
