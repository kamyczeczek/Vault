---
type: Concept
title: REFLECTION_PROMISING_METHODS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# Deep Reflection — Which of Our Novel Methods Are Actually Promising?

**Date:** 2026-09-24 · **Scope:** all `members/` novel methods vs evidence in `results/`, `s47_ref/`, ablation reports · **Method:** critical re-verification of every "win" claim, cross-file consistency checks, and protocol-level threat analysis.

---

## 1. First-order finding: the evidence base is protocol-fragile

The same method pair can win on one protocol and lose on another. Before declaring any method "promising," we must rank the *protocols*, not just the methods.

| Claim | Protocol A (raw MAE) | Protocol B (normalized) | Verdict |
|---|---|---|---|
| "We beat DLinear on ETTh1" | ❌ DLinear 2.036 beats StateSpace 2.142 / KNN 2.150 (`results_academic_sota.json`) | ✅ AMR-FBS wins all H∈{96,192,336,720} (`results_rigorous_literature.json`) | **Scale-dependent.** Only true on normalized data. |
| "BigDict dominates sunspot H24" | KNN 8.23 / AMR-FBS 15.68 / BigDict 15.65 (single frozen fit, S47) | Multi-origin long-horizon: DLinear beats AMR-FBS at origin 1800 (19.39 vs 32.26 MAE) (`results_sunspot_master.json`) | **Single-origin claim does not transfer to multi-origin.** |
| "Thomas is our kill-zone" | AMR-FBS: 0.0015 (AGENTIC table) vs 0.0049 (academic SOTA) vs 0.0572 (BigDict ablation run) — **same method, 14× spread across files** | BigDict-compact 0.0139 vs BigDict-full 0.2281 | **Not comparable across files.** Different origins/seeds/train-lengths. No shared canonical chaos eval. |

Consequences:
- `AGENTIC_DISCOVERY.md` and `HANDOFF.md` mix protocols inside single tables. Treating them as one scoreboard overstates every "Ours" win.
- The **one true win that survives every protocol** is AMR-FBS on non-linear regimes (chaos + seasonal + multiscale + trending), especially vs SpectralFFT/Theta/ARIMA/ETS.

---

## 2. Per-method critical verdicts

### 2.1 AMR-FBS — 🥇 most promising (anchor method)
**Why:** the only novel method that wins across regime families without a config switch: Thomas (0.0049, ~44× DLinear), seasonal (0.136, best), multiscale (0.213, best), trending (0.58, best), OU (0.45, best vs KNN 0.45 tie), multi-horizon Electricity H720 (73.74, beats its own adaptive hybrid at long horizons).
**Threats:**
- Normalized vs raw ETTh1 ambiguity — on raw scale DLinear wins. Publication must pin the scale and report both.
- Win margin vs SpectralFFT/Theta on non-chaos tasks is thin (0.21 vs 0.28/0.22 class margins are fine; but trending 0.58 vs DLinear 1.01 is the *only* big non-chaos win).
- DM tests vs AMR-FBS are consistently **non-significant** for our hybrids (p=0.15–0.39) — i.e., the "adaptive" layer adds noise, not signal, over AMR-FBS.

### 2.2 KNNFeatureForecaster — 🥈 promising, but parameter-fragile
**Why:** best sunspot H24 (8.23, 44× ETS), best OU, ~50% win rate across the 6-domain comprehensive bench.
**Threats (serious):**
- **Config sensitivity is proven, not hypothetical:** k_neighbors=5 vs default 24 inflated MSE by 37–42% (Electricity 112.13 vs 80.16). One wrong default silently corrupts results. Every KNN number in the repo must be checked against its config.
- The KNN DM-test bug (`k_neighbors=5`) **is now fixed and re-run** (verified: current `results_dm_tests.json` KNN = 80.16/1572.35/65.51, exactly matching benchmark). **`HANDOFF.md` "Known Issue #3" is stale — update the doc.**
- Motif retrieval has ~2k training windows → nearest-neighbor statistics are noisy on short datasets. Needs per-dataset k (P2 item).

### 2.3 BigDict family — 🥇 the *science* is promising, the *model* is mixed
The family (big_dict_elm / new_big_dict_elm / big_dict_tree / subband_bigdict / signal_adaptive_bigdict / big_dict_lasso) is where the strongest **publishable insight** lives — but the insight is about *feature scale mismatch*, not about "a better forecaster."

