---
type: Concept
title: measurements
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:19:26Z }
---

# Measurements

Standing numbers from the benchmark runs, and the reasoning behind every metric
that was retired. Read the retirement notes before reusing a metric — a number
without its caveat is worse than no number.

## Current state

| Metric | Value | Note |
|---|---|---|
| `mean_family_recall` | 0.938 | up from 0.875 baseline (93.8% across all benchmark families) |
| `concept_coverage` | 1.000 | 100% required concept coverage across all 8 benchmark cases |
| `mean_family_precision` | 0.654 | up from 0.629 baseline with intra-family reranking |
| `mean_exact_recall` | 0.312 | up from 0.250 |
| mean latency | 99.4 ms | two-stage candidate scoring under 100ms |
| corpus damage | 4.0% (419 / 10,364) | was reported as 62%; that was the over-firing detector |
| glued tokens | 3 | was 1,784 |
## Retired: `mean_exact_recall` (0.25)

Retired because it measures the annotation, not the retriever. Three independent
proofs, none of which any ranking change could fix:

1. **The gold lacks a query term.** In 6 of 8 cases the AND-precise path can never
   return it. `automl-experiment` has 3 of 6 required terms present.
2. **Given the right family for free**, and ranking by term coverage alone, the
   gold still lands at 11/386, 18/191, 76/210. The signal is not there.
3. **Six of eight golds are front matter.** A precision-oriented metric against a
   copyright page measures the labelling, not the system.

A metric that cannot be improved by making the retriever better is the wrong
metric. Do not tune ranking against it.

## Superseded: the 62% corpus-damage figure

Wrong by an order of magnitude. It came from the first `check_corpus_health.py`
detector, which fired on legitimate CamelCase identifiers and on rare technical
vocabulary. The 4.0% figure is from the structural signal in defect class 1.

## Superseded: source-level quarantine

Tried, measured, reverted. It discarded 417 clean chunks to hide 419 damaged
ones, evicting all 828 chunks of *Paradigms* and all 1,123 of *AIMA* over one
damaged chunk each — and it removed a `causal-intervention` gold that was never
damaged. Quarantine is chunk-level; the corpus is never modified.

## Not yet measured

- **Ranking within a correct family.** Family recall is high, family precision is
  0.654; the gap says the ordering inside a family is unmeasured, not merely weak.
- **Latency under the token-budgeted gateway.** The DB-1 clip contract reports a
  budget, not a measured p95.
- **Multi-hop questions.** One-hop tag neighbours are measured (Experiment C,
  +0.0323 recall). Two-hop has never been run.

## Retired: `recall@5` on Trust Set (2026-10-13)

Retired because it measures the annotation exact ID, not the retriever.
Proven by `docs/reviews/session-2026-10-13-kr-t13-gold-id-verification.md`:

1. **Family match vs exact match.** In 16 of 18 "false refusals" (88.9%), the retriever returns a correct chunk of the exact same slug (family recall @5 = 88.9%) but not the exact gold chunk ID annotated (exact recall @5 = 0%).
2. **Defect class 4.** Re-ingest reuses chunk IDs across entirely new text or different chunk numbering while preserving file slug, so exact ID matching fails while semantic family retrieval succeeds.

A metric that penalizes correct document retrieval due to arbitrary chunk numbering is the wrong metric. Use `family_recall@5` instead.

## Trust Set — measurement context (2026-10-14)

The Trust Set measurement (`pilots/graphrag/eval/measure_trust_set.py`) runs
with semantic OFF (`oblicz_pokrycie` called without `pytanie=`). The semantic
ON variant was measured on 2026-10-14 on a scratch copy — it improves false
refusals (27.3% → 0.0%) but regresses OOC refusal (66.7% → 40.0%). The pilot
was terminated on that basis (MRR@5=0.295 < 0.4). The scratch copy was not
committed; the committed code is semantic OFF.

Read the flag `handoff/flags/kr-pilot-terminated-2026-10-14.md` (root) for
the full measurement.
