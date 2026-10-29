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
- Reference (every run): `docs/adr/0001-s49-closeout-and-protocol-discrepancies.md` — S49 closeout & protocol audit
- Reference (every run): `../benchmark-core/CONTEXT.md` §Evaluation protocol
- Reference (every run): `SAB_L_H720_RESULT.md`, `H2K_H720_RESULT.md`, `AMR_24_168_H720_RESULT.md` — evaluated candidates
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
| `h2k.py` | Horizon-decomposed, drift-corrected KNN retrieval | **rejected** — 2.7270 vs BigDict 2.4777, not promoted |
| `sab_l.py` | Signal-adaptive BigDict bank, L=336, scale-mismatch corrected | **rejected** — 4.4611 vs BigDict 2.4777, 0/12 origins |
| `amr_24_168.py` | Explicit daily/weekly envelope specialist | **rejected** — 3.1480 vs BigDict 2.4777, 1/12 origins |

## Kill budget

Each candidate gets two development iterations. SAB-L exhausted its budget,
had its bugs fixed, still lost 0/12, and was closed. `SAB_L_H720_RESULT.md`
is the record — read it before spending a third iteration on anything similar.

## Open work

Recorded from the project as it stands: the S49 H720 line is CLOSED (REJECT).
All three pre-registered candidate models have been implemented, tested, and
evaluated on the locked 12-origin sliding suite:

- `SAB-L`: rejected (mean raw MAE 4.4611 vs BigDict 2.4777, 0/12 origins).
- `H2K`: rejected (mean raw MAE 2.7270 vs BigDict 2.4777, not promoted).
- `AMR-24/168`: rejected (mean raw MAE 3.1480 vs BigDict 2.4777, std 1.3573,
  1/12 origins < 1.9781). Cleared G3 regression guard (H96 2.0132, H336 3.5592),
  but failed mandatory H720 gates G1 and G2. 5-seed G4 sweep evaluated in
  `results/etth1_h720_amr24168_g4.json` (mean rank 6.1 -> FAIL). See
  `AMR_24_168_H720_RESULT.md`.

Meta-H selector was not run and was closed with the line.

### Protocol fidelity audit & closeout findings

A detailed protocol fidelity audit was conducted (ADR 0001,
`docs/adr/0001-s49-closeout-and-protocol-discrepancies.md` and Execution Annex in
`LONGTERM_ETTH1_H720_DESIGN.md`):

1. **Origins count**: Pre-registration declared 20 eval origins; execution ran
   on 12 locked origins (step=720h, sliding 360-day window).
2. **Seed coverage**: Pre-registration specified 5 seeds across all stochastic
   methods; main tables recorded seed 42, with 5 seeds measured only for G4.
3. **Threshold comparability**: The G1 threshold 1.9781 originated in S-44 from
   a 3-member blend evaluated over 2161 dense rolling origins (step=1), whereas
   S49 applied it directly to single models across 12 sparse origins. While not
   proving single models cannot achieve this, empirical performance shows all
   three candidates also lost to simple baselines on this suite (BigDictELM
   2.4777, DLinear 2.5384).

**Next step rule**: Do not run further iterations of these models or tune against
the locked origins. A new research line requires a genuinely new inductive bias,
freshly registered dev origins, and an aligned benchmark protocol.

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

### `H2K_H720_RESULT.md` is now in this project — RESOLVED 2026-10-27

`LONGTERM_ETTH1_H720_DESIGN.md` and `CONTEXT.md` point at `H2K_H720_RESULT.md`
for the H2K record. It had been filed as a dataset inbox item
(`the archived dataset inbox`), off-project. It is now
consolidated next to `SAB_L_H720_RESULT.md` in this project, so both references
resolve locally.

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
