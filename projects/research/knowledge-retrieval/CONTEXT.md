---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# CONTEXT.md — knowledge-retrieval

One job: answer the question "does retrieval return the right passage, with intact
evidence?" — and produce the number, the defect list, and the gate that keeps each
defect from returning.

## Inputs

- Working (this run): `../../_archive/agentic-research-lab/knowledge/corpus/*.md` — the chunks under test
- Working (this run): `../../_archive/agentic-research-lab/subprojects/vera/benchmark/QUESTIONS.md` — the annotated question set
- Reference (every run): `references/defect-classes.md`
- Reference (every run): `references/measurements.md`

## Process

1. **Freeze the corpus.** Record the graph fingerprint before the run. A benchmark
   over a moving corpus measures corpus drift, not retrieval.
2. **Annotate by hand, verify mechanically.** A gold chunk id must resolve *and*
   contain the required concepts. A backticked id in prose is not evidence.
3. **Measure.** Family recall, concept coverage, family precision, latency.
4. **Triage the damage.** Damaged chunks are excluded at query time, never deleted
   from the corpus.
5. **Record the verdict** in `reports/`, including which metric retired and why.

## Outputs

- `reports/<round>_<finding>.md` — the investigation record
- Updated `references/measurements.md` and `references/defect-classes.md`
- A gate in `../../_archive/agentic-research-lab/scripts/check_*.py` for each new defect class

## Human check

Read the report and ask: does the number describe the retriever, or does it
describe the annotation? A metric that cannot be improved by making the retriever
better is measuring the wrong thing — retire it, write down the three proofs, and
pick a new one. Then check the precision number specifically: recall can be
trivially high while returning nothing useful.

## The three measurements that matter

| Metric | Question | Healthy when |
|---|---|---|
| Family recall | Did the right *source* appear in the results? | > 0.85 |
| Concept coverage | Did the required terms survive extraction? | > 0.95 |
| Family precision | Of what came back, how much is on-topic? | **this is the honest one** |

Family precision is the weak number and the one worth improving. High recall with
low precision means the retriever returns the right book and a pile of front
matter beside it — a failure a reader notices immediately and a recall metric
scores as a success.

## Why a damaged chunk is quarantined, not repaired

Source-level quarantine was tried and reverted: it discarded 417 clean chunks to
hide 419 damaged ones, evicting all 828 chunks of one book and all 1,123 of
another over a single damaged chunk each. Quarantine is chunk-level. The corpus is
the record of what was ingested; damage is an operational fact about specific
chunks, and it is tracked there.

## Open work

Everything below was read out of the live artifacts on 2026-09-27, not carried
over from a prior round. The standing numbers in `references/measurements.md` are
the reference; these are the questions that number does not answer.

### RESOLVED (2026-10-16) — the standing table's 0.746 had no artifact

The table's "Not yet measured" note carried 0.746 while the table itself carried
0.654. 0.746 was unverified and is now retired: it lived only in the C-6 commit
message, and no benchmark run behind it was ever recorded. The number with an
artifact is 0.654 (`mean_family_precision`) with `mean_latency_ms` 100.188, at
fingerprint `0a5b47437367` in
`../../_archive/agentic-research-lab/knowledge/graph/retrieval_benchmark_results.json`
(the same fingerprint on disk now). `references/measurements.md` now carries
0.654 and no longer states 0.746. `0.629` is the pre-reranking baseline the table
already labels as such. Correction to the prior entry: it recorded the artifact
as 0.629 / 112.601 ms; the file on disk reads 0.654 / 100.188 ms.

### Five of eight golds name a chunk the retriever did not return

This is defect class 4 — an id that resolves proves nothing about *what* it
resolves to — recurring in the benchmark spec itself. Chunk ids are
`NN_<slug of filename>`, and a re-ingest renumbers the prefix while keeping the
slug, so one slug now resolves to many chunks. In five of the eight cases the
retriever returned a *different* chunk of the *correct* family: family recall
1.0, exact recall 0.0, and the returned id carrying the gold's slug under a
different prefix.

| Case | Gold id | Returned instead |
|---|---|---|
| `production-reliability` | `05_building_llms_for_production…` | `345_building_llms_for_production…` |
| `automl-experiment` | `31_automated_machine_learning…` | `139_automated_machine_learning…` |
| `multiagent-coordination` | `55_multiagent_systems_algorithmic…` | `10_multiagent_systems_algorithmic…` |
| `causal-intervention` | `25_the_book_of_why…` | `10_the_book_of_why…` |
| `graph-scaling` | `02_graph_databases_new_opportunities…` | same slug, other prefix |

