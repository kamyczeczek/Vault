---
type: Concept
id: 15_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 16/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Per-chunk description prompt
You are summarizing one section of a long book to help an
agent navigate the book later. Read the section below and
produce:
1. A one- or two-sentence summary of what this section covers.
2. A comma-separated list of key elements: named characters,
locations, organizations, or central topics that appear in
this section.
Output format (exactly this; no extra prose, no Markdown
headers):
SUMMARY: <one to two sentences>
KEY_ELEMENTS: <comma-separated list>
Book-level description prompt
You are writing a one-line description of an unknown book
based on the chapter-by-chapter summaries below. Your output
is shown to an agent that needs to decide whether this book
is likely to contain the answer to a user’s question --
without spoiling the book’s identity.
Strict rules:
- Output exactly 1 or 2 sentences describing the book’s plot,
setting, and central conflict.
- Do NOT name, guess, or restore the book’s title, author, or
any canonical name. The character and place names in the
input have been anonymized; use only the names that
literally appear in the input text, and do not infer the
"real" name behind any character.
- Do not begin with "This book", "The novel", or similar
boilerplate; just describe what happens.
- Do not use quotes, bullet points, headings, or Markdown.
Reply with the summary paragraph only -- no preamble, no
closing remarks.
Figure 7: The two prompts that generate routing metadata in the book-to-skill pipeline (Section 3.1). The per-chunk
description prompt runs once per chunk and produces the description the agent reads before opening the chunk. The
book-level description prompt runs once per book over the chunk descriptions and produces the always-in-context
text that gates discovery.
Book text Chunk store
text + stable IDs
BM25 index
Question
BGE-M3
vectors
BM25 retrieval
ranked IDs
Dense retrieval
ranked IDs
RRF fusion
merge ranked IDs
BGE reranker
score chunk text
Evidence prompt
question +
top-k chunks
Answer modelFinal answer
Figure 8: Hybrid RAG baseline pipeline. The chunk store builds separate sparse and dense indexes; the question
queries both retrievers, RRF merges their ranked chunk IDs, and the reranked evidence is passed to the answer
model.
visually. The rescue that the table reports as num-
bers becomes geometry: at K=20 the flat pack
alone holds the high-accuracy end of the frontier
(0.462), while raw and hierarchical collapse
together to 0.257 and 0.267, twice as far down
the accuracy axis. The gap is wider than any-
thing on the En.MC plane, where the three con-
figurations stay within a standard error at every
15
