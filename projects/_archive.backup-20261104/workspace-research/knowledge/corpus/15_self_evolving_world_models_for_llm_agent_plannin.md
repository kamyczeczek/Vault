---
type: Concept
id: 15_self_evolving_world_models_for_llm_agent_plannin
title: "Self-Evolving World Models for LLM Agent Planning (part 16/24)"
source: "Self-Evolving World Models for LLM Agent Planning.pdf"
tags: [agentic, agents, context-engineering, icm, memory, planning, prompt-engineering, reflection, self-evolution, world-models]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Environment Agent Steps withFt Action changed Change rate
ALFWorld ReAct 17,867 1,614 9.0%
ReflAct 17,981 946 5.3%
ScienceWorldReAct 11,450 1,912 16.7%
ReflAct 10,981 1,376 12.5%
Table 9: Action changes after selective foresight is
shown to Gemma-4-26B-A4B during Agent Planning.
tion history, which the agent may use to revise
its draft action; this occurs on 5.3% to 16.7%
of exposed steps. Figures 11 and 12 compare
WORLDEVOLVERwith the no-world-model base-
line by task type. The clearest gains occur on
transition-sensitive ALFWorldPICK2 tasks and Sci-
enceWorldLifespan, Thermom., and Chemistry
tasks, whereas ALFWorldPICK is nearly saturated
and ScienceWorld State Change remains near
zero across methods. These results identify the task
types on which foresight is associated with higher
task success across the evaluated benchmarks.
Foresight ConfidenceFigure 13 reports Ex-
act Match over predictions ranked by WORLDE-
VOLVER’s confidence across quantiles. In most
settings, Exact Match decreases as confidence cov-
erage expands, indicating that higher-confidence
predictions are generally more reliable and can sup-
port selective foresight. Across all retention per-
centages, WORLDEVOLVERremains well above
Zero-Shot, RAWM-ϕ, and ITP-I, suggesting that
the confidence gate filters a stronger predictive sig-
nal rather than merely selecting examples that are
easy for all methods. This aligns with Table 2,
where adding Ft consistently matches or improves
over removingF t across planning settings.
AgentBoard reports two planning metrics along-
side Success Rate.Progress Raterecords the max-
imum task progress reached across trials.Ground-
ingmeasures how often the environment accepts
the agent’s actions as valid. Table 10 reports both
metrics for every cell of Table 2 for completeness.
Comparison of Retrieval MethodsWe compare
the top-1 transition-retrieval accuracy of WORLDE-
VOLVER’s action-based Episodic Memory and
RAWM-ϕ (Yang et al., 2025), using Gemma-4-
26B-A4B as the shared backbone throughout.
As discussed in Section 4.2, action-centered re-
trieval outperforms full state-action retrieval in both
environments, with a particularly large gain on
ALFWorld. State descriptions in these environ-
ments are lengthy and highly repetitive, whereas
action strings already encode task-relevant state in-
0.45 0.50 0.55 0.60 0.65 0.70 0.75 0.80
Prediction score
Exact Match
T oken F1
Cosine
ALFWorld
ScienceWorld
Figure 9: World Model Prediction across five randomly
seeded trajectory orders with uncertainty bands.
formation, including object identities and relations,
as in“take soapbottle 1 from shelf 1”in ALF-
World and“connect battery cathode to green light
bulb cathode”in ScienceWorld. RAWM- ϕ per-
forms (s, a)→(s, a, s′) retrieval: it matches the
full current state-action pair (st, at) against stored
state-action keys (si, ai) and returns the associated
transition (si, ai, si+1). Repetitive state descrip-
tions can therefore dominate the comparison and
dilute the action signal during transition matching.
Robustness to Evaluation OrderWe also evalu-
ate five random seeds for World Model Prediction,
each defining a different evaluation order over tra-
jectories. Figure 9 reports the mean and standard
deviation across the five orders in each environment
under the shared evaluation protocol used here.
The results are consistent across the five seeded
trajectory orders, indicating that performance is not
sensitive to the specific order in either environment.
Statistical Uncertainty and Success@1For
Gemma-4-26B-A4B, we compute task-level 95%
bootstrap confidence intervals from 10,000 resam-
ples and report Success@1, which records task suc-
cess on the first trial. Each cell in Table 12 reports
best-of-5 Success Rate [95% CI] / Success@1 in
percentage points for direct comparison.
WORLDEVOLVERw/ Ft has the highest best-of-
5 point estimate in all four settings, although the
confidence intervals overlap. It also achieves the
highest Success@1 among world-model methods
in all four settings. Across all methods, its Suc-
cess@1 is highest in both ScienceWorld settings,
ties the no-world-model baseline on ALFWorld
ReflAct, and trails it on ALFWorld ReAct.
Planning-Time Overhead and Memory Growth
Table 13 reports WORLDEVOLVERw/o Ft us-
ing Gemma-4-26B-A4B with kME =5 and kMS =1.
WM invocations include prediction and memory-
16
