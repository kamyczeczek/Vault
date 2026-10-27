# VERA SIM-1 S2 Protocol: Retrieve → Answer (No Gates)

You are a VERA researcher executing the **S2 (No Gates)** arm of the simplicity ablation study.

## Your Task

Run the minimal VERA protocol on benchmark questions Q1-Q23 using B0.2 pinned queries.
**NO VERIFICATION GATES** — retrieve, synthesize, output claims directly.

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
  "claim_id": "Q5_S2_c01",
  "statement": "The lab's reflection protocol handles session compaction by persisting accepted rule candidates...",
  "source_ids": ["00_reflection_protocol", "01_session_compaction_rules"],
  "support_type": "direct",
  "confidence": "high",
  "mechanism": "Reflection protocol explicitly stores accepted rule candidates during compaction",
  "limitation": "Only covers rule candidates, not full context",
  "verification_status": "unverified"
}
```

### 3. Verification Gates

**NONE** — This is the baseline no-verification protocol.

## Output

Write claims to: `../vera/experiments/runs/sim1_ecc_replication/claims_S2_Q{QID}.jsonl`
(No verification output file needed)

## Questions to Process

Process ALL 23 questions (Q1-Q23) using their B0.2 pinned queries from QUESTIONS.md.

## Success Criteria

- Claims synthesized for all questions
- **Zero verification overhead** — measure absolute minimum cost/time
- Quality comparison against S0 and S1 on same questions

## Notes

- This is the absolute baseline — no grounding check, no reproducibility, no negative controls
- Expected to fail on L3-L5 (conflicting, causal, proposal questions)
- Track token usage, wall-clock time, and API cost per question
- Use `vera-researcher` agent for retrieval/synthesis only