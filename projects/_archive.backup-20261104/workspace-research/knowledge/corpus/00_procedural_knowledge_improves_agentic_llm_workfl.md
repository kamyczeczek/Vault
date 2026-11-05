---
type: Concept
id: 00_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 1/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Procedural Knowledge Improves Agentic LLM Workflows
Vincent Hsiao
NRC Postdoctoral Fellow, Naval Research Laboratory
Washington, DC
United States
vincent.hsiao.ctr@us.navy.mil
Mark Roberts
Navy Center for Applied Research in AI, Naval Research Laboratory
Washington, DC
United States
mark.c.roberts20.civ@us.navy.mil
Leslie Smith
Navy Center for Applied Research in AI, Naval Research Laboratory
Washington, DC
United States
leslie.n.smith20.civ@us.navy.mil
November 12, 2025
Abstract
Large language models (LLMs) often struggle when performing agentic tasks without
substantial tool support, prom-pt engineering, or fine tuning. Despite research showing
that domain-dependent, procedural knowledge can dramatically increase planning ef-
ficiency, little work evaluates its potential for improving LLM performance on agentic
tasks that may require implicit planning. We formalize, implement, and evaluate an
agentic LLM workflow that leverages procedural knowledge in the form of a hierarchical
task network (HTN). Empirical results of our implementation show that hand-coded
HTNs can dramatically improve LLM performance on agentic tasks, and using HTNs can
boost a 20b or 70b parameter LLM to outperform a much larger 120b parameter LLM
baseline. Furthermore, LLM-created HTNs improve overall performance, though less
so. The results suggest that leveraging expertise–from humans, documents, or LLMs–to
curate procedural knowledge will become another important tool for improving LLM
workflows.
KeywordsLarge Language Models, Agentic Systems, Task Networks
1 Introduction
Procedural knowledge generally describes a sequence for solving a problem and has played an important
role in AI. For example, spanning nearly 50 years of automated planning research, procedural knowledge
has been effective for areas such as decomposing abstract tasks into concrete actions (27; 2), control
rules for search (1), learning macro operators (6), plan recognition (7), knowledge-based planning (18),
and planning and acting ( 8), to name only a few. Procedural knowledge also plays a central role in
DISTRIBUTION STATEMENT A.Approved for public release; distribution is unlimited.
arXiv:2511.07568v1  [cs.AI]  10 Nov 2025
