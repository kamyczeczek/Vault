---
status: decided
recommendation: keep pointer (do not migrate root PLAN.md into handoff/status/PLAN.md)
decided_at: 2026-10-18
owner: mateusz
---

# plan-md-migration

Should root `PLAN.md` be moved into `handoff/status/PLAN.md` (becoming the
single home) instead of the current pointer file?

Context: `handoff/status/PLAN.md` is a pointer to root `/PLAN.md`, which stays
in `ALLOWED_ROOT` and is referenced widely (SCARS, flags, reviews). Moving it
would break many references; the pointer keeps one home per fact (ICM inv. 8).

Recommendation: keep the pointer. Migration is a separate decision if the
cost/benefit changes.
not checked: —
