---
type: Concept
id: 04_memory_for_autonomous_llm_agents_mechanisms_eval
title: "Memory for Autonomous LLM Agents: (part 5/15)"
source: "Memory for Autonomous LLM Agents Mechanisms, Evaluation, and Emerging Frontiers.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Table 1: Representative memory systems and benchmarks for LLM agents (2020–2026).
System Year Memory Category Distinguishing Feature
RAG [Lewis et al.,
2020]
2020 Non-parametric re-
trieval
First to couple a seq2seq generator with a dense docu-
ment retriever at NeurIPS 2020.
RETRO [Borgeaud
et al., 2022]
2022 Retrieval at scale Chunks retrieved from a 2-trillion-token corpus; 7.5B-
parameter model rivals 175B Jurassic-1 on 10/16
benchmarks.
ReAct [Yao et al.,
2022]
2022 Trajectory traces Reasoning-and-acting traces double as short-horizon
working memory; 34% absolute gain on ALFWorld.
Reflexion [Shinn
et al., 2023]
2023 Reflective episodic Verbal self-critiques stored as episodic memory; 91%
pass@1 on HumanEval (vs. 80% GPT-4 baseline).
Generative
Agents [Park et al.,
2023]
2023 Episodic + reflective 25 simulated characters autonomously organize a Valen-
tine’s party via observation–reflection–planning cycles.
V oyager [Wang et al.,
2023a]
2023 Procedural skill li-
brary
3.3×more unique items and 15.3×faster tech-tree pro-
gression than prior Minecraft agents.
LongMem [Wang
et al., 2023b]
2023 Long-form external Frozen backbone + residual side-network; memory bank
scales to 65k tokens.
ChatDB [Hu et al.,
2023]
2023 Structured symbolic SQL databases as agent memory; supports precise IN-
SERT/SELECT queries over interaction records.
ExpeL [Zhao et al.,
2024]
2024 Experiential learning Systematically extracts success/failure “rules of thumb”
from trajectory comparisons.
MemGPT [Packer
et al., 2024]
2024 Hierarchical virtual OS-inspired paging across main context, recall DB, and
archival vector store.
MemoryBank [Zhong
et al., 2024]
2024 Long-term with for-
getting
Ebbinghaus-curve decay applied to chatbot memory;
published at AAAI 2024.
LoCoMo [Maharana
et al., 2024]
2024 Benchmark Up to 35 sessions, 300+ turns, 9k–16k tokens per conver-
sation; humans still far ahead.
MemBench [Tan
et al., 2025]
2025 Benchmark Separates factual vs. reflective memory; participation vs.
observation modes; ACL 2025 Findings.
MemoryAgentBench [Hu
et al., 2025]
2025 Benchmark Tests four cognitive competencies; no current system
masters all four.
Agentic Memory [Yu
et al., 2026]
2026 Unified STM/LTM
policy
Memory ops trained as RL actions via step-wise GRPO;
outperforms all memory-augmented baselines on five
benchmarks.
MemoryArena [He
et al., 2026]
2026 Benchmark Multi-session interdependent tasks in four domains; near-
saturated LoCoMo models drop to 40–60% here.
querying them via natural language. This is a pragmatic
compromise: schema at write time, flexibility at read time.
4.3 Reflective and self-improving memory
Reflexion [Shinn et al., 2023] introduced a deceptively sim-
ple idea: after failing a task, have the agent write a natural
language post-mortem, then prepend it to the prompt on the
next attempt. No gradient updates, no reward model—just
a text file of self-critiques. The results were striking: 91%
pass@1 on HumanEval, versus 80% for GPT-4 without re-
flection.
Generative Agents [Park et al., 2023] built a richer
pipeline. Raw observations accumulate in an episodic
stream. Periodically, the agent clusters related observations
and synthesizes higher-orderreflections—e.g., “Klaus has
been eating alone and seems withdrawn.” Retrieval scores
memories by a weighted mix of recency (exponential de-
cay), relevance (embedding similarity), and importance (a
self-assessed integer). This multi-signal scoring is a sub-
stantial improvement over pure cosine similarity and re-
mains influential in later designs.
ExpeL [Zhao et al., 2024] pushes the paradigm further
by systematically contrasting successful and failed trajecto-
ries, extracting discriminative “rules of thumb,” and storing
them as reusable heuristics. Think-in-Memory [Liu et al.,
2024a] separates retrieval from reasoning: the agent first re-
calls, then performs a dedicated thinking step over the re-
called content before generating a response.
The central risk of reflective memory isself-reinforcing
error. If the agent incorrectly concludes “API X always
returns errors with parameter Y ,” it will avoid that call
path forever, never collecting evidence to overturn the false
belief. Over-generalization is the sibling risk: a lesson
learned in one context applied blindly in another. Qual-
ity gates—confidence scores, contradiction checking against
other memories, periodic expiration—are necessary but still
underdeveloped.
The problem becomes more acute at scale. A sin-
gle incorrect reflection in a short-lived agent causes lim-
ited damage; the same incorrect reflection persisting in
a long-running production agent—potentially influencing
thousands of downstream decisions over weeks—can be
catastrophic. The severity of the reflective memory failure
5
