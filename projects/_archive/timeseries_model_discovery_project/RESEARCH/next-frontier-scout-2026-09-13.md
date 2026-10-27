---
type: Concept
title: next-frontier-scout-2026-09-13
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:31Z }
---

# Next Frontier Scout — h720 ETTh1 H=720

**Date:** 2026-09-13
**Scout:** frontier-scout
**Incumbent (terminal):** S-26 Ridge mixture — 2-member `NLinear L336 a=1 + a=10`, per-horizon stack `α=10000`, no-intercept — **1.9909 MAE / 2.4710 RMSE** (rolling full 2161 origins, disjoint-4 1.9696) — `./CONTEXT.md:4` `sub_experiments/spectral_omega_gate/results_tsfm_phase2.json:38-43`
**Frontier status:** Univariate linear family on OT alone **SATURATED** (H2 Dyadic Wavelet + successors closed by stop rule; §H2 `CONTEXT.md:152-160`). Omega-gated **zero-shot** TSFM Phase 2 **REJECTED** on sampled weighted estimate 2.1218 ≥ 1.9859 (C-bucket anti-selective), `PHASE2_DECISION.md:20-26` `results_tsfm_phase2.json:44-52,54-57`. Six post-S-26 probes S-39..S-41 likewise REJECTED (`ensemble_linear_frontier_reflection_2026-09-13.md:10-14,49-70`).
**Graph-aware context:** `python brains/ts_brain/ask.py "h720 ETTh1"` + `python brains/reflection_brain/ask.py "h720"` executed (fallback per assignment — `omp agent --cwd workspaces/ts-brain context` unavailable in this Windows shell). Surfaced scars referenced below as `ts_brain:*` / `reflection_brain:*`. No `omp` relay required.
**Sources read (and cited):** `./CONTEXT.md` · `sub_experiments/spectral_omega_gate/PHASE2_DECISION.md` · `sub_experiments/spectral_omega_gate/results_tsfm_phase2.json` · `RESEARCH/ensemble_linear_frontier_reflection_2026-09-13.md` · `RESEARCH/2026-09-12_omega-h720-integration.md` · `RESEARCH/next-frontier-scout-2026-09-12.md` · `brains/ts_brain` + `brains/reflection_brain` ask.py

---

## 1. Why nothing in the exhausted family can be proposed

Per `CONTEXT.md:152-160` H2 stop rule **fired** (`full ≥ 1.9859 OR disjoint-4 > 1.9696 → saturated`): wavelet DWT is a unitary rotation of the 336-dim NLinear span — only subband-dependent penalties were novel and moved held-out val `< 0.004` (`reflection_brain 2026-09-12_0435_S-h2-wavelet-terminal-close P1/P3`). All of the following are **refuted — MUST NOT propose** (ask.py + CONTEXT + reflection):

| Refuted class | Evidence | Scar / guard |
|---|---|---|
| Any linear transform of same `L=336` window (DWT, rFFT/FITS, any unitary rotation) | H2 best 1.9906 (−0.0003 vs S-26), singleton wavelet 2.0566 vs NLinear 2.0571 | `reflection P1` rotation-invariance no-op |
| Non-linear readout on the same saturated basis (RF/RFF on deltas, ELMTree alone, wavelet-KNN) | S-35 `2.0112 (+0.0203)`, S-41 `2.3589`, H2-KNN `held-out 2.60–2.65` never enters best set | `reflection P3` non-linearity on saturated basis inherits saturation |
| Dense / naive-sparse multivariate linear over 7 channels (2352-dim) | S-24 `2.0539`, S-34 `2.0539`, S-37 tabu collapse to singleton `2.0244` | cross-channel val correlations do not transfer |
| Decision-tree / leaf-linear regime heads (constant or linear leaves, level or level-free) | S-21 `8.57`, S-21b `+0.23, held-out 3.04/3.19` | `reflection 2026-09-08_1200 P1/P2` level-memorization; `ts_brain 04_subexperiment_findings_leaderboard` S-21 recurrence |
| Volatility / KNN-disagreement / trend gating over S-26 pair (continuous or tercile) | S-23 `2.0114 (+0.0134)`, S-36 `2.4724 (+0.4815, disjoint 2.5975)`, S-38 `full 1.9748 but disjoint 2.0914 (>1.9696)` | S-36 val→test vol shift `−0.48 to −0.90σ`; `ts_brain multi_vari_*` S-36 § |
| Horizon-band α, per-horizon intercept, horizon-weighted ridge, window-scale / calendar-phase scalars, RevIN L=512 | S-27 `−0.0045 < 0.005`, S-28 `5.91 catastrophic`, S-29 `disjoint 1.9852`, S-30 `delta 0.0000`, S-31 `2.0036`, S-32 `1.9928` | — |
| **Omega-gated zero-shot TSFM** (`Ω₃₃₆>0.5 → Chronos-Bolt Base`) | Sampled weighted `2.1218 (−0.1309 vs S-26)`, bucket C `2.2741` worst where gate fires; 95% CI `[1.9733,2.2847]` straddles threshold from above; disjoint-4 `1.8739` PROMOTED but **overridden** by sampled | `PHASE2_DECISION.md:4` `results_tsfm_phase2.json:56-58` |

