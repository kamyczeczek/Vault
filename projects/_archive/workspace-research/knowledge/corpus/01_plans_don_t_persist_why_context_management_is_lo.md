---
type: Concept
id: 01_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 2/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
the window and be re-read each step (context-time). While the plan text stays visible, both
mechanisms produce the same actions. They differ only once the text leaves the window,
which is exactly where context compression, summarization, and KV-cache eviction operate.
To separate the two, we use replay pairing (Figure 1). For each trajectory we run two
matched conditions: A keeps the plan in history; B replays the same trajectory with the
plan removed. The plan-fidelity signal is the cosine distance between the two hidden states
at each step. It measures how much the hidden state changes when the plan is taken out
of history. This signal also mixes in position, history length, and discourse structure (§3);
length- and content-matched controls are the main follow-up (§9).
In a Llama-3.1-70B ReAct agent on ALFWorld (Shridhar et al., 2020), the plan signal jumps
to 0.453 at step +1, drops 4.1× in one action-observation cycle, and settles near 0.027 by
step+5. HotpotQA drops even faster (12.4×). A Ridge probe at the peak layer (L32) predicts
the signal at R2 = 0.875, separates active from decayed plans at AUROC 0.999, and transfers
to HotpotQA with no retraining. One caveat: step index is also almost perfectly decodable
here (R2=0.978 at L32), so part of the AUROC reflects trajectory phase, not plan content.
We have not run the mixed-effects control that would separate the two (§5). The headline
reading holds either way: the plan-presence signal is a context-window effect that fades
within a step, not a state the agent keeps.
Reasoning-trace contamination.Reasoning models emit <think>. . .</think> traces before
each action (DeepSeek-AI, 2025). Run unchanged on DeepSeek-R1-Distill-Llama-70B, replay
pairing makes the step+1 signal look 4.5× smaller than Llama’s (0.022 vs. 0.099), as if R1
barely encodes the plan. This is a measurement artifact. The model re-states plan content
inside prior <think> blocks, and standard stripping leaves those blocks in place, so both
conditions still carry the plan and the distance under-counts. Strict stripping removes prior
<think> blocks from condition B only. It recovers +163% in-sample, +153% held-out, and
changes Llama’s signal by just +4.8%. The Llama-trained L32 probe on R1 strict-stripped
states (n=19) reaches AUROC 0.748 (p=6×10−4); R1 self-probes reach 1.000 on two distilled
families, along a direction 89.3◦ from Llama’s.
Scope.The claims are representational, not behavioral: strict stripping has small, non-
significant task-success effects, and uniform L32 steering is a null. Content-specific controls
and stronger causal tests remain future work.
Contributions.
1. Evidence that the plan is a context-time object: in standard LLMs it decays 4-
12× within one step out of hidden state, with cross-domain and within-family
replication.
2. A compression stress test: naive plan eviction cuts ALFWorld success by 34.7pp,
and probe-gated re-surfacing doesnotrecover it (§8).
3. Replay pairing as a measurement method, plus thereasoning-trace confoundand
strict stripping fix, which recovers +163% of step+1 signal on R1 and is a verified
no-op on non-reasoning Llama.
4. Probe-transfer and self-probe evidence that corrected hidden states carry plan-
related signal, with R1 using a different hidden-state direction from Llama.
2 Related Work
Context-time vs. weight-time memory.A growing line of work asks where information
a model uses actually resides: incontext-timememory (text in the window, supplied at
inference) orweight-timememory (absorbed into parameters). Retrieval-head analysis
shows that long-context factuality is carried by a small set of attention heads that copy
from the window rather than from parameters (Wu et al., 2024); multi-turn studies find
that models “get lost” when relevant content is distributed across turns instead of re-stated
(Laban et al., 2025). Context compression, summarization, and KV-cache eviction all bet that
some tokens can be dropped without changing behavior. Our plan-fidelity measurement
is a direct test of that bet for one important token type: it asks whether the plan is re-read
2
