---
type: Concept
id: 06_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 7/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Setting ALFWorld ScienceWorld
Exact Match Token F1 Cosine Similarity Exact Match Token F1 Cosine Similarity
Gemma-4-26B-A4B
Zero-Shot 3.60 35.48 67.91 0.41 16.42 52.45
RAWM-ϕ(Yang et al., 2025) 20.06 48.13 71.30 14.93 27.31 56.50
ITP-I (Liu et al., 2026) 1.46 32.48 66.10 0.39 11.50 47.69
WORLDEVOLVER(w/oM E) 7.53 38.08 69.06 2.71 19.29 55.04
WORLDEVOLVER(w/oM S) 47.16 72.61 78.88 34.65 46.93 66.51
WORLDEVOLVER52.88 76.75 80.13 51.55 62.43 73.85
Qwen3.5-9B
Zero-Shot 1.58 34.06 66.39 0.59 12.72 49.27
RAWM-ϕ(Yang et al., 2025) 14.41 38.63 66.31 2.76 16.53 49.76
ITP-I (Liu et al., 2026) 0.00 11.22 52.88 0.00 6.68 41.94
WORLDEVOLVER(w/oM E) 2.04 33.80 65.81 0.90 13.98 50.40
WORLDEVOLVER(w/oM S) 34.86 61.56 74.34 28.92 44.84 65.08
WORLDEVOLVER37.04 62.38 74.64 29.82 44.88 65.15
Gemma-4-31B
Zero-Shot 2.71 38.42 69.90 7.58 25.28 58.55
RAWM-ϕ(Yang et al., 2025) 34.33 57.49 72.66 32.84 42.38 64.84
ITP-I (Liu et al., 2026) 1.36 33.61 67.64 0.56 11.91 49.63
WORLDEVOLVER(w/oM E) 6.73 41.30 71.72 13.34 30.90 61.32
WORLDEVOLVER(w/oM S) 56.27 80.02 81.21 56.74 66.50 76.00
WORLDEVOLVER56.41 80.87 81.39 62.03 71.60 78.42
Table 1: World model prediction accuracy on Word2World; higher is better for all metrics.w/o ME removes
episodic memory, whilew/o MS removes semantic memory. All memories Mt are initialized empty and updated
online during interaction. Unless otherwise specified, WORLDEVOLVERhere usesk ME =5andk MS =1.
Agent Setting ALFWorld ScienceWorld
Gemma-4-26B-A4B GPT-5.4-mini Gemma-4-26B-A4B GPT-5.4-mini
ReAct
w/o World Model 23.88 49.25 44.44 65.56
RAWM-ϕ(Yang et al., 2025) 22.39 41.79 43.33 57.78
ITP-I (Liu et al., 2026) 25.37 38.81 34.44 60.00
WORLDEVOLVERw/oF t 24.63 43.28 46.67 62.22
WORLDEVOLVERw/F t 26.12 50.75 52.22 63.33
ReflAct
w/o World Model 26.12 50.00 42.22 60.00
RAWM-ϕ(Yang et al., 2025) 20.15 42.54 41.11 58.89
ITP-I (Liu et al., 2026) 23.13 30.60 37.78 58.89
WORLDEVOLVERw/oF t 24.63 44.78 48.89 62.22
WORLDEVOLVERw/F t 27.61 47.01 50.00 63.33
Table 2: Agent planning success rate; higher is better. w/ and w/o Ft denote with and without selective foresight.
Underlines denote the best overall setting, and bold denotes the best setting among world-model-based methods.
dilute the action signal, whereas episodic mem-
ory retrieval more directly matches the target tran-
sition being simulated. Representative cases in
Appendix D show that action-centered retrieval
can still miss fine-grained executability constraints.
The three metrics yield consistent rankings across
backbones and environments, capturing correlated
aspects of prediction quality in this evaluation.
Overall, accurate world model prediction bene-
fits most from combining episodic retrieval with se-
mantic rules. The full WORLDEVOLVERachieves
the highest prediction accuracy across both environ-
ments and all three backbones. Gains over episodic
memory alone are particularly pronounced on Sci-
enceWorld for the Gemma models, while Qwen3.5-
9B shows smaller but consistent improvements
from integrating semantic memory.
4.3 Experiments on Agent Planning
Table 2 evaluates agent planning by Success Rate:
(1) Compared with world-model prediction results
in Section 4.2, improving planning success is sub-
stantially more challenging. RAWM-ϕ and ITP-I
often underperform the no-world-model baseline,
further confirming that misaligned foresight can
degrade action selection. (2) WORLDEVOLVERis
the strongest world-model method across all eight
settings; selective foresight further improves or ties
the no-foresight variant in every setting. Relative
to RAWM-ϕ, WORLDEVOLVERw/o Ft improves
7