In short: **no univariate-linear basis/shrinkage variant, no same-window non-linear readout, no dense multivariate linear, no learned univariate scalar gate, and no zero-shot TSFM gate** may be re-proposed. The next bets must be (a) **multivariate with proper sparsity/low-rank regularization**, (b) **non-linear with an orthogonal representation** (not a rotation), or (c) a **protocol change** (trainable adaptation, not zero-shot). The three bets below satisfy that.

---

## 2. Bet 1 — PEFT Fine-Tuned TSFM + S-26 Ridge Stack [PRIMARY, Protocol Change]

### Concept
Phase 2 proved **zero-shot Chronos-Bolt is anti-selective** on ETTh1 H=720: C-regime (Ω>0.5, 53.9% mass `results_tsfm_phase2.json:65`) where the gate fires has the **worst** bucket MAE `2.2741` vs B `1.9109` / A `2.1993` (`PHASE2_DECISION.md:56`). `PHASE2_DECISION.md:5` explicitly licenses the successor: *"Any follow-up must propose a different gate, a **fine-tuned TSFM**, or a non-zero-shot adaptation; re-running disjoint-4 or sampled with the same Chronos-Bolt Base + 0.5 threshold will not change the verdict."* This bet executes that: **parameter-efficient fine-tuning (PEFT/LoRA) on ETTh1** under S-20-clean, then a **learned** per-horizon ridge blend with S-26 (no hard Ω gate).

Why not refuted: no prior S-* fine-tuned a foundation model on ETTh1; Phase 2 scar is **zero-shot only**. Uses frozen S-26 members as anchors; the TSFM is the only trainable member and its train/val boundary is S-20-clean compliant.

### Member pool
- `M=3`: `NLinear L336 a=1`, `NLinear L336 a=10` (S-26 pair, L2-penalised linear — `methods/neural_models.py`), plus `ChronosBolt-LoRA` — Chronos-Bolt Base (pinned hash, e.g. `amazon/chronos-bolt-base@<sha>`) with LoRA adapters `r=8, α=16, dropout=0.1` on attention q/v projections only; base weights frozen, ~0.3% trainable params.
- TSFM training data: **history-only OT windows** `L=336` (primary; ablate `L=720` as sensitivity, one extra arm). Targets `H=720`. No exogenous channels, no future leak — same `data.py` `ProtocolData` containment as `BaseForecaster.history_`.
- Optimizer: AdamW `lr=1e-4`, `weight_decay=0.01`, batch 32, early stopping on **frozen val MAE** (train-8545 fit / val-2880 rolling, chronological split — see Protocol), patience 5 epochs, max 50 epochs. Quantile/MAE loss consistent with rolling MAE selector.

