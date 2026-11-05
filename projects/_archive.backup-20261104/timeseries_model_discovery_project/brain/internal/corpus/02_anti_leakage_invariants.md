---
type: Concept
id: 02_anti_leakage_invariants
title: "Anti-Leakage Invariants & Information Containment"
source: "./CONTEXT.md"
tags: [anti-leakage, invariants, protocol, security]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Anti-Leakage Invariants & Information Containment

## Strict Design Invariants to Guarantee Valid Forecasts
1. **API-Level Containment**:
   - `ProtocolData` exposes test data only via `forecast_views()` (which yields `train_view` for fitting and `test_score_view` strictly for scoring) and `test_scores()` (explicit holdout accessor returning a detached copy).
   - Internal raw fields (`.test`, `.series`, `.train`, `.validation`) are name-mangled and private; stray access raises an `AttributeError`.

2. **Model-Level Containment**:
   - The entire `methods/` package is I/O-blind (no file system reading inside model code).
   - Every model's `predict()` method derives its starting baseline strictly from `self.history_` — the exact array passed to `fit()`, which terminates at row 11,424 (`train.csv`).
   - Anchors, lag features, rolling windows (`history_[-input_length:]`), and recursive autoregressive predictions originate entirely from train data.
   - For weighted/decayed models (e.g. `TemporalLagKNN`), decay and neighbor weights are calculated solely over train-side origin timestamps.
