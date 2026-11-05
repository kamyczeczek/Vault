---
type: Concept
id: 14_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 15/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Preprint.
Table 6: Per-layer step+1 plan signal (5 ALFWorld tasks). The R1/Llama ratio is far from
uniform; peaks differ.
Layer R1-Distill-70B Llama-70B Ratio
L8 0.002 0.031 0.07
L32 0.0230.1840.12
L40 0.026 0.129 0.20
L48 0.030 0.113 0.27
L56 0.032 0.096 0.33
L72 0.0390.070 0.56
L80 0.022 0.044 0.50
Llama-3.1-70B Llama-3.1-8B Phi-3-Medium (14B) Qwen2.5-72B
0.0
0.1
0.2
0.3
0.4
0.5
0.6Plan signal (1  cos sim)
0.453
0.110
0.382
0.068
N/A
N/A
N/A
N/A
replay-paired replay-paired unpaired unpaired
Multi-model plan signal: data availability
Step +1 signal
Step +2 signal
Figure 7: Multi-model panel. Llama-3.1-70B: full replay-paired decay curve, peak L32, decay
4.1×. Llama-3.1-8B: same shape at smaller scale (peak 0.382, 10.9 × decay) at matched
relative depth around 33%. Phi-3 and Qwen2.5: plan signal not computable from archival
data (non-replay-paired).
Residual-stream steering ( nruns=5paired, n=150pooled).We sweep at L32 with α∈
{0.5, 1.0, 2.0} on 30 held-out ALFWorld tasks × 5 paired runs. At α=0.5 the pooled paired
contrast is a clean directional null: ∆= +1.33 pp (SR 54.7% → 56.0%; paired Wilcoxon
p=0.97; McNemar 11/12/7 help/hurt/tie, p=1.00; 95% bootstrap CI [−8.0, +11.3]). Within-
replicate ∆s straddle zero: +8.9 pp at nruns=3, −10.0 pp at the new nruns=2 replicate.
Pooling resolves them. α=1.0 and α=2.0 both yield −3.3 pp drops below baseline. Uniform
residual addition along the L32 plan direction is not a behavioral knob at this scale, which
is the directional null the population-coded view predicts: a single-axis push along a
measurement of the plan-presence contrast does not function as an intervention.
Head-level structure.A deterministic head-level analysis shows the plan direction is dis-
tributed across the 64 heads at L32 with mixed-sign top-3: top-3 captures 23% of ∑h |ch|,
top-10 captures 55%. A head-aware intervention that respects the signs of ch (n=90 paired,
β=1.0) gives +3.3 pp at effective magnitude 0.094 (directional but within noise). At β=2.0
(effective magnitude 0.188) it flips to −4.4 pp. Scaling head-aware to match α=0.5’s effective
magnitude (β≈ 5.3) destabilizes generation: the model stops emitting termination tokens
within the LLM-call budget. Uniform addition at the same effective magnitude ran cleanly
but landed at the n=150 null above. Both intervention shapes (uniform at matched mag-
nitude, head-aware at low magnitude) fail to reliably move task success. The asymmetry
is what isolates the population-coded contrast as a measurement of which heads carry
productive vs. antagonistic plan signal, rather than as a knob that can be scaled arbitrarily.
A.9 Why Does ALFWorld Decay Slower than HotpotQA?
The 3 × gap between ALFWorld decay (4.1 ×) and HotpotQA decay (12.4 ×), given the
near-identical initial signal (0.453 vs. 0.445), has a plausible structural explanation in the
observations themselves. ALFWorld observations (“You arrive at countertop 1. On the
15
