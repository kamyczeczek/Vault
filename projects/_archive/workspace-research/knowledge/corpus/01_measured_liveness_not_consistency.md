---
type: Concept
id: 01_measured_liveness_not_consistency
title: "Measured Lesson — Consistency Gates Pass While the Thing They Guard Is Dead (root audit 2026-09-16) (part 2/2)"
source: "measured_liveness_not_consistency.md"
tags: [gate-semantics, liveness, observability, reflection]
generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:29Z }
---
taxonomy: #liveness #gate-semantics #observability
- Ask the *consumer's* question, not the *maintainer's*. "Is the corpus consistent with the
  manifest?" is the maintainer's question. "Does a query return the right brain?" is the
  consumer's. The defects lived precisely in the gap.
- **Gate the liveness of checks themselves.** A check that emits output on a schedule is not a
  check; it is a printer. Freshness must be part of the contract, or staleness reads as data.
- **Surface warnings from passing gates.** If rc=0 hides stderr, then "warn but continue" is
  indistinguishable from "healthy", and no one ever investigates.
- **Verify exit codes through pipes.** Otherwise a correct script appears broken or a broken
  one appears correct.

The meta-finding: the strategies were sound. The workspace had strong mechanism-class gates and
a verified reflection loop (121 reflections, 88% naming a mechanism). The gap was a *class*
missing — no gate asked "does the thing work?" — and a missing class is invisible to a suite
that only checks what it already knows about.

## Provenance

- Audit: `AUDIT-2026-09-16.md` (read-only whole-workspace assessment, all numbers computed live)
- Fix commit: `789d716` (all four defects + the two liveness gates)
- Gates: `PROCESS/run_gates.py`, `PROCESS/check_brain_router.py`
- Freshness probe: `.jcode/hooks/epidemiology.py`
- Recomputed live for this chunk: 13/13 gates pass; preflight suite 31 pass / 0 fail /
  14 red-path blocks; ledger stale 9 days.
