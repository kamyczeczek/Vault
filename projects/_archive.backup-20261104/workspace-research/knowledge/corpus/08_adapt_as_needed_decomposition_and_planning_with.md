---
type: Concept
id: 08_adapt_as_needed_decomposition_and_planning_with
title: "ADAPT: As-Needed Decomposition and Planning with Language Models (part 9/28)"
source: "ADAPT As-Needed Decomposition and Planning with Language Models.pdf"
tags: [LLM, Products, Think, agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Executor LM Planner LM Success Rate
GPT-3.5 − 38.4
GPT-3.5 GPT-3.5 58.3
LLaMA-2-70B − 20.4
LLaMA-2-70B GPT-3.5 43.3
Table 4: ADAPT improves performance on ALFWorld
(dev) when using different planner and executor LLMs.
advanced LLM be used to devise plans. To this
end, we explore different combinations of planner
and executor LLM, with the latter using both gated
and open-source models on ALFWorld.
Results. Table 4 shows that ADAPT can suc-
cessfully be used to generate plans from one LLM
that are useful to a different, possibly smaller, ex-
ecutor LLM, improving success rates by up to
19.9% compared to the executor-only (ReAct) set-
ting. Interestingly, using an open-source model,
such as LLaMA-2-70B-chat (Touvron et al., 2023)
can be used as an executor with a more advanced
LLMs such as GPT-3.5 to improve success rates
by 22.9% points. Since the planner LLM is used
sparingly, open-source executors can dramatically
decrease the monetary or computational costs of us-
ing ADAPT. We defer combining knowledge from
stronger and weaker LMs within ADAPT to future
work, as examined in the context of mathematical
reasoning (Fu et al., 2023; Saha et al., 2023a).
6.5 How does ADAPT compare to baselines in
terms of LLM calls?
Setup. Performance of decision-making agents
can be enhanced by increasing the number of calls
allowed to an LLM, e.g., number of retrials in Re-
flexion. To verify that the gains in ADAPT are
not simply due to higher number of LLM calls, we
compare the average of number of LLM calls made
by ADAPT to the baselines.
Results. Fig. 7 shows that a ADAPT employs a
comparable number of LLM calls w.r.t. Try-Again
and Reflexion baselines in order to yield perfor-
mance improvements discussed in Sec. 5 (Tables 1
and 2). Note that while all methods including Re-
Act and Plan-and-Execute baselines are offered a
comparable computational budget, the actual num-
ber of LLM calls used by the latter is often lower
due to their inability to handle intermediate exe-
cution failures. This strengthens the argument for
effectiveness of ADAPT as the improvements do
AlfWorld WebShop T extCraft
0
10
20
30Avg. #LLM Calls
ReAct
Plan-&-Exec
Try Again
Reflexion
ADaPT
Figure 7: Average number of LLM calls for each ap-
proach including ADAPT and baselines discussed in
Sec. 4.2 with GPT-3.5 LLM across datasets.
not simply stem from using substantially higher
number of calls to the LLM.
7 Conclusion
We introduce ADAPT, a recursive algorithm de-
signed to harness the planning capabilities of
LLMs, dynamically decomposing complex tasks
when the LLM acting as an executor encoun-
ters challenges. Our evaluation across three di-
verse decision-making tasks, ALFWorld, WebShop,
and TextCraft, reveals impressive performance of
ADAPT, surpassing existing baselines by substan-
tial margins of up to 28.3%, 27%, and 33% points,
respectively. This not only underscores the effec-
tiveness of ADAPT but also highlights the signif-
icance of as-needed decomposition in enhancing
task performance. Moreover, our findings demon-
strate that ADAPT not only adapts to the capabili-
ties of the underlying executor LLM but also takes
into account the complexity of individual task in-
stances, showcasing its versatility and effectiveness.
Acknowledgements
Part of this work was done during internship at
AI2 and was partially supported at UNC by NSF-
CAREER Award 1846185, NSF-AI Engage Insti-
tute DRL-2112635, DARPA Machine Common-
sense (MCS) Grant N66001-19-2-4031,. We sin-
cerely thank Bodhisattwa Prasad Majumder, Chris
Callison-Burch, Shashank Gupta, Peter Jansen, Bill
Yuchen Lin and the Aristo team for their valuable
feedback. We also thank Swarnadeep Saha, Elias
Stengel-Eskin, and Peter Hase for their feedback.
9
