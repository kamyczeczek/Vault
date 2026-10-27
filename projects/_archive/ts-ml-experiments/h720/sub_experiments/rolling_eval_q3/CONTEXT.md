---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# rolling_eval_q3 — Rolling-Origin Evaluation of the q3 kNN k-Grid (S-01-q3)

## Question
The legacy `q3_k_sweep` experiment swept the neighbor count $k$ of
`HeuristicLagKNN(q=3, history_fraction=0.1)` over 13 values on a single
720-row window (`test.csv[:720]`) and crowned **k=32** the family
optimum (MAE 1.7204, ahead of k=24 at 1.7553). Does that ranking and
the "large neighborhoods win" conclusion survive **sliding stride-1
origins across the full 2,880-row test region** (2,161 origins,
published-protocol-comparable), or was k=32 one favorable window draw?

## Protocol (pinned in `.unlazy/h720-s01/PLAN.md` C1; pattern =
`sub_experiments/rolling_eval/`, S-01)
- **Family**: `HeuristicLagKNN(q=3, neighbors=k, history_fraction=0.1,
  delays=(1,2,3,6,12,24))`, k ∈ {1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20,
  24, 32} — 13 configs.
- **Frozen fit**: every model fit exactly once on all of `train.csv`
  (11,425 rows) — the locked protocol's fit history. The
  `history_fraction=0.1` truncation is applied *inside* the model to
  the full fit history (most recent 10% of train.csv origins); no
  pre-sliced fit window.
- **Per-origin history**: at origin `t` (test-row index), `history_ =
  eval_series[:11425+t]` — all observed rows strictly before the scored
  window `test[t:t+720]`. Past test-region rows are legitimate forecast
  time history (benchmark sliding-window convention); scored rows are
  never seen. The KNN index itself stays frozen (fitted on train.csv
  only) — only the query point moves with the origin.
- **Origins**: `t ∈ [0, 2160]`, stride 1 → 2,161 windows per model.
- **Disjoint spread**: secondary diagnostic at `t = 0, 720, 1440, 2160`
  + max/min window-MAE ratio (stability).
- **Anchors**: origin t=0 must reproduce the legacy `q3_k_sweep`
  4-decimal numbers (k32 1.7204/2.1405, k3 2.8565/3.3663); failure
  aborts the run before any write. Both reproduced; additionally all
  13 t=0 windows match the legacy per-k table at 4 decimals (13/13).
- Deterministic: no RNG anywhere (distance-weighted KNN is exact).
- Accessor: `data.py::ProtocolData.rolling_views()` → `(fit_history,
  eval_series, test)`.

## Results — rolling (2,161 stride-1 origins, frozen fit)

| Model | Rolling MAE | Rolling RMSE | W1 | W2 | W3 | W4 | max/min | Legacy t=0 MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **knn_q3_k32_recent10** | **2.5583** | **3.0994** | 1.7204 | 4.9090 | 2.4162 | 2.8160 | 2.853 | 1.7204 |
| knn_q3_k24_recent10 | 2.6058 | 3.1549 | 1.7553 | 4.7848 | 2.5976 | 2.9694 | 2.726 | 1.7553 |
| knn_q3_k20_recent10 | 2.6402 | 3.1954 | 1.7747 | 4.8702 | 2.6778 | 2.9931 | 2.744 | 1.7747 |
| knn_q3_k16_recent10 | 2.6865 | 3.2485 | 2.0081 | 4.9619 | 2.7691 | 3.0703 | 2.471 | 2.0081 |
| knn_q3_k12_recent10 | 2.7379 | 3.3099 | 2.0515 | 4.8005 | 2.9621 | 3.1781 | 2.340 | 2.0515 |
| knn_q3_k10_recent10 | 2.7813 | 3.3601 | 2.2421 | 4.7603 | 3.1129 | 3.2468 | 2.123 | 2.2421 |
| knn_q3_k8_recent10 | 2.8301 | 3.4186 | 2.1921 | 4.5391 | 3.2828 | 3.2234 | 2.071 | 2.1921 |
| knn_q3_k6_recent10 | 2.9093 | 3.5137 | 2.7639 | 4.2504 | 3.6195 | 3.0746 | 1.538 | 2.7639 |
| knn_q3_k5_recent10 | 2.9592 | 3.5738 | 2.9054 | 4.5274 | 3.9199 | 3.0278 | 1.558 | 2.9054 |
| knn_q3_k4_recent10 | 3.0166 | 3.6462 | 2.9516 | 4.7559 | 4.2840 | 3.0505 | 1.611 | 2.9516 |
| knn_q3_k3_recent10 | 3.1138 | 3.7624 | 2.8565 | 5.2112 | 4.9925 | 3.0219 | 1.824 | 2.8565 |
| knn_q3_k2_recent10 | 3.2669 | 3.9515 | 2.8347 | 4.6841 | 4.9528 | 3.2184 | 1.747 | 2.8347 |
| knn_q3_k1_recent10 | 3.6756 | 4.4500 | 3.3836 | 6.7267 | 5.0077 | 3.2865 | 2.047 | 3.3836 |

