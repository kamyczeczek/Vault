---
type: Concept
title: frontier_scout_arch
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Frontier Scout — Architecture-Level Cheap Wins vs S-26 1.9909

Date: 2026-09-11 | Graph fingerprint: 627189679626 (nodes 273, edges 1411, files 16) | Incumbent: S-26 2-member NLinear L336 a=1+a=10, α=10000, MAE 1.9909/2.4710

## Context (why a new MAP/hyperparam, not a new family)

* Closed families — **Scar [8] P1** piecewise-constant memorizes level; **Scar [9] P2** in-sample is memorization (S-21 trees 2.33 in-sample → 3.59 held-out → 8.57 test; S-21b still +0.23): no tree/constant-leaf head survives the held-out-half gate. **S-10** MultiRateELM +0.22 vs S-26, **S-11** RBF +0.29, **S-24** multivariate +0.056, **S-23** gated blend +0.013 — exogenous/multirate/RBF classes closed under S-20-clean protocol. S-27 horizon-band α REJECTED (−0.0045 < 0.005, disjoint 1.9709 > 1.9696), S-28 intercept catastrophic (5.91). Pool growth rejected.
* Open surface — `base.py:197 _lag_dataset` hotspot degree 27 (graph-brain `ask --hotspots`, in 14 out 13) and still-zero orphan set — map surface untapped. `neural_models.py` has only 3 lookbacks (96/336/720) in pool; no RevIN-window variant of NLinear, no horizon-weighted loss, no per-horizon α shrinkage calibration beyond a flat 11-point grid. Both bets below are ≤1 file + 1 scalar hyperparam, S-20-clean compatible.

---

## Bet 1 — Horizon-Weighted Ridge Objective (MAP-level, single scalar γ)

**Idea:** Keep the S-26 2-member stack and per-horizon ridge (no-intercept), but replace the pooled val selector `mean_h |r_h|² + α||w||²` with a **horizon-weighted** loss `Σ_h u_h(γ)·|r_h|² + α||w||²` where `u_h(γ) ∝ exp(γ·h/H)` or linear `1+γ·h/H`. γ is a single scalar tuned on the held-out half (n2=1080/1081) alongside α (11-point grid × e.g. γ∈{−0.5,0,0.5,1.0}). Selection still on held-out MAE; refit-all-val; frozen full 2161 is the only scorer. Cost: one weight vector broadcast, no new members, no new fit code.

**Why it might work:** W1 2.67 vs W2 1.29 spread persists; far-horizon residuals dominate MAE but are noisier — flat averaging over-weights them. A mild γ lets val pick an α/γ pair that discounts noisy tails (or up-weights them if they carry the hedge signal) without the 3-band discontinuity that killed S-27.

**Why not closed per scars:** Not a piecewise-constant head, not a new member family, not a gate; it is a loss reweighting of the incumbent ridge. Scars [8] P1 / [9] P2 forbid level-memorizing heads and in-sample selection — this respects both: selection on held-out half, ridge head unchanged, disjoint guard unchanged. Closed multirate/RBF/multivariate results do not predict this scalar's sign.

**Falsifiable acceptance (S-20-clean):**
- Full 2161 MAE < 1.9859 (≥0.005 vs 1.9909) **AND** disjoint-4 MAE ≤ 1.9696 (no regression vs S-26 disjoint 1.9696). Val selector: pooled MAE on held-out half; frozen test never consulted for γ.
- Reject if best γ=0 (flat) or gain does not survive refit-all-val, or disjoint guard violated — then S-26 terminal holds.

**Blast-risk (graph):**
- Touched symbol: `horizon-weighted α selection inside rolling_arm.py` + downstream `Ridge(alpha=α)` per horizon (no new method file). Blast of `_lag_dataset` (`ask --blast _lag_dataset --depth 2`: seed `base.py:197`) shows 14 callers — e.g. `fit @ knn_models.py:77` (HeuristicLagKNN) and `fit @ rbf.py:89` — but this bet touches **none** of them; it only reweights the already-materialized member residual tensor `R[M,H]` before the ridge solve. Regression risk is isolated to the rolling arm's val loop; member forecasts byte-identical.

## Bet 2 — RevIN-NLinear Lookback Ablation (single hyperparam L*, MAP-adjacent)

