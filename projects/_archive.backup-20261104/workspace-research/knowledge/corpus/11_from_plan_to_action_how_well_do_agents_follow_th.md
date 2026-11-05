---
type: Concept
id: 11_from_plan_to_action_how_well_do_agents_follow_th
title: "From Plan to Action: How Well Do Agents Follow the Plan? (part 12/13)"
source: "From Plan to Action How Well Do Agents Follow the Plan"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

From Plan to Action: How Well Do Agents Follow the Plan? ASE ’26, October 12–16, 2026, Munich, Germany
Devstral-small GPT5-mini DeepSeek-V3 DeepSeek-R1
Figure 18: Phase flow analysis under Standard plan for SWE-bench Pro (L ★(Φ)= N R P V).
Figure 19: Compliance metrics on SWE-bench Verified deter-
ministic (a) and SWE-bench Pro (b)
SAGE [13] shows that plans distilled from prior executions can
guide future behavior and improve performance on software en-
gineering tasks. While these approaches demonstrate the benefits
of planning, they primarily evaluate success at the task level and
implicitly assume that agents will follow the generated or provided
plans during execution. Jia et al. [15] assess whether a web agent’s
actions align with its stated plan using LLM-based judges. However,
this approach relies on costly and potentially unstable LLM scoring,
limiting its scalability. In contrast, our work introduces mathe-
matically defined plan compliance metrics that enable systematic
analysis of agent behavior under controlled plan variations.
8 Threats to Validity
External Validity.We evaluate four models and conduct experi-
ments on two different benchmarks, which consist of real-world
GitHub issues and differ in task composition, providing comple-
mentary evaluation settings. We use a structured plan common
among several programming agents (e.g., mini-SWE-agent, Trae
agent, OpenHands) as the standard plan to avoid bias and to be
representative of common practice.
Internal Validity.To minimize the impact of nondeterminism of
agents, we use a consistent default configuration across all experi-
ments and repeat each experiment three times, focusing on stable
behavioral patterns rather than random artifacts.
Construct Validity.Our analysis relies on a phase-level abstrac-
tion of trajectories, which may omit fine-grained or project-specific
actions. However, it captures the core problem-solving stages that
determine plan compliance: navigation, reproduction, patching, and
validation. Our pipeline is built on top of peer-reviewed artifacts
and is validated with well-vetted tools. We distinguish between
key variations, such as newly generated tests and regression tests.
Remaining low-level differences are treated as general actions and
do not affect the main conclusions.
9 Discussion
Generalization to Other Domains.Although this work focuses
on programming agents, our process-centric analysis is not limited
to software engineering. Applying it to another domain requires
defining a domain-specific plan-phase vocabulary and mapping
agent actions to these phases. The computation of plan compliance
metrics remains unchanged. For example, a scientific discovery
agent following an Observation-Research-Hypothesis-Experiment-
Analysis workflow [35] can be represented using the corresponding
phase alphabet, with actions mapped through predefined rules or
an LLM-based classifier. Controlled plan variations, such as phase
removal and periodic reminders, can similarly be adapted to other
domains, whereas plan augmentation requires domain knowledge
to introduce task-relevant phases. Thus, our framework provides
a general methodology for studying how instructed plans shape
agent behavior and task success across domains.
Implications for Agent Design and Training.Our findings sug-
gest that plan compliance should serve as a process-level signal
rather than a maximized objective. Strict compliance is neither
necessary nor always beneficial: agents may productively adapt
an instructed plan to the task, whereas missing phases, harmful
reordering, or loss of plan awareness can hinder successful exe-
cution. During execution, compliance signals can support online
monitoring and trigger targeted reminders or adaptive plan refine-
ment when harmful deviations emerge. During post-training, they
can provide process-level supervision for teaching agents to fol-
low task-appropriate plans while retaining the flexibility to adapt,
rather than memorizing fixed workflows or optimizing solely for
task success. This analysis can also support long-term monitoring
as models, scaffolds, and task distributions evolve.
10 Conclusion
This paper analyzes 21,120 trajectories to assess plan compliance in
programming agents. It introduces novel plan compliance metrics
and runs agents under a variety of plans. It also evaluates the impact
of different system-prompt plans on the agent’s success in the issue-
resolution task. We find that while plans clearly matter for task
success, agents often struggle to comply with them. This highlights
the potential to further boost agent performance in future work via
better plans and/or improved plan compliance.
11 Data Availability Statement
The artifacts of this paper are publicly available at [22].
Acknowledgments
This work is supported by NSF CCF-2238045 and IBM-Illinois Dis-
covery Accelerator Institute (IIDAI) grants. We thank anonymous
reviewers for their thoughtful comments and feedback.
