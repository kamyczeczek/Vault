# VERA SIM-1 S1 Protocol: Retrieve → Answer → Grounding Gate (G1 Only)

You are a VERA researcher executing the **S1 (Gate 1 Only)** arm of the simplicity ablation study.

## Your Task

Run the simplified VERA protocol on benchmark questions Q1-Q23 using B0.2 pinned queries.
**Only G1 (Grounding Gate) is required.** G2 (Reproducibility) and G3 (Negative Controls) are SKIPPED.

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
  "claim_id": "Q5_S1_c01",
  "statement": "The lab's reflection protocol handles session compaction by persisting accepted rule candidates...",
  "source_ids": ["00_reflection_protocol", "01_session_compaction_rules"],
  "support_type": "direct",
  "confidence": "high",
  "mechanism": "Reflection protocol explicitly stores accepted rule candidates during compaction",
  "limitation": "Only covers rule candidates, not full context",
  "verification_status": "unverified"
}
```

### 3. Verification Gate (G1 ONLY)

#### G1 — Grounding Gate
Verify ALL source_ids resolve via ask.py:
```bash
for chunk_id in "${source_ids[@]}"; do
  python ../vera/knowledge/graph/ask.py "$chunk_id"
done
```
ALL must return the chunk content (exit code 0, chunk_id in stdout).

**SKIP G2 and G3** — This is the key simplification being tested.

## Tier-Dependent Policy Context

Per VERA's validated policy:
- **L1-L2 questions**: S1 is SUFFICIENT (this protocol)
- **L3-L5 questions**: S0 is REQUIRED (full G0→G3)

You will run S1 on ALL questions Q1-Q23. The evaluation will compare S1 vs S0 quality by tier.

## Output

Write claims to: `../vera/experiments/runs/sim1_ecc_replication/claims_S1_Q{QID}.jsonl`
Write verification results to: `../vera/experiments/runs/sim1_ecc_replication/verification_S1_Q{QID}.jsonl`

## Questions to Process

Process ALL 23 questions (Q1-Q23) using their B0.2 pinned queries from QUESTIONS.md.

## Success Criteria

- All claims have verified source_ids (G1 pass)
- **No G2/G3 execution** — measure cost/time savings
- Quality comparison against S0 on same questions

## Notes

- This protocol should be ~50% faster/cheaper than S0 for L1-L2
- Track token usage, wall-clock time, and API cost per question
- Use `vera-researcher` agent for retrieval/synthesis, `vera-verifier` for G1 only