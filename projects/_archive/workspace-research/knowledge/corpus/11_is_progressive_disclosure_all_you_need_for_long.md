---
type: Concept
id: 11_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 12/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

for tree-organized retrieval. InThe Twelfth Inter-
national Conference on Learning Representations
(ICLR).
Simeng Sun, Yang Liu, Shuohang Wang, Dan Iter, Chen-
guang Zhu, and Mohit Iyyer. 2024. PEARL: Prompt-
ing large language models to plan and execute actions
over long documents. InProceedings of the 18th
Conference of the European Chapter of the Associ-
ation for Computational Linguistics (EACL), pages
469–486, St. Julian’s, Malta. Association for Compu-
tational Linguistics.
Yiqun Sun, Pengfei Wei, and Lawrence B. Hsieh. 2026.
Don’t retrieve, navigate: Distilling enterprise knowl-
edge into navigable agent skills for QA and RAG. In
First Workshop on Agent Skills (ACM CAIS 2026).
Non-archival.
Tencent Hy Team. 2026. Hy3. https://huggin
gface.co/tencent/Hy3. Hugging Face model
card; evaluates on SKILLSBENCH.
Thoughtworks. 2026. Progressive context disclosure.
Technology Radar, https://www.thoughtwor
ks.com/radar/techniques/progressiv
e-context-disclosure.
Virgilio Jr. 2026. book-to-skill: Turn any technical
book PDF into a claude code skill. GitHub repository
https://github.com/virgiliojr94/bo
ok-to-skill.
Cunxiang Wang, Ruoxi Ning, Boqi Pan, Tonghui Wu,
Qipeng Guo, Cheng Deng, Guangsheng Bao, Xi-
angkun Hu, Zheng Zhang, Qian Wang, and Yue
Zhang. 2025. NovelQA: Benchmarking question
answering on documents exceeding 200K tokens. In
The Thirteenth International Conference on Learning
Representations (ICLR).
Demi Wang, Lintang Sutawika, and Graham Neubig.
2026. Skill induction for code agents on web automa-
tion. InFirst Workshop on Agent Skills (ACM CAIS
2026).
Simon Willison. 2025. Claude skills are awesome,
maybe a bigger deal than MCP. Personal blog,
https://simonwillison.net/2025/O
ct/16/claude-skills/.
Renjun Xu and Yang Yan. 2026. Agent skills for large
language models: Architecture, acquisition, security,
and the path forward.Preprint, arXiv:2602.12430.
Zed Industries. 2025. Agent client protocol. https:
//agentclientprotocol.com . Protocol
specification website.
Chi Zhang, Yimin Liu, Xinze Chen, and Ping Ji. 2026.
What keeps agent skills from being reusable? evi-
dence from 138K SKILL.md files. InFirst Workshop
on Agent Skills (ACM CAIS 2026).
Xinrong Zhang, Yingfa Chen, Shengding Hu, Zi-
hang Xu, Junhao Chen, Moo Khai Hao, Xu Han,
Zhen Leng Thai, Shuo Wang, Zhiyuan Liu, and
Maosong Sun. 2024a. ∞Bench: Extending long con-
text evaluation beyond 100K tokens. InProceedings
of the 62nd Annual Meeting of the Association for
Computational Linguistics (V olume 1: Long Papers),
pages 15262–15277, Bangkok, Thailand. Association
for Computational Linguistics.
Yusen Zhang, Ruoxi Sun, Yanfei Chen, Tomas Pfister,
Rui Zhang, and Sercan O. Arik. 2024b. Chain of
agents: Large language models collaborating on long-
context tasks. InAdvances in Neural Information
Processing Systems 37 (NeurIPS).
Jun Zhao, Can Zu, Hao Xu, Yi Lu, Wei He, Yiwen
Ding, Tao Gui, Qi Zhang, and Xuanjing Huang. 2024.
LongAgent: Scaling language models to 128k con-
text through multi-agent collaboration. InProceed-
ings of the 2024 Conference on Empirical Methods
in Natural Language Processing (EMNLP), pages
16310–16324, Miami, Florida, USA. Association for
Computational Linguistics.
Chenyu Zhou, Huacan Chai, Wenteng Chen, Zihan
Guo, Rong Shan, Yuanyi Song, Tianyi Xu, Yingx-
uan Yang, Aofan Yu, Weiming Zhang, Congming
Zheng, Jiachen Zhu, Zeyu Zheng, Zhuosheng Zhang,
Xingyu Lou, Changwang Zhang, Zhihui Fu, Jun
Wang, Weiwen Liu, and 2 others. 2026. External-
ization in LLM agents: A unified review of memory,
skills, protocols and harness engineering.Preprint,
arXiv:2604.08224.
A Methodology details
A.1 Task instructions and scoring
Every approach the paper compares runs the same
task instruction (Figure 5), which tells the agent
to read each question and write its answer to
a per-question file, and states where to find the
book. A book-QA item takes one of two instruc-
tions: multiple-choice for En.MC and free-form for
En.QA and Zh.QA. Holding the instruction fixed
across raw, flat, and hierarchical leaves
the file system beside the text as the only vari-
able, so a score difference reflects how the agent
reached a passage rather than how it was asked
(Section 3.3).
A deterministic verifier then scores the writ-
ten answers, matching the official ∞Bench
compute_scores.py: it extracts the option let-
ter for multiple choice by regular expression and
compares it to the gold label, and it scores free-
form answers by ∞Bench’s normalized match and
token-level F1, with the Chinese variant normal-
izing Chinese punctuation and whitespace. No
answer-extraction model sits between the agent and
11
