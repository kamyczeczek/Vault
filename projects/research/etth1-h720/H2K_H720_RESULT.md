---
type: Concept
title: H2K_H720_RESULT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# H2K ETTh1 H720 result — development candidate evaluated, not promoted

## Decision

**Do not promote H2K as the S49 H720 specialist.** It is a useful, reproducible
long-horizon candidate and beats several simple baselines, but it does not
clear the preregistered H720 gates and does not beat the novel incumbent.

The candidate remains in `members/h2k.py`; this is not a deletion or a claim
that all motif-retrieval ideas are useless. It is a completed candidate result
under the early-dev/locked-final protocol.

## Implementation and correctness

H2K uses three 240-hour blocks. For each block it:

1. computes a local 24-hour level and level-relative normalized shape;
2. retrieves the k nearest training-window shapes;
3. adds the retrieved future deviation to the current local level;
4. re-anchors the next block on the preceding block, with a conservative
   local-slope contribution.

The corrected implementation removed an earlier level-handling error that
produced huge forecasts. The focused tests in `test_h2k.py` cover finite
720-hour predictions, training-slice-only fitting, block continuation, and
representation determinism: **4 passed**.

The final configuration was selected only on early origins
`8640, 9360, 10080, 10800` using the genuine ETTh1 OT series and a fixed
360-day training slice. The selected frozen configuration was:

- `input_length=168`
- `k_neighbors=48`
- `block_length=240`
- `drift_damping=0.0`

The early-dev ablation selected this configuration at mean MAE **3.6224**.
For context, BigDictELM scored **2.8712** on the same four early origins.

## Locked final evaluation

Canonical late-origin suite: 12 disjoint 720-hour origins, fixed 360-day
sliding training windows, genuine ETTh1, leakage-safe fit on `s[o-8640:o]`.
No late-origin scores were used to select H2K.

| method | mean raw MAE | std | normalized MAE | origins < 1.9781 |
|---|---:|---:|---:|---:|
| BigDictELM | 2.4777 | 0.7051 | 0.3818 | 3/12 |
| AMR-FBS | 2.5294 | 0.6552 | 0.3900 | 3/12 |
| DLinear | 2.5384 | 0.5169 | 0.3939 | 2/12 |
| H2K | **2.7270** | **1.0014** | **0.4260** | **3/12** |
| Persistence | 2.8769 | 0.7953 | 0.4540 | 2/12 |
| KNN L96/k24 | 3.0345 | 0.9701 | 0.4693 | 1/12 |
| SpectralFFT | 7.9853 | 5.4949 | 1.2724 | 0/12 |

H2K wins against BigDictELM on **5/12** origins, DLinear on **6/12**, and
AMR-FBS on **6/12**. It beats SpectralFFT on **10/12**. It is better than
KNN L96/k24 on **8/12**, which supports the intended value of the blockwise
retention, but the improvement is not consistent enough to beat the proven
linear-dictionary incumbent.

### Preregistered gates

- **G1:** fail — 2.7270 is not below the S44 reference 1.9781.
- **G2:** fail as a novel-specialist gate — H2K beats DLinear on only 6/12
  origins and does not beat the current novel incumbent; it does beat
  SpectralFFT, but that is insufficient.
- **G3:** not claimed; the H96/H336 regression suite remains pending.
- **G4:** not claimed; this run reports the pairwise matrix rather than a
  preregistered multi-seed rank analysis.

## Interpretation

H2K is a real but modest improvement over the direct KNN baseline, and it
shows that the level-relative/blockwise treatment is less pathological than
the earlier broken implementation. However, motif retrieval is brittle across
regimes: H2K has a larger across-origin standard deviation than BigDictELM and
loses badly on several origins. The remaining error growth over the six
120-hour bins is `[2.2677, 2.9191, 2.4263, 2.6754, 3.0024, 3.0711]`, so the
long-horizon structure is not solved.

**Next step:** AMR-24/168 remains the next S49 candidate. Do not tune H2K
against the locked late origins; if revisited, do so only on explicitly new
early-development origins or a separately registered protocol.

## Next step
AMR-24/168 is the next S49 candidate. Implement and evaluate it with the
same separate early-dev origins and locked final protocol; do not tune it
against the late-origin H720 results.

- `members/h2k.py`
- `test_h2k.py`
- `diag_h2k_early_dev.py`
- `diag_h2k_ablation.py`
- `run_h2k_h720_final.py`
- `results/h2k_early_dev_selection.json`
- `results/h2k_early_dev_ablation.json`
- `results/etth1_h720_multi_origin_sliding360d_h2k_l168_k48.json`
- `results/etth1_h720_multi_origin_sliding360d_h2k_l168_k48.md`
- `results/h2k_final_console.log`
