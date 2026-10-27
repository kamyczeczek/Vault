---
type: Concept
title: BIG_DICT_ELM_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# BigDictELM — Filter-Bank ELM with NLinear Anchor (benchmark-core)

**Idea you requested:** big dictionary of *filtered different versions* of features, big dict of *nonlinear combinations*, linear Ridge on top (ELM), + NLinear tricks.

**Status:** design. Implement: `members/big_dict_elm.py`. Wire: `bench.py`.

## Pipeline
```
x (L=96) -> anchor a=x[-1] -> xa = x - a
  |
  +-> Filter bank F (causal, O(L) each, numpy-only):
  |   [0] identity(xa)
  |   [1-4] MA causal: 3,6,12,24
  |   [5-6] EMA alpha 0.3, 0.7
  |   [7] diff1 (prepend 0)
  |   [8] diff2
  |   [9-10] HP residual: xa - MA12, xa - MA24
  |   [11-13] SWT db4 approx: level1..3 reconstructed to L (pywt, optional fallback to MA if unavailable)
  |   => F≈12-14 vectors length L => flat F_flat dim D0=F*L (≈1152-1344)
  |
  +-> Standardise (fit mu/sd on train F_flat, eps 1e-8)
  |
  +-> Nonlinear dictionary (frozen random, seed 42):
  |   Wr ~ N(0,1/D0)  shape (D0, Hdict) , Hdict=512
  |   b ~ U[0,2pi)    shape (Hdict)
  |   phi_rand = cos(F_std @ Wr + b)          [RFF]
  |   phi_sq   = (F_std[:, ::stride])^2       stride picks every k-th to keep small (64 dims)
  |   Phi = concat [ F_std , phi_rand , phi_sq ]  dim D = D0 + Hdict + 64
  |   activation alt: tanh also supported, cos default (bounded)
  |
  +-> Vectorized Ridge (no intercept, Cholesky) per horizon:
        W* = argmin ||Phi W - Y_delta||^2 + alpha||W||^2
        Y_delta = Y - a_train  (teacher anchor)
  +-> Predict: F_flat(hist-a) -> Phi -> delta_hat = Phi @ W* -> y_hat = delta_hat + a
  NLinear trick: anchor is last value, per-window; also passed as de-anchoring only (not as feature) to keep ELM stationary.
```

## Why this beats S46 pooled ELM
- S46 pooled: 1 wavelet pooled feature (12-d) -> ELM -> thin. BigDict keeps **time resolution** (no pooling) and **diversity** (12 filters), so dictionary covers trend/season/noise subspaces separately.
- S47 showed `subband_cA1/d1` direct Ridge wins on multiscale/seasonal; BigDict subsumes them as members of F.
- RFF dict is wider (512) than S46 hidden 96, still CPU-cheap (matmul 1k×512).

## Hyperparams (fast bench defaults)
- L=96 fixed (avoids H48/H96 mismatch); H varies per task.
- Hdict=512, sigma scale 1/sqrt(D0), alpha=10 (sweep [1,10,100] if budget).
- Ridge alpha grid search not needed for 6-task smoke; fev uses fixed 10.
- seed 42 frozen per task (train[:2000] fit).

## Complexity
Fit: O(n·D0 + n·D·Hdict + D³) with n≈1900, D≈1700 => <0.3s/task CPU. Predict O(L·F + D·H).

## bench.py wiring — new member `bigdict_elm`
- `fit_bigdict(train,H)` -> BigDictELM(...).fit(train, horizon=H)
- `pred_bigdict(model, hist)` -> model.predict_hist(hist)  (set history_)
- New pool D = A + [bigdict_elm]; suite report adds `Pool D` alongside A/B/C. Gates: G1 meanD<meanA-0.005, G2 rank<2, G3 wins≥½.

## Risks / ablations
- If `pywt` missing, SWT filters fallback to identity (no crash).
- If D large causes overfit on tiny `ou_H24`, Ridge alpha lifts to 100.
- Ablate: dict-only vs filter+dict vs filter+linear to isolate gain.

## Next step: implement `members/big_dict_elm.py` then wire.
