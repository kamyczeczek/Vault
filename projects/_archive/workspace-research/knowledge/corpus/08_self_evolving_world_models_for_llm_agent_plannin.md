---
type: Concept
id: 08_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 9/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Environment Memory setup Exact Match Token F1 Cosine
ALFWorld Full 0.5288 0.7675 0.8013
Reset 0.4387 0.6675 0.7723
ScienceWorld Full 0.5155 0.6243 0.7385
Reset 0.2070 0.3456 0.6178
Table 3: World Model Prediction with persistent mem-
ory and memory reset before each trajectory.
Environment Agent Best-of-5 SR Success@1∆SR (pp)
ALFWorld ReAct 24.1% 18.9% -0.5
ReflAct 23.9% 19.7% -0.7
ScienceWorld ReAct 45.6% 23.3% -1.1
ReflAct 47.8% 30.0% -1.1
Table 4: Agent Planning with memory reset before
each task, averaged over three runs. ∆ SR is measured
against full-memory WORLDEVOLVERw/oF t.
smaller for GPT-5.4-mini because its stronger plan-
ning ability leaves less room for substantial im-
provement from world model foresight.
Memory Reset ControlsTo isolate cross-task
accumulation from within-trajectory and within-
task learning, we add reset controls for both ME
and MS. For World Model Prediction, both memo-
ries are cleared at the start of each trajectory. For
Agent Planning, both memories are cleared before
each task and retained across all five trials for that
task. All control experiments use Gemma-4-26B-
A4B; in Agent Planning, the agent and world model
share this backbone. Tables 3 and 4 report the cor-
responding results. The planning results are means
over three complete runs, and the deltas use the
reported full-memory WORLDEVOLVERw/o Ft
results as the baseline for a direct comparison.
Resetting memory substantially reduces next-
observation prediction accuracy but changes best-
of-5 planning success by only 0.5 to 1.1 points for
two reasons. First, the evaluations measure dif-
ferent outcomes: World Model Prediction directly
scores every one-step forecast, whereas Agent Plan-
ning scores final task completion. A wrong forecast
therefore affects planning success only if it leads
to a harmful action that the agent cannot correct
after observing the actual outcome. Second, Agent
Planning retains memory across the five trials of
each task, so later trials can use evidence collected
in earlier trials. Lower one-step accuracy therefore
does not imply an equally large drop in best-of-5
success under this controlled reset protocol.
From Prediction to PlanningTables 1 and 2
evaluate distinct stages of the pipeline. World
40% 50% 60% 70%
Best-of-5 Success Rate
ALFWorld / ReAct
ALFWorld / ReflAct
ScienceWorld / ReAct
ScienceWorld / ReflAct
No-WM WorldEvolver w/ Ft
Figure 6: GPT-5.4-mini Agent Planning best-of-5 Suc-
cess Rate with task-level 95% bootstrap confidence in-
tervals across all four environment-agent settings.
Model Prediction directly scores static, one-step
next-observation predictions, whereas Agent Plan-
ning evaluates their effect on closed-loop behav-
ior. A prediction error matters only if it changes
the agent’s action and may then alter subsequent
states. Improvements in one-step prediction accu-
racy therefore do not directly translate into higher
terminal task success in closed-loop planning.
Compared with the smaller open-source Gemma-
4-26B-A4B, GPT-5.4-mini has stronger general
reasoning capabilities. Its parametric world knowl-
edge and interaction history already support many
action-effect inferences without an external world
model, yielding a stronger no-world-model base-
line and less headroom for additional foresight. Fig-
ure 6 makes these mixed results explicit: the confi-
dence intervals overlap with their no-world-model
counterparts in all four settings.
5 Conclusion
We presented WORLDEVOLVER, a training-free
framework for self-evolving world models in LLM
agent planning. Rather than updating model param-
eters, WORLDEVOLVERrevises world model con-
text at test time through episodic memory, seman-
tic memory, and selective foresight. Experiments
on ALFWorld and ScienceWorld show that these
mechanisms improve both world model fidelity
and downstream planning performance. WORLDE-
VOLVERachieves the strongest prediction accuracy
on Word2World across three backbones and im-
proves downstream agent success rates, suggesting
that reliable foresight depends on how environmen-
tal signals are processed and presented to the agent,
motivating future work on agentic world modeling.
9
