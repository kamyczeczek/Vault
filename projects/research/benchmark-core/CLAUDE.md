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
| `PROTOCOL.md` | Contract (L1) | Normative v2 multi-domain generalization protocol (frozen; §15 amendment register) |
| `manifest.py` → `results/manifest.json` | Factory (L3) | Dev / quarantine / Lockbox split, families, domains, frozen SHA-256 |
| `metrics.py` | Factory (L3) | MASE, FEV clipping to [0.01, 100], skill score |
| `bootstrap.py` | Factory (L3) | Cluster bootstrap over dataset families, B = 10 000 |
| `ledger.py` → `ledger.jsonl` | Factory (L3) | Append-only hash-chained audit ledger (Genesis + amendments A1–A4) |
| `guards.py` | Factory (L3) | Gates 1–3, population N ≤ 8, STOP rules |
| `audit_v2.py` | Factory (L3) | Independent procedural audit (PROTOCOL.md §9) |
| `scan_denominator_anomalies.py` | Factory (L3) | Phase 1b MASE-denominator scan (20/20 tasks, 0 anomalies) |
| `test_benchmark_v2.py` | Test (L3) | 11 unit tests for the v2 foundation (incl. scanner regression) |
| `results/` | Product (L4) | Metrics per experiment |
| `plots/` | Product (L4) | Figures generated from `results/` |
| `scripts/` | Factory (L3) | `diebold_mariano_test.py` — significance testing for paired forecasts |
| `../../_archive/` | Archive | One-off repair scripts, retired; see `../../_archive/CONTEXT.md` |

## Route by intent

| Intent | Go to |
|---|---|
| Add a forecasting architecture | `members/<name>.py`, interface in `CONTEXT.md` §1 |
| Read the normative benchmark protocol | `PROTOCOL.md` |
| Verify the ledger + manifest independently | `python audit_v2.py` |
| Rebuild the frozen manifest | `python build_manifest_v2.py --offline` |
| Re-scan MASE denominators | `python scan_denominator_anomalies.py --layer dev` |
| Initialize the ledger (once, refuses if present) | `python init_ledger_v2.py` |
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
