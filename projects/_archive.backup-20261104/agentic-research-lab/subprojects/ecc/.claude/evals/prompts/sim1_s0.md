# VERA SIM-1 S0 Protocol: Full Verification (G0→G3)

You are a VERA researcher executing the **S0 (Full Protocol)** arm of the simplicity ablation study.

## Your Task

Run the complete VERA research protocol on benchmark questions Q1-Q23 using B0.2 pinned queries.

## Protocol Steps

### 1. Retrieval
For each question, use the pinned queries from `../vera/benchmark/QUESTIONS.md`:
```bash
python ../vera/knowledge/graph/context_gateway.py --query "<pinned_query>" --budget default --limit 5
```
Use the graph fingerprint `44172cafee34` (pinned at commit).

### 2. Claim Synthesis
For each retrieved chunk, synthesize claims with this schema:
```json
{
  "claim_id": "Q5_S0_c01",
  "statement": "The lab's reflection protocol handles session compaction by persisting accepted rule candidates...",
  "source_ids": ["00_reflection_protocol", "01_session_compaction_rules"],
  "support_type": "direct",
  "confidence": "high",
  "mechanism": "Reflection protocol explicitly stores accepted rule candidates during compaction",
  "limitation": "Only covers rule candidates, not full context",
  "verification_status": "unverified"
}
```

### 3. Verification Gates (ALL REQUIRED for S0)

#### G1 — Grounding Gate
Verify ALL source_ids resolve via ask.py:
```bash
for chunk_id in "${source_ids[@]}"; do
  python ../vera/knowledge/graph/ask.py "$chunk_id"
done
```
ALL must return the chunk content (exit code 0, chunk_id in stdout).

#### G2 — Reproducibility Gate
Re-run retrieval for each pinned query, compare chunk sets (Jaccard ≥0.9):
```bash
python ../vera/knowledge/graph/context_gateway.py --query "<pinned_query>" --budget default --limit 5
```

#### G3 — Negative Controls Gate
Run injection test detectors on your claim pool:
- D1: Broken citation (ask.py resolution)
- D2: Unsupported mechanism (content-word overlap)
- D3: Self-contradiction (negation detection)
- D4: Correlation-as-causation (route to human rater log)
- D5: Unsourced novelty (empty source_ids)

## Output

Write claims to: `../vera/experiments/runs/sim1_ecc_replication/claims_S0_Q{QID}.jsonl`
Write verification results to: `../vera/experiments/runs/sim1_ecc_replication/verification_S0_Q{QID}.jsonl`

## Questions to Process

Process ALL 23 questions (Q1-Q23) using their B0.2 pinned queries from QUESTIONS.md.

## Success Criteria

- All claims have verified source_ids (G1 pass)
- Reproducibility Jaccard ≥0.9 (G2 pass)
- Injection detection rate ≥0.8 for D1,D2,D3,D5 (G3 pass)
- D4 cases logged to two-rater log template

## Notes

- This is the LOAD-BEARING protocol for L3-L5 questions (per tier-dependent policy)
- Track token usage, wall-clock time, and API cost per question
- Use `vera-researcher` agent for retrieval/synthesis, `vera-verifier` for gates