---
type: Concept
title: S49_PLAN
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# S49 — Wavelet Feature Engineering + NLinear Anchoring on h720 (Research & Plan)

**Date:** 2026-09-15
**Slice (proposed):** `S-49-wavelet-anchor`
**Directory (proposed):** `projects/ts-ml-experiments/h720/sub_experiments/wavelet_anchor_s49/`
**Status:** PRE-REGISTRATION / PLAN ONLY — NOT executed. Requires the user's full three-stage spec (see §6) and an explicit go decision.

---

## 1. Closure state — this idea is already built and *closed* twice

The user's request — *feature engineering on wavelets, with NLinear's last-value anchoring* — maps **directly** onto two prior h720 bets. Both are REJECTED and their families are recorded CLOSED. Citing this is mandatory per **S-43 P3** (a family can be refused by citation, not re-execution).

| Bet | What it did | Verdict | Family closed |
|---|---|---|---|
| **S-46** `anchored_wavelet_elm_s46` (2026-09-14, same day as the attachment) | `anchor → SWT db4 J=3 periodization + VisuShrink → fixed tanh ELM (h200/h400) → per-horizon readout → de-anchor`. The design doc's own "Attachment of this task" is the NLinear-anchoring-trick writeup with Stages 0/4 = anchor/de-anchor and Stages 1–3 = DWT/SWT→threshold→ELM→Lasso. | **REJECTED.** Best blend = S-44 subset (no wavelet member enters tabu). Held-out gain `−0.0085` (≤0.005 FAIL). Both wavelet singletons >2.90. Blend `full 1.9781 = incumbent` (delta 0.0000), G1–G4 all fail. | **anchored-wavelet-ELM family closed** (reopen only with *different wavelet / activation / dictionary* or a protocol change). |
| **S-48** `subband_experts_s48` (2026-09-15) | `anchor → SWT db4 J=3 → 4 per-horizon Ridge experts on subbands cA3/d3/d2/d1 (no pooling, no ELM)`. | **REJECTED.** Tabu stays on S-44 subset; subband experts never enter. Blend = S-44 (delta 0.0000). | **subband-direct-Ridge family closed** for ETTh1 H720 S-20-clean. |

**Therefore:** re-running "anchored wavelets + ELM/Ridge readout on L=336 / J=3 / db4 / last-value anchor" is a same-class re-open and will be refused by citation. A new bet must differ on a *declared non-equivalent* axis (S-43 P3).

Also relevant context (why incremental wavelet variants fail here):
- **H2** (linear DWT): DWT of the anchored L=336 window is an **orthogonal rotation of NLinear's span** → uniform-alpha wavelet Ridge ≡ NLinear(α). Univariate linear family **saturated**. Stop rule FIRED.
- **S-47** mini-suite: subband `cA` (low-pass) carries signal *on synthetic H=48/96*, but on real H=720 `cA3` is collinear with NLinear L336 → does not transfer.

---

## 2. What the attachment actually specifies (as recoverable)

The attachment's recoverable text begins:

> *"Adding NLinear's anchoring trick to your three-stage architecture is a sound and elegant refinement. The anchoring mechanism directly addresses a critical weakness in the pipeline you've designed: distribution shift. By anchoring the input to the last observed value, you make the model's job significantly easier and more …"*

