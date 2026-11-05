---
type: Concept
id: 02_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 3/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

2 Related Work
World Models For LLM Agents.World-model
foresightextends the model-based reinforcement
learning lineage (Ha and Schmidhuber, 2018;
Hafner et al., 2025) to language agents. Ex-
isting systems instantiate this idea by using an
LLM as both planner and simulator (Hao et al.,
2023), training next-state predictors for web navi-
gation (Chae et al., 2025), adding explicit predic-
tion before action (Fu et al., 2025), or learning
task-level world knowledge for text-game plan-
ning (Qiao et al., 2024). Other work improves
foresightthrough offline training or joint optimiza-
tion, such as co-training agents and world mod-
els (Fang et al., 2025), retrieval-augmented world
model learning (Yang et al., 2025), and synthetic-
environment training (Ding et al., 2026). RAWM-ϕ
retrieves from a fixed transition library with a PPO-
trained head (Yang et al., 2025). AutoManual con-
structs an online manual for the planner (Chen et al.,
2024), while WALL-E 2.0 builds symbolic transi-
tion knowledge for model-predictive control (Zhou
et al., 2025). Imagine-then-Plan adapts the imagi-
nation horizon (Liu et al., 2026). A complementary
lesson from episodic-control and language-agent
memory systems is that accumulated interaction
experience can ground later decisions through re-
trieved histories (Blundell et al., 2016; Pritzel et al.,
2017; Deng et al., 2024; Zheng et al., 2024; Zhong
et al., 2024; Zhou et al., 2024; Liu et al., 2025).
WORLDEVOLVERstarts with empty memory, accu-
mulates executed transitions and mismatch-derived
textual rules online without parameter updates,
confidence-gates one-step predictions, aligns mem-
ory updates with the executed action, and leaves
the downstream policy frozen.
Self-Evolution.Recent work increasingly studies
self-evolving agents, where interaction improves
behavior through verbal feedback, skill libraries,
distilled experience, or persistent context (Wang
et al., 2024a; Packer et al., 2023; Zhao et al., 2024).
A growing line offullyautonomous approaches
removes human supervision and bootstraps agents
from zero or minimal data. Challenger-solver
methods co-evolve a task proposer and a solver,
with the proposer generating increasingly difficult
tasks (Huang et al., 2025; Yu et al., 2025; Xia et al.,
2025; Yue et al., 2026). WebRL instead adapts
an online curriculum from the web agent’s current
performance (Qi et al., 2025). Early Experience
and DreamGym improve agents by collecting or
synthesizing interaction data (Zhang et al., 2025a;
Chen et al., 2025), while Co-Evolving Agents and
CURE use failures or mutual evaluation to improve
specialized learners (Jung et al., 2025; Wang et al.,
2025). Several works also couple agents with co-
evolving task generators or environment simulators
that adapt to the agent’s frontier (Guo et al., 2025).
Closer to our setting, a few recent efforts begin to
evolve a learned world model alongside the agent,
either by retraining it on environment rollouts via
self-supervised RL (Yu et al., 2026; Ding et al.,
2026), dynamically updating an abstracted state
model during exploration (Kim and Hwang, 2025),
or alternating updates between neural and symbolic
components (Zhao et al., 2026). However, most ex-
isting methods evolve the agent policy or external
context, rather than the world model that supports
future prediction. As a result, they do not directly
address how predictive models should adapt under
changing environments or unreliableforesight.
3 Methodology
3.1 Problem Formulation
We formulate each task as a partially observed in-
teraction process (S,A,O,T) , where S is the en-
vironment state space, A is the action space, O is
the observation space, and T:S × A → Sis the
transition function. At time step t, the agent can-
not directly access the hidden environment state.
Instead, it observes a textual interaction state:
st = (o1, a1, . . . , ot−1, at−1, ot),
where oi ∈ Oand ai ∈ Adenote observations and
actions, respectively. Given the current state st, the
agent policy generates an action:
at ∼π θ(· |st).
A world model predicts future K-step observations
from the current state and a candidate action:
(ˆot+1, . . . ,ˆot+K)∼W θ(· |st, at).
We mainly focus on one-stepforesightbecause the
next predicted observation ˆot+1 from the world
model directly influences the current action deci-
sion of the agent, while the realized observation
ot+1 immediately provides supervision on whether
the prediction was reliable. The goal is therefore to
select and improveˆot+1 through deployment-time
continual evolution, while keeping both the agent
policyπ θ and world modelW θ frozen.
3
