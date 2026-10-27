---
type: Concept
grade: active
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — benchmark-core

Time-series forecasting architectures and the cross-domain benchmark harness.
Owns `members/` and `bench.py`; every other time-series project depends on this
one and none re-vendors it.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | This file |
| `CONTEXT.md` | Contract (L1) | Model interface, evaluation protocol, leakage rules |
| `AGENTIC_DISCOVERY.md` | Reference (L3) | Mission and the standing SOTA comparison table |
| `REFLECTION_PROMISING_METHODS.md` | Reference (L3) | Post-reflection evidence ranking: what won, what was demoted or frozen |
| `members/` | Factory (L3) | Every forecaster, one file each, common fit/pred interface |
| `bench.py` | Factory (L3) | The S-47 diverse mini-suite: 8 tasks, 5 rolling origins, frozen fit, looped over seeds |
| `results/` | Product (L4) | Metrics per experiment |
| `plots/` | Product (L4) | Figures generated from `results/` |
| `scripts/` | Factory (L3) | `diebold_mariano_test.py` — significance testing for paired forecasts |
| `../../_archive/` | Archive | One-off repair scripts, retired; see `../../_archive/CONTEXT.md` |

## Route by intent

| Intent | Go to |
|---|---|
| Add a forecasting architecture | `members/<name>.py`, interface in `CONTEXT.md` §1 |
| Run the full benchmark suite | `python bench.py` |
| Write a run somewhere other than the committed artifact | `python bench.py --out-dir <dir>` |
| Re-run the suite over N seeds (default 5) | `python bench.py --seeds 5` |
| Evaluate on one domain (sunspot, thomas, financial, stock) | `run_<domain>_*.py` or `evaluate_*.py` |
| Multi-horizon protocol (Zhou et al. LTSF) | `python benchmark_multi_horizon.py` |
| Compare against literature SOTA | `python compare_all_sota.py` |
| Test whether a change is significant | `scripts/diebold_mariano_test.py` |
| BigDict component ablation | `python bigdict_ablation.py` |
| Read current best numbers | `AGENTIC_DISCOVERY.md` |

## Dependencies

- **On `../etth1-h720`** — none. That project imports from here.
- **On `../../_archive/datasets`** — `fetch_scientific_datasets` is imported directly by
  `benchmark_multi_horizon.py`, `heuristic_hyperparameter_search.py`, and
  `scripts/diebold_mariano_test.py`. Each puts `../../_archive/datasets` on `sys.path` from
  its own `__file__`; none of them copy it. Moving or renaming that module means
  editing all three.
- Models here are scored against frozen baselines; changing a baseline changes
  every historical result, so treat it as a versioned decision.

## Standalone



Run `python preflight.py` first; exit 1 lists exactly what is missing.

Siblings live under `$WORKSPACE_ROOT` (default: this project's parent,

i.e. `projects/research/`). Missing optional siblings degrade the project;

missing hard files block it. What each sibling is used for: see

`Dependencies` above.



## Rules

- `results_s47.json` and `harness.log` are the committed evidence. Any run
  that is not the one being reported goes to `--out-dir`, or it overwrites the
  artifact the project is ranked by.
- One model per file in `members/`. No model is defined in a runner script.
- A result is only valid if the fit is frozen before the prediction window.
- Report mean ± std over seeds for anything stochastic. A single run is a hint,
  not a result.
