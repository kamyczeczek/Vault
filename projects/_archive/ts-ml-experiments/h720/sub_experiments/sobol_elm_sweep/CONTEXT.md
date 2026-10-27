---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-Experiment: Sobol Quasi-Random Weight Init for HeuristicLagELM (H=720)

## Purpose
Test whether placing ELM hidden neurons *regularly across the
lag-feature space* (scrambled Sobol low-discrepancy sequence instead of
iid N(0,1)) improves whole-history fits. The prior ELM sweep showed
full history trailing the best recent window (1.6771 vs 1.6344); the
hypothesis was that coverage gaps in the weight draw degrade the
whole-history fit.

## Design
Matched pairs: `weight_init ∈ {sobol, normal}` at identical
`hidden_dim ∈ {64, 256, 1024, 4096}`, whole history
(`history_fraction = 1.0`), fast lags `(1, 2, 3, 6, 12)`.

- Sobol draw: `qmc.Sobol(d=len(delays)+1, scramble=True, seed=42)` →
  `ndtri()` (weights, unit normal quantiles) and affine `U(-1,1)`
  (biases). Same distributional targets as `normal`, different
  *placement* — quasi-random, space-filling.
- Normal draw: `RandomState(42)`, iid — the original scheme.

Protocol (locked, same as main leaderboard, via shared `data.py` split):
fit on all of `train.csv` (11,425 rows), forecast H=720, score against
the first 720 rows of `test.csv`. One identical chronological split for
every subexperiment.

## Results
| hidden_dim | sobol MAE | sobol_iid MAE | normal MAE | best |
|---:|---:|---:|---:|---|
| 64   | 1.8981 | 2.0317 | **1.5923** | normal |
| 256  | 1.7134 | **1.6330** | 1.7108 | sobol_iid |
| 1024 | 1.9293 | 1.8005 | **1.7504** | normal |
| 4096 | 2.2508 | 2.3042 | **2.2403** | normal |

## Findings
1. **Original hypothesis rejected.** Plain Sobol placement (ndtri grid)
   never beats iid normal — at 64 and 1024 markedly worse. The
   whole-history deficit of the ELM is *not* a weight-coverage artifact
   and must come from the training distribution itself (older origins
   pull the ridge solution away from the recent regime).
2. **`sobol_iid` (normal-mimicking Sobol) only wins at 256 neurons**
   (1.6330 vs 1.7108 normal, 1.7134 sobol) — the only configuration
   where Sobol placement plus iid-joint properties beats both
   references. At 64/1024/4096 it sits between or below them; at 64 it
   is the *worst* draw. Space-filling placement is not a robust
   substitute for iid randomness; where it helps (mid capacity), the
   gain is small and capacity-dependent.
3. **Leaderboard best is capacity-driven, not placement-driven:**
   normal-init ELM at `hidden_dim=64`, whole history, fast lags — MAE
   **1.5923** / RMSE 1.9823. Beats every Sobol variant at every width,
   the prior best (256n, recent 50%, 1.6344), and the daily baseline
   (1.6720). Capacity, not placement, was the differentiator.
4. Small hidden_dim + whole history is the winning region for this
   model family; the prior recent-window advantage inverted at 64
   neurons.

## Mimicry verification of `sobol_iid` (hidden 4096, d=5)
- Per-neuron norms: mean 2.128, std 0.688 — identical to `normal`
  (2.133/0.694), matching chi(5) (KS D=0.0002, p=1.0).
- Marginals: KS vs N(0,1) D=0.0039, p=0.913 (normal: p=0.902).
- Covariance ≈ identity: diag [0.997, 1.003], max off-diag 0.005.
- Isotropic: per-axis squared-mass share [0.199..0.201] (uniform ref 0.2).
- Spread: mean nearest-neighbour angle 0.181 rad vs normal 0.173 —
  Sobol-level space-filling with normal-joint statistics.

## Design note
`sobol_iid` = Sobol placement + iid-normal joint properties: directions
from a Sobol grid (normalised), radii from chi(d) quantiles of a Sobol
coordinate (norm diversity), a random QR-rotation kills the ndtri
grid's cubic-axis structure (isotropy), biases from the last Sobol
coordinate (U(-1,1)). See `methods/neural_models.py::_init_weights`.

## Directory Structure
- `CONTEXT.md` — this document
- `run_sweep.py` — matched-pair sweep script
- `results.json` — metrics + matched pairs
- `interactive.html` — ground truth vs best/worst/normal reference
