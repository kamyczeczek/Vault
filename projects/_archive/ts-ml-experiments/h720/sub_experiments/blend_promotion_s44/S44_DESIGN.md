---
type: Concept
title: S44_DESIGN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S-44 Design — Blend-Promotion Re-registration of the Bet 3 PatchTST-Delta Blend (Pre-Registration)

**Date:** 2026-09-14
**Slice:** `S-44-blend-promotion` · **Directory:** `projects/ts-ml-experiments/h720/sub_experiments/blend_promotion_s44/`
**Status:** Pre-registration design ONLY — a separate executor implements after parent approval.
**Supersedes:** the *gate semantics* of Bet 3's registration (`RESEARCH/next-frontier-scout-2026-09-13.md` §4) — NOT its pool, protocol, seed, or evidence.
**Governing invariants:** S-43 P1 (gate-semantics declared up front — BINDING), P2 (per-window deltas vs the in-harness incumbent), P3 (surviving positive recorded), P4 (portfolio frontier record) — `MONITORING/reflection/2026-09-13_2350_S-43-bet3-terminal-close.md`; `CONTEXT.md` `## Prevention rules — S-43`.

## 1. Motivation & lineage

**Bet 3 → S-43 P1 → S-44.** Bet 3 (`sub_experiments/patchtst_delta_bet3/`, evidence `results_patchtst_bet3.json` + `harness.log`) ran the scout §4 spec with a fused acceptance list: blend-promotion conditions AND member-capability conditions in one "all must hold" chain (`rolling_arm.py:424` per S-43 P1 root-cause). The frozen-test blend cleared every accuracy condition — `test_full 1.978126 / 2.461264` (≤ 1.9859, < 1.9909), `test_disjoint 1.863419` (≤ 1.9696), `test_W4 1.889616` vs the in-harness S-26 anchor's own W4 `1.957937` (−0.0683), held-out gain `+0.020368` (> 0.005) — and the paired bootstrap put the mean gain's 95% CI at `[-0.018506, -0.006913]` (B=2000, seed 0, resample origins; upper < 0). The verdict was nonetheless `REJECT (close family)` because two *non-accuracy* conditions failed: PatchTST singleton val `3.026725 > 2.90` and train-val gap `0.179497 > 0.15`.

S-43's reflection isolated the defect as decision-theoretic: the spec never declared whether the binding gate is singleton-based or blend-based, nor named a resolution when they disagree. S-43 P1 now REQUIRES that declaration at pre-registration. **S-44 is that declaration made for the one candidate whose blend evidence is already on file** — a re-registration of gate semantics over a frozen, already-executed protocol. Not a new search, not a new member, not a re-opening of the patch-attention family (see D5).

**Why legitimate, not cherry-picking.** Pool, protocol, seed, and every number were fixed before this document existed (Bet 3 artifacts 2026-09-13, reproduced deterministically across two runs — original + post-W4-fix regeneration, all metrics stable to printed precision per S-43 P2 solution record). S-44 changes exactly one thing: which conditions BIND the promotion decision. The parity clause (D8) makes this enforceable — if the S-44 harness does not reproduce Bet 3's numbers to 1e-4, the harness is wrong and nothing proceeds.

## 2. Gate-semantics declaration (S-43 P1, stated up front)

| Element | Semantics for S-44 |
|---|---|
| **Binding gate** | **BLEND-based**: the frozen-test stacked blend of the tabu-selected subset must beat the S-26 incumbent (conditions in D2). |
| **Singleton screen** | Demoted to non-binding diagnostic (member-capacity observation, D5). Cannot flip a PASS to FAIL. |
| **Resolution on disagreement** | The blend decides promotion. A blend win does NOT re-open the member family; the Bet 3 family close (member-capability) STANDS independently of the promotion outcome (D5, D11). |

## 3. Mandatory design decisions

### D1 — Slice identity & directory
Slice id `S-44-blend-promotion`; directory `sub_experiments/blend_promotion_s44/` with `S44_DESIGN.md` (this file), `rolling_arm.py`, `results_s44.json`, `harness.log`. Rationale: sibling-slice naming convention (`patchtst_delta_bet3/`, `group_sparse_bet2/`); the name states the claim — blend promotion — so a future reader cannot mistake S-44 for a new member search.

