---
type: Concept
id: icm-determinism-rule
title: "Derived Rule: ICM Determinism — reflection routing must be replayable"
source: "derived: synthesis over 00_from_plan_to_action_how_well_do_agents_follow_th, 10_from_plan_to_action_how_well_do_agents_follow_th, planning-with-files-pattern, 00_hooks_board_events, 12_is_progressive_disclosure_all_you_need_for_long (corpus, 2026-09-15)"
tags: [icm, determinism, reflection, routing, reproducibility, context-engineering, agents, planning, progressive-disclosure, derived-rule]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Derived Rule — ICM reflection routing must be replayable

Gap this closes: the ICM corpus documents the *workflow* of reflection (stages,
Inputs Tables, progressive disclosure) but not its *determinism*. Only one corpus
chunk co-tags `icm` + `determinism` (`planning-with-files-pattern`), and the
tag `determinism` appears on exactly one chunk overall — while 373 chunks tag
`icm`. The reproducibility of the pipeline's own retrieval was therefore
undocumented, which is the exact property the pipeline claims.

## Rule

Reflection retrieval is replayable iff, given the same corpus fingerprint and the
same query, it returns the byte-identical chunk id set. Three conditions, all
already satisfied by the machinery, none previously stated as a requirement:

1. **Routing is exact-tag intersection, ordered by id.** `ask.py --tag a --tag b`
   resolves to `SELECT id FROM nodes WHERE tags LIKE a AND tags LIKE b ORDER BY id`
   when no question words are supplied. `ORDER BY id` is what makes the set stable;
   it must not be replaced by rank (`bm25`) or insertion order.
2. **Queries are recorded, not reconstructed.** A digest carries the literal
   `python knowledge/graph/ask.py ...` invocations in its Routing header, plus the
   `fingerprint` of the graph they ran against. A future run re-executes those
   strings and asserts the id set is unchanged. Provenance is what makes the
   replay checkable rather than merely claimed.
3. **Content search is never load-bearing for citations.** `ask.py` with question
   words falls back through FTS5 `bm25` → LIKE fallback, and `bm25` ranking is not
   stable across schema or corpus changes. Tag intersection is the citation path;
   content search is discovery only. (Observed this session: the phrase
   `deterministic replay reproducible` matched zero chunks while the same concept
   was reachable via tags — content search has false negatives that tags do not.)

## Grounding

- `00_from_plan_to_action_how_well_do_agents_follow_th` — "across runs, confirming
  the non-determinism"; plan quality is measurable only once run-to-run variance
  is controlled. The ICM pipeline's value claim (ordered phases beat implicit
  stages) inherits that requirement.
- `10_from_plan_to_action_how_well_do_agents_follow_th` — explicit non-determinism
  elimination as a precondition for evaluating plan-following.
- `planning-with-files-pattern` — the only `icm`+`determinism` chunk: plan,
  findings, and progress live on disk so a later cycle re-reads the same state
  instead of re-deriving it from context.
- `00_hooks_board_events` — hooks kept non-blocking specifically "to preserve
  determinism"; gating is separated from the hot path. Routing, not hooking, is
  where determinism is won or lost.
- `12_is_progressive_disclosure_all_you_need_for_long` — "Every call runs at
  temperature 0": determinism is an evaluation-time property the corpus already
  treats as a precondition, not an optimization.

## Check

Replay contract (executable, no new machinery):

```
python knowledge/graph/ask.py "" --tag <t1> --tag <t2> --limit N
```

run against two fingerprints of the same corpus must yield identical id
sequences. A digest citing this rule records its queries and fingerprint; a
divergent replay is a pipeline bug, not a model artifact.