Context rows (S-01 harness, same protocol): elm_h64_full_fastlags
2.3092 / daily 2.5491 / persistence 2.5985 — i.e. under rolling
evaluation the best q3-kNN (2.5583) sits *between* daily (2.5491) and
persistence (2.5985), and the ELM leader stays far ahead.

## Key Findings

### (a) Does the k=32 optimum survive rolling evaluation? YES.
The legacy ordering is fully preserved, not overturned. Rolling MAE is
**monotone decreasing in k across the whole grid** (3.6756 at k=1 →
2.5583 at k=32) — stricter than legacy, where the grid was
non-monotone (k10 2.2421 sat *above* k8 2.1921): rolling evaluation
didn't just confirm the k=32 optimum, it cleaned the small-k
irregularity the single window had produced. k=32 remains the family
optimum, the legacy top-4 ordering (k32 > k24 > k20 > k16) is intact,
and the big-k advantage survives, redistributed: the k32 gap over the
k≤6 band *shrinks* under rolling (legacy 1.04–1.66 MAE → rolling
0.35–1.12, a 33–66% compression — the single window had exaggerated
how much big k buys over small k), while the gap over its actual
legacy rivals k20/k24 *widens* 36–51% (k32−k24: 0.0349 → 0.0475;
k32−k20: 0.0543 → 0.0819). The "large neighborhoods win" conclusion is
real signal, not window luck — and the k32 edge is strongest exactly
where the competition is. One legacy claim does NOT survive, though:

**The seasonal-naive gap — but only barely.** Legacy window: k32
(1.7204) trailed daily (1.6720) by 2.9%. Rolling: k32 (2.5583) trails
daily (2.5491) by just **0.4%** — rolling evaluation narrows the gap
from 0.0484 to 0.0092 MAE, and the rest of the k-grid falls further
behind (k24 +2.2%, k12 +7.4%, k1 +44%). So k=32 is the only config
that even approaches seasonal-naive under honest rolling evaluation;
the family-wide legacy claim "nearly matches the daily baseline"
(q3_k_sweep finding 2) holds only at the k=32 edge and fails
everywhere else. Note daily itself never dominates k32 on rolling
RMSE (k32 3.0994 vs daily 3.1120) — the two are statistically
indistinguishable on this protocol.

### (b) Regime-fragility (window-2 blowup) varies U-shaped with k.
Window 2 (t=720) is the **worst window for 12 of 13 k** (the lone
exception is k=2, whose worst window is W3 4.9528), with W2 MAE in a
4.25–5.21 band for all k≥2 (only k=1 blows past, to 6.73). The
*severity* of the blowup is nearly k-independent; what k changes is
how much the easy windows are won:
- **Small k (2≤k≤6)**: W2 4.25–5.21 with max/min ratio 1.54–2.05. With
  few neighbors, distance-weighting concentrates on the nearest
  matches, so the forecast tracks whatever the recent state is,
  regime-shift included.
- **Large k (k≥8)**: W2 4.54–4.96, nearly identical in absolute terms
  to small k — but the max/min ratio climbs steeply: 2.07 (k8) → 2.12
  (k10) → 2.34 (k12) → 2.47 (k16) → 2.74 (k20) → 2.73 (k24) →
  **2.85 (k32)** — near-monotone (k24 dips 0.02 below k20) and 38%
  above the k8 level. The widening ratio comes entirely from the
  *easy* windows improving (k32 W1 1.72 vs k8 2.19), not from the hard
  one getting worse. A wide distance-weighted average is anchored to
  the fit-time regime distribution (recent-10% of train.csv), so when
  winter low-amplitude arrives every k overshoots by ~the same amount
  — large k just had more to lose.