### Gate / protocol
- **S-20-clean adapted for a trainable member:** Phase-1 (val search): fit S-26 pair on `train 8545` + fine-tune TSFM-LoRA on `train 8545` (val 2880 untouched for early stopping only). Phase-2 (selection): per-horizon ridge **no-intercept** stack over `M=3` predictions, `α` grid `[0.1,1,10,100,300,1000,3000,10000,30000]` (11-grid per S-26), fitted on `val[0:1080)` and selected on `val[1080:2161)` (chronological 1080/1081, pooled MAE) — identical to H2/S-36 protocol, so the ridge selector's sample budget (~1080 origins) matches S-26.
- Frozen test: refit S-26 pair on `11425` + **re-fine-tune** TSFM-LoRA on `11425` (or fine-tune once on 11425 after hyper-selection; document choice — either is S-20-clean as long as val and test are never mixed). Score `full 2161` (primary) + `disjoint-4` (diagnostic) + `W4` hardness. Ω stratification reported as **diagnostic only** (no hard gate). TSFM inference cost logged (LoRA adds ~0 params at inference after merge).
- Guards carried forward: `|Ω̄_test−Ω̄_val|/σ_val < 0.5` (already `0.3832` PASS `results_tsfm_phase2.json:26`), `ρ(Ω₃₃₆,S-26 MAE)` negative `p<0.01` re-verified, `P(Ω>0.5)≥0.10` reported — but they are **not** promotion gates for this bet. The ridge blend absorbs regime signal continuously.

### Falsifiable acceptance criteria (all must hold vs S-26 1.9909/1.9696)
- **Primary:** `MAE_full(2161, gated ridge) ≤ 1.9859` (≥ 0.0050 improvement over S-26 `1.9909`, H2 bound) **AND** `≤ S-26` by any margin.
- **Stability:** `MAE_disjoint-4 ≤ 1.9696` (S-26 disjoint cap; `results_tsfm_phase2.json:38-42`).
- **Statistical:** bootstrap `B=2000` 95% CI on `MAE_full` has **upper < 1.9909** (or point ≤1.9859 with CI lower < threshold — sampled CI `[1.9733,2.2847]` is the failure template to beat).
- **Non-degeneracy:** per-horizon ridge weight mass on TSFM `mean_h |w_TSFm(h)| > 0.02` and `std_h(w_TSFm) > 0.01` (gate not collapsed to S-26 pair, which S-36 showed collapses to delta `0.0000` on pure pair).

### Explicit close condition
- **If** after PEFT with early stopping, the TSFM-LoRA singleton val MAE `> 2.8527` (S-26 val_full `results_tsfm_phase2.json` / `CONTEXT.md:102` `2.8527`) **or** frozen-test `MAE_full ≥ 1.9909` **or** `disjoint-4 > 1.9696` despite val selection of `α` in interior (not edge `0.1/30000`), then **REJECT and close the foundation-model adaptation family for ETTh1 H=720 under S-20-clean**: *"PEFT-adapted Chronos-Bolt does not transfer to H=720 even with ETTh1 gradient; Ω-anti-selectivity is not cured by LoRA at this data budget (8545/11425 rows)."* Document singleton, 3-member pooled, and val→test transfer delta. No further TSFM fine-tuning variants (full-FT, larger r, different base) without a new pre-registration.

### Why this is the top bet
- Only direction explicitly **opened** by Phase 2's own decision (`PHASE2_DECISION.md:5`).
- Retains S-26's heavy-shrinkage benefit (`α=10000`) while adding capacity where S-26 is saturated — long-horizon spectral peaks that univariate linear cannot capture.
- LoRA's ~0.3% trainable params respects the `~1080`-origin ridge budget that killed S-24/S-34 (2352-dim dense) — regularization is architectural, not post-hoc.
- Cost: 1 fine-tune (~minutes on GPU) + 2161×720 scoring (same as any S-*); no per-origin TSFM API latency.

---

## 3. Bet 2 — Group-Sparse Multivariate NLinear with Patch Embedding [Multivariate with Proper Regularization]

### Concept
S-34/S-37 failed because a 7-channel × L=336 flat NLinear is `7×336=2352` linear weights per horizon step fitted on `~1080` held-out origins — over-parameterized by ~2×, so val correlations are spurious and transfer flips sign (`S-37 tabu collapse to singleton 2.0244 (+0.0335)` `ensemble…:13`). The fix is **structured sparsity + dimensionality reduction**, not more members: **patch embedding** (temporal downsampling) + **group-lasso channel selection**.

