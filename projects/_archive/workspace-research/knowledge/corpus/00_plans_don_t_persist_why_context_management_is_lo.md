---
type: Concept
id: 00_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 1/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
Plans Don’t Persist: Why Context Management Is Load Bear-
ing for LLM Agents
Aman Mehta
Snowflake AI Research
aman.mehta@snowflake.com
Anupam Datta
Snowflake AI Research
anupam.datta@snowflake.com
Abstract
Long-horizon agents depend on context management: systems compress,
summarize, and evict old tokens so tasks can continue beyond finite win-
dows. That is safe only when dropped information is no longer needed
or has been internalized. Plans are the stress case: they are written early,
used for many steps, and first to be evicted. We introducereplay pairing,
a diagnostic that runs the same trajectory with and without the plan in
history and measures hidden-state cosine distance. On Llama-3.1-70B,
plan signal spikes to 0.453 one step after the plan, then falls 4.1 × in a
single action-observation step; HotpotQA falls 12.4 ×. This is evidence
that standard LLM agents do not carry plans forward as persistent state,
and instead depend on the plan remaining in context. A layer- L32 probe
detects this decay as a diagnostic, not as proof that it reads plan content
itself. Reasoning models add a measurement confound: their <think>
traces re-derive plan content, so standard stripping leaves plan evidence
in the stripped condition. We name this thereasoning-trace confoundand
fix it with strict stripping, which removes prior <think> blocks from the
stripped run only. It recovers +163% of the step+1 signal in-sample and
+153% held out, while not meaningfully changing non-reasoning Llama
(+4.8%). On DeepSeek-R1-Distill-Llama-70B, a Llama-trained probe trans-
fers at AUROC 0.748 ( p=6×10−4), while R1-specific probes reach 1.000,
suggesting R1 encodes plan signal in a different hidden-state direction. Fi-
nally, a compression stress test shows the practical cost: naive plan eviction
cuts ALFWorld success by 34.7pp, while probe-gated re-surfacing does not
recover it. The contribution is a measurement and stress-test framework
showing that agent-critical information can be context-resident rather than
persistent. Context management is load bearing, but plan protection alone
is not enough.
1 Introduction
Context management is becoming load-bearing for LLM agents. To run long horizons
within a finite window, deployments compress, summarize, and evict old context, betting
that dropped tokens do not change behavior. Whether that bet is safe depends on where
information lives: incontext-timememory (text in the window, re-read each step) or in
persistent internal state that survives once the text is gone. The agent’splanis the sharpest
case. It is written once, early, so it is first to be evicted. If the plan is held in internal state,
dropping its text is free; if it is only re-read each step, dropping it silently breaks an agent
that passed every behavioral test while the text was still visible. This did not matter when
contexts were short and nothing scrolled away; modern context management makes it
matter. Which mechanism holds is the question this paper answers.
Planning frameworks like ReAct (Yao et al., 2022), Chain-of-Thought (Wei et al., 2022), Tree
of Thoughts (Yao et al., 2023), and Reflexion (Shinn et al., 2023) all assume the same thing:
the agent writes a plan, and the plan guides what it does next. Behavioral alignment metrics
confirm that it does. But behavior alone cannot tell two mechanisms apart. The plan could
be held in hidden state across the trajectory (internalized), or it could live only as text in
1
arXiv:2606.22953v1  [cs.AI]  22 Jun 2026
