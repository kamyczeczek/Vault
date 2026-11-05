---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-experiment: Cross-family ensemble (S-08)

## Purpose
Blend the three structurally-diverse strongest families (ELM h64 full,
kNN q3 k32 recent10, daily seasonal-naive) with non-negative, sum-1
weights fit on VALIDATION windows only (S-02 convention inside
`methods/ensemble.py`: 2,161 stride-1 origins over the trailing 2,880
validation rows, per-origin history = all rows strictly before the
scored window, members frozen on the full train+val fit series).
Members stay frozen; the test region is never consulted for weighting
(structural: `fit` receives only the 11,425-row `train.csv` series,
asserted in the runner).

## Directory structure
- `smoke_ensemble.py` — synthetic gates: simplex-projection units,
  shape (720), determinism (byte-identical refits), weights
  non-negative + sum-1, origin math (2,880 − 720 + 1 = 2,161).
- `_diagnose_weights.py` — scratch (kept for the record): acceptance
  pre-check of the weight objectives — prints per-member validation
  MAE from the residual matrix for BOTH the MSE-blend and the L1
  optimum; caught the residual-matrix axis-scrambling bug (see
  Findings).
- `_reconcile_val.py` — scratch (kept for the record): proved the
  ensemble-internal and runner window conventions are IDENTICAL
  (daily val MAE 3.4977 both ways) — the apparent discrepancy was
  inside the weight solver, not the window math.
- `run_sweep.py` — rolling sweep: ensemble + 3 members +
  persistence anchor, fail-loud 4-decimal anchor checks
  (ELM 2.3092 / daily 2.5491 / persistence 2.5985), acceptance
  block (validation boolean + test delta + weights + no-test
  assert + L1 diagnostic).
- `results.json` — machine-readable output.

## Weight solver (two objectives, both validation-only, no RNG)
1. **PRIMARY `weights_`** — squared-error blend: closed-form
   equality-constrained solve + Euclidean simplex projection (Duchi
   et al. 2008). The slice Goal is to *blend* the families; the MSE
   blend is the classic convex surrogate and produces a genuine
   3-family mix.
2. **DIAGNOSTIC `mae_weights_`** — the L1 optimum over the simplex
   (the acceptance metric itself): convex piecewise-linear objective,
   pairwise coordinate descent + exact 1-D ternary line search →
   global optimum, deterministic. On this data it degenerates to a
   VERTEX ([0, 1, 0] = pure kNN).

## Results (rolling, frozen fit, 2,161 stride-1 origins)

| model | rolling MAE | rolling RMSE |
|-------|------------|--------------|
| elm_h64_full_fastlags (member) | 2.3092 | 2.8046 |
| **cross_family_ensemble (MSE-blend)** | **2.3103** | **2.7957** |
| daily (member) | 2.5491 | 3.1120 |
| knn_q3_k32_recent10 (member) | 2.5583 | 3.0994 |
| persistence (anchor) | 2.5985 | 3.1282 |

Validation segment (weight-search windows): ensemble 2.7500 vs
members elm 3.1246 / knn 2.6566 / daily 3.4977. Primary weights
[elm 0.3048, knn 0.6056, daily 0.0896] — sum-1, non-negative ✓.

Anchors: ELM 2.3092 ✓, daily 2.5491 ✓, persistence 2.5985 ✓
(fail-loud, all OK). Registry-wide smoke 12/12 OK (ensemble
included; N_ROWS override `validation_rows=1000` for the synthetic
2,200-row budget — the default 2,880 exceeds it).

## Acceptance (slices.md S-08) — recorded, one boolean negative
1. **Boolean: ensemble ≤ min(members) on validation — FALSE**
   (2.7500 > 2.6566 kNN). The L1 diagnostic proves this is a DATA
   property, not a solver artifact: the global L1 optimum over the
   entire weight simplex is the kNN vertex itself — **no non-trivial
   blend of these members improves the best member's validation
   MAE**. Recorded in `results.json` → `acceptance.l1_diagnostic`.
2. **Test delta reported** ✅ — ensemble 2.3103 vs best member ELM
   2.3092: **+0.0011** (0.05%); ensemble sits between its members
   (ELM 2.3092 < ensemble < daily 2.5491 < kNN 2.5583).
3. **Weights reported** ✅ — [0.3048, 0.6056, 0.0896], non-negative,
   sum-1, from validation windows only.
4. **No test data for weighting** ✅ — structural: `fit` receives
   `train.csv` only; the runner asserts `len(fit_history) == 11,425`.

## Key findings
1. **L1-optimal blending degenerates to model selection**: the
   acceptance metric's optimum over the simplex is a vertex (pure
   kNN on validation). Convex-combination ensembling under MAE
   cannot beat the best member here — the three families' residual
   vectors are too co-linear in sign for cancellation on the L1
   ball. Recorded as the slice's central negative result.
2. **Rank flip between validation and test explains the test
   outcome**: kNN is the validation best (2.6566) but only third on
   test (2.5583 vs ELM's 2.3092); the MSE-blend inherits kNN's
   60.6% weight and lands 0.0011 above test-best ELM. Validation-
   weighted blending is only as good as the validation→test rank
   transfer — here it transfers poorly (S-02 measured the same
   kNN/daily flip).
3. **MSE vs MAE surrogate choice changes the ranking, not the
   verdict**: MSE-blend val 2.7500 vs L1-blend val 2.6566 (pure
   kNN) — the MSE blend is *worse* on the acceptance metric than
   just picking the validation-best member. Both objectives were
   kept in the model so this is auditable per-config.
4. **Ensemble does not reduce regime fragility**: ensemble W2
   (t=720) MAE 3.5902 — the kNN W2 blowup (4.9090) bleeds through
   the 60.6% weight; ELM's W2 is 1.8146. Weighting toward the
   validation-best member imported its fragility instead of
   diversifying it (W-window spread ensemble 2.26× vs ELM 1.36×).
5. **Two in-session bugs were caught by cross-checking, not by
   luck**: (a) the weight search lacked a length guard — synthetic
   smoke rows (2,200) < `validation_rows` (2,880) silently yielded
   a negative start index and an empty prediction array; now
   fail-loud. (b) the residual matrix was built with
   `(P − A).reshape(-1, m)` on an `(n, m, H)` array — C-order
   flattening scrambled member identity with horizon step,
   producing plausible-looking but garbage weights. The stateless
   daily member acted as the sensor: its "solo" score from the
   scrambled matrix (3.0962) could not match its known val MAE
   (3.4977) — a hard contradiction that localized the bug in one
   step. Both scratches are kept above.

## Verdict
Negative result, fully documented: validation-weighted convex
blending adds nothing over the best single family on ETTh1 H=720
rolling (+0.0011 test MAE vs ELM; L1-optimal blend = pure kNN).
Leaderboard unchanged (NLinear L=336 2.0571). No follow-on slice
depends on S-08's outcome; the ensemble stays in the registry as a
working, deterministic component (smoke-clean 12/12).
