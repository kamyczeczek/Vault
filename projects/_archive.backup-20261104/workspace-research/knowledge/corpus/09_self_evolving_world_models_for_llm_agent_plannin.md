---
type: Concept
id: 09_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 10/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Limitations
Evaluation ScopeTo simplify evaluation and
isolate the effects of deployment-time world-model
revision from downstream agent behavior, we con-
duct experiments in two controlled long-horizon
text environments, ALFWorld and ScienceWorld.
This setting allows us to focus specifically on
world-modelforesightand online adaptation, but
does not cover broader domains such as web nav-
igation, code generation, robotics, or multimodal
interaction. Extending WORLDEVOLVERto these
settings is a natural direction for future work.
Confidence EstimationOur foresight filtering
mechanism relies on prediction confidence signals
derived from token-level probabilities, which may
not be available in some closed-model APIs. In
such settings, alternative confidence estimators,
such as self-consistency or learned calibration mod-
els, would be required. In addition, the current
dynamic filtering strategy assumes that prediction
confidence correlates with prediction accuracy, as
supported by Figure 13, but this relationship can
vary across environments and backbone models.
We leave more robust confidence estimation and
adaptive filtering mechanisms to future work.
Ethical Considerations
Our code implementation is available at https:
//github.com/magicgh/WorldEvolver. ALF-
World (Shridhar et al., 2021), ScienceWorld (Wang
et al., 2022), and the Word2World benchmark (Li
et al., 2025b) are publicly available for research
use. AI assistance was used as auxiliary support
for coding and paper writing; all research decisions
and claims are the authors’ own.
Acknowledgments
This research/project is supported by the National
Research Foundation, Singapore under its National
Large Language Models Funding Initiative (AISG
Award No: AISG-NMLP-2024-002), and the Sin-
gapore Ministry of Education (MOE) Academic
Research Fund (AcRF) Tier 1 grant (Proposal ID:
24-SIS-SMU-002). Any opinions, findings and
conclusions or recommendations expressed in this
material are those of the author(s) and do not re-
flect the views of National Research Foundation,
Singapore.
References
Charles Blundell, Benigno Uria, Alexander Pritzel,
Yazhe Li, Avraham Ruderman, Joel Z. Leibo,
Jack Rae, Daan Wierstra, and Demis Hassabis.
2016. Model-free episodic control.arXiv preprint
arXiv:1606.04460.
Hyungjoo Chae, Namyoung Kim, Kai Tzu-iunn Ong,
Minju Gwak, Gwanwoo Song, Jihoon Kim, Sungh-
wan Kim, Dongha Lee, and Jinyoung Yeo. 2025.
Web agents with world models: Learning and lever-
aging environment dynamics in web navigation. In
The Thirteenth International Conference on Learning
Representations (ICLR).
Minghao Chen, Yihang Li, Yanting Yang, Shiyu Yu,
Binbin Lin, and Xiaofei He. 2024. AutoManual:
Constructing instruction manuals by LLM agents via
interactive environmental learning. InAdvances in
Neural Information Processing Systems (NeurIPS).
Zhaorun Chen, Zhuokai Zhao, Kai Zhang, Bo Liu,
Qi Qi, Yifan Wu, Tarun Kalluri, Sara Cao, Yuan-
hao Xiong, Haibo Tong, Huaxiu Yao, Hengduo Li,
Jiacheng Zhu, Xian Li, Dawn Song, Bo Li, Ja-
son Weston, and Dat Huynh. 2025. Scaling agent
learning via experience synthesis.arXiv preprint
arXiv:2511.03773.
Meng Chu, Xuan Billy Zhang, Kevin Qinghong Lin,
Lingdong Kong, Jize Zhang, Teng Tu, Weijian Ma,
Ziqi Huang, Senqiao Yang, Wei Huang, Yeying Jin,
Zhefan Rao, Jinhui Ye, Xinyu Lin, Xichen Zhang,
Qisheng Hu, Shuai Yang, Leyang Shen, Wei Chow,
and 23 others. 2026. Agentic world modeling:
Foundations, capabilities, laws, and beyond.arXiv
preprint arXiv:2604.22748.
Yang Deng, Xuan Zhang, Wenxuan Zhang, Yifei Yuan,
See Kiong Ng, and Tat-Seng Chua. 2024. On the
Multi-turn instruction following for conversational
web agents. InProceedings of the 62nd Annual Meet-
ing of the Association for Computational Linguistics
(Volume 1: Long Papers), pages 8795–8812.
Hang Ding, Peidong Liu, Junqiao Wang, Ziwei Ji, Meng
Cao, Rongzhao Zhang, Lynn Ai, Eric Yang, Tianyu
Shi, and Lei Yu. 2026. DynaWeb: Model-based
reinforcement learning of web agents.arXiv preprint
arXiv:2601.22149.
Jingtao Ding, Yunke Zhang, Yu Shang, Yuheng Zhang,
Zefang Zong, Jie Feng, Yuan Yuan, Hongyuan Su,
Nian Li, Nicholas Sukiennik, Fengli Xu, and Yong
Li. 2025. Understanding world or predicting future?
a comprehensive survey of world models.ACM Com-
puting Surveys, 58(3):1–38.
Tianqing Fang, Hongming Zhang, Zhisong Zhang,
Kaixin Ma, Wenhao Yu, Haitao Mi, and Dong Yu.
2025. WebEvolver: Enhancing web agent self-
improvement with coevolving world model. InPro-
ceedings of the 2025 Conference on Empirical Meth-
ods in Natural Language Processing (EMNLP).
10
