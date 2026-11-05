---
type: Concept
id: 00_plan_compliance_runtime_verification_web_researc
title: "Plan Compliance, Execution Fidelity, and Runtime Verification in LLM Agents"
source: "plan_compliance_runtime_verification_web_research.md"
tags: [agentic, agents, context-engineering, icm, planning, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---

# Plan Compliance, Execution Fidelity, and Runtime Verification in LLM Agents

## Core concepts

Long-horizon autonomous agents are typically equipped with high-level plans to guide execution. However, empirical compliance with instructed plans varies significantly across model families and difficulty levels. Without systematic measurement of plan compliance, it is impossible to determine whether an agent succeeded through deliberate strategic reasoning or spurious benchmark heuristics. Furthermore, runtime verification is required to guarantee that atomic agent actions align with the plan before execution.

## Evidence from web sources

- **From Plan to Action: How Well Do Agents Follow the Plan? (Liu et al., ASE 2026, DOI 10.1145/3832783.3834400, arXiv 2604.12147):** Systematic evaluation of 21,120 SWE-agent trajectories across four frontier models (GPT-5 mini, DeepSeek-V3, DeepSeek-R1, Devstral-small) on SWE-bench Verified and SWE-bench Pro under eight plan variations.
  - Formulates three formal compliance metrics: Plan Phase Compliance (PPC), Plan Order Compliance (POC), and Plan Phase Fidelity (PPF).
  - Findings: Removing a plan significantly reduces task success across all models (especially for medium/hard issues). Even imperfectly followed plans substantially enhance local reasoning and prevent aimless exploration.
  - Context window pressure causes plan drift over long trajectories; introducing a "Reminded Plan" setting (re-inserting the plan every 5 steps) restores compliance and boosts success rates across models.
  - Artifact repository: `github.com/Intelligent-CAT-Lab/Planning-Analysis`.
- **RefineAct: Automatic Runtime Verification of LLM Agent Actions (ASE 2026):** Runtime verification framework that checks proposed agent actions against pre-conditions and invariants before dispatching them to the environment. Intercepts non-compliant actions and triggers localized re-planning.
- **Agent Planning Benchmark (APB, arXiv 2606.04874):** Diagnostic framework measuring multi-step decomposition, milestone tracking, and error recovery under strict plan adherence.

## Why it matters for this workspace

This directly validates the ICM contract architecture:
1. `pipeline/WORKFLOW.md` and stage `CONTEXT.md` files provide the explicit global plan that prevents drift.
2. The P3 Compaction Guard and re-anchor requirement in `stages/04_reflect/CONTEXT.md` (re-injecting plan and phase headers every N calls) exactly implements Liu et al.'s "Reminded Plan" mechanism to defeat context window degradation.
3. Automated verification gates (`check_*.py`) act as the runtime verification layer (RefineAct pattern) enforcing compliance.

## Source

web: https://arxiv.org/html/2604.12147v3 + https://conf.researchr.org/ + https://lab-design.github.io/papers/ASE-26/ + https://arxiv.org/html/2606.04874v2
