---
id: repo_entropy_ai_agents
type: candidate
date: 2026-09-30
topic: repository entropy accelerated by AI agents
status: candidate
sources:
  - knowledge/corpus/00_harness_engineering_for_agentic_ai_coding_tools.md
  - knowledge/corpus/42_refactoring_improving_the_design_of_existing_cod.md
  - knowledge/corpus/07_working_effectively_with_legacy_code_michael_c_f.md
  - knowledge/corpus/00_slop_code_bench.md
  - knowledge/corpus/reflection_rule_of_scars.md
  - knowledge/corpus/00_session_compaction_for_ai_agents_research.md
title: 2026_09_30_repo_entropy_ai_agents
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# Repository Entropy Under AI Agents — Synthesis Candidate

## Thesis

AI agents invert the classic debt equation: they accelerate *creation* far faster than *review*, so repository entropy (code drift, doc/code desync, config drift, memory-store noise) grows super-linearly unless the workspace installs **deterministic gates** that run at machine frequency. Entropy management shifts from a human habit to a pipeline property.

## What accelerates entropy (mechanisms, grounded)

1. **Review-bandwidth inversion.** Debt "comes with interest payments: the extra cost of maintenance" (`42_refactoring...`). Agents remove the authoring bottleneck, so interest accrues on a codebase growing at agent throughput while human review stays at human rate.
2. **Harness/config drift — the new artifact class.** The 2,853-repo harness study (`00_harness_engineering...`, trust_tier 1) shows configuration artifacts (AGENTS.md, skills, subagents, context files) now dominate how tools behave, yet they sit *outside* the managed corpus: nothing traces them for staleness. The fastest-decaying files in an agent workspace are the instructions that steer the agents.
3. **Desync between code and derived knowledge.** Agents modify code without touching docs/graphs. Live example from this session: ingest detected a **MANIFEST STALE** state (9 untraced corpus notes, 194-row manifest) and had to self-heal. Without the gate, 10 sources would have sat untracked indefinitely.
4. **Memory-store noise accumulation.** agentmemory baseline (2026-09-30): 36 raw observations, 0 distilled lessons, uniform importance, empty profile slots. Raw-log growth with no consolidation is entropy in the memory tier itself; semantic distillation currently has a 5-summary floor, so small workspaces never clear it.
5. **Slop generation.** `00_slop_code_bench` frames agent output as benchmark-measurable degradation: near-perfect recall on static tasks collapses when memory must be *used decision-relevantly* (see `00_persistent_memory_hierarchies`, MemoryAgentBench finding).

## Countermeasures (design)

| # | Measure | Precedent in this workspace |
|---|---|---|
| 1 | **Gates at machine frequency** — session-start preflight + manifest/consistency checks; fail-stop, auto-heal | `preflight.py`, manifest gate (just exercised) |
| 2 | **Harness artifacts as first-class corpus** — ingest AGENTS.md/CLAUDE.md/skills into tracking so staleness is detectable, not assumed | `ingest.py` → manifest fingerprint |
| 3 | **Scars, not re-litigation** — compile recurring failures into constraints; monotone (blocked stays blocked), sublinear growth | `SCARRED_FROM` edges (24 live), `reflection_rule_of_scars` |
| 4 | **Scheduled consolidation** — cold-session episodic→semantic→procedural with verify gate; evict ungrounded items | agentmemory 4-tier pipeline + `evict_stale.py` analogue |
| 5 | **Eviction as a primary mechanism** — two-stage archive (D10), lesson TTL, compaction | `evict_stale.py`, `projects/_archive/` |
| 6 | **Entropy metrics** — measurable proxies: untraced-corpus %, stale manifest rows, failing-gate count, lesson/observation ratio, doc-code divergence score | AGENTS.md "hill-climbable goals" rule |

## Key insight

Entropy reduction in an agent workspace is **asymmetric work**: creation is free and fast; detection and deletion are the expensive parts. The workspace's architecture (ICM: verified corpus → derived graph → reflection → meta-learning) is already an entropy-reduction engine — the missing piece is **scheduling**: every mechanism above must run automatically at boundaries (session start, session end, nightly), not by hand.

## Open questions / next experiments

1. Does tracking harness artifacts in the manifest (measure 2) measurably cut config drift? (A/B: drift-detection latency with/without tracking.)
2. Can consolidation clear the 5-summary floor for small workspaces via per-session episodic batching instead of global counts?
3. Is `memory_verify` citation density a usable proxy for lesson groundedness at scale?
