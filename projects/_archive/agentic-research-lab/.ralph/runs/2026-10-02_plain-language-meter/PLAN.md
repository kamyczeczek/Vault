# Decision graph plan

## Destination

D-001 meter picked + D-002 comparison design written to
docs/research/plain-language-meter.md + D-004 production eval-set seed v1
(plumbing); then D-005 score the three mechanisms on the set

## Nodes

| ID | Type | Status | Blocks | Depends on |
|---|---|---|---|---|
| D-001 | decision | RESOLVED | D-002 |  |
| D-002 | decision | RESOLVED | D-003 | D-001 |
| D-003 | decision | RESOLVED | D-004 | D-002 |
| D-004 | decision | RESOLVED | D-005 | D-003 |
| D-005 | decision | OPEN |  | D-004 |

## Frontier

D-005

## Decisions so far

- D-001 RESOLVED 2026-10-02: two-tier meter — held-out lay-reader
  comprehension task (primary), G-Eval-style LLM rubric (per-iteration
  proxy), FactPICO-style faithfulness as safety counter-metric; surface
  indices rejected as primary.
- D-002 RESOLVED 2026-10-03 (I-002): comparison design written to
  `docs/research/plain-language-meter.md` + harness skeleton; G1/G2 met.
- D-003 RESOLVED 2026-10-03 (I-003): deterministic fixture + public CLI
  contract frozen; G2 re-verified; dead-code integration clean.
- D-004 RESOLVED 2026-10-03 (I-004): production eval-set contract frozen —
  `knowledge/eval_sets/plain_language_v1.json` (fingerprinted, stratified,
  oracle-first) + deterministic builder
  `scripts/build_plain_language_eval_set.py`; seed v1 = 3 real KB-scale
  agent outputs; G4 added. MC-distractor generation and the 20-passage
  production set are model-backed and deferred to a budgeted step.
- D-005 OPEN: score the three prompt-layer mechanisms (always-on rule /
  few-shot / post-hoc rewrite) on the set. Needs model access — a
  human/budget call. G3 stays human-owned and gates the run's DONE.

## Not yet specified

- The 20-passage production eval set + model-backed MC distractor
  generator (adapter seam in the builder). Seed v1 (this node) uses 3
  passages and recall items only.
- Lay-reader model cast (pick a small, distinct-from-generators model) —
  runtime config, not embedded in the set (D-003/D-004).

## Out of scope

- Personalization (ReLay's contribution) — recorded, not in the
  mechanism candidates.
- New graph rebuilds; the `00_web_*` literature is already in the graph.
