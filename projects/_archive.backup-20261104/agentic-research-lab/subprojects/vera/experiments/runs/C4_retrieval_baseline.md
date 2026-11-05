---
type: Concept
title: C4_retrieval_baseline
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# C-4 — Retrieval baseline: what is actually measurable, and what is not

Date: 2026-09-26
Companion to: `C1_corpus_whitespace_defect.md`, `C2_corpus_repair_triage.md`
Status: VALID baseline established; `mean_exact_recall` retired as a metric

## Baseline

```
status                     VALID — measured over the searchable corpus;
                            419 damaged chunks excluded at query time
cases                            8
mean_exact_precision        0.075
mean_exact_recall           0.250   <- retired, see below
mean_family_precision       0.460
mean_family_recall          0.875
mean_concept_coverage       0.958
mean_latency_ms           119.07
```

This is the first non-VOID retrieval number in the project. The previous "baseline" was
fabricated (tags in the FTS index) and the VOID stamp on it was honest but stale.

## `mean_exact_recall` measures the annotation, not the retriever

`mean_exact_recall` sits at 0.25 and cannot be raised by improving retrieval. Three
independent measurements show why:

**1. No single chunk contains the query.** In 6 of 8 cases the gold chunk lacks one or more
query terms, so an AND-precise path can never return it:

| case | query terms present in gold |
|---|---|
| causal-intervention | 4/4 |
| scientific-discovery | 4/5 (`hypothesis`) |
| production-reliability | 4/6 (`reliability`, `retrieval`) |
| agent-memory | 3/5 (`hierarchy`, `compaction`) |
| planning-workflow | 3/6 (`decomposition`, `long`, `horizon`) |
| graph-scaling | 5/6 (`traversal`) |
| automl-experiment | 3/6 (`experiment`, `evaluation`, `optimization`) |
| multiagent-coordination | 6/6 |

**2. An oracle cannot find them either.** Given the correct source family for free, and
ranking purely by term coverage, the gold still lands at rank 11/386 (`causal-intervention`),
18/191 (`graph-scaling`), 76/210 (`automl-experiment`). Term overlap does not distinguish these
chunks from their neighbours, so no lexical ranker will.

**3. The golds were front matter.** 6 of 8 pointed at title pages — *"ALSO BY JUDEA PEARL"*,
*"Ian Robinson, Jim Webber & Emil Eifrem, 2nd Edition"*, a Springer series title page, a
contents listing. They were auto-selected by "first chunk of the right book", which is a
property of the annotation, not of relevance. 5 have been re-annotated to substantive chunks
covering all required concepts. The metrics did not move, which is the expected result: the
replacement chunks are equally indistinguishable by term overlap.

Recall-depth probe, OR path, gold chunk reachability:

| depth | 5 | 20 | 60 | 200 | 600 | 2000 | 5000 |
|---|---|---|---|---|---|---|---|
| cases reachable | 2/8 | 3/8 | 5/8 | 6/8 | 6/8 | 7/8 | 7/8 |

The 8th case, `causal-intervention`, is unreachable at any depth because its gold chunk is one
of the 319 quarantined *Book of Why* chunks. So the metric ceiling is **0.875**, and **0.75** at
any depth a user would tolerate.

## What to measure instead

- **`mean_family_recall` (0.875)** — did we reach the right *book*? This is the meaningful
  retrieval question for a corpus of sources, and it is well above the 0.625 recorded before the
  tag and quarantine fixes.
- **`mean_concept_coverage` (0.958)** — did the returned text actually contain the concepts? This
  is the metric that would move if chunk selection improved, and it is already high.
- **`mean_family_precision` (0.46)** — the honest weak number. Half the returned chunks come from
  the wrong book. This is where effort belongs.

`mean_exact_recall` is retained in the artifact for continuity but is no longer a target. A
future run should either drop it or replace it with an oracle-normalised measure
(`recall / 0.875`) so that it reports distance from the achievable ceiling rather than implying
the retriever is broken.

## Benchmark defects found and fixed

1. **Truncated gold id.** `multiagent-coordination` pointed at
   `00_multiagent_systems_algorithmic_game_theoretic_and_logical_foundations` (80 chars) when
   chunk ids truncate at 55. Re-annotated to a chunk that exists and covers both concepts.
