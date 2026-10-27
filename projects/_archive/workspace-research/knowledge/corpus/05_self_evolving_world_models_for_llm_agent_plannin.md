---
type: Concept
id: 05_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 6/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Because the final action may differ from the draft
action used for the initial prediction, WORLDE-
VOLVERaligns the learning signal with the ac-
tion actually executed in the environment. When
at ̸=a (0)
t , the world model (7) is queried once
more with at to obtain ˆot+1. This second query
ensures that Semantic Memory is updated from
the mismatch between the prediction for the exe-
cuted action and the realized observation. After (8)
executing at, WORLDEVOLVER(9) appends the re-
alized transition (ot, at, ot+1) to Episodic Memory.
It then compares the executed-action prediction
ˆot+1 with the realized observation ot+1; if they
differ after factorization, the LLM critic (10) pro-
duces rule updates ∆M t
S. Finally, the algorithm
(11) returns the action and updated non-parametric
memories. This preserves action-level consistency.
4 Experiment
We evaluate WORLDEVOLVERalong two comple-
mentary axes. First,World Model Prediction
(Section 4.2) measures how accurately the model
predicts future observations relative to real environ-
ment transitions. Second,Agent Planning(Sec-
tion 4.3) evaluates whether these world models
improve closed-loop task performance for agents.
Finally, Section 4.4 discusses the effects of mem-
ory hyperparameters and online continual learning,
with additional analyses provided in Appendix C.
4.1 Setups
This subsection summarizes the experimental setup,
and additional details are provided in Appendix A.
DatasetsWe conduct evaluations on both world
model prediction and agent planning. To evalu-
ate the alignment between prediction and ground
truth, we adopt the Word2World Benchmark (Li
et al., 2025b), which provides transition datasets
for ALFWorld (Shridhar et al., 2021) and Science-
World (Wang et al., 2022). The test split contains
195 trajectories for each environment. In agent
planning, we use AgentBoard (Ma et al., 2024),
with 134 ALFWorld tasks and 90 ScienceWorld
tasks. Each configuration runs L=5 trials per task,
with a maximum of 30 steps per trial.
BaselinesWe define each comparison by the fore-
sight provided by the world model while keeping
both the agent and backbone model fixed. We con-
sider the following baselines:Zero-Shot,RA WM-
ϕ(Yang et al., 2025), andITP-I(Liu et al., 2026).
AgentsWe apply two agent types with distinct
planning styles to test whether the world model gen-
eralizes across reasoning paradigms:ReAct(Yao
et al., 2023a) andReflAct(Kim et al., 2025).
Evaluation MetricsPrediction metrics measure
whether the world model matches the next obser-
vation; planning metrics measure whether the ex-
posed signal helps the agent complete tasks.
• World model prediction:(1) Exact Match
uses normalized string matching between pre-
dicted and reference observations. (2) Token
F1 measures lexical overlap after tokenization,
micro-averaged across all examples. (3) Cosine
Similarity measures semantic similarity using
Qwen3-Embedding-8B (Zhang et al., 2025b) em-
beddings in the same retrieval space.
• Agent planning:We report Success Rate, de-
fined as whether the agent completes the task
within the allowed interaction budget, and aggre-
gate results using best-of-Lacross trials.
Implementation DetailsWorld model predic-
tion uses Qwen3.5-9B (Qwen Team, 2026),
Gemma-4-26B-A4B, and Gemma-4-31B (Google
DeepMind, 2026). Agent planning evaluation uses
Gemma-4-26B-A4B and GPT-5.4-mini (OpenAI,
2026), with the agent and world model sharing
the same model. Additional implementation details
and prompts are shown in Appendix B and E.
4.2 Experiments on World Model Prediction
Table 1 evaluates next-observation prediction: (1)
Among the baselines, RAWM-ϕ is strongest across
Gemma-4-26B, Qwen3.5-9B, and Gemma-4-31B,
showing that retrieval from collected trajecto-
ries provides useful transition evidence for next-
observation prediction. By contrast, ITP-I con-
sistently underperforms Zero-Shot, due to over-
generation of imagined future details. (2) The
memory ablations of WORLDEVOLVERshow
complementary roles: Semantic Memory alone
gives modest gains over Zero-Shot, whereas the
Episodic Memory variant provides substantially
larger improvements and outperforms RAWM-ϕ,
even though RAWM-ϕ retrieves from the full de-
ployment trajectory set in advance while Episodic
Memory accumulates strictly online. This gap sug-
gests that retrieval quality depends on the retrieval
key. RAWM-ϕ retrieves from full state-action text,
where long and repetitive state descriptions can
6
