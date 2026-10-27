---
type: Concept
title: baseline
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Experiment: Baseline (B0)

Purpose: deliberately simple reference pipeline. Anything added later must beat this on the
scorecard with a fixed cost budget. No optimization allowed in B0 — its job is a floor, not a rival.

## Pinned configuration

```yaml
name: vera-baseline
question_source: subprojects/vera/benchmark/QUESTIONS.md (frozen IDs only)
retrieval:
  tool: "python knowledge/graph/ask.py '<question>'"
  mode: single lexical query, top-N results
  N: 8            # pin at first run; document observed truncation in runs/
  query_form: verbatim question text
  reformulation: none
  graph_expansion: none
synthesis:
  passes: 1
  prompt_contract: >
    You are answering a research question using ONLY the retrieved chunks.
    Output the answer contract (sections 1-12 below). Cite chunk IDs inline.
    Do not use outside knowledge; say UNSOURCED for anything not in chunks.
  critic: none
  verification: none
  debate: none
output:
  schema: "subprojects/vera/metrics/claim_schema.md"
  artifact: runs/<qid>_B0.md + runs/<qid>_B0_claims.jsonl
fingerprint: 679a4aa15608  # re-pinned 2026-09-24 (frozen study value 05bc79e4b41e ended with DB-1 freshness probe; see runs/DB1_arms.md)
seed: <LLM sampling seed or temperature=0 setting used; record exact provider+model>
```

## Answer contract (all B0 answers must have)

1. Research question  2. Scope/exclusions  3. Search dimensions
4. Sources consulted (chunk IDs)  5. Main claims  6. Per-claim evidence
7. Contradictory/limiting evidence  8. Mechanisms  9. Failure modes
10. Confidence + open questions  11. Proposed experiment  12. Provenance block
    (fingerprint, config name, run timestamp, raw tool-call log path)

## Determinism & rerun rule

- One official run per question: `runs/<qid>_B0/` containing answer, claims.jsonl, tool log.
- Rerun procedure: same config file byte-identical → identical claim hashes required on L1/L4
  questions (stable subset: Q1, Q2, Q3, Q13, Q14, Q15, Q16). L2/L3/L5 tolerate variance;
  report it, don't hide it.
- Any config edit = new experiment ID (B0.1, …), never mutate B0.

## Cost logging

After each run append to `runs/costs.jsonl`:
`{"qid":..,"experiment":"B0","tokens_in":..,"tokens_out":..,"tool_calls":..,"wall_s":..,"fingerprint":".."}`

## B0.1 Addendum (2026-09-24, fingerprint 05bc79e4b41e)

Empirical finding from first B0 attempts: verbatim question text yields **zero matches** on
long-form questions because ask.py ranks on shared-term overlap ("trust tiers evidence" also
failed — a chunk must contain all terms; "trust_tier provenance tiers raw intake attested"
succeeded with 5 overlapping terms). `--recall` did not rescue long verbatim text.

Decision (config change ⇒ new ID, per determinism rule): **B0.1** = same B0 contract except
`query_form: core-terms` — the synthesizer distills the question into 2–5 key vocabulary terms
(ONE decomposition step, logged as `query_used:` in the run's provenance block; NOT iterative
reformulation, which belongs to Experiment B). Zero-match verbatim B0 runs are kept as floor
data points in costs.jsonl, not repeated.

- B0: documented, zero-match floor for long verbatim queries (Q1, Q13 attempts logged)
- B0.1: operational floor; first runs completed for stable subset Q1, Q13–Q16
  (`runs/Q*_B0.1.md` + claims + costs rows)

## B0.2 Addendum (2026-09-24)

Reproducibility check (Q13 r2) found B0.1's *query layer* under-determined: the same question
distills to different core-terms between runs. Fix: **pinned query terms** — each benchmark
question now carries a `pinned_query:` line (written 2026-09-24 in QUESTIONS.md); runs use it
verbatim, never re-derive. Pinned so far: Q2, Q4, Q5, Q6 (task-set questions). Unpinned
questions fall back to B0.1 core-terms until their first run records terms (log, then pin).
Determinism scope narrowed accordingly: byte-identical retrieval guaranteed only for pinned
questions; synthesis-layer variance reported per claim class (direct/inferred must be stable,
novel may drift — logged, not passed/failed).

## Runbook

```bash
# per question
python knowledge/graph/ask.py "<question text>" > subprojects/vera/experiments/runs/<qid>_B0/retrieved.txt
# synthesize per prompt_contract (agent turn, logged), write <qid>_B0.md + <qid>_B0_claims.jsonl
# score against metrics/scorecard.md, append costs.jsonl
# rerun stable subset once; diff claim hashes → runs/rerun_diff.txt
```

## Exit criteria for B0

- [ ] 20/20 questions have answer + claims + cost rows
- [ ] Stable-subset rerun: 100% claim-hash agreement (or variance table logged)
- [ ] Scorecard row for B0 exists for all 7 dimensions
