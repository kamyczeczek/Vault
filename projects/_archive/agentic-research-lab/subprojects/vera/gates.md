---
type: Concept
title: gates
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Gates: VERA Phase 1

## Leaf tickets

- [x] V1: Is the benchmark complete?
  - Type: research
  - Question: Do `benchmark/QUESTIONS.md` contain 20 questions across 5 difficulty levels, each with scope, seed corpus IDs, ≥1 distractor, target structure?
  - Evidence: 24 verified chunk IDs annotated (reports/seed_annotation.md); every block has `seeds:`, `distractors:`, `level:` keys

- [x] V2: Is the baseline deterministic?
  - Type: task
  - Question: Does `experiments/baseline.md` pin query, retrieval params, prompt, output schema, and corpus fingerprint?
  - Evidence: B0.1 addendum (query_form: core-terms) + pinned fingerprint 05bc79e4b41e + 5 stable-subset runs logged in runs/; rerun-diff pending next session (V-N1)

- [x] V3: Is the scorecard operational?
  - Type: task
  - Question: Does `metrics/scorecard.md` define all 7 dimensions with measurement commands and one negative control each?
  - Evidence: `metrics/tools/score_b01.py` produced the dims 1/3/7 table in `reports/B0.1_phase1.md` including the distractor-only negative control (Q1 → 0 seed hits, expected <0.2)

- [x] V4: Is the claim schema canonical?
  - Type: task
  - Question: Does `metrics/claim_schema.md` define claim_id, sources, support_type, mechanism, limitation, verification_status?
  - Evidence: runs/Q1_B0.1_claims.jsonl etc. parse against all fields; open item: schema needs a `workspace:` source namespace (Q1 c03 cited CONTEXT.md with empty source_ids — addendum pending)

- [x] V5: Is the injection test spec fixed?
  - Type: research
  - Question: Are the 5 defect types (broken citation, unsupported mechanism, self-contradiction, correlation-as-causation, unsourced novelty) spec'd with one planted instance each?
  - Evidence: `experiments/injection_test.md` lists all 5 with insertion points and expected detection gate; candidate D6 (same-source double citation) added from Q4 findings

## Integration gates

- [x] V-N1: Phase 1 green
  - Type: task
  - Question: Do V1–V5 all hold, with one logged baseline run?
  - Evidence: progress.md entry "VERA Phase 1 complete"; run dirs `subprojects/vera/experiments/runs/Q1,Q2,Q3,Q4,Q13–Q16_B0.1*` + costs.jsonl + reports/B0.1_phase1.md

## Phase 2 tickets (simplicity & DB direction, researcher-set 2026-09-24)

- [x] P2-1: Is the SIM-1 arm set runnable?
  - Type: task
  - Question: Are S0/S1/S2 pipeline variants spec'd with fixed task set + metrics in experiments/phase2_simplicity_db.md?
  - Evidence: SIM-1 section has 3 arms, 6-question task set, 4 metrics, verdict rule; FIRST RESULTS in runs/SIM1_arms.md (S1>S2 resolved, S1 vs S0 inconclusive pending gate ablations)

- [x] P2-2: Does a distilled orientation pack exist?
  - Type: task
  - Question: Is orientation pack B (one-page simple pack) written and smaller than pack A by ≥50%?
  - Evidence: experiments/sim2_packB.md = 1,718 B vs pack A = 44,969 B → 96% reduction; routes depth to queries, does not duplicate it

- [x] P2-3: Is the single-graph read path defined?
  - Type: research
  - Question: Does DB-1 specify the D1 constraint set (ask.py + context_gateway only) and freshness probe?
  - Evidence: DB-1 section in experiments/phase2_simplicity_db.md (arms D0/D1, freshness probe, verdict rule: recall parity + ≥50% token cut + zero stale reads)

- [x] P2-4: Are the new benchmark questions Q21–Q23 annotated?
  - Type: research
  - Question: Do Q21–Q23 have verified seeds/distractors per the Phase-2 seed table?
  - Evidence: QUESTIONS.md "Phase-2 additions log" — seeds verified via ask.py 2026-09-24; 3rd 00_/01_ duplicate pair (bend2) confirmed

## Abandonment protocol

ABANDON: <id> <non-empty reason> — handoff recorded in progress.md
