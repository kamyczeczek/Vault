---
type: Concept
id: 04_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 5/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

such as(‘fridge 1’, ‘is’, ‘open’)and(‘apple 1’, ‘in’,
‘fridge 1’). Following Hao et al. (2023) and Shen
et al. (2026), we use a mapping function g to trans-
form raw observation text into factorized tuples,
producing ˆzt+1 =g(ˆot+1) and zt+1 =g(o t+1).
The revision process therefore follows the pipeline
(st, at)
Wθ
− − →ˆot+1,
(ˆot+1, ot+1)
g
− →(ˆzt+1, zt+1) LLM critic− − − − − − →ri,
where the final stage produces textual feedback on
the contextual memory rather than updating the
world model parameters. When ˆzt+1 ̸=z t+1, the
mismatch is treated as a failure case, and the LLM
critic transforms it into candidate textual rules ri.
Each rule is associated with an evidence score ei,
initialized to 1, which is updated by ±1/|MS| de-
pending on whether the rule is supported or contra-
dicted by the factorized-tuple comparison on sub-
sequent observations. Only rules with ei >0 are
added to the context. The resulting rule-evidence
pairs are collected as ∆M t
S, and the semantic mem-
ory is updated incrementally as
M t+1
S =M t
S ∪∆M t
S.
Following batch semantic-gradient updates for
language-based agent systems (Wang et al., 2024b),
Semantic Memory can accumulate a mini-batch of
kMS mismatch cases before revising the rendered
rule set. In this variant, the LLM critic produces
∆M t
S as the aggregated rule-evidence updates over
the mini-batch of mismatches. Thus, Semantic
Memory is the exploration branch: it turns failures
into inspectable prompt-level knowledge without
gradient updates toW θ.
Selective ForesightAlthough memory can im-
prove prediction quality, unreliableforesightmay
still mislead the downstream agent. As shown in
Figure 2, noisy predictions can degrade decision
making more than providing noforesightat all (Jan-
ner et al., 2019; Qian et al., 2026). This raises a
practical question: should the agent always trust the
predicted future, or should unreliable predictions
be filtered before they influence action selection?
Selective Foresight addresses this problem by
exposing only sufficiently confident predictions to
the agent policy. Suppose the world model gener-
ates a predicted observation sequence tokenized as
y1:n. When token probabilities are available from
the backend model, we first compute the average
Algorithm 1 WORLDEVOLVERUpdate
Input:agent-visible state st, observation ot, policy πθ,
world model Wθ, memories M t
E, Mt
S, retrieval size kME ,
semantic batch sizek MS , thresholdτ.
Output:executed action at and updated memories
M t+1
E , Mt+1
S .
// Draft and predict
1: Sample draft actiona (0)
t ∼π θ(· |st).
2: Retrieve M t
E,kME
(a(0)
t ) from M t
E by action-
token Jaccard score.
3: Query Wθ on (st, a(0)
t , Mt
E,kME
(a(0)
t ), Mt
S) to
obtain(ˆot+1, qt).
// Selectiveforesight
4: SetF t ←ˆot+1 ifq t ≥τ; otherwiseF t ←∅.
5: Samplea (1)
t ∼π θ(· |st, Ft).
6: Set executed actiona t ←a (1)
t .
// Align prediction with executed action
7: If at ̸=a (0)
t , obtain a new ˆot+1 by querying Wθ
on(s t, at, Mt
E,kME
(at), Mt
S).
// Execute and update memory
8: Execute at in the environment and observeot+1.
9: SetM t+1
E ←M t
E ∪ {(ot, at, ot+1)}.
10: Compute or accumulate ∆M t
S of size kMS from
(ˆot+1, ot+1)and updateM t+1
S .
11: Returna t, Mt+1
E , Mt+1
S .
token-level log probability:
ℓt = 1
n
Xn
i=1
logp θ(yi |y <i, st, at, Mt),
and convert it into a normalized confidence score:
qt = exp(ℓ t)∈(0,1] . This score corresponds to
the geometric mean token probability of the output.
The final agent-visibleforesightis defined as
Ft =
(
ˆot+1, q t ≥τ,
∅, q t < τ,
whereτdenotes the confidence threshold.
Selective Foresight therefore acts as an absten-
tion mechanism based on prediction confidence,
reducing the risk that unreliable simulations nega-
tively influence downstream decision making.
3.3 Agent Planning with World Models
Algorithm 1 shows one closed-loop planning step.
The agent (1) samples a draft action a(0)
t from the
frozen policy, (2) retrieveskME episodic transitions
for this action, and (3) asks the frozen world model
to predict the consequence of a(0)
t under the cur-
rent memory context. Selective Foresight then (4)
converts the prediction into an agent-visible signal:
the predicted observation is passed to the policy
only when its confidence qt exceeds the threshold
τ; otherwise, noforesightis provided to the policy.
The agent policy subsequently (5-6) samples the
executed actiona t =a (1)
t conditioned on(s t, Ft).
5
