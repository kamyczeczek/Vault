---
type: Concept
id: 01_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 2/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

ure 1) exposes it as a single SKILL.md whose
always-loaded description routes the agent to the
book and whose body indexes chunk files under
references/ that it reads on demand. Hier-
archical disclosure ( hierarchical, Figure 2)
pushes the same idea one level further: each chunk
becomes its own skill with an always-loaded de-
scription, and a meta-router routes among them.
Both are progressive disclosure in the sense of An-
thropic (2025b); they differ only in routingdepth
and in whether per-chunk descriptions pay always-
loaded ( hierarchical) or load-on-activation
(flat) context.
We build both disclosure packs by implement-
ing the widely adoptedbook-to-skillrecipe (Vir-
gilio Jr., 2026): split a book along its own struc-
ture into chunks, then attach a short LLM-written
description to each; both packs share one chunk
set, so the only thing that varies is how the agent
reaches a passage. To run the comparison, we turn
∞Bench (Zhang et al., 2024a) into an agent en-
vironment, following the practice of established
prior evaluation work (Merrill et al., 2026; Li et al.,
2026), and we test across three agent harnesses and
three model families, with hybrid-rag, a clas-
sical retrieve-and-rerank baseline, as an external
reference.
Our findings are three-fold. On a single book,
flat disclosure helps only to the extent that the
agent cannot already navigate the document: it
matches or exceeds raw-document navigation un-
der Pi and Claude-Code, but adds nothing under
Codex, whose bare model already greps for the en-
tities each question names. The hierarchical pack
never beats the flat one, and sometimes collapses
accuracy outright, dropping En.MC from 0.9126
to 0.6398 on Pi gpt-5.4-mini. At library scale
the picture flips: bundling twenty books sinks even
Codex under raw navigation, where English open
QA falls to 0.26, while flat disclosure holds it at
0.46. The same scaling is an efficiency loss, not
only an accuracy loss: as the corpus grows, accu-
racy falls and the per-question cost of reaching any
fixed accuracy rises, so a larger library is strictly
less efficient to read. Progressive disclosure thus
buys context, not intelligence: its gain is negligible
for a single book under a strong agent but deci-
sive for a library, and one level is enough. Our
contributions are:
1. A controlled comparison of three agentic
reading approaches (Section 3).We cast
raw-document navigation, flat disclosure, and
hierarchical disclosure as three routes to the
same book, building the two disclosure packs
over one fixed chunk set so that only the
wiring varies.
2. A long-context agent environment (Sec-
tion 4).We turn static book QA into an inter-
active environment that logs the agent’s tra-
jectory and emits a per-run reward, a repro-
ducible testbed for long-context agents.
3. The first systematic study of progressive dis-
closure for long-document understanding
(Section 5).We measure a pattern practition-
ers argue at scale but have never validated,
on ∞Bench across three harnesses and three
model families.
2 Related work
2.1 Reading long documents
Long-context modeling.Bigger context win-
dows have not bought uniformly better long-
context use: Liu et al. (2024) document U-shaped
performance over context position, and Hsieh et al.
(2024) show effective context size lagging far
behind the advertised window. We evaluate on
∞Bench (Zhang et al., 2024a), a book-length
benchmark (Bai et al., 2024, 2025; Wang et al.,
2025; Karpinska et al., 2024; Koˇciský et al., 2018)
where frontier models degrade heavily, so an agen-
tic alternative earns a controlled test.
Retrieval augmented generation.Retrieval
augmented generation (RAG) softens raw long-
context degradation but stays unstable across tasks:
long context wins when resources permit while re-
trieval wins on cost (Li et al., 2024), and the recent
literature reaches contradictory conclusions (Li
et al., 2025). Hierarchical retrieval augments flat
chunk-and-rank with tree summaries, cascading
metadata, and entity graphs (Sarthi et al., 2024;
Chen et al., 2024; Edge et al., 2024), improving
coverage on book-length and larger inputs but lock-
ing the structure inside the retriever. We instead
expose the same hierarchy as an artifact the agent
reads and navigates directly.
Agentic reading.A parallel line lets the model
navigate the document directly: recursive summary
trees (Chen et al., 2023), gist-based pagination with
lookup on demand (Lee et al., 2024), typed query-
decomposition plans (Sun et al., 2024), and multi-
2