**Idea:** Add **one** RevIN-normalized NLinear variant as a 3rd pool candidate (or as a direct incumbent challenger), reusing `RLinear`'s per-window `(μ,σ)` standardization (`neural_models.py:220 _window_stats`) but with NLinear's last-value-anchored target convention already proven at H=720. In practice the cheapest probe is `NLinearRevIN(L=512 or 336, ridge a∈{1,10})` — L=512 is the untried mid-long lookback between 336 and 720 (FITS/RLinear at 720 are 2.12–2.16, so 512 may be the sweet spot without weekly-boundary noise that hurt R=(1,2,4,8,168) in S-10). Run as a drop-in member for the same tabu-2 selection (or as a singleton vs L336); no new graph edges beyond one `fit` method.

**Why it might work:** Incumbent contraction to L336 a=1+a=10 with α=10000 signals heavy shrinkage compensating for noisy per-horizon weights on ~1080 val points; longer standardized windows can de-noise far-horizon coefficients without adding families. RevIN on kNN helped strongly (+0.17) but on ELM hurt — untested on the linear family where level-freedom is already via anchoring; the combination is genuinely open. L=512 has never been scored.

**Why not closed per scars:** No tree head, no cross-channel, no gating — just a window-length + normalization change inside the surviving univariate linear class. Scar [10] P4 val→test flip was about multivariate correlations, not window length. S-06 already shows L336 > L720 > L96 ordering for NLinear, so 512 is the natural interpolation, not a new family. S-11's "norm hurts RBF" does not generalize to linear ridge (different head).

**Falsifiable acceptance (S-20-clean):**
- Either (a) tabu-2/3 with the augmented pool (12→13 members) selects the new variant and **full 2161 MAE < 1.9859 and disjoint-4 ≤ 1.9696**, or (b) singleton RevIN-L512 beats singleton L336_a=10 on frozen test by ≥0.005 with same guards. Val selection on held-out half only.
- Reject if val gain (any) inverts on disjoint or full — then pool remains 12 and S-26 stands. No second variant tried without a clean win.

**Blast-risk (graph):**
- Touched symbol: `fit @ neural_models.py` (new `NLinearRevIN` or `input_length=512` config). Hotspot `fit @ nlinear_knn.py:65 degree 48` is unrelated. Blast of `_lag_dataset` is irrelevant here — NLinear/RLinear do **not** call `_lag_dataset` (they use inline window loops `neural_models.py:165/233`); callers of `_lag_dataset` are `knn_models.py`, `multirate.py`, `rbf.py`, `residual.py` (`ask --blast _lag_dataset --depth 2` lists them). So a RevIN-NLinear addition has **zero blast** to those 14 callers; risk is confined to `neural_models.py` + `REGISTRY` + rolling arm's candidate list. File-hash gate catches stale `graph.db`.

---

## Execution order & stop rule

1. Bet 1 first (zero new model, ~hours). If accepted, re-baseline S-26→S-29 and then try Bet 2 on the new incumbent.
2. Bet 2 second (one model file, one L sweep). Either bet alone needs both full 2161 ≥0.005 and disjoint guard; otherwise terminal.
3. Blast check before each: `python ../../brains/graph_brain/ask.py --blast _lag_dataset --depth 2 | head -n 10` (expect `seed base.py:197` and callers e.g. `knn_models.py:77`) and `python ../../brains/graph_brain/build_graph.py --check` fresh.

## Evidence cited

* `MONITORING/reflection/2026-09-11_graph-aware-overall-reflection.md:22-24 P4` — hotspot fit d48, `_lag_dataset` d27, dead-code (none), fingerprint 627189679626.
* `./methods/base.py:197` `_lag_dataset` (14 callers per blast).
* `./methods/neural_models.py:136-260` NLinear/RLinear (lookbacks 96/336/720 only; RevIN via `_window_stats` at :220).
* `./CONTEXT.md:4-6,100-114` S-26 1.9909, S-27 banded −0.0045 REJECT, S-28 intercept catastrophic, S-10/S-11/S-24 closed.
* Graph: `python ../../brains/graph_brain/ask.py --blast _lag_dataset --depth 2 | head -n 10` → seed `base.py:197`, caller `fit @ knn_models.py:77` (representative of 14).