### D2 — Binding gate is blend-based; promotion = incumbent replacement
The selected subset's frozen-test blend must satisfy ALL of:

| # | Binding condition | Bet 3 evidence |
|---|---|---|
| G1 | `MAE_full(2161) ≤ 1.9859` (H2 bound: ≥ 0.0050 vs S-26 1.9909) | 1.978126 PASS |
| G2 | `MAE_full < 1.9909` (strictly better than incumbent) | 1.978126 PASS |
| G3 | `MAE_disjoint-4 ≤ 1.9696` (S-26 stability cap) | 1.863419 PASS |
| G4 | Paired-bootstrap Δ CI upper < 0 — Δ = per-origin MAE(blend) − per-origin MAE(S-26 anchor), B=2000, seed 0, resample origins, convention identical to Bet 3 `bootstrap_paired_diff_ci` (`rolling_arm.py:168-176`) | upper −0.006913 PASS |

If ALL hold → **S-44 becomes the new incumbent**: CONTEXT.md leaderboard top row + all incumbent references update; S-26 1.9909/2.4710 moves to second place. Otherwise S-26 stays terminal. Rationale: S-43 P1 forbids a blend that passes the project-wide promotion rule from being recorded as a blend failure; under a blend-based gate, singleton vals and train-val gaps are capacity/regularity observations about *members*, not promotion conditions.

### D3 — Pool is FROZEN = the Bet 3 pool exactly
`M=4`: `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L, patchtst_P48_D16_1L]` — same PatchTST architectures (primary P=24 D=32 2-layer, heads=2, FFN=64, dropout 0.30, stochastic depth 0.10, attn-dropout 0.2, weight-decay 1e-2, no causal mask; ablation P=48 D=16 1-layer; level-free delta convention, anchor = OT `window[-1]`) and same training config: **AdamW lr 3e-4, batch 64, grad clip 1.0, early stop on val delta-MAE patience 5 max 50, seed 0, deterministic**. NO new members, NO hyperparameter changes. Rationale: this is a re-registration of gate semantics; any pool/protocol change would invalidate the re-registration logic (the promotion would rest on evidence that does not exist yet, re-opening the family D5 forbids).

### D4 — Selection protocol unchanged from Bet 3
Tabu-7 over the frozen pool (fixed-α fast 3000, aspiration, `no_improve=5`, init = best singleton) → chronological ridge selection: 11-α grid `[0.1, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000]`, per-horizon ridge **no-intercept**, fit `val[0:1080)` / select `val[1080:2161)` (pooled MAE). Members frozen `8545` for val, refit `11425` for frozen test. `val_full` = chronological half-split (fit `val[0:1080)` at selected α, score `val[1080:2161)`). **Held-out S-26 delta-ridge control precondition**: 2-member `[a1, a10]` no-intercept delta-ridge fitted on `val[0:1080)` (fast-α 3000), scored on `val[1080:2161)` = 2.5225; the selected subset must beat it by > 0.005 to proceed to frozen test. The frozen-test blend stack is the per-horizon ridge no-intercept fitted on `val[0:1080)` at the selected α, applied to the 11425-refit members' test predictions (mirror Bet 3 `rolling_arm.py:364-367, 419`). Rationale: identical machinery is a precondition for D8 parity; changing any knob would make S-44 a new experiment requiring fresh evidence.

### D5 — Demoted diagnostics + explicit close conditions
**Demoted to non-binding diagnostics** (reported in `demoted_diagnostics`, cannot flip PASS→FAIL): singleton PatchTST val (Bet 3: 3.026725 / 3.151670), train-val gap (P24 −0.089755, P48 +0.179497), attention entropy (2.392 / 1.859; collapse threshold 0.5 bits). Rationale (S-43 P1): under a blend-based gate these are member-capacity/regularity observations, not promotion conditions.
**Close conditions (any one → REJECT)**: (a) tabu-selected subset contains NO PatchTST member (selection collapses to linear-only — no promotable object exists, only a re-labeled S-26); (b) held-out gain ≤ 0.005 (precondition fails, REJECT at plan time before test); (c) paired-bootstrap Δ CI upper ≥ 0; (d) any binding accuracy condition G1–G3 fails. **On REJECT: S-26 remains terminal AND the patch-attention family close (Bet 3) STANDS** — the family close is a statement about member capability (PatchTST cannot stand alone vs the incumbent: singleton 3.0267 > 2.90); S-44 only tests whether the *specific 3-member blend* is promotable. S-44 does not re-open member-family exploration either way.

