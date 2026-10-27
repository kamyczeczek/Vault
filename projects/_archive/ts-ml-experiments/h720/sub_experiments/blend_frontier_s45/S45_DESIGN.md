---
type: Concept
title: S45_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-45 Design — Blend-Frontier Expansion vs the S-44 Incumbent Blend (Pre-Registration)

**Date:** 2026-09-14
**Slice:** `S-45-blend-frontier` · **Directory:** `projects/ts-ml-experiments/h720/sub_experiments/blend_frontier_s45/`
**Status:** Pre-registration design ONLY — a separate executor implements after parent approval.
**Supersedes:** none — first bet against the S-44 blend incumbent; no prior registration is re-declared.
**Governing invariants:** S-43 P1 (gate semantics declared up front — BINDING), P2 (per-window deltas vs the in-harness incumbent), P3 (surviving positive recorded), P4 (portfolio frontier record) — `MONITORING/reflection/2026-09-13_2350_S-43-bet3-terminal-close.md`; S-44 P1 (parity block binding on every future bet), P2 (incumbent anchors re-derived in-harness vs the CURRENT incumbent; future bets target 1.9781) — `MONITORING/reflection/2026-09-14_0348_S-44-blend-promotion.md`; `CONTEXT.md` `## Prevention rules — S-43` + S-44 section.

## 1. Motivation & lineage

**S-44 → S-45.** S-44 promoted the Bet 3 blend to incumbent: 3-member `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L]`, per-horizon ridge no-intercept α=30000, members frozen 8545/11425 — full **1.978126 / RMSE 2.461264**, disjoint-4 **1.863419**, paired-vs-S-26 Δ 95% CI **[−0.018506, −0.006913]** (`results_s44.json`). Its `plan_impact.opens` named the frontier this bet enters: *"blend-incumbent frontier: future bets must beat the S-44 blend under a declared gate."* S-44 P2 fixes the target: **1.9781**, anchors re-derived in-harness.

