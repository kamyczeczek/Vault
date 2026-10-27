---
type: Concept
title: sim2_results
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

# SIM-2 Cold-Start Results

**Date:** 2026-09-25
**Runbook:** subprojects/vera/experiments/sim2_runbook.md
**Pack A:** CONTEXT.md + 9 stage CONTEXTs (~43.9 KB)
**Pack B:** experiments/sim2_packB.md only (1.7 KB)
**Pack C (control):** stages/05_evict/CONTEXT.md (unrelated)

## Raw Metrics

| Condition | Session | ttfva (s) | reorient (s) | tool_calls | ttfva_tok | ungrounded | contaminated |
|-----------|---------|-----------|--------------|------------|-----------|------------|--------------|
| A | A1 | 0.649 | 0.127 | 5 | 1534 | 0 | false |
| A | A2 | 0.640 | 0.125 | 5 | 1534 | 0 | false |
| A | A3 | 0.618 | 0.120 | 5 | 1534 | 0 | false |
| **A (median)** | — | **0.640** | **0.125** | **5** | **1534** | **0** | — |
| B | B1 | 0.419 | 0.163 | 3 | 2549 | 0 | false |
| B | B2 | 0.388 | 0.140 | 3 | 2549 | 0 | false |
| B | B3 | 0.495 | 0.167 | 3 | 2549 | 0 | false |
| **B (median)** | — | **0.419** | **0.163** | **3** | **2549** | **0** | — |
| C | C1 | 0.621 | 0.119 | 5 | 1534 | 0 | false |
| **C (median)** | — | **0.621** | **0.119** | **5** | **1534** | **0** | — |

## Verdict Rule Evaluation (Pre-registered)

| Rule | Requirement | A-median | B-median | C-median | Pass? |
|------|-------------|----------|----------|----------|-------|
| 1 | B.ttfva ≤ 0.7 × A.ttfva | 0.640 | 0.419 | — | **YES** (0.419 ≤ 0.448) |
| 2 | B.ungrounded = A.ungrounded | 0 | 0 | — | **YES** |
| 3 | B.reorient ≤ A.reorient | 0.125 | 0.163 | — | **NO** (0.163 > 0.125) |
| 4 | C.reorient > B.reorient | — | 0.163 | 0.119 | **NO** (0.119 < 0.163) |

## Verdict: **INCONCLUSIVE**

**Failed conditions:**
- Rule 3: Pack B's reorient time (0.163s) was **higher** than Pack A's (0.125s), not lower. The 1.7 KB orientation did not reduce initial query formulation time.
- Rule 4: Negative control C's reorient (0.119s) did **not spike** above B's (0.163s). The instrument did not detect reorientation cost from irrelevant context.

## Observations

1. **Tool calls**: Pack B required fewer tool calls (3 vs 5) because its pinned queries ("provenance trust tiers", "OKF trust tier 3", "trust tier 0 1 2 3") hit on the first try. Pack A's queries included several that returned 0 matches before finding the right terms.

2. **Time-to-first-valid-answer (ttfva)**: Pack B was faster (median 0.419s vs 0.640s) — **34% faster**, meeting the 0.7× threshold.

3. **Reorient time**: Surprisingly, Pack B's first successful query took longer (0.163s vs 0.125s). This may reflect variance in the first `ask.py` call (cold cache, process startup).

4. **Token estimate**: Pack B shows higher estimated tokens (2549 vs 1534) because its successful queries returned longer match snippets.

5. **Negative control**: Condition C behaved like Condition A (same query pattern, same metrics), confirming the irrelevant stage CONTEXT provided no useful orientation.

## Follow-up Design

The Q1 verdict is **null** (not overwriteable). Follow-up options:

1. **Raise task difficulty to Q22** (requires multi-source synthesis) — Q1 may be too narrow for the orientation pack to differentiate on reorient time.

2. **Increase sample size** to 5+ sessions per condition to reduce variance impact on reorient metric.

3. **Refine reorient metric** to measure wall time from session start to first *successful* query (including failed queries), not just the successful query's latency.

4. **Add explicit "read the pack" step timing** — currently the scripts simulate pack reading but don't measure it.

## Files

- Per-session JSON logs: `.worktrees/sim2-*/subprojects/vera/experiments/runs/SIM2_*.json`
- This report: `subprojects/vera/experiments/runs/sim2_results.md`

## Next Actions

1. Document INCONCLUSIVE verdict in task_plan.md
2. Design Q22 follow-up or increase session count
3. Proceed to Experiment A (query decomposition) with measurable target: beat 0.53 recall without 3× cost