2. **Two concepts absent from their gold.** `production-reliability` required `retrieval` and
   `automl-experiment` required `experiment`; neither word occurs in the annotated chunk. Both
   concepts replaced with terms the gold actually supports (`deployment`/`prompting` and
   `automated`).
3. **6 of 8 golds were front matter** — re-annotated as described above.
4. **Quarantine was source-level, not chunk-level.** The first cut excluded whole families and
   discarded 417 clean chunks to hide 419 damaged ones, including all 828 chunks of *Paradigms of
   AI Programming* and all 1,123 of *AIMA* over a single damaged chunk each, and it removed the
   `causal-intervention` gold even though that chunk is undamaged. Now chunk-level.

## Detector correction

`check_corpus_health.py` reported 6,401/10,364 chunks (62%) damaged. The true figure was
**419/10,364 (4.0%)**. The overcount came from two signals that both fire on legitimate text:

- CamelCase run-ons flagged `basePrice`, `daysOverdrawn`, `frequentRenterPoints` — real
  identifiers from *Refactoring* and *Beginning Software Engineering*.
- Corpus-absent long tokens flagged any word used fewer than 6 times in a 4.5M-word corpus, which
  in a corpus that size is ordinary technical vocabulary.

The signal that discriminates is structural: an extraction artifact is a long **all-lowercase**
run with no camelCase boundary, hyphen, or underscore. `MIN_GLUE_LEN = 32` (the longest credible
English single token, `antidisestablishmentarianism`, is 28). No frequency heuristic, so the gate
behaves identically on a two-chunk fixture and on the full corpus.

Damage is concentrated in four sources, 99% of it in two:

| chunks damaged | source |
|---|---|
| 319 | *The Book of Why* (386 chunks total — 83% damaged) |
| 98 | *The Mythical Man-month* (103 chunks total — 95% damaged) |
| 1 | *Paradigms of AI Programming* (828 chunks total) |
| 1 | *AIMA* (1,123 chunks total) |

## Quarantine

`scripts/build_quarantine.py` writes `knowledge/graph/quarantine.json`: 419 chunk ids excluded
at query time by `ask.py` on the FTS path, the tag-only path, and the alias path. The corpus is
never modified, so a re-ingested clean chunk is re-admitted by re-running the script. Repair
requires better source PDFs (see C-2); nothing in code can undo lost whitespace without
fabricating text.

## Not attempted, and why

- **BM25 `k1`/`b` tuning.** Rejected in C-1 and still rejected — but the reason is now precise.
  The gold chunks are unreachable because they do not contain the query terms, not because the
  ranker is mistuned. Tuning would move `mean_family_precision`, which is the metric worth
  attacking, and would leave `mean_exact_recall` at its 0.25 ceiling.
- **Chunk re-segmentation.** Merging adjacent chunks would raise per-chunk term coverage and is
  the most promising lever for `mean_concept_coverage`. It re-derives the corpus and moves the
  fingerprint, so it is a separate decision.

## Correction: single-gold annotation was also under-crediting the retriever

`mean_family_precision` initially read 0.46 — "half the returned chunks come from the wrong
book". That was false. Inspecting the actual top-5 for each case showed the retriever returning
correct, better sources that the benchmark scored as false positives because exactly one family
was annotated:

| case | result scored wrong | actually is |
|---|---|---|
| agent-memory | `persistent_memory_hierarchies_agents` | directly on-topic; 2/2 required concepts |
| agent-memory | `memory_eviction_forgetting_web_research` | directly on-topic; 2/2 required concepts |
| agent-memory | `session_compaction_for_ai_agents` | on-topic; 1/2 concepts |
| planning-workflow | `long_horizon_planning_`, `world_models_long_hori` | on-topic for a long-horizon query |
| scientific-discovery | `autonomous_scientific_` | on-topic for automated discovery |

`agent-memory` requires `memory` and `context`; four of its five results contain both. The
benchmark asked "did you find the one book I picked" and reported "no" for answers that would
have satisfied a user. `gold_sources` already accepted a list, so the fix is annotation, not code:
7 alternate golds added across 4 cases, every id verified to exist in `graph.db`.

After multi-gold annotation:

```
mean_exact_precision        0.075 ->  0.225
mean_exact_recall           0.250 ->  0.333
mean_family_precision       0.460 ->  0.652
mean_family_recall          0.875 ->  0.958
mean_concept_coverage       0.958   (unchanged)
mean_latency_ms           119.07 -> 475.31  (see note)
```