**The two licensing clauses** (both closed families left an explicit exception; S-45's cross member is the first candidate satisfying BOTH simultaneously):
- **Bet 2** (linear multivariate close, `CONTEXT.md` Bet 2 section tail): *"No further linear multivariate members without a non-linear cross-channel interaction."*
- **Bet 3** (patch-attention non-linear close, `RESEARCH/next-frontier-scout-2026-09-13.md` §4 tail, body quoted in `CONTEXT.md` Bet 3 section): *"No further non-linear readouts on `L≤336` without exogenous channels or a different pretext (e.g. masked pre-training)."*

`patchtst_cross_P24_D32_2L` is a **non-linear (attention) readout WITH exogenous channels** whose bidirectional attention runs **across channels** — the non-linear cross-channel interaction Bet 2 demands, on the exogenous inputs Bet 3 demands. It is neither a linear multivariate member (Bet 2's closed class) nor a univariate non-linear readout on L≤336 (Bet 3's closed class). **`patchtst_P24_D32_2L_s1`** is the incumbent's univariate PatchTST-Delta architecture retrained with seed 1 — cheap seed-diversity: S-44 proved the P24 member carries transferable signal (held-out gain +0.0204, test −0.0128); an independent-seed twin is the lowest-variance diversity candidate. NOT a family re-opening: same architecture, no capability claim, purely a blend member (the patch-attention member-capability close stands; the incumbent already contains its seed-0 sibling).

**Why legitimate.** One frozen run, zero tuning (D10), a declared blend-based gate vs the in-harness incumbent (D2), a binding parity block on the incumbent re-derivation (D6), honest close conditions (D5). No prior evidence exists — unlike S-44, this design asserts no expected verdict.

## 2. Gate-semantics declaration (S-43 P1, stated up front)

| Element | Semantics for S-45 |
|---|---|
| **Binding gate** | **BLEND-based**: the frozen-test stacked blend of the tabu-selected subset must beat the **S-44 incumbent blend re-derived in-harness** (G1–G4, D2) — NOT vs S-26. |
| **Singleton screen** | Demoted to non-binding diagnostic (new-member singleton vals, D5). Cannot flip PASS→FAIL. |
| **Resolution on disagreement** | The blend decides. A blend win does NOT re-open either closed family (Bet 2 linear-multivariate, Bet 3 patch-attention member capability); a blend loss does not extend them. The seed twin makes no capability claim either way. |

## 3. Mandatory design decisions

### D1 — Slice identity, artifacts & the seed mechanism
Slice id `S-45-blend-frontier`; directory `sub_experiments/blend_frontier_s45/` with `S45_DESIGN.md` (this file), `rolling_arm.py`, `patchtst_cross.py` (new-member module: the cross-attention member AND the seed-1 twin wrapper), `results_s45.json`, `harness.log`. Both new members import the Bet 3 encoder classes (`PatchTSTDelta`, `PatchTSTEncoder`, `_StochasticDepth`, `ffn_for`) VERBATIM from the sibling `patchtst_delta_bet3/` directory via `sys.path.insert` (S-44 precedent, recorded as a `harness.log` audit line) — architecture-identical code by construction, not transcription.
**Seed-1 twin mechanism (fixed):** `patchtst_cross.py` defines `_set_deterministic_seed(seed)` (torch.manual_seed(seed), np.random.seed(seed), `use_deterministic_algorithms(True, warn_only=True)`, cudnn deterministic/benchmark-off) and `class PatchTSTModelS1(PatchTSTModel)` whose `fit()` is a **line-for-line mirror of Bet 3's `PatchTSTModel.fit` with exactly ONE change**: the module-level `_set_deterministic()` call (seed 0) is replaced by `_set_deterministic_seed(1)`. Why not re-seed before `fit()`: Bet 3's `fit()` calls the module-level `_set_deterministic()` internally at its start (`patchtst_encoder.py:211`), overwriting any external pre-seed — the seed MUST be parameterized at that call site. The mirror is documented in the module docstring (only-delta note) + a `harness.log` audit line. Seed 1 is set BEFORE `PatchTSTDelta` construction, so weight init AND `torch.randperm` batch order both derive from seed 1 — a genuinely independent draw. Determinism tripwire: twin predictions exactly equal to the seed-0 member's ⇒ seed discipline violated ⇒ run VOID (D9).

### D2 — Binding gate is blend-based vs the S-44 incumbent; promotion = incumbent replacement
The tabu-selected subset's frozen-test blend must satisfy ALL of (every threshold vs the **in-harness S-44 incumbent re-derivation** from the same run, D7; parity-anchored to the `results_s44.json` values in §5):

| # | Binding condition |
|---|---|
| G1 | `MAE_full(2161) ≤ in-harness incumbent full − 0.0050` (= 1.978126 − 0.0050 = **1.9731**; the H2 ≥0.0050-improvement bound applied to the new incumbent) |
| G2 | `MAE_full < in-harness incumbent full` (**< 1.9781**; strictly better) |
| G3 | `MAE_disjoint-4 ≤ in-harness incumbent disjoint-4` (**≤ 1.8634**) |
| G4 | Paired-bootstrap Δ CI upper < 0 — Δ = per-origin MAE(new blend) − per-origin MAE(S-44 incumbent, in-harness), B=2000, seed 0, resample origins, percentile 2.5/97.5 — convention identical to S-44's `bootstrap_paired_diff_ci` (Bet 3 `rolling_arm.py:168-176`) |

**G3 justification (incumbent-relative is the honest bar):** the incumbent's disjoint-4 (1.8634) is far below the S-26 cap (1.9696); a blend clearing only the S-26 cap could still be disjoint-wise much worse than the incumbent (e.g. 1.95 ≤ 1.9696 but ≫ 1.8634) — promoting it would silently trade disjoint robustness for mean. G3 therefore binds **incumbent-relative**; the S-26 stability cap (≤ 1.9696) is retained as a **secondary reported check** (non-binding; a breach above even the old cap is a red flag surfaced in the artifact). **PROMOTION = incumbent replacement**: CONTEXT.md top row becomes the S-45 blend; the S-44 row is demoted with a dethroned annotation; S-26 drops to third place; all incumbent references re-anchor per S-44 P2.

### D3 — Pool frozen M=6 = the 4 S-44 pool members + exactly 2 new members (zero tuning)
Pool order FIXED (tabu neighbor enumeration and stable-sort tie-breaking depend on it): `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L, patchtst_P48_D16_1L, patchtst_P24_D32_2L_s1, patchtst_cross_P24_D32_2L]`. The first 4 are the S-44 pool verbatim: NLinear factories from `methods/neural_models.py`, PatchTST members via the Bet 3 encoder import (seed 0), identical constructor args to S-44's `rolling_arm.py:90-97`. NO other changes.
**`patchtst_cross_P24_D32_2L`** (7-channel level-free cross-attention PatchTST):
- **Data path (Bet 2's multivariate loading, mirrored exactly):** `load_multivariate_split()` pattern — `H720_ROOT/train.csv` + `test.csv`, CSV column order `[HUFL, HULL, MUFL, MULL, LUFL, LULL, OT]`, reordered to `CHANNELS = [OT, HUFL, HULL, MUFL, MULL, LUFL, LULL]` via `CHANNEL_TO_CSV_IDX` (`group_sparse_bet2/rolling_arm.py:46-47,149-168`); fail-loud sync asserts `np.allclose(fit_multi[:, 0], fit_series)` and the test-side equivalent (Bet 2 `rolling_arm.py:289` pattern).
- **Tokens:** per window `W ∈ R^{336×7}`, level-free shift per channel `W̃ = W − W[335]` (each channel's own last value, broadcast); per channel reshape to 14 patches × P=24; token stream `T ∈ R^{98×24}`, token `t = c·14 + p` (channel-major). Channel-shared linear patch projection `proj: R^24 → R^32` + learnable positional encoding (per patch position, `R^{14×32}`) + learnable channel embedding (`R^{7×32}`): `h_t = proj(x_t) + pos[p] + ch[c]`, dropout 0.30.
- **Encoder:** 2-layer `nn.TransformerEncoder` (D=32, heads=2, FFN=64, dropout 0.30, GELU, norm_first, attn-dropout 0.2, **NO causal mask**) — bidirectional attention over all 98 tokens lets tokens attend ACROSS channels (the non-linear cross-channel interaction); per-layer `_StochasticDepth(0.10)` post-encoder (no-op at inference, Bet 3 pattern).
- **Standardization:** train-only per-channel-per-patch-position-per-element μ/σ ∈ `R^{7×14×24}` over the level-free shifted windows of the training series ONLY (8545 for the val-phase fit; recomputed on 11425 for the test-phase refit — Bet 2 patch_embed train-only rule, extended per channel), σ floored 1e-6.
- **Decoder:** mean-pool over all 98 tokens → per-horizon linear head `R^32 → R^720` → OT delta; predict: delta + OT `window[-1]` (same anchor discipline as the univariate member). Target is OT-only (`y_delta = OT[end:end+720] − OT_anchor`) — multivariate information enters ONLY through inputs.
- **Training config (Bet 3 values verbatim):** AdamW 3e-4, batch 64, grad clip 1.0, MAE loss on deltas, seed 0, deterministic CPU; weight-decay grouping mirrored from Bet 3 `_build_param_groups` (decay 1e-2 on proj+head; none on norms, pos, channel embedding). Trains on the same windows as the univariate member (`end ∈ [336, len(series)−H]`); internal chronological tail split `n//8` for early stopping on val delta-MAE — **shipped Bet 3 discipline: patience 40, max_epochs 400** (`patchtst_encoder.py:158`). *Resolution note:* the "patience 5 max 50" phrasing carried from S-44 D3 describes the Bet 1 LoRA discipline; S-44's executor used the shipped Bet 3 defaults and 59/59 parity at abs_diff 0.0 confirmed that reading — it binds here ("Bet 3 verbatim" = the shipped code path). Capacity ≈58k params (same envelope as the univariate primary's 57,648 — zero-tuning capacity discipline; exact count recorded in the artifact).

**`patchtst_P24_D32_2L_s1`**: `PatchTSTModelS1(patch_size=24, D=32, n_layers=2, H=720)` — identical config to the incumbent's P24 member except the seed (D1 mechanism).

### D4 — Selection protocol identical to S-44/Bet 3; held-out control = the incumbent re-derived
Tabu-7 over the frozen M=6 pool (fixed-α fast 3000, aspiration, `no_improve=5`, init = best singleton, max_iter 25 cap, neighbor enumeration by sorted member index — Bet 3 code path) → chronological ridge selection: 11-α grid `[0.1, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000]`, per-horizon ridge **no-intercept**, fit `val[0:1080)` / select `val[1080:2161)` (pooled MAE). Members frozen `8545` for val, refit `11425` for frozen test. `val_full` = chronological half-split (fit `val[0:1080)` at selected α, score `val[1080:2161)`). Assertions `n_val == 2161`, `len(train_series) == 8545`, `len(fit_series) == 11425` (Bet 3).
**Held-out control:** the **S-44 incumbent blend re-derived on val** — its 3-member subset at its α (per-horizon ridge no-intercept **α=30000**, fit `val[0:1080)`, scored `val[1080:2161)`); by construction this equals the incumbent's `val_full` **2.493567** (§5 parity row). **Precondition to frozen test:** the selected subset's best-α half-split score (`score_full` convention) must beat the control by **> 0.005** (i.e. < 2.4886 given parity); fail ⇒ REJECT at plan time (C2). Frozen-test stack = the val half-split `stack` at `best_alpha` applied to the 11425-refit members' test predictions (Bet 3/S-44 convention exactly); the incumbent's test metrics likewise from its own α=30000 half-split stack on the 11425-refit incumbent members.

### D5 — Demoted diagnostics + close conditions (incl. the S-20-clean family close)
**Demoted (non-binding, cannot flip PASS→FAIL):** new-member singleton vals (twin, cross); train-val gaps for all 4 PatchTST-family members (flag > 0.15); attention entropy (nats, as shipped; collapse flag < 0.5 — for the cross member the uniform-attention ceiling is ln 98 ≈ 4.58 vs ln 14 ≈ 2.64 univariate, threshold unchanged); W1–W4 deltas vs the **in-harness incumbent blend's own W1–W4** (same run, S-44 P2); horizon tercile deltas likewise; twin-vs-seed0 prediction divergence on val (mean |Δpred| + correlation — measures whether seed diversity materialized; exact 0 ⇒ VOID, D9).
**Close conditions (any → REJECT):**
- **C1** selected subset ⊆ S-44 pool (no new member — nothing gained; S-44 remains incumbent; no further same-class members without new pre-registration);
- **C2** held-out gain ≤ 0.005 (plan-time precondition);
- **C3** paired Δ CI upper ≥ 0;
- **C4** any of G1–G3 fails.
**On REJECT:** S-44 stays incumbent; the cross-channel-attention and seed-diversity directions are recorded with their numbers (S-43 P3 analog — future proposals refused by citation). **Family close (additional, fires only if):** BOTH new members' singleton val > 2.90 AND no subset containing a new member scores better than the incumbent's held-out control (2.493567) on `val[1080:2161)` ⇒ declare the **blend-frontier-expansion family closed under S-20-clean**, citing both licensing clauses as spent (Bet 2's non-linear-cross-channel exception and Bet 3's exogenous-channels exception were exercised and produced nothing at this data budget).

### D6 — Parity block (S-44 P1 — binding on every future bet)
Within the SAME harness run, the S-44 incumbent is re-derived as a subset evaluation (its 3 members are in the M=6 pool; its stack at its α=30000) and parity-checked vs `results_s44.json` on every §5 row at tol 1e-4, plus the fail-loud S-26 anchor (1.990897 / 2.470999 / 1.969617 / 1.957937 ± 1e-4). **If any parity row fails > 1e-4: verdict VOID (`ABORT_PARITY`)** — the harness (not the numbers) is wrong; fix the harness and re-run; no verdict is emitted from a parity-failing run. Parity proves the incumbent comparison is against the real incumbent, not a drifted re-implementation.

### D7 — Incumbent anchor discipline (S-44 P2)
Every comparison, bootstrap, and W-window/tercile delta in the artifact is vs the **in-harness S-44 blend derivation from the same run** — never a constant copied from a leaderboard. The ONLY permitted copied constants are the §5 parity expected-values themselves (ground truth from `results_s44.json`). The binding thresholds of D2 are computed from the in-harness incumbent values (which parity anchors to 1.978126 / 1.863419).

### D8 — Artifacts
`results_s45.json` (schema §6) + `harness.log` (mirrors S-44's log format: member-training lines, tabu trace lines, audit lines [encoder import, seed-mechanism only-delta, multivariate sync asserts], bootstrap/stratified lines, parity lines, binding-gate line, close-conditions line, final `VERDICT=PROMOTED|REJECTED` line) + `patchtst_cross.py` + this design. Harness command recorded in the artifact: `C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe projects/ts-ml-experiments/h720/sub_experiments/blend_frontier_s45/rolling_arm.py` (hermes venv python, CPU torch — S-44 ran torch 2.13.0+cpu, 452.1 s; S-45 expected ~450–700 s: 2 extra members to train in the val phase + 2 refits in the test phase; the cross member's 98-token encoder is the heavy item — wall time materially beyond the range is a report fact, not a protocol deviation).

### D9 — What would falsify / abort / void
1. **Parity failure > 1e-4 on any §5 row** (or S-26 anchor) ⇒ VOID (`ABORT_PARITY`) — harness bug (nondeterminism or transcription); fix, re-run.
2. **C1 collapse** — tabu selects a subset ⊆ S-44 pool ⇒ REJECT (honest record; nothing gained).
3. **Binding failure** — any of G1–G4 fails ⇒ REJECT (honest record; S-44 stays incumbent).
4. **Nondeterminism / seed-discipline violation** — e.g. the twin trained under seed 0 (exposed by exact-0 divergence vs the seed-0 member) ⇒ VOID.
5. **Cross-member leakage** — if the cross member's training inputs are found to contain any val/test content beyond the S-20-clean freeze discipline (fit series = train.csv rows only: 8545 val-phase / 11425 test-phase refit; μ/σ from train-only windows; multivariate test.csv rows enter ONLY via the rolling history swap for test-origin predictions) ⇒ the entire run is VOID.

### D10 — Budget
Single run, deterministic, zero tuning. No additional seeds beyond the seed-1 twin (which IS one of the two new members). No grid beyond the protocol's fixed 11-α grid. No architecture sweeps; all new-member hyperparameters are the Bet 3 values verbatim (D3).

## 4. Acceptance & close conditions

| Condition | Type | Threshold | Gate |
|---|---|---|---|
| G1 full MAE | binding | ≤ 1.9731 (incumbent 1.978126 − 0.0050) | promote |
| G2 full MAE vs incumbent | binding | < 1.9781 (in-harness incumbent) | promote |
| G3 disjoint-4 | binding | ≤ 1.8634 (in-harness incumbent disjoint) | promote |
| G4 paired Δ CI upper (vs incumbent) | binding | < 0 (B=2000, seed 0, resample origins) | promote |
| S-26 stability cap (secondary) | non-binding check | disjoint ≤ 1.9696 | report |
| Held-out gain (precondition to test) | procedural | > 0.005 vs control 2.493567 | reach test |
| C1 subset ⊆ S-44 pool | close | no new member selected | reject |
| C2 held-out gain ≤ 0.005 | close | ≤ 0.005 | reject |
| C3 paired CI upper ≥ 0 | close | ≥ 0 | reject |
| C4 any of G1–G3 fails | close | — | reject |
| Family close (S-20-clean) | close | BOTH new-member singleton vals > 2.90 AND no new-member subset beats 2.493567 held-out | close family |
| New-member singleton vals | non-binding diagnostic | (info) | report |
| Train-val gap | non-binding diagnostic | (info; flag > 0.15) | report |
| Attention entropy | non-binding diagnostic | (info; collapse < 0.5 nats) | report |
| W1–W4 deltas vs in-harness incumbent | non-binding diagnostic | (info) | report |
| Horizon tercile deltas vs incumbent | non-binding diagnostic | (info) | report |
| Twin divergence vs seed-0 (val) | diagnostic + tripwire | (info; == 0 ⇒ VOID) | report |
| Parity vs `results_s44.json` (§5) | harness acceptance | ≤ 1e-4 each | abort if violated |

## 5. Parity requirements (vs `results_s44.json` — incumbent re-derivation, tol 1e-4 unless noted)

| Quantity | S-44 value | Tolerance |
|---|---|---|
| Incumbent subset (as subset eval) | `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L]` | exact |
| Incumbent stack α | 30000 | exact |
| Incumbent best_fast (3-member fast @ α=3000, val[1080:2161)) | 2.502112 (2.5021117513632665) | 1e-4 |
| Incumbent val_full (3-member @ α=30000, held-out half) = held-out control | 2.4936 (2.493567251979277) | 1e-4 |
| Singleton vals (incumbent-pool members, frozen 8545) | 2.8970 / 2.8970 / 3.0267 / 3.1517 (2.896975832201712 / 2.896964035619671 / 3.026725290054874 / 3.15167046606894) | 1e-4 |
| Incumbent test_full MAE / RMSE | 1.978126 / 2.461264 (1.9781264265828236 / 2.4612639073807663) | 1e-4 |
| Incumbent test_disjoint-4 | 1.863419 (1.8634190252257932) | 1e-4 |
| Incumbent test_W4 | 1.889616 (1.8896163750508768) | 1e-4 |
| Incumbent W1 / W2 / W3 | 2.160695 / 1.565548 / 2.208259 (2.1606949742408026 / 1.5655481914300127 / 2.208259044704783) | 1e-4 |
| Incumbent horizon terciles | 1.826621 / 1.978770 / 2.128989 (full precision in `results_s44.json.stratified`) | 1e-4 |
| Incumbent paired Δ-vs-S-26 CI (re-derived) | [−0.018506, −0.006913] (mean −0.012771) | 1e-4 |
| S-26 anchor (re-derived, fail-loud) | 1.990897 / 2.470999 / 1.969617 / 1.957937 | 1e-4 |

Failure of any row > 1e-4 ⇒ `parity.all_pass = false` ⇒ harness bug ⇒ VOID (`ABORT_PARITY`), fix, re-run. The promotion/rejection verdict is emitted only from a parity-passing run. These expected-values are the only copied constants in the harness (D7).

## 6. Artifact schema — `results_s45.json`

```json
{
  "slice": "S-45-blend-frontier",
  "harness_command": "C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe projects/ts-ml-experiments/h720/sub_experiments/blend_frontier_s45/rolling_arm.py",
  "device": "<as-run, e.g. cpu (torch 2.13.0+cpu)>",
  "protocol": "S-20-clean blend-frontier expansion of the S-44 incumbent; binding gate BLEND-based vs the in-harness S-44 incumbent re-derivation (S-43 P1 / S-44 P2); parity block per S-44 P1",
  "pool": ["nlinear_L336_a1", "nlinear_L336_a10", "patchtst_P24_D32_2L", "patchtst_P48_D16_1L", "patchtst_P24_D32_2L_s1", "patchtst_cross_P24_D32_2L"],
  "new_members": {
    "patchtst_P24_D32_2L_s1": {"type": "seed-1 twin of the incumbent's univariate PatchTST-Delta member (Bet 3 architecture verbatim)", "seed": 1},
    "patchtst_cross_P24_D32_2L": {"type": "7-channel level-free cross-attention PatchTST: 98 tokens (7ch x 14 patches), channel-shared proj P24->D32 + channel embedding + pos encoding, 2-layer Transformer heads=2 FFN=64, no causal mask", "seed": 0}
  },
  "params": {"L": 336, "P": 24, "D": 32, "layers": 2, "heads": 2, "ffn": 64, "dropout": 0.3, "stochastic_depth": 0.1, "weight_decay": 0.01, "attn_dropout": 0.2, "lr": 0.0003, "batch": 64, "grad_clip": 1.0, "H": 720, "capacity_cross_params": 0, "capacity_twin_params": 57648, "early_stop": "patience 40, max_epochs 400, internal n//8 chronological tail split (Bet 3 shipped discipline)"},
  "incumbent_s44_rederived": {"subset": ["nlinear_L336_a1", "nlinear_L336_a10", "patchtst_P24_D32_2L"], "alpha": 30000.0, "best_fast": 0.0, "val_full": 0.0, "test_full_mae": 0.0, "test_full_rmse": 0.0, "test_disjoint_mae": 0.0, "test_w4_mae": 0.0, "w1_w4": [0.0, 0.0, 0.0, 0.0], "horizon_terciles": [0.0, 0.0, 0.0]},
  "s26_anchor": {"mae": 0.0, "rmse": 0.0, "disjoint": 0.0, "w4": 0.0, "tol": 0.0001, "expected": {"mae": 1.990897385574145, "rmse": 2.470998626872596, "disjoint": 1.9696168477494975, "w4": 1.9579365851264652}, "pass": true},
  "held_out_control": {"type": "S-44 incumbent 3-member blend re-derived: per-horizon ridge no-intercept alpha=30000, fit val[0:1080), scored val[1080:2161)", "mae_val_heldout": 0.0, "alpha": 30000.0},
  "singleton_val": {"nlinear_L336_a1": 0.0, "nlinear_L336_a10": 0.0, "patchtst_P24_D32_2L": 0.0, "patchtst_P48_D16_1L": 0.0, "patchtst_P24_D32_2L_s1": 0.0, "patchtst_cross_P24_D32_2L": 0.0},
  "trace": [{"iter": 0, "cur": ["..."], "fast": 0.0, "true": 0.0, "alpha": 0.0, "best_fast": 0.0, "best_set": ["..."]}],
  "best_subset": ["..."], "best_idx": [0], "best_fast": 0.0, "best_alpha": 0.0,
  "val_full": 0.0, "heldout_gain_over_control": 0.0, "heldout_precondition_pass": true,
  "parity": {"tol": 0.0001, "checks": [{"quantity": "incumbent_test_full_mae", "s44": 1.9781264265828236, "s45": 0.0, "abs_diff": 0.0, "pass": true}], "all_pass": true},
  "binding_gate": {
    "full_le_incumbent_minus_005": {"value": 0.0, "threshold": 1.9731, "pass": true},
    "full_lt_incumbent": {"value": 0.0, "incumbent": 1.9781, "pass": true},
    "disjoint_le_incumbent": {"value": 0.0, "incumbent": 1.8634, "pass": true},
    "paired_ci_upper_lt_0": {"ci_95": [0.0, 0.0], "upper": 0.0, "pass": true},
    "all_binding_pass": true
  },
  "secondary_checks": {"disjoint_le_s26_cap_19696": {"value": 0.0, "cap": 1.9696, "pass": true, "binding": false}},
  "demoted_diagnostics": {
    "new_member_singleton_vals": {"patchtst_P24_D32_2L_s1": 0.0, "patchtst_cross_P24_D32_2L": 0.0},
    "train_val_gap": {"patchtst_P24_D32_2L": 0.0, "patchtst_P48_D16_1L": 0.0, "patchtst_P24_D32_2L_s1": 0.0, "patchtst_cross_P24_D32_2L": 0.0}, "gap_flag": true,
    "attention_entropy_last": {"patchtst_P24_D32_2L": 0.0, "patchtst_P48_D16_1L": 0.0, "patchtst_P24_D32_2L_s1": 0.0, "patchtst_cross_P24_D32_2L": 0.0}, "entropy_collapse": false,
    "twin_vs_seed0_divergence_val": {"mean_abs_delta_pred": 0.0, "corr": 0.0, "exact_zero": false},
    "w1_w4_deltas_vs_incumbent": [{"window": "W1", "s45_mae": 0.0, "incumbent_mae": 0.0, "delta": 0.0}],
    "horizon_terciles": [{"horizon_tercile": "h1_first240", "s45_mae": 0.0, "incumbent_mae": 0.0, "delta": 0.0}]
  },
  "test_full": {"mae": 0.0, "rmse": 0.0, "n": 2161, "delta_vs_incumbent": 0.0},
  "bootstrap": {"convention": "resample origins, B=2000, seed 0, percentile 2.5/97.5", "s45_full": {"mean": 0.0, "ci_95": [0.0, 0.0], "B": 2000}, "incumbent_full": {"mean": 0.0, "ci_95": [0.0, 0.0], "B": 2000}, "paired_delta": {"mean": 0.0, "ci_95": [0.0, 0.0], "B": 2000, "upper_bound_negative": true}},
  "stratified": {"disjoint_windows": [{"window": "W1", "start": 0, "s45_mae": 0.0, "incumbent_mae": 0.0, "delta": 0.0}], "horizon_terciles": []},
  "test_disjoint": {"mae": 0.0, "rmse": 0.0},
  "test_w4": {"mae": 0.0, "incumbent_w4": 0.0, "delta_vs_incumbent": 0.0, "binding": false},
  "close": {"condition": "subset-of-S44-pool OR heldout_gain<=0.005 OR paired_ci_upper>=0 OR any G1-G3 fails", "c1_subset_of_s44_pool": false, "c2_heldout_gain": false, "c3_ci_upper_ge_0": false, "c4_any_g1_g3_fails": false, "family_close_s20_clean": false, "trigger": false, "message": "..."},
  "verdict": "PROMOTED|REJECTED",
  "plan_impact": {"invalidates": "S-44 incumbent status on PROMOTION (S-44 row demoted with dethroned annotation; S-26 drops to third)", "confirms": "on REJECT: S-44 remains incumbent; cross-channel-attention and seed-diversity directions recorded with numbers", "opens": "on PROMOTION: re-anchored blend-incumbent frontier (S-44 P2 turnover applies)"},
  "elapsed_s": 0.0
}
```

## 7. What would falsify this bet

1. **Parity failure > 1e-4 on any §5 row or the S-26 anchor** — the harness (not the numbers) is wrong: nondeterminism (seed-0/seed-1 discipline violation, GPU nondeterminism), a transcription error, or protocol drift. VOID (`ABORT_PARITY`), fix, re-run; no verdict from a parity-failing run.
2. **Twin divergence exactly 0** — the seed-1 mechanism failed (twin trained under seed 0 and duplicated the incumbent member) ⇒ seed-discipline violation ⇒ VOID.
3. **Cross-member leakage** — any val/test content in the cross member's training inputs beyond the S-20-clean freeze discipline ⇒ entire run VOID.
4. **C1 collapse** — tabu selects a subset of the S-44 pool only ⇒ REJECT; nothing gained; both new directions recorded with their singleton vals; no further same-class members without new pre-registration.
5. **A binding condition fails** (G1–G4) or the held-out precondition (C2) ⇒ REJECT; S-44 stays incumbent; if additionally both new-member singleton vals > 2.90 AND no new-member subset beats 2.493567 held-out, the blend-frontier-expansion family closes under S-20-clean (licensing clauses spent).
6. **Post-promotion falsifier (normal science):** a later pre-registered bet beating the S-45 blend under its own declared gate supersedes it — standard incumbent turnover; does not falsify S-45's evidence.

## 8. Cited evidence

- `projects/ts-ml-experiments/h720/CONTEXT.md` — leaderboard top rows (S-44 incumbent 1.9781/2.4613; S-26 1.9909/2.4710 dethroned row), Bet 2 section (~line 367, close tail = licensing clause 1), Bet 3 section (~line 376), `## Prevention rules — S-43` (~line 389, P1–P4), S-44 section (~line 397, standing-after-promotion: future bets must beat the S-44 blend under a declared gate).
- `RESEARCH/next-frontier-scout-2026-09-13.md` §4 (Bet 3 spec + close condition, line 126 tail = licensing clause 2), §6.
- `projects/ts-ml-experiments/h720/sub_experiments/blend_promotion_s44/S44_DESIGN.md` (structural precedent: D-numbered decisions, §4/§5/§6/§7) + `results_s44.json` (every §5 parity value at full precision: best_fast 2.5021117513632665, val_full 2.493567251979277, test_full 1.9781264265828236/2.4612639073807663, disjoint 1.8634190252257932, W4 1.8896163750508768, paired CI [−0.018505562732342832, −0.006913352503709525]) + `harness.log` (parity 59/59 abs_diff 0.0).
- `projects/ts-ml-experiments/h720/sub_experiments/patchtst_delta_bet3/patchtst_encoder.py` (encoder classes verbatim-imported; `_set_deterministic` line 32; `PatchTSTModel.fit` seed call line 211; patience/max_epochs defaults line 158) + `rolling_arm.py` (stack machinery, tabu, `bootstrap_paired_diff_ci` lines 168–176, `_verify_s26_anchor` lines 189–235).
- `projects/ts-ml-experiments/h720/sub_experiments/group_sparse_bet2/patch_embed.py` (CHANNELS, train-only μ/σ) + `rolling_arm.py` (CSV_COLS/CHANNEL_TO_CSV_IDX lines 46–47, `load_multivariate_split` lines 149–168, multivariate dispatch lines 171–196, sync assert line 289).
- `projects/ts-ml-experiments/h720/data.py` (`get_protocol_data`, `rolling_views`; Bet 2's multivariate path is the loading precedent — the cross member mirrors it, D3).
- `MONITORING/reflection/2026-09-14_0348_S-44-blend-promotion.md` (P1 parity-block rule, P2 incumbent-anchor discipline + turnover anchors) · `MONITORING/reflection/2026-09-13_2350_S-43-bet3-terminal-close.md` (P1–P4 invariants).

**Expected verdict: none asserted.** S-45 is a new bet with no prior evidence on file; the verdict is whatever the single frozen, parity-passing run emits under the declared gate.
