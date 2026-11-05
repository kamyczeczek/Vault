---
type: Concept
id: 08_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 9/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
planning with external tools (Ruan et al., 2023; Kong et al., 2023). All of these approaches can
be viewed as implementing a form of controlled, or ‘system 2’, processing (as contrasted with au-
tomatic, or ‘system 1’, processing) (Schneider & Shiffrin, 1977; Sloman, 1996; Kahneman, 2011).
Our approach has a similar high-level motivation, and shares some components with other black box
approaches (e.g., tree search (Yao et al., 2023)), but also introduces a number of new components
(error monitoring, task decomposition, task coordination, state/action distinction), and combines
these components in a novel manner (see Section A.2 for further discussion).
There have also been a number of proposals for incorporating modularity into deep learning sys-
tems, including neural module networks (Andreas et al., 2016), and recurrent independent mecha-
nisms (Goyal et al., 2019). Ours is distinguished from these approaches by the use of black-box
modules that perform specific high-level functions (many of which are inspired by formal theories
of decision-making, as discussed below), rather than merely incorporating a general bias toward
modularity.
Our approach is inspired by formal theories of decision-making and planning, and has a particu-
larly close connection to reinforcement learning (RL) (Sutton & Barto, 2018). In particular, many
of the modules in the MAP algorithm are closely related to aspects of traditional RL algorithms.
Specifically, theActorandEvaluatormodules bear some resemblance to the actor and the critic
in the popular actor-critic framework (Barto et al., 1983), and the TaskDecomposer is related to
hierarchical RL (Sutton et al., 1999; Dietterich, 2000; Bacon et al., 2017), in which temporal ab-
stractions are learned to achieve subgoals. ThePredictoris also closely related to the world model
that can substitute for direct interation with the environment in model-based RL (Sutton & Barto,
2018; Daw, 2012). An important difference in each of these cases is that the modules in MAP only
receive a task description and a couple of examples, relying on the general-purpose knowledge of the
LLM to effectively perform the task, rather than being trained through RL. This also distinguishes
the approach from other recent efforts to combine LLMs and RL (Carta et al., 2023; Zhou et al.,
2024; Zhai et al., 2024), which involve training with RL through direct interaction with an external
environment, whereas MAP generates plans internally. Finally, there are also some modules that
have no obvious analog in previous RL algorithms, but which were necessitated by weaknesses that
LLMs display in the planning domain. These include theMonitor, which was necessitated by the
tendency of LLMs to hallucinate or violate task constraints, and theOrchestrator, which allows
MAP to autonomously determine when a goal has been achieved (without groundtruth evaluation)
and thus terminate planning.
6 CONCLUSION AND FUTURE DIRECTIONS
In this work, we have proposed the MAP architecture, a modular agentic approach aimed at improv-
ing planning with LLMs. In experiments on four challenging domains, we found that MAP signif-
icantly improved multi-step planning and decision-making performance over other LLM methods
(e.g., Chain of Thought, Multi-Agent Debate, Tree of Thought). While these results represent a
significant step forward, there is still room for improvement. In particular, while improving per-
formance significantly, the model still has less than optimal performance on Tower of Hanoi, the
Reward Revaluation graph traversal task, and the PlanBench benchmark (Valmeekam et al., 2023)
(see Section A.6 for discussion of failure modes). This may be due in part to the inherent limita-
tions of prompting and in-context learning as methods for the specialization of MAP’s modules. A
promising avenue for further improvement may be to jointly fine-tune smaller open-source LLMs
to serve as modules across a range of diverse tasks, rather than relying only on black box methods
(as with GPT-4). This approach would also eliminate the need for task-specific prompts, and may
further improve zero-shot planning on novel tasks.
An additional limitation of the current implementation is the computational cost incurred by the
model (see Section A.8). Although this aligns well with the deliberative nature of controlled (i.e.,
‘system 2’) processes (Kahneman, 2011), it would nevertheless be desirable to find ways to reduce
these costs. In Section A.8, we present results from a version of MAP that achieves significantly
improved efficiency, while retaining the same level of performance, by caching and re-using the
outputs of some modules. We also found that MAP is effective when used with a smaller model
(Llama3-70B), though performance was not as strong as the version that used GPT-4. Further im-
9
