---
type: Concept
id: 16_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 17/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Agent Mode Condition
ALFWorld ScienceWorld
Progress Rate Grounding Progress Rate Grounding
Gemma-4-26B-A4B
ReAct
w/o World Model 61.57 72.13 76.58 35.76
RAWM-ϕ(Yang et al., 2025) 60.70 76.77 74.88 34.28
ITP-I (Liu et al., 2026) 63.25 75.17 73.42 40.31
WORLDEVOLVERw/oF t 61.57 79.76 79.47 35.02
ReflAct
w/o World Model 63.81 70.25 75.22 33.09
RAWM-ϕ(Yang et al., 2025) 58.27 69.29 73.89 29.41
ITP-I (Liu et al., 2026) 61.38 72.95 74.68 36.65
WORLDEVOLVERw/oF t 62.38 77.30 77.58 26.93
GPT-5.4-mini
ReAct
w/o World Model 75.31 76.05 88.31 38.62
RAWM-ϕ(Yang et al., 2025) 73.82 79.62 84.74 40.23
ITP-I (Liu et al., 2026) 70.52 83.61 85.62 40.40
WORLDEVOLVERw/oF t 74.07 77.04 87.39 40.59
ReflAct
w/o World Model 76.12 78.81 84.43 40.89
RAWM-ϕ(Yang et al., 2025) 71.27 78.21 83.25 39.07
ITP-I (Liu et al., 2026) 66.23 78.14 82.87 42.79
WORLDEVOLVERw/oF t 71.95 82.23 82.69 41.56
Table 10: AgentBoard planning metrics for the Success Rate results in Table 2. Values are percentages without
percent signs for both backbones and environments.
Environment Action-Jaccard RAWM-ϕ∆
ALFWorld 0.783 0.529 +0.254
ScienceWorld 0.687 0.653 +0.034
Table 11: Top-1 transition-retrieval accuracy.∆ denotes
Action-Jaccard minus RAWM-ϕacross environments.
update calls, whereas LLM calls include all under-
lying LLM calls. Maximum prompt tokens mea-
sure the peak context length associated with mem-
ory growth during closed-loop planning.
The two representative failures in Section D
show how relevant memory can still mislead pre-
diction. In ALFWorld, retrieved successful pickup
transitions cause the model to predict a pickup for
“take soapbottle 2 from garbagecan 1, ”although
the gold observation is“Nothing happens. ”In Sci-
enceWorld, same-task circuit transitions cause the
model to predict a successful connection for“con-
nect green light bulb anode to switch cathode using
yellow wire, ”although the simulator returns“No
known action matches that input. ”In both cases, re-
trieval identifies the correct task domain but misses
a fine-grained executability or command-validity
constraint during action-conditioned prediction.
ALFWorld
Method ReAct ReflAct
w/o World Model23.9 [17,31]/22.4 26.1 [19,34]/20.9
RAWM-ϕ22.4 [16,29]/17.2 20.1 [14,27]/15.7
ITP-I25.4 [19,33]/18.7 23.1 [16,31]/14.2
WORLDEVOLVERw/oF t 24.6 [18,32]/17.2 24.6 [18,32]/17.9
WORLDEVOLVERw/F t 26.1 [19,34]/19.4 27.6 [21,35]/20.9
ScienceWorld
Method ReAct ReflAct
w/o World Model44.4 [34,56]/28.9 42.2 [32,52]/31.1
RAWM-ϕ43.3 [33,53]/26.7 41.1 [31,51]/25.6
ITP-I34.4 [24,44]/24.4 37.8 [28,48]/27.8
WORLDEVOLVERw/oF t 46.7 [37,57]/24.4 48.9 [39,59]/32.2
WORLDEVOLVERw/F t 52.2 [42,62]/36.7 50.0 [40,60]/33.3
Table 12: Agent Planning uncertainty and first-trial suc-
cess for Gemma-4-26B-A4B. Each cell reports best-of-5
Success Rate [task-level 95% bootstrap CI] / Success@1
(%) across all four environment-agent settings.
Selective-Foresight Threshold CalibrationSe-
lective Foresight is used only in Agent Planning.
As detailed in Appendix B, thresholds are se-
lected from the Word2World test-set confidence-
quality curves in Figure 7, which sweep confidence-
retention levels and report Token F1. These curves
provide prediction-level threshold sensitivity. We
then fix the selected thresholds and transfer them
unchanged to AgentBoard, so no AgentBoard plan-
17
