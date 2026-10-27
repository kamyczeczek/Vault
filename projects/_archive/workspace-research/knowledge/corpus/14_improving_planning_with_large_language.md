---
type: Concept
id: 14_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 15/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
A.2 EXTENDEDRELATEDWORK
In this section, we consider in more detail how MAP relates to existing black-box and agentic LLM
approaches:
• Similar to MAP, both scratchpad (Nye et al., 2021) and chain-of-thought (CoT) (Wei et al.,
2022b) decompose a problem into intermediate computations. However, unlike MAP, nei-
ther scratchpad nor CoT factorize these intermediate computations into specialized mod-
ules.
• Tree-of-thought (ToT) (Yao et al., 2023) introduces some degree of factorization, but the
factorization is not as extensive as in MAP. The ‘generator’ module in ToT carries out
a combination of the functions carried out by both theActor(action proposal) and the
Predictor(prediction of the states that will result from these actions) in MAP. The ‘eval-
uator’ module in ToT carries out a combination of the functions carried out by both the
Monitor(error detection) and theEvaluator(prediction of state value) in MAP. ToT does
not contain any component that carries out the functions of theTaskDecomposer(subgoal
proposal) and theOrchestrator(autonomously determining when a goal or subgoal has
been achieved).
• Multi-agent debate (i.e., Society of Mind) (Du et al., 2023) involves the interaction of multi-
ple LLM instances; but, unlike MAP, these model instances are not specialized to perform
specific functions. Similarly, the Large Language Model-based Actor-Critic (LLaMAC)
approach (Zhang et al., 2023a) involves interaction between many LLM agents, and incor-
porates more specialization (there is a ’critic’ module that coordinates the decision-making
process across many ’actors’), though there is less module specialization than there is in
MAP.
• Similar to MAP, reflexion (Shinn et al., 2023) involves an element of self evaluation of
proposed policies, but this depends on interaction with the external environment to deter-
mine the outcome of each policy (whereas in MAP, this self evaluation process is entirely
internal to the agent). The dependence on interaction with the external environment makes
this approach unsuitable for the planning domain (planning is, by definition, performed
internally).
• Describe-Explain-Plan-Select (Wang et al., 2023) involves the coordination of multiple
modules, but the approach is specific to settings involving an agent that is spatially embed-
ded in a 2D environment. For instance, the method utilizes the spatial proximity of objects
to the agent for prioritization of subgoals. This approach cannot be directly applied to the
tasks that we consider in the present work.
• Some recent work has aimed to combine external tool use with LLM planning agents,
including Task Planning and Tool Usage (TPTU) (Ruan et al., 2023; Kong et al., 2023).
Because this work evaluates on tasks involving external tool use, it is not directly compara-
ble with our approach, but we plan to extend our approach to incorporate tool use in future.
We expect that MAP’s modular approach will afford improved performance in this domain,
relative to the more minimal planning approaches that have previously been employed (i.e.,
involving planning in a single LLM agent).
16
