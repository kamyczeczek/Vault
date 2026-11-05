---
type: Concept
id: 12_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 13/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
Table 2: Probe validity controls. Real: binary AUROC of step +1 vs. step≥+ 3. Shuffled:
same probe with labels permuted. Step R2: linear regressor predicting step index from
hidden state.
Layer Real AUROC Shuffled AUROC∆StepR 2
L8 1.000 0.297 0.703 0.998
L32 1.000 n/a n/a 0.978
AUROC
(real, L8)
AUROC
(shuffled)
AUROC
(within-step)
Step-idx R²
(L8)
Step-idx R²
(L32)
0.0
0.2
0.4
0.6
0.8
1.0Score
1.000
0.297
0.588
0.998 0.978
gap=0.703
chance
Plan signal Leakage controls Step-index R²
Figure 5: Step-index leakage at L8. Real binary AUROC (1.000) drops to chance (0.297)
under label shuffling. The Ridge regression target at L32 (continuous plan-signal magnitude)
sidesteps this confound.
A.4 Probe Calibration
Brier score and 10-bin Expected Calibration Error (ECE) at L32 are in Figure 6. The main bi-
nary probe (step+1 vs. ≥+ 3) is near-perfectly calibrated (Brier= 2.5 × 10−6, ECE= 0.0002),
which is unsurprising given the wide plan-signal gap between classes. The harder boundary
probe (step +2 vs. +3, plan-signal gap 0.110 vs. 0.060) shows moderate miscalibration
(ECE=0.066), addressed via per-domain isotonic recalibration.
0.0 0.5 1.0
Mean predicted probability
0.0
0.2
0.4
0.6
0.8
1.0Fraction of positives
ECE = 0.0002
Main probe (step+1 vs step +3)
Perfect
0.0 0.5 1.0
Mean predicted probability
0.0
0.2
0.4
0.6
0.8
1.0Fraction of positives
ECE = 0.0657
Boundary probe (step+2 vs step+3)
Perfect
Figure 6: Reliability diagram for theL 32 probe. Diagonal indicates perfect calibration.
A.5 Strict-Strip Per-Task Recovery
Per-task strict-strip recovery on R1-Distill-Llama-70B is in Table 4. Every task shows positive
recovery; the cross-task mean is +0.036 (+163%). Five held-out tasks covering two task
types not in the in-sample set yield+153%.
13
