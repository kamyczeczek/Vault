---
type: Concept
id: 05_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 6/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

For our domains, we define a function verify:S → {0,1} , that identifies terminal states (i.e.,
verify(s) = 1ifs∈ Sterm and0otherwise). The reward function is then:
r(s,a) =
(
rsuccess ifverify(T(s ,a)) = 1(a terminal state)
rstep otherwise
where rsuccess = 1is a positive reward for task completion and rstep is a negative reward for non-terminal
steps (e.g., rstep =−0.1 ). Primitive tasks from the HTN are linked to Sterm, which can be verified using
verify.
An agent’s behavior is described by a stochastic policyπ:S ×A →[0,1], where π(s, a) =P(ai =a|s i =s)
is the probability of selecting a in state s. A solution to M is a policy π that maximizes the expected
reward (in this case a policy that reaches a terminal state in the fewest steps).
Initial Analysis. In this work, we investigate the use of an agentic LLM system as the policy π that
operates within this MDP framework. We show that divide-and-conquer mechanisms such as task
decomposition can be used to constrain π to work on smaller problems, increasing the expected reward
obtained by our agentic LLM.
The general MDP model allows us to hypothesize about why we expect this approach to work. We assume
that there exists a task-aware assembly function A:S ×K→C and let Ci be the context produced from
states i used as input to the LLM at each iteration.
Task Success Rate. A task succeeds if a terminal state s∈ Sterm is reached within H steps. Let
(a0, . . . , aH−1 ) be a sequence of actions that arrives at a terminal state from an initial state s0. As-
suming deterministic transitions, the probability of taking these actions depends solely on the LLM’s
parameterizationθ, which governs action selection:
Pθ(a0, a1, . . . , aH−1 ) =
H−1Y
i=0
Pθ(ai|Ci)
Here, Pθ(ai|Ci) represents the LLM’s conditional probability of selecting action ai given context Ci.
This factorization arises because each action depends only on the current context (Markov property).
Task Decomposition. A task decomposition splits a problem into a sequence of smaller subtasks,
(κ0, . . . , κn−1). Let Pθ(κj) be the probability of successfully completing subtask j. Decomposition
improves task success if:
Pθ(full task)<
n−1Y
j=0
Pθ(κj)
We hypothesize that we can improve the right side of this equation through contextual scaffolding. We
assume that the LLM’s ability to complete a subtask Pθ(κj) increases by reducing context complexity.
When the agent works on a specific subtask κj, the assembly function A(si, κj) generates a focused
context C ′
i,j. By constraining the problem space through reducing context complexity, the conditional
probability of selecting a correct actiona i should increase:
Pθ(ai|C ′
i,j)> Pθ(ai|Ci)
Because the probability of success for a subtask κj, Pθ(κj), is the product of the individual Pθ(ai|C ′
i,j),
the task success rateP θ(κj)will also increase.
4 ProcLLM: Embedding Procedural knowledge into an agentic LLM
ProcLLM implements a planning and acting system (8) in which an agent iterates between HTN planning,
where it updates the current (sub)task based on progress, and action execution, where it executes
primitive tasks (i.e., actions) and verifies that they are completed. Relating ProcLLM to the formalism,
we next describe the components of this system, as shown in Figure 2.
Environment and states S. For the benchmarks we study in this paper, the environment corresponds
to a file system with text files and python code files (Figure 2, bottom in yellow). The agent is provided
6