Why not refuted: no prior S-* used patch embedding or group-lasso channel sparsity. S-37 used naïve channel dropout `p=0.3` (uniform masking, no sparsity penalty) and kept full 336-dim per channel — still 2352-dim. This bet is orthogonal by construction (implements `H2 P1` pre-condition: must show held-out gain from the **penalty structure alone** before delegation).

### Member pool
- **Base univariate anchors (2):** `NLinear L336 a=1`, `NLinear L336 a=10` (S-26 — guarantees no regression vs incumbent even if multivariate is rejected by selection).
- **Patch embedding:** per-channel, non-overlapping patches `P=24` (hourly → daily patches; `L=336 → 14 patches`), each patch mean-pooled (or max-pooled — ablation one arm) then standardized with **train-only** μ/σ (S-04 norm discipline). This is **not** a unitary rotation (unlike DWT/rFFT): it is a learned-free downsampling `336 → 14` that reduces per-channel dim by `24×`.
- **Multivariate members (2–3):** `GroupSparseNLinear` operating on the patch matrix `X ∈ ℝ^{7×14}` (98 features per origin, not 2352). Formulation per horizon step `h`:
  ```
  ŷ_h = Σ_c Σ_p w_{c,p,h} · x_{c,p}    with group-lasso penalty λ Σ_c ||w_{c,:,h}||₂
  ```
  where groups are channels `c ∈ {OT,HUFL,HULL,MUFL,MULL,LUFL,LULL}`. OT group is **unpenalized** (or λ_OT = 0.1·λ) so the model can always fall back to univariate. Two λ arms: `λ ∈ {0.5, 2.0}` × patch `P ∈ {24, 48}` (total 4 candidates; tabu selects among them — cheap). Ridge fallback `a=10` inside groups for numerical stability. Trained with `sklearn.linear_model.MultiTaskElasticNet`-style grouped penalty or `group_lasso` package — deterministic, closed-form per step via block-coordinate descent, no RNG.
- Effective params: `98 × 720 = 70k` weights (+ group shrinkage) vs `2352 × 720 = 1.69M` in S-34 — `24×` reduction, now under the `~1080`-origin budget.

### Gate / protocol
- **S-20-clean, S-25-style tabu search over mixed pool:** pool `M=6` (2 univariate + up to 4 group-sparse patch members). Tabu-7 search, fixed-α fast score `α=3000`, aspiration, `no_improve=5`. Members frozen `8545` for val, refit `11425` for test. Per-horizon ridge no-intercept over selected subset (same 11-α grid). No Ω gate. Chronological `val[0:1080)` fit / `val[1080:2161)` select, pooled MAE selector; `disjoint-4` diagnostic only.
- **Transfer guard (S-37 lesson):** reject any candidate whose frozen-test MAE exceeds its `val_full` MAE by `> 0.15` (detects val-local cross-channel overfit). `val_full` here is the ridge-refit on all 2161 val origins at selected `α`.
- **Diagnostics:** report selected channel groups (non-zero `||w_{c}||₂`), effective sparsity `(#active channels)/7`, and `Δ val→test` per channel group.

### Falsifiable acceptance criteria (all must hold)
- **Primary:** `MAE_full ≤ 1.9859` and `< 1.9909` (≥0.0050 vs S-26).
- **Stability:** `MAE_disjoint-4 ≤ 1.9696`.
- **Sparsity sanity:** `1 ≤ #active_exo_channels ≤ 3` (OT always active; 0 exo = univariate fallback, 6 exo = dense failure replay) and `val_full` beats S-26 `val 2.8527` by `> 0.005` (penalty-structure gain must appear on held-out val — `H2 P1` precondition).
- **Transfer:** `MAE_full − MAE_val_full < 0.15` (no S-24/S-34-style flip).

