---
type: Concept
title: agent-error-reflection
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

fingerprint: 5f4f9d29057b  plan_version: ad0a031aa564  phase: 04_reflect
routing: ask.py --tag icm --tag reflection --limit 12; ask.py --tag agents --tag memory --limit 12; ask.py --tag self-evolution --tag reflection --limit 12; ask.py --tag agents --tag reflection --tag planning --limit 12
slug: agent-error-reflection
method: in-process audit (omp agent spawn hangs at the harness level — verified: `omp agent -p PING_OK` produced no output in 60s with no extension loaded; the spawn contract's deterministic routing was executed directly, and outputs are validated by the same gate, `scripts/check_reflection.py`)

## Claim

The literature splits "making errors not come back" into three distinct mechanisms that only work together:

1. **Document** the error at a granularity finer than success/fail (`05_self_debug_rubber_duck`, `03_agentdebug_root_cause_attribution`).
2. **Reflect** on it in language a later run can retrieve — not learn into weights (`01_reflexion_verbal_reinforcement`).
3. **Evict** the lesson when it turns out to be wrong, because the documentation itself can be the error (`04_honest_lying_memory_confabulation`, `02_expel_experiential_insight_extraction`).

Most failure comes from stopping after step 2. The papers that get to step 3 measure the failure it causes when you don't.

## Evidence

**Documenting** — `05_self_debug_rubber_duck`: rubber-duck explanation (model reads its own output and articulates it) finds errors with *zero* external feedback. On Spider, with no unit tests, explanation alone gained 2–3% baseline and 9% on hardest-level. Where unit tests *were* available (TransCoder, MBPP), the gain was 12%. The gap is the measured cost of an ungrounded diagnosis. Reusing failed predictions rather than discarding them matched baselines generating 10× more candidates.

**Reflecting** — `01_reflexion_verbal_reinforcement`: the policy is `θ = {M_a, mem}`, not weights. A binary fail signal plus trajectory is converted by a self-reflection model into a verbal lesson naming the wrong action `a_i` and the correct `a_i'`, stored in `mem`, read on the next trial. Recurrence prevention is therefore a *retrieval* problem, not a learning one. Bounded memory Ω = 1–3 lessons is the paper's own ceiling: it cannot accumulate across tasks. +22% AlfWorld, +20% HotPotQA, +11% HumanEval; 91% pass@1 HumanEval.

**The granularity that matters** — `03_agentdebug_root_cause_attribution`: failures are a *cascade*, not a list. A single root-cause error propagates through later decisions. The **critical error** is the earliest step whose correction directly prevents final failure — found by counterfactual substitution, not by flagging every mistake. 500+ trajectories over ALFWorld/WebShop/GAIA produced the AgentErrorTaxonomy (memory / reflection / planning / action / system); 10 annotators at κ=0.55 were instructed to find the *minimal root-cause set*. Failures cluster mid-trajectory, steps 6–15. 24.3% all-correct detection vs 0.3% baseline; up to 26% relative task-success gain.

**Evicting** — `04_honest_lying_memory_confabulation`: **memory confabulation**. In 16 frozen ALFWorld environments, **0 of 121 reflections mentioned the correct target object** — every reflection was confabulated and reused across trials while the environment reset to the correct task each time. Reflection Repetition Rate (RRR) = 0.64. The mitigation replaces open-ended self-diagnosis with *programmatic extraction of trajectory-level failure signals* — the environment supplies the error content, not the agent's self-narrative. Correct-object mention 0% → 86%, RRR 0.64 → 0.10, 3 of 16 solved.

**Cross-task persistence** — `02_expel_experiential_insight_extraction`: Reflexion's lesson dies with its task; ExpeL keeps successes *and failures* in a pool, then extracts insights with ADD / EDIT / UPVOTE / DOWNVOTE, evicting at importance zero. The stated reason is the important one: *"even successful trajectories can be suboptimal and mislead the generated insights."* A lesson derived from a lucky success is wrong, and the ledger can purge it. Reflexion has no such mechanism.

## Decision

Five corpus chunks added and the graph rebuilt. The synthesis that the graph now supports, and that no single paper states alone:

> An error-logging system is only recurrence-preventing if every stored lesson has (a) a provenance in environment evidence, not agent self-narrative, and (b) an eviction path. (a) without (b) freezes a good lesson; (b) without (a) lets a confabulated one reinforce forever. Reflexion has neither; ExpeL has (b) only; Honest Lying proves (a) is the load-bearing half; AgentDebug supplies the granularity at which (a) is even extractable.

This project's own reflection stage has (a) — every claim cites a chunk id — and the candidate ledger has (b) in the form of the `proposed → rejected` transition. The literature gap is the *determinism* of the eviction trigger: nothing decides when a stored lesson is stale except a human or a re-run. `04_honest_lying_memory_confabulation` is the only chunk co-tagged `reflection` + `determinism`, and it diagnoses the problem rather than solving it — this is the `icm_reflection_determinism_gap` candidate already in the backlog, now backed by primary literature.

## Next bet

The highest-leverage open item is no longer `P4`. It is closing the determinism gap in eviction: define the condition under which a stored lesson is re-validated or evicted automatically (corpus fingerprint move is the existing precedent — `04_honest_lying`'s RRR metric is the measurable signal). That turns the project's candidate ledger from a human-triaged list into a self-correcting one, which is exactly what the five papers agree is missing.
