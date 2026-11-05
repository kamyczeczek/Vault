---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:18Z }
---

# PROCESS/07_reflect/CONTEXT.md — Reflection & Rule Synthesis Stage

## Purpose

Convert completed work into durable, schema-complete prevention knowledge.
Every task that finishes, changes state, or hits a problem MUST close with a
reflection file in `MONITORING/reflection/` before the session yields.

This stage is enforced by `PROCESS/run_gates.py` (`reflection_complete` gate)
and by the git `pre-commit` hook (`hooks/pre-commit`). Both are deterministic;
neither invokes an LLM.

## Why This Stage Exists

The agent is stateless. Without a mandatory reflection step, each session
repeats the same mistakes, and hard-won diagnostic paths are lost. This stage
converts experience into persistent rules.

## Inputs

- Task artifacts: `PROGRESS.md`, `output/`, tool logs from the completed task
- Problems: `MONITORING/KNOWLEDGE/problems/*.md` (if any were created/updated)
- Brain data:
  - `brain/reflection_index.json` — scar index
  - `brain/digest.md` — scar digest
  - `brain/ask.py` — query interface for graph/RAG/reflection/skills
  - `brain/verify_sync.py` — freshness verifier

## Process

### Step 1 — Determine trigger

Run `python PROCESS/check_reflection_trigger.py --task-dir <task_dir>`
or manually evaluate against `MONITORING/reflection/REFLECTION_RULES.md` R1:

| # | Trigger |
|---|---------|
| T1 | Task finished, no block |
| T2 | Task yielded-partial or blocked |
| T3 | Problem solved/analyzed |
| T4 | User requested a reflection |
| T5 | Contract/routing changed |
| T6 | Problem lifecycle event |

If none apply → exit this stage; no reflection required.

### Step 2 — Deterministic knowledge injection (no free recall)

Before writing, query the brain and graph deterministically. This is the
"reflection worker prompt" — the agent follows this contract exactly:

```
You are a reflection worker for the unified project brain.

## REQUIRED QUERIES (run these before drafting any reflection)

1. Scar query:
   python brain/ask.py "scars matching: <task domain keywords>" --limit 5

2. Graph query:
   python brain/ask.py "knowledge graph: <task domain keywords>" --limit 5

3. Problem recurrence check:
   python PROCESS/check_problems.py check "<problem fingerprint tokens>"

4. Negative memory:
   python brain/ask.py rejected --limit 5

## REQUIRED CITATION FORMAT

- **Rebuild if out of sync:** if `brain/verify_sync.py` exits non-zero, run
  the rebuild chain below and re-check:
  ```
  python brain/build_reflection_index.py && python brain/gen_digest.py
  python brain/verify_sync.py --quiet
  ```
  This MUST exit 0 before the reflection is complete.

Every claim in `problems`, `solutions`, and `prevention_rules` MUST cite
at least one scar id, problem id, or graph node id returned by the queries
above. Format: `[scar:<id>]`, `[problem:<id>]`, `[graph:<id>]`.

A claim with no citation is rejected.

## REQUIRED PREVENTION RULE

For each distinct problem, produce one `invariant` that is:
- Deterministic: same trigger → same rule
- Falsifiable: can be checked by a script or gate
- Actionable: names the owning doc and the exact change

Route the invariant to its owning doc per REFLECTION_RULES.md R5.

## BANNED QUALIFIERS (R4/G2)

Do NOT use: "should work", "probably fine", "looks good", "seems to",
"I think", "generally", "more or less", "try to".

## OUTPUT

Write ONE file: MONITORING/reflection/YYYY-MM-DD_HHMM_S-XX-<slug>.md
Mirror MONITORING/reflection/_template.md exactly.
```

### Step 3 — Write reflection file

Write to `MONITORING/reflection/YYYY-MM-DD_HHMM_S-XX-<slug>.md` following
the exact schema in `REFLECTION_RULES.md` R3 and `_template.md`.

Required fields (in order):
- Title / Date / Status / Invoking rule
- `work_summary` — 1–3 sentences
- `problems` — one subsection per problem with `id`, `symptom`, `root_cause`
- `solutions` — per problem: `solution`, `verification_evidence`, `files_changed`
- `prevention_rules` — per problem: `invariant`, `owning_doc`, `owning_doc_updated`
- `next_action_routing_changes` — applied changes or `none`
- `open_risks` — deferred items or `none`

### Step 4 — Rebuild brain artifacts

After writing the reflection, rebuild the reflection index and digest:

```bash
python brain/build_reflection_index.py
python brain/gen_digest.py
```

### Step 5 — Verify brain sync

```bash
python brain/verify_sync.py --quiet
```

This MUST exit 0. If it exits non-zero, the reflection is incomplete.
Re-run the rebuild chain until `verify_sync.py` reports `in_sync: true`.

### Step 6 — Update reflection record

If `next_action_routing_changes` names a doc that needs updating, apply
those updates in this session before marking the reflection complete.

## Outputs

- `MONITORING/reflection/YYYY-MM-DD_HHMM_S-XX-<slug>.md` — schema-complete
  reflection file
- `brain/reflection_index.json` — rebuilt index (Step 4)
- `brain/digest.md` — rebuilt digest (Step 4)
- `brain/.last_build.json` — updated sidecar (Step 5)

## Human Check

1. Read the reflection file: does every problem have an `invariant` + `owning_doc`?
2. Does `brain/verify_sync.py --quiet` exit 0?
3. Are any `next_action_routing_changes` applied?

## Forbidden Actions

- **Empty reflection:** writing a file with unfilled fields is a silent failure.
  Every field must be filled or explicitly marked `none`.
- **Skipping rebuild:** yielding without rebuilding the brain after a reflection
  is an incomplete close.
- **Fabricating evidence:** every "solved" claim MUST cite a log path or
  re-runnable command.
- **Skipping citation:** claims without scar/problem/graph citations are rejected.

## Handoff

On exit, the reflection is complete. The session may yield. Ownership of
any newly synthesized rule transfers to its destination (`_factory/`,
`MONITORING/`, or project `AGENTS.md`).

## Routing

From `PROCESS/WORKFLOW.md`:
- K-10 routes `07_reflect · skill` to `/retro`
- K-11 routes `07_reflect · skill` to `/handoff`
