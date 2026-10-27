---
type: Concept
id: 18_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 19/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

0 50 100 150 200
0
25
50
75
100
ALFWorld
Exact Match (%)
Gemma-4-26B-A4B
0 50 100 150 200
Qwen3.5-9B
0 50 100 150 200
Gemma-4-31B
0 50 100 150 200
0
25
50
75
100
ScienceWorld
Exact Match (%) 0 50 100 150 200 0 50 100 150 200
Trajectory index
Zero-Shot RAWM-ϕ ITP-I WorldEvolver
Figure 10: Trajectory-level world model prediction Exact Match (%) along the Word2World deployment order. We
report macro Exact Match averaged over the prediction steps within each trajectory.
0
20
40
60
80
100
SR (%)
PICK CLEAN HEAT COOL LOOK PICK2 Lifespan
Find
Melt. PointThermom.Life Stage
State Change
Chemistry
w/o WM
RAWM-ϕ
ITP-I
WorldEvolver
w/o Ft
WorldEvolver
w/ Ft
ReAct
96 0 91 0 50 76 93 83 50 50 60 0 56
96 0 78 0 28 59 70 78 43 62 40 0 67
96 0 70 5 6 65 85 72 36 62 40 0 67
100 0 83 0 17 71 85 67 36 75 40 0 89
100 3 91 24 17 82 85 89 29 62 40 0 78
ALFWorld ScienceWorld
PICK CLEAN HEAT COOL LOOK PICK2 Lifespan
Find
Melt. PointThermom.Life Stage
State Change
Chemistry
w/o WM
RAWM-ϕ
ITP-I
WorldEvolver
w/o Ft
WorldEvolver
w/ Ft
ReflAct
100 26 43 19 72 47 85 94 14 75 0 0 67
100 10 13 19 67 65 81 89 29 62 0 0 67
96 3 35 0 28 24 81 94 21 75 0 0 56
96 19 35 5 67 59 81 89 36 62 0 0 89
96 16 26 14 78 71 89 94 14 75 20 0 78
Figure 11: Heatmap of agent planning success rates (%) for GPT-5.4-mini across different world models, reported
as best-of-5 performance on ALFWorld and ScienceWorld task types.
19

0
20
40
60
80
100
SR (%)
PICK CLEAN HEAT COOL LOOK PICK2 Lifespan
Find
Melt. PointThermom.Life Stage
State Change
Chemistry
w/o WM
RAWM-ϕ
ITP-I
WorldEvolver
w/o Ft
WorldEvolver
w/ Ft
ReAct
100 0 0 0 0 47 56 78 21 62 20 0 22
96 0 0 0 0 41 41 83 29 62 0 0 44
100 0 0 0 0 59 30 72 14 62 20 0 22
100 0 0 0 0 53 52 78 14 75 20 0 56
100 0 0 0 0 65 70 94 14 62 0 0 44
ALFWorld ScienceWorld
PICK CLEAN HEAT COOL LOOK PICK2 Lifespan
Find
Melt. PointThermom.Life Stage
State Change
Chemistry
w/o WM
RAWM-ϕ
ITP-I
WorldEvolver
w/o Ft
WorldEvolver
w/ Ft
ReflAct
100 0 0 0 0 65 37 94 21 62 0 0 33
92 0 0 0 0 29 30 94 21 62 0 0 44
96 0 0 0 0 47 33 89 0 62 0 0 44
96 0 0 0 0 59 48 94 21 75 20 0 44
100 3 0 0 0 71 52 94 21 75 20 0 44
Figure 12: Heatmap of agent planning success rates (%) for Gemma-4-26B-A4B across different world models,
reported as best-of-5 performance on ALFWorld and ScienceWorld task types.
0 25 50 75 100
0
25
50
75
100
ALFWorld
Exact Match (%)
Gemma-4-26B-A4B
0 25 50 75 100
Qwen3.5-9B
0 25 50 75 100
Gemma-4-31B
0 25 50 75 100
0
25
50
75
100
ScienceWorld
Exact Match (%)
0 25 50 75 100 0 25 50 75 100
T op-confidence prefix (%)
Zero-Shot RAWM-ϕ ITP-I WorldEvolver
Figure 13: Selective foresight confidence calibration, measured as Exact Match on the top-confidence prefix.
20
