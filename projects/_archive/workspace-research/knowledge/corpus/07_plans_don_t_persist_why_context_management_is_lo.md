---
type: Concept
id: 07_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 8/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
7 Plan Maintenance in Reasoning Models
In the standard-LLM regime, plans are not stored across steps; they are re-read from
context. Reasoning models behave differently, and standard replay pairing does not see the
difference.
The apparent deficit.On a 5-task ALFWorld subset, standard replay pairing on DeepSeek-
R1-Distill-Llama-70B (DeepSeek-AI, 2025) gives step +1 plan signal of 0.022, versus 0.099 for
Llama-3.1-70B on the same tasks, so R1 looks 4.5× weaker. Taken at face value, a reasoning
model that emits explicit <think> traces appears to encode the plan less than a standard
instruct model.
Three hypotheses, one cause.Dilution (a uniform R1/Llama ratio across depth) is ruled
out: the ratio varies 4.4× across layers and the models peak at different layers (L72 vs. L32).
Position mismatch is small (Llama exceeds R1 at every matched position). The remaining
cause is contamination via re-derivation: re-stated plan content inside prior <think> blocks
reappears in B’s history, so both conditions encode plan content (Appendix A).
Strict-strip correction and verification.Re-running B with strict stripping raises step
+1 plan signal from 0.022 to 0.058, a +163% change; every in-sample task moves the
same way (Appendix A.5) and the R1-Llama gap shrinks from 4.5 × to 1.7×. Five held-
out tasks of unseen types yield +153%. On non-reasoning Llama strict stripping is a
+4.8% no-op, ruling out a generic reasoning-history mechanism. The recovery is large
but partial, and the residual 1.7× gap is consistent with plan content also re-stated in the
retained Thought:/Action: text, which strict stripping does not remove; redacting plan
spans wherever they occur is the clean follow-up (§9).
Probe transfer.The Llama-trained L32 probe applied zero-shot to R1 strict-strip ( n=19)
reaches AUROC 0.748 (p=6×10−4); R1 self-probes (n=85) reach 1.000, in a direction 89.3◦
from Llama’s L32 (Table 5). R1-Distill-Qwen-32B is the same (self-probe 1.000, n=85). On
a third family, Qwen3-32B-native ( enable_thinking=True; n=15, 270 step pairs), the L26
self-probe fits per-step plan-fidelity at R2=0.997 but its binary spike-vs-decay AUROC is
only 0.616: Qwen3-native shows persistent plan-conditional drift (cos-distance rises from
0.030 at step +2 to ∼ 0.13 by step +19) instead of spike-then-decay. So linear encoding of
plan presence holds across all three reasoning families; the spike-decay timing is specific to
distilled R1.
Behavioral check (cross-family, n=25).Across R1-Distill-Llama-70B, Qwen3-32B-thinking
(Qwen Team, 2025), and their non-reasoning baselines, behavioral effects are small and
not significant: both reasoning models score 0/25 raw, and strict stripping moves Qwen3-
thinking to 2/25 (matching its no-thinking twin) while R1 stays 0/25 (Fisher p=0.49). Our
claim is representational, not behavioral; it rests on the paired-trajectory and probe-transfer
numbers above (full Phase-1 detail in Appendix B, Table 8).
8 When Context Management Fails: A Compression Stress Test
The decay finding makes a falsifiable operational prediction: if the plan is a context-time
object with no internal backup, a compression policy that evicts plan tokens should sharply
hurt task success, and the early-warning probe (§5.3) should be able to re-surface the
plan in time to prevent the loss. We test both on 30 ALFWorld tasks ( ×5 runs = 150
runs/policy, Llama-3.1-70B, 20-step cap) under four context policies at a matched budget
(keep_recent=4 messages plus the system prompt): none (no eviction); naive (system
prompt + last 4 messages); plan_protected (naive with the plan span always pinned); and
probe_gated (naive, re-injecting the plan only on steps where the probe fires). Significance
is paired permutation (10k) with bootstrap 95% CIs (Table 9 in Appendix C).
Eviction is catastrophic; protecting the plan does not fix it.Naive eviction nearly thirds
task success (56.7% → 22.0%, −34.7pp, p< 0.001): agents keep no usable plan once its
tokens leave the window, exactly as the decay curve predicts. But neither plan-aware policy
recovers ( p=0.89 and 0.67 vs. naive), even though probe_gated re-surfaces the plan 6.1
8
