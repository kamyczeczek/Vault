---
type: Concept
id: 01_graph_memory_starter_inventory
title: "graph-memory-starter — knowledge-graph + RAG memory for AI assistants (source inventory) (part 2/2)"
source: "graph-memory-starter-inventory.md"
tags: [context-engineering, determinism, hooks, knowledge-graph, memory, prompt-engineering, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

**Ontology (fixed before any doc was written).** Entity types PERSON/ROLE/POLICY/PROCESS/
DOCUMENT. Predicates `approved_by, held_by, delegates_to, part_of, references`. Conditions
(amounts, dates, windows) live in the entity description, never on the edges.

**Evals (README, "Glitch Cat Club evals, Aug 2026").** One 3-hop question (policy → role →
holder → delegate), 3 model tiers × 2 conditions. Haiku: search = 1 of 3 hops, wrong, 5 calls,
~660 tok; graph = 3 of 3, correct, 0 calls, ~400 tok. Sonnet 13 calls/8 docs/~1180 tok vs
0/0/~400. Fable 5: 6/4/~780 vs 0/0/~400. Retrieval 2 ms; the ~400-token injection is fixed at
any corpus size. External validation of these claims, and the correspondence to this
workspace's own `ask.py`/corpus/folder-vocabulary design, is recorded in
`RESEARCH/2026-09-03_knowledge-architecture-research/` §7.

**Source.** `https://github.com/Glitch-Cat-Club/graph-memory-starter`; full dump
`knowledge/raw/graph-memory-starter.txt`.
