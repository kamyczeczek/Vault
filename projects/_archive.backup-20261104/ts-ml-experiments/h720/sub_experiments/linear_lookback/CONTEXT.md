---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-experiment: Long-lookback linear family (S-06)

## Purpose
Score the linear family at long lookbacks under the canonical rolling
protocol (frozen fit on train.csv 11,425 rows; 2,161 stride-1 origins),
per the S-06 slice contract (`PROCESS/03_plan/slices.md`):
- **NLinear** (last-value anchoring) chain L ∈ {96, 336, 720} at the
  legacy default ridge_alpha=1.0 — first rolling numbers for NLinear
  at all (it was t=0-only before: legacy 2.3507).
- **RLinear** (NEW model, S-06): RevIN-standardized window (per-window
  mu/sigma, `_SCALE_EPS` clamp), no structural transform — the
  standardized raw window IS the feature vector. OLS (a=0) and Ridge
  (a=1) at L ∈ {336, 720}.
- **DLinear L=720** completes the S-05 chain 96 → 336 → 720.

Design note: one alpha per family keeps the lookback chain
unconfounded (NLinear a=1 legacy default; DLinear/RLinear a=0 OLS
— S-05 showed Ridge=OLS for these features).

## Directory structure
- `smoke_registry.py` — registry-wide smoke test (10 models:
  construct default config, fit 2,200 synthetic rows, predict 720
  finite values). Implements the prevention rule from S-05 P1
  (lost-import guard); routed into `PROCESS/04_implement/CONTEXT.md`.
- `regression_gate.py` — 5 anchors: the 4 canonical t=0 models
  (ELM 1.5923/1.9823, kNN 1.7204/2.1405, persistence 1.7952/2.2503,
  daily 1.6720/2.1719) + NLinear legacy t=0 reference
  2.3507/2.8173 (default input_length=336, a=1.0).
- `run_sweep.py` — rolling sweep, 8 configs + 3 fail-loud rolling
  anchors (ELM 2.3092, daily 2.5491, persistence 2.5985).
- `results.json` — machine-readable output incl. lookback chains.

## Results (rolling, frozen fit, 2,161 stride-1 origins)

| model | rolling MAE | rolling RMSE | note |
|-------|------------|--------------|------|
| **nlinear_L336_a1** | **2.0571** | **2.5071** | **new leaderboard leader** |
| nlinear_L96_a1 | 2.0925 | 2.5612 | NLinear rolling baseline |
| rlinear_L336_a0 | 2.1220 | 2.6025 | ≡ dlinear_L336 (see below) |
| rlinear_L336_a1 | 2.1220 | 2.6025 | Ridge = OLS (well-conditioned) |
| nlinear_L720_a1 | 2.1534 | 2.6003 | |
| rlinear_L720_a0 | 2.1687 | 2.6356 | ≡ dlinear_L720 |
| rlinear_L720_a1 | 2.1687 | 2.6356 | |
| dlinear_L720_a0 | 2.1687 | 2.6356 | completes DLinear chain |

Anchors: ELM 2.3092 ✓, daily 2.5491 ✓, persistence 2.5985 ✓
(fail-loud, all OK). Regression gate 5/5 OK. Registry smoke 10/10 OK.

## Key findings

1. **NLinear L=336 (a=1) is the new rolling leader: 2.0571**
   (previous leader: DLinear L96 2.1163, −0.059). NLinear's
   last-value anchoring + ridge beats the RevIN-standardized family
   on this series at every shared lookback (2.0925 vs 2.1163 at L96;
   2.0571 vs 2.1220 at L336).
2. **RLinear ≡ DLinear row-for-row on identical L** (2.1220 at 336,
   2.1687 at 720, both alphas): the moving-average decomposition is
   an invertible linear re-parametrization of the window's column
   span, so the joint OLS solution is unchanged — the
   **Toner-Darlow equivalence**, now confirmed empirically
   in-project at H=720. DLinear's S-05 win over the legacy artifact
   is therefore attributable to RevIN-standardization + joint solve,
   NOT to the decomposition itself.
3. **Published lookback effect refuted in-project**: longer is NOT
   better for ETTh1 at H=720 rolling. NLinear peaks at L=336
   (2.0571), degrades at L=720 (2.1534); DLinear/RLinear peak at
   L=96 (2.1163). Chain monotonicity (acceptance criterion) is
   recorded in `results.json` → `lookback_chains`; there is no
   monotone L=96→336→720 improvement in any family.
4. All 8 configs beat persistence (2.5985) — acceptance criterion
   "all rows beat persistence" met with wide margin (best 2.0571,
   worst 2.1687).

## Verification gates (all passed 2026-09-03)
- Registry-wide smoke: 10/10 (incl. user-WIP ELMTree).
- Regression gate: 5/5 anchors 4-decimal.
- Rolling anchors: 3/3 fail-loud OK.
- Determinism: full re-run after the chain-lookup fix reproduced
  every rolling number exactly.
