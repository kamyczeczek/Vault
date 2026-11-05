---
type: Concept
title: AGENTS
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:17:45Z }
---

# AGENTS.md — Time Series Model Discovery Workspace

## 1. Identity

This workspace discovers, evaluates, and selects time-series forecasting models using a modular, evidence-first workflow. One agent walks numbered stage folders; the filesystem does the orchestration.

## 2. Root routing table

| Task | Target |
|---|---|
| Start work | `PROCESS/WORKFLOW.md` |
| Stage contract | `PROCESS/<stage>/CONTEXT.md` |
| Reflection / learning | `MONITORING/reflection/` |
| Graph knowledge base | `brain/` |
| Skills catalog | `skills/SKILLS.md` |
| Core doctrine | `PRINCIPLES.md` |
| Isolated ts-brain worker | `brain/worker/` |

## 3. Invariants

1. **One folder, one job.** Each stage does one step and states its own contract.
2. **Numbering encodes order.** Renaming reorders the pipeline — that is the point.
3. **Every contract is explicit.** `CONTEXT.md` names exact inputs, process, outputs, and human check.
4. **The filesystem is the state machine.** Status is derivable by scanning `output/`.
| 5. **Graph brain freshness before query.** Run `python brain/verify_sync.py --rebuild` before `brain/ask.py`.
| 6. **Reflection before close.** Every task that finishes, changes state, or hits a problem MUST produce a schema-complete reflection file in `MONITORING/reflection/` and pass `python PROCESS/run_gates.py --all` (gate `reflection_close`) before the session yields. The reflection worker queries the unified brain deterministically (`brain/ask.py`, `brain/verify_sync.py`) and injects graph knowledge; no free recall.
7. **Skill files are project-local.** Skills live under `skills/`, tracked by `skills/SKILLS.md`.
9. **Principles govern routing & Git workflow.** `PRINCIPLES.md` is the top-level contract. After any change, update ICM routing if the change affects skills, stage flow, or task ownership. If the user did not specify skills, the agent MUST select required skills from `skills/SKILLS.md` before proceeding. The agent MUST inspect git history on touched paths before edits, anchor before exploratory tasks, and seal passing work with structured Lore git trailers (P3, P4).

## 4. Out of scope

Real-time multi-agent orchestration, high-concurrency serving, automated mid-pipeline branching. This workspace is for sequential, human-reviewed, repeatable model discovery.