The latency figure is a benchmark artifact, not a regression: the runner measures the first
query against a cold FTS page cache. Measured warm in-process, live queries run 112–244 ms,
consistent with the pre-annotation 119 ms.

**Lesson worth keeping: before treating a retrieval metric as ground truth, print what it is
scoring.** Both of the "quality" problems found in this round — the void corpus and the
unreachable gold — were measurement defects that looked like product defects, and both were
invisible to 15 passing quality gates.

## Rejected: chunk re-segmentation (measured, not assumed)

Merging adjacent chunks was the top-ranked remaining lever for concept coverage. It was
simulated before any code was written, because it re-derives 10,364 files and moves the
fingerprint. **It buys nothing.**

Chunks are already ~2,507 chars at the median (p25 2,075, p75 2,901), so size is not the
constraint. The question was whether a query's terms are split across a chunk boundary, and
the answer is that they are not. Fraction of cases where one contiguous window contains every
query term:

| window | all query terms in one chunk |
|---|---|
| 1 (current) | 5/8 |
| 2 | 5/8 |
| 3 | 5/8 |
| 4 | 5/8 |

Flat across every window size. The diagnosis inverts the premise: the three failing cases are
not fragmented, they are **single-chunk notes** (`agent-memory` n=1, `scientific-discovery` n=1)
or small books whose vocabulary does not contain the term at all —

| case | chunks in family | terms in some chunk | term absent from the whole source |
|---|---|---|---|
| scientific-discovery | 1 | 4/5 | `hypothesis` |
| agent-memory | 1 | 3/5 | `hierarchy`, `compaction` |
| planning-workflow | 15 | 5/6 | `decomposition` |

Nothing can be merged that would surface a word the source never uses. Re-segmentation was
aimed at a defect that does not exist, and it would have moved the fingerprint for zero
measured gain.

**What would actually move concept coverage** is query-side, not chunk-side: synonym or alias
expansion at query time (`compaction` → `context`, `decomposition` → `workflow`) so a user who
asks in different words than the book did can still reach it. That is a retriever change, it
leaves the corpus and fingerprint untouched, and it is the next thing worth measuring.

Note: the `mean_latency_ms` of 126 ms on a re-run confirms the 475 ms figure above is a cold
FTS page cache on the runner's first query, not a regression.

## Rejected: three retriever levers (all measured flat)

Chunking was the wrong layer, so the remaining idea was the retriever. Four candidate levers
were tested by monkey-patching the live `ask.py` in-process and re-running all 8 cases. **Every
one produced byte-identical scores.**

| lever | exact recall | family recall |
|---|---|---|
| baseline | 0.333 | 0.958 |
| + synonym aliases (`hierarchy`→`persistent`, `compaction`→`context`, `decomposition`→`workflow`, `hypothesis`→`automated`) | 0.333 | 0.958 |
| + irrelevant aliases (overfit control) | 0.333 | 0.958 |
| top family granted 2 result slots instead of 1 | 0.333 | 0.958 |
| FTS fetch depth 8 → 40 | 0.333 | 0.958 |
| FTS fetch depth 8 → 200 | 0.333 | 0.958 |

The irrelevant-alias row is the important one: it is the control, and it also moved nothing.
When a targeted change and a deliberately meaningless one both leave the score identical, the
score is not measuring the thing being changed. It is saturated.

**Why it is saturated.** `mean_family_recall` is 0.958 — every case finds the correct book at
depth 5. The whole remaining gap is *which chunk inside a large book*, and the diagnosis from
the depth probe says the gold chunk is simply not distinguishable: within the correct family it
sits at rank 11/386, 18/191, 76/210 on pure term overlap, and the recall-depth sweep showed it
unreachable even at depth 5000 for one case. Adding slots, depth, or synonyms changes which
arbitrary page of the right book is shown, never *which* page is correct.

Raising these numbers further would require semantic matching — embeddings, or LLM reranking of
candidate chunks. That is a different system with different failure modes, and at
`mean_family_recall` 0.958 / `mean_concept_coverage` 0.958 the product is already answering the
question asked of it. The honest recommendation is to stop optimising here and spend effort on
the corpus damage that is still real: 419 chunks in two books that need better source PDFs.

None of these levers was committed. No code changed; the only edits are this record and the
benchmark artifact re-run, which is byte-identical.
