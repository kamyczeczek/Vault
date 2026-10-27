---
type: Concept
title: injection_test
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# Experiment E: Verification-Gate Injection Test

Spec (frozen before running; changes = new experiment ID).

## Defect types (5, one planted instance each per candidate run)

| ID | Type | Planted instance | Expected detecting gate |
|---|---|---|---|
| D1 | Broken citation | Cite a chunk ID that does not exist in knowledge/corpus/ | Tool grounding (C): ask.py resolution fails |
| D2 | Unsupported mechanism | Claim a mechanism the cited chunk never states | Tool grounding (C) + rubric: claim vs chunk text mismatch |
| D3 | Self-contradiction | Two claims in one report assert opposite conditions | Peer pair (D): independent critic inconsistency check |
| D4 | Correlation-as-causation | "X caused Y" where source only reports co-occurrence | Falsification probe (E): negative control probe |
| D5 | Unsourced novelty | A confident-looking claim marked nowhere, no citation | Tool grounding (C): resolvable-citation check flags missing source |

Candidate defect classes (queued, not yet in the 5×5 matrix):

| ID | Type | Planted instance | Expected detecting gate |
|---|---|---|---|
| D6 | Same-source double citation | One chunk cited twice as if independent evidence | Rubric: evidence-independence check |
| D7 | Part-sibling displacement | Seed names part k/n of a part-split source; answer cites a sibling part m/n as the source | Scoring policy: source-level vs strict-ID recall must be chosen per question before the E-suite (origin: DB1-F3, Q6 parity row 2026-09-24) |

## Runner configurations

- **A** synthesis only (no critic)
- **B** + LLM self-critique
- **C** + tool grounding: every claim's source IDs resolved via ask.py; support = cited chunk text contains the mechanism
- **D** + peer-review pair (two independent critics, rubric score, both must pass)
- **E** + causal-falsification probes: ablation/counterfactual with observable output + negative control

## Protocol

1. Run config on 10 questions (L1, L2, L3 mix) with a clean candidate rule set.
2. Re-run same 10 with exactly one planted defect of each type (total 50 planted cases;
   randomize insertion position within the claim list; log insertion point).
3. Per case record: detected? (bool), detecting gate, false-positive flag on clean claims.
4. Primary metric: per-gate detection rate per defect type (5×5 matrix, gate × defect).
5. Secondary: false-positive rate on clean runs; added cost per gate from costs.jsonl.

## Passing rule for a gate to stay on the hot path

Detection rate for its expected defect type ≥ 0.8 AND added cost ≤ 2× baseline cost of that
question set. Gates failing this are demoted to post-hoc review (still logged, not blocking).

## Negative control

Run every gate on a corpus-subset question set built ONLY from distractor IDs: detection of
"defects" there must be near zero (gates fire on real defects, not on sparsity). If a gate
fires on distractor-only inputs, instrument defect — file finding, re-run after fix.

## Deliverables

- `experiments/runs/E_injection/` per-config raw outputs
- `reports/injection_test.md`: the 5×5 matrix, FP rates, cost per gate, demotion decisions
- Promotion candidate (only if matrix shows ≥1 gate earns its place): written in
  `reflection/candidates/` format with tool outputs as evidence
