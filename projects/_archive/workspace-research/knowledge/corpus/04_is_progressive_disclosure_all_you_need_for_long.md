---
type: Concept
id: 04_is_progressive_disclosure_all_you_need_for_long
title: "Is Progressive Disclosure All You Need for Long-Context Agents? (part 5/17)"
source: "Is Progressive Disclosure All You Need for Long-Context Agents"
tags: [agentic, agents, anti-leakage, context-engineering, icm, memory, planning, prompt-engineering, reflection, progressive-disclosure]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

Table of Contents
| ch-01 | Walton, Arctic     |
| ch-02 | Victor’s youth     |
| ...   |                    |
3 · loaded on demand
references/
    chapter-01.md
    chapter-02.md
    ...
    chapter-31.md
always in context on activation on demand
Figure 1: Theflatpack. Example isFrankenstein.
3.2 The three approaches
We state each approach precisely, including which
artifacts stay in context versus load on demand,
because the practitioner literature does not sepa-
rate these. The flat and hierarchical packs
(Figure 1, Figure 2) differ only in where each arti-
fact sits on the disclosure timeline.
raw: raw-document navigation.The first ap-
proach exposes no skill pack. We place the raw
book in the sandboxed file system beside the ques-
tion and leave the agent’s navigation policy uncon-
strained. Depending on the harness, it may open
the whole file, grep first, or read only matched pas-
sages. This is the approach an agent falls back
on when no structure is prepared for it, and the
reference point against which we measure what
disclosure adds.
flat: single-level disclosure.The skill pack
is a single skill rooted at one SKILL.md file (Fig-
ure 1). Its description field is always in con-
text and describes the book as a whole, telling the
agent to open the skill whenever a question con-
cerns that title (discovery). Once the description
matches the task, the agent reads the SKILL.md
body: a table that indexes every chunk by its path
and its per-chunk description (activation). The
agent then reads one or more chunk files from
references/ based on that table (execution).
The per-chunk descriptions live in the body, so they
pay context only after the book activates.
hierarchical: recursive disclosure.Each
chunk becomes its own skill: a SKILL.md whose
description field is the chunk’s description
from Section 3.1 and whose body is the chunk con-
tent (Figure 2). A meta-router at the top carries a
book-level description and routes among the child
skills. The meta-router description and every child-
skill description are always in context (discovery).
The agent matches the task to one or more child de-
scriptions and reads the corresponding child bodies
on demand; for chunk content,activationandexe-
cutioncollapse, since the body is the content itself.
Reading a chunk is one step shorter than in flat,
because every chunk is already a skill whose de-
scription sits in context. hierarchical differs
from flat on two axes: the routing recurses one
level deeper, and the per-chunk descriptions move
from on-demand body context to always-loaded
description context.
3.3 What the comparison isolates
All three approaches hand the agent the identical
task instruction over the same book (Appendix Fig-
ure 5) and score its written answer with the same
deterministic verifier; only how the agent reaches
a passage changes: raw navigation, flat disclosure,
or hierarchical disclosure. We measure the three
approaches independently, then read two contrasts
between their accuracies to answer the two ques-
tions from Section 1.
The raw vs. flat contrast tests whether pro-
gressive disclosure helps at all on book-length un-
derstanding: whether a single description-gated
load of indexed chunks beats giving the agent only
the raw document and leaving navigation to it. The
flat vs. hierarchical contrast tests whether
depthof disclosure matters: whether promoting
per-chunk descriptions into always-loaded child
descriptions and adding a meta-router improves
routing enough to justify the always-loaded con-
text tax.
4 LOONGDOC: a long-context agent
environment
A static long-context reasoning benchmark scores
one answer string and stops there. It cannot watch
4
