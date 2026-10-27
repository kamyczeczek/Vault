---
type: Concept
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# benchmark-core — Diverse, Fast Time Series Bench (standalone)

Not H720. Purpose: evaluate methods across domains/horizons in **seconds-to-minutes** on CPU, not hours.

## Why standalone
H720 is ETTh1 H720 saturated (S-44 1.9781 incumbent, S46/S48 both REJECTED). This project tests **cross-domain generality** on a `fev-bench-mini`-style mini suite (7 domains, covariates, multivariate) with a lightweight `fev` wrapper. Offline fallback is 6 synthetic domains (seasonal/trending/spiky/OU/multi-scale) + ETTh1 slice.

## Quick start
```bash
pip install fev pywt scikit-learn
python bench.py            # 7-task synthetic+ETTh1 mini (12s)
python bench.py --fev      # fev-bench-mini 20 tasks (requires HF datasets)
python test_thomas.py      # run Thomas chaotic attractor sanity check tests
pytest                     # run pytest test suite
```

## Layout
- `bench.py` — main harness (tasks, members, LOO ridge stack, gates)
- `members/` — NLinear, RFF, SubbandExpert, PooledELM
- `tasks/` — fev adapter + synthetic generators
- `results/` — per-run json + harness.log
- `test_thomas.py` — Thomas chaotic attractor sanity check & unit tests

### Dynamical-system benchmarks
`thomas_H24` is classified as `chaotic`. It uses a canonical Thomas trajectory by default, with optional initial-condition perturbations for sensitivity experiments. The diagnostics include boundedness, autocorrelation, and finite-time divergence checks. Forecast scores should be interpreted as short-horizon scores because long chaotic trajectories lose phase alignment.

`chaos_protocol.py` provides leakage-safe horizon-wise evaluation. It evaluates a causal `fit_predict(history, horizon)` callback at multiple rolling origins and reports MAE, RMSE, and prediction/target correlation for each horizon. Use it to compare predictability curves rather than relying on a single `H=24` score.

Run the lightweight Thomas comparison with:
```bash
python thomas_compare.py --output results_thomas.json
```
This compares persistence, direct NLinear, and a recursive ridge delay-coordinate model over horizons 1, 4, 8, 24, and 48 without running the full benchmark suite. Development origins and locked evaluation origins are reported separately. Plot the locked-set curves with:
```bash
python plot_thomas.py results_thomas.json
python plot_thomas_forecasts.py --output plots/thomas_forecasts.png
```

The forecast visualization uses the shared Thomas method registry and includes persistence, NLinear variants, RFF, SWT subband experts, and recursive ridge delay forecasting. Methods requiring unavailable optional dependencies are skipped without preventing the other curves from being plotted.

For long-horizon sunspot forecast plots, run:
```bash
python plot_sunspot_longterm.py --origin 2000 --horizon 120 --output plots/sunspot_longterm_forecasts.png
```
The plot uses a dedicated full sunspot registry containing the standard baselines plus BigDictELM, BigDict tree, Subband BigDict, ESN reservoir, deterministic ESN, and recursive ridge. It uses a 96-month context window and displays the actual future continuation when available. `sunspot_eval.py` adds horizon-grid evaluation with nonnegative predictions and stability fields; `sunspot_hybrid.py` provides a low-frequency plus residual baseline; and `sunspot_selector.py` chooses a method using development origins only.
