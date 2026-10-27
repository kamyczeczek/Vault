---
type: Concept
title: SAB_L_H720_RESULT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# SAB-L H720 diagnostic and rejection (2026-09-24)

## Decision

**REJECT SAB-L as an S49 H720 specialist.** The two-iteration kill budget is exhausted. Do not spend more compute on SAB-L width, random-feature dimension, or further ridge/profile tuning. The next H720 candidates are H2K and AMR-24/168.

## What was wrong

Two batch transforms in `members/sab_l.py` mixed the sample and time axes:

- 2-D EMA smoothed across training windows (`axis=0`) during fit but did not smooth the single forecast context.
- 2-D moving average likewise smoothed across training windows during fit, producing train/forecast feature distributions that could never agree.

Both now operate along the time axis of each context and match the one-dimensional transform. Five focused regression tests in `test_sab_l.py` cover MA, EMA, single/batched context equivalence, agreement with BigDict's compact EMA bank, and finite leakage-safe fit/predict.

The feature-scaling path was also completed: train-only `mu_`/`sd_` are now applied during prediction, not only fitting.

## Controlled development evidence

The diagnostic origins (12240 and 16560) were already part of the canonical suite and are therefore **not independent development evidence**. They were used only to debug and isolate mechanisms:

| configuration | mean raw MAE, 2 diagnostic origins |
|---|---:|
| BigDictELM L96 | 1.4483 |
| SAB-L compact, grouped heads | 3.1868 |
| SAB-L approx, grouped heads | 4.2597 |
| SAB-L approx, direct H720 head | 4.8988 |

Grouped heads were better than a direct H720 head, but the cosine-only SAB-L architecture remained far behind BigDict. Artifacts: `results/sabl_dev_diagnostic.json`, `results/sabl_architecture_diagnostic.json`.

## Independent development selection

Four early origins (8640, 9360, 10080, 10800) were used to select a compact SAB-L ridge strength without consulting the later evaluation origins:

| configuration | mean raw MAE |
|---|---:|
| BigDictELM L96 | 2.8712 |
| compact SAB-L alpha=10 | 4.0023 |
| **compact SAB-L alpha=30 (selected)** | **3.7799** |
| compact SAB-L alpha=100 | 3.7910 |
| compact SAB-L alpha=300 | 3.8920 |
| compact SAB-L alpha=1000 | 3.8802 |

Artifact: `results/sabl_early_dev_selection.json`.

## Locked final evaluation

Frozen SAB-L configuration: L=336, compact bank, grouped heads, alpha=30, seed=42. Canonical genuine-ETTh1 protocol: 12 disjoint 30-day origins, fixed 360-day training window, leakage-safe, raw MAE.

| method | mean raw MAE | std | origins below 1.9781 |
|---|---:|---:|---:|
| BigDictELM | **2.4777** | 0.7051 | 3/12 |
| AMR-FBS | 2.5294 | 0.6552 | 3/12 |
| DLinear | 2.5384 | 0.5169 | 2/12 |
| KNN | 3.0345 | 0.9701 | 1/12 |
| **SAB-L (selected)** | **4.4611** | **1.2017** | **0/12** |
| SpectralFFT | 7.9853 | 5.4949 | 0/12 |

SAB-L beat BigDict on 0/12 origins, DLinear on 0/12, and AMR-FBS on 0/12. It fails G1 and G2 decisively. G1 cannot be evaluated fully until the H96/H336 regression suite, but the mandatory H720 gates already fail, so PASS is impossible.

Artifact: `results/etth1_h720_multi_origin_sliding360d_sabl_a30_compact.{json,md}`.

## Interpretation and next step

The initial catastrophic score was partly implementation error, but correcting it did not validate the method. A longer context plus grouped ridge heads is not enough to beat the proven L96 BigDict family. The next iteration should not be a minor SAB-L mutation; it should use a genuinely different long-horizon inductive bias:

1. **H2K:** horizon-decomposed, drift-corrected KNN/seasonal carry-forward.
2. **AMR-24/168:** explicit 24-hour and 168-hour envelope structure with weekly level anchoring.

Both must use separate early dev origins and a locked final protocol. No further tuning of SAB-L is justified.
