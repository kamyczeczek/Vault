---
type: Concept
title: etth1_h720_multi_origin_sliding360d
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# ETTh1 H720 multi-origin (different starting points) test

Data: zhouhaoyi/ETDataset ETT-small ETTh1.csv (HF mirror ETDataset/ett)  n=17420  2016-07-01..2018-06-26  OT mean=13.325 std=8.567

Protocol: 12 disjoint 30-day origins, fixed 360d sliding train window, leakage-safe, frozen seeds.

## Aggregate (mean over origins, raw MAE)

| method | MAE raw | std | MAE norm | bins[0..5] (120h each) | <1.9781 |
|---|---|---|---|---|---|
| bigdict_elm | 2.4777 | 0.7051 | 0.3818 | [2.1745, 2.6855, 2.1198, 2.3595, 2.7075, 2.8192] | 3/12 |
| amr_fbs | 2.5294 | 0.6552 | 0.39 | [2.1837, 2.5875, 2.3307, 2.4487, 2.6973, 2.9288] | 3/12 |
| dlinear | 2.5384 | 0.5169 | 0.3939 | [2.0381, 2.8254, 2.3227, 2.4595, 2.9592, 2.6252] | 2/12 |
| nlinear_L96 | 2.6653 | 0.9415 | 0.4146 | [2.1243, 2.9597, 2.4445, 2.6923, 2.9968, 2.7742] | 2/12 |
| persistence | 2.8769 | 0.7953 | 0.454 | [2.4209, 3.3622, 2.7308, 2.7824, 3.0936, 2.8715] | 2/12 |
| theta | 2.8788 | 0.8936 | 0.4528 | [2.4421, 3.3683, 2.6745, 2.7397, 3.1282, 2.9199] | 3/12 |
| drift_linear | 3.0247 | 0.9599 | 0.4748 | [2.8793, 3.2459, 2.7172, 2.9816, 3.4049, 2.9193] | 2/12 |
| knn_96_k24 | 3.0345 | 0.9701 | 0.4693 | [2.5119, 3.1067, 2.3856, 2.9222, 3.2632, 4.0172] | 1/12 |
| sab_l | 4.1541 | 1.1433 | 0.6554 | [3.4373, 4.5306, 4.825, 3.8467, 4.2687, 4.0159] | 0/12 |
| spectral_fft | 7.9853 | 5.4949 | 1.2724 | [7.2233, 8.4612, 8.1532, 8.069, 7.8269, 8.178] | 0/12 |

## Incumbent S44 H720: 1.9781 raw MAE. Best-novel check: see table.