---
type: Concept
grade: active
title: CLAUDE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CLAUDE.md — etth1-h720

Long-horizon (H720) ETTh1 forecasting. The incumbent trail: H2K, SAB-L, AMR-24/168.
Depends on `../benchmark-core` for the model interface and the evaluation protocol.

## Where things live

| Path | Role | Description |
|---|---|---|
| `CLAUDE.md` | Catalog (L0) | This file |
| `CONTEXT.md` | Contract (L1) | The H720 protocol, gates, and kill budget |
| `LONGTERM_ETTH1_H720_DESIGN.md` | Reference (L3) | Pre-registered design: what H720 breaks and why |
| `SAB_L_H720_RESULT.md` | Reference (L3) | SAB-L rejected — read before reviving it |
| `members/` | Factory (L3) | The three long-horizon specialists |
| `results/` | Product (L4) | H720 metrics per origin |
| `../benchmark-core/` | Dependency | Model interface, baselines, frozen-fit harness |
| `_workspace_paths.py` | Factory (L3) | The only place data path, `results/` and cross-project imports are set |
| `../../_archive/datasets/` | Dependency | `ETTh1_h1.csv`, archived not vendored |

## Route by intent

| Intent | Go to |
|---|---|
| Run the canonical 12-origin H720 suite | `python run_h2k_h720_final.py` |
| Multi-origin H720 test (S49) | `python run_etth1_h720_multi_origin.py` |
| Develop a candidate on early origins only | `diag_h2k_early_dev.py` / `diag_sabl_early_dev.py` |
| Isolate the H2K correction | `python diag_h2k_ablation.py` |
| Isolate SAB-L architecture (bank vs head) | `python diag_sab_l_arch.py` |
| Correctness / leakage checks | `test_h2k.py`, `test_sab_l.py`, `test_amr_24_168.py` |
| BigDict scaling control | `python run_bigdict_std_control.py` |

## Dependencies

- **On `../benchmark-core`** — `members/` interface and baselines. `h2k.py` and
  `sab_l.py` import `BigDictELM` and `KNNFeatureForecaster` from there.
  `_workspace_paths.py` puts both project roots on `sys.path`; the `members/`
  directories are namespace packages, so no file is vendored.
- **On `../../_archive/datasets`** — `ETTh1_h1.csv`, archived not vendored.
  `_workspace_paths.data_csv()` resolves it and names the fetch step
  (`fetch_etth1.py`) if it is ever missing.

## Standalone



Run `python preflight.py` first; exit 1 lists exactly what is missing.

Siblings live under `$WORKSPACE_ROOT` (default: this project's parent,

i.e. `projects/research/`). The `benchmark-core` and `_archive` links above are

hard: missing ones block the suite. Missing optional siblings degrade

the project. What each sibling is used for: see `Dependencies` above.



## Rules

- **Development origins are not test origins.** Selection happens on early
  origins; the locked 12-origin suite is scored once. Re-running selection on the
  test origins invalidates the result.
- H720 is 30 days ahead. Level-relative error dominates; a model that fits
  absolute level will lose to one that anchors on the last observation.
- A candidate gets two iterations. After that it is killed, not tuned further.
