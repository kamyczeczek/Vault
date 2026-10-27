---
type: Concept
id: 17_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 18/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Setting
WM invocations
/ agent step
LLM calls
/ agent step
Retrieval
ms / call
Max prompt tokens
/ WM call
ALFWorld ReAct 2.086 1.609 16.244 2,982
ALFWorld ReflAct 2.054 1.642 18.335 2,726
ScienceWorld ReAct 2.157 1.866 10.100 4,324
ScienceWorld ReflAct 2.131 1.874 10.906 4,211
Table 13: Planning-time overhead and peak context
length for WORLDEVOLVERw/oF t during planning.
Environment
Predictions
scored Mean F1
Mean
confidence
ECE-F1-10
↓
F1 C-index
↑
ALFWorld 34,150 0.7646 0.9912 0.2266 0.6632
ScienceWorld 29,489 0.6065 0.9771 0.3706 0.6963
Table 14: Confidence calibration and ranking diagnos-
tics across five seeded trajectory orders in aggregate.
ning outcome is used for threshold selection.
To reduce sensitivity to a single evaluation or-
der, we aggregate post-hoc calibration diagnostics
across five randomly seeded trajectory orders for
World Model Prediction in each environment.
Selective Foresight uses qt to rank and filter pre-
dictions rather than as a probability estimate. ECE-
F1-10 is the sample-weighted absolute gap between
mean confidence and mean Token F1 across ten
confidence bins. Because Token F1 is our primary
prediction-quality metric and is continuous, we
report C-index for ranking instead of ROC-AUC,
which would require binarizing F1 at an arbitrary
threshold. C-index measures how often higher con-
fidence corresponds to higher F1 across compara-
ble pairs, with 0.5 indicating random ranking and
1.0 perfect ranking. Scores of 0.6632 and 0.6963
indicate 66.3% and 69.6% correct ordering on ALF-
World and ScienceWorld, respectively.
D Case Study
We present one retrieval failure from each environ-
ment. In both cases, Episodic Memory retrieves
task-relevant transitions, but the model fails to rec-
ognize that the specific action cannot be executed
and incorrectly predicts a successful outcome.
Retrieval surfaces closely related same-task tran-
sitions involving the relevant object class and loca-
tion. The failure arises because the current transi-
tion depends on a fine-grained executability condi-
tion: although similar pickup and location memo-
ries are relevant, the specific target command pro-
duces no state change. The model therefore over-
generalizes from nearby successful transitions and
predicts a pickup despite the no-op outcome.
Retrieval is domain-relevant: all retrieved transi-
tions involve circuit construction in the same task
Field Value
Task put two soapbottle in cart
Target action take soapbottle 2 from garbagecan 1
Model prediction You pick up the soapbottle 2 from the garbagecan 1.
Gold next state Nothing happens.
Rank Source action Source gold
1 take soapbottle 1 from
shelf 1
You pick up the soapbottle 1 from the
shelf 1.
2 go to garbagecan 1 You arrive at garbagecan 1. On the
garbagecan 1, you see a papertowelroll
1, and a soapbottle 2.
3 examine sinkbasin 1 On the sinkbasin 1, you see a soapbar 1.
4 go to shelf 1 You arrive at shelf 1. On the shelf 1, you
see a soapbottle 1.
5 go to shelf 2 You arrive at shelf 2. On the shelf 2, you
see nothing.
Table 15: Representative Episodic Memory retrieval
failure in ALFWorld with retrieved transitions.
Field Value
Task electrical conductivity of unknown substance L
Target action connect green light bulb anode to switch cathode using
yellow wire
Model prediction The yellow wire connects green bulb anode to switch
cathode.
Gold next state No known action matches that input.
Rank Source action Source gold
1 connect battery cathode to
green light bulb
Connections must specify specific
points of contact on polarized electri-
cal components. . .
2 connect battery cathode to
green light bulb cathode
cathode on battery is now connected to
cathode on green light bulb
3 connect battery anode to
switch
Connections must specify specific
points of contact on polarized electri-
cal components. . .
4 connect battery anode to
switch anode
anode on battery is now connected to
anode on switch
5 connect battery to switch Connections must specify specific
points of contact on polarized electri-
cal components. . .
Table 16: Representative Episodic Memory retrieval
failure in ScienceWorld with circuit transitions.
family. The failure is that simulator command va-
lidity is highly specific. Similar connection memo-
ries help identify the correct physical domain, but
they do not guarantee that every phrasing of a con-
nection command is accepted by the environment.
The model overgeneralizes from nearby valid cir-
cuit updates and predicts a successful connection.
Together, these cases show that action-centered re-
trieval can identify the relevant domain while still
missing fine-grained executability constraints.
E Prompts
The ReAct and ReflAct prompts for ALFWorld
are shown in Figures 14 and 15, with Science-
World counterparts in Figures 16 and 17. World-
model prompts are provided in Figures 18–23. The
two memory-update prompts used in WORLDE-
VOLVERare shown in Figures 24 and 25.
18