Two facts the attachment asserts:
1. The user already has a **"three-stage architecture"** for h720 — this is *not* the S-46 four-stage (anchor→wavelet→ELM→readout) decomposition; the user's own pipeline is described as **three stages** and the anchoring is proposed as an *addition* to it.
2. The motivation is **distribution shift** (the DLinear/NLinear paper's rationale: serious train/test distribution shift on ETTh1/ETTh2).

**Gap:** the full three-stage spec — what the three stages are, what features they consume, how they currently handle level — is **not on disk** and only the first sentence survives in memory. The S-46 four-stage pipeline was *my* (prior-session) interpretation of the same attachment; the user's mental model is a different, pre-existing three-stage design. **§6 surfaces this as the blocking open question.**

---

## 3. Why naive re-runs fail (the failure signature)

Every post-S-26 wavelet/non-linear probe on ETTh1 H720 shares one signature (see `MONITORING/reflection/2026-09-13_2200`):
- held-out val edge < 0.005 (or negative), **does not transfer** to frozen test;
- or val→test **distribution shift** (S-36 volatility gate: −0.48 to −0.90σ; Spectral-Ω: +0.52σ);
- wavelet members are **collinear with NLinear L336** (low-pass ≈ NLinear; details ≈ noise).

So the bar any new bet must clear (S-44 incumbent, per S-44 P2):
- **G1** `full ≤ 1.9731` (1.9781 − 0.005)
- **G2** `full < 1.9781`
- **G3** `disjoint-4 ≤ 1.8634`
- **G4** paired Δ 95% CI upper < 0 (B=2000, seed 0)
- **Precondition:** held-out gain > 0.005 vs S-44 control (2.4936) *before* frozen test.

---

## 4. Proposed non-equivalent axis (S49) — the only honest pivot

To escape citation-refusal (S-43 P3) the bet must change a structural axis S-46/S-48 did **not**:

**(A) Wavelet family / basis change.** S-46/S-48 used `db4`, `J=3`, `periodization`. A genuinely different basis:
- **Complex wavelet / analytic (DT-CWT)** for shift-invariant magnitude+phase at each scale (PyWavelets has no DT-CWT; needs `pytorch-wavelets` or `dtcwt` — a real dependency change, not a knob).
- **Learned / data-adaptive wavelet** (learnbale lifting scheme, or a small `nn` per-subband), vs the *fixed* `pywt` dictionary S-46 used. This also answers the S-46 "different dictionary" reopen clause.

**(B) Readout class change (orthogonal to S-46 dense ELM / S-48 Ridge).**
- **Per-horizon structured-sparse / group-sparse** readout over subbands (group = scale → forces scale selection), not Lasso-over-flattened-ELM (S-46) nor per-subband independent Ridge (S-48).
- **Per-horizon low-rank / shared-basis** readout across the 720 steps (exploits horizon correlation the 720 independent fits ignore).

**(C) Resolution / horizon context change (the CONTEXT-listed remaining frontier).**
- `J>3` (more scales) or `L>336` (longer lookback) — S-46/S-48 were locked to L=336/J=3 to match the S-44 span. A longer anchoring window is a *different protocol knob*, allowed.

**(D) Anchor variant.** S-46/S-48 used last-value only (S-46 explicitly rejected mean/median/learned anchors as follow-ups). A **seasonal/learned anchor** is a declared non-equivalent follow-up — but high risk (S-28 intercept catastrophe scar; keep `fit_intercept=False` on the head).

**Recommended single bet:** **(A)+(B)** — *learned/fixed analytic multi-scale decomposition (DT-CWT or learned lifting) → per-horizon group-sparse readout → NLinear last-value anchor/de-anchor*. This is non-equivalent to both S-46 (fixed ELM dict) and S-48 (independent per-subband Ridge) on two declared axes, and exercises the "distribution shift" motivation (multi-scale magnitude+phase is more shift-robust than level-only anchoring).

---

## 5. Pre-registration skeleton (to fill after the spec + go-decision)

Mirrors S-46/S-48 conventions: one `rolling_arm.py` (self-contained tabu-7 + per-horizon ridge stack, no shared-refactor), one member module, parity block vs `results_s44.json` (tol 1e-4), gate semantics **BLEND-based** (S-43 P1) vs in-harness S-44 re-derivation.

- **Pool:** S-44 `M=4` incumbent pool + 1–2 new multi-scale members (group-sparse readout). `M=5/6`.
- **Protocol:** S-20-clean — members frozen 8545 (val), refrozen 11425 (test); tabu-7 fixed-α 3000 no_improve 5; per-horizon ridge no-intercept 11-α grid on `val[0:1080)/val[1080:2161)`; held-out S-44 control precondition >0.005; frozen test stack on 11425-refit; S-44 parity block.
- **Binding gate:** G1–G4 above. Promotion = incumbent replacement (S-44 P2).
- **Close family (if rejected):** record surviving positive per S-43 P3; declare the *learned/analytic multi-scale + group-sparse* family closed under S-20-clean.

---

## 6. OPEN QUESTIONS — blocking before any code (must resolve)

1. **The "three-stage architecture" spec.** What are the three stages, what do they currently consume, and where does wavelet feature engineering + anchoring plug in? The S-46 implementation assumed a 4-stage (anchor→wavelet→ELM→readout) decomposition of the *attachment's* idea; your message implies a *pre-existing* 3-stage pipeline. I need its definition to implement "feature engineering based mostly on wavelets" correctly. *(No copy exists on disk; only the 1-sentence framing survived.)*
2. **Which non-equivalent axis do you want** — (A) basis/learned-wavelet, (B) group-sparse/low-rank readout, (C) longer window/scales, (D) anchor variant? Recommend **A+B**.
3. **Confirm go-decision** given S-46/S-48 are already closed — i.e. you want a *non-equivalent* re-attempt (new family), not a re-run.

---

## 7. Cited evidence (grounded)
- `h720/CONTEXT.md` §S-46 (lines ~408–416): REJECTED, anchored-wavelet-ELM family closed. §S-48 (~426–431): REJECTED, subband-direct-Ridge closed. §H2 (~153–160): linear wavelet saturated, stop rule fired. §Prevention rules S-43 (~389–406): gate semantics, per-window deltas, family-close record, S-44 incumbent 1.9781/1.8634.
- `anchored_wavelet_elm_s46/S46_DESIGN.md`: the attachment's Stages 0–4 are literally its design; cites "Attachment of this task — aiming NLinear's anchoring trick".
- `subband_experts_s48/S48_DESIGN.md`, `diverse_mini_s47/S47_DESIGN.md` (subband `cA` wins synthetic, not H720).
- `MONITORING/reflection/2026-09-13_2200_improvement-how-to-make-it-better.md` P3: repeated spurious-capacity bets on the saturated 336-dim span.
