---
type: Concept
id: 2026-09-02_h720-etth1-research
date: 2026-09-02
scenario: S4
surface: h720 ETTh1 forecasting SOTA & experiment directions
status: done
supersedes: none
title: README
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Research: H=720 ETTh1 Forecasting — SOTA Comparison & Experiment Directions

Read-only commission (TsResearch subagent + main-agent verification): how the
project's single-origin H=720 ETTh1 results relate to published ETTh1-720
SOTA, and which experiment directions are worth evaluating. Headline: the
project's best (HeuristicLagELM 1.5923 raw ≈ 0.173 std-MAE) is numerically
below the best published univariate NLinear (0.226) but is NOT a SOTA claim
(single origin, window-tuned, low-amplitude scoring window); 10 prioritized
directions delivered, directions 1–2 (rolling-origin eval + validation-split
selection) gating everything else. The directions were consumed into
`PROCESS/03_plan/slices.md` (S-01…S-12).

## Migration note
Cutover 2026-09-05: this record was split out of the shared
`PROCESS/02_research/{findings,open_questions,references}.md` stage files
(research 1 of 2; commission 2 lives in
`RESEARCH/2026-09-03_knowledge-architecture-research/`). The 2026-09-02
content is preserved verbatim; the stage folder keeps only its contract.
