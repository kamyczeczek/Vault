---
type: Concept
title: etth1_h720_multi_origin
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# ETTh1 H720 multi-origin (different starting points) test

Data: zhouhaoyi/ETDataset ETT-small ETTh1.csv (HF mirror ETDataset/ett)  n=17420  2016-07-01..2018-06-26  OT mean=13.325 std=8.567

Protocol: 18 disjoint 30-day origins, expanding train (cap 360d), leakage-safe, frozen seeds.

## Aggregate (mean over origins, raw MAE)

| method | MAE raw | std | MAE norm | bins[0..5] (120h each) | <1.9781 |
|---|---|---|---|---|---|
| nlinear_L96 | 2.7421 | 0.9428 | 0.3716 | [2.261, 3.0366, 2.6171, 2.7211, 2.9456, 2.8713] | 2/18 |
| dlinear | 2.8014 | 0.8699 | 0.3721 | [2.2538, 2.9721, 2.6004, 2.6443, 3.1889, 3.1488] | 2/18 |
| bigdict_elm | 2.9544 | 1.0953 | 0.3831 | [2.2238, 2.9937, 2.548, 3.0411, 3.4345, 3.4855] | 3/18 |
| amr_fbs | 3.0688 | 1.1763 | 0.3968 | [2.531, 3.0563, 2.7969, 2.9714, 3.4375, 3.6199] | 3/18 |
| persistence | 3.11 | 1.0712 | 0.4203 | [2.7774, 3.3474, 3.1268, 3.0422, 3.2414, 3.1248] | 2/18 |
| theta | 3.1266 | 1.109 | 0.4213 | [2.7946, 3.3303, 3.0702, 2.9819, 3.3242, 3.2585] | 3/18 |
| drift_linear | 3.1567 | 1.0538 | 0.4292 | [3.2274, 3.2366, 2.8754, 3.1136, 3.3809, 3.1065] | 2/18 |
| knn_96_k24 | 3.4941 | 1.209 | 0.458 | [2.6901, 3.3207, 2.8365, 3.4328, 4.2709, 4.4135] | 1/18 |
| spectral_fft | 11.8686 | 7.5048 | 1.4942 | [8.2087, 10.837, 12.0934, 13.1069, 13.3905, 13.5748] | 0/18 |

## Incumbent S44 H720: 1.9781 raw MAE. Best-novel check: see table.