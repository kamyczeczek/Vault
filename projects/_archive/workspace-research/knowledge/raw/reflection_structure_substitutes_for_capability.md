---
type: Concept
title: reflection_structure_substitutes_for_capability
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Structure substitutes for capability at the small-model end — that is the measured generalization, not "graphs beat search"

taxonomy: #retrieval #context-engineering #memory #knowledge-graph #determinism

**Problem.** "Walk the hops in code, not in the model" is easy to over-claim as a universal.
The evidence says something narrower and more useful.

**Symptom (measured).** graph-memory-starter (github.com/Glitch-Cat-Club, verified public
2026-09-16) ran one 3-hop question (policy → role → holder → delegate) across 3 model tiers
under two conditions. Searching, the model drove Grep+Read itself. Through the graph, a
recursive-CTE walk ran before the model was invoked and the model only read the result.

| Model | Search | Graph |
|---|---|---|
| Fable 5 | 3/3 hops, 6 calls, ~780 tok | 3/3, 0 calls, ~400 tok |
| Sonnet | 3/3, 13 calls, ~1180 tok | 3/3, 0 calls, ~400 tok |
| Haiku | **1/3, 5 calls, ~660 tok — WRONG** | **3/3, 0 calls, ~400 tok** |

**Root cause.** Only the weakest model flipped wrong→correct. Strong models reached the answer
either way; the graph only changed their cost. Independently confirmed at scale: arXiv
2603.11513 (360M–8B, oracle retrieval designed to isolate *use* from *find*) — with retrieval
guaranteed to contain the answer, models ≤7B still fail 85–100% of the time, the 7B model
extracts the correct answer only 14.6%, and the dominant failure mode is *irrelevant
generation* (61–100%): "the model ignores the provided context completely." Their conclusion:
for sub-7B models the bottleneck is **context utilization, not retrieval quality**.

**Design rule.** The correct generalization is *capability-conditional*: structure substitutes
for capability at the small-model end, and for cost at every tier. Do not record "graphs beat
search" — the strong-model rows refute it. Do record the mechanism: traversing in code removes
the *reasoning* load, which is the exact load small models cannot carry.

**Boundary.** One question, one corpus, no published variance — the flip could be noise even
though the mechanism is real. And the workspace's own `knowledge/graph/ask.py` is the RAG
(model-driven) half, which is correct *for a strong orchestrator*: it sits at the end of the
capability axis where model-driven retrieval is fine.

**Source.** `RESEARCH/2026-09-03_knowledge-architecture-research/` §7.2, reopened 2026-09-16.
