---
type: Concept
id: 13_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 14/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

10 20 30 40 50 60 70 80 90
T op-confidence (%)
60
65
70
75
80
85T oken F1 (%)
99.9998
99.9996 99.9991 99.9980 99.9955 99.9897 99.9725
99.9181
99.7416
99.9995 99.9981 99.9948 99.9878
99.9725
99.9346
99.8292
99.5613
99.0587ALFWorld
ScienceWorld
Figure 7: Selective foresight confidence calibration
on Token F1 (%) for Gemma-4-26B-A4B under the
WORLDEVOLVERconfiguration in both environments.
Agent Gemma-4-26B-A4B GPT-5.4-mini
ALFWorld ScienceWorld ALFWorld ScienceWorld
ReAct1−10 −4 1−10 −4 1−10 −6 1−10 −4
ReflAct1−10 −5 1−10 −4 1−10 −6 1−10 −3
Table 5: Values ofτ used for selective foresight filtering
in the w/F t agent-planning settings across backbones.
backbone as Wθ. To support deployment-time con-
tinual learning, episodic memory ME and seman-
tic memory MS persist across tasks within each
environment. Selective foresight is applied when
the geometric-mean token probability qt exceeds
threshold τ. Figures 7 and 13 show that confidence
scores correlate with both Exact Match and Token
F1 on Gemma-4-26B-A4B. Per-cell thresholds (Ta-
ble 5) are selected from these calibration curves,
with values near 1−10−5 performing well; GPT-
5.4-mini follows the same calibration procedure.
C Evaluation and Analysis
RuntimeThe accuracy gains of WORLDE-
VOLVERcome from episodic and semantic mem-
ory modules, raising the question of whether these
improvements justify the added inference cost. Ta-
ble 6 shows that WORLDEVOLVERintroduces only
moderate runtime overhead relative to Zero-Shot
and ITP-I. For example, on Gemma-4-26B-A4B,
runtime increases from 1.05s to 1.48s per transi-
tion for WORLDEVOLVER, compared to 1.42s for
ITP-I, while achieving substantially stronger Exact
Match performance in Table 1. This suggests that
the additional computation is effectively utilized
for retrieval and mismatch-driven rule condition-
ing rather than longer imagination rollouts alone.
RAWM-ϕ is the cheapest among most world-model
approaches because retrieval embeddings are pre-
computed offline and excluded from runtime mea-
surement. Despite this advantage, its prediction
Method Runtime (s/transition)
ALFWorld ScienceWorld Average GPU/h
Gemma-4-26B-A4B
Zero-Shot 1.04 1.06 1.05 3.72
RAWM-ϕ0.63 0.89 0.75 2.65
ITP-I 1.26 1.61 1.42 5.03
WORLDEVOLVER1.44 1.53 1.48 5.24
Qwen3.5-9B
Zero-Shot 0.53 0.80 0.66 2.32
RAWM-ϕ0.56 0.91 0.72 2.55
ITP-I 1.15 1.33 1.23 4.36
WORLDEVOLVER0.69 1.27 0.96 3.38
Gemma-4-31B
Zero-Shot 0.70 0.82 0.75 2.66
RAWM-ϕ0.51 0.53 0.52 1.84
ITP-I 0.97 1.45 1.19 4.21
WORLDEVOLVER1.25 1.45 1.34 4.73
Table 6: World model prediction runtime, reported as
seconds per evaluated transition and total GPU hours
across both environments on a single NVIDIA H200
GPU. All methods use the same serving setup.
k M E
ALFWorld ScienceWorld
EM F1 Cosine EM F1 Cosine
1 0.4006 0.6931 0.7741 0.1585 0.3098 0.5888
2 0.4817 0.7331 0.7909 0.3624 0.4922 0.6834
3 0.4933 0.7383 0.7925 0.4764 0.5960 0.7297
4 0.5253 0.7623 0.7997 0.4811 0.5961 0.7275
5 0.5290 0.7646 0.7977 0.5038 0.6064 0.7312
Table 7: Varying Episodic Memory retrieval sizekME
with kMS =1. The kME =5 row reports the five-seed
aggregate; the other rows report canonical runs.
accuracy remains consistently below WORLDE-
VOLVER. Overall, WORLDEVOLVERprovides the
best trade-off between runtime and prediction per-
formance across the evaluated backbones.
Memory Hyperparameter AnalysisWe first se-
lect kME =5 using WORLDEVOLVERw/o MS and
kMS =1 using WORLDEVOLVERw/o ME. We
then combine these values in the full model and use
the same configuration across all environments and
backbones instead of selecting separate hyperpa-
rameters for each setting. Tables 7 and 8 report the
corresponding sweeps with Gemma-4-26B-A4B
on ALFWorld and ScienceWorld, respectively.
The best tested combination is
(kME , kMS )=(5,5) on ALFWorld and (5,3)
on ScienceWorld. We nevertheless use the shared
setting (5,1) across environments and backbones.
This configuration is selected on Word2World and
transferred unchanged to AgentBoard; therefore,
the memory hyperparameters are not tuned to the
AgentBoard planning results in this evaluation.
14
