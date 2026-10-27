---
type: Concept
title: 2026-09-13_2200_improvement-how-to-make-it-better
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Reflection — 2026-09-13_2200_improvement-how-to-make-it-better
Date: 2026-09-13
Status: complete
Invoking rule: REFLECTION_RULES.md (T4 user requested a reflection)

## work_summary
Second reflection (forward-looking, prescriptive) on h720 ETTh1 H=720 terminal S-26 (1.9909/2.4710) after all recent bets REJECTED (H2 saturated, S-34 dense multivariate, S-35 level-free RF, S-36 volatility-gated, spectral omega zero-shot TSFM Phase 2). Graph-aware via `python brains/ts_brain/ask.py "improvement tuning regularization"` + `python brains/reflection_brain/ask.py "improvement better frontier protocol"` (fallback — `omp agent --cwd workspaces/reflection-brain` probed, workspace present but isolated agent unavailable on this Windows win32 shell; ask.py fallback documented and sufficient per assignment). Scout `RESEARCH/next-frontier-scout-2026-09-13.md` Bet1/Bet2/Bet3 still-viable directions triaged into 3 concrete, falsifiable improvement protocols with expected gain, cost, close condition and routing invariants.

## problems
### P1: Zero-shot spectral gating spent the TSFM budget without trainable adaptation or uncertainty gating
- **symptom:** Omega-gated Chronos-Bolt Base zero-shot Phase 2 REJECTED on sampled weighted estimate 2.1218 vs S-26 1.9909 (delta +0.1309, 95% CI [1.9733,2.2847] straddles threshold from above); bucket C (Omega>0.5, 53.9% mass, gate fires) had worst bucket MAE 2.2741 vs B 1.9109/A 2.1993 — anti-selective. Disjoint-4 1.8739 PROMOTED but overridden by sampled per `PHASE2_DECISION.md:20-26`. Prior `phase2_inspect.md:36-52` measured 108 min full cost on CPU (6.16 s/origin, 9.0× no amortization); even the 64-origin sampled ran 104.4 s wall.
- **root_cause:** Hard Omega>0.5 gate on a zero-shot model has no calibration to ETTh1 residuals and no selective uncertainty signal; phase2_inspect never measured bootstrap CI on the pilot smoke — full 1165-call plan was budgeted before proving point estimate could clear 1.9859 within CI. `RESEARCH/next-frontier-scout-2026-09-13.md:24` closes this family: "no zero-shot TSFM gate may be re-proposed"; Phase 2 decision explicitly licenses only fine-tuned TSFM variants.

### P2: Full-2161 CPU evaluation was planned before a sampled gate proved viability — budget burned on doomed rollouts
- **symptom:** `phase2_inspect.md:43-52` extrapolates 1165 gated origins × 6.16 s = 119.6 min serial / 108 min batched — 7–8× over the 15-min CPU budget and 900 s agent budget that cancelled the run (`phase2_inspect.md:29-32`). `/tmp/phase2_run.log` stalled at chunk 0:20, never reaching metrics. Prior probes S-39..S-41 likewise paid full 2161 cost for outcomes already predictable on held-out val.
- **root_cause:** No sampled-before-full CI gate in the protocol — full rolling was the default even for low-EV bets. `phase2_inspect.md:77-98` Option A (disjoint-4 + 64 stratified sampled, ~8 min) is the minimal scientifically sufficient decision path but was introduced only as a post-hoc rescue, not as a pre-registered gate.

