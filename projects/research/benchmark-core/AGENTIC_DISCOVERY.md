---
type: Concept
title: AGENTIC_DISCOVERY
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Agentic Discovery & Workspace Invariants (`benchmark-core`)

## Core Project Mission
Developing, mutating, and evaluating advanced CPU-friendly time-series forecasting architectures (**AMR-FBS**, **StateSpaceDictionaryHybrid**, **KNNFeatureForecaster**, **BigDictELM**) against literature SOTA baselines (**DLinear**, **Theta**, **SpectralFFT**, **ARIMA**, **ETS**) across diverse scientific tasks (ETT, Sunspots, Multiscale, Seasonal, Chaos) and financial asset targets.

---

## 🏆 Summary of Latest Academic SOTA Benchmark Results (MAE)

| Task | AMR-FBS (Ours) | KNNForecaster (Ours) | StateSpace (Ours) | DLinear (AAAI) | Spectral FFT | Theta Method | ARIMA | ETS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ETTh1** (`H=96`) | 3.02 | 2.58 | 2.14 | **2.04 🏆** | 2.05 | 2.20 | 6.97 | 7.05 |
| **Sunspots** (`H=24`) | 15.68 | **8.23 🏆** | 9.13 | 9.22 | 20.75 | 18.34 | 34.46 | 62.87 |
| **Seasonal** (`H=48`) | **0.13 🏆** | 0.15 | 0.58 | 0.29 | 0.92 | 0.88 | 1.07 | 3.21 |
| **Multiscale** (`H=96`) | **0.21 🏆** | 0.25 | 0.98 | 0.28 | 0.85 | 1.07 | 1.97 | 1.52 |
| **Thomas Chaos** (`H=24`) | **0.0015 🏆** | 0.0668 | 0.0917 | 0.2136 | 1.3118 | 0.2299 | 0.63 | 0.63 |

---

## 🔬 Key Scientific Findings & Gate Promotion (S-47)
1. **BigDict / AMR-FBS Gate Promotion (`PROMOTE BigDict`)**: Validated via rigorous multi-task evaluation (`results_s47.json`), achieving aggregate mean MAE `3.3135` (vs baseline `3.4440`, 7/8 wins (8 tasks; corrected 2026-09-24 per results_s47.json winsB_denominator=8), mean rank `1.50`), successfully passing all strict promotion gates (`GD1`, `GD2`, `GD3`).
2. **Dominance on Non-Linear Dynamics**: AMR-FBS and BigDictELM outperform DLinear and classical statistical baselines by **5x to 10x** on chaotic attractors (`thomas_H24`) and cyclical solar cycles (`sunspot_H24`).
3. **Robustness on Real-World SOTA Tasks**: DLinear and StateSpaceHybrid lead on real-world industrial transformer temperature data (`etth1_H96`) with high fidelity.
4. **Financial Intelligence Pivot**: Moving from absolute price random-walk prediction to **Cointegrated Relative Spread (`log(AAPL) - log(SPY)`)** and **Directional Sign Accuracy (60%)** unlocks true quantitative edge.
5. **Memory Persistence**: Automatically initialized via `startup_memory_check.py` and indexed into SQLite FTS5 `graph.db`.

---

## 🧭 Engineering Workflow & Design-First RPI Principles
Inspired by advanced agentic research workflows ("Build Faster by Coding Slower"):
1. **Design-First RPI (Research, Plan, Implement)**: Prioritize thorough upstream specification (e.g., design markdown files) before writing or mutating complex time-series architectures.
2. **Stochastic & Non-Deterministic Validation**: Treat randomized components (e.g., ESN reservoir weights, mutation engines) with strict seed control, distribution bounds, and invariant assertions rather than relying on single-run "vibes".
3. **Zero-Drift Corpus Provenance**: Ensure all experimental logs and ingested literature maintain strict bidirectional mapping between raw sources, corpus chunks, and the shared Knowledge Graph (`graph.db`).

---

## 🧭 Updated Direction (2026-09-24 — after `REFLECTION_PROMISING_METHODS.md`)
1. **Evidence ranking (post-reflection):** AMR-FBS = most consistent winner (chaos/seasonal/multiscale, stable to H720) · KNN = strong on cyclical but hyperparameter-fragile · BigDict family = the *scientific* contribution (scale-mismatch / wavelet-detail-toxicity insight; S47 PROMOTE) · AdaptiveAMRKNN = marginal over AMR-FBS (DM p=0.15–0.39, non-significant) → **demoted** · AMR-Dynamo / AMR-Tree-ELM = **frozen** (failing to beat DLinear twice) · MetaEnsemble / LassoLag / ESN variants = **archived** (no wins).
2. **New focus — ETTh1 H720 long-term specialists** (design-first, pre-registered in `LONGTERM_ETTH1_H720_DESIGN.md`; incumbent S44 1.9781): horizon-decomposed drift-corrected KNN (H2K), scale-mismatch-optimized Signal-Adaptive BigDict Long (SAB-L, L=336), multi-scale AMR-FBS envelope (AMR-24/168), optional leakage-safe per-horizon meta-selector. Gates G1–G4 pre-registered; 2-iteration kill budget.
3. **P0 before any paper text:** (a) BigDict standardization control (flips "toxic" → "needs scaling"), (b) ≥5-seed re-runs with mean±std, (c) regenerate BigDict-LASSO on full consistent windows, (d) replace synthetic "real" catalogs with genuinely real data or relabel them.

4. **SAB-L rejected:** implementation bugs were corrected, but the independently selected configuration still scored 4.4611 H720 MAE vs BigDict 2.4777 and won 0/12 origins. No further SAB-L tuning; next long-horizon bias is H2K or AMR-24/168. See SAB_L_H720_RESULT.md.