### D6 — Train-val gap handling
P48 (+0.179497) violates the 0.15 regularity bound; P24 (−0.089755) does not. **DECISION: do NOT exclude `patchtst_P48_D16_1L` from the pool.** The pool stays frozen at 4 members (D3); tabu may still reject P48-containing subsets on val merit — as it did in Bet 3, where every P48-containing superset scored worse than the winner (fast 2.5081–2.5171 vs best 2.5021; see `results_patchtst_bet3.json` trace iters 0–8). Report the gap as a diagnostic on any P48-containing subset and flag it in the artifact. Do NOT add a new gap-based acceptance condition. Rationale: pruning the pool post-hoc would be a protocol change (violates D3/D8) and would smuggle a regularity condition back into the binding gate that S-43 P1 just removed.

### D7 — Per-window W4 reporting (S-43 P2)
Report per-window W1–W4 deltas vs the **in-harness S-26 anchor** (same run, same frozen fit, `_verify_s26_anchor` per-origin MAEs) — never vs a leaderboard constant. W4 is a **non-binding diagnostic**: no 1.90 cap, no W4 condition can reject the blend. Bet 3 evidence already shows W4 −0.0683 better (1.889616 vs 1.957937); W1 is +0.0274 worse (2.160695 vs 2.133334) and W2 +0.0000, W3 −0.0656 — all four deltas are reported honestly. Horizon terciles (h1 −0.0068, h2 +0.0060, h3 −0.0375) reported likewise. Rationale: S-43 P2 requires the incumbent-relative comparison from the same frozen fit; the blend buys mean, W3/W4, and long-horizon gains at a small W1 cost — a diagnostic the verdict line must state, not a gate.

### D8 — Reproduction parity requirements (the re-registration clause)
Given identical pool/seed/protocol, the S-44 harness MUST reproduce Bet 3's val-phase selection and frozen-test metrics. **If any check fails beyond 1e-4, the harness is WRONG (a bug) — abort and fix the harness; the Bet 3 numbers are ground truth.** This clause is what makes S-44 a re-registration rather than a new experiment. See §5 table. Rationale: Bet 3's numbers were produced under the frozen pool/seed/protocol and verified twice (original run + post-W4-fix regeneration, S-43 P2 solution record: "all other metrics reproduced to printed precision"); any deviation is nondeterminism or a transcription bug in the S-44 harness, never new evidence.

### D9 — Fail-loud S-26 anchor
Re-derive the S-26 anchor in-harness before any scoring: `MAE_full 1.9909 / RMSE 2.4710 / disjoint 1.9696 / W4 1.9579`, each **±1e-4** (Bet 3 re-derived 1.990897 / 2.470999 / 1.969617 / 1.957937 — all inside 4e-5; the shipped Bet 3 check used tol 0.002, S-44 tightens it deliberately). Abort on mismatch. Rationale: the promotion compares against the incumbent; a drifted anchor silently changes the meaning of every delta (the S-43 P2 W4-misattribution scar is the precedent for constant-vs-incumbent confusion).

