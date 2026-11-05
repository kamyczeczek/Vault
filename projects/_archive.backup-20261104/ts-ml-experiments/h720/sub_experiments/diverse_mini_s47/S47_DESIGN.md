---
type: Concept
title: S47_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S47 — Diverse Mini Suite (6-task fast + cross-domain probe)

**Status:** PRE-REGISTRATION (binding per S43 P1). Code + run to land in same PR.

## Goal
Test whether anchored-wavelet methods (S46-style) have *any* cross-domain signal when ETTh1 H720 is saturated, and provide a **diverse but extremely fast** harness for future frontier bets. ETTh1 alone filters every wavelet/ELM variant (H2, S35, S46 all REJECTED with singleton >2.90). A 6-task mini-suite (ETTh1 + 5 synthetic domains emulating FEv-bench-mini / fev/Monash coverage) gives a cheap `≈2–5 min` CPU probe vs S46's `6.5h` full ETTh1 rolling.

## Suite
6 tasks, each `train=2000, W=5 rolling origins stride H, H variable` (matches fev-bench `W≤20` small-dataset protocol). Metric: **per-task MAE**, aggregate **mean rank + mean MAE normalized by task std**. Runtime reported per-task.

| Task | Domain analogue | Generator | H | Freq |
|------|-----------------|-----------|---|------|
| 1 ETTh1-like | ETT (transformer temp) | real ETTh1 OT slice (reuse `data.py` OT) | 96 | hourly |
| 2 Seasonal | Electricity (strong daily/weekly) | `sin(2πt/24)+0.5 sin(2πt/168)+AR1 noise` | 48 | hourly |
| 3 Trending | ExchangeRate-like (random walk) | `cumsum N(0,1) + weak AR` | 48 | daily |
| 4 Spiky | Traffic/Weather exogenous | `AR(2) + sparse spikes + AR noise` | 48 | 10-min |
| 5 Mean-reverting | Illness weekly | `OU process + seasonal` | 24 | weekly |
| 6 Multi-scale | fev mixed | `sum of 3 sines (periods 12,48,168) + noise` | 96 | hourly |

Fallback: if `fev` datasets unreachable offline, use the 6 synthetic generators above with fixed seed 0. Synthetic is deterministic and proves harness plumbing; `fev` YAMLs can be swapped in later without harness change.

## Members
`M=5` pooled baseline (S44-style without PatchTST retrain cost) + 2 contrasts:

- `nlinear_L96_a1`, `nlinear_L336_a1`, `nlinear_L96_a10` (linear anchors)
- `rff_rbf_h64` (fast non-linear ELM-style, no training beyond ridge)
- `subband_expert` group = `4` SWT subband Ridge experts `cA3/d3/d2/d1` (S46-intelligent-merge idea, no pooling, per-horizon Ridge directly on subband)

Comparisons:
- `Pool A (baseline)`: 5 linear/RFF
- `Pool B (+subband-experts)`: 5 + 4 experts = 9
- `Pool C (+pooled-ELM S46-style)`: 5 + 1 pooled F=12 ELM-Ridge = 6  (sanity: should lose per S46)

Each pool runs the **same** tabu+ridge-stack selector as S44/S46 (S20-clean: `train 1500` fit for val selector, `W=5` origins, per-horizon Ridge no-intercept `α grid [0.1..30000]`, held-out half). Fast path: `W=5` not 2161 → seconds not hours.

## Gates (binding BLEND-based vs pool A, per S43 P1)
- **G1**: mean MAE(B) < mean MAE(A) (−0.005 normalized)
- **G2**: mean rank(B) < mean rank(A)
- **G3**: B beats A on ≥4/6 tasks
All three → PROMOTE subband family; else REJECT pooled-ELM sanity expected REJECT. Singleton gate demoted (diagnostic).

## Harness
`rolling_arm.py`: generates/loads 6 tasks, builds P_val (W=5) for each member, runs pools A/B/C via `fit_stack_map` (borrow S44 tabu), reports per-task + aggregate. `results_s47.json` + `harness.log`. No 2161-origin ETTh1 full rolling; ETTh1 task uses the `H=96` slice with `W=5` only (fast). ETTh1 H720 incumbent `1.9781` remains the H720 leaderboard row — S47 is a **suite probe**, not a promotion attempt on H720.

## If offline (fev unreachable)
Run synthetic 6-task suite fully offline; mark `suite_source: synthetic` in results. Validates harness in `<5 min` and gives a real diversity signal (seasonal vs trending vs spiky behave differently). Full `fev-bench-mini` YAML swap is a one-liner later.
