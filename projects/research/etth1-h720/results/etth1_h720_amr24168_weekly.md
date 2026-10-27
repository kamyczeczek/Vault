# ETTh1 H720 locked AMR-24/168 evaluation (anchor=weekly)

Protocol: genuine ETTh1 OT, fixed 360-day sliding window, 12 later origins; AMR-24/168 lookback=336, hdict=256, seed=42, anchor_rule=weekly (selected on early dev origins).

| method | MAE raw | std | MAE norm | <1.9781 |
|---|---:|---:|---:|---:|
| bigdict_elm | 2.4777 | 0.7051 | 0.3818 | 3/12 |
| amr_fbs | 2.5294 | 0.6552 | 0.39 | 3/12 |
| dlinear | 2.5384 | 0.5169 | 0.3939 | 2/12 |
| nlinear_L96 | 2.6653 | 0.9415 | 0.4146 | 2/12 |
| persistence | 2.8769 | 0.7953 | 0.454 | 2/12 |
| theta | 2.8788 | 0.8936 | 0.4528 | 3/12 |
| drift_linear | 3.0247 | 0.9599 | 0.4748 | 2/12 |
| knn_96_k24 | 3.0345 | 0.9701 | 0.4693 | 1/12 |
| amr_24_168 | 3.148 | 1.3573 | 0.4872 | 1/12 |
| spectral_fft | 7.9853 | 5.4949 | 1.2724 | 0/12 |

## Gates (H720)
- G1 (mean raw MAE < 1.9781): amr=3.148 -> FAIL
- G2 (beat DLinear on 3/12 and SpectralFFT on 10/12): FAIL