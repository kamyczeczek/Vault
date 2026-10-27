---
type: Concept
title: vera_expa_findings
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Verification & Extraction of Experimental Findings

fingerprint: 4880aab33ca4
# superseded_fingerprint: 31989e46d0a5
# superseded_fingerprint: 1f0d6e7e0b21
# superseded_fingerprint: 44172cafee34
plan_version: a4d9465d311f
phase: 04_reflect
**date:** 2026-09-25
**chapters_cited:** `00_06_self_correction_grounding_requirement`, `00_08_lesson_persistence_eviction_requirement`, `00_09_mistake_correction_abstraction_level`, `00_agent_error_taxonomy_debugging_web_research`, `00_00_software_factory_isolate_build_prove_ship`, `00_agent_hooks_lifecycle_guardrails`

---

## Claim

Experimentally observed agent errors become durable prevention only when (a) the correction is extracted at **pattern abstraction level**, not instance level; (b) the lesson is governed by deterministic guardrails that prevent its own misapplication; and (c) the system retains the ability to **evict** the lesson when it ceases to hold. Without all three, a stored "lesson" degrades performance just as fast as no memory at all — or worse, because it compounds confidently wrong guidance.

The workspace already encodes all three primitives: `(failure condition → reason → correction)` triples in candidate format (chunk `00_09_mistake_correction_abstraction_level`), eviction-at-zero scoring in ExpeL's ledger model (chunk `00_08_lesson_persistence_eviction_requirement`), and hook-gated lifecycle interception that enforces correctness before state changes propagate (chunk `00_agent_hooks_lifecycle_guardrails`). The gap is a verification gate between *candidate* and *accepted* that independently re-runs the corrected behavior rather than trusting the agent's own testimony.

---

## Evidence

**E1 — Ungrounded self-correction measurably degrades performance.** Huang et al. (Google DeepMind, 2023, arXiv:2310.01798) shows accuracy drops after intrinsic self-correction rounds across GSM8K, CommonSenseQA, and a third reasoning benchmark, using GPT-4 and PaLM-2 with no external verifier. The mechanism is verification asymmetry: a model that cannot reliably solve a problem cannot reliably judge its solution. The critique and the error come from the same distribution. The revision is conditioned on an unverified diagnosis, which is worse than no diagnosis.

Chunk id: `00_06_self_correction_grounding_requirement`

**E2 — Eviction is what makes a stored lesson trustworthy.** ExpeL (02_expel_experiential_insight_extraction) gives every insight ι starting importance 2, with `ADD`, `UPVOTE`, `EDIT` incrementing and `DOWNVOTE` decrementing; an insight is evicted at zero. This is what makes the ledger self-correcting rather than self-reinforcing. Honest Lying (chunk `04_honest_lying_memory_confabulation` — **not present in the corpus, citation unverified**; the paper was never ingested) would show the cost of absence: 0 of 121 reflections in 16 frozen ALFWorld environments mentioned the correct target object, RRR 0.64 — not missing lessons but confidently wrong lessons re-read on every trial. Treat that half as unsupported until the source is ingested; the ExpeL half is carried by the cited chunk below. The paper notes insights grow monotonically in practice; eviction handles wrong lessons but not volume — retrieval is the separate second mechanism.

Chunk id: `00_08_lesson_persistence_eviction_requirement`

**E3 — The transferable unit is the (condition→reason→correction) triple, not the trajectory.** An et al. (EMNLP 2024 Findings, doi:10.18653/v1/2024.findings-emnlp.46) fine-tunes open-source LLMs on `(wrong CoT, mistake location, corrected CoT)` triples. Finding 2: mistake-correction data beats ordinary CoT data for the same budget, because it encodes failure-mode explanations that correct-only data never contains. A correct solution demonstrates one path to right; a corrected mistake documents the *conditions under which the model tends to go wrong*. Recurrence prevention scales with abstraction level: pattern > rule > instance.

Chunk id: `00_09_mistake_correction_abstraction_level`

**E4 — Modular error taxonomy isolates root causes for targeted correction.** Zhu et al. (arXiv:2509.25370, 2025) classifies agent failures into five modules: Memory (retrieval, persistence, eviction), Reflection (ungrounded self-correction, confabulation, missing eviction), Planning (plan-drift, incomplete decomposition, horizon collapse), Action (tool misuse, parameter errors, sequencing faults), System (liveness, consistency, resource exhaustion). AgentDebug's detect→attribute→correct pipeline yields +24% all-correct accuracy and +26% relative task-success improvement on ALFWorld, GAIA, and WebShop.

Chunk id: `00_agent_error_taxonomy_debugging_web_research`

**E5 — Isolate-build-prove-ship requires observable contracts at each station, not just instructions.** The software factory workflow encodes four stations (Isolate, Build, Prove, Ship). Its core claim is that a sequence of Markdown instructions is not a factory unless the repository can detect incomplete or false completion. The locally retrieved accepted lessons (`agent-sandboxing`, `automated-peer-review-loops`, `defensive-failure-mode-hardening`, `icm-methodology-hardening`) already align with this structure.

Chunk id: `00_00_software_factory_isolate_build_prove_ship`

**E6 — Deterministic hooks govern stochastic models.** Lifecycle hooks (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) are deterministic interception points. `Exit 2` denies a tool call and injects diagnostic error into the conversation so the model self-corrects on the next turn. A sliding-window hash cache of `hash(tool_name, args, output)` detects non-progressing cycles in fast models.

Chunk id: `00_agent_hooks_lifecycle_guardrails`

---

## Decision

Three design decisions follow:

**D1 — Promotion gate requires external ground truth, not self-testimony.**
An experiment that reports its own success is unverifiable. Before a candidate can move from `proposed` to `experimental`, it must pass an independent verification step: either an automated test suite, an external oracle, or a before↔after artifact pair captured in isolation. The `review_gate.jsonl` contract (see pipeline phase: 04_reflect) already encodes this; D1 names it as the general principle.

**D2 — Lessons live at pattern abstraction, stored as `(condition → reason → correction)`.**
Instance-level logs ("action `a_i` was wrong at step k") prevent nothing on future trajectories. Rule-level statements ("when X, avoid Y") are better but still tied to a specific domain formulation. Pattern-level triples generalize: they capture the *structure* of the failure, which recurs across domains. Candidates must be written in this form to qualify.

**D3 — Every stored lesson must carry its own eviction predicate.**
A lesson without an escape hatch is a lie waiting to be cited. The eviction predicate answers: under what observed conditions does this lesson cease to apply? If the predicate is empty, the lesson should not be promoted. ExpeL's integer scoring is one implementation; the workspace's `reflection/memory.md` promotion path is another — both require an explicit downgrade/withdraw mechanism.

---

## Next Bet

The highest-leverage experiment: **implement a post-promotion audit that checks every accepted lesson against its own eviction predicate on a held-out trajectory**. If any accepted lesson fires in a scenario where its condition no longer holds (i.e., the condition was mis-specified or the environment changed), the lesson's score should decrement. This turns the memory system from a read-once archive into a continuously calibrated one — closing the loop that ExpeL started and the AGA bandit approach formalized mathematically.

A secondary bet: add `AgentDebug`-style root-cause attribution to the `reflect` stage of `pipeline/06_reflect`. Currently `spawn.py` retrieves chunks by tag intersection and writes a digest. Adding a `detect→attribute→correct` wrapper would make the reflection step itself produce structured error-classified candidates rather than flat observations.