Both ids resolve and both chunks carry the required concepts, so
`check_citation_integrity.py` passes. The texts differ: `05_…` opens *Preface*
while `345_…` opens mid-chapter. Family metrics are blind to this by construction
— `family()` strips the prefix — so `mean_family_recall` 0.875 and every other
family number stay green while half the cases are scored against a passage the
reader never asked for. No gate can assert the gold is the *best* chunk of its
family, because "best" is an annotation judgement. The open question is how much
of family precision 0.629 is real off-topic pile and how much is this. It has
not been decomposed.

### `planning-workflow` fails for a reason no metric classifies

It is the one case at `family_recall` 0.0, and it is not a precision failure or a
ranking failure. All five hits are on-topic long-horizon planning documents, and
the gold is `06_full_walkthrough_workflow_for_ai_coding_matt_poc` — a 91,778-char
chunk whose body opens `(0:07) [music] >> Yeah, we're good…`. It is a transcript,
and the query `agent planning decomposition long horizon workflow` is answered by
four on-topic documents the retriever preferred. Either the gold is a bad
annotation (defect class 2 again, in a new disguise — front matter was the old
shape, an unanswerable document is the new one) or the retriever is right and
the score is wrong. Nothing records which, and one case in eight moves the
family-recall mean by 0.125.

### The three "Not yet measured" items are still not measured

- **Ranking within a correct family.** Still unmeasured, and the id drift above
  makes it harder: family recall says the book was found, and nothing says
  whether the right *page* of it surfaced.
- **Latency under the token-budgeted gateway.** `context_gateway.py` has
  `BUDGETS = {fast: 800, default: 1600, deep: 3200}` and reports a budget. No p95
  exists anywhere in the workspace. DB-1 reports the budget contract, which is
  what `measurements.md` says, and the 119.1 ms number is `ask.py` alone.
- **Two-hop questions.** One-hop is measured (Experiment C, +0.0323 recall,
  0.5806 → 0.6129). `EXPC_graph_expansion_20260925_050904.json` is the only
  expansion artifact; no two-hop run exists. Five of the 23 VERA questions are
  level 4 and would exercise it.

### Semantic retrieval is a deferred decision, not a rejected one

C-7 deliberately did not build hybrid FTS5 + embeddings, on the evidence that all
four retriever levers returned byte-identical scores and `mean_family_recall` was
0.958. Both halves of that argument are now stale: family recall is 0.875 in the
committed artifact, and the levers were measured against a saturated *family*
score while the real gap is *within* a family. The finding stands on its own
terms — semantic search is the right answer to "I don't know the word the book
used", which is still worth ~0.0 here — but the stated justification no longer
matches the numbers. Re-decide it against the within-family gap, not the family
number.

### Annotation coverage: 8 benchmark cases, 23 annotated questions

`../../_archive/agentic-research-lab/subprojects/vera/benchmark/QUESTIONS.md` annotates 23
questions across five difficulty levels, with `distractors:` on all 23 and
`pinned_query:` on 13. `retrieval_benchmark.json` uses 8 of them. Levels 3–5 —
conflicting evidence, causal comparison, open-ended proposal — are entirely
absent from the measured set, and the distractor field is unused by
`run_retrieval_benchmark.py`, so a retriever that returns the *wrong* chunk of
the *right* book scores the same as one that returns the right book. The
precision question this project exists to answer is not asked by the harness that
produces its numbers.

### Two quarantined chunks are still damaged on disk

`scan_corpus` over `knowledge/corpus` today reports 2 offending chunks and 3 glue
tokens — matching `quarantine.json` exactly (329_paradigms…, 949_artificial…),
which is why the benchmark stamp reads VALID. The damage is excluded at query
time, not repaired: `329_paradigms…` still contains
`provethataddstheprimitivegoalshow`. `measurements.md` says "corpus damage
4.0% (419 / 10,364)" under *Current state* while the same row's note says the
figure was 419 and quarantine removed all but 2. The denominator is also stale —
the corpus is 10,337 chunks now. Re-extract those two from source or accept the
exclusion permanently, and restate the damage row as a number about today.
