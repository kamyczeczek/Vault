---
type: Concept
title: AMR_24_168_H720_RESULT
generated: { by: opencode/agent, at: 2026-10-27T00:00:00Z }
---

# AMR-24/168 ETTh1 H720 result — implemented, evaluated, not promoted

## Decision

**REJECT AMR-24/168 as the S49 H720 specialist.** It is the third and final
candidate in the H720 line. Its model was finished (the no-op weekly anchor was
made a real `anchor_rule`), developed on early dev origins, and scored once on
the locked 12-origin suite. It clears the no-regression gate G3 but fails the
two mandatory H720 gates G1 and G2, so PASS is impossible. Per the design's
"All members fail -> REJECT S49 after the 2-iteration kill budget" clause, and
with H2K and SAB-L already closed, this closes the S49 H720 line as **a partial
result**: the long-horizon level-anchoring idea is not worthless (it beats the
naive spectral baseline and shows a strong single-origin win at 8640) but it
does not beat the proven L96 BigDict family at H720.

## What was fixed

The skeleton's weekly anchoring was inert: `predict_hist` computed the 7-day
mean and then did `p + 0.0 * anchor`, i.e. a no-op. It is now a first-class
`anchor_rule` (`last` / `weekly` / `blend`) routed through the base class's
`_anchor_level` hook, so the base ELM core, feature bank and random dictionary
are reused verbatim and the anchoring is identical in `fit` and `predict_hist`.
Decision documented in `members/amr_24_168.py`, covered by `test_amr_24_168.py`.

## Development selection (early origins only)

Four early origins (8640, 9360, 10080, 10800) chose the anchor rule; BigDict
kept as an external reference. Artifact: `results/amr_early_dev_selection.json`.

| configuration | mean raw MAE |
|---|---:|
| AMR-24/168 `last` | 3.5422 |
| **AMR-24/168 `weekly` (selected)** | **3.4374** |
| AMR-24/168 `blend` | 3.4498 |
| BigDictELM L96 (ref) | 2.8712 |

Frozen configuration: `lookback=336, hdict=256, seed=42, anchor_rule=weekly`.

## Locked final evaluation

Genuine ETTh1 OT, fixed 360-day sliding window, 12 later 720-hour origins,
leakage-safe fit on `s[o-8640:o]`, seed 42. No late-origin value informed the
selection. Artifact: `results/etth1_h720_amr24168_weekly.{json,md}`.

| method | mean raw MAE | std | MAE norm | origins < 1.9781 |
|---|---:|---:|---:|---:|
| BigDictELM | 2.4777 | 0.7051 | 0.3818 | 3/12 |
| AMR-FBS | 2.5294 | 0.6552 | 0.3900 | 3/12 |
| DLinear | 2.5384 | 0.5169 | 0.3939 | 2/12 |
| **AMR-24/168 (selected)** | **3.1480** | **1.3573** | **0.4872** | **1/12** |
| SpectralFFT | 7.9853 | 5.4949 | 1.2724 | 0/12 |

AMR-24/168 beats BigDictELM on 3/12, DLinear on 3/12, and SpectralFFT on
10/12. Its across-origin standard deviation (1.3573) is the highest of any
method here: it is excellent on some origins (2.42 at 8640; 1.49 at 12240) and
catastrophic on others (6.19 at 14400; 5.27 at 9360). The weekly level anchor
helps but does not stabilize the long horizon the way the L96 BigDict family
does.

## Gates (pre-registered)

- **G1** (mean rolling raw MAE H720 < 1.9781): **FAIL** — 3.1480.
- **G2** (beat DLinear and SpectralFFT at H720): **FAIL** — DLinear on 3/12
  only; SpectralFFT on 10/12.
- **G3** (no-regression at H96/H336, within +5% of the member's S47-pool best):
  **PASS** — H96 mean 2.0132 (ref 3.2641, +5% 3.4273); H336 mean 3.5592
  (ref 6.7378, +5% 7.0747). Artifact `results/etth1_h720_amr24168_g3.json`.
- **G4** (mean rank <= 2 across members + SOTA baselines, 5 seeds): **not claimed**
  — 5-seed sweep was not run to completion; G1 and G2 already fail decisively, so
  the candidate is rejected regardless of G4.

PASS = G1 ∧ G2 ∧ G3. G1 and G2 fail, so the candidate is rejected regardless of
G3/G4. G3 is reported because it was the unmeasured gate flagged for every
H720 candidate in this line.

## Interpretation and next step

AMR-24/168 is a better-than-SAB-L but worse-than-H2K result: it clears the
regression gate and beats the naive spectral baseline, but it loses to the L96
BigDict family on the H720 mean. The explicit 24h/168h envelope + weekly anchor
reduces the worst-case blowup versus a direct 720-dim readout, but the residual
level drift over a 30-day horizon is not tamed enough to clear G1. The block of
results in this line (H2K 2.7270, SAB-L 4.4611, AMR-24/168 3.1480; all below
the S44 incumbent 1.9781 or worse) says the long-horizon specialist idea, in
its current forms, does not beat the proven multi-scale BigDict baseline on
ETTh1 H720.

**Next step:** close S49 per the null-result clause. No further H720
iteration is justified without a genuinely new inductive bias and newly
registered early-dev origins. Do not tune against the locked late origins.

## Artifacts

- `members/amr_24_168.py`, `test_amr_24_168.py`
- `diag_amr_early_dev.py` -> `results/amr_early_dev_selection.json`
- `run_amr_h720_final.py` -> `results/etth1_h720_amr24168_weekly.{json,md}`,
  `results/etth1_h720_amr24168_g3.json`
