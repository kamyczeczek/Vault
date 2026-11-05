---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Sub-Experiment: Temporal (Time-Decayed) kNN on the q3/k Base ($H=720$)

## Purpose
Test whether **soft exponential temporal decay** — older neighbours contribute
less to the weighted average — improves the g3 anchor-lag KNN family
(`q3_k_sweep` base: $q=3$, delays $(1,2,3,6,12,24)$, recent-10% history, best
$k=32$ at MAE 1.7204). Two questions:

1. Does recency weighting replace the **hard** recent-10% truncation
   (damped-window / fading-factor approach to concept drift)?
2. Does temporal weighting let the neighborhood grow **beyond** $k=32$
   (more neighbours under a soft recency prior)?

## Model Formulation
`TemporalLagKNN` (`methods/knn_models.py`, registry `temporal_lag_knn`) —
"select by similarity, weight by recency" (time-decayed kNN / ItemKNN-TD
family; decay applied **after** neighbor selection, not inside the distance):

$$w_i = \frac{1}{d_i + \epsilon}\, e^{-\lambda\,\mathrm{age}_i},
\qquad \mathrm{age}_i = T - t_i \text{ (steps)},\qquad
\lambda = \frac{\ln 2}{\text{half-life}}$$

$\hat y = \frac{\sum_i w_i\,y_i}{\sum_i w_i}$; weights computed in
log-space (shift by max) for numerical stability. $\lambda=0$ recovers
`HeuristicLagKNN`'s distance weights **exactly** (verified to $<10^{-9}$).

## Directory Structure
- `CONTEXT.md` — this document
- `results.json` — metrics for all 70 configurations + 2 references
- `interactive.html` — ground truth + all 70 prediction traces, MAE ranking, MAE-vs-k curves
- `run_sweep.py` — sweep definition; re-runnable in ~10 s

## Evaluation Protocol (exact)
Fit `TemporalLagKNN(q=3, neighbors=k, delays=(1,2,3,6,12,24),
history_fraction=f, decay=ln(2)/hl)` on all of `train.csv` (11,425 rows,
`data.py` shared split), forecast H=720, score against `test.csv[:720]`.
Axes: $k \in \{3, 8, 16, 24, 32, 64, 128\}$ × half-life $\in
\{\infty, 720, 240, 72, 24\}$ h × $f \in \{0.1, 1.0\}$.

- **Anchors reproduced exactly (4 decimals), in-script hard-fail otherwise:**
  `k3_hlinf_recent10` → 2.8565/3.3663 and `k32_hlinf_recent10` →
  1.7204/2.1405, matching `q3_k_sweep`'s `k3_q3_recent10`/`k32_q3_recent10`.
- **Results persistence rule:** a sweep whose `results.json` has
  `"results": []` is a FAILED run — re-execute before trusting the table.
- **Visualization gate:** `interactive.html` MUST contain the ground-truth
  trace PLUS one prediction trace per configuration (71 total).