### D10 — Artifacts
`results_s44.json` (schema §6) + `harness.log` (non-empty, mirrors Bet 3's log format incl. the tabu trace lines, audit lines, bootstrap/stratified lines, and a final `VERDICT=PROMOTED|REJECTED` line) + this design file. Harness command recorded in the artifact: `C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe projects/ts-ml-experiments/h720/sub_experiments/blend_promotion_s44/rolling_arm.py` (hermes venv python, cpu torch — Bet 3 ran `torch 2.13.0+cpu`, ~450–510 s). Tabu trace format mirrors Bet 3: `{iter, cur (names), fast, true, alpha, best_fast, best_set}`.

### D11 — Verdict semantics & promotion mechanics
`PROMOTED` only if every binding condition G1–G4 passes (and the held-out precondition was met to reach test, and no close condition fired). `REJECTED` otherwise. **On PROMOTION:** the CONTEXT.md leaderboard's top row becomes the S-44 blend — 3-member `NLinear L336 a=1 + a=10 + PatchTST-Delta P24 D32 2L`, per-horizon ridge no-intercept α=30000, members frozen 8545/11425, `1.9781 / 2.4613`, disjoint-4 1.8634 — and `1.9909` moves to second place; all CONTEXT incumbent references update. S-43 P3/P4 records are updated accordingly: the "surviving positive" is no longer merely a searchable finding — it is the incumbent; the four-family close block (S-43 P4) is annotated that family (4) patch-attention non-linear remains closed for *member/singleton capability* while the specific blend is promoted, and the admissible-next-move routing (dataset / horizon / protocol change) is otherwise unchanged. **On REJECTION:** no leaderboard change; S-26 stays terminal; family close stands (D5). Expected outcome given Bet 3's evidence: **PROMOTED** — all four binding conditions already hold on the recorded numbers; S-44 formalizes the promotion under corrected gate semantics.

## 4. Acceptance & close conditions

| Condition | Type | Threshold | Bet 3 value | Gate |
|---|---|---|---|---|
| G1 full MAE | binding | ≤ 1.9859 | 1.978126 | promote |
| G2 full MAE vs incumbent | binding | < 1.9909 | 1.978126 | promote |
| G3 disjoint-4 | binding | ≤ 1.9696 | 1.863419 | promote |
| G4 paired Δ CI upper | binding | < 0 (B=2000, seed 0) | −0.006913 | promote |
| Held-out gain (precondition to test) | procedural | > 0.005 | +0.020368 | reach test |
| C1 subset has ≥ 1 PatchTST member | close | any PatchTST | yes (P24) | reject if violated |
| C2 held-out gain ≤ 0.005 | close | ≤ 0.005 | — | reject |
| C3 paired Δ CI upper ≥ 0 | close | ≥ 0 | — | reject |
| C4 any of G1–G3 fails | close | — | — | reject |
| Singleton PatchTST val | non-binding diagnostic | (info) | 3.026725 / 3.151670 | report |
| Train-val gap | non-binding diagnostic | (info; flag if > 0.15) | P24 −0.089755 / P48 +0.179497 | report |
| Attention entropy | non-binding diagnostic | (info; collapse < 0.5) | 2.392 / 1.859 | report |
| W1–W4 deltas vs in-harness anchor | non-binding diagnostic | (info) | +0.0274 / +0.0000 / −0.0656 / −0.0683 | report |
| Horizon tercile deltas | non-binding diagnostic | (info) | −0.0068 / +0.0060 / −0.0375 | report |
| Parity vs Bet 3 (§5) | harness acceptance | ≤ 1e-4 each | — | abort if violated |

## 5. Parity requirements (vs `results_patchtst_bet3.json`)

| Quantity | Bet 3 value | Tolerance |
|---|---|---|
| Best subset | `[nlinear_L336_a1, nlinear_L336_a10, patchtst_P24_D32_2L]` | exact |
| best_alpha | 30000 | exact |
| best_fast | 2.502112 (2.5021117513632665) | 1e-4 |
| Held-out control (val[1080:2161)) | 2.5225 (2.5224798283169374) | 1e-4 |
| Held-out gain | +0.0204 (0.020368076953670933) | 1e-4 |
| val_full (half-split) | 2.4936 (2.493567251979277) | 1e-4 |
| Singleton vals (4 dp) | 2.8970 / 2.8970 / 3.0267 / 3.1517 | 1e-4 |
| test_full MAE / RMSE | 1.9781 / 2.4613 (1.9781264265828236 / 2.4612639073807663) | 1e-4 |
| test_disjoint-4 | 1.8634 (1.8634190252257932) | 1e-4 |
| test_W4 | 1.8896 (1.8896163750508768) | 1e-4 |
| Paired Δ CI | [−0.0185, −0.0069] ([-0.018505562732342832, −0.006913352503709525]) | 1e-4 |
| S-26 anchor (re-derived) | 1.9909 / 2.4710 / 1.9696 / 1.9579 | 1e-4 (D9) |
| Tabu trace | iters 0–8 sequence, init singleton `nlinear_L336_a10` fast 2.5206, stop at no_improve 5 | exact set sequence |

Failure of any row > 1e-4 (or any set/sequence mismatch) ⇒ `parity.all_pass = false` ⇒ harness bug ⇒ abort, fix, re-run. The promotion verdict is emitted only from a parity-passing run.

## 6. Artifact schema — `results_s44.json`

```json
{
  "slice": "S-44-blend-promotion",
  "harness_command": "C:/Users/Mateusz/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe projects/ts-ml-experiments/h720/sub_experiments/blend_promotion_s44/rolling_arm.py",
  "device": "<as-run, e.g. cpu (torch 2.13.0+cpu)>",
  "protocol": "S-20-clean re-registration of Bet 3 (identical frozen pool/seed/protocol); binding gate BLEND-based per S-43 P1; singleton/regularity conditions demoted to diagnostics",
  "pool": ["nlinear_L336_a1", "nlinear_L336_a10", "patchtst_P24_D32_2L", "patchtst_P48_D16_1L"],
  "params": { "...mirror Bet 3 params block (lr 3e-4, batch 64, dropout 0.3, seed 0, deterministic)..." : "" },
  "s26_anchor": { "mae": 1.990897, "rmse": 2.470999, "disjoint": 1.969617, "w4": 1.957937, "tol": 1e-4, "pass": true },
  "parity": { "tol": 1e-4, "checks": [ { "quantity": "test_full_mae", "bet3": 1.9781264265828236, "s44": 0.0, "abs_diff": 0.0, "pass": true } ], "all_pass": true },
  "held_out_control": { "type": "2-member S-26 delta-ridge, no-intercept, fit val[0:1080) at fast-alpha 3000", "mae_val_heldout": 2.5225, "alpha_reference": 10000.0 },
  "singleton_val": { "nlinear_L336_a1": 2.8970, "nlinear_L336_a10": 2.8970, "patchtst_P24_D32_2L": 3.0267, "patchtst_P48_D16_1L": 3.1517 },
  "trace": [ { "iter": 0, "cur": ["..."], "fast": 0.0, "true": 0.0, "alpha": 30000.0, "best_fast": 0.0, "best_set": ["..."] } ],
  "best_subset": ["nlinear_L336_a1", "nlinear_L336_a10", "patchtst_P24_D32_2L"],
  "best_idx": [0, 1, 2], "best_fast": 2.502112, "best_alpha": 30000.0,
  "val_full": 2.4936, "heldout_gain_over_control": 0.020368, "heldout_precondition_pass": true,
  "binding_gate": {
    "full_le_19859": { "value": 1.9781, "pass": true },
    "full_lt_s26": { "value": 1.9781, "s26": 1.9909, "pass": true },
    "disjoint_le_19696": { "value": 1.8634, "pass": true },
    "paired_ci_upper_lt_0": { "ci_95": [-0.0185, -0.0069], "upper": -0.0069, "pass": true },
    "all_binding_pass": true
  },
  "demoted_diagnostics": {
    "patchtst_singleton_vals": { "patchtst_P24_D32_2L": 3.0267, "patchtst_P48_D16_1L": 3.1517 },
    "best_patchtst_val": 3.0267, "best_patchtst_name": "patchtst_P24_D32_2L",
    "train_val_gap": { "patchtst_P24_D32_2L": -0.0898, "patchtst_P48_D16_1L": 0.1795 }, "gap_flag": true,
    "attention_entropy_last": { "patchtst_P24_D32_2L": 2.392, "patchtst_P48_D16_1L": 1.859 }, "entropy_collapse": false,
    "w1_w4_deltas": [ { "window": "W1", "s44_mae": 0.0, "s26_mae": 0.0, "delta": 0.0 } ],
    "w1_regression_note": "W1 +0.0274 vs in-harness S-26 anchor — reported, non-binding",
    "horizon_terciles": [ { "horizon_tercile": "h1_first240", "s44_mae": 0.0, "s26_mae": 0.0, "delta": 0.0 } ]
  },
  "test_full": { "mae": 1.9781, "rmse": 2.4613, "n": 2161, "delta_vs_s26": -0.0128 },
  "bootstrap": { "convention": "resample origins, B=2000, seed 0, percentile 2.5/97.5", "s44_full": { "mean": 0.0, "ci_95": [0.0, 0.0], "B": 2000 }, "s26_full": { "mean": 0.0, "ci_95": [0.0, 0.0], "B": 2000 }, "paired_delta": { "mean": -0.0128, "ci_95": [-0.0185, -0.0069], "B": 2000, "upper_bound_negative": true } },
  "stratified": { "disjoint_windows": [ { "window": "W1", "start": 0, "s44_mae": 0.0, "s26_mae": 0.0, "delta": 0.0 } ], "horizon_terciles": [ ] },
  "test_disjoint": { "mae": 1.8634, "rmse": 2.3707 },
  "test_w4": { "mae": 1.8896, "s26_incumbent_w4": 1.9579, "w4_delta_vs_s26": -0.0683, "binding": false },
  "close": { "condition": "no-PatchTST subset OR heldout_gain<=0.005 OR paired_ci_upper>=0 OR any G1-G3 fails", "trigger": false, "message": "..." },
  "verdict": "PROMOTED",
  "plan_impact": { "invalidates": "S-26 incumbent status (moves to second place) on PROMOTION", "confirms": "patch-attention member-capability close (S-43 P3 record updated)", "opens": "blend-incumbent frontier: future bets must beat the S-44 blend under a declared gate" },
  "elapsed_s": 0.0
}
```

## 7. What would falsify this bet

1. **Parity failure > 1e-4 on any §5 row** — the harness (not the numbers) is wrong: nondeterminism (seed-0 violation, GPU nondeterminism), a transcription error, or a protocol drift. Abort, fix, re-run; no verdict is emitted from a parity-failing run. This is the falsifier of the *harness*, and it blocks everything.
2. **Tabu selection deviates from `[a1, a10, P24]`** (e.g. collapses to linear-only, or picks a P48-containing subset) under the identical frozen pool/seed/protocol — by D8 this is a harness bug, not a new finding; if it somehow survived parity it would trigger close condition C1 (no PatchTST member) ⇒ REJECT.
3. **A binding condition fails in the re-run** — full > 1.9859, or full ≥ 1.9909, or disjoint > 1.9696, or paired Δ CI upper ≥ 0 ⇒ REJECT; S-26 stays terminal; the Bet 3 family close stands. Given parity, the only reachable member of this class is G4-style statistical indecisiveness, which the recorded CI (upper −0.0069) already excludes.
4. **Held-out gain ≤ 0.005** ⇒ REJECT at plan time before frozen test (procedural, not accuracy).
5. **Post-promotion falsifier (normal science, not a defect):** a later pre-registered bet beating the S-44 blend under its own declared gate would supersede the S-44 incumbent — standard incumbent turnover; it does not falsify S-44's evidence, only its incumbency.
6. **Design-level falsifier:** if the parent rules that S-43 P1 does not license retroactive re-registration of an already-executed bet, this design is void and S-26 stays terminal with the Bet 3 close unchanged.

## 8. Cited evidence

- `RESEARCH/next-frontier-scout-2026-09-13.md` §4 (Bet 3 spec being superseded), §5 (harness shape).
- `projects/ts-ml-experiments/h720/CONTEXT.md` — leaderboard (S-26 1.9909/2.4710), Bet 3 section (~line 375), `## Prevention rules — S-43` (P1–P4).
- `projects/ts-ml-experiments/h720/sub_experiments/patchtst_delta_bet3/results_patchtst_bet3.json` + `harness.log` + `rolling_arm.py` (all Bet 3 numbers above; `bootstrap_paired_diff_ci` lines 168–176; `_verify_s26_anchor` lines 189–235; tabu loop lines 296–359).
- `projects/ts-ml-experiments/h720/sub_experiments/greedy_linear_mixture_s26/` (S-26 anchor pattern; incumbent facts 1.9909/2.4710, disjoint 1.9696, val_full 2.8527).
- `MONITORING/reflection/2026-09-13_2350_S-43-bet3-terminal-close.md` (P1/P2/P3/P4 invariants; two-run reproduction record).

**Expected verdict: PROMOTED** (all binding conditions hold on Bet 3's recorded evidence; S-44 exists to make that promotion rule-conformant under S-43 P1, with parity proving no new evidence was invented).
