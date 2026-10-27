---
type: Concept
id: 08_enhancing_llm_based_agents_via_global
title: "Enhancing LLM-Based Agents via Global (part 9/13)"
source: "Enhancing LLM-Based Agents via Global.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

4.2.3 Case Study
Figure 2 presents a specific example of the competitive agent frameworks in our experi-
ment, including ReAct, CodeAct, and GoalAct, with GLM-4-Plus as the base LLM. We
observe that ReAct has restricted action space due to the text or json formats and its
tendency to repeatedly attempt solutions, often getting stuck in local branches. Code-
Act leverages code to express complex logic, which enhances its action space. However,
its approach of invoking multiple tools within a single piece of code introduces exe-
cution difficulties, as each tool’s output may contain uncertainties. In contrast, our
proposed method, GoalAct, effectively avoids the local branch issue by implementing
a global planning strategy. Additionally, its hierarchical execution mechanism enables
the agent to flexibly choose appropriate skills based on task complexity, utilizing
searching for simpler tasks and coding for more complex ones. These observations
demonstrate that GoalAct offers superior performance and greater generalizability.
5 Conclusion
This paper presents GoalAct, which enhances LLM-based agents by integrating global
planning and hierarchical execution. Experimental results on the LegalAgentBench
benchmark demonstrate that GoalAct achieves state-of-the-art (SOTA) performance,
with an average improvement of 12.22% over existing methods. In the future, GoalAct
can be integrated with mechanisms such as agent reflection [23] and memory [24] to
facilitate the development of more advanced and intelligent agent systems.
References
[1] Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z., Tang, J.,
Chen, X., Lin, Y., et al.: A survey on large language model based autonomous
agents. Frontiers of Computer Science 18(6), 186345 (2024)
[2] Lai, H., Liu, X., Iong, I.L., Yao, S., Chen, Y., Shen, P., Yu, H., Zhang, H., Zhang,
X., Dong, Y., et al.: Autowebglm: A large language model-based web navigating
agent. In: Proceedings of the 30th ACM SIGKDD Conference on Knowledge
Discovery and Data Mining, pp. 5295–5306 (2024)
[3] Schick, T., Dwivedi-Yu, J., Dess ` ı, R., Raileanu, R., Lomeli, M., Hambro, E.,
Zettlemoyer, L., Cancedda, N., Scialom, T.: Toolformer: Language models can
teach themselves to use tools. Advances in Neural Information Processing Systems
36, 68539–68551 (2023)
[4] Achiam, J., Adler, S., Agarwal, S., Ahmad, L., Akkaya, I., Aleman, F.L., Almeida,
D., Altenschmidt, J., Altman, S., Anadkat, S., et al.: Gpt-4 technical report.
arXiv preprint arXiv:2303.08774 (2023)
[5] Liu, A., Feng, B., Xue, B., Wang, B., Wu, B., Lu, C., Zhao, C., Deng,
C., Zhang, C., Ruan, C., et al.: Deepseek-v3 technical report. arXiv preprint
arXiv:2412.19437 (2024)
9