### Explicit close condition
- **If** tabu search again collapses to the univariate pair `[L336_a1, L336_a10]` (or any subset with `0` active exo channels) **and** the best multivariate singleton val `> 2.85` (i.e. worse than S-26 val), then **REJECT and close the linear multivariate family for ETTh1 H=720 under S-20-clean**: *"Group-sparse patch-linear multivariate members add no orthogonal signal beyond the L336 OT linear span at this horizon and data budget; cross-channel correlations are val-local regardless of sparsity structure."* Document channel-group norms and patch-P sensitivity. No further linear multivariate members without a non-linear cross-channel interaction.

---

## 4. Bet 3 — Level-Free PatchTST-Style Non-Linear Encoder on Orthogonal Patches [Non-Linear with Orthogonal Representation]

### Concept
H2 P3 forbids *"non-linearity on a saturated basis"* — S-35's RF on 336-dim deltas (`2.0112`) and S-41's RFF (`2.3589`) failed because they kept the **same 336-dim window** as NLinear. This bet changes the **representation**: **patch-tokenized, level-free deltas** fed to a **shallow Transformer encoder** (PatchTST-style) — a non-equivalent feature map with temporal downsampling and inter-patch attention, not a rotation.

Why not refuted: no prior S-* used patch tokenization or attention. S-10 MultiRateELM used MaxPool views + ELM mean ensemble (`2.2744`) — pooling without attention and with ELM readout, not a Transformer. S-36/S-38 gating used scalar conditioning, not sequence encoding. Level-free anchoring (`S-21b` pattern) is necessary but was not sufficient for trees — this bet adds **bounded-capacity attention** with **strong regularization** (the missing piece).

### Member pool
- **Univariate anchors (2):** `NLinear L336 a=1`, `NLinear L336 a=10` (S-26 — same guarantee).
- **Non-linear member (1–2):** `PatchTST-Delta` — steps per origin:
  1. **Level-free deltas:** `d = window[−336:] − anchor` where `anchor = window[−1]` (OT last value), `d ∈ ℝ^{336}`. Target delta `d* = y − anchor` (horizon tail, `anchor` re-added at predict — `S-21b` level-free pattern, prevents level memorization `reflection 2026-09-08 P2`).
  2. **Patch tokenization:** `336 → 14` tokens of `P=24` (or `P=48 → 7` tokens — one ablation arm), each token `∈ ℝ^{P}` → linear projection `→ ℝ^{D=32}` + learnable positional encoding.
  3. **Encoder:** 2-layer Transformer encoder, `heads=2`, `D=32`, `FFN=64`, `dropout=0.30`, `stochastic_depth=0.10`, `weight_decay=1e-2` on all non-norm weights, `attention dropout 0.2`. **No causal mask** (full bidirection within lookback).
  4. **Decoder:** per-horizon linear head from pooled token mean (or last-token) `→ ℝ^{720}` delta forecast, then `+ anchor`.
- Capacity: `~28k` params (projection `24×32 + 2×(attn+ffn) + head 32×720`) — tiny vs data budget, intentionally under-parameterized. Trained with AdamW `lr=3e-4`, early stopping on val delta-MAE, gradient clip `1.0`, batch `64`.
- One member is primary (`P=24, D=32, 2 layers`); second is capacity ablation (`P=48, D=16, 1 layer`) — tests whether fewer longer patches regularize better.

