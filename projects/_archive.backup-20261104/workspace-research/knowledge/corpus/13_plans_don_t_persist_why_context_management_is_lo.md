---
type: Concept
id: 13_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 14/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Preprint.
Table 3: 4-way graded probe at L32 (5-fold CV , 80 examples/class). Rows are true classes,
columns predicted.
True↓Pred→ +1+2+3+5 F1
+1 800 0 0 0.994
+2 0719 0 0.882
+3 0 105911 0.733
+5 1 0 1366 0.841
Table 4: Strict-strip recovery on R1-Distill-Llama-70B (5 in-sample ALFWorld tasks).
Task (type) Standard Strict-strip∆
task_000 (pick_heat) 0.029 0.067+0.038
task_002 (pick_two_obj) 0.020 0.062+0.042
task_003 (pick_clean) 0.020 0.053+0.033
task_004 (pick_and_place) 0.018 0.054+0.036
task_006 (pick_and_place) 0.023 0.055+0.032
Mean0.0220.058+0.036
A.6 Reasoning-Model Per-Layer Plan Signal (Dilution Test)
Table 5: Cross-regime probe transfer (referenced in §7). The Llama-trained L32 probe
is at ceiling on Llama, drops on R1 raw, and partially recovers under strict stripping
(p=6×10−4, n=19). Self-probes reach ceiling on both R1 distillations. Qwen3-32B-native
(enable_thinking=True) shows linear encoding ( R2=0.997) without spike-decay locality
(binary AUROC 0.616). The R1 self-probe is at 89.3 ◦ from Llama’s L32 (cosine 0.012); R1-
Qwen=R1-Distill-Qwen-32B.
Probe Eval target AUROCn
LlamaL 32 Llama ALFWorld0.99980
LlamaL 32 Llama HotpotQA1.00025
LlamaL 32 R1 raw (transfer) 0.600 5
LlamaL 32 R1 strict (transfer)0.748[0.62,0.87]19
R1L 32 (self) R1 strict1.00085
R1-QwenL 32 (self) R1-Qwen strict1.00085
Qwen3L 26 (self) Qwen3-think † 0.616∗ 15
†enable_thinking=True, 270 step pairs. ∗RegressionR 2=0.997.
To test the dilution hypothesis (that a reasoning model spreads representation more thinly
across layers, predicting a uniform R1/Llama signal ratio across depth), we report per-layer
plan signal at step +1 on the 5-task ALFWorld subset in Table 6. The R1/Llama ratio varies
4.4× across depth and the two models peak at different absolute layers (L72 for R1, L32 for
Llama). Strong-form dilution is ruled out.
A.7 Cross-Scale Multi-Model Panel
Table 7 collects the cross-model decay results referenced in Section 6; Figure 7 summarizes
them graphically.
A.8 Intervention Sweeps and Head-Level Analysis
Context-level re-anchoring.On 30 held-out ALFWorld tasks ( max_steps= 200), the control,
probe-triggered, and oracle always-replan conditions all land within ±1 task of one another.
This is a clean 30-task null, which is what the in-context retrieval account predicts.
14
