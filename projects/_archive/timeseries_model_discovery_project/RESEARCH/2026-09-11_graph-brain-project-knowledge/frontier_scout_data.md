---
type: Concept
title: frontier_scout_data
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Frontier Scout — New Data/Aux Signal to Break S-26 Terminal 1.9909

**Terminal:** S-26 `2× NLinear L336 a∈{1,10} + per-horizon ridge α=10000` → 1.9909/2.4710 (full 2161, `CONTEXT.md:4` LEADERBOARD_START). Contradiction 6→2 members, α* at penultimate grid point — pool exhaustion (`MONITORING/reflection/2026-09-11_graph-aware-overall-reflection.md:18-20` P3, `next_direction.md:3-4` Rank 1 rationale). 7 families rejected via held-out-half gate (`reflection.md:14-16` P2). Budget: ~2k val origins (`n2=1080/1081`), so DOF must be O(1) scalar, not new window.

**Protocol invariants (cite):** `./data.py:137-201` `ProtocolData` — `ETTh1.csv` 17,420 rows, `train.csv` 11,425 (8545 train + 2880 val), `test.csv` 2880, H=720 locked; `forecast_views()` / `rolling_views()` only sanctioned access, `__train/__test` name-mangled, `_cached_protocol()` single source. Anti-leakage: anchors/lags/norms from `self.history_` only; member factories must be `preds_for_train_fit` (8545) for val vs `preds_for_full_fit` (11425) for frozen test (P1 leakage scar). Aux available: file is 7-channel `date,HUFL,HULL,MUFL,MULL,LUFL,LULL,OT` (header `data.py:54` + csv check) — currently **univariate OT only**; exogenous 6 channels + `date` timestamp unused. Graph centrality: `python ../../brains/graph_brain/ask.py --hotspots | head -n 5` → `fit  ./methods/nlinear_knn.py:65  in=0 out=48 degree=48` (top hotspot, `ask.py --stats` 1021 CALLS / 273 nodes) and `_lag_dataset @ base.py:197 degree=27` — any window-feature change fans to all members (next_direction.md Rank 3 enabler); scalar aux avoids that blast radius.

**Explicitly NOT next (closed):** `next_direction.md:25-28` — multivariate 7-channel window closed at S-24, non-linear/trees/gated closed at S-21/S-21b/S-23, pool growth beyond 12 closed. S-24 finding `CONTEXT.md:92-94`: `multi_L336 val 2.2434 vs best univariate 2.85` but `test 2.0539 (+0.0559 vs 1.9980)` — cross-channel correlations fit val-local regime, flip on frozen test. Any revisit must be RevIN-normalized single probe + flip gate — not ranked. Both bets below deliberately violate S-24's failure mode.

---

## Bet 1 — Calendar phase scalar (highest EV, zero exogenous window)

**New information:** Absolute time — hour-of-day + day-of-week phase from `date`, orthogonal to OT history window. S-26 stack is purely auto-regressive (`OT[t-L:t]`); it cannot know wall-clock phase that drives daily load (`HUFL..LULL` are load channels, OT is temperature — calendar load cycle leaks into OT via physics, not lags).

**What (no code):** Single scalar `c_t = [sin(2π·hour/24), cos(2π·hour/24)] → 1-D phase` or `hour mod 24` distance, computed per origin from `eval_series` timestamp (strictly `history` time, no future). Stack becomes `M=2 → M=3` where third member is `calendar_bias[h] = γ_h · c_{t+h}` — per-horizon ridge with 1 scalar feature, same `S-20-clean` protocol (held-out n2 selection, refit-all-val, frozen 11425→concat test). DOF = 720 scalars, regularised by same 11-α grid; or even fixed `α=10000` to keep DOF minimal.

**Why not S-24 multivariate:** S-24 fed `7×L` raw exogenous window (672–2352 dims) through NLinear/RLinear — high-capacity cross-channel correlator that memorised val regime. This is **1 scalar per horizon, no HUFL..LULL channels touched**, no window matrix, no cross-channel weights. Falsifies via disjoint diagnostic if it were regime-memorization.

**Falsifiable acceptance:**
- Selector `full 2161 MAE < 1.9909 - 0.005` (i.e. ≤1.9859) with `α*` interior (not all 30000) on held-out half.
- Disjoint guard: `disjoint-4` also improves vs S-26 `1.9696` (`CONTEXT.md:102`), or at least not worse by >0.002 — else regime bet.
- Leakage guard: `c_t` derived from `history_[ -720 + h ]` timestamp only; no `test[t:t+720]` peeking; `preds_for_train_fit` / `preds_for_full_fit` split respected.
- Scar guard: `[10] P4 val→test flip gate` — held-out half must beat ridge delta before frozen test (val selector is gate); `[9] P3 disjoint selector` — `full 2161` is selector, `disjoint-4` diagnostic only, never selector (next_direction.md:12).

**Reject →** calendar phase carries no orthogonal signal at H=720 beyond what L336 window already spans.

## Bet 2 — RevIN window-statistic scalar (per-origin OT norm residual)

**New information:** Per-origin window scale — `μ = mean(history_[-L:])`, `σ = std(history_[-L:])` (L=336, same as incumbent lookback) as a single scalar correction, not a new member pool. RevIN-style but as **1-D residual gate**, not per-channel normalisation. S-04 found norm@720 helps kNN but hurts ELM; S-24's multivariate RevIN variants were untested in isolation — this is the deprioritised single RevIN-normalised exogenous probe (`reflection.md:87` open_risks) collapsed to univariate OT statistics.

**What:** Append one scalar `s_t = (OT_{t+h} residual bias) ≈ σ_t` as per-horizon coefficient: `pred = ridge_2member(t,h) + β_h · σ_t` (or `μ_t` demeaned), ridge-fitted per horizon on same held-out split. Alternative: `RevIN residual = (history_[-L:] - μ)/σ` already in NLinear — this bet exposes the **discarded scale** as explicit signal. Still `data.py:166-168` fit_history only.

**Why not S-24 multivariate:** No HUFL..LULL, no `7×L` window matrix, no multi-channel member. One scalar derived from OT window itself (information already in L336 window but non-linearly via σ), so capacity is 720 weights vs S-24's `7×336 + 720×8` weights. Heavy shrinkage guard applies (`α=10000` penultimate signals over-parameterisation — P3 invariant).

**Falsifiable acceptance:** Identical to Bet 1 — `full 2161 Δ < -0.005`, disjoint not harmed, held-out beats no-intercept ridge delta (`2.5191` at `α=10000` per `CONTEXT.md:106-107`), `α*` interior. Additional guard: vary L∈{96,336,720} scalar — if best L differs between held-out and disjoint, reject as scale-regime mem.

**Reject →** window scale is already spanned by linear span of L336 + heavy ridge; no gain under ~2k budget.

---

**Scout stop rule:** If both reject, S-26 is terminal for univariate linear span under ~2k val budget; next frontier needs external data (holiday calendar, weather reanalysis) beyond ETTh1 file, per `next_direction.md:30`.

**Cites:** `reflection.md:9-24 P2/P3`, `next_direction.md:5-12/25-30 ranks + Explicitly NOT next`, `data.py:54-68 constants + 137-201 ProtocolData`, `CONTEXT.md:92-102 S-24/S-26 + 4 LEADERBOARD_START`, `ask.py --hotspots:69 nlinear_knn.py:65 degree 48`, `ask.py --stats: 1021 CALLS 273 nodes`.