## Results ($H=720$, sorted by MAE)
| Configuration | MAE | RMSE | $k$ | Half-life | History |
|---|---|---|---|---|---|
| **`k32_hlinf_recent10`** (= parent, anchor) | **1.7204** | **2.1405** | 32 | $\infty$ | Recent 10% |
| `k24_hlinf_recent10` (anchor sibling) | 1.7553 | 2.1663 | 24 | $\infty$ | Recent 10% |
| `k32_hl720_recent10` | 1.7866 | 2.2276 | 32 | 720 h | Recent 10% |
| `k64_hlinf_recent10` | 1.7931 | 2.2221 | 64 | $\infty$ | Recent 10% |
| `k24_hl720_recent10` | 1.8535 | 2.2823 | 24 | 720 h | Recent 10% |
| `k128_hlinf_recent10` | 1.9299 | 2.3708 | 128 | $\infty$ | Recent 10% |
| `k64_hl720_recent10` | 1.9424 | 2.3901 | 64 | 720 h | Recent 10% |
| `k128_hlinf_recent100` | 1.9637 | 2.3822 | 128 | $\infty$ | Full |
| `k64_hlinf_recent100` | 1.9761 | 2.4096 | 64 | $\infty$ | Full |
| `k16_hlinf_recent10` | 2.0081 | 2.4538 | 16 | $\infty$ | Recent 10% |
| `k32_hl240_recent10` | 2.0335 | 2.4996 | 32 | 240 h | Recent 10% |
| `k32_hlinf_recent100` | 2.0351 | 2.4851 | 32 | $\infty$ | Full |
| `k128_hl720_recent10` | 2.0746 | 2.5362 | 128 | 720 h | Recent 10% |
| `k16_hl720_recent10` | 2.1042 | 2.5598 | 16 | 720 h | Recent 10% |
| `k24_hl240_recent10` | 2.1604 | 2.6145 | 24 | 240 h | Recent 10% |
| `k8_hlinf_recent10` | 2.1921 | 2.6416 | 8 | $\infty$ | Recent 10% |
| `k8_hl720_recent10` | 2.2372 | 2.6873 | 8 | 720 h | Recent 10% |
| `k24_hlinf_recent100` | 2.2438 | 2.7276 | 24 | $\infty$ | Full |
| `k8_hl240_recent10` | 2.3241 | 2.7770 | 8 | 240 h | Recent 10% |
| `k64_hl720_recent100` | 2.3283 | 2.7596 | 64 | 720 h | Full |
| `k16_hl240_recent10` | 2.3381 | 2.8083 | 16 | 240 h | Recent 10% |
| `k64_hl240_recent10` | 2.3559 | 2.8301 | 64 | 240 h | Recent 10% |
| `k128_hl720_recent100` | 2.3630 | 2.7548 | 128 | 720 h | Full |
| `k128_hl240_recent10` | 2.4219 | 2.9145 | 128 | 240 h | Recent 10% |
| `k32_hl720_recent100` | 2.5255 | 2.9572 | 32 | 720 h | Full |
| `k16_hlinf_recent100` | 2.5391 | 3.0523 | 16 | $\infty$ | Full |
| `k8_hl72_recent10` | 2.6174 | 3.0868 | 8 | 72 h | Recent 10% |
| `k24_hl720_recent100` | 2.7320 | 3.1738 | 24 | 720 h | Full |
| `k3_hlinf_recent10` (= g3/k3 anchor) | 2.8565 | 3.3663 | 3 | $\infty$ | Recent 10% |
| `k3_hl720_recent10` | 2.8620 | 3.3708 | 3 | 720 h | Recent 10% |
| `k3_hl240_recent10` | 2.8803 | 3.3902 | 3 | 240 h | Recent 10% |
| `k3_hl720_recent100` | 2.8973 | 3.6549 | 3 | 720 h | Full |
| `k3_hlinf_recent100` | 2.9365 | 3.6061 | 3 | $\infty$ | Full |
| `k128_hl72_recent100` | 2.9447 | 3.4317 | 128 | 72 h | Full |
| `k128_hl240_recent100` | 2.9510 | 3.3728 | 128 | 240 h | Full |
| `k3_hl72_recent10` | 3.0060 | 3.5631 | 3 | 72 h | Recent 10% |
| `k8_hl720_recent100` | 3.0830 | 3.5167 | 8 | 720 h | Full |
| `k3_hl240_recent100` | 3.1056 | 3.8506 | 3 | 240 h | Full |
| `k3_hl72_recent100` | 3.1079 | 3.8528 | 3 | 72 h | Full |
| `k3_hl24_recent100` | 3.1079 | 3.8528 | 3 | 24 h | Full |
| `k64_hl240_recent100` | 3.1327 | 3.5988 | 64 | 240 h | Full |
| `k16_hl720_recent100` | 3.1435 | 3.5685 | 16 | 720 h | Full |
| `k8_hlinf_recent100` | 3.2002 | 3.6966 | 8 | $\infty$ | Full |
| `k8_hl24_recent10` | 3.2218 | 3.8906 | 8 | 24 h | Recent 10% |
| `k128_hl24_recent100` | 3.2507 | 3.9247 | 128 | 24 h | Full |
| `k32_hl240_recent100` | 3.3009 | 3.7885 | 32 | 240 h | Full |
| `k3_hl24_recent10` | 3.3246 | 4.0435 | 3 | 24 h | Recent 10% |
| `k24_hl240_recent100` | 3.3400 | 3.8308 | 24 | 240 h | Full |
| `k16_hl72_recent10` | 3.4327 | 3.9317 | 16 | 72 h | Recent 10% |
| `k32_hl72_recent10` | 3.5054 | 4.0178 | 32 | 72 h | Recent 10% |
| `k8_hl240_recent100` | 3.6354 | 4.1386 | 8 | 240 h | Full |
| `k128_hl72_recent10` | 3.6553 | 4.1476 | 128 | 72 h | Recent 10% |
| `k24_hl72_recent10` | 3.7161 | 4.2349 | 24 | 72 h | Recent 10% |
| `k16_hl240_recent100` | 3.8705 | 4.3632 | 16 | 240 h | Full |
| `k64_hl72_recent10` | 3.9374 | 4.4367 | 64 | 72 h | Recent 10% |
| `k64_hl72_recent100` | 4.2653 | 5.0018 | 64 | 72 h | Full |
| `k32_hl72_recent100` | 4.3127 | 5.0712 | 32 | 72 h | Full |
| `k24_hl72_recent100` | 4.3128 | 5.0713 | 24 | 72 h | Full |
| `k8_hl72_recent100` | 4.4766 | 5.2667 | 8 | 72 h | Full |
| `k16_hl72_recent100` | 4.4951 | 5.2747 | 16 | 72 h | Full |
| `k64_hl24_recent100` | 4.6515 | 5.5194 | 64 | 24 h | Full |
| `k32_hl24_recent100` | 4.6516 | 5.5194 | 32 | 24 h | Full |
| `k24_hl24_recent100` | 4.6516 | 5.5194 | 24 | 24 h | Full |
| `k8_hl24_recent100` | 4.6528 | 5.5209 | 8 | 24 h | Full |
| `k16_hl24_recent100` | 4.6528 | 5.5209 | 16 | 24 h | Full |
| `k128_hl24_recent10` | 4.9844 | 5.5295 | 128 | 24 h | Recent 10% |
| `k16_hl24_recent10` | 5.0076 | 5.6539 | 16 | 24 h | Recent 10% |
| `k64_hl24_recent10` | 5.2054 | 5.7957 | 64 | 24 h | Recent 10% |
| `k32_hl24_recent10` | 5.2702 | 5.9255 | 32 | 24 h | Recent 10% |
| `k24_hl24_recent10` | 5.2835 | 5.9401 | 24 | 24 h | Recent 10% |