**The mechanism finding (strong):**
- Wavelet detail coefficients have ~10× lower variance than all other features → they receive saturated ridge shrinkage but still worsen conditioning → **Thomas error 0.2281 → 0.0195 (−91%)** after removal; compact (D=672) even better (0.0139, −94%).
- This is a *counter-intuitive* result (high-frequency detail is usually theorized to help) → genuinely novel.

**The threats that would sink a paper if unaddressed:**
1. **The claim is under-specified.** "Detail coeffs are toxic" vs "unstandardized detail coeffs destabilize ridge" are different claims. The *standardization control is not yet run.* If standardizing cD1–cD3 restores value on trending tasks, the true finding is "fix the scaling, keep the features" — which is more interesting and needs testing.
2. **BigDict-LASSO is currently broken on chaos** (0.7961 vs Ridge 0.0195 — a 40× gap on the same task, same features). Root cause identified (no standardization) but unfixed. Additionally the pywt even-length bug caused **365/665 windows (55%) to be silently dropped** — the LASSO result is on inconsistent data and must be regenerated.
3. ~~**Frozen seed 42, one draw, no variance bars.**~~ **RESOLVED
   2026-09-27.** `bench.py --seeds 5` (923s) now loops the suite and reports
   mean ± std for every pool, member and aggregate. Result: BigDict survives —
   gap over Pool A −0.2514 ± 0.0205, mean rank 1.35 ± 0.16, 7/8 wins with zero
   variance, all gates true on all 5 seeds. The *subband* family, promoted on a
   single draw, does not: G2 (mean rank < 2.0) fails at 2.225 ± 0.205 on every
   seed, so its verdict is REJECTED. The gap over Pool A *is* real
   (−0.0249 ± 0.0147) — it is the rank gate, not the margin, that rejects it.
4. **Gate "7/6 wins" inconsistency:** `results_s47.json` reports 8 tasks and
   `AGENTIC_DISCOVERY.md` says "7/6 wins". The denominator is 8; the discovery
   doc needs the fix.

### 2.4 AdaptiveAMRKNN (dual-scale routing) — 🟡 disappointing on scrutiny
- Beats KNN/DLinear/FFT **significantly** (DM p < 1e-4) — but those are weak baselines; winning DLinear on Electricity says little.
- vs AMR-FBS (the real comparison): **not significant** on Electricity (z=1.43, p=0.15) and Solar (z=0.86, p=0.39); significant only on Traffic.
- Multi-horizon: flips to *worse* than AMR-FBS at H=720.
- **Honest read: the spectral peak-to-median router is not buying much over plain AMR-FBS.** Demote from flagship to "variant that occasionally helps."

### 2.5 StateSpaceDictionaryHybrid — 🟡 competent, no decisive win
Best-our-method on raw ETTh1 (2.14, still behind DLinear 2.04). Wins the textbook-validated intervention experiment (MSE 8.17). No regime where it clearly beats AMR-FBS/KNN. Keep as a strong baseline, not a contribution.

### 2.6 ESN / DeterministicCycleESN / MetaEnsembleStacker / LassoLagHybrid — ⚪ no win recorded
Never #1 on any task in any results file we audited. Archive, don't kill (cheap to re-run in future gates).

### 2.7 AMR-Dynamo-Attractor & AMR-Tree-ELM — ❌ kill for sunspot
- AMR-Dynamo: MAE 32–49 vs DLinear 16–19 across sunspot origins, **and** asymmetry error 0.58–0.59 (DLinear 0.00–0.025). It predicts the *wrong shape* of the cycle — worse than linear. The physics prior (Waldmeier asymmetry built-in) is not being exploited by the estimator.
- AMR-Tree-ELM: niche sunspot filters, no recorded win over AMR-FBS/KNN.
- Per your own "Fail Fast & Cheap" rule (CLAUDE.md): both have now failed twice. Kill or freeze.

### 2.8 Financial strategies (Vaknin / SubbandMomentum / AlphaMomentum / TrendDrift) — ⚪ unvalidated
Backtests with plots only: **no walk-forward, no out-of-sample, no DM vs buy&hold.** The 60% directional-sign claim on the cointegrated spread is the most interesting open thread, but as-is it's an in-sample anecdote. Cannot support "edge" language.

---

## 3. Methodological threats (cross-cutting)

