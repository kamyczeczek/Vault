---
type: Concept
title: CONTEXT
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:45:31Z }
---

# CONTEXT — handoff/decisions/

Owner decisions, one file per decision. ICM contract (invariant 4).

## What it reads
- `handoff/flags/*.md` — facts that motivate a decision (read-only reference).
- `handoff/status/NEXT.md` — the single next sentence (read-only reference).

## What it writes
- `<slug>.md` — one decision per file (frontmatter + rationale).
- `STATUS.md` (via `scripts/build_status.py`) renders only decisions with
  `status: open`.

## Process
1. A new decision is opened as `handoff/decisions/<slug>.md` with
   `status: open`.
2. When resolved, set `status: decided`, fill `decided_at`, keep the file
   (one home per fact, ICM inv. 8).
3. `scripts/build_status.py` rebuilds `handoff/status/STATUS.md` from the
   open decisions.

## Schema (frontmatter)
- `status: open|decided`
- `recommendation` — the proposed resolution (one line).
- `decided_at` — ISO date when decided, or empty while open.
- `owner` — who owns the call.

## Human check
A human reads `STATUS.md` → `## Open decisions`; if a decision is stale or
resolved in reality, update its file and rebuild. `verified_at` lives in the
consuming manual files, not here.

## Not checked
- No decisions migrated from `handoff/flags/` yet beyond the PLAN.md pointer
  question (see `plan-md-migration.md`).
- `workspace-skills.md` symlink vs copy decision not captured here
  (P3 optional; tracked as not-checked in `handoff/status/CONTEXT.md`).
