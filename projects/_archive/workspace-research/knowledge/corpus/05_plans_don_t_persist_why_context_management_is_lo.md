---
type: Concept
id: 05_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 6/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
0 8 16 24 28 32 36 40 44 48 52 56 64 72 80
Layer
0.0
0.2
0.4
0.6
0.8Plan signal at step +1
L32: 0.686
(peak)
(a) Layer profile at step+1.
0 2 4 6 8 10 12
Step relative to plan
0.0
0.1
0.2
0.3
0.4
0.5Plan signal
clean+place (n=18)
pick two (n=15)
heat+place (n=13)
pick+place (n=19)
examine (n=5)
cool+place (n=10) (b) Decay by task type.
Figure 2: Plan signal is localized in depth but stable across tasks. The peak layer is L32
(signal 0.686), and all six ALFWorld task types converge to the same residual.
-2 0 2 4 6 8 10 12 14 16
Step relative to plan
0.0
0.1
0.2
0.3
0.4
0.5Plan signal (1  cos sim)
plan
injected0.453
0.110
4.1× drop
Pre-plan
Post-plan
Figure 3: Plan signal (mean ± SE, 80 tasks) as a function of step offset from guard injection.
Pre-plan signal (s<0) is near zero (validation). Signal jumps to 0.453 at step+1 then drops
4.1×in one step.
On ALFWorld, the probe predicts plan-signal magnitude at R2 = 0.875 ± 0.016, well below
the R2 = 1 a trivially-leaked feature would produce. The induced binary decision at
τ= 0.15 reaches AUROC 0.999 with balanced precision (0.985) and recall (0.825). Applying
the ALFWorld probe direction zero-shot to HotpotQA gives AUROC 1.000 at both L32 and
L40.
Caveat: probe AUROC near1.0is partly step-index leakage.Step index is near-perfectly
decodable from the residual stream (R2=0.978 at L32; Appendix A), and plan-signal mag-
nitude is correlated with step index by construction, so a probe that learns “predict step
index” would also score high on the active-vs-decayed contrast. We have not run the
discriminating control: a mixed-effects analysis holding step index, task type, plan length,
and observation-plan overlap fixed. Until then the AUROC should be read as “at least as
informative as step index,” not as a content-specific representation.
The cross-domain transfer is more informative than the in-domain AUROC. At the ALF-
World cutoff τ= 0.15, L40 transfer is sharp on HotpotQA (F1 0.968); L32 keeps full recall
but fires on HotpotQA-specific variance (precision 0.513), which a short isotonic recalibra-
6
