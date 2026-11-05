---
type: Concept
id: 12_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 13/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Yanzhao Zhang, Mingxin Li, Dingkun Long, Xin Zhang,
Huan Lin, Baosong Yang, Pengjun Xie, An Yang,
Dayiheng Liu, Junyang Lin, Fei Huang, and Jingren
Zhou. 2025b. Qwen3 Embedding: Advancing text
embedding and reranking through foundation models.
arXiv preprint arXiv:2506.05176.
Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu
Lin, Yong-Jin Liu, and Gao Huang. 2024. ExpeL:
LLM agents are experiential learners. InProceedings
of the AAAI Conference on Artificial Intelligence,
volume 38, pages 19632–19642.
Hongyu Zhao, Siyu Zhou, Haolin Yang, Zengyi Qin,
and Tianyi Zhou. 2026. Neuro-symbolic synergy
for interactive world modeling.arXiv preprint
arXiv:2602.10480.
Ce Zheng, Lei Li, Qingxiu Dong, Yuxuan Fan, Zhiyong
Wu, Jingjing Xu, and Baobao Chang. 2023. Can
we edit factual knowledge by in-context learning?
InProceedings of the 2023 Conference on Empiri-
cal Methods in Natural Language Processing, pages
4862–4876.
Longtao Zheng, Rundong Wang, Xinrun Wang, and
Bo An. 2024. Synapse: Trajectory-as-exemplar
prompting with memory for computer control. In
The Twelfth International Conference on Learning
Representations (ICLR).
Wanjun Zhong, Lianghong Guo, Qiqi Gao, He Ye, and
Yanlin Wang. 2024. MemoryBank: Enhancing large
language models with long-term memory. InPro-
ceedings of the AAAI Conference on Artificial Intelli-
gence.
Ruiwen Zhou, Yingxuan Yang, Muning Wen, Ying Wen,
Wenhao Wang, Chunling Xi, Guoqiang Xu, Yong Yu,
and Weinan Zhang. 2024. TRAD: Enhancing LLM
agents with step-wise thought retrieval and aligned
decision. InProceedings of the 47th International
ACM SIGIR Conference on Research and Develop-
ment in Information Retrieval (SIGIR).
Siyu Zhou, Tianyi Zhou, Yijun Yang, Guodong Long,
Deheng Ye, Jing Jiang, and Chengqi Zhang. 2025.
WALL-E 2.0: World alignment by neurosymbolic
learning improves world model-based LLM agents.
arXiv preprint arXiv:2504.15785.
A Experimental Setups
World Model BaselinesWe consider three
inference-only baselines without gradient updates:
• Zero-Shotfollows the standard zero-shot
prompting paradigm for large language mod-
els (Radford et al., 2019). The task description,
current state, and proposed action are rendered
directly as a next-observation prediction query.
• RA WM-ϕ (Yang et al., 2025) reimplements
RAWM as an offline retrieval baseline using
only the retrieval encoder; ϕ denotes the ab-
sence of RAWM’s PPO-trained MLP head, iso-
lating the in-context retrieval contribution from
the trained scoring component. It embeds
the current query (st, at) and stored transitions
(si, ai, oi+1), retrieves the most similar top-1
transition by cosine similarity from a fixed re-
trieval library, and formats them as in-context ex-
amples for prediction. We use trajectories from
the Word2World (Li et al., 2025b) test split as
the retrieval source for both world-model pre-
diction and agent planning. Retrieval is imple-
mented with Qwen3-Embedding-8B for all re-
trieval queries across both evaluated environ-
ments under the shared embedding configuration.
• ITP-I(Liu et al., 2026) is the training-free vari-
ant of Imagine-then-Plan. In the original frame-
work, adaptive lookahead operates within the
agent planning loop, where the agent selects an
imagination horizon and conditions action selec-
tion on the generated foresight. To isolate the ef-
fects of the world model while keeping the agent
fixed, we move horizon selection and imagina-
tion into the world model itself. The world model
selects k∈ {0, . . . , kmax} with kmax=5 and re-
turns the corresponding imagined future. For
prediction evaluation, ITP-I is restricted to one-
step imagination so that all methods share the
same next-observation mismatch target. Multi-
step imagination is used only in agent planning
evaluation, where the downstream agent can con-
sume longer horizon foresight during planning.
Agent PoliciesWe evaluate two representative
agent policies to test whether world-model signals
transfer reliably across different agent types.
• ReActfollows the standard thought-action inter-
action format (Yao et al., 2023a), using in-context
examples from the AgentBoard prompt.
• ReflActaugments ReAct with goal-state reflec-
tion before action selection (Kim et al., 2025).
This setting tests whether world-model predic-
tions remain beneficial when the downstream
agent already performs explicit reflection.
B Implementation Details
All generations use temperature 0, top- p sam-
pling with p=0.5, random seed 42, and a 32,768-
token context window. The mismatch critic and
factorized-tuple mapping function g share the same
13
