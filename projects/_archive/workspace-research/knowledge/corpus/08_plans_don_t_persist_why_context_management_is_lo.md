---
type: Concept
id: 08_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 9/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
Full
context
Naive
eviction
Plan
protected
Probe
gated
0
20
40
60T ask success (%)
56.7%
22.0% 20.7%
24.7%
naive eviction
-34.7pp
plan-aware policies
do not recover
Context compression stress test
Figure 4: Context-compression stress test on 30 ALFWorld tasks and 5 runs per task. Naive
eviction sharply reduces task success, while two plan-aware policies do not recover perfor-
mance at the same context budget. Error bars show standard errors.
times per run. The likely reason: at keep_recent=4 the evicted context is mostly recent
observations and actions, the working state the agent needs, which re-surfacing a stale plan
does not restore. So the lesson is sharper than “protect the plan”: plan tokens are unsafe
to drop, but plan-protection alone is not a compression fix; plan-fidelity monitoring is a
diagnostic, not a turnkey eviction policy.
9 Discussion and Limitations
Implications for context management.The plan is a case study in a general question:
which tokens an agent can safely drop. The same replay-pairing test applies to other tokens
that may live only in context, such as safety instructions, constraints, and tool schemas.
Reasoning models add a second mechanism: their <think> traces re-derive plan content
step by step, partially substituting for keeping the plan in the window (and why naive
replay pairing under-counts on them). Since probe-gated re-surfacing did not recover the
static-plan loss (§8), whether such a self-refreshing scratchpad survives compression better
than a static block is an open question we hope this workshop takes up.
What we do not establish.The contribution is methodological and representational, not
behavioral. Open controls remain: plan-content specificity vs. position/length/discourse;
whether the orthogonal R1 direction is a distinct concept or a rotated encoding; strict
stripping specificity; a keep_recent budget sweep; probe causality beyond step index at
scale (n≥100); and replication beyond our models and domains.
References
Emmanuel Ameisen, Tom Conerly, et al. Circuit tracing: Revealing computational graphs in
language models.Anthropic Research Blog, 2025.
Nora Belrose, Zach Furman, Logan Smith, Danny Halawi, Igor Ostrovsky, Lev McKinney,
Stella Biderman, and Jacob Steinhardt. Eliciting latent predictions from transformers with
the tuned lens.arXiv preprint arXiv:2303.08112, 2023.
Collin Burns, Haotian Ye, Dan Klein, and Jacob Steinhardt. Discovering latent knowledge in
language models without supervision.arXiv preprint arXiv:2212.03827, 2023.
Chen et al. Tracing the traces: Latent temporal signals for efficient and accurate reasoning.
arXiv preprint arXiv:2510.10494, 2025.
DeepSeek-AI. DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement
learning.Nature, 2025.
Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian,
Ahmad Al-Dahle, Aieleen Letman, Akhil Mathur, Alan Schelten, Amy Yang, et al. The
Llama 3 herd of models.arXiv preprint arXiv:2407.21783, 2024.
9
