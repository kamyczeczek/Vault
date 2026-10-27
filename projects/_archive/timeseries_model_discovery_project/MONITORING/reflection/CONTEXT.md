---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# reflection/CONTEXT.md — Stage: Post-Work Reflection & Rule Synthesis

## Purpose
Capture, after every completed piece of work, a **deterministic** written reflection: what problems occurred, how they were solved, the verification evidence, and the permanent prevention rule that stops the same problem recurring. This is the learning feedback loop of the ICM architecture.

## Why This Stage Exists
The agent is stateless; the filesystem is its only memory. Without a mandatory reflection step, each session repeats the same mistakes, and hard-won diagnostic paths (like tracing a failing oh-my-pi extension through `~/.omp/logs/`) are lost. This stage converts experience into persistent rules.

## Entry Contract (two-tier: reflection via isolated worker)
The reflection file MUST be produced by an isolated worker started with `--cwd workspaces/reflection-brain` so the reflection graph is in the worker prompt and a faulty graph cannot contaminate the orchestrator (file contract: worker writes `MONITORING/reflection/YYYY-MM-DD_HHMM_S-XX-slug.md`, orchestrator reads only that file and validates schema / rejects inconsistent reports — see `workspaces/AGENTS.md`, `PROCESS/WORKFLOW.md` K-28, `workspaces/check_isolation.py`). Direct orchestrator writes without the worker violate the invariant.

You are in this folder because a piece of work has finished. "Finished" means any of:
- A task reached Yield without a block (successful completion).
- A task was abandoned or yielded-partial (`yielded-partial` / `blocked`).
- A problem was solved and logged to `MONITORING/KNOWLEDGE/problems/`.
- The user explicitly asked for a reflection (e.g. "do a reflection").

**Trigger timing:** Reflection runs as the **cleanup phase** of a completed task — after implementation is verified, before the session log is finalized (see `logs/CONTEXT.md`). It is not a separate thread; it is the mandatory closing step of every task that touched files, changed state, or hit a problem.

## Inputs (MUST have before writing a reflection file)
- The task's own progress log (`*/PROGRESS.md`) and result.
- Any block report (`logs/block-*.md`) or problem entry (`MONITORING/KNOWLEDGE/problems/*.md`).
- The concrete tool/output evidence (log paths, commands run, file paths) from the work itself.

## Exit Contract
You MUST NOT leave this stage unless:
1. A reflection file exists at `reflection/YYYY-MM-DD_HHMM_S-XX-slug.md` following the exact schema in `REFLECTION_RULES.md` + the template `_template.md`, produced by `omp agent --cwd workspaces/reflection-brain` (the worker ran `ask.py rejected` + `ask.py "<scope>"` before proposing prevention_rules).
2. Every problem in the work has: symptom, root cause, solution, and verification evidence — each non-empty and stated as a fact or falsifiable claim (no soft words; see `_factory/OPERATOR_DOCTRINE.md` §4).
3. Each distinct problem produced a **prevention rule** (Invariant) that is routed to its owning doc (`_factory/<file>`, `MONITORING/AGENTS.md`, or project `AGENTS.md`) — OR an explicit statement that the owning doc already covers it.
4. The reflection's `next_action_routing_changes` are applied: if the reflection discovered that the routing table (`ROOT/AGENTS.md` §2) or a stage contract needs updating, that update is made in this session before the reflection is marked complete.
5. The owning doc(s) referenced in the reflection were updated in this session (or a pointer to the pending update was written).

## Forbidden Actions in This Stage
- **Empty reflection:** writing a file with unfilled fields is a silent failure (doctrine §3). Every field must be filled or explicitly marked `none`.
- **Rewriting history:** `logs/*.md` are append-only; never edit a past session log from a reflection.
- **Fabricating evidence:** every "solved" claim MUST cite a log path or re-runnable command. No invented fixes.
- **Skipping the routing update:** if the reflection shows the routing table or stage contract is incomplete, you MUST update it before completing the reflection.

## Handoff
On exit, the reflection is complete. Ownership of any newly synthesized rule transfers to its destination (`_factory/`, `MONITORING/`, or project `AGENTS.md`). The session closes per `logs/CONTEXT.md` Touchdown schema.

## Routing
From the Layer-1 routing table in `ROOT/AGENTS.md` §2: reflection tasks position-address to this folder. Read **this file first**, then `REFLECTION_RULES.md`, then mirror `_template.md`.