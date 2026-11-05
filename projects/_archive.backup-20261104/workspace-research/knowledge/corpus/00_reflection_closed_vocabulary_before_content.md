---
type: Concept
id: 00_reflection_closed_vocabulary_before_content
title: "Closed vocabulary before content is the defensible core — content-addressed identity makes structure walkable"
source: "reflection_closed_vocabulary_before_content.md"
tags: [context-engineering, determinism, domain-modeling, knowledge-graph, memory, prompt-engineering, reflection, retrieval]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Closed vocabulary before content is the defensible core — content-addressed identity makes structure walkable

taxonomy: #determinism #knowledge-graph #domain-modeling #retrieval

**Problem.** A knowledge graph's value is usually attributed to the database or the query
language. The load-bearing decision is earlier and cheaper.

**Symptom (first-hand, from source).** graph-memory-starter fixes its ontology *before* writing
any document: entity types PERSON/ROLE/POLICY/PROCESS/DOCUMENT; predicates approved_by,
held_by, delegates_to, part_of, references. Node identity is `uuid5(NAMESPACE_OID,
f"{type}:{name}")`, so "Ops Manager" declared in doc 1 and doc 4 is the *same node* — no
lookup, no ML, no embedding similarity. Conditions (amounts, dates, windows) live on the
entity description, never on the edges.

**Root cause.** Identity is content-addressed, so the build is deterministic and the traversal
is reproducible. Because identity does not depend on a model judging similarity, the query path
needs **no LLM at all** — a recursive CTE walks k hops in 2 ms. And because the result is a
bounded set of triples, the injected context is ~400 tokens *regardless of corpus size*:
growth is absorbed at build, not at query. Corroboration that this is an industry pattern, not
a local trick: cognee ships a `namespace_entity_type_node_ids.py` migration and a merged PR
"deterministic key-based entity dedup via merged_into edges (SDK-208)" — the same
namespace+type+name keyed dedup at framework scale.

**Design rule.** Fix the vocabulary first; everything downstream becomes mechanical. The
workspace already applies this at a different grain: `CONTEXT.md` per folder and routing
tables are a closed vocabulary that makes navigation walkable; the corpus chunk id is a stable
handle to a lossless payload; `check_reflection.py`'s dead-route check fails when a tag is
absent from the vocabulary — a closed vocabulary that is actually enforced.

**Boundary.** A closed vocabulary trades surprise for coverage: out-of-vocabulary questions
return `(no memory matches for this prompt)` rather than a guess. That loud failure is a
feature, but it means the vocabulary must be maintained, or questions silently go unanswered.

**Source.** `RESEARCH/2026-09-03_knowledge-architecture-research/` §7.5 and §7.7, reopened
2026-09-16.
