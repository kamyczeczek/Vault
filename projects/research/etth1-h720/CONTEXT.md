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

### Threshold comparability — measured 2026-11-01

The ADR 0001 caveat ("the two numbers are not directly comparable") is now a number.
The S44 blend (NLinear L336 a=1 + NLinear L336 a=10 + PatchTST-Delta P24 D32 2L,
per-horizon ridge, no intercept, `alpha=30000`, frozen) was scored on the S49
protocol — 12 locked origins, step 720 h, 8640..16560 — with its ridge weights
refitted out-of-sample per origin (members frozen at row 5760, ridge on the first
1080 of the 2161 out-of-sample tail origins; the exact structural mirror of S44's
`val[0:1080)`).

| method | mean raw MAE | wins vs DLinear |
|---|---|---|
| S44 blend (seed 42) | 4.1255 | 4/12 |
| S44 blend (5-seed mean) | 4.1721 | — |
| PatchTST-Delta P24 D32 2L (seed 42) | 2.6065 | 6/12 |
| NLinear L336 a=1 / a=10 | 2.6996 | 5/12 |
| BigDictELM L96 | 2.4777 | 6/12 |
| DLinear | 2.5384 | 0/12 |

Verdict, produced by the rule fixed before the run: 4.1255 >= 2.4777, so 1.9781 was
a protocol artifact (2161 dense step-1 origins), not a level reachable on 12 sparse
step-720 origins. The blend is also worse than each of its own members: with no
intercept the ridge can only learn a level multiplier, and the multiplier learned on
a biased-low out-of-sample region over-corrects at the scored origin.

Consistency control: the identical S44 frozen test reproduces 1.978126 (rel diff
4.2e-11) on both data files. Artifacts: `S44_CALIBRATION_RESULT.md`,
`results/s44_calibration.json`, `results/s44_calibration_reproduction.json`,
pre-registration `GATES-s44-calibration.md` (Amendment A1). S49 stays closed; no
model is promoted and nothing is re-tuned.
## Resolved implementation history

The project entry points were repaired and verified on 2026-09-27. `_workspace_paths.py` is the single owner of the archived ETTh1 data path, result/plot directories, and cross-project imports. Do not add `__init__.py` to either sibling `members/` directory: both are namespace packages, and package initialization hides borrowed benchmark-core modules.

The canonical run directory is this project. `H2K_H720_RESULT.md` was moved here on 2026-10-27 so H2K and the other S49 records resolve locally. The fixes produced artifacts and 11 passing tests; this history is closed, not an invitation to rerun locked-origin work.

## Not open, deliberately

- SAB-L: closed; kill budget exhausted, 0/12 origins. No third iteration.
- H2K: closed at 2.7270 locked mean raw MAE; any revival needs new early development origins or a separately registered protocol.
- Meta-H: not built; two of its three pre-registered inputs were rejected. It stays unbuilt unless a third member earns its place.
