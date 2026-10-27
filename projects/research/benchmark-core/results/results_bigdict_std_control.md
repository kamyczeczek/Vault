---
type: Concept
title: results_bigdict_std_control
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# BigDict Standardization Control

repro_ok=False (vs root-ablation refs, 25% tol.)

| thomas_H24 | full | none | D0=1440 | MAE=0.5434 |
| thomas_H24 | full | all | D0=1440 | MAE=1.597 |
| thomas_H24 | full | detail_only | D0=1440 | MAE=0.5434 |
| thomas_H24 | compact | none | D0=672 | MAE=0.5928 |
| trending_H48 | full | none | D0=1440 | MAE=1.8243 |
| trending_H48 | full | all | D0=1440 | MAE=1.1761 |
| trending_H48 | full | detail_only | D0=1440 | MAE=1.8243 |
| trending_H48 | compact | none | D0=672 | MAE=1.469 |

## Verdict
DETAILS_INTRINSICALLY_TOXIC: even standardized detail coeffs do not fix Thomas; keep the compact/full signal-adaptive split.
