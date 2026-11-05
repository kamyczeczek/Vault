---
type: Concept
id: 06_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 7/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
Table 1: Probe performance. ALFWorld: Ridge regression at ℓ∗ = 32, 5-fold CV on 1360
steps across 80 tasks. HotpotQA transfer: zero-shot application of the ALFWorld probe
direction to 238 HotpotQA steps (60 positive, 178 negative) at two destination layers. R2 is
reported for regression; binary metrics are computed by thresholding regression output at
τ=0.15.
Metric ALFWorld HotpotQAL 32 HotpotQAL 40
R2 0.875±0.016 n/a n/a
AUROC0.999 1.000 1.000
F1 (τ=0.15)0.8980.6780.968
Precision 0.985 0.513 0.938
Recall 0.825 1.000 1.000
tion lifts to F1 0.920. Some component of the plan-presence direction generalizes across
domains beyond what step index would predict, but the operating point needs per-domain
calibration.
5.2 Probe Validity, Gradedness, and Calibration
Three controls back the probe (full numbers in Appendix A): a shuffled-label control and
step-index regressor confirm the residual fit ( R2 = 0.875) captures structure beyond the
R2 = 0.978 step-index baseline at L32; a 4-class step classifier attains macro F1 = 0.862 with
strictly monotonic confusion; and the main binary probe is near-perfectly calibrated (Brier
≈10 −6).
5.3 Lag Analysis: Early Warning
The probe is useful only if it fires before behavioral failure. Defining lag=s deviate −s probe_fire
(deviation = first action with plan-alignment < 0.3 from a Claude Opus 4 judge), of the
80 tasks 31 deviated, and on those the probe fires on average 4.45 steps ahead (median 5),
leading deviation in 74.2% of cases. A 4-5 step lead is well within ALFWorld’s 20-step cap,
so a context manager could use the probe to decidewhento re-surface the plan into the
window.
6 Cross-Domain and Cross-Model Validation
We test the standard-LLM result along two axes: domain (HotpotQA) and scale (Llama-3.1-
8B).
Cross-domain (HotpotQA).On 30 HotpotQA pairs with the same Llama-3.1-70B, step +1
plan signal is 0.445 and drops to 0.036 at step +2 (12.4×, p< 0.001); the initial magnitude
nearly matches ALFWorld (0.453). The faster drop fits HotpotQA’s observations being
Wikipedia passages unrelated to the plan, vs. ALFWorld’s plan-relevant room states. The
peak layer is L34 (vs. L32); the encoding locus is domain-invariant. The ALFWorld-trained
probe transfers zero-shot at AUROC 1.000, with isotonic recalibration lifting L32 transfer to
F1 = 0.920. The direction is domain-invariant; only the operating point needs recalibration.
Cross-scale (Llama-3.1-8B).On 20 ALFWorld tasks, plan signal peaks at 0.382 and decays
10.9× by step +5, matching the 70B shape; the peak sits at ∼ 37.5% relative depth (L12 of 32)
vs. ∼ 40% (L32 of 80) for 70B, as the attention-reconstruction account predicts: plan signal
lives in a depth-relative band, not a fixed layer (full multi-model panel in Appendix A.7).
7
