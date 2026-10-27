---
type: Concept
id: 02_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 3/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Preprint.
from the window each step or held in durable state, and finds the former in standard LLMs.
The plan has no weight-time backup, which places it squarely in the context-time regime,
where eviction is unsafe.
Planning and faithfulness in LLM agents.The standard paradigm interleaves reasoning
and acting (Yao et al., 2022; Wei et al., 2022; Yao et al., 2023; Shinn et al., 2023; Huang et al.,
2022). These frameworks assume explicit plans improve behavior, which behavioral metrics
confirm, but they do not test the mechanism by which the plan influences subsequent steps.
Repeated-run studies show that multi-step agents can diverge early under identical inputs,
and that consistency can amplify both correct and incorrect interpretations (Mehta, 2026a;b).
Our work asks a complementary question: whether the plan representation itself persists
across those steps. We extend plan-faithfulness analysis to the representational level and
find that high behavioral alignment can coexist with 12×representational decay.
Hidden-state representations.LLM hidden states linearly encode many semantic properties
(Burns et al., 2023; Marks & Tegmark, 2024; Zou et al., 2023). Circuit tracing (Ameisen
et al., 2025) and the Tuned Lens (Belrose et al., 2023; nostalgebraist, 2020) look at the layer
dimension within one forward pass. Replay pairing operates on a different axis: the
temporal dimension of multi-step agent behavior. The question is how plan information
persists across forward passes.
Interventions and reasoning-model probes.Activation steering (Turner et al., 2023; Zou
et al., 2023), inference-time intervention (Li et al., 2023), and self-refinement (Madaan et al.,
2023) target hidden states or context. For reasoning models, several works probe R1 hidden
states in single-turn settings (Liu et al., 2025; Wang et al., 2025a; Chen et al., 2025); Wang et al.
(2025b) report poor instruction-following inside traces and Wu et al. (2025) propose Thinking
Intervention; Stolfo et al. (2025) apply activation differencing single-turn. The piece we add
is identifying the contamination that hits paired-trajectory methods on reasoning models in
multi-turn agent loops, and a fix.
3 Method
3.1 Agent Setup
We run two classes of model as ReAct agents (Yao et al., 2022). The non-reasoning model
is Llama-3.1-70B-Instruct (Grattafiori et al., 2024) (primary), with Llama-3.1-8B-Instruct
for within-family replication. The reasoning model is DeepSeek-R1-Distill-Llama-70B
(DeepSeek-AI, 2025), a Llama-3.1-70B base distilled from DeepSeek-R1 reasoning traces.
It produces explicit <think>. . .</think> blocks before each action. We inject a <think>\n
prefix at generation time so the reasoning trace always opens with the right tag (the Llama
chat template does not emit the opening<think>on its own).
The primary environment is ALFWorld (Shridhar et al., 2020), a text-based household
environment where the agent completes tasks by navigating rooms and manipulating
objects through a natural-language action space ( go_to, pick_up, put, heat, cool, clean,
examine). It spans six task types ranging from 3-4 to 6-8 plan steps. We use the text-only
(non-visual) variant, following standard ReAct-on-ALFWorld baselines (Yao et al., 2022).
The secondary environment is HotpotQA (Yang et al., 2018). We collect 30 trajectory pairs
using the same replay-pairing protocol (§4) and the same model and prompt configuration,
for a direct cross-domain comparison.
Models run on 8 ×H200 GPUs with pipeline parallelism. Full hidden states ( R8192) are
captured at the last token position at every forward pass.
3.2 Plan Elicitation
To study plan faithfulness we first need an explicit plan, so we inject a guard message asking
the agent for a multi-step plan:
3
