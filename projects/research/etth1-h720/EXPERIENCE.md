---
type: Concept
title: EXPERIENCE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# EXPERIENCE.md — etth1-h720

Distilled on demand 2026-09-27 from `CONTEXT.md` Open work + `CLAUDE.md` Rules.
Each lesson names its evidence. Root links here (D11).

## Verified practices

1. **Development origins are not test origins.**
   Select on early origins; score the locked 12-origin suite once. Re-running
   selection on test origins invalidates the result. Evidence: `CLAUDE.md` Rules.
2. **Read the per-origin table, not the mean.**
   12 origins on a chaotic series always contain a lucky win; below 6/12 wins
   write it as a loss even when the mean is lower. Evidence: `CONTEXT.md`
   Human check. Case: H2K 2.7270 locked mean, 5/12 vs BigDictELM — closed as
   S49 specialist, not revived by re-tuning locked origins.
3. **Kill budget: two iterations, then kill.**
   SAB-L exhausted its budget, had bugs fixed, still lost 0/12 (4.4611 vs
   BigDict 2.4777) — closed, record in `SAB_L_H720_RESULT.md`.
   Read it before a third iteration on anything similar. Evidence:
   `CONTEXT.md` Kill budget.
4. **Level-relative error dominates at H720.**
   30 days ahead: anchor on the last observation, predict a delta; absolute-
   level fitters lose. Evidence: `CONTEXT.md` "Why H720 is its own problem".
5. **A no-op anchor is not an anchor.**
   `predict_hist` computed the weekly anchor then returned `p + 0.0 * anchor`
   — the design-doc anchoring as a no-op. Decide the real rule and write it
   down before running anything. Evidence: Open work §AMR-24/168 item 1.

## Known-unresolved

- AMR-24/168 never scored (skeleton subclass, no `diag_amr_early_dev.py`, no
  locked runner); `daily_weight`/`weekly_weight` never swept.
- G3 (no-regression H96/H336) and G4 (mean rank over 5 seeds) never evaluated
  — every H720 number is a single seed.
- Entry points unrunnable from here: no `data/` (only
  `../datasets/data/ETTh1_h1.csv`), no `results/`, `members/` missing five
  imports that exist only in `../benchmark-core/members/`, no `__init__.py`;
  runs of record were made from `benchmark-core/`, not here.
- `H2K_H720_RESULT.md` was formerly filed in `../datasets/INBOX/raw/`; it is now
  consolidated beside `SAB_L_H720_RESULT.md` in this project.
  `SAB_L_H720_RESULT.md` — consolidate or fix the two references.
- Meta-H stays unbuilt (two rejected inputs).

## Skills used

None vendored (D8 lazy).
