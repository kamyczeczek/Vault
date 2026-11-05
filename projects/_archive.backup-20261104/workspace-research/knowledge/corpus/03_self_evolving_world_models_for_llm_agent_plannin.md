---
type: Concept
id: 03_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 4/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Self-Evolving World Model
Memory
Semantic Memory
Episodic Memory
...
Prediction
...
Selective
Foresight
Agent
frozen
Environment
...
Mismatch
!= ...
filter action
observation
memory update
Figure 3: Overview of WORLDEVOLVER. A frozen world model produces action-conditioned predictions using
Episodic Memory for exploitation through retrieval-based simulation over previous action transitions and Semantic
Memory for exploration through persistent heuristic-rule discovery from prediction-observation mismatches. Selec-
tive Foresight filters the prediction before it conditions the frozen agent.
3.2 WORLDEVOLVER
WORLDEVOLVERaddresses a central challenge
in world-model-based agents: predicted futures
can improve decision making, but unreliablefore-
sightmay also mislead the agent. As illustrated in
Figure 3, rather than updating model parameters,
WORLDEVOLVERevolves the evidence provided
to the frozen world model at inference time.
At step t, the frozen world model Wθ is aug-
mented with a non-parametric memory store:
Mt = (M t
E, Mt
S),
where M t
E denotes Episodic Memory and M t
S de-
notes Semantic Memory. The world model con-
ditions on the current task context, observation,
candidate action, and retrieved memory to generate
predictions that are gated by confidence.
Inspired by the classical distinction between
episodic and semantic memory (Tulving, 1972),
Episodic Memory stores concrete interaction ex-
periences, while Semantic Memory stores ab-
stract, reusable knowledge. In WORLDEVOLVER,
Episodic Memory supports exploitation by re-
calling relevant transitions, whereas Semantic
Memory supports exploration and uses prediction-
observation mismatches as its update signal.
Episodic MemoryEpisodic Memory stores con-
crete interaction experiences. The key intuition is
that previous transitions can provide useful ground-
ing for predicting what may happen after a similar
action in the current environment state. Prior work
on language-agent memory shows that retrieved
trajectories and replayed experiences can improve
decision making by grounding new actions in previ-
ous interactions rather than relying only on abstract
instructions. The episodic memory contains real-
ized transitions M t
E ={(o i, ai, oi+1)}i<t. Given
a candidate action at and retrieval size kME, it re-
trieves thek ME most similar past transitions:
M t
E,kME
(at) = TopK
kME
(oi,ai,oi+1)∈M t
E
sim(at, ai).
It then renders each selected item as raw text con-
taining the previous observation, action, and next
observation in the context. The similarity function
sim is defined as the Jaccard score over the open-
vocabulary action token set. Since new memory
records are appended only after execution, retrieval
at step t only relies on previously accumulated ex-
perience, with the episodic memory updated as
M t+1
E =M t
E ∪ {(ot, at, ot+1)}.
Semantic MemoryThe semantic memory con-
verts prediction-observation mismatches into per-
sistent textual heuristics without updating model
parameters. Instead of treating mismatches as fail-
ures of the world model weights, we interpret them
as feedback on the contextual memory. Such mis-
matches provide correction evidence for improving
future simulations. We store these corrections as
M t
S ={(r i, ei)}
|M t
S |
i=1 , where each ri is a heuristic
rule with evidence scoree i ∈R.
Before applying the textual revision, we first
compare predictions and observations in a factor-
ized state space. The key comparison is therefore
not whether two observations share the same sur-
face wording, but whether they describe the same
objects, relations, and actions. For example, the
observation“The fridge 1 is open. In the fridge 1,
you see an apple 1. ”can be factorized into tuples
4