- Net effect: k=32 wins three of four disjoint windows against k=8
  (W1 −0.47, W3 −0.87, W4 −0.41) but **loses W2 to k8 by 0.37** and
  loses W2 to k=6 by 0.66 — the rolling win comes from the easy
  regimes, not from the hard one. The W2 regime shift caps the family:
  k32's W2 (4.91) is 2.85× its best window and is where the S-01
  harness found the family's regime fragility (persistence W2 2.15,
  ELM 1.82).

### (c) Most stable k: k=6 (max/min 1.54×), with k=5 close (1.56×).
k=6 posts the lowest max/min ratio in the grid — W2 4.25 (lowest of
all 13), W3 3.62, W1 2.76, W4 3.07 — a genuinely flat profile, though
at a high absolute level (rolling 2.9093, 13.7% worse than k32). The
stability ranking (k6 1.54, k5 1.56, k4 1.61, k2 1.75, k3 1.82) is
dominated by mid-small k; every k≥12 exceeds 2.3× and k=32 is the
**most fragile** config in the grid by ratio (2.85×; W2 4.91 is 2.85×
its best window — though on absolute W2 it merely ties the family:
k16 4.96, k1 6.73). Stability and rolling accuracy anti-correlate
across this family: the k that wins on average is the most fragile.
If a deployment values worst-case windows, the k5–k6 band is the pick
(W2 4.25–4.53; k8 4.54 is close, k4 4.76 is not); if average accuracy,
k=32 — but no k in this family offers both.

### Rolling-vs-legacy summary
- The single t=0 window **understated error for every k**, and the
  understatement is U-shaped in k: smallest at k4–k5 (Δ = rolling −
  legacy: +0.065/+0.054) — where W1 ≈ the rolling average — and
  largest for k≥8 (Δ +0.54 to +0.87, peaking at k20 +0.866), with the
  k32 edge itself at +0.838. The legacy window flattered the big-k
  configs hardest: their t=0 advantage was partly window-specific.
  This is the window-tuning artifact the S-02 val-selection slice
  quantifies from the selection side.
- The seasonal-naive comparison: k32 alone reaches statistical parity
  with daily (0.4% behind on MAE, ahead on RMSE); every other k in the
  family loses to daily by 2.2%–44%.
- Practical read: keep k=32 as the family's accuracy pick (strictly
  best in W1/W3/W4 and best rolling MAE/RMSE), accept its 2.85×
  fragility, or drop to the stable-but-slower k∈{4..6} band — no k in
  this family offers both accuracy and stability. Under the
  published-protocol-comparable rolling view the family's ceiling is
  daily-parity, not daily-dominance.
- Runtime: 13 models × 2,161 origins ran in 165–168 s across two
  runs (~13 s/model, deterministic — identical 4-decimal outputs) —
  stride-1 full-region rolling is cheap at this scale.

## Directory Structure
- `CONTEXT.md` — this document
- `run_sweep.py` — rolling harness (re-run:
  `python sub_experiments/rolling_eval_q3/run_sweep.py`)
- `results.json` — per-k rolling + disjoint metrics, max/min ratios,
  legacy-t0 comparison, anchors

## Legacy q3_k_sweep single-origin table (archived; do not compare
## against rolling numbers)

| k | t=0 MAE | t=0 RMSE | | k | t=0 MAE | t=0 RMSE |
|---:|---:|---:|---|---:|---:|---:|
| 32 | 1.7204 | 2.1405 | | 6 | 2.7639 | 3.2312 |
| 24 | 1.7553 | 2.1663 | | 5 | 2.9054 | 3.4167 |
| 20 | 1.7747 | 2.2006 | | 4 | 2.9516 | 3.4605 |
| 16 | 2.0081 | 2.4538 | | 3 | 2.8565 | 3.3663 |
| 12 | 2.0515 | 2.5321 | | 2 | 2.8347 | 3.4316 |
| 10 | 2.2421 | 2.7240 | | 1 | 3.3836 | 4.1279 |
| 8 | 2.1921 | 2.6416 | | | | |

(Source: `sub_experiments/q3_k_sweep/CONTEXT.md`; its `results.json`
is a FAILED run — `"results": []` — so these rows are the archived
table values, which this harness re-verified at t=0 for all 13 k
(13/13 exact to 4 decimals).)

## Next (plan slices)
- **S-02** `val_selection` (leaf-2, in flight) — fit on train-only
  8,545 rows, select on the validation segment, score once on test:
  quantifies the window-tuning artifact this slice observed from the
  evaluation side.
- **S-03** leaderboard conversion (main-owned) — rolling numbers become
  canonical; the k-grid rolling table above is the q3-family source.
