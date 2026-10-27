---
type: Concept
title: reflection-fastpath-backend
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:09Z }
---

# Decision ticket: Reflection fast-path backend

## Question
Which execution backend should replace the current `omp launch` path, if any, while preserving the ICM contracts?

## ICM constraints
- **Catalog:** `pipeline/06_reflect/WORKFLOW.md` and `spawn.py` route the phase.
- **Contract:** `stages/04_reflect/CONTEXT.md` defines inputs, grounding, and outputs.
- **Factory:** `pipeline/06_reflect/presearch.py` and the reflection prompt define deterministic retrieval and schemas.
- **Product:** `reflection/digests/`, `reflection/candidates/`, and `reflection/timings/` are run artifacts.
- **State:** graph fingerprint, plan version, trace events, and timing JSON must remain Python-owned.

## Evidence gathered
| Backend | Result | Decision status |
|---|---|---|
| `omp launch --extension` | Completed the existing reflection in ~181 s; artifacts passed grounding gates | Current production path |
| Direct Nara models | 402/429 insufficient credits, or upstream-unavailable | Reject for now |
| Infron DeepSeek free | 429 requires Team balance | Reject for now |
| 9router models | 401 no active credentials | Reject for now |
| google-ai-studio models | 404 endpoint missing | Reject for now |
| **omniroute** (7/10 models) | 6.7–24.6 s, structured JSON with claims/candidates/next_bets | **Primary candidate** |

## Decision
Do **not** replace `omp` yet. Use the omniroute backend behind an explicit feature flag with automatic fallback to `omp`. The replacement must first pass a structured-output probe (done: `pipeline/06_reflect/backend_probe.py`) and the full reflection gates.

## Required next artifact
A `--backend omniroute --model cx/gpt-5.6-luna-low` flag on `reflect.py`, with a timeout and automatic fallback to `omp` on failure.

## Rollback
The existing `pipeline/06_reflect/spawn.py` remains the default. Any replacement must be enabled by an explicit flag and must leave the current path untouched when the flag is absent.
