---
type: Concept
id: 00_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 1/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Self-Evolving World Models for LLM Agent Planning
Xuan Zhang1 Wenxuan Zhang2 See-Kiong Ng1 Yang Deng3,∗
1National University of Singapore
2Singapore University of Technology and Design 3Singapore Management University
xuanzhang@u.nus.edu
Abstract
World models offer a principled way to
equip long-horizon LLM agents withfore-
sight: predictions of action consequences be-
fore execution. However, unreliable fore-
sight can be ignored, misused, or even de-
grade downstream decision-making. In this
paper, we introduce WORLDEVOLVER, a self-
evolving world model framework that revises
its deployment-time context while keeping the
downstream agent and all model parameters
frozen. WORLDEVOLVERintegrates three
modules: (i) Episodic Memory, which exploits
real action transitions through retrieval-based
simulation; (ii) Semantic Memory, which ex-
tracts persistent heuristic rules from prediction-
observation mismatches; and (iii) Selective
Foresight, which filters low-confidence pre-
dictions before integrating them into agent
reasoning context. We evaluate WORLDE-
VOLVERon ALFWorld and ScienceWorld, mea-
suring world model prediction accuracy on
Word2World and downstream agent success
rate on AgentBoard. Extensive experiments
show that WORLDEVOLVERachieves the high-
est prediction accuracy across three backbones
and leads other world model baselines on down-
stream agent success rate, demonstrating that
test-time memory revision enhances both pre-
dictive fidelity and planning performance.
1 Introduction
LLM agents are typically improved through mem-
ory: reusing verbal feedback, retrieved experiences,
skill libraries, or persistent context across interac-
tions (Shinn et al., 2023; Wang et al., 2024a; Packer
et al., 2023). A complementary paradigm is emerg-
ing through world models (Li et al., 2025a; Ding
et al., 2025; Maes et al., 2026), where agents im-
prove not only by recalling past interaction expe-
rience, but also by anticipating future outcomes
*Corresponding author.
(a) Frozen World Model
World Model
frozen
Agent
frozen
Environment
external world
predicted signal action
observation
(b) Offline-tuned World Model
offline trajectories
...
parameter update online deploymentdistribution
shift
(c) Self-evolving World Model
Mismatch
!=
prediction observation
revision
training
World Model
frozen
Agent
frozen
Environment
external worldaction
observation
Figure 1: Contrast of different world models. Frozen (a)
and offline-tuned (b) world models supply predictions
to the agent without revising from deployment-time in-
teraction; self-evolving (c) world models accumulate
realized transitions and evolve through mismatches be-
tween predicted and observed outcomes.
under candidate actions, analogous to learned en-
vironment models in model-based reinforcement
learning (Ha and Schmidhuber, 2018; Hafner et al.,
2025). Recent LLM-agent work follows this intu-
ition through next-state prediction for web naviga-
tion (Chae et al., 2025), one-step visual web looka-
head (Gu et al., 2025), explicit prediction before
ReAct-style action (Fu et al., 2025), and task knowl-
edge models for text-game planning (Qiao et al.,
2024). These works suggest that world-modelfore-
sightcan serve as a useful complement to memory-
based adaptation, particularly for planning and de-
cision making in long-horizon tasks.
However, the reliability offoresightis not static.
Deployed agents continually face evolving envi-
ronments and new task instances, creating distri-
1
arXiv:2606.30639v2  [cs.AI]  1 Sep 2026
