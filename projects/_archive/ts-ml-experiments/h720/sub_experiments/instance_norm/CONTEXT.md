---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-Experiment: Instance Normalization (window-std, RevIN-style) — S-04

## Question
Does RevIN-style scale normalization (divide lag features AND targets by the
trailing-window population std at each origin, then re-scale predictions)
improve the rolling-origin MAE of the HeuristicLag* pipeline (ETTh1 OT,
H=720)? Does the optional per-output affine readout add anything on top?
Plan slice: `PROCESS/03_plan/slices.md` S-04 (acceptance: rolling MAE
normalized-vs-parent at equal config, delta in raw AND train-σ units,
win/lose vs daily under the same protocol).

## Protocol (identical to S-01/S-03 canonical)
- Frozen fit: every model fit once on all of `train.csv` (11,425 rows).
- Rolling: 2,161 stride-1 origins; at origin `t`, `history_ = eval_series[:11425+t]`.
- Normalization (S-04): per-origin `scale(i) = std(series[i-w:i])` (population,
  window `w ∈ {168, 720}`, clamp `_SCALE_EPS=1e-8`); `X` and `Y` divided by it;
  prediction multiplied by the forecast-time window std, then anchor added.
- Affine: per-output least squares `(γ, β)` mapping in-sample standardized
  predictions to targets; kNN fitted on leave-one-out predictions (in-sample
  kNN is degenerate — each point is its own zero-distance neighbour).
- Anchors (fail-loud, all OK): parents + daily + persistence reproduce S-01
  rolling numbers AND legacy t=0 numbers at 4 decimals.

## Results — rolling (2,161 origins, frozen fit; train-σ = 8.3684)

| model | MAE | RMSE | Δ MAE vs parent (raw) | Δ (train-σ) | vs daily |
|---|---|---|---|---|---|
| elm_parent (h64, full, normal) | 2.3092 | 2.8046 | — | — | win |
| elm_norm168 | 2.3289 | 2.8330 | +0.0197 | +0.0024 | win |
| elm_norm168_affine | 2.3293 | 2.8334 | +0.0201 | +0.0024 | win |
| elm_norm720 | 2.3740 | 2.8820 | +0.0648 | +0.0077 | win |
| elm_norm720_affine | 2.3749 | 2.8829 | +0.0657 | +0.0079 | win |
| knn_parent (q3, k32, 10%) | 2.5583 | 3.0994 | — | — | lose |
| knn_norm168 | 2.4440 | 2.9532 | −0.1143 | −0.0137 | win |
| knn_norm168_affine | 2.5164 | 3.0359 | −0.0419 | −0.0050 | win |
| **knn_norm720** | **2.3815** | **2.8745** | **−0.1768** | **−0.0211** | **win** |
| knn_norm720_affine | 2.4053 | 2.9004 | −0.1530 | −0.0183 | win |
| daily (reference) | 2.5491 | 3.1120 | — | — | — |
| persistence (reference) | 2.5985 | 3.1282 | — | — | — |

Full metrics (disjoint windows, t=0 anchors, config details): `results.json`.

## Key Findings
1. **Normalization is family-dependent — model-class, not free lunch.**
   It HURTS the ELM (+0.020 best-case, +0.003 σ-units): the ridge readout on
   anchor-differenced features is already scale-robust, and dividing by a
   short noisy window std injects variance. It HELPS kNN strongly (−0.177 at
   w=720): the Euclidean distance metric is scale-sensitive, and per-origin
   scaling makes neighbours comparable across regimes.
2. **Window length optimum is family-dependent too**: kNN wants the LONG
   window (720 ≫ 168: −0.177 vs −0.114) — regime-scale estimation needs a
   month of data; ELM least-harm is the SHORT window (168 < 720: +0.020 vs
   +0.065) — less scale-estimation noise injected into a scale-robust readout.
3. **Affine readout adds nothing here** (neutral-to-negative in both
   families; worst case kNN norm@168 +0.072). The anchor+differencing
   machinery already handles level shifts; the learnable γ/β adds estimation
   variance without systematic bias to correct.
4. **Verdict flip**: parent kNN (2.5583) LOSES to daily (2.5491); every
   normalized kNN variant WINS (best knn_norm720 by 6.6%). Instance
   normalization flips the kNN-vs-daily verdict — and knn_norm720 becomes
   the best kNN config on the canonical rolling leaderboard.
5. **Leader unchanged**: ELM h64 full normal (2.3092) survives S-04; the
   kNN gap to ELM narrows from 0.249 to 0.073.

## Directory Structure
- `run_sweep.py` — sweep harness (anchors, 10 configs + 2 references).
- `results.json` — per-config rolling + disjoint metrics, deltas, anchors.

Re-run: `python sub_experiments/instance_norm/run_sweep.py` (from `h720/`).
