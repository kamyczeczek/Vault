---
type: Concept
id: 06_ts_diverse_protocol
title: "ts-diverse Benchmark Protocol"
source: "projects/ts-diverse/README.md"
tags: [protocol, ts-diverse, benchmark, synthetic, etth1, evaluation]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# ts-diverse Benchmark Protocol

## Purpose
Standalone fast time-series benchmarking project (`projects/ts-diverse/`) separate from `h720`.
Evaluates diverse activation ELM architectures across heterogeneous task types in <1 minute on CPU.

## Constraints
- **No GPU/torch dependency**: pure NumPy
- **No decision trees**: user explicitly rejected tree-based methods ("disaster - slow and often fail big")
- **Ridge regression readout**: ELM style, Cholesky decomposition
- **Wavelet features required**: SWT multi-family
- **NLinear anchoring trick**: last-value subtraction on input window
- **Prediction plots**: must generate forecast vs ground truth visualizations

## Benchmark Suite (6 Tasks)
| Task | Horizon | Type | Description |
|------|---------|------|-------------|
| `etth1_H96` | 96 | real | ETTh1 dataset, H=96 |
| `seasonal_H48` | 48 | synthetic | Strong seasonal pattern |
| `trending_H48` | 48 | synthetic | Linear trend |
| `spiky_H48` | 48 | synthetic | Sparse spikes |
| `ou_H24` | 24 | synthetic | Ornstein-Uhlenbeck mean-reversion |
| `multiscale_H96` | 96 | synthetic | Multiple temporal scales |

## Evaluation Protocol
- **Rolling window**: 96-step lookback, stride 1
- **Validation split**: 15% of training windows for alpha selection
- **Alpha grid**: `(30, 100, 300)` for Ridge regularization
- **Metric**: Mean Absolute Error (MAE)
- **Pool structure**: Pool A (linear only) → Pool B (+subband) → Pool D (+BigDictELM)
- **Promotion rule**: mean MAE improvement ≥ 0.005 AND rank < 2 AND wins ≥ 4/6 tasks

## Model Registry
| Model | Description | Status |
|-------|-------------|--------|
| `nlinear_a1` | NLinear L=96, alpha=1 | Baseline |
| `nlinear_a10` | NLinear L=96, alpha=10 | Baseline |
| `rff_h64` | Random Fourier Features h=64 | Baseline |
| `subband_cA1` | SWT db4/sym4 cA1 subband | Expert |
| `subband_d1` | SWT detail d1 subband | Expert |
| `wavelet_pooled` | Pooled wavelet features | Expert |
| `bigdict_elm` | BigDictELM multi-activation | Proposed |
| `bigdict_tree` | Tree variant (exists but unused) | Rejected |

## BigDictELM Architecture
- **Filter bank**: identity + MA(3,6,12,24) + EMA(0.3,0.7) + diff1/diff2 + HP residuals + SWT db4/sym4 levels=2
- **Activation dictionary**: configurable `act_type`:
  - `"cos"` — Random Fourier Features (periodic)
  - `"rbf"` — Gaussian RBF with sampled centers
  - `"hybrid"` — 50% cosine + 50% RBF
  - `"multi_family"` — equal split: cos + rbf + tanh + mish
- **Hidden budget**: 384 nodes, split equally across activation families for multi_family (96 each)
- **Readout**: Vectorized Ridge via Cholesky decomposition
- **Anchoring**: NLinear-style last-value subtraction on input window, added back after prediction

## Key Results
| Pool | Members | Mean MAE | Wins | Status |
|------|---------|----------|------|--------|
| A | nlinear×2 + rff | 2.7388 | 0/6 | Baseline |
| B | +subband_cA1 + subband_d1 | 2.3594 | 4/6 | **PROMOTE** |
| D | +bigdict_elm | 2.4909 | 6/6 | REJECTED (rank 2.00) |

## Anti-Leakage Rules
1. All features derive from training window only
2. Validation split is chronological (first 85% train, last 15% val)
3. Alpha selection on val, refit on full train, test never consulted during tuning
4. Wavelet centers sampled from training data only
