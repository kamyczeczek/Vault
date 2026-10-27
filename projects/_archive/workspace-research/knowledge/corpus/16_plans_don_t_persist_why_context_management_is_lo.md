---
type: Concept
id: 16_plans_don_t_persist_why_context_management_is_lo
title: "Preprint. (part 17/17)"
source: "Plans Don’t Persist Why Context Management Is Load Bearing for LLM Agents.pdf"
tags: [agentic, agents, anti-leakage, context-engineering, memory, planning, prompt-engineering, reflection]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Preprint.
Behavioral results do not depend on this post-processor.The Phase 1 task-success table
(Table 8) uses only maxt score(t)> 0 counts per condition, which are computed directly
from the saved trajectory results without any cross-condition pairing. The per-run success
flag in our raw logs is decoupled from goal completion (it triggers on step-limit truncation),
which is why we explicitly redefine real success as max -score>0 throughout Section 7.
C Context-Compression Stress Test Details
We evaluate four context policies on 30 ALFWorld tasks (task indices 50-79), 5 runs each (150
runs/policy), with Llama-3.1-70B as a ReAct agent under a 20-step cap. All policies share the
budget keep_recent=4 retained messages plus the system prompt; the agent’s full message
list is preserved internally, but only the compressed view is sent to the model on each call.
The probe used byprobe_gatedis theL 32 Ridge probe of §5, firing at thresholdτ=0.15; on
a fire it re-injects the pinned plan span for that step. Per-policy success is maxt score(t)> 0.
Comparisons use a paired permutation test (10,000 permutations) with 95% bootstrap CIs
over the 30 tasks; all results integrity-checked for 30 tasks × 4 policies × 5 runs with no
errored or zero-step runs (Table 9).
Table 9: Context-compression stress test (150 runs/policy). ∆ and p are paired permutation
tests vs. the noted baseline; CIs are bootstrap 95%. Naive eviction is catastrophic (p< 0.001);
neither plan-aware policy recovers (both CIs cross zero).
Policy Success SE∆(ref)pResurf.
none56.7%4.0% n/a n/a 0.0
naive22.0% 3.4%−34.7 (none)[−44.7,−24.7]<0.001 0.0
plan_protected20.7% 3.3%−1.3 (naive)[−10.7,+8.0]0.89 0.0
probe_gated24.7% 3.5%+2.7 (naive)[−6.7,+12.0]0.67 6.1
17
