---
type: Concept
title: scorecard
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# VERA Scorecard (7 dimensions)

Every experiment row logs all 7. A mechanism promotes only if it improves ≥2 dimensions
without regressing Integrity or exceeding the Cost budget (from task_plan.md decision log).

| # | Dimension | Metric | measure: (command / rubric) | negative_control: |
|---|---|---|---|---|
| 1 | Coverage | Relevant-node recall vs annotated seeds | intersect(retrieved_ids, seeds)/\|seeds\| per question, averaged | L1 questions: recall on distractor-only variant must stay <0.2 |
| 2 | Contradiction | Opposing-evidence detection rate | on L3 questions: 1 if ≥1 seed tagged in `contradicts`/`refutes` edges is in the report, else 0 | L1 (no controversy expected): report must NOT invent conflicts; flag rate scored against 0 |
| 3 | Grounding | Resolvable + supporting citation ratio | for each claim: ask.py resolves its source IDs AND chunk text supports mechanism (rubric 0/1) | distractor-only set: claims unsupported by retrieved text must be catchable → ratio near 0 expected |
| 4 | Depth | Mechanism coverage rubric 0–3 | 0 no mechanism · 1 named · 2 primitive+condition · 3 +limitation/threat boundary; two raters (LLM rubric + human), log agreement | single-paragraph answers capped at 1 by rater instruction; verify raters cap (calibration row) |
| 5 | Integrity | Injected-defect detection rate | from injection_test.md 5×5 matrix | distractor-only negative control (see injection_test.md) |
| 6 | Reproducibility | Re-run agreement | normalized claim hashes identical across N≥3 runs on stable subset | randomize a single claim input → hashes must change (instrument not frozen) |
| 7 | Cost | Tokens, tool calls, wall-time, passes | costs.jsonl rows; report total + per-question mean | B0 floor: any config >3× B0 total cost must justify via ≥2 dimension gains |

## Reporting format

`reports/<experiment>.md` contains one table:

| qid | dim | value | config_hash | fingerprint | notes |

plus a `verdict:` line: PROMOTE / REJECT / INCONCLUSIVE (INCONCLUSIVE requires the reason
recorded — what measurement to rerun and what threshold would decide it).

## Instrument hygiene

- Metric code lives in `subprojects/vera/metrics/tools/` (not in workspace root) — lab code
  stays untouched; VERA imports workspace read-only.
- Every metric tool prints its input fingerprint so stale-metric reuse is impossible.
