---
type: Concept
id: 00_memory_for_autonomous_llm_agents_mechanisms_eval
title: "Memory for Autonomous LLM Agents: (part 1/15)"
source: "Memory for Autonomous LLM Agents Mechanisms, Evaluation, and Emerging Frontiers.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Memory for Autonomous LLM Agents:
Mechanisms, Evaluation, and Emerging Frontiers
Pengfei Du1
1 Hong Kong Research Institute of Technology, HongKong, China
E-mail: lldpf1234@gmail.com
Abstract
Large language model (LLM) agents increasingly oper-
ate in settings where a single context window is far too
small to capture what has happened, what was learned,
and what should not be repeated. Memory—the abil-
ity to persist, organize, and selectively recall information
across interactions—is what turns a stateless text genera-
tor into a genuinely adaptive agent. This survey offers
a structured account of how memory is designed, imple-
mented, and evaluated in modern LLM-based agents, cov-
ering work from 2022 through early 2026. We formalize
agent memory as awrite–manage–readloop tightly cou-
pled with perception and action, then introduce a three-
dimensional taxonomy spanning temporal scope, represen-
tational substrate, and control policy. Five mechanism fam-
ilies are examined in depth: context-resident compression,
retrieval-augmented stores, reflective self-improvement, hi-
erarchical virtual context, and policy-learned management.
On the evaluation side, we trace the shift from static re-
call benchmarks to multi-session agentic tests that interleave
memory with decision-making, analyzing four recent bench-
marks that expose stubborn gaps in current systems. We
also survey applications where memory is the differentiat-
ing factor—personal assistants, coding agents, open-world
games, scientific reasoning, and multi-agent teamwork—
and address the engineering realities of write-path filtering,
contradiction handling, latency budgets, and privacy gover-
nance. The paper closes with open challenges: continual
consolidation, causally grounded retrieval, trustworthy re-
flection, learned forgetting, and multimodal embodied mem-
ory.
Keywords:large language model agents; agent memory;
long-term memory; retrieval-augmented generation; contin-
ual adaptation; agent evaluation
1 Introduction
Scaling large language models has unlocked a new class of
autonomous software agents—systems that perceive envi-
ronments, reason about goals, wield tools, and take action
over extended time horizons [Brown et al., 2020, Achiam
et al., 2023, Touvron et al., 2023]. What separates these
agents from a vanilla chatbot is not merely bigger models; it
is the expectation that theylearn from experience. A coding
assistant should remember that a particular API is flaky, a
game-playing agent should recall which crafting recipes it
already mastered, and a personal scheduler should never ask
a user’s birthday twice. All of this demands memory.
1.1 What goes wrong without it
Picture a debugging assistant that works on a large codebase
across a week of sessions. Without memory, every Mon-
day morning it rediscovers the directory layout, re-reads the
same README, and—worst of all—retries the exact fix
that crashed the build on Friday. Equip the same agent with
even a modest memory module and the dynamic shifts: it
arrives already knowing the hotspots, skips the dead ends,
and gradually distills project-specific heuristics.
This is not a marginal improvement; it is a qualitative
change. Memory transforms a stateless LLM into aself-
evolvingagent [Zhang et al., 2024a] that can (i) accumu-
late factual knowledge and user preferences, (ii) develop be-
havioral patterns grounded in prior experience, (iii) avoid
repeating costly mistakes, and (iv) continuously improve
through interaction.
1.2 A brief history of neural memory
The ambition to give neural networks external storage dates
back over a decade. Memory Networks [Weston et al., 2015]
and their end-to-end variant [Sukhbaatar et al., 2015] intro-
duced differentiable read-write access to external slots for
question answering. Neural Turing Machines [Graves et al.,
2014] and Differentiable Neural Computers [Graves et al.,
2016] pushed further, supporting both content-based and
location-based addressing over a memory matrix. Memoriz-
ing Transformers [Wu et al., 2022] and Recurrent Memory
Transformers [Bulatov et al., 2022] later integrated explicit
memory layers directly into the Transformer backbone.
A parallel thread focused on retrieval. RAG [Lewis et al.,
2020] married a pre-trained generator with a dense docu-
ment retriever, and RETRO [Borgeaud et al., 2022] showed
that pulling from atrillion-token corpus at inference time
could match much larger models at a fraction of the param-
eter count. These systems proved a crucial point: external
knowledge stores can be queried dynamically during gener-
ation without retraining.
The leap from retrieval-augmentedmodelsto memory-
augmentedagentshappened quickly. ReAct [Yao et al.,
2022] interleaved reasoning traces with environment ac-
tions, producing an interpretable trajectory that doubles
as short-horizon memory. Reflexion [Shinn et al., 2023]
took this further by storing verbal self-critiques after task
attempts—essentially giving the agent a post-mortem jour-
nal. Then came the Generative Agents paper [Park et al.,
1
arXiv:2603.07670v1  [cs.AI]  8 Mar 2026
