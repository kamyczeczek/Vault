---
type: Concept
title: EXPERIENCE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# EXPERIENCE.md — benchmark-core

Distilled on demand 2026-09-27 from `CONTEXT.md` Open work + `CLAUDE.md` Rules.
Each lesson names its evidence. Root links here (D11).

## Verified practices

1. **One model per file; none defined in a runner.**
   `members/<name>.py` with `fit`/`pred` (or `.fit()`/`.predict()`); anything
   inexpressible in the interface does not belong. Evidence: `CLAUDE.md` Rules;
   `CONTEXT.md` "The model interface".
2. **Frozen fit before the prediction window — always.**
   No prediction-window statistic in scaling, normalization, or dictionary
   construction. Check the fit window in the log before believing any number
   from a new runner. Evidence: `CONTEXT.md` Process §3, Human check.
3. **Rolling origins (W=5 min), horizons independent, frozen fit per origin.**
   Evidence: `CONTEXT.md` "Evaluation protocol".
4. **A single run is a hint, not a result.**
   Mean ± std over seeds for anything stochastic. Counter-evidence the rule is
   unenforced: no seed sweep anywhere — every committed number (incl. random-
   reservoir BigDict family, ESNs) is a single sample. Evidence: `CLAUDE.md`
   Rules; Open work "No seed sweep anywhere".
5. **Significance or it didn't happen.**
   Paired forecasts via `scripts/diebold_mariano_test.py`; p > 0.05 means
   indistinguishable — write it that way. Several models demoted on exactly
   this basis. Evidence: `CONTEXT.md` "Significance".
6. **Execute the recorded verdicts or they are fiction.**
   2026-09-24 kill/archive list (2 frozen, 2 to `members/_archive/`) never
   executed: no `_archive/` exists, all four files still live and imported.
   Evidence: Open work "Dead decisions not carried out".
7. **Baselines are versioned decisions.**
   Changing a baseline changes every historical result. Evidence:
   `CLAUDE.md` Dependencies.

## Known-unresolved (numbers not to trust yet)

- BigDict std control: `"repro_ok": false`, `detail_only` rows numerically
  identical to `none` (thomas 0.5434, trending 1.8243) — verdict
  ("details intrinsically toxic") rests on a no-op arm.
- `big_dict_lasso.py` rewritten, never re-benchmarked; two summary docs still
  report old numbers from the run that dropped 365/665 windows.
- No committed `harness.log` for the S-47 result — the fit-window check the
  Human check requires cannot be performed on the ranked result.
- Six members imported by nothing (incl. `signal_adaptive_bigdict` — the
  routing head-to-head unrun, so the BigDict promotion rests on fixed config).
- DM grid has no multiplicity correction (~16 methods × protocols → 5–10 false
  "significant" wins at parity).
- "Real dataset" results are generated series with `source`-string metadata.
- Financial 60% directional-sign thread: in-sample only, no walk-forward, no
  DM vs buy-and-hold.
- Runners that cannot start: `evaluate_adaptive_hybrid.py`
  (`ModuleNotFoundError`), `bench.py --fev` (writes to pre-rename path).
- Docs mislead: `README.md` Layout (absent `tasks/`, wrong member names),
  Quick start (7-task vs 6 vs actual 8), cross-project refs read as local,
  cited `HANDOFF.md` exists nowhere.

## Skills used

None vendored (D8 lazy).
