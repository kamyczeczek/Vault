---
type: Concept
id: 01_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 2/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

bution shifts analogous to the sim-to-real gap in
robotics (Tobin et al., 2017). As a result, a frozen
world model (Figure 1(a)) suffers from such distri-
bution shifts and can mispredict future transitions.
At the same time, absorbing each mismatch through
gradient-based parameter updates (Figure 1(b)) is
a poor fit for online deployment: such updates in-
cur high computation costs at LLM scale and can
introduce side effects such as over-editing or catas-
trophic forgetting (Zheng et al., 2023; Yao et al.,
2023b; Hartvigsen et al., 2023).
This makes self-evolution (Qiu et al., 2026; Chu
et al., 2026) a fundamental requirement for de-
ployed world models (Figure 1(c)): they should
detect mismatches between predicted and observed
outcomes and adapt accordingly. Meanwhile, the
agent-environment loop already exposes reusable
evidence: realized transitions record what actu-
ally happened, while prediction-observation mis-
matches indicate what the world model misunder-
stood. Retaining these signals as explicit context
offers an auditable alternative to repeated parame-
ter updates, so later predictions can condition on
deployment-time evidence to generate more reli-
ableforesightwithout changing model weights.
Even once such evidence is retained,foresight
remains an action-conditioning signal: once ren-
dered to the agent, it can change the next action.
Prior work shows that current agents can ignore,
misuse, or even be harmed by world-model simu-
lations (Qian et al., 2026), echoing model-based
RL evidence that learned rollouts should be trusted
selectively under model error (Janner et al., 2019).
Similarly, recent adaptive-lookahead work further
suggests that useful imagination depends on when
and how far the agent should simulate, rather than
on fixed-horizon rollouts (Liu et al., 2026). The
controlled oracle diagnostic in Figure 2 provides
supporting evidence under a fixed agent and back-
bone: noisyforesighthurts action accuracy, while
oracleforesightimproves it.
These observations motivate WORLDEVOLVER:
a standalone self-evolving world model that contin-
uously revises its deployment-time context while
the downstream agent and all model parame-
ters remain frozen. It addresses three succes-
sive deployment-time challenges through a three-
module design: grounding predictions in realized
transitions when parametric knowledge is insuffi-
cient, abstracting individual prediction-observation
mismatches into reusable knowledge, and filter-
ing unreliableforesightbefore it can condition the
ALFWorld ScienceWorld0.2
0.3
0.4
0.5Action Accuracy
0.385
0.271
0.344
0.251
0.493
0.281
No foresight Noisy foresight Perfect foresight
Figure 2: Preliminary oracle study with Gemma-4-26B-
A4B on the Word2World evaluation set (Li et al., 2025b).
The ReAct agent receives noforesight, noisyforesight,
or perfectforesight, and generated actions are scored
against teacher actions by exact action accuracy.
agent. This structure supports online adaptation.
Concretely, our proposed WORLDEVOLVER
couples three complementary mechanisms in an
executed-action-aligned loop.Episodic Memory
serves as the exploitation component that reuses
accumulated action-transition experience through
retrieval-based simulation, whileSemantic Mem-
oryacts as the exploration component that turns
prediction-observation mismatches into persistent
heuristic knowledge. To mitigate the risk of un-
reliableforesight,Selective Foresightfilters low-
confidence predictions before exposing them to the
frozen agent. Ifforesightchanges the draft action,
the world model predicts the revised action again
and, after execution, stores the realized transition
in ME and updates MS from the corresponding
prediction-observation mismatch. In summary, our
contributions are as follows:
• We introduce WORLDEVOLVER, a standalone
self-evolving world model for LLM agents that
revises the deployment-time world-model con-
text while the agent and all model parameters
remain frozen during environmental interaction.
• We instantiate this memory-centricforesight
framework as an executed-action-aligned loop
with three mechanisms: Episodic Memory re-
trieves realized transitions, Semantic Memory
accumulates mismatch-derived rules, and Selec-
tive Foresight filters unreliable predictions before
they reach the agent.
• We benchmark the WORLDEVOLVERframework
against RAWM-ϕ and ITP-I on Word2World (Li
et al., 2025b), ALFWorld (Shridhar et al., 2021),
and ScienceWorld (Wang et al., 2022), evaluat-
ing both world-model prediction alignment with
future observations and downstream planning im-
provements from the generatedforesight.
2
