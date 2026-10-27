---
type: Concept
title: Deep learning models for time series
tags: [deep-learning, transformer, lstm, tcn, nlinear, patchtst]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Deep learning models for time series

Deep models excel when you have enough data and long-range dependencies matter.

## LSTMs / GRUs
- **Strengths**: handles variable-length sequences, captures long-range dependencies.
- **Weaknesses**: slow to train, prone to overfitting on small data, requires careful regularization.
- **When to use**: long sequences (> 100 steps), enough data to justify the capacity.

## Temporal Convolutional Networks (TCN)
- **Strengths**: parallelizable (unlike RNNs), dilated convolutions capture long-range patterns.
- **Weaknesses**: receptive field grows with depth; may need very deep networks for long horizons.
- **When to use**: long sequences, need for fast training.

## Transformers for time series
- **PatchTST**: patching + transformer encoder. State-of-the-art on many benchmarks.
- **iTransformer**: inverted transformer; treats variates as tokens.
- **Strengths**: captures complex dependencies, benefits from large data.
- **Weaknesses**: data-hungry, overfits on small datasets, computationally expensive.
- **When to use**: large datasets (> 50k observations), multivariate series, long horizons.

## NLinear / DLinear
- **Strengths**: surprisingly strong baselines; linear models with normalization; extremely fast.
- **Weaknesses**: still linear; may fail on chaotic or highly nonlinear series.
- **When to use**: quick baseline before trying more complex models.

## Model selection heuristic
- Data < 10k: classical or ML
- Data 10k-100k: try NLinear/DLinear, then TCN
- Data > 100k: transformer-based models viable
