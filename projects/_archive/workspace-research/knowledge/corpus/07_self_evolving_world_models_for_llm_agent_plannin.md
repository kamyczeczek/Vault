---
type: Concept
id: 07_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 8/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

0
20
40
60
80
GPT-5.4-mini
SR (%)
ALFWorld - ReAct
 ALFWorld - ReflAct
 ScienceWorld - ReAct
 ScienceWorld - ReflAct
1 2 3 4 5
0
20
40
60
Gemma-4-26B-A4B
SR (%)
1 2 3 4 5
 1 2 3 4 5
 1 2 3 4 5
Trial index
w/o WM RAWM-phi ITP-I WorldEvolver w/o Ft WorldEvolver w/ Ft
Figure 4: Cumulative best-of-LAgent Planning Success Rate on ALFWorld and ScienceWorld.
-2
-1
0
Δ EM (%)
-25
-15
-5
0
-2
-1
0
Δ EM (%)
-25
-15
-5
0
1 2 3 4 5
kMS
-2
-1
0
Δ EM (%)
1 2 3 4 5
kME
-25
-15
-5
0
Gemma-4-26BQwen3.5-9BGemma-4-31B
ALFWorld ScienceWorld
Figure 5: Relative gains from memory hyperparameters
for world model prediction, reported as ∆EM. kMS
varies semantic-memory batch size relative to 1, while
kME varies episodic-memory retrieval size relative to5.
average Success Rate by 3.67 points, showing
the advantage of continual episodic retrieval and
mismatch-derived heuristic rule generation over
static offline retrieval. (3) Improvements over the
no-world-model baseline span both agent types and
both model backbones. WORLDEVOLVERw/o Ft
exceeds the no-world-model baseline in four set-
tings: Gemma-4-26B-A4B with ReAct on ALF-
World (23.88 to 24.63), Gemma-4-26B-A4B on
ScienceWorld for both ReAct and ReflAct (44.44
to 46.67; 42.22 to 48.89), and GPT-5.4-mini with
ReflAct on ScienceWorld (60.00 to 62.22).
WORLDEVOLVERw/ Ft beats the no-world-
model baseline across all four Gemma-4-26B-A4B
cells, averaging +2.24 Success Rate points on
ALFWorld and +3.33 on ScienceWorld over the
no-foresight variant; even ReflAct on ALFWorld
lifts WORLDEVOLVERfrom 24.63 to 27.61, above
the 26.12 baseline. GPT-5.4-mini gains are more
mixed: WORLDEVOLVERw/ Ft tops the no-world-
model baseline in only two of four cells, winning
by +1.50 on ReAct/ALFWorld and +3.33 on Re-
flAct/ScienceWorld but losing by−2.99 on ReflAc-
t/ALFWorld and −2.23 on ReAct/ScienceWorld.
Confidence-gated abstention is therefore more ben-
eficial for the weaker backbone, where the agent
leaves more room for useful world model guidance.
4.4 Discussion
Memory HyperparametersFigure 5 evaluates
memory hyperparameters on the same setting as Ta-
ble 1. Episodic retrieval is the dominant factor: in-
creasing kME from 1 to 5 improves Exact Match by
16.8/23.5 points on ALFWorld and ScienceWorld
for Gemma-4-26B-A4B, 7.6/19.2 for Qwen3.5-9B,
and 9.0/19.3 for Gemma-4-31B. Semantic batch
size is much less sensitive: most kMS choices dif-
fer by within two points, except Gemma-4-31B
on ALFWorld. We therefore use kME = 5 and
kMS = 1 in Section 4.2, combining the strongest
episodic retrieval with a semantic update size that
is competitive across backbones and environments.
Online Continual LearningFigure 4 analyzes
cumulative best-of-L success rate from trialL=1 to
L=5. The slope of each curve reflects the benefit of
additional successful attempts beyond the first trial.
This analysis is particularly relevant for WORLDE-
VOLVER, since episodic memory ME and semantic
memory MS accumulate across trials and tasks
within the same environment, allowing later agent
replanning to exploit refined world-model fore-
sight. The clearest separation appears on Science-
World with Gemma-4-26B-A4B, where WORLDE-
VOLVERvariants increasingly outperform RAWM-
ϕ and ITP-I as the trial index grows, demonstrat-
ing that deployment-time memory is most effec-
tive when agents can iteratively replan. Gains are
8