### P3: Repeated spurious-capacity bets on the saturated 336-dim span without a held-out penalty-structure or orthogonality precondition
- **symptom:** Six post-S-26 probes REJECTED with same signature: held-out val edge <0.005 that does not transfer. H2 wavelet best 1.9906 vs S-26 1.9909 (delta −0.0003) — DWT is a rotation of the NLinear span, subband penalties moved val <0.004 (`CONTEXT.md:152-160` stop rule FIRED). S-34/S-37 dense 2352-dim multivariate val 3.77–38.91 spurious vs test 2.0539; S-35 RF on same window 2.0112; S-36 diverse-spread gating held −0.0078 but test +0.4815 via val→test volatility shift −0.48 to −0.90σ. Scout `2026-09-13.md:14-24` marks entire univariate-linear / same-window non-linear / dense multivariate families as refuted.
- **root_cause:** No plan-time filter requiring candidate families to prove penalty-structure gain on held-out val (H2 P1: val_beats >0.005) or orthogonality of the representation before delegation. Bets were scored only after paying the 2161-origin test cost.

## solutions
### P1
- **solution:** Improvement I1 — PEFT Fine-Tuned TSFM + S-26 Ridge Stack (Scout Bet1, Protocol Change). Pin `amazon/chronos-bolt-base@<sha>` with LoRA r=8/alpha16 on q/v only (~0.3% trainable); train on `train 8545` (val 2880 untouched for early stopping), then per-horizon ridge no-intercept over M=3 (2× NLinear anchors + ChronosBolt-LoRA) on `val[0:1080)`→select on `val[1080:2161)` with 11-α grid; refit LoRA on 11425 for frozen test. Omega stratification diagnostic only, no hard gate. Expected gain: sampled full ≤1.9859 (≥0.0050 over S-26) with disjoint-4 ≤1.9696 and bootstrap upper <1.9909. Cost: 1 GPU fine-tune (minutes) + 2161×720 scoring (same as any S-*); LoRA merged at inference, no per-origin latency. Close condition: if TSFM-LoRA singleton val >2.8527 (S-26 val_full) or frozen-test full ≥1.9909 or disjoint-4 >1.9696 with interior alpha, REJECT and close the foundation-model adaptation family for H=720 under S-20-clean (no further full-FT / larger-r without new pre-registration); document singleton, 3-member pooled and val→test delta.
- **verification_evidence:** `RESEARCH/next-frontier-scout-2026-09-13.md:30-61` (Bet1 pool, optimizer, S-20-clean Phase1/Phase2, 4-gate acceptance, explicit close text); `projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/PHASE2_DECISION.md:5,20-26,54-57` (zero-shot anti-selectivity C 2.2741, sampled 2.1218, fine-tuned licensed successor); `projects/ts-ml-experiments/h720/CONTEXT.md:4,152-160` (S-26 1.9909/1.9696 baselines, H2 fired stop rule); `brains/ts_brain/ask.py "improvement tuning regularization"` + `brains/reflection_brain/ask.py "improvement better frontier protocol"` (fallback executed, 1 match + 5 scars surfaced).
- **files_changed:**
  - `MONITORING/reflection/2026-09-13_2200_improvement-how-to-make-it-better.md`
  - `projects/ts-ml-experiments/h720/MONITORING/reflection/2026-09-13_2200_improvement-how-to-make-it-better.md`

