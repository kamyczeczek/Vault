---
type: Concept
title: C1_corpus_whitespace_defect
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# C-1 — Retrieval benchmark baseline invalidated by corpus whitespace stripping

Date: 2026-09-26
Status: OPEN — blocks all retrieval-quality claims until corpus is repaired
Graph fingerprint at measurement: `44172cafee34`

## What was measured

`knowledge/graph/run_retrieval_benchmark.py` (8 cases, `retrieval_benchmark.json`) was re-run
against the live graph. The previously committed results were stamped `0ab25af68261`, so a
controlled A/B was run at one fixed fingerprint (`44172cafee34`) toggling only the `ask.py`
FTS bind order.

| Metric | pre-fix bind | fixed bind |
|---|---|---|
| mean_exact_precision | 0.146 | 0.050 |
| mean_exact_recall | 0.250 | 0.125 |
| mean_family_precision | 0.646 | 0.487 |
| mean_family_recall | 0.750 | 0.625 |
| mean_concept_coverage | 1.000 | 0.938 |
| mean_latency_ms | 16.4 | 159.7 |

**The bind fix made retrieval measurably worse.** That is the opposite of the assumption in the
previous session's handoff, which treated the fix as an unquestioned improvement. The fix is
still correct — it restores the intended FTS `MATCH` semantics — but it exposed a defect that
the broken bind had been hiding by making the precise path return `[]` and letting the cheap
alias path carry every query.

## Root cause

Corpus chunk bodies have had **whitespace stripped inside words**, on disk in
`knowledge/corpus/*.md`, not introduced by graph building.

```
disk:  "CausalInferenceinStatistics:APrimer\n(withMadelynGlymourandNicholasJewell)"
db:    "CausalInferenceinStatistics:APrimer"
```

- 7073 of 10364 nodes (68%) contain a 14+ character unbroken alphabetic run.
- A 400-node sample found 391/400 (98%) with a 12+ character run.
- FTS5 `unicode61` splits on whitespace, so `CausalInference` is a single token. The query term
  `causal` cannot match it. The gold chunk for `causal-intervention` contains no standalone
  token `\bcausal\b` in body or title at all.

Consequence: for the `causal-intervention` case, gold is absent from the AND path
(`gold_in_prec = 0`) **and** absent from the alias path (`gold_in_alias = 0`). No amount of BM25
`k1`/`b` tuning or reformulation can recover a term the index cannot see.

## Why this is a retrieval-blocking defect, not a tuning gap

1. `mean_exact_precision` fell 0.146 → 0.050 while `limit=5` and `_aggregate_families` reserves
   diversity slots. With the AND path now returning rows, it outranks the alias path that used to
   supply the correct family.
2. `ask.py:197` drops `alias_rows` entirely whenever `precise` is non-empty. Once `precise` stops
   returning `[]`, the alias path — which matched 2/2 gold families for `scientific-discovery` and
   1/1 for `agent-memory` — stops contributing.
3. Latency rose 16ms → 160ms because the AND path now runs real FTS scans and, for two cases,
   `_alias_rows` full-table `LIKE '%family%'` scans over a 747 MB database.

## Secondary defect found while profiling

`ask.py:197` alias-path drop, and `_alias_rows` is a 50ms-per-case sequential scan. Both are
tuning concerns, deferred; they are only measurable on a repaired corpus.

## What must happen before any retrieval claim is made

1. Repair the ingestion/extraction path that strips whitespace, and re-derive affected corpus
   chunks from their `knowledge/raw/` sources. This is a corpus change: it will move the graph
   fingerprint.
2. Rebuild the graph and re-run the benchmark. Expect exact recall to rise substantially; treat
   the pre-repair numbers in this record as void.
3. Re-annotate `retrieval_benchmark.json` gold ids if any chunk ids shifted during repair.
4. Only then measure BM25 `k1`/`b` for long-form chunks, and compare against this repaired
   baseline — not against `0ab25af68261`.

## Rejected approach

Tuning `k1`/`b` or adding query expansion first. Both optimize scoring over a token stream that
is already missing 68% of its words. That is the "optimize an unmeasured load-bearing claim"
failure the lab's own `causal-falsification-loops` rule warns against: the intervention point
here is upstream, in ingestion.
