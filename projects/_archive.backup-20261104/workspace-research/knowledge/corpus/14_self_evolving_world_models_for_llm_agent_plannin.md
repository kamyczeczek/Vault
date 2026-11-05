---
type: Concept
id: 14_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 15/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

k M S
ALFWorld ScienceWorld
EM F1 Cosine EM F1 Cosine
1 0.5288 0.7675 0.8013 0.5155 0.6243 0.7385
2 0.5313 0.7662 0.8007 0.4772 0.5889 0.7223
3 0.5334 0.7701 0.8018 0.5540 0.6573 0.7565
4 0.5379 0.7762 0.8023 0.4909 0.6034 0.7308
5 0.5388 0.7776 0.8028 0.4994 0.6134 0.7348
Table 8: Semantic Memory batch-size sweep (kME =5).
Memory EvolutionFigure 10 plots trajectory-
macro Exact Match in deployment order.
WORLDEVOLVERconsistently stays in a higher
accuracy band than Zero-Shot, RAWM-ϕ, and ITP-
I across environments and backbones, indicating
that online memories provide reusable context
beyond the current trajectory. The separation is
most pronounced for the Gemma family models.
On ScienceWorld, WORLDEVOLVERshows a
clear mid-deployment lift, while on ALFWorld it
remains high and stable throughout, suggesting
that ALFWorld’s more regular transition structure
enables earlier reuse of accumulated evidence.
Qwen3.5-9B exhibits lower and noisier local Exact
Match, implying that memory evidence is less
effective when the backbone model is less reliable
at predicting next observations during deployment.
Difficulty BreakdownFigure 8 reports success
rate by task difficulty. ALFWorld easy tasks are
nearly saturated for both backbones, making the
hard split more informative. On the hard version
of ALFWorld, GPT-5.4-mini already achieves sub-
stantially higher success than Gemma-4-26B-A4B,
leaving limited room for additional foresight gains;
for Gemma-4-26B-A4B, WORLDEVOLVERyields
small improvements mainly when selective fore-
sight is enabled. ScienceWorld is less saturated,
especially for Gemma-4-26B-A4B, so differences
among world-model methods are more visible. In
this setting, WORLDEVOLVERimproves Gemma-
4-26B-A4B across both agent types and gives the
clearest GPT-5.4-mini gain on ReflAct hard tasks,
increasing success from 46.00 to 54.00 without Ft
and 50.00 with Ft. Overall, world model foresight
is most useful when tasks are not saturated and tran-
sition uncertainty remains across environments.
Task Type BreakdownFigures 11 and 12 depict
the success rates of GPT-5.4-mini and Gemma-
4-26B-A4B by task type. The heatmaps show
a consistent pattern across backbones. On ALF-
World,PICK is nearly saturated, whileCLEAN,COOL,
Easy
(n=24)
Hard
(n=110)
0
50
100
ALFWorld - ReAct
SR (%)
96
39
96
30
96
26
100
31
100
40
GPT-5.4-mini
Easy
(n=24)
Hard
(n=110)
100
7
96
6
100
9
100
8
100
10
Gemma-4-26B-A4B
Easy
(n=24)
Hard
(n=110)
0
50
100
ALFWorld - ReflAct
SR (%)
100
39
100
30
96
16
96
34
96
36
Easy
(n=24)
Hard
(n=110)
100
10
92
5
96
7
96
9
100
12
Easy
(n=34)
Hard
(n=56)
0
50
100
ScienceWorld - ReAct
SR (%)
91
50
71
50
82
46
85
48
82
52
Easy
(n=34)
Hard
(n=56)
59
36
47 4138 32
56
41
71
41
Easy
(n=34)
Hard
(n=56)
0
50
100
ScienceWorld - ReflAct
SR (%)
82
46
76
48
82
45
76
54
85
50
Easy
(n=34)
Hard
(n=56)
44 4138 4341 36
53
46
56
45
w/o WM
WorldEvolver w/o Ft
RAWM-phi
WorldEvolver w/ Ft
ITP-I
Figure 8: Agent Planning Success Rate (%) by Agent-
Board easy/hard split, reported as best-of-5.
andLOOK remain difficult, especially for Gemma-4-
26B-A4B. The clearest gains appear on transition-
sensitive types such as PICK2, where WORLDE-
VOLVERimproves both backbones and both agent
policies, suggesting that weaker planners leave
more room for useful foresight. On ScienceWorld,
gains concentrate on task families that require track-
ing environment dynamics, including Lifespan,
Thermom., and Chemistry, while State Change
remains near zero across all methods and back-
bones. This suggests that world model foresight
captures reusable task-family dynamics, but re-
mains limited when relevant transitions are too
sparse to be reliably accumulated by ME or ab-
stracted into MS for reuse across subsequent tasks.
Action-Level Effect of Selective ForesightFor
Gemma-4-26B-A4B, we measure how often visible
selective foresight changes the draft action, aggre-
gated over all foresight-exposed decision steps in
the AgentBoard planning rollouts. All rows in Ta-
ble 9 correspond to the w/F t condition.
The world model adds Ft to the agent’s interac-
15
