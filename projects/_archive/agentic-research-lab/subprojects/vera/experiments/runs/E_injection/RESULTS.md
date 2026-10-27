---
type: Concept
title: RESULTS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# E-Suite Injection Test Results (Experiment E)

**Fingerprint:** 44172cafee34
**Date:** 2026-09-24

## Summary

| Metric | Value |
|--------|-------|
| Questions | 10 (L1×3, L2×5, L3×2) |
| Clean claims | 23 |
| Planted defects | 50 (10 questions × 5 defect types) |
| Total claims tested | 73 |
| Clean false positives | 0 (0%) |

## Detection Matrix (5×5)

| Defect Type | Description | Planted | Detected | Rate | Runner Configs |
|-------------|-------------|---------|----------|------|----------------|
| **D1** | Broken citation (unresolvable source_id) | 10 | 10 | **1.00** | C (tool grounding) |
| **D2** | Unsupported mechanism (claim not in source) | 10 | 10 | **1.00** | C (heuristic overlap) |
| **D3** | Self-contradiction (negation-wrap) | 10 | 10 | **1.00** | C (string detection) |
| **D4** | Correlation-as-causation | 10 | 0 | **0.00** | — (not scriptable) |
| **D5** | Unsourced novelty (empty source_ids) | 10 | 10 | **1.00** | C (schema check) |

## Injection Test Passing Rule (from injection_test.md)

> **Passing rule:** detection rate ≥ 0.8 AND cost ≤ 2× baseline

| Defect | Detection Rate | Pass? |
|--------|----------------|-------|
| D1 | 1.00 | ✅ |
| D2 | 1.00 | ✅ |
| D3 | 1.00 | ✅ |
| D4 | 0.00 | ❌ (requires two-rater log) |
| D5 | 1.00 | ✅ |

**Gate-C (tool grounding + schema checks) PASSES for D1, D2, D3, D5.**
**D4 requires human rater path (two-rater log pending).**

## Per-Question Breakdown

All 10 questions show identical pattern:
- 4/5 defect types auto-detected by gate-C
- D4 always routed to two-rater log (no scriptable detector)
- 0 false positives on clean claims

## Cost Analysis

- Gate-C runs as pure Python + `ask.py` subprocess calls
- No LLM calls required for D1, D2 (heuristic), D3, D5
- Cost ≈ baseline (single-pass retrieval + claim check)
- **Cost ratio well under 2× threshold**

## Next Steps

1. **Two-rater inter-rater log for D4** (debt from GATE_ABLATION_Q13Q14.md)
   - Need human raters to judge correlation-vs-causation on the 10 D4 planted cases
   - Log agreement/disagreement for inter-rater reliability

2. **E-suite complete for automated gate-C**
   - Clean claims: 23, all verified clean
   - Planted claims: 50, 40 auto-detected, 10 pending (D4)

3. **Promote to injection_test.md results section**

## Files Generated

- `clean_claims.jsonl` — 23 grounded claims from pool digest
- `planted_claims.jsonl` — 73 claims (23 clean + 50 planted, shuffled)
- `positions.jsonl` — insertion positions for reproducibility (seed 20260924)
- `clean_gate_c_results.jsonl` — gate-C on clean pool (0 FP)
- `planted_gate_c_results.jsonl` — gate-C on planted pool (40/50 detected)
- `positions.jsonl` — insertion positions for reproducibility