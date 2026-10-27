---
type: Concept
id: 03_memory_for_autonomous_llm_agents_mechanisms_eval
title: "Memory for Autonomous LLM Agents: (part 4/15)"
source: "Memory for Autonomous LLM Agents Mechanisms, Evaluation, and Emerging Frontiers.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

archival_memory_searchare canonical exam-
ples [Packer et al., 2024]. Quality here hinges on the
LLM’s instruction-following ability and on how well the
memory API is documented in the system prompt.
Learned controltreats memory operations as policy ac-
tions optimized end-to-end. Agentic Memory [Yu et al.,
2026] trains store, retrieve, update, summarize, and discard
as callable tools via a three-stage RL pipeline with step-wise
GRPO. The payoff is substantial—learned policies discover
non-obvious strategies such as preemptive summarization
before the context is full—but so is the training cost.
3.4 Representative systems at a glance
Table 1 plots key systems and benchmarks on a timeline.
4 Core Memory Mechanisms
We now examine each mechanism family in detail, ground-
ing the discussion in concrete system designs and their em-
pirical trade-offs.
4.1 Context-resident memory and compres-
sion
The most straightforward way to give an agent memory is to
keep relevant information in the prompt. System messages,
recent conversation turns, scratchpad notes—everything the
LLM “sees” on every call functions as working memory
with perfect in-window recall.
The trouble starts when history outgrows the window.
Several compression strategies have emerged: (i)sliding
windowsthat retain thenmost recent turns and drop the rest;
(ii)rolling summariesthat periodically condense older his-
tory into a shorter precis; (iii)hierarchical summariesop-
erating at turn, session, and topic granularities; (iv)task-
conditioned compression, where the current query decides
which parts of history keep full detail. The Self-Controlled
Memory system [Liang et al., 2023] hands this decision to
the agent itself, letting it choose which segments deserve
verbatim retention versus aggressive condensation.
Context-resident memory is transparent and
infrastructure-free, but it carries a well-known pathol-
ogy:summarization drift. Each compression pass silently
discards low-frequency details. After enough passes,
the agent “remembers” a sanitized, generic version of
history—precisely the kind of memory that fails on edge
cases. Extending context windows to 100k+ tokens [Chen
et al., 2023] delays the problem but cannot eliminate it, and
longer contexts incur quadratic cost increases in attention.
To make this concrete: consider an agent that processes
50 user interactions per day. After one week of rolling sum-
marization, the raw 350-turn history has been compressed
through at least three summary cycles. A rare but critical
instruction from day one—say, “never call the production
database directly”—may survive the first compression but
is exactly the kind of low-frequency, high-importance de-
tail that tends to vanish by the third pass. The agent then
proceeds to call the production database, with predictable
consequences.
This is not a hypothetical failure mode; it mirrors re-
ported issues in deployed long-running chatbots and cod-
ing assistants. The implication is clear: for any agent ex-
pected to run for more than a handful of sessions, context-
resident memory should be supplemented—not replaced,
but supplemented—with an external store that preserves raw
records at full fidelity.
A less obvious but equally important limitation of
context-resident memory isattentional dilution. Even
within a sufficiently large window, the LLM’s attention
mechanism must distribute capacity across all tokens. As
more memory content is injected, the model’s ability to
focus on any single piece degrades—a phenomenon em-
pirically documented in the “lost in the middle” literature,
where information placed in the center of a long context is
recalled less reliably than information at the beginning or
end. This suggests that simply making the window bigger
is not a complete solution; the agent must alsocuratewhat
enters the window, which brings us back to the fundamental
need for retrieval and filtering mechanisms.
4.2 Retrieval-augmented memory stores
RAG [Lewis et al., 2020] demonstrated that pairing a gen-
erator with a non-parametric retrieval index produces strong
results on knowledge-intensive tasks. In agent settings, the
store is populated not with encyclopedia articles but withliv-
ing interaction records: tool call logs, environment observa-
tions, user corrections, partial plans, and verbal reflections.
Indexing granularity.Fine-grained indexing (individ-
ual tool calls or single sentences) gives precise recall but
can fragment multi-step reasoning into meaningless shards.
Coarse-grained indexing (full sessions or long passages)
preserves context but drowns the signal in noise. The prac-
tical sweet spot is multi-granularity indexing, where the re-
triever adaptively selects the right resolution. Dense passage
retrieval [Karpukhin et al., 2020] via learned encoders, typ-
ically backed by FAISS-style approximate nearest-neighbor
search [Johnson et al., 2021], remains the default implemen-
tation, often augmented with sparse BM25 and metadata fil-
ters (timestamps, tool types, task tags).
Query formulation.A subtlety that many systems gloss
over: the agent’s immediate inputx t is often a poor retrieval
query. A user asking “Why did that crash?” needs the
agent to retrieve the crash log from two sessions ago, not
the most semantically similar sentence. Strategies include
LLM-reformulated queries, multi-query fan-out with result
fusion, and using the current subgoal as an additional re-
trieval signal. Self-RAG [Asai et al., 2024] goes one step
further and teaches the model to decidewhetherretrieval is
warranted at all—a simple gate that substantially cuts un-
necessary latency.
Scale.RETRO [Borgeaud et al., 2022] and follow-up
work on trillion-token datastores [Raad et al., 2024] sug-
gest that retrieval memory can scale to years of interaction
history without architectural changes. The bottleneck shifts
decisively from storage torelevance: ensuring that the most
useful—not merely the mostsimilar—records are returned.
Read-write memory.RET-LLM [Sun et al., 2024]
bridges free-form retrieval and structured storage by let-
ting the agent write structured triplets at storage time while
4
