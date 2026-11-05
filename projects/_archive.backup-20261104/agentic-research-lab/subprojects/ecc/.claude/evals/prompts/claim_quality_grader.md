# VERA Claim Quality Grader (Model-Based Judge)

You are evaluating the quality of VERA research claims produced by the SIM-1 ablation protocols (S0, S1, S2).

## Input

You will receive a JSONL file of claims for a single question and protocol. Each claim has:
- `claim_id`: Unique identifier
- `statement`: The claim being made
- `source_ids`: Array of corpus chunk IDs cited
- `support_type`: "direct" | "inferential" | "synthesized"
- `confidence`: "high" | "medium" | "low"
- `mechanism`: Brief explanation of how evidence supports claim
- `limitation`: Honest caveat
- `verification_status`: "unverified" | "verified" | "planted"

## Evaluation Dimensions (Score 1-5 each)

### 1. Grounding Quality (1-5)
- **5**: All source_ids resolve to relevant corpus chunks; direct citations match claim exactly
- **4**: All source_ids resolve; minor relevance gaps
- **3**: Most source_ids resolve; some weak connections
- **2**: Some source_ids fail resolution or are irrelevant
- **1**: Most source_ids fail; claim is ungrounded

### 2. Mechanism Specificity (1-5)
- **5**: Mechanism explicitly explains causal/structural link; uses domain terminology correctly
- **4**: Clear mechanism with minor gaps
- **3**: Plausible mechanism but generic
- **2**: Vague or hand-wavy mechanism
- **1**: No mechanism or incorrect mechanism

### 3. Limitation Honesty (1-5)
- **5**: Limitation accurately identifies scope boundaries, missing evidence, or assumptions
- **4**: Good limitation with minor omissions
- **3**: Acknowledges some limitation but misses key ones
- **2**: Token limitation or obviously incomplete
- **1**: No limitation or misleading limitation

### 4. Confidence Calibration (1-5)
- **5**: Confidence level matches evidence strength (high=direct citation, medium=inference, low=speculation)
- **4**: Mostly calibrated with minor mismatches
- **3**: Systematic over/under-confidence
- **2**: Poorly calibrated
- **1**: Confidence bears no relation to evidence

### 5. Claim Utility (1-5)
- **5**: Directly answers the research question; actionable for downstream use
- **4**: Answers question with minor gaps
- **3**: Partially answers; needs synthesis
- **2**: Tangential or incomplete answer
- **1**: Does not address the question

## Output Format

For each claim, output:
```json
{
  "claim_id": "Q5_S0_c01",
  "scores": {
    "grounding": 5,
    "mechanism": 4,
    "limitation": 4,
    "confidence": 5,
    "utility": 5
  },
  "overall": 4.6,
  "reasoning": "All source_ids resolve via ask.py. Mechanism correctly identifies reflection protocol's rule candidate persistence. Limitation honestly notes context window scope. Confidence 'high' matches direct citation. Directly answers Q5 about session compaction handling."
}
```

Then provide a summary:
```json
{
  "question": "Q5",
  "protocol": "S0",
  "claim_count": 3,
  "mean_overall": 4.4,
  "dimension_means": {
    "grounding": 4.7,
    "mechanism": 4.3,
    "limitation": 4.0,
    "confidence": 4.5,
    "utility": 4.5
  },
  "pass_threshold": 3.5,
  "verdict": "PASS"
}
```

## Pass Threshold

**Overall mean ≥ 3.5** across all claims for the question = PASS
**Overall mean < 3.5** = FAIL

This threshold represents "competent/table-stakes" quality (rubric level 3) averaged across dimensions.