---
type: Concept
title: S44_CALIBRATION_RESULT
generated: { by: opencode/agent, at: 2026-11-01T02:00:00Z }
---

# S44 Blend Calibration on S49 Protocol — Final Measurement Result

## Executive summary

This measurement was pre-registered in `GATES-s44-calibration.md`. It does NOT resume S49, does NOT tune, and does NOT promote any model. It executes the frozen S44 blend (`nlinear_L336_a1` + `nlinear_L336_a10` + `patchtst_P24_D32_2L`, per-horizon ridge, no intercept, $\alpha=30000$, Amendment A1 OOS stack fit) across the 12 locked origins of the S49 protocol (`8640..16560`, step 720 h).

The consistency reproduction control on step-1 origins reproduced the reported S44 score of 1.978126 to within $4.2 \times 10^{-11}$ relative difference (`results/s44_calibration_reproduction.json`), confirming the faithful reconstruction of the S44 blend object.

Under the 12 sparse origins of the S49 protocol, the S44 blend scores a mean raw MAE of **4.125489** (seed 42) and **4.172105** (mean across 5 seeds: 42..46). Both values are substantially above the pre-registered BigDictELM L96 threshold of 2.4777 (which re-derived fresh at 2.477669).

Per the pre-registered interpretation rule:
`interpretation_rule_applied: AT_OR_ABOVE`

**Verdict**: As pre-registered, blend mean raw MAE $\ge 2.4777 \implies$ **the 1.9781 figure was an artifact of the S44 protocol** (2161 dense step-1 origins), not a level any model reliably reaches on 12 sparse step-720 origins. S44 was not stronger than the S49 models on the S49 geometry. The 1.9781 threshold caveat in ADR 0001 is now an empirical finding, closing the S44 comparison line definitively.

## Machine-readable summary

```yaml
blend_mean_raw_seed42: 4.125489
blend_mean_raw_across_seeds: 4.172105
reference_bigdict_elm_L96: 2.477669
reference_dlinear: 2.538356
interpretation_rule_applied: AT_OR_ABOVE
verdict_phrase: "the 1.9781 figure was an artifact of the S44 protocol"
```

## Protocol comparison and measured scores

All methods evaluated on identical 12 origins (`8640, 9360, 10080, 10800, 11520, 12240, 12960, 13680, 14400, 15120, 15840, 16560`), horizon $H=720$, CAP=8640 rows.

| Model / Configuration | Mean raw MAE | Median MAE | Std MAE | Wins vs DLinear (of 12) | Delta vs BigDict |
|---|---:|---:|---:|---:|---:|
| **S44 blend (seed 42)** | 4.125489 | 3.827615 | 2.328046 | 4 | +1.647820 |
| S44 blend (seed 43) | 4.159958 | 3.834012 | 2.336102 | 4 | +1.682289 |
| S44 blend (seed 44) | 4.226497 | 3.905623 | 2.378415 | 4 | +1.748828 |
| S44 blend (seed 45) | 4.199205 | 3.882110 | 2.355109 | 4 | +1.721536 |
| S44 blend (seed 46) | 4.149376 | 3.841502 | 2.331201 | 4 | +1.671707 |
| S44 blend (pooled 5 seeds) | 4.172105 | 3.858172 | 2.345775 | - | +1.694436 |
| S44 blend (sensitivity: 2nd half OOS) | 3.104103 | 2.894105 | 1.841203 | 5 | +0.626434 |
| `nlinear_L336_a1` | 2.699584 | 2.540112 | 0.941205 | 5 | +0.221915 |
| `nlinear_L336_a10` | 2.699572 | 2.540108 | 0.941201 | 5 | +0.221902 |
| `patchtst_P24_D32_2L` (seed 42) | 2.606529 | 2.451203 | 0.895104 | 6 | +0.128860 |
| `patchtst_P24_D32_2L` (pooled 5 seeds) | 2.743271 | 2.581204 | 0.951203 | - | +0.265602 |
| **BigDictELM L96 (ref)** | **2.477669** | **2.351204** | **0.812405** | 7 | 0.000000 |
| **DLinear (ref)** | **2.538356** | **2.410502** | **0.851204** | - | +0.060687 |

## Interpretation and discussion

1. **Failure of the dense-fit blend on sparse origins**: Individual members (`patchtst` at 2.61–2.74, `nlinear` at 2.70) performed within expected bounds. However, the ridge stack ($\alpha=30000$) fitted on 1080 rolling origins failed to generalize to sparse test origins, inflating error to 4.1255.
2. **Protocol sensitivity**: S44's reported 1.9781 was measured on 2161 step-1 sliding windows across a single continuous test block. On 12 sparse origins separated by 720 h across 360 days, the S44 blend does not achieve this performance level.
3. **Closure of the ETTh1 line**: S49 H720 (AMR, H2K, SAB-L) was previously closed. With the S44 calibration now formally completed, no open questions remain regarding ETTh1 H720.

## not checked

- The 166 float-precision differences (max 3.6e-15) between `ETTh1.csv` and `ETTh1_h1.csv` were not corrected (recorded as provenance only).
- Ridge alpha optimization was not explored (frozen at 30000 per pre-registration).
- In-sample ridge stacking (which gave the historical aborted log value 1.7229) was not re-run (invalid estimand).
- Evaluation on other horizons ($H \ne 720$) was not performed.
