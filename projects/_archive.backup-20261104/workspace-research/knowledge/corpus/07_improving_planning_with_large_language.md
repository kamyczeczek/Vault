---
type: Concept
id: 07_improving_planning_with_large_language
title: "Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5 (part 8/34)"
source: "IMPROVING PLANNING WITH LARGE LANGUAGE.pdf"
tags: [1, 2, agentic, agents, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Published atNature Communications(2025) https://doi.org/10.1038/s41467-025-63804-5
→mystery blocksworld (mystery BW)), and transfer between completely different tasks (ToH→
Mystery BW). We found that MAP outperformed both GPT-4 ICL and CoT in each of these settings,
indicating that MAP can improve the generalizability and robustness of planning in LLMs.
Table 3: Transfer between different planning tasks. Results reflect % solved problems.
Model n7tree→n15star Valuepath BW→Mystery BW ToH→Mystery BW
GPT-4 ICL 51 0.2 0
GPT-4 CoT 65 1.4 0
MAP 80 12.2 6.6
4.1 ABLATION STUDY
We also carried out an ablation study to determine the relative importance of each of MAP’s major
components, focusing on the 3-disk ToH problems. Figure 3 (left) shows the results. We found that
theMonitorwas the most important component, as ablating this module resulted in significantly
fewer solved problems, due primarily to an increased tendency to propose invalid moves (31% in-
valid moves vs. 0% for other ablation models). This highlights the importance of having a separate,
modularized monitoring process. Ablating the tree search andTaskDecomposermodule also re-
sulted in significantly fewer solved problems. The impaired performance following the ablation of
the tree search indicates the benefit of considering the multi-step implications of proposed actions,
rather than committing to a single action as is done in standard autoregressive methods such as chain-
of-thought. The impaired performance following the ablation of theTaskDecomposerhighlights
the benefit of decomposing a task into subgoals, which allows MAP to factorize a complex task into
a set of smaller, more manageable tasks. Overall, these results suggest that all major components
played an important role in MAP’s performance. Moreover, the improved performance was not due
entirely to the use of tree search (which is shared with tree-of-thoughts (Yao et al., 2023)), but also
depended on the incorporation of other modules such as theTaskDecomposerand especially the
Monitor.
5 RELATED WORK
Early work in AI formalized planning as a problem of search through a combinatorial state space,
typically utilizing various heuristic methods to make this search tractable (Newell & Simon, 1956;
Newell et al., 1959). Problems such as ToH figured prominently in this early research (Simon, 1975),
as it affords the opportunity to explore ideas based on hierarchical or recursive planning (in which
a larger problem is decomposed into a set of smaller problems). Our proposed architecture adopts
some of the key ideas from this early work, including tree search and hierarchical planning.
A few recent studies have investigated planning and multi-step decision making in LLMs. These
studies suggest that, although LLMs can perform relatively simple planning tasks (Huang et al.,
2022), and can learn to make more complex plans given extensive domain-specific fine-tuning (Pal-
lagani et al., 2022; Wu et al., 2023), they struggle on tasks that require zero-shot or few-shot gen-
eration of multi-step plans (Valmeekam et al., 2023; Momennejad et al., 2023). These results also
align with studies that have found poor performance in tasks that involve other forms of extended
multi-step reasoning, such as arithmetic (Dziri et al., 2023). Our approach is in large part motivated
by the poor planning and reasoning performance exhibited by LLMs in these settings.
Some recent approaches have employed various forms of heuristic search to improve performance
in LLMs (Lu et al., 2021; Zhang et al., 2023b), but these approaches have generally involved search
at the level of individual tokens. Importantly, this is in contrast to our approach, in which search is
performed at the more abstract level of task states (described in natural language). Ours is similar
to other recently proposed black-box approaches in which ‘thoughts’ – meaningful chunks of nat-
ural language – are utilized as intermediate computations to solve more complex problems. These
approaches include scratchpads (Nye et al., 2021), chain-of-thought (Wei et al., 2022b), tree-of-
thoughts (Yao et al., 2023), reflexion (Shinn et al., 2023), multi-agent methods (Du et al., 2023;
Zhang et al., 2023a), Describe-Explain-Plan-Select (Wang et al., 2023), and methods for combining
8
