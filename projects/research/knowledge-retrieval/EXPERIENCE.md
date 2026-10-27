---
type: Concept
title: EXPERIENCE
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# EXPERIENCE.md — knowledge-retrieval

Distilled on demand 2026-09-27 from live artifacts in this project.
Each lesson names its evidence. Nothing here is copied to the root —
the root links here (D11).

## Verified practices (smallest pieces first)

1. **Retire a metric that scores the annotation, not the system.**
   `mean_exact_recall` retired on three independent proofs (gold lacks the
   query term; gold unrankable even with family for free; 6/8 golds are front
   matter). Evidence: `references/measurements.md`.
   Lesson: a metric no retriever improvement can move is the wrong metric.
   Do not tune ranking against it.

2. **Quarantine chunks, never sources, never the corpus.**
   Source-level quarantine discarded 417 clean chunks to hide 419 damaged
   ones (all 828 of *Paradigms*, all 1,123 of *AIMA* over one bad chunk each)
   and removed an undamaged gold. Evidence: `references/measurements.md`
   "Superseded: source-level quarantine".
   Lesson: damage is chunk-level operational fact; the corpus is the record.

3. **Distrust the first detector's count by an order of magnitude.**
   First `check_corpus_health.py` reported 62% damage (6,401 hits); true count
   419 (4.0%). It fired on CamelCase identifiers and rare vocabulary.
   Discriminating signal: all-lowercase run, `MIN_GLUE_LEN = 32` (longest
   credible English token 28). Evidence: `references/defect-classes.md` §1.
   Lesson: over-reporting is its own defect class — an untrusted gate is unrunned.

4. **Assert relational properties, not local ones.**
   15 local-property gates passed continuously through all six defect classes.
   Every real failure was relational (claim↔evidence, id↔text).
   Evidence: `references/defect-classes.md` §6.
   Lesson: a gate ships the bug it prevents — write it after the defect, with
   a regression test.

5. **An id that resolves proves nothing about what it resolves to.**
   Chunk ids are `NN_<slug>`; re-ingest renumbers prefixes, slug stays — one
   slug, many chunks. Five of eight benchmark golds name a chunk the retriever
   did not return (right family, wrong page). Evidence: `CONTEXT.md` Open work
   + `references/defect-classes.md` §4.
   Lesson: gold must exist AND contain every required concept; family metrics
   are blind to within-family drift by construction.

6. **Freeze the corpus before measuring.**
   Benchmark over a moving corpus measures drift, not retrieval. Record graph
   fingerprint first. Evidence: `CONTEXT.md` Process §1; standing-table vs
   artifact dispute (0.746 claimed vs 0.629 in
   `retrieval_benchmark_results.json` at fingerprint `0a5b47437367`).
   Lesson: a headline number with no artifact behind it is unverified.

7. **Precision is the honest number.**
   Recall 0.938 with precision 0.654 means the right book plus front matter.
   Family recall 1.0 + exact recall 0.0 = right book, wrong page.
   Evidence: `CONTEXT.md` "The three measurements that matter".
   Lesson: read precision first; recall alone scores pile as success.

## Composed rule (what the pieces add up to)

> Measure the retriever, quarantine the chunk, gate the relation.
> Write down what each metric cannot see.

## Known-unresolved (not practices yet)

- Within-family ranking unmeasured; 8 of 23 annotated questions used; levels 3–5 absent; distractor field unused by harness.
- p95 latency under token-budgeted gateway unmeasured (`ask.py` 99.4 ms ≠ gateway).
- Two-hop traversal never run (one-hop +0.0323 recall only).
- Semantic/hybrid re-decision deferred — old justification (family recall 0.958) stale against current 0.875 artifact.
- 2 chunks still damaged on disk (excluded, not repaired); damage-row denominator stale (10,364 vs 10,337 today).

## Skills used

None vendored (D8 lazy). This project measures; it needed no workflow skill to date.