1. **Protocol fragmentation** — 5+ different eval protocols coexist (raw MAE, normalized MSE/MAE, frozen-fit W=5 S47, multi-origin, single-origin H24, DM-test n=480). No two numbers in different files are guaranteed comparable. *Fix: one canonical suite; chaos via `chaos_protocol.py`; everything else via locked rolling origins.*
2. **Multiple comparisons** — ~16 methods × 8–12 tasks × several protocols, no multiplicity correction. With this many tests, 5–10 "significant" DM wins are expected by chance even at true parity. *Fix: Holm-Bonferroni or BH-FDR across the DM grid.*
3. **"Real datasets" are synthetic** — the ETT download failed; Solar_Activity_SIDC, Traffic, Industrial sensors are all *generated* catalogs. Any "dominates real data" claim currently rests on synthetic data. This is the single biggest credibility risk for publication.
4. **MAPE on near-zero series** — solar MAPE > 8e9 (known, SMAPE partially patched). Never report MAPE on near-zero series; use SMAPE or only MAE/MSE.
5. **Config drift** — the KNN bug (5 vs 24 neighbors) changed MSE by 40% with no test catching it. There's no API-contract test for member constructors. *Fix: pytest fixtures that assert the canonical constructor signature per method.*
6. **Stale docs as sources of truth** — HANDOFF lists the KNN bug as "NOT yet applied" while it *is* applied and re-run; AGENTIC_DISCOVERY's "7/6 wins" should be 7/8. Both docs will mislead the next session/agent.

---

## 4. Revised "promising" ranking (post-reflection)

| Rank | Method | One-line verdict |
|---|---|---|
| 1 | **AMR-FBS** | Broadest, most consistent winner; anchor of any paper. |
| 2 | **The scale-mismatch insight (BigDict ablation)** | The most *novel scientific contribution* — but currently under-specified (standardization control missing) and built on single-seed, inconsistent-data runs. |
| 3 | **KNNFeatureForecaster** | Strong on cyclical/mean-reverting; fragile to hyperparameters; config must be pinned per dataset. |
| 4 | **SignalAdaptiveBigDict** | Natural integration of #2 (route compact vs full by signal type) — the right next experiment, not yet proven. |
| 5 | **StateSpaceHybrid** | Solid baseline; not a contribution on its own. |
| — | AdaptiveAMRKNN | Marginal over AMR-FBS; demote. |
| — | ESN, MetaEnsemble, LassoLag, AMR-Dynamo, AMR-Tree-ELM | No wins; archive/kill. |
| — | Financial strategies | Unvalidated; needs walk-forward + OOS before any claim. |

---

## 5. Priority action list (what actually moves the project)

**P0 — before writing any paper text**
1. Run the **standardization control**: BigDict with cD1–cD3 standardized. Outcome flips the finding's wording ("toxic" vs "needs scaling") — cheap, decisive.
2. **Regenerate BigDict-LASSO results** on full consistent windows (fix pywt even-length handling) + standardized features + LASSO max_iter raised.
3. **Multi-seed rerun (≥5 seeds)** for BigDictELM/Tree/SignalAdaptive with mean±sd; single-seed numbers get a `⚠ single-seed` marker everywhere.
4. **Fix the pywt window-dropping bug** so no experiment silently runs on 45% of its data.

**P1 — protocol consolidation**
5. Canonical eval: chaos = `chaos_protocol.py` (rolling, locked origins); linear tasks = frozen W=5 S47; real data = 20 rolling origins. Report raw **and** normalized, in one table.
6. Full DM pairwise grid with **Holm correction**; add significance stars to every results table.
7. Acquire genuinely real data (correct ETT source per `H720` lineage, real SSN sunspot) — or relabel the current "real" catalogs as synthetic in all docs.
8. Doc hygiene: update HANDOFF (KNN bug fixed) + AGENTIC_DISCOVERY ("7/6" → "7/8 wins, 8 tasks").

**P2 — strengthening the top-3 claims**
9. Per-dataset k search for KNN + stability report (k ∈ {5,12,24,48}).
10. Financial: walk-forward OOS + DM vs buy&hold on the cointegrated spread; only then keep the 60% directional claim alive.
11. `SignalAdaptiveBigDict` head-to-head vs fixed-compact and vs AMR-FBS on the canonical suite — this tests whether *routing* adds value (the AdaptiveAMRKNN result suggests it may not).

**Kill/archive now:** `amr_dynamo_attractor.py`, `amr_tree_elm.py` (freeze), `meta_ensemble_stacker.py`, `lasso_lag_mutation.py` (archive to `members/_archive/`).