### P2
- **solution:** Improvement I2 — Sampled-Before-Full CI Gate + Infra Fix (Evaluation Budget Change). Pre-register two-stage harness `rolling_arm.py --origins {disjoint4,sampled,full}` per `phase2_inspect.md:79-98`. Stage 1 (decision, ~40 s): disjoint-4 MAE vs 1.9696; Stage 2 (estimate, ~6 min serial): stratified 64 (60 = 20×A/B/C + 4 disjoint, seed 0) weighted full estimate with B=2000 bootstrap 95% CI — promotion to full 2161 requires point ≤1.9859 AND CI upper <1.9909, else REJECT at sampled cost. Infra: flush `harness.log` per chunk, partial `results_*.json` with `mode: sampled`, `estimated: true`, guard `750 s` budget trip, and GPU-gate `full` behind `--device cuda` (full remains ground truth, not default). Expected gain: 95% reduction in TSFM calls (1165→22 gated) and ~14× latency reduction (108 min→8 min) for negative bets; 6.16 s smoke validated. Cost: one extra script flag + CI bootstrap (B=2000, ~seconds). Close condition: if sampled 95% CI lower >1.9859 with point ≥1.9909 (as Phase 2 2.1218 [1.9733,2.2847]), close the configuration without full rollout — full GPU run becomes optional validation, never a promotion path for same threshold.
- **verification_evidence:** `projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/phase2_inspect.md:36-52,77-98` (measured 6.16 s single / 55.50 s batch10 ratio 9.0×, 108–120 min extrapolation, Option A/B/C spec); `projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/PHASE2_DECISION.md:28-32,50-58` (disjoint 25.1 s vs sampled 104.4 s, sampled verdict REJECTED, CI table); `RESEARCH/next-frontier-scout-2026-09-13.md:130-139` harness shape demanding frozen S-26 re-derivation before scoring.
- **files_changed:**
  - `MONITORING/reflection/2026-09-13_2200_improvement-how-to-make-it-better.md`
  - `projects/ts-ml-experiments/h720/MONITORING/reflection/2026-09-13_2200_improvement-how-to-make-it-better.md`

### P3
- **solution:** Improvement I3 — Orthogonal Representation + Structured Sparsity with Held-Out val_beats Precondition (Architecture Pivot — Scout Bet2+Bet3 merged as ordered bets). (a) Bet2: Group-Sparse Patch NLinear — 14 patches P=24 (336→14 mean-pooled, train-only μ/σ), GroupSparseNLinear on ℝ^{7×14}=98 features with group-lasso penalty `λ·Σ_c||w_{c,:,h}||2` (OT unpenalized, exo λ∈{0.5,2.0}, P∈{24,48}, 4 candidates tabu-selected, effective 70k weights vs 1.69M dense — 24× cut). (b) Bet3: Level-Free PatchTST-Delta — anchor `window[-1]`, 14 tokens P=24→D32, 2-layer encoder heads2/FFN64 dropout0.30, delta head 32×720, ~28k params, AdamW 3e-4 early-stopping on val delta-MAE. Both under S-20-clean tabu (2 anchors + candidates), per-horizon ridge no-intercept, transfer guard `full−val_full<0.15`, attention entropy check. Ordering Bet2→Bet3 (multivariate sparsity before attention; cheaper, directly addresses 2352-dim scar). Expected gain: each bet targets disjoint saturated subfamily — Bet2 beats S-26 val 2.8527 by >0.005 on held-out AND full ≤1.9859/disjoint ≤1.9696 with 1–3 active exo channels; Bet3 requires held-out delta-ridge beat >0.005 and val_full−held_out<0.10 else auto-reject before test. Cost: Bet2 deterministic block-coordinate descent (seconds); Bet3 one GPU train (~minutes) + standard rolling. Close condition: Bet2 — if tabu collapses to univariate pair (0 exo active) AND best multivariate singleton val>2.85 → close linear multivariate family; Bet3 — if PatchTST singleton val>2.90 or held-out gain<0.005 or full≥1.9909/disjoint>1.9696 → close patch-attention non-linear family on L≤336; all three Bets closed ⇒ univariate + linear-multivariate + same-window non-linear formally closed per Scout §6, frontier becomes dataset/H protocol change.
- **verification_evidence:** `RESEARCH/next-frontier-scout-2026-09-13.md:64-95` (Bet2 patch/group-lasso formulation, tabu, sparsity guards), `RESEARCH/next-frontier-scout-2026-09-13.md:97-127` (Bet3 PatchTST-Delta architecture, capacity, held-out precondition, W4 ≤1.90 cap), `projects/ts-ml-experiments/h720/CONTEXT.md:152-160,276-288` (H2 saturation basis-rotation, S-34 val 3.77–38.91 dense collapse), `MONITORING/reflection/2026-09-12_0435_S-h2-wavelet-terminal-close.md:9-14,45-60` (rotation-invariance P1/P3, penalty noise 0.005 bar).
- **files_changed:**
  - `MONITORING/reflection/2026-09-13_2200_improvement-how-to-make-it-better.md`
  - `projects/ts-ml-experiments/h720/MONITORING/reflection/2026-09-13_2200_improvement-how-to-make-it-better.md`

