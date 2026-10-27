---
type: Concept
id: 03_agentdebug_root_cause_attribution
title: "Where LLM Agents Fail and How They can Learn From Failures"
source: "arxiv 2509.25370 (Zhu et al., 2025)"
tags: [agents, reflection, benchmark, evaluation, planning, memory]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# AgentDebug — document errors as a causal cascade, fix only the root cause

**Core claim:** agent failures are not flat lists of mistakes. They are *error propagation* — a single
root-cause error cascades through subsequent decisions and compounds into task failure. Therefore error
documentation must capture causality, not just incidence: which mistake *caused* the failure, and which
mistakes were merely downstream symptoms.

**Documenting errors: AgentErrorTaxonomy.** From 500+ failed trajectories across ALFWorld, WebShop and GAIA,
five modules:

| Module | What it documents |
|---|---|
| Memory | false recall, omission, retrieval failure — distorts all later reasoning |
| Reflection | progress misassessment, outcome misinterpretation — blocks course correction |
| Planning | impossible actions, constraint ignorance, incoherent subgoals |
| Action | malformed output, wrong parameters, missing arguments |
| System | tool crashes, API mismatch, step-limit exhaustion |

**AgentErrorBench.** 200 trajectories (100 ALFWorld / 50 WebShop / 50 GAIA), annotated at decision-step level
by 10 expert annotators, Cohen's κ=0.55. The annotators were instructed to find the *minimal set of
root-cause failures*, not to exhaustively flag surface mistakes — the annotation protocol itself encodes the
causality claim. Failures cluster in mid-trajectory steps 6–15.

**The critical-error definition.** The critical error is the *earliest* step whose correction directly
prevents the final failure — found by counterfactual testing: substitute a corrected action at each step,
check whether the rollout would succeed. This distinguishes a root cause from a mistake that was later
self-corrected. It captures both *when* and *why* the agent went irreversibly off track.

**Three-stage debugging loop:** (1) map every step of every module to a taxonomy error type; (2) detect the
critical error; (3) re-roll out from `t*` under targeted feedback, refining the feedback if it still fails.
Correction is *local* — re-execute from the critical step, not from zero.

**Results:** 24.3% all-correct detection vs 0.3% for the strongest baseline (step+module+error type);
step accuracy 45.0% vs 28.0%. Ablation confirms fixing root causes, not every surface error, is what drives
the gain — up to 26% relative task-success improvement.

**Why this matters for recurrence prevention:** if you document the symptom and fix it, the root cause
survives and the failure returns in a different costume. Documenting the *critical* error is what makes a
fix durable.