References (shared protocol): persistence 1.7952/2.2503, daily
seasonal-naive 1.6720/2.1719.

## Key Findings
1. **Temporal decay does NOT beat the hard window.** The parent
   `k32_hlinf_recent10` (1.7204) stays best; the mildest decay (30-day
   half-life) already costs +0.066 MAE (1.7866). Decay strength and error
   are monotone: hl 720 → 240 → 72 → 24 h degrades smoothly to 5.27+.
   The hard recent-10% truncation is not a crude approximation of a soft
   window — it is the better inductive bias here: for 720-step forecasts,
   regime alignment (only the current regime's states) matters more than
   smooth recency confidence.
2. **More neighbours: $k=32$ remains the optimum** in the recent-10% arm
   (64 → 1.7931, 128 → 1.9299). In the **full-history** arm, larger $k$
   *does* help monotonically (k32 2.0351 → k64 1.9761 → k128 1.9637) but
   never catches the truncated arm — dense-recent state space beats
   sparse-global at every $k$.
3. **Strong decay makes $k$ irrelevant.** At hl = 24/72 h the weighted mean
   collapses onto the most recent neighbours regardless of $k$ (e.g. all
   `k*_hl24_recent100` ≈ 4.65): the exponential dominates the $1/d$
   distance term, so selection beyond the newest few origins has no effect.
4. **Decay is more destructive on the full-history arm** (best full+decay
   2.3630 vs best full untruncated 1.9637): with globally selected
   neighbours, decay re-weights toward the recent few — but those
   neighbours were already chosen for similarity, so the double recency
   emphasis discards the similarity signal that justified the larger pool.