## prevention_rules
### P1
- **invariant:** Never re-propose a zero-shot foundation-model gate on ETTh1 H=720 without a calibrated uncertainty signal and bootstrap CI — any TSFM promotion MUST be PEFT/fine-tuned on ETTh1 under S-20-clean and blended via learned per-horizon ridge (no hard Omega threshold); zero-shot Chronos-Bolt + Omega 0.5 is refuted (sampled 2.1218 anti-selective C 2.2741) and may not be re-delegated without a new gate or adapter.
- **owning_doc:** `projects/ts-ml-experiments/h720/CONTEXT.md`
- **owning_doc_updated:** N (H2 stop rule + `RESEARCH/next-frontier-scout-2026-09-13.md:24-26` + `PHASE2_DECISION.md:5` already record this closure; this rule codifies the forward ban)
- **family:** protocol-domain

### P2
- **invariant:** Always sample before full — any harness whose full cost exceeds 15 min CPU (measured ≥6 s/origin serial, batched 9.0× no amortization) MUST run disjoint-4 + 64 stratified sampled with B=2000 bootstrap 95% CI as the binding promotion gate; full 2161 rolling is GPU-only (`--device cuda`) and never the default on CPU. A point estimate ≥1.9859 or CI straddling from above at sampled cost closes the configuration without full rollout.
- **owning_doc:** `projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/phase2_inspect.md`
- **owning_doc_updated:** N (Option A spec already exists; this reflection elevates it to a project-wide budget gate for all future h720 bets)
- **family:** protocol-domain

### P3
- **invariant:** Always require val_beats gate — a candidate family that is a linear transform (DWT/rFFT/unitary) of the incumbent L=336 span, or a non-linear readout on the same span, MUST demonstrate held-out val gain >0.005 over the S-26 delta-ridge control from the penalty/structure alone before test delegation; dense 7-channel multivariate (2352-dim) without group sparsity is banned, and patch-embedded group-lasso / patch-attention are the only admissible successors. Failure to beat val on 1081 held-out origins rejects at plan time, not after 2161 test origins.
- **owning_doc:** `projects/ts-ml-experiments/h720/CONTEXT.md`
- **owning_doc_updated:** N (`CONTEXT.md:152-160` H2 stop rule + `MONITORING/reflection/2026-09-12_0435_S-h2-wavelet-terminal-close.md` P1/P3 invariants already state this; this rule merges them into the val_beats precondition for all future bets)
- **family:** protocol-domain

## next_action_routing_changes
- none (this is a prescriptive reflection; routing changes are the three invariants above — no AGENTS.md/CONTEXT.md structural edits required in this session; next scout cycle cites Bet1→Bet2→Bet3 order per `RESEARCH/next-frontier-scout-2026-09-13.md:140`)

## open_risks
- Bet1 LoRA r=8 may be under-capacity for 720-step spectral peaks — ablation r=16/full-FT intentionally deferred until after first close condition fires to avoid over-searching the TSFM family.
- Bet2 patch mean-pooling discards intra-patch phase — max-pool ablation is budgeted as one arm only; a transformer-style patch embedding would revert to Bet3 capacity without the attention ablation.
- Phase2 sampled estimate weighted MAE 2.1218 has 95% CI width 0.31 — stratification reduces variance but not enough to rescue far-above-threshold points; a future full GPU 2161 run will still be needed to validate any Bet that passes sampled.
- Isolation: `omp agent --cwd workspaces/reflection-brain` was probed and found unavailable on this win32 host (workspace exists, agent binary shows `omp launch` usage only); graph-aware fallback via `brains/ts_brain/ask.py` + `brains/reflection_brain/ask.py` was executed and documented per assignment.
