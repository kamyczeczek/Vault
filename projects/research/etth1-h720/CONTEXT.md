---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — etth1-h720

One job: win at horizon 720 on ETTh1 without leaking the test window, and prove it
on a locked origin suite.

## Inputs

- Working (this run): `members/<candidate>.py`
- Reference (every run): `LONGTERM_ETTH1_H720_DESIGN.md` — why H720 breaks standard models
- Reference (every run): `../benchmark-core/CONTEXT.md` §Evaluation protocol
- Reference (every run): `SAB_L_H720_RESULT.md` — a killed candidate, and why
- Working (this run): `../../_archive/datasets/data/ETTh1_h1.csv`

## Process

1. Read the design doc. It states the incumbent number every candidate must beat.
2. Develop on **development origins only** (`diag_*_early_dev.py`).
3. Freeze the configuration. Do not revisit it.
4. Score once on the locked 12-origin sliding suite (`run_h2k_h720_final.py`).
5. Write mean ± std and the per-origin win count to `results/`.

## Outputs

- `results/etth1_h720_<candidate>_<protocol>.json` — per-origin metrics
- `results/<candidate>.md` — the human-readable verdict

## Human check

Read the per-origin table, not the mean. Twelve origins on a chaotic series will
produce at least one lucky win; a candidate that wins 3/12 has not beaten the
incumbent even if its mean is lower. If the win count is below 6/12, write the
result up as a loss.

## Why H720 is its own problem

At 720 steps the prediction error is dominated by level drift, not by shape. The
fix that works is anchoring the input on the last observed value and predicting a
delta. The models here fall into three families:

| Model | Idea | Status |
|---|---|---|
| `h2k.py` | Horizon-decomposed, drift-corrected KNN retrieval | current lead |
| `sab_l.py` | Signal-adaptive BigDict bank, L=336, scale-mismatch corrected | **rejected** — 4.4611 vs BigDict 2.4777, 0/12 origins |
| `amr_24_168.py` | Explicit daily/weekly envelope specialist | candidate |

## Kill budget

Each candidate gets two development iterations. SAB-L exhausted its budget,
had its bugs fixed, still lost 0/12, and was closed. `SAB_L_H720_RESULT.md`
is the record — read it before spending a third iteration on anything similar.

## Open work

Recorded from the project as it stands: both H720 candidates that were carried
to a locked protocol are rejected, and the third has never been run.

### AMR-24/168 is the next candidate and is not yet evaluated

`LONGTERM_ETTH1_H720_DESIGN.md` and `SAB_L_H720_RESULT.md` both name it the next
S49 candidate; `H2K_H720_RESULT.md` repeats that. What exists today is only a
skeleton — `members/amr_24_168.py` subclasses `AMRFBSForecaster` and has never
been scored. Nothing in this project has run it. Open, in order:

1. **Finish the model.** `predict_hist` computes the weekly anchor and then
   returns `p + 0.0 * anchor`; the anchor is multiplied by zero, so the weekly
   level anchoring the design doc specifies is currently a no-op. `daily_weight`
   and `weekly_weight` are also accepted but never swept. Decide the real
   anchor rule and write it down before running anything.
2. **Add the two missing diagnostics.** There is no `diag_amr_early_dev.py` and
   no locked final runner — the `SAB_L_H720_RESULT.md` / `H2K_H720_RESULT.md`
   recipe (early dev origins 8640/9360/10080/10800, then one locked pass over
   the 12 later origins) is the precedent to copy. The 2-iteration kill budget
   in the Kill budget section applies to this candidate too.
3. **Run it on the same locked suite** and record the per-origin table, not just
   the mean, per the Human check above.

### G3 has never been evaluated for either candidate

G3 (no-regression at H96/H336, within +5% of the member's S47-pool best) is
recorded as "not claimed" in `H2K_H720_RESULT.md` and cannot be evaluated for
SAB-L either — both were killed on the H720 gates before the regression suite
ran. G4 (mean rank across 5 seeds) is likewise unclaimed: every H720 number in
this line is a single seed, so the frozen-random variability the design doc
pre-registered was never quantified at H720. If S49 is ever revived rather than
closed, these are the unmeasured gates.

### The project could not run its own entry points — RESOLVED 2026-09-27

All three causes were real; each is now fixed and each fix is verified by a run
that produced artifacts, not by an inspection.

- **Data.** There was no `data/` directory, so every script failed on
  `ROOT / "data" / "ETTh1_h1.csv"`. The only copy in the workspace is
  `../../_archive/datasets/data/ETTh1_h1.csv`, and it is archived, not vendored.
  `_workspace_paths.data_csv()` returns that path and, if the file is ever
  missing, exits naming the fetch step
  (`python ../../_archive/datasets/fetch_etth1.py`) instead of raising `FileNotFoundError`
  from deep inside a runner. Fetching it back is a deliberate act, not a
  side effect of running a benchmark.
- **Outputs.** Nothing created `results/`, and `run_etth1_h720_multi_origin.py`
  also wrote a plot into an uncreated `plots/`. `_workspace_paths.bootstrap()`
  creates `results/` at import, and the plot path creates `plots/` before
  `savefig`. Every artifact of record now lands in *this* project's `results/`,
  not in `../benchmark-core/results/`.
- **Members.** `members/` here holds only `h2k.py`, `sab_l.py` and
  `amr_24_168.py`, but the runners also import `big_dict_elm`, `knn_feature_forecaster`,
  `amr_fbs` and `sota_baselines`, which live only in `../benchmark-core/members/`.
  Both `members/` directories are namespace packages, so putting both project
  roots on `sys.path` resolves local and borrowed modules together. Do not add
  `__init__.py` to either directory: that hides one project's modules from the
  other and re-breaks exactly these imports.

`_workspace_paths.py` is the single place any of this is configured; entry
points import it and nothing else. `conftest.py` does the same for pytest.
`run_bigdict_std_control.py` no longer hardcodes `sys.path.insert(0, "members")`
relative to the CWD.

Verified after the change: all 8 entry points import; `diag_h2k_ablation.py` and
`diag_h2k_early_dev.py` run end-to-end and write `results/*.json` + `*.log`;
`python -m pytest` is 11 passed, including `test_amr_24_168.py`, which could not
previously resolve its base class.

The canonical run directory is **this project**, not `../benchmark-core`.

### `H2K_H720_RESULT.md` is not in this project

`LONGTERM_ETTH1_H720_DESIGN.md` and `CONTEXT.md` point at
`H2K_H720_RESULT.md` for the H2K record, but that file is not here — the copy
in the workspace is `../../_archive/datasets/INBOX/raw/H2K_H720_RESULT.md`, i.e. filed as a
dataset inbox item. `SAB_L_H720_RESULT.md` sits here correctly. Consolidate the
H2K record next to it, or fix the two references to point where the file
actually is.

### Not open, deliberately

- SAB-L: closed. Kill budget exhausted, 0/12 origins. No third iteration.
- H2K: closed as an S49 specialist at 2.7270 locked mean raw MAE, 5/12 vs
  BigDictELM. It beats plain KNN on 8/12, so the blockwise level-relative idea
  is not worthless — but it must not be re-tuned against the locked late
  origins. Any revival needs explicitly new early dev origins or a separately
  registered protocol.
- Meta-H (per-horizon-block selector over {H2K, SAB-L, AMR-24/168}) was
  pre-registered as optional and last. With H2K and SAB-L killed it has two
  rejected inputs; it stays unbuilt unless a third member earns its place.
