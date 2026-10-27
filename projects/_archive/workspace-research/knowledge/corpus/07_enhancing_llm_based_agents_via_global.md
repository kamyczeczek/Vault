---
type: Concept
id: 07_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 8/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

T able 3An ablation study was conducted to evaluate the effectiveness of GoalAct with the
GLM-4-Plus as the base LLM. The notation ‘w/o’ indicates experiments where specific
modules were removed.
Method 1-hop 2-hop 3-hop 4-hop 5-hop Writing ALL
GoalAct 0.9506 0.9187 0.8500 0.7375 0.6983 0.8643 0.8710
w/o global plan 0.9281 0.7375 0.8000 0.6208 0.6950 0.8454 0.7896
w/o searching 0.8950 0.8063 0.7500 0.6708 0.6100 0.8521 0.7906
w/o coding 0.8381 0.7833 0.6333 0.6208 0.4833 0.8447 0.7304
w/o writing 0.9381 0.9000 0.7667 0.6708 0.5767 0.8247 0.8264
improves average performance by 14.45% on GPT-4o-mini, 10.09% on Qwen-
max, and 12.11% on GLM-4-Plus , with an overall average improvement of
12.22%. These results demonstrate the broad effectiveness of GoalAct.
• The inherent limitations of various baseline methods undermine their
performance. P-S executes a static global plan, which limits its adaptability in
complex scenarios, leading to poor performance. P-E dynamically updates its global
plan, demonstrating improvements over P-S in some scenarios. However, as its global
plan does not account for task execution, the execution feasibility of its plan in some
tasks is weak, ultimately resulting in performance degradation. ReAct exhibits rel-
atively strong performance, but the absence of global planning and its reliance on
action formats constrained by text or json impose an upper bound on its effective-
ness in certain scenarios. CodeAct extends the action space through python code;
however, in complex scenarios, invoking multiple tools within a single code exe-
cution often results in errors. Moreover, experimental results show that CodeAct
performs poorly in Writing tasks, highlighting its significant limitations.
• As the task difficulty increases, the performance gain of GoalAct over
the second-best method becomes more pronounced. Specifically, the relative
improvements on average are 3.26% for 1-hop , 7.98% for 2-hop , 20% for 3-
hop, 9.86% for 4-hop , and 15.5% for 5-hop . Furthermore, in Writing tasks,
GoalAct achieves a 12.74% improvement, further validating its strong adaptability
and generalization across different task types.
4.2.2 Ablation Study
To evaluate the effectiveness ofGlobal Planning and Hierarchical Execution, we
conducted an ablation study by systematically removing key components of GoalAct
with GLM-4-Plus as the base LLM. Table 3 presents the results, from which we observe
the following: Removing the global plan reduces average performance by 8.14%,
8.04% for Searching, 14.06% for Coding, and 4.46% for W riting(with Writing
tasks specifically declining by 3.96%). These ablation results validate the rationality
of GoalAct’s design and highlight the necessity of synergy among its components to
achieve optimal performance.
8