### Gate / protocol
- **S-20-clean, mixed pool `M=4` (2 linear + 2 PatchTST):** tabu search as in Bet 2 (fixed-α fast score `α=3000`, 11-α scan on winner). Members frozen `8545` for val, refit `11425` for test. Per-horizon ridge no-intercept over selected deltas/predictions (ridge blends the linear and non-linear members' delta forecasts). No Ω gate, no tree head — ridge is the only blender.
- **Regularization audit:** log train/val gap per epoch, attention entropy, and token-norm stability (`refit/frozen` ratio `0.8–1.3` — mirrors H2 subband-stability check `0.88–1.21`). If gap diverges or entropy collapses (`< 0.5` bits), auto-reject as overfit before test.
- **Scar compliance:** `held-out val superiority over the delta ridge control` required before test (`reflection 2026-09-08 P1`): the `2`-member S-26 delta-ridge is re-derived in-harness as control; PatchTST subset must beat it on `val[1080:2161)` by `> 0.005` to proceed to frozen test — else REJECT at plan time.

### Falsifiable acceptance criteria (all must hold)
- **Primary:** `MAE_full ≤ 1.9859` and `< 1.9909`.
- **Stability:** `MAE_disjoint-4 ≤ 1.9696` and `W4 ≤ 1.90` (S-26 W4 `1.8427`; `reflection Wald` — W4 is hardest window).
- **Held-out precondition:** `MAE_held-out(val) < MAE_S-26-delta-ridge(val) − 0.005` (proves representation adds signal beyond linear span — `H2 P1`).
- **Regularization:** `val_full − held_out < 0.10` and `train−val gap < 0.15` on delta-MAE (no S-21-style `in-sample 2.33 → held-out 3.65` memorizatiom).

### Explicit close condition
- **If** PatchTST singletons val `> 2.90` (worse than S-26 delta-ridge) **or** the best subset's held-out gain `< 0.005` (fails precondition) **or** frozen-test `MAE_full ≥ 1.9909` / `disjoint-4 > 1.9696`, then **REJECT and close the patch-attention non-linear family for ETTh1 H=720 under S-20-clean**: *"A bounded-capacity attention encoder on level-free patch deltas inherits the univariate saturation; the 14-day OT window's predictable structure is already spanned by the L336 linear map, and inter-patch attention adds no orthogonal frequency/latent signal at this horizon."* Document held-out delta, attention entropy, and val→test transfer. No further non-linear readouts on `L≤336` without exogenous channels or a different pretext (e.g. masked pre-training).

---

## 5. How to execute (one slice at a time, S-20-clean, fail-loud)

For every bet, identical harness shape (mirrors `spectral_omega_gate/rolling_arm_phase2.py` and H2):

1. `python data.py` — verify split `train 8545 / val 2880 / test 2880` (`ProtocolData.load()`).
2. Fit members on `train 8545` → roll `val 2161` origins → `held-out 1080/1081` ridge selection → refit `val_full` → report `held_out`, `val_full`, `disjoint-4` diagnostic.
3. **Fail-loud anchors:** re-derive S-26 `1.9909/2.4710 ±1e-4` on frozen `11425` before any scoring (as `S-20b 8/8 anchors` did); else abort.
4. Refreeze on `11425` → roll `full 2161` test → `MAE_full / RMSE_full / disjoint-4 / W1-4 / bootstrap CI B=2000`.
5. **Promotion requires `full ≤1.9859` AND `disjoint-4 ≤1.9696`** (H2 stop rule). Either fails → REJECT per bet's close condition. Document `plan_impact` (`invalidates/confirms/opens`) as `results_tsfm_phase2.json:68-78` does.

Suggested order: **Bet 1 → Bet 2 → Bet 3** (Bet 1 has the highest expected information gain per Phase 2's explicit opening and the smallest protocol delta; Bet 2 directly addresses the `2352-dim` over-parameterization scar; Bet 3 is the non-linear orthogonality test that would definitively close the univariate non-linear question).

---

## 6. What closing all three would mean

If Bets 1–3 all trigger their close conditions, the univariate + linear-multivariate + same-window non-linear families are **formally closed** under the current `S-20-clean / H2` protocol. The remaining frontier is then not a member swap but a **dataset or horizon protocol change**: different `H` (96/192/336), different dataset (ETTh2/ETTm1/Weather), or a pre-training protocol (masked patch pre-training on the full 17 420-row series before S-20-clean fine-tuning) — each requiring a new `CONTEXT.md` protocol amendment and a fresh `1.9909` baseline for that protocol.

---

*Scout completed 2026-09-13. Graph-aware via `brains/ts_brain/ask.py` + `brains/reflection_brain/ask.py` (ts_brain: H2 saturation `rotation-invariance`, S-21/S-21b level-memorization, S-36 volatility-shift; reflection_brain: `2026-09-12_0435 P1/P3`, `2026-09-08_1200 P1/P2`). All thresholds and pool sizes chosen to be falsifiable against `1.9909` / `1.9696` under S-20-clean.*
